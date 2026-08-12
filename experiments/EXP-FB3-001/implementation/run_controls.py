"""EXP-FB3-001 controls run: counter verification and H016/H017 port fidelity.

Four control blocks, all reported before any family verdict:

  A. counter verification -- the exact counters are checked against literal
     brute-force enumeration of multisets/typed tuples on small cases, with
     WHOLE COUNT VECTOR equality (not just the total);
  B. conservation control -- the exact total equals the closed form for every
     typing pattern, over structured and random bases at several sizes, and the
     FFT route's rounding margin is measured at the largest N used;
  C. auxiliary-machinery control -- greedy incremental sumsets against
     brute force, the two height computations against each other, and the
     small-multiples log-space claim on a real curve;
  D. port fidelity -- the recorded H016/H017 cell statistics in
     inputs/h100_session/h016_base_yield.json are re-derived: internal
     consistency of the recorded statistics, exact recomputation of the recorded
     curve orders, and reproduction of the recorded sampled means from exact
     count vectors through the recorded 800-target sampling protocol.

Usage:  python3 run_controls.py --out <raw-result.json>
"""

from __future__ import annotations

import argparse
import itertools
import json
import platform
import resource
import sys
import time
from datetime import datetime, timezone

import numpy as np
import sympy

import fb3_core as C
from run_battery import jsonable, now_iso, peak_mb

H016_PATH = "../../../inputs/h100_session/h016_base_yield.json"
SAMPLING_MC_REPS = 400


# --------------------------------------------------------------------------
# A. counter verification against brute force
# --------------------------------------------------------------------------

def control_counter_verification(log) -> dict:
    cases = []
    small_orders = [211, 307, 401, 503, 1009]
    rng = np.random.default_rng(20260724)
    for n_order in small_orders:
        for b in (5, 8, 13, 20):
            logs = C.distinct_logs(rng, n_order, b)
            ref = C.brute_force_counts(n_order, logs)
            burn = C.counts_untyped_m3(n_order, logs)
            direct = C.counts_untyped_m3_direct(n_order, logs)
            fft, err = C.counts_untyped_m3_fft(n_order, logs)
            cases.append({
                "kind": "untyped_multiset3", "N": n_order, "B": b,
                "logs": logs.tolist(),
                "brute_force_total": int(ref.sum()),
                "closed_form_total": C.total_untyped_m3(b),
                "vector_equal_burnside": bool(np.array_equal(ref, burn)),
                "vector_equal_direct": bool(np.array_equal(ref, direct)),
                "vector_equal_fft": bool(np.array_equal(ref, fft)),
                "n_targets_compared": int(ref.size),
                "fft_max_abs_rounding_deviation": err,
                "max_count": int(ref.max()),
            })
    # structured (highly additive) small bases: the adversarial case for counters
    for n_order in (211, 1009):
        for logs in ([1, 2, 3, 4, 5, 6, 7], list(range(1, 21)),
                     [1, 2, 4, 8, 16, 32, 64, 128],
                     [n_order - 1, n_order - 2, 1, 2, 3]):
            arr = np.array(sorted(set(int(v) % n_order for v in logs)), dtype=np.int64)
            ref = C.brute_force_counts(n_order, arr)
            burn = C.counts_untyped_m3(n_order, arr)
            direct = C.counts_untyped_m3_direct(n_order, arr)
            fft, err = C.counts_untyped_m3_fft(n_order, arr)
            cases.append({
                "kind": "untyped_multiset3_structured", "N": n_order,
                "B": int(arr.size), "logs": arr.tolist(),
                "brute_force_total": int(ref.sum()),
                "closed_form_total": C.total_untyped_m3(int(arr.size)),
                "vector_equal_burnside": bool(np.array_equal(ref, burn)),
                "vector_equal_direct": bool(np.array_equal(ref, direct)),
                "vector_equal_fft": bool(np.array_equal(ref, fft)),
                "n_targets_compared": int(ref.size),
                "fft_max_abs_rounding_deviation": err,
                "max_count": int(ref.max()),
            })
    # typed counters
    for n_order in (211, 401, 1009):
        for sizes in ((4, 3, 5), (7, 2, 2), (10, 6, 4)):
            subs = C.random_disjoint_sub_bases(n_order, list(sizes), rng)
            ref = C.brute_force_typed_111(n_order, *subs)
            got = C.counts_typed_111(n_order, *subs)
            cases.append({
                "kind": "typed_111", "N": n_order, "sizes": list(sizes),
                "brute_force_total": int(ref.sum()),
                "closed_form_total": sizes[0] * sizes[1] * sizes[2],
                "vector_equal": bool(np.array_equal(ref, got)),
                "n_targets_compared": int(ref.size),
            })
        for b1, b2 in ((6, 5), (9, 3), (4, 11)):
            s1, s2 = C.random_disjoint_sub_bases(n_order, [b1, b2], rng)
            ref = C.brute_force_typed_1_2(n_order, s1, s2)
            got = C.counts_typed_1_2(n_order, s1, s2)
            cases.append({
                "kind": "typed_1_2", "N": n_order, "sizes": [b1, b2],
                "brute_force_total": int(ref.sum()),
                "closed_form_total": b1 * b2 * (b2 + 1) // 2,
                "vector_equal": bool(np.array_equal(ref, got)),
                "n_targets_compared": int(ref.size),
            })
    flags = []
    for c in cases:
        flags.extend([v for k, v in c.items() if k.startswith("vector_equal")])
        flags.append(c["brute_force_total"] == c["closed_form_total"])
    verdict = "pass" if all(flags) else "FAIL"
    log(f"A. counter verification: {len(cases)} cases, "
        f"{len(flags)} vector/total assertions -> {verdict}")
    return {"verdict": verdict, "n_cases": len(cases), "n_assertions": len(flags),
            "all_true": bool(all(flags)), "cases": cases,
            "note": "agreement is on the FULL per-target count vector over all N "
                    "targets, not only on the total"}


