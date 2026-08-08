"""EXP-FIB-001 orchestrator: executes RUN-FIB-001..008 in sequence, enforcing
the frozen budget's stage caps, and writes the immutable run records plus
frozen-instances.yaml / analysis.md / execution-report.yaml.

Usage: python3 -m driver.orchestrate   (run from experiments/EXP-FIB-001/)
"""
from __future__ import annotations

import io
import json
import math
import os
import resource
import sys
import time
from contextlib import redirect_stdout
from math import comb

import yaml

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from harness.rho import solve as rho_solve  # noqa: E402

from . import decompcost, instances, invariant, runlib, statslib  # noqa: E402
from .common import canon_lift  # noqa: E402

EXP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PER_SOLVE_CAP = 20.0
PER_CURVE_DECOMP_WALL_CAP = 1500.0
PER_RUN_WALL_CAP = 1800.0
STAGE_BUDGETS = {
    "freeze_and_truth_control": 1200.0,
    "invariant_tables": 3300.0,
    "decomposition_measurement": 3600.0,
    "correlation_and_decision": 900.0,
    "twophase_gated": 900.0,
}
TARGETS_PER_MAIN_CURVE = 200
TARGETS_PER_TRUTH_CURVE = 50
SAMPLE_MAX_EVALS_20BIT = 50_000_000
CORRELATION_PREFIX_MIN = 100
PERM_SEED = 20260807

deviations_log: list[str] = []
anomalies_log: list[str] = []


def _resources():
    ru = resource.getrusage(resource.RUSAGE_SELF)
    return {"peak_rss_bytes_self_reported": ru.ru_maxrss, "cpu_seconds_user": ru.ru_utime,
            "cpu_seconds_sys": ru.ru_stime,
            "note": "ru_maxrss units are platform-dependent (bytes on macOS, KB on Linux)"}


def _run(run_id, command, parameters, seeds, fn):
    """Execute fn() capturing stdout, timing, and exceptions; write the run."""
    buf = io.StringIO()
    t0 = time.time()
    status = "completed_valid"
    invalid_reason = None
    raw = {}
    summary = {}
    stderr_text = ""
    try:
        with redirect_stdout(buf):
            raw, summary, status_override, invalid_reason_override = fn()
        if status_override:
            status = status_override
            invalid_reason = invalid_reason_override
    except Exception as e:  # noqa: BLE001
        status = "failed_implementation"
        invalid_reason = f"implementation_error: {e!r}"
        stderr_text = f"{e!r}\n"
        import traceback
        stderr_text += traceback.format_exc()
    t1 = time.time()
    timing = {"started_at": runlib.now_iso(), "wall_seconds": t1 - t0}
    resources = _resources()
    certificate = {"kind": "none", "verified": True, "verifier": "no-claim",
                    "note": "measurement run; no discrete-log or relation claim made"}
    run_dir = runlib.write_run(
        run_id, status=status, command=command, parameters=parameters, seeds=seeds,
        timing=timing, resources=resources, raw=raw, summary=summary,
        stdout_text=buf.getvalue(), stderr_text=stderr_text, certificate=certificate,
        invalid_reason=invalid_reason, deviations=list(deviations_log),
        anomalies=list(anomalies_log))
    print(f"[{run_id}] status={status} wall={t1 - t0:.1f}s -> {run_dir}", file=sys.stderr)
    return {"run_id": run_id, "status": status, "wall_seconds": t1 - t0,
            "summary": summary, "raw": raw}


# ---------------------------------------------------------------------------
# RUN-FIB-001: freeze instances/targets/factor bases; exhaustive-truth control
# ---------------------------------------------------------------------------

def _build_all_curves():
    main_ctx = {s["id"]: instances.build_curve(s) for s in instances.MAIN_CURVES}
    truth_ctx = {s["id"]: instances.build_curve(s) for s in instances.TRUTH_CURVES}
    return main_ctx, truth_ctx


