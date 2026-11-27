# Ontology — tag schemes

Dam decks grouping the set's flat labels. Each subdirectory is a set of tags;
the words in a filename are the tags and each blank-line-separated card is a
unique `snake_case` track name (`baroque_carnival`). Decks are hand-edited plain
text; tooling only reads and reports, and checks are advisory, not a gate. This
is the canonical copy inside Hedgehog, so a clone of the set keeps its labels.

- `spines/` — live-coding affordances: `score`, `loop`, `long-form`, `bed`, …
- `dimensions/` — parametric root tags: `key:A`, `key:F`, `key:F#`, …

A modulated track carries each root it visits: `campina` is `key:A` + `key:D`,
`strobe` is `key:E` + `key:F#`. Mode stays in headers.

Sessions are ordered narratives, not tag decks; a landing is a double-blank
hold point inside a track, not a session tag.

These are lightweight ontologies, not taxonomies: tags overlap, none is primary,
and meanings stay stable. Headers own exact tempo, key and seat data; tags never
duplicate it. Genre folders and BPM are not tags. The local
`agents/toolbox/dam.py` is deprecated and kept for historical interest; queries
now live in upstream `dam-query`, and plain dam tools read any deck.

## Browsing

`dam-query` is the upstream replacement; pass one deck directory directly:

```sh
# spines
dam-query --tags -- notes/ontology/spines       # every label with counts
dam-query --key loden -- notes/ontology/spines  # labels for one track
dam-query groove loop -- notes/ontology/spines  # tracks carrying both labels
dam-query --check -- notes/ontology/spines      # advisory duplicate keys

# dimensions
dam-query --tags -- notes/ontology/dimensions          # roots with counts
dam-query key:A -- notes/ontology/dimensions           # tracks in one root
dam-query --key campina -- notes/ontology/dimensions   # every root for a track
dam-query --check -- notes/ontology/dimensions         # advisory duplicate keys

# plain dam tools
dam-read 'notes/ontology/spines/*bed*'
dam-read 'notes/ontology/spines/groove loop'
(cd notes/ontology/spines && dam-set-sizes)  # counts by set of tags
```

## Editing decks

To change a label, move its card to a differently named file. There is no
separate index to regenerate. Keep one card per track in `spines/` and start
each card with its track name; in `dimensions/` a track may legitimately appear
in several decks.

## Spines

Spines are a lightweight, flexible ontology of **live-coding affordances**, not
a taxonomy: labels overlap, none is primary, and the vocabulary can grow. Their
meanings stay stable — without that, browsing would only be relative to whoever
filed the tracks. Listening clues follow from those affordances; exact
tempo/key/seat data stays in headers.

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
| `network` | Several equal written lines interlock on long, non-matching cycles; no single carrier, landings where subsets realign. |
| `matrix` | A grid of movements x voices; required scores form the band, optional scores are offered live and launched by named voice calls. |

For `network`, derive unequal long periods from one cell with `slow (p/q)`,
`off` and `iter`; land at subset LCMs rather than the full LCM, which usually
sits past the end. Avoid a drone or pad so no seat becomes a single carrier.

For `matrix`, make each row a `mkMovement` with a short descriptive label,
voice names and `Silent`/`Score`/`Optional` cells; avoid letter names (`a`, `b`,
…) so live calls read by meaning. Define named accessors with `mkVoice`; the
matrix chooses *what*, while `p`, `clutchIn`, `xfadeIn`, `attacks` and `multi`
choose *how*. Pass the same ID to the transition as the seat given to `mkVoice`:
it is both the cell lookup and the destination stream, so a voice keeps one dN
across rows. `mPlay` announces the row and returns a pair for each named seat:
a score brings its pattern; an optional, silent or omitted seat brings `silence`,
so entering a row clears what it does not score. It chooses no fade. The
executable interface is in `notes/matrix-api.tidal`.

`score` is for lines written in this project; `transcription` is reserved for
literal readings of outside sources.

## Dimensions

Dimensions are parametric root tags stored in the same plain-text format. The
root vocabulary comes from the deck filenames, so there is no table to keep in
sync. A modulated track carries each root it visits; mode stays in the track
header.
