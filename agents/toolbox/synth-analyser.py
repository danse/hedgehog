#!/usr/bin/env python3
"""Render a project SynthDef offline and report its band balance.

Uses sclang + scsynth -N, so it needs no running server and cannot disturb
the live set. The audio numbers come from scripts/analyse-audio.py.

Usage:
  agents/toolbox/synth-analyser.py NAME [--param K=V ...] [options]
  agents/toolbox/synth-analyser.py --all [options]

Options:
  --defs FILE      SynthDef source (default boot/HedgeSynths.scd)
  --freq HZ        note frequency (default 440)
  --sustain S      event sustain (default 0.5)
  --param K=V      synth control, repeatable (e.g. --param bow=0.12)
  --window S       analysis window (default 0.25)
  --bands LIST     band edges in Hz (default 500,1500,3000,6000)
  --all            analyse every SynthDef in --defs
  --keep WAV       copy the rendered WAV here instead of deleting it
"""
import argparse
import importlib.util
import os
import re
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
ANALYSER = ROOT / "scripts" / "analyse-audio.py"
spec = importlib.util.spec_from_file_location("analyse_audio", ANALYSER)
analyse_audio = importlib.util.module_from_spec(spec)
spec.loader.exec_module(analyse_audio)

SCD = r'''~dirt = (numChannels: 2);
this.executeFile("{defs}");
~def = SynthDescLib.global[{name}].def;
~params = [{params}];
~list = [
    [0.0, ["/g_new", 1, 0, 0]],
    [0.0, ["/d_recv", ~def.asBytes]],
    [0.25, ["/s_new", "{name}", 1000, 0, 1,
        "out", 0, "freq", {freq}, "sustain", {sustain}] ++ ~params],
    [{duration}, ["/c_set", 0, 0]]
];
Score.write(~list, "{osc}");
0.exit;
'''


def sc_name(name):
    return "\\" + name


def parse_params(items):
    out = []
    for item in items:
        if "=" not in item:
            raise ValueError("--param expects K=V, got %r" % item)
        k, v = item.split("=", 1)
        try:
            float(v)
        except ValueError:
            raise ValueError("--param value must be numeric, got %r" % v)
        out.append('"%s", %s' % (k, v))
    return ", ".join(out)


def render(name, args, tmp, duration):
    osc = tmp / "score.osc"
    wav = tmp / "tone.wav"
    scd = tmp / "render.scd"
    scd.write_text(SCD.format(
        defs=str(args.defs), name=sc_name(name), params=parse_params(args.param),
        freq=args.freq, sustain=args.sustain, duration=duration, osc=str(osc)))
    run = subprocess.run(["sclang", str(scd)], cwd=ROOT, text=True,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if run.returncode != 0 or "ERROR" in run.stdout:
        raise RuntimeError("sclang failed:\n" + run.stdout[-2000:])
    run = subprocess.run(["scsynth", "-N", str(osc), "_", str(wav),
                          "48000", "wav", "int16", "-o", "2", "-u", "58010"],
                         cwd=ROOT, text=True, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    if run.returncode != 0 or "SynthDef not found" in run.stdout:
        raise RuntimeError("scsynth failed:\n" + run.stdout[-2000:])
    return wav


def analyse(wav, args):
    x, sr = analyse_audio.load_wav(str(wav))
    peak = float(np.max(np.abs(x))) if len(x) else 0.0
    if 0.0 < peak < 0.05:
        factor = 0.5 / peak
        y = np.clip(x * factor, -1.0, 1.0)
        with wave.open(str(wav), "wb") as out:
            out.setnchannels(1)
            out.setsampwidth(2)
            out.setframerate(sr)
            out.writeframes((y * 32767).astype("<i2").tobytes())
        print("(quiet synth: normalised by %.1f for analysis)" % factor)
    cmd = [sys.executable, str(ANALYSER), "--window", str(args.window),
           "--bands", args.bands, str(wav)]
    out = subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE).stdout
    print(out.strip())
    x, sr = analyse_audio.load_wav(str(wav))
    size = max(256, int(sr * args.window))
    cutoff = next((b for b in (int(v) for v in args.bands.split(","))
                   if b >= 3000), 3000)
    shares, flats = [], []
    for start in range(0, len(x) - size, size):
        seg = x[start:start + size]
        if np.sqrt(np.mean(seg ** 2)) < 0.01:
            continue
        mag = np.abs(np.fft.rfft(seg * np.hanning(len(seg)))) + 1e-12
        freqs = np.fft.rfftfreq(len(seg), 1 / sr)
        hi = mag[freqs >= cutoff]
        if not len(hi):
            continue
        shares.append(hi.sum() / mag.sum())
        flats.append(np.exp(np.log(hi).mean()) / hi.mean())
    if shares:
        share, flat = float(np.mean(shares)), float(np.mean(flats))
        if share > 0.05 and flat > 0.15:
            verdict = "HISS (noise-like high band)"
        elif share > 0.05:
            verdict = "bright but tonal"
        else:
            verdict = "clean"
        print("\n%s: >%d Hz = %.1f%% of power, flatness %.2f -> %s (%d windows)"
              % (wav.stem, cutoff, 100 * share, flat, verdict, len(shares)))


def def_names(path):
    return re.findall(r"SynthDef\(\\([A-Za-z0-9_]+)", path.read_text())


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("name", nargs="?", help="SynthDef name without the backslash")
    ap.add_argument("--defs", type=Path, default=ROOT / "boot" / "HedgeSynths.scd")
    ap.add_argument("--freq", type=float, default=440.0)
    ap.add_argument("--sustain", type=float, default=0.5)
    ap.add_argument("--param", action="append", default=[], metavar="K=V")
    ap.add_argument("--window", type=float, default=0.25)
    ap.add_argument("--bands", default="500,1500,3000,6000")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--keep", type=Path)
    args = ap.parse_args()
    if bool(args.name) == bool(args.all):
        ap.error("give a NAME or --all, not both")

    names = def_names(args.defs) if args.all else [args.name]
    if not names:
        ap.error("no SynthDefs found in %s" % args.defs)
    tmp_root = "/tmp/opencode" if os.path.isdir("/tmp/opencode") else None
    try:
        for name in names:
            with tempfile.TemporaryDirectory(prefix="hedgehog-synth-",
                                             dir=tmp_root) as td:
                tmp = Path(td)
                wav = render(name, args, tmp, max(3.0, args.sustain + 4.0))
                print("\n=== %s (%g Hz, sustain %g) ===" %
                      (name, args.freq, args.sustain))
                analyse(wav, args)
                if args.keep:
                    out = args.keep if len(names) == 1 else args.keep / (name + ".wav")
                    out.parent.mkdir(parents=True, exist_ok=True)
                    out.write_bytes(wav.read_bytes())
    except (RuntimeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
