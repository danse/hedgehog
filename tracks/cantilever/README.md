# Cantilever

**Separate track.** A playful, jazz-adjacent acoustic illusion: a small
imaginary ensemble anchored at one end, extending under load. **92 BPM base ·
D dorian.** Lazy swing, implied polymeter and through-composition, with slight
tempo shifts at the structural joints.

Only Dirt-Samples acoustic banks are used — double bass, brushed kit, ride,
plucked piano, sax, trumpet sparkles, woodblock, metal, breath and wind. No
custom samples, no pads/arps/casio-style timbres, no obvious electronic
processing.

Eval `00-setup.tidal` once (one `let` block), then play the sections in order:

`01-footing` → `02-span` → `03-load` → `04-overhang` → `05-creak` →
`06-snap` → `07-settle` → `08-afterimage`

## Orbit map

| Orbit | Role | Main pattern |
|---|---|---|
| d1 | soft kick / foot | `kickSoft` / `kickSparse` |
| d2 | brushes | `brush` / `brushFoot` / `brushSnap` |
| d3 | ride | `ride` / `rideBell` / `rub` |
| d4 | piano low / comping | `compSpan` … `compSettle` / `pianoPedal` / `pianoCreak` |
| d5 | piano high / colour | `colourSpan` … `colourOver` / `motifSettle` / `pianoAfter` |
| d6 | double bass | `bassFoot` / `bassWalk` / `bassWalk4` / `bassLoad` / `bassCreak` / `bassSnap` / `bassSettle` |
| d7 | sax | `reedCall` / `reedLong` / `reedCreak` |
| d8 | trumpet sparkle | `trumpetOver` / `trumpetSnap` / `trumpetAfter` |
| d9 | hand percussion / creaks | `wood` / `wood3` / `shime` / `metalSpark` / `creak` |
| d10 | air | `air` / `windBed` |

## Structure (~12½ min, open coda)

| # | Section | Tempo | Cycles | Approx. |
|---|---|---|---|---|
| 1 | **Footing** — the anchor is set; solo bass, room, a foot tap | 92 | 32 | 1:24 |
| 2 | **Span** — the beam extends; ride, comping, 3-against-4 woodblock | 92 | 40 | 1:44 |
| 3 | **Load** — the full ensemble takes weight, still lazy | 92 | 40 | 1:44 |
| 4 | **Overhang** — the far end hangs; tempo nudges up, trumpet appears | 98 | 40 | 1:38 |
| 5 | **Creak** — tempo drops; kit falls away, room and low clusters take over | 86 | 32 | 1:29 |
| 6 | **Snap** — a short hard release, then the hole | 96 | 24 | 1:00 |
| 7 | **Settle** — the structure comes to rest; bluesy piano answer | 92 | 40 | 1:44 |
| 8 | **Afterimage** — open coda; the room keeps the shape | 92 | 40+ | 1:44+ |

## How to run

1. Start SuperDirt/audio (`scripts/up.sh`) and open Tidal in Emacs.
2. Eval `tracks/cantilever/00-setup.tidal` as one block.
3. Work through `01`→`08`. Each section glides to its tempo over 16 s
   (`glideBpm` in `boot/BootTidal.hs`), rather than jumping.
4. `06-snap` is performed in three gestures: the break, then the commented
   "hole" (everything drops except a trumpet stab), then bass alone into
   `07-settle`.
5. `08-afterimage` is open-ended. Leave the last chord ringing, then `hush`
   when the room has decayed.

## Notes

- **Swing** — `swing8 = swingBy (1/5) 4` (8th-note lilt) and
  `swing16 = swingBy (1/5) 8` (16th-note lilt). The delay is in the second
  half of each slice, so the offbeats lean back.
- **Implied polymeter** — `wood3` is a fast-3 woodblock against the 4/4 pulse,
  `shime` is fast-5, and several harmonic phrases use `slow 3` or `slow 4`
  against the bass, so the layers drift in and out of phase.
- **Tuning** — pitched samples are calibrated with `speedAt base p`, e.g.
  `bass1:0 = C2` (`c3`), `pluck:5 = C3` (`c4`), `pluck:8 = D4` (`d5`),
  `sax:5 = C3` (`c4`), `trump:5 = B5` (`b6`), `trump:7 = E6` (`e7`).
  Written pitches are Tidal letter names, one octave above scientific pitch.
- **One-shots** — the setup sets `loop 0` on plucked, reed, trumpet and
  percussion voices so long `sustain` values do not retrigger short samples.
  `windBed` keeps `loop 1` for the coda bed.
- **Chords** — harmony is built with `Sound.Tidal.Chords` (`chordAt`), not
  hand-written voicings. The boot file exposes `tidal-core` so the chord
  module is importable.
- **Levels** — `gain` is non-linear (`amp * gain^4`); reverb `size <= 0.9`.
  The trumpet is deliberately quiet and distant — it should be a sparkle,
  never a featured voice.
- **Tempo glides** — `setbpm` jumps the clock, so section boundaries use
  `glideBpm target 16` (defined in `boot/BootTidal.hs`). It forks and steps the
  tempo 10×/s, so the sender is not blocked; each glide starts from the tempo
  current at call time. Overlapping glides are not cancelled, so leave a
  section playing long enough for its 16 s glide to finish.
- **Trumpet** — `trumpetOver` and `trumpetAfter` use `slow 16`, so each written
  note lands once every 16 cycles. Expect long silences between stabs.
