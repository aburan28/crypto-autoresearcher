#!/usr/bin/env python3
"""
EXP-MONO-b19c6b executor: third K3/K4 attempt, family-keyed panel,
design-time-verified power (n=20000 null draws/cell), pre-registered
Fisher-combined panel-level statistic as a co-equal primary metric.

Usage: python3 run_experiment.py <master_seed> <output_dir>

Stage order (per specification.yaml `stage_order_and_the_terminating_stage`):
  Stage 0 -- exact-identity sanity gate, reused fixture (same fixture cell as
             EXP-MONO-c819ba/EXP-MONO-670aa6, already independently confirmed
             twice).
  Stage 1 -- construct the family-keyed 100-curve primary panel, THEN run the
             mandatory independence-verification (extract and compare p, B,
             t_used for every matching curve_ordinal across the two
             families) BEFORE any Stage-2/3 compute. Any collision is
             `failed_infrastructure`.
  Stage 2 -- MANDATORY NULL-OBJECT GATE. For every curve: 20000 matched-null
             draws + 1 null-object-pick draw, both statistics (Var, C/F).
             HARD STOP if EITHER the per-curve Holm test OR the
             Fisher-combined panel-level test is significant, in EITHER
             family. Raw per-curve p-values persisted.
  Stage 3 -- real arm, ONLY entered if Stage 2 passes in BOTH tests, BOTH
             families. Reports per-curve Holm AND Fisher-combined, side by
             side, plus the enrichment comparison (P6).
  Stage 4 -- EXTENDED dual-path control: all 100 real-arm cells, PLUS a
             deterministic sample of >=200 null/null-object draws, with
             persisted, thresholded (1e-6 relative) residual diagnostics.
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
from conv import (
    convolution_tower, exact_stats, character_spectrum, var_from_character_side,
    stat_bundle_from_coords,
)
from controls import draw_symmetric_subset
from stats import permutation_pvalue, holm_bonferroni, fisher_exact_2x2, fisher_combined_pvalue

ALPHA = 0.05
N_NULL_DRAWS = 20000
M_PRIMARY = 4
BUDGET_WALL_SECONDS = 7200
BUDGET_SOFT_STOP_SECONDS = 3000  # per handoff: "if wall-clock trends past
                                  # ~3000s with no end in sight, STOP and
                                  # report the exact progress and cause as
                                  # an infrastructure/budget signal."

# Extended dual-path sample selection rule (Stage 4): for each curve, the
# null-subset draw_index values {0, 100} (both congruent to 0 mod 100, the
# smallest two, deterministic and reproducible) PLUS the single
# null-object-pick draw (draw_index=0). 100 curves x 3 samples = 300 total,
# exceeding the >=200 floor with >=1 per curve, at the minimal cost
# consistent with the frozen "draw_index congruent to 0 mod 100" rule.
# Disclosed interpretation choice (implementation.md).
DUAL_PATH_NULL_SUBSET_INDICES = [0, 100]

# ---------------------------------------------------------------------------
# STAGE 0: exact-identity gate on one frozen fixture cell, reused verbatim
# from EXP-MONO-c819ba/EXP-MONO-670aa6's own Stage 0 (already independently
# confirmed twice). No family/master_seed dependence -- this is a pure
# arithmetic-identity check, unrelated to the seed-derivation fix.
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
    """F = N/4, forced even so a symmetric-subset prefix (or random +/- pair
    draw) stays exactly symmetric; identical convention to both
    predecessors' own ladder_fb/primary_F_of."""
    f = N // 4
    return f - (f % 2)


def peak_rss_bytes():
    ru = resource.getrusage(resource.RUSAGE_SELF)
    if sys.platform == "darwin":
        return ru.ru_maxrss
    return ru.ru_maxrss * 1024


