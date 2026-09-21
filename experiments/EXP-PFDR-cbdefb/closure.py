"""The V_{F,D} last-fall closure instrument of EXP-PFDR-cbdefb (TASK-20260903-6745ea).

Frozen convention (stage1-closure-convention.md, written before the first official run):

    Ambient space.  B_{<=D} = the span of the ring monomials of total degree <= D in the
    meter's Ring (squarefree digit mode B = F_p[a]/(a^2 - a) for d = 2; the ordinary
    polynomial ring with explicit membership generators for d > 2 and for the s = 1
    direct presentation).  Degree = the meter's reduced total degree.

    W_0(D)  = V_{F,D-1}  +  span{ m * f : f in F, m a ring monomial, deg m <= D - deg f }
              (the meter's cumulative Macaulay row space at D, reduced rows; V_{F,D_min-1} = 0).
    Pass t  : F_t = W_t cap B_{<=D-1}  (the fall space: echelon rows whose pivot lies below
              the degree-D block);  W_{t+1} = W_t + sum_i  a_i * F_t  over all ring variables.
    V_{F,D} = the fixed point.  Fall at D  <=>  dim(V_{F,D} cap B_{<=D-1}) > dim V_{F,D-1}.
    d_ff = least D with a fall; d_lf = largest D <= D_max with a fall.
    iteration_count(D) = (number of passes that inserted at least one new pivot) + 1.

Section 2 of the note derives that this is exactly the image, under reduction modulo the
field equations, of Huang-Kosters-Yeo's V_{F,D} computed in the polynomial ring with the
field equations a(a - 1) as members of F; "multiply by all monomials keeping degree <= D"
is realised as iterated multiplication of fallen elements by single variables (every
intermediate product of a fallen element stays fallen or lands in degree D, so the two
readings generate the same space).

Two engines with identical semantics:
  * SPARSE  -- the shared meter's exact Echelon (harness/macaulay_fp/linalg.py), dict rows.
               The reference engine; used for every system whose column space at D_max has
               at most SPARSE_COLUMN_LIMIT columns, and on a declared subsample above it.
  * DENSE   -- float64 reduced row echelon with BLAS matrix products and a reduction mod p
               after every product.  Exact: all partial sums are bounded by rank * p^2
               <= 1024 * 65537^2 < 2^53 (asserted at construction), so every float64 value
               is an exact integer.  Used above SPARSE_COLUMN_LIMIT; wherever both run, the
               histories must agree integer for integer (cross_check).

Completeness certificate (censoring flag), squarefree rings only:
  In B every ideal is radical, so I = ideal(F) = I(Z) with Z = common zeros in {0,1}^n and
  dim(I cap B_{<=D}) = N_D - r_D, r_D = rank of evaluation at Z on B_{<=D}.
  (S) structural: every fall occurs at some D <= n + 1 (V_{F,n+1} is an ideal), so
      D_max >= n + 1 certifies the history complete.
  (C1) dim V_{F,D_max} == N_{D_max} - r_{D_max}.
  (C2) for D = D_max+1 .. n:  I cap B_{<=D} == (I cap B_{<=D-1}) + sum_i a_i (I cap B_{<=D-1}),
       decided by the dual (annihilator) dimension; C2(n + 1) is trivial.
  C1 and every C2 imply V_{F,D} = I cap B_{<=D} for every D >= D_max, hence no fall above
  D_max.  A draw whose history is neither structurally nor (C1 + C2)-certified is
  RIGHT-CENSORED and never enters a slope fit.  Ordinary rings: never certified.
"""
from __future__ import annotations

import os
import time
from typing import Dict, List, Optional, Sequence, Tuple

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")          # contract: maximum_workers 1

import numpy as np  # noqa: E402

from harness.macaulay_fp import ColumnSpace, Ring, analyze_layer  # noqa: E402
from harness.macaulay_fp.linalg import Echelon  # noqa: E402
from harness.macaulay_fp.macaulay import layer_rows  # noqa: E402
from harness.macaulay_fp.poly import Poly  # noqa: E402

SPARSE_COLUMN_LIMIT = 256
CERTIFICATE_COLUMN_LIMIT = 1024      # certificate attempted only when the full ring has <= this many monomials

CONVENTION_ID = "cbdefb-closure-v1: cumulative-Macaulay W0 + V_{F,D-1}; fallen x variables to fixed point; reduced degree; fall iff dim(V_D cap B_{<=D-1}) > dim V_{D-1}"


