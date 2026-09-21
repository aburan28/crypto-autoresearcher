"""RED TEAM check 2: does P3 generalize, and what does a P3 DEPARTURE mean?

Constructs frames INDEPENDENTLY of every committed artifact (no fpylll in this
environment, so no committed basis is regenerated -- these are new q-ary bases
of the same shape, which is exactly the out-of-sample setting under test).
Statistic and verdict rule copied verbatim from
tasks/TASK-20260806-0617ed/predicate.py.
"""
import numpy as np

GATE_K = 4.0
N = 8
Q = 3329

def v_stat(Qf):
    d, beta = Qf.shape
    diag = np.einsum("ij,ij->i", Qf, Qf)
    return float(np.sum((diag - beta / d) ** 2))

def mu0(d, beta):
    return 2.0 * beta * (d - beta) / (d * (d + 2.0))

def adjudicate(vs, d, beta):
    v = np.asarray(vs, float); n = v.size
    m = v.mean(); s = v.std(ddof=1); se = s / np.sqrt(n)
    z = (m - mu0(d, beta)) / se if se > 0 else np.inf
    verdict = "DEPARTURE" if z >= GATE_K else ("ANOMALY_BELOW_NULL" if z <= -GATE_K
                                               else "AGREEMENT_UPPER_BOUND")
    return dict(Vbar=m, sd=s, se=se, z=z, verdict=verdict, excess=m - mu0(d, beta))

def tail_frame(B, beta):
    """last-beta GSO frame of the row-basis B (same construction as b2a/predicate)."""
    Qf, _ = np.linalg.qr(np.asarray(B, float).T)
    return np.ascontiguousarray(Qf[:, B.shape[0] - beta:])

def qary_rows(d, k, q, rng, form):
    A = rng.integers(0, q, size=(k, d - k)).astype(float)
    B = np.zeros((d, d))
    if form == "I_first":          # [[I_k, A],[0, q I_{d-k}]]
        B[:k, :k] = np.eye(k); B[:k, k:] = A
        B[k:, k:] = q * np.eye(d - k)
    else:                           # [[q I_k, 0],[A, I_{d-k}]]
        B[:k, :k] = q * np.eye(k)
        B[k:, :k] = A.T; B[k:, k:] = np.eye(d - k)
    return B

def dct_orthogonal(d):
    n = np.arange(d)
    H = np.cos(np.pi * (n[:, None] + 0.5) * n[None, :] / d) * np.sqrt(2.0 / d)
    H[:, 0] /= np.sqrt(2.0)
    return H  # orthonormal columns

rng = np.random.default_rng(20260806)
print("=" * 78)
print("A. Which q-ary row form reproduces the committed `unreduced` V?")
print("   committed: (100,30) V = 9.362794 +- 0.080704 ; (140,30) V = 6.750435 +- 0.052182")
for (d, beta) in [(100, 30), (140, 30), (100, 40), (140, 40)]:
    k = d // 2
    for form in ("I_first", "q_first"):
        vs = [v_stat(tail_frame(qary_rows(d, k, Q, rng, form), beta)) for _ in range(N)]
        a = adjudicate(vs, d, beta)
        print("   d=%3d b=%2d  %-8s  Vbar=%10.5f  sd=%8.5f  z=%12.1f  %s"
              % (d, beta, form, a["Vbar"], a["sd"], a["z"], a["verdict"]))

print()
print("=" * 78)
print("B. NULL OBJECT 1 -- the trivial lattice Z^d in its identity basis.")
print("   Zero cryptographic content; V is exact.")
for (d, beta) in [(100, 30), (100, 40), (140, 30), (140, 40)]:
    B = np.eye(d)
    v = v_stat(tail_frame(B, beta))
    print("   d=%3d b=%2d  V=%.10f   beta(1-beta/d)=%.10f   mu0=%.6f   -> z = +inf, DEPARTURE"
          % (d, beta, v, beta * (1 - beta / d), mu0(d, beta)))

