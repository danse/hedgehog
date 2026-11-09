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

# Remember the cue so a page reload starts there too.
printf '%s\n' "$n" > current.txt
[ -L current.js ] && rm -f current.js
echo "[vis-hydra-swap] Cue set to sketch 0${n} (current.txt = ${n})"
echo "  Live swap: press $n in the browser. Reload also starts at 0${n}."
