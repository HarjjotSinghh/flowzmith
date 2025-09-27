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
      case "active": return "text-green-500 bg-green-500/10"
      case "completed": return "text-blue-500 bg-blue-500/10"
      case "archived": return "text-gray-500 bg-gray-500/10"
      default: return "text-gray-500 bg-gray-500/10"
    }
  }

  return (
    <div className="min-h-screen bg-background">
      <DashboardHeader user={session?.user} />
      
      <div className="max-w-[1320px] mx-auto px-6 py-8">
        <AnimatedSection delay={0.1}>
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-3xl font-semibold text-foreground mb-2">Projects</h1>
              <p className="text-muted-foreground">
                Manage your smart contract projects and development workflows
              </p>
            </div>
            <Button className="flex items-center gap-2">
              <Plus className="h-4 w-4" />
              New Project
            </Button>
          </div>
        </AnimatedSection>

        {/* Filter Tabs */}
        <AnimatedSection delay={0.2}>
          <div className="flex space-x-1 mb-6">
            {[
              { key: "all", label: "All Projects", count: projects.length },
              { key: "active", label: "Active", count: projects.filter(p => p.status === "active").length },
              { key: "completed", label: "Completed", count: projects.filter(p => p.status === "completed").length },
              { key: "archived", label: "Archived", count: projects.filter(p => p.status === "archived").length }
            ].map((tab) => (
              <button
                key={tab.key}
                onClick={() => setFilter(tab.key as any)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  filter === tab.key
                    ? "bg-primary text-primary-foreground"
                    : "text-muted-foreground hover:text-foreground hover:bg-muted"
                }`}
              >
                {tab.label} ({tab.count})
              </button>
            ))}
          </div>
        </AnimatedSection>

        {/* Projects Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredProjects.map((project, index) => (
            <AnimatedSection key={project.id} delay={0.1 * (index + 1)}>
              <Card className="hover:shadow-lg transition-all duration-200 cursor-pointer group">
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-primary/10 rounded-lg">
                        <FolderOpen className="h-5 w-5 text-primary" />
                      </div>
                      <div>
                        <CardTitle className="text-lg">{project.name}</CardTitle>
                        <div className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(project.status)}`}>
                          {project.status}
                        </div>
                      </div>
                    </div>
                    <Button variant="ghost" size="icon" className="opacity-0 group-hover:opacity-100 transition-opacity">
                      <MoreHorizontal className="h-4 w-4" />
                    </Button>
                  </div>
                </CardHeader>
                
                <CardContent className="space-y-4">
                  <p className="text-muted-foreground text-sm line-clamp-2">
                    {project.description}
                  </p>
                  
                  <div className="flex items-center gap-4 text-sm text-muted-foreground">
                    <div className="flex items-center gap-1">
                      <Code className="h-4 w-4" />
                      {project.contracts} contracts
                    </div>
                    <div className="flex items-center gap-1">
                      <Users className="h-4 w-4" />
                      {project.team.length} members
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-1 text-sm text-muted-foreground">
                    <Clock className="h-4 w-4" />
                    Updated {project.lastModified}
                  </div>
                  
                  <div className="flex flex-wrap gap-1">
                    {project.tags.map((tag) => (
                      <span key={tag} className="px-2 py-1 bg-muted rounded text-xs">
                        {tag}
                      </span>
                    ))}
                  </div>
                  
                  <div className="flex items-center justify-between pt-2">
                    <div className="flex -space-x-2">
                      {project.team.slice(0, 3).map((member, idx) => (
                        <div key={idx} className="w-6 h-6 bg-primary rounded-full flex items-center justify-center text-xs font-medium text-primary-foreground border-2 border-background">
                          {member[0]}
                        </div>
                      ))}
                      {project.team.length > 3 && (
                        <div className="w-6 h-6 bg-muted rounded-full flex items-center justify-center text-xs border-2 border-background">
                          +{project.team.length - 3}
                        </div>
                      )}
                    </div>
                    <Button variant="ghost" size="sm" className="opacity-0 group-hover:opacity-100 transition-opacity">
                      <ExternalLink className="h-4 w-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </AnimatedSection>
          ))}
        </div>

        {/* Empty State */}
        {filteredProjects.length === 0 && (
          <AnimatedSection delay={0.3}>
            <div className="text-center py-12">
              <FolderOpen className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-medium text-foreground mb-2">No projects found</h3>
              <p className="text-muted-foreground mb-4">
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
