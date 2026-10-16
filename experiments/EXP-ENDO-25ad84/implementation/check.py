#!/usr/bin/env python3
"""Integrity check for EXP-ENDO-25ad84 (not an outcome gate).

Fails on missing or altered artifacts, changed frozen parameters, a row
silently dropped, or a control row that does not recompute identically.
Scientific outcomes, including failed controls, are read in the report.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))
FROZEN_ARGS = {"ells": "2,3,5,7,11,13", "depth": 2, "max_nodes": 64, "disc_bound": 1048576,
               "samples": 200, "verify_scalars": 8, "max_bits": 521, "seed": 20261016}


def main() -> int:
    run_dir = Path(sys.argv[1])
    import yaml
    for name in ("manifest.yaml", "raw-result.json", "rows.jsonl", "table.md"):
        if not (run_dir / name).is_file():
            print(f"missing {name}", file=sys.stderr)
            return 1
    man = yaml.safe_load((run_dir / "manifest.yaml").read_text())
    for name, digest in man["artifacts"].items():
        if hashlib.sha256((run_dir / name).read_bytes()).hexdigest() != digest:
            print(f"{name} digest mismatch", file=sys.stderr)
            return 1
    raw = json.loads((run_dir / "raw-result.json").read_text())
    args = raw["provenance"]["args"]
    for k, v in FROZEN_ARGS.items():
        if args.get(k) != v:
            print(f"frozen parameter {k} changed: {args.get(k)!r}", file=sys.stderr)
            return 1
    rows = raw["rows"]
    lines = [json.loads(l) for l in (run_dir / "rows.jsonl").read_text().splitlines() if l.strip()]
    if len(lines) != len(rows) or [r["name"] for r in lines] != [r["name"] for r in rows]:
        print("rows.jsonl and raw-result.json disagree", file=sys.stderr)
        return 1
    roles = {r.get("role") for r in rows}
    for role in ("control+model", "control+ascent", "control-"):
        if role not in roles:
            print(f"control role {role} absent", file=sys.stderr)
            return 1
    # recompute the two constructed control rows from their recorded curves
    from harness.endosweep import isomodel as IM
    from harness.endosweep.targets import Target, verify
    for r in rows:
        if r.get("role") not in ("control+model", "control+ascent"):
            continue
        T = verify(Target(r["name"], int(r["p"], 16), "weierstrass", {"a": int(r["a"], 16), "b": int(r["b"], 16)},
                          int(r["n"], 16), r["cofactor"], family="control"))
        again = IM.screen_curve(T, ells=[int(x) for x in FROZEN_ARGS["ells"].split(",")], depth=FROZEN_ARGS["depth"],
                                max_nodes=FROZEN_ARGS["max_nodes"], disc_bound=FROZEN_ARGS["disc_bound"],
                                samples=FROZEN_ARGS["samples"], verify_scalars=FROZEN_ARGS["verify_scalars"],
                                seed=FROZEN_ARGS["seed"], role=r["role"])
        for key in ("baseline", "best", "ascent", "instrument_check"):
            if json.dumps(again[key], sort_keys=True) != json.dumps(r[key], sort_keys=True):
                print(f"{r['name']}: {key} does not recompute", file=sys.stderr)
                return 1
    print(f"ok: {len(rows)} rows, {sum(1 for r in rows if 'error' in r)} with recorded errors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