# --------------------------------------------------------------------------
# B. conservation / closed-form control at working scale
# --------------------------------------------------------------------------

def control_conservation(log) -> dict:
    checks = []
    rng = np.random.default_rng(11)
    for bits in (14, 16, 18):
        cv = C.find_curve(bits, 1, 1 << bits)
        n_order = cv.n_order
        b = C.matched_size(n_order)
        expected = C.total_untyped_m3(b)
        bases = {
            "matched_random": C.random_base(n_order, b, rng),
            "high_bit_interval": C.geom_high_bit_interval(cv, b)["logs"],
            "small_height": C.geom_small_height(cv, b)["logs"],
            "coset_union": C.geom_coset_union(cv, b)["logs"],
            "small_multiples": C.geom_small_multiples(cv, b)["logs"],
        }
        for name, logs in bases.items():
            cnt = C.counts_untyped_m3(n_order, logs)
            fft, err = C.counts_untyped_m3_fft(n_order, logs)
            st = C.cell_stats(cnt)
            checks.append({
                "bits": bits, "N": n_order, "B": b, "base": name,
                "exact_total": int(cnt.sum()), "closed_form_total": expected,
                "total_ok": bool(int(cnt.sum()) == expected),
                "exact_mean": st["mean"],
                "closed_form_mean": expected / n_order,
                "mean_matches_closed_form": bool(
                    abs(st["mean"] - expected / n_order) < 1e-12),
                "coverage": st["coverage"], "max_count": st["max_count"],
                "coverage_le_min_1_mean": bool(
                    st["coverage"] <= min(1.0, st["mean"]) + 1e-12),
                "equality_iff_no_double": bool(
                    (abs(st["coverage"] - st["mean"]) < 1e-12)
                    == (st["max_count"] <= 1)),
                "fft_vector_equal": bool(np.array_equal(cnt, fft)),
                "fft_max_abs_rounding_deviation": err,
            })
        for w in C.FROZEN["asym_ladder_weights"]:
            b1, b2, b3 = C.asym_split_sizes(b, w)
            subs = C.random_disjoint_sub_bases(n_order, [b1, b2, b3], rng)
            cnt = C.counts_typed_111(n_order, *subs)
            checks.append({
                "bits": bits, "N": n_order, "B": b, "base": f"typed_111/{w}",
                "sizes": [b1, b2, b3],
                "exact_total": int(cnt.sum()), "closed_form_total": b1 * b2 * b3,
                "total_ok": bool(int(cnt.sum()) == b1 * b2 * b3),
                "typed_le_B3_over_27": bool(b1 * b2 * b3 <= b ** 3 / 27 + 1e-9),
                "typed_over_untyped": (b1 * b2 * b3) / expected,
            })
    ok = all(c["total_ok"] for c in checks)
    extra = all(c.get("coverage_le_min_1_mean", True)
                and c.get("equality_iff_no_double", True)
                and c.get("fft_vector_equal", True) for c in checks)
    verdict = "pass" if (ok and extra) else "FAIL"
    log(f"B. conservation/closed-form control: {len(checks)} checks -> {verdict}")
    return {"verdict": verdict, "n_checks": len(checks), "checks": checks,
            "max_fft_rounding_deviation": max(
                [c.get("fft_max_abs_rounding_deviation", 0.0) for c in checks])}


