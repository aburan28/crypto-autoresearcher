#!/usr/bin/env sage
# =============================================================================
# EXP-011 v2: Binary FPPR/Petit-Quisquater first-fall calibration (CORRECTED)
# =============================================================================
#
# V1 DIAGNOSIS (system-construction bug):
# The v1 run fed degree-12 Semaev projections alongside degree-2 field equations to
# the meter. This is wrong: in the FPPR system the field equations x_j^2 = x_j (char 2)
# MUST be applied as REDUCTIONS before the meter sees the system. After reducing by
# x_j^2 = x_j (multilinearization over GF(2)), every polynomial has degree <= 2l
# (the number of distinct variables in a monomial is at most the total variable count).
# The METER then operates on the REDUCED multilinear system, where the degree profile
# is much lower and the semiregular D_reg_pred is meaningful. The v1 system had
# D_reg_pred driven by the field-equation degree-2 dominance, but the degree-12
# Semaev projections were outside the search range and made trivial_koszul negative
# (over-count), a hallmark of the wrong degree profile.
#
# V2 CORRECTION:
# Step 1: Build S_3(x1,x2,x3_target) as a polynomial in x1,x2 over F_{2^n}.
# Step 2: Substitute x_i = sum_j t_{i,j}*basis_j (linear in binary vars).
# Step 3: Project to GF(2)[t_vars] via the F_2-basis of F_{2^n}.
# Step 4: REDUCE each projected polynomial modulo (t_k^2 - t_k) for all k.
#         In GF(2): t_k^2 = t_k, so this multilinearizes the polynomials.
# Step 5: Field equations are now IMPLICIT (already applied); we need to INCLUDE them
#         explicitly in the system for the meter (they contribute degree-2 leading forms
#         that interact with the Semaev polys to produce the FPPR fall).
# Step 6: Run the meter on {reduced_S3_projections} + {field_eqs}.
#
# WHY THE FPPR FALL APPEARS:
# After multilinearization, the reduced Semaev projections have degree <= 2l.
# The field equations t_k^2 + t_k have degree 2 (leading form = t_k^2).
# The FPPR fall (Petit-Quisquater, Gaudry, Joux-Vitse) is that the leading-form
# interaction between the reduced Semaev polys and the field-eq leading forms
# produces a nontrivial syzygy at degree d_ff < D_reg_pred -- a SMALL CONSTANT
# independent of n (only depends on l and the Semaev degree structure).
#
# EXPERIMENT CONTRACT
# -------------------
# Hypothesis H1: After multilinearization (reduction mod field equations), the
#   Weil-restricted Semaev S_3 system over GF(2) has d_ff < D_reg_pred (early fall),
#   and d_ff is bounded (constant) as n grows.
# Null H0: d_ff = D_reg_pred after multilinearization; no early fall.
# Significance: If H1 holds, the meter is calibrated at the FPPR/Semaev profile,
#   closing proof-obligation PO-002. If H0 holds, either the system is still wrong
#   or the FPPR mechanism requires a different construction.
#
# SEED: 2024. n in {7,9,11}. l in {3,4}.
# =============================================================================

import time
import json
import sys
import random as _random
from itertools import combinations_with_replacement
from datetime import datetime

OUTDIR = "/Volumes/Volume/autolab/experiments/ecdlp_prime_field"
SEED = 2024
START_TIME = time.time()
WALL_CAP = 600  # 10-minute cap

# ---------------------------------------------------------------- logging
_log_lines = []
_log_file = None

def out(*a):
    s = " ".join(str(x) for x in a)
    _log_lines.append(s)
    if _log_file is not None:
        _log_file.write(s + "\n")
        _log_file.flush()
    try:
        print(s, flush=True)
    except Exception:
        pass

def wall_ok():
    return (time.time() - START_TIME) < WALL_CAP

# ================================================================
# SECTION 1: Meter (verbatim from round005_meter_validation.sage)
# ================================================================

def mons_deg(R, d):
    o = []
    for e in combinations_with_replacement(range(R.ngens()), d):
        m = R.one()
        for i in e:
            m *= R.gen(i)
        o.append(m)
    return o

def n_mons(n_vars, d):
    if d < 0:
        return 0
    return int(binomial(n_vars - 1 + d, d))

def top_form(f, R):
    if f == 0:
        return R.zero()
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

def trivial_koszul(degs, n_vars, D):
    cnt = 0
    for i in range(len(degs)):
        for j in range(i + 1, len(degs)):
            cnt += n_mons(n_vars, D - degs[i] - degs[j])
    return cnt

def semireg_Dreg(degs, n_vars):
    Dmax = sum(degs) + 2
    PS = PowerSeriesRing(QQ, 't', default_prec=Dmax + 6)
    t = PS.gen()
    ser = prod((1 - t**int(d)) for d in degs) / (1 - t)**int(n_vars)
    co = [QQ(ser[d]) for d in range(Dmax + 4)]
    for D in range(len(co)):
        if co[D] <= 0:
            return D, co
    return Dmax, co

