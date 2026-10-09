#!/usr/bin/env python3
"""EXP-FROB-8451c7 Stages 0-1 launcher (frozen contract v1).

Stage 0: Arm A integer successive-multiplication ledger + Phi_8(2)=17.
Stage 1: Arm B n=17 torus fibre Boolean-count panel vs subspace / Z/17Z /
         orbit-union / identity / null-curve controls.

Observations only. No Magma/Sage/AUXIN/Bedrock. No ECDLP solve. No n>=131
attack. Amazon Bedrock is not selected.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

_IMPL = Path(__file__).resolve().parent
if str(_IMPL) not in sys.path:
    sys.path.insert(0, str(_IMPL))

from gf2 import MOD_F2_8, MOD_F2_17, Field, clmul, pmod  # noqa: E402

EXPERIMENT_ID = "EXP-FROB-8451c7"
HYPOTHESIS_ID = "H-FROB-66d9ae"
APPROVED_BY = "DEC-20261002-93fc80"
G5, G6 = 6725, 39201
N_LEDGER = 131
N_TOY = 17
G_TORUS = 4
SEED_CURVE = 2026100217
SEED_FIBRE = 2026100218
SEED_NULL = 2026100219
PREREG = {
    "least_m_g5": 11,
    "least_m_g6": 9,
    "semaev_degree_g5": 512,
    "semaev_degree_g6": 128,
    "image_bound_check": "8 * 39201**3 < 2**51",
    "phi8": 17,
}
EXP_ROOT = Path(__file__).resolve().parents[1]


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"refusing overwrite: {path}")
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"refusing overwrite: {path}")
    path.write_text(text, encoding="utf-8")


def least_m(ceiling: int, target_bits: int) -> dict[str, Any]:
    target = 1 << target_bits
    product = 1
    m = 0
    while product < target:
        product *= ceiling
        m += 1
    return {
        "ceiling": ceiling,
        "least_m": m,
        "product": product,
        "target": target,
        "semaev_degree": 1 << (m - 2) if m >= 2 else None,
        "meets_target": product >= target,
    }


def phi8_of_two() -> int:
    return (1 << 4) + 1


def f28_mul_selftest(f8: Field) -> dict[str, Any]:
    """Fixed multiplication check in F_{2^8}: (t+1)*(t^2+1) vs schoolbook."""
    a, b = 0b11, 0b101  # t+1, t^2+1
    got = f8.mul(a, b)
    raw = pmod(clmul(a, b), f8.mod)
    return {
        "a": a,
        "b": b,
        "product": got,
        "schoolbook": raw,
        "ok": got == raw == pmod(clmul(a, b), MOD_F2_8),
        "modulus": f8.mod,
    }


def stage0(run_dir: Path) -> dict[str, Any]:
    t0 = time.time()
    g5 = least_m(G5, N_LEDGER)
    g6 = least_m(G6, N_LEDGER)
    phi8 = phi8_of_two()
    image_num = 8 * (G6 ** 3)
    image_ok = image_num < (1 << 51)
    f8 = Field(MOD_F2_8)
    mul = f28_mul_selftest(f8)

    prereg = {
        "experiment_id": EXPERIMENT_ID,
        "frozen_at_stage": 0,
        "predictions": {
            "least_m_g5": g5["least_m"],
            "least_m_g6": g6["least_m"],
            "semaev_degree_g5": g5["semaev_degree"],
            "semaev_degree_g6": g6["semaev_degree"],
            "phi8": phi8,
            "image_bound_m3_num": image_num,
            "image_bound_m3_ok": image_ok,
        },
        "preregistered_targets": PREREG,
        "match_preregistered": (
            g5["least_m"] == PREREG["least_m_g5"]
            and g6["least_m"] == PREREG["least_m_g6"]
            and g5["semaev_degree"] == PREREG["semaev_degree_g5"]
            and g6["semaev_degree"] == PREREG["semaev_degree_g6"]
            and phi8 == PREREG["phi8"]
            and image_ok
            and mul["ok"]
        ),
    }
    ledger = {
        "experiment_id": EXPERIMENT_ID,
        "arm": "A_integer_ledger",
        "n_ledger": N_LEDGER,
        "g5": g5,
        "g6": g6,
        "phi8": phi8,
        "image_bound": {"numerator": image_num, "lt_2_51": image_ok},
        "f28_mul_selftest": mul,
        "field_poly_f2_8": MOD_F2_8,
    }

    stage0_dir = EXP_ROOT / "stage0"
    write_json(stage0_dir / "preregistered-predictions.json", prereg)
    write_json(stage0_dir / "arm-a-ledger.json", ledger)

    raw = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "stage": 0,
        "status": "completed",
        "preregistered_match": prereg["match_preregistered"],
        "ledger": ledger,
        "preregistered": prereg,
        "wall_clock_seconds": time.time() - t0,
        "amazon_bedrock": "NOT_USED",
    }
    write_json(run_dir / "raw-result.json", raw)
    write_text(
        run_dir / "manifest.yaml",
        "\n".join(
            [
                f"experiment_id: {EXPERIMENT_ID}",
                "stage: 0",
                "arm: A_integer_ledger",
                f"approved_by: {APPROVED_BY}",
                f"preregistered_match: {str(prereg['match_preregistered']).lower()}",
                "artifacts:",
                "  - raw-result.json",
                "  - manifest.yaml",
                "stage0_paths:",
                "  - experiments/EXP-FROB-8451c7/stage0/preregistered-predictions.json",
                "  - experiments/EXP-FROB-8451c7/stage0/arm-a-ledger.json",
                "scientific_conclusion: null",
                "",
            ]
        ),
    )
    return raw


def factor_small(n: int) -> list[int]:
    factors: list[int] = []
    x = n
    d = 2
    while d * d <= x:
        while x % d == 0:
            factors.append(d)
            x //= d
        d += 1 if d == 2 else 2
    if x > 1:
        factors.append(x)
    return factors


def curve_order(f: Field, a: int, b: int) -> dict[str, Any]:
    """Count #E(F_{2^n}) for y^2 + x y = x^3 + a x^2 + b by enumeration."""
    n = f.n
    count = 1  # point at infinity
    for x in range(1 << n):
        if x == 0:
            # y^2 = b; squaring is bijective on F_{2^n} => exactly one y
            count += 1
            continue
        # z = y/x; z^2 + z = x + a + b * x^{-2}
        x2 = f.mul(x, x)
        rhs = x ^ a ^ f.mul(b, f.inv(x2))
        if f.trace(rhs) == 0:
            count += 2
    return {"a": a, "b": b, "order": count, "n": n}


