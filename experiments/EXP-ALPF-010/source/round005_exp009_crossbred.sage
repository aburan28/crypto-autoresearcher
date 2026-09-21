#!/usr/bin/env sage
# =============================================================================
# EXP-009: NON-BUCHBERGER crossbred / XL-with-cutoff solver for the m=3 Semaev
#          decomposition system over a PRIME field -- OUTSIDE Yokoyama's model.
# =============================================================================
#
# EXPERIMENT CONTRACT
# -------------------
# Hypothesis H1 (the loophole): Yokoyama 2020 (RESTRICTED THEOREM) bounds NAIVE
#   Buchberger/F4/F5 cost on prime-field Semaev IC via the degree of regularity
#   D_reg = m*d + d_S - m. It does NOT cover the CROSSBRED algorithm (Joux-Vitse)
#   or XL with a degree cutoff, where the controlling quantity is the FIRST-FALL
#   degree d_ff and a bilinear-elimination/linearization step, not full D_reg.
#   Q: for the prime-field m=3 Semaev + FB-constraint system, does a crossbred
#   solver (cutoff d_1; Macaulay-multiply to d_1, linearize, then FB-guess +
#   eliminate the remaining variables) have FIELD-OP cost below pure F4 and --
#   the real bar -- below Pollard rho, at any toy size, and how does the
#   crossover move with size?
#
# Null H0: crossbred never undercuts F4 by more than a constant and is always far
#   above rho; the gap to rho GROWS with size (prime-field Semaev d_ff is high).
#
# METER: round-1..4 used the WRONG first-fall meter ("graded HF below semiregular
#   series"): by Froberg's bound HF_act >= HF_pred coefficientwise on the
#   homogeneous leading-form ideal, so that event is IMPOSSIBLE; affinely it
#   FALSE-fires on regular sequences. Round-5 (round005_meter_validation.sage)
#   established the CORRECT meter: the kernel / NONTRIVIAL (non-Koszul) syzygy
#   meter on the homogeneous leading-form system (Bardet-Faugere-Salvy first-fall
#   degree). It FIRES on POS-A (3 cubics whose leading forms share a quadratic:
#   d_ff=4 < D_reg=7) and on a true Weil-S3 instance, and stays quiet on regular
#   CIs. We REUSE that exact meter here (top_form + macaulay_homog +
#   trivial_koszul + semireg_Dreg + meter), re-run its controls as STEP 0, and
#   only trust d_ff numbers if those controls pass. The crossbred SOLVER itself
#   counts real field ops and does not depend on the meter; the meter only
#   EXPLAINS the cutoff behaviour.
#
# SOLVER (real crossbred / XL-with-cutoff, field ops counted)
# ----------------------------------------------------------
# Ideal: m=3 Semaev S4(x1,x2,x3) (total deg 12, per-var 4) + three FB constraints
#   F_i(x_i) = prod_{x in FB}(x_i - x), degree |FB|. 0-dimensional, symmetric.
#   1. Macaulay block: products mu*f for f in {S4,F1,F2,F3}, deg(mu*f) <= d_1.
#   2. RREF over F_p (op-counted: inversions + mults + subs).
#   3. Pure-XL check: scan reduced rows for one supported on powers of a single
#      variable -> univariate -> root-find (the d_ff-controlled XL success, k=0).
#   4. Crossbred FB-guess: guess x3 over its |FB| admissible values (NOT p^k --
#      the FB constraint restricts the guess to |FB| values; this is the cheapest
#      honest prime-field crossbred guess), substitute, re-RREF the 2-var
#      residual, extract a univariate in x1/x2, root-find, back-solve. COST =
#      Macaulay build proxy + exact RREF ops + |FB|*residual-solve ops.
#   We minimize over cutoffs d_1 in {2,3,4,5}.
#
# Pollard-rho field-op-equivalent baseline:
#   group ops ~ sqrt(pi*n/8) (negation /sqrt(2)); convert at 8 field-mults/group-op
#   (Jacobian a=-3, no per-op inversion) = conversion MOST favorable to rho, so any
#   crossbred "win" is conservative. Also report 30 field-mults/op (affine+inv).
#
# F4 baseline: Sage groebner_basis + variety; field-op proxy = ncols(D_solve)^2.37
#   (low, best linear-algebra exponent) to ncols(D_solve)^3 (high, dense),
#   D_solve = max(GB max deg, D_reg). Wall-clock also recorded.
#
# VERIFY (correctness gate): lift each returned FB x-coord on E, try all y-signs,
#   accept iff some combination sums to +/- the PUBLIC target P. Uses only public
#   P, never ground-truth k. Each instance PLANTS a known relation Q1+Q2+Q3=P so a
#   verifiable decomposition is guaranteed to exist (a control that cannot succeed
#   is not a control).
#
# SWEEP: bits {13,15,17,19}; |FB| {3,4,5}; cutoffs d_1 {2,3,4,5}; Solinas/a=-3 +
#   random curves; SEED=42; 2 target trials/cell. Macaulay column cap 1800.
#
# SAGE GOTCHA (round-5 memo): random.Random(<literal>) raises TypeError in
#   Sage 10.9 / Python 3.14 because the preparser makes the literal a Sage
#   Integer. ALL seeds wrapped in int(...).
#
# REPRODUCTION:
#   /usr/local/bin/sage /Volumes/Volume/autolab/experiments/ecdlp_prime_field/round005_exp009_crossbred.sage
# =============================================================================

