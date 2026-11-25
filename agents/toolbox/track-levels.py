#!/usr/bin/env python3
"""Coarse per-track level/energy audit, with a shared inter-track comparison.

This is a *macroscopic* check, not a loudness meter. GHC parses the sender's
statement groups into AST facts; Python keeps the level/energy arithmetic. It
never starts GHCi, SuperDirt, sclang or an OSC clock. For each
stream it takes the loudest section it ever receives, then sums those maxima to
describe the fullest texture the track reaches. Sections are not accumulated:
streams replace one another, so a long track is not louder just because it has
more paragraphs.

Two views share exactly the same measurement core:

  track    one row per track plus the contributing streams
  compare  one row per track, with ratios against the first track

Amplitude is `amp * gain**4 * source`, where `gain` is Tidal's quartic trim and
`source` is the measured full-buffer RMS of the referenced WAV. Synths have no
cheap offline source level here, so they use a nominal 1.0 and are flagged;
`synth-analyser.py` is the tool for diagnosing a specific SynthDef. Energy per
cycle is `amplitude**2 * sounding_seconds * events`, and the reported RMS is
that energy divided by the cycle length and square-rooted. Sounding time uses
`sustain`/`release`/`decay`, pattern holds (`_`), `legato`, and a capped
`room`/`size` reverb tail; all are reduced to representative values and capped
at one cycle. Filters, panning, phase cancellation and true sample envelopes
are deliberately invisible. Your ears still settle the mix.

Usage:
  agents/toolbox/track-levels.py track [options] TRACK ...
  agents/toolbox/track-levels.py compare [options] TRACK ...

Options:
  --all          read every tracks/*/*.tidal file (no TRACK args needed)
  --beats N      quarter-note beats per cycle (default: from header, else 4)
  --no-samples   use nominal source level 1.0 everywhere (fastest)
  --dir PATH     extra sample corpus root, searched before Dirt-Samples
"""
import argparse
import importlib.util
import json
import math
import re
import subprocess
import sys
import wave
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
ANALYSER = ROOT / "scripts" / "analyse-audio.py"
CHECK_TIDAL = ROOT / "scripts" / "check-tidal.py"
TRACK_AST = ROOT / "agents" / "toolbox" / "track-ast"
DIRT = Path.home() / ".local/share/SuperCollider/downloaded-quarks/Dirt-Samples"
LOCAL = ROOT / "samples"

spec = importlib.util.spec_from_file_location("analyse_audio", ANALYSER)
analyse_audio = importlib.util.module_from_spec(spec)
spec.loader.exec_module(analyse_audio)

spec = importlib.util.spec_from_file_location("check_tidal", CHECK_TIDAL)
check_tidal = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_tidal)


NUM_RE = re.compile(r"-?\d+(?:\.\d+)?")
CONTROL_KEYS = ("amp", "gain", "level", "sustain", "release", "decay",
                "attack", "legato", "room", "size", "speed", "rate", "delay")
NON_PATTERN_CALLS = set(CONTROL_KEYS) | {"s", "pF", "chordAt"}
NOTE_RE = re.compile(r"^[a-gA-G][#bsf]?-?\d+$")


@dataclass
class Alias:
    kind: str                  # pattern | voice | control
    body: list
    params: list = field(default_factory=list)


@dataclass
class Voice:
    events: float = 0.0
    energy: float = 0.0
    level_sum: float = 0.0
    dur_sum: float = 0.0
    flags: set = field(default_factory=set)

    def add(self, other):
        self.events += other.events
        self.energy += other.energy
        self.level_sum += other.level_sum
        self.dur_sum += other.dur_sum
        self.flags |= other.flags
        return self

    def level(self):
        return self.level_sum / self.events if self.events > 0 else 0.0

    def dur(self, cycle_sec):
        return self.dur_sum / self.events if self.events > 0 else cycle_sec

    def rms(self, cycle_sec):
        return math.sqrt(self.energy / cycle_sec) if cycle_sec > 0 else 0.0

    def scaled(self, events_factor=1.0, dur_factor=1.0):
        v = Voice(self.events * events_factor,
                  self.energy * events_factor * dur_factor,
                  self.level_sum * events_factor,
                  self.dur_sum * events_factor * dur_factor,
                  set(self.flags))
        return v


@dataclass
class Track:
    path: Path
    bpm: float
    beats: float
    aliases: dict
    statements: list


