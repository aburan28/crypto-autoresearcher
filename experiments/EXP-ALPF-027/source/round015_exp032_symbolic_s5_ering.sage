# round015_exp032_symbolic_s5_ering.sage
# EXP-032: Symbolic S5 (m=4) Semaev in elementary-symmetric e-ring coords at TRUE degree.
# Integrity upgrade of NR-027 (round 11), which used a REDUCED-SURROGATE Semaev degree
# (not the true per-variable degree 2^(m-1)=8) and found all crossbred-admissible
# D<D_reg cuts to be gate_meaningful=False (e-ring FB-row artifact).
#
# This script:
#   (0) loads + INLINE self-validates the gated meter against 4 fixtures
#       (POS-A, NEG-1, e-ring m=3 base-fires-but-fails-gate, POS-C Weil S_3 passes gate).
#       If ANY fixture is wrong -> verdict INCONCLUSIVE and STOP.
#   (1) builds the genuine m=4 Semaev S5 with TRUE per-variable degree 8, and VERIFIES it
#       vanishes on real point 5-tuples whose sum is O (genuineness control).
#   (2) rewrites S5 in elementary-symmetric e-ring coords at the SMALLEST cell (bits=13, |FB|=3),
#       takes the homogeneous leading form.
#   (3) runs meter_gated (sumpoly_indices = S5 rows) + crossbred admissibility check.
#   (4) confirms whether any admissible D<D_reg cut is gate_meaningful=False at TRUE degree
#       (= NR-027 holds at true degree) or whether a masked gate_meaningful fall appears
#       (= CANDIDATE, flag loudly).
#
# Brutal honesty: gate_meaningful is a CANDIDATE not a survivor. A base 'fire' that is not
# gate_meaningful is NOT a positive. Count structural facts (degrees, ranks), not wall-clock wins.
#
# Wall-clock guarded. Writes all outputs the moment a result exists, then returns.

import time, json, sys, os
from sage.all import *

EXP_DIR = "/Volumes/Volume/autolab/experiments/ecdlp_prime_field"
BASENAME = "round015_exp032_symbolic_s5_ering"
LOG_PATH = os.path.join(EXP_DIR, BASENAME + ".log")
JSON_PATH = os.path.join(EXP_DIR, BASENAME + "_result.json")
MD_PATH = os.path.join(EXP_DIR, BASENAME + "_result.md")
METER_PATH = os.path.join(EXP_DIR, "round007_exp012_localization_gate.sage")

T0 = time.time()
BUDGET_SEC = 360.0  # ~6 min hard wall-clock guard for the whole script

_logf = open(LOG_PATH, "w")
def LOG(*a):
    msg = " ".join(str(x) for x in a)
    _logf.write(msg + "\n")
    _logf.flush()
    print(msg)

def elapsed():
    return time.time() - T0

def budget_left():
    return BUDGET_SEC - elapsed()

LOG("=== EXP-032 symbolic S5 e-ring true-degree ===")
LOG("start:", time.strftime("%Y-%m-%d %H:%M:%S"))
LOG("git/file: " + BASENAME)

# Result accumulator (written defensively at the end no matter what).
RES = {
    "experiment": "EXP-032 symbolic S5 e-ring true degree",
    "meter_self_validated": False,
    "fixtures": {},
    "s5_genuine": None,
    "s5_true_per_var_degree": None,
    "s5_total_degree": None,
    "ering_leading_form": None,
    "meter_at_true_degree": None,
    "crossbred_admissible_cuts": None,
    "any_gate_meaningful_fall": None,
    "nr027_holds_at_true_degree": None,
    "verdict": "inconclusive",
    "elapsed_sec": None,
    "notes": [],
}

# -----------------------------------------------------------------------------
# (0) Load + self-validate the gated meter.
# -----------------------------------------------------------------------------
LOG("\n--- (0) loading gated meter ---")
meter_ok = True
try:
    load(METER_PATH)  # provides meter_gated(...) and helpers
    LOG("loaded meter from", METER_PATH)
except Exception as e:
    LOG("FATAL: could not load meter:", repr(e))
    meter_ok = False

# Some meter files define _monomials_of_degree; ensure a fallback exists.
if "_monomials_of_degree" not in globals():
    def _monomials_of_degree(Rg, d):
        if d == 0:
            return [Rg.one()]
        from itertools import combinations_with_replacement
        gens = Rg.gens()
        out = []
        for combo in combinations_with_replacement(range(len(gens)), d):
            m = Rg.one()
            for i in combo:
                m *= gens[i]
            out.append(m)
        return out

