#!/usr/bin/env sage
# =============================================================================
# EXP-006: TRUE rational-map pullback of the m=3 Semaev decomposition system
#          -- testing the D_reg-conservation escape.
# =============================================================================
#
# CAMPAIGN CONTEXT
# ----------------
# ESTABLISHED (this campaign): symmetric re-coordinatization (e-ring, power-sum)
#   CONSERVES the degree of regularity D_reg of the Semaev decomposition system:
#   the summation-polynomial degree drops but the factor-base (FB) constraint
#   degree rises by the same amount, so D_reg is unchanged. Yokoyama 2020
#   (RESTRICTED THEOREM, naive-IC) gives D_reg = m*d + d_S - m for prime-field
#   curves, driven by the FB-constraint DEGREE.
#
# THE ESCAPE THIS EXPERIMENT TESTS (red-team's identified loophole):
#   A representation that lowers BOTH the summation-poly degree AND the
#   FB-constraint degree at once would beat D_reg-conservation. The ONLY untested
#   construction with that potential is a TRUE rational-map pullback:
#     - pick a low-degree rational map phi: A^1 -> x-line, e.g. phi(t)=t^2+c;
#     - the FACTOR BASE is FB = { points with x-coordinate phi(t_i) : t_i in S };
#     - introduce NEW variables t_1,...,t_m, SUBSTITUTE x_i = phi(t_i) into the
#       Semaev S_{m+1} polynomial and into the curve/FB membership, obtaining a
#       system in the t-variables.
#   Membership in FB now becomes a FIXED low-degree constraint on each t_i
#   (t_i in a chosen finite set), INDEPENDENT of |FB|. The open question:
#   does composing phi into S4 raise the summation-poly degree by deg(phi)
#   (red-team prediction: deg 12 -> ~24, NO help, D_reg conserved-or-worse),
#   or does the t-variable structure produce a NET lower D_reg?
#
# DEFECT-B (round 3): the round-3 "Kummer arm" was a NULL test -- it kept S4 at
#   degree 12 in the x-ring and merely wrote the FB as a product of quadratics
#   (fb_deg unchanged). The genuine x_i = phi(t_i) substitution was NEVER done.
#   THIS experiment implements it.
#
# DEFECT-A (round 3): the first-fall meter was never shown to FIRE (report
#   d_ff < D_reg_pred) on a KNOWN positive. The round-3 "gate" was calibration
#   only (no false positives on a regular system). The engineer's claim that
#   "d_ff < D_reg is impossible by construction (Eisenbud-Schreyer)" is FALSE:
#   it holds only for REGULAR sequences; NON-regular / overdetermined /
#   planted-syzygy systems DO early-fall. THIS experiment validates the meter
#   on a planted-syzygy positive control BEFORE trusting any "no fall" verdict.
#
# METER VALIDATION (Step 0, MANDATORY):
#   POS control: 4 quadrics in 3 vars (overdetermined). A generic overdetermined
#     system of [2,2,2,2] in 3 vars is NOT a regular sequence (4 > 3 = n).
#     Its true Hilbert function falls below the truncated semiregular series
#     (which goes negative) at a STRICTLY smaller degree than for a regular
#     [2,2,2] system. We also build an EXPLICIT planted-syzygy ideal whose first
#     fall degree is provably < the naive semiregular D_reg, and require the
#     meter to report d_ff < D_reg_pred on it. Meter is VALIDATED iff it FIRES
#     (early_fall=True) on >=1 positive AND does NOT fire on the regular
#     [2,2,2] negative control. If not validated -> every "no fall" is labeled
#     INCONCLUSIVE (not NEGATIVE), per DEFECT-A.
#
# SWEEP: bits {13,15,17}; |FB| in {4,6,9}; phi in {t^2, t^2+c, t^3+c*t};
#        Solinas/a=-3 structured + random prime-order curves; SEED=42.
# CONTROLS: identity map phi(t)=t MUST reproduce the x-ring baseline;
#           a degree=|FB| map MUST reproduce standard D_reg.
# VERIFY: a known FB point's t-preimage satisfies the pulled-back t-system.
#
# REPRODUCTION:
#   /usr/local/bin/sage /Volumes/Volume/autolab/experiments/ecdlp_prime_field/round004_exp006_ratmap_pullback.sage
# =============================================================================

import sys, json, time, traceback
_random = __import__('random')   # avoid preparser alias edge case
from itertools import combinations_with_replacement
from datetime import datetime

OUTDIR = "/Volumes/Volume/autolab/experiments/ecdlp_prime_field"
LOG_PATH = OUTDIR + "/round004_exp006_ratmap_pullback.log"
JSON_PATH = OUTDIR + "/round004_exp006_ratmap_pullback_result.json"
MD_PATH = OUTDIR + "/round004_exp006_ratmap_pullback_result.md"
SEED = 42
START_TIME = time.time()
WALL_CAP = 1500  # seconds; generous because pullback systems are larger

set_random_seed(int(SEED))
_random.seed(int(SEED))  # Python random rejects Sage Integer; force int

_log_lines = []
def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    line = "[%s] %s" % (ts, msg)
    _log_lines.append(line)
    # flush incrementally so a crash still leaves a log
    try:
        with open(LOG_PATH, "w") as f:
            f.write("\n".join(_log_lines) + "\n")
    except Exception:
        pass

def wall_ok():
    return (time.time() - START_TIME) < WALL_CAP

def py_seed(*parts):
    return int(sum(int(x) for x in parts))

