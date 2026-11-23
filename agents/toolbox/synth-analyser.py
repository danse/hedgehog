#!/usr/bin/env python3
"""Render a project SynthDef offline and report its band balance.

Reports noise in two places: high-band hiss (>3 kHz) and noise-like air in
the harmonic range (120-3000 Hz), where a low-passed scrape hides from the
high-band test. The inter-harmonic floor compares the spectrum between the
note's harmonics with the peaks themselves, in dB.

Uses sclang + scsynth -N, so it needs no running server and cannot disturb
the live set. The audio numbers come from scripts/analyse-audio.py.

Usage:
  agents/toolbox/synth-analyser.py NAME [--param K=V ...] [options]
  agents/toolbox/synth-analyser.py --all [options]

Options:
  --defs FILE      SynthDef source (default boot/HedgeSynths.scd)
  --freq HZ        note frequency (default 440)
  --pitches LIST   comma-separated Hz to sweep; one verdict line per pitch
  --sustain S      event sustain (default 0.5)
  --param K=V      synth control, repeatable (e.g. --param bow=0.12)
  --window S       analysis window (default 0.25)
  --bands LIST     band edges in Hz (default 500,1500,3000,6000)
  --all            analyse every SynthDef in --defs
  --keep WAV       copy the rendered WAV here instead of deleting it
"""
import argparse
import importlib.util
import math
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


def band_flatness(mag, freqs, lo, hi):
    """Geometric / arithmetic mean in a band: flat means noise-like."""
    m = (freqs >= lo) & (freqs < hi)
    if m.sum() < 8:
        return None
    band = mag[m] + 1e-12
    return float(np.exp(np.log(band).mean()) / band.mean())


def harmonic_floor(mag, freqs, f0, lo, hi, tol=5.0):
    """Gap level between harmonics relative to their peaks, in dB.

    Only partials within 34 dB of the fundamental count. Past a synth's body
    filter the harmonics are gone, and scoring the noise there as a 'gap'
    falsely raises the floor on low notes. Skip non-harmonic sources too.
    """
    if not f0 or f0 <= 0 or hi <= lo + f0:
        return None
    harmonic, fundamental = [], None
    for n in range(1, int(hi / f0)):
        if n * f0 < lo:
            continue
        pk = np.abs(freqs - n * f0) <= tol
        if not pk.any():
            continue
        p = float(mag[pk].max())
        if fundamental is None:
            if p < 1e-9:
                return None
            fundamental = p
        if p >= fundamental * 0.02:
            harmonic.append((n, p))
    if len(harmonic) < 4:
        return None
    gaps = []
    for (a, _), (b, _) in zip(harmonic, harmonic[1:]):
        if b != a + 1:
            continue
        gp = np.abs(freqs - (a + 0.5) * f0) <= tol
        if gp.any():
            gaps.append(float(np.median(mag[gp])))
    if not gaps:
        return None
    db = 20 * math.log10(np.median(gaps)
                         / (np.median([p for _, p in harmonic]) + 1e-12))
    return db if db < -12 else None


def analyse(wav, args, label=None):
    label = label or wav.stem
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
    if not args.pitches:
        cmd = [sys.executable, str(ANALYSER), "--window", str(args.window),
               "--bands", args.bands, str(wav)]
        out = subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE).stdout
        print(out.strip())
    x, sr = analyse_audio.load_wav(str(wav))
    size = max(256, int(sr * args.window))
    cutoff = next((b for b in (int(v) for v in args.bands.split(","))
                   if b >= 3000), 3000)
    shares, flats, mids, floors = [], [], [], []
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
        mid = band_flatness(mag, freqs, 120, cutoff)
        if mid is not None:
            mids.append(mid)
        floor = harmonic_floor(mag, freqs, args.freq, 120, cutoff)
        if floor is not None:
            floors.append(floor)
    if shares:
        share, flat = float(np.mean(shares)), float(np.mean(flats))
        if share > 0.05 and flat > 0.15:
            verdict = "HISS (noise-like high band)"
        elif share > 0.05:
            verdict = "bright but tonal"
        else:
            verdict = "clean"
        print("\n%s: >%d Hz = %.1f%% of power, flatness %.2f -> %s (%d windows)"
              % (label, cutoff, 100 * share, flat, verdict, len(shares)))
    if mids:
        mid = float(np.mean(mids))
        if mid > 0.04:
            air = "noise-like air in the harmonic band"
        elif mid > 0.015:
            air = "a little air"
        else:
            air = "tonal"
        print("mid 120-%d Hz: flatness %.3f -> %s" % (cutoff, mid, air))
    if floors:
        db = float(np.mean(floors))
        state = "raised (noise-like floor)" if db > -50 else "deep"
        print("harmonic floor: %.0f dB below the peaks -> %s" % (db, state))


def def_names(path):
    return re.findall(r"SynthDef\(\\([A-Za-z0-9_]+)", path.read_text())


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("name", nargs="?", help="SynthDef name without the backslash")
    ap.add_argument("--defs", type=Path, default=ROOT / "boot" / "HedgeSynths.scd")
    ap.add_argument("--freq", type=float, default=440.0)
    ap.add_argument("--pitches", metavar="LIST",
                    help="comma-separated Hz to sweep, e.g. 147,220,294")
    ap.add_argument("--sustain", type=float, default=0.5)
    ap.add_argument("--param", action="append", default=[], metavar="K=V")
    ap.add_argument("--window", type=float, default=0.25)
    ap.add_argument("--bands", default="500,1500,3000,6000")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--keep", type=Path)
    args = ap.parse_args()
    if bool(args.name) == bool(args.all):
        ap.error("give a NAME or --all, not both")
    try:
        freqs = ([float(p) for p in args.pitches.split(",")]
                 if args.pitches else [args.freq])
    except ValueError:
        ap.error("--pitches must be comma-separated Hz values")
    if any(f <= 0 for f in freqs):
        ap.error("--pitches values must be positive")

    names = def_names(args.defs) if args.all else [args.name]
    if not names:
        ap.error("no SynthDefs found in %s" % args.defs)
    many = len(names) * len(freqs) > 1
    tmp_root = "/tmp/opencode" if os.path.isdir("/tmp/opencode") else None
    try:
        for name in names:
            for freq in freqs:
                args.freq = freq
                with tempfile.TemporaryDirectory(prefix="hedgehog-synth-",
                                                 dir=tmp_root) as td:
                    tmp = Path(td)
                    wav = render(name, args, tmp, max(3.0, args.sustain + 4.0))
                    if args.pitches:
                        analyse(wav, args, label="%s @ %g Hz" % (name, freq))
                    else:
                        print("\n=== %s (%g Hz, sustain %g) ===" %
                              (name, freq, args.sustain))
                        analyse(wav, args)
                    if args.keep:
                        out = (args.keep / ("%s-%g.wav" % (name, freq))
                               if many else args.keep)
                        out.parent.mkdir(parents=True, exist_ok=True)
                        out.write_bytes(wav.read_bytes())
    except (RuntimeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
