#!/usr/bin/env python3
"""EXP-ENDO-33a1ee: timed isogenous-model scalar multiplication, one frozen run.

Runs harness/endosweep/isobench on other/BADA55-VPR-224 (target) and on the
constructed 3-isogenous neighbour of NIST P-256 (positive control), with the
frozen point count, repetitions and compiler flags.  Observations only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
import time
from pathlib import Path

EXPERIMENT_ID = "EXP-ENDO-33a1ee"
RUN_ID = "RUN-ENDO-bc1b14"
SOURCE_ROWS = "experiments/EXP-ENDO-25ad84/runs/RUN-ENDO-d7cb69/raw-result.json"
SOURCE_ROWS_SHA256 = "0576225d496168485a8c30d5d460edab1ab969e7cd3a4d7850e43406a65282da"
CURVES = {"target": "other/BADA55-VPR-224", "control": "control+: 3-isogenous neighbour of NIST P-256"}
FROZEN = ["--points", "64", "--reps", "41", "--bootstrap", "4000", "--seed", "20261016", "--cflags=-O2 -march=native"]
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
    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    t0 = time.time()
    cmds = {}
    for role, curve in CURVES.items():
        out = run_dir / role
        cmd = [sys.executable, "-m", "harness.endosweep.isobench.isobench", "--rows", SOURCE_ROWS,
               "--curve", curve, "--out-dir", str(out), *FROZEN]
        cmds[role] = cmd
        rc = subprocess.run(cmd, cwd=REPO).returncode
        if rc != 0:
            print(f"{role}: isobench exited {rc}", file=sys.stderr)
            return rc
    import yaml
    git = lambda *c: subprocess.check_output(["git", *c], cwd=REPO, text=True).strip()
    files = [f"{role}/{name}" for role in CURVES for name in
             ("summary.json", "timings.json", "bench-input.txt", "bench-output.txt")]
    summ = {role: json.loads((run_dir / role / "summary.json").read_text()) for role in CURVES}
    (run_dir / "raw-result.json").write_text(json.dumps(summ, indent=1))
    lscpu = subprocess.run(["lscpu"], capture_output=True, text=True).stdout
    manifest = {
        "experiment_id": EXPERIMENT_ID, "run_id": RUN_ID,
        "commands": {k: " ".join(v) for k, v in cmds.items()}, "frozen_arguments": FROZEN, "curves": CURVES,
        "source_rows": {"path": SOURCE_ROWS, "sha256": SOURCE_ROWS_SHA256},
        "repository_commit": git("rev-parse", "HEAD"),
        "repository_dirty": bool(git("status", "--porcelain", "--", "harness")),
        "python": sys.version, "platform": platform.platform(), "lscpu": lscpu,
        "started_utc": started, "finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "wall_seconds": round(time.time() - t0, 1),
        "artifacts": {name: sha256(run_dir / name) for name in ["raw-result.json", *files]},
        "claim_tier": "measured wall-clock on one shared cloud host; known-scalar multiplication only, no ECDLP claim",
        "validity": "valid" if all(s["correct"] for s in summ.values()) else "invalid",
    }
    (run_dir / "manifest.yaml").write_text(yaml.safe_dump(manifest, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
