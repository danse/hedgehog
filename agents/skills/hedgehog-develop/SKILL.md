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
  Browse tag decks with `agents/toolbox/dam.py` (`--scheme dimensions` for
  root tags); never duplicate labels into headers. `score` is written here,
  `transcription` is an outside source.
- Session guides are ordered narratives (`notes/sessions/ladder.md`), not tag
  decks; a landing is a double-blank hold point in a track, not a session tag.
- In a setup `let`, join the logical parts with bare `--` lines, not blank
  lines: the whole block stays one sender group and one eval. Double blanks
  between sections still mark landings.
- Dam stores/transforms plain text in-repo; it lacks query/reverse/check.
  `tag` has filters/graph tools but uses cwd-relative hardlinks, so use it only
  as a local export from the decks.
- Knowledge placement: stable workflow in skills, session plans and unvetted
  preferences in `notes/`; headers stay track-specific and point to
  `notes/learning/gotchas.md`. Prefer one canonical source plus a thin viewer.
- Public repo: commit only on explicit request; keep drafts unvetted and
  untracked until listened to; preserve score credits and user edits.
- Verify: `dam.py --check` for labels and `scripts/check-tidal.sh <file>` for
  edited sources; report results.
