"""M_D quantities and the LITERAL mutant closure W_D, with wdag-v1 witness
extraction. Written from EXP-CERTBIN-e94b27 object.mutant_closure_W_D and
EXP-CERTBIN-ddfe75 object.certificate_format (wdag-v1) only.

W^(0) = rowspace(M_D);
W^(i+1) = W^(i) + span{ v_j * b : b in a basis of W^(i) cap B_{<=D-1}, j };
stop at the first i with dim W^(i+1) = dim W^(i).
The basis of W^(i) cap B_{<=D-1} is the set of RREF rows (descending
degrevlex columns) whose leading monomial has degree <= D-1. At EVERY
iteration the full basis is multiplied (BR-5).
"""
import numpy as np

import br_linalg as LA


def macaulay_stats(space, M_packed):
    """rank, "1 in rowspace", dims_by_deg (d = 0..D), P (rank of the
    projection on the degree-D monomials), plus an independent P route."""
    rows, piv, _ = LA.rref(M_packed, space.ncols, full=False)
    rank = len(piv)
    dbd = space.dims_by_deg(piv)
    one = space.const_col in piv
    # second route for P: rank of the degree-D columns alone
    topcols = np.flatnonzero(space.col_deg == space.D)
    assert topcols.size and topcols.max() < topcols.min() + topcols.size  # contiguous block first
    ntop = topcols.size
    # degree-D columns are the first ntop columns (degree-descending order)
    assert topcols[0] == 0 and topcols[-1] == ntop - 1
    _, pivtop, _ = LA.rref(M_packed, ntop, full=False)
    return {
        "rank": rank,
        "one": bool(one),
        "dims_by_deg": dbd,
        "P": rank - dbd[space.D - 1],
        "P_direct": len(pivtop),
    }


def vanishes_at(space, rows_packed, solutions):
    """True iff every row (a polynomial in B_{<=D}) evaluates to 0 at every
    assignment u in solutions (bit i of u = v_i)."""
    if rows_packed.shape[0] == 0 or not solutions:
        return True
    cm = space.col_masks
    for u in solutions:
        ev = ((cm & int(u)) == cm).astype(np.uint8)
        w = LA.pack(ev.reshape(1, -1))[0]
        par = np.bitwise_count(rows_packed & w).sum(axis=1) & 1
        if par.any():
            return False
    return True


class LevelZeroSolver:
    """Express an element of rowspace(M_D) as a sum of Macaulay rows."""

    def __init__(self, space, M_packed):
        self.space = space
        R = M_packed.shape[0]
        ident = np.eye(R, dtype=np.uint8)
        track = LA.pack(ident)
        A = np.concatenate([M_packed, track], axis=1)
        self.W = M_packed.shape[1]
        rows, piv, _ = LA.rref(A, space.ncols, full=True)
        self.rows = rows
        self.piv = piv
        self.R = R

    def express(self, y):
        """y: packed row in rowspace(M_D). Returns sorted list of row indices."""
        bits = LA.bits_at(y, self.piv)
        sel = self.rows[bits]
        acc = np.bitwise_xor.reduce(sel, axis=0) if sel.shape[0] else np.zeros(self.rows.shape[1], dtype=np.uint64)
        if not np.array_equal(acc[:self.W], y):
            raise ValueError("vector not in rowspace(M_D)")
        tr = LA.unpack(acc[self.W:].reshape(1, -1), self.R)[0]
        return [int(i) for i in np.flatnonzero(tr)]


