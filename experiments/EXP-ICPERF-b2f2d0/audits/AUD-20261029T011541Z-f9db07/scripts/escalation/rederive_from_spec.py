#!/usr/bin/env python3
"""Escalation re-derivation for EXP-ICPERF-b2f2d0 (audit AUD-20261029T011541Z-f9db07).

A verification written under the audit directory; never a trial or run record.
Written from experiments/EXP-ICPERF-b2f2d0/specification.yaml text only. It does
not import or read run.py, check.py, the trial plan, RESULTS.md, or the sweep
reader's blind_rederive.py (the sweep script was read, as the dispatcher asked;
this file is written separately and shares no code with it).

Part 1  enumerate readings of the spec's sampler sentence, filter them with the
        spec's NON-numeric constraints only (no use of 2943/289567/28), then
        compute the survivors' statistics.
Part 2  shift-triple sensitivity: for every (a,b,c) in [1,31]^3 with the
        left/right/left form, compute the 64-draw statistics.  Answers two
        questions: do the frozen integers pin the triple, and do the two band
        "controls" separate a wrong xorshift from the frozen one?
Part 3  band acceptance under the canonical sampler on other seeds (control
        characterisation of the bands, not a trial of the hypothesis).
Part 4  optional: compare with a producer raw-result.json given as argv[1].

Spec-text facts used (specification.yaml):
  objective: "64 independent geometric counts with success probability 1/50
             from the frozen xorshift32 sampler at seed 20261017"
  formula:   "Draws use xorshift32 from seed 20261017 and stop when the state
             is divisible by 50."
  controls:  CV compared with population value sqrt(1 - 1/50), integer band
             [0.81,1.21] on CV^2; median/mean against ln 2, band [0.6,0.8]
  scale:     "Sixty-four draws at mean 50"
  invalid:   "a split between the two central order statistics invalidates"
  CV^2 formula in the spec: (n*Q - S^2)/S^2 (population variance / mean^2);
  median ratio: median*n/S.
"""
import json
import math
import sys
from fractions import Fraction

SEED, P_DEN, N = 20261017, 50, 64
MASK = (1 << 32) - 1
CAP = 1 << 16  # per-draw step cap; a draw that never stops marks the reading degenerate
#               (P[geometric(1/50) > 65536] = (49/50)^65536 ~ e^-1324, so no honest draw hits it)


def make_step(a, b, c):
    def step(x):
        x = (x ^ (x << a)) & MASK
        x = x ^ (x >> b)
        x = (x ^ (x << c)) & MASK
        return x
    return step


def draws(step, seed=SEED, order="step_then_test", count="trials", stream="continue",
          n=N, p_den=P_DEN):
    """Return list of n counts or None if degenerate (cap hit)."""
    out = []
    x = seed
    for i in range(n):
        if stream == "restart":
            x = seed
        k = 0
        if order == "step_then_test":
            while True:
                x = step(x)
                k += 1
                if x % p_den == 0:
                    break
                if k > CAP:
                    return None
        elif order == "test_then_step":          # seed itself is a tested state
            while True:
                k += 1
                if x % p_den == 0:
                    break
                x = step(x)
                if k > CAP:
                    return None
        elif order == "test_then_step_advance":  # as above, but advance past the stop
            while True:
                k += 1
                hit = (x % p_den == 0)
                x = step(x)
                if hit:
                    break
                if k > CAP:
                    return None
        else:
            raise ValueError(order)
        out.append(k if count == "trials" else k - 1)   # "failures" = trials - 1
    return out


