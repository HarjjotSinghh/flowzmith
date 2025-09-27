"use client"

import { Plus, FileText, Zap, Settings, Play, Upload, FolderOpen, Code, BarChart3, MessageSquare } from "lucide-react"
import { Button } from "@/components/ui/button"
import Link from "next/link"

interface ActionCardProps {
  title: string
  description: string
  icon: React.ReactNode
  href: string
  variant?: "default" | "secondary"
}

function ActionCard({ title, description, icon, href, variant = "default" }: ActionCardProps) {
  const baseClasses = "w-full p-4 rounded-lg border transition-all duration-200 hover:scale-105 cursor-pointer"
  const variantClasses = variant === "default" 
    ? "bg-card/50 border-border hover:bg-card/70 hover:border-primary/50"
    : "bg-primary/10 border-primary/20 hover:bg-primary/20 hover:border-primary/40"
  
  return (
    <Link href={href}>
      <div className={`${baseClasses} ${variantClasses}`}>
        <div className="flex items-start space-x-3">
          <div className="p-2 bg-primary/10 rounded-lg">
            {icon}
          </div>
          <div className="flex-1 min-w-0">
            <h3 className="font-medium text-foreground mb-1">{title}</h3>
            <p className="text-sm text-muted-foreground">{description}</p>
          </div>
        </div>
      </div>
    </Link>
  )
}

export function QuickActions() {
  const actions = [
    {
      title: "New Contract",
      description: "Generate a smart contract from scratch",
      icon: <Plus className="h-5 w-5 text-primary" />,
      href: "/chat",
      variant: "secondary" as const
    },
    {
      title: "Import Contract",
      description: "Upload and analyze existing code",
      icon: <Upload className="h-5 w-5 text-primary" />,
      href: "/chat"
    },
    {
      title: "Deploy Contract",
      description: "Deploy to Flow testnet or mainnet",
      icon: <Play className="h-5 w-5 text-primary" />,
      href: "/chat"
    },
    {
      title: "AI Optimization",
      description: "Optimize existing contracts with AI",
      icon: <Zap className="h-5 w-5 text-primary" />,
      href: "/chat"
    }
  ]

  const navigationActions = [
    {
      title: "Chat with AI",
      description: "Start a conversation with AI assistant",
      icon: <MessageSquare className="h-5 w-5 text-primary" />,
      href: "/chat"
    },
    {
      title: "Projects",
      description: "Manage your smart contract projects",
      icon: <FolderOpen className="h-5 w-5 text-primary" />,
      href: "/dashboard/projects"
    },
    {
      title: "Contracts",
      description: "View and manage smart contracts",
      icon: <Code className="h-5 w-5 text-primary" />,
      href: "/dashboard/contracts"
    },
    {
      title: "Analytics",
      description: "Track performance and usage metrics",
      icon: <BarChart3 className="h-5 w-5 text-primary" />,
      href: "/dashboard/analytics"
    }
  ]

  return (
    <div className="bg-card/50 backdrop-blur-sm rounded-xl border border-border p-6">
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-foreground mb-1">Quick Actions</h2>
        <p className="text-muted-foreground">Start building with AI assistance</p>
      </div>
      
      <div className="space-y-3">
        {actions.map((action, index) => (
          <ActionCard key={index} {...action} />
        ))}
      </div>
      
      <div className="mt-6 pt-4 border-t border-border">
        <h3 className="text-sm font-medium text-foreground mb-3">Navigate</h3>
        <div className="space-y-2">
          {navigationActions.map((action, index) => (
            <Link key={index} href={action.href}>
              <div className="flex items-center space-x-3 p-2 rounded-lg hover:bg-muted/50 transition-colors cursor-pointer">
                <div className="p-1 bg-primary/10 rounded">
                  {action.icon}
                </div>
                <div>
                  <p className="text-sm font-medium text-foreground">{action.title}</p>
                  <p className="text-xs text-muted-foreground">{action.description}</p>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </div>
      
      <div className="mt-6 pt-4 border-t border-border">
        <Link href="/chat">
          <Button className="w-full" size="sm">
            <MessageSquare className="h-4 w-4 mr-2" />
            Chat with AI Assistant
          </Button>
        </Link>
      </div>
    </div>
  )
}