# --------------------------------------------------------------------------
# GHC AST facts. `track-ast/Facts.hs` parses the sender groups; this side
# reads a small S-expression and keeps all level/energy arithmetic.
# --------------------------------------------------------------------------

def sexpr_tokens(text):
    i, out = 0, []
    while i < len(text):
        ch = text[i]
        if ch.isspace():
            i += 1
        elif ch in "()":
            out.append(ch)
            i += 1
        elif ch == '"':
            j, escaped = i + 1, False
            while j < len(text) and (escaped or text[j] != '"'):
                if escaped:
                    escaped = False
                elif text[j] == "\\":
                    escaped = True
                j += 1
            out.append(json.loads(text[i:j + 1]))
            i = j + 1
        else:
            j = i
            while j < len(text) and not text[j].isspace() \
                    and text[j] not in '()"':
                j += 1
            out.append(text[i:j])
            i = j
    return out


def parse_sexpr(text):
    tokens = sexpr_tokens(text)
    pos = 0

    def read():
        nonlocal pos
        token = tokens[pos]
        pos += 1
        if token == "(":
            items = []
            while tokens[pos] != ")":
                items.append(read())
            pos += 1
            return items
        if token == ")":
            raise ValueError("unexpected ')' in AST fact")
        return token

    value = read()
    if pos != len(tokens):
        raise ValueError("trailing tokens in AST fact")
    return value


def node_kind(node):
    return node[0] if isinstance(node, list) and node else None


def var_name(node):
    return node[1] if node_kind(node) == "var" else None


def app_parts(expr):
    """Return (head, args) for an application spine."""
    if node_kind(expr) == "app":
        return expr[1], expr[2:]
    return expr, []


def walk(node):
    if isinstance(node, list):
        yield node
        for item in node:
            yield from walk(item)


def collect_strings(expr):
    return [node[1] for node in walk(expr) if node_kind(node) == "str"]


def collect_vars(expr):
    return {node[1] for node in walk(expr) if node_kind(node) == "var"}


def find_calls(expr, name):
    for node in walk(expr):
        if node_kind(node) == "app" and var_name(node[1]) == name:
            yield node[2:]


_FACTS_BINARY = None


def facts_binary():
    global _FACTS_BINARY
    if _FACTS_BINARY is None:
        _FACTS_BINARY = subprocess.check_output(
            [str(TRACK_AST / "build.sh")], text=True).strip()
    return _FACTS_BINARY


def ast_facts(blocks):
    groups = [(block[0][0], "\n".join(line for _, line in block))
              for block in blocks if block]
    payload = b"".join(str(lineno).encode() + b"\0" + text.encode() + b"\0"
                       for lineno, text in groups)
    raw = subprocess.check_output([facts_binary()], input=payload)
    for line in raw.decode("utf-8").splitlines():
        fields = line.split(" ", 2)
        if len(fields) != 3:
            continue
        yield int(fields[0]), fields[1], parse_sexpr(fields[2])


def mean_numbers(text):
    nums = [float(n) for n in NUM_RE.findall(text)]
    return sum(nums) / len(nums) if nums else None


# --------------------------------------------------------------------------
# Track reading
# --------------------------------------------------------------------------

def detect_tempo(code):
    m = re.search(r"\b(?:setbpm|glideBpm)\s+(\d+(?:\.\d+)?)", code)
    return float(m.group(1)) if m else 120.0


def tempo_from_statements(statements):
    """Read the home tempo from parsed statements, not header text."""
    for _, expr in statements:
        for name in ("glideBpm", "setbpm"):
            for args in find_calls(expr, name):
                if args:
                    return parse_num_expr(args[0])
    return None


def detect_beats(code):
    m = re.search(r"one\s+cycle\s*=\s*one\s+(\d+)/(\d+)\s+bar",
                  code, re.IGNORECASE)
    if m:
        return 4.0 * int(m.group(1)) / int(m.group(2))
    return 4.0


def make_alias(body, params):
    head, _ = app_parts(body)
    head_name = var_name(head)
    if params:
        kind = "voice"
    elif head_name in ("gain", "amp", "level"):
        kind = "control"
    elif head_name in ("cat", "slowCat") or node_kind(body) == "str":
        kind = "pattern"
    else:
        kind = "voice"
    return Alias(kind, body, list(params))


