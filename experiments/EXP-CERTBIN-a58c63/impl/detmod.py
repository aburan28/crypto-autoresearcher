"""INDEPENDENT determinant routine for C-BREAK (new; imports nothing from
regimeB.py or the solver). Own field tables (built here from the modulus), own
pivoting: Markowitz-style -- at each step, among the not-yet-eliminated rows
with a nonzero entry in the current column (columns taken in the order given),
the row with the FEWEST nonzeros is the pivot, ties to the LARGEST row index.
Characteristic 2: det = product of the pivots (no sign)."""
import numpy as np


class DetField:
    def __init__(self, n, mod):
        q1 = (1 << n) - 1
        exp = np.zeros(2 * q1 + 1, dtype=np.int64)
        log = np.zeros(1 << n, dtype=np.int64)
        x = 1
        for i in range(q1):
            exp[i] = x
            log[x] = i
            x <<= 1
            if x >> n:
                x ^= mod
        if x != 1:
            raise ValueError("generator check failed")
        exp[q1:2 * q1] = exp[:q1]
        exp[2 * q1] = exp[0]
        self.n, self.mod, self.q1, self.exp, self.log = n, mod, q1, exp, log


def determinant(A, DF):
    """A: square (k x k) integer array over F_{2^n}. Returns the determinant
    (an int; 0 iff singular)."""
    A = np.array(A, dtype=np.int64, copy=True)
    k = A.shape[0]
    if k == 0:
        return 1
    log, exp, q1 = DF.log, DF.exp, DF.q1
    active = np.ones(k, dtype=bool)
    nnz = (A != 0).sum(axis=1)
    logdet = 0
    for j in range(k):
        rows = np.flatnonzero((A[:, j] != 0) & active)
        if rows.size == 0:
            return 0
        best = rows[nnz[rows] == nnz[rows].min()]
        p = int(best[-1])
        pv = int(A[p, j])
        logdet = (logdet + int(log[pv])) % q1
        active[p] = False
        others = rows[rows != p]
        if others.size:
            J = np.flatnonzero(A[p, j:]) + j
            lp = log[A[p, J]]
            lf = (log[A[others, j]] - log[pv]) % q1
            A[np.ix_(others, J)] ^= exp[lf[:, None] + lp[None, :]]
            nnz[others] = (A[others] != 0).sum(axis=1)
    return int(exp[logdet])


def minor(M, rows, cols, DF):
    return determinant(np.asarray(M)[np.ix_(np.asarray(rows, dtype=np.int64), np.asarray(cols, dtype=np.int64))], DF)
