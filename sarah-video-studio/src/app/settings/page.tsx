"use client";
import { useState } from "react";
import { Save, Check } from "lucide-react";

export default function SettingsPage() {
  const [saved, setSaved] = useState(false);
  const [style, setStyle] = useState({
    profile: "SARAH_SIGNATURE",
    captions: "minimalist_bold",
    zoom: "subtle",
    music: -24,
    color: "cinematic_warm",
    pacing: "dynamic_human"
  });

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="min-h-screen p-8 max-w-4xl mx-auto flex flex-col gap-8 text-gray-200">
      <header className="border-b border-gray-800 pb-6">
        <h1 className="text-2xl font-light">Editing Profile & Style Memory</h1>
        <p className="text-gray-400 mt-1">The AI Agent will automatically apply these settings to all new videos.</p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="space-y-6 bg-gray-900 border border-gray-800 p-6 rounded-xl">
          <h2 className="text-lg font-medium text-white mb-4">Core Preferences</h2>
          
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-400">Default Preset</label>
            <select 
              value={style.profile}
              onChange={e => setStyle({...style, profile: e.target.value})}
              className="w-full bg-gray-950 border border-gray-700 rounded-lg p-2.5 text-sm focus:border-blue-500 outline-none"
            >
              <option value="SARAH_SIGNATURE">Sarah Signature</option>
              <option value="SARAH_PROFESSIONAL">Sarah Professional (LinkedIn)</option>
              <option value="SARAH_EDUCATIONAL">Sarah Educational</option>
              <option value="SARAH_CINEMATIC">Sarah Cinematic</option>
            </select>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-400">Pacing & Rhythm</label>
            <select 
              value={style.pacing}
              onChange={e => setStyle({...style, pacing: e.target.value})}
              className="w-full bg-gray-950 border border-gray-700 rounded-lg p-2.5 text-sm focus:border-blue-500 outline-none"
            >
              <option value="dynamic_human">Dynamic but Human (Keep Natural Pauses)</option>
              <option value="fast">Aggressive (Remove all dead air)</option>
              <option value="measured">Measured (Slower, professional)</option>
            </select>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-400">Dynamic Zoom Intensity</label>
            <select 
              value={style.zoom}
              onChange={e => setStyle({...style, zoom: e.target.value})}
              className="w-full bg-gray-950 border border-gray-700 rounded-lg p-2.5 text-sm focus:border-blue-500 outline-none"
            >
              <option value="subtle">Subtle Semantic Punches (1.10x)</option>
              <option value="none">Disabled (Static Cam)</option>
              <option value="high">High Frequency</option>
            </select>
          </div>
        </div>

        <div className="space-y-6 bg-gray-900 border border-gray-800 p-6 rounded-xl">
          <h2 className="text-lg font-medium text-white mb-4">Aesthetic</h2>
          
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-400">Caption Style</label>
            <select 
              value={style.captions}
              onChange={e => setStyle({...style, captions: e.target.value})}
              className="w-full bg-gray-950 border border-gray-700 rounded-lg p-2.5 text-sm focus:border-blue-500 outline-none"
            >
              <option value="minimalist_bold">Minimalist Bold (Semantic Emphasis)</option>
              <option value="clean_lower_third">Clean Lower Third</option>
              <option value="karaoke">Karaoke Word-by-Word</option>
            </select>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-400">Color & Lighting</label>
            <select 
              value={style.color}
              onChange={e => setStyle({...style, color: e.target.value})}
              className="w-full bg-gray-950 border border-gray-700 rounded-lg p-2.5 text-sm focus:border-blue-500 outline-none"
            >
              <option value="cinematic_warm">Cinematic Warm (Studio Polish)</option>
              <option value="neutral">Neutral & True</option>
              <option value="high_contrast">High Contrast</option>
            </select>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-400">Background Music Level (dB)</label>
            <input 
              type="range" 
              min="-40" 
              max="0" 
              value={style.music}
              onChange={e => setStyle({...style, music: parseInt(e.target.value)})}
              className="w-full"
            />
            <div className="text-xs text-right text-gray-500">{style.music} dB</div>
          </div>
        </div>
      </div>

      <div className="flex justify-end">
        <button 
          onClick={handleSave}
          className="bg-blue-600 hover:bg-blue-500 text-white px-8 py-3 rounded-full font-medium transition flex items-center gap-2"
        >
          {saved ? <><Check className="w-5 h-5" /> Saved</> : <><Save className="w-5 h-5" /> Save Profile</>}
        </button>
      </div>
    </div>
  );
}