def read_track(path):
    code = path.read_text(encoding="utf-8")
    blocks = check_tidal.group_blocks(path)
    aliases, statements = {}, []
    for lineno, kind, value in ast_facts(blocks):
        if kind == "BIND":
            name, params, body = value
            aliases[name] = make_alias(body, params)
        elif kind == "STMT":
            statements.append((lineno, value))
    bpm = tempo_from_statements(statements) or detect_tempo(code)
    return Track(path, bpm, detect_beats(code), aliases, statements)


# --------------------------------------------------------------------------
# AST alias expansion: beta-reduction over GHC-parsed expressions.
# --------------------------------------------------------------------------

def param_bindings(params, args):
    out = {}
    for param, arg in zip(params, args):
        kind = node_kind(param)
        if kind == "pvar":
            out[param[1]] = arg
        elif kind == "ptuple" and node_kind(arg) == "tuple":
            out.update(param_bindings(param[1:], arg[1:]))
    return out


def subst_expr(expr, bindings):
    if node_kind(expr) == "var" and expr[1] in bindings:
        return bindings[expr[1]]
    if isinstance(expr, list):
        return [subst_expr(item, bindings) for item in expr]
    return expr


def map_over_list(fn, items, aliases, depth):
    if node_kind(items) != "list":
        return None
    return expand_ast(["list"] + [["app", fn, item] for item in items[1:]],
                      aliases, depth + 1)


def record_field(name, value, aliases, depth):
    """Resolve a record-selector application such as `utopia variants`."""
    record = expand_ast(value, aliases, depth + 1)
    if node_kind(record) != "record":
        return None
    for field in record[2]:
        if field[0] == name:
            return field[1]
    return None


def expand_ast(expr, aliases, depth=0):
    if depth > 8 or not isinstance(expr, list):
        return expr
    kind = node_kind(expr)

    if kind == "var":
        alias = aliases.get(expr[1])
        if alias and not alias.params:
            return expand_ast(alias.body, aliases, depth + 1)
        return expr

    if kind == "let":
        binds, body = expr[1], expr[2]
        local = {}
        for name, params, bound in binds:
            local[name] = make_alias(expand_ast(bound, aliases, depth + 1),
                                     params)
        return expand_ast(body, dict(aliases, **local), depth + 1)

    if kind == "lam":
        return ["lam", expr[1], expand_ast(expr[2], aliases, depth + 1)]

    if kind == "record":
        fields = [[name, expand_ast(body, aliases, depth + 1)]
                  for name, body in expr[2]]
        return ["record", expr[1], fields]

    if kind == "app":
        head, args = expr[1], expr[2:]
        if node_kind(head) == "lam":
            params = head[1]
            replaced = subst_expr(head[2],
                                  param_bindings(params, args[:len(params)]))
            expanded = expand_ast(replaced, aliases, depth + 1)
            rest = [expand_ast(a, aliases, depth + 1)
                    for a in args[len(params):]]
            return ["app", expanded] + rest if rest else expanded
        name = var_name(head)
        if name and args:
            field = record_field(name, args[0], aliases, depth)
            if field is not None:
                return expand_ast(field, aliases, depth + 1)
        alias = aliases.get(name) if name else None
        if alias and alias.params and len(args) >= len(alias.params):
            count = len(alias.params)
            replaced = subst_expr(alias.body,
                                  param_bindings(alias.params, args[:count]))
            expanded = expand_ast(replaced, aliases, depth + 1)
            rest = [expand_ast(a, aliases, depth + 1) for a in args[count:]]
            return ["app", expanded] + rest if rest else expanded
        if alias and not alias.params:
            head = expand_ast(head, aliases, depth + 1)
            if var_name(head) and var_name(head) != name:
                return expand_ast(["app", head] + args, aliases, depth + 1)
        if var_name(head) == "fmap" and len(args) >= 2:
            mapped = map_over_list(args[0], args[1], aliases, depth)
            if mapped is not None:
                return mapped
        return ["app", head] + [expand_ast(a, aliases, depth + 1)
                                for a in args]

    if kind == "op" and expr[1] in ("<$>", "<&>"):
        mapped = map_over_list(expr[2], expr[3], aliases, depth)
        if mapped is not None:
            return mapped

    return [expand_ast(item, aliases, depth + 1) if isinstance(item, list)
            else item for item in expr]


# --------------------------------------------------------------------------
# Mini-notation reduction
# --------------------------------------------------------------------------

