#!/usr/bin/env python3
"""Browse the spine labels stored as dam decks in notes/ontology/spines/.

The decks are the canonical copy: tags are the words in each filename and
each blank-line-separated card is one track path. Track headers are not
duplicated.
"""
import argparse
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPINES = ROOT / "notes" / "ontology" / "spines"

VOCAB_RE = re.compile(r"^\|\s*`([a-z][a-z-]*)`\s*\|\s*([^|]+?)\s*\|")
CARD_RE = re.compile(r"\n\s*\n")


def load():
    vocab = {}
    readme = (SPINES / "README.md").read_text(encoding="utf-8")
    for line in readme.splitlines():
        m = VOCAB_RE.match(line)
        if m:
            vocab[m.group(1)] = m.group(2).strip()

    rows = []
    for path in sorted(SPINES.iterdir()):
        if path.name == "README.md" or not path.is_file():
            continue
        tags = tuple(path.name.split())
        for card in CARD_RE.split(path.read_text(encoding="utf-8")):
            track = next((line.strip() for line in card.splitlines()
                          if line.strip()), "")
            if track:
                rows.append((track, tags))
    return vocab, rows


def show(vocab, rows):
    for label in sorted(vocab):
        names = [Path(track).stem for track, tags in rows if label in tags]
        print("%-14s %s" % (label + ":", ", ".join(sorted(names)) or "-"))


def show_counts(vocab, rows):
    counts = {label: 0 for label in vocab}
    for _, tags in rows:
        for tag in tags:
            counts[tag] = counts.get(tag, 0) + 1
    for label, meaning in vocab.items():
        print("%-14s %2d  %s" % (label, counts.get(label, 0), meaning))


def check(vocab, rows):
    indexed = [track for track, _ in rows]
    actual = {str(path.relative_to(ROOT))
              for path in (ROOT / "tracks").glob("*/*.tidal")
              if not path.name.startswith(".")}  # ignore Emacs lock files
    problems = {
        "missing": sorted(actual - set(indexed)),
        "stale": sorted(set(indexed) - actual),
        "duplicate": sorted(t for t, n in Counter(indexed).items() if n > 1),
        "unknown tag": sorted({t for _, tags in rows for t in tags}
                              - set(vocab)),
        "unused tag": sorted(t for t in vocab
                             if not any(t in tags for _, tags in rows)),
    }
    for name, items in problems.items():
        print("%-12s %s" % (name + ":", ", ".join(items) or "-"))
    print("checked %d tracks in %d decks" % (len(rows),
          len([p for p in SPINES.iterdir()
               if p.is_file() and p.name != "README.md"])))
    return any(problems.values())


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("labels", nargs="*", metavar="LABEL",
                    help="show tracks carrying all these labels")
    ap.add_argument("--track", metavar="NAME",
                    help="show labels for one track (stem or path)")
    ap.add_argument("--tags", action="store_true", dest="list_tags",
                    help="list the vocabulary with usage counts")
    ap.add_argument("--check", action="store_true",
                    help="verify coverage and tag consistency")
    args = ap.parse_args()

    vocab, rows = load()
    if args.check:
        raise SystemExit(1 if check(vocab, rows) else 0)
    if args.list_tags:
        show_counts(vocab, rows)
        return
    if args.track:
        hits = [(track, tags) for track, tags in rows
                if Path(track).stem == args.track or track.endswith(args.track)]
        if not hits:
            ap.error("no such track in the index: " + args.track)
        for track, tags in hits:
            print("%-34s %s" % (track, " ".join(tags)))
        return
    if args.labels:
        unknown = set(args.labels) - set(vocab)
        if unknown:
            ap.error("unknown label(s): " + ", ".join(sorted(unknown)))
        wanted = set(args.labels)
        hits = [(track, tags) for track, tags in rows if wanted <= set(tags)]
        for track, tags in sorted(hits):
            print("%-34s %s" % (track, " ".join(tags)))
        if not hits:
            print("(no track carries all of those labels)")
        return
    show(vocab, rows)


if __name__ == "__main__":
    main()
