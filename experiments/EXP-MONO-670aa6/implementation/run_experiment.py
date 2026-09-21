#!/usr/bin/env python3
"""
EXP-MONO-670aa6 executor: corrected-calibration replication of
EXP-MONO-c819ba's K3/K4 discriminating test.

Usage: python3 run_experiment.py <master_seed> <output_dir>

Stage order (per specification.yaml `stage_order_and_the_terminating_stage`):
  Stage 0 -- exact-identity sanity gate, reused fixture.
  Stage 1 -- construct the 100-curve primary panel and the 8-curve legacy panel.
  Stage 2 -- MANDATORY NULL-OBJECT GATE. HARD STOP if it fails in either family.
  Stage 3 -- real arm and correction, ONLY entered if Stage 2 passes in BOTH
             families. No real-arm statistic is computed before this point.
  Stage 4 -- legacy/graded controls on the 8-curve sub-panel.
"""
import sys
import os
import json
import time
import platform
import resource

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from curve import curve_discriminant_ok, ConstructionFailure
from groupstate import CurveState
from panel_primary import build_primary_panel, PRIMARY_DOMAIN
from panel_legacy import build_legacy_panel, LEGACY_DOMAIN
from conv import (
    convolution_tower, exact_stats, character_spectrum, var_from_character_side,
    max_C, stat_bundle_from_coords, cell_stats_fft,
)
from controls import draw_symmetric_subset, subgroup_control, coset_union_control
from stats import permutation_pvalue, holm_bonferroni, fisher_exact_2x2

ALPHA = 0.05
N_NULL_DRAWS = 200
BUDGET_WALL_SECONDS = 7200
BUDGET_SOFT_STOP_SECONDS = 6300  # ~87.5% of budget: stop and report if not through
                                  # both families' primary panels by this point.

# ---------------------------------------------------------------------------
# STAGE 0: exact-identity gate on one frozen fixture cell, reused verbatim
# from EXP-MONO-c819ba's own Stage 0 (already independently confirmed twice).
# ---------------------------------------------------------------------------
FIXTURE_P, FIXTURE_A, FIXTURE_B = 101, 1, 1


def stage0_fixture_gate():
    assert curve_discriminant_ok(FIXTURE_A, FIXTURE_B, FIXTURE_P)
    cs = CurveState(FIXTURE_P, FIXTURE_A, FIXTURE_B)
    N = cs.N
    F = N // 2
    fb = cs.fb_full[:F]
    fbset = set(fb)
    symmetric = all((x, (-y) % FIXTURE_P) in fbset for (x, y) in fb)
    coords = cs.coords_of(fb)

    tower = convolution_tower(coords, cs.n1, cs.n2, 2)
    N1, N2 = tower[1], tower[2]

    st1 = exact_stats(N1, N, F, 1)
    var1_formula = (F * (N - F)) / (N * N)
    m1_exact_match = abs(st1["var_ordered_exact"] - var1_formula) < 1e-12

    Shat = character_spectrum(coords, cs.n1, cs.n2)
    sumsq_N2 = int((N2.astype(object) ** 2).sum())
    sum_nontrivial_4 = var_from_character_side(Shat, N, 2) * (N ** 2)
    additive_quadruple_rhs = (F ** 4) / N + sum_nontrivial_4 / N
    additive_quadruple_lhs = sumsq_N2
    m2_rel_residual = abs(additive_quadruple_lhs - additive_quadruple_rhs) / additive_quadruple_lhs

    st2 = exact_stats(N2, N, F, 2)
    var2_char = var_from_character_side(Shat, N, 2)
    m2_var_rel_residual = abs(st2["var_ordered_exact"] - var2_char) / st2["var_ordered_exact"]

    return {
        "fixture": {"p": FIXTURE_P, "A": FIXTURE_A, "B": FIXTURE_B, "N": N,
                    "n1": cs.n1, "n2": cs.n2, "F": F, "fb_symmetric": symmetric},
        "m1": {"var_exact_integer_side": st1["var_ordered_exact"],
               "var_formula_F(N-F)/N^2": var1_formula, "match": m1_exact_match},
        "m2_additive_quadruple": {
            "sum_R_N2(R)^2_exact": additive_quadruple_lhs,
            "F^4/N_plus_sum_nontrivial_Shat^4_over_N": additive_quadruple_rhs,
            "relative_residual": m2_rel_residual,
        },
        "m2_variance_identity": {
            "var_exact_integer_side": st2["var_ordered_exact"],
            "var_character_side_float": var2_char,
            "relative_residual": m2_var_rel_residual,
        },
        "gate_pass": bool(m1_exact_match and m2_rel_residual < 1e-9 and m2_var_rel_residual < 1e-9),
    }


