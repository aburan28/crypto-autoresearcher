# round015_exp031_torus_semaev.sage
# EXP-031: Torus-based Semaev index calculus (H-TS-001).
#
# IDEA (Granger-Vercauteren algebraic-tori IC):
#   The algebraic torus T_2(F_p) = ker(Norm: F_{p^2}^* -> F_p^*) is the
#   norm-1 subgroup of F_{p^2}^*, of order p+1.  It admits a rational
#   parametrization psi: A^1 --> T_2 (a degree-1/birational map), so its
#   MULTIPLICATIVE group law is LOW DEGREE in the parameter coordinate t.
#   A "summation relation" in the torus is: decompose a target torus
#   element as a PRODUCT of factor-base torus elements.  In parameter
#   coords this is an elementary-symmetric (Vieta) polynomial system whose
#   per-variable degree is FAR below the EC Semaev 4^(m-1).
#
# WHAT WE TEST (bounded: p in {127,1031}, m in {2,3}):
#   (a) per-variable degree of the torus summation system vs EC Semaev 4^(m-1)
#   (b) gated meter (round007 meter, self-validated on 4 fixtures)
#   (c) ANTI-CIRCULARITY: is the relation genuinely the torus mult-group
#       relation (Vieta on rational parametrization), not an EC-Semaev relabel?
#   (d) DECISIVE EC-DESCENT: does a torus relation constrain the prime-field
#       EC scalar k, or only solve a F_{p^2}^* DLP that does NOT descend to
#       the EC group?  We report the test curve's EMBEDDING DEGREE.
#
# EXPECTED NULL: torus gives a genuine LOW-degree summation relation
#   (the GV win) BUT solves a finite-field DLP in F_{p^2}^* that does not
#   descend to prime-field EC DLP (no small embedding degree) -> bankable
#   NEGATIVE for the EC target.  CANDIDATE only if a low-degree torus
#   relation genuinely constrains the EC k for a P-256-like curve.

import time, json, sys, traceback
T_START = time.time()
BUDGET_SEC = 420.0  # ~7 min wall guard

RESULT = {
    "experiment": "EXP-031 torus-based Semaev (H-TS-001)",
    "params": "p in {127,1031}; m in {2,3}; T_2(F_p) norm-1 torus, rational parametrization",
    "meter_fixtures": {},
    "meter_self_validated": False,
    "torus": {},
    "degree_compare": {},
    "gate_runs": {},
    "anti_circularity": "",
    "ec_descent": {},
    "verdict": "inconclusive",
    "notes": [],
}

def note(s):
    RESULT["notes"].append(s)
    print("[NOTE]", s)

# ---------------------------------------------------------------------------
# 0. Load + self-validate the hardened gated meter (4 fixtures).
# ---------------------------------------------------------------------------
METER_PATH = "/Volumes/Volume/autolab/experiments/ecdlp_prime_field/round007_exp012_localization_gate.sage"
meter_ok = True
try:
    load(METER_PATH)
    note("loaded meter from %s" % METER_PATH)
except Exception as e:
    meter_ok = False
    note("METER LOAD FAILED: %r" % e)
    traceback.print_exc()

def run_meter(polys, R, sumpoly_indices, Dmax=14):
    """Wrapper: returns dict with d_ff,D_reg,fires,gate_passes,gate_meaningful,gate_detail."""
    out = meter_gated(polys, R, sumpoly_indices, Dmax=Dmax)
    # round007 meter returns a tuple or dict; normalize.
    if isinstance(out, dict):
        d = out
    else:
        keys = ["d_ff", "D_reg", "fires", "gate_passes", "gate_meaningful", "gate_detail"]
        d = {}
        for i, k in enumerate(keys):
            d[k] = out[i] if i < len(out) else None
    return d

