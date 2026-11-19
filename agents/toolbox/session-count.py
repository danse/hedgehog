#!/usr/bin/env python3
"""Tally sessions per track from the git log.

A session is approximated by a commit that touched a track's `.tidal` file.
Multi-file tracks (`tracks/<name>/00-setup.tidal`, etc.) count once per commit,
however many of their files changed. Run from anywhere in the repository.

Usage:
  agents/toolbox/session-count.py [--grep PATTERN] [--limit N]

Options:
  --grep PATTERN   only count commits whose subject matches PATTERN, e.g.
                   `--grep session` for the terse session commits
  --limit N        show only the top N tracks (default: all)
"""
import argparse
import collections
import subprocess

GENRES = {'ambient', 'techno', 'dance'}


def track_of(path):
    """Return the track name for a tracked .tidal path, else None."""
    parts = path.strip().split('/')
    if len(parts) < 2 or parts[0] != 'tracks' or not path.endswith('.tidal'):
        return None
    if len(parts) == 2:
        return parts[1][:-6]
    return parts[1] if parts[1] not in GENRES else parts[2][:-6]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--grep', metavar='PATTERN',
                    help='only count commits whose subject matches PATTERN')
    ap.add_argument('--limit', type=int, metavar='N', help='show only the top N tracks')
    args = ap.parse_args()

    cmd = ['git', 'log', '--pretty=format:%H', '--name-only']
    if args.grep:
        cmd.append('--grep=' + args.grep)
    out = subprocess.check_output(cmd, text=True)

    counts = collections.Counter()
    current = set()
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        if len(line) == 40 and all(c in '0123456789abcdef' for c in line):
            for name in current:
                counts[name] += 1
            current = set()
        else:
            name = track_of(line)
            if name:
                current.add(name)
    for name in current:
        counts[name] += 1

    rows = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    if args.limit:
        rows = rows[:args.limit]
    width = max((len(name) for name, _ in rows), default=0)
    for name, n in rows:
        print('%3d  %-*s' % (n, width, name))
    print('%3d  %s' % (len(counts), 'tracks'))


if __name__ == '__main__':
    main()
