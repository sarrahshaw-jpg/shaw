"""Stage 6: render each kept segment - face-follow framing + animated zoom (zoompan,
2x supersampled for smoothness), face light, cinematic tone, sharpening.
Landscape source: ld = full-frame push-ins; ig = 9:16 face-follow crop + push-ins."""
import os, sys
from common import *

V = sys.argv[1]
SRC = sys.argv[2]
plan = jload(os.path.join(WORK, "plan.json"))
probe = jload(os.path.join(WORK, "probe.json"))
faces = jload(os.path.join(WORK, "faces.json"))
SW, SH, FPS = probe["w"], probe["h"], probe["fps"]
T = TARGETS[V]
TW, TH = T["w"], T["h"]
segs = plan["segments"]
SODIR = SEGS[V]
os.makedirs(SODIR, exist_ok=True)

landscape_src = SW >= SH * 0.95
vertical_src = SH >= SW * 0.95

def spec():
    if V == "ld":
        return "pad" if vertical_src else "crop"
    # ig
    if vertical_src or landscape_src:
        return "vcrop"
    return "pad"

MODE = spec()
if MODE == "crop":
    BW, BH = SW, SH
elif MODE == "vcrop":
    if vertical_src:
        BW = SW
        BH = round(SW * 16 / 9 / 2) * 2
    else:
        BW = round(SH * 9 / 16 / 2) * 2
        BH = SH
else:
    BW, BH = SW, SH
print(f"VARIANT {V}: out {TW}x{TH} | src {SW}x{SH} | mode={MODE} base={BW}x{BH}")

path = faces.get("path", [])
def face_center_at(src_t):
    if not path:
        return faces.get("cx", SW / 2), faces.get("cy", SH * 0.38)
    if src_t <= path[0]["t"]:
        return path[0]["cx"], path[0]["cy"]
    if src_t >= path[-1]["t"]:
        return path[-1]["cx"], path[-1]["cy"]
    for a, b in zip(path, path[1:]):
        if a["t"] <= src_t <= b["t"]:
            u = (src_t - a["t"]) / max(1e-6, b["t"] - a["t"])
            return a["cx"] + (b["cx"] - a["cx"]) * u, a["cy"] + (b["cy"] - a["cy"]) * u
    return path[-1]["cx"], path[-1]["cy"]

def piecewise(points, var="t"):
    pts = sorted(points)
    e = f"{pts[-1][1]:.1f}"
    for i in range(len(pts) - 2, -1, -1):
        t0, v0 = pts[i]
        t1, v1 = pts[i + 1]
        e = f"if(lt({var},{t1:.3f}),{v0:.1f}+({v1:.1f}-{v0:.1f})*({var}-{t0:.3f})/{t1 - t0:.3f},{e})"
    return e

def zoompan_chain(ps, in_w, in_h, out_w, out_h):
    """animated zoom centered on the face (piecewise follow), 2x supersampled input."""
    D = ps["dur"]
    N = max(1, round(D * FPS))
    z0, z1 = ps["zoom"]
    z = f"{z0:.4f}+({z1 - z0:.4f})*on/{N}"
    spts_x, spts_y = [], []
    n = min(5, max(2, int(D / 1.0) + 1))
    for k in range(n + 1):
        lt = D * k / n
        fcx, fcy = face_center_at(ps["src_s"] + lt)
        if MODE == "v crop":
            fcx = fcx - (SW - BW) / 2.0
            fcy = fcy
        if V == "ld":
            cx = in_w / 2 + (fcx * (in_w / SW) - in_w / 2) * 0.8
            cy = in_h / 2 + (fcy * (in_h / SH) - in_h / 2) * 0.8
        else:
            cx = in_w / 2 + (fcx * (in_w / BW) - in_w / 2) * 0.85
            cy = in_h / 2 + (fcy * (in_h / SH) - in_h / 2) * 0.85
        spts_x.append((lt, cx))
        spts_y.append((lt, cy))
    x = f"clip({piecewise(spts_x, 'on')}-(iw/zoom)/2,0,iw-iw/zoom)"
    y = f"clip({piecewise(spts_y, 'on')}-(ih/zoom)/2,0,ih-ih/zoom)"
    return (f"scale={in_w * 2}:{in_h * 2}:flags=lanczos,"
            f"zoompan=z='{z}':x='{x}':y='{y}':d=1:s={out_w}x{out_h}:fps={FPS}")

