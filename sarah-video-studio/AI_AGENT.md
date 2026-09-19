# AI Agent Architecture

The **SarahVideoAgent** is designed as a persistent, stateful tool router that understands the semantic context of a video.

## How it works

1. **Intake & Analysis:**
   - Raw video is uploaded.
   - Extract audio using FFmpeg (`src/video-engine`).
   - Generate transcript with timestamps (`src/caption-engine`).
   - AI analyzes transcript for "hooks", "filler words", "key statements", and "pauses".

2. **Editing Decision List (EDL) Generation:**
   - Instead of immediately destructing the video, the agent creates an EDL.
   - Example EDL:
     - `Cut: 00:02:10 - 00:02:15 (Reason: filler 'um')`
     - `Zoom: 00:05:00 - 00:10:00 (Scale: 1.15, Reason: Key Concept 'Psychology')`
     - `Caption: 00:05:00 (Emphasis: 'Psychology')`

3. **Natural Language Routing:**
   - The user looks at the preview (built using Web technologies that mock the EDL).
   - User types: *"Make it more dynamic."*
   - Agent interprets prompt -> Modifies EDL (increases zoom frequency, tightening cuts) -> Refreshes Preview.

4. **Execution:**
   - Upon Approval, the Agent sends the EDL to the Render Engine (FFmpeg/Remotion) for the final high-quality output.

## Tool Orchestration
The agent currently routes commands to:
- `AudioEngine` (cleanup, EQ)
- `CaptionEngine` (transcription, alignment)
- `VideoEngine` (cropping, cutting, b-roll)
