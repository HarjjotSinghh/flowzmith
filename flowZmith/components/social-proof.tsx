"use client"

import { Database, Bot, Globe, Users, Code2, Zap } from "lucide-react"
import { motion } from "framer-motion"

const MetricCard = ({
  icon: Icon,
  value,
  label,
  trend,
  index,
  isProvider = false,
  description = ""
}: {
  icon: React.ComponentType<any>
    value?: string
  label: string
  trend?: string
    index: number
    isProvider?: boolean
    description?: string
}) => (
  <motion.div
    initial={{ opacity: 0, filter: "blur(10px)", y: 20 }}
    whileInView={{ opacity: 1, filter: "blur(0px)", y: 0 }}
    viewport={{ once: true }}
    transition={{ delay: index * 0.05, duration: 0.5 }}
    whileHover={{ backgroundColor: "hsl(var(--accent))", zIndex: 10 }}
    className="flex flex-col items-start gap-4 border-2 border-foreground bg-background p-6 group transition-all duration-300 cursor-default h-full relative"
  >
    <div className="flex h-10 w-10 items-center justify-center border-2 border-foreground bg-background group-hover:bg-black group-hover:border-black transition-colors duration-300">
      <Icon className="h-5 w-5 group-hover:text-accent transition-colors duration-300" />
    </div>
    <div className="w-full">
      {value && <div className="text-3xl font-black text-foreground group-hover:text-black tracking-tighter transition-colors duration-300 uppercase">{value}</div>}
      <div className={`font-black tracking-widest transition-colors duration-300 uppercase ${isProvider ? 'text-lg text-foreground group-hover:text-black mb-2' : 'text-[10px] text-foreground/80 group-hover:text-black/70'}`}>
        {label}
      </div>
      {description && <p className="text-xs font-bold text-foreground/80 group-hover:text-black/80 uppercase leading-tight mt-2">{description}</p>}
      {trend && (
        <div className="mt-4 inline-flex items-center gap-2 text-[10px] font-black bg-black text-accent px-2 py-0.5 group-hover:bg-white group-hover:text-black transition-colors duration-300">
          <span className="h-1.5 w-1.5 rounded-full bg-accent animate-pulse group-hover:bg-black" />
          {trend.toUpperCase()}
        </div>
      )}
    </div>
    <div className="absolute bottom-0 right-0 w-2 h-2 bg-foreground group-hover:bg-black transition-colors" />
  </motion.div>
)

export function SocialProof() {
  const items = [
    { icon: Zap, value: "25K+", label: "SIMULATED DEPLOYS", trend: "LIVE BETA" },
    { icon: Code2, value: "100%", label: "REALTIME SYNC", trend: "CONVEX CORE" },
    { icon: Users, value: "50+", label: "TEAMS ONBOARDED", trend: "WEEKLY GROWTH" },
    { icon: Database, value: "5", label: "DATA PIPELINES", trend: "AUTOMATED" },
    { icon: Database, label: "CONVEX BACKBONE", description: "LOW LATENCY COLLABORATION LAYERS BACKED BY LIVE SYNC.", isProvider: true },
    { icon: Bot, label: "OPENAI COPILOTS", description: "PROMPT TO CONTRACT GENERATION WITH GUARDRAILS AND REVIEWS.", isProvider: true },
    { icon: Globe, label: "FIRECRAWL INTEL", description: "CONTEXT INGESTION FROM DOCS, AUDITS, AND CHANGELOGS.", isProvider: true },
  ]

  return (
    <section className="py-24 bg-background overflow-hidden border-t-2 border-foreground border-x-2 border-foreground mx-auto max-w-[1400px] lg:px-16">
      <div className="mx-auto w-full max-w-6xl">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true }}
          className="flex flex-col items-start gap-4 mb-16"
        >
          <div className="bg-accent text-black font-black px-4 py-1 text-xs tracking-[0.3em]">
            PROOF OF MOMENTUM
          </div>
          <h2 className="text-4xl md:text-6xl font-black text-foreground tracking-tighter uppercase leading-none">
            TRUSTED INFRASTRUCTURE.
          </h2>
          <p className="text-lg md:text-xl font-bold text-foreground/80 max-w-2xl border-l-4 border-accent pl-6">
            FLOWZMITH INTEGRATES REAL-TIME DATA, AI GUIDANCE, AND DEPLOYMENT SAFEGUARDS TO KEEP BUILDERS SHIPPING SAFELY.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 border-4 border-foreground bg-foreground gap-[4px]">
          {/* First 4 metrics */}
          {items.slice(0, 4).map((item, idx) => (
            <MetricCard key={idx} {...item} index={idx} />
          ))}
          {/* Next 3 providers spanning the remaining columns */}
          {items.slice(4).map((item, idx) => (
            <div key={idx + 4} className={idx === 2 ? "sm:col-span-2 lg:col-span-2" : "col-span-1"}>
              <MetricCard {...item} index={idx + 4} />
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}