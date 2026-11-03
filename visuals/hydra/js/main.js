import { Smooth, Motion } from './utils.js';
import { initOsc } from './osc.js';

const canvas = document.getElementById('hydra-canvas');
const hudSketch = document.getElementById('hud-sketch');
const hudAudio = document.getElementById('hud-audio');
const hud = document.getElementById('hud');
const debugEl = document.getElementById('debug');

let hydra = null;
let currentSketch = 1;
let smooth = Object.create(Smooth);
smooth.init(96); // heavy smoothing
initOsc();

// Boot Hydra
function boot() {
  hydra = new Hydra({
    canvas: canvas,
    detectAudio: true,
    enableStreamCapture: false,
    width: window.innerWidth,
    height: window.innerHeight
  });
  // Try to prefer virtual mic if present later via getUserMedia
  setupAudio();
  loadSketch(currentSketch);
  bindKeys();
  loop();
}

async function setupAudio() {
  try {
    // Enumerate devices and prefer Hydra-Virtual-Mic if available
    const devices = await navigator.mediaDevices.enumerateDevices();
    const mics = devices.filter(d => d.kind === 'audioinput');
    const virt = mics.find(d => /hydra.*virt|virtual.*mic/i.test(d.label));
    if (virt) {
      console.log('[hydra] Found virtual mic:', virt.label);
      hudAudio.textContent = 'audio: Hydra-Virtual-Mic';
    } else if (mics.length > 0) {
      console.log('[hydra] Using mic:', mics[0].label);
      hudAudio.textContent = `audio: ${mics[0].label.slice(0,28)}`;
    } else {
      hudAudio.textContent = 'audio: (none)';
    }
  } catch (e) {
    console.warn('[hydra] enumerateDevices failed:', e);
    hudAudio.textContent = 'audio: err';
  }
}

async function loadSketch(n) {
  currentSketch = n;
  try {
    const mod = await import(`../sketches/0${n}.js`);
    if (typeof mod.default === 'function') {
      mod.default({ hydra, smooth, Motion });
      hudSketch.textContent = `sketch: 0${n}${mod.name ? '-' + mod.name : ''}`;
    } else if (typeof mod.run === 'function') {
      mod.run({ hydra, smooth, Motion });
      hudSketch.textContent = `sketch: 0${n}`;
    } else {
      hudSketch.textContent = `sketch: 0${n}`;
    }
    console.log(`[hydra] loaded sketch 0${n}`);
  } catch (e) {
    console.error('[hydra] failed to load sketch', n, e);
    hudSketch.textContent = `sketch: 0${n} (err)`;
  }
}

function bindKeys() {
  window.addEventListener('keydown', (e) => {
    if (e.key >= '1' && e.key <= '5') {
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
  if (hydra && hydra.setResolution) {
    hydra.setResolution(window.innerWidth, window.innerHeight);
  }
});

boot();
