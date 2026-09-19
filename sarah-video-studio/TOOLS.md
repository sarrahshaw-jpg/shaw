# Agent Tools

The AI Agent has access to the following modular tools:

## 1. `TRANSCRIBE`
- **Engine:** Whisper (or fallback mock).
- **Purpose:** Generates a timestamped array of spoken words.

## 2. `ANALYZE_VIDEO`
- **Purpose:** Scans the visual feed to track face position (for smart cropping) and lighting quality.

## 3. `REMOVE_FILLERS`
- **Purpose:** Searches the transcript for "um, uh, like" and cross-references with the EDL to generate safe cuts without clipping audio.

## 4. `AUDIO_CLEANUP`
- **Purpose:** Applies a vocal EQ and noise reduction chain via FFmpeg.

## 5. `BROLL_SEARCH`
- **Purpose:** Takes a semantic query from the transcript (e.g., "office politics") and retrieves relevant, premium visuals from a licensed or generated asset library.

## 6. `CAPTION_GENERATOR`
- **Purpose:** Takes raw text and formats it into visually appealing phrased blocks with strategic keyword emphasis.

## 7. `VIDEO_RENDERER`
- **Purpose:** Ingests the final EDL and executes the actual pixel rendering (via FFmpeg or Remotion).
