"""Run and audit the native A/B/A six-class comparison in a sealed container.

Each trial has a baseline before and after the candidate. Repeated arms use
the same deterministic walkers, so this measures host timing drift and method
work counts; it does not estimate independent collision success probability.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from harness import sixclass_isolated, sixclass_native

SCHEMA = "crypto.autoresearch.sixclass-paired.v1"
NATIVE_SCHEMA = "crypto.sixclass.paired-native.v1"
ARMS = ("baseline_before", "six_class", "baseline_after")
COUNT_FIELDS = ("walkers", "class_visits", "distinguished", "dead_trails",
                "collisions", "dp_entries")


def audit(job: Path, binary: Path, walkers: int, trials: int,
          native: dict, elapsed_ns: int) -> dict:
    if not 1 <= walkers <= 1_000_000 or not 1 <= trials <= 100:
        raise ValueError("walkers or trials outside native bounds")
    if (native.get("schema") != NATIVE_SCHEMA
            or native.get("job_sha256") != sixclass_native.digest(job)
            or native.get("max_walkers") != walkers
            or len(native.get("trials", [])) != trials
            or not native.get("unpriced")):
        raise ValueError("native comparison does not match the requested job and bounds")
    source = json.loads(job.read_text())
    branches = source["curve"]["num_branches"]
    rows = []
    for index, trial in enumerate(native["trials"]):
        if trial.get("index") != index:
            raise ValueError("trial index is missing or out of order")
        for name in ARMS:
            arm = trial[name]
            if (any(type(arm.get(field)) is not int or arm[field] < 0
                    for field in (*COUNT_FIELDS, "setup_ns", "campaign_ns", "total_ns"))
                    or arm["total_ns"] != arm["setup_ns"] + arm["campaign_ns"]
                    or arm["walkers"] > walkers
                    or arm["distinguished"] > arm["walkers"]
                    or arm["dp_entries"] > arm["distinguished"]
                    or (arm["distinguished"] > 0) != arm["first_dp_verified"]):
                raise ValueError(f"invalid native arm counters: {name}")
            if arm["log"] is not None and not sixclass_native.verify_log(source, arm["log"]):
                raise ValueError(f"invalid recovered logarithm in {name}")
        before, candidate, after = (trial[name] for name in ARMS)
        routing = candidate.get("route_by_twist")
        if routing is not None:
            if (not isinstance(routing, list) or len(routing) != 6
                    or any(not isinstance(class_row, list) or len(class_row) != branches
                           or any(type(count) is not int or count < 0 for count in class_row)
                           for class_row in routing)
                    or sum(map(sum, routing)) != candidate["class_visits"]):
                raise ValueError("invalid six-class routing telemetry")
        if before["method"] != after["method"] or before["method"] != native["baseline"]:
            raise ValueError("A/A baseline methods differ")
        # The same seeds, target, and walkers make A/A counters deterministic.
        if any(before[field] != after[field] for field in COUNT_FIELDS):
            raise ValueError("A/A controls did different work")
        if before["log"] != after["log"]:
            raise ValueError("A/A controls disagree on the recovered logarithm")
        rows.append({"index": index, "baseline_before_ns": before["total_ns"],
                     "six_class_ns": candidate["total_ns"],
                     "baseline_after_ns": after["total_ns"],
                     "baseline_drift_ratio": (after["total_ns"] / before["total_ns"]
                                              if before["total_ns"] else None),
                     "routing_screen": ({"twist_visits": [sum(c) for c in routing],
                                          "branch_visits": [sum(c[j] for c in routing)
                                                            for j in range(branches)],
                                          "independent_samples": False}
                                         if routing is not None else None),
                     "six_class_to_bracket_mean_ratio":
                     (candidate["total_ns"] / ((before["total_ns"] + after["total_ns"]) / 2)
                      if before["total_ns"] + after["total_ns"] else None)})
    return {"schema": SCHEMA, "job_sha256": sixclass_native.digest(job),
            "binary_sha256": sixclass_native.digest(binary),
            "native_schema": NATIVE_SCHEMA, "image": sixclass_isolated.IMAGE,
            "requested_walkers": walkers, "requested_trials": trials,
            "elapsed_ns": elapsed_ns, "native": native, "paired_rows": rows,
            "status": "bounded_diagnostic_only",
            "claim_limits": ["deterministic repeats do not measure collision CDF",
                             "BigUint wall times are not production instruction-equivalent costs",
                             "unpriced categories block full attack cost claims"]}


def run(job: Path, binary: Path, walkers: int, trials: int, out: Path,
        *, sudo: bool = False, timeout: int = 120) -> dict:
    if not 1 <= walkers <= 1_000_000 or not 1 <= trials <= 100:
        raise ValueError("walkers or trials outside native bounds")
    native, elapsed_ns = sixclass_isolated._run_container(
        binary, [(job, "/input/job.json", True)],
        ["/input/job.json", str(walkers), str(trials)], sudo=sudo, timeout=timeout)
    receipt = audit(job, binary, walkers, trials, native, elapsed_ns)
    sixclass_isolated._write_new(out, receipt)
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--job", type=Path, required=True)
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--walkers", type=int, required=True)
    parser.add_argument("--trials", type=int, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--sudo", action="store_true")
    args = parser.parse_args()
    receipt = run(args.job, args.binary, args.walkers, args.trials, args.out,
                  sudo=args.sudo, timeout=args.timeout)
    print(json.dumps({"receipt": str(args.out), "paired_rows": receipt["paired_rows"]},
                     sort_keys=True))


if __name__ == "__main__":
    main()
