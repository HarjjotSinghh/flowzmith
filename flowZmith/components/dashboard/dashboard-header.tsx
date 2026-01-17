"use client"

import { Button } from "@/components/ui/button"
import { Terminal, Settings, Bell, LogOut, Wallet, ExternalLink, Shield } from "lucide-react"
import { signOut } from "next-auth/react"
import { useAccount, useDisconnect } from "wagmi"

interface DashboardHeaderProps {
  user: any
}

export function DashboardHeader({ user }: DashboardHeaderProps) {
  const { address, isConnected, chainId } = useAccount()
  const { disconnect } = useDisconnect()

  const navItems = [
    { name: "OVERVIEW", href: "/dashboard" },
    { name: "AI CHAT", href: "/chat" },
    { name: "PROJECTS", href: "/dashboard/projects" },
    { name: "CONTRACTS", href: "/dashboard/contracts" },
    { name: "ANALYTICS", href: "/dashboard/analytics" },
  ]

  return (
    <header className="border-b-4 border-foreground bg-background">
      <div className="mx-auto px-6 py-4">
        <div className="flex items-center justify-between gap-6">
          <div className="flex items-center space-x-6">
            <div className="flex items-center gap-3 group">
              <div className="h-10 w-10 bg-accent flex items-center justify-center border-2 border-foreground group-hover:bg-foreground transition-colors">
                <Terminal className="h-6 w-6 text-black group-hover:text-accent" />
              </div>
              <div className="hidden sm:block">
                <div className="text-xl font-black tracking-tighter text-foreground leading-none uppercase">FLOWZMITH</div>
                <div className="text-[10px] font-bold text-accent bg-black px-1 mt-1">WS LOCKED</div>
              </div>
            </div>

            <nav className="hidden xl:flex items-center gap-1">
              {navItems.map((item) => (
                <a
                  key={item.name}
                  href={item.href}
                  className="px-4 py-2 text-[10px] font-black hover:bg-accent hover:text-black transition-all border-2 border-transparent hover:border-foreground"
                >
                  {`> ${item.name}`}
                </a>
              ))}
            </nav>
          </div>

          <div className="flex items-center gap-4">
            {isConnected ? (
              <div className="hidden md:flex items-center gap-4 border-2 border-foreground p-2 bg-muted/5">
                <div className="h-8 w-8 bg-accent flex items-center justify-center border border-foreground">
                  <Wallet className="h-4 w-4 text-black" />
                </div>
                <div className="space-y-0.5">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-black tracking-tighter">0 FLOW</span>
                    {chainId === 747 && (
                      <span className="text-[8px] bg-black text-accent px-1 font-bold border border-accent">EVM</span>
                    )}
                  </div>
                  <div className="text-[10px] font-bold opacity-50 flex items-center gap-1">
                    {address?.slice(0, 6)}...{address?.slice(-4)}
                    <a href={`https://evm.flowscan.io/address/${address}`} target="_blank" rel="noopener noreferrer">
                      <ExternalLink className="h-3 w-3" />
                    </a>
                  </div>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => disconnect()}
                  className="h-8 px-2 text-[10px] border-2"
                >
                  DISCONNECT
                </Button>
              </div>
            ) : (
              <div className="hidden md:block">
                <appkit-button />
              </div>
            )}

            <div className="flex items-center gap-2">
              <Button variant="outline" size="icon" className="border-2 border-foreground hover:bg-accent hover:text-black group relative">
                <Bell className="h-4 w-4" />
                <span className="absolute top-1 right-1 h-2 w-2 bg-red-500 animate-pulse" />
              </Button>

              <Button variant="outline" size="icon" className="border-2 border-foreground hover:bg-accent hover:text-black">
                <Settings className="h-4 w-4" />
              </Button>
            </div>

            <div className="flex items-center gap-4 pl-4 border-l-2 border-foreground">
              <div className="hidden md:block text-right">
                <p className="text-[10px] font-black leading-none uppercase">{user?.name || "ANON USER"}</p>
                <p className="text-[8px] font-bold opacity-50 mt-1 uppercase truncate max-w-[120px]">{user?.email}</p>
              </div>
              <div className="h-10 w-10 bg-foreground flex items-center justify-center border-2 border-foreground">
                <Shield className="h-5 w-5 text-accent" />
              </div>
              <Button
                variant="outline"
                size="icon"
                onClick={() => signOut()}
                className="border-2 border-foreground hover:bg-red-500 hover:text-white"
              >
                <LogOut className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}
