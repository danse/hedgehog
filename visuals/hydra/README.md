# Hydra (self-hosted)

This folder contains the local Hydra setup for the Hedgehog set.

## Files
- `index.html` - Loads Hydra synth and boots our app
- `css/style.css` - Fullscreen, minimal UI
- `js/main.js` - Boot, audio input selection, sketch loader, hotkeys (1-5)
- `js/utils.js` - Helpers for slow-fluid motion (smoothing, lerp, motion budget)
- `js/osc.js` - Optional OSC receiver for hybrid cues (off by default)
- `sketches/` - Movement sketches mirroring `notes/set-plan.md`

## Audio input
Hydra uses `getUserMedia`. Use `scripts/vis-audio-route.sh` to create `Hydra-Virtual-Mic` from the USB monitor. Select it in the browser dropdown.

## Usage
1. Route audio: `../../scripts/vis-audio-route.sh start`
2. Serve: `../../scripts/vis-hydra-up.sh` (starts local server, opens browser)
3. Select `Hydra-Virtual-Mic` in the page
4. Swap sketches with keys `1-5` or `../../scripts/vis-hydra-swap.sh <n>`

## Notes
- Keep motion restrained. Default smoothing should be high.
- Test performance on target hardware (Celeron N4020). Reduce feedback/modulate if stuttering.
- OSC is disabled by default; enable only if desired for automatic cues.
