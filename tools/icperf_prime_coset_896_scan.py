"""Target-blind, write-once 16-seed search for a 63-bit d=896 coset base.

This prepares factor-base inputs. It neither runs a decomposition solver nor
measures an ECDLP pipeline. Every attempted seed and complete point list is
retained; the winner is selected only by realized point count.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))
from tools.icperf_explicit_base import prepare, sha256_file  # noqa: E402

FIXTURE = ROOT / "research/icperf_prime_fixtures_20261017/n63_seed20261017.json"
DIVISOR = 896
TARGET_SIZE = 441
SEEDS = list(range(20261017, 20261033))


def upper_count(base_size: int, m: int) -> int:
    """Maximum distinct sums from signed, repetition-allowed m-multisets."""
    return math.comb(2 * base_size + m - 1, m)


def count_threshold(order: int, m: int) -> int:
    """Smallest base size whose optimistic signed-multiset count reaches order."""
    low, high = 0, 1
    while upper_count(high, m) < order:
        high *= 2
    while high - low > 1:
        mid = (low + high) // 2
        if upper_count(mid, m) < order:
            low = mid
        else:
            high = mid
    return high


def build_scan() -> dict:
    fixture = json.loads(FIXTURE.read_bytes())
    p, order = fixture["curve"]["p"], fixture["curve"]["order"]
    assert (p - 1) % DIVISOR == 0
    assert count_threshold(order, 8) == TARGET_SIZE
    started = dt.datetime.now(dt.timezone.utc).isoformat()
    wall = time.perf_counter()
    cpu = time.process_time()
    attempts = []
    for seed in SEEDS:
        candidate = prepare(FIXTURE, "subgroup", DIVISOR, TARGET_SIZE, seed)
        size = candidate["realized_size"]
        candidate["signed_m8_multiset_upper_count"] = upper_count(size, 8)
        candidate["signed_m8_count_reaches_order"] = upper_count(size, 8) >= order
        attempts.append(candidate)
    selected = max(attempts, key=lambda item: (item["realized_size"],
                                               -item["base_parameters"]["seed"]))
    return {
        "schema": "icperf-prime-coset-896-search-v1",
        "scope": "target-blind complete candidate scan and counting preflight; no relation or ECDLP cost claim",
        "source_sha256": sha256_file(Path(__file__)),
        "fixture_sha256": sha256_file(FIXTURE),
        "base_preparer_sha256": sha256_file(ROOT / "tools/icperf_explicit_base.py"),
        "divisor": DIVISOR,
        "target_size": TARGET_SIZE,
        "seeds": SEEDS,
        "selection_rule": "largest realized point count; ties to lowest seed",
        "curve": fixture["curve"],
        "signed_m8_count_threshold": TARGET_SIZE,
        "selected_seed": selected["base_parameters"]["seed"],
        "selected_realized_size": selected["realized_size"],
        "selected_point_sha256": selected["point_sha256"],
        "attempts": attempts,
        "scan": {"started_at_utc": started,
                 "finished_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
                 "wall_seconds": time.perf_counter() - wall,
                 "cpu_seconds": time.process_time() - cpu,
                 "attempt_count": len(attempts)},
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    record = build_scan()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x") as stream:
        json.dump(record, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"selected_seed": record["selected_seed"],
                      "selected_realized_size": record["selected_realized_size"],
                      "count_threshold": record["signed_m8_count_threshold"]}, sort_keys=True))


if __name__ == "__main__":
    main()
