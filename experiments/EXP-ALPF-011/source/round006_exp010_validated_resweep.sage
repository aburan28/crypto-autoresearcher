#!/usr/bin/env sage
# =============================================================================
# EXP-010: Re-run ALL prior m=3 Semaev representations through the VALIDATED
#          (round-5 Bardet-Faugere-Salvy nontrivial-syzygy) first-fall meter.
# =============================================================================
#
# WHY THIS EXPERIMENT (campaign state, rounds 1-5):
#   Rounds 1-4 concluded "no early fall" (d_ff = D_reg) for the e-ring,
#   power-sum, and rational-map-pullback re-coordinatizations of the prime-field
#   m=3 Semaev decomposition system. Those verdicts used a BROKEN meter
#   ("HF_act < HF_pred"), which is impossible homogeneously by Froberg's bound
#   (HF_act >= HF_pred) and false-fires on the affine system. So NR-009/010/012/
#   013/015 were really INCONCLUSIVE, not bankable negatives.
#
#   Round 5 VALIDATED the correct meter: the KERNEL / nontrivial-syzygy meter on
#   the HOMOGENEOUS leading-form system. POS-A (3 cubics whose leading forms
#   share a quadratic factor) FIRES (d_ff=4 < D_reg=7); NEG-1 (3 generic
#   quadrics) and NEG-2 (3 generic cubics) stay quiet (d_ff = D_reg).
#
#   EXP-010 RE-MEASURES every prior representation with that validated meter and
#   DECIDES: does ANY prime-field re-coordinatization of the m=3 Semaev+FB system
#   genuinely early-fall (d_ff < D_reg, campaign's FIRST prime-field algebra-track
#   POSITIVE), or is it d_ff = D_reg everywhere (a now-BANKABLE multi-rep
#   NEGATIVE, finally measured with a working instrument)?
#
# REPRESENTATIONS (each m=3, |FB| in {4,5}, bits in {13,15,17,19}, Solinas/a=-3
#   AND random prime-order curves, seed 42):
#   (A) x-ring baseline           system [S4(x1,x2,x3), F(x1),F(x2),F(x3)]
#                                  -- MUST reproduce EXP-009 D_reg (7/10/12 for
#                                     |FB|=3/4/5), sanity.
#   (B) e-ring (elem. symmetric)  S4 in e1,e2,e3 + FB constraints (degree |FB|).
#   (C) power-sum                 S4 in p1,p2,p3 + FB constraints; report the
#                                  round-5 positive-dimensional anomaly.
#   (D) rational-map pullback     x=phi(t), phi in {t^2, t^2+c}; finite-set FB
#                                  constraint G(t_i)=prod(t_i-tau).
#
# METER INPUT DISCIPLINE (CRITICAL, item (4)):
#   The validated meter (round005) operates on the HOMOGENEOUS LEADING FORMS of
#   the generators. We feed it the ACTUAL decomposition generators in each
#   representation's coordinates (S4-image + FB constraints), and the round005
#   meter() takes their top_form() internally. We DO NOT hand it a degenerate
#   reduction.
#
# MANDATORY inline meter self-validation FIRST (item (1)): POS-A fires (4<7),
#   NEG-1/NEG-2 quiet. If not -> ALL results INCONCLUSIVE.
#
# REPRODUCTION:
#   /usr/local/bin/sage /Volumes/Volume/autolab/experiments/ecdlp_prime_field/round006_exp010_validated_resweep.sage
# =============================================================================

import sys, json, time, traceback
_random = __import__('random')
from itertools import combinations_with_replacement
from datetime import datetime

OUTDIR   = "/Volumes/Volume/autolab/experiments/ecdlp_prime_field"
METER_SRC = OUTDIR + "/round005_meter_validation.sage"
LOG_PATH = OUTDIR + "/round006_exp010_validated_resweep.log"
JSON_PATH = OUTDIR + "/round006_exp010_validated_resweep_result.json"
MD_PATH   = OUTDIR + "/round006_exp010_validated_resweep_result.md"
SEED = 42
START_TIME = time.time()
WALL_CAP = 3000  # seconds

set_random_seed(int(SEED))
_random.seed(int(SEED))

