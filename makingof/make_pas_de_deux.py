#!/usr/bin/env python3
"""Single-section transcription of Adam's Pas de deux (Mutopia MIDI).

All 48 printed bars become 24 Tidal cycles, one continuous paragraph of
streams with no section boundaries or transitions. The Seconda's upper-staff
chords are split: lowest note stays in the pedal voice, upper notes become a
sparse inner line.
"""
import struct
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
d = open(HERE / 'scores' / 'giselle.mid', 'rb').read()
div = struct.unpack('>H', d[12:14])[0]
pos = 14
N = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']


def nm(n):
    return N[n % 12].lower().replace('#', 's') + str(n // 12)


def vlq(b, i):
    v = 0
    while True:
        x = b[i]
        i += 1
        v = (v << 7) | (x & 127)
        if not x & 128:
            return v, i


tracks = []
for _ in range(5):
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

BAR = div * 2
PICKUP = div // 2
SLOTS = 8  # one 2/4 score bar = 8 Tidal 16ths at this mapping


def slotmap(track):
    out = {}
    for tick, note in tracks[track]:
        t = tick - PICKUP
        if t < 0:
            continue
        bar = t // BAR + 1
        slot = min(SLOTS - 1, int((t % BAR) / div * 4))
        out.setdefault((bar, slot), []).append(note)
    return out


VOICES = {name: slotmap(i) for i, name in
          [(1, 'lead'), (2, 'answer'), (3, 'pedal'), (4, 'bass')]}


def token(notes):
    if not notes:
        return '~'
    names = sorted(set(nm(n) for n in notes))
    return names[0] if len(names) == 1 else '[' + ','.join(names) + ']'


def line(voice, pair_index, split=None):
    """One Tidal cycle = two score bars = 16 slots."""
    src = VOICES[voice]
    out = []
    for bar in (2 * pair_index - 1, 2 * pair_index):
        for slot in range(SLOTS):
            notes = src.get((bar, slot), [])
            ordered = sorted(set(notes))
            if split == 'low':
                chosen = [ordered[0]] if len(ordered) > 1 else notes
            elif split == 'high':
                chosen = ordered[1:] if len(ordered) > 1 else []
            else:
                chosen = notes
            out.append(token(chosen))
    return '  "' + ' '.join(out) + '"'


def emit(dn, voice, helper, split=None):
    rows = [line(voice, i, split) for i in range(1, 25)]
    return 'd%d $ %s (cat [\n%s])' % (dn, helper, ',\n'.join(rows))


HEAD = '''-- Pas de deux — single-section techno after Adam (Act I of Giselle)
-- 140 BPM · one continuous transcription of all 48 printed bars of the Mutopia
-- edition (Adam, arr. Laurence Sardain, public domain). Two 2/4 score bars
-- make one 4/4 Tidal cycle, so each mini-notation line below is one cycle and
-- the whole track is 24 cycles (~41 s). Every note comes from that edition's
-- MIDI; nothing is invented. The piece stays in G major.
--
-- One section only: no kit handovers, no xfades, no tempo changes mid-track.
-- Every stream is one editor paragraph, so C-RET starts the whole piece on the
-- downbeat. The only fade is the ending.
--
-- Voice map: Prima upper = tune (d7), Prima lower = answer (d8), Seconda lower
-- = G/C bass (d3). The Seconda upper staff's two-note chords are split: the
-- low note stays as the pedal (d4), the upper note becomes a sparse inner line
-- (d9). That is the only derived voice — it adds movement to the otherwise
-- static G/D pedal without inventing notes.
--
-- Gotchas: reverb size <= 0.9; `amp` is linear (prefer it to `gain`). Mini-
-- notation accidentals are `s`/`f` (fs4, bf3), never `#`. Score first in every
-- `#` chain: `#` takes whole/steps from the left (see boot/BootTidal.hs).
-- juno:7 is C3 and moog:3 is G1, so speedAt runs from those notes.
-- tech: 0 closed hh, 5 kick1, 7 open hh; odx:11 is the crash.

glideBpm 140 8

-- ---------------------------------------------------------------------------
-- Voices. Eval this whole block as one paragraph: C-RET at point.
-- ---------------------------------------------------------------------------
let
  subAt :: Pattern Note -> ControlPattern
  subAt p = speedAt "g1" p # s "moog:3"
      # sustain 0.22 # release 0.1 # lpf 260 # lpq 0.2 # amp 1.7
  keysAt :: Pattern Note -> ControlPattern
  keysAt p = speedAt "c3" p # s "juno:7"
      # sustain 0.4 # release 0.5 # lpf 2400 # room 0.45 # size 0.6 # amp 0.32
  innerAt :: Pattern Note -> ControlPattern
  innerAt p = note p # s "hedge_melodica"
      # attack 0.04 # sustain 0.18 # release 0.2
      # room 0.35 # size 0.5 # amp 0.75
  leadAt :: Pattern Note -> ControlPattern
  leadAt p = note p # s "hedge_whistle"
      # attack 0.04 # sustain 0.5 # release 0.3
      # room 0.35 # size 0.55 # amp 2.6
  reedAt :: Pattern Note -> ControlPattern
  reedAt p = note p # s "hedge_melodica"
      # attack 0.05 # sustain 0.1 # release 0.12
      # room 0.25 # size 0.45 # amp 1.1
'''

KIT = [
    '-- One kit phrase for the whole piece. No section changes.',
    'd1 $ s "tech:5*4" # amp 1.05 # room 0.04 # size 0.12',
    'd2 $ s "tech:0*16" # amp "3.6 2 2.6 2" # hpf 500 # room 0.05 # size 0.14',
    'd5 $ s "~ ~ cp:0 ~ ~ ~ cp:0 ~" # amp 0.6 # room 0.2 # size 0.36',
    'd6 $ s "~ ~ ~ ~ ~ ~ ~ tech:7" # amp 0.7 # hpf 350 # room 0.12 # size 0.24 # pan 0.56',
    'd10 $ note "[g3,b3,d4]" # s "hedge_pad" # sustain 2.4 # amp 0.38 # room 0.5 # size 0.62',
]


def main():
    out = [HEAD]
    out.extend(KIT)
    out.append(emit(3, 'bass', 'subAt'))
    out.append(emit(4, 'pedal', 'keysAt', split='low'))
    out.append(emit(7, 'lead', 'leadAt'))
    out.append(emit(8, 'answer', 'reedAt'))
    out.append(emit(9, 'pedal', 'innerAt', split='high'))
    out.append('')
    out.append('fadeSilence 8 [1,2,3,4,5,6,7,8,9,10]\n')
    path = ROOT / 'tracks' / 'techno' / 'pas-de-deux.tidal'
    open(path, 'w').write('\n'.join(out))
    print('wrote', path)


if __name__ == '__main__':
    main()
