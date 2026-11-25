# Making of

Source scores and the scripts that decoded them into the score-based
tracks. Paths are relative to this folder, so none of this depends on `/tmp`.
General-purpose helper scripts live in the sibling [`../toolbox/`](../toolbox/).

## Scores

| File | Source | Rights |
|---|---|---|
| `scores/giselle.ly`, `scores/giselle.mid` | Adam, *Pas de deux (1er acte)*, "New arrangement" typeset by Laurence Sardain, Mutopia-2006/12/22-897 | Placed in the public domain by the typesetter |
| `scores/chopin_nocturne_op9_n2.ly`, `.mid`, `-a4.pdf` | Chopin, Nocturne Op. 9 No. 2 (1833), edition by Renato Biolcati Rinaldi, Mutopia-2014/12/18-1590; from G. Schirmer, New York, 1881 scans at the Library of Congress | © 2014 Renato Biolcati Rinaldi, CC BY-SA 3.0 |
| `scores/pachelbel_canon_per_3_violini_e_basso.mid` | Pachelbel, *Canon per 3 Violini e Basso* (1694), Mutopia-2015/09/02-2047, typesetting © 2015 Michael Fischer v. Mollard, source IMSLP; read with `scripts/midi-reader` | CC BY 4.0 |
| `scores/melos.mid` | Four-bar LilyPond export, three labelled voices, read with `scripts/midi-reader` | User-produced; no external rights |
| `scores/salem.midi` | Ten-bar LilyPond 2.24.4 export titled "Test", four labelled voices on a 60-step/bar grid, read with `scripts/midi-reader --steps 60 --bars 10` (and `--gates --bars 10` for the onset grid) | User-produced; no external rights |

The track headers carry the same credits. Keep them when reusing the scores.

## Scripts

| Script | Status |
|---|---|
| `decode_chopin.py` | Current. Turns the Chopin MIDI into Tidal mini-notation; imported by both Chopin generators. |
| `make_pas_de_deux.py` | Current single-section transcription. Its header predates the later gotchas-pointer edit. |
| `make_ambient_nocturne.py` | Stale. It regenerates the original ambient track; the live file has since gained `glideBpm 40 30`, `resetCycles`, a merged coda/cadenza ending in `hush`, and header edits. |
| `make_nocturne.py` | Historical. Generated the techno nocturne, which has since been deleted. |
| `make_giselle_sections.py` | Superseded four-section version; writes the old `tracks/techno/giselle.tidal` name. |

**Do not run these over the tracks**: they write the whole file from scratch and
would lose later hand edits. Use them as a record of how the transcriptions were
derived, or copy their output and reapply the edits.

The reusable audio analyser lives in [`scripts/analyse-audio.py`](../../scripts/analyse-audio.py),
not here.
