import { Smooth, Motion } from './utils.js';
import { initOsc } from './osc.js';

const canvas = document.getElementById('hydra-canvas');
const hudSketch = document.getElementById('hud-sketch');
const hudAudio = document.getElementById('hud-audio');
const hud = document.getElementById('hud');
const debugEl = document.getElementById('debug');

let hydra = null;
let smooth = Object.create(Smooth);
smooth.init(96); // heavy smoothing
initOsc();

function setHydraResolution() {
  if (!hydra || !hydra.setResolution) return;
  const dpr = Math.min(window.devicePixelRatio || 1, 2);
  const w = Math.max(1, Math.floor((canvas.clientWidth || window.innerWidth) * dpr));
  const h = Math.max(1, Math.floor((canvas.clientHeight || window.innerHeight) * dpr));
  hydra.setResolution(w, h);
}

// Browsers remember a per-site microphone choice, which survives reboots and can
// silently point Hydra at the physical USB mic (often silent). Hydra always asks
// for `audio: true` with no device, so we probe for the virtual mic first and
// rewrite Hydra's request to use it whenever it exists.
async function preferVirtualMic() {
  const md = navigator.mediaDevices;
  if (!md || !md.getUserMedia || !md.enumerateDevices) return;
  const orig = md.getUserMedia.bind(md);
  let virtId = null;
  try {
    // Labels are only visible after permission has been granted.
    const probe = await orig({ audio: true });
    probe.getTracks().forEach((t) => t.stop());
    await new Promise((r) => setTimeout(r, 80)); // let the device release
    const devices = await md.enumerateDevices();
    const mics = devices.filter((d) => d.kind === 'audioinput');
    console.log('[hydra] inputs:', mics.map((m) => ({ label: m.label, id: m.deviceId })));
    const virt = mics.find((m) => /hydra|loopback|virt|pw-loopback/i.test(m.label));
    if (virt) virtId = virt.deviceId;
    else console.warn('[hydra] no Hydra-Virtual-Mic found; using browser default');
  } catch (e) {
    console.warn('[hydra] audio probe failed:', e);
    return;
  }
  if (!virtId) return;
  md.getUserMedia = (constraints = {}) => {
    if (constraints && constraints.audio && !constraints.video) {
      const a = typeof constraints.audio === 'object' ? constraints.audio : {};
      if (!a.deviceId) {
        constraints = { ...constraints, audio: { ...a, deviceId: { exact: virtId } } };
      }
    }
    return orig(constraints);
  };
  console.log('[hydra] forcing Hydra audio input to Hydra-Virtual-Mic');
}

// Boot Hydra
async function boot() {
  await preferVirtualMic();
  hydra = new Hydra({
    canvas: canvas,
    detectAudio: true,
    enableStreamCapture: false,
    width: window.innerWidth,
    height: window.innerHeight
  });
  // Sync backing resolution after layout (avoids first-load blur)
  requestAnimationFrame(() => {
    setHydraResolution();
    requestAnimationFrame(setHydraResolution);
  });
  // Hydra requests the default mic in its constructor (detectAudio). Report the
  // device it actually got and warn if the analyser stays silent.
  reportAudio();
  watchAudio();
  loadSketch(await initialSketch());
  bindKeys();
  loop();
}

function audioTrack() {
  const aud = hydra && hydra.synth && hydra.synth.a;
  return (aud && aud.stream) ? aud.stream.getAudioTracks()[0] : null;
}

function audioLabel() {
  const t = audioTrack();
  return t ? (t.label || 'input') : '';
}

// Hydra creates its own analyser, so we cannot force a device here. We can
// however report which input it picked and whether a signal is arriving.
function reportAudio() {
  let tries = 0;
  const timer = setInterval(() => {
    const t = audioTrack();
    if (t) {
      clearInterval(timer);
      const s = t.getSettings ? t.getSettings() : {};
      console.log('[hydra] audio input:', t.label, s);
      hudAudio.textContent = `audio: ${(t.label || 'input').slice(0, 26)}`;
      if (!/hydra|loopback|virt|pw-loopback/i.test(t.label || '')) {
        console.warn('[hydra] not using Hydra-Virtual-Mic; select it in browser mic settings');
      }
      return;
    }
    if (++tries > 40) {
      clearInterval(timer);
      hudAudio.textContent = 'audio: no input (permission/routing?)';
    }
  }, 100);
}

function watchAudio() {
  let live = 0;
  let silent = 0;
  setInterval(() => {
    const aud = hydra && hydra.synth && hydra.synth.a;
    if (!aud || !aud.fft) return;
    const peak = Math.max(...Array.from(aud.fft).map(Number));
    if (peak > 0.001) { live += 1; silent = 0; }
    else { silent += 1; live = 0; }
    const label = audioLabel() || 'input';
    if (live > 3) {
      hudAudio.textContent = `audio: ${label.slice(0, 26)} · live`;
    } else if (silent > 40) {
      hudAudio.textContent = `audio: ${label.slice(0, 26)} · silent? (wrong mic?)`;
    }
  }, 250);
}

