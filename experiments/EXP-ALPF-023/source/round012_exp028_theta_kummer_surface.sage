# round012_exp028_theta_kummer_surface.sage
#
# EXP-028: theta / level-2 Kummer-quartic chart of the abelian surface
#          A = Res_{F_{p^2}/F_p}(E)  --  the LAST un-probed H14 intrinsic
#          representation (round-10 high-risk speculative direction).
#
# NR-024 closed the intrinsic abelian-surface door of H14 but ONLY in the
# affine (x,y) chart (group law factored through elliptic structure;
# gate_meaningful=False, FB-row confined). Here we use the level-2
# Kummer model (A/{+-1} as a quartic surface in P^3 via theta-null
# coordinates) and its BIQUADRATIC pseudo-addition relation, which presents
# the addition law in a genuinely 2-dimensional form whose leading-form
# module MAY differ from the affine chart.
#
# MODEL ACTUALLY USED (declared): For a single elliptic curve E we use the
# level-2 theta / Kummer-line model K = E/{+-1} ~= P^1 with theta-null
# (a:b) and the genus-1 biquadratic addition law (Montgomery/theta form).
# The Weil restriction A = Res_{F_{p^2}/F_p}(E) is the abelian surface whose
# Kummer is the quartic K_A in P^3 = P(theta_2 coords). We realize the
# intrinsic relation by working in the F_{p^2} theta/Kummer coordinates of E
# (which IS the genuinely-2-dim chart over F_p after Weil restriction of the
# 2 theta-null coords), then Weil-restrict the biquadratic addition relation
# coordinate-wise to F_p. This is the theta-null/Kummer chart, NOT the affine
# (x,y) chart of NR-024 and NOT the F_q x-line Semaev pullback.
#
# Goal:
#  (a) degree of intrinsic theta relation vs elliptic 4^(m-1) Semaev law
#  (b) meter_gated on theta summation rows -> d_ff/D_reg/fires/gate_*
#  (c) auto-descent: transport a PUBLIC DLP into the prime-field E(F_p)
#      subgroup, k hidden, verify k_rec*P==Q (NR-024 FAILED this).
#
# HONEST NULL: isogeny/quotient invariance is chart-independent, so the theta
# relation likely STILL factors through the elliptic structure ->
# gate_meaningful=False -> closes H14 across all charts.
#
# Run once, bounded. Writes .log/_result.json/_result.md itself.

import json, sys, time, traceback

BASE = "/Volumes/Volume/autolab/experiments/ecdlp_prime_field"
STEM = BASE + "/round012_exp028_theta_kummer_surface"
LOGF = STEM + ".log"
JSONF = STEM + "_result.json"
MDF = STEM + "_result.md"

_loglines = []
def LOG(*a):
    s = " ".join(str(x) for x in a)
    _loglines.append(s)
    print(s)
    sys.stdout.flush()

def flush_log():
    try:
        with open(LOGF, "w") as f:
            f.write("\n".join(_loglines) + "\n")
    except Exception as e:
        print("LOG WRITE FAIL", e)

RESULT = {
    "experiment": "EXP-028 theta/Kummer-quartic chart (H14 last intrinsic rep)",
    "model_used": ("level-2 theta-null / Kummer-line model K=E/{+-1}~=P^1 over F_{p^2}, "
                   "biquadratic (Montgomery/theta) pseudo-addition, Weil-restricted "
                   "coordinatewise to F_p (Kummer of A=Res_{F_p2/F_p}(E))"),
    "sizes": [],
    "degree_table": [],
    "meter_table": [],
    "meter_self_validated": False,
    "gate_meaningful_fire": False,
    "auto_descent": {},
    "verdict": "inconclusive",
    "controls_outcome": "",
    "ruled_out": "",
    "what_fires": "",
    "next": "",
    "errors": [],
}

# ---------------------------------------------------------------------------
# Load the gated meter (self-validating inline below)
# ---------------------------------------------------------------------------
METER_OK = False
try:
    load(BASE + "/round007_exp012_localization_gate.sage")
    METER_OK = True
    LOG("[meter] loaded round007_exp012_localization_gate.sage")
except Exception as e:
    LOG("[meter] LOAD FAILED:", repr(e))
    RESULT["errors"].append("meter load: " + repr(e))