def find_koblitz_curve(f17: Field) -> dict[str, Any]:
    """Deterministic search: first (a,b) in F_2 with a prime factor bitlen >= 15."""
    candidates = [(0, 1), (1, 1)]
    trials = []
    for a, b in candidates:
        rec = curve_order(f17, a, b)
        factors = factor_small(rec["order"])
        rec["factors"] = factors
        rec["max_prime_bitlen"] = max((p.bit_length() for p in factors), default=0)
        trials.append(rec)
        if rec["max_prime_bitlen"] >= 15:
            rec["selected"] = True
            return {"selected": rec, "trials": trials, "seed_curve": SEED_CURVE}
    return {
        "selected": None,
        "trials": trials,
        "seed_curve": SEED_CURVE,
        "impediment": "no_koblitz_candidate_with_prime_factor_bitlen_ge_15",
    }


def order_17_element(f8: Field) -> dict[str, Any]:
    """Find t in F_{2^8}^* of order 17 (divides 255 = 3*5*17)."""
    for cand in range(2, 1 << f8.n):
        if f8.pow(cand, 17) == 1:
            # 17 is prime => order is 1 or 17; cand!=1 already.
            return {"t": cand, "order": 17, "ok": True}
    return {"t": None, "order": None, "ok": False}


def gf2_rank(rows: list[list[int]]) -> int:
    """Row-reduce bit-matrix over F_2; return rank."""
    if not rows:
        return 0
    A = [row[:] for row in rows]
    n_cols = len(A[0])
    rank = 0
    row = 0
    for col in range(n_cols):
        pivot = None
        for r in range(row, len(A)):
            if A[r][col]:
                pivot = r
                break
        if pivot is None:
            continue
        A[row], A[pivot] = A[pivot], A[row]
        for r in range(len(A)):
            if r != row and A[r][col]:
                A[r] = [a ^ b for a, b in zip(A[r], A[row])]
        rank += 1
        row += 1
        if row >= len(A):
            break
    return rank


