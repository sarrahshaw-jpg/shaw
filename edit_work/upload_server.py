"""Private in-workspace upload server.
The user's browser reaches it through the platform preview tunnel and pushes
files in 4MB chunks - so attachment size limits don't apply.
GET /       -> upload page (drag & drop, mobile friendly, progress bars)
POST /upload?name=&chunk=&total=  -> raw chunk body appended to uploads/<name>
GET /status -> JSON of received files
"""
import os, re, json, html
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs, unquote

ROOT = "/home/user/shaw/edit_work/uploads"
os.makedirs(ROOT, exist_ok=True)
CHUNK_DIR = os.path.join(ROOT, ".parts")
os.makedirs(CHUNK_DIR, exist_ok=True)

PAGE = """<!doctype html><html><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>Video Drop — Edit Studio</title><style>
*{box-sizing:border-box;font-family:-apple-system,'Segoe UI',Roboto,sans-serif}
body{margin:0;min-height:100vh;background:linear-gradient(160deg,#0e1016,#1a1f2e);color:#eef2ff;display:flex;align-items:center;justify-content:center;padding:24px}
.card{max-width:560px;width:100%;background:#151a26;border:1px solid #2a3247;border-radius:20px;padding:32px;box-shadow:0 20px 60px rgba(0,0,0,.5)}
h1{margin:0 0 6px;font-size:26px}p.sub{margin:0 0 22px;color:#9aa7c7;font-size:14px;line-height:1.5}
#drop{border:2px dashed #3d4a6b;border-radius:16px;padding:38px 20px;text-align:center;cursor:pointer;transition:.2s}
#drop.over{border-color:#ffd60a;background:rgba(255,214,10,.06)}
#drop .big{font-size:40px}#drop b{color:#ffd60a}
button{margin-top:18px;width:100%;padding:14px;border:0;border-radius:12px;background:#ffd60a;color:#10131c;font-weight:700;font-size:16px;cursor:pointer}
.item{margin-top:16px;background:#0e1220;border-radius:12px;padding:12px 14px;font-size:14px}
.bar{height:8px;background:#232b42;border-radius:6px;margin-top:8px;overflow:hidden}
.bar i{display:block;height:100%;width:0;background:linear-gradient(90deg,#ffd60a,#ff9f0a);transition:width .2s}
.ok{color:#32d74b}.err{color:#ff6b6b}
ul{margin:18px 0 0;padding-left:18px;color:#9aa7c7;font-size:13px;line-height:1.7}
</style></head><body><div class=card>
<h1>🎬 Video Drop</h1>
<p class=sub>Private one-hop transfer into my edit studio. Works from phone or computer. Upload the <b>video</b> and the <b>reference screenshot</b> together.</p>
<div id=drop><div class=big>🎥</div><br>Drag & drop your video here<br>or tap to pick files</div>
<input id=file type=file multiple style=display:none>
<div id=list></div>
<button onclick="document.getElementById('file').click()">Pick files</button>
<ul><li>Files of any size — sent in small chunks</li><li>Keep this page open until all bars hit 100%</li><li>Then just tell me “uploaded” in the chat</li></ul>
</div><script>
const drop=document.getElementById('drop'),input=document.getElementById('file'),list=document.getElementById('list');
drop.onclick=()=>input.click();
drop.ondragover=e=>{e.preventDefault();drop.classList.add('over')};
drop.ondragleave=()=>drop.classList.remove('over');
drop.ondrop=e=>{e.preventDefault();drop.classList.remove('over');handle(e.dataTransfer.files)};
input.onchange=()=>handle(input.files);
async function handle(files){for(const f of files)await send(f);}
async function send(f){
 const div=document.createElement('div');div.className='item';
 div.innerHTML=`<b>${f.name}</b> <span id=s>— 0%</span><div class=bar><i id=b></i></div>`;
 list.appendChild(div);
 const bar=div.querySelector('#b'),st=div.querySelector('#s');
 const CH=4*1024*1024,total=Math.max(1,Math.ceil(f.size/CH));
 for(let i=0;i<total;i++){
   const blob=f.slice(i*CH,(i+1)*CH);
   let ok=false;
   for(let r=0;r<4&&!ok;r++){
     try{
       const res=await fetch(`/upload?name=${encodeURIComponent(f.name)}&chunk=${i}&total=${total}`,{method:'POST',body:blob});
       if(res.ok)ok=true;
     }catch(e){await new Promise(r=>setTimeout(r,800*r+500));}
   }
   if(!ok){st.textContent='— failed, retry';st.className='err';return;}
   const p=Math.round((i+1)/total*100);
   bar.style.width=p+'%';st.textContent='— '+p+'%';
 }
 st.textContent='✅ uploaded';st.className='ok';
}
</script></body></html>"""

def safe_name(n):
    n = os.path.basename(unquote(n or ""))
    n = re.sub(r"[^A-Za-z0-9 ._\-()]", "_", n).strip(". ")
    return n or "upload.bin"

