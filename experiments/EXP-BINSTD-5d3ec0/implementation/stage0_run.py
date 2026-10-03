"""Stage 0 for EXP-BINSTD-5d3ec0: product-law / |Gamma_13| / n=19 order /
preregistered predictions / methodological note / w=1 baseline.

MUST complete and write artifacts BEFORE any Stage 1 scientific run.
certificate.kind: none
"""
from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from curve import Curve, find_prime_order_generator, is_prime  # noqa: E402
from gamma import (  # noqa: E402
    enum_gamma,
    find_mu,
    gamma_upper_bound,
    log2_exact,
    product_law_table,
)
from gf2n import MOD19, N19, TableField, is_irreducible  # noqa: E402
from runpack import write_run  # noqa: E402

STAGE0 = ROOT / "stage0"
WS = [1, 2, 3, 5, 8, 10, 13, 15]
N131 = 131
PRED_GAMMA13 = 71.0
PRED_ATTEMPTS13 = 60.0
TOL = 0.5


def write_product_law():
    rows = product_law_table(N131, WS)
    g13 = next(r for r in rows if r["w"] == 13)
    payload = {
        "experiment_id": "EXP-BINSTD-5d3ec0",
        "stage": 0,
        "n": N131,
        "role": "structural_certificate_product_law",
        "formula": "|Gamma_w| <= C(n,w)*2^w; attempts_free = 2^n/|Gamma_w|",
        "note": (
            "Exact |Gamma_13| enumeration at n=131 is infeasible (pattern upper "
            "bound ~2^71). Stage-0 re-derivation uses the transparent upper bound "
            "C(131,13)*2^13 as in IDEA-20260926-b48c9d / H-BINSTD-4a07ff claim (B). "
            "Distinct-z collisions only lower |Gamma_w|, raising attempts — bias "
            "favours the object (optimistic assumption disclosed)."
        ),
        "gamma13_rederivation": {
            "C_131_13": g13["C_n_w"],
            "pattern_count_upper": g13["pattern_count_upper"],
            "gamma13_log2_upper": g13["gamma_log2_upper"],
            "predicted_gamma13_log2": PRED_GAMMA13,
            "abs_delta_bits": abs(g13["gamma_log2_upper"] - PRED_GAMMA13),
            "within_tolerance_0_5": abs(g13["gamma_log2_upper"] - PRED_GAMMA13) <= TOL,
            "attempts_w13_log2_upper": g13["attempts_free_log2_upper"],
            "predicted_attempts_w13_log2": PRED_ATTEMPTS13,
            "attempts_abs_delta_bits": abs(g13["attempts_free_log2_upper"] - PRED_ATTEMPTS13),
            "attempts_within_tolerance_0_5": abs(g13["attempts_free_log2_upper"] - PRED_ATTEMPTS13)
            <= TOL,
            "measured_vs_modeled": "modeled_arithmetic",
        },
        "rows": rows,
        "certificate_kind": "none",
        "no_break_claim": True,
    }
    path = STAGE0 / "product-law-n131.yaml"
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    return payload


