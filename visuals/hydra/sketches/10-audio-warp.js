// 10 - Audio Warp
// The warp amount follows the bass, so low hits visibly bend the image.
// Unlike 07-oscillators, audio drives the displacement, not the phase.
export const name = 'audio-warp';
export default function run({ Motion }){
  const mb = (Motion && Motion.budget) ? Motion.budget : 0.6;
  const bass = () => a.fft[0] || 0;
  const mid  = () => a.fft[1] || 0;

  // Structured base so the displacement is easy to read.
  voronoi(6, 0.1)
    .color(() => 0.4 + bass() * 0.5, 0.6, 0.95)
    .brightness(0.45)
    .contrast(1.3)
    .out(o0);

  // Bass pushes the warp; the modulator drifts slowly so the lens moves too.
  src(o0)
    .modulate(
      osc(4, 0.08, () => mid() * 0.4),
      () => Math.min(0.2, (0.02 + bass() * 0.22) * mb)
    )
    .rotate(() => time * 0.02)
    .out(o1);

  render(o1);
}
