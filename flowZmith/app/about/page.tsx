"use client"

import { SubpageLayout } from "@/components/subpage-layout"
import { AnimatedSection } from "@/components/animated-section"

export default function AboutPage() {
  return (
    <SubpageLayout 
      title="THE CORE." 
      subtitle="WE ARE ARCHITECTS OF THE FLOW EVOLUTION."
      category="Company // identity"
    >
      <div className="max-w-4xl space-y-16">
        <AnimatedSection delay={0.2}>
          <div className="space-y-8">
            <h2 className="text-4xl font-black uppercase tracking-tighter italic">OUR MISSION</h2>
            <p className="text-2xl font-bold leading-tight uppercase">
              TO LOWER THE BARRIER FOR SMART CONTRACT DEVELOPMENT BY COMBINING STATE-OF-THE-ART AI AGENTS WITH THE MOST SECURE BLOCKCHAIN INFRASTRUCTURE.
            </p>
            <p className="text-lg text-foreground/70 uppercase font-medium">
              FLOWZMITH WAS BORN OUT OF THE NEED FOR FASTER, MORE RELIABLE TOOLING IN THE FLOW ECOSYSTEM. WE BELIEVE THAT THE FUTURE OF WEB3 IS AI-ASSISTED, WHERE DEVELOPERS CAN FOCUS ON ARCHITECTURE AND LOGIC WHILE OUR AGENTS HANDLE THE BOILERPLATE AND SECURITY VALIDATION.
            </p>
          </div>
        </AnimatedSection>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-12 pt-16 border-t-2 border-foreground">
          <AnimatedSection delay={0.3}>
            <div className="space-y-4">
              <h3 className="text-xl font-black uppercase bg-black text-accent inline-block px-2">01. RESOURCE ORIENTED</h3>
              <p className="text-sm font-bold uppercase text-foreground/80 leading-relaxed">
                WE DEEPLY UNDERSTAND CADENCE. OUR ENGINES ARE TRAINED SPECIFICALLY ON RESOURCE-ORIENTED PATTERNS TO ENSURE YOUR CODE IS IDIOMATIC AND SECURE.
              </p>
            </div>
          </AnimatedSection>
          <AnimatedSection delay={0.4}>
            <div className="space-y-4">
              <h3 className="text-xl font-black uppercase bg-black text-accent inline-block px-2">02. OPEN COLLABORATION</h3>
              <p className="text-sm font-bold uppercase text-foreground/80 leading-relaxed">
                WE BELIEVE IN THE POWER OF TEAMS. FLOWZMITH IS BUILT FROM THE GROUND UP TO SUPPORT MULTI-USER WORKSPACES AND SHARED AI CONTEXT.
              </p>
            </div>
          </AnimatedSection>
        </div>

        <AnimatedSection delay={0.5}>
          <div className="bg-muted/10 border-2 border-foreground p-12 mt-16">
            <h2 className="text-3xl font-black uppercase mb-8">THE STATS</h2>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-8">
              <div>
                <div className="text-4xl font-black text-accent">10K+</div>
                <div className="text-[10px] font-bold uppercase opacity-50">CONTRACTS GEN</div>
              </div>
              <div>
                <div className="text-4xl font-black text-accent">2.5K</div>
                <div className="text-[10px] font-bold uppercase opacity-50">ACTIVE AGENTS</div>
              </div>
              <div>
                <div className="text-4xl font-black text-accent">99.9%</div>
                <div className="text-[10px] font-bold uppercase opacity-50">UPTIME SYNC</div>
              </div>
              <div>
                <div className="text-4xl font-black text-accent">$0.2s</div>
                <div className="text-[10px] font-bold uppercase opacity-50">LATENCY AVG</div>
              </div>
            </div>
          </div>
        </AnimatedSection>
      </div>
    </SubpageLayout>
  )
}
