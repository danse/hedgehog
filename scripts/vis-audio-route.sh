#!/usr/bin/env bash
# Hedgehog Hydra audio routing via PipeWire loopback.
# Creates a virtual microphone fed by the default sink's monitor, links it, and
# (by default) makes it the default source so browser getUserMedia picks it up.
if [ "${1:-}" = "--help" ] || [ "${1:-}" = "-h" ]; then
  cat <<EOF
Usage: $0 {start|status|stop}
  start   create/link Hydra-Virtual-Mic from the default sink's monitor and make
          it the default source; saves the previous source and is idempotent
  status  print whether it is running, the default sink/source and monitor links
  stop    unlink and remove the virtual mic, restore the previous default source
EOF
  exit 0
fi
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"

VIRT_SINK_NAME="hydra-virt-sink"
VIRT_SRC_NAME="hydra-virt-src"
STATE_DIR="${XDG_RUNTIME_DIR:-/tmp}/hedgehog"
PREV_SOURCE_FILE="$STATE_DIR/hydra-prev-source"

action="${1:-start}"

is_running() {
  local out
  out="$(pw-cli ls Node 2>/dev/null || true)"
  grep -q "node.name = \"$VIRT_SRC_NAME\"" <<< "$out"
}

default_sink_name() {
  wpctl inspect @DEFAULT_AUDIO_SINK@ 2>/dev/null \
    | sed -n 's/.*node.name = "\(.*\)"/\1/p' | head -1
}

default_source_name() {
  wpctl inspect @DEFAULT_AUDIO_SOURCE@ 2>/dev/null \
    | sed -n 's/.*node.name = "\(.*\)"/\1/p' | head -1
}

node_id() {
  pw-cli ls Node 2>/dev/null | awk -v n="$1" '
    /^[[:space:]]*id [0-9]+,/ { id = $2; gsub(/,/, "", id) }
    $0 ~ ("node.name = \"" n "\"") { print id; exit }
  '
}

is_audio_source() {
  wpctl inspect "$1" 2>/dev/null | grep -q 'media.class = "Audio/Source"'
}

start_loopback() {
  if is_running; then
    echo "[vis-audio-route] Loopback already running"
    return 0
  fi
  if ! command -v pw-loopback >/dev/null 2>&1; then
    echo "[vis-audio-route] pw-loopback not found (install pipewire)" >&2
    return 1
  fi
  echo "[vis-audio-route] Creating $VIRT_SRC_NAME"
  pw-loopback \
    --capture-props="media.class=Audio/Sink node.name=$VIRT_SINK_NAME device.description=Hydra-Virtual-Sink" \
    --playback-props="media.class=Audio/Source node.name=$VIRT_SRC_NAME device.description=Hydra-Virtual-Mic" \
    --latency=64/48000 \
    >/dev/null 2>&1 &
  for _ in $(seq 1 20); do
    is_running && return 0
    sleep 0.1
  done
  echo "[vis-audio-route] Loopback did not appear" >&2
  return 1
}

# Feed the default sink's monitor into the loopback's sink side.
# The loopback then exposes that signal on its source side (the virtual mic).
link_monitor() {
  local sink ch
  sink="$(default_sink_name)"
  if [ -z "$sink" ]; then
    echo "[vis-audio-route] No default sink; cannot link monitor" >&2
    return 1
  fi
  for ch in FL FR; do
    if pw-link -l 2>/dev/null | grep -F -A3 "$sink:monitor_$ch" \
         | grep -Fq "$VIRT_SINK_NAME:playback_$ch"; then
      continue
    fi
    # The monitor is a port on the sink node: <sink>:monitor_FL, not a node
    # named <sink>.monitor (that is the PulseAudio-style name).
    pw-link "$sink:monitor_$ch" "$VIRT_SINK_NAME:playback_$ch" 2>/dev/null || true
    if pw-link -l 2>/dev/null | grep -F -A3 "$sink:monitor_$ch" \
         | grep -Fq "$VIRT_SINK_NAME:playback_$ch"; then
      echo "[vis-audio-route] Linked $sink:monitor_$ch -> $VIRT_SINK_NAME:playback_$ch"
    else
      echo "[vis-audio-route] Could not link $sink:monitor_$ch" >&2
    fi
  done
}

