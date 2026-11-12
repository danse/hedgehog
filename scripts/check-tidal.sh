#!/usr/bin/env bash
# Typecheck track files without making sound.
#
# Loads boot/BootTidal.hs into GHCi with its OSC target redirected to an unused
# port, so evaluating patterns cannot reach a running SuperDirt. Each file gets
# a fresh GHCi session, so a missing definition cannot be masked by a previous
# track.
#
# Usage: scripts/check-tidal.sh [track.tidal ...]
#        scripts/check-tidal.sh            # every tracks/*.tidal
set -u
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
invoke_dir="$PWD"
cd "$root" || exit 2

if [ "$#" -gt 0 ]; then
  files=()
  for f in "$@"; do
    case "$f" in
      /*) files+=("$f") ;;
      *)  files+=("$invoke_dir/$f") ;;
    esac
  done
else
  shopt -s nullglob
  files=(tracks/*.tidal)
fi
if [ "${#files[@]}" -eq 0 ]; then
  echo "check-tidal: no track files" >&2
  exit 2
fi
if ! command -v ghci >/dev/null 2>&1; then
  echo "check-tidal: ghci not found" >&2
  exit 2
fi

# Derive the silent boot from the real one instead of keeping a copy in sync by
# hand. If BootTidal.hs changes shape, the substitution below stops matching and
# this guard fails loudly.
boot_tmp=$(mktemp)
log_tmp=$(mktemp)
trap 'rm -f "$boot_tmp" "$log_tmp"' EXIT
sed \
  -e 's|^tidalInst <- mkTidal$|tidalInst <- mkTidalWith [(superdirtTarget { oPort = 57199 }, [superdirtShape])] (defaultConfig { cCtrlPort = 6019 })|' \
  -e 's|^:set prompt .*|:set prompt ""|' \
  boot/BootTidal.hs >"$boot_tmp"
if ! grep -q 'oPort = 57199' "$boot_tmp"; then
  echo "check-tidal: cannot derive a silent boot from boot/BootTidal.hs" >&2
  echo "check-tidal: expected a line 'tidalInst <- mkTidal'" >&2
  exit 2
fi

fail=0
for f in "${files[@]}"; do
  printf '%-28s ' "$f"
  if { cat "$boot_tmp"; python3 scripts/check-tidal.py "$f"; printf ':q\n'; } \
       | ghci -v0 >"$log_tmp" 2>&1; then
    if grep -qE 'error:|not in scope|parse error' "$log_tmp"; then
      echo FAIL
      grep -E -A6 'error:|not in scope|parse error' "$log_tmp" \
        | sed 's/^/    /' | head -40
      fail=1
    else
      echo ok
    fi
  else
    echo FAIL
    tail -20 "$log_tmp" | sed 's/^/    /'
    fail=1
  fi
done

exit "$fail"
