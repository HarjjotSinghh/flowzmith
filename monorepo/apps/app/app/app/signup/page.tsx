"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { AnimatedSection } from "@/components/animated-section"
import { Github, Code, Sparkles, Zap, ArrowRight, User, Mail, Lock } from "lucide-react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { signIn } from "next-auth/react"

export default function SignupPage() {
  const [isLoading, setIsLoading] = useState(false)
  const router = useRouter()

  const handleGithubSignup = async () => {
    setIsLoading(true)
    console.log("Starting GitHub signup...")
    
    try {
      // Method 1: Try with redirect: true (default behavior)
      await signIn("github", { 
        callbackUrl: "/dashboard"
      })
      
      // If we reach here, there was an error
      console.log("Signup completed but no redirect happened")
      setIsLoading(false)
    } catch (error) {
      console.error("Error initiating GitHub OAuth:", error)
      setIsLoading(false)
    }
  }

  // Alternative method using window.location
  const handleGithubSignupAlternative = () => {
    setIsLoading(true)
    console.log("Using alternative signup method...")
    
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
                  Join
                  <span className="text-primary"> FlowZmith</span>
                </h2>
                <p className="text-muted-foreground text-xl leading-relaxed">
                  Start building smart contracts with AI-powered tools. 
                  Create, deploy, and optimize contracts for Flow blockchain.
                </p>
              </AnimatedSection>

              <AnimatedSection delay={0.2} className="grid grid-cols-3 gap-6 mt-12">
                {[
                  { icon: Code, label: "AI-Powered", desc: "Smart contract generation" },
                  { icon: Zap, label: "Fast Deploy", desc: "One-click deployment" },
                  { icon: Sparkles, label: "Optimized", desc: "AI code optimization" }
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

        {/* Right Side - Signup Form */}
        <div className="w-full lg:w-1/2 flex items-center justify-center px-4 py-12">
          <div className="w-full max-w-md space-y-8">
            <AnimatedSection className="text-center">
              <div className="space-y-2">
                <h1 className="text-foreground text-4xl font-semibold">
                  Create Account
                </h1>
                <p className="text-muted-foreground text-lg">
                  Start your AI development journey
                </p>
              </div>
            </AnimatedSection>

            <AnimatedSection delay={0.1} className="space-y-6">
              {/* GitHub OAuth Button */}
              <Button
                onClick={handleGithubSignupAlternative}
                disabled={isLoading}
                className="w-full bg-secondary text-secondary-foreground hover:bg-secondary/90 px-6 py-4 rounded-2xl font-medium shadow-lg flex items-center gap-3 text-lg h-auto"
              >
                {isLoading ? (
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-current" />
                ) : (
                  <Github className="h-6 w-6" />
                )}
                {isLoading ? "Creating Account..." : "Sign up with GitHub"}
              </Button>

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

              {/* Login Link */}
              <Link href="/login">
                <Button
                  variant="outline"
                  className="w-full border-border text-foreground hover:bg-accent hover:text-accent-foreground px-6 py-4 rounded-2xl font-medium text-lg h-auto flex items-center gap-2"
                >
                  <ArrowRight className="w-5 h-5" />
                  Sign in instead
                </Button>
              </Link>
            </AnimatedSection>

            <AnimatedSection delay={0.2} className="text-center">
              <p className="text-muted-foreground text-sm">
                By creating an account, you agree to our{" "}
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
                  { icon: Code, label: "AI-Powered" },
                  { icon: Zap, label: "Fast Deploy" },
                  { icon: Sparkles, label: "Optimized" }
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