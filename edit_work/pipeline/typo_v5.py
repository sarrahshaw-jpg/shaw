"""v5 editorial visual system - replaces stickers/tiles entirely.

Editorial cards: photographic stills (cinematic), cover-cropped, darkened +
desaturated + vignetted so they read as environment behind the speaker.
Glyphs: huge Playfair italic punctuation as typographic art.
Ghost keywords: Playfair italic, very soft, above the head, never on the face.
All drawn on the BACKGROUND layer in s6b - person mask keeps her in front.
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance
from common import *

ED = os.path.join(ASSETS, "editorial")
PF_IT = os.path.join(FONTS, "Playfair-Italic.ttf")

def cover_crop(img, w, h):
    s = max(w / img.width, h / img.height)
    im = img.resize((int(img.width * s + 0.5), int(img.height * s + 0.5)), Image.LANCZOS)
    x = (im.width - w) // 2
    y = (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))

def editorial_card(src_path, size=(560, 740)):
    img = Image.open(src_path).convert("RGB")
    img = cover_crop(img, *size)
    img = ImageEnhance.Color(img).enhance(0.82)
    img = ImageEnhance.Brightness(img).enhance(0.60)
    mask = Image.new("L", (size[0] * 2, size[1] * 2), 0)
    d = ImageDraw.Draw(mask)
    d.ellipse([-size[0] * 0.35, -size[1] * 0.25, size[0] * 2.35, size[1] * 2.25], fill=255)
    mask = mask.resize(size).filter(ImageFilter.GaussianBlur(60))
    dark = Image.new("RGB", size, (8, 9, 12))
    img = Image.composite(img, dark, mask)
    out = img.convert("RGBA")
    a = Image.new("L", (size[0] * 2, size[1] * 2), 0)
    da = ImageDraw.Draw(a)
    da.rounded_rectangle([10, 10, size[0] * 2 - 10, size[1] * 2 - 10], radius=48, fill=255)
    a = a.resize(size).filter(ImageFilter.GaussianBlur(18))
    out.putalpha(a)
    return out

def ghost_editorial(text, W=1000, H=200, px=104):
    font = ImageFont.truetype(PF_IT, px)
    tmp = Image.new("RGBA", (W * 2, H * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(tmp)
    d.text((W, H), text, font=font, fill=(242, 240, 235, 255), anchor="mm")
    a = tmp.getchannel("A").point(lambda v: int(v * 0.40))
    tmp.putalpha(a)
    bbox = tmp.getbbox()
    if bbox:
        pad = 40
        bbox = (max(0, bbox[0] - pad), max(0, bbox[1] - pad),
                min(tmp.width, bbox[2] + pad), min(tmp.height, bbox[3] + pad))
        tmp = tmp.crop(bbox)
    return tmp.resize((tmp.width // 2, tmp.height // 2), Image.LANCZOS)

def glyph_card(ch, size=(560, 740)):
    c = Image.new("RGBA", size, (0, 0, 0, 0))
    px = np.zeros((size[1], size[0], 4), np.uint8)
    yy, xx = np.mgrid[0:size[1], 0:size[0]]
    t = (xx + yy) / (size[0] + size[1])
    for i, v in ((2, 16), (1, 15), (0, 18)):
        px[..., i] = (v * (0.75 + 0.5 * t)).astype(np.uint8)
    px[..., 3] = 255
    grad = Image.fromarray(px, "RGBA")
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([8, 8, size[0] - 8, size[1] - 8], radius=44, fill=255)
    c.paste(grad, (0, 0), mask)
    d = ImageDraw.Draw(c)
    f = ImageFont.truetype(PF_IT, int(size[1] * 0.52))
    d.text((size[0] / 2, size[1] / 2), ch, font=f, fill=(238, 236, 230, 255), anchor="mm")
    a = Image.new("L", size, 0)
    ImageDraw.Draw(a).rounded_rectangle([8, 8, size[0] - 8, size[1] - 8], radius=44, fill=255)
    a = a.filter(ImageFilter.GaussianBlur(2))
    c.putalpha(a)
    return c

def build_all(outdir, plan):
    os.makedirs(outdir, exist_ok=True)
    words = plan["words"]
    def g(sub, nth=1, default=None):
        hits = [w for w in words if sub in w["w"].lower()]
        return round(hits[nth - 1]["s"], 2) if len(hits) >= nth else default

    cards_spec = [
        {"id": "harvard",  "src": os.path.join(ED, "harvard_library.jpg"),  "t": g("harvard", 1, 15.0),  "side": "L", "win": 3.4, "scale": 0.92},
        {"id": "qmark",    "glyph": "?",                                    "t": g("permission", 1, 27.0), "side": "R", "win": 3.0, "scale": 0.88},
        {"id": "mic",      "src": os.path.join(ED, "microphone.jpg"),       "t": g("powerless", 1, 33.0), "side": "R", "win": 3.4, "scale": 0.92},
        {"id": "chart",    "src": os.path.join(ED, "credibility_chart.png"),"t": g("credible", 1, 46.9), "side": "L", "win": 3.4, "scale": 0.92},
    ]
    ghosts = [
        {"text": "HARVARD",   "t": g("harvard", 1, 15.0)},
        {"text": "POWERLESS", "t": g("powerless", 1, 33.0)},
        {"text": "CREDIBLE",  "t": g("credible", 1, 46.9)},
        {"text": "ASK ANYWAY","t": g("ask", 5, 57.5)},
    ]
    files = []
    for spec in cards_spec:
        p = os.path.join(outdir, f"card_{spec['id']}.png")
        if "src" in spec:
            editorial_card(spec["src"]).save(p)
        else:
            glyph_card(spec["glyph"]).save(p)
        spec["file"] = p
        files.append(p)
    jsave(os.path.join(WORK, "typo.json"), {"cards": cards_spec, "ghosts": ghosts})
    print("TYPO v5:", [(c["id"], c["t"]) for c in cards_spec])
    return files