# ----- Build the 4 mandatory fixtures -----
# POS-A: should FIRE with d_ff = 4 < 7 and be gate_meaningful.
#        A small over-determined system whose summation-poly rows create a genuine
#        low-degree syzygy. We use the canonical fixture shape from the meter's design:
#        a homogeneous quadric "summation" relation plus FB membership rows that combine
#        to a degree-4 fall.
def build_POS_A():
    F = GF(101)
    R = PolynomialRing(F, ["x0", "x1", "x2"], order="degrevlex")
    x0, x1, x2 = R.gens()
    # summation-style quadric (this is the "Semaev surrogate" leading-form carrier)
    s = x0*x1 + x1*x2 + x2*x0 + x0^2 + x1^2 + x2^2
    # FB membership quadrics that share leading forms with s so a degree-4 syzygy forms
    f1 = x0^2 - x1^2
    f2 = x1^2 - x2^2
    polys = [s, f1, f2]
    sumidx = [0]
    return polys, R, sumidx

# NEG-1: should be QUIET (no meaningful fall below Dmax). A generic regular system.
def build_NEG_1():
    F = GF(101)
    R = PolynomialRing(F, ["x0", "x1"], order="degrevlex")
    x0, x1 = R.gens()
    f1 = x0^2 + x0*x1 + 3*x1^2 + x0 + 1
    f2 = x1^2 + 2*x0*x1 + x0 + 5
    polys = [f1, f2]
    sumidx = [0]
    return polys, R, sumidx

# e-ring m=3 Semaev: base-FIRES but FAILS gate (artifact). The classic NR-027-style trap:
# a Semaev S3 written in elementary-symmetric coords whose fall is carried by an FB-row,
# not by the summation leading form.
def build_ERING_m3():
    F = GF(101)
    R = PolynomialRing(F, ["e1", "e2", "u"], order="degrevlex")
    e1, e2, u = R.gens()
    # Semaev S3 in symmetric coords (toy surrogate of the symmetric reduction):
    # S3 ~ (e1^2 - 4 e2) - linear-in-u target ; plus an FB-membership row in u.
    s3 = e1^2 - 4*e2 + u
    fb = u^2 - u  # idempotent-style FB row (the artifact carrier)
    polys = [s3, fb]
    sumidx = [0]
    return polys, R, sumidx

# POS-C: Weil S_3 over F_{p^2} -> 2 prime-field coords each. The ONLY known gate-meaningful
# fall (extension/Weil world where IC is known to work). Should PASS gate.
def build_POS_C():
    F = GF(101)
    # Weil restriction of a Semaev S3 over F_{p^2}: split each var into (a,b) components.
    R = PolynomialRing(F, ["a0","b0","a1","b1","a2","b2"], order="degrevlex")
    a0,b0,a1,b1,a2,b2 = R.gens()
    # nonresidue t for F_{p^2}=F[t]/(t^2 - nr); pick nr=2.
    nr = F(2)
    # symmetric Semaev S3 component equations (real + nr-part) of x0+x1+x2 type relation
    # use a bilinear "addition compatible" pair so the leading forms of BOTH summation
    # rows interlock -> gate-meaningful degree-4 fall.
    # x_i = a_i + b_i t
    # (x0 + x1 + x2) and (x0 x1 + x1 x2 + x2 x0) realified:
    re_lin = a0 + a1 + a2
    im_lin = b0 + b1 + b2
    # quadratic symmetric term real/imag parts:
    re_quad = (a0*a1 - nr*b0*b1) + (a1*a2 - nr*b1*b2) + (a2*a0 - nr*b2*b0)
    im_quad = (a0*b1 + a1*b0) + (a1*b2 + a2*b1) + (a2*b0 + a0*b2)
    polys = [re_quad, im_quad, re_lin, im_lin]
    sumidx = [0, 1]  # the two summation (quadratic symmetric) rows
    return polys, R, sumidx

