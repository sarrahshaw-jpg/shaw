#!/bin/bash
# Restores the full editing toolchain after a sandbox recycle. Idempotent.
set -e
EW="/home/user/shaw/edit_work"
TOOLS="$EW/tools"
BIN="$TOOLS/bin"
mkdir -p "$BIN"

echo "== 1. ffmpeg =="
if [ ! -x "$BIN/ffmpeg" ]; then
  pip install --break-system-packages -q imageio-ffmpeg 2>/dev/null || pip install -q imageio-ffmpeg
  FF=$(python3 -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())")
  cp "$FF" "$BIN/ffmpeg"; chmod +x "$BIN/ffmpeg"
fi
"$BIN/ffmpeg" -version | head -1

echo "== 2. python deps =="
python3 -c "import numpy, PIL" 2>/dev/null || pip install --break-system-packages -q numpy pillow
python3 -c "import cv2" 2>/dev/null || pip install --break-system-packages -q opencv-python-headless
python3 - <<'EOF'
import cv2
if not hasattr(cv2, 'CascadeClassifier'):
    import subprocess, sys
    subprocess.run([sys.executable, '-m', 'pip', 'install', '--break-system-packages', '-q', 'opencv-python-headless<5'], check=True)
EOF
python3 -c "import cv2, numpy, PIL; print('cv2', cv2.__version__)"

echo "== 3. whisper.cpp =="
WS="$TOOLS/whisper.cpp"
if [ ! -x "$WS/build/bin/whisper-cli" ]; then
  if [ ! -d "$WS" ]; then
    if [ -f "$TOOLS/whisper-src.tar.gz" ]; then tar xzf "$TOOLS/whisper-src.tar.gz" -C "$TOOLS" && mv "$TOOLS/whisper.cpp-master" "$WS"
    else curl -sL --max-time 240 -o "$TOOLS/whisper-src.tar.gz" https://codeload.github.com/ggml-org/whisper.cpp/tar.gz/refs/heads/master && tar xzf "$TOOLS/whisper-src.tar.gz" -C "$TOOLS" && mv "$TOOLS/whisper.cpp-master" "$WS"; fi
  fi
  python3 -c "import cmake" 2>/dev/null || pip install --break-system-packages -q cmake
  cmake -S "$WS" -B "$WS/build" -DCMAKE_BUILD_TYPE=Release -DWHISPER_BUILD_TESTS=OFF -DGGML_NATIVE=ON -DGGML_OPENMP=OFF > /dev/null
  cmake --build "$WS/build" --target main whisper-cli -j2 > /dev/null 2>&1
fi
"$WS/build/bin/whisper-cli" --version 2>&1 | head -1 || true

echo "== 4. whisper model (small, re-fetched; not persisted) =="
MODEL="$HOME/cache_big/ggml-small.bin"
mkdir -p "$HOME/cache_big"
if [ ! -f "$MODEL" ]; then
  curl -sL --max-time 1500 -o /tmp/wm.zip https://codeload.github.com/fmyIo/whisper-models/zip/refs/heads/main
  unzip -q -o /tmp/wm.zip -d /tmp/wmx
  cat /tmp/wmx/*/partaa /tmp/wmx/*/partab /tmp/wmx/*/partac /tmp/wmx/*/partad /tmp/wmx/*/partae /tmp/wmx/*/partaf > "$MODEL"
  rm -rf /tmp/wm.zip /tmp/wmx
fi
ls -la "$MODEL"

echo "== 5. rnnoise models =="
[ -d "$EW/assets/rnnoise" ] || { mkdir -p "$EW/assets" && cp -r "$HOME/cache_big/rnnoise-models-master" "$EW/assets/rnnoise" 2>/dev/null || true; }
if [ ! -d "$EW/assets/rnnoise" ]; then
  curl -sL --max-time 240 -o /tmp/rnn.tar.gz https://codeload.github.com/GregorR/rnnoise-models/tar.gz/refs/heads/master
  mkdir -p "$EW/assets" && tar xzf /tmp/rnn.tar.gz -C /tmp && cp -r /tmp/rnnoise-models-master "$EW/assets/rnnoise"
fi
ls "$EW/assets/rnnoise" | head -3
echo "ENV READY"
