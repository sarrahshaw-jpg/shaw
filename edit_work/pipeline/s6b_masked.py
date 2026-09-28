"""Stage 6b: masked compositing - re-renders segments that contain pop windows with
tiles + ghost keywords BEHIND the person (MediaPipe selfie segmentation).
Vertical deliverable: tiles sit in the visible background beside her silhouette,
keywords float above her head. Landscape deliverable (vertical source): blur-fill
bars host the tiles; center keeps the person. Writes per-variant bake manifests."""
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

tiles = jload(os.path.join(WORK, "tiles_v3.json"))
tile_files = [Image.open(f).convert("RGBA") for f in tiles["files"]]
tile_times = tiles["times"]
TILE_WIN = tiles.get("win", 2.1)
kw_events = tiles.get("keywords", [])
KW_FONT = ImageFont.truetype(os.path.join(FONTS, "Montserrat-ExtraBold.ttf"), 86)

# face light layer (color-safe white glow)
fl_path = os.path.join(WORK, "gfx", V, "face_light.png")
FL = np.array(Image.open(fl_path).convert("RGBA")).astype(np.float32) / 255.0
FL_A = FL[..., 3:4] * 0.9

seg = mp.solutions.selfie_segmentation.SelfieSegmentation(model_selection=1)

VERTICAL_SRC = SH >= SW * 0.95
PADMODE = (V == "ld" and VERTICAL_SRC)   # 16:9 deliverable from vertical source

def tile_slot_x(slot_i, fg_x0, fg_x1):
    if not PADMODE:
        # vertical: visible background LEFT / RIGHT of her silhouette
        return TW * (0.165 if slot_i % 2 == 0 else 0.835)
    return (fg_x0 - 400) if slot_i % 2 == 0 else (fg_x1 + 400)

_slot_phase = 0
def kw_y():
    return TH * 0.19 if PADMODE else TH * 0.155

def tile_y():
    if PADMODE:
        return TH * 0.62
    return TH * (0.335 if _slot_phase % 2 == 0 else 0.545)

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

_LUT_X = np.array([0, 26, 82, 184, 235, 255], np.float32)
_LUT_Y = np.array([7, 33, 92, 188, 236, 250], np.float32)   # shadow lift + gentle S

def tone(base):
    """premium look matched to the ffmpeg route: WB nudge, S-curve, sat, clarity."""
    x = base.astype(np.float32)
    x[..., 0] *= 0.985   # R
    x[..., 2] *= 1.015   # B
    for c in range(3):
        x[..., c] = np.interp(x[..., c], _LUT_X, _LUT_Y)
    x = np.clip(x / 255.0, 0, 1) ** (1 / 1.09)
    x = x * 1.02 + 0.006
    gray = (0.2126 * x[..., 0] + 0.7152 * x[..., 1] + 0.0722 * x[..., 2])[..., None]
    x = np.clip(gray + (x - gray) * 1.06, 0, 1)
    x *= 255.0
    b1 = cv2.GaussianBlur(x, (0, 0), 2.0)
    x += 0.30 * (x - b1)
    b2 = cv2.GaussianBlur(x, (0, 0), 7.0)
    x += 0.16 * (x - b2)
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

