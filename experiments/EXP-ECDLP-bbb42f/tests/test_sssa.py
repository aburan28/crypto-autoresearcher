import sys, random
sys.path.insert(0, "experiments/EXP-ECDLP-bbb42f")
from driver.curve_order import compute_group_order
from driver.ecc import scalar_mult, random_point
from driver.sssa import sssa_solve
from sympy import isprime, nextprime

def find_anomalous_curve(p, seed):
    rng = random.Random(seed)
    for _ in range(20000):
        a = rng.randrange(0, p)
        b = rng.randrange(0, p)
        if (4 * a**3 + 27 * b * b) % p == 0:
            continue
        order_rng = random.Random(repr((seed, a, b)))
        try:
            N, ctr, npts = compute_group_order(a, b, p, order_rng)
        except RuntimeError:
            continue
        if N == p:
            return a, b, N
    return None

fails = 0
tests = 0
import time
for p in [97, 1009, 10007, 100003, 1048583, int(nextprime(1 << 24)), int(nextprime(1 << 28))]:
    p = int(p)
    found = find_anomalous_curve(p, seed=p)
    if found is None:
        print(f"p={p}: no anomalous curve found in search budget")
        continue
    a, b, N = found
    rng = random.Random(p + 1)
    P = random_point(a, b, p, rng)
    while P[1] == 0:
        P = random_point(a, b, p, rng)
    k_true = rng.randrange(1, p)
    Q = scalar_mult(k_true, P, a, p)
    if Q is None or Q[1] == 0:
        continue
    tests += 1
    try:
        t0 = time.time()
        k_computed, diag = sssa_solve(P[0], P[1], Q[0], Q[1], a, b, p)
        dt = time.time() - t0
    except Exception as e:
        print(f"p={p} EXCEPTION: {e}")
        fails += 1
        continue
    ok = (k_computed == k_true)
    print(f"p={p} a={a} b={b} N={N} k_true={k_true} k_computed={k_computed} OK={ok} time={dt:.3f}s")
    if not ok:
        fails += 1

print(f"tests={tests} fails={fails}")
