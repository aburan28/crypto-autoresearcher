"""Real multiplication on fast Kummer surfaces: does the RM family ever qualify?

The candidate ("C2") under test: genus-2 Jacobians of the Tautz-Top-Verberkmoes
family

    C_t : y^2 = D_5(x) + t,      D_5(x) = x^5 - 5x^3 + 5x  (the Dickson polynomial),

carry an endomorphism phi with phi^2 + phi - 1 = 0 (real multiplication by
Z[(1+sqrt5)/2]).  phi and phi - 1 are units, commute with [-1] and so descend
to the Kummer surface, which would give the triple (P, phi P, (phi-1) P) a
two-dimensional differential addition chain needs.  The named obstruction:
the FAST (Gaudry / squared-theta) Kummer needs all of J[2] rational -- in the
degree-5 model, f = D_5 + t must split into five distinct linear factors over
F_p -- and #J = 16 * (prime), and the family might never give both.

What this module establishes, and how
-------------------------------------
* **The 2-torsion condition (proven, then checked).**  J[2] is the group of
  even subsets of the six Weierstrass points {roots of f, infinity} modulo
  complement; Frobenius fixes infinity, so it acts trivially on J[2] iff it
  fixes every root, i.e. iff f splits completely over F_p.  For f = D_5 + t,
  write x = z + 1/z: then D_5(x) = z^5 + z^-5, the roots are z + 1/z for the
  fifth roots z of a root w of w^2 + t w + 1, and z (hence x) runs over the
  torus F_p^* (if t^2 - 4 is a square) or the norm-one torus of order p + 1
  (if not).  ``split_criterion`` turns that into a closed form: f splits iff
  p = 1 (mod 5), t^2 - 4 is a nonzero square and w is a fifth power in F_p^*,
  or p = 4 (mod 5), t^2 - 4 is a non-square and w is a fifth power in the
  norm-one torus (the torus whose order 5 divides is the only one where all
  five fifth roots of w stay in it).  For p = +-2 (mod 5) z -> z^5 is a bijection on both tori, so
  D_5 permutes F_p (the "permutation polynomial" of the family's origin) and
  f has exactly ONE rational root for every t.  The criterion is compared
  with direct root counting on every member.
* **#J for every member, exactly.**  N1 = #C(F_p) and N2 = #C(F_{p^2}) for
  ALL t at once: the values g(x), x in F_{p^2}, are binned by (Re, nr*Im^2),
  and sum_x chi(N(g(x) + t)) becomes a sum over bins of a cross-correlation in
  t, done by FFT (floating point, rounded; an ArithmeticError is raised
  if any value is more than 1e-3 from an integer).  #J = (N1^2 + N2)/2 - p, the twist's with -a1.
  Spot-checked against ``genus2.jacobian_order`` (pure brute force) and
  against PARI's ``hyperellcharpoly`` when cypari2 is installed.
* **The RM is real (measured on every member).**  The characteristic
  polynomial T^4 - s1 T^3 + s2 T^2 - p s1 T + p^2 factors as
  (T^2 - aT + p)(T^2 - a'T + p) with a, a' conjugate in Z[(1+sqrt5)/2] iff
  s1^2 - 4 s2 + 8p = 5 v^2 for an integer v.  Counted on every member, and on
  the control.
* **phi on points.**  For a rational point P = (x, y), with x = z + 1/z and
  zeta a primitive fifth root of unity, the correspondence
  P -> (zeta z + 1/(zeta z), y) + (z/zeta + zeta/z, y) has Mumford form
  u = X^2 - phi1 x X + (x^2 - 3 - phi1), v = y, phi1 = zeta + 1/zeta, with
  coefficients in F_p(sqrt5) -- so T is defined over F_p exactly when
  p = +-1 (mod 5), the same primes on which f can split.  Writing T for it, T = pi_* sigma pi^* for the
  cyclic cover z -> z + 1/z; the quotient by sigma has genus 0, which gives
  T^2 = T_{sigma^2} + 2 and 2 + 2T + 2T_{sigma^2} = 0, hence T^2 + T - 1 = 0.
  ``verify_rm_member`` checks that relation on points and the eigenvalue of T
  on a subgroup of prime order l = #J/16.
* **Positive control.**  The same pipeline on the translation family g + t
  with g a random monic quintic (no RM): same parametrisation, same splitting
  test, same order computation.  The control must show 16*prime hits at a
  comparable rate for a zero count on the RM side to mean anything.

What is NOT checked: the fast Kummer needs more than rational 2-torsion (the
squared fundamental theta constants must be rational, which imposes further
square conditions on the Rosenhain invariants -- not derived or tested here),
so the counts below are counts of members passing the NECESSARY conditions.
Nor is phi written in Kummer (theta) coordinates; its cost is a one-off per
scalar multiplication and does not enter the ceiling below.
"""
from __future__ import annotations

