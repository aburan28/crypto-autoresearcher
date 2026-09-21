#!/usr/bin/env sage
# =============================================================================
# EXP-PFDR-4bfc6f -- Stage 1 driver (TASK-20260903-3a77d3)
#
# PROVENANCE (handoff constraint 6: "no existing file under
# experiments/EXP-ALPF-*/ is edited; reconstructions of the inline meter live
# under experiments/EXP-PFDR-4bfc6f/ with their provenance recorded").
#
# This file is NEW, lives entirely under experiments/EXP-PFDR-4bfc6f/, and
# touches no byte of any archived EXP-ALPF-* file. It contains two kinds of
# code:
#
#  (R) RECONSTRUCTION: the inline ALPF leading-form meter (top_form,
#      macaulay_homog, trivial_koszul, semireg_Dreg, meter, mons_deg, n_mons)
#      is reassembled from the two independent archived copies in
#      experiments/EXP-ALPF-009/source/round005_exp008_fixeddeg_fb.sage
#      (l.44-128) and experiments/EXP-ALPF-010/source/round005_exp009_crossbred.sage
#      (l.216-300), which agree function-for-function (diffed by this
#      session, see implementation.md). The file EXP-ALPF-011 itself
#      load()ed (round005_meter_validation.sage) is ABSENT from the archive
#      (confirmed: not present anywhere under experiments/ by this session's
#      own `find`/`git ls-files`) -- this is the O1 finding of the prior
#      dispatch TASK-20260903-06b269, reconfirmed here. The macaulay_homog_rows
#      / trivial_koszul_local / froberg_Dreg_local / top_form_local /
#      row-owner-tracked shrink-test machinery is reassembled from
#      experiments/EXP-ALPF-013/source/round007_exp012_localization_gate.sage
#      (l.83-227), independently of the round005 copies, for the shrink test
#      (P2 metric).
#
#  (V) VERBATIM EXCERPT (unmodified): the exact e-ring builder functions
#      py_seed, semaev_S3, build_S4_poly, rewrite_S4_in_e_coords,
#      build_fb_constraints_e_ring, find_solinas_prime, find_prime_order_curve
#      are copied BYTE-FOR-BYTE from
#      experiments/EXP-ALPF-011/source/round006_exp010_validated_resweep.sage
#      (line ranges recorded per-function below). Reason this file cannot
#      simply `load()` the archived .sage file directly and run its
#      top-level driver: the archived file's SECTION 0 executes
#      `load(METER_SRC)` where METER_SRC is the absent round005 file at a
#      hardcoded absolute path OUTDIR = "/Volumes/Volume/autolab/..." (l.56-57,
#      l.94-106) outside this task's write_scope
#      (experiments/EXP-PFDR-4bfc6f/ only) and outside this filesystem
#      entirely; running the archived driver top-to-bottom is therefore
#      impossible without either editing the archived file (forbidden) or
#      writing outside write_scope (forbidden). This is the SAME
#      reconstruction pattern the contract itself prescribes for the meter
#      (Stage 1), applied to the pure builder FUNCTIONS, which have no such
#      dependency -- they are extracted unmodified and driven from here.
#      A textual diff against the archived file confirms byte-identity (see
#      implementation.md, section "verbatim excerpt diff").
# =============================================================================

import sys, json, time
from datetime import datetime

OUT_JSON = "stage1_driver_result.json"
SEED = 42
_random = __import__('random')

_events = []
def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    line = "[%s] %s" % (ts, msg)
    _events.append(line)
    print(line)

set_random_seed(int(SEED))
_random.seed(int(SEED))

def py_seed(*parts):
    return int(sum(int(x) for x in parts))

# =============================================================================
# (R) RECONSTRUCTED inline meter -- from EXP-ALPF-009 l.44-128 / EXP-ALPF-010 l.216-300
# =============================================================================
from itertools import combinations_with_replacement

def mons_deg(R, d):
    o = []
    for e in combinations_with_replacement(range(R.ngens()), d):
        m = R.one()
        for i in e: m *= R.gen(i)
        o.append(m)
    return o

