"use client"

import { SubpageLayout } from "@/components/subpage-layout"
import { AnimatedSection } from "@/components/animated-section"
import { Book, Code, Search, Terminal } from "lucide-react"

const docCategories = [
  { 
    title: "GETTING STARTED", 
    links: ["INITIAL SETUP", "WALLET CONNECTION", "FIRST CONTRACT", "ENVIRONMENT CONFIG"],
    icon: Terminal 
  },
  { 
    title: "CADENCE CORE", 
    links: ["RESOURCES 101", "CAPABILITIES", "EVENTS & EMITTERS", "ACCESS CONTROL"],
    icon: Code 
  },
  { 
    title: "AI AGENTS", 
    links: ["PROMPT ENGINEERING", "CONTEXT SHARING", "BATCH GENERATION", "OPTIMIZATION TIPS"],
    icon: Book 
  },
  { 
    title: "DEPLOYMENT", 
    links: ["TESTNET PROTOCOLS", "MAINNET READINESS", "VERSIONING", "MIGRATION GUIDES"],
    icon: Search 
  },
]

export default function DocsPage() {
  return (
    <SubpageLayout 
      title="ARCHIVE." 
      subtitle="MASTER THE PROTOCOLS OF THE FLOWZMITH WORKSPACE."
      category="Resources // intelligence"
    >
      <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
        <AnimatedSection delay={0.2} className="md:col-span-2">
          <div className="relative">
            <input type="text" className="w-full bg-muted/5 border-4 border-foreground p-6 text-xl font-black uppercase tracking-widest outline-none focus:bg-accent focus:text-black transition-all" placeholder="SEARCH ARCHIVE..." />
            <Search className="absolute right-6 top-1/2 -translate-y-1/2 h-8 w-8 opacity-20" />
          </div>
        </AnimatedSection>

        {docCategories.map((cat, index) => (
          <AnimatedSection key={cat.title} delay={0.1 * index}>
            <div className="border-2 border-foreground h-full bg-background flex flex-col">
              <div className="bg-foreground text-background p-4 flex items-center gap-3">
                <cat.icon className="h-5 w-5" />
                <h3 className="text-sm font-black uppercase tracking-[0.2em]">{cat.title}</h3>
              </div>
              <div className="p-6 flex-grow">
                <div className="space-y-4">
                  {cat.links.map(link => (
                    <a key={link} href="#" className="block text-lg font-bold uppercase hover:text-accent transition-colors border-b border-foreground/10 pb-2">
                      {`./${link}`}
                    </a>
                  ))}
                </div>
              </div>
              <div className="p-4 border-t border-foreground/10 text-right">
                <button className="text-[10px] font-black uppercase tracking-widest hover:text-accent">
                  EXPAND CATEGORY →
                </button>
              </div>
            </div>
          </AnimatedSection>
        ))}
      </div>

      <div className="mt-24 bg-accent p-8 md:p-12 border-4 border-foreground flex flex-col md:flex-row items-center justify-between gap-8">
        <div>
          <h2 className="text-3xl font-black uppercase tracking-tighter text-black">NEW TO CADENCE?</h2>
          <p className="text-black/70 font-bold uppercase">START WITH OUR INTERACTIVE ONBOARDING FLOW.</p>
        </div>
        <button className="h-14 px-10 bg-black text-white font-black uppercase border-2 border-black hover:bg-white hover:text-black transition-all">
          COMMENCE TUTORIAL
        </button>
      </div>
    </SubpageLayout>
  )
}
