#!/usr/bin/env python3
"""Driver / CLI entry point for EXP-DTREE-001's 12 planned runs.

Usage (from the repo root, matching the "command" recorded in each run's
manifest):
    python3 experiments/EXP-DTREE-001/implementation/driver.py <subcommand>

Subcommands map 1:1 to the frozen specification's planned_runs:
    freeze          -> RUN-DTREE-001
    slope           -> RUN-DTREE-002
    single-level    -> RUN-DTREE-003 (16-bit), RUN-DTREE-004 (20-bit), RUN-DTREE-005 (24-bit)
    depth2          -> RUN-DTREE-006 (16-bit), RUN-DTREE-007 (20-bit), RUN-DTREE-008 (24-bit)
    medbase-logs    -> RUN-DTREE-009
    rho             -> RUN-DTREE-010
    prob-sampling   -> RUN-DTREE-011
    aggregate       -> RUN-DTREE-012
"""
from __future__ import annotations

import argparse
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

import common  # noqa: E402
import instances  # noqa: E402
import slope as slope_mod  # noqa: E402
import costs  # noqa: E402
import aggregate as aggregate_mod  # noqa: E402

BITS_TO_RUN = {16: ("RUN-DTREE-003", "RUN-DTREE-006"), 20: ("RUN-DTREE-004", "RUN-DTREE-007"),
               24: ("RUN-DTREE-005", "RUN-DTREE-008")}

# Redirects ALL run reads/writes (never just writes) to an isolated directory
# for pre-execution smoke testing. Unset (the normal case) means the real,
# immutable experiments/EXP-DTREE-001/runs/. Set only from the scratchpad in
# this session's own smoke-test invocations, never for an official run.
OUT_ROOT = os.environ.get("DTREE_OUT_ROOT") or None


def runs_dir() -> str:
    return OUT_ROOT or common.RUNS_DIR


def run001_raw() -> str:
    return os.path.join(runs_dir(), "RUN-DTREE-001", "raw.json")


def _command_line(subcommand: str, extra: list[str]) -> str:
    rel = os.path.relpath(os.path.abspath(__file__), common.REPO)
    parts = ["python3", rel, subcommand, *extra]
    return " ".join(parts)


