#!/usr/bin/env python3
"""certify76.py -- exact descent-free certificate for EXP-ECRANK-76a70d.

NEW module beside the committed machinery (spec implementation_constraint;
never an edit to construct_highrank.py / coset_structure.py / exact_certify.py).
Imports ecrank_engine.py (which carries the verbatim copies of the committed
Mestre/quartic functions and the byte-identical exact_certify loader).

Architecture
------------
Instance: forced points (b_i, r_i), i = 1..n, with s(b_i) = d_i * r_i^2 for
class values d_i drawn from ONE k = 3 coset of the committed support
{-1, 2, 3, 5, 7, 11, 13}; deg s in {3, 4}; s nonsingular (C4 filter upstream).

Per class d (points (b_i, r_i) with that d):
  W_d : w^2 = s(u)/d  contains the class points exactly (r_i^2 = s(b_i)/d).
  deg s = 3: integral Weierstrass model via the COMMITTED
    cubic_to_weierstrass scaling (exact on-curve rechecks built in).
  deg s = 4: COMMITTED quartic_reduction at the class's FIRST point, then the
    same integral scaling.  The reduction base point (b_1, r_1) maps to the
    FINITE point R0 = (m*, w*) with m* = cp/(2e), w* = b - d*cp/(2e^2)
    (coefficients (a,b,c,d,e) of the shifted quartic, cp = c - d^2/(4e^2));
    its fiber partner (b_1, -r_1) maps to O.  Closed form is re-checked
    exactly against w*^2 = D(m*) and the on-curve equation.
  certified_e := committed exact_certify.certify(W_d, images of ALL class
    points) -> exact F_l within-class rank lower bound (<= n_e).

Base class d1 = first (sorted) class value present; E0' = W_{d1};
kappa' = R0 of E0' (deg 4) or O (deg 3).  Note kappa' = Phi_{base,1}, the
image of the base class's first point under E0's own reduction.

Lifts: for class d_i, e_i = sf(d_i*d_1) = class_value(m_i XOR m_1) (an
element of the coset direction space V, asserted both ways), d_i*d_1 =
e_i*f_i^2, rho_i = r_i*f_i/d_1, so (sqrt(e_i)*rho_i)^2 = s(b_i)/d_1 and
Phi_i := (b_i, sqrt(e_i)*rho_i) mapped into E0' lies in E0'(Q(sqrt(e_i))).

Galois/eigenspace layer (exact, in Q(sqrt(e_i))):
  tau_i = the nontrivial automorphism of Q(sqrt(e_i)).  For deg 4 the
  transported involution is iota' = t_{kappa'} o [-1]; for deg 3 it is [-1]
  (kappa' = O).  Diagnostic check: tau_i(Phi_i) == -Phi_i + kappa' whenever
  some generator acts nontrivially.
  Psi_i := kappa' - 2*Phi_i is a genuine chi_{e_i}-eigenvector:
  tau_i(Psi_i) == -Psi_i exactly (checked componentwise in the field) for
  every generator with chi = -1; generators with chi = +1 act as the
  identity on Q(sqrt(e_i)) (vacuous, recorded).

Units and aggregate (certificate-kind split per the frozen success criterion):
  eig_unit_e = 1 if certified_e >= 1 and (e trivial: Mazur-non-torsion via
    the committed certifier and witnesses; e nontrivial: at least one Psi of
    the class passes the 24-torsion screen).
  fl_unit_e = certified_e - eig_unit_e (the F_l certifier's within-class
    extra units).
  aggregate_total = SUM_e certified_e  MINUS 1 if any NONBASE class has
    certified_e < 2 (a within-class dependency leaks a relation into the
    trivial-character equation, which can consume one unit there; the
    deduction is conservative and exact), otherwise SUM_e certified_e.
  Claim: rank E0'(K_V) >= aggregate_total.  Exact ingredients: Q[G]
  character decomposition of E0'(K_V) (x) Q; the translation-corrected lift
  phi~ = phi - kappa_e is a group homomorphism (isomorphism of varieties);
  the committed F_l certifier; exact sigma-checks; the 24-screen.  Within-
  class Psi-pair independence follows from certified_e = 2 alone (projector
  argument; no torsion screen needed).  NO descent, NO root numbers, NO
  floating point anywhere in this module (IV-6).

Torsion screens: Mazur witnesses m*P != O, m = 1..12 on every Q-rational
image point (spec certification_machinery); screen m*Psi != O, m = 1..24 on
field points.  The 24 bound covers Kenku-Momose torsion orders over
quadratic fields (RECALLED pointer, provenance: recalled -- pointer, not
support; the witnesses m*Psi != O themselves are exact computations and the
rank argument above uses only them plus the projector lemma).

Kummer: [K_V : Q] = 8 via 7 exact integer square tests -- class_value(v) is
not a rational square for each of the 7 nonzero v in V (the 3 singles, 3
pairs, 1 triple of the basis masks: exactly the full pairwise-independence
set).  Coset closure mod squares and pairwise distinctness of the 8 member
values are checked exactly (IV-5).
"""