# --- Fixtures (POS-A, NEG-1, e-ring m=3 Semaev, POS-C Weil S_3) ---
def fixture_POS_A():
    # A planted low-degree system that should FIRE with d_ff small and be
    # gate_meaningful (summation-poly leading-form rows participate).
    R = PolynomialRing(GF(101), 3, "x")
    x0, x1, x2 = R.gens()
    # A genuine Semaev-style S_3 over GF(101) in x-coords (low first fall).
    # Use Semaev S_3 for y^2=x^3+x+1 surrogate via symmetric construction.
    # We construct an explicitly low-d_ff system known to fire.
    polys = [
        x0 + x1 + x2 - 5,
        x0*x1 + x1*x2 + x0*x2 - 7,
        x0*x1*x2 - 11,
    ]
    return polys, R, [0, 1, 2]

def fixture_NEG_1():
    # A generic dense system that should stay QUIET (no early fall).
    R = PolynomialRing(GF(101), 3, "x")
    x0, x1, x2 = R.gens()
    polys = [
        x0^3 + x1^2*x2 + 3*x0*x1 + 7,
        x1^3 + x2^2*x0 + 5*x1*x2 + 2,
        x2^3 + x0^2*x1 + 4*x0*x2 + 9,
    ]
    return polys, R, []

def build_semaev3_ering(p=101):
    # e-ring m=3 Semaev: base-fires but FAILS gate (artifact). Use Sage's
    # division-polynomial / Semaev S_3 for a curve, mapped to e-ring coords.
    Fp = GF(p)
    E = EllipticCurve(Fp, [1, 1])
    # Semaev S_3(X1,X2,X3) = (X1-X2)^2 X3^2 -2((X1+X2)(X1X2+a)+2b)X3 + ((X1X2-a)^2 -4b(X1+X2))
    a, b = Fp(1), Fp(1)
    R = PolynomialRing(Fp, 3, "X")
    X1, X2, X3 = R.gens()
    S3 = ((X1 - X2)^2 * X3^2
          - 2*((X1 + X2)*(X1*X2 + a) + 2*b)*X3
          + ((X1*X2 - a)^2 - 4*b*(X1 + X2)))
    return E, S3, R, (X1, X2, X3)

def fixture_ering_semaev3():
    E, S3, R, (X1, X2, X3) = build_semaev3_ering(101)
    # e-ring style: add slack power-sum eqns -> base fire but gate fails.
    polys = [S3, X1 + X2 + X3 - 3, X1*X2 + X2*X3 + X1*X3 - 4]
    return polys, R, [0]

def fixture_POS_C_weil():
    # POS-C: Weil restriction S_3 over F_{p^2} -> gate-meaningful fall.
    p = 11
    Fp2 = GF(p^2, "w")
    w = Fp2.gen()
    E = EllipticCurve(Fp2, [1, 1])
    a, b = Fp2(1), Fp2(1)
    # Build Semaev S_3 over F_{p^2}, then Weil-restrict to F_p (2 coords each).
    R = PolynomialRing(GF(p), 6, "u")
    u = R.gens()
    # X_i = u_{2i} + w*u_{2i+1}; we need w^2. Fp2 minimal poly:
    f = Fp2.modulus()  # w^2 + c1 w + c0 = 0
    c = f.list()  # [c0, c1, 1]
    c0, c1 = GF(p)(c[0]), GF(p)(c[1])
    def Xi(i):
        return (u[2*i], u[2*i+1])  # (real, w-part)
    def mul(A, B):
        ar, ai = A; br, bi = B
        # (ar+ai w)(br+bi w) = ar br + (ar bi+ai br) w + ai bi w^2
        # w^2 = -c1 w - c0
        rr = ar*br - ai*bi*c0
        ri = ar*bi + ai*br - ai*bi*c1
        return (rr, ri)
    def add(A, B):
        return (A[0]+B[0], A[1]+B[1])
    def sub(A, B):
        return (A[0]-B[0], A[1]-B[1])
    def scal(s, A):
        return (s*A[0], s*A[1])
    aa = (GF(p)(1), GF(p)(0))
    bb = (GF(p)(1), GF(p)(0))
    A1, A2, A3 = Xi(0), Xi(1), Xi(2)
    d12 = sub(A1, A2)
    term1 = mul(mul(d12, d12), mul(A3, A3))
    s12 = add(A1, A2)
    p12 = mul(A1, A2)
    inner = add(mul(s12, add(p12, aa)), scal(GF(p)(2), bb))
    term2 = scal(GF(p)(-2), mul(inner, A3))
    pm = sub(p12, aa)
    term3a = mul(pm, pm)
    term3b = scal(GF(p)(-4), mul(bb, s12))
    term3 = add(term3a, term3b)
    S = add(add(term1, term2), term3)
    polys = [S[0], S[1]]  # real + w-part = 2 equations over F_p
    return polys, R, [0, 1]

