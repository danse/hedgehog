# Tenfold

**Separate track.** Synthapella-inspired ambient. **125 BPM · B♭ minor.**
No drums or percussion — drones, pads, arp, lead, bell, filtered noise and
shimmer only.

Inspired by the synth-only version of Stephan Bodzin's "Powers of Ten": slow
melodic/ambient evolution, no drums. **Progression** i–VI–III–VII
(`bfm – gf – df – af`).

Eval `00-setup.tidal` once (one `let` block), then play the sections in order:

`01-emergence` → `02-ascent` → `03-expansion` → `04-suspension` →
`05-drift` → `06-dissolve`

## Orbit map

| Orbit | Role | Main pattern |
|---|---|---|
| d1 | sub drone | `subDrone` |
| d2 | low pad | `lowPad` |
| d3 | high pad | `highPad` |
| d4 | arpeggio | `arp` |
| d5 | lead melody | `lead` / `melody` |
| d6 | bell / counter | `bell` |
| d7 | noise / air | `noiseBed` |
| d8 | synth bass | `bassPulse` / `bassLong` |
| d9 | shimmer | `shimmer` |

## Structure (~7–9 min)

1. **Emergence** (`01-emergence.tidal`) — sub drone and low pad only.
2. **Ascent** (`02-ascent.tidal`) — high pad, soft bass, first arp hint.
3. **Expansion** (`03-expansion.tidal`) — full palette: arp, lead, bell, texture.
4. **Suspension** (`04-suspension.tidal`) — pulse loosens to long bass; lead
   becomes the higher, sparser melody; pads and bells float.
5. **Drift** (`05-drift.tidal`) — lead/bell/arp fade out; pads, noise, long bass.
6. **Dissolve** (`06-dissolve.tidal`) — pads/drone only, then silence.

## How to run

1. Start SuperDirt/audio (`scripts/up.sh`) and open Tidal in Emacs.
2. Eval `tracks/tenfold/00-setup.tidal` (one `let` block, all at once).
3. Work through `01`→`06`, using `fadeSilence n [orbits]` for group fades.

## Notes

- No percussion: motion comes from the arp, bass pulse and slow filter moves.
- The setup is a single `let` block; keep it free of blank lines if editing.
- `gain` is non-linear (`amp * gain^4`); reverb `size <= 0.9`.
