#!/usr/bin/env python3
"""Generate tracks/techno/nocturne.tidal from the decoded Chopin MIDI."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
from decode_chopin import UPPER, LOWER, bar_events, SLOTS, nm

BASS_SLOTS = (0, 12, 24, 36)   # one root per dotted-quarter group


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


def cat_lines(lines):
    return ',\n'.join(lines)


HEAD = '''-- Nocturne — techno after Chopin's Nocturne Op. 9 No. 2
-- 140 BPM · the complete 37-bar Mutopia transcription (Chopin, 1833; edition
-- by Renato Biolcati Rinaldi, Mutopia-2014/12/18-1590, CC BY-SA 3.0 — source
-- G. Schirmer, New York, 1881, from Library of Congress scans). Every note is
-- decoded from that edition's MIDI, not invented. The right hand is the tune,
-- the left hand's broken chords are the keys, and the low note of each
-- dotted-quarter group is the bass. The tune is transposed down one octave
-- for a warmer register; everything else is at its written pitch.
--
-- Mapping: one score 32nd = one Tidal 16th, so a score eighth becomes a
-- quarter and one 12/8 score bar becomes 48 slots = three Tidal cycles.
-- One mini-notation line below is one score bar (three Tidal cycles, ~5.1 s).
-- Kit phrases run on a 4-cycle grid, so the two realign every four score bars.
-- A section's lines are one editor paragraph: C-RET evaluates all its streams
-- together on the downbeat.
--
-- Form follows the score: A (1-8), A' (9-16), A'' (17-24), Coda (25-31),
-- then the written-out cadenza and final chord (32-37). ~111 cycles, ~3 min.
--
-- Gotchas: reverb size <= 0.9; `amp` is linear (prefer it to `gain`). Mini-
-- notation accidentals are `s`/`f` (ef4, bf3), never `#`. Project synth voices
-- take `note`; sample voices take `speedAt`. juno:7 is C3, moog:3 is G1.
-- tech: 0 closed hh, 5 kick1, 7 open hh, 11 snare1; odx:11 is the crash.

glideBpm 140 30

-- ---------------------------------------------------------------------------
-- Reused voices. Everything used once stays inline at its section. Keep this
-- whole block one paragraph: C-RET evaluates the paragraph at point.
-- ---------------------------------------------------------------------------
let
  -- Kit voices; each section writes its own phrase and re-enters d1/d2.
  kickOn :: Pattern String -> ControlPattern
  kickOn p = s p # amp 1.05 # room 0.04 # size 0.12
  hatsOn :: Pattern String -> ControlPattern
  hatsOn p = s p # amp "3.6 2 2.6 2" # hpf 500 # room 0.05 # size 0.14
  clapOn :: Pattern String -> ControlPattern
  clapOn p = s p # amp 0.6 # room 0.2 # size 0.36
  openOn :: Pattern String -> ControlPattern
  openOn p = s p # amp 0.7 # hpf 350 # room 0.12 # size 0.24 # pan 0.56
  --
  -- A kit: four on the floor with a fourth-bar ghost tag. Shared by A and A''.
  kickA :: ControlPattern
  kickA = kickOn (cat [
    "tech:5*4",
    "tech:5*4",
    "tech:5*4",
    "tech:5 ~ ~ ~ tech:5 ~ ~ ~ tech:5 ~ tech:5 ~ tech:5 ~ tech:5 ~"])
  hatsA :: ControlPattern
  hatsA = hatsOn (cat [
    "tech:0*16",
    "tech:0*16",
    "tech:0*16",
    "tech:0*32"])
  clap :: ControlPattern
  clap = clapOn "~ ~ cp:0 ~ ~ ~ cp:0 ~"
  openHat :: ControlPattern
  openHat = openOn "~ ~ ~ ~ ~ ~ ~ tech:7"
  crash :: ControlPattern
  crash = s "odx:11" # amp 0.5 # hpf 500 # room 0.35 # size 0.6
  --
  -- Sample voices. `speedAt` only cares about intervals, so the base note
  -- names the sample's natural pitch. Score first in every `#` chain: `#`
  -- takes whole/steps from the left, so `s` first would give each note a
  -- bar-length whole and kill articulation (see boot/BootTidal.hs).
  subAt :: Pattern Note -> ControlPattern
  subAt p = speedAt "g1" p # s "moog:3"
      # sustain 0.5 # release 0.15 # lpf 280 # lpq 0.2 # amp 1.5
  keysAt :: Pattern Note -> ControlPattern
  keysAt p = speedAt "c3" p # s "juno:7"
      # sustain 0.18 # release 0.3 # lpf 2600 # room 0.4 # size 0.55 # amp 0.42
  --
  -- Project synth voices. `note` is MIDI; `n` would get SuperDirt's offset.
  -- The tune is boosted well above the kit and breathes through its rests;
  -- the earlier Giselle attempt buried it at amp 1 with a 0.14 s sustain.
  leadAt :: Pattern Note -> ControlPattern
  leadAt p = note (p - 12) # s "hedge_whistle"
      # pF "breath" 0.1 # pF "vib" 5 # pF "depth" 0.012
      # attack 0.04 # sustain 0.7 # release 0.4
      # room 0.4 # size 0.6 # amp 3
  padAt :: Pattern Note -> ControlPattern
  padAt p = note p # s "hedge_pad"
      # sustain 2.4 # amp 0.38 # room 0.5 # size 0.62
'''


def section(title, comment, b1, b2, kit, streams):
    lines = ['-- ' + title]
    lines.extend('--    ' + c for c in comment)
    lines.extend(kit)
    for dn, fn, extra in streams:
        body = cat_lines(fn(b1, b2))
        if extra:
            lines.append('d%d $ %s (cat [\\n%s]) %s' % (dn, '', body, extra))
        else:
            lines.append('d%d $ %s (cat [\\n%s])' % (dn, '', body))
    return '\n\n'.join(lines)


def emit_stream(dn, fn, b1, b2, voice):
    return 'd%d $ %s (cat [\n%s])' % (dn, voice, cat_lines(fn(b1, b2)))


def main():
    out = [HEAD]

    def lead(b1, b2):
        return [voice_line(UPPER, b) for b in range(b1, b2 + 1)]

    def keys(b1, b2):
        return [voice_line(LOWER, b, drop_bass=True) for b in range(b1, b2 + 1)]

    def bass(b1, b2):
        return [voice_line(LOWER, b, slots=set(BASS_SLOTS)) for b in range(b1, b2 + 1)]

    sections = [
        ('1. A theme — score bars 1-8',
         ['the tune in E-flat over broken chords. Full band: the A kit, backbeat,',
          'bass roots and an E-flat pad. Hold eight Tidal cycles... two passes.'],
         1, 8,
         ['d1 kickA', 'd2 hatsA', 'd5 $ clap', 'd6 openHat', 'd9 $ slow 8 $ crash'],
         [(3, bass, 'subAt'), (4, keys, 'keysAt'), (7, lead, 'leadAt'),
          (8, lambda a, b: ['  "[ef3,g3,bf3]"'] * (b - a + 1), 'padAt')]),

        ('2. A varied — score bars 9-16',
         ['the same theme with a Busy middle and a Tempo-I return at bar 11.',
          'The pad drops; the kit moves to the score\'s 2/4 pulse.'],
         9, 16,
         ['d8 silence', 'd5 silence', 'd6 silence', 'd9 silence',
          'd1 $ kickOn (cat [\n'
          '  "tech:5 ~ ~ ~ ~ ~ ~ ~ tech:5 ~ ~ ~ ~ ~ ~ ~",\n'
          '  "tech:5 ~ ~ ~ ~ ~ ~ ~ tech:5 ~ ~ ~ ~ ~ ~ ~",\n'
          '  "tech:5 ~ ~ ~ ~ ~ ~ ~ tech:5 ~ ~ ~ tech:5 ~ ~",\n'
          '  "tech:5 ~ ~ ~ tech:5 ~ ~ ~ tech:5 ~ ~ ~ tech:5 ~ ~ ~"])',
          'd2 $ hatsOn (cat [\n'
          '  "tech:0 ~ tech:0 ~ tech:0 ~ tech:0 ~ tech:0 ~ tech:0 ~ tech:0 ~ tech:0 ~",\n'
          '  "tech:0 ~ tech:0 ~ tech:0 ~ tech:0 ~ tech:0 ~ tech:0 ~ tech:0 ~ tech:0 ~",\n'
          '  "tech:0*32",\n'
          '  "tech:0 ~ tech:0 ~ tech:0 ~ tech:0 ~ tech:0 ~ tech:0 ~ tech:0 ~ tech:0 ~"])'],
         [(3, bass, 'subAt'), (4, keys, 'keysAt'), (7, lead, 'leadAt')]),

        ('3. A doubled — score bars 17-24',
         ['the most ornamented pass, with the full A kit and backbeat back.',
          'One pass.'],
         17, 24,
         ['d1 kickA', 'd2 hatsA', 'd5 $ clap', 'd6 openHat'],
         [(3, bass, 'subAt'), (4, keys, 'keysAt'), (7, lead, 'leadAt'),
          (8, lambda a, b: ['  "[ef3,g3,bf3]"'] * (b - a + 1), 'padAt')]),

        ('4. Coda — score bars 25-31',
         ['the written Coda: new material over a stretto, with the kit building',
          'from the 2/4 pulse through 4/4 to an eighth-note roll into the cadenza.'],
         25, 31,
         ['d8 silence',
          'd1 $ kickOn (cat [\n'
          '  "tech:5 ~ ~ ~ ~ ~ ~ ~ tech:5 ~ ~ ~ ~ ~ ~ ~",\n'
          '  "tech:5 ~ ~ ~ tech:5 ~ ~ ~ tech:5 ~ ~ ~ tech:5 ~ ~ ~",\n'
          '  "tech:5 ~ tech:5 ~ tech:5 ~ tech:5 ~ tech:5 ~ tech:5 ~ tech:5 ~ tech:5 ~",\n'
          '  "tech:5 ~ ~ ~ tech:5 ~ ~ ~ tech:5 ~ ~ ~ tech:5 ~ ~ ~",\n'
          '  "tech:5*8",\n'
          '  "tech:5*16",\n'
          '  "tech:5*16"])',
          'd2 $ hatsOn (cat [\n'
          '  "tech:0 ~ tech:0 ~ tech:0 ~ tech:0 ~ tech:0 ~ tech:0 ~ tech:0 ~ tech:0 ~",\n'
          '  "tech:0*16",\n'
          '  "tech:0*16",\n'
          '  "tech:0*16",\n'
          '  "tech:0*32",\n'
          '  "tech:0*32",\n'
          '  "tech:0*32"])'],
         [(3, bass, 'subAt'), (4, keys, 'keysAt'), (7, lead, 'leadAt')]),

        ('5. Cadenza and final — score bars 32-37',
         ['the written-out cadenza, the repeated final chord and the fermata.',
          'The kit falls away; the pad holds and the final fade is the only one.'],
         32, 37,
         ['d1 silence', 'd2 silence', 'd5 silence', 'd6 silence', 'd4 silence', 'd3 silence'],
         [(7, lead, 'leadAt'),
          (8, lambda a, b: ['  "[ef3,g3,bf3]"'] * (b - a + 1), 'padAt')]),
    ]

    for title, comment, b1, b2, kit, streams in sections:
        out.append('-- ' + title)
        out.extend('--    ' + c for c in comment)
        out.extend(kit)
        for dn, fn, voice in streams:
            out.append(emit_stream(dn, fn, b1, b2, voice))
        out.append('')
    out.append('fadeSilence 8 [8]\n')
    open(ROOT / 'tracks' / 'techno' / 'nocturne.tidal', 'w').write('\n'.join(out))
    print('wrote tracks/techno/nocturne.tidal')


if __name__ == '__main__':
    main()
