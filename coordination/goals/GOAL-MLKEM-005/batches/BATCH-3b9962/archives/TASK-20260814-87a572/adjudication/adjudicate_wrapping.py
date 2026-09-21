import time
import numpy as np
from fpylll import IntegerMatrix, LLL, FPLLL, GSO, BKZ
from fpylll.algorithms.bkz2 import BKZReduction

SEED_ROOT = 715923

def test(d, beta, row_expo, mpfr_bits, label):
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
        bkz.lll_obj()
        elapsed = time.time() - t0
        FPLLL.set_precision(53)
        return {"label": label, "row_expo": row_expo, "status": "COMPLETED (just self.lll_obj(), not full tour)", "elapsed": elapsed}
    except Exception as exc:
        elapsed = time.time() - t0
        FPLLL.set_precision(53)
        return {"label": label, "row_expo": row_expo, "status": "ERROR", "error": f"{type(exc).__name__}: {exc}", "elapsed": elapsed}

d, beta = 256, 40
print("Testing bkz.lll_obj() (the exact call BKZReduction.__call__ makes at bkz.py:123) after constructing BKZReduction(L):")
print(test(d, beta, row_expo=True,  mpfr_bits=212, label="via BKZReduction(L).lll_obj(), WITH ROW_EXPO"))
print(test(d, beta, row_expo=False, mpfr_bits=212, label="via BKZReduction(L).lll_obj(), WITHOUT ROW_EXPO"))