# --------------------------------------------------------------------------
# C. auxiliary machinery: greedy sumsets, height equivalence, small multiples
# --------------------------------------------------------------------------

def brute_sigma(n_order: int, logs, m: int) -> set[int]:
    return {sum(t) % n_order
            for t in itertools.combinations_with_replacement(list(map(int, logs)), m)}


def control_machinery(log) -> dict:
    out: dict = {}

    # C1. greedy incremental sumsets vs brute force, step by step
    n_order = 1009
    rng = np.random.default_rng(3)
    pool = C.distinct_logs(rng, n_order, 40)
    train, held = C.greedy_split(n_order, 777)
    train_bits = C.bits_from_indices(np.flatnonzero(train), n_order)
    b = 10
    sel = C.greedy_select(n_order, pool, train_bits, b)
    step_checks = []
    for k in range(1, b + 1):
        prefix = sel["selection_order"][:k]
        s2 = brute_sigma(n_order, prefix, 2)
        s3 = brute_sigma(n_order, prefix, 3)
        step_checks.append({"k": k, "sigma2_brute": len(s2), "sigma3_brute": len(s3)})
    final_cnt = C.counts_untyped_m3(n_order, sel["logs"])
    reach = set(np.flatnonzero(final_cnt > 0).tolist())
    brute_reach = brute_sigma(n_order, sel["logs"], 3)
    # exhaustive check that greedy's first choice maximised the training gain
    first_gains = {}
    for d in map(int, pool):
        first_gains[d] = int(train[(3 * d) % n_order])
    best_first = max(first_gains.values())
    out["greedy"] = {
        "N": n_order, "B": b, "pool": int(pool.size),
        "sigma3_from_counts_equals_brute": bool(reach == brute_reach),
        "sigma3_size": len(brute_reach),
        "internal_sigma3_size_at_stop": sel["sigma3_size_at_stop"],
        "internal_matches_brute": bool(sel["sigma3_size_at_stop"] == len(brute_reach)),
        "internal_train_covered": sel["train_targets_covered_at_stop"],
        "brute_train_covered": int(sum(train[list(brute_reach)])),
        "train_cover_matches": bool(sel["train_targets_covered_at_stop"]
                                    == int(sum(train[list(brute_reach)]))),
        "first_gain_is_max": bool(sel["marginal_gains"][0] == best_first),
        "step_sizes": step_checks,
        "monotone_gains": bool(all(x >= 0 for x in sel["marginal_gains"])),
        "leakage_structural_guard": ("greedy_select() has no access to the "
                                     "held-out mask; only train_bits is passed"),
        "held_out_untouched_check": bool(
            (C.bits_from_indices(np.flatnonzero(held), n_order) & train_bits) == 0),
    }
    out["greedy"]["verdict"] = "pass" if (
        out["greedy"]["sigma3_from_counts_equals_brute"]
        and out["greedy"]["internal_matches_brute"]
        and out["greedy"]["train_cover_matches"]
        and out["greedy"]["first_gain_is_max"]
        and out["greedy"]["held_out_untouched_check"]) else "FAIL"

    # C2. height: enumerated minimum over representations vs continued fractions
    cv = C.find_curve(14, 1, 1 << 14)
    p = cv.p
    h_max = 64
    hmap = C.height_map_enumerated(p, h_max)
    disagree = []
    for x in range(p):
        cf = C.height_cf(x, p)
        en = hmap.get(x)
        if cf <= h_max:
            if en is None or en != cf:
                disagree.append({"x": x, "cf": cf, "enumerated": en})
        elif en is not None:
            disagree.append({"x": x, "cf": cf, "enumerated": en})
    out["height_equivalence"] = {
        "p": p, "h_max": h_max, "x_values_checked": p,
        "n_with_height_le_h_max": len(hmap),
        "n_disagreements": len(disagree),
        "disagreements_sample": disagree[:5],
        "verdict": "pass" if not disagree else "FAIL",
        "note": "the enumerated minimum over all coprime (u,v) with max(|u|,|v|) "
                "<= h_max agrees with the continued-fraction convergent minimum "
                "for every x in [0,p) on this curve",
    }

    # C3. small-multiples base is the log-space initial segment {1..B}
    b14 = C.matched_size(cv.n_order)
    sm = C.geom_small_multiples(cv, b14)
    out["small_multiples_log_space"] = {
        "B": b14, "is_initial_segment": sm["is_initial_segment"],
        "pool_before_truncate": sm["pool_before_truncate"],
        "verdict": "pass" if sm["is_initial_segment"] else "FAIL",
        "note": "dedup-by-x of x(jG), j=1..2B is a no-op in log space for "
                "2B < N/2, so the H017 base is {1,...,B}: this makes the H017 "
                "geometry exactly reproducible from the recorded convention "
                "without knowing G",
    }
    log(f"C. machinery control: greedy={out['greedy']['verdict']} "
        f"height={out['height_equivalence']['verdict']} "
        f"small_mult={out['small_multiples_log_space']['verdict']}")
    out["verdict"] = ("pass" if all(out[k]["verdict"] == "pass"
                                    for k in ("greedy", "height_equivalence",
                                              "small_multiples_log_space"))
                     else "FAIL")
    return out


