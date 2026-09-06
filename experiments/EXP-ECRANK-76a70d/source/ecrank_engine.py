#!/usr/bin/env python3
"""
EXP-ECRANK-76a70d -- delta-multiplier engine, core module.

GOAL-ECRANK-002 / RQ-ECRANK-27dcc5 / BATCH-07e367 / TASK-20260906-908f6b.
Executor implementation of the FROZEN approved contract
experiments/EXP-ECRANK-76a70d/specification.yaml (version 1, protocol bytes
sha256 bcff5ced4c31468e3e09b49b7197b793888775f4df0d63074bad6c3905044b8f,
approved by DEC-20260905-2d466e). This module implements; it interprets
nothing and changes no status.

PROVENANCE OF COMMITTED PIECES (never an edit to a committed file; D4 rule)
--------------------------------------------------------------------------
* polysqrt_trunc / mestre_polys / pmul / psub / peval / prod_linear / pshift /
  quartic_reduction / quartic_point_to_cubic / cubic_to_weierstrass /
  verify_on_curve / disc_from_ainv are VERBATIM copies of the pure-Fraction
  functions of coordination/goals/GOAL-ECRANK-002/batches/BATCH-e0caa5/tasks/
  TASK-20260822-a7a9e8/src/construct_highrank.py (the module itself cannot be
  imported: it imports cypari at top level; the contract declares stdlib only).
  Copy fidelity is pinned by sha256 of the source file in every run manifest
  and behaviorally re-verified by the run-1 smoke self-test on the committed
  highrank_pool.json fixtures (certified totals 7 and 9) and the contract's
  named degenerate fixture A = (+-1,+-3,+-5,+-7) (constant s = 4096).
* The exact F_l-reduction within-class certifier is
  coordination/goals/GOAL-ECQ-002/batches/BATCH-8b08ef/tasks/
  TASK-20260823-827765/scripts/exact_certify.py (IDEA-20260829-d53906's
  design; RUN-ECQ-f5af06-v2-A-certify measurement), imported BYTE-IDENTICAL
  (sha256 1bc7c05954fdf9531c41eb942e91f918e401098971b2211501a9628ae011ea8e
  re-checked at import; import fails loudly on drift). Run UNCHANGED.
* The coset enumeration re-implements the committed algorithm of
  experiments/EXP-ECRANK-e1e30e/source/twist_family.py subspaces() /
  affine_subspaces() / class_value() (RREF-pivot enumeration, min-mask coset
  representatives) stdlib-pure, provenance-noted; counts re-verified by the
  smoke self-test against the committed enumeration figures (11,811 direction
  subspaces, 188,976 affine subspaces, EV-ECRANK-6695dc).

IMPLEMENTATION CHOICES (IC-n) -- the contract fixes the protocol; these are
the executor's documented choices where the protocol leaves mechanics open.
They are recorded here and in every run manifest; none alters a frozen field.

IC-1 COUNTED-OPS CONVENTION. The budget authority is the counted exact-op
  counter: every Fraction arithmetic operation (+,-,*,/,** incl. reflected),
  every exact integer square/power test (math.isqrt, integer perfect-power
  checks), and every modular exponentiation (pow with modulus, used by the
  F_p point counting and Legendre symbols) increments the counter by 1.
  Plain integer +,-,* inside hot integer scans are counted where they occur
  in counted helper functions (per-u scan tests count 1 op per test point).
  RNG calls (integer PRNG) are NOT exact rational ops and are not counted;
  they are deterministic and wall-tracked. Checkpoint every 10^7 counted ops
  (contract stopping_rules); per-run cap 1.0e8 counted ops; per-run wall cap
  7200 s; exhaustion is reported as exhaustion, inert in both directions.

IC-2 DRAW MECHANICS / H CELLS. Each b-tuple gets exactly 8 fibration draws
  (contract counted_ops_note "<= 8 fibration draws"). Draw t fixes a seeded
  5-subset S of the n r-coordinates and draws them as rationals of height
  <= H_MAX = 10^4 (IC-3); the remaining n-5 coordinates are solved exactly
  (IC-4). A found instance is classified by its ACTUAL full r-height
  h = max_i max(|num_i|, den_i) into the nested cumulative cells
  H in {10^2, 10^3, 10^4}: N(n, H) = # distinct-minimal-model nonsingular
  in-box instances with h <= H, computed over the FULL pre-registered sample
  at every H level (stopping rule "the full 10^4 sample runs at every H
  level"). Frozen-box membership requires h <= 10^4 for ALL r_i (contract
  box "r-height <= 10^4"); finds with h > 10^4 (solved coordinates escaping
  the box) are recorded as found_out_of_box observations and excluded from
  all counts and from the success criterion -- the frozen box, not an
  adaptive widening. Height sub-boxes are nested and deterministic; no RNG
  consumes H (seeds_note).

IC-3 RATIONAL DRAW. One drawn r-coordinate = sign * num/den reduced:
  sign = rng.choice([1,-1]); num = rng.randint(1, H_MAX); den =
  rng.randint(1, H_MAX); r = Fraction(sign*num, den) reduced by gcd.
  Nonzero by construction (r_i != 0 required by the C4 filter). No rejection
  loops; the RNG call sequence is fixed per draw (1 choice + 2 randint per
  fixed coordinate).

IC-4 FIBRATION SOLVE. gamma[m][i] = c[m][i] * d_i where c[1..n-5] is an
  exact reduced basis of ker(Vandermonde(b)) (the n-5 linear relations of
  W(b); M3). Per draw: K_m = -sum_{i in S} gamma[m][i] * r_i^2; solve the
  (n-5)x(n-5) exact linear system gamma[:,T] * y = K for y_l = r_l^2
  (Fraction Gauss-Jordan). Singular system -> draw fails
  ('singular_fibration'). Each y_l must be a NONZERO POSITIVE rational
  square (numerator and denominator perfect squares, exact isqrt); on
  success the Bezout candidates are the 2^(n-5) sign combinations of
  (+-sqrt(y_l)) -- all rational, all yielding the SAME s (s depends on y
  only); the canonical positive-root representative is recorded and the
  sign symmetry is noted. s is then the unique quartic interpolant of
  s(b_i) = d_i * r_i^2 (Lagrange, exact; trailing coefficients above
  degree 4 must vanish identically -- asserted, which is exactly the
  ellipticity condition (d_i r_i^2) in W(b)); the M2 identity is
  cross-checked exactly via delta*g^2 == s (mod p) with g the Lagrange
  interpolant of the r_i and delta the Lagrange interpolant of the d_i.

IC-5 CLASS PATTERNS AND COSETS. Per arm: rng = random.Random(seed); the
  eligible coset list (all affine k=3 subspaces of F_2^7 over the committed
  support whose 3-dim direction space V contains the -1 mask; sorted
  canonically) is drawn with rng.sample(eligible, 3) -> 3 streams. Each
  stream gets its own RNG: random.Random(rng.getrandbits(64)) (derived from
  the arm seed; separate seeded b-streams per C6), and an equal split of the
  sample (remainder to earlier streams). Per b-tuple: b = (0, 1) + a seeded
  sample of n-2 distinct integers from [-20,20]\\{0,1} in sampled order (no
  adaptive reordering). Class pattern (from the stream's coset; the 8 class
  values form 4 sign-pairs {x,-x} because -1 in V): n=8 -> 2 seeded sign-
  pairs {d,-d},{e,-e} (4 classes x 2 points); n=6 -> 1 seeded sign-pair plus
  1 seeded extra class outside it (3 classes x 2); n=10 -> 2 seeded sign-
  pairs plus 1 seeded extra outside them (5 classes: 4 x 2 + 1 x 2). The
  pattern multiset is position-shuffled with the stream RNG. Pair patterns
  guarantee mixed signs (real solvability per the eligibility rationale).
  The Kummer field is K_V = Q(sqrt v : v in V) of the DIRECTION space
  (3-dim, contains -1): [K_V:Q] = 8 certified by the 7 exact integer square
  tests on V's nontrivial elements, for every arm and every pattern; the
  twists of the base E0 (the d_1-twist, d_1 = first populated class in
  sorted order) are indexed by e_i = squarefree_part(d_i * d_1) in V
  (post-XOR-fix transport semantics: squarefree of the product, never the
  raw product or mask XOR).

IC-6 KNOWN-FALSE CONTROL BRANCH. At d = (1..1) the engine's solution branch
  is Mestre's closed form (contract M2: "at d = (1..1) the system contains
  Mestre's trunc-sqrt whenever n <= 10"): delta == 1, g = polysqrt_trunc(p,
  n/2), s = g^2 - p (== delta*g^2 mod p), r_i = g(b_i). The control run
  applies the IDENTICAL degeneracy filter and IDENTICAL certification
  pipeline and reports the certified total; the contract fixes the expected
  totals (7 at n=8, 9 at n=10). Control sample count (5 b-tuples per n) is
  an implementation choice; the contract names no count.

IC-7 PLANTED SYNTHETIC CONTROL (C5/IV-2). 3 planted n=8-shaped instances.
  The subspace is WRITTEN DOWN FROM the planted solutions: relations
  rel_m: -alpha_m^2 * u_{m-1} + u_{m+4} = 0 (m = 1,2,3), alpha_m seeded in
  {1,2,3}; i.e. gamma rows with exactly two nonzero entries; d = (1..1)
  (synthetic). Square-pattern locus: u_{m+4} = alpha_m^2 u_{m-1} -- every
  draw whose fixed/solved split is a transversal of the 3 coupled pairs
  {m-1, m+4} with coordinates 3,4 fixed succeeds with ALL solved
  coordinates automatic nonzero rational squares; the IDENTICAL solve /
  squareness-test / classification / count-vs-H metric code runs on it.
  The planted draw stream embeds the known solutions: draw t (t = 1..T,
  T = 12000) makes the IDENTICAL rng calls (sign choices, subset draw) but
  plants magnitudes r_i = (t + i) for the fixed coordinates, so every found
  point has r-height ~= alpha_max * t -- a known, linear-in-t height
  schedule giving planted growth exponent +1 in box height H (counts ~ H /
  (7 * alpha_max) after the ~1/7 transversal success rate). Recovery check:
  per-decade ratios of cumulative counts must lie in [5, 20] (planted +1
  "within a factor of 2 per decade") and the log-log slope within
  log10(2) of +1. Seeding: random.Random(760708) fresh stream (the declared
  arm-B seed; NO new seed invented, no seed adjusted).

IC-8 DISTINCT-MINIMAL-MODEL DEDUP. Two found instances are the same model
  iff their associated elliptic curves are Q-isomorphic (two Q-curves share
  a minimal model iff Q-isomorphic; affine images x |-> alpha*x + beta of
  the quartic coordinate give Q-isomorphic curves and are so identified).
  Canonical key: the base curve E0 (class-d_1 twist) put in short Weierstrass
  form y^2 = x^3 + A x + B over Q (exact Fractions), reduced by weighted
  scaling (A,B) ~ (u^4 A, u^6 B): A,B cleared to integers with the unique
  minimal-height representative extracted by exact 4th/6th-power stripping;
  pairwise isomorphism cross-check by exact tests (A2/A1 a rational 4th
  power, B2/B1 a rational 6th power, (A2/A1)^3 == (B2/B1)^2, common root
  consistency), with j-invariant as exact pre-filter. PARI ellminimalmodel
  is NOT used (contract declares stdlib only for the pipeline); the
  canonical short form is an exact complete invariant of the Q-isomorphism
  class, which is what "distinct minimal models" counts (O-08).

IC-9 CERTIFICATION ARCHITECTURE (zero descent; IV-6). Base E0 := the
  d_1-twist model d_1*w^2 = s(u) (elliptic over Q: cubic if deg s = 3; if
  deg s = 4 it carries the Q-point (b_1, r_1) since e_1 = 1). Per populated
  class value d (n_d forced points): e = sf(d*d_1), g^2 = d*d_1/e (exact
  isqrt); the twist model m*w^2 = s(u), m = e*d_1, carries the class points
  (b_i, r_i/g) exactly (transport identity m*(r_i/g)^2 = s(b_i) re-checked
  exactly, IV-5). Per-class integral Weierstrass model: deg s = 3 -> exact
  integer scaling to [0,a2,0,a4,a6]; deg s = 4 -> committed quartic_reduction
  with base point the class's first point + quartic_point_to_cubic for the
  others + cubic_to_weierstrass (built-in exact on-curve rechecks). Per-class
  certification: exact_certify.certify(model, class points) (imported
  unchanged; includes exact on-curve, Mazur m=1..12 non-torsion, exact
  torsion bound, F_l stacked-matrix independence). certified_e :=
  certified_rank_lower_bound. Mazur witnesses m*P (m=1..12) recorded per
  point on the class model. CERTIFICATE-KIND SPLIT: eigenspace units =
  sum_e min(1, certified_e) (cross-class Z-independence by the committed
  Galois-eigenspace argument, verify_certificate.py's exact algebra, no
  numerics); F_l within-class units = sum_e max(0, certified_e - 1);
  certified k=3 total = sum_e certified_e = rank E0(K_V) lower bound,
  [K_V:Q] = 8 (7 Kummer square tests recorded). c_e := n_e - certified_e
  (HEUR-2 measurement; a certifier shortfall is reported as measured, never
  interpreted). Verifier verdicts must carry zero errors; any rejection
  fires IV-5 and invalidates the run (reported, not repaired silently).
  Numerical regulator cross-check (optional, NEVER the certificate, IV-6):
  only if a certified instance exists, via cypari ellheightmatrix, recorded
  as floating-point cross-check data outside the certificate; descent_calls
  = 0 and pari_ellrank_calls = 0 everywhere.

IC-10 LOCAL SOLVABILITY (arm A only; P0/F2). For every sampled (b, pattern)
  the single diagonal form sum_i gamma_i x_i^2 = 0 (integer-scaled gamma) is
  checked at the real place (mixed signs -> solvable; all-same-sign ->
  MEASURED real obstruction recorded) and at every prime p <= 100:
  constructive witness search -- a pair (i,j) with (-gamma_i*gamma_j | p) =
  1 yields an explicit nonsingular F_p point (Hensel-liftable) ->
  'solvable_constructive'; if no pair qualifies and all gamma_i lie in one
  square class mod p with (-1|p) = -1, an explicit 3-coordinate witness is
  constructed via a^2 + b^2 = -1 (sums of two squares are surjective on F_p
  for p = 3 mod 4) -> 'solvable_constructive'; otherwise
  'no_constructive_witness' is recorded -- NEVER as an obstruction (an
  obstruction claim requires proved insolubility, which is never computed;
  the general isotropy of diagonal forms in >= 5 variables over Q_p is a
  RECALLED pointer per rule 9, noted, not relied on as evidence). F2 fires
  only on the measured real-place obstruction or would require a proved
  p-insolubility, which this pipeline never asserts.

IC-11 AUGMENTATION SCAN / NULL OBJECTS (run 6, seed 760711). Best
  constructed instance := highest certified k=3 total among in-box
  nonsingular instances (arm C preferred per the pre-declared fallback "n=10
  if found, else the best n=8 instance"; ties -> lower height(s) -> earlier
  in seeded order). Scan box u = num/den, |num| <= 10^3, 1 <= den <= 20,
  gcd = 1; per class d of the instance's coset (all 8): exact integer test
  s(u)/d a rational square (denominator-cleared perfect-square test, then
  exact Fraction re-verification). Null objects: 8 seeded random quartics,
  degree in {3,4}, nonsingular (exact disc != 0, deterministic rejection
  logged), integer coefficients of bit-size matched to the constructed s
  (|coef| <= 2^B, B = max bit length over s coefficient numerators and
  denominators), scanned over the SAME 4 non-forced classes with the
  identical box and test. Fisher exact one-sided (alpha = 0.05) on the
  2x2 table of PRODUCTIVE cells (>= 1 hit): [[productive_constructed, 4],
  [productive_null, 32]] (cells are the unit of the contract's declared
  test: "4 constructed non-forced cells vs 32 null cells"; hit totals are
  additionally recorded). Exact hypergeometric tail via math.comb.

IC-12 DETERMINISM. PYTHONHASHSEED=0; every list sorted before use; single
  process; no time-dependent branch except the wall-cap stop check (7200 s,
  far above actual runtime; the counted-ops stop is deterministic). The
  arm-B replay run re-executes the identical command; the instance list is
  compared BIT-FOR-BIT (sha256 + byte compare) and secondary artifacts
  (cell counts, op counters, per-b statuses) are compared field-wise;
  divergence voids both runs (IV-7) and is reported, never repaired.

NO DESCENT, NO NETWORK, NO PARI IN THE PIPELINE. The only optional PARI use
is the IC-9 numerical regulator cross-check outside the certificate.
"""

