import sys
sys.path.insert(0, "experiments/EXP-ECDLP-bbb42f")
from driver.isogeny3 import psi_3_roots
from driver.sampler import sample_unplanted_curves

p, accepted, tally, attempts = sample_unplanted_curves(20, master_seed=20260902001, count=20, k_max=6)
for c in accepted:
    roots = psi_3_roots(c["a"], c["b"], p)
    print(f"a={c['a']} b={c['b']} psi_3_roots={roots}")
