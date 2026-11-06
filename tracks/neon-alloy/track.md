# Neon Alloy — track plan

**Separate track**. Glam electro-pop / synth noir vibe (driving bass, crisp electro drums, shimmering synths/hooks).  
**Tempo** 118 BPM · **Key** A minor

## Orbit map
| Orbit | Role | Main pattern |
|---|---|---|
| d1 | kick | `kick` / `kickDrive` |
| d2 | snare/clap | `snare` / `clap` |
| d3 | hats/percussion | `hats` / `hatsOpen` / `perc` |
| d4 | chords/synth/arp | `chords` / `chordsStab` / `arp` |
| d5 | lead/hook | `hook` / `lead` |
| d6 | texture/accents | `stab` / `hoover` / `shimmer` |
| d7 | fx | `riser` / `impact` |
| d8 | bass | `bassMain` + `bassOct` / `bassDrive` |

## Structure (~4–6 min)
1. **Intro** (`01-intro.tidal`) — beat + bass + filtered chords.
2. **Verse** (`02-verse.tidal`) — groove settles, hook teases in.
3. **Chorus** (`03-chorus.tidal`) — full lift: hook, arp/stabs, open hats, bass drive option.
4. **Break** (`04-break.tidal`) — strip to chords/bass fragments + tension.
5. **Final** (`05-final.tidal`) — last chorus energy and outro.

## How to run
1. Start SuperDirt/audio (`scripts/up.sh`) and open Tidal in Emacs.
2. Eval `tracks/goldfrapp/00-setup.tidal`.
3. Work through `01`→`05`.

## Notes
- `gain` is non-linear (`amp * gain^4`); reverb `size <= 0.9`.
- `hoover`/sample names depend on your Dirt-Samples; swap if missing (`moog`, `stab`, `arpy` are safe fallbacks).
