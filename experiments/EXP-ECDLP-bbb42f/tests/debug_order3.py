import sys, math
sys.path.insert(0, "experiments/EXP-ECDLP-bbb42f")
from driver.curve_order import bsgs_order_candidates
from driver.ecc import scalar_mult

p, a, b = 97, 91, 67
P = (55, 57)
L = p + 1
t_bound = math.isqrt(4 * p) + 1
print("t_bound", t_bound)

true_ks = []
for k in range(-t_bound, t_bound + 1):
    N = L + k
    if N <= 0:
        continue
    if scalar_mult(N, P, a, p) is None:
        true_ks.append(k)
print("true k values with N*P=O:", true_ks, "-> N values:", [L+k for k in true_ks])

cands = bsgs_order_candidates(P, a, p)
print("bsgs candidates:", sorted(cands))
