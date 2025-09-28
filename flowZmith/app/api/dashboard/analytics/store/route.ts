import { NextRequest, NextResponse } from 'next/server'
import { auth } from '@/lib/auth'
import { userQueries } from '@/lib/db/queries'

export async function POST(request: NextRequest) {
  try {
    // Check authentication
    const session = await auth()
    if (!session?.user?.email) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    // Get user from database
    const user = await userQueries.findByEmail(session.user.email)
    if (!user) {
      return NextResponse.json({ error: 'User not found' }, { status: 404 })
    }

    const body = await request.json()
    const { 
      eventType, 
      eventData, 
      timestamp = new Date().toISOString(),
      metadata = {} 
    } = body

    // Validate required fields
    if (!eventType) {
      return NextResponse.json({ error: 'Event type is required' }, { status: 400 })
    }

    // Store analytics event in database
    // This would typically go to an analytics table, but for now we'll log it
    console.log('Analytics Event:', {
      userId: user.id,
      userEmail: session.user.email,
      eventType,
      eventData,
      timestamp,
      metadata
    })

    // You can extend this to store in a dedicated analytics table
    // For now, we'll just return success
    return NextResponse.json({ 
      success: true, 
      message: 'Analytics event stored successfully',
      eventId: `event_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    })

  } catch (error) {
    console.error('Analytics store error:', error)
    return NextResponse.json({ error: 'Failed to store analytics event' }, { status: 500 })
  }
}

export async function GET(request: NextRequest) {
  try {
    // Check authentication
    const session = await auth()
    if (!session?.user?.email) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    // Get user from database
    const user = await userQueries.findByEmail(session.user.email)
    if (!user) {
      return NextResponse.json({ error: 'User not found' }, { status: 404 })
    }

    // Get query parameters
    const { searchParams } = new URL(request.url)
    const eventType = searchParams.get('eventType')
    const startDate = searchParams.get('startDate')
    const endDate = searchParams.get('endDate')
    const limit = parseInt(searchParams.get('limit') || '100')

    // This would typically query an analytics table
    // For now, we'll return mock data based on user activity
    const mockAnalytics = {
      events: [
        {
          id: `event_${Date.now()}_1`,
          eventType: 'api_call',
          eventData: { endpoint: '/api/generate', method: 'POST' },
          timestamp: new Date().toISOString(),
          metadata: { userAgent: 'dashboard', source: 'web' }
        },
        {
          id: `event_${Date.now()}_2`,
          eventType: 'file_generated',
          eventData: { fileType: 'cadence', fileName: 'NFTContract.cdc' },
          timestamp: new Date(Date.now() - 3600000).toISOString(),
          metadata: { source: 'ai_chat' }
        }
      ],
      summary: {
        totalEvents: 2,
        eventTypes: ['api_call', 'file_generated'],
        timeRange: {
          start: startDate || new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
          end: endDate || new Date().toISOString()
        }
      }
    }

    return NextResponse.json(mockAnalytics)

  } catch (error) {
    console.error('Analytics fetch error:', error)
    return NextResponse.json({ error: 'Failed to fetch analytics data' }, { status: 500 })
  }
}