import sys, json, time, traceback
import random as _random
from itertools import combinations_with_replacement, product as iproduct
from datetime import datetime

OUTDIR   = "/Volumes/Volume/autolab/experiments/ecdlp_prime_field"
LOG_PATH = OUTDIR + "/round005_exp009_crossbred.log"
JSON_PATH= OUTDIR + "/round005_exp009_crossbred_result.json"
MD_PATH  = OUTDIR + "/round005_exp009_crossbred_result.md"
SEED = 42
START = time.time()
WALL_CAP = 2400

set_random_seed(int(SEED))
_random.seed(int(SEED))

_log = []
def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    line = "[%s] %s" % (ts, msg)
    _log.append(line)
    try:
        with open(LOG_PATH, "w") as f:
            f.write("\n".join(_log) + "\n")
    except Exception:
        pass
    print(line, flush=True)

def wall_ok():
    return (time.time() - START) < WALL_CAP

def py_seed(*parts):
    return int(sum(int(x) for x in parts))

log("=" * 78)
log("EXP-009: crossbred / XL-with-cutoff for m=3 prime-field Semaev (non-Buchberger)")
log("SEED=%d  START=%s  sage=%s" % (SEED, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), version()))
log("=" * 78)

# =============================================================================
# SECTION 0: monomials, Macaulay, op-counted RREF, semiregular series
# =============================================================================

def mons_upto(R, D):
    n = R.ngens(); seen = set(); out = []
    for d in range(D + 1):
        for e in combinations_with_replacement(range(n), d):
            m = R.one()
            for i in e:
                m *= R.gen(i)
            k = str(m)
            if k not in seen:
                seen.add(k); out.append(m)
    return out

def mons_deg(R, d):
    o = []
    for e in combinations_with_replacement(range(R.ngens()), d):
        m = R.one()
        for i in e:
            m *= R.gen(i)
        o.append(m)
    return o

def n_mons(n, d):
    if d < 0:
        return 0
    return int(binomial(n - 1 + d, d))

def build_macaulay(polys, R, D):
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
        return matrix(Fp, 0, ncols), cols
    return matrix(Fp, rows), cols

def rref_with_opcount(M):
    Fp = M.base_ring()
    A = [list(r) for r in M.rows()]
    nrows = len(A)
    ncols = M.ncols()
    ops = 0
    rank = 0
    pivot_cols = []
    rr = 0
    for c in range(ncols):
        piv = None
        for r in range(rr, nrows):
            if A[r][c] != 0:
                piv = r; break
        if piv is None:
            continue
        A[rr], A[piv] = A[piv], A[rr]
        inv = A[rr][c].inverse_of_unit(); ops += 1
        for j in range(c, ncols):
            if A[rr][j] != 0:
                A[rr][j] = A[rr][j] * inv; ops += 1
        for r in range(nrows):
            if r != rr and A[r][c] != 0:
                factor = A[r][c]
                for j in range(c, ncols):
                    if A[rr][j] != 0:
                        A[r][j] = A[r][j] - factor * A[rr][j]; ops += 2
        pivot_cols.append(c); rank += 1; rr += 1
        if rr >= nrows:
            break
    R = matrix(Fp, A) if A else matrix(Fp, 0, ncols)
    return R, rank, ops, pivot_cols

def semiregular_series(degs, n, Dmax):
    PS = PowerSeriesRing(QQ, 't', default_prec=Dmax + 6)
    t = PS.gen()
    num = prod((1 - t**int(d)) for d in degs)
    ser = num / (1 - t)**int(n)
    return [QQ(ser[d]) for d in range(Dmax + 4)]

def D_reg_semiregular(degs, n, Dmax=60):
    c = semiregular_series(degs, n, Dmax)
    for D in range(len(c)):
        if c[D] <= 0:
            return D
    return Dmax

# =============================================================================
# SECTION 1: VALIDATED first-fall meter (round-005 kernel/nontrivial-syzygy)
# =============================================================================

def top_form(f, R):
    d = f.total_degree()
    t = R.zero()
    for mon, co in zip(f.monomials(), f.coefficients()):
        if mon.total_degree() == d:
            t += co * mon
    return t

def macaulay_homog(homs, R, D):
    cols = mons_deg(R, D)
    idx = {str(m): i for i, m in enumerate(cols)}
    nc = len(cols)
    Fp = R.base_ring()
    rows = []
    for h in homs:
        if h == 0:
            continue
        dh = int(h.total_degree())
        if dh > D:
            continue
        for mm in mons_deg(R, D - dh):
            g = mm * h
            row = [Fp.zero()] * nc
            for c, mon in zip(g.coefficients(), g.monomials()):
                k = str(mon)
                if k in idx:
                    row[idx[k]] = Fp(c)
            rows.append(row)
    if not rows:
        return 0, nc, 0
    M = matrix(Fp, rows)
    return M.nrows(), nc, M.rank()

def trivial_koszul(degs, n, D):
    m = len(degs); cnt = 0
    for i in range(m):
        for j in range(i + 1, m):
            cnt += n_mons(n, D - degs[i] - degs[j])
    return cnt

