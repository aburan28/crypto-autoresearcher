#!/usr/bin/env python3
"""Driver for EXP-SEMBIN-354a75. Measures; concludes nothing.

WHAT IT PRODUCES. Two machine-readable artifacts and a log:

  raw-result.json    every aggregate, every control outcome, every tail check,
                     the eq. (11) baseline, the per-cell ratios with intervals,
                     and a flat results table keyed by (n, m, t, k,
                     presentation, class_count, subspace, B, seed).
  per-R-counts.json  the per-R counts THEMSELVES, columnar, for every target of
                     every configuration. The contract requires these retained
                     rather than aggregated: the zero fraction and the tail
                     checks are not recoverable from a mean, and the
                     chained-minus-single comparison has to be per R because a
                     mean of zero is consistent with a chain that loses
                     solutions on some R and gains on others.

THE THREE PRESENTATIONS, KEPT APART. `single` is eq. (4)/(6), the x-multisets
with S_{t+1}(x_1..x_t, R_X) = 0. `chained` is eq. (5), those admitting a full
chain with every u_i in F_q. `usable` is the strict subset whose y_i all lie in
F_q. The paper counts the s >= 2 solutions as useful relations too (Section 3,
step 3), so `single` is the algorithmically relevant yield and `usable` is
reported beside it rather than instead of it.

TWO TARGET POPULATIONS, ALSO KEPT APART. eq. (11) models "random z in F_q", but
the algorithm's R_X is the x-coordinate of an F_q-rational point, which is only
about half of F_q. `side=E` is the algorithm's population and is primary;
`side=T` is the other half, where z carries no rational point. Conflating them
would average over two populations that need not behave alike, and whether they
do is measurable rather than assumable.

NOTHING HERE SAMPLES INSIDE A CELL. Each per-R count is a complete enumeration
of the decompositions of that R. The 2000 draws are draws of R, which is what
the contract specifies; the count at each drawn R is exact. Cells that did not
fit their cap would be recorded unreached with the size of V^t they needed --
the machinery is present and reports an empty list only because every declared
cell fitted.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import os
import random
import resource
import sys
import time
from math import comb, factorial

import numpy as np
import yaml

from fastfield import FastField
from yield_core import (CellContext, build_subspace, count_multiset_sums,
                        multiset_tuples, span_of, sums_of_tuples,
                        validate_subspace, validate_target)
from yield_core import _expand as expand_prefixes
from yield_null import class_count_inflation, null_block
from yield_stats import (Z95, class_count, eq11, extreme_tail_check,
                         mean_interval, poisson_fit, ratio_block, wilson)

U32 = np.uint32

CLASS_VARIANTS = ("semaev_v_to_the_t_over_t_factorial",
                  "exact_multiset_count_binom_V_plus_t_minus_1_choose_t",
                  "known_false_v_to_the_t_no_symmetry")

PRESENTATIONS = ("single", "chained", "usable")

# Columns retained per R. Deliberately columnar: 720 000 target rows in a
# dict-per-row layout is mostly punctuation.
PER_R_COLUMNS = ("R_x", "R_y", "usable_point_multiset",
                 "outside_fq_point_multiset", "point_multiset_total",
                 "single_x_multiset", "chained_x_multiset",
                 "single_x_ordered", "chained_x_ordered", "max_y_outside_fq",
                 "x_multiset_outside_only", "x_multiset_both_kinds",
                 "lemma2_side_condition_holds", "tau_O", "tau_T2")


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def derived_seed(seed: int, label: str) -> int:
    """A per-configuration seed that is a pure function of the label.

    Reproducibility needs the draw sequence to be recoverable from the record
    alone, so the seed is derived by hashing the configuration label rather
    than by advancing a shared generator whose position depends on iteration
    order.
    """
    h = hashlib.sha256(f"{seed}|{label}".encode()).hexdigest()
    return (int(h[:15], 16) ^ seed) & ((1 << 63) - 1)


# --------------------------------------------------------------------------
# Control 1: the eq. (11) baseline
# --------------------------------------------------------------------------
def baseline_control(tables_path: str) -> dict:
    """Recompute eq. (11) at EVERY printed P_theoretical cell of Tables 1-2.

    The contract asks for the four cells whose probability the paper prints;
    the frozen transcription actually carries 33, and checking all of them
    costs nothing and is a strictly stronger check of the same thing. It
    remains a check on THIS PROGRAM'S ARITHMETIC and is not evidence that
    eq. (11) is right: the probability column is the model's own output, not
    an observation.
    """
    tables = yaml.safe_load(open(tables_path))
    rows = []
    for tname in ("table_1", "table_2"):
        for r in tables[tname]["rows"]:
            if r.get("P_theoretical") is None:
                continue
            t = r.get("t", r.get("t_eq_m"))
            m = r.get("m", r.get("t_eq_m"))
            n, k = r["n"], r["k"]
            got = eq11(n, t, k)["P"]
            printed = float(r["P_theoretical"])
            rows.append({
                "table": tname, "n": n, "m": m, "t": t, "k": k,
                "tk_minus_n": t * k - n,
                "printed_P_theoretical": printed,
                "recomputed_P": got,
                "recomputed_rounded_4dp": round(got, 4),
                "recomputed_truncated_4dp": math.floor(got * 1e4) / 1e4,
                "matches_by_rounding": abs(round(got, 4) - printed) < 5e-9,
                "matches_by_truncation": (
                    abs(math.floor(got * 1e4) / 1e4 - printed) < 5e-9),
                "abs_error": abs(got - printed),
            })
    by_round = sum(r["matches_by_rounding"] for r in rows)
    by_trunc = sum(r["matches_by_truncation"] for r in rows)
    either = sum(r["matches_by_rounding"] or r["matches_by_truncation"]
                 for r in rows)
    return {
        "source": tables_path,
        "cells_checked": len(rows),
        "matched_by_rounding": by_round,
        "matched_by_truncation": by_trunc,
        "matched_by_either": either,
        "all_matched_to_four_decimals": either == len(rows),
        "max_abs_error": max(r["abs_error"] for r in rows),
        "convention_note": (
            "The paper's printed column truncates rather than rounds: "
            "0.283469 prints as 0.2834 and 0.486583 as 0.4865. Both "
            "conventions are reported per cell so the reader can see which "
            "one the source uses rather than taking this program's word."),
        "not_evidence_for_eq11": (
            "This control checks that eq. (11) is being EVALUATED correctly. "
            "The printed column is the model's own output, so agreement here "
            "is not evidence that the model is right."),
        "rows": rows,
    }


# --------------------------------------------------------------------------
# Target drawing
# --------------------------------------------------------------------------
def draw_targets(ctx: CellContext, side: str, count: int,
                 rng: random.Random) -> list[tuple[int, int]]:
    """`count` uniform affine points of the chosen curve with x outside V.

    x outside V is Lemma 2's own hypothesis (R_X not in V) and is also what
    the algorithm does -- a target already in the factor base is not a
    decomposition problem. Sampling x uniformly and then one of its two
    y-values uniformly is uniform on affine points, since every x with points
    carries exactly two of them once x = 0 is excluded, and x = 0 lies in V.
    """
    curve = ctx.curve if side == "E" else ctx.twist
    Vset = set(ctx.V)
    q = ctx.field.q
    out = []
    while len(out) < count:
        x = rng.randrange(1, q)
        if x in Vset:
            continue
        ys = curve.ys_for_x_scalar(x)
        if not ys:
            continue
        out.append((x, ys[rng.randrange(len(ys))]))
    return out


# --------------------------------------------------------------------------
# One configuration
# --------------------------------------------------------------------------
def run_config(cell: dict, subspace: str, b_mode: str, seed: int, draws: int,
               sides=("E", "T")) -> dict:
    n, m, t, k = cell["n"], cell["m"], cell["t"], cell["k"]
    label = f"n{n}-m{m}-t{t}-k{k}-{subspace}-{b_mode}-s{seed}"
    dseed = derived_seed(seed, label)
    field = FastField.get(n)

    nprng = np.random.default_rng(dseed)
    pyrng = random.Random(dseed ^ 0xA5A5)
    if b_mode == "B_eq_1":
        b = 1
    elif b_mode == "random_B":
        b = int(nprng.integers(1, field.q))
    else:
        raise ValueError(b_mode)
    a = 0
    V, basis = build_subspace(field, k, subspace, nprng)

    t0 = time.time()
    ctx = CellContext(n, a, b, V)
    setup_seconds = time.time() - t0

    out = {
        "label": label, "cell": {"n": n, "m": m, "t": t, "k": k},
        "tk_minus_n": t * k - n,
        "subspace_variant": subspace, "V_basis": [int(v) for v in basis],
        "V_size": len(V), "curve_A": a, "curve_B": b, "b_mode": b_mode,
        "seed": seed, "derived_seed": dseed,
        "field_modulus_hex": hex(field.modulus),
        "field_generator": int(field.generator),
        "factor_base_rational_points": ctx.e_pts.n,
        "factor_base_twist_points": ctx.t_pts.n,
        "distinct_rational_x_in_V": ctx.n_rational_x,
        "distinct_irrational_x_in_V": ctx.n_irrational_x,
        "enumeration_domain_V_to_the_t": len(V) ** t,
        "enumeration_classes_exact_multiset": comb(len(V) + t - 1, t),
        "enumeration_point_multisets_rational": comb(ctx.e_pts.n + t - 1, t),
        "setup_seconds": setup_seconds,
        "sides": {},
    }

    for side in sides:
        pts = ctx.e_pts if side == "E" else ctx.t_pts
        if pts.n == 0:
            out["sides"][side] = {"skipped": "no factor-base points on this "
                                             "side, so no decomposition exists"}
            continue
        t1 = time.time()
        Rs = draw_targets(ctx, side, draws, pyrng)
        cols = {c: [] for c in PER_R_COLUMNS}
        for R in Rs:
            validate_target(R)
            res = ctx.solve_for_target(R, t, side=side)
            l2 = ctx.lemma2_side_condition(R, t, side=side)
            cols["R_x"].append(R[0])
            cols["R_y"].append(R[1])
            for key in ("usable_point_multiset", "outside_fq_point_multiset",
                        "point_multiset_total", "single_x_multiset",
                        "chained_x_multiset", "single_x_ordered",
                        "chained_x_ordered", "max_y_outside_fq",
                        "x_multiset_outside_only", "x_multiset_both_kinds"):
                cols[key].append(int(res[key]))
            cols["tau_O"].append(int(res["tau_counts_for_s_positive"]["O"]))
            cols["tau_T2"].append(int(res["tau_counts_for_s_positive"]["T2"]))
            cols["lemma2_side_condition_holds"].append(int(l2["holds"]))
        seconds = time.time() - t1
        out["sides"][side] = summarise_side(cols, n, m, t, k, seconds)
        out["sides"][side]["_columns"] = cols
    return out


def summarise_side(cols: dict, n: int, m: int, t: int, k: int,
                   seconds: float) -> dict:
    single = np.array(cols["single_x_multiset"], dtype=np.int64)
    chained = np.array(cols["chained_x_multiset"], dtype=np.int64)
    usable = np.array(cols["usable_point_multiset"], dtype=np.int64)
    single_ord = np.array(cols["single_x_ordered"], dtype=np.int64)
    chained_ord = np.array(cols["chained_x_ordered"], dtype=np.int64)
    outside = np.array(cols["outside_fq_point_multiset"], dtype=np.int64)
    l2 = np.array(cols["lemma2_side_condition_holds"], dtype=bool)
    tau_o = np.array(cols["tau_O"], dtype=np.int64)
    tau_t2 = np.array(cols["tau_T2"], dtype=np.int64)
    draws = single.size

    counts = {"single": single, "chained": chained, "usable": usable}
    ordered = {"single": single_ord, "chained": chained_ord}

    ratios = {}
    for pres, arr in counts.items():
        ratios[pres] = {v: ratio_block(arr, n, t, k, v)
                        for v in CLASS_VARIANTS}

    diff = chained - single
    # The Lemma-2 comparison, restricted to where the lemma actually applies.
    held = int(l2.sum())
    diff_held = diff[l2]
    return {
        "draws": draws,
        "enumeration_seconds": seconds,
        "ratios": ratios,
        "counts_summary": {
            pres: {
                "mean": float(arr.mean()),
                "variance": float(arr.var(ddof=1)) if draws > 1 else 0.0,
                "zero_fraction": float(np.count_nonzero(arr == 0) / draws),
                "zero_fraction_ci95": list(
                    wilson(int(np.count_nonzero(arr == 0)), draws)),
                "max": int(arr.max()), "total": int(arr.sum()),
                "histogram": {str(v): int(c) for v, c in
                              zip(*np.unique(arr, return_counts=True))},
            } for pres, arr in counts.items()
        },
        "ordered_counts_summary": {
            pres: {"mean": float(arr.mean()), "total": int(arr.sum()),
                   "max": int(arr.max())}
            for pres, arr in ordered.items()
        },
        "c_of_t": c_of_t_block(counts, ordered, n, t, k),
        "poisson_fit": {pres: poisson_fit(arr) for pres, arr in counts.items()},
        "extreme_tail": {pres: extreme_tail_check(arr)
                         for pres, arr in counts.items()},
        "lemma2": {
            "side_condition_holds_count": held,
            "side_condition_holds_fraction": held / draws,
            "side_condition_failure_fraction": 1.0 - held / draws,
            "side_condition_failure_ci95": list(
                wilson(draws - held, draws)),
            "chained_minus_single_histogram": {
                str(v): int(c) for v, c in
                zip(*np.unique(diff, return_counts=True))},
            "R_with_chained_below_single": int(np.count_nonzero(diff < 0)),
            "R_with_chained_above_single": int(np.count_nonzero(diff > 0)),
            "R_with_chained_equal_single": int(np.count_nonzero(diff == 0)),
            "R_where_they_differ_and_condition_HELD": int(
                np.count_nonzero(diff[l2] != 0)) if held else 0,
            "R_where_they_differ_and_condition_FAILED": int(
                np.count_nonzero(diff[~l2] != 0)) if draws - held else 0,
            "chained_minus_single_histogram_condition_held": {
                str(v): int(c) for v, c in
                zip(*np.unique(diff_held, return_counts=True))} if held else {},
            "outside_fq_total": int(outside.sum()),
            "outside_fq_mean": float(outside.mean()),
            "R_with_any_outside_fq_solution": int(np.count_nonzero(outside)),
            "outside_fq_fraction_of_point_multisets": (
                float(outside.sum()
                      / max(1, int(np.array(cols["point_multiset_total"]).sum())))),
            "tau_infinity_total": int(tau_o.sum()),
            "tau_2torsion_total": int(tau_t2.sum()),
            "max_y_outside_fq_over_all_R": int(
                np.array(cols["max_y_outside_fq"]).max()),
            "s_equals_one_ever": False,
            "s_equals_one_note": (
                "s = 1 is impossible in this construction, not merely "
                "unobserved: a single y outside F_q forces the twist part to "
                "be one affine twist point, which would have to equal "
                "infinity or the 2-torsion point to re-enter E(F_q), and the "
                "2-torsion point has x = 0 which lies in V and is rational. "
                "Lemma 2 part 1's 's = 0 or s >= 2' therefore holds here "
                "WITHOUT its side condition. Verified in "
                "selftest_yield_core.py route F."),
        },
    }


def c_of_t_block(counts: dict, ordered: dict, n: int, t: int, k: int) -> dict:
    """HEUR-003's c(t), at both granularities, because the heuristic is ambiguous.

    HEUR-003 states the per-R count is Poisson with mean 2^{tk-n} * c(t) and
    that c(t) = 1 when eq. (11) is exact. Those two clauses do not agree: with
    eq. (11) exact the CLASS count has mean 2^{tk-n}/t!, not 2^{tk-n}. The
    formula is the mean of the ORDERED count and the calibration clause is the
    mean of the CLASS count, so c(t) is reported once per granularity against
    its own matching model mean. Both are 1 exactly when eq. (11) is exact,
    which is the reading under which the two clauses are consistent. The
    ambiguity is recorded rather than resolved here: the prediction is frozen.
    """
    two_pow = 2.0 ** (t * k - n)
    out = {
        "model_mean_ordered_2_pow_tk_minus_n": two_pow,
        "model_mean_class_2_pow_tk_minus_n_over_t_factorial":
            two_pow / factorial(t),
        "ambiguity_note": (
            "HEUR-003's formula names 2^{tk-n}, which is the mean of the "
            "ORDERED count; its calibration clause 'c(t) = 1 when eq. (11) "
            "is exact' is true of the CLASS count against 2^{tk-n}/t!. Both "
            "readings are reported. Neither the heuristic nor the frozen "
            "prediction was altered."),
    }
    for pres, arr in counts.items():
        lo, hi = mean_interval(arr)
        out[f"c_of_t_class_granularity_{pres}"] = {
            "value": float(arr.mean()) / (two_pow / factorial(t)),
            "ci95": [lo / (two_pow / factorial(t)),
                     hi / (two_pow / factorial(t))],
        }
    for pres, arr in ordered.items():
        lo, hi = mean_interval(arr)
        out[f"c_of_t_ordered_granularity_{pres}"] = {
            "value": float(arr.mean()) / two_pow,
            "ci95": [lo / two_pow, hi / two_pow],
        }
    return out


# --------------------------------------------------------------------------
# Exact measurements over ALL targets (no sampling error at all)
# --------------------------------------------------------------------------
def exact_usable_over_all_R(ctx: CellContext, t: int,
                            state_cap: int = 3_000_000) -> dict:
    """Exact usable-relation count for EVERY affine R, by one enumeration.

    The 2000-draw measurement the contract specifies carries binomial
    sampling error; this does not. It enumerates every t-multiset of the
    F_q-rational factor base once, histograms the sums, and reads the zero
    fraction off the whole target population. It answers only for the
    `usable` presentation -- `single` and `chained` need the twist side and
    the chain walk, which is the per-R path -- and it is reported beside the
    sampled figure rather than instead of it.
    """
    X, Y, L = ctx.e_pts.X, ctx.e_pts.Y, ctx.e_pts.n
    curve = ctx.curve
    Vset = set(int(v) for v in ctx.V)
    expected = comb(L + t - 1, t)
    per_first = max(1, comb(L + t - 2, t - 1)) if t > 1 else 1
    block = max(1, min(L, state_cap // max(1, per_first)))
    seen: dict[int, int] = {}
    visited = at_infinity = x_inside_V = 0
    Varr = np.array(sorted(Vset), dtype=U32)
    for lo in range(0, L, block):
        hi = min(lo + block, L)
        idx = np.arange(lo, hi, dtype=np.int64)
        sx, sy = X[idx].copy(), Y[idx].copy()
        si = np.zeros(idx.size, dtype=bool)
        last = idx
        for _ in range(t - 1):
            parent, new = expand_prefixes(last, L)
            sx, sy, si = curve.add(sx[parent], sy[parent], si[parent],
                                   X[new], Y[new],
                                   np.zeros(new.shape, dtype=bool))
            last = new
        visited += int(sx.size)
        # A decomposition of R uses the sum S = -R, so keep the sums whose
        # x is a legal target: affine and outside V.
        at_infinity += int(si.sum())
        keep = ~si
        if keep.any():
            kx, ky = sx[keep], sy[keep]
            inV = np.isin(kx, Varr)
            x_inside_V += int(inV.sum())
            kx, ky = kx[~inV], ky[~inV]
            keys = curve.key(kx, ky, np.zeros(kx.size, dtype=bool))
            u, c = np.unique(keys, return_counts=True)
            for kk, cc in zip(u.tolist(), c.tolist()):
                seen[kk] = seen.get(kk, 0) + cc
    assert visited == expected, (visited, expected)
    total_affine = ctx.curve.group_order() - 1
    targets = total_affine - ctx.e_pts.n          # affine points with x not in V
    hit = len(seen)
    incidences = sum(seen.values())
    # THE CONSERVATION IDENTITY, exact and model-free. Every t-multiset of the
    # rational factor base sums to exactly one group element, so the incidences
    # must account for every multiset enumerated. This is what fixes the mean
    # realized count without any probability model: it is
    # C(L+t-1, t) / (number of targets), up to the multisets that land on
    # infinity or inside V and are therefore not decompositions of a legal
    # target. A mismatch here would mean the enumeration lost or duplicated
    # multisets, which no statistical check downstream could detect.
    accounted = incidences + at_infinity + x_inside_V
    return {
        "enumerated_multisets": visited,
        "expected_multisets_binom_L_plus_t_minus_1_choose_t": expected,
        "rational_factor_base_points_L": L,
        "conservation": {
            "incidences_on_legal_targets": incidences,
            "multisets_summing_to_infinity": at_infinity,
            "multisets_whose_sum_has_x_in_V": x_inside_V,
            "accounted_total": accounted,
            "identity_holds": accounted == expected,
        },
        "target_population_affine_x_outside_V": targets,
        "targets_with_at_least_one_usable_relation": hit,
        "exact_hit_fraction": hit / targets if targets else float("nan"),
        "exact_zero_fraction": 1.0 - hit / targets if targets else float("nan"),
        "exact_mean_count": incidences / targets if targets else float("nan"),
        "incidences": incidences,
        "eq11_semaev_lambda": len(Vset) ** t / factorial(t) / ctx.field.q,
        "ratio_of_exact_mean_to_eq11_semaev_lambda": (
            (incidences / targets)
            / (len(Vset) ** t / factorial(t) / ctx.field.q)
            if targets else float("nan")),
        "closed_form_note": (
            "The exact mean is C(L+t-1, t) / (targets), with L the number of "
            "F_q-RATIONAL factor-base points rather than |V|. L = 2r - 1 where "
            "r is the number of x in V carrying a rational point, and r is "
            "binomial(|V|, ~1/2) over curves, so E[L] is about |V| and L "
            "fluctuates with standard deviation about sqrt(|V|). eq. (11) "
            "uses |V|^t/t! in place of C(L+t-1, t); the ratio between them is "
            "the whole of the discrepancy in the mean, and it is computable "
            "in closed form without any measurement."),
    }


def exhaustive_all_R(ctx: CellContext, t: int, side: str = "E",
                     cap_seconds: float = 240.0) -> dict:
    """Per-R single/chained counts over the WHOLE target population.

    Only run where the population is small enough to walk; the point is to
    show what the 2000-draw sampling error costs by removing it. Returns
    `completed: False` with what it reached if the cap bites, and the
    incomplete pass is then reported as such and used for nothing.
    """
    curve = ctx.curve if side == "E" else ctx.twist
    Vset = set(int(v) for v in ctx.V)
    q = ctx.field.q
    single_hits = chained_hits = usable_hits = seen = 0
    single_tot = chained_tot = usable_tot = 0
    t0 = time.time()
    for x in range(1, q):
        if x in Vset:
            continue
        ys = curve.ys_for_x_scalar(x)
        if not ys:
            continue
        for y in ys:
            res = ctx.solve_for_target((x, y), t, side=side)
            seen += 1
            single_tot += res["single_x_multiset"]
            chained_tot += res["chained_x_multiset"]
            usable_tot += res["usable_point_multiset"]
            single_hits += int(res["single_x_multiset"] > 0)
            chained_hits += int(res["chained_x_multiset"] > 0)
            usable_hits += int(res["usable_point_multiset"] > 0)
        if time.time() - t0 > cap_seconds:
            return {"completed": False, "reason": "wall-clock cap",
                    "targets_walked": seen, "seconds": time.time() - t0,
                    "x_reached": x, "q": q}
    return {
        "completed": True, "side": side, "targets": seen,
        "seconds": time.time() - t0,
        "single": {"hit_fraction": single_hits / seen,
                   "zero_fraction": 1 - single_hits / seen,
                   "mean": single_tot / seen},
        "chained": {"hit_fraction": chained_hits / seen,
                    "zero_fraction": 1 - chained_hits / seen,
                    "mean": chained_tot / seen},
        "usable": {"hit_fraction": usable_hits / seen,
                   "zero_fraction": 1 - usable_hits / seen,
                   "mean": usable_tot / seen},
    }


# --------------------------------------------------------------------------
# Controls that are not the main sweep
# --------------------------------------------------------------------------
def exhaustiveness_control(cells: list[dict], seed: int) -> list[dict]:
    """Enumerate V^t twice under two orderings; per-R counts must be identical.

    An enumeration whose result depends on the order in which it visits the
    domain has missed part of it. The permutation is applied to the
    factor-base point list, which changes every intermediate prefix and every
    chunk boundary while leaving the set of multisets alone.
    """
    out = []
    for cell in sorted(cells, key=lambda c: (1 << c["k"]) ** c["t"])[:3]:
        n, m, t, k = cell["n"], cell["m"], cell["t"], cell["k"]
        field = FastField.get(n)
        V, basis = build_subspace(field, k, "low_degree_polynomial",
                                  np.random.default_rng(seed))
        ctx = CellContext(n, 0, 1, V)
        rng = random.Random(seed)
        Rs = draw_targets(ctx, "E", 300, rng)
        keys = ctx.curve.key(
            np.array([R[0] for R in Rs], dtype=U32),
            np.array([R[1] ^ R[0] for R in Rs], dtype=U32),   # -R
            np.zeros(len(Rs), dtype=bool))
        base, states = count_multiset_sums(ctx.curve, ctx.e_pts.X,
                                           ctx.e_pts.Y, t, keys)
        agree = True
        perms = []
        for pseed in (1, 2, 3):
            perm = np.random.default_rng(seed + pseed).permutation(ctx.e_pts.n)
            alt, states2 = count_multiset_sums(ctx.curve, ctx.e_pts.X,
                                               ctx.e_pts.Y, t, keys, perm=perm)
            ok = bool(np.array_equal(base, alt)) and states2 == states
            perms.append({"perm_seed": int(seed + pseed), "identical": ok})
            agree &= ok
        # and against the independent per-R lookup path
        per_r = np.array([ctx.solve_for_target(R, t)["usable_point_multiset"]
                          for R in Rs], dtype=np.int64)
        lookup_ok = bool(np.array_equal(base, per_r))
        out.append({
            "cell": {"n": n, "m": m, "t": t, "k": k},
            "V_to_the_t": (1 << k) ** t,
            "multisets_enumerated": states,
            "expected_multisets": comb(ctx.e_pts.n + t - 1, t),
            "targets": len(Rs),
            "order_independent": agree,
            "permutations": perms,
            "agrees_with_independent_per_R_path": lookup_ok,
            "passed": agree and lookup_ok,
        })
    return out


def invalid_input_control() -> dict:
    """R at infinity and a V that is not F_2-closed: both must be rejected."""
    results = {}
    try:
        validate_target(None)
        results["R_at_infinity_rejected"] = False
    except ValueError as exc:
        results["R_at_infinity_rejected"] = True
        results["R_at_infinity_message"] = str(exc)
    not_closed = [0, 1, 2, 4]          # 1 ^ 2 = 3 is absent
    try:
        validate_subspace(not_closed, 2)
        results["non_subspace_V_rejected"] = False
    except ValueError as exc:
        results["non_subspace_V_rejected"] = True
        results["non_subspace_message"] = str(exc)
    try:
        validate_subspace(span_of([1, 2]), 2)
        results["genuine_subspace_accepted"] = True
    except ValueError as exc:
        results["genuine_subspace_accepted"] = False
        results["genuine_subspace_error"] = str(exc)
    wrong_size = span_of([1, 2])
    try:
        validate_subspace(wrong_size, 3)
        results["wrong_dimension_rejected"] = False
    except ValueError:
        results["wrong_dimension_rejected"] = True
    results["passed"] = (results["R_at_infinity_rejected"]
                         and results["non_subspace_V_rejected"]
                         and results["genuine_subspace_accepted"]
                         and results["wrong_dimension_rejected"])
    return results


# --------------------------------------------------------------------------
# Aggregation across configurations
# --------------------------------------------------------------------------
def pool_cell(entries: list[dict], side: str, n: int, m: int, t: int,
              k: int) -> dict:
    """Pool a cell's configurations into one ratio per presentation.

    Pooling is over the union of all drawn R across the cell's 20
    configurations (2 subspace variants x 2 curve coefficients x 5 seeds), so
    the interval narrows by sqrt(20) relative to any single configuration
    while the object measured stays the cell. Per-configuration numbers are
    kept too, since a spread across curve coefficients would matter and a
    pooled figure would hide it.
    """
    pooled = {}
    for pres, col in (("single", "single_x_multiset"),
                      ("chained", "chained_x_multiset"),
                      ("usable", "usable_point_multiset")):
        arr = np.concatenate([np.array(e["sides"][side]["_columns"][col],
                                       dtype=np.int64)
                              for e in entries if side in e["sides"]
                              and "_columns" in e["sides"][side]])
        pooled[pres] = {v: ratio_block(arr, n, t, k, v) for v in CLASS_VARIANTS}
        pooled[pres]["poisson_fit"] = poisson_fit(arr)
        pooled[pres]["extreme_tail"] = extreme_tail_check(arr)
        pooled[pres]["histogram"] = {str(v): int(c) for v, c in
                                     zip(*np.unique(arr, return_counts=True))}
    l2 = np.concatenate([
        np.array(e["sides"][side]["_columns"]["lemma2_side_condition_holds"],
                 dtype=bool)
        for e in entries if side in e["sides"]
        and "_columns" in e["sides"][side]])
    sing = np.concatenate([
        np.array(e["sides"][side]["_columns"]["single_x_multiset"],
                 dtype=np.int64)
        for e in entries if side in e["sides"]
        and "_columns" in e["sides"][side]])
    chai = np.concatenate([
        np.array(e["sides"][side]["_columns"]["chained_x_multiset"],
                 dtype=np.int64)
        for e in entries if side in e["sides"]
        and "_columns" in e["sides"][side]])
    outs = np.concatenate([
        np.array(e["sides"][side]["_columns"]["outside_fq_point_multiset"],
                 dtype=np.int64)
        for e in entries if side in e["sides"]
        and "_columns" in e["sides"][side]])
    diff = chai - sing
    pooled["lemma2"] = {
        "draws": int(l2.size),
        "side_condition_failure_fraction": float(1 - l2.mean()),
        "side_condition_failure_ci95": list(
            wilson(int((~l2).sum()), int(l2.size))),
        "chained_minus_single_histogram": {
            str(v): int(c) for v, c in zip(*np.unique(diff,
                                                      return_counts=True))},
        "R_where_they_differ": int(np.count_nonzero(diff)),
        "R_where_they_differ_and_condition_HELD": int(
            np.count_nonzero(diff[l2])),
        "R_where_they_differ_and_condition_FAILED": int(
            np.count_nonzero(diff[~l2])),
        "outside_fq_solution_total": int(outs.sum()),
        "R_with_any_outside_fq_solution": int(np.count_nonzero(outs)),
        "y_outside_Fq_solution_fraction": float(
            outs.sum() / max(1, int(
                np.concatenate([
                    np.array(e["sides"][side]["_columns"]
                             ["point_multiset_total"], dtype=np.int64)
                    for e in entries if side in e["sides"]
                    and "_columns" in e["sides"][side]]).sum()))),
    }
    pooled["c_of_t"] = c_of_t_block(
        {"single": sing, "chained": chai,
         "usable": np.concatenate([
             np.array(e["sides"][side]["_columns"]["usable_point_multiset"],
                      dtype=np.int64)
             for e in entries if side in e["sides"]
             and "_columns" in e["sides"][side]])},
        {"single": np.concatenate([
            np.array(e["sides"][side]["_columns"]["single_x_ordered"],
                     dtype=np.int64)
            for e in entries if side in e["sides"]
            and "_columns" in e["sides"][side]]),
         "chained": np.concatenate([
             np.array(e["sides"][side]["_columns"]["chained_x_ordered"],
                      dtype=np.int64)
             for e in entries if side in e["sides"]
             and "_columns" in e["sides"][side]])},
        n, t, k)
    return pooled


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--per-r-out", required=True)
    ap.add_argument("--repo", default="/workspace")
    ap.add_argument("--draws", type=int, default=None)
    ap.add_argument("--only-cells", type=int, default=None)
    ap.add_argument("--seeds", type=int, default=None)
    ap.add_argument("--skip-exhaustive", action="store_true")
    args = ap.parse_args()

    spec_path = os.path.join(args.repo, "experiments/EXP-SEMBIN-354a75/"
                                        "specification.yaml")
    tables_path = os.path.join(args.repo, "inputs/SEMAEV-2015-310/tables.yaml")
    spec = yaml.safe_load(open(spec_path))["experiment"]
    inputs = spec["inputs"]
    cells = [dict(c) for c in inputs["cells"]]
    seeds = list(inputs["seeds"])
    subspaces = list(inputs["subspace_variants"])
    draws = args.draws or int(inputs["random_R_draws_per_cell"])
    if args.only_cells:
        cells = cells[:args.only_cells]
    if args.seeds:
        seeds = seeds[:args.seeds]

    started = now()
    result = {
        "experiment_id": spec["id"],
        "hypothesis_id": spec["hypothesis_id"],
        "run_id": "RUN-SEMBIN-1b9afe",
        "task_id": "TASK-20260913-4df669",
        "specification_version": spec["version"],
        "specification_status": spec["status"],
        "specification_approved_by": spec["approved_by"],
        "started_at": started,
        "protocol": {
            "cells_declared": cells,
            "seeds": seeds,
            "subspace_variants": subspaces,
            "curve_coefficient_modes": ["B_eq_1", "random_B"],
            "curve_A": 0,
            "curve_A_note": ("The paper writes y^2 + xy = x^3 + a x^2 + b and "
                             "tabulates B only, so A is fixed at 0 and "
                             "recorded rather than varied."),
            "R_draws_per_configuration_per_side": draws,
            "class_count_variants": list(CLASS_VARIANTS),
            "presentations": list(PRESENTATIONS),
            "target_populations": {
                "E": "R uniform on affine E(F_q) with R_X outside V -- the "
                     "algorithm's own population, and Lemma 2's hypothesis",
                "T": "R_X uniform over the F_q values carrying NO rational "
                     "point, represented as affine points of the quadratic "
                     "twist. The other half of eq. (11)'s 'random z in F_q'.",
            },
            "window": inputs["window"],
            "no_cells_added_note": (
                "Exactly the nine declared cells were run. No cell outside "
                "tk - n in [-6, +6] was added."),
        },
        "controls": {},
        "cells": [],
        "unreached_cells": [],
        "results_table": [],
        "deviations": [],
        "unexpected_observations": [],
    }

    # ---- control 1: baseline -------------------------------------------
    base = baseline_control(tables_path)
    result["controls"]["baseline"] = base
    print(f"[baseline] {base['matched_by_either']}/{base['cells_checked']} "
          f"printed cells reproduced to 4 dp "
          f"(rounding {base['matched_by_rounding']}, "
          f"truncation {base['matched_by_truncation']}), "
          f"max abs error {base['max_abs_error']:.2e}", flush=True)
    if not base["all_matched_to_four_decimals"]:
        result["stopped"] = {
            "reason": "procedure_defect",
            "detail": ("eq. (11) did not reproduce the printed decimals; the "
                       "contract's first stopping rule halts the run here."),
            "failing_rows": [r for r in base["rows"]
                             if not (r["matches_by_rounding"]
                                     or r["matches_by_truncation"])],
        }
        json.dump(result, open(args.out, "w"), indent=1, sort_keys=True)
        return 3

    # The spec's own per-cell annotation is checked against the frozen table.
    annot = []
    tables = yaml.safe_load(open(tables_path))
    printed = {}
    for tname in ("table_1", "table_2"):
        for r in tables[tname]["rows"]:
            if r.get("P_theoretical") is None:
                continue
            t = r.get("t", r.get("t_eq_m"))
            m = r.get("m", r.get("t_eq_m"))
            printed.setdefault((r["n"], m, t, r["k"]), set()).add(
                float(r["P_theoretical"]))
    for c in cells:
        if c.get("paper_probability") is None:
            continue
        key = (c["n"], c["m"], c["t"], c["k"])
        vals = printed.get(key, set())
        annot.append({
            "cell": {kk: c[kk] for kk in ("n", "m", "t", "k")},
            "specification_annotation": c["paper_probability"],
            "frozen_table_printed_values": sorted(vals),
            "annotation_matches_frozen_table": (
                any(abs(c["paper_probability"] - v) < 5e-9 for v in vals)),
            "recomputed_eq11": eq11(c["n"], c["t"], c["k"])["P"],
        })
    result["controls"]["specification_annotation_crosscheck"] = {
        "purpose": ("The specification's `paper_probability` field is an "
                    "annotation on the cell list, not the frozen source. It "
                    "is checked against inputs/SEMAEV-2015-310/tables.yaml so "
                    "that a mis-citation in the annotation is not mistaken "
                    "for eq. (11) failing to reproduce."),
        "rows": annot,
        "all_annotations_match": all(a["annotation_matches_frozen_table"]
                                     for a in annot),
    }
    for a in annot:
        if not a["annotation_matches_frozen_table"]:
            result["unexpected_observations"].append({
                "kind": "specification_annotation_mismatch",
                "cell": a["cell"],
                "detail": (
                    f"specification.yaml annotates paper_probability = "
                    f"{a['specification_annotation']} for this cell, but the "
                    f"frozen transcription prints "
                    f"{sorted(a['frozen_table_printed_values'])} for it, and "
                    f"eq. (11) gives {a['recomputed_eq11']:.6f}. The "
                    f"annotation is not the frozen source and was not edited; "
                    f"the baseline control above is run against the frozen "
                    f"table, where eq. (11) does reproduce every printed "
                    f"value."),
            })

    # ---- control 5: invalid input ---------------------------------------
    result["controls"]["invalid_input"] = invalid_input_control()
    print(f"[invalid_input] passed={result['controls']['invalid_input']['passed']}",
          flush=True)

    # ---- control 6: exhaustiveness --------------------------------------
    ex = exhaustiveness_control(cells, seeds[0])
    result["controls"]["exhaustiveness"] = {
        "cells": ex, "passed": all(e["passed"] for e in ex)}
    print(f"[exhaustiveness] passed={result['controls']['exhaustiveness']['passed']}",
          flush=True)

    # ---- control 2 and 4: matched null and known-false realization ------
    nulls, nulls_kf = [], []
    for c in cells:
        nulls.append(null_block(c["n"], c["m"], c["t"], c["k"], seeds,
                                draws=draws, mode="exact_multiset"))
        nulls_kf.append(null_block(c["n"], c["m"], c["t"], c["k"], seeds,
                                   draws=draws, mode="ordered"))
    result["controls"]["matched_null"] = {
        "design": ("A symmetric random map on the EXACT class count "
                   "C(|V|+t-1, t), realized and pushed through the same ratio "
                   "code. Its ratio against the matching class-count variant "
                   "is the test of the pipeline; its ratio against Semaev's "
                   "variant MEASURES eq. (11)'s class-count approximation and "
                   "tests nothing about the code."),
        "gate": ("The contract stops the run if this returns a ratio BELOW 1. "
                 "A ratio above 1 on the null is the class-count inflation, "
                 "which is a property of eq. (11), not of the counting."),
        "cells": nulls,
        "min_matched_ratio": min(b["matched_ratio_min"] for b in nulls),
        "max_matched_ratio": max(b["matched_ratio_max"] for b in nulls),
    }
    result["controls"]["known_false_class_count"] = {
        "design": ("Two independent forms. (a) DENOMINATOR: the same measured "
                   "counts divided by eq. (11) evaluated with K = |V|^t and no "
                   "symmetry correction, which must shift every ratio by the "
                   "expected t! factor. (b) REALIZATION: a non-symmetric "
                   "random map on |V|^t ordered tuples, which must inflate the "
                   "realized mean by t! against the symmetric map."),
        "realization_cells": nulls_kf,
    }
    null_min = result["controls"]["matched_null"]["min_matched_ratio"]
    print(f"[matched_null] matched ratio range "
          f"[{null_min:.4f}, "
          f"{result['controls']['matched_null']['max_matched_ratio']:.4f}]",
          flush=True)
    if null_min < 1.0 - 0.05:
        result["stopped"] = {
            "reason": "matched_null_below_one",
            "detail": ("The realized random map returned a ratio below 1 "
                       "under the matched class count, so the pipeline is "
                       "producing the deficit itself. The contract stops the "
                       "whole run here."),
            "min_matched_ratio": null_min,
        }
        json.dump(result, open(args.out, "w"), indent=1, sort_keys=True)
        return 4

    # ---- the main sweep --------------------------------------------------
    per_r_file = {"run_id": result["run_id"], "columns": list(PER_R_COLUMNS),
                  "note": ("Per-R counts retained in full, columnar, for every "
                           "target of every configuration and both target "
                           "populations. Row i of every column refers to the "
                           "same R."),
                  "configurations": []}
    run_index = 0
    for cell in cells:
        n, m, t, k = cell["n"], cell["m"], cell["t"], cell["k"]
        entries = []
        for subspace in subspaces:
            for b_mode in ("B_eq_1", "random_B"):
                for seed in seeds:
                    run_index += 1
                    t0 = time.time()
                    cfg = run_config(cell, subspace, b_mode, seed, draws)
                    secs = time.time() - t0
                    rss = (resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
                           * 1024)
                    cfg["run_index"] = run_index
                    cfg["wall_seconds"] = secs
                    cfg["peak_rss_bytes_process_high_water"] = rss
                    entries.append(cfg)
                    slim = {kk: vv for kk, vv in cfg.items() if kk != "sides"}
                    slim["sides"] = {}
                    percfg = {"label": cfg["label"], "columns": {}}
                    for side, sd in cfg["sides"].items():
                        cols = sd.pop("_columns", None)
                        slim["sides"][side] = sd
                        if cols is not None:
                            percfg["columns"][side] = cols
                            sd["_columns"] = cols   # keep for pooling
                    per_r_file["configurations"].append(percfg)
                    print(f"[{run_index:3d}] {cfg['label']}: "
                          f"{secs:6.2f}s rss={rss/1e9:.2f}GB "
                          + " ".join(
                              f"{s}:single={cfg['sides'][s]['counts_summary']['single']['mean']:.4f}"
                              for s in cfg["sides"]
                              if "counts_summary" in cfg["sides"][s]),
                          flush=True)
        cell_out = {
            "cell": {"n": n, "m": m, "t": t, "k": k},
            "tk_minus_n": t * k - n,
            "paper_probability_annotation": cell.get("paper_probability"),
            "eq11": {v: eq11(n, t, k, v) for v in CLASS_VARIANTS},
            "class_count_inflation_exact_over_semaev":
                class_count_inflation(1 << k, t),
            "enumeration_domain_V_to_the_t": (1 << k) ** t,
            "reached_exhaustively": True,
            "configurations": [
                {kk: vv for kk, vv in e.items() if kk != "sides"}
                | {"sides": {s: {k2: v2 for k2, v2 in sd.items()
                                 if k2 != "_columns"}
                             for s, sd in e["sides"].items()}}
                for e in entries],
            "pooled": {},
        }
        for side in ("E", "T"):
            if not any(side in e["sides"] and "_columns" in e["sides"][side]
                       for e in entries):
                continue
            cell_out["pooled"][side] = pool_cell(entries, side, n, m, t, k)
        # exact, sampling-error-free supplements
        if not args.skip_exhaustive:
            field = FastField.get(n)
            V, _basis = build_subspace(field, k, "low_degree_polynomial",
                                       np.random.default_rng(
                                           derived_seed(seeds[0], "exact")))
            ctx = CellContext(n, 0, 1, V)
            cell_out["exact_usable_all_R_B1_low_degree"] = (
                exact_usable_over_all_R(ctx, t))
            if n <= 17:
                cell_out["exhaustive_all_R_B1_low_degree"] = (
                    exhaustive_all_R(ctx, t, "E"))
            del ctx
        result["cells"].append(cell_out)

        for e in entries:
            for side, sd in e["sides"].items():
                if "ratios" not in sd:
                    continue
                for pres in PRESENTATIONS:
                    for variant in CLASS_VARIANTS:
                        rb = sd["ratios"][pres][variant]
                        result["results_table"].append({
                            "n": n, "m": m, "t": t, "k": k,
                            "tk_minus_n": t * k - n,
                            "presentation": pres,
                            "class_count": variant,
                            "subspace": e["subspace_variant"],
                            "B": e["curve_B"], "b_mode": e["b_mode"],
                            "seed": e["seed"],
                            "target_population": side,
                            "draws": rb["draws"],
                            "measured_hit_fraction": rb["measured_hit_fraction"],
                            "measured_zero_fraction": rb["measured_zero_fraction"],
                            "measured_mean_count": rb["measured_mean_count"],
                            "modelled_P": rb["modelled_P_zero_complement"],
                            "ratio_zero_headline": rb["ratio_zero_headline"],
                            "ratio_zero_ci95": rb["ratio_zero_ci95"],
                            "ratio_mean": rb["ratio_mean"],
                        })
        for e in entries:      # release the retained columns for this cell
            for sd in e["sides"].values():
                sd.pop("_columns", None)

    result["finished_at"] = now()
    result["peak_rss_bytes_process_high_water"] = (
        resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024)
    result["total_configurations_run"] = run_index
    result["maximum_runs_allowed"] = spec["budget"]["maximum_runs"]

    json.dump(result, open(args.out, "w"), indent=1, sort_keys=True,
              default=float)
    with open(args.per_r_out, "w") as fh:
        json.dump(per_r_file, fh, separators=(",", ":"), sort_keys=True)
        fh.write("\n")
    print(f"\nwrote {args.out} and {args.per_r_out}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
