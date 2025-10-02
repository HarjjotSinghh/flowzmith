import { v } from "convex/values";
import { mutation, query } from "./_generated/server";
import { Doc, Id } from "./_generated/dataModel";

// Start a collaboration session
export const startCollaborationSession = mutation({
  args: {
    contractId: v.id("contracts"),
  },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) {
      throw new Error("Not authenticated");
    }

    const user = await ctx.db
      .query("users")
      .withIndex("by_email", (q) => q.eq("email", identity.email!))
      .first();

    if (!user) {
      throw new Error("User not found");
    }

    const contract = await ctx.db.get(args.contractId);
    if (!contract) {
      throw new Error("Contract not found");
    }

    // Check if user has access to the contract
    if (
      contract.createdBy !== user._id &&
      !contract.collaborators.includes(user._id) &&
      !contract.isPublic
    ) {
      throw new Error("Not authorized to access this contract");
    }

    // Check if there's already an active session
    const existingSession = await ctx.db
      .query("collaborationSessions")
      .withIndex("by_contract", (q) => q.eq("contractId", args.contractId))
      .filter((q) => q.eq(q.field("isActive"), true))
      .first();

    if (existingSession) {
      // Join existing session
      const updatedParticipants = existingSession.participants.filter(
        (p) => p.userId !== user._id
      );
      updatedParticipants.push({
        userId: user._id,
        joinedAt: Date.now(),
        lastActiveAt: Date.now(),
      });

      await ctx.db.patch(existingSession._id, {
        participants: updatedParticipants,
        lastActivityAt: Date.now(),
      });

      return existingSession._id;
    }

    // Create new session
    const sessionId = await ctx.db.insert("collaborationSessions", {
      contractId: args.contractId,
      participants: [
        {
          userId: user._id,
          joinedAt: Date.now(),
          lastActiveAt: Date.now(),
        },
      ],
      isActive: true,
      createdAt: Date.now(),
      lastActivityAt: Date.now(),
    });

    // Log analytics
    await ctx.db.insert("analytics", {
      type: "collaboration_started",
      userId: user._id,
      contractId: args.contractId,
      metadata: {
        success: true,
      },
      timestamp: Date.now(),
    });

    return sessionId;
  },
});

// Join a collaboration session
export const joinCollaborationSession = mutation({
  args: {
    sessionId: v.id("collaborationSessions"),
  },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) {
      throw new Error("Not authenticated");
    }

    const user = await ctx.db
      .query("users")
      .withIndex("by_email", (q) => q.eq("email", identity.email!))
      .first();

    if (!user) {
      throw new Error("User not found");
    }

    const session = await ctx.db.get(args.sessionId);
    if (!session || !session.isActive) {
      throw new Error("Session not found or inactive");
    }

    const contract = await ctx.db.get(session.contractId);
    if (!contract) {
      throw new Error("Contract not found");
    }

    // Check if user has access to the contract
    if (
      contract.createdBy !== user._id &&
      !contract.collaborators.includes(user._id) &&
      !contract.isPublic
    ) {
      throw new Error("Not authorized to access this contract");
    }

    // Add user to session if not already present
    const existingParticipant = session.participants.find(
      (p) => p.userId === user._id
    );

    if (!existingParticipant) {
      const updatedParticipants = [
        ...session.participants,
        {
          userId: user._id,
          joinedAt: Date.now(),
          lastActiveAt: Date.now(),
        },
      ];

      await ctx.db.patch(args.sessionId, {
        participants: updatedParticipants,
        lastActivityAt: Date.now(),
      });
    } else {
      // Update last active time
      const updatedParticipants = session.participants.map((p) =>
        p.userId === user._id
          ? { ...p, lastActiveAt: Date.now() }
          : p
      );

      await ctx.db.patch(args.sessionId, {
        participants: updatedParticipants,
        lastActivityAt: Date.now(),
      });
    }

    return { success: true };
  },
});

// Leave a collaboration session
export const leaveCollaborationSession = mutation({
  args: {
    sessionId: v.id("collaborationSessions"),
  },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) {
      throw new Error("Not authenticated");
    }

    const user = await ctx.db
      .query("users")
      .withIndex("by_email", (q) => q.eq("email", identity.email!))
      .first();

    if (!user) {
      throw new Error("User not found");
    }

    const session = await ctx.db.get(args.sessionId);
    if (!session) {
      throw new Error("Session not found");
    }

    const updatedParticipants = session.participants.filter(
      (p) => p.userId !== user._id
    );

    if (updatedParticipants.length === 0) {
      // End session if no participants left
      await ctx.db.patch(args.sessionId, {
        isActive: false,
        participants: [],
      });
    } else {
      await ctx.db.patch(args.sessionId, {
        participants: updatedParticipants,
        lastActivityAt: Date.now(),
      });
    }

    return { success: true };
  },
});