def n_mons(n, d):
    if d < 0: return 0
    return int(binomial(n - 1 + d, d))

def top_form(f, R):
    d = f.total_degree()
    t = R.zero()
    for mon, co in zip(f.monomials(), f.coefficients()):
        if mon.total_degree() == d: t += co * mon
    return t

def macaulay_homog(homs, R, D):
    cols = mons_deg(R, D)
    idx = {str(m): i for i, m in enumerate(cols)}
    nc = len(cols)
    Fp = R.base_ring()
    rows = []
    for h in homs:
        if h == 0: continue
        dh = int(h.total_degree())
        if dh > D: continue
        for mm in mons_deg(R, D - dh):
            g = mm * h
            row = [Fp.zero()] * nc
            for c, mon in zip(g.coefficients(), g.monomials()):
                k = str(mon)
                if k in idx: row[idx[k]] = Fp(c)
            rows.append(row)
    if not rows: return 0, nc, 0
    M = matrix(Fp, rows)
    return M.nrows(), nc, M.rank()

def trivial_koszul(degs, n, D):
    cnt = 0
    for i in range(len(degs)):
        for j in range(i + 1, len(degs)):
            cnt += n_mons(n, D - degs[i] - degs[j])
    return cnt

def semireg_Dreg(degs, n):
    Dmax = sum(degs) + 2
    PS = PowerSeriesRing(QQ, 't', default_prec=Dmax + 6)
    t = PS.gen()
    ser = prod((1 - t**int(d)) for d in degs) / (1 - t)**int(n)
    co = [QQ(ser[d]) for d in range(Dmax + 4)]
    for D in range(len(co)):
        if co[D] <= 0: return D, co
    return Dmax, co

def meter(polys, R, label="", max_D=None):
    n = R.ngens()
    degs = [int(f.total_degree()) for f in polys]
    homs = [top_form(f, R) for f in polys]
    Dreg, co = semireg_Dreg(degs, n)
    if max_D is None: max_D = Dreg
    d_ff = None
    for D in range(min(degs), min(max_D, Dreg) + 1):
        nr, nc, rk = macaulay_homog(homs, R, D)
        ker = nr - rk
        triv = trivial_koszul(degs, n, D)
        nontriv = ker - triv
        if d_ff is None and nontriv > 0:
            d_ff = D
        if d_ff is not None: break
    if d_ff is None: d_ff = Dreg
    fires = (d_ff < Dreg)
    return d_ff, Dreg, fires

def meter_here(polys, R, label=""):
    homs = [top_form(f, R) for f in polys]
    homs_nz = [h for h in homs if h != 0]
    leading_degs = sorted([int(h.total_degree()) for h in homs_nz])
    d_ff, Dreg, fires = meter(polys, R, label=label)
    return {'label': label, 'd_ff': int(d_ff), 'D_reg_pred': int(Dreg),
            'fires': bool(fires), 'leading_form_degs': leading_degs,
            'n_vars': int(R.ngens())}

# =============================================================================
# (R) RECONSTRUCTED shrink-test machinery -- from EXP-ALPF-013 l.83-227
# =============================================================================
def top_form_local(f):
    if f == 0: return f
    d = f.degree()
    R = f.parent()
    res = R(0)
    for mono, coeff in f.dict().items():
        if sum(mono) == d:
            res += coeff * R.monomial(*mono)
    return res

def _weak_compositions(D, n):
    if n == 1:
        yield (D,); return
    for first in range(D + 1):
        for rest in _weak_compositions(D - first, n - 1):
            yield (first,) + rest

def _monomials_of_degree(R, D):
    if D < 0: return []
    return [R.monomial(*comp) for comp in _weak_compositions(D, R.ngens())]

def _num_monomials(n, D):
    if D < 0: return 0
    return binomial(n - 1 + D, D)

