#!/usr/bin/env bash
# Hedgehog environment sanity check. Safe to run any time.
set -u
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"

fail=0
ok()   { printf '  \033[32mok\033[0m    %s\n' "$*"; }
bad()  { printf '  \033[31mFAIL\033[0m  %s\n' "$*"; fail=1; }
warn() { printf '  \033[33mwarn\033[0m  %s\n' "$*"; }

echo "Hedgehog check — $root"

echo "[binaries]"
for c in sclang scsynth ghci emacs ffmpeg; do
  if command -v "$c" >/dev/null 2>&1; then ok "$c -> $(command -v "$c")"; else bad "$c missing"; fi
done

echo "[emacs]"
if command -v emacs >/dev/null 2>&1; then
  sender_log=$(mktemp)
  if emacs --batch -q --init-directory "$root/emacs" \
       -l "$root/emacs/init.el" -l "$root/scripts/check-sender.el" \
       >"$sender_log" 2>&1; then
    ok "sender statement grouping"
  else
    bad "sender statement grouping"
    sed 's/^/        /' "$sender_log" | tail -20
  fi
  rm -f "$sender_log"
else
  warn "emacs missing — sender checks skipped"
fi

echo "[audio]"
if command -v pw-jack >/dev/null 2>&1; then ok "pw-jack present"; else bad "pw-jack missing (apt install pipewire-jack)"; fi
if command -v pw-cli >/dev/null 2>&1 && pw-cli info 0 >/dev/null 2>&1; then
  ok "PipeWire running"
else
  bad "PipeWire not reachable"
fi
if [ -e /usr/lib/x86_64-linux-gnu/pipewire-0.3/jack/libjack.so.0 ]; then
  ok "PipeWire JACK library present"
else
  bad "PipeWire JACK library missing"
fi
if [ -f /etc/ld.so.conf.d/pipewire-jack-x86_64-linux-gnu.conf ]; then
  ok "system-wide PipeWire JACK enabled"
else
  ok "per-app pw-jack (scripts/up.sh uses it)"
fi

echo "[superdirt]"
sd="$HOME/.local/share/SuperCollider/downloaded-quarks/SuperDirt"
ds="$HOME/.local/share/SuperCollider/downloaded-quarks/Dirt-Samples"
[ -d "$sd" ] && ok "SuperDirt quark" || bad "SuperDirt quark missing"
if [ -d "$ds" ]; then
  n=$(find "$ds" -maxdepth 1 -mindepth 1 -type d | wc -l)
  ok "Dirt-Samples ($n folders)"
else
  bad "Dirt-Samples missing"
fi

echo "[tidal]"
tidal_out=$(cd "$root" && printf ':m + Sound.Tidal.Context\n:q\n' | ghci -v0 2>&1)
if printf '%s' "$tidal_out" | grep -qiE 'could not load module|failed|error:'; then
  bad "ghci cannot load Sound.Tidal.Context (cabal install --lib tidal)"
else
  ok "ghci can load Sound.Tidal.Context"
fi

echo "[tracks]"
if command -v ghci >/dev/null 2>&1; then
  if track_out=$(scripts/check-tidal.sh 2>&1); then
    n=$(find "$root" -mindepth 2 -maxdepth 2 -name '*.tidal' | wc -l)
    ok "all $n track files typecheck (silent boot)"
  else
    bad "track typecheck"
    printf '%s\n' "$track_out" | sed 's/^/        /'
  fi
else
  warn "ghci missing — track typecheck skipped"
fi

echo "[disk]"
avail=$(df --output=avail -BG / | tail -1 | tr -dc '0-9')
if [ "${avail:-0}" -ge 10 ]; then
  ok "${avail}G free"
elif [ "${avail:-0}" -ge 5 ]; then
  warn "${avail}G free — enough for a short take, not a long session"
else
  bad "${avail}G free — clean caches before recording"
fi

echo "[runtime]"
if pgrep -u "$USER" -f 'sclang.*BootSuperDirt.scd' >/dev/null 2>&1; then
  ok "SuperDirt running"
else
  warn "SuperDirt not running (scripts/up.sh)"
fi
if ss -lun 2>/dev/null | grep -q ':57120'; then
  ok "UDP 57120 open (SuperDirt listening)"
else
  warn "UDP 57120 closed"
fi

echo "[set]"
# SuperDirt's dirt_reverb maps size through linexp(0, 1, 0.01, 0.98); above
# ~0.9 the loop gain passes unity and the orbit rings forever, even after hush.
bad_size=""
while IFS= read -r -d '' f; do
  for n in $(grep -oE '\bsize[[:space:]]+[0-9]*\.?[0-9]+' "$f" | awk '{print $2}'); do
    if awk -v n="$n" 'BEGIN { exit !(n + 0 > 0.9) }'; then
      bad_size="$bad_size ${f#"$root"/}:$n"
    fi
  done
done < <(find "$root" -mindepth 2 -maxdepth 2 -name '*.tidal' -print0 2>/dev/null)
if [ -n "$bad_size" ]; then
  bad "reverb size > 0.9 self-oscillates:$bad_size"
else
  ok "reverb size within 0..0.9"
fi

echo "[realtime]"
pid=$(pgrep -x scsynth | head -1)
if [ -n "$pid" ]; then
  pol=$(chrt -p "$pid" 2>/dev/null | sed -n 's/.*scheduling policy: //p')
  prio=$(chrt -p "$pid" 2>/dev/null | sed -n 's/.*scheduling priority: //p')
  case "$pol" in
    SCHED_FIFO|SCHED_RR) ok "scsynth $pol priority $prio" ;;
    *) warn "scsynth ${pol:-unknown} — no RT (log out/in or reboot after limits change)" ;;
  esac
  if grep -qiE 'real.?time|scheduling priority' logs/superdirt.log 2>/dev/null; then
    warn "RT warning in logs/superdirt.log"
  fi
else
  warn "scsynth not running"
fi

echo
if [ "$fail" -eq 0 ]; then
  echo "All blocking checks passed."
else
  echo "Fix the FAIL entries above."
fi
exit "$fail"
