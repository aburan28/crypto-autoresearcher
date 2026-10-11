#!/usr/bin/env python3
"""EXP-BINSTD-a8bfd8 Stages 0-1 launcher (HOLD-I modulus-weight confound).

Stage 0: Enumerate irreducible weight-3/weight-5 moduli at m in {7,11,15};
         build F_2-multiplication tensors; freeze preregistered predictions,
         tensor census, and E1/N_leaf bands into stage0/.
Stage 1: Build matched (m,t=2,l) descended window-product systems; record
         total monomial support and mean XOR-clause length; write
         stage1/support-census.json and RESULTS.md with exactly one O-* label.

Observations only. Stages 2-3 remain on the design contract / design card
TASK-20261002-c39f37 and are NOT enumerated in trial-plan-v1. No Magma/Sage/
AUXIN/Bedrock. No ECDLP solve. No security-difference claim from w.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

EXPERIMENT_ID = "EXP-BINSTD-a8bfd8"
HYPOTHESIS_ID = "H-BINSTD-85e778"
APPROVED_BY = "DEC-20261002-b1f692"
TASK_ID = "TASK-20261003-a5391d"
EXP_ROOT = Path(__file__).resolve().parents[1]
FIELD_DEGREES = (7, 11, 15)
L_LEVELS = (6, 7, 8)
E1_C_BAND = [0.9, 1.0]
N_LEAF_BAND = [0.95, 1.05]
ALLOWED_OUTCOMES = {
    "O-E1-CONFIRMED",
    "O-E2",
    "O-A-FALSE",
    "O-B-FALSE",
    "O-9d12bd-FALSE",
    "O-99294c-FALSE",
    "O-ARTIFACT",
    "O-IMPEDIMENT",
    "O-STAGES-0-1-COMPLETE",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


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


def clmul(a: int, b: int) -> int:
    r = 0
    while b:
        if b & 1:
            r ^= a
        a <<= 1
        b >>= 1
    return r


def pmod(a: int, m: int) -> int:
    dm = m.bit_length() - 1
    while a and a.bit_length() - 1 >= dm:
        a ^= m << (a.bit_length() - 1 - dm)
    return a


def pgcd(a: int, b: int) -> int:
    while b:
        a, b = b, pmod(a, b)
    return a


def is_irreducible(mod: int) -> bool:
    n = mod.bit_length() - 1
    x = 2
    cur = x
    ok = True
    for i in range(1, n + 1):
        cur = pmod(clmul(cur, cur), mod)
        if i <= n // 2 and pgcd(mod, cur ^ x) != 1:
            ok = False
    return ok and cur == x


def poly_to_string(mod: int) -> str:
    n = mod.bit_length() - 1
    terms = []
    for i in range(n, -1, -1):
        if (mod >> i) & 1:
            if i == 0:
                terms.append("1")
            elif i == 1:
                terms.append("x")
            else:
                terms.append(f"x^{i}")
    return " + ".join(terms) if terms else "0"


def find_irreducible(m: int, weight: int) -> int:
    head = 1 << m
    if weight == 3:
        for k in range(1, m):
            cand = head | (1 << k) | 1
            if is_irreducible(cand):
                return cand
    elif weight == 5:
        for k3 in range(3, m):
            for k2 in range(2, k3):
                for k1 in range(1, k2):
                    cand = head | (1 << k3) | (1 << k2) | (1 << k1) | 1
                    if is_irreducible(cand):
                        return cand
    raise ArithmeticError(f"no irreducible weight-{weight} of degree {m}")


def multiplication_tensor_stats(m: int, mod: int) -> dict[str, Any]:
    """Count distinct quadratic monomials and per-output XOR lengths.

    Structure constants: e_i * e_j = sum_k c_{ijk} e_k. For i<=j, each nonzero
    c_{ijk} contributes quadratic monomial x_i x_j (or x_i^2 when i=j) to
    output bit k. Distinct quadratic monomials are counted across all outputs.
    Per-output XOR length is the number of nonzero (i,j) contributions to k.
    """
    # Claim (A) uses incidence total (sum over outputs of nonzero i<=j
    # contributions). The union of pairs is modulus-blind because every
    # e_i*e_j is nonzero; per-output XOR length scales with weight w.
    distinct_pairs: set[tuple[int, int]] = set()
    per_output_xor: list[int] = []
    for k in range(m):
        xor_len = 0
        for i in range(m):
            for j in range(i, m):
                prod = pmod(clmul(1 << i, 1 << j), mod)
                if (prod >> k) & 1:
                    xor_len += 1
                    distinct_pairs.add((i, j))
        per_output_xor.append(xor_len)
    incidence_total = sum(per_output_xor)
    return {
        "modulus_int": mod,
        "modulus_hex": hex(mod),
        "modulus_poly": poly_to_string(mod),
        "weight": bin(mod).count("1"),
        "irreducible": True,
        "distinct_quadratic_monomials": incidence_total,
        "distinct_quadratic_monomials_definition": (
            "sum over output bits of nonzero (i<=j) contributions; "
            "equals total nonzero structure-constant incidences"
        ),
        "union_quadratic_pairs": len(distinct_pairs),
        "per_output_xor_lengths": per_output_xor,
        "mean_per_output_xor_length": (
            sum(per_output_xor) / len(per_output_xor) if per_output_xor else 0.0
        ),
        "max_per_output_xor_length": max(per_output_xor) if per_output_xor else 0,
    }


Poly = frozenset  # frozenset[int] monomial bitmasks


def poly_add(a: Poly, b: Poly) -> Poly:
    return frozenset(a.symmetric_difference(b))


def poly_mul(a: Poly, b: Poly) -> Poly:
    out: dict[int, int] = {}
    for m1 in a:
        for m2 in b:
            m = m1 | m2  # Boolean: x_i^2 = x_i
            out[m] = out.get(m, 0) ^ 1
    return frozenset(m for m, c in out.items() if c)


def window_elem(block_id: int, l: int, m: int) -> list[Poly]:
    bits: list[Poly] = []
    for i in range(m):
        if i < l:
            bits.append(frozenset({1 << (block_id * l + i)}))
        else:
            bits.append(frozenset())
    return bits


def mul_schoolbook_reduce(x: list[Poly], y: list[Poly], mod: int, m: int) -> list[Poly]:
    acc: list[Poly] = [frozenset() for _ in range(2 * m - 1)]
    for i in range(m):
        if not x[i]:
            continue
        for j in range(m):
            if not y[j]:
                continue
            acc[i + j] = poly_add(acc[i + j], poly_mul(x[i], y[j]))
    lower = mod ^ (1 << m)
    for deg in range(2 * m - 2, m - 1, -1):
        if not acc[deg]:
            continue
        chunk = acc[deg]
        acc[deg] = frozenset()
        shift = deg - m
        for b in range(m):
            if (lower >> b) & 1:
                acc[shift + b] = poly_add(acc[shift + b], chunk)
    return acc[:m]


def poly_add_list(a: list[Poly], b: list[Poly]) -> list[Poly]:
    return [poly_add(x, y) for x, y in zip(a, b)]


def sym_square(bits: list[Poly], m: int, mod: int) -> list[Poly]:
    """Squaring is F_2-linear: bit positions of e_i^2 determine the map."""
    out: list[Poly] = [frozenset() for _ in range(m)]
    for i in range(m):
        sq = pmod(clmul(1 << i, 1 << i), mod)
        for b in range(m):
            if (sq >> b) & 1:
                out[b] = poly_add(out[b], bits[i])
    return out


def descended_window_product_stats(m: int, mod: int, l: int) -> dict[str, Any]:
    """Descended t=2-style system: Semaev-S3 ANF on two V_l windows + fixed x3=1.

    S3(x1,x2,1) = (x1 x2 + x1 + x2)^2 + x1 x2 + 1  (char-2, b=1). Uses two
    factor-base windows (arity-2 FB summands) and forces reduction via the
    square, so modulus weight appears even when 2(l-1) < m.
    Fixed V = degree-<l polynomial window for both FB elements.
    """
    x1 = window_elem(0, l, m)
    x2 = window_elem(1, l, m)
    one = [frozenset({0}) if i == 0 else frozenset() for i in range(m)]  # const 1
    p12 = mul_schoolbook_reduce(x1, x2, mod, m)
    # x1*1 = x1, x2*1 = x2
    s = poly_add_list(poly_add_list(p12, x1), x2)
    s2 = sym_square(s, m, mod)
    # S3 = s2 + x1*x2*1 + b = s2 + p12 + 1
    eqs = poly_add_list(poly_add_list(s2, p12), one)
    support: set[int] = set()
    term_counts: list[int] = []
    for bit_poly in eqs:
        support |= set(bit_poly)
        term_counts.append(len(bit_poly))
    return {
        "m": m,
        "l": l,
        "t": 2,
        "system": "semaev_S3_x3_fixed_1",
        "modulus_int": mod,
        "modulus_hex": hex(mod),
        "modulus_poly": poly_to_string(mod),
        "weight": bin(mod).count("1"),
        "core_variable_count": 2 * l,
        "descended_total_support": sum(term_counts),
        "descended_union_monomials": len(support),
        "mean_xor_clause_length": (
            sum(term_counts) / len(term_counts) if term_counts else 0.0
        ),
        "per_output_term_counts": term_counts,
        "max_xor_clause_length": max(term_counts) if term_counts else 0,
        "V_description": f"degree_lt_{l}_polynomial_window",
    }


def stage0(run_dir: Path) -> dict[str, Any]:
    t0 = time.perf_counter()
    stage0_dir = EXP_ROOT / "stage0"
    stage0_dir.mkdir(parents=True, exist_ok=True)

    cells: list[dict[str, Any]] = []
    claim_a_ok = True
    claim_a_details: list[dict[str, Any]] = []
    for m in FIELD_DEGREES:
        tri = find_irreducible(m, 3)
        pent = find_irreducible(m, 5)
        tri_stats = multiplication_tensor_stats(m, tri)
        pent_stats = multiplication_tensor_stats(m, pent)
        ratio = (
            pent_stats["distinct_quadratic_monomials"]
            / tri_stats["distinct_quadratic_monomials"]
            if tri_stats["distinct_quadratic_monomials"]
            else None
        )
        a_holds = (
            ratio is not None
            and pent_stats["distinct_quadratic_monomials"]
            > tri_stats["distinct_quadratic_monomials"]
        )
        if not a_holds:
            claim_a_ok = False
        cell = {
            "m": m,
            "trinomial": tri_stats,
            "pentanomial": pent_stats,
            "pent_over_tri_distinct_quadratic_ratio": ratio,
            "claim_A_direction_holds": a_holds,
        }
        cells.append(cell)
        claim_a_details.append(
            {
                "m": m,
                "tri_distinct": tri_stats["distinct_quadratic_monomials"],
                "pent_distinct": pent_stats["distinct_quadratic_monomials"],
                "ratio": ratio,
                "a_holds": a_holds,
            }
        )

    prereg = {
        "schema": "binstd.hold_i.preregistered_predictions.v1",
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "task_id": TASK_ID,
        "committed_before_stage1": True,
        "committed_at": utc_now(),
        "field_degrees": list(FIELD_DEGREES),
        "predictions": {
            "A_tensor_sparsity": {
                "quantity": "distinct_quadratic_monomials pentanomial/trinomial",
                "direction": "> 1 (bounded away from 1; constant-factor in m)",
                "falsifies_as": "O-A-FALSE when equal at any m in {7,11,15}",
            },
            "B_descended_support": {
                "quantity": "descended_total_support and mean_xor_clause_length",
                "direction": "pentanomial > trinomial at matched (m,t=2,l)",
                "falsifies_as": "O-B-FALSE",
            },
            "E1_conflict_band": {
                "quantity": "Stage-3 WDSat/ANF conflict_count ratio",
                "interval": E1_C_BAND,
                "note": "Frozen here; Stage 3 not in trial-plan-v1.",
            },
            "N_leaf_band_9d12bd": {
                "quantity": "leaf_count(pentanomial)/leaf_count(trinomial)",
                "interval": N_LEAF_BAND,
                "note": "Frozen for Stage-2/3; not measured in Stages 0-1.",
            },
        },
        "amazon_bedrock": "NOT SELECTED",
    }
    census = {
        "schema": "binstd.hold_i.tensor_census.v1",
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "task_id": TASK_ID,
        "recorded_at": utc_now(),
        "cells": cells,
        "claim_A_ok": claim_a_ok,
        "claim_A_details": claim_a_details,
        "amazon_bedrock": "NOT SELECTED",
    }
    note = (
        f"# Stage 0 derivations — {EXPERIMENT_ID}\n\n"
        f"- Hypothesis: `{HYPOTHESIS_ID}` / approval `{APPROVED_BY}`.\n"
        f"- Enumerated first irreducible weight-3 and weight-5 moduli at "
        f"m in {list(FIELD_DEGREES)} (deterministic lex order).\n"
        f"- Multiplication tensors: schoolbook structure constants via "
        f"`clmul`+`pmod`; distinct quadratic monomials counted across all "
        f"output bits; per-output XOR lengths recorded.\n"
        f"- E1 c-band frozen to {E1_C_BAND}; N_leaf band frozen to {N_LEAF_BAND}.\n"
        f"- Claim (A) direction holds on Stage-0 census: `{claim_a_ok}`.\n"
        f"- No Magma/Sage/AUXIN/Bedrock. No Stage-1 metrics used as evidence "
        f"before this freeze.\n"
        f"- Recorded at {utc_now()}.\n"
    )
    write_json(stage0_dir / "preregistered-predictions.json", prereg)
    write_json(stage0_dir / "tensor-census.json", census)
    write_text(stage0_dir / "derivations-note.md", note)

    outcome = "S0-FREEZE-OK" if claim_a_ok else "O-A-FALSE"
    elapsed = time.perf_counter() - t0
    return {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "task_id": TASK_ID,
        "stage": 0,
        "status": "completed_valid",
        "outcome": outcome,
        "claim_A_ok": claim_a_ok,
        "cells_summary": claim_a_details,
        "artifacts": [
            "experiments/EXP-BINSTD-a8bfd8/stage0/preregistered-predictions.json",
            "experiments/EXP-BINSTD-a8bfd8/stage0/tensor-census.json",
            "experiments/EXP-BINSTD-a8bfd8/stage0/derivations-note.md",
        ],
        "wall_seconds": elapsed,
        "claims": {"break": False, "exponent_move": False, "attack": False},
        "amazon_bedrock": "NOT_USED",
        "run_dir": str(run_dir),
    }


def stage1(run_dir: Path) -> dict[str, Any]:
    t0 = time.perf_counter()
    prereg_path = EXP_ROOT / "stage0" / "preregistered-predictions.json"
    census_path = EXP_ROOT / "stage0" / "tensor-census.json"
    if not prereg_path.is_file() or not census_path.is_file():
        result = {
            "experiment_id": EXPERIMENT_ID,
            "hypothesis_id": HYPOTHESIS_ID,
            "approved_by": APPROVED_BY,
            "task_id": TASK_ID,
            "stage": 1,
            "status": "failed_infrastructure",
            "outcome": "O-IMPEDIMENT",
            "reason": "stage0 freeze missing; Stage 0 must complete first",
            "claims": {"break": False, "exponent_move": False, "attack": False},
            "amazon_bedrock": "NOT_USED",
            "run_dir": str(run_dir),
        }
        _write_results("O-IMPEDIMENT", result)
        return result

    stage0_census = json.loads(census_path.read_text(encoding="utf-8"))
    if stage0_census.get("claim_A_ok") is False:
        result = {
            "experiment_id": EXPERIMENT_ID,
            "hypothesis_id": HYPOTHESIS_ID,
            "approved_by": APPROVED_BY,
            "task_id": TASK_ID,
            "stage": 1,
            "status": "completed_valid",
            "outcome": "O-A-FALSE",
            "reason": "Stage 0 already falsified (A); Stage 1 skipped per SR-2",
            "claims": {"break": False, "exponent_move": False, "attack": False},
            "amazon_bedrock": "NOT_USED",
            "run_dir": str(run_dir),
        }
        _write_results("O-A-FALSE", result)
        return result

    stage1_dir = EXP_ROOT / "stage1"
    stage1_dir.mkdir(parents=True, exist_ok=True)

    comparisons: list[dict[str, Any]] = []
    claim_b_ok = True
    for m in FIELD_DEGREES:
        tri = find_irreducible(m, 3)
        pent = find_irreducible(m, 5)
        for l in L_LEVELS:
            if l >= m:
                comparisons.append(
                    {
                        "m": m,
                        "l": l,
                        "skipped": True,
                        "reason": "l >= m; window not a proper subspace of F_2^m",
                    }
                )
                continue
            tri_s = descended_window_product_stats(m, tri, l)
            pent_s = descended_window_product_stats(m, pent, l)
            b_support = pent_s["descended_total_support"] > tri_s["descended_total_support"]
            b_xor = pent_s["mean_xor_clause_length"] > tri_s["mean_xor_clause_length"]
            b_holds = b_support and b_xor
            if not b_holds:
                claim_b_ok = False
            comparisons.append(
                {
                    "m": m,
                    "l": l,
                    "t": 2,
                    "skipped": False,
                    "trinomial": tri_s,
                    "pentanomial": pent_s,
                    "support_ratio_pent_over_tri": (
                        pent_s["descended_total_support"] / tri_s["descended_total_support"]
                        if tri_s["descended_total_support"]
                        else None
                    ),
                    "xor_length_ratio_pent_over_tri": (
                        pent_s["mean_xor_clause_length"] / tri_s["mean_xor_clause_length"]
                        if tri_s["mean_xor_clause_length"]
                        else None
                    ),
                    "claim_B_support_holds": b_support,
                    "claim_B_xor_holds": b_xor,
                    "claim_B_holds": b_holds,
                }
            )

    support = {
        "schema": "binstd.hold_i.support_census.v1",
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "task_id": TASK_ID,
        "recorded_at": utc_now(),
        "summation_arity_t": 2,
        "l_levels": list(L_LEVELS),
        "comparisons": comparisons,
        "claim_B_ok": claim_b_ok,
        "amazon_bedrock": "NOT SELECTED",
        "note": (
            "t=2 descended system = Semaev-S3(x1,x2,1) on two fixed-V degree-<l "
            "window elements under each modulus (matched V). Stages 2-3 deferred."
        ),
    }
    write_json(stage1_dir / "support-census.json", support)

    if claim_b_ok:
        outcome = "O-STAGES-0-1-COMPLETE"
    else:
        outcome = "O-B-FALSE"
    elapsed = time.perf_counter() - t0
    result = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "task_id": TASK_ID,
        "stage": 1,
        "status": "completed_valid",
        "outcome": outcome,
        "claim_B_ok": claim_b_ok,
        "n_comparisons": sum(1 for c in comparisons if not c.get("skipped")),
        "artifacts": [
            "experiments/EXP-BINSTD-a8bfd8/stage1/support-census.json",
            "experiments/EXP-BINSTD-a8bfd8/RESULTS.md",
        ],
        "wall_seconds": elapsed,
        "claims": {"break": False, "exponent_move": False, "attack": False},
        "amazon_bedrock": "NOT_USED",
        "run_dir": str(run_dir),
        "scope_note": (
            "Stages 0-1 only under trial-plan-v1. Stage 2 controls and Stage 3 "
            "WDSat/ANF E1-vs-E2 remain authorized on the contract but are not "
            "in this plan."
        ),
    }
    _write_results(outcome, result)
    return result


def _write_results(outcome: str, result: dict[str, Any]) -> None:
    if outcome not in ALLOWED_OUTCOMES:
        raise ValueError(f"unexpected outcome {outcome!r}")
    text = (
        f"# RESULTS — {EXPERIMENT_ID} (Stages 0-1 admission plan)\n\n"
        f"- Hypothesis: `{HYPOTHESIS_ID}`\n"
        f"- Approved by: `{APPROVED_BY}`\n"
        f"- Executor task: `{TASK_ID}`\n"
        f"- Outcome (exactly one): **{outcome}**\n"
        f"- Stage: {result.get('stage')}\n"
        f"- Status: `{result.get('status')}`\n"
        f"- Claim (A) ok (Stage 0): `{result.get('claim_A_ok', 'see stage0/tensor-census.json')}`\n"
        f"- Claim (B) ok (Stage 1): `{result.get('claim_B_ok', 'n/a')}`\n"
        f"- Break / exponent / attack: false / false / false\n"
        f"- Amazon Bedrock: NOT USED\n"
        f"- Stages 2-3: not enumerated in trial-plan-v1; remain on design card "
        f"`TASK-20261002-c39f37`.\n"
        f"- Recorded at: {utc_now()}\n"
    )
    results_path = EXP_ROOT / "RESULTS.md"
    if results_path.exists():
        # Stage 1 may refresh RESULTS.md after Stage 0; allow overwrite of
        # this single summary file within the same admission execution.
        results_path.write_text(text, encoding="utf-8")
    else:
        write_text(results_path, text)


def emit_run_artifacts(run_dir: Path, payload: dict[str, Any]) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    raw = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "task_id": TASK_ID,
        "amazon_bedrock": payload.get("amazon_bedrock", "NOT_USED"),
        "claims": payload.get("claims", {"break": False, "exponent_move": False, "attack": False}),
        "stage": payload.get("stage"),
        "result": {
            "status": payload.get("status"),
            "stage": payload.get("stage"),
            "outcome": payload.get("outcome"),
            "detail": payload,
        },
        "recorded_at": utc_now(),
    }
    (run_dir / "raw-result.json").write_text(
        json.dumps(raw, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    lines = [
        f"experiment_id: {EXPERIMENT_ID}",
        f"hypothesis_id: {HYPOTHESIS_ID}",
        f"approved_by: {APPROVED_BY}",
        f"task_id: {TASK_ID}",
        f"stage: {payload.get('stage')}",
        f"status: {payload.get('status')}",
        f"outcome: {payload.get('outcome')}",
        "amazon_bedrock: NOT_USED",
        "claims:",
        "  break: false",
        "  exponent_move: false",
        "  attack: false",
    ]
    (run_dir / "manifest.yaml").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=int, required=True, choices=[0, 1])
    parser.add_argument("--trial-plan", required=True)
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args(argv)
    run_dir = Path(args.run_dir)
    plan_path = Path(args.trial_plan)
    if not plan_path.is_file():
        print(f"missing trial plan: {plan_path}", file=sys.stderr)
        return 2
    try:
        if args.stage == 0:
            payload = stage0(run_dir)
        else:
            payload = stage1(run_dir)
        emit_run_artifacts(run_dir, payload)
    except Exception as exc:  # noqa: BLE001 — surface infra failures honestly
        err = {
            "experiment_id": EXPERIMENT_ID,
            "hypothesis_id": HYPOTHESIS_ID,
            "approved_by": APPROVED_BY,
            "task_id": TASK_ID,
            "stage": args.stage,
            "status": "failed_infrastructure",
            "outcome": "O-IMPEDIMENT",
            "reason": f"{type(exc).__name__}: {exc}",
            "claims": {"break": False, "exponent_move": False, "attack": False},
            "amazon_bedrock": "NOT_USED",
            "run_dir": str(run_dir),
        }
        try:
            emit_run_artifacts(run_dir, err)
            _write_results("O-IMPEDIMENT", err)
        except Exception:  # noqa: BLE001
            pass
        print(err["reason"], file=sys.stderr)
        return 1
    print(json.dumps({"stage": args.stage, "outcome": payload.get("outcome"),
                      "status": payload.get("status")}, sort_keys=True))
    return 0 if payload.get("status") == "completed_valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
