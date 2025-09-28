"use client"

import { useEffect, useState } from "react"
import { useSession } from "next-auth/react"

export default function DebugAuthPage() {
  const { data: session, status } = useSession()
  const [envCheck, setEnvCheck] = useState<any>(null)

  useEffect(() => {
    // Check environment variables
    fetch('/api/test-auth')
      .then(res => res.json())
      .then(data => setEnvCheck(data))
      .catch(err => console.error('Error checking auth:', err))
  }, [])

  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-foreground mb-8">Auth Debug Information</h1>
        
        <div className="space-y-6">
          {/* Environment Variables */}
          <div className="bg-card p-6 rounded-lg border">
            <h2 className="text-xl font-semibold text-foreground mb-4">Environment Variables</h2>
            {envCheck ? (
              <div className="space-y-2">
                <div className="flex items-center space-x-2">
                  <span className="font-medium">GitHub Client ID:</span>
                  <span className={envCheck.environment?.hasGithubClientId ? "text-green-500" : "text-red-500"}>
                    {envCheck.environment?.hasGithubClientId ? "✅ Set" : "❌ Not Set"}
                  </span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="font-medium">GitHub Client Secret:</span>
                  <span className={envCheck.environment?.hasGithubClientSecret ? "text-green-500" : "text-red-500"}>
                    {envCheck.environment?.hasGithubClientSecret ? "✅ Set" : "❌ Not Set"}
                  </span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="font-medium">NextAuth Secret:</span>
                  <span className={envCheck.environment?.hasNextAuthSecret ? "text-green-500" : "text-red-500"}>
                    {envCheck.environment?.hasNextAuthSecret ? "✅ Set" : "❌ Not Set"}
                  </span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="font-medium">NextAuth URL:</span>
                  <span className="text-blue-500">{envCheck.environment?.nextAuthUrl || "Not Set"}</span>
                </div>
              </div>
            ) : (
              <p className="text-muted-foreground">Loading environment check...</p>
            )}
          </div>

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
              {session && (
                <div className="mt-4">
                  <h3 className="font-medium text-foreground mb-2">User Info:</h3>
                  <pre className="bg-muted p-4 rounded text-sm overflow-auto">
                    {JSON.stringify(session.user, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          </div>

          {/* Quick Actions */}
          <div className="bg-card p-6 rounded-lg border">
            <h2 className="text-xl font-semibold text-foreground mb-4">Quick Actions</h2>
            <div className="space-y-4">
              <div>
                <a 
                  href="/api/auth/signin/github" 
                  className="inline-block bg-primary text-primary-foreground px-4 py-2 rounded hover:bg-primary/90"
                >
                  Test GitHub Sign In
                </a>
              </div>
              <div>
                <a 
                  href="/api/auth/providers" 
                  className="inline-block bg-secondary text-secondary-foreground px-4 py-2 rounded hover:bg-secondary/90"
                  target="_blank"
                >
                  Check Available Providers
                </a>
              </div>
              <div>
                <a 
                  href="/api/auth/session" 
                  className="inline-block bg-accent text-accent-foreground px-4 py-2 rounded hover:bg-accent/90"
                  target="_blank"
                >
                  Check Session JSON
                </a>
              </div>
            </div>
          </div>

          {/* Error Information */}
          {envCheck?.error && (
            <div className="bg-red-500/10 border border-red-500/20 p-6 rounded-lg">
              <h2 className="text-xl font-semibold text-red-500 mb-4">Error</h2>
              <p className="text-red-400">{envCheck.error}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