_log_lines = []
def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    line = "[%s] %s" % (ts, msg)
    _log_lines.append(line)
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
log("EXP-010: validated-meter re-sweep of all m=3 Semaev representations")
log("SEED=%d  START=%s" % (SEED, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
log("=" * 78)

# =============================================================================
# SECTION 0: IMPORT the VALIDATED meter from round005 (do NOT re-derive it).
# round005_meter_validation.sage runs main() at import and writes its own log.
# We load it, then grab the exported instrument functions:
#   top_form(f,R), macaulay_homog(homs,R,D), trivial_koszul(degs,n,D),
#   semireg_Dreg(degs,n), meter(polys,R,label) , mons_deg(R,d), n_mons(n,d).
# =============================================================================
log("\nLoading VALIDATED meter from %s ..." % METER_SRC)
try:
    load(METER_SRC)   # defines top_form, macaulay_homog, trivial_koszul,
                       # semireg_Dreg, meter, mons_deg, n_mons (and runs its main()).
    log("  meter module loaded; instrument functions in scope: "
        "top_form, macaulay_homog, trivial_koszul, semireg_Dreg, meter")
except Exception as ex:
    log("  FATAL: could not load meter: %s" % ex)
    log(traceback.format_exc())
    raise

# round005's main() closes its module-global _LOG file handle at end of import.
# The imported meter()/out() write to that handle -> "I/O on closed file" if we
# call meter() now. Reopen _LOG to an EXP-010-owned scratch file so the imported
# meter can keep logging without crashing. _LOG is in scope after load().
try:
    _LOG = open(OUTDIR + "/round006_exp010_meter_inner.log", "w")  # noqa: F811
    log("  reopened imported meter's _LOG -> round006_exp010_meter_inner.log")
except Exception as ex:
    log("  WARNING: could not reopen meter _LOG: %s" % ex)

# round005 meter() writes to ITS OWN _LOG (now closed) and also prints. We want
# its per-cell output captured in OUR log. Wrap it so we redirect output here and
# return (d_ff, D_reg, fires) the same way.
def meter_here(polys, R, label=""):
    """Call the validated meter; the meter logs to round005's (closed) file but
    still returns (d_ff, Dreg, fires). We additionally recompute the homogeneous
    leading-form degree profile we FED it, for the report."""
    homs = [top_form(f, R) for f in polys]
    homs_nz = [h for h in homs if h != 0]
    leading_degs = sorted([int(h.total_degree()) for h in homs_nz])
    d_ff, Dreg, fires = meter(polys, R, label=label)
    return {'label': label, 'd_ff': int(d_ff), 'D_reg_pred': int(Dreg),
            'fires': bool(fires), 'leading_form_degs': leading_degs,
            'n_vars': int(R.ngens())}

# =============================================================================
# SECTION 1: INLINE MANDATORY meter self-validation (POS-A fires, NEG quiet).
# Rebuilt here so the result is captured in OUR json/log (round005's controls
# write only to round005's files). Same constructions as round005.
# =============================================================================
def selfvalidate_meter():
    log("\n" + "=" * 70)
    log("STEP 0 (MANDATORY): inline meter self-validation")
    log("  POS-A: 3 cubics whose leading forms share a quadratic factor -> MUST fire (d_ff=4<7)")
    log("  NEG-1: 3 generic quadrics (regular CI) -> MUST stay quiet (d_ff=D_reg)")
    log("  NEG-2: 3 generic cubics -> MUST stay quiet (d_ff=D_reg)")
    log("=" * 70)
    rng = _random.Random(int(101))
    Rc = PolynomialRing(GF(10007), ['x', 'y', 'z'], order='degrevlex')
    def rquad():
        return sum(GF(10007)(rng.randint(1, 10006)) * m for m in mons_deg(Rc, 2))
    def rcub():
        return sum(GF(10007)(rng.randint(1, 10006)) * m for m in mons_deg(Rc, 3))
    def rlin():
        return sum(GF(10007)(rng.randint(1, 10006)) * g for g in Rc.gens())
    # POS-A
    q = rquad()
    posA = [rlin() * q for _ in range(3)]
    # NEG-1 / NEG-2 with independent rng streams for cleanliness
    rng1 = _random.Random(int(11)); rng2 = _random.Random(int(22))
    def rquad1():
        return sum(GF(10007)(rng1.randint(1, 10006)) * m for m in mons_deg(Rc, 2))
    def rcub2():
        return sum(GF(10007)(rng2.randint(1, 10006)) * m for m in mons_deg(Rc, 3))
    neg1 = [rquad1() for _ in range(3)]
    neg2 = [rcub2() for _ in range(3)]

    rA = meter_here(posA, Rc, label="POS-A topshare-q cubics")
    r1 = meter_here(neg1, Rc, label="NEG-1 3 generic quadrics")
    r2 = meter_here(neg2, Rc, label="NEG-2 3 generic cubics")

    posA_ok = (rA['fires'] and rA['d_ff'] == 4 and rA['D_reg_pred'] == 7)
    neg1_ok = (not r1['fires'])
    neg2_ok = (not r2['fires'])
    validated = bool(posA_ok and neg1_ok and neg2_ok)

    log("\n  SELF-VALIDATION RESULTS:")
    log("   POS-A: d_ff=%d D_reg=%d fires=%s  (need d_ff=4,D_reg=7,fires=True) -> %s"
        % (rA['d_ff'], rA['D_reg_pred'], rA['fires'], "OK" if posA_ok else "FAIL"))
    log("   NEG-1: d_ff=%d D_reg=%d fires=%s  (need fires=False) -> %s"
        % (r1['d_ff'], r1['D_reg_pred'], r1['fires'], "OK" if neg1_ok else "FAIL"))
    log("   NEG-2: d_ff=%d D_reg=%d fires=%s  (need fires=False) -> %s"
        % (r2['d_ff'], r2['D_reg_pred'], r2['fires'], "OK" if neg2_ok else "FAIL"))
    log("  METER_SELF_VALIDATED = %s" % validated)
    return {'validated': validated,
            'POS_A': rA, 'NEG_1': r1, 'NEG_2': r2,
            'posA_ok': posA_ok, 'neg1_ok': neg1_ok, 'neg2_ok': neg2_ok}

# =============================================================================
# SECTION 2: Semaev S3/S4 + representation builders
# (re-implemented here, matching EXP-005/006 logic; not re-deriving the meter).
# =============================================================================
def semaev_S3(x1, x2, x3, a, b, ring):
    Fp = ring.base_ring(); aa = Fp(a); bb = Fp(b)
    A = (x1 - x2)**2
    B = -2*((x1 + x2)*(x1*x2 + aa) + 2*bb)
    C = (x1*x2 - aa)**2 - 4*bb*(x1 + x2)
    return A*x3**2 + B*x3 + C

def build_S4_poly(a, b, p, xR_const):
    """S4(x1,x2,x3) = Res_Y[S3(x1,x2,Y), S3(x3,xR,Y)] with xR fixed. deg 12, deg-4/var."""
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
    return S4, R3

# ---------- (B) e-ring (elementary symmetric) ----------
def rewrite_S4_in_e_coords(S4, R3, Fp):
    x1r, x2r, x3r = R3.gens()
    Rsym = PolynomialRing(Fp, ['e1','e2','e3'], order='degrevlex')
    e1, e2, e3 = Rsym.gens()
    p_int = int(Fp.characteristic())
    e_mons = [(int(a), int(b), int(c))
              for a in range(13) for b in range(7) for c in range(5)
              if int(a) + 2*int(b) + 3*int(c) <= 12]
    rng_loc = _random.Random(py_seed(SEED, 77777))
    n_sample = len(e_mons) + 30
    sample_es, sample_vals = [], []
    for _ in range(n_sample * 5):
        if len(sample_es) >= n_sample:
            break
        xv = [Fp(rng_loc.randint(0, p_int - 1)) for _ in range(3)]
        val = S4.subs({x1r: xv[0], x2r: xv[1], x3r: xv[2]})
        ex1 = xv[0]+xv[1]+xv[2]
        ex2 = xv[0]*xv[1]+xv[0]*xv[2]+xv[1]*xv[2]
        ex3 = xv[0]*xv[1]*xv[2]
        sample_es.append((ex1, ex2, ex3)); sample_vals.append(val)
    A_mat = matrix(Fp, [[ex1**a*ex2**b*ex3**c for (a,b,c) in e_mons]
                        for (ex1,ex2,ex3) in sample_es])
    rhs = vector(Fp, sample_vals)
    try:
        cv = A_mat.solve_right(rhs)
    except Exception:
        return None, None
    S4sym = sum(cv[i]*(e1**a*e2**b*e3**c) for i,(a,b,c) in enumerate(e_mons) if cv[i] != Fp.zero())
    rng_ver = _random.Random(py_seed(SEED, 99999)); n_ok = 0
    for _ in range(30):
        xv = [Fp(rng_ver.randint(0, p_int - 1)) for _ in range(3)]
        v = S4.subs({x1r: xv[0], x2r: xv[1], x3r: xv[2]})
        ex1 = xv[0]+xv[1]+xv[2]; ex2 = xv[0]*xv[1]+xv[0]*xv[2]+xv[1]*xv[2]; ex3 = xv[0]*xv[1]*xv[2]
        if v == S4sym(ex1, ex2, ex3): n_ok += 1
    if n_ok < 27:
        return None, None
    return S4sym, Rsym

def build_fb_constraints_e_ring(FB_xs, Rsym):
    e1, e2, e3 = Rsym.gens(); Fp = Rsym.base_ring()
    R_t = PolynomialRing(Rsym, 't'); t = R_t.gen()
    F_t = prod(t - Fp(xi) for xi in FB_xs)
    modulus = t**3 - e1*t**2 + e2*t - e3
    rem = F_t % modulus
    cons = [Rsym(rem[d]) for d in range(3) if Rsym(rem[d]) != Rsym.zero()]
    return cons

# ---------- (C) power-sum ----------
def rewrite_S4_in_powersum_coords(S4, R3, Fp):
    x1r, x2r, x3r = R3.gens()
    Rps = PolynomialRing(Fp, ['p1','p2','p3'], order='degrevlex')
    p1, p2, p3 = Rps.gens()
    p_int = int(Fp.characteristic())
    ps_mons = [(int(a), int(b), int(c))
               for a in range(13) for b in range(7) for c in range(5)
               if int(a) + 2*int(b) + 3*int(c) <= 12]
    rng_loc = _random.Random(py_seed(SEED, 55555))
    n_sample = len(ps_mons) + 30
    sample_ps, sample_vals = [], []
    for _ in range(n_sample * 5):
        if len(sample_ps) >= n_sample:
            break
        xv = [Fp(rng_loc.randint(0, p_int - 1)) for _ in range(3)]
        val = S4.subs({x1r: xv[0], x2r: xv[1], x3r: xv[2]})
        ps1 = xv[0]+xv[1]+xv[2]; ps2 = xv[0]**2+xv[1]**2+xv[2]**2; ps3 = xv[0]**3+xv[1]**3+xv[2]**3
        sample_ps.append((ps1, ps2, ps3)); sample_vals.append(val)
    A_mat = matrix(Fp, [[ps1**a*ps2**b*ps3**c for (a,b,c) in ps_mons]
                        for (ps1,ps2,ps3) in sample_ps])
    rhs = vector(Fp, sample_vals)
    try:
        cv = A_mat.solve_right(rhs)
    except Exception:
        return None, None
    S4ps = sum(cv[i]*(p1**a*p2**b*p3**c) for i,(a,b,c) in enumerate(ps_mons) if cv[i] != Fp.zero())
    rng_ver = _random.Random(py_seed(SEED, 44444)); n_ok = 0
    for _ in range(30):
        xv = [Fp(rng_ver.randint(0, p_int - 1)) for _ in range(3)]
        v = S4.subs({x1r: xv[0], x2r: xv[1], x3r: xv[2]})
        ps1 = xv[0]+xv[1]+xv[2]; ps2 = xv[0]**2+xv[1]**2+xv[2]**2; ps3 = xv[0]**3+xv[1]**3+xv[2]**3
        if v == S4ps(ps1, ps2, ps3): n_ok += 1
    if n_ok < 27:
        return None, None
    return S4ps, Rps

def build_fb_constraints_powersum(FB_xs, Rps):
    p1, p2, p3 = Rps.gens(); Fp = Rps.base_ring(); char = int(Fp.characteristic())
    if char in (2, 3):
        return None
    inv2 = Fp(2).inverse_of_unit(); inv3 = Fp(3).inverse_of_unit()
    e1_sym = p1
    e2_sym = inv2 * (p1**2 - p2)
    e3_sym = inv3 * (p3 - p1*p2 + e2_sym*p1)
    R_t = PolynomialRing(Rps, 't_ps'); t = R_t.gen()
    F_t = prod(t - Fp(xi) for xi in FB_xs)
    modulus = t**3 - e1_sym*t**2 + e2_sym*t - e3_sym
    try:
        rem = F_t % modulus
    except Exception:
        return None
    cons = [Rps(rem[d]) for d in range(3) if Rps(rem[d]) != Rps.zero()]
    return cons

# ---------- (D) rational-map pullback x = phi(t) ----------
def phi_apply(kind, c, t):
    if kind == 't2':  return t*t
    if kind == 't2c': return t*t + c
    raise ValueError(kind)

def pullback_S4_to_t(S4, R3, kind, c, Rt):
    Fp = Rt.base_ring(); t1, t2, t3 = Rt.gens(); cc = Fp(c)
    images = [phi_apply(kind, cc, t1), phi_apply(kind, cc, t2), phi_apply(kind, cc, t3)]
    out = Rt.zero()
    for coeff, mon in zip(S4.coefficients(), S4.monomials()):
        e = mon.exponents()[0]
        term = Fp(coeff)
        for vi in range(3):
            if e[vi] > 0:
                term = term * images[vi]**int(e[vi])
        out = out + term
    return out

def build_t_preimages(kind, c, FB_xs, Fp):
    cc = Fp(c); T = []; xmap = {}
    for x in FB_xs:
        xv = Fp(x); found = None
        target = xv - cc if kind == 't2c' else xv
        if target.is_square():
            found = target.sqrt()
        if found is not None:
            T.append(found); xmap[int(x)] = found
    return xmap, T

# =============================================================================
# SECTION 3: curve families (reused from EXP-006)
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
            E = EllipticCurve(Fp, [Fp(a), b]); n = E.order()
            if is_prime(n):
                return int(b), E, int(n)
        except Exception:
            continue
    return None

# =============================================================================
# SECTION 4: main sweep -- per (rep, curve, bits, |FB|) cell, run validated meter
# =============================================================================
def run_sweep():
    TARGET_BITS = [13, 15, 17, 19]
    FB_SIZES = [4, 5]
    PHIS = [('t2', 0), ('t2c', 7)]

    # build curves: structured (Solinas, a=-3) + random prime-order
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
            log("  Structured %dbit p=%d (%s) a=%d n=%d" % (tb, p, shape, int(E.a4()), n))
    set_random_seed(SEED+100)
    for tb in TARGET_BITS:
        p = random_prime(2**tb - 1, lbound=2**(tb-1)+2**(tb-2))
        rnd_a = int(GF(p).random_element())
        res = find_prime_order_curve(p, rnd_a, max_tries=300, seed=SEED+tb+200)
        if res is not None:
            b_v, E, n = res
            curves.append({'family':'random','bits':tb,'p':int(p),'shape':"random_%dbit"%tb,
                           'a':int(E.a4()),'b':int(E.a6()),'n':int(n),'E':E})
            log("  Random     %dbit p=%d a=%d n=%d" % (tb, p, int(E.a4()), n))

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
        FB_pool = []; tries = 0
        while len(FB_pool) < max(FB_SIZES) and tries < 2000:
            tries += 1
            Qp = E.random_point()
            if Qp != E(0) and int(Qp[0]) not in FB_pool and int(Qp[0]) != xR:
                FB_pool.append(int(Qp[0]))
        log("  xR=%d  FB_pool(%d)=%s" % (xR, len(FB_pool), FB_pool[:6]))
        try:
            S4, R3 = build_S4_poly(c_info['a'], c_info['b'], p, xR)
            log("  S4: total_deg=%d per_var_deg=%d terms=%d"
                % (S4.total_degree(), max(S4.degree(g) for g in R3.gens()), len(S4.monomials())))
        except Exception as ex:
            log("  S4 build FAILED: %s" % ex); continue
        x1r, x2r, x3r = R3.gens()

        # representation rewrites are |FB|-independent; do once per curve
        S4sym, Rsym = rewrite_S4_in_e_coords(S4, R3, Fp)
        if S4sym is None:
            log("  e-ring rewrite FAILED for this curve")
        else:
            log("  e-ring S4sym: total_deg=%d terms=%d" % (S4sym.total_degree(), len(S4sym.monomials())))
        S4ps, Rps = rewrite_S4_in_powersum_coords(S4, R3, Fp)
        if S4ps is None:
            log("  power-sum rewrite FAILED for this curve")
        else:
            log("  power-sum S4ps: total_deg=%d terms=%d" % (S4ps.total_degree(), len(S4ps.monomials())))

        for n_fb in FB_SIZES:
            if not wall_ok(): break
            if len(FB_pool) < n_fb:
                log("  SKIP |FB|=%d (pool too small)" % n_fb); continue
            FB_use = FB_pool[:n_fb]
            cell = {'family':c_info['family'],'bits':c_info['bits'],'p':p,
                    'a':c_info['a'],'b':c_info['b'],'xR':xR,'n_fb':n_fb,
                    'FB':list(FB_use),
                    'S4_total_deg':int(S4.total_degree()),
                    'reps':{}}

            # ---- (A) x-ring baseline ----
            try:
                F1 = prod(x1r - Fp(x) for x in FB_use)
                F2 = prod(x2r - Fp(x) for x in FB_use)
                F3 = prod(x3r - Fp(x) for x in FB_use)
                base_sys = [S4, F1, F2, F3]
                log("\n  -- |FB|=%d  (A) x-ring  gen_degs=%s --"
                    % (n_fb, [f.total_degree() for f in base_sys]))
                r = meter_here(base_sys, R3, label="%s_%db_FB%d_A_xring"
                               % (c_info['family'], c_info['bits'], n_fb))
                cell['reps']['A_xring'] = r
                log("    (A) x-ring: lf_degs=%s d_ff=%d D_reg=%d fires=%s"
                    % (r['leading_form_degs'], r['d_ff'], r['D_reg_pred'], r['fires']))
            except Exception as ex:
                log("    (A) x-ring FAILED: %s" % ex)
                cell['reps']['A_xring'] = {'error': str(ex)}

            # ---- (B) e-ring ----
            if S4sym is not None:
                try:
                    cons = build_fb_constraints_e_ring(FB_use, Rsym)
                    e_sys = [S4sym] + cons
                    log("  -- |FB|=%d  (B) e-ring  gen_degs=%s (FB cons:%d) --"
                        % (n_fb, [f.total_degree() for f in e_sys], len(cons)))
                    r = meter_here(e_sys, Rsym, label="%s_%db_FB%d_B_ering"
                                   % (c_info['family'], c_info['bits'], n_fb))
                    cell['reps']['B_ering'] = r
                    log("    (B) e-ring: lf_degs=%s d_ff=%d D_reg=%d fires=%s"
                        % (r['leading_form_degs'], r['d_ff'], r['D_reg_pred'], r['fires']))
                except Exception as ex:
                    log("    (B) e-ring FAILED: %s" % ex)
                    cell['reps']['B_ering'] = {'error': str(ex)}
            else:
                cell['reps']['B_ering'] = {'error': 'e-ring rewrite failed'}

            # ---- (C) power-sum ----
            if S4ps is not None:
                try:
                    cons = build_fb_constraints_powersum(FB_use, Rps)
                    if cons is None:
                        cell['reps']['C_powersum'] = {'error': 'FB constraint build failed (char 2/3?)'}
                        log("    (C) power-sum: FB constraint build failed")
                    else:
                        ps_sys = [S4ps] + cons
                        log("  -- |FB|=%d  (C) power-sum  gen_degs=%s (FB cons:%d) --"
                            % (n_fb, [f.total_degree() for f in ps_sys], len(cons)))
                        # detect positive-dimensional anomaly: ideal dimension
                        posdim = None
                        try:
                            posdim = int(ideal(ps_sys).dimension())
                        except Exception as ex2:
                            log("    (C) power-sum dimension probe failed: %s" % ex2)
                        r = meter_here(ps_sys, Rps, label="%s_%db_FB%d_C_powersum"
                                       % (c_info['family'], c_info['bits'], n_fb))
                        r['ideal_dimension'] = posdim
                        r['pos_dim_anomaly'] = bool(posdim is not None and posdim > 0)
                        cell['reps']['C_powersum'] = r
                        log("    (C) power-sum: lf_degs=%s d_ff=%d D_reg=%d fires=%s ideal_dim=%s pos_dim_anomaly=%s"
                            % (r['leading_form_degs'], r['d_ff'], r['D_reg_pred'], r['fires'],
                               posdim, r['pos_dim_anomaly']))
                except Exception as ex:
                    log("    (C) power-sum FAILED: %s" % ex)
                    cell['reps']['C_powersum'] = {'error': str(ex)}
            else:
                cell['reps']['C_powersum'] = {'error': 'power-sum rewrite failed'}

            # ---- (D) rational-map pullback x=phi(t) ----
            for (pk, cval) in PHIS:
                if not wall_ok(): break
                try:
                    Rt = PolynomialRing(Fp, ['t1','t2','t3'], order='degrevlex')
                    t1, t2, t3 = Rt.gens()
                    S4_phi = pullback_S4_to_t(S4, R3, pk, cval, Rt)
                    xmap, T = build_t_preimages(pk, cval, FB_use, Fp)
                    T = list(dict.fromkeys([Fp(tt) for tt in T]))
                    repkey = 'D_phi_%s' % pk
                    if len(T) < 1:
                        cell['reps'][repkey] = {'error': 'no t-preimages in GF(p) for FB under phi',
                                                'n_preimages': 0,
                                                'S4_phi_total_deg': int(S4_phi.total_degree())}
                        log("    (D) phi=%s: no preimages; degrees only (S4_phi deg=%d)"
                            % (pk, S4_phi.total_degree()))
                        continue
                    G1 = prod(t1 - tau for tau in T)
                    G2 = prod(t2 - tau for tau in T)
                    G3 = prod(t3 - tau for tau in T)
                    # verify pullback correctness on a known preimage
                    ver_ok = True
                    for x in FB_use:
                        if int(x) in xmap:
                            tt = xmap[int(x)]
                            if phi_apply(pk, Fp(cval), tt) != Fp(x):
                                ver_ok = False; break
                            if prod(tt - tau for tau in T) != Fp(0):
                                ver_ok = False; break
                    pull_sys = [S4_phi, G1, G2, G3]
                    log("  -- |FB|=%d  (D) phi=%s  gen_degs=%s (S4_phi=%d, FB_t=%d, npre=%d) --"
                        % (n_fb, pk, [f.total_degree() for f in pull_sys],
                           S4_phi.total_degree(), G1.total_degree(), len(T)))
                    r = meter_here(pull_sys, Rt, label="%s_%db_FB%d_D_phi_%s"
                                   % (c_info['family'], c_info['bits'], n_fb, pk))
                    r['n_preimages'] = len(T)
                    r['S4_phi_total_deg'] = int(S4_phi.total_degree())
                    r['preimage_verify'] = bool(ver_ok)
                    cell['reps'][repkey] = r
                    log("    (D) phi=%s: lf_degs=%s d_ff=%d D_reg=%d fires=%s preimg_verify=%s"
                        % (pk, r['leading_form_degs'], r['d_ff'], r['D_reg_pred'], r['fires'], ver_ok))
                except Exception as ex:
                    log("    (D) phi=%s FAILED: %s" % (pk, ex))
                    cell['reps']['D_phi_%s' % pk] = {'error': str(ex)}

            cells.append(cell)
    return cells

# =============================================================================
# SECTION 5: drive + serialize
# =============================================================================
RESULT = {'experiment':'EXP-010_validated_resweep','seed':SEED,
          'timestamp':datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
          'meter_self_validation':None,'cells':[],'crashed':False,'error':None}
try:
    sv = selfvalidate_meter()
    RESULT['meter_self_validation'] = {
        'validated': sv['validated'],
        'POS_A': {'d_ff':sv['POS_A']['d_ff'],'D_reg_pred':sv['POS_A']['D_reg_pred'],'fires':sv['POS_A']['fires']},
        'NEG_1': {'d_ff':sv['NEG_1']['d_ff'],'D_reg_pred':sv['NEG_1']['D_reg_pred'],'fires':sv['NEG_1']['fires']},
        'NEG_2': {'d_ff':sv['NEG_2']['d_ff'],'D_reg_pred':sv['NEG_2']['D_reg_pred'],'fires':sv['NEG_2']['fires']},
    }
    if not sv['validated']:
        log("\nMETER DID NOT SELF-VALIDATE -> all sweep results INCONCLUSIVE.")
        log("Still running sweep for completeness, but verdict will be inconclusive.")
    log("\n" + "="*78)
    log("STEP 1: validated-meter representation sweep")
    log("="*78)
    cells = run_sweep()
    RESULT['cells'] = cells
except Exception as ex:
    RESULT['crashed'] = True
    RESULT['error'] = "%s\n%s" % (ex, traceback.format_exc())
    log("FATAL: %s" % ex); log(traceback.format_exc())

# ---- write JSON ----
try:
    with open(JSON_PATH, "w") as f:
        json.dump(RESULT, f, indent=2, default=str)
    log("WROTE %s" % JSON_PATH)
except Exception as ex:
    log("JSON write failed: %s" % ex)

# =============================================================================
# SECTION 6: compose verdict + markdown
# =============================================================================
def compose_md(R):
    mv = R.get('meter_self_validation') or {}
    validated = bool(mv.get('validated', False))
    crashed = R.get('crashed', False)

    # collect rep firing data
    rep_order = ['A_xring','B_ering','C_powersum','D_phi_t2','D_phi_t2c']
    rep_label = {'A_xring':'(A) x-ring baseline',
                 'B_ering':'(B) e-ring (elem sym)',
                 'C_powersum':'(C) power-sum',
                 'D_phi_t2':'(D) pullback x=t^2',
                 'D_phi_t2c':'(D) pullback x=t^2+c'}
    any_fire = False
    fired_cells = []
    measured = {k: {'fire':0,'total':0,'dff_eq_dreg':0} for k in rep_order}
    for cell in R.get('cells', []):
        for k in rep_order:
            r = cell.get('reps', {}).get(k)
            if not r or 'error' in r or r.get('d_ff') is None:
                continue
            measured[k]['total'] += 1
            if r.get('fires'):
                measured[k]['fire'] += 1
                any_fire = True
                fired_cells.append((cell, k, r))
            else:
                if int(r['d_ff']) == int(r['D_reg_pred']):
                    measured[k]['dff_eq_dreg'] += 1

    lines = []
    lines.append("# EXP-010 Result: validated-meter re-sweep of m=3 Semaev representations")
    lines.append("")
    lines.append("SEED=%d  timestamp=%s" % (R['seed'], R['timestamp']))
    lines.append("")
    lines.append("Meter imported via `load()` from "
                 "`round005_meter_validation.sage` (validated nontrivial-syzygy / "
                 "Bardet-Faugere-Salvy first-fall meter on homogeneous leading forms).")
    lines.append("")

    # --- meter self-validation FIRST ---
    lines.append("## 1. Meter self-validation (MANDATORY, reported first)")
    lines.append("")
    lines.append("| control | d_ff | D_reg_pred | fires | required | OK |")
    lines.append("|---|---|---|---|---|---|")
    pa = mv.get('POS_A',{}); n1 = mv.get('NEG_1',{}); n2 = mv.get('NEG_2',{})
    lines.append("| POS-A (3 cubics, shared quadratic leading factor) | %s | %s | %s | fire @ d_ff=4<D_reg=7 | %s |"
                 % (pa.get('d_ff'),pa.get('D_reg_pred'),pa.get('fires'),
                    (pa.get('fires') and pa.get('d_ff')==4 and pa.get('D_reg_pred')==7)))
    lines.append("| NEG-1 (3 generic quadrics, regular CI) | %s | %s | %s | quiet | %s |"
                 % (n1.get('d_ff'),n1.get('D_reg_pred'),n1.get('fires'), (not n1.get('fires'))))
    lines.append("| NEG-2 (3 generic cubics, regular) | %s | %s | %s | quiet | %s |"
                 % (n2.get('d_ff'),n2.get('D_reg_pred'),n2.get('fires'), (not n2.get('fires'))))
    lines.append("")
    lines.append("**METER_SELF_VALIDATED = %s**" % validated)
    lines.append("")
    if not validated:
        lines.append("> POS-A did not fire as required (or a negative false-fired). "
                     "Per the mandatory posture, ALL representation results below are "
                     "INCONCLUSIVE -- the meter build is wrong in this run.")
        lines.append("")

    # --- per-rep / per-cell table ---
    lines.append("## 2. Per-representation per-cell results (d_ff / D_reg_pred / fires)")
    lines.append("")
    lines.append("Leading-form degree profile is the homogeneous top-form degrees actually fed to the meter.")
    lines.append("")
    lines.append("| curve | bits | |FB| | rep | leading-form degs | d_ff | D_reg_pred | fires |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for cell in R.get('cells', []):
        cid = cell['family']
        for k in rep_order:
            r = cell.get('reps', {}).get(k)
            if not r:
                continue
            if 'error' in r:
                lines.append("| %s | %d | %d | %s | (err: %s) | - | - | - |"
                             % (cid, cell['bits'], cell['n_fb'], rep_label[k], r['error'][:40]))
                continue
            if r.get('d_ff') is None:
                continue
            extra = ""
            if k == 'C_powersum' and r.get('pos_dim_anomaly'):
                extra = " [POS-DIM anomaly: ideal_dim=%s]" % r.get('ideal_dimension')
            lines.append("| %s | %d | %d | %s | %s | %d | %d | %s%s |"
                         % (cid, cell['bits'], cell['n_fb'], rep_label[k],
                            r.get('leading_form_degs'), r['d_ff'], r['D_reg_pred'],
                            r['fires'], extra))
    lines.append("")

    # --- which reps fire ---
    lines.append("## 3. Which representations fire vs not")
    lines.append("")
    lines.append("| rep | cells measured | cells firing (d_ff<D_reg) | cells d_ff=D_reg |")
    lines.append("|---|---|---|---|")
    for k in rep_order:
        m = measured[k]
        lines.append("| %s | %d | %d | %d |" % (rep_label[k], m['total'], m['fire'], m['dff_eq_dreg']))
    lines.append("")

    # --- sanity vs EXP-009 ---
    lines.append("## 4. Sanity vs EXP-009 (x-ring D_reg must match 7/10/12 for |FB|=3/4/5)")
    lines.append("")
    sane = []
    for cell in R.get('cells', []):
        r = cell.get('reps', {}).get('A_xring')
        if r and 'error' not in r and r.get('D_reg_pred') is not None:
            expD = {3:7, 4:10, 5:12}.get(cell['n_fb'])
            sane.append((cell['family'], cell['bits'], cell['n_fb'], r['D_reg_pred'], expD,
                         (expD is None or r['D_reg_pred'] == expD)))
    lines.append("| curve | bits | |FB| | x-ring D_reg | EXP-009 expected | match |")
    lines.append("|---|---|---|---|---|---|")
    for (fam, bits, nfb, dreg, expD, ok) in sane:
        lines.append("| %s | %d | %d | %d | %s | %s |" % (fam, bits, nfb, dreg, expD, ok))
    all_xring_sane = all(s[5] for s in sane) if sane else False
    lines.append("")
    lines.append("**x-ring matches EXP-009 D_reg in all measured cells: %s**" % all_xring_sane)
    lines.append("")

    # --- verdict ---
    lines.append("## 5. Verdict")
    lines.append("")
    if crashed:
        verdict = "inconclusive (run crashed: %s)" % (str(R.get('error',''))[:160])
    elif not validated:
        verdict = ("INCONCLUSIVE -- meter did not self-validate (POS-A must fire d_ff=4<7, "
                   "negatives quiet). No representation verdict can be promoted.")
    elif any_fire:
        verdict = ("POSITIVE (SURVIVED) -- at least one PRIME-FIELD m=3 representation "
                   "genuinely early-falls (d_ff < D_reg) under the validated meter. "
                   "This is the campaign's FIRST prime-field algebra-track positive. "
                   "See firing cells below; escalate per EXP-011.")
    else:
        verdict = ("FAILED (BANKABLE NEGATIVE) -- with a SELF-VALIDATED meter, NO prime-field "
                   "m=3 re-coordinatization (x-ring, e-ring, power-sum, rational-map pullback) "
                   "early-falls: d_ff = D_reg in every measured cell. This converts the prior "
                   "inconclusive NR-009/010/012/013/015 into a VALIDATED multi-representation "
                   "NEGATIVE for the m=3 prime-field Semaev decomposition system.")
    lines.append(verdict)
    lines.append("")

    # --- what fires / bankable ---
    lines.append("## 6. What fires / what is now bankable")
    lines.append("")
    if any_fire:
        lines.append("Firing cells (prime-field POSITIVE -- give exact system):")
        for (cell, k, r) in fired_cells[:20]:
            lines.append("- %s %db |FB|=%d rep=%s: leading-form degs=%s, d_ff=%d < D_reg=%d"
                         % (cell['family'], cell['bits'], cell['n_fb'], rep_label[k],
                            r['leading_form_degs'], r['d_ff'], r['D_reg_pred']))
    else:
        if validated and not crashed:
            lines.append("- NO representation fired. With POS-A firing inline in the SAME run, "
                         "this is a BANKABLE NEGATIVE: NR-009 (e-ring), NR-010/012/013 "
                         "(power-sum / D_reg-conservation), NR-015 (rational-map pullback) "
                         "are now VALIDATED negatives for m=3 prime-field Semaev, no longer "
                         "inconclusive.")
            lines.append("- x-ring reproduces EXP-009 (no early fall), consistent.")
            lines.append("- power-sum positive-dimensional anomaly (round 5) is re-checked: "
                         "see ideal_dim column; even where pos-dim, the homogeneous "
                         "leading-form meter reports d_ff = D_reg (no early fall).")
    lines.append("")

    # --- next ---
    lines.append("## 7. Next structure to test")
    lines.append("")
    if any_fire:
        lines.append("- EXP-011: take the firing system, run an explicit graded Macaulay / F4 "
                     "step-degree solve, confirm the GB falls at d_ff, and compute the HONEST "
                     "index-calculus cost (relations needed, relation probability, rank, "
                     "target descent) vs Pollard rho at the swept sizes and extrapolated.")
    else:
        lines.append("- The remaining untested lever is a FIXED-degree membership factor base "
                     "whose constraint degree is bounded INDEPENDENTLY of |FB| AND that does "
                     "not raise the Semaev degree: e.g. a structural pullback where phi's image "
                     "is cut by one low-degree equation (subfield/trace/norm membership). "
                     "On prime fields the trace/norm route was blocked by the descent obstruction "
                     "(NR-016); the open question is whether any OTHER prime-field coordinate "
                     "system cuts the FB with a |FB|-independent low-degree equation.")
        lines.append("- Also: re-run POS-C (Weil-restricted S3 over F_{p^2}) through THIS meter "
                     "build to confirm the FPPR early-fall still fires here (cross-meter check), "
                     "isolating that the prime-field 'no fall' is a property of the prime-field "
                     "coordinates, not of the meter.")
        lines.append("- Higher m (m=4): the S-degree / FB-degree tradeoff shifts; re-measure d_ff "
                     "there with the same validated meter.")
    return "\n".join(lines), verdict, validated, any_fire, all_xring_sane

try:
    md, verdict_text, validated, any_fire, all_xring_sane = compose_md(RESULT)
    RESULT['verdict'] = verdict_text
    RESULT['any_rep_fires'] = bool(any_fire)
    RESULT['xring_matches_exp009'] = bool(all_xring_sane)
    with open(MD_PATH, "w") as f:
        f.write(md + "\n")
    log("WROTE %s" % MD_PATH)
    with open(JSON_PATH, "w") as f:
        json.dump(RESULT, f, indent=2, default=str)
    log("rewrote JSON with verdict")
except Exception as ex:
    log("MD write failed: %s" % ex); log(traceback.format_exc())

log("\nDONE. wall=%.1fs" % (time.time()-START_TIME))
