// Hedgehog — headless SuperCollider + SuperDirt startup.
// scripts/up.sh starts scsynth first, then runs this file with pw-jack.

(
s.latency = 0.35;

// scsynth is started separately so it cannot inherit sclang's UDP socket
// on port 57120, which otherwise steals OSC replies and Tidal messages.
s.statusWatcher.serverRunning = true;
s.statusWatcher.notified = true;
s.statusWatcher.instVarPut(\sampleRate, 48000.0);
s.statusWatcher.instVarPut(\actualSampleRate, 48000.0);

// scsynth is started separately with -b 4096, but sclang cannot discover that
// from the faked status, so its allocator still uses the default 1024 and dies
// partway through Dirt-Samples (2040 files). Keep these two numbers in sync.
s.options.numBuffers = 4096;
s.newAllocators;
s.sendDefaultGroups;
    ~dirt = SuperDirt(2, s);

    // Default Dirt-Samples from ~/.local/share/SuperCollider/downloaded-quarks
    ~dirt.loadSoundFiles;

    // Extra samples for this set (uncomment once samples/ has content):
    // ~dirt.loadSoundFiles("/home/marea/hub/hedgehog/samples/*");

    // Project SynthDefs live in their own file.
    this.executeFile(thisProcess.nowExecutingPath.dirname +/+ "HedgeSynths.scd");

    // 12 stereo orbits; Tidal orbits 0..11 map onto these.
    ~dirt.start(57120, 0 ! 12);

    "SuperDirt ready on port 57120".postln;
)
