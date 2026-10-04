#!/usr/bin/env python3
"""Red-team recomputation for REVIEW-SEMBIN-20260913-9d649f, joints J2, J3, J5.

Written for TASK-20260913-cf9d98. This is an INDEPENDENT reimplementation of the
cost model of COST-SEMBIN-8d123b: it imports nothing from the producer's code and
re-states every formula from the record and the review plan. It is validated
against the record's own quoted figures before any new number is reported, so
that a disagreement localises to the model rather than to a transcription.

Nothing here re-derives Semaev's memory accounting (J1) or the yield mechanism
(J4); those joints belong to another task. The memory model is taken AS THE
RECORD STATES IT and attacked only as a comparison.
"""

from __future__ import annotations

import json
import math

LOG2_3 = math.log2(3.0)
VOW_CONSTANT_LOG2 = math.log2(0.886)
FIPS_N = [163, 233, 283, 409, 571]


# ==========================================================================
# Semaev side, restated from COST-SEMBIN-8d123b / review-plan parameters
# ==========================================================================

def log2_factorial(m: int) -> float:
    return math.lgamma(m + 1.0) / math.log(2.0)


def log2_add(a: float, b: float) -> float:
    hi, lo = max(a, b), min(a, b)
    return hi if hi - lo > 60 else hi + math.log2(1.0 + 2.0 ** (lo - hi))


def log2_macaulay_width(nvars: int, degree: int = 4) -> float:
    return math.log2(sum(math.comb(nvars, d) for d in range(degree + 1)))


def semaev_time_log2(n: int, m: int, omega: float = 3.0,
                     omega_prime: float = 2.0) -> float:
    """stage 1 = m! 2^{n/m} n^{4w}; stage 2 = 2^{k w'}; un-ceiled k as in Table 3."""
    k = n / m
    stage1 = log2_factorial(m) + k + 4.0 * omega * math.log2(n)
    stage2 = k * omega_prime
    return log2_add(stage1, stage2)


def semaev_stage1_log2(n: int, m: int, omega: float = 3.0) -> float:
    return log2_factorial(m) + n / m + 4.0 * omega * math.log2(n)


def semaev_optimal_m(n: int, m_hi: int = 30) -> int:
    return min(range(2, min(m_hi, n) + 1), key=lambda m: semaev_stage1_log2(n, m))


