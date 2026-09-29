"""Independent implementation of the Huang-Kosters-Yeo V_{F,D} closure.

Written for TASK-20260904-42b33a (blind re-derivation) from the DEFINITION in
review_plan.blind_rederivation.quantity of ledger/handoffs/TASK-20260904-42b33a.yaml
and the mechanism section of ledger/hypotheses/H-PFDR-c88f14.yaml ONLY.

No file listed in review_plan.blind_rederivation.blind_from was opened, and
nothing from harness/macaulay_fp is imported.  All linear algebra below is my
own.

Conventions implemented (READING 1, "literally the polynomial-ring definition"):

    R = F_p[a_{1,0..s-1}, a_{2,0..s-1}],  n = 2s
    F = { S~ } u { a_{k,i}^2 - a_{k,i} }        (S~ = multilinear representative)
    V_{F,D} = smallest F_p-subspace of R_{<=D} containing F n R_{<=D} and closed
              under  v -> h v  for every monomial h with deg(h v) <= D.
    fall at D  <=>  dim( V_{F,D} n R_{<=D-1} ) > dim V_{F,D-1}
    d_ff = least D <= D_max with a fall ; d_lf = largest D <= D_max with a fall

Computation happens in the squarefree quotient B = R/(a_i^2 - a_i) via the
equivalence proved in the report (identical fall history); READING 1 is also
executed literally, in the honest polynomial ring, at s = 2 and s = 3 as an
empirical check of that equivalence.

Degrees in B: deg_B(v) = max popcount of a monomial with nonzero coefficient.
The multiplication condition in B is deg(h) + deg_B(v) <= D (READING 2a, the
shadow of Reading 1).  A third reading, deg_B(h v) <= D (READING 2b), is
implemented separately in variant_2b().
"""

import numpy as np

# ----------------------------------------------------------------- linear algebra


def _gauss(A, p):
    """Full RREF of A (float64, entries already reduced mod p). Returns (E, piv)."""
    A = np.mod(A, p)
    keep = np.any(A != 0, axis=1)
    A = A[keep]
    if A.shape[0] == 0:
        return A, np.zeros(0, dtype=np.int64)
    piv = []
    r = 0
    while r < A.shape[0]:
        sub = A[r:]
        nzc = np.nonzero(np.any(sub != 0, axis=0))[0]
        if nzc.size == 0:
            break
        c = int(nzc[0])
        i = r + int(np.nonzero(sub[:, c])[0][0])
        if i != r:
            A[[r, i]] = A[[i, r]]
        inv = pow(int(A[r, c]) % p, p - 2, p)
        A[r] = np.mod(A[r] * inv, p)
        col = A[:, c].copy()
        col[r] = 0.0
        nzr = np.nonzero(col)[0]
        if nzr.size:
            A[nzr] = np.mod(A[nzr] - np.outer(col[nzr], A[r]), p)
        piv.append(c)
        r += 1
    return A[:r], np.array(piv, dtype=np.int64)


class LinSpace:
    """Row space over F_p kept in reduced row echelon form (columns in the
    caller's order).  Exactness: entries < p, so each inner product term is
    < p^2 and a sum of N of them is < N p^2; the caller asserts N p^2 < 2^53."""

    def __init__(self, N, p):
        self.N, self.p = N, p
        self.R = np.zeros((0, N))
        self.piv = np.zeros(0, dtype=np.int64)
        assert N * (p - 1) ** 2 < 2 ** 53, "float64 exactness bound violated"

    @property
    def dim(self):
        return int(self.R.shape[0])

    def reduce(self, A):
        A = np.mod(A, self.p)
        if self.R.shape[0]:
            A = np.mod(A - A[:, self.piv] @ self.R, self.p)
        return A

    def add_rows(self, A, chunk=192):
        """Add rows; returns True if the dimension grew."""
        grew = False
        A = np.asarray(A, dtype=np.float64)
        for i in range(0, A.shape[0], chunk):
            blk = self.reduce(A[i:i + chunk])
            blk = blk[np.any(blk != 0, axis=1)]
            if blk.shape[0] == 0:
                continue
            E, ep = _gauss(blk, self.p)
            if E.shape[0] == 0:
                continue
            if self.R.shape[0]:
                self.R = np.mod(self.R - self.R[:, ep] @ E, self.p)
            self.R = np.vstack([self.R, E])
            self.piv = np.concatenate([self.piv, ep])
            o = np.argsort(self.piv, kind="stable")
            self.R, self.piv = self.R[o], self.piv[o]
            grew = True
        return grew


