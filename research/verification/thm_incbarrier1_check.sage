# THM-INCBARRIER1 verification script (TASK-20260718-THMINC).
# Independent check of the claims made in research/THM_INCBARRIER1.md:
#  (1) EC chord arrangements have richness r <= 3 (data check on recorded hists).
#  (2) Identities: num_lines = C(M,2) - 2*T3 ; c2 = C(M,2) - 3*T3 (recorded data).
#  (3) Independent recomputation of per-instance T3 from recorded x_set (T3 = 2 * #x-triples).
#  (4) Full-group collinear-triple count T3full by exact enumeration; cross-check against
#      the closed form (n^2 - 6n + 5 + 3z + 2t)/6 (z = #2-torsion x's, t = #order-3 points).
#  (5) Exact mean and variance of T3 over uniform B-subsets of X_E (hypergeometric moments);
#      measured 6-seed means vs exact model (z-scores); instrument heuristic ratio h/mu.
#  (6) Group-AP x-set excess family: T3(AP) exact count vs generic mean (excess factor).
#  (7) Per-cell Weil-method barrier numbers: provable error scale M*sqrt(p*B)/3 vs mu.
# Curves are rebuilt with the instrument's own procedure (CURVE_SEED = 20260717) and
# asserted equal to the curves recorded in RUN-INCB-001-b/raw.json.
# Deterministic; no randomness except the seeded curve/x-set rebuild (fixed seeds).
import json, sys
from math import comb, sqrt
from fractions import Fraction
def Frac(a, b):
    return Fraction(int(a), int(b))

REPO = "/Volumes/Volume/crypto-autoresearcher"
RAW = REPO + "/experiments/EXP-INCB-001/runs/RUN-INCB-001-b/raw.json"
OUT = REPO + "/research/verification/thm_incbarrier1_check_output.json"
CURVE_SEED = 20260717
PRIMES = [211, 1009, 4099]

report = {"checks": [], "curves": [], "cells": [], "ap_test": [], "notes": []}
def check(name, ok, detail=""):
    report["checks"].append({"name": name, "pass": bool(ok), "detail": detail})
    print(("PASS " if ok else "FAIL ") + name + (" :: " + str(detail) if detail else ""), flush=True)

def make_curve(p):
    F = GF(p); set_random_seed(CURVE_SEED)
    while True:
        a = F(randint(1, p - 1)); b = F(randint(1, p - 1))
        if 4 * a**3 + 27 * b**2 != 0:
            E = EllipticCurve(F, [a, b])
            n = int(E.order())
            if (p + 1 - n) % p != 0:
                return E, n, int(a), int(b)

def curve_data(p, a, b):
    """Return (L, z, t, sqrt_table) for y^2 = x^3 + a x + b over F_p."""
    F = GF(p)
    L = 0; z = 0; t = 0; ys = {}
    for xx in range(p):
        v = F(xx)**3 + F(a)*F(xx) + F(b)
        if v == 0:
            z += 1; L += 1; ys[xx] = 0
        elif v.is_square():
            L += 1; ys[xx] = int(v.sqrt())
    # order-3 points: P != O, 3P = O  <=>  x(2P) = x(P), y(P) != 0
    for xx, yy in ys.items():
        if yy == 0:
            continue
        lam = (F(3)*F(xx)**2 + F(a)) / F(2*yy)
        x2 = lam**2 - F(2*xx)
        if int(x2) == xx:
            t += 2
    return L, z, t, ys

def addp(P1, P2, p, a):
    """Raw affine addition over F_p; P = (x,y) or None for O."""
    if P1 is None: return P2
    if P2 is None: return P1
    x1, y1 = P1; x2, y2 = P2
    if x1 == x2:
        if (y1 + y2) % p == 0: return None
        lam = ((3*x1*x1 + a) * pow(2*y1, -1, p)) % p
    else:
        lam = ((y2 - y1) * pow((x2 - x1) % p, -1, p)) % p
    x3 = (lam*lam - x1 - x2) % p
    y3 = (lam*(x1 - x3) - y1) % p
    return (x3, y3)