class WClosure:
    def __init__(self, space, M_packed, keep_levels=True, max_iter=64):
        self.space = space
        self.M = M_packed
        self.keep = keep_levels
        self.max_iter = max_iter

    def run(self):
        sp = self.space
        D = sp.D
        R0, piv0, _ = LA.rref(self.M, sp.ncols, full=True)
        self.levels = [(R0, list(piv0))]
        self.trans = []          # per transition i -> i+1: (fallen_rows, chosen_labels, Pred_chosen)
        dims = [len(piv0)]
        fallen_counts = []
        one_first = 0 if sp.const_col in piv0 else None
        i = 0
        while True:
            Rr, pv = self.levels[-1]
            fidx = [q for q, c in enumerate(pv) if sp.col_deg[c] <= D - 1]
            fallen_counts.append(len(fidx))
            Fb = Rr[fidx]
            P, labels = sp.products(Fb)
            Pred = LA.reduce_by_rref(P, Rr, pv)
            Rp, pp, po = LA.rref(Pred, sp.ncols, full=True)
            dims.append(len(pv) + len(pp))
            if len(pp) == 0:
                break                        # dim W^(i+1) == dim W^(i): fixpoint at index i
            Rr2 = LA.reduce_by_rref(Rr, Rp, pp)
            rows = np.concatenate([Rr2, Rp], axis=0)
            cols = list(pv) + list(pp)
            order = np.argsort(np.asarray(cols), kind="stable")
            rows = rows[order]
            cols = [cols[q] for q in order]
            if self.keep:
                chosen = [labels[q] for q in po]
                self.trans.append((Fb, chosen, Pred[po]))
                self.levels.append((rows, cols))
            else:
                self.levels = [(rows, cols)]
            i += 1
            if one_first is None and sp.const_col in cols:
                one_first = i
            if i >= self.max_iter:
                raise RuntimeError("W_D iteration cap reached")
        Rf, pf = self.levels[-1]
        self.final_rows, self.final_piv = Rf, pf
        self.record = {
            "dims": dims,                         # dim W^(0), ..., dim W^(i+1) (last == previous)
            "fixpoint_index": i,                  # first i with dim W^(i+1) == dim W^(i)
            "final_dim": dims[-1],
            "one": one_first is not None,
            "one_first_iteration": one_first,
            "dims_by_deg": sp.dims_by_deg(pf),    # d = 0..D
            "fallen_basis_size_per_iteration": fallen_counts,
            "product_rows_per_iteration": [sp.nv * f for f in fallen_counts],
        }
        return self.record

    # ------------------------------------------------------------------
    # witness extraction (wdag-v1)
    # ------------------------------------------------------------------
    def in_level(self, y, L):
        Rr, pv = self.levels[L]
        return LA.is_zero(LA.reduce_vec(y, Rr, pv))

    def min_level(self, y):
        for L in range(len(self.levels)):
            if self.in_level(y, L):
                return L
        raise ValueError("vector not in W")

    def _solver(self, L):
        """Tracking RREF of the chosen reduced products of transition L-1 -> L."""
        if not hasattr(self, "_solvers"):
            self._solvers = {}
        if L not in self._solvers:
            Fb, chosen, Pc = self.trans[L - 1]
            d = Pc.shape[0]
            A = np.concatenate([Pc, LA.pack(np.eye(d, dtype=np.uint8))], axis=1)
            rows, piv, _ = LA.rref(A, self.space.ncols, full=True)
            self._solvers[L] = (rows, piv, d)
        return self._solvers[L]

    def decompose(self, y, L):
        """y in W^(L), L >= 1: returns (w, {j: g_j}) with y = w + sum_j v_j g_j,
        w in W^(L-1), g_j in W^(L-1) cap B_{<=D-1}."""
        sp = self.space
        Rprev, pprev = self.levels[L - 1]
        yp = LA.reduce_vec(y, Rprev, pprev)
        rows, piv, d = self._solver(L)
        W = sp.W
        bits = LA.bits_at(yp, piv)
        sel = rows[bits]
        acc = np.bitwise_xor.reduce(sel, axis=0) if sel.shape[0] else np.zeros(rows.shape[1], dtype=np.uint64)
        if not np.array_equal(acc[:W], yp):
            raise ValueError("decompose: not in W^(L)")
        S = np.flatnonzero(LA.unpack(acc[W:].reshape(1, -1), d)[0])
        Fb, chosen, Pc = self.trans[L - 1]
        groups = {}
        for q in S:
            j, m = chosen[int(q)]
            groups.setdefault(j, []).append(m)
        g = {}
        w = y.copy()
        for j, ms in sorted(groups.items()):
            gj = np.bitwise_xor.reduce(Fb[ms], axis=0)
            if not gj.any():
                continue
            g[j] = gj
            w ^= sp.product_one(j, gj)
        if not self.in_level(w, L - 1):
            raise ValueError("decompose: remainder not in W^(L-1)")
        return w, g

    def witness(self, lvl0, max_nodes=200000):
        """wdag-v1 witness of 1 in W_D. lvl0: LevelZeroSolver."""
        sp = self.space
        one = sp.one_row()
        nodes = []

        def add_node(rows, prods):
            nid = len(nodes)
            nodes.append({"id": nid, "rows": rows, "prods": prods})
            if len(nodes) > max_nodes:
                raise RuntimeError("witness too large")
            return nid

        def expand(y):
            L = self.min_level(y)
            if L == 0:
                ridx = lvl0.express(y)
                rows = [[list(sp.mus[r // sp.neq]), r % sp.neq] for r in ridx]
                return rows, []
            w, g = self.decompose(y, L)
            rows_w, prods_w = expand(w) if w.any() else ([], [])
            prods = list(prods_w)
            for j, gj in sorted(g.items()):
                r_g, p_g = expand(gj)
                cid = add_node(r_g, p_g)
                prods.append([int(j), cid])
            return rows_w, prods

        rows, prods = expand(one)
        out = add_node(rows, prods)
        return {"D": sp.D, "nv": sp.nv, "nodes": nodes, "output": out}
