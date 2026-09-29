"""Generic F_{p^k} = F_p[x]/(m_k(x)) field arithmetic, per this contract's
`field_arithmetic_representation`. ONE representation, uniform for
k=1,2,3,4 (and any further degree needed internally, e.g. for a per-ladder-
step tower -- see `tower.py`), found by Rabin's irreducibility test over
the candidate family x^k - a (binomial), falling back to x^k - a*x - b
only if no binomial succeeds within the stated search bound.

k=1 is simply F_p itself (m_1(x) = x); elements are 1-tuples (c0,).

NO sympy, NO sage, NO numpy: pure Python 3 stdlib integer arithmetic only.
"""
from __future__ import annotations

import polymod_fp as pm


def _prime_factors(n: int):
    fs = []
    d = 2
    m = n
    while d * d <= m:
        if m % d == 0:
            fs.append(d)
            while m % d == 0:
                m //= d
        d += 1
    if m > 1:
        fs.append(m)
    return fs


def _mk_coeffs_binomial(p: int, k: int, a: int):
    """coeffs of x^k - a, ascending order, length k+1."""
    c = [0] * (k + 1)
    c[0] = (-a) % p
    c[k] = 1
    return c


def _mk_coeffs_fallback(p: int, k: int, a: int, b: int):
    """coeffs of x^k - a*x - b, ascending order, length k+1. Requires k>=2."""
    c = [0] * (k + 1)
    c[0] = (-b) % p
    c[1] = (-a) % p
    c[k] = 1
    return c


