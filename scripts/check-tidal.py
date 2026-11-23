#!/usr/bin/env python3
"""Turn .tidal files into GHCi input, splitting top-level statements.

Adjacent top-level expressions are emitted one at a time (GHCi's :{ ... :}
accepts one expression group, not several).  Multi-line single expressions,
`let` blocks and indented continuations are wrapped in :{ ... :}.

Every emitted source line carries a LINE pragma with its original line number,
so GHCi reports errors against the .tidal file instead of <interactive>.

Lets you syntax-check a track without a running SuperDirt: pipe the output into
ghci and the expressions evaluate while their OSC is dropped.
"""
import re
import sys

CONTINUATION_RE = re.compile(
    r"^[ \t]*(?:#|\$|\.|\||,|[\[\](){}]|>|=|<-)")
STRONG_START_RE = re.compile(
    r"^[ \t]*(?:d[0-9]+|xfadeIn|xfade|fadeIn|fadeOut|setbpm|hush)(?:[ \t]|$)")
LET_RE = re.compile(r"^[ \t]*let(?:[ \t]|$)")


def indent(line):
    """Return the indentation width, with tabs advancing to the next 8th column."""
    col = 0
    for ch in line:
        if ch == " ":
            col += 1
        elif ch == "\t":
            col += 8 - (col % 8)
        else:
            break
    return col


def is_blank(line):
    return line.strip() == ""


def is_comment(line):
    return line.lstrip().startswith("--")


def base_indent(lines):
    widths = [indent(l) for l in lines
              if not is_blank(l) and not is_comment(l)]
    return min(widths) if widths else 0


def group_statements(lines):
    """Split (line number, text) pairs into statement groups."""
    base = base_indent([text for _, text in lines])
    groups, current, pending_comments = [], [], []
    in_let = False

    for lineno, line in lines:
        if is_blank(line):
            continue
        if is_comment(line):
            if current and (in_let or indent(line) > base):
                current.append((lineno, line))
            else:
                pending_comments.append((lineno, line))
            continue

        starts_statement = (
            not CONTINUATION_RE.match(line)
            and (indent(line) <= base
                 or (not in_let and STRONG_START_RE.match(line))))

        if starts_statement:
            if current:
                groups.append(current)
            current = pending_comments + [(lineno, line)]
            pending_comments = []
            in_let = bool(LET_RE.match(line))
        elif current:
            current.append((lineno, line))
        else:
            # Orphan indented line: start a group with it anyway.
            current = pending_comments + [(lineno, line)]
            pending_comments = []
            in_let = bool(LET_RE.match(line))

    if current:
        groups.append(current)
    return groups


for path in sys.argv[1:]:
    print(f"-- ===== {path}")
    with open(path, encoding="utf-8") as fh:
        lines = [(n, line.rstrip("\n")) for n, line in enumerate(fh, 1)]

    for block in group_statements(lines):
        if not any(not is_comment(text) for _, text in block):
            continue
        print(":{")
        for lineno, text in block:
            print('{-# LINE %d "%s" #-}' % (lineno, path))
            print(text)
        print(":}")
