"""Apply the Coordinator's exact-metric confound amendment to a fresh preview.

Run prepare_packet.py first. This changes prospective approval bytes only and
never invokes a solver or edits the archived review-required specification.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ORIGINAL_SPEC_SHA256 = "aa13733b0d711bbe5ba3f9dcf538df99b16f2c5056014464b9756a365fb04751"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def main() -> None:
    spec_path = HERE / "specification.yaml"
    assert digest(spec_path) == ORIGINAL_SPEC_SHA256, "regenerate the original preview before amendment"
    doc = yaml.safe_load(spec_path.read_text())
    exp = doc["experiment"]
    assert exp["id"] == "EXP-ICPERF-515ae3" and exp["status"] == "approved"
    exp["metrics"] = {
        "primary": [
            "C-custody: exact raw-member hashes, schedule coverage and one explicit classification per fixed cell.",
            "C-coset, C-random and C-smallx: independent exact polynomial-root, base-member, sign, lift and full-target-point acceptance for every claimed certificate.",
            "Exact monitor-null fault detection and fail-closed classification before scientific calls.",
        ],
        "secondary": [
            "Descriptive per-cell wall and CPU seconds, sampled process-tree RSS, scratch peak, minimum free bytes and stop-cap or censor state; no runtime comparison is decisive.",
            "Phase trace, reported Groebner degree or matrix dimensions when instrumented; absent values remain null.",
            "Equation and variable counts, quotient lower bound, root count and false-root categories.",
            "Host and Sage identity, command and source hashes, and raw byte hashes.",
        ],
    }
    exp["variable_ledger"] = {
        "independent": [{"name": "arm_bundle", "levels": ["coset-m2", "random-m2", "small_x-m2"]}],
        "factors": [
            {"name": "field_and_subgroup", "treatment": "fixed", "value": "p=9223372021248595841; r=9223372018953067627", "how": "One archived curve and subgroup for all fixed inputs."},
            {"name": "base_size_and_arity", "treatment": "fixed", "value": "B=475; m=2", "how": "Bound in each archived request."},
            {"name": "factor_base", "treatment": "measured", "how": "Different archived base per named arm; its exact identity is recorded, with no isolated base-effect inference."},
            {"name": "target", "treatment": "measured", "how": "Separately planted target per arm is archived and checked; no common-target comparison."},
            {"name": "encoder", "treatment": "measured", "how": "Archived coset quadratic lift and direct random/small-x encoders co-vary with arm."},
            {"name": "equation_shape", "treatment": "measured", "how": "Equation/variable counts and request hashes are recorded per arm; shape co-varies with encoder."},
            {"name": "source_backend_and_order", "treatment": "fixed", "value": "SHA-bound source, backend, flags, term order and model cap 64", "how": "One frozen source/input manifest and execution plan governs all calls."},
            {"name": "schedule_and_caps", "treatment": "fixed", "value": "monitor-null then coset/random/small_x; one worker; 600 s/cell; 2100 s total; 8 GiB guards", "how": "Frozen order and supervisor limits apply to every scheduled cell."},
            {"name": "host_load", "treatment": "measured", "how": "Recorded as descriptive telemetry; it cannot change exact acceptance or custody predicates."},
        ],
        "comparisons": [
            {"id": "C-custody", "arms": ["run_archive"], "differs_in": [], "design": "absolute"},
            {"id": "C-coset", "arms": ["coset-m2"], "differs_in": [], "design": "absolute"},
            {"id": "C-random", "arms": ["random-m2"], "differs_in": [], "design": "absolute"},
            {"id": "C-smallx", "arms": ["small_x-m2"], "differs_in": [], "design": "absolute"},
            {"id": "C-cross-arm", "arms": ["coset-m2", "random-m2", "small_x-m2"], "differs_in": ["factor_base", "target", "encoder", "equation_shape"], "design": "confounded", "reason": "Separately planted targets and bases, with quadratic-lift versus direct encodings and different equation shapes; descriptive only."},
        ],
        "aa_not_applicable": "Decisive C-custody and C-cell predicates are exact byte/hash, finite-field and full-point checks. No timing, RSS, cap, yield or cross-arm comparison supports or refutes a hypothesis in this diagnostic; noisy telemetry is secondary and censored at its guard.",
        "crosses_map": False,
    }
    prior = "experiments/EXP-ICPERF-891f7f/runs/RUN-ICPERF-7ed866"
    source = "research/icperf_prime63_m2_diagnostic_integration_20261018/diagnostic_packet.json"
    exp["prediction_provenance"] = [
        {"prediction": "P-monitor", "first_recorded_in": source, "written_at": "2026-10-18", "data_seen": [{"path": prior, "measured": "Earlier monitor error and raw-custody classifications."}, {"path": source, "measured": "Synthetic monitor-null and checker validation controls."}], "sample_status": "in_sample", "overlap": "Close monitor and custody instrument; this is calibration only."},
        {"prediction": "P-planted", "first_recorded_in": source, "written_at": "2026-10-18", "data_seen": [{"path": prior, "measured": "Same m=2 planted arm inputs under earlier 300-second calls, with censors."}, {"path": source, "measured": "Integration validation of archived planted witnesses and checker."}], "sample_status": "in_sample", "overlap": "Same m=2 planted cells and close source; this is calibration only."},
    ]
    exp["decision_impact"]["on_negative"] = (
        "An at-cap or otherwise missing certificate remains censored or unresolved and does not weaken H-ICPERF-05021b. "
        "A wrong accepted root or contradiction of a checked planted witness invalidates the instrument and requires replay.")
    exp["success_criterion"] = (
        "C-custody and exact monitor-null fail-closed checks pass, and every accepted certificate in C-coset, "
        "C-random and C-smallx passes independent full-point replay. Any verified certificate establishes bounded "
        "interface feasibility for only its exact input; no comparative timing or factor-base inference follows.")
    exp["falsification_criterion"] = (
        "C-coset, C-random or C-smallx finds an accepted root failing independent exact checks, or a claimed "
        "no-solution response contradicts an archived checked planted witness; this invalidates the instrument. "
        "At-cap failure is censored, not falsification of the method.")
    exp["interpretation_limits"].append(
        "C-cross-arm is confounded; wall/RSS/cap telemetry has no A/A noise floor and supports no comparison or negative feasibility inference.")
    spec_path.write_text(yaml.safe_dump(doc, sort_keys=False, width=110))

    plan_path = HERE / "trial-plan.json"
    plan = json.loads(plan_path.read_text())
    plan["specification_sha256"] = digest(spec_path)
    save_json(plan_path, plan)
    plan_sha = digest(plan_path)
    handoff_path = HERE / "handoff.yaml"
    handoff = yaml.safe_load(handoff_path.read_text())
    handoff["handoff"]["execution"]["trial_plan_sha256"] = plan_sha
    handoff_path.write_text(yaml.safe_dump(handoff, sort_keys=False, width=110))
    queue_path = HERE / "dispatch_queue.json"
    queue = json.loads(queue_path.read_text())
    for task in queue["tasks"]:
        if task["id"] == "TASK-20261019-904fbf":
            task["handoff"]["execution"]["trial_plan_sha256"] = plan_sha
    save_json(queue_path, queue)
    save_json(HERE / "prospective-hashes.json", {
        "specification": digest(spec_path), "trial_plan": plan_sha,
        "queue": digest(queue_path), "handoff": digest(handoff_path),
    })


if __name__ == "__main__":
    main()
