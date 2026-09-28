"""Shared utilities for the edit pipeline."""
import json, os, re, subprocess, shlex, sys

CACHE = "/home/user/cache_big"
WORK  = "/home/user/cache_big/build"
ASSETS= "/home/user/shaw/edit_work/assets"
SEGS  = {"ld": os.path.join(WORK, "segs_ld"), "ig": os.path.join(WORK, "segs_ig")}
OUT   = "/home/user/shaw/edits"

FFMPEG = "/home/user/shaw/edit_work/tools/bin/ffmpeg"
RNNN   = os.path.join(ASSETS, "rnnoise/somnolent-hogwash-2018-09-01/sh.rnnn")
FONTS  = os.path.join(ASSETS, "fonts")
EMOJI  = os.path.join(ASSETS, "emoji")
WHISPER_BIN = "/home/user/shaw/edit_work/tools/whisper.cpp/build/bin/whisper-cli"
WHISPER_MODEL = os.path.join(CACHE, "ggml-small.bin")

TARGETS = {
    "ld": {"w": 1920, "h": 1080, "name": "LinkedIn 16:9"},
    "ig": {"w": 1080, "h": 1920, "name": "Instagram Reel 9:16"},
}

def sh(cmd, **kw):
    """Run a command, echo on failure."""
    r = subprocess.run(cmd, shell=isinstance(cmd, str), capture_output=True, text=True, **kw)
    if r.returncode != 0:
        print("CMD FAILED:", cmd if isinstance(cmd, str) else " ".join(cmd))
        print(r.stderr[-3000:])
        raise SystemExit(1)
    return r

def run(cmd):
    return subprocess.run(cmd, shell=isinstance(cmd, str), capture_output=True, text=True)

def jload(p, default=None):
    if not os.path.exists(p):
        return default
    with open(p) as f:
        return json.load(f)

def jsave(p, obj):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w") as f:
        json.dump(obj, f, indent=1)

def probe(path):
    r = run([FFMPEG, "-hide_banner", "-i", path])
    err = r.stderr
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.?\d*)", err)
    dur = int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3]) if m else 0.0
    w = h = fps = 0
    has_audio = "Audio:" in err
    m = re.search(r"Video:.*?(\d{2,5})x(\d{2,5})", err)
    if m:
        w, h = int(m[1]), int(m[2])
    m = re.search(r"(\d+(?:\.\d+)?) fps", err)
    if m:
        fps = float(m[1])
    m = re.search(r"Video: (\w+)", err)
    vcodec = m[1] if m else "?"
    return {"dur": dur, "w": w, "h": h, "fps": fps or 30.0, "has_audio": has_audio, "vcodec": vcodec}
