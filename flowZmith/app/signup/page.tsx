"use client"

import { Button } from "@/components/ui/button"
import { Terminal, ShieldCheck, Zap, UserPlus } from "lucide-react"
import Link from "next/link"
import SignIn from "@/components/sign-in"

export default function SignupPage() {
  return (
    <div className="min-h-screen bg-background text-foreground font-mono selection:bg-accent selection:text-black">
      <div className="grid min-h-screen lg:grid-cols-2 border-4 border-foreground m-4">
        {/* Left Side: Terminal Info */}
        <div className="hidden lg:flex flex-col justify-between border-r-4 border-foreground bg-black p-12 relative overflow-hidden">
          <div className="absolute inset-0 pointer-events-none opacity-20 bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.25)_50%),linear-gradient(90deg,rgba(255,0,0,0.06),rgba(0,255,0,0.02),rgba(0,0,255,0.06))] bg-[length:100%_2px,3px_100%]" />

          <div className="relative z-10 space-y-8">
            <Link href="/" className="flex items-center gap-3 group">
              <div className="h-10 w-10 bg-accent flex items-center justify-center border-2 border-foreground group-hover:bg-foreground transition-colors">
                <Terminal className="h-6 w-6 text-black group-hover:text-accent" />
              </div>
              <span className="text-3xl font-black tracking-tighter">FLOWZMITH</span>
            </Link>

            <div className="space-y-6 pt-12">
              <div className="bg-accent text-black font-black px-4 py-1 text-xs inline-block">
                INITIALIZING NEW ENTITY REGISTRATION
              </div>
              <h1 className="text-6xl font-black tracking-tighter uppercase leading-none">
                JOIN THE CORE.
              </h1>
              <p className="text-xl font-bold text-foreground/80 border-l-4 border-accent pl-6 max-w-md">
                CREATE YOUR FLOW WORKSPACE. SECURE CONTRACTS. AI WORKFLOWS. INSTANT COLLABORATION.
              </p>
            </div>

            <div className="space-y-4 pt-8">
              {[
                { icon: Zap, label: "PROMPT TO CONTRACT V1" },
                { icon: ShieldCheck, label: "SECURE BY DEFAULT" },
              ].map((feature) => (
                <div key={feature.label} className="flex items-center gap-4 border-2 border-foreground p-4 bg-muted/10">
                  <feature.icon className="h-6 w-6 text-accent" />
                  <span className="text-sm font-black tracking-widest uppercase">{feature.label}</span>
                  <div className="ml-auto text-[10px] text-accent animate-pulse">PENDING AUTH</div>
                </div>
              ))}
            </div>
          </div>

          <div className="relative z-10 text-[10px] font-black tracking-[0.5em] text-foreground/80">
            FLOWZMITH REGISTRY V1.2.0 // NODE 01
          </div>
        </div>

        {/* Right Side: Signup Form */}
        <div className="flex flex-col justify-center items-center p-8 bg-background">
          <div className="w-full max-w-md space-y-12">
            <div className="space-y-4">
              <div className="flex justify-between items-end">
                <h2 className="text-5xl font-black tracking-tighter uppercase">REGISTER</h2>
                <div className="text-[10px] font-black text-accent bg-black px-2 py-0.5">OPEN REGISTRY</div>
              </div>
              <div className="h-2 w-full bg-foreground" />
            </div>

            <div className="space-y-8">
              <div className="border-4 border-foreground p-8 bg-muted/5 relative">
                <div className="absolute -top-3 -left-3 bg-background border-2 border-foreground p-1">
                  <UserPlus className="h-4 w-4" />
                </div>
                <SignIn />
              </div>

              <div className="relative py-4">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t-0 border-foreground border-dashed" />
                </div>
                <div className="relative flex justify-center text-[10px] font-black tracking-widest">
                  <span className="px-4 bg-background uppercase">Already Registered?</span>
                </div>
              </div>

              <Link href="/login" className="block">
                <Button variant="outline" className="w-full h-16 text-xl border-4 hover:bg-accent hover:text-black hover:border-foreground transition-all">
                  SIGN IN INSTEAD
                </Button>
              </Link>
            </div>

            <p className="text-[10px] font-bold text-foreground/80 uppercase leading-relaxed text-center">
              BY REGISTERING, YOU ACKNOWLEDGE THE{" "}
              <Link href="/terms" className="text-accent hover:underline">
                TERMS OF SERVICE
              </Link>{" "}
              AND{" "}
              <Link href="/privacy" className="text-accent hover:underline">
                PRIVACY PROTOCOLS
              </Link>.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}