import { NextResponse } from "next/server"

export async function GET() {
  return NextResponse.json({
    message: "API is working",
    timestamp: new Date().toISOString(),
    environment: {
      hasGithubClientId: !!process.env.GITHUB_CLIENT_ID,
      hasGithubClientSecret: !!process.env.GITHUB_CLIENT_SECRET,
      hasNextAuthSecret: !!process.env.NEXTAUTH_SECRET,
      nextAuthUrl: process.env.NEXTAUTH_URL
    }
  })
}
