"""Lemma B-S instrument quantities (new): the reduced interpolant of
F(v_1, v_2) = 1 / S_3(v_1, v_2, x_R) on V x V (V in increasing integer order),
delta = max{a + b : Coef[a, b] != 0}, top = Coef[2^l - 1, 2^l - 1], and the
identity top == sum_{V x V} F / lambda_0^2 (spec object.regime_B.delta).

Phi is the 2^l x 2^l matrix mapping values on V to the coefficients of the
reduced univariate interpolant (exponents < 2^l): Phi = Vand^{-1} with
Vand[i, e] = v_i^e. Coef = Phi F Phi^T."""
import numpy as np


class MatGF:
    def __init__(self, F):
        self.F = F
        self.q1 = F.q1
        self.log = F.np_log.astype(np.int64)
        self.exp = np.concatenate([F.np_exp, F.np_exp[:1]]).astype(np.int64)

    def mul(self, A, B):
        A = np.asarray(A, dtype=np.int64)
        B = np.asarray(B, dtype=np.int64)
        la = self.log[A][:, :, None]
        lb = self.log[B][None, :, :]
        prod = self.exp[la + lb]
        prod[np.broadcast_to((A == 0)[:, :, None], prod.shape)] = 0
        prod[np.broadcast_to((B == 0)[None, :, :], prod.shape)] = 0
        return np.bitwise_xor.reduce(prod, axis=1)

    def inv(self, A):
        """Gauss-Jordan inverse over F_{2^n} (small matrices)."""
        F = self.F
        A = [list(map(int, r)) for r in np.asarray(A)]
        n = len(A)
        I = [[1 if i == j else 0 for j in range(n)] for i in range(n)]
        for c in range(n):
            p = next(r for r in range(c, n) if A[r][c] != 0)
            A[c], A[p] = A[p], A[c]
            I[c], I[p] = I[p], I[c]
            iv = F.inv(A[c][c])
            A[c] = [F.mul(iv, x) for x in A[c]]
            I[c] = [F.mul(iv, x) for x in I[c]]
            for r in range(n):
                if r != c and A[r][c] != 0:
                    f = A[r][c]
                    A[r] = [x ^ F.mul(f, y) for x, y in zip(A[r], A[c])]
                    I[r] = [x ^ F.mul(f, y) for x, y in zip(I[r], I[c])]
        return np.array(I, dtype=np.int64)


class DeltaCalc:
    def __init__(self, F, l, lam0):
        self.F, self.l = F, l
        self.mg = MatGF(F)
        q = 1 << l
        V = list(range(q))
        vand = np.zeros((q, q), dtype=np.int64)
        for i, v in enumerate(V):
            p = 1
            for e in range(q):
                vand[i, e] = p
                p = F.mul(p, v)
        self.vand = vand
        self.Phi = self.mg.inv(vand)
        self.PhiT = self.Phi.T.copy()
        self.lam0 = lam0
        self.inv_lam0_sq = F.inv(F.mul(lam0, lam0))
        a = np.arange(q)
        self.degsum = a[:, None] + a[None, :]

    def coef(self, Fvals):
        return self.mg.mul(self.mg.mul(self.Phi, Fvals), self.PhiT)

    def compute(self, g0vals_grid):
        """g0vals_grid: (2^l, 2^l) values of g_0 on V x V, all nonzero (unsat).
        Returns dict(delta, top, sum_over_lam0sq, identity_ok)."""
        F = self.F
        Fv = self.mg.exp[(self.q1_neg(self.mg.log[g0vals_grid]))]
        Cf = self.coef(Fv)
        nz = Cf != 0
        delta = int(self.degsum[nz].max()) if nz.any() else -1
        q = 1 << self.l
        top = int(Cf[q - 1, q - 1])
        s = int(np.bitwise_xor.reduce(Fv.reshape(-1)))
        rhs = F.mul(s, self.inv_lam0_sq)
        return {"delta": delta, "top": top, "sum_F_over_lam0_sq": rhs, "top_identity_ok": top == rhs}

    def q1_neg(self, lg):
        return (self.mg.q1 - lg) % self.mg.q1
