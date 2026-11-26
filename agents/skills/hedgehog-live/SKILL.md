---
name: Hedgehog live coding
description: Guide Hedgehog live sessions: handovers, landings, voice overflows and safe verification.
---

# Live-session protocol

Use during live coding, handovers and A/B tuning. Read `AGENTS.md`,
`notes/learning/gotchas.md`, `notes/learning/voice-overflows.md` and the target
header first.

- Establish state: current track/section (ask if unsure); seat maps from headers
  (`dN` = first entry). Streams can outlive their track — check fades, `list` or
  `cycleD <secs>`.
- Next track: gentle handover in tempo/key/density at a landing; contrast only
  when asked. Name the concrete line; don't bake it into a file. A double blank
  is a landing: the texture can hold there.
- Overflow: `seats(out) \ seats(in)`, including rewritten IDs (`dN`, `multi`,
  `xfadeIn`, `clutchIn`, `clear`, `fadeSilence` targets). Take a silence barrier
  only when the form wants one; on an upbeat handover, fade the leftovers
  before the next intro with selective `fadeSilence` or `multi xfadeIn`.
  `ID` has `Num` but not `Enum`: write `[6,7,8]`, never `[6..8]`.
  `clearAll` and any `clutchIn ... silence` cut tails — avoid them. Don't thin
  event density to smooth a join; that tends to sound clumsy.
- Browse tag schemes with upstream `dam-query`; pass `notes/ontology/spines`
  or `notes/ontology/dimensions` directly. The local `dam.py` is deprecated.
- Editing live: ears decide mix/noise/commit; offer A/B and wait. Preserve
  uncommitted edits; keep old versions as comments only when asked. `amp` is
  linear level, `gain` a trim, `level a p` clears the trim; `size <= 0.9`.
  `lpf`/`hpf` moves are a core device here; give them the same visibility as
  `amp`, with `-- from lpf <value>` fallbacks. Use
  `clutchIn` for entries and `xfadeIn`/`fadeMulti` for fades. Inline patterns at
  their section; `let` only for reuse. Short comments; a trailing `-- from ...`
  names the value a change replaces.
- A/B lines: render each suggestion in a fenced `haskell` block, one line per
  option, so the live coder can select and copy it directly rather than pick it
  out of prose. Annotate the replaced value with `-- from <param> <value>`
  (`-- from N` for tempo); that is the immediate fallback. On a social stream,
  treat that readability as part of the performance: listeners may start to care
  precisely because the move is legible and reversible.
- Direct seats: `dN` takes one `ControlPattern`. Prefer composition:
  `d7 . bellVoice $ slow 4 counter`, `d6 . shadowVoice $ shadow`; never
  `d7 bellVoice $ ...`. For parameter chains, `d8 . (air #) $ amp 0.14`.
- Verify: run `scripts/check-tidal.sh <file>` and report. Do not commit, `hush`,
  restart the REPL or clear streams without being asked.
