"""Deterministic public-input constructor screen; no scalar-truth oracle.

Plan-only enumerates public coordinate inputs and never calls prepare/evaluate.
An actual launch requires a frozen plan and the exact committed source closure.
Exit 0 means computation completed, independently of candidate success/failure.
"""
from __future__ import annotations

import argparse
from collections import Counter as Bag
import hashlib
import json
import os
from pathlib import Path
import re
import sys

from constructor import conditional_recover, prepare
from curve import Curve, Point, certify_public_parameters, point_json

ALPHA = [0, 1, 2, -2, -3]
BETA = [1, 2, 3, 4, -1, -2, -3, -4]
SOURCE_REQUIRED = {"curve.py", "constructor.py", "compute.py", "verify.py", "controller.py", "driver.py"}


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_plan(path: Path) -> tuple[dict, str]:
    document = json.loads(path.read_text())
    plan = document.get("extensions", {}).get("nongeneric_screen", document)
    if "screen_plan" in plan:
        plan = plan["screen_plan"]
    validate_plan(plan)
    return plan, sha256(path)


def validate_plan(plan: dict) -> None:
    if plan.get("fixture") != {"p": 11, "a": 1, "b": 6, "r": 13, "seed_base": [2, 7]}:
        raise ValueError("screen is restricted to the frozen mandatory F11 fixture")
    if plan.get("alpha") != ALPHA or plan.get("beta") != BETA or plan.get("scales") != list(range(1, 11)):
        raise ValueError("fixed grammar/scaling units changed")
    controls = plan.get("controls", {})
    if controls.get("invalid_anchor") != {"alpha": -1, "beta": 1}:
        raise ValueError("invalid-anchor control changed")
    if controls.get("fiber") != {"alpha": ALPHA, "beta": 0} or controls.get("wrong_root") is not True:
        raise ValueError("fiber/wrong-root controls changed")
    if controls.get("aa_replay") != {"alpha": 0, "beta": 1, "reference_id": "candidate:a0:b1"}:
        raise ValueError("A/A control changed")


def arms(plan: dict) -> list[dict]:
    p = plan["fixture"]["p"]

    def parameter_arm(kind: str, alpha: int, beta: int) -> dict:
        return {"id": f"{kind}:a{alpha}:b{beta}", "kind": kind,
                "alpha_integer": alpha, "beta_integer": beta,
                "alpha": alpha % p, "beta": beta % p}

    result = [parameter_arm("candidate", a, b) for a in plan["alpha"] for b in plan["beta"]]
    result += [parameter_arm("fiber", a, 0) for a in plan["controls"]["fiber"]["alpha"]]
    result += [parameter_arm("invalid_anchor", -1, 1)]
    result += [{"id": "wrong_root:anchored_power_root", "kind": "wrong_root",
                "alpha_integer": None, "beta_integer": None, "alpha": None, "beta": None}]
    replay = parameter_arm("aa_replay", 0, 1)
    replay["reference_id"] = "candidate:a0:b1"
    result += [replay]
    return result


def public_points(plan: dict) -> tuple[list[Point], dict]:
    """Coordinate enumeration, not scalar-orbit enumeration; separately charged."""
    fixture = plan["fixture"]
    p, a, b, r = (fixture[key] for key in ("p", "a", "b", "r"))
    certification = certify_public_parameters(p, a, b, r)
    curve = Curve(p, a, b)
    points = [None]
    for x in range(p):
        for y in range(p):
            if curve.contains((x, y)):
                points.append((x, y))
    if len(points) != r:
        raise ValueError("fixture coordinate census is not exactly the declared group")
    return points, {"parameter_certification": certification,
                    "coordinate_enumeration": curve.counter.snapshot(),
                    "point_count": len(points), "scalar_orbit_tables": 0}


def scaled_point(point: Point, u: int, p: int) -> Point:
    return None if point is None else (point[0] * u**2 % p, point[1] * u**3 % p)


