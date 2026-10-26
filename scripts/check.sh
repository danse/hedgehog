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

echo
if [ "$fail" -eq 0 ]; then
  echo "All blocking checks passed."
else
  echo "Fix the FAIL entries above."
fi
exit "$fail"