// Browsers may start the AudioContext suspended until a user gesture.
function resumeAudio() {
  const ctx = hydra && hydra.synth && hydra.synth.a && hydra.synth.a.context;
  if (ctx && ctx.state === 'suspended') ctx.resume().catch(() => {});
}
window.addEventListener('pointerdown', resumeAudio);
window.addEventListener('keydown', resumeAudio);

// Which cue is showing. The page keeps it in localStorage so a reload (or a
// restored tab) comes back to the same sketch. `?sketch=N` overrides it, which
// makes a bookmark or a link to one cue work; `current.txt` is only the fallback
// for a browser that has never swapped a cue.
const SKETCH_KEY = 'hedgehog.sketch';

function sketchNumber(v) {
  const n = parseInt(v, 10);
  return (n >= 1 && n <= 9) ? n : null;
}

function storedSketch() {
  try {
    return sketchNumber(localStorage.getItem(SKETCH_KEY));
  } catch (e) {
    return null; // storage can be disabled (private mode, blocked cookies)
  }
}

function rememberSketch(n) {
  try {
    localStorage.setItem(SKETCH_KEY, String(n));
  } catch (e) {}
  // Keep the address in step too: a copied URL then carries the cue, and a
  // stale `?sketch=` cannot win over a later keypress after a reload.
  try {
    const url = new URL(location.href);
    if (url.searchParams.get('sketch') !== String(n)) {
      url.searchParams.set('sketch', String(n));
      history.replaceState(null, '', url);
    }
  } catch (e) {} // file:// origins may refuse history changes
}

async function initialSketch() {
  const fromUrl = sketchNumber(new URLSearchParams(location.search).get('sketch'));
  if (fromUrl) return fromUrl;
  const stored = storedSketch();
  if (stored) return stored;
  try {
    const res = await fetch('./sketches/current.txt', { cache: 'no-store' });
    if (res.ok) {
      const n = sketchNumber((await res.text()).trim());
      if (n) return n;
    }
  } catch (e) {}
  return 1;
}

async function loadSketch(n) {
  rememberSketch(n);
  const base = `0${n}`;
  const file = `${base}.js`;
  try {
    const mod = await import(`../sketches/${file}?t=${Date.now()}`);
    if (typeof mod.default === 'function') {
      mod.default({ hydra, smooth, Motion });
      hudSketch.textContent = `sketch: ${base}${mod.name ? '-' + mod.name : ''}`;
    } else if (typeof mod.run === 'function') {
      mod.run({ hydra, smooth, Motion });
      hudSketch.textContent = `sketch: ${base}`;
    } else {
      hudSketch.textContent = `sketch: ${base}`;
    }
    console.log(`[hydra] loaded sketch ${file}`);
  } catch (e) {
    console.error('[hydra] failed to load sketch', file, e);
    hudSketch.textContent = `sketch: ${base} (err)`;
  }
}

function bindKeys() {
  window.addEventListener('keydown', (e) => {
    if (e.key >= '1' && e.key <= '9') {
      loadSketch(parseInt(e.key));
      return;
    }
    if (e.key === 'h') {
      hud.classList.toggle('hidden');
      return;
    }
    if (e.key === 'd') {
      debugEl.hidden = !debugEl.hidden;
      debugEl.classList.toggle('hidden');
      return;
    }
    if (e.key === 'f') {
      if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen().catch(()=>{});
      } else {
        document.exitFullscreen().catch(()=>{});
      }
    }
  });
}

function loop() {
  requestAnimationFrame(loop);
  try {
    if (typeof a !== 'undefined' && a.fft) {
      // push a few bands
      smooth.push((a.fft[0]+a.fft[1]+a.fft[2])/3 * 0.01);
      if (!debugEl.hidden) {
        const m = smooth.mean().toFixed(4);
        const r = smooth.rms().toFixed(4);
        debugEl.textContent = `fft0:${(a.fft[0]||0).toFixed(3)} fft1:${(a.fft[1]||0).toFixed(3)} fft2:${(a.fft[2]||0).toFixed(3)}\nmean:${m} rms:${r} motion:${Motion.budget}`;
      }
    }
  } catch(e) {}
}

window.addEventListener('resize', () => {
  setHydraResolution();
});

if (document.readyState === 'complete') {
  requestAnimationFrame(boot);
} else {
  window.addEventListener('load', () => requestAnimationFrame(boot), { once: true });
}