def write_n19_order_check():
    ok_irr, irr_details = is_irreducible(MOD19)
    F = TableField(N19, MOD19)
    E = Curve(F, 0, 1)
    order = E.count_by_trace()
    expected = 4 * 130873
    ell = 130873
    t2 = (0, F.sqrt(1))
    # Unique 2-torsion among affine points of order dividing 2: (0, sqrt(B))
    # Confirm 2*T2 = O and no other x with 2P=O for P!=O except this.
    other_2tors = []
    for x in range(F.q):
        P = E.lift_x(x)
        if P is None:
            continue
        if E.mul(2, P) is None and P != t2:
            # also check negation is same point for order-2
            if P[0] != 0:
                other_2tors.append(P)
    # For binary curves the unique order-2 point is (0, sqrt(B)).
    unique_2tors = E.mul(2, t2) is None and E.on_curve(t2) and len(other_2tors) == 0
    # Cyclic 2-Sylow (Z/4): exists point of order 4.
    has_order4 = False
    order4_point = None
    for x in range(min(F.q, 5000)):
        P = E.lift_x(x)
        if P is None:
            continue
        if E.mul(4, P) is None and E.mul(2, P) is not None:
            has_order4 = True
            order4_point = P
            break
    G, _ = find_prime_order_generator(E, order, 4, seed=7)
    mu = find_mu(ell, N19)
    gamma1 = enum_gamma(mu, ell, N19, 1)
    payload = {
        "experiment_id": "EXP-BINSTD-5d3ec0",
        "stage": 0,
        "n": N19,
        "irreducible": "t^19 + t^5 + t^2 + t + 1",
        "modulus_int": MOD19,
        "irreducibility_ok": ok_irr,
        "irreducibility_details": irr_details,
        "curve": "y^2 + xy = x^3 + 1",
        "A": 0,
        "B": 1,
        "order_measured": order,
        "order_expected": expected,
        "order_match": order == expected,
        "ell": ell,
        "ell_prime": is_prime(ell),
        "cofactor": 4,
        "unique_2_torsion_point": {"x": t2[0], "y": t2[1]},
        "unique_2_torsion_ok": unique_2tors,
        "other_affine_2_torsion_count": len(other_2tors),
        "two_sylow_cyclic_Z4": has_order4,
        "order4_point_example": None
        if order4_point is None
        else {"x": order4_point[0], "y": order4_point[1]},
        "prime_order_generator_example": {"x": G[0], "y": G[1]},
        "mu_mod_ell": mu,
        "mu_check_mu2_plus_mu_plus_2": (mu * mu + mu + 2) % ell,
        "ord_ell_mu": N19,
        "gamma1_exact_size": len(gamma1),
        "gamma1_upper": gamma_upper_bound(N19, 1),
        "DO4_stop": order != expected,
        "certificate_kind": "none",
        "measured_vs_modeled": "measured",
        "no_break_claim": True,
    }
    path = STAGE0 / "n19-order-check.yaml"
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    return payload


def write_preregistered(pl, n19):
    # Collision-cost bands 2^{n - l'/2} for Stage 1 (MODELED; frozen before Stage 1)
    bands = {}
    for lp in (8, 10, 12):
        pred = 2 ** (N19 - lp / 2)
        bands[lp] = {
            "l_prime": lp,
            "predicted_scalar_mults": pred,
            "predicted_log2": N19 - lp / 2,
            "factor_1_5_low": pred / 1.5,
            "factor_1_5_high": pred * 1.5,
            "measured_vs_modeled": "modeled",
        }
    payload = {
        "experiment_id": "EXP-BINSTD-5d3ec0",
        "written_before_stage1": True,
        "frozen_from": "experiments/EXP-BINSTD-5d3ec0/specification.yaml",
        "heuristic_under_test": ["HEUR-BINSTD-4a07ff-H1", "HEUR-BINSTD-4a07ff-H2"],
        "predictions": {
            "A_stage0_structural": {
                "gamma13_log2_within_0_5_of_71": pl["gamma13_rederivation"][
                    "within_tolerance_0_5"
                ],
                "attempts_w13_log2_within_0_5_of_60": pl["gamma13_rederivation"][
                    "attempts_within_tolerance_0_5"
                ],
                "n19_order_equals_4_130873": n19["order_match"],
                "measured_vs_modeled": "modeled_arithmetic_plus_measured_order",
            },
            "B_stage1_collision": {
                "quantity": "scalar_mults_to_dlp within factor 1.5 of 2^{n-l'/2}",
                "koblitz_vs_control_ratio_band": [0.67, 1.5],
                "cells": bands,
                "measured_vs_modeled": "modeled_band_not_a_post_hoc_fit",
            },
            "C_stage2_H2": {
                "quantity": "coupled_onehot_vs_perpattern_work_ratio",
                "predicted_min_ratio": 1.0,
                "DO2_if_ratio_below_0_5_at_two_cells": True,
                "measured_vs_modeled": "modeled_prediction",
            },
            "D_certificates": {
                "certificate_pass_rate": 1.0,
                "vocabulary": ["discrete_log", "decomposition", "key_recovery", "none"],
            },
        },
        "optimistic_assumptions_restated": [
            "|Gamma_w| upper-bounded by C(n,w)*2^w; collisions lower coverage",
            "Stage-1 1.5x band uses heuristic H1; labeled heuristic",
            "H2 transplants KN-FIND-47da4e independent-summand overhead to coupled shape",
            "Solinas ~2^5.5 recalled; not in measured Stage-1 units",
            "Pure-Python closure D<=4 may under-count vs SAT; optional SAT skipped",
        ],
        "note": (
            "These bands are frozen BEFORE Stage 1+. Retuning after observing "
            "outcomes requires protocol_amendment. No break/rho/exponent claim."
        ),
        "certificate_kind": "none",
    }
    path = STAGE0 / "preregistered-predictions.yaml"
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    return payload


