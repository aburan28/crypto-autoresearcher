import sys, time
sys.path.insert(0, "experiments/EXP-ECDLP-bbb42f")
from driver.planted import find_anomalous_curve
from driver.sampler import field_prime_for_bits
from driver.ecc import seeded_rng

p = field_prime_for_bits(24)
seed_rng = seeded_rng(20260902004, 24, "planted-origin", 0)
t0 = time.time()
found = find_anomalous_curve(p, seed_rng, max_attempts=30000)
print("found after", found["attempt"], "attempts, time=", time.time() - t0)
