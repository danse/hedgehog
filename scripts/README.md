# Scripts

Helper scripts for running the set, switching audio, recording, and driving
visuals. Paths are relative to the repo root.

## Start / stop

| Script | Purpose |
|---|---|
| `up.sh` | Start `scsynth` and SuperDirt under `pw-jack`, route audio to Bluetooth, and open Emacs on the project. `--no-emacs` starts only SuperCollider. |
| `down.sh` | Stop SuperDirt and project `scsynth`. |
| `edit.sh` | Open the project-contained Emacs in `tracks/`. |

`up.sh` starts `scsynth` as a separate process before `sclang`. If `sclang`
spawns it instead, it inherits sclang's UDP socket on port 57120 and steals
OSC replies and Tidal messages, so SuperDirt starts but stays silent. The boot
file does not boot a server; run `pw-jack scsynth ...` first if starting by hand.

## Audio

| Script | Purpose |
|---|---|
| `audio-usb.sh` | Route SuperCollider output to the USB audio device. |
| `audio-bt.sh` | Route SuperCollider output to Bluetooth headphones. |
| `record.sh [name]` | Record the default monitor to 24-bit WAV in `recordings/`. |

## Analysis

| Script | Purpose |
|---|---|
| `analyse-audio.py [--window S] [--bands Hz,...] [--f0] [--raw-f32 SR CH] FILE…` | Per-window RMS, peak, spectral centroid and band balance, with optional pitch. Needs only numpy. This is where the one-off audio analyses live so they survive a `/tmp` wipe — e.g. the pluck sample's hissy tail (centroid 333 → 4057 Hz over 1.5 s). |

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

`audio-bt.sh` selects the routable `bluez_output` `Audio/Sink` node, so it no
longer mistakes the device or the internal driver for a default sink. It also
unmutes the headset, sets a safe volume and links `SuperCollider:out_1/2` to
that sink's JACK playback ports. If your headset reports under a different
name, use the `pw-link` lines above.

## Visuals

| Script | Purpose |
|---|---|
| `vis-audio-route.sh {start\|status\|stop}` | Create/link `Hydra-Virtual-Mic`, set it as default source, restore on stop. |
| `vis-hydra-up.sh` | Start routing, serve `visuals/hydra` on `localhost:8000`, open the browser. |

`vis-audio-route.sh start` preserves the default sink's volume and mute state.
Without this, starting `pw-loopback` can make WirePlumber reapply an old saved
volume and drop the headset to near-silence. It also only saves/restores real
`Audio/Source` nodes, so a stale sink ID cannot become the default source.
| `vis-hydra-swap.sh <n>` | Set the fallback cue sketch (1-10) in `current.txt` and print the hotkey and `?sketch=` URL for a live swap. |

See [visuals/README.md](../visuals/README.md) and
[visuals/hydra/README.md](../visuals/hydra/README.md).

## Checks

| Script | Purpose |
|---|---|
| `check.sh` | Environment sanity check: binaries, audio, Tidal, samples, disk, reverb limits, and a silent typecheck of every track. |
| `check-tidal.sh [file ...]` | Typecheck tracks without sound: derives a silent boot from `boot/BootTidal.hs` and runs each file in a fresh GHCi. Defaults to every `tracks/*/*.tidal` track. Errors report the `.tidal` file and line number, not GHCi's `<interactive>` counter. |
| `check-tidal.py` | Convert `.tidal` blocks to GHCi `:{ :}` commands for syntax checks (output can be piped into ghci). |
