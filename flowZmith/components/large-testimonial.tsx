"use client"

import Image from "next/image"
import { motion } from "framer-motion"
import { Quote } from "lucide-react"

export function LargeTestimonial() {
  return (
    <section className="w-full border-y-4 border-foreground overflow-hidden bg-background py-24 border-x-2 border-foreground mx-auto max-w-[1400px] lg:px-16 relative">
      {/* Decorative elements */}
      <div className="absolute top-4 left-4 text-[10px] font-black text-foreground/80 opacity-30">TESTIMONIAL 01 CORE</div>
      <div className="absolute bottom-4 right-4 text-[10px] font-black text-foreground/80 opacity-30">VERIFIED BLOCK 772A</div>

      <div className="mx-auto max-w-6xl px-6">
        <div className="flex flex-col items-center gap-12 text-center">
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            className="h-16 w-16 bg-accent flex items-center justify-center border-2 border-foreground shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]"
          >
            <Quote className="h-8 w-8 text-black" />
          </motion.div>

          <motion.div
            initial={{ opacity: 0, filter: "blur(20px)" }}
            whileInView={{ opacity: 1, filter: "blur(0px)" }}
            viewport={{ once: true }}
            transition={{ duration: 0.8, ease: "easeOut" }}
            className="text-4xl md:text-5xl lg:text-7xl font-black tracking-tighter leading-[0.9] uppercase italic"
          >
            "Flowzmith's real-time previews cut our debugging time in half and made coding collaboratively actually enjoyable."
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.4 }}
            className="flex flex-col items-center gap-6"
          >
            <div className="relative">
              <div className="absolute -inset-2 border-2 border-accent border-dashed animate-[spin_10s_linear_infinite]" />
              <Image
                src="/images/guillermo-rauch.png"
                alt="Guillermo Rauch avatar"
                width={80}
                height={80}
                className="w-20 h-20 relative border-4 border-foreground grayscale hover:grayscale-0 transition-all duration-500"
              />
            </div>
            <div className="space-y-1">
              <div className="text-2xl font-black tracking-tighter text-foreground uppercase">Guillermo Rauch</div>
              <div className="text-xs font-bold text-accent bg-black px-2 py-0.5 inline-block tracking-widest uppercase">CEO, Vercel</div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  )
}
