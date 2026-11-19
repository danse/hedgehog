# Toolbox

Small helper scripts for recurring agent tasks. These are the tools that used
to live in `/tmp` and vanish on shutdown. Nothing here is part of the live set;
see [`../../scripts/`](../../scripts/) for that.

## Scripts

| Script | Purpose |
|---|---|
| `session-count.py [--grep PATTERN] [--limit N]` | Tally commits that touched each track's `.tidal` files as a proxy for sessions, sorted highest first. Multi-file tracks count once per commit. `--grep session` narrows to the terse `session` commits. |
| `fake-dirt.py` | Answer Tidal's `/dirt/handshake` on `127.0.0.1:57199` so a headless Tidal instance can tick without SuperDirt. Run it in the background (`python3 agents/toolbox/fake-dirt.py &`), then stop it with its PID. Nothing starts it automatically. |

`fake-dirt.py` is for inspecting pattern output when no audio server is
available — it emits no sound. The reusable audio analyser is in
[`../../scripts/analyse-audio.py`](../../scripts/analyse-audio.py).