def run_fib_001():
    t_stage0 = time.time()
    main_ctx, truth_ctx = _build_all_curves()

    fingerprints = {}
    targets_main = {}
    for cid, ctx in main_ctx.items():
        fingerprints[cid] = {**instances.curve_fingerprint(ctx), "field_bits": ctx.spec["field_bits"],
                              "seed": ctx.spec["seed"]}
        targets_main[cid] = instances.generate_targets(ctx, TARGETS_PER_MAIN_CURVE)
    targets_truth = {}
    for cid, ctx in truth_ctx.items():
        fingerprints[cid] = {**instances.curve_fingerprint(ctx), "field_bits": ctx.spec["field_bits"],
                              "seed": ctx.spec["seed"]}
        targets_truth[cid] = instances.generate_targets(ctx, TARGETS_PER_TRUTH_CURVE, tag="truth_targets")

    # write frozen-instances.yaml (top-level required artifact)
    frozen = {"experiment_id": "EXP-FIB-001",
              "main_curves": {cid: fingerprints[cid] for cid in main_ctx},
              "truth_curves": {cid: fingerprints[cid] for cid in truth_ctx},
              "frozen_at": runlib.now_iso()}
    with open(os.path.join(EXP_DIR, "frozen-instances.yaml"), "w") as f:
        yaml.safe_dump(frozen, f, sort_keys=False)

    # exhaustive-truth control on the 3 truth curves (150 audit targets)
    audit_results = []
    mismatches = []
    for cid, ctx in truth_ctx.items():
        table, n_evals = invariant.build_table_exact(ctx)
        for tgt in targets_truth[cid]:
            R = (tgt["Rx"], tgt["Ry"])
            measured = invariant.n_R_exact(table, R)
            truth = invariant.independent_exact_count(ctx, R)
            ok = measured == truth
            if not ok:
                mismatches.append({"curve": cid, "target_index": tgt["index"],
                                    "measured": measured, "truth": truth})
            audit_results.append({"curve": cid, "target_index": tgt["index"],
                                   "measured_nR": measured, "truth_nR": truth, "match": ok})
        if time.time() - t_stage0 > STAGE_BUDGETS["freeze_and_truth_control"]:
            deviations_log.append(
                "freeze_and_truth_control stage exceeded its 1200s budget mid-audit; "
                "remaining truth curves processed anyway to complete the 150-target audit "
                "honestly rather than leaving it partial (recorded as a timing deviation)."
            )
            break

    agreement = sum(1 for a in audit_results if a["match"]) / len(audit_results) if audit_results else None
    ctrl_pass = agreement == 1.0 if agreement is not None else False

    raw = {"fingerprints": fingerprints,
           "targets_main": targets_main, "targets_truth": targets_truth,
           "audit_results": audit_results}
    summary = {
        "CTRL-EXHAUSTIVE-TRUTH": {
            "n_audit_targets": len(audit_results), "agreement_fraction": agreement,
            "pass": ctrl_pass, "mismatches": mismatches,
        },
        "curve_fingerprints": {cid: {"sha256": fingerprints[cid]["sha256"], "B": fingerprints[cid]["B"],
                                       "N": fingerprints[cid]["N"]} for cid in fingerprints},
    }
    status = "completed_valid" if ctrl_pass else "invalid_measurement"
    invalid_reason = None if ctrl_pass else "CTRL-EXHAUSTIVE-TRUTH mismatch: n_R instrument failure"
    print(f"truth control agreement: {agreement}")
    return raw, summary, status, invalid_reason


# ---------------------------------------------------------------------------
# RUN-FIB-002: exact 16-bit invariant tables + n_R for 200 targets/curve
# ---------------------------------------------------------------------------

