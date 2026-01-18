"use client"

import { SubpageLayout } from "@/components/subpage-layout"
import { AnimatedSection } from "@/components/animated-section"
import { Send, Mail, MapPin, MessageSquare } from "lucide-react"

export default function ContactPage() {
  return (
    <SubpageLayout 
      title="CONNECT." 
      subtitle="ESTABLISH A SECURE LINE WITH OUR AGENTS."
      category="Company // communication"
    >
      <div className="grid grid-cols-1 lg:grid-cols-[1fr_400px] gap-16">
        <AnimatedSection delay={0.2}>
          <form className="space-y-8" onSubmit={(e) => e.preventDefault()}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div className="space-y-2">
                <label className="text-[10px] font-black uppercase tracking-widest text-foreground/50">AGENT NAME</label>
                <input type="text" className="w-full bg-background border-2 border-foreground p-4 text-sm font-bold uppercase focus:bg-accent focus:text-black outline-none transition-all" placeholder="YOUR NAME" />
              </div>
              <div className="space-y-2">
                <label className="text-[10px] font-black uppercase tracking-widest text-foreground/50">ENTITY MAIL</label>
                <input type="email" className="w-full bg-background border-2 border-foreground p-4 text-sm font-bold uppercase focus:bg-accent focus:text-black outline-none transition-all" placeholder="YOU@DOMAIN.COM" />
              </div>
            </div>
            <div className="space-y-2">
              <label className="text-[10px] font-black uppercase tracking-widest text-foreground/50">PROTOCOL SUBJECT</label>
              <select className="w-full bg-background border-2 border-foreground p-4 text-sm font-bold uppercase focus:bg-accent focus:text-black outline-none transition-all appearance-none rounded-none cursor-pointer">
                <option>PARTNERSHIP INQUIRY</option>
                <option>TECHNICAL SUPPORT</option>
                <option>MEDIA REQUEST</option>
                <option>OTHER</option>
              </select>
            </div>
            <div className="space-y-2">
              <label className="text-[10px] font-black uppercase tracking-widest text-foreground/50">TRANSMISSION DATA</label>
              <textarea className="w-full bg-background border-2 border-foreground p-4 text-sm font-bold uppercase focus:bg-accent focus:text-black outline-none transition-all min-h-[200px]" placeholder="YOUR MESSAGE..."></textarea>
            </div>
            <button className="h-16 px-12 bg-foreground text-background font-black uppercase border-2 border-foreground hover:bg-accent hover:text-black transition-all text-xl flex items-center gap-4 group">
              EXECUTE SEND <Send className="h-5 w-5 group-hover:translate-x-1 group-hover:translate-y-[-4px] transition-transform" />
            </button>
          </form>
        </AnimatedSection>

        <div className="space-y-12">
          <AnimatedSection delay={0.3}>
            <div className="space-y-4">
              <h3 className="text-xl font-black uppercase tracking-tighter">DIRECT CHANNELS</h3>
              <div className="space-y-4">
                <div className="flex items-center gap-4 group cursor-pointer">
                  <div className="p-3 border-2 border-foreground bg-muted/10 group-hover:bg-accent group-hover:text-black transition-colors">
                    <Mail className="h-5 w-5" />
                  </div>
                  <div>
                    <div className="text-[10px] font-black opacity-50 uppercase">EMAIL</div>
                    <div className="text-sm font-bold">CORE@FLOWZMITH.IO</div>
                  </div>
                </div>
                <div className="flex items-center gap-4 group cursor-pointer">
                  <div className="p-3 border-2 border-foreground bg-muted/10 group-hover:bg-accent group-hover:text-black transition-colors">
                    <MessageSquare className="h-5 w-5" />
                  </div>
                  <div>
                    <div className="text-[10px] font-black opacity-50 uppercase">DISCORD</div>
                    <div className="text-sm font-bold">DISCORD.GG/FLOWZMITH</div>
                  </div>
                </div>
                <div className="flex items-center gap-4 group cursor-pointer">
                  <div className="p-3 border-2 border-foreground bg-muted/10 group-hover:bg-accent group-hover:text-black transition-colors">
                    <MapPin className="h-5 w-5" />
                  </div>
                  <div>
                    <div className="text-[10px] font-black opacity-50 uppercase">LOCATION</div>
                    <div className="text-sm font-bold">DECENTRALIZED / GLOBAL</div>
                  </div>
                </div>
              </div>
            </div>
          </AnimatedSection>

          <AnimatedSection delay={0.4}>
            <div className="p-8 border-2 border-foreground bg-black text-accent font-black text-xs space-y-4 italic">
              <p>RESPONSE TIME: 0.2s - 24h</p>
              <p>SECURITY STATUS: ENCRYPTED</p>
              <p>AGENTS ONLINE: 12</p>
            </div>
          </AnimatedSection>
        </div>
      </div>
    </SubpageLayout>
  )
}
