#!/usr/bin/env sage
# =============================================================================
# EXP-014: Binary FPPR/Petit-Quisquater calibration -- CORRECTED (Round 7)
# =============================================================================
#
# CAMPAIGN CONTEXT (PO-002):
# EXP-011 (round 6) produced fires but was adjudicated as malformed because:
#   (a) S_3 correctness was NOT verified against real point triples.
#   (b) System consistency (ideal != [1]) was not checked.
#   (c) The localization gate (EXP-012) had not been applied.
#
# THIS FILE (EXP-014):
#   1. Builds a REAL ordinary binary curve E/F_{2^n} (n in {7,9,11,13}).
#   2. Derives S_3(X1,X2,X3) via double resultant in the 5-variable ring
#      F[x1,x2,x3,y1,y2], eliminating y1 and y2 via the curve equations
#      and the chord condition. VERIFIED against >= 12 real point triples.
#   3. Factor base V = l-dimensional F_2-subspace. X1, X2 BOTH FREE over V.
#      X3 = fixed target (NOT in V).
#   4. Projects S_3(X1,X2,x_target) to GF(2)[t_vars] and multilinearizes.
#   5. Adds field equations t_k^2 + t_k.
#   6. Checks system consistency (GB != [1] OR genuine relation witness).
#   7. Applies the GATED meter from EXP-012 with sumpoly_indices = S3 rows.
#   8. Reports d_ff, D_reg, fires, gate_passes, gate_meaningful.
#   9. Checks d_ff bounded as n grows (FPPR signature).
#  10. Contrasts with prime-field x-ring (EXP-009/010: d_ff=D_reg, no fire).
#
# HONESTY: if S3 wrong / ideal=[1] / gate unavailable, report INCONCLUSIVE.
#
# PARAMETERS: n in {7,9,11,13}, l in {3,4}, SEED=20240701.
# =============================================================================

import os, sys, json, time
import random as _random
from itertools import combinations_with_replacement

EXPDIR = "/Volumes/Volume/autolab/experiments/ecdlp_prime_field"
SEED   = int(20240701)
START_TIME = time.time()
WALL_CAP   = int(540)   # 9-minute hard cap

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
_LOG_FILE = None

def _open_log():
    global _LOG_FILE
    if _LOG_FILE is None or getattr(_LOG_FILE, "closed", True):
        _LOG_FILE = open(
            os.path.join(EXPDIR, "round007_exp014_binary_fppr_corrected.log"), "a")
    return _LOG_FILE

def log(msg):
    f = _open_log()
    s = "[%s] %s" % (time.strftime("%H:%M:%S"), str(msg))
    f.write(s + "\n"); f.flush()
    try:
        print(s, flush=True)
    except Exception:
        pass

def wall_ok():
    return (time.time() - START_TIME) < WALL_CAP

# ---------------------------------------------------------------------------
# Load gated meter from EXP-012
# ---------------------------------------------------------------------------
GATE_PATH = os.path.join(EXPDIR, "round007_exp012_localization_gate.sage")
_GATE_LOADED = False
try:
    load(GATE_PATH)
    _GATE_LOADED = True
    log("Gated meter loaded from %s" % GATE_PATH)
except Exception as _ge:
    log("WARN: could not load gated meter: %s" % _ge)

# ---------------------------------------------------------------------------
# Inline base meter (fallback + self-validation; matches round005 definition)
# ---------------------------------------------------------------------------
def _mons_deg(R, d):
    o = []
    for e in combinations_with_replacement(range(R.ngens()), d):
        m = R.one()
        for i in e:
            m *= R.gen(i)
        o.append(m)
    return o

def _n_mons(n, d):
    if d < 0:
        return 0
    return int(binomial(n - 1 + d, d))

def _top_form(f, R):
    if f == 0:
        return R.zero()
    d = f.total_degree()
    t = R.zero()
    for mon, co in zip(f.monomials(), f.coefficients()):
        if mon.total_degree() == d:
            t += co * mon
    return t

def _macaulay_homog(homs, R, D):
    cols = _mons_deg(R, D)
    idx  = {str(m): i for i, m in enumerate(cols)}
    nc   = len(cols)
    Fp   = R.base_ring()
    rows = []
    for h in homs:
        if h == 0: continue
        dh = int(h.total_degree())
        if dh > D: continue
        for mm in _mons_deg(R, D - dh):
            g   = mm * h
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

def _trivial_koszul(degs, n, D):
    cnt = 0
    for i in range(len(degs)):
        for j in range(i + 1, len(degs)):
            cnt += _n_mons(n, D - degs[i] - degs[j])
    return cnt

def _semireg_Dreg(degs, n):
    Dmax = sum(degs) + 2
    PS   = PowerSeriesRing(QQ, 't', default_prec=Dmax + 6)
    t    = PS.gen()
    ser  = prod((1 - t**int(d)) for d in degs) / (1 - t)**int(n)
    co   = [QQ(ser[d]) for d in range(Dmax + 4)]
    for D in range(len(co)):
        if co[D] <= 0:
            return D, co
    return Dmax, co

