#!/usr/bin/env python3
"""finalize_manifest.py — write runs/<run-id>/manifest.yaml for EXP-ICI-001.

Captures: exact command, git commit + dirty-tree, environment, timing (from
raw.json), resources, artifact sha256 checksums, cell summary, validity.
Flow-style YAML matching experiments/EXP-FB-001/runs/RUN-FB-001-a/manifest.yaml,
extended with the docs/evidence-and-reproducibility.md minimum-manifest fields.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys

REPO = "/Volumes/Volume/crypto-autoresearcher"


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git(args):
    return subprocess.run(["git", "-C", REPO] + args,
                          capture_output=True, text=True).stdout.strip()


def yq(s):
    """Quote a scalar for YAML flow style."""
    if s is None:
        return "null"
    if isinstance(s, bool):
        return "true" if s else "false"
    if isinstance(s, (int, float)):
        return repr(s)
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"') + '"'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--command", required=True)
    ap.add_argument("--params", required=True, help="JSON object string")
    ap.add_argument("--validity-status", required=True)
    ap.add_argument("--validity-reason", required=True)
    args = ap.parse_args()

    raw_path = os.path.join(args.run_dir, "raw.json")
    raw = {}
    if os.path.exists(raw_path):
        with open(raw_path) as f:
            raw = json.load(f)

    commit = git(["rev-parse", "HEAD"])
    dirty = bool(git(["status", "--porcelain"]))
    sage_ver = subprocess.run(["sage", "--version"], capture_output=True,
                              text=True).stdout.strip()
    py_ver = subprocess.run(["sage", "-python", "-c", "import sys;print(sys.version.split()[0])"],
                            capture_output=True, text=True).stdout.strip()
    uname = subprocess.run(["uname", "-srm"], capture_output=True, text=True).stdout.strip()

    arts = {}
    for key, fn in (("raw_results", "raw.json"), ("stdout_log", "stdout.txt"),
                    ("stderr_log", "stderr.txt")):
        p = os.path.join(args.run_dir, fn)
        if os.path.exists(p):
            arts[key] = {"path": os.path.relpath(p, REPO + "/experiments/EXP-ICI-001"),
                         "sha256": sha256_of(p), "bytes": os.path.getsize(p)}

    cells = raw.get("cells", [])
    cell_summary = [{"n": c.get("n"), "curve_seed": c.get("curve_seed"),
                     "status": c.get("status"),
                     "n_measured": c.get("n_targets_measured")} for c in cells]

    params = json.loads(args.params)

    lines = []
    lines.append("run: {id: %s, experiment_id: EXP-ICI-001," % yq(args.run_id))
    lines.append("  command: %s," % yq(args.command))
    lines.append("  git_commit: %s, dirty_tree: %s," % (yq(commit), yq(dirty)))
    lines.append("  parameters: %s," % json.dumps(params))
    lines.append("  environment: {os: %s, sage_version: %s, sage_python: %s}," %
                 (yq(uname), yq(sage_ver), yq(py_ver)))
    lines.append("  timing: {started_at: %s, finished_at: %s, wall_seconds: %s}," %
                 (yq(raw.get("started_at")), yq(raw.get("finished_at")),
                  yq(round(raw.get("wall_s", -1), 3))))
    lines.append("  resources: {peak_rss_bytes: %s}," % yq(raw.get("peak_rss_bytes")))
    art_strs = []
    for k, v in arts.items():
        art_strs.append("%s: {path: %s, sha256: %s, bytes: %d}" %
                        (k, yq(v["path"]), yq(v["sha256"]), v["bytes"]))
    lines.append("  artifacts: {%s}," % ", ".join(art_strs))
    lines.append("  cell_summary: %s," % json.dumps(cell_summary))
    lines.append("  validity_status: %s, validity_reason: %s}" %
                 (yq(args.validity_status), yq(args.validity_reason)))

    mpath = os.path.join(args.run_dir, "manifest.yaml")
    with open(mpath, "w") as f:
        f.write("\n".join(lines) + "\n")
    print("wrote", mpath)


if __name__ == "__main__":
    main()
