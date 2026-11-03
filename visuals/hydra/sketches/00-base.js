// Base helpers for all sketches
export function base({ Motion } = {}) {
  const m = Motion || { budget: 0.6 };
  return { m };
}
export const name = 'base';
export default base;
