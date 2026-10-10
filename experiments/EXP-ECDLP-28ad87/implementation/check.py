#!/usr/bin/env python3
"""EXP-ECDLP-28ad87 independent run checker (read only). Usage: check.py <run_dir>.

Does NOT import run.py. Own polynomial arithmetic over F_p, own Cantor composition/reduction
for C: y^2 = x^6 + a x^2 + b (classes [D - inf+ - inf-], D affine of degree 2, zero class None),
own Euler-criterion point counts and own affine EC arithmetic. Exit 0 iff every gate holds.
"""
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import primeset  # noqa: E402

EXP_ID = "EXP-ECDLP-28ad87"
SAMPLE = 20


# ---- polynomials mod p, coefficient lists low -> high ----
def tr(a):
    while a and a[-1] == 0:
        a.pop()
    return a


class Field:
    def __init__(self, p):
        self.p = p

    def add(self, a, b):
        p = self.p
        n = max(len(a), len(b))
        return tr([((a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0)) % p for i in range(n)])

    def sub(self, a, b):
        p = self.p
        n = max(len(a), len(b))
        return tr([((a[i] if i < len(a) else 0) - (b[i] if i < len(b) else 0)) % p for i in range(n)])

    def mul(self, a, b):
        p = self.p
        if not a or not b:
            return []
        out = [0] * (len(a) + len(b) - 1)
        for i, x in enumerate(a):
            for j, y in enumerate(b):
                out[i + j] = (out[i + j] + x * y) % p
        return tr(out)

    def scal(self, a, c):
        return tr([x * c % self.p for x in a])

    def divmod(self, a, b):
        p = self.p
        a = list(a)
        inv = pow(b[-1], -1, p)
        q = [0] * max(1, len(a) - len(b) + 1)
        while len(a) >= len(b):
            c = a[-1] * inv % p
            sh = len(a) - len(b)
            q[sh] = c
            for i, y in enumerate(b):
                a[sh + i] = (a[sh + i] - c * y) % p
            a.pop()
            tr(a)
        return tr(q), a

    def xgcd(self, a, b):
        # iterative extended Euclid; returns monic g with s*a + t*b = g
        r = [list(a), list(b)]
        s = [[1], []]
        t = [[], [1]]
        while r[1]:
            q, rem = self.divmod(r[0], r[1])
            r = [r[1], rem]
            s = [s[1], self.sub(s[0], self.mul(q, s[1]))]
            t = [t[1], self.sub(t[0], self.mul(q, t[1]))]
        g = r[0]
        c = pow(g[-1], -1, self.p)
        return self.scal(g, c), self.scal(s[0], c), self.scal(t[0], c)


class Cover:
    """Jacobian of y^2 = x^6 + a x^2 + b."""

    def __init__(self, p, a, b):
        self.f = Field(p)
        self.p = p
        self.F = tr([b % p, 0, a % p, 0, 0, 0, 1])

    def add(self, D, E):
        f = self.f
        if D is None:
            return E
        if E is None:
            return D
        (u1, v1), (u2, v2) = D, E
        g1, e1, e2 = f.xgcd(u1, u2)
        g, c1, c2 = f.xgcd(g1, f.add(v1, v2))
        s1, s2, s3 = f.mul(c1, e1), f.mul(c1, e2), c2
        den = f.mul(g, g)
        u = f.divmod(f.mul(u1, u2), den)[0]
        num = f.add(f.add(f.mul(f.mul(s1, u1), v2), f.mul(f.mul(s2, u2), v1)),
                    f.mul(s3, f.add(f.mul(v1, v2), self.F)))
        v = f.divmod(num, g)[0]
        if len(u) == 1:
            return None
        v = f.divmod(v, u)[1]
        if len(u) == 5:
            w = f.divmod(f.sub(self.F, f.mul(v, v)), u)[0]
            if len(w) != 3:
                raise ArithmeticError("exceptional")
            w = f.scal(w, pow(w[-1], -1, self.p))
            v = f.divmod(f.scal(v, self.p - 1), w)[1]
            u = w
        if len(u) != 3:
            raise ArithmeticError("exceptional")
        return (u, v)

    def neg(self, D):
        if D is None:
            return None
        return (D[0], self.f.divmod(self.f.scal(D[1], self.p - 1), D[0])[1])

    def mul(self, k, D, _depth=0):
        """Scalar multiple; an exceptional intermediate divisor (prob ~1/p) is avoided by
        re-splitting the scalar k = c1 + (k - c1) with a seeded c1 (different addition chains)."""
        try:
            return self._mul(k, D)
        except ArithmeticError:
            if _depth > 40 or k < 4:
                raise
            c1 = random.Random(f"split:{k}:{_depth}").randrange(2, k - 1)
            return self.add(self.mul(c1, D, _depth + 1), self.mul(k - c1, D, _depth + 1))

    def _mul(self, k, D):
        R = None
        for ch in bin(k)[2:]:
            R = self.add(R, R)
            if ch == "1":
                R = self.add(R, D)
        return R