def iter_groups(plan: dict, points: list[Point]):
    fixture = plan["fixture"]
    p, a, b, r = (fixture[key] for key in ("p", "a", "b", "r"))
    for u in plan["scales"]:
        model = {"p": p, "a": a * u**4 % p, "b": b * u**6 % p, "r": r}
        for public_base in points[1:]:
            base_id = f"x{public_base[0]}:y{public_base[1]}"
            base = scaled_point(public_base, u, p)
            for arm in arms(plan):
                group_id = f"u{u}:{base_id}:{arm['id']}"
                yield group_id, u, model, base, arm


def describe_plan(plan: dict) -> dict:
    points, planning_cost = public_points(plan)
    counts = Bag()
    for _, _, _, _, arm in iter_groups(plan, points):
        counts[arm["kind"]] += len(points)
    candidates = [arm for arm in arms(plan) if arm["kind"] == "candidate"]
    aliases = {}
    for arm in candidates:
        aliases.setdefault(f"{arm['alpha']},{arm['beta']}", []).append(arm["id"])
    return {"schema": "nongeneric.plan-description/v1", "measurement_started": False,
            "candidate_point_cases": counts["candidate"],
            "control_cases": sum(v for k, v in counts.items() if k != "candidate"),
            "total_cases": sum(counts.values()), "case_counts_by_kind": dict(sorted(counts.items())),
            "arm_ids": [arm["id"] for arm in arms(plan)],
            "candidate_modular_aliases": [ids for ids in aliases.values() if len(ids) > 1],
            "independent_statistical_samples": 0,
            "planning_cost": planning_cost,
            "covariance_views_are_repeated_models": True}


def validate_source_manifest(path: Path, actual: bool) -> tuple[dict, str]:
    manifest = json.loads(path.read_text())
    entries = manifest.get("files")
    if not isinstance(entries, dict) or set(entries) != SOURCE_REQUIRED:
        raise ValueError("source manifest must contain the exact six-file source closure")
    source_root = Path(__file__).resolve().parent
    for name, expected in entries.items():
        if not re.fullmatch(r"[0-9a-f]{64}", expected) or sha256(source_root / name) != expected:
            raise ValueError(f"source manifest mismatch: {name}")
    if actual and not re.fullmatch(r"[0-9a-f]{40}", manifest.get("source_revision_c", "")):
        raise ValueError("actual run requires the exact committed source revision C")
    return manifest, sha256(path)


def write_json_exclusive(path: Path, value: object) -> None:
    with path.open("xb") as output:
        output.write(canonical_json(value))


def retained_jsonl_rows(path: Path) -> int:
    """Count complete line terminators after failure; truncated bytes stay raw."""
    if not path.exists():
        return 0
    with path.open("rb") as source:
        return sum(block.count(b"\n") for block in iter(lambda: source.read(1 << 20), b""))


def runtime_facts(protocol_path: Path, manifest_path: Path | None, context_path: Path | None = None) -> dict:
    source_root = Path(__file__).resolve().parent
    paths = {name: source_root / name for name in sorted(SOURCE_REQUIRED)}
    paths["protocol"] = protocol_path
    if manifest_path is not None:
        paths["source_manifest"] = manifest_path
    if context_path is not None:
        paths["provider_context"] = context_path
    return {"resuid": list(os.getresuid()), "resgid": list(os.getresgid()),
            "supplementary_groups": os.getgroups(),
            "input_access": {name: {"exists": path.is_file(), "writable": os.access(path, os.W_OK)}
                             for name, path in paths.items()},
            "environment_values_collected": False}


def enforce_runtime_facts(facts: dict) -> None:
    if facts["resuid"] != [1000, 1000, 1000] or facts["resgid"] != [1000, 1000, 1000] or facts["supplementary_groups"]:
        raise ValueError("actual run requires UID/GID1000 and no supplementary groups")
    if any(not item["exists"] or item["writable"] for item in facts["input_access"].values()):
        raise ValueError("actual source, manifest and protocol must exist and be read-only to the worker")