def macaulay_homog_rows(homog_forms, R, D):
    K = R.base_ring()
    cols = _monomials_of_degree(R, D)
    col_index = {}
    for j, m in enumerate(cols):
        col_index[m.exponents()[0]] = j
    rows = []
    row_owner = []
    for i, h in enumerate(homog_forms):
        if h == 0: continue
        di = h.degree()
        if D - di < 0: continue
        for mm in _monomials_of_degree(R, D - di):
            poly = mm * h
            vec = [K(0)] * len(cols)
            for mono, coeff in poly.dict().items():
                vec[col_index[mono]] = K(coeff)
            rows.append(vec)
            row_owner.append(i)
    if len(rows) == 0:
        M = matrix(K, 0, len(cols))
    else:
        M = matrix(K, rows)
    return M, row_owner, cols

def trivial_koszul_local(degs, n, D):
    total = 0
    m = len(degs)
    for i in range(m):
        for j in range(i + 1, m):
            r = D - degs[i] - degs[j]
            if r >= 0: total += _num_monomials(n, r)
    return total

def froberg_Dreg_local(degs, n, Dmax=40):
    bound = max(Dmax, sum(int(d) for d in degs) + 4)
    Pt = PowerSeriesRing(QQ, 't', default_prec=bound + 4)
    t = Pt.gen()
    num = Pt(1)
    for d in degs: num = num * (1 - t**int(d))
    den = (1 - t)**int(n)
    series = num / den
    for D in range(bound + 1):
        if QQ(series[D]) <= 0: return D
    return None

def meter_local(polys, R, Dmax=14):
    n = R.ngens()
    forms = [top_form_local(R(f)) for f in polys]
    degs = [h.degree() for h in forms]
    D_reg = froberg_Dreg_local(degs, n, Dmax=Dmax + 4)
    d_ff = None
    nontriv_profile = {}
    Dlimit = Dmax
    if D_reg is not None: Dlimit = max(Dmax, D_reg + 1)
    for D in range(1, Dlimit + 1):
        M, row_owner, cols = macaulay_homog_rows(forms, R, D)
        nrows = M.nrows()
        if nrows == 0:
            nontriv_profile[D] = 0; continue
        rk = M.rank()
        ker = nrows - rk
        triv = trivial_koszul_local(degs, n, D)
        nontriv = ker - triv
        nontriv_profile[D] = int(nontriv)
        if d_ff is None and nontriv > 0: d_ff = D
        if d_ff is not None and D_reg is not None and D > D_reg: break
    fires = (d_ff is not None and D_reg is not None and d_ff < D_reg)
    return {"n": int(n), "degs": [int(d) for d in degs],
            "d_ff": (int(d_ff) if d_ff is not None else None),
            "D_reg": (int(D_reg) if D_reg is not None else None),
            "fires": bool(fires),
            "nontriv_profile": {int(k): int(v) for k, v in nontriv_profile.items()}}

def shrink_test(polys, R, D, sum_indices):
    """nontriv_full - nontriv_fb at degree D (P2 metric). sum_indices name the
    rows treated as 'summation' (S4) rows to remove for the FB-only subsystem."""
    n = R.ngens()
    forms = [top_form_local(R(f)) for f in polys]
    degs = [h.degree() for h in forms]
    sum_set = set(int(i) for i in sum_indices)
    fb_indices = [i for i in range(len(forms)) if i not in sum_set]
    M_full, owner_full, cols = macaulay_homog_rows(forms, R, D)
    nrows_full = M_full.nrows()
    rk_full = M_full.rank() if nrows_full > 0 else 0
    ker_full = nrows_full - rk_full
    koszul_full = trivial_koszul_local(degs, n, D)
    nontriv_full = ker_full - koszul_full
    fb_forms = [forms[i] for i in fb_indices]
    fb_degs = [degs[i] for i in fb_indices]
    M_fb, owner_fb, cols_fb = macaulay_homog_rows(fb_forms, R, D)
    nrows_fb = M_fb.nrows()
    rk_fb = M_fb.rank() if nrows_fb > 0 else 0
    ker_fb = nrows_fb - rk_fb
    koszul_fb = trivial_koszul_local(fb_degs, n, D)
    nontriv_fb = ker_fb - koszul_fb
    return {"D": int(D), "nontriv_full": int(nontriv_full), "nontriv_fb": int(nontriv_fb),
            "shrink": int(nontriv_full - nontriv_fb)}

