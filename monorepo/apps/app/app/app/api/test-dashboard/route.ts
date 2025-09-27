import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  try {
    // Return mock data without authentication for testing
    const mockStats = {
      apiCallsToday: {
        value: "42",
        change: "+12.5%",
        trend: "up"
      },
      tokensProcessed: {
        value: "1.2K",
        change: "+8.3%",
        trend: "up"
      },
      avgResponseTime: {
        value: "1.2s",
        change: "-15.2%",
        trend: "up"
      },
      successRate: {
        value: "99.8%",
        change: "+0.1%",
        trend: "up"
      },
      totalRequests: 150,
      weekRequests: 45,
      monthRequests: 120,
      recentActivity: [
        {
          id: "1",
          role: "assistant",
          content: "Generated NFT Marketplace contract with proper access controls and resource management.",
          timestamp: new Date(Date.now() - 2 * 60 * 1000).toISOString()
        },
        {
          id: "2",
          role: "user",
          content: "Create a new contract to sell NFTs to all the people",
          timestamp: new Date(Date.now() - 5 * 60 * 1000).toISOString()
        },
        {
          id: "3",
          role: "assistant",
          content: "Optimized gas usage in Token contract by 23% through efficient storage patterns.",
          timestamp: new Date(Date.now() - 15 * 60 * 1000).toISOString()
        },
        {
          id: "4",
          role: "user",
          content: "hey",
          timestamp: new Date(Date.now() - 30 * 60 * 1000).toISOString()
        },
        {
          id: "5",
          role: "assistant",
          content: "Security audit completed with 95% score. Contract ready for deployment.",
          timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString()
        }
      ]
    }

    return NextResponse.json(mockStats)
  } catch (error) {
    console.error('Test dashboard error:', error)
    return NextResponse.json({ error: 'Failed to fetch test data' }, { status: 500 })
  }
}
