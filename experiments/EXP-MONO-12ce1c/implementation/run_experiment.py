#!/usr/bin/env python3
"""
EXP-MONO-12ce1c orchestrator. Runs Stage 0 through Stage 4 exactly in the
order specification.yaml `stage_order_and_the_terminating_stage` declares,
and writes raw-result.json to the given run directory.

Usage: python3 run_experiment.py <seed> <run_dir>
"""
import sys
import os
import json
import time
import hashlib
import math
import platform
from fractions import Fraction as F

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from seed import Drawer
from fields import Fp2, build_sqrt_table, legendre
from curve import factor_base, find_same_order_curve, ConstructionFailure
from panel import build_panel, PANEL_DOMAIN
from path1 import (
    build_base_points, enumerate_signed_sums, observed_permutation,
    predicted_permutation, sign_keys, cycle_type,
)
from semaev_path2 import SemaevPath2, s3_vanishes_at_sum_and_difference
from sublocus import signed_sum_x_coords, collision_count
from controls import positive_control_1, chebotarev_check, positive_control_2_planted, measured_null_1_cross_curve

STAGE2_N = 20000
STAGE3_N = 20000
DUALPATH_N = 2000
QUARTIC_N = 20000
PLANTED_N = 1000
CROSSCURVE_N = 5000

M4_STAGE3_MS = [4, 5]


def now_iso():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def stage0_check():
    """Zero-compute symbolic identity + 105-curve evaluation.
    Loads the 105 curves' (p, trace_t, Z) from RUN-MONO-4b50b6-002's own
    committed raw-result.json (v3_trace_formula block)."""
    import sympy as sp
    p, t, Z = sp.symbols("p t Z")
    S_expr = (p - t - Z) / 2
    Nns_expr = (p + t - Z) / 2
    freq_split_new = (S_expr ** 2 + Nns_expr ** 2 - (p - Z)) / p ** 2
    committed_delta = (t ** 2 - 2 * p * Z + Z ** 2 - 2 * p + 2 * Z) / (2 * p ** 2)
    symbolic_diff = sp.simplify(freq_split_new - sp.Rational(1, 2) - committed_delta)
    identity_holds = (symbolic_diff == 0)

    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    src = os.path.join(repo_root, "experiments", "EXP-MONO-4b50b6", "runs",
                        "RUN-MONO-4b50b6-002", "raw-result.json")
    with open(src) as fh:
        d = json.load(fh)
    v3 = d["v3_trace_formula"]
    n_curves = 0
    max_abs_diff = F(0)
    per_curve = []
    for pstr, lst in v3.items():
        pp = int(pstr)
        for rec in lst:
            tt = rec["trace_t"]
            ZZ = rec["Z"]
            S = F(pp - tt - ZZ, 2)
            Nns = F(pp + tt - ZZ, 2)
            freq_new = (S ** 2 + Nns ** 2 - (pp - ZZ)) / F(pp ** 2)
            committed_delta_val = F(tt ** 2 - 2 * pp * ZZ + ZZ ** 2 - 2 * pp + 2 * ZZ, 2 * pp ** 2)
            freq_old = F(1, 2) + committed_delta_val
            diff = freq_new - freq_old
            n_curves += 1
            if abs(diff) > max_abs_diff:
                max_abs_diff = abs(diff)
            per_curve.append({"p": pp, "trace_t": tt, "Z": ZZ, "diff_exact_fraction": str(diff)})
    all_agree = (max_abs_diff == 0)
    return {
        "identity_symbolic_diff": str(symbolic_diff),
        "identity_holds": bool(identity_holds),
        "source_105_curves": src,
        "n_curves_evaluated": n_curves,
        "max_abs_diff_exact_fraction": str(max_abs_diff),
        "all_105_curves_agree": bool(all_agree),
        "gate_pass": bool(identity_holds and all_agree),
        "per_curve_sample_first_5": per_curve[:5],
    }


