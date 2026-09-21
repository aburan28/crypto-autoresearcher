import time, sys
import numpy as np
from fpylll import IntegerMatrix, LLL, FPLLL, GSO

SEED_ROOT = 715923

def build(d, beta, row_expo, mpfr_bits):
    seed = int(np.random.default_rng([SEED_ROOT, 0, d, beta, 0, 0]).integers(0, 2**31 - 1))
    FPLLL.set_random_seed(seed)
    A = IntegerMatrix.random(d, "qary", k=d // 2, q=3329)
    LLL.reduction(A)
    FPLLL.set_precision(mpfr_bits)
    flags = GSO.ROW_EXPO if row_expo else 0
    try:
        M = GSO.Mat(A, flags=flags, float_type="mpfr")
        M.update_gso()
        lll_obj = LLL.Reduction(M, flags=LLL.DEFAULT)
        t0 = time.time()
        lll_obj()
        elapsed = time.time() - t0
        FPLLL.set_precision(53)
        return {"row_expo": row_expo, "mpfr_bits": mpfr_bits, "status": "COMPLETED", "elapsed": elapsed}
    except Exception as exc:
        FPLLL.set_precision(53)
        return {"row_expo": row_expo, "mpfr_bits": mpfr_bits, "status": "ERROR", "error": f"{type(exc).__name__}: {exc}"}

d, beta = 256, 40
print(f"=== d={d} beta={beta}, isolated LLL step only ===")
print("WITHOUT ROW_EXPO (Red Team's construction):", build(d, beta, row_expo=False, mpfr_bits=212))
print("WITH ROW_EXPO (Validator's construction):   ", build(d, beta, row_expo=True, mpfr_bits=212))