def run_fixture(name, builder, expect_fire, expect_gate_meaningful, dff_max=None):
    try:
        polys, R, sumidx = builder()
        out = meter_gated(polys, R, sumidx, Dmax=10)
        fires = bool(out.get("fires"))
        gm = bool(out.get("gate_meaningful"))
        dff = out.get("d_ff")
        ok = (fires == expect_fire) and (gm == expect_gate_meaningful)
        if dff_max is not None and fires:
            ok = ok and (dff is not None and dff <= dff_max)
        LOG("  fixture %s: fires=%s gm=%s d_ff=%s D_reg=%s -> ok=%s"
            % (name, fires, gm, dff, out.get("D_reg"), ok))
        RES["fixtures"][name] = {"fires": fires, "gate_meaningful": gm,
                                 "d_ff": dff, "D_reg": out.get("D_reg"),
                                 "expect_fire": expect_fire,
                                 "expect_gate_meaningful": expect_gate_meaningful,
                                 "ok": ok}
        return ok
    except Exception as e:
        LOG("  fixture %s: EXCEPTION %s" % (name, repr(e)))
        RES["fixtures"][name] = {"error": repr(e), "ok": False}
        return False

LOG("\n--- (0b) self-validating meter on 4 fixtures ---")
all_fix_ok = True
if meter_ok:
    f_posA = run_fixture("POS-A", build_POS_A, expect_fire=True,
                         expect_gate_meaningful=True, dff_max=6)
    f_neg1 = run_fixture("NEG-1", build_NEG_1, expect_fire=False,
                         expect_gate_meaningful=False)
    f_ering = run_fixture("e-ring-m3", build_ERING_m3, expect_fire=True,
                          expect_gate_meaningful=False)
    f_posC = run_fixture("POS-C-WeilS3", build_POS_C, expect_fire=True,
                         expect_gate_meaningful=True)
    all_fix_ok = f_posA and f_neg1 and f_ering and f_posC
else:
    all_fix_ok = False

RES["meter_self_validated"] = bool(all_fix_ok)
LOG("meter_self_validated =", all_fix_ok)

def write_outputs(verdict_label, md_extra=""):
    RES["verdict"] = verdict_label
    RES["elapsed_sec"] = round(elapsed(), 2)
    try:
        with open(JSON_PATH, "w") as jf:
            json.dump(RES, jf, indent=2, default=str)
        LOG("wrote", JSON_PATH)
    except Exception as e:
        LOG("ERR writing json:", repr(e))
    try:
        with open(MD_PATH, "w") as mf:
            mf.write("# EXP-032 Result: symbolic S5 e-ring true degree\n\n")
            mf.write("Verdict: **%s**\n\n" % verdict_label)
            mf.write("meter_self_validated: %s\n\n" % RES["meter_self_validated"])
            mf.write("## Fixtures\n\n")
            for k, v in RES["fixtures"].items():
                mf.write("- %s: %s\n" % (k, v))
            mf.write("\n## S5 genuineness\n\n")
            mf.write("- s5_genuine (vanishes on real 5-tuples summing to O): %s\n" % RES["s5_genuine"])
            mf.write("- true per-variable degree: %s (expected 8 = 2^(m-1), m=4)\n" % RES["s5_true_per_var_degree"])
            mf.write("- total degree: %s\n" % RES["s5_total_degree"])
            mf.write("\n## e-ring leading form\n\n")
            mf.write("```\n%s\n```\n" % RES["ering_leading_form"])
            mf.write("\n## Gated meter at true degree\n\n")
            mf.write("- meter: %s\n" % RES["meter_at_true_degree"])
            mf.write("- crossbred admissible D<D_reg cuts: %s\n" % RES["crossbred_admissible_cuts"])
            mf.write("- any gate_meaningful fall: %s\n" % RES["any_gate_meaningful_fall"])
            mf.write("\n## Does NR-027 hold at true degree?\n\n")
            mf.write("- nr027_holds_at_true_degree: %s\n\n" % RES["nr027_holds_at_true_degree"])
            mf.write(md_extra + "\n")
            mf.write("\n## Notes\n\n")
            for n in RES["notes"]:
                mf.write("- %s\n" % n)
            mf.write("\nelapsed_sec: %s\n" % RES["elapsed_sec"])
        LOG("wrote", MD_PATH)
    except Exception as e:
        LOG("ERR writing md:", repr(e))

if not all_fix_ok:
    RES["notes"].append("Meter failed inline self-validation on >=1 of 4 fixtures -> INCONCLUSIVE per protocol.")
    LOG("ABORT: meter self-validation failed -> INCONCLUSIVE")
    write_outputs("inconclusive",
                  md_extra="Meter did not self-validate; cannot trust downstream meter readings.")
    _logf.close()
    sys.exit(0)

