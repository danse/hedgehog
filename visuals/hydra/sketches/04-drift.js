// 4 - Drift (10:00-13:00) | stripped back
// Foggy, desaturated, slow rotation
export const name = 'drift';
export default function run({ Motion }){
  const mb = Motion?.budget ?? 0.6;
  noise(4, 0.008)
    .rotate(0, 0.0008)
    .modulate(osc(6, 0.008), () => Math.max(0.001, (a.fft[0]||0)*0.02)*mb)
    .color(0.48, 0.58, 0.88)
    .brightness(0.25)
    .saturate(1.0)
    .out(o0);
  /*
  src(o0)
    .scale(1.008)
    .rotate(0.0006)
    //.modulate(noise(2, 0.01), () => Math.max(0.0005, (a.fft[1]||0)*0.01)*mb)
    //.blend(o0, 0.02)
    .out(o1);
  */
  render(o0);
}