def cmd_freeze(args) -> None:
    started = time.time()
    with common.captured_output() as (out, err):
        print("RUN-DTREE-001: freezing main instances, tiny instances, and the slope grid")
        frozen = instances.build_frozen_instances()
        for bits, rec in frozen["main_instances"].items():
            print(f"  main {bits}-bit (seed {rec['seed']}): p={rec['p']} n={rec['n']} "
                  f"standard_B={rec['standard_B']} distinct_targets={rec['distinct_target_points']}/{rec['requested_target_count']}")
        for bits, rec in frozen["tiny_instances"].items():
            print(f"  tiny {bits}-bit (seed {rec['seed']}): p={rec['p']} n={rec['n']} "
                  f"qualifying_b_prime={rec['qualifying_b_prime']}")
        grid = frozen["slope_grid"]
        print(f"  slope grid: total_qualifying_cells={grid['total_qualifying_cells']} "
              f"design_infeasible={grid['design_infeasible']}")
    finished = time.time()

    anomalies = []
    if grid["design_infeasible"]:
        anomalies.append({
            "type": "design_infeasible",
            "stage": "freeze",
            "description": (
                f"The frozen slope-grid rule (B'>=8, C(B',3)>=50, lambda<=0.7) yields "
                f"{grid['total_qualifying_cells']} qualifying cells across the three tiny "
                f"curves (8/10/12 bits, seed 1), fewer than the required "
                f"{grid['rule']['min_cells_required_across_all_tiny_curves']}. Root cause: "
                f"harness.toycurve.generate_instance's deterministic search accepts the FIRST "
                f"curve meeting a weak bar (largest prime factor >= 5), not one with a large "
                f"prime-order subgroup; for seed=1 at 8/10/12 bits this yields group orders "
                f"n=23, n=19, n=31 respectively (recorded exactly in this run's raw output), "
                f"far too small for 0.7*n >= 50 to ever hold at any B'>=8. Per the freeze "
                f"stage's own stop rule this is recorded as design_infeasible with the exact "
                f"lambda table, and the frozen grid is NOT improvised or replaced -- the C1 "
                f"slope fit is not computable from this frozen input; C2 (which does not "
                f"depend on the tiny curves) is unaffected."),
        })
    for bits, rec in frozen["main_instances"].items():
        if rec["distinct_target_points"] < rec["requested_target_count"]:
            anomalies.append({
                "type": "target_collisions",
                "stage": "freeze",
                "description": (
                    f"main curve {bits}-bit (n={rec['n']}) has only {rec['distinct_target_points']} "
                    f"distinct points among the {rec['requested_target_count']} requested targets "
                    f"(R = a*P+b*Q for 50 distinct seeded (a,b) pairs); by the pigeonhole "
                    f"principle this is unavoidable once n < 50, and is even likely for n in the "
                    f"low hundreds. Every target keeps its own distinct, recorded (a,b) seed pair "
                    f"as specified; several pairs simply land on the same group element."),
            })

    record = common.RunRecord(
        run_id="RUN-DTREE-001", purpose="Freeze main instances, targets, standard/medium factor "
                                          "bases; compute and freeze the slope grid from exact lambda values.",
        command=_command_line("freeze", []),
        seeds={"main_instance_seeds": {16: 1, 20: 2, 24: 3}, "tiny_instance_seeds": {8: 1, 10: 1, 12: 1},
               "seed_to_size_mapping_policy": "ascending seed to ascending bit size (documented choice, "
                                               "spec states one-to-one without pinning the pairing)"},
        inputs={"main_curve_bits": [16, 20, 24], "tiny_curve_bits": [8, 10, 12],
                "curve_ids": {str(bits): common.curve_id(rec["p"], rec["a"], rec["b"], bits)
                              for bits, rec in frozen["main_instances"].items()}},
        started=started, finished=finished,
        metrics={"total_qualifying_slope_cells": grid["total_qualifying_cells"],
                 "design_infeasible": grid["design_infeasible"],
                 "main_instance_n": {str(b): r["n"] for b, r in frozen["main_instances"].items()},
                 "tiny_instance_n": {str(b): r["n"] for b, r in frozen["tiny_instances"].items()}},
        raw=frozen,
        summary={"slope_grid": grid, "main_standard_B": {str(b): r["standard_B"] for b, r in frozen["main_instances"].items()}},
        certificates=[{"kind": "none"}],
        anomalies=anomalies,
    )
    run_dir = common.write_run(record, out.getvalue(), err.getvalue(), out_root=OUT_ROOT)
    print(f"wrote {run_dir}")


