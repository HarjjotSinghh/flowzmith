import { v } from "convex/values";
import { mutation, query } from "./_generated/server";
import { Doc, Id } from "./_generated/dataModel";

// Create a new smart contract
export const createContract = mutation({
  args: {
    name: v.string(),
    description: v.optional(v.string()),
    code: v.string(),
    language: v.string(),
    network: v.string(),
    tags: v.array(v.string()),
    isPublic: v.boolean(),
  },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) {
      throw new Error("Not authenticated");
    }

    // Find or create user
    let user = await ctx.db
      .query("users")
      .withIndex("by_email", (q) => q.eq("email", identity.email!))
      .first();

    if (!user) {
      const userId = await ctx.db.insert("users", {
        email: identity.email!,
        name: identity.name,
        image: identity.pictureUrl,
        createdAt: Date.now(),
        isActive: true,
      });
      user = await ctx.db.get(userId);
    }

    const contractId = await ctx.db.insert("contracts", {
      name: args.name,
      description: args.description,
      code: args.code,
      language: args.language,
      version: "1.0.0",
      createdBy: user!._id,
      collaborators: [],
      status: "draft",
      network: args.network,
      createdAt: Date.now(),
      updatedAt: Date.now(),
      tags: args.tags,
      isPublic: args.isPublic,
    });

    // Create initial version
    await ctx.db.insert("contractVersions", {
      contractId,
      version: "1.0.0",
      code: args.code,
      changelog: "Initial version",
      createdBy: user!._id,
      createdAt: Date.now(),
      isActive: true,
    });

    // Log analytics
    await ctx.db.insert("analytics", {
      type: "contract_created",
      userId: user!._id,
      contractId,
      metadata: {
        network: args.network,
        language: args.language,
        success: true,
      },
      timestamp: Date.now(),
    });

    return contractId;
  },
});

// Get contracts for a user
export const getUserContracts = query({
  args: {
    limit: v.optional(v.number()),
    status: v.optional(v.string()),
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
      .query("contracts")
      .withIndex("by_creator", (q) => q.eq("createdBy", user._id))
      .order("desc");

    if (args.status) {
      query = ctx.db
        .query("contracts")
        .withIndex("by_status", (q) => q.eq("status", args.status as any))
        .filter((q) => q.eq(q.field("createdBy"), user._id))
        .order("desc");
    }

    const contracts = await query.take(args.limit || 50);

    return contracts.map((contract) => ({
      ...contract,
      createdBy: user,
    }));
  },
});

// Get public contracts
export const getPublicContracts = query({
  args: {
    limit: v.optional(v.number()),
    network: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    let query = ctx.db
      .query("contracts")
      .withIndex("by_public", (q) => q.eq("isPublic", true))
      .order("desc");

    if (args.network) {
      query = ctx.db
        .query("contracts")
        .withIndex("by_network", (q) => q.eq("network", args.network!))
        .filter((q) => q.eq(q.field("isPublic"), true))
        .order("desc");
    }

    const contracts = await query.take(args.limit || 20);

    // Get creator info for each contract
    const contractsWithCreators = await Promise.all(
      contracts.map(async (contract) => {
        const creator = await ctx.db.get(contract.createdBy);
        return {
          ...contract,
          createdBy: creator,
        };
      })
    );

    return contractsWithCreators;
  },
});

// Get a specific contract
export const getContract = query({
  args: { id: v.id("contracts") },
  handler: async (ctx, args) => {
    const contract = await ctx.db.get(args.id);
    if (!contract) {
      return null;
    }

    const creator = await ctx.db.get(contract.createdBy);
    const collaborators = await Promise.all(
      contract.collaborators.map((id) => ctx.db.get(id))
    );

    return {
      ...contract,
      createdBy: creator,
      collaborators: collaborators.filter(Boolean),
    };
  },
});

// Update contract code
export const updateContract = mutation({
  args: {
    id: v.id("contracts"),
    code: v.string(),
    changelog: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) {
      throw new Error("Not authenticated");
    }

    const contract = await ctx.db.get(args.id);
    if (!contract) {
      throw new Error("Contract not found");
    }

    const user = await ctx.db
      .query("users")
      .withIndex("by_email", (q) => q.eq("email", identity.email!))
      .first();

    if (!user) {
      throw new Error("User not found");
    }

    // Check if user has permission to edit
    if (
      contract.createdBy !== user._id &&
      !contract.collaborators.includes(user._id)
    ) {
      throw new Error("Not authorized to edit this contract");
    }

    // Update contract
    await ctx.db.patch(args.id, {
      code: args.code,
      updatedAt: Date.now(),
    });

    // Create new version
    const versions = await ctx.db
      .query("contractVersions")
      .withIndex("by_contract", (q) => q.eq("contractId", args.id))
      .collect();

    const nextVersion = `1.${versions.length}.0`;

    await ctx.db.insert("contractVersions", {
      contractId: args.id,
      version: nextVersion,
      code: args.code,
      changelog: args.changelog || "Updated contract code",
      createdBy: user._id,
      createdAt: Date.now(),
      isActive: true,
    });

    // Deactivate previous version
    const activeVersion = versions.find((v) => v.isActive);
    if (activeVersion) {
      await ctx.db.patch(activeVersion._id, { isActive: false });
    }

    return { success: true, version: nextVersion };
  },
});