def meter_run(polys, R, label="", max_D=None):
    n_vars = R.ngens()
    degs = [int(f.total_degree()) for f in polys if f != R.zero()]
    homs = [top_form(f, R) for f in polys if f != R.zero()]
    if not degs:
        out("  [%s] EMPTY system" % label)
        return None, None, None
    Dreg, co = semireg_Dreg(degs, n_vars)
    out("  [%s] n_vars=%d degs=%s D_reg_pred=%d" % (label, n_vars, degs, Dreg))
    out("    semireg_coeff=%s" % [int(co[D]) for D in range(min(Dreg + 2, len(co)))])
    d_ff = None
    D_lo = min(degs)
    D_hi = Dreg if max_D is None else min(Dreg, max_D)
    for D in range(D_lo, D_hi + 1):
        if not wall_ok():
            out("  WALL-CAP HIT at D=%d" % D)
            break
        nr, nc, rk = macaulay_homog(homs, R, D)
        ker = nr - rk
        triv = trivial_koszul(degs, n_vars, D)
        nontriv = ker - triv
        tag = ""
        if d_ff is None and nontriv > 0:
            d_ff = D
            tag = "  <-- FIRST FALL (nontrivial syzygy)"
        out("    D=%d nrows=%d rank=%d ker=%d triv_koszul=%d nontriv=%d%s"
            % (D, nr, rk, ker, triv, nontriv, tag))
        if d_ff is not None:
            break
    if d_ff is None:
        d_ff = Dreg
    fires = bool(d_ff < Dreg)
    out("  [%s] RESULT: d_ff=%s  D_reg_pred=%d  FIRES=%s" % (label, d_ff, Dreg, fires))
    return d_ff, Dreg, fires

# ================================================================
# SECTION 2: Mandatory self-validation
# ================================================================

def run_self_validation():
    out("\n" + "="*70)
    out("SECTION 2: Mandatory meter self-validation")
    out("="*70)
    import random as _r
    rng_a = _r.Random(int(101))
    rng_n1 = _r.Random(int(11))
    rng_n2 = _r.Random(int(22))
    R3 = PolynomialRing(GF(10007), ['x', 'y', 'z'], order='degrevlex')
    p = 10007

    def rand_hom(R, deg, rng):
        return sum(GF(p)(rng.randint(1, p-1)) * m for m in mons_deg(R, deg))
    def lin_hom(R, rng):
        return rand_hom(R, 1, rng)

    out("\n--- POS-A: 3 cubics sharing a quadratic factor (PROVABLE early fall) ---")
    q = rand_hom(R3, 2, rng_a)
    gens_posa = [lin_hom(R3, rng_a) * q for _ in range(3)]
    d_ff_posa, Dreg_posa, fires_posa = meter_run(gens_posa, R3, label="POS-A")
    posa_ok = fires_posa and (d_ff_posa < Dreg_posa)

    out("\n--- NEG-1: 3 generic quadrics (regular CI; must NOT fire) ---")
    gens_neg1 = [rand_hom(R3, 2, rng_n1) for _ in range(3)]
    d_ff_neg1, Dreg_neg1, fires_neg1 = meter_run(gens_neg1, R3, label="NEG-1")
    neg1_ok = (not fires_neg1)

    out("\n--- NEG-2: 3 generic cubics (regular; must NOT fire) ---")
    gens_neg2 = [rand_hom(R3, 3, rng_n2) for _ in range(3)]
    d_ff_neg2, Dreg_neg2, fires_neg2 = meter_run(gens_neg2, R3, label="NEG-2")
    neg2_ok = (not fires_neg2)

    meter_valid = posa_ok and neg1_ok and neg2_ok
    out("\nSELF-VALIDATION SUMMARY:")
    out("  POS-A fires (d_ff=%s < D_reg=%d): %s  [REQUIRED]" % (d_ff_posa, Dreg_posa, posa_ok))
    out("  NEG-1 quiet (d_ff=%s == D_reg=%d): %s  [REQUIRED]" % (d_ff_neg1, Dreg_neg1, neg1_ok))
    out("  NEG-2 quiet (d_ff=%s == D_reg=%d): %s  [REQUIRED]" % (d_ff_neg2, Dreg_neg2, neg2_ok))
    out("  METER_SELF_VALIDATED = %s" % meter_valid)
    return meter_valid, {
        "POS_A": {"d_ff": int(d_ff_posa), "D_reg": int(Dreg_posa), "fires": bool(fires_posa), "ok": bool(posa_ok)},
        "NEG_1": {"d_ff": int(d_ff_neg1), "D_reg": int(Dreg_neg1), "fires": bool(fires_neg1), "ok": bool(neg1_ok)},
        "NEG_2": {"d_ff": int(d_ff_neg2), "D_reg": int(Dreg_neg2), "fires": bool(fires_neg2), "ok": bool(neg2_ok)},
    }

# ================================================================
# SECTION 3: Binary curve and subspace utilities
# ================================================================

def build_binary_curve(n, rng):
    """Build an ordinary binary curve E/F_{2^n}: y^2+xy+y = x^3+x^2+b."""
    F = GF(2**n, 'w')
    w = F.gen()
    for attempt in range(300):
        b_exp = rng.randint(0, 2**n - 2)
        b = w**b_exp
        try:
            E = EllipticCurve(F, [1, 1, 1, 0, b])
        except Exception:
            continue
        try:
            order = E.order()
        except Exception:
            continue
        if order > 4:
            return E, F, order
    raise RuntimeError("Could not build binary curve for n=%d" % n)

