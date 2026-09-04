"""Smoke test: s = 2, one instance, both readings, plus the ideal cap / certificate."""
import sys, time
sys.path.insert(0, "/home/user/crypto-autoresearcher/coordination/reviews/pfdr-battery-20260904/reviews/TASK-20260904-42b33a/scripts")

import numpy as np
from hky import (SquarefreeRing, semaev_S3_digit, deg_poly, closure_B, dim_leq,
                 zero_set, ideal_cap_dim, eval_rank)
from polyring import PolyRing, closure_poly, dim_leq_poly, field_eqs, mask_to_exp
from params import INSTANCES, D_MAX

p, cs, a, b, ts, xR = INSTANCES[0]
s = 2
n = 2 * s
gen = semaev_S3_digit(p, a, b, xR, s)
print("instance", (p, cs, a, b, ts, xR), "s =", s, "n =", n)
print("deg_B(S~) =", deg_poly(gen), " #terms =", len(gen))

ring = SquarefreeRing(n, p, D_MAX)
Z = zero_set(gen, n, p)
print("|Z| =", len(Z), "Z =", [(z & ((1 << s) - 1), z >> s) for z in Z][:12])

t0 = time.time()
dims_B, caps = {}, {}
for D in range(0, D_MAX + 1):
    cap = ideal_cap_dim(Z, ring, D, p)
    W, rounds, prod = closure_B(ring, gen, D, ideal_dim=cap)
    dims_B[D] = (W, rounds, prod)
    caps[D] = cap
    print(f"  B  D={D}: N={ring.ncols(min(D,n))} dimV={W.dim} cap={cap} rounds={rounds} prod={prod}")
print("B time", round(time.time() - t0, 2))

falls_B = []
for D in range(1, D_MAX + 1):
    W = dims_B[D][0]
    lhs = dim_leq(W, ring, D, D - 1)
    rhs = dims_B[D - 1][0].dim
    print(f"  fall test D={D}: dim(V_D n B_<=D-1)={lhs} vs dim V_{{D-1}}={rhs}")
    if lhs > rhs:
        falls_B.append(D)
print("B falls:", falls_B)

# ---- literal polynomial ring
t0 = time.time()
gens = [{mask_to_exp(m, n): c for m, c in gen.items()}] + field_eqs(n)
dims_P = {}
for D in range(0, D_MAX + 1):
    pr = PolyRing(n, p, D)
    W, rounds, prod = closure_poly(pr, gens, D)
    dims_P[D] = (W, pr, rounds, prod)
    print(f"  R  D={D}: N={pr.N} dimV={W.dim} rounds={rounds} prod={prod}")
print("poly time", round(time.time() - t0, 2))

falls_P = []
for D in range(1, D_MAX + 1):
    W, pr, _, _ = dims_P[D]
    lhs = dim_leq_poly(W, pr, D - 1)
    rhs = dims_P[D - 1][0].dim
    print(f"  fall test D={D}: {lhs} vs {rhs}")
    if lhs > rhs:
        falls_P.append(D)
print("R falls:", falls_P)
print("AGREE:", falls_B == falls_P)
