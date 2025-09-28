import { NextRequest, NextResponse } from 'next/server'
import { auth } from '@/lib/auth'
import { userQueries } from '@/lib/db/queries'
import { 
  chatRequestQueries, 
  requestAnalyticsQueries, 
  userPlanQueries,
  dashboardDataQueries 
} from '@/lib/db/chat-queries'

export async function GET(request: NextRequest) {
  try {
    const session = await auth()
    
    if (!session?.user?.email) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    // Get user from database
    const user = await userQueries.findByEmail(session.user.email)
    if (!user) {
      return NextResponse.json({ error: 'User not found' }, { status: 404 })
    }

    // Get or recalculate dashboard data
    let dashboardData = await dashboardDataQueries.getByUserId(user.id)
    if (!dashboardData) {
      dashboardData = await dashboardDataQueries.recalculate(user.id)
    }

    // Get user plan and limits
    const plan = await userPlanQueries.getCurrentPlan(user.id)
    const limits = await userPlanQueries.checkLimits(user.id)

    // Get recent requests
    const recentRequests = await chatRequestQueries.getByUserId(user.id, 10)

    // Get performance metrics
    const performance = await requestAnalyticsQueries.getUserPerformance(user.id)

    // Get usage by time period
    const now = new Date()
    const last7Days = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
    const last30Days = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000)

    const [weeklyStats] = await chatRequestQueries.getUserStats(user.id, last7Days, now)
    const [monthlyStats] = await chatRequestQueries.getUserStats(user.id, last30Days, now)

    return NextResponse.json({
      success: true,
      dashboard: {
        user: {
          id: user.id,
          email: user.email,
          name: user.name,
          plan: user.plan,
          requestsUsed: user.requestsUsed,
          requestsLimit: user.requestsLimit
        },
        metrics: {
          totalRequests: dashboardData?.totalRequests || 0,
          totalTokensUsed: dashboardData?.totalTokensUsed || 0,
          totalCost: dashboardData?.totalCost || 0,
          averageResponseTime: dashboardData?.averageResponseTime || 0,
          requestsThisMonth: dashboardData?.requestsThisMonth || 0,
          requestsToday: dashboardData?.requestsToday || 0
        },
        limits: {
          monthlyUsed: limits.monthlyUsed,
          monthlyLimit: limits.monthlyLimit,
          dailyUsed: limits.dailyUsed,
          dailyLimit: limits.dailyLimit,
          canMakeRequest: limits.canMakeRequest,
          planName: limits.plan
        },
        performance: {
          averageResponseTime: performance?.averageResponseTime || 0,
          successRate: performance?.successRate || 0,
          averageRating: performance?.averageRating || 0,
          totalRequests: performance?.totalRequests || 0
        },
        usage: {
          weekly: {
            requests: weeklyStats?.totalRequests || 0,
            tokens: weeklyStats?.totalTokens || 0,
            cost: weeklyStats?.totalCost || 0
          },
          monthly: {
            requests: monthlyStats?.totalRequests || 0,
            tokens: monthlyStats?.totalTokens || 0,
            cost: monthlyStats?.totalCost || 0
          }
        },
        recentRequests: recentRequests.map(request => ({
          id: request.id,
          prompt: request.prompt.substring(0, 100) + '...',
          status: request.status,
          tokensUsed: request.tokensUsed,
          cost: request.cost,
          duration: request.duration,
          createdAt: request.createdAt?.toISOString()
        })),
        requestsByCategory: dashboardData?.requestsByCategory || {},
        lastCalculatedAt: dashboardData?.lastCalculatedAt?.toISOString()
      }
    })
  } catch (error) {
    console.error('Error getting dashboard data:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

export async function POST(request: NextRequest) {
  try {
    const session = await auth()
    
    if (!session?.user?.email) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    // Get user from database
    const user = await userQueries.findByEmail(session.user.email)
    if (!user) {
      return NextResponse.json({ error: 'User not found' }, { status: 404 })
    }

    // Recalculate dashboard data
    const dashboardData = await dashboardDataQueries.recalculate(user.id)

    return NextResponse.json({
      success: true,
      message: 'Dashboard data recalculated',
      data: dashboardData
    })
  } catch (error) {
    console.error('Error recalculating dashboard data:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
