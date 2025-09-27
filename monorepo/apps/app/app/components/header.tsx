"use client"

import type React from "react"

import { Button } from "@/components/ui/button"
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet"
import { Menu, Wallet } from "lucide-react"
import Link from "next/link" // Import Link for client-side navigation
import { useAccount, useDisconnect } from "wagmi"
import {useSession} from "next-auth/react"
import Image from "next/image"
export function Header() {
  const { data: session } = useSession()

  const { address, isConnected } = useAccount()
  const { disconnect } = useDisconnect()
  const navItems = [
    { name: "Features", href: "#features-section" },
    { name: "Pricing", href: "#pricing-section" },
    { name: "Testimonials", href: "#testimonials-section" }, // Changed from Docs to Testimonials
  ]

  const handleConnectWallet = () => {
    // AppKit will handle the connection through the web component
  }

  const handleScroll = (e: React.MouseEvent<HTMLAnchorElement>, href: string) => {
    e.preventDefault()
    const targetId = href.substring(1) // Remove '#' from href
    const targetElement = document.getElementById(targetId)
    if (targetElement) {
      targetElement.scrollIntoView({ behavior: "smooth" })
    }
  }

  return (
    <header className="w-full py-4 px-6">
      <div className=" mx-auto flex items-center justify-between">
        <div className="flex items-center gap-6">
        <div className="flex items-center space-x-3">
            <Image src="/images/flowZmithsLogo.svg" alt="FlowZmith" width={32} height={32} />
            <span className="text-xl font-semibold text-foreground">FlowZmith</span>
          </div>
          <nav className="hidden md:flex items-center gap-2">
            {navItems.map((item) => (
              <Link
                key={item.name}
                href={item.href}
                onClick={(e) => handleScroll(e, item.href)} // Add onClick handler
                className="text-[#888888] hover:text-foreground px-4 py-2 rounded-full font-medium transition-colors"
              >
                {item.name}
              </Link>
            ))}
          </nav>
        </div>
        <div className="flex items-center gap-2">
         
         
            <Link href="/plans" className="w-full mt-2 border-border bg-accent text-foreground hover:bg-accent/90 hover:text-accent-foreground px-6 py-2 rounded-full font-medium shadow-sm">
              Plans
            </Link>
          
          {session ? (
                  <>
                  <Link href="/dashboard" className="w-full mt-2 border-border bg-accent text-foreground hover:bg-accent/90 hover:text-accent-foreground px-6 py-2 rounded-full font-medium shadow-sm">Dashboard</Link>
                  </>
                ): (
                  <>
                  <Link href="/login" className="w-full mt-2 border-border bg-accent text-foreground hover:bg-accent/90 hover:text-accent-foreground px-6 py-2 rounded-full font-medium shadow-sm">Login</Link>
                  </>
                )}
          <Sheet>
            <SheetTrigger asChild className="md:hidden">
              <Button  size="icon" className="text-foreground">
                <Menu className="h-7 w-7" />
                <span className="sr-only">Toggle navigation menu</span>
              </Button>
            </SheetTrigger>
            <SheetContent side="bottom" className="bg-background border-t border-border text-foreground">
              <SheetHeader>
                <SheetTitle className="text-left text-xl font-semibold text-foreground">Navigation</SheetTitle>
              </SheetHeader>
              <nav className="flex flex-col gap-4 mt-6">
                {navItems.map((item) => (
                  <Link
                    key={item.name}
                    href={item.href}
                    onClick={(e) => handleScroll(e, item.href)} // Add onClick handler
                    className="text-[#888888] hover:text-foreground justify-start text-lg py-2"
                  >
                    {item.name}
                  </Link>
                ))}
                {session ? (
                  <Link href="/dashboard" className="w-full mt-2">
                    <Button variant="outline" className="w-full border-border bg-accent text-foreground hover:bg-accent/90 hover:text-accent-foreground px-6 py-2 rounded-full font-medium shadow-sm">
                      Dashboard
                    </Button>
                  </Link>
                ) : (
                  <>
                  <Link href="/login" className="w-full mt-2">
                    <Button variant="outline" className="w-full border-border bg-accent text-foreground hover:bg-accent/90 hover:text-accent-foreground px-6 py-2 rounded-full font-medium shadow-sm">
                      Login
                    </Button>
                  </Link>
                  </>
                )}
                <Link href="/chat" className="w-full mt-2">
                  <Button variant="outline" className="w-full border-border bg-accent text-foreground hover:bg-accent/90 hover:text-accent-foreground px-6 py-2 rounded-full font-medium shadow-sm">
                    AI Chat
                  </Button>
                </Link>
                <Link href="/plans" className="w-full mt-2">
                  <Button variant="outline" className="w-full border-border bg-accent text-foreground hover:bg-accent/90 hover:text-accent-foreground px-6 py-2 rounded-full font-medium shadow-sm">
                    Plans
                  </Button>
                </Link>
                
              </nav>
            </SheetContent>
          </Sheet>
        </div>
      </div>
    </header>
  )
}
