"""Fixed-circuit, blinded public ECDLP attempts on a prospectively drawn cohort.

Plan-only does not draw a cohort or evaluate any candidate. Actual generation
and attempts happen once, inside the admitted isolated worker. Completion is an
operational observation and is independent of candidate success probability.
"""
from __future__ import annotations

import argparse
from collections import Counter as Bag
import hashlib
import json
import math
import os
from pathlib import Path
import re
import sys

from constructor import prepare
from curve import Counter, Curve, certify_public_parameters, point_from_json, point_json

SCHEMA = "classical.ecdlp.transfer-study"
EXPERIMENT = "EXP-ECDLP-8dc19d"
RUN = "RUN-ECDLP-994f70"
SOURCE_REQUIRED = {"curve.py", "constructor.py", "cohort.py", "compute.py", "verify.py", "controller.py", "driver.py"}
MULTIPLIERS = (1, 2, 3, 5)
CIRCUITS = ((1, -4), (-2, -1))
REPLICATES = 4


def arm_specs():
    result = []
    for number, (alpha, beta) in enumerate(CIRCUITS, 1):
        for a in MULTIPLIERS:
            result.append({"id": f"circuit{number}.a{a}", "kind": "candidate",
                           "alpha": alpha, "beta": beta, "base_multiplier": a})
    result += [{"id": "uniform_candidate", "kind": "uniform_candidate", "base_multiplier": 1},
               {"id": "bsgs_reference", "kind": "bsgs_reference", "base_multiplier": 1},
               {"id": "aa_circuit1_a1", "kind": "aa_replay", "alpha": 1, "beta": -4,
                "base_multiplier": 1, "reference_arm_id": "circuit1.a1"}]
    return result


