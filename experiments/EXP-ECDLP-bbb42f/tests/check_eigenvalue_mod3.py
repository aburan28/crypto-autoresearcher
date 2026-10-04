import sys
sys.path.insert(0, "experiments/EXP-ECDLP-bbb42f")
from driver.sampler import sample_unplanted_curves

p, accepted, tally, attempts = sample_unplanted_curves(20, master_seed=20260902001, count=20, k_max=6)
print("p mod 3 =", p % 3)
for c in accepted:
    N = c["N"]
    t = (p + 1 - N)
    tm3 = t % 3
    pm3 = p % 3
    roots = [r for r in (0, 1, 2) if (r * r - tm3 * r + pm3) % 3 == 0]
    print(f"N={N} t mod 3={tm3} roots of X^2-tX+p mod 3: {roots}")
