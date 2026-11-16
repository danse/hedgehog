# TODO

Remove when done

- **`tracks/dance/`: the other three traditions** — `atrium` covers house. Still to write, one track at a time: breakbeat / rave (~140 BPM), UK garage / 2-step (~130), trance / progressive (~134). Same long-form shape (10-12 sections, ~9 min) and the same seat discipline as `atrium` (`dN` = kick, hats, bass, pad, clap, stabs, open hat, rim, lead, vocal/air).
- **Hydra: minute-scale (long-horizon) audio smoothing/state** — `a.fft` bins are short-time *frequency* bands (low bin = bass), not minute-long events. For visuals that evolve over tens of seconds/minutes, add explicit time-domain smoothing/integration in JS (e.g. very slow EMA/accumulator of band energy, larger windows than current `Smooth`/loop usage) and expose it to sketches. Consider configurable time constants per sketch/movement.
- **Emacs/Tidal sender: factor into a reusable component** — `hedgehog-send-region`/eval helpers in `emacs/init.el` are growing into a small heuristic statement splitter for Tidal/GHCi (`let` blocks, indented continuations, adjacent `dN` actions, `:{ :}` handling). Extract to `emacs/lisp/` (or integrate into the project’s `tidal.el`) as a focused module with clear semantics; avoid a full Haskell parser. Consider whether improvements belong upstream in `tidal.el`.
- enable tidal event highlighting?
- can i generate tag files for emacs to read on this project?
