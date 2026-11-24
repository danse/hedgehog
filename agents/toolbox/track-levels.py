#!/usr/bin/env python3
"""Coarse per-track level/energy audit, with a shared inter-track comparison.

This is a *macroscopic* check, not a loudness meter. It reads Tidal source
statically, so it never starts GHCi, SuperDirt, sclang or an OSC clock. For each
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
import math
import re
import sys
import wave
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
ANALYSER = ROOT / "scripts" / "analyse-audio.py"
CHECK_TIDAL = ROOT / "scripts" / "check-tidal.py"
DIRT = Path.home() / ".local/share/SuperCollider/downloaded-quarks/Dirt-Samples"
LOCAL = ROOT / "samples"

spec = importlib.util.spec_from_file_location("analyse_audio", ANALYSER)
analyse_audio = importlib.util.module_from_spec(spec)
spec.loader.exec_module(analyse_audio)

spec = importlib.util.spec_from_file_location("check_tidal", CHECK_TIDAL)
check_tidal = importlib.util.module_from_spec(spec)
_saved_argv = sys.argv
sys.argv = [str(CHECK_TIDAL)]  # check-tidal.py runs its loop at import time
spec.loader.exec_module(check_tidal)
sys.argv = _saved_argv


DEF_RE = re.compile(r"^(\s+)(\w+)((?:\s+\w+)*)\s*=\s*(.*)$")
NUM_RE = re.compile(r"-?\d+(?:\.\d+)?")
CONTROL_KEYS = ("amp", "gain", "sustain", "release", "decay", "attack",
                "legato", "room", "size", "speed", "rate", "delay")
NOTE_RE = re.compile(r"^[a-gA-G][#bsf]?-?\d+$")


@dataclass
class Alias:
    kind: str                  # pattern | voice | control
    expr: str
    args: list = field(default_factory=list)


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
# Small text helpers. Quotes are protected before identifier substitution so
# a bank called `bass` cannot be rewritten into a pattern alias called `bass`.
# --------------------------------------------------------------------------

def protect_strings(text):
    saved = []

    def repl(m):
        saved.append(m.group(0))
        return "\x01STR%d\x01" % (len(saved) - 1)

    return re.sub(r'"(?:[^"\\]|\\.)*"', repl, text), saved


def restore_strings(text, saved):
    for i, s in enumerate(saved):
        text = text.replace("\x01STR%d\x01" % i, s)
    return text


def split_top(text, sep=","):
    """Split on a separator outside quotes and brackets."""
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


def strip_comments(text):
    return "\n".join(re.sub(r"--.*$", "", line).rstrip()
                     for line in text.splitlines())


def unwrap(text):
    """Remove balanced outer parentheses so `#` and `$` are visible."""
    text = text.strip()
    while text.startswith("(") and text.endswith(")"):
        depth, pairs = 0, {"(": ")", "[": "]", "{": "}", "<": ">"}
        closes = set(pairs.values())
        for i, ch in enumerate(text):
            if ch in pairs:
                depth += 1
            elif ch in closes:
                depth -= 1
                if depth == 0 and i != len(text) - 1:
                    return text
        text = text[1:-1].strip()
    return text


def mean_numbers(text):
    nums = [float(n) for n in NUM_RE.findall(text)]
    return sum(nums) / len(nums) if nums else None


def read_arg(text, pos):
    """Read one Haskell-ish argument starting at pos; return (arg, end)."""
    while pos < len(text) and text[pos].isspace():
        pos += 1
    if pos >= len(text):
        return None, pos
    ch = text[pos]
    if ch == '"':
        end = pos + 1
        while end < len(text):
            if text[end] == "\\":
                end += 2
                continue
            if text[end] == '"':
                end += 1
                break
            end += 1
        return text[pos:end], end
    if ch in "([{":
        close = {")": "(", "]": "[", "}": "{"}
        pairs = {"(": ")", "[": "]", "{": "}"}
        depth = 0
        for end in range(pos, len(text)):
            c = text[end]
            if c in pairs:
                depth += 1
            elif c in close:
                depth -= 1
                if depth == 0:
                    return text[pos:end + 1], end + 1
        return text[pos:], len(text)
    end = pos
    while end < len(text) and not text[end].isspace() \
            and text[end] not in ",]$#":
        end += 1
    return text[pos:end], end


# --------------------------------------------------------------------------
# Track reading
# --------------------------------------------------------------------------

def detect_tempo(code):
    m = re.search(r"\b(?:setbpm|glideBpm)\s+(\d+(?:\.\d+)?)", code)
    return float(m.group(1)) if m else 120.0


def detect_beats(code):
    m = re.search(r"one\s+cycle\s*=\s*one\s+(\d+)/(\d+)\s+bar",
                  code, re.IGNORECASE)
    if m:
        return 4.0 * int(m.group(1)) / int(m.group(2))
    return 4.0


def parse_let(code):
    lines = strip_comments(code).splitlines()
    start = next((i for i, line in enumerate(lines)
                  if line.lstrip() == "let"), None)
    aliases = {}
    if start is None:
        return aliases

    i = start + 1
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        ind = len(line) - len(line.lstrip())
        if ind == 0:
            break
        m = DEF_RE.match(line)
        if not m:
            i += 1  # a type signature or stray continuation
            continue
        ind_s, name, arg_text, rhs = m.groups()
        args = arg_text.split()
        definition_indent = len(ind_s)
        j = i + 1
        while j < len(lines):
            nxt = lines[j]
            if not nxt.strip():
                j += 1
                continue
            nxt_ind = len(nxt) - len(nxt.lstrip())
            if nxt_ind < definition_indent:
                break
            nm = DEF_RE.match(nxt)
            if nxt_ind == definition_indent and nm:
                break
            if "::" in nxt and "=" not in nxt:
                j += 1
                continue
            rhs += " " + nxt.strip()
            j += 1

        rhs = rhs.strip()
        if not rhs:
            i = j
            continue
        if re.match(r"^(gain|amp|level)\s", rhs):
            aliases[name] = Alias("control", rhs)
        elif re.match(r'^(cat|slowCat)\s*\[|^"|^<', rhs):
            aliases[name] = Alias("pattern", rhs)
        else:
            aliases[name] = Alias("voice", rhs, args)
        i = j
    return aliases


def parse_statements(code):
    numbered = [(n, line.rstrip()) for n, line in
                enumerate(strip_comments(code).splitlines(), 1)]
    out = []
    for block in check_tidal.group_statements(numbered):
        text = " ".join(t.strip() for _, t in block if t.strip())
        if not text or text.startswith("let"):
            continue
        out.append(text)
    return out


def read_track(path):
    code = path.read_text(encoding="utf-8")
    return Track(path, detect_tempo(code), detect_beats(code),
                 parse_let(code), parse_statements(code))


# --------------------------------------------------------------------------
# Alias expansion
# --------------------------------------------------------------------------

def substitute_bindings(text, bindings):
    protected, saved = protect_strings(text)
    for key, value in bindings.items():
        protected = re.sub(r"\b%s\b" % re.escape(key),
                           lambda m, v=value: "(" + v + ")", protected)
    return restore_strings(protected, saved)


def expand(expr, aliases, depth=0):
    if depth > 8:
        return expr
    before = expr
    protected, saved = protect_strings(expr)

    # Control aliases first: `# chordsGain` -> `# amp 2`.
    for name, alias in aliases.items():
        if alias.kind == "control":
            protected = re.sub(r"#\s*\b%s\b" % re.escape(name),
                               "# " + alias.expr, protected)

    # Function aliases. Read balanced arguments so `pad (hA |+ 3)` survives.
    for name, alias in aliases.items():
        if alias.kind != "voice" or not alias.args:
            continue
        pattern = re.compile(r"\b%s\b" % re.escape(name))
        pos = 0
        while True:
            m = pattern.search(protected, pos)
            if not m:
                break
            rest = protected[m.end():]
            actual, consumed = [], 0
            ok = True
            for _ in alias.args:
                arg, end = read_arg(rest, consumed)
                if arg is None:
                    ok = False
                    break
                actual.append(arg)
                consumed = end
            if not ok:
                pos = m.end()
                continue
            body = alias.expr
            for formal, value in zip(alias.args, actual):
                body = re.sub(r"\b%s\b" % re.escape(formal),
                              lambda mm, v=value: "(" + v + ")", body)
            replacement = "(" + body + ")"
            protected = protected[:m.start()] + replacement \
                + protected[m.end() + consumed:]
            pos = m.start() + len(replacement)

    # Pattern aliases and zero-argument voice aliases are plain substitution.
    for name, alias in aliases.items():
        if alias.kind in ("pattern", "voice") and \
                (alias.kind == "pattern" or not alias.args):
            protected = re.sub(r"\b%s\b" % re.escape(name),
                               lambda m, e=alias.expr: "(" + e + ")", protected)

    expr = restore_strings(protected, saved)
    if expr == before:
        return expr
    return expand(expr, aliases, depth + 1)


# --------------------------------------------------------------------------
# Mini-notation reduction
# --------------------------------------------------------------------------

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


def choose_duration_strings(base):
    strings = re.findall(r'"(?:[^"\\]|\\.)*"', base)
    useful = []
    for s in strings:
        inner = s[1:-1]
        toks = pattern_tokens(inner)
        if len(toks) > 1 or re.search(r"[~_*\[\]<>()]", inner):
            useful.append(inner)
    return useful or [s[1:-1] for s in strings]


def s_arguments(base):
    """Return the string arguments of top-level `s` calls."""
    protected, saved = protect_strings(base)
    out = []
    pattern = re.compile(r"\bs\s+")
    pos = 0
    while True:
        m = pattern.search(protected, pos)
        if not m:
            break
        arg, end = read_arg(protected, m.end())
        if arg is None:
            break
        pm = re.match(r"\x01STR(\d+)\x01", arg)
        if pm:
            out.append(saved[int(pm.group(1))][1:-1])
        elif arg.startswith("("):
            out.extend(s[1:-1] for s in
                       re.findall(r'"(?:[^"\\]|\\.)*"', arg))
        pos = end
    return out


# --------------------------------------------------------------------------
# Control values and sample levels
# --------------------------------------------------------------------------

def parse_num(value):
    """Reduce a Tidal control value to one representative number."""
    v = value.strip()
    if not v:
        return 0.0
    range_m = re.search(r"\brange\s+(-?[\d.]+)\s+(-?[\d.]+)", v)
    if range_m:
        return (float(range_m.group(1)) + float(range_m.group(2))) / 2
    if v.startswith('"'):
        return mean_numbers(v) or 0.0
    choose_m = re.search(r"\bchoose\s*\[([^\]]*)\]", v)
    if choose_m:
        return mean_numbers(choose_m.group(1)) or 0.0
    irand_m = re.search(r"\birand\s+(\d+(?:\.\d+)?)", v)
    if irand_m:
        return float(irand_m.group(1)) / 2
    if re.search(r"\b(rand|sine|saw|triangle|isine|noise)\b", v):
        return 0.5
    if v.startswith("("):
        inner = v[1:-1]
        if "|+" in inner or "|-" in inner:
            left = inner.split("|", 1)[0]
            return parse_num(left)
    n = mean_numbers(v)
    return n if n is not None else 0.0


def parse_controls(fragments):
    controls = {}
    for frag in fragments:
        frag = frag.strip()
        if not frag:
            continue
        m = re.match(r"^([A-Za-z][\w]*)\s+(.+)$", frag, re.S)
        if not m:
            continue
        key, value = m.groups()
        value = parse_num(value)
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
# Expression evaluation
# --------------------------------------------------------------------------

def prefix_adjust(prefixes):
    events_factor, dur_factor, flags = 1.0, 1.0, set()
    for p in prefixes:
        p = p.strip()
        m = re.search(r"\bdegradeBy\s+(-?[\d.]+)", p)
        if m:
            events_factor *= max(0.0, 1.0 - float(m.group(1)))
        m = re.search(r"\bslow\s+(\d+(?:\.\d+)?)", p)
        if m and float(m.group(1)) > 0:
            n = float(m.group(1))
            events_factor /= n
            dur_factor *= n
        m = re.search(r"\bfast\s+(\d+(?:\.\d+)?)", p)
        if m and float(m.group(1)) > 0:
            n = float(m.group(1))
            events_factor *= n
            dur_factor /= n
        m = re.search(r"\bstruct\s+\"([^\"]*)\"", p)
        if m:
            gates = pattern_tokens(m.group(1))
            ratio = (sum(1 for g in gates if g == "t") / len(gates)
                     if gates else 1.0)
            events_factor *= ratio
            dur_factor *= ratio
        m = re.search(r"\bevery\s+(\d+)\s*\(", p)
        if m:
            n = max(1, int(m.group(1)))
            gate = re.search(r"\bstruct\s+\"([^\"]*)\"", p)
            ratio = 1.0
            if gate:
                gates = pattern_tokens(gate.group(1))
                ratio = (sum(1 for g in gates if g == "t") / len(gates)
                         if gates else 1.0)
            factor = (n - 1 + ratio) / n
            events_factor *= factor
            dur_factor *= factor
        if re.search(r"\bsometimes\b", p):
            events_factor *= 1.5
            dur_factor /= 1.5
        if re.search(r"\b(rand|sine|saw|range|choose|irand)\b", p):
            flags.add("moving")
    return events_factor, dur_factor, flags


def evaluate(expr, aliases, ctx):
    expanded = unwrap(expand(expr, aliases))
    parts = split_top(expanded, "$")
    prefixes, body = parts[:-1], parts[-1]
    ef, df, pflags = prefix_adjust(prefixes)

    if re.match(r"^stack\s*\[", body):
        inner = body[body.index("[") + 1:]
        inner = inner[:inner.rfind("]")] if "]" in inner else inner
        voice = Voice()
        for item in split_top(inner, ","):
            voice.add(evaluate(item, aliases, ctx))
        return voice.scaled(ef, df)

    if re.match(r"^cat\s*\[", body):
        inner = body[body.index("[") + 1:]
        inner = inner[:inner.rfind("]")] if "]" in inner else inner
        items = [item for item in split_top(inner, ",") if item]
        if not items:
            return Voice()
        voices = [evaluate(item, aliases, ctx) for item in items]
        voice = Voice()
        for v in voices:
            voice.events += v.events / len(voices)
            voice.energy += v.energy / len(voices)
            voice.level_sum += v.level_sum / len(voices)
            voice.dur_sum += v.dur_sum / len(voices)
            voice.flags |= v.flags
        return voice.scaled(ef, df)

    parts = split_top(body, "#")
    base = parts[0]
    controls = parse_controls(parts[1:])

    # `s` and `note` are often written after `#`, so scan the whole body, not
    # only the pre-# base.
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


def stream_items(statement):
    st = statement.strip()
    m = re.match(r"^d(\d+)\s*(?:\$\s*)?(.*)$", st)
    if m:
        return [(int(m.group(1)), m.group(2).strip())]
    m = re.match(r"^(?:xfadeIn|clutchIn|fadeIn|fadeOut)\s+(\d+)\s+"
                 r"[\d.]+\s*\$\s*(.*)$", st)
    if m:
        return [(int(m.group(1)), m.group(2).strip())]
    m = re.match(r"^(?:multi|fadeMulti)(?:\s+\w+)?\s+[\d.]+\s*\[(.*)\]$", st)
    if m:
        out = []
        for item in split_top(m.group(1), ","):
            pair = re.match(r"^\(\s*(\d+)\s*,\s*(.*)\)$", item)
            if pair:
                out.append((int(pair.group(1)), pair.group(2).strip()))
        return out
    return []


def measure_track(track, sampler, beats_override=None):
    beats = beats_override if beats_override else track.beats
    cycle_sec = 4.0 * 60.0 / track.bpm * (beats / 4.0)
    ctx = {"sampler": sampler, "cycle_sec": cycle_sec}
    streams = {}
    for statement in track.statements:
        if statement.startswith("once "):
            continue
        for sid, expr in stream_items(statement):
            voice = evaluate(expr, track.aliases, ctx)
            if sid not in streams or voice.energy > streams[sid].energy:
                streams[sid] = voice
    total = Voice()
    for voice in streams.values():
        total.add(voice)
    return {"track": track, "streams": streams, "total": total,
            "cycle_sec": cycle_sec, "beats": beats}


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
        print("  %-6s %8s %7s %7s %9s  %s" %
              ("STREAM", "LEVEL", "DENS", "DUR_S", "RMS/CYC", "SOURCE"))
        for sid, v in sorted(result["streams"].items()):
            source = "sample" if "sample" in v.flags else \
                ("synth" if "synth" in v.flags else "nominal")
            print("  %-6s %8s %7s %7s %9s  %s" %
                  ("d%d" % sid, fmt(v.level(), 8, 3), fmt(v.events, 7, 1),
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
