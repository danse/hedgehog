// 4 - Drift (10:00-13:00) | stripped back
// Foggy, desaturated, slow rotation
export const name = 'drift';
export default function run({ Motion }){
  const mb = (Motion && Motion.budget) ? Motion.budget : 0.6;
  noise(4, 0.008)
    .rotate(0, 0.0008)
    .modulate(osc(6, 0.008), () => (a.fft[0]||0)*0.0006*mb)
    .color(0.48, 0.58, 0.88)
    .brightness(-0.18)
    .saturate(0.8)
    .out(o0);
  src(o0)
    .scale(1.006)
    .rotate(0.0006)
    .blur(0.4)
    .blend(o0, 0.015)
    .out(o1);
  render(o1);
}
