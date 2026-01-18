"use client"

import { Header } from "./header"
import { FooterSection } from "./footer-section"
import { AnimatedSection } from "./animated-section"
import { motion } from "framer-motion"

interface SubpageLayoutProps {
  children: React.ReactNode
  title: string
  subtitle?: string
  category?: string
}

export function SubpageLayout({ children, title, subtitle, category }: SubpageLayoutProps) {
  return (
    <div className="min-h-screen bg-background font-mono selection:bg-accent selection:text-black">
      <div className="mx-auto max-w-[1400px] border-x-2 border-foreground min-h-screen flex flex-col">
        <Header />
        
        <main className="flex-grow">
          {/* Page Hero */}
          <div className="border-b-2 border-foreground p-6 md:p-12 lg:p-16 bg-muted/5">
            <AnimatedSection delay={0.1}>
              <div className="space-y-6">
                {category && (
                  <div className="inline-block bg-accent text-black font-black px-4 py-1 text-xs tracking-widest uppercase">
                    {category}
                  </div>
                )}
                <h1 className="text-5xl md:text-7xl lg:text-8xl font-black tracking-tighter uppercase leading-[0.8] break-words">
                  {title}
                </h1>
                {subtitle && (
                  <p className="text-xl md:text-2xl font-bold text-foreground/80 border-l-4 border-accent pl-6 max-w-3xl uppercase leading-tight">
                    {subtitle}
                  </p>
                )}
              </div>
            </AnimatedSection>
          </div>

          <div className="p-6 md:p-12 lg:p-16">
            {children}
          </div>
        </main>

        <FooterSection />
      </div>
    </div>
  )
}
