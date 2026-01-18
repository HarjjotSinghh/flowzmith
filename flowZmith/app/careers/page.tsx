"use client"

import { SubpageLayout } from "@/components/subpage-layout"
import { AnimatedSection } from "@/components/animated-section"
import { ArrowRight } from "lucide-react"

const openings = [
  { title: "AI ARCHITECT", type: "FULL TIME", location: "REMOTE / GLOBAL", team: "ENGINEERING" },
  { title: "CADENCE SPECIALIST", type: "CONTRACT", location: "ON-CHAIN", team: "PROTOCOL" },
  { title: "PRODUCT DESIGNER", type: "FULL TIME", location: "REMOTE", team: "UX / UI" },
  { title: "DEV REL ENGINEER", type: "FULL TIME", location: "REMOTE", team: "GROWTH" },
]

export default function CareersPage() {
  return (
    <SubpageLayout 
      title="JOIN CORE." 
      subtitle="BUILD THE FUTURE OF ON-CHAIN INTELLIGENCE WITH US."
      category="Company // evolution"
    >
      <div className="space-y-12">
        <AnimatedSection delay={0.2}>
          <p className="text-2xl font-bold uppercase max-w-2xl leading-tight">
            WE ARE ALWAYS LOOKING FOR AGENTS WHO PUSH THE BOUNDARIES OF WHAT'S POSSIBLE IN WEB3 AND AI.
          </p>
        </AnimatedSection>

        <div className="mt-16 border-2 border-foreground">
          <div className="bg-foreground text-background p-4 flex justify-between items-center">
            <span className="text-xs font-black uppercase tracking-widest">OPEN PROTOCOLS (4)</span>
            <span className="text-[10px] font-bold">UPDATED: 2026.01.17</span>
          </div>
          <div className="divide-y-2 divide-foreground">
            {openings.map((job, index) => (
              <AnimatedSection key={job.title} delay={0.1 * index}>
                <div className="p-6 md:p-8 flex flex-col md:flex-row md:items-center justify-between group hover:bg-accent transition-colors cursor-pointer">
                  <div className="space-y-2 mb-4 md:mb-0">
                    <div className="flex items-center gap-3">
                      <h3 className="text-2xl font-black uppercase tracking-tighter group-hover:text-black">{job.title}</h3>
                      <span className="px-2 py-0.5 bg-black text-accent text-[8px] font-black">{job.type}</span>
                    </div>
                    <div className="flex gap-4 text-[10px] font-bold text-foreground/50 group-hover:text-black/60 uppercase">
                      <span>{job.team}</span>
                      <span>//</span>
                      <span>{job.location}</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 font-black text-xs group-hover:text-black">
                    INITIALIZE APPLICATION <ArrowRight className="h-4 w-4" />
                  </div>
                </div>
              </AnimatedSection>
            ))}
          </div>
        </div>

        <AnimatedSection delay={0.5}>
          <div className="mt-24 p-8 border-2 border-dashed border-foreground/30 text-center">
            <h3 className="text-xl font-black uppercase mb-4 opacity-50">NO MATCHING ROLE?</h3>
            <p className="text-sm font-bold uppercase mb-8 opacity-50">SEND YOUR AGENT MANIFESTO TO CAREERS@FLOWZMITH.IO</p>
            <button className="px-8 py-3 border-2 border-foreground font-black text-xs hover:bg-foreground hover:text-background transition-all uppercase">
              GENERAL SUBMISSION
            </button>
          </div>
        </AnimatedSection>
      </div>
    </SubpageLayout>
  )
}
