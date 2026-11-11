# Substructure

**Separate track** (not part of the Hedgehog live set). Complex-bass ambient,
no pads or drones. **72 BPM · D minor · focus: complex bass structure**
(8-cycle evolving form).

Eval `00-setup.tidal` first, then play the section files in order:

`01-intro` → `02-build` → `03-main` → `04-breakdown` → `05-rebuild` →
`06-outro`

No sustained pad beds or drones in this track — harmony/texture use fragmented,
rhythmic, or staccato samples (`arpy`, `moog`, `stab`, `glitch`, `space`,
`industrial`, `pluck`).

## Stream map

`dN` is a stream slot; Tidal sends it to SuperDirt orbit `N-1`.

| Stream | Role | Main pattern |
|---|---|---|
| d1 | kick | `kick` |
| d2 | hats/click | `hats` / `click` |
| d3 | percussion | `perc` |
| d4 | harmony (continuous) | `chordFlow` / `chordStab` / `chordStabAlt` / `chordPulse` / `stabHit` |
| d5 | texture fragments | `glitchTex` / `spaceTex` / `metalTex` |
| d6 | motif | `motif` / `motifArp` |
| d7 | fx | `riser` / `burst` |
| d8 | bass (main) | `bassMain` / `bassDrive` / `bassBreak` |
| d9 | bass (anchor) | `bassAnchor` |
| d10 | bass (ghost/detail) | `bassGhost` |

## Structure (~6–8 min sketch, extend by repeating sections)

1. **Intro** (`01-intro.tidal`) — sparse texture + bass enters (main, dark filter), establish the 8-cycle form.
2. **Build** (`02-build.tidal`) — add anchor/ghost bass layers, harmony stabs, light pulse/texture.
3. **Main** (`03-main.tidal`) — full groove: kick/hats, stabs/texture, motif answers bass; optional drive.
4. **Breakdown** (`04-breakdown.tidal`) — remove drums/detail, `bassBreak`/dark bass + sparse stabs/texture.
5. **Rebuild** (`05-rebuild.tidal`) — pulse and detail return: `bassDrive`/anchor/ghost, pulsing
   harmony, metal/space texture and `motifArp`; optional kick for the last wave.
6. **Outro** (`06-outro.tidal`) — dissolve to bass fragments and sparse texture, then silence.

## How to run

1. Start SuperDirt/audio as usual (`scripts/up.sh` from repo root) and open Tidal in Emacs.
2. Eval `tracks/substructure/00-setup.tidal`.
3. Work through `01`→`06` in order, or improvise using the stream map.

## Notes

- Bass is intentionally complex: two 4-cycle phrases (`bassA/B`) concatenated
  into an 8-cycle form, patterned sustain, and moving filter. Anchor/ghost
  layers add rhythmic structure without cluttering the low root.
- Keep headroom: bass + kick + stabs can build up. If muddy, lower `d4`/`d8`
  gain slightly or cut `d8` lpf.
- `gain` is non-linear in SuperDirt (`amp * gain^4`); reverb `size <= 0.9`.