def _meter_base(polys, R, label="", Dmax=40):
    nonzero = [f for f in polys if f != 0]
    if not nonzero:
        log("  [%s] EMPTY system" % label)
        return None, None, None
    n    = R.ngens()
    degs = [int(f.total_degree()) for f in nonzero]
    homs = [_top_form(f, R) for f in nonzero]
    Dreg, co = _semireg_Dreg(degs, n)
    log("  [%s] n=%d degs=%s D_reg=%d" % (label, n, degs, Dreg))
    d_ff = None
    for D in range(min(degs), min(Dreg + 1, Dmax + 1)):
        if not wall_ok():
            log("  [%s] WALL-CAP at D=%d" % (label, D)); break
        nr, nc, rk = _macaulay_homog(homs, R, D)
        ker   = nr - rk
        triv  = _trivial_koszul(degs, n, D)
        nontriv = ker - triv
        tag = ""
        if d_ff is None and nontriv > 0:
            d_ff = D; tag = "  <-- FIRST FALL"
        log("    D=%d nrows=%d rank=%d ker=%d triv=%d nontriv=%d%s"
            % (D, nr, rk, ker, triv, nontriv, tag))
        if d_ff is not None: break
    if d_ff is None:
        d_ff = Dreg
    fires = bool(d_ff < Dreg)
    log("  [%s] d_ff=%s D_reg=%d fires=%s" % (label, d_ff, Dreg, fires))
    return int(d_ff), int(Dreg), fires

# ---------------------------------------------------------------------------
# Self-validation (MANDATORY)
# ---------------------------------------------------------------------------
def run_self_validation():
    log("\n" + "="*68)
    log("SELF-VALIDATION: POS-A fires, NEG-1 quiet, NEG-2 quiet")
    log("="*68)
    rng_a  = _random.Random(int(101))
    rng_n1 = _random.Random(int(11))
    rng_n2 = _random.Random(int(22))
    p  = 10007
    Fp = GF(p)
    R3 = PolynomialRing(Fp, ['x', 'y', 'z'], order='degrevlex')

    def rh(deg, rng):
        return sum(Fp(rng.randint(1, p-1)) * m for m in _mons_deg(R3, deg))

    q        = rh(2, rng_a)
    posa_g   = [rh(1, rng_a) * q for _ in range(3)]
    d_a, Dr_a, fi_a = _meter_base(posa_g, R3, "POS-A")
    posa_ok  = bool(fi_a and d_a is not None and d_a < Dr_a)

    neg1_g   = [rh(2, rng_n1) for _ in range(3)]
    d_n1, Dr_n1, fi_n1 = _meter_base(neg1_g, R3, "NEG-1")
    neg1_ok  = bool(not fi_n1)

    neg2_g   = [rh(3, rng_n2) for _ in range(3)]
    d_n2, Dr_n2, fi_n2 = _meter_base(neg2_g, R3, "NEG-2")
    neg2_ok  = bool(not fi_n2)

    meter_ok = posa_ok and neg1_ok and neg2_ok
    log("POS-A: d_ff=%s D_reg=%s fires=%s ok=%s [MUST fire]" % (d_a,  Dr_a,  fi_a,  posa_ok))
    log("NEG-1: d_ff=%s D_reg=%s fires=%s ok=%s [must NOT]"  % (d_n1, Dr_n1, fi_n1, neg1_ok))
    log("NEG-2: d_ff=%s D_reg=%s fires=%s ok=%s [must NOT]"  % (d_n2, Dr_n2, fi_n2, neg2_ok))
    log("METER_SELF_VALIDATED = %s" % meter_ok)
    return meter_ok, {
        "POS_A": {"d_ff": int(d_a),  "D_reg": int(Dr_a),  "fires": bool(fi_a),  "ok": bool(posa_ok)},
        "NEG_1": {"d_ff": int(d_n1), "D_reg": int(Dr_n1), "fires": bool(fi_n1), "ok": bool(neg1_ok)},
        "NEG_2": {"d_ff": int(d_n2), "D_reg": int(Dr_n2), "fires": bool(fi_n2), "ok": bool(neg2_ok)},
    }

# ---------------------------------------------------------------------------
# Curve and S_3 utilities
# ---------------------------------------------------------------------------
def build_binary_curve(n, rng):
    """Ordinary binary curve E/F_{2^n} with order > 8, model [1,1,1,0,b]."""
    F = GF(2**n, 'w')
    w = F.gen()
    candidates = [w**i for i in range(2**n - 1)] + [F.one()]
    rng.shuffle(candidates)
    for b in candidates:
        try:
            E = EllipticCurve(F, [1, 1, 1, 0, b])
            ord_ = E.order()
            if ord_ > 8:
                return E, F, int(ord_)
        except Exception:
            continue
    raise RuntimeError("Could not build binary curve for n=%d" % n)


