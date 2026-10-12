"""Independent checker for EXP-CZLIFT-a255fc run directories.

Re-verifies every recorded sample point on its curve exactly; re-counts the
height grid for the first two curves with a slow scalar re-search at a reduced
height and compares; re-derives the summary from the recorded per-curve
records; checks coverage fractions are in [0, 1] and distinct <= N_p; checks
the manifest. A failure here is invalid output, never a result.
"""
from __future__ import annotations

import json
import math
import os
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run as driver  # noqa: E402


def slow_count(ai, H: int) -> int:
    b2, b4, b6, _ = driver.b_invariants(ai)
    n = 1
    for d in range(1, math.isqrt(H) + 1):
        for a in range(-H, H + 1):
            if math.gcd(a, d) != 1:
                continue
            g = driver.g_exact(a, d, b2, b4, b6)
            if g < 0:
                continue
            c = math.isqrt(g)
            if c * c == g:
                n += 1 if c == 0 else 2
    return n


def main(argv=None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print("usage: check.py RUN_DIR", file=sys.stderr)
        return 1
    run_dir = args[0]
    raw = json.load(open(os.path.join(run_dir, "raw-result.json")))
    manifest = yaml.safe_load(open(os.path.join(run_dir, "manifest.yaml")))["run"]
    if manifest["experiment_id"] != driver.EXP_ID or manifest["status"] != "completed_valid":
        print("manifest experiment id / status mismatch", file=sys.stderr)
        return 1
    curves = raw["raw"]["curves"]
    if [c["label"] for c in curves] != [c[0] for c in driver.CURVES]:
        print("curve list differs from the frozen ladder", file=sys.stderr)
        return 1
    for cv in curves:
        b2, b4, b6, _ = driver.b_invariants(cv["ainvs"])
        for a, d, c in cv["points_sample"]:
            if driver.g_exact(a, d, b2, b4, b6) != c * c or math.gcd(a, d) != 1:
                print(f"sample point {(a, d, c)} is not on {cv['label']}", file=sys.stderr)
                return 1
        for cell in cv["coverage"]:
            if not (0 <= cell["coverage"] <= 1) or cell["distinct"] > cell["N_p"]:
                print("coverage cell out of range", file=sys.stderr)
                return 1
    for cv in curves[:2]:
        H = 300
        if str(H) in cv["counts"] and slow_count(cv["ainvs"], H) != cv["counts"][str(H)]:
            print(f"height-{H} count for {cv['label']} does not reproduce", file=sys.stderr)
            return 1
    fresh = driver.summarize(curves)
    for key, value in fresh.items():
        if raw["metrics"].get(key) != value:
            print(f"summary field {key} does not re-derive", file=sys.stderr)
            return 1
    print("check ok: sample points verify, counts reproduce, summary re-derives")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
