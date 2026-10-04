"""Spectral (FFT) cross-check for the decomposition-count vector c_D(r) at
arity m = 3, for EXP-RELN-f202be.

This module is the SECOND, INDEPENDENT implementation required by the
contract (INV-2 accounting identity, spectral route). It imports nothing
beyond the Python standard library and numpy, and shares no module,
function, or helper with source/direct_enumerator.py. It knows nothing
about elliptic curves or group generators: it operates purely on an index
set D subset of Z/N (for E-arms the caller supplies each point's discrete
log index from the curve's log table; this module never sees a curve
point).

Method (verified against a brute-force multiset enumeration on a small
synthetic example before use in any run -- see
runs/RUN-RELN-f202be-stage0/spectral_selftest.json):

  v = indicator vector of D, length N.
  V = FFT(v).
  c_ord(r)  = ordered-triple count, sum_{a,b,c in D} [a+b+c = r]
            = IFFT(V^3)(r)                                  (real, rounded)
  P(r)      = #{(d,e) in D x D : 2d + e = r}
            = IFFT(V2 * V)(r), where V2(t) = V(2t mod N)     (real, rounded)
  c_triple(r) = 1[r * inv(3) mod N in D]     (the {d,d,d} pattern)
  c_pair(r)   = P(r) - c_triple(r)            (the {d,d,e}, d!=e pattern)
  c(r) [multiset count] = (c_ord(r) + 3*c_pair(r) + 5*c_triple(r)) / 6

  E_3        = sum_r c(r)^2
  E_3^ord    = sum_r c_ord(r)^2
  Parseval check (before rounding): E_3^ord == (1/N) sum_t |V(t)|^6
    to relative 1e-9.
"""
from __future__ import annotations

import numpy as np


def _round_nonneg_int(a: np.ndarray) -> np.ndarray:
    return np.rint(a).astype(np.int64)


def spectral_multiset_counts(indices: list[int], N: int) -> dict:
    """Compute the spectral multiset count vector for base `indices` in Z/N.

    `indices` must be distinct integers in [0, N). N must be odd (so that 2
    and 3 are invertible mod N; the contract's N is always an odd prime).
    """
    if N % 2 == 0:
        raise ValueError("spectral route requires odd N (2 must be invertible)")
    if N % 3 == 0:
        raise ValueError("spectral route requires N not divisible by 3")

    v = np.zeros(N, dtype=np.complex128)
    v[np.array(indices, dtype=np.int64) % N] = 1.0

    V = np.fft.fft(v)

    # c_ord: ordered-triple cyclic self-convolution.
    c_ord_c = np.fft.ifft(V ** 3)
    parseval_lhs = float(np.sum(np.abs(c_ord_c) ** 2))  # before rounding
    parseval_rhs = float(np.sum(np.abs(V) ** 6) / N)
    parseval_relative_residual = (
        abs(parseval_lhs - parseval_rhs) / parseval_rhs if parseval_rhs != 0 else 0.0
    )

    idx = np.arange(N)
    inv2 = pow(2, -1, N)
    inv3 = pow(3, -1, N)

    V2 = V[(2 * idx) % N]
    P_c = np.fft.ifft(V2 * V)

    v_real = v.real
    c_triple = v_real[(inv3 * idx) % N]

    c_ord = _round_nonneg_int(c_ord_c.real)
    P = _round_nonneg_int(P_c.real)
    c_triple_i = _round_nonneg_int(c_triple)
    c_pair = P - c_triple_i

    c_multiset_num = c_ord.astype(np.float64) + 3 * c_pair.astype(np.float64) + 5 * c_triple_i.astype(np.float64)
    # This must be exactly divisible by 6 for a valid Z/N base; report the
    # remainder so a caller can flag disagreement rather than silently round.
    remainder = np.mod(np.rint(c_multiset_num).astype(np.int64), 6)
    c_multiset = np.rint(c_multiset_num / 6.0).astype(np.int64)

    E3_ord = int(np.sum(c_ord.astype(np.int64) ** 2))
    E3 = int(np.sum(c_multiset.astype(np.int64) ** 2))

    # Spectral summaries (secondary metrics), toy-only, log-defined.
    nonzero_freq_mag = np.abs(V[1:])  # chi != 1
    sixth_moment = float(np.sum(nonzero_freq_mag ** 6) / N)
    max_mag = float(np.max(nonzero_freq_mag)) if N > 1 else 0.0

    return {
        "N": int(N),
        "B": int(len(indices)),
        "c_multiset": c_multiset,
        "c_ord": c_ord,
        "E3": E3,
        "E3_ord": E3_ord,
        "parseval_relative_residual": parseval_relative_residual,
        "divisibility_remainder_nonzero_count": int(np.count_nonzero(remainder)),
        "spectral_sixth_moment_over_B3": sixth_moment / (len(indices) ** 3) if len(indices) > 0 else None,
        "spectral_max_freq_mag": max_mag,
    }


def selftest() -> dict:
    """Brute-force cross-check on a small synthetic base, independent of any
    curve or the direct_enumerator module (uses only itertools locally, kept
    inline so this module needs no import of direct_enumerator.py)."""
    import itertools
    from collections import Counter

    N = 23
    D = sorted({1, 3, 7, 9, 15, 20, 4})
    B = len(D)
    cnt: Counter = Counter()
    for i, j, k in itertools.combinations_with_replacement(range(B), 3):
        r = (D[i] + D[j] + D[k]) % N
        cnt[r] += 1
    direct_vec = [cnt.get(r, 0) for r in range(N)]

    spec = spectral_multiset_counts(D, N)
    max_err = max(abs(int(spec["c_multiset"][r]) - direct_vec[r]) for r in range(N))
    return {
        "N": N,
        "D": D,
        "max_abs_error_vs_bruteforce": max_err,
        "parseval_relative_residual": spec["parseval_relative_residual"],
        "pass": max_err == 0,
    }


if __name__ == "__main__":
    import json

    print(json.dumps(selftest(), indent=2))
