# THM-INCBARRIER2 verification script (TASK-20260724-LEMINC).
# Independent exact/numerical check of the claims made in research/THM_INCBARRIER2.md:
#  (A) Exact chord-profile identity: T3(F) = mu_tilde + (1/6) * sum_{x in F} delta(x),
#      with r(x) = #ordered pairs (P,Q) in Pcal^2, P != Q, P+Q != O, x(P+Q) = x;
#      T = sum r = M(M-1) - 2(B - z_F); rbar = T/L; mu_tilde = (B*rbar - 2d)/6.
#  (B) S = sum_{x in F} r(x) = 6*T3 + 2d (re-verified per instance).
#  (C) Second-moment identity: N2 = sum_x r(x)^2 = 2*E1 - sum_{g 2-torsion} A'(g)^2,
#      where E1 = restricted
#      additive energy #{(P,Q,P',Q'): P+Q = P'+Q' != O, P!=Q, P'!=Q'}.
#  (D) Certificate: |T3 - mu_tilde| <= (1/6)*sqrt(B * N2tilde), N2tilde = N2 - T^2/L >= 0.
#  (E) Profile flatness for uniform-x factor bases: N2tilde / M^2 (predicted O(1), ~2-4)
#      and fourth profile moment delta4 / (M^4/L) (predicted O(1)); vs AP family where
#      N2tilde = Theta(M^3) and the certificate is tight to a constant factor.
#  (F) Character sums U(psi) (numpy): Parseval checks sum|U|^2 = p*N2, sum|U|^4 = p*E_x;
#      unconditional lower bounds sum_{psi!=0}|U|^2 >= T^2*(p-L)/L and
#      sum_{psi!=0}|U|^4 >= (sum_{psi!=0}|U|^2)^2/(p-1); max|U| vs Weil scale 2M*sqrt(p).
#  (G) Group-AP family: T3 = 2*floor((B-1)^2/4) re-verified; certificate tightness ratio.
# Curves as recorded in THM_INCBARRIER1.md (rebuilt there; here hardcoded a,b and
# independently re-checked via E.order()). Deterministic; seeded sampling only.
# Toy scale p <= 2^12: no crypto-scale claim (rule 7).
import json, random
from math import sqrt, floor
from fractions import Fraction
import numpy as np

REPO = "/Volumes/Volume/crypto-autoresearcher"
OUT = REPO + "/research/verification/thm_incbarrier2_check_output.json"
CURVES = {211: (7, 62, 210), 1009: (921, 976, 984), 4099: (211, 1972, 4056)}
UNI_CELLS = [(211, 8), (1009, 10), (1009, 16), (4099, 8), (4099, 16), (4099, 28)]
UNI_SEEDS = [20260721, 7, 99]
AP_CELLS = [(211, 8), (1009, 16), (4099, 28)]
CHAR_INSTANCES = [(1009, 16, 20260721), (4099, 28, 20260721)]  # (p,B,seed) for character sums

def Fr(a, b=1):
    return Fraction(int(a), int(b))

report = {"checks": [], "instances": [], "ap": [], "char": [], "env": {}}
def check(name, ok, detail=""):
    report["checks"].append({"name": name, "pass": bool(ok), "detail": str(detail)})
    print(("PASS " if ok else "FAIL ") + name + (" :: " + str(detail) if detail else ""), flush=True)

def curve_data(p, a, b):
    sq = {}
    for y in range(p): sq[(y*y) % p] = y
    L = 0; z = 0; ys = {}
    for xx in range(p):
        v = (xx**3 + a*xx + b) % p
        if v == 0: z += 1; L += 1; ys[xx] = 0
        elif v in sq: L += 1; ys[xx] = sq[v]
    return L, z, ys

