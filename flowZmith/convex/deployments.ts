import { v } from "convex/values";
import { mutation, query } from "./_generated/server";
import { Doc, Id } from "./_generated/dataModel";

// Start a new deployment
export const startDeployment = mutation({
  args: {
    contractId: v.id("contracts"),
    network: v.string(),
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

    // Check if user has permission to deploy
    if (
      contract.createdBy !== user._id &&
      !contract.collaborators.includes(user._id)
    ) {
      throw new Error("Not authorized to deploy this contract");
    }

    const deploymentId = await ctx.db.insert("deployments", {
      contractId: args.contractId,
      userId: user._id,
      network: args.network,
      status: "pending",
      logs: [
        {
          level: "info",
          message: "Deployment started",
          timestamp: Date.now(),
        },
      ],
      startedAt: Date.now(),
    });

    // Update contract status
    await ctx.db.patch(args.contractId, {
      status: "testing",
      updatedAt: Date.now(),
    });

    // Log analytics
    await ctx.db.insert("analytics", {
      type: "contract_deployed",
      userId: user._id,
      contractId: args.contractId,
      metadata: {
        network: args.network,
        success: false, // Will be updated when deployment completes
      },
      timestamp: Date.now(),
    });

    return deploymentId;
  },
});

// Update deployment status
export const updateDeploymentStatus = mutation({
  args: {
    deploymentId: v.id("deployments"),
    status: v.union(
      v.literal("pending"),
      v.literal("deploying"),
      v.literal("success"),
      v.literal("failed")
    ),
    txHash: v.optional(v.string()),
    contractAddress: v.optional(v.string()),
    gasUsed: v.optional(v.number()),
    cost: v.optional(v.number()),
    error: v.optional(v.string()),
    logMessage: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    const deployment = await ctx.db.get(args.deploymentId);
    if (!deployment) {
      throw new Error("Deployment not found");
    }

    const updateData: any = {
      status: args.status,
    };

    if (args.txHash) updateData.txHash = args.txHash;
    if (args.contractAddress) updateData.contractAddress = args.contractAddress;
    if (args.gasUsed) updateData.gasUsed = args.gasUsed;
    if (args.cost) updateData.cost = args.cost;
    if (args.error) updateData.error = args.error;

    if (args.status === "success" || args.status === "failed") {
      updateData.completedAt = Date.now();
    }

    // Add log entry
    if (args.logMessage) {
      const newLog = {
        level: args.status === "failed" ? "error" : "info",
        message: args.logMessage,
        timestamp: Date.now(),
      };
      updateData.logs = [...deployment.logs, newLog];
    }

    await ctx.db.patch(args.deploymentId, updateData);

    // Update contract status
    const contract = await ctx.db.get(deployment.contractId);
    if (contract) {
      let contractStatus = contract.status;
      if (args.status === "success") {
        contractStatus = "deployed";
        // Update contract with deployment info
        await ctx.db.patch(deployment.contractId, {
          status: contractStatus,
          deploymentAddress: args.contractAddress,
          deploymentTxHash: args.txHash,
          gasUsed: args.gasUsed,
          deploymentCost: args.cost,
          deployedAt: Date.now(),
          updatedAt: Date.now(),
        });
      } else if (args.status === "failed") {
        contractStatus = "failed";
        await ctx.db.patch(deployment.contractId, {
          status: contractStatus,
          updatedAt: Date.now(),
        });
      }

      // Send notification to user
      await ctx.db.insert("notifications", {
        userId: deployment.userId,
        type: args.status === "success" ? "deployment_success" : "deployment_failed",
        title: args.status === "success" ? "Deployment Successful" : "Deployment Failed",
        message: args.status === "success" 
          ? `Contract "${contract.name}" deployed successfully to ${deployment.network}`
          : `Contract "${contract.name}" deployment failed: ${args.error || "Unknown error"}`,
        data: { 
          contractId: deployment.contractId,
          deploymentId: args.deploymentId,
        },
        isRead: false,
        createdAt: Date.now(),
      });
    }

    return { success: true };
  },
});

// Get deployment details
export const getDeployment = query({
  args: { id: v.id("deployments") },
  handler: async (ctx, args) => {
    const deployment = await ctx.db.get(args.id);
    if (!deployment) {
      return null;
    }

    const contract = await ctx.db.get(deployment.contractId);
    const user = await ctx.db.get(deployment.userId);

    return {
      ...deployment,
      contract,
      user,
    };
  },
});

// Get deployments for a contract
export const getContractDeployments = query({
  args: {
    contractId: v.id("contracts"),
    limit: v.optional(v.number()),
  },
  handler: async (ctx, args) => {
    const deployments = await ctx.db
      .query("deployments")
      .withIndex("by_contract", (q) => q.eq("contractId", args.contractId))
      .order("desc")
      .take(args.limit || 20);

    const deploymentsWithUsers = await Promise.all(
      deployments.map(async (deployment) => {
        const user = await ctx.db.get(deployment.userId);
        return {
          ...deployment,
          user,
        };
      })
    );

    return deploymentsWithUsers;
  },
});