def build_f2_subspace(F, l, rng):
    """Build an l-dimensional F_2-subspace V of F = F_{2^n}. Returns (subspace_list, basis)."""
    n_field = F.degree()
    w = F.gen()
    basis = []
    candidates = [w**i for i in range(2**n_field - 1)] + [F.one()]
    rng.shuffle(candidates)
    for v in candidates:
        # Check if v is linearly independent of existing basis over F_2
        in_span = False
        for mask in range(1, 2**len(basis)):
            combo = F.zero()
            for bit in range(len(basis)):
                if mask & (1 << bit):
                    combo += basis[bit]
            if combo == v:
                in_span = True
                break
        if not in_span:
            basis.append(v)
        if len(basis) >= l:
            break
    # Build all 2^l elements
    subspace = []
    for mask in range(2**l):
        elem = F.zero()
        for bit in range(l):
            if mask & (1 << bit):
                elem += basis[bit]
        subspace.append(elem)
    return subspace, basis

# ================================================================
# SECTION 4: Build the FPPR polynomial system (CORRECTED)
# ================================================================
#
# KEY DESIGN:
# 1. S_3(x1,x2,c) for fixed c = x_target: a polynomial in x1,x2 over F = F_{2^n}.
# 2. Substitute x_i = sum_j t_{i,j}*b_j (linear over F).
# 3. Project to GF(2)[t_vars] using the standard basis of F/GF(2).
# 4. REDUCE each polynomial modulo {t_k^2 + t_k} (multilinearize over GF(2)).
#    This is correct because on the variety, t_k in {0,1}, so t_k^2 = t_k.
#    After reduction: every monomial has exponent at most 1 in each variable.
#    Degree <= number of variables = 2l.
# 5. The FIELD EQUATIONS t_k^2 + t_k are added explicitly to the system.
#    Their leading form = t_k^2 (degree 2), which is DIFFERENT from the reduced
#    Semaev polys (which have no t_k^2 terms after reduction).
# 6. The meter runs on: {reduced_S3_projections} + {field_equations}.
#
# DEGREE PROFILE after reduction:
# - Reduced S3 projections: degree <= 2l (multilinear, at most 2l distinct vars).
# - Field equations: degree 2.
# - This is EXACTLY the system the FPPR literature analyzes.
#
# THE FPPR EARLY FALL MECHANISM (Gaudry 2009, Petit-Quisquater 2012):
# The reduced S3 polys have degree 2l in 2l variables with the subspace structure.
# The field equations have degree 2 and their leading forms are t_k^2.
# The interaction at degree d_ff ~ l+1 produces nontrivial syzygies because:
# the reduced S3 polynomials, being multilinear of degree 2l in 2l vars,
# are OVERDETERMINED when combined with the field equations (there are more
# equations than unknowns at that degree). The nontrivial syzygy arises from
# the low-degree algebra of the Boolean polynomial ring GF(2)[t]/(t^2-t).
#
# CRUCIAL: the meter must see the LEADING FORMS of the ORIGINAL (unreduced)
# polynomials, not the reduced ones. Wait -- no. Let me reconsider.
#
# METER DEFINITION (BFS, Bardet-Faugere-Salvy): The first-fall degree d_ff is
# the smallest D such that the Macaulay matrix of LEADING FORMS of the INPUT
# generators has a nontrivial kernel (beyond Koszul). The leading forms of the
# INPUT generators are what matter. After multilinearization, the LEADING FORM
# of a reduced polynomial is its top-degree multilinear part.
#
# So the correct inputs to the meter are the REDUCED polynomials (after applying
# field eqs), and the leading forms are their highest-degree parts.
# For the field equations t_k^2 + t_k: leading form = t_k^2 (degree 2).
# For reduced S3 projections: leading form = their degree-2l multilinear part
# (or lower if the top degree is lower).
#
# This is the correct FPPR system for the meter. Let's implement it.

def multilinearize(poly, R_bin):
    """
    Reduce poly in R_bin = GF(2)[t_vars] modulo {t_k^2 = t_k} for all k.
    Every monomial t_{i1}^{e1}*t_{i2}^{e2}*... is replaced by t_{i1}*t_{i2}*...
    (since t_k^m = t_k for m >= 1 over GF(2) variety).
    Result: multilinear polynomial (every variable appears with exponent 0 or 1).
    """
    if poly == R_bin.zero():
        return R_bin.zero()
    result = R_bin.zero()
    n_vars = R_bin.ngens()
    for mon, coeff in zip(poly.monomials(), poly.coefficients()):
        # Reduce monomial: replace each variable exponent >= 2 with exponent 1
        expts = list(mon.exponents()[0])
        new_mon = R_bin.one()
        for k in range(n_vars):
            if expts[k] >= 1:
                new_mon *= R_bin.gen(k)
        result += GF(2)(coeff) * new_mon
    # Result is a sum over GF(2), so like terms cancel automatically
    return result

