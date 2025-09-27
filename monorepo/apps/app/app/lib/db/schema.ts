import { pgTable, text, timestamp, uuid, jsonb, integer, boolean, varchar } from 'drizzle-orm/pg-core'
import { relations } from 'drizzle-orm'

// Users table
export const users = pgTable('users', {
  id: uuid('id').primaryKey().defaultRandom(),
  email: text('email').notNull().unique(),
  name: text('name'),
  image: text('image'),
  githubId: text('github_id').unique(),
  // User plan and subscription details
  plan: varchar('plan', { length: 20 }).default('free'), // free, pro, enterprise
  planExpiresAt: timestamp('plan_expires_at'),
  requestsUsed: integer('requests_used').default(0),
  requestsLimit: integer('requests_limit').default(100), // Monthly limit
  // User status and preferences
  isActive: boolean('is_active').default(true),
  lastLoginAt: timestamp('last_login_at'),
  createdAt: timestamp('created_at').defaultNow().notNull(),
  updatedAt: timestamp('updated_at').defaultNow().notNull(),
})

// User variables table for storing user-specific data
export const userVariables = pgTable('user_variables', {
  id: uuid('id').primaryKey().defaultRandom(),
  userId: uuid('user_id').notNull().references(() => users.id, { onDelete: 'cascade' }),
  key: varchar('key', { length: 255 }).notNull(),
  value: text('value'),
  jsonValue: jsonb('json_value'),
  type: varchar('type', { length: 50 }).notNull().default('string'), // string, number, boolean, json
  description: text('description'),
  isPublic: boolean('is_public').default(false),
  createdAt: timestamp('created_at').defaultNow().notNull(),
  updatedAt: timestamp('updated_at').defaultNow().notNull(),
})

// User preferences table
export const userPreferences = pgTable('user_preferences', {
  id: uuid('id').primaryKey().defaultRandom(),
  userId: uuid('user_id').notNull().references(() => users.id, { onDelete: 'cascade' }),
  theme: varchar('theme', { length: 20 }).default('system'), // light, dark, system
  language: varchar('language', { length: 10 }).default('en'),
  timezone: varchar('timezone', { length: 50 }).default('UTC'),
  notifications: jsonb('notifications').default({}),
  createdAt: timestamp('created_at').defaultNow().notNull(),
  updatedAt: timestamp('updated_at').defaultNow().notNull(),
})

// User sessions table for tracking active sessions
export const userSessions = pgTable('user_sessions', {
  id: uuid('id').primaryKey().defaultRandom(),
  userId: uuid('user_id').notNull().references(() => users.id, { onDelete: 'cascade' }),
  sessionToken: text('session_token').notNull().unique(),
  expiresAt: timestamp('expires_at').notNull(),
  createdAt: timestamp('created_at').defaultNow().notNull(),
  lastAccessed: timestamp('last_accessed').defaultNow().notNull(),
})

// User activity logs
export const userActivity = pgTable('user_activity', {
  id: uuid('id').primaryKey().defaultRandom(),
  userId: uuid('user_id').notNull().references(() => users.id, { onDelete: 'cascade' }),
  action: varchar('action', { length: 100 }).notNull(), // login, logout, contract_created, etc.
  details: jsonb('details'),
  ipAddress: text('ip_address'),
  userAgent: text('user_agent'),
  createdAt: timestamp('created_at').defaultNow().notNull(),
})

// User API keys for external integrations
export const userApiKeys = pgTable('user_api_keys', {
  id: uuid('id').primaryKey().defaultRandom(),
  userId: uuid('user_id').notNull().references(() => users.id, { onDelete: 'cascade' }),
  name: varchar('name', { length: 100 }).notNull(),
  keyHash: text('key_hash').notNull(),
  permissions: jsonb('permissions').default([]),
  lastUsed: timestamp('last_used'),
  expiresAt: timestamp('expires_at'),
  isActive: boolean('is_active').default(true),
  createdAt: timestamp('created_at').defaultNow().notNull(),
  updatedAt: timestamp('updated_at').defaultNow().notNull(),
})