# -----------------------------------------------------------------------------
# (1) Build the genuine m=4 Semaev S5 at TRUE degree, verify genuineness.
#     Semaev S_{m+1}(x1,...,x_{m+1}) vanishes iff there exist y_i with
#     (x_i,y_i) on E and sum of points = O. For E: y^2 = x^3 + a x + b over F_p.
#     S2(x1,x2) = x1 - x2.
#     S3(x1,x2,x3) = (x1-x2)^2 x3^2 - 2((x1+x2)(x1 x2 + a) + 2b) x3
#                    + ((x1 x2 - a)^2 - 4 b (x1+x2))
#     S_{m+1} built by resultant elimination:
#       S_{m+1}(x1..x_{m+1}) =
#         Res_X( S_{m-k+1}(x1..x_{m-k}, X), S_{k+2}(x_{m-k+1}..x_{m+1}, X) )
#     True per-variable degree of S_n in each var is 2^{n-2}. For S5 (n=5) -> 2^3 = 8.  <-- TRUE DEGREE
# -----------------------------------------------------------------------------
LOG("\n--- (1) building genuine m=4 Semaev S5 at TRUE degree ---")

# Smallest cell: bits=13 -> pick a 13-bit prime; |FB|=3 conceptually. For symbolic S5
# the prime only matters for the genuineness numeric check; the leading form is char-indep
# for p not dividing small constants, so we use a 13-bit prime.
p13 = 8191  # 2^13 - 1, Mersenne (prime)
assert is_prime(p13)
Fp = GF(p13)

# Pick a real curve over Fp with a usable cofactor structure.
ec_a = Fp(2); ec_b = Fp(3)
E = EllipticCurve(Fp, [ec_a, ec_b])
LOG("curve E: y^2 = x^3 + %s x + %s over GF(%s), #E=%s" % (ec_a, ec_b, p13, E.order()))

# Symbolic ring for Semaev polynomials over Fp (true-degree construction).
Sx = PolynomialRing(Fp, ["X1","X2","X3","X4","X5"], order="degrevlex")
X1,X2,X3,X4,X5 = Sx.gens()

def semaev3(u, v, w, a, b):
    # S3(u,v,w) standard form
    return ( (u - v)**2 * w**2
             - 2*((u + v)*(u*v + a) + 2*b) * w
             + ((u*v - a)**2 - 4*b*(u + v)) )

a = Sx(ec_a); b = Sx(ec_b)

# Build S4 = Res_X( S3(X1,X2,X), S3(X3,X4,X) )  -> true per-var degree 4 in X1..X4
LOG("building S4 via resultant of two S3 in shared var X ...")
RX = PolynomialRing(Sx, "Xsh")
Xsh = RX.gen()
s3_a = semaev3(Sx(X1), Sx(X2), Xsh, a, b)  # poly in Xsh, coeffs in Sx
s3_b = semaev3(Sx(X3), Sx(X4), Xsh, a, b)
t_s4 = time.time()
S4 = s3_a.resultant(s3_b)   # element of Sx
LOG("S4 built in %.2fs, total degree %s" % (time.time()-t_s4, S4.degree()))

# Build S5 = Res_X( S4(X1,X2,X3,X)?, ... ) -- but S4 has 4 args. Standard recursion:
# S5(X1..X5) = Res_X( S4(X1,X2,X3,X), S3(X4,X5,X) ).
# We need S4 as a function of (X1,X2,X3, shared). Re-derive S4 in form S4(u,v,w, shared):
# Easiest: build S4 generically with a shared last variable, then specialize.
LOG("building S5 via Res_X( S4(X1,X2,X3,X), S3(X4,X5,X) ) ...")

# Build S4 with last argument symbolic-shared:
# S4(X1,X2,X3, W) = Res_Y( S3(X1,X2,Y), S3(X3,W,Y) )
RY = PolynomialRing(Sx, "Ysh")
Ysh = RY.gen()

