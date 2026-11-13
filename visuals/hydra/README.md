# Hydra (self-hosted)

This folder contains the local Hydra setup for the Hedgehog set.

## Files
- `index.html` - Loads Hydra synth and boots our app
- `css/style.css` - Fullscreen, minimal UI
- `js/main.js` - Boot, virtual-mic selection, sketch loader, hotkeys (1-9)
- `js/utils.js` - Helpers for slow-fluid motion (smoothing, lerp, motion budget)
- `js/osc.js` - Optional OSC receiver for hybrid cues (off by default)
- `sketches/` - Cue and test sketches; see [sketches/README.md](sketches/README.md)

## Audio input
`scripts/vis-audio-route.sh start` creates `Hydra-Virtual-Mic`, links the default
sink's monitor into it, and makes it the default source. `vis-hydra-up.sh` calls
this automatically, so routing survives a reboot in one command.

Browsers remember a per-site microphone choice, which can survive reboots and
point back at the physical USB mic. To make this robust, the page probes for
`Hydra-Virtual-Mic` at boot and forces Hydra's audio request to use it whenever
it exists (falling back to the browser default only if routing is down). No
manual mic selection is normally needed; both Chromium and Firefox work.

If the HUD says `silent?`, check `scripts/vis-audio-route.sh status` and that the
monitor links exist. If it shows the USB mic, routing was not running when the
page loaded — start routing and reload.

## Usage
1. Serve + route: `../../scripts/vis-hydra-up.sh` (starts server, opens browser)
2. Confirm the HUD says `Hydra-Virtual-Mic · live`
3. Swap sketches with keys `1-9` or `../../scripts/vis-hydra-swap.sh <n>`.
   The page remembers the cue in `localStorage` and mirrors it in `?sketch=N`,
   so a reload, a restored tab, or a copied URL comes back to the same sketch.
   `current.txt` is only the fallback for a browser that has no stored cue.
   Open `index.html?sketch=3` to jump straight to one.

Routing manually: `../../scripts/vis-audio-route.sh {start|status|stop}`.
`stop` also restores the previous default source.

## Notes
- Keep motion restrained. Default smoothing should be high.
- Test performance on target hardware (Celeron N4020). Reduce feedback/modulate if stuttering.
- OSC is disabled by default; enable only if desired for automatic cues.
