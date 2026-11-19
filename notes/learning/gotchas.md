# Shared track gotchas

These apply to every track. They live here instead of in each header, so a
header only needs a pointer plus anything specific to that track.

- **Reverb:** keep `size <= 0.9`. `scripts/check.sh` enforces this.
- **Level:** `amp` is linear; `gain` is `amp * gain^4`. Prefer `amp` for level
  and use `gain` only to trim an already-shaped voice.
- **Accidentals:** mini-notation uses `s`/`f` (`fs4`, `bf3`), never `#`.
- **`#` order:** put the rhythm/score operand first. `#` takes `whole`/`steps`
  from the left, so `note ... # s "..."` gives short arcs and
  `s "..." # note ...` gives bar-length ones. The full explanation is in
  [tidal.md](tidal.md).

Track headers carry only local facts — sample bases, palette, section order,
score credits — and one line pointing back here.