def cmd_slope(args) -> None:
    frozen = instances.load_frozen(run001_raw())
    started = time.time()
    with common.captured_output() as (out, err):
        print("RUN-DTREE-002: exact-enumeration slope measurement")
        result = slope_mod.run_slope_measurement(frozen)
        print(f"  design_infeasible={result['design_infeasible']}")
        print(f"  confirmatory_slope_fit={result['confirmatory_slope_fit']}")
    finished = time.time()

    anomalies = []
    if result["design_infeasible"]:
        anomalies.append({
            "type": "confirmatory_measurement_not_applicable", "stage": "exact_slope",
            "description": ("Propagated from RUN-DTREE-001's design_infeasible finding: the "
                             "confirmatory slope fit, CTRL-ENUMERATION-AUDIT, and all three "
                             "pre-registered tail checks have zero qualifying cells to operate "
                             "on and are reported as not_applicable, not improvised."),
        })
    else:
        for bits, audit in result["ctrl_enumeration_audit"].items():
            if audit.get("applicable") and not audit.get("agrees"):
                anomalies.append({"type": "enumeration_audit_disagreement", "stage": "exact_slope",
                                   "description": f"tiny curve {bits}-bit: independent audit disagreed "
                                                   f"at B'={audit['chosen_b_prime']}: {audit}"})

    certs = [{"kind": "none"}]
    record = common.RunRecord(
        run_id="RUN-DTREE-002", purpose="Exact-enumeration slope measurement over the frozen grid, "
                                          "CTRL-ENUMERATION-AUDIT, Poisson/extreme-cell/zero-cell tail checks.",
        command=_command_line("slope", []),
        seeds={"audit_seed": 20260807},
        inputs={"grid_source": "RUN-DTREE-001/raw.json"},
        started=started, finished=finished,
        metrics={"design_infeasible": result["design_infeasible"],
                 "total_qualifying_cells": result["total_qualifying_cells"],
                 "slope_gamma": (result["confirmatory_slope_fit"] or {}).get("slope_gamma"),
                 "slope_ci_95": (result["confirmatory_slope_fit"] or {}).get("ci_95")},
        raw=result,
        summary={"confirmatory_slope_fit": result["confirmatory_slope_fit"],
                 "ctrl_enumeration_audit": result["ctrl_enumeration_audit"],
                 "tail_checks": result["tail_checks"]},
        certificates=certs,
        anomalies=anomalies,
        heuristic_validation={
            "heuristic_id": "HEUR-001",
            "statement_ref": "ledger/hypotheses/H-DTREE-001.yaml#heuristic_assumptions[0]",
            "prediction": "gamma = m-1 = 2 (HEUR-001) vs gamma ~ m = 3 (birthday model)",
            "theoretical_distribution": "N/A (log-slope point comparison, not a CDF comparison)",
            "sample_size": result["total_qualifying_cells"],
            "scale_relevance": "toy (8-12 bit fields)",
        },
    )
    run_dir = common.write_run(record, out.getvalue(), err.getvalue(), out_root=OUT_ROOT)
    print(f"wrote {run_dir}")


def cmd_single_level(args) -> None:
    frozen = instances.load_frozen(run001_raw())
    bits = args.bits
    run_id = BITS_TO_RUN[bits][0]
    rec = frozen["main_instances"][bits]
    started = time.time()
    with common.captured_output() as (out, err):
        print(f"{run_id}: single-level C1 at {bits} bits (standard_B={rec['standard_B']})")
        result = costs.run_single_level(rec)
        print(f"  n_measured={result['n_measured']} found={result['decomposition_found_count']} "
              f"p_dec={result['p_dec_m3_B']} c1={result['c1_single_level']} "
              f"cumulative_gb_seconds={result['cumulative_gb_seconds']:.2f}")
    finished = time.time()

    anomalies = []
    if result["censored_by_budget"]:
        anomalies.append({"type": "cancelled_by_budget", "stage": "single_level",
                           "description": f"{len(result['censored_by_budget'])} of "
                                          f"{result['n_targets_requested']} targets not attempted "
                                          f"(cumulative Groebner-time cap reached): "
                                          f"{result['censored_by_budget']}"})
    n_capped = sum(1 for r in result["per_target"] if r["gb"] and r["gb"]["status"] != "completed")
    if n_capped:
        anomalies.append({"type": "capped_solves", "stage": "single_level",
                           "description": f"{n_capped}/{result['n_measured']} Groebner solves at "
                                          f"{run_id} hit the 20s per-solve cap or crashed within it "
                                          f"(charged at full cap cost, CTRL-FAILED-DESCENT)."})

    certs = [r["certificate"] for r in result["per_target"] if r["certificate"]] or [{"kind": "none"}]
    record = common.RunRecord(
        run_id=run_id, purpose=f"CTRL-SINGLE-LEVEL C1 at {bits} bits (50 shared targets, failures at cap cost).",
        command=_command_line("single-level", [f"--bits {bits}"]),
        seeds={"target_seed": rec["seed"]},
        inputs={"bits": bits, "curve_id": common.curve_id(rec["p"], rec["a"], rec["b"], bits),
                "standard_B": rec["standard_B"], "n": rec["n"]},
        started=started, finished=finished,
        metrics={"p_dec_m3_B": result["p_dec_m3_B"], "c1_single_level": result["c1_single_level"],
                 "c_solve_m3_mean": result["c_solve_m3"]["mean"], "n_measured": result["n_measured"],
                 "decomposition_found_count": result["decomposition_found_count"]},
        raw=result,
        summary={"c_solve_m3": result["c_solve_m3"], "p_dec_m3_B": result["p_dec_m3_B"],
                 "c1_single_level": result["c1_single_level"], "c1_undefined_reason": result["c1_undefined_reason"],
                 "n_measured": result["n_measured"], "censored_by_budget": result["censored_by_budget"]},
        certificates=certs,
        anomalies=anomalies,
        cost_model={"operation_unit": "groebner_wall_clock_seconds (implementation-bound proxy, sympy "
                                       "Buchberger/grevlex; NOT the theoretical degree of regularity)",
                    "assumptions": ["failed/capped solves charged at the full 20s cap (CTRL-FAILED-DESCENT)",
                                    "P(m,B) measured by exact curve-group-law decomposition test, "
                                    "decoupled from whether Groebner itself finished"],
                    "notes": "C1 = mean(C_solve) / P; undefined when P=0 (never silently treated as infinite)."},
    )
    run_dir = common.write_run(record, out.getvalue(), err.getvalue(), out_root=OUT_ROOT)
    print(f"wrote {run_dir}")