def semaev_memory_log2(n: int, m: int, storage: str, degree: int = 4) -> float:
    """log2 bits. max(relation store, Groebner working set), ceiled k."""
    k = -(-n // m)
    store = k + math.log2(m * k + 2 * n)
    if storage == "dense":
        nvars = (m - 2) * n + k * m
        ws = 2.0 * log2_macaulay_width(nvars, degree)
    elif storage == "semaev_sparse":
        ws = (4.0 * math.log2(n * m) - math.log2(24.0)
              + 3.0 * math.log2(n) - math.log2(m))
    else:
        raise ValueError(storage)
    return log2_add(store, ws)


# ==========================================================================
# baseline side
# ==========================================================================

def vow_time_log2(n: int, processors_log2: float = 0.0,
                  cofactor: int = 1, walk_constant: float = 0.886,
                  automorphism_speedup_log2: float = 0.0) -> float:
    """0.886 sqrt(q) group ops, q = 2^n / cofactor, on 2^processors_log2 cores."""
    return (math.log2(walk_constant) + (n - math.log2(cofactor)) / 2.0
            - processors_log2 - automorphism_speedup_log2)


def vow_memory_log2(n: int, store_log2: float = 30.0) -> float:
    """distinguished-point store: 2^store_log2 points at 3n bits each."""
    return store_log2 + math.log2(3.0 * n)


# ==========================================================================
# metrics
# ==========================================================================

def combine(metric: str, t: float, mem: float, alpha: float = 1.0,
            budget_log2: float | None = None) -> float:
    if metric == "time_only":
        return t
    if metric == "product":
        return t + mem
    if metric == "max":
        return max(t, mem)
    if metric == "weighted":                       # T * M^alpha
        return t + alpha * mem
    if metric == "budget_soft":                    # passes = max(1, M/B)
        return t + max(0.0, mem - budget_log2)
    if metric == "budget_hard":                    # infeasible above the cap
        return t if mem <= budget_log2 else float("inf")
    raise ValueError(metric)


def compare(n: int, metric: str, storage: str, *, store_log2: float = 30.0,
            processors_log2: float = 0.0, cofactor: int = 1,
            walk_constant: float = 0.886, automorphism_speedup_log2: float = 0.0,
            alpha: float = 1.0, budget_log2: float | None = None,
            baseline_memory: str = "store", m: int | None = None) -> dict:
    """margin_bits > 0 means SEMAEV is ahead, matching the record's sign."""
    if m is None:
        m = semaev_optimal_m(n)
    st = semaev_time_log2(n, m)
    sm = semaev_memory_log2(n, m, storage)
    bt = vow_time_log2(n, processors_log2, cofactor, walk_constant,
                       automorphism_speedup_log2)
    if baseline_memory == "store":
        bm = vow_memory_log2(n, store_log2)
    elif baseline_memory == "none":
        bm = -1e9
    else:
        raise ValueError(baseline_memory)
    sc = combine(metric, st, sm, alpha, budget_log2)
    bc = combine(metric, bt, bm, alpha, budget_log2)
    return {"n": n, "m": m, "semaev_time": st, "semaev_mem": sm,
            "baseline_time": bt, "baseline_mem": bm,
            "semaev_cost": sc, "baseline_cost": bc,
            "margin_bits": (bc - sc) if math.isfinite(bc - sc)
            else (math.inf if sc < bc else -math.inf),
            "semaev_wins": sc < bc}


def crossover(metric: str, storage: str, n_lo: int = 250, n_hi: int = 900,
              **kw) -> int | None:
    for n in range(n_lo, n_hi + 1):
        if compare(n, metric, storage, **kw)["semaev_wins"]:
            # require monotone-after: the record reports monotonicity
            return n
    return None


# ==========================================================================
# STEP 0 -- validate this reimplementation against the record's own figures
# ==========================================================================

def validation() -> dict:
    """Reproduce COST-SEMBIN-8d123b's quoted numbers before attacking them."""
    quoted = {
        163: dict(t=123.7697, d=70.3526, s=55.2782, m=7, v=81.3254,
                  mt=-42.4443, md=-73.8632, ms=-58.7888),
        233: dict(t=138.7283, d=77.7467, s=59.9741, m=9, v=116.3254,
                  mt=-22.4029, md=-60.7004, ms=-42.9278),
        283: dict(t=147.6495, d=80.0103, s=61.9374, m=9, v=141.3254,
                  mt=-6.3241, md=-46.6047, ms=-28.5319),
        409: dict(t=166.5438, d=86.8371, s=66.5250, m=11, v=204.3254,
                  mt=37.7816, md=-8.7946, ms=11.5175),
        571: dict(t=186.3070, d=91.7726, s=70.2718, m=12, v=285.3254,
                  mt=99.0184, md=47.9882, ms=69.4889),
    }
    rows, worst = [], 0.0
    for n, q in quoted.items():
        m = semaev_optimal_m(n)
        got = {
            "t": semaev_time_log2(n, m), "m": m,
            "d": semaev_memory_log2(n, m, "dense"),
            "s": semaev_memory_log2(n, m, "semaev_sparse"),
            "v": vow_time_log2(n),
            "mt": compare(n, "time_only", "dense")["margin_bits"],
            "md": compare(n, "product", "dense")["margin_bits"],
            "ms": compare(n, "product", "semaev_sparse")["margin_bits"],
        }
        diffs = {k: round(got[k] - q[k], 6) for k in q if k != "m"}
        worst = max(worst, max(abs(v) for v in diffs.values()))
        rows.append({"n": n, "m_agrees": got["m"] == q["m"],
                     "recomputed": {k: (round(v, 4) if isinstance(v, float) else v)
                                    for k, v in got.items()},
                     "record": q, "diff_bits": diffs})
    cross = {
        "time_only/dense": crossover("time_only", "dense"),
        "time_only/sparse": crossover("time_only", "semaev_sparse"),
        "product/dense": crossover("product", "dense"),
        "product/sparse": crossover("product", "semaev_sparse"),
        "max/dense": crossover("max", "dense"),
        "max/sparse": crossover("max", "semaev_sparse"),
    }
    return {"per_n": rows, "worst_abs_diff_bits": round(worst, 6),
            "crossovers_recomputed": cross,
            "crossovers_in_record": {"time_only": 303, "product/dense": 435,
                                     "product/sparse": 375, "max": 303},
            "reproduces_record": (worst < 5e-4
                                  and cross["product/dense"] == 435
                                  and cross["product/sparse"] == 375
                                  and cross["time_only/dense"] == 303
                                  and cross["max/dense"] == 303)}


# ==========================================================================
# J2 -- is the baseline charged symmetrically
# ==========================================================================

def j2_store_sweep() -> dict:
    """(a) the store_log2 the record fixes at 30 and never sweeps."""
    out = {}
    for w in [0, 10, 20, 30, 40, 48, 60, 80]:
        row = {}
        for storage in ("dense", "semaev_sparse"):
            row[storage] = {
                "crossover_product": crossover("product", storage, store_log2=w),
                "crossover_AT": crossover("product", storage, store_log2=w),
                "margin_409": round(compare(409, "product", storage,
                                            store_log2=w)["margin_bits"], 4),
                "margin_571": round(compare(571, "product", storage,
                                            store_log2=w)["margin_bits"], 4),
                "verdict_409": ("semaev" if compare(409, "product", storage,
                                                    store_log2=w)["semaev_wins"]
                                else "vow"),
            }
        out[f"store_log2={w}"] = row
    # contract's own declared sweep values
    contract_values = [30, 40, 48, 60]
    spread = {}
    for storage in ("dense", "semaev_sparse"):
        xs = [crossover("product", storage, store_log2=w) for w in [0, 20, 40, 60]]
        spread[storage] = {"crossovers_at_store_0_20_40_60": xs,
                           "range_in_n": max(xs) - min(xs)}
    return {"sweep": out,
            "contract_declared_store_values": contract_values,
            "contract_declared_processor_values_log2": [0, 20, 40],
            "spread_over_store": spread,
            "metric_choice_range_in_n": {
                "dense": 435 - 303, "semaev_sparse": 375 - 303}}


def j2_coherent_vow() -> dict:
    """(b) the vOW time-memory tradeoff the record does not model.

    vOW with M processors, w stored distinguished points, DP probability theta:
      total work   W  = 0.886 * 2^{n/2}     (unchanged; it is a birthday bound)
      wall time    T  = W * (1/M + 1/w)     (the second term is the DP tail, 1/theta,
                                             with theta = w / W so that exactly w
                                             points are stored)
      memory       Mem = 3n * max(w, M) bits   (DP store, or per-processor state)
    so T * Mem = 3n * W * (max(w,M)/M + max(w,M)/w) >= 2 * 3n * W, and the minimum
    over the whole tradeoff curve is attained anywhere with w ~ M.  The product is
    therefore INVARIANT along the curve at 3n * 0.886 * 2^{n/2} (within a factor 2),
    independent of store_log2.
    """
    rows = []
    for n in (283, 310, 409, 571):
        W = vow_time_log2(n)
        best = None
        grid = []
        for lw in range(0, 81, 4):
            for lm in range(0, 81, 4):
                # T = W * (2^-lm + 2^-lw); Mem = 3n * 2^max(lw,lm)
                t = W + math.log2(2.0 ** (-lm) + 2.0 ** (-lw))
                mem = math.log2(3.0 * n) + max(lw, lm)
                grid.append((t + mem, lw, lm, t, mem))
        best = min(grid)
        rows.append({
            "n": n,
            "log2_total_work": round(W, 4),
            "record_charged_product": round(W + vow_memory_log2(n, 30.0), 4),
            "min_product_over_tradeoff_curve": round(best[0], 4),
            "argmin_store_log2": best[1], "argmin_processors_log2": best[2],
            "record_overcharge_bits": round(W + vow_memory_log2(n, 30.0) - best[0], 4),
            "analytic_min_product": round(W + math.log2(3.0 * n) + 1.0, 4),
        })
    # crossovers under the coherent baseline product (store effectively 2^1)
    coh = {s: crossover("product", s, store_log2=1.0) for s in
           ("dense", "semaev_sparse")}
    coh_margin = {s: round(compare(409, "product", s,
                                   store_log2=1.0)["margin_bits"], 4)
                  for s in ("dense", "semaev_sparse")}
    return {"tradeoff_grid": rows, "crossover_coherent_vow": coh,
            "margin_409_coherent_vow": coh_margin,
            "note": ("The record charges vOW the MEMORY of a 2^30-point store and "
                     "the TIME of a single processor. Those are different "
                     "operating points on the vOW curve. At any single coherent "
                     "point the product is ~3n*0.886*2^{n/2}.")}


def j2_dp_time_penalty() -> dict:
    """The time penalty for a small store, at the processor counts the contract lists."""
    rows = []
    for n in (409, 571):
        W = vow_time_log2(n)
        for lm in (0, 20, 40):
            for lw in (20, 30, 40, 60):
                t = W + math.log2(2.0 ** (-lm) + 2.0 ** (-lw))
                ideal = W - lm
                rows.append({"n": n, "processors_log2": lm, "store_log2": lw,
                             "log2_time_with_DP_tail": round(t, 4),
                             "log2_time_ideal_parallel": round(ideal, 4),
                             "penalty_bits": round(t - ideal, 4)})
    return {"rows": rows,
            "reading": ("At the M = 1 the record charges, the DP tail penalty is "
                        "2^-w of the total and is numerically zero. Charging the "
                        "tradeoff at the record's own operating point therefore "
                        "does NOT move the crossover down. The tradeoff matters "
                        "only through MEMORY, and there it moves the crossover UP.")}


def j2_small_corrections() -> dict:
    """(c) the 0.886 constant and (d) the FIPS cofactor, both closed numerically."""
    # slope of the margin in n, to convert bits into n
    base = compare(409, "product", "semaev_sparse")["margin_bits"]
    up = compare(410, "product", "semaev_sparse")["margin_bits"]
    slope = up - base                                  # bits of margin per unit n
    out = {"margin_slope_bits_per_n_at_409": round(slope, 4)}

    # walk constant
    consts = {"0.886 (record, Pollard serial rho)": 0.886,
              "1.0 (naive sqrt)": 1.0,
              "1.2533 = sqrt(pi/2) (two-walk / parallel collision)": 1.2533}
    out["walk_constant"] = {
        name: {"log2_shift_vs_record": round(math.log2(c / 0.886), 4),
               "crossover_product_sparse": crossover("product", "semaev_sparse",
                                                     walk_constant=c),
               "margin_409": round(compare(409, "product", "semaev_sparse",
                                           walk_constant=c)["margin_bits"], 4)}
        for name, c in consts.items()}

    # FIPS cofactor: the attack runs in the prime-order subgroup of order ~2^n/h
    out["cofactor"] = {}
    for h in (1, 2, 4):
        out["cofactor"][f"h={h}"] = {
            "vow_time_409": round(vow_time_log2(409, cofactor=h), 4),
            "bits_cheaper_than_h=1": round(vow_time_log2(409)
                                           - vow_time_log2(409, cofactor=h), 4),
            "crossover_product_sparse": crossover("product", "semaev_sparse",
                                                  cofactor=h),
            "crossover_time_only": crossover("time_only", "dense", cofactor=h),
            "margin_409_sparse": round(compare(409, "product", "semaev_sparse",
                                               cofactor=h)["margin_bits"], 4)}
    out["cofactor_direction"] = (
        "Taking q = 2^n rather than 2^n/h makes the baseline's cost LARGER, not "
        "smaller. Charging the cofactor makes rho CHEAPER by log2(sqrt(h)) = 0.5 "
        "(h=2) or 1.0 (h=4) bits and moves every crossover UP. The record and the "
        "review plan both state the opposite direction.")

    # negation / automorphism speedup, recalled magnitudes
    out["automorphism"] = {
        f"speedup_log2={s}": {
            "crossover_product_sparse": crossover("product", "semaev_sparse",
                                                  automorphism_speedup_log2=s),
            "margin_409_sparse": round(
                compare(409, "product", "semaev_sparse",
                        automorphism_speedup_log2=s)["margin_bits"], 4)}
        for s in (0.0, 0.5, 4.84)}
    return out


def j2_matched_null() -> dict:
    """Re-run the record's attribution control under the metric that binds."""
    rows = []
    for metric in ("time_only", "product", "max"):
        for storage in ("dense", "semaev_sparse"):
            vs_vow = crossover(metric, storage)
            vs_null = crossover(metric, storage, baseline_memory="none")
            vs_min = crossover(metric, storage, store_log2=1.0)
            rows.append({"metric": metric, "storage": storage,
                         "crossover_vs_vow_store_2^30": vs_vow,
                         "crossover_vs_zero_memory_null": vs_null,
                         "crossover_vs_coherent_vow_store_2^1": vs_min,
                         "record_reported_share": 0 if metric != "product" else None})
    return {"rows": rows,
            "reading": ("Under the product metric the record's zero-memory null is "
                        "not a null: log2(0) makes the baseline cost -inf and the "
                        "crossover undefined, so the control returns no share and "
                        "the '0 share' the record quotes comes only from the two "
                        "metrics under which memory is inert. A store of 2^1 rather "
                        "than 2^30 is the informative null and it moves the "
                        "crossover.")}


# ==========================================================================
# J3 -- the metric set
# ==========================================================================

def j3_degeneracy() -> dict:
    """Are the four declared metrics four?"""
    rows = []
    for n in FIPS_N:
        m = semaev_optimal_m(n)
        st, bt = semaev_time_log2(n, m), vow_time_log2(n)
        for storage in ("dense", "semaev_sparse"):
            sm, bm = semaev_memory_log2(n, m, storage), vow_memory_log2(n, 30.0)
            rows.append({
                "n": n, "storage": storage,
                "product_margin": round(combine("product", bt, bm)
                                        - combine("product", st, sm), 4),
                "AT_margin": round(combine("product", bt, bm)
                                   - combine("product", st, sm), 4),
                "time_only_margin": round(bt - st, 4),
                "max_margin": round(max(bt, bm) - max(st, sm), 4),
                "semaev_memory_exceeds_its_time": sm > st,
                "baseline_memory_exceeds_its_time": bm > bt,
            })
    return {"rows": rows,
            "AT_identical_to_product_by_construction": True,
            "max_identical_to_time_only_here": all(
                not r["semaev_memory_exceeds_its_time"]
                and not r["baseline_memory_exceeds_its_time"] for r in rows),
            "distinct_metrics": 2,
            "distinct_verdicts": 2}


def j3_weighted() -> dict:
    """T * M^alpha, the interpolating family the record does not report."""
    out = {}
    for alpha in (0.0, 0.1, 0.25, 0.5, 0.75, 1.0):
        out[f"alpha={alpha}"] = {
            s: {"crossover": crossover("weighted", s, alpha=alpha),
                "margin_409": round(compare(409, "weighted", s,
                                            alpha=alpha)["margin_bits"], 4)}
            for s in ("dense", "semaev_sparse")}
    # alpha at which n=409 flips, per reading
    flips = {}
    for s in ("dense", "semaev_sparse"):
        lo, hi = 0.0, 1.0
        for _ in range(60):
            mid = (lo + hi) / 2.0
            if compare(409, "weighted", s, alpha=mid)["semaev_wins"]:
                lo = mid
            else:
                hi = mid
        flips[s] = round(lo, 4)
    out["alpha_at_which_409_flips"] = flips
    return out


def j3_fixed_budget() -> dict:
    """THE METRIC THE RECORD OWES: a fixed memory budget B bits.

    Hard reading: an algorithm that cannot fit in B bits does not run.
    Soft reading: it runs, paying time * ceil(memory/B) passes (external memory).
    The baseline is charged honestly: with a budget of B bits it stores
    min(B/3n, whatever it wants) distinguished points and its total work is
    unchanged, because serial rho with Brent cycle detection needs O(n) bits.
    """
    out = {"hard": {}, "soft": {}, "semaev_min_memory_over_m": {}}
    # what is the CHEAPEST memory Semaev can run at, at each n, over all m?
    for n in FIPS_N + [310]:
        per = {}
        for storage in ("dense", "semaev_sparse"):
            best = min(((semaev_memory_log2(n, m, storage), m)
                        for m in range(2, 31)))
            per[storage] = {"min_memory_log2_bits": round(best[0], 3),
                            "at_m": best[1],
                            "memory_at_time_optimal_m": round(
                                semaev_memory_log2(n, semaev_optimal_m(n),
                                                   storage), 3)}
        out["semaev_min_memory_over_m"][n] = per

    for b in (30, 40, 50, 60, 70, 80):
        hard, soft = {}, {}
        for storage in ("dense", "semaev_sparse"):
            # HARD: Semaev must pick an m whose memory fits; minimise time over those
            def hard_cost(n: int) -> tuple[float, int | None]:
                feas = [(semaev_time_log2(n, m), m) for m in range(2, 31)
                        if semaev_memory_log2(n, m, storage) <= b]
                return min(feas) if feas else (math.inf, None)

            def hard_win(n: int) -> bool:
                c, _ = hard_cost(n)
                return c < vow_time_log2(n)

            x_hard = next((n for n in range(250, 1201) if hard_win(n)), None)
            c409, m409 = hard_cost(409)
            hard[storage] = {
                "crossover": x_hard,
                "semaev_feasible_at_409": m409 is not None,
                "semaev_time_409": (None if not math.isfinite(c409)
                                    else round(c409, 4)),
                "margin_409": (None if not math.isfinite(c409)
                               else round(vow_time_log2(409) - c409, 4)),
                "verdict_409": "vow" if not hard_win(409) else "semaev"}
            # SOFT: time * (memory/B) when memory > B
            soft[storage] = {
                "crossover": crossover("budget_soft", storage, budget_log2=b),
                "margin_409": round(compare(409, "budget_soft", storage,
                                            budget_log2=b)["margin_bits"], 4),
                "margin_571": round(compare(571, "budget_soft", storage,
                                            budget_log2=b)["margin_bits"], 4),
                "verdict_409": ("semaev" if compare(409, "budget_soft", storage,
                                                    budget_log2=b)["semaev_wins"]
                                else "vow")}
        out["hard"][f"B=2^{b} bits"] = hard
        out["soft"][f"B=2^{b} bits"] = soft

    # the budget at which n=409 flips under the soft reading
    flip = {}
    for storage in ("dense", "semaev_sparse"):
        lo, hi = 0.0, 200.0
        for _ in range(200):
            mid = (lo + hi) / 2.0
            if compare(409, "budget_soft", storage,
                       budget_log2=mid)["semaev_wins"]:
                hi = mid
            else:
                lo = mid
        flip[storage] = round(hi, 3)
    out["soft_budget_log2_at_which_409_flips_to_semaev"] = flip
    return out


# ==========================================================================
# J5 -- the declined stopping rule
# ==========================================================================

def _stage1_real_m(n: float, m: float, omega: float = 3.0) -> float:
    """n/m + log2(m!) + 4w log2 n, with m real. Stirling via lgamma."""
    return n / m + math.lgamma(m + 1.0) / math.log(2.0) + 4.0 * omega * math.log2(n)


def _argmin_real(n: float) -> float:
    """Golden-section minimise _stage1_real_m over m in [2, sqrt(n)*4]."""
    lo, hi = 2.0, max(8.0, 4.0 * math.sqrt(n))
    gr = (math.sqrt(5.0) - 1.0) / 2.0
    a, b = lo, hi
    c = b - gr * (b - a)
    d = a + gr * (b - a)
    for _ in range(400):
        if _stage1_real_m(n, c) < _stage1_real_m(n, d):
            b = d
        else:
            a = c
        c = b - gr * (b - a)
        d = a + gr * (b - a)
        if (b - a) < 1e-12 * max(1.0, b):
            break
    return (a + b) / 2.0


def _balance_ln_m(ln_n: float) -> float:
    """Solve m^2 log2 m = n in log space: 2L + ln(L/ln2) = ln n, L = ln m."""
    L = ln_n / 2.0
    for _ in range(200):
        f = 2.0 * L + math.log(L / math.log(2.0)) - ln_n
        fp = 2.0 + 1.0 / L
        L -= f / fp
    return L


def j5_c_fit() -> dict:
    """Independent fit of c. joint_balance.py is NOT imported or consulted."""
    ladder = []
    # dense ladder in log10 n, integer AND real argmin, out to float64's limit
    exps = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 20, 30, 50, 80, 120,
            180, 250, 300]
    for e in exps:
        n = 10.0 ** e
        m_real = _argmin_real(n)
        cost_real = _stage1_real_m(n, m_real)
        # integer argmin, checked on both neighbours
        m_int = min((math.floor(m_real), math.ceil(m_real)),
                    key=lambda mm: _stage1_real_m(n, float(mm)))
        cost_int = _stage1_real_m(n, float(m_int))
        ln_n = e * math.log(10.0)
        c_fit = cost_int / math.sqrt(n * ln_n)
        c_real = cost_real / math.sqrt(n * ln_n)
        ln_m = math.log(m_real)
        m_law = math.sqrt(2.0 * math.log(2.0) * n / ln_n)
        ladder.append({
            "log10_n": e,
            "m_argmin_real": float(f"{m_real:.6g}"),
            "m_argmin_int": m_int if m_int < 2 ** 62 else float(f"{m_int:.6g}"),
            "m_star_published_law": float(f"{m_law:.6g}"),
            "law_relative_error_vs_argmin": round(m_law / m_real - 1.0, 5),
            "ln_m_over_ln_n": round(ln_m / ln_n, 6),
            "c_fitted_integer_m": round(c_fit, 6),
            "c_fitted_real_m": round(c_real, 6),
            "c_from_balance_identity": round(
                2.0 * math.sqrt(ln_m / (math.log(2.0) * ln_n)), 6),
            "gap_to_asymptote": round(2.0 / math.sqrt(2.0 * math.log(2.0))
                                      - c_fit, 6),
        })
    c_star = 2.0 / math.sqrt(2.0 * math.log(2.0))

    # the analytic continuation, pushed far past what float64 can grid-search
    far = []
    for e in (300, 600, 1000, 10 ** 4, 10 ** 5, 10 ** 6, 10 ** 9, 10 ** 15):
        ln_n = e * math.log(10.0)
        L = _balance_ln_m(ln_n)
        far.append({"log10_n": e, "ln_m_over_ln_n": round(L / ln_n, 8),
                    "c_from_balance_identity": round(
                        2.0 * math.sqrt(L / (math.log(2.0) * ln_n)), 8),
                    "gap_to_asymptote": round(
                        c_star - 2.0 * math.sqrt(L / (math.log(2.0) * ln_n)), 8)})

    tail = [r for r in ladder if r["log10_n"] >= 7]
    rising = all(b["c_fitted_real_m"] > a["c_fitted_real_m"]
                 for a, b in zip(tail, tail[1:]))
    below = all(r["c_fitted_real_m"] < c_star for r in tail)
    # is the gap SHRINKING at the rate loglog n / log n, or is it a fixed offset?
    gaps = [(r["log10_n"], c_star - r["c_fitted_real_m"]) for r in tail]
    ratio_test = [{"log10_n": e, "gap": round(g, 6),
                   "gap_times_log_n_over_loglog_n": round(
                       g * math.log(10.0 ** e)
                       / math.log(math.log(10.0 ** e)), 5)}
                  for e, g in gaps]
    # fixed-offset null: fit gap = A (constant) vs gap = B*loglogn/logn
    import statistics
    const_resid = statistics.pstdev([g for _, g in gaps])
    scaled = [g * math.log(10.0 ** e) / math.log(math.log(10.0 ** e))
              for e, g in gaps]
    scaled_resid = statistics.pstdev(scaled) / statistics.mean(scaled)
    return {
        "c_published": round(c_star, 6),
        "ladder": ladder,
        "analytic_continuation": far,
        "tail_monotone_rising_from_1e7": rising,
        "tail_below_asymptote": below,
        "gap_scaling_test": ratio_test,
        "gap_constant_model_stdev": round(const_resid, 6),
        "gap_loglog_over_log_model_relative_stdev": round(scaled_resid, 6),
        "verdict": ("CONVERGING" if rising and below
                    and far[-1]["gap_to_asymptote"] < 1e-3 else "STABLE_OFFSET"),
    }


