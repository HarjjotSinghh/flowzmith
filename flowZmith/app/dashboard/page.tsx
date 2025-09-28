"use client"

import { useEffect, useState } from "react"
import { useSession } from "next-auth/react"
import { useRouter } from "next/navigation"
import { AnimatedSection } from "@/components/animated-section"
import { DashboardHeader } from "@/components/dashboard/dashboard-header"
import { UsageStats } from "@/components/dashboard/usage-stats"
import { CostTracking } from "@/components/dashboard/cost-tracking"
import { RequestTimeline } from "@/components/dashboard/request-timeline"
import { RecentActivity } from "@/components/dashboard/recent-activity"
import { QuickActions } from "@/components/dashboard/quick-actions"
import { CreditsDisplay } from "@/components/dashboard/credits-display"

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
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    )
  }

  if (!session) {
    return null
  }

  return (
    <div className="min-h-screen bg-background">
      <DashboardHeader user={session.user} />
      
      <div className="max-w-[1320px] mx-auto px-6 py-8">
        <AnimatedSection delay={0.1}>
          <div className="mb-8">
            <h1 className="text-3xl font-semibold text-foreground mb-2">
              Welcome back, {session.user?.name || session.user?.email}
            </h1>
            <p className="text-muted-foreground">
              Here's your AI development dashboard with usage insights and analytics.
            </p>
          </div>
        </AnimatedSection>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Stats and Cost */}
          <div className="lg:col-span-2 space-y-6">
            <AnimatedSection delay={0.2}>
              <UsageStats />
            </AnimatedSection>
            
            <AnimatedSection delay={0.3}>
              <CostTracking />
            </AnimatedSection>
            
            <AnimatedSection delay={0.4}>
              <RequestTimeline />
            </AnimatedSection>
          </div>

          {/* Right Column - Activity and Actions */}
          <div className="space-y-6">
            <AnimatedSection delay={0.2}>
              <CreditsDisplay user={{ 
                email: session.user.email, 
                name: session.user.name || undefined 
              }} />
            </AnimatedSection>
            
            <AnimatedSection delay={0.3}>
              <QuickActions />
            </AnimatedSection>
            
            <AnimatedSection delay={0.4}>
              <RecentActivity />
            </AnimatedSection>
          </div>
        </div>
      </div>
    </div>
  )
}
