#!/usr/bin/env python3
"""J1 PART A -- Validator TASK-20260826-9605ae independent derivation.

Cell: d=64, beta=25, mpfr_bits=53, q=3329.
Construction transcribed from the PINNED PREDECESSOR
  coordination/goals/GOAL-MLKEM-005/batches/BATCH-f9780d/tasks/TASK-20260824-b3e9da/
    rt_ctrl_1_matched_pair.py   sha256 bc0524ee...b25035, worker_main_cell lines 42-79,
evaluated at d=64/beta=25/mpfr_bits=53 (the predecessor's module-level D=512, BETA=55
are NOT used).  NOT transcribed from the producer's v2 file, which this script does not
import, read or reference.

STRATEGIES ARE PINNED BY CONTENT.  Absolute path, sha256 verified before use, abort on
mismatch.  Every number this script emits carries the strategies sha256 it was produced
under (or the explicit statement that no strategies argument was passed).

MY DEFINITION OF 'NUMBER OF TOURS', stated before looking at the instrument:
  the number of iterations of the `while True:` loop in
  fpylll.algorithms.bkz.BKZReduction.__call__ that ran to completion, i.e. the number of
  invocations of `self.tour(...)` made BY THAT LOOP (depth 0), equivalently the value of
  the loop counter `i` when the loop breaks.  Recursive `self.tour(...)` invocations made
  from fpylll.algorithms.bkz2.BKZReduction.svp_preprocessing (one per entry of
  params.strategies[block_size].preprocessing_block_sizes, per svp_reduction) are NOT
  tours under this definition; they are preprocessing sub-calls.
MY ROUTE: a subclass of the bkz2 BKZReduction that maintains a re-entrancy depth counter
around `tour` and increments the tour count only on depth-0 entry.  It delegates to
super() and changes no arithmetic.  The all-calls counter is reported alongside so the
two quantities can be seen to differ (or not) on this cell.
"""
import argparse
import hashlib
import json
import os
import sys
import time

STRATEGIES_ABS = ("/home/user/crypto-autoresearcher/coordination/goals/GOAL-MLKEM-005/"
                  "batches/BATCH-f9780d/tasks/TASK-20260824-b3e9da/inputs/"
                  "fplll_strategies_default.json")
STRATEGIES_EXPECTED_SHA256 = "f516b0a6f0c580cff72e1e2c3562c44dc6f17e8f99613e9e4020e35481b27a18"