// Chat requests table for tracking all chat interactions
export const chatRequests = pgTable('chat_requests', {
  id: uuid('id').primaryKey().defaultRandom(),
  userId: uuid('user_id').notNull().references(() => users.id, { onDelete: 'cascade' }),
  sessionId: text('session_id'), // Group related requests in a session
  // Request details
  prompt: text('prompt').notNull(),
  response: text('response'),
  // Request metadata
  model: varchar('model', { length: 50 }).default('gpt-4'),
  tokensUsed: integer('tokens_used').default(0),
  cost: integer('cost').default(0), // Cost in cents
  duration: integer('duration').default(0), // Duration in milliseconds
  // Request status
  status: varchar('status', { length: 20 }).default('pending'), // pending, completed, failed, cancelled
  errorMessage: text('error_message'),
  // Request context
  ipAddress: text('ip_address'),
  userAgent: text('user_agent'),
  // Timestamps
  startedAt: timestamp('started_at').defaultNow().notNull(),
  completedAt: timestamp('completed_at'),
  createdAt: timestamp('created_at').defaultNow().notNull(),
})

// User plans table for subscription management
export const userPlans = pgTable('user_plans', {
  id: uuid('id').primaryKey().defaultRandom(),
  userId: uuid('user_id').notNull().references(() => users.id, { onDelete: 'cascade' }),
  planName: varchar('plan_name', { length: 50 }).notNull(), // free, pro, enterprise
  // Plan limits
  monthlyRequests: integer('monthly_requests').notNull(),
  dailyRequests: integer('daily_requests').notNull(),
  maxTokensPerRequest: integer('max_tokens_per_request').notNull(),
  // Plan features
  features: jsonb('features').default([]), // Array of feature names
  // Plan status
  isActive: boolean('is_active').default(true),
  // Billing
  pricePerMonth: integer('price_per_month').default(0), // Price in cents
  billingCycle: varchar('billing_cycle', { length: 20 }).default('monthly'),
  // Timestamps
  startsAt: timestamp('starts_at').defaultNow().notNull(),
  expiresAt: timestamp('expires_at'),
  createdAt: timestamp('created_at').defaultNow().notNull(),
  updatedAt: timestamp('updated_at').defaultNow().notNull(),
})

// Request analytics table for detailed tracking
export const requestAnalytics = pgTable('request_analytics', {
  id: uuid('id').primaryKey().defaultRandom(),
  userId: uuid('user_id').notNull().references(() => users.id, { onDelete: 'cascade' }),
  requestId: uuid('request_id').notNull().references(() => chatRequests.id, { onDelete: 'cascade' }),
  // Analytics data
  requestType: varchar('request_type', { length: 50 }).notNull(), // chat, code_generation, analysis
  category: varchar('category', { length: 50 }), // nft, token, marketplace, etc.
  complexity: varchar('complexity', { length: 20 }).default('medium'), // low, medium, high
  // Performance metrics
  responseTime: integer('response_time').notNull(), // Milliseconds
  tokensInput: integer('tokens_input').default(0),
  tokensOutput: integer('tokens_output').default(0),
  // Quality metrics
  userRating: integer('user_rating'), // 1-5 rating
  wasSuccessful: boolean('was_successful').default(true),
  // Timestamps
  createdAt: timestamp('created_at').defaultNow().notNull(),
})

// User dashboard data table for caching dashboard metrics
export const userDashboardData = pgTable('user_dashboard_data', {
  id: uuid('id').primaryKey().defaultRandom(),
  userId: uuid('user_id').notNull().references(() => users.id, { onDelete: 'cascade' }),
  // Dashboard metrics
  totalRequests: integer('total_requests').default(0),
  totalTokensUsed: integer('total_tokens_used').default(0),
  totalCost: integer('total_cost').default(0),
  averageResponseTime: integer('average_response_time').default(0),
  // Usage by category
  requestsByCategory: jsonb('requests_by_category').default({}),
  // Time-based data
  requestsThisMonth: integer('requests_this_month').default(0),
  requestsToday: integer('requests_today').default(0),
  // Last updated
  lastCalculatedAt: timestamp('last_calculated_at').defaultNow().notNull(),
  createdAt: timestamp('created_at').defaultNow().notNull(),
  updatedAt: timestamp('updated_at').defaultNow().notNull(),
})