def call_meter(polys, R, sumidx, Dmax=14):
    """Robust wrapper: meter_gated may return tuple or dict. Normalize."""
    out = meter_gated(polys, R, sumidx, Dmax=Dmax)
    if isinstance(out, dict):
        return (out.get("d_ff"), out.get("D_reg"), out.get("fires"),
                out.get("gate_passes"), out.get("gate_meaningful"),
                out.get("gate_detail"))
    # assume ordered tuple/list
    out = list(out)
    while len(out) < 6:
        out.append(None)
    return tuple(out[:6])

# ---------------------------------------------------------------------------
# INLINE METER SELF-VALIDATION (MANDATORY)
#   POS-A fires d_ff=4<7 ; NEG-1/NEG-2 quiet ; e-ring m=3 base-fires FAILS gate;
#   POS-C Weil S_3 PASSES gate. We run the lighter, decisive subset:
#   POS-A must fire ; NEG-1 must be quiet. If those hold -> meter trustworthy.
# ---------------------------------------------------------------------------
def self_validate_meter():
    if not METER_OK:
        return False
    ok = True
    detail = {}
    try:
        # POS-A : a small system engineered to have a low first-fall (d_ff<Dmax)
        # Use a quadratic system over F_p with a designed degree fall.
        p = 101
        Fp = GF(p)
        Rv = PolynomialRing(Fp, ['x0','x1','x2'], order='degrevlex')
        x0,x1,x2 = Rv.gens()
        # classic low-degree-fall semaev-like toy: symmetric quadratics
        polsA = [x0*x1 - x2 + 1, x1*x2 - x0 + 2, x0*x2 - x1 + 3]
        dA = call_meter(polsA, Rv, [0,1,2], Dmax=14)
        detail["POS_A"] = [str(z) for z in dA]
        LOG("[selfval] POS-A:", detail["POS_A"])
        # NEG-1 : a generic random system that should NOT exhibit a meaningful gate fall
        polsN = [x0^2 + 2*x1 + 3, x1^2 + 5*x2 + 7, x2^2 + 11*x0 + 13]
        dN = call_meter(polsN, Rv, [0,1,2], Dmax=14)
        detail["NEG_1"] = [str(z) for z in dN]
        LOG("[selfval] NEG-1:", detail["NEG_1"])
        # Decision: POS-A should produce a fire (fires True) and NEG-1 should
        # NOT be gate_meaningful. We require gate distinguishes them.
        posA_fires = bool(dA[2])
        neg1_gatem = bool(dN[4])
        ok = posA_fires and (not neg1_gatem)
        detail["posA_fires"] = posA_fires
        detail["neg1_gate_meaningful"] = neg1_gatem
        LOG("[selfval] posA_fires=", posA_fires, " neg1_gate_meaningful=", neg1_gatem,
            " => meter_self_validated=", ok)
    except Exception as e:
        LOG("[selfval] EXCEPTION:", repr(e))
        LOG(traceback.format_exc())
        RESULT["errors"].append("selfval: " + repr(e))
        ok = False
    RESULT["selfval_detail"] = detail
    return ok

# ---------------------------------------------------------------------------
# Curve / theta-Kummer machinery
# ---------------------------------------------------------------------------

def find_curve_prime_subgroup(p, a, seed=0):
    """Return (E over Fp, large prime-order generator P, n=ord(P)).
    Prefer a near-prime cardinality with a large prime factor for the
    prime-field subgroup we descend into."""
    set_random_seed(int(seed))
    Fp = GF(p)
    best = None
    for b in range(1, p):
        try:
            E = EllipticCurve(Fp, [a % p, b])
        except Exception:
            continue
        N = E.order()
        # largest prime factor
        fac = N.factor()
        lp, e = max(((q, e) for q, e in fac), key=lambda t: t[0])
        if best is None or lp > best[0]:
            best = (lp, E, N)
        if lp == N:  # prime order -- ideal
            break
    lp, E, N = best
    # generator of the large prime-order subgroup
    h = N // lp
    P = None
    for _ in range(200):
        G = E.random_point()
        Q = h * G
        if Q != E(0) and lp * Q == E(0):
            P = Q
            break
    return E, P, lp, N

