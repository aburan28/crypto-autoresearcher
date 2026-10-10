"""Independent checker for EXP-CZLIFT-17b7eb run directories.

Recomputes the first two curves of the sweep from the recorded seed and
compares them row by row with raw-result.json; re-derives every summary
number from the recorded rows; and checks the manifest names this experiment
and the run id. A checker failure is an invalid output, never a result.
"""
from __future__ import annotations

import json
import os
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import run as driver  # noqa: E402
from harness import czlift  # noqa: E402


def main(argv=None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print("usage: check.py RUN_DIR", file=sys.stderr)
        return 1
    run_dir = args[0]
    raw = json.load(open(os.path.join(run_dir, "raw-result.json")))
    manifest = yaml.safe_load(open(os.path.join(run_dir, "manifest.yaml")))["run"]
    if manifest["experiment_id"] != driver.EXP_ID:
        print("manifest experiment id mismatch", file=sys.stderr)
        return 1
    if manifest["status"] != "completed_valid":
        print("manifest status is not completed_valid", file=sys.stderr)
        return 1
    params = manifest["inputs"]["parameters"]
    seed = manifest["inputs"]["seed"]
    curves = raw["raw"]["curves"]
    if not curves:
        print("no curves recorded", file=sys.stderr)
        return 1
    expected = czlift.anomalous_cm_curves(params["pmax"])
    if [(c["D"], c["p"]) for c in curves] != [(D, p) for D, p, *_ in expected]:
        print("curve list differs from a fresh enumeration", file=sys.stderr)
        return 1
    for D, p, A, B, j in expected[:2]:
        rec = next(c for c in curves if c["p"] == p and c["D"] == D)
        fresh = driver.measure_curve(D, p, A, B, j, seed=seed, samples=params["samples"],
                                     per_class=params["per_class"])
        if fresh["rows"] != rec["rows"]:
            print(f"rows for (D={D}, p={p}) do not reproduce", file=sys.stderr)
            return 1
    fresh_summary = driver.summarize(curves)
    recorded = raw["metrics"]
    for key, value in fresh_summary.items():
        if recorded.get(key) != value:
            print(f"summary field {key} does not re-derive from the rows", file=sys.stderr)
            return 1
    for c in curves:
        for r in c["rows"]:
            if r["degenerate"] != (r["vP"] >= 2):
                print("degenerate flag inconsistent with vP", file=sys.stderr)
                return 1
            if r["success"] and not r["ratio_defined"]:
                print("success without a defined ratio", file=sys.stderr)
                return 1
    print("check ok: rows reproduce, summary re-derives, flags consistent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
