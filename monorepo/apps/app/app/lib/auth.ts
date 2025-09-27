import NextAuth from "next-auth"
import GitHub from "next-auth/providers/github"
import type { NextAuthConfig } from "next-auth"
import { userQueries } from "@/lib/db/queries"
import { userPlanQueries } from "@/lib/db/chat-queries"

// Debug environment variables
console.log("Auth Debug:", {
  hasGithubClientId: !!process.env.GITHUB_CLIENT_ID,
  hasGithubClientSecret: !!process.env.GITHUB_CLIENT_SECRET,
  hasNextAuthSecret: !!process.env.NEXTAUTH_SECRET,
  nextAuthUrl: process.env.NEXTAUTH_URL
})

export const config = {
  providers: [
    ...(process.env.GITHUB_CLIENT_ID && process.env.GITHUB_CLIENT_SECRET ? [
      GitHub({
        clientId: process.env.GITHUB_CLIENT_ID,
        clientSecret: process.env.GITHUB_CLIENT_SECRET,
      })
    ] : []),
  ],
  pages: {
    signIn: "/login",
  },
  callbacks: {
    authorized({ request, auth }) {
      const { pathname } = request.nextUrl
      if (pathname.startsWith("/dashboard")) return !!auth
      return true
    },
    async redirect({ url, baseUrl }) {
      if (url.startsWith("/")) return `${baseUrl}${url}`
      else if (new URL(url).origin === baseUrl) return url
      return baseUrl
    },
    async signIn({ user, account, profile }) {
      try {
        if (account?.provider === "github" && user.email) {
          // Check if user exists
          const existingUser = await userQueries.findByEmail(user.email)
          
          if (!existingUser) {
            // New user - create account with 10 free credits
            console.log("Creating new user with 10 free credits:", user.email)
            
            const newUser = await userQueries.create({
              email: user.email,
              name: user.name || profile?.name,
              image: user.image || (profile?.avatar_url as string),
              githubId: (profile?.id as string) || null,
              plan: 'free',
              requestsUsed: 0,
              requestsLimit: 10, // 10 free credits
              isActive: true,
              lastLoginAt: new Date()
            })

            // Create free plan for new user
            await userPlanQueries.upsert(newUser.id, {
              userId: newUser.id,
              planName: 'free',
              monthlyRequests: 10,
              dailyRequests: 10,
              maxTokensPerRequest: 2000,
              features: ['basic_chat', 'code_generation'],
              isActive: true,
              pricePerMonth: 0,
              billingCycle: 'monthly'
            })

            console.log("New user created with 10 free credits:", newUser.id)
          } else {
            // Existing user - update login time
            await userQueries.update(existingUser.id, {
              lastLoginAt: new Date(),
              isActive: true
            })
            console.log("Existing user login:", existingUser.email)
          }
        }
        return true
      } catch (error) {
        console.error("Error in signIn callback:", error)
        return true // Allow sign in even if database operation fails
      }
    },
    async jwt({ token, user, account, profile }) {
      if (user) {
        token.id = user.id
        token.email = user.email
        token.name = user.name
        token.image = user.image
        token.githubId = profile?.id
      }
      return token
    },
    async session({ session, token }) {
      if (token) {
        session.user.id = token.id as string
        session.user.email = token.email as string
        session.user.name = token.name as string
        session.user.image = token.image as string
        session.user.githubId = token.githubId as string
      }
      return session
    },
  },
} satisfies NextAuthConfig

export const { handlers, signIn, signOut, auth } = NextAuth(config)