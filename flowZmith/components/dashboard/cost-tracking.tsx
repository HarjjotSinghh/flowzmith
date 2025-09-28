"use client"

import { useState, useEffect } from "react"
import { DollarSign, CreditCard, TrendingUp, AlertCircle, Loader2 } from "lucide-react"
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
    <div className="flex items-center justify-between p-4 bg-card/30 rounded-lg border border-border/50">
      <div className="flex-1">
        <p className="font-medium text-foreground">{service}</p>
        <p className="text-sm text-muted-foreground">{loading ? "Loading..." : usage}</p>
      </div>
      <div className="text-right">
        <p className="font-semibold text-foreground">{loading ? "..." : amount}</p>
        <div className="flex items-center space-x-2 mt-1">
          <div className="w-16 h-2 bg-muted rounded-full overflow-hidden">
            <div 
              className="h-full bg-primary transition-all duration-300"
              style={{ width: `${Math.min(percentage, 100)}%` }}
            />
          </div>
          <span className="text-xs text-muted-foreground">{loading ? "..." : `${percentage}%`}</span>
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
      service: "API Calls",
      amount: `$${costData.costBreakdown.apiCalls.cost.toFixed(4)}`,
      usage: `${costData.costBreakdown.apiCalls.count} calls`,
      percentage: costData.costBreakdown.apiCalls.percentage
    },
    {
      service: "Storage",
      amount: `$${costData.costBreakdown.storage.cost.toFixed(4)}`,
      usage: `${costData.costBreakdown.storage.count} MB`,
      percentage: costData.costBreakdown.storage.percentage
    },
    {
      service: "Processing",
      amount: `$${costData.costBreakdown.processing.cost.toFixed(4)}`,
      usage: `${costData.costBreakdown.processing.count} units`,
      percentage: costData.costBreakdown.processing.percentage
    }
  ] : []

  const budgetUsage = costData ? 
    Math.round((parseFloat(costData.totalCost) / 200) * 100) : 0

  return (
    <div className="bg-card/50 backdrop-blur-sm rounded-xl border border-border p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-semibold text-foreground mb-1">Cost Tracking</h2>
          <p className="text-muted-foreground">Current month spending breakdown</p>
        </div>
        <Button variant="outline" size="sm" className="flex items-center space-x-2">
          <CreditCard className="h-4 w-4" />
          <span>Manage Billing</span>
        </Button>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4 mb-6">
          <p className="text-red-400 text-sm mb-2">Failed to load cost data: {error}</p>
          <button 
            onClick={() => window.location.reload()} 
            className="text-sm text-red-400 hover:text-red-300 underline"
          >
            Retry
          </button>
        </div>
      )}

      {/* Budget Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-primary/10 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <DollarSign className="h-4 w-4 text-primary" />
            <span className="text-sm font-medium text-foreground">Total Spent</span>
          </div>
          <p className="text-2xl font-bold text-foreground">
            {loading ? <Loader2 className="h-6 w-6 animate-spin" /> : `$${costData?.totalCost || "0.0000"}`}
          </p>
        </div>
        
        <div className="bg-muted/50 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
            <span className="text-sm font-medium text-foreground">Projected Monthly</span>
          </div>
          <p className="text-2xl font-bold text-foreground">
            {loading ? <Loader2 className="h-6 w-6 animate-spin" /> : `$${costData?.projectedMonthlyCost || "0.0000"}`}
          </p>
        </div>
        
        <div className="bg-green-500/10 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <AlertCircle className="h-4 w-4 text-green-500" />
            <span className="text-sm font-medium text-foreground">Remaining Credits</span>
          </div>
          <p className="text-2xl font-bold text-foreground">
            {loading ? <Loader2 className="h-6 w-6 animate-spin" /> : costData?.remainingCredits || 0}
          </p>
        </div>
      </div>

      {/* Cost Breakdown */}
      <div className="space-y-3">
        <h3 className="font-medium text-foreground mb-3">Cost Breakdown</h3>
        {costItems.map((item, index) => (
          <CostItem key={index} {...item} loading={loading} />
        ))}
      </div>

      {/* Budget Progress Bar */}
      <div className="mt-6">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-foreground">Budget Usage</span>
          <span className="text-sm text-muted-foreground">
            {loading ? "..." : `${budgetUsage}% used`}
          </span>
        </div>
        <div className="w-full h-3 bg-muted rounded-full overflow-hidden">
          <div 
            className="h-full bg-gradient-to-r from-primary to-primary-dark transition-all duration-500" 
            style={{ width: `${budgetUsage}%` }} 
          />
        </div>
      </div>
    </div>
  )
}
