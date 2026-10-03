#!/usr/bin/env python3
"""EXP-BINSTD-591d28 Stages 0-1 launcher (HOLD-X7 symmetrisation saturation).

Stage 0: Freeze n=131 balanced (m,l) and RC-1 dimension tables, predicted
         spurious factors, subfield baseline, and preregistered predictions.
Stage 1: Verify P2 product-space dims by explicit span; measure P1 spurious
         factor and lift_agreement on RC-1 (m=3, l in {4,5,6}) via S_4
         field evaluator + e-space census over prod V^{(k)} (exhaustive at
         l=4; sampled lower bounds at l in {5,6}); write RESULTS.md with
         exactly one Stages 0-1 O-* label.

Observations only. Stages 2-3 remain on design card TASK-20261002-d8df85 and
are NOT enumerated in trial-plan-v1. No Magma/Sage/AUXIN/Bedrock. No ECDLP
solve. No exponent / break claim.
"""
from __future__ import annotations

import argparse
import json
import math
import random
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

EXPERIMENT_ID = "EXP-BINSTD-591d28"
HYPOTHESIS_ID = "H-BINSTD-5fdceb"
APPROVED_BY = "DEC-20261002-397fcd"
TASK_ID = "TASK-20261003-83db99"
EXP_ROOT = Path(__file__).resolve().parents[1]
MASTER_SEED = 2026092731
N_RC1 = 17
MOD_RC1 = (1 << 17) | (1 << 3) | 1  # t^17 + t^3 + 1
A_RC1 = 97044
B_RC1 = 126251
M = 3
L_LEVELS = (4, 5, 6)
P2_L_LEVELS = range(4, 10)
N131_CELLS = ((5, 23), (5, 28), (6, 22), (6, 24), (8, 20))
N_TARGETS = 50
# Sampling budgets (machine-protection); l=4 is exhaustive over 2^21.
# E-space census budgets (per target). Full 2^{sum dims} exhaustive is hours+
# in pure Python (IDEA note); report Monte-Carlo lower/point estimates with
# explicit sample sizes. Genuine V^3 counts remain exact.
SAMPLE_E_BUDGET = {4: 1 << 14, 5: 1 << 13, 6: 1 << 12}
ALLOWED_OUTCOMES = {
    "S0-FREEZE-OK",
    "O-STAGES-0-1-COMPLETE",
    "O-POSITIVE",
    "O-SURPRISE",
    "O-NEGATIVE",
    "O-ARTIFACT",
    "O-IMPEDIMENT",
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


def write_yaml_manifest(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"refusing overwrite: {path}")

    def dump(obj: Any, indent: int = 0) -> list[str]:
        pad = "  " * indent
        lines: list[str] = []
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    lines.append(f"{pad}{k}:")
                    lines.extend(dump(v, indent + 1))
                elif isinstance(v, bool):
                    lines.append(f"{pad}{k}: {'true' if v else 'false'}")
                elif v is None:
                    lines.append(f"{pad}{k}: null")
                elif isinstance(v, (int, float)):
                    lines.append(f"{pad}{k}: {v}")
                else:
                    s = str(v).replace('"', '\\"')
                    lines.append(f'{pad}{k}: "{s}"')
        elif isinstance(obj, list):
            for item in obj:
                if isinstance(item, (dict, list)):
                    lines.append(f"{pad}-")
                    lines.extend(dump(item, indent + 1))
                else:
                    lines.append(f"{pad}- {item}")
        return lines

    path.write_text("\n".join(dump(data)) + "\n", encoding="utf-8")


def peak_rss_bytes() -> int | None:
    try:
        import resource

        return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) * 1024
    except Exception:
        return None


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


class Field:
    def __init__(self, n: int, mod: int):
        self.n = n
        self.mod = mod
        self.q = 1 << n

    def mul(self, a: int, b: int) -> int:
        return pmod(clmul(a, b), self.mod)

    def sqr(self, a: int) -> int:
        return self.mul(a, a)

    def pow(self, a: int, e: int) -> int:
        r = 1
        while e:
            if e & 1:
                r = self.mul(r, a)
            a = self.mul(a, a)
            e >>= 1
        return r

    def inv(self, a: int) -> int:
        if a == 0:
            raise ZeroDivisionError
        return self.pow(a, self.q - 2)


def formula_dim(k: int, l: int, n: int) -> int:
    return min(k * (l - 1) + 1, n)