def xsum_xdiff(x1, y1, x2, y2, p):
    """x(P1+P2) and x(P1-P2) for x1 != x2, raw modular arithmetic."""
    inv = pow((x2 - x1) % p, -1, p)
    lam1 = ((y2 - y1) * inv) % p
    lam2 = ((-y2 - y1) * inv) % p
    return (lam1*lam1 - x1 - x2) % p, (lam2*lam2 - x1 - x2) % p

def t3_of_xset(xs, ys, p, klein_xs=None):
    """T3 = (2/3) * sum over unordered x-pairs of e_F(pair), minus Klein indicator."""
    xs = sorted(xs); Fset = set(xs); total = 0
    for i in range(len(xs)):
        x1 = xs[i]; y1 = ys[x1]
        for j in range(i+1, len(xs)):
            x2 = xs[j]; y2 = ys[x2]
            xa, xb = xsum_xdiff(x1, y1, x2, y2, p)
            e = 0
            if xa in Fset and xa != x1 and xa != x2: e += 1
            if xb in Fset and xb != x1 and xb != x2 and xb != xa: e += 1
            total += e
    assert total % 3 == 0
    adj = 1 if (klein_xs and all(k in Fset for k in klein_xs)) else 0
    return 2 * total // 3 - adj

with open(RAW) as f:
    raw = json.load(f)