def cmd_depth2(args) -> None:
    frozen = instances.load_frozen(run001_raw())
    bits = args.bits
    run_id = BITS_TO_RUN[bits][1]
    rec = frozen["main_instances"][bits]
    started = time.time()
    with common.captured_output() as (out, err):
        print(f"{run_id}: depth-2 C2 at {bits} bits")
        result = costs.run_depth2(rec)
        for key, s in result["per_config_summary"].items():
            print(f"  {key}: n1={s['stage1_n_measured']} p1={s['p_m_prime_Bmed']} "
                  f"p2={s['p_m_B_stage2']} c2={s['c2']}")
        print(f"  cumulative_gb_seconds={result['cumulative_gb_seconds']:.2f} "
              f"budget_exhausted={result['budget_exhausted']}")
    finished = time.time()

    vp = costs.validity_prefix_check(result["per_config_summary"])
    anomalies = []
    if result["budget_exhausted"]:
        anomalies.append({"type": "cumulative_budget_exhausted", "stage": "depth2",
                           "description": f"{run_id} hit the 1500s cumulative Groebner-time cap after "
                                          f"{result['rounds_completed']} target rounds; remaining "
                                          f"targets/configs recorded per-config in "
                                          f"censored_by_budget_target_indices."})
    if not vp["validity_prefix_met"]:
        anomalies.append({"type": "resource_exhaustion_validity_prefix", "stage": "depth2",
                           "description": f"{run_id}: only {vp['n_configs_meeting_minimum']} "
                                          f"configuration(s) reached the {vp['min_targets_per_config']}-target "
                                          f"minimum (need >= {vp['min_configs_required']}); per the frozen "
                                          f"stopping rule this size's depth-2 measurement is "
                                          f"resource_exhaustion -- recorded, not evidence."})

    certs = []
    for cfg in result["configs"].values():
        for r in cfg["stage1"]:
            if r.get("certificate"):
                certs.append(r["certificate"])
        for r in cfg["stage2"]:
            if r.get("certificate"):
                certs.append(r["certificate"])
    if not certs:
        certs = [{"kind": "none"}]

    status = "completed_valid"
    if not vp["validity_prefix_met"]:
        status = "resource_exhaustion"

    record = common.RunRecord(
        run_id=run_id, purpose=f"Depth-2 C2 measurement at {bits} bits: frozen configuration order, "
                                 f"50 shared targets, both stages charged, CTRL-FAILED-DESCENT.",
        command=_command_line("depth2", [f"--bits {bits}"]),
        seeds={"target_seed": rec["seed"]},
        inputs={"bits": bits, "curve_id": common.curve_id(rec["p"], rec["a"], rec["b"], bits),
                "standard_B": rec["standard_B"], "n": rec["n"],
                "b_med_grid": {str(m): rec["medium_bases"][m]["size"] for m in (2, 4, 8, 16)},
                "config_order": [costs.config_key(m, mult) for m, mult in costs.FROZEN_CONFIG_ORDER]},
        started=started, finished=finished,
        metrics={"cumulative_gb_seconds": result["cumulative_gb_seconds"],
                 "budget_exhausted": result["budget_exhausted"],
                 "validity_prefix_met": vp["validity_prefix_met"],
                 "c2_by_config": {k: v["c2"] for k, v in result["per_config_summary"].items()}},
        raw=result,
        summary={"per_config_summary": result["per_config_summary"], "validity_prefix": vp},
        certificates=certs,
        anomalies=anomalies,
        status=status,
        # resource_exhaustion is a distinct terminal status (docs/task-lifecycle.md step 6),
        # not the same thing as an invalid run: every measurement actually taken is real,
        # certificate-verified data. valid=True/invalid_reason=None here says "trust the
        # data that exists"; status="resource_exhaustion" (and the anomaly above) says "it
        # falls short of the pre-registered validity-prefix threshold for a decisive
        # comparison" -- recorded, per the falsification_criterion, as inconclusive rather
        # than invalidated.
        valid=True,
        invalid_reason=None,
        cost_model={"operation_unit": "groebner_wall_clock_seconds (implementation-bound proxy)",
                    "assumptions": ["stage-1 and stage-2 success probabilities measured independently "
                                    "per configuration via the exact curve-group-law test",
                                    "C2 = C_solve(m')/P(m',B_med) + m'*C_solve(m)/P(m,B), both terms "
                                    "measured fresh on this configuration's own attempts, not inherited "
                                    "from the single-level run",
                                    "failed/capped solves charged at the full 20s cap"],
                    "notes": "bootstrap CI on C2/C1 is computed in RUN-DTREE-012 (aggregation), not here, "
                             "per the planned-run split."},
    )
    run_dir = common.write_run(record, out.getvalue(), err.getvalue(), out_root=OUT_ROOT)
    print(f"wrote {run_dir}")


