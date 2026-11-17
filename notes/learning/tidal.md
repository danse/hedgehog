# `#` and its precedence

`#` merges control values and takes the `whole`/`steps` metadata (what Tidal
calls the time structure) from its left operand
(`tidal-core/src/Sound/Tidal/Core.hs:260`):

```haskell
(#) = (|>)
a |> b = flip union <$> a <* b    -- structure from left, values from right
```

`<*` keeps the left pattern's `whole` and `steps`
(`tidal-core/src/Sound/Tidal/Pattern.hs:140`); the event `part`s are the
intersection. So values commute; the metadata does not:

| pattern | `whole` | `steps` | events |
|---|---|---:|---:|
| `s "bass1"` | `0>1` | 1 | 1 |
| `note "g4 a4 b4 c5"` | `0>¼`, `¼>½`, … | 4 | 4 |
| `s "bass1" # note "g4 a4 b4 c5"` | `0>1` (all four) | 1 | 4 |
| `note "g4 a4 b4 c5" # s "bass1"` | `0>¼`, `¼>½`, … | 4 | 4 |

**The event count does not change.** `s "bass1" # note "g4 a4 b4 c5"` still
fires four notes, one per quarter; `#` only gives each of them a bar-length
`whole` and `steps = 1`. The audible `part`s are the intersection of both
operands, so the finer rhythm survives either way.

`pace n` and `segment n` read `steps` (`Pattern.hs:82`, `UI.hs:1186`), and
`swing8`/`swing16` place their shifts from `whole`, so those are the
transforms where the left-hand `whole`/`steps` actually bite:

```haskell
pace 8 $ s "bass1" # note ns   -- steps = 1 -> fast 8 -> 128 events/bar
note (pace 8 ns) # s "bass1"   -- steps = 8 -> 8 events/bar
s "bass1*8" # note ns          -- same, rhythm written on the left
```

**Rule:** put the rhythm-carrying operand first, or write the rhythm into `s`,
and let `pace`/`segment` wrap the pattern whose step count you mean. Not
because `#` changes how many events fire, but because `whole`/`steps` come
from the left and decide how whole-sensitive transforms act. Pitches and
other controls (`note`, `n`, `speed`, …) belong on the right.

This is why the `speedAt` "single note" hunt looked like an operand-order bug:
`s "gtr:0" # speedAt "c2" line` fires exactly the same events as the
score-first order — it only leaves each one with a bar-length `whole`. The
real cause was an unbracketed `<...>` line, which is `slowcat`: one token per
cycle.

Daywork's `motifBass` was the first form: 16 notes crammed into 1/8 of a cycle
and repeated 8× — about 51 notes/s at 96 BPM, so the tune was heard as a
timbre rather than a melody.