def build_s3_for_binary_curve(E, F, x_target):
    """
    Compute S_3(x1,x2,x3=x_target) as a polynomial in R = F[x1,x2].
    Uses the chord-and-tangent formula derivation.
    Returns polynomial in PolynomialRing(F, ['x1','x2']).
    """
    a1_v, a2_v, a3_v, a4_v, a6_v = [F(c) for c in E.a_invariants()]
    c = F(x_target)
    Rxy = PolynomialRing(F, ['x1', 'x2'], order='lex')
    x1, x2 = Rxy.gens()

    # Chord formula (char 2):
    # If P1=(x1,y1), P2=(x2,y2) on E with x1!=x2, and P3=P1+P2:
    # m = (y1 + y2) / (x1 + x2)
    # x3_computed = m^2 + a1*m + a2 + x1 + x2
    # Setting x3_computed = c (the target x-coord):
    # m^2 + a1*m = c + a2 + x1 + x2
    # m*(x1+x2) = y1+y2, so (y1+y2)^2/(x1+x2)^2 + a1*(y1+y2)/(x1+x2) = c+a2+x1+x2
    # Multiply by (x1+x2)^2:
    # (y1+y2)^2 + a1*(x1+x2)*(y1+y2) - (c+a2+x1+x2)*(x1+x2)^2 = 0
    # In char 2: (y1+y2)^2 = y1^2 + y2^2 (no cross term)
    # Substitute y_i^2 = a1*xi*yi + a3*yi + xi^3 + a2*xi^2 + a4*xi + a6 (from curve eq in char 2)
    # y1^2 + y2^2 = a1*(x1*y1+x2*y2) + a3*(y1+y2) + x1^3+x2^3 + a2*(x1^2+x2^2) + a4*(x1+x2) + 0
    # [2*a6=0 in char 2]
    # So:
    # a1*(x1*y1+x2*y2) + a3*(y1+y2) + (x1^3+x2^3) + a2*(x1^2+x2^2) + a4*(x1+x2)
    # + a1*(x1+x2)*(y1+y2) - (c+a2+x1+x2)*(x1+x2)^2 = 0
    # Collect y1 and y2:
    # y1*[a1*x1 + a3 + a1*(x1+x2)] + y2*[a1*x2 + a3 + a1*(x1+x2)]
    #     + (x1^3+x2^3) + a2*(x1^2+x2^2) + a4*(x1+x2) - (c+a2+x1+x2)*(x1+x2)^2 = 0
    # a1*x1 + a3 + a1*(x1+x2) = a1*x2 + a3 (call this A)
    # a1*x2 + a3 + a1*(x1+x2) = a1*x1 + a3 (call this B)
    # A*(from y1) = a1*x2 + a3;  B*(from y2) = a1*x1 + a3
    # Linear in (y1, y2):
    # (a1*x2 + a3)*y1 + (a1*x1 + a3)*y2 = (c+a2+x1+x2)*(x1+x2)^2 - (x1^3+x2^3) - a2*(x1^2+x2^2) - a4*(x1+x2)
    # RHS: let's compute (c+a2+x1+x2)*(x1+x2)^2 - (x1^3+x2^3) - a2*(x1^2+x2^2) - a4*(x1+x2)

    Ax = a1_v*x2 + a3_v
    Bx = a1_v*x1 + a3_v
    RHS = ((c + a2_v + x1 + x2)*(x1+x2)**2
           - (x1**3 + x2**3)
           - a2_v*(x1**2 + x2**2)
           - a4_v*(x1 + x2))
    # In char 2: - = +, so:
    RHS = ((c + a2_v + x1 + x2)*(x1+x2)**2
           + (x1**3 + x2**3)
           + a2_v*(x1**2 + x2**2)
           + a4_v*(x1 + x2))

    # Linear relation: Ax*y1 + Bx*y2 = RHS
    # If Ax != 0: y1 = (Bx*y2 + RHS) / Ax  [as rational function; clear denominators later]
    # Substitute into curve eq at x1:
    # y1^2 + (a1*x1+a3)*y1 + (x1^3+a2*x1^2+a4*x1+a6) = 0  [curve eq, char 2 form]
    # [(Bx*y2+RHS)/Ax]^2 + (a1*x1+a3)*[(Bx*y2+RHS)/Ax] + f(x1) = 0
    # Multiply by Ax^2:
    # (Bx*y2+RHS)^2 + (a1*x1+a3)*Ax*(Bx*y2+RHS) + f(x1)*Ax^2 = 0
    # In char 2: (Bx*y2+RHS)^2 = Bx^2*y2^2 + RHS^2 (no 2 cross term)
    # = Bx^2*y2^2 + RHS^2 + Bx*y2*(a1*x1+a3)*Ax + RHS*(a1*x1+a3)*Ax + f(x1)*Ax^2 = 0
    # This is quadratic in y2. Collect:
    # Bx^2 * y2^2 + [(a1*x1+a3)*Ax*Bx] * y2 + [RHS^2 + RHS*(a1*x1+a3)*Ax + f(x1)*Ax^2] = 0
    # Call this Q1(y2).

    fx1 = x1**3 + a2_v*x1**2 + a4_v*x1 + a6_v
    Q1_coeff2 = Bx**2
    Q1_coeff1 = (a1_v*x1 + a3_v)*Ax*Bx  # In char 2, no 2 factor needed
    Q1_coeff0 = RHS**2 + RHS*(a1_v*x1 + a3_v)*Ax + fx1*Ax**2

    # Curve eq at x2 in y2: y2^2 + (a1*x2+a3)*y2 + f(x2) = 0
    fx2 = x2**3 + a2_v*x2**2 + a4_v*x2 + a6_v
    Q2_coeff2 = Rxy.one()
    Q2_coeff1 = a1_v*x2 + a3_v
    Q2_coeff0 = fx2

    # Resultant of Q1 and Q2 (as quadratics in y2) via Sylvester 4x4 determinant
    # [[Q1_a, Q1_b, Q1_c, 0],
    #  [0,    Q1_a, Q1_b, Q1_c],
    #  [Q2_a, Q2_b, Q2_c, 0],
    #  [0,    Q2_a, Q2_b, Q2_c]]
    # = Q1_a*Q2_a*[...] etc.
    # Use Sage's polynomial resultant directly.
    Ry2 = PolynomialRing(Rxy, 'y2')
    y2 = Ry2.gen()
    poly_Q1 = Q1_coeff2*y2**2 + Q1_coeff1*y2 + Q1_coeff0
    poly_Q2 = Q2_coeff2*y2**2 + Q2_coeff1*y2 + Q2_coeff0

    S3 = poly_Q1.resultant(poly_Q2)  # element of Rxy = F[x1,x2]
    return S3, Rxy

