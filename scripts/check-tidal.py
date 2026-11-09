#!/usr/bin/env python3
"""Turn blank-line-separated .tidal blocks into GHCi :{ ... :} commands.

Lets you syntax-check a track without a running SuperDirt: pipe the output into
ghci and the expressions evaluate while their OSC is dropped.
"""
import sys

for path in sys.argv[1:]:
    print(f"-- ===== {path}")
    blocks, cur = [], []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if line.strip() == "":
                if cur:
                    blocks.append(cur)
                    cur = []
            else:
                cur.append(line)
    if cur:
        blocks.append(cur)

    for block in blocks:
        code = [l for l in block if l.strip() and not l.strip().startswith("--")]
        if not code:
            continue
        print(":{")
        print("\n".join(block))
        print(":}")
