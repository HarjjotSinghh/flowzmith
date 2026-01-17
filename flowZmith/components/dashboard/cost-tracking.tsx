"use client"

import { useState, useEffect } from "react"
import { DollarSign, CreditCard, TrendingUp, AlertCircle, Loader2, Zap } from "lucide-react"
import { Button } from "@/components/ui/button"

interface CostItemProps {
  service: string
  amount: string
  usage: string
  percentage: number
  loading?: boolean
}

function CostItem({ service, amount, usage, percentage, loading }: CostItemProps) {
  return (
    <div className="flex items-center justify-between p-4 bg-background border-2 border-foreground group hover:bg-accent transition-colors duration-200">
      <div className="flex-1">
        <p className="font-black text-xs uppercase tracking-tighter group-hover:text-black">{service}</p>
        <p className="text-[10px] font-bold text-foreground/60 uppercase group-hover:text-black/80">{loading ? "SYNCING..." : usage}</p>
      </div>
      <div className="text-right">
        <p className="text-lg font-black tracking-tighter group-hover:text-black">{loading ? "..." : amount}</p>
        <div className="flex items-center gap-2 mt-1">
          <div className="w-20 h-1.5 bg-foreground/20 group-hover:bg-black/20 overflow-hidden">
            <div 
              className="h-full bg-foreground group-hover:bg-black transition-all duration-300"
              style={{ width: `${Math.min(percentage, 100)}%` }}
            />
          </div>
          <span className="text-[10px] font-black group-hover:text-black">{loading ? "..." : `${percentage}%`}</span>
        </div>
      </div>
    </div>
  )
}

interface CostData {
  totalCost: string
  projectedMonthlyCost: string
  remainingCredits: number
  costBreakdown: {
    apiCalls: { count: number; cost: number; percentage: number }
    storage: { count: number; cost: number; percentage: number }
    processing: { count: number; cost: number; percentage: number }
  }
  costTrend: "up" | "down" | "neutral"
  savings: {
    thisMonth: string
    comparedToLastMonth: "up" | "down"
  }
}

export function CostTracking() {
  const [costData, setCostData] = useState<CostData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchCostData = async () => {
      try {
        setLoading(true)
        const response = await fetch('/api/dashboard/costs')
        
        if (!response.ok) {
          if (response.status === 401) {
            throw new Error('Please log in to view cost data')
          } else if (response.status === 404) {
            throw new Error('User not found. Please try logging in again')
          } else {
            throw new Error(`Failed to fetch cost data (${response.status})`)
          }
        }
        
        const data = await response.json()
        setCostData(data)
      } catch (err) {
        console.error('Error fetching cost data:', err)
        setError(err instanceof Error ? err.message : 'Failed to load cost data')
      } finally {
        setLoading(false)
      }
    }

    fetchCostData()
  }, [])

  const costItems = costData ? [
    {
      service: "API CALLS",
      amount: `$${costData.costBreakdown.apiCalls.cost.toFixed(4)}`,
      usage: `${costData.costBreakdown.apiCalls.count} CALLS`,
      percentage: costData.costBreakdown.apiCalls.percentage
    },
    {
      service: "AKAVE STORAGE",
      amount: `$${costData.costBreakdown.storage.cost.toFixed(4)}`,
      usage: `${costData.costBreakdown.storage.count} MB`,
      percentage: costData.costBreakdown.storage.percentage
    },
    {
      service: "CORE PROCESSING",
      amount: `$${costData.costBreakdown.processing.cost.toFixed(4)}`,
      usage: `${costData.costBreakdown.processing.count} UNITS`,
      percentage: costData.costBreakdown.processing.percentage
    }
  ] : []

  const budgetUsage = costData ? 
    Math.round((parseFloat(costData.totalCost) / 200) * 100) : 0

  return (
    <div className="space-y-6">
      {error && (
        <div className="bg-red-500 text-white p-4 font-black text-[10px] uppercase border-2 border-foreground">
          SYNC ERROR: {error.toUpperCase()}
        </div>
      )}

      {/* Budget Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-accent text-black p-4 border-2 border-foreground">
          <div className="flex items-center gap-2 mb-2">
            <DollarSign className="h-4 w-4" />
            <span className="text-[10px] font-black uppercase tracking-widest">TOTAL SPENT</span>
          </div>
          <p className="text-2xl font-black tracking-tighter">
            {loading ? <Loader2 className="h-6 w-6 animate-spin" /> : `$${costData?.totalCost || "0.0000"}`}
          </p>
        </div>
        
        <div className="bg-black text-white p-4 border-2 border-foreground">
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp className="h-4 w-4 text-accent" />
            <span className="text-[10px] font-black uppercase tracking-widest">PROJECTED</span>
          </div>
          <p className="text-2xl font-black tracking-tighter">
            {loading ? <Loader2 className="h-6 w-6 animate-spin" /> : `$${costData?.projectedMonthlyCost || "0.0000"}`}
          </p>
        </div>
        
        <div className="bg-background text-foreground p-4 border-2 border-foreground">
          <div className="flex items-center gap-2 mb-2">
            <Zap className="h-4 w-4 text-accent" />
            <span className="text-[10px] font-black uppercase tracking-widest">REMAINING</span>
          </div>
          <p className="text-2xl font-black tracking-tighter">
            {loading ? <Loader2 className="h-6 w-6 animate-spin" /> : costData?.remainingCredits || 0}
          </p>
        </div>
      </div>

      {/* Cost Breakdown */}
      <div className="space-y-2">
        <div className="text-[10px] font-black uppercase tracking-widest opacity-50 mb-2">BREAKDOWN // SERVICES</div>
        {costItems.map((item, index) => (
          <CostItem key={index} {...item} loading={loading} />
        ))}
      </div>

      {/* Budget Progress Bar */}
      <div className="pt-4 border-t-2 border-foreground/10">
        <div className="flex items-center justify-between mb-2">
          <span className="text-[10px] font-black uppercase tracking-widest">QUOTA UTILIZATION</span>
          <span className="text-[10px] font-black">
            {loading ? "ANALYZING..." : `${budgetUsage}% USED`}
          </span>
        </div>
        <div className="w-full h-4 bg-muted/20 border-2 border-foreground overflow-hidden">
          <div 
            className="h-full bg-accent transition-all duration-500" 
            style={{ width: `${budgetUsage}%` }} 
          />
        </div>
      </div>

      <Button variant="terminal" className="w-full h-12 text-xs font-black">
        MANAGE BILLING & SUBSCRIPTION
      </Button>
    </div>
  )
}