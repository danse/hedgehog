# Spines — dam decks

Flat spine labels for browsing the set, stored in dam's plain-text format:
the words in each filename are the tags, and each blank-line-separated card is
one track path. This directory is the canonical copy inside Hedgehog, so a
clone of the set keeps its labels. `agents/toolbox/spines.py` is just a reader;
labels are deliberately not duplicated into track headers.

Browse:

```sh
agents/toolbox/spines.py                  # every label and its tracks
agents/toolbox/spines.py groove loop      # tracks carrying both labels
agents/toolbox/spines.py --track loden    # labels for one track
agents/toolbox/spines.py --tags           # vocabulary with usage counts
agents/toolbox/spines.py --check          # coverage and consistency

dam-read 'notes/spines/*bed*'             # dam's own reader
dam-read 'notes/spines/groove loop'
(cd notes/spines && dam-set-sizes)        # counts by set of tags
```

To change a label, move its card to a differently named file. There is no
separate index to regenerate. Keep one card per track and start each card with
its `tracks/...tidal` path.

## Vocabulary

| Label | Meaning when browsing |
|---|---|
| `bed` | A sustained layer that seats enter over. |
| `drone` | A held root or pedal that anchors the piece. |
| `groove` | A rhythm-first bed; the beat or band pattern is the carrier. |
| `pulse` | A bare metric grid or tick (kick, tapan, clock). |
| `loop` | One short harmonic loop reshaped by seat swaps. |
| `modal-shift` | A key, degree or maqam lift is the formal event. |
| `score` | A written line or motif carries the through-line. |
| `transcription` | A literal reading of an external MIDI or score source. |
| `single-breath` | One uninterrupted span, or a cue-only bed with no fixed arrangement. |
| `long-form` | An extended sectioned arc with landings and detach points. |

`score` is for lines written in this project; `transcription` is reserved for
literal readings of outside sources. Genre folders and BPM are not spines.
