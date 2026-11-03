// Optional OSC bridge (disabled by default)
// To enable later: set window.HYDRA_OSC = true and point to your bridge
export function initOsc() {
  if (!window.HYDRA_OSC) return null;
  // Placeholder - implement with osc-js/websocket bridge when needed
  console.log('[hydra] OSC disabled (set window.HYDRA_OSC to enable)');
  return null;
}
