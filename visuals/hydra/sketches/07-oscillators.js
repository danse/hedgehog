// 7 - Oscillators (beginner friendly)
// Using osc() with audio modulation
export const name = 'oscillators';
export default function run({ Motion }){
  const mb = (Motion && Motion.budget) ? Motion.budget : 0.6;
  osc(10, 0.1, () => 0.5 + (a.fft[0]||0)*0.01*mb)
    .rotate(() => time*0.05)
    .kaleid(4)
    .color(0.2, 0.8, 1.0)
    .out(o0);
  src(o0)
    .modulate(osc(5), 0.1)
    .out(o1);
  render(o1);
}
