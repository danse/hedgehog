#!/usr/bin/env bash
# Swap Hydra sketch to match movement cues
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root/visuals/hydra/sketches"

n="${1:-}"
if [[ ! "$n" =~ ^[1-5]$ ]]; then
  echo "Usage: $0 <1-5>" >&2
  echo "  1=emergence 2=pulse 3=bloom 4=drift 5=dissolve" >&2
  exit 1
fi

# Create/update symlink current.js pointing to sketch
ln -sf "0${n}.js" current.js
echo "[vis-hydra-swap] Swapped to sketch 0${n} (current.js -> 0${n}.js)"
echo "  In browser: press $n or refresh page."
