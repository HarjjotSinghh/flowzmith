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
    success: { color: "text-accent", bg: "bg-black" },
    error: { color: "text-red-500", bg: "bg-black" },
    warning: { color: "text-foreground", bg: "bg-black" },
    info: { color: "text-foreground", bg: "bg-black" }
  }
  
  const config = typeConfig[activity.type]
  
  return (
    <div className="flex items-start space-x-4 p-4 hover:bg-accent hover:text-black group border-2 border-transparent hover:border-foreground transition-all duration-200 cursor-default">
      <div className={`p-2 border-2 border-foreground ${config.bg} flex-shrink-0 group-hover:bg-black group-hover:border-black transition-colors`}>
        <div className={`${config.color} group-hover:text-accent`}>
          {activity.icon}
        </div>
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-xs font-black uppercase tracking-tighter mb-1">{activity.title}</p>
        <p className="text-[10px] font-bold opacity-80 uppercase leading-snug mb-2 line-clamp-2">{activity.description}</p>
        <div className="flex items-center space-x-1 text-[9px] font-black opacity-50 uppercase tracking-widest group-hover:opacity-100">
          <Clock className="h-3 w-3" />
          <span>{activity.timestamp}</span>
        </div>
      </div>
      <div className="w-2 h-2 bg-foreground group-hover:bg-black group-hover:animate-ping self-center" />
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
        
        const activityItems: ActivityItem[] = data.recentActivity.map((activity: RecentActivityData, index: number) => {
          const timeAgo = new Date(activity.timestamp)
          const now = new Date()
          const diffInMinutes = Math.floor((now.getTime() - timeAgo.getTime()) / (1000 * 60))
          
          let timeString = ''
          if (diffInMinutes < 1) timeString = 'JUST NOW'
          else if (diffInMinutes < 60) timeString = `${diffInMinutes} MINS AGO`
          else if (diffInMinutes < 1440) timeString = `${Math.floor(diffInMinutes / 60)} HOURS AGO`
          else timeString = `${Math.floor(diffInMinutes / 1440)} DAYS AGO`

          let type: "success" | "error" | "warning" | "info" = "info"
          let icon = <FileText className="h-4 w-4" />
          let title = "AI RESPONSE"
          let description = activity.content

          if (activity.role === 'user') {
            type = "info"
            icon = <FileText className="h-4 w-4" />
            title = "USER REQUEST"
          } else if (activity.role === 'assistant') {
            if (activity.content.toLowerCase().includes('error') || activity.content.toLowerCase().includes('failed')) {
              type = "error"
              icon = <XCircle className="h-4 w-4" />
              title = "AI ERROR"
            } else if (activity.content.toLowerCase().includes('warning') || activity.content.toLowerCase().includes('caution')) {
              type = "warning"
              icon = <AlertTriangle className="h-4 w-4" />
              title = "AI WARNING"
            } else if (activity.content.toLowerCase().includes('success') || activity.content.toLowerCase().includes('complete')) {
              type = "success"
              icon = <CheckCircle className="h-4 w-4" />
              title = "AI SUCCESS"
            } else {
              type = "success"
              icon = <Zap className="h-4 w-4" />
              title = "AI RESPONSE"
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

        setActivities(activityItems.slice(0, 10)) 
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
    <div className="space-y-1">
      {error && (
        <div className="bg-red-500 text-white p-4 font-black text-[10px] uppercase border-2 border-foreground mb-4">
          CRITICAL ERROR: {error.toUpperCase()}
          <button 
            onClick={() => window.location.reload()} 
            className="ml-4 underline hover:bg-black p-1 transition-colors"
          >
            RETRY SYNC
          </button>
        </div>
      )}

      {loading ? (
        <div className="flex flex-col items-center justify-center py-12 gap-4">
          <Loader2 className="h-8 w-8 animate-spin text-accent" />
          <div className="text-[10px] font-black uppercase tracking-[0.3em] animate-pulse">READING ACTIVITY LOG...</div>
        </div>
      ) : (
        <div className="divide-y-2 divide-foreground/10">
          {activities.length > 0 ? (
            activities.map((activity) => (
              <ActivityItemComponent key={activity.id} activity={activity} />
            ))
          ) : (
            <div className="text-center py-12">
              <p className="text-[10px] font-black uppercase opacity-50 tracking-widest italic">NO ACTIVITY LOGGED IN CURRENT SESSION</p>
            </div>
          )}
        </div>
      )}
      
      {activities.length > 0 && (
        <div className="mt-6 pt-6 border-t-2 border-foreground/10">
          <button className="w-full py-3 bg-black text-white text-[10px] font-black uppercase tracking-[0.2em] border-2 border-foreground hover:bg-accent hover:text-black transition-colors">
            VIEW FULL SYSTEM LOG →
          </button>
        </div>
      )}
    </div>
  )
}