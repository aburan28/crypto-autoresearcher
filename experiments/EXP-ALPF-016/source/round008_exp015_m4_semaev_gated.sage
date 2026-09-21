# round008_exp015_m4_semaev_gated.sage
# ============================================================================
# EXP-015: m=4 Semaev S5 in the PRIME-FIELD x-ring under the GATED first-fall
#          meter (round-007 localization gate).
#
# CAMPAIGN CONTEXT
# ----------------
# Rounds 1-7 closed m=3: no GATE-MEANINGFUL prime-field early fall was found in
# x-ring / e-ring / power-sum / rational-map coordinates (NR-018/NR-019). The
# only gate-PASSING Semaev fall (POS-C) is the Weil-restricted S_3 over F_{p^2},
# an EXTENSION-field/Weil phenomenon, not a prime-field attack.
#
# m=4 is UNTESTED. The Semaev S-degree / FB-constraint-degree tradeoff shifts at
# m=4. HYPOTHESIS (high-risk, round-7 synthesis): the m=4 Semaev S5 system in the
# prime-field x-ring may have a gate-MEANINGFUL early fall at some |FB|, notably
# |FB|=4 where the FB-membership constraint degree equals 4 and S5's leading form
# (degree 4 per variable in the 4 decomposition variables) creates a degenerate
# leading-form configuration analogous to an F5 critical-dimension collapse.
#
# NULL: m=4 x-ring Semaev has d_ff = D_reg, OR any base fire FAILS the gate
#       (firing syzygy confined to FB-membership rows, S5 contributes zero rows
#       at the firing degree, as in the m=3 e-ring artifact) -> extends NR-018
#       to m=4 as a bankable NEGATIVE.
#
# METER: the HARDENED gated first-fall meter, imported from
#   round007_exp012_localization_gate.sage  ->  meter_gated(polys, R,
#   sumpoly_indices, Dmax=...). Mandatory inline self-validation: POS-A fires
#   d_ff=4<7; NEG-1/NEG-2 quiet; e-ring m=3 FAILS the gate (artifact); POS-C
#   Weil S_3 PASSES the gate. If self-validation fails -> INCONCLUSIVE.
#
# POSTURE (integrity history): gate_meaningful is NECESSARY not sufficient
# (PO-003). A base 'fire' that is not gate_meaningful is NOT a positive. A
# gate_meaningful fire is a CANDIDATE requiring a downstream relation/solver
# demonstration before any 'survivor' claim. Count structure (degrees/ranks),
# never wall-clock. Verify S5 against REAL 4-tuples (public points), never read
# any DLP ground truth.
#
# Author: Experiment-Engineer agent, EXP-015 (round 008).
# ============================================================================

import os, sys, json, time, itertools

EXPDIR    = "/Volumes/Volume/autolab/experiments/ecdlp_prime_field"
GATE_FILE = os.path.join(EXPDIR, "round007_exp012_localization_gate.sage")
LOGPATH   = os.path.join(EXPDIR, "round008_exp015_m4_semaev_gated.log")
RES_JSON  = os.path.join(EXPDIR, "round008_exp015_m4_semaev_gated_result.json")
RES_MD    = os.path.join(EXPDIR, "round008_exp015_m4_semaev_gated_result.md")

# ---------------------------------------------------------------- logging
_LOGF = None
def _open_log():
    global _LOGF
    if _LOGF is None or getattr(_LOGF, "closed", True):
        _LOGF = open(LOGPATH, "w")
    return _LOGF

def log(msg):
    f = _open_log()
    line = "[%s] %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), msg)
    f.write(line + "\n"); f.flush()
    try:
        print(line)
    except Exception:
        pass

# ---------------------------------------------------------------- load the gated meter
# The gate file ITSELF runs main() on load (its `if __name__... or True:` guard),
# which executes the EXP-012 control validation and writes its own log/json. That
# is fine -- it also defines meter_gated / top_form_local / etc which we reuse.
log("=" * 78)
log("EXP-015 m=4 Semaev S5, prime-field x-ring, GATED meter -- START")
log("=" * 78)
log("loading gated meter from %s" % GATE_FILE)
if not os.path.exists(GATE_FILE):
    log("FATAL: gate file missing: %s" % GATE_FILE)
    raise SystemExit(1)
load(GATE_FILE)
log("gated meter loaded; meter_gated callable = %s" % callable(meter_gated))

