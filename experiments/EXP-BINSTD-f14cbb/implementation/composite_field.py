"""Composite-field F_{2^{k*n}} = F_{2^k} · F_{2^n} for gcd(k,n)=1.

Representation: element = list of k-bit ints of length n
  x = sum_{i=0}^{n-1} c_i α^i ,  c_i in K=F_{2^k}, α root of μ over F_2
where μ is the defining polynomial of L=F_{2^n}/F_2 (remains irr over K).

Relative Frobenius fixing K and acting as Frob on L:
  σ(sum c_i α^i) = sum c_i α^{2i}  (reduce mod μ), since the CRT exponent
  s ≡ 0 (mod k), s ≡ 1 (mod n) yields coefficient-Frobenius^0 and α|->α^2.

Trace F→L: Tr(sum c_i α^i) = sum_i Tr_{K/F_2}(c_i) α^i.
"""
from __future__ import annotations

from typing import List, Optional, Sequence, Tuple

from gf2n_local import GF2n, clmul, pmod, is_irreducible


def crt_exponent(k: int, n: int) -> int:
    """s ≡ 0 (mod k), s ≡ 1 (mod n); requires gcd(k,n)=1."""
    # s = k * (k^{-1} mod n)
    inv = pow(k % n, -1, n)
    return k * inv


class CompositeField:
    """F = K·L with K=F_{2^k}, L=F_{2^n}, gcd(k,n)=1, [F:F_2]=k*n."""

    def __init__(self, k_field: GF2n, n_field: GF2n):
        self.K = k_field
        self.L = n_field
        self.k = k_field.n
        self.n = n_field.n
        if math_gcd(self.k, self.n) != 1:
            raise ValueError("degrees must be coprime for simple compositum")
        self.N = self.k * self.n
        self.mu = n_field.mod  # degree-n irreducible over F_2
        self.s = crt_exponent(self.k, self.n)  # relative Frob exponent
        # Precompute α^{2i} reduction table for relative Frob speed:
        # α is represented as [0,1,0,...,0] i.e. poly X
        # For reduction mod μ over K: since μ has F_2 coeffs, reduction uses K-arithmetic
        # identical to F_2 when coeffs in {0,1}, but K-general for products.

    # ---- element helpers: el is List[int] length n, each in 0..2^k-1 ----

    def zero(self) -> List[int]:
        return [0] * self.n

    def one(self) -> List[int]:
        e = [0] * self.n
        e[0] = 1
        return e

    def from_K(self, c: int) -> List[int]:
        e = [0] * self.n
        e[0] = c & (self.K.q - 1)
        return e

    def add(self, a: List[int], b: List[int]) -> List[int]:
        return [x ^ y for x, y in zip(a, b)]

    def _reduce(self, coeffs: List[int]) -> List[int]:
        """Reduce polynomial with K-coeffs modulo μ (F_2 coeffs)."""
        mu = self.mu
        deg = self.n
        # coeffs may be longer than n
        c = list(coeffs)
        while len(c) > deg:
            # leading term at position d = len(c)-1: c[d] * X^d
            # X^n = μ without leading bit = lower terms of μ
            d = len(c) - 1
            lead = c[d]
            if lead == 0:
                c.pop()
                continue
            # X^d = X^{d-n} * X^n = X^{d-n} * (μ_low)
            shift = d - deg
            # μ = X^n + lower; for each bit j of lower, add lead * X^{shift+j}
            lower = mu ^ (1 << deg)
            j = 0
            tmp = lower
            while tmp:
                if tmp & 1:
                    idx = shift + j
                    while len(c) <= idx:
                        c.append(0)
                    c[idx] = self.K.add(c[idx], lead)  # XOR; lead is in K
                tmp >>= 1
                j += 1
            c.pop()
        while len(c) < deg:
            c.append(0)
        return c[:deg]

    def mul(self, a: List[int], b: List[int]) -> List[int]:
        """Schoolbook poly mul over K, reduce mod μ."""
        out = [0] * (2 * self.n - 1)
        for i, ai in enumerate(a):
            if ai == 0:
                continue
            for j, bj in enumerate(b):
                if bj == 0:
                    continue
                out[i + j] = self.K.add(out[i + j], self.K.mul(ai, bj))
        return self._reduce(out)

    def mul_by_K(self, a: List[int], c: int) -> List[int]:
        if c == 0:
            return self.zero()
        return [self.K.mul(x, c) for x in a]

    def relative_frob(self, a: List[int]) -> List[int]:
        """σ: fix K-coeffs, α |-> α^2."""
        # sum c_i α^i  |-> sum c_i α^{2i}
        out = [0] * (2 * self.n)
        for i, ci in enumerate(a):
            if ci:
                out[2 * i] ^= ci  # still need reduce; use XOR since c in K and positions
        # out is F_2-style but coeffs are K elements — reduce carefully
        return self._reduce(out)

    def relative_frob_pow(self, a: List[int], e: int) -> List[int]:
        x = a
        for _ in range(e % self.n):  # σ^n = id on F (order n = [F:K])
            x = self.relative_frob(x)
        return x

    def trace_to_L(self, a: List[int]) -> int:
        """Tr_{F/L}(a) as an element of L=F_{2^n} (bit-packed int).

        Tr(sum c_i α^i) = sum_i Tr_{K/F_2}(c_i) α^i.
        """
        r = 0
        for i, ci in enumerate(a):
            if self.K.trace_to_f2(ci):
                r ^= 1 << i
        return r

    def hilbert90_solve(self, t: int, y: Optional[List[int]] = None) -> List[int]:
        """Solve σ(b) = t·b with t in K^*, Norm(t)=t^n=1 (order | n).

        b = sum_{i=0}^{n-1} t^{-i} σ^i(y). Returns b (nonzero for generic y).
        """
        if y is None:
            # y = α (generic)
            y = [0] * self.n
            y[1] = 1
        t_inv = self.K.inv(t)
        acc = self.zero()
        sig_y = list(y)
        tpow = 1  # t^{0}
        for i in range(self.n):
            # add t^{-i} * σ^i(y)
            term = self.mul_by_K(sig_y, tpow)
            acc = self.add(acc, term)
            tpow = self.K.mul(tpow, t_inv)
            sig_y = self.relative_frob(sig_y)
        return acc


def math_gcd(a: int, b: int) -> int:
    while b:
        a, b = b, a % b
    return a