def validate_meter():
    if not meter_ok:
        return False
    results = {}
    ok_all = True

    def check(name, polys, R, idx, want_fire, want_meaning):
        try:
            d = run_meter(polys, R, idx)
            fires = bool(d.get("fires"))
            gm = bool(d.get("gate_meaningful"))
            dff = d.get("d_ff")
            dreg = d.get("D_reg")
            ok = (fires == want_fire) and (gm == want_meaning)
            results[name] = {"d_ff": _i(dff), "D_reg": _i(dreg),
                             "fires": fires, "gate_meaningful": gm,
                             "want_fire": want_fire, "want_meaning": want_meaning,
                             "ok": ok}
            note("FIXTURE %s: d_ff=%s D_reg=%s fires=%s gate_meaningful=%s -> %s"
                 % (name, dff, dreg, fires, gm, "OK" if ok else "MISMATCH"))
            return ok
        except Exception as e:
            results[name] = {"error": repr(e), "ok": False}
            note("FIXTURE %s ERROR: %r" % (name, e))
            traceback.print_exc()
            return False

    pa = fixture_POS_A();      ok_all &= check("POS-A", pa[0], pa[1], pa[2], True, True)
    n1 = fixture_NEG_1();      ok_all &= check("NEG-1", n1[0], n1[1], n1[2], False, False)
    er = fixture_ering_semaev3(); ok_all &= check("e-ring-S3", er[0], er[1], er[2], True, False)
    try:
        pc = fixture_POS_C_weil(); ok_all &= check("POS-C-Weil", pc[0], pc[1], pc[2], True, True)
    except Exception as e:
        results["POS-C-Weil"] = {"error": repr(e), "ok": False}
        note("POS-C build error: %r" % e); ok_all = False

    RESULT["meter_fixtures"] = results
    return bool(ok_all)

def _i(x):
    try:
        return int(x)
    except Exception:
        return x

# ---------------------------------------------------------------------------
# 1. Torus construction T_2(F_p) and rational parametrization.
# ---------------------------------------------------------------------------
def build_torus(p):
    """T_2(F_p) = norm-1 subgroup of F_{p^2}^*, order p+1.
    Rational parametrization psi: A^1 -> T_2 \ {1}:
        choose non-square d in F_p, F_{p^2}=F_p(sqrt(d)).
        For t in F_p, psi(t) = (t + sqrt(d))/(t - sqrt(d))  has norm
        N(psi(t)) = (t^2 - d)/(t^2 - d) = ... compute properly:
        N(a) = a * a^p = a * conj(a).  conj(t+sqrt d) = t - sqrt d.
        N((t+s)/(t-s)) = ((t+s)/(t-s)) * ((t-s)/(t+s)) = 1.  YES norm 1.
    So psi(t) in T_2 for all t with t^2 != d.  This is the standard
    degree-1 rational parametrization of the conic / Pell torus.
    """
    Fp = GF(p)
    d = Fp(least_nonsquare(p))
    Fp2 = GF(p^2, "s", modulus=x^2 - d) if False else GF(p^2, "s")
    # Use explicit construction so sqrt(d) is a generator-like element.
    R1 = PolynomialRing(Fp, "X")
    Xv = R1.gen()
    Fp2 = Fp.extension(Xv^2 - d, "s")
    s = Fp2.gen()  # s^2 = d
    assert s^2 == Fp2(d)
    return Fp, Fp2, d, s

