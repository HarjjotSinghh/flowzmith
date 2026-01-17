"use client"

import type React from "react"

import { Button } from "@/components/ui/button"
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet"
import { Menu } from "lucide-react"
import Link from "next/link"
import Image from "next/image"
import { useSession } from "next-auth/react"
import { ThemeSwitcher } from "@/components/theme-switcher"

export function Header() {
  const { data: session } = useSession()

  const navItems = [
    { name: "Features", href: "#features-section" },
    { name: "Pricing", href: "#pricing-section" },
    { name: "Testimonials", href: "#testimonials-section" },
  ]

  const handleScroll = (e: React.MouseEvent<HTMLAnchorElement>, href: string) => {
    e.preventDefault()
    const targetId = href.substring(1)
    const targetElement = document.getElementById(targetId)
    if (targetElement) {
      targetElement.scrollIntoView({ behavior: "smooth" })
    }
  }

  return (
    <header className="w-full">
      <div className="mx-auto flex items-center justify-between px-6 py-4">
        <div className="flex items-center gap-6">
          <Link href="/" className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-full border border-border bg-card/70">
              <Image src="/images/flowZmithsLogo.svg" alt="Flowzmith" width={24} height={24} />
            </div>
            <div>
              <span className="text-lg font-semibold text-foreground font-display">Flowzmith</span>
              <div className="text-xs text-muted-foreground">AI smart contracts</div>
            </div>
          </Link>
          <nav className="hidden md:flex items-center gap-2">
            {navItems.map((item) => (
              <Link
                key={item.name}
                href={item.href}
                onClick={(e) => handleScroll(e, item.href)}
                className="text-sm text-muted-foreground hover:text-foreground transition-colors"
              >
                {item.name}
              </Link>
            ))}
          </nav>
        </div>
        <div className="flex items-center gap-3">
          <ThemeSwitcher />
          <Link
            href="/plans"
            className="hidden sm:inline-flex items-center rounded-full border border-border bg-card/80 px-4 py-2 text-sm font-medium text-foreground hover:bg-muted transition-colors"
          >
            Plans
          </Link>
          {session ? (
            <Link href="/dashboard">
              <Button className="rounded-full px-5">Dashboard</Button>
            </Link>
          ) : (
            <Link href="/login">
              <Button className="rounded-full px-5">Login</Button>
            </Link>
          )}
          <Sheet>
            <SheetTrigger asChild className="md:hidden">
              <Button size="icon" variant="ghost" className="text-foreground">
                <Menu className="h-5 w-5" />
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
                    onClick={(e) => handleScroll(e, item.href)}
                    className="text-foreground/90 hover:text-foreground justify-start text-lg py-2"
                  >
                    {item.name}
                  </Link>
                ))}
                <Link href="/plans" className="w-full mt-2">
                  <Button variant="outline" className="w-full rounded-full">
                    Plans
                  </Button>
                </Link>
                {session ? (
                  <Link href="/dashboard" className="w-full">
                    <Button className="w-full rounded-full">Dashboard</Button>
                  </Link>
                ) : (
                  <Link href="/login" className="w-full">
                    <Button className="w-full rounded-full">Login</Button>
                  </Link>
                )}
                <Link href="/chat" className="w-full">
                  <Button variant="outline" className="w-full rounded-full">
                    AI Chat
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
