import random, sys
sys.path.insert(0, 'experiments/EXP-ECDLP-bbb42f')
from driver.curve_order import compute_group_order, verify_group_order
from driver.ecc import on_curve

def brute_force_order(a, b, p):
    count = 1  # infinity
    for x in range(p):
        rhs = (x ** 3 + a * x + b) % p
        if rhs == 0:
            count += 1
        else:
            ls = pow(rhs, (p - 1) // 2, p)
            if ls == 1:
                count += 2
    return count

random.seed(1234)
fails = 0
trials_run = 0
for trial in range(40):
    p = random.choice([97, 101, 1009, 10007, 100003])
    a = random.randrange(0, p)
    b = random.randrange(0, p)
    if (4 * a ** 3 + 27 * b * b) % p == 0:
        continue
    trials_run += 1
    rng = random.Random(trial)
    try:
        N, ctr, npts = compute_group_order(a, b, p, rng)
    except Exception as e:
        print("FAIL exc", p, a, b, e)
        fails += 1
        continue
    bf = brute_force_order(a, b, p)
    if N != bf:
        fails += 1
        print("MISMATCH", p, a, b, "computed", N, "brute", bf, "npts", npts)
print("trials_run=", trials_run, "fails=", fails)