def primary_F_of(N):
    """F = N/4, forced even so a symmetric-subset prefix (or random
    +/- pair draw) stays exactly symmetric; identical convention to
    EXP-MONO-c819ba's ladder_fb (see implementation.md interpretation note)."""
    f = N // 4
    return f - (f % 2)


def peak_rss_bytes():
    ru = resource.getrusage(resource.RUSAGE_SELF)
    # ru_maxrss is KB on Linux, bytes on macOS (Darwin)
    if sys.platform == "darwin":
        return ru.ru_maxrss
    return ru.ru_maxrss * 1024


def main():
    t_start = time.time()
    master_seed = int(sys.argv[1])
    out_dir = sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)
    sampling_domain = f"{PRIMARY_DOMAIN}/run-{master_seed}"
    legacy_sampling_domain = f"{LEGACY_DOMAIN}/run-{master_seed}"

    result = {"master_seed": master_seed, "sampling_domain": sampling_domain,
              "legacy_sampling_domain": legacy_sampling_domain,
              "panel_domain": PRIMARY_DOMAIN, "legacy_domain": LEGACY_DOMAIN,
              "alpha": ALPHA, "n_null_draws": N_NULL_DRAWS,
              "checkpoints": {}}

    def checkpoint(name):
        result["checkpoints"][name] = round(time.time() - t_start, 3)

    # ---------------- STAGE 0 ----------------
    stage0 = stage0_fixture_gate()
    result["stage0"] = stage0
    checkpoint("stage0_done")
    if not stage0["gate_pass"]:
        result["halted_at"] = "stage0"
        result["reason"] = "Stage-0 exact identity gate failed; per stopping_rules, no further compute spent."
        _finish(result, out_dir, t_start)
        return

    # ---------------- STAGE 1: PANEL CONSTRUCTION ----------------
    primary = build_primary_panel()
    result["primary_panel_construction"] = {
        "domain": primary["domain"],
        "realized_counts": primary["realized_counts"],
        "declared_counts": primary["declared_counts"],
        "construction_failures": primary["construction_failures"],
        "panel": primary["panel"],
    }
    checkpoint("primary_panel_construction_done")

    realized_j0 = primary["realized_counts"]["j0"]
    realized_ro = primary["realized_counts"]["random-ordinary"]
    if realized_j0 < 40 or realized_ro < 40:
        result["halted_at"] = "stage1_primary_panel_shortfall"
        result["reason"] = (
            f"Realized panel sizes (j0={realized_j0}, random-ordinary={realized_ro}) "
            f"fall below the success_criterion's 40-per-family floor. Reported as "
            f"failed_infrastructure per PRIMARY PANEL CONSTRUCTION FAILURES ARE "
            f"REPORTED, NEVER BACKFILLED.")
        _finish(result, out_dir, t_start)
        return

    curve_states = {"j0": {}, "random-ordinary": {}}
    curve_meta = {"j0": {}, "random-ordinary": {}}
    fb_construction_failures = {"j0": [], "random-ordinary": []}
    for family in ("j0", "random-ordinary"):
        for rec in primary["panel"][family]:
            k = rec["curve_ordinal"]
            try:
                cs = CurveState(rec["p"], rec["A"], rec["B"])
            except ConstructionFailure as e:
                fb_construction_failures[family].append({"curve_ordinal": k, "error": str(e)})
                continue
            F = primary_F_of(cs.N)
            if F < 2:
                fb_construction_failures[family].append(
                    {"curve_ordinal": k, "error": f"F=N/4 too small (N={cs.N}, F={F})"})
                continue
            fb = cs.fb_full[:F]
            fbset = set(fb)
            symmetric = all((x, (-y) % cs.p) in fbset for (x, y) in fb)
            if not symmetric:
                fb_construction_failures[family].append(
                    {"curve_ordinal": k, "error": "real FB prefix at F=N/4 failed symmetry check"})
                continue
            curve_states[family][k] = cs
            curve_meta[family][k] = {
                "p": cs.p, "N": cs.N, "n1": cs.n1, "n2": cs.n2, "F": F,
                "fb_full_symmetric": cs.fb_full_symmetric, "real_fb_symmetric": symmetric,
                "field_bits": rec["field_bits"], "A": rec["A"], "B": rec["B"],
            }
    result["primary_panel_curve_records"] = curve_meta
    result["primary_panel_fb_construction_failures"] = fb_construction_failures
    result["primary_panel_realized_after_fb_check"] = {
        f: len(curve_states[f]) for f in curve_states}
    checkpoint("primary_curvestates_done")

    for family in curve_states:
        if len(curve_states[family]) < 40:
            result["halted_at"] = "stage1_fb_construction_shortfall"
            result["reason"] = (
                f"After factor-base construction/symmetry checks, family {family} realized "
                f"only {len(curve_states[family])} curves (< 40-floor). failed_infrastructure.")
            _finish(result, out_dir, t_start)
            return

    legacy = build_legacy_panel()
    result["legacy_panel_construction"] = legacy
    checkpoint("legacy_panel_construction_done")

    if time.time() - t_start > BUDGET_SOFT_STOP_SECONDS:
        result["halted_at"] = "budget_soft_stop_after_panel_construction"
        result["reason"] = "Elapsed time exceeded the soft-stop threshold before Stage 2 could begin."
        _finish(result, out_dir, t_start)
        return

    # ---------------- STAGE 2: NULL-OBJECT GATE (data collection) ----------------
    # For every primary-panel curve: draw 200 "null-subset" symmetric subsets and
    # ONE "null-object-pick" symmetric subset, all size F=N/4, and compute BOTH
    # statistics (Var, C/F) at m=4 for each draw. NO REAL-ARM (actual factor base)
    # cell is computed here or anywhere below until the gate passes.
    stage2_per_curve = {"j0": {}, "random-ordinary": {}}
    null_stats_cache = {"j0": {}, "random-ordinary": {}}  # family -> k -> {"var": [...], "cf": [...]}
    for family in curve_states:
        for k, cs in curve_states[family].items():
            F = curve_meta[family][k]["F"]
            null_vars, null_cfs = [], []
            for di in range(N_NULL_DRAWS):
                pts = draw_symmetric_subset(cs, F, sampling_domain, k, m=4, draw_index=di,
                                             label="null-subset")
                coords = cs.coords_of(pts)
                bundle = stat_bundle_from_coords(coords, cs.n1, cs.n2, cs.N, F, 4)
                null_vars.append(bundle["var_exact"])
                null_cfs.append(bundle["C_over_F"])
            null_stats_cache[family][k] = {"var": null_vars, "cf": null_cfs}

            pts_obj = draw_symmetric_subset(cs, F, sampling_domain, k, m=4, draw_index=0,
                                             label="null-object-pick")
            coords_obj = cs.coords_of(pts_obj)
            bundle_obj = stat_bundle_from_coords(coords_obj, cs.n1, cs.n2, cs.N, F, 4)

            p_var = permutation_pvalue(bundle_obj["var_exact"], null_vars)
            p_cf = permutation_pvalue(bundle_obj["C_over_F"], null_cfs)
            stage2_per_curve[family][k] = {
                "F": F, "null_object_var": bundle_obj["var_exact"],
                "null_object_var_ordered": bundle_obj["var_ordered_exact"],
                "null_object_var_multiset": bundle_obj["var_multiset_exact"],
                "null_object_mean_ordered": bundle_obj["mean_ordered"],
                "null_object_mean_multiset": bundle_obj["mean_multiset"],
                "null_object_C_over_F": bundle_obj["C_over_F"],
                "p_var_uncorrected": p_var, "p_cf_uncorrected_informational": p_cf,
                "null_draw_vars_ordered": null_vars,
                "null_draw_C_over_F": null_cfs,
            }
        checkpoint(f"stage2_null_draws_done_{family}")
        if time.time() - t_start > BUDGET_SOFT_STOP_SECONDS:
            result["halted_at"] = f"budget_soft_stop_during_stage2_{family}"
            result["reason"] = "Elapsed time exceeded the soft-stop threshold mid-Stage-2."
            result["stage2_partial"] = stage2_per_curve
            _finish(result, out_dir, t_start)
            return

    # ---------------- STAGE 2: Holm/Bonferroni families (i), (ii) ----------------
    # Families (i)/(ii) are the FROZEN, literal declared families: Var-only,
    # m=4, per curve, within each of the two curve families. (C/F null-object
    # p-values are computed above and Holm-corrected below purely as an
    # additional informational diagnostic -- see implementation.md -- they do
    # NOT gate the run per the frozen multiplicity_correction text, which
    # names only Var for families (i)/(ii).)
    gate = {}
    for family in ("j0", "random-ordinary"):
        ks = sorted(stage2_per_curve[family].keys())
        pvals_var = [stage2_per_curve[family][k]["p_var_uncorrected"] for k in ks]
        sig_var, adj_var, n_sig_var = holm_bonferroni(pvals_var, ALPHA)
        pvals_cf = [stage2_per_curve[family][k]["p_cf_uncorrected_informational"] for k in ks]
        sig_cf, adj_cf, n_sig_cf = holm_bonferroni(pvals_cf, ALPHA)
        gate[family] = {
            "n_curves": len(ks), "curve_ordinals": ks,
            "var_family_holm": {"n_significant": n_sig_var,
                                 "significant_curve_ordinals": [ks[i] for i in range(len(ks)) if sig_var[i]],
                                 "adjusted_pvalues": dict(zip(ks, adj_var))},
            "cf_family_holm_informational_not_gating": {
                "n_significant": n_sig_cf,
                "significant_curve_ordinals": [ks[i] for i in range(len(ks)) if sig_cf[i]],
                "adjusted_pvalues": dict(zip(ks, adj_cf))},
        }
    result["stage2_per_curve"] = stage2_per_curve
    result["stage2_null_object_gate"] = gate
    gate_pass_j0 = gate["j0"]["var_family_holm"]["n_significant"] == 0
    gate_pass_ro = gate["random-ordinary"]["var_family_holm"]["n_significant"] == 0
    gate_pass = gate_pass_j0 and gate_pass_ro
    result["stage2_gate_pass"] = gate_pass
    result["stage2_gate_pass_per_family"] = {"j0": gate_pass_j0, "random-ordinary": gate_pass_ro}
    checkpoint("stage2_gate_evaluated")

    if not gate_pass:
        result["halted_at"] = "stage2_null_object_gate"
        result["outcome"] = "instrument_still_uncalibrated"
        result["reason"] = (
            "HARD STOP per specification.yaml stopping_rules: the null-object arm "
            "produced at least one Holm/Bonferroni-corrected significant curve "
            "(Var statistic, m=4) in family/families: "
            + ",".join(f for f, ok in result["stage2_gate_pass_per_family"].items() if not ok)
            + ". No Stage-3 real-arm number is computed, read, or reported below.")
        _finish(result, out_dir, t_start)
        return

    # ---------------- STAGE 3: real arm, ONLY reached because gate_pass ----------
    stage3_per_curve = {"j0": {}, "random-ordinary": {}}
    route1_crosscheck = {"j0": {}, "random-ordinary": {}}
    for family in curve_states:
        for k, cs in curve_states[family].items():
            F = curve_meta[family][k]["F"]
            fb_real = cs.fb_full[:F]
            coords_real = cs.coords_of(fb_real)
            bundle_real = stat_bundle_from_coords(coords_real, cs.n1, cs.n2, cs.N, F, 4)

            # dual_path_control: cross-check route 2 (FFT) against route 1
            # (direct roll convolution) on every real-arm cell.
            tower1 = convolution_tower(coords_real, cs.n1, cs.n2, 4)
            st1 = exact_stats(tower1[4], cs.N, F, 4)
            route1_route2_rel_residual = (
                abs(st1["var_ordered_exact"] - bundle_real["var_exact"]) / st1["var_ordered_exact"]
                if st1["var_ordered_exact"] != 0 else 0.0)
            route1_crosscheck[family][k] = {
                "route1_var": st1["var_ordered_exact"], "route2_var": bundle_real["var_exact"],
                "relative_residual": route1_route2_rel_residual,
                "within_1e-9": route1_route2_rel_residual < 1e-9,
            }

            null_vars = null_stats_cache[family][k]["var"]
            null_cfs = null_stats_cache[family][k]["cf"]
            p_var = permutation_pvalue(bundle_real["var_exact"], null_vars)
            p_cf = permutation_pvalue(bundle_real["C_over_F"], null_cfs)
            median_null_var = sorted(null_vars)[len(null_vars) // 2]
            median_null_cf = sorted(null_cfs)[len(null_cfs) // 2]
            stage3_per_curve[family][k] = {
                "F": F, "var_real": bundle_real["var_exact"], "C_over_F_real": bundle_real["C_over_F"],
                "var_real_ordered": bundle_real["var_ordered_exact"],
                "var_real_multiset": bundle_real["var_multiset_exact"],
                "mean_real_ordered": bundle_real["mean_ordered"],
                "mean_real_multiset": bundle_real["mean_multiset"],
                "median_null_var": median_null_var, "median_null_C_over_F": median_null_cf,
                "var_real_over_median_null": (bundle_real["var_exact"] / median_null_var
                                               if median_null_var else None),
                "C_over_F_real_over_median_null": (bundle_real["C_over_F"] / median_null_cf
                                                    if median_null_cf else None),
                "p_var_uncorrected": p_var, "p_cf_uncorrected": p_cf,
            }
        checkpoint(f"stage3_real_arm_done_{family}")

    result["dual_path_control_real_arm"] = route1_crosscheck
    all_route_ok = all(v["within_1e-9"] for fam in route1_crosscheck.values() for v in fam.values())
    result["dual_path_control_all_within_1e-9"] = all_route_ok

    # ---------------- STAGE 3: Holm/Bonferroni families (iii), (iv) ----------------
    real_arm_holm = {}
    for family in ("j0", "random-ordinary"):
        ks = sorted(stage3_per_curve[family].keys())
        # family (iii)/(iv): Var AND C/F p-values pooled, m=4, per curve -- one
        # declared family per curve-family, 2*n_curves tests each.
        entries = []  # (kind, k, pvalue)
        for k in ks:
            entries.append(("var", k, stage3_per_curve[family][k]["p_var_uncorrected"]))
            entries.append(("cf", k, stage3_per_curve[family][k]["p_cf_uncorrected"]))
        pvals = [e[2] for e in entries]
        sig, adj, n_sig = holm_bonferroni(pvals, ALPHA)
        sig_curves = sorted({entries[i][1] for i in range(len(entries)) if sig[i]})
        real_arm_holm[family] = {
            "n_tests": len(entries), "n_curves": len(ks),
            "n_significant_tests": n_sig,
            "significant_curve_ordinals": sig_curves,
            "per_test_adjusted_pvalue": [
                {"kind": entries[i][0], "curve_ordinal": entries[i][1],
                 "raw_p": entries[i][2], "adjusted_p": adj[i], "significant": sig[i]}
                for i in range(len(entries))],
        }
    result["stage3_real_arm_holm_families_iii_iv"] = real_arm_holm

    # ---------------- P5: enrichment (uncorrected nominal exceedance) ----------
    def nominal_exceedance_count(family):
        ks = sorted(stage3_per_curve[family].keys())
        exceed = sum(1 for k in ks if stage3_per_curve[family][k]["p_var_uncorrected"] < ALPHA)
        return exceed, len(ks)

    j0_exceed, j0_n = nominal_exceedance_count("j0")
    ro_exceed, ro_n = nominal_exceedance_count("random-ordinary")
    p5_fisher = fisher_exact_2x2(j0_exceed, j0_n - j0_exceed, ro_exceed, ro_n - ro_exceed)
    result["p5_enrichment"] = {
        "statistic_used": "Var, m=4, uncorrected two-sided permutation p < 0.05, per curve, this run",
        "j0_exceedance_count": j0_exceed, "j0_n": j0_n,
        "j0_rate": j0_exceed / j0_n if j0_n else None,
        "random_ordinary_exceedance_count": ro_exceed, "random_ordinary_n": ro_n,
        "random_ordinary_rate": ro_exceed / ro_n if ro_n else None,
        "fisher_exact_p_two_sided": p5_fisher,
    }

    result["stage3_per_curve"] = stage3_per_curve
    checkpoint("stage3_done")

    if time.time() - t_start > BUDGET_SOFT_STOP_SECONDS:
        result["halted_at"] = "budget_soft_stop_after_stage3"
        result["reason"] = "Elapsed time exceeded the soft-stop threshold before Stage 4 could begin."
        _finish(result, out_dir, t_start)
        return

    # ---------------- STAGE 4: legacy 8-curve sub-panel controls -----------------
    stage4 = run_legacy_stage4(legacy, legacy_sampling_domain)
    result["stage4_legacy_controls"] = stage4
    checkpoint("stage4_done")

    result["completed"] = True
    result["outcome"] = "controlled_null_confirmed_or_exceptional_locus_see_stage3"
    _finish(result, out_dir, t_start)


def run_legacy_stage4(legacy, sampling_domain):
    """Reruns EXP-MONO-c819ba's own subgroup / coset-union / F-ladder / m-ladder
    / prime-ladder controls on the 8-curve legacy panel, under this contract's
    domain and seeds, purely as continuity evidence (never corrected, never
    contributes to the primary escalation decision)."""
    F_LADDER_DENOMS = {"N/16": 16, "N/8": 8, "N/4": 4, "N/2": 2}

    def ladder_fb(cs, denom):
        target = max(2, cs.N // denom)
        target -= target % 2
        return cs.fb_full[:target]

    def band_label(ratio, lo, hi):
        if ratio is None:
            return None
        return "IN_BAND" if lo <= ratio <= hi else ("ABOVE_BAND" if ratio > hi else "BELOW_BAND")

    curve_states = {}
    construction_errors = {}
    for c in legacy["curves"]:
        role = c["role"]
        try:
            curve_states[role] = CurveState(c["p"], c["A"], c["B"])
        except ConstructionFailure as e:
            construction_errors[role] = str(e)

    subgroup_capable = [role for role, cs in curve_states.items() if cs.n2 % 4 == 0]
    subgroup_availability = {
        "capable_roles": subgroup_capable,
        "precondition_met": len(subgroup_capable) >= 2,
    }
    out = {"construction_errors": construction_errors, "subgroup_availability": subgroup_availability}
    if len(subgroup_capable) < 2:
        out["positive_control_1"] = "SKIPPED: subgroup-availability precondition unmet"
        out["positive_control_2"] = "SKIPPED: subgroup-availability precondition unmet"
    else:
        stage4_subgroup = {}
        for role in subgroup_capable:
            cs = curve_states[role]
            stage4_subgroup[role] = {}
            for h_label, kk in (("h=N/2", 2), ("h=N/4", 4)):
                coords, h = subgroup_control(cs, kk)
                if coords is None:
                    stage4_subgroup[role][h_label] = {"skipped": True, "reason": f"{kk} does not divide n2={cs.n2}"}
                    continue
                cstats = cell_stats_fft(coords, cs.n1, cs.n2, cs.N, h, m_list=(2,))
                forced_rel_dev = cs.N / h - 1
                measured_rel_dev = cstats["per_m"][2]["max_rel_dev"]
                stage4_subgroup[role][h_label] = {
                    "h": h, "N": cs.N, "forced_relative_deviation": forced_rel_dev,
                    "measured_relative_deviation_m2": measured_rel_dev,
                    "exact_match": abs(measured_rel_dev - forced_rel_dev) < 1e-9,
                    "C_over_F": cstats["C_over_F"],
                    "C_over_F_exact_match_1": abs(cstats["C_over_F"] - 1.0) < 1e-9,
                }
        out["positive_control_1"] = stage4_subgroup
        pc1_pass = all(v.get("skipped") or (v["exact_match"] and v["C_over_F_exact_match_1"])
                       for role in stage4_subgroup for v in stage4_subgroup[role].values())
        out["positive_control_1_pass"] = pc1_pass

        stage4_coset = {}
        for role, cs in curve_states.items():
            cu = coset_union_control(cs, sampling_domain, 0, 0, 0)
            if cu is None:
                continue
            h = cu["h"]
            coords = cu["coords"]
            cstats = cell_stats_fft(coords, cs.n1, cs.n2, cs.N, cu["fb_size"], m_list=(1,))
            Shat_measured = cstats["Shat"]
            H4_coords = subgroup_control(cs, 4)[0]
            import numpy as np
            Shat_H = character_spectrum(H4_coords, cs.n1, cs.n2)
            from conv import indicator_grid
            delta = indicator_grid([cu["g_coord"]], cs.n1, cs.n2).astype(complex)
            chi_g = np.fft.fft2(delta)
            Shat_pred = Shat_H + Shat_H * chi_g
            max_abs_diff = float(np.max(np.abs(Shat_measured - Shat_pred)))
            max_abs_val = float(np.max(np.abs(Shat_measured)))
            F = cu["fb_size"]
            stage4_coset[role] = {
                "h": h, "F": F, "C": cstats["C"], "C_over_F": cstats["C_over_F"],
                "forced_spectrum_max_abs_diff": max_abs_diff,
                "forced_spectrum_relative_tolerance": max_abs_diff / max_abs_val if max_abs_val else None,
                "matches_forced_spectrum": (max_abs_diff / max_abs_val) < 1e-8 if max_abs_val else None,
            }
        out["positive_control_2"] = stage4_coset

    # graded controls: F-ladder / m-ladder, all curves; prime ladder, RO curves.
    N_NULL_DRAWS_LEGACY = N_NULL_DRAWS
    graded = {}
    for role, cs in curve_states.items():
        graded[role] = {}
        for label, denom in F_LADDER_DENOMS.items():
            fb = ladder_fb(cs, denom)
            F = len(fb)
            coords = cs.coords_of(fb)
            real_stats = cell_stats_fft(coords, cs.n1, cs.n2, cs.N, F, m_list=(1, 2, 3, 4))

            null_stats_list = []
            for di in range(N_NULL_DRAWS_LEGACY):
                pts = draw_symmetric_subset(cs, F, sampling_domain, 0, m=0, draw_index=di,
                                             label="null-subset")
                ncoords = cs.coords_of(pts)
                null_stats_list.append(cell_stats_fft(ncoords, cs.n1, cs.n2, cs.N, F, m_list=(1, 2, 3, 4)))

            def agg_var(m):
                vals = [ns["per_m"][m]["var_ordered"] for ns in null_stats_list]
                mean = sum(vals) / len(vals)
                sd = (sum((v - mean) ** 2 for v in vals) / len(vals)) ** 0.5
                return mean, sd

            mean_cf_null = sum(ns["C_over_F"] for ns in null_stats_list) / len(null_stats_list)
            l3 = real_stats["C_over_F"] / mean_cf_null if mean_cf_null else None
            per_m_out = {}
            for m in (1, 2, 3, 4):
                mean_var_null, sd_var_null = agg_var(m)
                l2 = real_stats["per_m"][m]["var_ordered"] / mean_var_null if mean_var_null else None
                per_m_out[m] = {
                    "real_var": real_stats["per_m"][m]["var_ordered"],
                    "null_mean_var": mean_var_null, "null_sd_var": sd_var_null,
                    "L2_var_real_over_var_null_mean": l2,
                    "L2_label": (band_label(l2, 0.7, 1.4) if m >= 2 else "CALIBRATION_EXCLUDED"),
                }
            graded[role][label] = {
                "F": F, "C_real": real_stats["C"], "C_over_F_real": real_stats["C_over_F"],
                "null_mean_C_over_F": mean_cf_null,
                "L3_C_over_F_ratio": l3, "L3_label": band_label(l3, 0.85, 1.15),
                "per_m": per_m_out, "n_null_draws": len(null_stats_list),
            }
    out["graded_controls_F_and_m_ladder"] = graded

    ro_roles = [r for r in ("RO1", "RO2", "RO3", "RO4") if r in curve_states]
    prime_ladder = []
    for role in ro_roles:
        cs = curve_states[role]
        fb = ladder_fb(cs, 2)
        F = len(fb)
        coords = cs.coords_of(fb)
        cstats = cell_stats_fft(coords, cs.n1, cs.n2, cs.N, F, m_list=(1,))
        import math
        c_over_sqrtF = cstats["C"] / math.sqrt(F) if F else None
        prime_ladder.append({"role": role, "p": cs.p, "N": cs.N, "F": F,
                              "C": cstats["C"], "C_over_sqrtF": c_over_sqrtF})
    fitted_exponent = None
    if len(prime_ladder) >= 2:
        import math
        xs = [math.log(c["N"]) for c in prime_ladder]
        ys = [math.log(c["C_over_sqrtF"]) for c in prime_ladder if c["C_over_sqrtF"] and c["C_over_sqrtF"] > 0]
        if len(ys) == len(xs) and len(xs) >= 2:
            n = len(xs)
            mx = sum(xs) / n
            my = sum(ys) / n
            num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
            den = sum((x - mx) ** 2 for x in xs)
            fitted_exponent = num / den if den else None
    out["prime_ladder"] = {"points": prime_ladder,
                            "fitted_exponent_of_N_in_C_over_sqrtF": fitted_exponent,
                            "note": "toy-scale trend over <=4 primes; never extrapolated."}
    return out


def _finish(result, out_dir, t_start):
    result["wall_seconds"] = time.time() - t_start
    result["peak_rss_bytes"] = peak_rss_bytes()
    result["environment"] = {"python_version": platform.python_version(),
                              "platform": platform.platform()}
    with open(os.path.join(out_dir, "raw-result.json"), "w") as f:
        json.dump(result, f, indent=2, default=str)
    print(json.dumps({"wall_seconds": result["wall_seconds"],
                       "completed": result.get("completed", False),
                       "halted_at": result.get("halted_at"),
                       "outcome": result.get("outcome"),
                       "stage2_gate_pass": result.get("stage2_gate_pass")}, indent=2))


if __name__ == "__main__":
    main()
