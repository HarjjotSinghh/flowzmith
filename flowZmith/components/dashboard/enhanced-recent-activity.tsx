"use client"

import { useState, useEffect, useRef } from "react"
import { Clock, CheckCircle, XCircle, AlertTriangle, FileText, Zap, Play, Loader2, MessageSquare, Code, Sparkles, Activity } from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"

interface ActivityItem {
  id: string
  type: "success" | "error" | "warning" | "info" | "streaming"
  title: string
  description: string
  timestamp: string
  icon: React.ReactNode
  isNew?: boolean
  progress?: number
}

interface RecentActivityData {
  id: string
  role: string
  content: string
  timestamp: string
}

function AnimatedActivityItem({ activity, index }: { activity: ActivityItem; index: number }) {
  const typeConfig = {
    success: { 
      color: "text-primary", 
      bg: "bg-primary/10", 
      border: "border-primary/20"
    },
    error: { 
      color: "text-destructive", 
      bg: "bg-destructive/10", 
      border: "border-destructive/20"
    },
    warning: { 
      color: "text-muted-foreground", 
      bg: "bg-muted/50", 
      border: "border-border"
    },
    info: { 
      color: "text-muted-foreground", 
      bg: "bg-muted/50", 
      border: "border-border"
    },
    streaming: { 
      color: "text-primary", 
      bg: "bg-primary/10", 
      border: "border-primary/20"
    }
  }
  
  const config = typeConfig[activity.type]
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: -20, scale: 0.95 }}
      transition={{ 
        duration: 0.3, 
        delay: index * 0.05,
        type: "spring",
        stiffness: 300,
        damping: 30
      }}
      className={`group relative flex items-start space-x-4 p-4 rounded-2xl border transition-all duration-300 hover:shadow-lg ${
        activity.isNew 
          ? `bg-primary/5 border-primary/30` 
          : `bg-card/70 border-border/70 hover:border-border`
      }`}
    >
      {/* New indicator */}
      {activity.isNew && (
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          className="absolute -top-1 -right-1 w-3 h-3 bg-primary rounded-full shadow-lg"
        >
          <div className="absolute inset-0 bg-primary rounded-full animate-ping opacity-75" />
        </motion.div>
      )}

      {/* Icon container */}
      <motion.div 
        className={`relative p-3 rounded-xl ${config.bg} border ${config.border} flex-shrink-0 group-hover:scale-110 transition-transform duration-200`}
        whileHover={{ rotate: 5 }}
      >
        <div className={`${config.color}`}>
          {activity.icon}
        </div>
        
        {/* Streaming progress indicator */}
        {activity.type === "streaming" && activity.progress !== undefined && (
          <motion.div
            className="absolute inset-0 rounded-xl border-2 border-primary/30"
            style={{
              background: `conic-gradient(from 0deg, transparent ${360 - (activity.progress * 3.6)}deg, rgba(168, 85, 247, 0.3) ${360 - (activity.progress * 3.6)}deg)`
            }}
          />
        )}
      </motion.div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between mb-2">
          <motion.h3 
            className="text-sm font-semibold text-foreground group-hover:text-primary transition-colors"
            layoutId={`title-${activity.id}`}
          >
            {activity.title}
          </motion.h3>
          
          {activity.type === "streaming" && (
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
              className="flex-shrink-0"
            >
              <Loader2 className="h-3 w-3 text-primary" />
            </motion.div>
          )}
        </div>
        
        <motion.p 
          className="text-xs text-muted-foreground mb-3 leading-relaxed"
          layoutId={`description-${activity.id}`}
        >
          {activity.description}
        </motion.p>
        
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2 text-xs text-muted-foreground">
            <Clock className="h-3 w-3" />
            <span>{activity.timestamp}</span>
          </div>
          
          {activity.progress !== undefined && activity.type === "streaming" && (
            <div className="flex items-center space-x-2">
              <div className="w-16 h-1 bg-muted rounded-full overflow-hidden">
                <motion.div
                  className="h-full bg-primary"
                  initial={{ width: 0 }}
                  animate={{ width: `${activity.progress}%` }}
                  transition={{ duration: 0.3 }}
                />
              </div>
              <span className="text-xs text-primary font-medium">{Math.round(activity.progress)}%</span>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  )
}

