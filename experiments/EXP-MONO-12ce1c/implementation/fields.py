"""
Pure-Python F_p and F_{p^2} arithmetic. No sympy, no numpy required for this module
(sympy is used only in semaev_path2.py for the resultant recursion).

F_{p^2} is represented as F_p[u]/(u^2 - n) for a fixed quadratic non-residue n
mod p. Elements are tuples (a, b) meaning a + b*u, a, b in [0, p).

Frobenius (the p-th power map) on this representation is conjugation:
    (a + b*u)^p = a + b*u^p = a + b*u*(u^{p-1}) = a + b*u*n^{(p-1)/2} = a - b*u
because n is a non-residue, so n^{(p-1)/2} = -1 mod p (Euler's criterion).
"""


def legendre(a: int, p: int) -> int:
    a %= p
    if a == 0:
        return 0
    r = pow(a, (p - 1) // 2, p)
    return -1 if r == p - 1 else r


def find_nonresidue(p: int) -> int:
    for n in range(2, p):
        if legendre(n, p) == -1:
            return n
    raise RuntimeError(f"no quadratic non-residue found mod {p} (should be impossible for p>2)")


def build_sqrt_table(p: int):
    """table[q] = smallest a in [0, p) with a*a % p == q, for every quadratic residue q,
    including 0 (a=0). O(p) space and time; p is at most a few thousand in this contract."""
    table = {}
    for a in range(0, (p + 1) // 2 + 1):
        q = (a * a) % p
        if q not in table:
            table[q] = a
    return table


class Fp2:
    def __init__(self, p: int, n: int = None):
        self.p = p
        self.n = n if n is not None else find_nonresidue(p)
        assert legendre(self.n, p) == -1
        self.n_inv = pow(self.n, p - 2, p)
        self.sqrt_table = build_sqrt_table(p)

    # ---- basic field ops ----
    def add(self, x, y):
        p = self.p
        return ((x[0] + y[0]) % p, (x[1] + y[1]) % p)

    def sub(self, x, y):
        p = self.p
        return ((x[0] - y[0]) % p, (x[1] - y[1]) % p)

    def neg(self, x):
        p = self.p
        return ((-x[0]) % p, (-x[1]) % p)

    def mul(self, x, y):
        p = self.p
        n = self.n
        a, b = x
        c, d = y
        return ((a * c + b * d * n) % p, (a * d + b * c) % p)

    def sqr(self, x):
        return self.mul(x, x)

    def scal(self, k, x):
        p = self.p
        return ((k * x[0]) % p, (k * x[1]) % p)

    def inv(self, x):
        p = self.p
        n = self.n
        a, b = x
        denom = (a * a - n * b * b) % p
        dinv = pow(denom, p - 2, p)
        return ((a * dinv) % p, ((-b) * dinv) % p)

    def div(self, x, y):
        return self.mul(x, self.inv(y))

    def from_fp(self, a: int):
        return (a % self.p, 0)

    def eq(self, x, y):
        p = self.p
        return x[0] % p == y[0] % p and x[1] % p == y[1] % p

    def is_zero(self, x):
        return x[0] % self.p == 0 and x[1] % self.p == 0

    def conj(self, x):
        """Frobenius (p-th power map) on F_{p^2} over F_p."""
        p = self.p
        return (x[0] % p, (-x[1]) % p)

    # ---- square roots ----
    def sqrt_of_fp_element(self, c: int):
        """Square root, in F_{p^2}, of c in F_p (c reduced mod p). Returns an F_p2 tuple.
        chi is the quadratic character of c mod p (0 if c==0 mod p)."""
        p = self.p
        c %= p
        if c == 0:
            return (0, 0), 0
        chi = legendre(c, p)
        if chi == 1:
            a = self.sqrt_table[c]
            return (a, 0), 1
        else:
            # c is a non-residue; c * n_inv is a residue (product of two non-residues)
            s2 = (c * self.n_inv) % p
            s = self.sqrt_table[s2]
            return (0, s), -1


def ec_add_fp2(F: Fp2, P, Q, A_fp2):
    """Elliptic curve point addition on y^2 = x^3 + A x + B, computed over F_{p^2}
    (B does not appear in the addition formula). P, Q are None (point at infinity)
    or (X, Y) pairs of F_p2 tuples. Standard chord-and-tangent law."""
    if P is None:
        return Q
    if Q is None:
        return P
    X1, Y1 = P
    X2, Y2 = Q
    if F.eq(X1, X2):
        if F.eq(Y1, F.neg(Y2)):
            return None
        # doubling (X1==X2 and Y1==Y2, since a field has at most 2 square roots)
        lam = F.div(F.add(F.scal(3, F.sqr(X1)), A_fp2), F.scal(2, Y1))
    else:
        lam = F.div(F.sub(Y2, Y1), F.sub(X2, X1))
    X3 = F.sub(F.sub(F.sqr(lam), X1), X2)
    Y3 = F.sub(F.mul(lam, F.sub(X1, X3)), Y1)
    return (X3, Y3)


def ec_neg_fp2(F: Fp2, P):
    if P is None:
        return None
    X, Y = P
    return (X, F.neg(Y))