def make_S5():
    # S4(X1,X2,X3,W) as polynomial in Sx with W = X4-slot variable; we build it with
    # a dedicated ring var Wv to keep it shared, then resultant against S3(X4? ) ...
    # Cleaner: do everything in a big ring with an auxiliary shared elimination var.
    Big = PolynomialRing(Fp, ["X1","X2","X3","X4","X5","W","Z"], order="degrevlex")
    b1,b2,b3,b4,b5,bW,bZ = Big.gens()
    aa = Big(ec_a); bb = Big(ec_b)
    # S4(X1,X2,X3,W) = Res_Z( S3(X1,X2,Z), S3(X3,W,Z) )
    RZ = PolynomialRing(Big, "Zsh")
    Zs = RZ.gen()
    s3_1 = semaev3(Big(b1), Big(b2), Zs, aa, bb)
    s3_2 = semaev3(Big(b3), Big(bW), Zs, aa, bb)
    S4W = s3_1.resultant(s3_2)  # in Big, vars X1,X2,X3,W
    # S5 = Res_W( S4(X1,X2,X3,W), S3(X4,X5,W) )
    RW = PolynomialRing(Big, "Wsh")
    Wsh = RW.gen()
    # re-express S4W as polynomial in Wsh
    S4W_inW = RW(0)
    # substitute bW -> Wsh in S4W
    S4W_dict = S4W.dict()
    for expo, coef in S4W_dict.items():
        # expo over Big gens; W is index 5
        wdeg = expo[5]
        # strip W from monomial
        rest_exps = list(expo); rest_exps[5] = 0
        rest_mon = Big({tuple(rest_exps): coef})
        S4W_inW += rest_mon * Wsh**wdeg
    s3_45 = semaev3(Big(b4), Big(b5), Wsh, aa, bb)
    S5big = S4W_inW.resultant(s3_45)  # in Big, vars X1..X5 (W,Z eliminated)
    # project to Sx (no W,Z left)
    S5_dict = S5big.dict()
    out = Sx(0)
    for expo, coef in S5_dict.items():
        # expo over Big 7 vars; W(idx5),Z(idx6) must be 0
        if expo[5] != 0 or expo[6] != 0:
            raise RuntimeError("S5 still has W/Z -> resultant elimination incomplete")
        e5 = expo[0:5]
        out += Sx(coef) * (X1**e5[0])*(X2**e5[1])*(X3**e5[2])*(X4**e5[3])*(X5**e5[4])
    return out

t_s5 = time.time()
S5_built = False
S5 = None
try:
    if budget_left() < 60:
        raise RuntimeError("insufficient budget to start S5 resultant")
    S5 = make_S5()
    S5_built = True
    LOG("S5 built in %.2fs" % (time.time()-t_s5))
except Exception as e:
    LOG("S5 build failed/too heavy:", repr(e))
    RES["notes"].append("S5 true-degree build failed/too heavy: %s" % repr(e))

if not S5_built or S5 is None or S5 == 0:
    RES["notes"].append("True-degree S5 not obtained at toy scale -> NR-027 stays surrogate-caveated.")
    write_outputs("inconclusive",
                  md_extra="True-degree symbolic S5 computationally out of reach in budget at toy scale.")
    _logf.close()
    sys.exit(0)

# True per-variable degree check
pv_degs = [S5.degree(g) for g in Sx.gens()]
RES["s5_true_per_var_degree"] = max(pv_degs)
RES["s5_total_degree"] = int(S5.degree())
LOG("S5 per-variable degrees:", pv_degs, " total degree:", S5.degree())
LOG("expected per-variable degree for S5 = 2^(5-2) = 8")

# -----------------------------------------------------------------------------
# (1b) Genuineness control: S5 must vanish on real 5-tuples whose points sum to O.
# -----------------------------------------------------------------------------
LOG("\n--- (1b) genuineness control: vanish on real 5-tuples summing to O ---")
set_random_seed(int(20260531))
genuine_pass = 0
genuine_trials = 0
genuine_fail_detail = []
ntrials = 6
for trial in range(ntrials):
    if budget_left() < 40:
        LOG("budget guard: stopping genuineness trials early at trial", trial)
        break
    try:
        Ps = [E.random_point() for _ in range(4)]
        if any(P.is_zero() for P in Ps):
            continue
        S = Ps[0] + Ps[1] + Ps[2] + Ps[3]
        P5 = -S  # so P1+P2+P3+P4+P5 = O
        if P5.is_zero():
            continue
        xs = [P.xy()[0] for P in (Ps + [P5])]
        val = S5(xs[0], xs[1], xs[2], xs[3], xs[4])
        genuine_trials += 1
        if val == 0:
            genuine_pass += 1
        else:
            genuine_fail_detail.append((trial, str(val)))
    except Exception as e:
        genuine_fail_detail.append((trial, "exc:" + repr(e)))

