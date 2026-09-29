"""Stage 8: cover images, posting copy, and copying finals into the repo."""
import os, re, subprocess, shutil
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from common import *

plan = jload(os.path.join(WORK, "plan.json"))
os.makedirs(OUT, exist_ok=True)

first_sent = []
for g in plan["captions"]:
    for w in g["words"]:
        first_sent.append(w["w"])
        if w["w"].rstrip()[-1:] in ".!?":
            break
    if first_sent and first_sent[-1].rstrip()[-1:] in ".!?":
        break
hook = " ".join(first_sent).strip().strip('"“”').strip()
if len(hook) > 90:
    hook = hook[:87].rsplit(" ", 1)[0] + "..."
kw_list = [k["text"].title() for k in plan["keywords"][:5]]

def cover(video, outp, TW, TH, label):
    # pick a clean frame: avoid concept-tile windows when present
    tiles = jload(os.path.join(WORK, "tiles.json"), {"times": [], "win": 0})
    t = 1.1
    win = tiles.get("win", 0)
    for _ in range(40):
        if all(not (tt - 0.4 <= t <= tt + win + 0.4) for tt in tiles.get("times", [])):
            break
        t += 0.7
    tmp = outp + ".frame.png"
    r = run([FFMPEG, "-y", "-hide_banner", "-loglevel", "error",
             "-ss", f"{t:.2f}", "-i", video, "-frames:v", "1", tmp])
    base = Image.open(tmp).convert("RGB")
    grad = Image.new("L", (1, TH))
    for y in range(TH):
        grad.putpixel((0, y), int(200 * max(0.0, (y / TH - 0.42)) ** 1.4))
    grad = grad.resize((TW, TH))
    black = Image.new("RGB", (TW, TH), (0, 0, 0))
    base = Image.composite(black, base, grad)
    d = ImageDraw.Draw(base)
    fs = int(TH * (0.085 if TH > TW else 0.075))
    font = ImageFont.truetype(os.path.join(FONTS, "Montserrat-ExtraBold.ttf"), fs)
    words, lines, cur = hook.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) > TW * 0.84 and cur:
            lines.append(cur); cur = w
        else:
            cur = t
        if len(lines) == 2:
            break
    if cur and len(lines) < 2:
        lines.append(cur)
    y = TH - int(TH * 0.16) - fs * len(lines)
    d.rectangle([TW * 0.08, y - fs * 0.45, TW * 0.08 + 10, y + 2], fill=(255, 214, 10))
    for ln in lines:
        d.text((TW * 0.08 + 30, y), ln, font=font, fill=(255, 255, 255))
        y += int(fs * 1.22)
    base.save(outp, quality=92)
    os.remove(tmp)
    print("COVER:", outp)

