import { v } from "convex/values";
import { mutation, query } from "./_generated/server";
import { Doc, Id } from "./_generated/dataModel";

// Get user notifications
export const getUserNotifications = query({
  args: {
    limit: v.optional(v.number()),
    unreadOnly: v.optional(v.boolean()),
  },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) {
      return [];
    }

    const user = await ctx.db
      .query("users")
      .withIndex("by_email", (q) => q.eq("email", identity.email!))
      .first();

    if (!user) {
      return [];
    }

    let query = ctx.db
      .query("notifications")
      .withIndex("by_user", (q) => q.eq("userId", user._id))
      .order("desc");

    if (args.unreadOnly) {
      query = ctx.db
        .query("notifications")
        .withIndex("by_user_unread", (q) => 
          q.eq("userId", user._id).eq("isRead", false)
        )
        .order("desc");
    }

    const notifications = await query.take(args.limit || 50);

    return notifications;
  },
});

// Mark notification as read
export const markNotificationAsRead = mutation({
  args: {
    notificationId: v.id("notifications"),
  },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) {
      throw new Error("Not authenticated");
    }

    const notification = await ctx.db.get(args.notificationId);
    if (!notification) {
      throw new Error("Notification not found");
    }

    const user = await ctx.db
      .query("users")
      .withIndex("by_email", (q) => q.eq("email", identity.email!))
      .first();

    if (!user || notification.userId !== user._id) {
      throw new Error("Not authorized to modify this notification");
    }

    await ctx.db.patch(args.notificationId, {
      isRead: true,
      readAt: Date.now(),
    });

    return { success: true };
  },
});

// Mark all notifications as read
export const markAllNotificationsAsRead = mutation({
  args: {},
  handler: async (ctx) => {
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

    const unreadNotifications = await ctx.db
      .query("notifications")
      .withIndex("by_user_unread", (q) => 
        q.eq("userId", user._id).eq("isRead", false)
      )
      .collect();

    for (const notification of unreadNotifications) {
      await ctx.db.patch(notification._id, {
        isRead: true,
        readAt: Date.now(),
      });
    }

    return { success: true, count: unreadNotifications.length };
  },
});

// Create a notification
export const createNotification = mutation({
  args: {
    userId: v.id("users"),
    type: v.union(
      v.literal("deployment_success"),
      v.literal("deployment_failed"),
      v.literal("collaboration_invite"),
      v.literal("contract_shared"),
      v.literal("audit_complete"),
      v.literal("system_update")
    ),
    title: v.string(),
    message: v.string(),
    contractId: v.optional(v.id("contracts")),
    deploymentId: v.optional(v.id("deployments")),
    sessionId: v.optional(v.id("collaborationSessions")),
  },
  handler: async (ctx, args) => {
    const data: any = {};
    if (args.contractId) data.contractId = args.contractId;
    if (args.deploymentId) data.deploymentId = args.deploymentId;
    if (args.sessionId) data.sessionId = args.sessionId;

    const notificationId = await ctx.db.insert("notifications", {
      userId: args.userId,
      type: args.type,
      title: args.title,
      message: args.message,
      data: Object.keys(data).length > 0 ? data : undefined,
      isRead: false,
      createdAt: Date.now(),
    });

    return notificationId;
  },
});

// Delete a notification
export const deleteNotification = mutation({
  args: {
    notificationId: v.id("notifications"),
  },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) {
      throw new Error("Not authenticated");
    }

    const notification = await ctx.db.get(args.notificationId);
    if (!notification) {
      throw new Error("Notification not found");
    }

    const user = await ctx.db
      .query("users")
      .withIndex("by_email", (q) => q.eq("email", identity.email!))
      .first();

    if (!user || notification.userId !== user._id) {
      throw new Error("Not authorized to delete this notification");
    }

    await ctx.db.delete(args.notificationId);

    return { success: true };
  },
});

// Get unread notification count
export const getUnreadNotificationCount = query({
  args: {},
  handler: async (ctx) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) {
      return 0;
    }

    const user = await ctx.db
      .query("users")
      .withIndex("by_email", (q) => q.eq("email", identity.email!))
      .first();

    if (!user) {
      return 0;
    }

    const unreadNotifications = await ctx.db
      .query("notifications")
      .withIndex("by_user_unread", (q) => 
        q.eq("userId", user._id).eq("isRead", false)
      )
      .collect();

    return unreadNotifications.length;
  },
});

// Clean up old notifications
export const cleanupOldNotifications = mutation({
  args: {
    daysOld: v.optional(v.number()),
  },
  handler: async (ctx, args) => {
    const daysOld = args.daysOld || 30;
    const cutoffTime = Date.now() - daysOld * 24 * 60 * 60 * 1000;

    const oldNotifications = await ctx.db
      .query("notifications")
      .withIndex("by_created_at", (q) => q.lt("createdAt", cutoffTime))
      .filter((q) => q.eq(q.field("isRead"), true))
      .collect();

    for (const notification of oldNotifications) {
      await ctx.db.delete(notification._id);
    }

    return { success: true, deleted: oldNotifications.length };
  },
});

// Send system notification to all users
export const sendSystemNotification = mutation({
  args: {
    title: v.string(),
    message: v.string(),
  },
  handler: async (ctx, args) => {
    // This would typically be restricted to admin users
    const users = await ctx.db.query("users").collect();

    const notifications = [];
    for (const user of users) {
      if (user.isActive) {
        const notificationId = await ctx.db.insert("notifications", {
          userId: user._id,
          type: "system_update",
          title: args.title,
          message: args.message,
          isRead: false,
          createdAt: Date.now(),
        });
        notifications.push(notificationId);
      }
    }

    return { success: true, sent: notifications.length };
  },
});