import { NextRequest, NextResponse } from "next/server";

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const redirect = searchParams.get("redirect") || "/cli";

    // GitHub OAuth configuration
    const clientId = process.env.GITHUB_CLIENT_ID;
    const redirectUri = `${process.env.NEXT_PUBLIC_APP_URL}/api/auth/github/callback`;

    if (!clientId) {
      return NextResponse.json(
        { error: "GitHub OAuth not configured" },
        { status: 500 }
      );
    }

    // Store redirect URL in session/cookie
    const response = NextResponse.redirect(
      `https://github.com/login/oauth/authorize?client_id=${clientId}&redirect_uri=${encodeURIComponent(
        redirectUri
      )}&scope=repo`
    );

    response.cookies.set("github_oauth_redirect", redirect, {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      maxAge: 600, // 10 minutes
    });

    return response;
  } catch (error: any) {
    console.error("GitHub OAuth error:", error);
    return NextResponse.json(
      { error: error.message || "OAuth failed" },
      { status: 500 }
    );
  }
}