def split_top(text, sep=","):
    """Split mini-notation on a separator outside quotes and brackets."""
    out, start, depth, quote, esc = [], 0, 0, False, False
    pairs = {"(": ")", "[": "]", "{": "}", "<": ">"}
    for i, ch in enumerate(text):
        if quote:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                quote = False
            continue
        if ch == '"':
            quote = True
        elif ch in pairs:
            depth += 1
        elif ch in pairs.values():
            depth = max(0, depth - 1)
        elif ch == sep and depth == 0:
            out.append(text[start:i].strip())
            start = i + 1
    out.append(text[start:].strip())
    return out


def pattern_tokens(text):
    return [t for t in split_top(text, " ") if t]


def token_stats(token, span):
    """Return (events, average duration in cycles) for one mini token."""
    token = token.strip()
    if not token or token == "~":
        return 0.0, 0.0
    if token == "_":
        return 0.0, 0.0

    # Chance and repeat modifiers.
    events_factor, dur_factor = 1.0, 1.0
    if token.endswith("?"):
        token = token[:-1]
        events_factor *= 0.5
    m = re.search(r"\*(\d+(?:\.\d+)?)$", token)
    if m:
        times = float(m.group(1))
        token = token[:m.start()]
        events_factor *= times
        dur_factor /= times

    # Euclidean patterns: (k,n,...) distribute k hits over n substeps.
    euclid = re.search(r"\((\d+)\s*,\s*(\d+)", token)
    if euclid:
        k, n = int(euclid.group(1)), int(euclid.group(2))
        if k > 0 and n > 0:
            return events_factor * k, dur_factor * span * n / k

    # Alternation and groups.
    if token.startswith("<") and token.endswith(">"):
        alts = pattern_tokens(token[1:-1]) or [token[1:-1]]
        stats = [pattern_stats(a, span) for a in alts]
        return (events_factor * sum(s[0] for s in stats) / len(stats),
                dur_factor * sum(s[1] for s in stats) / len(stats))
    if token.startswith("[") and token.endswith("]"):
        return token_stats_group(token[1:-1], span, events_factor, dur_factor)

    return events_factor, dur_factor * span


def token_stats_group(inner, span, events_factor, dur_factor):
    tokens = pattern_tokens(inner)
    if not tokens:
        return 0.0, 0.0
    sub = pattern_stats(inner, span)
    return events_factor * sub[0], dur_factor * sub[1]


def pattern_stats(text, span=1.0):
    """Return (events per span, average duration in cycles) for a pattern."""
    tokens = pattern_tokens(text)
    if not tokens:
        return 0.0, 0.0
    step = span / len(tokens)
    events, dur_sum = 0.0, 0.0
    pending = None       # (events, duration for one step, extra steps held)

    def flush():
        nonlocal events, dur_sum, pending
        if pending:
            ev, dur, held = pending
            events += ev
            dur_sum += ev * (dur + held * step)
            pending = None

    for tok in tokens:
        if tok == "~":
            flush()
            continue
        if tok == "_":
            if pending:
                ev, dur, held = pending
                pending = (ev, dur, held + 1)
            continue
        flush()
        ev, dur = token_stats(tok, step)
        if ev > 0:
            pending = (ev, dur, 0)
    flush()
    avg = dur_sum / events if events > 0 else 0.0
    return events, avg


def collect_pattern_strings(expr, skip=False):
    """Strings in pattern position, excluding sample/control arguments."""
    if not isinstance(expr, list):
        return []
    if node_kind(expr) == "str":
        return [] if skip else [expr[1]]
    if node_kind(expr) == "app":
        head, args = app_parts(expr)
        name = var_name(head)
        out = []
        for i, arg in enumerate(args):
            arg_skip = skip or name in NON_PATTERN_CALLS or \
                (name == "speedAt" and i == 0)
            out.extend(collect_pattern_strings(arg, arg_skip))
        return out
    out = []
    for item in expr:
        out.extend(collect_pattern_strings(item, skip))
    return out


def choose_duration_strings(expr):
    strings = collect_pattern_strings(expr)
    useful = []
    for s in strings:
        toks = pattern_tokens(s)
        if len(toks) > 1 or re.search(r"[~_*\[\]<>()]", s):
            useful.append(s)
    if useful:
        return useful
    return strings or s_arguments(expr)


