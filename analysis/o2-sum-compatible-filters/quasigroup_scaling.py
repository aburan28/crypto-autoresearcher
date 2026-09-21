#!/usr/bin/env python3
"""
The control O2_quasigroup_gap.md section 4 says is missing.

That document enumerated all Latin squares of order 3,4,5 exhaustively and found
the normalized excess (eps - 1/M)/Lambda <= 0.17, never approaching M.  But it
stated plainly that this CANNOT separate "quasigroups are special" from
"M <= 5 is too small for the M loss to appear", because the arbitrary-f excess
was small there too.

The discriminating question is how the excess SCALES with M.  If quasigroups
realize the (star) bound, (eps_q - 1/M)/Lambda grows like M.  If Theorem C's
exact-case rigidity has an approximate shadow, it stays O(1).

Exhaustive enumeration dies at M=6 (8.1e8 squares), so this samples instead,
using JACOBSON-MATTHEWS -- the standard Markov chain that is uniform on Latin
squares.  A cheaper sampler was deliberately NOT used: permuting rows/columns/
symbols of the cyclic table yields only isotopes of the cyclic GROUP, which are
group-like by construction and would rig the control toward this program's own
conclusion.

Three comparators at matched sample size K, so the maxima are comparable:
    eps_grp    group law                       -- Theorem A: excess <= 1
    eps_quasi  max over K uniform Latin squares -- the Wagner-usable class
    eps_randf  max over K uniform arbitrary f   -- matched null, NOT tree-usable
    eps_arb    exact max over ALL f             -- the (star) ceiling
"""
import sys

import numpy as np

sys.path.insert(0, ".")
from fourier_obstruction import is_prime, curve_order, dlog_table


# ------------------------------------------------- Jacobson-Matthews sampler
class JM:
    """Uniform sampler on Latin squares of order M (Jacobson & Matthews 1996).

    State is the incidence array f[r,c,s] in {0,1}, with at most one cell equal
    to -1 ("improper").  Proper states are exactly the Latin squares, and the
    chain is uniform on them.
    """

    def __init__(self, M, rng):
        self.M, self.rng = M, rng
        self.f = np.zeros((M, M, M), dtype=np.int8)
        for r in range(M):
            for c in range(M):
                self.f[r, c, (r + c) % M] = 1
        self.improper = None  # (r,c,s) with f == -1

    def _ones(self, axis, i, j):
        """Indices k with f == 1 along `axis`, other two coords fixed at i,j."""
        f = self.f
        v = (f[:, i, j] if axis == 0 else
             f[i, :, j] if axis == 1 else
             f[i, j, :])
        return np.flatnonzero(v == 1)

    def step(self):
        M, rng, f = self.M, self.rng, self.f
        if self.improper is None:
            while True:
                r, c, s = rng.integers(0, M, 3)
                if f[r, c, s] == 0:
                    break
        else:
            r, c, s = self.improper

        # pick the conflicting coordinates; when improper there are two choices
        rs = self._ones(0, c, s)
        cs = self._ones(1, r, s)
        ss = self._ones(2, r, c)
        r2 = rs[rng.integers(len(rs))]
        c2 = cs[rng.integers(len(cs))]
        s2 = ss[rng.integers(len(ss))]

        f[r, c, s] += 1
        f[r2, c, s] -= 1
        f[r, c2, s] -= 1
        f[r, c, s2] -= 1
        f[r2, c2, s] += 1
        f[r2, c, s2] += 1
        f[r, c2, s2] += 1
        f[r2, c2, s2] -= 1

        self.improper = (r2, c2, s2) if f[r2, c2, s2] < 0 else None

    def square(self, mixing):
        """Advance `mixing` steps and return a proper Latin square."""
        for _ in range(mixing):
            self.step()
        while self.improper is not None:
            self.step()
        return np.argmax(self.f == 1, axis=2)


def is_latin(L, M):
    ok = all(len(np.unique(L[r])) == M for r in range(M))
    return ok and all(len(np.unique(L[:, c])) == M for c in range(M))


# ------------------------------------------------- exact counts / filters
def triple_counts(hv, M, N):
    ind = np.zeros((M, N))
    for a in range(M):
        ind[a] = (hv == a).astype(float)
    F = np.fft.rfft(ind, axis=1)
    C = np.zeros((M, M, M))
    for a in range(M):
        for b in range(M):
            conv = np.fft.irfft(F[a] * F[b], n=N)
            for c in range(M):
                C[a, b, c] = float(conv[hv == c].sum())
    return C


def Lambda(hv, M):
    N = len(hv)
    return max(float(np.abs(np.fft.fft(np.exp(2j * np.pi * t * hv / M)) / N).max())
               for t in range(1, M))


def eps_of(C, L, M, tot):
    return float(C[np.arange(M)[:, None], np.arange(M)[None, :], L].sum()) / tot


def find_curve(p_target):
    p = p_target
    while not is_prime(p):
        p += 1
    for a in range(0, 30):
        for b in range(1, 30):
            if (4 * a ** 3 + 27 * b * b) % p == 0:
                continue
            n = curve_order(p, a, b)
            if is_prime(n):
                return p, a, b, n
    return None


def main():
    rng = np.random.default_rng(20260802)
    K = 600
    p, a, b, N = find_curve(8219)
    _, pts = dlog_table(p, a, b, N)
    xs = np.array([0 if P is None else P[0] for P in pts])

    print(f"curve: p={p} a={a} b={b}  N={N} (prime)   K={K} samples per class")
    print("Jacobson-Matthews, uniform on Latin squares; mixing = 8*M^2 steps/sample after 50*M^2 burn-in\n")

    print(f"{'filter':>10} {'M':>4} {'Lambda':>9} {'excess_grp':>11} "
          f"{'excess_quasi':>13} {'excess_randf':>13} {'excess_arb':>11} "
          f"{'(star) cap':>11}")

    for kind in ("x mod M", "dlog mod M"):
        for M in (4, 8, 16, 32):
            hv = (xs % M) if kind == "x mod M" else (np.arange(N) % M)
            if len(np.unique(hv)) < M:
                continue
            C = triple_counts(hv, M, N)
            tot = float(N) ** 2
            L = Lambda(hv, M)

            grp = (np.arange(M)[:, None] + np.arange(M)[None, :]) % M
            e_grp = eps_of(C, grp, M, tot)
            e_arb = float(C.max(axis=2).sum()) / tot

            jm = JM(M, rng)
            jm.square(50 * M * M)               # burn-in
            e_q = 0.0
            for _ in range(K):
                L2 = jm.square(8 * M * M)
                assert is_latin(L2, M)
                e_q = max(e_q, eps_of(C, L2, M, tot))

            e_rf = max(eps_of(C, rng.integers(0, M, (M, M)), M, tot)
                       for _ in range(K))

            f = lambda e: (e - 1.0 / M) / L
            import sys; sys.stdout.flush()
            print(f"{kind:>10} {M:>4} {L:>9.5f} {f(e_grp):>11.3f} "
                  f"{f(e_q):>13.3f} {f(e_rf):>13.3f} {f(e_arb):>11.3f} "
                  f"{M:>11}")
        print()

    print("=" * 96)
    print("Excess = (eps - 1/M)/Lambda.  Theorem A caps the group law at 1;")
    print("(star) caps arbitrary f at M (last column).")
    print("If excess_quasi tracks M, quasigroups realize the loss and j=2 reopens")
    print("for quasigroup combining.  If it stays O(1), Theorem C has an")
    print("approximate shadow and the closure survives.")


if __name__ == "__main__":
    main()
