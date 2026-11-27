# TODO

Remove when done

- **`tracks/dance/`: the remaining traditions** — written: `atrium` (house, 124 BPM), `mezzanine` (UK garage, 130 BPM). Still to write, one track at a time: breakbeat / rave (~140 BPM), trance / progressive (~134). Same long-form shape (10-12 sections, ~9 min) and the same seat discipline (`dN` = kick, hats, bass, pad, clap, stabs, open hat, rim, lead, vocal/air).
- **Hydra: minute-scale (long-horizon) audio smoothing/state** — `a.fft` bins are short-time *frequency* bands (low bin = bass), not minute-long events. For visuals that evolve over tens of seconds/minutes, add explicit time-domain smoothing/integration in JS (e.g. very slow EMA/accumulator of band energy, larger windows than current `Smooth`/loop usage) and expose it to sketches. Consider configurable time constants per sketch/movement.
- **Emacs/Tidal sender: factor into a reusable component** — `hedgehog-send-region`/eval helpers in `emacs/init.el` are growing into a small heuristic statement splitter for Tidal/GHCi (`let` blocks, indented continuations, adjacent `dN` actions, `:{ :}` handling). Extract to `emacs/lisp/` (or integrate into the project’s `tidal.el`) as a focused module with clear semantics; avoid a full Haskell parser. Consider whether improvements belong upstream in `tidal.el`.
- **`swing16` mangles off-grid onsets** — `swingBy (1/5) n` shifts by a fixed fraction of the slice, so it only works on 8th/16th grids: a note just before the half-slice (slice position 0.3–0.5) fires twice, one just before the slice end (0.8–1) is dropped (`hh*20` keeps 19 of 20 onsets; triplets gain a hit). On-grid material is fine — the extra events are non-onset continuations that never sound, but they would pollute event highlighting. No track swings off-grid material today; if one does, use a position-aware shift rather than `swingBy` (not `delay`/`delaytime`, which are the echo effect).
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
- **`Variants` belongs to grid schemes, not general score names** — the `loden`
  `plain`/`utopia` record gives clean live calls for alternate grids, but as a
  second score vocabulary per track it doesn't scale. Prefer local pattern
  functions and composition for written lines; evaluate `Variants` on a
  selection of tracks with grid-like structures (engines and the
  like), and revisit only if a shared naming layer emerges.
- **Emacs tags** — `stitch` and other `let`-local pattern names are not in TAGS;
  evaluate the setup paragraph, or find a tags/LSP setup that indexes locals.
  Check `visit-tags-table`/`tags-table-list` after the ontology move too.
- **`C-c C-i` on `cycleD` → "C-c TAB is undefined"** — Emacs reads `C-i` as
  `TAB`, so interrupting a running `cycleD` with `C-c C-i` sends `C-c TAB`,
  which has no binding and leaves the loop going. Find a reliable interrupt
  (rebind `C-c C-i`, or a distinct key) so a live coder can abort `cycleD`
  without restarting the REPL.
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
- **Equalisation gaps: quema → `baroque_carnival` → `strobe`** — the
  `clearAll 128` handover dropped hard: `track-levels.py compare` puts baroque
  at ~0.56× quema's RMS/cycle, and §1 Seed is only two quiet voices.
  Baroque → strobe is different: whole-track RMS/cycle is equal (1.254 vs
  1.253), so the impedance is at the *entry sections* (baroque's coda = ground
  + bell; strobe's §1 Doors = four filtered voices), not in track level.
  Verify both by ear. A tool-side check won't help offline: put a one-line
  **level note at the very top of the header** instead — words first, numbers
  only if they earn their place: `-- level: loud (10 seats)`; baroque:
  `-- level: mid (seed = 2 voices)`; strobe: `-- level: mid (doors = 4 voices)`.
  Headers need a diet — one short line, not a paragraph. Record in
  `hedgehog-develop`.
- **A `contributors` skill** — not credits for scores/samples, but a curated
  index of other live coders and their Tidal repos/tracks: who works in which
  style, which `.tidal` sets are worth reading, and what we borrowed from each.
  Candidates found: `pselle/livecode` (sets/songs/curiosities),
  `cleary/livecode` (sets/study/weekly/collab), `ghalestrilo/pieces` (EPs + sets),
  `kindohm/365tidalpatterns`, `vism2889/1000tidalpatterns`,
  `shatteredaesthetic/patterncycles`, `8v01d/TidalCycles`, plus
  `tidalcycles/awesome-tidalcycles` as the index. Also **mirways** — source of
  the *latigazo eléctrico* (electric whip), the crack of overlapping fades;
  repo unconfirmed. Keep it offline-readable and credit borrowed patterns in
  track headers.
- enable tidal event highlighting?
- remove comments around landings. Many landings have a one-line comment about the landing, making paragraph jumps with emacs uncomfortable. For instance there is a landing and then `-- Landing: ...` and then a blank line. Remove the one-line comments so that landings are represented simply by the double newline. Their meaning is implicit. Add this to the dev skill
- is meridian in the ontology?
