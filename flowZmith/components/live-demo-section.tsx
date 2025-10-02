"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Play, Pause, RotateCcw, Users, Database, Bot, Zap, Eye, Code2, Activity } from "lucide-react"
import Link from "next/link"

interface LiveMetric {
  label: string
  value: string
  change: string
  trend: "up" | "down" | "stable"
}

const LiveDemoSection = () => {
  const [isDemoRunning, setIsDemoRunning] = useState(false)
  const [currentStep, setCurrentStep] = useState(0)
  const [metrics, setMetrics] = useState<LiveMetric[]>([
    { label: "Active Users", value: "12", change: "+2", trend: "up" },
    { label: "Contracts Created", value: "47", change: "+5", trend: "up" },
    { label: "Real-time Syncs", value: "1,284", change: "+127", trend: "up" },
    { label: "API Calls", value: "8.2K", change: "+892", trend: "up" }
  ])

  const demoSteps = [
    {
      title: "User Joins Platform",
      description: "New developer connects to real-time workspace",
      icon: Users,
      tech: "Convex Auth"
    },
    {
      title: "AI Generates Contract",
      description: "OpenAI creates Cadence smart contract from natural language",
      icon: Bot,
      tech: "GPT-5 Integration"
    },
    {
      title: "Data Crawled Live",
      description: "Firecrawl fetches latest Flow documentation for context",
      icon: Database,
      tech: "Firecrawl API"
    },
    {
      title: "Real-time Collaboration",
      description: "Multiple users edit contract simultaneously with live sync",
      icon: Zap,
      tech: "Convex Real-time"
    },
    {
      title: "Contract Deployed",
      description: "Smart contract deployed to Flow blockchain successfully",
      icon: Code2,
      tech: "Flow CLI"
    }
  ]

  useEffect(() => {
    if (isDemoRunning) {
      const interval = setInterval(() => {
        setMetrics(prev => prev.map(metric => ({
          ...metric,
          value: metric.label === "Active Users"
            ? String(parseInt(metric.value) + Math.floor(Math.random() * 3))
            : metric.label === "Contracts Created"
            ? String(parseInt(metric.value) + Math.floor(Math.random() * 2))
            : metric.label === "Real-time Syncs"
            ? String(parseInt(metric.value.replace(/,/g, '')) + Math.floor(Math.random() * 50)).replace(/\B(?=(\d{3})+(?!\d))/g, ",")
            : String((parseFloat(metric.value.replace(/K/, '')) + Math.random() * 0.5).toFixed(1)) + "K",
          change: `+${Math.floor(Math.random() * 10)}`,
          trend: "up" as const
        })))
      }, 2000)

      return () => clearInterval(interval)
    }
  }, [isDemoRunning])

  useEffect(() => {
    if (isDemoRunning) {
      const stepInterval = setInterval(() => {
        setCurrentStep(prev => (prev + 1) % demoSteps.length)
      }, 4000)

      return () => clearInterval(stepInterval)
    }
  }, [isDemoRunning, demoSteps.length])

  const startDemo = () => {
    setIsDemoRunning(true)
    setCurrentStep(0)
  }

  const stopDemo = () => {
    setIsDemoRunning(false)
  }

  const resetDemo = () => {
    setIsDemoRunning(false)
    setCurrentStep(0)
    setMetrics([
      { label: "Active Users", value: "12", change: "+2", trend: "up" },
      { label: "Contracts Created", value: "47", change: "+5", trend: "up" },
      { label: "Real-time Syncs", value: "1,284", change: "+127", trend: "up" },
      { label: "API Calls", value: "8.2K", change: "+892", trend: "up" }
    ])
  }

  return (
    <section className="py-20 relative overflow-hidden">
      {/* Background Effects */}
      <div className="absolute inset-0" />
      <div className="absolute top-1/3 left-1/4 w-96 h-96 bg-primary/10 rounded-full filter blur-3xl" />
      <div className="absolute bottom-1/3 right-1/4 w-96 h-96 bg-primary/10 rounded-full filter blur-3xl" />

      <div className="relative z-10 max-w-7xl mx-auto px-5">
        {/* Header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary/10 border border-primary/30 rounded-full text-sm font-medium text-primary backdrop-blur-sm mb-6">
            <Activity className="w-4 h-4" />
            {isDemoRunning ? "Demo Running Live" : "Interactive Demo Available"}
          </div>

          <h2 className="text-4xl md:text-6xl font-bold text-foreground mb-6 leading-tight">
            See It In Action
            <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-tr from-primary/70 to-primary">
              Real-Time Integration
            </span>
          </h2>

          <p className="text-xl text-muted-foreground max-w-3xl mx-auto leading-relaxed mb-8">
            Watch the power of Convex + OpenAI + Firecrawl working together in our live demo environment
          </p>

          {/* Demo Controls */}
          <div className="flex justify-center gap-4">
            {!isDemoRunning ? (
              <Link href={'https://www.youtube.com/watch?v=LL6dfPs0COo'} target="_blank">
                <Button
                  onClick={startDemo}
                  className="bg-gradient-to-r from-primary to-primary-dark hover:from-primary-dark hover:to-primary text-primary-foreground px-8 py-3 rounded-full font-semibold shadow-lg transition-all duration-300 "
                >
                  <Play className="w-5 h-5 mr-2" />
                  Start Live Demo
                </Button>
              </Link>
            ) : (
              <Button
                onClick={stopDemo}
                className="bg-destructive hover:bg-destructive/80 text-destructive-foreground px-8 py-3 rounded-full font-semibold shadow-lg transition-all duration-300"
              >
                <Pause className="w-5 h-5 mr-2" />
                Pause Demo
              </Button>
            )}

            <Button
              onClick={resetDemo}
              variant="outline"
              className="border-border text-foreground hover:bg-card px-8 py-3 rounded-full font-semibold transition-all duration-300"
            >
              <RotateCcw className="w-5 h-5 mr-2" />
              Reset
            </Button>

            <Link href="/convex-test">
              <Button
                variant="outline"
                className="border-primary/50 text-primary hover:bg-primary/10 px-8 py-3 rounded-full font-semibold transition-all duration-300"
              >
                <Eye className="w-5 h-5 mr-2" />
                Full Demo
              </Button>
            </Link>
          </div>
        </div>

        {/* Live Metrics Dashboard */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
          {metrics.map((metric, index) => (
            <Card key={index} className="bg-card/50 border-border backdrop-blur-sm p-6">
              <div className="flex justify-between items-start mb-2">
                <span className="text-sm text-muted-foreground">{metric.label}</span>
                {isDemoRunning && (
                  <div className="w-2 h-2 bg-primary rounded-full animate-pulse" />
                )}
              </div>
              <div className="text-2xl font-bold text-foreground mb-1">{metric.value}</div>
              <div className={`text-sm ${
                metric.trend === "up" ? "text-primary" :
                metric.trend === "down" ? "text-destructive" : "text-muted-foreground"
              }`}>
                {metric.change}
              </div>
            </Card>
          ))}
        </div>

        {/* Demo Steps Visualization */}
        <div className="bg-card/50 border border-border rounded-2xl p-8 backdrop-blur-sm">
          <h3 className="text-2xl font-semibold text-foreground mb-8 text-center">
            Integration Pipeline
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
            {demoSteps.map((step, index) => {
              const Icon = step.icon
              const isActive = isDemoRunning && index === currentStep

              return (
                <div
                  key={index}
                  className={`relative text-center transition-all duration-500 ${
                    isActive ? "scale-105" : "scale-100"
                  }`}
                >
                  {/* Connection Line */}
                  {index < demoSteps.length - 1 && (
                    <div className={`absolute top-8 left-full -translate-x-[calc(50%+8px)] w-full h-0.5 bg-gradient-to-r ${
                      isActive ? "from-transparent to-primary" : "from-transparent to-border"
                    } transition-all duration-500`} />
                  )}

                  {/* Step Circle */}
                  <div className={`relative mb-4 mx-auto w-16 h-16 rounded-full flex items-center justify-center transition-all duration-500 ${
                    isActive
                      ? "bg-gradient-to-r from-primary to-primary-dark shadow-lg shadow-primary/50"
                      : "bg-card border-border"
                  }`}>
                    <Icon className={`w-8 h-8 ${isActive ? "text-foreground" : "text-muted-foreground"}`} />
                    {isActive && (
                      <div className="absolute inset-0 rounded-full bg-primary/20 animate-ping" />
                    )}
                  </div>

                  {/* Step Content */}
                  <div className="space-y-2">
                    <h4 className={`font-semibold ${isActive ? "text-foreground" : "text-muted-foreground"}`}>
                      {step.title}
                    </h4>
                    <p className="text-sm text-muted-foreground leading-relaxed">
                      {step.description}
                    </p>
                    <Badge variant="secondary" className="bg-card text-muted-foreground border-border">
                      {step.tech}
                    </Badge>
                  </div>
                </div>
              )
            })}
          </div>

          {/* Current Step Description */}
          {isDemoRunning && (
            <div className="mt-8 p-4 bg-primary/10 border border-primary/30 rounded-lg">
              <div className="flex items-center gap-3">
                <div className="w-3 h-3 bg-primary rounded-full animate-pulse" />
                <span className="text-primary font-medium">
                  Currently executing: {demoSteps[currentStep].title}
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Tech Stack Integration Details */}
        <div className="mt-12 text-center">
          <div className="inline-flex items-center gap-6 px-6 py-3 bg-card/50 border border-border rounded-full backdrop-blur-sm">
            <div className="flex items-center gap-2">
              <Database className="w-5 h-5 text-yellow-300" />
              <span className="text-sm text-foreground">Convex Real-time</span>
            </div>
            <span className="text-muted-foreground">+</span>
            <div className="flex items-center gap-2">
              <Bot className="w-5 h-5 text-accent-foreground" />
              <span className="text-sm text-foreground">OpenAI GPT-5</span>
            </div>
            <span className="text-muted-foreground">+</span>
            <div className="flex items-center gap-2">
              <Activity className="w-5 h-5 text-orange-400" />
              <span className="text-sm text-foreground">Firecrawl Data</span>
            </div>
            <span className="text-muted-foreground">=</span>
            <div className="flex items-center gap-2">
              <Zap className="w-5 h-5 text-primary" />
              <span className="text-sm text-foreground font-medium">Flowzmith Live</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

export default LiveDemoSection