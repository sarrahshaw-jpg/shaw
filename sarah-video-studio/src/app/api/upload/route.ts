import { NextRequest, NextResponse } from "next/server";
import { writeFile } from "fs/promises";
import path from "path";
import { v4 as uuidv4 } from "uuid";
import fs from "fs";

export async function POST(req: NextRequest) {
  try {
    const data = await req.formData();
    const file: File | null = data.get("file") as unknown as File;

    if (!file) {
      return NextResponse.json({ success: false, error: "No file uploaded" }, { status: 400 });
    }

    const bytes = await file.arrayBuffer();
    const buffer = Buffer.from(bytes);

    const videoId = uuidv4();
    const uploadDir = path.join(process.cwd(), "media", "uploads");
    
    if (!fs.existsSync(uploadDir)) {
      fs.mkdirSync(uploadDir, { recursive: true });
    }

    const filepath = path.join(uploadDir, `${videoId}.mp4`);
    await writeFile(filepath, buffer);

    // Normally here we would trigger the asynchronous AI Agent to start processing.
    // For this prototype, we return the ID to the client, which navigates to the editor.

    return NextResponse.json({ success: true, videoId });
  } catch (error) {
    console.error("Upload error:", error);
    return NextResponse.json({ success: false, error: "Failed to upload file" }, { status: 500 });
  }
}
