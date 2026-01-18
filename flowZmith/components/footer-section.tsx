"use client"

import { Twitter, Github, Linkedin, Terminal } from "lucide-react"
import Link from "next/link"

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
            <a href="https://twitter.com" target="_blank" className="p-2 border-2 border-foreground hover:bg-accent hover:text-black transition-all">
              <Twitter className="h-4 w-4" />
            </a>
            <a href="https://github.com" target="_blank" className="p-2 border-2 border-foreground hover:bg-accent hover:text-black transition-all">
              <Github className="h-4 w-4" />
            </a>
            <a href="https://linkedin.com" target="_blank" className="p-2 border-2 border-foreground hover:bg-accent hover:text-black transition-all">
              <Linkedin className="h-4 w-4" />
            </a>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-12 sm:grid-cols-3">
          <div className="space-y-4">
            <h3 className="text-xs font-black uppercase tracking-widest text-accent bg-black inline-block px-1">01 PRODUCT</h3>
            <div className="flex flex-col gap-2">
              <Link href="/features" className="text-sm font-bold hover:text-accent transition-colors">./FEATURES</Link>
              <Link href="/plans" className="text-sm font-bold hover:text-accent transition-colors">./PRICING</Link>
              <Link href="/integrations" className="text-sm font-bold hover:text-accent transition-colors">./INTEGRATIONS</Link>
            </div>
          </div>
          <div className="space-y-4">
            <h3 className="text-xs font-black uppercase tracking-widest text-accent bg-black inline-block px-1">02 COMPANY</h3>
            <div className="flex flex-col gap-2">
              <Link href="/about" className="text-sm font-bold hover:text-accent transition-colors">./ABOUT</Link>
              <Link href="/careers" className="text-sm font-bold hover:text-accent transition-colors">./CAREERS</Link>
              <Link href="/contact" className="text-sm font-bold hover:text-accent transition-colors">./CONTACT</Link>
            </div>
          </div>
          <div className="space-y-4">
            <h3 className="text-xs font-black uppercase tracking-widest text-accent bg-black inline-block px-1">03 RESOURCES</h3>
            <div className="flex flex-col gap-2">
              <Link href="/docs" className="text-sm font-bold hover:text-accent transition-colors">./DOCS</Link>
              <Link href="/api" className="text-sm font-bold hover:text-accent transition-colors">./API</Link>
              <Link href="/support" className="text-sm font-bold hover:text-accent transition-colors">./SUPPORT</Link>
            </div>
          </div>
        </div>
      </div>

      <div className="mx-auto max-w-6xl mt-16 pt-8 border-t-2 border-foreground/10 flex flex-col md:flex-row justify-between items-center gap-4 text-[10px] font-black text-foreground/80 uppercase tracking-widest">
        <span>© 2026 FLOWZMITH CORP NULL RESERVED</span>
        <div className="flex gap-8">
          <Link href="/privacy" className="hover:text-accent">PRIVACY POLICY</Link>
          <Link href="/terms" className="hover:text-accent">TERMS OF SERVICE</Link>
          <span className="text-accent">STABLE BUILD V1.2.0</span>
        </div>
      </div>
    </footer>
  )
}