#!/usr/bin/env bash
# Start local server for Hydra and open browser
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root/visuals/hydra"

PORT="${PORT:-8000}"
URL="http://localhost:$PORT/"

echo "[vis-hydra-up] Serving $(pwd) on $URL"

# Try common servers
if command -v python3 >/dev/null 2>&1; then
  python3 -m http.server "$PORT" >/dev/null 2>&1 &
  PID=$!
elif command -v python >/dev/null 2>&1; then
  python -m SimpleHTTPServer "$PORT" >/dev/null 2>&1 &
  PID=$!
elif command -v busybox >/dev/null 2>&1; then
  busybox httpd -f -p "$PORT" >/dev/null 2>&1 &
  PID=$!
else
  echo "No http server found (python3/python/busybox)" >&2
  exit 1
fi

sleep 1

# Try to open browser
if command -v xdg-open >/dev/null 2>&1; then
  xdg-open "$URL" >/dev/null 2>&1 &
elif command -v gio >/dev/null 2>&1; then
  gio open "$URL" >/dev/null 2>&1 &
elif command -v firefox >/dev/null 2>&1; then
  firefox "$URL" >/dev/null 2>&1 &
fi

echo "[vis-hydra-up] Server PID $PID. Press Ctrl-C to stop."
trap "kill $PID 2>/dev/null || true; exit" INT TERM
wait $PID
