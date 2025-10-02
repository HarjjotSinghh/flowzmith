"use client"

import { cn } from "@/lib/utils"

interface AnimatedShinyTextProps {
  children: React.ReactNode
  className?: string
  shimmerWidth?: number
}

export function AnimatedShinyText({
  children,
  className,
  shimmerWidth = 100,
}: AnimatedShinyTextProps) {
  return (
    <p
      className={cn(
        "animate-shiny-text bg-gradient-to-r from-transparent via-foreground/40 to-transparent bg-[length:var(--shimmer-width)_100%] bg-clip-text text-transparent",
        className
      )}
      style={{
        "--shimmer-width": `${shimmerWidth}px`,
      } as React.CSSProperties}
    >
      {children}
    </p>
  )
}