// Add collaborator to contract
export const addCollaborator = mutation({
  args: {
    contractId: v.id("contracts"),
    userEmail: v.string(),
  },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) {
      throw new Error("Not authenticated");
    }

    const contract = await ctx.db.get(args.contractId);
    if (!contract) {
      throw new Error("Contract not found");
    }

    const owner = await ctx.db
      .query("users")
      .withIndex("by_email", (q) => q.eq("email", identity.email!))
      .first();

    if (!owner || contract.createdBy !== owner._id) {
      throw new Error("Only contract owner can add collaborators");
    }

    const collaborator = await ctx.db
      .query("users")
      .withIndex("by_email", (q) => q.eq("email", args.userEmail))
      .first();

    if (!collaborator) {
      throw new Error("User not found");
    }

    if (contract.collaborators.includes(collaborator._id)) {
      throw new Error("User is already a collaborator");
    }

    await ctx.db.patch(args.contractId, {
      collaborators: [...contract.collaborators, collaborator._id],
    });

    // Send notification
    await ctx.db.insert("notifications", {
      userId: collaborator._id,
      type: "collaboration_invite",
      title: "Collaboration Invitation",
      message: `You've been invited to collaborate on "${contract.name}"`,
      data: { contractId: args.contractId },
      isRead: false,
      createdAt: Date.now(),
    });

    return { success: true };
  },
});

// Search contracts
export const searchContracts = query({
  args: {
    query: v.string(),
    limit: v.optional(v.number()),
  },
  handler: async (ctx, args) => {
    const results = await ctx.db
      .query("contracts")
      .withSearchIndex("search_contracts", (q) =>
        q.search("name", args.query).eq("isPublic", true)
      )
      .take(args.limit || 10);

    // Get creator info for each contract
    const contractsWithCreators = await Promise.all(
      results.map(async (contract) => {
        const creator = await ctx.db.get(contract.createdBy);
        return {
          ...contract,
          createdBy: creator,
        };
      })
    );

    return contractsWithCreators;
  },
});

// Delete contract
export const deleteContract = mutation({
  args: { id: v.id("contracts") },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) {
      throw new Error("Not authenticated");
    }

    const contract = await ctx.db.get(args.id);
    if (!contract) {
      throw new Error("Contract not found");
    }

    const user = await ctx.db
      .query("users")
      .withIndex("by_email", (q) => q.eq("email", identity.email!))
      .first();

    if (!user || contract.createdBy !== user._id) {
      throw new Error("Only contract owner can delete the contract");
    }

    // Delete contract versions
    const versions = await ctx.db
      .query("contractVersions")
      .withIndex("by_contract", (q) => q.eq("contractId", args.id))
      .collect();

    for (const version of versions) {
      await ctx.db.delete(version._id);
    }

    // Delete the contract
    await ctx.db.delete(args.id);

    return { success: true };
  },
});

// Get contract analytics
export const getContractAnalytics = query({
  args: { contractId: v.id("contracts") },
  handler: async (ctx, args) => {
    const contract = await ctx.db.get(args.contractId);
    if (!contract) {
      return null;
    }

    const deployments = await ctx.db
      .query("deployments")
      .withIndex("by_contract", (q) => q.eq("contractId", args.contractId))
      .collect();

    const analytics = await ctx.db
      .query("analytics")
      .withIndex("by_contract", (q) => q.eq("contractId", args.contractId))
      .collect();

    const totalDeployments = deployments.length;
    const successfulDeployments = deployments.filter(
      (d) => d.status === "success"
    ).length;
    const failedDeployments = deployments.filter(
      (d) => d.status === "failed"
    ).length;

    const totalGasUsed = deployments.reduce(
      (sum, d) => sum + (d.gasUsed || 0),
      0
    );
    const totalCost = deployments.reduce((sum, d) => sum + (d.cost || 0), 0);

    return {
      totalDeployments,
      successfulDeployments,
      failedDeployments,
      successRate: totalDeployments > 0 ? successfulDeployments / totalDeployments : 0,
      totalGasUsed,
      totalCost,
      recentActivity: analytics.slice(-10),
    };
  },
});