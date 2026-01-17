"use client"

import { Twitter, Github, Linkedin, Terminal } from "lucide-react"

export function FooterSection() {
  return (
    <footer className="border-t-0 py-16 bg-background border-x-2 border-foreground mx-auto max-w-[1400px] lg:px-16">
      <div className="mx-auto w-full max-w-6xl flex flex-col gap-12 lg:flex-row lg:items-start lg:justify-between">
        <div className="space-y-6">
          <div className="flex items-center gap-3">
            <div className="h-8 w-8 bg-foreground flex items-center justify-center">
              <Terminal className="h-5 w-5 text-background" />
            </div>
            <span className="text-2xl font-black tracking-tighter text-foreground">FLOWZMITH</span>
          </div>
          <p className="text-sm font-bold text-foreground/80 max-w-xs leading-tight">
            DECENTRALIZED AI ARCHITECTS.
            POWERING THE FLOW ECOSYSTEM SINCE 2024.
          </p>
          <div className="flex items-center gap-4">
            <a href="#" className="p-2 border-2 border-foreground hover:bg-accent hover:text-black transition-all">
              <Twitter className="h-4 w-4" />
            </a>
            <a href="#" className="p-2 border-2 border-foreground hover:bg-accent hover:text-black transition-all">
              <Github className="h-4 w-4" />
            </a>
            <a href="#" className="p-2 border-2 border-foreground hover:bg-accent hover:text-black transition-all">
              <Linkedin className="h-4 w-4" />
            </a>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-12 sm:grid-cols-3">
          <div className="space-y-4">
            <h3 className="text-xs font-black uppercase tracking-widest text-accent bg-black inline-block px-1">01 PRODUCT</h3>
            <div className="flex flex-col gap-2">
              <a href="#" className="text-sm font-bold hover:text-accent transition-colors">./FEATURES</a>
              <a href="#" className="text-sm font-bold hover:text-accent transition-colors">./PRICING</a>
              <a href="#" className="text-sm font-bold hover:text-accent transition-colors">./INTEGRATIONS</a>
            </div>
          </div>
          <div className="space-y-4">
            <h3 className="text-xs font-black uppercase tracking-widest text-accent bg-black inline-block px-1">02 COMPANY</h3>
            <div className="flex flex-col gap-2">
              <a href="#" className="text-sm font-bold hover:text-accent transition-colors">./ABOUT</a>
              <a href="#" className="text-sm font-bold hover:text-accent transition-colors">./CAREERS</a>
              <a href="#" className="text-sm font-bold hover:text-accent transition-colors">./CONTACT</a>
            </div>
          </div>
          <div className="space-y-4">
            <h3 className="text-xs font-black uppercase tracking-widest text-accent bg-black inline-block px-1">03 RESOURCES</h3>
            <div className="flex flex-col gap-2">
              <a href="#" className="text-sm font-bold hover:text-accent transition-colors">./DOCS</a>
              <a href="#" className="text-sm font-bold hover:text-accent transition-colors">./API</a>
              <a href="#" className="text-sm font-bold hover:text-accent transition-colors">./SUPPORT</a>
            </div>
          </div>
        </div>
      </div>

      <div className="mx-auto max-w-6xl mt-16 pt-8 border-t-2 border-foreground/10 flex flex-col md:flex-row justify-between items-center gap-4 text-[10px] font-black text-foreground/80 uppercase tracking-widest">
        <span>© 2026 FLOWZMITH CORP NULL RESERVED</span>
        <div className="flex gap-8">
          <a href="#" className="hover:text-accent">PRIVACY POLICY</a>
          <a href="#" className="hover:text-accent">TERMS OF SERVICE</a>
          <span className="text-accent">STABLE BUILD V1.2.0</span>
        </div>
      </div>
    </footer>
  )
}