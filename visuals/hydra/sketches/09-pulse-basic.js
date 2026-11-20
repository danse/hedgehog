// 9 - Basic Pulse

export const name = 'pulse-basic';
export default function run({ Motion }){
  const mb = (Motion && Motion.budget) ? Motion.budget : 0.6;
  osc(60, () => a.fft[1]*0.01, 0)
    //.scale(() => 1 + (a.fft[0]||0)*0.05*mb)
    .color(() => (a.fft[0]||0)*0.01, () => (a.fft[2]||0)*0.01, 1)
    //.rotate(() => time*0.1)
    .out(o0);
  /*
  src(o0)
    .scrollX(() => (a.fft[1]||0)*0.0001)
    .scrollY(() => (a.fft[3]||0)*0.0001)
    .out(o1);
  */
  render(o0);
  /*
    the original simple shape
  shape(100)
    .scale(() => 0.3 + (a.fft[0]||0)*0.02*mb)
    .color(1, 0.3, 0.6)
    .out(o0);
  src(o0)
    .rotate(() => (a.fft[0]||0)*0.0001)
    .out(o1);
    render(o1);
  */
}
