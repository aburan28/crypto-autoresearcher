# THM_JETBARRIER1 -- verification of the symbolic lemmas anchoring research/THM_JETBARRIER1.md
# Executor task TASK-20260718-THMJET (theory track, D1). Deterministic, single sage invocation.
# Artifact: research/verification/thm_jetbarrier1_check.out.json (+ stdout/stderr logs).
# Provenance: S3 convention copied verbatim from
#   experiments/EXP-JETB-001/jetbarrier1_model_check.sage (line 37).
# Checks S1..S8 anchor, respectively:
#   S1: leading coefficient of S_R(x1,z)=S3(x1,z,x_R) in z is (x1-x_R)^2   [L5(a)]
#   S2: x1=x_R fiber is exactly linear: -4*y_R^2*z + duplication numerator [L5(b)]
#   S3: one Newton step on a separable quadratic hits a root iff start=root [L5(c)]
#   S4: S3 symmetry + diagonal-gradient identities + discriminant resultant [C1 support]
#   S5: dual-number Taylor identity S(x+e t) = S(x) + e*(grad S . t)        [L1 anchor]
#   S6: concrete singular-locus dimension/degree of the S3 surface          [C1 evidence]
#   S7: generic (function-field) singular locus, m=3 and m=2 varieties      [C1 core]
#   S8: numeric anchors at p=101: omega-linearity, exhaustive Newton fact,
#       degenerate-fiber root = x(2R)                                     [T3/L5 anchors]
import json, time

T0 = time.time()
receipt = {
  "id": "THM-JETBARRIER1-check",
  "task": "TASK-20260718-THMJET",
  "purpose": "symbolic/numeric anchors for research/THM_JETBARRIER1.md",
  "started_utc": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
  "sage_version": None,
  "checks": [],
}
try:
    from sage.misc.banner import version as _v
    receipt["sage_version"] = str(_v())
except Exception:
    pass

def rec(cid, ok, details):
    receipt["checks"].append({"id": cid, "status": "PASS" if ok else "FAIL", "details": details})

def rec_censored(cid, why):
    receipt["checks"].append({"id": cid, "status": "CENSORED",
                              "details": why + " (infrastructure censoring, not evidence)"})

def _jdefault(o):
    # Sage preparser turns integer literals into sage Integer; make JSON-safe.
    try:
        return int(o)
    except Exception:
        return str(o)

def S3poly(X1, X2, X3, A, B):
    return ((X1-X2)**2 * X3**2 - 2*((X1+X2)*(X1*X2+A) + 2*B)*X3
            + ((X1*X2-A)**2 - 4*B*(X1+X2)))

# ---------------- S1 + S2: fiber structure of S_R(x1,z) over QQ[A,B,x1,xR,z] ----------------
R = PolynomialRing(QQ, names='A,B,x1,xR,z')
A, B, x1, xR, z = R.gens()
SR = S3poly(x1, z, xR, A, B)
lc2 = SR.coefficient(z**2)
ok1 = (lc2 == (x1 - xR)**2)
rec("S1_leading_coeff", ok1,
    "lc_z(S_R) = %s ; expected (x1-xR)^2" % str(lc2))

SRf = S3poly(xR, z, xR, A, B)
c2 = SRf.coefficient(z**2)
c1 = SRf.coefficient(z)
c0 = SRf.subs({z: 0})
ok2 = (c2 == 0) and (c1 == -4*(xR**3 + A*xR + B)) and (c0 == (xR**2 - A)**2 - 8*B*xR)
rec("S2_degenerate_fiber", ok2,
    ("S_R(xR,z) = (%s)*z + (%s); z^2 coeff = %s; expected linear with z-coeff "
     "-4*(xR^3+A*xR+B) = -4*y_R^2 and constant = duplication-formula numerator "
     "(xR^2-A)^2-8*B*xR, i.e. root = x(2R)") % (str(c1), str(c0), str(c2)))

