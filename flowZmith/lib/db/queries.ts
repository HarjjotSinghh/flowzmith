import { eq, and, desc, asc } from 'drizzle-orm'
import { db } from './index'
import { users, userVariables, userPreferences, userSessions, userActivity, userApiKeys } from './schema'
import type { User, NewUser, UserVariable, NewUserVariable, UserPreference, NewUserPreference } from './schema'

// User queries
export const userQueries = {
  // Create a new user
  async create(user: NewUser) {
    const [newUser] = await db.insert(users).values(user).returning()
    return newUser
  },

  // Find user by email
  async findByEmail(email: string) {
    const [user] = await db.select().from(users).where(eq(users.email, email))
    return user
  },

  // Find user by GitHub ID
  async findByGitHubId(githubId: string) {
    const [user] = await db.select().from(users).where(eq(users.githubId, githubId))
    return user
  },

  // Find user by ID
  async findById(id: string) {
    const [user] = await db.select().from(users).where(eq(users.id, id))
    return user
  },

  // Update user
  async update(id: string, data: Partial<NewUser>) {
    const [updatedUser] = await db
      .update(users)
      .set({ ...data, updatedAt: new Date() })
      .where(eq(users.id, id))
      .returning()
    return updatedUser
  },

  // Delete user
  async delete(id: string) {
    await db.delete(users).where(eq(users.id, id))
  }
}

// User variables queries
export const userVariableQueries = {
  // Create a new user variable
  async create(variable: NewUserVariable) {
    const [newVariable] = await db.insert(userVariables).values(variable).returning()
    return newVariable
  },

  // Get all variables for a user
  async getByUserId(userId: string) {
    return await db
      .select()
      .from(userVariables)
      .where(eq(userVariables.userId, userId))
      .orderBy(asc(userVariables.key))
  },

  // Get variable by key for a user
  async getByKey(userId: string, key: string) {
    const [variable] = await db
      .select()
      .from(userVariables)
      .where(and(eq(userVariables.userId, userId), eq(userVariables.key, key)))
    return variable
  },

  // Update variable
  async update(id: string, data: Partial<NewUserVariable>) {
    const [updatedVariable] = await db
      .update(userVariables)
      .set({ ...data, updatedAt: new Date() })
      .where(eq(userVariables.id, id))
      .returning()
    return updatedVariable
  },

  // Update or create variable
  async upsert(userId: string, key: string, value: string, type: string = 'string', description?: string) {
    const existing = await userVariableQueries.getByKey(userId, key)
    
    if (existing) {
      return await userVariableQueries.update(existing.id, { value, type, description })
    } else {
      return await userVariableQueries.create({
        userId,
        key,
        value,
        type,
        description
      })
    }
  },

  // Delete variable
  async delete(id: string) {
    await db.delete(userVariables).where(eq(userVariables.id, id))
  },

  // Delete variable by key
  async deleteByKey(userId: string, key: string) {
    await db
      .delete(userVariables)
      .where(and(eq(userVariables.userId, userId), eq(userVariables.key, key)))
  }
}

// User preferences queries
export const userPreferenceQueries = {
  // Create or update preferences
  async upsert(userId: string, preferences: Partial<NewUserPreference>) {
    const [existing] = await db
      .select()
      .from(userPreferences)
      .where(eq(userPreferences.userId, userId))

    if (existing) {
      const [updated] = await db
        .update(userPreferences)
        .set({ ...preferences, updatedAt: new Date() })
        .where(eq(userPreferences.userId, userId))
        .returning()
      return updated
    } else {
      const [created] = await db
        .insert(userPreferences)
        .values({ userId, ...preferences })
        .returning()
      return created
    }
  },

  // Get user preferences
  async getByUserId(userId: string) {
    const [preferences] = await db
      .select()
      .from(userPreferences)
      .where(eq(userPreferences.userId, userId))
    return preferences
  }
}

// User sessions queries
export const userSessionQueries = {
  // Create session
  async create(userId: string, sessionToken: string, expiresAt: Date) {
    const [session] = await db
      .insert(userSessions)
      .values({
        userId,
        sessionToken,
        expiresAt
      })
      .returning()
    return session
  },

  // Find session by token
  async findByToken(sessionToken: string) {
    const [session] = await db
      .select()
      .from(userSessions)
      .where(eq(userSessions.sessionToken, sessionToken))
    return session
  },

  // Update session last accessed
  async updateLastAccessed(sessionToken: string) {
    await db
      .update(userSessions)
      .set({ lastAccessed: new Date() })
      .where(eq(userSessions.sessionToken, sessionToken))
  },

  // Delete session
  async delete(sessionToken: string) {
    await db.delete(userSessions).where(eq(userSessions.sessionToken, sessionToken))
  },

  // Delete expired sessions
  async deleteExpired() {
    await db
      .delete(userSessions)
      .where(eq(userSessions.expiresAt, new Date()))
  }
}

// User activity queries
export const userActivityQueries = {
  // Log activity
  async log(userId: string, action: string, details?: any, ipAddress?: string, userAgent?: string) {
    const [activity] = await db
      .insert(userActivity)
      .values({
        userId,
        action,
        details,
        ipAddress,
        userAgent
      })
      .returning()
    return activity
  },

  // Get user activity
  async getByUserId(userId: string, limit: number = 50) {
    return await db
      .select()
      .from(userActivity)
      .where(eq(userActivity.userId, userId))
      .orderBy(desc(userActivity.createdAt))
      .limit(limit)
  }
}

// User API keys queries
export const userApiKeyQueries = {
  // Create API key
  async create(userId: string, name: string, keyHash: string, permissions: string[] = [], expiresAt?: Date) {
    const [apiKey] = await db
      .insert(userApiKeys)
      .values({
        userId,
        name,
        keyHash,
        permissions,
        expiresAt
      })
      .returning()
    return apiKey
  },

  // Get user API keys
  async getByUserId(userId: string) {
    return await db
      .select()
      .from(userApiKeys)
      .where(eq(userApiKeys.userId, userId))
      .orderBy(desc(userApiKeys.createdAt))
  },

  // Find API key by hash
  async findByHash(keyHash: string) {
    const [apiKey] = await db
      .select()
      .from(userApiKeys)
      .where(eq(userApiKeys.keyHash, keyHash))
    return apiKey
  },

  // Update API key
  async update(id: string, data: Partial<typeof userApiKeys.$inferInsert>) {
    const [updated] = await db
      .update(userApiKeys)
      .set({ ...data, updatedAt: new Date() })
      .where(eq(userApiKeys.id, id))
      .returning()
    return updated
  },

  // Delete API key
  async delete(id: string) {
    await db.delete(userApiKeys).where(eq(userApiKeys.id, id))
  }
}
