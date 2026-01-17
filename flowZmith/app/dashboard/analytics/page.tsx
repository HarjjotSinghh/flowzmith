"use client"

import { useState } from "react"
import { useSession } from "next-auth/react"
import { AnimatedSection } from "@/components/animated-section"
import { DashboardHeader } from "@/components/dashboard/dashboard-header"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { 
  TrendingUp, 
  TrendingDown, 
  Activity, 
  Users, 
  Code, 
  DollarSign,
  BarChart3,
  PieChart,
  LineChart,
  Download,
  Filter,
  Calendar,
  ArrowUpRight,
  ArrowDownRight,
  Zap,
  Shield,
  Clock
} from "lucide-react"

interface MetricCard {
  title: string
  value: string
  change: number
  changeType: "increase" | "decrease"
  icon: React.ReactNode
  description: string
}

interface ChartData {
  name: string
  value: number
  color: string
}

export default function AnalyticsPage() {
  const { data: session } = useSession()
  const [timeRange, setTimeRange] = useState<"7d" | "30d" | "90d" | "1y">("30d")
  const [activeTab, setActiveTab] = useState<"overview" | "contracts" | "usage" | "performance">("overview")

  const metrics: MetricCard[] = [
    {
      title: "Total Contracts",
      value: "24",
      change: 12.5,
      changeType: "increase",
      icon: <Code className="h-5 w-5" />,
      description: "Smart contracts deployed"
    },
    {
      title: "Active Users",
      value: "1,247",
      change: 8.2,
      changeType: "increase",
      icon: <Users className="h-5 w-5" />,
      description: "Monthly active users"
    },
    {
      title: "Gas Usage",
      value: "2.4K FLOW",
      change: -3.1,
      changeType: "decrease",
      icon: <Zap className="h-5 w-5" />,
      description: "Total gas consumed"
    },
    {
      title: "Revenue",
      value: "$12,847",
      change: 15.3,
      changeType: "increase",
      icon: <DollarSign className="h-5 w-5" />,
      description: "Platform revenue"
    }
  ]

  const contractTypes: ChartData[] = [
    { name: "NFT", value: 8, color: "hsl(var(--primary))" },
    { name: "Token", value: 6, color: "hsl(var(--secondary))" },
    { name: "Marketplace", value: 4, color: "hsl(var(--accent))" },
    { name: "DAO", value: 3, color: "hsl(var(--muted-foreground))" },
    { name: "DeFi", value: 3, color: "hsl(var(--destructive))" }
  ]

  const usageData = [
    { day: "Mon", contracts: 4, users: 120 },
    { day: "Tue", contracts: 6, users: 180 },
    { day: "Wed", contracts: 3, users: 95 },
    { day: "Thu", contracts: 8, users: 220 },
    { day: "Fri", contracts: 5, users: 150 },
    { day: "Sat", contracts: 2, users: 80 },
    { day: "Sun", contracts: 1, users: 45 }
  ]

  const performanceMetrics = [
    { name: "Deployment Success Rate", value: "98.5%", trend: "up" },
    { name: "Average Gas Cost", value: "0.0012 FLOW", trend: "down" },
    { name: "Security Score", value: "94.2", trend: "up" },
    { name: "Response Time", value: "1.2s", trend: "down" }
  ]

  return (
    <div className="min-h-screen bg-background font-mono text-foreground border-x-2 border-foreground mx-auto max-w-[1440px]">
      <DashboardHeader user={session?.user} />
      
      <div className="px-6 py-8">
        <AnimatedSection delay={0.1}>
          <div className="flex items-center justify-between mb-8 border-b-2 border-foreground pb-6">
            <div>
              <h1 className="text-4xl md:text-6xl font-black tracking-tighter uppercase leading-none">ANALYTICS.</h1>
              <p className="text-lg font-bold text-foreground/80 mt-2 border-l-4 border-accent pl-4">
                TRACK YOUR PLATFORM PERFORMANCE AND USAGE METRICS V4.2
              </p>
            </div>
            <div className="flex items-center gap-2">
              <Button variant="outline" className="flex items-center gap-2 font-black text-xs h-10">
                <Filter className="h-4 w-4" />
                FILTER
              </Button>
              <Button variant="outline" className="flex items-center gap-2 font-black text-xs h-10">
                <Download className="h-4 w-4" />
                EXPORT
              </Button>
            </div>
          </div>
        </AnimatedSection>

        {/* Time Range Selector */}
        <AnimatedSection delay={0.2}>
          <div className="flex flex-wrap gap-2 mb-8">
            {[
              { key: "7d", label: "LAST 7 DAYS" },
              { key: "30d", label: "LAST 30 DAYS" },
              { key: "90d", label: "LAST 90 DAYS" },
              { key: "1y", label: "LAST YEAR" }
            ].map((range) => (
              <button
                key={range.key}
                onClick={() => setTimeRange(range.key as any)}
                className={`px-4 py-2 border-2 border-foreground text-[10px] font-black tracking-widest transition-all ${
                  timeRange === range.key
                    ? "bg-accent text-black"
                  : "bg-background text-foreground hover:bg-muted"
                }`}
              >
                {range.label}
              </button>
            ))}
          </div>
        </AnimatedSection>

        {/* Metrics Grid */}
        <AnimatedSection delay={0.3}>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
            {metrics.map((metric, index) => (
              <Card key={metric.title} className="hover:translate-y-[-4px] transition-transform duration-200 group">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-[10px] font-black text-foreground/80 mb-1 uppercase tracking-widest">
                        {metric.title}
                      </p>
                      <p className="text-3xl font-black text-foreground mb-1 tracking-tighter uppercase">
                        {metric.value}
                      </p>
                      <div className="flex items-center gap-1">
                        {metric.changeType === "increase" ? (
                          <ArrowUpRight className="h-4 w-4 text-accent" />
                        ) : (
                            <ArrowDownRight className="h-4 w-4 text-foreground/80" />
                        )}
                        <span className={`text-[10px] font-black px-1 ${
                          metric.changeType === "increase" ? "bg-accent text-black" : "bg-black text-white"
                        }`}>
                          {metric.change > 0 ? "+" : ""}{metric.change}%
                        </span>
                      </div>
                    </div>
                    <div className="p-3 bg-black border border-foreground group-hover:bg-accent transition-colors">
                      <div className="text-accent group-hover:text-black">
                        {metric.icon}
                      </div>
                    </div>
                  </div>
                  <p className="text-[10px] font-bold text-foreground/60 mt-4 uppercase">
                    {metric.description}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        </AnimatedSection>

        {/* Tab Navigation */}
        <AnimatedSection delay={0.4}>
          <div className="flex flex-wrap gap-2 mb-8 border-b-2 border-foreground pb-4">
            {[
              { key: "overview", label: "OVERVIEW", icon: <BarChart3 className="h-4 w-4" /> },
              { key: "contracts", label: "CONTRACTS", icon: <Code className="h-4 w-4" /> },
              { key: "usage", label: "USAGE", icon: <Activity className="h-4 w-4" /> },
              { key: "performance", label: "PERFORMANCE", icon: <Shield className="h-4 w-4" /> }
            ].map((tab) => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key as any)}
                className={`flex items-center gap-2 px-6 py-3 border-2 border-foreground text-xs font-black tracking-tighter transition-all ${
                  activeTab === tab.key
                    ? "bg-foreground text-background"
                  : "bg-background text-foreground hover:bg-muted"
                }`}
              >
                {tab.icon}
                {tab.label}
              </button>
            ))}
          </div>
        </AnimatedSection>

        {/* Content based on active tab */}
        {activeTab === "overview" && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <AnimatedSection delay={0.5}>
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <PieChart className="h-5 w-5" />
                    Contract Types Distribution
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {contractTypes.map((type, index) => (
                      <div key={type.name} className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <div 
                            className="w-3 h-3 rounded-full" 
                            style={{ backgroundColor: type.color }}
                          />
                          <span className="text-sm font-medium">{type.name}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-sm text-foreground/80">{type.value} contracts</span>
                          <div className="w-16 bg-muted rounded-full h-2">
                            <div 
                              className="h-2 rounded-full" 
                              style={{ 
                                backgroundColor: type.color,
                                width: `${(type.value / 24) * 100}%`
                              }}
                            />
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </AnimatedSection>

            <AnimatedSection delay={0.6}>
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <LineChart className="h-5 w-5" />
                    Weekly Activity
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {usageData.map((data, index) => (
                      <div key={data.day} className="flex items-center justify-between">
                        <span className="text-sm font-medium">{data.day}</span>
                        <div className="flex items-center gap-4">
                          <div className="flex items-center gap-2">
                            <span className="text-xs text-foreground/80">Contracts:</span>
                            <span className="text-sm font-medium">{data.contracts}</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <span className="text-xs text-foreground/80">Users:</span>
                            <span className="text-sm font-medium">{data.users}</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </AnimatedSection>
          </div>
        )}

        {activeTab === "performance" && (
          <AnimatedSection delay={0.5}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {performanceMetrics.map((metric, index) => (
                <Card key={metric.name}>
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-foreground/80 mb-1">
                          {metric.name}
                        </p>
                        <p className="text-2xl font-bold text-foreground">
                          {metric.value}
                        </p>
                      </div>
                      <div className="p-3 bg-primary/10 rounded-lg">
                        {metric.trend === "up" ? (
                          <TrendingUp className="h-5 w-5 text-primary" />
                        ) : (
                            <TrendingDown className="h-5 w-5 text-foreground/80" />
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </AnimatedSection>
        )}

        {activeTab === "usage" && (
          <AnimatedSection delay={0.5}>
            <Card>
              <CardHeader>
                <CardTitle>Usage Analytics</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center py-12">
                  <Activity className="h-12 w-12 text-foreground/80 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-foreground mb-2">Usage Analytics</h3>
                  <p className="text-foreground/80">
                    Detailed usage analytics and insights coming soon
                  </p>
                </div>
              </CardContent>
            </Card>
          </AnimatedSection>
        )}

        {activeTab === "contracts" && (
          <AnimatedSection delay={0.5}>
            <Card>
              <CardHeader>
                <CardTitle>Contract Analytics</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center py-12">
                  <Code className="h-12 w-12 text-foreground/80 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-foreground mb-2">Contract Analytics</h3>
                  <p className="text-foreground/80">
                    Detailed contract analytics and insights coming soon
                  </p>
                </div>
              </CardContent>
            </Card>
          </AnimatedSection>
        )}
      </div>
    </div>
  )
}
