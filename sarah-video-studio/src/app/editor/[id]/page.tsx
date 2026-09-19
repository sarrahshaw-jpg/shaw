"use client";

import { useState, useEffect, use } from "react";
import { Play, Pause, SkipBack, MessageSquare, Scissor, Type, Zap, Image as ImageIcon, Volume2, Music, Check, Download, RotateCcw, Settings2 } from "lucide-react";
import { useRouter } from "next/navigation";

export default function EditorPage({ params }: { params: Promise<{ id: string }> }) {
  const resolvedParams = use(params);
  const videoId = resolvedParams.id;
  const isDemo = videoId.startsWith("demo-");
  
  const [isPlaying, setIsPlaying] = useState(false);
  const [viewMode, setViewMode] = useState<"preview" | "comparison">("preview");
  const [prompt, setPrompt] = useState("");
  const [isProcessingAI, setIsProcessingAI] = useState(false);
  const [agentLog, setAgentLog] = useState<{role: string, msg: string}[]>([
    { role: "agent", msg: "I've analyzed the raw video. I removed 4 filler words, cut 2 long pauses, added 3 semantic zooms on your key statements, and generated clean captions. How does it look?" }
  ]);

  const handleCommand = (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) return;
    
    setAgentLog(prev => [...prev, { role: "user", msg: prompt }]);
    setIsProcessingAI(true);
    
    // Simulate Agent processing
    setTimeout(() => {
      setAgentLog(prev => [...prev, { 
        role: "agent", 
        msg: `Understood. Applying: "${prompt}". I've updated the editing decision list (EDL). The timeline has been refreshed.`
      }]);
      setIsProcessingAI(false);
      setPrompt("");
    }, 2000);
  };

  return (
    <div className="flex h-screen bg-black text-white flex-col overflow-hidden font-sans">
      {/* HEADER */}
      <header className="h-14 border-b border-gray-800 flex items-center justify-between px-6 bg-gray-950">
        <div className="flex items-center gap-4">
          <div className="font-semibold tracking-wide text-sm">SARAH <span className="text-blue-500">STUDIO</span></div>
          <div className="h-4 w-px bg-gray-700"></div>
          <div className="text-xs text-gray-400 font-mono">PROJECT: {isDemo ? "DEMO_PROJECT" : videoId}</div>
          {isDemo && <span className="bg-blue-900 text-blue-200 text-[10px] px-2 py-0.5 rounded font-bold uppercase tracking-wider">Demo Mode</span>}
        </div>
        <div className="flex items-center gap-3">
          <button className="text-xs bg-gray-800 hover:bg-gray-700 px-3 py-1.5 rounded flex items-center gap-2 transition">
            <Settings2 className="w-3.5 h-3.5" /> Style Profile
          </button>
          <button className="text-xs bg-blue-600 hover:bg-blue-500 font-medium px-4 py-1.5 rounded flex items-center gap-2 transition">
            <Check className="w-3.5 h-3.5" /> Approve & Export
          </button>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden">
        {/* LEFT PANEL - AI Agent Chat & Controls */}
        <div className="w-80 border-r border-gray-800 flex flex-col bg-gray-950">
          <div className="p-4 border-b border-gray-800 bg-gray-900/50">
            <h2 className="text-sm font-semibold mb-1 flex items-center gap-2">
              <Zap className="w-4 h-4 text-blue-400" /> AI Co-Pilot
            </h2>
            <p className="text-xs text-gray-400">Direct the agent using natural language.</p>
          </div>
          
          <div className="flex-1 p-4 overflow-y-auto flex flex-col gap-4">
            {agentLog.map((log, i) => (
              <div key={i} className={`flex flex-col ${log.role === 'user' ? 'items-end' : 'items-start'}`}>
                <div className={`text-xs px-3 py-2 rounded-xl max-w-[90%] ${
                  log.role === 'user' 
                    ? 'bg-blue-600 text-white rounded-br-none' 
                    : 'bg-gray-800 text-gray-200 rounded-bl-none'
                }`}>
                  {log.msg}
                </div>
              </div>
            ))}
            {isProcessingAI && (
              <div className="flex items-start">
                <div className="text-xs px-3 py-2 rounded-xl bg-gray-800 text-gray-400 rounded-bl-none flex items-center gap-2">
                  <div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce"></div>
                  <div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce delay-100"></div>
                  <div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce delay-200"></div>
                </div>
              </div>
            )}
          </div>

          <div className="p-4 border-t border-gray-800 bg-gray-900/50">
            <form onSubmit={handleCommand} className="relative">
              <input 
                type="text" 
                value={prompt}
                onChange={e => setPrompt(e.target.value)}
                placeholder="e.g. Make this more cinematic..."
                className="w-full bg-gray-950 border border-gray-700 rounded-lg pl-3 pr-10 py-2.5 text-sm focus:outline-none focus:border-blue-500 transition"
              />
              <button 
                type="submit"
                className="absolute right-2 top-2 bottom-2 bg-blue-600 hover:bg-blue-500 text-white rounded p-1.5 flex items-center justify-center transition disabled:opacity-50"
                disabled={isProcessingAI || !prompt.trim()}
              >
                <MessageSquare className="w-3.5 h-3.5" />
              </button>
            </form>
            <div className="flex flex-wrap gap-1 mt-2">
              <button onClick={() => setPrompt("Remove fillers")} className="text-[10px] bg-gray-800 hover:bg-gray-700 px-2 py-1 rounded text-gray-300">Remove fillers</button>
              <button onClick={() => setPrompt("Add b-roll")} className="text-[10px] bg-gray-800 hover:bg-gray-700 px-2 py-1 rounded text-gray-300">Add b-roll</button>
              <button onClick={() => setPrompt("Less zooms")} className="text-[10px] bg-gray-800 hover:bg-gray-700 px-2 py-1 rounded text-gray-300">Less zooms</button>
            </div>
          </div>
        </div>

        {/* CENTER PANEL - Video Preview */}
        <div className="flex-1 flex flex-col relative bg-[#050505]">
          <div className="absolute top-4 right-4 z-10 flex bg-gray-900 rounded-lg p-1 border border-gray-700">
            <button 
              onClick={() => setViewMode("preview")}
              className={`text-xs px-3 py-1 rounded ${viewMode === 'preview' ? 'bg-gray-700 text-white' : 'text-gray-400 hover:text-white'}`}
            >
              Final Edit
            </button>
            <button 
              onClick={() => setViewMode("comparison")}
              className={`text-xs px-3 py-1 rounded ${viewMode === 'comparison' ? 'bg-gray-700 text-white' : 'text-gray-400 hover:text-white'}`}
            >
              Compare Original
            </button>
          </div>

          <div className="flex-1 flex items-center justify-center p-8 overflow-hidden">
            {/* Mock Video Player */}
            <div className="relative aspect-[9/16] h-full max-h-[70vh] bg-gray-900 rounded-lg overflow-hidden border border-gray-800 shadow-2xl flex items-center justify-center">
              
              {/* Simulate the video frame */}
              <div className="absolute inset-0 bg-gradient-to-b from-gray-800 to-black flex flex-col items-center justify-center p-6 text-center">
                <div className="w-24 h-24 bg-gray-700 rounded-full mb-4 flex items-center justify-center opacity-50">
                   {/* Placeholder for Face/Subject */}
                   <span className="text-4xl text-gray-500">👤</span>
                </div>
                <div className="text-gray-500 text-xs mt-auto pb-12 font-mono">
                  [9:16 VERTICAL RENDER ENGINE]
                </div>
              </div>

              {/* Mock Captions */}
              <div className="absolute bottom-16 left-0 right-0 px-8 text-center">
                <span className="bg-black/70 text-white text-lg font-bold px-3 py-1.5 rounded-lg leading-snug inline-block">
                  Your brain remembers <span className="text-yellow-400">emotional peaks</span>.
                </span>
              </div>

              {/* Center Play Button Overlay if paused */}
              {!isPlaying && (
                <div className="absolute inset-0 bg-black/40 flex items-center justify-center">
                  <button onClick={() => setIsPlaying(true)} className="bg-white/10 hover:bg-white/20 p-4 rounded-full backdrop-blur transition">
                    <Play className="w-8 h-8 text-white ml-1" />
                  </button>
                </div>
              )}
            </div>
            
            {viewMode === 'comparison' && (
              <div className="relative aspect-[9/16] h-full max-h-[70vh] bg-gray-900 rounded-lg overflow-hidden border border-gray-800 shadow-2xl flex items-center justify-center ml-4 opacity-50 grayscale">
                <div className="absolute top-2 left-2 bg-black/50 text-[10px] px-2 py-1 rounded">ORIGINAL</div>
                <div className="absolute inset-0 flex flex-col items-center justify-center p-6 text-center">
                  <div className="w-24 h-24 bg-gray-700 rounded-full mb-4 flex items-center justify-center">
                    <span className="text-4xl text-gray-500">👤</span>
                  </div>
                  <div className="text-gray-600 text-xs mt-auto pb-12 font-mono">
                    [RAW LOG FOOTAGE]
                  </div>
                </div>
              </div>
            )}
          </div>
          
          {/* Timeline / Scrub Bar */}
          <div className="h-48 border-t border-gray-800 bg-gray-900 flex flex-col">
            <div className="flex items-center justify-between px-4 py-2 border-b border-gray-800 bg-gray-950">
              <div className="flex items-center gap-3">
                <button onClick={() => setIsPlaying(!isPlaying)} className="hover:text-blue-400 transition">
                  {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                </button>
                <button className="hover:text-blue-400 transition">
                  <SkipBack className="w-4 h-4" />
                </button>
                <span className="text-xs font-mono text-gray-400">00:00:12 / 00:00:45</span>
              </div>
              <div className="flex gap-2">
                <button className="text-[10px] bg-gray-800 hover:bg-gray-700 px-2 py-1 rounded flex items-center gap-1"><Scissor className="w-3 h-3" /> CUTS</button>
                <button className="text-[10px] bg-blue-900/40 text-blue-300 hover:bg-blue-900/60 px-2 py-1 rounded flex items-center gap-1"><Type className="w-3 h-3" /> CAPTIONS</button>
                <button className="text-[10px] bg-gray-800 hover:bg-gray-700 px-2 py-1 rounded flex items-center gap-1"><ImageIcon className="w-3 h-3" /> B-ROLL</button>
              </div>
            </div>

            {/* Timeline UI Mock */}
            <div className="flex-1 p-4 relative overflow-x-auto">
              <div className="w-[800px] h-full flex flex-col gap-1 relative">
                
                {/* Playhead */}
                <div className="absolute left-[200px] top-0 bottom-0 w-px bg-red-500 z-20">
                  <div className="w-3 h-3 bg-red-500 absolute -top-1.5 -left-1.5 rounded-sm"></div>
                </div>

                {/* Track: Video */}
                <div className="h-8 bg-gray-800 rounded flex overflow-hidden border border-gray-700 items-center">
                  <div className="w-12 h-full border-r border-gray-700 flex items-center justify-center bg-gray-900 text-gray-500">
                    <Video className="w-3 h-3" />
                  </div>
                  <div className="flex-1 flex gap-0.5 p-0.5">
                    <div className="w-32 h-full bg-blue-900/50 rounded-sm"></div>
                    <div className="w-4 h-full bg-red-900/50 rounded-sm relative group cursor-help">
                       <span className="hidden group-hover:block absolute -top-6 left-0 bg-black text-[9px] px-1 py-0.5 whitespace-nowrap z-30">AI Removed Pause</span>
                    </div>
                    <div className="w-48 h-full bg-blue-800/50 rounded-sm border-t-2 border-yellow-500 relative group">
                       <span className="hidden group-hover:block absolute -top-6 left-0 bg-black text-[9px] px-1 py-0.5 whitespace-nowrap z-30">110% Zoom applied</span>
                    </div>
                    <div className="w-64 h-full bg-blue-900/50 rounded-sm"></div>
                  </div>
                </div>

                {/* Track: Audio */}
                <div className="h-8 bg-gray-800 rounded flex overflow-hidden border border-gray-700 items-center mt-1">
                  <div className="w-12 h-full border-r border-gray-700 flex items-center justify-center bg-gray-900 text-gray-500">
                    <Volume2 className="w-3 h-3" />
                  </div>
                  <div className="flex-1 px-1 flex items-center">
                    {/* Simulated Waveform */}
                    <div className="w-full h-4 flex items-end gap-[1px] opacity-70">
                      {Array.from({length: 100}).map((_, i) => (
                        <div key={i} className="w-1 bg-green-500/60" style={{ height: \`\${Math.random() * 100}%\` }}></div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Track: Captions & Text */}
                <div className="h-6 bg-gray-800 rounded flex overflow-hidden border border-gray-700 items-center mt-1">
                  <div className="w-12 h-full border-r border-gray-700 flex items-center justify-center bg-gray-900 text-gray-500">
                    <Type className="w-3 h-3" />
                  </div>
                  <div className="flex-1 flex gap-1 p-0.5 text-[8px] font-mono overflow-hidden">
                    <div className="w-16 h-full bg-purple-900/60 rounded flex items-center px-1 truncate border border-purple-700">Did you know...</div>
                    <div className="w-24 h-full bg-purple-900/60 rounded flex items-center px-1 truncate border border-purple-700">Your brain remembers...</div>
                    <div className="w-20 h-full bg-yellow-900/60 rounded flex items-center px-1 truncate border border-yellow-700 font-bold">EMOTIONAL PEAKS.</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
