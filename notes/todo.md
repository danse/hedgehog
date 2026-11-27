# TODO

Remove when done

- **`tracks/dance/`: the remaining traditions** — written: `atrium` (house, 124 BPM), `mezzanine` (UK garage, 130 BPM). Still to write, one track at a time: breakbeat / rave (~140 BPM), trance / progressive (~134). Same long-form shape (10-12 sections, ~9 min) and the same seat discipline (`dN` = kick, hats, bass, pad, clap, stabs, open hat, rim, lead, vocal/air).
- **Hydra: minute-scale (long-horizon) audio smoothing/state** — `a.fft` bins are short-time *frequency* bands (low bin = bass), not minute-long events. For visuals that evolve over tens of seconds/minutes, add explicit time-domain smoothing/integration in JS (e.g. very slow EMA/accumulator of band energy, larger windows than current `Smooth`/loop usage) and expose it to sketches. Consider configurable time constants per sketch/movement.
- **Emacs/Tidal sender: factor into a reusable component** — `hedgehog-send-region`/eval helpers in `emacs/init.el` are growing into a small heuristic statement splitter for Tidal/GHCi (`let` blocks, indented continuations, adjacent `dN` actions, `:{ :}` handling). Extract to `emacs/lisp/` (or integrate into the project’s `tidal.el`) as a focused module with clear semantics; avoid a full Haskell parser. Consider whether improvements belong upstream in `tidal.el`.
- **`swing16` mangles off-grid onsets** — `swingBy (1/5) n` shifts by a fixed fraction of the slice, so it only works on 8th/16th grids: a note just before the half-slice (slice position 0.3–0.5) fires twice, one just before the slice end (0.8–1) is dropped (`hh*20` keeps 19 of 20 onsets; triplets gain a hit). On-grid material is fine — the extra events are non-onset continuations that never sound, but they would pollute event highlighting. No track swings off-grid material today; if one does, use a position-aware shift rather than `swingBy` (not `delay`/`delaytime`, which are the echo effect).
- **Lore in session guides** — a guide can say whether the set carried a story,
  contrasting with `ladder`'s plain goal; ordinary guides need no special mark.
- **Emacs tags** — `stitch` and other `let`-local pattern names are not in TAGS;
  evaluate the setup paragraph, or find a tags/LSP setup that indexes locals.
  Check `visit-tags-table`/`tags-table-list` after the ontology move too.
- **Replace deprecated `dam.py` with upstream `dam-query`** — the validated
  queries now exist in `../dam` on the `agents` branch as `dam-query`
  (`--tags`, `--key`, tag intersection, advisory `--check`). The local script
  is kept only for historical interest: it records the interface that shaped
  the decks, but assumes the old `tracks/...tidal` paths. Don't extend it. Once
  `dam-query` is merged or installed, remove the local reader and update the
  skill/toolbox references; decks stay hand-edited meanwhile.
- **`dam-query` can't intersect tags across schemes** — `TAG [TAG...]` only
  matches labels in one deck's filename, so `key:E groove` over `dimensions/` +
  `spines/` finds nothing. Cross-scheme browsing needs `--key NAME`, or a new
  query mode that joins rows by key across decks. Note the limitation in
  `notes/ontology/README.md` until then.
- enable tidal event highlighting?
