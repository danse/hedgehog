// 9 - Basic Pulse
// Simple circle pulsing with bass
export const name = 'pulse-basic';
export default function run({ Motion }){
  const mb = (Motion && Motion.budget) ? Motion.budget : 0.6;
  shape(100)
    .scale(() => 0.3 + (a.fft[0]||0)*0.02*mb)
    .color(1, 0.3, 0.6)
    .out(o0);
  src(o0)
    .rotate(() => (a.fft[0]||0)*0.0001)
    .out(o1);
  render(o1);
}