# Make the virtual mic the default source so browsers use it unless they have a
# per-site device preference saved. The previous default is restored on stop.
set_default_source() {
  local id prev_name prev_id
  id="$(node_id "$VIRT_SRC_NAME")"
  if [ -z "$id" ]; then
    echo "[vis-audio-route] $VIRT_SRC_NAME not found" >&2
    return 1
  fi
  mkdir -p "$STATE_DIR"
  if [ ! -f "$PREV_SOURCE_FILE" ]; then
    prev_name="$(default_source_name)"
    prev_id="$(node_id "$prev_name" || true)"
    if [ -n "$prev_id" ] && [ "$prev_id" != "$id" ] && is_audio_source "$prev_id"; then
      echo "$prev_id" > "$PREV_SOURCE_FILE"
    fi
  fi
  wpctl set-default "$id"
  echo "[vis-audio-route] Default source -> $VIRT_SRC_NAME ($id)"
}

restore_default_source() {
  local prev
  [ -f "$PREV_SOURCE_FILE" ] || return 0
  prev="$(cat "$PREV_SOURCE_FILE")"
  if [ -n "$prev" ] && is_audio_source "$prev"; then
    wpctl set-default "$prev" >/dev/null 2>&1 || true
    echo "[vis-audio-route] Restored default source ($prev)"
  fi
  rm -f "$PREV_SOURCE_FILE"
}

show_status() {
  if is_running; then
    echo "[vis-audio-route] RUNNING ($VIRT_SRC_NAME)"
  else
    echo "[vis-audio-route] STOPPED"
  fi
  echo "  default sink:   $(default_sink_name)"
  echo "  default source: $(default_source_name)"
  if is_running; then
    echo "  monitor links:"
    pw-link -l 2>/dev/null \
      | awk '/:playback_(FL|FR)$/ { target = $1 } /^[[:space:]]*\|<-/ { print "    " $2 " -> " target }' \
      | grep -F "$VIRT_SINK_NAME" || echo "    (none)"
  fi
}

case "$action" in
  start)
    # Starting pw-loopback makes WirePlumber reapply a saved sink volume,
    # which can drop the headset to near-silence. Preserve it explicitly.
    sink_id=$(wpctl inspect @DEFAULT_AUDIO_SINK@ 2>/dev/null \
      | sed -n 's/^id \([0-9]*\),.*/\1/p' | head -1)
    sink_vol=""
    sink_mute=0
    if [ -n "$sink_id" ]; then
      sink_vol=$(wpctl get-volume "$sink_id" 2>/dev/null | awk '{print $2}')
      wpctl get-volume "$sink_id" 2>/dev/null | grep -q '\[MUTED\]' && sink_mute=1 || true
    fi
    start_loopback
    link_monitor
    set_default_source
    if [ -n "$sink_id" ] && [ -n "$sink_vol" ]; then
      wpctl set-mute "$sink_id" "$sink_mute" >/dev/null
      wpctl set-volume "$sink_id" "$sink_vol" >/dev/null
    fi
    ;;
  stop)
    echo "[vis-audio-route] Stopping..."
    pkill -f "node.name=$VIRT_SRC_NAME" >/dev/null 2>&1 || true
    pkill -f "node.name=$VIRT_SINK_NAME" >/dev/null 2>&1 || true
    sleep 0.3
    restore_default_source
    echo "[vis-audio-route] Stopped."
    ;;
  status)
    show_status
    ;;
  *)
    echo "Usage: $0 {start|stop|status}" >&2
    exit 1
    ;;
esac