# ----------------------------------------------------------------------------------------
# variable tables
# ----------------------------------------------------------------------------------------
def variable_monomials(ring: Ring):
    return [ring.sq_var(i) for i in range(ring.n_sq)] + [ring.free_var(j) for j in range(ring.n_free)]


def multiplication_table(ring: Ring, columns: ColumnSpace) -> np.ndarray:
    """T[i, j] = column index of (variable i) * (monomial j), or -1 if outside the column space."""
    vars_ = variable_monomials(ring)
    T = np.full((len(vars_), columns.ncols), -1, dtype=np.int64)
    for j, m in enumerate(columns.monomials):
        for i, v in enumerate(vars_):
            T[i, j] = columns.index.get(ring.mono_mul(m, v), -1)
    return T


# ----------------------------------------------------------------------------------------
# dense exact RREF over F_p
# ----------------------------------------------------------------------------------------
class DenseRREF:
    """Reduced row echelon form over F_p; pivot = highest nonzero column; float64 exact."""

    CHUNK = 256

    def __init__(self, p: int, ncols: int) -> None:
        if p * p * (ncols + 1) >= 2 ** 53:
            raise ValueError("dense engine exactness bound violated")
        self.p = p
        self.N = ncols
        self.M = np.zeros((0, ncols))
        self.pivcols = np.zeros(0, dtype=np.int64)
        self.matmul_flops = 0

    @property
    def rank(self) -> int:
        return int(self.M.shape[0])

    def _reduce(self, R: np.ndarray) -> np.ndarray:
        if self.rank == 0 or R.shape[0] == 0:
            return R % self.p
        F = R[:, self.pivcols]
        if not F.any():
            return R % self.p
        self.matmul_flops += 2 * R.shape[0] * self.rank * self.N
        return np.rint(R - F @ self.M) % self.p

    def _rref_small(self, R: np.ndarray) -> Tuple[List[np.ndarray], List[int]]:
        """RREF of a residual block already reduced against the pivots (rows zero at pivot columns)."""
        p = self.p
        rows: List[np.ndarray] = []
        cols: List[int] = []
        R = R.copy()
        while True:
            nz = R != 0
            live = nz.any(axis=1)
            if not live.any():
                break
            lead = np.where(live, self.N - 1 - np.argmax(nz[:, ::-1], axis=1), -1)
            i = int(np.argmax(lead))
            c = int(lead[i])
            row = np.rint(R[i] * pow(int(R[i, c]), -1, p)) % p
            f = R[:, c]
            R = np.rint(R - np.outer(f, row)) % p
            for k in range(len(rows)):
                fk = rows[k][c]
                if fk:
                    rows[k] = np.rint(rows[k] - fk * row) % p
            rows.append(row)
            cols.append(c)
        return rows, cols

    def add_batch(self, R: np.ndarray) -> int:
        """Insert rows (K x N, entries in [0, p)); returns the number of new pivots."""
        p = self.p
        inserted = 0
        R = np.asarray(R, dtype=np.float64)
        for start in range(0, R.shape[0], self.CHUNK):
            blk = self._reduce(R[start:start + self.CHUNK])
            if not blk.any():
                continue
            rows, cols = self._rref_small(blk)
            if not rows:
                continue
            NR = np.stack(rows)
            NC = np.array(cols, dtype=np.int64)
            if self.rank:
                G = self.M[:, NC]
                if G.any():
                    self.matmul_flops += 2 * self.rank * len(cols) * self.N
                    self.M = np.rint(self.M - G @ NR) % p
            self.M = np.vstack([self.M, NR])
            self.pivcols = np.concatenate([self.pivcols, NC])
            inserted += len(rows)
        return inserted

    def extend_columns(self, ncols: int) -> "DenseRREF":
        E = DenseRREF(self.p, ncols)
        E.M = np.hstack([self.M, np.zeros((self.rank, ncols - self.N))])
        E.pivcols = self.pivcols.copy()
        return E


# ----------------------------------------------------------------------------------------
# closure drivers
# ----------------------------------------------------------------------------------------
def _degree_of_column(columns: ColumnSpace, col: int) -> int:
    for d in range(columns.max_degree + 1):
        if columns.degree_start[d] <= col < columns.degree_end[d]:
            return d
    raise ValueError("column outside the column space")


