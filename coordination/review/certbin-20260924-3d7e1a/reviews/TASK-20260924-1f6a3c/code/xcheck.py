"""Independent second computation of rank_3, rank_4, dim(R_4 cap B_{<=d}) and the W_4
iterates at full scale (18 variables), sharing NO code with boolsys/gf2lin/closure.

  * its own column order: degree DESCENDING, and within a degree the reverse of
    itertools.combinations order (not degrevlex; the quantities do not depend on
    the within-degree order);
  * rows built from the hand-formula equations of wcert_check (or the explicit
    lists), with its own mu*f_k products;
  * packed uint64 matrices and vectorised Gauss-Jordan (full RREF);
  * W^(i) cap B_{<=3} = RREF rows whose pivot column has degree <= 3 (in RREF with
    all degree-4 columns first, such a row is zero on every degree-4 column).
"""
import itertools

import numpy as np

NV = 18
NEQ = 17


class XCheck:
    def __init__(self, D=4):
        self.D = D
        cols = []
        for d in range(D, -1, -1):
            block = []
            for c in itertools.combinations(range(NV), d):
                m = 0
                for i in c:
                    m |= 1 << i
                block.append(m)
            cols.extend(reversed(block))
        self.cols = cols
        self.C = len(cols)
        self.col = {m: i for i, m in enumerate(cols)}
        self.deg = np.array([bin(m).count("1") for m in cols])
        self.W = (self.C + 63) // 64
        self.const_col = self.col[0]
        # product gather tables: for target column t containing v_j,
        # (v_j g)[t] = g[t] (if deg t <= D-1) + g[t \\ v_j]
        self.tgt, self.sA, self.sB = [], [], []
        pad = self.C
        for j in range(NV):
            T, A, B = [], [], []
            for t, m in enumerate(cols):
                if (m >> j) & 1:
                    T.append(t)
                    A.append(t if bin(m).count("1") <= D - 1 else pad)
                    B.append(self.col[m & ~(1 << j)])
            self.tgt.append(np.array(T))
            self.sA.append(np.array(A))
            self.sB.append(np.array(B))

    def mus(self, dmax):
        out = []
        for d in range(dmax + 1):
            for c in itertools.combinations(range(NV), d):
                m = 0
                for i in c:
                    m |= 1 << i
                out.append(m)
        return out

    def rows_bool(self, eqs, D):
        mus = self.mus(D - 2)
        M = np.zeros((len(mus) * NEQ, self.C), dtype=np.uint8)
        r = 0
        for mu in mus:
            for k in range(NEQ):
                for m in eqs[k]:
                    M[r, self.col[m | mu]] ^= 1
                r += 1
        return M

    def pack(self, Mb):
        P = np.packbits(Mb, axis=1, bitorder="little")
        pad = self.W * 8 - P.shape[1]
        if pad:
            P = np.concatenate([P, np.zeros((P.shape[0], pad), dtype=np.uint8)], axis=1)
        return np.ascontiguousarray(P).view(np.uint64).copy()

    def unpack(self, P):
        return np.unpackbits(P.view(np.uint8), axis=1, bitorder="little")[:, :self.C]

    def rref(self, P):
        """Vectorised Gauss-Jordan over F_2 on a packed matrix; returns (RREF rows, pivot cols)."""
        P = P.copy()
        R = P.shape[0]
        r = 0
        piv = []
        for c in range(self.C):
            if r >= R:
                break
            w, b = divmod(c, 64)
            colbits = (P[r:, w] >> np.uint64(b)) & np.uint64(1)
            nz = np.flatnonzero(colbits)
            if nz.size == 0:
                continue
            p = r + int(nz[0])
            if p != r:
                tmp = P[r].copy()
                P[r] = P[p]
                P[p] = tmp
            allbits = (P[:, w] >> np.uint64(b)) & np.uint64(1)
            allbits[r] = 0
            idx = np.flatnonzero(allbits)
            if idx.size:
                P[idx] ^= P[r]
            piv.append(c)
            r += 1
        return P[:r], piv

    def products(self, Pl):
        X = self.unpack(Pl)
        Xp = np.concatenate([X, np.zeros((X.shape[0], 1), dtype=np.uint8)], axis=1)
        out = []
        for j in range(NV):
            Y = np.zeros((X.shape[0], self.C), dtype=np.uint8)
            Y[:, self.tgt[j]] = Xp[:, self.sA[j]] ^ Xp[:, self.sB[j]]
            out.append(self.pack(Y))
        return np.concatenate(out, axis=0) if out else np.zeros((0, self.W), np.uint64)

    def run(self, eqs, max_iter=64):
        D = self.D
        M3 = self.pack(self.rows_bool(eqs, 3)[:, :])  # M_3 rows embedded in degree<=4 columns
        R3, piv3 = self.rref(M3)
        M4 = self.pack(self.rows_bool(eqs, 4))
        R4, piv4 = self.rref(M4)
        pdeg4 = self.deg[piv4] if piv4 else np.array([], dtype=int)
        out = {
            "rank_3": len(piv3),
            "one_in_R3": self.const_col in piv3,
            "rank_4": len(piv4),
            "one_in_R4": self.const_col in piv4,
            "R4_cap_dims": [int(np.sum(pdeg4 <= d)) for d in range(4)],
        }
        Wm, piv = R4, piv4
        dims = [len(piv)]
        first = 0 if self.const_col in piv else None
        it = 0
        while True:
            pdeg = self.deg[piv]
            low = Wm[pdeg <= D - 1]
            prods = self.products(low)
            Wm, piv = self.rref(np.concatenate([Wm, prods], axis=0))
            it += 1
            dims.append(len(piv))
            if first is None and self.const_col in piv:
                first = it
            if dims[-1] == dims[-2]:
                break
            if it >= max_iter:
                raise RuntimeError("no fixpoint")
        pdeg = self.deg[piv]
        out.update({"W4_dims": dims, "W4_fixpoint_index": it - 1, "W4_first_one_iteration": first,
                    "W4_final_dim": len(piv), "W4_cap_dims": [int(np.sum(pdeg <= d)) for d in range(D + 1)]})
        return out