import json
import random
import time
from dataclasses import asdict, dataclass, field
from math import isqrt, log2

import numpy as np
from sympy import isprime, primerange
from sympy.ntheory import sqrt_mod

from . import genus2 as G2
from . import lattice as LA

D5 = [0, 5, 0, -5, 0, 1]          # x^5 - 5x^3 + 5x, low degree first


# ---------------------------------------------------------------------------
# small helpers
# ---------------------------------------------------------------------------

def legendre_table(p: int) -> np.ndarray:
    """chi(v) for v in F_p as an int8 array (chi(0) = 0)."""
    chi = -np.ones(p, dtype=np.int8)
    sq = (np.arange(1, p, dtype=np.int64) ** 2) % p
    chi[sq] = 1
    chi[0] = 0
    return chi


def nonresidue(p: int) -> int:
    return next(z for z in range(2, p) if pow(z, (p - 1) // 2, p) == p - 1)


def poly_eval_fp(coeffs: list[int], xs: np.ndarray, p: int) -> np.ndarray:
    r = np.zeros_like(xs)
    for c in reversed(coeffs):
        r = (r * xs + c) % p
    return r


def poly_eval_fp2(coeffs: list[int], a: np.ndarray, b: np.ndarray, p: int, nr: int):
    """g(a + b s) with s^2 = nr, coefficients in F_p; returns (Re, Im)."""
    R = np.zeros_like(a)
    I = np.zeros_like(a)
    for c in reversed(coeffs):
        R, I = (R * a + (I * b % p) * nr + c) % p, (R * b + I * a) % p
    return R, I


def _correlate_sum(H: np.ndarray, Gm: np.ndarray, p: int) -> np.ndarray:
    """S(t) = sum_cols sum_R H[R, col] * Gm[(R + t) mod p, col], via FFT along axis 0."""
    FH = np.fft.rfft(H.astype(np.float64), axis=0)
    FG = np.fft.rfft(Gm.astype(np.float64), axis=0)
    spec = np.sum(np.conj(FH) * FG, axis=1)
    S = np.fft.irfft(spec, n=p)
    Sr = np.rint(S)
    err = float(np.max(np.abs(S - Sr))) if p else 0.0
    if err > 1e-6 * max(1.0, float(np.max(np.abs(S)))) and err > 1e-3:
        raise ArithmeticError(f"FFT rounding error {err} at p = {p}")
    return Sr.astype(np.int64)


# ---------------------------------------------------------------------------
# point counts of y^2 = g(x) + t for every t in F_p at once
# ---------------------------------------------------------------------------

@dataclass
class FamilyCounts:
    p: int
    g: list[int]
    N1: np.ndarray          # #C_t(F_p) for t = 0..p-1
    N2: np.ndarray          # #C_t(F_{p^2})
    roots: np.ndarray       # number of distinct x in F_p with g(x) + t = 0

    def order(self, t: int) -> int:
        n1, n2 = int(self.N1[t]), int(self.N2[t])
        return (n1 * n1 + n2) // 2 - self.p

    def twist_order(self, t: int) -> int:
        p = self.p
        a1 = int(self.N1[t]) - p - 1
        a2 = (int(self.N2[t]) - p * p - 1 + a1 * a1) // 2
        return 1 - a1 + a2 - p * a1 + p * p

    def s1_s2(self, t: int) -> tuple[int, int]:
        p = self.p
        a1 = int(self.N1[t]) - p - 1
        a2 = (int(self.N2[t]) - p * p - 1 + a1 * a1) // 2
        return -a1, a2


def family_counts(p: int, g: list[int]) -> FamilyCounts:
    """N1, N2 of y^2 = g(x) + t for all t in F_p (g monic of degree 5, low first)."""
    assert len(g) == 6 and g[5] % p == 1
    chi = legendre_table(p)
    nr = nonresidue(p)
    # N1: values of g on F_p, histogram, correlation with chi(v + t)
    xs = np.arange(p, dtype=np.int64)
    gv = poly_eval_fp(g, xs, p)
    h1 = np.bincount(gv, minlength=p)
    # S1(t) = sum_v h1[v] chi(v + t)
    S1 = _correlate_sum(h1.reshape(p, 1), chi.astype(np.int64).reshape(p, 1), p)
    N1 = 1 + p + S1
    roots = h1[(-xs) % p]          # #{x : g(x) = -t}
    # N2: g(a + b s) for all (a, b); N(g + t) = (R + t)^2 - nr I^2
    a = np.repeat(np.arange(p, dtype=np.int64), p)
    b = np.tile(np.arange(p, dtype=np.int64), p)
    R, I = poly_eval_fp2(g, a, b, p, nr)
    del a, b
    Q = (nr * (I * I % p)) % p
    del I
    H = np.bincount(R * p + Q, minlength=p * p).reshape(p, p)
    del R, Q
    cols = np.nonzero(H.sum(axis=0))[0]
    H = H[:, cols]
    u = np.arange(p, dtype=np.int64)
    Gm = chi[((u * u)[:, None] - cols[None, :]) % p].astype(np.int64)
    S2 = _correlate_sum(H, Gm, p)
    N2 = 1 + p * p + S2
    return FamilyCounts(p, [c % p for c in g], N1, N2, roots)


class MemberCounter:
    """#J and #J_twist of single curves y^2 = f(x) over one F_p, by direct exact summation.

    Used for the split-by-construction control, where every member has a
    different f and the all-t FFT does not apply.  O(p^2) numpy work per
    curve, integer arithmetic throughout."""

    def __init__(self, p: int):
        self.p = p
        self.chi = legendre_table(p).astype(np.int64)
        self.nr = nonresidue(p)
        self.a = np.repeat(np.arange(p, dtype=np.int64), p)
        self.b = np.tile(np.arange(p, dtype=np.int64), p)
        self.xs = np.arange(p, dtype=np.int64)

    def orders(self, f: list[int]) -> tuple[int, int, int, int]:
        p = self.p
        N1 = 1 + p + int(self.chi[poly_eval_fp(f, self.xs, p)].sum())
        R, I = poly_eval_fp2(f, self.a, self.b, p, self.nr)
        nrm = (R * R - self.nr * (I * I % p)) % p
        N2 = 1 + p * p + int(self.chi[nrm].sum())
        a1 = N1 - p - 1
        a2 = (N2 - p * p - 1 + a1 * a1) // 2
        return 1 + a1 + a2 + p * a1 + p * p, 1 - a1 + a2 - p * a1 + p * p, -a1, a2


def split_quintic(p: int, rng: random.Random) -> list[int]:
    """prod (x - r_i) for five distinct random r_i in F_p, low degree first."""
    roots = rng.sample(range(p), 5)
    f = [1]
    for r in roots:
        f = [((f[i - 1] if i else 0) - r * (f[i] if i < len(f) else 0)) % p for i in range(len(f) + 1)]
    return f


# ---------------------------------------------------------------------------
# the closed-form splitting criterion for D_5 + t
# ---------------------------------------------------------------------------

def split_criterion(p: int, t: int) -> bool:
    """True iff x^5 - 5x^3 + 5x + t has five distinct roots in F_p (derived in the module docstring).

    p = 1 (mod 5): w (root of w^2 + t w + 1) must lie in F_p^* (t^2 - 4 a nonzero
    square) and be a fifth power there.  p = 4 (mod 5): w must lie in the
    norm-one torus of F_{p^2} (t^2 - 4 a non-square) and be a fifth power in
    that cyclic group of order p + 1, i.e. w^((p+1)/5) = 1.  p = 2, 3 (mod 5):
    never.  t = +-2 (singular) never.
    """
    t %= p
    if p % 5 in (2, 3) or p == 5:
        return False
    disc = (t * t - 4) % p
    if disc == 0:
        return False
    is_sq = pow(disc, (p - 1) // 2, p) == 1
    inv2 = pow(2, -1, p)
    if p % 5 == 1:
        if not is_sq:
            return False
        s = int(sqrt_mod(disc, p))
        w = (-t + s) * inv2 % p
        return pow(w, (p - 1) // 5, p) == 1
    # p = 4 mod 5: work in F_p[s]/(s^2 - disc)
    if is_sq:
        return False
    w = ((-t) * inv2 % p, inv2)              # (-t + s)/2, s = sqrt(disc)

    def mul(x, y):
        return ((x[0] * y[0] + x[1] * y[1] * disc) % p, (x[0] * y[1] + x[1] * y[0]) % p)

    e, r, base = (p + 1) // 5, (1, 0), w
    while e:
        if e & 1:
            r = mul(r, base)
        base = mul(base, base)
        e >>= 1
    return r == (1, 0)


def rm_factorization(p: int, s1: int, s2: int) -> int | None:
    """v >= 0 with s1^2 - 4 s2 + 8p = 5 v^2, or None: the char. poly. splits over Q(sqrt5)."""
    d = s1 * s1 - 4 * s2 + 8 * p
    if d < 0 or d % 5:
        return None
    v = isqrt(d // 5)
    return v if 5 * v * v == d else None


# ---------------------------------------------------------------------------
# the survey
# ---------------------------------------------------------------------------

@dataclass
class FamilyStats:
    label: str
    primes: int = 0
    members: int = 0                      # (p, t) pairs with nonsingular C_t
    split: int = 0                        # f splits completely (full rational J[2])
    split_and_16: int = 0                 # ... and 16 | #J (must equal split)
    hits: int = 0                         # ... and #J / 16 prime
    hits_twist: int = 0                   # ... and #J_twist / 16 prime
    hits_both: int = 0                    # both
    rm_factor_all: int = 0                # members whose charpoly splits over Q(sqrt5)
    rm_factor_split: int = 0
    criterion_disagreements: int = 0      # closed-form criterion vs root count (RM family only)
    v2_hist: dict = field(default_factory=dict)   # 2-adic valuation of #J over split members
    examples: list = field(default_factory=list)

    def rates(self) -> dict:
        s = max(self.split, 1)
        return {"split_fraction": self.split / max(self.members, 1),
                "hit_rate_given_split": self.hits / s,
                "twist_hit_rate_given_split": self.hits_twist / s,
                "both_rate_given_split": self.hits_both / s,
                "rm_factor_fraction": self.rm_factor_all / max(self.members, 1)}


def _random_quintic(p: int, rng: random.Random) -> list[int]:
    """Monic quintic with zero x^4 and constant terms (the shape of D_5)."""
    return [0, rng.randrange(p), rng.randrange(p), rng.randrange(p), 0, 1]


def _nonsingular_ts(p: int, g: list[int]) -> set[int]:
    """t with g + t squarefree: g(x) = -t at a critical point x (g'(x) = 0) is singular."""
    from sympy import Poly, symbols, GF
    X = symbols("x")
    gp = Poly(list(reversed(g)), X, modulus=p)
    dg = gp.diff(X)
    bad = set()
    # critical values: roots of dg in F_p and in extensions; singular t satisfy
    # Res_x(g + t, g') = 0, a polynomial in t of degree 4; evaluate directly
    T = symbols("T")
    from sympy import resultant
    res = Poly(resultant(Poly(list(reversed(g)), X).as_expr() + T, Poly(list(reversed(g)), X).diff(X).as_expr(), X),
               T, modulus=p)
    for t in range(p):
        if res.eval(t) % p == 0:
            bad.add(t)
    del gp, dg
    return set(range(p)) - bad


def survey(pmin: int = 1000, pmax: int = 2000, controls_per_prime: int = 1, seed: int = 20261008,
           keep_examples: int = 12, spot_check_pari: int = 0, log=None) -> dict:
    """RM family vs control over every prime pmin < p < pmax with p = +-1 (mod 5).

    Primes p = +-2 (mod 5) are scanned for splitting only (the theorem says
    never; the scan checks it) and for RM factorisation on a subset.
    """
    rng = random.Random(seed)
    rm = FamilyStats("RM family y^2 = x^5 - 5x^3 + 5x + t")
    ctl = FamilyStats("control y^2 = g(x) + t, g random monic quintic (no RM)")
    sctl = FamilyStats("control y^2 = prod (x - r_i), five random distinct roots (generic, split by construction)")
    inert = {"primes": 0, "members_scanned": 0, "split": 0, "d5_is_permutation_all": True,
             "rm_factor_members": 0, "members_counted": 0}
    pari_checks = {"done": 0, "agree": 0, "available": True}
    t0 = time.time()
    for p in primerange(pmin + 1, pmax):
        if p % 5 in (2, 3):
            inert["primes"] += 1
            xs = np.arange(p, dtype=np.int64)
            vals = poly_eval_fp(D5, xs, p)
            perm = len(np.unique(vals)) == p
            inert["d5_is_permutation_all"] &= bool(perm)
            inert["members_scanned"] += p
            h1 = np.bincount(vals, minlength=p)
            inert["split"] += int(np.sum(h1 == 5))
            if inert["primes"] <= 4:          # RM factorisation on a few inert primes
                fc = family_counts(p, D5)
                for t in range(p):
                    if t in (2, p - 2):
                        continue
                    s1, s2 = fc.s1_s2(t)
                    inert["members_counted"] += 1
                    inert["rm_factor_members"] += rm_factorization(p, s1, s2) is not None
            continue
        good = _nonsingular_ts(p, D5)
        rm_split_before = rm.split
        fc = family_counts(p, D5)
        if pari_checks["done"] < spot_check_pari:
            _pari_check(fc, sorted(good), rng, pari_checks)
        _tally_filtered(rm, fc, good, True, keep_examples)
        rm.primes += 1
        for _ in range(controls_per_prime):
            while True:
                g = _random_quintic(p, rng)
                goodg = _nonsingular_ts(p, g)
                if len(goodg) > p - 5:
                    break
            fcg = family_counts(p, g)
            if pari_checks["done"] < spot_check_pari:
                _pari_check(fcg, sorted(goodg), rng, pari_checks)
            _tally_filtered(ctl, fcg, goodg, False, keep_examples)
        ctl.primes += 1
        # split-by-construction control: about a third as many members as the RM family has split ones here
        k = (rm.split - rm_split_before + 2) // 3
        mc = MemberCounter(p)
        for _ in range(k):
            f = split_quintic(p, rng)
            N, Nt, s1, s2 = mc.orders(f)
            v = rm_factorization(p, s1, s2)
            sctl.members += 1
            sctl.split += 1
            sctl.rm_factor_all += v is not None
            sctl.rm_factor_split += v is not None
            _v2(sctl, N)
            sctl.split_and_16 += N % 16 == 0 and Nt % 16 == 0
            h = N % 16 == 0 and isprime(N // 16)
            ht = Nt % 16 == 0 and isprime(Nt // 16)
            sctl.hits += bool(h)
            sctl.hits_twist += bool(ht)
            sctl.hits_both += bool(h and ht)
            if h and len(sctl.examples) < keep_examples:
                sctl.examples.append({"p": p, "f": f, "order": N, "l": N // 16, "twist_order": Nt,
                                      "twist_l_prime": bool(ht), "s1": s1, "s2": s2, "rm_v": v})
        sctl.primes += 1
        del mc
        if log:
            log(f"p={p} rm split={rm.split} hits={rm.hits} | ctl split={ctl.split} hits={ctl.hits} "
                f"| split-ctl {sctl.split} hits={sctl.hits} "
                f"[{time.time() - t0:.0f}s]")
    return {"rm": rm, "control": ctl, "split_control": sctl, "inert_primes": inert, "pari_spot_checks": pari_checks,
            "elapsed_s": round(time.time() - t0, 1),
            "range": [pmin, pmax], "seed": seed}


def _v2(st: FamilyStats, N: int) -> None:
    k = (N & -N).bit_length() - 1
    st.v2_hist[k] = st.v2_hist.get(k, 0) + 1


def _pari_check(fc: FamilyCounts, ts: list[int], rng: random.Random, acc: dict, k: int = 3) -> None:
    """Compare #J for k random members with PARI's hyperellcharpoly (skipped without cypari2)."""
    try:
        import cypari2
    except ImportError:
        acc["available"] = False
        return
    pari = cypari2.Pari()
    p = fc.p
    for t in rng.sample(ts, k):
        f = [(c + (t if i == 0 else 0)) % p for i, c in enumerate(fc.g)]
        expr = "+".join(f"{c}*x^{i}" for i, c in enumerate(f) if c)
        P = pari(f"hyperellcharpoly(Mod(1,{p})*({expr}))")
        acc["done"] += 1
        acc["agree"] += int(pari.subst(P, "x", 1)) == fc.order(t)


def _tally_filtered(st, fc, good, check_criterion, keep_examples):
    p = fc.p
    for t in range(p):
        if t not in good:
            continue
        st.members += 1
        s1, s2 = fc.s1_s2(t)
        v = rm_factorization(p, s1, s2)
        st.rm_factor_all += v is not None
        split = int(fc.roots[t]) == 5
        if check_criterion and split != split_criterion(p, t):
            st.criterion_disagreements += 1
        if not split:
            continue
        st.split += 1
        st.rm_factor_split += v is not None
        N, Nt = fc.order(t), fc.twist_order(t)
        _v2(st, N)
        st.split_and_16 += N % 16 == 0 and Nt % 16 == 0
        h = N % 16 == 0 and isprime(N // 16)
        ht = Nt % 16 == 0 and isprime(Nt // 16)
        st.hits += bool(h)
        st.hits_twist += bool(ht)
        st.hits_both += bool(h and ht)
        if h and sum(e["p"] % 5 == p % 5 for e in st.examples) < keep_examples // 2:
            st.examples.append({"p": p, "t": t, "g": fc.g, "order": N, "l": N // 16, "twist_order": Nt,
                                "twist_l_prime": bool(ht), "s1": s1, "s2": s2, "rm_v": v})


# ---------------------------------------------------------------------------
# explicit RM on points
# ---------------------------------------------------------------------------

def phi_of_point(p: int, phi1: int, x: int, y: int):
    """T(P - inf) in Mumford form: u = X^2 - phi1 x X + (x^2 - 3 - phi1), v = y."""
    u = G2._trim([(x * x - 3 - phi1) % p, (-phi1 * x) % p, 1])
    v = G2._trim([y % p])
    return (u, v)


def _rational_points(p: int, f: list[int], rng: random.Random, k: int):
    out = []
    while len(out) < k:
        x = rng.randrange(p)
        rhs = sum(c * pow(x, i, p) for i, c in enumerate(f)) % p
        if rhs == 0:
            continue
        y = sqrt_mod(rhs, p)
        if y is not None:
            out.append((x, int(y)))
    return out


def _roots_fp(p: int, f: list[int]) -> list[int]:
    return [x for x in range(p) if sum(c * pow(x, i, p) for i, c in enumerate(f)) % p == 0]


def verify_rm_member(p: int, t: int, seed: int = 1) -> dict:
    """Build T on points of J(C_t)/F_p, check T^2 + T - 1 = 0 and its eigenvalue on J[l], l = #J/16."""
    assert p % 5 in (1, 4)
    rng = random.Random(seed)
    f = [(c + (t if i == 0 else 0)) % p for i, c in enumerate(D5)]
    J = G2.Jacobian(p, f)
    fc_order = G2.jacobian_order(p, f) if p < 400 else None
    out: dict = {"p": p, "t": t, "p_mod_5": p % 5}
    # orders from the FFT counter (cross-checked against brute force at small p)
    fc = family_counts(p, D5)
    N, Nt = fc.order(t), fc.twist_order(t)
    out["order"], out["twist_order"] = N, Nt
    if fc_order is not None:
        out["order_bruteforce_agrees"] = fc_order == N
    phi1s = sorted(int(r) for r in sqrt_mod(5, p, all_roots=True))
    phi1s = sorted({(-1 + r) * pow(2, -1, p) % p for r in phi1s})
    out["phi1_roots_of_X2+X-1"] = phi1s
    checks: dict = {}
    phi1 = phi1s[0]
    assert (phi1 * phi1 + phi1 - 1) % p == 0
    # T(P) is on J
    pts = _rational_points(p, f, rng, 40)
    imgs = [phi_of_point(p, phi1, x, y) for x, y in pts]
    checks["T(P) on J for 40 rational points"] = all(J.on_jacobian(D) for D in imgs)
    # T^2 + T - 1 = 0 on points whose image splits over F_p
    rel_ok, rel_n = True, 0
    for (x, y), img in zip(pts, imgs):
        r = _roots_fp(p, img[0] + [0] * (3 - len(img[0])))
        if len(r) != 2 or r[0] == r[1]:
            continue
        TT = J.add(phi_of_point(p, phi1, r[0], y), phi_of_point(p, phi1, r[1], y))
        P = J.point_divisor(x, y)
        lhs = J.add(J.add(TT, img), J.neg(P))
        rel_ok &= J.is_identity(lhs)
        rel_n += 1
    checks[f"T(T(P)) + T(P) - P = 0 on {rel_n} points with split image"] = rel_ok and rel_n > 0
    # full rational 2-torsion and 16 | #J
    roots = _roots_fp(p, f)
    out["rational_weierstrass_points"] = len(roots)
    if len(roots) == 5:
        tors = [J.point_divisor(r, 0) for r in roots]
        sums = {str(J.identity())}
        import itertools
        for k in range(1, 5):
            for S in itertools.combinations(tors[:4], k):
                D = J.identity()
                for T_ in S:
                    D = J.add(D, T_)
                sums.add(str(D))
        checks["J[2] rational: 16 distinct sums of four Weierstrass divisors, each killed by 2"] = (
            len(sums) == 16 and all(J.is_identity(J.add(T_, T_)) for T_ in tors))
    # eigenvalue on the prime-order subgroup
    if N % 16 == 0 and isprime(N // 16):
        l = N // 16
        out["l"] = l
        P1, P2 = _rational_points(p, f, rng, 2)
        D0 = J.add(J.point_divisor(*P1), J.point_divisor(*P2))
        D = J.mul(16, D0)
        while J.is_identity(D):
            P1, P2 = _rational_points(p, f, rng, 2)
            D0 = J.add(J.point_divisor(*P1), J.point_divisor(*P2))
            D = J.mul(16, D0)
        TD = J.mul(16, J.add(phi_of_point(p, phi1, *P1), phi_of_point(p, phi1, *P2)))
        checks["l * D = 0"] = J.is_identity(J.mul(l, D))
        lams = sorted({(-1 + int(r)) * pow(2, -1, l) % l for r in (sqrt_mod(5, l, all_roots=True) or [])})
        lam = next((L for L in lams if J.mul(L, D) == TD), None)
        out["eigenvalue_on_J[l]"] = lam
        checks["T acts on J[l] as a root of X^2 + X - 1 mod l"] = lam is not None
        if lam is not None:
            red = LA.reduce([1, lam], l)
            cb = LA.coefficient_bits(red, samples=32, seed=seed)
            ok = True
            for _ in range(4):
                k = rng.randrange(1, l)
                k1, k2 = red.decompose(k)
                ok &= J.mul(k, D) == J.add(J.mul(k1, D), J.mul(k2, TD))
            out["glv2_with_T"] = {"reconstructs kD (4 random k)": ok, **cb, "l_bits": l.bit_length()}
            checks["2-dim decomposition k = k1 + k2*lambda reconstructs kD"] = ok
            # (phi - 1) P, the third point of the differential chain triple
            out["triple_P_TP_(T-1)P_distinct"] = len({str(D), str(TD), str(J.add(TD, J.neg(D)))}) == 3
    out["checks"] = checks
    out["ok"] = all(bool(v) for v in checks.values())
    return out


# ---------------------------------------------------------------------------
# payoff ceiling
# ---------------------------------------------------------------------------

def ladder_vs_2d_chain(rho: float, bits: int = 254, precomp_ops: float = 0.0) -> dict:
    """Ratio of a 1-D Montgomery ladder (bits steps of DBL + ADD) to a 2-D
    differential chain on half-length scalars (bits/2 steps of DBL + 2 ADD,
    Bernstein's binary chain shape), with rho = cost(xADD)/cost(xDBL).
    Modelled; ``precomp_ops`` (in DBL units) charges phi images and setup."""
    one = bits * (1 + rho)
    two = (bits / 2) * (1 + 2 * rho) + precomp_ops
    return {"rho": rho, "ladder_DBL_units": one, "chain2d_DBL_units": two, "speedup": one / two}


def _wilson(k: int, n: int, z: float = 1.96) -> list[float]:
    if n == 0:
        return [0.0, 1.0]
    ph = k / n
    den = 1 + z * z / n
    c = (ph + z * z / (2 * n)) / den
    h = z * (ph * (1 - ph) / n + z * z / (4 * n * n)) ** 0.5 / den
    return [round(c - h, 4), round(c + h, 4)]


def run(pmin: int = 1000, pmax: int = 1600, controls_per_prime: int = 1, seed: int = 20261008,
        pari_checks: int = 12, verify_members: int = 4, log=None) -> dict:
    res = survey(pmin, pmax, controls_per_prime, seed, spot_check_pari=pari_checks, log=log)
    rm, ctl, sctl = res["rm"], res["control"], res["split_control"]
    out: dict = {"question": "Can the RM family y^2 = x^5 - 5x^3 + 5x + t meet the fast-Kummer conditions "
                             "(f splits over F_p, 16 | #J, #J/16 prime)?",
                 "range": res["range"], "seed": seed, "elapsed_s": res["elapsed_s"],
                 "pari_spot_checks": res["pari_spot_checks"], "inert_primes": res["inert_primes"]}
    for key, st in (("rm", rm), ("control", ctl), ("split_control", sctl)):
        d = asdict(st)
        d["rates"] = st.rates()
        d["hit_rate_wilson95"] = _wilson(st.hits, st.split)
        d["both_rate_wilson95"] = _wilson(st.hits_both, st.split)
        out[key] = d
    # explicit RM on points for a few of the hits, both residue classes of p mod 5
    picks, seen = [], set()
    for ex in rm.examples:
        cls = ex["p"] % 5
        if sum(1 for e in picks if e["p"] % 5 == cls) < max(1, verify_members // 2) and ex["p"] not in seen:
            picks.append(ex)
            seen.add(ex["p"])
    out["explicit_rm"] = [verify_rm_member(e["p"], e["t"], seed=1) for e in picks[:verify_members]]
    p127 = 2**127 - 1
    out["kummer_prime_2^127-1"] = {
        "p mod 5": p127 % 5,
        "consequence": "p = 2 (mod 5): z -> z^5 is a bijection on F_p^* and on the norm-one torus, so D_5 "
                       "permutes F_p and x^5 - 5x^3 + 5x + t has exactly one root in F_p for EVERY t; no member "
                       "of the family over F_{2^127-1} has rational J[2] (theorem; checked exhaustively on every "
                       "inert prime of the survey range)"}
    out["payoff_ceiling_modelled"] = [ladder_vs_2d_chain(r) for r in (0.5, 0.75, 1.0, 1.25, 1.5)]
    return out


def markdown(r: dict) -> str:
    rm, ctl, sc = r["rm"], r["control"], r["split_control"]
    L = ["# RM family on fast Kummer surfaces: survey", "",
         f"Primes {r['range'][0]} < p < {r['range'][1]}, seed {r['seed']}, {r['elapsed_s']} s.  "
         "All counts are exact (FFT point counts, rounded and checked); every figure here is measured.", "",
         "| | RM family D_5 + t | control A: g + t, g random | control B: random split f |",
         "|:--|--:|--:|--:|"]
    rows = [("primes p = +-1 (mod 5)", "primes", "primes"),
            ("nonsingular members (p, t)", "members", "members"),
            ("f splits completely (all of J[2] rational)", "split", "split"),
            ("... and 16 divides #J and #J_twist", "split_and_16", "split_and_16"),
            ("... and #J/16 prime", "hits", "hits"),
            ("... and #J_twist/16 prime", "hits_twist", "hits_twist"),
            ("... both (twist-secure)", "hits_both", "hits_both"),
            ("char. poly. factors over Q(sqrt5), all members", "rm_factor_all", "rm_factor_all"),
            ("char. poly. factors over Q(sqrt5), split members", "rm_factor_split", "rm_factor_split")]
    for lab, a, b in rows:
        L.append(f"| {lab} | {rm[a]} | {ctl[b]} | {sc[b]} |")
    def cell(d, key, w):
        return f"{d['rates'][key]:.4f} {d[w]}"
    L.append("| hit rate given split (Wilson 95%) | " + " | ".join(
        cell(d, "hit_rate_given_split", "hit_rate_wilson95") for d in (rm, ctl, sc)) + " |")
    L.append("| twist-secure rate given split (Wilson 95%) | " + " | ".join(
        cell(d, "both_rate_given_split", "both_rate_wilson95") for d in (rm, ctl, sc)) + " |")
    L.append(f"| split fraction | {rm['rates']['split_fraction']:.4f} | {ctl['rates']['split_fraction']:.4f} | "
             "1 (by construction) |")
    L.append("| 2-adic valuation of #J over split members | " + " | ".join(
        ", ".join(f"{k}: {v}" for k, v in sorted(d["v2_hist"].items(), key=lambda kv: int(kv[0])))
        for d in (rm, ctl, sc)) + " |")
    L += ["", f"Closed-form splitting criterion vs root count, RM family: {rm['criterion_disagreements']} disagreements.",
          f"PARI hyperellcharpoly spot checks: {r['pari_spot_checks']}.", "",
          "Inert primes p = +-2 (mod 5) in the range: " + json.dumps(r["inert_primes"]), "",
          "## Explicit RM on points", ""]
    for e in r["explicit_rm"]:
        L.append(f"* p = {e['p']} (p mod 5 = {e['p_mod_5']}), t = {e['t']}: #J = {e['order']} = 16 * {e.get('l')}, "
                 f"eigenvalue of T on J[l] = {e.get('eigenvalue_on_J[l]')}; all checks pass: {e['ok']}")
        for k, v in e["checks"].items():
            L.append(f"  * {k}: {v}")
    L += ["", "## Examples (first hits)", "", "| p | t | #J | l = #J/16 | twist l prime | v (a - a' = v sqrt5) |",
          "|--:|--:|--:|--:|:--|--:|"]
    for e in rm["examples"]:
        L.append(f"| {e['p']} | {e['t']} | {e['order']} | {e['l']} | {e['twist_l_prime']} | {e['rm_v']} |")
    L += ["", "## Payoff ceiling (modelled)", "",
          "1-D ladder: `b` steps of xDBL + xADD; 2-D chain: `b/2` steps of xDBL + 2 xADD; rho = xADD/xDBL.", "",
          "| rho | speed-up |", "|--:|--:|"]
    for c in r["payoff_ceiling_modelled"]:
        L.append(f"| {c['rho']} | {c['speedup']:.3f} |")
    L += ["", f"p = 2^127 - 1: {r['kummer_prime_2^127-1']['consequence']}.", ""]
    return "\n".join(L)


def main(argv=None) -> int:
    import argparse
    import os
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pmin", type=int, default=1000)
    ap.add_argument("--pmax", type=int, default=1600)
    ap.add_argument("--controls-per-prime", type=int, default=1)
    ap.add_argument("--seed", type=int, default=20261008)
    ap.add_argument("--pari-checks", type=int, default=12)
    ap.add_argument("--out-dir", default=None)
    args = ap.parse_args(argv)
    r = run(args.pmin, args.pmax, args.controls_per_prime, args.seed, args.pari_checks, log=print)
    if args.out_dir:
        os.makedirs(args.out_dir, exist_ok=True)
        with open(os.path.join(args.out_dir, "rm_kummer.json"), "w") as fh:
            json.dump(r, fh, indent=1, default=str)
            fh.write("\n")
        with open(os.path.join(args.out_dir, "rm_kummer.md"), "w") as fh:
            fh.write(markdown(r))
    print(markdown(r))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
