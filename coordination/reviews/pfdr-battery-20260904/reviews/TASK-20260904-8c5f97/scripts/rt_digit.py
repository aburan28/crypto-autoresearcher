"""Red-team independent re-implementation of the (2,2,3) digit Macaulay meter.

Written for TASK-20260904-8c5f97.  Shares NO code with harness/macaulay_fp or
with experiments/EXP-PFDR-fd901a/run_experiment.py.  Route:

    values of S~ on {0,1}^6  ->  Moebius transform -> multilinear coefficients
    -> Macaulay layer rows (monomial merge = bitwise OR)
    -> exact echelon over F_p with pivot = highest column, top-degree columns last.

That reproduces the SEMANTICS documented in harness/macaulay_fp/linalg.py
(full_rank = #echelon rows, top_rank = #pivots in the top block,
fall_dim = full_rank - top_rank) by a different construction (evaluation +
Moebius) than the producer's (symbolic expansion).
"""
from itertools import combinations

N = 6  # digit variables at (m, d, s) = (2, 2, 3)


# ---------------------------------------------------------------- S_3 (own copy)
def s3(x1, x2, x3, A, Bc, p):
    """Semaev third summation polynomial, standard short-Weierstrass form."""
    t = (x1 - x2) ** 2 * x3 * x3
    t -= 2 * ((x1 + x2) * (x1 * x2 + A) + 2 * Bc) * x3
    t += (x1 * x2 - A) ** 2 - 4 * Bc * (x1 + x2)
    return t % p


def ell(bits, lo):
    """linear digit form a_{lo} + 2 a_{lo+1} + 4 a_{lo+2} evaluated at a bit vector"""
    return ((bits >> lo) & 1) + 2 * ((bits >> (lo + 1)) & 1) + 4 * ((bits >> (lo + 2)) & 1)


def stilde_values(A, Bc, xr, p):
    """value vector of S~ on the 64 points of {0,1}^6 (index = bitmask)"""
    return [s3(ell(v, 0), ell(v, 3), xr, A, Bc, p) for v in range(1 << N)]


def moebius(vals, p):
    """multilinear coefficients from values: c_m = sum_{v subset m} (-1)^{|m|-|v|} f(v)"""
    coeffs = list(vals)
    for i in range(N):
        bit = 1 << i
        for m in range(1 << N):
            if m & bit:
                coeffs[m] = (coeffs[m] - coeffs[m ^ bit]) % p
    return coeffs


def poly_from_values(vals, p):
    c = moebius(vals, p)
    return {m: c[m] % p for m in range(1 << N) if c[m] % p}


# ---------------------------------------------------------------- column order
def column_order(D):
    """columns = squarefree monomials of degree <= D, LOW degree first, top last"""
    cols = []
    for d in range(D + 1):
        for c in combinations(range(N), d):
            m = 0
            for i in c:
                m |= 1 << i
            cols.append(m)
    index = {m: i for i, m in enumerate(cols)}
    top_start = len(cols) - len([1 for c in combinations(range(N), D)])
    return index, top_start, len(cols)


def echelon_ranks(rows, p, top_start):
    """rows: list of {col: coeff}. pivot = highest column index."""
    piv = {}
    for row in rows:
        r = {c: v % p for c, v in row.items() if v % p}
        while r:
            lead = max(r)
            if lead not in piv:
                inv = pow(r[lead], -1, p)
                piv[lead] = {c: (v * inv) % p for c, v in r.items()}
                break
            f = r[lead]
            pr = piv[lead]
            for c, v in pr.items():
                nv = (r.get(c, 0) - f * v) % p
                if nv:
                    r[c] = nv
                else:
                    r.pop(c, None)
    full = len(piv)
    top = sum(1 for lead in piv if lead >= top_start)
    return full, top


def profile(poly, p, dmin=3, dmax=6, nvars=N):
    """per-layer (full_rank, top_rank, fall_dim) for D in [dmin, dmax]"""
    if not poly:
        return [(0, 0, 0)] * (dmax - dmin + 1)
    degf = max(bin(m).count("1") for m in poly)
    out = []
    for D in range(dmin, dmax + 1):
        index, top_start, _ = column_order(D)
        md = D - degf
        rows = []
        if md >= 0:
            for c in combinations(range(nvars), md):
                mu = 0
                for i in c:
                    mu |= 1 << i
                row = {}
                for m, v in poly.items():
                    col = index[m | mu]
                    row[col] = (row.get(col, 0) + v) % p
                rows.append({k: v for k, v in row.items() if v})
        full, top = echelon_ranks(rows, p, top_start) if rows else (0, 0)
        out.append((full, top, full - top))
    return out


def d_ff(prof, dmin=3):
    for i, (_, _, fall) in enumerate(prof):
        if fall > 0:
            return dmin + i
    return None
