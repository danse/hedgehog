# Hedgehog — agent notes

Usage, layout and the live-coding workflow are in `README.md`; this file only
records things that are not obvious from the repository itself.

## Local upstream checkouts

When checking how Tidal or Hydra behaves, read the local checkouts before
searching the web or Hackage:

- Tidal: `/home/marea/hub/tidal` — monorepo (`tidal-core`, `tidal-parse`, …).
- Hydra: `/home/marea/hub/hydra` — `hydra-synth` checkout.

Treat both as read-only references unless the task is explicitly about changing
Tidal or Hydra. The installed Tidal used by the tracks is 1.10.3; the checkout
may be newer, so confirm version-specific behaviour in its source.

`visuals/hydra/` is this project's own Hydra page and sketches, not the Hydra
library checkout.

## Writing a track

- `dN` numbers follow the order streams first enter: `d1` is the opening sound,
  and each new layer takes the next free number. Keep that order when adding
  sections.
- Keep a pattern inline at its section if it is used only once; name it in the
  setup `let` block only when another section reuses it. A bare audition track
  may have no `let` block at all.
- Shared gotchas (`size <= 0.9`, `amp` vs `gain`, `s`/`f`, `#` order) live in
  `notes/learning/gotchas.md`. Track headers carry only track-specific notes
  and a pointer to that file; don't repeat the shared rules in each header.
- A double blank line between paragraphs marks a **landing**: the texture is
  complete there and can hold on its own. The live coder can dwell on it and
  listen, or detach from the track there — e.g. to mix another intro in. A
  single blank line stays an ordinary paragraph separator and carries no such
  hint. `tenfold.tidal` has one after the drone and low pad enter; the trailing
  one in `grin.tidal` is a detach point as the pad holds Em9.
