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
- Static feedback: `agents/toolbox/track-levels.py track|compare` needs no GHCi,
  OSC or audio server. The live sender groups statements and GHC parses them
  into AST facts; Python keeps the RMS/cycle model: cached WAV RMS or nominal
  `1.0` for synths, `amp × gain^4 × source`, density, fades and capped tail,
  per-stream max then sum. It is coarse triage, not a loudness meter. Fix the
  hottest streams by intra-track equalisation; leave dense textures alone.
- Spines are flat browsing labels, not a taxonomy: 1–3 tags per track, no
  primary label. Canonical copy is `notes/spines/` dam decks; browse/query with
  `agents/toolbox/spines.py`; never duplicate labels into headers. `score` is
  written here, `transcription` is an outside source.
- Dam stores/transforms plain text in-repo; it lacks query/reverse/check.
  `tag` has filters/graph tools but uses cwd-relative hardlinks, so use it only
  as a local export from the decks.
- Knowledge placement: stable workflow in skills, session plans and unvetted
  preferences in `notes/`; headers stay track-specific and point to
  `notes/learning/gotchas.md`. Prefer one canonical source plus a thin viewer.
- Public repo: commit only on explicit request; keep drafts unvetted and
  untracked until listened to; preserve score credits and user edits.
- Verify: `spines.py --check` for labels and `scripts/check-tidal.sh <file>` for
  edited sources; report results.
