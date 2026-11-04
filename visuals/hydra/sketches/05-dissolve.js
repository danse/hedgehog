// 5 - Dissolve (13:00-16:00) | d1,d2 only
// Wispy trails, slow to near-static
export const name = 'dissolve';
export default function run({ Motion }){
  const mb = (Motion && Motion.budget) ? Motion.budget : 0.6;
  voronoi(3, 0.01)
    .rotate(() => time*0.0006)
    .modulate(osc(7, 0.008), () => Math.max(0.001, (a.fft[0]||0)*0.015)*mb)
    .kaleid(2)
    .color(() => 0.42 + (a.fft[0]||0)*0.0001, 0.58, 0.92)
    .brightness(0.3)
    .contrast(1.2)
    .out(o0);
  src(o0)
    .scale(() => 1.006 + (a.fft[1]||0)*0.00002)
    .rotate(0.0006)
    .modulate(noise(2, 0.008), () => Math.max(0.0005, (a.fft[2]||0)*0.01)*mb)
    .blend(o0, 0.025)
    .out(o1);
  render(o1);
}