def stage_a_ig(ps):
    """static 9:16 window, face-followed via per-frame x/y (crop w/h are static)."""
    spts_x, spts_y = [], []
    n = min(7, max(2, int(ps["dur"] / 0.7) + 1))
    for k in range(n + 1):
        lt = ps["dur"] * k / n
        fcx, fcy = face_center_at(ps["src_s"] + lt)
        cx = fcx * 0.85 + SW / 2 * 0.15
        cy = fcy * 0.78 + SH * 0.22
        spts_x.append((lt, cx - BW / 2))
        spts_y.append((lt, cy - BH / 2))
    x = f"clip({piecewise(spts_x)},0,iw-{BW})"
    y = f"clip({piecewise(spts_y)},0,ih-{BH})"
    return f"crop={BW}:{BH}:x='{x}':y='{y}',scale={BW * 2}:{BH * 2}:flags=bicubic"

DN = "hqdn3d=1.1:0.9:4:4"   # light temporal denoise - detail preserved
# v5 conservative grade: neutral WB, micro-contrast, NO lifts/gamma boosts
WB = "colortemperature=temperature=6600:pl=0.5"
CURVES = "curves=master='0/0.012 0.5/0.53 1/0.99'"
TONE = "eq=contrast=1.015:saturation=1.04:brightness=0.004:gamma=1.03"
SHARP = "cas=0.24,unsharp=5:5:0.28:5:5:0.0,unsharp=7:7:0.14:7:7:0.0"
LOOK = ",".join([WB, CURVES, TONE])
fl = os.path.join(WORK, "gfx", V, "face_light.png")

for ps in segs:
    outp = os.path.join(SODIR, f"seg_{ps['i']:03d}.mp4")
    if MODE == "crop" and V == "ld":
        vp = f"[0:v]setpts=PTS-STARTPTS,{DN},{zoompan_chain(ps, SW, SH, TW, TH)},{LOOK}[b]"
    elif MODE == "vcrop":
        # vertical base window already face-followed; add centered animated push + upscale
        D = ps["dur"]; N = max(1, round(D * FPS)); z0, z1 = ps["zoom"]
        z = f"{z0:.4f}+({z1 - z0:.4f})*on/{N}"
        zp = (f"zoompan=z='{z}':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)/2':d=1:s={BW}x{BH}:fps={FPS},"
              f"scale={TW}:{TH}:flags=lanczos")
        vp = f"[0:v]setpts=PTS-STARTPTS,{DN},{stage_a_ig(ps)},{zp},{LOOK}[b]"
    else:  # pad: vertical source -> landscape with blurred fill
        D = ps["dur"]; N = max(1, round(D * FPS)); z0, z1 = ps["zoom"]
        z = f"{z0:.4f}+({z1 - z0:.4f})*on/{N}"
        fg = (f"[0:v]setpts=PTS-STARTPTS,{DN},"
              f"scale={SW * 2}:{SH * 2}:flags=lanczos,"
              f"zoompan=z='{z}':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)/2':d=1:s={SW}x{SH}:fps={FPS},"
              f"scale={TW}:{TH}:force_original_aspect_ratio=decrease:flags=lanczos[fg];"
              f"[0:v]scale={TW}:{TH}:force_original_aspect_ratio=increase,"
              f"crop={TW}:{TH},gblur=sigma=26,eq=brightness=-0.05:saturation=0.85[bg];")
        vp = fg + f"[bg][fg]overlay=(W-w)/2:(H-h)/2,{LOOK}[b]"

    r = run([FFMPEG, "-y", "-hide_banner", "-loglevel", "error",
             "-ss", f"{ps['src_s']:.3f}", "-t", f"{ps['dur']:.3f}", "-i", SRC,
             "-loop", "1", "-t", f"{ps['dur']:.3f}", "-i", fl,
             "-filter_complex",
             f"{vp};[b][1:v]overlay=0:0:format=auto:eof_action=pass[bt];"
             f"[bt]{SHARP},format=yuv420p[v]",
             "-map", "[v]", "-an", "-c:v", "libx264", "-preset", "veryfast",
             "-crf", "16", "-g", "30", outp])
    if r.returncode != 0:
        print("SEG FAIL", outp, "\n", r.stderr[-1800:]); sys.exit(1)
    print(f"  seg {ps['i']:03d} {ps['dur']:.2f}s z {ps['zoom'][0]}->{ps['zoom'][1]}")
print(f"SEGMENTS {V}: {len(segs)} rendered")
