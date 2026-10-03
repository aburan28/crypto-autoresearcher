#!/usr/bin/env python3
"""Stage 2 for EXP-BINSTD-b7344f: ICPERF schema + portfolio hold (TASK-20261001-8c14b5)."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from runpack import EXP_ID, TASK_ID, EXP_ROOT, dump_text, dump_yaml, utc_now, write_run_package  # noqa: E402

# Reuse a stage-2 run id — mint if needed; we have 5 IDs, used 1 stage0 + 4 stage1.
# Allocate one more for stage2.
RUN_STAGE2 = None  # set in main after allocate, or hardcode after mint


def stage2(run_id: str):
    assert (EXP_ROOT / "stage1" / "cost-shape-summary.yaml").exists()
    s1 = yaml.safe_load((EXP_ROOT / "stage1" / "cost-shape-summary.yaml").read_text())
    s0_floors = yaml.safe_load((EXP_ROOT / "stage0" / "product-law-floors.yaml").read_text())
    s0_v = yaml.safe_load((EXP_ROOT / "stage0" / "v-beta-table.yaml").read_text())

    started = utc_now()
    t0 = time.time()

    dump_yaml(
        EXP_ROOT / "stage2" / "icperf-distribution-schema.yaml",
        {
            "experiment_id": EXP_ID,
            "task_id": TASK_ID,
            "stage": 2,
            "schema_request_for": "RQ-ICPERF-94c86e",
            "status": "schema_only_not_executed",
            "columns": [
                {
                    "name": "cv_per_attempt",
                    "unit": "dimensionless",
                    "definition": "std/mean of per-instance solver opcounts; sat/unsat separate",
                },
                {
                    "name": "max_over_median",
                    "unit": "dimensionless",
                    "definition": "robust heavy-tail signature",
                },
                {
                    "name": "hill_alpha_tail_with_ci",
                    "unit": "dimensionless",
                    "definition": "Hill alpha with bootstrap 95% CI; indicative at N~400",
                },
                {
                    "name": "watchdog_exclusion_rate",
                    "unit": "fraction",
                    "definition": "infra exclusions / (infra + finished); never folded into CV",
                },
            ],
            "note": "Schema request only. No CDCL engines installed (IMP-no-cdcl). Do not treat W4 CV as CDCL evidence.",
        },
    )

    m_le_3_hold = all(
        f["exceeds_rho"] for f in s0_floors["floors"] if f["m"] in (2, 3)
    )
    v_hold = bool(s0_v.get("all_nonpositive_within_1e-9"))
    cv_ok = bool(s1.get("HEUR_H1_cv_lt_0_1", {}).get("unsat")) and bool(
        s1.get("HEUR_H1_cv_lt_0_1", {}).get("sat")
    )
    if v_hold and m_le_3_hold and cv_ok:
        do = "DO-1"
    elif v_hold and m_le_3_hold and not cv_ok:
        do = "DO-2"
    else:
        do = "DO-3"

    dump_text(
        EXP_ROOT / "stage2" / "portfolio-hold.md",
        f"""# Portfolio hold — EXP-BINSTD-b7344f Stage 2

Decision orientation: **{do}**

## Stage-0 arithmetic (modeled)

- V(β) ≤ 0 for all ρ ≥ 1 on the Stage-0 grid: `{v_hold}`
- Product-law FREE-oracle floors exceed rho at m ∈ {{2,3}}: `{m_le_3_hold}`
- Therefore a concurrent IC∪rho portfolio cannot improve expectation at m ≤ 3
  under the concentrated-IC / exponential-rho model (HOLD-U).

## Stage-1 controlled null (measured)

- Unsat CV: `{s1['primary_cv']['unsat']}`
- Sat CV: `{s1['primary_cv']['sat']}`
- HEUR-H1 (CV < 0.1) on both: `{cv_ok}`

W4 cost-shape is a **controlled null** only. IMP-no-cdcl remains: absence of
WDSat / CryptoMiniSat / CaDiCaL / Macaulay2 is infrastructure, not thin-tail
evidence about CDCL search.

## Claims refused

- No break, no exponent move, no deployed V(β*)>0, no CDCL heavy-tail claim,
  no positive portfolio authorization. m ≥ 4 remains an arity/oracle question,
  not a portfolio question.

## certificate.kind

Stage-2 artifacts use `certificate.kind: none`.
""",
    )

    metrics = {
        "decision_orientation": do,
        "stage0_V_nonpositive": v_hold,
        "stage0_m_le_3_floor_exceeds_rho": m_le_3_hold,
        "stage1_cv_ok": cv_ok,
    }
    write_run_package(
        run_id,
        stage=2,
        arm="icperf_schema_and_portfolio_hold",
        seed=None,
        command="python3 experiments/EXP-BINSTD-b7344f/implementation/stage2_run.py",
        parameters={"curve_id": None},
        metrics=metrics,
        valid=True,
        invalid_reason=None,
        termination_reason="completed",
        stdout_text=json.dumps(metrics, indent=2),
        started_at=started,
        finished_at=utc_now(),
        wall_seconds=time.time() - t0,
        certificate={
            "kind": "none",
            "verified": True,
            "note": "Stage-2 schema + hold writeup; certificate.kind none.",
        },
    )
    print("Stage 2 complete", metrics, flush=True)
    return metrics


if __name__ == "__main__":
    import subprocess

    out = subprocess.check_output(
        ["python3", "tools/allocate_id.py", "--next", "run", "--area", "BINSTD"],
        cwd=str(EXP_ROOT.parents[1]),
        text=True,
    )
    # parse RUN-BINSTD-xxxxxx
    import re

    m = re.search(r"RUN-BINSTD-[0-9a-f]{6}", out)
    if not m:
        raise SystemExit(f"allocate_id failed: {out}")
    rid = m.group(0)
    chk = subprocess.check_output(
        ["python3", "tools/allocate_id.py", "--check", rid],
        cwd=str(EXP_ROOT.parents[1]),
        text=True,
    )
    if "OK:" not in chk:
        raise SystemExit(chk)
    stage2(rid)
