"""Genus-2 Jacobians: the rank-4 route, with counted arithmetic and toy proofs.

A Jacobian of a genus-2 curve y^2 = f(x) (deg f = 5) with CM by a quartic
field has an endomorphism ring of Z-rank 4, so a cyclic prime-order subgroup
admits a FOUR-dimensional decomposition from FREE automorphisms:

* Buhler-Koblitz curves  y^2 = x^5 + b      carry zeta_5: (x, y) -> (z x, y),
  z a primitive 5th root of unity in F_p (p = 1 mod 5); Z[zeta_5] has rank 4;
* Furukawa-Kawazoe-Takahashi curves y^2 = x^5 + a x carry zeta_8:
  (x, y) -> (z^2 x, z y), z a primitive 8th root of unity (p = 1 mod 8);
  Z[zeta_8] has rank 4.

This module gives the sweeper the two things it lacked for that route:

1. **arithmetic with counted operations** -- Cantor's composition and
   reduction in affine Mumford form (u, v), generic and unoptimised, so the
   count is an honest UPPER bound on what explicit formulas cost;
2. **toy-scale proof of the structure** -- a BK (or FKT) Jacobian over a
   small prime, its order from the zeta function (#C(F_p) and #C(F_{p^2})
   by brute force), a divisor of prime order n, the eigenvalue of the
   automorphism on it, and the 4-dimensional decomposition reconstructing
   k*D from explicit images with coefficients inside the Babai bound.

``synthetic_genus2_targets`` registers structural 128-bit targets (a prime
n = 1 mod 5 or mod 8 of about 2^254, the automorphism as a declared unit of
that order) so the sweep ranks the rank-4 route next to the elliptic ones;
``install_counted_model`` writes the measured affine counts into the cost
table under ``genus2_affine_cantor_counted``.
"""
from __future__ import annotations

import json
import random
from dataclasses import dataclass

from sympy import factorint, isprime, nextprime
from sympy.ntheory.residue_ntheory import nthroot_mod

from . import costmodel as CM
from . import lattice as LA


# ---------------------------------------------------------------------------
# counted polynomial arithmetic over F_p (low-degree first)
# ---------------------------------------------------------------------------

class Counter:
    def __init__(self, p: int):
        self.p = p
        self.M = self.S = self.I = 0

    def snapshot(self):
        return {"M": self.M, "S": self.S, "I": self.I}

    def reset(self):
        self.M = self.S = self.I = 0


def _trim(f):
    while len(f) > 1 and f[-1] == 0:
        f.pop()
    return f


def deg(f):
    return -1 if (len(f) == 1 and f[0] == 0) else len(f) - 1


def padd(f, g, p):
    n = max(len(f), len(g))
    return _trim([((f[i] if i < len(f) else 0) + (g[i] if i < len(g) else 0)) % p for i in range(n)])


def psub(f, g, p):
    n = max(len(f), len(g))
    return _trim([((f[i] if i < len(f) else 0) - (g[i] if i < len(g) else 0)) % p for i in range(n)])


def pmul(f, g, C: Counter):
    p = C.p
    if deg(f) < 0 or deg(g) < 0:
        return [0]
    out = [0] * (len(f) + len(g) - 1)
    for i, a in enumerate(f):
        if a == 0:
            continue
        for j, b in enumerate(g):
            if b == 0:
                continue
            C.M += 1
            out[i + j] = (out[i + j] + a * b) % p
    return _trim(out)


def pscale(f, c, C: Counter):
    C.M += sum(1 for a in f if a)
    return _trim([(a * c) % C.p for a in f])


def pdivmod(f, g, C: Counter):
    """Quotient and remainder of f by g (g monic or not; one inversion if not)."""
    p = C.p
    f = list(f)
    dg = deg(g)
    if dg < 0:
        raise ZeroDivisionError
    if g[-1] != 1:
        C.I += 1
        inv = pow(g[-1], -1, p)
    else:
        inv = 1
    q = [0] * max(1, len(f) - dg)
    while deg(f) >= dg:
        c = f[-1] * inv % p
        if inv != 1:
            C.M += 1
        shift = len(f) - 1 - dg
        q[shift] = c
        for i in range(dg + 1):
            if g[i]:
                C.M += 1
                f[shift + i] = (f[shift + i] - c * g[i]) % p
        f.pop()
        if not f:
            f = [0]
            break
        _trim(f)
    return _trim(q), _trim(f)


