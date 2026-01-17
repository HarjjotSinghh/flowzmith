"use client"

import { useState } from "react"
import { Check, Terminal } from "lucide-react"
import { Button } from "@/components/ui/button"
import { motion } from "framer-motion"

const pricingPlans = [
  {
    name: "BUILDER FREE",
    monthlyPrice: "$0",
    annualPrice: "$0",
    description: "PERFECT FOR INDIVIDUAL BUILDERS GETTING STARTED.",
    features: [
      "REAL TIME CODE SUGGESTIONS",
      "SINGLE MCP SERVER",
      "UP TO 2 AI AGENTS",
      "FLOW TEST DEPLOYMENTS",
    ],
    buttonText: "GET STARTED",
  },
  {
    name: "ARCHITECT PRO",
    monthlyPrice: "$20",
    annualPrice: "$16",
    description: "IDEAL FOR PROFESSIONAL TEAMS SHIPPING WEEKLY.",
    features: [
      "ENHANCED PREVIEWS",
      "MULTIPLE MCP SERVERS",
      "UP TO 10 AI AGENTS",
      "COLLABORATIVE CHAT",
      "PRIORITY SUPPORT",
    ],
    buttonText: "JOIN PRO",
    popular: true,
  },
  {
    name: "ENTITY ULTRA",
    monthlyPrice: "$200",
    annualPrice: "$160",
    description: "ENTERPRISE SCALE WITH DEDICATED SUPPORT.",
    features: [
      "UNLIMITED MCP CLUSTERS",
      "UNLIMITED AI AGENTS",
      "ENTERPRISE SECURITY",
      "SLA BACKED DEPLOY",
    ],
    buttonText: "TALK TO SALES",
  },
]

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.15,
    },
  },
}

const cardVariants = {
  hidden: { opacity: 0, filter: "blur(12px)", y: 30 },
  visible: {
    opacity: 1,
    filter: "blur(0px)",
    y: 0,
    transition: { duration: 0.6, ease: "easeOut" }
  },
}

export function PricingSection() {
  const [isAnnual, setIsAnnual] = useState(true)

  return (
    <section className="py-24 border-b-2 border-foreground bg-background overflow-hidden border-x-2 border-foreground mx-auto max-w-[1400px] lg:px-16">
      <div className="mx-auto w-full max-w-6xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="flex flex-col items-center text-center gap-6 mb-12"
        >
          <div className="bg-accent text-black font-black px-4 py-1 text-xs tracking-[0.3em]">
            PRICING PROTOCOLS
          </div>
          <h2 className="text-4xl md:text-6xl font-black text-foreground tracking-tighter uppercase leading-none">
            CHOOSE YOUR TIER.
          </h2>
          <p className="text-lg md:text-xl font-bold text-foreground/80 max-w-2xl">
            A PLAN FOR EVERY DEVELOPER, FROM INDIE BUILDERS TO ENTERPRISE CLUSTERS.
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          className="mt-12 flex items-center justify-center"
        >
          <div className="inline-flex items-center border-4 border-foreground bg-muted/10 p-1">
            <button
              onClick={() => setIsAnnual(true)}
              className={`px-4 md:px-6 py-2 text-[10px] md:text-xs font-black transition-all uppercase ${isAnnual ? "bg-foreground text-background" : "text-foreground/80 hover:text-foreground"
              }`}
            >
              ANNUAL DISCOUNT
            </button>
            <button
              onClick={() => setIsAnnual(false)}
              className={`px-4 md:px-6 py-2 text-[10px] md:text-xs font-black transition-all uppercase ${!isAnnual ? "bg-foreground text-background" : "text-foreground/80 hover:text-foreground"
              }`}
            >
              MONTHLY ACCESS
            </button>
          </div>
        </motion.div>

        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.1 }}
          className="mt-16 grid grid-cols-1 md:grid-cols-3 border-4 border-foreground bg-foreground gap-[4px]"
        >
          {pricingPlans.map((plan) => (
            <motion.div
              key={plan.name}
              variants={cardVariants as any}
              whileHover={{ zIndex: 10 }}
              className={`p-6 md:p-8 flex flex-col transition-all duration-300 hover:bg-accent h-full group relative ${plan.popular ? "bg-muted/[0.99]" : "bg-background"
              }`}
            >
              {plan.popular && (
                <div className="absolute top-0 right-0 bg-accent text-black px-3 py-1 text-[10px] font-black uppercase tracking-widest border-l-2 border-b-2 border-foreground z-10 group-hover:bg-black group-hover:text-accent group-hover:border-accent transition-colors duration-300">
                  RECOMMENDED
                </div>
              )}

              <div className="flex items-center mb-8">
                <div className="text-[10px] font-black text-white bg-black px-2 py-0.5 uppercase tracking-widest group-hover:bg-black group-hover:text-accent transition-colors duration-300">
                  {plan.name}
                </div>
              </div>

              <div className="mt-4 flex items-baseline gap-2">
                <div className="text-4xl md:text-5xl font-black text-foreground group-hover:text-black transition-colors duration-300">
                  {isAnnual ? plan.annualPrice : plan.monthlyPrice}
                </div>
                <span className={`text-[10px] font-bold uppercase tracking-widest transition-colors duration-300 ${plan.popular ? "text-foreground/80" : "text-foreground/80"} group-hover:text-black/60`}>
                  /MONTHLY
                </span>
              </div>

              <p className={`mt-4 text-xs font-bold leading-snug uppercase min-h-[3em] transition-colors duration-300 ${plan.popular ? "text-foreground/80" : "text-foreground/80"} group-hover:text-black/80`}>
                {plan.description}
              </p>

              <div className="mt-8 space-y-4 flex-grow">
                {plan.features.map((feature) => (
                  <div key={feature} className={`flex items-start gap-3 border-b pb-2 transition-colors duration-300 ${plan.popular ? "border-foreground/15" : "border-foreground/5"} group-hover:border-black/10`}>
                    <Check className="h-3.5 w-3.5 text-accent shrink-0 mt-0.5 group-hover:text-black transition-colors duration-300" />
                    <span className="text-[10px] font-bold uppercase tracking-wider text-foreground group-hover:text-black transition-colors duration-300">
                      {feature}
                    </span>
                  </div>
                ))}
              </div>

              <div className="mt-12">
                <Button
                  variant={plan.popular ? "terminal" : "outline"}
                  className={`w-full h-14 text-base md:text-lg border-2 ${plan.popular
                    ? "group-hover:bg-black group-hover:text-accent group-hover:border-black bg-accent text-black"
                    : "group-hover:bg-black group-hover:text-white group-hover:border-black"
                    }`}
                >
                  {plan.buttonText}
                  <Terminal className="ml-2 h-4 w-4" />
                </Button>
              </div>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  )
}