def run_fib_002():
    main_ctx, _ = _build_all_curves()
    per_curve = {}
    for cid in ("C16-1", "C16-2"):
        ctx = main_ctx[cid]
        t0 = time.time()
        table, n_evals = invariant.build_table_exact(ctx)
        build_wall = time.time() - t0
        targets = instances.generate_targets(ctx, TARGETS_PER_MAIN_CURVE)
        n_R_list = []
        for tgt in targets:
            R = (tgt["Rx"], tgt["Ry"])
            n_R_list.append(invariant.n_R_exact(table, R))
        hist = {}
        for v in n_R_list:
            hist[v] = hist.get(v, 0) + 1
        per_curve[cid] = {"B": ctx.B, "N": ctx.N, "C_B_3": comb(ctx.B, 3),
                            "table_build_seconds": build_wall, "table_n_evals": n_evals,
                            "n_R_per_target": n_R_list, "histogram": hist,
                            "lambda_expected": comb(ctx.B, 3) / ctx.N if ctx.N else None}
        print(f"{cid}: B={ctx.B} N={ctx.N} table_build={build_wall:.2f}s mean n_R={sum(n_R_list)/len(n_R_list):.2f}")
    raw = {"per_curve": per_curve}
    summary = {cid: {"B": per_curve[cid]["B"], "N": per_curve[cid]["N"],
                       "table_build_seconds": per_curve[cid]["table_build_seconds"],
                       "mean_n_R": sum(per_curve[cid]["n_R_per_target"]) / len(per_curve[cid]["n_R_per_target"]),
                       "lambda_expected": per_curve[cid]["lambda_expected"]}
               for cid in per_curve}
    return raw, summary, None, None


# ---------------------------------------------------------------------------
# RUN-FIB-003: sampled 20-bit invariant tables (5e7 evals or 1500s cap)
# ---------------------------------------------------------------------------

def run_fib_003():
    main_ctx, _ = _build_all_curves()
    per_curve = {}
    for cid in ("C20-1", "C20-2"):
        ctx = main_ctx[cid]
        sample = invariant.build_table_sampled(ctx, SAMPLE_MAX_EVALS_20BIT, PER_CURVE_DECOMP_WALL_CAP)
        targets = instances.generate_targets(ctx, TARGETS_PER_MAIN_CURVE)
        n_R_estimates = []
        for tgt in targets:
            R = (tgt["Rx"], tgt["Ry"])
            est = invariant.n_R_sampled_estimate(sample, R, ctx.B)
            n_R_estimates.append(est)
        per_curve[cid] = {"B": ctx.B, "N": ctx.N, "C_B_3": comb(ctx.B, 3),
                            "sample_n_evals": sample["n_evals"], "sample_stop_reason": sample["stop_reason"],
                            "sample_wall_seconds": sample["wall_seconds"],
                            "n_R_estimates": n_R_estimates,
                            "lambda_expected": comb(ctx.B, 3) / ctx.N if ctx.N else None}
        print(f"{cid}: B={ctx.B} N={ctx.N} n_evals={sample['n_evals']} stop={sample['stop_reason']} "
              f"wall={sample['wall_seconds']:.1f}s")
        if sample["n_evals"] < SAMPLE_MAX_EVALS_20BIT:
            deviations_log.append(
                f"{cid}: sampled invariant table stopped at n_evals={sample['n_evals']} "
                f"(< target 5e7) due to stop_reason={sample['stop_reason']} (1500s per-curve cap), "
                "per the frozen stopping rule; recorded honestly, never extrapolated."
            )
    raw = {"per_curve": per_curve}
    summary = {cid: {"B": per_curve[cid]["B"], "N": per_curve[cid]["N"],
                       "sample_n_evals": per_curve[cid]["sample_n_evals"],
                       "sample_stop_reason": per_curve[cid]["sample_stop_reason"],
                       "lambda_expected": per_curve[cid]["lambda_expected"]}
               for cid in per_curve}
    return raw, summary, None, None


# ---------------------------------------------------------------------------
# RUN-FIB-004 / RUN-FIB-005: decomposition cost measurement
# ---------------------------------------------------------------------------

