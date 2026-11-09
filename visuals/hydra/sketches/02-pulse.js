// 2 - Slow pulse (3:00-6:00) | +d5
// Barely visible pulses, mid-low driven
export const name = 'pulse';
export default function run({ Motion }){
  const mb = Motion?.budget ?? 0.9;
  //voronoi(() => 5+a.fft[1], 0.2) // scale
  //voronoi(6, () => a.fft[1]*0.005) // speed
  voronoi(6, 0.2, () => 0.1 + a.fft[1]) // blending
    //.rotate(() => time*0.002)
    //.modulate(osc(10, 0.15), () => (a.fft[1]||0)*0.03*mb)
    .color(() => 0.45 + a.fft[0]*0.2, 0.65, 0.95)
    .brightness(a.fft[2])
    .contrast(1.5)
    .out(o0);
  /*
  src(o0)
    .scale(() => 1.012 + (a.fft[0]||0)*0.00005)
    .rotate(0.002)
    .modulate(noise(3, 0.012), () => Math.max(0.001, (a.fft[2]||0)*0.02)*mb)
    .blend(o0, 0.04)
    .out(o1);
   */
  render(o0);
}