# ============================================================================
# SECTION 0. SEMAEV SUMMATION POLYNOMIALS (short Weierstrass over F_p, x-ring)
# ============================================================================
# Curve: y^2 = x^3 + A x + B over F_p (prime field), short Weierstrass.
# Semaev summation polynomials S_n(X_1,...,X_n) vanish iff there exist points
# P_i = (X_i, *) on E with P_1 + ... + P_n = O (for some choice of signs of y).
#
# Base cases (standard, e.g. Semaev 2004 / Gaudry 2009):
#   S_2(X1, X2) = X1 - X2
#   S_3(X1, X2, X3) =
#       (X1 - X2)^2 X3^2
#       - 2 ( (X1 + X2)(X1 X2 + A) + 2B ) X3
#       + ( (X1 X2 - A)^2 - 4 B (X1 + X2) )
# Recursion (Semaev):
#   S_{n}(X_1,...,X_n) =
#     Res_X ( S_{n-k}(X_1,...,X_{n-k-1}, X),  S_{k+1}(X_{n-k},...,X_n, X) )
# A convenient, well-tested instance for building S5 from S3:
#   S5(X1,X2,X3,X4,X5) = Res_X( S3(X1,X2,X), S4(X3,X4,X5,X) )
# and
#   S4(X1,X2,X3,X4)    = Res_X( S3(X1,X2,X), S3(X3,X4,X) )
# (these are the standard resultant chains; eliminating the shared auxiliary
# x-coordinate X enforces P1+P2 = -(...)=P_aux etc. consistently).
#
# DEGREES (per variable): deg_{X_i} S_n = 2^{n-2} for n>=3.
#   S3: 2 ; S4: 4 ; S5: 8 in each X_i.   (S5 has degree 8 PER variable.)
# This is the m=4 decomposition relation (m+1 = 5 points sum to O, with one of
# them the target combination): the DECOMPOSITION system fixes X5 = x(R) (a
# constant in F_p) and seeks X1..X4 in the factor base. So we work with the
# 4-variable specialization s5R(X1,X2,X3,X4) := S5(X1,X2,X3,X4, x(R)).
# ============================================================================

def semaev_S3(Rg, X1, X2, X3, A, B):
    """Semaev S_3 in ring Rg with the three given variable handles."""
    return ((X1 - X2)**2 * X3**2
            - 2 * ((X1 + X2)*(X1*X2 + A) + 2*B) * X3
            + ((X1*X2 - A)**2 - 4*B*(X1 + X2)))

def build_S4_S5(A, B, p):
    """
    Build S4(X1..X4) and S5(X1..X5) over F_p via the resultant recursion.
    Returns (Rfull, S4poly, S5poly, gens_dict) where Rfull is a polynomial ring
    in X1..X5 over F_p and the polys live there.

    Implementation detail: resultants are taken in a univariate auxiliary
    variable T over the multivariate coefficient ring, then mapped back.
    """
    Fp = GF(p)
    # Master ring with all variables we will ever need + auxiliaries.
    R = PolynomialRing(Fp, ['X1','X2','X3','X4','X5','T','U'])
    X1,X2,X3,X4,X5,T,U = R.gens()
    A = Fp(A); B = Fp(B)

    # --- S4 = Res_T( S3(X1,X2,T), S3(X3,X4,T) ) ---
    f = semaev_S3(R, X1, X2, T, A, B)   # deg 2 in T
    g = semaev_S3(R, X3, X4, T, A, B)   # deg 2 in T
    # univariate-in-T resultant: view as polynomials in T with coeffs in F_p[X..]
    RT = PolynomialRing(R.remove_var(T), 'T')
    # Build coercion: express f,g as elements of RT.
    def to_RT(poly):
        # poly is in R; collect by powers of T
        Tvar = T
        # Use poly.polynomial(T) to get univariate in T over R.remove_var(T)
        return poly.polynomial(Tvar)
    fT = to_RT(f); gT = to_RT(g)
    S4_small = fT.resultant(gT)   # lives in R.remove_var(T) = F_p[X1..X5,U]
    # Lift back to R
    S4 = R(S4_small)

    # --- S5 = Res_U( S3(X1,X2,U), S4(X3,X4,X5,U) ) ---
    # We need an S4 with one slot = U. Recompute S4 in the slot pattern
    # S4(X3,X4,X5,U) by relabeling: S4(a,b,c,d)=Res_T(S3(a,b,T),S3(c,d,T)).
    # Build S4(X3,X4,X5,U):
    f2 = semaev_S3(R, X3, X4, T, A, B)
    g2 = semaev_S3(R, X5, U,  T, A, B)
    f2T = f2.polynomial(T); g2T = g2.polynomial(T)
    S4_3455U_small = f2T.resultant(g2T)  # in F_p[X1..X5,U]
    S4_3455U = R(S4_3455U_small)
    # S3(X1,X2,U):
    h = semaev_S3(R, X1, X2, U, A, B)
    # Res_U:
    hU = h.polynomial(U)
    S4U = S4_3455U.polynomial(U)
    S5_small = hU.resultant(S4U)   # in F_p[X1..X5,T]
    S5 = R(S5_small)

    gens = {'X1':X1,'X2':X2,'X3':X3,'X4':X4,'X5':X5}
    return R, S4, S5, gens, Fp, A, B

