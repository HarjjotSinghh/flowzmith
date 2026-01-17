"use client"

import { useState } from "react"
import { useSession } from "next-auth/react"
import { AnimatedSection } from "@/components/animated-section"
import { DashboardHeader } from "@/components/dashboard/dashboard-header"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { 
  Plus, 
  FileText, 
  Code, 
  Download, 
  Copy, 
  Eye, 
  Edit,
  Trash2,
  CheckCircle,
  AlertTriangle,
  Clock,
  GitBranch,
  Zap,
  Shield,
  MoreHorizontal
} from "lucide-react"

interface Contract {
  id: string
  name: string
  type: "NFT" | "Token" | "Marketplace" | "DAO" | "DeFi"
  status: "draft" | "deployed" | "verified" | "archived"
  language: "Cadence"
  size: string
  lastModified: string
  gasUsed: string
  securityScore: number
  project: string
  description: string
}

export default function ContractsPage() {
  const { data: session } = useSession()
  const [filter, setFilter] = useState<"all" | "draft" | "deployed" | "verified" | "archived">("all")
  const [typeFilter, setTypeFilter] = useState<string>("all")

  const contracts: Contract[] = [
    {
      id: "1",
      name: "NFTCollection",
      type: "NFT",
      status: "deployed",
      language: "Cadence",
      size: "2.3 KB",
      lastModified: "1 hour ago",
      gasUsed: "0.001 FLOW",
      securityScore: 95,
      project: "NFT Marketplace",
      description: "ERC-721 compatible NFT collection contract with royalty support"
    },
    {
      id: "2",
      name: "TokenContract",
      type: "Token",
      status: "verified",
      language: "Cadence",
      size: "1.8 KB",
      lastModified: "3 hours ago",
      gasUsed: "0.0008 FLOW",
      securityScore: 98,
      project: "DeFi Lending Protocol",
      description: "Fungible token contract with minting and burning capabilities"
    },
    {
      id: "3",
      name: "MarketplaceCore",
      type: "Marketplace",
      status: "draft",
      language: "Cadence",
      size: "4.1 KB",
      lastModified: "2 days ago",
      gasUsed: "0.002 FLOW",
      securityScore: 87,
      project: "NFT Marketplace",
      description: "Core marketplace functionality for buying and selling NFTs"
    },
    {
      id: "4",
      name: "GovernanceToken",
      type: "DAO",
      status: "deployed",
      language: "Cadence",
      size: "2.7 KB",
      lastModified: "1 week ago",
      gasUsed: "0.0012 FLOW",
      securityScore: 92,
      project: "DAO Governance System",
      description: "Governance token with voting and delegation features"
    },
    {
      id: "5",
      name: "LendingPool",
      type: "DeFi",
      status: "verified",
      language: "Cadence",
      size: "3.5 KB",
      lastModified: "3 days ago",
      gasUsed: "0.0015 FLOW",
      securityScore: 96,
      project: "DeFi Lending Protocol",
      description: "Lending pool contract with automated interest calculations"
    }
  ]

  const filteredContracts = contracts.filter(contract => {
    const statusMatch = filter === "all" || contract.status === filter
    const typeMatch = typeFilter === "all" || contract.type === typeFilter
    return statusMatch && typeMatch
  })

  const getStatusColor = (status: string) => {
    switch (status) {
      case "deployed": return "text-primary bg-primary/10"
      case "verified": return "text-primary bg-primary/10"
      case "draft": return "text-foreground/80 bg-muted/60"
      case "archived": return "text-foreground/80 bg-muted/40"
      default: return "text-foreground/80 bg-muted/40"
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "deployed": return <CheckCircle className="h-4 w-4" />
      case "verified": return <Shield className="h-4 w-4" />
      case "draft": return <Clock className="h-4 w-4" />
      case "archived": return <AlertTriangle className="h-4 w-4" />
      default: return <Clock className="h-4 w-4" />
    }
  }

  const getTypeIcon = (type: string) => {
    switch (type) {
      case "NFT": return <FileText className="h-4 w-4" />
      case "Token": return <Zap className="h-4 w-4" />
      case "Marketplace": return <GitBranch className="h-4 w-4" />
      case "DAO": return <Shield className="h-4 w-4" />
      case "DeFi": return <Code className="h-4 w-4" />
      default: return <FileText className="h-4 w-4" />
    }
  }

  return (
    <div className="min-h-screen bg-background font-mono text-foreground border-x-2 border-foreground mx-auto max-w-[1440px]">
      <DashboardHeader user={session?.user} />
      
      <div className="px-6 py-8">
        <AnimatedSection delay={0.1}>
          <div className="flex items-center justify-between mb-8 border-b-2 border-foreground pb-6">
            <div>
              <h1 className="text-4xl md:text-6xl font-black tracking-tighter uppercase leading-none">SMART CONTRACTS.</h1>
              <p className="text-lg font-bold text-foreground/80 mt-2 border-l-4 border-accent pl-4">
                MANAGE AND DEPLOY YOUR CADENCE SMART CONTRACTS ON FLOW V1.2
              </p>
            </div>
            <Button className="flex items-center gap-2 h-12 px-6 font-black text-xs">
              <Plus className="h-5 w-5" />
              NEW CONTRACT
            </Button>
          </div>
        </AnimatedSection>

        {/* Filters */}
        <AnimatedSection delay={0.2}>
          <div className="flex flex-wrap gap-4 mb-8">
            {/* Status Filter */}
            <div className="flex flex-wrap gap-2">
              {[
                { key: "all", label: "ALL" },
                { key: "draft", label: "DRAFT" },
                { key: "deployed", label: "DEPLOYED" },
                { key: "verified", label: "VERIFIED" },
                { key: "archived", label: "ARCHIVED" }
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
                  {tab.label}
                </button>
              ))}
            </div>

            {/* Type Filter */}
            <div className="flex flex-wrap gap-2">
              {[
                { key: "all", label: "ALL TYPES" },
                { key: "NFT", label: "NFT" },
                { key: "Token", label: "TOKEN" },
                { key: "Marketplace", label: "MARKETPLACE" },
                { key: "DAO", label: "DAO" },
                { key: "DeFi", label: "DEFI" }
              ].map((tab) => (
                <button
                  key={tab.key}
                  onClick={() => setTypeFilter(tab.key)}
                  className={`px-4 py-2 border-2 border-foreground text-[10px] font-black tracking-widest transition-all ${
                    typeFilter === tab.key
                      ? "bg-accent text-black"
                    : "bg-background text-foreground hover:bg-muted"
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </div>
          </div>
        </AnimatedSection>

        {/* Contracts Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
          {filteredContracts.map((contract, index) => (
            <AnimatedSection key={contract.id} delay={0.1 * (index + 1)}>
              <Card className="hover:translate-y-[-4px] transition-all duration-200 cursor-default group relative overflow-hidden">
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-black border border-foreground group-hover:bg-accent transition-colors">
                        <div className="group-hover:text-black text-accent">
                          {getTypeIcon(contract.type)}
                        </div>
                      </div>
                      <div>
                        <CardTitle className="text-xl font-black tracking-tighter uppercase">{contract.name}</CardTitle>
                        <div className="flex items-center gap-2 mt-1">
                          <div className={`inline-flex items-center gap-1 px-2 py-0.5 text-[10px] font-black uppercase ${getStatusColor(contract.status)}`}>
                            {getStatusIcon(contract.status)}
                            {contract.status}
                          </div>
                          <span className="text-[10px] font-bold text-foreground/50 uppercase">{contract.language}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </CardHeader>
                
                <CardContent className="space-y-4">
                  <p className="text-foreground/80 text-xs font-bold uppercase leading-snug line-clamp-2">
                    {contract.description}
                  </p>
                  
                  <div className="grid grid-cols-2 gap-4 text-[10px] font-black uppercase">
                    <div>
                      <span className="opacity-50">SIZE:</span>
                      <span className="ml-1">{contract.size}</span>
                    </div>
                    <div>
                      <span className="opacity-50">GAS:</span>
                      <span className="ml-1">{contract.gasUsed}</span>
                    </div>
                    <div>
                      <span className="opacity-50">SECURITY:</span>
                      <span className="ml-1 text-accent">{contract.securityScore}%</span>
                    </div>
                    <div>
                      <span className="opacity-50">PROJECT:</span>
                      <span className="ml-1">{contract.project}</span>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-1 text-[10px] font-bold text-foreground/50 uppercase">
                    <Clock className="h-3 w-3" />
                    SYNCED {contract.lastModified}
                  </div>
                  
                  <div className="flex items-center justify-between pt-4 border-t border-foreground/10">
                    <div className="flex gap-1">
                      <Button variant="outline" size="icon" className="h-8 w-8 border-2">
                        <Eye className="h-4 w-4" />
                      </Button>
                      <Button variant="outline" size="icon" className="h-8 w-8 border-2">
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button variant="outline" size="icon" className="h-8 w-8 border-2">
                        <Download className="h-4 w-4" />
                      </Button>
                    </div>
                    <Button variant="outline" size="icon" className="h-8 w-8 border-2 hover:bg-red-500 hover:text-white transition-colors">
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </CardContent>
                <div className="absolute bottom-0 right-0 w-2 h-2 bg-foreground group-hover:bg-accent transition-colors" />
              </Card>
            </AnimatedSection>
          ))}
        </div>

        {/* Empty State */}
        {filteredContracts.length === 0 && (
          <AnimatedSection delay={0.3}>
            <div className="text-center py-12">
              <FileText className="h-12 w-12 text-foreground/80 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-foreground mb-2">No contracts found</h3>
              <p className="text-foreground/80 mb-4">
                {filter === "all" 
                  ? "Get started by creating your first smart contract"
                  : `No ${filter} contracts found`
                }
              </p>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Create Contract
              </Button>
            </div>
          </AnimatedSection>
        )}
      </div>
    </div>
  )
}
