// 1 - Emergence (0:00-3:00) | d1,d2 only
// Very subtle, low-frequency driven, cool tones
export const name = 'emergence';
export default function run({ Motion }){
  const mb = (Motion && Motion.budget) ? Motion.budget : 0.6;
  voronoi(4, 0.015)
    .rotate(() => time*0.001)
    .modulate(osc(8, 0.01), () => Math.max(0.002, (a.fft[0]||0)*0.025)*mb)
    .kaleid(3)
    .color(() => 0.4 + (a.fft[0]||0)*0.0002, 0.6, 1.0)
    .brightness(0.35)
    .contrast(1.4)
    .out(o0);
  src(o0)
    .scale(() => 1.01 + (a.fft[1]||0)*0.00002)
    .rotate(0.001)
    .modulate(noise(3, 0.012), () => Math.max(0.001, (a.fft[2]||0)*0.015)*mb)
    .blend(o0, 0.03)
    .out(o1);
  render(o1);
}