def stats(d):
    n = len(d)
    S = sum(d)
    Q = sum(v * v for v in d)
    o = sorted(d)
    lo, hi = o[n // 2 - 1], o[n // 2]
    cv2 = Fraction(n * Q - S * S, S * S) if S else None
    mr = Fraction(lo * n, S) if S else None
    return {
        "sample_sum": S,
        "sum_squares": Q,
        "median": lo,
        "median_split": lo != hi,
        "cv2": float(cv2) if cv2 is not None else None,
        "cv_in_band": cv2 is not None and Fraction(81, 100) <= cv2 <= Fraction(121, 100),
        "median_ratio": float(mr) if mr is not None else None,
        "median_ratio_in_band": mr is not None and Fraction(3, 5) <= mr <= Fraction(4, 5),
        "sample_mean": S / n,
        "distinct_values": len(set(d)),
    }


def spec_constraints(d, count):
    """Non-numeric constraints read from the spec text. No frozen integer is used."""
    reasons = []
    if d is None:
        return ["degenerate: a draw never stopped"]
    if len(set(d)) == 1:
        reasons.append("'independent' violated: all 64 draws identical")
    if count == "failures":
        reasons.append("support {0,1,..}: population mean 49 and CV 1/sqrt(1-p), "
                       "contradicting spec 'mean 50' and control value sqrt(1 - 1/50)")
    if min(d) == 0 and count == "trials":
        reasons.append("zero count under trial-count support")
    # immediate-restop degeneracy: >=63 draws of size <=1 means the stream re-tests a stop state
    if sum(1 for v in d if v <= 1) >= N - 1:
        reasons.append("'independent' violated: stop state re-tested, draws 2..64 trivial")
    return reasons


def part1():
    step = make_step(13, 17, 5)
    rows = []
    for order in ("step_then_test", "test_then_step", "test_then_step_advance"):
        for count in ("trials", "failures"):
            for stream in ("continue", "restart"):
                d = draws(step, order=order, count=count, stream=stream)
                r = {"triple": [13, 17, 5], "order": order, "count": count, "stream": stream}
                r["excluded_by_spec_text"] = spec_constraints(d, count)
                r["stats"] = stats(d) if d is not None else None
                rows.append(r)
    return rows


def part2():
    canon = None
    total = nondeg = band_both = exact = 0
    exact_triples = []
    per_triple_sum = {}
    for a in range(1, 32):
        for b in range(1, 32):
            for c in range(1, 32):
                d = draws(make_step(a, b, c))
                total += 1
                if d is None or len(set(d)) == 1:
                    continue
                nondeg += 1
                s = stats(d)
                if s["cv_in_band"] and s["median_ratio_in_band"]:
                    band_both += 1
                if (s["sample_sum"], s["sum_squares"], s["median"]) == (2943, 289567, 28):
                    exact += 1
                    exact_triples.append([a, b, c])
                per_triple_sum[(a, b, c)] = s["sample_sum"]
                if (a, b, c) == (13, 17, 5):
                    canon = s
    sums = list(per_triple_sum.values())
    return {
        "triples_total": total,
        "triples_nondegenerate": nondeg,
        "nondegenerate_passing_both_bands": band_both,
        "band_pass_fraction": band_both / nondeg if nondeg else None,
        "triples_reproducing_2943_289567_28": exact,
        "exact_triples": exact_triples,
        "distinct_sample_sums_over_triples": len(set(sums)),
        "triples_with_sample_sum_2943": sum(1 for v in sums if v == 2943),
        "canonical_13_17_5": canon,
    }


def part3(n_seeds=2000):
    step = make_step(13, 17, 5)
    ok = cv_ok = mr_ok = split = joint = 0
    for s in range(1, n_seeds + 1):
        st = stats(draws(step, seed=s))
        cv_ok += st["cv_in_band"]
        mr_ok += st["median_ratio_in_band"]
        ok += st["cv_in_band"] and st["median_ratio_in_band"]
        split += st["median_split"]
        joint += st["cv_in_band"] and st["median_ratio_in_band"] and not st["median_split"]
    return {
        "seeds": f"1..{n_seeds}",
        "cv_band_pass_fraction": cv_ok / n_seeds,
        "median_ratio_band_pass_fraction": mr_ok / n_seeds,
        "both_bands_pass_fraction": ok / n_seeds,
        "median_split_fraction": split / n_seeds,
        "both_bands_and_no_split_fraction": joint / n_seeds,
        "population_reference": {
            "cv": math.sqrt(1 - 1 / P_DEN),
            "cv2": 1 - 1 / P_DEN,
            "median_trials_support": math.ceil(-math.log(2) / math.log(1 - 1 / P_DEN)),
            "ln2": math.log(2),
        },
    }


if __name__ == "__main__":
    which = set(sys.argv[2:]) or {"1", "2", "3"}
    out = {}
    if "1" in which:
        out["part1_readings"] = part1()
    if "2" in which:
        out["part2_triple_sweep"] = part2()
    if "3" in which:
        out["part3_band_acceptance_other_seeds"] = part3()
    if len(sys.argv) > 1 and sys.argv[1] != "-":
        claimed = json.load(open(sys.argv[1]))
        canon = stats(draws(make_step(13, 17, 5)))
        keys = ["sample_sum", "sum_squares", "median", "cv_in_band", "median_ratio_in_band"]
        out["part4_compare"] = {
            "mine": {k: canon[k] for k in keys},
            "claimed": {k: claimed.get(k) for k in keys},
            "equal": all(canon[k] == claimed.get(k) for k in keys),
        }
    json.dump(out, sys.stdout, indent=1, default=str)
    print()
