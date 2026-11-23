#!/usr/bin/env python3
"""Inspect a recording or sample: level, brightness and band balance over time.

Usage:
  scripts/analyse-audio.py [options] FILE [FILE ...]

Options:
  --window S      analysis window in seconds (default 1.0)
  --bands LIST    band edges in Hz, comma separated (default 500,2000,4000,8000)
  --f0            add an autocorrelation pitch estimate per window
  --raw-f32 SR CH read raw 32-bit float audio instead of WAV

One row per window: time, rms, peak, spectral centroid, share of spectral power
in each band (<500, 500-2000, ..., 8000+), and optionally f0 with a note name.
Only numpy is needed. This is the durable home for the one-off analyses used
while making tracks (rising noise, sample tails); those lives in /tmp are wiped
when the machine shuts down.
"""
import argparse
import os
import sys
import wave

import numpy as np

NAMES = ['c', 'cs', 'd', 'ds', 'e', 'f', 'fs', 'g', 'gs', 'a', 'as', 'b']


def load_wav(path):
    with wave.open(path, 'rb') as w:
        sr = w.getframerate()
        ch = w.getnchannels()
        width = w.getsampwidth()
        raw = w.readframes(w.getnframes())
    if width == 3:
        # 24-bit PCM: three little-endian bytes per sample, signed.
        b = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3).astype(np.int32)
        packed = b[:, 0] | (b[:, 1] << 8) | (b[:, 2] << 16)
        signed = np.where(packed >= (1 << 23), packed - (1 << 24), packed)
        x = signed.astype(np.float64) / float(1 << 23)
    else:
        dtype = {1: np.uint8, 2: np.int16, 4: np.int32}.get(width)
        if dtype is None:
            raise ValueError('unsupported sample width %d bytes' % width)
        x = np.frombuffer(raw, dtype=dtype).astype(np.float64)
        if width == 1:
            x = (x - 128) / 128
        else:
            x /= float(2 ** (8 * width - 1))
    return x.reshape(-1, ch).mean(axis=1), sr


def note_name(freq):
    if freq <= 0:
        return '-'
    n = int(round(69 + 12 * np.log2(freq / 440)))
    return '%s%d' % (NAMES[n % 12], n // 12 - 1)


def f0(x, sr, lo=40, hi=1200):
    """Dominant autocorrelation lag in the lo..hi Hz range, plus confidence."""
    x = x - x.mean()
    if np.max(np.abs(x)) < 1e-5:
        return 0.0, 0.0
    n = 1 << (len(x) * 2 - 1).bit_length()
    spec = np.fft.rfft(x, n)
    ac = np.fft.irfft(spec * np.conj(spec))[:len(x)]
    ac /= ac[0] + 1e-12
    a, b = int(sr / hi), min(len(x) - 2, int(sr / lo))
    if b <= a:
        return 0.0, 0.0
    k = a + int(np.argmax(ac[a:b]))
    if ac[k] < 0.2:
        return 0.0, ac[k]
    p, q, r = ac[k - 1], ac[k], ac[k + 1]
    lag = k + 0.5 * (p - r) / (p - 2 * q + r + 1e-12)
    return sr / lag, q


def analyse(path, args, edges):
    if args.raw_f32:
        sr, ch = args.raw_f32
        x = np.fromfile(path, dtype='<f4').astype(np.float64)
        x = x.reshape(-1, ch).mean(axis=1)
    else:
        x, sr = load_wav(path)
    size = max(256, int(sr * args.window))
    print('\n%s: %.2fs, %d Hz, %d windows' % (os.path.basename(path), len(x) / sr, sr,
                                             max(1, int(np.ceil(len(x) / size)))))
    labels = ['<%d' % edges[0]]
    labels += ['%d-%d' % (a, b) for a, b in zip(edges, edges[1:])]
    labels += ['%d+' % edges[-1]]
    head = '%6s %7s %7s %9s' % ('time', 'rms', 'peak', 'centroid')
    head += ''.join(' %9s' % lab for lab in labels)
    if args.f0:
        head += ' %10s %5s' % ('f0', 'note')
    print(head)

    for start in range(0, len(x), size):
        seg = x[start:start + size]
        if len(seg) < 8:
            break
        rms = np.sqrt(np.mean(seg ** 2))
        peak = np.max(np.abs(seg))
        win = seg * np.hanning(len(seg))
        mag = np.abs(np.fft.rfft(win))
        freqs = np.fft.rfftfreq(len(seg), 1 / sr)
        total = mag.sum() + 1e-12
        centroid = (mag * freqs).sum() / total
        row = '%6.1f %7.3f %7.3f %9.0f' % (start / sr, rms, peak, centroid)
        bounds = [0] + edges + [sr / 2]
        for lo, hi in zip(bounds, bounds[1:]):
            mask = (freqs >= lo) & (freqs < hi)
            row += ' %9.3f' % (mag[mask].sum() / total)
        if args.f0:
            f, conf = f0(seg, sr)
            row += ' %10.1f %5s' % (f, note_name(f))
        print(row)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('files', nargs='+', metavar='FILE')
    ap.add_argument('--window', type=float, default=1.0, metavar='S')
    ap.add_argument('--bands', default='500,2000,4000,8000', metavar='LIST')
    ap.add_argument('--f0', action='store_true')
    ap.add_argument('--raw-f32', nargs=2, type=int, metavar=('SR', 'CH'))
    args = ap.parse_args()
    try:
        edges = sorted(int(b) for b in args.bands.split(','))
    except ValueError:
        ap.error('--bands must be comma-separated Hz values')
    for path in args.files:
        try:
            analyse(path, args, edges)
        except (OSError, ValueError) as exc:
            print('%s: %s' % (path, exc), file=sys.stderr)
            return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