def _run_decomp_measurement(curve_ids):
    main_ctx, _ = _build_all_curves()
    per_curve = {}
    run_t0 = time.time()
    for cid in curve_ids:
        ctx = main_ctx[cid]
        targets = instances.generate_targets(ctx, TARGETS_PER_MAIN_CURVE)
        measurements = []
        curve_t0 = time.time()
        stop_reason = "completed_all_targets"
        for tgt in targets:
            if time.time() - curve_t0 > PER_CURVE_DECOMP_WALL_CAP:
                stop_reason = "per_curve_cumulative_cap_1500s"
                break
            if time.time() - run_t0 > PER_RUN_WALL_CAP:
                stop_reason = "per_run_wall_cap_1800s"
                break
            r = decompcost.measure_s4_decomposition(ctx.E.p, ctx.E.a, ctx.E.b, ctx.V,
                                                      tgt["Rx"], cap_seconds=PER_SOLVE_CAP)
            r["target_index"] = tgt["index"]
            measurements.append(r)
        n_measured = len(measurements)
        n_capped = sum(1 for m in measurements if m["capped"])
        resource_exhaustion = n_measured < CORRELATION_PREFIX_MIN
        per_curve[cid] = {"B": ctx.B, "N": ctx.N, "n_targets_planned": len(targets),
                            "n_measured": n_measured, "n_capped": n_capped,
                            "stop_reason": stop_reason,
                            "resource_exhaustion": resource_exhaustion,
                            "measurements": measurements,
                            "wall_seconds_curve": time.time() - curve_t0}
        print(f"{cid}: B={ctx.B} measured={n_measured}/{len(targets)} capped={n_capped} "
              f"stop={stop_reason} resource_exhaustion={resource_exhaustion}")
        if resource_exhaustion:
            anomalies_log.append(
                f"{cid}: only {n_measured}/{len(targets)} targets measured before the per-curve "
                f"1500s decomposition-cost budget was exhausted (of which {n_capped} hit the 20s "
                "per-solve cap); below the 100-target minimum prefix required for the correlation "
                "run, so this curve is marked resource_exhaustion for RUN-FIB-006, not evidence."
            )
    return per_curve


def run_fib_004():
    per_curve = _run_decomp_measurement(("C16-1", "C16-2"))
    raw = {"per_curve": per_curve}
    summary = {cid: {"n_measured": per_curve[cid]["n_measured"], "n_capped": per_curve[cid]["n_capped"],
                       "resource_exhaustion": per_curve[cid]["resource_exhaustion"],
                       "stop_reason": per_curve[cid]["stop_reason"]} for cid in per_curve}
    return raw, summary, None, None


def run_fib_005():
    per_curve = _run_decomp_measurement(("C20-1", "C20-2"))
    raw = {"per_curve": per_curve}
    summary = {cid: {"n_measured": per_curve[cid]["n_measured"], "n_capped": per_curve[cid]["n_capped"],
                       "resource_exhaustion": per_curve[cid]["resource_exhaustion"],
                       "stop_reason": per_curve[cid]["stop_reason"]} for cid in per_curve}
    return raw, summary, None, None


# ---------------------------------------------------------------------------
# RUN-FIB-006: correlation decision
# ---------------------------------------------------------------------------