def write_methodological_note(pl, n19):
    text = f"""# Methodological note — EXP-BINSTD-5d3ec0 Stage 0

Experiment: `EXP-BINSTD-5d3ec0` / task `TASK-20261001-eaf0c5` /
hypothesis `H-BINSTD-4a07ff` (source `IDEA-20260926-b48c9d`).

## What Stage 0 freezes

1. **Product-law table at n=131** for w in {{1,2,3,5,8,10,13,15}}:
   `|Gamma_w| <= C(131,w)*2^w`, `attempts_free = 2^131/|Gamma_w|`.
   Re-derived `|Gamma_13|` upper log2 = {pl['gamma13_rederivation']['gamma13_log2_upper']:.4f}
   (prediction 71.0 ± 0.5:
   {pl['gamma13_rederivation']['within_tolerance_0_5']});
   attempts_w13 log2 = {pl['gamma13_rederivation']['attempts_w13_log2_upper']:.4f}
   (prediction 60.0 ± 0.5:
   {pl['gamma13_rederivation']['attempts_within_tolerance_0_5']}).

2. **n=19 order check**: measured order {n19['order_measured']}
   (expected 4*130873={n19['order_expected']}, match={n19['order_match']});
   130873 prime={n19['ell_prime']}; unique 2-torsion (0,1)={n19['unique_2_torsion_ok']};
   2-Sylow cyclic Z/4={n19['two_sylow_cyclic_Z4']}.
   DO-4 stop would fire if order mismatched.

3. **Preregistered Stage-1/2 bands** written in
   `preregistered-predictions.yaml` **before** any Stage-1 run manifest.

4. **w=1 baseline row**: `|Gamma_1|` upper = 262 at n=131 (exact 2n),
   orbit-union gain exactly n on relations (KN-FIND-47da4e /
   frobenius-orbit README) — reproduced as arithmetic identity, not an
   attack measurement.

## Certificate vocabulary

- Stage-0 / metric-only: `certificate.kind: none`
- DLP solutions: `discrete_log` + independent `[x]P=Q` re-check
- Relation hits (P,z): `decomposition` + re-verify `Q=[z]P` with `x(P) in V'`

## Explicit non-claims

- No deployed-curve attack.
- No claim that the mechanism beats matched Pollard rho.
- No exponent improvement from the tau-adic object.
- No extrapolation of Stage-2 ratios to n=131.
- Amazon Bedrock not used. No AUXIN edits.

## Measured vs modeled

Stage-0 `|Gamma_w|` / attempts columns are **MODELED arithmetic** (upper
bounds). n=19 order is **MEASURED**. Stage-1 scalar-multiplication costs and
Stage-2 closure work will be **MEASURED**; comparison bands above are
**MODELED** and frozen here.
"""
    path = STAGE0 / "methodological-note.md"
    path.write_text(text, encoding="utf-8")
    return path


