#!/usr/bin/env python3
"""Stage 0 for EXP-BINSTD-b7344f: symbolic V(β) + product-law floors (TASK-20261001-8c14b5).

Observations only. No ECDLP attack runs. certificate.kind: none.
"""
from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from runpack import (  # noqa: E402
    EXP_ID,
    TASK_ID,
    EXP_ROOT,
    dump_text,
    dump_yaml,
    utc_now,
    write_run_package,
)

RUN_STAGE0 = "RUN-BINSTD-08f0ab"
RHO_GRID = [1.0, 1.5, 2.0, 10.0, 100.0]
BETA_GRID = [round(0.05 * i, 2) for i in range(1, 20)]  # 0.05..0.95
M_VALUES = [2, 3, 4, 5, 8]
RHO_BASELINE_LOG2 = 60.81
N_BITS = 131


def V_beta(rho: float, beta: float) -> float:
    """Concentrated-IC / exponential-rho portfolio value (HOLD-U closed form).

    V(β) = μ_ρ - (μ_ρ/(1-β)) * (1 - exp(-ρ*(1-β)/β))
    with μ_ρ normalized to 1 so V is a fraction of pure-rho expected cost.
    """
    if beta <= 0.0 or beta >= 1.0:
        raise ValueError("beta must be in (0,1)")
    return 1.0 - (1.0 / (1.0 - beta)) * (1.0 - math.exp(-rho * (1.0 - beta) / beta))


def product_law_floor_log2(m: int) -> float:
    """FREE-oracle product-law floor: m * 2^n field-op lower bound → log2 = n + log2(m)."""
    return N_BITS + math.log2(m)