def cmd_medbase_logs(args) -> None:
    frozen = instances.load_frozen(run001_raw())
    started = time.time()
    with common.captured_output() as (out, err):
        print("RUN-DTREE-009: CTRL-MEDBASE-LOGS medium-base log-table construction cost")
        by_size = {}
        for bits, rec in frozen["main_instances"].items():
            r = costs.run_medbase_logs(rec)
            by_size[bits] = r
            print(f"  {bits}-bit: n_sampled={r['n_sampled_elements']} "
                  f"per_element_cost={r['measured_per_element_cost_seconds']['mean']}")
    finished = time.time()

    certs = []
    for r in by_size.values():
        for e in r["per_element"]:
            if e.get("certificate"):
                certs.append(e["certificate"])
    if not certs:
        certs = [{"kind": "none"}]

    record = common.RunRecord(
        run_id="RUN-DTREE-009", purpose="CTRL-MEDBASE-LOGS: medium-base log-table construction cost "
                                          "at the smallest B_med per size.",
        command=_command_line("medbase-logs", []),
        seeds={bits: rec["seed"] for bits, rec in frozen["main_instances"].items()},
        inputs={"smallest_b_med_multiplier": 2, "n_sample_requested": 10},
        started=started, finished=finished,
        metrics={"per_element_cost_seconds": {str(b): r["measured_per_element_cost_seconds"]["mean"]
                                               for b, r in by_size.items()}},
        raw={"by_size": by_size},
        summary={str(b): {"per_element_cost": r["measured_per_element_cost_seconds"],
                           "extrapolation_to_full_grid": r["extrapolation_to_full_grid"]}
                 for b, r in by_size.items()},
        certificates=certs,
        cost_model={"operation_unit": "groebner_wall_clock_seconds",
                    "assumptions": ["per-element cost measured at the smallest B_med only, "
                                    "extrapolated LINEARLY to larger B_med by multiplying by size",
                                    "extrapolation is flagged, never presented as measured"],
                    "notes": "charged to preprocessing, never to per-target descent cost."},
    )
    run_dir = common.write_run(record, out.getvalue(), err.getvalue(), out_root=OUT_ROOT)
    print(f"wrote {run_dir}")


