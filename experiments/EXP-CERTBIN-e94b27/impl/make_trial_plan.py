#!/usr/bin/env python3
"""Writes experiments/EXP-CERTBIN-e94b27/trial-plan-v1.json from the frozen
specification alone (spec execution.trial_plan_rule): input paths and hashes,
set-selection rules, phases, closures per set and output paths. It contains no
computed closure value and no instance index."""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import yaml  # noqa: E402

from common import (REPO, SPEC, INPUT_FILES, RECEIPT, S_SELFTEST, W5_WATCHDOG, RUN_WATCHDOG,  # noqa: E402
                    MEM_LIMIT, sha256_file, dump_json, now)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    if os.path.exists(a.out):
        print("trial plan exists; never overwritten", file=sys.stderr)
        return 1
    spec = yaml.safe_load(open(a.spec))["experiment"]
    assert spec["status"] == "approved" and spec["approved_by"] and spec["version"] == 1
    plan = {
        "schema": "certbin.rc1.trial_plan.v1",
        "experiment_id": spec["id"], "spec_version": spec["version"], "run_id": a.run_id,
        "specification": {"path": SPEC, "sha256": sha256_file(os.path.join(REPO, SPEC))},
        "written_at": now(),
        "contains_computed_values": False,
        "inputs": [{"path": p, "sha256": sha256_file(os.path.join(REPO, p))} for p in INPUT_FILES],
        "input_receipt": RECEIPT,
        "seeds": {"S_selftest": S_SELFTEST, "note": spec["replication"]["seeds_note"]},
        "instance_sets": {k: spec["instance_sets"][k] for k in ("U62", "S62", "C20", "N-AFF62", "N-F262")},
        "instance_set_expected_sizes": {"U62": 62, "S62": 62, "C20": 20, "N-AFF62": 62, "N-F262": 62},
        "missing_field_rule": spec["instance_sets"]["missing_field_rule"],
        "closures_run": spec["object"]["closures_run"],
        "closures_per_set": {
            "M_3,M_4 (C-BASE)": ["U62", "S62", "C20", "N-AFF62", "N-F262"],
            "W_4": ["U62", "S62", "C20", "N-AFF62", "N-F262"],
            "M_5": ["U62", "S62", "N-AFF62", "N-F262"],
            "W_5": {"U62": "every instance refuted by neither W_4 nor M_5 (verified or reported)",
                    "S62": "the 10 lowest-idx instances",
                    "N-AFF62": "up to the 10 lowest-idx instances refuted by neither W_4 nor M_5",
                    "N-F262": "up to the 10 lowest-idx instances refuted by neither W_4 nor M_5"},
        },
        "w5_selection_note": ("W_5 residual selection uses the closure outputs of phases 2-3 as REPORTED by "
                              "the engine (the verifier runs after all closures, phase 6)."),
        "controls": [c["id"] for c in spec["controls"]],
        "c_det_instances": "10 lowest-idx U62 and 5 lowest-idx S62: M_5 (rank_5, 1 in R_5) and W_4 (dim, iterations, 1 in W_4)",
        "phases": spec["execution"]["phases"],
        "watchdogs": {"run_seconds": RUN_WATCHDOG, "w5_per_instance_seconds": W5_WATCHDOG},
        "resources": {"memory_cap_bytes": MEM_LIMIT, "workers": 1, "maximum_runs": spec["budget"]["maximum_runs"]},
        "decision_rules": [d["id"] for d in spec["decision_rules"]],
        "commands": {"main": spec["execution"]["command"], "determinism": spec["execution"]["determinism_command"],
                     "verify": spec["execution"]["verify_command"]},
        "outputs": [x if isinstance(x, str) else str(x) for x in spec["required_artifacts"]],
        "run_dir": f"experiments/EXP-CERTBIN-e94b27/runs/{a.run_id}/",
    }
    dump_json(a.out, plan)
    print(f"wrote {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
