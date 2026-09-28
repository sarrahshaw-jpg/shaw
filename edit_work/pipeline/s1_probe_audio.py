"""Stage 1: probe the source, build the mastered (HD) audio track + whisper input."""
import os, re, sys, json
from common import *

SRC = sys.argv[1]
os.makedirs(WORK, exist_ok=True)

p = probe(SRC)
jsave(os.path.join(WORK, "probe.json"), p)
print(f"PROBE: {p['w']}x{p['h']} @ {p['fps']}fps  {p['dur']:.1f}s  audio={p['has_audio']} codec={p['vcodec']}")
if not p["has_audio"]:
    print("FATAL: source has no audio track"); sys.exit(1)

# silence map for head/tail trim
r = run([FFMPEG, "-hide_banner", "-i", SRC, "-vn", "-af",
         "silencedetect=noise=-32dB:d=0.40", "-f", "null", "-"])
sil_s = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", r.stderr)]
sil_e = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r.stderr)]
jsave(os.path.join(WORK, "silence.json"), {"starts": sil_s, "ends": sil_e})
print(f"SILENCE: {len(sil_s)} regions")

# ---- audio master: clean -> tone -> control -> loud  (the "HD voice" chain)
deesser = "deesser=i=0.35:m=0.5:f=0.5"
chain = [
    "highpass=f=78",                     # rumble/handling noise out
    "adeclick",                          # clicks/pops
    f"arnndn=m={RNNN}:mix=0.92",         # AI broadband denoise (voice-preserving blend)
    "equalizer=f=190:t=q:w=0.9:g=-2.2",  # de-mud
    "equalizer=f=2800:t=q:w=1.3:g=2.6",  # presence/clarity
    "treble=g=1.6:f=9500",               # air
    "bass=g=1.6:f=110",                  # warmth
    deesser,                             # tame harsh S
    "acompressor=threshold=-19dB:ratio=2.6:attack=9:release=130:makeup=5:campaign=0:frequency=0:knee=6".replace(":campaign=0:frequency=0", ""),
    "alimiter=limit=0.93:level=false",   # transparent peak control
]
af = ",".join(chain)
master = os.path.join(WORK, "master_audio.wav")
sh([FFMPEG, "-y", "-hide_banner", "-loglevel", "error", "-i", SRC, "-vn",
    "-af", af, "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", master])
print("MASTER AUDIO OK ->", master)

# whisper input: same cleaning, 16k mono
wh = os.path.join(WORK, "whisper16k.wav")
sh([FFMPEG, "-y", "-hide_banner", "-loglevel", "error", "-i", master,
    "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", wh])
print("WHISPER INPUT OK ->", wh)
