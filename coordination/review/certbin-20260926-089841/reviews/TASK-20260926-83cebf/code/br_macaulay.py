"""Macaulay matrices M_D and the multiplication maps v_j * (.), written from
EXP-CERTBIN-4e92d7 object.macaulay_matrix (conventions reused by
EXP-CERTBIN-e94b27 object.macaulay_M_D).

ROWS: one row per pair (mu, k), mu over the multilinear monomials of degree
<= D-2 ordered by (degree ascending, then ascending sorted index tuple),
k = 0..neq-1; row index = (index of mu) * neq + k; the row is the multilinear
reduction of mu * f_k; zero rows are retained.
COLUMNS: every multilinear monomial of degree <= D in DESCENDING degrevlex
order, constant LAST: a > b iff deg a > deg b, or deg a = deg b and at the
largest variable index i where a and b differ, a does NOT contain v_i.
"""
import numpy as np

from br_system import mu_order, mask_of
import br_linalg as LA


def degrevlex_desc(monos, nv):
    def key(m):
        s = set(m)
        return (len(m), tuple(0 if i in s else -1 for i in reversed(range(nv))))
    # a > b iff key(a) > key(b): at the largest differing index the monomial
    # WITHOUT that variable has 0 > -1.
    return sorted(monos, key=key, reverse=True)


class Space:
    """The column space B_{<=D} in nv variables, with the Macaulay row set for
    systems of neq quadratic equations (columns in mu_order(2, nv))."""

    def __init__(self, nv, D, neq):
        self.nv, self.D, self.neq = nv, D, neq
        monos = degrevlex_desc(mu_order(D, nv), nv)
        self.col_monos = monos
        self.col_masks = np.array([mask_of(m) for m in monos], dtype=np.int64)
        self.ncols = len(monos)
        self.W = LA.nwords(self.ncols)
        self.colidx = np.full(1 << nv, -1, dtype=np.int64)
        self.colidx[self.col_masks] = np.arange(self.ncols)
        self.col_deg = np.array([len(m) for m in monos], dtype=np.int64)
        assert self.col_deg[-1] == 0 and self.ncols - 1 == int(self.colidx[0])
        self.const_col = self.ncols - 1
        # row multipliers
        self.mus = mu_order(D - 2, nv)
        self.mu_masks = np.array([mask_of(m) for m in self.mus], dtype=np.int64)
        self.nrows = len(self.mus) * neq
        # system columns (degree <= 2) and the product target table
        self.sys_monos = mu_order(2, nv)
        self.sys_masks = np.array([mask_of(m) for m in self.sys_monos], dtype=np.int64)
        tgt_masks = self.mu_masks[:, None] | self.sys_masks[None, :]
        self.target = self.colidx[tgt_masks]
        assert (self.target >= 0).all()
        # multiplication by v_j: for each column t containing v_j, the source
        # column t \ {v_j}; new[t] = old[t] + old[t \ {v_j}]
        self.mult = []
        for j in range(nv):
            bit = 1 << j
            tj = np.flatnonzero((self.col_masks & bit) != 0)
            sj = self.colidx[self.col_masks[tj] ^ bit]
            assert (sj >= 0).all()
            self.mult.append((tj, sj))

    # ------------------------------------------------------------------
    def build_dense(self, E):
        """E: (neq, len(sys_monos)) 0/1. Returns the dense (nrows, ncols) M_D."""
        assert E.shape == (self.neq, len(self.sys_monos)), E.shape
        M = np.zeros((self.nrows, self.ncols), dtype=np.uint8)
        nmu = len(self.mus)
        base = np.arange(nmu) * self.neq
        ks, ms = np.nonzero(E)
        for k, m in zip(ks, ms):
            M[base + k, self.target[:, m]] ^= 1
        return M

    def build(self, E):
        return LA.pack(self.build_dense(E))

    def row_label(self, r):
        return (list(self.mus[r // self.neq]), r % self.neq)

    # ------------------------------------------------------------------
    def products(self, rows_packed):
        """All v_j * b for b in rows (each of degree <= D-1), j = 0..nv-1.
        Returns (packed products, labels) with label (j, m), block order j
        outer, m inner."""
        f = rows_packed.shape[0]
        if f == 0:
            return np.zeros((0, self.W), dtype=np.uint64), []
        dense = LA.unpack(rows_packed, self.ncols)
        topdeg = self.col_deg == self.D
        assert not dense[:, topdeg].any(), "multiplying a row of degree D"
        out = np.zeros((self.nv * f, self.ncols), dtype=np.uint8)
        for j, (tj, sj) in enumerate(self.mult):
            blk = out[j * f:(j + 1) * f]
            blk[:, tj] = dense[:, tj] ^ dense[:, sj]
        labels = [(j, m) for j in range(self.nv) for m in range(f)]
        return LA.pack(out), labels

    def product_one(self, j, row_packed):
        dense = LA.unpack(row_packed.reshape(1, -1), self.ncols)[0]
        out = np.zeros(self.ncols, dtype=np.uint8)
        tj, sj = self.mult[j]
        out[tj] = dense[tj] ^ dense[sj]
        return LA.pack(out.reshape(1, -1))[0]

    def dims_by_deg(self, piv_cols):
        """dim(X cap B_{<=d}) for d = 0..D, from the leading columns of an
        echelon basis in this (degree-descending) column order."""
        degs = self.col_deg[np.asarray(piv_cols, dtype=np.int64)] if piv_cols else np.zeros(0, dtype=np.int64)
        return [int(np.count_nonzero(degs <= d)) for d in range(self.D + 1)]

    def poly_of_row(self, row_packed):
        """The set of monomial masks of a packed row."""
        dense = LA.unpack(row_packed.reshape(1, -1), self.ncols)[0]
        return set(int(x) for x in self.col_masks[np.flatnonzero(dense)])

    def row_of_poly(self, masks):
        v = np.zeros(self.ncols, dtype=np.uint8)
        for m in masks:
            c = int(self.colidx[m])
            assert c >= 0
            v[c] ^= 1
        return LA.pack(v.reshape(1, -1))[0]

    def one_row(self):
        return self.row_of_poly([0])
