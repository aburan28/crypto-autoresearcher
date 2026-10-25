"""Record one exact-inversion tooling benchmark; not a curve-yield trial."""
from __future__ import annotations

import hashlib
import json
import platform
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
INTERVAL_SOURCE = HERE.parents[1] / "conductor_relation_yield_20261014/exact_interval.py"
sys.path.insert(0, str(INTERVAL_SOURCE.parent))
from exact_interval import interval


def main() -> None:
    population, draws, observed, divisor = 81640511860, 32768, 2048, 58800
    start = time.perf_counter_ns()
    result = interval(population, draws, observed, 1, divisor)
    wall_ns = time.perf_counter_ns() - start
    output = {"schema": "ectd.confirmation-interval-tooling-benchmark/v1",
              "scope": "single exact-interval calculation; no relation-yield data",
              "command": "python3 benchmark_interval.py > benchmark-interval.json",
              "source_sha256": hashlib.sha256(INTERVAL_SOURCE.read_bytes()).hexdigest(),
              "python": sys.version, "platform": platform.platform(),
              "wall_ns": wall_ns, "parameters": {"population": population,
                  "draws": draws, "observed": observed,
                  "tail_numerator": 1, "tail_denominator": divisor},
              "result": result}
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
