"""Stage 7: final assembly per variant - xfade transitions, keyword/emoji overlays,
caption burn, two-pass -14 LUFS audio, mux."""
import os, sys, json, re
from common import *

V = sys.argv[1]
plan = jload(os.path.join(WORK, "plan.json"))
T = TARGETS[V]
TW, TH = T["w"], T["h"]
segs = plan["segments"]
GFX = os.path.join(WORK, "gfx", V)
SODIR = SEGS[V]
ODIR = os.path.join(WORK, "out", V)
os.makedirs(ODIR, exist_ok=True)

seg_files = [os.path.join(SODIR, f"seg_{ps['i']:03d}.mp4") for ps in segs]
for f in seg_files:
    if not os.path.exists(f):
        raise SystemExit(f"missing segment {f}")

# src->dst time mapping (matches s5/s3 logic)
_offsets = []
_t = 0.0
for _ps in segs:
    _offsets.append((_ps["src_s"], _ps["src_e"], _t))
    _t += _ps["dur"] - _ps["tr_after"]
def src2dst(t):
    for s, e, b in _offsets:
        if s <= t < e:
            return b + (t - s)
    return min(max(t, 0), plan["new_dur"])

big_i = 0
trans = []
for ps in segs[:-1]:
    if ps["tr_after"] >= 0.26 and big_i < 3:
        trans.append(("smoothleft" if big_i % 2 == 0 else "smoothup", ps["tr_after"]))
        big_i += 1
    else:
        trans.append(("fade", ps["tr_after"]))

# ---------------- inputs ----------------
cmd = [FFMPEG, "-y", "-hide_banner", "-loglevel", "error"]
for f in seg_files:
    cmd += ["-i", f]

CS = 260
overlays = []   # (kind, file, start, win, pos_idx)
if os.environ.get("EDIT_STYLE") == "ref":
    if V == "ld":
        typo = jload(os.path.join(WORK, "typo.json"), {"cards": []})
        for c in typo["cards"]:
            if os.path.exists(c.get("file", "")):
                s = min(max(c["t"], 0.3), plan["new_dur"] - c["win"] - 0.4)
                overlays.append(("card", c["file"], s, c["win"], 0 if c["side"] == "L" else 1))


for kind, f, s, win, _ in overlays:
    cmd += ["-loop", "1", "-t", f"{win:.3f}", "-i", f]

# ---------------- video graph: plain concat (frame-accurate sync, no overlaps) ----------------
parts = []
parts.append("".join(f"[{i}:v]" for i in range(len(seg_files))) +
             f"concat=n={len(seg_files)}:v=1:a=0[cc]")
base = "cc"
TILE_SCALE = {"ld": 0.78, "ig": 1.0}[V]
for oi, (kind, f, s, win, pos_i) in enumerate(overlays):
    idx = len(seg_files) + oi
    lab_in = f"o{oi}"
    if kind == "card":
        CW2, CH2 = 457, 604
        parts.append(f"[{idx}:v]scale={CW2}:{CH2}:flags=bicubic,"
                     f"format=rgba,fade=t=in:st=0:d=0.35:alpha=1,"
                     f"fade=t=out:st={win-0.40:.2f}:d=0.40:alpha=1,setpts=PTS-STARTPTS+{s:.3f}/TB[{lab_in}]")
        fg_w = int(TH * 9 / 16 * 0.98)
        bar = (TW - fg_w) // 2
        X = (bar - CW2) // 2 if pos_i == 0 else TW - (bar - CW2) // 2 - CW2
        Y = (TH - CH2) // 2
        parts.append(f"[{base}][{lab_in}]overlay={X}:{Y}:"
                     f"enable='between(t,{s:.3f},{s+win:.3f})':eof_action=pass[b{oi}]")
    elif kind == "tile":
        parts.append(f"[{idx}:v]zoompan=z='1.07-0.07*on/(25*{win:.2f})':d=1:s=640x640:fps=25,"
                     f"scale={int(640*TILE_SCALE)}:{int(640*TILE_SCALE)}:flags=bicubic,"
                     f"format=rgba,fade=t=in:st=0:d=0.20:alpha=1,"
                     f"fade=t=out:st={win-0.30:.2f}:d=0.30:alpha=1,setpts=PTS-STARTPTS+{s:.3f}/TB[{lab_in}]")
        _w = int(640 * TILE_SCALE)
        if V == "ld":
            fg_w = int(TH * 9 / 16 * 0.98)
            bar = (TW - fg_w) // 2
            side_left = (pos_i % 2 == 0)
            X = (bar - _w) // 2 if side_left else TW - (bar - _w) // 2 - _w
            Y = int(TH * 0.34) if pos_i % 3 else int(TH * 0.58)
        else:
            X = (TW - _w) // 2
            Y = int(TH * 0.72 - _w / 2)
        parts.append(f"[{base}][{lab_in}]overlay={X}:{Y}:"
                     f"enable='between(t,{s:.3f},{s+win:.3f})':eof_action=pass[b{oi}]")
    elif kind == "kw":
        parts.append(f"[{idx}:v]format=rgba,fade=t=in:st=0:d=0.28:alpha=1,"
                     f"fade=t=out:st={win-0.30:.2f}:d=0.30:alpha=1,setpts=PTS-STARTPTS+{s:.3f}/TB[{lab_in}]")
        parts.append(f"[{base}][{lab_in}]overlay=0:0:enable='between(t,{s:.3f},{s+win:.3f})':eof_action=pass[b{oi}]")
    else:
        px, py = emoji_pos[pos_i]
        X = px * TW - CS / 2
        Y = py * TH - CS / 2
        parts.append(f"[{idx}:v]format=rgba,fade=t=in:st=0:d=0.16:alpha=1,"
                     f"fade=t=out:st={win-0.22:.2f}:d=0.22:alpha=1,setpts=PTS-STARTPTS+{s:.3f}/TB[{lab_in}]")
        yex = f"{Y:.0f}-14*min(max(t-{s:.3f}\\,0)/0.55\\,1)"
        parts.append(f"[{base}][{lab_in}]overlay=x={X:.0f}:y='{yex}':"
                     f"enable='between(t,{s:.3f},{s+win:.3f})':eof_action=pass[b{oi}]")
    base = f"b{oi}"