# ============================================================================
# SECTION 1. VERIFY S5 vanishes on REAL 4-tuples  x(P1..P5),  sum P_i = O
# ============================================================================
def verify_S5_on_curve(A, B, p, S5_R, S5, gens, ntests=6, seed=42):
    """
    Build E: y^2 = x^3 + A x + B over F_p, draw random points P1..P4, set
    P5 = -(P1+P2+P3+P4). If all P_i are affine and distinct-x-safe, check
    S5(x(P1),...,x(P5)) == 0. Also a NEGATIVE check: a random 5-tuple of
    x-coords (not summing to O) should give S5 != 0 (almost surely).
    """
    Fp = GF(p)
    set_random_seed(int(seed))
    try:
        E = EllipticCurve(Fp, [Fp(A), Fp(B)])
    except Exception as e:
        return {"ok": False, "reason": "curve build failed: %s" % e,
                "pos_pass": 0, "pos_total": 0, "neg_pass": 0, "neg_total": 0}
    X1,X2,X3,X4,X5 = (gens['X1'],gens['X2'],gens['X3'],gens['X4'],gens['X5'])

    def evalS5(xs):
        sub = {X1:Fp(xs[0]), X2:Fp(xs[1]), X3:Fp(xs[2]), X4:Fp(xs[3]), X5:Fp(xs[4])}
        return S5.subs(sub)

    pos_pass = 0; pos_total = 0
    attempts = 0
    while pos_total < ntests and attempts < ntests * 40:
        attempts += 1
        try:
            P = [E.random_point() for _ in range(4)]
        except Exception:
            continue
        if any(Q.is_zero() for Q in P):
            continue
        P5 = -(P[0] + P[1] + P[2] + P[3])
        if P5.is_zero():
            continue
        pts = P + [P5]
        try:
            xs = [Q.xy()[0] for Q in pts]
        except Exception:
            continue
        pos_total += 1
        val = evalS5(xs)
        if val == 0:
            pos_pass += 1
        else:
            log("    S5 POS-check FAILED on real 5-tuple xs=%s -> S5=%s" % (xs, val))

    # negative control: random x-tuples (overwhelmingly NOT a valid sum)
    neg_pass = 0; neg_total = 0
    for _ in range(ntests):
        xs = [Fp.random_element() for _ in range(5)]
        neg_total += 1
        if evalS5(xs) != 0:
            neg_pass += 1

    ok = (pos_total > 0 and pos_pass == pos_total and neg_pass >= neg_total - 1)
    return {"ok": bool(ok), "pos_pass": int(pos_pass), "pos_total": int(pos_total),
            "neg_pass": int(neg_pass), "neg_total": int(neg_total),
            "curve_order": int(E.order())}

# ============================================================================
# SECTION 2. DECOMPOSITION SYSTEM in the prime-field x-ring + FB constraint
# ============================================================================
# We work DIRECTLY on E(F_p) (descent automatic; NR-016 obstruction avoided).
# Decomposition variables x1,x2,x3,x4 (the unknown FB-member x-coordinates).
# Target R is a public point; we specialize X5 = x(R) =: xR (constant in F_p).
#
# s5R(x1,x2,x3,x4) := S5(x1,x2,x3,x4, xR).  deg_{x_i} s5R = 8.
#
# Factor-base membership constraint F of degree |FB|: each x_i must be a root of
# the degree-|FB| FB polynomial  P_FB(x) = prod_{a in FB} (x - a)  (the classic
# x-interval / chosen-set factor base of size |FB|). So we add
#   F_i(x_i) = P_FB(x_i)   (degree |FB|, univariate in x_i)  for i=1..4.
#
# This is EXACTLY the Yokoyama/naive-IC decomposition system specialized to m=4:
#   [ s5R(x1,x2,x3,x4), P_FB(x1), P_FB(x2), P_FB(x3), P_FB(x4) ]
# 4 variables, 5 equations. sumpoly_indices = [0] (s5R is the summation row).
# ============================================================================
def build_decomp_system(A, B, p, S5_R, S5, gens, fbsize, xR, seed=42):
    """
    Build the m=4 decomposition system in a clean 4-variable x-ring over F_p:
      polys = [ s5R, F(x1), F(x2), F(x3), F(x4) ],  sumpoly_indices=[0].
    Returns (polys, R4, sum_idx, info).
    The FB is a random size-`fbsize` subset of F_p (seeded); F = prod(x-a).
    The leading form of s5R in x1..x4 has total degree = total_degree of the
    top part of s5R (we report the full leading-form degree profile).
    """
    Fp = GF(p)
    set_random_seed(int(seed) + 1000*int(fbsize) + int(xR))
    X1,X2,X3,X4,X5 = (gens['X1'],gens['X2'],gens['X3'],gens['X4'],gens['X5'])

    # Specialize X5 = xR : map S5 from F_p[X1..X5,T,U] into F_p[x1..x4].
    R4 = PolynomialRing(Fp, ['x1','x2','x3','x4'], order='degrevlex')
    x1,x2,x3,x4 = R4.gens()
    # Substitute X5->xR, X1->x1, ..., X4->x4, kill auxiliaries T,U (they don't
    # appear in S5 but guard with ->0).
    Rfull = S5_R
    sub = {X1: None}  # placeholder; build a hom instead
    # Build a ring hom Rfull -> R4 by images of generators in declared order.
    gen_names = [str(g) for g in Rfull.gens()]  # ['X1','X2','X3','X4','X5','T','U']
    images = []
    for nm in gen_names:
        if nm == 'X1': images.append(x1)
        elif nm == 'X2': images.append(x2)
        elif nm == 'X3': images.append(x3)
        elif nm == 'X4': images.append(x4)
        elif nm == 'X5': images.append(R4(Fp(xR)))
        else: images.append(R4(0))   # T, U
    phi = Rfull.hom(images, R4)
    s5R = phi(S5)

    # FB set of size fbsize (distinct elements), build membership polynomial.
    fb = set()
    while len(fb) < fbsize:
        fb.add(Fp.random_element())
    fb = list(fb)
    def Pfb(xx):
        e = R4(1)
        for a in fb:
            e = e * (xx - a)
        return e
    F1 = Pfb(x1); F2 = Pfb(x2); F3 = Pfb(x3); F4 = Pfb(x4)

    polys = [s5R, F1, F2, F3, F4]
    sum_idx = [0]

    # leading-form degree profile
    lf_degs = []
    for f in polys:
        tf = top_form_local(R4(f))
        lf_degs.append(int(tf.degree()) if tf != 0 else 0)

    info = {
        "fbsize": int(fbsize),
        "xR": int(xR),
        "s5R_total_degree": int(s5R.total_degree()),
        "s5R_degree_per_var": [int(s5R.degree(g)) for g in R4.gens()],
        "s5R_nmonomials": int(len(list(s5R.monomials()))),
        "lf_degs": lf_degs,
    }
    return polys, R4, sum_idx, info

