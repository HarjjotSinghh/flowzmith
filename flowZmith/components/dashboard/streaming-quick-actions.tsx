"use client"

import { useState } from "react"
import { Plus, FileText, Zap, Settings, Play, Upload, FolderOpen, Code, BarChart3, MessageSquare, Sparkles, Loader2, CheckCircle } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { useStreamingChat } from "@/hooks/use-streaming-chat"
import Link from "next/link"

interface StreamingActionCardProps {
  title: string
  description: string
  icon: React.ReactNode
  action: () => void
  variant?: "default" | "primary" | "secondary"
  isLoading?: boolean
  isCompleted?: boolean
  badge?: string
}

function StreamingActionCard({ 
  title, 
  description, 
  icon, 
  action, 
  variant = "default",
  isLoading = false,
  isCompleted = false,
  badge
}: StreamingActionCardProps) {
  const baseClasses = "group relative overflow-hidden rounded-xl border transition-all duration-300 cursor-pointer transform hover:scale-[1.02] hover:shadow-lg"
  
  const variantClasses = {
    default: "bg-gradient-to-br from-card/80 to-card/40 border-border/50 hover:border-primary/30 hover:shadow-primary/10",
    primary: "bg-gradient-to-br from-muted/40 to-muted/20 border-primary/20 hover:border-primary/40 hover:shadow-primary/20",
    secondary: "bg-gradient-to-br from-secondary/10 to-secondary/5 border-secondary/20 hover:border-secondary/40 hover:shadow-secondary/20"
  }
  
  return (
    <div 
      className={`${baseClasses} ${variantClasses[variant]}`}
      onClick={action}
    >
      {/* Animated background gradient */}
      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000" />
      
      <div className="relative p-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className={`p-3 rounded-xl transition-all duration-300 ${
              variant === "primary" ? "bg-primary/20 group-hover:bg-primary/30" :
              variant === "secondary" ? "bg-secondary/20 group-hover:bg-secondary/30" :
              "bg-muted/50 group-hover:bg-muted/70"
            }`}>
              {isLoading ? (
                <Loader2 className="h-6 w-6 animate-spin text-primary" />
              ) : isCompleted ? (
                <CheckCircle className="h-6 w-6 text-primary" />
              ) : (
                <div className="transition-transform duration-300 group-hover:scale-110">
                  {icon}
                </div>
              )}
            </div>
            {badge && (
              <Badge variant="secondary" className="text-xs font-medium">
                {badge}
              </Badge>
            )}
          </div>
        </div>
        
        <div className="space-y-2">
          <h3 className="font-semibold text-foreground group-hover:text-primary transition-colors duration-300">
            {title}
          </h3>
          <p className="text-sm text-foreground/80 leading-relaxed">
            {description}
          </p>
        </div>
        
        {/* Status indicator */}
        {(isLoading || isCompleted) && (
          <div className="mt-4 pt-3 border-t border-border/50">
            <div className="flex items-center space-x-2 text-xs">
              {isLoading && (
                <>
                  <div className="w-2 h-2 bg-primary rounded-full animate-pulse" />
                  <span className="text-primary font-medium">Generating...</span>
                </>
              )}
              {isCompleted && (
                <>
                  <div className="w-2 h-2 bg-primary rounded-full" />
                  <span className="text-primary font-medium">Completed</span>
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

interface NavigationCardProps {
  title: string
  description: string
  icon: React.ReactNode
  href: string
  count?: number
}

function NavigationCard({ title, description, icon, href, count }: NavigationCardProps) {
  return (
    <Link href={href}>
      <div className="group flex items-center space-x-4 p-4 rounded-xl bg-gradient-to-r from-muted/30 to-muted/10 border border-border/50 hover:border-primary/30 hover:bg-gradient-to-r hover:from-primary/5 hover:to-primary/2 transition-all duration-300 cursor-pointer">
        <div className="p-2 bg-primary/10 rounded-lg group-hover:bg-primary/20 transition-colors duration-300">
          {icon}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center space-x-2">
            <h4 className="font-medium text-foreground group-hover:text-primary transition-colors duration-300">
              {title}
            </h4>
            {count !== undefined && (
              <Badge variant="outline" className="text-xs">
                {count}
              </Badge>
            )}
          </div>
          <p className="text-sm text-foreground/80 mt-1">{description}</p>
        </div>
      </div>
    </Link>
  )
}

export function StreamingQuickActions() {
  const [loadingStates, setLoadingStates] = useState<Record<string, boolean>>({})
  const [completedStates, setCompletedStates] = useState<Record<string, boolean>>({})
  const { generateContract, generateWithContext, isLoading } = useStreamingChat()

  const handleStreamingAction = async (actionId: string, prompt: string, type: 'contract' | 'context') => {
    setLoadingStates(prev => ({ ...prev, [actionId]: true }))
    setCompletedStates(prev => ({ ...prev, [actionId]: false }))

    try {
      if (type === 'contract') {
        await generateContract(prompt)
      } else {
        await generateWithContext({ prompt, context: 'Generate optimized smart contract' })
      }
      
      setCompletedStates(prev => ({ ...prev, [actionId]: true }))
      setTimeout(() => {
        setCompletedStates(prev => ({ ...prev, [actionId]: false }))
      }, 3000)
    } catch (error) {
      console.error('Streaming action failed:', error)
    } finally {
      setLoadingStates(prev => ({ ...prev, [actionId]: false }))
    }
  }

  const streamingActions = [
    {
      id: "new-contract",
      title: "Generate Smart Contract",
      description: "Create a new contract with AI assistance and real-time streaming",
      icon: <Sparkles className="h-6 w-6 text-primary" />,
      action: () => handleStreamingAction("new-contract", "Generate a comprehensive NFT smart contract for Flow blockchain", "contract"),
      variant: "primary" as const,
      badge: "AI Powered"
    },
    {
      id: "optimize-contract",
      title: "AI Contract Optimization",
      description: "Optimize existing contracts with advanced AI analysis",
      icon: <Zap className="h-6 w-6 text-secondary" />,
      action: () => handleStreamingAction("optimize-contract", "Optimize smart contract for gas efficiency and security", "context"),
      variant: "secondary" as const,
      badge: "Beta"
    },
    {
      id: "security-audit",
      title: "Security Analysis",
      description: "Perform comprehensive security audit with real-time feedback",
      icon: <Settings className="h-6 w-6 text-primary" />,
      action: () => handleStreamingAction("security-audit", "Perform security audit and vulnerability analysis", "context"),
      variant: "default" as const,
      badge: "New"
    }
  ]

  const navigationItems = [
    {
      title: "AI Chat Assistant",
      description: "Interactive contract development",
      icon: <MessageSquare className="h-5 w-5 text-primary" />,
      href: "/chat",
      count: 12
    },
    {
      title: "Project Management",
      description: "Organize your smart contracts",
      icon: <FolderOpen className="h-5 w-5 text-primary" />,
      href: "/dashboard/projects",
      count: 8
    },
    {
      title: "Contract Library",
      description: "Browse deployed contracts",
      icon: <Code className="h-5 w-5 text-primary" />,
      href: "/dashboard/contracts",
      count: 24
    },
    {
      title: "Analytics Dashboard",
      description: "Performance insights & metrics",
      icon: <BarChart3 className="h-5 w-5 text-primary" />,
      href: "/dashboard/analytics"
    }
  ]

  return (
    <Card className="bg-gradient-to-br from-card/80 to-card/40 border-border/50 backdrop-blur-sm">
      <CardHeader className="pb-4">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-primary/10 rounded-lg">
            <Sparkles className="h-5 w-5 text-primary" />
          </div>
          <div>
            <CardTitle className="text-xl font-semibold bg-gradient-to-r from-foreground to-foreground/70 bg-clip-text text-transparent">
              AI-Powered Actions
            </CardTitle>
            <p className="text-sm text-foreground/80 mt-1">
              Generate and optimize contracts with streaming AI
            </p>
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-6">
        {/* Streaming Actions Grid */}
        <div className="grid grid-cols-1 gap-4">
          {streamingActions.map((action) => (
            <StreamingActionCard
              key={action.id}
              title={action.title}
              description={action.description}
              icon={action.icon}
              action={action.action}
              variant={action.variant}
              isLoading={loadingStates[action.id]}
              isCompleted={completedStates[action.id]}
              badge={action.badge}
            />
          ))}
        </div>
        
        {/* Navigation Section */}
        <div className="pt-4 border-t border-border/50">
          <h3 className="text-sm font-semibold text-foreground mb-4 flex items-center space-x-2">
            <FolderOpen className="h-4 w-4" />
            <span>Quick Navigation</span>
          </h3>
          <div className="space-y-3">
            {navigationItems.map((item, index) => (
              <NavigationCard key={index} {...item} />
            ))}
          </div>
        </div>
        
        {/* Primary CTA */}
        <div className="pt-4 border-t border-border/50">
          <Link href="/chat">
            <Button 
              className="w-full bg-gradient-to-r from-primary to-primary/80 hover:from-primary/90 hover:to-primary/70 text-primary-foreground shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-[1.02]" 
              size="lg"
            >
              <MessageSquare className="h-5 w-5 mr-2" />
              Start AI Conversation
              <Sparkles className="h-4 w-4 ml-2" />
            </Button>
          </Link>
        </div>
      </CardContent>
    </Card>
  )
}
