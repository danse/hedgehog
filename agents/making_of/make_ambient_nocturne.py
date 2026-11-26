#!/usr/bin/env python3
"""Generate tracks/ambient/nocturne.tidal from the decoded Chopin MIDI."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE))
from decode_chopin import UPPER, LOWER, bar_events, SLOTS

BASS_SLOTS = (0, 12, 24, 36)


def voice_line(track, b, slots=None, drop_bass=False):
    ev = bar_events(track, b)
    out = []
    for s in range(SLOTS):
        if slots is not None and s not in slots:
            out.append('~')
            continue
        if drop_bass and s in BASS_SLOTS:
            out.append('~')
            continue
        ns = ev.get(s, [])
        if not ns:
            out.append('~')
        elif len(ns) == 1:
            out.append(ns[0])
        else:
            out.append('[' + ','.join(sorted(set(ns))) + ']')
    return '  "' + ' '.join(out) + '"'


def emit(dn, fn, b1, b2, voice):
    lines = [fn(b) for b in range(b1, b2 + 1)]
    return 'd%d $ %s (cat [\n%s])' % (dn, voice, ',\n'.join(lines))


HEAD = '''-- Nocturne — ambient after Chopin's Nocturne Op. 9 No. 2
-- 78 BPM · beatless. The same 37-bar Mutopia transcription as the techno
-- version (Chopin, 1833; edition by Renato Biolcati Rinaldi,
-- Mutopia-2014/12/18-1590, CC BY-SA 3.0; source G. Schirmer, New York, 1881,
-- from Library of Congress scans). Every note comes from that edition's MIDI.
-- The right hand is the tune, the left hand's broken chords are the plucked
-- voice, and the low note of each dotted-quarter group is the bass. The tune
-- sits an octave below written pitch; everything else is as written.
--
-- Mapping: one score 32nd = one Tidal 16th, so a score eighth becomes a
-- quarter and one 12/8 score bar becomes 48 slots = three Tidal cycles.
-- One mini-notation line below is one score bar (~9 s here). At 78 BPM the
-- whole piece runs about 5.5 minutes.
--
-- No kit. The score's own rhythm carries the movement. Sections follow its
-- form: A (1-8), A' (9-16), A'' (17-24), Coda (25-31), cadenza/final (32-37).
-- Each section's four streams are one editor paragraph: C-RET starts all of
-- them together on the downbeat. No transitions between sections — the earlier
-- xfadeIn ramps read as noise risers (the fiddle's bow scrape arrived before
-- the tone), so sections now change hard. Envelopes are sized to the score's
-- note spacing at this tempo: a 16th slot is 0.19 s, lead notes are typically
-- 0.38 s apart and the left hand 0.77 s apart, so long fixed sustains would
-- stack half a dozen copies of the same line. Reverb supplies the tail. The
-- final fade to silence is the only transition left.
--
-- Gotchas: reverb size <= 0.9; `amp` is linear (prefer it to `gain`). Mini-
-- notation accidentals are `s`/`f` (ef4, bf3), never `#`. Put the score first
-- in every `#` chain so `#` takes whole/steps from it, not from `s` (see
-- boot/BootTidal.hs). `pluck:5` is C3, so speedAt runs from c4; moog:3 is G1.

glideBpm 78 30

-- Clear every seat this track does not use. Other ambient tracks leave a
-- looping hedge_noise riser on d8 (neon_alloy) or an air bed on d1 (campina);
-- a leftover there keeps rising straight through our hard section changes,
-- since this track only writes d2-d5. Eval these with the voices below.
d1 silence
d6 silence
d7 silence
d8 silence
d9 silence
d10 silence

-- ---------------------------------------------------------------------------
-- Voices. Eval this whole block as one paragraph: C-RET at point.
-- ---------------------------------------------------------------------------
let
  -- Bowed tune: a short attack and a modest overlap (about 0.65 s total
  -- against a 0.38 s median gap) keep the line legato without stacking it.
  -- The fiddle's bow scrape is a bandpassed white-noise layer that tracks the
  -- pitch; at 0.08 it can read as a rising hiss over an ascending phrase, so
  -- keep it near inaudible and let the string carry the tune. One octave down.
  leadAt :: Pattern Note -> ControlPattern
  leadAt p = note (p - 12) # s "hedge_fiddle"
      # pF "bow" 0.02
      # attack 0.06 # sustain 0.28 # release 0.32
      # room 0.62 # size 0.8 # amp 1.1
  -- Broken chords: just enough tail to join one pluck to the next.
  keysAt :: Pattern Note -> ControlPattern
  keysAt p = speedAt "c4" p # s "pluck" # n 5
      # sustain 0.32 # release 0.28 # lpf 2200 # lpq 0.25
      # room 0.6 # size 0.76 # amp 0.6
  -- Root notes only, felt more than heard: one per 2.3 s, with a little tail.
  bassAt :: Pattern Note -> ControlPattern
  bassAt p = speedAt "g1" p # s "moog:3"
      # sustain 1.1 # release 0.7 # lpf 220 # lpq 0.2
      # room 0.55 # size 0.7 # amp 1.1
  -- Slow bowed bed under the whole piece; chord colour changes at the Coda.
  padAt :: Pattern Note -> ControlPattern
  padAt p = note p # s "hedge_strings"
      # attack 1.5 # sustain 3 # release 2.5
      # room 0.7 # size 0.85 # amp 1.2
'''


def main():
    out = [HEAD]

    def lead(b):
        return voice_line(UPPER, b)

    def keys(b):
        return voice_line(LOWER, b, drop_bass=True)

    def bass(b):
        return voice_line(LOWER, b, slots=set(BASS_SLOTS))

    def chord(c):
        return lambda b: '  "' + c + '"'

    sections = [
        ('1. A — score bars 1-8', 'the tune in E-flat over its broken chords.',
         1, 8, '[ef2,bf2,g3]'),
        ('2. A prime — score bars 9-16', 'the same theme with a busier middle.',
         9, 16, '[ef2,bf2,c3]'),
        ('3. A double prime — score bars 17-24', 'the most ornamented pass.',
         17, 24, '[ef2,bf2,g3]'),
        ('4. Coda — score bars 25-31', 'new material, then the stretto.',
         25, 31, '[af2,ef3,c4]'),
        ('5. Cadenza and final — score bars 32-37',
         'the written-out cadenza, final chord and fermata.',
         32, 37, '[ef2,bf2,ef3]'),
    ]

    for title, desc, b1, b2, padchord in sections:
        out.append('-- ' + title + ' — ' + desc)
        out.append(emit(2, lead, b1, b2, 'leadAt'))
        out.append(emit(3, keys, b1, b2, 'keysAt'))
        out.append(emit(4, bass, b1, b2, 'bassAt'))
        out.append(emit(5, chord(padchord), b1, b2, 'padAt'))
        out.append('')

    out.append('fadeSilence 16 [2,3,4,5]\n')
    open(ROOT / 'tracks' / 'ambient' / 'nocturne.tidal', 'w').write('\n'.join(out))
    print('wrote tracks/ambient/nocturne.tidal')


if __name__ == '__main__':
    main()
