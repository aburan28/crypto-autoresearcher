import time, os
import numpy as np
from fpylll import IntegerMatrix, LLL, FPLLL, GSO, BKZ

SEED_ROOT = 715923
d = 192

# --- Red Team's exact construction: isolated LLL step only, beta=40 label ---
seed_rt = int(np.random.default_rng([SEED_ROOT, 0, d, 40, 0, 0]).integers(0, 2**31 - 1))
FPLLL.set_random_seed(seed_rt)
A = IntegerMatrix.random(d, "qary", k=d // 2, q=3329)
t0 = time.time()
LLL.reduction(A)
lll_elapsed = time.time() - t0
M = GSO.Mat(A, flags=GSO.ROW_EXPO)
lll_obj = LLL.Reduction(M, flags=LLL.DEFAULT)
t1 = time.time()
try:
    lll_obj()
    print(f"RED TEAM construction (isolated LLL step only) at d=192: COMPLETED in {time.time()-t1:.4f}s (seed={seed_rt})")
except Exception as exc:
    print(f"RED TEAM construction (isolated LLL step only) at d=192: ERROR after {time.time()-t1:.4f}s: {type(exc).__name__}: {exc}")

# --- Validator's exact construction: full native BKZ.reduction tour, beta=10, arm_index=99 ---
strategies_path = "/usr/share/libfplll8/strategies/default.json"
if not os.path.exists(strategies_path):
    strategies_path = BKZ.DEFAULT_STRATEGY
seed_val = int(np.random.default_rng([SEED_ROOT, 0, d, 10, 99, 0]).integers(0, 2**31 - 1))
FPLLL.set_random_seed(seed_val)
A2 = IntegerMatrix.random(d, "qary", k=d // 2, q=3329)
par = BKZ.Param(block_size=10, strategies=strategies_path, flags=BKZ.AUTO_ABORT)
t2 = time.time()
try:
    BKZ.reduction(A2, par)
    print(f"VALIDATOR construction (full native BKZ.reduction tour) at d=192, beta=10: COMPLETED in {time.time()-t2:.4f}s (seed={seed_val})")
except Exception as exc:
    print(f"VALIDATOR construction (full native BKZ.reduction tour) at d=192, beta=10: ERROR after {time.time()-t2:.4f}s: {type(exc).__name__}: {exc}")
