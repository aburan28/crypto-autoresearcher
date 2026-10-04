"""Stage-3 linear algebra over Z/q (C-4): collector rank tracking, structured
Gaussian elimination (SGE), Lanczos, back-substitution. Every modular
multiplication is charged 1 unit and every inversion 10 (C-3, OQ-2); every
step is appended to an operation log whose counts the independent audit
recomputes from the logged dimensions (C-6 accounting audit).

System (kernel fixing, OQ-3). A relation sum_i c_i P_i = a_j G + b_j Q gives
the homogeneous row (c_1..c_L, -a_j, -b_j) over the columns (classes, G, Q).
Its kernel contains (log P_1..log P_L, 1, k); the collector stops at rank
ncols - 1 = L + 1 (plus 10 excess rows), where the kernel is one-dimensional,
and the kernel is fixed by log G = 1. Equivalently the solver works on the
inhomogeneous system with columns (classes, Q) and right-hand side a_j:
    sum_i c_i x_i - b_j x_Q = a_j.

SGE: repeat {delete a weight-1 column with its row; else merge on a weight-2
column (fraction-free: r2 <- r1[c] r2 - r2[c] r1)} until no column has
weight <= 2; the rest goes to Lanczos on B = A^T D A (D a label-derived
nonzero diagonal, retried with a fresh D on breakdown), then eliminated
columns are recovered by back-substitution.
"""

from __future__ import annotations

from arith import Zq


class LAFailure(RuntimeError):
    pass


# ------------------------------------------------------------------ rank tracker
class RankTracker:
    """Incremental row echelon basis over Z/q (charged: collector decision)."""

    def __init__(self, ncols: int, q: int, cost, log: list):
        self.n, self.q, self.Z, self.log = ncols, q, Zq(q, cost), log
        self.basis = {}  # pivot col -> dense normalized row

    @property
    def rank(self):
        return len(self.basis)

    def add(self, row: dict) -> bool:
        Z, q = self.Z, self.q
        snap_m, snap_i = Z.c.la_mul, Z.c.la_inv
        v = [0] * self.n
        for j, c in row.items():
            v[j] = c % q
        used = []
        for c in sorted(self.basis):
            if v[c]:
                b = self.basis[c]
                f = v[c]
                nz = 0
                for j in range(self.n):
                    if j != c and b[j]:
                        v[j] = (v[j] - Z.mul(f, b[j])) % q
                        nz += 1
                v[c] = 0
                used.append(nz + 1)  # nnz of the basis row incl. its pivot
        piv = next((j for j in range(self.n) if v[j]), None)
        nnz_v = 0
        if piv is not None:
            inv = Z.inv(v[piv])
            for j in range(self.n):
                if j != piv and v[j]:
                    v[j] = Z.mul(v[j], inv)
                    nnz_v += 1
            v[piv] = 1
            self.basis[piv] = v
            nnz_v += 1
        self.log.append({"step": "rank_reduce", "basis_nnz_used": used, "new_pivot": piv,
                         "new_row_nnz": nnz_v if piv is not None else 0,
                         "la_mul": Z.c.la_mul - snap_m, "la_inv": Z.c.la_inv - snap_i})
        return piv is not None