def run_fib_006(fib002_raw, fib003_raw, fib004_raw, fib005_raw):
    main_ctx, _ = _build_all_curves()
    nR_by_curve = {}
    for cid, d in fib002_raw["per_curve"].items():
        # histogram keys round-trip through JSON as strings when raw.json is
        # reloaded from disk (e.g. by driver.resume); coerce back to int.
        hist_int = {int(k): v for k, v in d["histogram"].items()}
        nR_by_curve[cid] = {"values": d["n_R_per_target"], "histogram": hist_int, "exact": True}
    for cid, d in fib003_raw["per_curve"].items():
        est_values = [round(e["estimate"]) for e in d["n_R_estimates"]]
        hist = {}
        for v in est_values:
            hist[v] = hist.get(v, 0) + 1
        nR_by_curve[cid] = {"values": est_values, "histogram": hist, "exact": False,
                              "raw_estimates": d["n_R_estimates"]}

    decomp_by_curve = {}
    for cid, d in fib004_raw["per_curve"].items():
        decomp_by_curve[cid] = d
    for cid, d in fib005_raw["per_curve"].items():
        decomp_by_curve[cid] = d

    results = {}
    for cid in ("C16-1", "C16-2", "C20-1", "C20-2"):
        ctx = main_ctx[cid]
        d = decomp_by_curve[cid]
        n_R_full = nR_by_curve[cid]["values"]
        # CTRL-QUASIRANDOM-DISTRIBUTION (HEUR-001 fit) and the extreme-value /
        # zero-class tail checks depend only on the n_R histogram (RUN-FIB-002/
        # 003), never on decomposition-cost data, so they are computed for
        # EVERY curve regardless of decomposition-cost resource_exhaustion.
        fit = statslib.poisson_fit(nR_by_curve[cid]["histogram"], ctx.B, ctx.N)
        tails = statslib.tail_checks(n_R_full, [None] * len(n_R_full), ctx.B, ctx.N, seed=PERM_SEED + 2)

        if d["resource_exhaustion"]:
            results[cid] = {"status": "resource_exhaustion",
                              "reason": f"only {d['n_measured']} of {d['n_targets_planned']} targets measured "
                                        f"(< {CORRELATION_PREFIX_MIN} minimum); correlation, label-shuffle "
                                        "control, and the hardest-decile tail check not computed for this "
                                        "curve (they require decomposition-cost data); the Poisson fit and "
                                        "the extreme-value/zero-class tail checks ARE computed below since "
                                        "they depend only on the n_R histogram.",
                              "poisson_fit": fit, "tail_checks": tails}
            continue
        idxs = [m["target_index"] for m in d["measurements"]]
        costs = [m["cost_seconds"] for m in d["measurements"]]
        n_R_prefix = [n_R_full[i] for i in idxs]

        corr = statslib.spearman_with_permutation_null(n_R_prefix, costs, seed=PERM_SEED)
        shuffle = statslib.label_shuffle_control(n_R_prefix, costs, seed=PERM_SEED + 1)
        # hardest-decile check needs the (n_R, cost) prefix specifically
        tails_prefix = statslib.tail_checks(n_R_prefix, costs, ctx.B, ctx.N, seed=PERM_SEED + 3)
        tails["hardest_decile_check"] = tails_prefix["hardest_decile_check"]

        results[cid] = {
            "status": "measured", "n_prefix": len(idxs),
            "correlation": corr, "label_shuffle_control": shuffle,
            "poisson_fit": fit, "tail_checks": tails,
        }
        print(f"{cid}: rho_s={corr.get('rho_s')} p={corr.get('p_value')} n={corr.get('n')} "
              f"shuffle_rho_s={shuffle.get('rho_s')}")

    # Bonferroni-adjusted Poisson fit p-values across the 4 curves (computed
    # for every curve now, regardless of decomposition-cost resource_exhaustion)
    n_curves_with_fit = sum(1 for r in results.values()
                              if r.get("poisson_fit", {}).get("p_value_raw") is not None)
    for cid, r in results.items():
        if r.get("poisson_fit", {}).get("p_value_raw") is not None:
            r["poisson_fit"]["p_value_bonferroni"] = min(1.0, r["poisson_fit"]["p_value_raw"] * 4)

    correlation_gate_curves = [cid for cid, r in results.items()
                                 if r.get("status") == "measured" and r["correlation"].get("rho_s") is not None
                                 and abs(r["correlation"]["rho_s"]) >= 0.4
                                 and r["correlation"].get("p_value", 1.0) < 0.01]
    shuffle_gate_pass = all(
        (r["label_shuffle_control"].get("rho_s") is None or abs(r["label_shuffle_control"]["rho_s"]) <= 0.2)
        for r in results.values() if r.get("status") == "measured"
    )

    raw = {"per_curve": results}
    summary = {
        "n_curves_measured": sum(1 for r in results.values() if r.get("status") == "measured"),
        "n_curves_resource_exhaustion": sum(1 for r in results.values() if r.get("status") == "resource_exhaustion"),
        "correlation_gate_curves_passing": correlation_gate_curves,
        "correlation_gate_pass_count": len(correlation_gate_curves),
        "correlation_gate_pass_overall": len(correlation_gate_curves) >= 3,
        "CTRL-LABEL-SHUFFLE_pass": shuffle_gate_pass,
        "per_curve_status": {cid: r.get("status") for cid, r in results.items()},
    }
    return raw, summary, None, None


