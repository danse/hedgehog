# Sketches

Hydra sketches for the set. Keys `1`-`9` swap, and the HUD shows the loaded
sketch name.

`js/main.js` loads `0N.js` (a symlink to the descriptive file, e.g.
`01.js -> 01-emergence.js`). `00-base.js` holds shared helpers and is not loaded
as a sketch by itself.

`current.txt` (gitignored) remembers the cue number to load on reload;
`scripts/vis-hydra-swap.sh <n>` writes it. Live swaps are the hotkeys.

## Cue sketches

These follow the five movements in [notes/set-plan.md](../../../notes/set-plan.md).

| Key | Sketch | Movement | Notes |
|---|---|---|---|
| 1 | `01-emergence.js` | Emergence (0:00–3:00) | d1,d2 only. Subtle, low-frequency driven. |
| 2 | `02-pulse.js` | Slow pulse (3:00–6:00) | +d5. Barely visible pulses, low scaling. |
| 3 | `03-bloom.js` | Bloom (6:00–10:00) | +d6,d7. Gentle folds, warmer hues. |
| 4 | `04-drift.js` | Drift (10:00–13:00) | Stripped back, foggy, desaturated. |
| 5 | `05-dissolve.js` | Dissolve (13:00–16:00) | d1,d2 only. Wispy trails, near-static tail. |

## Test sketches

| Key | Sketch | Purpose |
|---|---|---|
| 6 | `06-basic-shapes.js` | Simple shapes reacting to audio |
| 7 | `07-oscillators.js` | `osc()` modulated by audio |
| 8 | `08-spectrum.js` | Frequency bands as bars |
| 9 | `09-pulse-basic.js` | Simple circle pulsing with bass |

## Adding a sketch

Create `0N-name.js` and symlink it as `0N.js`, or edit the existing target
directly. Keep motion restrained and use `Motion.budget` for scaling.
