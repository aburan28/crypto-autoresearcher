import sys, time
sys.path.insert(0, "experiments/EXP-ECDLP-bbb42f")
from driver.planted import find_anomalous_curve
from driver.sampler import field_prime_for_bits
from driver.ecc import seeded_rng

from driver.sampler import j_invariant
from driver.curve_order import compute_group_order

for bits in (24,):
    p = field_prime_for_bits(bits)
    seed_rng = seeded_rng(20260902004, bits, "planted-origin", 0)
    t0 = time.time()
    for attempt in range(2000):
        a = seed_rng.randrange(0, p)
        b = seed_rng.randrange(0, p)
        j = j_invariant(a, b, p)
        if j is None or j == 0 or j == (1728 % p):
            continue
        order_rng = seeded_rng(a, b, p, "order")
        t1 = time.time()
        try:
            N, ctr, npts = compute_group_order(a, b, p, order_rng)
        except RuntimeError:
            print(f"attempt {attempt}: RuntimeError, took {time.time()-t1:.3f}s")
            continue
        dt = time.time() - t1
        if dt > 0.5:
            print(f"attempt {attempt}: SLOW {dt:.3f}s N={N} points_used={npts}")
        if attempt % 200 == 0:
            print(f"attempt {attempt}, elapsed {time.time()-t0:.2f}s")
        if N == p:
            print(f"FOUND at attempt {attempt}, total time {time.time()-t0:.2f}s")
            break
    else:
        print(f"bits={bits}: not found in 2000 attempts, total time {time.time()-t0:.2f}s")
