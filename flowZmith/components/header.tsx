"use client"

import type React from "react"
import { Button } from "@/components/ui/button"
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet"
import { Menu, Terminal } from "lucide-react"
import Link from "next/link"
import { useSession } from "next-auth/react"

export function Header() {
  const { data: session } = useSession()

  const navItems = [
    { name: "FEATURES", href: "#features-section" },
    { name: "PRICING", href: "#pricing-section" },
    { name: "DOCS", href: "/docs" },
  ]

  const handleScroll = (e: React.MouseEvent<HTMLAnchorElement>, href: string) => {
    if (href.startsWith("#")) {
      e.preventDefault()
      const targetId = href.substring(1)
      const targetElement = document.getElementById(targetId)
      if (targetElement) {
        targetElement.scrollIntoView({ behavior: "smooth" })
      }
    }
  }

  return (
    <header className="w-full border-b-2 border-foreground border-x-1 bg-background sticky top-0 z-50 overflow-hidden max-w-[1440px] mx-auto">
      <div className="mx-auto flex items-center justify-between px-4 md:px-6 py-4 max-w-[1440px]">
        <div className="flex items-center gap-4 md:gap-8 overflow-hidden">
          <Link href="/" className="flex items-center gap-2 group shrink-0">
            <div className="flex h-8 w-8 items-center justify-center border-2 border-foreground bg-accent group-hover:bg-foreground transition-colors">
              <Terminal className="h-5 w-5 text-black group-hover:text-accent" />
            </div>
            <div className="flex flex-col leading-none">
              <span className="text-lg md:text-xl font-black tracking-tighter text-foreground">FLOWZMITH</span>
              <span className="text-[10px] font-bold text-accent bg-black px-1 self-start mt-0.5">V1.2.0</span>
            </div>
          </Link>
          <nav className="hidden md:flex items-center gap-4 lg:gap-6 overflow-hidden">
            {navItems.map((item) => (
              <Link
                key={item.name}
                href={item.href}
                onClick={(e) => handleScroll(e, item.href)}
                className="text-[10px] lg:text-xs font-bold text-foreground/80 hover:text-accent transition-colors tracking-widest whitespace-nowrap"
              >
                {`// ${item.name}`}
              </Link>
            ))}
          </nav>
        </div>
        <div className="flex items-center gap-2 md:gap-4 shrink-0">
          <div className="hidden sm:flex items-center gap-2 px-3 py-1 border border-muted-foreground/30 text-[9px] md:text-[10px] font-mono text-foreground/80">
            <span className="h-2 w-2 bg-accent animate-pulse" />
            <span className="hidden lg:inline">SYSTEM ONLINE</span>
            <span className="lg:hidden">ONLINE</span>
          </div>

          {session ? (
            <Link href="/dashboard" className="hidden xs:block">
              <Button variant="terminal" size="sm" className="h-8 md:h-10 text-[10px] md:text-xs">DASHBOARD</Button>
            </Link>
          ) : (
              <Link href="/login" className="hidden xs:block">
                <Button variant="terminal" size="sm" className="h-8 md:h-10 text-[10px] md:text-xs">LOGIN</Button>
            </Link>
          )}

          <Sheet>
            <SheetTrigger asChild>
              <Button size="icon" variant="ghost" className="border-2 border-foreground md:hidden h-8 w-8">
                <Menu className="h-4 w-4" />
              </Button>
            </SheetTrigger>
            <SheetContent side="right" className="bg-background border-l-4 border-foreground text-foreground p-0">
              <div className="p-6 h-full flex flex-col overflow-y-auto">
                <SheetHeader className="mb-8">
                  <SheetTitle className="text-left text-2xl font-black tracking-tighter uppercase">DIRECTORY</SheetTitle>
                </SheetHeader>
                <nav className="flex flex-col gap-2">
                  {navItems.map((item) => (
                    <Link
                      key={item.name}
                      href={item.href}
                      onClick={(e) => handleScroll(e, item.href)}
                      className="text-lg font-bold p-4 border-2 border-transparent hover:border-foreground hover:bg-accent hover:text-black transition-all"
                    >
                      {`> ${item.name}`}
                    </Link>
                  ))}
                  <div className="xs:hidden mt-4 space-y-2">
                    {session ? (
                      <Link href="/dashboard">
                        <Button variant="terminal" className="w-full">DASHBOARD</Button>
                      </Link>
                    ) : (
                      <Link href="/login">
                        <Button variant="terminal" className="w-full">LOGIN</Button>
                      </Link>
                    )}
                  </div>
                </nav>
                <div className="mt-auto pt-12">
                  <div className="text-[10px] font-mono text-foreground/80 text-center tracking-[0.3em]">
                    END OF TRANSMISSION
                  </div>
                </div>
              </div>
            </SheetContent>
          </Sheet>
        </div>
      </div>
    </header>
  )
}