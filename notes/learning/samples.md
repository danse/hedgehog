# Listing available samples

There are three different questions here, and only one of them has a live
answer in Tidal.

## What is actually loaded

SuperDirt prints one line of `bank (variants)` pairs at boot, straight after
`N existing sample banks`. In this setup sclang is headless, so that line lands
in the log:

```bash
grep -A1 'existing sample banks' logs/superdirt.log | tail -1
```

This is the authoritative list — it shows what SuperDirt registered, not what
happens to be on disk. The distinction matters: with sclang's default
`numBuffers = 1024`, loading died at bank `ht` and everything after it
(`tok`, `tabla`, `jvbass`, …) was silently absent, even though the files were
there. `boot/BootSuperDirt.scd` now sets `s.options.numBuffers = 4096` to match
scsynth's `-b 4096` in `scripts/up.sh`; all 218 banks load.

SuperDirt also has `~dirt.soundLibrary.postSampleInfo`, which posts a richer
table (variants, duration range, memory footprint), but it writes to the SC log
and there is no OSC command wired up to trigger it from the REPL.

## What files a bank contains

```bash
ls ~/.local/share/SuperCollider/downloaded-quarks/Dirt-Samples/tok/
# 000_0.wav  001_1.wav  002_2.wav  003_3.wav
```

Filenames are sorted and numbered from zero, so those are `tok:0` … `tok:3`.
`samples/README.md` covers adding set-specific banks under `samples/`.

## From the Tidal REPL

Tidal 1.10.3 has no sample-list command. Checking the local checkout, the only
OSC messages it sends to SuperDirt are `/dirt/handshake`, `/dirt/hello`,
`/dirt/synth-info` (control names for one named synth) and `/dirt/play`. The
`samples` function in `Sound.Tidal.UI` is a pattern combinator for picking
variants:

```haskell
samples "arpy*8" (run 16)
```

— it is not a listing. Use the log or the shell for discovery, then write the
bank name into the pattern.