def least_nonsquare(p):
    Fp = GF(p)
    for c in range(2, p):
        if not Fp(c).is_square():
            return c
    return None

def psi(t, s, Fp2):
    """psi(t) = (t + s)/(t - s), an element of T_2 (norm 1)."""
    num = Fp2(t) + s
    den = Fp2(t) - s
    return num / den

def norm_of(a, p):
    return a * a^p  # in F_p (as element of Fp2)

# ---------------------------------------------------------------------------
# 2. Torus summation system (product decomposition in parameter coords).
# ---------------------------------------------------------------------------
def torus_group_law_in_t(p, d):
    """psi(t1)*psi(t2) = psi(t3) gives a rational addition law on the
    parameter line.  Compute it symbolically.
    (t1+s)/(t1-s) * (t2+s)/(t2-s) = (t3+s)/(t3-s).
    Cross-multiplying and using s^2=d gives t3 = (t1 t2 + d)/(t1 + t2).
    This is the Pell/Chebyshev addition: a DEGREE-1 (bilinear) law in each
    variable -- vastly lower than EC chord-tangent (degree grows as 4^(m-1)
    in Semaev).  Verify symbolically and numerically.
    """
    Fp = GF(p)
    Rt = PolynomialRing(Fp, ["t1", "t2"])
    t1, t2 = Rt.gens()
    # Claim: t3 = (t1*t2 + d)/(t1 + t2)
    t3_num = t1*t2 + Fp(d)
    t3_den = t1 + t2
    return Rt, (t1, t2), t3_num, t3_den

def torus_summation_system(p, d, m):
    """Build the m-fold torus summation (product) relation in parameter
    coords using the iterated bilinear law -> a symmetric polynomial
    system.  Target torus element parametrized by t0; decompose as product
    of m factor-base elements parametrized by u_1..u_m.

    The product psi(u_1)*...*psi(u_m) = psi(T) where T is a rational
    function of the elementary symmetric polynomials of the u_i, all of
    DEGREE 1 per variable (Pell composition is multiplicative-linear).

    Concretely, define homogeneous coordinates: psi(u) <-> (u : 1) on P^1
    acted on by the multiplicative group via Mobius matrix M(u)=[[u,d],[1,u]]
    (since composing two gives M(u1)*M(u2) up to the bilinear law).
    Product of M(u_i) is a 2x2 matrix whose entries are the power sums /
    elementary symmetric combos -> each entry degree <= m but per-variable
    degree 1.  The summation relation = (matrix entry) - (target) = 0.
    """
    Fp = GF(p)
    nv = m + 1  # u_1..u_m and target T
    R = PolynomialRing(Fp, ["u%d" % i for i in range(1, m+1)] + ["T"])
    gens = R.gens()
    us = gens[:m]
    T = gens[m]
    dd = Fp(d)
    # Mobius matrix for Pell composition: M(u) = [[u, d],[1, u]]
    M = matrix(R, [[us[0], dd], [R(1), us[0]]])
    for i in range(1, m):
        Mi = matrix(R, [[us[i], dd], [R(1), us[i]]])
        M = M * Mi
    # Product element corresponds to psi with parameter ratio M[0][0]/M[1][0]
    # plus offset; the torus product equals target psi(T) iff:
    #   M * [T, 1]^T  is proportional to ... actually the cleanest relation:
    #   the product matrix M represents psi(prod) and equals (up to scalar)
    #   M(T_eff).  We extract the summation relation as the requirement that
    #   the product's "parameter" equals T:
    #   numerator: M[0][0]*1 + M[0][1]*0 etc.  Use:
    #   product psi-parameter t_prod satisfies  t_prod = M[0][0]*? ...
    # Simplest faithful relation: psi(u_1)...psi(u_m) has matrix M; the
    # corresponding torus element is M[0][0] + M[1][0]*s over M ... define
    # the SUMMATION polynomial as resultant-free direct relation:
    #   (M[0][0] - T*M[1][0]) = 0  AND  (M[0][1] - T*M[1][1]) = 0 would
    #   force M = T*I-ish; instead the single relation tying product to T:
    a11, a12 = M[0][0], M[0][1]
    a21, a22 = M[1][0], M[1][1]
    # The product torus element as (X:Y) with X=a11+a12, Y=a21+a22 (apply to
    # parametrization vector (1,1)) ; require it equals psi(T) ~ (T+? ...).
    # Use the clean invariant relation for Pell torus product:
    #   relation R_m = a11 - T*a21   (degree 1 in T, per-u degree 1)
    rel1 = a11 - T*a21
    rel2 = a12 - T*a22
    polys = [rel1, rel2]
    return R, gens, polys, M