export function EnhancedRecentActivity() {
  const [activities, setActivities] = useState<ActivityItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [streamingActivities, setStreamingActivities] = useState<Map<string, ActivityItem>>(new Map())
  const wsRef = useRef<WebSocket | null>(null)
  const retryTimeoutRef = useRef<NodeJS.Timeout>(null)

  // Simulate streaming activity updates
  const simulateStreamingActivity = (id: string, title: string, description: string) => {
    const streamingActivity: ActivityItem = {
      id,
      type: "streaming",
      title,
      description,
      timestamp: "Now",
      icon: <Sparkles className="h-4 w-4" />,
      isNew: true,
      progress: 0
    }

    setStreamingActivities(prev => new Map(prev.set(id, streamingActivity)))

    // Simulate progress updates
    let progress = 0
    const progressInterval = setInterval(() => {
      progress += Math.random() * 15 + 5
      if (progress >= 100) {
        progress = 100
        clearInterval(progressInterval)
        
        // Convert to success activity
        setTimeout(() => {
          const completedActivity: ActivityItem = {
            id,
            type: "success",
            title: title.replace("Generating", "Generated"),
            description: description.replace("in progress", "completed successfully"),
            timestamp: "Just now",
            icon: <CheckCircle className="h-4 w-4" />,
            isNew: true
          }
          
          setStreamingActivities(prev => {
            const newMap = new Map(prev)
            newMap.delete(id)
            return newMap
          })
          
          setActivities(prev => [completedActivity, ...prev.slice(0, 5)])
        }, 1000)
      } else {
        setStreamingActivities(prev => {
          const newMap = new Map(prev)
          const activity = newMap.get(id)
          if (activity) {
            newMap.set(id, { ...activity, progress })
          }
          return newMap
        })
      }
    }, 200)
  }

  const fetchRecentActivity = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const response = await fetch('/api/dashboard/stats')
      
      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Please log in to view recent activity')
        } else if (response.status === 404) {
          throw new Error('User not found. Please try logging in again')
        } else {
          throw new Error(`Failed to fetch recent activity (${response.status})`)
        }
      }
      
      const data = await response.json()
      
      // Check if recentActivity exists in the response
      if (!data.recentActivity) {
        console.warn('No recentActivity data in response:', data)
        setActivities([])
        return
      }
      
      // Transform the data into activity items
      const activityItems: ActivityItem[] = data.recentActivity.map((activity: RecentActivityData) => {
        const timeAgo = new Date(activity.timestamp)
        const now = new Date()
        const diffInMinutes = Math.floor((now.getTime() - timeAgo.getTime()) / (1000 * 60))
        
        let timeString = ''
        if (diffInMinutes < 1) timeString = 'Just now'
        else if (diffInMinutes < 60) timeString = `${diffInMinutes}m ago`
        else if (diffInMinutes < 1440) timeString = `${Math.floor(diffInMinutes / 60)}h ago`
        else timeString = `${Math.floor(diffInMinutes / 1440)}d ago`

        // Determine activity type and icon based on content
        let type: ActivityItem["type"] = "info"
        let icon = <MessageSquare className="h-4 w-4" />
        let title = "AI Response"
        let description = activity.content.substring(0, 60) + (activity.content.length > 60 ? '...' : '')

        if (activity.role === 'user') {
          type = "info"
          icon = <MessageSquare className="h-4 w-4" />
          title = "User Request"
        } else if (activity.role === 'assistant') {
          if (activity.content.toLowerCase().includes('error') || activity.content.toLowerCase().includes('failed')) {
            type = "error"
            icon = <XCircle className="h-4 w-4" />
            title = "AI Error"
          } else if (activity.content.toLowerCase().includes('warning') || activity.content.toLowerCase().includes('caution')) {
            type = "warning"
            icon = <AlertTriangle className="h-4 w-4" />
            title = "AI Warning"
          } else if (activity.content.toLowerCase().includes('contract') || activity.content.toLowerCase().includes('solidity')) {
            type = "success"
            icon = <Code className="h-4 w-4" />
            title = "Contract Generated"
          } else {
            type = "success"
            icon = <Zap className="h-4 w-4" />
            title = "AI Response"
          }
        }

        return {
          id: activity.id,
          type,
          title,
          description,
          timestamp: timeString,
          icon
        }
      })

      setActivities(activityItems.slice(0, 6))
    } catch (err) {
      console.error('Error fetching recent activity:', err)
      setError(err instanceof Error ? err.message : 'Failed to load recent activity')
      
      // Retry after 5 seconds on error
      retryTimeoutRef.current = setTimeout(() => {
        fetchRecentActivity()
      }, 5000)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchRecentActivity()

    // Set up periodic refresh
    const refreshInterval = setInterval(fetchRecentActivity, 30000) // Refresh every 30 seconds

    return () => {
      clearInterval(refreshInterval)
      if (retryTimeoutRef.current) {
        clearTimeout(retryTimeoutRef.current)
      }
    }
  }, [])

  // Demo: Simulate streaming activities periodically
  useEffect(() => {
    const demoInterval = setInterval(() => {
      if (Math.random() > 0.7) { // 30% chance every 10 seconds
        const activities = [
          { title: "Generating Smart Contract", description: "ERC-20 token contract in progress..." },
          { title: "Generating DeFi Protocol", description: "Liquidity pool contract in progress..." },
          { title: "Generating NFT Contract", description: "ERC-721 collection contract in progress..." },
          { title: "Generating DAO Contract", description: "Governance contract in progress..." }
        ]
        
        const randomActivity = activities[Math.floor(Math.random() * activities.length)]
        simulateStreamingActivity(
          `streaming-${Date.now()}`,
          randomActivity.title,
          randomActivity.description
        )
      }
    }, 10000)

    return () => clearInterval(demoInterval)
  }, [])

  const allActivities = [
    ...Array.from(streamingActivities.values()),
    ...activities
  ].slice(0, 8)

  const retryFetch = () => {
    setError(null)
    setLoading(true)
    retryTimeoutRef.current = setTimeout(() => {
      fetchRecentActivity()
    }, 100)
  }

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="bg-gradient-to-br from-card/50 to-card/30 backdrop-blur-sm rounded-2xl border border-border/50 p-6 shadow-xl"
    >
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center space-x-3">
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
              className="p-2 bg-primary/10 rounded-lg"
            >
              <Activity className="h-5 w-5 text-primary" />
            </motion.div>
            <div>
              <h2 className="text-xl font-bold bg-gradient-to-r from-foreground to-foreground/70 bg-clip-text text-transparent">
                Recent Activity
              </h2>
              <p className="text-sm text-muted-foreground">Real-time development updates</p>
            </div>
          </div>
          
          {streamingActivities.size > 0 && (
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              className="flex items-center space-x-2 px-3 py-1 bg-primary/10 border border-primary/20 rounded-full"
            >
              <div className="w-2 h-2 bg-primary rounded-full animate-pulse" />
              <span className="text-xs text-primary font-medium">Live</span>
            </motion.div>
          )}
        </div>
      </div>
      
      <AnimatePresence mode="popLayout">
        {error && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="bg-destructive/10 border border-destructive/20 rounded-xl p-4 mb-6"
          >
            <p className="text-destructive text-sm mb-3">Failed to load recent activity: {error}</p>
            <button 
              onClick={retryFetch}
              className="text-sm text-destructive hover:text-destructive/80 underline transition-colors"
            >
              Retry
            </button>
          </motion.div>
        )}

        {loading ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="flex items-center justify-center py-12"
          >
            <div className="flex items-center space-x-3">
              <Loader2 className="h-6 w-6 animate-spin text-primary" />
              <span className="text-muted-foreground">Loading activity...</span>
            </div>
          </motion.div>
        ) : (
          <div className="space-y-3 max-h-96 overflow-y-auto custom-scrollbar">
            {allActivities.length > 0 ? (
              allActivities.map((activity, index) => (
                <AnimatedActivityItem key={activity.id} activity={activity} index={index} />
              ))
            ) : (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="text-center py-12"
              >
                <div className="mb-4">
                  <div className="w-16 h-16 bg-muted/50 rounded-full flex items-center justify-center mx-auto mb-3">
                    <Activity className="h-8 w-8 text-muted-foreground" />
                  </div>
                  <p className="text-muted-foreground">No recent activity</p>
                  <p className="text-xs text-muted-foreground/70 mt-1">Start a conversation to see activity here</p>
                </div>
              </motion.div>
            )}
          </div>
        )}
      </AnimatePresence>
      
      <motion.div 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
        className="mt-6 pt-4 border-t border-border/50"
      >
        <button className="group flex items-center space-x-2 text-sm text-primary hover:text-primary/80 transition-all duration-200">
          <span>View All Activity</span>
          <motion.div
            className="transform group-hover:translate-x-1 transition-transform"
            whileHover={{ x: 4 }}
          >
            →
          </motion.div>
        </button>
      </motion.div>
    </motion.div>
  )
}
