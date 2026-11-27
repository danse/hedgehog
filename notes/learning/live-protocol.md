# Live protocol — one screen

For live coders and their assistants. Read `AGENTS.md`,
`notes/learning/gotchas.md`, `notes/learning/glossary.md`,
`notes/learning/voice-overflows.md` and the target header first.

## State
- Ask the current track/section if unsure; seats are `dN` in first-entry order.
- Streams outlive tracks: check fades or `list`; avoid `cycleD` while listening.
- A double blank in a track is a landing: hold there, or detach.

## Handover
- Match tempo/key/density at a landing; contrast only when asked.
- Overflow is `seats(out) \ seats(in)`, including rewritten IDs.
- Fade only leftovers with `fadeSilence` or `multi xfadeIn`.
- Avoid `clearAll` and `clutchIn ... silence`; don't thin density to smooth a
  join. Exception: a `lechuga` work session, where a hard cut can be the point.

## Lines
- `C-c C-c` evals the current line; `C-RET` evals the paragraph. Single-line
  eval is how staged sections arrive one layer at a time.
- Offer A/B, wait for ears; never bake live ideas into a file unasked.
- Render suggestions in fenced `haskell` blocks, one selectable line per option.
- Annotate the replaced value: `-- from <param> <value>` (tempo: `-- from N`).
- `amp` is linear level; `gain` a trim; `level a p` clears it; `size <= 0.9`.
- `lpf`/`hpf` moves are first-class: `-- from lpf 1600`.
- `dN` takes one `ControlPattern`. Compose:
  `d7 . bellVoice $ slow 4 counter`
  `d2 . (# lpf 700) . padVoice . move $ loop`
- Never write `d7 bellVoice $ ...` or `d8 air # amp 0.14`.
- `ID` has `Num` but not `Enum`: `fadeSilence 8 [1,2,3]`, not `[1..3]`.
- `multi` needs a 3-arg transition: `multi xfadeIn`, not pattern-level `multi fadeIn`.

## Ontology
- Tag schemes live under `notes/ontology/`.
- Spines = live-coding affordances; `notes/ontology/spines/`.
- Dimensions = parametric root tags (`key:A`); `notes/ontology/dimensions/`.
  A modulating track carries each root (`strobe`: `key:E` + `key:F#`).
- Set guides are ordered narratives (`notes/sets/`), not tags: `ladder` is a
  listener-facing goal; a `lechuga` is a work session — explorative, no
  audience yet, allowed heavy/lengthy, and ending in a live-built flower.
  A landing is a double-blank hold point in a track, not a session tag.
- Headers own exact tempo/key/seats; tags never duplicate them.

## Safety
- Verify with `scripts/check-tidal.sh <file>`; report.
- Don't commit, `hush`, restart the REPL or clear streams without being asked.
- Skill edits need `/reload` in a running parent session.
- On social streams, legible copyable lines and fallbacks are part of the performance.
