import Link from "next/link";
import { Upload, Film, Settings, Activity } from "lucide-react";

export default function Home() {
  return (
    <main className="min-h-screen p-8 max-w-6xl mx-auto flex flex-col gap-8">
      <header className="flex justify-between items-center border-b border-gray-800 pb-6">
        <div>
          <h1 className="text-3xl font-light tracking-tight">SARAH <span className="font-semibold text-blue-500">STUDIO AI</span></h1>
          <p className="text-gray-400 mt-1 text-sm">Intelligent Post-Production Agent</p>
        </div>
        <nav className="flex gap-4">
          <Link href="/library" className="text-sm text-gray-400 hover:text-white transition">Library</Link>
          <Link href="/settings" className="text-sm text-gray-400 hover:text-white transition">Profile</Link>
        </nav>
      </header>

      <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mt-4">
        <Link href="/upload" className="bg-gray-900 border border-gray-800 rounded-xl p-6 flex flex-col items-center justify-center gap-3 hover:bg-gray-800 transition group cursor-pointer h-48">
          <div className="bg-blue-500/10 p-4 rounded-full group-hover:scale-110 transition">
            <Upload className="w-8 h-8 text-blue-500" />
          </div>
          <span className="font-medium">Upload New Video</span>
        </Link>

        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 flex flex-col items-center justify-center gap-3 h-48 opacity-75">
          <div className="bg-purple-500/10 p-4 rounded-full">
            <Film className="w-8 h-8 text-purple-500" />
          </div>
          <span className="font-medium">Recent Edits</span>
          <p className="text-xs text-gray-500">2 pending review</p>
        </div>

        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 flex flex-col items-center justify-center gap-3 h-48 opacity-75">
          <div className="bg-green-500/10 p-4 rounded-full">
            <Settings className="w-8 h-8 text-green-500" />
          </div>
          <span className="font-medium">Editing Style</span>
          <p className="text-xs text-gray-500">Sarah Signature Active</p>
        </div>

        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 flex flex-col items-center justify-center gap-3 h-48 opacity-75">
          <div className="bg-orange-500/10 p-4 rounded-full">
            <Activity className="w-8 h-8 text-orange-500" />
          </div>
          <span className="font-medium">Agent Status</span>
          <p className="text-xs text-green-500">Online & Ready</p>
        </div>
      </section>

      <section className="mt-8">
        <h2 className="text-xl font-medium mb-4">How it works</h2>
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 space-y-4 text-sm text-gray-300">
          <p>1. <strong>Upload</strong> raw talking-head footage (MP4, MOV).</p>
          <p>2. <strong>AI Analyzes</strong> speech, pauses, hooks, and lighting.</p>
          <p>3. <strong>Agent Edits</strong> the video using the "Sarah Signature" style (cuts, zooms, captions, b-roll).</p>
          <p>4. <strong>Review & Command</strong> using natural language (e.g. <em>"Make this more cinematic"</em>).</p>
          <p>5. <strong>Export</strong> to TikTok, Reels, Shorts, and LinkedIn formats.</p>
        </div>
      </section>
    </main>
  );
}
