import sys, time
sys.path.insert(0, "experiments/EXP-ECDLP-bbb42f")
from driver.planted import find_anomalous_curve, walk_forward_chain
from driver.sampler import field_prime_for_bits
from driver.ecc import seeded_rng

p = field_prime_for_bits(20)
for restart in range(30):
    seed_rng = seeded_rng(20260902004, 20, "planted-origin", restart)
    t0 = time.time()
    try:
        special = find_anomalous_curve(p, seed_rng, max_attempts=100000)
    except RuntimeError as e:
        print(f"restart {restart}: find_anomalous_curve FAILED after {time.time()-t0:.2f}s: {e}")
        continue
    dt_find = time.time() - t0
    walk_rng = seeded_rng(20260902004, 20, "planted-walk", restart)
    t1 = time.time()
    try:
        chain = walk_forward_chain(special["a"], special["b"], p, 4, walk_rng)
        print(f"restart {restart}: SUCCESS find={dt_find:.2f}s walk={time.time()-t1:.4f}s attempt={special['attempt']}")
        break
    except RuntimeError as e:
        print(f"restart {restart}: find={dt_find:.2f}s walk dead-end after {time.time()-t1:.4f}s: {e}")