# --------------------------------------------------------------------------
# D. port fidelity against the recorded H016/H017 statistics
# --------------------------------------------------------------------------

def sampled_mean_band(counts: np.ndarray, n_targets: int, reps: int,
                      rng) -> np.ndarray:
    n_order = counts.size
    idx = rng.integers(0, n_order, size=(reps, n_targets))
    return counts[idx].mean(axis=1)


def control_port_fidelity(log) -> dict:
    with open(H016_PATH) as fh:
        rec = json.load(fh)
    rng = np.random.default_rng(916016)
    cells = []
    for entry in rec["sizes"]:
        p, a, b_coef = entry["p"], entry["a"], entry["b"]
        n_order, base_b = entry["N"], entry["B"]
        n_tg = entry["n_targets"]
        # D1 exact order recomputation from the recorded curve parameters
        order = C.curve_order_char_sum(p, a, b_coef)
        lo, hi = C.hasse_interval(p)
        # D2 closed-form mean
        closed_mean = C.total_untyped_m3(base_b) / n_order
        # D3 internal consistency of the recorded statistics
        qr = entry["bases"]["qr"]
        sm = entry["bases"]["small_mult"]
        rd = entry["bases"]["random"]
        nulls = np.array(entry["perm_null"]["null_means"], dtype=np.float64)
        internal = {
            "qr_total_equals_mean_times_n": bool(
                abs(qr["total"] - qr["mean_per_target"] * n_tg) < 1e-9),
            "qr_counts_sum_equals_total": bool(sum(qr["counts"]) == qr["total"]),
            "sm_counts_sum_equals_total": bool(sum(sm["counts"]) == sm["total"]),
            "random_counts_sum_equals_total": bool(sum(rd["counts"]) == rd["total"]),
            "qr_ratio_recomputed": qr["mean_per_target"] / rd["mean_per_target"],
            "qr_ratio_recorded": entry["qr_vs_random"]["ratio"],
            "sm_ratio_recomputed": sm["mean_per_target"] / rd["mean_per_target"],
            "sm_ratio_recorded": entry["sm_vs_random"]["ratio"],
            "mean_band_recomputed": [float(np.percentile(nulls, 2.5)),
                                     float(np.percentile(nulls, 97.5))],
            "mean_band_recorded": entry["perm_null"]["mean_band_95"],
            "qr_emp_p_recomputed_raw_fraction": float(np.count_nonzero(
                np.abs(nulls - nulls.mean())
                >= abs(qr["mean_per_target"] - nulls.mean()) - 1e-15) / nulls.size),
            "qr_emp_p_recomputed_h016_convention": C.empirical_p_h016(
                qr["mean_per_target"], nulls),
            "qr_emp_p_recorded": entry["perm_null"]["qr_emp_p_two_sided"],
            "identified_recorded_pvalue_convention":
                "2 * min(#{null >= obs}, #{null <= obs}) / n",
            "theory_mean_recorded": entry["theory_mean_triples_per_target"],
            "theory_mean_recomputed": closed_mean,
        }
        internal["ratios_match"] = bool(
            abs(internal["qr_ratio_recomputed"] - internal["qr_ratio_recorded"]) < 1e-9
            and abs(internal["sm_ratio_recomputed"] - internal["sm_ratio_recorded"]) < 1e-9)
        internal["bands_match"] = bool(np.allclose(internal["mean_band_recomputed"],
                                                   internal["mean_band_recorded"],
                                                   rtol=0, atol=1e-9))
        internal["theory_mean_matches"] = bool(
            abs(internal["theory_mean_recorded"] - closed_mean) < 1e-12)
        internal["pvalue_convention_reproduced"] = bool(
            abs(internal["qr_emp_p_recomputed_h016_convention"]
                - internal["qr_emp_p_recorded"]) < 1e-12)
        # D4 exact recomputation of the H017 small-multiples base ({1..B})
        sm_logs = np.arange(1, base_b + 1, dtype=np.int64)
        sm_counts = C.counts_untyped_m3(n_order, sm_logs)
        sm_exact = C.cell_stats(sm_counts)
        sm_band = sampled_mean_band(sm_counts, n_tg, SAMPLING_MC_REPS, rng)
        # D5 matched-random reconstruction, exact counts + recorded sampling
        rand_means, rand_cov, rand_sampled = [], [], []
        for _ in range(100):
            rb = C.random_base(n_order, base_b, rng)
            cnt = C.counts_untyped_m3(n_order, rb)
            st = C.cell_stats(cnt)
            rand_means.append(st["mean"])
            rand_cov.append(st["coverage"])
            rand_sampled.append(sampled_mean_band(cnt, n_tg, 20, rng))
        rand_sampled = np.concatenate(rand_sampled)
        # D6 QR walk, same-family reconstruction (walk RNG not recorded)
        qr_recon: dict = {"attempted": False}
        try:
            cv_full = _rebuild_recorded_curve(p, a, b_coef, n_order)
            qw = C.geom_qr_walk(cv_full, base_b, seed=4242)
            qcnt = C.counts_untyped_m3(n_order, qw["logs"])
            qst = C.cell_stats(qcnt)
            qband = sampled_mean_band(qcnt, n_tg, SAMPLING_MC_REPS, rng)
            qr_recon = {
                "attempted": True, "walk_steps": qw["steps"],
                "exact_stats": qst,
                "sampled_mean_band_95": [float(np.percentile(qband, 2.5)),
                                         float(np.percentile(qband, 97.5))],
                "recorded_qr_mean": qr["mean_per_target"],
                "recorded_inside_reconstructed_band": bool(
                    np.percentile(qband, 2.5) <= qr["mean_per_target"]
                    <= np.percentile(qband, 97.5)),
                "bit_exact_replay_possible": False,
                "why": ("the recorded conventions do not pin the walk's RNG "
                        "stream, index function, or start point, so only a "
                        "same-family distributional comparison is possible"),
            }
        except Exception as exc:                       # noqa: BLE001
            qr_recon = {"attempted": True, "error": repr(exc)}
        sm_lo, sm_hi = float(np.percentile(sm_band, 2.5)), float(np.percentile(sm_band, 97.5))
        rs_lo, rs_hi = (float(np.percentile(rand_sampled, 2.5)),
                        float(np.percentile(rand_sampled, 97.5)))
        cell = {
            "recorded_bits": entry["bits"], "p": p, "a": a, "b": b_coef,
            "recorded_N": n_order, "recorded_B": base_b, "n_targets": n_tg,
            "order_recomputed": order,
            "order_matches_recorded": bool(order == n_order),
            "order_prime": bool(sympy.isprime(n_order)),
            "order_in_hasse_interval": bool(lo <= n_order <= hi),
            "internal_consistency": internal,
            "small_multiples_exact": {
                "logs_are_initial_segment": True,
                "exact_stats": sm_exact,
                "closed_form_total": C.total_untyped_m3(base_b),
                "total_ok": bool(int(sm_counts.sum()) == C.total_untyped_m3(base_b)),
                "sampled_mean_band_95": [sm_lo, sm_hi],
                "recorded_sampled_mean": sm["mean_per_target"],
                "recorded_inside_band": bool(sm_lo <= sm["mean_per_target"] <= sm_hi),
                "n_nonzero_targets_exact": int(np.count_nonzero(sm_counts)),
                "recorded_nonzero_in_sample": int(sum(1 for v in sm["counts"] if v)),
                "expected_nonzero_in_sample": float(
                    n_tg * np.count_nonzero(sm_counts) / n_order),
                "recorded_max_count": int(max(sm["counts"])),
                "exact_max_count": int(sm_counts.max()),
                "recorded_max_le_exact_max": bool(max(sm["counts"]) <= int(sm_counts.max())),
            },
            "matched_random_reconstruction": {
                "n_bases": 100,
                "exact_mean_is_constant": bool(len(set(np.round(rand_means, 12))) == 1),
                "exact_mean": float(np.mean(rand_means)),
                "closed_form_mean": closed_mean,
                "exact_coverage_mean": float(np.mean(rand_cov)),
                "sampled_mean_band_95": [rs_lo, rs_hi],
                "recorded_random_mean": rd["mean_per_target"],
                "recorded_random_inside_band": bool(rs_lo <= rd["mean_per_target"] <= rs_hi),
                "recorded_qr_mean": qr["mean_per_target"],
                "recorded_qr_inside_band": bool(rs_lo <= qr["mean_per_target"] <= rs_hi),
                "recorded_perm_null_band": entry["perm_null"]["mean_band_95"],
                "band_overlaps_recorded_perm_null": bool(
                    rs_lo <= entry["perm_null"]["mean_band_95"][1]
                    and entry["perm_null"]["mean_band_95"][0] <= rs_hi),
            },
            "qr_walk_reconstruction": qr_recon,
            "prior_cell_pvalues_derived_from_record": {
                "qr_two_sided_recorded": entry["perm_null"]["qr_emp_p_two_sided"],
                "qr_two_sided_convention_r_plus_1": C.empirical_p(
                    qr["mean_per_target"], nulls)["p"],
                "qr_two_sided_h016_convention": C.empirical_p_h016(
                    qr["mean_per_target"], nulls),
                "small_mult_two_sided_convention_r_plus_1": C.empirical_p(
                    sm["mean_per_target"], nulls)["p"],
                "small_mult_two_sided_h016_convention": C.empirical_p_h016(
                    sm["mean_per_target"], nulls),
                "qr_mean": qr["mean_per_target"],
                "small_mult_mean": sm["mean_per_target"],
                "random_mean": rd["mean_per_target"],
                "null_mean": float(nulls.mean()),
                "n_null_draws": int(nulls.size),
                "derivation": ("derived from the recorded perm_null.null_means "
                               "and the recorded base means; the record itself "
                               "stores an explicit p-value only for the QR cell, "
                               "under the identified 2*min(tail)/n convention"),
            },
        }
        checks = [cell["order_matches_recorded"], cell["order_prime"],
                  cell["order_in_hasse_interval"], internal["ratios_match"],
                  internal["bands_match"], internal["theory_mean_matches"],
                  internal["pvalue_convention_reproduced"],
                  internal["qr_total_equals_mean_times_n"],
                  internal["qr_counts_sum_equals_total"],
                  internal["sm_counts_sum_equals_total"],
                  internal["random_counts_sum_equals_total"],
                  cell["small_multiples_exact"]["total_ok"],
                  cell["small_multiples_exact"]["recorded_inside_band"],
                  cell["small_multiples_exact"]["recorded_max_le_exact_max"],
                  cell["matched_random_reconstruction"]["recorded_random_inside_band"],
                  cell["matched_random_reconstruction"]["recorded_qr_inside_band"],
                  cell["matched_random_reconstruction"]["band_overlaps_recorded_perm_null"]]
        cell["n_checks"] = len(checks)
        cell["n_failed"] = int(sum(1 for v in checks if not v))
        cell["verdict"] = "pass" if all(checks) else "FAIL"
        log(f"D. port fidelity bits={entry['bits']} p={p}: {cell['verdict']} "
            f"(order {order} vs recorded {n_order}; "
            f"{cell['n_checks'] - cell['n_failed']}/{cell['n_checks']} checks)")
        cells.append(cell)
    verdict = "pass" if all(c["verdict"] == "pass" for c in cells) else "PARTIAL"
    return {"verdict": verdict, "source": "inputs/h100_session/h016_base_yield.json",
            "recorded_conventions": rec["conventions"],
            "sampling_reconstruction": {
                "protocol": f"{rec['sizes'][0]['n_targets']} uniform targets per "
                            "curve, same set for all bases (recorded convention)",
                "replacement_assumption": "with replacement; the record does not "
                                          "state which, and the finite-population "
                                          "correction for 800 of >= 8329 targets "
                                          "is under 5% of the band width",
                "mc_reps": SAMPLING_MC_REPS},
            "cells": cells}


