"""Exact F_{2^n} arithmetic for ARM C's enumeration.  n <= 20 only.

Written for this experiment.  Nothing here is recalled: the defining polynomial
is SEARCHED for and its primitivity is VERIFIED by building the full
multiplicative cycle and checking its length is exactly 2^n - 1, so a wrong
remembered tap list cannot make a wrong field look right.

Representation: an element of F_{2^n} = F_2[x]/(f) is the integer whose bit i is
the coefficient of x^i.  Products are computed once into exp/log tables and
every later operation is index arithmetic on those tables, which keeps the
enumeration exact and lets numpy do it in bulk.
"""

from __future__ import annotations

import numpy as np

# Candidate defining polynomials, tried in this order and VERIFIED before use.
# Each entry is the integer bit pattern of f(x) including the x^n term.
_CANDIDATE_TAPS = {
    2: [0b111],
    3: [0b1011],
    4: [0b10011],
    5: [0b100101],
    6: [0b1000011],
    7: [0b10000011],
    8: [0b100011101],
    9: [0b1000010001],
    10: [0b10000001001],
    11: [0b100000000101],
    12: [0b1000001010011],
    13: [0b10000000011011],
    14: [0b100010001000011],
    15: [0b1000000000000011],
    16: [0b10001000000001011],
    17: [0b100000000000001001],
    18: [0b1000000010000000001],
    19: [0b10000000000000100111],
    20: [0b100000000000000001001],
}


class BinaryField:
    """F_{2^n} with a verified primitive defining polynomial and full tables."""

    def __init__(self, n: int):
        if not 2 <= n <= 20:
            raise ValueError(f"this class is for 2 <= n <= 20 (got {n})")
        self.n = n
        self.size = 1 << n
        self.order = self.size - 1          # multiplicative group order
        self.poly, self.poly_search_tries = self._find_primitive_poly()
        self.exp, self.log = self._build_tables()
        self.trace_mask = self._build_trace_mask()

    # -- defining polynomial ------------------------------------------------
    def _cycle_length_of_x(self, poly: int) -> int:
        """Multiplicative order of x modulo poly, or 0 if x is not invertible.

        Returns 0 early if the cycle closes before 2^n - 1 steps.
        """
        n, size, order = self.n, self.size, self.order
        cur, steps = 1, 0
        seen_one_again = 0
        while True:
            cur <<= 1
            if cur & size:
                cur ^= poly
            steps += 1
            if cur == 1:
                seen_one_again = steps
                break
            if steps > order:
                return 0
        return seen_one_again

    def _find_primitive_poly(self):
        tries = 0
        candidates = list(_CANDIDATE_TAPS.get(self.n, []))
        # exhaustive fallback: every monic degree-n polynomial with f(0) = 1
        candidates += [self.size | (c << 1) | 1
                       for c in range(0, self.size >> 1)]
        for poly in candidates:
            tries += 1
            if poly < self.size or poly >= (self.size << 1):
                continue
            if not poly & 1:
                continue
            if self._cycle_length_of_x(poly) == self.order:
                return poly, tries
        raise RuntimeError(f"no primitive polynomial found for n={self.n}")

    # -- tables -------------------------------------------------------------
    def _build_tables(self):
        size, order, poly = self.size, self.order, self.poly
        exp = np.zeros(order, dtype=np.int64)
        log = np.full(size, -1, dtype=np.int64)
        cur = 1
        for i in range(order):
            exp[i] = cur
            log[cur] = i
            cur <<= 1
            if cur & size:
                cur ^= poly
        assert cur == 1, "cycle did not close: polynomial is not primitive"
        assert int((log[1:] < 0).sum()) == 0, "log table has holes"
        return exp, log

    def _build_trace_mask(self) -> int:
        """Bit j of the mask is Tr(x^j); then Tr(a) = parity(a & mask).

        Tr(z) = sum_{i=0}^{n-1} z^{2^i}, computed here by explicit repeated
        squaring on each basis element with no shortcut.
        """
        mask = 0
        for j in range(self.n):
            z = 1 << j
            acc = 0
            cur = z
            for _ in range(self.n):
                acc ^= cur
                cur = self.mul_scalar(cur, cur)
            # acc is Tr(x^j) as a field element; it must lie in F_2
            if acc not in (0, 1):
                raise AssertionError(f"trace of x^{j} is not in F_2: {acc}")
            if acc == 1:
                mask |= 1 << j
        return mask

    # -- scalar ops ---------------------------------------------------------
    def mul_scalar(self, a: int, b: int) -> int:
        res, size, poly = 0, self.size, self.poly
        while b:
            if b & 1:
                res ^= a
            b >>= 1
            a <<= 1
            if a & size:
                a ^= poly
        return res

    def trace_scalar(self, a: int) -> int:
        return bin(a & self.trace_mask).count("1") & 1

    # -- vector ops (numpy, exact) -----------------------------------------
    def trace_vec(self, a: np.ndarray) -> np.ndarray:
        masked = a & self.trace_mask
        if hasattr(np, "bitwise_count"):
            return (np.bitwise_count(masked) & 1).astype(np.int64)
        parity = np.zeros(masked.shape, dtype=np.int64)
        for bit in range(self.n):
            parity ^= (masked >> bit) & 1
        return parity

    def mul_vec_by_scalar_log(self, log_a: np.ndarray, b: int) -> np.ndarray:
        """a * b for nonzero a given log(a), nonzero b.  Returns elements."""
        lb = int(self.log[b])
        return self.exp[(log_a + lb) % self.order]

    def inv_vec(self, a: np.ndarray) -> np.ndarray:
        return self.exp[(-self.log[a]) % self.order]
