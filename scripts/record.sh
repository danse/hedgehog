#!/usr/bin/env bash
# Record the default PipeWire/Pulse monitor to recordings/ as 24-bit WAV.
# Usage: scripts/record.sh [name]   (Ctrl-C to stop)
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
mkdir -p "$root/recordings"
name="${1:-take-$(date +%Y%m%d-%H%M%S)}"
out="$root/recordings/$name.wav"

sink=""
if command -v wpctl >/dev/null 2>&1; then
  sink=$(wpctl inspect @DEFAULT_AUDIO_SINK@ 2>/dev/null \
    | sed -n 's/.*node.name = "\(.*\)"/\1/p' | head -1)
fi

if [ -z "$sink" ]; then
  echo "Could not determine default sink; recording 'default' monitor." >&2
  src="default"
else
  src="${sink}.monitor"
fi

echo "Recording '$src' -> $out"
echo "Ctrl-C to stop."
exec ffmpeg -hide_banner -loglevel warning \
  -f pulse -i "$src" \
  -ac 2 -ar 48000 -c:a pcm_s24le \
  "$out"
