"use client"

import Image from "next/image"
import { motion } from "framer-motion"

const testimonials = [
  {
    quote:
      "FLOWZMITH FEELS LIKE HAVING A SENIOR REVIEWER EMBEDDED IN OUR EDITOR. WE SHIP FASTER WITH FEWER REGRESSIONS.",
    name: "ANNETTE BLACK",
    company: "SONY",
    avatar: "/images/avatars/annette-black.png",
  },
  {
    quote: "THE MCP SERVER CONNECTIONS SAVED US DAYS OF CONFIGURATION WORK.",
    name: "DIANNE RUSSELL",
    company: "MCDONALD'S",
    avatar: "/images/avatars/dianne-russell.png",
  },
  {
    quote:
      "THE MULTI-AGENT CODING FLOW HELPED US RESOLVE COMPLEX BUGS IN HOURS INSTEAD OF WEEKS.",
    name: "CAMERON WILLIAMSON",
    company: "IBM",
    avatar: "/images/avatars/cameron-williamson.png",
  },
  {
    quote: "FLOWZMITH BROUGHT OUR INTEGRATIONS TOGETHER IN ONE PLACE AND SIMPLIFIED THE WORKFLOW.",
    name: "ROBERT FOX",
    company: "MASTERCARD",
    avatar: "/images/avatars/robert-fox.png",
  },
  {
    quote: "WE UPGRADED TO PRO IN THE FIRST WEEK. IT QUICKLY BECAME PART OF OUR CORE STACK.",
    name: "DARLENE ROBERTSON",
    company: "FERRARI",
    avatar: "/images/avatars/darlene-robertson.png",
  },
  {
    quote:
      "REAL-TIME PREVIEWS MADE PAIR PROGRAMMING MORE PRODUCTIVE AND SIGNIFICANTLY FASTER.",
    name: "CODY FISHER",
    company: "APPLE",
    avatar: "/images/avatars/cody-fisher.png",
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
  hidden: { opacity: 0, filter: "blur(10px)", scale: 0.95 },
  visible: {
    opacity: 1,
    filter: "blur(0px)",
    scale: 1,
    transition: { duration: 0.5 }
  },
}

export function TestimonialGridSection() {
  return (
    <section className="py-24 bg-background border-t-2 border-foreground border-x-2 border-foreground mx-auto max-w-[1400px] lg:px-16">
      <div className="mx-auto w-full max-w-6xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="flex flex-col items-center text-center gap-6 mb-16"
        >
          <div className="bg-accent text-black font-black px-4 py-1 text-xs tracking-[0.3em]">
            USER VOICES
          </div>
          <h2 className="text-4xl md:text-6xl font-black text-foreground tracking-tighter uppercase leading-none">
            CODING MADE EFFORTLESS.
          </h2>
          <p className="text-lg md:text-xl font-bold text-foreground/80 max-w-2xl">
            HEAR HOW TEAMS BUILD FASTER, COLLABORATE SEAMLESSLY, AND SHIP WITH CONFIDENCE.
          </p>
        </motion.div>

        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.1 }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 border-2 border-foreground bg-foreground gap-[2px]"
        >
          {testimonials.map((item) => (
            <motion.div
              key={item.name}
              variants={itemVariants}
              whileHover={{ backgroundColor: "hsl(var(--accent))" }}
              className="bg-background p-8 flex flex-col group transition-all duration-300 cursor-default"
            >
              <div className="flex-grow mb-8 relative">
                <span className="absolute -top-4 -left-2 text-4xl font-black text-accent group-hover:text-black/20 transition-colors">"</span>
                <p className="text-sm font-bold text-foreground/80 group-hover:text-black leading-snug transition-colors relative z-10">
                  {item.quote}
                </p>
              </div>
              <div className="flex items-center gap-4 pt-6 border-t-2 border-foreground/5 group-hover:border-black/10 transition-colors">
                <div className="relative">
                  <Image
                    src={item.avatar}
                    alt={`${item.name} avatar`}
                    width={44}
                    height={44}
                    className="h-11 w-11 border-2 border-foreground grayscale group-hover:grayscale-0 transition-all"
                  />
                  <div className="absolute -bottom-1 -right-1 h-3 w-3 bg-accent border border-foreground group-hover:bg-black transition-colors" />
                </div>
                <div>
                  <div className="text-sm font-black text-foreground group-hover:text-black transition-colors uppercase tracking-tight">{item.name}</div>
                  <div className="text-[10px] font-bold text-foreground/80 group-hover:text-black/60 transition-colors uppercase tracking-widest">{item.company}</div>
                </div>
              </div>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  )
}
