"use client"

import { useState, useEffect } from "react"
import { TrendingUp, Zap, Database, Clock, Loader2 } from "lucide-react"
import { motion } from "framer-motion"

interface StatCardProps {
  title: string
  value: string
  change: string
  icon: React.ReactNode
  trend: "up" | "down" | "neutral"
  loading?: boolean
  index: number
}

function StatCard({ title, value, change, icon, trend, loading, index }: StatCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, filter: "blur(8px)", y: 10 }}
      animate={{ opacity: 1, filter: "blur(0px)", y: 0 }}
      transition={{ delay: index * 0.1, duration: 0.4 }}
      whileHover={{ y: -4, backgroundColor: "hsl(var(--muted)/0.1)" }}
      className="bg-background border-2 border-foreground p-4 relative group transition-all"
    >
      <div className="flex items-center justify-between mb-4">
        <div className="h-10 w-10 bg-black flex items-center justify-center border border-foreground group-hover:bg-accent group-hover:border-black transition-colors duration-300">
          <div className="group-hover:text-black transition-colors duration-300">
            {icon}
          </div>
        </div>
        {loading ? (
          <Loader2 className="h-4 w-4 animate-spin text-accent" />
        ) : (
            <motion.span
              initial={{ scale: 0.9 }}
              animate={{ scale: 1 }}
              className={`text-[10px] font-black px-1 ${trend === 'up' ? 'bg-accent text-black' : 'bg-black text-white'}`}
            >
            {change}
            </motion.span>
        )}
      </div>
      <div>
        <p className="text-2xl font-black text-foreground mb-1 tracking-tighter uppercase group-hover:text-accent transition-colors duration-300">
          {loading ? "..." : value}
        </p>
        <p className="text-[10px] font-black text-foreground/80 uppercase tracking-widest group-hover:text-foreground transition-colors duration-300">{title}</p>
      </div>
      <motion.div
        className="absolute bottom-0 right-0 w-2 h-2 bg-foreground"
        whileHover={{ backgroundColor: "hsl(var(--accent))" }}
      />
    </motion.div>
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
          throw new Error(`Failed to fetch stats (${response.status})`)
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
      title: "API CALLS 24H",
      value: stats.apiCallsToday.value,
      change: stats.apiCallsToday.change,
      icon: <Zap className="h-5 w-5 text-accent" />,
      trend: stats.apiCallsToday.trend
    },
    {
      title: "TOKENS PROCESSED",
      value: stats.tokensProcessed.value,
      change: stats.tokensProcessed.change,
      icon: <Database className="h-5 w-5 text-accent" />,
      trend: stats.tokensProcessed.trend
    },
    {
      title: "AVG LATENCY",
      value: stats.avgResponseTime.value,
      change: stats.avgResponseTime.change,
      icon: <Clock className="h-5 w-5 text-accent" />,
      trend: stats.avgResponseTime.trend
    },
    {
      title: "SUCCESS RATE",
      value: stats.successRate.value,
      change: stats.successRate.change,
      icon: <TrendingUp className="h-5 w-5 text-accent" />,
      trend: stats.successRate.trend
    }
  ] : [
    { title: "API CALLS 24H", value: "0", change: "+0%", icon: <Zap className="h-5 w-5 text-accent" />, trend: "neutral" as const },
    { title: "TOKENS PROCESSED", value: "0", change: "+0%", icon: <Database className="h-5 w-5 text-accent" />, trend: "neutral" as const },
    { title: "AVG LATENCY", value: "0ms", change: "0%", icon: <Clock className="h-5 w-5 text-accent" />, trend: "neutral" as const },
    { title: "SUCCESS RATE", value: "0%", change: "0%", icon: <TrendingUp className="h-5 w-5 text-accent" />, trend: "neutral" as const }
  ]

  return (
    <div className="space-y-4">
      {error && (
        <motion.div
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          className="bg-red-500 text-white p-4 font-black text-xs border-2 border-foreground mb-4"
        >
          ERROR: {error.toUpperCase()}
          <button 
            onClick={() => window.location.reload()} 
            className="ml-4 underline hover:bg-black p-1 transition-colors"
          >
            RETRY SYNC
          </button>
        </motion.div>
      )}
      
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {(loading && !stats ? Array(4).fill(statsData[0]) : statsData).map((stat, index) => (
          <StatCard key={index} {...stat} loading={loading} index={index} />
        ))}
      </div>
    </div>
  )
}