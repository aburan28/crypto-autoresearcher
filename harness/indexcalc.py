"""Toy prime-field index calculus, end-to-end, with an explicit operation-count
cost model for a head-to-head against the Pollard-rho baseline.

This is the decision-relevant measurement for the prime-field ECDLP question:
does summation-polynomial point decomposition, run as a full index calculus
(relation collection + linear algebra), solve the discrete log in fewer group
operations than generic rho at reachable scale? The recovered k is verified
(k*P == Q), so every solve carries a certificate.

Everything is toy scale and exact. The factor base is built as multiples of P so
its elements lie in <P> (logs well-defined); the solver never uses those known
multipliers -- it recovers them -- so the operation counts are a faithful cost
simulation.
"""
from __future__ import annotations

from dataclasses import dataclass

from .toycurve import ECDLPInstance, EllipticCurve, Point, _seed_int


@dataclass(frozen=True)
class IndexCalcResult:
    solved: bool
    k: int | None
    group_operations: int
    relations_collected: int
    factor_base_size: int
    targets_tried: int
    certificate: dict | None = None
    reason: str = ""


def _solve_mod_n(rows: list[list[int]], rhs: list[int], n: int, require_col: int):
    """Gaussian elimination over GF(n) (n prime), reduced row echelon form.

    Free variables (columns that never take a pivot -- e.g. factor-base elements
    that never appeared in a relation) are assigned 0; this is fine as long as
    `require_col` (the unknown k) is itself pinned to a pivot and the system is
    consistent. Returns the solution vector, or None if inconsistent or if
    `require_col` is a free variable (k undetermined)."""
    m = len(rows)
    cols = len(rows[0]) if rows else 0
    A = [r[:] + [rhs[i] % n] for i, r in enumerate(rows)]
    pivot_col_of_row = []
    r = 0
    for c in range(cols):
        piv = next((i for i in range(r, m) if A[i][c] % n != 0), None)
        if piv is None:
            continue
        A[r], A[piv] = A[piv], A[r]
        inv = pow(A[r][c], -1, n)
        A[r] = [(v * inv) % n for v in A[r]]
        for i in range(m):
            if i != r and A[i][c] % n != 0:
                f = A[i][c]
                A[i] = [(A[i][j] - f * A[r][j]) % n for j in range(cols + 1)]
        pivot_col_of_row.append(c)
        r += 1
        if r == m:
            break
    # Consistency: no row of the form [0 ... 0 | nonzero].
    for i in range(r, m):
        if A[i][cols] % n != 0 and all(A[i][j] % n == 0 for j in range(cols)):
            return None
    pivot_cols = set(pivot_col_of_row)
    if require_col not in pivot_cols:
        return None                      # k is a free variable -> undetermined
    sol = [0] * cols
    for i, c in enumerate(pivot_col_of_row):
        sol[c] = A[i][cols] % n
    return sol


def solve(inst: ECDLPInstance, factor_base_size: int = 20,
          max_targets: int | None = None) -> IndexCalcResult:
    """Recover k by toy index calculus. Counts group operations for the cost model."""
    E = inst.curve()
    P, Q, n = inst.P, inst.Q, inst.n
    L = factor_base_size
    if max_targets is None:
        max_targets = 200 * n            # generous; relation collection is the cost

    ops = 0

    # Factor base F_i = r_i * P in <P>. r_i unknown to the linear solver.
    r = [(_seed_int(inst.seed, f"ic_fb{i}") % (n - 1)) + 1 for i in range(L)]
    F = []
    for ri in r:
        F.append(E.mul(ri, P))
        ops += ri.bit_length()           # scalar-mult op estimate (one-time setup)
    # Precompute signed pair-sums S_i + S_j -> (i, si, j, sj) for O(1) lookup.
    signed = [(F[i], 1) for i in range(L)] + [(E.negate(F[i]), -1) for i in range(L)]
    pair_index: dict[Point, tuple[int, int, int, int]] = {}
    for a_idx in range(len(signed)):
        Pa, sa = signed[a_idx]
        ia = a_idx % L
        for b_idx in range(a_idx, len(signed)):
            Pb, sb = signed[b_idx]
            ib = b_idx % L
            s = E.add(Pa, Pb)
            ops += 1
            pair_index.setdefault(s, (ia, sa, ib, sb))

    # Relation collection: R = a*P + b*Q; if R is a signed factor-base pair-sum,
    # record  sa*x_ia + sb*x_ib - b*k = a   (unknowns x_1..x_L, k).
    rows: list[list[int]] = []
    rhs: list[int] = []
    need = 4 * (L + 1)                    # over-collect for robust full rank on k
    tried = 0
    a_coef = _seed_int(inst.seed, "ic_a0") % n
    b_coef = (_seed_int(inst.seed, "ic_b0") % n) or 1
    R = E.add(E.mul(a_coef, P), E.mul(b_coef, Q))
    ops += a_coef.bit_length() + b_coef.bit_length()
    while len(rows) < need and tried < max_targets:
        tried += 1
        hit = pair_index.get(R)
        if hit is not None:
            ia, sa, ib, sb = hit
            row = [0] * (L + 1)
            row[ia] += sa
            row[ib] += sb
            row[L] = (-b_coef) % n
            rows.append([v % n for v in row])
            rhs.append(a_coef % n)
        # advance by one group op; alternate adding P and Q so both a and b
        # vary (a constant b-column would make k under-determined).
        if tried & 1:
            R = E.add(R, P)
            a_coef = (a_coef + 1) % n
        else:
            R = E.add(R, Q)
            b_coef = (b_coef + 1) % n
        ops += 1

    if len(rows) < L + 1:
        return IndexCalcResult(False, None, ops, len(rows), L, tried,
                               reason="insufficient relations within budget")
    sol = _solve_mod_n(rows, rhs, n, require_col=L)
    if sol is None:
        return IndexCalcResult(False, None, ops, len(rows), L, tried,
                               reason="relation matrix rank-deficient")
    k = sol[L] % n
    cert = None
    solved = E.mul(k, P) == Q
    if solved:
        cert = {"kind": "discrete_log",
                "statement": {"curve": {"p": E.p, "a": E.a, "b": E.b},
                              "P": list(P), "Q": list(Q), "k": int(k)}}
    return IndexCalcResult(bool(solved), int(k) if solved else None, ops,
                           len(rows), L, tried, certificate=cert,
                           reason="" if solved else "recovered k failed verification")
