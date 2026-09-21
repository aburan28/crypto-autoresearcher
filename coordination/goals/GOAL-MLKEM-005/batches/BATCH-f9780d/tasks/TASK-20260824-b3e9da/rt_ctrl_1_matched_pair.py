#!/usr/bin/env python3
"""RT-CTRL-1 as a MATCHED PAIR (route (c) of instrument_readiness_20260824.md).

Construction, seed formula, precision-before-GSO ordering and ROW_EXPO-free
mpfr GSO are reused VERBATIM from the pinned predecessor
  BATCH-0d5018/tasks/TASK-20260815-f14d3c/
    stage0_d512_beta5570_precision_bisection_and_reattempt.py
  sha256 58a1fdc21f45730789feeff69c6a6fd7c24bf4938be15d6e878afd246d0de485
(itself reusing BATCH-279acb/TASK-20260815-6e4c02's worker_main_cell).

THE ONE DELIBERATE DEPARTURE, and the reason this file exists: the predecessor
resolved BKZ strategies BY PATH (/usr/share/libfplll8/strategies/default.json)
and recorded no hash and no package version. That path does not exist in this
container and neither does fpylll 0.6.4's build-time fallback, so a
byte-identical re-run FAILS at BKZ.Param with `Cannot open strategies file.`
before any tour -- an instrument failure that must never be read as the
obstruction RT-CTRL-1 targets (AGENTS.md rule 3).

Route (c) therefore runs BOTH precisions in ONE invocation under ONE strategies
source, BOUND BY CONTENT (sha256 recorded below and the file archived beside
this script). The 75-bit cell is the contrast; the predecessor's 2502.74 s is a
cross-container sanity reference ONLY and is never the comparison.
"""
import hashlib, json, os, sys, time

SEED_ROOT = 715923                       # verbatim from the predecessor
Q = 3329
D = 512
BETA = 55
HERE = os.path.dirname(os.path.abspath(__file__))
STRATEGIES = os.path.join(HERE, "inputs", "fplll_strategies_default.json")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def worker_main_cell(d, beta, mpfr_bits):
    """Construction shape reused verbatim; only the strategies source differs."""
    import numpy as np
    from fpylll import IntegerMatrix, LLL, BKZ, FPLLL, GSO
    from fpylll.algorithms.bkz2 import BKZReduction

    result = {"d": d, "beta": beta, "mpfr_bits": mpfr_bits,
              "construction": "corrected_mpfr_no_row_expo"}
    try:
        seed = int(np.random.default_rng([SEED_ROOT, 0, d, beta, 0, 0])
                   .integers(0, 2 ** 31 - 1))
        FPLLL.set_random_seed(seed)
        result["seed_used"] = seed
        result["strategies_file_used"] = STRATEGIES
        result["strategies_sha256"] = sha256(STRATEGIES)

        A = IntegerMatrix.random(d, "qary", k=d // 2, q=Q)
        t0 = time.time()
        LLL.reduction(A)
        result["outer_lll_reduction_elapsed_seconds"] = time.time() - t0

        FPLLL.set_precision(mpfr_bits)          # BEFORE GSO.Mat construction
        M = GSO.Mat(A, float_type="mpfr")       # explicitly NO flags=GSO.ROW_EXPO
        M.update_gso()
        result["gso_float_type_used"] = M.float_type
        L = LLL.Reduction(M, flags=LLL.DEFAULT)

        par = BKZ.Param(block_size=beta, strategies=STRATEGIES,
                        flags=BKZ.AUTO_ABORT)
        bkz = BKZReduction(L)
        t1 = time.time()
        bkz(par)
        result["bkz_elapsed_seconds"] = time.time() - t1
        result["tours"] = getattr(bkz, "tours", None)
        b0 = A[0].norm()
        result["b0_norm"] = float(b0)
        result["root_hermite_factor"] = float(b0) ** (1.0 / d) / (Q ** 0.5) ** (1.0 / 1)
        result["status"] = "COMPLETED"
    except Exception as exc:                     # noqa: BLE001 - recorded, not raised
        result["status"] = "ERROR"
        result["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        try:
            from fpylll import FPLLL as _F
            _F.set_precision(53)
        except Exception:
            pass
    return result


def main():
    out = os.path.join(HERE, "rt_ctrl_1_matched_pair_results.json")
    cells = [{"mpfr_bits": 75, "role": "REFERENCE (the contrast)"},
             {"mpfr_bits": 100, "role": "RT-CTRL-1 (the target)"}]
    report = {"task": "TASK-20260824-b3e9da", "batch": "BATCH-f9780d",
              "goal": "GOAL-MLKEM-005", "d": D, "beta": BETA,
              "strategies_sha256": sha256(STRATEGIES),
              "predecessor_script_sha256":
                  "58a1fdc21f45730789feeff69c6a6fd7c24bf4938be15d6e878afd246d0de485",
              "cells": []}
    for c in cells:
        print(f"[{time.strftime('%H:%M:%S')}] cell mpfr_bits={c['mpfr_bits']} "
              f"({c['role']}) starting", flush=True)
        t = time.time()
        r = worker_main_cell(D, BETA, c["mpfr_bits"])
        r["role"] = c["role"]
        r["cell_wall_clock_seconds"] = time.time() - t
        report["cells"].append(r)
        print(f"[{time.strftime('%H:%M:%S')}] cell mpfr_bits={c['mpfr_bits']} "
              f"-> {r['status']} in {r['cell_wall_clock_seconds']:.1f}s", flush=True)
        with open(out, "w") as fh:
            json.dump(report, fh, indent=2)
    print(json.dumps(report, indent=2)[:1200], flush=True)
    print(f"\nwrote {out}", flush=True)


if __name__ == "__main__":
    main()