def closure_dense(ring: Ring, gens: Sequence[Poly], columns: ColumnSpace, dmin: int, dmax: int,
                  T: Optional[np.ndarray] = None, want_basis: bool = False) -> dict:
    p = ring.p
    if T is None:
        T = multiplication_table(ring, columns)
    nvar = T.shape[0]
    prev: Optional[DenseRREF] = None
    prev_dim = 0
    prev_processed = 0          # rows of prev with pivot below the degree-(D-1) block were multiplied at D-1
    history = []
    for D in range(dmin, dmax + 1):
        t0 = time.monotonic()
        N = columns.ncols_upto(D)
        top_start = columns.degree_start[D]
        if prev is None:
            E = DenseRREF(p, N)
            rows, _, _ = layer_rows(ring, gens, D, "cumulative")
            already = 0
        else:
            E = prev.extend_columns(N)
            rows, _, _ = layer_rows(ring, gens, D, "per_layer")
            rows = [r for r in rows if r]
            already = prev_processed
        # rows of the carried basis that were fallen at D-1 (pivot < degree_start[D-1]) were multiplied at D-1
        processed_mask = np.zeros(E.rank, dtype=bool)
        if prev is not None:
            processed_mask[:] = E.pivcols < columns.degree_start[D - 1]
        if rows:
            R = np.zeros((len(rows), N))
            for k, poly in enumerate(rows):
                for m, c in poly.items():
                    R[k, columns.index[m]] = c
            E.add_batch(R)
        dim_w0 = E.rank
        processed = list(processed_mask) + [False] * (E.rank - len(processed_mask))
        passes = []
        growth = 0
        while True:
            fm = E.pivcols < top_start
            idx = [i for i in range(E.rank) if fm[i] and not processed[i]]
            for i in idx:
                processed[i] = True
            inserted = 0
            if idx:
                new = E.M[idx]
                low = new[:, :top_start]
                if new[:, top_start:].any():
                    raise AssertionError("fall row with a degree-D component")
                K = len(idx)
                prods = np.zeros((nvar * K, N))
                for i in range(nvar):
                    tgt = T[i, :top_start]
                    ok = tgt >= 0
                    src_cols = np.nonzero(ok)[0]
                    blk = prods[i * K:(i + 1) * K]
                    # a variable maps a monomial either to itself (variable already present) or to a
                    # strictly larger monomial; both maps are injective on their domain, so two
                    # fancy-index accumulations realise the scatter without np.add.at
                    same = src_cols[tgt[src_cols] == src_cols]
                    move = src_cols[tgt[src_cols] != src_cols]
                    if len(same):
                        blk[:, same] += low[:, same]
                    if len(move):
                        blk[:, tgt[move]] += low[:, move]
                prods %= p
                before = E.rank
                inserted = E.add_batch(prods)
                processed.extend([False] * (E.rank - before))
            passes.append([len(idx), inserted])
            if inserted > 0:
                growth += 1
            else:
                break
        fall_dim = int((E.pivcols < top_start).sum())
        history.append({
            "D": D, "ncols": N, "ncols_top": N - top_start, "dim_W0": dim_w0, "dim_V": E.rank,
            "fall_dim": fall_dim, "dim_V_prev": prev_dim, "new_fall": fall_dim - prev_dim,
            "fall": fall_dim > prev_dim, "iteration_count": growth + 1, "passes_with_growth": growth,
            "passes": passes, "seconds": round(time.monotonic() - t0, 3),
        })
        prev, prev_dim = E, E.rank
        prev_processed = fall_dim
    out = {"engine": "dense", "history": history}
    if want_basis and prev is not None:
        out["basis"] = prev
    return out