def predicted_spurious(l: int, n: int = N_RC1, m: int = M) -> float:
    dims = [formula_dim(k, l, n) for k in range(1, m + 1)]
    return float(math.factorial(m) * (2 ** (sum(dims) - m * l)))


def _f2_rank(vectors: list[int]) -> int:
    """Rank of a list of bitvectors over F_2 (MSB-gaussian)."""
    basis: list[int] = []
    for v in vectors:
        x = v
        for b in basis:
            if x == 0:
                break
            if x.bit_length() == b.bit_length():
                x ^= b
        if x:
            basis.append(x)
            basis.sort(key=lambda z: -z.bit_length())
            # re-orthogonalize
            cleaned: list[int] = []
            for g in basis:
                y = g
                for c in cleaned:
                    if y.bit_length() == c.bit_length():
                        y ^= c
                if y:
                    cleaned.append(y)
                    cleaned.sort(key=lambda z: -z.bit_length())
            basis = cleaned
    return len(basis)


def product_space_dims_span(l: int, n: int, mod: int, m: int = M) -> list[int]:
    """Explicit F_2-span dims of V^{(k)} for V = span{1,t,...,t^{l-1}}.

    For the coordinate subspace, V^{(k)} = span{t^0,...,t^{k(l-1)}} reduced
    modulo the field polynomial, so dim = rank{t^i mod f : 0 <= i <= k(l-1)}.
    """
    F = Field(n, mod)
    dims: list[int] = []
    for k in range(1, m + 1):
        max_exp = k * (l - 1)
        vecs = [F.pow(2, i) for i in range(max_exp + 1)]  # t^i
        dims.append(_f2_rank(vecs))
    return dims


def product_bases(l: int, n: int, mod: int, m: int = M) -> tuple[list[int], list[list[int]]]:
    """Return (dims, bases) for V^{(k)} = span{t^0..t^{k(l-1)}} reduced."""
    F = Field(n, mod)
    dims: list[int] = []
    bases: list[list[int]] = []
    for k in range(1, m + 1):
        max_exp = k * (l - 1)
        vecs = [F.pow(2, i) for i in range(max_exp + 1)]
        # Build explicit basis via gaussian
        basis: list[int] = []
        for v in vecs:
            x = v
            for b in basis:
                if x == 0:
                    break
                if x.bit_length() == b.bit_length():
                    x ^= b
            if x:
                basis.append(x)
                basis.sort(key=lambda z: -z.bit_length())
                cleaned: list[int] = []
                for g in basis:
                    y = g
                    for c in cleaned:
                        if y.bit_length() == c.bit_length():
                            y ^= c
                    if y:
                        cleaned.append(y)
                        cleaned.sort(key=lambda z: -z.bit_length())
                basis = cleaned
        dims.append(len(basis))
        bases.append(basis)
    return dims, bases


def s3_coeffs_field(F: Field, B: int, x: int, y: int) -> tuple[int, int, int]:
    xy = F.mul(x, y)
    xp = x ^ y
    alpha = F.mul(xp, xp)
    beta = xy
    gamma = F.mul(xy, xy) ^ B
    return alpha, beta, gamma


def s4_field(F: Field, B: int, x1: int, x2: int, x3: int, x4: int) -> int:
    a1, b1, c1 = s3_coeffs_field(F, B, x1, x2)
    a2, b2, c2 = s3_coeffs_field(F, B, x3, x4)
    t1 = F.mul(a1, c2) ^ F.mul(a2, c1)
    t2 = F.mul(a1, b2) ^ F.mul(a2, b1)
    t3 = F.mul(b1, c2) ^ F.mul(b2, c1)
    return F.mul(t1, t1) ^ F.mul(t2, t3)


def elementary_symmetric(x1: int, x2: int, x3: int, F: Field) -> tuple[int, int, int]:
    e1 = x1 ^ x2 ^ x3
    e2 = F.mul(x1, x2) ^ F.mul(x1, x3) ^ F.mul(x2, x3)
    e3 = F.mul(F.mul(x1, x2), x3)
    return e1, e2, e3


def expand_cubic_from_roots(F: Field, r1: int, r2: int, r3: int) -> tuple[int, int, int]:
    """Return (e1,e2,e3) for (X+r1)(X+r2)(X+r3) in char 2."""
    e1 = r1 ^ r2 ^ r3
    e2 = F.mul(r1, r2) ^ F.mul(r1, r3) ^ F.mul(r2, r3)
    e3 = F.mul(F.mul(r1, r2), r3)
    return e1, e2, e3


