"""Resume EXP-FIB-001 after RUN-FIB-006 failed with an implementation bug
(statslib.tail_checks crashed on a placeholder costs=[None,...] list because
a non-empty list of Nones is truthy in Python). RUN-FIB-001..005 and
RUN-FIB-007 completed_valid and are reloaded from disk unchanged (immutable,
not rerun). The corrected correlation-decision run is written under a NEW
run id, RUN-FIB-006B, per the run-record immutability rule (the defective
RUN-FIB-006 stays in the ledger marked failed_implementation with its
reason). RUN-FIB-008 and the final analysis.md/execution-report.yaml then
proceed using RUN-FIB-006B's results.
"""
from __future__ import annotations

import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from . import orchestrate as orch  # noqa: E402
from . import runlib, statslib  # noqa: E402

EXP_DIR = orch.EXP_DIR


def _load(run_id):
    with open(os.path.join(EXP_DIR, "runs", run_id, "raw.json")) as f:
        raw = json.load(f)
    return raw


def main():
    r2_raw = _load("RUN-FIB-002")
    r3_raw = _load("RUN-FIB-003")
    r4_raw = _load("RUN-FIB-004")
    r5_raw = _load("RUN-FIB-005")
    r7_raw = _load("RUN-FIB-007")

    results = {}
    for rid in ("RUN-FIB-001", "RUN-FIB-002", "RUN-FIB-003", "RUN-FIB-004", "RUN-FIB-005",
                "RUN-FIB-007"):
        with open(os.path.join(EXP_DIR, "runs", rid, "manifest.yaml")) as f:
            import yaml
            m = yaml.safe_load(f)["run"]
        results[rid] = {"run_id": rid, "status": m["status"],
                         "wall_seconds": m["timing"]["wall_seconds"],
                         "raw": _load(rid), "summary": json.load(
                             open(os.path.join(EXP_DIR, "runs", rid, "summary.json")))}
    # keep the defective RUN-FIB-006 in the tally, honestly, as failed_implementation
    with open(os.path.join(EXP_DIR, "runs", "RUN-FIB-006", "manifest.yaml")) as f:
        import yaml
        m6 = yaml.safe_load(f)["run"]
    results["RUN-FIB-006"] = {"run_id": "RUN-FIB-006", "status": m6["status"],
                                "wall_seconds": m6["timing"]["wall_seconds"],
                                "raw": {}, "summary": {}}

    orch.deviations_log.append(
        "RUN-FIB-006 failed_implementation: statslib.tail_checks crashed on a "
        "placeholder costs=[None]*n list (truthiness bug: a non-empty list of "
        "Nones is truthy). Fixed in statslib.py (guard requires all(c is not "
        "None for c in costs)). The defective RUN-FIB-006 directory is kept, "
        "unmodified, marked failed_implementation; the corrected correlation "
        "decision was re-run as a NEW run id, RUN-FIB-006B, per the run-record "
        "immutability rule (never overwrite/delete/re-key a run directory)."
    )

    r6b = orch._run(
        "RUN-FIB-006B",
        "python3 -m driver.resume  # RUN-FIB-006B: corrected retry of the correlation "
        "decision run (RUN-FIB-006 failed_implementation; statslib.tail_checks bug fixed)",
        {"permutation_replicates": statslib.PERMUTATION_REPLICATES,
         "correlation_prefix_min": orch.CORRELATION_PREFIX_MIN,
         "supersedes": "RUN-FIB-006 (failed_implementation)"},
        {"permutation_seed": orch.PERM_SEED},
        lambda: orch.run_fib_006(r2_raw, r3_raw, r4_raw, r5_raw),
    )
    results["RUN-FIB-006B"] = r6b

    ratios = orch.compute_predictor_cost_ratio(r7_raw, r4_raw, r5_raw)
    cost_gate_curves = [cid for cid, ratio in ratios.items() if ratio is not None and ratio <= 0.1]
    correlation_gate_pass = r6b["summary"]["correlation_gate_pass_overall"]
    cost_gate_pass = len(cost_gate_curves) >= 3
    gate_pass = correlation_gate_pass and cost_gate_pass
    gate_reason = (
        f"correlation_gate_pass={correlation_gate_pass} "
        f"(curves passing: {r6b['summary']['correlation_gate_curves_passing']}); "
        f"predictor_cost_gate_pass={cost_gate_pass} (ratios: {ratios}); "
        "RUN-FIB-008 requires both gates to pass on the frozen protocol."
    )
    print(gate_reason, file=sys.stderr)

    r8 = orch._run(
        "RUN-FIB-008", "python3 -m driver.resume  # RUN-FIB-008: gated two-phase (secondary)",
        {"gate_pass": gate_pass}, {"instance_seeds": [1, 2]},
        lambda: orch.run_fib_008(gate_pass, gate_reason, r4_raw, r5_raw, r6b["raw"], r7_raw, ratios),
    )
    results["RUN-FIB-008"] = r8

    orch._write_final_artifacts(results, ratios, gate_pass, gate_reason,
                                  correlation_run_id="RUN-FIB-006B")
    print("DONE", results.keys())


if __name__ == "__main__":
    main()
