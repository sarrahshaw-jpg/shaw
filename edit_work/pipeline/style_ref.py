"""LinkedIn-Learning style layer (reference match):
- sentence-case white captions on a translucent dark pill (bottom)
- big soft-gradient concept tiles popping mid-frame at script beats
Used when EDIT_STYLE=ref. Everything drawn with PIL - no external deps.
"""
import os, math, numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from common import *

FB = os.path.join(FONTS, "Montserrat-ExtraBold.ttf")
FM = os.path.join(FONTS, "Montserrat-Medium.ttf")

GRAD = [(255, 143, 177), (194, 101, 232), (125, 139, 245)]   # pink -> purple -> periwinkle

def _grad_rounded(size, rad, inset):
    W, H = size
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    g = Image.new("RGBA", (W, H))
    px = np.zeros((H, W, 4), dtype=np.uint8)
    diag = np.sqrt(W ** 2 + H ** 2)
    yy, xx = np.mgrid[0:H, 0:W]
    t = np.clip(((xx + yy) / diag), 0, 1) ** 1.1
    n = len(GRAD) - 1
    for c in range(3):
        val = np.zeros_like(t)
        for k in range(n):
            t0, t1 = k / n, (k + 1) / n
            m = np.clip((t - t0) / (t1 - t0), 0, 1)
            val += GRAD[k][c] * (1 - m) + GRAD[k + 1][c] * m
        px[..., c] = val.astype(np.uint8)
    px[..., 3] = 255
    g = Image.fromarray(px, "RGBA")
    mask = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(mask)
    d.rounded_rectangle([inset, inset, W - inset, H - inset], radius=rad, fill=255)
    img.paste(g, (0, 0), mask)
    return img

def _shadow_canvas(size, strength=90, blur=18, yoff=26):
    W, H = size
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(sh)
    d.ellipse([W * 0.22, H * 0.80, W * 0.78, H * 1.02], fill=(0, 0, 0, strength))
    return sh.filter(ImageFilter.GaussianBlur(blur))

def _tile_base(size=(640, 640)):
    W, H = size
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    canvas.alpha_composite(_shadow_canvas(size))
    tile = _grad_rounded(size, rad=150, inset=52)
    canvas.alpha_composite(tile)
    return canvas

def tile_sorry(path):
    c = _tile_base()
    d = ImageDraw.Draw(c)
    # white speech bubble
    bx0, by0, bx1, by1 = 130, 190, 510, 380
    d.rounded_rectangle([bx0, by0, bx1, by1], radius=54, fill=(255, 255, 255, 255))
    d.polygon([(215, 370), (300, 370), (225, 460)], fill=(255, 255, 255, 255))
    f = ImageFont.truetype(FB, 92)
    d.text(((bx0 + bx1) / 2, (by0 + by1) / 2), "Sorry?", font=f, fill=(176, 83, 201, 255), anchor="mm")
    c.save(path)

def tile_trust(path):
    c = _tile_base()
    d = ImageDraw.Draw(c)
    # shield with check
    cx, cy = 320, 300
    pts = [(cx, cy - 150), (cx + 128, cy - 100), (cx + 128, cy + 40),
           (cx, cy + 150), (cx - 128, cy + 40), (cx - 128, cy - 100)]
    d.polygon(pts, fill=(255, 255, 255, 255))
    d.line([(cx - 55, cy + 5), (cx - 12, cy + 55), (cx + 62, cy - 45)],
           fill=(176, 83, 201, 255), width=30, joint="curve")
    c.save(path)

def tile_question(path):
    c = _tile_base()
    d = ImageDraw.Draw(c)
    d.ellipse([170, 130, 470, 430], fill=(255, 255, 255, 255))
    f = ImageFont.truetype(FB, 210)
    d.text((320, 272), "?", font=f, fill=(176, 83, 201, 255), anchor="mm")
    c.save(path)

def tile_chart(path):
    c = _tile_base()
    d = ImageDraw.Draw(c)
    base = 470
    for i, h in enumerate([250, 180, 120]):
        x = 155 + i * 130
        d.rounded_rectangle([x, base - h, x + 95, base], radius=26, fill=(255, 255, 255, 255))
    d.line([(180, 205), (300, 285), (420, 240)], fill=(255, 255, 255, 255), width=0)
    arr = [(415, 330), (470, 330), (442, 380)]
    d.polygon(arr, fill=(255, 255, 255, 255))
    c.save(path)

def build_tiles(gfx_dir):
    os.makedirs(gfx_dir, exist_ok=True)
    paths = [os.path.join(gfx_dir, f"tile{i}.png") for i in range(4)]
    tile_sorry(paths[0]); tile_trust(paths[1]); tile_question(paths[2]); tile_chart(paths[3])
    return paths

