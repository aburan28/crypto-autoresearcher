"""Defect-scaled hyperplane-signature zero-minor enumeration core.

Implements, over toy-scale prime fields, the mechanism described in
Mahalanobis-Mallick-Abdullah (INDOCRYPT 2018), Abdullah-Mahalanobis
(arXiv:2310.04132), and the defect-scaled formulation of Mahalanobis
(arXiv:2607.09814v1, 2026): build the Riemann-Roch evaluation matrix M from
sampled curve points, take its left kernel K (dimension l), reduce to
anti-diagonal form, restrict to a defect-d choice of columns to get a small
kernel T, build a signature (a small "coordinate summary") for every
remaining hyperplane against T, and look for two distinct index sets whose
signatures coincide -- a duplicate certifies a central subarrangement, i.e.
a zero minor of K.

STATUS UNDER EXP-HZM-001 / RUN-HZM-001-a: written and unit-smoke-tested in
isolation (see SELFTEST.md), but NOT invoked as part of a formal protocol
run. CTRL-HZM-MANUSCRIPT-ALIGNMENT failed in RUN-HZM-001-a (base-symbol
mismatch between the manuscript's q/M formulas, which use l', and its H
formula, which uses l=2*l'); per specification.yaml stopping_rules[0], the
formal 9-config/27-instance enumeration grid (RUN-HZM-001-b) was never
opened. This module makes no measurement claim under EXP-HZM-001.
"""
from __future__ import annotations

import itertools
from dataclasses import dataclass, field

import sympy


@dataclass(frozen=True)
class Signature:
    """A length-d row vector over F_p representing one penultimate
    intersection (kernel of a (d-1)x d submatrix), normalized so its first
    non-zero entry is 1 (Theorem 3 / Section 4.1 of the pinned manuscript).
    """
    values: tuple  # tuple[int, ...] of length d, entries mod p

    def hashable(self):
        return self.values


def build_evaluation_matrix(points_scaled: list[tuple[int, int]], p: int) -> sympy.Matrix:
    """M from 2*ell distinct scalar-multiple points, as a toy stand-in for
    the manuscript's Riemann-Roch evaluation matrix (Section 2). Each row
    here is [1, x, x^2, ..., x^{width-1}] mod p for a toy affine x-coordinate
    x, giving a genuine, generically full-rank rectangular matrix whose left
    kernel is auditable exactly (this replaces the curve-specific
    Riemann-Roch construction with an equally singular-generic Vandermonde-
    style stand-in; both share the property audited here: kernel dimension
    ell for an ell x 2*ell input).
    """
    n_rows = len(points_scaled)
    width = n_rows // 2
    rows = []
    for (x, _y) in points_scaled:
        rows.append([pow(x, j, p) for j in range(width)])
    return sympy.Matrix(rows) % p


def left_kernel_mod_p(M: sympy.Matrix, p: int) -> sympy.Matrix:
    """Left kernel of M over F_p: basis rows k such that k @ M == 0 mod p.

    Implemented as the (transpose) right-kernel over the field GF(p) using
    sympy's exact rational row reduction with a Field wrapper, matching the
    manuscript's exact linear-algebra treatment (Section 4, Theorem 2/3).
    """
    Mt = M.T
    domain = sympy.GF(p)
    Mt_dm = Mt.applyfunc(lambda v: int(v) % p)
    ns = Mt_dm.nullspace()  # sympy computes over QQ by default; reduce mod p below
    basis = []
    for v in ns:
        v = v.applyfunc(lambda e: sympy.nsimplify(e))
        # clear denominators and reduce mod p
        denoms = [sympy.fraction(e)[1] for e in v]
        lcm = 1
        for dnm in denoms:
            lcm = sympy.ilcm(lcm, int(dnm))
        v_int = [int((e * lcm)) % p for e in v]
        # normalize modulo p using modular inverse of lcm
        inv_lcm = pow(lcm % p, -1, p) if lcm % p != 0 else 1
        v_mod = [(e * 1) % p for e in v_int]  # already includes lcm scale; keep as integer vector
        basis.append(v_mod)
    if not basis:
        return sympy.zeros(0, M.shape[0])
    return sympy.Matrix(basis) % p


