"use client"

import { Button } from "@/components/ui/button"
import { ThemeSwitcher } from "@/components/theme-switcher"
import { User, Settings, Bell, LogOut, Wallet, ExternalLink } from "lucide-react"
import { signOut } from "next-auth/react"
import { useAccount, useDisconnect } from "wagmi"
import Image from "next/image"

interface DashboardHeaderProps {
  user: any
}

export function DashboardHeader({ user }: DashboardHeaderProps) {
  const { address, isConnected, chainId } = useAccount()
  const { disconnect } = useDisconnect()

  const handleSwitchNetwork = async () => {
    console.log("Switch network functionality will be handled by AppKit")
  }

  return (
    <header className="border-b border-border bg-card/80 backdrop-blur-sm">
      <div className="max-w-[1320px] mx-auto px-6 py-4">
        <div className="flex items-center justify-between gap-6">
          <div className="flex items-center space-x-3">
            <Image src="/images/flowZmithsLogo.svg" alt="Flowzmith" width={32} height={32} />
            <div>
              <div className="text-lg font-semibold text-foreground font-display">Flowzmith</div>
              <div className="text-xs text-muted-foreground">Workspace</div>
            </div>
          </div>

          <nav className="hidden lg:flex items-center space-x-6">
            <a href="/dashboard" className="text-foreground font-medium hover:text-primary transition-colors">
              Overview
            </a>
            <a href="/chat" className="text-muted-foreground hover:text-foreground transition-colors">
              Chat
            </a>
            <a href="/dashboard/projects" className="text-muted-foreground hover:text-foreground transition-colors">
              Projects
            </a>
            <a href="/dashboard/contracts" className="text-muted-foreground hover:text-foreground transition-colors">
              Contracts
            </a>
            <a href="/dashboard/analytics" className="text-muted-foreground hover:text-foreground transition-colors">
              Analytics
            </a>
          </nav>

          <div className="flex items-center gap-3">
            <ThemeSwitcher />
            {isConnected ? (
              <div className="hidden md:flex items-center space-x-3 rounded-full border border-border bg-muted/60 px-3 py-2">
                <Wallet className="h-4 w-4 text-primary" />
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="text-sm font-medium text-foreground">0 FLOW</span>
                    {chainId === 747 ? (
                      <span className="text-xs bg-primary/15 text-primary px-2 py-1 rounded-full">
                        Flow EVM
                      </span>
                    ) : (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={handleSwitchNetwork}
                        className="text-xs h-6 px-2"
                      >
                        Switch Network
                      </Button>
                    )}
                  </div>
                  <div className="text-xs text-muted-foreground">
                    {address?.slice(0, 6)}...{address?.slice(-4)}
                    <a
                      href={`https://evm.flowscan.io/address/${address}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="ml-1 hover:text-primary"
                    >
                      <ExternalLink className="h-3 w-3 inline ml-1" />
                    </a>
                  </div>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => disconnect()}
                  className="text-xs"
                >
                  Disconnect
                </Button>
              </div>
            ) : (
              <appkit-button />
            )}

            <Button variant="ghost" size="icon" className="relative">
              <Bell className="h-4 w-4" />
              <span className="absolute -top-1 -right-1 h-2 w-2 bg-primary rounded-full"></span>
            </Button>

            <Button variant="ghost" size="icon">
              <Settings className="h-4 w-4" />
            </Button>

            <div className="flex items-center space-x-3 pl-3 border-l border-border">
              <div className="w-8 h-8 bg-muted rounded-full flex items-center justify-center">
                <User className="h-4 w-4 text-muted-foreground" />
              </div>
              <div className="hidden sm:block">
                <p className="text-sm font-medium text-foreground">{user?.name || "User"}</p>
                <p className="text-xs text-muted-foreground">{user?.email}</p>
              </div>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => signOut()}
                className="text-muted-foreground hover:text-foreground"
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
