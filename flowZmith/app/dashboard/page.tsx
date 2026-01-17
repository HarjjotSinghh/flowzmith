"use client"

import { useEffect, useState } from "react"
import { useSession } from "next-auth/react"
import { useRouter } from "next/navigation"
import { DashboardHeader } from "@/components/dashboard/dashboard-header"
import { UsageStats } from "@/components/dashboard/usage-stats"
import { CostTracking } from "@/components/dashboard/cost-tracking"
import { RequestTimeline } from "@/components/dashboard/request-timeline"
import { RecentActivity } from "@/components/dashboard/recent-activity"
import { QuickActions } from "@/components/dashboard/quick-actions"
import { CreditsDisplay } from "@/components/dashboard/credits-display"
import { AnimatedSection } from "@/components/animated-section"

export default function DashboardPage() {
  const { data: session, status } = useSession()
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    if (status === "loading") return
    
    if (!session) {
      router.push("/login")
      return
    }
    
    setIsLoading(false)
  }, [session, status, router])

  if (isLoading || status === "loading") {
    return (
      <div className="min-h-screen bg-black flex flex-col items-center justify-center font-mono text-accent">
        <div className="text-4xl font-black mb-4 animate-pulse">LOADING SYSTEM RESOURCES...</div>
        <div className="w-64 h-2 bg-muted/20 border border-accent overflow-hidden">
          <div className="h-full bg-accent animate-[loading_2s_ease-in-out_infinite]" style={{ width: '40%' }}></div>
        </div>
        <div className="mt-4 text-[10px] tracking-[0.5em] opacity-50 uppercase">AUTHENTICATING USER PROTOCOL</div>
        <style jsx>{`
          @keyframes loading {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(300%); }
          }
        `}</style>
      </div>
    )
  }

  if (!session) {
    return null
  }

  return (
    <div className="min-h-screen bg-background font-mono text-foreground border-x-2 border-foreground mx-auto max-w-[1440px]">
      <DashboardHeader user={session.user} />
      
      <div className="px-6 py-8">
        <AnimatedSection delay={0.1}>
          <div className="mb-12 border-b-2 border-foreground pb-8 flex flex-col md:flex-row md:items-end justify-between gap-4">
            <div>
              <div className="inline-block bg-accent text-black font-black px-2 py-0.5 text-xs mb-4">
                SESSION ACTIVE // {session.user?.email}
              </div>
              <h1 className="text-5xl md:text-7xl font-black tracking-tighter uppercase leading-none">
                WELCOME BACK.
              </h1>
              <p className="text-xl font-bold text-foreground/80 mt-4 border-l-4 border-accent pl-6">
                AI DEVELOPMENT DASHBOARD // USAGE INSIGHTS AND ANALYTICS V4.2
              </p>
            </div>
            <div className="text-right hidden md:block">
              <div className="text-[10px] font-black opacity-50 uppercase tracking-widest">SERVER TIME</div>
              <div className="text-2xl font-black">{new Date().toLocaleTimeString()}</div>
            </div>
          </div>
        </AnimatedSection>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Left Column - Stats and Cost */}
          <div className="lg:col-span-8 space-y-8">
            <AnimatedSection delay={0.2}>
              <div className="border-2 border-foreground p-1">
                <div className="bg-foreground text-background px-4 py-1 text-xs font-black">USAGE METRICS REALTIME</div>
                <div className="p-4 bg-muted/5">
                  <UsageStats />
                </div>
              </div>
            </AnimatedSection>
            
            <div className="grid md:grid-cols-2 gap-8">
              <AnimatedSection delay={0.3}>
                <div className="border-2 border-foreground p-1 h-full">
                  <div className="bg-foreground text-background px-4 py-1 text-xs font-black">COST TRACKING</div>
                  <div className="p-4 bg-muted/5">
                    <CostTracking />
                  </div>
                </div>
              </AnimatedSection>
              <AnimatedSection delay={0.4}>
                <div className="border-2 border-foreground p-1 h-full">
                  <div className="bg-foreground text-background px-4 py-1 text-xs font-black">QUICK ACTIONS</div>
                  <div className="p-4 bg-muted/5">
                    <QuickActions />
                  </div>
                </div>
              </AnimatedSection>
            </div>
            
            <AnimatedSection delay={0.5}>
              <div className="border-2 border-foreground p-1">
                <div className="bg-foreground text-background px-4 py-1 text-xs font-black">REQUEST TIMELINE LATENCY</div>
                <div className="p-4 bg-muted/5">
                  <RequestTimeline />
                </div>
              </div>
            </AnimatedSection>
          </div>

          {/* Right Column - Activity and Actions */}
          <div className="lg:col-span-4 space-y-8">
            <AnimatedSection delay={0.2}>
              <div className="border-2 border-foreground p-1">
                <div className="bg-accent text-black px-4 py-1 text-xs font-black">CREDITS REMAINING</div>
                <div className="p-4 bg-muted/5">
                  <CreditsDisplay user={{
                    email: session.user.email,
                    name: session.user.name || undefined
                  }} />
                </div>
              </div>
            </AnimatedSection>
            
            <AnimatedSection delay={0.3}>
              <div className="border-2 border-foreground p-1">
                <div className="bg-foreground text-background px-4 py-1 text-xs font-black">RECENT ACTIVITY LOG</div>
                <div className="p-4 bg-muted/5 h-[600px] overflow-auto custom-scrollbar">
                  <RecentActivity />
                </div>
              </div>
            </AnimatedSection>
          </div>
        </div>
      </div>

      <div className="border-t-2 border-foreground p-4 text-[10px] font-black flex justify-between uppercase opacity-50">
        <span>ENCRYPTED CONNECTION: AES-256</span>
        <span>FLOWZMITH CORE DASHBOARD V4</span>
      </div>
    </div>
  )
}