def independence_verification(panel):
    """Mandatory Stage-1 check, run BEFORE any Stage-2/3 compute: directly
    extract and compare (p, B, t_used) for every matching curve_ordinal
    across the two families. Reports the comparison explicitly.

    Interpretation note (disclosed, per implementation.md): a "collision" is
    the FULL TUPLE (p, B, t_used) matching identically between the two
    families at a given curve_ordinal -- exactly the failure mode
    EXP-MONO-670aa6 exhibited (100% identical triples across all 100
    curve_ordinals, because its seed rule never keyed on family, so both
    families literally drew from the same stream). A single-field
    coincidence (e.g. both families' curve happening to accept at the same
    t_used, or two curve_ordinals at DIFFERENT primes happening to land on
    the same small B) is expected by chance under correct, independent
    family-keying and does NOT by itself indicate a seed-derivation bug --
    only the fully-matching triple would. Every field is still reported per
    curve_ordinal for full transparency, and full-triple collisions are what
    gates the run."""
    j0_by_k = {r["curve_ordinal"]: r for r in panel["panel"]["j0"]}
    ro_by_k = {r["curve_ordinal"]: r for r in panel["panel"]["random-ordinary"]}
    common_ks = sorted(set(j0_by_k) & set(ro_by_k))
    comparisons = []
    collisions = []
    for k in common_ks:
        j0r, ror = j0_by_k[k], ro_by_k[k]
        p_collision = j0r["p"] == ror["p"]
        b_collision = j0r["B"] == ror["B"]
        t_collision = j0r["t_used"] == ror["t_used"]
        rec = {
            "curve_ordinal": k,
            "j0_p": j0r["p"], "random_ordinary_p": ror["p"], "p_collision": p_collision,
            "j0_B": j0r["B"], "random_ordinary_B": ror["B"], "B_collision": b_collision,
            "j0_t_used": j0r["t_used"], "random_ordinary_t_used": ror["t_used"],
            "t_used_collision": t_collision,
        }
        full_triple_collision = p_collision and b_collision and t_collision
        rec["full_triple_collision"] = full_triple_collision
        comparisons.append(rec)
        if full_triple_collision:
            collisions.append(rec)
    return {
        "n_matched_curve_ordinals_compared": len(common_ks),
        "comparisons": comparisons,
        "n_collisions": len(collisions),
        "collisions": collisions,
        "zero_collisions": len(collisions) == 0,
    }


def family_holm_and_fisher(per_curve_arm, ks, var_key, cf_key):
    """Pools Var AND C/F raw p-values for `ks` curves into ONE Holm family
    (per multiplicity_correction's explicit Var-AND-C/F pooling), and
    computes the Fisher-combined statistic SEPARATELY for Var and for C/F
    (per fisher_combined_panel_statistic's own text: "separately for Var
    and C/F"). Returns a dict with both results."""
    entries = []
    for k in ks:
        entries.append(("var", k, per_curve_arm[k][var_key]))
        entries.append(("cf", k, per_curve_arm[k][cf_key]))
    pvals = [e[2] for e in entries]
    sig, adj, n_sig = holm_bonferroni(pvals, ALPHA)
    sig_curves = sorted({entries[i][1] for i in range(len(entries)) if sig[i]})

    var_pvals = [per_curve_arm[k][var_key] for k in ks]
    cf_pvals = [per_curve_arm[k][cf_key] for k in ks]
    var_stat, var_df, var_combined_p = fisher_combined_pvalue(var_pvals)
    cf_stat, cf_df, cf_combined_p = fisher_combined_pvalue(cf_pvals)

    return {
        "holm_pooled_var_and_cf": {
            "n_tests": len(entries), "n_curves": len(ks),
            "n_significant_tests": n_sig,
            "significant_curve_ordinals": sig_curves,
            "per_test": [
                {"kind": entries[i][0], "curve_ordinal": entries[i][1],
                 "raw_p": entries[i][2], "adjusted_p": adj[i], "significant": sig[i]}
                for i in range(len(entries))],
        },
        "fisher_combined_var": {"statistic": var_stat, "df": var_df,
                                 "combined_p": var_combined_p,
                                 "significant": var_combined_p < ALPHA,
                                 "k_pooled": len(ks)},
        "fisher_combined_cf": {"statistic": cf_stat, "df": cf_df,
                                "combined_p": cf_combined_p,
                                "significant": cf_combined_p < ALPHA,
                                "k_pooled": len(ks)},
    }