def s_arguments(expr):
    """Return the string arguments of `s` calls in an AST."""
    out = []
    for args in find_calls(expr, "s"):
        for arg in args:
            if node_kind(arg) == "str":
                out.append(arg[1])
            elif isinstance(arg, list):
                out.extend(collect_strings(arg))
    return out


# --------------------------------------------------------------------------
# Control values and sample levels
# --------------------------------------------------------------------------

def parse_num_expr(expr):
    """Reduce a Tidal control expression to one representative number."""
    kind = node_kind(expr)
    if kind == "num":
        return float(expr[1])
    if kind == "str":
        return mean_numbers(expr[1]) or 0.0
    if kind == "neg":
        return -parse_num_expr(expr[1])
    if kind == "op" and expr[1] in ("|+", "|-"):
        return parse_num_expr(expr[2])

    head, args = app_parts(expr)
    name = var_name(head)
    if name == "range" and len(args) >= 2:
        return (parse_num_expr(args[0]) + parse_num_expr(args[1])) / 2
    if name == "choose" and args and node_kind(args[0]) == "list":
        values = []
        for item in args[0][1:]:
            values.append(float(item[1]) if node_kind(item) == "num"
                          else parse_num_expr(item))
        return sum(values) / len(values) if values else 0.0
    if name == "irand" and args:
        return parse_num_expr(args[0]) / 2
    if name in ("rand", "sine", "saw", "triangle", "isine", "noise"):
        return 0.5
    if collect_vars(expr) & {"rand", "sine", "saw", "triangle", "isine",
                             "noise"}:
        return 0.5

    values = [float(node[1]) for node in walk(expr)
              if node_kind(node) == "num"]
    values.extend(mean_numbers(node[1]) for node in walk(expr)
                  if node_kind(node) == "str" and mean_numbers(node[1]))
    return sum(values) / len(values) if values else 0.0


def parse_controls(fragments):
    controls = {}
    for frag in fragments:
        head, args = app_parts(frag)
        key = var_name(head)
        if not key:
            continue
        value = parse_num_expr(args[0]) if args else 0.0
        if key == "level":
            controls["amp"] = value
            controls["gain"] = 1.0
        elif key in CONTROL_KEYS:
            controls[key] = value
    return controls


def sample_labels(patterns):
    labels = []
    for pat in patterns:
        for tok in pattern_tokens(pat):
            clean = tok.rstrip("?")
            euclid = re.search(r"\((\d+)\s*,\s*(\d+)\s*,?\s*<([^>]*)>", clean)
            if euclid:
                variants = [int(x) for x in euclid.group(3).split()]
                clean = clean[:euclid.start()] + clean[euclid.end():]
            else:
                variants = []
            m = re.match(r"^([0-9A-Za-z][A-Za-z0-9_-]*)(?::(\d+))?", clean)
            if not m:
                continue
            bank = m.group(1)
            if NOTE_RE.match(bank) or bank in ("t", "T"):
                continue
            if not variants:
                variants = [int(m.group(2)) if m.group(2) else 0]
            labels.extend((bank, v) for v in variants)
    return labels


class Sampler:
    def __init__(self, use_samples, extra_dir):
        self.enabled = use_samples
        self.roots = ([Path(extra_dir)] if extra_dir else []) + [DIRT, LOCAL]
        self.cache, self.missing = {}, set()

    def rms(self, bank, var):
        key = (bank, var)
        if key in self.cache:
            return self.cache[key]
        if not self.enabled:
            self.cache[key] = 1.0
            return 1.0
        for root in self.roots:
            bank_dir = root / bank
            if not bank_dir.is_dir():
                continue
            files = sorted(p for p in bank_dir.iterdir()
                           if p.suffix.lower() == ".wav")
            if not files:
                continue
            path = files[var % len(files)]
            try:
                x, _ = analyse_audio.load_wav(str(path))
                value = float(np.sqrt(np.mean(x ** 2))) if len(x) else 0.0
                self.cache[key] = value
                return value
            except Exception:
                break
        self.missing.add(key)
        self.cache[key] = 1.0
        return 1.0


# --------------------------------------------------------------------------
# AST evaluation: energy arithmetic only.
# --------------------------------------------------------------------------

MOVING = {"rand", "sine", "saw", "triangle", "isine", "noise", "range",
          "choose", "irand"}