def stage0() -> dict:
    started = utc_now()
    t0 = time.time()

    table = []
    max_v_per_rho = {}
    all_nonpositive = True
    for rho in RHO_GRID:
        row_max = -float("inf")
        for beta in BETA_GRID:
            v = V_beta(rho, beta)
            table.append({"rho": rho, "beta": beta, "V_beta": v, "modeled": True})
            row_max = max(row_max, v)
            if v > 1e-9:
                all_nonpositive = False
        max_v_per_rho[str(rho)] = row_max

    # Corner check β→0+: V(0)=0 by construction of the formula limit
    # t-1 >= ln t at t=1/β for ρ>=1
    derivation = """# Derivation note — V(β) ≤ 0 for ρ ≥ 1 (HOLD-U)

Experiment: EXP-BINSTD-b7344f / TASK-20261001-8c14b5 / H-BINSTD-32867d.

## Closed form

With IC deterministic at μ_IC = ρ · μ_ρ and rho completion time exponential,
a budget share β to IC gives (μ_ρ normalized to 1):

```
V(β) = 1 - (1/(1-β)) · (1 - exp(-ρ·(1-β)/β))
```

## Non-positivity for ρ ≥ 1

V(β) ≤ 0 for all β ∈ (0,1) whenever ρ ≥ 1 reduces to:

```
(1-β)/β ≥ -ln(β)    i.e.    t - 1 ≥ ln t    at t = 1/β
```

For t > 1, f(t) = t - 1 - ln t has f(1) = 0 and f'(t) = 1 - 1/t ≥ 0, so
f(t) ≥ 0. Equality only at t = 1 (β → 1, degenerate). Thus max_β V(β) ≤ 0
on the Stage-0 grid for every ρ ≥ 1 (numerical check within 1e-9).

## Scope

Modeled / derived only. No ECDLP attack run. No break / exponent / CDCL /
positive-portfolio claim. Stage 1 is a controlled null on the W4 instrument.
"""

    floors = []
    for m in M_VALUES:
        fl = product_law_floor_log2(m)
        ratio = 2 ** (fl - RHO_BASELINE_LOG2)
        floors.append(
            {
                "m": m,
                "n_bits": N_BITS,
                "product_law_floor_log2": fl,
                "rho_baseline_log2": RHO_BASELINE_LOG2,
                "product_law_floor_ratio_vs_rho": ratio,
                "exceeds_rho": ratio > 1.0,
                "oracle_assumption": "FREE (oracle cost = 0); optimistic understates true IC floor",
                "modeled": True,
            }
        )

    dump_yaml(
        EXP_ROOT / "stage0" / "v-beta-table.yaml",
        {
            "experiment_id": EXP_ID,
            "task_id": TASK_ID,
            "stage": 0,
            "formula": "V(beta)=1-(1/(1-beta))*(1-exp(-rho*(1-beta)/beta))",
            "rho_grid": RHO_GRID,
            "beta_grid": BETA_GRID,
            "entries": table,
            "max_V_per_rho": max_v_per_rho,
            "all_nonpositive_within_1e-9": all_nonpositive,
            "modeled": True,
            "no_break_claim": True,
        },
    )
    dump_text(EXP_ROOT / "stage0" / "derivation-note.md", derivation)
    dump_yaml(
        EXP_ROOT / "stage0" / "product-law-floors.yaml",
        {
            "experiment_id": EXP_ID,
            "task_id": TASK_ID,
            "stage": 0,
            "curve_label": "ECC2K-130 arithmetic bound (n=131); no attack run",
            "floors": floors,
            "note": "m<=3 floors exceed rho baseline; portfolio cannot help below a floor.",
            "modeled": True,
            "no_break_claim": True,
        },
    )
    dump_yaml(
        EXP_ROOT / "stage0" / "preregistered-predictions.yaml",
        {
            "experiment_id": EXP_ID,
            "task_id": TASK_ID,
            "written_before_stage1": True,
            "predictions": [
                {
                    "id": "P-H0",
                    "heuristic": "HEUR-BINSTD-32867d-H0",
                    "quantity": "max_beta V(beta) for each rho>=1 on Stage-0 grid",
                    "prediction": "<= 0 within 1e-9",
                    "kind": "modeled",
                },
                {
                    "id": "P-FLOOR",
                    "quantity": "product-law FREE-oracle floor / rho at m in {2,3}",
                    "prediction": "> 1 (HOLD-U ~218 at m=3)",
                    "kind": "modeled",
                },
                {
                    "id": "P-H1",
                    "heuristic": "HEUR-BINSTD-32867d-H1",
                    "quantity": "CV of W4 int32 opcounts on RC-1 sat and unsat",
                    "prediction": "< 0.1 (controlled null; not CDCL evidence)",
                    "kind": "measured_in_stage1",
                    "cv_null_threshold": 0.1,
                    "cv_anomaly_threshold": 1.0,
                },
            ],
            "no_break_claim": True,
            "no_cdcl_claim": True,
        },
    )
    dump_text(
        EXP_ROOT / "stage0" / "methodological-note.md",
        """# Methodological note — EXP-BINSTD-b7344f Stage 0/1 framing

- Stage 0 is **symbolic / modeled**: V(β) table and product-law floors.
  No ECDLP attack, no CDCL engine, no break claim.
- Stage 1 wraps EXP-CERTBIN-e94b27 W4 closure as a **controlled null** for
  HEUR-H1 (CV near zero). Absence of WDSat/CryptoMiniSat/CaDiCaL/Macaulay2
  is disclosed as IMP-no-cdcl — not thin-tail evidence about CDCL.
- Measured vs modeled columns stay separate.
- certificate.kind vocabulary: discrete_log | decomposition | key_recovery | none.
  Stage-0 / cost-shape / Stage-2 manifests use **none**.
- Positive DO-1 does **not** authorize a CDCL portfolio experiment or
  deployed claim. Amazon Bedrock unused.
""",
    )

    finished = utc_now()
    wall = time.time() - t0
    metrics = {
        "n_table_entries": len(table),
        "all_nonpositive_within_1e-9": all_nonpositive,
        "max_V_across_grid": max(max_v_per_rho.values()),
        "m3_floor_ratio_vs_rho": next(f["product_law_floor_ratio_vs_rho"] for f in floors if f["m"] == 3),
    }
    write_run_package(
        RUN_STAGE0,
        stage=0,
        arm="symbolic_V_beta_and_floors",
        seed=None,
        command="python3 experiments/EXP-BINSTD-b7344f/implementation/stage0_run.py",
        parameters={
            "curve_id": "ECC2K-130-arithmetic-bound-only",
            "rho_grid": RHO_GRID,
            "beta_grid": BETA_GRID,
            "m_values": M_VALUES,
            "rho_baseline_log2": RHO_BASELINE_LOG2,
        },
        metrics=metrics,
        valid=all_nonpositive and metrics["m3_floor_ratio_vs_rho"] > 1.0,
        invalid_reason=None,
        termination_reason="completed",
        stdout_text=json.dumps(metrics, indent=2),
        started_at=started,
        finished_at=finished,
        wall_seconds=wall,
        certificate={
            "kind": "none",
            "verified": True,
            "note": "Stage-0 symbolic/modeled artifacts; certificate.kind none.",
        },
    )
    print("Stage 0 complete", metrics, flush=True)
    return metrics


if __name__ == "__main__":
    stage0()
