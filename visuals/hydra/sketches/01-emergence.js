// 1 - Emergence (0:00–3:00) | d1,d2 only
// Very subtle, low-frequency driven, cool tones
export const name = 'emergence';
export default function run({ Motion }){
  const mb = (Motion && Motion.budget) ? Motion.budget : 0.6;
  osc(10, 0.01, 0.8)
    .rotate(0, 0.001)
    .modulate(noise(3, 0.01), () => (a.fft[0]||0)*0.0008*mb)
    .kaleid(2)
    .color(0.4, 0.6, 1.0)
    .brightness(-0.15)
    .contrast(1.1)
    .out(o0);
  src(o0)
    .scale(1.01)
    .rotate(0.0005)
    .hue(() => (a.fft[1]||0)*0.00001)
    .blend(o0, 0.02)
    .out(o1);
  render(o1);
}
