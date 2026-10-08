"""FourQ as a VERIFIED target: parameters, explicit endomorphisms, eigenvalues.

FourQ (Costello-Longa, Asiacrypt 2015) is the twisted Edwards curve
    E / F_{p^2}:  -x^2 + y^2 = 1 + d x^2 y^2,   p = 2^127 - 1,  F_{p^2} = F_p(i), i^2 = -1,
with #E(F_{p^2}) = 392 * N, N prime.  Its two endomorphisms psi (Q-curve,
degree 2 composed with Frobenius) and phi (complex multiplication) are given
in the authors' Magma script (FourQlib/FourQ-Magma/Full-Routine-Affine.txt)
as compositions through the isogenous Weierstrass model
    W: y^2 = x^3 + A x + B,  A = -(30 - 8 sqrt5),  B = 56 - 32 sqrt5,
with tau: E -> Ehat (degree 2), tau_dual: Ehat -> E, delta: W -> Ehat an
isomorphism, and phiW, psiW endomorphisms of W followed by the p-power
Frobenius.  This module transcribes those formulas, evaluates them on
points, and derives everything the sweeper needs from the evaluations:

* the group order and the generator are verified from the constants;
* the CM discriminant comes from the trace of Frobenius by the exact
  discriminant scan (no literature value is assumed);
* lambda_psi is the root of x^2 = +-2 (mod N) that the evaluated psi(P)
  actually realises, and lambda_phi the eigenvalue of the evaluated phi(P)
  among the candidates from the ring of discriminant D_K;
* the 4-dimensional decomposition {1, phi, psi, phi psi} is checked by
  reconstructing k*P from explicit images for random k.

Operation counts of phi and psi are those of THIS affine implementation
(with inversions) and are reported as such; the FourQ paper's optimised
projective formulas are cheaper.
"""
from __future__ import annotations

import json
import random
from dataclasses import dataclass, field

from sympy import isprime

from . import lattice as LA
from . import quadorder as QO


P127 = 2**127 - 1
D_IM = 125317048443780598345676279555970305165
D_RE = 4205857648805777768770
N_FOURQ = 0x29CBC14E5E0A72F05397829CBC14E5DFBD004DFE0F79992FB2540EC7768CE7
COFACTOR = 392
# FourQlib FourQ_params.h GENERATOR_x / GENERATOR_y: little-endian u64 limbs, [re_lo, re_hi, im_lo, im_hi]
GEN_X_LIMBS = (0x286592AD7B3833AA, 0x1A3472237C2FB305, 0x96869FB360AC77F6, 0x1E1F553F2878AA9C)
GEN_Y_LIMBS = (0xB924A2462BCBB287, 0x0E3FEE9BA120785A, 0x49A7C344844C8B5C, 0x6E1C4AF8630E0242)
RT5_IM = 87392807087336976318005368820707244464      # sqrt(5) = RT5_IM * i in F_{p^2}
RT2 = 2**64                                           # sqrt(2) in F_p since 2^128 = 2 (mod p)


@dataclass
class Fp2Counter:
    M: int = 0     # F_{p^2} multiplications
    S: int = 0     # F_{p^2} squarings
    I: int = 0     # F_{p^2} inversions
    Mp: int = 0    # F_p multiplications inside the above (3 per M, 2 per S)

    def reset(self):
        self.M = self.S = self.I = self.Mp = 0

    def snapshot(self):
        return {"M2": self.M, "S2": self.S, "I2": self.I, "Mp_equiv": self.Mp}


