#!/usr/bin/env python3
"""EXP-ENDO-7494e7: combined route (2-GLV on a cheaper-model isogenous neighbour), one frozen run.

Reads the committed RUN-ENDO-d7cb69 rows and runs harness/endosweep/isoglv.py
on the seven population curves with a positive model-change gain plus the two
frozen controls.  Observations only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

EXPERIMENT_ID = "EXP-ENDO-7494e7"
RUN_ID = "RUN-ENDO-795989"
SOURCE_ROWS = "experiments/EXP-ENDO-25ad84/runs/RUN-ENDO-d7cb69/raw-result.json"
SOURCE_ROWS_SHA256 = "0576225d496168485a8c30d5d460edab1ab969e7cd3a4d7850e43406a65282da"
CONTROLS = "control+ascent: 11-descendant of a j = 0 curve (256-bit),mnt/mnt5/1"
FROZEN = ["--ells", "2,3,5,7,11,13", "--depth", "2", "--max-nodes", "64", "--disc-bound", "2000000",
          "--build-limit", "3", "--build-seconds", "900", "--max-candidates", "12", "--verify-scalars", "8",
          "--seed", "20261016", "--include", CONTROLS]
REPO = Path(__file__).resolve().parents[3]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--trial-plan", required=True)
    ap.add_argument("--run-dir", required=True)
    args = ap.parse_args()
    run_dir = Path(args.run_dir)
    if sha256(REPO / SOURCE_ROWS) != SOURCE_ROWS_SHA256:
        print("source rows changed", file=sys.stderr)
        return 2
    out = Path(tempfile.mkdtemp(prefix="isoglv-"))
    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    cmd = [sys.executable, "-m", "harness.endosweep.isoglv", "--rows", SOURCE_ROWS, "--out-dir", str(out), *FROZEN]
    t0 = time.time()
    proc = subprocess.run(cmd, cwd=REPO)
    if proc.returncode != 0:
        return proc.returncode
    shutil.copyfile(out / "isoglv.json", run_dir / "raw-result.json")
    shutil.copyfile(out / "rows.jsonl", run_dir / "rows.jsonl")
    rows = json.loads((run_dir / "raw-result.json").read_text())["rows"]
    import yaml
    git = lambda *c: subprocess.check_output(["git", *c], cwd=REPO, text=True).strip()
    manifest = {
        "experiment_id": EXPERIMENT_ID, "run_id": RUN_ID, "command": " ".join(cmd), "frozen_arguments": FROZEN,
        "source_rows": {"path": SOURCE_ROWS, "sha256": SOURCE_ROWS_SHA256},
        "repository_commit": git("rev-parse", "HEAD"),
        "repository_dirty": bool(git("status", "--porcelain", "--", "harness")),
        "python": sys.version, "platform": platform.platform(),
        "python_flint": __import__("flint").__version__, "sympy": __import__("sympy").__version__,
        "started_utc": started, "finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "wall_seconds": round(time.time() - t0, 1), "rows": len(rows),
        "rows_with_error": sum(1 for r in rows if "error" in r),
        "artifacts": {name: sha256(run_dir / name) for name in ("raw-result.json", "rows.jsonl")},
        "claim_tier": "modelled operation counts; no timing, no ECDLP claim",
        "validity": "valid" if rows else "invalid",
    }
    (run_dir / "manifest.yaml").write_text(yaml.safe_dump(manifest, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
