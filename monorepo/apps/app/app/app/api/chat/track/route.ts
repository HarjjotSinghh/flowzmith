import { NextRequest, NextResponse } from 'next/server'
import { auth } from '@/lib/auth'
import { userQueries } from '@/lib/db/queries'
import { chatRequestQueries, requestAnalyticsQueries, userPlanQueries } from '@/lib/db/chat-queries'

export async function POST(request: NextRequest) {
  try {
    const session = await auth()
    
    if (!session?.user?.email) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const body = await request.json()
    const { 
      prompt, 
      sessionId, 
      model = 'gpt-4',
      requestType = 'chat',
      category,
      complexity = 'medium'
    } = body

    if (!prompt) {
      return NextResponse.json({ error: 'Prompt is required' }, { status: 400 })
    }

    // Get user from database
    const user = await userQueries.findByEmail(session.user.email)
    if (!user) {
      return NextResponse.json({ error: 'User not found' }, { status: 404 })
    }

    // Check user limits
    const limits = await userPlanQueries.checkLimits(user.id)
    if (!limits.canMakeRequest) {
      return NextResponse.json({ 
        error: 'Request limit exceeded',
        details: limits
      }, { status: 429 })
    }

    // Create chat request record
    const chatRequest = await chatRequestQueries.create({
      userId: user.id,
      sessionId,
      prompt,
      model,
      status: 'pending',
      ipAddress: request.headers.get('x-forwarded-for') || request.headers.get('x-real-ip'),
      userAgent: request.headers.get('user-agent')
    })

    return NextResponse.json({
      success: true,
      requestId: chatRequest.id,
      limits: {
        monthlyUsed: limits.monthlyUsed,
        monthlyLimit: limits.monthlyLimit,
        dailyUsed: limits.dailyUsed,
        dailyLimit: limits.dailyLimit
      }
    })
  } catch (error) {
    console.error('Error tracking chat request:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

export async function PUT(request: NextRequest) {
  try {
    const session = await auth()
    
    if (!session?.user?.email) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const body = await request.json()
    const { 
      requestId, 
      status, 
      response, 
      tokensUsed, 
      cost, 
      duration,
      userRating,
      errorMessage 
    } = body

    if (!requestId) {
      return NextResponse.json({ error: 'Request ID is required' }, { status: 400 })
    }

    // Get user from database
    const user = await userQueries.findByEmail(session.user.email)
    if (!user) {
      return NextResponse.json({ error: 'User not found' }, { status: 404 })
    }

    // Update chat request
    const updatedRequest = await chatRequestQueries.updateStatus(
      requestId, 
      status, 
      response, 
      errorMessage
    )

    // Update metrics if provided
    if (tokensUsed || cost || duration) {
      await chatRequestQueries.updateMetrics(requestId, {
        tokensUsed,
        cost,
        duration
      })
    }

    // Create analytics record if request completed
    if (status === 'completed' && response) {
      await requestAnalyticsQueries.create({
        userId: user.id,
        requestId,
        requestType: body.requestType || 'chat',
        category: body.category,
        complexity: body.complexity || 'medium',
        responseTime: duration || 0,
        tokensInput: body.tokensInput || 0,
        tokensOutput: tokensUsed || 0,
        userRating,
        wasSuccessful: true
      })
    }

    return NextResponse.json({
      success: true,
      request: updatedRequest
    })
  } catch (error) {
    console.error('Error updating chat request:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
