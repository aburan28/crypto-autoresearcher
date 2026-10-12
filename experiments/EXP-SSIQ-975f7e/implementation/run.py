"""Frozen integer scan for IDEA-20261006-14ca06.

Importing this module does not start the scan. The approved trial plan supplies
the output directory when an Executor launches the scientific run.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

EXPERIMENT_ID = "EXP-SSIQ-975f7e"
RUN_ID = "RUN-SSIQ-be0b59"
PRIMES = (2, 3, 5, 7)
X = 30
LOW = 31
HIGH = 180


def factor_7_smooth(value: int) -> list[int] | None:
    remainder = value
    factors: list[int] = []
    for prime in PRIMES:
        while remainder % prime == 0:
            factors.append(prime)
            remainder //= prime
    return factors if remainder == 1 else None


def longest_prefix(factors: list[int]) -> int:
    product = 1
    for prime in factors:
        if product * prime > X:
            break
        product *= prime
    return product


def build_report() -> dict:
    rows = []
    for degree in range(LOW, HIGH + 1):
        factors = factor_7_smooth(degree)
        if factors is None:
            continue
        ascending = longest_prefix(factors)
        descending = longest_prefix(list(reversed(factors)))
        ascending_cofactor = degree // ascending
        descending_cofactor = degree // descending
        ratio_at_least_two = max(ascending, descending) >= 2 * min(ascending, descending)
        opposite_cofactor_sides = (ascending_cofactor > X) != (descending_cofactor > X)
        rows.append({
            "degree": degree,
            "factors_ascending": factors,
            "ascending_prefix": ascending,
            "descending_prefix": descending,
            "ascending_cofactor": ascending_cofactor,
            "descending_cofactor": descending_cofactor,
            "ratio_at_least_two": ratio_at_least_two,
            "opposite_cofactor_sides": opposite_cofactor_sides,
            "meets_both": ratio_at_least_two and opposite_cofactor_sides,
        })
    by_degree = {row["degree"]: row for row in rows}
    controls = {
        "thirty_excluded": 30 not in by_degree,
        "eleven_excluded": factor_7_smooth(11) is None,
        "thirty_two_prefixes_equal": by_degree[32]["ascending_prefix"] == by_degree[32]["descending_prefix"],
        "all_degrees_in_range": all(LOW <= row["degree"] <= HIGH for row in rows),
        "all_factors_allowed": all(set(row["factors_ascending"]) <= set(PRIMES) for row in rows),
        "all_products_reconstruct": all(
            row["degree"] == row["ascending_prefix"] * row["ascending_cofactor"]
            == row["descending_prefix"] * row["descending_cofactor"] for row in rows
        ),
    }
    return {
        "schema": "crypto.autoresearch.ssiq_prefix_scan.v1",
        "experiment_id": EXPERIMENT_ID,
        "run_id": RUN_ID,
        "source_idea": "IDEA-20261006-14ca06",
        "B": 7,
        "X": X,
        "range": {"lower_exclusive": 30, "upper_inclusive": HIGH},
        "smooth_count": len(rows),
        "match_count": sum(row["meets_both"] for row in rows),
        "controls": controls,
        "rows": rows,
    }


def write_run(run_dir: Path) -> None:
    started_at = datetime.now(timezone.utc).isoformat()
    start = time.perf_counter()
    report = build_report()
    elapsed = time.perf_counter() - start
    source = Path(__file__).resolve()
    source_sha256 = hashlib.sha256(source.read_bytes()).hexdigest()
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    tracked_dirty = bool(subprocess.check_output(
        ["git", "status", "--porcelain", "--untracked-files=no"], text=True
    ).strip())
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "raw-result.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (run_dir / "manifest.yaml").write_text(
        "run:\n"
        f"  id: {RUN_ID}\n"
        f"  experiment_id: {EXPERIMENT_ID}\n"
        "  hypothesis_id: H-SSIQ-85f1f1\n"
        "  goal_id: GOAL-SSIQ-001\n"
        "  task_id: TASK-20261010-a3cf39\n"
        "  status: completed_unreviewed\n"
        f"  recorded_at: {json.dumps(started_at)}\n"
        "  code:\n"
        f"    commit: {commit}\n"
        f"    dirty: {str(tracked_dirty).lower()}\n"
        "    command: python3 experiments/EXP-SSIQ-975f7e/implementation/run.py --run-dir <run_dir>\n"
        "    source_path: experiments/EXP-SSIQ-975f7e/implementation/run.py\n"
        f"    source_sha256: {source_sha256}\n"
        "  environment:\n"
        f"    python: {json.dumps(platform.python_version())}\n"
        f"    platform: {json.dumps(platform.platform())}\n"
        f"    executable: {json.dumps(sys.executable)}\n"
        "  inputs:\n"
        "    parameters: {B: 7, X: 30, lower_exclusive: 30, upper_inclusive: 180}\n"
        "    seeds: {declared: []}\n"
        "  timing:\n"
        f"    wall_clock_seconds: {elapsed:.9f}\n"
        "  result:\n"
        "    validity_status: pending_checker\n"
        "    certificate: {kind: none, verified: false}\n"
        "    metrics:\n"
        f"      smooth_count: {report['smooth_count']}\n"
        f"      match_count: {report['match_count']}\n"
        "  artifacts:\n"
        "    raw_result: raw-result.json\n"
        "    stdout: stdout.log\n"
        "    stderr: stderr.log\n"
        "    environment: environment.json\n"
        "    command: command.txt\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args()
    write_run(Path(args.run_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
