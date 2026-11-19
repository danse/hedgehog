#!/usr/bin/env python3
"""Decode Mutopia Chopin Nocturne Op.9 No.2 MIDI into Tidal mini-notation.

Mapping: one score 32nd (48 MIDI ticks) -> one Tidal 16th slot.
So a score eighth -> a Tidal quarter, and one 12/8 score bar (2304 ticks)
-> 48 slots = three 4/4 Tidal cycles. One line per score bar.
"""
import struct
from pathlib import Path

HERE = Path(__file__).resolve().parent
MID = HERE / 'scores' / 'chopin_nocturne_op9_n2.mid'
d = open(MID, 'rb').read()
div = struct.unpack('>H', d[12:14])[0]
ntrk = struct.unpack('>H', d[10:12])[0]
pos = 14
NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']


def nm(n):
    """Tidal note name: MIDI 60 (scientific C4) is c5 in Tidal."""
    return NAMES[n % 12].lower().replace('#', 's') + str(n // 12)


def vlq(b, i):
    v = 0
    while True:
        x = b[i]
        i += 1
        v = (v << 7) | (x & 127)
        if not x & 128:
            return v, i


tracks = []
for _ in range(ntrk):
    ln = struct.unpack('>I', d[pos + 4:pos + 8])[0]
    body = d[pos + 8:pos + 8 + ln]
    pos += 8 + ln
    i = 0
    tick = 0
    run = None
    notes = []
    while i < len(body):
        dt, i = vlq(body, i)
        tick += dt
        b = body[i]
        if b & 128:
            st = b
            i += 1
            if st < 0xf0:
                run = st
        else:
            st = run
        if st == 0xff:
            i += 1
            l, i = vlq(body, i)
            i += l
            continue
        if st in (0xf0, 0xf7):
            l, i = vlq(body, i)
            i += l
            continue
        ty = st & 0xf0
        if ty in (0x80, 0x90):
            note = body[i]
            vel = body[i + 1]
            i += 2
            if ty == 0x90 and vel > 0:
                notes.append((tick, note))
        elif ty in (0xa0, 0xb0, 0xe0):
            i += 2
        elif ty in (0xc0, 0xd0):
            i += 1
    tracks.append(notes)

BAR = div * 6          # 12/8 = 2304 ticks
PICKUP = div // 2      # the anacrusis, one eighth
SLOT = div // 8        # one 32nd = 48 ticks = one Tidal 16th
SLOTS = BAR // SLOT    # 48 slots per score bar

UPPER, LOWER = tracks[1], tracks[2]


def bar_events(track, b):
    """Return {slot: [note names]} for score bar b (1-based)."""
    lo = PICKUP + (b - 1) * BAR
    hi = lo + BAR
    out = {}
    for tick, note in track:
        if lo <= tick < hi:
            sl = (tick - lo) // SLOT
            out.setdefault(sl, []).append(nm(note))
    return out


def line(track, b):
    ev = bar_events(track, b)
    slots = []
    for s in range(SLOTS):
        ns = ev.get(s, [])
        if not ns:
            slots.append('~')
        elif len(ns) == 1:
            slots.append(ns[0])
        else:
            slots.append('[' + ','.join(sorted(set(ns))) + ']')
    return '  "' + ' '.join(slots) + '"'


if __name__ == '__main__':
    import sys
    b1 = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    b2 = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    for b in range(b1, b2 + 1):
        print('bar %d lead:' % b)
        print(line(UPPER, b))
        print('bar %d keys:' % b)
        print(line(LOWER, b))
