"use client"

import { SubpageLayout } from "@/components/subpage-layout"
import { AnimatedSection } from "@/components/animated-section"
import { Wand2, Workflow, ShieldCheck, Timer, Server, Sparkles, Code, Zap } from "lucide-react"

const featureList = [
  {
    title: "PROMPT TO CONTRACT",
    description: "GENERATE PRODUCTION-READY CADENCE CONTRACTS WITH GUIDED PROMPTS AND BUILT-IN LINTING. OUR AI UNDERSTANDS THE UNIQUE RESOURCE-ORIENTED PARADIGM OF FLOW.",
    icon: Wand2,
  },
  {
    title: "SYNC COLLABORATION",
    description: "INVITE TEAMMATES AND EDIT SMART CONTRACTS IN SYNC WITH INSTANT UPDATES. INTEGRATED VERSION CONTROL AND CONFLICT RESOLUTION FOR WEB3 TEAMS.",
    icon: Workflow,
  },
  {
    title: "SECURITY GUARDRAILS",
    description: "AUTOMATIC CHECKS FOR COMMON FLOW VULNERABILITIES. STATIC ANALYSIS AND FORMAL VERIFICATION ASSISTANCE BUILT INTO THE WORKFLOW.",
    icon: ShieldCheck,
  },
  {
    title: "SPEED RUN DEPLOY",
    description: "COMPILE, SIMULATE, AND DEPLOY IN A SINGLE WORKSPACE. REDUCE THE DEPLOYMENT CYCLE FROM HOURS TO SECONDS.",
    icon: Timer,
  },
  {
    title: "RESOURCES OBSERVER",
    description: "TRACK USAGE, CREDITS, AND DEPLOYMENT STATS IN ONE PLACE. REAL-TIME MONITORING OF ACCOUNT STATE AND CONTRACT RESOURCES.",
    icon: Server,
  },
  {
    title: "AI CODE REVIEW",
    description: "CONTEXTUAL FEEDBACK ON CODE QUALITY BEFORE YOU SHIP. THE AI ANALYZES YOUR ARCHITECTURE FOR EFFICIENCY AND COMPLIANCE.",
    icon: Sparkles,
  },
]

export default function FeaturesPage() {
  return (
    <SubpageLayout 
      title="CORE FEATURES." 
      subtitle="A COMPLETE WORKSPACE FOR THE NEXT GENERATION OF FLOW DEVELOPERS."
      category="Product // capabilities"
    >
      <div className="grid grid-cols-1 md:grid-cols-2 gap-[2px] bg-foreground border-2 border-foreground">
        {featureList.map((feature, index) => (
          <AnimatedSection key={feature.title} delay={0.1 * index}>
            <div className="bg-background p-8 md:p-12 h-full group hover:bg-accent transition-all duration-300">
              <div className="h-16 w-16 border-2 border-foreground flex items-center justify-center mb-8 bg-muted/10 group-hover:bg-black group-hover:text-accent transition-colors">
                <feature.icon className="h-8 w-8" />
              </div>
              <h3 className="text-3xl font-black tracking-tighter uppercase mb-4 group-hover:text-black">
                {`[ ${feature.title} ]`}
              </h3>
              <p className="text-lg font-bold text-foreground/70 leading-snug uppercase group-hover:text-black/80">
                {feature.description}
              </p>
            </div>
          </AnimatedSection>
        ))}
      </div>

      <div className="mt-24 border-4 border-foreground p-8 md:p-16 bg-black text-white relative overflow-hidden">
        <div className="absolute top-0 right-0 p-4 opacity-10">
          <Zap className="w-32 h-32 text-accent" />
        </div>
        <div className="relative z-10 max-w-3xl">
          <h2 className="text-4xl md:text-6xl font-black tracking-tighter uppercase mb-8 leading-none">
            ENGINEERED FOR THE FLOW V2 EVOLUTION.
          </h2>
          <p className="text-xl font-bold text-accent mb-12 uppercase leading-tight">
            WE ARE CONSTANTLY UPDATING OUR CORE ENGINE TO SUPPORT THE LATEST CADENCE IMPROVEMENTS.
          </p>
          <div className="flex flex-wrap gap-4">
            <div className="px-4 py-2 border border-accent text-accent text-xs font-black uppercase">CADENCE 1.0 READY</div>
            <div className="px-4 py-2 border border-accent text-accent text-xs font-black uppercase">EVM COMPATIBLE</div>
            <div className="px-4 py-2 border border-accent text-accent text-xs font-black uppercase">MULTI-NODE SYNC</div>
          </div>
        </div>
      </div>
    </SubpageLayout>
  )
}
