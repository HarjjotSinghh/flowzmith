import { NextResponse } from 'next/server'
import { healthCheck } from '@/lib/db/utils'

export async function GET() {
  try {
    const [connectionResult, statsResult] = await Promise.all([
      healthCheck.checkDatabase(),
      healthCheck.getDatabaseStats()
    ])

    return NextResponse.json({
      success: true,
      database: connectionResult,
      stats: statsResult,
      timestamp: new Date().toISOString()
    })
  } catch (error) {
    console.error('Database health check error:', error)
    return NextResponse.json(
      { 
        success: false, 
        error: 'Database health check failed',
        timestamp: new Date().toISOString()
      },
      { status: 500 }
    )
  }
}