# ---------------- S3: exact Newton fact on separable quadratics ----------------
R3 = PolynomialRing(QQ, names='c,r1,r2,z0')
c, r1, r2, z0 = R3.gens()
F3 = Frac(R3)
q  = lambda u: c*(u-r1)*(u-r2)
qp = lambda u: c*(2*u - r1 - r2)
Nmap = z0 - q(z0)/qp(z0)
id1 = (Nmap - r1)*(2*z0 - r1 - r2) - (z0 - r1)**2
id2 = (Nmap - r2)*(2*z0 - r1 - r2) - (z0 - r2)**2
crit = qp(z0) - 2*c*(z0 - (r1+r2)/2)
ok3 = (id1 == 0) and (id2 == 0) and (crit == 0)
rec("S3_newton_quadratic_exact", ok3,
    ("identities (N(z0)-ri)*(2z0-r1-r2) == (z0-ri)^2 for i=1,2 over the fraction field: "
     "N(z0)=ri iff z0=ri (given 2z0 != r1+r2); q'(z0)=0 iff z0=(r1+r2)/2 (unique critical "
     "point = the recorded deriv0-skip locus). id residuals: %s, %s, %s")
    % (str(id1), str(id2), str(crit)))

# ---------------- S4: S3 symmetry + diagonal gradient + resultant ----------------
R4 = PolynomialRing(QQ, names='A,B,x1,x2,x3')
A4, B4, X1, X2, X3 = R4.gens()
S = S3poly(X1, X2, X3, A4, B4)
sym1 = (S - S3poly(X2, X1, X3, A4, B4) == 0)
sym2 = (S - S3poly(X3, X2, X1, A4, B4) == 0)
e1 = X1 + X2 + X3
e2 = X1*X2 + X1*X3 + X2*X3
e3 = X1*X2*X3
alt = (e2 - A4)**2 - 4*e1*e3 - 4*B4*e1
sym3 = (S == alt)
d1 = S.derivative(X1).subs({X2: X1})
d2 = S.derivative(X2).subs({X2: X1})
d3 = S.derivative(X3).subs({X2: X1})
gd = (d1 == d2)
g3id = (d3 == -4*(X1**3 + A4*X1 + B4))
g1id = (d1 == -2*(3*X1**2 + A4)*X3 + 2*(X1**3 - A4*X1 - 2*B4))
RAB = PolynomialRing(QQ, names='A,B')
Aa, Bb = RAB.gens()
Rx = PolynomialRing(RAB, names='x')
xx = Rx.gen()
f = xx**3 + Aa*xx + Bb
res = f.resultant(f.derivative())
resok = (RAB(res) == 4*Aa**3 + 27*Bb**2)
ok4 = sym1 and sym2 and sym3 and gd and g3id and g1id and resok
rec("S4_symmetry_diagonal_resultant", ok4,
    ("symmetry x1<->x2: %s, x1<->x3: %s, S3 == (e2-A)^2-4*e1*e3-4*B*e1: %s ; "
     "diagonal (x2=x1): d1==d2: %s ; d3 == -4*(x1^3+A*x1+B) = -4*y1^2: %s ; "
     "d1 == -2*(3x1^2+A)x3 + 2(x1^3-A*x1-2B): %s ; resultant(x^3+Ax+B,3x^2+A) = %s "
     "(curve discriminant 4A^3+27B^2, nonzero iff E smooth: %s)")
    % (sym1, sym2, sym3, gd, g3id, g1id, str(res), resok))

# ---------------- S5: dual-number Taylor identity over QQ ----------------
R5 = PolynomialRing(QQ, names='A,B,x1,x2,x3,t1,t2,t3,e')
A5, B5, a1, a2, a3, t1, t2, t3, ee = R5.gens()
Q5 = R5.quotient(R5.ideal(ee**2))
Aq, Bq, q1, q2, q3, u1, u2, u3, eq = Q5.gens()
Sd = S3poly(q1 + eq*u1, q2 + eq*u2, q3 + eq*u3, Aq, Bq)
L = Sd.lift()
cc1 = L.coefficient(ee)
cc0 = L - cc1*ee
Sbare = S3poly(a1, a2, a3, A5, B5)
expect = u1*Sbare.derivative(a1) + u2*Sbare.derivative(a2) + u3*Sbare.derivative(a3)
ok5 = (cc0 == Sbare) and (cc1 == expect)
rec("S5_dual_taylor", ok5,
    "S3(x+e t) mod e^2 == S3(x) + e*(grad S3 . t) over QQ (mechanism of L1/T1)")

