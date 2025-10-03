import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  try {
    const accessToken = request.cookies.get("github_access_token")?.value;

    if (!accessToken) {
      return NextResponse.json(
        { error: "Not authenticated with GitHub" },
        { status: 401 }
      );
    }

    const body = await request.json();
    const { repo_name, description, files, is_private = false } = body;

    if (!repo_name || !files) {
      return NextResponse.json(
        { error: "Repository name and files are required" },
        { status: 400 }
      );
    }

    // Create repository
    const createRepoResponse = await fetch(
      "https://api.github.com/user/repos",
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${accessToken}`,
          "Content-Type": "application/json",
          Accept: "application/vnd.github.v3+json",
        },
        body: JSON.stringify({
          name: repo_name,
          description: description || "Flow smart contract project",
          private: is_private,
          auto_init: true,
        }),
      }
    );

    if (!createRepoResponse.ok) {
      const error = await createRepoResponse.json();
      return NextResponse.json(
        { error: error.message || "Failed to create repository" },
        { status: createRepoResponse.status }
      );
    }

    const repoData = await createRepoResponse.json();

    // Upload files to repository
    const uploadPromises = files.map(async (file: any) => {
      const content = Buffer.from(file.content).toString("base64");

      return fetch(
        `https://api.github.com/repos/${repoData.full_name}/contents/${file.path}`,
        {
          method: "PUT",
          headers: {
            Authorization: `Bearer ${accessToken}`,
            "Content-Type": "application/json",
            Accept: "application/vnd.github.v3+json",
          },
          body: JSON.stringify({
            message: `Add ${file.path}`,
            content,
          }),
        }
      );
    });

    await Promise.all(uploadPromises);

    return NextResponse.json({
      success: true,
      repo_url: repoData.html_url,
      repo_name: repoData.full_name,
    });
  } catch (error: any) {
    console.error("GitHub repo creation error:", error);
    return NextResponse.json(
      { error: error.message || "Failed to create repository" },
      { status: 500 }
    );
  }
}
