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
  Shield
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
      case "deployed": return "text-green-500 bg-green-500/10"
      case "verified": return "text-blue-500 bg-blue-500/10"
      case "draft": return "text-yellow-500 bg-yellow-500/10"
      case "archived": return "text-gray-500 bg-gray-500/10"
      default: return "text-gray-500 bg-gray-500/10"
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
    <div className="min-h-screen bg-background">
      <DashboardHeader user={session?.user} />
      
      <div className="max-w-[1320px] mx-auto px-6 py-8">
        <AnimatedSection delay={0.1}>
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-3xl font-semibold text-foreground mb-2">Smart Contracts</h1>
              <p className="text-muted-foreground">
                Manage and deploy your Cadence smart contracts on Flow blockchain
              </p>
            </div>
            <Button className="flex items-center gap-2">
              <Plus className="h-4 w-4" />
              New Contract
            </Button>
          </div>
        </AnimatedSection>

        {/* Filters */}
        <AnimatedSection delay={0.2}>
          <div className="flex flex-wrap gap-4 mb-6">
            {/* Status Filter */}
            <div className="flex space-x-1">
              {[
                { key: "all", label: "All" },
                { key: "draft", label: "Draft" },
                { key: "deployed", label: "Deployed" },
                { key: "verified", label: "Verified" },
                { key: "archived", label: "Archived" }
              ].map((tab) => (
                <button
                  key={tab.key}
                  onClick={() => setFilter(tab.key as any)}
                  className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                    filter === tab.key
                      ? "bg-primary text-primary-foreground"
                      : "text-muted-foreground hover:text-foreground hover:bg-muted"
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </div>

            {/* Type Filter */}
            <div className="flex space-x-1">
              {[
                { key: "all", label: "All Types" },
                { key: "NFT", label: "NFT" },
                { key: "Token", label: "Token" },
                { key: "Marketplace", label: "Marketplace" },
                { key: "DAO", label: "DAO" },
                { key: "DeFi", label: "DeFi" }
              ].map((tab) => (
                <button
                  key={tab.key}
                  onClick={() => setTypeFilter(tab.key)}
                  className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                    typeFilter === tab.key
                      ? "bg-primary text-primary-foreground"
                      : "text-muted-foreground hover:text-foreground hover:bg-muted"
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </div>
          </div>
        </AnimatedSection>

        {/* Contracts Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredContracts.map((contract, index) => (
            <AnimatedSection key={contract.id} delay={0.1 * (index + 1)}>
              <Card className="hover:shadow-lg transition-all duration-200 cursor-pointer group">
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-primary/10 rounded-lg">
                        {getTypeIcon(contract.type)}
                      </div>
                      <div>
                        <CardTitle className="text-lg">{contract.name}</CardTitle>
                        <div className="flex items-center gap-2 mt-1">
                          <div className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(contract.status)}`}>
                            {getStatusIcon(contract.status)}
                            {contract.status}
                          </div>
                          <span className="text-xs text-muted-foreground">{contract.language}</span>
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
                    {contract.description}
                  </p>
                  
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-muted-foreground">Size:</span>
                      <span className="ml-1 font-medium">{contract.size}</span>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Gas Used:</span>
                      <span className="ml-1 font-medium">{contract.gasUsed}</span>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Security:</span>
                      <span className="ml-1 font-medium">{contract.securityScore}%</span>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Project:</span>
                      <span className="ml-1 font-medium">{contract.project}</span>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-1 text-sm text-muted-foreground">
                    <Clock className="h-4 w-4" />
                    Updated {contract.lastModified}
                  </div>
                  
                  <div className="flex items-center justify-between pt-2">
                    <div className="flex space-x-1">
                      <Button variant="ghost" size="sm" className="opacity-0 group-hover:opacity-100 transition-opacity">
                        <Eye className="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" size="sm" className="opacity-0 group-hover:opacity-100 transition-opacity">
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" size="sm" className="opacity-0 group-hover:opacity-100 transition-opacity">
                        <Copy className="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" size="sm" className="opacity-0 group-hover:opacity-100 transition-opacity">
                        <Download className="h-4 w-4" />
                      </Button>
                    </div>
                    <Button variant="ghost" size="sm" className="opacity-0 group-hover:opacity-100 transition-opacity text-red-500 hover:text-red-600">
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </AnimatedSection>
          ))}
        </div>

        {/* Empty State */}
        {filteredContracts.length === 0 && (
          <AnimatedSection delay={0.3}>
            <div className="text-center py-12">
              <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-medium text-foreground mb-2">No contracts found</h3>
              <p className="text-muted-foreground mb-4">
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
