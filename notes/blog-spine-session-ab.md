# Draft — Axes, not folders

*Not posted. Material for a short post on live coding and software engineering:
the spine/dimension/session split, the new `matrix` spine, and the `-- from`
A/B fallback.*

A live set generates three different questions, and no single folder answers all
of them. Before a piece: what can I *do* with it while it is running? During a
handover: where does it sit relative to the key and tempo of what just played?
After the night: what actually happened, in what order? Hedgehog keeps three
small kinds of text for those three questions, and the interesting part is how
little machinery they need.

## Three axes

A **spine** describes a live-coding affordance. `groove`, `loop`, `long-form`,
`bed`, `score`, `network`, `matrix`: these say what a track gives you to work
with, not what it is called in a programme. A `groove loop` track is a rhythm
bed over a short harmony you can keep reshaping by swapping seats. Adding
`matrix` this week was less like adding a genre and more like naming an
interface: a grid of movements by voices.

A **dimension** is one parametric fact, currently just the root. `key:A`,
`key:E`, `key:F#` are separate cards because a modulated track visits more than
one root. Mode stays in the track header, where the exact chords live. This is
deliberately not a taxonomy: tags overlap, none is primary, and the vocabulary
changes only when the affordance changes.

A **session** is an ordered narrative. `ladder.md` records nine rungs from
ambient into dance and back to the grid. It says, for example, that strobe was
taken whole tone up from the previous E anchor, that its doors landing let the
break arrive, and that `grin` followed with E minor turning Dorian. The set of
tags can tell you which tracks share an affordance; only the session can tell
you why one followed another.

Keeping these apart is the whole trick. If the spine deck tried to hold
sequence, it would rot after the first night. If the session tried to hold
definitions, it would become a second ontology nobody maintained. If the root
were folded into the spine name, every modulation would need a new label. Three
plain-text decks and two short guides do the work that a database schema would
usually claim.

## Adding a spine: matrix

Most spines name a shape you can hear. `matrix` names an interface you can call.
The first two tracks that use it, `lattice` and `riddle`, are far apart in tempo
and palette — one ambient, one 140 BPM and noisy — but both are grids. A
movement is a row of seats, and each cell is `Silent`, `Score` or `Optional`. A
`Score` is the band the row brings with it. An `Optional` is a colour waiting on
the table; a named voice call can bring it in without changing the row.

The rule that makes this usable live is: the matrix chooses *what*, the
transition chooses *how*. `mPlay` announces the row and returns every named seat
as a transition-ready pair. For a scored seat it returns the pattern; for an
optional, silent or omitted seat it returns `silence`. Entering a row therefore
clears what the row does not score, but it does not choose a fade. The live coder
puts a voice under `p`, `clutchIn`, `xfadeIn` or `attacks`. A call such as
`clutchIn 9 8 $ chip tangle` is the sentence that chooses the entry; `chip
tangle` by itself is only a pattern.

That split matters because the same cell can arrive differently. A bell can be
attacked, a stab clutched, a hiss faded. If a voice call buried its own envelope,
the grid would decide the character of every entrance and the live coder would
only be choosing a name. Keeping the envelope at the call site leaves the
decision where the ear is. It also makes an optional voice a mix problem: if a
colour is going to enter and leave, it has to be audible when it appears. That
belongs in the track's levels, not in the cell.

Names are part of the interface too. Movement rows are `opening`, `hollow`,
`scatter`, `mirror` — short descriptive labels, not `a`, `b`, `c`. `mOptionals`
prints what a row is offering in the same words. A voice accessor is built with
`mkVoice` at one seat, and that seat is both the cell key and the destination
stream, so a colour keeps its `dN` as the row changes. A live call reads like a
sentence about the music rather than a lookup in a spreadsheet.

`camel`, grown from a lechuga session, borrowed the interface from `riddle` and
`quema`'s loop. That is the useful test of a spine: a new piece can use the same
grid without inheriting the old piece's sounds. The grid stores facts; the call
site stores intent.

## The fallback lives in the edit

The same preference for small, local structure shows up in the tracks
themselves. A live change carries its old value in a trailing comment:

```haskell
glideBpm 104 40 -- from 100
...
# amp 0.24 -- from amp 0.26
```

The opening tempo that sets a track's home does not need an annotation; only a
change does. That one line turns a tempo move into a reversible decision. The
person who arrives at the file next — often the same person, an hour later —
does not have to reconstruct what was tried. They can A/B immediately, and the
fallback is not in a chat log or a memory of the set.

This is version control in miniature, but it is not a diff. A diff describes
what changed between two commits; the inline fallback describes what the
*current* line replaced while someone was listening. It is closer to a
well-labelled knob than to history, and it stays next to the sound it affects.

## What the blank line does

A track paragraph is a live action or a setup block. Two blank lines between
paragraphs mean a landing: the texture is complete there and can hold. The
live coder can dwell on it, detach to bring in another intro, or end the set
there. We used to write `-- Landing: the full band can hold here` above the gap.
Those comments are gone.

Removing them was not tidying. The gap already meant what the sentence said,
and Emacs already treats a double blank as a paragraph boundary, so the comment
made the paragraph jump less comfortable without adding information. The format
carries the structure; prose would only duplicate it. The same reasoning puts
shared gotchas in one learning note and track-specific facts in headers, rather
than repeating rules in every file.

## Why this is software engineering

The pattern is familiar enough to be boring in a codebase: separate stable
vocabulary from runtime sequence, keep metadata beside the thing it describes
but not inside its interface, and make the previous state visible at the point
of change. What is different here is the timescale. A live coder reads these
files while sound is coming out of the speakers. There is no time to join
tables, no patience for a schema, and no appetite for a tool that knows more
than the ear.

So the metadata stays deliberately dumb. A card is a track name in a
blank-line-separated file. A session is a numbered list with a sentence of
context per rung. A fallback is a comment on the same line. None of it tries to
be authoritative; all of it survives a clone and a quiet afternoon.

The post's small claim is that this is a design virtue, not a lack of
ambition. A live instrument needs interfaces that can be read at a glance and
changed without ceremony. When the axes are honest — what it affords, what root
it visits, what happened — you can browse them separately and let the music
decide how they combine. The arrangement is not in the ontology. It is in the
room.
