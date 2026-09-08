"""
Exact multiset decomposition-count vectors for EXP-RELN-141a86 Stage 0b/0e.

Implements, for a base D of B distinct residues in Z/N (N a positive
integer modulus -- prime where the contract calls for a prime-order group,
not necessarily prime for the Sidon/Bose-Chowla arm which lives in
Z/(q^3-1)):

    c_D(r) = #{ unordered multisets {d_1,...,d_m} of elements of D
                (repetition allowed) with d_1+...+d_m == r (mod N) }

for m in {2, 3, 4}, by DIRECT combinatorial enumeration over unordered
index tuples (i_1 <= i_2 <= ... <= i_m), which is exact (no FFT rounding)
and is fast enough for the B <= ~200 bases used in this contract's Stage 0
controls (INV-A4 Sidon bases, small closed-form checks). For larger B
(own-enumeration Stage 0e at N up to 2^20), a cyclic-convolution (repeated
polynomial multiplication via numpy FFT with exact-integer rounding
verification) is provided as `count_vector_convolution`, used only when the
direct O(B^m) approach would be too slow.

Both paths are exact: the FFT path rounds the (necessarily integer)
result and asserts closeness to an integer before accepting it, exactly as
EXP-FB3-001's own FFT control does (see raw-result.json
fft_max_abs_rounding_deviation).
"""

from __future__ import annotations

from itertools import combinations_with_replacement
from typing import Dict, List, Sequence, Tuple

import numpy as np


def count_vector_direct(D: Sequence[int], N: int, m: int) -> List[int]:
    """
    Exact c_D(r) for r in 0..N-1, by direct enumeration of all
    combinations_with_replacement(D, m) (i.e. unordered multisets).
    O(C(B+m-1, m)) time -- exact for every entry, no rounding.
    """
    counts = [0] * N
    for combo in combinations_with_replacement(D, m):
        r = sum(combo) % N
        counts[r] += 1
    return counts


def count_vector_convolution(D: Sequence[int], N: int, m: int) -> List[int]:
    """
    Exact c_D(r) via cyclic convolution: build the indicator vector of D,
    convolve it with itself m times cyclically (mod N) using FFT, then
    correct for the UNORDERED-multiset convention by subtracting the
    over-counted ordered-tuple diagonal contributions using the standard
    inclusion-exclusion (Newton's identity / power-sum to elementary
    symmetric conversion) -- implemented here for m in {2, 3} only (the
    m used by this contract), via direct algebraic identities:

      m=2: ordered pairs O2(r) = sum_i sum_j [d_i+d_j=r];
           unordered U2(r) = (O2(r) + [r == 2*d_i for exactly the diagonal
           terms]) / 2, i.e. U2(r) = (O2(r) + diag2(r)) / 2 where
           diag2(r) = #{d in D : 2d == r (mod N)} (each diagonal ordered
           pair (d,d) is counted once in O2 but represents exactly one
           unordered multiset {d,d}, so U2 = (O2 - diag2)/2 + diag2
           = (O2 + diag2) / 2).
      m=3: ordered triples O3(r) = (indicator * indicator * indicator)(r)
           (cyclic autoconvolution power 3). Unordered U3 relates to O3 by
           the standard multiset-vs-ordered-tuple correction:
             O3(r) = 6*U3_distinct(r) + 3*U3_pair(r) + U3_triple(r)
           where U3_distinct counts multisets of 3 DISTINCT elements
           summing to r, U3_pair counts multisets with exactly one repeated
           pair {d,d,e} (d!=e), U3_triple counts {d,d,d}. The full unordered
           count (what this contract's c_D means) is
           U3(r) = U3_distinct(r) + U3_pair(r) + U3_triple(r), so this
           routine instead computes U3 directly via the exact orbit-counting
           (Burnside/cycle-index) decomposition for the symmetric group S_3
           acting on ordered triples:
             U3(r) = (1/6) [ O3(r) + 3*P3(r) + 2*T3(r) ]
           where P3(r) = #{ordered pairs (d,e) in D^2 : 2d+e == r} (fixed
           points of a transposition: positions 1,2 equal) and
           T3(r) = #{d in D : 3d == r} (fixed points of a 3-cycle). This is
           exactly the same Burnside/cycle-index method EXP-FB3-001 itself
           uses (raw-result.json vector_equal_burnside), reproduced here
           independently.

    Returns a list of NON-NEGATIVE INTEGERS (rounded from the FFT result
    after asserting max rounding deviation < 1e-6); raises AssertionError if
    the FFT result is not integer-close (this would indicate an
    implementation defect, never silently accepted).
    """
    if m not in (2, 3):
        raise NotImplementedError("count_vector_convolution implemented for m in {2,3} only")

    indicator = np.zeros(N, dtype=np.float64)
    for d in D:
        indicator[d % N] += 1.0

    F = np.fft.fft(indicator)

    def cyclic_autoconv(order: int) -> np.ndarray:
        return np.fft.ifft(F ** order).real

    O2 = cyclic_autoconv(2)
    diag2 = np.zeros(N)
    for d in D:
        diag2[(2 * d) % N] += 1.0
    U2_float = (O2 + diag2) / 2.0

    if m == 2:
        return _round_exact(U2_float)

    # m == 3
    O3 = cyclic_autoconv(3)
    # P3(r) = #{(d,e) in D^2 : 2d + e == r}: convolve indicator*2 (diag) with indicator
    diag2_conv_indicator = np.fft.ifft(np.fft.fft(diag2) * F).real
    P3 = diag2_conv_indicator
    T3 = np.zeros(N)
    for d in D:
        T3[(3 * d) % N] += 1.0
    U3_float = (O3 + 3.0 * P3 + 2.0 * T3) / 6.0
    return _round_exact(U3_float)


