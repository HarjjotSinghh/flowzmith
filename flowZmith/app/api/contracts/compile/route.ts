import { NextRequest, NextResponse } from "next/server";
import { exec } from "child_process";
import { promisify } from "util";
import fs from "fs/promises";
import path from "path";
import os from "os";

const execAsync = promisify(exec);

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { contract_code, contract_name } = body;

    if (!contract_code) {
      return NextResponse.json(
        { error: "Contract code is required" },
        { status: 400 }
      );
    }

    // Create a temporary file for compilation
    const tempDir = await fs.mkdtemp(path.join(os.tmpdir(), "flow-compile-"));
    const contractFile = path.join(tempDir, `${contract_name || "Contract"}.cdc`);

    try {
      // Write contract to temp file
      await fs.writeFile(contractFile, contract_code);

      // Try to compile using Flow CLI
      try {
        const { stdout, stderr } = await execAsync(
          `flow cadence check ${contractFile}`,
          { cwd: tempDir }
        );

        // Clean up
        await fs.rm(tempDir, { recursive: true, force: true });

        return NextResponse.json({
          success: true,
          message: "Contract compiled successfully",
          output: stdout,
          warnings: stderr ? stderr.split("\n").filter(Boolean) : [],
        });
      } catch (execError: any) {
        // Clean up
        await fs.rm(tempDir, { recursive: true, force: true });

        return NextResponse.json(
          {
            success: false,
            error: "Compilation failed",
            message: execError.stderr || execError.message,
          },
          { status: 400 }
        );
      }
    } catch (error: any) {
      // Clean up on error
      try {
        await fs.rm(tempDir, { recursive: true, force: true });
      } catch {}

      throw error;
    }
  } catch (error: any) {
    console.error("Compilation error:", error);
    return NextResponse.json(
      { error: error.message || "Compilation failed" },
      { status: 500 }
    );
  }
}
