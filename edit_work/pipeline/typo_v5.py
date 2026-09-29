"""v6 editorial visual system.

Smaller, quieter, warmer than v5:
- cards ~310px wide on the 1080 frame (was ~520) - they support, never dominate
- one warm editorial palette across the whole set: charcoal / ivory / antique gold
  (v5's cool teal glass chart is gone - user rejected the blue/green look)
- chart is drawn programmatically (crisp at any size, perfectly on-palette)
- hairline ivory border + soft shadow on every card so edges read clean
- person stays in front via the s6b mask; nothing ever touches her face
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance
from common import *

ED = os.path.join(ASSETS, "editorial")
PF_IT = os.path.join(FONTS, "Playfair-Italic.ttf")

CARD_W, CARD_H = 520, 690          # master size; scaled down at paste time
CHARCOAL = (28, 26, 22)            # warm charcoal
IVORY = (240, 233, 218)
GOLD = (212, 178, 122)

def cover_crop(img, w, h):
    s = max(w / img.width, h / img.height)
    im = img.resize((int(img.width * s + 0.5), int(img.height * s + 0.5)), Image.LANCZOS)
    x = (im.width - w) // 2
    y = (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))

def _finish_card(img):
    """rounded corners, hairline ivory border, soft drop shadow -> clean edges."""
    w, h = img.size
    S = 2
    big = img.resize((w * S, h * S), Image.LANCZOS)
    mask = Image.new("L", (w * S, h * S), 0)
    ImageDraw.Draw(mask).rounded_rectangle([8, 8, w * S - 8, h * S - 8], radius=52, fill=255)
    big.putalpha(mask)
    # hairline border in ivory (proper alpha composite over the card)
    border = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    ImageDraw.Draw(border).rounded_rectangle([12, 12, w * S - 12, h * S - 12], radius=50,
                                             outline=IVORY + (255,), width=3)
    big = Image.alpha_composite(big, border)
    # soft shadow behind the card
    sh = Image.new("RGBA", (w * S + 160, h * S + 160), (0, 0, 0, 0))
    shm = Image.new("L", (w * S, h * S), 0)
    ImageDraw.Draw(shm).rounded_rectangle([40, 60, w * S - 40, h * S - 20], radius=52, fill=95)
    shm = shm.filter(ImageFilter.GaussianBlur(26))
    sh.paste(Image.new("RGBA", (w * S, h * S), (0, 0, 0, 255)), (80, 80), shm)
    sh.paste(big, (80, 80), big)
    return sh.resize((int(sh.width / S), int(sh.height / S)), Image.LANCZOS)

def editorial_card(src_path, size=(CARD_W, CARD_H)):
    img = Image.open(src_path).convert("RGB")
    img = cover_crop(img, *size)
    img = ImageEnhance.Color(img).enhance(0.68)          # cohesive, quiet
    img = ImageEnhance.Brightness(img).enhance(0.55)
    arr = np.asarray(img).astype(np.float32)
    arr[..., 0] = np.clip(arr[..., 0] * 1.06, 0, 255)    # gentle warm cast
    arr[..., 2] = np.clip(arr[..., 2] * 0.90, 0, 255)
    img = Image.fromarray(arr.astype(np.uint8))
    return _finish_card(img.convert("RGBA"))

def glyph_card(ch, size=(CARD_W, CARD_H)):
    S = 2
    W, H = size[0] * S, size[1] * S
    px = np.zeros((H, W, 3), np.uint8)
    yy, xx = np.mgrid[0:H, 0:W]
    t = ((xx + yy) / (W + H)).astype(np.float32)
    for i, v in ((2, 34), (1, 31), (0, 28)):             # warm charcoal gradient
        px[..., i] = (v * (0.82 + 0.36 * t)).astype(np.uint8)
    c = Image.fromarray(px, "RGB").convert("RGBA")
    d = ImageDraw.Draw(c)
    f = ImageFont.truetype(PF_IT, int(H * 0.52))
    # gold glyph with subtle ivory edge
    d.text((W / 2 + 3 * S, H / 2 + 3 * S), ch, font=f, fill=(0, 0, 0, 120), anchor="mm")
    d.text((W / 2, H / 2), ch, font=f, fill=GOLD + (255,), anchor="mm")
    return _finish_card(c)

def chart_card(size=(CARD_W, CARD_H)):
    """Editorial line chart, drawn: 'credibility drops when you over-apologise'.
    Charcoal panel, faint ivory grid, one ivory line declining, gold endpoint dot."""
    S = 2
    W, H = size[0] * S, size[1] * S
    px = np.zeros((H, W, 3), np.uint8)
    yy, xx = np.mgrid[0:H, 0:W]
    t = ((xx + yy) / (W + H)).astype(np.float32)
    for i, v in ((2, 32), (1, 29), (0, 26)):
        px[..., i] = (v * (0.85 + 0.30 * t)).astype(np.uint8)
    c = Image.fromarray(px, "RGB").convert("RGBA")
    d = ImageDraw.Draw(c)
    ml, mr, mt, mb = int(W * 0.14), int(W * 0.10), int(H * 0.16), int(H * 0.16)
    iw, ih = W - ml - mr, H - mt - mb
    for k in range(5):                                    # faint grid
        y = mt + ih * k / 4
        d.line([(ml, y), (W - mr, y)], fill=IVORY + (26,), width=S)
    for k in range(4):
        x = ml + iw * k / 3
        d.line([(x, mt), (x, H - mb)], fill=IVORY + (16,), width=S)
    pts_t = [0.0, 0.28, 0.55, 0.78, 1.0]
    vals = [0.16, 0.24, 0.44, 0.70, 0.80]                 # y-fraction from top (declining trust)
    pts = [(ml + iw * a, mt + ih * b) for a, b in zip(pts_t, vals)]
    # smooth polyline via many interpolated samples (catmull-rom-ish)
    xs = np.interp(np.linspace(0, 1, 240), pts_t, [p[0] for p in pts])
    ys = np.interp(np.linspace(0, 1, 240), pts_t, [p[1] for p in pts])
    line = list(zip(xs, ys))
    d.line(line, fill=IVORY + (255,), width=9 * S // 2, joint="curve")
    ex, ey = line[-1]
    d.ellipse([ex - 16 * S, ey - 16 * S, ex + 16 * S, ey + 16 * S], fill=GOLD + (255,))
    d.ellipse([ex - 7 * S, ey - 7 * S, ex + 7 * S, ey + 7 * S], fill=(30, 27, 23, 255))
    # small gold tick where the decline begins
    sx, sy = line[0]
    d.ellipse([sx - 9 * S, sy - 9 * S, sx + 9 * S, sy + 9 * S], fill=IVORY + (120,))
    return _finish_card(c)

def build_all(outdir, plan):
    os.makedirs(outdir, exist_ok=True)
    words = plan["words"]
    def g(sub, nth=1, default=None):
        hits = [w for w in words if sub in w["w"].lower()]
        return round(hits[nth - 1]["s"], 2) if len(hits) >= nth else default

    cards_spec = [
        {"id": "harvard",  "src": os.path.join(ED, "harvard_library.jpg"),  "t": g("harvard", 1, 15.0),  "side": "L", "win": 3.4, "scale": 0.62},
        {"id": "qmark",    "glyph": "?",                                    "t": g("permission", 1, 27.0), "side": "R", "win": 3.0, "scale": 0.58},
        {"id": "mic",      "src": os.path.join(ED, "microphone.jpg"),       "t": g("powerless", 1, 33.0), "side": "R", "win": 3.4, "scale": 0.62},
        {"id": "chart",    "chart": True,                                   "t": g("credible", 1, 46.9), "side": "L", "win": 3.4, "scale": 0.62},
    ]
    ghosts = [
        {"text": "HARVARD",   "t": g("harvard", 1, 15.0)},
        {"text": "POWERLESS", "t": g("powerless", 1, 33.0)},
        {"text": "CREDIBLE",  "t": g("credible", 1, 46.9)},
        {"text": "ASK ANYWAY","t": g("ask", 4, 62.9)},
    ]
    files = []
    for spec in cards_spec:
        p = os.path.join(outdir, f"card_{spec['id']}.png")
        if "src" in spec:
            editorial_card(spec["src"]).save(p)
        elif spec.get("chart"):
            chart_card().save(p)
        else:
            glyph_card(spec["glyph"]).save(p)
        spec["file"] = p
        files.append(p)
    jsave(os.path.join(WORK, "typo.json"), {"cards": cards_spec, "ghosts": ghosts})
    print("TYPO v6:", [(c["id"], c["t"]) for c in cards_spec])
    return files