def boolean_panel_torus(f17: Field, t: int, f8: Field) -> dict[str, Any]:
    """H2 panel: g*n free descended coords; linear forms from fibre b^2=b*t.

    Fibre equation in F_{2^8}: b^2 + b*t = 0 => b(b+t)=0. Lifted as linear
    constraint templates on the g=4 coordinate blocks in F_{2^{17}} after
    identifying the order-17 label with the toy cell (Phi_8(2)=17). Rank after
    quotient is the F_2-rank of those templates; deficiency listed explicitly.
    """
    g, n = G_TORUS, N_TOY
    before = g * n
    # Identity block (free coords) contributes no linear cut; fibre imposes
    # that each coordinate block is constant on the t-coset label.
    # Build g linear forms: for block i, sum of bits equals bit_i(t) pattern
    # embedded into F_{2^{17}} via the low 8 bits (torus ambient).
    rows: list[list[int]] = []
    deficiency: list[str] = []
    t_bits = [(t >> j) & 1 for j in range(8)]
    for i in range(g):
        row = [0] * before
        # One parity constraint per torus coordinate block (linear part).
        base = i * n
        for j in range(min(8, n)):
            row[base + j] = 1
        rows.append(row)
        # Record the constant term target from t (not part of the rank matrix).
        deficiency.append(f"block_{i}_parity_targets_t_bit_{i % 8}={t_bits[i % 8]}")
    after = gf2_rank(rows)
    # |F|: size of the order-17 cyclic subgroup (torus F_2-points).
    subgroup = []
    x = 1
    for _ in range(17):
        subgroup.append(x)
        x = f8.mul(x, t)
    # Fibre of t under b |-> b^2 / b = b (for b!=0) equals {t}; with b=0, |fibre|=2.
    fibre = [0, t]
    return {
        "family": "torus",
        "boolean_count_before_quotient": before,
        "boolean_count_after_quotient": after,
        "first_fall_degree": "UNDETERMINED",
        "first_fall_degree_note": "No Groebner/Semaev elimination under this card; cap leaves UNDETERMINED.",
        "factor_base_size_F": len(set(subgroup)),
        "fibre_size": len(fibre),
        "linear_deficiency_forms": deficiency,
        "rank_rows": len(rows),
        "seed_fibre": SEED_FIBRE,
    }


def boolean_panel_subspace() -> dict[str, Any]:
    """Dim-8 F_2-subspace of F_{2^{17}}: 8 free bits; same rank pipeline."""
    dim, n = 8, N_TOY
    before = dim  # parametrization by dim free F_2 coeffs (not g*n)
    # No further linear cut on free params => after = before
    after = dim
    return {
        "family": "subspace_dim8",
        "boolean_count_before_quotient": before,
        "boolean_count_after_quotient": after,
        "first_fall_degree": "UNDETERMINED",
        "factor_base_size_F": 1 << dim,
        "linear_deficiency_forms": [],
        "note": "Equal-cardinality comparator is size 2^8; not a rational-point torus.",
    }


def boolean_panel_orbit_union() -> dict[str, Any]:
    """KN-FIND-47da4e (representative, shift) encoding of the dim-8 subspace."""
    # rep: 8 bits; shift index: ceil(log2(n)) bits for n=17 -> 5 bits
    before = 8 + 5
    after = before  # encoding-only; no extra linear quotient
    return {
        "family": "orbit_union_shift",
        "boolean_count_before_quotient": before,
        "boolean_count_after_quotient": after,
        "first_fall_degree": "UNDETERMINED",
        "factor_base_size_F": 1 << 8,
        "encoding": {"representative_bits": 8, "shift_bits": 5, "n": N_TOY},
    }


def boolean_panel_identity() -> dict[str, Any]:
    """Identity projection: predicted Boolean count = ambient dimension (b=1)."""
    return {
        "family": "identity_projection",
        "boolean_count_before_quotient": N_TOY,
        "boolean_count_after_quotient": N_TOY,
        "first_fall_degree": "UNDETERMINED",
        "factor_base_size_F": 1 << N_TOY,
        "prediction": "ambient_dimension_with_b_1",
    }


def boolean_panel_z17() -> dict[str, Any]:
    """Relabelled Z/17Z: fibre equation replaced by +1 in Z/17Z."""
    # Elements of Z/17Z need ceil(log2(17))=5 bits; +1 is a permutation (no cut).
    before = 5
    after = 5
    return {
        "family": "relabelled_Z17",
        "boolean_count_before_quotient": before,
        "boolean_count_after_quotient": after,
        "first_fall_degree": "UNDETERMINED",
        "factor_base_size_F": 17,
        "fibre_equation": "x |-> x+1 in Z/17Z",
    }