def main():
    t_start = time.time()
    master_seed = int(sys.argv[1])
    out_dir = sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)
    sampling_domain = f"{PRIMARY_DOMAIN}/run-{master_seed}"

    result = {"master_seed": master_seed, "sampling_domain": sampling_domain,
              "panel_domain": PRIMARY_DOMAIN, "alpha": ALPHA,
              "n_null_draws": N_NULL_DRAWS, "m_primary": M_PRIMARY,
              "checkpoints": {}}

    def checkpoint(name):
        result["checkpoints"][name] = round(time.time() - t_start, 3)

    def soft_stop_check(where):
        elapsed = time.time() - t_start
        if elapsed > BUDGET_SOFT_STOP_SECONDS:
            result["halted_at"] = f"budget_soft_stop_{where}"
            result["reason"] = (
                f"Elapsed time ({elapsed:.1f}s) exceeded the {BUDGET_SOFT_STOP_SECONDS}s "
                f"soft-stop threshold at stage/point '{where}'. Reported as an "
                f"infrastructure/budget signal per the handoff's explicit instruction, "
                f"NOT a silent reduction of the declared draw count or panel size.")
            _finish(result, out_dir, t_start)
            return True
        return False

    # ---------------- STAGE 0 ----------------
    stage0 = stage0_fixture_gate()
    result["stage0"] = stage0
    checkpoint("stage0_done")
    if not stage0["gate_pass"]:
        result["halted_at"] = "stage0"
        result["reason"] = "Stage-0 exact identity gate failed; per stopping_rules, no further compute spent."
        _finish(result, out_dir, t_start)
        return

    # ---------------- STAGE 1: FAMILY-KEYED PANEL CONSTRUCTION ----------------
    primary = build_primary_panel(master_seed)
    result["primary_panel_construction"] = {
        "domain": primary["domain"], "master_seed": primary["master_seed"],
        "realized_counts": primary["realized_counts"],
        "declared_counts": primary["declared_counts"],
        "construction_failures": primary["construction_failures"],
        "panel": primary["panel"],
    }
    checkpoint("primary_panel_construction_done")

    # ---------------- STAGE 1: MANDATORY INDEPENDENCE VERIFICATION ----------------
    # Runs BEFORE any Stage-2/3 compute, per the handoff and specification's
    # own text, even though the frozen design should make every value differ.
    indep = independence_verification(primary)
    result["stage1_independence_verification"] = indep
    checkpoint("stage1_independence_verification_done")
    if not indep["zero_collisions"]:
        result["halted_at"] = "stage1_independence_verification"
        result["outcome"] = "failed_infrastructure"
        result["reason"] = (
            f"Independence verification found {indep['n_collisions']} (p,B,t_used) "
            f"collision(s) between matched curve_ordinals across families. This means "
            f"the family-keying implementation itself has a bug. STOPPING per "
            f"stopping_rules; no Stage-2/3 compute performed.")
        _finish(result, out_dir, t_start)
        return

    realized_j0 = primary["realized_counts"]["j0"]
    realized_ro = primary["realized_counts"]["random-ordinary"]
    if realized_j0 < 40 or realized_ro < 40:
        result["halted_at"] = "stage1_primary_panel_shortfall"
        result["outcome"] = "failed_infrastructure"
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
                "trace": rec["trace"], "computed_supersingular": rec["computed_supersingular"],
                "p_mod_3": rec["p_mod_3"], "t_used": rec["t_used"],
            }
    result["primary_panel_curve_records"] = curve_meta
    result["primary_panel_fb_construction_failures"] = fb_construction_failures
    result["primary_panel_realized_after_fb_check"] = {
        f: len(curve_states[f]) for f in curve_states}
    checkpoint("primary_curvestates_done")

    # Report Stage-0/Stage-1 mandatory j0/supersingular checks directly.
    j0_p_mod3_violations = [k for k, m in curve_meta["j0"].items() if m["p_mod_3"] != 1]
    ro_supersingular_leaks = [k for k, m in curve_meta["random-ordinary"].items()
                               if m["computed_supersingular"]]
    result["j0_p_mod_3_admission_check"] = {
        "n_curves": len(curve_meta["j0"]), "n_violations": len(j0_p_mod3_violations),
        "violating_curve_ordinals": j0_p_mod3_violations,
        "all_admitted_correctly": len(j0_p_mod3_violations) == 0,
    }
    result["random_ordinary_supersingularity_check"] = {
        "n_curves": len(curve_meta["random-ordinary"]),
        "n_supersingular_leaked_into_panel": len(ro_supersingular_leaks),
        "leaked_curve_ordinals": ro_supersingular_leaks,
        "all_ordinary": len(ro_supersingular_leaks) == 0,
    }
    if j0_p_mod3_violations or ro_supersingular_leaks:
        result["halted_at"] = "stage1_admission_rule_violation"
        result["outcome"] = "failed_infrastructure"
        result["reason"] = "j0 p=1(mod 3) or random-ordinary supersingularity admission rule violated in the realized panel; construction-implementation defect."
        _finish(result, out_dir, t_start)
        return

    for family in curve_states:
        if len(curve_states[family]) < 40:
            result["halted_at"] = "stage1_fb_construction_shortfall"
            result["outcome"] = "failed_infrastructure"
            result["reason"] = (
                f"After factor-base construction/symmetry checks, family {family} realized "
                f"only {len(curve_states[family])} curves (< 40-floor). failed_infrastructure.")
            _finish(result, out_dir, t_start)
            return

    if soft_stop_check("after_stage1"):
        return

    # ---------------- STAGE 2: NULL-OBJECT GATE (data collection) ----------------
    # For every primary-panel curve: draw N_NULL_DRAWS "null-subset" symmetric
    # subsets and ONE "null-object-pick" symmetric subset, all size F=N/4,
    # and compute BOTH statistics (Var, C/F) at m=4 for each draw. NO
    # REAL-ARM (actual factor base) cell is computed here or anywhere below
    # until the gate passes. Raw null-population arrays are used in-memory to
    # compute p-values but are NOT persisted (only the resulting raw p-values
    # are, per the contract's own required_artifacts) -- persisting 100
    # curves x N_NULL_DRAWS x 2 stats floats would be a multi-hundred-MB
    # artifact the contract does not require.
    stage2_per_curve = {"j0": {}, "random-ordinary": {}}
    null_stats_cache = {"j0": {}, "random-ordinary": {}}
    for family in curve_states:
        for k, cs in sorted(curve_states[family].items()):
            F = curve_meta[family][k]["F"]
            null_vars, null_cfs = [], []
            for di in range(N_NULL_DRAWS):
                pts = draw_symmetric_subset(cs, F, sampling_domain, master_seed, family, k,
                                             m=M_PRIMARY, draw_index=di, label="null-subset")
                coords = cs.coords_of(pts)
                bundle = stat_bundle_from_coords(coords, cs.n1, cs.n2, cs.N, F, M_PRIMARY)
                null_vars.append(bundle["var_exact"])
                null_cfs.append(bundle["C_over_F"])
            null_stats_cache[family][k] = {"var": null_vars, "cf": null_cfs}

            pts_obj = draw_symmetric_subset(cs, F, sampling_domain, master_seed, family, k,
                                             m=M_PRIMARY, draw_index=0, label="null-object-pick")
            coords_obj = cs.coords_of(pts_obj)
            bundle_obj = stat_bundle_from_coords(coords_obj, cs.n1, cs.n2, cs.N, F, M_PRIMARY)

            p_var = permutation_pvalue(bundle_obj["var_exact"], null_vars)
            p_cf = permutation_pvalue(bundle_obj["C_over_F"], null_cfs)
            stage2_per_curve[family][k] = {
                "F": F, "null_object_var": bundle_obj["var_exact"],
                "null_object_var_ordered": bundle_obj["var_ordered_exact"],
                "null_object_var_multiset": bundle_obj["var_multiset_exact"],
                "null_object_C_over_F": bundle_obj["C_over_F"],
                "p_var_raw": p_var, "p_cf_raw": p_cf,
            }
            if time.time() - t_start > BUDGET_SOFT_STOP_SECONDS:
                result["stage2_partial"] = stage2_per_curve
                result["stage2_partial_progress"] = f"family={family}, last curve_ordinal={k}"
                soft_stop_check(f"during_stage2_{family}_k{k}")
                return
        checkpoint(f"stage2_null_draws_done_{family}")
        if soft_stop_check(f"after_stage2_{family}"):
            return

    # ---------------- STAGE 2: Holm/Bonferroni (i)/(ii) AND Fisher-combined ----
    # Families (i)/(ii): Var-AND-C/F POOLED (explicit, unambiguous per the
    # frozen text). The Fisher-combined statistic is computed SEPARATELY for
    # Var and C/F, per family, as a CO-EQUAL gating metric alongside Holm.
    gate = {}
    for family in ("j0", "random-ordinary"):
        ks = sorted(stage2_per_curve[family].keys())
        fam_result = family_holm_and_fisher(stage2_per_curve[family], ks, "p_var_raw", "p_cf_raw")
        gate[family] = {"n_curves": len(ks), "curve_ordinals": ks, **fam_result}
    result["stage2_per_curve_raw_pvalues"] = {
        family: {k: {"p_var_raw": v["p_var_raw"], "p_cf_raw": v["p_cf_raw"]}
                 for k, v in stage2_per_curve[family].items()}
        for family in stage2_per_curve
    }
    result["stage2_null_object_gate"] = gate

    def family_gate_pass(fam_gate):
        holm_pass = fam_gate["holm_pooled_var_and_cf"]["n_significant_tests"] == 0
        fisher_var_pass = not fam_gate["fisher_combined_var"]["significant"]
        fisher_cf_pass = not fam_gate["fisher_combined_cf"]["significant"]
        return holm_pass and fisher_var_pass and fisher_cf_pass

    gate_pass_j0 = family_gate_pass(gate["j0"])
    gate_pass_ro = family_gate_pass(gate["random-ordinary"])
    gate_pass = gate_pass_j0 and gate_pass_ro
    result["stage2_gate_pass"] = gate_pass
    result["stage2_gate_pass_per_family"] = {"j0": gate_pass_j0, "random-ordinary": gate_pass_ro}
    checkpoint("stage2_gate_evaluated")

    if not gate_pass:
        result["halted_at"] = "stage2_null_object_gate"
        result["outcome"] = "instrument_still_uncalibrated_despite_design_time_verification"
        failing = [f for f, ok in result["stage2_gate_pass_per_family"].items() if not ok]
        result["reason"] = (
            "HARD STOP per specification.yaml stopping_rules: the null-object arm "
            "produced at least one significant result (per-curve Holm test OR "
            "Fisher-combined test, Var or C/F) at alpha=0.05 in family/families: "
            + ",".join(failing) +
            ". This is a highly significant, surprising finding given the design-time "
            "arithmetic power verification recorded in the frozen contract's "
            "coordinator_approval_rationale -- flagged prominently per the contract's "
            "own outcome text. No Stage-3 real-arm number is computed, read, or "
            "reported below.")
        _finish(result, out_dir, t_start)
        return

    if soft_stop_check("after_stage2_gate"):
        return

    # ---------------- STAGE 3: real arm, ONLY reached because gate_pass ----------
    stage3_per_curve = {"j0": {}, "random-ordinary": {}}
    route1_crosscheck = {"j0": {}, "random-ordinary": {}}
    for family in curve_states:
        for k, cs in sorted(curve_states[family].items()):
            F = curve_meta[family][k]["F"]
            fb_real = cs.fb_full[:F]
            coords_real = cs.coords_of(fb_real)
            bundle_real = stat_bundle_from_coords(coords_real, cs.n1, cs.n2, cs.N, F, M_PRIMARY)

            # dual_path_control: cross-check route 2 (FFT) against route 1
            # (direct roll convolution) on every real-arm cell.
            tower1 = convolution_tower(coords_real, cs.n1, cs.n2, M_PRIMARY)
            st1 = exact_stats(tower1[M_PRIMARY], cs.N, F, M_PRIMARY)
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
                "p_var_raw": p_var, "p_cf_raw": p_cf,
            }
        checkpoint(f"stage3_real_arm_done_{family}")

    result["dual_path_control_real_arm"] = route1_crosscheck
    all_route_ok_real_arm = all(v["within_1e-9"] for fam in route1_crosscheck.values() for v in fam.values())
    result["dual_path_control_real_arm_all_within_1e-9"] = all_route_ok_real_arm

    result["stage3_per_curve_raw_pvalues"] = {
        family: {k: {"p_var_raw": v["p_var_raw"], "p_cf_raw": v["p_cf_raw"]}
                 for k, v in stage3_per_curve[family].items()}
        for family in stage3_per_curve
    }

    # ---------------- STAGE 3: Holm/Bonferroni (iii)/(iv) AND Fisher-combined --
    real_arm_result = {}
    for family in ("j0", "random-ordinary"):
        ks = sorted(stage3_per_curve[family].keys())
        fam_result = family_holm_and_fisher(stage3_per_curve[family], ks, "p_var_raw", "p_cf_raw")
        real_arm_result[family] = {"n_curves": len(ks), "curve_ordinals": ks, **fam_result}
    result["stage3_real_arm_holm_and_fisher_families_iii_iv"] = real_arm_result

    # ---------------- P6: enrichment (uncorrected nominal exceedance, Var) ----
    def nominal_exceedance_count(family):
        ks = sorted(stage3_per_curve[family].keys())
        exceed = sum(1 for k in ks if stage3_per_curve[family][k]["p_var_raw"] < ALPHA)
        return exceed, len(ks)

    j0_exceed, j0_n = nominal_exceedance_count("j0")
    ro_exceed, ro_n = nominal_exceedance_count("random-ordinary")
    p6_fisher = fisher_exact_2x2(j0_exceed, j0_n - j0_exceed, ro_exceed, ro_n - ro_exceed)
    result["p6_enrichment"] = {
        "statistic_used": "Var, m=4, uncorrected two-sided permutation p < 0.05, per curve, this run "
                           "(secondary/non-primary, licensed by a genuinely independent panel)",
        "j0_exceedance_count": j0_exceed, "j0_n": j0_n,
        "j0_rate": j0_exceed / j0_n if j0_n else None,
        "random_ordinary_exceedance_count": ro_exceed, "random_ordinary_n": ro_n,
        "random_ordinary_rate": ro_exceed / ro_n if ro_n else None,
        "fisher_exact_p_two_sided": p6_fisher,
    }

    result["stage3_per_curve"] = stage3_per_curve
    checkpoint("stage3_done")

    if soft_stop_check("after_stage3"):
        return

    # ---------------- STAGE 4: EXTENDED dual-path control -----------------------
    # All 100 real-arm cells already cross-checked above
    # (dual_path_control_real_arm). Now extend to a deterministic sample of
    # >=200 null/null-object draws: per curve, null-subset draw_index in
    # {0,100} plus the null-object-pick draw (draw_index=0) -- 3 samples per
    # curve x 100 curves = 300 total, all indices congruent to 0 mod 100,
    # >=1 per curve, per the frozen selection rule. See implementation.md for
    # the disclosed concrete-count interpretation.
    stage4_samples = []
    for family in curve_states:
        for k, cs in sorted(curve_states[family].items()):
            F = curve_meta[family][k]["F"]
            samples_this_curve = []
            for di in DUAL_PATH_NULL_SUBSET_INDICES:
                pts = draw_symmetric_subset(cs, F, sampling_domain, master_seed, family, k,
                                             m=M_PRIMARY, draw_index=di, label="null-subset")
                samples_this_curve.append(("null-subset", di, pts))
            pts_obj = draw_symmetric_subset(cs, F, sampling_domain, master_seed, family, k,
                                             m=M_PRIMARY, draw_index=0, label="null-object-pick")
            samples_this_curve.append(("null-object-pick", 0, pts_obj))

            for (label, di, pts) in samples_this_curve:
                coords = cs.coords_of(pts)
                bundle2 = stat_bundle_from_coords(coords, cs.n1, cs.n2, cs.N, F, M_PRIMARY)
                tower1 = convolution_tower(coords, cs.n1, cs.n2, M_PRIMARY)
                st1 = exact_stats(tower1[M_PRIMARY], cs.N, F, M_PRIMARY)
                rel_residual = (abs(st1["var_ordered_exact"] - bundle2["var_exact"]) / st1["var_ordered_exact"]
                                if st1["var_ordered_exact"] != 0 else 0.0)
                stage4_samples.append({
                    "family": family, "curve_ordinal": k, "label": label, "draw_index": di,
                    "route1_var": st1["var_ordered_exact"], "route2_var": bundle2["var_exact"],
                    "route1_route2_relative_residual": rel_residual,
                    "route2_max_imag_residual": bundle2["route2_max_imag_residual"],
                    "route2_max_round_residual": bundle2["route2_max_round_residual"],
                    "within_1e-6": rel_residual < 1e-6,
                })
    n_stage4_samples = len(stage4_samples)
    max_rel_residual = max((s["route1_route2_relative_residual"] for s in stage4_samples), default=0.0)
    max_imag_residual = max((s["route2_max_imag_residual"] for s in stage4_samples), default=0.0)
    max_round_residual = max((s["route2_max_round_residual"] for s in stage4_samples), default=0.0)
    all_within_threshold = all(s["within_1e-6"] for s in stage4_samples)
    result["stage4_extended_dual_path_sample"] = {
        "n_samples": n_stage4_samples,
        "meets_200_floor": n_stage4_samples >= 200,
        "selection_rule": "per curve: null-subset draw_index in {0,100} plus null-object-pick draw_index=0",
        "samples": stage4_samples,
        "max_route1_route2_relative_residual": max_rel_residual,
        "max_route2_max_imag_residual": max_imag_residual,
        "max_route2_max_round_residual": max_round_residual,
        "threshold": 1e-6,
        "all_within_threshold": all_within_threshold,
    }
    checkpoint("stage4_done")

    if not all_within_threshold or n_stage4_samples < 200:
        result["halted_at"] = "stage4_dual_path_threshold_breach"
        result["outcome"] = "failed_infrastructure"
        result["reason"] = (
            f"Stage-4 extended dual-path sample: n_samples={n_stage4_samples} "
            f"(floor 200), all_within_threshold={all_within_threshold} "
            f"(threshold 1e-6 relative). A breach or shortfall here is "
            f"failed_infrastructure, never evidence, per stopping_rules.")
        _finish(result, out_dir, t_start)
        return

    result["completed"] = True
    result["outcome"] = ("exceptional_locus_found"
                          if (real_arm_result["j0"]["holm_pooled_var_and_cf"]["n_significant_tests"] > 0
                              or real_arm_result["j0"]["fisher_combined_var"]["significant"]
                              or real_arm_result["j0"]["fisher_combined_cf"]["significant"]
                              or real_arm_result["random-ordinary"]["holm_pooled_var_and_cf"]["n_significant_tests"] > 0
                              or real_arm_result["random-ordinary"]["fisher_combined_var"]["significant"]
                              or real_arm_result["random-ordinary"]["fisher_combined_cf"]["significant"])
                          else "controlled_null_confirmed_at_verified_power")
    _finish(result, out_dir, t_start)


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