# ---------------- S6: concrete singular locus of the S3 surface ----------------
p6 = 1009
F6 = GF(p6)
A6, B6 = None, None
Ea = None
for Aa6 in range(3, 40):
    for Bb6 in range(1, 40):
        if F6(4*Aa6**3 + 27*Bb6**2) == 0:
            continue
        E6 = EllipticCurve(F6, [Aa6, Bb6])
        N6 = int(E6.order())
        tr6 = p6 + 1 - N6
        if tr6 == 0 or N6 == p6:
            continue
        A6, B6, Ea = Aa6, Bb6, E6
        break
    if A6 is not None:
        break
R6 = PolynomialRing(F6, names='x1,x2,x3')
X1, X2, X3 = R6.gens()
S6p = S3poly(X1, X2, X3, F6(A6), F6(B6))
J6 = R6.ideal([S6p, S6p.derivative(X1), S6p.derivative(X2), S6p.derivative(X3)])
det6 = {"p": int(p6), "A": int(A6), "B": int(B6), "N_E": int(Ea.order())}
try:
    from cysignals.alarm import alarm, cancel_alarm, AlarmInterrupt
    alarm(120)
    try:
        dim6 = J6.dimension()
        det6["dimension"] = int(dim6)
        if dim6 == 0:
            det6["degree_closure"] = int(J6.vector_space_dimension())
            alarm(120)
            try:
                det6["n_Fp_points"] = len(J6.variety(F6))
            except AlarmInterrupt:
                det6["n_Fp_points"] = "censored_timeout"
    except AlarmInterrupt:
        rec_censored("S6_concrete_singular_locus", "Groebner/variety > 120 s at p=1009")
        det6 = None
    finally:
        cancel_alarm()
except ImportError:
    dim6 = J6.dimension()
    det6["dimension"] = int(dim6)
if det6 is not None:
    ok6 = (det6.get("dimension") == 0)
    rec("S6_concrete_singular_locus", ok6,
        "singular-locus ideal of x-only S3 surface over F_1009 (A=%s,B=%s): %s"
        % (A6, B6, json.dumps(det6, default=_jdefault)))

# ---------------- S7: generic singular loci over function fields ----------------
try:
    from cysignals.alarm import alarm, cancel_alarm, AlarmInterrupt
    have_alarm = True
except ImportError:
    have_alarm = False

KAB = Frac(PolynomialRing(QQ, names='A,B'))
R7 = PolynomialRing(KAB, names='x1,x2,x3')
Y1, Y2, Y3 = R7.gens()
Aa7 = KAB(PolynomialRing(QQ, names='A,B').gen(0))
Bb7 = KAB(PolynomialRing(QQ, names='A,B').gen(1))
S7p = S3poly(Y1, Y2, Y3, Aa7, Bb7)
J7 = R7.ideal([S7p, S7p.derivative(Y1), S7p.derivative(Y2), S7p.derivative(Y3)])
if have_alarm:
    alarm(240)
    try:
        dim7 = J7.dimension()
        vd7 = int(J7.vector_space_dimension()) if dim7 == 0 else None
        rec("S7_generic_singular_locus_m3", dim7 == 0,
            "over Frac(QQ[A,B]): singular locus of x-only S3 surface has dimension %s, "
            "degree(closure) %s" % (dim7, vd7))
    except AlarmInterrupt:
        rec_censored("S7_generic_singular_locus_m3", "generic elimination > 240 s")
    finally:
        cancel_alarm()
    # m=2 target variety S_R(x1,z), generic over A,B,xR
    K2 = Frac(PolynomialRing(QQ, names='A,B,xR'))
    R8 = PolynomialRing(K2, names='x1,z')
    w1, wz = R8.gens()
    gA = PolynomialRing(QQ, names='A,B,xR')
    A8 = K2(gA.gen(0)); B8 = K2(gA.gen(1)); xR8 = K2(gA.gen(2))
    SR8 = S3poly(w1, wz, xR8, A8, B8)
    J8 = R8.ideal([SR8, SR8.derivative(w1), SR8.derivative(wz)])
    alarm(120)
    try:
        dim8 = J8.dimension()
        vd8 = int(J8.vector_space_dimension()) if dim8 == 0 else None
        rec("S7_generic_singular_locus_m2", dim8 <= 0,
            "over Frac(QQ[A,B,xR]): singular locus of the plane curve S_R(x1,z)=0 has "
            "dimension %s (<=0 expected), degree(closure) %s" % (dim8, vd8))
    except AlarmInterrupt:
        rec_censored("S7_generic_singular_locus_m2", "generic elimination > 120 s")
    finally:
        cancel_alarm()