capf = os.path.join(GFX, "captions.ass").replace(":", "\\:")
parts.append(f"[{base}]subtitles=filename='{capf}':fontsdir={FONTS},format=yuv420p[vout]")

video_out = os.path.join(ODIR, "video_noaudio.mp4")
cmd += ["-filter_complex", ";".join(parts), "-map", "[vout]",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-profile:v", "high",
        "-level", "4.1", "-g", "60", "-movflags", "+faststart",
        "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
        video_out]
r = run(cmd)
if r.returncode != 0:
    print(r.stderr[-2500:]); raise SystemExit("final video encode failed")
print(f"VIDEO OK {V} -> {video_out}")

# ---------------- audio: segment trims + acrossfades + 2-pass loudnorm ----------------
master = os.path.join(WORK, "master_audio.wav")

def build_audio_cmd(measured=None, out=None):
    cmd = [FFMPEG, "-y", "-hide_banner", "-loglevel", "info"]
    for _ in segs:
        cmd += ["-i", master]
    graph = []
    for i, ps in enumerate(segs):
        graph.append(f"[{i}:a]atrim=start={ps['src_s']:.3f}:end={ps['src_e']:.3f},asetpts=PTS-STARTPTS[a{i}]")
    # hard concat = zero overlap/echo (crossfades doubled the voice at every join)
    graph.append("".join(f"[a{i}]" for i in range(len(segs))) +
                 f"concat=n={len(segs)}:v=0:a=1[cat]")
    cur = "cat"
    ln = "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json"
    if measured:
        ln = ("loudnorm=I=-14:TP=-1.5:LRA=11"
              f":measured_I={measured['input_i']}:measured_TP={measured['input_tp']}"
              f":measured_LRA={measured['input_lra']}:measured_thresh={measured['input_thresh']}"
              ":linear=true:print_format=json")
    graph.append(f"[{cur}]{ln},aresample=48000[aout]")
    cmd += ["-filter_complex", ";".join(graph), "-map", "[aout]"]
    if out:
        cmd += ["-c:a", "aac", "-b:a", "192k", out]
    else:
        cmd += ["-f", "null", "-"]
    return cmd

# ---- pass 1: measure
r = run(build_audio_cmd(None, None))
m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", r.stderr)
if not m:
    print(r.stderr[-2000:]); raise SystemExit("loudnorm measure failed")
measured = json.loads(m.group(0))

# ---- pass 2
audio_out = os.path.join(ODIR, "final_audio.m4a")
p2 = build_audio_cmd(measured, audio_out)
r = run(p2)
if r.returncode != 0:
    print(r.stderr[-2500:]); raise SystemExit("audio pass2 failed")
print(f"AUDIO OK {V} -> {audio_out}")

# ---------------- mux ----------------
final = os.path.join(ODIR, "final.mp4")
r = run([FFMPEG, "-y", "-hide_banner", "-loglevel", "error",
         "-i", video_out, "-i", audio_out,
         "-c:v", "copy", "-c:a", "copy", "-movflags", "+faststart", final])
if r.returncode != 0:
    print(r.stderr[-1500:]); raise SystemExit("mux failed")
print(f"FINAL {V} OK -> {final}")
