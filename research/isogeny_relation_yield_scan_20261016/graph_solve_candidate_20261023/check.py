"""Separate Sage point replay for a candidate graph relation solve."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

from sage.all import EllipticCurve, GF

ROOT = Path(__file__).resolve().parents[3]
LEGACY = ROOT / "research/conductor_relation_yield_20261014"
sys.path.insert(0, str(LEGACY))
from verify_collector import verify


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(input_path: Path, collector_path: Path, count_path: Path, solve_path: Path) -> dict:
    result = json.loads(solve_path.read_text())
    if (result.get("schema") != "ectd.graph-complete-solve-candidate.v1" or
            result.get("input_sha256") != sha(input_path) or
            result.get("collector_sha256") != sha(collector_path) or
            result.get("count_sha256") != sha(count_path)):
        raise ValueError("solve artifact or input digest differs")
    fields = input_path.read_text().splitlines()
    header = fields[0].split()
    if len(header) != 7 or header[0] != "curve":
        raise ValueError("prepared curve header differs")
    p, a, b, r, nbase, ntarget = map(int, header[1:])
    if (p, a, b, r, ntarget) != tuple(result[key] for key in ("p", "a", "b", "r", "targets")) or len(fields) != 1 + nbase + ntarget:
        raise ValueError("prepared curve or target count differs")
    E = EllipticCurve(GF(p), [a, b])
    G = E(result["generator"])
    Q = E(result["Q"])
    if r * G != E(0) or r * Q != E(0):
        raise ValueError("generator or Q subgroup check differs")
    replay = verify(input_path, collector_path, tuple(result["generator"]),
                    tuple(result["Q"]), {512, 2048, 8192, 32768}, count_path)
    if (replay["status"] != "valid" or replay["unknown_columns"] != result["unknown_columns"] or
            replay["rank_increments"] != result["rank"] or
            replay["unique_canonical_coefficient_rows"] != result["unique_coefficient_rows"]):
        raise ValueError("rank or relation replay differs")
    if result["status"] == "censored_insufficient_rank":
        if (result["rank"] >= result["unknown_columns"] or
                any(result.get(key) is not None for key in ("scalar", "base_logs", "solution"))):
            raise ValueError("rank-censored solve reports a scalar")
        return {"status": "valid_censored", "rank": result["rank"],
                "unknown_columns": result["unknown_columns"]}
    if result["status"] != "verified_scalar":
        raise ValueError("unsupported solve status")
    scalar = result.get("scalar")
    logs = result.get("base_logs")
    if (not isinstance(scalar, int) or not 0 <= scalar < r or
            not isinstance(logs, list) or len(logs) != nbase // 2 or
            not all(isinstance(value, int) and 0 <= value < r for value in logs) or
            scalar * G != Q):
        raise ValueError("independent Sage Q-scalar equation failed")
    base = []
    for index, line in enumerate(fields[1:1 + nbase]):
        terms = line.split()
        if len(terms) != 4 or terms[:2] != ["base", str(index)]:
            raise ValueError("base row differs")
        base.append(E([int(terms[2]), int(terms[3])]))
    for orbit, value in enumerate(logs):
        if value * G != base[2 * orbit] or -base[2 * orbit] != base[2 * orbit + 1]:
            raise ValueError(f"independent factor-base log equation failed at {orbit}")
    targets = []
    for index, line in enumerate(fields[1 + nbase:]):
        terms = line.split()
        if len(terms) != 6 or terms[:2] != ["target", str(index)]:
            raise ValueError("target row differs")
        alpha, beta = int(terms[2]), int(terms[3])
        point = E([int(terms[4]), int(terms[5])])
        if alpha * G + beta * Q != point:
            raise ValueError(f"independent target point equation failed at {index}")
        targets.append((alpha, beta, point))
    checked_triples = 0
    for line in collector_path.read_text().splitlines()[1:]:
        terms = line.split("\t")
        if terms[0] != "triple":
            continue
        target_id, i, j, k = map(int, terms[1:])
        alpha, beta, point = targets[target_id]
        if base[i] + base[j] + base[k] != point:
            raise ValueError(f"independent relation point equation failed at {target_id}")
        lhs = sum(logs[point_id // 2] * (1 if point_id % 2 == 0 else -1)
                  for point_id in (i, j, k)) % r
        if lhs != (alpha + beta * scalar) % r:
            raise ValueError(f"independent relation log equation failed at {target_id}")
        checked_triples += 1
    return {"status": "valid_verified_scalar", "scalar": scalar,
            "base_orbits_checked": len(logs), "targets_checked": len(targets),
            "triples_checked": checked_triples}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("input", "collector", "count", "solve"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(check(args.input, args.collector, args.count, args.solve), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
