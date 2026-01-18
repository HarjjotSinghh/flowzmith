"use client"

import { SubpageLayout } from "@/components/subpage-layout"
import { AnimatedSection } from "@/components/animated-section"
import { Box, Code2, Database, Github, Globe, Layers, Link2, Shield } from "lucide-react"
import Link from "next/link"

const integrations = [
  { name: "GITHUB", description: "SYNC YOUR REPOSITORIES AND DEPLOY STRAIGHT FROM YOUR BRANCHES.", icon: Github },
  { name: "FLOW CLI", description: "DEEP INTEGRATION WITH THE OFFICIAL FLOW COMMAND LINE INTERFACE.", icon: Code2 },
  { name: "AKAVE STORAGE", description: "SECURE, DECENTRALIZED DATA STORAGE FOR YOUR PROJECT ASSETS.", icon: Database },
  { name: "REOWN", description: "SEAMLESS WALLET CONNECTION PROTOCOLS FOR ALL EVM & FLOW WALLETS.", icon: Link2 },
  { name: "CADENCE V1", description: "FULL SUPPORT FOR THE NEWEST RESOURCE-ORIENTED SMART CONTRACT LANGUAGE.", icon: Layers },
  { name: "MAINNET NODES", description: "DIRECT ACCESS TO MAINNET AND TESTNET DEPLOYMENT ENDPOINTS.", icon: Globe },
]

export default function IntegrationsPage() {
  return (
    <SubpageLayout 
      title="INTEGRATIONS." 
      subtitle="PLUG INTO THE ENTIRE FLOW ECOSYSTEM WITH A SINGLE WORKSPACE."
      category="Product // connectivity"
    >
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
        {integrations.map((item, index) => (
          <AnimatedSection key={item.name} delay={0.1 * index}>
            <div className="border-2 border-foreground p-8 bg-background relative overflow-hidden group hover:translate-y-[-4px] hover:shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] transition-all">
              <div className="flex justify-between items-start mb-12">
                <div className="p-3 bg-foreground text-background">
                  <item.icon className="h-6 w-6" />
                </div>
                <div className="text-[10px] font-black text-accent bg-black px-2">READY</div>
              </div>
              <h3 className="text-2xl font-black uppercase tracking-tight mb-4">{item.name}</h3>
              <p className="text-sm font-bold text-foreground/70 uppercase leading-snug">{item.description}</p>
              <div className="mt-8 pt-4 border-t border-foreground/10">
                <button className="text-[10px] font-black uppercase tracking-widest hover:text-accent transition-colors">
                  VIEW DOCUMENTATION →
                </button>
              </div>
            </div>
          </AnimatedSection>
        ))}
      </div>

      <div className="mt-24 text-center">
        <AnimatedSection delay={0.5}>
          <h2 className="text-3xl font-black uppercase mb-8 italic">NEED A CUSTOM INTEGRATION?</h2>
          <Link href="/contact">
            <button className="h-16 px-12 bg-accent text-black font-black uppercase border-2 border-foreground hover:bg-black hover:text-accent transition-all text-xl">
              TALK TO ARCHITECTS
            </button>
          </Link>
        </AnimatedSection>
      </div>
    </SubpageLayout>
  )
}