import builtins
import hashlib
import importlib.util
import itertools
import json
import math
import os
import random
import sys
import time
from fractions import Fraction as Fr
from math import gcd, isqrt

Fr0 = Fr(0)
Fr1 = Fr(1)

# --------------------------------------------------------------------------
# IC-1: counted exact-op instrumentation
# --------------------------------------------------------------------------

OPS = {"count": 0}
_COUNTING = {"on": False}
_orig = {}
_ORIG_POW = builtins.pow
_ORIG_ISQRT = math.isqrt


def _wrap_frac(name):
    f = getattr(Fr, name)

    def wrapper(self, other):
        if _COUNTING["on"]:
            OPS["count"] += 1
        return f(self, other)

    return wrapper


def _install_counter():
    if _orig:
        return
    for name in ("__add__", "__radd__", "__sub__", "__rsub__", "__mul__",
                 "__rmul__", "__truediv__", "__rtruediv__", "__pow__",
                 "__rpow__", "__floordiv__", "__rfloordiv__"):
        _orig[name] = getattr(Fr, name)
        setattr(Fr, name, _wrap_frac(name))

    def counting_pow(*a):
        if _COUNTING["on"]:
            OPS["count"] += 1
        return _ORIG_POW(*a)

    def counting_isqrt(n):
        if _COUNTING["on"]:
            OPS["count"] += 1
        return _ORIG_ISQRT(n)

    _orig["pow"] = builtins.pow
    _orig["isqrt"] = math.isqrt
    builtins.pow = counting_pow
    math.isqrt = counting_isqrt
    # module-local aliases used by copied committed code
    globals()["math_isqrt"] = counting_isqrt