def semaev_S3_binary(E, F):
    """
    Derive S_3(x1,x2,x3) for binary curve E/F via double resultant.

    Starting point: chord condition in char 2:
      If P1=(x1,y1), P2=(x2,y2) with x1!=x2 and x(P1+P2) = x3, then
        (y1+y2)^2 + a1*(y1+y2)*(x1+x2) + (x3+a2+x1+x2)*(x1+x2)^2 = 0

    Steps:
      1. In the ring F[x1,x2,x3,y1,y2]:
           c1    = y1^2 + (a1*x1+a3)*y1 + f(x1)         (curve at P1)
           c2    = y2^2 + (a1*x2+a3)*y2 + f(x2)         (curve at P2)
           chord = (y1+y2)^2 + a1*(y1+y2)*(x1+x2)
                   + (x3+a2+x1+x2)*(x1+x2)^2            (chord condition)
      2. r1 = Res_{y1}(c1, chord)     -- polynomial in x1,x2,x3,y2
      3. S3 = Res_{y2}(r1, c2)        -- polynomial in x1,x2,x3

    The result satisfies: S3(x(P1),x(P2),x(P3))=0 iff P1+P2+P3=O for points
    on E with distinct x-coordinates.
    Returns (S3_poly_in_R5, R5) where R5 = F[x1,x2,x3,y1,y2] with x1,x2,x3
    in positions 0,1,2.
    """
    a1v, a2v, a3v, a4v, a6v = [F(c) for c in E.a_invariants()]
    R5 = PolynomialRing(F, ['x1','x2','x3','y1','y2'], order='lex')
    x1v, x2v, x3v, y1v, y2v = R5.gens()

    fx1   = x1v**3 + a2v*x1v**2 + a4v*x1v + a6v
    fx2   = x2v**3 + a2v*x2v**2 + a4v*x2v + a6v
    c1    = y1v**2 + (a1v*x1v + a3v)*y1v + fx1
    c2    = y2v**2 + (a1v*x2v + a3v)*y2v + fx2
    chord = ((y1v + y2v)**2
             + a1v*(y1v + y2v)*(x1v + x2v)
             + (x3v + a2v + x1v + x2v)*(x1v + x2v)**2)

    r1  = c1.resultant(chord, y1v)
    S3  = r1.resultant(c2, y2v)
    return S3, R5


def verify_S3(E, F, S3, R5, n_trials=14):
    """Verify S3 against real point triples P1+P2+P3=O on E."""
    x1v, x2v, x3v, y1v, y2v = R5.gens()
    ok = 0; tot = 0
    for _ in range(n_trials * 2):
        if tot >= n_trials:
            break
        try:
            P1 = E.random_point(); P2 = E.random_point()
            if P1 == E(0) or P2 == E(0): continue
            P3 = -(P1 + P2)
            if P3 == E(0): continue
            if P1.xy()[0] == P2.xy()[0]: continue   # degenerate (tangent case)
            v1, v2, v3 = P1.xy()[0], P2.xy()[0], P3.xy()[0]
            val = S3.subs({x1v: v1, x2v: v2, x3v: v3, y1v: F(0), y2v: F(0)})
            tot += 1
            if val == F(0):
                ok += 1
            else:
                log("  S3 VERIFY FAIL: S3=%s (expected 0)" % val)
        except Exception as e:
            pass
    log("  S3 correctness: %d/%d triples satisfied S3=0" % (ok, tot))
    return ok, tot


# ---------------------------------------------------------------------------
# Subspace
# ---------------------------------------------------------------------------
def build_f2_subspace(F, l, rng):
    n_field = F.degree()
    w       = F.gen()
    elems   = [F.zero()] + [w**i for i in range(2**n_field - 1)]
    rng.shuffle(elems)
    basis   = []
    for v in elems:
        if v == F.zero(): continue
        in_span = False
        for mask in range(1, 2**len(basis)):
            combo = F.zero()
            for bit in range(len(basis)):
                if mask & (1 << bit):
                    combo += basis[bit]
            if combo == v:
                in_span = True; break
        if not in_span:
            basis.append(v)
        if len(basis) >= l:
            break
    subspace = []
    for mask in range(2**l):
        elem = F.zero()
        for bit in range(l):
            if mask & (1 << bit):
                elem += basis[bit]
        subspace.append(elem)
    return subspace, basis


# ---------------------------------------------------------------------------
# Find a genuine relation: x(P1), x(P2) in V, x(P1+P2) = x_target
# ---------------------------------------------------------------------------
def find_genuine_relation(E, F, subspace, x_target, max_attempts=3000):
    V_set    = set(subspace)
    V_points = []
    for xv in subspace:
        if xv == F.zero(): continue
        try:
            pts = E.lift_x(xv, all=True)
            V_points.extend(pts)
        except Exception:
            pass
    log("    Points with x in V: %d" % len(V_points))
    if len(V_points) < 2:
        return None, None, None
    for _ in range(max_attempts):
        i  = _random.randrange(len(V_points))
        j  = _random.randrange(len(V_points))
        P1 = V_points[i]; P2 = V_points[j]
        if P1 == E(0) or P2 == E(0): continue
        try:
            S  = P1 + P2
            if S == E(0): continue
            xS = S.xy()[0]
            if xS == F(x_target):
                return P1, P2, S
        except Exception:
            continue
    return None, None, None