// Get user deployments
export const getUserDeployments = query({
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
      .query("deployments")
      .withIndex("by_user", (q) => q.eq("userId", user._id))
      .order("desc");

    if (args.status) {
      query = ctx.db
        .query("deployments")
        .withIndex("by_status", (q) => q.eq("status", args.status as any))
        .filter((q) => q.eq(q.field("userId"), user._id))
        .order("desc");
    }

    const deployments = await query.take(args.limit || 50);

    const deploymentsWithContracts = await Promise.all(
      deployments.map(async (deployment) => {
        const contract = await ctx.db.get(deployment.contractId);
        return {
          ...deployment,
          contract,
        };
      })
    );

    return deploymentsWithContracts;
  },
});

// Get deployment statistics
export const getDeploymentStats = query({
  args: {
    timeframe: v.optional(v.string()), // "24h", "7d", "30d", "all"
  },
  handler: async (ctx, args) => {
    const timeframe = args.timeframe || "30d";
    let cutoffTime = 0;

    switch (timeframe) {
      case "24h":
        cutoffTime = Date.now() - 24 * 60 * 60 * 1000;
        break;
      case "7d":
        cutoffTime = Date.now() - 7 * 24 * 60 * 60 * 1000;
        break;
      case "30d":
        cutoffTime = Date.now() - 30 * 24 * 60 * 60 * 1000;
        break;
      default:
        cutoffTime = 0;
    }

    const deployments = await ctx.db
      .query("deployments")
      .filter((q) => q.gte(q.field("startedAt"), cutoffTime))
      .collect();

    const totalDeployments = deployments.length;
    const successfulDeployments = deployments.filter(
      (d) => d.status === "success"
    ).length;
    const failedDeployments = deployments.filter(
      (d) => d.status === "failed"
    ).length;
    const pendingDeployments = deployments.filter(
      (d) => d.status === "pending" || d.status === "deploying"
    ).length;

    const totalGasUsed = deployments.reduce(
      (sum, d) => sum + (d.gasUsed || 0),
      0
    );
    const totalCost = deployments.reduce((sum, d) => sum + (d.cost || 0), 0);

    // Group by network
    const networkStats = deployments.reduce((acc, d) => {
      if (!acc[d.network]) {
        acc[d.network] = { total: 0, success: 0, failed: 0 };
      }
      acc[d.network].total++;
      if (d.status === "success") acc[d.network].success++;
      if (d.status === "failed") acc[d.network].failed++;
      return acc;
    }, {} as Record<string, { total: number; success: number; failed: number }>);

    // Calculate average deployment time for completed deployments
    const completedDeployments = deployments.filter(
      (d) => d.completedAt && d.startedAt
    );
    const averageDeploymentTime = completedDeployments.length > 0
      ? completedDeployments.reduce(
          (sum, d) => sum + (d.completedAt! - d.startedAt),
          0
        ) / completedDeployments.length
      : 0;

    return {
      totalDeployments,
      successfulDeployments,
      failedDeployments,
      pendingDeployments,
      successRate: totalDeployments > 0 ? successfulDeployments / totalDeployments : 0,
      totalGasUsed,
      totalCost,
      averageDeploymentTime,
      networkStats,
    };
  },
});

// Get recent deployment activity
export const getRecentDeploymentActivity = query({
  args: {
    limit: v.optional(v.number()),
  },
  handler: async (ctx, args) => {
    const deployments = await ctx.db
      .query("deployments")
      .order("desc")
      .take(args.limit || 10);

    const activityWithDetails = await Promise.all(
      deployments.map(async (deployment) => {
        const contract = await ctx.db.get(deployment.contractId);
        const user = await ctx.db.get(deployment.userId);
        return {
          ...deployment,
          contract,
          user,
        };
      })
    );

    return activityWithDetails;
  },
});

// Cancel a pending deployment
export const cancelDeployment = mutation({
  args: {
    deploymentId: v.id("deployments"),
  },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) {
      throw new Error("Not authenticated");
    }

    const deployment = await ctx.db.get(args.deploymentId);
    if (!deployment) {
      throw new Error("Deployment not found");
    }

    const user = await ctx.db
      .query("users")
      .withIndex("by_email", (q) => q.eq("email", identity.email!))
      .first();

    if (!user || deployment.userId !== user._id) {
      throw new Error("Not authorized to cancel this deployment");
    }

    if (deployment.status !== "pending" && deployment.status !== "deploying") {
      throw new Error("Cannot cancel completed deployment");
    }

    await ctx.db.patch(args.deploymentId, {
      status: "failed",
      error: "Cancelled by user",
      completedAt: Date.now(),
      logs: [
        ...deployment.logs,
        {
          level: "info",
          message: "Deployment cancelled by user",
          timestamp: Date.now(),
        },
      ],
    });

    // Update contract status back to draft
    await ctx.db.patch(deployment.contractId, {
      status: "draft",
      updatedAt: Date.now(),
    });

    return { success: true };
  },
});