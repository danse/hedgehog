# Hedgehog

Live-coded tracks. TidalCycles → SuperDirt → PipeWire JACK, edited in a
project-contained Emacs.

Tracks live in one folder per genre (`ambient/`, `techno/`); each track is a
single `<track>.tidal` file with its setup block and sections. Evaluate the
setup block at the top first. See `ambient/hedgehog.tidal` for a complete set.

## Status

| Piece | State |
|---|---|
| Tidal 1.10.3 on GHC 9.8.4 | installed via `cabal install --lib` |
| SuperDirt 1.7.3 + Dirt-Samples | present (218 banks loaded) |
| Project boot files, custom synths, live set | written and syntax-checked |
| `pipewire-jack` | installed; SC routes to the USB sink |
| End-to-end audio | **verified** (bd/sn, sine and pad recorded from the monitor) |
| Realtime priority limits | **pending** — install before rehearsing |

## Start

```sh
scripts/check.sh        # verify binaries, audio, Tidal, samples, disk, tracks
scripts/up.sh           # start SuperDirt
scripts/edit.sh         # open Emacs on the project
```

`up.sh --no-emacs` starts only SuperCollider. `scripts/down.sh` stops it.
Logs go to `logs/superdirt.log`.

## Playing

Open a track under `ambient/` or `techno/` and evaluate the setup block at the
top of its `.tidal` file first, then work through the sections below (the file
header lists the order).

Within a track, `dN` numbers follow the order the streams first enter, so `d1`
is always the opening sound.

| Key | Action |
|---|---|
| `C-RET` | eval the block under point (blank-line separated) |
| `C-c C-c` | eval the current line |
| `C-c C-r` | eval the active region |
| `C-c C-h` / `C-c C-k` | hush everything |
| `C-c C-s` | start / restart the Tidal REPL |
| `C-c C-i` | interrupt the REPL |
| `C-c C-v` | show the Tidal output buffer |

`C-RET` and `C-c C-r` split adjacent top-level expressions (blocks of `dN`,
`xfadeIn`, `fadeSilence`, bindings, etc.) and send them one at a time. A
multi-line single expression or a `let` block is wrapped in `:{ ... :}`.
Indented statements and continuation lines are handled.

## Layout

Each area documents itself:

- `ambient/`, `techno/` — one folder per genre, one `.tidal` file per track
- `scripts/` — see `scripts/README.md`
- `visuals/` — see `visuals/README.md`
- `notes/` — set plan, TODO, learning notes in `notes/learning/`
- `samples/` — see `samples/README.md`

`boot/` holds the Tidal/SuperDirt boot files, `emacs/` the project editor config,
and `recordings/` the gitignored takes. `boot/BootTidal.hs` also defines the
shared track helpers (`speedAt`, `swing8`, `swing16`, `chordAt`, `fadeSilence`,
`fadeMulti`, `glideBpm`), so each track's setup block only defines its own
voices and arrangements.

## Sound check

```sh
scripts/up.sh --no-emacs
scripts/edit.sh
```
Then in Emacs:

```haskell
d1 $ s "bd sn"
d2 $ s "hh*8" # gain 0.5
```
Hear the USB output, then `hush`.

## Recording

```sh
scripts/record.sh take-01        # Ctrl-C to stop
```
Records the default PipeWire/Pulse monitor to 24-bit WAV in `recordings/`.
For a clean take, close notification sounds or route SuperDirt to its own sink.

## Troubleshooting

**No sound / `Cannot connect to server socket`** — SuperCollider is not going
through PipeWire. Check `command -v pw-jack`; `scripts/up.sh` launches sclang via
`pw-jack`, so install `pipewire-jack` first.

**SuperDirt did not come up** — `tail -30 logs/superdirt.log`. Common causes:
audio device busy, `sclang` not on PATH, PipeWire JACK library missing.

**Tidal REPL says a function is not in scope** — `C-c C-s` restarts ghci and
re-runs `boot/BootTidal.hs`. Setup-block definitions must be re-evaluated
after a restart.

**Clicking / xruns** — realtime limits are not installed; see Phase 0.4 in the
project notes. Reduce `s.options.numBuffers` or raise `s.latency` in
`boot/BootSuperDirt.scd`.

**A synth is missing** — the `super*` synths shipped with SuperDirt need
`sc3-plugins`, which is not installed. This set uses samples plus three custom
synths (`hedge_sine`, `hedge_pad`, `hedge_noise`) defined in `BootSuperDirt.scd`,
so it does not depend on them.

## Credits

TidalCycles (Alex McLean and contributors), SuperDirt (Julian Rohrhuber, Alex
McLean), Dirt-Samples (tidalcycles). Check sample licences before publishing
recordings.