import math
from fractions import Fraction as Fr

import ecrank_engine as E

O = None  # point at infinity, for both Fr and QS coordinates


# --------------------------------------------------------------------------
# exact arithmetic in Q(sqrt(e)), e a nonzero squarefree integer
# --------------------------------------------------------------------------

class QS:
    """a + b*sqrt(e) with a, b exact Fractions.  Pure stdlib, exact."""

    __slots__ = ("e", "a", "b")

    def __init__(self, e, a=0, b=0):
        self.e = int(e)
        self.a = Fr(a)
        self.b = Fr(b)

    def _co(self, o):
        if isinstance(o, QS):
            if o.e != self.e:
                raise AssertionError("mixed quadratic fields %d/%d"
                                     % (self.e, o.e))
            return o
        return QS(self.e, o, 0)

    def __add__(self, o):
        o = self._co(o)
        return QS(self.e, self.a + o.a, self.b + o.b)

    __radd__ = __add__

    def __sub__(self, o):
        o = self._co(o)
        return QS(self.e, self.a - o.a, self.b - o.b)

    def __rsub__(self, o):
        o = self._co(o)
        return QS(self.e, o.a - self.a, o.b - self.b)

    def __mul__(self, o):
        o = self._co(o)
        return QS(self.e,
                  self.a * o.a + self.b * o.b * Fr(self.e),
                  self.a * o.b + self.b * o.a)

    __rmul__ = __mul__

    def __neg__(self):
        return QS(self.e, -self.a, -self.b)

    def __truediv__(self, o):
        o = self._co(o)
        nrm = o.a * o.a - o.b * o.b * Fr(o.e)
        if nrm == 0:
            raise ZeroDivisionError("division by zero in Q(sqrt(%d))" % self.e)
        return self * QS(o.e, o.a / nrm, -o.b / nrm)

    def __rtruediv__(self, o):
        return self._co(o) / self

    def __eq__(self, o):
        if o is None:
            return False
        o = self._co(o)
        return self.a == o.a and self.b == o.b

    def __hash__(self):
        return hash((self.e, self.a, self.b))

    def conj(self):
        return QS(self.e, self.a, -self.b)

    def is_zero(self):
        return self.a == 0 and self.b == 0

    def to_json(self):
        return {"a": str(self.a), "b": str(self.b), "e": self.e}

    def __repr__(self):
        return "(%s)+(%s)*sqrt(%d)" % (self.a, self.b, self.e)


def qs_pt_to_json(P):
    if P is None:
        return None
    return [P[0].to_json() if isinstance(P[0], QS) else str(P[0]),
            P[1].to_json() if isinstance(P[1], QS) else str(P[1])]


# --------------------------------------------------------------------------
# exact point arithmetic on [0, a2, 0, a4, a6] over Fr or QS (a1 = a3 = 0)
# --------------------------------------------------------------------------

def w_on_curve(a2, a4, a6, P):
    if P is None:
        return True
    x, y = P
    return y * y == x * x * x + a2 * x * x + a4 * x + a6


def w_neg(P):
    if P is None:
        return None
    return (P[0], -P[1])


def w_add(a2, a4, a6, P, Q):
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2:
        if y1 + y2 == 0:
            return None
        lam = (3 * x1 * x1 + 2 * a2 * x1 + a4) / (2 * y1)
    else:
        lam = (y2 - y1) / (x2 - x1)
    x3 = lam * lam - a2 - x1 - x2
    y3 = lam * (x1 - x3) - y1
    return (x3, y3)


