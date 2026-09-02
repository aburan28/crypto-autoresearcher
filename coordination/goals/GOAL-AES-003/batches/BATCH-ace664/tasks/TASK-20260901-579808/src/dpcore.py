#!/usr/bin/env python3
# dpcore.py -- TASK-20260901-579808 (BATCH-ace664, GOAL-AES-003)
#
# Shared exact-DP core for the envelope-relative excess-zero statistic X of
# IDEA-20260901-026d6a (inherited verbatim), written FRESH for this task.
#
#   Ze(h) = 16 - wt_e_byte(h);  F(h) = 4*popcount(vmask & 0b1110);
#   X(h) = Ze(h) - F(h);        S = sum_h X(h).
# Null H0-X: non-forced bytes independent Bernoulli at class rates
#   D0 (diagonal of active-vanished hits): p = 1/256 exact
#   D1 (diagonal otherwise):               p_diag = ezdiag_miss/(4*n_miss)
#   O  (off-diagonal non-vanished words):  p_off  = ezoff_miss/(12*n_miss)
#
# Exact DP: all class rates are written over the COMMON DENOMINATOR
#   D = lcm(256, 4*n_miss, 12*n_miss)
# so every per-byte Bernoulli factor is ((D - a)/D, a/D) with integer a, and
# the convolved pmf of S is an INTEGER polynomial {k: int} with denominator
# D^B, B = total non-forced bytes. All reported p-values, means, variances,
# tails, and the realized-composition cutoff are exact rationals derived from
# these integers (fractions.Fraction for the reported values). No float
# enters the decision-bearing arithmetic.
#
# INFERENCE BLOCK: policy executor-implementation; requested_policy
# executor-implementation; resolved_model_id
# fireworks-ai/accounts/fireworks/models/qwen3p8-max (ACTUAL session model
# under inference amendment DEC-20260831-0d1eeb); fallback_used true;
# model_verified false; degraded_requirements [];
# amendment DEC-20260831-0d1eeb;
# standing_basis 0137a051eb5828789eb267fa83c8278086578d4c.
import json
from math import gcd
from fractions import Fraction

NAIVE_NUM, NAIVE_DEN = 1, 256
SUBSAMPLE_CAP = 2000  # frozen n_hits ceiling for full exact DP (not expected at t=1)


def lcm(a, b):
    return a // gcd(a, b) * b


def load_receipt(path):
    with open(path) as f:
        return json.load(f)


def per_hit_x(mask, wt_e_byte):
    F = 4 * bin(mask & 0b1110).count("1")
    Ze = 16 - wt_e_byte
    return Ze - F, F, Ze


def build_rows(receipt):
    """Per-hit rows with X, subclass, and zero_mask_e cross-checks."""
    hits = receipt.get("hit_e_detail", [])
    rows = []
    ok_x_nonneg = ok_forced = ok_xmask = True
    any_zmask = False
    for h in hits:
        mask, wt = h["vanishing_word_mask"], h["wt_e_byte"]
        X, F, Ze = per_hit_x(mask, wt)
        if X < 0:
            ok_x_nonneg = False
        row = {"thread": h["thread"], "in_thread_index": h["in_thread_index"],
               "W": h["W"], "mask": mask, "wt_e_byte": wt, "Ze": Ze, "F": F, "X": X,
               "subclass": "active" if mask == 1 else
                           ("inactive" if (mask & 1) == 0 and bin(mask).count("1") == 1
                            else "multi_word")}
        if "zero_mask_e" in h:
            any_zmask = True
            zm = h["zero_mask_e"]
            forced_bits = 0
            for j in (1, 2, 3):
                if mask & (1 << j):
                    for r in range(4):
                        forced_bits |= 1 << (4 * (((j + r) % 4 + 4) % 4) + r)
            if (forced_bits & ~zm) != 0:
                ok_forced = False
            Xz = bin(zm).count("1") - bin(forced_bits).count("1")
            row["X_from_zero_mask_e"] = Xz
            row["zero_mask_e"] = zm
            if Xz != X:
                ok_xmask = False
                row["x_mask_mismatch"] = True
        rows.append(row)
    checks = {"X_nonneg_all_hits": ok_x_nonneg,
              "forced_bytes_zero_where_logged": ok_forced}
    if any_zmask:
        checks["X_equals_zero_mask_e_derivation"] = ok_xmask
    return rows, checks