def closure_sparse(ring: Ring, gens: Sequence[Poly], columns: ColumnSpace, dmin: int, dmax: int) -> dict:
    """Reference engine: the shared meter's Echelon, same semantics as closure_dense."""
    p = ring.p
    vars_ = variable_monomials(ring)
    prev_rows: List[Tuple[int, dict]] = []      # (pivot, row) of V_{F,D-1}
    prev_dim = 0
    history = []
    for D in range(dmin, dmax + 1):
        t0 = time.monotonic()
        top_start = columns.degree_start[D]
        E = Echelon(p, top_start=top_start)
        processed = set()
        for piv, row in sorted(prev_rows, key=lambda x: -x[0]):
            E.add(dict(row))
            if piv < columns.degree_start[D - 1]:
                processed.add(piv)
        rows, _, _ = layer_rows(ring, gens, D, "cumulative" if not prev_rows else "per_layer")
        for poly in rows:
            if poly:
                E.add(E.encode(columns.encode(poly)))
        dim_w0 = E.rank
        passes = []
        growth = 0
        while True:
            new = [c for c in E.pivots if c < top_start and c not in processed]
            inserted = 0
            for c in sorted(new, reverse=True):
                processed.add(c)
                poly = columns.decode(E.pivots[c])
                for v in vars_:
                    prod = ring.mul_monomial(poly, v)
                    if prod and E.add(E.encode(columns.encode(prod))):
                        inserted += 1
            passes.append([len(new), inserted])
            if inserted > 0:
                growth += 1
            else:
                break
        fall_dim = sum(1 for c in E.pivots if c < top_start)
        history.append({
            "D": D, "ncols": columns.ncols_upto(D), "ncols_top": columns.ncols_exact(D), "dim_W0": dim_w0,
            "dim_V": E.rank, "fall_dim": fall_dim, "dim_V_prev": prev_dim, "new_fall": fall_dim - prev_dim,
            "fall": fall_dim > prev_dim, "iteration_count": growth + 1, "passes_with_growth": growth,
            "passes": passes, "seconds": round(time.monotonic() - t0, 3),
        })
        prev_rows = [(c, E.pivots[c]) for c in E.pivots]
        prev_dim = E.rank
    return {"engine": "sparse", "history": history}


HISTORY_KEYS = ("D", "dim_W0", "dim_V", "fall_dim", "dim_V_prev", "new_fall", "fall", "iteration_count", "passes")


def histories_agree(h1: List[dict], h2: List[dict]) -> bool:
    if len(h1) != len(h2):
        return False
    return all(all(a[k] == b[k] for k in HISTORY_KEYS) for a, b in zip(h1, h2))


# ----------------------------------------------------------------------------------------
# graded-rank (per-layer meter) first fall, for CTRL-DFF-AGREEMENT / P1
# ----------------------------------------------------------------------------------------
def graded_profile(ring: Ring, gens: Sequence[Poly], columns: ColumnSpace, dmin: int, dmax: int) -> dict:
    layers = []
    d_ff = None
    for D in range(dmin, dmax + 1):
        L = analyze_layer(ring, gens, D, "per_layer", columns, frobenius=False)
        layers.append({"D": D, "rows": L.row_count, "full_rank": L.full_rank, "top_rank": L.top_rank,
                       "fall_dim": L.fall_dim})
        if L.fall_dim > 0 and d_ff is None:
            d_ff = D
    return {"graded_d_ff": d_ff, "layers": layers}


# ----------------------------------------------------------------------------------------
# zeros, ideal dimensions, completeness certificate (squarefree rings)
# ----------------------------------------------------------------------------------------
def evaluation_matrix(ring: Ring, columns: ColumnSpace) -> np.ndarray:
    """Ev[z, j] = monomial_j(z) for z in {0,1}^n (z as a bitmask), squarefree ring only."""
    n = ring.n_sq
    masks = np.array([m[0] for m in columns.monomials], dtype=np.int64)
    zs = np.arange(1 << n, dtype=np.int64)
    return ((masks[None, :] & ~zs[:, None]) == 0).astype(np.float64)


def zero_set(ring: Ring, gens: Sequence[Poly], columns: ColumnSpace, Ev: np.ndarray) -> List[int]:
    p = ring.p
    alive = np.ones(Ev.shape[0], dtype=bool)
    for g in gens:
        v = np.zeros(columns.ncols)
        for m, c in g.items():
            v[columns.index[m]] = c
        vals = np.rint(Ev @ v) % p
        alive &= vals == 0
    return [int(z) for z in np.nonzero(alive)[0]]


def _rref_dict(p: int, rows: List[dict]) -> Tuple[Dict[int, dict], int]:
    E = Echelon(p)
    for r in rows:
        E.add(dict(r))
    piv = sorted(E.pivots)
    rref = {c: dict(E.pivots[c]) for c in piv}
    for c in piv:
        prow = rref[c]
        for c2 in piv:
            if c2 == c:
                continue
            r2 = rref[c2]
            f = r2.get(c, 0)
            if f:
                for col, v in prow.items():
                    nv = (r2.get(col, 0) - f * v) % p
                    if nv:
                        r2[col] = nv
                    else:
                        r2.pop(col, None)
    return rref, len(piv)


