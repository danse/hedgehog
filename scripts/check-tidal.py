#!/usr/bin/env python3
"""Turn .tidal files into GHCi input, splitting top-level statements.

Adjacent top-level expressions are emitted one at a time (GHCi's :{ ... :}
accepts one expression group, not several).  Multi-line single expressions,
`let` blocks and indented continuations are wrapped in :{ ... :}.

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
    """Split LINES into statement groups (lists of lines)."""
    base = base_indent(lines)
    groups, current, pending_comments = [], [], []
    in_let = False

    for line in lines:
        if is_blank(line):
            continue
        if is_comment(line):
            if current and (in_let or indent(line) > base):
                current.append(line)
            else:
                pending_comments.append(line)
            continue

        starts_statement = (
            not CONTINUATION_RE.match(line)
            and (indent(line) <= base
                 or (not in_let and STRONG_START_RE.match(line))))

        if starts_statement:
            if current:
                groups.append(current)
            current = pending_comments + [line]
            pending_comments = []
            in_let = bool(LET_RE.match(line))
        elif current:
            current.append(line)
        else:
            # Orphan indented line: start a group with it anyway.
            current = pending_comments + [line]
            pending_comments = []
            in_let = bool(LET_RE.match(line))

    if current:
        groups.append(current)
    return groups


for path in sys.argv[1:]:
    print(f"-- ===== {path}")
    with open(path, encoding="utf-8") as fh:
        lines = [line.rstrip("\n") for line in fh]

    for block in group_statements(lines):
        if not any(not is_comment(l) for l in block):
            continue
        if len(block) == 1:
            print(block[0])
        else:
            print(":{")
            print("\n".join(block))
            print(":}")
