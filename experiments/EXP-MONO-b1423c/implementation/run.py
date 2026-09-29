"""
EXP-MONO-b1423c executor script.

K5 sensitivity check: does EXP-MONO-b19c6b's Fisher-combined statistic
reject a genuine, maximally-extreme positive control (RO3's exact
subgroup factor base)? See specification.yaml for the full frozen
contract; this script implements it literally.

Reused BYTE-IDENTICAL from experiments/EXP-MONO-b19c6b/implementation/:
  fields.py, curve.py, conv.py, groupstate.py, stats.py
Reused VERBATIM function from experiments/EXP-MONO-c819ba/implementation/
controls.py: subgroup_control (copied into this directory's controls.py,
diffed byte-for-byte against the source at run time below).
New to this contract: seed.py (NullSubsetDrawer, this contract's own
frozen seed_derivation_rule) and controls.py's draw_symmetric_null_subset
(same rejection-sampling mechanism, new preimage).
"""
import hashlib
import json
import math
import os
import resource
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from groupstate import CurveState
from controls import subgroup_control, draw_symmetric_null_subset
from conv import (
    character_spectrum, var_from_character_side, max_C,
    convolution_tower, exact_stats, cell_stats_fft, stat_bundle_from_coords,
)
from stats import permutation_pvalue, fisher_combined_pvalue


DOMAIN = "EXP-MONO-b1423c/v1"
MASTER_SEED = 20260901
M_PRIMARY = 4
N_NULL_DRAWS = 20000
DUAL_PATH_TOL = 1e-9

RO3_P, RO3_A, RO3_B = 307, 269, 6
CELLS = [("h=N/2", 2, 144), ("h=N/4", 4, 72)]


def sha256_of(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()


def verify_subgroup_control_source_verbatim():
    """Confirm this directory's copied subgroup_control matches
    EXP-MONO-c819ba's own source verbatim (byte-for-byte), per the
    contract's reuse requirement."""
    import re
    src_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "..",
        "EXP-MONO-c819ba", "implementation", "controls.py")
    src_path = os.path.normpath(src_path)
    with open(src_path) as f:
        src = f.read()
    m = re.search(r"def subgroup_control.*?return coords, h\n", src, re.S)
    orig = m.group(0)
    here_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "controls.py")
    with open(here_path) as f:
        mine = f.read()
    m2 = re.search(r"def subgroup_control.*?return coords, h\n", mine, re.S)
    mine_func = m2.group(0)
    return orig == mine_func, src_path