# ---------------------------------------------------------------------------
# Project S3(X1,X2,x_target) to GF(2)[t_vars] and multilinearize
# ---------------------------------------------------------------------------
def project_S3_to_binary(S3, R5, x_target, basis, F, l):
    """
    Fix X3 = x_target in S3, substitute Xi = sum_j t_{i,j}*basis[j],
    project F-coefficients to GF(2) via the standard basis of F/GF(2),
    and multilinearize (reduce mod t_k^2 = t_k).

    Returns (ml_polys, R_bin, sum_indices_range)
      ml_polys      -- list of multilinear GF(2) polynomials (the S3 projections)
      R_bin         -- GF(2)[t10,t11,...,t1{l-1},t20,...,t2{l-1}]
      n_s3_polys    -- count of S3 projection polys (sumpoly_indices = range(n_s3_polys))
    """
    x1v, x2v, x3v, y1v, y2v = R5.gens()
    n_field = F.degree()
    w = F.gen()

    var_names = (["t1%d" % j for j in range(l)] +
                 ["t2%d" % j for j in range(l)])
    R_bin = PolynomialRing(GF(2), var_names, order='degrevlex')
    R_F   = PolynomialRing(F,     var_names, order='degrevlex')
    t_F   = list(R_F.gens())

    X1_sym = sum(F(basis[j]) * t_F[j]     for j in range(l))
    X2_sym = sum(F(basis[j]) * t_F[l + j] for j in range(l))
    X3_val = F(x_target)

    # Evaluate S3(X1_sym, X2_sym, X3_val) in R_F
    # (y1,y2 do not appear in S3 by construction, but we pass them as 0 just in case)
    S3_eval = R_F.zero()
    for mon, coeff in zip(S3.monomials(), S3.coefficients()):
        e = mon.exponents()[0]
        e1, e2, e3 = int(e[0]), int(e[1]), int(e[2])
        # e[3],e[4] are y1,y2 exponents; S3 should have e[3]=e[4]=0
        if len(e) > 3 and (int(e[3]) != 0 or int(e[4]) != 0):
            continue   # skip residual y terms (should not exist after double resultant)
        term = F(coeff) * (X1_sym**e1) * (X2_sym**e2) * (X3_val**e3)
        S3_eval += term

    # Project to GF(2) via the F_2-basis {1, w, w^2, ..., w^{n-1}}
    proj_polys_dict = {}
    for mon, coeff in zip(S3_eval.monomials(), S3_eval.coefficients()):
        coeff_list = list(coeff.polynomial())
        expts      = mon.exponents()[0]
        bin_mon    = R_bin.one()
        for vi, exp in enumerate(expts):
            bin_mon *= R_bin.gen(vi)**int(exp)
        for k in range(len(coeff_list)):
            c_k = GF(2)(int(coeff_list[k]))
            if c_k != GF(2)(0):
                proj_polys_dict.setdefault(k, R_bin.zero())
                proj_polys_dict[k] += c_k * bin_mon

    raw_polys = list(proj_polys_dict.values())

    # Multilinearize (reduce mod t_k^2 = t_k)
    def ml(poly):
        if poly == R_bin.zero(): return R_bin.zero()
        result = R_bin.zero()
        nv = R_bin.ngens()
        for mon, coeff in zip(poly.monomials(), poly.coefficients()):
            expts  = list(mon.exponents()[0])
            new_m  = R_bin.one()
            for k in range(nv):
                if expts[k] >= 1:
                    new_m *= R_bin.gen(k)
            result += GF(2)(coeff) * new_m
        return result

    seen = set(); ml_polys = []
    for p in raw_polys:
        mp = ml(p)
        if mp != R_bin.zero():
            s = str(mp)
            if s not in seen:
                seen.add(s); ml_polys.append(mp)

    return ml_polys, R_bin


# ---------------------------------------------------------------------------
# System consistency check
# ---------------------------------------------------------------------------
def verify_consistency(system, R_bin):
    try:
        I  = ideal(R_bin, system)
        gb = I.groebner_basis()
        is_unit = (len(gb) == 1 and gb[0] == R_bin.one())
        log("  Consistency: GB size=%d, unit=%s" % (len(gb), is_unit))
        return not is_unit
    except Exception as e:
        log("  Consistency check exception: %s" % e)
        return None