else:
    rec_censored("S7_generic_singular_locus_m3", "cysignals unavailable")
    rec_censored("S7_generic_singular_locus_m2", "cysignals unavailable")

# ---------------- S8: numeric anchors at p=101 ----------------
set_random_seed(20260717)
p8 = 101
F8 = GF(p8)
E8 = None
for Aa8 in range(0, 50):
    for Bb8 in range(1, 50):
        if F8(4*Aa8**3 + 27*Bb8**2) == 0:
            continue
        Et = EllipticCurve(F8, [Aa8, Bb8])
        Nt = int(Et.order())
        if p8 + 1 - Nt == 0 or Nt == p8:
            continue
        E8, A8v, B8v, N8 = Et, Aa8, Bb8, Nt
        break
    if E8 is not None:
        break
det8 = {"p": int(p8), "A": int(A8v), "B": int(B8v), "N_E": int(N8)}

# (a) omega-linearity spot check (20 probes), replicating fg_probe convention
def du_(u, v): return (u[0]+v[0], u[1]+v[1])
def ds_(u, v): return (u[0]-v[0], u[1]-v[1])
def dm_(u, v): return (u[0]*v[0], u[0]*v[1] + u[1]*v[0])
def ddiv_(u, v): return (u[0]/v[0], (u[1]*v[0] - u[0]*v[1])/(v[0]**2))

fg = {"tested": 0, "base_fail": 0, "lin_fail": 0, "swap_fail": 0, "skipped": 0}
for _ in range(60):
    if fg["tested"] >= 20:
        break
    P = E8.random_point(); Q = E8.random_point()
    if P.is_zero() or Q.is_zero():
        fg["skipped"] += 1; continue
    X1, Y1 = P.xy(); X2, Y2 = Q.xy()
    if Y1 == 0 or Y2 == 0 or X1 == X2:
        fg["skipped"] += 1; continue
    R3 = P + Q
    if R3.is_zero():
        fg["skipped"] += 1; continue
    X3, Y3 = R3.xy()
    a = F8.random_element(); b = F8.random_element()
    lam1 = (3*X1**2 + A8v)/(2*Y1); lam2 = (3*X2**2 + A8v)/(2*Y2)
    s = a/(2*Y1) + b/(2*Y2)
    Pt = ((X1, a), (Y1, lam1*a)); Qt = ((X2, b), (Y2, lam2*b))
    lamt = ddiv_(ds_(Qt[1], Pt[1]), ds_(Qt[0], Pt[0]))
    x3t = ds_(ds_(dm_(lamt, lamt), Pt[0]), Qt[0])
    y3t = ds_(dm_(lamt, ds_(Pt[0], x3t)), Pt[1])
    fg["tested"] += 1
    if not (x3t[0] == X3 and y3t[0] == Y3):
        fg["base_fail"] += 1
    if Y3 != 0:
        c3 = 2*Y3*s
        lin_ok = (x3t[1] == c3) and (y3t[1] == ((3*X3**2 + A8v)/(2*Y3))*c3)
    else:
        lin_ok = (x3t[1] == 0) and (y3t[1] == (3*X3**2 + A8v)*s)
    if not lin_ok:
        fg["lin_fail"] += 1
