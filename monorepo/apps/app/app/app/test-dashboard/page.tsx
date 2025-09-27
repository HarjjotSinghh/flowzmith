"use client"

import { useState, useEffect } from "react"

export default function TestDashboard() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const testAPI = async () => {
      try {
        setLoading(true)
        const response = await fetch('/api/dashboard/stats')
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`)
        }
        
        const data = await response.json()
        setStats(data)
        console.log('Dashboard stats:', data)
      } catch (err) {
        console.error('Error fetching stats:', err)
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    testAPI()
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p>Loading dashboard test...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-red-500 mb-4">Error</h1>
          <p className="text-muted-foreground mb-4">{error}</p>
          <button 
            onClick={() => window.location.reload()} 
            className="px-4 py-2 bg-primary text-primary-foreground rounded-lg"
          >
            Retry
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Dashboard API Test</h1>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-card p-6 rounded-lg border">
            <h3 className="text-lg font-semibold mb-2">API Calls Today</h3>
            <p className="text-3xl font-bold text-primary">{stats?.apiCallsToday?.value || '0'}</p>
            <p className="text-sm text-muted-foreground">{stats?.apiCallsToday?.change || '0%'}</p>
          </div>
          
          <div className="bg-card p-6 rounded-lg border">
            <h3 className="text-lg font-semibold mb-2">Tokens Processed</h3>
            <p className="text-3xl font-bold text-primary">{stats?.tokensProcessed?.value || '0K'}</p>
            <p className="text-sm text-muted-foreground">{stats?.tokensProcessed?.change || '0%'}</p>
          </div>
          
          <div className="bg-card p-6 rounded-lg border">
            <h3 className="text-lg font-semibold mb-2">Avg Response Time</h3>
            <p className="text-3xl font-bold text-primary">{stats?.avgResponseTime?.value || '0s'}</p>
            <p className="text-sm text-muted-foreground">{stats?.avgResponseTime?.change || '0%'}</p>
          </div>
          
          <div className="bg-card p-6 rounded-lg border">
            <h3 className="text-lg font-semibold mb-2">Success Rate</h3>
            <p className="text-3xl font-bold text-primary">{stats?.successRate?.value || '0%'}</p>
            <p className="text-sm text-muted-foreground">{stats?.successRate?.change || '0%'}</p>
          </div>
        </div>

        <div className="bg-card p-6 rounded-lg border">
          <h3 className="text-lg font-semibold mb-4">Recent Activity</h3>
          <div className="space-y-3">
            {stats?.recentActivity?.map((activity: any) => (
              <div key={activity.id} className="flex items-start space-x-3 p-3 bg-muted/50 rounded-lg">
                <div className="w-2 h-2 bg-primary rounded-full mt-2"></div>
                <div className="flex-1">
                  <p className="text-sm font-medium">{activity.role === 'user' ? 'User Request' : 'AI Response'}</p>
                  <p className="text-sm text-muted-foreground">{activity.content}</p>
                  <p className="text-xs text-muted-foreground mt-1">
                    {new Date(activity.timestamp).toLocaleString()}
                  </p>
                </div>
              </div>
            )) || (
              <p className="text-muted-foreground">No recent activity</p>
            )}
          </div>
        </div>

        <div className="mt-8 p-4 bg-muted/50 rounded-lg">
          <h3 className="text-lg font-semibold mb-2">Raw API Response</h3>
          <pre className="text-sm text-muted-foreground overflow-auto">
            {JSON.stringify(stats, null, 2)}
          </pre>
        </div>
      </div>
    </div>
  )
}
