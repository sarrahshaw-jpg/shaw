"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { Upload as UploadIcon, Video, AlertCircle, Loader } from "lucide-react";

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const router = useRouter();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);

    // Create a form data object
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("/api/upload", {
        method: "POST",
        body: formData,
      });
      
      const data = await res.json();
      
      if (data.videoId) {
        router.push(`/editor/${data.videoId}`);
      } else {
        alert("Upload failed. Are you in Demo Mode?");
        // Fallback for demo
        router.push(`/editor/demo-123`);
      }
    } catch (err) {
      console.error(err);
      router.push(`/editor/demo-123`); // Fallback to demo mode
    }
  };

  return (
    <div className="min-h-screen p-8 max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-light">Upload Footage</h1>
        <p className="text-gray-400 mt-1">Upload your raw video. The AI Agent will handle the rest.</p>
      </div>

      <div className="bg-gray-900 border-2 border-dashed border-gray-700 rounded-2xl p-12 flex flex-col items-center justify-center">
        {uploading ? (
          <div className="flex flex-col items-center gap-4">
            <Loader className="w-12 h-12 text-blue-500 animate-spin" />
            <p className="text-lg">Uploading and initiating AI Agent...</p>
            <p className="text-sm text-gray-500">Extracting audio, transcribing, and analyzing scenes.</p>
          </div>
        ) : (
          <>
            <div className="bg-gray-800 p-6 rounded-full mb-6">
              <UploadIcon className="w-12 h-12 text-gray-400" />
            </div>
            
            <input 
              type="file" 
              id="video-upload" 
              accept="video/mp4,video/quicktime,video/webm" 
              className="hidden"
              onChange={handleFileChange}
            />
            
            <label 
              htmlFor="video-upload" 
              className="bg-blue-600 hover:bg-blue-500 text-white px-8 py-3 rounded-full font-medium cursor-pointer transition mb-4"
            >
              Select Video
            </label>
            
            <p className="text-sm text-gray-500 mb-6">MP4, MOV, WebM up to 2GB</p>

            {file && (
              <div className="flex items-center gap-3 bg-gray-800 px-6 py-4 rounded-xl w-full max-w-md mb-6">
                <Video className="text-blue-400 w-6 h-6" />
                <div className="flex-1 truncate">
                  <p className="text-sm font-medium truncate">{file.name}</p>
                  <p className="text-xs text-gray-400">{(file.size / (1024 * 1024)).toFixed(2)} MB</p>
                </div>
              </div>
            )}

            {file && (
              <button 
                onClick={handleUpload}
                className="bg-white text-black hover:bg-gray-200 px-8 py-3 rounded-full font-bold transition flex items-center gap-2"
              >
                Start AI Processing
              </button>
            )}
          </>
        )}
      </div>

      <div className="mt-8 bg-blue-900/20 border border-blue-900/50 rounded-xl p-4 flex gap-3 text-sm text-blue-200">
        <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
        <p>
          <strong>Note:</strong> If the backend upload fails due to sandbox limitations, the system will automatically enter <strong>Demo Mode</strong> and load a pre-analyzed sample project so you can explore the editing interface and AI Agent architecture.
        </p>
      </div>
    </div>
  );
}
