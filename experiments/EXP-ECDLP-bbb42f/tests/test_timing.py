import random, sys, time
sys.path.insert(0, "experiments/EXP-ECDLP-bbb42f")
from driver.curve_order import compute_group_order
import sympy

for bits in (20, 24, 28):
    p = int(sympy.nextprime(1 << bits))
    rng = random.Random(42 + bits)
    t0 = time.time()
    N, ctr, npts = compute_group_order(p, 5, p, rng)
    dt = time.time() - t0
    print(f"bits={bits} p={p} N={N} time={dt:.4f}s field_mults={ctr.field_mults} points_used={npts}")