# ---------------- captions: sentence chunks, pill box ----------------
def chunk_captions(words, max_chars=58):
    """Sentence-first chunking; long sentences split at clause punctuation
    (comma/dash/colon) so captions never break mid-thought. libass wraps
    <=58-char events into max two lines."""
    sents, cur = [], []
    for w in words:
        cur.append(w)
        if w["w"].rstrip().endswith((".", "!", "?")):
            sents.append(cur); cur = []
    if cur:
        sents.append(cur)

    def mk(ws):
        return {"s": ws[0]["s"], "e": ws[-1]["e"] + 0.15,
                "text": " ".join(x["w"].strip() for x in ws)}

    events = []
    for s in sents:
        txt = " ".join(x["w"].strip() for x in s)
        if len(txt) <= max_chars:
            events.append(mk(s))
            continue
        # split at clause punctuation nearest to the middle-limit
        cut = None
        for i in range(1, len(s)):
            if len(" ".join(x["w"] for x in s[:i])) > max_chars:
                break
            if s[i - 1]["w"].rstrip()[-1:] in ",;:—-":
                cut = i
        if cut is None:
            cut = max(1, len(s) // 2)
            # avoid splitting contractions/pairs: shift to a word boundary is fine
        e1 = mk(s[:cut])
        e1["e"] = s[cut]["s"] - 0.02 if cut < len(s) else e1["e"]
        events.append(e1)
        rest = s[cut:]
        # recurse for very long remainder
        if len(" ".join(x["w"] for x in rest)) > max_chars * 1.6:
            mid = len(rest) // 2
            e2 = mk(rest[:mid]); e2["e"] = rest[mid]["s"] - 0.02
            events.append(e2)
            events.append(mk(rest[mid:]))
        else:
            events.append(mk(rest))
    # enforce sequential timing
    for a, b in zip(events, events[1:]):
        if a["e"] > b["s"] - 0.02:
            a["e"] = max(a["s"] + 0.18, b["s"] - 0.02)
    return events

ASS_HDR = """[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Pill,Montserrat,{sz},&H00FFFFFF,&H00FFFFFF,&H00000000,&H50000000,0,0,0,0,100,100,0.2,0,3,14,0,2,{mL},{mR},{mV},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

def ts(t):
    t = max(0, t)
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"

def write_pill_ass(events, path, TW, TH, mL=40, mR=40, mV=230):
    sz = 58 if TH >= TW else 52
    hdr = ASS_HDR.format(W=TW, H=TH, sz=sz, mL=mL, mR=mR, mV=mV)
    lines = [f"Dialogue: 0,{ts(e['s'])},{ts(e['e'])},Pill,,0,0,0,,{e['text']}" for e in events]
    with open(path, "w") as f:
        f.write(hdr + "\n".join(lines) + "\n")

# ---------------- beat times ----------------
def beat_times(plan):
    """find dst-times for the four concept tiles from the transcript."""
    words = plan["words"]
    def find(sub, nth=1):
        hits = [w for w in words if sub in w["w"].lower()]
        return hits[nth - 1]["s"] if len(hits) >= nth else None
    t1 = find("sorry", 1) or 0.4                     # hook apology
    t2 = find("trust", 1) or plan["new_dur"] * 0.40  # studies -> trust
    t3 = find("permission", 1) or plan["new_dur"] * 0.55  # permission
    t4 = find("credible", 1) or plan["new_dur"] * 0.85    # credibility drop
    return [t1, t2, t3, t4]


# ---------------- v4: premium phrase captions ----------------
def normtok(s):
    import re as _re
    return _re.sub(r"[^a-z']", "", s.lower().replace("\u2019", "'")).strip("'")

def phrase_captions(words, emphasis, max_words=3, max_chars=18):
    """2-3 word phrases, broken at punctuation/natural pauses."""
    events, cur = [], []
    for w in words:
        cur.append(w)
        txt = " ".join(x["w"].strip() for x in cur)
        endp = w["w"].rstrip().rstrip("\"'”’")[-1:] in ",.!?;:"
        nxt_gap = None
        if endp or len(cur) >= max_words or len(txt) > max_chars:
            events.append({"words": cur, "s": cur[0]["s"], "e": cur[-1]["e"] + 0.14})
            cur = []
    if cur:
        events.append({"words": cur, "s": cur[0]["s"], "e": cur[-1]["e"] + 0.14})
    for a, b in zip(events, events[1:]):
        if a["e"] > b["s"] - 0.02:
            a["e"] = max(a["s"] + 0.15, b["s"] - 0.02)
    return events

ACCENT = "&HFFD60A&"      # warm gold (BGR)
WHITE = "&HFFFFFF&"

def write_phrase_ass(events, path, TW, TH, emphasis, mL=40, mR=40, mV=None):
    if mV is None:
        mV = int(TH * 0.205)
    sz = 52 if TH >= TW else 46
    emph = set(emphasis or [])
    hdr = ASS_HDR_PHRASE.format(W=TW, H=TH, sz=sz, mL=mL, mR=mR, mV=mV)
    lines = []
    for ev in events:
        ws = ev["words"]
        for i, w in enumerate(ws):
            start = ev["s"] if i == 0 else w["s"]
            end = ws[i + 1]["s"] if i < len(ws) - 1 else ev["e"]
            if end - start <= 0.03:
                continue
            key = normtok(w["w"])
            parts = []
            for j, wj in enumerate(ws):
                tok = wj["w"].strip()
                kj = normtok(wj["w"])
                if j == i:
                    if kj in emph:
                        tag = "{\\c" + ACCENT + "\\fscx107\\fscy107\\t(0,90,\\fscx100\\fscy100)}"
                    else:
                        tag = "{\\fscx105\\fscy105\\t(0,90,\\fscx100\\fscy100)}"
                    parts.append(tag + tok + "{\\r}")
                else:
                    parts.append(tok)
            lines.append(f"Dialogue: 0,{ts(start)},{ts(end)},Cap,,0,0,0,,{' '.join(parts)}")
    with open(path, "w") as f:
        f.write(hdr + "\n".join(lines) + "\n")

ASS_HDR_PHRASE = """[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Montserrat,{sz},&H00FFFFFF,&H00FFFFFF,&H282828,&H8C000000,-1,0,0,0,100,100,0.4,0,1,2.6,1.4,2,{mL},{mR},{mV},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
