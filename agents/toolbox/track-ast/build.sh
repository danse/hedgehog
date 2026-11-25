#!/usr/bin/env bash
# Build (or reuse) the GHC AST fact helper. Prints the binary path on stdout.
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
src="$root/Facts.hs"
cache="${XDG_CACHE_HOME:-$HOME/.cache}/hedgehog"
version="$(ghc --numeric-version)"
build="$cache/track-ast-ghc$version"
bin="$build/facts"
if [ ! -x "$bin" ] || [ "$src" -nt "$bin" ]; then
  mkdir -p "$build"
  ghc -package ghc -O0 -outputdir "$build" -o "$bin" "$src" 1>&2
fi
printf '%s\n' "$bin"
