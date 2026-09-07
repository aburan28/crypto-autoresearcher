import sys, random
sys.path.insert(0, "experiments/EXP-ECDLP-bbb42f")
from driver.isogeny3 import psi_3_roots

p = 1048583
rng = random.Random(999)
has_root = 0
total = 0
for _ in range(30):
    a = rng.randrange(0, p)
    b = rng.randrange(0, p)
    if (4*a**3 + 27*b*b) % p == 0:
        continue
    total += 1
    roots = psi_3_roots(a, b, p)
    if roots:
        has_root += 1
    print(f"a={a} b={b} roots={roots}")
print(f"has_root={has_root}/{total}")
