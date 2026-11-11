# Abutment

**Companion track to Cantilever.** Reassuring, jazz-adjacent acoustic music:
after the failure, the surviving abutment becomes the survey datum, takes the
temporary props, is enlarged, and finally carries the load. **90 BPM home ·
D major.** Lazy swing, through-composed, seven sections in four acts, with an
open coda.

Only Dirt-Samples acoustic banks are used — double bass, brushed kit, ride,
plucked piano, sax, trumpet sparkles, woodblock, glass taps, metal, breath and
wind. No custom samples, no pads/arps/casio-style timbres.

Eval `00-setup.tidal` once (one `let` block), then play the sections in order:

`01-all-clear` → `02-survey` → `03-shore` → `04-abutment` →
`05-transfer` → `06-occupancy` → `07-steady`

## Story

*Cantilever* ends with the snap. *Abutment* starts after the dust has settled.

The projecting span is gone; the heavy block at the anchored end survived. It
was never the visible idea, but it did not fail. The piece is not about
building a bigger cantilever — it is about returning the load to the thing that
can carry it:

1. **All Clear** — the site is declared safe. The abutment stands alone,
   exposed: low D pedal, piano, air. We hear the mass.
2. **Survey** — the wreck is measured from the one thing that has not moved.
   The abutment becomes the datum: woodblock ticks, plumb-line clicks, a
   cautious walking bass.
3. **Shore** — temporary props take the broken stub and cables run the load
   back into the abutment. The first weight since the failure.
4. **Abutment** — the old block is underpinned and new mass is keyed in
   behind it. The turn: tempo lifts, sax enters, warm maj9/6-9 chords.
5. **Transfer** — the props are eased out and the load moves into the
   abutment. A sus4 hangs, then resolves. It holds.
6. **Occupancy** — the span is rebuilt and reopened; people return. Warm
   melody, plagal G–D cadence, brighter but grateful, not triumphant.
7. **Steady** — evening. The structure rests; the load is carried silently.
   Sparse piano, bass and room, then an open coda.

The reassurance is that the conflict is already over. The last thing we hear is
the support, not the span.

## Stream map

`dN` is a stream slot; Tidal sends it to SuperDirt orbit `N-1`.

| Stream | Role | Main pattern |
|---|---|---|
| d1 | soft kick / foot | `kickSoft` / `kickSparse` |
| d2 | brushes | `brushSoft` / `brush` / `brushWork` |
| d3 | ride | `rideSoft` / `ride` / `rideBell` |
| d4 | piano low / comping | `pianoPedal` / `compSurvey` … `compOcc` / `pianoSteady` |
| d5 | piano high / colour | `pianoColour` / `colourSurvey` … `colourOcc` / `pianoAfter` |
| d6 | double bass | `bassPedal` / `bassSurvey` / `bassShore` / `bassAbut` / `bassTrans` / `bassOcc` / `bassSteady` |
| d7 | sax | `reedShore` / `reedAbut` / `reedTrans` / `reedOcc` |
| d8 | trumpet sparkle | `trumpetOcc` / `trumpetSteady` |
| d9 | tools / site sounds | `woodTick` / `plumb` / `knock` / `metalTool` / `wood` |
| d10 | air / room | `air` / `windBed` / `gravel` |

## Structure (~11½ min, open coda)

| Act | # | Section | Tempo | Cycles | Approx. |
|---|---|---|---|---|---|
| I. Assess | 1 | **All Clear** — the abutment alone; dust settles | 90 | 28 | 1:15 |
| | 2 | **Survey** — the datum; measured from the survivor | 90 | 36 | 1:36 |
| II. Repair | 3 | **Shore** — props and tie-backs take the stub | 90 | 36 | 1:36 |
| | 4 | **Abutment** — underpinned; new mass keyed in | 94 | 40 | 1:42 |
| III. Return | 5 | **Transfer** — props eased out; the load moves in | 92 | 36 | 1:34 |
| | 6 | **Occupancy** — rebuilt, reopened, people return | 90 | 40 | 1:47 |
| IV. Rest | 7 | **Steady** — evening; the load is held; open coda | 86 | 40+ | 1:52+ |

## How to run

1. Start SuperDirt/audio (`scripts/up.sh`) and open Tidal in Emacs.
2. Eval `tracks/abutment/00-setup.tidal` as one block.
3. Work through `01`→`07`. Each section glides to its tempo over 16 s
   (`glideBpm` in `boot/BootTidal.hs`), rather than jumping. If `glideBpm` is
   not in scope, restart the Tidal REPL (`C-c C-s`) so the boot reloads.
4. `07-steady` is open-ended. Leave the last chord and air ringing, then
   evaluate `fadeSilence 24 [4,5,6,8,10]`; only after the room has decayed,
   evaluate `hush` on its own.

## Notes

- **Relationship to Cantilever** — Cantilever is D dorian and ends in the
  snap. Abutment answers in D major: the same ensemble, the same room, but the
  low register carries the argument and the cadences are plagal (G–D). The
  unresolved sus chords stand for the load; the six-nine and maj-nine chords
  are the reassurance.
- **Four acts** — the seven sections group as Assess (1–2), Repair (3–4),
  Return (5–6) and Rest (7). *Abutment* is the turn; *Transfer* is the
  resolution; *Occupancy* is the return to normal; *Steady* is the open coda.
- **Shared helpers** — `speedAt`, `swing8`, `swing16`, `chordAt` and
  `fadeSilence` are defined in `boot/BootTidal.hs`; the setup only defines this
  track's voices.
- **Swing** — `swing8 = swingBy (1/5) 4` (8th-note lilt) and
  `swing16 = swingBy (1/5) 8` (16th-note lilt). The offbeats lean back.
- **Tuning** — pitched samples are calibrated with `speedAt base p`:
  `bass1:0 = C2` (`c3`), `pluck:5 = C3` (`c4`), `pluck:8 = D4` (`d5`),
  `sax:5 = C3` (`c4`), `trump:5 = B5` (`b6`), `trump:7 = E6` (`e7`).
  Written pitches are Tidal letter names, one octave above scientific pitch.
- **One-shots** — each voice triggers its sample once; `sustain` and `release`
  shape the tail.
- **Chords** — harmony is built with `Sound.Tidal.Chords` (`chordAt`), not
  hand-written voicings. The boot file exposes `tidal-core` so the chord
  module is importable.
- **Levels** — this track uses `amp` (linear) rather than `gain`
  (`amp * gain^4`); reverb `size <= 0.9`. The mix has not been balanced by ear
  yet, so expect to trim `amp` values once you hear it. The trumpet is
  deliberately quiet and distant.
- **Tempo glides** — `setbpm` jumps the clock, so section boundaries use
  `glideBpm target 16` (defined in `boot/BootTidal.hs`). It forks and steps the
  tempo 10×/s, so the sender is not blocked; each glide starts from the tempo
  current at call time. Overlapping glides are not cancelled, so leave a
  section playing long enough for its 16 s glide to finish.
- **Trumpet** — `trumpetOcc` and `trumpetSteady` use `slow 16`, so each written
  note lands once every 16 cycles. Expect long silences between stabs.
- **Open coda** — `07-steady` does not stop itself. `fadeSilence` and `hush`
  are separate blocks; evaluate them in order, with a pause between.
