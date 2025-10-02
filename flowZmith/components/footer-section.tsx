"use client"

import { Twitter, Github, Linkedin } from "lucide-react"
import Image from "next/image"
export function FooterSection() {
  return (
    <footer className="w-full max-w-[1320px] mx-auto px-5 flex flex-col md:flex-row justify-between items-start gap-8 md:gap-0 py-10 md:py-[70px] border-t border-border/50">
      {/* Left Section: Logo, Description, Social Links */}
      <div className="flex flex-col justify-start items-start gap-8 p-4 md:p-8">
      <div className="flex items-center space-x-3">
            <Image src="/images/flowZmithsLogo.svg" alt="Flowzmith" width={32} height={32} />
            <span className="text-xl font-semibold text-foreground">Flowzmith</span>
          </div>
        <p className="text-muted-foreground text-sm font-medium leading-[18px] text-left">Coding made effortless</p>
        <div className="flex justify-start items-start gap-3">
          <a href="#" aria-label="Twitter" className="w-4 h-4 flex items-center justify-center">
            <Twitter className="w-full h-full text-muted-foreground hover:text-foreground transition-colors" />
          </a>
          <a href="#" aria-label="GitHub" className="w-4 h-4 flex items-center justify-center">
            <Github className="w-full h-full text-muted-foreground hover:text-foreground transition-colors" />
          </a>
          <a href="#" aria-label="LinkedIn" className="w-4 h-4 flex items-center justify-center">
            <Linkedin className="w-full h-full text-muted-foreground hover:text-foreground transition-colors" />
          </a>
        </div>
      </div>
      {/* Right Section: Product, Company, Resources */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-8 md:gap-12 p-4 md:p-8 w-full md:w-auto">
        <div className="flex flex-col justify-start items-start gap-3">
          <h3 className="text-muted-foreground text-sm font-medium leading-5">Product</h3>
          <div className="flex flex-col justify-end items-start gap-2">
            <a href="#" className="text-foreground text-sm font-normal leading-5 hover:text-primary transition-colors">
              Features
            </a>
            <a href="#" className="text-foreground text-sm font-normal leading-5 hover:text-primary transition-colors">
              Pricing
            </a>
            <a href="#" className="text-foreground text-sm font-normal leading-5 hover:text-primary transition-colors">
              Integrations
            </a>
            <a href="#" className="text-foreground text-sm font-normal leading-5 hover:text-primary transition-colors">
              Real-time Previews
            </a>
            <a href="#" className="text-foreground text-sm font-normal leading-5 hover:text-primary transition-colors">
              Multi-Agent Coding
            </a>
          </div>
        </div>
        <div className="flex flex-col justify-start items-start gap-3">
          <h3 className="text-muted-foreground text-sm font-medium leading-5">Company</h3>
          <div className="flex flex-col justify-center items-start gap-2">
            <a href="#" className="text-foreground text-sm font-normal leading-5 hover:text-primary transition-colors">
              About us
            </a>
            <a href="#" className="text-foreground text-sm font-normal leading-5 hover:text-primary transition-colors">
              Our team
            </a>
            <a href="#" className="text-foreground text-sm font-normal leading-5 hover:text-primary transition-colors">
              Careers
            </a>
            <a href="#" className="text-foreground text-sm font-normal leading-5 hover:text-primary transition-colors">
              Brand
            </a>
            <a href="#" className="text-foreground text-sm font-normal leading-5 hover:text-primary transition-colors">
              Contact
            </a>
          </div>
        </div>
        <div className="flex flex-col justify-start items-start gap-3">
          <h3 className="text-muted-foreground text-sm font-medium leading-5">Resources</h3>
          <div className="flex flex-col justify-center items-start gap-2">
            <a href="#" className="text-foreground text-sm font-normal leading-5 hover:text-primary transition-colors">
              Terms of use
            </a>
            <a href="#" className="text-foreground text-sm font-normal leading-5 hover:text-primary transition-colors">
              API Reference
            </a>
            <a href="#" className="text-foreground text-sm font-normal leading-5 hover:text-primary transition-colors">
              Documentation
            </a>
            <a href="#" className="text-foreground text-sm font-normal leading-5 hover:text-primary transition-colors">
              Community
            </a>
            <a href="#" className="text-foreground text-sm font-normal leading-5 hover:text-primary transition-colors">
              Support
            </a>
          </div>
        </div>
      </div>
    </footer>
  )
}
