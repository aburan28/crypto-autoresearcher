import sys
sys.path.insert(0, "experiments/EXP-ECDLP-bbb42f")
from driver.isogeny3 import psi_3_roots
from driver.sampler import sample_unplanted_curves

p, accepted, tally, attempts = sample_unplanted_curves(28, master_seed=20260902003, count=20, k_max=6)
has_root = 0
for c in accepted:
    roots = psi_3_roots(c["a"], c["b"], p)
    if roots:
        has_root += 1
    N = c["N"]
    t = p + 1 - N
    print(f"N={N} t mod3={t%3} psi_3_roots={roots}")
print(f"has_root={has_root}/{len(accepted)}")
