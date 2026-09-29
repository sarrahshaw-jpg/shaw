"""Stage 6b v5: editorial background compositing.
- conservative grade: NO bilateral smoothing, neutral WB, micro-contrast, restrained
  crispness (detail preserved, nothing plasticky)
- face light at 40% of v4 strength
- editorial cards (photographic/glyph) + ghost keywords on the BACKGROUND layer,
  person in front via MediaPipe mask - nothing over her face
- vertical: cards alternate left/right of her silhouette, ghosts above head
- landscape pad mode: ghosts above head; cards handled by s7 in the blur bars
"""
import os, sys, json, subprocess
import warnings; warnings.filterwarnings("ignore")
import numpy as np
import cv2
import mediapipe as mp
from PIL import Image, ImageDraw, ImageFont, ImageFilter
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

typo = jload(os.path.join(WORK, "typo.json"), {"cards": [], "ghosts": []})
CARDS = []
for c in typo["cards"]:
    if os.path.exists(c.get("file", "")):
        CARDS.append({"img": Image.open(c["file"]).convert("RGBA"), **c})
KW_FONT = ImageFont.truetype(os.path.join(FONTS, "Playfair-Italic.ttf"), 104)
# v6.1 ghost keywords: bold spaced caps + soft shadow (user: bolder, clean, visible)
GHOST_FONT_PATH = os.path.join(FONTS, "Montserrat-ExtraBold.ttf")
GHOST_FONT = ImageFont.truetype(GHOST_FONT_PATH, 112)
GHOST_SP = 16
GHOSTS = typo.get("ghosts", [])

fl_path = os.path.join(WORK, "gfx", V, "face_light.png")
FL_A = 0.0   # v6: face light REMOVED - original exposure is the reference

seg = mp.solutions.selfie_segmentation.SelfieSegmentation(model_selection=1)

VERTICAL_SRC = SH >= SW * 0.95
PADMODE = (V == "ld" and VERTICAL_SRC)

def card_pos(spec, fg_x0, fg_x1):
    if PADMODE:
        x = (fg_x0 - 330) if spec["side"] == "L" else (fg_x1 + 330)
        return x, TH * 0.40
    # v6: smaller cards, higher in the background layer, close to her silhouette
    x = TW * (0.205 if spec["side"] == "L" else 0.795)
    return x, TH * 0.375

def ghost_pos():
    return TW / 2, TH * 0.165

def face_center(src_t):
    path = faces.get("path", [])
    if not path:
        return faces.get("cx", SW / 2), faces.get("cy", SH * 0.4)
    if src_t <= path[0]["t"]:
        return path[0]["cx"], path[0]["cy"]
    if src_t >= path[-1]["t"]:
        return path[-1]["cx"], path[-1]["cy"]
    for a, b in zip(path, path[1:]):
        if a["t"] <= src_t <= b["t"]:
            u = (src_t - a["t"]) / max(1e-6, b["t"] - a["t"])
            return a["cx"] + (b["cx"] - a["cx"]) * u, a["cy"] + (b["cy"] - a["cy"]) * u
    return path[-1]["cx"], path[-1]["cy"]

_LUT_X = np.array([0, 64, 128, 200, 255], np.float32)
_LUT_Y = np.array([0, 64, 128, 200, 255], np.float32)   # v6: identity - color untouched

def tone(base):
    """v6: NO color grade at all (original is the reference; the v5 LUT/gamma/
    gain stack caused the washed-out white-grey cast). Only crispness: a light
    two-band unsharp mask, which adds detail without halos or smoothing."""
    x = base.astype(np.float32)
    b1 = cv2.GaussianBlur(x, (0, 0), 2.0)
    x += 0.24 * (x - b1)
    b2 = cv2.GaussianBlur(x, (0, 0), 5.0)
    x += 0.10 * (x - b2)
    return np.clip(x, 0, 255)

def paste_rgba(base, tile, cx, cy, scale=1.0, alpha_mult=1.0):
    t = tile
    if scale != 1.0:
        t = t.resize((int(t.width * scale), int(t.height * scale)), Image.LANCZOS)
    if alpha_mult != 1.0:
        arr = np.array(t)
        arr[..., 3] = (arr[..., 3] * alpha_mult).astype(np.uint8)
        t = Image.fromarray(arr)
    h, w = t.height, t.width
    x0, y0 = int(cx - w / 2), int(cy - h / 2)
    x1, y1 = x0 + w, y0 + h
    if x1 <= 0 or y1 <= 0 or x0 >= base.shape[1] or y0 >= base.shape[0]:
        return
    sx0, sy0 = max(0, -x0), max(0, -y0)
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(base.shape[1], x1), min(base.shape[0], y1)
    t_np = np.array(t).astype(np.float32)[sy0:sy0 + y1 - y0, sx0:sx0 + x1 - x0]
    a = t_np[..., 3:4] / 255.0
    base[y0:y1, x0:x1] = base[y0:y1, x0:x1] * (1 - a) + t_np[..., :3] * a

