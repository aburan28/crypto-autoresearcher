"""Schoolbook GF(2^n) arithmetic for EXP-BINSTD-cf4bf7 (n=34/37; no exp/log tables)."""
from __future__ import annotations


def clmul(a: int, b: int) -> int:
    r = 0
    while b:
        if b & 1:
            r ^= a
        a <<= 1
        b >>= 1
    return r


def pmod(a: int, m: int) -> int:
    dm = m.bit_length() - 1
    while a and a.bit_length() - 1 >= dm:
        a ^= m << (a.bit_length() - 1 - dm)
    return a


def pgcd(a: int, b: int) -> int:
    while b:
        a, b = b, pmod(a, b)
    return a


def is_irreducible(mod: int) -> tuple[bool, dict]:
    """Rabin-style irreducibility test over F_2."""
    n = mod.bit_length() - 1
    details: dict = {"n": n, "gcd_checks": []}
    x = 2  # t
    cur = x
    ok = True
    for i in range(1, n + 1):
        cur = pmod(clmul(cur, cur), mod)  # t^{2^i}
        if i <= n // 2:
            g = pgcd(mod, cur ^ x)
            details["gcd_checks"].append({"i": i, "gcd": g})
            if g != 1:
                ok = False
    details["t_pow_2n_equals_t"] = cur == x
    ok = ok and cur == x
    return ok, details


def find_irreducible(n: int, prefer_trinomial: bool = True) -> int:
    """Search a low-weight irreducible of degree n (deterministic ascending)."""
    if prefer_trinomial:
        for k in range(1, n):
            mod = (1 << n) | (1 << k) | 1
            ok, _ = is_irreducible(mod)
            if ok:
                return mod
    for k in range(1, n):
        for j in range(1, k):
            for i in range(0, j):  # i=0 yields weight-4 with constant term already set
                terms = {n, k, j, 0}
                if i:
                    terms.add(i)
                mod = 0
                for e in terms:
                    mod |= 1 << e
                if mod.bit_length() - 1 != n:
                    continue
                ok, _ = is_irreducible(mod)
                if ok:
                    return mod
    raise RuntimeError(f"no irreducible found for n={n}")


def poly_to_string(mod: int) -> str:
    n = mod.bit_length() - 1
    parts = []
    for e in range(n, -1, -1):
        if (mod >> e) & 1:
            if e == 0:
                parts.append("1")
            elif e == 1:
                parts.append("t")
            else:
                parts.append(f"t^{e}")
    return "+".join(parts) if parts else "0"