# =============================================================================
# (V) VERBATIM EXCERPT -- byte-identical to
# experiments/EXP-ALPF-011/source/round006_exp010_validated_resweep.sage
# =============================================================================

def semaev_S3(x1, x2, x3, a, b, ring):
    # verbatim l.190-195
    Fp = ring.base_ring(); aa = Fp(a); bb = Fp(b)
    A = (x1 - x2)**2
    B = -2*((x1 + x2)*(x1*x2 + aa) + 2*bb)
    C = (x1*x2 - aa)**2 - 4*bb*(x1 + x2)
    return A*x3**2 + B*x3 + C

def build_S4_poly(a, b, p, xR_const):
    # verbatim l.197-212
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

def rewrite_S4_in_e_coords(S4, R3, Fp):
    # verbatim l.215-251
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
        if len(sample_es) >= n_sample: break
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
    # verbatim l.253-261
    e1, e2, e3 = Rsym.gens(); Fp = Rsym.base_ring()
    R_t = PolynomialRing(Rsym, 't'); t = R_t.gen()
    F_t = prod(t - Fp(xi) for xi in FB_xs)
    modulus = t**3 - e1*t**2 + e2*t - e3
    rem = F_t % modulus
    cons = [Rsym(rem[d]) for d in range(3) if Rsym(rem[d]) != Rsym.zero()]
    return cons

def find_solinas_prime(target_bits):
    # verbatim l.350-363
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
    # verbatim l.365-378
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
# STEP 0: mandatory inline meter self-validation (matches archive section 1)
# =============================================================================
def selfvalidate_meter():
    rng = _random.Random(int(101))
    Rc = PolynomialRing(GF(10007), ['x', 'y', 'z'], order='degrevlex')
    def rquad():
        return sum(GF(10007)(rng.randint(1, 10006)) * m for m in mons_deg(Rc, 2))
    def rcub():
        return sum(GF(10007)(rng.randint(1, 10006)) * m for m in mons_deg(Rc, 3))
    def rlin():
        return sum(GF(10007)(rng.randint(1, 10006)) * g for g in Rc.gens())
    q = rquad()
    posA = [rlin() * q for _ in range(3)]
    rng1 = _random.Random(int(11)); rng2 = _random.Random(int(22))
    def rquad1():
        return sum(GF(10007)(rng1.randint(1, 10006)) * m for m in mons_deg(Rc, 2))
    def rcub2():
        return sum(GF(10007)(rng2.randint(1, 10006)) * m for m in mons_deg(Rc, 3))
    neg1 = [rquad1() for _ in range(3)]
    neg2 = [rcub2() for _ in range(3)]
    rA = meter_here(posA, Rc, label="POS-A")
    r1 = meter_here(neg1, Rc, label="NEG-1")
    r2 = meter_here(neg2, Rc, label="NEG-2")
    return {'POS_A': rA, 'NEG_1': r1, 'NEG_2': r2}

log("=== STEP 0: inline meter self-validation ===")
sv = selfvalidate_meter()
for k in ('POS_A','NEG_1','NEG_2'):
    log("  %s: %s" % (k, sv[k]))

archived_expected = {
    'POS_A': {'d_ff': 4, 'D_reg_pred': 7, 'fires': True},
    'NEG_1': {'d_ff': 4, 'D_reg_pred': 4, 'fires': False},
    'NEG_2': {'d_ff': 7, 'D_reg_pred': 7, 'fires': False},
}
selfval_match = {}
for k in ('POS_A','NEG_1','NEG_2'):
    exp = archived_expected[k]; got = sv[k]
    ok = (got['d_ff']==exp['d_ff'] and got['D_reg_pred']==exp['D_reg_pred'] and got['fires']==exp['fires'])
    selfval_match[k] = bool(ok)
    log("  %s MATCH archive section-1 table: %s" % (k, ok))
METER_SELF_VALIDATED = all(selfval_match.values())
log("METER_SELF_VALIDATED = %s" % METER_SELF_VALIDATED)

