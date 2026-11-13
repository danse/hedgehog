#!/usr/bin/env bash
# Swap Hydra sketch to match movement cues
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root/visuals/hydra/sketches"

n="${1:-}"
if [[ ! "$n" =~ ^[1-9]$ ]]; then
  echo "Usage: $0 <1-9>" >&2
  echo "  1=emergence 2=pulse 3=bloom 4=drift 5=dissolve" >&2
  echo "  6=basic-shapes 7=oscillators 8=spectrum 9=pulse-basic" >&2
  exit 1
fi

# Remember the cue as the fallback for a fresh browser (no stored state).
# The open page keeps its own cue in localStorage and in ?sketch=, so the live
# swap is pressing the key there.
printf '%s\n' "$n" > current.txt
[ -L current.js ] && rm -f current.js
echo "[vis-hydra-swap] current.txt set to 0${n} (fallback for a browser with no cue)."
echo "  Live swap: press $n in the browser."
echo "  Or open:   http://localhost:${PORT:-8000}/?sketch=${n}"
