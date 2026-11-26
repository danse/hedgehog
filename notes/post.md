# Post notes

Raw material, not a draft. Three threads — two bugs, one claim — from
`tracks/ambient/daywork.tidal`, `tracks/techno/grin.tidal` and
`tracks/ambient/loden.tidal`. They can be one piece (the bugs as the opening,
the claim as the turn) or several.

## 1. The bass that wouldn't change pitch

The fix landed as `3fa570b fix the work tune`.

### Symptom

- A 16-note bass motif, `note "g4 g4 a4 b4 …"`, layered over `s "bass1"`.
- Transposing it did nothing audible; the line stayed a low blur.
- `pace 8` "fixed" the rhythm but turned it into a rasp.

### Wrong turns worth keeping

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

### The actual mechanism

- `# = (|>)` and `a |> b = flip union <$> a <* b` (`Core.hs:238,260`).
- `<*` keeps `whole` and `steps` from the left; `part`s are intersected.
- `s "bass1"` is `steps = 1`; `note ns` is `steps = 16`.
- `s "bass1" # note ns` is therefore `steps = 1`, even though it has 16 notes.
- `pace` reads `steps` (`Pattern.hs:82`): `pace 8` on `steps = 1` runs `fast 8`.

### The measurement

| expression | steps | events/cycle |
|---|---:|---:|
| `s "bass1"` | 1 | 1 |
| `note ns` | 16 | 16 |
| `s "bass1" # note ns` | 1 | 16 |
| `pace 8 $ s "bass1" # note ns` | 8 | **128** |

128 events/cycle at 96 BPM ≈ 51 notes/s. A melody played 50× too fast is a
timbre.

### The fix

```haskell
note (pace 8 ns) # s "bass1"
s "bass1*8" # note ns
```

Either way the rhythm sits on the left of `#`.

### Angles for the post

- "Commuting values, not time": `#` looks commutative and isn't.
- The bug is invisible in the source: both versions read like the same
  instrument-plus-notes.
- `pace` is the tell: it is one of the few functions that consumes `steps`.
- Sample pitch: the hit is C1 (~32 Hz) with a strong C2 partial, so "what note
  is this sample" is not a single answer.
- The `whole`/`part` mix-up as a caution about debugging tools.

### Loose ends

- Does `|<` behave the same way? (`#` is `|>`; `|<` is the mirror.)
- How does Tidal 2 spell this? Worth a sentence if the post is
  version-agnostic.

## 2. The live set as the artifact

The same week, one track. Nothing here is about `#`; it is about what the
practice asks of the code.

The bug is one instance of something larger: live coding is the only everyday
practice where changing a running system *is* the deliverable. Nothing is
deployed; the running thing is the artifact. The cost of a wrong idea is
audible in seconds, and "correct" is a property of a performance rather than a
state you reach and protect.

The argument needs the artifact more than the thesis. `grin.tidal` is a set
list, a program and a test target in one file:

- `-- or continue...` is a branch; stage cues ("a stage every two bars") are
  instructions to a performer who is also the compiler.
- `AGENTS.md` is a style guide for a live set: stream numbers follow the order
  voices enter; name a pattern only when another section reuses it.
- Structure is audible: the coda was shorter than its own crossfade, so it
  stopped before the return arrived. Fade length was silently setting section
  length, and nobody had written that rule down.
- One parameter can be the argument: the machine reprise keeps the notes and
  the kick and drops the swing.
- Composition by measurement: the surviving voice had to be a sample long
  enough to hold a bar, so the short ones were ruled out by file length, not
  taste.

### What the checks can't see

Typecheck, then a headless tick with the OSC port pointed at nothing. Both are
cheap and worth having. Neither can see the file's own admission — a
mis-bracketed chord "passes the typechecker, which only sees a string, and fails
when the stream ticks" — and neither can see whether the fades line up, or
whether the thing is any good. A verified live set that still needs ears is
probably the honest centre.

### Angles for the wider piece

1. The score is a running system — show the file, don't describe it.
2. The live set as a test harness — and the limit of the metaphor: no test
   suite, no review, one user, so the transferable skill is narrow.
3. Error as an event, not an abort: audible, fixed on the next bar line, no
   rollback and no incident.

## The claim, verbatim

From the session that built `grin` (Nov 2026), kept because the paraphrase in
thread 2 lost the sharper wording — "legible", "nothing is ever deployed":

> Live coding is the only everyday practice where changing a running system is
> the deliverable. Nothing is ever deployed; the running thing is the artifact.
> That makes the cost of a wrong idea legible in seconds, and it makes
> "correct" a property of a performance rather than a state you reach and then
> protect.