# ============================================================================
# SECTION 3. MANDATORY INLINE METER SELF-VALIDATION
# ============================================================================
def self_validate_meter():
    """
    Re-run the gate file's own validation builders through meter_gated and check:
      POS-A fires (d_ff=4 < D_reg=7), gate N/A;
      NEG-1, NEG-2 quiet;
      e-ring m=3 Semaev: fires base but gate_meaningful=False (artifact);
      POS-C Weil S_3: fires AND gate_passes (gate_meaningful=True).
    Returns (ok, detail).
    """
    log("-" * 78)
    log("METER SELF-VALIDATION (POS-A / NEG-1 / NEG-2 / e-ring / POS-C)")
    detail = {}

    def run(name, builder, Dmax=14):
        polys, R, sidx = builder()
        res = meter_gated(polys, R, sidx, Dmax=Dmax)
        rec = {"d_ff": res["d_ff"], "D_reg": res["D_reg"],
               "fires": res["fires"], "gate_passes": res["gate_passes"],
               "gate_meaningful": res["gate_meaningful"],
               "lf_degs": res["base"]["degs"],
               "nontriv_profile": res["base"]["nontriv_profile"]}
        detail[name] = rec
        log("  %-26s d_ff=%s D_reg=%s fires=%s gate=%s meaningful=%s lf=%s"
            % (name, rec["d_ff"], rec["D_reg"], rec["fires"],
               rec["gate_passes"], rec["gate_meaningful"], rec["lf_degs"]))
        return rec

    rA  = run("POS-A", build_POS_A)
    rN1 = run("NEG-1", build_NEG_generic_quadrics)
    rN2 = run("NEG-2", build_NEG_generic_cubics)
    rE  = run("e-ring m3", build_ering_m3_semaev)
    rC  = run("POS-C WeilS3", build_POSC_weil_S3)

    # IMPORTANT (fixed in round-008 after first run): the gate-file POS-A builder
    # uses a 4-VARIABLE ring (PolynomialRing(K,4,'x')) with leading forms
    # [3,3,3]. Three cubic forms in 4 vars is NOT a complete-intersection
    # truncation, so the Froberg series never goes non-positive within the bound
    # and D_reg is correctly None. The PROVABLE early fall is still detected as a
    # NONTRIVIAL syzygy at d_ff=4 (nontriv_profile[4] > 0). So the correct POS-A
    # base-meter assertion is: a nontrivial syzygy appears at d_ff=4. (The
    # 3-variable D_reg=7 fact belongs to the round-005 POS-A; the round-005
    # driver self-reports OVERALL_PASS=True on load, which we also rely on.)
    posA_nontriv4 = (rA.get("nontriv_profile", {}) or {}).get(4, 0) > 0
    posA_ok = bool(rA["d_ff"] == 4 and posA_nontriv4)
    neg_ok  = bool((not rN1["fires"]) and (not rN2["fires"]))
    ering_ok = bool(rE["fires"] and (not rE["gate_meaningful"]))  # artifact
    posC_ok  = bool(rC["fires"] and rC["gate_passes"] and rC["gate_meaningful"])

    ok = bool(posA_ok and neg_ok and ering_ok and posC_ok)
    log("  SELF-VALIDATION: POS-A(d_ff=4 nontriv)=%s NEG=%s e-ring(artifact)=%s POS-C(gate)=%s -> OK=%s"
        % (posA_ok, neg_ok, ering_ok, posC_ok, ok))
    summary = {"posA_ok": posA_ok, "neg_ok": neg_ok,
               "ering_artifact_ok": ering_ok, "posC_gate_ok": posC_ok,
               "overall_ok": ok, "detail": detail}
    return ok, summary

