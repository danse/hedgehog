#!/usr/bin/env bash
# Switch SuperCollider output to USB Audio Device
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "[audio-usb] Switching SuperCollider to USB Audio Device..."

if ! pgrep -x scsynth >/dev/null 2>&1; then
  echo "  Warning: scsynth is not running. Routing will be applied when it starts." >&2
fi

# Set USB as default sink
usb_id=""
if command -v wpctl >/dev/null 2>&1; then
  usb_id=$(wpctl status 2>/dev/null | awk '/USB Audio Device/ && /Analog Stereo|Digital Stereo/ && /[0-9]+\./ {match($0,/[0-9]+\./); id=substr($0,RSTART,RLENGTH-1); print id; exit}')
  if [ -n "$usb_id" ]; then
    echo "  Setting default sink to $usb_id (USB Audio Device)"
    wpctl set-default "$usb_id" >/dev/null || true
  else
    echo "  Could not find USB Audio Device in wpctl status" >&2
  fi
fi

# Find USB playback ports
usb_l=""
usb_r=""
if command -v pw-jack >/dev/null 2>&1; then
  usb_l=$(pw-jack jack_lsp 2>/dev/null | grep -E 'USB Audio Device.*Digital Stereo.*playback_FL|USB Audio Device Digital Stereo.*playback_FL' | head -1)
  usb_r=$(pw-jack jack_lsp 2>/dev/null | grep -E 'USB Audio Device.*Digital Stereo.*playback_FR|USB Audio Device Digital Stereo.*playback_FR' | head -1)
  if [ -z "$usb_l" ] || [ -z "$usb_r" ]; then
    usb_l=$(pw-jack jack_lsp 2>/dev/null | grep -E 'USB Audio Device.*playback_FL' | head -1)
    usb_r=$(pw-jack jack_lsp 2>/dev/null | grep -E 'USB Audio Device.*playback_FR' | head -1)
  fi
fi

if [ -z "${usb_l:-}" ] || [ -z "${usb_r:-}" ]; then
  echo "  Could not find USB playback ports." >&2
  exit 1
fi

echo "  Ports: $usb_l / $usb_r"

# Disconnect SuperCollider from anything it's currently connected to
if command -v pw-jack >/dev/null 2>&1 && pgrep -x scsynth >/dev/null 2>&1; then
  # Disconnect out_1
  while IFS= read -r conn; do
    [ -z "$conn" ] && continue
    pw-jack jack_disconnect SuperCollider:out_1 "$conn" >/dev/null 2>&1 || true
  done < <(pw-jack jack_lsp -c 2>/dev/null | awk '/^SuperCollider:out_1[[:space:]]*$/{p=1;next} p && /^[A-Za-z]/{p=0} p && /^[[:space:]]+.+:/{gsub(/^[[:space:]]+/,"",$0); print}')
  
  # Disconnect out_2
  while IFS= read -r conn; do
    [ -z "$conn" ] && continue
    pw-jack jack_disconnect SuperCollider:out_2 "$conn" >/dev/null 2>&1 || true
  done < <(pw-jack jack_lsp -c 2>/dev/null | awk '/^SuperCollider:out_2[[:space:]]*$/{p=1;next} p && /^[A-Za-z]/{p=0} p && /^[[:space:]]+.+:/{gsub(/^[[:space:]]+/,"",$0); print}')
  
  # Connect to USB
  if pw-jack jack_connect SuperCollider:out_1 "$usb_l" >/dev/null 2>&1; then
    echo "  Connected SuperCollider:out_1 -> $usb_l"
  else
    echo "  Failed to connect out_1" >&2
  fi
  if pw-jack jack_connect SuperCollider:out_2 "$usb_r" >/dev/null 2>&1; then
    echo "  Connected SuperCollider:out_2 -> $usb_r"
  else
    echo "  Failed to connect out_2" >&2
  fi
fi

echo "[audio-usb] Done. Audio should now come through your USB soundcard."