## 3. The horn that clipped the whistle

### Symptom

- In `loden.tidal` section 6, a high-frequency "resonance" got loud when the
  whistle overlapped the horn. The whistle had already been chased once — its
  vibrato swept 86 Hz on a ~0.24 s cycle, dragging the bandpassed air with it —
  and was fixed at pattern level (`depth 0.03 → 0.012`, `breath 0.3 → 0.12`).
  The residual felt like it might be the amplifiers.

### Wrong turns worth keeping

1. **"It's the whistle's vibrato again."** The earlier fix had cut the sweep to
   under one FFT bin. The residual followed the horn, not the whistle.
2. **"It's the playback chain."** Plausible, but an offline render of the two
   synths alone reproduced the loudness, so the signal itself was at fault.

### The actual mechanism

- On the overlapping bars the whistle pitch is exactly two octaves above the
  horn: `df7` = 4 × `df5`, `ef7` = 4 × `ef5`. The whistle fundamental lands on
  the horn's strong 4th saw harmonic, so they stack.
- Both synths set `limitertype 0`. That selects the first branch of
  `Select.ar(limitertype, [signal, Limiter.ar(signal), softclip(...)])` in
  SuperDirt's `dirt_monitor` — i.e. **no limiter at all**. Nothing catches the
  overs.
- The horn's `opening` envelope (`Env.perc(attack * 0.4, 0.3)`,
  `levelScale: 1200`) swept its bandpass from ~1900 Hz down to ~700 Hz in
  0.3 s, straight through the whistle's register. That decay matched the
  reported "short resonance" duration.

### The measurement

Offline render at the section-6 pitches, amps unchanged (`horn 10`,
`whistle 3`):

| case | peak | samples over full scale |
|---|---:|---:|
| horn alone | 3.87 | 13% |
| whistle alone | 1.13 | 8% |
| both | 4.91 | 20% |

After taming the two internal gains (`horn × 0.13`, `whistle × 0.45`) and the
opening (`levelScale 1200 → 500`): horn 0.50, whistle 0.51, both 0.99, **zero**
clipped samples across all four section-6 bars.

### Loose ends / what to refine

- The gain factors were chosen analytically, to land the combined peak just
  under full scale. They have not been checked by ear in the room yet — if the
  horn now sits too quietly against the other voices, raise its `amp` rather
  than the internal gain so the headroom stays explicit.
- Only the whistle and horn were touched. Other synths with vibrato/resonance
  were left alone deliberately.
- The `limitertype 0` setting is still there. A softclip (`limitertype 2`) on
  the horn and whistle orbits would be a different way to catch future overs
  without reducing level; worth trying if more voices start stacking.

## 4. Week of 16–20 Nov 2026

34 commits, 125 files, +4115/−562.

### The speedAt fix

- c9dd2d5: score-first in the `#` chain (boot comment + 7 tracks,
  95+/92−). `#` takes whole/steps from the left, so with the sample
  first swing8 couldn't move notes and pace/segment saw steps=1 —
  thread 1's bug at set scale. tidal.md notes a similar "single note"
  hunt that was really an unbracketed `<...>` (slowcat).

### Classical experiments from scores

- nocturne (Chopin, 37 bars, 40 BPM, ~11 min) and pas de deux (Adam,
  48 bars → 24 cycles, five voices, lead d1, fadeMulti 4).
- Scores were already public; what's new is provenance in the repo:
  agents/making_of/ sources and generators, with a stale/superseded
  table.
- Missing `_` explained: decoder drops note-offs. 391 of 471 tune
  notes are 2-slot holds; the left hand is ~all 1-slot. Envelope is
  a fair stand-in for the left hand, an approximation for the tune —
  TODO in the header.

### New tracks and the agent interface

- Added: oculus, campina, loden, nocturne, pas_de_deux; mezzanine and
  seba extended. Session tally: cantilever 27, daywork 26, tenfold 21.
- agents/ now has making_of/ and toolbox/ READMEs; AGENTS.md is a
  live-set style guide (dN = entry order, shared gotchas, untracked
  drafts vetted by ear).

### The running thing has state the file doesn't

- hush leaves IDs registered as silence; resetCycles only resets the
  clock; no API deletes an ID. A leftover stream surfaced via cycleD.
- Install incident: GHC upgrade broke Tidal via an uninitialised
  tidal-link/link submodule, not ableton-link-dev; no code changes
  for 1.10.3.

### Back to thread 2

- "Correct is a property of a performance" becomes a publication
  rule: commit only what has been listened to. Checks pass; ears decide.

