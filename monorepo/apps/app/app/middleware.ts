import { auth } from "@/lib/auth"
import { NextResponse } from "next/server"

export default auth((req) => {
  const { nextUrl } = req
  const isLoggedIn = !!req.auth

  // Protect dashboard and chat routes
  if (nextUrl.pathname.startsWith("/dashboard") || nextUrl.pathname.startsWith("/chat")) {
    if (isLoggedIn) return NextResponse.next()
    return NextResponse.redirect(new URL("/login", nextUrl))
  }

  return NextResponse.next()
})

export const config = {
  matcher: ["/dashboard/:path*", "/chat/:path*"]
}