# ------------------------------------------------------------------ SGE
def sge(rows, rhs, ncols, Z, log):
    """Returns (active_rows, active_cols, elim_stack, rows, rhs); rows are mutated
    copies. Raises LAFailure('inconsistent') on a 0 = nonzero row."""
    q = Z.q
    rows = [dict(r) for r in rows]
    rhs = list(rhs)
    active_rows = set(range(len(rows)))
    active_cols = set(range(ncols))
    elim = []
    while active_cols:
        weights = {c: [] for c in active_cols}
        for r in sorted(active_rows):
            for c in rows[r]:
                if c in active_cols:
                    weights[c].append(r)
        zero = [c for c in sorted(active_cols) if not weights[c]]
        if zero:
            raise LAFailure(f"column {zero[0]} has weight 0 (rank deficient)")
        w1 = [c for c in sorted(active_cols) if len(weights[c]) == 1]
        if w1:
            c = w1[0]
            r = weights[c][0]
            elim.append((c, r))
            active_rows.discard(r)
            active_cols.discard(c)
            log.append({"step": "sge_singleton", "col": c, "row": r, "la_mul": 0, "la_inv": 0})
            continue
        w2 = [c for c in sorted(active_cols) if len(weights[c]) == 2]
        if not w2:
            break
        c = w2[0]
        r1, r2 = sorted(weights[c], key=lambda r: (len(rows[r]), r))
        snap = Z.c.la_mul
        piv, f = rows[r1][c], rows[r2][c]
        n1, n2 = len(rows[r1]), len(rows[r2])
        new = {}
        for j, v in rows[r2].items():
            new[j] = Z.mul(piv, v)
        for j, v in rows[r1].items():
            new[j] = (new.get(j, 0) - Z.mul(f, v)) % q
        new = {j: v for j, v in new.items() if v}
        rhs[r2] = (Z.mul(piv, rhs[r2]) - Z.mul(f, rhs[r1])) % q
        rows[r2] = new
        elim.append((c, r1))
        active_rows.discard(r1)
        active_cols.discard(c)
        log.append({"step": "sge_merge", "col": c, "pivot_row": r1, "row": r2, "pivot_nnz": n1,
                    "row_nnz": n2, "la_mul": Z.c.la_mul - snap, "la_inv": 0})
        if not new:  # active rows never hold eliminated columns, so the row is 0 = rhs
            active_rows.discard(r2)
            if rhs[r2]:
                raise LAFailure("inconsistent (0 = nonzero after merge)")
    for r in list(active_rows):
        if not rows[r]:
            active_rows.discard(r)
            if rhs[r]:
                raise LAFailure("inconsistent (0 = nonzero row)")
    return active_rows, active_cols, elim, rows, rhs


# ------------------------------------------------------------------ Lanczos
def lanczos(rows_c, rhs_c, nc, Z, log, dvals):
    """Solve A x = rhs (A: rows_c over compact columns 0..nc-1, consistent,
    full column rank) via Lanczos on B = A^T D A. Returns x or raises."""
    q = Z.q
    nr = len(rows_c)
    nnz = sum(len(r) for r in rows_c)

    def dot(u, v):
        s = 0
        for a, b in zip(u, v):
            if a and b:
                s += a * b
        Z.count(len(u))
        return s % q

    def apply_B(w):
        y = []
        for row in rows_c:
            s = 0
            for j, c in row.items():
                s += c * w[j]
            y.append(s % q)
        Z.count(nnz)
        y = [dvals[i] * y[i] % q for i in range(nr)]
        Z.count(nr)
        z = [0] * nc
        for i, row in enumerate(rows_c):
            yi = y[i]
            for j, c in row.items():
                z[j] += c * yi
        Z.count(nnz)
        return [v % q for v in z]

    snap = Z.c.la_mul
    b = [0] * nc
    for i, row in enumerate(rows_c):
        di = dvals[i] * rhs_c[i] % q
        for j, c in row.items():
            b[j] += c * di
    b = [v % q for v in b]
    Z.count(nr + nnz)
    log.append({"step": "lanczos_rhs", "nr": nr, "nc": nc, "nnz": nnz,
                "la_mul": Z.c.la_mul - snap, "la_inv": 0})
    x = [0] * nc
    w = b[:]
    w_prev = Bw_prev = inv_prev = None
    for it in range(nc + 2):
        if not any(w):
            break
        sm, si = Z.c.la_mul, Z.c.la_inv
        Bw = apply_B(w)
        wBw = dot(w, Bw)
        if wBw == 0:
            log.append({"step": "lanczos_iter", "nr": nr, "nc": nc, "nnz": nnz, "has_prev": w_prev is not None,
                        "breakdown": True, "la_mul": Z.c.la_mul - sm, "la_inv": Z.c.la_inv - si})
            raise LAFailure("lanczos breakdown (self-orthogonal w)")
        inv = Z.inv(wBw)
        coef = Z.mul(dot(w, b), inv)
        x = [(xi + coef * wi) % q for xi, wi in zip(x, w)]
        Z.count(nc)
        c1 = Z.mul(dot(Bw, Bw), inv)
        w_new = [(u - c1 * v) % q for u, v in zip(Bw, w)]
        Z.count(nc)
        has_prev = w_prev is not None
        if has_prev:
            c2 = Z.mul(dot(Bw, Bw_prev), inv_prev)
            w_new = [(u - c2 * v) % q for u, v in zip(w_new, w_prev)]
            Z.count(nc)
        log.append({"step": "lanczos_iter", "nr": nr, "nc": nc, "nnz": nnz, "has_prev": has_prev,
                    "breakdown": False, "la_mul": Z.c.la_mul - sm, "la_inv": Z.c.la_inv - si})
        w_prev, Bw_prev, inv_prev, w = w, Bw, inv, w_new
    else:
        raise LAFailure("lanczos did not terminate in nc + 2 iterations")
    sm = Z.c.la_mul
    ok = True
    for i, row in enumerate(rows_c):
        s = 0
        for j, c in row.items():
            s += c * x[j]
        if s % q != rhs_c[i] % q:
            ok = False
    Z.count(nnz)
    log.append({"step": "lanczos_check", "nr": nr, "nc": nc, "nnz": nnz, "ok": ok,
                "la_mul": Z.c.la_mul - sm, "la_inv": 0})
    if not ok:
        raise LAFailure("lanczos solution fails A x = rhs")
    return x


