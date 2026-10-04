#!/usr/bin/env python3
"""EXP-SEMBIN-04ec3c -- charge the decomposition oracle's MEMORY, symmetrically
with the rho baseline, across every summand count and store budget.

Implements the cost model exactly as frozen in
experiments/EXP-SEMBIN-04ec3c/specification.yaml. No cost model is invented
here; the contract's `cost_model` block is the specification and this file is
its transcription.

Deterministic, seedless, standard library only. Every quantity is an integer
parameter sweep in log2 space.

THE COMPARISON, in one line: rho's total WORK is invariant along its own
time-memory curve, so a store buys the baseline wall-clock parallelism but never
fewer operations; the index-calculus side's store buys operations directly. That
asymmetry is why charging the oracle's memory is a fair comparison rather than a
punitive one, and it is why this sweep exists.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass, asdict

# --------------------------------------------------------------------------
# curve degrees, read from frozen sources (see the contract's procedure block)
# --------------------------------------------------------------------------
# Certicom binary challenge degrees, from the level-1 and level-2 tables in
# inputs/BAILEY-2009-541-ECC2K130/talk-35minutes_text.md. The "Bits" column is
# the field extension degree, checkable because ECC2K-130 appears at 131.
# NOTE the 359-bit level-2 entry is ECCp-359, a PRIME-field curve, so there is
# no binary Certicom challenge at 359 and none is listed.
CERTICOM_BINARY = [97, 109, 131, 163, 191, 239]
# FIPS binary degrees, from the "Curve K-163" .. "Curve K-571" headings in
# inputs/SAFECURVES-20260825/specs/sp800-186.txt; the B- family shares each.
FIPS_BINARY = [163, 233, 283, 409, 571]
ALL_DEGREES = sorted(set(CERTICOM_BINARY) | set(FIPS_BINARY))

# ECC2K-130 specifics. #E = 4r with r the 129-bit prime below, so the prime
# subgroup order is 2^128.9993..., NOT 2^131. Using #E would overstate rho.
ECC2K130_R = 680564733841876926932320129493409985129
ECC2K130_LOG2_R = math.log2(ECC2K130_R)
# Published rho reference for ECC2K-130, including the <-1> x <pi> speedup.
ECC2K130_RHO_PUBLISHED = 60.8090
# vOW total work constant, H-SEMBIN-97ea23 / HEUR-VOW-CURVE (unvalidated).
VOW_WORK_CONST_BITS = math.log2(0.886)

OMEGA_LINALG = 2.0  # sparse Wiedemann: |F|^2 operations


def log2_factorial(m: int) -> float:
    return math.lgamma(m + 1) / math.log(2.0)


def subgroup_log2(n: int) -> float:
    """log2 of the prime subgroup order used for the yield term.

    For ECC2K-130 the real value is used. For every other degree the contract
    does not name a cofactor, so n is used and the choice is REPORTED rather
    than hidden: a cofactor of 2 or 4 shifts the yield term by 1 or 2 bits and
    changes no sign anywhere in this sweep.
    """
    if n == 131:
        return ECC2K130_LOG2_R
    return float(n)


# --------------------------------------------------------------------------
# oracle models, exactly as the contract's cost_model.oracle_models lists them
# --------------------------------------------------------------------------
def oracle_log2(model: str, m: int, d: float, budget_log2_entries: float | None):
    """(time exponent, store exponent) for one decomposition attempt, in log2.

    d is the factor-base dimension, so |F| = 2^d.
    Returns (time_bits, store_bits, s) where s is the number of summands
    tabulated (0 where the notion does not apply).
    """
    if model == "FREE":
        return 0.0, 0.0, 0
    if model == "ENUM":
        # fix m-1 summands, test membership of the remainder
        return (m - 1) * d, 0.0, 0
    if model == "MITM":
        # tabulate sums of floor(m/2), probe with the complement
        s = m // 2
        return math.ceil(m / 2) * d, s * d, s
    if model == "MITM_CAPPED":
        if budget_log2_entries is None:
            s = m // 2
        else:
            s_max = 0 if d <= 0 else int(budget_log2_entries // d)
            s = min(m // 2, max(0, s_max))
        return (m - s) * d, s * d, s
    raise ValueError(f"unknown oracle model {model!r}")


@dataclass
class Cell:
    n: int
    m: int
    model: str
    budget_log2_entries: float | None
    d: float
    log2_relation_phase: float
    log2_linalg: float
    log2_total: float
    log2_store_entries: float
    s_tabulated: int
    log2_rho_vow: float
    log2_rho_published: float | None
    margin_vs_vow_bits: float
    margin_vs_published_bits: float | None
    beats_vow: bool
    beats_published: bool | None
    degenerate: bool
    degenerate_reason: str | None
    at_d_bound: bool


def cost_at(n: int, m: int, model: str, d: float,
            budget_log2_entries: float | None) -> Cell:
    nn = subgroup_log2(n)
    oracle_t, oracle_store, s = oracle_log2(model, m, d, budget_log2_entries)
    # relations needed 2^d; trials per relation m! * N / |F|^m; oracle per trial
    relation = d + log2_factorial(m) + (nn - m * d) + oracle_t
    linalg = OMEGA_LINALG * d
    total = relation if relation - linalg > 60 else (
        linalg if linalg - relation > 60
        else max(relation, linalg) + math.log2(1.0 + 2.0 ** -abs(relation - linalg)))
    # the store is the larger of the oracle table and the sparse matrix
    store = max(oracle_store, d + math.log2(max(m, 1)))
    rho_vow = nn / 2.0 + VOW_WORK_CONST_BITS
    rho_pub = ECC2K130_RHO_PUBLISHED if n == 131 else None
    k = nn / m if m else 0.0
    degenerate = (k < 2.0) or (m > n) or (d < 1.0)
    reason = None
    if k < 2.0:
        reason = f"k = n/m = {k:.2f} < 2: not a factor base"
    elif m > n:
        reason = f"m = {m} exceeds n = {n}"
    elif d < 1.0:
        reason = f"d = {d:.2f} < 1"
    return Cell(
        n=n, m=m, model=model, budget_log2_entries=budget_log2_entries,
        d=round(d, 4),
        log2_relation_phase=round(relation, 4),
        log2_linalg=round(linalg, 4),
        log2_total=round(total, 4),
        log2_store_entries=round(store, 4),
        s_tabulated=s,
        log2_rho_vow=round(rho_vow, 4),
        log2_rho_published=rho_pub,
        margin_vs_vow_bits=round(total - rho_vow, 4),
        margin_vs_published_bits=(None if rho_pub is None
                                  else round(total - rho_pub, 4)),
        beats_vow=bool(total < rho_vow),
        beats_published=(None if rho_pub is None else bool(total < rho_pub)),
        degenerate=degenerate, degenerate_reason=reason,
        at_d_bound=False,
    )


def minimise_over_d(n: int, m: int, model: str,
                    budget_log2_entries: float | None,
                    d_lo: float = 1.0, d_hi: float | None = None,
                    step: float = 0.25) -> Cell:
    """Grid-minimise total cost over the factor-base dimension."""
    if d_hi is None:
        d_hi = float(n)
    best: Cell | None = None
    d = d_lo
    while d <= d_hi + 1e-9:
        c = cost_at(n, m, model, d, budget_log2_entries)
        if best is None or c.log2_total < best.log2_total:
            best = c
        d += step
    assert best is not None
    best.at_d_bound = (abs(best.d - d_lo) < step or abs(best.d - d_hi) < step)
    return best


def min_store_for_subrho(n: int, m: int, baseline: str = "vow",
                         d_step: float = 0.05) -> dict:
    """Smallest store admitting a sub-baseline cell at this (n, m) under MITM.

    Sweeps d upward and reports the first d whose MITM total falls below the
    baseline, with the store that d then requires. Returns store None when no d
    in range reaches it.
    """
    nn = subgroup_log2(n)
    target = (nn / 2.0 + VOW_WORK_CONST_BITS) if baseline == "vow" \
        else (ECC2K130_RHO_PUBLISHED if n == 131 else nn / 2.0 + VOW_WORK_CONST_BITS)
    d = 1.0
    while d <= float(n) + 1e-9:
        c = cost_at(n, m, "MITM", d, None)
        if c.log2_total < target and not c.degenerate:
            return {"n": n, "m": m, "baseline": baseline,
                    "reachable": True,
                    "d": round(d, 4),
                    "log2_total": c.log2_total,
                    "log2_store_entries": c.log2_store_entries,
                    "store_exceeds_baseline_work_by_bits":
                        round(c.log2_store_entries - target, 4),
                    "target": round(target, 4)}
        d += d_step
    return {"n": n, "m": m, "baseline": baseline, "reachable": False,
            "target": round(target, 4),
            "note": "no factor-base dimension in [1, n] reaches the baseline"}


# --------------------------------------------------------------------------
# controls
# --------------------------------------------------------------------------
COMMITTED_FLOOR = {2: 89.25, 3: 68.58, 4: 56.40, 5: 48.44, 6: 42.85, 8: 35.61}


def control_floor_repro(tolerance_bits: float) -> dict:
    """C-FLOOR-REPRO. Structural agreement with the committed floor table.

    The committed table's exact constants convention is NOT recoverable from the
    records that publish it (see the contract). So the gate is STRUCTURAL --
    ordering, strict monotone decrease, and the sign of every margin against the
    published rho reference -- and the absolute offsets are reported as a
    diagnostic rather than used as a gate. A tolerance widened to fit what was
    just measured has stopped being a check, which is why absolute agreement is
    not the criterion.
    """
    rows = []
    for m in sorted(COMMITTED_FLOOR):
        c = minimise_over_d(131, m, "FREE", None)
        rows.append({
            "m": m,
            "committed_log2": COMMITTED_FLOOR[m],
            "recomputed_log2": c.log2_total,
            "offset_bits": round(c.log2_total - COMMITTED_FLOOR[m], 4),
            "d_star": c.d,
            "committed_beats_published_rho":
                COMMITTED_FLOOR[m] < ECC2K130_RHO_PUBLISHED,
            "recomputed_beats_published_rho": c.beats_published,
            "sign_agrees": (COMMITTED_FLOOR[m] < ECC2K130_RHO_PUBLISHED)
                           == bool(c.beats_published),
        })
    committed_desc = all(rows[i]["committed_log2"] > rows[i + 1]["committed_log2"]
                         for i in range(len(rows) - 1))
    recomputed_desc = all(rows[i]["recomputed_log2"] > rows[i + 1]["recomputed_log2"]
                          for i in range(len(rows) - 1))
    signs_agree = all(r["sign_agrees"] for r in rows)
    offsets = [abs(r["offset_bits"]) for r in rows]
    return {
        "rows": rows,
        "committed_strictly_decreasing_in_m": committed_desc,
        "recomputed_strictly_decreasing_in_m": recomputed_desc,
        "all_margin_signs_agree": signs_agree,
        "m3_above_published_rho_both": (
            COMMITTED_FLOOR[3] > ECC2K130_RHO_PUBLISHED
            and not bool(rows[1]["recomputed_beats_published_rho"])),
        "m4_below_published_rho_both": (
            COMMITTED_FLOOR[4] < ECC2K130_RHO_PUBLISHED
            and bool(rows[2]["recomputed_beats_published_rho"])),
        "max_abs_offset_bits": round(max(offsets), 4),
        "offset_grows_with_m": all(offsets[i] <= offsets[i + 1] + 1e-9
                                   for i in range(len(offsets) - 1)),
        "absolute_agreement_within_tolerance": max(offsets) <= tolerance_bits,
        "absolute_agreement_is_not_the_gate": True,
        "passed": bool(committed_desc and recomputed_desc and signs_agree),
        "pass_criterion": (
            "STRUCTURAL: both tables strictly decreasing in m, every margin sign "
            "against the published rho reference agreeing, m=3 above and m=4 "
            "below. Absolute offsets reported, not gated."),
    }


def control_m3_anchor() -> dict:
    """C-M3-ANCHOR. The measured anchor: d-independence at m=3, base 2^132.58."""
    out = {}
    for model in ("ENUM", "MITM"):
        totals = [cost_at(131, 3, model, d, None).log2_total
                  for d in range(10, 61, 2)]
        spread = max(totals) - min(totals)
        out[model] = {
            "d_range": [10, 60],
            "log2_total_min": round(min(totals), 4),
            "log2_total_max": round(max(totals), 4),
            "spread_bits": round(spread, 4),
            "d_independent_within_1_bit": spread < 1.0,
            "measured_implicit_base": 132.58,
            "offset_from_measured_bits": round(min(totals) - 132.58, 4),
            "within_5_bits_of_measured": abs(min(totals) - 132.58) <= 5.0,
        }
    out["passed"] = bool(
        out["ENUM"]["d_independent_within_1_bit"]
        and out["MITM"]["d_independent_within_1_bit"]
        and out["ENUM"]["within_5_bits_of_measured"])
    out["why_this_is_the_stronger_control"] = (
        "It checks against a MEASURED quantity rather than another derivation. "
        "If the derivation does not reproduce d-independence at m=3 the oracle "
        "exponent is wrong and every larger-m row inherits the error.")
    return out


def control_null_no_memory_charge(budgets: list[float]) -> dict:
    """C-NULL-NO-MEMORY-CHARGE. Null object: store charged at zero.

    With the store free, MITM_CAPPED collapses to MITM at every budget. If the
    set of sub-rho cells is the SAME with and without the charge, the charge is
    buying nothing and this contract's premise is refuted.
    """
    charged, uncharged = set(), set()
    for n in ALL_DEGREES:
        for m in range(2, 17):
            for b in budgets:
                c = minimise_over_d(n, m, "MITM_CAPPED", b)
                if c.beats_vow and not c.degenerate:
                    charged.add((n, m, b))
                u = minimise_over_d(n, m, "MITM", None)
                if u.beats_vow and not u.degenerate:
                    uncharged.add((n, m, b))
    return {
        "subrho_cells_charged": len(charged),
        "subrho_cells_store_free": len(uncharged),
        "sets_identical": charged == uncharged,
        "cells_the_charge_removes": len(uncharged - charged),
        "discriminates": charged != uncharged,
        "verdict": ("CHARGE DISCRIMINATES: the memory charge removes sub-rho "
                    "cells the store-free reading admits"
                    if charged != uncharged else
                    "PREMISE REFUTED: identical cell sets, so the memory charge "
                    "buys nothing and this result is about the product law alone"),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--floor-tolerance-bits", type=float, default=8.0)
    ap.add_argument("--m-max", type=int, default=16)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    budgets = [30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0]

    controls = {
        "C-FLOOR-REPRO": control_floor_repro(args.floor_tolerance_bits),
        "C-M3-ANCHOR": control_m3_anchor(),
        "C-NULL-NO-MEMORY-CHARGE": control_null_no_memory_charge(budgets),
    }

    # P1: ENUM is d- and m-independent
    enum_probe = []
    for m in range(2, args.m_max + 1):
        totals = [cost_at(131, m, "ENUM", d, None).log2_total
                  for d in range(5, 61, 5)]
        enum_probe.append({"m": m, "spread_over_d_bits": round(max(totals) - min(totals), 6),
                           "log2_total": round(totals[0], 4),
                           "beats_published_rho": totals[0] < ECC2K130_RHO_PUBLISHED})

    # MITM with store free, per m, at every degree
    mitm_free = []
    for n in ALL_DEGREES:
        for m in range(2, args.m_max + 1):
            c = minimise_over_d(n, m, "MITM", None)
            mitm_free.append(asdict(c))

    # MITM_CAPPED sweep over budgets
    capped = []
    for n in ALL_DEGREES:
        for m in range(2, args.m_max + 1):
            for b in budgets:
                c = minimise_over_d(n, m, "MITM_CAPPED", b)
                capped.append(asdict(c))

    # minimum store admitting a sub-rho cell, per (n, m)
    min_store = []
    for n in ALL_DEGREES:
        for m in range(2, args.m_max + 1):
            min_store.append(min_store_for_subrho(n, m, "vow"))

    reachable = [r for r in min_store if r.get("reachable")]
    by_degree = {}
    for n in ALL_DEGREES:
        rows = [r for r in reachable if r["n"] == n]
        if rows:
            best = min(rows, key=lambda r: r["log2_store_entries"])
            by_degree[n] = {
                "m_minimising_store": best["m"],
                "min_log2_store_entries": best["log2_store_entries"],
                "at_that_cell_log2_total": best["log2_total"],
                "baseline": best["target"],
                "store_exceeds_baseline_work_by_bits":
                    best["store_exceeds_baseline_work_by_bits"],
            }

    subrho_capped = [c for c in capped
                     if c["beats_vow"] and not c["degenerate"]]
    subrho_at_or_below_2_80 = [c for c in subrho_capped
                               if c["budget_log2_entries"] is not None
                               and c["budget_log2_entries"] <= 80.0]

    result = {
        "experiment_id": "EXP-SEMBIN-04ec3c",
        "hypothesis_id": "H-SEMBIN-8e7ae3",
        "what_this_is": (
            "Arithmetic on a cost model, sweeping the oracle store the existing "
            "floor table left free. Not a measurement, not an algorithm, not an "
            "attack, and not a statement about the security of any curve."),
        "degrees": {"certicom_binary": CERTICOM_BINARY,
                    "fips_binary": FIPS_BINARY,
                    "note_359": ("the 359-bit level-2 Certicom challenge is "
                                 "ECCp-359, a PRIME-field curve; there is no "
                                 "binary challenge at 359")},
        "controls": controls,
        "P1_enum_probe": enum_probe,
        "mitm_store_free": mitm_free,
        "mitm_capped": capped,
        "min_store_for_subrho": min_store,
        "min_store_by_degree": by_degree,
        "P5_subrho_cells_at_budget_le_2_80": subrho_at_or_below_2_80,
        "summary": {
            "enum_beats_rho_anywhere": any(e["beats_published_rho"] for e in enum_probe),
            "enum_d_independent_everywhere": all(e["spread_over_d_bits"] < 1e-6
                                                 for e in enum_probe),
            "mitm_store_free_first_m_below_published_rho_at_131": next(
                (c["m"] for c in sorted(
                    [c for c in mitm_free
                     if c["n"] == 131 and c["beats_published"]
                     and not c["degenerate"]],
                    key=lambda c: c["m"])), None),
            "any_subrho_cell_at_budget_le_2_80": len(subrho_at_or_below_2_80) > 0,
            "ecc2k130_min_store": by_degree.get(131),
        },
        "inherited_assumptions": [
            "HEUR-GENERIC-MSUM (unvalidated) -- m-SUM over this group admits no "
            "better generic time-store tradeoff than partial meet-in-the-middle. "
            "THIS CARRIES THE WHOLE RESULT. A sub-generic oracle voids every row.",
            "HEUR-VOW-CURVE (unvalidated) for the vOW baseline column.",
            "Sparse linear algebra at |F|^2 time.",
            "Semaev's Assumption 1 is NOT inherited: no degree bound enters any "
            "model here, deliberately.",
        ],
    }
    text = json.dumps(result, indent=1)
    if args.out:
        with open(args.out, "w") as fh:
            fh.write(text + "\n")
    else:
        sys.stdout.write(text + "\n")


if __name__ == "__main__":
    main()