// Update cursor position
export const updateCursorPosition = mutation({
  args: {
    sessionId: v.id("collaborationSessions"),
    line: v.number(),
    column: v.number(),
  },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) {
      throw new Error("Not authenticated");
    }

    const user = await ctx.db
      .query("users")
      .withIndex("by_email", (q) => q.eq("email", identity.email!))
      .first();

    if (!user) {
      throw new Error("User not found");
    }

    const session = await ctx.db.get(args.sessionId);
    if (!session || !session.isActive) {
      throw new Error("Session not found or inactive");
    }

    const updatedParticipants = session.participants.map((p) =>
      p.userId === user._id
        ? {
            ...p,
            cursor: { line: args.line, column: args.column },
            lastActiveAt: Date.now(),
          }
        : p
    );

    await ctx.db.patch(args.sessionId, {
      participants: updatedParticipants,
      lastActivityAt: Date.now(),
    });

    return { success: true };
  },
});

// Apply code change
export const applyCodeChange = mutation({
  args: {
    sessionId: v.id("collaborationSessions"),
    changeType: v.union(
      v.literal("insert"),
      v.literal("delete"),
      v.literal("replace")
    ),
    line: v.number(),
    column: v.number(),
    content: v.string(),
  },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) {
      throw new Error("Not authenticated");
    }

    const user = await ctx.db
      .query("users")
      .withIndex("by_email", (q) => q.eq("email", identity.email!))
      .first();

    if (!user) {
      throw new Error("User not found");
    }

    const session = await ctx.db.get(args.sessionId);
    if (!session || !session.isActive) {
      throw new Error("Session not found or inactive");
    }

    const contract = await ctx.db.get(session.contractId);
    if (!contract) {
      throw new Error("Contract not found");
    }

    // Check if user has edit permission
    if (
      contract.createdBy !== user._id &&
      !contract.collaborators.includes(user._id)
    ) {
      throw new Error("Not authorized to edit this contract");
    }

    // Record the code change
    const changeId = await ctx.db.insert("codeChanges", {
      sessionId: args.sessionId,
      contractId: session.contractId,
      userId: user._id,
      changeType: args.changeType,
      position: {
        line: args.line,
        column: args.column,
      },
      content: args.content,
      timestamp: Date.now(),
      applied: true,
    });

    // Update session activity
    await ctx.db.patch(args.sessionId, {
      lastActivityAt: Date.now(),
    });

    return { changeId, success: true };
  },
});

// Get active collaboration session for a contract
export const getActiveSession = query({
  args: {
    contractId: v.id("contracts"),
  },
  handler: async (ctx, args) => {
    const session = await ctx.db
      .query("collaborationSessions")
      .withIndex("by_contract", (q) => q.eq("contractId", args.contractId))
      .filter((q) => q.eq(q.field("isActive"), true))
      .first();

    if (!session) {
      return null;
    }

    // Get participant details
    const participants = await Promise.all(
      session.participants.map(async (p) => {
        const user = await ctx.db.get(p.userId);
        return {
          ...p,
          user,
        };
      })
    );

    return {
      ...session,
      participants,
    };
  },
});

// Get recent code changes for a session
export const getRecentChanges = query({
  args: {
    sessionId: v.id("collaborationSessions"),
    limit: v.optional(v.number()),
  },
  handler: async (ctx, args) => {
    const changes = await ctx.db
      .query("codeChanges")
      .withIndex("by_session", (q) => q.eq("sessionId", args.sessionId))
      .order("desc")
      .take(args.limit || 50);

    // Get user details for each change
    const changesWithUsers = await Promise.all(
      changes.map(async (change) => {
        const user = await ctx.db.get(change.userId);
        return {
          ...change,
          user,
        };
      })
    );

    return changesWithUsers;
  },
});

// Clean up inactive sessions
export const cleanupInactiveSessions = mutation({
  args: {},
  handler: async (ctx) => {
    const cutoffTime = Date.now() - 30 * 60 * 1000; // 30 minutes ago

    const inactiveSessions = await ctx.db
      .query("collaborationSessions")
      .withIndex("by_active", (q) => q.eq("isActive", true))
      .filter((q) => q.lt(q.field("lastActivityAt"), cutoffTime))
      .collect();

    for (const session of inactiveSessions) {
      await ctx.db.patch(session._id, {
        isActive: false,
      });
    }

    return { cleanedUp: inactiveSessions.length };
  },
});

// Get collaboration statistics
export const getCollaborationStats = query({
  args: {
    contractId: v.id("contracts"),
  },
  handler: async (ctx, args) => {
    const sessions = await ctx.db
      .query("collaborationSessions")
      .withIndex("by_contract", (q) => q.eq("contractId", args.contractId))
      .collect();

    const changes = await ctx.db
      .query("codeChanges")
      .withIndex("by_contract", (q) => q.eq("contractId", args.contractId))
      .collect();

    const totalSessions = sessions.length;
    const activeSessions = sessions.filter((s) => s.isActive).length;
    const totalChanges = changes.length;
    const uniqueCollaborators = new Set(
      sessions.flatMap((s) => s.participants.map((p) => p.userId))
    ).size;

    const recentActivity = changes
      .filter((c) => c.timestamp > Date.now() - 24 * 60 * 60 * 1000) // Last 24 hours
      .length;

    return {
      totalSessions,
      activeSessions,
      totalChanges,
      uniqueCollaborators,
      recentActivity,
    };
  },
});