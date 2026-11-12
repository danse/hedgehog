# Post notes: the bass that wouldn't change pitch

Raw material, not a draft. Track: `tracks/ambient/daywork.tidal`; the fix landed as
`3fa570b fix the work tune`.

## Symptom

- A 16-note bass motif, `note "g4 g4 a4 b4 …"`, layered over `s "bass1"`.
- Transposing it did nothing audible; the line stayed a low blur.
- `pace 8` "fixed" the rhythm but turned it into a rasp.

## Wrong turns worth keeping

1. **"Samples don't support `note`."** They do. `note` becomes `~freq`, and for
   a buffer `freq` is a resample ratio: `rate = speed * (freq / 60.midicps)`
   (`core-synths.scd:31`). Absolute for synths, relative for samples.
2. **"It's just the register."** Plausible: `g4…c5` on a C1 sample is 18–33 Hz,
   so `|+ 24` should make it audible. It didn't, because pitch was never the
   problem.
3. **"All 16 notes are stacked on one event."** They aren't. Printing `whole`
   shows every event carrying the left pattern's `0>1/8`, which looks like a
   stack. Printing `part` shows they are sequential: 16 notes inside 1/8 of a
   cycle, repeated 8×. A diagnostic that lied by omission.

## The actual mechanism

- `# = (|>)` and `a |> b = flip union <$> a <* b` (`Core.hs:238,260`).
- `<*` keeps `whole` and `steps` from the left; `part`s are intersected.
- `s "bass1"` is `steps = 1`; `note ns` is `steps = 16`.
- `s "bass1" # note ns` is therefore `steps = 1`, even though it has 16 notes.
- `pace` reads `steps` (`Pattern.hs:82`): `pace 8` on `steps = 1` runs `fast 8`.

## The measurement

| expression | steps | events/cycle |
|---|---:|---:|
| `s "bass1"` | 1 | 1 |
| `note ns` | 16 | 16 |
| `s "bass1" # note ns` | 1 | 16 |
| `pace 8 $ s "bass1" # note ns` | 8 | **128** |

128 events/cycle at 96 BPM ≈ 51 notes/s. A melody played 50× too fast is a
timbre.

## The fix

```haskell
note (pace 8 ns) # s "bass1"
s "bass1*8" # note ns
```

Either way the rhythm sits on the left of `#`.

## Angles for the post

- "Commuting values, not time": `#` looks commutative and isn't.
- The bug is invisible in the source: both versions read like the same
  instrument-plus-notes.
- `pace` is the tell: it is one of the few functions that consumes `steps`.
- Sample pitch: the hit is C1 (~32 Hz) with a strong C2 partial, so "what note
  is this sample" is not a single answer.
- The `whole`/`part` mix-up as a caution about debugging tools.

## Loose ends

- Does `|<` behave the same way? (`#` is `|>`; `|<` is the mirror.)
- How does Tidal 2 spell this? Worth a sentence if the post is
  version-agnostic.