def pxgcd(f, g, C: Counter):
    """Monic d = gcd(f, g) with d = s f + t g."""
    p = C.p
    r0, r1 = list(f), list(g)
    s0, s1 = [1], [0]
    t0, t1 = [0], [1]
    while deg(r1) >= 0:
        q, r = pdivmod(r0, r1, C)
        r0, r1 = r1, r
        s0, s1 = s1, psub(s0, pmul(q, s1, C), p)
        t0, t1 = t1, psub(t0, pmul(q, t1, C), p)
    if r0[-1] != 1:
        C.I += 1
        inv = pow(r0[-1], -1, p)
        r0, s0, t0 = pscale(r0, inv, C), pscale(s0, inv, C), pscale(t0, inv, C)
    return r0, s0, t0


# ---------------------------------------------------------------------------
# the Jacobian
# ---------------------------------------------------------------------------

class Jacobian:
    """J(C) for C: y^2 = f(x), f monic of degree 5, Mumford (u, v) representation."""

    def __init__(self, p: int, f: list[int], C: Counter | None = None):
        assert len(f) == 6 and f[5] % p == 1
        self.p, self.f = p, [c % p for c in f]
        self.C = C or Counter(p)

    def identity(self):
        return ([1], [0])

    def is_identity(self, D):
        return deg(D[0]) == 0

    def neg(self, D):
        u, v = D
        return (u, _trim([(-c) % self.p for c in v]))

    def on_jacobian(self, D) -> bool:
        u, v = D
        if u[-1] != 1 or deg(v) >= deg(u) and deg(u) > 0:
            return False
        Cq = Counter(self.p)
        _, r = pdivmod(psub(self.f, pmul(v, v, Cq), self.p), u, Cq)
        return deg(r) < 0

    def add(self, D1, D2):
        C, p = self.C, self.p
        u1, v1 = D1
        u2, v2 = D2
        if deg(u1) == 0:
            return D2
        if deg(u2) == 0:
            return D1
        # composition (Cantor)
        d1, e1, e2 = pxgcd(u1, u2, C)
        d, c1, c2 = pxgcd(d1, padd(v1, v2, p), C)
        s1, s2, s3 = pmul(c1, e1, C), pmul(c1, e2, C), c2
        u = pmul(u1, u2, C)
        if deg(d) > 0:
            u, _ = pdivmod(u, pmul(d, d, C), C)
        num = padd(padd(pmul(pmul(s1, u1, C), v2, C), pmul(pmul(s2, u2, C), v1, C), p),
                   pmul(s3, padd(pmul(v1, v2, C), self.f, p), C), p)
        if deg(d) > 0:
            num, _ = pdivmod(num, d, C)
        _, v = pdivmod(num, u, C)
        # reduction
        while deg(u) > 2:
            un, _ = pdivmod(psub(self.f, pmul(v, v, C), p), u, C)
            if un[-1] != 1:
                C.I += 1
                un = pscale(un, pow(un[-1], -1, p), C)
            _, v = pdivmod(_trim([(-c) % p for c in v]), un, C)
            u = un
        if u[-1] != 1:
            C.I += 1
            u = pscale(u, pow(u[-1], -1, p), C)
        return (u, v)

    def mul(self, k: int, D):
        if k < 0:
            return self.mul(-k, self.neg(D))
        R, Q = self.identity(), D
        while k:
            if k & 1:
                R = self.add(R, Q)
            Q = self.add(Q, Q)
            k >>= 1
        return R

    def point_divisor(self, x: int, y: int):
        return (_trim([(-x) % self.p, 1]), _trim([y % self.p]))

    def random_divisor(self, rng: random.Random):
        """Sum of two random points: a generic degree-2 divisor."""
        D = self.identity()
        for _ in range(2):
            while True:
                x = rng.randrange(self.p)
                rhs = sum(c * pow(x, i, self.p) for i, c in enumerate(self.f)) % self.p
                from sympy.ntheory import sqrt_mod
                y = sqrt_mod(rhs, self.p)
                if y is not None:
                    D = self.add(D, self.point_divisor(x, int(y)))
                    break
        return D

    def automorphism(self, D, alpha: int, beta: int):
        """Image of D under (x, y) -> (alpha x, beta y): u'(x) = alpha^deg u * u(x/alpha), v'(x) = beta v(x/alpha)."""
        p = self.p
        u, v = D
        du = deg(u)
        ainv = pow(alpha, -1, p)
        u2 = _trim([(c * pow(ainv, i, p) * pow(alpha, du, p)) % p for i, c in enumerate(u)])
        v2 = _trim([(beta * c * pow(ainv, i, p)) % p for i, c in enumerate(v)])
        self.C.M += 2 * len(u) + 2 * len(v)
        return (u2, v2)


# ---------------------------------------------------------------------------
# order of the Jacobian over a toy field, by the zeta function
# ---------------------------------------------------------------------------