def split_dollars(expr):
    if node_kind(expr) == "op" and expr[1] == "$":
        return split_dollars(expr[2]) + [expr[3]]
    return [expr]


def chain_fragments(expr):
    if node_kind(expr) == "chain" and expr[1] == "#":
        return expr[2:]
    return [expr]


def gate_ratio(pattern):
    gates = pattern_tokens(pattern)
    return (sum(1 for g in gates if g == "t") / len(gates)) if gates else 1.0


def prefix_functions(expr):
    """Split a composed Tidal prefix on `(.)` into its parts."""
    kind = node_kind(expr)
    if kind == "op" and expr[1] == ".":
        return prefix_functions(expr[2]) + prefix_functions(expr[3])
    if kind == "sectionL":
        return prefix_functions(expr[1])
    if kind == "sectionR":
        return prefix_functions(expr[2])
    return [expr]


def prefix_adjust_ast(prefixes):
    events_factor, dur_factor, flags = 1.0, 1.0, set()
    for prefix in prefixes:
        for fn in prefix_functions(prefix):
            head, args = app_parts(fn)
            name = var_name(head)
            if name == "degradeBy" and args:
                events_factor *= max(0.0, 1.0 - parse_num_expr(args[0]))
            elif name == "degrade":
                events_factor *= 0.5
            elif name in ("slow", "fast") and args:
                n = parse_num_expr(args[0])
                if n > 0:
                    if name == "slow":
                        events_factor /= n
                        dur_factor *= n
                    else:
                        events_factor *= n
                        dur_factor /= n
            elif name == "struct" and args and node_kind(args[0]) == "str":
                ratio = gate_ratio(args[0][1])
                events_factor *= ratio
                dur_factor *= ratio
            elif name == "every" and args:
                n = max(1, int(parse_num_expr(args[0])))
                ratio = 1.0
                for inner in args[1:]:
                    for gate in find_calls(inner, "struct"):
                        if gate and node_kind(gate[0]) == "str":
                            ratio = gate_ratio(gate[0][1])
                factor = (n - 1 + ratio) / n
                events_factor *= factor
                dur_factor *= factor
            if "sometimes" in collect_vars(fn):
                events_factor *= 1.5
                dur_factor /= 1.5
            if collect_vars(fn) & MOVING:
                flags.add("moving")
    return events_factor, dur_factor, flags


def evaluate_ast(expr, aliases, ctx):
    expanded = expand_ast(expr, aliases)
    parts = split_dollars(expanded)
    prefixes, body = parts[:-1], parts[-1]
    ef, df, pflags = prefix_adjust_ast(prefixes)

    head, args = app_parts(body)
    if var_name(head) == "stack" and args and node_kind(args[0]) == "list":
        voice = Voice()
        for item in args[0][1:]:
            voice.add(evaluate_ast(item, aliases, ctx))
        return voice.scaled(ef, df)

    if var_name(head) == "cat" and args and node_kind(args[0]) == "list":
        items = args[0][1:]
        if not items:
            return Voice()
        voice = Voice()
        for item in items:
            v = evaluate_ast(item, aliases, ctx)
            voice.events += v.events / len(items)
            voice.energy += v.energy / len(items)
            voice.level_sum += v.level_sum / len(items)
            voice.dur_sum += v.dur_sum / len(items)
            voice.flags |= v.flags
        return voice.scaled(ef, df)

    fragments = chain_fragments(body)
    controls = parse_controls(fragments[1:])

    strings = choose_duration_strings(body)
    if not strings:
        return Voice()
    events, dur_cycles = 0.0, 0.0
    for s in strings:
        ev, du = pattern_stats(s)
        events += ev / len(strings)
        dur_cycles += du / len(strings)

    labels = sample_labels(s_arguments(body))
    samples = [(b, v) for b, v in labels if not b.startswith("hedge_")]
    synths = [(b, v) for b, v in labels if b.startswith("hedge_")]
    if samples:
        source = sum(ctx["sampler"].rms(bank, var)
                     for bank, var in samples) / len(samples)
        src_flag = "sample"
    elif synths:
        source, src_flag = 1.0, "synth"
    else:
        source, src_flag = 1.0, "nominal"
    if any((b, v) in ctx["sampler"].missing for b, v in samples):
        pflags.add("missing-sample")

    amp = controls.get("amp", 1.0) * (controls.get("gain", 1.0) ** 4)
    level = amp * source
    cycle_sec = ctx["cycle_sec"]

    speed = controls.get("speed", controls.get("rate", 1.0))
    if speed > 0 and src_flag == "sample":
        dur_cycles /= speed
    dur_cycles *= df
    events *= ef

    event_sec = dur_cycles * cycle_sec
    if "sustain" in controls and controls["sustain"] > 0:
        event_sec = controls["sustain"]
    else:
        event_sec *= controls.get("legato", 1.0)
    event_sec += controls.get("release", 0.0) + controls.get("decay", 0.0)
    room, size = controls.get("room", 0.0), controls.get("size", 0.0)
    event_sec += min(2.0, room * (0.5 + size) * 2.0)
    event_sec = max(0.0, min(cycle_sec, event_sec))

    energy = events * (level ** 2) * event_sec
    flags = set(pflags) | {src_flag}
    if any(k in controls for k in ("gain", "room", "sustain", "release",
                                   "decay", "legato", "speed", "rate")):
        flags.add("approx")
    return Voice(events, energy, events * level, events * event_sec, flags)


