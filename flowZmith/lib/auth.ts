import NextAuth from "next-auth"
import GitHub from "next-auth/providers/github"
import type { NextAuthConfig } from "next-auth"
import { userQueries } from "@/lib/db/queries"

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
          console.log("GitHub sign-in for:", user.email)
          // Database operations will be handled by API routes
          // This makes the auth config Edge Runtime compatible
        }
        return true
      } catch (error) {
        console.error("Error in signIn callback:", error)
        return true
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
        session.user.id = token.id as string;
        session.user.email = token.email as string;
        session.user.name = token.name as string;
        session.user.image = token.image as string;
        session.user.githubId = token.githubId as string;

        // Fetch user data from database to get requestsLimit
        // Gracefully handle errors to prevent session creation from failing
        try {
          if (session.user.email) {
            const userData = await userQueries.findByEmail(session.user.email);
            if (userData) {
              session.user.requestsLimit = userData.requestsLimit || 0;
            } else {
              // Set default if user not found
              session.user.requestsLimit = 0;
            }
          }
        } catch (error) {
          console.error("Error fetching user data for session:", error);
          // Set default on error to prevent session failure
          session.user.requestsLimit = 0;
        }
      }
      return session
    },
  },
} satisfies NextAuthConfig

export const { handlers, signIn, signOut, auth } = NextAuth(config)