def main():
    t_start = time.time()
    result = {
        "master_seed": MASTER_SEED,
        "domain": DOMAIN,
        "m_primary": M_PRIMARY,
        "n_null_draws": N_NULL_DRAWS,
        "ro3": {"p": RO3_P, "A": RO3_A, "B": RO3_B},
    }

    # ---------------- source-verbatim check on subgroup_control -------------
    verbatim_ok, c819ba_src_path = verify_subgroup_control_source_verbatim()
    result["subgroup_control_source_verbatim_match"] = verbatim_ok
    result["subgroup_control_source_path"] = c819ba_src_path
    if not verbatim_ok:
        result["completed"] = False
        result["outcome"] = "failed_infrastructure"
        result["halted_at"] = "subgroup_control_source_check"
        result["reason"] = "Copied subgroup_control does not match EXP-MONO-c819ba's source verbatim."
        _finish(result, t_start)
        return

    # ---------------- build RO3 curve state ----------------------------------
    cs = CurveState(RO3_P, RO3_A, RO3_B)
    result["ro3_reconstructed"] = {
        "p": cs.p, "A": cs.A, "B": cs.B, "N": cs.N, "n1": cs.n1, "n2": cs.n2,
    }
    struct_ok = (cs.N == 288 and cs.n1 == 3 and cs.n2 == 96)
    result["ro3_structure_matches_spec"] = struct_ok
    if not struct_ok:
        result["completed"] = False
        result["outcome"] = "failed_infrastructure"
        result["halted_at"] = "ro3_structure_check"
        result["reason"] = (
            f"Reconstructed RO3 group structure (N={cs.N}, n1={cs.n1}, n2={cs.n2}) "
            "does not match the archived (N=288, n1=3, n2=96).")
        _finish(result, t_start)
        return

    # ---------------- RECONSTRUCTION VERIFICATION (must pass before S1-S5) --
    verification = {}
    all_verified = True
    for h_label, k, h_expected in CELLS:
        coords, h = subgroup_control(cs, k)
        if coords is None or h != h_expected:
            verification[h_label] = {
                "skipped_or_mismatched": True, "k": k, "h": h, "h_expected": h_expected,
            }
            all_verified = False
            continue
        cstats = cell_stats_fft(coords, cs.n1, cs.n2, cs.N, h, m_list=(2, M_PRIMARY))
        forced_rel_dev = cs.N / h - 1
        measured_rel_dev_m2 = cstats["per_m"][2]["max_rel_dev"]
        c_over_f = cstats["C_over_F"]
        exact_match_dev = abs(measured_rel_dev_m2 - forced_rel_dev) < 1e-9
        exact_match_cf = abs(c_over_f - 1.0) < 1e-9
        # archived comparison values, from EXP-MONO-c819ba/execution_report.yaml
        # L4_positive_control_1_subgroup block (read-only comparison, not reuse
        # of any computed number):
        archived_forced_rel_dev = {"h=N/2": 1.0, "h=N/4": 3.0}[h_label]
        archived_c_over_f = 1.0
        matches_archive = (
            abs(forced_rel_dev - archived_forced_rel_dev) < 1e-9
            and abs(measured_rel_dev_m2 - archived_forced_rel_dev) < 1e-9
            and abs(c_over_f - archived_c_over_f) < 1e-9
        )
        verification[h_label] = {
            "k": k, "h": h,
            "forced_relative_deviation": forced_rel_dev,
            "measured_relative_deviation_m2": measured_rel_dev_m2,
            "C_over_F": c_over_f,
            "exact_match_forced_vs_measured": exact_match_dev,
            "exact_match_C_over_F_1": exact_match_cf,
            "matches_c819ba_archived_exact_values": matches_archive,
            "coords_digest_sha256": hashlib.sha256(
                json.dumps(sorted(coords)).encode()).hexdigest(),
        }
        all_verified = all_verified and matches_archive

    result["reconstruction_verification"] = verification
    result["reconstruction_verified"] = all_verified
    if not all_verified:
        result["completed"] = False
        result["outcome"] = "failed_infrastructure"
        result["halted_at"] = "reconstruction_verification"
        result["reason"] = (
            "RO3 subgroup reconstruction did not reproduce EXP-MONO-c819ba's "
            "own archived exact values. Per stopping_rules, no S1-S5 arm is computed.")
        _finish(result, t_start)
        return

    # ---------------- load background panel (reuse, unmodified) -------------
    b19c6b_run_path = os.path.normpath(os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "..",
        "EXP-MONO-b19c6b", "runs", "RUN-MONO-b19c6b-1", "raw-result.json"))
    with open(b19c6b_run_path) as f:
        b19c6b_raw = json.load(f)
    bg_per_curve = b19c6b_raw["stage3_per_curve_raw_pvalues"]["random-ordinary"]
    background_p_var = [v["p_var_raw"] for v in bg_per_curve.values()]
    background_p_cf = [v["p_cf_raw"] for v in bg_per_curve.values()]
    result["background_panel_source"] = b19c6b_run_path
    result["background_panel_family"] = "random-ordinary"
    result["background_panel_size"] = len(background_p_var)
    result["background_panel_curve_ordinals"] = sorted(bg_per_curve.keys(), key=int)
    result["background_panel_sha256"] = sha256_of(bg_per_curve)

    # ---------------- per-cell: real stats, null draws, S5, dual-path -------
    cells_out = {}
    for h_label, k, h in CELLS:
        coords, _ = subgroup_control(cs, k)
        F = h

        # real-arm stats at m=4 (route 2 / FFT, primary path)
        real_route2 = stat_bundle_from_coords(coords, cs.n1, cs.n2, cs.N, F, M_PRIMARY)
        var_real = real_route2["var_ordered_exact"]
        c_over_f_real = real_route2["C_over_F"]

        # dual-path control: route 1 direct convolution vs route 2 FFT
        tower = convolution_tower(coords, cs.n1, cs.n2, M_PRIMARY)
        route1_stats = exact_stats(tower[M_PRIMARY], cs.N, F, M_PRIMARY)
        var_route1 = route1_stats["var_ordered_exact"]
        rel_diff_var = (abs(var_route1 - var_real) / abs(var_real)
                         if var_real != 0 else abs(var_route1 - var_real))
        dual_path_ok = rel_diff_var < DUAL_PATH_TOL

        # null distribution: 20000 matched-null symmetric subsets
        null_var = []
        null_cf = []
        for di in range(N_NULL_DRAWS):
            pts = draw_symmetric_null_subset(cs, F, DOMAIN, MASTER_SEED, h, di)
            null_coords = [cs.coord(P) for P in pts]
            Shat_null = character_spectrum(null_coords, cs.n1, cs.n2)
            var_n = var_from_character_side(Shat_null, cs.N, M_PRIMARY)
            c_n, _ = max_C(Shat_null)
            null_var.append(var_n)
            null_cf.append(c_n / F)

        # S5: raw two-sided permutation p-value of the known-positive cell alone
        p_var_raw = permutation_pvalue(var_real, null_var)
        p_cf_raw = permutation_pvalue(c_over_f_real, null_cf)

        null_var_sorted = sorted(null_var)
        null_cf_sorted = sorted(null_cf)

        cells_out[h_label] = {
            "k": k, "h": h, "F": F,
            "var_real": var_real,
            "C_over_F_real": c_over_f_real,
            "dual_path_control": {
                "route1_var_ordered_exact": var_route1,
                "route2_var_ordered_exact": var_real,
                "relative_difference": rel_diff_var,
                "within_1e-9": dual_path_ok,
            },
            "null_distribution_summary": {
                "n_draws": N_NULL_DRAWS,
                "var_min": null_var_sorted[0],
                "var_max": null_var_sorted[-1],
                "var_mean": sum(null_var) / N_NULL_DRAWS,
                "var_median": (null_var_sorted[N_NULL_DRAWS // 2 - 1] + null_var_sorted[N_NULL_DRAWS // 2]) / 2.0,
                "cf_min": null_cf_sorted[0],
                "cf_max": null_cf_sorted[-1],
                "cf_mean": sum(null_cf) / N_NULL_DRAWS,
                "cf_median": (null_cf_sorted[N_NULL_DRAWS // 2 - 1] + null_cf_sorted[N_NULL_DRAWS // 2]) / 2.0,
            },
            "S5_raw_pvalue_var": p_var_raw,
            "S5_raw_pvalue_C_over_F": p_cf_raw,
            "S5_near_floor_var": p_var_raw <= 2.0 / (N_NULL_DRAWS + 1),
            "S5_near_floor_C_over_F": p_cf_raw <= 2.0 / (N_NULL_DRAWS + 1),
            "var_real_vs_null_mean_ratio": (var_real / (sum(null_var) / N_NULL_DRAWS)
                                             if sum(null_var) != 0 else None),
            "C_over_F_real_vs_null_mean_ratio": (c_over_f_real / (sum(null_cf) / N_NULL_DRAWS)
                                                  if sum(null_cf) != 0 else None),
        }

    result["cells"] = cells_out

    # ---------------- S1-S4: Fisher-combined mixed panels -------------------
    fisher_out = {}
    for h_label, _, _ in CELLS:
        p_var_cell = cells_out[h_label]["S5_raw_pvalue_var"]
        p_cf_cell = cells_out[h_label]["S5_raw_pvalue_C_over_F"]

        mixed_var = [p_var_cell] + list(background_p_var)
        mixed_cf = [p_cf_cell] + list(background_p_cf)

        stat_v, df_v, p_v = fisher_combined_pvalue(mixed_var)
        stat_c, df_c, p_c = fisher_combined_pvalue(mixed_cf)

        fisher_out[h_label] = {
            "mixed_panel_size": len(mixed_var),
            "Var_statistic": {"fisher_stat": stat_v, "df": df_v, "combined_pvalue": p_v,
                               "rejects_at_0.05": p_v < 0.05},
            "C_over_F_statistic": {"fisher_stat": stat_c, "df": df_c, "combined_pvalue": p_c,
                                    "rejects_at_0.05": p_c < 0.05},
        }

    result["fisher_combined_mixed_panels"] = fisher_out
    result["S1"] = fisher_out["h=N/2"]["Var_statistic"]["combined_pvalue"]
    result["S2"] = fisher_out["h=N/4"]["Var_statistic"]["combined_pvalue"]
    result["S3"] = fisher_out["h=N/2"]["C_over_F_statistic"]["combined_pvalue"]
    result["S4"] = fisher_out["h=N/4"]["C_over_F_statistic"]["combined_pvalue"]

    # ---------------- outcome classification (observations only) ------------
    s5_extreme = any(
        cells_out[h_label]["S5_near_floor_var"] or cells_out[h_label]["S5_near_floor_C_over_F"]
        for h_label, _, _ in CELLS
    )
    any_s1_s4_rejects = any(
        fisher_out[h_label]["Var_statistic"]["rejects_at_0.05"]
        or fisher_out[h_label]["C_over_F_statistic"]["rejects_at_0.05"]
        for h_label, _, _ in CELLS
    )
    if not s5_extreme:
        outcome_label = "positive_control_itself_not_extreme"
    elif any_s1_s4_rejects:
        outcome_label = "sensitivity_confirmed"
    else:
        outcome_label = "sensitivity_gap_confirmed"

    result["s5_shows_known_positive_extreme"] = s5_extreme
    result["any_s1_s4_rejects_at_0.05"] = any_s1_s4_rejects
    result["outcome_label_per_spec_outcomes_block"] = outcome_label

    dual_path_all_ok = all(cells_out[h]["dual_path_control"]["within_1e-9"] for h, _, _ in CELLS)
    result["dual_path_control_all_within_1e-9"] = dual_path_all_ok

    result["completed"] = True
    result["outcome"] = "completed_valid" if dual_path_all_ok else "invalid_measurement"
    if not dual_path_all_ok:
        result["reason"] = "Dual-path route1/route2 disagreement exceeded 1e-9 relative tolerance on at least one cell."

    _finish(result, t_start)


def _finish(result, t_start):
    result["wall_seconds"] = time.time() - t_start
    usage = resource.getrusage(resource.RUSAGE_SELF)
    # ru_maxrss is bytes on macOS/Darwin, KB on Linux
    peak_rss = usage.ru_maxrss * (1 if sys.platform == "darwin" else 1024)
    result["peak_rss_bytes"] = peak_rss
    result["certificate"] = {"kind": "none", "note": "Pure measurement/statistics run; no DLOG solve or relation claimed."}
    out_dir = os.path.normpath(os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "runs", "RUN-MONO-b1423c-1"))
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "raw-result.json"), "w") as f:
        json.dump(result, f, indent=2, sort_keys=True, default=str)
    print(json.dumps({k: result[k] for k in
                       ("completed", "outcome", "wall_seconds", "peak_rss_bytes")
                       if k in result}, indent=2))


if __name__ == "__main__":
    main()