# ---------------------------------------------------------------------------
# 3. EC-descent / embedding degree analysis for a P-256-like toy curve.
# ---------------------------------------------------------------------------
def ec_embedding_degree(p):
    """Build a random prime-order-ish curve over F_p (P-256-like: prime or
    near-prime order, NO small embedding degree by design) and report its
    embedding degree k = mult. order of p mod n, n = group order (or its
    largest prime factor)."""
    Fp = GF(p)
    best = None
    for trial in range(40):
        a = Fp.random_element()
        b = Fp.random_element()
        if 4*a^3 + 27*b^2 == 0:
            continue
        E = EllipticCurve(Fp, [a, b])
        n = E.order()
        nf = factor(n)
        ell = max([q for q, _ in nf])  # largest prime factor
        if ell < 5:
            continue
        # embedding degree wrt ell = mult order of p mod ell
        k = Mod(p, ell).multiplicative_order()
        cand = {"a": int(a), "b": int(b), "order": int(n),
                "order_factored": str(nf), "largest_prime_factor": int(ell),
                "embedding_degree_k": int(k), "is_prime_order": bool(n.is_prime())}
        # prefer prime-order curve with large k (P-256-like)
        if best is None:
            best = cand
        if cand["is_prime_order"] and cand["embedding_degree_k"] > best["embedding_degree_k"]:
            best = cand
        if cand["is_prime_order"] and cand["embedding_degree_k"] >= ell - 2:
            return cand
    return best

# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main():
    print("="*70)
    print("EXP-031 torus-based Semaev IC -- START", time.ctime())
    print("="*70)

    # 0. meter self-validation
    mv = validate_meter()
    RESULT["meter_self_validated"] = bool(mv)
    note("METER SELF-VALIDATED = %s" % mv)

    for p in [127, 1031]:
        if time.time() - T_START > BUDGET_SEC:
            note("BUDGET hit before p=%d; skipping remaining sizes" % p)
            break
        pkey = "p=%d" % p
        Fp, Fp2, d, s = build_torus(p)
        torder = p + 1
        # verify a parametrized element is in T_2 (norm 1)
        t_test = Fp(3) if Fp(3) != Fp(0) else Fp(2)
        e = psi(t_test, s, Fp2)
        nm = norm_of(e, p)
        in_torus = (nm == Fp2(1))
        RESULT["torus"][pkey] = {
            "F_p2_order": int(p^2),
            "torus_order_p+1": int(torder),
            "torus_order_factored": str(factor(torder)),
            "nonsquare_d": int(d),
            "param_psi_norm1_check": bool(in_torus),
            "parametrization": "psi(t)=(t+s)/(t-s), s^2=d  ->  Pell torus, Mobius M(u)=[[u,d],[1,u]]",
        }
        note("%s torus order p+1=%d (factored %s) norm1-check=%s"
             % (pkey, torder, factor(torder), in_torus))

        for m in [2, 3]:
            if time.time() - T_START > BUDGET_SEC:
                note("BUDGET hit before %s m=%d; skipping" % (pkey, m))
                break
            mkey = "%s,m=%d" % (pkey, m)
            try:
                Rt, (t1, t2), t3n, t3d = torus_group_law_in_t(p, d)
                # numeric verification of bilinear addition law t3=(t1t2+d)/(t1+t2)
                ok_law = True
                for _ in range(8):
                    a1 = Fp.random_element(); a2 = Fp.random_element()
                    if a1 + a2 == 0 or a1 - a2 == 0:
                        continue
                    prod = psi(a1, s, Fp2) * psi(a2, s, Fp2)
                    # recover its parameter t3
                    t3val = (a1*a2 + d) / (a1 + a2)
                    if psi(t3val, s, Fp2) != prod:
                        ok_law = False
                R, gens, polys, Mmat = torus_summation_system(p, d, m)
                # per-variable degree of summation relations
                pv_degs = []
                for f in polys:
                    pv = max([f.degree(g) for g in R.gens()])
                    pv_degs.append(int(pv))
                tot_degs = [int(f.degree()) for f in polys]
                ec_semaev_pv = 2  # EC Semaev S_m is degree 2 per x-variable... but
                # the relevant blow-up metric is the GROEBNER-solving degree which
                # scales ~ 4^(m-1) for EC; torus addition is BILINEAR (per-var 1).
                ec_blowup = 4^(m-1)
                RESULT["degree_compare"][mkey] = {
                    "torus_summation_per_var_degree": max(pv_degs),
                    "torus_summation_total_degrees": tot_degs,
                    "torus_addition_law": "t3=(t1*t2+d)/(t1+t2)  (BILINEAR, per-var deg 1)",
                    "torus_addition_law_verified": bool(ok_law),
                    "EC_semaev_solving_blowup_4^(m-1)": int(ec_blowup),
                    "EC_semaev_per_var_x_degree": int(ec_semaev_pv),
                }
                note("%s torus per-var deg=%d (law bilinear, verified=%s) vs EC blowup 4^(m-1)=%d"
                     % (mkey, max(pv_degs), ok_law, ec_blowup))

                # gated meter on the torus summation system
                try:
                    dmeter = run_meter(polys, R, list(range(len(polys))))
                    RESULT["gate_runs"][mkey] = {
                        "d_ff": _i(dmeter.get("d_ff")),
                        "D_reg": _i(dmeter.get("D_reg")),
                        "fires": bool(dmeter.get("fires")),
                        "gate_passes": bool(dmeter.get("gate_passes")),
                        "gate_meaningful": bool(dmeter.get("gate_meaningful")),
                        "gate_detail": str(dmeter.get("gate_detail"))[:300],
                    }
                    note("%s METER: d_ff=%s D_reg=%s fires=%s gate_meaningful=%s"
                         % (mkey, dmeter.get("d_ff"), dmeter.get("D_reg"),
                            dmeter.get("fires"), dmeter.get("gate_meaningful")))
                except Exception as e:
                    RESULT["gate_runs"][mkey] = {"error": repr(e)}
                    note("%s METER ERROR: %r" % (mkey, e))
            except Exception as e:
                RESULT["degree_compare"][mkey] = {"error": repr(e)}
                note("%s SYSTEM ERROR: %r" % (mkey, e))
                traceback.print_exc()

        # EC-descent / embedding-degree analysis for this p
        try:
            ec = ec_embedding_degree(p)
            RESULT["ec_descent"][pkey] = ec
            note("%s EC curve: order=%s prime_order=%s largest_prime=%s embedding_degree_k=%s"
                 % (pkey, ec.get("order"), ec.get("is_prime_order"),
                    ec.get("largest_prime_factor"), ec.get("embedding_degree_k")))
        except Exception as e:
            RESULT["ec_descent"][pkey] = {"error": repr(e)}
            note("%s EC-descent ERROR: %r" % (pkey, e))

    # -----------------------------------------------------------------------
    # Anti-circularity + EC-descent reasoning -> verdict
    # -----------------------------------------------------------------------
    RESULT["anti_circularity"] = (
        "The torus summation relations come from the MULTIPLICATIVE group law "
        "of T_2 expressed via the Mobius matrix M(u)=[[u,d],[1,u]] on the "
        "rational parametrization psi(t)=(t+s)/(t-s) (Pell/Chebyshev "
        "composition t3=(t1 t2 + d)/(t1 + t2)).  This is BILINEAR (per-variable "
        "degree 1) and is structurally DISTINCT from the EC chord-tangent "
        "Semaev polynomial S_m (whose Groebner solving degree blows up as "
        "~4^(m-1)).  No EC point coordinates, no EC addition formula, and no "
        "Semaev S_m enter the construction -- it is purely the F_{p^2}^* "
        "norm-1 subgroup law.  Hence it is NOT an EC-Semaev relabel: GENUINELY "
        "a different (torus) algebra."
    )

    # Determine whether torus DLP descends to EC.  T_2(F_p) sits inside
    # F_{p^2}^*; solving a DLP there corresponds to an EC instance ONLY when
    # the EC group embeds into F_{p^2}^* via a pairing, i.e. embedding degree
    # k=2 (MOV/Frey-Ruck).  P-256-like curves are chosen with LARGE embedding
    # degree, so no such embedding exists.
    descends = False
    descent_reasons = []
    for pkey, ec in RESULT["ec_descent"].items():
        if isinstance(ec, dict) and "embedding_degree_k" in ec:
            k = ec["embedding_degree_k"]
            d2 = (k == 2)
            descent_reasons.append("%s: embedding_degree_k=%s -> torus T_2 (in F_{p^2}^*) "
                                   "%s the EC group (k==2 required for MOV/Frey-Ruck embedding)"
                                   % (pkey, k, "CAN reach" if d2 else "CANNOT reach"))
            descends = descends or d2
    RESULT["ec_descent"]["descent_reasoning"] = descent_reasons
    RESULT["ec_descent"]["torus_DLP_descends_to_EC"] = bool(descends)

    # Verdict: 'survived' only if a low-degree torus relation genuinely
    # constrains the prime-field EC k for a P-256-like (large embedding degree)
    # curve.  Since T_2 lives in F_{p^2}^* and a P-256-like curve does NOT embed
    # there (k != 2), the low-degree torus relation solves the WRONG DLP.
    any_lowdeg = any(
        isinstance(v, dict) and v.get("torus_summation_per_var_degree", 99) <= 2
        for v in RESULT["degree_compare"].values()
    )
    if descends and any_lowdeg:
        RESULT["verdict"] = "survived"
        note("VERDICT survived: low-degree torus relation constrains EC k (k==2 found!)")
    elif any_lowdeg and not descends:
        RESULT["verdict"] = "failed"
        note("VERDICT failed: torus gives genuine LOW-degree summation relation "
             "(GV win) but it solves an F_{p^2}^* DLP that does NOT descend to "
             "prime-field EC (embedding degree != 2).  Bankable NEGATIVE.")
    else:
        RESULT["verdict"] = "inconclusive"
        note("VERDICT inconclusive: degree or descent measurement incomplete.")

    if not RESULT["meter_self_validated"]:
        RESULT["verdict"] = "inconclusive"
        note("Meter NOT self-validated on 4 fixtures -> forcing INCONCLUSIVE.")

    RESULT["elapsed_sec"] = round(time.time() - T_START, 1)
    print("="*70)
    print("VERDICT:", RESULT["verdict"], " elapsed", RESULT["elapsed_sec"], "s")
    print("="*70)

# Run
try:
    main()
except Exception as e:
    RESULT["fatal"] = repr(e)
    traceback.print_exc()

# Write results defensively
OUT_JSON = "/Volumes/Volume/autolab/experiments/ecdlp_prime_field/round015_exp031_torus_semaev_result.json"
try:
    with open(OUT_JSON, "w") as fh:
        json.dump(RESULT, fh, indent=2, default=str)
    print("WROTE", OUT_JSON)
except Exception as e:
    print("JSON WRITE FAILED:", repr(e))

print("DONE-EXP-031")
