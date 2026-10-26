#!/usr/bin/env bash
# Open Emacs with the project-contained config.
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [ "$#" -eq 0 ]; then
  set -- "$root/live/00-setup.tidal"
fi

exec emacs -q --init-directory "$root/emacs" -l "$root/emacs/init.el" "$@"