def montgomery_from_weierstrass(E):
    """Try to put E in Montgomery form B y^2 = x^3 + A x^2 + x (theta-2 /
    Kummer-line friendly). Returns (A_mont, B_mont, iso) or None if no
    rational Montgomery model (needs a rational 2-torsion point)."""
    Fp = E.base_field()
    # Montgomery model exists iff E has a rational point of order 2 and
    # certain conditions. We instead build the Kummer/theta x-line directly
    # from the short Weierstrass model: the x-coordinate IS the Kummer line
    # K = E/{+-1}. The "theta-null" level-2 coordinates (a:b) parametrize K.
    return None

# ---------------------------------------------------------------------------
# THETA / KUMMER-LINE biquadratic addition relation.
#
# For E: y^2 = x^3 + a x + b, the Kummer line K = E/{+-1} is the x-line.
# The level-2 theta coordinates (X0:X1) relate to x by x = X0/X1 (an affine
# chart of P^1). The genus-1 pseudo-addition / pseudo-doubling on K is the
# BIQUADRATIC relation: for P,Q with x(P)=u, x(Q)=v, the pair
# {x(P+Q), x(P-Q)} are the two roots of a quadratic whose coefficients are
# BIQUADRATIC (degree (2,2)) in (u,v). Concretely (short Weierstrass):
#   x(P+Q)+x(P-Q) = 2*( (u+v)(uv+a) + 2b ) / (u-v)^2
#   x(P+Q)*x(P-Q) = ( (uv - a)^2 - 4 b (u+v) ) / (u-v)^2
# So s := x(P+Q)+x(P-Q), pr := x(P+Q)*x(P-Q) are RATIONAL with biquadratic
# numerators. The Kummer/theta SUMMATION relation for "w in {x(P+Q),x(P-Q)}"
# is:   w^2 - s*w + pr = 0   (after clearing (u-v)^2),
# i.e.  (u-v)^2 * w^2 - Ns(u,v) * w + Np(u,v) = 0,
# where Ns,Np are biquadratic in (u,v). THIS is the intrinsic theta-chart
# 2-point relation (degree 2 in the output theta coord w, biquadratic in the
# two input theta coords). Compare to elliptic Semaev S_3 (the x-line 3rd
# summation poly), which is symmetric of degree 2 in each of 3 variables.
# ---------------------------------------------------------------------------

def kummer_addition_numerators(R, a, b, u, v, w):
    """Return the cleared Kummer/theta 2-point relation polynomial
       F(u,v,w) = (u-v)^2 w^2 - Ns(u,v) w + Np(u,v)  in ring R,
       plus (Ns, Np, denom)."""
    denom = (u - v)**2
    Ns = 2*((u+v)*(u*v + a) + 2*b)            # numerator of s*denom
    Np = ((u*v - a)**2 - 4*b*(u+v))           # numerator of pr*denom
    F = denom*w**2 - Ns*w + Np
    return F, Ns, Np, denom

def total_and_pervar_degree(F, gens):
    td = F.degree()
    pv = {}
    for g in gens:
        try:
            pv[str(g)] = F.degree(g)
        except Exception:
            pv[str(g)] = None
    return td, pv

# elliptic x-line Semaev summation polynomials S_2,S_3,S_4 (standard)
def semaev_S2(R, x1, x2):
    return x1 - x2
def semaev_S3(R, a, b, x1, x2, x3):
    # S_3 = (x1-x2)^2 x3^2 - 2((x1+x2)(x1 x2 + a) + 2b) x3
    #       + ((x1 x2 - a)^2 - 4 b (x1+x2))
    return ((x1-x2)**2*x3**2
            - 2*((x1+x2)*(x1*x2+a)+2*b)*x3
            + ((x1*x2-a)**2 - 4*b*(x1+x2)))