def dec(x):
    return None if x is None else (list(x[0]), list(x[1]))


# ---- elliptic curve ----
def eadd(P, Q, a, p):
    if P is None:
        return Q
    if Q is None:
        return P
    if P[0] == Q[0]:
        if (P[1] + Q[1]) % p == 0:
            return None
        m = (3 * P[0] * P[0] + a) * pow(2 * P[1], -1, p) % p
    else:
        m = (Q[1] - P[1]) * pow(Q[0] - P[0], -1, p) % p
    x = (m * m - P[0] - Q[0]) % p
    return (x, (m * (P[0] - x) - P[1]) % p)


def emul(k, P, a, p):
    R = None
    while k:
        if k & 1:
            R = eadd(R, P, a, p)
        P = eadd(P, P, a, p)
        k >>= 1
    return R


def chi(n, p):
    n %= p
    if n == 0:
        return 0
    return 1 if pow(n, (p - 1) // 2, p) == 1 else -1


def order_E(p, a, b):
    return p + 1 + sum(chi(x ** 3 + a * x + b, p) for x in range(p))


def order_E2(p, a, b):
    return p + 2 + sum(chi(x ** 4 + a * x * x + b * x, p) for x in range(p))


def peval(poly, x, p):
    r = 0
    for c in reversed(poly):
        r = (r * x + c) % p
    return r


def main():
    if len(sys.argv) != 2:
        print("usage: check.py <run_dir>")
        return 2
    d = sys.argv[1]
    rp, mp = os.path.join(d, "raw-result.json"), os.path.join(d, "manifest.yaml")
    bad = []
    if not os.path.isfile(rp):
        bad.append("raw-result.json missing")
    if not os.path.isfile(mp):
        bad.append("manifest.yaml missing")
    if bad:
        print("FAIL: " + "; ".join(bad))
        return 1
    raw = json.load(open(rp, encoding="utf-8"))
    man = {}
    for line in open(mp, encoding="utf-8"):
        if ": " in line:
            k, v = line.rstrip("\n").split(": ", 1)
            try:
                man[k] = json.loads(v)
            except ValueError:
                man[k] = v
    if raw.get("experiment_id") != EXP_ID:
        bad.append("raw experiment_id mismatch")
    if man.get("experiment_id") != EXP_ID:
        bad.append("manifest experiment_id mismatch")
    cells = raw.get("cells", [])
    if not cells:
        bad.append("no cells")
    nrel_checked = 0
    for i, c in enumerate(cells):
        tag = f"cell{i}(p={c.get('p')},{c.get('arm')},seed={c.get('seed')},c={c.get('curve_index')})"

        def fail(field, msg=""):
            bad.append(f"{tag}.{field} {msg}".strip())

        try:
            p, a, b, l, k = c["p"], c["a"], c["b"], c["l"], c["k"]
            P, Q = tuple(c["P"]), tuple(c["Q"])
            if p <= 3 or p % 2 == 0 or not primeset.is_prime(p):
                fail("p", "not an odd prime > 3")
            if b % p == 0 or (4 * a ** 3 + 27 * b * b) % p == 0:
                fail("curve", "singular or b=0")
            # (a) orders
            nE, nE2 = order_E(p, a, b), order_E2(p, a, b)
            if nE != c["order_E"]:
                fail("order_E", f"recorded {c['order_E']} recount {nE}")
            if nE2 != c["order_E2"]:
                fail("order_E2", f"recorded {c['order_E2']} recount {nE2}")
            if not (primeset.is_prime(l) and l % 2 == 1 and l >= 64 and l != p and nE % l == 0
                    and nE % (l * l) != 0 and nE2 % l != 0):
                fail("l", "violates prime/odd/>=64/!=p/divides #E/l^2 !| #E/l !| #E''")
            nJ = nE * nE2
            cof = nJ // l
            # points
            for nm, Z in (("P", P), ("Q", Q)):
                if (Z[1] * Z[1] - Z[0] ** 3 - a * Z[0] - b) % p:
                    fail(nm, "not on E")
            if emul(l, P, a, p) is not None or emul(k, P, a, p) != Q:
                fail("P/Q/k", "[l]P != O or [k]P != Q")
            # (b) pullbacks
            cov = Cover(p, a, b)
            Aexp = ([(-P[0]) % p, 0, 1], [P[1] % p])
            Bexp = ([(-Q[0]) % p, 0, 1], [Q[1] % p])
            A, B = dec(c["A"]), dec(c["B"])
            if A != Aexp:
                fail("A", "differs from phi^*P")
            if B != Bexp:
                fail("B", "differs from phi^*Q")
            if A is not None and cov.mul(l, Aexp) is not None:
                fail("ctrl_pullback", "[l]phi^*P != 0 on recount")
            # factor base
            target = 1
            while target * target < p:
                target += 1
            S, x = [], 0
            while len(S) < target and x < p:
                if chi(peval(cov.F, x, p), p) >= 0:
                    S.append(x)
                x += 1
            if S != c["factor_base_x"]:
                fail("factor_base_x", "differs from recomputed first ceil(sqrt p) square-F x")
            Sset = set(S)
            # multipliers: cofactor part lies in [l]Jac
            mults = c["multipliers"]
            if len(mults) != 20:
                fail("multipliers", "count != 20")
            for mm in mults[:3]:
                M = dec(mm["M"])
                t = cov.add(M, cov.neg(cov.add(cov.mul(mm["r"], Aexp), cov.mul(mm["s"], Bexp))))
                if cov.mul(cof, t) is not None:
                    fail("multipliers", f"j={mm['j']} cofactor part not in [l]Jac")
            # (c) relations
            recs = c.get("relation_records", [])
            if len(recs) != c["relations"]:
                fail("relation_records", f"{len(recs)} records vs relations={c['relations']}")
            rr = random.Random(f"check:{EXP_ID}:{i}")
            for rec in rr.sample(recs, min(SAMPLE, len(recs))):
                nrel_checked += 1
                rt = f"relation@test{rec['test_index']}"
                R = dec(rec["R"])
                if rec["T"] is None:
                    if rec.get("T_computed"):
                        fail(rt, "T missing")
                    continue
                T = dec(rec["T"])
                try:
                    Rr = cov.add(cov.add(cov.mul(rec["r"], Aexp), cov.mul(rec["s"], Bexp)), T)
                except ArithmeticError:
                    fail(rt, "rebuild hit exceptional divisor")
                    continue
                if Rr != R:
                    fail(rt, "rebuilt [r]A+[s]B+T != recorded R")
                if cov.mul(cof, T) is not None:
                    fail(rt, "T not in [l]Jac(C)")
                if R is None:
                    fail(rt, "R is identity")
                    continue
                u, v = R
                x1, x2 = rec["roots"]
                if cov.f.mul([(-x1) % p, 1], [(-x2) % p, 1]) != u:
                    fail(rt, "u does not equal (X-x1)(X-x2)")
                if x1 not in Sset or x2 not in Sset:
                    fail(rt, "root not in S")
                for xr, sg in zip(rec["roots"], rec["signs"]):
                    yv = peval(v, xr, p)
                    if yv * yv % p != peval(cov.F, xr, p):
                        fail(rt, f"v({xr}) not a root of F")
                        continue
                    ys = min(yv, p - yv)
                    if yv == ys and sg != 1 or yv != ys and sg != -1:
                        fail(rt, f"sign at {xr}")
            # (d) k claims
            la = c.get("linear_algebra")
            if la and la.get("verified"):
                kk = la.get("recovered_k")
                if kk is None or emul(kk, P, a, p) != Q:
                    fail("linear_algebra", "claimed verified but [recovered_k]P != Q")
            if not c.get("recovered_k_matches", {}).get("rho"):
                fail("rho", "did not recover k")
            rk = c.get("rho", {}).get("k")
            if rk is None or emul(rk, P, a, p) != Q:
                fail("rho.k", "[k]P != Q")
            if c.get("ctrl_pullback") is not True:
                fail("ctrl_pullback")
            if c.get("ctrl_homomorphism") is not True:
                fail("ctrl_homomorphism")
            # (e) probabilities
            t_, dc = c["tests"], c["decompositions"]
            if c["decomposition_probability"] != (dc / t_ if t_ else 0.0):
                fail("decomposition_probability", "!= decompositions/tests")
            nS = len(S)
            if c["factor_base_size"] != nS:
                fail("factor_base_size")
            if abs(c["predicted_probability"] - 2 * (nS / p) ** 2) > 1e-15:
                fail("predicted_probability", "!= 2(|S|/p)^2")
            if abs(c["predicted_probability_old"] - (nS / p) ** 2 / 2) > 1e-15:
                fail("predicted_probability_old", "!= (|S|/p)^2/2")
            if dc != c["relations"]:
                fail("relations", "!= decompositions")
        except (KeyError, TypeError, ValueError) as e:
            fail("record", f"malformed: {e!r}")
    print(f"{'OK' if not bad else 'FAIL'}: {len(cells)} cells, {nrel_checked} relations re-derived, "
          f"{len(bad)} problems" + ("" if not bad else " :: " + "; ".join(bad[:10])))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
