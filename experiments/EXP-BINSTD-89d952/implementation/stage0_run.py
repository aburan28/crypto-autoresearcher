#!/usr/bin/env python3
"""Stage 0 for EXP-BINSTD-89d952: HOLD-T corrected affordability table (no /mu),
cancelation certificate, stable-V census, methodological note.

Arithmetic / census only. Zero scientific group walks on deployed curves.
certificate.kind: none.
"""
from __future__ import annotations

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
    peak_rss_bytes,
    utc_now,
    write_run_package,
)

RUN_ID = "RUN-BINSTD-260c42"

# Frozen cells from specification.yaml Stage0-corrected-table
FROZEN_CELLS = [
    {"m": 3, "l": 8, "value": 2796202},
    {"m": 4, "l": 8, "value": 178956970},
    {"m": 5, "l": 6, "value": 8947848},
    {"m": 4, "l": 5, "value": 43690},
]

# Inherited REJECTED /mu comparator column from IDEA-20260922-493606 (source).
# These are NOT recomputed predictions; labeled inherited_rejected.
SOURCE_MU_REJECTED = {
    (3, 8): {
        "mu1_pseudorandom": 2796203,  # 2^24/6 rounded in source prose
        "note": "source m=3,l=8 anchor; corrected integer floor is 2796202",
    },
    (4, 8): {
        "mu1_pseudorandom": 178956971,  # 2^32/24
        "mu_n37_koblitz": 4836675,  # 178956971/37 — REJECTED divisor
        "n_used_unsound": 37,
    },
    (5, 6): {
        "mu1_pseudorandom": 8947849,  # 2^30/120
        "mu_n29_koblitz": 308547,  # 8947849/29 — REJECTED divisor
        "n_used_unsound": 29,
    },
    (4, 5): {
        "mu1_pseudorandom": 43691,  # 2^20/24
        "note": "HOLD-T successor cell at n=31,l=5; no /mu applied in corrected table",
    },
}

N_LIST = [17, 19, 23, 29, 31, 37, 41]
EXPECTED_EMPTY_MID = [29, 37]

METHOD_NOTE = """# Methodological note — EXP-BINSTD-89d952 Stage 0

Task `TASK-20261001-e15653`. Observations only. No attack claim.
No rho-competitiveness claim. Amazon Bedrock unused.

## HOLD-T corrections absorbed

From `analysis/binstd-idea-review-20260926/reviews/IDEA-20260922-493606.yaml`
(verdict defective / HOLD-T):

1. **Remove /mu.** Per-instance divisor μ=n does not exist (a77711 Lemmas A1/A2;
   KN-FIND-47da4e). Corrected leaf count is `N = 2^{ml}/m!` identical for
   Koblitz-shaped and pseudorandom-shaped arms. Cancelation on the n-target
   orbit system: `n · 2^{ml}/(m! · n) = 2^{ml}/m!`.
2. **Forbid n∈{29,37} as Frobenius-stable measurement cells.** `ord_29(2)=28`,
   `ord_37(2)=36` ⇒ mid-dimension τ-stable V empty.
3. **Instrument replan.** WDSat/CaDiCaL absent; Stage 1 uses pure-Python
   S₄/W₄ from EXP-CERTBIN-e94b27 patterns. CNF-XOR leaf counts are NOT a
   success criterion. Feasibility of S₄ Macaulay at 15 variables is the first
   Stage-1 metric.
4. **Anchor honesty.** IDEA-20260904-b40e6d ~2.8e6 is a **design estimate**,
   labeled unmeasured — not a completed-run anchor.
5. **Primary prediction.** arm_ratio ≈ 1 (shape-blind equality), not the
   source /μ differential. Source /μ is the named falsifiable alternative.
6. **Successor seam.** True m≥4 measurement without symmetry claim routes to
   CERTBIN S₅ extension; this packet does not close that gap.

## certificate.kind vocabulary

Closed set only: `discrete_log | decomposition | key_recovery | none`.
Stage 0 uses `none`. Verified planted finds in Stage 1 may use
`decomposition`. Pure cost/refutation observations use `none`.

## What is NOT claimed

- No break of any curve.
- No competitiveness with Pollard rho.
- No per-instance μ-orbit / canonical-representative constraint (unsound).
- No transfer of toy n=19 costs to deployed n≥131.
"""