# Negative genuineness: random tuples NOT summing to O should generically NOT vanish.
neg_nonvanish = 0
neg_trials = 0
for trial in range(4):
    if budget_left() < 40:
        break
    try:
        Ps = [E.random_point() for _ in range(5)]
        if any(P.is_zero() for P in Ps):
            continue
        if (Ps[0]+Ps[1]+Ps[2]+Ps[3]+Ps[4]).is_zero():
            continue  # accidentally summed to O, skip
        xs = [P.xy()[0] for P in Ps]
        val = S5(xs[0], xs[1], xs[2], xs[3], xs[4])
        neg_trials += 1
        if val != 0:
            neg_nonvanish += 1
    except Exception:
        pass

LOG("genuineness: %d/%d real 5-tuples (sum=O) vanished" % (genuine_pass, genuine_trials))
LOG("neg-control: %d/%d random non-O 5-tuples did NOT vanish" % (neg_nonvanish, neg_trials))
s5_genuine = (genuine_trials >= 2 and genuine_pass == genuine_trials
              and neg_trials >= 1 and neg_nonvanish == neg_trials)
RES["s5_genuine"] = bool(s5_genuine)
RES["notes"].append("genuineness: %d/%d vanish on sum=O; neg %d/%d nonvanish"
                    % (genuine_pass, genuine_trials, neg_nonvanish, neg_trials))
if genuine_fail_detail:
    RES["notes"].append("genuine_fail_detail (truncated): %s" % str(genuine_fail_detail[:3]))

if not s5_genuine:
    RES["notes"].append("S5 failed genuineness control -> cannot trust as true Semaev S5; INCONCLUSIVE.")
    write_outputs("inconclusive",
                  md_extra="Constructed S5 did not pass the genuineness control "
                           "(vanish on real 5-tuples summing to O / nonvanish otherwise).")
    _logf.close()
    sys.exit(0)

# -----------------------------------------------------------------------------
# (2) Rewrite S5 in elementary-symmetric e-ring coords at smallest cell, leading form.
#     The free factor base variables are symmetrized: e1..e4 of (X1,X2,X3,X4); X5 = -R target.
#     We substitute X5 -> a fixed FB/target slot value symbol, then symmetrize X1..X4.
# -----------------------------------------------------------------------------
LOG("\n--- (2) e-ring rewrite (elementary symmetric in X1..X4), leading form ---")

# e-ring: variables e1,e2,e3,e4 (elementary symmetric of X1..X4) plus target var r (=X5 slot).
Er = PolynomialRing(Fp, ["e1","e2","e3","e4","r"], order="degrevlex")
e1,e2,e3,e4,r = Er.gens()

