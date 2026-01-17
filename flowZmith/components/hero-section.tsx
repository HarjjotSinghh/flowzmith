'use client'

import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Header } from "./header"
import { ArrowUpRight, ShieldCheck, Sparkles, Zap } from "lucide-react"

export function HeroSection() {
  return (
    <section className="relative mx-auto my-6 w-full max-w-6xl overflow-hidden rounded-[32px] border border-border/70 bg-card/85">
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute inset-0 bg-[radial-gradient(1200px_circle_at_10%_-10%,hsl(var(--primary)/0.12),transparent_45%)]" />
        <div className="absolute inset-0 bg-[radial-gradient(900px_circle_at_90%_10%,hsl(var(--foreground)/0.08),transparent_45%)]" />
        <div className="absolute inset-0 opacity-40" style={{ backgroundImage: "linear-gradient(to right, hsl(var(--border)/0.6) 1px, transparent 1px), linear-gradient(to bottom, hsl(var(--border)/0.6) 1px, transparent 1px)", backgroundSize: "48px 48px" }} />
      </div>

      <div className="relative z-10">
        <Header />

        <div className="grid gap-10 px-6 pb-14 pt-10 lg:grid-cols-[1.2fr_0.8fr]">
          <div className="space-y-6 text-left">
            <div className="inline-flex items-center gap-2 rounded-full border border-border bg-muted/70 px-4 py-2 text-xs font-semibold uppercase tracking-[0.2em] text-muted-foreground">
              <span className="h-1.5 w-1.5 rounded-full bg-primary" />
              Now in public beta
            </div>
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-display font-semibold text-balance">
              Build, verify, and ship Flow smart contracts at product speed.
            </h1>
            <p className="text-base md:text-lg text-muted-foreground max-w-xl">
              Flowzmith blends AI pair-programming with production-grade deployment, so your team can move from prompt to on-chain in minutes.
            </p>
            <div className="flex flex-wrap gap-3">
              <Link href="/login">
                <Button className="rounded-full px-6">Start building</Button>
              </Link>
              <Link href="/plans">
                <Button variant="outline" className="rounded-full px-6">
                  View plans
                </Button>
              </Link>
            </div>
            <div className="flex flex-wrap gap-4 text-xs text-muted-foreground">
              <div className="flex items-center gap-2">
                <span className="h-1.5 w-1.5 rounded-full bg-primary" />
                Real-time with Convex
              </div>
              <div className="flex items-center gap-2">
                <span className="h-1.5 w-1.5 rounded-full bg-primary" />
                GPT-assisted workflows
              </div>
              <div className="flex items-center gap-2">
                <span className="h-1.5 w-1.5 rounded-full bg-primary" />
                Secure Flow deployments
              </div>
            </div>
          </div>

          <div className="space-y-4">
            <div className="surface rounded-3xl p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Daily flow</p>
                  <p className="text-3xl font-semibold">2.4K contracts</p>
                </div>
                <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-primary/15 text-primary">
                  <Sparkles className="h-5 w-5" />
                </div>
              </div>
              <div className="mt-6 flex items-center gap-3 text-sm text-muted-foreground">
                <span className="inline-flex items-center gap-2 rounded-full border border-border px-3 py-1">
                  <ShieldCheck className="h-4 w-4 text-primary" />
                  Audited templates
                </span>
                <span className="inline-flex items-center gap-2 rounded-full border border-border px-3 py-1">
                  <Zap className="h-4 w-4 text-primary" />
                  3x faster
                </span>
              </div>
            </div>

            <div className="surface rounded-3xl p-6">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm font-medium">Live deployment status</p>
                  <p className="text-xs text-muted-foreground">Flow EVM � 2 minutes ago</p>
                </div>
                <ArrowUpRight className="h-4 w-4 text-primary" />
              </div>
              <div className="mt-4 rounded-2xl border border-border bg-muted/60 p-4">
                <p className="text-sm font-medium">Contract: StreamingRewards.cdc</p>
                <p className="text-xs text-muted-foreground mt-1">Gas usage optimized by 18%</p>
              </div>
            </div>

            <div className="surface rounded-3xl p-6 animate-float">
              <p className="text-sm font-medium">Team velocity</p>
              <div className="mt-4 flex items-center justify-between text-xs text-muted-foreground">
                <span>Design</span>
                <span className="text-foreground">16 min</span>
              </div>
              <div className="mt-2 flex items-center justify-between text-xs text-muted-foreground">
                <span>Generate</span>
                <span className="text-foreground">4 min</span>
              </div>
              <div className="mt-2 flex items-center justify-between text-xs text-muted-foreground">
                <span>Deploy</span>
                <span className="text-foreground">2 min</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
