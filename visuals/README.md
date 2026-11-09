# Hedgehog Visuals (Hydra)

This directory contains a self-contained Hydra setup for live-coded,
audio-reactive visuals that pair with the Hedgehog TidalCycles set.

## Philosophy
- **Audio-first**: Sync primarily to the SuperDirt monitor (same source as `scripts/record.sh`). Use `a.fft[]`/RMS for texture and motion.
- **Hybrid cues**: Mirror the 5-movement structure from `notes/set-plan.md`. Start with manual swaps (like switching Tidal patterns), add OSC triggers later if desired.
- **Slow fluid**: Restraint over flash. Prioritize breathy motion, gentle morphing fields, and low-frequency response for a D minor ambient set.
- **Non-invasive**: Visuals must not interfere with `pw-jack`/SuperCollider/JACK routing. All routing is reversible.

## Setup

### Tools
- **Hydra** (browser-based, WebGL) - Live-coding feel akin to Tidal. Supports audio input and can receive OSC for scene changes.
- Fallback: Glava considered if performance is poor on the Celeron N4020 (especially with the upgrade running).

### Audio routing (PipeWire)
Hydra reads system audio via microphone input. Feed it the USB monitor without touching scsynth/JACK:

Option A (recommended): `pw-loopback` + `pw-link`
```bash
./scripts/vis-audio-route.sh start
```
This creates `Hydra-Virtual-Mic`, links the **current default sink's monitor**
into the loopback (so the USB device profile can change across reboots), and
makes the virtual mic the default source. `stop` restores the previous default
source. `status` shows the current routing.

The page detects `Hydra-Virtual-Mic` at boot and forces Hydra's audio request to
use it when present, so a saved per-site mic choice cannot silently fall back to
the physical USB mic. Chromium and Firefox both work.

Option B: `pactl` module-null-sink + module-loopback routing the USB monitor to it.

Helpers live in `../scripts/` (see [../scripts/README.md](../scripts/README.md)).
Kill the loopback to revert instantly.

### Where things live

- `hydra/` — the app itself; see [hydra/README.md](hydra/README.md) for boot,
  audio input, and usage.
- `hydra/sketches/` — cue and test sketches; see
  [hydra/sketches/README.md](hydra/sketches/README.md) for the catalog.
- `../scripts/` — routing, serving, and swap helpers; see
  [../scripts/README.md](../scripts/README.md).

### Cues
Sketch catalog and movement mapping:
[hydra/sketches/README.md](hydra/sketches/README.md). Swap manually with keys
`1`-`9` or `./scripts/vis-hydra-swap.sh <n>`; OSC triggers are optional later.

### Tuning guidelines
- Heavy FFT smoothing / lerping to avoid jitter
- Motion budget: cap modulate strength; prefer slow rotation/feedback
- Keep RMS-based scaling conservative
- Test on Celeron N4020 with upgrade running; lower resolution/FPS if needed
- Avoid many stacked `out()` feedback chains

### Getting started
1. `./scripts/vis-hydra-up.sh` (creates/links the virtual mic, serves, opens browser)
2. Confirm the HUD says `Hydra-Virtual-Mic · live` (if it says `silent?`, check
   `./scripts/vis-audio-route.sh status` and reload after fixing routing)
3. Play set, swap with `./scripts/vis-hydra-swap.sh <num>` or hotkeys `1`-`9`

Debug hints: `./scripts/vis-audio-route.sh status`, `pw-link -l | grep hydra`,
and the page's `d` debug overlay (`a.fft` values). HUD `silent?` means the
analyser is receiving zeros — usually the wrong browser input or no monitor link.

## References
- Hydra: https://hydra.ojack.xyz/
- TidalCycles: https://tidalcycles.org/
- Set plan: `../notes/set-plan.md`
