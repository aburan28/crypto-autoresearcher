"""EXP-FB3-001 family analysis: Holm-Bonferroni, growth slopes, prior cells.

Consumes the three size runs and the controls run and produces the family-level
record: one Holm family of 8 cells per size (6 new geometries + the 2 prior
H016/H017 cells), bootstrap CIs across the replicate axis, growth slopes of each
ratio against log2 N, and the pre-registered analytic-arm consequence checks.

This script performs no measurement of its own; it aggregates immutable run
records.  It states no research decision -- the verdict against the frozen
criteria is reported as a mechanical check of the criteria's clauses.

Usage:  python3 run_family.py --runs <dir> --out <raw-result.json>
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import resource
import sys
import time
from datetime import datetime, timezone

import numpy as np

import fb3_core as C
from run_battery import jsonable, now_iso, peak_mb

FAMILY_GEOMETRIES = ["high_bit_interval", "small_height", "mixed_two_base",
                     "coset_union", "greedy_optimized", "asymmetric_sizing"]
PRIOR_CELLS = ["prior_H016_qr_base", "prior_H017_small_multiples"]
SIZES = [14, 16, 18]


def load(path: str) -> dict:
    with open(path) as fh:
        return json.load(fh)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", required=True, help="experiments/EXP-FB3-001/runs")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    started = now_iso()
    t0 = time.time()
    lines: list[str] = []

    def log(msg: str) -> None:
        print(msg, flush=True)
        lines.append(msg)

    log("=== EXP-FB3-001 family analysis (Holm + growth arm) ===")
    log(f"started_at {started}")

    size_runs = {}
    for bits in SIZES:
        path = os.path.join(args.runs, f"RUN-FB3-001-N{bits}", "raw-result.json")
        size_runs[bits] = load(path)
        log(f"loaded {path}")
    ctrl = load(os.path.join(args.runs, "RUN-FB3-001-CTRL", "raw-result.json"))
    log("loaded RUN-FB3-001-CTRL/raw-result.json")

    # ------------------------------------------------------------------
    # Prior cells (H016 QR, H017 small multiples) from the recorded record.
    # They are NOT re-run; their recorded statistics enter the accounting.
    # ------------------------------------------------------------------
    prior = {"source": "inputs/h100_session/h016_base_yield.json via "
                       "RUN-FB3-001-CTRL port-fidelity control",
             "recorded_sizes_bits": [], "cells": {}}
    pf_cells = ctrl["controls"]["D_port_fidelity"]["cells"]
    for name, key in (("prior_H016_qr_base", "qr"),
                      ("prior_H017_small_multiples", "small_mult")):
        per_bits: dict[str, list] = {}
        for cell in pf_cells:
            der = cell["prior_cell_pvalues_derived_from_record"]
            bits = cell["recorded_bits"]
            mean = der["qr_mean"] if key == "qr" else der["small_mult_mean"]
            p_rp1 = (der["qr_two_sided_convention_r_plus_1"] if key == "qr"
                     else der["small_mult_two_sided_convention_r_plus_1"])
            p_h016 = (der["qr_two_sided_h016_convention"] if key == "qr"
                      else der["small_mult_two_sided_h016_convention"])
            per_bits.setdefault(str(bits), []).append({
                "p": cell["p"], "N": cell["recorded_N"], "B": cell["recorded_B"],
                "sampled_mean": mean, "sampled_random_mean": der["random_mean"],
                "ratio_sampled": mean / der["random_mean"] if der["random_mean"] else None,
                "null_mean": der["null_mean"], "n_null_draws": der["n_null_draws"],
                "p_two_sided_r_plus_1": p_rp1,
                "p_two_sided_h016_convention": p_h016,
            })
        prior["cells"][name] = {
            "per_recorded_size": per_bits,
            "measurement_basis": "sampled over 800 uniform targets (the prior "
                                 "protocol); NOT exact whole-group counting",
            "recorded_at_bits": sorted(per_bits),
        }
    prior["recorded_sizes_bits"] = sorted({c["recorded_bits"] for c in pf_cells})

    # ------------------------------------------------------------------
    # Per-size family table.
    # ------------------------------------------------------------------
    family: dict[str, dict] = {}
    ratio_series: dict[str, dict[int, dict[str, list[float]]]] = {}
    for bits in SIZES:
        run = size_runs[bits]
        cells = run["cells"]
        entry: dict[str, dict] = {}
        pvals_primary: dict[str, float | None] = {}
        pvals_coverage: dict[str, float | None] = {}
        for geometry in FAMILY_GEOMETRIES:
            sub = [c for c in cells if c["geometry"] == geometry]
            measured = [c for c in sub if c.get("terminal_state") == "measured"]
            if not measured:
                entry[geometry] = {
                    "terminal_state": "infeasible",
                    "n_cells": len(sub),
                    "reason": sub[0].get("reason") if sub else "cell absent",
                }
                pvals_primary[geometry] = None
                pvals_coverage[geometry] = None
                continue
            rec: dict = {"terminal_state": "measured", "n_replicates": len(measured),
                         "evaluation_domain": measured[0]["evaluation_domain"],
                         "N_values": sorted({c["N"] for c in measured}),
                         "B_values": sorted({c["B"] for c in measured})}
            for key in C.STAT_KEYS:
                vals = [c["metrics"][key]["ratio"] for c in measured]
                raws = [c["stats"][key] for c in measured]
                nullm = [c["metrics"][key]["null_mean"] for c in measured]
                ps = [c["metrics"][key]["p_two_sided"] for c in measured]
                ps_h = [c["metrics"][key]["p_two_sided_h016_convention"]
                        for c in measured]
                by_curve: dict[int, list[float]] = {}
                for c in measured:
                    by_curve.setdefault(c["curve_index"], []).append(
                        c["metrics"][key]["ratio"])
                rec[key] = {
                    "exact_cell_value_mean": float(np.mean(raws)),
                    "null_mean_mean": float(np.mean(nullm)),
                    "ratio_point_estimate": float(np.mean(vals)),
                    "bootstrap_replicate_axis": C.bootstrap_ci(
                        vals, C.FROZEN["bootstrap_resamples"],
                        C.FROZEN["bootstrap_seed"] + bits),
                    "bootstrap_curve_cluster": C.cluster_bootstrap_ci(
                        by_curve, C.FROZEN["bootstrap_resamples"],
                        C.FROZEN["bootstrap_seed"] + bits + 1),
                    "permutation_p_two_sided_max": float(np.max(ps)),
                    "permutation_p_two_sided_mean": float(np.mean(ps)),
                    "permutation_p_two_sided_min": float(np.min(ps)),
                    "permutation_p_h016_convention_mean": float(np.mean(ps_h)),
                    "direction": ("above_null" if float(np.mean(vals)) > 1
                                  else "below_null" if float(np.mean(vals)) < 1
                                  else "equal_to_null"),
                }
                ratio_series.setdefault(geometry, {}).setdefault(bits, {})[key] = vals
            # Family p-value per cell: the mean over replicates of the
            # permutation p-value (declared before execution; the max and min
            # are also reported so the choice is auditable).
            pvals_primary[geometry] = rec["mean"]["permutation_p_two_sided_mean"]
            pvals_coverage[geometry] = rec["coverage"]["permutation_p_two_sided_mean"]
            entry[geometry] = rec
        # prior cells occupy their family slots
        for name in PRIOR_CELLS:
            pc = prior["cells"][name]["per_recorded_size"].get(str(bits))
            if pc:
                ps = [v["p_two_sided_r_plus_1"] for v in pc]
                entry[name] = {
                    "terminal_state": "prior_recorded_cell",
                    "n_recorded_curves": len(pc),
                    "p_two_sided_r_plus_1_mean": float(np.mean(ps)),
                    "p_two_sided_r_plus_1_min": float(np.min(ps)),
                    "p_two_sided_r_plus_1_max": float(np.max(ps)),
                    "p_two_sided_h016_convention_mean": float(np.mean(
                        [v["p_two_sided_h016_convention"] for v in pc])),
                    "ratio_sampled_mean": float(np.mean(
                        [v["ratio_sampled"] for v in pc])),
                    "detail": pc,
                }
                pvals_primary[name] = float(np.mean(ps))
                pvals_coverage[name] = None
            else:
                entry[name] = {
                    "terminal_state": "censored_not_recorded_at_this_size",
                    "recorded_at_bits": prior["cells"][name]["recorded_at_bits"],
                    "note": "the prior cells were recorded at 2^14 and 2^17 only; "
                            "the family slot is retained so the Holm family size "
                            "stays 8 at every size (conservative)",
                }
                pvals_primary[name] = None
                pvals_coverage[name] = None
        holm_primary = C.holm(pvals_primary, C.FROZEN["holm_alpha"])
        holm_coverage = C.holm(pvals_coverage, C.FROZEN["holm_alpha"])
        family[str(bits)] = {
            "cells": entry,
            "holm_primary_mean_yield_ratio": holm_primary,
            "holm_secondary_coverage_ratio": holm_coverage,
            "family_size": holm_primary["family_size"],
            "primary_metric": "exact mean yield ratio (structured / matched "
                              "random), whole group except greedy_optimized "
                              "(held-out half)",
        }
        log(f"-- size 2^{bits}: family_size={holm_primary['family_size']} "
            f"rejections={sum(1 for v in holm_primary['cells'].values() if v['reject_at_alpha'])}")

    # ------------------------------------------------------------------
    # Growth arm: slope of each ratio against log2 N.
    # ------------------------------------------------------------------
    growth: dict[str, dict] = {}
    for geometry, per_size in ratio_series.items():
        growth[geometry] = {}
        for key in C.STAT_KEYS:
            series = {bits: per_size[bits][key] for bits in sorted(per_size)
                      if key in per_size[bits]}
            growth[geometry][key] = C.growth_slope(
                series, C.FROZEN["bootstrap_resamples"],
                C.FROZEN["bootstrap_seed"] + 77)
        gm = growth[geometry]["mean"]
        log(f"   growth {geometry:24s} mean_slope={gm['slope']:+.6f} "
            f"ci95={[round(v, 6) for v in gm['ci95']]} "
            f"cov_slope={growth[geometry]['coverage']['slope']:+.6f} "
            f"ci95={[round(v, 6) for v in growth[geometry]['coverage']['ci95']]}")

    # ------------------------------------------------------------------
    # Non-family measured arms (secondary typings) and exploratory arms.
    # These cannot satisfy the frozen success criterion and are reported
    # separately from the pre-registered family.
    # ------------------------------------------------------------------
    non_family: dict[str, dict] = {}
    extra_geoms = sorted({c["geometry"] for bits in SIZES
                          for c in size_runs[bits]["cells"]
                          if c["geometry"] not in FAMILY_GEOMETRIES})
    for geometry in extra_geoms:
        per_size: dict[int, dict[str, list[float]]] = {}
        entry: dict[str, dict] = {"per_size": {}}
        for bits in SIZES:
            sub = [c for c in size_runs[bits]["cells"]
                   if c["geometry"] == geometry
                   and c.get("terminal_state") == "measured"]
            if not sub:
                continue
            entry["per_size"][str(bits)] = {
                key: {"ratio_mean": float(np.mean([c["metrics"][key]["ratio"]
                                                   for c in sub])),
                      "exact_value_mean": float(np.mean([c["stats"][key]
                                                         for c in sub]))}
                for key in C.STAT_KEYS}
            per_size[bits] = {key: [c["metrics"][key]["ratio"] for c in sub]
                              for key in C.STAT_KEYS}
        entry["growth"] = {
            key: C.growth_slope({b: per_size[b][key] for b in sorted(per_size)},
                                C.FROZEN["bootstrap_resamples"],
                                C.FROZEN["bootstrap_seed"] + 91)
            for key in C.STAT_KEYS} if len(per_size) > 1 else {}
        entry["family_membership"] = ("not a pre-registered family cell; "
                                      "reported for completeness")
        non_family[geometry] = entry

    exploratory: dict[str, dict] = {}
    arms = sorted({e["arm"] for bits in SIZES
                   for e in size_runs[bits]["exploratory"]})
    for arm in arms:
        entry = {"per_size": {}, "kind": None}
        per_size = {}
        for bits in SIZES:
            sub = [e for e in size_runs[bits]["exploratory"]
                   if e["arm"] == arm and e.get("state") == "measured"]
            if not sub:
                continue
            entry["kind"] = sub[0].get("kind")
            rec = {"n": len(sub),
                   "exact_mean": float(np.mean([e["stats"]["mean"] for e in sub])),
                   "exact_coverage": float(np.mean([e["stats"]["coverage"]
                                                    for e in sub])),
                   "exact_concentration": float(np.mean([e["stats"]["concentration"]
                                                         for e in sub])),
                   "closed_form_total_ok": all(
                       e.get("closed_form_total_ok",
                             e["exact_total"] == e["closed_form_total"])
                       for e in sub)}
            if "metrics" in sub[0]:
                rec |= {f"ratio_{key}": float(np.mean([e["metrics"][key]["ratio"]
                                                      for e in sub]))
                        for key in C.STAT_KEYS}
                per_size[bits] = {key: [e["metrics"][key]["ratio"] for e in sub]
                                  for key in C.STAT_KEYS}
            if "effective_base_size" in sub[0]:
                rec["effective_base_size"] = sorted({e["effective_base_size"]
                                                     for e in sub})
                rec["identity_holds_with_effective_size"] = all(
                    e["identity_holds_with_effective_size"] for e in sub)
            entry["per_size"][str(bits)] = rec
        if len(per_size) > 1:
            entry["growth"] = {
                key: C.growth_slope({b: per_size[b][key] for b in sorted(per_size)},
                                    C.FROZEN["bootstrap_resamples"],
                                    C.FROZEN["bootstrap_seed"] + 93)
                for key in C.STAT_KEYS}
        exploratory[arm] = entry

    # ------------------------------------------------------------------
    # Pre-registered analytic arm: consequences (i)-(iv) against measurement.
    # ------------------------------------------------------------------
    all_cells = [c for bits in SIZES for c in size_runs[bits]["cells"]
                 if c.get("terminal_state") == "measured"]
    whole = [c for c in all_cells if c["evaluation_domain"] == "whole_group"]
    untyped_whole = [c for c in whole
                     if c["geometry"] in ("high_bit_interval", "small_height",
                                          "coset_union")]
    cons_i = {
        "statement": "the exact mean per-target yield equals C(B+m-1,m)/N for "
                     "every base of size B, independent of geometry",
        "n_cells_checked": len(untyped_whole),
        "max_abs_deviation_of_mean_from_closed_form": max(
            abs(c["stats"]["mean"] - c["closed_form_total"] / c["N"])
            for c in untyped_whole),
        "max_abs_mean_ratio_minus_one": max(
            abs(c["metrics"]["mean"]["ratio"] - 1.0) for c in untyped_whole),
        "all_untyped_mean_ratios_exactly_one": all(
            c["metrics"]["mean"]["ratio"] == 1.0 for c in untyped_whole),
        "closed_form_total_control_all_pass": all(
            c["closed_form_total_ok"] for c in all_cells),
    }
    cons_i["status"] = ("CONFIRMED" if (cons_i["max_abs_deviation_of_mean_from_closed_form"]
                                       < 1e-12
                                       and cons_i["closed_form_total_control_all_pass"])
                        else "CONTRADICTED")
    slopes_untyped = {g: growth[g]["mean"] for g in
                      ("high_bit_interval", "small_height", "coset_union")
                      if g in growth}
    cons_ii = {
        "statement": "the growth slope of the mean-yield ratio versus log N is "
                     "identically zero for matched-size untyped bases",
        "slopes": {g: v["slope"] for g, v in slopes_untyped.items()},
        "cis95": {g: v["ci95"] for g, v in slopes_untyped.items()},
        "all_slopes_zero": all(v["slope"] == 0.0 for v in slopes_untyped.values()),
    }
    cons_ii["status"] = "CONFIRMED" if cons_ii["all_slopes_zero"] else "CONTRADICTED"
    viol = [c for c in all_cells
            if c["stats"]["coverage"] > min(1.0, c["stats"]["mean"]) + 1e-12]
    eq_ok = all((abs(c["stats"]["coverage"] - c["stats"]["mean"]) < 1e-12)
                == (c["stats"]["max_count"] <= 1) for c in all_cells)
    cov_ratios = {g: family[str(SIZES[-1])]["cells"][g]["coverage"]["ratio_point_estimate"]
                  for g in FAMILY_GEOMETRIES
                  if family[str(SIZES[-1])]["cells"][g]["terminal_state"] == "measured"}
    cons_iii = {
        "statement": "coverage <= min(1, mean) with equality iff no target has "
                     "two decompositions; additive structure can only lower "
                     "coverage at matched size",
        "n_cells_checked": len(all_cells),
        "n_bound_violations": len(viol),
        "equality_condition_holds_everywhere": bool(eq_ok),
        "coverage_ratio_at_largest_size": cov_ratios,
        "n_geometries_with_coverage_ratio_above_1": sum(
            1 for v in cov_ratios.values() if v > 1.0),
        "geometries_above_1": {g: v for g, v in cov_ratios.items() if v > 1.0},
    }
    cons_iii["status"] = ("CONFIRMED" if (not viol and eq_ok) else "CONTRADICTED")
    typed = [c for c in whole if c["geometry"].startswith("mixed_two_base")
             or c["geometry"] == "asymmetric_sizing"]
    cons_iv = {
        "statement": "typed decompositions with B1+B2+B3 = B total B1*B2*B3 <= "
                     "B^3/27 < C(B+2,3) ~ B^3/6, so typing is a fixed penalty "
                     "of about 4.5x rather than a lever",
        "n_typed_cells": len(typed),
        "typed_over_untyped_total": sorted({
            round(c["extra"]["typed_total_vs_untyped_total"], 8) for c in typed}),
        "balanced_split_penalty_measured": None,
        "all_typed_totals_below_untyped": all(
            c["closed_form_total"] < C.total_untyped_m3(c["B"]) for c in typed),
        "all_typed_ratios_below_1": all(
            c["metrics"]["mean"]["ratio"] < 1.0 for c in typed),
    }
    for bits in SIZES:
        for c in size_runs[bits]["cells"]:
            if c["geometry"] == "asymmetric_sizing" and c.get("extra"):
                for item in c["extra"]["ladder"]:
                    if item["weights"] == [1, 1, 1]:
                        cons_iv["balanced_split_penalty_measured"] = (
                            1.0 / item["typed_total_vs_untyped_total"])
                        break
                break
        if cons_iv["balanced_split_penalty_measured"]:
            break
    cons_iv["status"] = ("CONFIRMED" if (cons_iv["all_typed_totals_below_untyped"]
                                        and cons_iv["all_typed_ratios_below_1"])
                         else "CONTRADICTED")

    # ------------------------------------------------------------------
    # Mechanical check of the frozen criteria (report, not decision).
    # ------------------------------------------------------------------
    criterion_rows = []
    for geometry in FAMILY_GEOMETRIES:
        rows = []
        for bits in SIZES:
            cell = family[str(bits)]["cells"][geometry]
            if cell["terminal_state"] != "measured":
                rows.append({"bits": bits, "state": cell["terminal_state"]})
                continue
            holm_entry = family[str(bits)]["holm_primary_mean_yield_ratio"]["cells"][geometry]
            boot = cell["mean"]["bootstrap_replicate_axis"]
            fam_ci = boot["ci99.375"]
            rows.append({
                "bits": bits, "state": "measured",
                "ratio": cell["mean"]["ratio_point_estimate"],
                "ci95": boot["ci95"], "family_wise_ci": fam_ci,
                "ci95_excludes_1": not (boot["ci95"][0] <= 1.0 <= boot["ci95"][1]),
                "family_wise_ci_excludes_1": not (fam_ci[0] <= 1.0 <= fam_ci[1]),
                "p_holm": holm_entry["p_holm"],
                "holm_rejects": holm_entry["reject_at_alpha"],
                "direction": cell["mean"]["direction"],
            })
        gm = growth.get(geometry, {}).get("mean", {})
        slope = gm.get("slope")
        slope_ci = gm.get("ci95")
        slope_excl0 = (slope_ci is not None
                       and not (slope_ci[0] <= 0.0 <= slope_ci[1]))
        alive_dir = bool(slope is not None and slope > 0)
        any_ci_excl = any(r.get("family_wise_ci_excludes_1") for r in rows)
        any_above_1 = any(r.get("direction") == "above_null" for r in rows)
        criterion_rows.append({
            "geometry": geometry, "per_size": rows,
            "growth_slope_mean_ratio": slope,
            "growth_slope_ci95": slope_ci,
            "slope_excludes_0": slope_excl0,
            "slope_in_alive_direction": alive_dir,
            "family_wise_ci_excludes_1_at_some_size": any_ci_excl,
            "any_size_shows_advantage_direction": any_above_1,
            "meets_success_criterion": bool(any_ci_excl and slope_excl0
                                            and alive_dir and any_above_1),
        })
        # coverage arm, reported separately (secondary metric, AMD-5)
        criterion_rows[-1]["coverage_arm"] = {
            "ratio_per_size": {str(b): (family[str(b)]["cells"][geometry]
                                        ["coverage"]["ratio_point_estimate"]
                                        if family[str(b)]["cells"][geometry]
                                        ["terminal_state"] == "measured" else None)
                               for b in SIZES},
            "family_wise_ci_per_size": {
                str(b): (family[str(b)]["cells"][geometry]["coverage"]
                         ["bootstrap_replicate_axis"]["ci99.375"]
                         if family[str(b)]["cells"][geometry]["terminal_state"]
                         == "measured" else None) for b in SIZES},
            "slope": growth.get(geometry, {}).get("coverage", {}).get("slope"),
            "slope_ci95": growth.get(geometry, {}).get("coverage", {}).get("ci95"),
        }

    n_meets = sum(1 for r in criterion_rows if r["meets_success_criterion"])
    verdict = {
        "success_criterion_verbatim":
            "At least one geometry with Holm-adjusted yield ratio CI excluding 1 "
            "AND a growth slope vs log N excluding 0 in the alive direction "
            "across 2^14..2^18 (exponent-relevant; triggers a larger-N "
            "confirmation arm and feeds base selection for EXP-R6-001).",
        "falsification_criterion_verbatim":
            "All geometries within CIs / permutation bands at every N, or every "
            "nonzero effect constant across N: scoped KILL of the F3 family -- "
            "\"no signal seen at reachable scale,\" with the family-wise "
            "correction reported.",
        "n_geometries_meeting_success_criterion": n_meets,
        "success_criterion_met": bool(n_meets > 0),
        "operationalisation": {
            "alive_direction": "ratio > 1 (an ADVANTAGE over matched random); the "
                               "hypothesis statement is about an advantage that "
                               "grows, so a deficit is not the alive direction",
            "holm_adjusted_ci": "the family-wise (99.375% = 1 - 0.05/8) bootstrap "
                                "CI is used as the Holm-adjusted CI; Bonferroni "
                                "width is conservative relative to Holm",
            "primary_metric": "exact mean yield ratio",
            "note": "this is a mechanical evaluation of the frozen clauses by the "
                    "executor; the official decision belongs to the Coordinator",
        },
    }
    log(f"geometries meeting the frozen success criterion: {n_meets}")

    wall = time.time() - t0
    out = {
        "run_id": "RUN-FB3-001-FAMILY",
        "experiment_id": "EXP-FB3-001",
        "amendment_id": "EXP-FB3-001-AMD-001",
        "purpose": "family-level Holm correction, bootstrap CIs, growth slopes, "
                   "prior-cell accounting, and analytic-arm consequence checks",
        "inputs": {"size_runs": [f"RUN-FB3-001-N{b}" for b in SIZES],
                   "controls_run": "RUN-FB3-001-CTRL"},
        "prior_cells": prior,
        "family_by_size": family,
        "growth": growth,
        "non_family_measured_arms": non_family,
        "exploratory_arms": exploratory,
        "analytic_arm": {"consequence_i_mean_is_geometry_independent": cons_i,
                         "consequence_ii_slope_identically_zero": cons_ii,
                         "consequence_iii_coverage_bound": cons_iii,
                         "consequence_iv_typing_penalty": cons_iv},
        "frozen_criteria_check": {"per_geometry": criterion_rows,
                                  "verdict": verdict},
        "controls_rollup": {
            "per_size": {str(b): size_runs[b]["controls"] for b in SIZES},
            "controls_run_verdicts": ctrl["control_verdicts"],
        },
        "timing": {"started_at": started, "finished_at": now_iso(),
                   "wall_clock_seconds": wall},
        "peak_memory_mb": peak_mb(),
        "environment": {"python": platform.python_version(),
                        "numpy": np.__version__, "platform": platform.platform()},
    }
    with open(args.out, "w") as fh:
        json.dump(out, fh, indent=1, default=jsonable)
    log(f"wrote {args.out}")
    log(f"wall_clock_seconds {wall:.1f} peak_memory_mb {peak_mb():.1f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