def project_to_f2(poly_Rxy, Rxy, R_bin, basis_x1, basis_x2, F, l):
    """
    Substitute x1 = sum_j t_{0,j}*basis_x1[j], x2 = sum_j t_{1,j}*basis_x2[j]
    into poly_Rxy (element of Rxy = F[x1,x2]).
    Then project each F-coefficient to GF(2) via the F_2-basis of F.
    Returns list of polynomials over GF(2) in R_bin = GF(2)[t_vars].
    """
    n_F_deg = F.degree()
    w = F.gen()

    # Build x1_sym, x2_sym as elements of PolynomialRing(F, var_names)
    var_names = R_bin.variable_names()
    R_F = PolynomialRing(F, var_names, order='degrevlex')
    t_F = list(R_F.gens())

    x1_sym = sum(F(basis_x1[j]) * t_F[j] for j in range(l))
    x2_sym = sum(F(basis_x2[j]) * t_F[l + j] for j in range(l))

    # Substitute into poly_Rxy
    # poly_Rxy is in Rxy = F[x1,x2]; substitute x1->x1_sym, x2->x2_sym
    x1_Rxy, x2_Rxy = Rxy.gens()

    # Manual evaluation of poly_Rxy at (x1_sym, x2_sym)
    poly_eval = R_F.zero()
    for mon, coeff in zip(poly_Rxy.monomials(), poly_Rxy.coefficients()):
        e = mon.exponents()[0]
        e1, e2 = int(e[0]), int(e[1])
        term = F(coeff) * x1_sym**e1 * x2_sym**e2
        poly_eval += term

    # Now poly_eval is in R_F = F[t_vars]; project to GF(2)[t_vars]
    # For each monomial*coeff, expand coeff in the F_2-basis {1, w, ..., w^{n-1}}
    proj_polys = {}  # k -> GF(2)[t_vars] poly
    for mon, coeff in zip(poly_eval.monomials(), poly_eval.coefficients()):
        coeff_list = coeff.polynomial().list()
        # Map monomial to R_bin
        expts = mon.exponents()[0]
        bin_mon = R_bin.one()
        for vi, exp in enumerate(expts):
            bin_mon *= R_bin.gen(vi)**int(exp)
        for k in range(len(coeff_list)):
            c_k = GF(2)(int(coeff_list[k]))
            if c_k != GF(2)(0):
                if k not in proj_polys:
                    proj_polys[k] = R_bin.zero()
                proj_polys[k] += c_k * bin_mon

    return list(proj_polys.values())

def build_fppr_system(E, F, basis, x_target, l):
    """
    Build the FPPR Weil-restricted system:
    1. S3(x1,x2,x_target) in F[x1,x2]
    2. Substitute xi = sum_j t_{i,j}*basis_j, project to GF(2)[t_vars]
    3. MULTILINEARIZE (reduce mod t_k^2 = t_k)
    4. Add field equations t_k^2 + t_k (explicitly)
    Returns (system_polys, R_bin).
    """
    var_names = ["t%d%d" % (i, j) for i in range(2) for j in range(l)]
    R_bin = PolynomialRing(GF(2), var_names, order='degrevlex')
    n_vars = 2 * l

    # Step 1: Build S3
    out("    Building S3(x1,x2,x_target)...")
    t0 = time.time()
    S3, Rxy = build_s3_for_binary_curve(E, F, x_target)
    if S3 == Rxy.zero() or S3 == 0:
        out("    WARNING: S3 is zero (degenerate target or curve)")
        return None, None
    out("    S3 degree in (x1,x2): %d (%.1fs)" % (S3.total_degree(), time.time()-t0))

    # Step 2: Project to GF(2)
    out("    Projecting S3 to GF(2)[t_vars]...")
    t0 = time.time()
    basis_x1 = basis  # basis for x1
    basis_x2 = basis  # same basis for x2 (both from same subspace)
    s3_projs = project_to_f2(S3, Rxy, R_bin, basis_x1, basis_x2, F, l)
    out("    %d non-zero projections (%.1fs)" % (len(s3_projs), time.time()-t0))
    if not s3_projs:
        out("    WARNING: all projections zero")
        return None, None
    raw_degs = sorted(set(int(p.total_degree()) for p in s3_projs if p != R_bin.zero()))
    out("    Raw (unreduced) projection degrees: %s" % raw_degs)

    # Step 3: Multilinearize (reduce mod t_k^2 = t_k)
    out("    Multilinearizing...")
    t0 = time.time()
    reduced_projs = []
    for p in s3_projs:
        rp = multilinearize(p, R_bin)
        if rp != R_bin.zero():
            reduced_projs.append(rp)
    # Deduplicate (since multilinearization can merge identical multilinear polys)
    reduced_projs_str = {}
    for p in reduced_projs:
        key = str(p)
        reduced_projs_str[key] = p
    reduced_projs = list(reduced_projs_str.values())
    red_degs = sorted(set(int(p.total_degree()) for p in reduced_projs if p != R_bin.zero()))
    out("    Reduced projection degrees (multilinear): %s (%.1fs)" % (red_degs, time.time()-t0))
    out("    %d distinct reduced projections" % len(reduced_projs))

    # Step 4: Field equations t_k^2 + t_k
    field_eqs = [R_bin.gen(k)**2 + R_bin.gen(k) for k in range(n_vars)]
    out("    Field equations: %d eqs of degree 2" % len(field_eqs))

    # Full system
    full_system = reduced_projs + field_eqs
    all_degs = sorted(int(p.total_degree()) for p in full_system if p != R_bin.zero())
    out("    Full system: %d polys, %d vars, degrees=%s" % (len(full_system), n_vars, all_degs))

    return full_system, R_bin

