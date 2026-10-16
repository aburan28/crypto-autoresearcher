#!/usr/bin/env python3
"""Exact conditional state and timestamp-choice arithmetic."""

import datetime as dt
import hashlib
import json
import math
import platform
import sys
import time
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
TARGETS = REPO / "research/nist_seed_selection_20261016/targets.json"
PROCESS = REPO / "research/nist_seed_generation_process_20261016/process_checks.json"
A, C, BITS, DRAWS = 0x5DEECE66D, 0xB, 48, 20


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out = HERE / "raw/selection_space.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        raise FileExistsError(out)
    targets = json.loads(TARGETS.read_text())
    process = json.loads(PROCESS.read_text())
    if not process:
        raise AssertionError("prior process record absent")
    runs = {}
    for t in targets:
        if t["kind"] == "prime":
            runs.setdefault(t["unix_time"], []).append(t["name"])
    if len(runs) != 6 or sum(map(len, runs.values())) != 10:
        raise AssertionError("unexpected prime stream reuse")
    if A % 4 != 1 or C % 2 != 1:
        raise AssertionError("full-period LCG conditions absent")
    first_residue = ((A * 0x330E + C) & ((1 << BITS) - 1)) % 4
    if first_residue != 1 or DRAWS % 4:
        raise AssertionError("candidate-start residue proof failed")
    strict_states = (1 << BITS) // math.gcd(DRAWS, 1 << BITS)
    if strict_states != 1 << 46:
        raise AssertionError("candidate-start state ceiling differs")
    start = dt.datetime(1997, 1, 1, tzinfo=dt.timezone.utc)
    end = dt.datetime(1999, 1, 1, tzinfo=dt.timezone.utc)
    timestamp_starts = int((end - start).total_seconds())
    if not all(start.timestamp() <= t < end.timestamp() for t in runs):
        raise AssertionError("recovered timestamp outside declared interval")
    scenarios = []
    for candidate_slots_per_start in (1, 16, 7026):
        pairs = timestamp_starts * candidate_slots_per_start
        scenarios.append({"slots_per_timestamp": candidate_slots_per_start,
                          "timestamp_slot_pairs": pairs,
                          "pair_bits": math.log2(pairs),
                          "distinct_seed_upper_bound": min(pairs, strict_states),
                          "interpretation": "conditional combinatorial ceiling, not attempts"})
    result = {"status": "derived_conditional_bounds", "created_utc":
              time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
              "command": sys.argv, "python": platform.python_version(),
              "script_sha256": digest(Path(__file__)),
              "inputs_sha256": {str(path.relative_to(REPO)): digest(path)
                                for path in (TARGETS, PROCESS)},
              "lcg_multiplier": A, "lcg_increment": C, "state_bits": BITS,
              "draws_per_candidate": DRAWS, "first_output_residue_mod4": first_residue,
              "strict_consecutive_candidate_start_states": strict_states,
              "arbitrary_between_window_draw_state_ceiling": 1 << BITS,
              "recovered_prime_stream_starts":
              [{"unix_time": t, "targets": sorted(names)} for t, names in sorted(runs.items())],
              "recovered_starts_count": len(runs),
              "calendar_interval_utc": [start.isoformat(), end.isoformat()],
              "possible_one_second_timestamp_starts": timestamp_starts,
              "conditional_scenarios": scenarios,
              "unknowns": ["number of actual starts tried", "number of candidate windows tested",
                           "earlier field-prime choice", "different seed recipe",
                           "historical acceptance rule"]}
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"path": str(out), "sha256": digest(out),
                      "strict_states": strict_states,
                      "timestamp_starts_1997_1998": timestamp_starts}))


if __name__ == "__main__":
    main()