def _rebuild_recorded_curve(p: int, a: int, b: int, n_order: int) -> C.Curve:
    """Rebuild the dlog table for a recorded H016 curve (G not recorded)."""
    isqr = C.qr_table(p)
    gx = gy = None
    for x in range(1, p):
        v = (x * x * x + a * x + b) % p
        if v == 0 or not isqr[v]:
            continue
        y = int(sympy.sqrt_mod(v, p))
        gx, gy = x, min(y, p - y)
        break
    xs, ys = C._enumerate_multiples(p, a, n_order, gx, gy)
    log_of_x = np.zeros(p, dtype=np.int64)
    canon = (2 * ys[1:n_order]) < p
    idx = np.flatnonzero(canon) + 1
    log_of_x[xs[idx]] = idx
    return C.Curve(bits=int(np.log2(p)) + 1, curve_index=0, seed=0, p=p, a=a, b=b,
                   n_order=n_order, tries=0, window_rejects=0, order_rejects=0,
                   gx=gx, gy=gy, xs=xs, log_of_x=log_of_x)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    started = now_iso()
    t0 = time.time()
    lines: list[str] = []

    def log(msg: str) -> None:
        print(msg, flush=True)
        lines.append(msg)

    log("=== EXP-FB3-001 controls run (counter verification + port fidelity) ===")
    log(f"started_at {started}")
    a = control_counter_verification(log)
    b = control_conservation(log)
    c = control_machinery(log)
    d = control_port_fidelity(log)
    wall = time.time() - t0
    out = {
        "run_id": "RUN-FB3-001-CTRL",
        "experiment_id": "EXP-FB3-001",
        "amendment_id": "EXP-FB3-001-AMD-001",
        "purpose": "counter verification against brute force, conservation and "
                   "closed-form controls, auxiliary-machinery controls, and "
                   "H016/H017 port fidelity",
        "controls": {
            "A_counter_verification": a,
            "B_conservation_closed_form": b,
            "C_auxiliary_machinery": c,
            "D_port_fidelity": d,
        },
        "control_verdicts": {"A": a["verdict"], "B": b["verdict"],
                             "C": c["verdict"], "D": d["verdict"]},
        "timing": {"started_at": started, "finished_at": now_iso(),
                   "wall_clock_seconds": wall},
        "peak_memory_mb": peak_mb(),
        "environment": {"python": platform.python_version(),
                        "numpy": np.__version__, "sympy": sympy.__version__,
                        "platform": platform.platform()},
    }
    with open(args.out, "w") as fh:
        json.dump(out, fh, indent=1, default=jsonable)
    log(f"verdicts: {json.dumps(out['control_verdicts'])}")
    log(f"wrote {args.out}")
    log(f"wall_clock_seconds {wall:.1f} peak_memory_mb {peak_mb():.1f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