def _eval_rows(Ev: np.ndarray, Z: List[int], N: int) -> List[dict]:
    return [{j: 1 for j in np.nonzero(Ev[z, :N])[0].tolist()} for z in Z]


def ideal_dimension(Ev: np.ndarray, Z: List[int], N: int, p: int) -> Tuple[int, int]:
    """(dim(I cap B_{<=D}), r_D) for the column count N of degree <= D."""
    rows = _eval_rows(Ev, Z, N)
    E = Echelon(p)
    for r in rows:
        E.add(r)
    return N - E.rank, E.rank


def c2_check(ring: Ring, columns: ColumnSpace, Ev: np.ndarray, Z: List[int], D: int, T: np.ndarray) -> dict:
    """C2(D): codim of (I_{<=D-1} + sum_i a_i I_{<=D-1}) in B_{<=D} equals r_D."""
    p = ring.p
    n = ring.n_sq
    N_prev = columns.ncols_upto(D - 1)
    N_D = columns.ncols_upto(D)
    rref_prev, r_prev = _rref_dict(p, _eval_rows(Ev, Z, N_prev))
    _, r_D = ideal_dimension(Ev, Z, N_D, p)
    piv = sorted(rref_prev)
    pivset = set(piv)
    Ebasis = [rref_prev[c] for c in piv]
    kernel = []
    for fcol in range(N_prev):
        if fcol in pivset:
            continue
        k = {fcol: 1}
        for c in piv:
            v = rref_prev[c].get(fcol, 0)
            if v:
                k[c] = (-v) % p
        kernel.append(k)
    top_cols = list(range(N_prev, N_D))
    nunk = r_prev + len(top_cols)
    tidx = {c: r_prev + i for i, c in enumerate(top_cols)}

    def lam(j: int) -> dict:
        if j >= N_prev:
            return {tidx[j]: 1}
        out = {}
        for k, e in enumerate(Ebasis):
            v = e.get(j, 0)
            if v:
                out[k] = v
        return out

    cons = Echelon(p)
    for i in range(n):
        for kv in kernel:
            row: dict = {}
            for g, coef in kv.items():
                tgt = int(T[i, g])
                for u, v in lam(tgt).items():
                    nv = (row.get(u, 0) + coef * v) % p
                    if nv:
                        row[u] = nv
                    else:
                        row.pop(u, None)
            if row:
                cons.add(row)
    codim = nunk - cons.rank
    return {"D": D, "codim_rhs": codim, "r_D": r_D, "holds": codim == r_D}


def certify_history(ring: Ring, gens: Sequence[Poly], columns: ColumnSpace, dim_V_Dmax: int, Dmax: int,
                    Ev: Optional[np.ndarray] = None, T: Optional[np.ndarray] = None) -> dict:
    """Completeness certificate for the fall history above D_max (squarefree rings)."""
    if ring.n_free:
        return {"attempted": False, "reason": "ordinary ring: no structural bound and no certificate", "certified": False}
    n = ring.n_sq
    if (1 << n) > CERTIFICATE_COLUMN_LIMIT:
        return {"attempted": False, "reason": f"2^n = {1 << n} exceeds the certificate column cap {CERTIFICATE_COLUMN_LIMIT}", "certified": False}
    t0 = time.monotonic()
    full = ColumnSpace.build(ring, n) if columns.max_degree < n else columns
    if Ev is None or Ev.shape[1] < full.ncols:
        Ev = evaluation_matrix(ring, full)
    if T is None or T.shape[1] < full.ncols:
        T = multiplication_table(ring, full)
    Z = zero_set(ring, gens, full, Ev)
    dim_I, r = ideal_dimension(Ev, Z, full.ncols_upto(Dmax), ring.p)
    out = {"attempted": True, "Z_size": len(Z), "structural": Dmax >= n + 1,
           "dim_I_at_Dmax": dim_I, "dim_V_at_Dmax": dim_V_Dmax, "C1": dim_V_Dmax == dim_I, "C2": []}
    if out["structural"]:
        out["certified"] = True
        out["route"] = "structural (D_max >= n + 1)"
    else:
        ok = out["C1"]
        for D in range(Dmax + 1, n + 1):
            if not ok:
                break
            c2 = c2_check(ring, full, Ev, Z, D, T)
            out["C2"].append(c2)
            ok = ok and c2["holds"]
        out["certified"] = bool(ok)
        out["route"] = "C1+C2" if ok else "not certified"
    out["seconds"] = round(time.monotonic() - t0, 3)
    return out


