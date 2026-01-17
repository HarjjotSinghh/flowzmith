"use client"

import { Button } from "@/components/ui/button"
import Link from "next/link"
import { ArrowUpRight, Play, Terminal } from "lucide-react"
import { motion } from "framer-motion"

export default function LiveDemoSection() {
  return (
    <section className="py-24 bg-background border-y-2 border-foreground overflow-hidden border-x-2 border-foreground mx-auto max-w-[1400px] lg:px-16">
      <div className="mx-auto w-full max-w-6xl">
        <div className="grid gap-16 lg:grid-cols-[1fr_450px]">
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="space-y-8"
          >
            <div className="bg-accent text-black font-black px-4 py-1 text-xs inline-block tracking-[0.3em]">
              LIVE WORKSPACE
            </div>
            <h2 className="text-4xl md:text-6xl font-black text-foreground tracking-tighter uppercase leading-[0.9]">
              SEE CONTRACTS GENERATED AND DEPLOYED.
            </h2>
            <p className="text-lg md:text-xl font-bold text-foreground/80 border-l-4 border-foreground pl-6 max-w-xl">
              EVERY PROMPT IS CAPTURED, REVIEWED, AND PUSHED TO FLOW WITH FULL CONTEXT. STAY INSIDE ONE WORKSPACE WHILE FLOWZMITH HANDLES THE HEAVY LIFTING.
            </p>
            <div className="flex flex-wrap gap-4 pt-4">
              <Link href="/chat">
                <Button size="lg" className="h-16 px-10 text-xl group relative overflow-hidden">
                  <span className="relative z-10">LAUNCH WORKSPACE</span>
                  <ArrowUpRight className="ml-2 h-6 w-6 relative z-10 group-hover:translate-x-1 group-hover:-translate-y-1 transition-transform" />
                  <motion.div
                    className="absolute inset-0 bg-accent"
                    initial={{ x: "-100%" }}
                    whileHover={{ x: 0 }}
                    transition={{ type: "tween", ease: "easeInOut", duration: 0.3 }}
                  />
                </Button>
              </Link>
              <Link href="https://www.youtube.com/watch?v=LL6dfPs0COo" target="_blank">
                <Button variant="outline" size="lg" className="h-16 px-10 text-xl border-2 hover:bg-black hover:text-white transition-all">
                  WATCH DEMO
                </Button>
              </Link>
            </div>
          </motion.div>

          <div className="space-y-6">
            <motion.div
              initial={{ opacity: 0, scale: 0.9, filter: "blur(10px)" }}
              whileInView={{ opacity: 1, scale: 1, filter: "blur(0px)" }}
              viewport={{ once: true }}
              transition={{ delay: 0.2 }}
              whileHover={{ y: -5 }}
              className="border-4 border-foreground bg-background p-6 group transition-all"
            >
              <div className="flex items-center justify-between border-b-2 border-foreground pb-4 mb-4">
                <div>
                  <p className="text-[10px] font-black tracking-widest text-foreground/80 uppercase">SESSION ID: 0x921A</p>
                  <p className="text-xl font-black text-foreground uppercase tracking-tighter group-hover:text-accent transition-colors">FLOW CONTRACT GENERATOR</p>
                </div>
                <div className="flex items-center gap-2 bg-black px-2 py-1">
                  <span className="h-2 w-2 rounded-full bg-accent animate-pulse" />
                  <span className="text-[10px] font-black text-accent uppercase">LIVE</span>
                </div>
              </div>
              <div className="space-y-4 text-xs font-bold uppercase">
                <div className="flex items-center justify-between border-b border-foreground/10 pb-2">
                  <span className="text-foreground/80">PROMPT CYCLES</span>
                  <span className="text-foreground">12</span>
                </div>
                <div className="flex items-center justify-between border-b border-foreground/10 pb-2">
                  <span className="text-foreground/80">AVERAGE RESPONSE</span>
                  <span className="text-foreground">1.6S</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-foreground/80">DEPLOY SUCCESS</span>
                  <span className="text-accent bg-black px-1">98%</span>
                </div>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, scale: 0.9, filter: "blur(10px)" }}
              whileInView={{ opacity: 1, scale: 1, filter: "blur(0px)" }}
              viewport={{ once: true }}
              transition={{ delay: 0.4 }}
              whileHover={{ x: 5 }}
              className="border-2 border-foreground bg-black p-6 group"
            >
              <div className="flex items-center gap-4 mb-4">
                <div className="flex h-10 w-10 items-center justify-center border border-accent bg-accent">
                  <Terminal className="h-5 w-5 text-black" />
                </div>
                <div>
                  <p className="text-sm font-black text-white tracking-widest uppercase">REALTIME TERMINAL</p>
                  <p className="text-[10px] font-bold text-accent uppercase">DEPLOY, TEST, AND SHIP</p>
                </div>
              </div>
              <div className="p-4 bg-zinc-900 border border-zinc-800 font-mono text-[10px] text-zinc-400">
                <p className="flex gap-2"><span>$</span> <span>flow deploy StreamingRewards.cdc</span></p>
                <p className="mt-2 text-accent flex gap-2"><span>?</span> <span>Deployment successful in 14s</span></p>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, scale: 0.9, filter: "blur(10px)" }}
              whileInView={{ opacity: 1, scale: 1, filter: "blur(0px)" }}
              viewport={{ once: true }}
              transition={{ delay: 0.6 }}
              className="border-2 border-foreground bg-background p-6"
            >
              <div className="flex items-center gap-4 mb-4">
                <div className="flex h-10 w-10 items-center justify-center border-2 border-foreground bg-foreground text-background">
                  <Play className="h-5 w-5" />
                </div>
                <div>
                  <p className="text-sm font-black text-foreground tracking-widest uppercase">WORKFLOW AUTOMATION</p>
                  <p className="text-[10px] font-bold text-foreground/80 uppercase">GENERATE, REVIEW, DEPLOY</p>
                </div>
              </div>
              <div className="flex flex-wrap gap-2 pt-2">
                {['GENERATE', 'REVIEW', 'DEPLOY', 'MONITOR'].map((step) => (
                  <span key={step} className="text-[9px] font-black border border-foreground px-2 py-0.5 hover:bg-foreground hover:text-background transition-colors cursor-default">
                    {step}
                  </span>
                ))}
              </div>
            </motion.div>
          </div>
        </div>
      </div>
    </section>
  )
}
