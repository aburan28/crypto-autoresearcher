"""DEVELOPMENT ONLY. Times the heavy stages on synthetic instances drawn from
this task's own dev seed (NOT the blind inputs, NOT any specification seed).
It never reads blind-inputs.json."""
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import system as S  # noqa: E402

DEV_SEED = 0xDE7A2C
rng = np.random.Generator(np.random.PCG64(DEV_SEED))
B = int(rng.integers(1, 1 << 17))
shape = S.Shape(4)
print("shape", shape.R, shape.C, shape.W)
for trial in range(int(sys.argv[1]) if len(sys.argv) > 1 else 1):
    xR = int(rng.integers(512, 1 << 17))
    t0 = time.time()
    coef = S.descend(B, xR)
    t1 = time.time()
    eqs = S.equations(coef)
    M = S.macaulay(shape, eqs)
    t2 = time.time()
    cp = S.column_pass(M, shape.C, keep_ops=True)
    t3 = time.time()
    leads, Z = S.row_pass(M)
    t4 = time.time()
    rank = len(cp["steps"])
    print(f"trial {trial}: descend {t1-t0:.3f}s macaulay {t2-t1:.3f}s colpass {t3-t2:.3f}s "
          f"rowpass {t4-t3:.3f}s rank {rank} |Z| {len(Z)} sumX {cp['sumX']} "
          f"cpass_ok {sorted(c for _, c in cp['steps']) == leads and len(Z) == shape.R - rank} "
          f"resid {cp['residual_nonzero_unused_rows']}")
    if trial == 0:
        E0 = S.equations(S.descend(B, 0))
        blocks = [S.macaulay(shape, E0)] + [
            S.macaulay(shape, S.equations(S.coef_xor(S.descend(B, 1 << j), S.descend(B, 0))))
            for j in range(17)]
        t5 = time.time()
        e = S.replay(blocks, cp["ops"])
        t6 = time.time()
        print(f"  replay 18 blocks {t6-t5:.3f}s steps {e.shape[0]}")