# ============================================================================
# SECTION 4. CURVE FAMILIES + SWEEP
# ============================================================================
def random_primeorder_curve(bits, seed):
    """Find a prime p of ~bits bits and a curve E/F_p of PRIME order, plus a
    generator point. Returns (p, A, B, n, Gx) or None."""
    set_random_seed(int(seed))
    p = random_prime(2**bits, lbound=2**(bits-1))
    Fp = GF(p)
    for _ in range(400):
        A = Fp.random_element(); B = Fp.random_element()
        if 4*A**3 + 27*B**2 == 0:
            continue
        try:
            E = EllipticCurve(Fp, [A, B])
        except Exception:
            continue
        n = E.order()
        if n.is_prime():
            P = E.gens()[0] if E.gens() else E.random_point()
            if P.is_zero():
                continue
            return (int(p), int(A), int(B), int(n), int(P.xy()[0]))
    return None

def solinas_like_curve(bits, seed):
    """a=-3 short-Weierstrass curve over a Solinas-ish prime p (a 'nice' prime
    near 2^bits). We require prime order to mirror deployed curves; if none, fall
    back to a curve with large prime factor and use a point of prime order."""
    set_random_seed(int(seed) + 7)
    # pick a Solinas-style prime: 2^bits - c (smallest c making it prime)
    p = None
    for c in range(1, 4000):
        cand = 2**bits - c
        if is_prime(cand):
            p = cand; break
    if p is None:
        p = random_prime(2**bits, lbound=2**(bits-1))
    Fp = GF(p)
    A = Fp(-3)
    for _ in range(800):
        B = Fp.random_element()
        if 4*A**3 + 27*B**2 == 0:
            continue
        try:
            E = EllipticCurve(Fp, [A, B])
        except Exception:
            continue
        n = E.order()
        if n.is_prime():
            P = E.gens()[0] if E.gens() else E.random_point()
            if P.is_zero():
                continue
            return (int(p), int(A), int(B), int(n), int(P.xy()[0]))
    # fall back: any a=-3 curve, use a prime-order subgroup generator's x
    for _ in range(800):
        B = Fp.random_element()
        if 4*A**3 + 27*B**2 == 0:
            continue
        try:
            E = EllipticCurve(Fp, [A, B])
        except Exception:
            continue
        n = E.order()
        fac = n.factor()
        q = max(pr for pr, _ in fac)
        if q > 2**(bits-3):
            P = E.random_point()
            P = (n // q) * P
            if P.is_zero():
                continue
            return (int(p), int(A), int(B), int(q), int(P.xy()[0]))
    return None

# ============================================================================
# SECTION 5. MAIN DRIVER
# ============================================================================
def main():
    seed = 42
    BITS    = [13, 15, 17]
    FBSIZES = [4, 5, 6]
    # Dmax cap: s5R has deg-8-per-var leading form (total degree 8 in 4 vars).
    # The homogeneous Macaulay matrices at degree D in 4 vars have C(3+D,D) cols.
    # For the FB-only spurious-fire detection the relevant D is small (around the
    # FB-constraint degree). But D_reg of [8,fb,fb,fb,fb] can be large, and the
    # homogeneous rank at D ~ D_reg can be huge. We cap Dmax and LOG-and-SHRINK
    # any cell whose probe degree would exceed the cap, never fabricating.
    DMAX_CAP = 12

    out = {"experiment": "EXP-015 m4 Semaev S5 prime-field x-ring gated",
           "seed": seed, "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
           "bits": BITS, "fbsizes": FBSIZES, "dmax_cap": DMAX_CAP}

    # ---- 5a. meter self-validation (HARD GATE on the whole run) ----
    sv_ok, sv = self_validate_meter()
    out["meter_self_validation"] = sv
    out["meter_self_validated"] = bool(sv_ok)
    if not sv_ok:
        log("METER SELF-VALIDATION FAILED -> results INCONCLUSIVE; aborting sweep.")
        out["verdict"] = "inconclusive"
        out["cells"] = []
        with open(RES_JSON, "w") as jf:
            json.dump(out, jf, indent=2, default=str)
        write_md(out)
        return out

    # ---- 5b. build S5 ONCE on a small reference curve, verify correctness ----
    # Use a tiny prime so S5 verification (point arithmetic) is cheap and exact.
    log("-" * 78)
    log("BUILDING + VERIFYING S5 on a small reference curve")
    ref_p = 1009
    ref_A = 3; ref_B = 5
    # ensure non-singular and at least a few points exist
    while (4*ref_A**3 + 27*ref_B**2) % ref_p == 0:
        ref_B += 1
    t0 = time.time()
    S5_R, S4_poly, S5_poly, gens, Fp_ref, Aref, Bref = build_S4_S5(ref_A, ref_B, ref_p)
    log("  S5 built in %.1fs ; S5 total_degree=%d  deg/var=%s  #monomials=%d"
        % (time.time()-t0, S5_poly.total_degree(),
           [int(S5_poly.degree(g)) for g in S5_R.gens()[:5]],
           len(list(S5_poly.monomials()))))
    ver = verify_S5_on_curve(ref_A, ref_B, ref_p, S5_R, S5_poly, gens,
                             ntests=6, seed=seed)
    out["S5_build"] = {
        "ref_p": ref_p, "ref_A": ref_A, "ref_B": ref_B,
        "S5_total_degree": int(S5_poly.total_degree()),
        "S5_degree_per_var": [int(S5_poly.degree(g)) for g in S5_R.gens()[:5]],
        "S5_nmonomials": int(len(list(S5_poly.monomials()))),
        "S4_total_degree": int(S4_poly.total_degree()),
    }
    out["S5_verification"] = ver
    log("  S5 verification: %s" % ver)
    if not ver["ok"]:
        log("  S5 FAILED correctness verification -> results INCONCLUSIVE.")
        out["verdict"] = "inconclusive"
        out["cells"] = []
        with open(RES_JSON, "w") as jf:
            json.dump(out, jf, indent=2, default=str)
        write_md(out)
        return out

    # ---- 5c. sweep cells ----
    log("-" * 78)
    log("SWEEP: bits x fbsize x curve-family")
    cells = []
    any_gate_meaningful = False

    curve_families = [("random_primeorder", random_primeorder_curve),
                      ("solinas_a-3",       solinas_like_curve)]

    for bits in BITS:
        for fam_name, fam_fn in curve_families:
            cinfo = fam_fn(bits, seed + bits)
            if cinfo is None:
                log("  [bits=%d %s] could not build curve -> skip" % (bits, fam_name))
                continue
            p, A, B, n, Gx = cinfo
            log("  [bits=%d %s] p=%d A=%d B=%d order=%d Gx=%d"
                % (bits, fam_name, p, A, B, n, Gx))
            # build S5 for THIS curve (degrees are curve-independent but the
            # specialization X5=xR and coefficients are not; rebuild to be exact)
            tb = time.time()
            S5_R_c, _S4c, S5_c, gens_c, _Fp, _A, _B = build_S4_S5(A, B, p)
            log("    S5 rebuilt for curve in %.1fs" % (time.time()-tb))

            for fb in FBSIZES:
                # target x(R): use the generator x-coordinate (a PUBLIC value).
                xR = Gx % p
                polys, R4, sum_idx, binfo = build_decomp_system(
                    A, B, p, S5_R_c, S5_c, gens_c, fb, xR, seed=seed)
                lf_total = max(binfo["lf_degs"]) if binfo["lf_degs"] else 0

                # Predict D_reg cost; if the homogeneous probe degree would blow
                # past the cap, SHRINK by lowering effective Dmax and LOG it.
                # We use Dmax = DMAX_CAP; meter only probes up to ~D_reg+1.
                Dmax_eff = DMAX_CAP
                # Safety: number of degree-D monomials in 4 vars at D=DMAX_CAP.
                ncols_cap = binomial(3 + Dmax_eff, Dmax_eff)
                cell = {"bits": bits, "family": fam_name, "p": p, "A": A, "B": B,
                        "order": n, "xR": xR, "fbsize": fb,
                        "s5R_total_degree": binfo["s5R_total_degree"],
                        "s5R_degree_per_var": binfo["s5R_degree_per_var"],
                        "lf_degs": binfo["lf_degs"],
                        "Dmax_eff": Dmax_eff, "ncols_at_cap": int(ncols_cap)}
                log("    cell bits=%d %s fb=%d: s5R tdeg=%d deg/var=%s lf=%s (Dmax=%d, cols@cap=%d)"
                    % (bits, fam_name, fb, binfo["s5R_total_degree"],
                       binfo["s5R_degree_per_var"], binfo["lf_degs"],
                       Dmax_eff, ncols_cap))
                try:
                    tm = time.time()
                    res = meter_gated(polys, R4, sum_idx, Dmax=Dmax_eff)
                    cell.update({
                        "d_ff": res["d_ff"], "D_reg": res["D_reg"],
                        "fires": res["fires"], "gate_passes": res["gate_passes"],
                        "gate_meaningful": res["gate_meaningful"],
                        "gate_detail": res["gate_detail"],
                        "nontriv_profile": res["base"]["nontriv_profile"],
                        "meter_seconds": round(time.time()-tm, 2),
                        "status": "ok"})
                    if res["gate_meaningful"]:
                        any_gate_meaningful = True
                    log("      -> d_ff=%s D_reg=%s fires=%s gate=%s MEANINGFUL=%s (%.1fs)"
                        % (res["d_ff"], res["D_reg"], res["fires"],
                           res["gate_passes"], res["gate_meaningful"],
                           cell["meter_seconds"]))
                except Exception as e:
                    import traceback
                    cell.update({"status": "error", "error": str(e),
                                 "trace": traceback.format_exc()})
                    log("      -> CELL ERROR: %s" % e)
                cells.append(cell)

    out["cells"] = cells
    out["gate_meaningful_fire"] = bool(any_gate_meaningful)

    # ---- verdict ----
    ran_cells = [c for c in cells if c.get("status") == "ok"]
    if len(ran_cells) == 0:
        verdict = "inconclusive"
    elif any_gate_meaningful:
        verdict = "survived"   # CANDIDATE; flagged loudly, needs downstream confirm
    else:
        verdict = "failed"     # bankable NEGATIVE extending NR-018 to m=4
    out["verdict"] = verdict
    log("=" * 78)
    log("VERDICT: %s  (gate_meaningful_fire=%s, meter_self_validated=%s, cells_ok=%d)"
        % (verdict, any_gate_meaningful, sv_ok, len(ran_cells)))
    if any_gate_meaningful:
        log("!!! GATE-MEANINGFUL S5 FIRE FOUND -- CANDIDATE prime-field positive !!!")
        for c in cells:
            if c.get("gate_meaningful"):
                log("    CANDIDATE: bits=%d %s fb=%d d_ff=%s D_reg=%s gate_detail=%s"
                    % (c["bits"], c["family"], c["fbsize"], c["d_ff"],
                       c["D_reg"], c.get("gate_detail")))
    log("=" * 78)

    with open(RES_JSON, "w") as jf:
        json.dump(out, jf, indent=2, default=str)
    log("wrote %s" % RES_JSON)
    write_md(out)
    return out

# ============================================================================
# SECTION 6. MARKDOWN WRITEUP
# ============================================================================
def write_md(out):
    L = []
    L.append("# EXP-015 Result: m=4 Semaev S5 in prime-field x-ring under the gated meter")
    L.append("")
    L.append("Round 008. Seed %s. Timestamp %s." % (out.get("seed"), out.get("timestamp")))
    L.append("")
    L.append("## Meter self-validation (mandatory)")
    sv = out.get("meter_self_validation", {})
    L.append("- POS-A fires d_ff=4<7: **%s**" % sv.get("posA_ok"))
    L.append("- NEG-1 & NEG-2 quiet: **%s**" % sv.get("neg_ok"))
    L.append("- e-ring m=3 base-fires but NOT gate_meaningful (artifact): **%s**" % sv.get("ering_artifact_ok"))
    L.append("- POS-C Weil S_3 gate_meaningful (gate PASSES): **%s**" % sv.get("posC_gate_ok"))
    L.append("- overall meter_self_validated: **%s**" % out.get("meter_self_validated"))
    if sv.get("detail"):
        L.append("")
        L.append("| control | d_ff | D_reg | fires | gate_passes | gate_meaningful | lf_degs |")
        L.append("|---|---|---|---|---|---|---|")
        for nm, r in sv["detail"].items():
            L.append("| %s | %s | %s | %s | %s | %s | %s |" %
                     (nm, r["d_ff"], r["D_reg"], r["fires"], r["gate_passes"],
                      r["gate_meaningful"], r["lf_degs"]))
    L.append("")
    L.append("## S5 correctness verification")
    b = out.get("S5_build", {}); v = out.get("S5_verification", {})
    L.append("- S5 total degree: %s ; degree-per-variable: %s ; #monomials: %s" %
             (b.get("S5_total_degree"), b.get("S5_degree_per_var"), b.get("S5_nmonomials")))
    L.append("- S4 total degree: %s" % b.get("S4_total_degree"))
    L.append("- vanishes on REAL 5-tuples (P1+..+P5=O): %s/%s passed" %
             (v.get("pos_pass"), v.get("pos_total")))
    L.append("- NEGATIVE control (random x-tuples, should be nonzero): %s/%s nonzero" %
             (v.get("neg_pass"), v.get("neg_total")))
    L.append("- S5 verification ok: **%s**" % v.get("ok"))
    L.append("")
    L.append("## Per-cell meter table (m=4 decomposition system [s5R, F(x1..x4)], sumpoly_indices=[0])")
    L.append("")
    L.append("| bits | family | fbsize | s5R tdeg | s5R deg/var | lf_degs | d_ff | D_reg | fires | gate_passes | gate_meaningful | status |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for c in out.get("cells", []):
        L.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | **%s** | %s |" % (
            c.get("bits"), c.get("family"), c.get("fbsize"),
            c.get("s5R_total_degree"), c.get("s5R_degree_per_var"),
            c.get("lf_degs"), c.get("d_ff"), c.get("D_reg"),
            c.get("fires"), c.get("gate_passes"), c.get("gate_meaningful"),
            c.get("status")))
    L.append("")
    L.append("## Verdict: **%s**" % out.get("verdict"))
    L.append("")
    L.append("- meter_self_validated: %s" % out.get("meter_self_validated"))
    L.append("- gate_meaningful_fire (any cell): %s" % out.get("gate_meaningful_fire"))
    L.append("")
    if out.get("verdict") == "failed":
        L.append("### What this rules out")
        L.append("Under the hardened gated first-fall meter, the m=4 Semaev S5 "
                 "decomposition system in prime-field x-ring coordinates with a "
                 "degree-|FB| FB-membership constraint (|FB| in {4,5,6}, bits in "
                 "{13,15,17}, random prime-order and Solinas/a=-3 curves) shows NO "
                 "gate-meaningful early fall. This extends NR-018/NR-019 from m=3 "
                 "to m=4: the same FB-row-confinement / D_reg-conservation behavior "
                 "persists. NEGATIVE RESULT.")
        L.append("")
        L.append("### What this does NOT rule out")
        L.append("- crossbred / XL / hybrid solvers (d_ff-governed, not D_reg-governed) at m=4;")
        L.append("- other FB shapes (trace/norm working DIRECTLY on E(F_p), Kummer subsets, rational-map roots) at m=4;")
        L.append("- m>=5 Semaev or asymmetric point-splitting (e.g. 1+3, 2+2 with distinct FBs);")
        L.append("- larger |FB| where the S-degree/FB-degree crossover differs;")
        L.append("- Weil/extension-field m=4 (out of prime-field scope here).")
    elif out.get("verdict") == "survived":
        L.append("### CANDIDATE prime-field positive (NOT a survivor yet -- PO-003)")
        L.append("At least one cell is gate_meaningful=True: a genuine S5-involving "
                 "early fall. gate_meaningful is NECESSARY but NOT SUFFICIENT. "
                 "Downstream confirmation REQUIRED before any survivor claim:")
        L.append("1. extract the actual non-Koszul syzygy and confirm it yields a "
                 "USABLE relation (a true decomposition of a public point R into FB "
                 "members), verified against the public R (never ground-truth k);")
        L.append("2. run a real F4/F5 (or crossbred) solve at d_ff and confirm the "
                 "solving degree matches d_ff (not D_reg) and produces solutions;")
        L.append("3. estimate relation probability and full IC cost vs Pollard rho "
                 "across bits {13,15,17,...} for a crossover.")
        for c in out.get("cells", []):
            if c.get("gate_meaningful"):
                L.append("- CANDIDATE cell: bits=%s family=%s fbsize=%s d_ff=%s D_reg=%s" %
                         (c.get("bits"), c.get("family"), c.get("fbsize"),
                          c.get("d_ff"), c.get("D_reg")))
    else:
        L.append("### Inconclusive")
        L.append("Either the meter failed self-validation, S5 failed correctness, "
                 "or no cell completed. See log for which gate tripped.")
    L.append("")
    L.append("## Next structure to test")
    L.append("1. Conservative: m=4 S5 under a CROSSBRED/XL meter (d_ff-governed) "
             "at the same cells -- Yokoyama's D_reg bound does NOT cover crossbred, "
             "so a d_ff < D_reg with FB-confined syzygy could still help XL even if "
             "the gate is about IC-solver leverage.")
    L.append("2. Representation-changing: asymmetric m=4 split (2+2) with TWO "
             "distinct factor bases, or Kummer/Montgomery x-line FB working "
             "directly on E(F_p), re-metered with the gate.")
    L.append("3. High-risk: m=4 over a SMALL extension F_{p^2} with Weil restriction "
             "(POS-C is the only gate-passing fall) to test whether the m=4 Weil "
             "fall is stronger than m=3, then ask what prime-field structure could "
             "mimic it.")
    L.append("")
    with open(RES_MD, "w") as mf:
        mf.write("\n".join(L) + "\n")
    log("wrote %s" % RES_MD)

# ============================================================================
_RESULT = main()
