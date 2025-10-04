"use client"

import { motion } from "framer-motion"
import type { HTMLAttributes, ReactNode } from "react"
import { useReducedMotion } from "@/hooks/use-reduced-motion"

interface OptimizedAnimatedSectionProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode
  delay?: number
  animation?: "fadeInUp" | "fadeInDown" | "fadeInLeft" | "fadeInRight" | "scaleIn" | "blurIn"
  duration?: number
  viewport?: { once?: boolean; amount?: number }
}

const animations = {
  fadeInUp: {
    initial: { opacity: 0, y: 60 },
    whileInView: { opacity: 1, y: 0 }
  },
  fadeInDown: {
    initial: { opacity: 0, y: -60 },
    whileInView: { opacity: 1, y: 0 }
  },
  fadeInLeft: {
    initial: { opacity: 0, x: -60 },
    whileInView: { opacity: 1, x: 0 }
  },
  fadeInRight: {
    initial: { opacity: 0, x: 60 },
    whileInView: { opacity: 1, x: 0 }
  },
  scaleIn: {
    initial: { opacity: 0, scale: 0.8 },
    whileInView: { opacity: 1, scale: 1 }
  },
  blurIn: {
    initial: { opacity: 0, filter: "blur(10px)", scale: 0.95 },
    whileInView: { opacity: 1, filter: "blur(0px)", scale: 1 }
  }
}

export function OptimizedAnimatedSection({
  children,
  className,
  delay = 0,
  animation = "fadeInUp",
  duration = 0.8,
  viewport = { once: true, amount: 0.2 },
  ...props
}: OptimizedAnimatedSectionProps) {
  const prefersReducedMotion = useReducedMotion()

  if (prefersReducedMotion) {
    return (
      <div className={className} style={props.style}>
        {children}
      </div>
    )
  }

  const selectedAnimation = animations[animation]

  return (
    <motion.div
      initial={selectedAnimation.initial}
      whileInView={selectedAnimation.whileInView}
      viewport={viewport}
      transition={{
        duration,
        ease: [0.33, 1, 0.68, 1],
        delay
      }}
      className={className}
      style={props.style}
    >
      {children}
    </motion.div>
  )
}