#!/usr/bin/env bash
# Print the live sender's statement groups with source line numbers.
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec emacs --batch --no-site-file -q --init-directory "$root/emacs" \
  -l "$root/emacs/init.el" \
  -l "$root/scripts/tidal-groups.el" -- "$@"