def cmd_rho(args) -> None:
    frozen = instances.load_frozen(run001_raw())
    started = time.time()
    with common.captured_output() as (out, err):
        print("RUN-DTREE-010: CTRL-MATCHED-RHO baseline")
        by_size = {}
        for bits, rec in frozen["main_instances"].items():
            r = costs.run_rho_baseline(rec)
            by_size[bits] = r
            print(f"  {bits}-bit: n_solved={r['n_solved']}/{r['n_targets']} "
                  f"median_ops={r['group_operations_summary']['median']}")
    finished = time.time()

    unsolved = {b: r["n_targets"] - r["n_solved"] for b, r in by_size.items()}
    anomalies = []
    for b, n in unsolved.items():
        if n:
            anomalies.append({"type": "rho_unsolved", "stage": "preprocessing_and_baselines",
                               "description": f"{n} of {by_size[b]['n_targets']} rho baseline targets "
                                              f"at {b} bits did not yield a certified discrete log "
                                              f"within the iteration budget."})

    certs = []
    for r in by_size.values():
        for t in r["per_target"]:
            if t.get("certificate"):
                certs.append(t["certificate"])
    if not certs:
        certs = [{"kind": "none"}]

    record = common.RunRecord(
        run_id="RUN-DTREE-010", purpose="CTRL-MATCHED-RHO baseline on the same 50 targets per main "
                                          "curve, verified discrete-log certificates.",
        command=_command_line("rho", []),
        seeds={str(bits): rec["seed"] for bits, rec in frozen["main_instances"].items()},
        inputs={"bits": [16, 20, 24]},
        started=started, finished=finished,
        metrics={"median_group_operations": {str(b): r["group_operations_summary"]["median"] for b, r in by_size.items()},
                 "n_solved": {str(b): r["n_solved"] for b, r in by_size.items()}},
        raw={"by_size": by_size},
        summary={str(b): r["group_operations_summary"] for b, r in by_size.items()},
        certificates=certs,
        anomalies=anomalies,
    )
    run_dir = common.write_run(record, out.getvalue(), err.getvalue(), out_root=OUT_ROOT)
    print(f"wrote {run_dir}")


def cmd_prob_sampling(args) -> None:
    frozen = instances.load_frozen(run001_raw())
    depth2_summaries = {}
    single_level_summaries = {}
    for bits, (sl_run, d2_run) in BITS_TO_RUN.items():
        depth2_summaries[bits] = aggregate_mod.load_run_raw(os.path.join(runs_dir(), d2_run))
        single_level_summaries[bits] = aggregate_mod.load_run_raw(os.path.join(runs_dir(), sl_run))

    started = time.time()
    with common.captured_output() as (out, err):
        print("RUN-DTREE-011: decomposition-probability sampling (Wilson) + CTRL-GENERIC-HEURISTIC")
        result = costs.run_probability_sampling_all_sizes(
            frozen["main_instances"], depth2_summaries, single_level_summaries, n_sample=200)
        for bits, r in result["by_size"].items():
            labels = {k: v["label"] for k, v in r["generic_heuristic_control"].items()}
            print(f"  {bits}-bit generic-heuristic labels: {labels}")
    finished = time.time()

    record = common.RunRecord(
        run_id="RUN-DTREE-011", purpose="Decomposition-probability sampling at 16-24 bits for every "
                                          "tested (m',B_med) cell (Wilson intervals); CTRL-GENERIC-"
                                          "HEURISTIC comparison of predicted vs measured C2.",
        command=_command_line("prob-sampling", []),
        seeds={str(bits): rec["seed"] for bits, rec in frozen["main_instances"].items()},
        inputs={"n_sample_per_cell": 200},
        started=started, finished=finished,
        metrics={"generic_heuristic_labels": {
            str(b): {k: v["label"] for k, v in r["generic_heuristic_control"].items()}
            for b, r in result["by_size"].items()}},
        raw=result,
        summary={str(b): {"cells": {k: v.get("wilson_95") for k, v in r["cells"].items()},
                           "generic_heuristic_control": r["generic_heuristic_control"]}
                 for b, r in result["by_size"].items()},
        certificates=[{"kind": "none"}],
    )
    run_dir = common.write_run(record, out.getvalue(), err.getvalue(), out_root=OUT_ROOT)
    print(f"wrote {run_dir}")


