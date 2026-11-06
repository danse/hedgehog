# TODO

- [ ] **Hydra: minute-scale (long-horizon) audio smoothing/state** — `a.fft` bins are short-time *frequency* bands (low bin = bass), not minute-long events. For visuals that evolve over tens of seconds/minutes, add explicit time-domain smoothing/integration in JS (e.g. very slow EMA/accumulator of band energy, larger windows than current `Smooth`/loop usage) and expose it to sketches. Consider configurable time constants per sketch/movement.
