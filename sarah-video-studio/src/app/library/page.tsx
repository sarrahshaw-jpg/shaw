import { Film, Clock, CheckCircle2, Video } from "lucide-react";

export default function LibraryPage() {
  const library = [
    { id: "proj_93x2", title: "Psychology of Hooks", date: "2026-09-18", duration: "00:00:45", status: "Published", platform: "TikTok, Reels" },
    { id: "proj_41b7", title: "Office Politics Explained", date: "2026-09-15", duration: "00:01:12", status: "Approved", platform: "LinkedIn" },
    { id: "demo-123", title: "Emotional Peaks (Demo)", date: "2026-09-19", duration: "00:00:30", status: "Draft", platform: "All" },
  ];

  return (
    <div className="min-h-screen p-8 max-w-6xl mx-auto flex flex-col gap-8 text-gray-200">
      <header className="border-b border-gray-800 pb-6 flex justify-between items-end">
        <div>
          <h1 className="text-2xl font-light">Content Library</h1>
          <p className="text-gray-400 mt-1">Manage and export your processed videos.</p>
        </div>
        <button className="bg-white text-black hover:bg-gray-200 px-6 py-2 rounded-full font-medium transition text-sm flex items-center gap-2">
          <Video className="w-4 h-4" /> Batch Upload
        </button>
      </header>

      <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
        <table className="w-full text-left text-sm">
          <thead className="bg-gray-950 border-b border-gray-800 text-gray-400">
            <tr>
              <th className="px-6 py-4 font-medium">Video</th>
              <th className="px-6 py-4 font-medium">Date</th>
              <th className="px-6 py-4 font-medium">Duration</th>
              <th className="px-6 py-4 font-medium">Platform</th>
              <th className="px-6 py-4 font-medium">Status</th>
              <th className="px-6 py-4 font-medium"></th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-800">
            {library.map(item => (
              <tr key={item.id} className="hover:bg-gray-800/50 transition group">
                <td className="px-6 py-4 flex items-center gap-3">
                  <div className="w-10 h-10 bg-gray-800 rounded flex items-center justify-center">
                    <Film className="w-4 h-4 text-gray-500" />
                  </div>
                  <div>
                    <div className="font-medium text-white">{item.title}</div>
                    <div className="text-xs text-gray-500 font-mono">{item.id}</div>
                  </div>
                </td>
                <td className="px-6 py-4 text-gray-400">{item.date}</td>
                <td className="px-6 py-4 text-gray-400 font-mono">{item.duration}</td>
                <td className="px-6 py-4">
                  <span className="bg-gray-800 text-gray-300 px-2 py-1 rounded text-xs">{item.platform}</span>
                </td>
                <td className="px-6 py-4">
                  {item.status === 'Published' && <span className="text-green-500 flex items-center gap-1.5"><CheckCircle2 className="w-4 h-4" /> {item.status}</span>}
                  {item.status === 'Approved' && <span className="text-blue-500 flex items-center gap-1.5"><CheckCircle2 className="w-4 h-4" /> {item.status}</span>}
                  {item.status === 'Draft' && <span className="text-yellow-500 flex items-center gap-1.5"><Clock className="w-4 h-4" /> {item.status}</span>}
                </td>
                <td className="px-6 py-4 text-right">
                  <a href={\`/editor/\${item.id}\`} className="text-blue-400 hover:text-blue-300 font-medium opacity-0 group-hover:opacity-100 transition">Open Editor →</a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
