// 6 - Basic Shapes (beginner friendly)
// Simple shapes reacting to audio
export const name = 'basic-shapes';
export default function run({ Motion }){
  const mb = (Motion && Motion.budget) ? Motion.budget : 0.6;
  shape(4)
    .scale(() => 0.5 + (a.fft[0]||0)*0.01*mb)
    .rotate(() => time*0.01)
    .color(1, 0.5, 0.8)
    .out(o0);
  src(o0)
    .modulate(shape(3), () => (a.fft[1]||0)*0.005*mb)
    .blend(o0, 0.1)
    .out(o1);
  render(o1);
}
