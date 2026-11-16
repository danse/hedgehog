# Scripts

Helper scripts for running the set, switching audio, recording, and driving
visuals. Paths are relative to the repo root.

## Start / stop

| Script | Purpose |
|---|---|
| `up.sh` | Start SuperDirt (via `pw-jack sclang`) and open Emacs on the project. `--no-emacs` starts only SuperCollider. |
| `down.sh` | Stop SuperDirt and project `scsynth`. |
| `edit.sh` | Open the project-contained Emacs in `tracks/`. |

## Audio

| Script | Purpose |
|---|---|
| `audio-usb.sh` | Route SuperCollider output to the USB audio device. |
| `audio-bt.sh` | Route SuperCollider output to Bluetooth headphones. |
| `record.sh [name]` | Record the default monitor to 24-bit WAV in `recordings/`. |

## JACK clients and the default sink

`up.sh` starts scsynth under `pw-jack`, so it is a **JACK client**, not an
application stream. Application streams follow the default sink when it changes
(a headset connects, `wpctl set-default` runs). JACK clients do not: their
`out_1`/`out_2` ports stay wherever they were linked, or nowhere.

That produces two confusing symptoms:

- **System sounds play, SuperDirt is silent.** Check `pw-link -l`:
  `SuperCollider:out_1/2` should each have an arrow to some sink. If they have
  none, link them by hand — a port can feed several sinks, so this does not
  steal the audio from anywhere else:

  ```
  pw-link SuperCollider:out_1 bluez_output.<addr>.1:playback_FL
  pw-link SuperCollider:out_2 bluez_output.<addr>.1:playback_FR
  ```

  Find `<addr>` with `wpctl status` or `pw-link -o`; for a USB device the sink
  is `alsa_output.*` with the same `playback_FL/FR` ports.

- **Audio is fine but Hydra is dark.** Hydra listens to the *default sink's
  monitor*, not to scsynth. If the default sink changes after
  `vis-audio-route.sh start` ran, the monitor links still point at the old sink
  and the virtual mic goes quiet. Re-run `vis-audio-route.sh start` (it is
  idempotent) after switching sinks, then check the HUD.

`audio-bt.sh` predates this: it finds the headset by name (`Vultech octopus`,
node `-133`), so it gives up on a device that reports as plain `Bluetooth` and
leaves the ports unlinked. Use the `pw-link` lines above in that case.

## Visuals

| Script | Purpose |
|---|---|
| `vis-audio-route.sh {start\|status\|stop}` | Create/link `Hydra-Virtual-Mic`, set it as default source, restore on stop. |
| `vis-hydra-up.sh` | Start routing, serve `visuals/hydra` on `localhost:8000`, open the browser. |
| `vis-hydra-swap.sh <n>` | Set the fallback cue sketch (1-9) in `current.txt` and print the hotkey and `?sketch=` URL for a live swap. |

See [visuals/README.md](../visuals/README.md) and
[visuals/hydra/README.md](../visuals/hydra/README.md).

## Checks

| Script | Purpose |
|---|---|
| `check.sh` | Environment sanity check: binaries, audio, Tidal, samples, disk, reverb limits, and a silent typecheck of every track. |
| `check-tidal.sh [file ...]` | Typecheck tracks without sound: derives a silent boot from `boot/BootTidal.hs` and runs each file in a fresh GHCi. Defaults to every `tracks/*/*.tidal` track. |
| `check-tidal.py` | Convert `.tidal` blocks to GHCi `:{ :}` commands for syntax checks (output can be piped into ghci). |