def addp(P1, P2, p, a):
    if P1 is None: return P2
    if P2 is None: return P1
    x1, y1 = P1; x2, y2 = P2
    if x1 == x2:
        if (y1 + y2) % p == 0: return None
        lam = ((3*x1*x1 + a) * pow(2*y1, -1, p)) % p
    else:
        lam = ((y2 - y1) * pow((x2 - x1) % p, -1, p)) % p
    x3 = (lam*lam - x1 - x2) % p
    return (x3, (lam*(x1 - x3) - y1) % p)

def neg(P, p):
    return (P[0], (-P[1]) % p)

def mulp(k, P, p, a):
    R = None; Q = P
    while k:
        if k & 1: R = addp(R, Q, p, a)
        Q = addp(Q, Q, p, a); k >>= 1
    return R

def xsum_xdiff(x1, y1, x2, y2, p):
    inv = pow((x2 - x1) % p, -1, p)
    lam1 = ((y2 - y1) * inv) % p
    lam2 = ((-y2 - y1) * inv) % p
    return (lam1*lam1 - x1 - x2) % p, (lam2*lam2 - x1 - x2) % p

def t3_of_xset(xs, ys, p, klein_xs):
    xs = sorted(xs); Fset = set(xs); total = 0
    for i in range(len(xs)):
        x1 = xs[i]; y1 = ys[x1]
        for j in range(i+1, len(xs)):
            x2 = xs[j]; y2 = ys[x2]
            xa, xb = xsum_xdiff(x1, y1, x2, y2, p)
            if xa in Fset and xa != x1 and xa != x2: total += 1
            if xb in Fset and xb != x1 and xb != x2 and xb != xa: total += 1
    assert total % 3 == 0
    adj = 1 if (klein_xs and all(k in Fset for k in klein_xs)) else 0
    return 2 * total // 3 - adj

def profile_pipeline(p, a, F_xs, ys, klein_xs, label):
    """Full chord-profile analysis of one factor base. Returns dict of measurements."""
    B = len(F_xs); Fset = set(F_xs)
    z_F = sum(1 for x in F_xs if ys[x] == 0)
    pts = []
    for x in F_xs:
        if ys[x] == 0: pts.append((x, 0))
        else:
            pts.append((x, ys[x])); pts.append((x, p - ys[x]))
    M = len(pts)
    assert M == 2*B - z_F
    Pset = set(pts)
    Aprime = {}; r = {}
    for P in pts:
        for Q in pts:
            if P == Q: continue
            R = addp(P, Q, p, a)
            if R is None: continue
            Aprime[R] = Aprime.get(R, 0) + 1
            r[R[0]] = r.get(R[0], 0) + 1
    T = sum(r.values())
    T_expect = M*(M-1) - 2*(B - z_F)
    check(f"T-formula {label}", T == T_expect, f"T={T} expected {T_expect}")
    L = len(ys)
    T3 = t3_of_xset(F_xs, ys, p, klein_xs)
    # tangent-degenerate unordered pairs {P, -2P}, 3P != O
    tang = set()
    for P in pts:
        R2 = addp(P, P, p, a)
        if R2 is None: continue
        Q = neg(R2, p)
        if Q == P or Q not in Pset: continue
        tang.add(frozenset((P, Q)))
    d = len(tang)
    S = sum(r.get(x, 0) for x in F_xs)
    check(f"S-identity {label}", S == 6*T3 + 2*d, f"S={S} 6T3+2d={6*T3+2*d} (T3={T3}, d={d})")
    N2 = sum(v*v for v in r.values())
    E1 = sum(v*v for v in Aprime.values())
    tors2 = [g for g in Aprime if g[1] == 0]
    tors_corr = sum(Aprime[g]**2 for g in tors2)
    check(f"N2=2E1-tors {label}", N2 == 2*E1 - tors_corr,
          f"N2={N2} 2E1-tors_corr={2*E1-tors_corr} (2-torsion correction {tors_corr})")
    rbar = Fraction(int(T), int(L))
    mu_tilde = Fraction(int(B*T), int(6*L)) - Fr(int(d), 3)
    dev = Fr(T3) - mu_tilde
    sumFdelta = Fr(S) - B*rbar
    check(f"profile-identity {label}", 6*dev == sumFdelta, f"6dev={6*dev} sumFdelta={sumFdelta}")
    N2t = Fr(int(N2)) - Fraction(int(T*T), int(L))
    check(f"N2tilde>=0 {label}", N2t >= 0, f"N2tilde={float(N2t):.2f}")
    cert = sqrt(float(B * N2t)) / 6.0
    check(f"certificate {label}", abs(float(dev)) <= cert + 1e-9,
          f"|dev|={abs(float(dev)):.4f} cert={cert:.4f} ratio={abs(float(dev))/cert if cert>0 else 0:.4f}")
    delta4 = sum((Fraction(int(r.get(x, 0))) - rbar)**4 for x in ys.keys())
    m4l = Fraction(int(M**4), int(L))
    res = {"label": label, "p": p, "B": B, "M": M, "z_F": z_F, "T3": T3, "d": d, "S": S,
           "mu_tilde": float(mu_tilde), "dev": float(dev), "cert": cert,
           "tightness": abs(float(dev))/cert if cert > 0 else None,
           "N2": N2, "N2tilde": float(N2t), "N2tilde_over_M2": float(N2t)/M**2,
           "delta4_over_M4L": float(delta4/m4l) if m4l else None,
           "weil_bound": M*sqrt(p*B)/3.0, "cert_vs_weil": cert/(M*sqrt(p*B)/3.0)}
    return res, pts, r, Aprime