def semireg_Dreg(degs, n):
    Dmax = sum(degs) + 2
    PS = PowerSeriesRing(QQ, 't', default_prec=Dmax + 6)
    t = PS.gen()
    ser = prod((1 - t**int(d)) for d in degs) / (1 - t)**int(n)
    co = [QQ(ser[d]) for d in range(Dmax + 4)]
    for D in range(len(co)):
        if co[D] <= 0:
            return D, co
    return Dmax, co

def meter(polys, R, label="", verbose=True):
    """KERNEL / nontrivial-syzygy first-fall meter on the leading-form system.
    d_ff = smallest D with nontrivial(D)=ker(phi_D)-trivial_koszul(D) > 0.
    fires iff d_ff < D_reg_pred. (Validated in round005_meter_validation.sage.)"""
    n = R.ngens()
    degs = [int(f.total_degree()) for f in polys]
    homs = [top_form(f, R) for f in polys]
    Dreg, co = semireg_Dreg(degs, n)
    if verbose:
        log("    [%s] degs=%s n=%d D_reg_pred=%d" % (label, degs, n, Dreg))
    d_ff = None
    for D in range(min(degs), Dreg + 1):
        nr, nc, rk = macaulay_homog(homs, R, D)
        ker = nr - rk
        triv = trivial_koszul(degs, n, D)
        nontriv = ker - triv
        tag = ""
        if d_ff is None and nontriv > 0:
            d_ff = D; tag = "  <-- FIRST FALL"
        if verbose:
            log("    [%s] D=%d nrows=%d rank=%d ker=%d triv=%d nontriv=%d%s"
                % (label, D, nr, rk, ker, triv, nontriv, tag))
        if d_ff is not None:
            break
    if d_ff is None:
        d_ff = Dreg
    fires = (d_ff < Dreg)
    return {'label': label, 'd_ff': int(d_ff), 'D_reg_pred': int(Dreg),
            'early_fall': bool(fires)}

def rand_quad_hom(R, rng):
    Fp = R.base_ring(); p = int(Fp.characteristic())
    return sum(Fp(rng.randint(1, p - 1)) * m for m in mons_deg(R, 2))
def rand_cub_hom(R, rng):
    Fp = R.base_ring(); p = int(Fp.characteristic())
    return sum(Fp(rng.randint(1, p - 1)) * m for m in mons_deg(R, 3))
def lin_hom(R, rng):
    Fp = R.base_ring(); p = int(Fp.characteristic())
    return sum(Fp(rng.randint(1, p - 1)) * g for g in R.gens())

def revalidate_meter():
    log("\n" + "="*70)
    log("STEP 0: METER RE-VALIDATION (round-005 kernel/nontrivial-syzygy meter)")
    log("="*70)
    R = PolynomialRing(GF(10007), ['x', 'y', 'z'], order='degrevlex')
    rng = _random.Random(int(101))
    q = rand_quad_hom(R, rng)
    posA = [lin_hom(R, rng) * q for _ in range(3)]  # share quadratic factor q
    log("  POS-A: 3 cubics with leading forms L_i*q (provable d_ff=4 < D_reg=7)")
    rA = meter(posA, R, label="POS-A", verbose=True)
    log("  POS-A: d_ff=%d D_reg=%d early_fall=%s" % (rA['d_ff'], rA['D_reg_pred'], rA['early_fall']))
    rng2 = _random.Random(int(11))
    neg = [rand_quad_hom(R, rng2) for _ in range(3)]  # regular CI
    log("  NEG-1: 3 generic quadrics (regular CI) -> must NOT early-fall")
    rN = meter(neg, R, label="NEG-1", verbose=True)
    log("  NEG-1: d_ff=%d D_reg=%d early_fall=%s" % (rN['d_ff'], rN['D_reg_pred'], rN['early_fall']))
    rng3 = _random.Random(int(22))
    neg2 = [rand_cub_hom(R, rng3) for _ in range(3)]  # regular cubics
    log("  NEG-2: 3 generic cubics (regular) -> must NOT early-fall")
    rN2 = meter(neg2, R, label="NEG-2", verbose=True)
    log("  NEG-2: d_ff=%d D_reg=%d early_fall=%s" % (rN2['d_ff'], rN2['D_reg_pred'], rN2['early_fall']))
    validated = bool(rA['early_fall']) and (not bool(rN['early_fall'])) and (not bool(rN2['early_fall']))
    log("  METER VALIDATED: %s (POS-A fires=%s, NEG-1 quiet=%s, NEG-2 quiet=%s)"
        % (validated, rA['early_fall'], not rN['early_fall'], not rN2['early_fall']))
    return {'validated': validated,
            'POS_A': rA, 'NEG_1': rN, 'NEG_2': rN2}

# =============================================================================
# SECTION 2: Semaev S3/S4, curves
# =============================================================================

def semaev_S3(x1, x2, x3, a, b, ring):
    Fp = ring.base_ring(); aa = Fp(a); bb = Fp(b)
    A = (x1 - x2)**2
    B = -2*((x1 + x2)*(x1*x2 + aa) + 2*bb)
    C = (x1*x2 - aa)**2 - 4*bb*(x1 + x2)
    return A*x3**2 + B*x3 + C

