import { NextRequest, NextResponse } from "next/server";

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const code = searchParams.get("code");

    if (!code) {
      return NextResponse.redirect("/cli?error=github_auth_failed");
    }

    // Exchange code for access token
    const tokenResponse = await fetch(
      "https://github.com/login/oauth/access_token",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify({
          client_id: process.env.GITHUB_CLIENT_ID,
          client_secret: process.env.GITHUB_CLIENT_SECRET,
          code,
        }),
      }
    );

    const tokenData = await tokenResponse.json();

    if (tokenData.error || !tokenData.access_token) {
      return NextResponse.redirect("/cli?error=github_token_failed");
    }

    // Get redirect URL from cookie
    const redirectUrl =
      request.cookies.get("github_oauth_redirect")?.value || "/cli";

    // Store access token in session/cookie
    const response = NextResponse.redirect(
      `${process.env.NEXT_PUBLIC_APP_URL}${redirectUrl}?github_connected=true`
    );

    response.cookies.set("github_access_token", tokenData.access_token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      maxAge: 60 * 60 * 24 * 30, // 30 days
    });

    response.cookies.delete("github_oauth_redirect");

    return response;
  } catch (error: any) {
    console.error("GitHub OAuth callback error:", error);
    return NextResponse.redirect("/cli?error=github_callback_failed");
  }
}
