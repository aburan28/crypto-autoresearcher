"""Q-curves over F_{p^2} beyond FourQ: explicit maps, CM sweep, dominance table.

A quadratic Q-curve of degree d (Smith, "Families of fast elliptic curves
from Q-curves", Asiacrypt 2013) reduced at an inert prime is a curve E over
F_{p^2} with a d-isogeny phi: E -> E^(p) to its Frobenius conjugate; then

    psi = pi_p o (isomorphism) o phi :  E -> E^(p) -> E^(p^2) = E

is an endomorphism of degree d*p with psi^2 = +-d * pi_{p^2}, so on
E(F_{p^2}) it acts as a square root of +-d.  FourQ (Costello-Longa 2015) is
the degree-2 member with complex multiplication by D = -40, where a second
such map (degree 5) gives the 4-dimensional decomposition.

This module does three things.

1. **Explicit maps at 127 bits (verified on points).**  Over F_{p^2},
   p = 2^127 - 1, a curve with a d-isogeny to its conjugate is found from the
   Hauptmodul of X_0(d): j = (t + 16)^3 / t with t * t^p = 4096 (d = 2), and
   j = (t + 27)(t + 3)^3 / t with t * t^p = 729 (d = 3), because the
   Atkin-Lehner involution t -> c/t sends j(tau) to j(d tau) and
   t^p = c/t makes j(d tau) = j^p.  The parametrisation is only a search
   device: every claim is re-checked on the constructed objects.  The kernel
   is a root of the 2- or 3-division polynomial in F_{p^2} (Cantor-Zassenhaus
   here), the codomain comes from Velu's formulas and must have j = j(E)^p,
   the isomorphism to E^(p) must be defined over F_{p^2}, and then
   psi(psi(P)) = [+-d] P is checked on random points, psi(P + Q) = psi(P) +
   psi(Q) is checked, and -- with #E from PARI's SEA (cypari2) -- the
   eigenvalue of psi on a subgroup of large prime order l and the 2-dim
   decomposition k = k1 + k2 lambda are checked.  The same builder is run on
   FourQ's own Weierstrass model W (from ``fourq.py``) as a cross-check.
   Operation counts of psi are those of this affine implementation.

2. **The CM sweep at p = 2^127 - 1 (exact, from CM theory).**  A 4-dim
   decomposition needs two independent cheap endomorphisms in the rank-2 ring
   End(E); on a Q-curve that means CM.  For a fundamental D < 0 with p split
   and the class of a prime p above p of order exactly 2, the CM curves have
   j in F_{p^2} \\ F_p, pi_{p^2} generates p^2 (Cornacchia), #E =
   N(pi - 1) for pi = +-gamma, and each ideal a in the class of p gives a
   Q-curve isogeny E -> E^(p) of degree N(a); psi_a is the element beta in p
   with (beta) = a p.  Its eigenvalue on the order-n subgroup is
   beta(lambda_omega) with lambda_omega fixed by pi = 1 there.  Everything is
   integer arithmetic in the order; D = -40 must reproduce FourQ's #E =
   392 * N and its lattice.  The curves themselves are not constructed in the
   sweep (only the FourQ point is cross-checked against ``fourq.py``).

3. **Costs (modelled).**  ``costmodel.multiscalar_cost`` on the exact LLL
   lattice of each configuration, F_p multiplications of 127-bit p, twisted
   Edwards a = -1 over F_{p^2} for every row (assuming the model exists:
   4 | #E is necessary and is reported) and Jacobian generic-a Weierstrass
   over F_{p^2} as a second model.  A degree-d map is charged

       c(d) = 3 * (sum over its prime steps of isogeny_step_cost(ell) + 20) + 6   [M]

   i.e. the harness's x-only step counts plus its 20 M2 y-recovery/model
   overhead, in F_{p^2} (M2 = 3 M), plus 2 M2 for the isomorphism; the
   Frobenius is a free conjugation.  FourQ is costed both with that formula
   and with ``fourq.py``'s measured (affine, projective-equivalent) counts.
"""
from __future__ import annotations

import json
import random
import time
from dataclasses import asdict, dataclass, field

from sympy import factorint, isprime, nextprime
from sympy.ntheory import sqrt_mod

from . import costmodel as CM
from . import fourq as FQ
from . import lattice as LA
from . import quadorder as QO

P = FQ.P127
Q2 = P * P

# Jacobian coordinates, generic a, over F_{p^2} in F_p units (M2 = 3 M, S2 = 2 M):
# DBL 1M2 + 8S2 = 19 M, ADD 11M2 + 5S2 = 43 M, mADD 7M2 + 4S2 = 29 M
CM.CURVE_MODELS.setdefault("weierstrass_jacobian_generic_a_fp2", {
    "note": "EFD dbl-2007-bl 1M+8S, add-2007-bl 11M+5S, madd-2007-bl 7M+4S over F_{p^2}, "
            "converted with M2 = 3M, S2 = 2M",
    "DBL": (19, 0), "ADD": (43, 0), "mADD": (29, 0)})

