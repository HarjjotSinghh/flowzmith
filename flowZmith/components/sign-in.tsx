
"use client"

import { signIn } from "next-auth/react"
import { Button } from "@/components/ui/button"
import { Github } from "lucide-react"

export default function SignIn() {
  return (
    <Button
      onClick={() => signIn("github", { callbackUrl: "/dashboard" })}
      className="w-full bg-secondary text-secondary-foreground hover:bg-secondary/90 px-6 py-4 rounded-2xl font-medium shadow-lg flex items-center gap-3 text-lg h-auto"
    >
      <Github className="h-6 w-6" />
      Continue with GitHub
    </Button>
  )
}