import sys, random
sys.path.insert(0, "experiments/EXP-ECDLP-bbb42f")
from driver.ecc import scalar_mult, tonelli_shanks

random.seed(123)
p = 1009
found = None
for trial in range(200):
    a = random.randrange(0, p)
    b = random.randrange(0, p)
    if (4*a**3+27*b*b) % p == 0:
        continue
    for x0 in range(0, p, 1):
        rhs = (x0**3+a*x0+b) % p
        y0 = tonelli_shanks(rhs, p)
        if y0 is None:
            continue
        cand = (x0, y0)
        if scalar_mult(3, cand, a, p) is None:
            found = (a, b, x0, y0)
            break
    if found:
        break

print("found:", found)
