// 5 - Dissolve (13:00–16:00) | d1,d2 only
// Wispy trails, slow to near-static
export const name = 'dissolve';
export default function run({ Motion }){
  const mb = (Motion && Motion.budget) ? Motion.budget : 0.6;
  osc(9, 0.006, 0.7)
    .rotate(0, 0.0004)
    .modulate(noise(3, 0.006), () => (a.fft[0]||0)*0.0004*mb)
    .color(0.42, 0.58, 0.92)
    .brightness(-0.22)
    .contrast(1.05)
    .out(o0);
  src(o0)
    .scale(1.004)
    .rotate(0.0003)
    .modulate(voronoi(2, 0.004), () => (a.fft[1]||0)*0.0003*mb)
    .blend(o0, 0.01)
    .out(o1);
  render(o1);
}
