"""Second correction pass: RUN-FIB-006B (completed_valid) computed the
correlation, label-shuffle, and Poisson/tail-check results correctly for the
one curve with sufficient decomposition-cost data (C16-1), but incorrectly
*skipped* the Poisson-fit / extreme-value / zero-class checks (CTRL-
QUASIRANDOM-DISTRIBUTION) for the three resource_exhaustion curves even
though those checks depend only on the n_R histogram (RUN-FIB-002/003), never
on decomposition-cost data -- a scope gap, not a crash. Fixed in
orchestrate.run_fib_006. RUN-FIB-006B is left in the ledger, unmodified,
still `completed_valid` (its own reported results were not wrong, merely
incomplete in scope); this produces the complete version under a NEW run id,
RUN-FIB-006C, which is authoritative for the final analysis. RUN-FIB-008's
gate decision is unaffected (it depends only on the correlation/cost gates,
neither of which changes) and is not re-run.
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from . import orchestrate as orch  # noqa: E402
from . import statslib  # noqa: E402
import yaml  # noqa: E402

EXP_DIR = orch.EXP_DIR


def _load(run_id):
    with open(os.path.join(EXP_DIR, "runs", run_id, "raw.json")) as f:
        return json.load(f)


def main():
    r2_raw = _load("RUN-FIB-002")
    r3_raw = _load("RUN-FIB-003")
    r4_raw = _load("RUN-FIB-004")
    r5_raw = _load("RUN-FIB-005")
    r7_raw = _load("RUN-FIB-007")

    results = {}
    for rid in ("RUN-FIB-001", "RUN-FIB-002", "RUN-FIB-003", "RUN-FIB-004", "RUN-FIB-005",
                "RUN-FIB-007", "RUN-FIB-006", "RUN-FIB-006B", "RUN-FIB-008"):
        with open(os.path.join(EXP_DIR, "runs", rid, "manifest.yaml")) as f:
            m = yaml.safe_load(f)["run"]
        raw = {}
        summary = {}
        if m["status"] not in ("failed_implementation", "cancelled_by_gate") or rid == "RUN-FIB-008":
            try:
                raw = _load(rid)
                summary = json.load(open(os.path.join(EXP_DIR, "runs", rid, "summary.json")))
            except Exception:
                pass
        results[rid] = {"run_id": rid, "status": m["status"],
                         "wall_seconds": m["timing"]["wall_seconds"], "raw": raw, "summary": summary}

    orch.deviations_log.append(
        "RUN-FIB-006B completed_valid but scoped CTRL-QUASIRANDOM-DISTRIBUTION "
        "(Poisson fit) and the extreme-value/zero-class tail checks to only the "
        "one curve (C16-1) with sufficient decomposition-cost data, even though "
        "those checks depend solely on the n_R histogram (RUN-FIB-002/003), not "
        "on decomposition-cost data -- an incompleteness, not a crash. Fixed in "
        "orchestrate.run_fib_006 (poisson_fit/tail_checks now computed for every "
        "curve). RUN-FIB-006B is left unmodified in the ledger, still "
        "completed_valid; RUN-FIB-006C is the complete, authoritative version "
        "per the run-record immutability rule."
    )

    r6c = orch._run(
        "RUN-FIB-006C",
        "python3 -m driver.resume2  # RUN-FIB-006C: complete correlation decision run "
        "(RUN-FIB-006B scoped the Poisson fit/tail checks to only 1 of 4 curves; fixed)",
        {"permutation_replicates": statslib.PERMUTATION_REPLICATES,
         "correlation_prefix_min": orch.CORRELATION_PREFIX_MIN,
         "supersedes": "RUN-FIB-006 (failed_implementation), RUN-FIB-006B (scope-incomplete)"},
        {"permutation_seed": orch.PERM_SEED},
        lambda: orch.run_fib_006(r2_raw, r3_raw, r4_raw, r5_raw),
    )
    results["RUN-FIB-006C"] = r6c

    ratios = orch.compute_predictor_cost_ratio(r7_raw, r4_raw, r5_raw)
    cost_gate_curves = [cid for cid, ratio in ratios.items() if ratio is not None and ratio <= 0.1]
    correlation_gate_pass = r6c["summary"]["correlation_gate_pass_overall"]
    cost_gate_pass = len(cost_gate_curves) >= 3
    gate_pass = correlation_gate_pass and cost_gate_pass
    gate_reason = (
        f"correlation_gate_pass={correlation_gate_pass} "
        f"(curves passing: {r6c['summary']['correlation_gate_curves_passing']}); "
        f"predictor_cost_gate_pass={cost_gate_pass} (ratios: {ratios}); "
        "RUN-FIB-008 requires both gates to pass on the frozen protocol. "
        "(Unchanged from the RUN-FIB-006B-based decision; RUN-FIB-008 was not re-run.)"
    )
    print(gate_reason, file=sys.stderr)

    orch._write_final_artifacts(results, ratios, gate_pass, gate_reason,
                                  correlation_run_id="RUN-FIB-006C")
    print("DONE", list(results.keys()))


if __name__ == "__main__":
    main()
