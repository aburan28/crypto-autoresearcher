#!/usr/bin/env python3
"""Stage 4 (zero compute) of EXP-PFDR-fd901a: flatness labels, rank-drop rates
with exact binomial intervals, the Semaev-minus-null table, the positive-control
table, the frozen-fixture record, tail checks and the censoring table -- every
number read back from runs/*/raw-result.json.  Writes analysis.md and
analysis.json; reports observations against the frozen criteria, never a
verdict about the hypothesis.

Usage: python3 experiments/EXP-PFDR-fd901a/analyze.py [--stop-check-only]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from fractions import Fraction
from math import comb
from typing import Dict, List, Optional, Tuple

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(HERE, "runs")
DEGREES = [3, 4, 5, 6]
FROZEN = {
    "flatness_min_identical": 38, "flatness_of": 40,
    "rank_drop_rate_max": 0.1,
    "posctrl_d_ff": {"4099": 65, "16411": 129},
    "semaev_minus_null_d_ff": -1,
    "e1e38b_semaev_d_ff": 5, "e1e38b_null_d_ff": 6, "e1e38b_semaev_fall_dim_at_d_ff": 4,
    "stop_rule_3_disagreement_fraction": 0.2,
}


def load_run(name: str) -> Optional[dict]:
    d = os.path.join(RUNS, name)
    if not os.path.isdir(d):
        return None
    with open(os.path.join(d, "raw-result.json")) as fh:
        raw = json.load(fh)
    with open(os.path.join(d, "manifest.yaml")) as fh:
        man = yaml.safe_load(fh)["run"]
    return {"raw": raw, "manifest": man, "id": name}


def binom_cdf(k: int, n: int, q: Fraction) -> Fraction:
    return sum(comb(n, i) * q**i * (1 - q) ** (n - i) for i in range(k + 1))


def clopper_pearson(k: int, n: int, alpha: float = 0.05) -> Tuple[float, float]:
    """Exact binomial 95% interval by bisection on the binomial CDF (no scipy)."""
    if n == 0:
        return (0.0, 1.0)
    a = Fraction(alpha) / 2

    def solve(target_fn, lo, hi):
        for _ in range(60):
            mid = (lo + hi) / 2
            if target_fn(mid):
                hi = mid
            else:
                lo = mid
        return float((lo + hi) / 2)

    lower = 0.0 if k == 0 else solve(lambda q: 1 - binom_cdf(k - 1, n, q) > a, Fraction(0), Fraction(1))
    upper = 1.0 if k == n else solve(lambda q: binom_cdf(k, n, q) < a, Fraction(0), Fraction(1))
    return (lower, upper)


INVARIANTS = ["full_rank", "top_rank", "fall_dim", "syzygy_dim", "deficit_series"]


def invariant_vector(draw: dict) -> Dict[str, object]:
    """Every graded invariant of one draw, keyed 'name@D', plus d_ff."""
    v: Dict[str, object] = {}
    for D in degrees_of(draw):
        rec = draw["per_layer"][str(D)]
        for name in INVARIANTS:
            v[f"{name}@{D}"] = rec[name]
    v["d_ff"] = draw["d_ff"]
    if "cumulative" in draw:
        for D in degrees_of(draw):
            v[f"cum_full_rank@{D}"] = draw["cumulative"][str(D)]["full_rank"]
            v[f"cum_deficit_series@{D}"] = draw["cumulative"][str(D)]["deficit_series"]
    return v


def key_of(d: dict) -> tuple:
    return (str(d["curve_seed"]), d["target_seed"], d.get("null_seed"))


def draws(run: dict, arm: str) -> List[dict]:
    return [d for d in run["raw"]["raw"]["draws"] if d["arm"] == arm and d.get("valid")]


def modal(values):
    vals = list(values)
    if not vals:
        return None
    return max(set(map(json.dumps, vals)), key=lambda s: sum(1 for v in vals if json.dumps(v) == s))


def degrees_of(d: dict) -> List[int]:
    return sorted(int(k) for k in d["per_layer"])


def profile(d: dict) -> tuple:
    return tuple((d["per_layer"][str(D)]["full_rank"], d["per_layer"][str(D)]["top_rank"]) for D in degrees_of(d))


def flatness(run_a: dict, run_b: dict, arm: str) -> dict:
    """Paired comparison (same curve seed, target seed, null seed) of every
    invariant between two primes, plus the modal-reference comparison."""
    A = {key_of(d): d for d in draws(run_a, arm)}
    B = {key_of(d): d for d in draws(run_b, arm)}
    keys = sorted(set(A) & set(B), key=str)
    out = {"paired_draws": len(keys), "per_invariant": {}, "all_invariants_identical_pairs": 0,
           "differing_pairs": []}
    all_same = 0
    for k in keys:
        va, vb = invariant_vector(A[k]), invariant_vector(B[k])
        same = va == vb
        all_same += same
        if not same:
            out["differing_pairs"].append({"key": [str(x) for x in k],
                                           "diff": {n: [va[n], vb[n]] for n in va if va[n] != vb[n]}})
    out["all_invariants_identical_pairs"] = all_same
    names = list(invariant_vector(A[keys[0]]).keys()) if keys else []
    for n in names:
        ident = sum(1 for k in keys if invariant_vector(A[k])[n] == invariant_vector(B[k])[n])
        out["per_invariant"][n] = {"identical_pairs": ident, "of": len(keys),
                                   "label": ("p-flat" if ident >= FROZEN["flatness_min_identical"] * len(keys) / FROZEN["flatness_of"] else "NOT p-flat")}
    modal_a = modal(profile(d) for d in A.values())
    modal_b = modal(profile(d) for d in B.values())
    out["modal_profile_a"] = json.loads(modal_a) if modal_a else None
    out["modal_profile_b"] = json.loads(modal_b) if modal_b else None
    out["draws_equal_to_own_mode_a"] = sum(1 for d in A.values() if json.dumps(profile(d)) == modal_a)
    out["draws_equal_to_own_mode_b"] = sum(1 for d in B.values() if json.dumps(profile(d)) == modal_b)
    return out


def rank_drop(run_small: dict, run_ref: dict, arm: str) -> dict:
    """Rank-drop events at the small prime against the reference (64-bit) modal
    profile: a draw with some full_rank(D) or top_rank(D) strictly below the
    reference; also 'any difference' events and the degree histogram."""
    ref = json.loads(modal(profile(d) for d in draws(run_ref, arm)))
    small = draws(run_small, arm)
    drops, diffs, by_degree = 0, 0, {str(D): 0 for D in DEGREES}
    events = []
    for d in small:
        pr = profile(d)
        is_drop = False
        for D, (fr, tr), (rf, rt) in zip(degrees_of(d), pr, ref):
            if fr < rf or tr < rt:
                is_drop = True
                by_degree[str(D)] += 1
        if is_drop:
            drops += 1
            events.append({"key": [str(x) for x in key_of(d)], "profile": [list(x) for x in pr]})
        if [list(x) for x in pr] != [list(x) for x in ref]:
            diffs += 1
    n = len(small)
    lo, hi = clopper_pearson(drops, n)
    return {"reference_modal_profile_64bit": ref, "draws": n, "rank_drop_events": drops,
            "rate": drops / n if n else None, "ci95_clopper_pearson": [lo, hi],
            "any_difference_events": diffs, "any_difference_fraction": diffs / n if n else None,
            "drops_by_degree": by_degree, "events": events}


def semaev_minus_null(run: dict) -> dict:
    S = draws(run, "semaev")
    N = draws(run, "null_support")
    out = {}
    names = list(invariant_vector(S[0]).keys())
    for n in names:
        ms = json.loads(modal(invariant_vector(d)[n] for d in S))
        mn = json.loads(modal(invariant_vector(d)[n] for d in N))
        out[n] = {"semaev_modal": ms, "null_modal": mn,
                  "difference": (ms - mn) if isinstance(ms, int) and isinstance(mn, int) else None,
                  "semaev_all_equal_mode": all(invariant_vector(d)[n] == ms for d in S),
                  "null_all_equal_mode": all(invariant_vector(d)[n] == mn for d in N)}
    return out


def arm_summary(run: dict, arm: str) -> dict:
    ds = draws(run, arm)
    if not ds:
        return {"draws": 0}
    profs = {}
    for d in ds:
        k = json.dumps([list(x) for x in profile(d)])
        profs[k] = profs.get(k, 0) + 1
    dff = {}
    for d in ds:
        dff[str(d["d_ff"])] = dff.get(str(d["d_ff"]), 0) + 1
    fd = {}
    for d in ds:
        k = json.dumps(d["profile_fall_dim"])
        fd[k] = fd.get(k, 0) + 1
    return {"draws": len(ds), "profile_histogram(full,top)@D3..6": profs, "d_ff_histogram": dff,
            "fall_dim_profile_histogram": fd,
            "deficit_series@3,4_modal": [json.loads(modal(d["per_layer"][str(degrees_of(ds[0])[0])]["deficit_series"] for d in ds)),
                                         json.loads(modal(d["per_layer"][str(degrees_of(ds[0])[1])]["deficit_series"] for d in ds))],
            "deficit_series_degrees": degrees_of(ds[0])[:2]}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stop-check-only", action="store_true")
    args = ap.parse_args()
    R = {name: load_run(f"RUN-PFDR-fd901a-{name}") for name in
         ["fixture-p4099", "posctrl-p4099", "posctrl-p16411", "sweep-p4099", "sweep-p64", "sweep-p256"]}
    present = {k: (v["manifest"]["status"] if v else "MISSING") for k, v in R.items()}

    result: Dict[str, object] = {"runs": present, "frozen_reference": FROZEN}

    # ---- stopping rule 3 check (Semaev at 4099 vs 64-bit: > 20% disagreement) ----
    if R["sweep-p4099"] and R["sweep-p64"]:
        rd = rank_drop(R["sweep-p4099"], R["sweep-p64"], "semaev")
        result["stop_rule_3"] = {"any_difference_fraction": rd["any_difference_fraction"],
                                 "threshold": FROZEN["stop_rule_3_disagreement_fraction"],
                                 "triggered": rd["any_difference_fraction"] > FROZEN["stop_rule_3_disagreement_fraction"]}
        if args.stop_check_only:
            print(json.dumps(result["stop_rule_3"]))
            return 0

    # ---- fixture ----
    if R["fixture-p4099"]:
        m = R["fixture-p4099"]["raw"]["metrics"]
        result["fixture"] = {k: m[k] for k in ["fixture_agrees", "stilde_coefficient_agreement", "rank_profile_agreement_all_D",
                                               "certificate_verified", "meter_profile_full_rank", "meter_profile_top_rank",
                                               "meter_d_ff", "meter_fall_dim", "curve_a", "curve_b", "x1", "x2", "x_R"]}
        result["fixture"]["per_degree"] = R["fixture-p4099"]["raw"]["raw"]["per_degree_comparison"]
        c = R["fixture-p4099"]["raw"]["raw"]["stage0_content_check"]
        result["stage0_content"] = {"content_D4": c["content_D4"], "n_entries_D4": c["n_entries_D4"],
                                    "max_param_degree": c["max_param_degree_per_entry"],
                                    "minor_degree_bound_2rD": c["minor_degree_bound_2rD"],
                                    "small_prime_specialisations": {q: {"samples": v["samples"], "equal_to_reference": v["equal_to_reference"]}
                                                                    for q, v in c["small_prime_specialisations"].items() if q != "reference_prime"},
                                    "reference": c["small_prime_specialisations"]["reference_prime"]}

    # ---- positive control ----
    pc = {}
    for p in ["4099", "16411"]:
        r = R[f"posctrl-p{p}"]
        if r:
            m = r["raw"]["metrics"]
            pc[p] = {"B": m["B"], "frozen_d_ff": FROZEN["posctrl_d_ff"][p],
                     "observed_d_ff_first_fall_histogram": m["d_ff_histogram"],
                     "observed_d_top_full_histogram": m["d_top_full_histogram"],
                     "series_d_reg": m["series_d_reg"], "draws": m["draw_count"],
                     "certificates_failed": m["planted_certificates_failed"]}
    if len(pc) == 2:
        dff = lambda p: sorted(int(k) for k in pc[p]["observed_d_ff_first_fall_histogram"])  # noqa: E731
        pc["strictly_increasing_first_fall"] = max(dff("4099")) < min(dff("16411"))
        pc["first_fall_equals_frozen"] = {p: dff(p) == [FROZEN["posctrl_d_ff"][p]] for p in ["4099", "16411"]}
        pc["d_top_full_equals_frozen"] = {p: sorted(int(k) for k in pc[p]["observed_d_top_full_histogram"]) == [FROZEN["posctrl_d_ff"][p]] for p in ["4099", "16411"]}
    result["positive_control"] = pc

    # ---- sweep ----
    sweep = {}
    for p in ["p4099", "p64", "p256"]:
        r = R[f"sweep-{p}"]
        if not r:
            continue
        sweep[p] = {"prime": r["raw"]["metrics"]["prime"], "status": r["manifest"]["status"],
                    "arms": {arm: arm_summary(r, arm) for arm in
                             ["semaev", "null_support", "noncurve_cubic", "secondary_direct_B8",
                              "semaev_named_p256", "null_support_named_p256", "semaev_named_p256_unplanted"]},
                    "certificates_failed": r["raw"]["metrics"]["planted_certificates_failed"],
                    "curve_rejections": r["raw"]["metrics"]["curve_rejections"],
                    "singular_rejections": r["raw"]["metrics"]["singular_rejections"],
                    "wall_seconds": r["manifest"]["timing"]["wall_seconds"],
                    "peak_rss_bytes": r["manifest"]["resources"]["peak_rss_bytes"]}
        sweep[p]["semaev_minus_null"] = semaev_minus_null(r)
        sec = draws(r, "secondary_direct_B8")
        if sec:
            sweep[p]["secondary_direct_B8"] = {"d_ff_histogram": arm_summary(r, "secondary_direct_B8")["d_ff_histogram"],
                                              "d_top_full": sorted({d["d_top_full"] for d in sec}),
                                              "series_d_reg": sorted({d["series_d_reg"] for d in sec}),
                                              "profile_fall_dim_D4..10_histogram": arm_summary(r, "secondary_direct_B8")["fall_dim_profile_histogram"]}
    result["sweep"] = sweep

    if R["sweep-p64"] and R["sweep-p256"]:
        result["flatness_64_vs_256"] = {arm: flatness(R["sweep-p64"], R["sweep-p256"], arm)
                                        for arm in ["semaev", "null_support", "noncurve_cubic", "secondary_direct_B8"]}
        s = result["flatness_64_vs_256"]["semaev"]
        result["criterion_3_semaev_flat"] = {"all_invariants_identical_pairs": s["all_invariants_identical_pairs"],
                                             "of": s["paired_draws"], "threshold": FROZEN["flatness_min_identical"],
                                             "met": s["all_invariants_identical_pairs"] >= FROZEN["flatness_min_identical"]}
    if R["sweep-p4099"] and R["sweep-p64"]:
        result["rank_drop_4099_vs_64"] = {arm: rank_drop(R["sweep-p4099"], R["sweep-p64"], arm)
                                          for arm in ["semaev", "null_support", "noncurve_cubic"]}
        rd = result["rank_drop_4099_vs_64"]["semaev"]
        result["criterion_4_rank_drop"] = {"rate": rd["rate"], "ci95": rd["ci95_clopper_pearson"],
                                           "threshold": FROZEN["rank_drop_rate_max"],
                                           "below_threshold": rd["rate"] < FROZEN["rank_drop_rate_max"]}
    if R["sweep-p64"] and R["sweep-p256"]:
        a = sweep["p64"]["semaev_minus_null"]
        b = sweep["p256"]["semaev_minus_null"]
        result["criterion_5_semaev_minus_null_same_at_both"] = {
            "same": all(a[n]["difference"] == b[n]["difference"] for n in a),
            "d_ff_difference_64": a["d_ff"]["difference"], "d_ff_difference_256": b["d_ff"]["difference"],
            "frozen_d_ff_difference": FROZEN["semaev_minus_null_d_ff"],
            "differing_invariants": [n for n in a if a[n]["difference"] != b[n]["difference"]]}
    # e1e38b cross-check
    xc = {}
    for p in sweep:
        r = R[f"sweep-{p}"]
        S = draws(r, "semaev")
        N = draws(r, "null_support")
        xc[p] = {"semaev_d_ff_histogram": arm_summary(r, "semaev")["d_ff_histogram"],
                 "semaev_fall_dim_at_5_histogram": {},
                 "null_d_ff_histogram": arm_summary(r, "null_support")["d_ff_histogram"],
                 "frozen": {"semaev_d_ff": 5, "null_d_ff": 6, "semaev_fall_dim_at_d_ff": 4}}
        for d in S:
            k = str(d["per_layer"]["5"]["fall_dim"])
            xc[p]["semaev_fall_dim_at_5_histogram"][k] = xc[p]["semaev_fall_dim_at_5_histogram"].get(k, 0) + 1
    result["e1e38b_cross_check"] = xc

    # tail checks
    tails = {}
    if "rank_drop_4099_vs_64" in result:
        rates = {arm: v["rate"] for arm, v in result["rank_drop_4099_vs_64"].items()}
        worst = max(rates, key=lambda a: rates[a])
        tails["highest_rank_drop_arm_at_4099"] = {"arm": worst, "rate": rates[worst],
                                                  "drops_by_degree": result["rank_drop_4099_vs_64"][worst]["drops_by_degree"]}
    if "flatness_64_vs_256" in result:
        tails["large_prime_deviating_draws"] = {arm: v["differing_pairs"] for arm, v in result["flatness_64_vs_256"].items()}
        for p in ["p64", "p256"]:
            r = R[f"sweep-{p}"]
            for arm in ["semaev", "null_support", "noncurve_cubic"]:
                ds = draws(r, arm)
                mode = modal(profile(d) for d in ds)
                dev = [{"key": [str(x) for x in key_of(d)], "profile": [list(x) for x in profile(d)]}
                       for d in ds if json.dumps(profile(d)) != mode]
                tails[f"off_mode_draws_{p}_{arm}"] = dev
    if R["sweep-p256"]:
        r = R["sweep-p256"]
        named = draws(r, "semaev_named_p256") or draws(r, "semaev_named_p256_unplanted")
        rnd = draws(r, "semaev")
        mode = modal(profile(d) for d in rnd)
        tails["named_p256_curve"] = {"named_curve": r["raw"]["raw"]["named_curve"] and
                                     {k: r["raw"]["raw"]["named_curve"][k] for k in ["window_x", "fallback_random_target"]},
                                     "arm": named[0]["arm"] if named else None,
                                     "profiles": [[list(x) for x in profile(d)] for d in named],
                                     "within_random_curve_mode": all(json.dumps(profile(d)) == mode for d in named),
                                     "random_curve_modal_profile": json.loads(mode),
                                     "d_ff": sorted({d["d_ff"] for d in named})}
    result["tail_checks"] = tails

    # censoring table
    result["censoring"] = {name: ("measured" if st == "completed_valid" else st) for name, st in present.items()}

    with open(os.path.join(HERE, "analysis.json"), "w") as fh:
        json.dump(result, fh, indent=1, sort_keys=True, default=str)
    write_markdown(result)
    print(json.dumps({k: result.get(k) for k in ["criterion_3_semaev_flat", "criterion_4_rank_drop",
                                                  "criterion_5_semaev_minus_null_same_at_both", "stop_rule_3"]}, indent=1))
    return 0


def write_markdown(res: dict) -> None:
    L: List[str] = []
    w = L.append
    w("# EXP-PFDR-fd901a -- Stage 4 analysis (observations only)")
    w("")
    w("Generated by `analyze.py` from `runs/*/raw-result.json`; every number below is")
    w("read back from a raw per-draw record (`analysis.json` holds the full tables).")
    w("This file reports measured values against the frozen criteria of the")
    w("specification as OBSERVATIONS. It states no verdict on H-PFDR-09e1b0; that")
    w("judgement belongs to the Reviewer and Coordinator.")
    w("")
    w("## Run status / censoring table")
    w("")
    w("| run | terminal status | reading |")
    w("|---|---|---|")
    for k, v in res["runs"].items():
        w(f"| RUN-PFDR-fd901a-{k} | {v} | {res['censoring'][k]} |")
    w("")
    if "fixture" in res:
        f = res["fixture"]
        w("## CTRL-FROZEN-FIXTURE (Stage 1)")
        w("")
        w(f"Instance: p = 4099, curve seed 1101 (A = {f['curve_a']}, B = {f['curve_b']}), target seed 1 "
          f"(x1 = {f['x1']}, x2 = {f['x2']}, x_R = {f['x_R']}). EXP-PFDR-5726af has no run, so the contract's "
          "fallback applies: an independent second implementation in the same run (sympy-built S~ from "
          "`harness.semaev.s3_expr`, dense Macaulay layers, sympy `DomainMatrix` rank over GF(p) and a naive elimination).")
        w("")
        w(f"- S~ coefficient-level agreement (meter vs sympy): **{f['stilde_coefficient_agreement']}**")
        w(f"- rank profile agreement at every D in 3..6: **{f['rank_profile_agreement_all_D']}**; planted certificate verified: {f['certificate_verified']}")
        w(f"- meter profile full_rank = {f['meter_profile_full_rank']}, top_rank = {f['meter_profile_top_rank']}, fall_dim = {f['meter_fall_dim']}, d_ff = {f['meter_d_ff']}")
        w("")
        w("| D | rows | cols | meter full/top | sympy full/top | naive full/top | agree |")
        w("|---|---|---|---|---|---|---|")
        for D, r in f["per_degree"].items():
            m, i = r["meter"], r["independent"]
            w(f"| {D} | {m['rows']} | {m['cols']} | {m['full_rank']}/{m['top_rank']} | {i['full_rank_sympy']}/{i['top_rank_sympy']} | {i['full_rank_naive']}/{i['top_rank_naive']} | {r['agree']} |")
        w("")
        c = res["stage0_content"]
        w("## Stage 0 content-prime check (from the fixture run)")
        w("")
        w(f"- D = 4 layer: {c['n_entries_D4']} nonzero entries of S~ over Z[A, B, x_R], maximal parameter degree {c['max_param_degree']}, integer content gcd = **{c['content_D4']}**")
        w(f"- minor-degree bound 2 r_D (r_D <= rows): {c['minor_degree_bound_2rD']}")
        w(f"- reference profile at 2^64 - 59 (uniform (A, B, x_R), 8 samples), (full, top) at D = 4, 5, 6: {c['reference']['modal_profile_D4_D5_D6']}")
        w("")
        w("| q | samples | equal to reference profile |")
        w("|---|---|---|")
        for q, v in sorted(c["small_prime_specialisations"].items(), key=lambda kv: int(kv[0])):
            w(f"| {q} | {v['samples']} | {v['equal_to_reference']} |")
        w("")
    if res.get("positive_control"):
        pc = res["positive_control"]
        w("## CTRL-POSITIVE-P-DEPENDENCE (Stage 2)")
        w("")
        w("| p | B | frozen d_ff | observed first-fall d_ff (histogram) | observed first D with top_rank = #monomials(D) | series d_reg | draws | cert failures |")
        w("|---|---|---|---|---|---|---|---|")
        for p in ["4099", "16411"]:
            if p in pc:
                v = pc[p]
                w(f"| {p} | {v['B']} | {v['frozen_d_ff']} | {v['observed_d_ff_first_fall_histogram']} | {v['observed_d_top_full_histogram']} | {v['series_d_reg']} | {v['draws']} | {v['certificates_failed']} |")
        w("")
        if "strictly_increasing_first_fall" in pc:
            w(f"- first-fall d_ff strictly increasing from 4099 to 16411: **{pc['strictly_increasing_first_fall']}**")
            w(f"- first-fall d_ff equal to the frozen integer (65 / 129): {pc['first_fall_equals_frozen']}")
            w(f"- first D with top_rank = #monomials(D) equal to the frozen integer (65 / 129): {pc['d_top_full_equals_frozen']}")
            w("")
            w("Reading recorded, not interpreted: under the contract's d_ff definition (first degree with")
            w("fall_dim > 0, per-layer, the same definition used for the Semaev arm) the control falls at")
            w("B + 2; the frozen integer B + 1 coincides with the degree at which the top block reaches")
            w("full column rank, which equals the series d_reg = B + 1 of IDEA-20260808-093497. Both")
            w("readings are reported; the frozen prediction is not adjusted.")
            w("")
    if res.get("sweep"):
        w("## Stage 3 sweep: per-arm summaries")
        w("")
        for p, s in res["sweep"].items():
            w(f"### {p} (p = {s['prime']}, status {s['status']}, wall {s['wall_seconds']} s, peak RSS {s['peak_rss_bytes']} bytes, certificate failures {s['certificates_failed']})")
            w("")
            w("| arm | draws | (full_rank, top_rank) at D = 3..6 (4..10 for the direct arm) : count | d_ff : count | fall_dim profile : count | deficit_series at D = 3, 4 (modal) |")
            w("|---|---|---|---|---|---|")
            for arm, a in s["arms"].items():
                if a["draws"] == 0:
                    continue
                w(f"| {arm} | {a['draws']} | {a['profile_histogram(full,top)@D3..6']} | {a['d_ff_histogram']} | {a['fall_dim_profile_histogram']} | {a['deficit_series@3,4_modal']} |")
            w("")
            if "secondary_direct_B8" in s:
                sd = s["secondary_direct_B8"]
                w(f"CTRL-SECONDARY-DIRECT-FIXED-B (B = 8, D = 4..10): d_ff {sd['d_ff_histogram']}, first D with full top rank {sd['d_top_full']}, series d_reg {sd['series_d_reg']}, fall_dim profiles {sd['profile_fall_dim_D4..10_histogram']}")
                w("")
            w(f"Curve rejection counts (random curves): {s['curve_rejections']}; singular cubics: {s['singular_rejections']}")
            w("")
    if "flatness_64_vs_256" in res:
        w("## p-flatness labels: 64-bit prime vs P-256 prime (paired by curve seed, target seed, null seed)")
        w("")
        for arm, f in res["flatness_64_vs_256"].items():
            w(f"### {arm}: {f['all_invariants_identical_pairs']} of {f['paired_draws']} pairs identical on EVERY invariant; "
              f"modal profile 64-bit {f['modal_profile_a']} ({f['draws_equal_to_own_mode_a']} draws), "
              f"P-256 {f['modal_profile_b']} ({f['draws_equal_to_own_mode_b']} draws)")
            w("")
            w("| invariant | identical pairs | of | label |")
            w("|---|---|---|---|")
            for n, v in f["per_invariant"].items():
                w(f"| {n} | {v['identical_pairs']} | {v['of']} | {v['label']} |")
            w("")
            if f["differing_pairs"]:
                w(f"Differing pairs: {json.dumps(f['differing_pairs'])}")
                w("")
        c3 = res["criterion_3_semaev_flat"]
        w(f"Frozen criterion (3): Semaev-arm invariants identical at the two large primes in at least {c3['threshold']} of {c3['of']} draws. "
          f"Observed: {c3['all_invariants_identical_pairs']} of {c3['of']} pairs identical on every invariant -> condition {'MET' if c3['met'] else 'NOT MET'} (observation).")
        w("")
    if "rank_drop_4099_vs_64" in res:
        w("## Rank-drop events at p = 4099 against the 64-bit modal profile")
        w("")
        w("| arm | draws | rank-drop events (some rank strictly below reference) | rate | exact 95% CI | any-difference events | drops by degree |")
        w("|---|---|---|---|---|---|---|")
        for arm, v in res["rank_drop_4099_vs_64"].items():
            w(f"| {arm} | {v['draws']} | {v['rank_drop_events']} | {v['rate']:.4f} | [{v['ci95_clopper_pearson'][0]:.4f}, {v['ci95_clopper_pearson'][1]:.4f}] | {v['any_difference_events']} | {v['drops_by_degree']} |")
        w("")
        c4 = res["criterion_4_rank_drop"]
        w(f"Frozen criterion (4): rank-drop rate at 4099 below {c4['threshold']} per draw. Observed Semaev-arm rate {c4['rate']:.4f}, "
          f"exact 95% CI [{c4['ci95'][0]:.4f}, {c4['ci95'][1]:.4f}] -> below threshold: {c4['below_threshold']} (observation). "
          "Stage 0 Schwartz-Zippel bound for uniform (A, B, x_R): 2 r_D / p <= 30 / 4099 = 0.0073 at D = 6.")
        w("")
        if "stop_rule_3" in res:
            w(f"Stopping rule 3 check after the 64-bit run: Semaev 4099-vs-64-bit any-difference fraction {res['stop_rule_3']['any_difference_fraction']:.4f} "
              f"(threshold {res['stop_rule_3']['threshold']}) -> triggered: {res['stop_rule_3']['triggered']}")
            w("")
    if res.get("sweep"):
        w("## Semaev minus NULL-SUPPORT, per invariant (modal values), at each prime")
        w("")
        for p, s in res["sweep"].items():
            w(f"### {p}")
            w("")
            w("| invariant | Semaev modal | null modal | difference | Semaev all draws = mode | null all draws = mode |")
            w("|---|---|---|---|---|---|")
            for n, v in s["semaev_minus_null"].items():
                w(f"| {n} | {v['semaev_modal']} | {v['null_modal']} | {v['difference']} | {v['semaev_all_equal_mode']} | {v['null_all_equal_mode']} |")
            w("")
        if "criterion_5_semaev_minus_null_same_at_both" in res:
            c5 = res["criterion_5_semaev_minus_null_same_at_both"]
            w(f"Frozen criterion (5): the Semaev-minus-null table is the same at both large primes. Observed: same = **{c5['same']}** "
              f"(differing invariants: {c5['differing_invariants']}). d_ff difference: 64-bit {c5['d_ff_difference_64']}, P-256 {c5['d_ff_difference_256']}, "
              f"frozen cross-check value (IDEA-20260903-e1e38b D5 via H-PFDR-4148b8) {c5['frozen_d_ff_difference']}.")
            w("")
    if res.get("e1e38b_cross_check"):
        w("## IDEA-20260903-e1e38b cross-check (frozen: Semaev d_ff = 5 with fall_dim(5) = 4; null d_ff = 6)")
        w("")
        w("| prime | Semaev d_ff histogram | Semaev fall_dim(5) histogram | null d_ff histogram |")
        w("|---|---|---|---|")
        for p, v in res["e1e38b_cross_check"].items():
            w(f"| {p} | {v['semaev_d_ff_histogram']} | {v['semaev_fall_dim_at_5_histogram']} | {v['null_d_ff_histogram']} |")
        w("")
    if res.get("tail_checks"):
        t = res["tail_checks"]
        w("## Tail checks")
        w("")
        if "highest_rank_drop_arm_at_4099" in t:
            w(f"- Highest rank-drop arm at 4099: {t['highest_rank_drop_arm_at_4099']}")
        if "large_prime_deviating_draws" in t:
            w(f"- Draws at a large prime whose paired 64/256 invariants differ: {json.dumps(t['large_prime_deviating_draws'])}")
        for k, v in t.items():
            if k.startswith("off_mode_draws_"):
                w(f"- {k}: {json.dumps(v)}")
        if "named_p256_curve" in t:
            w(f"- CTRL-NAMED-CURVE (NIST P-256): {json.dumps(t['named_p256_curve'])}")
        w("")
    w("## CTRL-CONFOUNDERS-NAMED")
    w("")
    w("(i) CRT / complete-splitting artifact (IDEA-20260830-cb8e46): only generator-level rank profiles are read; no ideal-level invariant appears. "
      "(ii) Output-degree proxy (IDEA-20260807-899c5e): no Groebner basis is computed anywhere in this package; every number is an exact graded rank.")
    w("")
    w("## Outcome labels of the contract, stated as observation")
    w("")
    items = []
    if "fixture" in res:
        items.append(f"(1) frozen fixture agrees exactly: {res['fixture']['fixture_agrees']}")
    if res.get("positive_control", {}).get("strictly_increasing_first_fall") is not None:
        pc = res["positive_control"]
        items.append(f"(2) positive control d_ff = 65 and 129 under the first-fall definition: {pc['first_fall_equals_frozen']}; strictly increasing: {pc['strictly_increasing_first_fall']}; "
                     f"top-block-full-rank degree = 65 and 129: {pc['d_top_full_equals_frozen']}")
    if "criterion_3_semaev_flat" in res:
        items.append(f"(3) Semaev invariants identical at 64-bit and P-256 in >= 38 of 40: {res['criterion_3_semaev_flat']['met']}")
    if "criterion_4_rank_drop" in res:
        items.append(f"(4) rank-drop rate at 4099 below 0.1: {res['criterion_4_rank_drop']['below_threshold']} (rate {res['criterion_4_rank_drop']['rate']}, CI {res['criterion_4_rank_drop']['ci95']})")
    if "criterion_5_semaev_minus_null_same_at_both" in res:
        items.append(f"(5) Semaev-minus-null table identical at both large primes: {res['criterion_5_semaev_minus_null_same_at_both']['same']}")
    for it in items:
        w(f"- {it}")
    w("")
    w("These are the contract's own predefined labels evaluated on the measured integers. Whether they")
    w("constitute outcome O1, O2 or an instrument outcome is for the review round to decide.")
    with open(os.path.join(HERE, "analysis.md"), "w") as fh:
        fh.write("\n".join(L) + "\n")


if __name__ == "__main__":
    sys.exit(main())
