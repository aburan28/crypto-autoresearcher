#!/usr/bin/env python3
"""Stage 0 for EXP-BINSTD-375338: ord_n(2) census, fixtures, orbit restatement."""
from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from arithmetic import (
    EMPTY_ROWS,
    FROZEN_EXPECTED_ORD,
    LIVE_ROWS,
    N_LIST,
    hexblob_fixture,
    koblitz_ab_fixture,
    ord_n_of_2,
    reachability_verdict,
    stable_dimensions,
    verify_ord_n_2,
)
from runpack import EXP_ROOT, REPO_ROOT, dump_text, dump_yaml, peak_rss_bytes, utc_now, write_run_package

RUN_ID = "RUN-BINSTD-66e032"

ORBIT_RESTATEMENT = """# Orbit-system restatement (Stage 0) — EXP-BINSTD-375338

Task `TASK-20261001-ff051b`. Observations/documentation only. No attack claim.
No per-instance CNF-XOR leaf-count / division-by-mu claim.

## Source reading (a77711 Lemmas A1/A2 at q=2)

IDEA-20260906-a77711 states that absolute Frobenius σ (coordinate-wise
squaring at q=2) is an **equivariance between conjugate targets**, not a
symmetry of a single fixed-target Semaev instance:

- **Lemma A1 (equivariance):** σ maps the solution ideal / decomposition set
  I_R of target R to I_{σR}. Equivalently, if (x₁,…,x_m) decomposes R then
  (x₁²,…,x_m²) decomposes σ(R) = (x_R², y_R²) as points on a Koblitz curve.
- **Lemma A2 (disjointness):** for R ∈ G \\ {O} with σR ≠ ±R,
  V(I_R) ∩ V(I_{σR}) = ∅ — a shifted tuple does **not** solve the same
  instance.

Consequently the correct algebraic object is the **orbit system** bundling
the n conjugate instances {I_R, I_{σR}, …, I_{σ^{n-1}R}} together with the
orbit of the target. A per-instance "shift-canonical" constraint that keeps
only one representative of a Frobenius orbit inside a **single** I_R is
**unsound**: it deletes solutions that belong to conjugate instances.

## HOLD-R absorption (IDEA-20260922-7ab503 review)

analysis/binstd-idea-review-20260926/reviews/IDEA-20260922-7ab503.yaml
(verdict defective / HOLD-R) requires:

1. Primary claim = equivariance (A1/A2), **not** source IDEA claim (A)/(D)
   leaf-ratio ~1/μ on one CNF-XOR instance.
2. K-163 and ECC2K-130 are **STRUCTURALLY EMPTY** for useful mid-dimension
   Frobenius-stable V (ord₁₆₃(2)=162, ord₁₃₁(2)=130); live rows route to FROB.
3. Parser `(0xHEX)` regression is already fixed on the current tree — Stage 0
   records a fixture only.
4. Named toys BIN-TOY-K19 / BIN-TOY-K17-STABLE; RC-1 null; Z/ℓ replica.

## What Stage 1 measures (authorized)

On BIN-TOY-K19 (non-stable poly window, same emptiness pattern as ECC2K-130):

- (a) same_instance_hits — predict 0
- (b) conjugate_instance_hits — predict 1.0 (as points); in-V fraction near 0
- (c) leg-swap control — predict 1.0
- (d) Z/ℓ scalar replica — statistics must match
- (e) solutions_lost under per-instance orbit-canonical constraint — predict >0
  with median fraction near (1 − 1/n)

Stable-V positive control at n=17; NULL-RC1 not-on-curve control.

`orbit_system_restatement_complete: true`
`per_instance_leaf_ratio_authorized: false`
"""