for cinfo in raw["curves"]:
    p = cinfo["p"]; a = cinfo["a"]; b = cinfo["b"]; n_rec = cinfo["n"]; L_rec = cinfo["lifting_x"]
    E, n, ai, bi = make_curve(p)
    check(f"curve-rebuild p={p}", (ai, bi, n) == (a, b, n_rec),
          f"rebuilt a={ai} b={bi} n={n} vs recorded a={a} b={b} n={n_rec}")
    L, z, t, ys = curve_data(p, a, b)
    check(f"L-match p={p}", L == L_rec, f"L={L} recorded {L_rec}")
    check(f"group-count-identity p={p}", n == 1 + 2*L - z, f"n={n}, L={L}, z={z}")

    # --- full-group triple enumeration over x-pairs ---
    xs_all = sorted(ys.keys())
    sum_e = 0; W2 = 0; Vset = set(); g = {x: 0 for x in xs_all}
    pk = p * p
    for i in range(len(xs_all)):
        x1 = xs_all[i]; y1 = ys[x1]
        for j in range(i+1, len(xs_all)):
            x2 = xs_all[j]; y2 = ys[x2]
            xa, xb = xsum_xdiff(x1, y1, x2, y2, p)
            cands = []
            if xa != x1 and xa != x2: cands.append(xa)
            if xb != x1 and xb != x2 and xb != xa: cands.append(xb)
            e = len(cands)
            sum_e += e
            if e == 2: W2 += 1
            for x3 in cands:
                tri = tuple(sorted((x1, x2, x3)))
                key = tri[0]*pk + tri[1]*p + tri[2]
                if key not in Vset:
                    Vset.add(key)
                    g[x1] += 1; g[x2] += 1; g[x3] += 1
    V = len(Vset)
    # Klein correction: the all-2-torsion x-triple (exists iff z=3) carries exactly ONE
    # point triple, not two (its points have no +/- partners). So T3full = 2V - kappa.
    kappa = 1 if z == 3 else 0
    T3full_enum = 2 * V - kappa
    check(f"sum_e=3V p={p}", sum_e == 3*V, f"sum_e={sum_e}, V={V}")
    A_form = n*n - 6*n + 5 + 3*z + 2*t
    T3full_form = Frac(A_form, 6)
    check(f"T3full-closed-form p={p}", T3full_form.denominator == 1 and int(T3full_form) == T3full_enum,
          f"formula={T3full_form} (n={n},z={z},t={t}), enumeration(2V-kappa)={T3full_enum}")
    W1 = sum(comb(gv, 2) for gv in g.values()) - 2*W2
    W0 = comb(V, 2) - W1 - W2
    # Klein x-triple data (for exact moments of T3 = 2X - Y, Y = indicator(Klein triple in F))
    klein = None
    if z == 3:
        kx = sorted(x for x in xs_all if ys[x] == 0)
        ke = []
        for i1 in range(3):
            for j1 in range(i1+1, 3):
                xa, xb = xsum_xdiff(kx[i1], 0, kx[j1], 0, p)
                cc = [u for u in (xa, xb) if u != kx[i1] and u != kx[j1]]
                ke.append(len(set(cc)))
        klein = {"xs": kx, "e_pairs": ke, "g": [g[x] for x in kx]}
    report["curves"].append({"p": p, "a": a, "b": b, "n": n, "L": L, "z": z, "t": t,
                             "V_xtriples": V, "T3full": T3full_enum, "kappa": kappa,
                             "W2_shared2": W2, "W1_shared1": W1, "W0_shared0": W0,
                             "klein": klein})
    print(f"p={p}: n={n} L={L} z={z} t={t} V={V} T3full={T3full_enum} W2={W2} W1={W1}", flush=True)

    # --- per-cell exact moments and measured comparison ---
    cells = [c for c in raw["cells"] if c["p"] == p]
    for cell in cells:
        B = cell["B"]
        def fall(x, k):
            r = 1
            for u in range(k): r *= (x - u)
            return r
        pi3 = Frac(fall(B,3), fall(L,3))
        mu_x = Frac(V * fall(B,3), fall(L,3))
        mu_T = Frac((2*V - kappa) * fall(B,3), fall(L,3))
        E_X2 = (Frac(V * fall(B,3), fall(L,3)) + Frac(2*W2 * fall(B,4), fall(L,4))
                + Frac(2*W1 * fall(B,5), fall(L,5)) + Frac(2*W0 * fall(B,6), fall(L,6)))
        var_x = E_X2 - mu_x*mu_x
        var_T = var_x + var_x + var_x + var_x          # T3 = 2X exactly when kappa = 0
        if kappa:
            # exact moments of T3 = 2X - Y, Y = 1[Klein x-triple subset of F]
            s2 = sum(e - 1 for e in klein["e_pairs"])
            s1 = sum(gv - 1 for gv in klein["g"]) - 2*s2
            s0 = (V - 1) - s1 - s2
            E_XY = pi3 * (Frac(1,1) + Frac(s2*fall(B-3,1), fall(L-3,1))
                          + Frac(s1*fall(B-3,2), fall(L-3,2))
                          + Frac(s0*fall(B-3,3), fall(L-3,3)))
            cov = E_XY - mu_x*pi3
            var_Y = pi3 - pi3*pi3
            var_T = var_T - (cov + cov + cov + cov) + var_Y
        sd_T = sqrt(max(0.0, float(var_T)))
        M = 2*B
        h = Frac(comb(M,2) * B, 3*L)          # instrument per-instance heuristic
        ratio_h_mu = float(h / mu_T) if mu_T else None
        ec_Ts = [inst["triples_T"] for inst in cell["instances"] if inst["family"] == "ec"]
        mean_meas = sum(ec_Ts)/len(ec_Ts)
        se_mean = sd_T/sqrt(len(ec_Ts)) if sd_T else None
        zscore = (mean_meas - float(mu_T))/se_mean if se_mean else None
        wb = M*sqrt(p*B)/3.0                      # proved Weil-method error scale
        report["cells"].append({"p": p, "B": B, "mu_exact": float(mu_T), "sd_exact": sd_T,
                                "heuristic_h": float(h), "h_over_mu": ratio_h_mu,
                                "measured_Ts": ec_Ts, "measured_mean": mean_meas,
                                "z_vs_exact_model": zscore,
                                "weil_error_scale": wb, "weil_over_mu": wb/float(mu_T) if mu_T else None})
        print(f"  cell p={p} B={B}: mu={float(mu_T):.4f} sd={sd_T:.4f} h/mu={ratio_h_mu:.4f} "
              f"meas_mean={mean_meas:.3f} z={zscore if zscore is None else round(zscore,3)} "
              f"weil/mu={wb/float(mu_T) if mu_T else None:.1f}", flush=True)

    # --- raw.json identity checks + independent T3 recomputation ---
    for cell in cells:
        for inst in cell["instances"]:
            if inst["family"] != "ec": continue
            Mi = inst["M"]; T = inst["triples_T"]; hist = {int(k): v for k, v in inst["hist"].items()}
            tag = f"p={p} B={cell['B']} seed={inst['seed']}"
            check(f"bezout-r<=3 {tag}", max(hist) <= 3, f"max r = {max(hist)}")
            check(f"lines-identity {tag}", inst["num_lines"] == comb(Mi,2) - 2*T,
                  f"num_lines={inst['num_lines']} vs C(M,2)-2T={comb(Mi,2)-2*T}")
            check(f"c2-identity {tag}", hist.get(2,0) == comb(Mi,2) - 3*T,
                  f"c2={hist.get(2,0)} vs C(M,2)-3T={comb(Mi,2)-3*T}")
            check(f"c3=T {tag}", hist.get(3,0) == T, f"c3={hist.get(3,0)} T={T}")
            kxs = klein["xs"] if klein else None
            T_re = t3_of_xset(inst["x_set"], ys, p, kxs)
            check(f"T3-recompute {tag}", T_re == T, f"recomputed {T_re} vs recorded {T}")
            if kxs:
                check(f"klein-not-in-F {tag}", not all(k in set(inst["x_set"]) for k in kxs),
                      "Klein triple presence would need the -1 correction")

    # --- group-AP excess family: point of order > 3*Bmax ensures no wraparound ---
    Bmax = max(c["B"] for c in cells)
    P0 = None; ord0 = None
    for xx in xs_all:
        if ys[xx] == 0: continue
        Q = E(GF(p)(xx), GF(p)(ys[xx]))
        o = int(Q.order())
        if o > 3*Bmax + 3:
            P0 = (xx, ys[xx]); ord0 = o; break
    if P0 is None:
        report["notes"].append(f"p={p}: no point of order > {3*Bmax+3}; AP test skipped")
    else:
        Bp = min(Bmax, (ord0 - 1)//3)
        xs_ap = []; seen = set(); P = None
        ok_build = True
        for i in range(1, Bp + 1):
            P = addp(P, P0, p, a)
            if P is None or P[0] in seen:
                ok_build = False; break
            seen.add(P[0]); xs_ap.append(P[0])
        check(f"AP-build p={p}", ok_build and len(xs_ap) == Bp,
              f"B'={Bp} distinct x's from ord={ord0} point")
        if ok_build:
            T_ap = t3_of_xset(xs_ap, ys, p)
            pred_ap = 2 * ((Bp - 1)**2 // 4)
            def fall(x, k):
                r = 1
                for u in range(k): r *= (x - u)
                return r
            mu_ap = float(Frac((2*V - kappa)*fall(Bp,3), fall(L,3)))
            check(f"AP-closed-count p={p}", T_ap == pred_ap,
                  f"T3_AP={T_ap} vs 2*floor((B'-1)^2/4)={pred_ap} (B'={Bp})")
            report["ap_test"].append({"p": p, "B_ap": Bp, "ord_point": ord0, "T3_ap": T_ap,
                                      "T3_ap_closed_pred": pred_ap, "mu_generic_sameB": mu_ap,
                                      "excess_factor": (T_ap/mu_ap) if mu_ap else None})
            print(f"  AP p={p}: B'={Bp} ord={ord0} T3_AP={T_ap} pred={pred_ap} mu_gen={mu_ap:.4f} "
                  f"excess={T_ap/mu_ap if mu_ap else None:.1f}", flush=True)

with open(OUT, "w") as f:
    json.dump(report, f, indent=1, default=str)
fails = [c for c in report["checks"] if not c["pass"]]
print(f"TOTAL CHECKS: {len(report['checks'])}, FAILURES: {len(fails)}", flush=True)
for c in fails: print("FAILED:", c, flush=True)