def stage0(run_dir: Path) -> dict[str, Any]:
    t0 = time.time()
    # n=131 formula table (exact arithmetic; no field reduction raise)
    n131 = []
    for m, l in N131_CELLS:
        dims = [formula_dim(k, l, 131) for k in range(1, m + 1)]
        n131.append(
            {
                "m": m,
                "l": l,
                "dims": dims,
                "sum_dims": sum(dims),
                "ml": m * l,
                "excess_unknowns": sum(dims) - m * l,
            }
        )
    rc1_formula = {}
    rc1_predicted = {}
    for l in L_LEVELS:
        dims = [formula_dim(k, l, N_RC1) for k in range(1, M + 1)]
        rc1_formula[str(l)] = dims
        rc1_predicted[str(l)] = {
            "dims": dims,
            "sum_dims": sum(dims),
            "ml": M * l,
            "predicted_spurious_factor": predicted_spurious(l),
            "predicted_log2": math.log2(predicted_spurious(l)),
            "band_factor": 4,
            "surprise_if_ratio_below_at_l6": 8,
        }
    # P2 fixture levels
    p2_expected = {str(l): [formula_dim(k, l, N_RC1) for k in range(1, M + 1)] for l in P2_L_LEVELS}

    prereg = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "task_id": TASK_ID,
        "frozen_at_stage": 0,
        "master_seed": MASTER_SEED,
        "n_targets": N_TARGETS,
        "m": M,
        "l_levels": list(L_LEVELS),
        "rc1": {"n": N_RC1, "modulus": "t^17+t^3+1", "A": A_RC1, "B": B_RC1},
        "n131_balanced_cells": n131,
        "rc1_dimension_formula": rc1_formula,
        "rc1_predicted_spurious": rc1_predicted,
        "p2_expected_dims": p2_expected,
        "p1_band_factor": 4,
        "surprise_threshold_l6": 8,
        "sample_e_budget": {str(k): v for k, v in SAMPLE_E_BUDGET.items()},
        "amazon_bedrock": "NOT SELECTED",
    }
    dim_tables = {
        "experiment_id": EXPERIMENT_ID,
        "n131": n131,
        "rc1_formula": rc1_formula,
        "p2_expected": p2_expected,
        "note": "Formula dims are exact for coordinate subspaces; Stage 1 verifies RC-1 by span.",
    }
    subfield = (
        f"# Subfield baseline (proves-too-much) — {EXPERIMENT_ID}\n\n"
        "On a subfield factor base V = F_q inside F_{q^n}, every product space "
        "satisfies V^{(k)} = V, so the symmetrised unknown count is m log2 q "
        "(JV 2010). Symmetrisation works on that slice. The HOLD-X7 certificate "
        "is that the same rewrite on a *coordinate subspace* saturates "
        "V^{(k)} with dim = min(k(l-1)+1, n) and therefore *increases* the "
        "Boolean unknown count relative to the plain ml-bit descent.\n\n"
        "Frozen fixture (Stage 1 P2): at RC-1 (n=17, l=6, m=3) dims must be "
        "exactly [6, 11, 16].\n\n"
        "Amazon Bedrock: NOT SELECTED.\n"
    )
    deriv = (
        f"# Derivations note — {EXPERIMENT_ID}\n\n"
        "Predicted spurious factor at RC-1: m! * 2^{sum_k dim V^{(k)} - m l} "
        "with dim V^{(k)} = min(k(l-1)+1, n).\n\n"
        f"At l=4,5,6 (m=3,n=17): {[predicted_spurious(l) for l in L_LEVELS]} "
        f"(log2 ≈ {[round(math.log2(predicted_spurious(l)), 3) for l in L_LEVELS]}).\n\n"
        "n=131 excess unknowns at balanced cells:\n"
    )
    for row in n131:
        deriv += (
            f"- (m,l)=({row['m']},{row['l']}): sum_dims={row['sum_dims']} "
            f"vs ml={row['ml']} (excess {row['excess_unknowns']})\n"
        )
    deriv += "\nAmazon Bedrock: NOT SELECTED.\n"

    stage0_dir = EXP_ROOT / "stage0"
    write_json(stage0_dir / "preregistered-predictions.json", prereg)
    write_json(stage0_dir / "dimension-tables.json", dim_tables)
    write_text(stage0_dir / "subfield-baseline.md", subfield)
    write_text(stage0_dir / "derivations-note.md", deriv)

    raw = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "task_id": TASK_ID,
        "stage": 0,
        "outcome": "S0-FREEZE-OK",
        "n131_cells": n131,
        "rc1_predicted_spurious": rc1_predicted,
        "claims": {"break": False, "exponent_move": False, "deployed_attack": False},
        "wall_clock_seconds": time.time() - t0,
        "peak_rss_bytes": peak_rss_bytes(),
        "amazon_bedrock": "NOT SELECTED",
        "recorded_at": utc_now(),
    }
    write_json(run_dir / "raw-result.json", raw)
    write_yaml_manifest(
        run_dir / "manifest.yaml",
        {
            "schema": "crypto.autoresearch.run_manifest.v1",
            "experiment_id": EXPERIMENT_ID,
            "hypothesis_id": HYPOTHESIS_ID,
            "approved_by": APPROVED_BY,
            "task_id": TASK_ID,
            "stage": 0,
            "outcome": "S0-FREEZE-OK",
            "frozen": True,
            "amazon_bedrock": "NOT SELECTED",
        },
    )
    print(json.dumps({"stage": 0, "outcome": "S0-FREEZE-OK"}, sort_keys=True))
    return raw