# =============================================================================
# STEP 1: archive-reproduction cell -- structured 13-bit curve, e-ring, |FB| in {4,5}
# (single representative curve/prime; see implementation.md for scope note)
# =============================================================================
log("\n=== STEP 1: archive-reproduction cell (structured 13-bit, a=-3) ===")
p13, shape13 = find_solinas_prime(13)
log("  p=%d shape=%s" % (int(p13), shape13))
res = find_prime_order_curve(p13, -3, max_tries=300, seed=SEED+13)
b_v, E, n_ord = res
log("  curve a=-3 b=%d n=%d" % (b_v, n_ord))
Fp13 = GF(p13)
set_random_seed(SEED + int(p13))
P_tgt = E.random_point()
while P_tgt == E(0):
    P_tgt = E.random_point()
xR = int(P_tgt[0])
FB_pool = []
tries = 0
while len(FB_pool) < 8 and tries < 4000:
    tries += 1
    Qp = E.random_point()
    if Qp != E(0) and int(Qp[0]) not in FB_pool and int(Qp[0]) != xR:
        FB_pool.append(int(Qp[0]))
log("  xR=%d FB_pool=%s" % (xR, FB_pool))

S4, R3 = build_S4_poly(int(E.a4()), int(E.a6()), int(p13), xR)
log("  S4 total_deg=%d" % S4.total_degree())
S4sym, Rsym = rewrite_S4_in_e_coords(S4, R3, Fp13)
log("  S4sym total_deg=%d terms=%d" % (S4sym.total_degree(), len(S4sym.monomials())))
e1v, e2v, e3v = Rsym.gens()

archive_cells = {
    4: {'expected_profile': [2,2,2,4], 'expected_dff': 3, 'expected_Dreg': 4},
    5: {'expected_profile': [3,3,3,4], 'expected_dff': 4, 'expected_Dreg': 5},
}
# |FB| in {6,7,8}: NOT in the archive (the archived sweep only covers |FB| in
# {4,5}); these are new P1-ladder cells per contract Stage 2, predicted by
# stage0-predictions.yaml P1 (forced d_ff = k-1 = 5,6,7; D_reg = 7,8,10), not
# archive-reproduction cells. Recorded separately below.
p1_ladder_predicted = {6: {'dff': 5, 'Dreg': 7}, 7: {'dff': 6, 'Dreg': 8}, 8: {'dff': 7, 'Dreg': 10}}

