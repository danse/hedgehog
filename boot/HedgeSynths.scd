// Hedgehog — project SynthDefs.
// Loaded by BootSuperDirt.scd once ~dirt exists; core UGens only.

(
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

    // Gentle vibratoed hum: a soft sine with just a whisper of noise.
    SynthDef(\hedge_hum, { |out, freq = 440, sustain = 1, pan,
        vib = 5.2, depth = 0.015, breath = 0.05, attack = 0.15, release = 1.4|
        var env = EnvGen.ar(Env.linen(attack, sustain, release), doneAction: 2);
        var pitch = Lag.kr(freq, 0.06) * (1 + SinOsc.kr(vib, 0, depth));
        var tone = SinOsc.ar(pitch);
        var air = HPF.ar(WhiteNoise.ar, 2200) * breath;
        Out.ar(out, DirtPan.ar((tone + air) * 0.5, ~dirt.numChannels, pan, env));
    }).add;

    // Breathy whistle: a clear pitched core with quiet air moving with it.
    SynthDef(\hedge_whistle, { |out, freq = 440, sustain = 1, pan,
        vib = 4.2, depth = 0.03, breath = 0.3, attack = 0.12, release = 0.9|
        var env = EnvGen.ar(Env.linen(attack, sustain, release), doneAction: 2);
        var pitch = Lag.kr(freq, 0.08) * (1 + SinOsc.kr(vib, 0, depth));
        var tone = SinOsc.ar(pitch) + (SinOsc.ar(pitch * 2) * 0.08);
        var air = BPF.ar(WhiteNoise.ar, pitch * 2, 3.0) * breath * 0.22;
        var hiss = HPF.ar(WhiteNoise.ar, 3600) * breath * 0.07;
        Out.ar(out, DirtPan.ar((tone * 0.5 + air + hiss) * 0.45, ~dirt.numChannels, pan, env));
    }).add;

    // Distant horn: soft brass core with a brief opening bloom.
    SynthDef(\hedge_horn, { |out, freq = 220, sustain = 1, pan,
        vib = 3.6, depth = 0.012, breath = 0.07, attack = 0.3, release = 1.6|
        var env = EnvGen.ar(Env.linen(attack, sustain, release), doneAction: 2);
        var pitch = Lag.kr(freq, 0.1) * (1 + SinOsc.kr(vib, 0, depth));
        var opening = EnvGen.ar(Env.perc(attack * 0.4, 0.3), levelScale: 500);
        var brass = Saw.ar(pitch * [0.995, 1.0, 1.005]).sum;
        var body = BPF.ar(brass, (pitch * 2.3) + opening, 1.0);
        var core = SinOsc.ar(pitch) * 0.22;
        var air = BPF.ar(WhiteNoise.ar, pitch * 3.5, 2.5) * breath * 0.06;
        var sig = LPF.ar(body + core, 3200);
        Out.ar(out, DirtPan.ar(((sig * 0.35) + air) * 0.13, ~dirt.numChannels, pan, env));
    }).add;

    // Sustained bowed tremolo: detuned saws with a slow amplitude shimmer.
    SynthDef(\hedge_strings, { |out, freq = 220, sustain = 1, pan,
        vib = 5.0, depth = 0.006, tremrate = 6.5, tremdepth = 0.18,
        attack = 0.8, release = 1.4|
        var env = EnvGen.ar(Env.linen(attack, sustain, release), doneAction: 2);
        var pitch = Lag.kr(freq, 0.15) * (1 + SinOsc.kr(vib, 0, depth));
        var bow = Saw.ar(pitch * [0.997, 1.0, 1.004]).sum;
        var body = LPF.ar(bow, 2600);
        var shimmer = 1 + SinOsc.kr(tremrate, 0, tremdepth);
        Out.ar(out, DirtPan.ar(body * 0.3 * shimmer, ~dirt.numChannels, pan, env));
    }).add;

    // Reedy free-reed voice: narrow saw with tracked breath, below the whistle.
    SynthDef(\hedge_melodica, { |out, freq = 440, sustain = 1, pan,
        vib = 5.0, depth = 0.01, breath = 0.12, attack = 0.18, release = 0.7,
        reed = 0.7, bright = 1700|
        var env = EnvGen.ar(Env.linen(attack, sustain, release), doneAction: 2);
        var pitch = Lag.kr(freq, 0.08) * (1 + SinOsc.kr(vib, 0, depth));
        var narrow = VarSaw.ar(pitch, 0, 0.32);
        var wide = Saw.ar(pitch);
        var source = (narrow * reed) + (wide * (1 - reed));
        var body = LPF.ar(source, bright);
        var air = BPF.ar(WhiteNoise.ar, pitch * 2.2, 2.5) * breath * 0.5;
        var sig = (body * 0.22) + air;
        Out.ar(out, DirtPan.ar(sig, ~dirt.numChannels, pan, env));
    }).add;

    // Dry clockwork tick: inharmonic metal partials with a short noise click.
    SynthDef(\hedge_clock, { |out, freq = 1200, sustain = 0.08, pan,
        decay = 0.06, metal = 0.65|
        var env = EnvGen.ar(Env.perc(0.001, decay), doneAction: 2);
        var partials = SinOsc.ar(freq * [1, 1.41, 1.93, 2.71]);
        var weights = [1, 0.55, 0.35, 0.2] * metal;
        var tone = (partials * weights).sum;
        var click = HPF.ar(WhiteNoise.ar, 5000) * (1 - metal) * 0.5;
        var sig = (tone * 0.3) + (click * 0.15);
        Out.ar(out, DirtPan.ar(sig, ~dirt.numChannels, pan, env));
    }).add;

    // Resonant plucked zither: Karplus-Strong string with a slight bend.
    SynthDef(\hedge_koto, { |out, freq = 440, sustain = 1, pan,
        decay = 2.0, damp = 0.3, bend = 0.6, bright = 3200|
        var env = EnvGen.ar(Env.perc(0.002, decay), doneAction: 2);
        var pitch = freq * Line.kr(1 - (bend * 0.02), 1, 0.18);
        var string = Pluck.ar(WhiteNoise.ar, Impulse.ar(0), 0.05, 1 / pitch, decay, damp);
        var body = LPF.ar(string, bright);
        var sig = body * 0.7;
        Out.ar(out, DirtPan.ar(sig, ~dirt.numChannels, pan, env));
    }).add;

    "Hedgehog SynthDefs loaded".postln;
)