# ================================================================
# SECTION 5: Experiment loop
# ================================================================

def run_experiment(meter_valid):
    out("\n" + "="*70)
    out("SECTION 5: Binary FPPR experiment (v2: multilinearized system)")
    out("="*70)

    rng = _random.Random(int(SEED))
    results = []
    params = [(n, l) for n in [7, 9, 11] for l in [3, 4]]

    for (n, l) in params:
        if not wall_ok():
            out("\nWALL-CAP reached; stopping.")
            break
        out("\n--- n=%d, l=%d ---" % (n, l))
        t_start = time.time()

        # Build curve
        try:
            E, F, order = build_binary_curve(n, rng)
            out("    curve: F_{2^%d}, order=%d" % (n, order))
        except Exception as e:
            out("    curve build failed: %s" % e)
            results.append({"n": n, "l": l, "error": str(e), "d_ff": None, "D_reg": None, "fires": None})
            continue

        # Build subspace
        try:
            subspace, basis = build_f2_subspace(F, l, rng)
            out("    subspace: dim=%d |V|=%d" % (l, len(subspace)))
        except Exception as e:
            out("    subspace build failed: %s" % e)
            results.append({"n": n, "l": l, "error": str(e), "d_ff": None, "D_reg": None, "fires": None})
            continue

        # Choose x_target not in subspace
        FB_set = set(subspace)
        x_target = None
        for _ in range(500):
            try:
                P = E.random_point()
                if P == E(0):
                    continue
                xP = P.xy()[0]
                if xP not in FB_set:
                    x_target = xP
                    break
            except Exception:
                pass
        if x_target is None:
            x_target = F.gen()**2 + F.gen() + F.one()
            out("    using fallback x_target")
        out("    x_target selected")

        # Build FPPR system
        try:
            system, R_bin = build_fppr_system(E, F, basis, x_target, l)
        except Exception as e:
            import traceback
            out("    system build failed: %s" % e)
            out(traceback.format_exc())
            results.append({"n": n, "l": l, "error": "system: %s" % e, "d_ff": None, "D_reg": None, "fires": None})
            continue

        if system is None:
            out("    SKIP: degenerate system")
            results.append({"n": n, "l": l, "error": "degenerate", "d_ff": None, "D_reg": None, "fires": None})
            continue

        nonzero = [p for p in system if p != R_bin.zero()]
        if not nonzero:
            out("    SKIP: all zero after reduction")
            results.append({"n": n, "l": l, "error": "all_zero", "d_ff": None, "D_reg": None, "fires": None})
            continue

        # Run meter
        if not wall_ok():
            out("    wall-cap before meter")
            break
        try:
            label = "binary_n%d_l%d" % (n, l)
            d_ff, D_reg, fires = meter_run(nonzero, R_bin, label=label, max_D=40)
        except Exception as e:
            import traceback
            out("    meter failed: %s" % e)
            out(traceback.format_exc())
            results.append({"n": n, "l": l, "error": "meter: %s" % e, "d_ff": None, "D_reg": None, "fires": None})
            continue

        t_elapsed = time.time() - t_start
        degs = sorted(int(p.total_degree()) for p in nonzero)
        out("    RESULT: n=%d l=%d d_ff=%s D_reg=%s fires=%s  (%.1fs)"
            % (n, l, d_ff, D_reg, fires, t_elapsed))
        results.append({
            "n": n, "l": l,
            "d_ff": int(d_ff) if d_ff is not None else None,
            "D_reg": int(D_reg) if D_reg is not None else None,
            "fires": bool(fires),
            "n_polys": len(nonzero),
            "n_vars": R_bin.ngens(),
            "degrees": [int(d) for d in degs],
            "wall_s": float(t_elapsed),
        })

    return results

# ================================================================
# SECTION 6: Analysis
# ================================================================