// Define relations
export const usersRelations = relations(users, ({ many }) => ({
  variables: many(userVariables),
  preferences: many(userPreferences),
  sessions: many(userSessions),
  activity: many(userActivity),
  apiKeys: many(userApiKeys),
  chatRequests: many(chatRequests),
  plans: many(userPlans),
  analytics: many(requestAnalytics),
  dashboardData: many(userDashboardData),
}))

export const userVariablesRelations = relations(userVariables, ({ one }) => ({
  user: one(users, {
    fields: [userVariables.userId],
    references: [users.id],
  }),
}))

export const userPreferencesRelations = relations(userPreferences, ({ one }) => ({
  user: one(users, {
    fields: [userPreferences.userId],
    references: [users.id],
  }),
}))

export const userSessionsRelations = relations(userSessions, ({ one }) => ({
  user: one(users, {
    fields: [userSessions.userId],
    references: [users.id],
  }),
}))

export const userActivityRelations = relations(userActivity, ({ one }) => ({
  user: one(users, {
    fields: [userActivity.userId],
    references: [users.id],
  }),
}))

export const userApiKeysRelations = relations(userApiKeys, ({ one }) => ({
  user: one(users, {
    fields: [userApiKeys.userId],
    references: [users.id],
  }),
}))

export const chatRequestsRelations = relations(chatRequests, ({ one, many }) => ({
  user: one(users, {
    fields: [chatRequests.userId],
    references: [users.id],
  }),
  analytics: many(requestAnalytics),
}))

export const userPlansRelations = relations(userPlans, ({ one }) => ({
  user: one(users, {
    fields: [userPlans.userId],
    references: [users.id],
  }),
}))

export const requestAnalyticsRelations = relations(requestAnalytics, ({ one }) => ({
  user: one(users, {
    fields: [requestAnalytics.userId],
    references: [users.id],
  }),
  request: one(chatRequests, {
    fields: [requestAnalytics.requestId],
    references: [chatRequests.id],
  }),
}))

export const userDashboardDataRelations = relations(userDashboardData, ({ one }) => ({
  user: one(users, {
    fields: [userDashboardData.userId],
    references: [users.id],
  }),
}))

// Type exports for TypeScript
export type User = typeof users.$inferSelect
export type NewUser = typeof users.$inferInsert
export type UserVariable = typeof userVariables.$inferSelect
export type NewUserVariable = typeof userVariables.$inferInsert
export type UserPreference = typeof userPreferences.$inferSelect
export type NewUserPreference = typeof userPreferences.$inferInsert
export type UserSession = typeof userSessions.$inferSelect
export type NewUserSession = typeof userSessions.$inferInsert
export type UserActivity = typeof userActivity.$inferSelect
export type NewUserActivity = typeof userActivity.$inferInsert
export type UserApiKey = typeof userApiKeys.$inferSelect
export type NewUserApiKey = typeof userApiKeys.$inferInsert
export type ChatRequest = typeof chatRequests.$inferSelect
export type NewChatRequest = typeof chatRequests.$inferInsert
export type UserPlan = typeof userPlans.$inferSelect
export type NewUserPlan = typeof userPlans.$inferInsert
export type RequestAnalytic = typeof requestAnalytics.$inferSelect
export type NewRequestAnalytic = typeof requestAnalytics.$inferInsert
export type UserDashboardData = typeof userDashboardData.$inferSelect
export type NewUserDashboardData = typeof userDashboardData.$inferInsert
