"""EXP-INSTR-36c8cf PHASE A driver.

PHASE A ONLY, per TASK-20260810-c98659:
  1. SR1 -- C-NULLC-REPRODUCTION.
  2. The SR3 v3 reference characterisation.

NO GEOMETRY-SPECIFIC CELL IS RUN HERE. SR2 forbids it until Stage 1 of
EXP-JINV-bd141d and EXP-VOLC-9f5571 has emitted the real geometry.

Item 2 is GATED IN THIS DRIVER on a machine check that the frozen contract
declares a numeric coverage for the "declared central interval". If it does
not, NO SR3 v3 DATA IS GENERATED AT ALL and the artifacts are written as
not_measured. Generating the per-row sampling distributions first and choosing
the coverage afterwards would fit the acceptance region to the data it gates --
which is the exact defect (a hull fitted to its own rows, floor slack 0.020397)
that the v3 redesign exists to repair.

Usage:  python3 -m harness.exp_instr_36c8cf.phase_a --run-suffix <suffix>
"""
from __future__ import annotations

import argparse
import io
import json
import os
import platform
import resource
import subprocess
import sys
import time
from contextlib import redirect_stdout

from harness import runner
from harness.exp_instr_36c8cf import refvalues, sr1

EXP_ID = "EXP-INSTR-36c8cf"
EXP_AREA = "INSTR"
TASK_ID = "TASK-20260810-c98659"
CONTRACT_VERSION = 1

# The twelve seeds declared by the frozen contract (replication.seeds). Read at
# run time from the contract rather than transcribed.
def declared_seeds() -> list[int]:
    import yaml
    with open(os.path.join(refvalues.REPO, refvalues.INSTR_SPEC), encoding="utf-8") as fh:
        spec = yaml.safe_load(fh)
    return list(spec["experiment"]["replication"]["seeds"])


def loadavg() -> dict:
    one, five, fifteen = os.getloadavg()
    return {"load_1min": round(one, 2), "load_5min": round(five, 2),
            "load_15min": round(fifteen, 2), "cpu_count": os.cpu_count(),
            "observed_at": time.strftime("%Y-%m-%dT%H:%M:%S%z")}


def inference_provenance() -> dict:
    """Agent-level inference provenance.

    The manifest's own `inference` block is harness/runner.py's static
    deterministic-execution block; this is the block for the agent that drove
    the run, recorded because AUTORESEARCH_POLICY is unset in this harness
    (D4 of DEC-20260810-d70ece) so the adapter-resolved environment was never
    applied.
    """
    resolved = None
    try:
        resolved = subprocess.run(
            [sys.executable, "-m", "orchestration.adapter", "resolve",
             "--role", "executor"],
            cwd=refvalues.REPO, capture_output=True, text=True,
            env={**os.environ, "PYTHONPATH": refvalues.REPO}).stdout.strip()
    except Exception as exc:                                   # pragma: no cover
        resolved = f"adapter probe failed: {type(exc).__name__}: {exc}"
    return {
        "requested_policy": "executor-implementation",
        "adapter_resolution_for_role_executor": resolved,
        "resolved_model_id_that_actually_answered": "claude-opus-5",
        "fallback_used": True,
        "fallback_reason": (
            "AUTORESEARCH_POLICY is unset in this Claude Code harness, so the "
            "adapter-resolved environment was not applied and the session model "
            "answered instead of the policy's resolved model. KNOWN AND ALREADY "
            "RECORDED as defect D4 of DEC-20260810-d70ece; the corrective is at "
            "harness level and is not this task's to make. Recorded, never "
            "silently substituted (AGENTS.md rule 11)."),
        "autoresearch_policy_env": os.environ.get("AUTORESEARCH_POLICY"),
        "autoresearch_backend_env": os.environ.get("AUTORESEARCH_BACKEND"),
        "model_verified": False,
        "model_verified_reason": "no adapter probe receipt; the env var is unset",
        "manifest_inference_block_note": (
            "harness/runner.py writes a static `inference` block for "
            "deterministic harness execution and is READ-ONLY to this task; the "
            "agent-level block is this file."),
    }