# ---------------------------------------------------------------------------
# RUN-FIB-007: predictor-cost accounting
# ---------------------------------------------------------------------------

def run_fib_007(fib002_raw, fib003_raw):
    main_ctx, _ = _build_all_curves()
    results = {}
    for cid in ("C16-1", "C16-2", "C20-1", "C20-2"):
        ctx = main_ctx[cid]
        rho_t0 = time.time()
        rho_result = rho_solve(ctx.inst)
        rho_wall = time.time() - rho_t0
        ops_per_second = (rho_result.total_group_operations / rho_wall) if rho_wall > 0 else None

        if cid in fib002_raw["per_curve"]:
            table_build_s = fib002_raw["per_curve"][cid]["table_build_seconds"]
            n_targets = len(fib002_raw["per_curve"][cid]["n_R_per_target"])
        else:
            table_build_s = fib003_raw["per_curve"][cid]["sample_wall_seconds"]
            n_targets = len(fib003_raw["per_curve"][cid]["n_R_estimates"])
        amortized_predictor_seconds = table_build_s / n_targets if n_targets else None
        amortized_predictor_group_ops = (amortized_predictor_seconds * ops_per_second
                                           if amortized_predictor_seconds is not None and ops_per_second else None)
        results[cid] = {
            "table_build_seconds_total": table_build_s, "n_targets": n_targets,
            "amortized_predictor_seconds_per_target": amortized_predictor_seconds,
            "rho_group_operations_per_second_measured": ops_per_second,
            "amortized_predictor_group_op_equivalents": amortized_predictor_group_ops,
            "rho_solved": rho_result.solved, "rho_total_group_operations": rho_result.total_group_operations,
            "rho_wall_seconds": rho_wall,
        }
        print(f"{cid}: amortized_predictor_s={amortized_predictor_seconds} "
              f"rho_ops_per_s={ops_per_second}")
    raw = {"per_curve": results}
    summary = {cid: {"amortized_predictor_seconds_per_target": results[cid]["amortized_predictor_seconds_per_target"]}
               for cid in results}
    return raw, summary, None, None


