"""Generic F_p / F_{p^2} numeric utilities shared by BOTH arms.

These are low-level field-arithmetic primitives (modular inverse, Legendre
symbol, modular square root, F_{p^2} representation and Frobenius) with no
notion of "t1,t2" or "c1,c0" -- they carry no intermediate value specific to
either arm's claim, and are exactly the kind of shared plumbing (like a
shared `mulmod`) the independence requirement does not forbid. Neither arm
imports the other; both import this.
"""
from __future__ import annotations


def legendre(a: int, p: int) -> int:
    """Legendre symbol (a/p) in {-1, 0, 1}, p an odd prime."""
    a %= p
    if a == 0:
        return 0
    r = pow(a, (p - 1) // 2, p)
    return -1 if r == p - 1 else r


def is_qr(a: int, p: int) -> bool:
    return legendre(a, p) == 1


def sqrt_mod(a: int, p: int):
    """Tonelli-Shanks. Returns one square root of a mod p, or None if a is
    not a QR mod p. a=0 -> 0."""
    a %= p
    if a == 0:
        return 0
    if legendre(a, p) != 1:
        return None
    if p % 4 == 3:
        return pow(a, (p + 1) // 4, p)
    # General Tonelli-Shanks
    q, s = p - 1, 0
    while q % 2 == 0:
        q //= 2
        s += 1
    z = 2
    while legendre(z, p) != -1:
        z += 1
    m = s
    c = pow(z, q, p)
    t = pow(a, q, p)
    r = pow(a, (q + 1) // 2, p)
    while t != 1:
        i, t2i = 0, t
        while t2i != 1:
            t2i = (t2i * t2i) % p
            i += 1
        b = pow(c, 1 << (m - i - 1), p)
        m = i
        c = (b * b) % p
        t = (t * c) % p
        r = (r * b) % p
    return r


def find_least_nonresidue(p: int) -> int:
    d = 2
    while legendre(d, p) != -1:
        d += 1
    return d


class Fp2:
    """F_{p^2} = F_p[w]/(w^2 - d), d a fixed non-residue mod p.

    Elements are (u, v) meaning u + v*w. Since w^2 = d and p is odd,
    Frobenius x -> x^p acts on this basis as (u, v) -> (u, -v) (standard
    conjugation), exactly as specified in `base_construction`.
    """

    def __init__(self, p: int):
        self.p = p
        self.d = find_least_nonresidue(p)

    def add(self, x, y):
        p = self.p
        return ((x[0] + y[0]) % p, (x[1] + y[1]) % p)

    def sub(self, x, y):
        p = self.p
        return ((x[0] - y[0]) % p, (x[1] - y[1]) % p)

    def mul(self, x, y):
        p, d = self.p, self.d
        u1, v1 = x
        u2, v2 = y
        return ((u1 * u2 + d * v1 * v2) % p, (u1 * v2 + v1 * u2) % p)

    def scal(self, k, x):
        p = self.p
        return ((k * x[0]) % p, (k * x[1]) % p)

    def conj(self, x):
        """Frobenius: (u, v) -> (u, -v) mod p."""
        p = self.p
        return (x[0] % p, (-x[1]) % p)

    def from_fp(self, u):
        return (u % self.p, 0)

    def is_in_fp(self, x):
        return x[1] % self.p == 0

    def eq(self, x, y):
        p = self.p
        return (x[0] % p, x[1] % p) == (y[0] % p, y[1] % p)

    def pow(self, x, n):
        result = (1, 0)
        base = x
        while n > 0:
            if n & 1:
                result = self.mul(result, base)
            base = self.mul(base, base)
            n >>= 1
        return result

    def norm(self, x):
        """Norm_{Fp2/Fp}(x) = x * conj(x) = u^2 - d*v^2 mod p."""
        p, d = self.p, self.d
        u, v = x
        return (u * u - d * v * v) % p

    def is_square(self, x):
        if x == (0, 0):
            return True
        return self.pow(x, (self.p * self.p - 1) // 2) == (1, 0)

    def sqrt(self, x):
        """General square root in F_{p^2} (standard 'complex method'):
        for x = u + v w with w^2 = d, write a candidate root (s,t) with
          s^2 + d t^2 = u        (I)
          2 s t = v              (II)
        Squaring (I) combined with the norm gives (s^2 - d t^2)^2 =
        u^2 - d v^2 = Norm(x); let m be a square root of Norm(x) in F_p
        (guaranteed to exist when x is a square in Fp2, since the norm of
        a square is itself a square in F_p). Then s^2 = (u+m)/2 or (u-m)/2
        for the two sign choices of m; exactly one of the two candidates is
        itself a QR in F_p when x is a genuine Fp2 square. Returns None if
        x is not a square in F_p2.
        """
        p = self.p
        u, v = x
        u %= p
        v %= p
        if v == 0:
            r = sqrt_mod(u, p)
            if r is not None:
                return (r, 0)
            t2 = (u * pow(self.d, -1, p)) % p
            t = sqrt_mod(t2, p)
            if t is None:
                return None
            return (0, t)
        norm_x = self.norm(x)
        m = sqrt_mod(norm_x, p)
        if m is None:
            return None
        inv2 = pow(2, -1, p)
        for msign in (m, (-m) % p):
            s2 = ((u + msign) * inv2) % p
            s = sqrt_mod(s2, p)
            if s is None or s == 0:
                continue
            t = (v * pow((2 * s) % p, -1, p)) % p
            cand = (s, t)
            if self.eq(self.mul(cand, cand), x):
                return cand
        return None


class Fp4:
    """F_{p^4} = F_{p^2}[z]/(z^2 - e), e a fixed non-square element of the
    SAME F_{p^2} = F_p[w]/(w^2-d) used elsewhere, so this tower genuinely
    contains that exact F_{p^2} as a subfield (the same w, unchanged).

    Elements are (A, B) meaning A + B*z, with A, B each an Fp2 element
    (u, v) tuple. Frobenius x -> x^p uses the characteristic-p freshman's
    dream identity (A+B)^p = A^p + B^p, giving
        x^p = conj(A) + conj(B) * s * z,   s := e^{(p-1)/2} in Fp2,
    since z^p = (z^2)^{(p-1)/2} * z = e^{(p-1)/2} * z = s*z.
    """

    def __init__(self, fp2: Fp2):
        self.fp2 = fp2
        self.p = fp2.p
        self.e = self._find_nonsquare()
        self.s = fp2.pow(self.e, (fp2.p - 1) // 2)

    def _find_nonsquare(self):
        fp2 = self.fp2
        for cand in [(0, 1), (1, 1), (1, 2), (2, 1), (1, 3), (3, 1), (2, 3), (3, 2)]:
            if not fp2.is_square(cand):
                return cand
        for u in range(0, fp2.p):
            for v in range(0, fp2.p):
                if (u, v) == (0, 0):
                    continue
                if not fp2.is_square((u, v)):
                    return (u, v)
        raise RuntimeError("no non-square found in Fp2 (unexpected)")

    def add(self, x, y):
        fp2 = self.fp2
        return (fp2.add(x[0], y[0]), fp2.add(x[1], y[1]))

    def sub(self, x, y):
        fp2 = self.fp2
        return (fp2.sub(x[0], y[0]), fp2.sub(x[1], y[1]))

    def mul(self, x, y):
        fp2 = self.fp2
        A, B = x
        C, D = y
        return (
            fp2.add(fp2.mul(A, C), fp2.mul(self.e, fp2.mul(B, D))),
            fp2.add(fp2.mul(A, D), fp2.mul(B, C)),
        )

    def pow(self, x, n):
        result = ((1, 0), (0, 0))
        base = x
        while n > 0:
            if n & 1:
                result = self.mul(result, base)
            base = self.mul(base, base)
            n >>= 1
        return result

    def frob(self, x):
        """x^p, the absolute p-power Frobenius of Fp4/Fp."""
        fp2 = self.fp2
        A, B = x
        return (fp2.conj(A), fp2.mul(fp2.conj(B), self.s))

    def eq(self, x, y):
        return self.fp2.eq(x[0], y[0]) and self.fp2.eq(x[1], y[1])

    def from_fp2(self, a):
        return (a, (0, 0))

    def sqrt_of_fp2_nonsquare(self, a):
        """Square root, IN Fp4, of an Fp2 element `a` that is a NON-square
        in Fp2. By construction a/e is then a square in Fp2 (non-square
        divided by the fixed non-square e is a square, since Fp2*/(Fp2*)^2
        has order 2), so y = sqrt_fp2(a/e) satisfies (y*z)^2 = y^2 * e = a.
        Returns the Fp4 element (0, y)."""
        fp2 = self.fp2
        a_over_e = fp2.mul(a, fp2.pow(self.e, fp2.p * fp2.p - 2))  # a * e^{-1} in Fp2* (order p^2-1)
        y = fp2.sqrt(a_over_e)
        if y is None:
            raise ValueError("sqrt_of_fp2_nonsquare: a/e unexpectedly not an Fp2 square (bug)")
        return ((0, 0), y)


def embed(val, from_level: int, to_level: int):
    """Embed a coordinate value from field level (0=Fp,1=Fp2,2=Fp4) up to a
    higher level, via the tower inclusions Fp subset Fp2 subset Fp4."""
    if from_level == to_level:
        return val
    if from_level == 0 and to_level == 1:
        return (val, 0)
    if from_level == 0 and to_level == 2:
        return ((val, 0), (0, 0))
    if from_level == 1 and to_level == 2:
        return (val, (0, 0))
    raise ValueError(f"cannot embed level {from_level} into level {to_level}")


def neg_val(val, level: int, p: int):
    if level == 0:
        return (-val) % p
    if level == 1:
        return ((-val[0]) % p, (-val[1]) % p)
    if level == 2:
        A, B = val
        return (((-A[0]) % p, (-A[1]) % p), ((-B[0]) % p, (-B[1]) % p))
    raise ValueError(level)


def frob_val(val, level: int, p: int, fp2: Fp2, fp4):
    if level == 0:
        return val % p
    if level == 1:
        return fp2.conj(val)
    if level == 2:
        return fp4.frob(val)
    raise ValueError(level)


def eq_val(val1, val2, level: int, p: int):
    if level == 0:
        return (val1 % p) == (val2 % p)
    if level == 1:
        return (val1[0] % p, val1[1] % p) == (val2[0] % p, val2[1] % p)
    if level == 2:
        return (
            (val1[0][0] % p, val1[0][1] % p) == (val2[0][0] % p, val2[0][1] % p)
            and (val1[1][0] % p, val1[1][1] % p) == (val2[1][0] % p, val2[1][1] % p)
        )
    raise ValueError(level)


def inert_delta(fp2: Fp2, D: int):
    """delta in F_{p^2} with delta^2 = D * inv(4) mod p, for D a non-residue
    mod p (inert regime). Since D/4 is itself a non-residue (4 is a QR), its
    square root in F_{p^2} = F_p[w]/(w^2-d) is a pure-w multiple: writing
    D/4 = k*d (k = (D/4)*d^{-1} mod p, itself then necessarily a QR in F_p
    because d is THE fixed non-residue and D/4 is a non-residue, so their
    ratio is a QR), delta = (0, sqrt(k))."""
    p, d = fp2.p, fp2.d
    Dover4 = (D * pow(4, -1, p)) % p
    k = (Dover4 * pow(d, -1, p)) % p
    root = sqrt_mod(k, p)
    if root is None:
        raise ValueError("inert_delta: k unexpectedly not a QR (implementation bug)")
    return (0, root)
