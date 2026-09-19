# Video Pipeline

This pipeline ensures maximum perceived production quality (cinematic, clean, premium) without relying on excessive, cheap effects.

## Stages

1. **Extraction (FFmpeg):**
   - Separate audio and video streams.
   
2. **Analysis:**
   - Detect silence/clipping.
   - Detect faces for smart cropping (maintains headroom).

3. **Transformation (EDL based):**
   - **Smart Cropping:** Master is 9:16 vertical (1080x1920).
   - **Dynamic Zoom Engine:** Subtle punch-ins (1.10x, 1.15x) using smooth interpolation.
   - **Color/Lighting:** Applied via LUTs or FFmpeg eq filters to correct flat lighting and ensure clean skin tones.

4. **Layering:**
   - **V1 (Video 1):** Primary Talking Head (with cuts/zooms).
   - **V2 (Video 2):** B-Roll / Visual Inserts.
   - **V3 (Graphics):** Text/Captions, minimal animations.

5. **Audio Mixing:**
   - Voice is compressed and EQ'd for studio presence.
   - Music is ducked automatically under the voice track.

6. **Render Targets:**
   - High Bitrate H.264 / AAC for social media platforms.