HAUPTMODUL = {
    # d: (Atkin-Lehner constant c, sqrt(c), j(t) numerator/denominator as callables on Fp2)
    2: (4096, 64),
    3: (729, 27),
}


def F(a, b=0, C=None):
    return FQ.Fp2(a, b, C)


def j_of_t(d: int, t):
    if d == 2:
        return (t + F(16)).sqr() * (t + F(16)) / t
    if d == 3:
        return (t + F(27)) * (t + F(3)).sqr() * (t + F(3)) / t
    raise ValueError(d)


def j_invariant(A, B):
    A3 = A.sqr() * A * 4
    return A3 * 1728 / (A3 + B.sqr() * 27)


def fp2_pow(x, e: int):
    r, b = F(1), x
    while e:
        if e & 1:
            r = r * b
        b = b.sqr()
        e >>= 1
    return r


def is_square(x) -> bool:
    return x.is_zero() or fp2_pow(x, (Q2 - 1) // 2) == F(1)


# ---------------------------------------------------------------------------
# polynomials over F_{p^2} (low degree first) and root finding
# ---------------------------------------------------------------------------

def _ptrim(f):
    while len(f) > 1 and f[-1].is_zero():
        f.pop()
    return f


def _pmul(f, g):
    out = [F(0)] * (len(f) + len(g) - 1)
    for i, a in enumerate(f):
        for j, b in enumerate(g):
            out[i + j] = out[i + j] + a * b
    return _ptrim(out)


def _pmod(f, m):
    f = list(f)
    inv = m[-1].inv()
    while len(f) >= len(m) and not (len(f) == 1 and f[0].is_zero()):
        c = f[-1] * inv
        s = len(f) - len(m)
        for i, b in enumerate(m):
            f[s + i] = f[s + i] - c * b
        f.pop()
        if not f:
            return [F(0)]
    return _ptrim(f) if f else [F(0)]


def _pgcd(f, g):
    while not (len(g) == 1 and g[0].is_zero()):
        f, g = g, _pmod(f, g)
    inv = f[-1].inv()
    return [c * inv for c in f]


def _ppowmod(base, e: int, m):
    r, b = [F(1)], _pmod(base, m)
    while e:
        if e & 1:
            r = _pmod(_pmul(r, b), m)
        b = _pmod(_pmul(b, b), m)
        e >>= 1
    return r


def roots_fp2(f, rng: random.Random) -> list:
    """All roots in F_{p^2} of a squarefree-or-not polynomial f (Cantor-Zassenhaus)."""
    f = _ptrim(list(f))
    xq = _ppowmod([F(0), F(1)], Q2, f)
    xq = xq + [F(0)] * max(0, 2 - len(xq))
    xq[1] = xq[1] - F(1)                      # X^(p^2) - X mod f
    xq = _ptrim(xq)
    g = f if (len(xq) == 1 and xq[0].is_zero()) else _pgcd(f, xq)
    out = []

    def split(h):
        if len(h) == 1:
            return
        if len(h) == 2:
            out.append(-(h[0] / h[1]))
            return
        while True:
            dlt = F(rng.randrange(P), rng.randrange(P))
            w = _ppowmod([dlt, F(1)], (Q2 - 1) // 2, h)
            w = [w[0] - F(1)] + w[1:]
            d = _pgcd(h, _ptrim(w)) if not (len(w) == 1 and w[0].is_zero()) else h
            if 1 < len(d) < len(h):
                split(d)
                split(_pdiv_exact(h, d))
                return

    split(g)
    return out


def _pdiv_exact(f, g):
    f = list(f)
    q = [F(0)] * (len(f) - len(g) + 1)
    inv = g[-1].inv()
    while len(f) >= len(g):
        c = f[-1] * inv
        s = len(f) - len(g)
        q[s] = c
        for i, b in enumerate(g):
            f[s + i] = f[s + i] - c * b
        f.pop()
    return _ptrim(q)


# ---------------------------------------------------------------------------
# short Weierstrass curves over F_{p^2}, affine (verification only)
# ---------------------------------------------------------------------------

class Weierstrass:
    def __init__(self, A, B):
        self.A, self.B = A, B

    def on_curve(self, Pt) -> bool:
        if Pt is None:
            return True
        x, y = Pt
        return y.sqr() == x.sqr() * x + self.A * x + self.B

    def add(self, P1, P2):
        if P1 is None:
            return P2
        if P2 is None:
            return P1
        x1, y1 = P1
        x2, y2 = P2
        if x1 == x2:
            if (y1 + y2).is_zero():
                return None
            lam = (x1.sqr() * 3 + self.A) / (y1 * 2)
        else:
            lam = (y2 - y1) / (x2 - x1)
        x3 = lam.sqr() - x1 - x2
        return (x3, lam * (x1 - x3) - y1)

    def neg(self, Pt):
        return None if Pt is None else (Pt[0], -Pt[1])

    def mul(self, k: int, Pt):
        if k < 0:
            return self.mul(-k, self.neg(Pt))
        R, Qp = None, Pt
        while k:
            if k & 1:
                R = self.add(R, Qp)
            Qp = self.add(Qp, Qp)
            k >>= 1
        return R

    def random_point(self, rng: random.Random):
        while True:
            x = F(rng.randrange(P), rng.randrange(P))
            y = (x.sqr() * x + self.A * x + self.B).sqrt()
            if y is not None:
                return (x, y)


# ---------------------------------------------------------------------------
# the Q-curve map psi = Frob o iso o Velu
# ---------------------------------------------------------------------------

@dataclass
class QMap:
    d: int
    x0: object          # kernel x-coordinate
    v: object
    u: object           # 0 for d = 2
    mu2: object         # isomorphism E' -> E^(p): (x, y) -> (mu^2 x, mu^3 y)
    mu3: object

    def __call__(self, Pt, C=None):
        if Pt is None:
            return None
        x, y = Pt
        x0, v, u, mu2, mu3 = self.x0, self.v, self.u, self.mu2, self.mu3
        if C is not None:          # count every operation, constants included
            x, y = F(x.a, x.b, C), F(y.a, y.b, C)
            x0, v, u, mu2, mu3 = (F(z.a, z.b, C) for z in (x0, v, u, mu2, mu3))
        one = F(1, 0, C)
        s = (x - x0).inv()
        s2 = s.sqr()
        if self.d == 2:
            X = x + v * s
            Y = y * (one - v * s2)
        else:
            s3 = s2 * s
            X = x + v * s + u * s2
            Y = y * (one - v * s2 - u * s3 * 2)
        X, Y = (mu2 * X).conj(), (mu3 * Y).conj()
        return (F(X.a, X.b), F(Y.a, Y.b))


def build_qmap(A, B, d: int, rng: random.Random) -> tuple[QMap | None, str]:
    """psi on y^2 = x^3 + A x + B over F_{p^2}, or None with the reason."""
    if d == 2:
        poly = [B, A, F(0), F(1)]
    elif d == 3:
        poly = [-A.sqr(), B * 12, A * 6, F(0), F(3)]
    else:
        raise ValueError(d)
    target = j_invariant(A, B).conj()
    roots = roots_fp2(poly, rng)
    if not roots:
        return None, "no F_{p^2}-rational kernel"
    for x0 in roots:
        gx = x0.sqr() * 3 + A
        if d == 2:
            v, u = gx, F(0)
        else:
            v, u = gx * 2, (x0.sqr() * x0 + A * x0 + B) * 4
        w = u + x0 * v
        A1, B1 = A - v * 5, B - w * 7
        if A1.is_zero() or B1.is_zero() or j_invariant(A1, B1) != target:
            continue
        mu2 = (B.conj() * A1) / (A.conj() * B1)
        mu = mu2.sqrt()
        if mu is None:
            return None, "codomain is the quadratic twist of E^(p) over F_{p^2} (mu^2 not a square)"
        assert (mu2.sqr() * A1) == A.conj() and (mu2.sqr() * mu2 * B1) == B.conj()
        return QMap(d, x0, v, u, mu2, mu2 * mu), "ok"
    return None, "no kernel whose Velu codomain has j = j(E)^p"


@dataclass
class ExplicitQCurve:
    d: int
    source: str
    A: str = ""
    B: str = ""
    t: str = ""
    tries: int = 0
    psi_sign: int | None = None
    order: int | None = None
    l: int | None = None
    cofactor: int | None = None
    eigenvalue: int | None = None
    checks: dict = field(default_factory=dict)
    ops_psi_affine: dict = field(default_factory=dict)
    psi_projective_equivalent_M: float | None = None
    decomposition: dict = field(default_factory=dict)
    note: str = ""


def _fp2_str(x) -> str:
    return f"{x.a:#x} + {x.b:#x}*i"


def _pari_order(A, B) -> int | None:
    try:
        import cypari2
    except ImportError:
        return None
    pari = cypari2.Pari()
    pari.allocatemem(256 * 10**6, silent=True) if hasattr(pari, "allocatemem") else None
    expr = (f"my(g=ffgen(Mod(1,{P})*(y^2+1),'y)); ellcard(ellinit([{A.a}+{A.b}*g,{B.a}+{B.b}*g],g))")
    return int(pari(expr))


def _large_prime_part(N: int, smooth: int = 1 << 20) -> tuple[int, int] | None:
    h = 1
    m = N
    q = 2
    while q < smooth and q * q <= m:
        while m % q == 0:
            m //= q
            h *= q
        q = nextprime(q)
    return (h, m) if m > 1 and isprime(m) else None


def verify_explicit(Ecurve: Weierstrass, psi: QMap, d: int, rng: random.Random, res: ExplicitQCurve,
                    order: int | None) -> None:
    E = Ecurve
    Ps = [E.random_point(rng) for _ in range(3)]
    res.checks["psi(P) on E (3 random points)"] = all(E.on_curve(psi(Pt)) for Pt in Ps)
    res.checks["psi(P+Q) = psi(P) + psi(Q)"] = psi(E.add(Ps[0], Ps[1])) == E.add(psi(Ps[0]), psi(Ps[1]))
    sign = None
    for eps in (1, -1):
        if all(psi(psi(Pt)) == E.mul(eps * d, Pt) for Pt in Ps):
            sign = eps
    res.psi_sign = sign
    res.checks[f"psi(psi(P)) = [+-{d}]P on 3 random points (sign {sign})"] = sign is not None
    C = FQ.Fp2Counter()
    psi(Ps[2], C)
    res.ops_psi_affine = C.snapshot()
    res.psi_projective_equivalent_M = 3.0 * C.M + 2.0 * C.S + 9.0 * C.I   # same rule as fourq_target
    if order is None or sign is None:
        return
    res.order = order
    lp = _large_prime_part(order)
    if lp is None:
        res.note = "no large prime factor found after trial division"
        return
    h, l = lp
    res.l, res.cofactor = l, h
    G = None
    while G is None:
        G = E.mul(h, E.random_point(rng))
    res.checks["[#E] P = O for a random P"] = E.mul(order, E.random_point(rng)) is None
    res.checks["[l] G = O, G = [h] P != O"] = E.mul(l, G) is None
    roots = sqrt_mod((sign * d) % l, l, all_roots=True) or []
    pg = psi(G)
    lam = next((int(r) for r in roots if E.mul(int(r), G) == pg), None)
    res.eigenvalue = lam
    res.checks[f"psi acts on <G> as a square root of {sign * d} mod l"] = lam is not None
    if lam is not None:
        red = LA.reduce([1, lam], l)
        cb = LA.coefficient_bits(red, samples=32)
        ok = True
        for _ in range(3):
            k = rng.randrange(1, l)
            k1, k2 = red.decompose(k)
            ok &= E.mul(k, G) == E.add(E.mul(k1, G), E.mul(k2, pg))
        res.decomposition = {"reconstructs kG (3 random k)": ok, **cb, "l_bits": l.bit_length()}
        res.checks["2-dim decomposition reconstructs kG"] = ok


def explicit_qcurve(d: int, seed: int = 1, max_tries: int = 40, want_order: bool = True) -> ExplicitQCurve:
    """A degree-d Q-curve over F_{p^2}, p = 2^127 - 1, from the X_0(d) Hauptmodul; verified on points."""
    rng = random.Random(seed)
    c, sc = HAUPTMODUL[d]
    res = ExplicitQCurve(d, f"X_0({d}) Hauptmodul, t * t^p = {c}")
    reasons: dict = {}
    for attempt in range(1, max_tries + 1):
        r = F(rng.randrange(1, P), rng.randrange(1, P))
        w = r.conj() / r                       # norm one
        t = w * sc
        assert t * t.conj() == F(c)
        j = j_of_t(d, t)
        if j.is_zero() or j == F(1728):
            continue
        A = j * (F(1728) - j) * 3
        B = j * (F(1728) - j).sqr() * 2
        psi, why = build_qmap(A, B, d, rng)
        reasons[why] = reasons.get(why, 0) + 1
        if psi is None:
            continue
        E = Weierstrass(A, B)
        res.tries = attempt
        res.A, res.B, res.t = _fp2_str(A), _fp2_str(B), _fp2_str(t)
        order = _pari_order(A, B) if want_order else None
        if want_order and order is not None and _large_prime_part(order) is None:
            continue
        verify_explicit(E, psi, d, rng, res, order)
        if order is None and want_order:
            res.note = "cypari2 unavailable: #E not computed, eigenvalue on a prime-order subgroup not checked"
        res.checks["j(E) = j(t) has j(E)^p = j of the Velu codomain"] = True
        res.note = (res.note + f"; build outcomes over attempts: {reasons}").strip("; ")
        return res
    res.note = f"no member in {max_tries} attempts: {reasons}"
    return res


def fourq_w_crosscheck(seed: int = 2) -> ExplicitQCurve:
    """Run the degree-2 builder on FourQ's Weierstrass model W and check psi^2 = +-2 there."""
    rng = random.Random(seed)
    m = FQ.FourQMaps(FQ.Fp2Counter())
    A, B = F(m.A.a, m.A.b), F(m.B.a, m.B.b)
    res = ExplicitQCurve(2, "FourQ's W: y^2 = x^3 - (30 - 8 sqrt5) x + 56 - 32 sqrt5 (fourq.py)")
    res.A, res.B = _fp2_str(A), _fp2_str(B)
    psi, why = build_qmap(A, B, 2, rng)
    if psi is None:
        res.note = why
        return res
    E = Weierstrass(A, B)
    # #W = #E_FourQ (isogenous): 392 N
    verify_explicit(E, psi, 2, rng, res, FQ.COFACTOR * FQ.N_FOURQ)
    return res


# ---------------------------------------------------------------------------
# CM Q-curves at p = 2^127 - 1: exact orders and eigenvalues from the order
# ---------------------------------------------------------------------------

def _sqrt_mod_composite(Dv: int, M: int) -> list[int]:
    from sympy.ntheory.modular import crt
    import itertools
    fac = factorint(M)
    sets, mods = [], []
    for pr, e in fac.items():
        rs = QO._sqrt_mod_prime_power(Dv, pr, e)
        if not rs:
            return []
        sets.append(rs)
        mods.append(pr ** e)
    out = set()
    for combo in itertools.product(*sets):
        out.add(int(crt(mods, list(combo))[0]) % M if len(mods) > 1 else combo[0] % M)
    return sorted(out)


def all_elements_of_norm(D: int, M: int) -> list[tuple[int, int]]:
    """Every (a, b), b != 0, with N(a + b omega) = M and gcd(b, M) = 1 (Cornacchia over all roots)."""
    from math import gcd, isqrt
    tau = D % 2
    absD = -D
    lim = isqrt(4 * M)
    out = set()
    for r in _sqrt_mod_composite(D % M, M) if M > 1 else [0]:
        for x0 in {r % M, (-r) % M}:
            if (x0 - D) % 2:
                x0 = (x0 + M) if M % 2 else x0
            a_, b_ = 2 * M, x0
            while b_ > lim:
                a_, b_ = b_, a_ % b_
            x = b_
            rem = 4 * M - x * x
            if rem <= 0 or rem % absD:
                continue
            y = isqrt(rem // absD)
            if y * y != rem // absD or gcd(y, M) != 1:
                continue
            for sx in (x, -x):
                for sy in (y, -y):
                    if (sx - sy * tau) % 2 == 0:
                        a, b = (sx - sy * tau) // 2, sy
                        if QO.norm(D, a, b) == M:
                            out.add((a, b))
    return sorted(out)


def _reduce_mod(D, x, p):
    return (x[0] % p, x[1] % p)


@dataclass
class CMQCandidate:
    D: int
    class_number_hint: str
    twist: int
    order: int
    cofactor: int
    n: int
    n_bits: int
    four_divides_order: bool
    pi: tuple[int, int]
    ideal_norms_in_class: list[int]
    best_2d: dict = field(default_factory=dict)
    best_4d: dict = field(default_factory=dict)
    pairs_4d: list = field(default_factory=list)
    is_fourq: bool = False
    fourq_crosscheck: dict = field(default_factory=dict)


def _fourq_eigen_crosscheck(betas, n: int) -> dict:
    """Express FourQ's verified psi, phi eigenvalues (fourq.py) as multiples of the CM-derived ones."""
    res = FQ.verify_fourq()
    out = {}
    for name, lam in (("psi (fourq.py)", res.lambda_psi), ("phi (fourq.py)", res.lambda_phi)):
        for N, lb, _ in betas:
            for m in (1, -1, 2, -2, 4, -4, 8, -8):
                if (m * lb - lam) % n == 0:
                    out[name] = f"= {m} * psi_a with N(a) = {N}"
        out.setdefault(name, "no match")
    return out


def map_cost(d: int) -> float:
    """Modelled cost (F_p M, 127-bit p) of a degree-d Q-curve map psi on an F_{p^2} curve."""
    steps = sum(e * CM.isogeny_step_cost(ell) for ell, e in factorint(d).items()) if d > 1 else 0.0
    return CM.M2_PER_M * (steps + CM.ISOGENY_CHAIN_OVERHEAD_M) + 2 * CM.M2_PER_M


def _order2_class(D: int, p: int):
    """Reduced form of a prime above p if its class has order exactly 2, else None."""
    if QO.kronecker_symbol_disc(D, p) != 1:
        return None
    b = int(sqrt_mod(D % (4 * p), 4 * p)) if False else None
    r = int(sqrt_mod(D % p, p))
    if (r - D) % 2:
        r = p - r
    # b = r (mod 2p) and b = D (mod 2) -> (b^2 - D) divisible by 4p
    b = r if (r * r - D) % (4 * p) == 0 else (r + p) % (2 * p)
    assert (b * b - D) % (4 * p) == 0
    f = QO.reduce_form(p, b, (b * b - D) // (4 * p))
    one = QO.principal_form(D)
    if f == one:
        return None
    if QO.compose_forms(f, f) != one:
        return None
    return f


def _class_norms(form, bound: int) -> list[int]:
    from math import gcd
    a, b, c = form
    out = set()
    for x in range(-bound, bound + 1):
        for y in range(0, bound + 1):
            if (x, y) == (0, 0) or gcd(x, y) != 1:
                continue
            v = a * x * x + b * x * y + c * y * y
            if v <= bound:
                out.add(v)
    return sorted(out)


def _cost_config(lams: list[int], n: int, costs: list[float], model: str, kinds: list[str]) -> dict:
    red = LA.reduce(lams, n)
    cb = LA.coefficient_bits(red, samples=256, seed=1)
    gens = [CM.Generator("1", 1, 0.0, "identity")] + [
        CM.Generator(f"g{i}", lam, c, k) for i, (lam, c, k) in enumerate(zip(lams[1:], costs, kinds), 1)]
    cost = CM.multiscalar_cost(cb["empirical_max_bits"], gens, model)
    return {"coeff_bits": cb["empirical_max_bits"], "bound_bits": cb["bound_bits"],
            "balanced_bits": round(cb["balanced_bits"], 2), "total_M": round(cost.total_M, 1),
            "endomorphism_M": round(cost.endomorphism_M, 1), "window": cost.window,
            "doublings": cost.doublings, "additions": round(cost.additions, 1)}


def cm_sweep(Dmax: int = 3000, p: int = P, max_cofactor: int = 1 << 12, max_norm: int = 61,
             models=("twisted_edwards_a=-1_extended_fp2", "weierstrass_jacobian_generic_a_fp2"),
             log=None) -> dict:
    t0 = time.time()
    stats = {"fundamental_D": 0, "p_split": 0, "class_of_p_order_2": 0, "candidates_small_cofactor": 0}
    cands: list[CMQCandidate] = []
    for D in QO.fundamental_discriminants(Dmax):
        if D in (-3, -4):
            continue
        stats["fundamental_D"] += 1
        if QO.kronecker_symbol_disc(D, p) != 1:
            continue
        stats["p_split"] += 1
        form = _order2_class(D, p)
        if form is None:
            continue
        stats["class_of_p_order_2"] += 1
        gams = all_elements_of_norm(D, p * p)
        if not gams:
            continue
        gam = gams[0]
        tr = QO.trace(D, *gam)
        for twist in (1, -1):
            order = p * p + 1 - twist * tr
            lp = _large_prime_part(order, smooth=max_cofactor + 1)
            if lp is None or lp[0] > max_cofactor:
                continue
            h, n = lp
            pi = (twist * gam[0], twist * gam[1])
            cands.append(CMQCandidate(D, f"form of p: {form}", twist, order, h, n, n.bit_length(), order % 4 == 0,
                                      pi, _class_norms(form, max_norm)))
    stats["candidates_small_cofactor"] = len(cands)
    for c in cands:
        D, n = c.D, c.n
        # lambda_omega: the root r of omega's polynomial with pi(r) = 1 mod n
        lam_w = next(r for r in QO.omega_eigenvalues(D, n) if QO.eigenvalue(D, *c.pi, r, n) == 1)
        gb = QO.conjugate(D, *c.pi)
        # psi_a for every ideal norm in the class: beta in p with (beta) = a p
        betas = []
        for N in c.ideal_norms_in_class:
            for (a, b) in all_elements_of_norm(D, N * p):
                prod = QO.multiply(D, (a, b), gb)
                if prod[0] % p or prod[1] % p:
                    continue
                lam = QO.eigenvalue(D, a, b, lam_w, n)
                if any(lam in ((x[1]) % n, (-x[1]) % n) for x in betas):
                    continue
                betas.append((N, lam, (a, b)))
        betas.sort()
        best2, best4 = None, None
        pairs = []
        model = models[0]
        for N, lam, el in betas:
            r = _cost_config([1, lam], n, [map_cost(N)], model, ["frobenius"])
            if best2 is None or r["total_M"] < best2["total_M"]:
                best2 = {"degree": N, **r}
        for i in range(len(betas)):
            for k in range(i + 1, len(betas)):
                N1, l1, _ = betas[i]
                N2, l2, _ = betas[k]
                if map_cost(N1) + map_cost(N2) > 400:
                    continue
                lams = [1, l1, l2, l1 * l2 % n]
                costs = [map_cost(N1), map_cost(N2), min(map_cost(N1), map_cost(N2))]
                r = _cost_config(lams, n, costs, model, ["frobenius"] * 3)
                if r["coeff_bits"] > n.bit_length() / 4 + 8:
                    continue                    # dependent pair (e.g. a and its conjugate)
                pairs.append({"degrees": [N1, N2], "coeff_bits": r["coeff_bits"], "total_M": r["total_M"]})
                if best4 is None or r["total_M"] < best4["total_M"]:
                    rw = _cost_config(lams, n, costs, models[1], ["frobenius"] * 3)
                    best4 = {"degrees": [N1, N2], **r, "weierstrass_total_M": rw["total_M"]}
        c.best_2d, c.best_4d = best2 or {}, best4 or {}
        c.pairs_4d = sorted(pairs, key=lambda x: x["total_M"])[:8]
        c.is_fourq = (D == -40 and c.order == FQ.COFACTOR * FQ.N_FOURQ)
        if c.is_fourq:
            c.fourq_crosscheck = _fourq_eigen_crosscheck(betas, n)
        if log:
            log(f"D={D} twist={c.twist} h={c.cofactor} n_bits={c.n_bits} 4D={c.best_4d.get('degrees')} "
                f"{c.best_4d.get('total_M')}")
    return {"p": p, "Dmax": Dmax, "max_cofactor": max_cofactor, "stats": stats,
            "candidates": [asdict(c) for c in cands], "elapsed_s": round(time.time() - t0, 1)}


# ---------------------------------------------------------------------------
# 2-dim (psi alone) and reference rows
# ---------------------------------------------------------------------------

def psi_only_rows(n_bits: int = 246, seed: int = 7) -> list[dict]:
    """psi with psi^2 = eps*d on a prime n of FourQ's size: the 2-dim lattice and its cost."""
    rows = []
    base = 1 << (n_bits - 1)
    for d in (1, 2, 3, 5, 7, 11, 13):
        for eps in (-1, 1):
            if d == 1 and eps == 1:
                continue
            n = nextprime(base + seed)
            while sqrt_mod((eps * d) % n, n) is None:
                n = nextprime(n)
            lam = int(sqrt_mod((eps * d) % n, n))
            cost = 2 * CM.M2_PER_M if d == 1 else map_cost(d)
            row = {"d": d, "psi^2": eps * d, "n_bits": n.bit_length(), "map_cost_M": cost,
                   "label": "GLS (degenerate d = 1)" if d == 1 else f"Smith degree-{d} Q-curve, psi alone"}
            for model in ("twisted_edwards_a=-1_extended_fp2", "weierstrass_jacobian_generic_a_fp2"):
                row[model] = _cost_config([1, lam], n, [cost], model, ["frobenius"])
            rows.append(row)
    return rows


def longa_sica_row(n_bits: int = 246) -> dict:
    """GLV+GLS on a j = 0 curve over F_{p^2} defined over F_p (zeta_3 and psi_GLS, psi^2 = -1): synthetic n."""
    n = nextprime(1 << (n_bits - 1))
    while n % 12 != 1:
        n = nextprime(n)
    i_root = int(sqrt_mod(n - 1, n))
    z3 = int(sqrt_mod(n - 3, n))
    z3 = (-1 + z3) * pow(2, -1, n) % n
    lams = [1, z3, i_root, z3 * i_root % n]
    costs = [1 * CM.M2_PER_M, 2 * CM.M2_PER_M, 2 * CM.M2_PER_M]
    out = {"label": "Longa-Sica GLV+GLS, j = 0 (zeta_3, psi_GLS), synthetic n", "n_bits": n.bit_length(),
           "map_costs_M": costs}
    for model in ("twisted_edwards_a=-1_extended_fp2", "weierstrass_jacobian_generic_a_fp2"):
        out[model] = _cost_config(lams, n, costs, model, ["unit", "frobenius", "frobenius"])
    return out


def fourq_rows() -> dict:
    T, res = FQ.fourq_target()
    lp = next(g["eigenvalue"] for g in T.declared_generators if g["kind"] == "unit")
    ls = next(g["eigenvalue"] for g in T.declared_generators if g["kind"] == "frobenius")
    cphi = next(g["cost_M"] for g in T.declared_generators if g["kind"] == "unit")
    cpsi = next(g["cost_M"] for g in T.declared_generators if g["kind"] == "frobenius")
    n = FQ.N_FOURQ
    lams = [1, lp, ls, lp * ls % n]
    out = {"verified": bool(T.verified), "n_bits": n.bit_length(), "psi_relation": res.psi_relation,
           "phi_relation": res.phi_relation, "measured_map_costs_M": {"phi (deg 5)": cphi, "psi (deg 2)": cpsi},
           "modelled_map_costs_M": {"deg 5": map_cost(5), "deg 2": map_cost(2)}}
    for model in ("twisted_edwards_a=-1_extended_fp2", "weierstrass_jacobian_generic_a_fp2"):
        out[f"{model} measured maps"] = _cost_config(lams, n, [cphi, cpsi, cpsi], model, ["frobenius"] * 3)
        out[f"{model} modelled maps"] = _cost_config(lams, n, [map_cost(5), map_cost(2), map_cost(2)], model,
                                                    ["frobenius"] * 3)
        out[f"{model} psi alone (2-dim), measured map"] = _cost_config([1, ls], n, [cpsi], model, ["frobenius"])
    out["generic_1dim_edwards"] = round(CM.multiscalar_cost(n.bit_length(), [CM.Generator("1", 1, 0.0, "identity")],
                                                          "twisted_edwards_a=-1_extended_fp2").total_M, 1)
    return out


def run(seed: int = 1, Dmax: int = 3000, explicit: bool = True, log=None) -> dict:
    out: dict = {"p": "2^127 - 1", "cost_unit": "F_p multiplications (M), 127-bit p, S = 0.8 M, M2 = 3 M, S2 = 2 M",
                 "map_cost_formula": "c(d) = 3*(sum isogeny_step_cost(ell) + 20) + 6",
                 "map_cost_table": {d: map_cost(d) for d in (2, 3, 5, 7, 11, 13)}}
    t0 = time.time()
    out["fourq"] = fourq_rows()
    out["psi_alone"] = psi_only_rows()
    out["longa_sica"] = longa_sica_row()
    out["cm_sweep"] = cm_sweep(Dmax, log=log)
    if explicit:
        out["explicit"] = [asdict(fourq_w_crosscheck(seed + 1))]
        for d in (2, 3):
            out["explicit"].append(asdict(explicit_qcurve(d, seed=seed + d)))
    out["elapsed_s"] = round(time.time() - t0, 1)
    return out


def markdown(r: dict) -> str:
    E, W = "twisted_edwards_a=-1_extended_fp2", "weierstrass_jacobian_generic_a_fp2"
    fq = r["fourq"]
    L = ["# Q-curves over F_{p^2} against FourQ", "",
         f"Cost unit: {r['cost_unit']}.  Map cost (modelled): {r['map_cost_formula']} -> "
         + ", ".join(f"d={d}: {c:.1f}" for d, c in r["map_cost_table"].items()) + ".", "",
         "## FourQ under the harness model", "",
         f"Verified maps (fourq.py): {fq['psi_relation']}; {fq['phi_relation']}; measured map costs "
         f"{fq['measured_map_costs_M']}.", "",
         "| configuration | coeff bits | total M (Edwards) | total M (Weierstrass) |", "|:--|--:|--:|--:|"]
    for lab, key in (("FourQ 4-dim, measured maps", "measured maps"), ("FourQ 4-dim, modelled maps", "modelled maps"),
                     ("FourQ psi alone (2-dim), measured map", "psi alone (2-dim), measured map")):
        e, w = fq[f"{E} {key}"], fq[f"{W} {key}"]
        L.append(f"| {lab} | {e['coeff_bits']} | {e['total_M']} | {w['total_M']} |")
    L.append(f"| generic 1-dim (no endomorphism), Edwards | {fq['n_bits']} | {fq['generic_1dim_edwards']} | |")
    ls = r["longa_sica"]
    L.append(f"| {ls['label']} | {ls[E]['coeff_bits']} | {ls[E]['total_M']} | {ls[W]['total_M']} |")
    L += ["", "## psi alone (2-dim), every degree", "",
          "| map | psi^2 | map cost M | coeff bits | total M (Edwards) | total M (Weierstrass) |",
          "|:--|--:|--:|--:|--:|--:|"]
    for row in r["psi_alone"]:
        L.append(f"| {row['label']} | {row['psi^2']} | {row['map_cost_M']:.1f} | {row[E]['coeff_bits']} | "
                 f"{row[E]['total_M']} | {row[W]['total_M']} |")
    cs = r["cm_sweep"]
    L += ["", f"## CM Q-curves at p = 2^127 - 1 (|D| <= {cs['Dmax']}, cofactor <= {cs['max_cofactor']})", "",
          f"Funnel: {cs['stats']}.", "",
          "| D | twist | cofactor | n bits | 4 \\| #E | class norms | best 2-dim (deg: M) | best 4-dim degrees | "
          "coeff bits | total M (Edwards) | total M (Weierstrass) | FourQ? |",
          "|--:|--:|--:|--:|:--|:--|:--|:--|--:|--:|--:|:--|"]
    for c in sorted(cs["candidates"], key=lambda c: c["best_4d"].get("total_M", 1e9)):
        b2, b4 = c["best_2d"], c["best_4d"]
        L.append(f"| {c['D']} | {c['twist']} | {c['cofactor']} | {c['n_bits']} | {c['four_divides_order']} | "
                 f"{c['ideal_norms_in_class'][:6]} | {b2.get('degree')}: {b2.get('total_M')} | "
                 f"{b4.get('degrees')} | {b4.get('coeff_bits')} | {b4.get('total_M')} | "
                 f"{b4.get('weierstrass_total_M')} | {'yes' if c['is_fourq'] else ''} |")
    for c in cs["candidates"]:
        if c["is_fourq"]:
            L += ["", f"D = -40 reproduces FourQ (#E = 392 N).  FourQ's verified maps: {c['fourq_crosscheck']}.  "
                  "4-dim pairs on it (degrees: coeff bits, total M Edwards): "
                  + "; ".join(f"{q['degrees']}: {q['coeff_bits']}, {q['total_M']}" for q in c["pairs_4d"])]
    L += ["", "## Explicit maps on points (p = 2^127 - 1)", ""]
    for e in r.get("explicit", []):
        L.append(f"* degree {e['d']}, {e['source']}: psi^2 = {e['psi_sign'] and e['psi_sign'] * e['d']}, "
                 f"#E = {e['order']}, cofactor {e['cofactor']}, l = {e['l'] and e['l'].bit_length()}-bit prime, "
                 f"eigenvalue found: {e['eigenvalue'] is not None}; psi affine ops {e['ops_psi_affine']} "
                 f"(projective-equivalent {e['psi_projective_equivalent_M']} M); {e['note']}")
        for k, v in e["checks"].items():
            L.append(f"  * {k}: {v}")
        if e.get("decomposition"):
            L.append(f"  * decomposition: {e['decomposition']}")
    return "\n".join(L) + "\n"


def main(argv=None) -> int:
    import argparse
    import os
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--dmax", type=int, default=3000)
    ap.add_argument("--no-explicit", action="store_true")
    ap.add_argument("--out-dir", default=None)
    args = ap.parse_args(argv)
    r = run(args.seed, args.dmax, not args.no_explicit, log=print)
    md = markdown(r)
    if args.out_dir:
        os.makedirs(args.out_dir, exist_ok=True)
        with open(os.path.join(args.out_dir, "qcurves.json"), "w") as fh:
            json.dump(r, fh, indent=1, default=str)
            fh.write("\n")
        with open(os.path.join(args.out_dir, "qcurves.md"), "w") as fh:
            fh.write(md)
    print(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
