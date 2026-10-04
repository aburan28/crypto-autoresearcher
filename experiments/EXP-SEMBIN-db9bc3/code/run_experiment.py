"""Driver for EXP-SEMBIN-db9bc3 / RUN-SEMBIN-251fd3.

Runs the seven arms IN THE CONTRACT'S ORDER -- C, R (gate), N, K, P, M, I --
and writes each arm's deliverable to the run directory THE MOMENT it completes,
so that a session killed mid-run leaves a partial but honest record on disk
(attempt 1 of this task died with everything still in memory).

Every number produced by arms C (closed forms), N, K, P, M and I is MODELED: a
closed-form evaluation of the source's formulas at stated parameters.  Only ARM
C's enumeration section is MEASURED (exhaustive integer counts at n <= 20).
No curve of cryptographic size is touched, no system is solved, no algebra
engine is used, and nothing here is a statement about any curve's security.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import platform
import resource
import subprocess
import sys
import time
from datetime import datetime, timezone

import numpy as np

import arm_c_coset as C
import arm_i_independent_memory as I
import nagao_cost as N
import semaev_repro as R
import selftest

HERE = os.path.dirname(os.path.abspath(__file__))
EXP_DIR = os.path.dirname(HERE)
RUN_ID = "RUN-SEMBIN-251fd3"
EXP_ID = "EXP-SEMBIN-db9bc3"
RUN_DIR = os.path.join(EXP_DIR, "runs", RUN_ID)
REPO = os.path.abspath(os.path.join(EXP_DIR, "..", ".."))

SEED_BASE = 20260913
MEMORY_CAP_BYTES = 2 * 1024 ** 3

SCOPE_STATEMENT = (
    "AFFECTED-VERSUS-SAFE SCOPE (required on every deliverable). This run is "
    "log2-domain arithmetic over a declared grid, conditional on Nagao's "
    "Proposition 5 and the first fall degree assumption, both GRANTED and "
    "untested here. 'Nagao ahead' at a cell means: under THIS program's "
    "enumeration of the absorbed terms T1-T5, at THAT (n, omega, C_0, metric, "
    "monomial-count reading, memory reading), the charged closed form is "
    "smaller than van Oorschot-Wiener's at the Pareto minimum of its own "
    "curve. It is NOT a statement that any curve -- B-163, B-233, B-283, "
    "B-409, B-571, their K- siblings, or any other -- is affected, weakened or "
    "attacked, and no row of this run supports such a reading in either "
    "direction. The units of the two sides are not identical (F_2 Macaulay "
    "operations against group operations; no conversion applied, direction "
    "disclosed in cost-surface.json unit_conversion_sensitivity). By the "
    "hypothesis's quantifier_order, a table at n <= 571 cannot contradict an "
    "asymptotic theorem whose n_0 is unstated; it can only describe "
    "applicability at these parameters. Observations only; no hypothesis "
    "status, evidence record, decision or knowledge promotion is made here.")

_T0 = time.time()


def log(msg: str) -> None:
    line = f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')} +{time.time() - _T0:7.1f}s] {msg}"
    print(line, flush=True)


def write_json(name: str, payload) -> str:
    path = os.path.join(RUN_DIR, name)
    with open(path, "w") as fh:
        json.dump(payload, fh, indent=1, default=_json_default)
    log(f"wrote {name} ({os.path.getsize(path)} bytes)")
    return path


def _json_default(o):
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    if hasattr(o, "numerator"):
        return str(o)
    return str(o)


def sha256_of(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git(*args) -> str:
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True,
                          text=True, check=False).stdout.strip()


def peak_rss_bytes() -> int:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024


# ---------------------------------------------------------------------------
# ARM C
# ---------------------------------------------------------------------------


def arm_c() -> dict:
    log("ARM C: closed-form bounds")
    ns = N.N_FIPS
    bounds = []
    for p in (2, 3, 5):
        for n in ns:
            a = C.bound_A(n, p)
            b = C.bound_B(n, p)
            bounds.append({
                "n": n, "p": p,
                "bound_A_no_empty_coset": {k: v for k, v in a.items()},
                "bound_B_product_within_1_bit": {
                    k: v for k, v in b.items() if k != "deficit_profile"},
                "bound_B_deficit_profile_C0_1_to_16": [
                    {"C_0": r["C_0"], "m": r["m"],
                     "total_deficit_bits": r["total_deficit_bits"]}
                    for r in b["deficit_profile"][:16]],
                "crude_readings": C.crude_bounds(n, p),
                "declared_C_0_range_violating_bound_A": [
                    c0 for c0 in N.C0_RANGE
                    if a["C_0_min"] is not None and c0 < a["C_0_min"]],
                "declared_C_0_range_violating_bound_B": [
                    c0 for c0 in N.C0_RANGE
                    if b["C_0_min"] is not None and c0 < b["C_0_min"]],
                "searched_coset_reading_at_C0_2": C.searched_coset_reading(n, p, 2),
                "modeled_not_measured": True,
            })
    # growth check across a wide n range so the order of growth is read off
    # numbers rather than asserted
    growth = []
    for n in (64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536):
        growth.append({"n": n, "bound_A_C0_min": C.bound_A(n, 2)["C_0_min"],
                       "bound_B_C0_min": C.bound_B(n, 2)["C_0_min"],
                       "log2_n": math.log2(n),
                       "log2_log2_n": math.log2(math.log2(n))})

    log("ARM C: exact enumeration (MEASURED), n <= 20, k <= 4")
    cells, unreached = [], []
    for n in (8, 10, 12, 14, 16, 18, 20):
        for k in (1, 2, 3, 4):
            rss = peak_rss_bytes()
            if rss > MEMORY_CAP_BYTES * 0.8:
                unreached.append({"n": n, "k": k,
                                  "reason": f"peak RSS {rss} approaching 2 GB cap; "
                                            "scope limit of the enumeration, not a "
                                            "statement about coset occupancy"})
                continue
            t = time.time()
            try:
                cell = C.enumerate_cell(n, k, SEED_BASE + 10 * n + k)
                cell["wall_seconds"] = time.time() - t
                cells.append(cell)
            except MemoryError as exc:
                unreached.append({"n": n, "k": k, "reason": f"MemoryError: {exc}"})
        log(f"  enumeration n={n} done, peak RSS {peak_rss_bytes() / 1e6:.0f} MB")

    # comparison summary
    z = [c["curve_minus_null_in_null_sd"] for c in cells
         if c["curve_minus_null_in_null_sd"] is not None]
    comparison = {
        "cells_enumerated": len(cells),
        "cells_unreached": len(unreached),
        "curve_minus_null_in_null_sd": {
            "values": z,
            "mean": float(np.mean(z)) if z else None,
            "max_abs": float(np.max(np.abs(z))) if z else None,
            "cells_beyond_2_sd": int(sum(1 for v in z if abs(v) > 2.0)),
            "cells_beyond_3_sd": int(sum(1 for v in z if abs(v) > 3.0)),
        },
        "curve_structured_V_vs_binomial_prediction": [
            {"n": c["n"], "k": c["k"],
             "observed_empty_structured_V": c["empty_cosets_curve_structured_V"],
             "observed_empty_random_V_mean": float(np.mean(c["empty_cosets_curve_random_V"])),
             "predicted_binomial": c["predicted_empty_cosets_binomial"],
             "null_mean": c["null_mean"], "null_sd": c["null_sd"],
             "structured_V_only_minus_null_in_null_sd": (
                 None if c["null_sd"] == 0.0 else
                 (c["empty_cosets_curve_structured_V"] - c["null_mean"]) / c["null_sd"]),
             "random_V_mean_minus_null_in_null_sd": (
                 None if c["null_sd"] == 0.0 else
                 (float(np.mean(c["empty_cosets_curve_random_V"])) - c["null_mean"]) / c["null_sd"])}
            for c in cells],
        "structured_V_only_max_abs_sd": max(
            (abs((c["empty_cosets_curve_structured_V"] - c["null_mean"]) / c["null_sd"])
             for c in cells if c["null_sd"] > 0.0), default=None),
        "structured_V_only_cells_beyond_2_sd": [
            {"n": c["n"], "k": c["k"],
             "z": (c["empty_cosets_curve_structured_V"] - c["null_mean"]) / c["null_sd"]}
            for c in cells if c["null_sd"] > 0.0
            and abs((c["empty_cosets_curve_structured_V"] - c["null_mean"]) / c["null_sd"]) > 2.0],
        "structured_V_caveat": ("structured V = span{1,x,...,x^{k-1}} is ONE draw per cell; "
                                "a single-draw z-score against 16 null draws is reported, not "
                                "tested; 28 cells at |z| > 2 would be expected ~1.3 times by "
                                "chance under the null"),
        "reading": ("HEUR-1's random model is compared with the exact curve "
                    "count at each cell; the per-cell z-scores are reported and "
                    "no verdict on the heuristic is given here"),
    }
    out = {
        "arm": "C", "runs_first": True,
        "closed_forms": C.CLOSED_FORMS,
        "bounds_at_each_n_p": bounds,
        "order_of_growth_table_p2": growth,
        "headline_p2": {
            "bound_A_C0_min_eps_0p05": {n: C.bound_A(n, 2)["C_0_min"] for n in ns},
            "bound_B_C0_min_1_bit": {n: C.bound_B(n, 2)["C_0_min"] for n in ns},
            "hypothesis_P1_quoted_9p2_at_571_is_the_crude_reading_p_to_C0_ge_n":
                C.crude_bounds(571, 2)["C_0_from_p_to_C0_ge_n_real"],
        },
        "exact_enumeration_measured": cells,
        "unreached_cells": unreached,
        "comparison": comparison,
        "enumeration_scope": ("p = 2, n in {8,...,20}, k in {1,...,4}, one seeded "
                              "random curve y^2+xy=x^3+Ax^2+B per cell, structured "
                              "V = span{1,x,..,x^{k-1}} plus 4 random k-dim V; null "
                              "= 8 uniformly random subsets of the same size. "
                              "Exhaustive at those parameters and nothing more."),
        "seeds": {"formula": "SEED_BASE + 10 n + k, SEED_BASE = 20260913"},
        "scope_statement": SCOPE_STATEMENT,
    }
    write_json("c0-lower-bound.json", out)
    return out


# ---------------------------------------------------------------------------
# ARM R
# ---------------------------------------------------------------------------


def arm_r() -> dict:
    log("ARM R: reproduction gate")
    cells = R.reproduction_cells()
    gate_groups = [g for g in {c["group"] for c in cells}
                   if "UNCORRECTED" not in g]
    gate_cells = [c for c in cells if c["group"] in gate_groups]
    control_cells = [c for c in cells if c["group"] not in gate_groups]
    fails = [c for c in gate_cells if not c["passed"]]
    errs = [c["abs_error_bits"] for c in gate_cells if c["abs_error_bits"] is not None]
    errs_1e3 = [c["abs_error_bits"] for c in gate_cells
                if c["abs_error_bits"] is not None and c["tolerance"] == 1e-3]
    # the UNCORRECTED figures must NOT be produced by the eq11 pipeline
    uncorrected_by_eq11 = []
    for d_sat, tgv, corrected in zip((4, 5, 6, 7), (186.7, 187.2, 212.8, 240.3),
                                     (181.7, 185.5, 212.8, 240.3)):
        v = R.semaev_stage1_log2(571, 12, 3.0, "eq11", "ceiled", d_sat, 4)["log2_stage1"]
        differs = abs(tgv - corrected) > 5e-2
        uncorrected_by_eq11.append({"d_sat": d_sat, "uncorrected_target": tgv,
                                    "corrected_target": corrected,
                                    "uncorrected_differs_from_corrected": differs,
                                    "eq11_pipeline_value": v,
                                    "pipeline_matches_uncorrected": abs(v - tgv) <= 5e-2,
                                    "pipeline_reproduces_uncorrected_where_it_differs":
                                        differs and abs(v - tgv) <= 5e-2,
                                    "note": (None if differs else
                                             "at d_sat >= 6 the d_sat term dominates and the two "
                                             "charges print the same figure; matching it is not "
                                             "a failure signal here")})
    degenerate = [R.degenerate_slice(n, R.semaev_optimal_m(n)) for n in N.N_FIPS]
    degenerate_ok = all(d["unceiled"]["agrees_to_1e_9"] and d["ceiled"]["agrees_to_1e_9"]
                        for d in degenerate)
    passed = (not fails) and degenerate_ok
    out = {
        "arm": "R", "runs_second": True, "is_hard_gate": True,
        "passed": passed,
        "gate_cells_total": len(gate_cells),
        "gate_cells_failed": len(fails),
        "worst_abs_error_bits_all_gate_cells": max(errs) if errs else None,
        "worst_abs_error_bits_at_1e-3_tolerance_cells": max(errs_1e3) if errs_1e3 else None,
        "n_cells_at_1e-3_tolerance": len(errs_1e3),
        "tolerance_policy": R.reproduction_cells.__doc__,
        "cells": gate_cells,
        "uncorrected_figures_control": {
            "note": ("the m!-only figures are reproduced BY NAME under the m!-only "
                     "charge to show the pipeline separates the two charges; the "
                     "eq11 pipeline must NOT produce them"),
            "m_only_pipeline_reproduces_m_only_targets": control_cells,
            "eq11_pipeline_against_uncorrected_targets": uncorrected_by_eq11,
            "eq11_pipeline_reproduces_an_uncorrected_figure_where_it_differs_from_corrected":
                any(u["pipeline_reproduces_uncorrected_where_it_differs"] for u in uncorrected_by_eq11),
        },
        "degenerate_slice": degenerate,
        "degenerate_slice_all_exact": degenerate_ok,
        "sign_convention_note": R.compare_8d123b.__doc__,
        "scope_statement": SCOPE_STATEMENT,
    }
    write_json("reproduction.json", out)
    return out


# ---------------------------------------------------------------------------
# ARM N
# ---------------------------------------------------------------------------


def arm_n() -> dict:
    log("ARM N: cost surface")
    rows = []
    for n in N.N_FIPS:
        for omega in N.OMEGA_SET + [N.OMEGA_SOURCE_OWN]:
            for c0 in N.C0_RANGE:
                for reading in N.READINGS:
                    cell = N.nagao_cell(n, 2, c0, omega, reading)
                    cell["omega_is_source_own_2p7_not_in_committed_set"] = (omega == N.OMEGA_SOURCE_OWN)
                    cell["T5b_relation_matrix_log2_entries"] = 2.0 * cell["T3_coset_constant_log2"]
                    cell["margins"] = {}
                    for metric in N.METRICS:
                        for mr in N.MEMORY_READINGS:
                            cell["margins"][f"{metric}|{mr}"] = N.margin(cell, metric, mr)
                    rows.append(cell)
    log(f"  {len(rows)} cells")

    # crossover surface
    log("ARM N: crossover surface")
    xo = []
    for omega in N.OMEGA_SET + [N.OMEGA_SOURCE_OWN]:
        for c0 in N.C0_RANGE:
            for metric in N.METRICS:
                for reading in N.READINGS:
                    for mr in N.MEMORY_READINGS:
                        x = N.crossover(2, c0, omega, metric, reading, mr, 16, 2000)
                        x["omega_is_source_own_2p7"] = (omega == N.OMEGA_SOURCE_OWN)
                        x["C_0_satisfies_ARM_C_bound_A_at_crossover"] = (
                            None if x["crossover_n"] is None else
                            N._bound_A_min(x["crossover_n"], 2) <= c0)
                        x["C_0_satisfies_ARM_C_bound_B_at_crossover"] = (
                            None if x["crossover_n"] is None else
                            N._bound_B_min(x["crossover_n"], 2) <= c0)
                        xo.append(x)
    log(f"  {len(xo)} crossover cells")

    # spreads at n = 571 (committed omega set only)
    t571 = [r for r in rows if r["n"] == 571 and not r["omega_is_source_own_2p7_not_in_committed_set"]]
    spreads = {}
    for metric in N.METRICS:
        for mr in N.MEMORY_READINGS:
            for reading in N.READINGS:
                key = f"{metric}|{mr}|{reading}"
                vals = {(r["omega"], r["C_0"]): r["margins"][f"{metric}|{mr}"]["nagao_metric_log2"]
                        for r in t571 if r["monomial_count_reading"] == reading}
                c0_spread = {om: max(v for (o, c), v in vals.items() if o == om)
                                 - min(v for (o, c), v in vals.items() if o == om)
                             for om in N.OMEGA_SET}
                om_spread = {c0: max(v for (o, c), v in vals.items() if c == c0)
                                 - min(v for (o, c), v in vals.items() if c == c0)
                             for c0 in N.C0_RANGE}
                bound_b = N._bound_B_min(571, 2)
                c0_spread_def = {om: max(v for (o, c), v in vals.items() if o == om and c >= bound_b)
                                     - min(v for (o, c), v in vals.items() if o == om and c >= bound_b)
                                 for om in N.OMEGA_SET}
                spreads[key] = {
                    "C_0_spread_bits_over_declared_range_per_omega": c0_spread,
                    "C_0_spread_bits_over_C_0_satisfying_bound_B_per_omega": c0_spread_def,
                    "omega_spread_bits_per_C_0": om_spread,
                    "max_C_0_spread_bits_declared_range": max(c0_spread.values()),
                    "max_C_0_spread_bits_bound_B_range": max(c0_spread_def.values()),
                    "max_omega_spread_bits": max(om_spread.values()),
                    "C_0_spread_exceeds_omega_spread_declared_range":
                        max(c0_spread.values()) > max(om_spread.values()),
                    "C_0_spread_exceeds_omega_spread_bound_B_range":
                        max(c0_spread_def.values()) > max(om_spread.values()),
                }
    omega_spread_theorem_form_571 = (3.0 - 2.376) * 8 * math.log2(571)

    # escalation flags: memory-charging metric, Nagao ahead at a FIPS label
    flags = []
    for r in rows:
        for key, mg in r["margins"].items():
            metric = key.split("|")[0]
            if metric in ("time_memory_product", "area_time_AT", "equal_rate_max") and mg["nagao_ahead"]:
                flags.append({"n": r["n"], "omega": r["omega"], "C_0": r["C_0"],
                              "reading": r["monomial_count_reading"],
                              "metric_and_memory_reading": key,
                              "margin_bits_nagao_minus_vow": mg["margin_bits_nagao_minus_vow"],
                              "C_0_satisfies_ARM_C_bound_A": r["C_0_satisfies_ARM_C_bound_A"],
                              "C_0_satisfies_ARM_C_bound_B_1bit": r["C_0_satisfies_ARM_C_bound_B_1bit"],
                              "omega_in_committed_set": not r["omega_is_source_own_2p7_not_in_committed_set"]})
    out = {
        "arm": "N",
        "grid": {"n": N.N_FIPS, "omega_committed": N.OMEGA_SET,
                 "omega_source_own_reported_not_a_4th_value": N.OMEGA_SOURCE_OWN,
                 "C_0": N.C0_RANGE, "metrics": N.METRICS, "readings": N.READINGS,
                 "memory_readings": N.MEMORY_READINGS, "p": 2, "d_F": 4},
        "sign_convention": "margin = Nagao - vOW in bits; POSITIVE means Nagao is WORSE",
        "vow_baseline": R.vow_pareto_minimum.__doc__,
        "column_definitions": N.__doc__,
        "cells": rows,
        "crossover_surface": xo,
        "crossover_surface_note": ("a SURFACE over (omega, C_0, metric, reading, memory "
                                   "reading); no single crossover number is reported"),
        "spreads_at_n_571": spreads,
        "omega_spread_of_theorem_form_n_8w_plus_1_at_571_bits": omega_spread_theorem_form_571,
        "escalation_flags_memory_charging_metric_nagao_ahead": flags,
        "escalation_note": ("cells listed above show, under THIS charging, the Nagao "
                            "closed form below vOW's Pareto minimum under a "
                            "memory-charging metric at a FIPS label. Per the contract's "
                            "claim_tier_and_review.escalation (a), these are FLAGGED for "
                            "review-breakthrough at max effort, non-degradable, core rule "
                            "12. They are NOT characterised as a result here."),
        "premise_contested_by_ARM_C": ("every cell carries C_0_satisfies_ARM_C_bound_A/B; "
                                       "cells violating either are computed and flagged, "
                                       "not dropped"),
        "unit_conversion_sensitivity": {n: N.unit_conversion_sensitivity(n) for n in N.N_FIPS},
        "modeled_not_measured": True,
        "scope_statement": SCOPE_STATEMENT,
    }
    write_json("cost-surface.json", out)
    write_concrete_cost(rows, xo, flags)
    return out


def write_concrete_cost(rows, xo, flags) -> None:
    import yaml
    sets = []
    for n in N.N_FIPS:
        entry = {"name": f"NIST/FIPS PUB 186-4 K-{n} and B-{n}", "security_parameter": f"n = {n}",
                 "vow_pareto_minimum_log2": {m: R.vow_pareto_minimum(n, m)["metric_log2"] for m in N.METRICS},
                 "cells": []}
        for r in rows:
            if r["n"] != n or r["omega_is_source_own_2p7_not_in_committed_set"]:
                continue
            entry["cells"].append({
                "omega": r["omega"], "C_0": r["C_0"], "reading": r["monomial_count_reading"],
                "m": r["m"], "N": r["N_frozen"],
                "T1_monomial_count_log2": round(r["T1_monomial_count_log2"], 4),
                "T2_linear_algebra_log2": round(r["T2_linear_algebra_exponent_log2"], 4),
                "T3_coset_constant_log2": round(r["T3_coset_constant_log2"], 4),
                "T4_inverse_yield_log2": round(r["T4_inverse_yield_log2"], 4),
                "T5_memory_log2_frozen_width": round(r["T5_memory_log2_frozen_width"], 4),
                "T5_memory_log2_dense_squared": round(r["T5_memory_log2_dense_width_squared"], 4),
                "time_log2_total": round(r["time_log2_total"], 4),
                "margins_nagao_minus_vow": {k: round(v["margin_bits_nagao_minus_vow"], 4)
                                            for k, v in r["margins"].items()},
                "C_0_satisfies_ARM_C_bound_A": r["C_0_satisfies_ARM_C_bound_A"],
                "C_0_satisfies_ARM_C_bound_B_1bit": r["C_0_satisfies_ARM_C_bound_B_1bit"],
            })
        sets.append(entry)
    doc = {"concrete_cost": {
        "id": f"run artifact of {RUN_ID}; NOT a ledger COST record (a COST id is a Coordinator act)",
        "hypothesis_id": "H-SEMBIN-4a80f3", "experiment_id": EXP_ID, "run_id": RUN_ID,
        "recorded_at": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "algorithm_ref": "Nagao ePrint 2015/984 Theorem 1, charged term by term (T1-T5) per H-SEMBIN-4a80f3",
        "cost_unit": ("log2 of F_2 Macaulay operations for Nagao time; log2 field elements for "
                      "Nagao memory; log2 group operations for vOW time; log2 bits for vOW memory. "
                      "No unit conversion applied; direction disclosed in cost-surface.json"),
        "bound_kind": "heuristic_estimate, MODELED not measured, conditional on Prop. 5 and the first fall degree assumption",
        "comparator_ref": "van Oorschot-Wiener at the Pareto minimum of T = W(1/M+1/w), Mem = 3n max(w,M), per EV-SEMBIN-71e5cd O-6/O-7",
        "sign_convention": "margin = Nagao - vOW; positive = Nagao worse",
        "metrics_defined": N.METRICS,
        "parameter_sets": sets,
        "crossover_surface": [{k: x[k] for k in ("omega", "C_0", "metric", "monomial_count_reading",
                                                  "memory_reading", "crossover_n", "reason_if_none",
                                                  "C_0_satisfies_ARM_C_bound_A_at_crossover",
                                                  "C_0_satisfies_ARM_C_bound_B_at_crossover")} for x in xo],
        "crossover_note": "a surface; never one number",
        "escalation_flags": flags,
        "optimistic_assumptions_restated": [
            "Proposition 5 (d_F <= 4 at p = 2) granted, proof omitted in the source",
            "first fall degree assumption granted",
            "HEUR-1 equidistribution of x-coordinates over F_2-affine cosets",
            "HEUR-2 Poisson yield",
            "Groebner cost charged as omega * log2(monomials) per Lemma 2, no constant",
            "no unit conversion between Macaulay F_2 operations and group operations",
        ],
        "affected_scope": "see scope_statement; no curve is asserted affected",
        "safe_scope": "see scope_statement; no curve is asserted safe either -- this run makes no security statement",
        "scope_statement": SCOPE_STATEMENT,
        "status": "run_artifact_observations_only",
    }}
    path = os.path.join(RUN_DIR, "concrete-cost.yaml")
    with open(path, "w") as fh:
        yaml.safe_dump(doc, fh, sort_keys=False, width=100)
    log(f"wrote concrete-cost.yaml ({os.path.getsize(path)} bytes)")


# ---------------------------------------------------------------------------
# ARM K
# ---------------------------------------------------------------------------


def arm_k() -> dict:
    log("ARM K: known-false object d_F = 5")
    rows = []
    for n in N.N_FIPS:
        for omega in N.OMEGA_SET:
            for c0 in N.C0_RANGE:
                for reading in N.READINGS:
                    c4 = N.nagao_cell(n, 2, c0, omega, reading, d_f=4)
                    c5 = N.nagao_cell(n, 2, c0, omega, reading, d_f=5)
                    nv = c4["N_frozen"]
                    # predicted rise, written from the degree ratio alone
                    if reading == "nagao_loose_N_to_the_d":
                        pred_time = omega * math.log2(nv)          # N^{5w}/N^{4w}
                    else:
                        pred_time = omega * math.log2((nv + 5) / 5)  # C(N+5,5)/C(N+4,4)
                    pred_mem = math.log2((nv + 5) / 5)
                    obs_time = c5["time_log2_total"] - c4["time_log2_total"]
                    obs_mem = c5["T5_memory_log2_frozen_width"] - c4["T5_memory_log2_frozen_width"]
                    rows.append({"n": n, "omega": omega, "C_0": c0, "reading": reading, "N": nv,
                                 "time_log2_dF4": c4["time_log2_total"], "time_log2_dF5": c5["time_log2_total"],
                                 "observed_time_rise_bits": obs_time, "predicted_time_rise_bits": pred_time,
                                 "time_rise_minus_predicted": obs_time - pred_time,
                                 "observed_memory_rise_bits": obs_mem, "predicted_memory_rise_bits": pred_mem,
                                 "memory_rise_minus_predicted": obs_mem - pred_mem,
                                 "cost_rose": obs_time > 0 and obs_mem > 0})
    dev = [abs(r["time_rise_minus_predicted"]) for r in rows]
    out = {"arm": "K", "cells": rows,
           "all_cells_rose": all(r["cost_rose"] for r in rows),
           "max_abs_time_rise_minus_predicted_bits": max(dev),
           "max_abs_memory_rise_minus_predicted_bits": max(abs(r["memory_rise_minus_predicted"]) for r in rows),
           "min_observed_time_rise_bits": min(r["observed_time_rise_bits"] for r in rows),
           "max_observed_time_rise_bits": max(r["observed_time_rise_bits"] for r in rows),
           "note": ("predicted rise is written from the degree ratio alone: omega*log2(N) under the "
                    "loose reading, omega*log2((N+5)/5) under the binomial reading, and log2((N+5)/5) "
                    "for memory. Any residual between observed and predicted would come from the "
                    "log-added index-calculus linear-algebra term; its size is reported above"),
           "modeled_not_measured": True, "scope_statement": SCOPE_STATEMENT}
    write_json("known-false-dF5.json", out)
    return out


# ---------------------------------------------------------------------------
# ARM P
# ---------------------------------------------------------------------------


def arm_p() -> dict:
    log("ARM P: nearby object, odd characteristic")
    traces = {}
    exps = []
    for p in (2, 3, 5):
        for omega in N.OMEGA_SET:
            tr = []
            e = N.theorem1_exponent(p, omega, tr)
            e["expected_form_value"] = (8 * omega + 1) if p == 2 else ((6 * p + 2) * omega + 1)
            e["matches_expected"] = abs(e["exponent_in_n"] - e["expected_form_value"]) < 1e-12
            e["expected_d_F"] = 4 if p == 2 else 3 * p + 1
            e["d_F_matches"] = e["d_F"] == e["expected_d_F"]
            exps.append(e)
        tr = []
        N.nagao_cell(283, p, 4, 2.807, "binomial_C_N_plus_d_choose_d", trace=tr)
        traces[p] = tr
    # code path diff: the function-call traces must be identical up to the p
    # argument itself
    import re

    def strip_p(t):
        return [re.sub(r"p=\d+", "p=P", s) for s in t]

    def strip_p_df(t):
        return [re.sub(r"d_F=\d+", "d_F=D", s) for s in strip_p(t)]
    diff = {"p2_vs_p3_identical_after_masking_p_only": strip_p(traces[2]) == strip_p(traces[3]),
            "p2_vs_p5_identical_after_masking_p_only": strip_p(traces[2]) == strip_p(traces[5]),
            "p2_vs_p3_identical_after_masking_p_and_derived_dF": strip_p_df(traces[2]) == strip_p_df(traces[3]),
            "p2_vs_p5_identical_after_masking_p_and_derived_dF": strip_p_df(traces[2]) == strip_p_df(traces[5]),
            "same_call_sequence_length": len(traces[2]) == len(traces[3]) == len(traces[5]),
            "note": ("masking p alone leaves d_F in the trace, and d_F is DERIVED from p by "
                     "d_F_bound, so the p-only masking is expected to differ at exactly the "
                     "d_F argument; the sequence of functions called is what the control is "
                     "about, and it is compared after masking both"),
            "trace_p2": traces[2], "trace_p3": traces[3], "trace_p5": traces[5]}
    import inspect
    src = inspect.getsource(N.d_F_bound) + inspect.getsource(N.theorem1_exponent) + inspect.getsource(N.nagao_cell)
    cells = []
    for p in (3, 5):
        for n in N.N_FIPS:
            for omega in N.OMEGA_SET:
                for c0 in (2, 3, 4, 6):
                    c = N.nagao_cell(n, p, c0, omega, "binomial_C_N_plus_d_choose_d")
                    c["margins"] = {m: N.margin(c, m) for m in N.METRICS}
                    cells.append(c)
    out = {"arm": "P", "exponents": exps,
           "all_exponents_match_6p_plus_2_form": all(e["matches_expected"] for e in exps),
           "all_degrees_match_3p_plus_1": all(e["d_F_matches"] for e in exps),
           "p3_omega_2p807_exponent": (6 * 3 + 2) * 2.807 + 1,
           "hypothesis_P6_quotes_54p5_at_p3_omega_2p807_but_its_own_formula_gives":
               (6 * 3 + 2) * 2.807 + 1,
           "code_path_diff": diff,
           "where_p_enters_source": src,
           "p_enters_only_via": ["d_F_bound(p): 4 if p == 2 else 3p+1 (Prop. 2 / Prop. 5, the source's own branch)",
                                 "log2(p) in the coset constant and yield"],
           "odd_characteristic_cells_control_not_target": cells,
           "modeled_not_measured": True, "scope_statement": SCOPE_STATEMENT}
    write_json("nearby-object-oddchar.json", out)
    return out


# ---------------------------------------------------------------------------
# ARM M
# ---------------------------------------------------------------------------


def arm_m() -> dict:
    log("ARM M: matched nulls")
    rows = []
    for n in N.N_FIPS:
        for omega in N.OMEGA_SET:
            for c0 in N.C0_RANGE:
                for reading in N.READINGS:
                    real = N.nagao_cell(n, 2, c0, omega, reading)
                    fy = N.nagao_cell(n, 2, c0, omega, reading, free_yield_null=True)
                    zm = N.nagao_cell(n, 2, c0, omega, reading, zero_memory_null=True)
                    row = {"n": n, "omega": omega, "C_0": c0, "reading": reading, "margins": {}}
                    for metric in N.METRICS:
                        for mr in N.MEMORY_READINGS:
                            mreal = N.margin(real, metric, mr)["margin_bits_nagao_minus_vow"]
                            mfy = N.margin(fy, metric, mr)["margin_bits_nagao_minus_vow"]
                            mzm = N.margin(zm, metric, mr)["margin_bits_nagao_minus_vow"]
                            row["margins"][f"{metric}|{mr}"] = {
                                "real": mreal, "free_yield_null": mfy, "zero_memory_null": mzm,
                                "real_minus_free_yield": mreal - mfy,
                                "real_minus_zero_memory": mreal - mzm}
                    rows.append(row)
    fy_share = [v["real_minus_free_yield"] for r in rows for v in r["margins"].values()]
    zm_share = [v["real_minus_zero_memory"] for r in rows for k, v in r["margins"].items()
                if not k.startswith("time_only")]
    out = {"arm": "M", "cells": rows,
           "free_yield_share_of_margin_bits": {"min": min(fy_share), "max": max(fy_share)},
           "zero_memory_share_of_margin_bits_memory_metrics": {"min": min(zm_share), "max": max(zm_share)},
           "note": ("the free-yield share equals T4 exactly and the zero-memory share equals "
                    "the charged memory column exactly, by construction; both are reported "
                    "beside the real margin so the reader sees how much of any margin each "
                    "absorbed term carries"),
           "modeled_not_measured": True, "scope_statement": SCOPE_STATEMENT}
    write_json("matched-nulls.json", out)
    return out


# ---------------------------------------------------------------------------
# ARM I
# ---------------------------------------------------------------------------


def arm_i(arm_n_cells) -> dict:
    log("ARM I: independent memory term (blind module) and comparison")
    blind = I.surface(N.N_FIPS, N.C0_RANGE)
    # compare AFTER the blind values exist; the comparison reads ARM N output
    # only here, in the driver, never inside arm_i_independent_memory.py
    comp = []
    for cell in blind:
        n, c0 = cell["n"], cell["C_0"]
        armn = next(r for r in arm_n_cells if r["n"] == n and r["C_0"] == c0)
        for reading, v in cell["per_reading"].items():
            if v["status"] != "evaluated":
                comp.append({"n": n, "C_0": c0, "m_reading": reading, "status": v["status"]})
                continue
            comp.append({"n": n, "C_0": c0, "m_reading": reading, "blind_log2": v["log2_count"],
                         "blind_m": v["m"], "blind_N": v["N"], "arm_n_m": armn["m"], "arm_n_N": armn["N_frozen"],
                         "arm_n_T5_frozen_width_log2": armn["T5_memory_log2_frozen_width"],
                         "disagreement_bits": v["log2_count"] - armn["T5_memory_log2_frozen_width"]})
    ceil_rows = [c for c in comp if c.get("m_reading") == "ceil" and "disagreement_bits" in c]
    all_rows = [c for c in comp if "disagreement_bits" in c]
    worst_ceil = max(ceil_rows, key=lambda c: abs(c["disagreement_bits"]))
    worst_any = max(all_rows, key=lambda c: abs(c["disagreement_bits"]))
    out = {"arm": "I", "blind_from": ["the ARM N implementation", "any ARM N output"],
           "blindness_statement": I.__doc__,
           "ambiguities_found_in_the_statement": ["A1 rounding of m = n/C_0", "A2 clamp m >= 2",
                                                  "A3 unit of the count"],
           "blind_values": blind, "comparison": comp,
           "largest_disagreement_bits_ceil_reading": worst_ceil,
           "largest_disagreement_bits_any_reading": worst_any,
           "cells_with_ceil_disagreement_above_1e-9": sum(1 for c in ceil_rows if abs(c["disagreement_bits"]) > 1e-9),
           "modeled_not_measured": True, "scope_statement": SCOPE_STATEMENT}
    write_json("independent-memory-term.json", out)
    return out


# ---------------------------------------------------------------------------
# manifest
# ---------------------------------------------------------------------------


def write_manifest(status, started, arms_done, valid, invalid_reason, result_metrics,
                   deviations, attempts):
    import yaml
    finished = datetime.now(timezone.utc)
    artifacts = {}
    for name in sorted(os.listdir(RUN_DIR)):
        if name == "manifest.yaml":
            continue
        p = os.path.join(RUN_DIR, name)
        if os.path.isfile(p):
            artifacts[name] = {"sha256": sha256_of(p), "bytes": os.path.getsize(p)}
    ru = resource.getrusage(resource.RUSAGE_SELF)
    doc = {"run": {
        "id": RUN_ID, "experiment_id": EXP_ID, "status": status,
        "code": {"commit": git("rev-parse", "HEAD"),
                 "dirty": bool(git("status", "--porcelain")),
                 "command": open(os.path.join(RUN_DIR, "command.txt")).read().strip()},
        "inference": {
            "requested_policy": "executor-implementation",
            "canonical_policy": "executor-implementation",
            "backend": None, "provider": None,
            "resolved_model_id": "claude-fable-5-1-thinking-medium",
            "resolved_model_id_provenance": "requested slug, self-reported; no adapter probe ran in this runtime",
            "model_provenance": "self-reported",
            "model_verified": False,
            "requested_reasoning_effort": None, "reasoning_effort": "medium",
            "fallback_used": False, "fallback_reason": None,
            "degraded_allowed": False, "degraded_requirements": [],
            "independent_session": False, "adapter_version": None, "config_digest": None},
        "environment": {"operating_system": platform.platform(), "architecture": platform.machine(),
                        "sage_version": None, "python_version": platform.python_version(),
                        "dependencies": {"numpy": np.__version__, "pyyaml": yaml.__version__,
                                         "standard_library_only_otherwise": True},
                        "groebner_engines_probed_and_absent": ["magma", "sage", "Singular", "msolve"]},
        "inputs": {"curve_id": ("ARM C enumeration only: y^2 + xy = x^3 + A x^2 + B over F_2^n, "
                                "n in {8,...,20}, one seeded random (A, B) per cell; no standardised "
                                "curve is used and none is claimed about"),
                   "seed": [SEED_BASE], "seed_formula": "SEED_BASE + 10 n + k per enumeration cell; sub-seeds +1000+d, +5000+d, +9000+d",
                   "parameters": {"n": N.N_FIPS, "omega": N.OMEGA_SET, "omega_source_own": N.OMEGA_SOURCE_OWN,
                                  "C_0": N.C0_RANGE, "metric": N.METRICS, "monomial_count_reading": N.READINGS,
                                  "memory_reading": N.MEMORY_READINGS, "characteristic": [2, 3, 5], "d_F": [4, 5],
                                  "enumeration_n": [8, 10, 12, 14, 16, 18, 20], "enumeration_k": [1, 2, 3, 4]},
                   "frozen_nagao_sha256_verified": "337fae555450162e56432ee137d0cb4bb20e2bd901c29f69b38a2f949e913218"},
        "timing": {"started_at": started, "finished_at": finished.strftime("%Y-%m-%dT%H:%M:%SZ"),
                   "wall_seconds": time.time() - _T0},
        "resources": {"peak_rss_bytes": ru.ru_maxrss * 1024, "cpu_seconds": ru.ru_utime + ru.ru_stime,
                      "memory_cap_bytes": MEMORY_CAP_BYTES},
        "result": {"metrics": result_metrics, "valid": valid, "invalid_reason": invalid_reason,
                   "certificate": {"kind": "none", "verified": None, "verifier": None,
                                   "in_place_of_a_certificate": ("pure arithmetic/measurement run: no discrete log "
                                                                 "is solved and no relation is claimed. The "
                                                                 "reproduction gate (ARM R, 1e-3 bits per cell) "
                                                                 "and selftest.json stand in place of a certificate")}},
        "artifacts": artifacts,
        "attempts": attempts,
        "arms_completed_in_order": arms_done,
        "protocol_deviations": deviations,
    }}
    with open(os.path.join(RUN_DIR, "manifest.yaml"), "w") as fh:
        yaml.safe_dump(doc, fh, sort_keys=False, width=100)
    log(f"wrote manifest.yaml (status {status})")


ATTEMPTS = [
    {"attempt": 1, "started_at": "2026-09-13T18:43:00Z", "ended_at": "2026-09-13T19:41:00Z",
     "outcome": "failed_infrastructure",
     "reason": ("subagent runtime activity timeout; the platform killed the session. Five modules "
                "were drafted under code/ (last write 19:09Z) and NOTHING was written to the run "
                "directory. Not evidence about anything (core rule 5)."),
     "artifacts": []},
    {"attempt": 2, "started_at": None, "outcome": "this run",
     "reused_from_attempt_1": ["arm_c_coset.py", "arm_i_independent_memory.py", "binary_field.py",
                               "nagao_cost.py", "semaev_repro.py (docstring of degenerate_slice corrected)"],
     "added_in_attempt_2": ["selftest.py", "run_experiment.py"]},
]


def main() -> int:
    started = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    ATTEMPTS[1]["started_at"] = started
    deviations = [
        {"deviation": ("the driver was executed TWICE within attempt 2. Execution 1 (19:52:57Z, "
                       "5.6 s, completed_valid) produced every deliverable; inspection then found "
                       "four DRIVER-LEVEL labelling defects, none touching a formula or a number: "
                       "(1) the 'eq11 pipeline reproduces an uncorrected figure' control was "
                       "trivially true at d_sat = 6, 7 where the corrected and uncorrected targets "
                       "print the same value; (2) the ARM P code-path diff masked p but not the "
                       "p-derived d_F, so the 'identical path' flag read False for the wrong "
                       "reason; (3) the ARM K note text described a residual that is numerically "
                       "zero; (4) ARM C's comparison reported only the pooled curve-minus-null "
                       "z-score, not the structured-V single-draw z-score. Execution 2 fixes the "
                       "labels and reruns everything."),
         "retained": ["raw-result.driver-exec-1.json", "manifest.driver-exec-1.yaml",
                      "reproduction.driver-exec-1.json", "stdout.log (both executions appended)"],
         "classification": "implementation_error in reporting labels, fixed; not evidence about anything",
         "numbers_changed_between_executions": "none expected; verified by the reviewer against the retained exec-1 files"},
    ]
    arms_done = []
    write_manifest("running", started, arms_done, None, None, {}, deviations, ATTEMPTS)

    log("self-test")
    st = selftest.run()
    write_json("selftest.json", st)
    if not st["all_pass"]:
        write_manifest("invalid", started, arms_done, False,
                       "implementation_error: self-test failed", {"selftest": st}, deviations, ATTEMPTS)
        return 2

    c = arm_c(); arms_done.append("C")
    r = arm_r(); arms_done.append("R")
    metrics = {
        "arm_c_bound_A_C0_min_p2": c["headline_p2"]["bound_A_C0_min_eps_0p05"],
        "arm_c_bound_B_C0_min_p2": c["headline_p2"]["bound_B_C0_min_1_bit"],
        "arm_c_enumeration_cells": c["comparison"]["cells_enumerated"],
        "arm_c_enumeration_unreached": c["comparison"]["cells_unreached"],
        "arm_c_curve_minus_null_max_abs_sd": c["comparison"]["curve_minus_null_in_null_sd"]["max_abs"],
        "arm_r_passed": r["passed"],
        "arm_r_gate_cells": r["gate_cells_total"],
        "arm_r_worst_abs_error_bits_1e-3_cells": r["worst_abs_error_bits_at_1e-3_tolerance_cells"],
        "arm_r_worst_abs_error_bits_all_cells": r["worst_abs_error_bits_all_gate_cells"],
    }
    if not r["passed"]:
        write_manifest("invalid", started, arms_done, False,
                       "implementation_error: ARM R reproduction gate failed; ARMS N,K,P,M,I not reported (core rule 5)",
                       metrics, deviations, ATTEMPTS)
        return 3

    n_out = arm_n(); arms_done.append("N")
    k_out = arm_k(); arms_done.append("K")
    p_out = arm_p(); arms_done.append("P")
    m_out = arm_m(); arms_done.append("M")
    i_out = arm_i(n_out["cells"]); arms_done.append("I")

    flags = n_out["escalation_flags_memory_charging_metric_nagao_ahead"]
    metrics.update({
        "arm_n_cells": len(n_out["cells"]),
        "arm_n_crossover_cells": len(n_out["crossover_surface"]),
        "arm_n_crossovers_null": sum(1 for x in n_out["crossover_surface"] if x["crossover_n"] is None),
        "arm_n_escalation_flag_cells": len(flags),
        "arm_n_escalation_flag_cells_committed_omega": sum(1 for f in flags if f["omega_in_committed_set"]),
        "arm_n_escalation_flag_cells_committed_omega_C0_satisfies_bound_B":
            sum(1 for f in flags if f["omega_in_committed_set"] and f["C_0_satisfies_ARM_C_bound_B_1bit"]),
        "arm_n_spreads_at_571": {k: {"max_C_0_spread_declared": v["max_C_0_spread_bits_declared_range"],
                                     "max_C_0_spread_bound_B": v["max_C_0_spread_bits_bound_B_range"],
                                     "max_omega_spread": v["max_omega_spread_bits"]}
                                 for k, v in n_out["spreads_at_n_571"].items()},
        "arm_k_all_cells_rose": k_out["all_cells_rose"],
        "arm_k_max_abs_time_rise_minus_predicted_bits": k_out["max_abs_time_rise_minus_predicted_bits"],
        "arm_p_all_exponents_match": p_out["all_exponents_match_6p_plus_2_form"],
        "arm_p_all_degrees_match": p_out["all_degrees_match_3p_plus_1"],
        "arm_p_code_path_identical_after_masking_p_only": p_out["code_path_diff"]["p2_vs_p3_identical_after_masking_p_only"]
                                                          and p_out["code_path_diff"]["p2_vs_p5_identical_after_masking_p_only"],
        "arm_p_code_path_identical_after_masking_p_and_derived_dF":
            p_out["code_path_diff"]["p2_vs_p3_identical_after_masking_p_and_derived_dF"]
            and p_out["code_path_diff"]["p2_vs_p5_identical_after_masking_p_and_derived_dF"],
        "arm_m_free_yield_share_bits": m_out["free_yield_share_of_margin_bits"],
        "arm_m_zero_memory_share_bits": m_out["zero_memory_share_of_margin_bits_memory_metrics"],
        "arm_i_largest_disagreement_bits_ceil": i_out["largest_disagreement_bits_ceil_reading"]["disagreement_bits"],
        "arm_i_largest_disagreement_bits_any_reading": i_out["largest_disagreement_bits_any_reading"]["disagreement_bits"],
    })
    raw = {"run_id": RUN_ID, "experiment_id": EXP_ID, "arms_in_order": arms_done,
           "summary_metrics": metrics, "selftest": st, "arm_c": c, "arm_r": r, "arm_n": n_out,
           "arm_k": k_out, "arm_p": p_out, "arm_m": m_out, "arm_i": i_out,
           "attempts": ATTEMPTS, "scope_statement": SCOPE_STATEMENT}
    write_json("raw-result.json", raw)
    valid = (r["passed"] and k_out["all_cells_rose"] and p_out["all_exponents_match_6p_plus_2_form"]
             and p_out["all_degrees_match_3p_plus_1"])
    write_manifest("completed_valid" if valid else "invalid", started, arms_done, valid,
                   None if valid else "invalidation rule fired; see raw-result.json summary_metrics",
                   metrics, deviations, ATTEMPTS)
    log("done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