# ----------------------------------------------------------------------------------------
# one system, end to end
# ----------------------------------------------------------------------------------------
def measure_system(ring: Ring, gens: Sequence[Poly], columns: ColumnSpace, dmin: int, dmax: int, *,
                   engine: str, cross_check: bool, certificate: bool,
                   T: Optional[np.ndarray] = None, Ev: Optional[np.ndarray] = None,
                   graded: bool = True) -> dict:
    """Closure fall history, graded-rank first fall, certificate and censoring flags for one system."""
    t0 = time.monotonic()
    gens = [g for g in gens]
    degs = [ring.degree(g) for g in gens]
    if any(d < 0 for d in degs):
        return {"degenerate": True, "reason": "zero generator", "generator_degrees": degs}
    if engine == "dense":
        res = closure_dense(ring, gens, columns, dmin, dmax, T=T)
    elif engine == "sparse":
        res = closure_sparse(ring, gens, columns, dmin, dmax)
    else:
        raise ValueError(engine)
    hist = res["history"]
    out = {"degenerate": False, "engine": engine, "convention": CONVENTION_ID, "generator_degrees": degs,
           "D_min": dmin, "D_max": dmax, "history": hist}
    if cross_check:
        other = closure_sparse(ring, gens, columns, dmin, dmax) if engine == "dense" else closure_dense(ring, gens, columns, dmin, dmax, T=T)
        out["cross_check"] = {"other_engine": other["engine"], "agree": histories_agree(hist, other["history"]),
                              "other_history": [{k: h[k] for k in HISTORY_KEYS} for h in other["history"]],
                              "seconds": sum(h["seconds"] for h in other["history"])}
    falls = [h["D"] for h in hist if h["fall"]]
    out["falls"] = falls
    out["d_ff"] = falls[0] if falls else None
    out["d_lf"] = falls[-1] if falls else None
    out["fall_iteration_counts"] = {str(h["D"]): h["iteration_count"] for h in hist if h["fall"]}
    out["min_iteration_count_at_falls"] = min((h["iteration_count"] for h in hist if h["fall"]), default=None)
    out["fall_with_iteration_count_1"] = any(h["fall"] and h["iteration_count"] == 1 for h in hist)
    out["no_fall_in_window"] = not falls                      # the contract's literal flag: no fall in (deg, D_max]
    out["single_fall_degree"] = bool(falls) and falls[0] == falls[-1]
    if graded:
        gp = graded_profile(ring, gens, columns, dmin, dmax)
        out["graded"] = gp
        out["closure_dff_equals_graded_dff"] = (out["d_ff"] == gp["graded_d_ff"])
    if certificate:
        out["certificate"] = certify_history(ring, gens, columns, hist[-1]["dim_V"], dmax, Ev=Ev, T=T)
        # per-degree diagnostic (added after the first two Stage 1 runs; changes no metric): dim(I cap B_{<=D})
        # beside dim V_{F,D}, so a fall entry whose closure inserted nothing (iteration count 1) can be read as
        # "W_0 already equalled the ideal's degree-<=D part" or not
        if out["certificate"].get("attempted") and ring.n_free == 0 and (1 << ring.n_sq) <= CERTIFICATE_COLUMN_LIMIT:
            full = ColumnSpace.build(ring, ring.n_sq) if columns.max_degree < ring.n_sq else columns
            Ev_full = Ev if (Ev is not None and Ev.shape[1] >= full.ncols) else evaluation_matrix(ring, full)
            Z = zero_set(ring, gens, full, Ev_full)
            for h in hist:
                dim_I, _r = ideal_dimension(Ev_full, Z, full.ncols_upto(h["D"]), ring.p)
                h["dim_I_at_D"] = dim_I
                h["W0_saturated"] = (h["dim_W0"] == dim_I)
                h["V_complete_at_D"] = (h["dim_V"] == dim_I)
    else:
        out["certificate"] = {"attempted": False, "reason": "not requested", "certified": False}
    out["right_censored"] = not out["certificate"].get("certified", False)
    out["seconds"] = round(time.monotonic() - t0, 3)
    return out
