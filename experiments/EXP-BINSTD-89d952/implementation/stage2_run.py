#!/usr/bin/env python3
"""Stage 2 for EXP-BINSTD-89d952: feasibility / peak_rss / instrument_unavailable report."""
from __future__ import annotations

import sys
import time
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from runpack import (  # noqa: E402
    EXP_ID,
    EXP_ROOT,
    TASK_ID,
    dump_yaml,
    peak_rss_bytes,
    utc_now,
    write_run_package,
)

RUN_ID = "RUN-BINSTD-a5d4b9"


def main() -> None:
    stage1 = EXP_ROOT / "stage1"
    if not (stage1 / "instrument_unavailable.yaml").exists() and not (
        stage1 / "arm-comparison.yaml"
    ).exists():
        raise SystemExit("REFUSE: Stage 1 terminal artifact missing")

    started = utc_now()
    t0 = time.time()
    stage2 = EXP_ROOT / "stage2"
    stage2.mkdir(parents=True, exist_ok=True)

    unavail = yaml.safe_load((stage1 / "instrument_unavailable.yaml").read_text())
    d6_path = stage1 / "d6-nonprotocol-probe.yaml"
    d6 = yaml.safe_load(d6_path.read_text()) if d6_path.exists() else None
    controls = yaml.safe_load((stage1 / "controls-report.yaml").read_text())

    # Analytic Macaulay size at D=4 vs D=6 for nv=15 (squarefree)
    def nmon(nv, D):
        from math import comb

        return sum(comb(nv, d) for d in range(D + 1))

    nv, neq = 15, 19
    analytic = {
        "nv": nv,
        "neq": neq,
        "D4": {
            "n_columns": nmon(nv, 4),
            "n_rows_if_eqdeg_le4_mu0": neq,  # would apply if deg<=4
            "note": "Equations have deg 6; D4 column space cannot host them",
        },
        "D6": {
            "n_columns": nmon(nv, 6),
            "n_rows_mu0": neq,
            "packed_nbytes_estimate": neq * ((nmon(nv, 6) + 63) // 64) * 8,
        },
        "label": "MODELED_analytic_size",
    }

    peak_from_stage1 = []
    for arm, rec in unavail.get("per_arm", {}).items():
        peak_from_stage1.append(
            {
                "arm": arm,
                "peak_rss_after_descend": rec.get("peak_rss_after_descend"),
                "max_boolean_degree": rec.get("descend_meta", {}).get("max_boolean_degree"),
                "macaulay_build_ok_D4": rec.get("macaulay_build_ok"),
            }
        )

    d6_measured = {}
    if d6:
        for arm, rec in d6.get("probes", {}).items():
            d6_measured[arm] = {
                "macaulay_build_ok": rec.get("macaulay_build_ok"),
                "macaulay_shape": rec.get("macaulay_shape"),
                "peak_rss_bytes": rec.get("peak_rss_bytes"),
                "wall_s": rec.get("wall_s"),
                "label": "MEASURED_non_protocol",
            }

    report = {
        "experiment_id": EXP_ID,
        "task_id": TASK_ID,
        "stage": 2,
        "DO_outcome_id": "DO-5",
        "instrument_unavailable": True,
        "macaulay_build_ok": False,
        "macaulay_build_ok_protocol_D4": False,
        "peak_rss_bytes": peak_rss_bytes(),
        "peak_rss_stage1_descend": peak_from_stage1,
        "analytic_macaulay_size": analytic,
        "reconcile_RSS_vs_analytic": {
            "protocol_D4": "N/A — build refused (degree 6 > D 4)",
            "non_protocol_D6": d6_measured,
            "note": (
                "Measured D6 Macaulay matrices are tiny (~19 rows × 9949 cols); "
                "RSS dominated by interpreter/field tables, not the matrix. "
                "Optimistic 4 GiB assumption for D4 was moot: algebraic degree, "
                "not memory, blocked the frozen instrument."
            ),
        },
        "further_seeds_run": False,
        "seeds_planned": [20260922, 20260926, 20261001, 20261002, 20261003],
        "seeds_run_for_arm_ratio": [],
        "reason_seeds_stopped": (
            "Frozen S_4/W_4@D=4 unreachable on both arms at primary seed; "
            "additional seeds cannot recover a degree obstruction."
        ),
        "controls_summary": {
            name: {
                "certificate_pass_rate": controls["controls"][name].get(
                    "certificate_pass_rate"
                ),
                "n_decomposable_targets_primary": controls["controls"][name].get(
                    "n_decomposable_targets_primary"
                ),
            }
            for name in controls.get("controls", {})
            if "certificate_pass_rate" in controls["controls"][name]
        },
        "optimistic_assumptions_restated": [
            "Assuming S_4 Macaulay at 15 variables fits in 4 GiB is optimistic; "
            "feasibility is the first Stage-1 metric (HOLD-T).",
            "Review's #E=4*130873 for Koblitz re-verified MEASURED match.",
            "Equality prediction assumes no residual shape effect; not testable "
            "without the frozen instrument.",
            "CNF-XOR leaf counts are not interchangeable with S_4 op counts.",
        ],
        "no_break_or_rho_claim": True,
        "no_mu_orbit_constraint_encoded": True,
        "source_artifacts": {
            "instrument_unavailable": str(
                stage1 / "instrument_unavailable.yaml"
            ),
            "arm_comparison": str(stage1 / "arm-comparison.yaml"),
            "controls_report": str(stage1 / "controls-report.yaml"),
        },
    }
    dump_yaml(stage2 / "feasibility-report.yaml", report)

    finished = utc_now()
    wall = time.time() - t0
    write_run_package(
        RUN_ID,
        stage=2,
        arm="feasibility-report",
        seed=None,
        command="python3 experiments/EXP-BINSTD-89d952/implementation/stage2_run.py",
        parameters={"inherits": "Stage1-two-arm"},
        metrics={
            "instrument_unavailable": True,
            "macaulay_build_ok": False,
            "peak_rss_bytes": peak_rss_bytes(),
            "wall_s": wall,
            "termination_reason": "completed",
            "DO_outcome_id": "DO-5",
        },
        valid=True,
        invalid_reason=None,
        termination_reason="completed",
        stdout_text="Stage 2 feasibility-report.yaml written\n",
        started_at=started,
        finished_at=finished,
        wall_seconds=wall,
        certificate={
            "kind": "none",
            "verified": True,
            "note": "Feasibility / instrument_unavailable report only",
        },
    )
    print("Stage 2 complete", RUN_ID)


if __name__ == "__main__":
    main()
