#!/usr/bin/env bash
# Start SuperDirt (headless) and open Emacs on the set.
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"
mkdir -p logs recordings

if ! command -v sclang >/dev/null 2>&1; then
  echo "sclang not found" >&2; exit 1
fi
if ! command -v pw-jack >/dev/null 2>&1; then
  echo "pw-jack not found — run: sudo apt install pipewire-jack" >&2; exit 1
fi

if pgrep -u "$USER" -f 'sclang.*BootSuperDirt.scd' >/dev/null 2>&1; then
  echo "SuperDirt already running."
else
  echo "Starting SuperCollider + SuperDirt (pw-jack)..."
  : > logs/superdirt.log
  nohup pw-jack sclang boot/BootSuperDirt.scd >> logs/superdirt.log 2>&1 &
  echo $! > logs/superdirt.pid

  ready=0
  for _ in $(seq 1 120); do
    if grep -q "SuperDirt ready" logs/superdirt.log 2>/dev/null; then ready=1; break; fi
    if ! kill -0 "$(cat logs/superdirt.pid)" 2>/dev/null; then break; fi
    sleep 0.5
  done

  if [ "$ready" -ne 1 ]; then
    echo "SuperDirt did not come up. Last log lines:" >&2
    tail -30 logs/superdirt.log >&2
    exit 1
  fi
  echo "SuperDirt ready (log: logs/superdirt.log)."
fi

if [ "${1:-}" != "--no-emacs" ]; then
  exec "$root/scripts/edit.sh"
fi

echo "Now: scripts/edit.sh"
