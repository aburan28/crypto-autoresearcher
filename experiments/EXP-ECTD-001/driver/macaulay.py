"""
macaulay.py -- Macaulay matrix construction and modular-rank first-fall-degree scan.

Operational definition of "macaulay_rank_defect_at_first_fall" (frozen driver
convention, documented in MANIFEST.md, identical across every curve/class/null arm):
build the Macaulay matrix M_D at increasing degree D starting from D0 = max total
degree among the frozen Semaev system's generators {S3(x1,x2,x_R), g(x1), g(x2)}:
  rows(D)    = {monomial * f_i : deg(monomial)+deg(f_i) <= D}, for each generator f_i
  columns(D) = all monomials of total degree <= D in (x1,x2)
expected_rank(D) = min(#rows, #cols)     [generic full-rank expectation]
actual_rank(D)   = rank of M_D over F_p, via Gaussian elimination
first_fall_degree = smallest D >= D0 with actual_rank(D) < expected_rank(D)
macaulay_rank_defect_at_first_fall = expected_rank - actual_rank at that D
If no fall is observed by D0 + max_extra_degrees (a fixed cap applied identically
everywhere), the meter is reported as not-observed-within-cap (never fabricated as
zero).
"""
from . import mvpoly


def macaulay_matrix(generators, D, nvars, p):
    cols = mvpoly.monomials_up_to_degree(nvars, D)
    col_index = {m: i for i, m in enumerate(cols)}
    rows = []
    for f in generators:
        df = f.total_degree()
        if df < 0 or df > D:
            continue
        for mm in mvpoly.monomials_up_to_degree(nvars, D - df):
            row_poly = mvpoly.MPoly({mm: 1}, nvars, p).mul(f)
            vec = [0] * len(cols)
            for mono, c in row_poly.terms.items():
                vec[col_index[mono]] = c % p
            rows.append(vec)
    return rows, cols


def rank_mod_p(rows, ncols, p):
    mat = [row[:] for row in rows]
    row_count = len(mat)
    r = 0
    for col in range(ncols):
        pivot = None
        for i in range(r, row_count):
            if mat[i][col] % p != 0:
                pivot = i
                break
        if pivot is None:
            continue
        mat[r], mat[pivot] = mat[pivot], mat[r]
        inv = pow(mat[r][col], p - 2, p)
        piv_row = mat[r]
        if inv != 1:
            piv_row = [(x * inv) % p for x in piv_row]
            mat[r] = piv_row
        for i in range(row_count):
            if i != r:
                factor = mat[i][col] % p
                if factor != 0:
                    row_i = mat[i]
                    mat[i] = [(row_i[k] - factor * piv_row[k]) % p for k in range(ncols)]
        r += 1
        if r == row_count:
            break
    return r


def first_fall_scan(generators, nvars, p, max_extra_degrees=6):
    D0 = max(f.total_degree() for f in generators)
    for D in range(D0, D0 + max_extra_degrees + 1):
        rows, cols = macaulay_matrix(generators, D, nvars, p)
        nrows = len(rows)
        ncols = len(cols)
        rank = rank_mod_p(rows, ncols, p) if rows else 0
        expected = min(nrows, ncols)
        defect = expected - rank
        if defect > 0:
            return {
                "first_fall_degree": D, "defect": defect,
                "nrows": nrows, "ncols": ncols, "rank": rank, "observed": True,
            }
    return {
        "first_fall_degree": None, "defect": None,
        "nrows": None, "ncols": None, "rank": None, "observed": False,
        "cap_degree": D0 + max_extra_degrees,
    }
