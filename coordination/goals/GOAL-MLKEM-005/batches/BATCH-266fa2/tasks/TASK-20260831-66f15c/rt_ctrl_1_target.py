#!/usr/bin/env python3
"""Fixed RT-CTRL-1 target worker with atomic progress records.

This file is intentionally a fresh, separately specified successor to the
incomplete BATCH-f9780d matched-pair runner.  It runs only the authorised
target cell (d=512, beta=55, seed formula unchanged, mpfr=100) under a
supervisor that owns the 21,600-second hard cap.  It makes no inference.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import signal
import sys
import time
from pathlib import Path

SEED_ROOT = 715923
Q = 3329
D = 512
BETA = 55
MPFR_BITS = 100


def atomic_json(path: Path, value: dict) -> None:
    """Write one complete state record, never a partly written final record."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, sort_keys=True, indent=2)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temp, path)
    try:
        directory_fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    except OSError:
        # Filesystem support is recorded by the supervisor; never fabricate it.
        pass


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", required=True, type=Path)
    parser.add_argument("--result", required=True, type=Path)
    parser.add_argument("--strategies", required=True, type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    state = {
        "schema": "crypto.autoresearch.rt_ctrl_1.progress.v1",
        "pid": os.getpid(),
        "d": D,
        "beta": BETA,
        "mpfr_bits": MPFR_BITS,
        "stage": "started",
        "monotonic_seconds": time.monotonic(),
        "wall_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "terminal": False,
    }

    def interrupted(signum: int, _frame: object) -> None:
        terminal = dict(state)
        terminal.update({
            "stage": "signal_received",
            "signal": signal.Signals(signum).name,
            "monotonic_seconds": time.monotonic(),
            "wall_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "terminal": True,
        })
        atomic_json(args.state, terminal)
        raise SystemExit(128 + signum)

    signal.signal(signal.SIGTERM, interrupted)
    signal.signal(signal.SIGINT, interrupted)
    atomic_json(args.state, state)

    if args.self_test:
        state.update({"stage": "self_test_waiting", "monotonic_seconds": time.monotonic()})
        atomic_json(args.state, state)
        # The supervisor deliberately terminates this before it completes.
        time.sleep(60)
        return 0

    try:
        import numpy as np
        from fpylll import BKZ, FPLLL, GSO, IntegerMatrix, LLL
        from fpylll.algorithms.bkz2 import BKZReduction

        state.update({"stage": "environment_ready", "strategies_sha256": sha256(args.strategies)})
        atomic_json(args.state, state)
        seed = int(np.random.default_rng([SEED_ROOT, 0, D, BETA, 0, 0]).integers(0, 2**31 - 1))
        FPLLL.set_random_seed(seed)
        state.update({"stage": "basis_generation", "seed_used": seed, "monotonic_seconds": time.monotonic()})
        atomic_json(args.state, state)
        matrix = IntegerMatrix.random(D, "qary", k=D // 2, q=Q)
        lll_started = time.monotonic()
        state.update({"stage": "outer_lll", "monotonic_seconds": lll_started})
        atomic_json(args.state, state)
        LLL.reduction(matrix)
        state.update({"stage": "gso", "outer_lll_elapsed_seconds": time.monotonic() - lll_started})
        atomic_json(args.state, state)
        FPLLL.set_precision(MPFR_BITS)
        gso = GSO.Mat(matrix, float_type="mpfr")
        gso.update_gso()
        reducer = LLL.Reduction(gso, flags=LLL.DEFAULT)
        params = BKZ.Param(block_size=BETA, strategies=str(args.strategies), flags=BKZ.AUTO_ABORT)
        bkz = BKZReduction(reducer)
        state.update({"stage": "bkz", "gso_float_type_used": gso.float_type, "monotonic_seconds": time.monotonic()})
        atomic_json(args.state, state)
        bkz_started = time.monotonic()
        bkz(params)
        result = dict(state)
        result.update({
            "status": "COMPLETED",
            "terminal": True,
            "stage": "completed",
            "bkz_elapsed_seconds": time.monotonic() - bkz_started,
            "tours": getattr(bkz, "tours", None),
            "monotonic_seconds": time.monotonic(),
        })
        atomic_json(args.result, result)
        atomic_json(args.state, result)
        return 0
    except Exception as exc:  # recorded observation, never reinterpreted here
        result = dict(state)
        result.update({
            "status": "ERROR",
            "error": f"{type(exc).__name__}: {exc}",
            "terminal": True,
            "stage": "exception",
            "monotonic_seconds": time.monotonic(),
        })
        atomic_json(args.result, result)
        atomic_json(args.state, result)
        return 0
    finally:
        try:
            from fpylll import FPLLL
            FPLLL.set_precision(53)
        except Exception:
            pass


if __name__ == "__main__":
    sys.exit(main())
