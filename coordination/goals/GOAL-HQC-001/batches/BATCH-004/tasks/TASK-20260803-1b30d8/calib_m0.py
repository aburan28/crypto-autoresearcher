#!/usr/bin/env python3
"""CALIB-M0 -- generic machine-constant microbenchmarks (array + RNG primitives).

TASK-20260803-1b30d8 / GOAL-HQC-001 / BATCH-004.

PURPOSE
-------
BATCH-003's feasibility analysis
(coordination/goals/GOAL-HQC-001/batches/BATCH-003/tasks/TASK-20260803-c470c0/
feasibility_analysis.md, section 9.1) cites `calib_m0.py` and `calib_m0b.py` as
the source of every machine constant in its cost model.  Neither script existed
in the repository (validator DEF-3; DEC-20260802-d94a64 D-6).  This file is the
reconstruction of the first of the two.

It measures ONLY generic machine primitives.  There is no HQC object anywhere in
this file: no ring, no fixed-weight vector, no code, no decoder, no failure
indicator, no HQC-derived array length.  Every size below is a round power of two
or a round multiple of 1024, chosen so that no HQC parameter leaks into a
calibration number.  Applying these constants to HQC-shaped parameter sets is
done in `calib_m0b.py`'s `rederivation` block and is labelled as derivation, not
as measurement.

CONSTANTS PRODUCED (units as consumed by the section 9.2 cost model)
--------------------------------------------------------------------
  R_add   int16 elementwise add/sub throughput, cache-resident   [elements/s]
  R_add_membound  the same at a memory-resident working set      [elements/s]
  R_xor64 uint64 elementwise XOR throughput, cache-resident      [words/s]
  R_rng   PCG64 uint64 generation rate                           [words/s]

R_rng is reported in THREE variants because the phrase "PCG64 uint64 generation"
in section 9.1 does not determine a measurement, and the original script does not
exist to disambiguate it.  All three are reported; none is silently preferred.

METHOD
------
Each measurement runs `--reps` independent timed repetitions.  A repetition times
`inner` back-to-back applications of the primitive and divides, so that the timer
resolution and the per-call Python overhead are amortised in a stated way rather
than an implicit one.  `inner` is auto-calibrated so a repetition takes about
`--target-ms` milliseconds.  Warmup repetitions are discarded.  Every repetition's
result is retained in the JSON, so a reviewer can recompute any statistic and can
see the spread; the summary reports median, mean, stdev, cv, min, max, p10, p90.

The MEDIAN is the point estimate.  The minimum is reported beside it because on a
shared container the minimum is the closest thing to an uncontended machine and
the median is the closest thing to what a batch of work will actually see.

DETERMINISM
-----------
Timings are not deterministic and are not claimed to be.  What is deterministic:
the operand data (seeded PCG64, seed recorded), the sizes, the repetition counts,
and the reduction from repetitions to summary statistics.  Re-running reproduces
the procedure exactly and the numbers to within the reported spread.

USAGE
-----
  python3 calib_m0.py --out calibration_results.json
  python3 calib_m0.py --smoke --out /tmp/smoke.json     # fast self-test

Exit status is 0 on success.  The script writes/updates the key
`calibration.m0` of the output JSON and leaves all other keys untouched.
"""

from __future__ import annotations

import argparse
import gc
import json
import os
import platform
import statistics
import subprocess
import sys
import time

import numpy as np

SCHEMA = "hqc-batch004-calibration/v1"
BLOCK = "m0"

# ---------------------------------------------------------------------------
# generic helpers (duplicated verbatim in calib_m0b.py so each script stands
# alone and neither import creates a __pycache__ directory)
# ---------------------------------------------------------------------------


def _run(cmd):
    try:
        return subprocess.run(
            cmd, capture_output=True, text=True, timeout=30, check=False
        ).stdout.strip()
    except Exception as exc:  # pragma: no cover - environment probing only
        return f"<unavailable: {exc}>"


