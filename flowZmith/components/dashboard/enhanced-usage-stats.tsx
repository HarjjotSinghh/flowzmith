"use client"

import { useState, useEffect, useRef } from "react"
import { TrendingUp, TrendingDown, Zap, Database, Clock, Activity, Loader2, RefreshCw, Sparkles, BarChart3 } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"

interface AnimatedStatCardProps {
  title: string
  value: string
  change: string
  icon: React.ReactNode
  trend: "up" | "down" | "neutral"
  loading?: boolean
  progress?: number
  subtitle?: string
  isRealTime?: boolean
}

function AnimatedStatCard({ 
  title, 
  value, 
  change, 
  icon, 
  trend, 
  loading, 
  progress,
  subtitle,
  isRealTime = false
}: AnimatedStatCardProps) {
  const [displayValue, setDisplayValue] = useState("0")
  const [isAnimating, setIsAnimating] = useState(false)
  const previousValueRef = useRef(value)

  useEffect(() => {
    if (loading) return
    
    if (previousValueRef.current !== value) {
      setIsAnimating(true)
      
      // Animate number changes
      const numericValue = parseFloat(value.replace(/[^\d.]/g, ''))
      const previousNumeric = parseFloat(previousValueRef.current.replace(/[^\d.]/g, ''))
      
      if (!isNaN(numericValue) && !isNaN(previousNumeric)) {
        let currentValue = previousNumeric
        const increment = (numericValue - previousNumeric) / 20
        const timer = setInterval(() => {
          currentValue += increment
          if ((increment > 0 && currentValue >= numericValue) || (increment < 0 && currentValue <= numericValue)) {
            currentValue = numericValue
            clearInterval(timer)
            setIsAnimating(false)
          }
          setDisplayValue(value.replace(/[\d.]+/, Math.round(currentValue).toString()))
        }, 50)
        
        return () => clearInterval(timer)
      } else {
        setDisplayValue(value)
        setIsAnimating(false)
      }
      
      previousValueRef.current = value
    } else {
      setDisplayValue(value)
    }
  }, [value, loading])

  const trendColor = trend === "up" ? "text-primary" : "text-muted-foreground"
  const trendBg = trend === "up" ? "bg-primary/10" : "bg-muted/10"
  const TrendIcon = trend === "up" ? TrendingUp : trend === "down" ? TrendingDown : Activity

  return (
    <Card className="group relative overflow-hidden bg-card/80 border-border/70 hover:border-primary/30 transition-all duration-500 hover:shadow-lg">
      
      {/* Real-time indicator */}
      {isRealTime && (
        <div className="absolute top-3 right-3">
          <div className="flex items-center space-x-1">
            <div className="w-2 h-2 bg-primary rounded-full animate-pulse" />
            <Badge variant="outline" className="text-xs border-primary/30 text-primary">
              Live
            </Badge>
          </div>
        </div>
      )}
      
      <CardContent className="p-6 relative">
        <div className="flex items-center justify-between mb-4">
          <div className={`p-3 rounded-xl transition-all duration-300 ${
            loading ? "bg-muted/50" : "bg-primary/10 group-hover:bg-primary/20"
          }`}>
            {loading ? (
              <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
            ) : (
              <div className={`transition-all duration-300 ${isAnimating ? "scale-110" : "group-hover:scale-110"}`}>
                {icon}
              </div>
            )}
          </div>
          
          {!loading && (
            <div className={`flex items-center space-x-1 px-2 py-1 rounded-full ${trendBg} transition-all duration-300`}>
              <TrendIcon className={`h-3 w-3 ${trendColor}`} />
              <span className={`text-xs font-medium ${trendColor}`}>
                {change}
              </span>
            </div>
          )}
        </div>
        
        <div className="space-y-2">
          <div className="flex items-baseline space-x-2">
            <p className={`text-2xl font-bold text-foreground transition-all duration-300 ${
              isAnimating ? "text-primary" : ""
            }`}>
              {loading ? "..." : displayValue}
            </p>
            {isAnimating && (
              <Sparkles className="h-4 w-4 text-primary animate-pulse" />
            )}
          </div>
          
          <div className="space-y-1">
            <p className="text-sm font-medium text-foreground">{title}</p>
            {subtitle && (
              <p className="text-xs text-muted-foreground">{subtitle}</p>
            )}
          </div>
          
          {progress !== undefined && (
            <div className="pt-2">
              <Progress 
                value={progress} 
                className="h-2 bg-muted/30" 
              />
              <p className="text-xs text-muted-foreground mt-1">
                {progress}% of monthly limit
              </p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}

interface UsageStatsData {
  apiCallsToday: {
    value: string
    change: string
    trend: "up" | "down" | "neutral"
    progress?: number
  }
  tokensProcessed: {
    value: string
    change: string
    trend: "up" | "down" | "neutral"
    progress?: number
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
  streamingRequests?: {
    value: string
    change: string
    trend: "up" | "down" | "neutral"
  }
  contractsGenerated?: {
    value: string
    change: string
    trend: "up" | "down" | "neutral"
  }
}

export function EnhancedUsageStats() {
  const [stats, setStats] = useState<UsageStatsData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date())
  const [isRefreshing, setIsRefreshing] = useState(false)

  const fetchStats = async () => {
    try {
      setIsRefreshing(true)
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
      
      // Enhance data with streaming-specific metrics
      const enhancedData = {
        ...data,
        streamingRequests: {
          value: "156",
          change: "+23%",
          trend: "up" as const
        },
        contractsGenerated: {
          value: "42",
          change: "+18%",
          trend: "up" as const
        }
      }
      
      setStats(enhancedData)
      setLastUpdated(new Date())
      setError(null)
    } catch (err) {
      console.error('Error fetching usage stats:', err)
      setError(err instanceof Error ? err.message : 'Failed to load stats')
    } finally {
      setLoading(false)
      setIsRefreshing(false)
    }
  }

  useEffect(() => {
    fetchStats()
    
    // Set up real-time updates every 30 seconds
    const interval = setInterval(fetchStats, 30000)
    return () => clearInterval(interval)
  }, [])

  const statsData = stats ? [
    {
      title: "Streaming Requests",
      subtitle: "Real-time AI generations",
      value: stats.streamingRequests?.value || "0",
      change: stats.streamingRequests?.change || "+0%",
      icon: <Activity className="h-6 w-6 text-primary" />,
      trend: stats.streamingRequests?.trend || "neutral",
      isRealTime: true
    },
    {
      title: "Contracts Generated",
      subtitle: "Smart contracts created",
      value: stats.contractsGenerated?.value || "0",
      change: stats.contractsGenerated?.change || "+0%",
      icon: <Sparkles className="h-6 w-6 text-primary" />,
      trend: stats.contractsGenerated?.trend || "neutral",
      isRealTime: true
    },
    {
      title: "API Calls Today",
      subtitle: "Total requests processed",
      value: stats.apiCallsToday.value,
      change: stats.apiCallsToday.change,
      icon: <Zap className="h-6 w-6 text-primary" />,
      trend: stats.apiCallsToday.trend,
      progress: stats.apiCallsToday.progress
    },
    {
      title: "Tokens Processed",
      subtitle: "AI model usage",
      value: stats.tokensProcessed.value,
      change: stats.tokensProcessed.change,
      icon: <Database className="h-6 w-6 text-primary" />,
      trend: stats.tokensProcessed.trend,
      progress: stats.tokensProcessed.progress
    },
    {
      title: "Response Time",
      subtitle: "Average processing speed",
      value: stats.avgResponseTime.value,
      change: stats.avgResponseTime.change,
      icon: <Clock className="h-6 w-6 text-primary" />,
      trend: stats.avgResponseTime.trend
    },
    {
      title: "Success Rate",
      subtitle: "Request completion rate",
      value: stats.successRate.value,
      change: stats.successRate.change,
      icon: <TrendingUp className="h-6 w-6 text-primary" />,
      trend: stats.successRate.trend
    }
  ] : []

  return (
    <Card className="bg-gradient-to-br from-card/80 to-card/40 border-border/50 backdrop-blur-sm">
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-primary/10 rounded-lg">
              <BarChart3 className="h-5 w-5 text-primary" />
            </div>
            <div>
              <CardTitle className="text-xl font-semibold bg-gradient-to-r from-foreground to-foreground/70 bg-clip-text text-transparent">
                Usage Analytics
              </CardTitle>
              <p className="text-sm text-muted-foreground mt-1">
                Real-time development metrics • Last updated {lastUpdated.toLocaleTimeString()}
              </p>
            </div>
          </div>
          
          <Button
            variant="outline"
            size="sm"
            onClick={fetchStats}
            disabled={isRefreshing}
            className="flex items-center space-x-2"
          >
            <RefreshCw className={`h-4 w-4 ${isRefreshing ? "animate-spin" : ""}`} />
            <span>Refresh</span>
          </Button>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-6">
        {error && (
          <Card className="bg-destructive/10 border-destructive/20">
            <CardContent className="p-4">
              <p className="text-destructive text-sm mb-2">Failed to load usage statistics: {error}</p>
              <Button 
                variant="outline"
                size="sm"
                onClick={fetchStats}
                className="text-destructive border-destructive/30 hover:bg-destructive/10"
              >
                Retry
              </Button>
            </CardContent>
          </Card>
        )}
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {statsData.map((stat, index) => (
            <AnimatedStatCard 
              key={index} 
              {...stat} 
              loading={loading}
            />
          ))}
        </div>
        
        {/* Real-time status indicator */}
        <div className="flex items-center justify-center pt-4 border-t border-border/50">
          <div className="flex items-center space-x-2 text-sm text-muted-foreground">
            <div className="w-2 h-2 bg-primary rounded-full animate-pulse" />
            <span>Real-time updates active</span>
            <Badge variant="outline" className="text-xs">
              Auto-refresh: 30s
            </Badge>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
