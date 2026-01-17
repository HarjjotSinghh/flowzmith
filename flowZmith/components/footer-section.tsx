"use client"

import { Twitter, Github, Linkedin } from "lucide-react"
import Image from "next/image"

export function FooterSection() {
  return (
    <footer className="border-t border-border/70 py-12">
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-10 px-6 md:flex-row md:items-start md:justify-between">
        <div className="space-y-4">
          <div className="flex items-center gap-3">
            <Image src="/images/flowZmithsLogo.svg" alt="Flowzmith" width={28} height={28} />
            <span className="text-lg font-semibold text-foreground font-display">Flowzmith</span>
          </div>
          <p className="text-sm text-muted-foreground max-w-xs">
            AI-powered smart contract workflows for Flow teams.
          </p>
          <div className="flex items-center gap-3">
            <a href="#" aria-label="Twitter" className="text-muted-foreground hover:text-foreground transition-colors">
              <Twitter className="h-4 w-4" />
            </a>
            <a href="#" aria-label="GitHub" className="text-muted-foreground hover:text-foreground transition-colors">
              <Github className="h-4 w-4" />
            </a>
            <a href="#" aria-label="LinkedIn" className="text-muted-foreground hover:text-foreground transition-colors">
              <Linkedin className="h-4 w-4" />
            </a>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-8 md:grid-cols-3">
          <div className="space-y-3 text-sm">
            <h3 className="text-xs font-semibold uppercase tracking-[0.2em] text-muted-foreground">Product</h3>
            <a href="#" className="block text-muted-foreground hover:text-foreground transition-colors">Features</a>
            <a href="#" className="block text-muted-foreground hover:text-foreground transition-colors">Pricing</a>
            <a href="#" className="block text-muted-foreground hover:text-foreground transition-colors">Integrations</a>
          </div>
          <div className="space-y-3 text-sm">
            <h3 className="text-xs font-semibold uppercase tracking-[0.2em] text-muted-foreground">Company</h3>
            <a href="#" className="block text-muted-foreground hover:text-foreground transition-colors">About</a>
            <a href="#" className="block text-muted-foreground hover:text-foreground transition-colors">Careers</a>
            <a href="#" className="block text-muted-foreground hover:text-foreground transition-colors">Contact</a>
          </div>
          <div className="space-y-3 text-sm">
            <h3 className="text-xs font-semibold uppercase tracking-[0.2em] text-muted-foreground">Resources</h3>
            <a href="#" className="block text-muted-foreground hover:text-foreground transition-colors">Docs</a>
            <a href="#" className="block text-muted-foreground hover:text-foreground transition-colors">API Reference</a>
            <a href="#" className="block text-muted-foreground hover:text-foreground transition-colors">Support</a>
          </div>
        </div>
      </div>
    </footer>
  )
}
