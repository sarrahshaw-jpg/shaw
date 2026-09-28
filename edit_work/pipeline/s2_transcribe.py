"""Stage 2: transcription with word-level timestamps via whisper.cpp (small model)."""
import os, sys, json, subprocess
from common import *

wh = os.path.join(WORK, "whisper16k.wav")
out_prefix = os.path.join(WORK, "asr")

r = run([WHISPER_BIN, "-m", WHISPER_MODEL, "-f", wh,
         "-l", "en", "-sow", "-ml", "1", "-oj", "-of", out_prefix,
         "-t", "2", "-np"])
js = out_prefix + ".json"
if not os.path.exists(js):
    print("whisper stdout tail:", r.stdout[-800:], r.stderr[-800:])
    raise SystemExit("no transcript produced")

data = json.load(open(js))
words = []
for seg in data.get("transcription", []):
    t = seg["text"].strip()
    s = seg["offsets"]["from"] / 1000.0
    e = seg["offsets"]["to"] / 1000.0
    if not t or t.startswith("[") or t.startswith("("):
        continue  # drop special/sound tokens
    words.append({"w": t, "s": round(s, 3), "e": round(e, 3)})

# merge tokens whisper splits oddly (e.g. "'s") and drop zero-length
merged = []
for w in words:
    if merged and (w["w"].startswith("'") or w["e"] <= w["s"]):
        merged[-1]["w"] += w["w"]
        merged[-1]["e"] = max(merged[-1]["e"], w["e"])
    else:
        merged.append(w)

jsave(os.path.join(WORK, "words.json"), merged)
print(f"TRANSCRIPT: {len(merged)} words")
print(" ".join(w['w'] for w in merged)[:600], "...")