def w_mul(a2, a4, a6, m, P):
    if m < 0:
        P = w_neg(P)
        m = -m
    R = None
    Q = P
    while m:
        if m & 1:
            R = w_add(a2, a4, a6, R, Q)
        Q = w_add(a2, a4, a6, Q, Q)
        m >>= 1
    return R


def pt_eq(P, Q):
    if P is None or Q is None:
        return P is None and Q is None
    return P[0] == Q[0] and P[1] == Q[1]


def popcount(x):
    return bin(x).count("1")


# --------------------------------------------------------------------------
# integral model of w^2 = D (deg 3): replicates the committed
# cubic_to_weierstrass scaling exactly, and exposes it as a map
# --------------------------------------------------------------------------

def cubic_model_from_D(D):
    """D: cubic Fraction poly.  Returns (ainv, u_lcm, A3) with the SAME
    integral ainv the committed cubic_to_weierstrass produces; the point map
    is (m, w) -> (A3*m*u^2, A3*w*u^3), valid over Fr or QS."""
    if len(D) != 4 or D[3] == 0:
        raise AssertionError("D is not a genuine cubic")
    A0, A1, A2, A3 = D[0], D[1], D[2], D[3]
    a2, a4, a6 = A2, A1 * A3, A0 * A3 * A3
    u = math.lcm(a2.denominator, a4.denominator, a6.denominator)
    ainv = [Fr(0), a2 * u * u, Fr(0), a4 * u ** 4, a6 * u ** 6]
    return [int(z) for z in ainv], u, A3


def cubic_map(u_lcm, A3, m, w):
    return (A3 * m * u_lcm * u_lcm, A3 * w * u_lcm ** 3)


# --------------------------------------------------------------------------
# deg-4 route: quartic reduction at a rational base point
# --------------------------------------------------------------------------

def quartic_route(q, base_u, base_w):
    """q: quartic Fraction poly with q(base_u) = base_w^2, base_w != 0.
    Committed quartic_reduction + integral scaling + the exact closed form
    for the image R0 of the base point itself."""
    if base_w == 0:
        raise AssertionError("quartic base point has w = 0")
    D, coef = E.quartic_reduction(q, Fr(base_u), Fr(base_w))
    ainv, u_lcm, A3 = cubic_model_from_D(D)
    a, b, c, d, e = coef
    cp = c - d * d / (4 * e * e)
    m0 = cp / (2 * e)
    w0 = b - d * cp / (2 * e * e)
    if w0 * w0 != E.peval(D, m0):
        raise AssertionError("base-point closed form off the cubic D")
    R0 = cubic_map(u_lcm, A3, m0, w0)
    if not E.verify_on_curve(ainv, R0[0], R0[1]):
        raise AssertionError("base-point image off the integral curve")
    return {"ainv": ainv, "u_lcm": u_lcm, "A3": A3, "coef": coef,
            "D": D, "R0": R0, "R0_local": (m0, w0)}


def route_map(route, t, v):
    """(t, v) on the shifted quartic -> integral Weierstrass point.
    t, v may be Fr or QS (same field)."""
    m, w = E.quartic_point_to_cubic(t, v, route["coef"])
    return cubic_map(route["u_lcm"], route["A3"], m, w)


# --------------------------------------------------------------------------
# the certificate
# --------------------------------------------------------------------------