def class_rates(receipt):
    """Exact rational class rates + common-denominator integer numerators."""
    nontrivial = receipt["nontrivial_trials"]
    n_hit = receipt["W_ge1_nontrivial"]
    n_miss = nontrivial - n_hit
    assert n_miss == receipt["whist"][0], "n_miss mismatch vs whist[0]"
    assert sum(receipt["whist"]) == nontrivial, "whist sum mismatch"
    assert n_hit == sum(receipt["whist"][1:]), "W_ge1 mismatch vs whist tail"
    if n_miss == 0:
        raise ValueError("degenerate: no miss trials; H0-X undefined")
    ezdm, ezom = receipt["ezdiag_miss"], receipt["ezoff_miss"]
    p_diag = Fraction(ezdm, 4 * n_miss)
    p_off = Fraction(ezom, 12 * n_miss)
    p_naive = Fraction(NAIVE_NUM, NAIVE_DEN)
    D = lcm(lcm(NAIVE_DEN, 4 * n_miss), 12 * n_miss)
    assert D % NAIVE_DEN == 0 and D % p_diag.denominator == 0 and D % p_off.denominator == 0
    a_naive = D // NAIVE_DEN
    a_diag = p_diag.numerator * (D // p_diag.denominator)
    a_off = p_off.numerator * (D // p_off.denominator)
    assert Fraction(a_naive, D) == p_naive
    assert Fraction(a_diag, D) == p_diag
    assert Fraction(a_off, D) == p_off
    return {"n_hit": n_hit, "n_miss": n_miss,
            "p_diag": p_diag, "p_off": p_off, "p_naive": p_naive,
            "D": D, "a_naive": a_naive, "a_diag": a_diag, "a_off": a_off}


def byte_poly(D, a, n):
    """Integer coefficients of ((D-a) + a x)^n (pmf of n Bernoulli(a/D))."""
    poly = [1]
    for _ in range(n):
        nxt = [0] * (len(poly) + 1)
        for k, v in enumerate(poly):
            nxt[k] += v * (D - a)
            nxt[k + 1] += v * a
        poly = nxt
    return poly


def conv_int(p, q):
    out = [0] * (len(p) + len(q) - 1)
    for i, vi in enumerate(p):
        if vi == 0:
            continue
        for j, vj in enumerate(q):
            if vj:
                out[i + j] += vi * vj
    return out


def hit_pmf_int(mask, rates):
    """Integer pmf of X(h) over D^(4 + n_off); a_d by D0/D1 class."""
    D = rates["D"]
    a_d = rates["a_naive"] if (mask & 1) else rates["a_diag"]
    n_off = 4 * (3 - bin(mask & 0b1110).count("1"))
    diag = byte_poly(D, a_d, 4)
    off = byte_poly(D, rates["a_off"], n_off)
    return conv_int(diag, off), 4 + n_off


def exact_null(rows, rates):
    """Exact null distribution of S = sum X(h) for the given hit rows.

    Returns dict with integer pmf {k: int}, denominator D^B, and exact
    Fraction readings (p_extra/p_deficit at S_obs, mean, variance, tails).
    """
    D = rates["D"]
    pmf = [1]
    B = 0
    mean_num = 0
    var_num = 0
    for r in rows:
        hpmf, nb = hit_pmf_int(r["mask"], rates)
        pmf = conv_int(pmf, hpmf)
        md = rates["p_naive"] if (r["mask"] & 1) else rates["p_diag"]
        nd = 4
        no = nb - 4
        m1 = nd * md + no * rates["p_off"]
        m2 = nd * md * (1 - md) + no * rates["p_off"] * (1 - rates["p_off"])
        mean_num += m1
        var_num += m2
        B += nb
    DB = D ** B
    total = sum(pmf)
    assert total == DB, "pmf does not sum to denominator"
    S_obs = sum(r["X"] for r in rows)
    n = len(rows)
    cum_tail = [0] * (len(pmf) + 1)  # cum_tail[j] = sum_{k>=j} pmf[k]
    acc = 0
    for j in range(len(pmf) - 1, -1, -1):
        acc += pmf[j]
        cum_tail[j] = acc
    assert S_obs >= 0, "X >= 0 per-hit implies S >= 0"
    p_extra = Fraction(cum_tail[S_obs] if S_obs < len(pmf) else 0, DB)
    p_deficit = Fraction(sum(pmf[:S_obs + 1]), DB)
    mean = mean_num
    variance = var_num
    # realized-composition cutoff: smallest integer c with tail(c) <= 1/20
    cutoff = None
    for c in range(0, len(pmf)):
        if cum_tail[c] * 20 <= DB:
            cutoff = c
            break
    size_at_cutoff = None if cutoff is None else Fraction(cum_tail[cutoff], DB)
    tail_at_cutoff_minus_1 = None if cutoff in (None, 0) else Fraction(cum_tail[cutoff - 1], DB)
    return {
        "n_hits": n, "S_obs": S_obs, "total_bytes_B": B,
        "pmf_int": pmf, "den_int": DB, "cum_tail_int": cum_tail,
        "p_extra": p_extra, "p_deficit": p_deficit,
        "null_mean": mean, "null_variance": variance,
        "S_obs_above_null_mean": Fraction(S_obs) > mean,
        "cutoff_c": cutoff,
        "size_at_cutoff": size_at_cutoff,
        "tail_at_cutoff_minus_1": tail_at_cutoff_minus_1,
        "cutoff_gt_null_mean": None if cutoff is None else Fraction(cutoff) > mean,
    }


def tail_floats(null, lo, hi):
    """float64 tail probabilities P(S >= j) for j in [lo, hi] (exact->rounded)."""
    pmf, DB, cum = null["pmf_int"], null["den_int"], null["cum_tail_int"]
    out = {}
    for j in range(max(lo, 0), min(hi, len(pmf) - 1) + 1):
        out[j] = float(Fraction(cum[j], DB))
    for j in range(min(hi, len(pmf) - 1) + 1, hi + 1):
        out[j] = 0.0
    if lo < 0:
        for j in range(lo, 0):
            out[j] = 1.0
    return out


def pmf_floats_at(null, js):
    """float64 point probabilities P(S = j) for the requested j (exact->rounded)."""
    pmf, DB = null["pmf_int"], null["den_int"]
    out = {}
    for j in js:
        out[j] = float(Fraction(pmf[j], DB)) if 0 <= j < len(pmf) else 0.0
    return out