class H(BaseHTTPRequestHandler):
    def log_message(self, fmt, *a):
        pass
    def _send(self, code, body, ctype="application/json"):
        data = body if isinstance(body, bytes) else json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)
    def do_GET(self):
        u = urlparse(self.path)
        if u.path.startswith("/dl/"):
            name = safe_name(u.path[4:])
            fp = os.path.join("/home/user/shaw/edits", name)
            if not os.path.isfile(fp):
                self._send(404, {"err": "not found"})
                return
            data = open(fp, "rb").read()
            self.send_response(200)
            self.send_header("Content-Type", "video/mp4" if name.lower().endswith((".mp4", ".mov")) else
                             ("image/jpeg" if name.lower().endswith((".jpg", ".jpeg")) else
                              ("text/markdown" if name.endswith(".md") else "application/octet-stream")))
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Content-Disposition", f'attachment; filename="{name}"')
            self.end_headers()
            self.wfile.write(data)
            return
        if u.path == "/files":
            d = "/home/user/shaw/edits"
            items = []
            for f in sorted(os.listdir(d)):
                fp = os.path.join(d, f)
                if os.path.isfile(fp):
                    items.append({"name": f, "size": os.path.getsize(fp)})
            self._send(200, {"items": items})
        elif u.path == "/status":
            files = [f for f in os.listdir(ROOT) if os.path.isfile(os.path.join(ROOT, f))]
            parts = len(os.listdir(CHUNK_DIR))
            self._send(200, {"files": files, "partial_parts": parts})
        elif u.path == "/down":
            d = "/home/user/shaw/edits"
            rows = ""
            icons = {".mp4": "🎬", ".jpg": "🖼", ".md": "📝", ".png": "🖼"}
            for f in sorted(os.listdir(d)):
                fp = os.path.join(d, f)
                if not os.path.isfile(fp):
                    continue
                sz = os.path.getsize(fp)
                hs = f"{sz/1048576:.1f} MB" if sz > 1048576 else f"{sz/1024:.0f} KB"
                ic = icons.get(os.path.splitext(f)[1].lower(), "📄")
                rows += f'<a class=row href="/dl/{f}"><span>{ic} {f}</span><b>{hs}</b></a>'
            page = ("<!doctype html><html><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>"
                    "<title>Final Edits — Download</title><style>*{box-sizing:border-box;font-family:-apple-system,'Segoe UI',Roboto,sans-serif}"
                    "body{margin:0;background:#0e1016;color:#eef2ff;padding:28px;max-width:640px;margin:auto}"
                    "h1{font-size:24px}p{color:#9aa7c7;font-size:14px}"
                    ".row{display:flex;justify-content:space-between;gap:12px;background:#151a26;border:1px solid #2a3247;"
                    "border-radius:14px;padding:16px 18px;margin:10px 0;color:#ffd60a;text-decoration:none;font-size:15px}"
                    ".row b{color:#9aa7c7;font-weight:600}.row:active{background:#1d2436}</style></head><body>"
                    "<h1>✅ Final edits — tap to download</h1>"
                    "<p>Start with the <b>light</b> versions for quick sharing; the full masters are highest quality.</p>"
                    + rows + "</body></html>")
            self._send(200, page.encode(), "text/html; charset=utf-8")
        elif u.path == "/":
            self._send(200, PAGE.encode(), "text/html; charset=utf-8")
        else:
            self._send(404, {"err": "not found"})
    def do_POST(self):
        u = urlparse(self.path)
        if u.path != "/upload":
            self._send(404, {"err": "not found"})
            return
        q = parse_qs(u.query)
        name = safe_name(q.get("name", ["upload.bin"])[0])
        try:
            idx = int(q.get("chunk", ["0"])[0]); total = int(q.get("total", ["1"])[0])
        except ValueError:
            self._send(400, {"err": "bad chunk"}); return
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length) if length else b""
        part = os.path.join(CHUNK_DIR, f"{name}.p{idx:06d}")
        with open(part, "wb") as f:
            f.write(body)
        have = {int(re.search(r"\.p(\d+)$", p).group(1)) for p in os.listdir(CHUNK_DIR)
                if p.startswith(name + ".p")}
        if len(have) >= total:
            final = os.path.join(ROOT, name)
            with open(final, "wb") as out:
                for i in range(total):
                    p = os.path.join(CHUNK_DIR, f"{name}.p{i:06d}")
                    if os.path.exists(p):
                        with open(p, "rb") as pf:
                            out.write(pf.read())
                        os.remove(p)
            self._send(200, {"ok": True, "done": name, "size": os.path.getsize(final)})
        else:
            self._send(200, {"ok": True, "received": idx, "have": len(have), "total": total})

ThreadingHTTPServer(("0.0.0.0", 8080), H).serve_forever()
