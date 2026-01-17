"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
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

  if (loading) {
    return (
      <div className="border-2 border-foreground p-6 bg-background flex flex-col items-center justify-center min-h-[200px]">
        <RefreshCw className="h-8 w-8 animate-spin text-accent" />
        <span className="mt-4 text-[10px] font-black uppercase tracking-[0.3em]">RETRIVING CREDIT DATA...</span>
      </div>
    )
  }

  if (error) {
    return (
      <div className="border-2 border-foreground p-6 bg-red-500 text-white font-black">
        <div className="flex items-center gap-2 mb-2">
          <AlertCircle className="h-5 w-5" />
          <span className="uppercase tracking-tighter">ERROR SYNC FAILED</span>
        </div>
        <p className="text-xs uppercase">{error}</p>
        <Button onClick={fetchCredits} variant="outline" className="mt-4 border-white text-white hover:bg-white hover:text-black w-full">
          RETRY CONNECTION
        </Button>
      </div>
    )
  }

  if (!credits) return null

  const usagePercentage = (credits.used / credits.limit) * 100
  const isOutOfCredits = credits.remaining === 0

  return (
    <div className="border-2 border-foreground bg-background p-1 hover:shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] transition-all">
      <div className="bg-foreground text-background p-4 flex justify-between items-center mb-1">
        <div className="flex items-center gap-2">
          <Coins className="h-5 w-5 text-accent" />
          <span className="font-black tracking-tighter uppercase">CREDITS REMAINING</span>
        </div>
        <div className="bg-accent text-black px-2 py-0.5 text-[10px] font-black uppercase">
          {credits.planName}
        </div>
      </div>
      
      <div className="p-4 space-y-6">
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-black uppercase text-foreground/80">USAGE LEVEL</span>
            <span className="text-xl font-black tracking-tighter">
              {credits.used} / {credits.limit}
            </span>
          </div>
          
          <div className="w-full bg-muted/20 border border-foreground h-4 relative">
            <div 
              className={`h-full transition-all duration-500 ${isOutOfCredits ? 'bg-red-500' : 'bg-accent'
              }`}
              style={{ width: `${Math.min(usagePercentage, 100)}%` }}
            />
            {/* Grid overlay for the progress bar */}
            <div className="absolute inset-0 opacity-20 pointer-events-none" style={{ backgroundImage: "linear-gradient(to right, #000 2px, transparent 2px)", backgroundSize: "8px 100%" }} />
          </div>
          
          <div className="flex justify-between text-[10px] font-black uppercase opacity-50">
            <span>{credits.remaining} L UNITS LEFT</span>
            <span>{usagePercentage.toFixed(0)}% EXHAUSTED</span>
          </div>
        </div>

        <div className={`p-3 border-2 ${isOutOfCredits ? 'border-red-500 bg-red-500/5 text-red-500' : 'border-accent bg-accent/5 text-accent'} flex items-center gap-3`}>
          {isOutOfCredits ? <AlertCircle className="h-5 w-5" /> : <CheckCircle className="h-5 w-5" />}
          <span className="text-[10px] font-black uppercase leading-tight">
            {isOutOfCredits
              ? "ZERO CREDITS DETECTED. PLEASE UPGRADE ACCESS."
              : `${credits.remaining} UNITS READY FOR DEPLOYMENT.`}
          </span>
        </div>

        {credits.features.length > 0 && (
          <div className="space-y-2">
            <span className="text-[10px] font-black text-foreground/80 uppercase">ACCESS LEVEL PERKS:</span>
            <div className="flex flex-wrap gap-2">
              {credits.features.map((feature, index) => (
                <div key={index} className="border border-foreground/30 px-2 py-0.5 text-[8px] font-black uppercase">
                  {`# ${feature.replace('_', ' ')}`}
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="grid grid-cols-2 gap-2 pt-2">
          <Link href="/chat" className="col-span-2">
            <Button variant="terminal" className="w-full h-12 uppercase text-xs">
              <MessageSquare className="h-4 w-4 mr-2" />
              START CHAT SESSION
            </Button>
          </Link>
          
          <Button 
            variant="outline" 
            size="sm" 
            onClick={fetchCredits}
            className="border-2 font-black uppercase text-[10px]"
          >
            <RefreshCw className="h-3 w-3 mr-2" />
            SYNC DATA
          </Button>
          
          {credits.plan === 'free' && (
            <Button variant="outline" size="sm" className="border-2 border-accent text-accent hover:bg-accent hover:text-black font-black uppercase text-[10px] bg-black">
              <Plus className="h-3 w-3 mr-2" />
              UPGRADE TIER
            </Button>
          )}
        </div>
      </div>
    </div>
  )
}
