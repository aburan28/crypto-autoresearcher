"""Mandatory structured evidence gate for new cryptanalytic performance claims."""
import argparse
import json
import math
import pathlib
import statistics
import sys

REQUIRED = {"claim_id", "family", "level", "scale", "metric", "unit", "scope",
            "baseline", "candidate", "provenance", "cost_model"}
LEVELS = {"local", "end_to_end", "attack_projection"}
FAMILIES = {"index_calculus", "rho", "isogeny", "groebner_sat", "structure", "scalar", "ecdlp"}
THROUGHPUT = {"relations_per_second", "iterations_per_second"}
UNITS = {"seconds", "cpu_seconds", "gpu_seconds", "joules", "usd",
         "group_operations", "field_operations"} | THROUGHPUT

class InvalidClaim(ValueError):
    pass

def check(condition, reason):
    if not condition:
        raise InvalidClaim(reason)

def positive(values):
    return isinstance(values, list) and len(values) >= 2 and all(
        type(x) in (float, int) and math.isfinite(x) and x > 0 for x in values)

def evaluate(record):
    check(isinstance(record, dict), "claim must be an object")
    check(REQUIRED <= record.keys(), "missing " + str(sorted(REQUIRED - record.keys())))
    check(record["family"] in FAMILIES, "unknown family")
    check(record["level"] in LEVELS, "unknown level")
    check(record["scale"] in {"toy-scale", "feasibility-scale", "cryptographic-scale"}, "unknown scale")
    check(record["unit"] in UNITS, "unknown unit")
    check(isinstance(record["claim_id"], str) and bool(record["claim_id"]), "missing claim id")
    check(isinstance(record["metric"], str) and bool(record["metric"]), "missing metric")
    for field in ("curve_id", "field", "bits", "instance_generator", "parameter_digest"):
        check(record["scope"].get(field), "missing scope." + field)
    p = record["provenance"]
    for field in ("protocol", "baseline_commit", "candidate_commit", "hardware",
                  "environment_digest", "verification_artifact", "run_ids"):
        check(p.get(field), "missing provenance." + field)
    check(isinstance(p["run_ids"], list) and len(set(p["run_ids"])) == len(p["run_ids"]),
          "run IDs must be unique")
    for arm_name in ("baseline", "candidate"):
        arm = record[arm_name]
        check(positive(arm.get("observations")), arm_name + ": insufficient positive observations")
        for field in ("attempted", "verified", "failed", "timed_out", "invalid"):
            check(type(arm.get(field)) is int and arm[field] >= 0, arm_name + ": missing outcome " + field)
        check(arm["attempted"] == sum(arm[x] for x in ("verified", "failed", "timed_out", "invalid")),
              arm_name + ": outcomes do not reconcile")
        check(arm["verified"] > 0 and arm["invalid"] == 0 and arm["timed_out"] == 0,
              arm_name + ": invalid/censored/unverified measurements are not qualified")
        check(len(arm.get("pairs", [])) == len(arm["observations"]) and
              len(set(arm["pairs"])) == len(arm["pairs"]), arm_name + ": missing or duplicate pair IDs")
    b, c = record["baseline"], record["candidate"]
    check(b["pairs"] == c["pairs"], "unmatched instances/seeds")
    check(b["attempted"] == c["attempted"], "unmatched attempts")
    model = record["cost_model"]
    check(model.get("type") in {"none", "measured", "projection"}, "invalid cost model")
    if record["level"] != "local":
        check(model["type"] != "none", "nonlocal claim requires cost model")
        check(record["unit"] not in THROUGHPUT, "throughput cannot be added as total cost")
        components = model.get("components")
        check(isinstance(components, list) and len(components) > 0, "missing cost components")
        for item in components:
            check(item.get("unit") == record["unit"], "incompatible component units")
            check(item.get("name") and all(type(item.get(k)) in (float, int) and
                  math.isfinite(item[k]) and item[k] > 0 for k in ("baseline", "candidate")),
                  "invalid cost component")
        if record["level"] == "attack_projection":
            check(model["type"] == "projection" and model.get("assumptions") and
                  model.get("uncertainty"), "projection requires assumptions and uncertainty")
        bv = sum(x["baseline"] for x in components)
        cv = sum(x["candidate"] for x in components)
    else:
        bv = statistics.median(b["observations"])
        cv = statistics.median(c["observations"])
    speedup = cv / bv if record["unit"] in THROUGHPUT else bv / cv
    return {"claim_id": record["claim_id"], "level": record["level"],
            "speedup": speedup, "unit": record["unit"],
            "pairs": len(b["pairs"]), "qualified_schema": True,
            "evidence": "projected" if model["type"] == "projection" else "measured"}

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("validate", "compare", "portfolio"))
    parser.add_argument("path", type=pathlib.Path)
    args = parser.parse_args(argv)
    try:
        paths = sorted(args.path.glob("*.json")) if args.command == "portfolio" else [args.path]
        results = [evaluate(json.loads(p.read_text())) for p in paths]
        print(json.dumps(results if args.command == "portfolio" else results[0], indent=2))
        return 0
    except (InvalidClaim, ValueError, KeyError, TypeError, OSError) as exc:
        print("PROGRESS FIDELITY FAILED: " + str(exc), file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
