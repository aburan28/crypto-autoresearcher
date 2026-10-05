#!/usr/bin/env python3
"""Paired synthetic benchmark for GF(2) certificate verification, not solving.

Run: python3 tools/gf2_bench_certificate.py --out /tmp/gf2-certificate.json
Input generation is outside timing; each timed call includes reconstruction.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import statistics
import sys
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from crypto_autoresearcher.gf2 import rank_only as ro

BASELINE_BLOB = "94f1a925316b183c54cc3fa6488d6ec254cc8f10"


def legacy_verify(M: np.ndarray, C: int, cert: ro.RankCertificate) -> bool:
    """Recompute each claimed pivot row from ``cert.comb`` and check that its
    leading 1 sits at ``cert.pivcols[k]`` and that earlier pivots are already
    eliminated from it. Refuses empty ``comb`` (dense-path placeholder)."""
    if not cert.comb:
        return False
    if len(cert.comb) != len(cert.pivcols):
        return False
    W = M.shape[1]
    seen = set()
    for k, (c, rows) in enumerate(zip(cert.pivcols, cert.comb)):
        if not rows or c in seen or c >= C:
            return False
        acc = np.zeros(W, dtype=np.uint64)
        for r in rows:
            if r < 0 or r >= M.shape[0]:
                return False
            acc ^= M[r]
        # Leading bit must be c; bits left of c must be 0.
        for w in range(c >> 6):
            if acc[w]:
                return False
        word = int(acc[c >> 6])
        low = c & 63
        if (word & ((1 << low) - 1)) != 0:
            return False
        if ((word >> low) & 1) != 1:
            return False
        seen.add(c)
    return True


def environment():
    info = {"platform": platform.platform(), "machine": platform.machine(),
            "processor": platform.processor(), "python": sys.version,
            "numpy": np.__version__, "cpu_count": os.cpu_count(),
            "affinity": None, "affinity_error": None, "numa_policy": "not_bound",
            "memory_type": "unavailable", "cpu_model": None}
    if hasattr(os, "sched_getaffinity"):
        try:
            allowed = sorted(os.sched_getaffinity(0))
            if allowed:
                os.sched_setaffinity(0, {allowed[0]})
                info["affinity"] = sorted(os.sched_getaffinity(0))
                nodes = sorted(Path("/sys/devices/system/cpu/cpu" + str(allowed[0])).glob("node*"))
                info["cpu_numa_nodes"] = [p.name for p in nodes]
        except OSError as exc:
            info["affinity_error"] = str(exc)
    p = Path("/proc/cpuinfo")
    if p.exists():
        for line in p.read_text().splitlines():
            if line.startswith("model name"):
                info["cpu_model"] = line.partition(":")[2].strip()
                break
    # Pin before allocation for first-touch locality, but do not claim membind.
    return info


def timed(fn, M, C, cert, iterations):
    start = time.perf_counter_ns()
    cpu_start = time.process_time_ns()
    for _ in range(iterations):
        if not fn(M, C, cert):
            raise RuntimeError("valid synthetic certificate rejected")
    return {"wall_us": (time.perf_counter_ns() - start) / iterations / 1000.0,
            "cpu_us": (time.process_time_ns() - cpu_start) / iterations / 1000.0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--repetitions", type=int, default=9)
    parser.add_argument("--iterations", type=int, default=100)
    args = parser.parse_args()
    if args.repetitions < 1 or args.iterations < 1:
        parser.error("repetitions and iterations must be positive")
    env = environment()
    rng = np.random.default_rng(20260930)
    # name, source rows, packed words, pivot column, contributing rows
    shapes = [
        ("tiny_single", 8, 1, 0, 1),
        ("short_combination", 32, 8, 0, 3),
        ("medium_combination", 128, 64, 127, 31),
        ("long_early_pivot", 512, 128, 0, 511),
        ("long_late_pivot", 512, 128, 8191, 511),
        ("wide_late_pivot", 128, 2048, 131071, 127),
    ]
    results = []
    for name, rows, words, pivot, count in shapes:
        M = rng.bit_generator.random_raw((rows, words))
        prefix = pivot // 64 + 1
        M[:, :prefix] = 0
        M[0, pivot // 64] = np.uint64(1 << (pivot % 64))
        cert = ro.RankCertificate((pivot,), (0,), (tuple(range(count)),))
        C = words * 64
        before = hashlib.sha256(M.tobytes()).hexdigest()
        for _ in range(5):
            assert legacy_verify(M, C, cert) and ro.verify_certificate(M, C, cert)
        samples = {"baseline": [], "candidate": []}
        iterations = args.iterations * (10 if count < 8 else 1)
        funcs = [("baseline", legacy_verify), ("candidate", ro.verify_certificate)]
        for repetition in range(args.repetitions):
            for label, fn in funcs[::1 if repetition % 2 == 0 else -1]:
                samples[label].append(timed(fn, M, C, cert, iterations))
        if hashlib.sha256(M.tobytes()).hexdigest() != before:
            raise RuntimeError("input mutated")
        baseline = statistics.median(s["wall_us"] for s in samples["baseline"])
        candidate = statistics.median(s["wall_us"] for s in samples["candidate"])
        baseline_cpu = statistics.median(s["cpu_us"] for s in samples["baseline"])
        candidate_cpu = statistics.median(s["cpu_us"] for s in samples["candidate"])
        results.append({"name": name, "rows": rows, "columns": C,
                        "contributing_rows": count, "pivot": pivot,
                        "matrix_sha256": before, "samples_us": samples,
                        "iterations_per_sample": iterations,
                        "baseline_median_us": baseline,
                        "candidate_median_us": candidate,
                        "speedup": baseline / candidate,
                        "baseline_cpu_median_us": baseline_cpu,
                        "candidate_cpu_median_us": candidate_cpu,
                        "cpu_speedup": baseline_cpu / candidate_cpu})
    data = {"schema": "gf2.certificate_benchmark.v1",
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            "scope": "synthetic certificate verification only; no solve benchmark",
            "seed": 20260930, "baseline_blob": BASELINE_BLOB,
            "repetitions": args.repetitions, "iterations": args.iterations,
            "environment": env,
            "source_sha256": {
                str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in [Path(__file__).resolve(), Path(ro.__file__).resolve()]},
            "results": results}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(data, indent=2) + "\n")
    for row in results:
        print(f"{row['name']}: {row['baseline_median_us']:.3f} -> "
              f"{row['candidate_median_us']:.3f} us ({row['speedup']:.2f}x)")


if __name__ == "__main__":
    main()
