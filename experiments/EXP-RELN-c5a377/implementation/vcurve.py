"""Independent, uncharged verifier arithmetic (certificates, audit replay).

Deliberately a different implementation from ``ecarith``: Jacobian projective
coordinates, Fermat inversion, right-to-left scalar multiplication. Shares no
code with the charged path.
"""

from __future__ import annotations


class VCurve:
    def __init__(self, p: int, a: int, b: int):
        self.p, self.a, self.b = p, a % p, b % p

    def on_curve(self, P) -> bool:
        if P is None:
            return True
        x, y = P
        p = self.p
        return (y * y - (x * x * x + self.a * x + self.b)) % p == 0

    def _to_aff(self, J):
        X, Y, Z = J
        p = self.p
        if Z % p == 0:
            return None
        zi = pow(Z, p - 2, p)
        zi2 = zi * zi % p
        return (X * zi2 % p, Y * zi2 * zi % p)

    def _dbl(self, J):
        X, Y, Z = J
        p = self.p
        if Z % p == 0 or Y % p == 0:
            return (1, 1, 0)
        S = 4 * X * Y * Y % p
        M = (3 * X * X + self.a * pow(Z, 4, p)) % p
        X3 = (M * M - 2 * S) % p
        Y3 = (M * (S - X3) - 8 * pow(Y, 4, p)) % p
        return (X3, Y3, 2 * Y * Z % p)

    def _add(self, J1, J2):
        p = self.p
        X1, Y1, Z1 = J1
        X2, Y2, Z2 = J2
        if Z1 % p == 0:
            return J2
        if Z2 % p == 0:
            return J1
        Z1s, Z2s = Z1 * Z1 % p, Z2 * Z2 % p
        U1, U2 = X1 * Z2s % p, X2 * Z1s % p
        S1, S2 = Y1 * Z2s * Z2 % p, Y2 * Z1s * Z1 % p
        if U1 == U2:
            return self._dbl(J1) if S1 == S2 else (1, 1, 0)
        H, R = (U2 - U1) % p, (S2 - S1) % p
        H2 = H * H % p
        H3 = H2 * H % p
        X3 = (R * R - H3 - 2 * U1 * H2) % p
        Y3 = (R * (U1 * H2 - X3) - S1 * H3) % p
        return (X3, Y3, H * Z1 * Z2 % p)

    def add(self, P, Q):
        J1 = (1, 1, 0) if P is None else (P[0], P[1], 1)
        J2 = (1, 1, 0) if Q is None else (Q[0], Q[1], 1)
        return self._to_aff(self._add(J1, J2))

    def neg(self, P):
        return None if P is None else (P[0], (-P[1]) % self.p)

    def mul(self, k: int, P):
        if P is None:
            return None
        R, A = (1, 1, 0), (P[0], P[1], 1)
        while k > 0:
            if k & 1:
                R = self._add(R, A)
            A = self._dbl(A)
            k >>= 1
        return self._to_aff(R)

    def lift_canonical(self, x: int):
        """Point with abscissa x and y <= (p-1)/2, or None if x does not lift."""
        p = self.p
        rhs = (x * x * x + self.a * x + self.b) % p
        if rhs == 0:
            return (x, 0)
        if pow(rhs, (p - 1) // 2, p) != 1:
            return None
        for y in _sqrt_candidates(rhs, p):
            if y * y % p == rhs:
                return (x, min(y, p - y))
        raise ArithmeticError("sqrt failed")


def _sqrt_candidates(n: int, p: int):
    if p % 4 == 3:
        yield pow(n, (p + 1) // 4, p)
        return
    # Cipolla: independent of the charged Tonelli-Shanks
    t = 0
    while pow((t * t - n) % p, (p - 1) // 2, p) != p - 1:
        t += 1
    w = (t * t - n) % p

    def m(u, v):
        return ((u[0] * v[0] + u[1] * v[1] * w) % p, (u[0] * v[1] + u[1] * v[0]) % p)
    r, base, e = (1, 0), (t, 1), (p + 1) // 2
    while e:
        if e & 1:
            r = m(r, base)
        base = m(base, base)
        e >>= 1
    yield r[0]
