# Edit Pipeline — LinkedIn + Instagram Reels

Pro-grade, fully automated short-form edit pipeline. Built for: **remove background
noise, HD/crisp picture, face light, remove gaps & fillers, captions, transitions,
intentional zoom-ins, hidden keyword text behind the head, emoji popups, HD voice —
without touching the background or boxing the frame.**

The original voice is **never** replaced — audio is only cleaned and enhanced.

## One-command run

```bash
bash edit_work/setup_env.sh                      # restore toolchain (idempotent, ~2 min after recycle)
python3 edit_work/pipeline/run_all.py SRC.mp4    # full edit
# -> edits/LinkedIn_1080p.mp4, edits/Instagram_Reel_1080x1920.mp4,
#    covers + edits/posting_kit.md
```

Resume a partial run: `python3 edit_work/pipeline/run_all.py SRC.mp4 6` (stages 6-8).

## Stages

| # | Script | What it does |
|---|--------|--------------|
| 1 | `s1_probe_audio.py` | Probe source; silence map; **HD voice chain**: highpass → adeclick → RNNoise AI denoise → mud-cut EQ → presence EQ → air → warmth → de-esser → compressor → limiter |
| 2 | `s2_transcribe.py` | whisper.cpp (small, English) word-level timestamps |
| 3 | `s3_plan.py` | The editor's brain: silence-sanitized timestamps, filler/stutter/gap cuts, keyword picks, emoji moments, zoom choreography, karaoke caption groups, src→dst time map |
| 4 | `s4_faces.py` | Face detection + tracking path (OpenCV cascades; auto-uses YuNet ONNX if present) |
| 5 | `s5_graphics.py` | Face-light (color-safe alpha glow), keyword-behind-head art with feathered head hole + soft shadow, emoji stickers w/ shadow, caption `.ass` |
| 6 | `s6_segments.py` | Per-segment renders: 2× supersampled `zoompan` push-ins, face-follow crop (9:16), tone + CAS/unsharp "crisp" pass |
| 7 | `s7_final.py` | xfade transitions (smoothleft/smoothup/circleopen on sentence cuts), overlay sequencing w/ fades, caption burn, **two-pass -14 LUFS** audio, faststart mux |
| 8 | `s8_deliverables.py` | Cover images (gradient + hook text), posting kit (captions + hashtags), files into `edits/` |

## Design decisions

- **Zooms**: `zoompan` on 2× lanczos-upscaled frames (sub-pixel smooth, no crop jitter —
  crop w/h are init-only in ffmpeg, so zoompan is the correct tool).
- **Face light**: white RGBA glow alpha-composited via `overlay`. The `blend=screen`
  route corrupts chroma in this ffmpeg build (plane-shifted YUV math) — verified and avoided.
- **Hidden keywords**: huge 4%-alpha outlined text placed just above the head with a
  feathered elliptical hole punched where the head is → text reads as *behind* the head.
- **Cuts**: never mid-word; breath padding kept; micro-runs absorbed; silences fused
  from both whisper timing and silencedetect (whisper stretches words across long pauses).
- **Audio**: segment trims → acrossfades matched to video transition durations →
  2-pass linear-phase loudnorm to -14 LUFS / TP -1.5 (YouTube/LinkedIn/IG target).
- **Framing**: background untouched, no added frames/borders; 9:16 re-centers on the
  tracked face; captions sit in UI-safe zones (Reels right-rail and bottom UI avoided).

## Requirements

Everything self-restores via `setup_env.sh` (ffmpeg static via imageio-ffmpeg,
whisper.cpp built from source, pip pkgs). The whisper model (`ggml-small.bin`,
~487 MB) lives in `~/cache_big/` and is re-fetched automatically if missing
(reassembled from `fmyIo/whisper-models` GitHub parts). Fonts + emoji + RNNoise
models are vendored under `edit_work/assets/`.

`samples_test_run/` contains a complete synthetic end-to-end validation run
(generated talking-head with noise, filler-pace gaps and dead air) used to QA
transitions, karaoke timing, color safety and loudness before the real footage.
