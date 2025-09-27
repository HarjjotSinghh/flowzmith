"use client"

import { useSession } from "next-auth/react"
import { Button } from "@/components/ui/button"
import { signOut } from "next-auth/react"
import Link from "next/link"

export default function TestAuthPage() {
  const { data: session, status } = useSession()

  if (status === "loading") {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-foreground mb-8">Authentication Test</h1>
        
        <div className="space-y-6">
          {/* Session Status */}
          <div className="bg-card p-6 rounded-lg border">
            <h2 className="text-xl font-semibold text-foreground mb-4">Session Status</h2>
            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <span className="font-medium">Status:</span>
                <span className={status === "authenticated" ? "text-green-500" : status === "loading" ? "text-yellow-500" : "text-red-500"}>
                  {status}
                </span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="font-medium">Has Session:</span>
                <span className={session ? "text-green-500" : "text-red-500"}>
                  {session ? "✅ Yes" : "❌ No"}
                </span>
              </div>
            </div>
          </div>

          {/* User Information */}
          {session && (
            <div className="bg-card p-6 rounded-lg border">
              <h2 className="text-xl font-semibold text-foreground mb-4">User Information</h2>
              <div className="space-y-2">
                <div className="flex items-center space-x-2">
                  <span className="font-medium">Name:</span>
                  <span>{session.user?.name}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="font-medium">Email:</span>
                  <span>{session.user?.email}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="font-medium">Image:</span>
                  <span>{session.user?.image ? "✅ Available" : "❌ Not available"}</span>
                </div>
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="bg-card p-6 rounded-lg border">
            <h2 className="text-xl font-semibold text-foreground mb-4">Actions</h2>
            <div className="space-y-4">
              {!session ? (
                <div className="space-y-2">
                  <p className="text-muted-foreground">You are not signed in.</p>
                  <Link href="/login">
                    <Button>Go to Login</Button>
                  </Link>
                </div>
              ) : (
                <div className="space-y-2">
                  <p className="text-green-500">You are signed in!</p>
                  <div className="flex space-x-4">
                    <Link href="/dashboard">
                      <Button>Go to Dashboard</Button>
                    </Link>
                    <Button 
                      variant="outline" 
                      onClick={() => signOut({ callbackUrl: "/login" })}
                    >
                      Sign Out
                    </Button>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* API Endpoints */}
          <div className="bg-card p-6 rounded-lg border">
            <h2 className="text-xl font-semibold text-foreground mb-4">API Endpoints</h2>
            <div className="space-y-2">
              <div>
                <a 
                  href="/api/auth/session" 
                  className="text-primary hover:underline"
                  target="_blank"
                >
                  /api/auth/session
                </a>
                <span className="text-muted-foreground ml-2">- Check session data</span>
              </div>
              <div>
                <a 
                  href="/api/auth/providers" 
                  className="text-primary hover:underline"
                  target="_blank"
                >
                  /api/auth/providers
                </a>
                <span className="text-muted-foreground ml-2">- Check available providers</span>
              </div>
              <div>
                <a 
                  href="/api/auth/signin/github" 
                  className="text-primary hover:underline"
                  target="_blank"
                >
                  /api/auth/signin/github
                </a>
                <span className="text-muted-foreground ml-2">- Direct GitHub sign-in</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