def int_arg(expr):
    if node_kind(expr) == "num":
        return int(float(expr[1]))
    return None


def call_items(expr, names):
    head, args = app_parts(expr)
    if var_name(head) in names:
        return head, args
    return None, None


def pair_items(expr):
    if node_kind(expr) != "list":
        return []
    out = []
    for item in expr[1:]:
        if node_kind(item) == "tuple" and len(item) >= 3:
            sid = int_arg(item[1])
            if sid is not None:
                out.append((sid, item[2]))
    return out


def stream_from_head(expr):
    """Return a stream id from a direct `dN` or fade/clutch call, if any."""
    name = var_name(expr)
    if name and re.fullmatch(r"d\d+", name):
        return int(name[1:])
    head, args = call_items(expr, {"xfadeIn", "clutchIn", "fadeIn", "fadeOut"})
    if head is not None and len(args) >= 2:
        return int_arg(args[0])
    kind = node_kind(expr)
    if kind == "op" and expr[1] == ".":
        return stream_from_head(expr[2]) or stream_from_head(expr[3])
    if kind == "chain":
        return stream_from_head(expr[2])
    if kind in ("sectionL", "sectionR"):
        return stream_from_head(expr[1] if kind == "sectionL" else expr[2])
    return None


def stream_items(expr, aliases):
    expanded = expand_ast(expr, aliases)
    if node_kind(expanded) == "let":
        return stream_items(expanded[2], aliases)
    if "once" in collect_vars(expanded):
        return []

    if node_kind(expanded) == "chain":
        return [(sid, ["chain", "#", body] + expanded[3:])
                for sid, body in stream_items(expanded[2], aliases)]

    if node_kind(expanded) == "op" and expanded[1] == "$":
        left, right = expanded[2], expanded[3]
        sid = stream_from_head(left)
        if sid is not None:
            return [(sid, right)]
        pairs = pair_items(right)
        if pairs:
            return pairs

    head, args = app_parts(expanded)
    name = var_name(head)
    if name and re.fullmatch(r"d\d+", name) and args:
        return [(int(name[1:]), args[0])]
    sid = stream_from_head(expanded)
    if sid is not None and len(args) >= 3:
        return [(sid, args[2])]
    pairs = pair_items(args[-1]) if args else []
    return pairs


def measure_track(track, sampler, beats_override=None):
    beats = beats_override if beats_override else track.beats
    cycle_sec = 4.0 * 60.0 / track.bpm * (beats / 4.0)
    ctx = {"sampler": sampler, "cycle_sec": cycle_sec}
    streams, sources = {}, {}
    for lineno, statement in track.statements:
        for sid, expr in stream_items(statement, track.aliases):
            voice = evaluate_ast(expr, track.aliases, ctx)
            if sid not in streams or voice.energy > streams[sid].energy:
                streams[sid] = voice
                sources[sid] = lineno
    total = Voice()
    for voice in streams.values():
        total.add(voice)
    return {"track": track, "streams": streams, "sources": sources,
            "total": total, "cycle_sec": cycle_sec, "beats": beats}


# --------------------------------------------------------------------------
# Output
# --------------------------------------------------------------------------

def fmt(v, width=6, prec=2):
    return ("%*.*f" % (width, prec, v)) if v is not None else "-"


