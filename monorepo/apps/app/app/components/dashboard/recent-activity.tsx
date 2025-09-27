"use client"

import { useState, useEffect } from "react"
import { Clock, CheckCircle, XCircle, AlertTriangle, FileText, Zap, Play, Loader2 } from "lucide-react"

interface ActivityItem {
  id: string
  type: "success" | "error" | "warning" | "info"
  title: string
  description: string
  timestamp: string
  icon: React.ReactNode
}

function ActivityItemComponent({ activity }: { activity: ActivityItem }) {
  const typeConfig = {
    success: { color: "text-green-500", bg: "bg-green-500/10" },
    error: { color: "text-red-500", bg: "bg-red-500/10" },
    warning: { color: "text-yellow-500", bg: "bg-yellow-500/10" },
    info: { color: "text-blue-500", bg: "bg-blue-500/10" }
  }
  
  const config = typeConfig[activity.type]
  
  return (
    <div className="flex items-start space-x-3 p-3 hover:bg-card/30 rounded-lg transition-colors">
      <div className={`p-2 rounded-lg ${config.bg} flex-shrink-0`}>
        <div className={`${config.color}`}>
          {activity.icon}
        </div>
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-foreground mb-1">{activity.title}</p>
        <p className="text-xs text-muted-foreground mb-2">{activity.description}</p>
        <div className="flex items-center space-x-1 text-xs text-muted-foreground">
          <Clock className="h-3 w-3" />
          <span>{activity.timestamp}</span>
        </div>
      </div>
    </div>
  )
}

interface RecentActivityData {
  id: string
  role: string
  content: string
  timestamp: string
}

export function RecentActivity() {
  const [activities, setActivities] = useState<ActivityItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchRecentActivity = async () => {
      try {
        setLoading(true)
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
        
        // Transform the data into activity items
        const activityItems: ActivityItem[] = data.recentActivity.map((activity: RecentActivityData, index: number) => {
          const timeAgo = new Date(activity.timestamp)
          const now = new Date()
          const diffInMinutes = Math.floor((now.getTime() - timeAgo.getTime()) / (1000 * 60))
          
          let timeString = ''
          if (diffInMinutes < 1) timeString = 'Just now'
          else if (diffInMinutes < 60) timeString = `${diffInMinutes} minutes ago`
          else if (diffInMinutes < 1440) timeString = `${Math.floor(diffInMinutes / 60)} hours ago`
          else timeString = `${Math.floor(diffInMinutes / 1440)} days ago`

          // Determine activity type and icon based on content
          let type: "success" | "error" | "warning" | "info" = "info"
          let icon = <FileText className="h-4 w-4" />
          let title = "AI Response"
          let description = activity.content.substring(0, 50) + (activity.content.length > 50 ? '...' : '')

          if (activity.role === 'user') {
            type = "info"
            icon = <FileText className="h-4 w-4" />
            title = "User Request"
            description = activity.content.substring(0, 50) + (activity.content.length > 50 ? '...' : '')
          } else if (activity.role === 'assistant') {
            if (activity.content.toLowerCase().includes('error') || activity.content.toLowerCase().includes('failed')) {
              type = "error"
              icon = <XCircle className="h-4 w-4" />
              title = "AI Error"
            } else if (activity.content.toLowerCase().includes('warning') || activity.content.toLowerCase().includes('caution')) {
              type = "warning"
              icon = <AlertTriangle className="h-4 w-4" />
              title = "AI Warning"
            } else if (activity.content.toLowerCase().includes('success') || activity.content.toLowerCase().includes('complete')) {
              type = "success"
              icon = <CheckCircle className="h-4 w-4" />
              title = "AI Success"
            } else {
              type = "success"
              icon = <Zap className="h-4 w-4" />
              title = "AI Response"
            }
            description = activity.content.substring(0, 50) + (activity.content.length > 50 ? '...' : '')
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

        setActivities(activityItems.slice(0, 6)) // Show only last 6 activities
      } catch (err) {
        console.error('Error fetching recent activity:', err)
        setError(err instanceof Error ? err.message : 'Failed to load recent activity')
      } finally {
        setLoading(false)
      }
    }

    fetchRecentActivity()
  }, [])

  return (
    <div className="bg-card/50 backdrop-blur-sm rounded-xl border border-border p-6">
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-foreground mb-1">Recent Activity</h2>
        <p className="text-muted-foreground">Your latest AI development activity</p>
      </div>
      
      {error && (
        <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4 mb-4">
          <p className="text-red-400 text-sm mb-2">Failed to load recent activity: {error}</p>
          <button 
            onClick={() => window.location.reload()} 
            className="text-sm text-red-400 hover:text-red-300 underline"
          >
            Retry
          </button>
        </div>
      )}

      {loading ? (
        <div className="flex items-center justify-center py-8">
          <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
        </div>
      ) : (
        <div className="space-y-1 max-h-80 overflow-y-auto custom-scrollbar">
          {activities.length > 0 ? (
            activities.map((activity) => (
              <ActivityItemComponent key={activity.id} activity={activity} />
            ))
          ) : (
            <div className="text-center py-8">
              <p className="text-muted-foreground">No recent activity</p>
            </div>
          )}
        </div>
      )}
      
      <div className="mt-4 pt-4 border-t border-border">
        <button className="text-sm text-primary hover:text-primary/80 transition-colors">
          View All Activity →
        </button>
      </div>
    </div>
  )
}
