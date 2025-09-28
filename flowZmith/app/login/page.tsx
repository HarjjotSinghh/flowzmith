"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { AnimatedSection } from "@/components/animated-section"
import { Github, Code, Sparkles, Zap, ArrowLeft } from "lucide-react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import Image from "next/image"
import { signIn } from "next-auth/react"
import SignIn from "@/components/sign-in"
export default function LoginPage() {
  const [isLoading, setIsLoading] = useState(false)
  const router = useRouter()

  const handleGithubLogin = async () => {
    setIsLoading(true)
    console.log("Starting GitHub login...")
    
    try {
      // Method 1: Try with redirect: true (default behavior)
      await signIn("github", { 
        callbackUrl: "/dashboard"
      })
      
      // If we reach here, there was an error
      console.log("Login completed but no redirect happened")
      setIsLoading(false)
    } catch (error) {
      console.error("Error initiating GitHub OAuth:", error)
      setIsLoading(false)
    }
  }

  // Alternative method using window.location
  const handleGithubLoginAlternative = () => {
    setIsLoading(true)
    console.log("Using alternative login method...")
    
    // Direct redirect to NextAuth GitHub provider
    const baseUrl = window.location.origin
    window.location.href = `${baseUrl}/api/auth/signin/github?callbackUrl=/dashboard`
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="flex min-h-screen">
        {/* Left Side - Image */}
        <div className="hidden lg:flex lg:w-1/2 relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-primary/20 to-primary-dark/30" />
          <div className="relative w-full h-full flex items-center justify-center p-12">
            <div className="text-center space-y-8 max-w-2xl">
              <AnimatedSection className="space-y-4">
                <div className="flex justify-center">
                  <div className="relative">
                    <div className="w-24 h-24 bg-primary/20 rounded-full flex items-center justify-center backdrop-blur-sm">
                      <Code className="w-12 h-12 text-primary" />
                    </div>
                    <div className="absolute -top-2 -right-2">
                      <Sparkles className="w-6 h-6 text-primary" />
                    </div>
                  </div>
                </div>
                <h2 className="text-foreground text-5xl font-bold leading-tight">
                  Welcome Back to
                  <span className="text-primary"> FlowZmith</span>
                </h2>
                <p className="text-muted-foreground text-xl leading-relaxed">
                  Continue your smart contract development journey with AI-powered tools.
                  Build, deploy, and optimize contracts for Flow blockchain.
                </p>
              </AnimatedSection>

              <AnimatedSection delay={0.2} className="grid grid-cols-3 gap-6 mt-12">
                {[
                  { icon: Code, label: "Continue Building", desc: "Pick up where you left off" },
                  { icon: Zap, label: "Fast Deploy", desc: "Real-time deployment" },
                  { icon: Sparkles, label: "AI Optimized", desc: "Smart contract optimization" }
                ].map((feature, index) => (
                  <div key={index} className="text-center space-y-2">
                    <feature.icon className="w-8 h-8 text-primary mx-auto" />
                    <h3 className="text-foreground font-semibold">{feature.label}</h3>
                    <p className="text-muted-foreground text-sm">{feature.desc}</p>
                  </div>
                ))}
              </AnimatedSection>
            </div>
          </div>
        </div>

        {/* Right Side - Login Form */}
        <div className="w-full lg:w-1/2 flex items-center justify-center px-4 py-12">
          <div className="w-full max-w-md space-y-8">
            <AnimatedSection className="text-center">
              <div className="space-y-2">
                <h1 className="text-foreground text-4xl font-semibold">
                  Welcome Back
                </h1>
                <p className="text-muted-foreground text-lg">
                  Sign in to continue building
                </p>
              </div>
            </AnimatedSection>
              
            <AnimatedSection delay={0.1} className="space-y-6">
              {/* GitHub OAuth Button */}
              <SignIn />
              

              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-border" />
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-4 bg-background text-muted-foreground">
                    Don't have an account?
                  </span>
                </div>
              </div>

              {/* Signup Link */}
              <Link href="/signup">
                <Button
                  variant="outline"
                  className="w-full border-border text-foreground hover:bg-accent hover:text-accent-foreground px-6 py-4 rounded-2xl font-medium text-lg h-auto flex items-center gap-2"
                >
                  <ArrowLeft className="w-5 h-5" />
                  Create an account
                </Button>
              </Link>
            </AnimatedSection>

            <AnimatedSection delay={0.2} className="text-center">
              <p className="text-muted-foreground text-sm">
                By signing in, you agree to our{" "}
                <Link href="/terms" className="text-primary hover:underline">
                  Terms of Service
                </Link>{" "}
                and{" "}
                <Link href="/privacy" className="text-primary hover:underline">
                  Privacy Policy
                </Link>
              </p>
            </AnimatedSection>

            {/* Mobile Features */}
            <div className="lg:hidden mt-12 space-y-4">
              <div className="grid grid-cols-3 gap-4 text-center">
                {[
                  { icon: Code, label: "Continue Building" },
                  { icon: Zap, label: "Fast Deploy" },
                  { icon: Sparkles, label: "AI Optimized" }
                ].map((feature, index) => (
                  <div key={index} className="space-y-2">
                    <feature.icon className="w-6 h-6 text-primary mx-auto" />
                    <p className="text-muted-foreground text-xs">{feature.label}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}