def print_track(result):
    t, total = result["track"], result["total"]
    flags = set().union(*(v.flags for v in result["streams"].values())) \
        if result["streams"] else set()
    name = t.path.stem
    print("%-18s %5.0f %6.2f %4d %8s %8s %9s  %s" %
          (name, t.bpm, result["beats"], len(result["streams"]),
           fmt(total.level(), 8, 3), fmt(total.events, 8, 1),
           fmt(total.rms(result["cycle_sec"]), 9, 3),
           ",".join(sorted(flags)) or "-"))
    return name


def print_track_view(results):
    print("Coarse source-level audit: loudest section per stream; synths "
          "nominal 1.0.")
    print("%-18s %5s %6s %4s %8s %8s %9s  FLAGS" %
          ("TRACK", "BPM", "BEATS", "DSTR", "LEVEL", "DENS", "RMS/CYC"))
    for result in results:
        print_track(result)
    for result in results:
        t = result["track"]
        print("\n%s — streams (loudest section)" % t.path.stem)
        print("  %-6s %6s %8s %7s %7s %9s  %s" %
              ("STREAM", "LINE", "LEVEL", "DENS", "DUR_S", "RMS/CYC", "SOURCE"))
        for sid, v in sorted(result["streams"].items()):
            source = "sample" if "sample" in v.flags else \
                ("synth" if "synth" in v.flags else "nominal")
            print("  %-6s %6d %8s %7s %7s %9s  %s" %
                  ("d%d" % sid, result["sources"].get(sid, 0),
                   fmt(v.level(), 8, 3), fmt(v.events, 7, 1),
                   fmt(v.dur(result["cycle_sec"]), 7, 2),
                   fmt(v.rms(result["cycle_sec"]), 9, 3), source))
    print("\nLEVEL = amp * gain^4 * source; DENS = events/cycle; DUR_S = "
          "representative sounding time; RMS/CYC = sqrt(energy/cycle).")


def print_compare_view(results):
    base = results[0]["total"].rms(results[0]["cycle_sec"]) or 1e-9
    print("Coarse inter-track comparison: same core as `track`; ratio to "
          "first track.")
    print("%-18s %5s %6s %4s %8s %8s %9s %8s" %
          ("TRACK", "BPM", "BEATS", "DSTR", "LEVEL", "DENS", "RMS/CYC", "xBASE"))
    for result in results:
        t, total = result["track"], result["total"]
        rms = total.rms(result["cycle_sec"])
        print("%-18s %5.0f %6.2f %4d %8s %8s %9s %7.2fx" %
              (t.path.stem, t.bpm, result["beats"], len(result["streams"]),
               fmt(total.level(), 8, 3), fmt(total.events, 8, 1),
               fmt(rms, 9, 3), rms / base))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="view")
    for view in ("track", "compare"):
        p = sub.add_parser(view, help=("per-track detail" if view == "track"
                                       else "inter-track comparison"))
        p.add_argument("tracks", nargs="*", metavar="TRACK")
        p.add_argument("--all", action="store_true",
                       help="read every tracks/*/*.tidal file")
        p.add_argument("--beats", type=float, metavar="N",
                       help="quarter-note beats per cycle (default: from track)")
        p.add_argument("--no-samples", action="store_true",
                       help="use nominal source level 1.0 everywhere")
        p.add_argument("--dir", metavar="PATH",
                       help="extra sample corpus root before Dirt-Samples")
    args = ap.parse_args()
    if args.view is None:
        ap.error("choose a view: track or compare")

    files = list(args.tracks)
    if args.all:
        files.extend(str(p) for p in sorted(ROOT.glob("tracks/*/*.tidal")))
    if not files:
        ap.error("give at least one TRACK, or use --all")
    paths = [Path(f) if Path(f).is_absolute() else ROOT / f for f in files]
    missing = [str(p) for p in paths if not p.is_file()]
    if missing:
        ap.error("no such track: " + ", ".join(missing))

    sampler = Sampler(not args.no_samples, args.dir)
    results = [measure_track(read_track(p), sampler, args.beats) for p in paths]
    if args.view == "track":
        print_track_view(results)
    else:
        print_compare_view(results)
    if sampler.missing:
        print("\nwarning: %d sample(s) not found; used nominal level: %s" %
              (len(sampler.missing),
               ", ".join("%s:%d" % pair for pair in
                         sorted(sampler.missing)[:12])), file=sys.stderr)


if __name__ == "__main__":
    main()
