"""Independent verifier arithmetic (uncharged).

Deliberately shares no code with ``fparith``: Jacobian coordinates, Python's
built-in ``pow(x, -1, p)`` for the single final inversion, and its own
square-root routine. Used for target generation, the A5 oracle, witness
replay and certificate checks, so that a defect in the charged arithmetic
cannot certify itself.
"""

from __future__ import annotations

O = None


class VCurve:
    def __init__(self, p: int, a: int, b: int):
        self.p, self.a, self.b = p, a % p, b % p

    # Jacobian (X, Y, Z) with x = X/Z^2, y = Y/Z^3; Z == 0 is infinity
    def _to_j(self, P):
        return (1, 1, 0) if P is O else (P[0], P[1], 1)

    def _from_j(self, J):
        X, Y, Z = J
        p = self.p
        if Z % p == 0:
            return O
        zi = pow(Z, -1, p)
        zi2 = zi * zi % p
        return (X * zi2 % p, Y * zi2 * zi % p)

    def _jdbl(self, J):
        X, Y, Z = J
        p = self.p
        if Z == 0 or Y % p == 0:
            return (1, 1, 0)
        S = 4 * X * Y * Y % p
        M = (3 * X * X + self.a * pow(Z, 4, p)) % p
        X3 = (M * M - 2 * S) % p
        Y3 = (M * (S - X3) - 8 * pow(Y, 4, p)) % p
        Z3 = 2 * Y * Z % p
        return (X3, Y3, Z3)

    def _jadd(self, J1, J2):
        p = self.p
        X1, Y1, Z1 = J1
        X2, Y2, Z2 = J2
        if Z1 == 0:
            return J2
        if Z2 == 0:
            return J1
        Z1s, Z2s = Z1 * Z1 % p, Z2 * Z2 % p
        U1, U2 = X1 * Z2s % p, X2 * Z1s % p
        S1, S2 = Y1 * Z2s * Z2 % p, Y2 * Z1s * Z1 % p
        if U1 == U2:
            if S1 != S2:
                return (1, 1, 0)
            return self._jdbl(J1)
        H = (U2 - U1) % p
        Rr = (S2 - S1) % p
        H2 = H * H % p
        H3 = H2 * H % p
        X3 = (Rr * Rr - H3 - 2 * U1 * H2) % p
        Y3 = (Rr * (U1 * H2 - X3) - S1 * H3) % p
        Z3 = H * Z1 * Z2 % p
        return (X3, Y3, Z3)

    def add(self, P, Q):
        return self._from_j(self._jadd(self._to_j(P), self._to_j(Q)))

    def neg(self, P):
        return O if P is O else (P[0], (-P[1]) % self.p)

    def signed(self, P, s: int):
        return P if s > 0 else self.neg(P)

    def sum_signed(self, pts_signs):
        J = (1, 1, 0)
        for P, s in pts_signs:
            J = self._jadd(J, self._to_j(self.signed(P, s)))
        return self._from_j(J)

    def mul(self, k: int, P):
        if P is O:
            return O
        J = (1, 1, 0)
        B = self._to_j(P)
        for bit in bin(k)[2:] if k > 0 else "":
            J = self._jdbl(J)
            if bit == "1":
                J = self._jadd(J, B)
        return self._from_j(J)

    def on_curve(self, P) -> bool:
        if P is O:
            return True
        x, y = P
        return (y * y - x * x * x - self.a * x - self.b) % self.p == 0

    def rhs(self, x: int) -> int:
        return (x * x * x + self.a * x + self.b) % self.p

    def liftable(self, x: int) -> bool:
        r = self.rhs(x)
        return r != 0 and pow(r, (self.p - 1) // 2, self.p) == 1

    def sqrt(self, n: int) -> int:
        """Cipolla's algorithm (different from the charged Tonelli-Shanks)."""
        p = self.p
        n %= p
        if n == 0:
            return 0
        if pow(n, (p - 1) // 2, p) != 1:
            raise ValueError("non-residue")
        t = 0
        while pow((t * t - n) % p, (p - 1) // 2, p) != p - 1:
            t += 1
        w = (t * t - n) % p

        def fmul(u, v):
            return ((u[0] * v[0] + u[1] * v[1] * w) % p, (u[0] * v[1] + u[1] * v[0]) % p)

        r, base, e = (1, 0), (t, 1), (p + 1) // 2
        while e:
            if e & 1:
                r = fmul(r, base)
            base = fmul(base, base)
            e >>= 1
        return r[0]

    def lift(self, x: int):
        y = self.sqrt(self.rhs(x))
        return (x, min(y, self.p - y))


def verify_decomposition(curve: VCurve, R, fb_points, terms) -> bool:
    """terms = [(index, sign)] * 5; checks R == sum sign * fb_points[index]."""
    if len(terms) != 5:
        return False
    for idx, s in terms:
        if s not in (1, -1) or not (0 <= idx < len(fb_points)):
            return False
        if not curve.on_curve(fb_points[idx]):
            return False
    return curve.sum_signed([(fb_points[i], s) for i, s in terms]) == R
