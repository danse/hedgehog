---
name: Hedgehog develop
description: Guide Hedgehog development mode: every block counts, static feedback, spine browsing and public-repo care.
---

# Development protocol

Use for track/tool/doc edits and set audits. This is **development mode**, not
the live-session interface: do not wait for landings during listening — every
block counts. Read `AGENTS.md`, gotchas and the target header.

- Priorities: live-coder readability and feedback now; fast scripted iteration;
  the repo as a public product; the user's ears decide final mix/noise/commit.
- Live handover discipline carries into development edits and audits: fade
  leftover seats with `fadeSilence`/`multi xfadeIn` before the next intro,
  avoid `clearAll` and `clutchIn ... silence`, and don't thin event density to
  smooth a join. The generalized `-- from ...` fallback lives in `AGENTS.md`;
  don't duplicate it here.
- Static feedback: `agents/toolbox/track-levels.py track|compare` needs no GHCi,
  OSC or audio server. The live sender groups statements and GHC parses them
  into AST facts; Python keeps the RMS/cycle model: cached WAV RMS or nominal
  `1.0` for synths, `amp × gain^4 × source`, density, fades and capped tail,
  per-stream max then sum. It is coarse triage, not a loudness meter. Fix the
  hottest streams by intra-track equalisation; leave dense textures alone.
- Under `notes/ontology/`: spines are live-coding affordances and dimensions
  are parametric root tags (`key:A`; modulating tracks carry each root).
  These are lightweight ontologies, not taxonomies: tags overlap, none is
  primary, meanings stay stable. Headers own exact tempo/key/seats.
  Browse tag decks with upstream `dam-query`; the local `agents/toolbox/dam.py`
  is deprecated and kept for historical interest. Pass `notes/ontology/spines`
  or `notes/ontology/dimensions` directly; never duplicate labels into headers.
  `score` is written here, `transcription` is an outside source.
- Keep `spines/` and `dimensions/` deck-only: a `README.md` inside one parses
  as a card. Vocabulary and writing clues live in `notes/ontology/README.md`.
- Track files are `snake_case` (`baroque_carnival.tidal`); ontology cards use
  the bare stem. Genre folders and BPM stay out of tag decks.
- Set guides are ordered narratives (`notes/sets/`): `ladder` is listener-facing;
  a `lechuga` is a repeatable work session (explorative, no audience yet,
  allowed heavy/lengthy, ending in a live-built flower named per session).
  They are not tag decks; a landing is a double-blank hold point in a track.
  Do not label landings with `-- Landing:` comments — the double blank is the
  only marker, so paragraph jumps stay clean in Emacs.
- In a setup `let`, join the logical parts with bare `--` lines, not blank
  lines: the whole block stays one sender group and one eval. Double blanks
  between sections still mark landings.
- Dam stores/transforms plain text in-repo. Upstream `main` lacks query/check;
  the `agents` branch adds `dam-query` (advisory checks), but reverse is still
  absent. `tag` has filters/graph tools but uses cwd-relative hardlinks, so use
  it only as a local export from the decks.
- Knowledge placement: stable workflow in skills, session plans and unvetted
  preferences in `notes/`; headers stay track-specific and point to
  `notes/learning/gotchas.md`. Prefer one canonical source plus a thin viewer.
- Matrix API: interface in `notes/matrix-api.tidal`, implementation in
  `boot/matrix.hs`. Voice calls return patterns; transitions stay at the call
  site.
- Outside ideas: the `contributors` skill indexes outside Tidal tune clones in
  `..`; credit anything actually borrowed in the track header.
- Public repo: commit only on explicit request; keep drafts unvetted and
  untracked until listened to; preserve score credits and user edits.
- Verify: `dam-query --check` (advisory) for labels and
  `scripts/check-tidal.sh <file>` for edited sources; report results.
