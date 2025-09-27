"use client"

import { useState } from "react"
import { Activity, TrendingUp, Clock, CheckCircle, XCircle, AlertTriangle } from "lucide-react"
import { Button } from "@/components/ui/button"

interface TimelineData {
  time: string
  requests: number
  success: number
  errors: number
}

interface RequestItem {
  id: string
  timestamp: string
  endpoint: string
  status: "success" | "error" | "warning"
  duration: string
  tokens: number
}

function LineChart({ data }: { data: TimelineData[] }) {
  const maxRequests = Math.max(...data.map(d => d.requests))
  
  return (
    <div className="relative h-48 w-full">
      <svg className="w-full h-full" viewBox="0 0 400 120">
        {/* Grid lines */}
        {[0, 1, 2, 3, 4].map(i => (
          <line
            key={i}
            x1="0"
            y1={24 + i * 20}
            x2="400"
            y2={24 + i * 20}
            stroke="hsl(var(--border))"
            strokeWidth="1"
            opacity="0.3"
          />
        ))}
        
        {/* Success line */}
        <polyline
          fill="none"
          stroke="hsl(var(--primary))"
          strokeWidth="2"
          points={data.map((d, i) => 
            `${(i / (data.length - 1)) * 380 + 10},${120 - (d.success / maxRequests) * 80 - 20}`
          ).join(" ")}
        />
        
        {/* Error line */}
        <polyline
          fill="none"
          stroke="hsl(var(--destructive))"
          strokeWidth="2"
          points={data.map((d, i) => 
            `${(i / (data.length - 1)) * 380 + 10},${120 - (d.errors / maxRequests) * 80 - 20}`
          ).join(" ")}
        />
        
        {/* Data points */}
        {data.map((d, i) => (
          <g key={i}>
            <circle
              cx={(i / (data.length - 1)) * 380 + 10}
              cy={120 - (d.requests / maxRequests) * 80 - 20}
              r="3"
              fill="hsl(var(--primary))"
            />
          </g>
        ))}
      </svg>
    </div>
  )
}

function RequestItemComponent({ request }: { request: RequestItem }) {
  const statusConfig = {
    success: { icon: CheckCircle, color: "text-green-500", bg: "bg-green-500/10" },
    error: { icon: XCircle, color: "text-red-500", bg: "bg-red-500/10" },
    warning: { icon: AlertTriangle, color: "text-yellow-500", bg: "bg-yellow-500/10" }
  }
  
  const config = statusConfig[request.status]
  const Icon = config.icon
  
  return (
    <div className="flex items-center space-x-4 p-3 bg-card/30 rounded-lg border border-border/50">
      <div className={`p-2 rounded-lg ${config.bg}`}>
        <Icon className={`h-4 w-4 ${config.color}`} />
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-foreground truncate">{request.endpoint}</p>
        <p className="text-xs text-muted-foreground">{request.timestamp}</p>
      </div>
      <div className="text-right">
        <p className="text-sm font-medium text-foreground">{request.duration}</p>
        <p className="text-xs text-muted-foreground">{request.tokens} tokens</p>
      </div>
    </div>
  )
}

export function RequestTimeline() {
  const [timeRange, setTimeRange] = useState("24h")
  
  const timelineData: TimelineData[] = [
    { time: "00:00", requests: 45, success: 42, errors: 3 },
    { time: "04:00", requests: 32, success: 30, errors: 2 },
    { time: "08:00", requests: 78, success: 75, errors: 3 },
    { time: "12:00", requests: 95, success: 92, errors: 3 },
    { time: "16:00", requests: 120, success: 115, errors: 5 },
    { time: "20:00", requests: 88, success: 85, errors: 3 },
    { time: "24:00", requests: 65, success: 62, errors: 3 }
  ]
  
  const recentRequests: RequestItem[] = [
    {
      id: "1",
      timestamp: "2 minutes ago",
      endpoint: "/api/contracts/generate",
      status: "success",
      duration: "1.2s",
      tokens: 1250
    },
    {
      id: "2", 
      timestamp: "5 minutes ago",
      endpoint: "/api/contracts/optimize",
      status: "success",
      duration: "0.8s",
      tokens: 890
    },
    {
      id: "3",
      timestamp: "8 minutes ago", 
      endpoint: "/api/contracts/deploy",
      status: "warning",
      duration: "3.1s",
      tokens: 2100
    },
    {
      id: "4",
      timestamp: "12 minutes ago",
      endpoint: "/api/contracts/validate",
      status: "error",
      duration: "0.3s",
      tokens: 0
    },
    {
      id: "5",
      timestamp: "15 minutes ago",
      endpoint: "/api/contracts/generate",
      status: "success", 
      duration: "1.5s",
      tokens: 1580
    }
  ]

  return (
    <div className="bg-card/50 backdrop-blur-sm rounded-xl border border-border p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-semibold text-foreground mb-1">Request Timeline</h2>
          <p className="text-muted-foreground">API usage patterns and performance</p>
        </div>
        <div className="flex space-x-2">
          {["1h", "24h", "7d", "30d"].map((range) => (
            <Button
              key={range}
              variant={timeRange === range ? "default" : "outline"}
              size="sm"
              onClick={() => setTimeRange(range)}
            >
              {range}
            </Button>
          ))}
        </div>
      </div>

      {/* Chart */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-primary rounded-full"></div>
              <span className="text-sm text-foreground">Success</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-destructive rounded-full"></div>
              <span className="text-sm text-foreground">Errors</span>
            </div>
          </div>
          <div className="flex items-center space-x-2 text-sm text-muted-foreground">
            <Activity className="h-4 w-4" />
            <span>Total: {timelineData.reduce((sum, d) => sum + d.requests, 0)} requests</span>
          </div>
        </div>
        <LineChart data={timelineData} />
      </div>

      {/* Recent Requests */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-medium text-foreground">Recent Requests</h3>
          <Button variant="ghost" size="sm" className="text-primary">
            View All
          </Button>
        </div>
        <div className="space-y-2 max-h-64 overflow-y-auto">
          {recentRequests.map((request) => (
            <RequestItemComponent key={request.id} request={request} />
          ))}
        </div>
      </div>
    </div>
  )
}
