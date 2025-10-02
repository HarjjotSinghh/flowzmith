"use client"

import { cn } from "@/lib/utils"
import { motion } from "framer-motion"

interface MagicCardProps {
  children: React.ReactNode
  className?: string
  gradientSize?: number
  gradientColor?: string
  gradientOpacity?: number
}

export function MagicCard({
  children,
  className,
  gradientSize = 200,
  gradientColor = "#262626",
  gradientOpacity = 0.8,
}: MagicCardProps) {
  return (
    <div
      className={cn(
        "relative overflow-hidden rounded-xl border border-border bg-card",
        className
      )}
    >
      <div className="absolute inset-0">
        <div
          className="absolute opacity-0 transition-opacity duration-300 group-hover:opacity-100"
          style={{
            background: `radial-gradient(circle at var(--mouse-x, 50%) var(--mouse-y, 50%), ${gradientColor} 0%, transparent 70%)`,
            width: `${gradientSize}px`,
            height: `${gradientSize}px`,
            opacity: gradientOpacity,
            transform: "translate(-50%, -50%)",
            left: "var(--mouse-x, 50%)",
            top: "var(--mouse-y, 50%)",
          }}
        />
      </div>
      <div className="relative z-10">{children}</div>
    </div>
  )
}