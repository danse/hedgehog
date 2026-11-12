#!/usr/bin/env bash
# Open Emacs with the project-contained config. With no argument, start in the
# tracks folder so the set is one key away.
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [ "$#" -eq 0 ]; then
  set -- "$root/tracks"
fi

exec emacs -q --init-directory "$root/emacs" -l "$root/emacs/init.el" "$@"