def stage2_cell(F, A, B, p, m, domain, n_trials):
    drawer = Drawer(domain, "spec-x", p, m)
    keys = sign_keys(m)
    n_ramified = 0
    n_diagonal = 0
    n_infinity = 0
    n_nondistinct_roots = 0
    n_no_frobenius_match = 0
    n_admissible = 0
    m1_violations = 0
    m2_matches = 0
    n_split_complete = 0
    A_fp2 = F.from_fp(A)
    n_root = 2 ** (m - 2)
    identity_type = tuple([1] * n_root)
    pure2_type = tuple([2] * (n_root // 2))
    for _ in range(n_trials):
        xs = [drawer.draw(p) for _ in range(m - 1)]
        if len(set(xs)) < len(xs):
            n_diagonal += 1
            continue
        fs = [(x * x * x + A * x + B) % p for x in xs]
        if any(f == 0 for f in fs):
            n_ramified += 1
            continue
        base_points = build_base_points(F, A, B, p, xs)
        chis = [c for _, c in base_points]
        roots = enumerate_signed_sums(F, A_fp2, base_points)
        perm, anomalies = observed_permutation(F, roots)
        if perm is None:
            if "infinity" in anomalies:
                n_infinity += 1
            elif "nondistinct_roots" in anomalies:
                n_nondistinct_roots += 1
            elif "no_frobenius_match" in anomalies:
                n_no_frobenius_match += 1
            continue
        n_admissible += 1
        ct = cycle_type(perm, keys)
        if ct != identity_type and ct != pure2_type:
            m1_violations += 1
        if ct == identity_type:
            n_split_complete += 1
        pred = predicted_permutation(keys, chis)
        if perm == pred:
            m2_matches += 1
    return {
        "n_trials": n_trials, "n_ramified": n_ramified, "n_diagonal": n_diagonal,
        "n_infinity_anomaly": n_infinity, "n_nondistinct_roots_anomaly": n_nondistinct_roots,
        "n_no_frobenius_match_anomaly": n_no_frobenius_match,
        "n_admissible": n_admissible,
        "M1_violations": m1_violations,
        "M2_matches": m2_matches,
        "M2_fraction": (m2_matches / n_admissible) if n_admissible else float("nan"),
        "n_split_complete": n_split_complete,
        "M3_measured": (n_split_complete / n_admissible) if n_admissible else float("nan"),
    }


def m3_forced_split_freq(p, trace, Z):
    S = F(p - trace - Z, 2)
    Nns = F(p + trace - Z, 2)
    m = 3
    return float((S ** (m - 1) + Nns ** (m - 1)) / F(p ** (m - 1)))


def mN_forced_split_freq(p, trace, Z, m):
    S = F(p - trace - Z, 2)
    Nns = F(p + trace - Z, 2)
    return float((S ** (m - 1) + Nns ** (m - 1)) / F(p ** (m - 1)))


def stage3_cell(F, A, B, p, N, tau, m, sign_convention, domain, fb, n_trials):
    A_fp2 = F.from_fp(A)
    drawer = Drawer(domain, "fb-x", p, m)
    n_fb = len(fb)
    ds = []
    n_valid = 0
    n_degenerate_draw = 0
    for _ in range(n_trials):
        idxs = []
        tries = 0
        while len(idxs) < (m - 1) and tries < 200:
            i = drawer.draw(n_fb)
            tries += 1
            if i in idxs:
                continue
            idxs.append(i)
        if len(idxs) < (m - 1):
            n_degenerate_draw += 1
            continue
        points_xy = [fb[i] for i in idxs]
        xcoords = signed_sum_x_coords(F, A_fp2, points_xy)
        D = collision_count(xcoords)
        ds.append(D)
        n_valid += 1
    mean_d = sum(ds) / len(ds) if ds else float("nan")
    if len(ds) > 1:
        var = sum((d - mean_d) ** 2 for d in ds) / (len(ds) - 1)
        se = math.sqrt(var / len(ds))
    else:
        se = float("nan")
    at_least_one = sum(1 for d in ds if d >= 1) / len(ds) if ds else float("nan")
    if m == 4:
        forced_e_d = 6 * (tau - 1) / N
    elif m == 5:
        forced_e_d = 16 * tau / N + 24 * (tau - 1) / N
    else:
        forced_e_d = None
    sigma = abs(mean_d - forced_e_d) / se if (se and se > 0 and forced_e_d is not None) else float("nan")
    return {
        "sign_convention": sign_convention, "n_trials": n_trials, "n_valid": n_valid,
        "n_degenerate_draw": n_degenerate_draw,
        "mean_D": mean_d, "D_std_error": se, "P_at_least_one_collision": at_least_one,
        "forced_E_D": forced_e_d, "sigma_deviation": sigma,
        "max_D_observed": max(ds) if ds else None,
        "D_histogram": {str(k): ds.count(k) for k in sorted(set(ds))} if ds else {},
    }


def main():
    seed = int(sys.argv[1])
    run_dir = sys.argv[2]
    os.makedirs(run_dir, exist_ok=True)
    t_start_wall = time.time()
    started_at = now_iso()

    result = {"seed": seed, "started_at": started_at}

    # ---------------- STAGE 0 ----------------
    stage0 = stage0_check()
    result["stage0"] = stage0
    if not stage0["gate_pass"]:
        result["TERMINATED_AT_STAGE0"] = True
        result["finished_at"] = now_iso()
        with open(os.path.join(run_dir, "raw-result.json"), "w") as fh:
            json.dump(result, fh, indent=2, default=str)
        print("STAGE 0 FAILED -- terminating, no further compute spent.")
        return

    # ---------------- STAGE 1 ----------------
    result["stage1"] = {
        "performed": False,
        "reason": "no network access in this execution environment; permitted by "
                  "specification.yaml budget.no_network_note.",
    }

    # ---------------- PANEL CONSTRUCTION ----------------
    panel = build_panel()
    result["panel"] = panel
    tau_ok = panel["tau_coverage_met"]

    sampling_domain = f"{PANEL_DOMAIN}/run-{seed}"
    result["domains"] = {"panel_domain": PANEL_DOMAIN, "sampling_domain": sampling_domain}

    curves = panel["curves"]
    curve_by_role = {c["role"]: c for c in curves}

    fp2_cache = {}
    sqrt_table_cache = {}

    def get_F(p):
        if p not in fp2_cache:
            fp2_cache[p] = Fp2(p)
        return fp2_cache[p]

    def get_sqrt_table(p):
        if p not in sqrt_table_cache:
            sqrt_table_cache[p] = build_sqrt_table(p)
        return sqrt_table_cache[p]

    # ---------------- FACTOR BASE PER CURVE ----------------
    factor_bases = {}
    for c in curves:
        role, p, A, B = c["role"], c["p"], c["A"], c["B"]
        sqt = get_sqrt_table(p)
        fb_fixed, digest_fixed, excl_fixed = factor_base(PANEL_DOMAIN, A, B, p, 0, "fixed", sqt)
        factor_bases[role] = {"fixed": {"fb": fb_fixed, "digest": digest_fixed, "excluded_zero": excl_fixed}}
        for m in M4_STAGE3_MS:
            fb_rand, digest_rand, excl_rand = factor_base(sampling_domain, A, B, p, m, "random", sqt)
            factor_bases[role][f"random_m{m}"] = {"fb": fb_rand, "digest": digest_rand, "excluded_zero": excl_rand}

    result["factor_base_digests"] = {
        role: {k: v["digest"] for k, v in d.items()} for role, d in factor_bases.items()
    }
    result["factor_base_sizes"] = {
        role: {k: len(v["fb"]) for k, v in d.items()} for role, d in factor_bases.items()
    }

    # ---------------- STAGE 4 CONTROLS + NULLS (committed BEFORE treatment) ----------------
    stage4 = {}

    # positive control 1: use the largest panel prime (p11, RO... none directly at p11;
    # reuse J0/J1728's prime p9=421's field is small; use the 11-bit prime via a throwaway
    # curve-free quartic test -- quartics need only a prime, not a curve)
    p_pc1 = panel["primes"]["p11"]
    pc1_raw = positive_control_1(sampling_domain, p_pc1, QUARTIC_N)
    pc1_check = chebotarev_check(pc1_raw["histogram"], pc1_raw["n_admissible"])
    pc1_pass = all(v["within_3_sigma"] for v in pc1_check.values()) and \
        pc1_raw["histogram"]["4"] > 0 and pc1_raw["histogram"]["3+1"] > 0
    stage4["positive_control_1"] = {"prime": p_pc1, "raw": pc1_raw, "chebotarev_check": pc1_check,
                                     "pass": pc1_pass}

    # positive control 2: planted collision, on every tau>=2 curve, m in {4,5}
    pc2_results = {}
    for c in curves:
        if c["tau"] < 2:
            continue
        role = c["role"]
        pc2_results[role] = {}
        for m in M4_STAGE3_MS:
            fb = factor_bases[role]["fixed"]["fb"]
            r = positive_control_2_planted(sampling_domain, c["p"], c["A"], c["B"], fb, m, PLANTED_N)
            pc2_results[role][f"m{m}"] = r
    pc2_pass = all(
        r["detection_rate"] == 1.0 for role in pc2_results for r in pc2_results[role].values()
        if r["n_valid"] > 0
    )
    stage4["positive_control_2_planted"] = {"per_curve": pc2_results, "pass": pc2_pass}

    # measured null 1: cross-curve, on RO3 + a same-order companion curve
    ro3 = curve_by_role["RO3"]
    Ap, Bp = find_same_order_curve(ro3["p"], ro3["A"], ro3["B"], ro3["N"])
    null1_raw = measured_null_1_cross_curve(sampling_domain, ro3["p"], ro3["A"], ro3["B"], Ap, Bp, CROSSCURVE_N)
    stage4["measured_null_1_cross_curve"] = {
        "E": {"p": ro3["p"], "A": ro3["A"], "B": ro3["B"], "N": ro3["N"]},
        "E_prime": {"A": Ap, "B": Bp},
        "raw": null1_raw,
        "forced_expectation": "4-cycles and 3+1 types appear at nonzero rate",
        "observed_matches_forced_expectation": null1_raw["four_cycles_or_3plus1_observed"],
        "finding": (
            "OBSERVED RESULT CONTRADICTS THE CONTRACT'S DECLARED FORCED VALUE: only the two "
            "Kummer-allowed cycle types (identity, pure-2) were observed, at every trial, exactly "
            "as in the treatment arms -- no 4-cycle or 3+1 type appeared. See controls.py "
            "measured_null_1_cross_curve docstring for the accompanying algebraic argument "
            "(Frobenius commutes with the chord-tangent addition formula's rational functions "
            "regardless of common curve membership, since each individual point's Frobenius image "
            "is +-itself purely from being a square root of an F_p element). Per the contract's "
            "own text (`arms_and_controls.measured_null_1`), this control's failure to show "
            "4-cycles/3+1 renders Stage 2 VOID; that disposition is applied below literally, "
            "not overridden by this Executor."
        ) if not null1_raw["four_cycles_or_3plus1_observed"] else "matches forced expectation",
    }

    # Ordering-control commitment: hash the above BEFORE any treatment (Stage 2/3) draw.
    commit_payload = json.dumps({
        "positive_control_1": stage4["positive_control_1"]["raw"]["histogram"],
        "positive_control_1_pass": pc1_pass,
        "positive_control_2_pass": pc2_pass,
        "measured_null_1_histogram": null1_raw["histogram"],
    }, sort_keys=True).encode("ascii")
    commit_hash = hashlib.sha256(commit_payload).hexdigest()
    commit_time = now_iso()
    stage4["ordering_control"] = {
        "commitment_sha256": commit_hash,
        "committed_at": commit_time,
        "note": "This hash covers positive_control_1, positive_control_2 and measured_null_1, "
                "all computed and hashed strictly before any Stage-2/3 treatment specialization "
                "below is classified. measured_null_2 is NOT separately pre-committed: the "
                "contract's own text (arms_and_controls.measured_null_2) defines it as 'same code "
                "path, same tuple count, same construction' as the tau>=1 Stage-3 treatment cells "
                "themselves, so it is read off those cells after the fact rather than drawn "
                "independently beforehand -- a disclosed, unavoidable tension in the frozen "
                "contract text, not an improvisation; flagged for reviewer.",
    }

    stage2_void_by_null1 = not null1_raw["four_cycles_or_3plus1_observed"]

    result["stage4_pretreatment"] = stage4

    if not pc1_pass:
        result["ABSOLUTE_GATE_FAILED"] = "positive_control_1 failed Chebotarev check; " \
            "NO RESULT MAY BE REPORTED FROM ANY ARM per specification.yaml."
        result["finished_at"] = now_iso()
        with open(os.path.join(run_dir, "raw-result.json"), "w") as fh:
            json.dump(result, fh, indent=2, default=str)
        print("POSITIVE CONTROL 1 FAILED -- terminating per absolute gate.")
        return

    # ---------------- STAGE 2 ----------------
    stage2 = {}
    m3_forced_records = {}
    for c in curves:
        role, p, A, B, trace, Z = c["role"], c["p"], c["A"], c["B"], c["trace"], c["Z"]
        F = get_F(p)
        stage2[role] = {}
        for m in (3, 4, 5):
            cell = stage2_cell(F, A, B, p, m, sampling_domain, STAGE2_N)
            cell["M3_forced"] = mN_forced_split_freq(p, trace, Z, m)
            n_adm = cell["n_admissible"]
            fv = cell["M3_forced"]
            if n_adm and 0 < fv < 1:
                se = math.sqrt(fv * (1 - fv) / n_adm)
                cell["M3_binomial_se"] = se
                cell["M3_sigma_deviation"] = abs(cell["M3_measured"] - fv) / se if se > 0 else float("nan")
            stage2[role][f"m{m}"] = cell
    result["stage2_generic_fibre_census"] = stage2

    # ---------------- DUAL-PATH CROSS-CHECK ----------------
    path2 = SemaevPath2()
    fixture = {
        "deg_T_S4_symbolic_generic": path2.fixture_deg_T_S4(),
    }
    # S3-vanishing fixture, per curve (a handful of real point pairs)
    s3_fixture_results = {}
    for c in curves[:3]:
        role, p, A, B = c["role"], c["p"], c["A"], c["B"]
        F = get_F(p)
        sqt = get_sqrt_table(p)
        checks = []
        cnt = 0
        x = 1
        pts = []
        while len(pts) < 4 and x < p:
            fx = (x ** 3 + A * x + B) % p
            if fx != 0 and legendre(fx, p) == 1:
                pts.append((x, sqt[fx]))
            x += 1
        for i in range(0, len(pts) - 1, 2):
            xP, yP = pts[i]
            xQ, yQ = pts[i + 1]
            ok_sum, ok_diff = s3_vanishes_at_sum_and_difference(A, B, p, xP, yP, xQ, yQ)
            checks.append({"xP": xP, "xQ": xQ, "vanishes_at_sum": ok_sum, "vanishes_at_diff": ok_diff})
        s3_fixture_results[role] = checks
    fixture["s3_vanishing_checks"] = s3_fixture_results
    fixture["s3_vanishing_all_pass"] = all(
        chk["vanishes_at_sum"] and chk["vanishes_at_diff"]
        for lst in s3_fixture_results.values() for chk in lst
    )

    dual_path = {"fixture": fixture, "cells": {}}
    total_disagreements = 0
    if fixture["deg_T_S4_symbolic_generic"] and fixture["s3_vanishing_all_pass"]:
        for c in curves:
            role, p, A, B = c["role"], c["p"], c["A"], c["B"]
            F = get_F(p)
            A_fp2 = F.from_fp(A)
            dual_path["cells"][role] = {}
            for m in M4_STAGE3_MS:
                drawer = Drawer(sampling_domain, "spec-x", p, m + 1000)  # offset label-scope: dedicated counter stream
                keys = sign_keys(m)
                n_checked = 0
                n_disagree = 0
                deg_this_instance = []
                tried = 0
                while n_checked < DUALPATH_N and tried < DUALPATH_N * 3:
                    tried += 1
                    xs = [drawer.draw(p) for _ in range(m - 1)]
                    if len(set(xs)) < len(xs):
                        continue
                    fs = [(x * x * x + A * x + B) % p for x in xs]
                    if any(f == 0 for f in fs):
                        continue
                    base_points = build_base_points(F, A, B, p, xs)
                    roots = enumerate_signed_sums(F, A_fp2, base_points)
                    perm, anomalies = observed_permutation(F, roots)
                    if perm is None:
                        continue
                    ct1 = cycle_type(perm, keys)
                    if m == 4:
                        degs, _ = path2.factor_S4_mod_p(xs[0], xs[1], xs[2], A, B, p)
                        deg_this_instance.append(None)
                    else:
                        degs, dTS5 = path2.factor_S5_mod_p(xs[0], xs[1], xs[2], xs[3], A, B, p)
                        deg_this_instance.append(dTS5)
                    ct2 = tuple(sorted(degs))
                    n_checked += 1
                    if ct1 != ct2:
                        n_disagree += 1
                total_disagreements += n_disagree
                cellrec = {"n_checked": n_checked, "n_disagree": n_disagree}
                if m == 5:
                    cellrec["deg_T_S5_instances_seen"] = sorted(set(deg_this_instance))
                dual_path["cells"][role][f"m{m}"] = cellrec
    else:
        dual_path["SKIPPED"] = "fixture check failed"
    dual_path["total_disagreements"] = total_disagreements
    result["dual_path_cross_check"] = dual_path

    # ---------------- STAGE 3 ----------------
    stage3 = {}
    if tau_ok:
        for c in curves:
            role, p, A, B, N, tau = c["role"], c["p"], c["A"], c["B"], c["N"], c["tau"]
            F = get_F(p)
            stage3[role] = {"tau": tau, "N": N}
            for m in M4_STAGE3_MS:
                stage3[role][f"m{m}"] = {}
                for conv in ("fixed", "random"):
                    fb_key = "fixed" if conv == "fixed" else f"random_m{m}"
                    fb = factor_bases[role][fb_key]["fb"]
                    cellres = stage3_cell(F, A, B, p, N, tau, m, conv, sampling_domain, fb, STAGE3_N)
                    stage3[role][f"m{m}"][conv] = cellres
        result["stage3_sublocus_census"] = stage3
        result["stage3_skipped"] = False
    else:
        result["stage3_sublocus_census"] = None
        result["stage3_skipped"] = True
        result["stage3_skip_reason"] = "tau coverage precondition unmet on constructed panel"

    # measured_null_2: read off tau=1 curves' m=4 stage-3 results
    if tau_ok:
        null2 = {}
        for role, rec in stage3.items():
            if rec["tau"] == 1:
                for conv in ("fixed", "random"):
                    d = rec["m4"][conv]
                    null2[f"{role}_{conv}"] = {
                        "max_D_observed": d["max_D_observed"], "n_valid": d["n_valid"],
                        "forced_exactly_zero_holds": (d["max_D_observed"] in (0, None)),
                    }
        result["measured_null_2_tau1_forced_zero"] = null2
        result["measured_null_2_pass"] = all(v["forced_exactly_zero_holds"] for v in null2.values())
    else:
        result["measured_null_2_tau1_forced_zero"] = None
        result["measured_null_2_pass"] = None

    result["stage2_void_by_measured_null_1"] = stage2_void_by_null1

    # ---------------- WRAP UP ----------------
    finished_at = now_iso()
    wall_seconds = time.time() - t_start_wall
    result["finished_at"] = finished_at
    result["wall_seconds"] = wall_seconds

    with open(os.path.join(run_dir, "raw-result.json"), "w") as fh:
        json.dump(result, fh, indent=2, default=str)

    print(f"DONE in {wall_seconds:.1f}s. Wrote {os.path.join(run_dir, 'raw-result.json')}")


if __name__ == "__main__":
    main()
