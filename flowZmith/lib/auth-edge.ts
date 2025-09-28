import { auth } from "@/lib/auth"
import type { NextRequest } from "next/server"

export async function getCurrentUser(request: NextRequest) {
  try {
    const session = await auth()
    return session?.user
  } catch (error) {
    console.error("Error getting current user:", error)
    return null
  }
}

export async function requireAuth(request: NextRequest) {
  const user = await getCurrentUser(request)
  if (!user) {
    throw new Error("Unauthorized")
  }
  return user
}