class Fp2:
    """a + b i over F_p, p = 2^127 - 1, with counted operations (counter shared)."""
    __slots__ = ("a", "b", "C")
    p = P127

    def __init__(self, a: int, b: int = 0, C: Fp2Counter | None = None):
        self.a, self.b = a % P127, b % P127
        self.C = C

    def _new(self, a, b):
        return Fp2(a, b, self.C)

    def __add__(self, o):
        return self._new(self.a + o.a, self.b + o.b)

    def __sub__(self, o):
        return self._new(self.a - o.a, self.b - o.b)

    def __neg__(self):
        return self._new(-self.a, -self.b)

    def __mul__(self, o):
        if isinstance(o, int):
            return self._new(self.a * o, self.b * o)
        if self.C is not None:
            self.C.M += 1
            self.C.Mp += 3
        p = P127
        ac, bd = self.a * o.a % p, self.b * o.b % p
        ad_bc = (self.a + self.b) * (o.a + o.b) - ac - bd
        return self._new(ac - bd, ad_bc)

    __rmul__ = __mul__

    def sqr(self):
        if self.C is not None:
            self.C.S += 1
            self.C.Mp += 2
        p = P127
        return self._new((self.a + self.b) * (self.a - self.b) % p, 2 * self.a * self.b % p)

    def inv(self):
        if self.C is not None:
            self.C.I += 1
            self.C.Mp += 2
        p = P127
        nrm = (self.a * self.a + self.b * self.b) % p
        ninv = pow(nrm, -1, p)
        return self._new(self.a * ninv, -self.b * ninv)

    def __truediv__(self, o):
        return self * o.inv()

    def conj(self):
        """The p-power Frobenius of F_{p^2}: a + b i -> a - b i."""
        return self._new(self.a, -self.b)

    def __eq__(self, o):
        return isinstance(o, Fp2) and self.a == o.a and self.b == o.b

    def __hash__(self):
        return hash((self.a, self.b))

    def is_zero(self):
        return self.a == 0 and self.b == 0

    def sqrt(self):
        """A square root in F_{p^2} (p = 3 mod 4), or None."""
        p = P127

        def sqrt_p(z):
            z %= p
            if z == 0:
                return 0
            r = pow(z, (p + 1) // 4, p)
            return r if r * r % p == z else None

        a, b = self.a, self.b
        if b == 0:
            r = sqrt_p(a)
            if r is not None:
                return self._new(r, 0)
            r = sqrt_p(-a)
            return None if r is None else self._new(0, r)
        nrm = (a * a + b * b) % p
        r = sqrt_p(nrm)
        if r is None:
            return None
        inv2 = pow(2, -1, p)
        for rr in (r, (-r) % p):
            x2 = (a + rr) * inv2 % p
            x = sqrt_p(x2)
            if x is None or x == 0:
                continue
            y = b * pow(2 * x, -1, p) % p
            cand = self._new(x, y)
            if cand.sqr() == self:
                return cand
        return None

    def __repr__(self):
        return f"({self.a:#x} + {self.b:#x} i)"


def fp2_from_limbs(limbs, C=None) -> Fp2:
    re = limbs[0] | (limbs[1] << 64)
    im = limbs[2] | (limbs[3] << 64)
    return Fp2(re, im, C)


# ---------------------------------------------------------------------------
# twisted Edwards curves over F_{p^2}
# ---------------------------------------------------------------------------

class Edwards:
    """-x^2 + y^2 = 1 + d x^2 y^2 (a = -1), affine, identity (0, 1)."""

    def __init__(self, d: Fp2, C: Fp2Counter):
        self.d, self.C = d, C
        self.one = Fp2(1, 0, C)

    def identity(self):
        return (Fp2(0, 0, self.C), Fp2(1, 0, self.C))

    def on_curve(self, P):
        x, y = P
        x2, y2 = x.sqr(), y.sqr()
        return (-x2 + y2) == (self.one + self.d * x2 * y2)

    def add(self, P, Q):
        x1, y1 = P
        x2, y2 = Q
        x1x2, y1y2 = x1 * x2, y1 * y2
        t = self.d * x1x2 * y1y2
        X = (x1 * y2 + y1 * x2) / (self.one + t)
        Y = (y1y2 + x1x2) / (self.one - t)
        return (X, Y)

    def neg(self, P):
        return (-P[0], P[1])

    def mul(self, k: int, P):
        if k < 0:
            return self.mul(-k, self.neg(P))
        R = self.identity()
        Q = P
        while k:
            if k & 1:
                R = self.add(R, Q)
            Q = self.add(Q, Q)
            k >>= 1
        return R

    def lift_x(self, x: Fp2):
        # y^2 = (1 + x^2) / (1 - d x^2)
        x2 = x.sqr()
        y2 = (self.one + x2) / (self.one - self.d * x2)
        y = y2.sqrt()
        return None if y is None else (x, y)


# ---------------------------------------------------------------------------
# the maps from the Magma script
# ---------------------------------------------------------------------------

class FourQMaps:
    def __init__(self, C: Fp2Counter):
        self.C = C
        f = lambda a, b=0: Fp2(a, b, C)  # noqa: E731
        self.d = f(D_RE, D_IM)
        self.E = Edwards(self.d, C)
        self.one, self.two = f(1), f(2)
        self.i = f(0, 1)
        self.rt5 = f(0, RT5_IM)
        self.rt2 = f(RT2)
        assert self.rt5.sqr() == f(5), "rt5 is not a square root of 5"
        assert self.rt2.sqr() == f(2), "rt2 is not a square root of 2"
        self.dhat = -(self.d + self.one).inv()
        self.Ehat = Edwards(self.dhat, C)
        self.A = -(f(30) - self.rt5 * 8)
        self.B = f(56) - self.rt5 * 32
        self.sd = self.dhat.sqrt()
        assert self.sd is not None and self.sd.sqr() == self.dhat
        s12_arg = -(f(12) + self.rt2 * 4 + self.rt5 * self.rt2 * 2)
        self.s12 = s12_arg.sqrt()
        assert self.s12 is not None and self.s12.sqr() == s12_arg
        self.c = self.rt2 * 2 + self.rt2 * self.rt5
        self.four = f(4)

    def on_W(self, P):
        x, y = P
        return y.sqr() == x * x.sqr() + self.A * x + self.B

    def tau(self, P):
        x, y = P
        x2, y2 = x.sqr(), y.sqr()
        X = (x * y * 2) / ((x2 + y2) * self.sd)
        Y = (x2 - y2 + self.two) / (y2 - x2)
        return (X, Y)

    def tau_dual(self, P):
        x, y = P
        x2, y2 = x.sqr(), y.sqr()
        X = (x * y * 2 * self.sd) / (x2 - y2 + self.two)
        Y = (y2 - x2) / (y2 + x2)
        return (X, Y)

    def delta(self, P):
        x, y = P
        X = self.s12 * (x - self.four) / y
        Y = (x - self.four - self.c) / (x - self.four + self.c)
        return (X, Y)

    def delta_inv(self, P):
        x, y = P
        t = self.c * (y + self.one) / (self.one - y)
        X = t + self.four
        Y = t * self.s12 / x
        return (X, Y)

    def phiW(self, P):
        x, y = P
        r = self.rt5
        f = lambda a, b=0: Fp2(a, b, self.C)  # noqa: E731
        x2 = x.sqr()
        x3 = x2 * x
        x4 = x2.sqr()
        x5 = x4 * x
        num = (x5 + r * 8 * x4 + (r * 40 + f(260)) * x3 + (r * 720 + f(640)) * x2
               + (r * 656 + f(4340)) * x + (r * 1920 + f(960)))
        q = x2 + r * 4 * x - (r * 4 - f(90)) * pow(5, -1, P127)
        X = num / (q.sqr() * 5)
        Y = -y * (x2 + (r * 4 - f(8)) * x - (r * 12 - f(26))) * (
            x4 + (r * 8 + f(8)) * x3 + x2 * 28 - (r * 48 + f(112)) * x - r * 32 - f(124))
        Y = Y / (r * q).sqr() / (r * q)
        return (X.conj(), Y.conj())            # X^p, Y^p

    def psiW(self, P):
        x, y = P
        r = self.rt5
        f = lambda a, b=0: Fp2(a, b, self.C)  # noqa: E731
        inv2 = pow(2, -1, P127)
        xm4 = x - self.four
        X = -x * inv2 - (f(9) + r * 4) / xm4
        Y = -y / (self.i * self.rt2) * (-f(inv2) + (f(9) + r * 4) / xm4.sqr())
        return (X.conj(), Y.conj())

    def phi(self, P):
        return self.tau_dual(self.delta(self.phiW(self.delta_inv(self.tau(P)))))

    def psi(self, P):
        return self.tau_dual(self.delta(self.psiW(self.delta_inv(self.tau(P)))))


# ---------------------------------------------------------------------------
# verification
# ---------------------------------------------------------------------------

@dataclass
class FourQResult:
    verified_parameters: bool = False
    verification: str = ""
    trace_fp2: int | None = None
    cm_discriminant: int | None = None
    conductor: int | None = None
    psi_relation: str = ""
    phi_relation: str = ""
    lambda_psi: int | None = None
    phi_element: tuple[int, int] | None = None
    lambda_phi: int | None = None
    endomorphism_checks: dict = field(default_factory=dict)
    ops_phi: dict = field(default_factory=dict)
    ops_psi: dict = field(default_factory=dict)
    decomposition: dict = field(default_factory=dict)
    note: str = ""


def verify_fourq(seed: int = 3) -> FourQResult:
    res = FourQResult()
    C = Fp2Counter()
    maps = FourQMaps(C)
    E = maps.E
    N = N_FOURQ
    p = P127
    if not isprime(N):
        res.verification = "N is not prime"
        return res
    order = COFACTOR * N
    t2 = p * p + 1 - order
    if abs(t2) > 2 * p:
        res.verification = "392 N is outside the Hasse interval"
        return res
    res.trace_fp2 = t2
    # generator from FourQlib, both limb conventions tried
    G = None
    for conv in (lambda L: L, lambda L: (L[2], L[3], L[0], L[1])):
        cand = (fp2_from_limbs(conv(GEN_X_LIMBS), C), fp2_from_limbs(conv(GEN_Y_LIMBS), C))
        if E.on_curve(cand):
            G = cand
            break
    if G is None:
        res.verification = "FourQlib generator is not on the curve under either limb convention"
        return res
    if E.mul(N, G) != E.identity():
        res.verification = "N * G is not the identity"
        return res
    # a second, independently lifted point of order N
    rng = random.Random(seed)
    P = None
    while P is None:
        Q = E.lift_x(Fp2(rng.randrange(p), rng.randrange(p), C))
        if Q is None:
            continue
        R = E.mul(COFACTOR, Q)
        if R != E.identity() and E.mul(N, R) == E.identity():
            P = R
    res.verified_parameters = True
    res.verification = "N prime; 392 N in the Hasse interval of p^2; FourQlib generator on E with N G = O; a random point times 392 has order N"
    # CM discriminant from the trace, exactly
    scan = QO.small_discriminant_scan(QO.frobenius_discriminant(p * p, t2), 2_000_000)
    res.cm_discriminant, res.conductor = scan.found, scan.conductor
    # the maps
    C.reset()
    phiP = maps.phi(P)
    res.ops_phi = C.snapshot()
    C.reset()
    psiP = maps.psi(P)
    res.ops_psi = C.snapshot()
    C.reset()
    checks = {"phi(P) on E": E.on_curve(phiP), "psi(P) on E": E.on_curve(psiP)}
    Q = E.mul(rng.randrange(1, N), P)
    checks["phi(P+Q) = phi(P)+phi(Q)"] = maps.phi(E.add(P, Q)) == E.add(phiP, maps.phi(Q))
    checks["psi(P+Q) = psi(P)+psi(Q)"] = maps.psi(E.add(P, Q)) == E.add(psiP, maps.psi(Q))
    # Both maps end in a p-power Frobenius, so neither is an element of the
    # CM order acting as a scalar with a known characteristic polynomial.  On
    # the cyclic subgroup each still acts as a scalar lambda, and lambda
    # satisfies a quadratic relation lambda^2 = d*lambda + c with SMALL
    # integers (the degree is small times a power of p, and p acts as 1 mod
    # N through pi_{p^2}).  Find (c, d) by testing phi(phi(P)) = c P + d phi(P)
    # over a box, then lambda as the root of x^2 - d x - c the image realises.
    from sympy.ntheory import sqrt_mod

    def find_relation(img, img2, bound_c=4000, bound_d=400):
        table = {}
        cP = E.identity()
        for c in range(0, bound_c + 1):
            table[cP] = c
            table[E.neg(cP)] = -c
            cP = E.add(cP, P)
        for d in range(-bound_d, bound_d + 1):
            cand = E.add(img2, E.neg(E.mul(d, img))) if d else img2
            if cand in table:
                return table[cand], d
        return None

    def realised_root(img, c, d):
        disc = (d * d + 4 * c) % N
        s = sqrt_mod(disc, N, all_roots=True) or []
        inv2 = pow(2, -1, N)
        for r in s:
            lam = (d + int(r)) * inv2 % N
            if E.mul(lam, P) == img:
                return lam
        return None

    rel_psi = find_relation(psiP, maps.psi(psiP))
    rel_phi = find_relation(phiP, maps.phi(phiP))
    res.psi_relation = (f"psi^2 = {rel_psi[1]} psi + {rel_psi[0]} on the subgroup" if rel_psi
                        else "no quadratic relation with |c|,|d| <= 60 on the subgroup")
    res.phi_relation = (f"phi^2 = {rel_phi[1]} phi + {rel_phi[0]} on the subgroup" if rel_phi
                        else "no quadratic relation with |c|,|d| <= 60 on the subgroup")
    checks["psi satisfies a small quadratic relation"] = rel_psi is not None
    checks["phi satisfies a small quadratic relation"] = rel_phi is not None
    if rel_psi:
        res.lambda_psi = realised_root(psiP, *rel_psi)
    if rel_phi:
        res.lambda_phi = realised_root(phiP, *rel_phi)
    checks["lambda_psi realised by psi(P)"] = res.lambda_psi is not None
    checks["lambda_phi realised by phi(P)"] = res.lambda_phi is not None
    # does phi coincide with a CM-order element on the subgroup?  (informational)
    if scan.found is not None and res.lambda_phi is not None:
        D = scan.found
        for lam_w in QO.omega_eigenvalues(D, N):
            for Nn in range(2, 65):
                for el in QO.elements_of_norm(D, Nn, primitive_only=True, up_to_units_and_conjugation=False):
                    if el.eigenvalue(lam_w, N) == res.lambda_phi:
                        res.phi_element = (el.a, el.b)
    checks["phi equals a CM-order element of norm <= 64 on the subgroup"] = res.phi_element is not None
    res.endomorphism_checks = checks
    if res.lambda_phi is None or res.lambda_psi is None:
        res.note = "eigenvalue identification incomplete; see checks"
        return res
    # 4-dimensional decomposition with explicit images
    lams = [1, res.lambda_phi, res.lambda_psi, res.lambda_phi * res.lambda_psi % N]
    red = LA.reduce(lams, N)
    cb = LA.coefficient_bits(red, samples=16, seed=seed)
    images = [P, phiP, psiP, maps.psi(phiP)]
    worst = 0
    ok = True
    for _ in range(4):
        k = rng.randrange(1, N)
        ks = red.decompose(k)
        worst = max(worst, max(abs(v) for v in ks))
        lhs = E.mul(k, P)
        rhs = E.identity()
        for ki, Qi in zip(ks, images):
            rhs = E.add(rhs, E.mul(ki, Qi))
        ok = ok and (lhs == rhs)
    res.decomposition = {"reconstructs kP (4 random k)": ok, "max_coeff_bits": worst.bit_length(),
                         "babai_bound_bits": cb["bound_bits"], "balanced_bits": cb["balanced_bits"],
                         "basis_inf_norm_bits": cb["basis_inf_norm_bits"]}
    return res


def fourq_target():
    """A registry Target for FourQ whose generators carry the VERIFIED eigenvalues."""
    from .targets import Target
    res = verify_fourq()
    gens = []

    def projective_equivalent_cost(ops: dict) -> float:
        # ASSUMPTION: the affine formulas carried projectively cost their M2 + S2
        # plus about 3 M2 per inversion avoided; in F_p (127-bit) units M2 = 3M, S2 = 2M.
        return 3.0 * ops["M2"] + 2.0 * ops["S2"] + 9.0 * ops["I2"]

    if res.lambda_phi is not None:
        gens.append({"name": f"phi (CM-type, {res.phi_relation})",
                     "eigenvalue": res.lambda_phi, "cost_M": projective_equivalent_cost(res.ops_phi),
                     "kind": "unit", "order_mod_n": None})
    if res.lambda_psi is not None:
        gens.append({"name": f"psi (Q-curve, {res.psi_relation})", "eigenvalue": res.lambda_psi,
                     "cost_M": projective_equivalent_cost(res.ops_psi), "kind": "frobenius", "order_mod_n": 2})
    T = Target("FourQ (verified maps)", P127, "structural", {}, N_FOURQ, 0, ext_degree=2,
               cost_model="twisted_edwards_a=-1_extended_fp2", declared_generators=gens,
               family="deployed",
               notes=(f"{res.verification}; D_K = {res.cm_discriminant}; {res.psi_relation}; {res.phi_relation}; "
                      f"phi/psi affine op counts {res.ops_phi} / {res.ops_psi}, charged as projective-equivalent "
                      f"{projective_equivalent_cost(res.ops_phi):.0f} M / {projective_equivalent_cost(res.ops_psi):.0f} M "
                      f"(assumption; the FourQ paper's optimised formulas are cheaper); costs in F_p (127-bit) multiplications"))
    T.verified = res.verified_parameters and res.lambda_phi is not None and res.lambda_psi is not None
    T.verification = res.verification if T.verified else f"VERIFICATION FAILED: {res.verification}; {res.note}"
    return T, res


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)
    res = verify_fourq()
    txt = json.dumps(res.__dict__, indent=1, default=str)
    if args.out:
        with open(args.out, "w") as f:
            f.write(txt)
    print(txt)
    return 0 if res.verified_parameters and res.lambda_phi is not None and res.lambda_psi is not None else 1


if __name__ == "__main__":
    raise SystemExit(main())
