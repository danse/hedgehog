# Hedgehog Visuals (Hydra)

This directory will contain a self-contained Hydra setup for live-coded, audio-reactive visuals that pair with the Hedgehog TidalCycles set.

## Philosophy
- **Audio-first**: Sync primarily to the SuperDirt monitor (same source as `scripts/record.sh`). Use `a.fft[]`/RMS for texture and motion.
- **Hybrid cues**: Mirror the 5-movement structure from `notes/set-plan.md`. Start with manual swaps (like switching Tidal patterns), add OSC triggers later if desired.
- **Slow fluid**: Restraint over flash. Prioritize breathy motion, gentle morphing fields, and low-frequency response for a D minor ambient set.
- **Non-invasive**: Visuals must not interfere with `pw-jack`/SuperCollider/JACK routing. All routing is reversible.

## Quick Plan

### Tools
- **Hydra** (browser-based, WebGL) - Live-coding feel akin to Tidal. Supports audio input and can receive OSC for scene changes.
- Fallback: Glava considered if performance is poor on the Celeron N4020 (especially with the upgrade running).

### Audio routing (PipeWire)
Hydra reads system audio via microphone input. Feed it the USB monitor without touching scsynth/JACK:

Option A (recommended): `pw-loopback`
```bash
pw-loopback \
  --capture-props='media.class=Audio/Sink node.name=hydra-virt-sink device.description=Hydra-Virtual-Sink' \
  --playback-props='media.class=Audio/Source node.name=hydra-virt-src device.description=Hydra-Virtual-Mic'
```
In browser mic selection choose `Hydra-Virtual-Mic`.

Option B: `pactl` module-null-sink + module-loopback routing `alsa_output.usb-GeneralPlus_USB_Audio_Device-00.analog-stereo.monitor` to it.

Scripts will live in `scripts/` (see below). Kill loopbacks to revert instantly.

### Project layout
```text
visuals/
├── hydra/
│   ├── index.html
│   ├── css/style.css
│   ├── js/
│   │   ├── main.js
│   │   ├── osc.js      # optional (hybrid OSC later)
│   │   └── utils.js
│   └── sketches/
│       ├── 00-base.js
│       ├── 01-emergence.js
│       ├── 02-pulse.js
│       ├── 03-bloom.js
│       ├── 04-drift.js
│       └── 05-dissolve.js
└── README.md
```

### Scripts (to be added)
```text
scripts/
├── vis-audio-route.sh  # start/stop/status for loopback
├── vis-hydra-up.sh     # start local server + open browser
└── vis-hydra-swap.sh   # swap sketches to match cues (1-5)
```

### Movement cues (mirror set-plan.md)
| # | Movement | Sketch | Notes |
|---|----------|---------|-------|
| 1 | Emergence (0:00–3:00) | `01-emergence.js` | d1,d2 only. Very subtle, low-frequency driven. |
| 2 | Slow pulse (3:00–6:00) | `02-pulse.js` | +d5. Barely visible pulses, keep scaling low. |
| 3 | Bloom (6:00–10:00) | `03-bloom.js` | +d6,d7. Gentle folds/morphs, warmer hues creep in. |
| 4 | Drift (10:00–13:00) | `04-drift.js` | stripped back. Foggy, desaturated. |
| 5 | Dissolve (13:00–16:00) | `05-dissolve.js` | d1,d2 only. Wispy trails, slow to near-static, pairs with tail. |

Manual swap first (script or hotkeys 1-5). OSC bridge optional later for automatic triggers.

### Tuning guidelines
- Heavy FFT smoothing / lerping to avoid jitter
- Motion budget: cap modulate strength; prefer slow rotation/feedback
- Keep RMS-based scaling conservative
- Test on Celeron N4020 with upgrade running; lower resolution/FPS if needed
- Avoid many stacked `out()` feedback chains

### Getting started (when implemented)
1. `./scripts/vis-audio-route.sh start` (create virtual mic)
2. `./scripts/vis-hydra-up.sh` (serve + open browser)
3. In browser select `Hydra-Virtual-Mic`, allow access
4. Play set, swap with `./scripts/vis-hydra-swap.sh <num>` or hotkeys 1-5

## References
- Hydra: https://hydra.ojack.xyz/
- TidalCycles: https://tidalcycles.org/
- Set plan: `../notes/set-plan.md`
