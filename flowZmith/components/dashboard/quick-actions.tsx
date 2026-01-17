"use client"

import { Plus, FileText, Zap, Settings, Play, Upload, FolderOpen, Code, BarChart3, MessageSquare, ArrowRight } from "lucide-react"
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
  return (
    <Link href={href}>
      <div className={`w-full p-4 border-2 border-foreground transition-all duration-200 cursor-pointer group flex items-start space-x-4 ${
        variant === "default" 
          ? "bg-background hover:bg-accent" 
          : "bg-accent/5 hover:bg-accent"
      }`}>
        <div className="p-2 bg-black border border-foreground flex-shrink-0 group-hover:bg-black group-hover:border-black transition-colors">
          <div className="text-accent group-hover:text-accent group-hover:scale-110 transition-transform">
            {icon}
          </div>
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="font-black text-xs uppercase tracking-tighter group-hover:text-black">{`[ ${title} ]`}</h3>
          <p className="text-[10px] font-bold text-foreground/60 uppercase leading-snug group-hover:text-black/80">{description}</p>
        </div>
        <ArrowRight className="h-4 w-4 self-center opacity-0 group-hover:opacity-100 group-hover:translate-x-1 transition-all group-hover:text-black" />
      </div>
    </Link>
  )
}

export function QuickActions() {
  const actions = [
    {
      title: "NEW CONTRACT",
      description: "GENERATE A SMART CONTRACT FROM SCRATCH",
      icon: <Plus className="h-5 w-5" />,
      href: "/chat",
      variant: "secondary" as const
    },
    {
      title: "IMPORT ASSETS",
      description: "UPLOAD AND ANALYZE EXISTING CADENCE CODE",
      icon: <Upload className="h-5 w-5" />,
      href: "/chat"
    },
    {
      title: "DEPLOY CORE",
      description: "DEPLOY TO FLOW TESTNET OR MAINNET NODES",
      icon: <Play className="h-5 w-5" />,
      href: "/chat"
    },
    {
      title: "AI OPTIMIZE",
      description: "REFACTOR EXISTING CONTRACTS WITH AI CORE V4",
      icon: <Zap className="h-5 w-5" />,
      href: "/chat"
    }
  ]

  const navigationActions = [
    {
      title: "AI COMMAND CHAT",
      description: "CONVERSE WITH THE CORE AI AGENT",
      icon: <MessageSquare className="h-4 w-4" />,
      href: "/chat"
    },
    {
      title: "PROJECT REPOSITORY",
      description: "MANAGE YOUR SMART CONTRACT WORKSPACES",
      icon: <FolderOpen className="h-4 w-4" />,
      href: "/dashboard/projects"
    },
    {
      title: "CONTRACT REGISTRY",
      description: "VIEW AND MANAGE COMPILED CONTRACTS",
      icon: <Code className="h-4 w-4" />,
      href: "/dashboard/contracts"
    },
    {
      title: "SYSTEM ANALYTICS",
      description: "TRACK PERFORMANCE AND USAGE METRICS",
      icon: <BarChart3 className="h-4 w-4" />,
      href: "/dashboard/analytics"
    }
  ]

  return (
    <div className="space-y-6">
      <div className="space-y-2">
        {actions.map((action, index) => (
          <ActionCard key={index} {...action} />
        ))}
      </div>
      
      <div className="pt-6 border-t-2 border-foreground/10">
        <div className="text-[10px] font-black uppercase tracking-widest opacity-50 mb-4">SYSTEM NAVIGATION</div>
        <div className="grid grid-cols-1 gap-2">
          {navigationActions.map((action, index) => (
            <Link key={index} href={action.href}>
              <div className="flex items-center space-x-3 p-3 border-2 border-transparent hover:border-foreground hover:bg-muted/10 transition-all cursor-pointer group">
                <div className="p-2 bg-black border border-foreground group-hover:bg-accent transition-colors">
                  <div className="text-accent group-hover:text-black">
                    {action.icon}
                  </div>
                </div>
                <div>
                  <p className="text-[10px] font-black uppercase tracking-tighter">{action.title}</p>
                  <p className="text-[9px] font-bold text-foreground/50 uppercase">{action.description}</p>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </div>
      
      <div className="pt-4">
        <Link href="/chat">
          <Button variant="terminal" className="w-full h-12 text-xs font-black">
            <MessageSquare className="h-4 w-4 mr-2" />
            INITIALIZE AI AGENT CHAT
          </Button>
        </Link>
      </div>
    </div>
  )
}