def char_sums(p, pts_r_xs, N2, T, M):
    """U(psi_k) = sum over counted pair-sums exp(-2 pi i k x / p); numpy, chunked."""
    xs = np.array(pts_r_xs, dtype=np.int64)
    sumU2 = 0.0; sumU4 = 0.0; maxU = 0.0; U0 = None
    for k0 in range(0, p, 512):
        ks = np.arange(k0, min(k0+512, p), dtype=np.int64)
        E = np.exp(-2j*np.pi*(ks[:, None]*xs[None, :] % p)/p)
        U = E.sum(axis=1); a = np.abs(U)**2
        if k0 == 0:
            U0 = a[0]; a[0] = 0.0
        sumU2 += float(a.sum()); sumU4 += float((a*a).sum())
        maxU = max(maxU, float(np.sqrt(a.max())))
    return {"sumU2_ne0": sumU2, "sumU4_ne0": sumU4, "maxU_ne0": maxU, "U0_sq": U0}

import sys; report["env"]["python_version"] = sys.version
report["env"]["numpy_version"] = np.__version__

for p in sorted(CURVES):
    a, b, n_rec = CURVES[p]
    L, z, ys = curve_data(p, a, b)
    n = 1 + 2*L - z
    check(f"curve-order p={p}", n == n_rec,
          f"n={n} from x-table identity (matches THM1 sage-verified rebuild {n_rec})")
    klein_xs = sorted(x for x in ys if ys[x] == 0) if z == 3 else None
    xs_all = sorted(ys.keys())

    # ---- uniform-x cells ----
    for (cp, B) in [c for c in UNI_CELLS if c[0] == p]:
        for seed in UNI_SEEDS:
            rng = random.Random(f"incbarrier2-{seed}-{p}-{B}")
            F_xs = sorted(rng.sample(xs_all, B))
            label = f"p={p},B={B},s={seed}"
            res, pts, r, Aprime = profile_pipeline(p, a, F_xs, ys, klein_xs, label)
            report["instances"].append(res)
            if (p, B, seed) in CHAR_INSTANCES:
                T = sum(r.values())
                rxs = []
                for x, v in r.items(): rxs += [x]*v
                ch = char_sums(p, rxs, N2=res["N2"], T=T, M=res["M"])
                ch["p"] = p; ch["B"] = B; ch["seed"] = seed
                check(f"parseval2 {label}", abs(ch["sumU2_ne0"] - (p*res["N2"] - T*T)) <= 1e-4*(p*res["N2"]),
                      f"sum|U|^2(ne0)={ch['sumU2_ne0']:.1f} vs pN2-T^2={p*res['N2']-T*T}")
                lb2 = Fraction(int(T*T*(p-L)), int(L))
                check(f"U2-lower-bound {label}", ch["sumU2_ne0"] >= float(lb2)*(1-1e-6),
                      f"sum|U|^2={ch['sumU2_ne0']:.1f} >= T^2(p-L)/L={float(lb2):.1f}")
                lbmax = sqrt(float(p*res["N2"] - T*T)/(p-1))
                check(f"maxU-lower-bound {label}", ch["maxU_ne0"] >= lbmax*(1-1e-6),
                      f"max|U|={ch['maxU_ne0']:.1f} >= {lbmax:.1f}; Weil scale 2M*sqrt(p)={2*res['M']*sqrt(p):.1f}")
                # fourth moment: exact x-multiset energy via numpy
                xs = np.array(rxs, dtype=np.int64)
                conv = np.bincount((xs[:, None]+xs[None, :]).ravel() % p, minlength=p)
                Ex = int((conv.astype(np.int64)**2).sum())
                check(f"parseval4 {label}", abs(ch["sumU4_ne0"] - (p*Ex - T**4)) <= 1e-4*p*Ex,
                      f"sum|U|^4(ne0)={ch['sumU4_ne0']:.1f} vs pEx-T^4={p*Ex-T**4}")
                lb4 = float(p*res["N2"] - T*T)**2/(p-1)
                check(f"U4-lower-bound {label}", ch["sumU4_ne0"] >= lb4*(1-1e-6),
                      f"sum|U|^4={ch['sumU4_ne0']:.1f} >= (sum|U|^2)^2/(p-1)={lb4:.1f}")
                ch["Ex"] = Ex; ch["Ex_diag2"] = 2*res["M"]**2  # diagonal scale k! M^{2k}, k=2 -> 2M^4? recorded raw
                report["char"].append(ch)

    # ---- AP cells ----
    # find a point of order > 3B+3 by scanning a bounded set of points
    best = {}
    for (cp, B) in [c for c in AP_CELLS if c[0] == p]:
        if B in best: continue
        P0 = None; ord0 = 0
        tried = 0
        for x in xs_all:
            if ys[x] == 0: continue
            for P in [(x, ys[x]), (x, p-ys[x])]:
                o = 1; R = P
                while R is not None and o <= n:
                    R = addp(R, P, p, a); o += 1
                o -= 1
                tried += 1
                if o > ord0: ord0 = o; P0 = P
            if tried > 400: break
        best[B] = (P0, ord0)
    for (cp, B) in [c for c in AP_CELLS if c[0] == p]:
        P0, ord0 = best[B]
        check(f"AP-order p={p},B={B}", 3*B < ord0, f"ord={ord0} need > {3*B}")
        F_ap = sorted({mulp(i, P0, p, a)[0] for i in range(1, B+1)})
        check(f"AP-distinct p={p},B={B}", len(F_ap) == B, f"|F|={len(F_ap)}")
        res, pts, r, Aprime = profile_pipeline(p, a, F_ap, ys, klein_xs, f"p={p},B={B},AP")
        t3_expect = 2*((B-1)**2 // 4)
        check(f"AP-T3-closed p={p},B={B}", res["T3"] == t3_expect, f"T3={res['T3']} formula {t3_expect}")
        res["ord0"] = ord0
        res["N2tilde_over_M3"] = res["N2tilde"]/res["M"]**3
        report["ap"].append(res)

n_fail = sum(1 for c in report["checks"] if not c["pass"])
report["summary"] = {"checks": len(report["checks"]), "failures": n_fail}
with open(OUT, "w") as f:
    json.dump(report, f, indent=1)
print(f"WROTE {OUT}: {len(report['checks'])} checks, {n_fail} failures", flush=True)