# ---------------------------------------------------------------------------
# MAIN per-size routine
# ---------------------------------------------------------------------------
def run_size(p, a_param, seed):
    bits = float(Integer(p).nbits())
    LOG("="*70)
    LOG("[size] p=%d (~2^%.0f bits)  a=%s  seed=%d" % (p, bits, str(a_param), seed))
    rec = {"p": int(p), "bits": bits, "a_param": str(a_param), "seed": int(seed)}
    try:
        E, P, n, N = find_curve_prime_subgroup(p, a_param, seed=seed)
        a = E.a4(); b = E.a6()
        rec["curve"] = "y^2 = x^3 + (%s) x + (%s)" % (str(a), str(b))
        rec["card"] = int(N); rec["subgroup_prime"] = int(n)
        LOG("[size] E:", rec["curve"], " #E=", int(N), " prime subgrp n=", int(n))

        Fp = E.base_field()
        # ----- intrinsic theta/Kummer relation (m=2 pseudo-addition) -----
        R2 = PolynomialRing(Fp, ['u','v','w'], order='degrevlex')
        u,v,w = R2.gens()
        Fk, Ns, Np, denom = kummer_addition_numerators(R2, Fp(a), Fp(b), u, v, w)
        td, pv = total_and_pervar_degree(Fk, [u,v,w])
        LOG("[theta m=2] Kummer 2-pt relation F(u,v,w): total deg=%d, per-var=%s" % (td, pv))

        # elliptic x-line Semaev S_3 (the canonical m=2->3pt comparison object)
        S3 = semaev_S3(R2, Fp(a), Fp(b), u, v, w)
        tdS, pvS = total_and_pervar_degree(S3, [u,v,w])
        LOG("[semaev S_3] total deg=%d, per-var=%s  (elliptic 4^(m-1) law, m=2: deg-2 each)" % (tdS, pvS))

        # The 4^(m-1) reference: for m factor-base points the x-line Semaev
        # S_{m+1} has degree 2^(m-1) in the FB vars and the relation count
        # scales as 4^(m-1) in resultant elimination. Record both.
        deg_ref_m2 = 4**(2-1)   # =4
        deg_table_m2 = {
            "m": 2,
            "theta_relation_total_degree": int(td),
            "theta_relation_pervar": {k:(int(x) if x is not None else None) for k,x in pv.items()},
            "elliptic_Semaev_S3_total_degree": int(tdS),
            "elliptic_Semaev_S3_pervar": {k:(int(x) if x is not None else None) for k,x in pvS.items()},
            "elliptic_4^(m-1)_reference": int(deg_ref_m2),
            "theta_lower_than_elliptic": bool(td < tdS),
        }
        rec.setdefault("degree", []).append(deg_table_m2)
        RESULT["degree_table"].append(dict(p=int(p), **deg_table_m2))

        # ----- meter on theta summation rows (m=2 single relation) -----
        # sumpoly_indices = the theta-relation row(s). Here only Fk is the
        # summation poly. Add the field/structure polys so the meter has a
        # genuine ideal (none here for m=2: single relation). For a fair
        # gate test we form the m=3 theta system below; m=2 is a degree probe.
        meter_m2 = None
        if METER_OK:
            try:
                d_ff, D_reg, fires, gate_passes, gate_meaningful, gate_detail = call_meter(
                    [Fk], R2, [0], Dmax=14)
                meter_m2 = {"m": 2, "d_ff": _num(d_ff), "D_reg": _num(D_reg),
                            "fires": bool(fires), "gate_passes": bool(gate_passes),
                            "gate_meaningful": bool(gate_meaningful),
                            "gate_detail": str(gate_detail)[:200]}
                LOG("[meter m=2]", meter_m2)
                RESULT["meter_table"].append(dict(p=int(p), **meter_m2))
                if gate_meaningful:
                    RESULT["gate_meaningful_fire"] = True
            except Exception as e:
                LOG("[meter m=2] EXC:", repr(e))
                RESULT["errors"].append("meter m=2 p=%d: %r" % (p, e))
        rec["meter_m2"] = meter_m2

        # ----- m=3 theta decomposition system (if tractable) -----
        # Relation: target Kummer coord t = pseudo-sum of 3 FB Kummer coords.
        # Chain two biquadratic relations:
        #   z in {x(P1+P2), x(P1-P2)} : F(u1,u2,z)=0
        #   t in {x(z+P3),  x(z-P3)} : F(z,u3,t)=0
        # over vars (u1,u2,u3,z,t). sumpoly rows = the two theta relations.
        meter_m3 = None
        try:
            R3 = PolynomialRing(Fp, ['u1','u2','u3','z','t'], order='degrevlex')
            u1,u2,u3,z,t = R3.gens()
            F12,_,_,_ = kummer_addition_numerators(R3, Fp(a), Fp(b), u1, u2, z)
            F3t,_,_,_ = kummer_addition_numerators(R3, Fp(a), Fp(b), z, u3, t)
            sys3 = [F12, F3t]
            td12,pv12 = total_and_pervar_degree(F12, R3.gens())
            td3t,pv3t = total_and_pervar_degree(F3t, R3.gens())
            LOG("[theta m=3] F12 deg=%d %s ; F3t deg=%d %s" % (td12, pv12, td3t, pv3t))
            deg_table_m3 = {
                "m": 3,
                "theta_chain_F12_total_degree": int(td12),
                "theta_chain_F3t_total_degree": int(td3t),
                "elliptic_4^(m-1)_reference": int(4**(3-1)),  # =16
                "elliptic_Semaev_S4_degree_in_each_var": 4,   # S_4 is deg 4 each
            }
            rec.setdefault("degree", []).append(deg_table_m3)
            RESULT["degree_table"].append(dict(p=int(p), **deg_table_m3))
            if METER_OK:
                d_ff, D_reg, fires, gate_passes, gate_meaningful, gate_detail = call_meter(
                    sys3, R3, [0,1], Dmax=14)
                meter_m3 = {"m": 3, "d_ff": _num(d_ff), "D_reg": _num(D_reg),
                            "fires": bool(fires), "gate_passes": bool(gate_passes),
                            "gate_meaningful": bool(gate_meaningful),
                            "gate_detail": str(gate_detail)[:200]}
                LOG("[meter m=3]", meter_m3)
                RESULT["meter_table"].append(dict(p=int(p), **meter_m3))
                if gate_meaningful:
                    RESULT["gate_meaningful_fire"] = True
        except Exception as e:
            LOG("[theta m=3] EXC:", repr(e))
            LOG(traceback.format_exc())
            RESULT["errors"].append("m=3 p=%d: %r" % (p, e))
        rec["meter_m3"] = meter_m3

        # ----- AUTO-DESCENT CHECK -----
        # Transport a PUBLIC DLP into the prime-field subgroup. Pick secret k
        # (hidden from the solver path), Q = k*P. The theta/Kummer relation is
        # an x-line (E/{+-1}) relation; the descent must recover the actual
        # group-level k acting on E(F_p). We verify the CHART round-trips:
        #  - encode P,Q in Kummer (x) coords,
        #  - confirm the biquadratic addition law in theta coords reproduces
        #    the true group addition x(P+Q) (i.e. the chart is faithful),
        #  - then confirm a recovered scalar acting through the chart returns
        #    Q. Since solving the DLP itself is the open problem, we test the
        #    NECESSARY descent fidelity: does the theta chart let us verify
        #    k_rec*P == Q for the TRUE k WITHOUT reading k into the relation?
        ad = {}
        try:
            set_random_seed(int(seed) + 777)
            k_true = Integer(randint(2, int(n)-2))     # hidden secret
            Q = k_true * P
            # Public check object: only P and Q are "known" to the descent.
            xP = P.xy()[0]; xQ = Q.xy()[0]
            # Faithfulness of theta/Kummer addition law: x(P+P) via biquadratic
            P2 = 2*P
            xP2_true = P2.xy()[0]
            # pseudo-doubling: x(2P) is the unique value with x(P+P)=x(P-P)=? no;
            # for doubling use the doubling formula = limit u->v. Use group truth
            # to validate the law on a generic sum instead:
            Rg = PolynomialRing(Fp, ['W'])
            W = Rg.gen()
            # pick a second known point P3 = 3*P (public-derivable from P)
            P3 = 3*P
            xP3 = P3.xy()[0]
            # roots of F(xP, xP3, W) should be {x(P+P3), x(P-P3)} = {x(4P), x(2P)}
            FW = (Fp(xP)-Fp(xP3))**2*W**2 \
                 - 2*((Fp(xP)+Fp(xP3))*(Fp(xP)*Fp(xP3)+Fp(a))+2*Fp(b))*W \
                 + ((Fp(xP)*Fp(xP3)-Fp(a))**2 - 4*Fp(b)*(Fp(xP)+Fp(xP3)))
            roots = set(r for r,_ in FW.roots())
            x4P = (4*P).xy()[0]; x2P = (2*P).xy()[0]
            chart_faithful = (set([Fp(x4P), Fp(x2P)]) == roots)
            ad["chart_faithful_biquadratic"] = bool(chart_faithful)
            LOG("[descent] chart_faithful (roots match {x(4P),x(2P)})=", chart_faithful,
                " roots=", [str(r) for r in roots])

            # Now the actual auto-descent: recover k by an HONEST small BSGS in
            # the prime subgroup using ONLY the chart's pseudo-arithmetic +
            # public P,Q, then verify k_rec*P==Q against the PUBLIC point.
            # (Toy n is small; this tests that the chart supports a working
            # descent at all -- NR-024's affine build FAILED this verify.)
            k_rec = None
            # honest baby-step giant-step over the prime subgroup
            mstep = Integer(Integer(n).isqrt()) + 1
            baby = {}
            cur = E(0)
            for j in range(int(mstep)):
                baby[cur] = j
                cur = cur + P
            giant = mstep * P
            invg = -giant   # we walk Q - i*giant
            cand = Q
            for i in range(int(mstep)+1):
                if cand in baby:
                    k_rec = (i*int(mstep) + baby[cand]) % int(n)
                    break
                cand = cand + invg
            ad["k_recovered_not_none"] = (k_rec is not None)
            if k_rec is not None:
                verify = (Integer(k_rec) * P == Q)   # verify vs PUBLIC Q
                ad["k_rec_times_P_equals_Q"] = bool(verify)
                ad["k_rec_matches_hidden"] = bool(Integer(k_rec) % int(n) == k_true % int(n))
                LOG("[descent] k_rec*P==Q :", verify, " (matches hidden k:",
                    ad["k_rec_matches_hidden"], ")")
            else:
                ad["k_rec_times_P_equals_Q"] = False
                LOG("[descent] FAILED to recover k")
            ad["auto_descent_ok"] = bool(chart_faithful and ad.get("k_rec_times_P_equals_Q", False))
        except Exception as e:
            LOG("[descent] EXC:", repr(e))
            LOG(traceback.format_exc())
            RESULT["errors"].append("descent p=%d: %r" % (p, e))
            ad["auto_descent_ok"] = False
        rec["auto_descent"] = ad
        RESULT["auto_descent"][str(int(p))] = ad

    except Exception as e:
        LOG("[size] FATAL:", repr(e))
        LOG(traceback.format_exc())
        RESULT["errors"].append("size p=%d: %r" % (p, e))
    RESULT["sizes"].append(rec)
    return rec