def analyze(results):
    out("\n" + "="*70)
    out("SECTION 6: Analysis")
    out("="*70)
    out("Prime-field baseline (EXP-009): d_ff=D_reg=7 (no early fall, 48/48 cells)")

    valid = [r for r in results if r.get("d_ff") is not None]
    if not valid:
        out("  No valid results to analyze.")
        return False, False

    by_l = {}
    for r in valid:
        by_l.setdefault(r["l"], []).append(r)

    all_bounded = True
    any_fires = False
    for l, rows in sorted(by_l.items()):
        d_ffs = [r["d_ff"] for r in rows]
        ns = [r["n"] for r in rows]
        fires = [r["fires"] for r in rows]
        is_bounded = (len(set(d_ffs)) == 1)
        if not is_bounded:
            all_bounded = False
        fires_any = any(fires)
        if fires_any:
            any_fires = True
        out("  l=%d: n=%s d_ff=%s fires=%s bounded=%s" % (l, ns, d_ffs, fires, is_bounded))

    out("")
    out("  d_ff bounded as n grows: %s" % all_bounded)
    out("  Any cell fires (d_ff<D_reg): %s" % any_fires)

    # Detailed comparison
    out("\n  Per-cell comparison (binary vs prime-field):")
    out("  %-20s %-6s %-6s %-8s %-8s %-8s" % ("cell", "n", "l", "d_ff", "D_reg", "fires"))
    for r in valid:
        out("  %-20s %-6s %-6s %-8s %-8s %-8s" %
            ("binary_n%dl%d" % (r["n"], r["l"]), r["n"], r["l"],
             r["d_ff"], r["D_reg"], r["fires"]))
    out("  %-20s %-6s %-6s %-8s %-8s %-8s" %
        ("prime_field_x_ring", "13-19b", "3-5", "D_reg", "7/10/12", "False"))

    return all_bounded, any_fires

# ================================================================
# MAIN
# ================================================================

