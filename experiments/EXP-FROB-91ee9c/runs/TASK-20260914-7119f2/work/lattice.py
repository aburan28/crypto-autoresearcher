from sage.all import GF, matrix, vector, Integer
from fractions import Fraction
import itertools


def all_set_partitions(items):
    """Yield all set partitions of a list `items` as list-of-tuples (blocks)."""
    items = list(items)
    if not items:
        yield []
        return
    first, rest = items[0], items[1:]
    for smaller in all_set_partitions(rest):
        # add `first` to each existing block
        for i in range(len(smaller)):
            yield smaller[:i] + [(first,) + smaller[i]] + smaller[i + 1:]
        # add `first` as its own new block
        yield [(first,)] + smaller


def poly_of_matrix(coeffs_const_first, M, F):
    n = M.nrows()
    result = matrix.zero(F, n, n)
    Mp = matrix.identity(F, n)
    for c in coeffs_const_first:
        result += c * Mp
        Mp = Mp * M
    return result


def build_kernels(atomic_factors, xminus1_factor, M, F, n):
    """atomic_factors: list of R-polynomials (sorted). Returns kers (list of
    VectorSpace, matching atomic_factors order), ker_x1 (VectorSpace)."""
    kers = []
    for f in atomic_factors:
        fm = poly_of_matrix(f.list(), M, F)
        kers.append(fm.right_kernel())
    xm1 = poly_of_matrix(xminus1_factor.list(), M, F)
    ker_x1 = xm1.right_kernel()
    return kers, ker_x1


def build_change_of_basis(kers, ker_x1, F, n):
    """Block order: ker_x1 first (dim 1), then each atomic kernel in order.
    Returns C (n x n matrix, sage) and block boundaries [(start,dim,label)]."""
    basis_rows = []
    blocks = []
    idx = 0
    b = list(ker_x1.basis())
    basis_rows.extend(b)
    blocks.append(("x1", idx, len(b)))
    idx += len(b)
    for i, k in enumerate(kers):
        b = list(k.basis())
        basis_rows.extend(b)
        blocks.append((i, idx, len(b)))
        idx += len(b)
    C = matrix(F, basis_rows).transpose()  # columns = basis vectors
    assert C.is_invertible(), "change-of-basis matrix must be invertible (direct sum check)"
    Cinv = C.inverse()
    return C, Cinv, blocks


def cinv_to_pylist(Cinv, q):
    n = Cinv.nrows()
    return [[int(Cinv[r, c]) for c in range(n)] for r in range(n)]


def vec_signature(vec_ints, cinv_py, blocks, q):
    """vec_ints: python list of ints (mod q) representing field element in
    standard basis 1,z,...,z^{n-1}. Returns (v0_nonzero: bool, atomic_mask: int)."""
    n = len(vec_ints)
    coords = [0] * n
    for r in range(n):
        row = cinv_py[r]
        s = 0
        for c in range(n):
            vc = vec_ints[c]
            if vc:
                s += row[c] * vc
        coords[r] = s % q
    v0_nonzero = False
    mask = 0
    for label, start, dim in blocks:
        nz = any(coords[start + i] != 0 for i in range(dim))
        if label == "x1":
            v0_nonzero = nz
        else:
            if nz:
                mask |= (1 << label)
    return v0_nonzero, mask
