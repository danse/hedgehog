#!/usr/bin/env bash
# Hedgehog Hydra audio routing via PipeWire loopback
# Creates virtual mic (Hydra-Virtual-Mic) from USB monitor for browser capture
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"

MONITOR="alsa_output.usb-GeneralPlus_USB_Audio_Device-00.analog-stereo.monitor"
VIRT_SINK_NAME="hydra-virt-sink"
VIRT_SRC_NAME="hydra-virt-src"

action="${1:-start}"

is_running() {
  pw-cli ls Node 2>/dev/null | grep -q "node.name = \"$VIRT_SRC_NAME\""
}

case "$action" in
  start)
    if is_running; then
      echo "[vis-audio-route] Already running ($VIRT_SRC_NAME)"
      exit 0
    fi
    echo "[vis-audio-route] Starting loopback from $MONITOR -> $VIRT_SRC_NAME"
    if ! command -v pw-loopback >/dev/null 2>&1; then
      echo "  pw-loopback not found. Install pipewire or use pactl method." >&2
      echo "  See visuals/README.md Option B." >&2
      exit 1
    fi
    # Create virtual sink and route monitor into it, expose as source
    pw-loopback \
      --capture-props="media.class=Audio/Sink node.name=$VIRT_SINK_NAME device.description=Hydra-Virtual-Sink" \
      --playback-props="media.class=Audio/Source node.name=$VIRT_SRC_NAME device.description=Hydra-Virtual-Mic" \
      --latency=64/48000 \
      >/dev/null 2>&1 &
    sleep 1
    if is_running; then
      echo "[vis-audio-route] Running. Select 'Hydra-Virtual-Mic' in browser."
    else
      echo "[vis-audio-route] Failed to start. Check PipeWire/pw-loopback." >&2
      exit 1
    fi
    ;;
  stop)
    echo "[vis-audio-route] Stopping..."
    pkill -f "node.name=$VIRT_SRC_NAME" >/dev/null 2>&1 || true
    pkill -f "node.name=$VIRT_SINK_NAME" >/dev/null 2>&1 || true
    sleep 0.5
    echo "[vis-audio-route] Stopped."
    ;;
  status)
    if is_running; then
      echo "[vis-audio-route] RUNNING ($VIRT_SRC_NAME)"
    else
      echo "[vis-audio-route] STOPPED"
    fi
    ;;
  *)
    echo "Usage: $0 {start|stop|status}" >&2
    exit 1
    ;;
esac
