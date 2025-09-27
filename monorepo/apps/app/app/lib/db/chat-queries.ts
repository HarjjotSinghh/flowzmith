import { eq, and, desc, asc, gte, lte, count, sum, avg } from 'drizzle-orm'
import { db } from './index'
import { 
  chatRequests, 
  userPlans, 
  requestAnalytics, 
  userDashboardData,
  users 
} from './schema'
import type { 
  ChatRequest, 
  NewChatRequest, 
  UserPlan, 
  NewUserPlan, 
  RequestAnalytic, 
  NewRequestAnalytic,
  UserDashboardData,
  NewUserDashboardData
} from './schema'

// Chat requests queries
export const chatRequestQueries = {
  // Create a new chat request
  async create(request: NewChatRequest) {
    const [newRequest] = await db.insert(chatRequests).values(request).returning()
    return newRequest
  },

  // Get requests by user
  async getByUserId(userId: string, limit: number = 50, offset: number = 0) {
    return await db
      .select()
      .from(chatRequests)
      .where(eq(chatRequests.userId, userId))
      .orderBy(desc(chatRequests.createdAt))
      .limit(limit)
      .offset(offset)
  },

  // Get requests by session
  async getBySessionId(sessionId: string) {
    return await db
      .select()
      .from(chatRequests)
      .where(eq(chatRequests.sessionId, sessionId))
      .orderBy(asc(chatRequests.createdAt))
  },

  // Update request status
  async updateStatus(id: string, status: string, response?: string, errorMessage?: string) {
    const [updatedRequest] = await db
      .update(chatRequests)
      .set({ 
        status, 
        response, 
        errorMessage,
        completedAt: status === 'completed' ? new Date() : undefined
      })
      .where(eq(chatRequests.id, id))
      .returning()
    return updatedRequest
  },

  // Update request metrics
  async updateMetrics(id: string, metrics: {
    tokensUsed?: number
    cost?: number
    duration?: number
  }) {
    const [updatedRequest] = await db
      .update(chatRequests)
      .set(metrics)
      .where(eq(chatRequests.id, id))
      .returning()
    return updatedRequest
  },

  // Get user request statistics
  async getUserStats(userId: string, startDate?: Date, endDate?: Date) {
    let query = db
      .select({
        totalRequests: count(),
        totalTokens: sum(chatRequests.tokensUsed),
        totalCost: sum(chatRequests.cost),
        averageDuration: avg(chatRequests.duration)
      })
      .from(chatRequests)
      .where(eq(chatRequests.userId, userId))

    if (startDate) {
      query = query.where(and(
        eq(chatRequests.userId, userId),
        gte(chatRequests.createdAt, startDate)
      ))
    }

    if (endDate) {
      query = query.where(and(
        eq(chatRequests.userId, userId),
        lte(chatRequests.createdAt, endDate)
      ))
    }

    const [stats] = await query
    return stats
  },

  // Get requests by date range
  async getByDateRange(userId: string, startDate: Date, endDate: Date) {
    return await db
      .select()
      .from(chatRequests)
      .where(and(
        eq(chatRequests.userId, userId),
        gte(chatRequests.createdAt, startDate),
        lte(chatRequests.createdAt, endDate)
      ))
      .orderBy(desc(chatRequests.createdAt))
  }
}

// User plans queries
export const userPlanQueries = {
  // Create or update user plan
  async upsert(userId: string, plan: NewUserPlan) {
    // Deactivate current plan
    await db
      .update(userPlans)
      .set({ isActive: false })
      .where(and(
        eq(userPlans.userId, userId),
        eq(userPlans.isActive, true)
      ))

    // Create new plan
    const [newPlan] = await db
      .insert(userPlans)
      .values({ userId, ...plan })
      .returning()
    return newPlan
  },

  // Get user's current plan
  async getCurrentPlan(userId: string) {
    const [plan] = await db
      .select()
      .from(userPlans)
      .where(and(
        eq(userPlans.userId, userId),
        eq(userPlans.isActive, true)
      ))
    return plan
  },

  // Get user's plan history
  async getPlanHistory(userId: string) {
    return await db
      .select()
      .from(userPlans)
      .where(eq(userPlans.userId, userId))
      .orderBy(desc(userPlans.createdAt))
  },

  // Check if user has exceeded limits
  async checkLimits(userId: string) {
    const plan = await this.getCurrentPlan(userId)
    if (!plan) return { canMakeRequest: false, reason: 'No active plan' }

    // Get current usage
    const now = new Date()
    const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1)
    const startOfDay = new Date(now.getFullYear(), now.getMonth(), now.getDate())

    const [monthlyUsage] = await db
      .select({ count: count() })
      .from(chatRequests)
      .where(and(
        eq(chatRequests.userId, userId),
        gte(chatRequests.createdAt, startOfMonth)
      ))

    const [dailyUsage] = await db
      .select({ count: count() })
      .from(chatRequests)
      .where(and(
        eq(chatRequests.userId, userId),
        gte(chatRequests.createdAt, startOfDay)
      ))

    const canMakeRequest = 
      monthlyUsage.count < plan.monthlyRequests &&
      dailyUsage.count < plan.dailyRequests

    return {
      canMakeRequest,
      monthlyUsed: monthlyUsage.count,
      monthlyLimit: plan.monthlyRequests,
      dailyUsed: dailyUsage.count,
      dailyLimit: plan.dailyRequests,
      plan: plan.planName
    }
  }
}