det8["fg_linearity"] = fg

# (b) exhaustive Newton fact on one non-degenerate fiber
G8 = E8.gen(0)
P1 = 3*G8; Qb = 5*G8; Rt = P1 + Qb          # Rt = 8*G8
xRv = Rt.xy()[0]
Rz = PolynomialRing(F8, names='z')
zz = Rz.gen()
SRf8 = S3poly(P1.xy()[0], zz, xRv, F8(A8v), F8(B8v))
roots = sorted(int(r) for r in SRf8.roots(multiplicities=False))
exp_roots = sorted([int((Rt - P1).xy()[0]), int((Rt + P1).xy()[0])])
SRd8 = SRf8.derivative()
crits, mism = [], []
for z0i in range(p8):
    z0 = F8(z0i)
    fv = SRf8(z0); dv = SRd8(z0)
    if dv == 0:
        crits.append(z0i); continue
    x2h = z0 - fv/dv
    hit = (SRf8(x2h) == 0)
    if hit != (z0i in roots):
        mism.append(z0i)
nb = {"fiber_roots": roots, "expected_roots_x(R-P1)_x(R+P1)": exp_roots,
      "roots_match": roots == exp_roots, "n_critical": len(crits),
      "critical_values": crits, "hit_iff_root_start_mismatches": len(mism)}
det8["newton_exhaustive_fiber"] = nb

# (c) degenerate fiber x1 = xR: linear, root = x(2R), Newton hits from 10 starts
SRg8 = S3poly(xRv, zz, xRv, F8(A8v), F8(B8v))
yRv = Rt.xy()[1]
deg_lin = SRg8.degree()
lc_ok = (SRg8[1] == -4*(yRv**2))
root_deg = (-SRg8[0]/SRg8[1]) if deg_lin == 1 else None
x2R = int((2*Rt).xy()[0])
hits10 = 0
for z0i in [0, 7, 13, 23, 42, 55, 61, 77, 88, 99]:
    z0 = F8(z0i)
    fv = SRg8(z0); dv = SRg8.derivative()(z0)
    if dv == 0:
        continue
    if SRg8(z0 - fv/dv) == 0:
        hits10 += 1
det8["degenerate_fiber"] = {"degree": int(deg_lin), "lin_coeff_is_-4yR2": bool(lc_ok),
                            "root": int(root_deg) if root_deg is not None else None,
                            "x_2R": x2R, "root_is_x2R": (int(root_deg) == x2R) if root_deg is not None else False,
                            "newton_hits_of_10": hits10}
ok8 = (fg["base_fail"] == 0 and fg["lin_fail"] == 0 and fg["tested"] == 20
       and nb["roots_match"] and len(mism) == 0 and nb["n_critical"] == 1
       and deg_lin == 1 and lc_ok and det8["degenerate_fiber"]["root_is_x2R"]
       and hits10 == 10)
rec("S8_numeric_anchors_p101", ok8, json.dumps(det8, default=_jdefault))

receipt["wall_seconds"] = round(time.time() - T0, 3)
receipt["finished_utc"] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
n_pass = sum(1 for c in receipt["checks"] if c["status"] == "PASS")
n_fail = sum(1 for c in receipt["checks"] if c["status"] == "FAIL")
n_cens = sum(1 for c in receipt["checks"] if c["status"] == "CENSORED")
receipt["summary"] = {"pass": n_pass, "fail": n_fail, "censored": n_cens}
OUT = "/Volumes/Volume/crypto-autoresearcher/research/verification/thm_jetbarrier1_check.out.json"
with open(OUT, "w") as fh:
    json.dump(receipt, fh, indent=2, default=_jdefault)
print(json.dumps(receipt["summary"], default=_jdefault))
print("receipt written:", OUT)