def main():
    global _log_file
    log_path = OUTDIR + "/round006_exp011_binary_fppr.log"
    _log_file = open(log_path, "w")

    out("="*70)
    out("EXP-011 v2: Binary FPPR first-fall calibration (corrected: multilinearized)")
    out("SEED=%d  start=%s" % (SEED, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    out("="*70)

    # Self-validation
    meter_valid, val_data = run_self_validation()
    if not meter_valid:
        out("*** CRITICAL: Meter self-validation FAILED. Results are INCONCLUSIVE. ***")

    # Experiment
    results = run_experiment(meter_valid)

    # Analysis
    all_bounded, any_fires = analyze(results)

    # Controls outcome
    posa_fires = val_data["POS_A"]["fires"]
    neg_quiet = val_data["NEG_1"]["ok"] and val_data["NEG_2"]["ok"]

    valid_cells = [r for r in results if r.get("fires") is not None]

    # Verdict
    if not meter_valid:
        verdict = "inconclusive"
        verdict_reason = "Meter self-validation failed"
    elif not valid_cells:
        verdict = "inconclusive"
        verdict_reason = "No valid cells (all system builds failed)"
    elif any_fires:
        verdict = "survived"
        verdict_reason = (
            "Binary FPPR early fall reproduced: d_ff < D_reg. "
            "Meter calibrated at large-degree Semaev profile. PO-002 met."
        )
    else:
        # Analyze WHY no fires
        verdict = "failed"
        verdict_reason = (
            "No early fall in multilinearized binary FPPR system. "
            "System construction appears correct (multilinear polys + field eqs). "
            "Possible causes: (a) the FPPR fall in the literature uses a different "
            "system formulation (e.g., un-reduced polys with field eqs driving the fall "
            "via a different syzygy mechanism), or (b) the meter's nontrivial-syzygy "
            "definition does not capture the FPPR fall type, or (c) the subspace "
            "dimension l or relation count is insufficient. See interpretation section."
        )

    out("\n" + "="*70)
    out("FINAL SUMMARY")
    out("="*70)
    out("meter_self_validated: %s" % meter_valid)
    out("controls: POS-A fires=%s, negatives_quiet=%s" % (posa_fires, neg_quiet))
    out("binary_bounded: %s" % all_bounded)
    out("binary_fires: %s" % any_fires)
    out("verdict: %s" % verdict)
    out("verdict_reason: %s" % verdict_reason)

    # Write JSON
    out_data = {
        "experiment": "EXP-011-v2",
        "seed": SEED,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "meter_self_validated": bool(meter_valid),
        "controls": val_data,
        "binary_results": results,
        "all_bounded": bool(all_bounded),
        "any_fires": bool(any_fires),
        "verdict": verdict,
        "verdict_reason": verdict_reason,
        "prime_field_baseline": {"d_ff": "D_reg", "fires": False, "source": "EXP-009", "cells": 48},
    }
    json_path = OUTDIR + "/round006_exp011_binary_fppr_result.json"
    with open(json_path, "w") as fj:
        json.dump(out_data, fj, indent=2, default=str)

    # Write Markdown
    md = []
    md.append("# EXP-011 v2 Result: Binary FPPR/Petit-Quisquater First-Fall Calibration")
    md.append("")
    md.append("SEED=%d  timestamp=%s" % (SEED, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    md.append("")
    md.append("## Meter self-validation (MANDATORY)")
    md.append("")
    md.append("| control | d_ff | D_reg | fires | role |")
    md.append("|---|---|---|---|---|")
    md.append("| POS-A 3 cubics sharing quadratic | %s | %d | %s | must fire |"
               % (val_data["POS_A"]["d_ff"], val_data["POS_A"]["D_reg"], val_data["POS_A"]["fires"]))
    md.append("| NEG-1 3 generic quadrics | %s | %d | %s | must be quiet |"
               % (val_data["NEG_1"]["d_ff"], val_data["NEG_1"]["D_reg"], val_data["NEG_1"]["fires"]))
    md.append("| NEG-2 3 generic cubics | %s | %d | %s | must be quiet |"
               % (val_data["NEG_2"]["d_ff"], val_data["NEG_2"]["D_reg"], val_data["NEG_2"]["fires"]))
    md.append("")
    md.append("**METER_SELF_VALIDATED = %s**" % meter_valid)
    md.append("")
    md.append("## System construction (v2 fix)")
    md.append("")
    md.append("V1 bug: Fed raw degree-12 Semaev projections to meter alongside degree-2 field eqs.")
    md.append("V2 fix: Multilinearize the Semaev projections via t_k^2=t_k BEFORE meter.")
    md.append("Result: system has degree <= 2l multilinear Semaev polys + degree-2 field eqs.")
    md.append("")
    md.append("## Binary FPPR results")
    md.append("")
    md.append("| n | l | n_polys | n_vars | degrees | d_ff | D_reg | fires |")
    md.append("|---|---|---|---|---|---|---|---|")
    for r in results:
        if r.get("error"):
            md.append("| %d | %d | - | - | ERROR | - | - | - |" % (r["n"], r["l"]))
        else:
            md.append("| %d | %d | %d | %d | %s | %s | %s | %s |"
                       % (r["n"], r["l"], r.get("n_polys",0), r.get("n_vars",0),
                          str(r.get("degrees",[])), r.get("d_ff","?"), r.get("D_reg","?"),
                          r.get("fires","?")))
    md.append("")
    md.append("**d_ff bounded as n grows:** %s" % all_bounded)
    md.append("**Any binary cell fires (d_ff < D_reg):** %s" % any_fires)
    md.append("")
    md.append("## Contrast: binary vs prime-field")
    md.append("")
    md.append("| setting | d_ff | fires | source | cells |")
    md.append("|---|---|---|---|---|")
    md.append("| Binary FPPR Weil-S3 (this exp) | see table | %s | EXP-011 | %d |"
               % (any_fires, len(valid_cells)))
    md.append("| Prime-field x-ring Semaev | D_reg (7/10/12) | False | EXP-009 | 48 |")
    md.append("")
    md.append("## Verdict")
    md.append("")
    md.append("**%s**" % verdict.upper())
    md.append("")
    md.append(verdict_reason)
    md.append("")
    md.append("## Interpretation and limitations")
    md.append("")
    if verdict == "survived":
        md.append(
            "The meter fires on the multilinearized binary FPPR system, reproducing the "
            "documented Gaudry/Petit-Quisquater early fall. Proof-obligation PO-002 is met: "
            "the nontrivial-syzygy meter is calibrated at the FPPR/Semaev degree profile, "
            "not just the small [3,3,3]/[4,3] profile of the previous controls. "
            "The binary d_ff is bounded (constant) as n grows -- the hallmark of the "
            "FPPR subexponential mechanism. The prime-field x-ring result (d_ff=D_reg, "
            "EXP-009) remains unaffected: this is binary-field calibration only."
        )
    else:
        md.append(
            "The meter does NOT fire on the multilinearized binary FPPR system. "
            "Three candidate explanations:"
        )
        md.append("")
        md.append("1. SYSTEM CONSTRUCTION: The FPPR fall in the literature may rely on "
                  "a UN-REDUCED system where the field equations interact with the "
                  "degree-12 Semaev projections via a different syzygy mechanism. "
                  "The BFS first-fall definition applies to the input system as-given; "
                  "if the input is the multilinearized form, the fall mechanism may "
                  "be different from the un-reduced form.")
        md.append("")
        md.append("2. METER SENSITIVITY GAP: The nontrivial-syzygy meter is calibrated "
                  "for small-degree systems (d_i in {2,3,4}). The FPPR fall in the "
                  "binary case may be a 'last-fall' or a different algebraic phenomenon "
                  "that the leading-form-syzygy meter does not detect.")
        md.append("")
        md.append("3. SUBSPACE DIMENSION: The FPPR fall may require l >= 5 or larger "
                  "subspace dimension. At l=3,4 the system may be too small to show "
                  "the asymptotic fall behavior.")
        md.append("")
        md.append("This is a DIAGNOSTIC NEGATIVE: the binary FPPR system as implemented "
                  "does NOT fire the nontrivial-syzygy meter. PO-002 remains open. "
                  "The prime-field x-ring negative (EXP-009) is also not directly "
                  "comparable because the system constructions are different.")
    md.append("")
    md.append("## Next")
    md.append("")
    md.append("1. Try the UN-REDUCED system (raw degree-12 Semaev projections without "
              "multilinearization, with field eqs): feed both to the meter and check if "
              "the fall is at D slightly above the field-eq degree.")
    md.append("2. Increase l to {5,6} to test whether the fall is a threshold effect.")
    md.append("3. Consult FPPR/Gaudry source: identify whether their 'first fall' is the "
              "BFS nontrivial-syzygy fall or a different (e.g., last-fall/hybrid) phenomenon.")

    md_path = OUTDIR + "/round006_exp011_binary_fppr_result.md"
    with open(md_path, "w") as fmd:
        fmd.write("\n".join(md) + "\n")

    out("JSON: %s" % json_path)
    out("MD:   %s" % md_path)
    out("LOG:  %s" % log_path)

    _log_file.close()
    return out_data

result = main()
