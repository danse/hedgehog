# Hedgehog

Live-coded tracks. TidalCycles → SuperDirt → PipeWire JACK, edited in a
project-contained Emacs.

Tracks live under `tracks/`, one folder per genre (`tracks/ambient/`,
`tracks/techno/`, `tracks/dance/`); each track is a single `<track>.tidal` file
with its setup block and sections. Evaluate the setup block at the top first. See
`tracks/ambient/hedgehog.tidal` for a complete set.

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
scripts/edit.sh         # open Emacs in tracks/
```

`up.sh --no-emacs` starts only SuperCollider. `scripts/down.sh` stops it.
Logs go to `logs/superdirt.log`.

## Playing

Open a track under `tracks/ambient/`, `tracks/techno/` or `tracks/dance/` and
evaluate the setup block at the top of its `.tidal` file first, then work
through the sections below (the file header lists the order).

Within a track, `dN` numbers follow the order the streams first enter, so `d1`
is always the opening sound.

Landing a track with fewer seats over one with more leaves **voice overflows** —
`dN` streams from the first track that the incoming track never rewrites. See
`notes/learning/voice-overflows.md` for the set-difference method and selective
fades; prefer those to a blanket `clearAll` when the outgoing tail is worth
keeping.

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

- `tracks/` — one folder per genre (`ambient/`, `techno/`, `dance/`), one
  `snake_case` `.tidal` file per track (`baroque_carnival.tidal`);
  `scripts/edit.sh` opens Emacs here
- `scripts/` — see `scripts/README.md`
- `agents/` — agent-facing material: `agents/making_of/` (score sources and
  generators), `agents/toolbox/` (helper scripts) and `agents/skills/` (OpenCode
  skills), each with its own README
- `visuals/` — see `visuals/README.md`
- `notes/` — set plan, TODO, learning notes in `notes/learning/`; tag decks in
  `notes/ontology/` (`spines/`, `dimensions/`); ordered session guide in
  `notes/sessions/`
- `samples/` — see `samples/README.md`

`boot/` holds the Tidal/SuperDirt boot files, with the project SynthDefs in
`boot/HedgeSynths.scd` (loaded by `boot/BootSuperDirt.scd`). `emacs/` holds the
project editor config (which loads `~/.emacs` last, so personal preferences win;
batch checks skip it), and `recordings/` the gitignored takes.
`boot/BootTidal.hs` also defines the shared track helpers (`speedAt`, `swing8`,
`swing16`, `chordAt`, `fadeSilence`, `fadeMulti`, `glideBpm`, `cycleD`), so each
track's setup block only defines its own voices and arrangements.

The root `TAGS` file indexes the boot files, tracks, scripts, agent tools and
Hydra sketches for Emacs (`visit-tags-table`). It is generated and gitignored;
regenerate it from the repo root with:

```sh
find boot tracks scripts agents emacs visuals/hydra -type f \( -name '*.hs' -o -name '*.tidal' -o -name '*.py' -o -name '*.sh' -o -name '*.js' -o -name '*.el' -o -name 'midi-reader' \) -print0 | xargs -0 etags
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
re-runs `boot/BootTidal.hs`. Setup-block definitions must be re-evaluated
after a restart.

**Clicking / xruns** — realtime limits are not installed; see Phase 0.4 in the
project notes. Reduce `s.options.numBuffers` or raise `s.latency` in
`boot/BootSuperDirt.scd`.

**A synth is missing** — `sc3-plugins` supplies SuperDirt's `super*` synths;
project-defined ones live in `boot/HedgeSynths.scd`. Restart SuperCollider
after changing that file.

## Credits

TidalCycles (Alex McLean and contributors), SuperDirt (Julian Rohrhuber, Alex
McLean), Dirt-Samples (tidalcycles). Check sample licences before publishing
recordings.
