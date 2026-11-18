#!/usr/bin/env bash
# Switch SuperCollider output to Bluetooth headphones (Vultech octopus)
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "[audio-bt] Switching SuperCollider to Bluetooth..."

if ! pgrep -x scsynth >/dev/null 2>&1; then
  echo "  Warning: scsynth is not running. Routing will be applied when it starts." >&2
fi

# The routable Bluetooth sink is a `bluez_output` Audio/Sink node, usually
# listed under Filters. The plain `Vultech octopus` sink is its internal driver
# and cannot be set as default, so keep them separate.
bt_id=""
bt_ids=()
if command -v wpctl >/dev/null 2>&1; then
  status=$(wpctl status 2>/dev/null)
  bt_id=$(printf '%s\n' "$status" | awk '
    /bluez_output\./ && /Audio\/Sink\]/ && /[0-9]+\./ {
      match($0, /[0-9]+\./); print substr($0, RSTART, RLENGTH - 1); exit
    }')
  while IFS= read -r id; do
    [ -n "$id" ] && bt_ids+=("$id")
  done < <(printf '%s\n' "$status" | awk '
    /bluez_output\./ && /Audio\/Sink\]/ && /[0-9]+\./ {
      match($0, /[0-9]+\./); print substr($0, RSTART, RLENGTH - 1)
    }
    /Sinks:/ {in_sinks = 1; next}
    /Sources:/ {in_sinks = 0}
    in_sinks && /Vultech octopus/ && /[0-9]+\./ {
      match($0, /[0-9]+\./); print substr($0, RSTART, RLENGTH - 1)
    }' | awk '!seen[$0]++')
fi

if [ -z "$bt_id" ]; then
  echo "  Could not find a routable Vultech octopus sink in wpctl status" >&2
  exit 1
fi

echo "  Bluetooth sinks: ${bt_ids[*]} (default: $bt_id)"
wpctl set-default "$bt_id" >/dev/null
for id in "${bt_ids[@]}"; do
  wpctl set-mute "$id" 0 >/dev/null
  wpctl set-volume "$id" 0.7 >/dev/null
done

# Prefer the JACK ports belonging to the chosen sink.
bt_l=""
bt_r=""
if command -v pw-jack >/dev/null 2>&1; then
  bt_l=$(pw-jack jack_lsp 2>/dev/null | grep -E "Vultech octopus-${bt_id}:playback_FL" | head -1 || true)
  bt_r=$(pw-jack jack_lsp 2>/dev/null | grep -E "Vultech octopus-${bt_id}:playback_FR" | head -1 || true)
  if [ -z "$bt_l" ] || [ -z "$bt_r" ]; then
    bt_l=$(pw-jack jack_lsp 2>/dev/null | grep -E 'Vultech.*playback_FL' | tail -1 || true)
    bt_r=$(pw-jack jack_lsp 2>/dev/null | grep -E 'Vultech.*playback_FR' | tail -1 || true)
  fi
fi

if [ -z "${bt_l:-}" ] || [ -z "${bt_r:-}" ]; then
  echo "  Could not find Bluetooth playback ports. Is it connected and paired?" >&2
  exit 1
fi

echo "  Ports: $bt_l / $bt_r"

# Disconnect SuperCollider from anything it is currently connected to.
if command -v pw-jack >/dev/null 2>&1 && pgrep -x scsynth >/dev/null 2>&1; then
  for side in 1 2; do
    while IFS= read -r conn; do
      [ -z "$conn" ] && continue
      pw-jack jack_disconnect "SuperCollider:out_${side}" "$conn" >/dev/null 2>&1 || true
    done < <(pw-jack jack_lsp -c 2>/dev/null | awk -v port="SuperCollider:out_${side}" '
      $0 == port {p = 1; next}
      p && /^[A-Za-z]/ {p = 0}
      p && /^[[:space:]]+.+:/ {gsub(/^[[:space:]]+/, "", $0); print}')
  done

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
