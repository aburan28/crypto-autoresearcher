import sys, time
import numpy as np
from fpylll import IntegerMatrix, LLL, FPLLL, GSO, BKZ
from fpylll.algorithms.bkz2 import BKZReduction

SEED_ROOT = 715923

def test(d, beta, row_expo, mpfr_bits):
    seed = int(np.random.default_rng([SEED_ROOT, 0, d, beta, 0, 0]).integers(0, 2**31 - 1))
    FPLLL.set_random_seed(seed)
    A = IntegerMatrix.random(d, "qary", k=d // 2, q=3329)
    LLL.reduction(A)
    FPLLL.set_precision(mpfr_bits)
    flags = GSO.ROW_EXPO if row_expo else 0
    M = GSO.Mat(A, flags=flags, float_type="mpfr")
    M.update_gso()
    L = LLL.Reduction(M, flags=LLL.DEFAULT)
    bkz = BKZReduction(L)
    strategies_path = "/usr/share/libfplll8/strategies/default.json"
    par = BKZ.Param(block_size=beta, strategies=strategies_path, flags=BKZ.AUTO_ABORT)
    t0 = time.time()
    try:
        bkz(par, tracer=True)
        elapsed = time.time() - t0
        FPLLL.set_precision(53)
        print(f"row_expo={row_expo}: COMPLETED in {elapsed:.3f}s")
    except Exception as exc:
        elapsed = time.time() - t0
        FPLLL.set_precision(53)
        print(f"row_expo={row_expo}: ERROR after {elapsed:.3f}s: {type(exc).__name__}: {exc}")

row_expo = sys.argv[1] == "true"
test(256, 40, row_expo=row_expo, mpfr_bits=212)
