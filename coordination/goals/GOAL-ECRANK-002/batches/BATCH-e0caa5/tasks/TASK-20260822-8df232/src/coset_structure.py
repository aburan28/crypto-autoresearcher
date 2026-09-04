#!/usr/bin/env python3
"""
TASK-20260822-8df232 -- coset structure measurement on the committed
GOAL-ECRANK-001 pool (experiments/EXP-ECRANK-e1e30e).

Subcommands (each is one bounded "run" for the run-record harness):

  profile   Rank-profile every curve in SEEDS + the committed pool over a
            twist support, via PARI ellrank (twist_family_local.profile).
            This is the expensive PARI-bound stage; everything else is cheap
            numpy-free post-processing of its output.
  extend    Extend an existing profile to a larger support by adding primes.
            Reuses every class whose new-prime bits are all 0 (identical to
            the smaller support's class by construction: class_value with the
            extra bits unset multiplies in nothing new) and computes PARI
            ellrank only for the genuinely new classes. Self-checks the reuse
            on a sample before trusting it for the rest.
  analyze   From one or more profile files: (a) regression-fixture check
            against the committed best_sum_multiplicity_k3/k4/... metrics,
            (b) k=3/k=4 optima on the extended support, (c) the coset table
            (max single-class certified rank vs total per curve's own best
            k=3 coset), (d) the linear relation between recorded base rank
            and best k=3 total, solved for total=31.

No claim in this file's output is asserted certified unless it also appears
in a *_certified.json produced by verify_certs.py; everything else is
'uncertified' (PARI ellrank r_low + point count, exactly as scan_pool.py
computed it, not independently re-checked here) and is labelled as such in
every artifact this script writes.
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from twist_family_local import (  # noqa: E402
    profile as pari_profile, class_value, twist_rank, affine_subspaces, optimise,
    DEFAULT_SUPPORT,
)

REPO_ROOT = "/Volumes/SSD990/crypto-autoresearcher"
POOL_PATH = os.path.join(
    REPO_ROOT, "experiments/EXP-ECRANK-e1e30e/runs/RUN-ECRANK-e1e30e-001/pool.json"
)
# Byte-identical to source/scan_pool.py's seeds list.
SEEDS = [
    {"ai": [1, -1, 1, 0, 0], "rank": 1},
    {"ai": [0, 0, 1, -7, 6], "rank": 3},
    {"ai": [0, 1, 1, -2, 0], "rank": 2},
    {"ai": [1, -1, 0, -79, 289], "rank": 4},
    {"ai": [1, 1, 1, -2, 0], "rank": 3},
]

# Committed regression targets, from
# experiments/EXP-ECRANK-e1e30e/runs/RUN-ECRANK-e1e30e-001/manifest.yaml
COMMITTED_K3_SUM_MULT = 20
COMMITTED_K3_N_CLASSES = 8
COMMITTED_K4_SUM_MULT = 32
COMMITTED_K4_N_CLASSES = 16
COMMITTED_K5_SUM_MULT = 52
COMMITTED_K6_SUM_MULT = 88


def load_curves():
    pool = json.load(open(POOL_PATH))
    return SEEDS + pool


def cmd_profile(args):
    support = DEFAULT_SUPPORT
    curves = load_curves()
    t0 = time.time()
    out = []
    n_timeout_total = 0
    deadline = t0 + args.budget_seconds if args.budget_seconds else None
    stopped_early_at = None
    for i, c in enumerate(curves):
        if deadline and time.time() > deadline:
            stopped_early_at = i
            break
        ai = c["ai"]
        (A, B), prof = pari_profile(ai, support, args.time_limit)
        n_timeout_total += sum(1 for e in prof if e["timed_out"])
        out.append({"ai": ai, "recorded_rank": c.get("rank"), "A": A, "B": B, "profile": prof})
        if i % 25 == 0 or i == len(curves) - 1:
            print(
                "[%4d/%d %.0fs] n_timeout_total=%d"
                % (i, len(curves), time.time() - t0, n_timeout_total),
                flush=True,
            )
    result = {
        "support": support,
        "time_limit_s": args.time_limit,
        "n_curves_requested": len(curves),
        "n_curves_completed": len(out),
        "stopped_early_at_index": stopped_early_at,
        "wall_seconds": time.time() - t0,
        "n_timeout_total": n_timeout_total,
        "curves": out,
    }
    json.dump(result, open(args.out, "w"))
    print(
        "DONE %.0fs, %d/%d curves, %d timeouts"
        % (result["wall_seconds"], len(out), len(curves), n_timeout_total)
    )
    if stopped_early_at is not None:
        print(
            "BUDGET EXCEEDED: stopped at curve index %d of %d -- partial result only"
            % (stopped_early_at, len(curves))
        )


def cmd_extend(args):
    add_primes = [int(x) for x in args.add.split(",")]
    old = json.load(open(args.inp))
    support_old = old["support"]
    support_new = support_old + add_primes
    n_old = len(support_old)
    n_add = len(add_primes)
    t0 = time.time()
    out_curves = []
    n_new_calls = 0
    n_timeout_new = 0
    spot_checked = 0
    spot_check_failures = []
    deadline = t0 + args.budget_seconds if args.budget_seconds else None
    stopped_early_at = None
    for ci, rec in enumerate(old["curves"]):
        if deadline and time.time() > deadline:
            stopped_early_at = ci
            break
        A, B = rec["A"], rec["B"]
        old_prof = rec["profile"]
        assert len(old_prof) == (1 << n_old)
        new_prof = [None] * (1 << (n_old + n_add))
        for new_mask in range(1 << (n_old + n_add)):
            old_mask = new_mask & ((1 << n_old) - 1)
            extra_mask = new_mask >> n_old
            if extra_mask == 0:
                entry = old_prof[old_mask]
                # Self-check the reuse assumption on the first few curves:
                # recompute a couple of extra_mask==0 entries independently
                # and require exact agreement before trusting the rest.
                if ci < args.spot_check_curves and old_mask in (0, (1 << n_old) - 1):
                    d = class_value(old_mask, support_old)
                    assert d == entry["d"], (
                        "class_value mismatch on reuse: curve %d mask %d" % (ci, old_mask)
                    )
                    rl, rh, pts = twist_rank(A, B, d, args.time_limit)
                    spot_checked += 1
                    if (rl, rh, len(pts)) != (entry["r_low"], entry["r_high"], len(entry["points"])):
                        spot_check_failures.append(
                            {"curve_index": ci, "mask": old_mask,
                             "reused": [entry["r_low"], entry["r_high"], len(entry["points"])],
                             "recomputed": [rl, rh, len(pts)]}
                        )
                new_prof[new_mask] = entry
            else:
                d_old = class_value(old_mask, support_old)
                d_extra = class_value(extra_mask, add_primes)
                d = d_old * d_extra
                rl, rh, pts = twist_rank(A, B, d, args.time_limit)
                n_new_calls += 1
                if rl < 0:
                    n_timeout_new += 1
                new_prof[new_mask] = {
                    "mask": new_mask, "d": d, "r_low": rl, "r_high": rh, "points": pts,
                    "certified": min(rl, len(pts)) if rl >= 0 else 0,
                    "timed_out": rl < 0,
                }
        out_curves.append(
            {"ai": rec["ai"], "recorded_rank": rec["recorded_rank"], "A": A, "B": B, "profile": new_prof}
        )
        if ci % 25 == 0 or ci == len(old["curves"]) - 1:
            print(
                "[%4d/%d %.0fs] new_calls=%d new_timeouts=%d spot_check_failures=%d"
                % (ci, len(old["curves"]), time.time() - t0, n_new_calls, n_timeout_new,
                   len(spot_check_failures)),
                flush=True,
            )
    if spot_check_failures:
        # Fail loudly rather than silently trust a broken reuse: the class-transport
        # bug precedent in the handoff constraints is exactly this failure mode.
        json.dump(spot_check_failures, open(args.out + ".SPOT_CHECK_FAILURES.json", "w"))
        print("SPOT CHECK FAILED: %d mismatches, see %s.SPOT_CHECK_FAILURES.json"
              % (len(spot_check_failures), args.out))
        sys.exit(1)
    result = {
        "support": support_new,
        "extended_from_support": support_old,
        "added_primes": add_primes,
        "time_limit_s": args.time_limit,
        "n_curves_requested": len(old["curves"]),
        "n_curves_completed": len(out_curves),
        "stopped_early_at_index": stopped_early_at,
        "wall_seconds": time.time() - t0,
        "n_new_pari_calls": n_new_calls,
        "n_timeout_new": n_timeout_new,
        "n_spot_checks_passed": spot_checked - len(spot_check_failures),
        "curves": out_curves,
    }
    json.dump(result, open(args.out, "w"))
    print(
        "DONE %.0fs, %d/%d curves, %d new PARI calls, %d new timeouts, %d spot checks passed"
        % (result["wall_seconds"], len(out_curves), len(old["curves"]), n_new_calls,
           n_timeout_new, spot_checked)
    )
    if stopped_early_at is not None:
        print(
            "BUDGET EXCEEDED: stopped at curve index %d of %d -- partial result only"
            % (stopped_early_at, len(old["curves"]))
        )


def _optimise_all_curves(curves, support, k):
    """Per curve: this curve's own best k-coset by sum_mult. Returns list of
    dicts with the curve, its best coset (m0,V), the per-class certified ranks
    in that coset, the total, and the max single-class certified rank in it."""
    n = len(support)
    AS = affine_subspaces(n, k)
    rows = []
    global_best = (-1, None, None, None)
    for rec in curves:
        prof = rec["profile"]
        res = optimise(prof, support, k, index_cache=AS)
        score, m0, V = res["sum_mult"]
        coset_masks = sorted(m0 ^ v for v in V)
        per_class = [prof[m]["certified"] for m in coset_masks]
        per_class_d = [prof[m]["d"] for m in coset_masks]
        row = {
            "ai": rec["ai"],
            "recorded_rank": rec["recorded_rank"],
            "k": k,
            "coset_m0": m0,
            "coset_masks": coset_masks,
            "coset_classes_d": per_class_d,
            "per_class_certified": per_class,
            "total_sum_mult": score,
            "max_single_class_certified": max(per_class),
            "n_classes_with_point": sum(1 for x in per_class if x >= 1),
            "residual_other_classes": score - max(per_class),
        }
        rows.append(row)
        if score > global_best[0]:
            global_best = (score, rec["ai"], m0, V)
    return rows, global_best


def _linear_fit(xs, ys):
    """OLS y = a*x + b, plus R^2. No numpy dependency."""
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    if sxx == 0:
        return None
    a = sxy / sxx
    b = my - a * mx
    ss_tot = sum((y - my) ** 2 for y in ys)
    ss_res = sum((y - (a * x + b)) ** 2 for x, y in zip(xs, ys))
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else None
    return {"slope": a, "intercept": b, "r_squared": r2, "n_points": n}


def cmd_analyze(args):
    n7 = json.load(open(args.n7))
    curves7 = n7["curves"]
    support7 = n7["support"]

    # (a) regression fixture check, k = 3..6, matching manifest.yaml exactly.
    fixture = {}
    for k in (3, 4, 5, 6):
        rows, best = _optimise_all_curves(curves7, support7, k)
        n = len(support7)
        AS = affine_subspaces(n, k)
        # n_classes objective, computed the same way scan_pool.py did (separately
        # from sum_mult, since the two objectives can pick different cosets).
        best_cls = (-1, None)
        for rec in curves7:
            prof = rec["profile"]
            res = optimise(prof, support7, k, index_cache=AS)
            s2, m0c, Vc = res["n_classes"]
            if s2 > best_cls[0]:
                best_cls = (s2, rec["ai"])
        fixture["k%d" % k] = {
            "best_sum_mult": best[0], "best_sum_mult_curve": best[1],
            "best_n_classes": best_cls[0], "best_n_classes_curve": best_cls[1],
        }
    fixture_check = {
        "k3_sum_mult": {"committed": COMMITTED_K3_SUM_MULT, "measured": fixture["k3"]["best_sum_mult"],
                         "match": fixture["k3"]["best_sum_mult"] == COMMITTED_K3_SUM_MULT},
        "k3_n_classes": {"committed": COMMITTED_K3_N_CLASSES, "measured": fixture["k3"]["best_n_classes"],
                          "match": fixture["k3"]["best_n_classes"] == COMMITTED_K3_N_CLASSES},
        "k4_sum_mult": {"committed": COMMITTED_K4_SUM_MULT, "measured": fixture["k4"]["best_sum_mult"],
                         "match": fixture["k4"]["best_sum_mult"] == COMMITTED_K4_SUM_MULT},
        "k4_n_classes": {"committed": COMMITTED_K4_N_CLASSES, "measured": fixture["k4"]["best_n_classes"],
                          "match": fixture["k4"]["best_n_classes"] == COMMITTED_K4_N_CLASSES},
        "k5_sum_mult": {"committed": COMMITTED_K5_SUM_MULT, "measured": fixture["k5"]["best_sum_mult"],
                         "match": fixture["k5"]["best_sum_mult"] == COMMITTED_K5_SUM_MULT},
        "k6_sum_mult": {"committed": COMMITTED_K6_SUM_MULT, "measured": fixture["k6"]["best_sum_mult"],
                         "match": fixture["k6"]["best_sum_mult"] == COMMITTED_K6_SUM_MULT},
    }

    # (b) base-rank field consistency: pool 'rank' == profile[mask=0]['r_low'],
    # same alarm(3) time limit as search_pool.py used to produce it.
    mismatches = []
    for rec in curves7:
        r_low_at_1 = rec["profile"][0]["r_low"]
        if rec["recorded_rank"] is not None and r_low_at_1 != rec["recorded_rank"]:
            mismatches.append({"ai": rec["ai"], "recorded_rank": rec["recorded_rank"],
                                "r_low_at_class_1": r_low_at_1})

    # (c) coset table at k=3 on the committed (n=7) support: every curve's own
    # best k=3 coset, max single class vs total.
    coset_rows, _ = _optimise_all_curves(curves7, support7, 3)
    coset_rows.sort(key=lambda r: -r["total_sum_mult"])
    residuals = [r["residual_other_classes"] for r in coset_rows]
    residuals_sorted = sorted(residuals)
    n_res = len(residuals_sorted)
    residual_summary = {
        "n": n_res,
        "mean": sum(residuals) / n_res,
        "min": residuals_sorted[0],
        "max": residuals_sorted[-1],
        "median": residuals_sorted[n_res // 2],
        "stdev": (sum((x - sum(residuals) / n_res) ** 2 for x in residuals) / n_res) ** 0.5,
    }
    fit_total_vs_max = _linear_fit(
        [r["max_single_class_certified"] for r in coset_rows],
        [r["total_sum_mult"] for r in coset_rows],
    )

    # (d) relation between recorded base rank and k=3 total, solved for total=31.
    xs = [r["recorded_rank"] for r in coset_rows if r["recorded_rank"] is not None]
    ys = [r["total_sum_mult"] for r in coset_rows if r["recorded_rank"] is not None]
    fit_total_vs_baserank = _linear_fit(xs, ys)
    by_rank_bucket = {}
    for r in coset_rows:
        rr = r["recorded_rank"]
        by_rank_bucket.setdefault(rr, []).append(r["total_sum_mult"])
    bucket_summary = {
        str(k): {"n": len(v), "mean_total_k3": sum(v) / len(v), "min": min(v), "max": max(v)}
        for k, v in sorted(by_rank_bucket.items())
    }
    base_rank_required_for_31 = None
    if fit_total_vs_baserank and fit_total_vs_baserank["slope"] != 0:
        base_rank_required_for_31 = (31 - fit_total_vs_baserank["intercept"]) / fit_total_vs_baserank["slope"]
    observed_rank_domain = [min(xs), max(xs)] if xs else None

    result_n7 = {
        "support": support7,
        "fixture_check": fixture_check,
        "fixture_measured_all_k": fixture,
        "base_rank_field_consistency": {
            "n_curves_checked": len(curves7),
            "n_mismatches": len(mismatches),
            "mismatches": mismatches[:20],
        },
        "coset_table_k3": {
            "note": "uncertified: PARI ellrank r_low + exhibited-point count, not "
                    "independently re-verified in exact arithmetic for every row; "
                    "see certificates/ for the rows that are.",
            "n_curves": len(coset_rows),
            "top_20": coset_rows[:20],
            "bottom_5": coset_rows[-5:],
            "residual_other_classes_summary": residual_summary,
            "fit_total_vs_max_single_class": fit_total_vs_max,
        },
        "relation_base_rank_vs_k3_total": {
            "note": "recorded_rank is the pool/seed base rank at d=1 (untwisted), "
                    "taken from the committed record, not recomputed here; see "
                    "base_rank_field_consistency for the cross-check against this "
                    "profile's own class-1 r_low.",
            "linear_fit": fit_total_vs_baserank,
            "by_rank_bucket": bucket_summary,
            "observed_base_rank_domain": observed_rank_domain,
            "base_rank_required_for_k3_total_31": base_rank_required_for_31,
            "extrapolation_warning": (
                None if not observed_rank_domain else
                "requested point (total=31) requires base_rank=%.3f, which is %.3f "
                "units outside the observed domain %s -- extrapolation, not interpolation"
                % (base_rank_required_for_31, max(0, base_rank_required_for_31 - observed_rank_domain[1]),
                   observed_rank_domain)
            ) if base_rank_required_for_31 is not None and observed_rank_domain and
                 base_rank_required_for_31 > observed_rank_domain[1] else None,
        },
    }

    out = {"n7": result_n7}

    if args.n8:
        n8 = json.load(open(args.n8))
        curves8 = n8["curves"]
        support8 = n8["support"]
        ext_fixture = {}
        for k in (3, 4):
            rows, best = _optimise_all_curves(curves8, support8, k)
            n = len(support8)
            AS = affine_subspaces(n, k)
            best_cls = (-1, None)
            for rec in curves8:
                prof = rec["profile"]
                res = optimise(prof, support8, k, index_cache=AS)
                s2, m0c, Vc = res["n_classes"]
                if s2 > best_cls[0]:
                    best_cls = (s2, rec["ai"])
            ext_fixture["k%d" % k] = {
                "best_sum_mult": best[0], "best_sum_mult_curve": best[1],
                "best_n_classes": best_cls[0], "best_n_classes_curve": best_cls[1],
            }
        out["n8_extended_support"] = {
            "support": support8,
            "added_primes": n8["added_primes"],
            "optima": ext_fixture,
        }

    json.dump(out, open(args.out, "w"), indent=1)
    print("Wrote", args.out)
    print(json.dumps(fixture_check, indent=1))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    p1 = sub.add_parser("profile")
    p1.add_argument("--time-limit", type=int, default=3)
    p1.add_argument("--budget-seconds", type=float, default=0)
    p1.add_argument("--out", required=True)
    p1.set_defaults(func=cmd_profile)

    p2 = sub.add_parser("extend")
    p2.add_argument("--in", dest="inp", required=True)
    p2.add_argument("--add", required=True, help="comma-separated new primes, e.g. 17 or 17,19")
    p2.add_argument("--time-limit", type=int, default=3)
    p2.add_argument("--budget-seconds", type=float, default=0)
    p2.add_argument("--spot-check-curves", type=int, default=5)
    p2.add_argument("--out", required=True)
    p2.set_defaults(func=cmd_extend)

    p3 = sub.add_parser("analyze")
    p3.add_argument("--n7", required=True)
    p3.add_argument("--n8", default=None)
    p3.add_argument("--out", required=True)
    p3.set_defaults(func=cmd_analyze)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