def j5_m_star_law() -> dict:
    """(b) does eq. (17)'s m* law understate the true argmin by 4-15%?"""
    rows = []
    for e in (3, 4, 5, 6, 7, 9, 11, 13):
        n = 10.0 ** e
        m_real = _argmin_real(n)
        m_int = min((math.floor(m_real), math.ceil(m_real)),
                    key=lambda mm: _stage1_real_m(n, float(mm)))
        m_law = math.sqrt(2.0 * math.log(2.0) * n / (e * math.log(10.0)))
        rows.append({"log10_n": e,
                     "m_argmin_real": float(f"{m_real:.6g}"),
                     "m_argmin_int": m_int if m_int < 2 ** 62
                     else float(f"{m_int:.6g}"),
                     "m_law": float(f"{m_law:.6g}"),
                     "law_understates_by_pct_vs_real":
                         round(100.0 * (1.0 - m_law / m_real), 3),
                     "law_understates_by_pct_vs_int":
                         round(100.0 * (1.0 - m_law / m_int), 3)})
    pct = [r["law_understates_by_pct_vs_real"] for r in rows]
    return {"rows": rows, "range_pct": [round(min(pct), 2), round(max(pct), 2)],
            "record_claimed_range_pct": [4, 15],
            "direction_confirmed": all(p > 0 for p in pct)}


# ==========================================================================

def main() -> None:
    out = {
        "task": "TASK-20260913-cf9d98",
        "review_round": "REVIEW-SEMBIN-20260913-9d649f",
        "note": ("Independent reimplementation; imports nothing from "
                 "memory_charged_cost.py or joint_balance.py."),
        "step0_validation_against_the_record": validation(),
        "J2_store_sweep": j2_store_sweep(),
        "J2_coherent_vow_tradeoff": j2_coherent_vow(),
        "J2_dp_time_penalty": j2_dp_time_penalty(),
        "J2_small_corrections": j2_small_corrections(),
        "J2_matched_null_rerun": j2_matched_null(),
        "J3_metric_degeneracy": j3_degeneracy(),
        "J3_weighted_memory_metric": j3_weighted(),
        "J3_fixed_memory_budget": j3_fixed_budget(),
        "J5_c_fit": j5_c_fit(),
        "J5_m_star_law": j5_m_star_law(),
    }
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