// Request analytics queries
export const requestAnalyticsQueries = {
  // Create analytics record
  async create(analytics: NewRequestAnalytic) {
    const [newAnalytics] = await db
      .insert(requestAnalytics)
      .values(analytics)
      .returning()
    return newAnalytics
  },

  // Get analytics by user
  async getByUserId(userId: string, limit: number = 100) {
    return await db
      .select()
      .from(requestAnalytics)
      .where(eq(requestAnalytics.userId, userId))
      .orderBy(desc(requestAnalytics.createdAt))
      .limit(limit)
  },

  // Get analytics by request
  async getByRequestId(requestId: string) {
    const [analytics] = await db
      .select()
      .from(requestAnalytics)
      .where(eq(requestAnalytics.requestId, requestId))
    return analytics
  },

  // Get user performance metrics
  async getUserPerformance(userId: string, startDate?: Date, endDate?: Date) {
    let query = db
      .select({
        averageResponseTime: avg(requestAnalytics.responseTime),
        successRate: avg(requestAnalytics.wasSuccessful ? 1 : 0),
        averageRating: avg(requestAnalytics.userRating),
        totalRequests: count()
      })
      .from(requestAnalytics)
      .where(eq(requestAnalytics.userId, userId))

    if (startDate) {
      query = query.where(and(
        eq(requestAnalytics.userId, userId),
        gte(requestAnalytics.createdAt, startDate)
      ))
    }

    if (endDate) {
      query = query.where(and(
        eq(requestAnalytics.userId, userId),
        lte(requestAnalytics.createdAt, endDate)
      ))
    }

    const [performance] = await query
    return performance
  }
}

// Dashboard data queries
export const dashboardDataQueries = {
  // Create or update dashboard data
  async upsert(userId: string, data: Partial<NewUserDashboardData>) {
    const [existing] = await db
      .select()
      .from(userDashboardData)
      .where(eq(userDashboardData.userId, userId))

    if (existing) {
      const [updated] = await db
        .update(userDashboardData)
        .set({ ...data, updatedAt: new Date() })
        .where(eq(userDashboardData.userId, userId))
        .returning()
      return updated
    } else {
      const [created] = await db
        .insert(userDashboardData)
        .values({ userId, ...data })
        .returning()
      return created
    }
  },

  // Get dashboard data
  async getByUserId(userId: string) {
    const [data] = await db
      .select()
      .from(userDashboardData)
      .where(eq(userDashboardData.userId, userId))
    return data
  },

  // Recalculate dashboard data
  async recalculate(userId: string) {
    const now = new Date()
    const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1)
    const startOfDay = new Date(now.getFullYear(), now.getMonth(), now.getDate())

    // Get all-time stats
    const [allTimeStats] = await db
      .select({
        totalRequests: count(),
        totalTokens: sum(chatRequests.tokensUsed),
        totalCost: sum(chatRequests.cost),
        averageResponseTime: avg(chatRequests.duration)
      })
      .from(chatRequests)
      .where(eq(chatRequests.userId, userId))

    // Get monthly stats
    const [monthlyStats] = await db
      .select({ count: count() })
      .from(chatRequests)
      .where(and(
        eq(chatRequests.userId, userId),
        gte(chatRequests.createdAt, startOfMonth)
      ))

    // Get daily stats
    const [dailyStats] = await db
      .select({ count: count() })
      .from(chatRequests)
      .where(and(
        eq(chatRequests.userId, userId),
        gte(chatRequests.createdAt, startOfDay)
      ))

    // Get requests by category
    const categoryStats = await db
      .select({
        category: requestAnalytics.category,
        count: count()
      })
      .from(requestAnalytics)
      .where(eq(requestAnalytics.userId, userId))
      .groupBy(requestAnalytics.category)

    const requestsByCategory = categoryStats.reduce((acc, stat) => {
      acc[stat.category || 'uncategorized'] = stat.count
      return acc
    }, {} as Record<string, number>)

    // Update dashboard data
    return await this.upsert(userId, {
      totalRequests: allTimeStats.totalRequests || 0,
      totalTokensUsed: allTimeStats.totalTokens || 0,
      totalCost: allTimeStats.totalCost || 0,
      averageResponseTime: allTimeStats.averageResponseTime || 0,
      requestsByCategory,
      requestsThisMonth: monthlyStats.count || 0,
      requestsToday: dailyStats.count || 0,
      lastCalculatedAt: new Date()
    })
  }
}
