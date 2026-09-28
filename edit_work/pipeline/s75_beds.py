"""Stage 7.5: light background music (voice-ducked) + sweet transition sounds,
mixed under the mastered voice. Synthesizes everything with numpy - no sources needed."""
import os, sys, json, wave, subprocess
import numpy as np
from common import *

V = sys.argv[1]
SR = 48000
plan = jload(os.path.join(WORK, "plan.json"))
DUR = plan["new_dur"] + 0.4
ODIR = os.path.join(WORK, "out", V)
voice_a = os.path.join(ODIR, "final_audio.m4a")     # mastered voice
final_v = os.path.join(ODIR, "video_noaudio.mp4")

rng = np.random.default_rng(7)
def env_ar(n, a, r, sr=SR):
    e = np.ones(n)
    na, nr = int(a * sr), int(r * sr)
    if na > 0: e[:na] = np.linspace(0, 1, na) ** 1.5
    if nr > 0: e[-nr:] *= np.linspace(1, 0, nr) ** 1.3
    return e

def lowpass(x, cutoff, sr=SR):
    """FFT brickwall with soft knee - good enough for pads."""
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / sr)
    g = 1 / (1 + (f / cutoff) ** 4)
    return np.fft.irfft(X * g, len(x))

def note(freq, dur, detune=0.0012, harm=(1.0, 0.35, 0.12)):
    n = int(dur * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for h, amp in enumerate(harm, start=1):
        for dt in (-detune, detune):
            out += amp * np.sin(2 * np.pi * freq * h * (1 + dt) * t)
    return out

# ---- music bed: F maj7 -> C maj7 -> D min7 -> Bb maj7 (warm, slow) ----
def F(n): return 440.0 * (2 ** ((n - 9) / 12))     # midi->freq, midi 9 = F5 ref? use A4=440 midi69
def midi(n): return 440.0 * 2 ** ((n - 69) / 12)

CHORDS = [
    [53, 57, 60, 64],   # F3 A3 C4 E4  (Fmaj7)
    [48, 52, 55, 59],   # C3 E3 G3 B3  (Cmaj7)
    [50, 53, 57, 60],   # D3 F3 A3 C4  (Dmin7)
    [46, 50, 53, 57],   # Bb2 D3 F3 A3 (Bbmaj7)
]
CH_DUR = 7.6
music = np.zeros(int(DUR * SR) + SR)
tpos = 0.0
ci = 0
while tpos < DUR:
    ch = CHORDS[ci % len(CHORDS)]
    n = int(CH_DUR * SR)
    pad = np.zeros(n)
    for m in ch:
        pad += note(midi(m), CH_DUR) * 0.22
        pad += note(midi(m + 12), CH_DUR, harm=(0.5, 0.1, 0.0)) * 0.08
    pad *= env_ar(n, 1.6, 2.2)
    bass = note(midi(ch[0] - 12), CH_DUR, harm=(1.0, 0.05, 0.0)) * 0.30 * env_ar(n, 0.8, 1.5)
    segm = pad + bass
    e = int(min(tpos * SR, len(music) - len(segm)))
    if e < 0: break
    music[e:e + len(segm)] += segm
    tpos += CH_DUR * 0.98          # slight overlap for legato
    ci += 1
music = music[:int(DUR * SR)]
music = lowpass(music, 2400)
# gentle tape noise
music += lowpass(rng.normal(0, 1, len(music)), 3800) * 0.006
music *= env_ar(len(music), 2.0, 3.0)
music /= max(1e-9, np.abs(music).max()) / 0.16          # base level

# ---- duck under voice ----
vr = subprocess.run([FFMPEG, "-loglevel", "error", "-i", voice_a, "-f", "f32le",
                     "-acodec", "pcm_f32le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True)
voice = np.frombuffer(vr.stdout, np.float32).copy()
n = min(len(voice), len(music))
env = np.abs(voice[:n])
k = np.ones(12000) / 12000
env = np.convolve(env, k, mode="same")
env = np.clip(env / (np.percentile(env, 92) + 1e-9), 0, 1)
duck = 1.0 - 0.62 * env
music[:n] *= duck[:n]

# ---- cute transition sfx at every cut + tiny sparkle on tile pops ----
def pop():
    n = int(0.09 * SR); t = np.arange(n) / SR
    f = 640 * np.exp(-t * 14) + 160
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 30) * 0.9

def ding():
    n = int(0.5 * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 1318.5 * t) + 0.4 * np.sin(2 * np.pi * 1975 * t)) * np.exp(-t * 9) * 0.5

def whoosh():
    n = int(0.22 * SR); t = np.arange(n) / SR
    x = rng.normal(0, 1, n)
    x = lowpass(x, 1600)
    return x * np.sin(np.pi * t / 0.22) ** 2 * 2.2

sfx = np.zeros(int(DUR * SR) + SR)
cut_times = []
acc = 0.0
for ps in plan["segments"][:-1]:
    acc += ps["dur"]
    cut_times.append(acc)
    acc -= ps["tr_after"]
# only section-level transitions get a sound (max 4, very quiet)
big_cuts = []
acc = 0.0
for i, ps in enumerate(plan["segments"][:-1]):
    acc += ps["dur"]
    if ps["tr_after"] >= 0.26 and len(big_cuts) < 4:
        big_cuts.append(acc)
    acc -= ps["tr_after"]
for ct in big_cuts:
    s = whoosh()
    e = int(ct * SR)
    if e + len(s) < len(sfx):
        sfx[e:e + len(s)] += s * 0.085
for tt in jload(os.path.join(WORK, "tiles_v3.json"))["times"]:
    s = ding(); e = int(tt * SR)
    if e + len(s) < len(sfx):
        sfx[e:e + len(s)] += s * 0.055
sfx = sfx[:int(DUR * SR)]
sfx /= max(1e-9, np.abs(sfx).max()) / 0.20

# ---- write stems + mix ----
def wsave(p, x):
    x16 = (np.clip(x, -1, 1) * 32767).astype(np.int16)
    with wave.open(p, "w") as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR)
        wf.writeframes(x16.tobytes())

music_p = os.path.join(ODIR, "bed_music.wav"); sfx_p = os.path.join(ODIR, "bed_sfx.wav")
wsave(music_p, music); wsave(sfx_p, sfx)

mixed = os.path.join(ODIR, "final_audio_fx.m4a")
cmd = [FFMPEG, "-y", "-loglevel", "error",
       "-i", voice_a, "-i", music_p, "-i", sfx_p,
       "-filter_complex",
       "[0:a]aformat=channel_layouts=stereo[v];"
       "[1:a]aformat=channel_layouts=stereo,volume=0.32[m];"
       "[2:a]aformat=channel_layouts=stereo,volume=0.9[s];"
       "[v][m]amix=inputs=2:duration=first:normalize=0[vm];"
       "[vm][s]amix=inputs=2:duration=first:normalize=0[mx];"
       "[mx]alimiter=limit=0.95,aresample=48000[out]",
       "-map", "[out]", "-c:a", "aac", "-b:a", "192k", mixed]
r = run(cmd)
if r.returncode != 0:
    print(r.stderr[-1500:]); raise SystemExit("bed mix failed")

final = os.path.join(ODIR, "final.mp4")
r = run([FFMPEG, "-y", "-loglevel", "error", "-i", final_v, "-i", mixed,
         "-c:v", "copy", "-c:a", "copy", "-movflags", "+faststart", final])
if r.returncode != 0:
    print(r.stderr[-1500:]); raise SystemExit("remux failed")
print(f"BEDS OK: music duck-ducked, {len(cut_times)} transition sfx, remuxed -> {final}")
