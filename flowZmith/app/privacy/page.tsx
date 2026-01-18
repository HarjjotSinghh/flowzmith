"use client"

import { SubpageLayout } from "@/components/subpage-layout"
import { AnimatedSection } from "@/components/animated-section"

export default function PrivacyPage() {
  return (
    <SubpageLayout 
      title="PRIVACY." 
      subtitle="OUR DATA HANDLING PROTOCOLS."
      category="Legal // security"
    >
      <div className="max-w-3xl space-y-12">
        <AnimatedSection delay={0.2}>
          <div className="space-y-6">
            <h2 className="text-2xl font-black uppercase tracking-tighter">01. DATA COLLECTION</h2>
            <p className="text-sm font-bold uppercase text-foreground/70 leading-relaxed">
              WE ONLY COLLECT DATA NECESSARY TO FACILITATE SMART CONTRACT GENERATION. THIS INCLUDES YOUR PROMPTS, WALLET ADDRESS, AND PROJECT METADATA. WE DO NOT SELL AGENT DATA TO EXTERNAL ENTITIES.
            </p>
          </div>
        </AnimatedSection>

        <AnimatedSection delay={0.3}>
          <div className="space-y-6">
            <h2 className="text-2xl font-black uppercase tracking-tighter">02. MODEL TRAINING</h2>
            <p className="text-sm font-bold uppercase text-foreground/70 leading-relaxed">
              USER PROMPTS ARE USED TO REFINE OUR AI AGENTS UNLESS YOU OPT-OUT IN YOUR WORKSPACE SETTINGS. ENTERPRISE DATA IS NEVER USED FOR GENERAL MODEL TRAINING.
            </p>
          </div>
        </AnimatedSection>

        <AnimatedSection delay={0.4}>
          <div className="space-y-6">
            <h2 className="text-2xl font-black uppercase tracking-tighter">03. ENCRYPTION</h2>
            <p className="text-sm font-bold uppercase text-foreground/70 leading-relaxed">
              ALL TRANSMISSIONS BETWEEN YOUR AGENT AND OUR CORE ARE ENCRYPTED VIA TLS 1.3. SENSITIVE WORKSPACE DATA IS STORED USING AES-256 ENCRYPTION AT REST.
            </p>
          </div>
        </AnimatedSection>

        <div className="p-8 border-2 border-foreground bg-muted/10 font-black text-[10px] uppercase space-y-2">
          <p>LAST_REVISION: 2026.01.17</p>
          <p>AUTH_LEVEL: GLOBAL_ACCESS</p>
          <p>PROTOCOL_ID: FM-PRIV-001</p>
        </div>
      </div>
    </SubpageLayout>
  )
}
