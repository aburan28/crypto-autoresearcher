"""
EXP-MONO-2114ea executor script.

Graded multi-curve positive control: does H-MONO-663fb4's own
Fisher-combined statistic have ANY power to detect a planted, mild,
multi-curve effect, as opposed to the single-extreme-outlier regime
EXP-MONO-b1423c already showed it structurally cannot detect?
See specification.yaml for the full frozen contract; this script
implements it literally.

Reused BYTE-IDENTICAL from experiments/EXP-MONO-b19c6b/implementation/:
  fields.py, curve.py, conv.py, groupstate.py, stats.py (imported directly,
  not copied -- see sys.path setup below).
Reused VERBATIM function (copied + runtime-diffed, per this lane's own
convention): experiments/EXP-MONO-c819ba/implementation/controls.py::
subgroup_control -> this directory's own controls.py.
Reused for Stage 1 ONLY (imported directly via importlib, not copied):
experiments/EXP-MONO-b1423c/implementation/controls.py::
draw_symmetric_null_subset + its own seed.py::NullSubsetDrawer, under the
SAME domain ("EXP-MONO-b1423c/v1") and master_seed (20260901) that
contract used, to reproduce its own archived RO3 result bit-for-bit.
New to this contract: seed_stage2.py (this contract's own frozen
seed_derivation_rule) and controls.py's perturbation-construction
functions (smallest_admissible_subgroup_index, fixed_coset_for_curve,
take_symmetric_prefix, construct_perturbed_factor_base).
"""
import hashlib
import importlib.util
import json
import math
import os
import resource
import sys
import time

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
B19C6B_IMPL = os.path.normpath(os.path.join(THIS_DIR, "..", "..", "EXP-MONO-b19c6b", "implementation"))
C819BA_CONTROLS_PATH = os.path.normpath(os.path.join(
    THIS_DIR, "..", "..", "EXP-MONO-c819ba", "implementation", "controls.py"))
B1423C_IMPL = os.path.normpath(os.path.join(THIS_DIR, "..", "..", "EXP-MONO-b1423c", "implementation"))
B19C6B_RAW_RESULT = os.path.normpath(os.path.join(
    THIS_DIR, "..", "..", "EXP-MONO-b19c6b", "runs", "RUN-MONO-b19c6b-1", "raw-result.json"))
B1423C_EXEC_REPORT_TARGETS = {
    # Read by hand from experiments/EXP-MONO-b1423c/execution_report.yaml
    # `S5_known_positive_cell_raw_pvalues` and `S1_S4_fisher_combined_mixed_panels`
    # blocks (reused_stage1_reproduction_target). NOT recomputed, only
    # compared against.
    "h=N/2": {
        "S5_raw_pvalue_var": 4.999750012499375e-05,
        "S5_raw_pvalue_C_over_F": 4.999750012499375e-05,
        "var_real": 2229025112064.0,
        "C_over_F_real": 1.0,
    },
    "h=N/4": {
        "S5_raw_pvalue_var": 4.999750012499375e-05,
        "S5_raw_pvalue_C_over_F": 4.999750012499375e-05,
        "var_real": 26121388032.0,
        "C_over_F_real": 1.0,
    },
    "S1": 0.5197796626550032,
    "S2": 0.5197796626550032,
    "S3": 0.47085766077181307,
    "S4": 0.47085766077181307,
}

sys.path.insert(0, THIS_DIR)
sys.path.insert(1, B19C6B_IMPL)

from groupstate import CurveState  # noqa: E402
from conv import (  # noqa: E402
    character_spectrum, var_from_character_side, max_C,
    convolution_tower, exact_stats, stat_bundle_from_coords,
)
from stats import permutation_pvalue, fisher_combined_pvalue, holm_bonferroni, chi2_sf_even_df  # noqa: E402
import controls  # noqa: E402  (this experiment's own controls.py)
from seed_stage2 import draw_symmetric_null_subset_stage2, DOMAIN as STAGE2_DOMAIN, MASTER_SEED as STAGE2_SEED  # noqa: E402

RO3_P, RO3_A, RO3_B = 307, 269, 6
RO3_CELLS = [("h=N/2", 2, 144), ("h=N/4", 4, 72)]
B1423C_DOMAIN = "EXP-MONO-b1423c/v1"
B1423C_MASTER_SEED = 20260901
N_NULL_DRAWS = 20000
M_PRIMARY = 4
DUAL_PATH_TOL = 1e-9
STAGE0_TOL = 1e-9
ALPHA = 0.05

FRACTION_LADDER = [0.02, 0.05, 0.10]
PANEL_SIZE_LADDER = [5, 10, 15]
GRID_CELLS = [
    (0.02, 10), (0.05, 10), (0.10, 10),
    (0.05, 5), (0.05, 15),
]


