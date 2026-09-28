"""Stage 5: design assets per target - face light, keyword-behind-head art, emoji stickers,
karaoke caption .ass files."""
import os, math, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from common import *

EDIT_STYLE = os.environ.get("EDIT_STYLE", "default")
if EDIT_STYLE == "ref":
    import style_ref

plan = jload(os.path.join(WORK, "plan.json"))
faces = jload(os.path.join(WORK, "faces.json"))
probe = jload(os.path.join(WORK, "probe.json"))
FB_W = os.path.join(WORK, "fb_font.ttf")

FB = os.path.join(FONTS, "Montserrat-ExtraBold.ttf")
FB_SZ = {"ld": 138, "ig": 104}
ASS_SZ = {"ld": 56, "ig": 64}

ASS_HDR = """[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,{font},{sz},&H00FFFFFF,&H00FFFFFF,&H00101010,&H96000000,-1,0,0,0,100,100,{spacing},0,1,{outline},{shadow},2,60,60,{margV},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

def ts(t):
    t = max(0, t)
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"

def draw_spaced(d, xy, text, font, fill, spacing):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=font, fill=fill)
        x += d.textlength(ch, font=font) + spacing

# src -> dst mapping (same logic as planner)
offsets = []
t_dst = 0.0
for ps in plan["segments"]:
    offsets.append((ps["src_s"], ps["src_e"], t_dst))
    t_dst += ps["dur"] - ps["tr_after"]
def src2dst(t):
    for s, e, b in offsets:
        if s <= t < e:
            return b + (t - s)
    return min(max(t, 0), plan["new_dur"])

for v, T in TARGETS.items():
    TW, TH = T["w"], T["h"]
    fdir = os.path.join(WORK, "gfx", v)
    os.makedirs(fdir, exist_ok=True)

    # ---------- face geometry in OUTPUT space ----------
    fcx, fcy, fw, fh = faces.get("cx", TW/2), faces.get("cy", TH*0.38), faces.get("w", TW*0.25), faces.get("h", TH*0.3)
    if v == "ld":
        # near full-frame crop, slight zoom: keep source coords, mild recentre
        z = 1.045
        ox = (TW - 0) / 2
        out_cx = (fcx - TW / 2) * z * 0.55 + TW / 2
        out_cy = (fcy - TH / 2) * z * 0.55 + TH / 2
        out_w, out_h = fw * z, fh * z
    else:
        # 9:16 crop centers on face
        z = 1.045
        crop_w = TH * 9 / 16
        out_cx = TW / 2
        out_cy = (fcy - TH / 2) * z * 0.75 + TH * 0.46
        out_w, out_h = fw * z, fh * z
        out_w = out_w * (TW / crop_w)   # face appears larger in tighter frame
        out_h = out_h * (TW / crop_w)

    # ---------- 1. face light (white glow, alpha-composited - color-safe) ----------
    yy, xx = np.mgrid[0:TH, 0:TW].astype(np.float32)
    rx, ry = max(out_w * 2.0, TW * 0.28), max(out_h * 1.55, TH * 0.20)
    core = np.exp(-(((xx - out_cx) / rx) ** 2 + ((yy - out_cy) / ry) ** 2) * 2.4)
    top = np.exp(-(((xx - out_cx) / (rx * 1.6)) ** 2 + ((yy - (out_cy - out_h * 1.15)) / (ry * 1.7)) ** 2) * 2.0)
    alpha = np.clip(core * 62 + top * 28, 0, 84).astype(np.uint8)
    w255 = np.full_like(alpha, 255)
    img = np.dstack([w255, w255, w255, alpha])
    Image.fromarray(img, "RGBA").save(os.path.join(fdir, "face_light.png"))

    # ---------- 2-4. style-dependent graphics ----------
    if EDIT_STYLE == "ref":
        # v4 premium phrase captions: word-timed, strategic accent, clean type
        events = style_ref.phrase_captions(plan["words"], plan.get("emphasis", []))
        mL, mR = (240, 240) if (v == "ld" and probe.get("w", 0) < probe.get("h", 0)) else (40, 40)
        style_ref.write_phrase_ass(events, os.path.join(fdir, "captions.ass"), TW, TH,
                                   plan.get("emphasis", []), mL, mR)
        continue

    # ---------- 2. keyword-behind-head art ----------
    font = ImageFont.truetype(FB, FB_SZ[v])
    for k, kw in enumerate(plan["keywords"][:5]):
        canvas = Image.new("RGBA", (TW, TH), (0, 0, 0, 0))
        d = ImageDraw.Draw(canvas)
        text = kw["text"]
        sp = FB_SZ[v] * 0.10
        tw = sum(d.textlength(c, font=font) + sp for c in text) - sp
        tx = min(max(out_cx - tw / 2, 30), TW - tw - 30)
        ty = out_cy - out_h / 2 - FB_SZ[v] * 1.30          # text floats just above the head
        ty = max(24, ty)
        draw_spaced(d, (tx + 3, ty + 3), text, font, (10, 10, 14, 80), sp)   # soft shadow for legibility
        draw_spaced(d, (tx, ty), text, font, (255, 255, 255, 58), sp)
        # punch a feathered hole where the head is -> text hides BEHIND the head
        hole = Image.new("L", (TW, TH), 0)
        hd = ImageDraw.Draw(hole)
        hd.ellipse([out_cx - out_w * 0.62, out_cy - out_h * 0.78,
                    out_cx + out_w * 0.62, out_cy + out_h * 0.62], fill=255)
        hole = hole.filter(ImageFilter.GaussianBlur(FB_SZ[v] * 0.22))
        a = canvas.getchannel("A")
        a = Image.fromarray((np.array(a).astype(np.float32) * (1 - np.array(hole).astype(np.float32) / 255)).astype(np.uint8))
        canvas.putalpha(a)
        canvas.save(os.path.join(fdir, f"kw{k}.png"))

    # ---------- 3. emoji stickers (with soft shadow) ----------
    CS = 260
    for m_i, m in enumerate(plan["emojis"]):
        src = Image.open(os.path.join(EMOJI, m["code"] + ".png")).convert("RGBA")
        es = 178 if v == "ld" else 196
        em = src.resize((es, es), Image.LANCZOS)
        canvas = Image.new("RGBA", (CS, CS), (0, 0, 0, 0))
        sh = Image.new("RGBA", (CS, CS), (0, 0, 0, 0))
        sd = ImageDraw.Draw(sh)
        sd.ellipse([CS/2-es*0.32, CS/2+es*0.30, CS/2+es*0.32, CS/2+es*0.44], fill=(0, 0, 0, 110))
        sh = sh.filter(ImageFilter.GaussianBlur(9))
        canvas = Image.alpha_composite(canvas, sh)
        canvas.alpha_composite(em, (CS//2 - es//2, CS//2 - es//2 - 6))
        canvas.save(os.path.join(fdir, f"em{m_i}.png"))

    # ---------- 4. karaoke captions (default style) ----------
    margV = 118 if v == "ld" else 620
    hdr = ASS_HDR.format(W=TW, H=TH, font="Montserrat", sz=ASS_SZ[v],
                         outline=3.2 if v == "ld" else 3.8, shadow=1.0,
                         spacing=0.6, margV=margV)
    lines = []
    HILITE = "{\\c&H0AD6FF&\\fscx109\\fscy109\\t(0,110,\\fscx100\\fscy100)}"
    RESET = "{\\r}"
    for g in plan["captions"]:
        ws = g["words"]
        for i, w in enumerate(ws):
            start = g["s"] if i == 0 else w["s"]
            end = ws[i + 1]["s"] if i < len(ws) - 1 else g["e"]
            if end - start <= 0.02:
                continue
            parts = [((HILITE + ws[j]["w"].strip() + RESET) if j == i else ws[j]["w"].strip())
                     for j in range(len(ws))]
            text = " ".join(parts)
            lines.append(f"Dialogue: 0,{ts(start)},{ts(end)},Cap,,0,0,0,,{text}")
    with open(os.path.join(fdir, "captions.ass"), "w") as f:
        f.write(hdr + "\n".join(lines) + "\n")


# ---------- shared concept tiles (ref style) ----------
if EDIT_STYLE == "ref":
    import tiles_v3
    v3dir = os.path.join(WORK, "gfx", "shared_v3")
    tpaths = tiles_v3.build_all(v3dir)
    times, kws = tiles_v3.beats(plan)
    jsave(os.path.join(WORK, "tiles_v3.json"),
          {"files": tpaths, "times": [round(t, 3) for t in times], "win": 2.1,
           "keywords": [[k, round(t, 3)] for k, t in kws]})
    jsave(os.path.join(WORK, "tiles.json"),
          {"files": tpaths, "times": [round(t, 3) for t in times], "win": 2.1})
    print("TILES v3:", [round(t, 1) for t in times], "| keywords:", [k for k, _ in kws])
print("GRAPHICS OK for", list(TARGETS.keys()))