def cmd_aggregate(args) -> None:
    frozen = instances.load_frozen(run001_raw())
    started = time.time()
    with common.captured_output() as (out, err):
        print("RUN-DTREE-012: aggregation")
        result = aggregate_mod.aggregate(runs_dir(), frozen)
        for bits, s in result["per_size"].items():
            print(f"  {bits}-bit: optimal_config={s['optimal_config']} optimal_c2={s['optimal_c2']} "
                  f"c1={s['c1_single_level']} winners={s['winning_configs_c2_below_0_8_c1_and_ci_below_1']}")
        print(f"  c2_claim_decided_positive_at_largest_size={result['c2_claim_decided_positive_at_largest_size']}")
        print(f"  c1_design_infeasible={result['c1_design_infeasible']}")
    finished = time.time()

    all_required_present = True
    missing = []
    for rid in [f"RUN-DTREE-{i:03d}" for i in range(1, 12)]:
        rd = os.path.join(runs_dir(), rid)
        for fname in ("manifest.yaml", "command.txt", "environment.json", "raw.json",
                      "summary.json", "stdout.txt", "stderr.txt"):
            if not os.path.exists(os.path.join(rd, fname)):
                all_required_present = False
                missing.append(os.path.join(rid, fname))

    anomalies = []
    if missing:
        anomalies.append({"type": "missing_prior_artifact", "stage": "aggregation",
                           "description": f"stop_rule triggered: missing required artifacts from an "
                                          f"earlier stage: {missing}"})

    record = common.RunRecord(
        run_id="RUN-DTREE-012", purpose="Aggregation: optimal B_med per size, C2/C1 with bootstrap "
                                          "CIs, slope-fit summary, fully charged totals.",
        command=_command_line("aggregate", []),
        seeds={},
        inputs={"prior_runs": [f"RUN-DTREE-{i:03d}" for i in range(1, 12)]},
        started=started, finished=finished,
        metrics={"c2_claim_decided_positive_at_largest_size": result["c2_claim_decided_positive_at_largest_size"],
                 "c1_design_infeasible": result["c1_design_infeasible"],
                 "all_required_prior_artifacts_present": all_required_present},
        raw=result,
        summary=result,
        certificates=[{"kind": "none"}],
        anomalies=anomalies,
        status="completed_valid" if all_required_present else "failed_infrastructure",
        valid=all_required_present,
        invalid_reason=None if all_required_present else f"missing prior artifacts: {missing}",
    )
    run_dir = common.write_run(record, out.getvalue(), err.getvalue(), out_root=OUT_ROOT)
    print(f"wrote {run_dir}")


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="subcommand", required=True)
    sub.add_parser("freeze")
    sub.add_parser("slope")
    p_sl = sub.add_parser("single-level")
    p_sl.add_argument("--bits", type=int, required=True, choices=[16, 20, 24])
    p_d2 = sub.add_parser("depth2")
    p_d2.add_argument("--bits", type=int, required=True, choices=[16, 20, 24])
    sub.add_parser("medbase-logs")
    sub.add_parser("rho")
    sub.add_parser("prob-sampling")
    sub.add_parser("aggregate")
    args = ap.parse_args()

    dispatch = {
        "freeze": cmd_freeze, "slope": cmd_slope, "single-level": cmd_single_level,
        "depth2": cmd_depth2, "medbase-logs": cmd_medbase_logs, "rho": cmd_rho,
        "prob-sampling": cmd_prob_sampling, "aggregate": cmd_aggregate,
    }
    dispatch[args.subcommand](args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
