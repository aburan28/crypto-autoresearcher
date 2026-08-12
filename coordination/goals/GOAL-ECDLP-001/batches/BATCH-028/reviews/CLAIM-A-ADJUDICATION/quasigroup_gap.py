#!/usr/bin/env python3
"""
Does the quasigroup class realize the M^2 loss?

Both independent derivations bound  eps <= 1/M + M*Lambda  for ADVERSARIAL f,
and  eps <= 1/M + Lambda  for the GROUP LAW.  The factor M is the entire
difference between closing the j=2 four-tree and not.

But an adversarial f is not usable in a Wagner tree.  A tree must, given
h(P)=a and a target bucket c, know which b to look for -- so f must be
invertible in each argument, i.e. a QUASIGROUP (Latin square).  That is the
real class, strictly between "group law" and "arbitrary".

EXACT CASE: settled by hand.  Exact sum-compatibility + associativity of + on E
forces f associative; an associative quasigroup is a group; h is then a
surjective hom E(F_p) -> ([M],f), impossible for N prime and M < N.

APPROXIMATE CASE: this script.  For M = 3,4,5 the Latin squares can be
enumerated EXHAUSTIVELY (12, 576, 161280), so max over quasigroups is computed
exactly, not sampled.  Compare three quantities on the same filter:

    eps_grp    f = group law (a+b mod M)          -- bound 1/M + Lambda
    eps_quasi  max over ALL Latin squares         -- the Wagner-usable class
    eps_arb    max over ALL f (f_joint)           -- bound 1/M + M*Lambda

If eps_quasi tracks eps_grp, the M loss is NOT realized by any tree-usable f
and the gap closes.  If eps_quasi tracks eps_arb, the loss is real and the
j=2 four-tree stays open for quasigroup combining.

Counts are exact: C[a][b][c] = #{(i,j) : h(i)=a, h(j)=b, h(i+j mod N)=c},
computed by cyclic convolution over the dlog indexing (P_i + P_j has dlog i+j).
No sampling anywhere.
"""
import itertools
import sys

import numpy as np

sys.path.insert(0, ".")
from fourier_obstruction import is_prime, curve_order, dlog_table


# ---------------------------------------------------------------- Latin squares
def latin_squares(M):
    """Enumerate every Latin square of order M as an M x M numpy array."""
    rows_all = [np.array(p) for p in itertools.permutations(range(M))]
    out, cur = [], []

    def rec(r):
        if r == M:
            out.append(np.array(cur))
            return
        for row in rows_all:
            ok = True
            for pr in cur:
                if np.any(pr == row):
                    ok = False
                    break
            if ok:
                cur.append(row)
                rec(r + 1)
                cur.pop()

    rec(0)
    return out


# ---------------------------------------------------------------- exact counts
def triple_counts(hv, M, N):
    """C[a,b,c] exactly, via cyclic convolution. No sampling."""
    ind = np.zeros((M, N))
    for a in range(M):
        ind[a] = (hv == a).astype(float)
    F = np.fft.rfft(ind, axis=1)
    C = np.zeros((M, M, M))
    for a in range(M):
        for b in range(M):
            conv = np.fft.irfft(F[a] * F[b], n=N)  # counts by k = i+j mod N
            for c in range(M):
                C[a, b, c] = float(conv[hv == c].sum())
    return C


def Lambda(hv, M):
    N = len(hv)
    best = 0.0
    for t in range(1, M):
        g = np.exp(2j * np.pi * t * hv / M)
        best = max(best, float(np.abs(np.fft.fft(g) / N).max()))
    return best


# ---------------------------------------------------------------- filters
def legendre(v, p):
    return 0 if v % p == 0 else (1 if pow(v, (p - 1) // 2, p) == 1 else -1)


def make_filter(kind, pts, p, M):
    out = np.zeros(len(pts), dtype=np.int64)
    for i, P in enumerate(pts):
        x = 0 if P is None else P[0]
        if kind == "x mod M":
            out[i] = x % M
        elif kind == "char":  # F1 family C, r bits -> M = 2^r
            r = int(np.log2(M))
            v = 0
            for j in range(r):
                v |= (1 if legendre(x - j, p) >= 0 else 0) << j
            out[i] = v
        elif kind == "dlog-int":  # [D] Proposition 2 -- the known escape
            out[i] = (i * M) // len(pts)
        elif kind == "dlog mod M":
            out[i] = i % M
    return out


def find_curve(p_target):
    p = p_target
    while not is_prime(p):
        p += 1
    for a in range(0, 20):
        for b in range(1, 20):
            if (4 * a ** 3 + 27 * b * b) % p == 0:
                continue
            n = curve_order(p, a, b)
            if is_prime(n):
                return p, a, b, n
    return None


# ---------------------------------------------------------------- main
def main():
    print("Enumerating Latin squares (exhaustive) ...")
    LS = {M: latin_squares(M) for M in (3, 4, 5)}
    for M in (3, 4, 5):
        print(f"  order {M}: {len(LS[M])} squares")
    print()

    hdr = (f"{'filter':>12} {'p':>7} {'M':>3} {'1/M':>8} {'Lambda':>9} "
           f"{'eps_grp':>9} {'eps_quasi':>9} {'eps_arb':>9} "
           f"{'(q-1/M)/L':>10} {'(a-1/M)/L':>10}")

    for kind in ("x mod M", "char", "dlog mod M", "dlog-int"):
        print(f"=== filter: {kind} ===")
        print(hdr)
        for p_t in (523, 1033, 2063, 4111):
            found = find_curve(p_t)
            if not found:
                continue
            p, a, b, N = found
            _, pts = dlog_table(p, a, b, N)
            for M in (3, 4, 5):
                if kind == "char" and M not in (4,):
                    continue  # char filter needs M a power of 2
                hv = make_filter(kind, pts, p, M)
                if len(np.unique(hv)) < M:
                    continue  # redundant: run at M_eff instead
                C = triple_counts(hv, M, N)
                tot = float(N) ** 2
                L = Lambda(hv, M)

                grp = np.array([[(x + y) % M for y in range(M)]
                                for x in range(M)])
                e_grp = sum(C[x, y, grp[x, y]]
                            for x in range(M) for y in range(M)) / tot
                e_arb = float(C.max(axis=2).sum()) / tot
                e_q = max(
                    sum(C[x, y, Lsq[x, y]] for x in range(M) for y in range(M))
                    for Lsq in LS[M]
                ) / tot

                nq = (e_q - 1.0 / M) / L if L > 0 else float("nan")
                na = (e_arb - 1.0 / M) / L if L > 0 else float("nan")
                print(f"{kind:>12} {p:>7} {M:>3} {1/M:>8.5f} {L:>9.5f} "
                      f"{e_grp:>9.5f} {e_q:>9.5f} {e_arb:>9.5f} "
                      f"{nq:>10.3f} {na:>10.3f}")
        print()

    print("=" * 100)
    print("READING THE TABLE")
    print("  Theorem A (group law) :  eps <= 1/M + Lambda        -> (eps-1/M)/Lambda <= 1")
    print("  (star)   (arbitrary f):  eps <= 1/M + M*Lambda      -> (eps-1/M)/Lambda <= M")
    print("  The two rightmost columns are those normalized excesses.")
    print("  If (q-1/M)/L stays near or below 1, quasigroups do NOT realize the M loss.")
    print("  If it grows toward M, they do, and j=2 stays open for quasigroup combining.")


if __name__ == "__main__":
    main()
