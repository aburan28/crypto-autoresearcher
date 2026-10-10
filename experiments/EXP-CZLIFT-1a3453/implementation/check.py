"""Independent checker for EXP-CZLIFT-1a3453: reproduces one curve per arm, re-derives the summary."""
from __future__ import annotations

import json
import os
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
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
    seed = manifest["inputs"]["seed"]
    curves = raw["raw"]["curves"]
    for arm in ("cm_canonical", "random_naive"):
        rec = next((c for c in curves if c["arm"] == arm), None)
        if rec is None:
            print(f"arm {arm} missing", file=sys.stderr)
            return 1
        fresh = driver.measure_curve(arm, rec["p"], rec["A"], rec["B"], rec["N"], rec["n"], seed=seed, label=rec["label"])
        for a, b in zip(fresh["rows"], rec["rows"]):
            for key in ("coord", "digit", "above", "shuffled_above", "uniform_above"):
                if a[key] != b[key]:
                    print(f"{arm} p={rec['p']}: {key} does not reproduce", file=sys.stderr)
                    return 1
            for key in ("max_power", "threshold", "shuffled_max_power", "uniform_max_power"):
                if abs(a[key] - b[key]) > 1e-6 * max(1.0, abs(b[key])):
                    print(f"{arm} p={rec['p']}: {key} does not reproduce", file=sys.stderr)
                    return 1
    fresh_summary = driver.summarize(curves)
    for key, value in fresh_summary.items():
        if key == "by_digit":
            continue
        rv = raw["metrics"].get(key)
        if isinstance(value, float):
            if rv is None or abs(rv - value) > 1e-9 * max(1.0, abs(value)):
                print(f"summary {key} does not re-derive", file=sys.stderr)
                return 1
        elif rv != value:
            print(f"summary {key} does not re-derive", file=sys.stderr)
            return 1
    print("check ok: one curve per arm reproduces, summary re-derives")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
