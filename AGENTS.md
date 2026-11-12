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
