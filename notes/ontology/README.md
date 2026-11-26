# Ontology — tag schemes

Dam decks grouping the set's flat labels. Each subdirectory is a set of tags;
the words in a filename are the tags and each blank-line-separated card is a
track path.

- `spines/` — live-coding affordances: `score`, `loop`, `long-form`, `bed`, …
- `dimensions/` — parametric root tags: `key:A`, `key:F`, `key:F#`, …

A modulated track carries each root it visits: `campina` is `key:A` + `key:D`,
`strobe` is `key:E` + `key:F#`. Mode stays in headers.

Sessions are ordered narratives, not tag decks: see `../sessions/ladder.md`.
A landing is a double-blank hold point inside a track, not a session tag.

These are lightweight ontologies, not taxonomies: tags overlap, none is primary,
and meanings stay stable. Headers own exact tempo, key and seat data; tags never
duplicate it. `agents/toolbox/dam.py` reads either scheme with `--scheme`
(default `spines`); dam tools read any deck.
