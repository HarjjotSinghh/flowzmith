"use client"

import { useState } from "react"
import { useSession } from "next-auth/react"
import { useRouter } from "next/navigation"
import { AnimatedSection } from "@/components/animated-section"
import { DashboardHeader } from "@/components/dashboard/dashboard-header"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { 
  Plus, 
  FolderOpen, 
  GitBranch, 
  Calendar, 
  Users, 
  Code, 
  ExternalLink,
  MoreHorizontal,
  Star,
  Clock
} from "lucide-react"

interface Project {
  id: string
  name: string
  description: string
  status: "active" | "completed" | "archived"
  contracts: number
  lastModified: string
  team: string[]
  tags: string[]
}

export default function ProjectsPage() {
  const { data: session } = useSession()
  const router = useRouter()
  const [filter, setFilter] = useState<"all" | "active" | "completed" | "archived">("all")

  const projects: Project[] = [
    {
      id: "1",
      name: "NFT Marketplace",
      description: "A comprehensive NFT marketplace built on Flow blockchain with AI-powered features",
      status: "active",
      contracts: 5,
      lastModified: "2 hours ago",
      team: ["Alice", "Bob", "Charlie"],
      tags: ["NFT", "Marketplace", "Flow"]
    },
    {
      id: "2", 
      name: "DeFi Lending Protocol",
      description: "Decentralized lending platform with smart contract automation",
      status: "active",
      contracts: 8,
      lastModified: "1 day ago",
      team: ["David", "Eve"],
      tags: ["DeFi", "Lending", "Automation"]
    },
    {
      id: "3",
      name: "DAO Governance System",
      description: "Decentralized governance system with voting mechanisms",
      status: "completed",
      contracts: 3,
      lastModified: "1 week ago",
      team: ["Frank", "Grace"],
      tags: ["DAO", "Governance", "Voting"]
    },
    {
      id: "4",
      name: "Token Launch Platform",
      description: "Platform for launching new tokens with automated liquidity",
      status: "archived",
      contracts: 2,
      lastModified: "2 weeks ago",
      team: ["Henry"],
      tags: ["Token", "Launch", "Liquidity"]
    }
  ]

  const filteredProjects = projects.filter(project => 
    filter === "all" || project.status === filter
  )

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active": return "text-primary bg-primary/10"
      case "completed": return "text-foreground/80 bg-muted/60"
      case "archived": return "text-foreground/80 bg-muted/40"
      default: return "text-foreground/80 bg-muted/40"
    }
  }

  return (
    <div className="min-h-screen bg-background font-mono text-foreground border-x-2 border-foreground mx-auto max-w-[1440px]">
      <DashboardHeader user={session?.user} />
      
      <div className="px-6 py-8">
        <AnimatedSection delay={0.1}>
          <div className="flex items-center justify-between mb-8 border-b-2 border-foreground pb-6">
            <div>
              <h1 className="text-4xl md:text-6xl font-black tracking-tighter uppercase leading-none">PROJECTS.</h1>
              <p className="text-lg font-bold text-foreground/80 mt-2 border-l-4 border-accent pl-4">
                MANAGE YOUR SMART CONTRACT PROJECTS AND DEVELOPMENT WORKFLOWS V2.0
              </p>
            </div>
            <Button className="flex items-center gap-2 h-12 px-6 font-black text-xs">
              <Plus className="h-5 w-5" />
              NEW PROJECT
            </Button>
          </div>
        </AnimatedSection>

        {/* Filter Tabs */}
        <AnimatedSection delay={0.2}>
          <div className="flex flex-wrap gap-2 mb-8">
            {[
              { key: "all", label: "ALL PROJECTS", count: projects.length },
              { key: "active", label: "ACTIVE", count: projects.filter(p => p.status === "active").length },
              { key: "completed", label: "COMPLETED", count: projects.filter(p => p.status === "completed").length },
              { key: "archived", label: "ARCHIVED", count: projects.filter(p => p.status === "archived").length }
            ].map((tab) => (
              <button
                key={tab.key}
                onClick={() => setFilter(tab.key as any)}
                className={`px-4 py-2 border-2 border-foreground text-[10px] font-black tracking-widest transition-all ${
                  filter === tab.key
                    ? "bg-foreground text-background"
                  : "bg-background text-foreground hover:bg-muted"
                }`}
              >
                {tab.label} ({tab.count})
              </button>
            ))}
          </div>
        </AnimatedSection>

        {/* Projects Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
          {filteredProjects.map((project, index) => (
            <AnimatedSection key={project.id} delay={0.1 * (index + 1)}>
              <Card className="hover:translate-y-[-4px] transition-all duration-200 cursor-default group relative overflow-hidden">
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-black border border-foreground group-hover:bg-accent transition-colors">
                        <FolderOpen className="h-5 w-5 text-accent group-hover:text-black" />
                      </div>
                      <div>
                        <CardTitle className="text-xl font-black tracking-tighter uppercase">{project.name}</CardTitle>
                        <div className={`inline-flex items-center px-2 py-0.5 text-[10px] font-black uppercase mt-1 ${getStatusColor(project.status)}`}>
                          {project.status}
                        </div>
                      </div>
                    </div>
                  </div>
                </CardHeader>
                
                <CardContent className="space-y-4">
                  <p className="text-foreground/80 text-xs font-bold uppercase leading-snug line-clamp-2">
                    {project.description}
                  </p>
                  
                  <div className="flex items-center gap-4 text-[10px] font-black uppercase">
                    <div className="flex items-center gap-1">
                      <Code className="h-4 w-4 text-accent" />
                      {project.contracts} CONTRACTS
                    </div>
                    <div className="flex items-center gap-1">
                      <Users className="h-4 w-4 text-accent" />
                      {project.team.length} MEMBERS
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-1 text-[10px] font-bold text-foreground/50 uppercase">
                    <Clock className="h-3 w-3" />
                    UPDATED {project.lastModified}
                  </div>
                  
                  <div className="flex flex-wrap gap-1">
                    {project.tags.map((tag) => (
                      <span key={tag} className="px-2 py-0.5 bg-black text-white text-[9px] font-black uppercase border border-foreground/20 group-hover:border-accent/50 transition-colors">
                        {tag}
                      </span>
                    ))}
                  </div>
                  
                  <div className="flex items-center justify-between pt-4 border-t border-foreground/10">
                    <div className="flex -space-x-2">
                      {project.team.slice(0, 3).map((member, idx) => (
                        <div key={idx} className="w-8 h-8 bg-black border-2 border-foreground flex items-center justify-center text-[10px] font-black text-accent group-hover:border-accent transition-colors">
                          {member[0]}
                        </div>
                      ))}
                      {project.team.length > 3 && (
                        <div className="w-8 h-8 bg-muted border-2 border-foreground flex items-center justify-center text-[10px] font-black">
                          +{project.team.length - 3}
                        </div>
                      )}
                    </div>
                    <Button variant="outline" size="icon" className="h-10 w-10 border-2">
                      <ExternalLink className="h-4 w-4" />
                    </Button>
                  </div>
                </CardContent>
                <div className="absolute bottom-0 right-0 w-2 h-2 bg-foreground group-hover:bg-accent transition-colors" />
              </Card>
            </AnimatedSection>
          ))}
        </div>

        {/* Empty State */}
        {filteredProjects.length === 0 && (
          <AnimatedSection delay={0.3}>
            <div className="text-center py-12">
              <FolderOpen className="h-12 w-12 text-foreground/80 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-foreground mb-2">No projects found</h3>
              <p className="text-foreground/80 mb-4">
                {filter === "all" 
                  ? "Get started by creating your first project"
                  : `No ${filter} projects found`
                }
              </p>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Create Project
              </Button>
            </div>
          </AnimatedSection>
        )}
      </div>
    </div>
  )
}