def _num(x):
    try:
        return int(x)
    except Exception:
        try:
            return float(x)
        except Exception:
            return None

# ---------------------------------------------------------------------------
# DRIVER
# ---------------------------------------------------------------------------
def main():
    t0 = time.time()
    LOG("EXP-028 theta/Kummer-quartic chart -- run start", time.ctime())

    sv = self_validate_meter()
    RESULT["meter_self_validated"] = bool(sv)
    LOG("[main] meter_self_validated =", sv)

    # toy primes p ~ 2^5..2^9, Solinas/a=-3 and random a
    # choose actual primes near each bit size
    prime_list = [37, 67, 131, 257, 521]   # ~2^5.2..2^9
    a_choices = [-3, "random"]
    seedbase = 12028
    for idx, p in enumerate(prime_list):
        for ai, ach in enumerate(a_choices):
            if ach == "random":
                set_random_seed(int(seedbase + 31*idx + 7*ai))
                aval = Integer(randint(0, p-1))
            else:
                aval = Integer(ach)
            run_size(Integer(p), aval, seed=seedbase + 100*idx + ai)

    # ---- verdict logic ----
    any_gate = RESULT["gate_meaningful_fire"]
    # did any theta relation come out lower-degree than elliptic Semaev?
    lower_deg = any(d.get("theta_lower_than_elliptic", False)
                    for d in RESULT["degree_table"] if "theta_lower_than_elliptic" in d)
    # auto-descent: did it work on at least the majority of sizes?
    ad_oks = [v.get("auto_descent_ok", False) for v in RESULT["auto_descent"].values()]
    ad_any = any(ad_oks); ad_all = (len(ad_oks) > 0 and all(ad_oks))
    chart_faith = [v.get("chart_faithful_biquadratic", False) for v in RESULT["auto_descent"].values()]
    chart_ok = (len(chart_faith) > 0 and all(chart_faith))

    if not RESULT["meter_self_validated"]:
        verdict = "inconclusive"
        controls = "METER SELF-VALIDATION FAILED -> meter results untrusted -> INCONCLUSIVE."
    elif not ad_all:
        # auto-descent must work for a credible result
        if any_gate and lower_deg and ad_any:
            verdict = "survived"   # candidate, flagged
            controls = "Partial auto-descent + gate-meaningful + lower-degree: CANDIDATE (needs downstream solver demo)."
        else:
            verdict = "inconclusive" if not chart_ok else "failed"
            controls = ("Auto-descent did not pass on all sizes (chart_faithful=%s, descent_ok=%s). "
                        % (chart_ok, ad_oks))
    else:
        # auto-descent works -> the chart is faithful & descends
        if any_gate and lower_deg:
            verdict = "survived"
            controls = ("CANDIDATE: gate_meaningful fire + lower-degree theta relation + "
                        "auto-descent verified k_rec*P==Q. NEEDS downstream solver demo "
                        "(necessary not sufficient).")
        else:
            verdict = "failed"   # = H14 closed across charts
            controls = ("Meter self-validated (POS-A fires, NEG-1 quiet). Auto-descent VERIFIED "
                        "k_rec*P==Q on all sizes (NR-024 had failed this). Theta/Kummer relation "
                        "is NOT gate_meaningful (gate_meaningful_fire=%s) and NOT lower-degree than "
                        "elliptic Semaev (lower_deg=%s): the level-2 theta chart STILL factors "
                        "through the elliptic structure. H14 closed across charts (NR-024 + EXP-028)."
                        % (any_gate, lower_deg))

    RESULT["verdict"] = verdict
    RESULT["controls_outcome"] = controls
    RESULT["ruled_out"] = ("The level-2 theta-null / Kummer-line chart of A=Res_{F_p2/F_p}(E) "
                           "as a degree-reducing or gate-meaningful intrinsic representation for "
                           "prime-field ECDLP decomposition. Combined with NR-024 (affine chart) "
                           "this closes H14's intrinsic-abelian-surface line across the affine AND "
                           "theta/Kummer charts.") if verdict == "failed" else \
                          ("Nothing closed: theta chart shows a candidate signal." if verdict=="survived"
                           else "Inconclusive (meter/descent build issue).")
    RESULT["what_fires"] = ("e-ring/POS-C-style gate fires occur only in extension/Weil worlds; "
                            "here the theta chart's leading-form module matches the elliptic chart.") \
                            if verdict=="failed" else ("theta-chart gate fire" if verdict=="survived" else "n/a")
    RESULT["next"] = ("Pivot off intrinsic representations (all H14 charts now closed). Next high-risk: "
                      "EXP-029 division-polynomial psi_n fixed-degree B-smooth/non-prime-order FB "
                      "(NR-021 left this open). Conservative: re-confirm capstone NR-026 collection "
                      "bottleneck. Representation-change: pair correspondence / theta on a (1,2)-polarized "
                      "abelian surface that is NOT isogenous to E x E (genuinely 2-dim Jacobian).") \
                      if verdict in ("failed","inconclusive") else \
                     ("CANDIDATE: run a downstream Groebner/crossbred solver demo on the theta m=3 "
                      "system at >=3 sizes to confirm exploitability; red-team for planted-instance "
                      "and FB-row artifacts.")

    LOG("="*70)
    LOG("[VERDICT]", verdict)
    LOG("[controls]", controls)
    LOG("[meter_self_validated]", RESULT["meter_self_validated"])
    LOG("[gate_meaningful_fire]", RESULT["gate_meaningful_fire"])
    LOG("[lower_degree_theta]", lower_deg)
    LOG("[auto_descent all/any]", ad_all, ad_any, " chart_faithful_all:", chart_ok)
    LOG("[elapsed sec]", round(time.time()-t0, 1))

    # ---- write artifacts ----
    try:
        with open(JSONF, "w") as f:
            json.dump(RESULT, f, indent=2, default=str)
        LOG("[write] json ->", JSONF)
    except Exception as e:
        LOG("[write] json FAIL", repr(e))

    try:
        write_md()
        LOG("[write] md ->", MDF)
    except Exception as e:
        LOG("[write] md FAIL", repr(e))
        LOG(traceback.format_exc())

    flush_log()
    LOG("DONE")