SEED_ROOT = 715923
Q = 3329


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def run_cell(d, beta, mpfr_bits, use_strategies, use_tracer):
    import numpy as np
    from fpylll import IntegerMatrix, LLL, BKZ, FPLLL, GSO
    from fpylll.algorithms.bkz2 import BKZReduction

    class CountingBKZ(BKZReduction):
        def __init__(self, A):
            BKZReduction.__init__(self, A)
            self._depth = 0
            self.top_level_tours = 0
            self.all_tour_calls = 0

        def tour(self, params, min_row=0, max_row=-1, tracer=None):
            self.all_tour_calls += 1
            if self._depth == 0:
                self.top_level_tours += 1
            self._depth += 1
            try:
                if tracer is None:
                    return BKZReduction.tour(self, params, min_row, max_row)
                return BKZReduction.tour(self, params, min_row, max_row, tracer)
            finally:
                self._depth -= 1

    out = {"d": d, "beta": beta, "mpfr_bits": mpfr_bits, "q": Q,
           "construction": "corrected_mpfr_no_row_expo",
           "transcribed_from": "BATCH-f9780d/TASK-20260824-b3e9da/"
                               "rt_ctrl_1_matched_pair.py::worker_main_cell L42-79",
           "use_strategies": use_strategies, "tracer_arg": use_tracer,
           "pid": os.getpid()}
    try:
        seed = int(np.random.default_rng([SEED_ROOT, 0, d, beta, 0, 0])
                   .integers(0, 2 ** 31 - 1))
        FPLLL.set_random_seed(seed)
        out["seed_used"] = seed

        if use_strategies:
            actual = sha256(STRATEGIES_ABS)
            if actual != STRATEGIES_EXPECTED_SHA256:
                raise SystemExit("ABORT: strategies sha256 mismatch %s" % actual)
            out["strategies_file_used"] = STRATEGIES_ABS
            out["strategies_sha256"] = actual
        else:
            out["strategies_file_used"] = None
            out["strategies_sha256"] = None
            out["strategies_note"] = "NO strategies= argument passed to BKZ.Param"

        A = IntegerMatrix.random(d, "qary", k=d // 2, q=Q)
        t0 = time.time()
        LLL.reduction(A)
        out["outer_lll_reduction_elapsed_seconds"] = time.time() - t0

        FPLLL.set_precision(mpfr_bits)              # BEFORE GSO.Mat construction
        M = GSO.Mat(A, float_type="mpfr")           # explicitly NO flags=GSO.ROW_EXPO
        M.update_gso()
        out["gso_float_type_used"] = M.float_type
        L = LLL.Reduction(M, flags=LLL.DEFAULT)

        if use_strategies:
            par = BKZ.Param(block_size=beta, strategies=STRATEGIES_ABS,
                            flags=BKZ.AUTO_ABORT)
        else:
            par = BKZ.Param(block_size=beta, flags=BKZ.AUTO_ABORT)
        out["strategies_preprocessing_block_sizes_at_beta"] = list(
            par.strategies[beta].preprocessing_block_sizes)

        bkz = CountingBKZ(L)
        t1 = time.time()
        if use_tracer:
            bkz(par, tracer=True)
        else:
            bkz(par)
        out["bkz_elapsed_seconds"] = time.time() - t1

        out["TOURS_top_level_loop_iterations"] = bkz.top_level_tours
        out["tour_calls_including_preprocessing"] = bkz.all_tour_calls
        out["predecessor_getattr_bkz_tours"] = getattr(bkz, "tours", None)
        out["bkz_trace_is_none"] = bkz.trace is None
        if bkz.trace is not None:
            kids = [c.label for c in bkz.trace.children]
            out["trace_root_label"] = bkz.trace.label
            out["trace_root_child_labels"] = [list(k) if isinstance(k, tuple) else k
                                              for k in kids]
            out["TOURS_trace_root_children_labelled_tour"] = sum(
                1 for k in kids if (isinstance(k, tuple) and k[0] == "tour"))

        b0_row = A[0].norm()
        out["B0_from_matrix_row0_norm"] = float(b0_row)
        r00 = M.get_r(0, 0)
        out["gso_r00_raw"] = float(r00)
        out["B0_from_gso_r00_sqrt"] = float(r00) ** 0.5
        M.update_gso()
        r00b = M.get_r(0, 0)
        out["B0_from_gso_r00_sqrt_after_update_gso"] = float(r00b) ** 0.5
        out["status"] = "COMPLETED"
    except SystemExit:
        raise
    except Exception as exc:  # recorded, not raised
        out["status"] = "ERROR"
        out["error"] = "%s: %s" % (type(exc).__name__, exc)
    finally:
        try:
            from fpylll import FPLLL as _F
            _F.set_precision(53)
        except Exception:
            pass
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--d", type=int, default=64)
    ap.add_argument("--beta", type=int, default=25)
    ap.add_argument("--mpfr-bits", type=int, default=53)
    ap.add_argument("--no-strategies", action="store_true")
    ap.add_argument("--tracer", action="store_true")
    a = ap.parse_args()
    r = run_cell(a.d, a.beta, a.mpfr_bits, not a.no_strategies, a.tracer)
    r["interpreter"] = sys.executable
    r["python_version"] = sys.version
    import fpylll
    r["fpylll_version"] = fpylll.__version__
    print(json.dumps(r, indent=2))