def environment_block(argv, seed):
    cpu_model = ""
    cache = ""
    try:
        with open("/proc/cpuinfo") as fh:
            for line in fh:
                if line.startswith("model name") and not cpu_model:
                    cpu_model = line.split(":", 1)[1].strip()
                if line.startswith("cache size") and not cache:
                    cache = line.split(":", 1)[1].strip()
    except OSError:
        pass
    mem_total = ""
    try:
        with open("/proc/meminfo") as fh:
            mem_total = fh.readline().split(":", 1)[1].strip()
    except OSError:
        pass
    git_commit = _run(["git", "rev-parse", "HEAD"])
    git_dirty_raw = _run(["git", "status", "--porcelain"])
    return {
        "recorded_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "command": "python3 " + " ".join(argv),
        "cwd": os.getcwd(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "python_version": sys.version.split()[0],
        "python_build": " ".join(platform.python_build()),
        "numpy_version": np.__version__,
        "cpu_model": cpu_model,
        "cpu_cache_size_reported": cache,
        "os_cpu_count": os.cpu_count(),
        "sched_affinity_count": len(os.sched_getaffinity(0))
        if hasattr(os, "sched_getaffinity")
        else None,
        "meminfo_MemTotal": mem_total,
        "loadavg_at_start": os.getloadavg(),
        "git_commit": git_commit,
        "git_dirty_tree": bool(git_dirty_raw),
        "git_dirty_paths": git_dirty_raw.splitlines()[:20],
        "seed": seed,
        "numpy_threading_note": (
            "elementwise numpy ufuncs used here are single-threaded; no BLAS call "
            "is made, so OMP/MKL thread counts do not affect these numbers"
        ),
    }


def summarize(samples, unit):
    """Reduce a list of per-repetition measurements to a summary + full detail."""
    s = sorted(samples)
    n = len(s)

    def pct(p):
        if n == 1:
            return s[0]
        idx = p * (n - 1) / 100.0
        lo = int(idx)
        hi = min(lo + 1, n - 1)
        frac = idx - lo
        return s[lo] * (1 - frac) + s[hi] * frac

    mean = statistics.fmean(s)
    stdev = statistics.stdev(s) if n > 1 else 0.0
    return {
        "unit": unit,
        "n_reps": n,
        "median": statistics.median(s),
        "mean": mean,
        "stdev": stdev,
        "cv": (stdev / mean) if mean else None,
        "min": s[0],
        "max": s[-1],
        "p10": pct(10),
        "p90": pct(90),
        "spread_max_over_min": (s[-1] / s[0]) if s[0] else None,
        "samples": s,
    }


def time_reps(call, work_units, reps, warmup, target_ms, max_inner=1 << 22):
    """Time `call()` in batches, returning per-repetition throughput/latency.

    `call(inner)` must perform `inner` applications of the primitive and return
    something that keeps the compiler/interpreter from eliding the work.
    Returns (per_rep_seconds_per_unit, inner_used).
    """
    # auto-calibrate `inner` so a repetition lasts about target_ms
    inner = 1
    while inner < max_inner:
        t0 = time.perf_counter_ns()
        call(inner)
        dt_ms = (time.perf_counter_ns() - t0) / 1e6
        if dt_ms >= target_ms:
            break
        # grow, but never by more than 8x at a time
        growth = max(2.0, min(8.0, (target_ms / dt_ms) if dt_ms > 0 else 8.0))
        inner = max(inner + 1, int(inner * growth))
    inner = min(inner, max_inner)

    for _ in range(warmup):
        call(inner)

    per_rep = []
    gc_was_enabled = gc.isenabled()
    gc.disable()
    try:
        for _ in range(reps):
            t0 = time.perf_counter_ns()
            call(inner)
            dt = (time.perf_counter_ns() - t0) / 1e9
            per_rep.append(dt / (inner * work_units))
    finally:
        if gc_was_enabled:
            gc.enable()
    return per_rep, inner


# ---------------------------------------------------------------------------
# measurements
# ---------------------------------------------------------------------------


def bench_elementwise(rng, dtype, op, sizes, reps, warmup, target_ms):
    """Elementwise binary ufunc throughput over a size sweep. Generic sizes only."""
    out = {}
    for n in sizes:
        if np.issubdtype(dtype, np.signedinteger):
            a = rng.integers(-2000, 2000, size=n, dtype=dtype)
            b = rng.integers(-2000, 2000, size=n, dtype=dtype)
        else:
            a = rng.integers(0, 2**63, size=n, dtype=np.uint64).astype(dtype)
            b = rng.integers(0, 2**63, size=n, dtype=np.uint64).astype(dtype)
        c = np.empty(n, dtype=dtype)

        def call(inner, a=a, b=b, c=c):
            for _ in range(inner):
                op(a, b, out=c)
            return c

        per_rep_s_per_elem, inner = time_reps(
            call, work_units=n, reps=reps, warmup=warmup, target_ms=target_ms
        )
        thr = [1.0 / t for t in per_rep_s_per_elem]
        out[str(n)] = {
            "n_elements": n,
            "bytes_per_array": n * np.dtype(dtype).itemsize,
            "working_set_bytes": 3 * n * np.dtype(dtype).itemsize,
            "inner_iterations_per_rep": inner,
            "throughput": summarize(thr, "elements_per_second"),
        }
    return out


def bench_rng(seed, sizes, reps, warmup, target_ms, scalar_draws):
    """PCG64 uint64 generation, three variants. Generic: no rejection, no structure."""
    res = {}

    # (a) raw PCG64 output words, bulk
    bulk_raw = {}
    for n in sizes:
        bg = np.random.PCG64(seed)

        def call(inner, bg=bg, n=n):
            x = None
            for _ in range(inner):
                x = bg.random_raw(n)
            return x

        per_rep, inner = time_reps(
            call, work_units=n, reps=reps, warmup=warmup, target_ms=target_ms
        )
        bulk_raw[str(n)] = {
            "n_words": n,
            "inner_iterations_per_rep": inner,
            "throughput": summarize([1.0 / t for t in per_rep], "words_per_second"),
        }
    res["bulk_random_raw"] = bulk_raw

    # (b) Generator.integers full-range uint64, bulk (the ordinary user-level API)
    bulk_int = {}
    for n in sizes:
        g = np.random.Generator(np.random.PCG64(seed))

        def call(inner, g=g, n=n):
            x = None
            for _ in range(inner):
                x = g.integers(0, 2**64, size=n, dtype=np.uint64, endpoint=False)
            return x

        per_rep, inner = time_reps(
            call, work_units=n, reps=reps, warmup=warmup, target_ms=target_ms
        )
        bulk_int[str(n)] = {
            "n_words": n,
            "inner_iterations_per_rep": inner,
            "throughput": summarize([1.0 / t for t in per_rep], "words_per_second"),
        }
    res["bulk_generator_integers"] = bulk_int

    # (c) scalar draws from a Python loop: one uint64 per Python-level call.
    #     This is the regime any per-index sampler operates in, and it is
    #     dominated by interpreter and call overhead rather than by PCG64.
    g = np.random.Generator(np.random.PCG64(seed))

    def call_scalar(inner, g=g):
        x = 0
        for _ in range(inner):
            x = g.integers(0, 2**64, dtype=np.uint64, endpoint=False)
        return x

    per_rep, inner = time_reps(
        call_scalar,
        work_units=1,
        reps=reps,
        warmup=warmup,
        target_ms=target_ms,
        max_inner=scalar_draws,
    )
    res["scalar_python_loop"] = {
        "n_words": 1,
        "inner_iterations_per_rep": inner,
        "throughput": summarize([1.0 / t for t in per_rep], "words_per_second"),
        "note": (
            "one Python-level call per 64-bit word; measures interpreter + numpy "
            "dispatch overhead, not the PCG64 stream rate"
        ),
    }
    return res


def aggregate_sweep(sweep, how):
    """Collapse a size sweep to one constant. `how` in {min_of_medians, median_of_medians, max_of_medians}."""
    meds = {k: v["throughput"]["median"] for k, v in sweep.items()}
    if how == "min_of_medians":
        k = min(meds, key=meds.get)
    elif how == "max_of_medians":
        k = max(meds, key=meds.get)
    else:
        vals = sorted(meds.values())
        target = vals[len(vals) // 2]
        k = [kk for kk, vv in meds.items() if vv == target][0]
    return {
        "rule": how,
        "size_selected": int(k),
        "value": meds[k],
        "per_size_medians": {int(kk): vv for kk, vv in meds.items()},
        "sweep_min_median": min(meds.values()),
        "sweep_max_median": max(meds.values()),
    }


# ---------------------------------------------------------------------------


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", required=True, help="JSON file to write/update")
    ap.add_argument("--seed", type=int, default=20260803)
    ap.add_argument("--reps", type=int, default=15)
    ap.add_argument("--warmup", type=int, default=3)
    ap.add_argument("--target-ms", type=float, default=30.0)
    ap.add_argument("--smoke", action="store_true", help="fast self-test, not a measurement")
    args = ap.parse_args(argv)

    reps = 3 if args.smoke else args.reps
    warmup = 1 if args.smoke else args.warmup
    target_ms = 3.0 if args.smoke else args.target_ms

    # Generic sizes only: powers of two. No HQC quantity appears here.
    # `cache_sizes` reproduces the range BATCH-003 section 9.1 states it used
    # (N = 4096 .. 65536) so the comparison is like-for-like.
    cache_sizes = [4096, 8192, 16384, 32768, 65536]
    # `small_sizes` is an ADDITION, not in BATCH-003's table. A cost model that
    # divides a total element count by one throughput implicitly assumes the
    # work arrives in arrays large enough to reach that throughput. Any transform
    # whose natural unit is a short vector runs in the per-call-overhead regime
    # instead. Measuring it is the only way to say how large that gap is.
    small_sizes = [64, 128, 256, 512, 1024, 2048]
    membound_sizes = [1 << 24]
    # RNG sweep spans four decades of BATCH SIZE on purpose: a generator's
    # words/s is strongly batch-size dependent (per-call overhead amortises),
    # so a single number is not a property of the machine unless the batch size
    # is stated with it. All sizes are powers of two; none comes from HQC.
    rng_sizes = [64, 256, 1024, 4096, 65536, 1 << 20]
    scalar_draws = 2000 if args.smoke else 200000
    if args.smoke:
        cache_sizes = [4096, 65536]
        small_sizes = [128, 1024]
        rng_sizes = [64, 4096, 65536]

    env = environment_block(["calib_m0.py"] + argv, args.seed)
    rng = np.random.Generator(np.random.PCG64(args.seed))

    t_start = time.time()
    block = {
        "script": "calib_m0.py",
        "block": BLOCK,
        "smoke": bool(args.smoke),
        "environment": env,
        "parameters": {
            "seed": args.seed,
            "reps": reps,
            "warmup": warmup,
            "target_ms": target_ms,
            "cache_resident_sizes": cache_sizes,
            "small_array_sizes": small_sizes,
            "memory_bound_sizes": membound_sizes,
            "rng_sizes": rng_sizes,
            "scalar_draw_cap": scalar_draws,
        },
        "hqc_quantities_used": [],
        "measurements": {},
    }

    print("[m0] int16 add, cache-resident sweep ...", flush=True)
    block["measurements"]["int16_add_cache"] = bench_elementwise(
        rng, np.int16, np.add, cache_sizes, reps, warmup, target_ms
    )
    print("[m0] int16 sub, cache-resident sweep ...", flush=True)
    block["measurements"]["int16_sub_cache"] = bench_elementwise(
        rng, np.int16, np.subtract, cache_sizes, reps, warmup, target_ms
    )
    print("[m0] int16 add, small-array (per-call overhead) sweep ...", flush=True)
    block["measurements"]["int16_add_small"] = bench_elementwise(
        rng, np.int16, np.add, small_sizes, reps, warmup, target_ms
    )
    print("[m0] int16 add, memory-bound ...", flush=True)
    block["measurements"]["int16_add_membound"] = bench_elementwise(
        rng, np.int16, np.add, membound_sizes, max(3, reps // 2), 1, target_ms
    )
    print("[m0] uint64 xor, cache-resident sweep ...", flush=True)
    block["measurements"]["uint64_xor_cache"] = bench_elementwise(
        rng, np.uint64, np.bitwise_xor, cache_sizes, reps, warmup, target_ms
    )
    print("[m0] PCG64 uint64 generation, three variants ...", flush=True)
    block["measurements"]["pcg64"] = bench_rng(
        args.seed, rng_sizes, reps, warmup, target_ms, scalar_draws
    )

    # ---- the constants the section 9.2 cost model consumes -----------------
    add_cache = block["measurements"]["int16_add_cache"]
    sub_cache = block["measurements"]["int16_sub_cache"]
    xor_cache = block["measurements"]["uint64_xor_cache"]
    pcg = block["measurements"]["pcg64"]

    block["constants"] = {
        "R_add": {
            "unit": "elements_per_second",
            "definition": (
                "int16 elementwise add throughput, cache-resident, taken at the "
                "SLOWEST size of the sweep (conservative end), median over reps"
            ),
            "aggregate": aggregate_sweep(add_cache, "min_of_medians"),
            "alternative_optimistic_aggregate": aggregate_sweep(
                add_cache, "max_of_medians"
            ),
            "subtract_cross_check": aggregate_sweep(sub_cache, "min_of_medians"),
        },
        "R_add_small_arrays": {
            "unit": "elements_per_second",
            "definition": (
                "int16 elementwise add throughput at SHORT array lengths, where "
                "per-call dispatch overhead rather than memory bandwidth sets the "
                "rate. Not present in BATCH-003's table; measured here because a "
                "cost model that divides a total element count by the large-array "
                "R_add silently assumes short-vector work runs at the same rate."
            ),
            "aggregate": aggregate_sweep(
                block["measurements"]["int16_add_small"], "min_of_medians"
            ),
            "per_size_medians": {
                int(k): v["throughput"]["median"]
                for k, v in block["measurements"]["int16_add_small"].items()
            },
        },
        "R_add_membound": {
            "unit": "elements_per_second",
            "definition": "int16 elementwise add throughput at a 2^24-element working set",
            "aggregate": aggregate_sweep(
                block["measurements"]["int16_add_membound"], "min_of_medians"
            ),
        },
        "R_xor64": {
            "unit": "words_per_second",
            "definition": "uint64 elementwise XOR throughput, cache-resident, slowest size",
            "aggregate": aggregate_sweep(xor_cache, "min_of_medians"),
        },
        "R_rng_variants": {
            "unit": "words_per_second",
            "definition": (
                "three distinct readings of 'PCG64 uint64 generation'; the phrase "
                "in BATCH-003 section 9.1 does not determine which, and the "
                "original script does not exist to disambiguate it"
            ),
            "bulk_random_raw": aggregate_sweep(pcg["bulk_random_raw"], "min_of_medians"),
            "bulk_generator_integers": aggregate_sweep(
                pcg["bulk_generator_integers"], "min_of_medians"
            ),
            "scalar_python_loop": {
                "rule": "single configuration",
                "value": pcg["scalar_python_loop"]["throughput"]["median"],
            },
        },
    }
    block["elapsed_seconds"] = time.time() - t_start
    block["loadavg_at_end"] = os.getloadavg()

    # ---- merge into the shared results file --------------------------------
    doc = {}
    if os.path.exists(args.out):
        with open(args.out) as fh:
            doc = json.load(fh)
    doc.setdefault("schema", SCHEMA)
    doc.setdefault("task", "TASK-20260803-1b30d8")
    doc.setdefault("goal", "GOAL-HQC-001")
    doc.setdefault("batch", "BATCH-004")
    doc.setdefault(
        "note",
        "Keys under `calibration` are machine constants measured on generic "
        "workloads and contain NO HQC quantity. Keys under `rederivation` apply "
        "those constants to published/BATCH-003 parameter sets and are "
        "derivation, not measurement.",
    )
    doc.setdefault("calibration", {})
    doc["calibration"][BLOCK] = block
    tmp = args.out + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(doc, fh, indent=2, sort_keys=False)
        fh.write("\n")
    os.replace(tmp, args.out)

    print(f"[m0] wrote calibration.{BLOCK} to {args.out} "
          f"({block['elapsed_seconds']:.1f} s)", flush=True)
    c = block["constants"]
    print(f"[m0] R_add            = {c['R_add']['aggregate']['value']:.4g} elem/s "
          f"(sweep {c['R_add']['aggregate']['sweep_min_median']:.3g} .. "
          f"{c['R_add']['aggregate']['sweep_max_median']:.3g})")
    print(f"[m0] R_add_membound   = {c['R_add_membound']['aggregate']['value']:.4g} elem/s")
    print(f"[m0] R_xor64          = {c['R_xor64']['aggregate']['value']:.4g} word/s")
    print(f"[m0] R_rng raw bulk   = {c['R_rng_variants']['bulk_random_raw']['value']:.4g} word/s")
    print(f"[m0] R_rng integers   = {c['R_rng_variants']['bulk_generator_integers']['value']:.4g} word/s")
    print(f"[m0] R_rng scalar     = {c['R_rng_variants']['scalar_python_loop']['value']:.4g} word/s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