results = {}
for n_fb in (4, 5, 6, 7, 8):
    FB_use = FB_pool[:n_fb]
    cons = build_fb_constraints_e_ring(FB_use, Rsym)
    sys_polys = [S4sym] + cons
    r = meter_here(sys_polys, Rsym, label="e-ring FB=%d" % n_fb)
    r['nontriv_at_dff'] = None
    # shrink test at d_ff: index 0 is S4sym (the "summation" row), 1.. are FB rows
    D_d_ff = r['d_ff']
    stest = shrink_test(sys_polys, Rsym, D_d_ff, sum_indices=[0])
    r['shrink_test'] = stest
    if n_fb in archive_cells:
        exp = archive_cells[n_fb]
        profile_match = (r['leading_form_degs'] == sorted(exp['expected_profile']))
        dff_match = (r['d_ff'] == exp['expected_dff'])
        dreg_match = (r['D_reg_pred'] == exp['expected_Dreg'])
        r['archive_match'] = {'profile': profile_match, 'd_ff': dff_match, 'D_reg': dreg_match}
        r['cell_kind'] = 'archive_reproduction'
    else:
        p1exp = p1_ladder_predicted[n_fb]
        r['p1_prediction_match'] = {'d_ff': r['d_ff'] == p1exp['dff'], 'D_reg': r['D_reg_pred'] == p1exp['Dreg']}
        r['cell_kind'] = 'new_p1_ladder_cell'
    log("  |FB|=%d [%s] profile=%s d_ff=%d D_reg=%d fires=%s shrink=%s"
        % (n_fb, r['cell_kind'], r['leading_form_degs'], r['d_ff'], r['D_reg_pred'], r['fires'], stest))

    # NULL-S4: replace S4sym top form's role with a random degree-4 poly in e1,e2,e3
    rngS4 = _random.Random(py_seed(SEED, n_fb, 31337))
    rand_deg4 = sum(GF(p13)(rngS4.randint(1, int(p13)-1)) * m for m in mons_deg(Rsym, 4))
    sys_nulls4 = [rand_deg4] + cons
    rn = meter_here(sys_nulls4, Rsym, label="NULL-S4 FB=%d" % n_fb)
    log("  |FB|=%d NULL-S4: d_ff=%d D_reg=%d fires=%s (predicted identical to Semaev arm: d_ff=%d,kernel=3)"
        % (n_fb, rn['d_ff'], rn['D_reg_pred'], rn['fires'], n_fb-1))

    # NULL-FB: keep genuine S4sym, replace membership constraints with random
    # polys of the SAME degree profile as the real membership constraints
    rngFB = _random.Random(py_seed(SEED, n_fb, 92653))
    deg_membership = n_fb - 2
    rand_membership = [sum(GF(p13)(rngFB.randint(1, int(p13)-1)) * m for m in mons_deg(Rsym, deg_membership))
                        for _ in range(len(cons))]
    sys_nullfb = [S4sym] + rand_membership
    rfb = meter_here(sys_nullfb, Rsym, label="NULL-FB FB=%d" % n_fb)
    log("  |FB|=%d NULL-FB: d_ff=%d D_reg=%d fires=%s (predicted: no fire)"
        % (n_fb, rfb['d_ff'], rfb['D_reg_pred'], rfb['fires']))

    # generic twin on the exact measured profile (CTRL-GENERIC-TWIN)
    rngGT = _random.Random(py_seed(SEED, n_fb, 271828))
    profile = r['leading_form_degs']
    generic_polys = [sum(GF(p13)(rngGT.randint(1, int(p13)-1)) * m for m in mons_deg(Rsym, d)) for d in profile]
    rgt = meter_here(generic_polys, Rsym, label="GENERIC-TWIN FB=%d" % n_fb)
    log("  |FB|=%d GENERIC-TWIN on profile %s: d_ff=%d D_reg=%d fires=%s (predicted: no fire, d_ff=D_reg)"
        % (n_fb, profile, rgt['d_ff'], rgt['D_reg_pred'], rgt['fires']))

    def poly_to_coeffs(f):
        # exponent tuple (over e1,e2,e3) -> int coefficient, for the F_p port cross-check
        d = {}
        for mono, coeff in f.dict().items():
            d[str(tuple(int(e) for e in mono))] = int(coeff)
        return d

    results[n_fb] = {
        'semaev_arm': r, 'null_s4': rn, 'null_fb': rfb, 'generic_twin': rgt,
        'FB_used': FB_use,
        'poly_export': {
            'S4sym': poly_to_coeffs(S4sym),
            'membership_cons': [poly_to_coeffs(c) for c in cons],
            'null_s4_poly': poly_to_coeffs(rand_deg4),
            'null_fb_polys': [poly_to_coeffs(c) for c in rand_membership],
            'generic_twin_polys': [poly_to_coeffs(g) for g in generic_polys],
            'p': int(p13),
        },
    }

out = {
    'seed': SEED,
    'sage_version': str(version()),
    'curve': {'p': int(p13), 'shape': shape13, 'a': int(E.a4()), 'b': int(E.a6()), 'n': int(n_ord), 'xR': xR, 'FB_pool': FB_pool},
    'selfvalidation': sv,
    'selfvalidation_match_archive': selfval_match,
    'meter_self_validated': bool(METER_SELF_VALIDATED),
    'e_ring_cells': results,
    'S4sym_total_degree': int(S4sym.total_degree()),
}
def _jsonable(o):
    if isinstance(o, dict):
        return {str(k): _jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_jsonable(v) for v in o]
    return o

with open(OUT_JSON, "w") as f:
    json.dump(_jsonable(out), f, indent=2, default=str)
log("\nWrote %s" % OUT_JSON)