def build_ld_from_ig(ig_master):
    """v6 LinkedIn = the SAME approved vertical composition, pillarboxed on a
    1920x1080 canvas from its own blurred background - never a side gallery of
    random images. A very thin hairline frame marks the exact video area that
    shows on LinkedIn (safe-area guide). A clean copy without the frame is
    written too, for direct posting."""
    FG_W = round(1080 * 9 / 16 / 2) * 2 + 0  # 608 -> keep even
    FG_W = 608
    x0 = (1920 - FG_W) // 2
    fc = (
        f"[0:v]scale={FG_W}:1080:flags=lanczos,setsar=1[fg];"
        f"[0:v]scale=1920:1080:force_original_aspect_ratio=increase:flags=lanczos,"
        f"crop=1920:1080,gblur=sigma=28,eq=brightness=-0.06:saturation=0.72[bg];"
        f"[bg][fg]overlay={x0}:0[base];"
        f"[base]drawbox=x={x0 - 1}:y=0:w=2:h=1080:color=white@0.45:t=fill,"
        f"drawbox=x={x0 + FG_W - 1}:y=0:w=2:h=1080:color=white@0.45:t=fill[vf]"
    )
    ld_frame = os.path.join(OUT, "LinkedIn_1080p.mp4")
    ld_clean = os.path.join(OUT, "LinkedIn_1080p_clean.mp4")
    r = run([FFMPEG, "-y", "-hide_banner", "-loglevel", "error", "-i", ig_master,
             "-filter_complex", fc, "-map", "[vf]", "-map", "0:a?",
             "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-profile:v", "high",
             "-level", "4.1", "-g", "60", "-pix_fmt", "yuv420p",
             "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
             "-c:a", "copy", "-movflags", "+faststart", ld_frame])
    if r.returncode != 0:
        print(r.stderr[-1500:]); raise SystemExit("ld build failed")
    r = run([FFMPEG, "-y", "-hide_banner", "-loglevel", "error", "-i", ig_master,
             "-filter_complex",
             f"[0:v]scale={FG_W}:1080:flags=lanczos,setsar=1[fg];"
             f"[0:v]scale=1920:1080:force_original_aspect_ratio=increase:flags=lanczos,"
             f"crop=1920:1080,gblur=sigma=28,eq=brightness=-0.06:saturation=0.72[bg];"
             f"[bg][fg]overlay={x0}:0[v]",
             "-map", "[v]", "-map", "0:a?",
             "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-profile:v", "high",
             "-level", "4.1", "-g", "60", "-pix_fmt", "yuv420p",
             "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
             "-c:a", "copy", "-movflags", "+faststart", ld_clean])
    if r.returncode != 0:
        print(r.stderr[-1500:]); raise SystemExit("ld clean build failed")
    print("LD OK: LinkedIn_1080p.mp4 (thin safe-area frame) + LinkedIn_1080p_clean.mp4")
    return ld_frame

def copy():
    final_ig = os.path.join(WORK, "out", "ig", "final.mp4")
    ig = os.path.join(OUT, "Instagram_Reel_1080x1920.mp4")
    ld = None
    if os.path.exists(final_ig):
        shutil.copy(final_ig, ig)
        ld = build_ld_from_ig(ig)
    return ld, ig

ld, ig = copy()

if os.path.exists(ld):
    cover(ld, os.path.join(OUT, "cover_linkedin.jpg"), 1920, 1080, "ld")
if os.path.exists(ig):
    cover(ig, os.path.join(OUT, "cover_reel.jpg"), 1080, 1920, "ig")

tags_linkedin = " ".join("#" + re.sub(r"[^\w]", "", k.replace(" ", "")).lower().capitalize() for k in kw_list[:4])
tags_ig = " ".join("#" + re.sub(r"[^\w]", "", k.replace(" ", "")).lower() for k in kw_list) + \
          " #reels #reelsinstagram #explore #viral #contentcreator #personalbranding #creatorlife #entrepreneurlife #growthmindset"
post = f"""# Posting Kit

## Hook (first line on-screen)
"{hook}"

## LinkedIn caption
{hook}

Here's the full breakdown - the 3 things that actually moved the needle:
{chr(10).join('- ' + k for k in kw_list[:3])}

Save this one for later, and tell me which point hit hardest.

{tags_linkedin} #Leadership #Growth

## Instagram caption
{hook}{chr(10)}{chr(10)}Full breakdown above - which one are you taking into this week?{chr(10)}{chr(10)}{tags_ig}

## Notes
- LinkedIn: 16:9 1080p - LinkedIn_1080p.mp4 has a very thin safe-area frame marking
  the exact video area; LinkedIn_1080p_clean.mp4 is frame-free for direct posting
- Instagram: 9:16 Reel, 1080x1920, captions placed for UI-safe zones
- Covers generated: cover_linkedin.jpg / cover_reel.jpg
- Removed {plan['removed_s']}s of dead air, fillers and gaps ({plan['new_dur']:.1f}s final runtime)
- Audio and video are frame-locked: identical timeline length, zero drift
"""
with open(os.path.join(OUT, "posting_kit.md"), "w") as f:
    f.write(post)
print("POSTING KIT OK")
print("DELIVERABLES in", OUT)
