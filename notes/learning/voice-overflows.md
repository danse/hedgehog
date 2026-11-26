# Voice overflows

A **voice overflow** is a stream left playing from the outgoing track when a
live coder lands on a track that does not write all of its seats.

Tidal stream IDs are global. Evaluating `d1`, `d2`, … in the incoming track
only rewrites the IDs that appear. Every other ID keeps its last pattern until
it is rewritten, faded, or `hush`ed. So a five-voice track landed over an
eight-voice track leaves three voices from the first one in the mix:

```
overflow = seats(outgoing) \ seats(incoming)
```

The live coder is stuck in the outgoing track's bubble: the incoming texture
arrives, but the high-numbered leftovers keep colouring it. It is hard to tell
which IDs are still live by ear, because `dN` numbers follow the order streams
first entered, not their musical importance — and a stream can be present in
the stream map but already faded to silence.

## Calculating before a landing

1. List the IDs the **incoming** track writes. Include `dN`, `multi`,
   `fadeMulti`, `xfadeIn`, `clutchIn`, `clear` and `fadeSilence` targets — a
   fade to silence still rewrites that stream.
2. List the IDs the **outgoing** track currently holds. If you are mid-set,
   read the section you are in, not just the header: a track may have added or
   faded voices since its first paragraph.
3. Subtract. The remainder is the overflow set.
4. Check whether the outgoing track has already scheduled fades for any of
   them. A voice that is on its way out does not need another fade.
5. Decide: hold it, fade only the overflow, or put a barrier before the
   incoming track.

`cycleD <secs>` from `boot/BootTidal.hs` is the ear check: it solos each active
stream in turn and prints its ID, so a suspected overflow can be confirmed
without guessing. It runs in the REPL; printout says to interrupt with
`C-c C-i`, which unsoloes the current voice before returning to the prompt.

## Handling the overflow

- **Hold it.** At a double-blank landing the leftover tail may be exactly what
  makes the handover interesting. No action needed.
- **Fade only the overflow.** This is usually the best move: it keeps the
  outgoing track's character while removing the streams the incoming track
  does not know about.

  ```haskell
  fadeSilence 8 [6,7,8]
  ```

  or, if the voices need different destinations:

  ```haskell
  multi xfadeIn 8 [(6, silence), (7, pianoMotif), (8, silence)]
  ```

- **Put a barrier before the incoming track.** `clearAll 4` fades all twelve
  seats to silence, so nothing can overflow. The cost is that it throws away
  the outgoing tail and makes the mix less interesting — useful for a hard
  reset, not as the default handover.
- **`hush`** is the extreme version: everything stops. It guarantees a clean
  slate but loses the landing entirely.

Prefer the selective fade. A barrier is a statement that the previous track is
over; a selective fade says the new track is entering over a still-living one.

## Worked examples

`yard` uses seats 1–8 (kick, bass, hats, chord stab, woodblock/wind, piano,
dub stab, sax/breath). `klang` uses 1–5 (pad, air, bass, whistle, answer).
Landing klang over a running yard therefore overflows:

```
overflow = {1..8} \ {1..5} = {6,7,8}
```

That is yard's piano, dub stab and d8 voice. If yard's coda has not already
faded them, `fadeSilence 8 [6,7,8]` after klang's bed is up gives a clean
handover without a `clearAll` barrier.

Similarly, `quema` uses 1–10 and `oculus` uses 1–5, so a quema → oculus landing
leaves seats 6–10 (conga, lead, open hat, rim/llamador, maracas) sounding.
Oculus's own outro line `fadeSilence 8 [2,3,4,6]` counts d6 as rewritten even
though that seat is empty in the track.

## Asking an agent

An agent can do this subtraction from the two files in minutes. Useful phrasings:

- "What overflows if I land klang over yard?"
- "Knowing where I was before, I'm stuck in an overflow at the middle of
  neon-alloy — which numbers?"
- "Which salem seats survive a landing on neon-alloy?"

Overflow is a relation, not a property of one file. The exact numbers need the
outgoing side: the previous track and section from the session context, or a
fresh `list`/`cycleD` output. In an ongoing session, "knowing where I was
before" is enough — the agent already has the earlier track in view and can do
the subtraction without being told again.

From neon-alloy's file alone we can still say: the chorus (§3) writes 1–7 and
does not touch d8; the break (§4) claims d8. So a chorus landing over yard
leaves yard's d8 (sax/breath) overflowing, while one over quema leaves d8 plus
d9 and d10, which neon-alloy never writes at all. The agent can propose the
minimal fade line; whether the leftovers are worth keeping is still a decision
for your ears.
