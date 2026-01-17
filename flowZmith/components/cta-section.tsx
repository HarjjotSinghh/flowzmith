"use client"

import { Button } from "@/components/ui/button"
import Link from "next/link"
import { ArrowRight, Terminal } from "lucide-react"
import { motion } from "framer-motion"

export function CTASection() {
  return (
    <section className="py-24 border-y-2 border-foreground bg-background overflow-hidden border-x-2 border-foreground mx-auto max-w-[1400px] lg:px-16">
      <div className="mx-auto w-full max-w-6xl">
        <motion.div
          initial={{ opacity: 0, scale: 0.95, filter: "blur(10px)" }}
          whileInView={{ opacity: 1, scale: 1, filter: "blur(0px)" }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="border-4 border-foreground bg-accent p-8 md:p-16 lg:p-20 relative overflow-hidden group"
        >
          <div className="absolute inset-0 opacity-10 pointer-events-none" style={{ backgroundImage: "linear-gradient(to right, #000 1px, transparent 1px), linear-gradient(to bottom, #000 1px, transparent 1px)", backgroundSize: "20px 20px" }} />

          <motion.div
            className="absolute inset-0 bg-[radial-gradient(circle_at_var(--x,_50%)_var(--y,_50%),rgba(255,255,255,0.3)_0%,transparent_50%)] pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity duration-300"
            style={{
              background: 'radial-gradient(circle at center, rgba(255,255,255,0.4) 0%, transparent 70%)',
              mixBlendMode: 'soft-light'
            }}
          />

          <div className="relative z-10 flex flex-col lg:flex-row lg:items-center lg:justify-between gap-16">
            <div className="space-y-6">
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0.3 }}
                className="bg-black text-accent font-black px-4 py-1 text-xs inline-block tracking-[0.3em]"
              >
                FINALIZE DEPLOYMENT
              </motion.div>
              <motion.h2
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0.4 }}
                className="text-4xl md:text-5xl lg:text-6xl font-black text-black tracking-tighter uppercase leading-[0.9]"
              >
                READY TO SHIP ON FLOW?
              </motion.h2>
              <motion.p
                initial={{ opacity: 0 }}
                whileInView={{ opacity: 1 }}
                viewport={{ once: true }}
                transition={{ delay: 0.5 }}
                className="text-lg md:text-xl font-bold text-black/80 max-w-2xl uppercase"
              >
                SPIN UP A NEW FLOW CONTRACT IN MINUTES.<br /> COLLABORATE IN REAL-TIME. SHIP WITH CONFIDENCE.
              </motion.p>
            </div>

            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ delay: 0.6 }}
              className="flex flex-col sm:flex-col-reverse gap-4 shrink-0 items-end justify-end h-full mt-auto"
            >
              <Link href="/login">
                <Button className="h-14 md:h-16 px-8 md:px-10 text-lg md:text-xl bg-black text-white hover:bg-white hover:text-black border-2 border-black transition-all duration-300 group/btn">
                  START BUILDING
                  <ArrowRight className="ml-2 h-5 w-5 md:h-6 md:w-6 group-hover/btn:translate-x-1 transition-transform" />
                </Button>
              </Link>
              <Link href="/plans">
                <Button variant="outline" className="h-14 md:h-16 px-8 md:px-10 text-lg md:text-xl border-2 border-black text-black bg-transparent hover:bg-black hover:text-accent transition-all duration-300 group/btn2">
                  VIEW PLANS
                  <Terminal className="ml-2 h-4 w-4 md:h-5 md:w-5 group-hover/btn2:rotate-12 transition-transform" />
                </Button>
              </Link>
            </motion.div>
          </div>
        </motion.div>

        <div className="mt-8 flex flex-col sm:flex-row justify-between items-center gap-4 text-[10px] font-black text-foreground/80 uppercase tracking-[0.4em]">
          <motion.span
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
          >
            FLOWZMITH TERMINAL V1.2.0
          </motion.span>
          <motion.span
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="text-accent bg-black px-2 py-1 animate-pulse"
          >
            SYSTEM READY FOR ENGAGEMENT
          </motion.span>
        </div>
      </div>
    </section>
  )
}
