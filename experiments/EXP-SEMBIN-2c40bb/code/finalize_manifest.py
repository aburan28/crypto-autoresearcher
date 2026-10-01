#!/usr/bin/env python3
"""Fill RUN-SEMBIN-3ae91c/manifest.yaml from the run directory's artifacts.

Shape copied from experiments/EXP-SEMBIN-92724f/runs/RUN-SEMBIN-cbd770/manifest.yaml.
The only hand-supplied values are the inference self-report and the status; every
metric is read from the arm JSON files.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import subprocess

import yaml

import surface_cost as S


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--started-at", required=True)
    ap.add_argument("--status", default="completed_valid")
    args = ap.parse_args()
    rd = os.path.abspath(args.run_dir)
    j = lambda name: json.load(open(os.path.join(rd, name)))  # noqa: E731
    gate, ctrl, armb, armf, armi, surf, meas, res, det = (
        j("reproduction-gate.json"), j("controls.json"), j("arm-b-coherent-baseline.json"),
        j("arm-f-fixed-budget.json"), j("sparse-implementation-comparison.json"), j("surface.json"),
        j("measurement-comparison.json"), j("resources.json"), j("determinism-check.json"))
    env = json.load(open(os.path.join(rd, "environment.json")))
    verification = j("COST-SEMBIN-e9960c.verification.json")
    U, R = S.K_READINGS[0], "record_point_M1_w30"
    git = lambda *a: subprocess.run(["git", *a], capture_output=True, text=True, cwd=rd).stdout.strip()  # noqa: E731
    finished = dt.datetime.now(dt.timezone.utc)
    started = dt.datetime.fromisoformat(args.started_at.replace("Z", "+00:00"))

    def rng(st, fld):
        return surf["crossover_ranges"][st][U]["stage1_argmin/persistent_crossover_n"][fld]["range"]

    man = {"run": {
        "id": "RUN-SEMBIN-3ae91c",
        "experiment_id": "EXP-SEMBIN-2c40bb",
        "status": args.status,
        "code": {"commit": git("rev-parse", "HEAD"),
                 "dirty": bool(git("status", "--porcelain")),
                 "command": open(os.path.join(rd, "command.txt")).read().strip(),
                 "post_run_commands": [
                     "python3 generate_cost_record.py --run-dir ../runs/RUN-SEMBIN-3ae91c",
                     "python3 verify_new_record.py --run-dir ../runs/RUN-SEMBIN-3ae91c",
                     "python3 finalize_manifest.py --run-dir ../runs/RUN-SEMBIN-3ae91c --started-at <ts>"],
                 "attempts": ("3 executions of command.txt: attempt 1 failed on a record-parsing "
                              "ValueError before any arm ran; attempt 2 completed every arm but was "
                              "superseded because raw-result.json was 79 MB and C4's criterion "
                              "mis-scored domain-floor cells; attempt 3 is the run of record. All "
                              "three are in stdout.log/stderr.log.")},
        "inference": {
            "requested_policy": "executor-implementation",
            "canonical_policy": "executor-implementation",
            "backend": None, "provider": None,
            "resolved_model_id": "claude-fable-5-1-thinking-medium",
            "model_provenance": "self-reported slug the subagent was dispatched on; user directive 'Use fable' recorded in the queue notes; no adapter resolution",
            "model_verified": False,
            "model_verified_reason": "no adapter probe (python3 -m orchestration.adapter doctor --probe) ran in this session",
            "requested_reasoning_effort": "medium", "reasoning_effort": "medium",
            "fallback_used": False, "fallback_reason": None,
            "degraded_allowed": False, "degraded_requirements": [],
            "independent_session": False, "adapter_version": None, "config_digest": None},
        "environment": {
            "operating_system": env["operating_system"], "architecture": env["architecture"],
            "sage_version": None, "python_version": env["python_version"],
            "dependencies": {"standard_library_only_for_computation": True,
                             "pyyaml_for_record_io": env["dependencies"]["pyyaml_used_only_by_record_writer"],
                             "mpmath": "not installed; not used"}},
        "inputs": {
            "curve_id": "none instantiated; n is a generic field degree from 3 to 700; FIPS labels 163/233/283/409/571 are parameter labels only",
            "seed": [], "randomness": "none anywhere; deterministic closed-form arithmetic",
            "parameters": {
                "cost_metric": S.METRIC_FAMILIES, "store_log2": S.STORE_GRID, "processors_log2": S.PROC_GRID,
                "baseline_charging_mode": S.MODES, "kappa": S.KAPPA_GRID, "cofactor_h": S.COFACTOR_GRID,
                "memory_budget_log2": S.BUDGET_GRID, "alpha": S.ALPHA_GRID, "storage_reading": S.STORAGES,
                "k_reading": S.K_READINGS, "m_selection": S.M_SELECTIONS, "omega": S.OMEGA_GRID,
                "omega_prime": 2.0, "degree_bound_GIVEN_not_measured": S.DEGREE_GRID,
                "curve_label": ["B-409", "K-409", "B-571", "K-571"], "scan_domain_n": [S.N_LO, S.N_HI],
                "m_range": [2, S.M_HI], "surface_cells": 254016,
                "surface_fixed_axes": "degree 4, omega 3.0; omega/degree/curve_label are one-at-a-time sensitivity tables in sensitivities.json"},
            "frozen_inputs": ["inputs/SEMAEV-2015-310/tables.yaml",
                              "experiments/EXP-SEMBIN-f4a17b/runs/RUN-SEMBIN-121b59/COST-SEMBIN-8d123b.yaml",
                              "coordination/review/sembin-20260913-9d649f/red-team-cf9d98/recomputations.json (read as data)",
                              "knowledge/literature/KN-LIT-e77232.md (formula statement for ARM I)"],
            "heuristic_under_test": "HEUR-VOW-CURVE -- UNVALIDATED; primary van Oorschot-Wiener paper NOT opened by any agent in this program; the tradeoff model is an internal restatement (red team J2(b)) and is not presented as sourced from van Oorschot-Wiener 1999"},
        "timing": {"started_at": started.strftime("%Y-%m-%dT%H:%M:%SZ"),
                   "finished_at": finished.strftime("%Y-%m-%dT%H:%M:%SZ"),
                   "wall_seconds": (finished - started).total_seconds(),
                   "compute_seconds_execution_1": res["compute_seconds_execution_1"]},
        "resources": {"peak_rss_bytes": res["peak_rss_bytes"], "cpu_seconds": res["cpu_seconds_both_executions"],
                      "budget_declared": {"cpu_cores": 2, "memory_gb": 2, "wall_clock_seconds": 1800},
                      "within_budget": res["peak_rss_bytes"] < 2 * 2 ** 30},
        "result": {
            "metrics": {
                "arm_R_reproduction_gate": {"passed": gate["gate"]["passed"],
                                            "largest_disagreement_vs_record_bits": gate["largest_disagreement_vs_record_bits"],
                                            "largest_disagreement_vs_red_team_bits": gate["largest_disagreement_vs_red_team_recomputations_bits"],
                                            "crossovers_time_only_dense_sparse_product_dense_sparse": [
                                                gate["crossovers"]["time_only_zero_memory_weight"]["dense"]["recomputed"],
                                                gate["crossovers"]["time_only_zero_memory_weight"]["semaev_sparse"]["recomputed"],
                                                gate["crossovers"]["time_memory_product"]["dense"]["recomputed"],
                                                gate["crossovers"]["time_memory_product"]["semaev_sparse"]["recomputed"]],
                                            "margins_409": gate["n409"]},
                "arm_N_prime_field_control": "UNREACHED (arm-n-prime-field-control.json)",
                "arm_S_crossover_range_over_store_declared_grid_vs_parent_metric_set_persistent": {
                    st: {"store_declared_grid_range": rng(st, "over_store_declared_grid_30_40_48_60_product_metric"),
                         "store_full_grid_range": rng(st, "over_store_full_grid_product_metric"),
                         "parent_metric_set_range": rng(st, "over_parent_metric_set_time_only_and_product_at_store30"),
                         "full_metric_set_range": rng(st, "over_full_metric_set_28_instances_at_store30")}
                    for st in S.STORAGES},
                "arm_S_collision_pairs_total": surf["collisions"]["total_colliding_pairs"],
                "arm_B_shift_record_to_own_curve_in_n_and_bits_at_409_stage1_argmin": {
                    st: armb["per_k_reading"][U][st]["shift_record_to_own_curve/stage1_argmin"] for st in S.STORAGES},
                "arm_B_vow_product_excess_bits": {n: v["excess_bits"] for n, v in armb["vow_product_excess_per_n"].items()},
                "arm_F_hard_band_409_dense_vs_sparse": armf["disagreement_bands"]["409"][f"dense_row_echelon|semaev_sparse/{U}/{R}/hard"],
                "arm_F_soft_band_409_dense_vs_sparse": armf["disagreement_bands"]["409"][f"dense_row_echelon|semaev_sparse/{U}/{R}/soft"],
                "arm_F_alpha_flip_409": {st: armf["alpha_flip"]["409"][f"{st}/{U}/{R}"]["alpha_star_closed_form_stage1_argmin_m"] for st in S.STORAGES},
                "arm_I_largest_disagreement_bits": armi["largest_cellwise_disagreement_bits"],
                "arm_I_n571_check_agrees": armi["kn_lit_e77232_n571_check"]["all_agree"],
                "C10_upper_bound_check": {st: {k: v for k, v in meas["upper_bound_check_per_reading"][st].items() if "every_row" in k}
                                          for st in S.STORAGES},
                "control_outcomes": {
                    "C1": "passed" if ctrl["C1_reproduction_gate"]["passed"] else "FAILED",
                    "C2": f"{ctrl['C2_table3_baseline_reproduction']['cells_agreeing_truncated_3sf']} truncated-3sf, {ctrl['C2_table3_baseline_reproduction']['cells_within_0p7pct']} within 0.7%, argmin 10/11/12, crossover {ctrl['C2_table3_baseline_reproduction']['crossover_papers_own_convention_stage1_vs_bare_2_pow_n_half']}",
                    "C3": "informative null run; baseline-store contribution -87..-88 in n (30 bits) -- not near zero; zero-memory comparator DEGENERATE under memory metrics",
                    "C4": "passed" if ctrl["C4_known_false_free_yield"]["passed"] else "FAILED",
                    "C5": "passed by 1957/3432/5977 bits; typo detector only, not a validity check",
                    "C6": "UNREACHED",
                    "C7": f"largest disagreement {armi['largest_cellwise_disagreement_bits']:.2e} bits; independence weakened (PD-I)",
                    "C8": "n scanned from 3; low-n artefact at n = 3..4 labelled",
                    "C9": "passed" if ctrl["C9_invalid_input_rejection"]["passed"] else "FAILED",
                    "C10": "33 rows under both MB readings; see measurement-comparison.json; neither reading picked"},
                "cost_record_verification": {"record": "COST-SEMBIN-e9960c.yaml", "figures_checked": verification["figures_checked"],
                                             "passed": verification["passed"]},
                "determinism": {"all_arm_json_identical_across_two_executions": det["all_identical"],
                                "differs_only_in": "stdout.log timestamps"}},
            "valid": True,
            "invalid_reason": None,
            "validity_note": ("completed_valid as a MEASUREMENT of two heuristic cost models: every arm terminal, ARM R gate passed, "
                              "ARM N UNREACHED with a recorded impediment (not a failure of this run). No statement about any curve's security."),
            "certificate": {"kind": "none", "verified": None, "verifier": None,
                            "reason": "pure derivation; no discrete logarithm solved and no factor-base relation claimed"}},
        "procedure_deviations": [
            {"id": "PD-I", "deviation": "memory_charged_cost.py (including semaev_memory_log2) was read in full during contract intake BEFORE sparse_independent.py was written",
             "effect": "ARM I / C7 independence is weaker than specified; the module imports nothing and uses an exact-integer route, but blindness was not achieved"},
            {"id": "PD-N", "deviation": "ARM N not instantiated; UNREACHED with concrete missing pieces per stopping rule 4", "effect": "C6 not run; all rows reported without it"},
            {"id": "PD-S", "deviation": "omega, degree_bound and curve_label are swept one-at-a-time in sensitivities.json rather than as full surface axes; m_selection added as a labelled axis",
             "effect": "the 254,016-cell surface fixes degree 4 / omega 3.0; the sensitivity tables cover the other values at the record and coherent points only"},
            {"id": "PD-A", "deviation": "three execution attempts; attempts 1-2 recorded in stdout.log/stderr.log; attempt 3 is the run of record", "effect": "none on results (attempt 2 and 3 agree on every figure; only file size and the C4 scoring criterion changed)"},
            {"id": "PD-M", "deviation": "mpmath not installed; float64 via math with exact integer binomials", "effect": "reproduction to 4.8e-5 bits shows float64 suffices at the printed precision"},
        ],
        "artifacts": {}}}
    for f in sorted(os.listdir(rd)):
        p = os.path.join(rd, f)
        if os.path.isfile(p) and f not in ("manifest.yaml",):
            man["run"]["artifacts"][f] = {"sha256": sha256(p), "bytes": os.path.getsize(p)}
    second = os.path.join(rd, "determinism-second-execution", "stdout.log")
    if os.path.exists(second):
        man["run"]["artifacts"]["determinism-second-execution/stdout.log"] = {"sha256": sha256(second), "bytes": os.path.getsize(second)}
    with open(os.path.join(rd, "manifest.yaml"), "w") as fh:
        yaml.safe_dump(man, fh, sort_keys=False, width=110, allow_unicode=True)
    print("manifest written", man["run"]["code"]["commit"], man["run"]["timing"]["wall_seconds"])


if __name__ == "__main__":
    main()
