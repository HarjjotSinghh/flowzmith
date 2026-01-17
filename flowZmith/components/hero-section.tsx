'use client'

import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Header } from "./header"
import { ArrowDown, Terminal, Zap, Code, Shield } from "lucide-react"
import { useEffect, useState } from "react"
import { motion, AnimatePresence } from "framer-motion"

const TERMINAL_LOGS = [
  { type: 'cmd', text: 'flow-cli keys generate' },
  { type: 'info', text: 'Generating new key pair...' },
  { type: 'success', text: '[SUCCESS] Public Key: 0x92f...a1b' },
  { type: 'cmd', text: 'flow-cli contract generate --prompt "NFT Staking"' },
  { type: 'info', text: 'AI CORE V4 initializing architecture...' },
  { type: 'info', text: 'Generating Cadence code...' },
  { type: 'success', text: 'Generated: StakingRewards.cdc' },
  { type: 'cmd', text: 'flow-cli project deploy --network mainnet' },
  { type: 'info', text: 'Simulating transaction...' },
  { type: 'progress', text: 'TRANSACTION PENDING... [88%]' },
  { type: 'success', text: 'DEPLOYED TO MAINNET AT 0x772a' },
];

export function HeroSection() {
  const [text, setText] = useState("")
  const [logs, setLogs] = useState<typeof TERMINAL_LOGS>([])
  const [logIndex, setLogIndex] = useState(0)
  const fullText = "build the future of flow."

  useEffect(() => {
    let i = 0
    const timer = setInterval(() => {
      setText(fullText.slice(0, i))
      i++
      if (i > fullText.length) clearInterval(timer)
    }, 100)
    return () => clearInterval(timer)
  }, [])

  useEffect(() => {
    const logInterval = setInterval(() => {
      setLogs(prev => {
        const nextLog = TERMINAL_LOGS[logIndex];
        const newLogs = [...prev, nextLog];
        if (newLogs.length > 8) newLogs.shift();
        return newLogs;
      });
      setLogIndex((prev) => (prev + 1) % TERMINAL_LOGS.length);
    }, 1500);
    return () => clearInterval(logInterval);
  }, [logIndex]);

  return (
    <section className="relative w-full overflow-hidden bg-background mx-auto max-w-[1400px] border-x-2 border-foreground">
      <Header />

      <div className="w-full">
        <div className="grid lg:grid-cols-[1fr_400px] border-b-2 border-foreground">
          <div className="p-6 md:p-12 lg:p-16 space-y-8 lg:border-r-2 border-foreground bg-background">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="space-y-4"
            >
              <motion.div
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ delay: 0.2 }}
                className="inline-block bg-accent text-black font-black px-4 py-1 text-xs"
              >
                INITIALIZING FLOW PROTOCOL V2
              </motion.div>
              <h1 className="text-4xl md:text-6xl lg:text-7xl xl:text-8xl font-black tracking-tighter leading-[0.9] text-foreground uppercase break-words">
                {text}
                <span className="animate-pulse">_</span>
              </h1>
            </motion.div>

            <motion.p
              initial={{ opacity: 0, filter: "blur(10px)" }}
              animate={{ opacity: 1, filter: "blur(0px)" }}
              transition={{ delay: 0.5, duration: 0.8 }}
              className="text-lg md:text-xl font-bold text-foreground/80 max-w-2xl leading-tight border-l-4 border-accent pl-4 md:pl-6 py-2"
            >
              AI-POWERED SMART CONTRACT ARCHITECTURE FOR THE FLOW ECOSYSTEM.
              FROM PROMPT TO ON-CHAIN IN SECONDS.
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.8 }}
              className="flex flex-wrap gap-4 pt-4"
            >
              <Link href="/login">
                <Button size="lg" className="h-14 md:h-16 px-6 md:px-10 text-lg md:text-xl group relative overflow-hidden">
                  <span className="relative z-10">EXECUTE START</span>
                  <Terminal className="ml-2 h-5 w-5 md:h-6 md:w-6 group-hover:rotate-12 transition-transform relative z-10" />
                  <motion.div
                    className="absolute inset-0 bg-accent"
                    initial={{ x: "-100%" }}
                    whileHover={{ x: 0 }}
                    transition={{ type: "tween", ease: "easeInOut", duration: 0.3 }}
                  />
                </Button>
              </Link>
              <Link href="/plans">
                <Button variant="outline" size="lg" className="h-14 md:h-16 px-6 md:px-10 text-lg md:text-xl border-accent text-accent hover:bg-accent hover:text-black bg-black transition-all duration-300">
                  VIEW PLANS
                </Button>
              </Link>
            </motion.div>

            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1.2, staggerChildren: 0.1 }}
              className="grid grid-cols-1 sm:grid-cols-3 gap-6 pt-8 border-t-2 border-foreground/10"
            >
              {[
                { icon: Zap, label: "Speed", value: "0.2s LATENCY" },
                { icon: Code, label: "Engine", value: "LLM CORE V4" },
                { icon: Shield, label: "Security", value: "AUDIT READY" }
              ].map((item, idx) => (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 1.2 + (idx * 0.1) }}
                  whileHover={{ y: -5 }}
                  className="space-y-1 cursor-default group"
                >
                  <div className="flex items-center gap-2 text-accent group-hover:text-foreground transition-colors">
                    <item.icon className="h-4 w-4" />
                    <span className="text-[10px] font-black uppercase tracking-widest">{item.label}</span>
                  </div>
                  <p className="text-xl font-black text-foreground">{item.value}</p>
                </motion.div>
              ))}
            </motion.div>
          </div>

          <div className="flex flex-col bg-black lg:bg-muted/10 overflow-hidden border-t-2 lg:border-t-0 border-foreground">
            <div className="p-4 border-b-2 border-foreground bg-accent text-black font-black text-xs flex justify-between items-center">
              <span>TERMINAL OUTPUT</span>
              <div className="flex gap-1">
                <div className="w-2 h-2 border border-black animate-pulse" />
                <div className="w-2 h-2 border border-black animate-pulse [animation-delay:0.2s]" />
                <div className="w-2 h-2 bg-black animate-pulse [animation-delay:0.4s]" />
              </div>
            </div>
            <div className="p-6 font-mono text-[10px] space-y-2 flex-grow bg-black lg:bg-transparent overflow-hidden h-[400px] flex flex-col justify-end">
              <AnimatePresence mode="popLayout">
                {logs.map((log, i) => (
                  <motion.div
                    key={log.text + i}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, height: 0 }}
                    className={`flex gap-2 group transition-all duration-200 p-1 hover:bg-accent hover:text-black cursor-default`}
                  >
                    <span className={log.type === 'cmd' ? 'text-accent group-hover:text-black' : 'text-zinc-500 group-hover:text-black'}>
                      {log.type === 'cmd' ? '$' : '>'}
                    </span>
                    <span className={`${log.type === 'cmd' ? 'text-white' :
                      log.type === 'success' ? 'text-accent' :
                        log.type === 'progress' ? 'bg-white text-black px-1 font-bold' :
                          'text-zinc-400'
                      } group-hover:text-black transition-colors duration-200`}>
                      {log.text}
                    </span>
                  </motion.div>
                ))}
              </AnimatePresence>

              <div className="mt-6 pt-6 border-t border-foreground/20 space-y-4">
                <motion.div
                  whileHover={{ backgroundColor: "rgba(255,255,255,0.05)" }}
                  className="border border-foreground/50 p-3 bg-muted/5 transition-colors group cursor-default"
                >
                  <div className="text-[8px] text-slate-500 mb-1 group-hover:text-white transition-colors">CONTRACT HEALTH</div>
                  <div className="text-lg font-black text-white lg:text-foreground group-hover:text-accent transition-colors tracking-tighter uppercase">STABLE_99.9%</div>
                </motion.div>
                <motion.div
                  whileHover={{ backgroundColor: "rgba(204,255,0,0.1)" }}
                  className="border border-accent/50 p-3 bg-accent/5 transition-colors group cursor-default"
                >
                  <div className="text-[8px] text-accent mb-1 group-hover:text-black transition-colors">TOTAL VOLUME</div>
                  <div className="text-lg font-black text-lg font-black text-accent group-hover:text-black transition-colors tracking-tighter uppercase">$1.2M+</div>
                </motion.div>
              </div>
            </div>
            <div className="mt-auto p-4 border-t-2 border-foreground text-[10px] font-bold flex justify-between bg-black text-white lg:text-foreground lg:bg-transparent">
              <span className="animate-pulse">CPU USAGE: 12%</span>
              <span className="animate-pulse [animation-delay:0.5s]">MEM USAGE: 456MB</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
