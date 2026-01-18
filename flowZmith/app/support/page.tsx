"use client"

import { SubpageLayout } from "@/components/subpage-layout"
import { AnimatedSection } from "@/components/animated-section"
import { HelpCircle, MessageSquare, LifeBuoy, FileQuestion } from "lucide-react"

const supportOptions = [
  { title: "KNOWLEDGE BASE", desc: "INSTANT ACCESS TO COMMON ISSUES AND RESOLUTIONS.", icon: FileQuestion },
  { title: "COMMUNITY CHAT", desc: "ENGAGE WITH OTHER ARCHITECTS IN OUR DISCORD.", icon: MessageSquare },
  { title: "DIRECT TICKET", desc: "SUBMIT A REQUEST FOR COMPLEX ARCHITECTURAL ISSUES.", icon: LifeBuoy },
  { title: "PRIORITY LINE", desc: "24/7 DEDICATED SUPPORT FOR ENTERPRISE ENTITIES.", icon: HelpCircle },
]

export default function SupportPage() {
  return (
    <SubpageLayout 
      title="ASSISTANCE." 
      subtitle="OUR AGENTS ARE STANDING BY TO RESOLVE ANY DISCREPANCIES."
      category="Resources // stability"
    >
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {supportOptions.map((opt, index) => (
          <AnimatedSection key={opt.title} delay={0.1 * index}>
            <div className="border-4 border-foreground p-8 flex flex-col h-full hover:bg-accent transition-all group">
              <div className="flex items-start justify-between mb-8">
                <div className="p-4 border-2 border-foreground bg-black group-hover:bg-black group-hover:text-accent transition-colors">
                  <opt.icon className="h-8 w-8 text-accent" />
                </div>
                <div className="text-[10px] font-black uppercase tracking-widest bg-black text-white px-2">ONLINE</div>
              </div>
              <h3 className="text-3xl font-black uppercase tracking-tighter mb-4 group-hover:text-black">{opt.title}</h3>
              <p className="text-lg font-bold text-foreground/70 uppercase leading-snug group-hover:text-black/80">{opt.desc}</p>
              <div className="mt-auto pt-12">
                <button className="w-full h-14 border-2 border-foreground bg-foreground text-background font-black uppercase group-hover:bg-black group-hover:text-accent transition-all">
                  INITIALIZE {opt.title.split(' ')[0]}
                </button>
              </div>
            </div>
          </AnimatedSection>
        ))}
      </div>

      <div className="mt-24 border-2 border-foreground p-12 bg-muted/5">
        <h2 className="text-3xl font-black uppercase mb-8 italic">SYSTEM STATUS</h2>
        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 bg-background border border-foreground/20">
            <span className="text-xs font-black uppercase">CORE AI ENGINE</span>
            <span className="text-xs font-black text-green-500 uppercase tracking-widest">OPERATIONAL</span>
          </div>
          <div className="flex items-center justify-between p-4 bg-background border border-foreground/20">
            <span className="text-xs font-black uppercase">DEPLOYMENT CLUSTER</span>
            <span className="text-xs font-black text-green-500 uppercase tracking-widest">OPERATIONAL</span>
          </div>
          <div className="flex items-center justify-between p-4 bg-background border border-foreground/20">
            <span className="text-xs font-black uppercase">AKAVE STORAGE SYNC</span>
            <span className="text-xs font-black text-green-500 uppercase tracking-widest">OPERATIONAL</span>
          </div>
        </div>
      </div>
    </SubpageLayout>
  )
}
