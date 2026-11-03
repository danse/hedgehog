// 2 - Slow pulse (3:00–6:00) | +d5
// Barely visible pulses, mid-low driven
export const name = 'pulse';
export default function run({ Motion }){
  const mb = (Motion && Motion.budget) ? Motion.budget : 0.6;
  osc(12, 0.012, 0.9)
    .rotate(0, 0.002)
    .modulate(voronoi(4, 0.01), () => (a.fft[1]||0)*0.0012*mb)
    .color(0.45, 0.65, 0.95)
    .brightness(-0.12)
    .out(o0);
  src(o0)
    .scale(() => 1.008 + (a.fft[0]||0)*0.00001*mb)
    .rotate(0.001)
    .modulate(noise(2, 0.008), () => (a.fft[2]||0)*0.0006*mb)
    .blend(o0, 0.03)
    .out(o1);
  render(o1);
}
