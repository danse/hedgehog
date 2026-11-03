#!/usr/bin/env bash
# Switch SuperCollider output to Bluetooth headphones (Vultech octopus)
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "[audio-bt] Switching SuperCollider to Bluetooth..."

if ! pgrep -x scsynth >/dev/null 2>&1; then
  echo "  Warning: scsynth is not running. Routing will be applied when it starts." >&2
fi

# Set Bluetooth as default sink
bt_id=""
if command -v wpctl >/dev/null 2>&1; then
  bt_id=$(wpctl status 2>/dev/null | awk '/Vultech octopus/ && /[0-9]+\./ {match($0,/[0-9]+\./); id=substr($0,RSTART,RLENGTH-1); print id; exit}')
  if [ -n "$bt_id" ]; then
    echo "  Setting default sink to $bt_id (Vultech octopus)"
    wpctl set-default "$bt_id" >/dev/null || true
  else
    echo "  Could not find Vultech octopus in wpctl status" >&2
  fi
fi

# Find Bluetooth playback ports (prefer the 133 node if present)
bt_l=""
bt_r=""
if command -v pw-jack >/dev/null 2>&1; then
  bt_l=$(pw-jack jack_lsp 2>/dev/null | grep -E 'Vultech.*133.*playback_FL|octopus-133.*playback_FL' | head -1)
  bt_r=$(pw-jack jack_lsp 2>/dev/null | grep -E 'Vultech.*133.*playback_FR|octopus-133.*playback_FR' | head -1)
  if [ -z "$bt_l" ] || [ -z "$bt_r" ]; then
    bt_l=$(pw-jack jack_lsp 2>/dev/null | grep -E 'Vultech.*playback_FL' | tail -1)
    bt_r=$(pw-jack jack_lsp 2>/dev/null | grep -E 'Vultech.*playback_FR' | tail -1)
  fi
fi

if [ -z "${bt_l:-}" ] || [ -z "${bt_r:-}" ]; then
  echo "  Could not find Bluetooth playback ports. Is it connected and paired?" >&2
  exit 1
fi

echo "  Ports: $bt_l / $bt_r"

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
  
  # Connect to Bluetooth
  if pw-jack jack_connect SuperCollider:out_1 "$bt_l" >/dev/null 2>&1; then
    echo "  Connected SuperCollider:out_1 -> $bt_l"
  else
    echo "  Failed to connect out_1" >&2
  fi
  if pw-jack jack_connect SuperCollider:out_2 "$bt_r" >/dev/null 2>&1; then
    echo "  Connected SuperCollider:out_2 -> $bt_r"
  else
    echo "  Failed to connect out_2" >&2
  fi
fi

echo "[audio-bt] Done. Audio should now come through your Bluetooth headphones."