def main() -> None:
    started = utc_now()
    t0 = time.time()
    stage0 = EXP_ROOT / "stage0"
    stage0.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []

    # (i) ord_n(2) census
    census_rows = []
    all_match = True
    for n in N_LIST:
        d = ord_n_of_2(n)
        ok = verify_ord_n_2(n, d)
        expected = FROZEN_EXPECTED_ORD[n]
        match = d == expected
        all_match = all_match and match and ok
        census_rows.append(
            {
                "n": n,
                "ord_n_2_recomputed": d,
                "ord_n_2_expected": expected,
                "ord_verified": ok,
                "match_expected": match,
                "label_recomputed": "RECOMPUTED",
                "label_expected": "EXPECTED",
            }
        )
        lines.append(f"ord_{n}(2) recomputed={d} expected={expected} match={match}")

    dump_yaml(
        stage0 / "ord-n-2-census.yaml",
        {
            "experiment_id": "EXP-BINSTD-375338",
            "task_id": "TASK-20261001-ff051b",
            "stage": 0,
            "method": "least d|(n-1) with 2^d ≡ 1 (mod n); verified by prime factors of d",
            "rows": census_rows,
            "all_match_expected": all_match,
        },
    )

    # (ii) stable-dimension sets
    stab_rows = []
    for n in N_LIST:
        stab = stable_dimensions(n)
        stab_rows.append({"n": n, **stab})
    dump_yaml(
        stage0 / "stable-dimension-sets.yaml",
        {
            "experiment_id": "EXP-BINSTD-375338",
            "task_id": "TASK-20261001-ff051b",
            "stage": 0,
            "method": (
                "T^n-1=(T+1)Phi_n; Phi_n splits into (n-1)/ord_n(2) irreducibles "
                "of degree ord_n(2); stable dims = {b*d, b*d+1 : b=0..(n-1)/d}"
            ),
            "rows": stab_rows,
        },
    )

    # (iii) reachability empty|live
    name_for_n = {
        131: "ECC2K-130",
        163: "K-163",
        233: "K-233",
        239: "sect239k1",
        283: "K-283",
        409: "K-409",
        571: "K-571",
        17: "toy-n17",
        19: "BIN-TOY-K19-pattern",
    }
    cells = []
    for n in N_LIST:
        stab = next(r for r in stab_rows if r["n"] == n)
        cells.append(
            reachability_verdict(n, name_for_n[n], stab["ord_n_2"], stab["mid_lane_empty"])
        )
    empty_ok = all(
        c["verdict"] == "STRUCTURALLY_EMPTY"
        for c in cells
        if c["name"] in EMPTY_ROWS
    )
    live_ok = all(
        c["verdict"] == "LIVE" for c in cells if c["name"] in LIVE_ROWS
    )
    dump_yaml(
        stage0 / "reachability-table-cells.yaml",
        {
            "experiment_id": "EXP-BINSTD-375338",
            "task_id": "TASK-20261001-ff051b",
            "stage": 0,
            "empty_rows_required": EMPTY_ROWS,
            "live_rows_required": LIVE_ROWS,
            "cells": cells,
            "empty_rows_marked_structurally_empty": empty_ok,
            "live_rows_marked_live": live_ok,
            "no_deployed_curve_attack": True,
        },
    )
    lines.append(f"empty_ok={empty_ok} live_ok={live_ok}")

    # (iv) Koblitz A,B fixture
    params = REPO_ROOT / "analysis" / "binstd-curve-audit" / "binary-curve-params.txt"
    ab = koblitz_ab_fixture(params)
    dump_yaml(stage0 / "koblitz-ab-regression-fixture.yaml", ab)
    lines.append(f"koblitz_ab_fixture_match={ab['koblitz_ab_fixture_match']}")

    # (v) hexblob regex fixture
    hx = hexblob_fixture(params.read_text(encoding="utf-8", errors="replace"))
    dump_yaml(stage0 / "hexblob-regex-fixture.yaml", hx)
    lines.append(f"hexblob_accepts_ox={hx['hexblob_regex_accepts_ox_form']}")

    # (vi) orbit-system restatement
    dump_text(stage0 / "orbit-system-restatement.md", ORBIT_RESTATEMENT)
    lines.append("orbit-system-restatement.md written")

    finished = utc_now()
    wall = time.time() - t0
    metrics = {
        "ord_n_2_all_match_expected": all_match,
        "empty_rows_marked_structurally_empty": empty_ok,
        "live_rows_marked_live": live_ok,
        "koblitz_ab_fixture_match": ab["koblitz_ab_fixture_match"],
        "hexblob_regex_accepts_ox_form": hx["hexblob_regex_accepts_ox_form"],
        "peak_rss_bytes": peak_rss_bytes(),
        "wall_s": wall,
        "termination_reason": "completed",
    }
    valid = all(
        [
            all_match,
            empty_ok,
            live_ok,
            ab["koblitz_ab_fixture_match"],
            hx["hexblob_regex_accepts_ox_form"],
        ]
    )
    write_run_package(
        RUN_ID,
        stage=0,
        arm="census_fixtures_restatement",
        seed=None,
        command="python3 experiments/EXP-BINSTD-375338/implementation/stage0_run.py",
        parameters={"n_list": N_LIST, "curve_id": None},
        metrics=metrics,
        valid=valid,
        invalid_reason=None if valid else "Stage 0 fixture/census mismatch",
        termination_reason="completed",
        stdout_text="\n".join(lines) + "\n",
        started_at=started,
        finished_at=finished,
        wall_seconds=wall,
        certificate={
            "kind": "none",
            "verified": False,
            "note": "Stage 0 arithmetic/census measurement only",
        },
    )
    print("\n".join(lines))
    print(f"valid={valid} run={RUN_ID}")


if __name__ == "__main__":
    main()