def primary_F_of(N):
    """F = N/4, forced even so a symmetric-subset prefix (or random +/- pair
    draw) stays exactly symmetric. IDENTICAL formula to
    EXP-MONO-b19c6b's own `run_experiment.py::primary_F_of` (that file is
    not one of the five files this contract is required to import
    byte-identical -- it is the panel-construction *driver*, not the
    reused statistical instrument -- so this formula is reproduced here,
    by name and value, to reconstruct EXP-MONO-b19c6b's own real,
    unperturbed x-coordinate factor base deterministically from each
    curve's already-archived (p, A, B), matching the archived per-curve F
    exactly. Not a re-derivation of anything about the STATISTIC under
    test, only of the panel's own disclosed real-factor-base convention."""
    f = N // 4
    return f - (f % 2)


def sha256_of(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()


def _load_module_from_path(mod_name, path):
    spec = importlib.util.spec_from_file_location(mod_name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod
    spec.loader.exec_module(mod)
    return mod


def load_b1423c_draw_symmetric_null_subset():
    """Load EXP-MONO-b1423c's own draw_symmetric_null_subset (and the
    NullSubsetDrawer it depends on, via that contract's own seed.py) by
    IMPORT, not copy, temporarily overriding sys.modules['seed'] so that
    b1423c's controls.py's own `from seed import NullSubsetDrawer`
    resolves to b1423c's seed.py rather than b19c6b's (already-imported,
    already used by `curve.py`'s own already-bound `seed_int` name, which
    is unaffected by this swap since it was already resolved at `curve.py`
    import time above)."""
    saved_seed_mod = sys.modules.get("seed")
    try:
        b1423c_seed_path = os.path.join(B1423C_IMPL, "seed.py")
        _load_module_from_path("seed", b1423c_seed_path)
        b1423c_controls_mod = _load_module_from_path(
            "b1423c_controls_impl", os.path.join(B1423C_IMPL, "controls.py"))
    finally:
        if saved_seed_mod is not None:
            sys.modules["seed"] = saved_seed_mod
        else:
            sys.modules.pop("seed", None)
    return b1423c_controls_mod.draw_symmetric_null_subset


def stage0_gate_floor_vs_threshold():
    """specification.yaml `inputs.fisher_floor_vs_threshold_stage0_check`:
    report the per-curve permutation floor against the Fisher combination's
    own effective degrees of freedom, at k in {5,10,15} (oracle arm) and at
    the full-panel size (48, always -- see implementation.md on why the
    full-panel size is fixed at 48 regardless of k), BEFORE any draw is
    spent. Reports whether an ALL-FLOOR panel (the maximally extreme case)
    would reject at alpha=0.05."""
    floor_p = 1.0 / (N_NULL_DRAWS + 1)
    out = {"permutation_floor": floor_p, "alpha": ALPHA, "by_k": {}}
    for k in PANEL_SIZE_LADDER:
        stat, df, p = fisher_combined_pvalue([floor_p] * k)
        out["by_k"][str(k)] = {
            "df": df, "all_floor_fisher_stat": stat,
            "all_floor_combined_pvalue": p,
            "all_floor_rejects_at_0.05": p < ALPHA,
        }
    stat48, df48, p48 = fisher_combined_pvalue([floor_p] * 48)
    out["full_panel_size_48"] = {
        "df": df48, "all_floor_fisher_stat": stat48,
        "all_floor_combined_pvalue": p48,
        "all_floor_rejects_at_0.05": p48 < ALPHA,
    }
    return out


def stage0_exact_elevation_check(cs, fb_coords_orig, coset_coords, r, n1, n2, N, F):
    """specification.yaml `inputs.exact_planted_elevation_precommitment`:
    directly compute the perturbed factor base's own Shat(chi) spectrum and
    its exact C/F, Var(m=4); separately reconstruct that same spectrum via
    linearity of the Fourier transform (Shat_perturbed = Shat_original -
    Shat_removed + Shat_added); compare the two. An exact algebraic
    identity, not an approximation -- a mismatch beyond 1e-9 relative (or a
    tight absolute floor for near-zero entries) is `failed_infrastructure`."""
    pert = controls.construct_perturbed_factor_base(cs, fb_coords_orig, coset_coords, r)
    perturbed_coords = pert["perturbed_coords"]
    removed = pert["removed"]
    added = pert["added"]

    Shat_orig = character_spectrum(fb_coords_orig, n1, n2)
    Shat_removed = character_spectrum(removed, n1, n2)
    Shat_added = character_spectrum(added, n1, n2)
    Shat_reconstructed = Shat_orig - Shat_removed + Shat_added
    Shat_direct = character_spectrum(perturbed_coords, n1, n2)

    import numpy as np
    abs_diff = np.abs(Shat_direct - Shat_reconstructed)
    denom = np.abs(Shat_reconstructed)
    denom_safe = np.where(denom > 1e-6, denom, 1.0)
    rel_err = abs_diff / denom_safe
    max_abs_err_where_small_denom = float(np.max(abs_diff[denom <= 1e-6])) if np.any(denom <= 1e-6) else 0.0
    max_rel_err = float(np.max(rel_err))

    var_direct = var_from_character_side(Shat_direct, N, M_PRIMARY)
    c_direct, _ = max_C(Shat_direct)
    cf_direct = c_direct / F if F else None
    var_reconstructed = var_from_character_side(Shat_reconstructed, N, M_PRIMARY)
    c_reconstructed, _ = max_C(Shat_reconstructed)
    cf_reconstructed = c_reconstructed / F if F else None

    passed = (max_rel_err < STAGE0_TOL) and (max_abs_err_where_small_denom < 1e-6)
    return {
        "fraction": r,
        "count_swapped": pert["count"],
        "count_requested_raw": pert["count_requested_raw"],
        "count_parity_adjusted": pert["count_parity_adjusted"],
        "max_relative_spectrum_error": max_rel_err,
        "max_absolute_spectrum_error_near_zero_denom": max_abs_err_where_small_denom,
        "passed": passed,
        "direct": {"Var": var_direct, "C": c_direct, "C_over_F": cf_direct},
        "closed_form_reconstruction": {"Var": var_reconstructed, "C": c_reconstructed, "C_over_F": cf_reconstructed},
        "perturbed_coords": perturbed_coords,
        "removed": removed,
        "added": added,
    }


def run_stage1_ro3_reproduction():
    """Hard gate: reproduce EXP-MONO-b1423c's own archived RO3 result,
    using its own domain/master_seed for the null draws (bit-for-bit),
    and this contract's own byte-identical/verbatim-diffed subgroup_control
    and conv.py/stats.py."""
    out = {}
    verbatim_ok, c819ba_src_path = controls.verify_subgroup_control_source_verbatim()
    out["subgroup_control_source_verbatim_match"] = verbatim_ok
    out["subgroup_control_source_path"] = c819ba_src_path
    if not verbatim_ok:
        out["passed"] = False
        out["halted_at"] = "subgroup_control_source_check"
        return out

    cs = CurveState(RO3_P, RO3_A, RO3_B)
    struct_ok = (cs.N == 288 and cs.n1 == 3 and cs.n2 == 96)
    out["ro3_reconstructed"] = {"p": cs.p, "A": cs.A, "B": cs.B, "N": cs.N, "n1": cs.n1, "n2": cs.n2}
    out["ro3_structure_matches_spec"] = struct_ok
    if not struct_ok:
        out["passed"] = False
        out["halted_at"] = "ro3_structure_check"
        return out

    draw_symmetric_null_subset_b1423c = load_b1423c_draw_symmetric_null_subset()

    with open(B19C6B_RAW_RESULT) as f:
        b19c6b_raw = json.load(f)
    bg_per_curve = b19c6b_raw["stage3_per_curve_raw_pvalues"]["random-ordinary"]
    background_p_var = [v["p_var_raw"] for v in bg_per_curve.values()]
    background_p_cf = [v["p_cf_raw"] for v in bg_per_curve.values()]

    cells_out = {}
    all_match = True
    for h_label, k, h_expected in RO3_CELLS:
        coords, h = controls.subgroup_control(cs, k)
        if coords is None or h != h_expected:
            cells_out[h_label] = {"mismatch": True, "h": h, "h_expected": h_expected}
            all_match = False
            continue
        F = h
        real = stat_bundle_from_coords(coords, cs.n1, cs.n2, cs.N, F, M_PRIMARY)
        var_real = real["var_ordered_exact"]
        c_over_f_real = real["C_over_F"]

        tower = convolution_tower(coords, cs.n1, cs.n2, M_PRIMARY)
        route1_stats = exact_stats(tower[M_PRIMARY], cs.N, F, M_PRIMARY)
        var_route1 = route1_stats["var_ordered_exact"]
        rel_diff_var = (abs(var_route1 - var_real) / abs(var_real) if var_real != 0
                         else abs(var_route1 - var_real))
        dual_path_ok = rel_diff_var < DUAL_PATH_TOL

        null_var, null_cf = [], []
        for di in range(N_NULL_DRAWS):
            pts = draw_symmetric_null_subset_b1423c(cs, F, B1423C_DOMAIN, B1423C_MASTER_SEED, h, di)
            null_coords = [cs.coord(P) for P in pts]
            Shat_null = character_spectrum(null_coords, cs.n1, cs.n2)
            null_var.append(var_from_character_side(Shat_null, cs.N, M_PRIMARY))
            c_n, _ = max_C(Shat_null)
            null_cf.append(c_n / F)

        p_var_raw = permutation_pvalue(var_real, null_var)
        p_cf_raw = permutation_pvalue(c_over_f_real, null_cf)

        target = B1423C_EXEC_REPORT_TARGETS[h_label]
        var_match = abs(var_real - target["var_real"]) / abs(target["var_real"]) < STAGE0_TOL
        cf_match = abs(c_over_f_real - target["C_over_F_real"]) < STAGE0_TOL
        p_var_match = abs(p_var_raw - target["S5_raw_pvalue_var"]) / target["S5_raw_pvalue_var"] < STAGE0_TOL
        p_cf_match = abs(p_cf_raw - target["S5_raw_pvalue_C_over_F"]) / target["S5_raw_pvalue_C_over_F"] < STAGE0_TOL
        cell_match = var_match and cf_match and p_var_match and p_cf_match and dual_path_ok
        all_match = all_match and cell_match

        cells_out[h_label] = {
            "k": k, "h": h, "F": F,
            "var_real": var_real, "C_over_F_real": c_over_f_real,
            "dual_path_relative_difference": rel_diff_var,
            "dual_path_within_1e-9": dual_path_ok,
            "S5_raw_pvalue_var": p_var_raw, "S5_raw_pvalue_C_over_F": p_cf_raw,
            "archived_target": target,
            "matches_archived_target": cell_match,
        }

    out["cells"] = cells_out
    if not all_match:
        out["passed"] = False
        out["halted_at"] = "stage1_cell_reproduction"
        return out

    fisher_out = {}
    for h_label, _, _ in RO3_CELLS:
        p_var_cell = cells_out[h_label]["S5_raw_pvalue_var"]
        p_cf_cell = cells_out[h_label]["S5_raw_pvalue_C_over_F"]
        mixed_var = [p_var_cell] + list(background_p_var)
        mixed_cf = [p_cf_cell] + list(background_p_cf)
        stat_v, df_v, p_v = fisher_combined_pvalue(mixed_var)
        stat_c, df_c, p_c = fisher_combined_pvalue(mixed_cf)
        fisher_out[h_label] = {
            "Var_statistic": {"fisher_stat": stat_v, "df": df_v, "combined_pvalue": p_v},
            "C_over_F_statistic": {"fisher_stat": stat_c, "df": df_c, "combined_pvalue": p_c},
        }
    S1 = fisher_out["h=N/2"]["Var_statistic"]["combined_pvalue"]
    S2 = fisher_out["h=N/4"]["Var_statistic"]["combined_pvalue"]
    S3 = fisher_out["h=N/2"]["C_over_F_statistic"]["combined_pvalue"]
    S4 = fisher_out["h=N/4"]["C_over_F_statistic"]["combined_pvalue"]
    out["fisher_combined_mixed_panels"] = fisher_out
    out["S1"], out["S2"], out["S3"], out["S4"] = S1, S2, S3, S4
    s_match = (
        abs(S1 - B1423C_EXEC_REPORT_TARGETS["S1"]) / B1423C_EXEC_REPORT_TARGETS["S1"] < STAGE0_TOL
        and abs(S2 - B1423C_EXEC_REPORT_TARGETS["S2"]) / B1423C_EXEC_REPORT_TARGETS["S2"] < STAGE0_TOL
        and abs(S3 - B1423C_EXEC_REPORT_TARGETS["S3"]) / B1423C_EXEC_REPORT_TARGETS["S3"] < STAGE0_TOL
        and abs(S4 - B1423C_EXEC_REPORT_TARGETS["S4"]) / B1423C_EXEC_REPORT_TARGETS["S4"] < STAGE0_TOL
    )
    out["s1_s4_match_archived_targets"] = s_match
    out["passed"] = all_match and s_match
    return out


def main():
    t_start = time.time()
    result = {
        "master_seed": STAGE2_SEED,
        "domain": STAGE2_DOMAIN,
        "m_primary": M_PRIMARY,
        "n_null_draws": N_NULL_DRAWS,
        "alpha": ALPHA,
        "fraction_ladder": FRACTION_LADDER,
        "panel_size_ladder": PANEL_SIZE_LADDER,
        "grid_cells": [{"fraction": r, "panel_size": k} for r, k in GRID_CELLS],
    }

    # ================= STAGE 0 (before any of the 20000 draws) ============
    result["stage0_floor_vs_threshold"] = stage0_gate_floor_vs_threshold()

    # ================= STAGE 1 (hard gate) =================================
    stage1 = run_stage1_ro3_reproduction()
    result["stage1_ro3_reproduction"] = stage1
    if not stage1.get("passed"):
        result["completed"] = False
        result["outcome"] = "failed_infrastructure"
        result["halted_at"] = "stage1_ro3_reproduction"
        result["reason"] = f"Stage 1 RO3 reproduction failed: {stage1.get('halted_at')}"
        _finish(result, t_start)
        return

    # ================= load background panel (reuse, unmodified) ==========
    with open(B19C6B_RAW_RESULT) as f:
        b19c6b_raw = json.load(f)
    curve_records = b19c6b_raw["primary_panel_curve_records"]["random-ordinary"]
    per_curve_pvals = b19c6b_raw["stage3_per_curve_raw_pvalues"]["random-ordinary"]
    result["background_panel_source"] = B19C6B_RAW_RESULT
    result["background_panel_size"] = len(curve_records)
    result["background_panel_sha256"] = sha256_of(curve_records)

    all_ordinals = sorted(curve_records.keys(), key=int)
    if len(all_ordinals) != 48:
        result["completed"] = False
        result["outcome"] = "failed_infrastructure"
        result["halted_at"] = "background_panel_size_check"
        result["reason"] = f"Expected 48 curves in archived panel, found {len(all_ordinals)}."
        _finish(result, t_start)
        return

    pool = all_ordinals[:15]
    result["candidate_pool_curve_ordinals"] = pool

    # ================= Stage 0 (per-curve exact elevation) + Stage 2 =======
    per_curve = {}
    stage0_elevation = {}
    infra_failure = None

    for ordinal in pool:
        rec = curve_records[ordinal]
        p, A, B = rec["p"], rec["A"], rec["B"]
        cs = CurveState(p, A, B)
        F_expected = primary_F_of(cs.N)
        struct_ok = (cs.N == rec["N"] and cs.n1 == rec["n1"] and cs.n2 == rec["n2"]
                     and F_expected == rec["F"] and F_expected <= len(cs.fb_full))
        if not struct_ok:
            infra_failure = {
                "stage": "curve_reconstruction", "curve_ordinal": ordinal,
                "reconstructed": {"N": cs.N, "n1": cs.n1, "n2": cs.n2,
                                   "F_expected": F_expected, "len_fb_full": len(cs.fb_full)},
                "archived": rec,
            }
            break

        # Same real x-coordinate factor base as EXP-MONO-b19c6b's own
        # `run_experiment.py::primary_F_of` / prefix-of-fb_full construction:
        # FB = first F elements of cs.fb_full (curve.py's own natural
        # construction order), F = N//4 forced even. This is the exact
        # REAL, unperturbed factor base -- reconstructed deterministically
        # from the archived (p, A, B), not re-derived from a seed.
        fb_coords_orig = cs.coords_of(cs.fb_full[:F_expected])
        F = len(fb_coords_orig)
        coset_coords, coset_k, coset_h_size = controls.fixed_coset_for_curve(cs)

        elevations = {}
        try:
            for r in FRACTION_LADDER:
                gate = stage0_exact_elevation_check(
                    cs, fb_coords_orig, coset_coords, r, cs.n1, cs.n2, cs.N, F)
                elevations[str(r)] = gate
                if not gate["passed"]:
                    infra_failure = {
                        "stage": "stage0_exact_elevation", "curve_ordinal": ordinal,
                        "fraction": r,
                        "max_relative_spectrum_error": gate["max_relative_spectrum_error"],
                    }
                    break
        except ValueError as e:
            infra_failure = {"stage": "perturbation_construction", "curve_ordinal": ordinal, "error": str(e)}
        if infra_failure:
            break
        stage0_elevation[ordinal] = {
            r: {"count_swapped": elevations[r]["count_swapped"],
                "count_requested_raw": elevations[r]["count_requested_raw"],
                "count_parity_adjusted": elevations[r]["count_parity_adjusted"],
                "direct": elevations[r]["direct"],
                "closed_form_reconstruction": elevations[r]["closed_form_reconstruction"],
                "max_relative_spectrum_error": elevations[r]["max_relative_spectrum_error"],
                "passed": elevations[r]["passed"]}
            for r in elevations
        }
        stage0_elevation[ordinal]["subgroup_index_k"] = coset_k
        stage0_elevation[ordinal]["subgroup_size_h"] = coset_h_size

        # ---- real (unperturbed) dual-path control, matched-null-panel arm's real-arm cell ----
        real_route2 = stat_bundle_from_coords(fb_coords_orig, cs.n1, cs.n2, cs.N, F, M_PRIMARY)
        tower = convolution_tower(fb_coords_orig, cs.n1, cs.n2, M_PRIMARY)
        route1_stats = exact_stats(tower[M_PRIMARY], cs.N, F, M_PRIMARY)
        var_real = real_route2["var_ordered_exact"]
        rel_diff_real = (abs(route1_stats["var_ordered_exact"] - var_real) / abs(var_real)
                          if var_real != 0 else abs(route1_stats["var_ordered_exact"] - var_real))

        # ---- ONE 20000-draw null population per curve (keyed on p,F,curve_ordinal) ----
        null_var, null_cf = [], []
        for di in range(N_NULL_DRAWS):
            pts = draw_symmetric_null_subset_stage2(
                cs, F, STAGE2_DOMAIN, STAGE2_SEED, int(ordinal), di)
            null_coords = [cs.coord(P) for P in pts]
            Shat_null = character_spectrum(null_coords, cs.n1, cs.n2)
            null_var.append(var_from_character_side(Shat_null, cs.N, M_PRIMARY))
            c_n, _ = max_C(Shat_null)
            null_cf.append(c_n / F)

        per_curve[ordinal] = {
            "p": p, "A": A, "B": B, "N": cs.N, "n1": cs.n1, "n2": cs.n2, "F": F,
            "archived_p_var_raw": per_curve_pvals[ordinal]["p_var_raw"],
            "archived_p_cf_raw": per_curve_pvals[ordinal]["p_cf_raw"],
            "real_unperturbed_var": var_real,
            "real_unperturbed_C_over_F": real_route2["C_over_F"],
            "real_unperturbed_dual_path_relative_difference": rel_diff_real,
            "real_unperturbed_dual_path_within_1e-9": rel_diff_real < DUAL_PATH_TOL,
            "null_var": null_var,
            "null_cf": null_cf,
            "perturbed": {},
        }

        for r in FRACTION_LADDER:
            gate = elevations[str(r)]
            perturbed_coords = gate["perturbed_coords"]
            real_pert = stat_bundle_from_coords(perturbed_coords, cs.n1, cs.n2, cs.N, F, M_PRIMARY)
            tower_pert = convolution_tower(perturbed_coords, cs.n1, cs.n2, M_PRIMARY)
            route1_pert = exact_stats(tower_pert[M_PRIMARY], cs.N, F, M_PRIMARY)
            var_pert = real_pert["var_ordered_exact"]
            rel_diff_pert = (abs(route1_pert["var_ordered_exact"] - var_pert) / abs(var_pert)
                              if var_pert != 0 else abs(route1_pert["var_ordered_exact"] - var_pert))
            p_var_raw = permutation_pvalue(var_pert, null_var)
            p_cf_raw = permutation_pvalue(real_pert["C_over_F"], null_cf)
            per_curve[ordinal]["perturbed"][str(r)] = {
                "var_perturbed": var_pert,
                "C_over_F_perturbed": real_pert["C_over_F"],
                "dual_path_relative_difference": rel_diff_pert,
                "dual_path_within_1e-9": rel_diff_pert < DUAL_PATH_TOL,
                "p_var_raw": p_var_raw,
                "p_cf_raw": p_cf_raw,
            }

    if infra_failure is not None:
        result["stage0_per_curve_elevation"] = stage0_elevation
        result["infra_failure"] = infra_failure
        result["completed"] = False
        result["outcome"] = "failed_infrastructure"
        result["halted_at"] = infra_failure["stage"]
        result["reason"] = f"Stage 0/curve-reconstruction gate failed: {infra_failure}"
        _finish(result, t_start)
        return

    result["stage0_per_curve_elevation"] = stage0_elevation

    dual_path_all_ok = all(
        per_curve[o]["real_unperturbed_dual_path_within_1e-9"]
        and all(per_curve[o]["perturbed"][str(r)]["dual_path_within_1e-9"] for r in FRACTION_LADDER)
        for o in pool
    )
    result["dual_path_control_all_within_1e-9"] = dual_path_all_ok

    # per-curve raw p-values summary (drop the 20000-length null arrays from
    # the summarized view; kept in `per_curve_full` for the required artifact
    # of per-curve raw p-values, but null arrays are large -- report summary
    # stats instead of the full 20000-length arrays in the top-level result
    # to keep raw-result.json a reasonable size; full arrays are not required
    # artifacts, only the resulting raw p-values are).
    per_curve_summary = {}
    for o in pool:
        pc = per_curve[o]
        per_curve_summary[o] = {
            "p": pc["p"], "N": pc["N"], "n1": pc["n1"], "n2": pc["n2"], "F": pc["F"],
            "archived_p_var_raw": pc["archived_p_var_raw"],
            "archived_p_cf_raw": pc["archived_p_cf_raw"],
            "real_unperturbed_var": pc["real_unperturbed_var"],
            "real_unperturbed_C_over_F": pc["real_unperturbed_C_over_F"],
            "real_unperturbed_dual_path_within_1e-9": pc["real_unperturbed_dual_path_within_1e-9"],
            "null_var_summary": {
                "mean": sum(pc["null_var"]) / N_NULL_DRAWS,
                "min": min(pc["null_var"]), "max": max(pc["null_var"]),
            },
            "null_cf_summary": {
                "mean": sum(pc["null_cf"]) / N_NULL_DRAWS,
                "min": min(pc["null_cf"]), "max": max(pc["null_cf"]),
            },
            "perturbed": pc["perturbed"],
        }
    result["per_curve_raw_pvalues"] = per_curve_summary

    # ================= Stage 2/3: grid cells =================================
    def full_panel_pvals(statistic_key, selected_ordinals, perturbed, fraction=None):
        """statistic_key in {'var','cf'}. If perturbed, use per-curve
        perturbed[fraction] p-value for selected_ordinals; else use each
        selected curve's own ARCHIVED unperturbed raw p-value (matched null
        panel, no new computation). Background (non-selected of the 48) is
        ALWAYS the archived unperturbed raw p-value."""
        pkey = "p_var_raw" if statistic_key == "var" else "p_cf_raw"
        vals = []
        selected_set = set(selected_ordinals)
        for o in all_ordinals:
            if o in selected_set and perturbed:
                vals.append(per_curve[o]["perturbed"][str(fraction)][pkey])
            else:
                vals.append(per_curve_pvals[o][pkey])
        return vals

    def oracle_pvals(statistic_key, selected_ordinals, perturbed, fraction=None):
        pkey = "p_var_raw" if statistic_key == "var" else "p_cf_raw"
        vals = []
        for o in selected_ordinals:
            if perturbed:
                vals.append(per_curve[o]["perturbed"][str(fraction)][pkey])
            else:
                vals.append(per_curve_pvals[o][pkey])
        return vals

    stage2_stage3 = {}
    for r, k in GRID_CELLS:
        selected = pool[:k]
        cell_key = f"r={r}_k={k}"
        cell_out = {"fraction": r, "panel_size": k, "selected_curve_ordinals": selected}
        for stat_name in ("var", "cf"):
            full_p = full_panel_pvals(stat_name, selected, perturbed=True, fraction=r)
            oracle_p = oracle_pvals(stat_name, selected, perturbed=True, fraction=r)
            fstat, fdf, fp = fisher_combined_pvalue(full_p)
            ostat, odf, op = fisher_combined_pvalue(oracle_p)
            sig, adj, nsig = holm_bonferroni(full_p, alpha=ALPHA)
            selected_idx = [all_ordinals.index(o) for o in selected]
            cell_out[f"T1_full_panel_{stat_name}"] = {
                "fisher_stat": fstat, "df": fdf, "combined_pvalue": fp, "rejects_at_0.05": fp < ALPHA,
            }
            cell_out[f"T2_oracle_{stat_name}"] = {
                "fisher_stat": ostat, "df": odf, "combined_pvalue": op, "rejects_at_0.05": op < ALPHA,
            }
            cell_out[f"T4_holm_{stat_name}"] = {
                "n_significant_of_48": nsig,
                "selected_curves_significant": [sig[i] for i in selected_idx],
                "selected_curves_adjusted_pvalues": [adj[i] for i in selected_idx],
            }
        stage2_stage3[cell_key] = cell_out
    result["stage2_stage3_grid"] = stage2_stage3

    # ================= T3: matched null-panel control (mandatory, every k) ===
    matched_null_panel = {}
    for k in PANEL_SIZE_LADDER:
        selected = pool[:k]
        cell_out = {"panel_size": k, "selected_curve_ordinals": selected}
        for stat_name in ("var", "cf"):
            full_p = full_panel_pvals(stat_name, selected, perturbed=False)
            oracle_p = oracle_pvals(stat_name, selected, perturbed=False)
            fstat, fdf, fp = fisher_combined_pvalue(full_p)
            ostat, odf, op = fisher_combined_pvalue(oracle_p)
            cell_out[f"T3_full_panel_{stat_name}"] = {
                "fisher_stat": fstat, "df": fdf, "combined_pvalue": fp, "rejects_at_0.05": fp < ALPHA,
            }
            cell_out[f"T3_oracle_{stat_name}"] = {
                "fisher_stat": ostat, "df": odf, "combined_pvalue": op, "rejects_at_0.05": op < ALPHA,
            }
        matched_null_panel[str(k)] = cell_out
    result["matched_null_panel_control"] = matched_null_panel

    matched_null_clean = all(
        not matched_null_panel[str(k)][f"T3_full_panel_{s}"]["rejects_at_0.05"]
        and not matched_null_panel[str(k)][f"T3_oracle_{s}"]["rejects_at_0.05"]
        for k in PANEL_SIZE_LADDER for s in ("var", "cf")
    )
    result["matched_null_panel_clean_at_every_panel_size"] = matched_null_clean

    # ================= Stage 3: detection-power surface =====================
    any_reject = False
    first_rejecting_cell = None
    for r, k in sorted(GRID_CELLS, key=lambda rk: (rk[0], rk[1])):
        cell_key = f"r={r}_k={k}"
        c = stage2_stage3[cell_key]
        cell_rejects = any(
            c[f"T1_full_panel_{s}"]["rejects_at_0.05"] or c[f"T2_oracle_{s}"]["rejects_at_0.05"]
            for s in ("var", "cf")
        )
        if cell_rejects and first_rejecting_cell is None:
            first_rejecting_cell = cell_key
            any_reject = True
        elif cell_rejects:
            any_reject = True
    result["stage3_any_cell_rejects"] = any_reject
    result["stage3_smallest_rejecting_cell"] = first_rejecting_cell

    # NOTE / DISCLOSED GRID-COVERAGE OBSERVATION: H-MONO-d9dc51's own
    # falsification_conditions[2] and this spec's own falsification_criterion(d)
    # both refer to "the strongest tested cell (10% perturbation, 15 curves)".
    # The APPROVED 5-cell L-shaped grid (all fractions at k=10; all panel
    # sizes at r=0.05) does NOT contain a (r=0.10, k=15) cell -- the two
    # ladders share only the (0.05, 10) cell, not a joint (0.10, 15) corner.
    # This is reported here explicitly rather than silently substituting a
    # nearby cell for the literal one H-MONO-d9dc51's text names: we report
    # the oracle outcome at BOTH tested edges (max fraction at its tested
    # panel size, and max panel size at its tested fraction) instead.
    max_fraction_cell = f"r={max(FRACTION_LADDER)}_k=10"
    max_panelsize_cell = f"r=0.05_k={max(PANEL_SIZE_LADDER)}"
    result["strongest_tested_cell_note"] = (
        "The grid does NOT contain a joint (r=0.10, k=15) cell (see "
        "H-MONO-d9dc51's own falsification_conditions[2] / this spec's "
        "falsification_criterion(d), which name that combination but the "
        "approved L-shaped grid does not test it). Reporting the oracle "
        "outcome at the two tested edges instead: max-fraction-at-its-"
        "tested-panel-size and max-panel-size-at-its-tested-fraction."
    )
    oracle_rejects_max_fraction_edge = any(
        stage2_stage3[max_fraction_cell][f"T2_oracle_{s}"]["rejects_at_0.05"] for s in ("var", "cf")
    )
    oracle_rejects_max_panelsize_edge = any(
        stage2_stage3[max_panelsize_cell][f"T2_oracle_{s}"]["rejects_at_0.05"] for s in ("var", "cf")
    )
    result["oracle_rejects_at_max_fraction_edge_cell"] = {
        "cell": max_fraction_cell, "rejects": oracle_rejects_max_fraction_edge}
    result["oracle_rejects_at_max_panelsize_edge_cell"] = {
        "cell": max_panelsize_cell, "rejects": oracle_rejects_max_panelsize_edge}
    oracle_rejects_strongest = oracle_rejects_max_fraction_edge or oracle_rejects_max_panelsize_edge
    result["oracle_rejects_at_strongest_tested_cell"] = oracle_rejects_strongest

    # ================= outcome classification (observations only) ===========
    if not matched_null_clean:
        outcome_label = "positive_control_itself_not_extreme_or_mixed"
        outcome_note = "matched null-panel control did not remain clean at every panel size (specificity concern)."
    elif any_reject:
        outcome_label = "sensitivity_confirmed_many_mild_curves"
        outcome_note = f"At least one full-panel or oracle cell rejects at alpha=0.05; smallest: {first_rejecting_cell}."
    else:
        outcome_label = "sensitivity_gap_confirmed_everywhere_tested"
        outcome_note = "No cell (full-panel or oracle) rejects anywhere in the tested grid, including the strongest cell."

    result["outcome_label_per_spec_outcomes_block"] = outcome_label
    result["outcome_label_note"] = outcome_note

    result["completed"] = True
    result["outcome"] = "completed_valid" if dual_path_all_ok else "invalid_measurement"
    if not dual_path_all_ok:
        result["reason"] = "Dual-path route1/route2 disagreement exceeded 1e-9 relative tolerance on at least one cell."

    _finish(result, t_start)


def _finish(result, t_start):
    result["wall_seconds"] = time.time() - t_start
    usage = resource.getrusage(resource.RUSAGE_SELF)
    peak_rss = usage.ru_maxrss * (1 if sys.platform == "darwin" else 1024)
    result["peak_rss_bytes"] = peak_rss
    result["certificate"] = {"kind": "none", "note": "Pure measurement/statistics run; no DLOG solve or relation claimed."}
    out_dir = os.path.normpath(os.path.join(THIS_DIR, "..", "runs", "RUN-MONO-2114ea-1"))
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "raw-result.json"), "w") as f:
        json.dump(result, f, indent=2, sort_keys=True, default=str)
    print(json.dumps({k: result[k] for k in
                       ("completed", "outcome", "wall_seconds", "peak_rss_bytes")
                       if k in result}, indent=2))


if __name__ == "__main__":
    main()
