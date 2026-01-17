"use client"

import { ShieldCheck, Sparkles, Workflow, Timer, Server, Wand2 } from "lucide-react"
import { motion } from "framer-motion"

const features = [
  {
    title: "PROMPT TO CONTRACT",
    description: "GENERATE CADENCE CONTRACTS WITH GUIDED PROMPTS AND BUILT-IN LINTING.",
    icon: Wand2,
  },
  {
    title: "SYNC COLLABORATION",
    description: "INVITE TEAMMATES AND EDIT IN SYNC WITH INSTANT UPDATES.",
    icon: Workflow,
  },
  {
    title: "SECURITY GUARDRAILS",
    description: "AUTOMATIC CHECKS FOR COMMON FLOW VULNERABILITIES.",
    icon: ShieldCheck,
  },
  {
    title: "SPEED RUN DEPLOY",
    description: "COMPILE, SIMULATE, AND DEPLOY IN A SINGLE WORKSPACE.",
    icon: Timer,
  },
  {
    title: "RESOURCES OBSERVER",
    description: "TRACK USAGE, CREDITS, AND DEPLOYMENT STATS IN ONE PLACE.",
    icon: Server,
  },
  {
    title: "AI CODE REVIEW",
    description: "CONTEXTUAL FEEDBACK ON CODE QUALITY BEFORE YOU SHIP.",
    icon: Sparkles,
  },
]

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
}

const itemVariants = {
  hidden: { opacity: 0, filter: "blur(10px)", y: 20 },
  visible: {
    opacity: 1,
    filter: "blur(0px)",
    y: 0,
    transition: { duration: 0.5, ease: "easeOut" }
  },
}

export function BentoSection() {
  return (
    <section className="py-24 border-y-2 border-foreground bg-background overflow-hidden border-x-2 border-foreground mx-auto max-w-[1400px] lg:px-16">
      <div className="mx-auto w-full max-w-6xl">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true }}
          className="flex flex-col gap-6 items-start mb-16"
        >
          <div className="bg-foreground text-background font-black px-4 py-1 text-xs tracking-[0.3em]">
            MODULES CORE FEATURES
          </div>
          <h2 className="text-4xl md:text-6xl font-black text-foreground tracking-tighter uppercase leading-none">
            EVERYTHING TO SHIP ON FLOW.
          </h2>
          <p className="text-lg md:text-xl font-bold text-foreground/80 max-w-2xl border-l-4 border-foreground pl-6">
            A SINGLE WORKSPACE FOR IDEATION, GENERATION, VALIDATION, AND DEPLOYMENT WITH TIGHT AI SUPPORT.
          </p>
        </motion.div>

        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.2 }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 border-2 border-foreground bg-foreground gap-[1px]"
        >
          {features.map((feature) => (
            <motion.div
              key={feature.title}
              variants={itemVariants}
              className="group p-8 transition-all duration-300 hover:bg-accent bg-background flex flex-col h-full cursor-pointer relative overflow-hidden"
            >
              <div className="flex h-12 w-12 items-center justify-center border-2 border-foreground bg-background group-hover:bg-black group-hover:border-black transition-colors duration-300">
                <feature.icon className="h-6 w-6 group-hover:text-accent transition-colors duration-300" />
              </div>

              <h3 className="mt-8 text-xl font-black tracking-tighter text-foreground group-hover:text-black transition-colors duration-300">
                {`[ ${feature.title} ]`}
              </h3>

              <p className="mt-4 text-sm font-bold text-foreground/80 group-hover:text-black/80 leading-snug transition-colors duration-300">
                {feature.description}
              </p>

              <div className="mt-auto pt-8 flex justify-between items-center">
                <div className="text-[10px] font-black tracking-widest text-foreground/80 group-hover:text-black/60 transition-colors duration-300 uppercase">
                  STATUS: READY
                </div>
                <div className="h-2 w-2 bg-foreground group-hover:bg-black group-hover:scale-150 transition-all duration-300 animate-pulse" />
              </div>

              <div className="absolute top-0 right-0 w-0 h-0 border-t-[20px] border-l-[20px] border-t-transparent border-l-transparent group-hover:border-t-black transition-all duration-300" />
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  )
}