def write_w1_baseline():
    row131 = {
        "n": 131,
        "w": 1,
        "gamma1_upper": gamma_upper_bound(131, 1),
        "gamma1_exact_if_no_collision": 2 * 131,
        "attempts_free_log2": log2_exact((1 << 131) / gamma_upper_bound(131, 1)),
        "orbit_union_relation_gain": 131,
        "note": (
            "w=1 must reproduce orbit-union gain n and no more "
            "(control w1_orbit_union_baseline)."
        ),
    }
    # toy n=19 exact
    F = TableField(N19, MOD19)
    E = Curve(F, 0, 1)
    order = 4 * 130873
    ell = 130873
    mu = find_mu(ell, N19)
    g1 = enum_gamma(mu, ell, N19, 1)
    payload = {
        "experiment_id": "EXP-BINSTD-5d3ec0",
        "stage": 0,
        "control": "w1_orbit_union_baseline",
        "n131": row131,
        "n19": {
            "mu": mu,
            "gamma1_exact": g1,
            "gamma1_exact_size": len(g1),
            "gamma1_upper": gamma_upper_bound(N19, 1),
            "distinct_z_deficit": gamma_upper_bound(N19, 1) - len(g1),
            "orbit_union_relation_gain_expected": N19,
        },
        "certificate_kind": "none",
        "measured_vs_modeled": "modeled_n131_upper__measured_n19_exact_gamma",
        "no_break_claim": True,
    }
    path = STAGE0 / "w1-baseline-row.yaml"
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    return payload


def main(run_id: str = "RUN-BINSTD-6a2c31"):
    STAGE0.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    pl = write_product_law()
    n19 = write_n19_order_check()
    if n19["DO4_stop"]:
        raise SystemExit("DO-4: n=19 order mismatch — refusing Stage 1+")
    pred = write_preregistered(pl, n19)
    write_methodological_note(pl, n19)
    w1 = write_w1_baseline()
    t1 = time.time()
    metrics = {
        "gamma13_log2": pl["gamma13_rederivation"]["gamma13_log2_upper"],
        "attempts_w13_log2": pl["gamma13_rederivation"]["attempts_w13_log2_upper"],
        "gamma13_within_tol": pl["gamma13_rederivation"]["within_tolerance_0_5"],
        "n19_order_match": n19["order_match"],
        "certificate_pass_rate": 1.0,
        "termination_reason": "completed",
    }
    cert = {
        "kind": "none",
        "verified": True,
        "verifier": "structural-arithmetic-no-discrete-log",
        "notes": (
            "Stage-0 product-law / order / predictions; certificate.kind none "
            "per docs/claims-and-verification.md."
        ),
    }
    stdout = json.dumps({"product_law": pl["gamma13_rederivation"], "n19": {
        "order_match": n19["order_match"],
        "ell_prime": n19["ell_prime"],
        "unique_2_torsion_ok": n19["unique_2_torsion_ok"],
    }}, indent=2)
    cmd = (
        f"python3 {Path(__file__).resolve()} --run-id {run_id}"
    )
    write_run(
        run_id,
        stage="0-product-law-order",
        command=cmd,
        parameters={"stage": 0, "n131": 131, "n19": 19},
        metrics=metrics,
        certificate=cert,
        stdout=stdout + "\n",
        raw={
            "gamma13": pl["gamma13_rederivation"],
            "n19_order": {k: n19[k] for k in (
                "order_measured", "order_expected", "order_match", "ell_prime",
                "unique_2_torsion_ok", "two_sylow_cyclic_Z4", "mu_mod_ell",
            )},
            "preregistered_written": True,
            "w1_baseline": {
                "n131_gamma1_upper": w1["n131"]["gamma1_upper"],
                "n19_gamma1_exact_size": w1["n19"]["gamma1_exact_size"],
            },
            "artifacts": [
                "stage0/product-law-n131.yaml",
                "stage0/n19-order-check.yaml",
                "stage0/preregistered-predictions.yaml",
                "stage0/methodological-note.md",
                "stage0/w1-baseline-row.yaml",
            ],
        },
        started=t0,
        finished=t1,
    )
    print(stdout)
    print(f"Stage 0 complete under {run_id}")


if __name__ == "__main__":
    rid = "RUN-BINSTD-6a2c31"
    if "--run-id" in sys.argv:
        rid = sys.argv[sys.argv.index("--run-id") + 1]
    main(rid)