def find_null_curve(f17: Field, target_order: int) -> dict[str, Any]:
    """Curve over F_{2^{17}} not defined over F_2, same cardinality.

    Cap is small (4 full enumerations): missing match is recorded on the
    null-curve control only and is not negative evidence against (A)-(C).
    """
    rng = SEED_NULL
    attempts = []
    for _ in range(4):
        rng = (1103515245 * rng + 12345) & 0x7FFFFFFF
        a = (rng % ((1 << f17.n) - 2)) + 2  # avoid 0,1
        rng = (1103515245 * rng + 12345) & 0x7FFFFFFF
        b = (rng % ((1 << f17.n) - 2)) + 2
        if a in (0, 1) and b in (0, 1):
            continue
        rec = curve_order(f17, a, b)
        attempts.append({"a": a, "b": b, "order": rec["order"]})
        if rec["order"] == target_order:
            rec["defined_over_f2"] = False
            rec["selected"] = True
            return {"selected": rec, "attempts": len(attempts), "seed_null": SEED_NULL}
    return {
        "selected": None,
        "attempts": len(attempts),
        "seed_null": SEED_NULL,
        "impediment": "null_curve_same_cardinality_not_found_in_cap",
        "attempt_orders": [x["order"] for x in attempts],
        "asserts_nothing_about": "H-FROB-66d9ae scientific content",
    }


def classify_outcome(stage0_ok: bool, panels: dict[str, Any]) -> str:
    if not stage0_ok:
        return "O-ARTIFACT"
    torus = panels["torus"]
    subspace = panels["subspace_dim8"]
    z17 = panels["relabelled_Z17"]
    t_after = torus["boolean_count_after_quotient"]
    s_after = subspace["boolean_count_after_quotient"]
    # Positive toy: torus after-quotient strictly below 68 and below subspace,
    # and Z/17Z does not reproduce the drop.
    if t_after < 68 and t_after < s_after and z17["boolean_count_after_quotient"] != t_after:
        return "O-POSITIVE-TOY"
    return "O-LEDGER"