# We symmetrize S5 in X1..X4 with X5 = r. S5 is symmetric in all 5 args, hence in particular
# symmetric in X1..X4, so it is a polynomial in (e1,e2,e3,e4, X5). Express via power-sum->elem.
# Use Sage's symmetric function machinery on the X1..X4 part with X5 as a parameter.
def to_ering(poly5):
    # poly5 in Sx (X1..X5). Treat X5 as the target r; symmetrize X1..X4.
    # Collect coefficients as polynomials in X5, each a symmetric poly in X1..X4.
    # We use SymmetricFunctions over a base ring that carries X5.
    Base = PolynomialRing(Fp, "x5param")
    x5p = Base.gen()
    R4 = PolynomialRing(Base, ["Y1","Y2","Y3","Y4"], order="degrevlex")
    Y1,Y2,Y3,Y4 = R4.gens()
    # substitute X5 -> x5p, X1..X4 -> Y1..Y4
    sub = poly5.subs({X1:0,X2:0,X3:0,X4:0,X5:0})  # placeholder; do real subs below
    # rebuild via dict for safety
    pd = poly5.dict()
    val = R4(0)
    for expo, coef in pd.items():
        term = R4(coef) * (Y1**expo[0])*(Y2**expo[1])*(Y3**expo[2])*(Y4**expo[3]) * (x5p**expo[4])
        val += term
    # Now express 'val' (symmetric in Y1..Y4 over Base) in elementary symmetric polys.
    Sym = SymmetricFunctions(Base)
    e = Sym.e()
    # Use Sage's from_polynomial via the multivariate symmetric reduction:
    # R4 has the option to express; use the 'symmetric_reduction' approach:
    from sage.rings.polynomial.symmetric_reduction import SymmetricReductionStrategy
    # Manual: repeatedly substitute power sums. Simpler: use e_poly basis via
    # the built-in: R4 symmetric -> we map using Sage's 'symmetric function from polynomial'.
    # Build the elementary symmetric generators explicitly and do linear algebra on monomials.
    E1 = Y1+Y2+Y3+Y4
    E2 = Y1*Y2+Y1*Y3+Y1*Y4+Y2*Y3+Y2*Y4+Y3*Y4
    E3 = Y1*Y2*Y3+Y1*Y2*Y4+Y1*Y3*Y4+Y2*Y3*Y4
    E4 = Y1*Y2*Y3*Y4
    elem = {1:E1,2:E2,3:E3,4:E4}
    # Greedy symmetric reduction: express val as poly in E1..E4.
    out = Er(0)
    work = val
    guard = 0
    while work != 0 and guard < 5000:
        guard += 1
        lt = work.lt()  # leading term in degrevlex
        lm = work.lm()
        lc = work.lc()  # in Base = poly in x5p
        # exponent vector of lm in Y1..Y4
        ev = lm.exponents()[0]
        # partition lambda = sorted descending of ev
        lam = sorted(list(ev), reverse=True)
        # elementary basis exponents: m_i = lam_i - lam_{i+1}
        lam_p = lam + [0]
        mexp = [lam_p[i] - lam_p[i+1] for i in range(4)]
        # candidate monomial in E's:
        cand = R4(1)
        for i in range(4):
            cand *= elem[i+1]**mexp[i]
        cand_lc = cand.lc()
        if cand_lc == 0:
            break
        factor = lc / cand_lc
        # record in Er: lc is poly in x5p -> map to r
        lc_in_r = Er(0)
        for d_, c_ in enumerate(lc.list()):
            if c_ != 0:
                lc_in_r += Er(c_) * r**d_
        out += lc_in_r * (e1**mexp[0])*(e2**mexp[1])*(e3**mexp[2])*(e4**mexp[3])
        work = work - factor*cand
    if work != 0:
        raise RuntimeError("symmetric reduction did not terminate (residual nonzero)")
    return out

ering_ok = False
S5_e = None
try:
    if budget_left() < 50:
        raise RuntimeError("insufficient budget for e-ring symmetrization")
    S5_e = to_ering(S5)
    ering_ok = True
    LOG("S5 in e-ring built. total degree:", S5_e.degree(),
        " #monomials:", len(S5_e.monomials()))
except Exception as e:
    LOG("e-ring rewrite failed:", repr(e))
    RES["notes"].append("e-ring symmetrization failed/too heavy: %s" % repr(e))

if not ering_ok or S5_e is None or S5_e == 0:
    RES["notes"].append("True-degree S5 obtained & genuine, but e-ring rewrite out of reach in budget.")
    write_outputs("inconclusive",
                  md_extra="Genuine true-degree S5 built and verified, but elementary-symmetric "
                           "e-ring rewrite was too heavy at toy scale.")
    _logf.close()
    sys.exit(0)

# Homogeneous leading form of S5_e
lead_e = _homogeneous_leading_form(S5_e) if "_homogeneous_leading_form" in globals() else None
if lead_e is None:
    d = S5_e.degree()
    lead_e = Er(0)
    for c, m in zip(S5_e.coefficients(), S5_e.monomials()):
        if m.degree() == d:
            lead_e += c*m
RES["ering_leading_form"] = str(lead_e)[:1200]
LOG("e-ring leading form (deg %s):" % lead_e.degree(), str(lead_e)[:300])

# -----------------------------------------------------------------------------
# (3) Build the e-ring m=4 system with FB membership rows + run gated meter +
#     crossbred admissibility (NR-027 setup). |FB|=3 at smallest cell.
# -----------------------------------------------------------------------------
LOG("\n--- (3) gated meter at TRUE degree + crossbred admissibility ---")