# --------------------------------------------------------- squarefree ring B


def popcount(x):
    return bin(x).count("1")


class SquarefreeRing:
    """B = F_p[a_0..a_{n-1}]/(a_i^2 - a_i); monomials are bitmasks."""

    def __init__(self, n, p, dmax):
        self.n, self.p, self.dmax = n, p, dmax
        self.order = sorted(range(1 << n), key=lambda m: (-popcount(m), m))
        self.pos = {m: i for i, m in enumerate(self.order)}
        # off[d] = number of masks of popcount > d  => level-d columns are order[off[d]:]
        self.off = [sum(1 for m in self.order if popcount(m) > d) for d in range(n + 1)]
        self._tgt = {}

    def ncols(self, D):
        D = min(D, self.n)
        return (1 << self.n) - self.off[D]

    def vec(self, poly, D):
        """dict {mask: coeff} -> dense level-D vector."""
        D = min(D, self.n)
        v = np.zeros(self.ncols(D))
        o = self.off[D]
        for m, c in poly.items():
            c %= self.p
            if c:
                v[self.pos[m] - o] = c
        return v

    def tgt(self, D, e, h):
        """index map: level-D columns of popcount <= e  ->  level-D column of (mask|h)."""
        D = min(D, self.n)
        key = (D, e, h)
        t = self._tgt.get(key)
        if t is None:
            o = self.off[D]
            src = self.order[self.off[e]:]           # masks of popcount <= e
            t = np.array([self.pos[m | h] - o for m in src], dtype=np.int64)
            assert (t >= 0).all()
            self._tgt[key] = t
        return t

    def seg(self, D, e):
        D = min(D, self.n)
        return self.off[e] - self.off[D]

    def mul_mon(self, v, D, e, h):
        """v: level-D vector of degree <= e; h: squarefree monomial mask."""
        D = min(D, self.n)
        t = self.tgt(D, e, h)
        return np.bincount(t, weights=v[self.seg(D, e):], minlength=self.ncols(D))

    def deg_of_col(self, D, j):
        D = min(D, self.n)
        return popcount(self.order[self.off[D] + j])

    def monomials_upto(self, t):
        out = [[] for _ in range(t + 1)]
        for m in range(1 << self.n):
            k = popcount(m)
            if k <= t:
                out[k].append(m)
        return [m for k in range(t + 1) for m in out[k]]


# ------------------------------------------------------------- poly arithmetic


def p_add(f, g, p):
    out = dict(f)
    for m, c in g.items():
        out[m] = (out.get(m, 0) + c) % p
        if out[m] == 0:
            del out[m]
    return out


def p_scal(f, k, p):
    k %= p
    if k == 0:
        return {}
    return {m: (c * k) % p for m, c in f.items() if (c * k) % p}


def p_mul(f, g, p):
    out = {}
    for m1, c1 in f.items():
        for m2, c2 in g.items():
            m = m1 | m2
            out[m] = (out.get(m, 0) + c1 * c2) % p
    return {m: c for m, c in out.items() if c}


def semaev_S3_digit(p, a, b, xR, s):
    """S~ = S_3(ell_1, ell_2, x_R) reduced mod the field equations, in B."""
    ell1 = {1 << i: pow(2, i, p) for i in range(s)}
    ell2 = {1 << (s + i): pow(2, i, p) for i in range(s)}
    one = {0: 1}
    diff = p_add(ell1, p_scal(ell2, -1, p), p)
    ssum = p_add(ell1, ell2, p)
    prod = p_mul(ell1, ell2, p)
    t1 = p_scal(p_mul(diff, diff, p), (xR * xR) % p, p)
    inner = p_add(p_mul(ssum, p_add(prod, p_scal(one, a, p), p), p),
                  p_scal(one, (2 * b) % p, p), p)
    t2 = p_scal(inner, (-2 * xR) % p, p)
    pa = p_add(prod, p_scal(one, -a, p), p)
    t3 = p_mul(pa, pa, p)
    t4 = p_scal(ssum, (-4 * b) % p, p)
    return p_add(p_add(t1, t2, p), p_add(t3, t4, p), p)


