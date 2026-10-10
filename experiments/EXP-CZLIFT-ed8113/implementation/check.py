"""Independent checker for EXP-CZLIFT-ed8113: re-runs the smallest prime's cells and re-derives the summary."""
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
    params = manifest["inputs"]["parameters"]
    seed = manifest["inputs"]["seed"]
    cells = raw["raw"]["cells"]
    if not cells:
        print("no cells", file=sys.stderr)
        return 1
    p0 = cells[0]["p"]
    rec = [c for c in cells if c["p"] == p0]
    # Re-run the first prime and compare its two cells exactly.
    _, fresh_raw = driver.build(seed, params["trials_per_cell"], [p0])
    if fresh_raw["cells"] != rec:
        print(f"cells for p={p0} do not reproduce", file=sys.stderr)
        return 1
    m = raw["metrics"]
    valid = sum(c["valid"] for c in cells)
    dep = sum(c["dependent"] for c in cells)
    if m["valid_trials_total"] != valid or m["dependent_total"] != dep:
        print("totals do not re-derive", file=sys.stderr)
        return 1
    if abs(m["dependence_rate_overall"] - dep / valid) > 1e-12:
        print("dependence rate does not re-derive", file=sys.stderr)
        return 1
    if m["control_detection_rate"] != sum(raw["raw"]["controls"]) / len(raw["raw"]["controls"]):
        print("control rate does not re-derive", file=sys.stderr)
        return 1
    for c in cells:
        for rel in c["relations"]:
            if not rel or max(abs(x) for x in rel) > driver.RELATION_BOUND:
                print("recorded relation outside the bound", file=sys.stderr)
                return 1
    print("check ok: first prime reproduces, totals re-derive, relations within bound")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
