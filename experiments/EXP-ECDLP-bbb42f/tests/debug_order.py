import sys, random
sys.path.insert(0, "experiments/EXP-ECDLP-bbb42f")
from driver.curve_order import bsgs_order_candidates
from driver.ecc import random_point

def brute_force_order(a, b, p):
    count = 1
    for x in range(p):
        rhs = (x ** 3 + a * x + b) % p
        if rhs == 0:
            count += 1
        else:
            ls = pow(rhs, (p - 1) // 2, p)
            if ls == 1:
                count += 2
    return count

random.seed(99)
for trial in range(60):
    p = random.choice([97, 101, 103, 1009, 1013])
    a = random.randrange(0, p)
    b = random.randrange(0, p)
    if (4*a**3 + 27*b*b) % p == 0:
        continue
    bf = brute_force_order(a, b, p)
    rng = random.Random(1)
    P = random_point(a, b, p, rng)
    cands = bsgs_order_candidates(P, a, p)
    if bf not in cands:
        print("BUG: true order not in candidate set", p, a, b, "P=", P, "bf=", bf, "cands=", cands)