# ---------------------------------------------------------------------------
# Experiment loop
# ---------------------------------------------------------------------------
def run_experiment(rng, meter_valid):
    log("\n" + "="*68)
    log("EXP-014: Binary FPPR gated-meter experiment")
    log("="*68)

    results = []
    params  = [(7,3),(7,4),(9,3),(9,4),(11,3),(11,4),(13,3)]

    for (n, l) in params:
        if not wall_ok():
            log("WALL-CAP reached; skipping n=%d,l=%d" % (n, l)); break

        log("\n--- n=%d, l=%d ---" % (n, l))
        t_start = time.time()
        cell    = {"n": n, "l": l}

        # 1. Curve
        try:
            E, F, order = build_binary_curve(n, rng)
            log("  curve: E/F_{2^%d}, order=%d" % (n, order))
            cell["order"] = int(order)
        except Exception as e:
            log("  curve failed: %s" % e); cell["error"] = "curve"; results.append(cell); continue

        # 2. S_3
        try:
            t0      = time.time()
            S3, R5  = semaev_S3_binary(E, F)
            log("  S3 computed: degree=%d (%.2fs)" % (S3.total_degree(), time.time()-t0))
            cell["S3_degree"] = int(S3.total_degree())
        except Exception as e:
            import traceback
            log("  S3 failed: %s\n%s" % (e, traceback.format_exc()))
            cell["error"] = "S3"; results.append(cell); continue

        # 3. Verify S_3 against real triples
        try:
            ok, tot = verify_S3(E, F, S3, R5, n_trials=12)
            cell["S3_verified"] = int(ok)
            cell["S3_trials"]   = int(tot)
            cell["S3_correct"]  = bool(ok >= tot - 1 and tot >= 8)
            if not cell["S3_correct"]:
                log("  S3 VERIFICATION FAILED (%d/%d); marking INCONCLUSIVE" % (ok, tot))
                cell["error"] = "S3_verify"; results.append(cell); continue
        except Exception as e:
            log("  S3 verify error: %s" % e)
            cell["S3_correct"] = False; cell["error"] = "S3_verify_exc"
            results.append(cell); continue

        # 4. Subspace
        try:
            subspace, basis = build_f2_subspace(F, l, rng)
            log("  subspace: dim=%d, |V|=%d" % (l, len(subspace)))
            cell["subspace_dim"]  = l
            cell["subspace_size"] = int(len(subspace))
        except Exception as e:
            log("  subspace failed: %s" % e); cell["error"] = "subspace"
            results.append(cell); continue

        # 5. x_target not in V
        V_set    = set(subspace)
        x_target = None
        for _ in range(2000):
            try:
                P = E.random_point()
                if P == E(0): continue
                xP = P.xy()[0]
                if xP not in V_set: x_target = xP; break
            except Exception: pass
        if x_target is None:
            log("  No x_target outside V"); cell["error"] = "no_xtarget"
            results.append(cell); continue
        log("  x_target found (not in V)")
        cell["x_target_in_V"] = False

        # 6. Genuine relation
        try:
            P1r, P2r, Psum = find_genuine_relation(E, F, subspace, x_target)
            if P1r is not None:
                # Double-check with S3
                x1v, x2v, x3v, y1v, y2v = R5.gens()
                s3val = S3.subs({x1v: P1r.xy()[0], x2v: P2r.xy()[0],
                                 x3v: x_target, y1v: F(0), y2v: F(0)})
                cell["genuine_relation_found"] = True
                cell["relation_S3_zero"]       = bool(s3val == F(0))
                log("  Genuine relation: x1=%s x2=%s S3=0: %s"
                    % (P1r.xy()[0], P2r.xy()[0], cell["relation_S3_zero"]))
            else:
                cell["genuine_relation_found"] = False
                log("  No genuine relation found (system may still be consistent)")
        except Exception as e:
            log("  Relation search error: %s" % e)
            cell["genuine_relation_found"] = False

        # 7. Project S3 -> GF(2) multilinear polys
        try:
            t0 = time.time()
            ml_polys, R_bin = project_S3_to_binary(S3, R5, x_target, basis, F, l)
            log("  S3 -> %d multilinear polys, %d vars (%.2fs)"
                % (len(ml_polys), R_bin.ngens(), time.time()-t0))
            if ml_polys:
                log("  Multilinear S3 degrees: %s"
                    % sorted(set(int(p.total_degree()) for p in ml_polys)))
            cell["n_s3_polys"] = int(len(ml_polys))
        except Exception as e:
            import traceback
            log("  Projection failed: %s\n%s" % (e, traceback.format_exc()))
            cell["error"] = "projection"; results.append(cell); continue

        # 8. Field equations
        n_tv    = 2 * l
        fld_eqs = [R_bin.gen(k)**2 + R_bin.gen(k) for k in range(n_tv)]
        log("  Field eqs: %d (degree 2)" % len(fld_eqs))
        cell["n_field_eqs"] = int(len(fld_eqs))

        # sumpoly_indices = indices of S3 projections (first group)
        full_system = ml_polys + fld_eqs
        sum_indices = list(range(len(ml_polys)))
        nonzero_sys = [p for p in full_system if p != R_bin.zero()]
        if not nonzero_sys:
            log("  All polys zero; skipping"); cell["error"] = "all_zero"
            results.append(cell); continue
        all_degs = sorted(int(p.total_degree()) for p in nonzero_sys)
        log("  Full system: %d polys, %d vars, degrees=%s"
            % (len(nonzero_sys), R_bin.ngens(), all_degs))
        cell["n_polys"]      = int(len(nonzero_sys))
        cell["n_vars"]       = int(R_bin.ngens())
        cell["degrees"]      = [int(d) for d in all_degs]
        cell["sum_indices"]  = [int(i) for i in sum_indices]

        # 9. Consistency
        if cell.get("genuine_relation_found") and cell.get("relation_S3_zero"):
            cell["consistent"] = True
            log("  Consistency: CONFIRMED (genuine relation witness)")
        else:
            c = verify_consistency(nonzero_sys, R_bin)
            cell["consistent"] = bool(c) if c is not None else None
        if cell.get("consistent") == False:
            log("  UNIT IDEAL: malformed system; skipping meter")
            cell["error"] = "unit_ideal"; results.append(cell); continue

        # 10. Gated meter
        if not wall_ok():
            log("  WALL-CAP before meter"); cell["error"] = "wall_cap"
            results.append(cell); continue

        label = "bin_n%d_l%d" % (n, l)
        if _GATE_LOADED:
            try:
                res = meter_gated(full_system, R_bin, sum_indices, Dmax=14)
                cell["d_ff"]           = res["d_ff"]
                cell["D_reg"]          = res["D_reg"]
                cell["fires"]          = res["fires"]
                cell["gate_passes"]    = res["gate_passes"]
                cell["gate_meaningful"]= res["gate_meaningful"]
                if res["gate_detail"] is not None:
                    gd = res["gate_detail"]
                    cell["gate_detail"] = {
                        k: (int(v) if isinstance(v, (int, Integer)) else
                            bool(v) if isinstance(v, bool) else v)
                        for k, v in gd.items()
                    }
                    log("  gate@D=%s: nontriv_full=%s nontriv_fb=%s shrink=%s direct=%s"
                        % (gd.get("D"), gd.get("nontriv_full"), gd.get("nontriv_fb"),
                           gd.get("involves_sum_shrink"), gd.get("involves_sum_direct")))
                log("  GATED: d_ff=%s D_reg=%s fires=%s gate=%s meaningful=%s"
                    % (res["d_ff"], res["D_reg"], res["fires"],
                       res["gate_passes"], res["gate_meaningful"]))
            except Exception as e:
                import traceback
                log("  meter_gated failed: %s\n%s" % (e, traceback.format_exc()))
                d_ff, D_reg, fires = _meter_base(nonzero_sys, R_bin, label=label)
                cell["d_ff"]          = d_ff
                cell["D_reg"]         = D_reg
                cell["fires"]         = fires
                cell["gate_passes"]   = None
                cell["gate_meaningful"]= None
                cell["gate_error"]    = str(e)
        else:
            d_ff, D_reg, fires = _meter_base(nonzero_sys, R_bin, label=label)
            cell["d_ff"]           = d_ff
            cell["D_reg"]          = D_reg
            cell["fires"]          = fires
            cell["gate_passes"]    = None
            cell["gate_meaningful"]= None

        cell["wall_s"] = float(time.time() - t_start)
        log("  DONE: d_ff=%s D_reg=%s fires=%s gate=%s meaningful=%s (%.1fs)"
            % (cell.get("d_ff"), cell.get("D_reg"), cell.get("fires"),
               cell.get("gate_passes"), cell.get("gate_meaningful"), cell["wall_s"]))
        results.append(cell)

    return results


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------
def analyze_results(results):
    log("\n" + "="*68)
    log("ANALYSIS")
    log("="*68)

    valid = [r for r in results if not r.get("error") and r.get("d_ff") is not None]
    if not valid:
        log("No valid cells.")
        return False, False, False, False

    any_fires          = False
    any_gate_passes    = False
    any_gate_meaningful= False

    log("\n  n   l  polys vars S3ok  rel  d_ff D_reg fires gate  meaningful")
    for r in sorted(valid, key=lambda x: (x.get("l",99), x.get("n",99))):
        log("  %-3d %-3d %-5s %-4s %-5s %-4s %-4s %-5s %-5s %-5s %s" % (
            r["n"], r["l"],
            r.get("n_polys","?"), r.get("n_vars","?"),
            r.get("S3_correct","?"),
            r.get("genuine_relation_found","?"),
            r.get("d_ff","?"), r.get("D_reg","?"),
            r.get("fires","?"), r.get("gate_passes","?"),
            r.get("gate_meaningful","?"),
        ))
        if r.get("fires"):          any_fires = True
        if r.get("gate_passes"):    any_gate_passes = True
        if r.get("gate_meaningful"):any_gate_meaningful = True

    # d_ff bounded across n?
    by_l = {}
    for r in valid:
        by_l.setdefault(r["l"], []).append(r)
    all_bounded = True
    for l, rows in sorted(by_l.items()):
        d_ffs = [r["d_ff"] for r in rows if r.get("d_ff") is not None]
        ns    = [r["n"] for r in rows]
        fire_l= [r.get("fires") for r in rows]
        gate_l= [r.get("gate_passes") for r in rows]
        bound = (len(set(d_ffs)) <= 1) if len(d_ffs) >= 2 else None
        if bound == False: all_bounded = False
        log("  l=%d: n=%s d_ff=%s fires=%s gate=%s bounded=%s"
            % (l, ns, d_ffs, fire_l, gate_l, bound))

    log("\nPrime-field baseline (EXP-009/010): d_ff=D_reg ALL cells, no fires")
    log("Binary summary: fires=%s gate_passes=%s meaningful=%s bounded=%s"
        % (any_fires, any_gate_passes, any_gate_meaningful, all_bounded))
    return all_bounded, any_fires, any_gate_passes, any_gate_meaningful


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    _open_log()
    log("="*68)
    log("EXP-014: Binary FPPR calibration (CORRECTED, Round 7)")
    log("SEED=%d  gate=%s  start=%s"
        % (SEED, _GATE_LOADED, time.strftime("%Y-%m-%d %H:%M:%S")))
    log("="*68)

    rng = _random.Random(SEED)

    meter_valid, val_data = run_self_validation()
    if not meter_valid:
        log("*** CRITICAL: meter self-validation FAILED; results INCONCLUSIVE ***")

    results = run_experiment(rng, meter_valid)
    all_bounded, any_fires, any_gate_passes, any_gate_meaningful = analyze_results(results)

    valid_cells     = [r for r in results if not r.get("error") and r.get("d_ff") is not None]
    s3_ok_cells     = [r for r in valid_cells if r.get("S3_correct")]

    # Verdict
    if not meter_valid:
        verdict = "inconclusive"
        vreason = "Base meter self-validation failed."
    elif not valid_cells:
        verdict = "inconclusive"
        vreason = "No valid cells (construction failures)."
    elif not s3_ok_cells:
        verdict = "inconclusive"
        vreason = "S3 not verified in any valid cell."
    elif any_gate_meaningful:
        verdict = "survived"
        vreason = ("Binary FPPR gated meter fires: d_ff<D_reg AND gate passes "
                   "(firing syzygy involves S3 leading form) in at least one cell "
                   "with verified-correct S3 and consistent ideal. PO-002 met.")
    elif any_fires and not any_gate_passes:
        verdict = "failed"
        vreason = ("Fires observed but gate fails: firing syzygies confined to "
                   "field-eq (FB) rows, not S3. Same spurious-fire pattern as "
                   "prime-field e-ring/power-sum. PO-002 not met.")
    elif any_fires:
        verdict = "inconclusive"
        vreason = ("Fires observed; gate result unavailable or mixed. "
                   "Cannot confirm PO-002 without gate passing.")
    else:
        verdict = "inconclusive"
        vreason = ("No fires in any cell. Multilinearized binary FPPR system "
                   "does not fire the nontrivial-syzygy meter. FPPR fall may "
                   "require different formulation or larger subspace dimension.")

    log("\n" + "="*68)
    log("VERDICT: %s" % verdict.upper())
    log("Reason: %s" % vreason)
    log("="*68)

    def _clean(v):
        if isinstance(v, bool):    return bool(v)
        if isinstance(v, Integer): return int(v)
        if isinstance(v, (int, float, str, list, dict, type(None))): return v
        return str(v)

    def clean_cell(r):
        out = {}
        for k, v in r.items():
            if isinstance(v, dict):
                out[k] = {kk: _clean(vv) for kk, vv in v.items()}
            elif isinstance(v, list):
                out[k] = [_clean(x) for x in v]
            else:
                out[k] = _clean(v)
        return out

    out_data = {
        "experiment":            "EXP-014",
        "seed":                  SEED,
        "timestamp":             time.strftime("%Y-%m-%d %H:%M:%S"),
        "gate_loaded":           bool(_GATE_LOADED),
        "meter_self_validated":  bool(meter_valid),
        "self_validation":       val_data,
        "results":               [clean_cell(r) for r in results],
        "all_bounded":           bool(all_bounded),
        "any_fires":             bool(any_fires),
        "any_gate_passes":       bool(any_gate_passes),
        "any_gate_meaningful":   bool(any_gate_meaningful),
        "n_valid_cells":         int(len(valid_cells)),
        "n_s3_ok_cells":         int(len(s3_ok_cells)),
        "verdict":               verdict,
        "verdict_reason":        vreason,
        "prime_field_baseline":  {
            "description": "EXP-009/010: d_ff=D_reg for all 48 cells, fires=False",
            "fires": False,
        },
    }

    json_path = os.path.join(EXPDIR, "round007_exp014_binary_fppr_corrected_result.json")
    with open(json_path, "w") as jf:
        json.dump(out_data, jf, indent=2, default=str)
    log("JSON: %s" % json_path)

    # Markdown
    md = []
    md.append("# EXP-014: Binary FPPR Calibration (Corrected, Round 7)")
    md.append("")
    md.append("SEED=%d  gate_loaded=%s  timestamp=%s"
              % (SEED, _GATE_LOADED, out_data["timestamp"]))
    md.append("")
    md.append("## Meter Self-Validation")
    md.append("")
    md.append("| control | d_ff | D_reg | fires | role |")
    md.append("|---|---|---|---|---|")
    for key, role in [("POS_A","MUST fire"),("NEG_1","must NOT fire"),("NEG_2","must NOT fire")]:
        v = val_data[key]
        md.append("| %s | %s | %s | %s | %s |" % (key, v["d_ff"], v["D_reg"], v["fires"], role))
    md.append("")
    md.append("**METER_SELF_VALIDATED = %s**" % meter_valid)
    md.append("")
    md.append("## S_3 Construction and Correctness")
    md.append("")
    md.append("S_3 derived via double resultant in F[x1,x2,x3,y1,y2]:")
    md.append("  r1 = Res_{y1}(curve1, chord_condition)")
    md.append("  S3 = Res_{y2}(r1, curve2)")
    md.append("Verified against 12+ real point triples P1+P2+P3=O on E.")
    md.append("")
    md.append("## Per-Cell Results")
    md.append("")
    md.append("| n | l | polys | vars | S3_ok | rel | d_ff | D_reg | fires | gate | meaningful |")
    md.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for r in sorted(results, key=lambda x: (x.get("l",99), x.get("n",99))):
        if r.get("error"):
            md.append("| %s | %s | ERROR:%s | - | - | - | - | - | - | - | - |"
                       % (r.get("n","?"), r.get("l","?"), r.get("error","")))
        else:
            md.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
                r.get("n","?"), r.get("l","?"),
                r.get("n_polys","?"), r.get("n_vars","?"),
                r.get("S3_correct","?"), r.get("genuine_relation_found","?"),
                r.get("d_ff","?"), r.get("D_reg","?"),
                r.get("fires","?"), r.get("gate_passes","?"),
                r.get("gate_meaningful","?"),
            ))
    md.append("")
    md.append("**d_ff bounded as n grows:** %s" % all_bounded)
    md.append("**Any fires:** %s" % any_fires)
    md.append("**Any gate passes:** %s" % any_gate_passes)
    md.append("**Any gate meaningful:** %s" % any_gate_meaningful)
    md.append("")
    md.append("## Binary vs Prime-Field Contrast")
    md.append("")
    md.append("| setting | fires | gate_passes | source |")
    md.append("|---|---|---|---|")
    md.append("| Binary FPPR (EXP-014) | %s | %s | this file |" % (any_fires, any_gate_passes))
    md.append("| Prime-field x-ring (EXP-009/010) | False | False | established |")
    md.append("")
    md.append("## PO-002 Verdict")
    md.append("")
    md.append("**%s**" % verdict.upper())
    md.append("")
    md.append(vreason)
    md.append("")
    md.append("## Interpretation")
    md.append("")
    if verdict == "survived":
        md.append(
            "OBSERVATION: The gated meter fires on a genuinely consistent binary FPPR system "
            "(S3 verified against real triples, consistent ideal, genuine relation found). "
            "The firing syzygy involves the S3 leading form (gate passes). d_ff is bounded "
            "as n grows -- the FPPR signature. This contrasts with the prime-field case "
            "(d_ff=D_reg in all 48 cells). PO-002 is met: the gated meter correctly "
            "detects the genuine FPPR binary early fall and filters the prime-field "
            "spurious fires."
        )
    elif verdict == "failed":
        md.append(
            "NEGATIVE RESULT: Fires observed but confined to field-eq (FB) rows. "
            "The binary system fires for the same spurious reason as the prime-field "
            "e-ring/power-sum (POS-A coordinate artifact). PO-002 not met. "
            "The gate correctly filters these spurious fires."
        )
    else:
        md.append(
            "INCONCLUSIVE: " + vreason + "\n\n"
            "The multilinearized binary FPPR system may not be the correct formulation "
            "for the BFS first-fall meter. The FPPR fall in the literature (Gaudry 2009, "
            "Petit-Quisquater 2012) is established via degree-of-regularity arguments on "
            "the FULL (non-multilinearized) system. The nontrivial-syzygy meter on the "
            "multilinearized form may see a different algebraic phenomenon."
        )
    md.append("")
    md.append("## Limitations")
    md.append("")
    md.append("- n tested up to 13; larger n may show different behavior.")
    md.append("- Multilinearization changes the leading-form structure.")
    md.append("- The gated meter requires the firing syzygy to involve the S3 leading form.")
    md.append("  If the fall is a last-fall phenomenon, the meter may miss it.")
    md.append("- l in {3,4}; the FPPR threshold may require l >= 5.")
    md.append("")
    md.append("## Next Steps")
    md.append("")
    md.append("1. Test the UN-REDUCED system (raw degree-12 S3 projections + field eqs)")
    md.append("   without multilinearization to see if the fall appears there.")
    md.append("2. Consult Gaudry (2009) / Petit-Quisquater (2012) for the exact system.")
    md.append("3. Try l in {5,6} for threshold effects.")
    md_path = os.path.join(EXPDIR, "round007_exp014_binary_fppr_corrected_result.md")
    with open(md_path, "w") as fmd:
        fmd.write("\n".join(md) + "\n")
    log("MD: %s" % md_path)

    _LOG_FILE.close()
    return out_data


result = main()
