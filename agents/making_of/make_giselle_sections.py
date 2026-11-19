#!/usr/bin/env python3
"""Generate a Tidal track from Adam's Giselle Pas de deux (Mutopia MIDI)."""
import struct
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
d = open(HERE / 'scores' / 'giselle.mid', 'rb').read()
div = struct.unpack('>H', d[12:14])[0]
pos = 14
N = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']

def nm(n):
    return N[n % 12].lower().replace('#', 's') + str(n // 12)

def vlq(b, i):
    v = 0
    while True:
        x = b[i]; i += 1; v = (v << 7) | (x & 127)
        if not x & 128:
            return v, i

tracks = []
for _ in range(5):
    ln = struct.unpack('>I', d[pos+4:pos+8])[0]
    body = d[pos+8:pos+8+ln]; pos += 8 + ln
    i = 0; tick = 0; run = None; notes = []
    while i < len(body):
        dt, i = vlq(body, i); tick += dt
        b = body[i]
        if b & 128:
            st = b; i += 1
            if st < 0xf0: run = st
        else:
            st = run
        if st == 0xff:
            i += 1; l, i = vlq(body, i); i += l; continue
        if st in (0xf0, 0xf7):
            l, i = vlq(body, i); i += l; continue
        ty = st & 0xf0
        if ty in (0x80, 0x90):
            note = body[i]; vel = body[i+1]; i += 2
            if ty == 0x90 and vel > 0:
                notes.append((tick, note))
        elif ty in (0xa0, 0xb0, 0xe0): i += 2
        elif ty in (0xc0, 0xd0): i += 1
    tracks.append(notes)

barlen = div * 2
pickup = div // 2

def bars(track):
    out = {}
    for tick, note in tracks[track]:
        t = tick - pickup
        if t < 0: continue
        b = t // barlen + 1
        slot = min(7, int(round(((t % barlen) / div + 1 - 1) * 4)))
        out.setdefault(b, ['~'] * 8)
        name = nm(note)
        if out[b][slot] == '~': out[b][slot] = name
        else: out[b][slot] = '[%s,%s]' % (out[b][slot].strip('[]'), name)
    return out

upper = bars(1)
counter = bars(2)
bass1 = bars(3)
bass2 = bars(4)

def line(src, b1, b2):
    a = src.get(b1, ['~'] * 8)
    z = src.get(b2, ['~'] * 8)
    return '  "' + ' '.join(a + z) + '"'

def emit(d, voice, src, pairs):
    rows = [line(src, a, b) for a, b in pairs]
    return 'd%d $ %s (cat [\n%s])' % (d, voice, ',\n'.join(rows))

# ---------------------------------------------------------------------------
head = '''-- Giselle — techno after Adam's Pas de deux (Act I)
-- 140 BPM · four sections that follow the 48 printed bars of the Mutopia
-- edition (Adam, arr. Sardain, public domain). Two 2/4 score bars make one
-- 4/4 Tidal bar, so every mini-notation line below is one 16th-note grid of a
-- bar-pair, and every note is transcribed from the score's MIDI/LilyPond —
-- nothing is invented. The piece stays in G major. The original is 80 BPM;
-- at 140 the eighths run about 1.75x faster.
--
-- Voice map: the Prima's upper staff is the tune, its lower staff the answer;
-- the Seconda's upper staff is the D/F# pedal, its lower staff the G/C bass.
-- Kit and drums carry between sections; only changing voices re-enter. Every
-- handover is hard — evaluate a section's lines on the downbeat.
--
-- Gotchas: reverb size <= 0.9; `amp` is linear (prefer it to `gain`). Mini-
-- notation accidentals are `s`/`f` (fs4, bf3), never `#`. One cycle is one bar
-- (~1.71 s at 140). Project synth voices take `note`; sample voices take
-- `speedAt`. juno:7 is C3 and moog:3 is G1, so speedAt runs from those.
-- tech: 0 closed hh, 5 kick1, 7 open hh, 11 snare1; odx:11 is the crash.

glideBpm 140 30

-- ---------------------------------------------------------------------------
-- Reused voices. Everything used once stays inline at its section. Keep this
-- whole block one paragraph: C-RET evaluates the paragraph at point.
-- ---------------------------------------------------------------------------
let
  -- One kit for the whole piece.
  kickOn :: Pattern String -> ControlPattern
  kickOn p = s p # amp 1.05 # room 0.04 # size 0.12
  -- Three straight bars, then a tag on the fourth.
  kick :: ControlPattern
  kick = kickOn (cat [
    "tech:5*4",
    "tech:5*4",
    "tech:5*4",
    "tech:5 ~ ~ ~ tech:5 ~ ~ ~ tech:5 ~ tech:5 ~ tech:5 ~ tech:5 ~"])
  -- tech:0 sits ~20 dB below the kick at source, so the hats need a lift.
  hatsOn :: Pattern String -> ControlPattern
  hatsOn p = s p # amp "4.4 2 3 2" # hpf 500 # room 0.05 # size 0.14
  hats :: ControlPattern
  hats = hatsOn (cat [
    "tech:0*16",
    "tech:0*16",
    "tech:0*16",
    "tech:0*32"])
  snareOn :: Pattern String -> ControlPattern
  snareOn p = s p # amp 0.68 # room 0.16 # size 0.3
  clapOn :: Pattern String -> ControlPattern
  clapOn p = s p # amp 0.6 # room 0.2 # size 0.36
  clap :: ControlPattern
  clap = clapOn "~ ~ cp:0 ~ ~ ~ cp:0 ~"
  openOn :: Pattern String -> ControlPattern
  openOn p = s p # amp 0.7 # hpf 350 # room 0.12 # size 0.24 # pan 0.56
  openHat :: ControlPattern
  openHat = openOn "~ ~ ~ ~ ~ ~ ~ tech:7"
  -- The DX crash is a 1.4 s wash that reads once per four-bar phrase.
  crash :: ControlPattern
  crash = s "odx:11" # amp 0.55 # hpf 500 # room 0.35 # size 0.6
  crashPhrase :: ControlPattern
  crashPhrase = slow 4 crash
  --
  -- Sample voices. `speedAt` only cares about intervals, so the base note
  -- names the sample's natural pitch.
  subAt :: Pattern Note -> ControlPattern
  subAt p = s "moog:3" # speedAt "g1" p
      # sustain 0.22 # release 0.1 # lpf 260 # lpq 0.2 # amp 1.7
  keysAt :: Pattern Note -> ControlPattern
  keysAt p = s "juno:7" # speedAt "c3" p
      # sustain 0.4 # release 0.5 # lpf 2400 # room 0.45 # size 0.6 # amp 0.32
  --
  -- Project synth voices. `note` is MIDI; `n` would get SuperDirt's offset.
  -- Only set parameters the SynthDef actually declares.
  padAt :: Pattern Note -> ControlPattern
  padAt p = s "hedge_pad" # note p
      # sustain 1.6 # amp 0.42 # room 0.5 # size 0.62
  bellAt :: Pattern Note -> ControlPattern
  bellAt p = s "hedge_clock" # note p
      # decay 0.38 # amp 1.5 # room 0.5 # size 0.7
  leadAt :: Pattern Note -> ControlPattern
  leadAt p = s "hedge_whistle" # note p
      # attack 0.06 # sustain 0.14 # release 0.25
      # room 0.35 # size 0.55 # amp 1
  -- hedge_horn is mixed ~5x below the other synth voices; loden uses amp 10.
  brassAt :: Pattern Note -> ControlPattern
  brassAt p = s "hedge_horn" # note p
      # attack 0.08 # sustain 0.22 # release 0.35
      # room 0.3 # size 0.5 # amp 10
  reedAt :: Pattern Note -> ControlPattern
  reedAt p = s "hedge_melodica" # note p
      # attack 0.05 # sustain 0.1 # release 0.12
      # room 0.25 # size 0.45 # amp 1.4
'''

sections = []
sections.append(('''-- 1. A theme — score bars 1-16, G major. The whole band: the Prima's tune on
--    the whistle, her counter-melody on the melodica, the Seconda's two pedals
--    under it. Hold for eight bars (two passes of the four-bar tune).
''', [
    (1, 'kick', None),
    (2, 'hats', None),
    (3, 'subAt', bass2, [(a, a+1) for a in range(1, 17, 2)]),
    (4, 'keysAt', bass1, [(a, a+1) for a in range(1, 17, 2)]),
    (5, '$ clap', None),
    (6, 'openHat', None),
    (7, 'leadAt', upper, [(a, a+1) for a in range(1, 17, 2)]),
    (8, 'reedAt', counter, [(a, a+1) for a in range(1, 17, 2)]),
    (9, 'crashPhrase', None),
    (10, '$ slow 4 $ padAt "[g3,b3,d4]" # sustain 6 # amp 0.3', None),
]))

sections.append(('''-- 2. Lyrical section — score bars 17-32. The tune moves to a higher,
--    long-breathed phrase and the pedals walk C–G–B minor. The pad leaves;
--    the kit carries over without a new entrance.
''', [
    (10, 'silence', None),
    (3, 'subAt', bass2, [(a, a+1) for a in range(17, 33, 2)]),
    (4, 'keysAt', bass1, [(a, a+1) for a in range(17, 33, 2)]),
    (7, 'leadAt', upper, [(a, a+1) for a in range(17, 33, 2)]),
    (8, 'reedAt', counter, [(a, a+1) for a in range(17, 33, 2)]),
]))

sections.append(('''-- 3. A returns — score bars 33-40. The opening gambit comes back on the
--    whistle and the G/C pedals return underneath. One pass only, four bars.
''', [
    (3, 'subAt', bass2, [(a, a+1) for a in range(33, 41, 2)]),
    (4, 'keysAt', bass1, [(a, a+1) for a in range(33, 41, 2)]),
    (7, 'leadAt', upper, [(a, a+1) for a in range(33, 41, 2)]),
    (8, 'reedAt', counter, [(a, a+1) for a in range(33, 41, 2)]),
    (10, '$ slow 4 $ padAt "[g3,b3,d4]" # sustain 6 # amp 0.3', None),
]))

sections.append(('''-- 4. Coda — score bars 41-48. The rising sequence and the V–I tag, with a
--    brass answer under the last phrase. The pad holds the final G.
''', [
    (3, 'subAt', bass2, [(a, a+1) for a in range(41, 49, 2)]),
    (4, 'keysAt', bass1, [(a, a+1) for a in range(41, 49, 2)]),
    (7, 'leadAt', upper, [(a, a+1) for a in range(41, 49, 2)]),
    (8, 'reedAt', counter, [(a, a+1) for a in range(41, 49, 2)]),
    (10, '$ slow 4 $ padAt "[g3,b3,d4]" # sustain 8 # amp 0.5 # room 0.7 # size 0.85', None),
]))

out = [head]
for comment, entries in sections:
    out.append(comment)
    for entry in entries:
        dn, voice = entry[0], entry[1]
        if len(entry) == 2:
            out.append('d%d\n' % dn)
        elif len(entry) == 3 and entry[2] is None:
            out.append('d%d %s\n' % (dn, voice))
        else:
            src, pairs = entry[2], entry[3]
            rows = [line(src, a, b) for a, b in pairs]
            out.append('d%d $ %s (cat [\n%s])\n' % (dn, voice, ',\n'.join(rows)))
out.append('fadeSilence 8 [10]\n')
open(ROOT / 'tracks' / 'techno' / 'giselle.tidal', 'w').write('\n'.join(out))
print('wrote tracks/techno/giselle.tidal')
