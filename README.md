# Hedgehog

Live-coded tracks. TidalCycles → SuperDirt → PipeWire JACK, edited in a
project-contained Emacs.

Tracks live in `tracks/`; each folder has its own tiny README and a `00-setup.tidal`
to evaluate first. See `tracks/hedgehog/README.md` for the main ambient set.

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
scripts/check.sh        # verify binaries, audio, Tidal, samples, disk
scripts/up.sh           # start SuperDirt
scripts/edit.sh         # open Emacs on tracks/
```

`up.sh --no-emacs` starts only SuperCollider. `scripts/down.sh` stops it.
Logs go to `logs/superdirt.log`.

## Playing

Open a track under `tracks/` and evaluate its `00-setup.tidal` first, then work
through the numbered section files (each track README lists the order).

| Key | Action |
|---|---|
| `C-RET` | eval the block under point (blank-line separated) |
| `C-c C-c` | eval the current line |
| `C-c C-r` | eval the active region |
| `C-c C-h` / `C-c C-k` | hush everything |
| `C-c C-s` | start / restart the Tidal REPL |
| `C-c C-i` | interrupt the REPL |
| `C-c C-v` | show the Tidal output buffer |

## Layout

```
boot/     BootTidal.hs, BootSuperDirt.scd (SuperDirt + project synths)
emacs/    init.el, lisp/tidal.el — self-contained editor config
tracks/   one folder per track; each has README + 00-setup + sections
scripts/  up, down, edit, record, checks
notes/    set plan, cue sheet, recovery
samples/  optional extra samples (not loaded until uncommented)
recordings/  gitignored takes
```

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
re-runs `boot/BootTidal.hs`. Definitions in `00-setup` must be re-evaluated
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
