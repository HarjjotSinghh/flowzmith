"use client"

import { useState, useEffect } from "react"
import { TrendingUp, Zap, Database, Clock, Loader2 } from "lucide-react"

interface StatCardProps {
  title: string
  value: string
  change: string
  icon: React.ReactNode
  trend: "up" | "down" | "neutral"
  loading?: boolean
}

function StatCard({ title, value, change, icon, trend, loading }: StatCardProps) {
  const trendColor = trend === "up" ? "text-green-500" : trend === "down" ? "text-red-500" : "text-muted-foreground"
  
  return (
    <div className="bg-card/50 backdrop-blur-sm rounded-xl border border-border p-6 hover:bg-card/70 transition-all duration-200">
      <div className="flex items-center justify-between mb-4">
        <div className="p-2 bg-primary/10 rounded-lg">
          {icon}
        </div>
        {loading ? (
          <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
        ) : (
          <span className={`text-sm font-medium ${trendColor}`}>
            {change}
          </span>
        )}
      </div>
      <div>
        <p className="text-2xl font-bold text-foreground mb-1">
          {loading ? "..." : value}
        </p>
        <p className="text-sm text-muted-foreground">{title}</p>
      </div>
    </div>
  )
}

interface UsageStatsData {
  apiCallsToday: {
    value: string
    change: string
    trend: "up" | "down" | "neutral"
  }
  tokensProcessed: {
    value: string
    change: string
    trend: "up" | "down" | "neutral"
  }
  avgResponseTime: {
    value: string
    change: string
    trend: "up" | "down" | "neutral"
  }
  successRate: {
    value: string
    change: string
    trend: "up" | "down" | "neutral"
  }
}

export function UsageStats() {
  const [stats, setStats] = useState<UsageStatsData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true)
        const response = await fetch('/api/dashboard/stats')
        
        if (!response.ok) {
          if (response.status === 401) {
            throw new Error('Please log in to view dashboard statistics')
          } else if (response.status === 404) {
            throw new Error('User not found. Please try logging in again')
          } else {
            throw new Error(`Failed to fetch stats (${response.status})`)
          }
        }
        
        const data = await response.json()
        setStats(data)
      } catch (err) {
        console.error('Error fetching usage stats:', err)
        setError(err instanceof Error ? err.message : 'Failed to load stats')
      } finally {
        setLoading(false)
      }
    }

    fetchStats()
  }, [])

  const statsData = stats ? [
    {
      title: "API Calls Today",
      value: stats.apiCallsToday.value,
      change: stats.apiCallsToday.change,
      icon: <Zap className="h-5 w-5 text-primary" />,
      trend: stats.apiCallsToday.trend
    },
    {
      title: "Tokens Processed",
      value: stats.tokensProcessed.value,
      change: stats.tokensProcessed.change,
      icon: <Database className="h-5 w-5 text-primary" />,
      trend: stats.tokensProcessed.trend
    },
    {
      title: "Avg Response Time",
      value: stats.avgResponseTime.value,
      change: stats.avgResponseTime.change,
      icon: <Clock className="h-5 w-5 text-primary" />,
      trend: stats.avgResponseTime.trend
    },
    {
      title: "Success Rate",
      value: stats.successRate.value,
      change: stats.successRate.change,
      icon: <TrendingUp className="h-5 w-5 text-primary" />,
      trend: stats.successRate.trend
    }
  ] : []

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-foreground mb-2">Usage Statistics</h2>
        <p className="text-muted-foreground">Your AI development activity overview</p>
      </div>
      
      {error && (
        <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4">
          <p className="text-red-400 text-sm mb-2">Failed to load usage statistics: {error}</p>
          <button 
            onClick={() => window.location.reload()} 
            className="text-sm text-red-400 hover:text-red-300 underline"
          >
            Retry
          </button>
        </div>
      )}
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {statsData.map((stat, index) => (
          <StatCard key={index} {...stat} loading={loading} />
        ))}
      </div>
    </div>
  )
}
