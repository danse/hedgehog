# Scripts

Helper scripts for running the set, switching audio, recording, and driving
visuals. Paths are relative to the repo root.

## Start / stop

| Script | Purpose |
|---|---|
| `up.sh` | Start SuperDirt (via `pw-jack sclang`) and open Emacs on the project. `--no-emacs` starts only SuperCollider. |
| `down.sh` | Stop SuperDirt and project `scsynth`. |
| `edit.sh` | Open the project-contained Emacs. |

## Audio

| Script | Purpose |
|---|---|
| `audio-usb.sh` | Route SuperCollider output to the USB audio device. |
| `audio-bt.sh` | Route SuperCollider output to Bluetooth headphones. |
| `record.sh [name]` | Record the default monitor to 24-bit WAV in `recordings/`. |

## Visuals

| Script | Purpose |
|---|---|
| `vis-audio-route.sh {start\|status\|stop}` | Create/link `Hydra-Virtual-Mic`, set it as default source, restore on stop. |
| `vis-hydra-up.sh` | Start routing, serve `visuals/hydra` on `localhost:8000`, open the browser. |
| `vis-hydra-swap.sh <n>` | Set the cue sketch (1-9): writes `current.txt` for reloads and prints the hotkey for a live swap. |

See [visuals/README.md](../visuals/README.md) and
[visuals/hydra/README.md](../visuals/hydra/README.md).

## Checks

| Script | Purpose |
|---|---|
| `check.sh` | Environment sanity check: binaries, audio, Tidal, samples, disk, reverb limits, and a silent typecheck of every track. |
| `check-tidal.sh [file ...]` | Typecheck tracks without sound: derives a silent boot from `boot/BootTidal.hs` and runs each file in a fresh GHCi. Defaults to every `*/*.tidal` track. |
| `check-tidal.py` | Convert `.tidal` blocks to GHCi `:{ :}` commands for syntax checks (output can be piped into ghci). |