def canonical_json(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def sha_file(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def write_json(path, value):
    with Path(path).open("xb") as stream:
        stream.write(canonical_json(value))


def add_counts(destination, source):
    for name, value in source.items():
        destination.tick(name, value)


def sum_counts(records):
    total = Counter()
    for record in records:
        add_counts(total, record)
    return total.snapshot()


def uniform_below(nonce_hex, role, draw_id, bound, counter=None):
    """Unbiased reduction of domain-separated SHA-256 public PRG draws."""
    if type(bound) is not int or not 1 <= bound <= (1 << 256):
        raise ValueError("positive at-most-256-bit sampling bound required")
    if not re.fullmatch(r"[0-9a-f]{64}", nonce_hex):
        raise ValueError("256-bit public cohort nonce required")
    prefix = bytes.fromhex(nonce_hex) + b"\x00transfer-study/v1/" + role.encode() + b"\x00" + draw_id.encode()
    threshold = ((1 << 256) // bound) * bound
    rejection_counter = 0
    while True:
        digest = hashlib.sha256(prefix + rejection_counter.to_bytes(8, "big")).digest()
        if counter is not None:
            counter.tick("rng_hash256_call")
        value = int.from_bytes(digest, "big")
        if value < threshold:
            sampled = value % bound
            if counter is not None:
                counter.tick("rng_modular_reduction")
            return sampled, {"role": role, "draw_id": draw_id, "bound": bound,
                             "rejection_counter": rejection_counter,
                             "digest_hex": digest.hex(), "value": sampled}
        if counter is not None:
            counter.tick("rng_rejected_digest")
        rejection_counter += 1


def scalar_inverse(value, modulus, counter):
    counter.tick("order_inverse_call")
    counter.tick("order_reduce")
    old_r, rem, old_t, coeff = modulus, value % modulus, 0, 1
    while rem:
        counter.tick("order_euclid_iteration")
        quotient = old_r // rem
        old_r, rem = rem, old_r - quotient * rem
        old_t, coeff = coeff, old_t - quotient * coeff
    if old_r != 1:
        raise ValueError("known target multiplier is not invertible")
    counter.tick("order_reduce")
    return old_t % modulus


def ungated_attempt(prepared, original_base, original_target, base_multiplier,
                     target_multiplier, include_query_counters=False):
    """Fixed L fresh calls; no all-target gate or scalar label is consulted."""
    model, r = prepared.model, prepared.model["r"]
    blinding = Curve(model["p"], model["a"], model["b"])
    if not blinding.contains(original_target) or original_target is None:
        raise ValueError("primary target must be a nonidentity public point")
    transformed_target = blinding.multiply(original_target, target_multiplier)
    curve = Curve(model["p"], model["a"], model["b"])
    length = r.bit_length() + 1
    value, current, fully_defined = 0, transformed_target, True
    evaluate, trace, reasons = Counter(), [], []
    for index in range(length):
        answer, counts = prepared.evaluate(current)
        add_counts(evaluate, counts)
        entry = {"index": index, "target": point_json(current), "answer": answer}
        if include_query_counters:
            entry["counters"] = counts
        trace.append(entry)
        curve.counter.tick("recovery_scalar_digit_update")
        if answer["status"] != "BIT":
            fully_defined = False
            reasons.append(answer["reason"])
        value = 2 * value + (answer["bit"] if answer["status"] == "BIT" else 0)
        if index + 1 < length:
            current = curve.add(current, current)
    denominator = 1 << length
    curve.counter.tick("recovery_scalar_interval_round")
    lower = r * value
    upper = r * (value + 1)
    candidate_prime = (lower + denominator - 1) // denominator if fully_defined else None
    nonempty = bool(fully_defined and candidate_prime < r and denominator * candidate_prime < upper)
    conversion = Counter()
    inverse_b = scalar_inverse(target_multiplier, r, conversion)
    candidate = None
    transformed_check = original_check = None
    if nonempty:
        conversion.tick("order_mul", 2)
        conversion.tick("order_reduce", 2)
        candidate = (base_multiplier * inverse_b % r) * candidate_prime % r
        transformed_check = curve.equal(curve.multiply(prepared.base, candidate_prime), transformed_target)
        original_check = curve.equal(curve.multiply(original_base, candidate), original_target)
    recovered = bool(nonempty and transformed_check and original_check)
    status = "RECOVERED" if recovered else "UNDEFINED" if not fully_defined else "EMPTY_INTERVAL" if not nonempty else "REJECTED_FINAL_VERIFICATION"
    reason = None if recovered else ",".join(sorted(set(reasons))) if not fully_defined else "EMPTY_BINARY_INTERVAL" if not nonempty else "FINAL_VERIFICATION_FAILED"
    return transformed_target, {
        "status": status, "reason": reason, "L": length,
        "candidate_scalar_prime": candidate_prime, "candidate_scalar": candidate,
        "scalar_prime": candidate_prime if recovered else None,
        "scalar": candidate if recovered else None,
        "target_multiplier_inverse": inverse_b,
        "interval": {"value": value if fully_defined else None, "denominator": denominator,
                     "lower_numerator": lower if fully_defined else None,
                     "upper_numerator": upper if fully_defined else None, "nonempty": nonempty},
        "predicate_evaluations": length, "retained_bit_reads": 0, "predicate_trace": trace,
        "counts": {"blinding": blinding.counter.snapshot(), "evaluate": evaluate.snapshot(),
                   "reduction": curve.counter.snapshot(), "conversion": conversion.snapshot()},
        "public_checks": {"transformed": transformed_check, "original": original_check}}


class BSGS:
    """Working additive Shanks reference; public baby table is baseline-only."""
    def __init__(self, model, base):
        self.model, self.base = dict(model), base
        curve = Curve(model["p"], model["a"], model["b"])
        self.m = math.isqrt(model["r"] - 1) + 1
        self.babies, point = {}, None
        for j in range(self.m):
            curve.counter.tick("bsgs_baby_insert")
            self.babies.setdefault(point, j)
            point = curve.add(point, base)
        self.stride = curve.negate(point)
        self.setup_counts = curve.counter.snapshot()

    def recover(self, target):
        curve = Curve(self.model["p"], self.model["a"], self.model["b"])
        if target is None or not curve.contains(target):
            raise ValueError("primary BSGS target must be nonidentity and on curve")
        gamma, found = target, None
        giant_visits = 0
        for i in range(self.m):
            giant_visits += 1
            curve.counter.tick("bsgs_giant_lookup")
            if gamma in self.babies:
                curve.counter.tick("bsgs_scalar_combination")
                candidate = i * self.m + self.babies[gamma]
                if candidate < self.model["r"] and curve.equal(curve.multiply(self.base, candidate), target):
                    found = candidate
                    break
            if i + 1 < self.m:
                gamma = curve.add(gamma, self.stride)
        return {"status": "RECOVERED" if found is not None else "BASELINE_FAILED",
                "reason": None if found is not None else "BSGS_EXHAUSTED",
                "candidate_scalar_prime": found, "candidate_scalar": found,
                "scalar_prime": found, "scalar": found, "L": None,
                "predicate_evaluations": 0, "retained_bit_reads": 0,
                "predicate_trace": [], "interval": None,
                "counts": {"online": curve.counter.snapshot()},
                "public_checks": {"transformed": found is not None, "original": found is not None},
                "giant_visits": giant_visits}


def uniform_attempt(model, base, target, nonce, draw_id):
    counter = Counter()
    candidate, sampling = uniform_below(nonce, "uniform-candidate", draw_id, model["r"] - 1, counter)
    candidate += 1
    curve = Curve(model["p"], model["a"], model["b"])
    verified = curve.equal(curve.multiply(base, candidate), target)
    return {"status": "RECOVERED" if verified else "REJECTED_FINAL_VERIFICATION",
            "reason": None if verified else "FINAL_VERIFICATION_FAILED", "L": None,
            "candidate_scalar_prime": candidate, "candidate_scalar": candidate,
            "scalar_prime": candidate if verified else None, "scalar": candidate if verified else None,
            "predicate_evaluations": 0, "retained_bit_reads": 0,
            "predicate_trace": [], "interval": None,
            "counts": {"rng": counter.snapshot(), "online": curve.counter.snapshot()},
            "public_checks": {"transformed": verified, "original": verified}}, sampling


def run_legacy_controls():
    """Frozen known-fixture regression; actual-only, before any fresh draw."""
    model = {"p": 11, "a": 1, "b": 6, "r": 13}
    original_base, target = (2, 7), (7, 2)
    transform = Curve(11, 1, 6)
    base = transform.multiply(original_base, 5)
    prepared = prepare(model, base, {"kind": "candidate", "alpha": 1, "beta": -4 % 11})
    transformed_target, candidate = ungated_attempt(prepared, original_base, target, 5, 1)
    reference = BSGS(model, original_base)
    baseline = reference.recover(target)
    negative = Curve(11, 1, 6)
    wrong_scalar_rejected = not negative.equal(negative.multiply(original_base, 8), target)
    passed = (candidate["status"] == "RECOVERED" and candidate["scalar_prime"] == 4
              and candidate["scalar"] == 7 and candidate["predicate_evaluations"] == 5
              and baseline["status"] == "RECOVERED" and baseline["scalar"] == 7
              and wrong_scalar_rejected)
    return {"schema": SCHEMA + ".legacy-control/v1", "passed": passed,
            "fresh_cohort_generated": False, "included_in_primary_attempt_counts": False,
            "model": model, "original_base": point_json(original_base), "target": point_json(target),
            "base_multiplier": 5, "target_multiplier": 1,
            "transformed_base": point_json(base), "transformed_target": point_json(transformed_target),
            "candidate_result": candidate, "bsgs_result": baseline,
            "wrong_scalar": 8, "wrong_scalar_rejected": wrong_scalar_rejected,
            "separate_setup_counts": {"base_transform": transform.counter.snapshot(),
                "constructor_setup": prepared.setup_counts, "bsgs_setup": reference.setup_counts},
            "negative_equation_counts": negative.counter.snapshot()}


def validate_plan(plan, actual=False):
    if plan.get("schema") != SCHEMA + ".compute-plan/v1" or plan.get("experiment_id") != EXPERIMENT or plan.get("run_id") != RUN:
        raise ValueError("wrong fixed transfer-study plan")
    if actual and plan.get("status") != "frozen":
        raise ValueError("actual invocation requires the frozen compute plan")
    expected = plan.get("expected", {})
    required = {"candidate_attempts_planned", "baseline_attempts_planned", "total_attempts_planned", "fixture_count_planned", "arm_ids"}
    if set(expected) != required or expected["arm_ids"] != [a["id"] for a in arm_specs()]:
        raise ValueError("exact five-field expected contract and eleven fixed arms required")
    for key in required - {"arm_ids"}:
        if type(expected[key]) is not int or expected[key] <= 0:
            raise ValueError("positive integral planned counts required")
    if expected["total_attempts_planned"] != expected["candidate_attempts_planned"] + expected["baseline_attempts_planned"]:
        raise ValueError("planned total differs")


def runtime_facts(plan_path, manifest_path, context_path, exclusion_path):
    root = Path(__file__).resolve().parent
    paths = {name: root / name for name in sorted(SOURCE_REQUIRED)}
    paths.update(protocol=plan_path, source_manifest=manifest_path,
                 provider_context=context_path, prior_exclusions=exclusion_path)
    return {"resuid": list(os.getresuid()), "resgid": list(os.getresgid()),
            "supplementary_groups": os.getgroups(),
            "input_access": {name: {"exists": path is not None and Path(path).is_file(),
                                    "writable": path is not None and os.access(path, os.W_OK)}
                             for name, path in paths.items()}, "environment_values_collected": False}


def enforce_runtime(facts):
    if facts["resuid"] != [1000] * 3 or facts["resgid"] != [1000] * 3 or facts["supplementary_groups"]:
        raise ValueError("isolated UID/GID1000 and no supplementary groups required")
    if any(not x["exists"] or x["writable"] for x in facts["input_access"].values()):
        raise ValueError("seven sources and all staged inputs must exist and be read-only to worker")


def validate_sources(path, plan):
    if path is None:
        raise ValueError("exact seven-file source manifest required")
    manifest = json.loads(path.read_bytes())
    if manifest.get("schema") != SCHEMA + ".source-manifest/v1" or set(manifest.get("files", {})) != SOURCE_REQUIRED:
        raise ValueError("wrong seven-file source closure")
    root = Path(__file__).resolve().parent
    for name, digest in manifest["files"].items():
        if not re.fullmatch(r"[0-9a-f]{64}", digest) or sha_file(root / name) != digest:
            raise ValueError("source hash differs: " + name)
    if not re.fullmatch(r"[0-9a-f]{40}", manifest.get("source_revision_c", "")):
        raise ValueError("actual source commit C required")
    fingerprint = sha_file(path)
    if plan.get("source_manifest_sha256") != fingerprint:
        raise ValueError("frozen plan/source-manifest binding differs")
    return manifest, fingerprint


def describe_plan(plan):
    import cohort
    description = cohort.describe_plan(plan)
    targets = description["target_cases_planned"]
    computed = {"candidate_attempts_planned": targets * 9 * REPLICATES,
                "baseline_attempts_planned": targets * (REPLICATES + 1),
                "total_attempts_planned": targets * (10 * REPLICATES + 1),
                "fixture_count_planned": description["fixture_count_planned"],
                "arm_ids": [a["id"] for a in arm_specs()]}
    if computed != plan["expected"]:
        raise ValueError("cohort schedule/eleven-arm four-draw counts differ from frozen expected contract")
    return {"schema": SCHEMA + ".plan-description/v1", "measurement_started": False,
            "fresh_cohort_generated": False, "candidate_attempts_executed": 0,
            **computed, "cohort_plan": description, "fixed_candidate_attempts_planned": targets * 8 * REPLICATES,
            "aa_attempts_planned": targets * REPLICATES,
            "uniform_attempts_planned": targets * REPLICATES,
            "bsgs_attempts_planned": targets, "coordinate_views_are_independent": False}


def fixture_model(fixture):
    return {key: fixture[key] for key in ("p", "a", "b", "r")}


def validate_public_cohort(public, description):
    if public.get("schema") != SCHEMA + ".public-cohort/v1" or public.get("generation_status") != "complete":
        raise ValueError("a complete fresh public cohort is required; partial cohort remains retained")
    fixtures = public.get("fixtures", [])
    if len(fixtures) != description["fixture_count_planned"]:
        raise ValueError("fresh fixture coverage differs")
    if sum(len(f["targets"]) for f in fixtures) != description["cohort_plan"]["target_cases_planned"]:
        raise ValueError("fresh target coverage differs")
    if len({f["curve_id"] for f in fixtures}) != len(fixtures):
        raise ValueError("duplicate fresh fixture ID")
    costs = []
    for f in fixtures:
        m = fixture_model(f)
        certification = certify_public_parameters(**m)
        curve = Curve(m["p"], m["a"], m["b"])
        base = point_from_json(f["base"])
        if base is None or not curve.contains(base) or curve.multiply(base, m["r"]) is not None:
            raise ValueError("invalid public prime-order base")
        ids = set()
        for t in f["targets"]:
            if t["target_id"] in ids:
                raise ValueError("duplicate public target ID")
            ids.add(t["target_id"])
            point = point_from_json(t["point"])
            if point is None or not curve.contains(point):
                raise ValueError("invalid/identity primary target")
        costs.append({"curve_id": f["curve_id"], "parameter_certification": certification,
                      "membership_and_base_order": curve.counter.snapshot(),
                      "curve_order_certificate_independently_verified_here": False})
    return costs


def run_attempts(plan, public, out, provenance):
    """Stream all outcomes; never retain a passing-only candidate subset."""
    counts = Bag()
    setup_totals, phase_totals = {}, {}
    target_count = sum(len(f["targets"]) for f in public["fixtures"])
    with (out / "attempts.jsonl").open("xb") as attempts, (out / "setups.jsonl").open("xb") as setups, (out / "diagnostics.jsonl").open("xb") as diagnostics, (out / "attempt-intents.jsonl").open("xb") as intents:
        for fixture in public["fixtures"]:
            model, curve_id = fixture_model(fixture), fixture["curve_id"]
            original_base = point_from_json(fixture["base"])
            prepared_cache = {}
            # Candidate/AA executions precede the baseline table's construction.
            ordered_arms = [a for a in arm_specs() if a["kind"] in ("candidate", "aa_replay")]
            ordered_arms += [a for a in arm_specs() if a["kind"] not in ("candidate", "aa_replay")]
            for arm in ordered_arms:
                a = arm["base_multiplier"]
                transform = Curve(model["p"], model["a"], model["b"])
                candidate_kind = arm["kind"] in ("candidate", "aa_replay")
                transformed_base = transform.multiply(original_base, a) if candidate_kind else original_base
                prepared = baseline = None
                if candidate_kind:
                    recipe = {"kind": "candidate", "alpha": arm["alpha"] % model["p"], "beta": arm["beta"] % model["p"]}
                    prepared = prepare(model, transformed_base, recipe)
                    prepared_cache[arm["id"]] = prepared
                elif arm["kind"] == "bsgs_reference":
                    baseline = BSGS(model, original_base)
                setup = {"schema": SCHEMA + ".setup/v1", **provenance,
                         "curve_id": curve_id, "arm_id": arm["id"], "kind": arm["kind"],
                         "model": model, "original_base": point_json(original_base),
                         "base_multiplier": a, "transformed_base": point_json(transformed_base),
                         "circuit": {k: arm[k] for k in ("alpha", "beta")} if candidate_kind else None,
                         "status": "UNDEFINED" if prepared and prepared.setup_reason else "READY",
                         "reason": prepared.setup_reason if prepared else None,
                         "counts": {"base_transform": transform.counter.snapshot(),
                                    "constructor_setup": prepared.setup_counts if prepared else {},
                                    "reference_setup": baseline.setup_counts if baseline else {}},
                         "shared_across_targets": True,
                         "reference_state_entries": len(baseline.babies) if baseline else 0}
                setups.write(canonical_json(setup))
                counts["setup_rows"] += 1
                setup_totals.setdefault(arm["id"], Counter())
                for vector in setup["counts"].values():
                    add_counts(setup_totals[arm["id"]], vector)
                for target in fixture["targets"]:
                    original_target = point_from_json(target["point"])
                    reps = REPLICATES if arm["kind"] != "bsgs_reference" else 1
                    for replicate in range(reps):
                        attempt_id = f"{curve_id}/{target['target_id']}/{arm['id']}/rep{replicate}"
                        reference_id = arm.get("reference_arm_id", arm["id"])
                        draw_id = f"{curve_id}/{target['target_id']}/{reference_id}/rep{replicate}"
                        intents.write(canonical_json({"attempt_id": attempt_id, "curve_id": curve_id, "target_id": target["target_id"], "arm_id": arm["id"], "replicate_index": replicate, "status": "started"}))
                        intents.flush()
                        counts["attempt_intents"] += 1
                        sampling = None
                        b = 1
                        transformed_target = original_target
                        if candidate_kind:
                            rng = Counter()
                            b, sampling = uniform_below(public["public_nonce_hex"], "target-blinding", draw_id, model["r"] - 1, rng)
                            b += 1
                            transformed_target, result = ungated_attempt(prepared, original_base, original_target, a, b)
                            result["counts"]["rng"] = rng.snapshot()
                        elif arm["kind"] == "uniform_candidate":
                            result, sampling = uniform_attempt(model, original_base, original_target, public["public_nonce_hex"], draw_id)
                        else:
                            result = baseline.recover(original_target)
                        row = {"schema": SCHEMA + ".attempt/v1", **provenance,
                               "attempt_id": attempt_id, "curve_id": curve_id, "target_id": target["target_id"],
                               "arm_id": arm["id"], "kind": arm["kind"], "replicate_index": replicate,
                               "model": model, "original_base": point_json(original_base),
                               "base_multiplier": a, "transformed_base": point_json(transformed_base),
                               "original_target": point_json(original_target), "target_multiplier": b,
                               "transformed_target": point_json(transformed_target), "sampling": sampling,
                               "result": result}
                        attempts.write(canonical_json(row))
                        attempts.flush()
                        counts["attempts"] += 1
                        counts["candidate_attempts" if candidate_kind else "baseline_attempts"] += 1
                        counts[f"{arm['id']}:{result['status']}"] += 1
                        phase_totals.setdefault(arm["id"], {})
                        for phase, vector in result["counts"].items():
                            phase_totals[arm["id"]].setdefault(phase, Counter())
                            add_counts(phase_totals[arm["id"]][phase], vector)
            # This exhaustive bit diagnostic never gates any primary attempt.
            if fixture["panel"] == "exact":
                for arm in arm_specs():
                    if arm["kind"] != "candidate":
                        continue
                    prepared = prepared_cache[arm["id"]]
                    points = [None] + [point_from_json(t["point"]) for t in fixture["targets"]]
                    for point in points:
                        answer, vector = prepared.evaluate(point)
                        row = {"schema": SCHEMA + ".diagnostic/v1", **provenance,
                               "curve_id": curve_id, "arm_id": arm["id"], "model": model,
                               "base_multiplier": arm["base_multiplier"],
                               "transformed_base": point_json(prepared.base),
                               "target": point_json(point), "answer": answer, "counters": vector,
                               "shared_setup_reused": True, "used_to_gate_primary": False}
                        diagnostics.write(canonical_json(row))
                        counts["diagnostic_rows"] += 1
            if counts["attempts"] % 10000 < 3000:
                print(json.dumps({"curve_completed": curve_id, "attempts_completed": counts["attempts"]}), flush=True)
    return {"counts": dict(sorted(counts.items())), "target_cases": target_count,
            "setup_counts_by_arm": {a: c.snapshot() for a, c in setup_totals.items()},
            "attempt_counts_by_arm_phase": {a: {p: c.snapshot() for p, c in phases.items()} for a, phases in phase_totals.items()}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--source-manifest", type=Path, required=True)
    parser.add_argument("--provider-context", type=Path)
    parser.add_argument("--prior-exclusions", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--plan-only", action="store_true")
    args = parser.parse_args()
    plan = json.loads(args.protocol.read_bytes())
    validate_plan(plan, actual=not args.plan_only)
    manifest, fingerprint = validate_sources(args.source_manifest, plan)
    if sha_file(args.prior_exclusions) != plan["cohort"]["exclusion_file_sha256"]:
        raise ValueError("bound prior exclusion bytes differ")
    exclusions = json.loads(args.prior_exclusions.read_bytes())
    facts = runtime_facts(args.protocol, args.source_manifest, args.provider_context, args.prior_exclusions)
    if args.provider_context is not None:
        enforce_runtime(facts)
    description = describe_plan(plan)
    description.update(runtime_facts=facts, provider_runtime_requirements_enforced=args.provider_context is not None)
    if args.plan_only:
        print(json.dumps(description), flush=True)
        return 0
    if args.provider_context is None:
        raise ValueError("actual isolated provider context required")
    args.output_dir.mkdir(parents=True, exist_ok=False)
    context = json.loads(args.provider_context.read_bytes())
    summary = {"schema": SCHEMA + ".compute-summary/v1", "experiment_id": EXPERIMENT, "run_id": RUN,
               "measurement_started": False, "fresh_cohort_generated": False, "completed": False, "primary_attempt_phase_started": False,
               "source_fingerprint": fingerprint, "source_revision_c": manifest["source_revision_c"],
               "protocol_sha256": sha_file(args.protocol), "official_protocol_sha256": context.get("protocol_sha256"),
               "all_clocks_wall_valid": False, "candidate_counter_execution_replayed": False,
               "runtime_facts": facts, "expected": plan["expected"],
               "independent_verification": "pending", "automatic_retry": False}
    try:
        summary["measurement_started"] = True
        legacy_controls = run_legacy_controls()
        write_json(args.output_dir / "control-phase.json", legacy_controls)
        summary["legacy_controls_passed"] = legacy_controls["passed"]
        if not legacy_controls["passed"]:
            raise ValueError("known-fixture control failed before fresh cohort generation")
        import cohort
        cohort_dir = args.output_dir / "cohort"
        summary["measurement_started"] = True
        public = cohort.generate(plan, cohort_dir, exclusions_data=exclusions)
        summary["fresh_cohort_generated"] = True
        cohort_path = cohort_dir / "cohort-public.json"
        if public != json.loads(cohort_path.read_bytes()):
            raise ValueError("returned public cohort differs from sealed generator output")
        validation = validate_public_cohort(public, description)
        summary["common_input_validation"] = validation
        summary["common_input_validation_allocation"] = "Observed once globally per fixture, reported separately; full per-arm workload comparisons must charge the same declared common validation once, not duplicate it as new executions."
        provenance = {"protocol_sha256": sha_file(args.protocol), "source_fingerprint": fingerprint,
                      "cohort_sha256": sha_file(cohort_path)}
        summary["primary_attempt_phase_started"] = True
        result = run_attempts(plan, public, args.output_dir, provenance)
        summary.update(result)
        if result["counts"].get("attempts") != plan["expected"]["total_attempts_planned"]:
            raise ValueError("completed attempt coverage differs from frozen expected contract")
        summary["completed"] = True
    except Exception as error:
        summary["failure"] = {"type": type(error).__name__, "message": str(error)}
        for name in ("attempt-intents.jsonl", "attempts.jsonl", "setups.jsonl", "diagnostics.jsonl"):
            p = args.output_dir / name
            if p.exists():
                with p.open("rb") as stream:
                    summary[name + "_complete_lines"] = sum(b.count(b"\n") for b in iter(lambda: stream.read(1 << 20), b""))
        write_json(args.output_dir / "failure.json", summary["failure"])
    summary["failure_attempt_accounting"] = "A flushed intent precedes every actual attempt. Completed record follows the result and is flushed. On interruption, intended-minus-recorded attempts are unresolved, not replayed or success-filtered; remaining planned IDs are unattempted. A partial trailing JSON line stays raw."
    files = []
    for p in sorted(args.output_dir.rglob("*")):
        if p.is_file():
            files.append({"path": p.relative_to(args.output_dir).as_posix(), "bytes": p.stat().st_size, "sha256": sha_file(p)})
    summary["retained_files_before_summary"] = files
    summary["comparison_cost_semantics"] = {"input_construction": "cohort generation/certification vectors observed once per fixed input cohort; retain separately", "common_validation": "observed once per fixture and separately attributed equally when full per-arm workloads are compared", "setup": "one actual base transformation/preparation per arm/fixture reused for all target repetitions", "restart_model": "known fresh b on every retry makes the target uniform in the nonzero prime-order group; q is empirical, zero observed successes do not prove q=0", "cold_retry_formula": "setup + mean online cost / observed q, vector by vector; undefined if observed successes zero", "actual_batch_formula": "(setup + sum online cost) / verified successes; undefined if observed successes zero", "timing_qualified": False}
    summary["unmetered_harness_work"] = ["Python control/container operations", "JSON/hash/file I/O and provenance/runtime checks", "cohort generation vectors are separate from candidate arithmetic vectors"]
    write_json(args.output_dir / "compute-summary.json", summary)
    write_json(args.output_dir / "completion.json", {"schema": SCHEMA + ".completion/v1",
        "completed": summary["completed"], "protocol_sha256": summary["protocol_sha256"],
        "source_fingerprint": fingerprint, "summary_sha256": sha_file(args.output_dir / "compute-summary.json"),
        "attempts_sha256": sha_file(args.output_dir / "attempts.jsonl") if (args.output_dir / "attempts.jsonl").exists() else None,
        "setups_sha256": sha_file(args.output_dir / "setups.jsonl") if (args.output_dir / "setups.jsonl").exists() else None,
        "diagnostics_sha256": sha_file(args.output_dir / "diagnostics.jsonl") if (args.output_dir / "diagnostics.jsonl").exists() else None})
    print(json.dumps({"completed": summary["completed"], "counts": summary.get("counts"), "failure": summary.get("failure")}), flush=True)
    return 0 if summary["completed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
