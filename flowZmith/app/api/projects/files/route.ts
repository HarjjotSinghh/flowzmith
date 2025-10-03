import { NextRequest, NextResponse } from "next/server";
import fs from "fs/promises";
import path from "path";

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const projectPath = searchParams.get("path");

    if (!projectPath) {
      return NextResponse.json(
        { error: "Project path is required" },
        { status: 400 }
      );
    }

    // Clean the path and resolve it
    const cleanPath = projectPath.replace(/^\/+/, ''); // Remove leading slashes
    const fullPath = path.resolve(process.cwd(), "../", cleanPath);

    // Security check: ensure path is within allowed directory
    const allowedBase = path.resolve(process.cwd(), "../flow_projects");
    if (!fullPath.startsWith(allowedBase)) {
      console.error(`Access denied: ${fullPath} is not within ${allowedBase}`);
      return NextResponse.json(
        { error: "Access denied" },
        { status: 403 }
      );
    }

    // Check if directory exists
    try {
      await fs.access(fullPath);
    } catch (error) {
      console.error(`Project not found at: ${fullPath}`, error);
      return NextResponse.json(
        { error: "Project not found", path: fullPath },
        { status: 404 }
      );
    }

    // Recursively read all files
    const files: any[] = [];

    async function readDirectory(dirPath: string, relativePath: string = "") {
      const entries = await fs.readdir(dirPath, { withFileTypes: true });

      for (const entry of entries) {
        const entryPath = path.join(dirPath, entry.name);
        const entryRelativePath = path.join(relativePath, entry.name);

        if (entry.isDirectory()) {
          files.push({
            name: entry.name,
            path: entryRelativePath,
            type: "directory",
          });
          await readDirectory(entryPath, entryRelativePath);
        } else {
          const content = await fs.readFile(entryPath, "utf-8");
          files.push({
            name: entry.name,
            path: entryRelativePath,
            type: "file",
            content,
          });
        }
      }
    }

    await readDirectory(fullPath);

    return NextResponse.json({ files });
  } catch (error: any) {
    console.error("Error fetching project files:", error);
    return NextResponse.json(
      { error: error.message || "Failed to fetch project files" },
      { status: 500 }
    );
  }
}
