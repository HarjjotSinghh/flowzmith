"use client"

import { SubpageLayout } from "@/components/subpage-layout"
import { AnimatedSection } from "@/components/animated-section"

export default function TermsPage() {
  return (
    <SubpageLayout 
      title="TERMS." 
      subtitle="RULES OF ENGAGEMENT IN THE FLOWZMITH WORKSPACE."
      category="Legal // framework"
    >
      <div className="max-w-3xl space-y-12">
        <AnimatedSection delay={0.2}>
          <div className="space-y-6">
            <h2 className="text-2xl font-black uppercase tracking-tighter">01. ELIGIBILITY</h2>
            <p className="text-sm font-bold uppercase text-foreground/70 leading-relaxed">
              BY ACCESSING THE CORE, YOU WARRANT THAT YOU ARE OF LEGAL AGE AND POSSESS THE NECESSARY AUTHENTICATION TO EXECUTE PROTOCOLS ON THE FLOW BLOCKCHAIN.
            </p>
          </div>
        </AnimatedSection>

        <AnimatedSection delay={0.3}>
          <div className="space-y-6">
            <h2 className="text-2xl font-black uppercase tracking-tighter">02. RESOURCE ALLOCATION</h2>
            <p className="text-sm font-bold uppercase text-foreground/70 leading-relaxed">
              SYSTEM CREDITS ARE ALLOCATED PER AGENT ID. UNUSED CREDITS EXPIRE ACCORDING TO YOUR TIER PROTOCOL. ATTEMPTING TO EXPLOIT RESOURCE QUOTAS WILL RESULT IN IMMEDIATE TERMINATION.
            </p>
          </div>
        </AnimatedSection>

        <AnimatedSection delay={0.4}>
          <div className="space-y-6">
            <h2 className="text-2xl font-black uppercase tracking-tighter">03. ARCHITECTURAL RESPONSIBILITY</h2>
            <p className="text-sm font-bold uppercase text-foreground/70 leading-relaxed">
              WHILE OUR AI AGENTS PROVIDE SECURITY GUARDRAILS, THE ULTIMATE RESPONSIBILITY FOR ON-CHAIN CODE RESIDES WITH THE DEPLOYING ENTITY. ALWAYS SIMULATE BEFORE FINAL DEPLOYMENT.
            </p>
          </div>
        </AnimatedSection>

        <div className="p-8 border-2 border-foreground bg-muted/10 font-black text-[10px] uppercase space-y-2">
          <p>VERSION: 1.2.0_REV_A</p>
          <p>STABILITY: STABLE</p>
          <p>PROTOCOL_REF: FLOW_ENGAGEMENT_V2</p>
        </div>
      </div>
    </SubpageLayout>
  )
}
