"""v3 creative layer: 8 small concept tiles (popped BEHIND the person by s6b),
ghost keyword events, beat detection from the corrected transcript."""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from common import *

FB = os.path.join(FONTS, "Montserrat-ExtraBold.ttf")
GRAD = [(255, 143, 177), (194, 101, 232), (125, 139, 245)]

def _grad_tile(size=(380, 380), rad=92):
    W, H = size
    px = np.zeros((H, W, 4), dtype=np.uint8)
    yy, xx = np.mgrid[0:H, 0:W]
    t = np.clip(((xx + yy) / np.sqrt(W * W + H * H)), 0, 1) ** 1.1
    n = len(GRAD) - 1
    for c in range(3):
        val = np.zeros_like(t)
        for k in range(n):
            m = np.clip((t - k / n) * n, 0, 1)
            val += GRAD[k][c] * (1 - m) + GRAD[k + 1][c] * m
        px[..., c] = val.astype(np.uint8)
    px[..., 3] = 255
    g = Image.fromarray(px, "RGBA")
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([8, 8, W - 8, H - 8], radius=rad, fill=255)
    out = Image.new("RGBA", size, (0, 0, 0, 0))
    out.paste(g, (0, 0), mask)
    return out

def _finish(canvas, path):
    # soft drop shadow
    W, H = canvas.size
    sh = Image.new("RGBA", (W + 40, H + 60), (0, 0, 0, 0))
    a = canvas.getchannel("A").point(lambda v: int(v * 0.55))
    black = Image.new("RGBA", canvas.size, (10, 10, 20, 255))
    sh.paste(black, (20, 34), a)
    sh = sh.filter(ImageFilter.GaussianBlur(12))
    base = Image.new("RGBA", sh.size, (0, 0, 0, 0))
    base.alpha_composite(sh)
    base.alpha_composite(canvas, (0, 0))
    base.save(path)

def t_sorry(p):
    c = _grad_tile(); d = ImageDraw.Draw(c)
    d.rounded_rectangle([78, 110, 302, 224], radius=34, fill=(255, 255, 255, 255))
    d.polygon([(120, 214), (176, 214), (132, 268)], fill=(255, 255, 255, 255))
    d.text((190, 166), "Sorry?", font=ImageFont.truetype(FB, 56), fill=(176, 83, 201, 255), anchor="mm")
    _finish(c, p)

def t_shield(p):
    c = _grad_tile(); d = ImageDraw.Draw(c)
    cx, cy = 190, 186
    pts = [(cx, cy - 88), (cx + 74, cy - 58), (cx + 74, cy + 24), (cx, cy + 88), (cx - 74, cy + 24), (cx - 74, cy - 58)]
    d.polygon(pts, fill=(255, 255, 255, 255))
    d.line([(cx - 32, cy + 2), (cx - 7, cy + 32), (cx + 36, cy - 26)], fill=(176, 83, 201, 255), width=18, joint="curve")
    _finish(c, p)

def t_heart(p):
    c = _grad_tile(); d = ImageDraw.Draw(c)
    cx, cy, r = 190, 190, 78
    d.ellipse([cx - r, cy - r + 14, cx, cy + 14], fill=(255, 255, 255, 255))
    d.ellipse([cx, cy - r + 14, cx + r, cy + 14], fill=(255, 255, 255, 255))
    d.rectangle([cx - r, cy - 6, cx + r, cy + 14], fill=(255, 255, 255, 255))
    d.polygon([(cx - r, cy - 8), (cx + r, cy - 8), (cx, cy + r + 24)], fill=(255, 255, 255, 255))
    _finish(c, p)

def t_question(p):
    c = _grad_tile(); d = ImageDraw.Draw(c)
    d.ellipse([98, 96, 282, 280], fill=(255, 255, 255, 255))
    d.text((190, 186), "?", font=ImageFont.truetype(FB, 120), fill=(176, 83, 201, 255), anchor="mm")
    _finish(c, p)

def t_mic(p):
    c = _grad_tile(); d = ImageDraw.Draw(c)
    d.rounded_rectangle([162, 92, 218, 218], radius=28, fill=(255, 255, 255, 255))
    d.arc([134, 140, 246, 250], 0, 180, fill=(255, 255, 255, 255), width=16)
    d.line([(190, 246), (190, 282)], fill=(255, 255, 255, 255), width=16)
    d.line([(152, 282), (228, 282)], fill=(255, 255, 255, 255), width=16)
    d.line([(128, 104), (252, 268)], fill=(255, 214, 10, 255), width=18)
    _finish(c, p)

def t_chart(p):
    c = _grad_tile(); d = ImageDraw.Draw(c)
    base = 280
    for i, h in enumerate([140, 100, 66]):
        x = 92 + i * 70
        d.rounded_rectangle([x, base - h, x + 52, base], radius=14, fill=(255, 255, 255, 255))
    _finish(c, p)

def t_door(p):
    c = _grad_tile(); d = ImageDraw.Draw(c)
    d.rounded_rectangle([128, 88, 252, 282], radius=40, fill=(255, 255, 255, 255))
    d.ellipse([214, 176, 234, 196], fill=(176, 83, 201, 255))
    for k in range(3):
        d.arc([40, 60 + k * 26, 130, 150 + k * 26], -60, 60, fill=(255, 255, 255, 210), width=8)
    _finish(c, p)

def t_up(p):
    c = _grad_tile(); d = ImageDraw.Draw(c)
    d.line([(190, 272), (190, 140)], fill=(255, 255, 255, 255), width=26)
    d.polygon([(190, 92), (246, 160), (134, 160)], fill=(255, 255, 255, 255))
    _finish(c, p)

TILE_FUNCS = [t_sorry, t_shield, t_heart, t_question, t_mic, t_chart, t_door, t_up]

TILE_SET = [t_sorry, t_shield, t_question, t_mic, t_chart, t_up]   # curated 6

def build_all(outdir):
    os.makedirs(outdir, exist_ok=True)
    paths = []
    for i, fn in enumerate(TILE_SET):
        p = os.path.join(outdir, f"t{i}.png")
        fn(p)
        paths.append(p)
    return paths

def find_word(words, sub, nth=1):
    hits = [w for w in words if sub in w["w"].lower()]
    return hits[nth - 1]["s"] if len(hits) >= nth else None

def beats(plan):
    w = plan["words"]
    g = lambda s, n=1, d=None: find_word(w, s, n) if find_word(w, s, n) is not None else d
    times = [
        g("sorry", 1) or 0.2,          # sorry bubble
        g("trust", 1) or 20.0,         # shield
        g("permission", 1) or 27.0,    # question
        g("powerless", 1) or 33.0,     # muted mic
        g("credible", 1) or 46.0,      # decline chart
        g("ask", 5) or 57.0,           # up arrow (final ask)
    ]
    kw = [
        ("HARVARD", g("harvard", 1) or 15.0),
        ("POWERLESS", g("powerless", 1) or 33.0),
        ("CREDIBLE", g("credible", 1) or 46.0),
        ("ASK ANYWAY", g("ask", 5) or 57.5),
    ]
    return times, kw