NOT_MEASURED_SR3 = (
    "NOT MEASURED, AND NO DATA WAS GENERATED. The frozen contract requires the "
    "SR3 v3 acceptance region to be 'a declared central interval' of the "
    "reference run's own empirical sampling distribution, but declares NO "
    "NUMERIC COVERAGE for that interval anywhere in specification.yaml, and no "
    "other committed record (H-INSTR-444c7b, DEC-20260810-a4bec4, "
    "DEC-20260809-de11f9, EXP-ICINV-4d33aa specification.yaml or amendments "
    "v1/v2) supplies one. The coverage is a frozen pre-registered parameter: "
    "choosing it AFTER seeing the per-row sampling distributions would fit the "
    "acceptance region to the data it gates, which is exactly the defect the v3 "
    "redesign exists to repair. The executor does not author amendments "
    "(handoff constraint) and does not invent a frozen parameter. Requires a "
    "Coordinator protocol_amendment declaring the coverage BEFORE the data is "
    "generated (contract constraint: filed before the affected data is "
    "generated).")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-suffix", required=True)
    args = ap.parse_args()

    started = time.time()
    load_before = loadavg()
    buf = io.StringIO()
    deviations: list[str] = []
    spec_errors: list[dict] = []

    with redirect_stdout(buf):
        print(f"=== {EXP_ID} PHASE A  ({TASK_ID}, contract v{CONTRACT_VERSION}) ===")
        print(f"host: {platform.platform()}  cpu_count={os.cpu_count()}")
        print(f"load average BEFORE: {load_before}")
        print("single-threaded, sequential; no internal parallelism")

        # ---------- baseline provenance, read at run time ----------
        print("\n--- reading every reference value from its committed record ---")
        published = refvalues.nullc_published_profile()
        bounds = refvalues.detection_bound_table()
        band = refvalues.superseded_band_slacks()
        data = refvalues.p4001_rate_m3_by_class()
        specfields = refvalues.instr_spec_declared_fields()
        seeds = declared_seeds()
        print(f"published NULL-C profile rows: {len(published['rows'])} "
              f"from {published['source_path']} ({published['source_sha256'][:12]}...)")
        print(f"  repetitions_per_cell recorded: {published['repetitions_per_cell']}")
        print(f"  planting construction recorded in that record: "
              f"{published['planting_construction_recorded']}")
        print(f"  permutation seeds recorded in that record: "
              f"{published['permutation_seeds_recorded']}")
        print(f"p=4001 rate_m3 sources agree exactly: {data['sources_agree_exactly']}")
        print(f"  class sizes: {data['class_sizes']}")
        print(f"superseded band [{band['band_low']}, {band['band_high']}] "
              f"floor slack {band['floor_slack']} ceiling slack {band['ceiling_slack']}")
        print(f"declared seeds ({len(seeds)}): {seeds}")

        if not data["sources_agree_exactly"]:
            raise RuntimeError("the two committed p = 4001 runs disagree on rate_m3")

        # ---------- SR1 ----------
        print("\n--- SR1: C-NULLC-REPRODUCTION ---")
        deltas = [r["delta"] for r in published["rows"]]
        print(f"deltas read from the record: {deltas}")
        t0 = time.time()
        sr1_out = sr1.run(data["groups"], deltas, seeds, published["rows"])
        sr1_out["wall_seconds"] = round(time.time() - t0, 3)
        sr1_out["published"] = published
        z = sr1_out["delta_zero_cell"]
        print(f"delta = 0 (construction-free): median p = {z['median_p']:.4f} "
              f"power = {z['power_at_0_05']:.2f}  "
              f"(published median p = {published['rows'][0]['median_p_published']}, "
              f"power = {published['rows'][0]['power_at_0_05_published']})")
        print(f"pooled mean of rate_m3 = {sr1_out['pooled_mean_of_rate_m3']:.6f}")
        for c in sr1_out["pct_of_mean_check"]:
            print(f"  delta {c['delta']:.3f}: measured {c['pct_of_mean_measured']:.2f}% "
                  f"of mean vs published {c['pct_of_mean_published']}%")
        for name, v in sr1_out["constructions"].items():
            row = "  ".join(
                f"d={r['delta']:.3f} med={r['measured']['median_p']:.4f} "
                f"pw={r['measured']['power_at_0_05']:.2f}" for r in v["rows"])
            print(f"  {name:<20} {row}   rows_matching={v['rows_matching']}/{v['rows_total']}")
        print(f"delta-zero row reproduced: {sr1_out['delta_zero_row_reproduced']}")
        print(f"constructions reproducing the FULL published profile: "
              f"{sr1_out['constructions_reproducing_published_profile']}")
        print(f"SR1 reproduced: {sr1_out['sr1_reproduced']}")
        print(f"SR1 wall seconds: {sr1_out['wall_seconds']}")

        if not sr1_out["sr1_reproduced"]:
            spec_errors.append({
                "field": ("EXP-INSTR-36c8cf controls[0] C-NULLC-REPRODUCTION -- "
                          "the planting construction and the permutation seed set "
                          "behind the published delta > 0 rows"),
                "classification": "specification_error",
                "why": (
                    "SR1 requires reproducing a published power profile whose "
                    "GENERATING CONSTRUCTION is recorded nowhere. red_team_notes.md "
                    "section 5 and red_team_report.yaml objection O3 state the "
                    "profile; neither states how the between-class mean shift was "
                    "applied, nor which permutation seeds gave the 12 repetitions. "
                    "The contract does not supply either. The delta = 0 row, which "
                    "is construction-free, IS reproduced; the delta > 0 rows are "
                    "not reproducible from any committed record."),
                "what_this_is_NOT": (
                    "This is NOT evidence that the control harness exercises a "
                    "different statistic. The committed permutation_null is called "
                    "unmodified on the committed data; the construction-free "
                    "delta = 0 row and the published 'as % of mean' column are both "
                    "reproduced, which is what binds this harness to the same "
                    "statistic and the same data. It is also NOT a finding about "
                    "NULL-C, about H-ICINV-6c7920, or about any curve."),
                "resolution": (
                    "Coordinator protocol_amendment declaring the SR1 planting "
                    "construction and seed set explicitly, filed before the "
                    "affected data is generated."),
            })

        # ---------- SR3 v3 gate: freeze check BEFORE any data is generated ----------
        print("\n--- SR3 v3: coverage freeze check (BEFORE any data is generated) ---")
        print(f"numeric interval coverage declared in the frozen contract: "
              f"{specfields['numeric_interval_coverage_declared']}")
        print(f"  coverage-bearing phrases found WITHOUT a number: "
              f"{specfields['phrases_found_without_a_number']}")
        if not specfields["numeric_interval_coverage_declared"]:
            print("STOP. No SR3 v3 data is generated. " + NOT_MEASURED_SR3)
            spec_errors.append({
                "field": ("EXP-INSTR-36c8cf inputs.sr3_amendment_v3.change / "
                          "characterisation_procedure -- the numeric COVERAGE of "
                          "the 'declared central interval'"),
                "classification": "specification_error",
                "why": NOT_MEASURED_SR3,
                "resolution": (
                    "Coordinator protocol_amendment declaring the coverage "
                    "(and, for the Phase B cells, the nominal level, the density "
                    "rows and the planted-size ladders) BEFORE the data is "
                    "generated."),
            })
        else:                                                  # pragma: no cover
            raise RuntimeError(
                "a numeric coverage was detected in the contract; this driver "
                "must be extended to run the characterisation at that coverage "
                "rather than stopping")

        load_after = loadavg()
        print(f"\nload average AFTER: {load_after}")

    finished = time.time()
    stdout_text = buf.getvalue()
    print(stdout_text)

    ru = resource.getrusage(resource.RUSAGE_SELF)
    metrics = {
        "phase": "A",
        "sr1_delta_zero_median_p": sr1_out["delta_zero_cell"]["median_p"],
        "sr1_delta_zero_power_at_0_05": sr1_out["delta_zero_cell"]["power_at_0_05"],
        "sr1_delta_zero_row_reproduced": sr1_out["delta_zero_row_reproduced"],
        "sr1_constructions_reproducing_published_profile":
            sr1_out["constructions_reproducing_published_profile"],
        "sr1_reproduced": sr1_out["sr1_reproduced"],
        "sr3v3_characterisation_status": "not_measured",
        "specification_errors": len(spec_errors),
        "wall_seconds": round(finished - started, 3),
        "cpu_seconds": round(ru.ru_utime + ru.ru_stime, 3),
    }

    result = runner.RunResult(
        run_suffix=args.run_suffix,
        curve_id="TOY-P12-p4001-class-set (4 committed isogeny classes, "
                 "read from EXP-ICINV-180a0d)",
        seed=seeds[0],
        parameters={
            "task_id": TASK_ID,
            "contract_version": CONTRACT_VERSION,
            "phase": "A",
            "seeds": seeds,
            "deltas": [r["delta"] for r in sr1_out["published"]["rows"]],
            "constructions": list(sr1_out["constructions"].keys()),
            "statistic": "harness.exp_icinv.permutation_null (NULL-C), unmodified",
            "parallelism": "none (single-threaded, sequential)",
        },
        metrics=metrics,
        certificate={"kind": "none",
                     "statement": {"why": "pure measurement run: no discrete-log "
                                          "solve and no factor-base relation is "
                                          "claimed anywhere in this run"}},
        valid=False,
        invalid_reason=(
            "specification_error: the frozen contract declares no numeric "
            "coverage for the SR3 v3 central interval, and the SR1 published "
            "profile's planting construction and seed set are recorded in no "
            "committed record. Both are frozen pre-registered parameters the "
            "executor may not invent. NO SR3 v3 DATA WAS GENERATED, "
            "deliberately. This status is NOT negative evidence about any "
            "instrument and NOT a passed control (AGENTS.md rule 5)."),
        stdout=stdout_text,
        stderr="",
        raw={
            "sr1": sr1_out,
            "specification_errors": spec_errors,
            "deviations": deviations,
            "host": {"load_before": load_before, "load_after": load_after,
                     "platform": platform.platform(), "cpu_count": os.cpu_count()},
            "inference_provenance": inference_provenance(),
            "detection_bound_table_recorded_for_phase_b": bounds,
            "superseded_band": band,
        },
    )

    command = (f"PYTHONPATH=. python3 -m harness.exp_instr_36c8cf.phase_a "
               f"--run-suffix {args.run_suffix}")
    run_id = runner.write_run(EXP_ID, EXP_AREA, result, status="completed_invalid",
                              command=command, started=started, finished=finished)
    run_dir = os.path.join(refvalues.REPO, "experiments", EXP_ID, "runs", run_id)

    def w(name, obj):
        with open(os.path.join(run_dir, name), "w", encoding="utf-8") as fh:
            json.dump(obj, fh, indent=2, sort_keys=True, default=str)

    w("nullc-reproduction.json", sr1_out)
    w("baseline-provenance.json", {
        "note": ("Every reference value used by this run was READ FROM ITS "
                 "COMMITTED RECORD AT RUN TIME and is bound by the sha256 below. "
                 "No reference value is transcribed into source at any precision "
                 "(EXP-ICINV-4d33aa amendment v2 change A4, CORR-20260807-a24675)."),
        "nullc_published_profile": sr1_out["published"],
        "detection_bound_table": bounds,
        "superseded_band_and_hull_slacks": band,
        "p4001_rate_m3_sources": data["sources"],
        "p4001_sources_agree_exactly": data["sources_agree_exactly"],
        "frozen_contract": {"path": specfields["source_path"],
                            "sha256": specfields["source_sha256"],
                            "version": CONTRACT_VERSION},
        "sr3v3_reference_run_ids": {
            "status": "NOT NAMED BY THIS RUN",
            "why": ("naming the reference run ids is part of the SR3 v3 "
                    "characterisation, which was not run: no coverage is "
                    "declared. The contract requires the ids to be named in the "
                    "run record that performs the comparison; this run performs "
                    "none."),
        },
        "inference_provenance": inference_provenance(),
    })
    for name in ("sr3v3-reference-sampling.json", "sr3v3-interval-stability.json",
                 "sr3v3-self-consistency.json"):
        w(name, {"status": "not_measured", "phase": "A",
                 "data_generated": False, "reason": NOT_MEASURED_SR3,
                 "blocks": ["the redesigned SR3 gate of EXP-ICINV-4d33aa is not "
                            "evaluable, so no successor run of EXP-ICINV-4d33aa "
                            "may be dispatched",
                            "GOAL-ENDO-001 criterion C4 is not discharged for the "
                            "SR3 v3 gate"],
                 "no_widening_rule": ("SR4 is not reached: no interval exists to "
                                      "widen, and none was constructed.")})
    phase_b = {
        "status": "not_measured", "phase": "B",
        "reason": ("PHASE B. SR2 forbids running any geometry-specific control "
                   "before Stage 1 of EXP-JINV-bd141d and EXP-VOLC-9f5571 has "
                   "emitted the real geometry. Phase B was not dispatched and no "
                   "geometry-specific cell was run."),
        "blocks": ["every arm verdict of EXP-JINV-bd141d",
                   "every arm verdict of EXP-VOLC-9f5571"],
    }
    for name in ("geometry-inputs.json", "detection-floors.json",
                 "false-positive-rates.json", "pseudo-crater-control.json",
                 "arbitrary-halves-control.json", "label-permutation-control.json",
                 "nuisance-direction.json",
                 "nullc-matched-order-recharacterisation.json"):
        w(name, phase_b)
    w("cell-coverage.json", {
        "phase_a_cells": [
            {"cell": "SR1 / C-NULLC-REPRODUCTION / NULL-C / committed p=4001 "
                     "4-class geometry / delta = 0 (construction-free)",
             "status": "measured",
             "measured": {"median_p": sr1_out["delta_zero_cell"]["median_p"],
                          "power_at_0_05": sr1_out["delta_zero_cell"]["power_at_0_05"],
                          "seeds": seeds}},
            {"cell": "SR1 / C-NULLC-REPRODUCTION / NULL-C / committed p=4001 "
                     "4-class geometry / delta > 0 rows",
             "status": "not_reproducible_from_committed_records",
             "blocks": ["the SR1 gate cannot be discharged as written, so under "
                        "the contract's own stopping rule nothing downstream of "
                        "it is characterised"],
             "reason": spec_errors[0]["why"] if spec_errors else None},
            {"cell": "SR3 v3 reference characterisation / variance-ratio "
                     "statistic / reference-run geometry / every density row",
             "status": "not_measured", "reason": NOT_MEASURED_SR3,
             "blocks": ["the redesigned SR3 gate of EXP-ICINV-4d33aa is not "
                        "evaluable; no successor run may be dispatched"]},
        ],
        "phase_b_cells": {
            "status": "not_enumerable_yet",
            "reason": ("the (statistic, geometry, density row) cells cannot even "
                       "be ENUMERATED until Stage 1 of EXP-JINV-bd141d and "
                       "EXP-VOLC-9f5571 emits the real class census, the real "
                       "per-level vertex counts and the real Velu volcano. "
                       "Enumerating them from the design document would be "
                       "reporting a control at an assumed geometry, which is an "
                       "invalidation rule of this contract."),
            "blocks": ["every arm verdict of EXP-JINV-bd141d",
                       "every arm verdict of EXP-VOLC-9f5571"],
        },
        "an_unmeasured_control_is_not_a_passed_control": True,
    })
    w("inference-provenance.json", inference_provenance())
    print(f"\nrun record: {run_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