def certify_instance(inst, coset, ec, mazur_max=12, screen_max=24):
    """inst: build_instance output (b, d_pattern, r, s as strings/ints).
    coset: eligible_cosets() entry {'m0','V','members'}.
    ec: committed exact_certify module (byte-identical loader).
    Returns the certificate dict (JSON-serializable)."""
    strict = []      # IV-5-class verifier rejections
    withholds = []   # conservative unit withholds / contingency notes
    checks = []      # recorded exact checks (name, passed)

    def check(name, ok):
        checks.append({"check": name, "passed": bool(ok)})
        if not ok:
            strict.append(name)
        return ok

    b = [Fr(x) for x in inst["b"]]
    r = [Fr(x) for x in inst["r"]]
    dpat = [int(d) for d in inst["d_pattern"]]
    s = [Fr(c) for c in inst["s"]]
    n = len(b)
    deg = len(s) - 1
    if deg not in (3, 4):
        return {"verdict": "REJECTED", "reason": "deg_s_%d_outside_filter" % deg,
                "checks": checks, "errors_strict": strict}

    # ---- coset checks (IV-5): membership, distinctness, closure, Kummer ----
    V = sorted(coset["V"])
    members = sorted(coset["members"])
    mvals = [E.class_value(m) for m in members]
    sfs = [E.squarefree_part(v) for v in mvals]
    Vvals = [E.class_value(v) for v in V]
    Vsfs = {E.squarefree_part(x) for x in Vvals}
    check("V_values_subgroup_closed_contain_1",
          1 in Vsfs and len(Vsfs) == 8
          and all(E.squarefree_part(x * y) in Vsfs
                  for x in Vvals for y in Vvals))
    check("coset_member_classes_distinct_mod_squares",
          len(set(sfs)) == len(sfs))
    # coset closure: products of two members land in the V value set, and
    # member * V lands back in the member set (a coset of V in Q*/Q^2;
    # products of two members are NOT members unless m0 is trivial)
    check("coset_closed_under_multiplication_mod_squares",
          all(E.squarefree_part(x * y) in Vsfs
              for x in mvals for y in mvals)
          and all(E.squarefree_part(x * v) in set(sfs)
                  for x in mvals for v in Vvals))
    basis = []
    span = {0}
    for v in V:
        if v not in span:
            basis.append(v)
            span |= {x ^ v for x in span}
    check("direction_space_dim_3", len(basis) == 3 and sorted(span) == V)
    kummer_tests = []
    for v in V:
        if v == 0:
            continue
        val = E.class_value(v)
        nonsq = (val < 0) or (not E.is_square_int(val))
        kummer_tests.append({"v": v, "class_value": val,
                             "not_a_rational_square": bool(nonsq)})
    check("kummer_7_square_tests_[K_V:Q]=8",
          len(kummer_tests) == 7 and all(t["not_a_rational_square"]
                                         for t in kummer_tests))
    mask_of = {}
    for m in members:
        mask_of[E.class_value(m)] = m

    # ---- class grouping ----
    classes = sorted(set(dpat))
    idx_of = {d: [i for i in range(n) if dpat[i] == d] for d in classes}
    d1 = classes[0]
    for d in classes:
        check("class_%d_in_coset" % d, d in mask_of)
    if strict:
        return {"verdict": "REJECTED", "reason": "class_outside_coset",
                "checks": checks, "errors_strict": strict}
    m1 = mask_of[d1]

    # ---- per-class models + committed F_l certification ----
    models = {}
    for d in classes:
        idxs = idx_of[d]
        qd = [c / Fr(d) for c in s]
        for i in idxs:
            check("class_%d_identity_r2_eq_qd_at_b%d" % (d, i),
                  r[i] * r[i] == E.peval(qd, b[i]))
        pts = [(b[i], r[i]) for i in idxs]
        if deg == 3:
            ainv_d, imgs = E.cubic_to_weierstrass(qd, pts)
            route = None
            ainv_chk, u_chk, A3_chk = cubic_model_from_D(qd)
            check("class_%d_model_replication" % d, ainv_d == ainv_chk)
        else:
            route = quartic_route(qd, b[idxs[0]], r[idxs[0]])
            ainv_d = route["ainv"]
            imgs = [route["R0"]] + [route_map(route, b[i] - b[idxs[0]], r[i])
                                    for i in idxs[1:]]
        for j, (x, y) in enumerate(imgs):
            check("class_%d_image_%d_on_curve" % (d, j),
                  E.verify_on_curve(ainv_d, x, y))
        cert = ec.certify(ainv_d, [[str(x), str(y)] for x, y in imgs])
        check("class_%d_Fl_certifier_no_off_curve" % d,
              not cert["on_curve_failures"])
        certified = cert["certified_rank_lower_bound"]
        # Mazur witnesses on every rational image point (spec m = 1..12)
        a2, a4, a6 = Fr(ainv_d[1]), Fr(ainv_d[3]), Fr(ainv_d[4])
        mazur = []
        for (x, y) in imgs:
            P = (Fr(x), Fr(y))
            wit = {}
            torsion_hit = False
            for m in range(1, mazur_max + 1):
                nonzero = w_mul(a2, a4, a6, m, P) is not None
                wit[m] = bool(nonzero)
                if not nonzero:
                    torsion_hit = True
            mazur.append({"torsion_under_mazur_%d" % mazur_max: torsion_hit,
                          "witnesses_mP_nonzero": wit})
        models[d] = {"ainv": ainv_d, "images": imgs, "route": route,
                     "cert": cert, "certified": certified, "mazur": mazur,
                     "n_points": len(idxs)}
        if cert["errors"]:
            withholds.append({"class": d, "certifier_errors": cert["errors"]})

    # ---- base model E0', kappa' ----
    q1 = [c / Fr(d1) for c in s]
    if deg == 3:
        ainv1, u1, A31 = cubic_model_from_D(q1)
        check("base_model_replication", ainv1 == models[d1]["ainv"])
        kappa = None  # O
    else:
        route1 = models[d1]["route"]
        ainv1 = route1["ainv"]
        kappa = (Fr(route1["R0"][0]), Fr(route1["R0"][1]))
    a2_1, a4_1, a6_1 = Fr(ainv1[1]), Fr(ainv1[3]), Fr(ainv1[4])

    # ---- lifts, Psi, sigma-checks, torsion screens (nonbase classes) ----
    sigma_checks = []
    screens = []
    psi_nontorsion = {d: [] for d in classes}
    for d in classes:
        if d == d1:
            continue
        idxs = idx_of[d]
        mi = mask_of[d]
        mask_e = mi ^ m1
        e_i = E.class_value(mask_e)
        check("class_%d_e_mask_in_V" % d, mask_e in set(V))
        prod = d * d1
        e_sf = E.squarefree_part(prod)
        check("class_%d_e_two_routes_agree" % d, e_i == e_sf)
        if e_i == 1:
            check("class_%d_nontrivial" % d, False)
            continue
        f2 = abs(prod) // abs(e_i)
        f = E.isqrt_c(f2)
        check("class_%d_square_decomposition" % d, e_i * f * f == prod)
        for i in idxs:
            rho = r[i] * Fr(f) / Fr(d1)
            w_field = QS(e_i, Fr(0), rho)
            check("class_%d_point_%d_lift_identity" % (d, i),
                  w_field * w_field == Fr(E.peval(q1, b[i])))
            if deg == 3:
                X = QS(e_i, A31 * b[i] * u1 * u1, 0)
                Y = QS(e_i, Fr(0), A31 * rho * u1 ** 3)
                Phi = (X, Y)
            else:
                Phi = route_map(route1, b[i] - b[idx_of[d1][0]], w_field)
            check("class_%d_point_%d_Phi_on_curve" % (d, i),
                  w_on_curve(QS(e_i, a2_1), QS(e_i, a4_1), QS(e_i, a6_1), Phi))
            kap = None if kappa is None else (QS(e_i, kappa[0]), QS(e_i, kappa[1]))
            Psi = w_add(QS(e_i, a2_1), QS(e_i, a4_1), QS(e_i, a6_1),
                        kap, w_mul(QS(e_i, a2_1), QS(e_i, a4_1), QS(e_i, a6_1),
                                   -2, Phi))
            # diagnostic: transported involution iota' = t_{kappa'} o [-1]
            conj_Phi = (Phi[0].conj(), Phi[1].conj())
            iota_Phi = w_add(QS(e_i, a2_1), QS(e_i, a4_1), QS(e_i, a6_1),
                             w_neg(Phi), kap)
            # per-generator sigma checks
            any_flip = False
            for j, gm in enumerate(basis):
                chi = -1 if popcount(mask_e & gm) % 2 else 1
                if chi == -1:
                    any_flip = True
                    conj_Psi = (Psi[0].conj(), Psi[1].conj())
                    ok = pt_eq(conj_Psi, w_neg(Psi))
                    sigma_checks.append({"class": d, "point": i,
                                         "generator": j, "basis_mask": gm,
                                         "chi": -1, "check": "tau(Psi)==-Psi",
                                         "passed": bool(ok)})
                    if not ok:
                        strict.append("sigma_check_class_%d_point_%d_gen_%d"
                                      % (d, i, j))
                    ok2 = pt_eq(conj_Phi, iota_Phi)
                    sigma_checks.append({"class": d, "point": i,
                                         "generator": j, "basis_mask": gm,
                                         "chi": -1,
                                         "check": "tau(Phi)==-Phi+kappa (iota')",
                                         "passed": bool(ok2)})
                    if not ok2:
                        strict.append("iota_check_class_%d_point_%d_gen_%d"
                                      % (d, i, j))
                else:
                    sigma_checks.append({"class": d, "point": i,
                                         "generator": j, "basis_mask": gm,
                                         "chi": 1,
                                         "check": "identity_action_on_Q(sqrt(e))",
                                         "passed": True})
            check("class_%d_point_%d_some_generator_flips" % (d, i), any_flip)
            # torsion screen m = 1..screen_max on Psi (exact field multiples)
            hit = None
            for m in range(1, screen_max + 1):
                if w_mul(QS(e_i, a2_1), QS(e_i, a4_1), QS(e_i, a6_1),
                         m, Psi) is None:
                    hit = m
                    break
            screens.append({"class": d, "point": i, "e": e_i,
                            "screen_max": screen_max, "torsion_order_hit": hit,
                            "Psi": qs_pt_to_json(Psi),
                            "Phi": qs_pt_to_json(Phi)})
            psi_nontorsion[d].append(hit is None)
            # consistency: certified_e = 2 forces Psi-pair independence, so a
            # screen hit with certified = 2 is a verifier inconsistency
            if hit is not None and models[d]["certified"] == 2:
                strict.append("screen_certifier_inconsistency_class_%d_point_%d"
                              % (d, i))

    # ---- units, conservative aggregate ----
    per_class = {}
    aggregate_raw = 0
    eig_units = 0
    leak = False
    for d in classes:
        certified = models[d]["certified"]
        aggregate_raw += certified
        if d == d1:
            eig = 1 if certified >= 1 else 0
        else:
            eig = 1 if (certified >= 1 and any(psi_nontorsion[d])) else 0
            if certified < 2:
                leak = True
        per_class[d] = {"certified_Fl_within_class": certified,
                        "eig_unit": eig,
                        "n_forced_points": models[d]["n_points"]}
        eig_units += eig
    aggregate = aggregate_raw - (1 if leak else 0)
    fl_units = aggregate - eig_units
    if leak:
        withholds.append({
            "aggregate_deduction": 1,
            "reason": "a nonbase class certified < 2: the within-class "
                      "dependency leaks a relation into the trivial-character "
                      "equation; one unit deducted (conservative, exact)"})
    if fl_units < 0:
        withholds.append({"anomaly": "fl_units_negative_capped",
                          "eig_units": eig_units, "aggregate": aggregate})
        eig_units = aggregate
        fl_units = 0

    verdict = "PASS" if not strict else "REJECTED"
    return {
        "verdict": verdict,
        "errors_strict": strict,
        "withholds": withholds,
        "deg_s": deg,
        "route": "cubic_clean" if deg == 3 else "quartic_base_reduction",
        "kappa_prime": (str(kappa[0]), str(kappa[1])) if kappa else "O",
        "base_class": d1,
        "classes": {str(d): per_class[d] for d in classes},
        "aggregate_total": aggregate,
        "aggregate_raw_sum_certified": aggregate_raw,
        "eig_units": eig_units,
        "fl_units": fl_units,
        "rank_claim": "rank E0'(K_V) >= %d (exact, descent-free)" % aggregate,
        "kummer_tests": kummer_tests,
        "basis_masks": basis,
        "checks": checks,
        "sigma_checks": sigma_checks,
        "torsion_screens": screens,
        "a_invariants": {str(d): models[d]["ainv"] for d in classes},
        "images": {str(d): [[str(x), str(y)] for x, y in models[d]["images"]]
                   for d in classes},
        "mazur_witnesses": {str(d): models[d]["mazur"] for d in classes},
        "Fl_certifier_results": {str(d): models[d]["cert"] for d in classes},
        "exact_arithmetic_only": True,
        "no_descent_no_root_numbers_no_floats": True,
    }
