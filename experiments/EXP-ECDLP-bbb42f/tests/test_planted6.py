import sys, time
sys.path.insert(0, "experiments/EXP-ECDLP-bbb42f")
from driver.planted import construct_planted_instance
from driver.predicates import classify
from driver.curve_order import compute_group_order
from driver.ecc import seeded_rng, random_point, scalar_mult
from driver.sssa import sssa_solve

t0 = time.time()
inst = construct_planted_instance(20, master_seed=20260902004, chain_len=4, k_max=6)
print("time", time.time() - t0, "restarts_used", inst["restarts_used"])
p = inst["p"]
er = inst["e_rand"]
N_er, _, _ = compute_group_order(er["a"], er["b"], p, seeded_rng("verify"))
print("E_rand N", N_er, "special N", inst["special_curve"]["N"])
cls = classify(N_er, p, 6)
print("classification", cls)

rng = seeded_rng("dlp")
P = random_point(er["a"], er["b"], p, rng)
while P[1] == 0:
    P = random_point(er["a"], er["b"], p, rng)
k_true = 12345 % (N_er - 1) + 1
Q = scalar_mult(k_true, P, er["a"], p)
k_computed, diag = sssa_solve(P[0], P[1], Q[0], Q[1], er["a"], er["b"], p)
print("k_true", k_true, "k_computed", k_computed, "OK", k_true == k_computed)