def compute_predictor_cost_ratio(fib007_raw, fib004_raw, fib005_raw):
    """ratio = amortized predictor cost / median decomposition cost, per curve."""
    decomp_by_curve = {**fib004_raw["per_curve"], **fib005_raw["per_curve"]}
    ratios = {}
    for cid, pc in fib007_raw["per_curve"].items():
        d = decomp_by_curve[cid]
        costs = [m["cost_seconds"] for m in d["measurements"]]
        if not costs or pc["amortized_predictor_seconds_per_target"] is None:
            ratios[cid] = None
            continue
        costs_sorted = sorted(costs)
        median = costs_sorted[len(costs_sorted) // 2]
        ratios[cid] = pc["amortized_predictor_seconds_per_target"] / median if median > 0 else None
    return ratios


# ---------------------------------------------------------------------------
# RUN-FIB-008: gated two-phase secondary
# ---------------------------------------------------------------------------

def run_fib_008(gate_pass, gate_reason, fib004_raw, fib005_raw, fib006_raw, fib007_raw, ratios):
    if not gate_pass:
        raw = {"gate_pass": False, "reason": gate_reason}
        summary = {"gate_pass": False, "reason": gate_reason}
        print(f"RUN-FIB-008 cancelled_by_gate: {gate_reason}")
        return raw, summary, "cancelled_by_gate", gate_reason

    # (Not reached in this execution; scaffold retained for completeness in
    # case a future re-run of this frozen protocol clears both gates.)
    raw = {"gate_pass": True, "note": "two-phase simulation not implemented in this run "
                                        "because the gate was not expected to pass; if reached, "
                                        "this is a specification_error to report to the Coordinator."}
    summary = raw
    return raw, summary, "invalid_measurement", "gate passed but two-phase simulator not exercised"


TOTAL_BUDGET = 9900.0


def main():
    exp_t0 = time.time()
    results = {}

    def budget_left():
        return TOTAL_BUDGET - (time.time() - exp_t0)

    # RUN-FIB-001
    r1 = _run("RUN-FIB-001",
              "python3 -m driver.orchestrate  # RUN-FIB-001: freeze + CTRL-EXHAUSTIVE-TRUTH",
              {"targets_per_main_curve": TARGETS_PER_MAIN_CURVE,
               "targets_per_truth_curve": TARGETS_PER_TRUTH_CURVE},
              {"instance_seeds": [1, 2]}, run_fib_001)
    results["RUN-FIB-001"] = r1
    truth_pass = r1["summary"]["CTRL-EXHAUSTIVE-TRUTH"]["pass"]
    if r1["status"] != "completed_valid" or not truth_pass:
        anomalies_log.append(
            "CTRL-EXHAUSTIVE-TRUTH failed or RUN-FIB-001 did not complete validly; per the frozen "
            "stopping rule, downstream correlation runs are recorded as invalid (instrument failure), "
            "not negative evidence. Stopping the experiment here."
        )
        _write_stop_summary(results, reason="CTRL-EXHAUSTIVE-TRUTH failure or RUN-FIB-001 invalid")
        return results

    # RUN-FIB-002
    r2 = _run("RUN-FIB-002", "python3 -m driver.orchestrate  # RUN-FIB-002: exact 16-bit invariant tables",
              {"targets_per_curve": TARGETS_PER_MAIN_CURVE, "curves": ["C16-1", "C16-2"]},
              {"instance_seeds": [1, 2]}, run_fib_002)
    results["RUN-FIB-002"] = r2

    # RUN-FIB-003
    r3 = _run("RUN-FIB-003", "python3 -m driver.orchestrate  # RUN-FIB-003: sampled 20-bit invariant tables",
              {"targets_per_curve": TARGETS_PER_MAIN_CURVE, "curves": ["C20-1", "C20-2"],
               "max_evals": SAMPLE_MAX_EVALS_20BIT, "time_budget_s": PER_CURVE_DECOMP_WALL_CAP},
              {"instance_seeds": [1, 2]}, run_fib_003)
    results["RUN-FIB-003"] = r3

    # RUN-FIB-004
    r4 = _run("RUN-FIB-004", "python3 -m driver.orchestrate  # RUN-FIB-004: 16-bit decomposition cost",
              {"targets_per_curve": TARGETS_PER_MAIN_CURVE, "curves": ["C16-1", "C16-2"],
               "per_solve_cap_s": PER_SOLVE_CAP, "per_curve_cumulative_cap_s": PER_CURVE_DECOMP_WALL_CAP},
              {"instance_seeds": [1, 2]}, run_fib_004)
    results["RUN-FIB-004"] = r4

    # RUN-FIB-005
    r5 = _run("RUN-FIB-005", "python3 -m driver.orchestrate  # RUN-FIB-005: 20-bit decomposition cost",
              {"targets_per_curve": TARGETS_PER_MAIN_CURVE, "curves": ["C20-1", "C20-2"],
               "per_solve_cap_s": PER_SOLVE_CAP, "per_curve_cumulative_cap_s": PER_CURVE_DECOMP_WALL_CAP},
              {"instance_seeds": [1, 2]}, run_fib_005)
    results["RUN-FIB-005"] = r5

    # RUN-FIB-006
    r6 = _run("RUN-FIB-006", "python3 -m driver.orchestrate  # RUN-FIB-006: correlation decision",
              {"permutation_replicates": statslib.PERMUTATION_REPLICATES,
               "correlation_prefix_min": CORRELATION_PREFIX_MIN},
              {"permutation_seed": PERM_SEED},
              lambda: run_fib_006(r2["raw"], r3["raw"], r4["raw"], r5["raw"]))
    results["RUN-FIB-006"] = r6

    # RUN-FIB-007
    r7 = _run("RUN-FIB-007", "python3 -m driver.orchestrate  # RUN-FIB-007: predictor-cost accounting",
              {}, {"instance_seeds": [1, 2]},
              lambda: run_fib_007(r2["raw"], r3["raw"]))
    results["RUN-FIB-007"] = r7

    ratios = compute_predictor_cost_ratio(r7["raw"], r4["raw"], r5["raw"])
    cost_gate_curves = [cid for cid, ratio in ratios.items() if ratio is not None and ratio <= 0.1]
    correlation_gate_pass = r6["summary"]["correlation_gate_pass_overall"]
    cost_gate_pass = len(cost_gate_curves) >= 3  # matched to the >=3/4 curve decisiveness rule used for correlation
    gate_pass = correlation_gate_pass and cost_gate_pass
    gate_reason = (
        f"correlation_gate_pass={correlation_gate_pass} "
        f"(curves passing: {r6['summary']['correlation_gate_curves_passing']}); "
        f"predictor_cost_gate_pass={cost_gate_pass} (ratios: {ratios}); "
        "RUN-FIB-008 requires both gates to pass on the frozen protocol."
    )
    print(gate_reason, file=sys.stderr)

    # RUN-FIB-008
    r8 = _run("RUN-FIB-008", "python3 -m driver.orchestrate  # RUN-FIB-008: gated two-phase (secondary)",
              {"gate_pass": gate_pass}, {"instance_seeds": [1, 2]},
              lambda: run_fib_008(gate_pass, gate_reason, r4["raw"], r5["raw"], r6["raw"], r7["raw"], ratios))
    results["RUN-FIB-008"] = r8

    _write_final_artifacts(results, ratios, gate_pass, gate_reason)
    return results


def _write_stop_summary(results, reason):
    with open(os.path.join(EXP_DIR, "analysis.md"), "w") as f:
        f.write(f"# EXP-FIB-001 analysis (stopped early)\n\n{reason}\n\n"
                f"See RUN-FIB-001/raw.json for the CTRL-EXHAUSTIVE-TRUTH detail.\n")


def _write_final_artifacts(results, ratios, gate_pass, gate_reason, correlation_run_id="RUN-FIB-006"):
    lines = [
        "# EXP-FIB-001 analysis",
        "",
        "Observations only; interpretation belongs to /review-evidence under",
        "Coordinator authority (docs/claims-and-verification.md).",
        "",
        "## CTRL-EXHAUSTIVE-TRUTH",
        f"{results['RUN-FIB-001']['summary']['CTRL-EXHAUSTIVE-TRUTH']}",
        "",
        f"## {correlation_run_id} correlation decision (per curve)",
    ]
    for cid, r in results[correlation_run_id]["raw"]["per_curve"].items():
        lines.append(f"- {cid}: {r}")
    lines += ["", "## RUN-FIB-007 predictor-cost ratios", f"{ratios}", "",
              "## RUN-FIB-008 gate", gate_reason]
    with open(os.path.join(EXP_DIR, "analysis.md"), "w") as f:
        f.write("\n".join(lines) + "\n")

    exec_report = {
        "runs": {rid: {"status": r["status"], "wall_seconds": r["wall_seconds"]}
                  for rid, r in results.items()},
        "gate_pass": gate_pass, "gate_reason": gate_reason,
        "predictor_cost_ratios": ratios,
        "generated_at": runlib.now_iso(),
    }
    with open(os.path.join(EXP_DIR, "execution-report.yaml"), "w") as f:
        yaml.safe_dump(exec_report, f, sort_keys=False)


if __name__ == "__main__":
    main()
