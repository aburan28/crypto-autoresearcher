"""Independent checker for EXP-CZLIFT-ae0a13 run directories.

Recomputes the first curve of each arm from the recorded seed and compares
row by row; re-derives the summary from the rows; checks the invariants that
are theorems (torsion section reduces to its point; its [n]-multiple is O)
hold on every row; checks the manifest. A failure here is invalid output.
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
    params = manifest["inputs"]["parameters"]
    seed = manifest["inputs"]["seed"]
    curves = raw["raw"]["curves"]
    if not curves or not any(c["arm"] == "cm_canonical" for c in curves) \
            or not any(c["arm"] == "random_naive" for c in curves):
        print("both arms must be present", file=sys.stderr)
        return 1
    for arm in ("cm_canonical", "random_naive"):
        rec = next(c for c in curves if c["arm"] == arm)
        fresh = driver.measure_curve(arm, rec["p"], rec["A"], rec["B"], rec["N"], rec["n"],
                                     seed=seed, samples=params["samples"], label=rec["label"])
        if fresh["rows"] != rec["rows"]:
            print(f"rows for arm {arm}, p={rec['p']} do not reproduce", file=sys.stderr)
            return 1
    fresh_summary = driver.summarize(curves)
    for key, value in fresh_summary.items():
        if raw["metrics"].get(key) != value:
            print(f"summary field {key} does not re-derive from the rows", file=sys.stderr)
            return 1
    for c in curves:
        for r in c["rows"]:
            if not (r["tor_reduces"] and r["degenerate_tor"]):
                print("a torsion-section row violates a theorem-level invariant", file=sys.stderr)
                return 1
            for s in r["sections"].values():
                if s["success"] and not s["ratio_defined"]:
                    print("success without a defined ratio", file=sys.stderr)
                    return 1
    print("check ok: arms reproduce, summary re-derives, invariants hold")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