def ord_n_of_2(n: int) -> int:
    if n <= 2 or n % 2 == 0:
        raise ValueError("n must be odd > 2")
    nm1 = n - 1
    divisors = []
    for i in range(1, int(nm1**0.5) + 1):
        if nm1 % i == 0:
            divisors.append(i)
            if i != nm1 // i:
                divisors.append(nm1 // i)
    for d in sorted(divisors):
        if pow(2, d, n) == 1:
            return d
    raise ValueError(f"ord_{n}(2) not found")


def verify_ord_n_2(n: int, d: int) -> bool:
    if d <= 0 or pow(2, d, n) != 1:
        return False
    x = d
    primes = []
    p = 2
    while p * p <= x:
        if x % p == 0:
            primes.append(p)
            while x % p == 0:
                x //= p
        p = 3 if p == 2 else p + 2
    if x > 1:
        primes.append(x)
    for p in primes:
        if pow(2, d // p, n) == 1:
            return False
    return True


def stable_dimensions(n: int, d: int | None = None) -> dict:
    if d is None:
        d = ord_n_of_2(n)
    f = (n - 1) // d
    dims = []
    for b in range(f + 1):
        dims.append(b * d)
        dims.append(b * d + 1)
    dims = sorted(set(dims))
    mid = [x for x in dims if x not in (0, 1, n - 1, n)]
    return {
        "ord_n_2": d,
        "phi_factor_count": f,
        "phi_factor_degree": d,
        "stable_dimensions": dims,
        "mid_dimensions": mid,
        "mid_lane_empty": len(mid) == 0,
        "label": "RECOMPUTED",
    }


def corrected_leaf(m: int, l: int) -> int:
    return (1 << (m * l)) // math.factorial(m)


def main() -> None:
    started = utc_now()
    t0 = time.time()
    stage0 = EXP_ROOT / "stage0"
    stage0.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []

    # --- corrected table ---
    rows = []
    table_match = True
    for cell in FROZEN_CELLS:
        m, l, expected = cell["m"], cell["l"], cell["value"]
        got = corrected_leaf(m, l)
        match = got == expected
        table_match = table_match and match
        inherited = SOURCE_MU_REJECTED.get((m, l), {})
        rows.append(
            {
                "m": m,
                "l": l,
                "formula": "2**(m*l)//math.factorial(m)",
                "value_recomputed": got,
                "value_frozen_expected": expected,
                "match_frozen": match,
                "label_recomputed": "RECOMPUTED",
                "inherited_rejected_mu_column": {
                    "label": "INHERITED_REJECTED",
                    "source": "IDEA-20260922-493606",
                    **inherited,
                },
            }
        )
        lines.append(f"table m={m} l={l} recomputed={got} expected={expected} match={match}")

    dump_yaml(
        stage0 / "corrected-table.yaml",
        {
            "experiment_id": EXP_ID,
            "task_id": TASK_ID,
            "stage": 0,
            "formula": "N_leaf_corrected(m,l) = 2**(m*l) // factorial(m)",
            "mu_column": "ABSENT (HOLD-T); inherited rejected comparator only",
            "b40e6d_anchor": {
                "value": 2.8e6,
                "label": "UNMEASURED_DESIGN_ESTIMATE",
                "source": "IDEA-20260904-b40e6d",
            },
            "rows": rows,
            "stage0_table_match": table_match,
        },
    )

    # --- cancelation certificate ---
    cancel_ok = True
    cancel_rows = []
    for cell in FROZEN_CELLS:
        m, l = cell["m"], cell["l"]
        n_demo = 19  # any n≠0; identity is algebraic
        N = corrected_leaf(m, l)
        # exact rational identity using integers: n * 2^{ml} / (m! * n) == 2^{ml}/m!
        left_num = n_demo * (1 << (m * l))
        left_den = math.factorial(m) * n_demo
        right_num = 1 << (m * l)
        right_den = math.factorial(m)
        # compare as reduced integers via cross-multiply
        identity = left_num * right_den == right_num * left_den
        floor_equal = (left_num // left_den) == (right_num // right_den) == N
        cancel_ok = cancel_ok and identity and floor_equal
        cancel_rows.append(
            {
                "m": m,
                "l": l,
                "n_demo": n_demo,
                "N_corrected": N,
                "identity_exact": identity,
                "floor_equal": floor_equal,
                "algebra": "n * 2**(m*l) / (factorial(m) * n) == 2**(m*l) / factorial(m)",
            }
        )
        lines.append(f"cancelation m={m} l={l} identity={identity} floor_equal={floor_equal}")

    dump_yaml(
        stage0 / "cancelation-certificate.yaml",
        {
            "experiment_id": EXP_ID,
            "task_id": TASK_ID,
            "stage": 0,
            "statement": (
                "On the n-target Frobenius orbit system the putative per-instance "
                "divisor n cancels: n*2^{ml}/(m!*n)=2^{ml}/m!. Citations: "
                "IDEA-20260906-a77711 Lemmas A1/A2; KN-FIND-47da4e."
            ),
            "rows": cancel_rows,
            "stage0_cancelation_pass": cancel_ok,
            "label": "RECOMPUTED",
        },
    )

    # --- stable-V census ---
    census_rows = []
    empty_29_37 = True
    for n in N_LIST:
        d = ord_n_of_2(n)
        ok = verify_ord_n_2(n, d)
        stab = stable_dimensions(n, d)
        if n in EXPECTED_EMPTY_MID:
            empty_29_37 = empty_29_37 and stab["mid_lane_empty"]
        census_rows.append(
            {
                "n": n,
                "ord_n_2_recomputed": d,
                "ord_verified": ok,
                **{k: stab[k] for k in (
                    "phi_factor_count",
                    "phi_factor_degree",
                    "stable_dimensions",
                    "mid_dimensions",
                    "mid_lane_empty",
                    "label",
                )},
                "forbidden_as_frobenius_stable_measurement_cell": n in (29, 37),
                "stage1_note": (
                    "ord_19(2)=18; no mid-dim stable V; Stage 1 uses random "
                    "polynomial-basis V of dim 5, not tau-stable"
                    if n == 19
                    else None
                ),
            }
        )
        lines.append(
            f"census n={n} ord={d} mid={stab['mid_dimensions']} empty={stab['mid_lane_empty']}"
        )

    dump_yaml(
        stage0 / "stable-v-census.yaml",
        {
            "experiment_id": EXP_ID,
            "task_id": TASK_ID,
            "stage": 0,
            "n_list": N_LIST,
            "expected_empty_mid_dim": EXPECTED_EMPTY_MID,
            "method": (
                "T^n-1=(T+1)Phi_n; Phi_n splits into (n-1)/ord_n(2) irreducibles "
                "of degree ord_n(2); stable dims = {b*d, b*d+1 : b=0..(n-1)/d}"
            ),
            "rows": census_rows,
            "stage0_census_empty_29_37": empty_29_37,
            "forbidden_measurement_cells": [29, 37],
        },
    )

    dump_text(stage0 / "methodological-note.md", METHOD_NOTE)
    lines.append("methodological-note.md written")

    finished = utc_now()
    wall = time.time() - t0
    hard_fail = not (table_match and cancel_ok and empty_29_37)
    metrics = {
        "stage0_table_match": table_match,
        "stage0_cancelation_pass": cancel_ok,
        "stage0_census_empty_29_37": empty_29_37,
        "peak_rss_bytes": peak_rss_bytes(),
        "wall_s": wall,
        "termination_reason": "completed",
        "hard_fail": hard_fail,
    }
    write_run_package(
        RUN_ID,
        stage=0,
        arm="stage0-arithmetic",
        seed=None,
        command="python3 experiments/EXP-BINSTD-89d952/implementation/stage0_run.py",
        parameters={"n_list": N_LIST, "frozen_cells": FROZEN_CELLS},
        metrics=metrics,
        valid=not hard_fail,
        invalid_reason=(
            "Stage 0 table/cancelation/census gate failed" if hard_fail else None
        ),
        termination_reason="completed",
        stdout_text="\n".join(lines) + "\n",
        started_at=started,
        finished_at=finished,
        wall_seconds=wall,
        certificate={
            "kind": "none",
            "verified": True,
            "note": "Stage 0 arithmetic/census; no discrete-log or decomposition claim",
        },
    )
    print("\n".join(lines))
    print(f"Stage 0 done hard_fail={hard_fail} run={RUN_ID}")
    if hard_fail:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
