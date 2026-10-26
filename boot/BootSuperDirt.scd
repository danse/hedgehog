// Hedgehog — headless SuperCollider + SuperDirt startup.
// Run with:  pw-jack sclang boot/BootSuperDirt.scd
// (scripts/up.sh does this for you and waits for "SuperDirt ready".)

(
s.options.numBuffers = 2048;
s.options.memSize = 8192 * 16;
s.options.numWireBufs = 128;
s.options.maxNodes = 1024 * 32;
s.options.numOutputBusChannels = 2;
s.options.numInputBusChannels = 2;
s.options.sampleRate = 48000;

s.latency = 0.35;

s.waitForBoot {
    ~dirt = SuperDirt(2, s);

    // Default Dirt-Samples from ~/.local/share/SuperCollider/downloaded-quarks
    ~dirt.loadSoundFiles;

    // Extra samples for this set (uncomment once samples/ has content):
    // ~dirt.loadSoundFiles("/home/marea/hub/hedgehog/samples/*");

    // --- project synths (core UGens only; no sc3-plugins needed) ---------
    // Warm three-oscillator drone/lead voice.
    SynthDef(\hedge_sine, { |out, freq = 220, sustain = 1, pan|
        var env = EnvGen.ar(Env.linen(0.5, sustain, 2), doneAction: 2);
        var sig = SinOsc.ar(freq)
                + SinOsc.ar(freq * 1.5, 0, 0.35)
                + SinOsc.ar(freq * 0.5, 0, 0.25);
        Out.ar(out, DirtPan.ar(sig, ~dirt.numChannels, pan, env));
    }).add;

    // Detuned pad with a sub octave.
    SynthDef(\hedge_pad, { |out, freq = 220, sustain = 1, pan|
        var env = EnvGen.ar(Env.linen(2, sustain, 4), doneAction: 2);
        var sig = (Saw.ar(freq * [0.997, 1, 1.003]).sum * 0.12)
                + (SinOsc.ar(freq * 0.5) * 0.2);
        sig = LPF.ar(sig, 900);
        Out.ar(out, DirtPan.ar(sig, ~dirt.numChannels, pan, env));
    }).add;

    // Filtered noise bed / riser.
    SynthDef(\hedge_noise, { |out, sustain = 1, pan|
        var env = EnvGen.ar(Env.linen(1, sustain, 2), doneAction: 2);
        var sig = LPF.ar(WhiteNoise.ar, 900);
        Out.ar(out, DirtPan.ar(sig, ~dirt.numChannels, pan, env));
    }).add;

    s.sync;

    // 12 stereo orbits; Tidal orbits 0..11 map onto these.
    ~dirt.start(57120, 0 ! 12);

    "SuperDirt ready on port 57120".postln;
};
)
