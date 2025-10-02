"use client"

import { cn } from "@/lib/utils"
import { forwardRef } from "react"

interface ShimmerButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode
  shimmerColor?: string
  shimmerSize?: string
  borderRadius?: string
  shimmerDuration?: string
  background?: string
  className?: string
  ...props
}

const ShimmerButton = forwardRef<HTMLButtonElement, ShimmerButtonProps>(
  (
    {
      children,
      className,
      shimmerColor = "#ffffff",
      shimmerSize = "110%",
      borderRadius = "100px",
      shimmerDuration = "3s",
      background = "rgba(0, 0, 0, 1)",
      ...props
    },
    ref
  ) => {
    return (
      <button
        style={
          {
            "--spread": "90deg",
            "--shimmer-color": shimmerColor,
            "--radius": borderRadius,
            "--speed": shimmerDuration,
            "--cut": shimmerSize,
            "--bg": background,
          } as React.CSSProperties
        }
        className={cn(
          "group relative z-0 flex cursor-pointer items-center justify-center overflow-hidden whitespace-nowrap border border-white/10 px-6 py-3 text-white [background:var(--bg)] [border-radius:var(--radius)] transition-all duration-300 hover:scale-105 active:scale-95",
          "before:absolute before:inset-0 before:z-0 before:rounded-[var(--radius)] before:bg-[linear-gradient(90deg,transparent,rgba(255,255,255,0.1),transparent)] before:opacity-0 before:transition-opacity before:duration-500 before:[transition-delay:0.4s] group-hover:before:opacity-100",
          "after:absolute after:inset-0 after:z-0 after:rounded-[var(--radius)] after:bg-[linear-gradient(90deg,transparent,var(--shimmer-color),transparent)] after:opacity-0 after:transition-opacity after:duration-500 after:[transition-delay:0.4s] group-hover:after:opacity-100",
          className
        )}
        ref={ref}
        {...props}
      >
        <span className="relative z-10">{children}</span>
      </button>
    )
  }
)

ShimmerButton.displayName = "ShimmerButton"

export { ShimmerButton }