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
  `xfadeIn`, `clutchIn`, `clear`, `fadeSilence` targets). Prefer selective
  `fadeSilence` or `multi xfadeIn` over `clearAll`.
- Browse spines with `agents/toolbox/spines.py` (dam decks in `notes/spines/`)
  to find compatible carriers.
- Editing live: ears decide mix/noise/commit; offer A/B and wait. Preserve
  uncommitted edits; keep old versions as comments only when asked. `amp` is
  linear level, `gain` a trim, `level a p` clears the trim; `size <= 0.9`. Use
  `clutchIn` for entries and `xfadeIn`/`fadeMulti` for fades. Inline patterns at
  their section; `let` only for reuse. Short comments; `-- from N` only for a
  fixed in-track tempo change, not a landing glide.
- Verify: run `scripts/check-tidal.sh <file>` and report. Do not commit, `hush`,
  restart the REPL or clear streams without being asked.