def windows():
    for c in CARDS:
        yield (max(0.0, c["t"] - 0.15), c["t"] + c["win"] + 0.25)
    for g in GHOSTS:
        yield (max(0.0, g["t"] - 0.15), g["t"] + 2.4)

def dst_spans():
    acc = 0.0
    for ps in segs:
        yield ps["i"], acc, acc + ps["dur"]
        acc += ps["dur"] - ps["tr_after"]

bake_ids = set()
for ps_i, d0, d1 in dst_spans():
    for w in windows():
        if d0 < w[1] and d1 > w[0]:
            bake_ids.add(ps_i)
print(f"BAKE: segments {sorted(bake_ids)}")

for ps in segs:
    if ps["i"] not in bake_ids:
        continue
    dur = ps["dur"]
    outp = os.path.join(SODIR, f"seg_{ps['i']:03d}.mp4")
    dec = subprocess.Popen(
        [FFMPEG, "-loglevel", "error", "-ss", f"{ps['src_s']:.3f}", "-t", f"{dur:.3f}",
         "-i", SRC, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    enc = subprocess.Popen(
        [FFMPEG, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
         "-s", f"{TW}x{TH}", "-r", str(FPS), "-i", "-", "-an",
         "-frames:v", str(ps.get("frames", round(dur * FPS))),
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "14", "-g", "30", outp],
        stdin=subprocess.PIPE)
    z0, z1 = ps["zoom"]
    frame_i = 0
    fg_x0, fg_x1 = 0, TW
    while True:
        buf = dec.stdout.read(SW * SH * 3)
        if len(buf) < SW * SH * 3:
            break
        t_loc = frame_i / FPS
        frame = np.frombuffer(buf, np.uint8).reshape(SH, SW, 3)
        frame = tone(frame.astype(np.float32))
        z = z0 + (z1 - z0) * (t_loc / max(dur, 0.01))
        fcx, fcy = face_center(ps["src_s"] + t_loc)
        cx = SW / 2 + (fcx - SW / 2) * 0.85
        cy = SH / 2 + (fcy - SH / 2) * 0.85
        cw, ch = SW / z, SH / z
        x0 = min(max(cx - cw / 2, 0), SW - cw); y0 = min(max(cy - ch / 2, 0), SH - ch)
        crop = frame[int(y0):int(y0 + ch), int(x0):int(x0 + cw)]
        m = None
        mfg = None
        if PADMODE:
            ch_i, cw_i = crop.shape[:2]
            s = TH / ch_i
            fg = cv2.resize(crop, (int(cw_i * s), TH), interpolation=cv2.INTER_LANCZOS4)
            fg_x0 = (TW - fg.shape[1]) // 2
            fg_x1 = fg_x0 + fg.shape[1]
            fsmall = cv2.resize(fg.astype(np.uint8), (240, 426))
            mres = seg.process(fsmall)
            mfg = mres.segmentation_mask if mres.segmentation_mask is not None else np.zeros((426, 240), np.float32)
            mfg = cv2.resize(mfg, (fg.shape[1], fg.shape[0]))
            mfg = np.clip(mfg, 0, 1) ** 1.15
            mfg = cv2.GaussianBlur(mfg, (7, 7), 0)
            layer = fg.astype(np.float32)
        else:
            frame = cv2.resize(crop, (TW, TH), interpolation=cv2.INTER_LANCZOS4)
            frame = np.clip(frame, 0, 255).astype(np.uint8)
            small = cv2.resize(frame, (480, int(480 * TH / TW)))
            mres = seg.process(small)
            m = cv2.resize(mres.segmentation_mask, (TW, TH)) if mres.segmentation_mask is not None else np.zeros((TH, TW), np.float32)
            m = np.clip(m, 0, 1) ** 1.15
            m = cv2.GaussianBlur(m, (9, 9), 0)
            layer = frame.astype(np.float32)

        dst_t = 0.0
        for psx in segs[:ps["i"]]:
            dst_t += psx["dur"] - psx["tr_after"]
        dst_t += t_loc

        for c in CARDS:
            if PADMODE:
                continue  # landscape: cards go in the bars via s7 overlays
            if c["t"] - 0.15 <= dst_t <= c["t"] + c["win"] + 0.25:
                a = min(1.0, 3.0 * min(dst_t - (c["t"] - 0.15), (c["t"] + c["win"] + 0.25) - dst_t))
                drift = 10.0 * min(1.0, max(0.0, dst_t - (c["t"] - 0.15)) / max(c["win"], 0.1))
                gx, gy = card_pos(c, fg_x0, fg_x1)
                paste_rgba(layer, c["img"], gx - (drift if c["side"] == "L" else -drift), gy,
                           scale=c.get("scale", 0.92), alpha_mult=a)
        for g in GHOSTS:
            if g["t"] - 0.15 <= dst_t <= g["t"] + 2.4:
                env = min(1.0, 3.0 * min(dst_t - (g["t"] - 0.15), (g["t"] + 2.4) - dst_t))
                # v6.2: dark vibrant amber + black outline; auto-fit so the word
                # NEVER touches the frame edges (min 8% margin each side)
                px = 112
                _mw = Image.new("RGBA", (1600, 300), (0, 0, 0, 0))
                _mwd = ImageDraw.Draw(_mw)
                def _w(p):
                    f = ImageFont.truetype(GHOST_FONT_PATH, p)
                    return sum(_mwd.textlength(c, font=f) + GHOST_SP for c in g["text"]) - GHOST_SP
                while px > 60 and _w(px) > TW * 0.84:
                    px -= 4
                gf = ImageFont.truetype(GHOST_FONT_PATH, px)
                tmp = Image.new("RGBA", (1600, 300), (0, 0, 0, 0))
                td = ImageDraw.Draw(tmp)
                wtxt = sum(td.textlength(c, font=gf) + GHOST_SP for c in g["text"]) - GHOST_SP
                x0 = 800 - wtxt / 2
                shd = Image.new("RGBA", (1600, 300), (0, 0, 0, 0))
                sd = ImageDraw.Draw(shd)
                xx = x0 + 5
                for c in g["text"]:
                    sd.text((xx, 156), c, font=gf, fill=(10, 10, 12, 210))
                    xx += sd.textlength(c, font=gf) + GHOST_SP
                shd = shd.filter(ImageFilter.GaussianBlur(7))
                xx = x0
                stroke = max(4, px // 18)
                for c in g["text"]:
                    td.text((xx, 150), c, font=gf, fill=(209, 144, 28, 255),
                            stroke_width=stroke, stroke_fill=(8, 8, 10, 255))
                    xx += td.textlength(c, font=gf) + GHOST_SP
                tmp = Image.alpha_composite(shd, tmp)
                peak = 0.92
                tmp.putalpha(tmp.getchannel("A").point(lambda v: int(v * peak * env)))
                bbox = tmp.getbbox()
                if bbox:
                    tmp = tmp.crop(bbox)
                gx, gy = ghost_pos()
                paste_rgba(layer, tmp, gx, gy, scale=1.0)
        layer = layer.astype(np.uint8)

        if PADMODE:
            out = layer
            hh, ww = fg.shape[:2]
            a3 = mfg[..., None]
            out[:, fg_x0:fg_x0 + ww] = out[:, fg_x0:fg_x0 + ww] * (1 - a3) + fg * a3
            out = np.clip(out, 0, 255).astype(np.uint8)
        else:
            out = (layer.astype(np.float32) * (1 - m[..., None]) + frame * m[..., None]).astype(np.uint8)
        enc.stdin.write(out.tobytes())
        frame_i += 1
    dec.stdout.close(); enc.stdin.close(); dec.wait(); enc.wait()
    print(f"  baked seg {ps['i']:03d} ({frame_i} frames)")

covered = []
for c in CARDS:
    mid = c["t"] + c["win"] / 2
    host = None
    for ps_i, d0, d1 in dst_spans():
        if d0 - 0.2 <= mid <= d1 + 0.2:
            host = ps_i
            break
    covered.append(host in bake_ids if host is not None else False)
jwrite = {"baked": sorted(bake_ids), "tiles_covered": covered, "all_covered": all(covered)}
jsave(os.path.join(WORK, f"bake_manifest_{V}.json"), jwrite)
print("BAKE MANIFEST:", jwrite)
