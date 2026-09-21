import sys, math
sys.path.insert(0, "experiments/EXP-ECDLP-bbb42f")
from driver.ecc import scalar_mult, point_add, point_neg, OpCounter

p, a, b = 97, 91, 67
P = (55, 57)

ctr = OpCounter()
t_bound = math.isqrt(4 * p) + 1
L = p + 1
m = math.isqrt(2 * t_bound) + 1
print("t_bound", t_bound, "m", m)

baby = {}
R = None
for bb in range(m):
    baby[R] = bb
    R = point_add(R, P, a, p, ctr)
print("baby keys:", list(baby.items()))

negQ_base = point_neg(scalar_mult(L, P, a, p, ctr), p)
a_min = -(t_bound // m) - 1
a_max = (t_bound // m) + 1
print("a_min", a_min, "a_max", a_max)

candidates = set()
for aa in range(a_min, a_max + 1):
    shift = None if aa == 0 else point_neg(scalar_mult(aa * m, P, a, p, ctr), p)
    target = point_add(negQ_base, shift, a, p, ctr)
    if target in baby:
        bb = baby[target]
        k = aa * m + bb
        N = L + k
        print("MATCH aa=", aa, "b=", bb, "k=", k, "N=", N, "in range?", p+1-t_bound <= N <= p+1+t_bound)
        if p + 1 - t_bound <= N <= p + 1 + t_bound and N > 0:
            ok = scalar_mult(N, P, a, p, ctr) is None
            print("  verify N*P==O ->", ok)
            if ok:
                candidates.add(N)
print("final candidates:", candidates)
