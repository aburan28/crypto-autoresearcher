#!/usr/bin/env python3
"""finalize_manifest.py — write runs/<run-id>/manifest.yaml for EXP-ICI-001.

Usage: python3 finalize_manifest.py <run_id> "<command>" "<parameters_json>"

Reads runs/<run_id>/raw.json for timings/resources/cell states, hashes
artifacts (raw.json, stdout.txt, stderr.txt), captures git/env, writes
manifest.yaml in the FB-001 flow style extended with timestamps, versions,
and resource measurements (docs/evidence-and-reproducibility.md minimum).
"""
import json
import os
import subprocess
import sys
from hashlib import sha256

EXP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(os.path.dirname(EXP))


def sh(path):
    h = sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git(args):
    return subprocess.run(["git", "-C", REPO] + args,
                          capture_output=True, text=True).stdout.strip()


def main():
    run_id, command, params_json = sys.argv[1], sys.argv[2], sys.argv[3]
    rdir = os.path.join(EXP, "runs", run_id)
    raw_path = os.path.join(rdir, "raw.json")
    with open(raw_path) as f:
        raw = json.load(f)
    arts = {}
    for name in ("raw.json", "stdout.txt", "stderr.txt"):
        p = os.path.join(rdir, name)
        if os.path.exists(p):
            arts[name] = {"path": "runs/%s/%s" % (run_id, name),
                          "sha256": sh(p), "bytes": os.path.getsize(p)}
    cells = raw.get("cells", [])
    states = {}
    for c in cells:
        states[c.get("status", "?")] = states.get(c.get("status", "?"), 0) + 1
    n_measured_sizes = len({c["n"] for c in cells
                            if c.get("status", "").startswith("measured")})
    dirty = bool(git(["status", "--porcelain"]))
    sage_v = subprocess.run(["sage", "--version"], capture_output=True,
                            text=True).stdout.strip()
    params = json.loads(params_json)
    validity = raw.get("_validity", {})
    lines = []
    lines.append('run: {id: %s, experiment_id: EXP-ICI-001,' % run_id)
    lines.append('  command: "%s",' % command.replace('"', '\\"'))
    lines.append('  git_commit: "%s", dirty_tree: %s,' % (git(["rev-parse", "HEAD"]),
                                                         str(dirty).lower()))
    lines.append('  sage_version: "%s", python: "sage-python 3.14.3", os: "macOS 15.6 Darwin arm64",' % sage_v)
    lines.append('  started_at: "%s", finished_at: "%s", wall_seconds: %.1f, peak_rss_bytes: %s,'
                 % (raw.get("started_at", "?"), raw.get("finished_at", "?"),
                    float(raw.get("wall_s", -1)), raw.get("peak_rss_bytes", -1)))
    lines.append('  parameters: %s,' % json.dumps(params))
    lines.append('  cell_states: %s, measured_sizes: %d,' % (json.dumps(states), n_measured_sizes))
    lines.append('  artifacts: %s,' % json.dumps(arts))
    lines.append('  validity_status: %s, validity_reason: "%s"}'
                 % (validity.get("status", "valid"), validity.get("reason", "").replace('"', '\\"')))
    with open(os.path.join(rdir, "manifest.yaml"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("wrote", os.path.join(rdir, "manifest.yaml"))


if __name__ == "__main__":
    main()