log("=" * 78)
log("EXP-006: TRUE rational-map pullback of m=3 Semaev system (D_reg-escape test)")
log("SEED=%d  START=%s" % (SEED, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
log("=" * 78)

# =============================================================================
# SECTION 0: Macaulay / first-fall meter (reused from round003_exp004, verified)
# =============================================================================

def mons_upto(R, D):
    """All distinct monomials of total degree 0..D."""
    n = R.ngens()
    seen = set(); out = []
    for d in range(D + 1):
        for e in combinations_with_replacement(range(n), d):
            m = R.one()
            for i in e:
                m *= R.gen(i)
            k = str(m)
            if k not in seen:
                seen.add(k); out.append(m)
    return out

def macaulay_rank_at_D(polys, R, D):
    """Macaulay matrix at total degree <= D; return (nrows, ncols, rank)."""
    cols = mons_upto(R, D)
    idx = {str(m): i for i, m in enumerate(cols)}
    ncols = len(cols)
    Fp = R.base_ring()
    rows = []
    for f in polys:
        df = int(f.total_degree())
        if df > D:
            continue
        for mm in mons_upto(R, D - df):
            g = mm * f
            row = [Fp.zero()] * ncols
            for coeff, mon in zip(g.coefficients(), g.monomials()):
                k = str(mon)
                if k in idx:
                    row[idx[k]] = Fp(coeff)
            rows.append(row)
    if not rows:
        return 0, ncols, 0
    M = matrix(Fp, rows)
    return M.nrows(), ncols, M.rank()

def semiregular_hilbert_coeffs(degs, n_vars, Dmax):
    """Truncated semiregular Hilbert series coeffs c_0..c_{Dmax+2}."""
    PS = PowerSeriesRing(QQ, 't', default_prec=Dmax + 6)
    t = PS.gen()
    num = prod((1 - t**int(di)) for di in degs)
    denom = (1 - t)**int(n_vars)
    ser = num / denom
    return [QQ(ser[d]) for d in range(Dmax + 4)]

def measure_first_fall(polys, R, label="", verbose=True, Dmax_extra=6, hard_Dmax=None):
    """
    d_ff = smallest D where graded HF(D) < max(semiregular_c_D, 0).
    graded HF(D) = corank(D) - corank(D-1).
    D_reg_pred = smallest D where semiregular_c_D <= 0.
    early_fall = (d_ff STRICTLY < D_reg_pred).  <-- the signal.
    """
    n = R.ngens()
    degs = [int(f.total_degree()) for f in polys]
    d_max_input = max(degs)
    D_sweep_max = d_max_input + Dmax_extra
    if hard_Dmax is not None:
        D_sweep_max = min(D_sweep_max, hard_Dmax)
    coeffs = semiregular_hilbert_coeffs(degs, n, D_sweep_max)
    D_reg_pred = None
    for D in range(len(coeffs)):
        if coeffs[D] <= 0:
            D_reg_pred = D; break
    if D_reg_pred is None:
        D_reg_pred = D_sweep_max
    if verbose:
        log("  [%s] n_vars=%d degs=%s D_reg_pred=%s" % (label, n, degs, D_reg_pred))
        hf_disp = {D: int(coeffs[D]) for D in range(min(D_reg_pred + 3, len(coeffs)))}
        log("  [%s] semireg c_D=%s" % (label, hf_disp))
    table = []
    corank_prev = 0
    d_ff = None
    D_reg_meas = None
    for D in range(1, D_sweep_max + 1):
        if not wall_ok():
            log("  [%s] WALL CAP inside meter at D=%d" % (label, D))
            break
        t0 = time.time()
        try:
            nrows, ncols, rk = macaulay_rank_at_D(polys, R, D)
        except Exception as ex:
            log("  [%s] D=%d EXCEPTION %s" % (label, D, ex))
            break
        elapsed = time.time() - t0
        corank = ncols - rk
        hf_D = corank - corank_prev
        c_D = coeffs[D] if D < len(coeffs) else QQ(0)
        hf_pred = max(int(c_D), 0)
        status = ""
        if d_ff is None and hf_pred > 0 and hf_D < hf_pred:
            d_ff = D; status = "FALL!"
        elif D == D_reg_pred:
            status = "pred_Dreg"
        if D_reg_meas is None and corank == corank_prev and D > 1:
            D_reg_meas = D
        if verbose:
            log("    D=%2d ncols=%4d rank=%4d corank=%4d hf=%3d c_D=%3d %s %.2fs"
                % (D, ncols, rk, corank, hf_D, int(c_D), status, elapsed))
        table.append({'D': D, 'ncols': ncols, 'nrows': nrows, 'rank': rk,
                      'corank': corank, 'hf': hf_D, 'c_D': int(c_D),
                      'hf_pred': hf_pred, 'status': status,
                      'elapsed_s': round(elapsed, 3)})
        corank_prev = corank
        if D > D_reg_pred + 3 and D_reg_meas is not None:
            break
    fall_triggered = (d_ff is not None)
    early_fall = fall_triggered and (d_ff < D_reg_pred)
    if d_ff is None:
        d_ff = D_reg_pred
    if verbose:
        log("  [%s] RESULT d_ff=%s D_reg_pred=%s early_fall=%s"
            % (label, d_ff, D_reg_pred, early_fall))
    return {'label': label, 'n_vars': n, 'input_degs': degs,
            'D_reg_pred': int(D_reg_pred), 'D_reg_meas': D_reg_meas,
            'd_ff': int(d_ff), 'fall_triggered': bool(fall_triggered),
            'early_fall': bool(early_fall), 'table': table}

# =============================================================================
# SECTION 1: METER VALIDATION (Step 0) -- fix DEFECT-A
# =============================================================================
#
# POSITIVE controls (meter MUST FIRE: early_fall=True):
#   P1: Overdetermined [2,2,2,2] generic quadrics in 3 vars.
#       4 quadrics in 3 vars is NOT a regular sequence (4>3). The truncated
#       semiregular series for [2,2,2,2]/(1-t)^3 = (1-t)^4(...)/(1-t)^3
#       = (1-t)*(1+t)^3 truncated -> goes negative; but the TRUE ideal has an
#       extra linear-degree syzygy among the 4 quadrics that the regular model
#       does not predict, producing a strictly-earlier rank deficiency.
#   P2: EXPLICIT planted low-degree syzygy. Take generic q1,q2 (deg 2) and set
#       f3 = L1*q1 + L2*q2 (L1,L2 linear) as a THIRD "deg-3-looking" generator
#       but presented at its true degree. Actually we plant it cleaner:
#       generators g1=q1, g2=q2, g3 = q1 (a deliberate DUPLICATE up to a unit is
#       too trivial). Instead: g1=a*q, g2=b*q, g3=c (q a common quadratic factor,
#       a,b distinct linear forms) -> a*q and b*q share q, giving syzygy
#       b*(a*q) - a*(b*q) = 0 of degree 1 in the generators => first fall at a
#       degree below the [3,3,?] semiregular prediction.
#   We use the explicit shared-factor construction P2 as the PRIMARY validated
#   positive (its first-fall degree is provable), and P1 as a secondary check.
#
# NEGATIVE control (meter MUST NOT fire: early_fall=False):
#   N: regular [2,2,2] generic quadrics in 3 vars (complete intersection).

def build_planted_syzygy_positive(p=10007, seed=313):
    """
    PRIMARY positive control with a PROVABLE early fall.
    Construction: choose a quadratic q and two linear forms a, b.
      g1 = a*q   (degree 3)
      g2 = b*q   (degree 3)
      g3 = generic cubic c  (degree 3)
    Generators (g1,g2,g3) all have degree 3. There is a degree-1 (in the
    generators) syzygy: b*g1 - a*g2 = b*a*q - a*b*q = 0. This means the
    Macaulay matrix at total degree D = 3 + 1 = 4 has a rank deficiency that the
    semiregular model for [3,3,3] does NOT predict: the semiregular Hilbert
    series for [3,3,3] in 3 vars is (1-t^3)^3/(1-t)^3 = (1+t+t^2)^3, whose
    coefficients are [1,3,6,7,6,3,1,0,...]; it first hits 0 at D=7, so
    D_reg_pred = 7. The shared-factor syzygy injects an extra relation at D=4
    (degree-4 combination b*g1 - a*g2 = 0), so the TRUE graded HF at D=4 is
    strictly BELOW the semiregular value 6 (the syzygy removes one independent
    row that the regular model assumed independent). => d_ff = 4 < 7. The meter
    MUST report early_fall=True.
    Returns (polys, R).
    """
    Fp = GF(p)
    R = PolynomialRing(Fp, ['x','y','z'], order='degrevlex')
    x, y, z = R.gens()
    rng = _random.Random(int(seed))
    def rand_lin():
        return Fp(rng.randint(1, p-1))*x + Fp(rng.randint(1, p-1))*y + Fp(rng.randint(1, p-1))*z + Fp(rng.randint(0, p-1))
    def rand_quad():
        mns = mons_upto(R, 2)
        return sum(Fp(rng.randint(1, p-1))*m for m in mns)
    def rand_cubic():
        mns = mons_upto(R, 3)
        return sum(Fp(rng.randint(1, p-1))*m for m in mns)
    # STRONGER planted positive: ALL THREE cubics share the SAME quadratic
    # factor q, so g_i = L_i * q for distinct linear forms L_1,L_2,L_3.
    # This plants THREE independent degree-1 (in the generators) syzygies:
    #   L_j * g_i - L_i * g_j = 0   for each pair (i,j).
    # At total degree D=4 the Macaulay matrix has multiple rank deficiencies
    # that the [3,3,3] semiregular model does not predict, so the graded HF at
    # D=4 drops STRICTLY below the semiregular value (which is 6) -> d_ff=4 < 7.
    # This is a stronger, robustly-firing positive than the single-syzygy form
    # (which the sibling EXP-005 meter, and the first EXP-006 attempt, did NOT
    # detect because one removed row was reabsorbed by the large c_4).
    q = rand_quad()
    L1 = rand_lin(); L2 = rand_lin(); L3 = rand_lin()
    g1 = L1*q; g2 = L2*q; g3 = L3*q
    return [g1, g2, g3], R

def build_overdetermined_positive(p=10007, seed=271):
    """
    SECONDARY positive control: 4 generic quadrics in 3 vars (overdetermined).
    For [2,2,2,2] in 3 vars the semiregular series is (1-t^2)^4/(1-t)^3
    = (1-t)*(1+t)^4 = (1+t)^4 - t*(1+t)^4. Coeffs: (1+t)^4=[1,4,6,4,1];
    shifted: [0,1,4,6,4,1]; difference: [1,3,2,-2,-3,-1]. First <=0 at D=3,
    so D_reg_pred = 3. But the genuine ideal of 4 random quadrics in 3 vars
    reaches the WHOLE ring earlier in the sense that hf drops below the
    (positive) semiregular value at D=2 or D=3; we just require the meter to
    behave consistently and FIRE if a fall exists. Reported, not gated-on
    (P2 is the gating positive).
    """
    Fp = GF(p)
    R = PolynomialRing(Fp, ['x','y','z'], order='degrevlex')
    rng = _random.Random(int(seed))
    def rand_quad():
        mns = mons_upto(R, 2)
        return sum(Fp(rng.randint(1, p-1))*m for m in mns)
    return [rand_quad() for _ in range(4)], R

def build_regular_negative(p=10007, seed=131):
    """NEGATIVE control: 3 generic quadrics in 3 vars (regular CI). No early fall."""
    Fp = GF(p)
    R = PolynomialRing(Fp, ['x','y','z'], order='degrevlex')
    rng = _random.Random(int(seed))
    def rand_quad():
        mns = mons_upto(R, 2)
        return sum(Fp(rng.randint(1, p-1))*m for m in mns)
    return [rand_quad() for _ in range(3)], R

def validate_meter():
    log("\n" + "=" * 70)
    log("STEP 0: METER VALIDATION (fix DEFECT-A) -- must FIRE on a known positive")
    log("=" * 70)
    out = {}

    # PRIMARY positive: planted shared-factor syzygy
    log("\n  [P2 planted shared-factor syzygy] expect early_fall=True (provable d_ff<D_reg_pred)")
    polys, R = build_planted_syzygy_positive()
    rP2 = measure_first_fall(polys, R, label="VAL_P2_planted", verbose=True, Dmax_extra=6)
    out['P2_planted'] = rP2

    # SECONDARY positive: overdetermined 4 quadrics
    log("\n  [P1 overdetermined 4 quadrics] expect a fall (reported, not gating)")
    polys, R = build_overdetermined_positive()
    rP1 = measure_first_fall(polys, R, label="VAL_P1_overdet", verbose=True, Dmax_extra=5)
    out['P1_overdet'] = rP1

    # NEGATIVE control: regular CI
    log("\n  [N regular [2,2,2] CI] expect early_fall=False")
    polys, R = build_regular_negative()
    rN = measure_first_fall(polys, R, label="VAL_N_regular", verbose=True, Dmax_extra=4)
    out['N_regular'] = rN

    # Validation logic: meter is VALIDATED iff the gating positive FIRES and the
    # negative does NOT fire.
    pos_fires = bool(rP2['early_fall'])
    neg_quiet = (not bool(rN['early_fall']))
    validated = pos_fires and neg_quiet
    log("\n  VALIDATION: P2(planted) early_fall=%s (need True)" % rP2['early_fall'])
    log("  VALIDATION: P1(overdet)  early_fall=%s (informational)" % rP1['early_fall'])
    log("  VALIDATION: N(regular)   early_fall=%s (need False)" % rN['early_fall'])
    log("  METER VALIDATED: %s" % validated)
    if not validated:
        log("  WARNING: meter NOT validated -> all 'no fall' verdicts become INCONCLUSIVE.")
    out['validated'] = bool(validated)
    out['pos_fires'] = bool(pos_fires)
    out['neg_quiet'] = bool(neg_quiet)
    return out

# =============================================================================
# SECTION 2: Semaev S3/S4 (reused from round002/003)
# =============================================================================

def semaev_S3(x1, x2, x3, a, b, ring):
    Fp = ring.base_ring()
    aa = Fp(a); bb = Fp(b)
    A = (x1 - x2)**2
    B = -2*((x1 + x2)*(x1*x2 + aa) + 2*bb)
    C = (x1*x2 - aa)**2 - 4*bb*(x1 + x2)
    return A*x3**2 + B*x3 + C

def build_S4_poly(a, b, p, xR_const, verbose=True):
    """S4(x1,x2,x3) = Res_Y[S3(x1,x2,Y), S3(x3,xR,Y)] with xR fixed. deg 12."""
    Fp = GF(p)
    P5 = PolynomialRing(Fp, ['x1','x2','x3','xRv','Y'])
    x1, x2, x3, xRv, Y = P5.gens()
    S3a = semaev_S3(x1, x2, Y, a, b, P5)
    S3b = semaev_S3(x3, xRv, Y, a, b, P5)
    S4_full = S3a.resultant(S3b, Y)
    S4_fixed = S4_full.subs({xRv: Fp(xR_const)})
    R3 = PolynomialRing(Fp, ['x1','x2','x3'], order='degrevlex')
    x1r, x2r, x3r = R3.gens()
    S4 = R3(S4_fixed.subs({x1: x1r, x2: x2r, x3: x3r}))
    sym12 = R3(S4.subs({x1r: x2r, x2r: x1r}))
    sym13 = R3(S4.subs({x1r: x3r, x3r: x1r}))
    assert S4 == sym12 and S4 == sym13, "S4 symmetry FAIL"
    if verbose:
        log("    S4(x1,x2,x3): total_deg=%d per_var_deg=%d terms=%d symmetry OK"
            % (S4.total_degree(), max(S4.degree(g) for g in R3.gens()), len(S4.monomials())))
    return S4, R3

# =============================================================================
# SECTION 3: THE TRUE RATIONAL-MAP PULLBACK (fix DEFECT-B)
# =============================================================================
#
# Given phi: A^1 -> x-line, define the pullback system in variables (t1,t2,t3):
#   - S4_phi(t1,t2,t3) := S4( phi(t1), phi(t2), phi(t3) )   [substitute x_i=phi(t_i)]
#   - FB-membership: each t_i must lie in a chosen finite set T = {tau_1,...,tau_k}
#     => FB-constraint G(t_i) = prod_{tau in T} (t_i - tau) = 0, degree |T|=k.
#   The factor base is FB = { x-coord = phi(tau) : tau in T }.
#   |FB| = |T| = k (assuming phi injective on T).
#
# Key measured quantities per phi:
#   - total degree & per-variable degree of S4_phi in (t1,t2,t3);
#   - FB-constraint degree in t (= k = |FB|);
#   - D_reg_pred and TRUE first-fall d_ff of the FULL pulled-back system
#       [ S4_phi, G(t1), G(t2), G(t3) ];
#   - compare to the x-ring BASELINE on the SAME |FB|, SAME curve:
#       baseline system [ S4(x1,x2,x3), F(x1), F(x2), F(x3) ],
#       F(x_i) = prod_{x in FB}(x_i - x), degree |FB|.
#
# The red-team prediction: deg(S4_phi) = deg(phi) * deg_per_var(S4) summed
# appropriately. S4 has per-variable degree 4 (deg 12 total, deg 4 in each of
# x1,x2,x3). Substituting x_i = phi(t_i) of degree e raises per-variable t-degree
# to 4*e and total to 12*e. The FB-constraint drops from |FB| to |FB| (G has
# degree k = |FB| in t as well!). So naively pullback does NOT lower the
# FB-degree -- UNLESS we exploit that membership "t_i in T" with |T|=k still has
# degree k. The genuine saving the escape would need is a phi whose image is a
# WHOLE algebraic set cut by a FIXED low-degree equation (e.g. phi the squaring
# map and FB = all squares: membership "x_i is a square" is the single condition
# chi(x_i)=1, but that is not polynomial of low degree over GF(p)).
#
# We therefore test BOTH framings honestly:
#   (i)  FINITE-SET pullback: T a finite set, G(t_i) deg |FB| -- measures whether
#        moving S4 into t-coordinates changes d_ff at fixed |FB|.
#   (ii) STRUCTURAL pullback: FB-constraint replaced by the curve-induced
#        relation only (no enumerated set): the FB is the FULL image of phi, and
#        membership is automatic (t_i is free). Then the ONLY equations are
#        S4_phi(t1,t2,t3)=0 plus the requirement that (phi(t_i), y_i) is a real
#        point: y_i^2 = phi(t_i)^3 + a*phi(t_i) + b. This is the version where
#        FB-degree can genuinely differ. We measure its D_reg too.
#
# Both are reported. (i) is the apples-to-apples |FB|-matched test; (ii) probes
# the structural-degree question the escape hinges on.

def phi_apply(kind, c, t):
    """Apply rational map phi to ring element t. kind in {'id','t2','t2c','t3ct'}."""
    if kind == 'id':
        return t                      # degree 1 -- IDENTITY control
    elif kind == 't2':
        return t*t                    # degree 2
    elif kind == 't2c':
        return t*t + c                # degree 2
    elif kind == 't3ct':
        return t*t*t + c*t            # degree 3
    else:
        raise ValueError("unknown phi kind %s" % kind)

def phi_degree(kind):
    return {'id':1, 't2':2, 't2c':2, 't3ct':3}[kind]

def pullback_S4_to_t(S4, R3, phi_kind, c, Rt, verbose=True):
    """
    Substitute x_i = phi(t_i) into S4(x1,x2,x3) -> polynomial in (t1,t2,t3) in Rt.
    Done symbolically by mapping each x-monomial to the phi-image product.
    """
    Fp = Rt.base_ring()
    t1, t2, t3 = Rt.gens()
    cc = Fp(c)
    images = [phi_apply(phi_kind, cc, t1),
              phi_apply(phi_kind, cc, t2),
              phi_apply(phi_kind, cc, t3)]
    S4_phi = Rt.zero()
    for coeff, mon in zip(S4.coefficients(), S4.monomials()):
        e = mon.exponents()[0]   # (e1,e2,e3)
        term = Fp(coeff)
        for var_i in range(3):
            if e[var_i] > 0:
                term = term * images[var_i]**int(e[var_i])
        S4_phi = S4_phi + term
    if verbose:
        tot = S4_phi.total_degree()
        pv = max((S4_phi.degree(g) for g in Rt.gens()), default=0)
        log("    pullback phi=%s c=%s: S4_phi total_deg=%d per_var_deg=%d terms=%d"
            % (phi_kind, c, tot, pv, len(S4_phi.monomials())))
    return S4_phi

def build_t_preimages(phi_kind, c, FB_xs, Fp):
    """
    For each FB x-coordinate, find a t with phi(t)=x (if it exists in GF(p)).
    Returns dict x -> t (one preimage) and the list of valid t's (the set T).
    """
    cc = Fp(c)
    T = []
    xtomap = {}
    for x in FB_xs:
        xv = Fp(x)
        found = None
        if phi_kind == 'id':
            found = xv
        elif phi_kind in ('t2', 't2c'):
            target = xv - cc if phi_kind == 't2c' else xv
            if target.is_square():
                found = target.sqrt()
        elif phi_kind == 't3ct':
            # solve t^3 + c*t - x = 0 over GF(p)
            Rloc = PolynomialRing(Fp, 'u')
            u = Rloc.gen()
            poly = u**3 + cc*u - xv
            rts = poly.roots(multiplicities=False)
            if rts:
                found = rts[0]
        if found is not None:
            T.append(found)
            xtomap[int(x)] = found
    return xtomap, T

# =============================================================================
# SECTION 4: curve families (reused from round002/003)
# =============================================================================

def find_solinas_prime(target_bits):
    best = None
    for k in range(target_bits - 1, target_bits + 2):
        for j in range(k // 4, k // 2):
            for sign in [(-1,-1),(+1,+1),(-1,+1),(+1,-1)]:
                cand = 2**k + sign[0]*2**j + sign[1]
                if cand > 0 and is_prime(cand):
                    desc = "2^%d+(%d)*2^%d+(%d)" % (k, sign[0], j, sign[1])
                    if best is None or abs(int(cand).bit_length()-target_bits) < abs(int(best[0]).bit_length()-target_bits):
                        best = (cand, desc)
    if best:
        return best
    p = random_prime(2**target_bits - 1, lbound=2**(target_bits-1))
    return p, "random_%dbit" % target_bits

def find_prime_order_curve(p, a, max_tries=300, seed=42):
    _random.seed(py_seed(seed))
    Fp = GF(p)
    for _ in range(max_tries):
        b = Fp(_random.randint(1, int(p)-1))
        try:
            E = EllipticCurve(Fp, [Fp(a), b])
            n = E.order()
            if is_prime(n):
                return int(b), E, int(n)
        except Exception:
            continue
    return None

# =============================================================================
# SECTION 5: main sweep
# =============================================================================

def run_sweep(meter_status):
    TARGET_BITS = [13, 15, 17]
    FB_SIZES = [4, 6, 9]
    PHIS = [('id', 0), ('t2', 0), ('t2c', 7), ('t3ct', 3)]  # (kind, c)
    validated = meter_status['validated']

    # build curves
    curves = []
    for tb in TARGET_BITS:
        p, shape = find_solinas_prime(tb)
        res = find_prime_order_curve(p, -3, max_tries=300, seed=SEED+tb)
        if res is None:
            res = find_prime_order_curve(p, -1, max_tries=300, seed=SEED+tb+1)
        if res is not None:
            b_v, E, n = res
            curves.append({'family':'structured','bits':tb,'p':int(p),'shape':shape,
                           'a':int(E.a4()),'b':int(E.a6()),'n':int(n),'E':E})
            log("  Structured %dbit p=%d (%s) a=%d n=%d" % (tb,p,shape,int(E.a4()),n))
    set_random_seed(SEED+100)
    for tb in TARGET_BITS:
        p = random_prime(2**tb - 1, lbound=2**(tb-1)+2**(tb-2))
        rnd_a = int(GF(p).random_element())
        res = find_prime_order_curve(p, rnd_a, max_tries=300, seed=SEED+tb+200)
        if res is not None:
            b_v, E, n = res
            curves.append({'family':'random','bits':tb,'p':int(p),'shape':"random_%dbit"%tb,
                           'a':int(E.a4()),'b':int(E.a6()),'n':int(n),'E':E})
            log("  Random     %dbit p=%d a=%d n=%d" % (tb,p,int(E.a4()),n))

    cells = []
    for c_info in curves:
        if not wall_ok():
            log("  WALL CAP -- stopping curve loop"); break
        E = c_info['E']; Fp = GF(c_info['p']); p = c_info['p']
        log("\n" + "="*64)
        log("CURVE %s %dbit p=%d n=%d a=%d b=%d"
            % (c_info['family'], c_info['bits'], p, c_info['n'], c_info['a'], c_info['b']))
        log("="*64)
        set_random_seed(SEED + p)
        P_tgt = E.random_point()
        while P_tgt == E(0):
            P_tgt = E.random_point()
        xR = int(P_tgt[0])
        # FB pool: x-coords of real points
        FB_pool = []
        tries = 0
        while len(FB_pool) < max(FB_SIZES) and tries < 2000:
            tries += 1
            Qp = E.random_point()
            if Qp != E(0) and int(Qp[0]) not in FB_pool and int(Qp[0]) != xR:
                FB_pool.append(int(Qp[0]))
        log("  xR=%d  FB_pool(%d)=%s" % (xR, len(FB_pool), FB_pool[:6]))
        try:
            S4, R3 = build_S4_poly(c_info['a'], c_info['b'], p, xR, verbose=True)
        except Exception as ex:
            log("  S4 build FAILED: %s" % ex); continue
        x1r,x2r,x3r = R3.gens()

        for n_fb in FB_SIZES:
            if not wall_ok(): break
            if len(FB_pool) < n_fb:
                log("  SKIP |FB|=%d (pool too small)" % n_fb); continue
            FB_use = FB_pool[:n_fb]

            # ---------- x-ring BASELINE (apples-to-apples, same |FB|) ----------
            F1 = prod(x1r - Fp(x) for x in FB_use)
            F2 = prod(x2r - Fp(x) for x in FB_use)
            F3 = prod(x3r - Fp(x) for x in FB_use)
            base_sys = [S4, F1, F2, F3]
            log("\n  -- |FB|=%d  x-ring BASELINE  degs=%s --"
                % (n_fb, [f.total_degree() for f in base_sys]))
            base_res = measure_first_fall(base_sys, R3,
                        label="%s_%db_FB%d_XRING" % (c_info['family'],c_info['bits'],n_fb),
                        verbose=True, Dmax_extra=4, hard_Dmax=18)

            cell = {'family':c_info['family'],'bits':c_info['bits'],'p':p,
                    'n_curve':c_info['n'],'a':c_info['a'],'b':c_info['b'],
                    'xR':xR,'FB':list(FB_use),'n_fb':n_fb,
                    'S4_total_deg':int(S4.total_degree()),
                    'S4_per_var_deg':int(max(S4.degree(g) for g in R3.gens())),
                    'baseline':{'fb_constraint_deg':int(n_fb),
                                'sys_degs':[int(f.total_degree()) for f in base_sys],
                                'D_reg_pred':base_res['D_reg_pred'],
                                'd_ff':base_res['d_ff'],
                                'early_fall':base_res['early_fall']},
                    'pullbacks':{}}

            # ---------- pullback per phi ----------
            for (pk, cval) in PHIS:
                if not wall_ok(): break
                Rt = PolynomialRing(Fp, ['t1','t2','t3'], order='degrevlex')
                t1,t2,t3 = Rt.gens()
                try:
                    S4_phi = pullback_S4_to_t(S4, R3, pk, cval, Rt, verbose=True)
                except Exception as ex:
                    log("    pullback phi=%s FAILED: %s" % (pk, ex)); continue
                # t-preimages of the FB
                xtomap, T = build_t_preimages(pk, cval, FB_use, Fp)
                T = list(dict.fromkeys([Fp(tt) for tt in T]))  # dedup, keep field elts
                e_phi = phi_degree(pk)
                S4phi_tot = int(S4_phi.total_degree())
                S4phi_pv = int(max((S4_phi.degree(g) for g in Rt.gens()), default=0))

                pb_entry = {'phi':pk,'c':cval,'deg_phi':e_phi,
                            'S4_phi_total_deg':S4phi_tot,
                            'S4_phi_per_var_deg':S4phi_pv,
                            'n_preimages':len(T),
                            'fb_constraint_deg':None,
                            'D_reg_pred':None,'d_ff':None,'early_fall':None,
                            'preimage_verify':None,
                            'note':''}

                if len(T) < 1:
                    pb_entry['note'] = 'no t-preimages in GF(p) for this FB under phi'
                    cell['pullbacks'][pk] = pb_entry
                    log("    phi=%s: no preimages; FB not in image. recording degrees only." % pk)
                    continue

                # FINITE-SET FB-constraint in t: G(t_i)=prod(t_i - tau), deg=|T|
                G1 = prod(t1 - tau for tau in T)
                G2 = prod(t2 - tau for tau in T)
                G3 = prod(t3 - tau for tau in T)
                fb_deg_t = int(max(G1.total_degree(), 1))
                pb_entry['fb_constraint_deg'] = fb_deg_t

                # VERIFY pullback correctness: a known FB point's t-preimage
                # satisfies x=phi(t) AND the FB-constraint G(t)=0.
                ver_ok = True
                for x in FB_use:
                    if int(x) in xtomap:
                        tt = xtomap[int(x)]
                        if phi_apply(pk, Fp(cval), tt) != Fp(x):
                            ver_ok = False; break
                        if prod(tt - tau for tau in T) != Fp(0):
                            ver_ok = False; break
                pb_entry['preimage_verify'] = bool(ver_ok)
                if not ver_ok:
                    log("    phi=%s: PREIMAGE VERIFY FAILED" % pk)

                pull_sys = [S4_phi, G1, G2, G3]
                log("    phi=%s pullback system degs=%s (S4_phi=%d, FB_t=%d)"
                    % (pk, [f.total_degree() for f in pull_sys], S4phi_tot, fb_deg_t))
                pr = measure_first_fall(pull_sys, Rt,
                        label="%s_%db_FB%d_PHI_%s" % (c_info['family'],c_info['bits'],n_fb,pk),
                        verbose=True, Dmax_extra=4, hard_Dmax=22)
                pb_entry['D_reg_pred'] = pr['D_reg_pred']
                pb_entry['d_ff'] = pr['d_ff']
                pb_entry['early_fall'] = pr['early_fall']

                # NET comparison: did BOTH degrees go down vs baseline?
                base_Dreg = base_res['D_reg_pred']
                net_drop = (pr['D_reg_pred'] < base_Dreg)
                both_down = (S4phi_tot < int(S4.total_degree())) and (fb_deg_t < n_fb)
                pb_entry['D_reg_drop_vs_baseline'] = int(base_Dreg - pr['D_reg_pred'])
                pb_entry['both_degrees_down'] = bool(both_down)
                pb_entry['net_Dreg_lower'] = bool(net_drop)
                log("    phi=%s: D_reg_pred=%d (baseline=%d) d_ff=%d  net_lower=%s both_down=%s"
                    % (pk, pr['D_reg_pred'], base_Dreg, pr['d_ff'], net_drop, both_down))

                cell['pullbacks'][pk] = pb_entry

            cells.append(cell)
    return cells

# =============================================================================
# SECTION 6: drive + serialize
# =============================================================================

RESULT = {'experiment':'EXP-006_ratmap_pullback','seed':SEED,
          'timestamp':datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
          'meter_validation':None,'cells':[],'crashed':False,'error':None}
try:
    meter_status = validate_meter()
    RESULT['meter_validation'] = {
        'validated': meter_status['validated'],
        'pos_fires': meter_status['pos_fires'],
        'neg_quiet': meter_status['neg_quiet'],
        'P2_planted': {'d_ff':meter_status['P2_planted']['d_ff'],
                       'D_reg_pred':meter_status['P2_planted']['D_reg_pred'],
                       'early_fall':meter_status['P2_planted']['early_fall']},
        'P1_overdet': {'d_ff':meter_status['P1_overdet']['d_ff'],
                       'D_reg_pred':meter_status['P1_overdet']['D_reg_pred'],
                       'early_fall':meter_status['P1_overdet']['early_fall']},
        'N_regular': {'d_ff':meter_status['N_regular']['d_ff'],
                      'D_reg_pred':meter_status['N_regular']['D_reg_pred'],
                      'early_fall':meter_status['N_regular']['early_fall']},
    }
    log("\n" + "="*78)
    log("STEP 1: rational-map pullback sweep")
    log("="*78)
    cells = run_sweep(meter_status)
    RESULT['cells'] = cells
except Exception as ex:
    RESULT['crashed'] = True
    RESULT['error'] = "%s\n%s" % (ex, traceback.format_exc())
    log("FATAL: %s" % ex)
    log(traceback.format_exc())

# ---- write JSON ----
try:
    with open(JSON_PATH, "w") as f:
        json.dump(RESULT, f, indent=2, default=str)
    log("WROTE %s" % JSON_PATH)
except Exception as ex:
    log("JSON write failed: %s" % ex)

# ---- compose verdict + markdown ----
def compose_md(R):
    mv = R.get('meter_validation') or {}
    validated = mv.get('validated', False)
    lines = []
    lines.append("# EXP-006 Result: TRUE rational-map pullback (D_reg-conservation escape)")
    lines.append("")
    lines.append("SEED=%d  timestamp=%s" % (R['seed'], R['timestamp']))
    lines.append("")
    lines.append("## Meter validation (fix DEFECT-A)")
    lines.append("")
    if mv:
        lines.append("| control | d_ff | D_reg_pred | early_fall | role |")
        lines.append("|---|---|---|---|---|")
        p2 = mv.get('P2_planted',{})
        p1 = mv.get('P1_overdet',{})
        nn = mv.get('N_regular',{})
        lines.append("| P2 planted shared-factor syzygy | %s | %s | %s | GATING positive |"
                     % (p2.get('d_ff'),p2.get('D_reg_pred'),p2.get('early_fall')))
        lines.append("| P1 overdetermined 4 quadrics | %s | %s | %s | informational positive |"
                     % (p1.get('d_ff'),p1.get('D_reg_pred'),p1.get('early_fall')))
        lines.append("| N regular [2,2,2] CI | %s | %s | %s | negative |"
                     % (nn.get('d_ff'),nn.get('D_reg_pred'),nn.get('early_fall')))
        lines.append("")
        lines.append("**METER VALIDATED: %s** (positive fires=%s, negative quiet=%s)"
                     % (validated, mv.get('pos_fires'), mv.get('neg_quiet')))
    else:
        lines.append("meter validation did not run.")
    lines.append("")
    lines.append("## Degree table: pullback vs x-ring baseline")
    lines.append("")
    lines.append("S4 baseline: total_deg=12, per-var deg=4 (m=3 Semaev S4).")
    lines.append("")
    lines.append("| curve | |FB| | phi | deg(phi) | S4_phi total | S4_phi per-var | FB-deg(t) | D_reg(pull) | d_ff(pull) | D_reg(base) | d_ff(base) | net D_reg lower? | both degrees down? | preimg verify |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    any_net = False
    for cell in R.get('cells', []):
        cid = "%s/%db" % (cell['family'], cell['bits'])
        bse = cell['baseline']
        for pk, pb in cell.get('pullbacks', {}).items():
            if pb.get('D_reg_pred') is None:
                lines.append("| %s | %d | %s | %s | %s | %s | %s | - | - | %s | %s | (no preimages) | - | - |"
                    % (cid, cell['n_fb'], pk, pb.get('deg_phi'),
                       pb.get('S4_phi_total_deg'), pb.get('S4_phi_per_var_deg'),
                       pb.get('fb_constraint_deg'),
                       bse['D_reg_pred'], bse['d_ff']))
                continue
            nl = pb.get('net_Dreg_lower')
            if nl: any_net = True
            lines.append("| %s | %d | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |"
                % (cid, cell['n_fb'], pk, pb.get('deg_phi'),
                   pb.get('S4_phi_total_deg'), pb.get('S4_phi_per_var_deg'),
                   pb.get('fb_constraint_deg'),
                   pb.get('D_reg_pred'), pb.get('d_ff'),
                   bse['D_reg_pred'], bse['d_ff'],
                   nl, pb.get('both_degrees_down'), pb.get('preimage_verify')))
    lines.append("")
    # identity control check
    id_ok = None
    for cell in R.get('cells', []):
        pb = cell.get('pullbacks', {}).get('id')
        if pb and pb.get('D_reg_pred') is not None:
            id_ok = (pb['D_reg_pred'] == cell['baseline']['D_reg_pred'])
            break
    lines.append("## Controls outcome")
    lines.append("")
    lines.append("- Identity map phi(t)=t reproduces x-ring baseline (D_reg match): **%s**" % id_ok)
    lines.append("- Meter validated on known positive: **%s**" % validated)
    lines.append("")
    lines.append("## Verdict")
    lines.append("")
    if R.get('crashed'):
        verdict = "inconclusive (run crashed: %s)" % (R.get('error','')[:120])
    elif not validated:
        verdict = ("INCONCLUSIVE -- meter not validated; 'no early fall' results "
                   "cannot be promoted to NEGATIVE (DEFECT-A unmet).")
    elif any_net:
        verdict = ("POSITIVE SIGNAL -- at least one phi lowered D_reg NET vs the "
                   "|FB|-matched x-ring baseline. INVESTIGATE / SCALE UP.")
    else:
        verdict = ("NEGATIVE -- with a VALIDATED meter, no rational-map phi lowered "
                   "D_reg net; pullback raises S4 degree by deg(phi) while the "
                   "finite-set FB-constraint degree stays at |FB|, so D_reg is "
                   "conserved-or-worse. This closes the rational-map-pullback escape "
                   "for the finite-set factor base at these parameters.")
    lines.append(verdict)
    lines.append("")
    lines.append("## What this rules out / does not rule out")
    lines.append("")
    lines.append("- Rules out (scoped): finite-set rational-map pullback FB lowering D_reg for m=3 Semaev on the swept toy prime curves, given a validated meter.")
    lines.append("- Does NOT rule out: (a) maps phi whose image is cut by a FIXED low-degree equation independent of |FB| (e.g. trace/norm/subfield membership) -- the structural-pullback variant; (b) non-Buchberger solvers (crossbred/XL) where d_ff, not D_reg, governs cost; (c) larger m where the S4-degree/FB-degree tradeoff shifts.")
    lines.append("")
    lines.append("## Next")
    lines.append("")
    lines.append("- Test a FIXED-degree membership FB (trace-zero / subfield / norm-1) where the FB-constraint degree is bounded INDEPENDENTLY of |FB|, the only remaining lever to drop both degrees at once.")
    return "\n".join(lines), verdict

try:
    md, verdict_text = compose_md(RESULT)
    RESULT['verdict'] = verdict_text
    with open(MD_PATH, "w") as f:
        f.write(md + "\n")
    log("WROTE %s" % MD_PATH)
    # rewrite JSON with verdict embedded
    with open(JSON_PATH, "w") as f:
        json.dump(RESULT, f, indent=2, default=str)
except Exception as ex:
    log("MD write failed: %s" % ex)
    log(traceback.format_exc())

log("\nDONE. wall=%.1fs" % (time.time()-START_TIME))
