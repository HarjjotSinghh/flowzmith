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
    <div className="min-h-screen bg-background">
      <DashboardHeader user={session?.user} />
      
      <div className="max-w-[1320px] mx-auto px-6 py-8">
        <AnimatedSection delay={0.1}>
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-3xl font-semibold text-foreground mb-2">Analytics</h1>
              <p className="text-muted-foreground">
                Track your platform performance and usage metrics
              </p>
            </div>
            <div className="flex items-center gap-2">
              <Button variant="outline" className="flex items-center gap-2">
                <Filter className="h-4 w-4" />
                Filter
              </Button>
              <Button variant="outline" className="flex items-center gap-2">
                <Download className="h-4 w-4" />
                Export
              </Button>
            </div>
          </div>
        </AnimatedSection>

        {/* Time Range Selector */}
        <AnimatedSection delay={0.2}>
          <div className="flex space-x-1 mb-6">
            {[
              { key: "7d", label: "Last 7 days" },
              { key: "30d", label: "Last 30 days" },
              { key: "90d", label: "Last 90 days" },
              { key: "1y", label: "Last year" }
            ].map((range) => (
              <button
                key={range.key}
                onClick={() => setTimeRange(range.key as any)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  timeRange === range.key
                    ? "bg-primary text-primary-foreground"
                    : "text-muted-foreground hover:text-foreground hover:bg-muted"
                }`}
              >
                {range.label}
              </button>
            ))}
          </div>
        </AnimatedSection>

        {/* Metrics Grid */}
        <AnimatedSection delay={0.3}>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {metrics.map((metric, index) => (
              <Card key={metric.title} className="hover:shadow-lg transition-all duration-200">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-muted-foreground mb-1">
                        {metric.title}
                      </p>
                      <p className="text-2xl font-bold text-foreground mb-1">
                        {metric.value}
                      </p>
                      <div className="flex items-center gap-1">
                        {metric.changeType === "increase" ? (
                          <ArrowUpRight className="h-4 w-4 text-green-500" />
                        ) : (
                          <ArrowDownRight className="h-4 w-4 text-red-500" />
                        )}
                        <span className={`text-sm font-medium ${
                          metric.changeType === "increase" ? "text-green-500" : "text-red-500"
                        }`}>
                          {metric.change > 0 ? "+" : ""}{metric.change}%
                        </span>
                      </div>
                    </div>
                    <div className="p-3 bg-primary/10 rounded-lg">
                      {metric.icon}
                    </div>
                  </div>
                  <p className="text-xs text-muted-foreground mt-2">
                    {metric.description}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        </AnimatedSection>

        {/* Tab Navigation */}
        <AnimatedSection delay={0.4}>
          <div className="flex space-x-1 mb-6">
            {[
              { key: "overview", label: "Overview", icon: <BarChart3 className="h-4 w-4" /> },
              { key: "contracts", label: "Contracts", icon: <Code className="h-4 w-4" /> },
              { key: "usage", label: "Usage", icon: <Activity className="h-4 w-4" /> },
              { key: "performance", label: "Performance", icon: <Shield className="h-4 w-4" /> }
            ].map((tab) => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key as any)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  activeTab === tab.key
                    ? "bg-primary text-primary-foreground"
                    : "text-muted-foreground hover:text-foreground hover:bg-muted"
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
                          <span className="text-sm text-muted-foreground">{type.value} contracts</span>
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
                            <span className="text-xs text-muted-foreground">Contracts:</span>
                            <span className="text-sm font-medium">{data.contracts}</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <span className="text-xs text-muted-foreground">Users:</span>
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
                        <p className="text-sm font-medium text-muted-foreground mb-1">
                          {metric.name}
                        </p>
                        <p className="text-2xl font-bold text-foreground">
                          {metric.value}
                        </p>
                      </div>
                      <div className="p-3 bg-primary/10 rounded-lg">
                        {metric.trend === "up" ? (
                          <TrendingUp className="h-5 w-5 text-green-500" />
                        ) : (
                          <TrendingDown className="h-5 w-5 text-red-500" />
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
                  <Activity className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-foreground mb-2">Usage Analytics</h3>
                  <p className="text-muted-foreground">
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
                  <Code className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-foreground mb-2">Contract Analytics</h3>
                  <p className="text-muted-foreground">
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
