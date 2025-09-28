import { NextResponse } from "next/server"
import { auth } from "@/lib/auth"

export async function GET() {
  try {
    const session = await auth()
    
    return NextResponse.json({
      hasSession: !!session,
      session: session ? {
        user: session.user,
        expires: session.expires
      } : null,
      environment: {
        hasGithubClientId: !!process.env.GITHUB_CLIENT_ID,
        hasGithubClientSecret: !!process.env.GITHUB_CLIENT_SECRET,
        hasNextAuthSecret: !!process.env.NEXTAUTH_SECRET,
        nextAuthUrl: process.env.NEXTAUTH_URL
      }
    })
  } catch (error) {
    return NextResponse.json({
      error: error instanceof Error ? error.message : "Unknown error",
      hasSession: false,
      environment: {
        hasGithubClientId: !!process.env.GITHUB_CLIENT_ID,
        hasGithubClientSecret: !!process.env.GITHUB_CLIENT_SECRET,
        hasNextAuthSecret: !!process.env.NEXTAUTH_SECRET,
        nextAuthUrl: process.env.NEXTAUTH_URL
      }
    })
  }
}