class Field:
    """Generic schoolbook F_{2^n}."""

    def __init__(self, n: int, mod: int):
        if mod.bit_length() - 1 != n:
            raise ValueError("modulus degree mismatch")
        ok, details = is_irreducible(mod)
        if not ok:
            raise ValueError(f"modulus not irreducible: {details}")
        self.n = n
        self.mod = mod
        self.q = 1 << n
        # Precompute F_2-linear maps for Artin-Schreier solve and trace.
        self.tr_mask = 0
        for j in range(n):
            if self._trace_slow(1 << j):
                self.tr_mask |= 1 << j
        # Matrix of z |-> z^2 + z on the polynomial basis (columns).
        self._as_cols = []
        for j in range(n):
            e = 1 << j
            img = self.mul(e, e) ^ e  # e^2 + e
            self._as_cols.append(img)
        self._as_solver = self._build_as_solver()

    def mul(self, a: int, b: int) -> int:
        return pmod(clmul(a, b), self.mod)

    def sqr(self, a: int) -> int:
        return self.mul(a, a)

    def pow(self, a: int, e: int) -> int:
        r = 1
        while e:
            if e & 1:
                r = self.mul(r, a)
            a = self.mul(a, a)
            e >>= 1
        return r

    def inv(self, a: int) -> int:
        if a == 0:
            raise ZeroDivisionError
        return self.pow(a, self.q - 2)

    def _trace_slow(self, a: int) -> int:
        s = 0
        x = a
        for _ in range(self.n):
            s ^= x
            x = self.mul(x, x)
        # Absolute trace lands in the prime field {0,1} ⊂ F_{2^n}.
        return s & 1

    def trace(self, a: int) -> int:
        return bin(a & self.tr_mask).count("1") & 1

    def sqrt(self, a: int) -> int:
        # In char 2, sqrt(a) = a^{2^{n-1}}
        x = a
        for _ in range(self.n - 1):
            x = self.mul(x, x)
        return x

    def half_trace(self, a: int) -> int:
        """Odd-n half-trace; for even n use solve_artin_schreier."""
        if self.n % 2 == 0:
            raise ValueError("half_trace requires odd n")
        s = 0
        x = a
        for _ in range((self.n - 1) // 2 + 1):
            s ^= x
            x = self.sqr(self.sqr(x))
        return s

    def _build_as_solver(self):
        """Gaussian elimination for z^2+z = c over F_2 (n x n, rank n-1)."""
        n = self.n
        # Build matrix M (n rows) with columns as bit vectors; also track pivot.
        # We solve M z = c where M's columns are _as_cols.
        mat = [self._as_cols[j] for j in range(n)]  # column j
        # Convert to row-major bit matrix for GE: rows[i] bit j = bit i of col j
        # Augment later per RHS. Pre-factor via RREF of M, recording free var.
        rows = []
        for i in range(n):
            row = 0
            for j in range(n):
                if (mat[j] >> i) & 1:
                    row |= 1 << j
            rows.append(row)
        # RREF
        pivots = [-1] * n
        r = 0
        col_used = []
        for c in range(n):
            piv = None
            for i in range(r, n):
                if (rows[i] >> c) & 1:
                    piv = i
                    break
            if piv is None:
                continue
            rows[r], rows[piv] = rows[piv], rows[r]
            for i in range(n):
                if i != r and (rows[i] >> c) & 1:
                    rows[i] ^= rows[r]
            pivots[c] = r
            col_used.append(c)
            r += 1
            if r == n:
                break
        return {"rows": rows, "pivots": pivots, "rank": r, "col_used": col_used}

    def solve_artin_schreier(self, c: int) -> int | None:
        """Return one z with z^2 + z = c, or None if no solution (Tr(c) != 0)."""
        if self.trace(c) != 0:
            return None
        n = self.n
        rows = list(self._as_solver["rows"])
        # Augment with RHS bits of c
        aug = []
        for i in range(n):
            rhs = (c >> i) & 1
            aug.append((rows[i], rhs))
        # Re-run elimination with augmentation (rows already RREF of M; apply same ops)
        # Simpler: fresh GE on augmented system
        arows = []
        for i in range(n):
            row = 0
            for j in range(n):
                if (self._as_cols[j] >> i) & 1:
                    row |= 1 << j
            arows.append((row, (c >> i) & 1))
        r = 0
        pivot_col = {}
        for ccol in range(n):
            piv = None
            for i in range(r, n):
                if (arows[i][0] >> ccol) & 1:
                    piv = i
                    break
            if piv is None:
                continue
            arows[r], arows[piv] = arows[piv], arows[r]
            prow, prhs = arows[r]
            for i in range(n):
                if i != r and (arows[i][0] >> ccol) & 1:
                    arows[i] = (arows[i][0] ^ prow, arows[i][1] ^ prhs)
            pivot_col[ccol] = r
            r += 1
        # Consistency: zero rows must have zero RHS
        for i in range(n):
            if arows[i][0] == 0 and arows[i][1] != 0:
                return None
        z = 0
        for ccol, prow_idx in pivot_col.items():
            if arows[prow_idx][1]:
                z |= 1 << ccol
        return z


def elements_of_f4(F: Field) -> list[int]:
    """Return the unique subfield F_4 = {x : x^4 = x} as ints."""
    out = []
    # For n divisible by 2, F_4 embeds uniquely.
    # Enumerate is impossible at n=34; construct algebraically:
    # F_4 = {0,1,ω,ω^2} with ω^2+ω+1=0.
    # Find a root of t^2+t+1 in F by testing whether it splits via factoring,
    # or search among elements of the subfield fixed by Frobenius^{n/gcd(2,n)}.
    # Elements of F_{2^d} inside F_{2^n} (d|n) are fixed by x |-> x^{2^d}.
    d = 2
    if F.n % d != 0:
        raise ValueError("F_4 not a subfield")
    # Generator of the subfield: find α with α^{4} = α and α not in F_2.
    # The polynomial X^2+X+1 divides X^{2^2}-X. Roots are the order-3 elements.
    # Search in the F_{2^2}-subfield constructed as powers of a normal element.
    # Practical: take β = t^{(2^n-1)/3} if 3 | (2^n-1), which it does for even n>=2.
    # ω = g^{(q-1)/3} has order 3, so ω^2+ω+1=0.
    # Finding a generator g of F^* is expensive; instead solve X^2+X+1=0 via AS? 
    # X^2 + X + 1 = 0 <=> X^2 + X = 1, Artin-Schreier with c=1.
    # Tr(1) = n mod 2; for even n Tr(1)=0, so solutions exist.
    omega = F.solve_artin_schreier(1)
    if omega is None:
        raise RuntimeError("F_4 root of X^2+X+1 not found")
    # The two roots are omega and omega+1.
    out = [0, 1, omega, omega ^ 1]
    # Verify
    for x in out:
        if F.pow(x, 4) != x:
            raise RuntimeError(f"element {x} not in F_4")
    return out