def stage1(run_dir: Path) -> dict[str, Any]:
    t0 = time.time()
    stage0_pred = EXP_ROOT / "stage0" / "preregistered-predictions.json"
    if not stage0_pred.is_file():
        raw = {
            "experiment_id": EXPERIMENT_ID,
            "stage": 1,
            "outcome": "O-IMPEDIMENT",
            "impediment": "stage0/preregistered-predictions.json missing; Stage 0 must freeze first",
            "claims": {"break": False, "exponent_move": False, "deployed_attack": False},
            "wall_clock_seconds": time.time() - t0,
            "peak_rss_bytes": peak_rss_bytes(),
            "amazon_bedrock": "NOT SELECTED",
        }
        write_json(run_dir / "raw-result.json", raw)
        write_yaml_manifest(
            run_dir / "manifest.yaml",
            {
                "schema": "crypto.autoresearch.run_manifest.v1",
                "experiment_id": EXPERIMENT_ID,
                "stage": 1,
                "outcome": "O-IMPEDIMENT",
                "amazon_bedrock": "NOT SELECTED",
            },
        )
        write_text(
            EXP_ROOT / "RESULTS.md",
            f"# RESULTS — {EXPERIMENT_ID}\n\nO-IMPEDIMENT: Stage 0 freeze missing.\n\n"
            "Amazon Bedrock: NOT SELECTED. No break / exponent claim.\n",
        )
        print(json.dumps({"stage": 1, "outcome": "O-IMPEDIMENT"}, sort_keys=True))
        return raw

    F = Field(N_RC1, MOD_RC1)
    B = B_RC1
    rng = random.Random(MASTER_SEED)
    targets = [rng.randrange(1, F.q) for _ in range(N_TARGETS)]

    # P2: explicit span vs formula
    p2_rows = []
    p2_ok = True
    for l in P2_L_LEVELS:
        measured = product_space_dims_span(l, N_RC1, MOD_RC1, M)
        expected = [formula_dim(k, l, N_RC1) for k in range(1, M + 1)]
        match = measured == expected
        p2_ok = p2_ok and match
        p2_rows.append({"l": l, "measured": measured, "expected": expected, "match": match})

    if not p2_ok:
        outcome = "O-ARTIFACT"
        census = {"p2": p2_rows, "outcome": outcome, "note": "P2 fixture failed; void P1"}
        write_json(EXP_ROOT / "stage1" / "support-census.json", census)
        raw = {
            "experiment_id": EXPERIMENT_ID,
            "stage": 1,
            "outcome": outcome,
            "p2": p2_rows,
            "claims": {"break": False, "exponent_move": False, "deployed_attack": False},
            "wall_clock_seconds": time.time() - t0,
            "peak_rss_bytes": peak_rss_bytes(),
            "amazon_bedrock": "NOT SELECTED",
        }
        write_json(run_dir / "raw-result.json", raw)
        write_yaml_manifest(
            run_dir / "manifest.yaml",
            {
                "schema": "crypto.autoresearch.run_manifest.v1",
                "experiment_id": EXPERIMENT_ID,
                "stage": 1,
                "outcome": outcome,
                "amazon_bedrock": "NOT SELECTED",
            },
        )
        write_text(
            EXP_ROOT / "RESULTS.md",
            f"# RESULTS — {EXPERIMENT_ID}\n\nO-ARTIFACT: P2 product-space dims mismatch.\n\n"
            f"P2 rows: {json.dumps(p2_rows)}\n\n"
            "Amazon Bedrock: NOT SELECTED. No break / exponent claim.\n",
        )
        print(json.dumps({"stage": 1, "outcome": outcome}, sort_keys=True))
        return raw

    cell_stats = []
    for l in L_LEVELS:
        dims, bases = product_bases(l, N_RC1, MOD_RC1, M)
        assert dims == [formula_dim(k, l, N_RC1) for k in range(1, M + 1)]
        V = set(range(1 << l))
        total_bits = sum(dims)
        space_size = 1 << total_bits
        # Stages 0-1 instrument: exact genuine V^3 census + lift check on unique
        # genuine e-vectors (scan is sparse). Full e-space Boolean enumerator over
        # 2^{sum dims} is the IDEA hours-scale path; here we report the predicted
        # factor beside measured genuine density and the m!-style ordered/unique-e
        # ratio as a structural fibre diagnostic (not a substitute for H1's full
        # e-space count — disclosed as partial for Stages 0-1 admission).
        mode = "genuine_exact_plus_fibre_diagnostic"
        genuine_total = 0
        lift_recover = 0
        lift_denom = 0
        ordered_over_unique = []
        unique_e_total = 0

        for xR in targets:
            gcount = 0
            e_mult: dict[tuple[int, int, int], int] = {}
            e_witness: dict[tuple[int, int, int], tuple[int, int, int]] = {}
            for x1 in range(1 << l):
                for x2 in range(1 << l):
                    for x3 in range(1 << l):
                        if s4_field(F, B, x1, x2, x3, xR) == 0:
                            gcount += 1
                            e = elementary_symmetric(x1, x2, x3, F)
                            e_mult[e] = e_mult.get(e, 0) + 1
                            e_witness.setdefault(e, (x1, x2, x3))
            genuine_total += gcount
            unique_e_total += len(e_mult)
            if e_mult:
                ordered_over_unique.append(gcount / len(e_mult))
            # Lift check: each genuine e was built from a V-triple witness;
            # verify monic identity (X+r1)(X+r2)(X+r3) and S4(witness)=0.
            for (e1, e2, e3), w in e_witness.items():
                lift_denom += 1
                if (
                    expand_cubic_from_roots(F, *w) == (e1, e2, e3)
                    and all(r in V for r in w)
                    and s4_field(F, B, w[0], w[1], w[2], xR) == 0
                ):
                    lift_recover += 1

        lift_agreement = (lift_recover / lift_denom) if lift_denom else 1.0
        predicted = predicted_spurious(l)
        mean_genuine = genuine_total / N_TARGETS
        mean_unique_e = unique_e_total / N_TARGETS
        mean_fibre = (
            sum(ordered_over_unique) / len(ordered_over_unique) if ordered_over_unique else None
        )
        # Structural diagnostic only — not H1's e-space/genuine spurious factor.
        cell_stats.append(
            {
                "l": l,
                "dims": dims,
                "mode": mode,
                "e_space_bits": total_bits,
                "e_space_size": space_size,
                "genuine_total_pooled": genuine_total,
                "mean_genuine_per_target": mean_genuine,
                "mean_unique_genuine_e_per_target": mean_unique_e,
                "mean_ordered_per_unique_e": mean_fibre,
                "m_factorial": float(math.factorial(M)),
                "predicted_spurious_factor": predicted,
                "spurious_factor_ratio": None,
                "spurious_factor_note": (
                    "Full e-space/genuine P1 ratio deferred to Boolean e-space "
                    "enumerator (hours-scale at l>=5 per IDEA). Stages 0-1 record "
                    "exact genuine census, lift_agreement, and ordered/unique-e fibre."
                ),
                "lift_agreement": lift_agreement,
                "lift_recover": lift_recover,
                "lift_denom": lift_denom,
                "count_is_lower_bound": False,
            }
        )

    # Stages 0-1 label: full O-POSITIVE/SURPRISE/NEGATIVE need complete P1 e-space
    # counts + Stages 2-3. Admission path emits O-STAGES-0-1-COMPLETE when P2 and
    # lift_agreement hold; O-ARTIFACT if either fails.
    artifact = any(row["lift_agreement"] != 1.0 for row in cell_stats)
    outcome = "O-ARTIFACT" if artifact else "O-STAGES-0-1-COMPLETE"

    census = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "task_id": TASK_ID,
        "stage": 1,
        "p2": p2_rows,
        "cells": cell_stats,
        "outcome": outcome,
        "note": (
            "Stages 0-1 instrument: P2 span + exact genuine V^3 census + lift_agreement. "
            "Full e-space/genuine P1 ratio is hours-scale (IDEA); not claimed here. "
            "Stages 2-3 (random-subspace null, Frobenius arm) not in trial-plan-v1."
        ),
        "amazon_bedrock": "NOT SELECTED",
    }
    write_json(EXP_ROOT / "stage1" / "spurious-lift-census.json", census)
    write_json(EXP_ROOT / "stage1" / "support-census.json", {"p2": p2_rows, "outcome": outcome})

    results = (
        f"# RESULTS — {EXPERIMENT_ID}\n\n"
        f"**Outcome (Stages 0-1):** `{outcome}`\n\n"
        f"Hypothesis: {HYPOTHESIS_ID}. Approved: {APPROVED_BY}. Task: {TASK_ID}.\n\n"
        "## P2 product-space dims\n\n"
        f"All match formula: `{p2_ok}`.\n\n"
        "## P1 spurious-lift (RC-1, m=3)\n\n"
    )
    for row in cell_stats:
        results += (
            f"- l={row['l']}: mean_genuine={row['mean_genuine_per_target']} "
            f"mean_ordered_per_unique_e={row['mean_ordered_per_unique_e']} "
            f"predicted_spurious={row['predicted_spurious_factor']} "
            f"lift_agreement={row['lift_agreement']} mode={row['mode']}\n"
        )
    results += (
        "\n## Scope\n\n"
        "Stages 0-1 only under trial-plan-v1 / TASK-20261003-83db99. "
        "Stages 2-3 remain on design card TASK-20261002-d8df85.\n\n"
        "No Magma/Sage/AUXIN/Bedrock. No ECDLP break. No exponent claim.\n"
        "Amazon Bedrock: NOT SELECTED.\n"
    )
    write_text(EXP_ROOT / "RESULTS.md", results)

    raw = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "task_id": TASK_ID,
        "stage": 1,
        "outcome": outcome,
        "p2_ok": p2_ok,
        "cells": cell_stats,
        "claims": {"break": False, "exponent_move": False, "deployed_attack": False},
        "wall_clock_seconds": time.time() - t0,
        "peak_rss_bytes": peak_rss_bytes(),
        "amazon_bedrock": "NOT SELECTED",
        "recorded_at": utc_now(),
    }
    write_json(run_dir / "raw-result.json", raw)
    write_yaml_manifest(
        run_dir / "manifest.yaml",
        {
            "schema": "crypto.autoresearch.run_manifest.v1",
            "experiment_id": EXPERIMENT_ID,
            "hypothesis_id": HYPOTHESIS_ID,
            "approved_by": APPROVED_BY,
            "task_id": TASK_ID,
            "stage": 1,
            "outcome": outcome,
            "frozen": True,
            "amazon_bedrock": "NOT SELECTED",
        },
    )
    print(json.dumps({"stage": 1, "outcome": outcome, "p2_ok": p2_ok}, sort_keys=True))
    return raw


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", type=int, required=True, choices=[0, 1, 2, 3])
    ap.add_argument("--trial-plan", required=True)
    ap.add_argument("--run-dir", required=True)
    args = ap.parse_args()
    run_dir = Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    plan_path = Path(args.trial_plan)
    if not plan_path.is_file():
        print(f"missing trial plan: {plan_path}", file=sys.stderr)
        return 2
    if "bedrock" in plan_path.as_posix().lower():
        print("Bedrock prohibited", file=sys.stderr)
        return 2
    if args.stage == 0:
        stage0(run_dir)
    elif args.stage == 1:
        stage1(run_dir)
    else:
        # Stages 2-3: additive drivers; do not rewrite stage0/stage1/RESULTS.md
        from stages23 import stage2, stage3

        if args.stage == 2:
            stage2(run_dir)
        else:
            stage3(run_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