print()
print("=" * 78)
print("C. SAME LATTICE, SAME BASIS VECTORS, DIFFERENT ROW ORDER (a unimodular")
print("   permutation).  P3's verdict on an unchanged lattice:")
for (d, beta) in [(100, 30), (140, 30)]:
    k = d // 2
    can, rev, perm = [], [], []
    for _ in range(N):
        B = qary_rows(d, k, Q, rng, "I_first")
        can.append(v_stat(tail_frame(B, beta)))
        rev.append(v_stat(tail_frame(B[::-1], beta)))
        p = rng.permutation(d)
        perm.append(v_stat(tail_frame(B[p], beta)))
    for name, vs in (("canonical order", can), ("rows reversed", rev),
                     ("rows randomly permuted", perm)):
        a = adjudicate(vs, d, beta)
        print("   d=%3d b=%2d  %-24s Vbar=%10.5f  z=%+12.2f  %s"
              % (d, beta, name, a["Vbar"], a["z"], a["verdict"]))

print()
print("=" * 78)
print("D. SAME LATTICE UP TO AMBIENT ISOMETRY (B -> B H, H orthogonal).")
print("   Every lattice invariant -- successive minima, SVP/CVP hardness, GSO")
print("   profile, determinant -- is unchanged.  P3's verdict:")
for (d, beta) in [(100, 30), (140, 30)]:
    k = d // 2
    H = dct_orthogonal(d)
    plain, rot, hrot = [], [], []
    for _ in range(N):
        B = qary_rows(d, k, Q, rng, "I_first")
        plain.append(v_stat(tail_frame(B, beta)))
        rot.append(v_stat(tail_frame(B @ H, beta)))
        Hr = np.linalg.qr(rng.standard_normal((d, d)))[0]
        hrot.append(v_stat(tail_frame(B @ Hr, beta)))
    for name, vs in (("identity isometry", plain), ("DCT isometry", rot),
                     ("Haar isometry", hrot)):
        a = adjudicate(vs, d, beta)
        print("   d=%3d b=%2d  %-20s Vbar=%10.5f  excess=%+10.5f  z=%+12.2f  %s"
              % (d, beta, name, a["Vbar"], a["excess"], a["z"], a["verdict"]))

print()
print("=" * 78)
print("E. Is V the ONLY admissible statistic?  The predicate's argument assumes")
print("   coordinates are exchangeable.  A q-ary lattice has k=d/2 distinguished")
print("   coordinates, so the true symmetry group is signed permutations WITHIN")
print("   each block.  W = sum_{a<k} P_aa - beta*k/d is then a DEGREE-1 invariant,")
print("   is not constant, and is not a function of V.")
for (d, beta) in [(100, 30), (140, 30)]:
    k = d // 2
    # null distribution of W under Haar (Monte Carlo, a mathematical object)
    wn = []
    for _ in range(400):
        Qh = np.linalg.qr(rng.standard_normal((d, beta)))[0]
        dg = np.einsum("ij,ij->i", Qh, Qh)
        wn.append(dg[:k].sum() - beta * k / d)
    sd_null = float(np.std(wn, ddof=1))
    for form in ("I_first",):
        ws, vs = [], []
        for _ in range(N):
            B = qary_rows(d, k, Q, rng, form)
            F = tail_frame(B, beta)
            dg = np.einsum("ij,ij->i", F, F)
            ws.append(dg[:k].sum() - beta * k / d)
            vs.append(v_stat(F))
        wm = float(np.mean(ws))
        print("   d=%3d b=%2d unreduced: W = %+10.5f  (Haar null sd of W = %.5f) -> %+8.1f null-sd"
              % (d, beta, wm, sd_null, wm / sd_null))
        print("              V = %+10.5f  (both statistics fire; W is not a function of V)"
              % np.mean(vs))