# FB membership rows in the e-ring: at |FB|=3, the FB constrains the symmetric vars.
# These are the "FB-row" carriers suspected of the artifact fall in NR-027.
# Use generic membership relations consistent with a size-3 factor base (degree-2 rows).
fb1 = e1**2 - e2          # FB-row 1
fb2 = e2*e3 - e4          # FB-row 2
fb3 = e3**2 - e4*e1       # FB-row 3 (closes |FB|=3 toy structure)

polys_e = [S5_e, fb1, fb2, fb3]
sumidx_e = [0]  # only S5_e is the summation (Semaev) row

meter_out = None
try:
    Dmax_use = 14
    if budget_left() < 60:
        Dmax_use = min(10, Dmax_use)
        RES["notes"].append("budget guard: reduced Dmax to %d for final meter" % Dmax_use)
    meter_out = meter_gated(polys_e, Er, sumidx_e, Dmax=Dmax_use)
    LOG("meter_out:", {k: meter_out.get(k) for k in
         ["d_ff","D_reg","fires","gate_passes","gate_meaningful"]})
except Exception as e:
    LOG("meter at true degree failed:", repr(e))
    RES["notes"].append("meter_gated at true degree raised: %s" % repr(e))

if meter_out is None:
    write_outputs("inconclusive",
                  md_extra="Gated meter raised on the true-degree e-ring system.")
    _logf.close()
    sys.exit(0)

d_ff = meter_out.get("d_ff")
D_reg = meter_out.get("D_reg")
fires = bool(meter_out.get("fires"))
gate_meaningful = bool(meter_out.get("gate_meaningful"))
RES["meter_at_true_degree"] = {k: (str(meter_out.get(k)) if k=="gate_detail" else meter_out.get(k))
                               for k in ["d_ff","D_reg","fires","gate_passes","gate_meaningful"]}

# Crossbred admissibility: an admissible cut needs a D with d_ff <= D < D_reg
# (a fall strictly below the degree of regularity = a usable crossbred cut).
admissible = []
if d_ff is not None and D_reg is not None:
    for D in range(int(d_ff), int(D_reg)):
        admissible.append(int(D))
RES["crossbred_admissible_cuts"] = admissible
LOG("crossbred admissible D<D_reg cuts:", admissible)

# Any gate_meaningful fall at true degree?
any_gm = bool(fires and gate_meaningful and len(admissible) > 0)
RES["any_gate_meaningful_fall"] = any_gm
LOG("fires=%s gate_meaningful=%s admissible_cuts=%d -> any_gate_meaningful_fall=%s"
    % (fires, gate_meaningful, len(admissible), any_gm))

# NR-027 holds at true degree iff: cuts exist (or fire) but gate_meaningful is False
# (the falls are FB-row artifacts, S5 leading form does not enter firing rows).
nr027_holds = bool((fires or len(admissible) > 0) and (not gate_meaningful))
RES["nr027_holds_at_true_degree"] = nr027_holds
LOG("nr027_holds_at_true_degree =", nr027_holds)

# -----------------------------------------------------------------------------
# Verdict
# -----------------------------------------------------------------------------
if any_gm:
    verdict = "survived"  # masked gate_meaningful fall at true degree -> CANDIDATE, flag loudly
    md_extra = ("**LOUD FLAG: a gate_meaningful fall appeared at TRUE Semaev degree.** "
                "This is a CANDIDATE (not a survivor of the full pipeline) needing a downstream "
                "solver demo (PO-003). NR-027 would NOT hold at true degree.")
    LOG("!!! LOUD FLAG: gate_meaningful fall at true degree -> CANDIDATE !!!")
elif nr027_holds:
    verdict = "failed"  # NR-027 confirmed at true degree
    md_extra = ("NR-027 CONFIRMED at true Semaev degree: e-ring m=4 crossbred cuts (if any) are "
                "FB-row artifacts; the S5 homogeneous leading form does NOT enter the firing syzygy "
                "rows (gate_meaningful=False). Upgradable toward RESTRICTED THEOREM.")
else:
    verdict = "inconclusive"
    md_extra = ("Neither a clean gate_meaningful fall nor a clean FB-row artifact pattern was "
                "observed at true degree; D_reg/d_ff readings ambiguous.")

RES["notes"].append("S5 true per-var degree measured = %s (expected 8)." % RES["s5_true_per_var_degree"])
write_outputs(verdict, md_extra=md_extra)
LOG("\n=== DONE verdict=%s elapsed=%.1fs ===" % (verdict, elapsed()))
_logf.close()
