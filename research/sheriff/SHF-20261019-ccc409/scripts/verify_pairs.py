#!/usr/bin/env python3
"""Independent re-check of retained replay pairs (shards/replay_strict_pairs_v2).

For every pair: (1) the .committed side must equal the blob at the audited base commit, and
(2) the exact comparison against the allowlist is recomputed from the two retained files alone.
Prints one line per pair and exits non-zero on any mismatch. Read-only.
"""
import subprocess, sys, json
from pathlib import Path
import yaml
sys.path.insert(0, str(Path(__file__).resolve().parent))
import replay_strict as R

BASE = "d0f70c0a0905a5d4d2fc7c082b6dd85e43094026"
allow = yaml.safe_load(open(R.CASE / "scripts/replay_allowlist.yaml"))
bad = 0
for c in sorted((R.CASE / "shards/replay_strict_pairs_v2").rglob("*.committed")):
    rel = c.relative_to(R.CASE / "shards/replay_strict_pairs_v2")
    eid, art = rel.parts[0], "/".join(rel.parts[1:])[: -len(".committed")]
    blob = subprocess.run(["git", "-C", str(R.REPO), "show", f"{BASE}:{art}"], capture_output=True, text=True).stdout
    same_base = blob == c.read_text()
    regen = c.with_name(c.name[: -len(".committed")] + ".regenerated")
    d, un = R.compare(R.load_any(c.read_text(), art), R.load_any(regen.read_text(), art), allow.get(art, []))
    ok = same_base and not un
    bad += not ok
    print(("OK  " if ok else "BAD ") + f"{eid} {art}: committed==base:{same_base} diffs:{len(d)} unexplained:{len(un)}")
sys.exit(1 if bad else 0)
