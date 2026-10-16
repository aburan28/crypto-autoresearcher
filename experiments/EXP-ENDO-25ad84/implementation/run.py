#!/usr/bin/env python3
"""EXP-ENDO-25ad84: isogenous-model scalar-multiplication screen, one frozen run.

Runs harness/endosweep/isomodel.py over the verified deployed registry and the
std-curves corpus at a pinned commit, with the frozen parameters below, and
writes the raw result, the per-curve rows and a manifest.  Observations only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path

EXPERIMENT_ID = "EXP-ENDO-25ad84"
RUN_ID = "RUN-ENDO-d7cb69"
STD_CURVES_URL = "https://github.com/J08nY/std-curves.git"
STD_CURVES_COMMIT = "77fe6e3585ca2c2225b59d7df24b7c775437276f"
FROZEN = ["--ells", "2,3,5,7,11,13", "--depth", "2", "--max-nodes", "64", "--disc-bound", "1048576",
          "--samples", "200", "--verify-scalars", "8", "--max-bits", "521", "--seed", "20261016"]
REPO = Path(__file__).resolve().parents[3]


def git(*args: str, cwd: Path) -> str:
    return subprocess.check_output(["git", *args], cwd=cwd, text=True).strip()


def std_curves() -> Path:
    """The pinned std-curves checkout: $ISOMODEL_STD_CURVES, else a cache clone."""
    root = Path(os.environ.get("ISOMODEL_STD_CURVES")
                or Path.home() / ".cache" / f"std-curves-{STD_CURVES_COMMIT[:12]}")
    if not (root / ".git").exists():
        subprocess.check_call(["git", "clone", "-q", STD_CURVES_URL, str(root)])
    if git("rev-parse", "HEAD", cwd=root) != STD_CURVES_COMMIT:
        subprocess.check_call(["git", "checkout", "-q", STD_CURVES_COMMIT], cwd=root)
    head = git("rev-parse", "HEAD", cwd=root)
    if head != STD_CURVES_COMMIT or git("status", "--porcelain", cwd=root):
        raise SystemExit(f"std-curves checkout is not the pinned clean commit ({head})")
    return root


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--trial-plan", required=True)
    ap.add_argument("--run-dir", required=True)
    args = ap.parse_args()
    run_dir = Path(args.run_dir)
    out = run_dir / "isomodel"
    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    root = std_curves()
    cmd = [sys.executable, "-m", "harness.endosweep.isomodel", "--std-curves", str(root),
           "--out-dir", str(out), *FROZEN]
    t0 = time.time()
    proc = subprocess.run(cmd, cwd=REPO, text=True, capture_output=True)
    (run_dir / "isomodel-stdout.log").write_text(proc.stdout)
    (run_dir / "isomodel-stderr.log").write_text(proc.stderr)
    if proc.returncode != 0:
        print(proc.stderr[-4000:], file=sys.stderr)
        return proc.returncode
    shutil.copyfile(out / "isomodel.json", run_dir / "raw-result.json")
    shutil.copyfile(out / "rows.jsonl", run_dir / "rows.jsonl")
    shutil.copyfile(out / "isomodel.md", run_dir / "table.md")
    raw = json.loads((run_dir / "raw-result.json").read_text())
    rows = raw["rows"]
    import yaml
    manifest = {
        "experiment_id": EXPERIMENT_ID, "run_id": RUN_ID,
        "command": " ".join(cmd), "frozen_arguments": FROZEN,
        "repository_commit": git("rev-parse", "HEAD", cwd=REPO),
        "repository_dirty": bool(git("status", "--porcelain", "--", "harness", cwd=REPO)),
        "std_curves": {"url": STD_CURVES_URL, "commit": STD_CURVES_COMMIT},
        "python": sys.version, "platform": platform.platform(),
        "python_flint": __import__("flint").__version__, "sympy": __import__("sympy").__version__,
        "started_utc": started, "finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "wall_seconds": round(time.time() - t0, 1),
        "rows": len(rows), "rows_with_error": sum(1 for r in rows if "error" in r),
        "artifacts": {name: sha256(run_dir / name) for name in ("raw-result.json", "rows.jsonl", "table.md")},
        "claim_tier": "modelled operation counts; no timing, no ECDLP claim",
        "validity": "valid" if rows else "invalid",
    }
    (run_dir / "manifest.yaml").write_text(yaml.safe_dump(manifest, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
