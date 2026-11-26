# Dimensions — dam decks

Parametric root tags, stored as dam decks like the spines. The words in each
filename are the tags and each blank-line-separated card is one track path.
A modulated track carries each root it visits; mode stays in the track header.

Browse with:

```sh
agents/toolbox/dam.py --scheme dimensions          # every root and its tracks
agents/toolbox/dam.py --scheme dimensions key:A    # tracks in one root
agents/toolbox/dam.py --scheme dimensions --track campina
agents/toolbox/dam.py --scheme dimensions --tags   # roots with counts
agents/toolbox/dam.py --scheme dimensions --check  # coverage and consistency
```

The root vocabulary comes from the deck filenames, so there is no table to
keep in sync. Unlike spines, a track may legitimately appear in several decks.
