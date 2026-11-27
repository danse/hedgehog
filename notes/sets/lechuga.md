# lechuga — work sessions

*Como algo que crece lento.* A **lechuga** is a set iterated for our own sake:
no audience at the moment, explorative, allowed to be heavy or lengthy. The
iterations are work rather than performance; a hard cut (`clearAll`) is
legitimate when the break itself is the material. Unlike `ladder.md`, there is
no listener-facing goal.

Each lechuga grows a **flower**: a track built live from that session's
learnings. The flower is named per session, so a new run starts fresh rather
than inheriting a previous route or name. Keep this a seed, not a chronicle.

## Dynamics

- Grow slowly. Give a texture time to say what it is before answering it.
- Colour moves, not track lists: network/colourful → dark/cold → the matrix
  question → flower. The route is chosen by ear each time.
- Level impedance lives at **entry sections**, not in whole-track level. Land at
  a landing and listen before judging the seam.
- A motif that won't let go is a handover waiting, not a problem. Let it ghost
  into the next texture instead of forcing it out.
- A harsh seam is material. Sometimes the right move is to cut the next track
  early rather than make the bridge behave.
- Surprises late in a track are worth keeping — they are what the flower
  remembers.
- Leave the last stretch for the flower; don't spend the whole hour on the arc.

## TODO

- **Equalisation gaps: quema → `baroque_carnival` → `strobe`** — the
  `clearAll 128` handover dropped hard: `track-levels.py compare` puts baroque
  at ~0.56× quema's RMS/cycle, and §1 Seed is only two quiet voices.
  Baroque → strobe is different: whole-track RMS/cycle is equal (1.254 vs
  1.253), so the impedance is at the *entry sections* (baroque's coda = ground
  + bell; strobe's §1 Doors = four filtered voices), not in track level.
  Verify both by ear in a lechuga run. A tool-side check won't help offline:
  put a one-line **level note at the very top of the header** instead — words
  first, numbers only if they earn their place: `-- level: loud (10 seats)`;
  baroque: `-- level: mid (seed = 2 voices)`; strobe:
  `-- level: mid (doors = 4 voices)`. Headers need a diet — one short line,
  not a paragraph. Record in `hedgehog-develop`.
