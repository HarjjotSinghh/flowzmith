"use client"

import { useEffect, useState } from "react"
import { useSession } from "next-auth/react"
import { useRouter } from "next/navigation"
import { motion, AnimatePresence } from "framer-motion"
import { Sparkles, Zap, TrendingUp, Activity, Settings, Bell } from "lucide-react"

import { AnimatedSection } from "@/components/animated-section"
import { DashboardHeader } from "@/components/dashboard/dashboard-header"
import { EnhancedUsageStats } from "@/components/dashboard/enhanced-usage-stats"
import { CostTracking } from "@/components/dashboard/cost-tracking"
import { RequestTimeline } from "@/components/dashboard/request-timeline"
import { EnhancedRecentActivity } from "@/components/dashboard/enhanced-recent-activity"
import { StreamingQuickActions } from "@/components/dashboard/streaming-quick-actions"
import { CreditsDisplay } from "@/components/dashboard/credits-display"
import { StreamingWidgets } from "@/components/dashboard/streaming-widgets"

interface DashboardStats {
  totalContracts: number
  activeStreams: number
  successRate: number
  avgResponseTime: number
}

export default function EnhancedDashboardPage() {
  const { data: session, status } = useSession()
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(true)
  const [dashboardStats, setDashboardStats] = useState<DashboardStats>({
    totalContracts: 0,
    activeStreams: 0,
    successRate: 0,
    avgResponseTime: 0
  })

  useEffect(() => {
    if (status === "loading") return
    
    if (!session) {
      router.push("/login")
      return
    }
    
    setIsLoading(false)
    
    // Simulate real-time stats updates
    const statsInterval = setInterval(() => {
      setDashboardStats(prev => ({
        totalContracts: prev.totalContracts + Math.floor(Math.random() * 2),
        activeStreams: Math.floor(Math.random() * 5),
        successRate: 95 + Math.random() * 5,
        avgResponseTime: 150 + Math.random() * 100
      }))
    }, 5000)

    return () => clearInterval(statsInterval)
  }, [session, status, router])

  if (isLoading || status === "loading") {
    return (
      <div className="min-h-screen bg-gradient-to-br from-background via-background to-background/95 flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          className="flex flex-col items-center space-y-4"
        >
          <div className="relative">
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
              className="w-12 h-12 border-4 border-primary/20 border-t-primary rounded-full"
            />
            <motion.div
              animate={{ rotate: -360 }}
              transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
              className="absolute inset-2 w-8 h-8 border-2 border-purple-500/30 border-b-purple-500 rounded-full"
            />
          </div>
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
            className="text-muted-foreground"
          >
            Loading your enhanced dashboard...
          </motion.p>
        </motion.div>
      </div>
    )
  }

  if (!session) {
    return null
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-background/95">
      {/* Background Effects */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-500/5 rounded-full blur-3xl" />
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-blue-500/5 rounded-full blur-3xl" />
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-gradient-to-r from-purple-500/3 to-blue-500/3 rounded-full blur-3xl" />
      </div>

      <DashboardHeader user={session.user} />
      
      <div className="relative max-w-[1400px] mx-auto px-6 py-8">
        {/* Welcome Section */}
        <AnimatedSection delay={0.1}>
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-8"
          >
            <div className="flex items-center justify-between mb-6">
              <div>
                <h1 className="text-4xl font-bold bg-gradient-to-r from-foreground via-foreground to-foreground/70 bg-clip-text text-transparent mb-2">
                  Welcome back, {session.user?.name?.split(' ')[0] || 'Developer'}
                </h1>
                <p className="text-lg text-muted-foreground">
                  Your AI-powered smart contract development hub with real-time insights
                </p>
              </div>
              
              <div className="flex items-center space-x-3">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="p-3 bg-card/50 hover:bg-card/70 border border-border/50 rounded-xl transition-all duration-200"
                >
                  <Bell className="h-5 w-5 text-muted-foreground" />
                </motion.button>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="p-3 bg-card/50 hover:bg-card/70 border border-border/50 rounded-xl transition-all duration-200"
                >
                  <Settings className="h-5 w-5 text-muted-foreground" />
                </motion.button>
              </div>
            </div>

            {/* Quick Stats Bar */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8"
            >
              <div className="bg-gradient-to-r from-purple-500/10 to-purple-500/5 border border-purple-500/20 rounded-xl p-4">
                <div className="flex items-center space-x-2 mb-1">
                  <Sparkles className="h-4 w-4 text-purple-500" />
                  <span className="text-sm text-muted-foreground">Contracts</span>
                </div>
                <motion.div
                  key={dashboardStats.totalContracts}
                  initial={{ scale: 1.1, color: "#a855f7" }}
                  animate={{ scale: 1, color: "inherit" }}
                  className="text-2xl font-bold text-foreground"
                >
                  {dashboardStats.totalContracts}
                </motion.div>
              </div>

              <div className="bg-gradient-to-r from-blue-500/10 to-blue-500/5 border border-blue-500/20 rounded-xl p-4">
                <div className="flex items-center space-x-2 mb-1">
                  <Activity className="h-4 w-4 text-blue-500" />
                  <span className="text-sm text-muted-foreground">Live Streams</span>
                </div>
                <motion.div
                  key={dashboardStats.activeStreams}
                  initial={{ scale: 1.1, color: "#3b82f6" }}
                  animate={{ scale: 1, color: "inherit" }}
                  className="text-2xl font-bold text-foreground"
                >
                  {dashboardStats.activeStreams}
                </motion.div>
              </div>

              <div className="bg-gradient-to-r from-green-500/10 to-green-500/5 border border-green-500/20 rounded-xl p-4">
                <div className="flex items-center space-x-2 mb-1">
                  <TrendingUp className="h-4 w-4 text-green-500" />
                  <span className="text-sm text-muted-foreground">Success Rate</span>
                </div>
                <motion.div
                  key={Math.round(dashboardStats.successRate)}
                  initial={{ scale: 1.1, color: "#10b981" }}
                  animate={{ scale: 1, color: "inherit" }}
                  className="text-2xl font-bold text-foreground"
                >
                  {dashboardStats.successRate.toFixed(1)}%
                </motion.div>
              </div>

              <div className="bg-gradient-to-r from-orange-500/10 to-orange-500/5 border border-orange-500/20 rounded-xl p-4">
                <div className="flex items-center space-x-2 mb-1">
                  <Zap className="h-4 w-4 text-orange-500" />
                  <span className="text-sm text-muted-foreground">Avg Response</span>
                </div>
                <motion.div
                  key={Math.round(dashboardStats.avgResponseTime)}
                  initial={{ scale: 1.1, color: "#f97316" }}
                  animate={{ scale: 1, color: "inherit" }}
                  className="text-2xl font-bold text-foreground"
                >
                  {Math.round(dashboardStats.avgResponseTime)}ms
                </motion.div>
              </div>
            </motion.div>
          </motion.div>
        </AnimatedSection>

        {/* Streaming Widgets */}
        <AnimatedSection delay={0.3}>
          <div className="mb-8">
            <StreamingWidgets />
          </div>
        </AnimatedSection>

        {/* Main Dashboard Grid */}
        <div className="grid grid-cols-1 xl:grid-cols-12 gap-6">
          {/* Left Column - Primary Stats and Analytics */}
          <div className="xl:col-span-8 space-y-6">
            <AnimatedSection delay={0.4}>
              <EnhancedUsageStats />
            </AnimatedSection>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <AnimatedSection delay={0.5}>
                <CostTracking />
              </AnimatedSection>
              
              <AnimatedSection delay={0.6}>
                <RequestTimeline />
              </AnimatedSection>
            </div>
          </div>

          {/* Right Column - Actions and Activity */}
          <div className="xl:col-span-4 space-y-6">
            <AnimatedSection delay={0.4}>
              <CreditsDisplay user={{ 
                email: session.user.email, 
                name: session.user.name || undefined 
              }} />
            </AnimatedSection>
            
            <AnimatedSection delay={0.5}>
              <StreamingQuickActions />
            </AnimatedSection>
            
            <AnimatedSection delay={0.6}>
              <EnhancedRecentActivity />
            </AnimatedSection>
          </div>
        </div>

        {/* Footer */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
          className="mt-12 pt-8 border-t border-border/50 text-center"
        >
          <p className="text-sm text-muted-foreground">
            Powered by AI • Real-time streaming • Enhanced UX
          </p>
        </motion.div>
      </div>
    </div>
  )
}