def public_order_gate(model: dict, base: Point, outcomes: dict[Point, dict]) -> dict:
    """Check the public two-pulse equation on all r retained targets.

    This validation uses public points/evaluated bits only. It neither labels
    scalar indices nor supplies any retained bit to subsequent recovery calls.
    Its linear fixed-fixture cost is charged separately from the constructor.
    """
    curve = Curve(model["p"], model["a"], model["b"])
    midpoint = curve.multiply(base, (model["r"] - 1) // 2)
    negative_base = curve.negate(base)
    bits = {}
    for target, answer in outcomes.items():
        curve.counter.tick("gate_outcome_inspection")
        bits[target] = answer["bit"] if answer["status"] == "BIT" else None
    residual = []
    for target in outcomes:
        translated = curve.add(target, base)
        curve.counter.tick("gate_retained_bit_read", 2)
        before, after = bits.get(target), bits.get(translated)
        pulse = int(curve.equal(target, midpoint)) - int(curve.equal(target, negative_base))
        residual.append(None if before not in (0, 1) or after not in (0, 1) else after - before - pulse)
    coverage = len(outcomes) == model["r"] and all(bit in (0, 1) for bit in bits.values())
    curve.counter.tick("gate_retained_bit_read")
    passed = coverage and bits.get(None) == 0 and all(value == 0 for value in residual)
    reason = None if passed else "UNDEFINED_COVERAGE" if not coverage else "IDENTITY_OR_TWO_PULSE_FAILURE"
    return {"pass": passed, "not_attempted_reason": reason,
            "target_order": [point_json(target) for target in outcomes],
            "two_pulse_residual": residual, "counters": curve.counter.snapshot(),
            "scalar_truth_access": False}


def fresh_group_recovery(model: dict, base: Point, arm: dict, outcomes: dict[Point, dict]) -> dict:
    """Run actual fresh predicates only after the complete public ordering gate."""
    gate = public_order_gate(model, base, outcomes)
    counters = {"gate": gate["counters"], "fresh_setup": {}, "evaluate": Bag(), "reduction": Bag()}
    recoveries = []
    if gate["pass"]:
        # New preparation is charged once and shared across this group's 13
        # targets. No retained outcomes/table is passed into Prepared or recover.
        recovery_prepared = prepare(model, base, arm)
        counters["fresh_setup"] = recovery_prepared.setup_counts
        for target in outcomes:
            answer = conditional_recover(recovery_prepared, target)
            recoveries.append({"target": point_json(target), "result": answer})
            counters["evaluate"].update(answer["evaluate_counts"])
            counters["reduction"].update(answer["reduction_counts"])
    return {"gate": gate, "recoveries": recoveries,
            "counters": {key: dict(sorted(value.items())) for key, value in counters.items()},
            "predicate_evaluations": sum(row["result"]["predicate_evaluations"] for row in recoveries),
            "retained_bit_reads_in_recovery": 0,
            "fresh_preparations": int(gate["pass"]), "oracle_table_verifier_only": False}


def execute(plan: dict, protocol_hash: str, source_hash: str, output_dir: Path,
            provider_context: dict | None = None, observed_runtime: dict | None = None) -> dict:
    """Called only after CLI source/protocol checks; streams every target outcome."""
    if output_dir.exists():
        raise ValueError("output directory already exists; no overwrite/resume in this implementation")
    output_dir.mkdir(parents=True)
    totals = {"setup": Bag(), "evaluate": Bag()}
    counts, statuses = Bag(), Bag()
    groups = 0
    recovery_totals = {"gate": Bag(), "fresh_setup": Bag(), "evaluate": Bag(), "reduction": Bag()}
    recovery_groups_passed, recovery_predicate_calls, recovery_targets_verified = 0, 0, 0
    records_path = output_dir / "records.jsonl"
    recovery_path = output_dir / "recovery.jsonl"
    phase = "public_input_preflight"
    try:
        planned = describe_plan(plan)
        points, planning_cost = public_points(plan)
        # The public coordinate census actually ran twice: retain both costs
        # rather than silently charging the second invocation as a free table.
        planning_cost["plan_description_pass"] = planned["planning_cost"]
        with records_path.open("xb") as raw, recovery_path.open("xb") as recovery_raw:
            phase = "constructor_grid_and_recovery"
            for group_id, u, model, base, arm in iter_groups(plan, points):
                prepared = prepare(model, base, arm)
                groups += 1
                totals["setup"].update(prepared.setup_counts)
                outcomes = {}
                for target_number, public_target in enumerate(points):
                    target = scaled_point(public_target, u, model["p"])
                    answer, cost = prepared.evaluate(target)
                    outcomes[target] = answer
                    totals["evaluate"].update(cost)
                    row = {"schema": "nongeneric.case/v1", "case_id": f"{group_id}:target{target_number}",
                           "group_id": group_id, "model": model, "scale_u": u,
                           "base": point_json(base), "target": point_json(target), "arm": arm,
                           "result": answer,
                           "counters": {"setup": prepared.setup_counts, "evaluate": cost},
                           "setup_charged": target_number == 0,
                           "source_fingerprint": source_hash, "protocol_sha256": protocol_hash}
                    raw.write(canonical_json(row))
                    counts[arm["kind"]] += 1
                    statuses[f"{arm['kind']}:{answer['status']}:{answer['reason']}"] += 1
                recovery = fresh_group_recovery(model, base, arm, outcomes)
                for phase, costs in recovery["counters"].items():
                    recovery_totals[phase].update(costs)
                recovery_groups_passed += int(recovery["gate"]["pass"])
                recovery_predicate_calls += recovery["predicate_evaluations"]
                recovery_targets_verified += sum(row["result"]["status"] == "RECOVERED" for row in recovery["recoveries"])
                recovery_row = {"schema": "nongeneric.recovery-group/v1", "group_id": group_id,
                                "model": model, "scale_u": u, "base": point_json(base), "arm": arm,
                                "source_fingerprint": source_hash, "protocol_sha256": protocol_hash, **recovery}
                recovery_raw.write(canonical_json(recovery_row))
        phase = "finalization"
        if sum(counts.values()) != planned["total_cases"] or counts["candidate"] != 62400:
            raise RuntimeError("fixed case grid did not complete")
        summary = {"schema": "nongeneric.compute-summary/v1", "measurement_started": True,
                   "experiment_id": plan.get("experiment_id"), "completed": True,
                   "candidate_point_cases": counts["candidate"], "control_cases": sum(counts.values()) - counts["candidate"],
                   "total_cases": sum(counts.values()), "setup_groups": groups,
                   "case_counts_by_kind": dict(sorted(counts.items())), "status_counts": dict(sorted(statuses.items())),
                   "operation_counts": {key: dict(sorted(value.items())) for key, value in totals.items()},
                   "recovery_operation_counts": {key: dict(sorted(value.items())) for key, value in recovery_totals.items()},
                   "recovery_groups": groups, "recovery_groups_gate_passed": recovery_groups_passed,
                   "recovery_fresh_predicate_evaluations": recovery_predicate_calls,
                   "recovery_retained_bit_reads": 0, "recovery_targets_publicly_verified": recovery_targets_verified,
                   "recovery_records_sha256": sha256(recovery_path),
                   "planning_cost": planning_cost, "records_sha256": sha256(records_path),
                   "source_fingerprint": source_hash, "protocol_sha256": protocol_hash,
                   "provider_context": provider_context, "scalar_truth_access": False,
                   "observed_runtime": observed_runtime,
                   "independent_verification": "pending", "timing_qualified": False,
                   "unmetered_harness_work": ["public model/point coordinate scaling uses raw modular integer arithmetic",
                                              "Python container/control operations outside named counters",
                                              "JSON serialization, hashing, file I/O and runtime/source checks"],
                   "state_accounting": {"candidate_field_state": "constant-size source registers; no field-sized table",
                                        "scalar_state_bits": "O(log r)", "python_allocation_peak_measured": False,
                                        "harness_public_fixture_points": len(points),
                                        "gate_retained_outcomes_per_group": len(points),
                                        "recovery_group_trace_query_bound": len(points) * (plan["fixture"]["r"].bit_length() + 1),
                                        "recovery_trace_is_output_not_constructor_advice": True},
                   "cost_semantics": "setup charged once per group; row setup counters repeated as provenance, setup_charged marks its one charge"}
        write_json_exclusive(output_dir / "compute-summary.json", summary)
        write_json_exclusive(output_dir / "completion.json", {"schema": "nongeneric.completion/v1", "completed": True,
                             "records_sha256": sha256(records_path), "compute_summary_sha256": sha256(output_dir / "compute-summary.json"),
                             "recovery_records_sha256": sha256(recovery_path),
                             "total_cases": sum(counts.values()), "protocol_sha256": protocol_hash,
                             "source_fingerprint": source_hash})
        return summary
    except BaseException as error:
        write_json_exclusive(output_dir / "failure.json", {"schema": "nongeneric.failure/v1", "completed": False,
                             "error_type": type(error).__name__, "error": str(error),
                             "phase": phase, "rows_processed": sum(counts.values()),
                             "rows_retained": retained_jsonl_rows(records_path),
                             "recovery_groups_retained": retained_jsonl_rows(recovery_path), "groups_started": groups,
                             "protocol_sha256": protocol_hash, "source_fingerprint": source_hash})
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--source-manifest", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--provider-context", type=Path)
    parser.add_argument("--plan-only", action="store_true")
    args = parser.parse_args(argv)
    try:
        plan, protocol_hash = load_plan(args.protocol)
        if args.plan_only:
            observed_runtime = runtime_facts(args.protocol, args.source_manifest, args.provider_context)
            source_hash = None
            if args.provider_context:
                if args.source_manifest is None:
                    raise ValueError("provider plan probe requires --source-manifest")
                enforce_runtime_facts(observed_runtime)
                _, source_hash = validate_source_manifest(args.source_manifest, actual=True)
            elif args.source_manifest:
                _, source_hash = validate_source_manifest(args.source_manifest, actual=False)
            description = describe_plan(plan)
            description["protocol_sha256"] = protocol_hash
            description["observed_runtime"] = observed_runtime
            description["provider_runtime_requirements_enforced"] = bool(args.provider_context)
            if source_hash:
                description["source_fingerprint"] = source_hash
            print(json.dumps(description, sort_keys=True))
            return 0
        if plan.get("status") != "frozen":
            raise ValueError("actual run requires a frozen implementation plan")
        if args.source_manifest is None or args.output_dir is None:
            raise ValueError("actual run requires --source-manifest and --output-dir")
        _, source_hash = validate_source_manifest(args.source_manifest, actual=True)
        if plan.get("source_manifest_sha256") != source_hash:
            raise ValueError("frozen plan does not bind this source manifest")
        observed_runtime = runtime_facts(args.protocol, args.source_manifest, args.provider_context)
        enforce_runtime_facts(observed_runtime)
        context = None
        if args.provider_context:
            context = {"sha256": sha256(args.provider_context), "record": json.loads(args.provider_context.read_text()),
                       "independently_validated_by_compute": False}
        summary = execute(plan, protocol_hash, source_hash, args.output_dir, context, observed_runtime)
        print(json.dumps({"completed": True, "total_cases": summary["total_cases"],
                          "independent_verification": "pending"}, sort_keys=True))
        return 0
    except (ValueError, OSError, json.JSONDecodeError) as error:
        print(f"configuration/execution error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
