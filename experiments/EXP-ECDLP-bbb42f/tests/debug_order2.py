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
found_bug = False
for trial in range(60):
    p = random.choice([97, 101, 103, 1009, 1013])
    a = random.randrange(0, p)
    b = random.randrange(0, p)
    if (4*a**3 + 27*b*b) % p == 0:
        continue
    bf = brute_force_order(a, b, p)
    order_rng = random.Random(1)  # same seeding as compute_group_order(...,rng1) in test where rng1=Random(1)
    for i in range(6):
        P = random_point(a, b, p, order_rng)
        cands = bsgs_order_candidates(P, a, p)
        if bf not in cands:
            print("BUG at point", i, "p=", p, "a=", a, "b=", b, "P=", P, "bf=", bf, "cands=", cands)
            found_bug = True
if not found_bug:
    print("no bug found in this sweep")
