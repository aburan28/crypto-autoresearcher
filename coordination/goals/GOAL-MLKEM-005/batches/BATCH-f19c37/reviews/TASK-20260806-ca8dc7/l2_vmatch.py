"""RED TEAM check 3: F-A1 claims `D` depends on the frame ONLY through `V`.
The AM-1 run tests that on ONE monotone family (the graded path), where V and D
are both monotone in t, so the ordering test cannot fail.  Here: a SECOND frame
family, matched in V exactly, with a two-level diagonal profile instead of the
graded family's spread profile.  If D depends on V alone, D must agree.

Red-team probe. My own frames, my own seeds, my own error draws. TOY tier.
Nothing here is pre-registered and nothing here is evidence about ML-KEM.
"""
import numpy as np

d, beta, N = 100, 30, 1 << 20
CH = 1 << 17
rng = np.random.default_rng(31415)

def v_stat(Q):
    dg = np.einsum("ij,ij->i", Q, Q)
    return float(np.sum((dg - Q.shape[1] / Q.shape[0]) ** 2))

def haar_frame(j):
    return np.linalg.qr(np.random.default_rng(900000 + j).standard_normal((d, beta)))[0]

def graded_frame(j, t):
    g = np.random.default_rng(500000 + j)
    S = g.choice(d, size=beta, replace=False); G = g.standard_normal((d, beta))
    E = np.zeros((d, beta)); E[S, np.arange(beta)] = 1.0
    return np.linalg.qr(np.sqrt(1 - t) * E + np.sqrt(t) * G)[0]

def pair_frame(j, V_target):
    """rank-beta projector on 2*beta coordinates, two-level diagonal, V exact."""
    c = (V_target + beta * beta / d) / beta
    u = (1.0 + np.sqrt(max(2 * c - 1, 0.0))) / 2.0        # = cos^2(theta)
    g = np.random.default_rng(770000 + j)
    idx = g.permutation(d)[: 2 * beta]
    Q = np.zeros((d, beta))
    Q[idx[:beta], np.arange(beta)] = np.sqrt(u)
    Q[idx[beta:], np.arange(beta)] = np.sqrt(1 - u)
    return Q

def diag_moments(Q):
    dg = np.einsum("ij,ij->i", Q, Q)
    return float(np.sum((dg - beta / d) ** 2)), float(np.sum((dg - beta / d) ** 3))

TS = [0.005, 0.0075, 0.01]
arms = {"haar": [haar_frame(j) for j in range(8)]}
for t in TS:
    gf = [graded_frame(j, t) for j in range(8)]
    arms["graded_t%.4f" % t] = gf
    Vt = float(np.mean([v_stat(q) for q in gf]))
    arms["pairV_%.4f" % t] = [pair_frame(j, Vt) for j in range(8)]

names = list(arms)
big = np.hstack([np.hstack(arms[n]) for n in names]).astype(np.float32)  # d x (8*beta*n)
print("frames stacked:", big.shape)

# CBD_{eta=2} errors, shared across arms (the design's own discipline)
acc = np.empty((big.shape[1], N), dtype=np.float32)
nrm = np.empty(N, dtype=np.float32)
erng = np.random.default_rng(20260806 + d)
for s in range(0, N, CH):
    e = (erng.integers(0, 2, size=(2, d, CH), dtype=np.int8).sum(0)
         - erng.integers(0, 2, size=(2, d, CH), dtype=np.int8).sum(0)).astype(np.float32)
    nrm[s:s + CH] = np.einsum("ij,ij->j", e, e)
    acc[:, s:s + CH] = big.T @ e
print("error draws done")

idx = int(round(N * 2 ** -10)) - 1
res = {}
for a, n in enumerate(names):
    q = []
    for j in range(8):
        cols = slice((a * 8 + j) * beta, (a * 8 + j + 1) * beta)
        R = np.einsum("ij,ij->j", acc[cols], acc[cols]) / nrm
        q.append(float(np.sort(R)[idx]))
    res[n] = np.array(q)

h = res["haar"].mean()
print()
print("%-16s %10s %12s %12s %12s" % ("arm", "V", "3rd moment", "q_emp mean", "D_raw (x q_Beta)"))
for n in names:
    V, M3 = np.mean([diag_moments(Q)[0] for Q in arms[n]]), np.mean([diag_moments(Q)[1] for Q in arms[n]])
    print("%-16s %10.4f %12.4f %12.8f %+12.8f" % (n, V, M3, res[n].mean(), res[n].mean() - h))
print()
print("V-matched pairs -- L2 (F-A1) requires these to agree:")
for t in TS:
    g, p = res["graded_t%.4f" % t], res["pairV_%.4f" % t]
    Dg, Dp = g.mean() - h, p.mean() - h
    se = np.sqrt(g.var(ddof=1) / 8 + p.var(ddof=1) / 8)   # haar term cancels exactly in D_p - D_g
    Vg = np.mean([v_stat(Q) for Q in arms["graded_t%.4f" % t]])
    Vp = np.mean([v_stat(Q) for Q in arms["pairV_%.4f" % t]])
    print("  V=%7.4f/%7.4f  D_graded=%+.8f  D_pair=%+.8f  ratio=%.3f  diff=%+.2f SE"
          % (Vg, Vp, Dg, Dp, Dp / Dg, (Dp - Dg) / se))

import json
json.dump({n: res[n].tolist() for n in names}, open("l2_vmatch_qemp.json", "w"), indent=1)
print("\nper-frame q_emp written to l2_vmatch_qemp.json")
