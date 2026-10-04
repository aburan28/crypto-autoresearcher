#!/usr/bin/env python3
"""Independent decomposition-certificate verifier for EXP-GFPN-05ff43.

Pure Python integer arithmetic only (no flint, no PARI, no code shared with the
solver path): F_q = F_p[z]/(z^5 - cmod) as 5-tuples, affine group law on
y^2 = x^3 + a2 x^2 + a4 x + a6, scalar multiplication by double-and-add.

A certificate (JSON) is accepted iff
  * the curve, field, base point G, scalar k and target R are as recorded and R = [k]G
    (known-scalar target), G has the recorded prime order n ([n]G = O);
  * each of the m listed factor-base points lies on the curve and satisfies the
    arm's factor-base condition: arm S5/raw: x(P) in F_p; arm torsion_S5: x(P) + b/x(P) in F_p;
  * with the listed signs, sum_i eps_i P_i == R exactly (m lifted points).
It returns the number of lifted verified points (m) on success and 0 otherwise.
"""
import json, sys

class FqP:
    def __init__(self, p, cmod):
        self.p, self.c = p, cmod
    def add(self, a, b): return tuple((x + y) % self.p for x, y in zip(a, b))
    def sub(self, a, b): return tuple((x - y) % self.p for x, y in zip(a, b))
    def neg(self, a): return tuple((-x) % self.p for x in a)
    def mul(self, a, b):
        p = self.p; r = [0] * 9
        for i in range(5):
            if a[i]:
                for j in range(5):
                    r[i + j] += a[i] * b[j]
        return tuple((r[k] + self.c * r[k + 5]) % p for k in range(4)) + (r[4] % p,)
    def one(self): return (1, 0, 0, 0, 0)
    def zero(self): return (0, 0, 0, 0, 0)
    def is_zero(self, a): return all(x == 0 for x in a)
    def scal(self, k, a): return tuple(k * x % self.p for x in a)
    def pow(self, a, e):
        r, b = self.one(), a
        while e:
            if e & 1: r = self.mul(r, b)
            b = self.mul(b, b); e >>= 1
        return r
    def inv(self, a):
        assert not self.is_zero(a)
        return self.pow(a, self.p ** 5 - 2)
    def div(self, a, b): return self.mul(a, self.inv(b))
    def in_Fp(self, a): return all(x == 0 for x in a[1:])

class CurveP:
    def __init__(self, F, a2, a4, a6):
        self.F, self.a2, self.a4, self.a6 = F, tuple(a2), tuple(a4), tuple(a6)
    def f(self, x):
        F = self.F
        return F.add(F.add(F.mul(F.add(F.mul(F.add(x, self.a2), x), self.a4), x), self.a6), F.zero())
    def on_curve(self, P):
        if P is None: return True
        return self.F.mul(P[1], P[1]) == self.f(P[0])
    def neg(self, P): return None if P is None else (P[0], self.F.neg(P[1]))
    def add(self, P, Q):
        F = self.F
        if P is None: return Q
        if Q is None: return P
        x1, y1 = P; x2, y2 = Q
        if x1 == x2:
            if F.is_zero(F.add(y1, y2)): return None
            num = F.add(F.add(F.scal(3, F.mul(x1, x1)), F.scal(2, F.mul(self.a2, x1))), self.a4)
            lam = F.div(num, F.scal(2, y1))
        else:
            lam = F.div(F.sub(y2, y1), F.sub(x2, x1))
        x3 = F.sub(F.sub(F.sub(F.mul(lam, lam), self.a2), x1), x2)
        y3 = F.sub(F.mul(lam, F.sub(x1, x3)), y1)
        return (x3, y3)
    def mul(self, k, P):
        R = None
        for bit in bin(int(k))[2:]:
            R = self.add(R, R)
            if bit == "1": R = self.add(R, P)
        return R

def verify(cert):
    """Return (ok, n_verified_points, reasons)."""
    reasons = []
    p, cmod = int(cert["p"]), int(cert["cmod"])
    F = FqP(p, cmod)
    cv = cert["curve"]
    E = CurveP(F, cv["a2"], cv["a4"], cv["a6"])
    G = (tuple(cert["G"][0]), tuple(cert["G"][1]))
    R = (tuple(cert["R"][0]), tuple(cert["R"][1]))
    k = int(cert["k"]); n = int(cert["subgroup_order"])
    if not E.on_curve(G): reasons.append("G not on curve")
    if not E.on_curve(R): reasons.append("R not on curve")
    if E.mul(n, G) is not None: reasons.append("[n]G != O")
    if E.mul(k, G) != R: reasons.append("R != [k]G")
    arm = cert["arm"]
    pts = []
    for i, (xy, eps) in enumerate(zip(cert["points"], cert["signs"])):
        P = (tuple(xy[0]), tuple(xy[1]))
        if not E.on_curve(P): reasons.append(f"P{i} not on curve")
        if arm in ("raw", "identity") or (arm.startswith("S") and arm[1:].isdigit()):
            if not F.in_Fp(P[0]): reasons.append(f"x(P{i}) not in F_p")
        elif arm.startswith("torsion_S") and arm[len("torsion_S"):].isdigit():
            if F.is_zero(P[0]): reasons.append(f"x(P{i}) = 0")
            else:
                t = F.add(P[0], F.div(E.a4, P[0]))
                if not F.in_Fp(t): reasons.append(f"x(P{i}) + b/x(P{i}) not in F_p")
                if not F.is_zero(E.a6): reasons.append("torsion arm on curve without (0,0)")
        else:
            reasons.append(f"unknown arm {arm}")
        if eps not in (1, -1): reasons.append(f"bad sign {eps}")
        pts.append(P if eps == 1 else E.neg(P))
    S = None
    for P in pts: S = E.add(S, P)
    if S != R: reasons.append("sum of signed points != R")
    m = int(cert["m"])
    if len(pts) != m: reasons.append(f"expected {m} points, got {len(pts)}")
    ok = not reasons
    return ok, (len(pts) if ok else 0), reasons

if __name__ == "__main__":
    bad = 0
    for path in sys.argv[1:]:
        cert = json.load(open(path))
        ok, npts, reasons = verify(cert)
        print(f"{path}: {'OK' if ok else 'FAIL'} lifted_points={npts} {reasons}")
        bad += (not ok)
    sys.exit(1 if bad else 0)