def is_irreducible_rabin(p: int, k: int, coeffs):
    """Rabin's irreducibility test for a monic degree-k poly `coeffs`
    (ascending, length k+1) over F_p. Returns (bool, detail dict)."""
    detail = {"gcd_checks": [], "full_check": None}
    for q in _prime_factors(k):
        e = p ** (k // q)
        xe = pm.powmod_x(e, coeffs, p)
        diff = pm.sub(xe, [0, 1], p)
        g = pm.gcd(coeffs, diff, p)
        ok = pm.deg(g) == 0
        detail["gcd_checks"].append({"prime_q": q, "exponent_p_pow": e, "gcd_deg": pm.deg(g), "ok": ok})
        if not ok:
            return False, detail
    xk = pm.powmod_x(p ** k, coeffs, p)
    full_ok = pm.trim(xk, p) == pm.trim([0, 1], p)
    detail["full_check"] = {"exponent_p_pow_k": p ** k, "result": xk, "ok": full_ok}
    return full_ok, detail


def find_m_k(p: int, k: int, max_a_tries: int = 50, max_fallback_a: int = 30, max_fallback_b: int = 30):
    """Search for a fixed monic irreducible degree-k m_k(x) over F_p, per
    the contract's exact procedure. Returns a dict with the winning
    polynomial and the FULL search transcript (both branches)."""
    if k == 1:
        return {
            "p": p, "k": 1, "branch": "trivial",
            "kind": "trivial", "coeffs": [0, 1], "a": None, "b": None,
            "search_log": [{"note": "k=1 is F_p itself; m_1(x)=x, no search needed."}],
        }
    search_log = []
    for a in range(2, 2 + max_a_tries):
        coeffs = _mk_coeffs_binomial(p, k, a)
        ok, detail = is_irreducible_rabin(p, k, coeffs)
        search_log.append({"branch": "binomial", "a": a, "irreducible": ok, "detail": detail})
        if ok:
            return {
                "p": p, "k": k, "branch": "binomial",
                "kind": "binomial", "coeffs": coeffs, "a": a, "b": None,
                "search_log": search_log,
            }
    # Fallback: x^k - a*x - b
    for a in range(1, 1 + max_fallback_a):
        for b in range(1, 1 + max_fallback_b):
            coeffs = _mk_coeffs_fallback(p, k, a, b)
            ok, detail = is_irreducible_rabin(p, k, coeffs)
            search_log.append({"branch": "fallback", "a": a, "b": b, "irreducible": ok, "detail": detail})
            if ok:
                return {
                    "p": p, "k": k, "branch": "fallback",
                    "kind": "fallback", "coeffs": coeffs, "a": a, "b": b,
                    "search_log": search_log,
                }
    raise RuntimeError(
        f"find_m_k: no irreducible degree-{k} polynomial found over F_{p} "
        f"within the stated search bounds (binomial a<={1+max_a_tries}, "
        f"fallback a<={max_fallback_a}, b<={max_fallback_b}). "
        f"Stage-0 verification failure -- infrastructure signal, not evidence."
    )


class FpK:
    """F_{p^k} = F_p[x]/(m_k(x)). Elements are k-tuples (c0,...,c_{k-1})
    meaning c0 + c1 x + ... + c_{k-1} x^{k-1} mod m_k(x). k=1 elements are
    1-tuples (c0,), plain F_p.
    """

    def __init__(self, p: int, k: int, mk: dict):
        assert mk["p"] == p and mk["k"] == k
        self.p = p
        self.k = k
        self.kind = mk["kind"]
        self.a = mk["a"]
        self.b = mk["b"]
        self.q = p ** k  # field size

    # ---- basic ring ops ----
    def zero(self):
        return tuple([0] * self.k)

    def one(self):
        return tuple([1] + [0] * (self.k - 1))

    def from_int(self, c: int):
        return tuple([c % self.p] + [0] * (self.k - 1))

    def eq(self, x, y):
        p = self.p
        return tuple(c % p for c in x) == tuple(c % p for c in y)

    def is_zero(self, x):
        p = self.p
        return all(c % p == 0 for c in x)

    def add(self, x, y):
        p = self.p
        return tuple((x[i] + y[i]) % p for i in range(self.k))

    def sub(self, x, y):
        p = self.p
        return tuple((x[i] - y[i]) % p for i in range(self.k))

    def neg(self, x):
        p = self.p
        return tuple((-c) % p for c in x)

    def scal(self, c: int, x):
        p = self.p
        return tuple((c * v) % p for v in x)

    def _reduce(self, coeffs):
        """Reduce a coefficient list of length possibly > k down to length k,
        using x^k = a (binomial) or x^k = a*x + b (fallback)."""
        p, k, a, b = self.p, self.k, self.a, self.b
        coeffs = list(coeffs)
        for d in range(len(coeffs) - 1, k - 1, -1):
            c = coeffs[d] % p
            if c == 0:
                continue
            coeffs[d] = 0
            if self.kind == "binomial":
                coeffs[d - k] = (coeffs[d - k] + c * a) % p
            else:
                coeffs[d - k + 1] = (coeffs[d - k + 1] + c * a) % p
                coeffs[d - k] = (coeffs[d - k] + c * b) % p
        return tuple(coeffs[i] % p for i in range(k))

    def mul(self, x, y):
        if self.k == 1:
            return ((x[0] * y[0]) % self.p,)
        k = self.k
        out = [0] * (2 * k - 1)
        for i in range(k):
            xi = x[i]
            if xi == 0:
                continue
            for j in range(k):
                out[i + j] += xi * y[j]
        return self._reduce(out)

    def pow(self, x, n: int):
        assert n >= 0
        result = self.one()
        base = x
        while n > 0:
            if n & 1:
                result = self.mul(result, base)
            base = self.mul(base, base)
            n >>= 1
        return result

    def inv(self, x):
        """Multiplicative inverse via Fermat: x^(q-2)."""
        return self.pow(x, self.q - 2)

    def lex_key(self, x):
        p = self.p
        return tuple(c % p for c in x)

    # ---- Frobenius ----
    def frob(self, x):
        """Absolute p-power Frobenius: x -> x^p."""
        return self.pow(x, self.p)

    def frob_iter(self, x, j: int):
        """Frob applied j times (iterated)."""
        r = x
        for _ in range(j):
            r = self.frob(r)
        return r

    def frob_direct(self, x, j: int):
        """x^(p^j) computed directly by one exponentiation."""
        return self.pow(x, self.p ** j)

    def is_in_subfield(self, x, j: int):
        """True iff x lies in F_{p^j} (j | k): x^(p^j) == x."""
        return self.eq(self.frob_direct(x, j), x)

    # ---- square roots (generalised Tonelli-Shanks) ----
    def _gen_sequence(self):
        """Fixed generator sequence x, x+1, x+2, ... used for non-residue
        search (and, for k=1, the classic scalar sequence 2,3,4,...)."""
        if self.k == 1:
            m = 2
            while True:
                yield (m % self.p,)
                m += 1
        else:
            m = 0
            while True:
                yield (m % self.p, 1) + tuple([0] * (self.k - 2))
                m += 1

    def is_square(self, x):
        if self.is_zero(x):
            return True
        return self.eq(self.pow(x, (self.q - 1) // 2), self.one())

    def find_nonresidue(self):
        for cand in self._gen_sequence():
            if not self.is_square(cand):
                return cand
        raise RuntimeError("unreachable: a finite field always has a non-residue")

    def sqrt(self, a, reverse: bool = False):
        """Generalised Tonelli-Shanks over F_{p^k}. Returns the
        LEXICOGRAPHICALLY SMALLER (or, if `reverse`, the labelling-control's
        REVERSE-lexicographic-larger) of the two square roots, or None if
        `a` is not a square. a=0 -> 0."""
        if self.is_zero(a):
            return self.zero()
        if not self.is_square(a):
            return None
        q = self.q
        if q % 4 == 3:
            r = self.pow(a, (q + 1) // 4)
        else:
            qq, s = q - 1, 0
            while qq % 2 == 0:
                qq //= 2
                s += 1
            z = self.find_nonresidue()
            m = s
            c = self.pow(z, qq)
            t = self.pow(a, qq)
            r = self.pow(a, (qq + 1) // 2)
            while not self.eq(t, self.one()):
                i = 0
                t2i = t
                while not self.eq(t2i, self.one()):
                    t2i = self.mul(t2i, t2i)
                    i += 1
                b = self.pow(c, 1 << (m - i - 1))
                m = i
                c = self.mul(b, b)
                t = self.mul(t, c)
                r = self.mul(r, b)
        other = self.neg(r)
        pick = max if reverse else min
        return pick(r, other, key=self.lex_key)
