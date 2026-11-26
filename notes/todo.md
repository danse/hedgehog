# TODO

Remove when done

- **`tracks/dance/`: the remaining traditions** — written: `atrium` (house, 124 BPM), `mezzanine` (UK garage, 130 BPM). Still to write, one track at a time: breakbeat / rave (~140 BPM), trance / progressive (~134). Same long-form shape (10-12 sections, ~9 min) and the same seat discipline (`dN` = kick, hats, bass, pad, clap, stabs, open hat, rim, lead, vocal/air).
- **Hydra: minute-scale (long-horizon) audio smoothing/state** — `a.fft` bins are short-time *frequency* bands (low bin = bass), not minute-long events. For visuals that evolve over tens of seconds/minutes, add explicit time-domain smoothing/integration in JS (e.g. very slow EMA/accumulator of band energy, larger windows than current `Smooth`/loop usage) and expose it to sketches. Consider configurable time constants per sketch/movement.
- **Emacs/Tidal sender: factor into a reusable component** — `hedgehog-send-region`/eval helpers in `emacs/init.el` are growing into a small heuristic statement splitter for Tidal/GHCi (`let` blocks, indented continuations, adjacent `dN` actions, `:{ :}` handling). Extract to `emacs/lisp/` (or integrate into the project’s `tidal.el`) as a focused module with clear semantics; avoid a full Haskell parser. Consider whether improvements belong upstream in `tidal.el`.
- **`swing16` mangles off-grid onsets** — `swingBy (1/5) n` shifts by a fixed fraction of the slice, so it only works on 8th/16th grids: a note just before the half-slice (slice position 0.3–0.5) fires twice, one just before the slice end (0.8–1) is dropped (`hh*20` keeps 19 of 20 onsets; triplets gain a hit). On-grid material is fine — the extra events are non-onset continuations that never sound, but they would pollute event highlighting. No track swings off-grid material today; if one does, use a position-aware shift rather than `swingBy` (not `delay`/`delaytime`, which are the echo effect).
- **`hedgehog-develop` skill: carry the live handover lessons** — development
  edits and audits should keep the discipline learned live: fade leftover seats
  with `fadeSilence`/`multi xfadeIn` before the next intro, avoid `clearAll` and
  `clutchIn ... silence`, and don't thin event density to smooth a join.
  `AGENTS.md` already holds the generalized `-- from ...` fallback annotation,
  so don't duplicate that here.
- **Skill edits need `/reload` in a running session** — changes to
  `agents/skills/*/SKILL.md` are on disk, but a session started before the edit
  can keep the old body until `/reload`. Remember too that `skills` paths
  resolve from the active working directory: the parent live session must start
  at the repo root to see `./agents/skills` at all. When a skill changes, a
  conversational pointer to the change is enough — let the agent load and read
  the skill itself rather than pasting the diff into the prompt.
- **Lore in session guides** — a guide can say whether the set carried a story,
  contrasting with `ladder`'s plain goal; ordinary guides need no special mark.
- **Blog material for this week** — the spine/dimension/session exchange and the
  A/B fallback convention could make a short post on live coding and software
  engineering.
- **`Variants` score names don't scale** — the `loden` record selectors give
  clean live calls but create a second vocabulary per track. Prefer local pattern
  functions and composition; revisit only if a shared naming layer emerges.
- **Emacs tags** — `stitch` and other `let`-local pattern names are not in TAGS;
  evaluate the setup paragraph, or find a tags/LSP setup that indexes locals.
  Check `visit-tags-table`/`tags-table-list` after the ontology move too.
- **`cycleD` should be Ctrl-C-cancellable** — make it interruptible from Emacs
  so a live coder can abort it without restarting the REPL.
- **`spines.py` for all tag schemes** — it still hardcodes
  `ontology/spines/` and that README's vocabulary. Generalise it to browse
  `spines/` and `dimensions/` (e.g. a `--scheme` flag, with a shared or
  per-scheme vocabulary), so one offline tool covers both tag decks.
- enable tidal event highlighting?
