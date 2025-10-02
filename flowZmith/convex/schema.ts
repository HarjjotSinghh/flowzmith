import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  // Users table for authentication and user management
  users: defineTable({
    email: v.string(),
    name: v.optional(v.string()),
    image: v.optional(v.string()),
    githubId: v.optional(v.string()),
    walletAddress: v.optional(v.string()),
    createdAt: v.number(),
    lastLoginAt: v.optional(v.number()),
    isActive: v.boolean(),
    preferences: v.optional(v.object({
      theme: v.optional(v.string()),
      notifications: v.optional(v.boolean()),
      defaultNetwork: v.optional(v.string()),
    })),
  })
    .index("by_email", ["email"])
    .index("by_github_id", ["githubId"])
    .index("by_wallet_address", ["walletAddress"]),

  // Smart contracts table
  contracts: defineTable({
    name: v.string(),
    description: v.optional(v.string()),
    code: v.string(),
    language: v.string(), // "cadence", "solidity", etc.
    version: v.string(),
    createdBy: v.id("users"),
    collaborators: v.array(v.id("users")),
    status: v.union(
      v.literal("draft"),
      v.literal("testing"),
      v.literal("deployed"),
      v.literal("failed"),
      v.literal("archived")
    ),
    network: v.string(), // "flow-testnet", "flow-mainnet", etc.
    deploymentAddress: v.optional(v.string()),
    deploymentTxHash: v.optional(v.string()),
    gasUsed: v.optional(v.number()),
    deploymentCost: v.optional(v.number()),
    createdAt: v.number(),
    updatedAt: v.number(),
    deployedAt: v.optional(v.number()),
    tags: v.array(v.string()),
    isPublic: v.boolean(),
    ipfsHash: v.optional(v.string()),
    auditResults: v.optional(v.object({
      score: v.number(),
      issues: v.array(v.object({
        severity: v.string(),
        message: v.string(),
        line: v.optional(v.number()),
      })),
      lastAuditAt: v.number(),
    })),
    metadata: v.optional(v.object({
      functions: v.array(v.string()),
      events: v.array(v.string()),
      dependencies: v.array(v.string()),
      complexity: v.optional(v.number()),
    })),
  })
    .index("by_creator", ["createdBy"])
    .index("by_status", ["status"])
    .index("by_network", ["network"])
    .index("by_created_at", ["createdAt"])
    .index("by_public", ["isPublic"])
    .searchIndex("search_contracts", {
      searchField: "name",
      filterFields: ["createdBy", "status", "network", "isPublic"],
    }),

  // Contract versions for version control
  contractVersions: defineTable({
    contractId: v.id("contracts"),
    version: v.string(),
    code: v.string(),
    changelog: v.optional(v.string()),
    createdBy: v.id("users"),
    createdAt: v.number(),
    isActive: v.boolean(),
  })
    .index("by_contract", ["contractId"])
    .index("by_contract_version", ["contractId", "version"]),

  // Real-time collaboration sessions
  collaborationSessions: defineTable({
    contractId: v.id("contracts"),
    participants: v.array(v.object({
      userId: v.id("users"),
      joinedAt: v.number(),
      lastActiveAt: v.number(),
      cursor: v.optional(v.object({
        line: v.number(),
        column: v.number(),
      })),
      selection: v.optional(v.object({
        start: v.object({ line: v.number(), column: v.number() }),
        end: v.object({ line: v.number(), column: v.number() }),
      })),
    })),
    isActive: v.boolean(),
    createdAt: v.number(),
    lastActivityAt: v.number(),
  })
    .index("by_contract", ["contractId"])
    .index("by_active", ["isActive"]),

  // Real-time code changes for collaboration
  codeChanges: defineTable({
    sessionId: v.id("collaborationSessions"),
    contractId: v.id("contracts"),
    userId: v.id("users"),
    changeType: v.union(
      v.literal("insert"),
      v.literal("delete"),
      v.literal("replace")
    ),
    position: v.object({
      line: v.number(),
      column: v.number(),
    }),
    content: v.string(),
    timestamp: v.number(),
    applied: v.boolean(),
  })
    .index("by_session", ["sessionId"])
    .index("by_contract", ["contractId"])
    .index("by_timestamp", ["timestamp"]),

  // Deployment logs and analytics
  deployments: defineTable({
    contractId: v.id("contracts"),
    userId: v.id("users"),
    network: v.string(),
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
    logs: v.array(v.object({
      level: v.string(),
      message: v.string(),
      timestamp: v.number(),
    })),
    startedAt: v.number(),
    completedAt: v.optional(v.number()),
    metadata: v.optional(v.object({
      flowCliVersion: v.optional(v.string()),
      nodeVersion: v.optional(v.string()),
      environment: v.optional(v.string()),
    })),
  })
    .index("by_contract", ["contractId"])
    .index("by_user", ["userId"])
    .index("by_status", ["status"])
    .index("by_network", ["network"])
    .index("by_started_at", ["startedAt"]),

  // Real-time notifications
  notifications: defineTable({
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
    data: v.optional(v.object({
      contractId: v.optional(v.id("contracts")),
      deploymentId: v.optional(v.id("deployments")),
      sessionId: v.optional(v.id("collaborationSessions")),
    })),
    isRead: v.boolean(),
    createdAt: v.number(),
    readAt: v.optional(v.number()),
  })
    .index("by_user", ["userId"])
    .index("by_user_unread", ["userId", "isRead"])
    .index("by_created_at", ["createdAt"]),

  // Analytics and metrics
  analytics: defineTable({
    type: v.union(
      v.literal("contract_created"),
      v.literal("contract_deployed"),
      v.literal("collaboration_started"),
      v.literal("user_login"),
      v.literal("api_call"),
      v.literal("error_occurred")
    ),
    userId: v.optional(v.id("users")),
    contractId: v.optional(v.id("contracts")),
    metadata: v.object({
      userAgent: v.optional(v.string()),
      ip: v.optional(v.string()),
      duration: v.optional(v.number()),
      error: v.optional(v.string()),
      language: v.optional(v.string()),
      network: v.optional(v.string()),
      success: v.optional(v.boolean()),
    }),
    timestamp: v.number(),
  })
    .index("by_type", ["type"])
    .index("by_user", ["userId"])
    .index("by_timestamp", ["timestamp"])
    .index("by_contract", ["contractId"]),

  // Documentation and knowledge base
  documentation: defineTable({
    title: v.string(),
    content: v.string(),
    category: v.string(),
    tags: v.array(v.string()),
    source: v.optional(v.string()), // "firecrawl", "manual", "api"
    url: v.optional(v.string()),
    lastCrawledAt: v.optional(v.number()),
    createdBy: v.optional(v.id("users")),
    createdAt: v.number(),
    updatedAt: v.number(),
    isActive: v.boolean(),
    priority: v.number(), // for search ranking
  })
    .index("by_category", ["category"])
    .index("by_source", ["source"])
    .index("by_updated_at", ["updatedAt"])
    .searchIndex("search_docs", {
      searchField: "content",
      filterFields: ["category", "isActive"],
    }),

  // API usage tracking
  apiUsage: defineTable({
    userId: v.optional(v.id("users")),
    endpoint: v.string(),
    method: v.string(),
    statusCode: v.number(),
    responseTime: v.number(),
    timestamp: v.number(),
    userAgent: v.optional(v.string()),
    ip: v.optional(v.string()),
  })
    .index("by_user", ["userId"])
    .index("by_endpoint", ["endpoint"])
    .index("by_timestamp", ["timestamp"]),
});