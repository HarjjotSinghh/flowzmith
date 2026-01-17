"use client"

import { Button } from "@/components/ui/button"
import { ThemeSwitcher } from "@/components/theme-switcher"
import { Sparkles, ShieldCheck, Zap } from "lucide-react"
import Link from "next/link"
import Image from "next/image"
import SignIn from "@/components/sign-in"

export default function SignupPage() {
  return (
    <div className="min-h-screen">
      <div className="grid min-h-screen lg:grid-cols-2">
        <div className="hidden lg:flex flex-col justify-between border-r border-border bg-card/80 p-12">
          <div className="flex items-center gap-3">
            <Image src="/images/flowZmithsLogo.svg" alt="Flowzmith" width={32} height={32} />
            <span className="text-xl font-semibold text-foreground font-display">Flowzmith</span>
          </div>
          <div className="space-y-6">
            <div className="inline-flex items-center gap-2 rounded-full border border-border bg-muted/70 px-4 py-2 text-xs font-semibold uppercase tracking-[0.2em] text-muted-foreground">
              Start building
            </div>
            <h1 className="text-4xl font-display font-semibold text-foreground">
              Create your Flow workspace in minutes.
            </h1>
            <p className="text-lg text-muted-foreground">
              Join teams shipping secure contracts faster with AI-assisted workflows and realtime collaboration.
            </p>
            <div className="grid grid-cols-1 gap-4">
              {[
                { icon: Sparkles, label: "AI prompt-to-contract" },
                { icon: Zap, label: "Fast deployment flows" },
                { icon: ShieldCheck, label: "Secure by default" },
              ].map((feature) => (
                <div key={feature.label} className="flex items-center gap-3 rounded-2xl border border-border/70 bg-card/70 p-4">
                  <feature.icon className="h-5 w-5 text-primary" />
                  <span className="text-sm text-foreground">{feature.label}</span>
                </div>
              ))}
            </div>
          </div>
          <div className="text-xs text-muted-foreground">Flowzmith © 2026</div>
        </div>

        <div className="flex flex-col justify-center px-6 py-12">
          <div className="mx-auto w-full max-w-md space-y-8">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-3xl font-display font-semibold text-foreground">Create account</h2>
                <p className="text-muted-foreground">Start your Flowzmith journey.</p>
              </div>
              <ThemeSwitcher />
            </div>

            <div className="space-y-6">
              <SignIn />

              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-border" />
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-4 bg-background text-muted-foreground">
                    Already have an account?
                  </span>
                </div>
              </div>

              <Link href="/login">
                <Button variant="outline" className="w-full rounded-full py-6">
                  Sign in instead
                </Button>
              </Link>
            </div>

            <p className="text-xs text-muted-foreground">
              By creating an account, you agree to our{" "}
              <Link href="/terms" className="text-primary hover:underline">
                Terms
              </Link>{" "}
              and{" "}
              <Link href="/privacy" className="text-primary hover:underline">
                Privacy Policy
              </Link>.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
