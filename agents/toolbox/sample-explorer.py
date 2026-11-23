#!/usr/bin/env python3
"""Search sample banks for a role, reporting properties rather than verdicts.

This is the exploratory counterpart to synth-analyser.py. That tool diagnoses
one known voice for defects; this one scans many samples and describes them so
you can pick one for a part. Nothing here is "bad": a large sub-octave is a
property that may be welcome on good speakers, so it is reported neutrally.

Note that the hold figure uses the whole buffer. A short-window estimate is
misleading — a sample can look steady for half a second and then decay away.

Usage:
  agents/toolbox/sample-explorer.py [options] [BANK ...]

Options:
  --min-len S       minimum buffer length in seconds
  --min-hold PCT    minimum hold: median RMS of the latter half vs the peak
  --max-sub PCT     maximum share of power below 40 Hz
  --root LO-HI      root pitch range in Hz, e.g. 40-100
  BANK ...          bank names or globs (default: all banks)
  --sort FIELD      file|len|root|sub|hold|cent (default: hold)
  --limit N         rows to print (default 40; 0 for all)
  --dir PATH        corpus root (default: installed Dirt-Samples)
  --window S        steady window for pitch and spectrum (default 0.5)
  --local           also scan this repo's samples/ directory

BANK names follow Dirt-Samples directory names; VAR is the file's index in the
sorted bank, which is the number after the colon in `s "bank:var"`. A `~` before
a root means autocorrelation missed it and the strongest playable partial was
used — check those by ear before writing a speedAt base.
"""
import argparse
import fnmatch
import importlib.util
import sys
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
ANALYSER = ROOT / "scripts" / "analyse-audio.py"
spec = importlib.util.spec_from_file_location("analyse_audio", ANALYSER)
analyse_audio = importlib.util.module_from_spec(spec)
spec.loader.exec_module(analyse_audio)

DIRT = Path.home() / ".local/share/SuperCollider/downloaded-quarks/Dirt-Samples"
LOCAL = ROOT / "samples"
ENV_WIN = 0.5  # seconds per section of the envelope profile


def features(path, window):
    """Return descriptive metrics for one WAV, or None if it is too short."""
    x, sr = analyse_audio.load_wav(str(path))
    dur = len(x) / sr
    if dur < 0.05:
        return None

    # Steady window: skip the attack, then measure pitch and band balance.
    start = int(sr * 0.1)
    n = min(int(sr * window), len(x) - start - 1)
    if n < 1024:
        return None
    seg = x[start:start + n]
    mag = np.abs(np.fft.rfft(seg * np.hanning(n))) + 1e-12
    freqs = np.fft.rfftfreq(n, 1 / sr)
    power = mag ** 2
    sub = 100 * float(power[freqs < 40].sum() / power.sum())
    cent = float((freqs * mag).sum() / mag.sum())
    f0, conf = analyse_audio.f0(seg, sr)
    if f0 <= 0 or f0 < 30:
        # Autocorrelation can lock onto a sub-octave or miss the voice. For a
        # speedAt base we want the note the sample is tuned to, so take the
        # strongest partial in the playable range instead of a 20-ish Hz sub.
        band = np.where(freqs >= 30)[0]
        f0 = float(freqs[band[mag[band].argmax()]]) if len(band) else 0.0
        conf = 0.0

    # Envelope across the entire buffer, not just the opening window.
    w = max(1, int(sr * ENV_WIN))
    rms = np.array([np.sqrt((x[i:i + w] ** 2).mean())
                    for i in range(0, len(x) - w + 1, w)])
    if not len(rms):
        return None
    hold = 100 * float(np.median(rms[len(rms) // 2:])) / (float(rms.max()) + 1e-12)
    return dict(dur=dur, root=f0, guess=conf <= 0,
                sub=sub, hold=hold, cent=cent)


def quick_dur(path):
    """Read the WAV header only, so the length filter skips long loads."""
    try:
        with wave.open(str(path), "rb") as w:
            return w.getnframes() / w.getframerate()
    except Exception:
        return None


def bank_dirs(args):
    roots = [Path(args.dir)] if args.dir else [DIRT]
    if args.local:
        roots.append(LOCAL)
    for base in roots:
        if not base.is_dir():
            print("warning: no corpus at %s" % base, file=sys.stderr)
            continue
        for bank in sorted(p for p in base.iterdir() if p.is_dir()):
            if args.banks and not any(fnmatch.fnmatch(bank.name, p)
                                      for p in args.banks):
                continue
            yield bank


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("banks", nargs="*", metavar="BANK",
                    help="bank names or globs; default is all banks")
    ap.add_argument("--min-len", type=float, default=0.0, metavar="S")
    ap.add_argument("--min-hold", type=float, default=0.0, metavar="PCT")
    ap.add_argument("--max-sub", type=float, default=None, metavar="PCT")
    ap.add_argument("--root", metavar="LO-HI",
                    help="root pitch range in Hz, e.g. 40-100")
    ap.add_argument("--sort", default="hold",
                    choices=["file", "len", "root", "sub", "hold", "cent"])
    ap.add_argument("--limit", type=int, default=40, metavar="N")
    ap.add_argument("--dir", metavar="PATH", help="override the corpus root")
    ap.add_argument("--window", type=float, default=0.5, metavar="S")
    ap.add_argument("--local", action="store_true",
                    help="also scan this repo's samples/ directory")
    args = ap.parse_args()

    root_range = None
    if args.root:
        try:
            lo, hi = (float(v) for v in args.root.split("-", 1))
        except ValueError:
            ap.error("--root expects LO-HI, e.g. 40-100")
        root_range = (lo, hi)

    rows = []
    for bank in bank_dirs(args):
        files = sorted(f for f in bank.iterdir() if f.suffix.lower() == ".wav")
        for var, path in enumerate(files):
            if args.min_len and (quick_dur(path) or 0) < args.min_len:
                continue
            try:
                f = features(path, args.window)
            except Exception as e:
                print("warning: skipped %s (%s)" % (path, e), file=sys.stderr)
                continue
            if f is None:
                continue
            if f["hold"] < args.min_hold:
                continue
            if args.max_sub is not None and f["sub"] > args.max_sub:
                continue
            if root_range and not root_range[0] <= f["root"] <= root_range[1]:
                continue
            f["label"] = "%s:%d" % (bank.name, var)
            rows.append(f)

    key = {
        "file": lambda r: r["label"],
        "len": lambda r: -r["dur"],
        "root": lambda r: r["root"],
        "sub": lambda r: r["sub"],
        "hold": lambda r: -r["hold"],
        "cent": lambda r: r["cent"],
    }[args.sort]
    rows.sort(key=key)
    if args.limit:
        rows = rows[:args.limit]

    print("%-16s %6s %-10s %7s %7s %8s" %
          ("SAMPLE", "DUR", "ROOT", "SUB%", "HOLD", "CENT"))
    for r in rows:
        print("%-16s %6.2f %-10s %6.1f%% %6.0f%% %8.0f" %
              (r["label"], r["dur"],
               "%s%s %g" % ("~" if r["guess"] else "",
                            analyse_audio.note_name(r["root"]), r["root"]),
               r["sub"], r["hold"], r["cent"]))
    print("%d match%s" % (len(rows), "" if len(rows) == 1 else "es"))


if __name__ == "__main__":
    main()
