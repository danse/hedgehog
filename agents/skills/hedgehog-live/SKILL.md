---
name: Hedgehog live coding
description: Guide Hedgehog live sessions: next-track choices, landings, voice overflows, A/B edits and safe verification.
---

# Live-session protocol

Use this during live coding, track handovers and A/B tuning. It adds workflow,
not rules: read `AGENTS.md`, `notes/learning/gotchas.md`,
`notes/learning/voice-overflows.md` and the target track header before acting.

## Establish the state

1. Identify the current track and section from the session. If ambiguous, ask.
2. Read the incoming and outgoing seat maps from their headers; `dN` numbers
   follow first entry, not musical importance.
3. A stream is not silent just because its track ended. Check its fades and,
   when needed, the live state with `list` or `cycleD <secs>`.

## Choosing what comes next

- Prefer a gentle handover: compatible tempo, nearby key or mode, and a density
  you can hold at a landing. Offer contrast only when asked.
- Name the concrete handover line and why it fits. Do not bake it into a file
  unless asked.
- A double blank is a landing: the texture can hold there before the next
  change.

## Landings and voice overflows

- `overflow = seats(outgoing) \ seats(incoming)`. Include every rewritten ID:
  `dN`, `multi`, `xfadeIn`, `clutchIn`, `clear` and `fadeSilence` targets.
- Prefer a selective `fadeSilence` or `multi xfadeIn` over `clearAll`.
  `clearAll` guarantees a clean slate but throws away the outgoing tail and is
  not the default handover.
- `-- from N` belongs only on an in-track tempo change whose predecessor is
  fixed by the arrangement. A landing glide onto a track stays unannotated.

## Editing while live

- The user's ears decide mix, noise and commit readiness. Offer A/B lines and
  wait for the verdict; do not bake them in unprompted.
- Preserve existing uncommitted edits. Keep old versions as commented A/B only
  when asked.
- Use `clutchIn` for entries and `xfadeIn`/`fadeMulti` for fades. `amp` is linear
  level, `gain` is only a trim; `level a p` clears the trim when one constant
  must mean the same on every voice. Keep `size <= 0.9`.
- Keep patterns inline at their section; name a pattern in the setup `let` only
  when another section reuses it. Follow the track's convention for inline seat
  names in `multi` blocks.
- Keep section comments short. Annotate in-track tempo changes with one trailing
  `-- from N`; do not annotate landing glides.
- Commit only on an explicit request.

## Verify

- Run `scripts/check-tidal.sh <file>` after edits and report the result.
- Do not commit, `hush`, restart the REPL or clear streams without being asked.
