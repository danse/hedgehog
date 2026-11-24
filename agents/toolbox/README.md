# Toolbox

Small helper scripts for recurring agent tasks. These are the tools that used
to live in `/tmp` and vanish on shutdown. Nothing here is part of the live set;
see [`../../scripts/`](../../scripts/) for that.

## Scripts

| Script | Purpose |
|---|---|
| `session-count.py [--grep PATTERN] [--limit N]` | Tally commits that touched each track's `.tidal` files as a proxy for sessions, sorted highest first. Multi-file tracks count once per commit. `--grep session` narrows to the terse `session` commits. |
| `fake-dirt.py` | Answer Tidal's `/dirt/handshake` on `127.0.0.1:57199` so a headless Tidal instance can tick without SuperDirt. Run it in the background (`python3 agents/toolbox/fake-dirt.py &`), then stop it with its PID. Nothing starts it automatically. |
| `synth-analyser.py NAME [--param K=V …] [--pitches 147,220,294]` / `--all` | Render a project SynthDef offline with `scsynth -N` and report its band balance through `analyse-audio.py`; `--pitches` sweeps notes and prints one verdict per pitch. Prints power and flatness above 3 kHz (hiss), plus flatness in 120-3000 Hz and the inter-harmonic floor for low-passed noise that the high-band test misses. The floor is skipped for non-harmonic sources, where it would be meaningless. Very quiet synths are normalised first. No running server needed; never touches the live set. |
| `sample-explorer.py [BANK …] [--min-len S] [--min-hold PCT] [--max-sub PCT] [--root LO-HI] [--sort FIELD]` | Search sample banks for a role, reporting properties rather than verdicts: root pitch (for `speedAt`), duration, power below 40 Hz, full-buffer hold and spectral centroid. `hold` is the median RMS of the latter half against the peak, so a sample that decays after a steady start scores low. Filter by bank name (globs allowed), sort by any column, and use `--local` to include this repo's `samples/`. Complements `synth-analyser.py`, which diagnoses one known voice instead. |
| `track-levels.py track\|compare [TRACK …] [--all] [--no-samples]` | Coarse macroscopic level/energy audit from Tidal source only — no GHCi, OSC or audio server. `track` shows per-track and per-stream rows; `compare` reuses the same core for inter-track ratios. Source level is measured RMS for referenced WAVs and nominal 1.0 for synths; `amp`, quartic `gain`, note density, `sustain`/`release` and a capped reverb tail feed one RMS/cycle figure. A static approximation, not a loudness meter. |
| `spines.py [LABEL …] [--track NAME] [--tags] [--check]` | Browse the flat spine labels stored as dam decks in `notes/spines/`: group by label, filter by one or more labels, look up a single track, or verify coverage. The decks are the single source of truth; labels are not duplicated into headers. |

`fake-dirt.py` is for inspecting pattern output when no audio server is
available — it emits no sound. The reusable audio analyser is in
[`../../scripts/analyse-audio.py`](../../scripts/analyse-audio.py);
`synth-analyser.py` drives it for SynthDefs and `sample-explorer.py` for sample
banks. The loader there handles 8/16/24/32-bit PCM, which matters because part
of the Dirt-Samples collection is 24-bit.