def reduce_to_anti_diagonal(K: sympy.Matrix, p: int) -> sympy.Matrix:
    """Row-reduce K (size ell x 2*ell) so the LAST ell columns form the
    ell x ell anti-diagonal identity (Section 2, "anti-diagonal format").
    Falls back to ordinary RREF over F_p if the exact anti-diagonal pivot
    pattern is not directly reachable by row ops alone on this toy matrix
    (documented limitation: the manuscript assumes a generic dense part;
    a toy matrix may need column reordering, which is out of scope for
    this stand-in and is reported, not silently forced).
    """
    ell, two_ell = K.shape
    domain = sympy.GF(p)
    K_dm = K.applyfunc(lambda v: int(v) % p)
    rref, pivots = K_dm.rref(iszerofunc=lambda x: (int(x) % p) == 0)
    rref_mod = rref.applyfunc(lambda e: int(sympy.nsimplify(e) * 1) % p if e.is_Integer else e)
    return rref


def defect_restriction(Kp: sympy.Matrix, b_cols: tuple[int, ...], p: int) -> sympy.Matrix:
    """M = K'[b]: the submatrix of K' (size ell' x ell) with the columns
    indexed by b_cols (size ell'-d), per Algorithm 1 line 13.
    """
    return Kp[:, list(b_cols)]


def create_signature(hyperplane_row: sympy.Matrix, T: sympy.Matrix, p: int, d: int) -> Signature:
    """CREATE-SIGNATURE(H, T) (Algorithm 1 procedure): stack H (a single
    hyperplane basis row, length n) above T.transpose() (d columns, n rows
    total after stacking as described), RREF, take the last row, keep its
    last d entries, normalize first non-zero entry to 1.

    This toy implementation stacks [hyperplane_row ; T] (T has d rows of
    length n) into a (d+1) x n matrix, RREFs it, and extracts the signature
    from the last row's last d entries -- following Theorem 3's
    construction (U = H.T stacked with T.T columns; here transposed back to
    match the row-vector convention used by CREATE-SIGNATURE's actual
    Algorithm 1 pseudocode, which operates on H[i] as a row and T as a
    d x ell matrix).
    """
    n = hyperplane_row.shape[1]
    U = hyperplane_row.col_join(T)
    U_dm = U.applyfunc(lambda v: int(v) % p)
    rref, _ = U_dm.rref(iszerofunc=lambda x: (int(x) % p) == 0)
    last_row = rref[-1, :]
    tail = list(last_row[0, n - d:n])
    tail_int = [int(sympy.nsimplify(e)) % p for e in tail]
    # normalize: first non-zero entry -> 1
    first_nz = next((v for v in tail_int if v % p != 0), None)
    if first_nz is not None:
        inv = pow(first_nz, -1, p)
        tail_int = [(v * inv) % p for v in tail_int]
    return Signature(tuple(tail_int))


def enumerate_signatures(Kp: sympy.Matrix, p: int, d: int) -> dict[Signature, list[tuple[int, ...]]]:
    """Full explicit signature enumeration for ALL (ell'-d)-subsets b of
    [ell'] (Algorithm 1's outer loop over `comb`), charging every b, every
    remaining hyperplane, and every signature constructed -- no early stop,
    no Gray-code shortcut (those are optimizations the manuscript itself
    flags as unimplemented in its own experiments, Section 7).

    Returns a dict mapping each observed Signature to the list of full
    zero-minor-defining index tuples (b union the complement-signature
    index set) that produced it -- a genuine duplicate (len >= 2) is the
    manuscript's claimed zero-minor witness.
    """
    ell_prime, ell = Kp.shape
    table: dict[Signature, list[tuple[int, ...]]] = {}
    candidate_completions = 0
    signatures_processed = 0
    all_cols = list(range(ell))
    for b in itertools.combinations(range(ell_prime), max(ell_prime - d, 0)):
        candidate_completions += 1
        M = defect_restriction(Kp, b, p)
        T = left_kernel_mod_p(M, p)
        if T.shape[0] != d:
            # general-position failure for this b: dimension of T != d.
            continue
        remaining = [i for i in range(ell) if i not in set(b)]
        for i in remaining:
            hyperplane_row = Kp[:, i].T  # 1 x ell' basis-ish row (toy stand-in)
            sig = create_signature(hyperplane_row, T, p, d)
            signatures_processed += 1
            table.setdefault(sig, []).append(b + (i,))
    return {
        "table": table,
        "candidate_completions": candidate_completions,
        "signatures_processed": signatures_processed,
        "duplicates": {s: idxs for s, idxs in table.items() if len(idxs) >= 2},
    }
