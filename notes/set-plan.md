# Hedgehog — set plan

**Tempo** 72 BPM · **Key** D minor · **Length** ~16 min · **Mood** ambient / downtempo

One cycle = 4 beats ≈ 3.33 s. `slow 4` = a chord every 13 s, `slow 8` ≈ 27 s.

## Movements

| # | Movement | Time | Streams | Action |
|---|---|---|---|---|
| 1 | Emergence | 0:00–3:00 | d1, d2 | Pads and sub only. No pulse. Let the room hear the drone. |
| 2 | Slow pulse | 3:00–6:00 | + d5 | Add `tick`. Add air (d4) quietly at 5:00. |
| 3 | Bloom | 6:00–10:00 | + d6, d7 | Pad progression and plucked melody. Open filters slowly. |
| 4 | Drift | 10:00–13:00 | − d7, d5 | Strip the melody, half-time pulse, darken the pad. |
| 5 | Dissolve | 13:00–16:00 | d1, d2 | Remove everything but bed and drone. Slow fade to `hush`. |

## Cue sheet

Eval `00-setup.tidal` first, then open the movement files. Keys: `C-RET` evals the
block under the cursor, `C-c C-h` hushes, `C-c C-s` starts/stops the Tidal REPL.

### 1 — Emergence
```
d1 $ bed
d2 $ drone
```
Wait at least two pad cycles (~53 s) before touching anything.

### 2 — Slow pulse
```
d5 $ tick
d4 $ air
```
Resist adding more. The pulse should be felt, not counted.

### 3 — Bloom
```
d6 $ pad
d7 $ degradeBy 0.3 $ pluck
```
Filter opening: `d6 $ pad # lpf (range 500 3500 $ slow 16 sine)`.
Change the phrase length of the melody rather than the notes:
`d7 $ degradeBy 0.15 $ slow 2 $ pluck`.

### 4 — Drift
```
d7 $ silence
d5 $ slow 4 $ tick
d6 $ pad # lpf 700 # gain 0.35
```
This section is allowed to be almost empty.

### 5 — Dissolve
```
d6 $ silence
d4 $ silence
d5 $ silence
d1 $ bed # lpf 600 # gain 0.35
```
Finally `hush` and let the room/hall tail ring.

## Transitions available

- `xfadeIn STREAM CYCLES $ pattern` — crossfade a new pattern in.
- `xfadeIn STREAM CYCLES $ silence` — crossfade out.
- `d9 $ riser` / `d9 $ silence` — noise swell into a new section.
- `hush` — emergency stop.

## Recovery

1. `hush`
2. `setbpm 72`
3. Re-eval `00-setup.tidal`, then one movement file.
4. If the REPL is wedged: `C-c C-i` (interrupt), then `C-c C-s` (restart).

## Recording notes

- Record from the default monitor with `scripts/record.sh take-<name>`.
- Leave 6 dB of headroom; ambient material is dense in the low end.
- Keep two takes per session, same cue sheet, and compare afterwards.
- Takes are gitignored; move the keepers out of `recordings/` if you want them tracked.

## Rehearsal checklist

- [ ] Sound check: sub audible but not booming, pad not masking the pulse.
- [ ] Cue through all five movements without a silence gap.
- [ ] Practice one deliberate mistake + recovery.
- [ ] Know where `hush` is without looking.
- [ ] 10 GB free before a long take.
