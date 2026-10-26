# Extra samples

Drop sample folders here (one folder per sound, files named `000_*.wav`,
`001_*.wav`, …) and uncomment the `~dirt.loadSoundFiles` line in
`boot/BootSuperDirt.scd`:

```supercollider
~dirt.loadSoundFiles("/home/marea/hub/hedgehog/samples/*");
```

Then restart SuperDirt (`scripts/down.sh && scripts/up.sh --no-emacs`).

Keep the default Dirt-Samples untouched; this folder is for set-specific
material. Use 48 kHz mono or stereo WAV to avoid resampling surprises.
Record licences/sources in `notes/` before publishing a recording.
