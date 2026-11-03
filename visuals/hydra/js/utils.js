// Hedgehog Hydra utils - slow fluid helpers
export const Smooth = {
  init(len = 64) {
    this.buf = new Array(len).fill(0);
    this.i = 0;
    this.alpha = 0.92; // heavy smoothing
  },
  push(v) {
    if (!this.buf) this.init();
    this.buf[this.i] = v;
    this.i = (this.i + 1) % this.buf.length;
  },
  mean() {
    if (!this.buf) return 0;
    let s = 0;
    for (let j = 0; j < this.buf.length; j++) s += this.buf[j];
    return s / this.buf.length;
  },
  rms() {
    if (!this.buf) return 0;
    let s = 0;
    for (let j = 0; j < this.buf.length; j++) s += this.buf[j] * this.buf[j];
    return Math.sqrt(s / this.buf.length);
  }
};

export function clamp(x, min, max) {
  return Math.max(min, Math.min(max, x));
}

export function lerp(a,b,t){ return a + (b-a)*clamp(t,0,1); }

// Motion budget to keep things restrained on lower-end hardware
export const Motion = {
  budget: 0.6,      // global multiplier
  maxMod: 0.5,      // cap modulate strength
  maxScroll: 0.25,  // cap scroll/speed
  scale(x){ return clamp(x * this.budget, 0, this.maxMod); }
};