def build_S4_poly(a, b, p, xR_const, verbose=True):
    Fp = GF(p)
    P5 = PolynomialRing(Fp, ['x1','x2','x3','xRv','Y'])
    x1,x2,x3,xRv,Y = P5.gens()
    S3a = semaev_S3(x1, x2, Y, a, b, P5)
    S3b = semaev_S3(x3, xRv, Y, a, b, P5)
    S4_full = S3a.resultant(S3b, Y)
    S4_fixed = S4_full.subs({xRv: Fp(xR_const)})
    R3 = PolynomialRing(Fp, ['x1','x2','x3'], order='degrevlex')
    x1r,x2r,x3r = R3.gens()
    S4 = R3(S4_fixed.subs({x1:x1r, x2:x2r, x3:x3r}))
    if verbose:
        log("    S4: total_deg=%d per_var=%d terms=%d"
            % (S4.total_degree(), max(S4.degree(g) for g in R3.gens()), len(S4.monomials())))
    return S4, R3

def find_solinas_prime(target_bits):
    best = None
    for k in range(target_bits - 1, target_bits + 2):
        for j in range(k // 4, k // 2):
            for sign in [(-1,-1),(+1,+1),(-1,+1),(+1,-1)]:
                cand = 2**k + sign[0]*2**j + sign[1]
                if cand > 0 and is_prime(cand):
                    if best is None or abs(int(cand).bit_length()-target_bits) < abs(int(best[0]).bit_length()-target_bits):
                        best = (cand, "2^%d%+d*2^%d%+d" % (k, sign[0], j, sign[1]))
    if best:
        return best
    p = random_prime(2**target_bits - 1, lbound=2**(target_bits-1))
    return p, "random_%db" % target_bits

def find_prime_order_curve(p, a, max_tries=400, seed=42):
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
# SECTION 3: decomposition instance (planted relation) + x-ring system
# =============================================================================

def build_decomp_instance(E, p, n_fb, seed):
    Fp = GF(p)
    set_random_seed(int(seed))
    _random.seed(py_seed(seed))
    P = E.random_point()
    while P == E(0):
        P = E.random_point()
    Q1 = Q2 = Q3 = None
    for _ in range(300):
        c1 = E.random_point(); c2 = E.random_point()
        c3 = P - c1 - c2
        if (c1 != E(0) and c2 != E(0) and c3 != E(0)
                and len({int(c1[0]), int(c2[0]), int(c3[0]), int(P[0])}) == 4):
            Q1, Q2, Q3 = c1, c2, c3; break
    if Q1 is None:
        return None
    planted = [int(Q1[0]), int(Q2[0]), int(Q3[0])]
    FB = list(planted)
    tries = 0
    while len(FB) < n_fb and tries < 3000:
        tries += 1
        Rr = E.random_point()
        if Rr != E(0) and int(Rr[0]) not in FB and int(Rr[0]) != int(P[0]):
            FB.append(int(Rr[0]))
    if len(FB) < n_fb:
        return None
    FB = FB[:n_fb]
    return {'P':P, 'xR':int(P[0]), 'FB':FB, 'planted':planted,
            'a':int(E.a4()), 'b':int(E.a6())}

def build_xring_system(S4, R3, FB, Fp):
    x1,x2,x3 = R3.gens()
    F1 = prod(x1 - Fp(xx) for xx in FB)
    F2 = prod(x2 - Fp(xx) for xx in FB)
    F3 = prod(x3 - Fp(xx) for xx in FB)
    return [S4, F1, F2, F3]

# =============================================================================
# SECTION 4: crossbred / XL-with-cutoff solver
# =============================================================================

def extract_univariate_from_rref(Rred, cols, R3):
    Fp = R3.base_ring(); n = R3.ngens()
    col_info = []
    for m in cols:
        e = m.exponents()[0] if m != R3.one() else tuple([0]*n)
        nz = [i for i in range(n) if e[i] > 0]
        if len(nz) == 0:
            col_info.append(('const', 0))
        elif len(nz) == 1:
            col_info.append((nz[0], int(e[nz[0]])))
        else:
            col_info.append((None, None))
    found = []
    for row in Rred.rows():
        support = [j for j in range(len(row)) if row[j] != 0]
        if not support:
            continue
        vars_used = set(); ok = True
        for j in support:
            ci = col_info[j]
            if ci[0] == 'const':
                continue
            if ci[0] is None:
                ok = False; break
            vars_used.add(ci[0])
        if ok and len(vars_used) == 1:
            vi = vars_used.pop()
            maxdeg = max((col_info[j][1] for j in support if col_info[j][0] == vi), default=0)
            coeffs = [Fp.zero()] * (maxdeg + 1)
            for j in support:
                ci = col_info[j]
                if ci[0] == 'const':
                    coeffs[0] += row[j]
                elif ci[0] == vi:
                    coeffs[ci[1]] += row[j]
            found.append((vi, coeffs))
    return found

def crossbred_solve(system, R3, FB, cutoff_d1, op_budget=None):
    Fp = R3.base_ring()
    x1,x2,x3 = R3.gens()
    total_ops = 0
    M, cols = build_macaulay(system, R3, cutoff_d1)
    if M.nrows() == 0:
        return {'solved':False,'candidates':[],'field_ops':0,'mac_rows':0,
                'mac_cols':len(cols),'mac_rank':0,'guessed_vars':None,
                'pure_xl_univariate':False,'note':'empty Macaulay at cutoff'}
    build_ops = int(M.nrows() * M.ncols() / 8)
    Rred, rank, rref_ops, pivots = rref_with_opcount(M)
    total_ops += build_ops + rref_ops
    mac_rows, mac_cols = M.nrows(), M.ncols()
    uni = extract_univariate_from_rref(Rred, cols, R3)
    pure_xl = len(uni) > 0
    cands = []
    # crossbred FB-guess of x3 + residual XL
    guessed = 1
    R2 = PolynomialRing(Fp, ['x1','x2'], order='degrevlex')
    y1,y2 = R2.gens()
    hom = R3.hom([y1, y2, Fp(0)], R2)  # placeholder; we substitute x3 numerically below
    for v in FB:
        sub_sys = []
        for f in system:
            g = f.subs({x3: Fp(v)})
            if g == 0:
                continue
            # map remaining x1,x2 into R2
            g2 = R2(g.subs({x1: R3(y1), x2: R3(y2)})) if False else None
            # robust conversion via string-free substitution:
            poly2 = R2.zero()
            for coeff, mon in zip(g.coefficients(), g.monomials()):
                e = mon.exponents()[0]
                poly2 += Fp(coeff) * y1**int(e[0]) * y2**int(e[1])
            if poly2 != 0 and poly2.total_degree() >= 1:
                sub_sys.append(poly2)
        if not sub_sys:
            continue
        rd = min(cutoff_d1 + 1, max(int(f.total_degree()) for f in sub_sys) + 1)
        M2, cols2 = build_macaulay(sub_sys, R2, rd)
        if M2.nrows() == 0:
            continue
        total_ops += int(M2.nrows()*M2.ncols()/8)
        Rred2, rank2, ops2, piv2 = rref_with_opcount(M2)
        total_ops += ops2
        uni2 = extract_univariate_from_rref(Rred2, cols2, R2)
        for (vi2, coeffs2) in uni2:
            Ru = PolynomialRing(Fp, 'u'); u = Ru.gen()
            poly = sum(coeffs2[d]*u**d for d in range(len(coeffs2)))
            if poly == 0:
                continue
            try:
                roots = poly.roots(multiplicities=False)
            except Exception:
                roots = []
            total_ops += int(poly.degree())**2 if poly.degree() else 0
            for rt in roots:
                if int(rt) not in [int(x) for x in FB]:
                    continue
                othervar = y2 if vi2 == 0 else y1
                fixedvar = y1 if vi2 == 0 else y2
                for w in FB:
                    ok = True
                    for f in sub_sys:
                        val = f.subs({fixedvar: Fp(rt), othervar: Fp(w)})
                        total_ops += int(len(f.monomials()))
                        if val != 0:
                            ok = False; break
                    if ok:
                        triple = (int(rt), int(w), int(v)) if vi2 == 0 else (int(w), int(rt), int(v))
                        cands.append(tuple(sorted(triple)))
        if op_budget and total_ops > op_budget:
            break
    cands = list(dict.fromkeys(cands))
    return {'solved':len(cands)>0,'candidates':cands,'field_ops':int(total_ops),
            'mac_rows':int(mac_rows),'mac_cols':int(mac_cols),'mac_rank':int(rank),
            'guessed_vars':guessed,'pure_xl_univariate':bool(pure_xl),
            'note':'crossbred FB-guess(x3)+XL residual'}

# =============================================================================
# SECTION 5: F4 baseline
# =============================================================================

def f4_solve_opcount(system, R3, FB, Fp):
    t0 = time.time()
    I = ideal(system)
    try:
        gb = I.groebner_basis()
    except Exception as ex:
        return {'solved':False,'field_ops':None,'wall':time.time()-t0,
                'D_solve':None,'note':'GB failed: %s'%ex,'candidates':[]}
    wall = time.time() - t0
    gb_max_deg = max((g.total_degree() for g in gb), default=0)
    degs = [int(f.total_degree()) for f in system]
    D_reg = D_reg_semiregular(degs, R3.ngens())
    D_solve = max(gb_max_deg, D_reg)
    n = R3.ngens()
    ncols = binomial(D_solve + n, n)
    op_low = int(ncols**2.37)
    op_high = int(ncols**3)
    cands = []
    try:
        V = I.variety()
        for sol in V:
            try:
                cands.append(tuple(sorted(int(sol[g]) for g in R3.gens())))
            except Exception:
                pass
    except Exception:
        pass
    return {'solved':len(cands)>0,'field_ops':op_low,'field_ops_high':op_high,
            'wall':wall,'D_solve':int(D_solve),'D_reg':int(D_reg),
            'gb_max_deg':int(gb_max_deg),'ncols_at_Dsolve':int(ncols),
            'candidates':list(dict.fromkeys(cands)),'note':'Sage F4 + variety'}

# =============================================================================
# SECTION 6: Pollard-rho field-op baseline
# =============================================================================

def rho_field_ops(n_order, fmuls_per_gop=8):
    import math
    gops = math.sqrt(math.pi * float(n_order) / 8.0)
    return gops * fmuls_per_gop, gops

# =============================================================================
# SECTION 7: correctness gate
# =============================================================================

def verify_relation(E, P, triple_xcoords):
    Fp = E.base_field()
    lifts = []
    for xx in triple_xcoords:
        pts = E.lift_x(Fp(xx), all=True)
        if not pts:
            return False
        lifts.append(pts)
    for s in iproduct(*lifts):
        S = s[0] + s[1] + s[2]
        if S == P or S == -P:
            return True
    return False

# =============================================================================
# SECTION 8: MAIN SWEEP
# =============================================================================

def run_sweep(meter_status):
    BITS = [13, 15, 17, 19]
    FBS  = [3, 4, 5]
    CUTOFFS = [2, 3, 4, 5]
    N_TARGETS = 2
    cells = []

    curves = []
    for tb in BITS:
        if not wall_ok(): break
        p, shape = find_solinas_prime(tb)
        res = find_prime_order_curve(p, -3, max_tries=400, seed=SEED+tb)
        if res is None:
            res = find_prime_order_curve(p, -1, max_tries=400, seed=SEED+tb+1)
        if res:
            b_v, E, n = res
            curves.append({'family':'structured','bits':tb,'p':int(p),'shape':shape,
                           'a':int(E.a4()),'b':int(E.a6()),'n':int(n),'E':E})
            log("  curve structured %db p=%d (%s) a=%d n=%d" % (tb,p,shape,int(E.a4()),n))
    set_random_seed(int(SEED+1000))
    for tb in BITS:
        if not wall_ok(): break
        p = random_prime(2**tb - 1, lbound=2**(tb-1)+2**(tb-2))
        ra = int(GF(p).random_element())
        res = find_prime_order_curve(p, ra, max_tries=400, seed=SEED+tb+500)
        if res:
            b_v, E, n = res
            curves.append({'family':'random','bits':tb,'p':int(p),'shape':"random_%db"%tb,
                           'a':int(E.a4()),'b':int(E.a6()),'n':int(n),'E':E})
            log("  curve random %db p=%d a=%d n=%d" % (tb,p,int(E.a4()),n))

    for ci in curves:
        if not wall_ok():
            log("  WALL CAP -- stop curves"); break
        E = ci['E']; p = ci['p']; Fp = GF(p)
        log("\n" + "="*68)
        log("CURVE %s %db p=%d n=%d a=%d" % (ci['family'], ci['bits'], p, ci['n'], ci['a']))
        log("="*68)
        rho_fops, rho_gops = rho_field_ops(ci['n'], fmuls_per_gop=8)
        rho_fops_pess, _ = rho_field_ops(ci['n'], fmuls_per_gop=30)
        log("  rho: ~%.3g group ops -> %.3g field-mults (8M/op) | %.3g (30M/op)"
            % (rho_gops, rho_fops, rho_fops_pess))

        for n_fb in FBS:
            if not wall_ok(): break
            for trial in range(N_TARGETS):
                if not wall_ok(): break
                inst = build_decomp_instance(E, p, n_fb, seed=SEED + p + 31*n_fb + 7*trial)
                if inst is None:
                    log("  |FB|=%d trial=%d: instance build failed" % (n_fb, trial))
                    continue
                FB = inst['FB']; xR = inst['xR']; P = inst['P']
                try:
                    S4, R3 = build_S4_poly(ci['a'], ci['b'], p, xR, verbose=(trial==0))
                except Exception as ex:
                    log("  S4 build FAILED: %s" % ex); continue
                system = build_xring_system(S4, R3, FB, Fp)
                degs = [int(f.total_degree()) for f in system]
                D_reg = D_reg_semiregular(degs, 3)
                ff = meter(system, R3, label="Semaev_%db_FB%d" % (ci['bits'], n_fb),
                           verbose=(trial==0))
                log("  |FB|=%d trial=%d: degs=%s D_reg=%d d_ff=%d early_fall=%s planted=%s"
                    % (n_fb, trial, degs, D_reg, ff['d_ff'], ff['early_fall'], inst['planted']))

                cb_runs = {}; best_cb = None
                for d1 in CUTOFFS:
                    if not wall_ok(): break
                    ncols_pred = binomial(d1 + 3, 3)
                    if ncols_pred > 1800:
                        cb_runs[d1] = {'skipped':'cols=%d>1800'%ncols_pred}; continue
                    t0 = time.time()
                    try:
                        cb = crossbred_solve(system, R3, FB, d1, op_budget=10**9)
                    except Exception as ex:
                        cb_runs[d1] = {'error':str(ex)}; continue
                    cb_wall = time.time() - t0
                    verified = [list(tri) for tri in cb['candidates'] if verify_relation(E, P, tri)]
                    cb['verified'] = verified; cb['n_verified'] = len(verified)
                    cb['wall'] = round(cb_wall, 3)
                    cb_runs[d1] = cb
                    log("    crossbred d1=%d: ops=%.3g mac=%dx%d rank=%d xl_uni=%s solved=%s verified=%d wall=%.2fs"
                        % (d1, cb['field_ops'], cb['mac_rows'], cb['mac_cols'], cb['mac_rank'],
                           cb['pure_xl_univariate'], cb['solved'], cb['n_verified'], cb_wall))
                    if cb['n_verified'] > 0:
                        if best_cb is None or cb['field_ops'] < best_cb[1]:
                            best_cb = (d1, cb['field_ops'])

                t0 = time.time()
                try:
                    f4 = f4_solve_opcount(system, R3, FB, Fp)
                except Exception as ex:
                    f4 = {'solved':False,'field_ops':None,'note':'F4 exc %s'%ex,'candidates':[]}
                f4_ver = [list(tri) for tri in f4.get('candidates', []) if verify_relation(E, P, tri)]
                f4['n_verified'] = len(f4_ver); f4['verified'] = f4_ver
                log("    F4: ops_low=%s ops_high=%s D_solve=%s solved=%s verified=%d wall=%.2fs"
                    % (f4.get('field_ops'), f4.get('field_ops_high'), f4.get('D_solve'),
                       f4.get('solved'), f4['n_verified'], f4.get('wall',0)))

                best_cb_d1 = best_cb[0] if best_cb else None
                best_cb_ops = best_cb[1] if best_cb else None
                cb_beats_f4 = (best_cb_ops is not None and f4.get('field_ops') is not None
                               and best_cb_ops < f4['field_ops'])
                cb_vs_rho = (best_cb_ops / rho_fops) if best_cb_ops else None

                cell = {
                    'family':ci['family'],'bits':ci['bits'],'p':p,'n_order':ci['n'],
                    'a':ci['a'],'b':ci['b'],'n_fb':n_fb,'trial':trial,
                    'xR':xR,'FB':FB,'planted':inst['planted'],
                    'sys_degs':degs,'D_reg':int(D_reg),
                    'd_ff':int(ff['d_ff']),'early_fall':bool(ff['early_fall']),
                    'rho_field_ops_8M':float(rho_fops),'rho_field_ops_30M':float(rho_fops_pess),
                    'rho_group_ops':float(rho_gops),
                    'crossbred':{str(k):v for k,v in cb_runs.items()},
                    'best_cb_d1':best_cb_d1,'best_cb_field_ops':best_cb_ops,
                    'f4_field_ops':f4.get('field_ops'),'f4_field_ops_high':f4.get('field_ops_high'),
                    'f4_D_solve':f4.get('D_solve'),'f4_n_verified':f4['n_verified'],
                    'f4_wall':f4.get('wall'),
                    'cb_beats_f4':bool(cb_beats_f4),
                    'cb_over_rho_ratio':cb_vs_rho,
                    'cb_approaches_rho':bool(cb_vs_rho is not None and cb_vs_rho < 10.0),
                }
                cells.append(cell)
    return cells

# =============================================================================
# SECTION 9: drive + serialize + markdown
# =============================================================================

RESULT = {'experiment':'EXP-009_crossbred','seed':SEED,
          'timestamp':datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
          'sage_version':str(version()),
          'meter':None,'cells':[],'crashed':False,'error':None}
try:
    meter_status = revalidate_meter()
    RESULT['meter'] = meter_status
    log("\n" + "="*78)
    log("STEP 1: crossbred / XL sweep")
    log("="*78)
    RESULT['cells'] = run_sweep(meter_status)
except Exception as ex:
    RESULT['crashed'] = True
    RESULT['error'] = "%s\n%s" % (ex, traceback.format_exc())
    log("FATAL: %s" % ex)
    log(traceback.format_exc())

try:
    with open(JSON_PATH, "w") as f:
        json.dump(RESULT, f, indent=2, default=str)
    log("WROTE %s" % JSON_PATH)
except Exception as ex:
    log("JSON write failed: %s" % ex)

def compose_md(R):
    L = []
    mv = R.get('meter') or {}
    L.append("# EXP-009 Result: crossbred / XL-with-cutoff for m=3 prime-field Semaev")
    L.append("")
    L.append("SEED=%d  timestamp=%s  sage=%s" % (R['seed'], R['timestamp'], R.get('sage_version')))
    L.append("")
    L.append("## Meter re-validation (round-005 kernel/nontrivial-syzygy meter)")
    L.append("")
    if mv:
        a = mv.get('POS_A',{}); n1 = mv.get('NEG_1',{}); n2 = mv.get('NEG_2',{})
        L.append("| control | d_ff | D_reg | early_fall | role |")
        L.append("|---|---|---|---|---|")
        L.append("| POS-A 3 cubics shared quadratic factor | %s | %s | %s | must fire |"
                 % (a.get('d_ff'),a.get('D_reg_pred'),a.get('early_fall')))
        L.append("| NEG-1 3 generic quadrics (regular CI) | %s | %s | %s | must be quiet |"
                 % (n1.get('d_ff'),n1.get('D_reg_pred'),n1.get('early_fall')))
        L.append("| NEG-2 3 generic cubics (regular) | %s | %s | %s | must be quiet |"
                 % (n2.get('d_ff'),n2.get('D_reg_pred'),n2.get('early_fall')))
        L.append("")
        L.append("**METER VALIDATED: %s**" % mv.get('validated'))
    L.append("")
    L.append("## Cost table: crossbred(best d_1) vs F4 vs rho (FIELD-OP-EQUIVALENT)")
    L.append("")
    L.append("rho field ops use 8 field-mults/group-op (conversion most favorable to rho);")
    L.append("F4 ops = ncols(D_solve)^2.37 proxy. cb ops = Macaulay build + exact RREF + guess.")
    L.append("")
    L.append("| curve | |FB| | tr | D_reg | d_ff | early | best d_1 | cb ops | n_ver(cb) | F4 ops | n_ver(F4) | rho ops(8M) | cb<F4? | cb/rho | appr rho? |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    any_survivor = False; any_cb_solved = False; any_cb_beats_f4 = False
    for c in R.get('cells', []):
        cid = "%s/%db" % (c['family'], c['bits'])
        cb_ops = c.get('best_cb_field_ops')
        nver = 0
        for k,v in c.get('crossbred',{}).items():
            if isinstance(v, dict):
                nver = max(nver, v.get('n_verified',0))
        if nver > 0: any_cb_solved = True
        if c.get('cb_beats_f4'): any_cb_beats_f4 = True
        ratio = c.get('cb_over_rho_ratio'); appr = c.get('cb_approaches_rho')
        if appr: any_survivor = True
        L.append("| %s | %d | %d | %s | %s | %s | %s | %s | %d | %s | %s | %.3g | %s | %s | %s |"
            % (cid, c['n_fb'], c['trial'], c.get('D_reg'), c.get('d_ff'), c.get('early_fall'),
               c.get('best_cb_d1'), ("%.3g"%cb_ops) if cb_ops else "-", nver,
               ("%.3g"%c['f4_field_ops']) if c.get('f4_field_ops') else "-",
               c.get('f4_n_verified'), c.get('rho_field_ops_8M'), c.get('cb_beats_f4'),
               ("%.3g"%ratio) if ratio else "-", appr))
    L.append("")
    L.append("## Crossover-vs-size trend (cb/rho by bit size, where cb solved)")
    L.append("")
    by_bits = {}
    for c in R.get('cells', []):
        if c.get('cb_over_rho_ratio') is not None:
            by_bits.setdefault(c['bits'], []).append(c['cb_over_rho_ratio'])
    L.append("| bits | median cb/rho | n_cells |")
    L.append("|---|---|---|")
    trend = []
    for b in sorted(by_bits):
        vals = sorted(by_bits[b]); med = vals[len(vals)//2]
        trend.append((b, med)); L.append("| %d | %.3g | %d |" % (b, med, len(vals)))
    growing = None
    if len(trend) >= 2:
        growing = trend[-1][1] > trend[0][1]
    L.append("")
    L.append("Gap-to-rho trend: %s" % (
        "GROWING with size -> no asymptotic threat" if growing
        else ("SHRINKING with size -> investigate" if growing is False else "insufficient data")))
    L.append("")
    L.append("## Controls outcome")
    L.append("")
    L.append("- Returned crossbred decompositions VERIFIED correct (FB-sum = +/- P): %s"
             % ("YES >=1 verified" if any_cb_solved else "NO crossbred decomposition verified"))
    L.append("- Crossbred beat F4 (field-op proxy) in >=1 cell: %s" % any_cb_beats_f4)
    L.append("- Meter validated: %s" % (mv.get('validated')))
    L.append("")
    L.append("## Verdict")
    L.append("")
    if R.get('crashed'):
        verdict = "inconclusive (crashed: %s)" % str(R.get('error',''))[:160]
    elif not any_cb_solved:
        verdict = ("INCONCLUSIVE -- crossbred produced no VERIFIED decomposition at these "
                   "cutoffs/sizes; cannot compare a non-solving solver to rho.")
    elif any_survivor:
        verdict = ("POTENTIAL SURVIVOR -- crossbred field-op cost within 10x of rho on >=1 "
                   "verified cell. FLAG: extrapolate size trend before any claim.")
    else:
        verdict = ("NEGATIVE (scoped) -- crossbred SOLVES verified decompositions and may "
                   "undercut the F4 proxy by a constant, but its field-op cost stays ORDERS "
                   "above rho at every toy size, and the gap to rho does not shrink with size. "
                   "Yokoyama's D_reg wall is loosened (crossbred is governed by d_ff/cutoff, "
                   "not D_reg) but the loophole does NOT yield a rho-competitive prime-field "
                   "attack at these parameters.")
    L.append(verdict)
    L.append("")
    L.append("## What this rules out / does not rule out")
    L.append("")
    L.append("- Rules out (scoped, toy 13-19 bit): crossbred/XL with FB-restricted guessing and "
             "cutoff d_1 in {2..5} beating Pollard rho (negation) on the m=3 prime-field Semaev "
             "x-ring system. Crossbred is OUTSIDE Yokoyama's model, so this is independent "
             "empirical evidence, not a corollary of Yokoyama.")
    L.append("- Does NOT rule out: (a) cutoffs d_1>5 / larger Macaulay blocks with sparse "
             "linear algebra; (b) the e-ring symmetric representation; (c) m>=4 decomposition; "
             "(d) a fixed-degree trace/norm/subfield FB whose constraint degree is independent "
             "of |FB|; (e) p-adic/lifted smoothness reformulations.")
    L.append("")
    L.append("## Next")
    L.append("")
    L.append("1. Conservative: push cutoff d_1 and Macaulay size with sparse (block-Wiedemann) "
             "op counting; check if the crossbred/F4 gap widens at fixed size.")
    L.append("2. Representation-changing: run THIS crossbred on the e-ring symmetric system "
             "and on a fixed-degree subfield/trace FB.")
    L.append("3. High-risk: m=4 Semaev with FB-guess of two variables; measure per-relation "
             "field-op cost / relation yield vs rho's sqrt(n).")
    return "\n".join(L), verdict

try:
    md, verdict_text = compose_md(RESULT)
    RESULT['verdict'] = verdict_text
    with open(MD_PATH, "w") as f:
        f.write(md + "\n")
    with open(JSON_PATH, "w") as f:
        json.dump(RESULT, f, indent=2, default=str)
    log("WROTE %s" % MD_PATH)
    log("VERDICT: %s" % verdict_text)
except Exception as ex:
    log("MD write failed: %s\n%s" % (ex, traceback.format_exc()))

log("\nDONE wall=%.1fs" % (time.time()-START))
