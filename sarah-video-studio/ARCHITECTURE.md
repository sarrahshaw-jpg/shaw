# Architecture

The Sarah Video Studio AI uses a modular architecture combining a modern frontend with a robust backend orchestration system.

## Components

### 1. Frontend (Next.js / React)
A polished UI to upload videos, preview edits, chat with the AI, and manage your library.
Located in `src/app` and `src/ui`.

### 2. AI Agent Router (`src/agent`)
The brain of the system. It receives natural language requests ("Make this more cinematic") and maps them to video processing tasks. It calls specific tools based on the video context.

### 3. Video Pipeline (`src/video-engine`)
Wraps FFmpeg and other video manipulation utilities. Handles cutting, cropping, dynamic zooms, and exporting to different aspect ratios.

### 4. Audio Engine (`src/audio-engine`)
Analyzes audio for silence, extracts transcripts (via Whisper or mock), and applies normalization and noise reduction.

### 5. Media Library (`src/database`)
A local JSON-based storage (for the prototype) that keeps track of videos, editing profiles, and versions.

## Data Flow
Upload Video -> Save to Local Storage -> Extract Audio -> Transcribe -> AI Tool Router (Decides Edits) -> Build Edit Decision List (EDL) -> Render Preview -> User Approval -> Final Render (FFmpeg).