def _round_exact(arr: np.ndarray, tol: float = 1e-6) -> List[int]:
    rounded = np.round(arr)
    max_dev = float(np.max(np.abs(arr - rounded)))
    if max_dev > tol:
        raise AssertionError(
            f"count_vector_convolution: FFT result not integer-close "
            f"(max abs deviation {max_dev} > tol {tol}); rejecting rather "
            f"than silently accepting a corrupted count vector"
        )
    return [int(x) for x in rounded.tolist()]


def stats_from_count_vector(counts: Sequence[int], N: int) -> Dict[str, float]:
    """
    stats.{mean, coverage, concentration, variance, max_count} exactly per
    EXP-FB3-001's own convention: mean = sum(c)/N; coverage =
    #{r: c(r)>0}/N; concentration = (1/N) sum c(r)(c(r)-1); variance =
    concentration + mean - mean^2 (the INV-A6 identity, used here as the
    DEFINITION for own-enumeration cells, consistent with the FB3 identity
    check).
    """
    total = sum(counts)
    mean = total / N
    nonzero = sum(1 for c in counts if c > 0)
    coverage = nonzero / N
    concentration = sum(c * (c - 1) for c in counts) / N
    variance = concentration + mean - mean * mean
    max_count = max(counts) if counts else 0
    return {
        "n_targets": N,
        "sum_counts": total,
        "mean": mean,
        "coverage": coverage,
        "concentration": concentration,
        "variance": variance,
        "max_count": max_count,
    }


def dispersion_delta(mean: float, concentration: float) -> float:
    """Delta = conc/mu + 1 - mu (INV-A6 identity), the frozen derivation
    rule -- never computed by any other rescaling."""
    mu = mean
    return concentration / mu + 1.0 - mu


if __name__ == "__main__":
    # Self-test: direct vs convolution agreement on a small case, m=2 and m=3.
    import random

    random.seed(20260906)
    N = 211
    D = sorted(random.sample(range(N), 13))
    for m in (2, 3):
        direct = count_vector_direct(D, N, m)
        conv = count_vector_convolution(D, N, m)
        assert direct == conv, (m, "mismatch", sum(direct), sum(conv))
    print("count_vectors.py self-test: OK (direct == convolution for m=2,3, N=211, B=13)")