# ------------------------------------------------------------------ full solve
def solve(rows, rhs, ncols, q, cost, log, dlabel, max_tries: int = 8):
    """SGE -> Lanczos -> back-substitution. `dlabel(try, i)` returns a nonzero
    element of Z/q (row scaling). Returns (x, info) or raises LAFailure."""
    Z = Zq(q, cost)
    active_rows, active_cols, elim, rws, rh = sge(rows, rhs, ncols, Z, log)
    cols = sorted(active_cols)
    cidx = {c: i for i, c in enumerate(cols)}
    ar = sorted(active_rows)
    rows_c = [{cidx[j]: v for j, v in rws[r].items() if j in cidx} for r in ar]
    rhs_c = [rh[r] for r in ar]
    x_full = [None] * ncols
    tries = 0
    if cols:
        if len(ar) < len(cols):
            raise LAFailure(f"SGE left {len(ar)} rows for {len(cols)} columns")
        last = None
        for t in range(max_tries):
            tries += 1
            dvals = [dlabel(t, i) for i in range(len(ar))]
            try:
                xc = lanczos(rows_c, rhs_c, len(cols), Z, log, dvals)
                break
            except LAFailure as e:
                last = e
        else:
            raise LAFailure(f"lanczos failed {max_tries} tries: {last}")
        for c, v in zip(cols, xc):
            x_full[c] = v
    for c, r in reversed(elim):
        sm, si = Z.c.la_mul, Z.c.la_inv
        row = rws[r]
        s = rh[r]
        for j, v in row.items():
            if j != c:
                if x_full[j] is None:
                    raise LAFailure(f"back-substitution order: column {j} unsolved")
                s = (s - Z.mul(v, x_full[j])) % q
        x_full[c] = Z.mul(s, Z.inv(row[c]))
        log.append({"step": "backsub", "col": c, "row_nnz": len(row),
                    "la_mul": Z.c.la_mul - sm, "la_inv": Z.c.la_inv - si})
    if any(v is None for v in x_full):
        raise LAFailure("unsolved columns after back-substitution")
    return x_full, {"sge_eliminated": len(elim), "lanczos_rows": len(ar), "lanczos_cols": len(cols),
                    "lanczos_tries": tries}


# ------------------------------------------------------------------ reference
def gauss_reference(rows, rhs, ncols, q):
    """Uncharged dense Gauss-Jordan over Z/q (agreement check only). Returns the
    unique solution, or None if inconsistent or not full column rank."""
    M = []
    for r, b in zip(rows, rhs):
        v = [0] * (ncols + 1)
        for j, c in r.items():
            v[j] = c % q
        v[ncols] = b % q
        M.append(v)
    piv_row = 0
    pivots = []
    for c in range(ncols):
        pr = next((i for i in range(piv_row, len(M)) if M[i][c]), None)
        if pr is None:
            return None
        M[piv_row], M[pr] = M[pr], M[piv_row]
        inv = pow(M[piv_row][c], -1, q)
        M[piv_row] = [v * inv % q for v in M[piv_row]]
        for i in range(len(M)):
            if i != piv_row and M[i][c]:
                f = M[i][c]
                M[i] = [(a - f * b) % q for a, b in zip(M[i], M[piv_row])]
        pivots.append(c)
        piv_row += 1
    for i in range(piv_row, len(M)):
        if M[i][ncols]:
            return None
    return [M[i][ncols] for i in range(ncols)]