def start_counting():
    _install_counter()
    _COUNTING["on"] = True


def stop_counting():
    _COUNTING["on"] = False


def ops_count():
    return OPS["count"]


def reset_ops():
    OPS["count"] = 0


# isqrt alias used everywhere below (counted)
def isqrt_c(n):
    return math.isqrt(n)


# --------------------------------------------------------------------------
# verbatim copies from construct_highrank.py (pure-Fraction subset; see
# module docstring for provenance and fidelity pinning)
# --------------------------------------------------------------------------


def pmul(a, b):
    r = [Fr(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        if x == 0:
            continue
        for j, y in enumerate(b):
            r[i + j] += x * y
    return r


def psub(a, b):
    n = max(len(a), len(b))
    r = [Fr(0)] * n
    for i, x in enumerate(a):
        r[i] += x
    for i, y in enumerate(b):
        r[i] -= y
    while len(r) > 1 and r[-1] == 0:
        r.pop()
    return r


def peval(p, x):
    s = Fr(0)
    for c in reversed(p):
        s = s * x + c
    return s


def prod_linear(A):
    p = [Fr(1)]
    for a in A:
        p = pmul(p, [Fr(-a), Fr(1)])
    return p


def pshift(p, c):
    """return p(t + c)"""
    out = [Fr(0)]
    base = [Fr(1)]
    for i, co in enumerate(p):
        if i > 0:
            base = pmul(base, [c, Fr(1)])
        out = psub(out, [-co * b for b in base])
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return out


def polysqrt_trunc(p, k):
    """p monic of degree 2k -> monic g of degree k with deg(p - g^2) <= k-1."""
    g = [Fr(0)] * (k + 1)
    g[k] = Fr(1)
    for j in range(k - 1, -1, -1):
        S = Fr(0)
        for u in range(j + 1, k + 1):
            v = k + j - u
            if 0 <= v <= k and v > j:
                S += g[u] * g[v]
        g[j] = (p[k + j] - S) / 2
    return g


def mestre_polys(A):
    """A: list of 2k distinct rationals. returns p, g, s = g^2 - p."""
    n = len(A)
    assert n % 2 == 0
    k = n // 2
    p = prod_linear([Fr(a) for a in A])
    g = polysqrt_trunc(p, k)
    s = psub(pmul(g, g), p)
    # exact check of the 2k simultaneous square conditions
    for a in A:
        if peval(s, Fr(a)) != peval(g, Fr(a)) ** 2:
            raise AssertionError("square condition failed at a=%s" % a)
    return p, g, s


def quartic_reduction(s, a0, e):
    """s quartic with s(a0) = e^2 (e != 0).  Return (D, coef) where D is the
    cubic in m and coef = (a,b,c,d,e) of the shifted quartic."""
    st = pshift(s, Fr(a0))
    st = st + [Fr(0)] * (5 - len(st))
    c0, d, c, b, a = st[0], st[1], st[2], st[3], st[4]
    if c0 != e * e:
        raise AssertionError("shift did not produce e^2 constant term")
    cp = c - d * d / (4 * e * e)
    P1 = psub([b], [Fr(0), d / e])
    P2 = psub([a], [Fr(0), Fr(0), Fr(1)])
    P3 = psub([cp], [Fr(0), 2 * e])
    D = psub(pmul(P1, P1), [4 * x for x in pmul(P2, P3)])
    return D, (a, b, c, d, e)


def quartic_point_to_cubic(t, v, coef):
    a, b, c, d, e = coef
    m = (v - e - (d / (2 * e)) * t) / (t * t)
    w = 2 * (a - m * m) * t + (b - (d / e) * m)
    return m, w


def cubic_to_weierstrass(D, pts):
    """w^2 = D(m), deg D = 3 -> Y^2 = X^3 + a2 X^2 + a4 X + a6 (integral)."""
    if len(D) != 4 or D[3] == 0:
        raise AssertionError("D is not a genuine cubic")
    A0, A1, A2, A3 = D[0], D[1], D[2], D[3]
    a2, a4, a6 = A2, A1 * A3, A0 * A3 * A3
    P = [(A3 * m, A3 * w) for m, w in pts]
    u = math.lcm(a2.denominator, a4.denominator, a6.denominator)
    a2, a4, a6 = a2 * u * u, a4 * u ** 4, a6 * u ** 6
    P = [(x * u * u, y * u ** 3) for x, y in P]
    ainv = [Fr(0), a2, Fr(0), a4, a6]
    for x, y in P:
        if y * y != x ** 3 + a2 * x * x + a4 * x + a6:
            raise AssertionError("weierstrass image point off curve")
    return [int(z) for z in ainv], P


def verify_on_curve(ainv, x, y):
    """EXACT check of y^2 + a1 x y + a3 y = x^3 + a2 x^2 + a4 x + a6.
    Own code, fractions only, no PARI."""
    a1, a2, a3, a4, a6 = [Fr(z) for z in ainv]
    x = Fr(x)
    y = Fr(y)
    return y * y + a1 * x * y + a3 * y == x ** 3 + a2 * x * x + a4 * x + a6


def disc_from_ainv(ainv):
    a1, a2, a3, a4, a6 = [Fr(z) for z in ainv]
    b2 = a1 * a1 + 4 * a2
    b4 = 2 * a4 + a1 * a3
    b6 = a3 * a3 + 4 * a6
    b8 = a1 * a1 * a6 + 4 * a2 * a6 - a1 * a3 * a4 + a2 * a3 * a3 - a4 * a4
    return -b2 * b2 * b8 - 8 * b4 ** 3 - 27 * b6 * b6 + 9 * b2 * b4 * b6


# --------------------------------------------------------------------------
# byte-identical import of the committed exact F_l certifier (IC-9)
# --------------------------------------------------------------------------

EXACT_CERTIFY_PATH = (
    "coordination/goals/GOAL-ECQ-002/batches/BATCH-8b08ef/tasks/"
    "TASK-20260823-827765/scripts/exact_certify.py")
EXACT_CERTIFY_SHA = (
    "1bc7c05954fdf9531c41eb942e91f918e401098971b2211501a9628ae011ea8e")


def load_exact_certify(repo_root):
    path = os.path.join(repo_root, EXACT_CERTIFY_PATH)
    digest = hashlib.sha256(open(path, "rb").read()).hexdigest()
    if digest != EXACT_CERTIFY_SHA:
        raise RuntimeError(
            "exact_certify.py sha256 drift: %s != pinned %s -- committed "
            "certifier changed; refusing to run" % (digest, EXACT_CERTIFY_SHA))
    spec = importlib.util.spec_from_file_location("exact_certify_committed",
                                                  path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod, digest


# --------------------------------------------------------------------------
# polynomial helpers (engine)
# --------------------------------------------------------------------------


def lagrange_interp(xs, ys):
    """Exact interpolant through points (xs, ys); degree <= len(xs)-1."""
    n = len(xs)
    total = [Fr(0)]
    for i in range(n):
        num = [Fr(1)]
        den = Fr(1)
        for j in range(n):
            if i == j:
                continue
            num = pmul(num, [Fr(-xs[j]), Fr(1)])
            den *= (xs[i] - xs[j])
        term = [(ys[i] / den) * c for c in num]
        total = psub(total, [-c for c in term])
    return total


def polymod_monic(f, p):
    """f mod p, p monic. Exact polynomial remainder."""
    r = list(f)
    dp = len(p) - 1
    while len(r) - 1 >= dp and any(c != 0 for c in r):
        lead = r[-1]
        if lead == 0:
            r.pop()
            continue
        shift = len(r) - 1 - dp
        for i in range(dp + 1):
            r[shift + i] -= lead * p[i]
        while len(r) > 1 and r[-1] == 0:
            r.pop()
    return r


def poly_disc(s):
    """Exact discriminant of polynomial s (deg 3 or 4), Fractions.
    disc = (-1)^{d(d-1)/2} res(s, s') / lc."""
    d = len(s) - 1
    lc = s[-1]
    if lc == 0 or d < 1:
        raise ValueError("poly_disc: degenerate input")
    der = [Fr(i) * s[i] for i in range(1, len(s))]
    # Sylvester matrix (d + (d-1)) x (d + (d-1))
    N = d + (d - 1)
    M = [[Fr(0)] * N for _ in range(N)]
    for i in range(d - 1):          # d-1 rows of s coefficients
        for j in range(d + 1):
            M[i][i + j] = s[d - j] if (d - j) >= 0 else Fr(0)
    for i in range(d):              # d rows of s' coefficients
        for j in range(d):
            M[(d - 1) + i][i + j] = der[(d - 1) - j] if (d - 1 - j) >= 0 else Fr(0)
    res = det_fraction(M)
    sign = -1 if (d * (d - 1) // 2) % 2 else 1
    return sign * res / lc


def det_fraction(M):
    """Exact determinant by Gauss elimination, Fractions."""
    n = len(M)
    M = [row[:] for row in M]
    det = Fr(1)
    for col in range(n):
        piv = None
        for i in range(col, n):
            if M[i][col] != 0:
                piv = i
                break
        if piv is None:
            return Fr(0)
        if piv != col:
            M[col], M[piv] = M[piv], M[col]
            det = -det
        det *= M[col][col]
        inv = Fr(1) / M[col][col]
        for i in range(col + 1, n):
            if M[i][col] != 0:
                f = M[i][col] * inv
                for j in range(col, n):
                    M[i][j] -= f * M[col][j]
    return det


# --------------------------------------------------------------------------
# exact square tests
# --------------------------------------------------------------------------


def is_square_int(n):
    if n < 0:
        return False
    r = isqrt_c(n)
    return r * r == n


def rational_square(y):
    """y a nonzero positive rational square? return sqrt(y) or None."""
    if y <= 0:
        return None
    num, den = y.numerator, y.denominator
    rn = isqrt_c(num)
    rd = isqrt_c(den)
    if rn * rn == num and rd * rd == den:
        return Fr(rn, rd)
    return None


def squarefree_part(n):
    """Squarefree part of a nonzero integer (committed semantics)."""
    if n == 0:
        raise ValueError("d=0")
    s = -1 if n < 0 else 1
    n = abs(n)
    out = 1
    d = 2
    while d * d <= n:
        e = 0
        while n % d == 0:
            n //= d
            e += 1
        if e & 1:
            out *= d
        d += 1 if d == 2 else 2
    out *= n
    return s * out


# --------------------------------------------------------------------------
# committed coset enumeration algorithm (twist_family.py, re-implemented
# stdlib-pure; IC/provenance in module docstring)
# --------------------------------------------------------------------------

SUPPORT_COMMITTED = [-1, 2, 3, 5, 7, 11, 13]


def class_value(mask, support=SUPPORT_COMMITTED):
    d = 1
    for i, g in enumerate(support):
        if mask >> i & 1:
            d *= g
    return d


def subspaces(n, k):
    """All k-dimensional subspaces of F_2^n, each as its sorted list of masks
    (committed algorithm: RREF pivot enumeration)."""
    out = []
    for pivots in itertools.combinations(range(n, ), k):
        free = [j for j in range(n) if j not in pivots]
        slots = [[j for j in free if j > piv] for piv in pivots]
        grids = [list(itertools.product([0, 1], repeat=len(s))) for s in slots]
        for choice in itertools.product(*grids):
            basis = []
            for i, piv in enumerate(pivots):
                v = 1 << piv
                for bit, j in zip(choice[i], slots[i]):
                    if bit:
                        v |= 1 << j
                basis.append(v)
            span = [0]
            for b in basis:
                span += [x ^ b for x in span]
            out.append(sorted(span))
    return out


def affine_subspaces(n, k):
    """All cosets m0 + V of all k-dimensional V <= F_2^n, deduplicated
    (committed algorithm: min-mask representatives)."""
    out = []
    for V in subspaces(n, k):
        reps = {min(m ^ v for v in V) for m in range(1 << n)}
        for m0 in sorted(reps):
            out.append((m0, V))
    return out


MINUS_ONE_MASK = 1 << SUPPORT_COMMITTED.index(-1)


def eligible_cosets():
    """All affine k=3 cosets whose direction space contains the -1 mask.
    Sorted canonically: by (sorted direction masks, coset representative)."""
    out = []
    for V in subspaces(len(SUPPORT_COMMITTED), 3):
        if MINUS_ONE_MASK not in V:
            continue
        Vs = tuple(V)
        reps = sorted({min(m ^ v for v in V) for m in range(1 << len(SUPPORT_COMMITTED))})
        for m0 in reps:
            members = tuple(sorted(m0 ^ v for v in V))
            out.append({"m0": m0, "V": Vs, "members": members,
                        "values": tuple(class_value(m) for m in members)})
    out.sort(key=lambda c: (c["V"], c["m0"]))
    return out


# --------------------------------------------------------------------------
# Vandermonde kernel, delta, gamma (M3)
# --------------------------------------------------------------------------


def vandermonde_kernel(b):
    """Exact reduced basis of {c : sum_i c_i b_i^j = 0, j = 0..4}, dim n-5.
    b: list of n distinct rationals (Fractions)."""
    n = len(b)
    V = [[Fr(b[i]) ** j for i in range(n)] for j in range(5)]
    # Gauss-Jordan to RREF
    M = [row[:] for row in V]
    pivots = []
    row = 0
    for col in range(n):
        if row >= 5:
            break
        piv = None
        for i in range(row, 5):
            if M[i][col] != 0:
                piv = i
                break
        if piv is None:
            continue
        M[row], M[piv] = M[piv], M[row]
        inv = Fr(1) / M[row][col]
        M[row] = [x * inv for x in M[row]]
        for i in range(5):
            if i != row and M[i][col] != 0:
                f = M[i][col]
                M[i] = [a - f * bb for a, bb in zip(M[i], M[row])]
        pivots.append(col)
        row += 1
    assert row == 5, "Vandermonde rank < 5 (b not distinct?)"
    free_cols = [c for c in range(n) if c not in pivots]
    basis = []
    for f in free_cols:
        c = [Fr(0)] * n
        c[f] = Fr(1)
        for r, pc in enumerate(pivots):
            c[pc] = -M[r][f]
        basis.append(c)
    return basis


# --------------------------------------------------------------------------
# fibration draw + solve (IC-2/3/4)
# --------------------------------------------------------------------------


def draw_rational(rng, H):
    """IC-3: seeded nonzero rational of height <= H."""
    sign = rng.choice([1, -1])
    num = rng.randint(1, H)
    den = rng.randint(1, H)
    g = gcd(num, den)
    return Fr(sign * (num // g), den // g)


def solve_draw(gamma, S, T, rS):
    """Solve gamma[:,T] y = K with K_m = -sum_{i in S} gamma[m][i] rS[i]^2.
    Returns y dict over T, or None with reason."""
    k = len(T)
    K = []
    for m in range(k):
        acc = Fr(0)
        for i in S:
            acc += gamma[m][i] * rS[i] * rS[i]
        K.append(-acc)
    A = [[gamma[m][l] for l in T] for m in range(k)]
    # exact Gauss-Jordan on augmented [A|K]
    M = [A[m] + [K[m]] for m in range(k)]
    for col in range(k):
        piv = None
        for i in range(col, k):
            if M[i][col] != 0:
                piv = i
                break
        if piv is None:
            return None, "singular_fibration"
        M[col], M[piv] = M[piv], M[col]
        inv = Fr(1) / M[col][col]
        M[col] = [x * inv for x in M[col]]
        for i in range(k):
            if i != col and M[i][col] != 0:
                f = M[i][col]
                M[i] = [a - f * bb for a, bb in zip(M[i], M[col])]
    y = {T[col]: M[col][k] for col in range(k)}
    return y, None


# --------------------------------------------------------------------------
# degeneracy filter (C4) and instance assembly
# --------------------------------------------------------------------------


def rational_height(r):
    return max(abs(r.numerator), r.denominator)


def build_instance(b, dpat, r, n):
    """Assemble s and run the exact C4 filter + identity checks.
    Returns dict or raises/rejects with reason."""
    xs = [Fr(x) for x in b]
    v = [Fr(dpat[i]) * r[i] * r[i] for i in range(n)]
    s = lagrange_interp(xs, v)
    # ellipticity: coefficients above degree 4 vanish identically
    for j in range(5, len(s)):
        if s[j] != 0:
            return None, "ellipticity_violation_degree_%d" % j
    s = s[:5]
    while len(s) > 1 and s[-1] == 0:
        s.pop()
    deg = len(s) - 1
    if deg not in (3, 4):
        return None, "degenerate_deg_s_%d" % deg
    # nonzero forced values (g(b_i) != 0)
    for i in range(n):
        if r[i] == 0:
            return None, "degenerate_r_zero_at_%d" % i
    # nonsingularity: exact discriminant of the quartic/cubic model
    disc = poly_disc(s)
    if disc == 0:
        return None, "singular_model_disc_zero"
    # forcing identity on points (exact)
    for i in range(n):
        if peval(s, xs[i]) != Fr(dpat[i]) * r[i] * r[i]:
            return None, "forcing_identity_failure_at_%d" % i
    # M2 identity cross-check: delta * g^2 == s (mod p)
    delta = lagrange_interp(xs, [Fr(x) for x in dpat])
    g = lagrange_interp(xs, [r[i] for i in range(n)])
    p = prod_linear(xs)
    lhs = polymod_monic(pmul(delta, pmul(g, g)), p)
    rhs = list(s) + [Fr(0)] * (max(0, len(lhs) - len(s)))
    if len(lhs) != len(rhs) or any(a != bb for a, bb in zip(lhs, rhs)):
        return None, "m2_identity_failure"
    h = max(rational_height(r[i]) for i in range(n))
    hs = max(max(abs(c.numerator), c.denominator) for c in s)
    return {"b": [str(x) for x in b], "d_pattern": list(dpat),
            "r": [str(x) for x in r], "s": [str(c) for c in s],
            "deg_s": deg, "disc_s": str(disc), "r_height": h,
            "height_s": hs, "delta": [str(c) for c in delta],
            "bezout_candidates": 2 ** (n - 5)}, None


# --------------------------------------------------------------------------
# canonical curve key for dedup (IC-8)
# --------------------------------------------------------------------------


def short_model_from_ainvs(ai):
    """VERBATIM committed stdlib short-form conversion from
    coordination/goals/GOAL-ECRANK-002/batches/BATCH-e0caa5/tasks/
    TASK-20260822-8df232/src/coset_structure.py (integer c4/c6 arithmetic,
    no PARI).  C6 dedup keys use this committed conversion; the committed
    pipeline's PARI ellminimalmodel is BANNED by this contract's own
    stdlib-only solver constraint -- disclosed adaptation, recorded in the
    run report."""
    a1, a2, a3, a4, a6 = ai
    b2 = a1 * a1 + 4 * a2
    b4 = 2 * a4 + a1 * a3
    b6 = a3 * a3 + 4 * a6
    c4 = b2 * b2 - 24 * b4
    c6 = -b2 * b2 * b2 + 36 * b2 * b4 - 216 * b6
    return -27 * c4, -54 * c6


def short_form_from_ainv(ainv):
    """[0,a2,0,a4,a6] -> short y^2 = x^3 + A x + B over Q (x -> x - a2/3)."""
    a2, a4, a6 = Fr(ainv[1]), Fr(ainv[3]), Fr(ainv[5])
    A = a4 - a2 * a2 / 3
    B = a6 + Fr(2, 27) * a2 ** 3 - a2 * a4 / 3
    return (A, B)


def _strip_power(x, k):
    """Largest y with y^k | x (x > 0 int); return (y, x // y^k)."""
    y = 1
    d = 2
    xx = x
    while d * d <= xx:
        e = 0
        while xx % d == 0:
            xx //= d
            e += 1
        if e:
            y *= d ** (e // k)
        d += 1 if d == 2 else 2
    if xx > 1:
        # remaining prime with exponent 1 < k
        pass
    return y


def canonical_short_key(AB):
    """Canonical representative of (A,B) under (u^4 A, u^6 B), exact.
    Strategy: write A = a * ra^4, B = b * rb^6 with a,b integer,
    4th/6th-power-free parts extracted; the scaling class is determined by
    the rational number A^3/B^2 (j-data) plus signs; we canonicalize by
    choosing u so that A' = u^4 A, B' = u^6 B are integers of minimal
    height: u = 1/w with w extracted from denominators."""
    A, B = AB
    if A == 0 and B == 0:
        raise ValueError("singular short form")
    # scale to integers first: u integral scaling cannot change class unless
    # we also divide; work with the invariant t = A^3 / B^2 when B != 0.
    if A == 0:
        # class determined by B up to 6th powers: canonical = 6th-power-free
        # part of B (sign kept)
        sgn = 1 if B > 0 else -1
        num = abs(B.numerator)
        den = B.denominator
        w = _strip_power(den, 6)
        # u = 1/w: B' = B * w^6 -> integer; strip 6th powers from numerator
        Bp = B * Fr(w) ** 6
        n2 = abs(Bp.numerator)
        y = _strip_power(n2, 6)
        Bp = Bp / Fr(y) ** 6
        return ("A0", str(Bp))
    if B == 0:
        sgn = 1 if A > 0 else -1
        den = A.denominator
        w = _strip_power(den, 4)
        Ap = A * Fr(w) ** 4
        y = _strip_power(abs(Ap.numerator), 4)
        Ap = Ap / Fr(y) ** 4
        return ("B0", str(Ap))
    # general: t = A^3/B^2 is a complete invariant of the scaling class
    # together with sign data: (A,B) ~ (u^4A, u^6B); t invariant. Two pairs
    # with equal t are isomorphic over Q iff ... they always are: given t,
    # choose u with u^12 = A^3/B^2 * (B'^2/A'^3)... canonicalize directly:
    # pick u so that A' = u^4 A = +-4th-power-free integer and B' determined.
    t = A ** 3 / B ** 2
    # canonical pair from t: A_c = t-part... use: A' = 1 * scaling: choose
    # u^2 = A/(sgn) ... simplest exact canonical: A' = A / (A's 4th powers),
    # then B' = B * (same u^6): must keep consistency: u^4 = 1/y^4 ->
    den = A.denominator
    w = _strip_power(den, 4)
    Ap = A * Fr(w) ** 4
    y = _strip_power(abs(Ap.numerator), 4)
    Ap = Ap / Fr(y) ** 4          # u = w/y : A' = u^4 A
    Bp = B * Fr(w / y) ** 6
    return ("gen", str(Ap), str(Bp), str(t))


def curves_isomorphic(AB1, AB2):
    """Exact Q-isomorphism test of short forms."""
    A1, B1 = AB1
    A2, B2 = AB2
    if A1 == 0:
        if A2 != 0:
            return False
        s = B2 / B1
        if s <= 0:
            return False
        rn = isqrt_c(isqrt_c(s.numerator)) if is_square_int(s.numerator) else None
        # s must be a 6th power
        num, den = s.numerator, s.denominator
        r6n = _exact_root(num, 6)
        r6d = _exact_root(den, 6)
        return r6n is not None and r6d is not None
    if B1 == 0:
        if B2 != 0:
            return False
        s = A2 / A1
        if s <= 0:
            return False
        r4n = _exact_root(s.numerator, 4)
        r4d = _exact_root(s.denominator, 4)
        return r4n is not None and r4d is not None
    if A2 == 0 or B2 == 0:
        return False
    t = A2 / A1
    s = B2 / B1
    if t <= 0 or s <= 0:
        # negative scaling u impossible over Q for even powers
        return False
    if t ** 3 != s ** 2:
        return False
    w = _exact_root(t.numerator, 4)
    wd = _exact_root(t.denominator, 4)
    if w is None or wd is None:
        return False
    u = Fr(w, wd)
    return u ** 4 == t and u ** 6 == s


def _exact_root(n, k):
    """Exact integer k-th root of n >= 0 or None."""
    if n < 0:
        return None
    if n == 0:
        return 0
    r = int(round(n ** (1.0 / k)))
    for cand in (r - 2, r - 1, r, r + 1, r + 2):
        if cand >= 0 and cand ** k == n:
            return cand
    return None


def j_invariant(AB):
    A, B = AB
    c4 = -48 * A
    disc = -16 * (4 * A ** 3 + 27 * B ** 2)
    if disc == 0:
        raise ValueError("singular")
    return c4 ** 3 / disc


# --------------------------------------------------------------------------
# local solvability (arm A; IC-10)
# --------------------------------------------------------------------------


def primes_upto(n):
    sieve = [True] * (n + 1)
    sieve[0:2] = [False, False]
    for i in range(2, int(n ** 0.5) + 1):
        if sieve[i]:
            sieve[i * i::i] = [False] * len(sieve[i * i::i])
    return [i for i, bb in enumerate(sieve) if bb]


PRIMES_100 = primes_upto(100)


def legendre(a, p):
    a %= p
    if a == 0:
        return 0
    return 1 if pow(a, (p - 1) // 2, p) == 1 else -1


def local_solvability(gamma_row, dpat=None):
    """IC-10. gamma_row: single relation row (Fractions) of the n=6 system;
    the diagonal form sum gamma_i x_i^2 = 0. Returns dict of outcomes."""
    # integer scale (zeros of the form unchanged by positive scaling)
    L = 1
    for c in gamma_row:
        L = math.lcm(L, c.denominator)
    G = [int(c * L) for c in gamma_row]
    out = {"real_place": None, "primes": {}, "obstruction": None}
    signs = set((g > 0) - (g < 0) for g in G if g != 0)
    if len(signs) >= 2:
        out["real_place"] = "solvable_mixed_signs"
    elif len(signs) == 1:
        out["real_place"] = "OBSTRUCTION_all_same_sign"
        out["obstruction"] = "real_place"
    else:
        out["real_place"] = "degenerate_all_zero"
    for p in PRIMES_100:
        Gm = [g % p for g in G]
        # constructive pair witness: (-gi*gj | p) = 1
        status = None
        witness = None
        for i in range(len(Gm)):
            for j in range(i + 1, len(Gm)):
                if Gm[i] % p == 0 or Gm[j] % p == 0:
                    continue
                if legendre((-Gm[i] * Gm[j]) % p, p) == 1:
                    # explicit: find x with x^2 = -gj/gi mod p
                    target = (-Gm[j] * pow(Gm[i], -1, p)) % p
                    x = _sqrt_mod(target, p)
                    witness = {"coords": [i, j], "x": [str(x), "1"]}
                    status = "solvable_constructive"
                    break
            if status:
                break
        if status is None:
            # all-same-square-class fallback with (-1|p) = -1:
            nonzero = [g % p for g in Gm if g % p != 0]
            if nonzero and all(legendre(g * pow(nonzero[0], -1, p) % p, p) == 1
                               for g in nonzero) and legendre(-1, p) == -1:
                g0 = nonzero[0]
                # find a,b with a^2+b^2 = -1 mod p (sums of two squares
                # surjective on F_p): scan a
                found = None
                for a in range(p):
                    t = (-1 - a * a) % p
                    if t == 0:
                        found = (a, 0)
                        break
                    sb = _sqrt_mod(t, p)
                    if sb is not None:
                        found = (a, sb)
                        break
                if found:
                    status = "solvable_constructive"
                    witness = {"coords": [0, 1, 2],
                               "x": [str(found[0]), str(found[1]), "1"],
                               "note": "same-square-class fallback a^2+b^2=-1"}
        if status is None:
            status = "no_constructive_witness"
        out["primes"][str(p)] = {"status": status, "witness": witness}
    return out


def _sqrt_mod(a, p):
    """Tonelli-Shanks exact; returns x with x^2 = a mod p or None."""
    if a % p == 0:
        return 0
    if legendre(a, p) != 1:
        return None
    if p % 4 == 3:
        return pow(a, (p + 1) // 4, p)
    # small p: brute force is fine (p <= 100)
    for x in range(1, p):
        if x * x % p == a:
            return x
    return None


# --------------------------------------------------------------------------
# augmentation scan + Fisher (IC-11)
# --------------------------------------------------------------------------


def scan_class(s, d, nmax=1000, dmax=20):
    """Exact scan: u = num/den, |num| <= nmax, 1 <= den <= dmax, gcd 1;
    test s(u)/d a nonzero rational square. Returns hits list."""
    L = 1
    for c in s:
        L = math.lcm(L, c.denominator)
    C = [int(c * L) for c in s]              # L*s integral
    deg = len(C) - 1
    hits = []
    dd_pows = {}
    for dd in range(1, dmax + 1):
        dd_pows[dd] = [dd ** j for j in range(deg + 1)]
    dl = abs(int(d)) * L if d != 0 else None
    if dl is None:
        return hits
    # s(u)/d square  <=>  (L*s(u)) * (L*d) is a square times (den^{2deg}) --
    # do it exactly per u with integer test then Fraction re-verification
    for dd in range(1, dmax + 1):
        dp = dd_pows[dd]
        for num in range(-nmax, nmax + 1):
            if num == 0:
                continue
            if gcd(abs(num), dd) != 1:
                continue
            OPS["count"] += 1 if _COUNTING["on"] else 0
            S = 0
            npow = 1
            for j in range(deg + 1):
                S += C[j] * npow * dp[deg - j]
                npow *= num
            # s(num/dd) = S / (L * dd^deg); s/d square <=> S*L*d / dd^deg ...
            # exact: T = S * (L * d) ; square test on T with dd^deg factor:
            # s(u)/d = S/(L*dd^deg*d) = (S*L*d)/(L^2*d^2*dd^deg)
            # numerator N = S*L*d, denominator D = (L*d)^2 * dd^deg.
            # square in Q <=> N * dd^deg_adjust ... use: value = Fr(S, L*dd**deg) / Fr(d)
            T = S * (L * int(d))
            if T <= 0:
                continue
            # value = T / (L*d*dd^deg)^2 * dd^deg / dd^deg ... exact route:
            den2 = (L * int(d) * dd ** deg)
            # value = T_adjust / den2^2 with T_adjust = S * L * d * dd^deg
            Ta = S * (L * int(d)) * (dd ** deg)
            if Ta <= 0:
                continue
            rt = isqrt_c(Ta)
            if rt * rt != Ta:
                continue
            val = Fr(rt, abs(den2))
            if val * val != peval(s, Fr(num, dd)) / Fr(d):
                continue
            hits.append({"u": "%d/%d" % (num, dd), "w": str(val)})
    return hits


def fisher_one_sided(a, n1, c, n2):
    """Exact one-sided Fisher test (greater) on [[a, n1],[c, n2]] where the
    first column counts successes out of row trials. Returns p-value
    (Fraction) and float."""
    K = a + c
    N = n1 + n2
    if K > N:
        raise ValueError("successes exceed trials")
    total = math.comb(N, n1)
    tail = 0
    k = a
    while k <= min(n1, K):
        if K - k <= n2:
            tail += math.comb(K, k) * math.comb(N - K, n1 - k)
        k += 1
    p = Fr(tail, total)
    return p, float(p)


# --------------------------------------------------------------------------
# checkpointing
# --------------------------------------------------------------------------


class Checkpointer:
    """Flush a prefix artifact every >= 10^7 counted ops (contract stopping
    rules) and at every interval_b b-tuples (crash resilience; the counted-
    ops cadence is the contract floor)."""

    def __init__(self, ckpt_dir, every_ops=10 ** 7):
        self.dir = ckpt_dir
        self.every = every_ops
        self.last = 0
        self.n = 0
        os.makedirs(ckpt_dir, exist_ok=True)

    def maybe(self, state_fn):
        c = ops_count()
        if c - self.last >= self.every:
            self.flush(state_fn, "ops_%d" % c)
            self.last = c

    def flush(self, state_fn, tag):
        self.n += 1
        path = os.path.join(self.dir, "ckpt-%03d-%s.json" % (self.n, tag))
        with open(path, "w") as f:
            json.dump(state_fn(), f)
        return path


# --------------------------------------------------------------------------
# misc helpers
# --------------------------------------------------------------------------


def frs(x):
    x = Fr(x)
    return "%d/%d" % (x.numerator, x.denominator)


def peak_rss_bytes():
    import resource
    r = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    # darwin: bytes; linux: kibibytes
    if sys.platform == "darwin":
        return r
    return r * 1024


def sha256_file(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()
