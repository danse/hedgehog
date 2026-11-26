#!/usr/bin/env python3
"""DEPRECATED — kept for historical interest only.

This was the local ontology browser. It records the query interface we
validated while developing the decks, but it assumes cards hold
`tracks/...tidal` paths; the decks now carry bare track names. The tag-folder
READMEs it read vocabulary from have been folded into `notes/ontology/README.md`
too, so it is not a working browser. Its queries live upstream in `../dam`'s
`dam-query` (agents branch). Do not extend or rely on this script; new query
work belongs there.
"""
import argparse
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ONTOLOGY = ROOT / "notes" / "ontology"
SCHEMES = ("spines", "dimensions")
VOCAB_RE = re.compile(r"^\|\s*`([^`]+)`\s*\|\s*([^|]+?)\s*\|")
CARD_RE = re.compile(r"\n\s*\n")


def deck_dir(scheme):
    return ONTOLOGY / scheme


def load(scheme="spines"):
    directory = deck_dir(scheme)
    vocab = {}
    readme = directory / "README.md"
    if readme.exists():
        for line in readme.read_text(encoding="utf-8").splitlines():
            m = VOCAB_RE.match(line)
            if m:
                vocab[m.group(1)] = m.group(2).strip()

    rows = []
    for path in sorted(directory.iterdir()):
        if path.name == "README.md" or not path.is_file():
            continue
        tags = tuple(path.name.split())
        if scheme == "dimensions":
            # Root labels come from the deck filenames; there is no table to
            # keep in sync, and mode still lives only in the track headers.
            for tag in tags:
                vocab.setdefault(tag, "Root area; mode stays in the track header.")
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


def check(vocab, rows, scheme):
    indexed = [track for track, _ in rows]
    actual = {str(path.relative_to(ROOT))
              for path in (ROOT / "tracks").glob("*/*.tidal")
              if not path.name.startswith(".")}  # ignore Emacs lock files
    if scheme == "spines":
        # One spine card per track.
        duplicate = sorted(t for t, n in Counter(indexed).items() if n > 1)
    else:
        # Modulated tracks legitimately carry several roots; only the same
        # track twice under one root is a duplicate card.
        pairs = [(track, tag) for track, tags in rows for tag in tags]
        duplicate = sorted({t for (t, _), n in Counter(pairs).items() if n > 1})
    problems = {
        "missing": sorted(actual - set(indexed)),
        "stale": sorted(set(indexed) - actual),
        "duplicate": duplicate,
        "unknown tag": sorted({t for _, tags in rows for t in tags}
                              - set(vocab)),
        "unused tag": sorted(t for t in vocab
                             if not any(t in tags for _, tags in rows)),
    }
    for name, items in problems.items():
        print("%-12s %s" % (name + ":", ", ".join(items) or "-"))
    directory = deck_dir(scheme)
    print("checked %d tracks in %d decks" % (len(rows),
          len([p for p in directory.iterdir()
               if p.is_file() and p.name != "README.md"])))
    return any(problems.values())


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("labels", nargs="*", metavar="LABEL",
                    help="show tracks carrying all these labels")
    ap.add_argument("--scheme", choices=SCHEMES, default="spines",
                    help="tag deck to browse (default: spines)")
    ap.add_argument("--track", metavar="NAME",
                    help="show labels for one track (stem or path)")
    ap.add_argument("--tags", action="store_true", dest="list_tags",
                    help="list the vocabulary with usage counts")
    ap.add_argument("--check", action="store_true",
                    help="verify coverage and tag consistency")
    args = ap.parse_args()

    vocab, rows = load(args.scheme)
    if args.check:
        raise SystemExit(1 if check(vocab, rows, args.scheme) else 0)
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