def jacobian_order(p: int, f: list[int]) -> int:
    """#J(F_p) = 1 + a1 + a2 + p a1 + p^2 with a1 = N1 - p - 1, a2 = (N2 - p^2 - 1 + a1^2)/2."""
    # N1 = #C(F_p) including the single point at infinity
    def chi(z):
        z %= p
        if z == 0:
            return 0
        return 1 if pow(z, (p - 1) // 2, p) == 1 else -1

    def fx(x):
        return sum(c * pow(x, i, p) for i, c in enumerate(f)) % p

    N1 = 1 + sum(1 + chi(fx(x)) for x in range(p))
    # F_{p^2} = F_p[t]/(t^2 - nr), nr a non-residue; chi_2(c) = chi(Norm(c)), Norm(a + bt) = a^2 - nr b^2
    nr = next(z for z in range(2, p) if chi(z) == -1)
    fc = f
    N2 = 1
    for a in range(p):
        for b in range(p):
            # evaluate f at a + b t:  powers of (a + b t)
            xa, xb = 1, 0
            ra, rb = fc[0], 0
            for i in range(1, 6):
                xa, xb = (xa * a + xb * b * nr) % p, (xa * b + xb * a) % p
                ra, rb = (ra + fc[i] * xa) % p, (rb + fc[i] * xb) % p
            nrm = (ra * ra - nr * rb * rb) % p
            N2 += 1 + chi(nrm)
    a1 = N1 - p - 1
    a2 = (N2 - p * p - 1 + a1 * a1) // 2
    return 1 + a1 + a2 + p * a1 + p * p


# ---------------------------------------------------------------------------
# toy verification of the rank-4 decomposition
# ---------------------------------------------------------------------------

@dataclass
class Genus2ToyResult:
    family: str
    p: int
    f: list[int]
    jacobian_order: int
    n: int
    automorphism: tuple[int, int]
    eigenvalue: int | None
    checks: dict
    ops_add: dict
    ops_dbl: dict


def _toy_prime(bits: int, modulus: int, seed: int) -> int:
    rng = random.Random(seed)
    while True:
        p = nextprime(rng.randrange(1 << (bits - 1), 1 << bits))
        if p % modulus == 1:
            return p


def verify_genus2_toy(family: str = "BK", bits: int = 9, seed: int = 1) -> Genus2ToyResult:
    rng = random.Random(seed)
    if family == "BK":
        p = _toy_prime(bits, 5, seed)
        z = next(int(r) for r in nthroot_mod(1, 5, p, all_roots=True) if int(r) != 1)
        alpha, beta, order_m = z, 1, 5
    elif family == "FKT":
        p = _toy_prime(bits, 8, seed)
        z = next(int(r) for r in nthroot_mod(1, 8, p, all_roots=True) if pow(int(r), 4, p) != 1)
        alpha, beta, order_m = z * z % p, z, 8
    else:
        raise ValueError(family)
    # pick a curve whose Jacobian has a large prime factor
    for attempt in range(200):
        c = rng.randrange(1, p)
        f = [c, 0, 0, 0, 0, 1] if family == "BK" else [0, c, 0, 0, 0, 1]
        N = jacobian_order(p, f)
        fac = factorint(N)
        n = max(fac)
        if n > 4 * p and fac[n] == 1 and n % order_m == 1:
            break
    else:
        raise RuntimeError("no suitable toy curve found")
    J = Jacobian(p, f)
    # a divisor of order n
    D = None
    while D is None:
        R = J.mul(N // n, J.random_divisor(rng))
        if not J.is_identity(R):
            D = R
    checks = {"N*D = 0 (zeta-function order kills a random divisor)": J.is_identity(J.mul(N, J.random_divisor(rng))),
              "n*D = 0": J.is_identity(J.mul(n, D))}
    # the automorphism
    img = J.automorphism(D, alpha, beta)
    checks["automorphism image is on J"] = J.on_jacobian(img)
    lam = None
    for r in nthroot_mod(1, order_m, n, all_roots=True) or []:
        r = int(r)
        if r != 1 and J.mul(r, D) == img:
            lam = r
            break
    checks[f"automorphism acts as a primitive {order_m}th root of unity mod n"] = lam is not None
    ops_add = ops_dbl = {}
    if lam is not None:
        d = 4
        lams = [pow(lam, i, n) for i in range(d)]
        red = LA.reduce(lams, n)
        cb = LA.coefficient_bits(red, samples=16, seed=seed)
        images = [D]
        for _ in range(d - 1):
            images.append(J.automorphism(images[-1], alpha, beta))
        ok = True
        worst = 0
        for _ in range(6):
            k = rng.randrange(1, n)
            ks = red.decompose(k)
            worst = max(worst, max(abs(v) for v in ks))
            lhs = J.mul(k, D)
            rhs = J.identity()
            for ki, Qi in zip(ks, images):
                rhs = J.add(rhs, J.mul(ki, Qi))
            ok = ok and (lhs == rhs)
        checks["4-dim decomposition reconstructs k*D (6 random k)"] = ok
        checks["max coefficient bits / Babai bound / ideal"] = (worst.bit_length(), cb["bound_bits"], cb["balanced_bits"])
        # operation counts of generic affine Cantor arithmetic
        J.C.reset()
        A, B = J.random_divisor(rng), J.random_divisor(rng)
        J.C.reset()
        J.add(A, B)
        ops_add = J.C.snapshot()
        J.C.reset()
        J.add(A, A)
        ops_dbl = J.C.snapshot()
    return Genus2ToyResult(family, p, f, N, n, (alpha, beta), lam, checks, ops_add, ops_dbl)


# ---------------------------------------------------------------------------
# cost-model hook and synthetic targets
# ---------------------------------------------------------------------------

def install_counted_model(bits: int = 9, seed: int = 1) -> dict:
    """Measure generic affine Cantor ADD/DBL counts and write them into the cost table."""
    r = verify_genus2_toy("BK", bits, seed)
    add, dbl = r.ops_add, r.ops_dbl
    # charge I at I_PER_M, S as M (the counter does not separate squarings)
    CM.CURVE_MODELS["genus2_affine_cantor_counted"]["DBL"] = (dbl["M"] + CM.I_PER_M * dbl["I"], 0)
    CM.CURVE_MODELS["genus2_affine_cantor_counted"]["ADD"] = (add["M"] + CM.I_PER_M * add["I"], 0)
    CM.CURVE_MODELS["genus2_affine_cantor_counted"]["mADD"] = (add["M"] + CM.I_PER_M * add["I"], 0)
    return {"ADD": add, "DBL": dbl}


def synthetic_genus2_targets(bits: int = 127) -> list:
    """Structural 128-bit-security genus-2 targets: prime n ~ 2^254 with the automorphism's order dividing n-1."""
    from .targets import Target
    out = []
    p = nextprime(1 << bits)

    def primitive_root_of_unity(m: int, n: int) -> int:
        """A primitive m-th root of unity mod the prime n (m | n-1), without sympy's slow nthroot_mod."""
        g = 2
        while True:
            z = pow(g, (n - 1) // m, n)
            if all(pow(z, m // q, n) != 1 for q in factorint(m)):
                return z
            g += 1

    for family, m in (("Buhler-Koblitz y^2=x^5+b, zeta_5", 5), ("Furukawa-Kawazoe-Takahashi y^2=x^5+ax, zeta_8", 8)):
        n = nextprime(p * p - 3 * p)
        while n % (4 * m) != 1:
            n = nextprime(n)
        z = primitive_root_of_unity(m, n)
        i_root = primitive_root_of_unity(4, n)
        for model in ("genus2_projective_assumed", "genus2_affine_cantor_counted"):
            out.append(Target(
                f"synthetic genus-2 {family} over F_p, p~2^{bits} [{model}]", p, "structural", {}, n, 0,
                cost_model=model, family="synthetic",
                declared_generators=[{"name": f"zeta_{m} automorphism", "eigenvalue": z, "cost_M": 4.0,
                                      "kind": "unit", "order_mod_n": m}],
                notes="rank-4 CM Jacobian; n is a prime of the right residue class, no curve equation; "
                      "costs in F_p (128-bit) multiplications under the named model"))
        # the F_{p^2} variant with a GLS-type Frobenius (psi^2 = -1 on the subgroup): 8-dimensional
        out.append(Target(
            f"synthetic genus-2 {family} over F_p^2 with GLS psi, p~2^{bits // 2} [genus2_projective_assumed]",
            nextprime(1 << (bits // 2)), "structural", {}, n, 0, ext_degree=2,
            cost_model="genus2_projective_assumed", family="synthetic",
            declared_generators=[{"name": f"zeta_{m} automorphism", "eigenvalue": z, "cost_M": 4.0,
                                  "kind": "unit", "order_mod_n": m},
                                 {"name": "psi (GLS twist Frobenius), psi^2=-1", "eigenvalue": i_root,
                                  "cost_M": 12.0, "kind": "frobenius", "order_mod_n": 4}],
            notes="Bos-Costello-Hisil-Lauter 2013 8-dimensional setting; costs in F_{p^2} multiplications "
                  "of a 64-bit p under the assumed model"))
    return out


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--bits", type=int, default=9)
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)
    out = {fam: verify_genus2_toy(fam, args.bits).__dict__ for fam in ("BK", "FKT")}
    txt = json.dumps(out, indent=1, default=str)
    if args.out:
        with open(args.out, "w") as f:
            f.write(txt)
    print(txt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
