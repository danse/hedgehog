# `#` and its precedence

`#` merges control values, but it takes the **time structure from its left**
operand (`tidal-core/src/Sound/Tidal/Core.hs:260`):

```haskell
(#) = (|>)
a |> b = flip union <$> a <* b    -- structure from left, values from right
```

`<*` keeps the left pattern's `whole` and `steps`
(`tidal-core/src/Sound/Tidal/Pattern.hs:140`); the event `part`s are the
intersection. So values commute, rhythm does not:

| pattern | `steps` |
|---|---:|
| `s "bass1"` | 1 |
| `note "g4 a4 b4 c5"` | 4 |
| `s "bass1" # note "g4 a4 b4 c5"` | 1 |
| `note "g4 a4 b4 c5" # s "bass1"` | 4 |

`pace n` and `segment n` read `steps` (`Pattern.hs:82`, `UI.hs:1186`), so that
is where it bites:

```haskell
pace 8 $ s "bass1" # note ns   -- steps = 1 -> fast 8 -> 128 events/bar
note (pace 8 ns) # s "bass1"   -- steps = 8 -> 8 events/bar
s "bass1*8" # note ns          -- same, rhythm written on the left
```

**Rule:** put the rhythm-carrying operand first, or write the rhythm into `s`,
and let `pace`/`segment` wrap the pattern whose step count you mean. Pitches
and other controls (`note`, `n`, `speed`, …) belong on the right.

Daywork's `motifBass` was the first form: 16 notes crammed into 1/8 of a cycle
and repeated 8× — about 51 notes/s at 96 BPM, so the tune was heard as a
timbre rather than a melody.
