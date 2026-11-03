// 3 - Bloom (6:00-10:00) | +d6,d7
// Gentle folds/morphs, warmer hues creep in
export const name = 'bloom';
export default function run({ Motion }){
  const mb = (Motion && Motion.budget) ? Motion.budget : 0.6;
  voronoi(5, 0.015)
    .rotate(() => time*0.0008)
    .modulate(osc(8, 0.01), () => (a.fft[1]||0)*0.0015*mb)
    .kaleid(3)
    .color(() => 0.5 + (a.fft[0]||0)*0.00001, 0.6, 0.9)
    .brightness(-0.08)
    .saturate(1.1)
    .out(o0);
  src(o0)
    .scale(1.012)
    .rotate(0.0015)
    .modulate(noise(3, 0.01), () => (a.fft[2]||0)*0.0008*mb)
    .blend(o0, 0.035)
    .hue(() => (a.fft[1]||0)*0.000015)
    .out(o1);
  render(o1);
}