def stage1(run_dir: Path) -> dict[str, Any]:
    t0 = time.time()
    stage0_prereg = EXP_ROOT / "stage0" / "preregistered-predictions.json"
    stage0_ledger = EXP_ROOT / "stage0" / "arm-a-ledger.json"
    if not stage0_prereg.is_file() or not stage0_ledger.is_file():
        raw = {
            "experiment_id": EXPERIMENT_ID,
            "stage": 1,
            "status": "failed_infrastructure",
            "outcome": "O-IMPEDIMENT",
            "reason": "stage0 freeze missing; Stage 0 must complete first",
            "wall_clock_seconds": time.time() - t0,
            "amazon_bedrock": "NOT_USED",
        }
        write_json(run_dir / "raw-result.json", raw)
        write_text(
            run_dir / "manifest.yaml",
            f"experiment_id: {EXPERIMENT_ID}\nstage: 1\noutcome: O-IMPEDIMENT\n",
        )
        return raw

    prereg = json.loads(stage0_prereg.read_text(encoding="utf-8"))
    stage0_ok = bool(prereg.get("match_preregistered"))

    phi8 = phi8_of_two()
    if phi8 != 17:
        stage0_ok = False

    f8 = Field(MOD_F2_8)
    f17 = Field(MOD_F2_17)
    mul = f28_mul_selftest(f8)
    if not mul["ok"]:
        stage0_ok = False

    t_rec = order_17_element(f8)
    curve = find_koblitz_curve(f17)

    if not t_rec["ok"] or curve.get("selected") is None:
        outcome = "O-IMPEDIMENT" if stage0_ok else "O-ARTIFACT"
        raw = {
            "experiment_id": EXPERIMENT_ID,
            "stage": 1,
            "status": "completed" if outcome != "O-IMPEDIMENT" else "failed_infrastructure",
            "outcome": outcome,
            "phi8": phi8,
            "f28_mul_selftest": mul,
            "order_17": t_rec,
            "curve_search": curve,
            "wall_clock_seconds": time.time() - t0,
            "amazon_bedrock": "NOT_USED",
        }
        write_json(run_dir / "raw-result.json", raw)
        write_text(
            run_dir / "manifest.yaml",
            f"experiment_id: {EXPERIMENT_ID}\nstage: 1\noutcome: {outcome}\n",
        )
        write_json(EXP_ROOT / "stage1" / "control-table.json", {"outcome": outcome, "curve": curve})
        return raw

    t = t_rec["t"]
    panels = {
        "torus": boolean_panel_torus(f17, t, f8),
        "subspace_dim8": boolean_panel_subspace(),
        "orbit_union_shift": boolean_panel_orbit_union(),
        "identity_projection": boolean_panel_identity(),
        "relabelled_Z17": boolean_panel_z17(),
    }
    null = find_null_curve(f17, curve["selected"]["order"])
    panels["null_curve"] = {
        "family": "null_curve",
        "curve": null,
        "boolean_count_before_quotient": None,
        "boolean_count_after_quotient": None,
        "first_fall_degree": "UNDETERMINED",
        "factor_base_size_F": None,
        "note": "Cardinality-matched control curve; Boolean panel not claimed as support.",
    }

    outcome = classify_outcome(stage0_ok, panels)
    control_table = {
        "experiment_id": EXPERIMENT_ID,
        "n": N_TOY,
        "phi8": phi8,
        "curve": curve["selected"],
        "order_17_element": t_rec,
        "panels": panels,
        "outcome": outcome,
        "field_poly_f2_8": MOD_F2_8,
        "field_poly_f2_17": MOD_F2_17,
    }
    stage1_dir = EXP_ROOT / "stage1"
    write_json(stage1_dir / "control-table.json", control_table)
    write_json(stage1_dir / "panels.json", panels)

    results = "\n".join(
        [
            f"# RESULTS — {EXPERIMENT_ID}",
            "",
            f"Hypothesis: {HYPOTHESIS_ID}",
            f"Approved by: {APPROVED_BY}",
            "",
            f"## Outcome",
            "",
            f"**{outcome}**",
            "",
            "Exactly one O-* label from H-FROB-66d9ae.",
            "",
            "## Arm A (Stage 0)",
            "",
            f"- preregistered_match: {stage0_ok}",
            f"- Phi_8(2): {phi8}",
            f"- F_2^8 mul selftest: {mul['ok']}",
            "",
            "## Arm B (Stage 1) Boolean counts after quotient",
            "",
            f"- torus: {panels['torus']['boolean_count_after_quotient']} (before {panels['torus']['boolean_count_before_quotient']})",
            f"- subspace_dim8: {panels['subspace_dim8']['boolean_count_after_quotient']}",
            f"- orbit_union_shift: {panels['orbit_union_shift']['boolean_count_after_quotient']}",
            f"- identity_projection: {panels['identity_projection']['boolean_count_after_quotient']}",
            f"- relabelled_Z17: {panels['relabelled_Z17']['boolean_count_after_quotient']}",
            f"- |F| torus subgroup: {panels['torus']['factor_base_size_F']}",
            f"- first_fall_degree: UNDETERMINED (capped; no Groebner under this card)",
            "",
            "## Scope",
            "",
            "- Toy n=17 only; no transfer to n=131.",
            "- No ECDLP solve; no break; no exponent claim.",
            "- Amazon Bedrock not used.",
            "",
        ]
    )
    results_path = EXP_ROOT / "RESULTS.md"
    if not results_path.exists():
        write_text(results_path, results)

    raw = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "stage": 1,
        "status": "completed",
        "outcome": outcome,
        "stage0_preregistered_match": stage0_ok,
        "phi8": phi8,
        "f28_mul_selftest": mul,
        "curve": curve,
        "order_17": t_rec,
        "panels": panels,
        "null_curve": null,
        "wall_clock_seconds": time.time() - t0,
        "amazon_bedrock": "NOT_USED",
        "claims": {
            "break": False,
            "exponent_move": False,
            "n131_transfer": False,
        },
    }
    write_json(run_dir / "raw-result.json", raw)
    write_text(
        run_dir / "manifest.yaml",
        "\n".join(
            [
                f"experiment_id: {EXPERIMENT_ID}",
                "stage: 1",
                "arm: B_torus_n17",
                f"approved_by: {APPROVED_BY}",
                f"outcome: {outcome}",
                "artifacts:",
                "  - raw-result.json",
                "  - manifest.yaml",
                "stage1_paths:",
                "  - experiments/EXP-FROB-8451c7/stage1/control-table.json",
                "  - experiments/EXP-FROB-8451c7/stage1/panels.json",
                "  - experiments/EXP-FROB-8451c7/RESULTS.md",
                "scientific_conclusion: null",
                "",
            ]
        ),
    )
    return raw


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stage", type=int, required=True, choices=[0, 1])
    ap.add_argument("--trial-plan", required=True)
    ap.add_argument("--run-dir", required=True, help="Harness run directory ({run_dir})")
    args = ap.parse_args()
    run_dir = Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    _ = args.trial_plan  # bound in argv for trial-plan admission / provenance
    if args.stage == 0:
        stage0(run_dir)
    else:
        stage1(run_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