# ---- which segments need baking (pop windows live in DST time) ----
def windows():
    for t0 in tile_times:
        yield (max(0.0, t0 - 0.15), t0 + TILE_WIN + 0.25)
    for _, t0 in kw_events:
        yield (max(0.0, t0 - 0.15), t0 + 2.4)

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
print(f"BAKE: segments {sorted(bake_ids)} need behind-person compositing")

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
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-g", "30", outp],
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
        frame = cv2.bilateralFilter(frame, 5, 24, 24)
        frame = tone(frame.astype(np.float32))
        # zoom crop about face
        z = z0 + (z1 - z0) * (t_loc / max(dur, 0.01))
        fcx, fcy = face_center(ps["src_s"] + t_loc)
        cx = SW / 2 + (fcx - SW / 2) * 0.85
        cy = SH / 2 + (fcy - SH / 2) * 0.85
        cw, ch = SW / z, SH / z
        x0 = min(max(cx - cw / 2, 0), SW - cw); y0 = min(max(cy - ch / 2, 0), SH - ch)
        crop = frame[int(y0):int(y0 + ch), int(x0):int(x0 + cw)]

        m = None
        if PADMODE:
            ch_i, cw_i = crop.shape[:2]
            s = TH / ch_i
            fg = cv2.resize(crop, (int(cw_i * s), TH), interpolation=cv2.INTER_LANCZOS4)
            fg_x0 = (TW - fg.shape[1]) // 2
            fg_x1 = fg_x0 + fg.shape[1]
            bg_fill = cv2.resize(crop, (TW, TH), interpolation=cv2.INTER_LANCZOS4)
            fg = tone(fg)
            b1 = cv2.GaussianBlur(fg, (0, 0), 2.0); fg += 0.30 * (fg - b1)
            b2 = cv2.GaussianBlur(fg, (0, 0), 7.0);  fg += 0.16 * (fg - b2)
            fg = np.clip(fg, 0, 255)
            fsmall = cv2.resize(fg.astype(np.uint8), (240, 426))
            mres = seg.process(fsmall)
            mfg = mres.segmentation_mask if mres.segmentation_mask is not None else np.zeros((426, 240), np.float32)
            mfg = cv2.resize(mfg, (fg.shape[1], fg.shape[0]))
            mfg = np.clip(mfg, 0, 1) ** 1.15
            mfg = cv2.GaussianBlur(mfg, (7, 7), 0)
            bg = cv2.GaussianBlur(bg_fill, (0, 0), 22)
            bg = tone(bg.astype(np.float32)) * np.array([0.90, 0.90, 0.94])
            layer = np.clip(bg, 0, 255)
        else:
            frame = cv2.resize(crop, (TW, TH), interpolation=cv2.INTER_LANCZOS4)
            frame = frame * (1 - FL_A) + 255.0 * FL[..., :3] * FL_A
            frame = np.clip(frame, 0, 255).astype(np.uint8)
            small = cv2.resize(frame, (480, int(480 * TH / TW)))
            mres = seg.process(small)
            m = cv2.resize(mres.segmentation_mask, (TW, TH)) if mres.segmentation_mask is not None else np.zeros((TH, TW), np.float32)
            m = np.clip(m, 0, 1) ** 1.15
            m = cv2.GaussianBlur(m, (9, 9), 0)
            layer = frame.astype(np.float32)

        # pop timing on the destination timeline
        dst_t = 0.0
        for psx in segs[:ps["i"]]:
            dst_t += psx["dur"] - psx["tr_after"]
        dst_t += t_loc

        for ti, tt in enumerate(tile_times):
            _slot_phase = ti
            if tt - 0.15 <= dst_t <= tt + TILE_WIN + 0.25:
                ph = tt - dst_t
                grow = 1.0 + 0.10 * max(0.0, (0.35 - abs(ph - 0.35)) / 0.35) if ph < 0.9 else 1.0
                a = min(1.0, 4.0 * min(dst_t - (tt - 0.15), (tt + TILE_WIN + 0.25) - dst_t))
                paste_rgba(layer, tile_files[ti], tile_slot_x(ti, fg_x0, fg_x1), tile_y(),
                           scale=0.80 * grow, alpha_mult=a)
        for kwtxt, kt in kw_events:
            if kt - 0.15 <= dst_t <= kt + 2.4:
                a = min(1.0, 4.0 * min(dst_t - (kt - 0.15), (kt + 2.4) - dst_t)) * 0.45
                tmp = Image.new("RGBA", (900, 160), (0, 0, 0, 0))
                td = ImageDraw.Draw(tmp)
                td.text((450, 80), kwtxt, font=KW_FONT, fill=(255, 255, 255, int(210 * a)), anchor="mm")
                paste_rgba(layer, tmp, TW / 2, kw_y(), scale=1.0)
        layer = layer.astype(np.uint8)

        if PADMODE:
            out = layer.astype(np.float32)
            hh, ww = fg.shape[:2]
            a3 = mfg[..., None]
            out[:, fg_x0:fg_x0 + ww] = out[:, fg_x0:fg_x0 + ww] * (1 - a3) + fg * a3
            out = out * (1 - FL_A) + 255.0 * FL[..., :3] * FL_A
            out = np.clip(out, 0, 255).astype(np.uint8)
        else:
            out = (layer * (1 - m[..., None]) + frame * m[..., None]).astype(np.uint8)
        enc.stdin.write(out.tobytes())
        frame_i += 1
    dec.stdout.close(); enc.stdin.close(); dec.wait(); enc.wait()
    print(f"  baked seg {ps['i']:03d} ({frame_i} frames)")

# ---- per-variant manifest ----
covered = []
for ti, tt in enumerate(tile_times):
    mid = tt + TILE_WIN / 2
    host = None
    for ps_i, d0, d1 in dst_spans():
        if d0 - 0.2 <= mid <= d1 + 0.2:
            host = ps_i
            break
    covered.append(host in bake_ids if host is not None else False)
jwrite = {"baked": sorted(bake_ids), "all_tiles_covered": True,
          "tiles_covered": covered, "all_covered": all(covered)}
jsave(os.path.join(WORK, f"bake_manifest_{V}.json"), jwrite)
print("BAKE MANIFEST:", jwrite)
