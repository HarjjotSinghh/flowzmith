"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { 
  Coins, 
  Zap, 
  Crown, 
  AlertCircle, 
  CheckCircle,
  RefreshCw,
  Plus,
  MessageSquare
} from "lucide-react"
import Link from "next/link"

interface CreditsData {
  used: number
  limit: number
  remaining: number
  isNewUser: boolean
  plan: string
  planName: string
  features: string[]
  canMakeRequest: boolean
}

interface CreditsDisplayProps {
  user?: {
    email: string
    name?: string
  }
}

export function CreditsDisplay({ user }: CreditsDisplayProps) {
  const [credits, setCredits] = useState<CreditsData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchCredits = async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/user/credits')
      const data = await response.json()
      
      if (data.success) {
        setCredits(data.credits)
        setError(null)
      } else {
        setError(data.error || 'Failed to load credits')
      }
    } catch (err) {
      setError('Failed to load credits')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchCredits()
  }, [])

  const getPlanColor = (plan: string) => {
    switch (plan) {
      case 'free': return 'bg-gray-100 text-gray-800'
      case 'pro': return 'bg-blue-100 text-blue-800'
      case 'enterprise': return 'bg-purple-100 text-purple-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getPlanIcon = (plan: string) => {
    switch (plan) {
      case 'free': return <Coins className="h-4 w-4" />
      case 'pro': return <Zap className="h-4 w-4" />
      case 'enterprise': return <Crown className="h-4 w-4" />
      default: return <Coins className="h-4 w-4" />
    }
  }

  if (loading) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-center">
            <RefreshCw className="h-6 w-6 animate-spin text-muted-foreground" />
            <span className="ml-2 text-muted-foreground">Loading credits...</span>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (error) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center text-red-500">
            <AlertCircle className="h-5 w-5 mr-2" />
            <span>{error}</span>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (!credits) return null

  const usagePercentage = (credits.used / credits.limit) * 100
  const isLowCredits = credits.remaining <= 2
  const isOutOfCredits = credits.remaining === 0

  return (
    <Card className="hover:shadow-lg transition-all duration-200">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Coins className="h-5 w-5 text-primary" />
            Credits
          </CardTitle>
          <div className="flex items-center gap-2">
            <Badge className={`${getPlanColor(credits.plan)} flex items-center gap-1`}>
              {getPlanIcon(credits.plan)}
              {credits.planName}
            </Badge>
            {credits.isNewUser && (
              <Badge className="bg-green-100 text-green-800">
                <CheckCircle className="h-3 w-3 mr-1" />
                New User
              </Badge>
            )}
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Credits Progress */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Usage</span>
            <span className="font-medium">
              {credits.used} / {credits.limit} credits
            </span>
          </div>
          
          <div className="w-full bg-muted rounded-full h-2">
            <div 
              className={`h-2 rounded-full transition-all duration-300 ${
                isOutOfCredits 
                  ? 'bg-red-500' 
                  : isLowCredits 
                    ? 'bg-yellow-500' 
                    : 'bg-primary'
              }`}
              style={{ width: `${Math.min(usagePercentage, 100)}%` }}
            />
          </div>
          
          <div className="flex items-center justify-between text-xs text-muted-foreground">
            <span>{credits.remaining} remaining</span>
            <span>{usagePercentage.toFixed(1)}% used</span>
          </div>
        </div>

        {/* Status Message */}
        {isOutOfCredits ? (
          <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-lg">
            <AlertCircle className="h-4 w-4 text-red-500" />
            <span className="text-sm text-red-700">
              No credits remaining. Upgrade your plan to continue.
            </span>
          </div>
        ) : isLowCredits ? (
          <div className="flex items-center gap-2 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
            <AlertCircle className="h-4 w-4 text-yellow-500" />
            <span className="text-sm text-yellow-700">
              Low credits remaining. Consider upgrading your plan.
            </span>
          </div>
        ) : credits.isNewUser ? (
          <div className="flex items-center gap-2 p-3 bg-green-50 border border-green-200 rounded-lg">
            <CheckCircle className="h-4 w-4 text-green-500" />
            <span className="text-sm text-green-700">
              Welcome! You have 10 free credits to get started.
            </span>
          </div>
        ) : (
          <div className="flex items-center gap-2 p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <CheckCircle className="h-4 w-4 text-blue-500" />
            <span className="text-sm text-blue-700">
              {credits.remaining} credits available for use.
            </span>
          </div>
        )}

        {/* Plan Features */}
        {credits.features.length > 0 && (
          <div className="space-y-2">
            <span className="text-sm font-medium text-muted-foreground">Plan Features:</span>
            <div className="flex flex-wrap gap-1">
              {credits.features.map((feature, index) => (
                <Badge key={index} variant="outline" className="text-xs">
                  {feature.replace('_', ' ')}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex gap-2 pt-2">
          <Link href="/chat" className="flex-1">
            <Button 
              size="sm" 
              className="w-full"
            >
              <MessageSquare className="h-4 w-4 mr-2" />
              Start Chat
            </Button>
          </Link>
          
          <Button 
            variant="outline" 
            size="sm" 
            onClick={fetchCredits}
            className="flex-1"
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          
          {credits.plan === 'free' && (
            <Button size="sm" className="flex-1">
              <Plus className="h-4 w-4 mr-2" />
              Upgrade
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