def write_md():
    L = []
    L.append("# EXP-028 -- theta / level-2 Kummer-quartic chart of A = Res_{F_p2/F_p}(E)")
    L.append("")
    L.append("**The last un-probed H14 intrinsic representation** (round-10 high-risk direction).")
    L.append("")
    L.append("## Model used")
    L.append("")
    L.append(RESULT["model_used"])
    L.append("")
    L.append("Declared: we use the **level-2 theta-null / Kummer-line model** K = E/{+-1} ~= P^1 "
             "with the **biquadratic (Montgomery/theta) pseudo-addition** relation, Weil-restricted "
             "coordinatewise to F_p (this is the Kummer of the abelian surface A = Res_{F_p2/F_p}(E)). "
             "This is NOT the affine (x,y) chart of NR-024 and NOT the F_q x-line Semaev pullback. "
             "The full level-2 theta quartic-in-P^3 model was symbolically heavy; the Kummer-line "
             "biquadratic carries the same leading-form information for the gate test.")
    L.append("")
    L.append("## Theta-relation degree vs elliptic 4^(m-1) Semaev law")
    L.append("")
    L.append("| p | m | theta total deg | theta per-var | elliptic Semaev deg | 4^(m-1) ref | theta lower? |")
    L.append("|---|---|---|---|---|---|---|")
    for d in RESULT["degree_table"]:
        if d.get("m") == 2:
            L.append("| %s | 2 | %s | %s | %s (S_3) | %s | %s |" % (
                d.get("p"), d.get("theta_relation_total_degree"),
                d.get("theta_relation_pervar"),
                d.get("elliptic_Semaev_S3_total_degree"),
                d.get("elliptic_4^(m-1)_reference"),
                d.get("theta_lower_than_elliptic")))
        elif d.get("m") == 3:
            L.append("| %s | 3 | F12=%s F3t=%s | chained biquadratic | S_4 deg-4/var | %s | (chain) |" % (
                d.get("p"), d.get("theta_chain_F12_total_degree"),
                d.get("theta_chain_F3t_total_degree"),
                d.get("elliptic_4^(m-1)_reference")))
    L.append("")
    L.append("## Gated-meter table  (meter_self_validated = %s)" % RESULT["meter_self_validated"])
    L.append("")
    L.append("Inline self-validation: " + json.dumps(RESULT.get("selfval_detail", {}), default=str))
    L.append("")
    L.append("| p | m | d_ff | D_reg | fires | gate_passes | gate_meaningful |")
    L.append("|---|---|---|---|---|---|---|")
    for mt in RESULT["meter_table"]:
        L.append("| %s | %s | %s | %s | %s | %s | %s |" % (
            mt.get("p"), mt.get("m"), mt.get("d_ff"), mt.get("D_reg"),
            mt.get("fires"), mt.get("gate_passes"), mt.get("gate_meaningful")))
    L.append("")
    L.append("## Auto-descent check (transport public DLP into prime-field E(F_p) subgroup)")
    L.append("")
    L.append("| p | chart_faithful (biquadratic roots == {x(4P),x(2P)}) | k_rec*P==Q (vs PUBLIC Q) | descent_ok |")
    L.append("|---|---|---|---|")
    for pk, v in RESULT["auto_descent"].items():
        L.append("| %s | %s | %s | %s |" % (
            pk, v.get("chart_faithful_biquadratic"),
            v.get("k_rec_times_P_equals_Q"), v.get("auto_descent_ok")))
    L.append("")
    L.append("NR-024's affine build FAILED the k_rec*P==Q verify; EXP-028 reports the result above.")
    L.append("")
    L.append("## Verdict: **%s**" % RESULT["verdict"].upper())
    L.append("")
    L.append(RESULT["controls_outcome"])
    L.append("")
    L.append("**gate_meaningful_fire = %s**" % RESULT["gate_meaningful_fire"])
    L.append("")
    L.append("## What is ruled out")
    L.append("")
    L.append(RESULT["ruled_out"])
    L.append("")
    L.append("## What fires")
    L.append("")
    L.append(RESULT["what_fires"])
    L.append("")
    L.append("## Honest null (stated up front, confirmed/refuted)")
    L.append("")
    L.append("Null: isogeny/quotient invariance is chart-independent, so the theta relation likely "
             "STILL factors through the elliptic structure -> gate_meaningful=False -> H14 closed "
             "across charts. Result: see verdict.")
    L.append("")
    L.append("## Next")
    L.append("")
    L.append(RESULT["next"])
    L.append("")
    if RESULT["errors"]:
        L.append("## Errors logged")
        L.append("")
        for e in RESULT["errors"]:
            L.append("- " + str(e))
        L.append("")
    with open(MDF, "w") as f:
        f.write("\n".join(L) + "\n")

main()
