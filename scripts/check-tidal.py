#!/usr/bin/env python3
"""Turn .tidal files into GHCi input, splitting top-level statements.

Statement grouping comes from the live Emacs sender (via tidal-groups.sh), so
offline checks and live sends agree.  Each emitted source line carries a LINE
pragma with its original number, so GHCi reports errors against the .tidal file
instead of <interactive>.

Lets you syntax-check a track without a running SuperDirt: pipe the output into
ghci and the expressions evaluate while their OSC is dropped.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GROUPS = ROOT / "scripts" / "tidal-groups.sh"


def group_blocks(path):
    """Return sender groups as lists of (line number, source line)."""
    raw = subprocess.check_output([str(GROUPS), str(path)])
    fields = raw.split(b"\0")
    if len(fields) % 4 != 1 or fields[-1]:
        raise RuntimeError("bad tidal-groups output for %s" % path)
    blocks = []
    for i in range(0, len(fields) - 1, 4):
        text = fields[i + 2].decode("utf-8")
        numbers = [int(n) for n in fields[i + 3].decode().split(",") if n]
        lines = text.splitlines()
        if len(numbers) != len(lines):
            raise RuntimeError("line numbers and text disagree for %s" % path)
        blocks.append(list(zip(numbers, lines)))
    return blocks


def main():
    for path in sys.argv[1:]:
        print(f"-- ===== {path}")
        for block in group_blocks(path):
            print(":{")
            for lineno, text in block:
                print('{-# LINE %d "%s" #-}' % (lineno, path))
                print(text)
            print(":}")


if __name__ == "__main__":
    main()
