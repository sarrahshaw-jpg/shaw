#!/usr/bin/env bash
# Package each claude/skills/<name>/ folder into dist/<name>.zip for upload to claude.ai (Settings → Skills).
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p dist
for d in claude/skills/*/; do
  name=$(basename "$d")
  [ -f "$d/SKILL.md" ] || { echo "skip $name: no SKILL.md"; continue; }
  rm -f "dist/$name.zip"
  (cd claude/skills && zip -qr "../../dist/$name.zip" "$name")
  echo "dist/$name.zip"
done
