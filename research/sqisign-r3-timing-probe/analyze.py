#!/usr/bin/env python3
"""Fixed analysis for the frozen SQIsign p324_3 timing protocol."""
import csv
import json
import math
import random
import statistics
import sys
from pathlib import Path

N_KEYS = 8
N_ROUNDS = 32
N_PERMUTATIONS = 10000


def read_rows(path):
    with Path(path).open(newline="") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == N_KEYS * N_ROUNDS, (path, len(rows))
    for row in rows:
        for field in ("round", "key", "position", "sign_ns", "loop2_iterations"):
            row[field] = int(row[field])
    assert {(r["round"], r["key"]) for r in rows} == {
        (i, j) for i in range(N_ROUNDS) for j in range(N_KEYS)
    }
    assert all(r["sign_ns"] > 0 for r in rows)
    assert all(
        {r["position"] for r in rows if r["round"] == i} == set(range(N_KEYS))
        for i in range(N_ROUNDS)
    )
    return rows


def ranks(values):
    ordered = sorted(enumerate(values), key=lambda x: x[1])
    result = [0.0] * len(values)
    for i, (idx, value) in enumerate(ordered):
        low = next(j for j, (_, v) in enumerate(ordered) if v == value)
        high = max(j for j, (_, v) in enumerate(ordered) if v == value)
        result[idx] = (low + high) / 2
    return result


def pearson(a, b):
    am, bm = statistics.mean(a), statistics.mean(b)
    denom = math.sqrt(sum((v - am) ** 2 for v in a) * sum((v - bm) ** 2 for v in b))
    return sum((x - am) * (y - bm) for x, y in zip(a, b)) / denom if denom else None


def spearman(a, b):
    return pearson(ranks(a), ranks(b))


def main(pristine_file, instrumented_file):
    pristine, instrumented = read_rows(pristine_file), read_rows(instrumented_file)
    by_identity = lambda rows: {
        (r["round"], r["key"]): r for r in rows
    }
    pa, ia = by_identity(pristine), by_identity(instrumented)
    matches = all(pa[key]["signature_fnv64"] == ia[key]["signature_fnv64"] for key in pa)
    assert matches, "deterministic replay failed; do not compare runs"
    assert all(r["loop2_iterations"] == 0 for r in pristine)
    timing = lambda key, a, b: statistics.median(
        pa[(i, key)]["sign_ns"] / 1e6 for i in range(a, b)
    )
    first = [timing(k, 0, 16) for k in range(N_KEYS)]
    second = [timing(k, 16, 32) for k in range(N_KEYS)]
    observed = spearman(first, second)
    assert observed is not None
    rng = random.Random(20260927)
    exceed = 0
    for _ in range(N_PERMUTATIONS):
        labels = list(range(N_KEYS))
        rng.shuffle(labels)
        score = spearman(first, [second[i] for i in labels])
        exceed += score is not None and score >= observed - 1e-12
    counts = [r["loop2_iterations"] for r in instrumented]
    times = [r["sign_ns"] / 1e6 for r in instrumented]
    raw_times = [r["sign_ns"] / 1e6 for r in pristine]
    output = {
        "matched_signature_checksums": len(pa),
        "valid_signatures_each_build": len(pa),
        "pristine_sign_ms": {
            "min": min(raw_times),
            "median": statistics.median(raw_times),
            "max": max(raw_times),
        },
        "loop_two_iterations": {
            "min": min(counts),
            "median": statistics.median(counts),
            "max": max(counts),
            "distinct": len(set(counts)),
            "nonzero_count": sum(c > 0 for c in counts),
            "spearman_with_instrumented_sign_time": spearman(counts, times),
        },
        "key_timing_control": {
            "first_half_median_ms_by_key": first,
            "second_half_median_ms_by_key": second,
            "spearman": observed,
            "permutation_exceedances": exceed,
            "permutations": N_PERMUTATIONS,
            "one_sided_plus_one_p": (exceed + 1) / (N_PERMUTATIONS + 1),
            "shuffle_seed": 20260927,
        },
    }
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("usage: analyze.py pristine.csv instrumented.csv")
    main(*sys.argv[1:])
