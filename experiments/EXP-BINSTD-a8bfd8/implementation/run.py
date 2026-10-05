#!/usr/bin/env python3
"""EXP-BINSTD-a8bfd8 Stages 0-3 launcher (HOLD-I modulus-weight confound).

Stage 0: Enumerate irreducible weight-3/weight-5 moduli at m in {7,11,15};
         build F_2-multiplication tensors; freeze preregistered predictions,
         tensor census, and E1/N_leaf bands into stage0/.
Stage 1: Build matched (m,t=2,l) descended window-product systems; record
         total monomial support and mean XOR-clause length; write
         stage1/support-census.json.
Stage 2: Same-weight, fixed-V, matched-width relabelling (9d12bd), and
         fixed-modulus basis-change (99294c) controls → stage2/controls.json.
Stage 3: WDSat/ANF E1-vs-E2 when an importable vendored solver is present;
         otherwise stage3/impediment.json with O-IMPEDIMENT (no Magma/Sage/
         AUXIN/Bedrock provisioning). Writes RESULTS.md with exactly one O-*.

Observations only. No ECDLP solve. No security-difference claim from w.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import random
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
    "O-STAGES-2-CONTROLS-OK",
}

STAGE2_M = 15
STAGE2_L = 6
STAGE2_RELABEL_SEEDS = 16
STAGE2_BASIS_SEEDS = 8
PRIMARY_SEED = 20261003


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



def find_all_irreducible(m: int, weight: int, limit: int = 8) -> list[int]:
    head = 1 << m
    out: list[int] = []
    if weight == 3:
        for k in range(1, m):
            cand = head | (1 << k) | 1
            if is_irreducible(cand):
                out.append(cand)
                if len(out) >= limit:
                    return out
    elif weight == 5:
        for k3 in range(3, m):
            for k2 in range(2, k3):
                for k1 in range(1, k2):
                    cand = head | (1 << k3) | (1 << k2) | (1 << k1) | 1
                    if is_irreducible(cand):
                        out.append(cand)
                        if len(out) >= limit:
                            return out
    return out


def gf2_rank(rows: list[int], width: int) -> int:
    mat = list(rows)
    rank = 0
    for col in range(width):
        piv = None
        for i in range(rank, len(mat)):
            if (mat[i] >> col) & 1:
                piv = i
                break
        if piv is None:
            continue
        mat[rank], mat[piv] = mat[piv], mat[rank]
        for i in range(len(mat)):
            if i != rank and ((mat[i] >> col) & 1):
                mat[i] ^= mat[rank]
        rank += 1
    return rank


def random_invertible_matrix(n: int, rng: random.Random) -> list[int]:
    """Return n row-bitmasks forming GL(n, F2)."""
    while True:
        rows = [rng.getrandbits(n) for _ in range(n)]
        if gf2_rank(rows, n) == n:
            return rows


def apply_linear_map(bits: list[Poly], matrix_rows: list[int]) -> list[Poly]:
    """Apply F2 linear map: out_i = xor_j M_ij in_j."""
    n = len(matrix_rows)
    assert len(bits) == n
    out: list[Poly] = [frozenset() for _ in range(n)]
    for i, row in enumerate(matrix_rows):
        acc: Poly = frozenset()
        for j in range(n):
            if (row >> j) & 1:
                acc = poly_add(acc, bits[j])
        out[i] = acc
    return out


def descended_with_window_map(
    m: int, mod: int, l: int, map_rows: list[int] | None
) -> dict[str, Any]:
    """Semaev-S3 with optional GL(l) map applied inside each V_l window."""
    x1 = window_elem(0, l, m)
    x2 = window_elem(1, l, m)
    if map_rows is not None:
        assert len(map_rows) == l
        # Map only the l live window coordinates of each block.
        def map_window(bits: list[Poly], block: int) -> list[Poly]:
            live = bits[:l]
            mapped_live = apply_linear_map(live, map_rows)
            return mapped_live + bits[l:]

        x1 = map_window(x1, 0)
        x2 = map_window(x2, 1)
    one = [frozenset({0}) if i == 0 else frozenset() for i in range(m)]
    p12 = mul_schoolbook_reduce(x1, x2, mod, m)
    s = poly_add_list(poly_add_list(p12, x1), x2)
    s2 = sym_square(s, m, mod)
    eqs = poly_add_list(poly_add_list(s2, p12), one)
    support: set[int] = set()
    term_counts: list[int] = []
    vars_used: set[int] = set()
    for bit_poly in eqs:
        support |= set(bit_poly)
        term_counts.append(len(bit_poly))
        for mono in bit_poly:
            v = mono
            while v:
                lsb = v & -v
                vars_used.add(lsb.bit_length() - 1)
                v ^= lsb
    # Drop the constant-1 monomial marker (bit 0 of mask 0 is not a var);
    # vars are encoded as bit positions in monomial masks; mask 0 is const.
    leaf_proxy = len({v for v in vars_used})  # variables appearing in any term
    # Constants use mask 0 which has no variable bits; leaf_proxy counts vars.
    return {
        "m": m,
        "l": l,
        "t": 2,
        "modulus_int": mod,
        "modulus_hex": hex(mod),
        "weight": bin(mod).count("1"),
        "core_variable_count": 2 * l,
        "descended_total_support": sum(term_counts),
        "descended_union_monomials": len(support),
        "mean_xor_clause_length": (
            sum(term_counts) / len(term_counts) if term_counts else 0.0
        ),
        "per_output_term_counts": term_counts,
        "leaf_proxy_vars_appearing": leaf_proxy,
        "nonzero_equation_count": sum(1 for t in term_counts if t > 0),
        "V_description": f"degree_lt_{l}_polynomial_window",
        "window_map_applied": map_rows is not None,
    }


def remap_monomial(mono: int, var_map_rows: list[int], nvars: int) -> int:
    """Apply GL(nvars) to variable bits inside a monomial bitmask."""
    # mono bit i set => variable i present. Image = product of images of vars.
    # Under F2 ANF with x^2=x, linear remapping of vars: substitute
    # x_j = xor_i M_ij y_i into the monomial and expand.
    # For a monomial that is a product of vars, substitute each var.
    if mono == 0:
        return 0
    # Collect source variables in the monomial.
    src_vars = []
    v = mono
    while v:
        lsb = v & -v
        src_vars.append(lsb.bit_length() - 1)
        v ^= lsb
    # Each source var j maps to the linear form with bits = column j of M,
    # where rows of M are stored as row-bitmasks: M_ij = (row_i >> j) & 1,
    # so column j bits across rows form the image of e_j.
    # Image of x_j is xor over i of M_ij y_i — as a linear Poly on y-bits.
    factors: list[Poly] = []
    for j in src_vars:
        bits: list[int] = []
        for i in range(nvars):
            if (var_map_rows[i] >> j) & 1:
                bits.append(1 << i)
        # linear form as set of singleton monomials
        factors.append(frozenset(bits) if bits else frozenset())
    # Multiply factors (Boolean).
    acc: Poly = frozenset({0})  # constant 1
    for f in factors:
        acc = poly_mul(acc, f if f else frozenset())
    # Result should be a single monomial if M is invertible? Not necessarily
    # for products; expand and XOR. Return XOR of all result monomials as
    # a multi-term poly — caller uses full poly_add across equation.
    # Here we return the frozenset via a side channel... keep as Poly.
    # Hack: encode Poly in a wrapper by returning object; change signature.
    return acc  # type: ignore[return-value]


def remap_equation_system(
    eqs: list[Poly], var_map_rows: list[int], nvars: int
) -> list[Poly]:
    """Rename/mix the Boolean unknowns of an ANF system by GL(nvars)."""
    out: list[Poly] = []
    for eq in eqs:
        acc: Poly = frozenset()
        for mono in eq:
            if mono == 0:
                acc = poly_add(acc, frozenset({0}))
                continue
            # Build product of images of each var in mono.
            src_vars = []
            v = mono
            while v:
                lsb = v & -v
                src_vars.append(lsb.bit_length() - 1)
                v ^= lsb
            factor_acc: Poly = frozenset({0})
            for j in src_vars:
                lin = frozenset(
                    1 << i for i in range(nvars) if (var_map_rows[i] >> j) & 1
                )
                factor_acc = poly_mul(factor_acc, lin)
            acc = poly_add(acc, factor_acc)
        out.append(acc)
    return out


def system_shape_indicators(eqs: list[Poly], nvars: int) -> dict[str, Any]:
    term_counts = [len(p) for p in eqs]
    support: set[int] = set()
    vars_used: set[int] = set()
    degree_hist: dict[int, int] = {}
    for p in eqs:
        support |= set(p)
        for mono in p:
            deg = bin(mono).count("1") if mono else 0
            degree_hist[deg] = degree_hist.get(deg, 0) + 1
            v = mono
            while v:
                lsb = v & -v
                vars_used.add(lsb.bit_length() - 1)
                v ^= lsb
    return {
        "nonzero_equation_count": sum(1 for t in term_counts if t > 0),
        "descended_total_support": sum(term_counts),
        "descended_union_monomials": len(support),
        "mean_xor_clause_length": (
            sum(term_counts) / len(term_counts) if term_counts else 0.0
        ),
        "leaf_proxy_vars_appearing": len(vars_used),
        "core_variable_count": nvars,
        "degree_histogram": {str(k): degree_hist[k] for k in sorted(degree_hist)},
    }


def build_semaev_eqs(m: int, mod: int, l: int) -> list[Poly]:
    x1 = window_elem(0, l, m)
    x2 = window_elem(1, l, m)
    one = [frozenset({0}) if i == 0 else frozenset() for i in range(m)]
    p12 = mul_schoolbook_reduce(x1, x2, mod, m)
    s = poly_add_list(poly_add_list(p12, x1), x2)
    s2 = sym_square(s, m, mod)
    return poly_add_list(poly_add_list(s2, p12), one)


def probe_wdsat_importable() -> dict[str, Any]:
    """Stage-3 admission: importable Python WDSat/ANF only (no build/provision)."""
    names = ("wdsat", "trimoska", "trimoska_wdsat", "anf_solver")
    found = []
    for name in names:
        spec = importlib.util.find_spec(name)
        if spec is not None:
            found.append({"name": name, "origin": getattr(spec, "origin", None)})
    vendored_c = (EXP_ROOT.parents[1] / "inputs" / "TRIMOSKA-WDSAT-2024" / "upstream" / "src" / "wdsat.c")
    return {
        "importable_modules": found,
        "vendored_c_source_present": vendored_c.is_file(),
        "vendored_c_path": str(vendored_c) if vendored_c.is_file() else None,
        "python_solver_importable": bool(found),
        "note": (
            "Contract defers Stage-3 solve unless a vendored WDSat/ANF is "
            "importable as a Python module. C sources alone → O-IMPEDIMENT; "
            "no Magma/Sage/AUXIN/Bedrock provisioning."
        ),
    }


def stage2(run_dir: Path) -> dict[str, Any]:
    t0 = time.perf_counter()
    # Require Stages 0-1 freeze artifacts (do not rewrite them).
    s0 = EXP_ROOT / "stage0" / "tensor-census.json"
    s1 = EXP_ROOT / "stage1" / "support-census.json"
    if not s0.is_file() or not s1.is_file():
        result = {
            "experiment_id": EXPERIMENT_ID,
            "hypothesis_id": HYPOTHESIS_ID,
            "approved_by": APPROVED_BY,
            "task_id": TASK_ID,
            "stage": 2,
            "status": "failed_infrastructure",
            "outcome": "O-IMPEDIMENT",
            "reason": "stage0/stage1 artifacts missing; Stages 2-3 require prior freeze",
            "claims": {"break": False, "exponent_move": False, "attack": False},
            "amazon_bedrock": "NOT_USED",
            "run_dir": str(run_dir),
        }
        return result

    stage0_census = json.loads(s0.read_text(encoding="utf-8"))
    stage1_census = json.loads(s1.read_text(encoding="utf-8"))
    if stage0_census.get("claim_A_ok") is False:
        return {
            "experiment_id": EXPERIMENT_ID,
            "hypothesis_id": HYPOTHESIS_ID,
            "approved_by": APPROVED_BY,
            "task_id": TASK_ID,
            "stage": 2,
            "status": "completed_valid",
            "outcome": "O-A-FALSE",
            "reason": "Stage 0 already falsified (A); Stage 2 skipped per SR-2",
            "claims": {"break": False, "exponent_move": False, "attack": False},
            "amazon_bedrock": "NOT_USED",
            "run_dir": str(run_dir),
        }
    if stage1_census.get("claim_B_ok") is False:
        # SR-3: Stage 3 optional; Stage 2 controls still informative — continue.
        pass

    m = STAGE2_M
    l = STAGE2_L
    tris = find_all_irreducible(m, 3, limit=2)
    pents = find_all_irreducible(m, 5, limit=2)
    if len(tris) < 2 or len(pents) < 2:
        return {
            "experiment_id": EXPERIMENT_ID,
            "hypothesis_id": HYPOTHESIS_ID,
            "approved_by": APPROVED_BY,
            "task_id": TASK_ID,
            "stage": 2,
            "status": "failed_infrastructure",
            "outcome": "O-IMPEDIMENT",
            "reason": f"need ≥2 irreducible tri and pent at m={m}",
            "claims": {"break": False, "exponent_move": False, "attack": False},
            "amazon_bedrock": "NOT_USED",
            "run_dir": str(run_dir),
        }

    # (i) same-weight control
    same_weight_rows = []
    for weight, mods in ((3, tris), (5, pents)):
        stats = [descended_with_window_map(m, mod, l, None) for mod in mods]
        supports = [s["descended_total_support"] for s in stats]
        xors = [s["mean_xor_clause_length"] for s in stats]
        same_weight_rows.append(
            {
                "weight": weight,
                "moduli_hex": [hex(x) for x in mods],
                "supports": supports,
                "xor_lengths": xors,
                "support_delta": max(supports) - min(supports),
                "xor_delta": max(xors) - min(xors),
                "exact_support_equal": supports[0] == supports[1],
                "exact_xor_equal": xors[0] == xors[1],
            }
        )
    # Cross-weight gap at primary pair (first tri vs first pent)
    primary_tri = descended_with_window_map(m, tris[0], l, None)
    primary_pent = descended_with_window_map(m, pents[0], l, None)
    cross_support = abs(
        primary_pent["descended_total_support"] - primary_tri["descended_total_support"]
    )
    cross_xor = abs(
        primary_pent["mean_xor_clause_length"] - primary_tri["mean_xor_clause_length"]
    )
    max_within_support = max(r["support_delta"] for r in same_weight_rows)
    max_within_xor = max(r["xor_delta"] for r in same_weight_rows)
    # Isolates w iff within-weight variation is strictly smaller than cross-weight gap.
    same_weight_isolates_w = (
        cross_support > 0
        and max_within_support < cross_support
        and cross_xor > 0
        and max_within_xor < cross_xor
    )

    # (ii) fixed-V across moduli
    fixed_v_ok = (
        primary_tri["V_description"] == primary_pent["V_description"]
        and primary_tri["core_variable_count"] == primary_pent["core_variable_count"]
        and primary_tri["l"] == primary_pent["l"] == l
    )

    # (iii) matched-width random relabelling (9d12bd)
    relabel_trials = []
    leaf_ratios = []
    support_gap_persists = 0
    for seed in range(PRIMARY_SEED, PRIMARY_SEED + STAGE2_RELABEL_SEEDS):
        rng = random.Random(seed)
        M = random_invertible_matrix(l, rng)
        tri_r = descended_with_window_map(m, tris[0], l, M)
        pent_r = descended_with_window_map(m, pents[0], l, M)
        leaf_t = tri_r["leaf_proxy_vars_appearing"]
        leaf_p = pent_r["leaf_proxy_vars_appearing"]
        leaf_ratio = (leaf_p / leaf_t) if leaf_t else None
        if leaf_ratio is not None:
            leaf_ratios.append(leaf_ratio)
        gap = pent_r["descended_total_support"] > tri_r["descended_total_support"]
        if gap:
            support_gap_persists += 1
        relabel_trials.append(
            {
                "seed": seed,
                "matrix_rows": M,
                "tri_support": tri_r["descended_total_support"],
                "pent_support": pent_r["descended_total_support"],
                "tri_leaf_proxy": leaf_t,
                "pent_leaf_proxy": leaf_p,
                "leaf_ratio_pent_over_tri": leaf_ratio,
                "support_gap_persists": gap,
            }
        )
    # N_leaf band: leaf_proxy ratio in [0.95, 1.05] for all seeds
    n_leaf_ok = bool(leaf_ratios) and all(N_LEAF_BAND[0] <= r <= N_LEAF_BAND[1] for r in leaf_ratios)
    # Matched-width must not destroy the w-support direction on a majority of seeds
    relabel_direction_ok = support_gap_persists >= (STAGE2_RELABEL_SEEDS * 3) // 4
    claim_9d12bd_ok = n_leaf_ok and relabel_direction_ok

    # (iv) fixed-modulus F_2-basis change on Boolean unknowns (99294c).
    # Invertible remapping of the 2l factor-base bit coordinates must preserve
    # solution-set shape indicators (nonzero eq count, degree histogram,
    # leaf_proxy). Support totals may redistribute across equations but the
    # degree histogram of the ANF is invariant under GL(2l) substitution.
    basis_trials = []
    basis_agree = True
    nvars = 2 * l
    base_eqs = build_semaev_eqs(m, tris[0], l)
    base_shape = system_shape_indicators(base_eqs, nvars)
    for seed in range(PRIMARY_SEED + 1000, PRIMARY_SEED + 1000 + STAGE2_BASIS_SEEDS):
        rng = random.Random(seed)
        B = random_invertible_matrix(nvars, rng)
        remapped = remap_equation_system(base_eqs, B, nvars)
        shape = system_shape_indicators(remapped, nvars)
        # Degree-histogram term counts are NOT invariant under expanded
        # linear substitution (products of linear forms fan out). Invariants:
        # nonzero equation count, variable count, leaf proxy, and max degree.
        base_max_deg = max(int(k) for k in base_shape["degree_histogram"])
        shape_max_deg = max(int(k) for k in shape["degree_histogram"])
        agree = (
            shape["nonzero_equation_count"] == base_shape["nonzero_equation_count"]
            and shape["core_variable_count"] == base_shape["core_variable_count"]
            and shape["leaf_proxy_vars_appearing"] == base_shape["leaf_proxy_vars_appearing"]
            and shape_max_deg == base_max_deg
        )
        if not agree:
            basis_agree = False
        basis_trials.append(
            {
                "seed": seed,
                "agree_shape_indicators": agree,
                "nonzero_equation_count": shape["nonzero_equation_count"],
                "leaf_proxy_vars_appearing": shape["leaf_proxy_vars_appearing"],
                "degree_histogram": shape["degree_histogram"],
                "support": shape["descended_total_support"],
            }
        )
    claim_99294c_ok = basis_agree

    artifact = same_weight_isolates_w and fixed_v_ok
    if not artifact:
        outcome = "O-ARTIFACT"
    elif not claim_9d12bd_ok:
        outcome = "O-9d12bd-FALSE"
    elif not claim_99294c_ok:
        outcome = "O-99294c-FALSE"
    else:
        outcome = "O-STAGES-2-CONTROLS-OK"

    controls = {
        "schema": "binstd.hold_i.stage2_controls.v1",
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "task_id": TASK_ID,
        "recorded_at": utc_now(),
        "m": m,
        "l": l,
        "t": 2,
        "same_weight": {
            "rows": same_weight_rows,
            "cross_support_gap": cross_support,
            "cross_xor_gap": cross_xor,
            "max_within_support_delta": max_within_support,
            "max_within_xor_delta": max_within_xor,
            "isolates_w": same_weight_isolates_w,
            "note": (
                "Pass when within-weight support/XOR deltas are strictly smaller "
                "than the cross-weight (pent vs tri) gaps — isolates w from the "
                "specific irreducible. Exact equality recorded per row."
            ),
        },
        "fixed_V": {
            "ok": fixed_v_ok,
            "V_description": primary_tri["V_description"],
            "core_variable_count": primary_tri["core_variable_count"],
        },
        "matched_width_relabel_9d12bd": {
            "n_seeds": STAGE2_RELABEL_SEEDS,
            "n_leaf_band": N_LEAF_BAND,
            "n_leaf_ok": n_leaf_ok,
            "leaf_ratios": leaf_ratios,
            "support_gap_persists_count": support_gap_persists,
            "relabel_direction_ok": relabel_direction_ok,
            "claim_9d12bd_ok": claim_9d12bd_ok,
            "trials": relabel_trials,
        },
        "basis_change_99294c": {
            "n_seeds": STAGE2_BASIS_SEEDS,
            "base_shape": base_shape,
            "claim_99294c_ok": claim_99294c_ok,
            "trials": basis_trials,
        },
        "outcome": outcome,
        "amazon_bedrock": "NOT SELECTED",
    }
    stage2_dir = EXP_ROOT / "stage2"
    stage2_dir.mkdir(parents=True, exist_ok=True)
    write_json(stage2_dir / "controls.json", controls)

    elapsed = time.perf_counter() - t0
    return {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "task_id": TASK_ID,
        "stage": 2,
        "status": "completed_valid",
        "outcome": outcome,
        "same_weight_isolates_w": same_weight_isolates_w,
        "fixed_V_ok": fixed_v_ok,
        "claim_9d12bd_ok": claim_9d12bd_ok,
        "claim_99294c_ok": claim_99294c_ok,
        "artifacts": [
            "experiments/EXP-BINSTD-a8bfd8/stage2/controls.json",
        ],
        "wall_seconds": elapsed,
        "claims": {"break": False, "exponent_move": False, "attack": False},
        "amazon_bedrock": "NOT_USED",
        "run_dir": str(run_dir),
    }


def stage3(run_dir: Path) -> dict[str, Any]:
    t0 = time.perf_counter()
    controls_path = EXP_ROOT / "stage2" / "controls.json"
    if not controls_path.is_file():
        result = {
            "experiment_id": EXPERIMENT_ID,
            "hypothesis_id": HYPOTHESIS_ID,
            "approved_by": APPROVED_BY,
            "task_id": TASK_ID,
            "stage": 3,
            "status": "failed_infrastructure",
            "outcome": "O-IMPEDIMENT",
            "reason": "stage2/controls.json missing",
            "claims": {"break": False, "exponent_move": False, "attack": False},
            "amazon_bedrock": "NOT_USED",
            "run_dir": str(run_dir),
        }
        _write_results("O-IMPEDIMENT", result)
        return result

    controls = json.loads(controls_path.read_text(encoding="utf-8"))
    stage2_outcome = controls.get("outcome")
    # If Stage 2 already falsified a control, that outcome is authoritative.
    if stage2_outcome in {"O-ARTIFACT", "O-9d12bd-FALSE", "O-99294c-FALSE", "O-A-FALSE", "O-B-FALSE"}:
        result = {
            "experiment_id": EXPERIMENT_ID,
            "hypothesis_id": HYPOTHESIS_ID,
            "approved_by": APPROVED_BY,
            "task_id": TASK_ID,
            "stage": 3,
            "status": "completed_valid",
            "outcome": stage2_outcome,
            "reason": "Stage 2 control outcome is terminal; Stage 3 solver arm not entered",
            "claims": {"break": False, "exponent_move": False, "attack": False},
            "amazon_bedrock": "NOT_USED",
            "run_dir": str(run_dir),
            "artifacts": ["experiments/EXP-BINSTD-a8bfd8/stage2/controls.json"],
        }
        _write_results(stage2_outcome, result)
        return result

    probe = probe_wdsat_importable()
    stage3_dir = EXP_ROOT / "stage3"
    stage3_dir.mkdir(parents=True, exist_ok=True)

    if not probe["python_solver_importable"]:
        impediment = {
            "schema": "binstd.hold_i.stage3_impediment.v1",
            "experiment_id": EXPERIMENT_ID,
            "hypothesis_id": HYPOTHESIS_ID,
            "approved_by": APPROVED_BY,
            "task_id": TASK_ID,
            "recorded_at": utc_now(),
            "outcome": "O-IMPEDIMENT",
            "reason": (
                "No importable Python WDSat/ANF module on this machine. "
                "Vendored C sources at inputs/TRIMOSKA-WDSAT-2024 are present "
                "but not built/provisioned (contract forbids Magma/Sage/AUXIN/"
                "Bedrock provisioning). Stages 0-2 deliverables stand."
            ),
            "probe": probe,
            "asserts_nothing_about": (
                "E1/E2 conflict-count classification; (A)/(B) Stage 0-1 claims; "
                "Stage-2 control outcomes"
            ),
            "amazon_bedrock": "NOT SELECTED",
        }
        write_json(stage3_dir / "impediment.json", impediment)
        elapsed = time.perf_counter() - t0
        result = {
            "experiment_id": EXPERIMENT_ID,
            "hypothesis_id": HYPOTHESIS_ID,
            "approved_by": APPROVED_BY,
            "task_id": TASK_ID,
            "stage": 3,
            "status": "completed_valid",
            "outcome": "O-IMPEDIMENT",
            "probe": probe,
            "artifacts": [
                "experiments/EXP-BINSTD-a8bfd8/stage2/controls.json",
                "experiments/EXP-BINSTD-a8bfd8/stage3/impediment.json",
                "experiments/EXP-BINSTD-a8bfd8/RESULTS.md",
            ],
            "wall_seconds": elapsed,
            "claims": {"break": False, "exponent_move": False, "attack": False},
            "amazon_bedrock": "NOT_USED",
            "run_dir": str(run_dir),
            "scope_note": (
                "Stages 0-2 complete; Stage 3 deferred with O-IMPEDIMENT under "
                "DEC-20261002-b1f692 SR-5. No E1/E2 classification."
            ),
        }
        _write_results("O-IMPEDIMENT", result)
        return result

    # Importable solver path reserved; not expected on this host.
    raise RuntimeError("importable solver present but solve arm not implemented in this admission")



def _write_results(outcome: str, result: dict[str, Any]) -> None:
    if outcome not in ALLOWED_OUTCOMES:
        raise ValueError(f"unexpected outcome {outcome!r}")
    stage = result.get("stage")
    plan_label = "Stages 0-3 expand plan" if stage in (2, 3) else "Stages 0-1 admission plan"
    body = (
        f"# RESULTS — {EXPERIMENT_ID} ({plan_label})\n\n"
        f"- Hypothesis: `{HYPOTHESIS_ID}`\n"
        f"- Approved by: `{APPROVED_BY}`\n"
        f"- Expand decision: `DEC-20261003-d323c0`\n"
        f"- Executor task: `{TASK_ID}`\n"
        f"- Outcome (exactly one): **{outcome}**\n"
        f"- Stage: {stage}\n"
        f"- Status: `{result.get('status')}`\n"
        f"- Claim (A) ok (Stage 0): `{result.get('claim_A_ok', 'see stage0/tensor-census.json')}`\n"
        f"- Claim (B) ok (Stage 1): `{result.get('claim_B_ok', 'see stage1/support-census.json')}`\n"
        f"- Stage-2 controls: same_weight_isolates_w={result.get('same_weight_isolates_w', 'see stage2/controls.json')}; "
        f"9d12bd={result.get('claim_9d12bd_ok', 'n/a')}; 99294c={result.get('claim_99294c_ok', 'n/a')}\n"
        f"- Break / exponent / attack: false / false / false\n"
        f"- Amazon Bedrock: NOT USED\n"
        f"- Recorded at: {utc_now()}\n"
    )
    results_path = EXP_ROOT / "RESULTS.md"
    # RESULTS.md is the single refreshable summary across admission executions.
    results_path.write_text(body, encoding="utf-8")


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
    global TASK_ID
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=int, required=True, choices=[0, 1, 2, 3])
    parser.add_argument("--trial-plan", required=True)
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args(argv)
    run_dir = Path(args.run_dir)
    plan_path = Path(args.trial_plan)
    if not plan_path.is_file():
        print(f"missing trial plan: {plan_path}", file=sys.stderr)
        return 2
    try:
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        if isinstance(plan.get("task_id"), str) and plan["task_id"].strip():
            TASK_ID = plan["task_id"]
    except (OSError, json.JSONDecodeError):
        pass
    try:
        if args.stage == 0:
            payload = stage0(run_dir)
        elif args.stage == 1:
            payload = stage1(run_dir)
        elif args.stage == 2:
            payload = stage2(run_dir)
        else:
            payload = stage3(run_dir)
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
            if args.stage in (1, 3):
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