def deg_poly(f):
    return max((popcount(m) for m in f), default=-1)


# ------------------------------------------------------------------- closure


def closure_B(ring, gen, D, ideal_dim=None, log=None):
    """V_{F,D} in B under Reading 2a.  Returns (LinSpace, rounds, productive)."""
    p, n = ring.p, ring.n
    Dm = min(D, n)
    N = ring.ncols(Dm)
    W = LinSpace(N, p)
    dg = deg_poly(gen)
    if dg < 0 or dg > D:
        return W, 0, 0
    g = ring.vec(gen, Dm)
    rows = [ring.mul_mon(g, Dm, dg, h) for h in ring.monomials_upto(min(D - dg, n))]
    W.add_rows(np.array(rows))
    rounds, productive = 0, 0
    CH = 512
    while True:
        if ideal_dim is not None and W.dim >= ideal_dim:
            break
        # expand lowest-degree basis rows first: they carry the most multipliers
        idx = [i for i in range(W.dim)
               if ring.deg_of_col(Dm, int(W.piv[i])) <= D - 1]
        idx.sort(key=lambda i: ring.deg_of_col(Dm, int(W.piv[i])))
        snapshot = W.R[idx].copy() if idx else None
        degs = [ring.deg_of_col(Dm, int(W.piv[i])) for i in idx]
        rounds += 1
        if not idx:
            break
        grew = False
        buf, nrows = [], 0
        for k in range(len(idx)):
            e = degs[k]
            for h in ring.monomials_upto(min(D - e, n)):
                if h == 0:
                    continue
                buf.append(ring.mul_mon(snapshot[k], Dm, e, h))
                nrows += 1
                if len(buf) >= CH:
                    grew |= W.add_rows(np.array(buf))
                    buf = []
                    if ideal_dim is not None and W.dim >= ideal_dim:
                        break
            if ideal_dim is not None and W.dim >= ideal_dim:
                break
        if buf:
            grew |= W.add_rows(np.array(buf))
        if log:
            log(f"      D={D} round {rounds}: rows={nrows} dim={W.dim} grew={grew}")
        if not grew:
            break
        productive += 1
    return W, rounds, productive


def dim_leq(W, ring, D, e):
    """dim( W n B_{<=e} ) using the descending-degree column order."""
    Dm = min(D, ring.n)
    if W.dim == 0:
        return 0
    degs = np.array([ring.deg_of_col(Dm, int(c)) for c in W.piv])
    return int(np.sum(degs <= e))


# ------------------------------------------------- ideal cap and certificate


def zero_set(gen, n, p):
    """Z = { z in {0,1}^n : S~(z) = 0 } via the subset (zeta) transform."""
    f = np.zeros(1 << n, dtype=np.int64)
    for m, c in gen.items():
        f[m] = c % p
    for i in range(n):
        bit = 1 << i
        idx = np.arange(1 << n)
        has = (idx & bit) != 0
        f[has] = (f[has] + f[idx[has] ^ bit]) % p
    return [int(z) for z in np.nonzero(f == 0)[0]]


def eval_matrix(Z, ring, D):
    """|Z| x N_D matrix of monomial evaluations (m(z) = 1 iff m subset z)."""
    Dm = min(D, ring.n)
    cols = ring.order[ring.off[Dm]:]
    M = np.zeros((len(Z), len(cols)))
    for i, z in enumerate(Z):
        for j, m in enumerate(cols):
            if (m & ~z) == 0:
                M[i, j] = 1.0
    return M


def ideal_cap_dim(Z, ring, D, p):
    """dim (I(Z) n B_{<=D}) = N_D - rank(eval matrix)."""
    Dm = min(D, ring.n)
    N = ring.ncols(Dm)
    if not Z:
        return N
    E, _ = _gauss(eval_matrix(Z, ring, D), p)
    return N - int(E.shape[0])


def eval_rank(Z, ring, D, p):
    if not Z:
        return 0
    E, _ = _gauss(eval_matrix(Z, ring, D), p)
    return int(E.shape[0])
