# EXP-JETB-001 -- D1: Generic-model barrier for jet-augmented relation channels.
# Toy certification per frozen specification.yaml:
#   primes {101,211,431}, seeds 20260717..20260722, fresh ordinary prime-field curves,
#   x-interval factor bases, m=2 target variety S_R(x1,x2)=S3(x1,x2,x_R) and
#   m=3 variety S3(x1,x2,x3).
# Screens under test (A1's tangent screen, implemented two independent ways):
#   ScreenX (x-only Semaev jet): pass iff S(x)=0 AND the homogeneous eps-system
#     grad S(x).t = 0 is consistent (kernel computed by exact linear algebra).
#   ScreenC (dual-number addition chain, m=2): pass iff P1+P2 = R over F_p[eps]/eps^2
#     for some tangent lift; for true chain relations a concrete lift witness is
#     constructed and verified by direct dual-number EC arithmetic.
# Simulable-model predictions P1..P7 (see specification.yaml): screen == zeroth-order
#   exactly, sigma_true = 1, leakage = 0, sigma_pass/p_m = 1, eps-solution space =
#   ker grad S of dimension (#vars)-1 (smooth) / #vars (singular), formal-group
#   linearity exact, one-step jet-linear (Newton) solve hit rate ~ 0 (<= 2/p).
# Controls: positive -- S-evaluation reproduces point-arithmetic truth on every
#   tuple + constructed relations pass Z and screen; negative -- no leakage among
#   non-relations (FB tuples, plus 200 uniform random pairs per instance).
# Output: single JSON document on stdout; progress on stderr. Deterministic: all RNG
#   via set_random_seed(seed) per (p,seed) instance.
import time, json, sys

def nowz():
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())

T0 = time.time()
STARTED = nowz()
try:
    from sage.misc.banner import version as _sv
    SAGE_VERSION = str(_sv())
except Exception:
    SAGE_VERSION = None

PRIMES = [101, 211, 431]
SEEDS = [20260717, 20260718, 20260719, 20260720, 20260721, 20260722]
NEWTON_STARTS = 100
NEWTON_CAP = 50
FG_PROBES = 100
RAND_NEG_PAIRS = 200

def S3poly(X1, X2, X3, A, B):
    return ((X1-X2)**2 * X3**2 - 2*((X1+X2)*(X1*X2+A) + 2*B)*X3
            + ((X1*X2-A)**2 - 4*B*(X1+X2)))

# ---- dual-number arithmetic: pair (c0, c1) = c0 + eps*c1 over F, eps^2 = 0 ----
def du(u, v): return (u[0]+v[0], u[1]+v[1])
def ds(u, v): return (u[0]-v[0], u[1]-v[1])
def dm(u, v): return (u[0]*v[0], u[0]*v[1] + u[1]*v[0])
def ddiv(u, v):
    return (u[0]/v[0], (u[1]*v[0] - u[0]*v[1])/(v[0]**2))

def S3_dual(x1d, x2d, x3d, Ad, Bd, F):
    two = (F(2), F(0)); four = (F(4), F(0))
    dx = ds(x1d, x2d)
    term1 = dm(dm(dx, dx), dm(x3d, x3d))
    inner = du(dm(du(x1d, x2d), du(dm(x1d, x2d), Ad)), dm(two, Bd))
    term2 = dm(two, dm(inner, x3d))
    q = ds(dm(x1d, x2d), Ad)
    term3 = dm(q, q)
    term4 = dm(four, dm(Bd, du(x1d, x2d)))
    return du(ds(term1, term2), ds(term3, term4))

def gen_curve(p, seed):
    F = GF(p)
    set_random_seed(seed)
    trials = 0
    while trials < 500:
        trials += 1
        A = F(randint(0, p-1)); Bv = F(randint(0, p-1))
        if 4*A**3 + 27*Bv**2 == 0:
            continue
        E = EllipticCurve(F, [A, Bv])
        N = int(E.order())
        tr = p + 1 - N
        if tr == 0:      # supersingular -- excluded
            continue
        if N == p:       # anomalous -- excluded
            continue
        ell = int(max(q for q, e in factor(N)))
        if ell*ell < N:  # require prime-order subgroup of size >= sqrt(N)
            continue
        return E, A, Bv, N, tr, ell, N//ell, trials
    return None

def make_fb(E, Bt):
    F = E.base_field(); p = int(F.characteristic())
    FB = []
    for xv in range(p):
        if len(FB) >= Bt: break
        try:
            pts = E.lift_x(F(xv), all=True)
        except Exception:
            continue
        if not pts: continue
        P = min(pts, key=lambda Q: int(Q.xy()[1]))   # deterministic min-y lift
        if P.is_zero(): continue
        FB.append((F(xv), P))
    return FB

def kernel_dim_witness(F, grads):
    A = matrix(F, [grads])
    K = A.right_kernel()
    dim = int(K.dimension())
    t = None
    if dim >= 1:
        t = tuple(K.basis()[0])
    return dim, t

def fg_probe(E, A, Bv, count):
    # Formal-group linearity: with lifts P~ = (x+eps*a, y+eps*lam*a), lam = dy/dx,
    # the omega-scalar (invariant differential omega = dx/(2y)) of a tangent vector
    # (a, lam*a) at (x,y) is a/(2y). Addition of dual-number points has first-order
    # part U with omega(U) = omega(V) + omega(W); at y=0 (vertical tangent) use the
    # equivalent contraction omega = dy/(3x^2+A), which forces dx-part = 0.
    F = E.base_field(); p = int(F.characteristic())
    r = {"tested": 0, "base_fail": 0, "lin_fail": 0, "swap_fail": 0, "skipped": 0}
    for _ in range(count):
        P = E.random_point(); Q = E.random_point()
        if P.is_zero() or Q.is_zero(): r["skipped"] += 1; continue
        x1, y1 = P.xy(); x2, y2 = Q.xy()
        if y1 == 0 or y2 == 0 or x1 == x2: r["skipped"] += 1; continue
        R3 = P + Q
        if R3.is_zero(): r["skipped"] += 1; continue
        x3, y3 = R3.xy()
        a = F(randint(0, p-1)); b = F(randint(0, p-1))
        lam1 = (3*x1**2 + A)/(2*y1); lam2 = (3*x2**2 + A)/(2*y2)
        s = a/(2*y1) + b/(2*y2)                    # sum of omega-scalars
        Pt = ((x1, a), (y1, lam1*a)); Qt = ((x2, b), (y2, lam2*b))
        lamt = ddiv(ds(Qt[1], Pt[1]), ds(Qt[0], Pt[0]))
        x3t = ds(ds(dm(lamt, lamt), Pt[0]), Qt[0])
        y3t = ds(dm(lamt, ds(Pt[0], x3t)), Pt[1])
        r["tested"] += 1
        if not (x3t[0] == x3 and y3t[0] == y3):
            r["base_fail"] += 1
        if y3 != 0:
            c3 = 2*y3*s
            lin_ok = (x3t[1] == c3) and (y3t[1] == ((3*x3**2 + A)/(2*y3))*c3)
        else:
            lin_ok = (x3t[1] == 0) and (y3t[1] == (3*x3**2 + A)*s)
        if not lin_ok:
            r["lin_fail"] += 1
        # swap-invariance: any (a',b') with the same omega-scalar sum must give
        # the identical dual-number sum
        a2 = F(randint(0, p-1)); b2 = 2*y2*(s - a2/(2*y1))
        Pt2 = ((x1, a2), (y1, lam1*a2)); Qt2 = ((x2, b2), (y2, lam2*b2))
        lamt2 = ddiv(ds(Qt2[1], Pt2[1]), ds(Qt2[0], Pt2[0]))
        x3t2 = ds(ds(dm(lamt2, lamt2), Pt2[0]), Qt2[0])
        y3t2 = ds(dm(lamt2, ds(Pt2[0], x3t2)), Pt2[1])
        if not (x3t2 == x3t and y3t2 == y3t):
            r["swap_fail"] += 1
    return r

def instance(p, seed, do_exhaustive):
    t_inst = time.time()
    F = GF(p)
    g = gen_curve(p, seed)
    if g is None:
        return {"p": p, "seed": seed, "error": "no_in_family_curve_in_500_trials"}
    E, A, Bv, N, tr, ell, cof, trials = g
    # target R in the prime-order (ell) subgroup
    G = None
    while G is None:
        cand = cof * E.random_point()
        if not cand.is_zero(): G = cand
    R = randint(1, ell-1) * G
    xRv = R.xy()[0]
    Bt = max(8, int(ceil(sqrt(2*p))))
    FB = make_fb(E, Bt)
    FBx = [u[0] for u in FB]; FBP = [u[1] for u in FB]
    FBx_set = set(FBx)
    nFB = len(FB)
    PR2 = PolynomialRing(F, names='x1,x2'); x1, x2 = PR2.gens()
    SR = S3poly(x1, x2, xRv, A, Bv)
    gSR1 = SR.derivative(x1); gSR2 = SR.derivative(x2)
    PR3 = PolynomialRing(F, names='y1,y2,y3'); y1, y2, y3 = PR3.gens()
    S3 = S3poly(y1, y2, y3, A, Bv)
    gS = [S3.derivative(y1), S3.derivative(y2), S3.derivative(y3)]
    Ad = (A, F(0)); Bd = (Bv, F(0)); xRd = (xRv, F(0))

    def base_truth2(i, j):
        P1, P2 = FBP[i], FBP[j]
        S = P1 + P2
        if not S.is_zero() and S.xy()[0] == xRv: return True
        D = P1 - P2
        if not D.is_zero() and D.xy()[0] == xRv: return True
        return False

    def base_truth3(i, j, k):
        P1, P2 = FBP[i], FBP[j]; x3v = FBx[k]
        S = P1 + P2
        if not S.is_zero() and S.xy()[0] == x3v: return True
        D = P1 - P2
        if not D.is_zero() and D.xy()[0] == x3v: return True
        return False

    m2 = {"n_tuples": 0, "n_true": 0, "n_screen_pass": 0, "n_screen_true_pass": 0,
          "n_leak": 0, "n_agree": 0, "zt_mismatch": 0, "zb_mismatch": 0,
          "n_singular_true": 0, "eps_dim_hist": {}, "witness_fail": 0,
          "grad_dot_fail": 0, "chain_true": 0, "chain_true_witness_fail": 0,
          "chain_true_witness_skip": 0, "true_pairs": []}
    for i in range(nFB):
        for j in range(i, nFB):
            a, b = FBx[i], FBx[j]
            c0 = SR(a, b)
            Z = (c0 == 0)
            g1, g2 = gSR1(a, b), gSR2(a, b)
            dim, t = kernel_dim_witness(F, [g1, g2])
            consistent = (dim >= 1)          # homogeneous system; measured, not assumed
            screen = Z and consistent
            bt = base_truth2(i, j)
            m2["n_tuples"] += 1
            if Z: m2["n_true"] += 1
            if screen: m2["n_screen_pass"] += 1
            if Z and screen: m2["n_screen_true_pass"] += 1
            if screen and not Z: m2["n_leak"] += 1
            if screen == Z: m2["n_agree"] += 1
            else: m2["zt_mismatch"] += 1
            if Z != bt: m2["zb_mismatch"] += 1
            if Z:
                if g1 == 0 and g2 == 0: m2["n_singular_true"] += 1
                m2["eps_dim_hist"][str(dim)] = m2["eps_dim_hist"].get(str(dim), 0) + 1
                if t is not None:
                    if g1*t[0] + g2*t[1] != 0: m2["grad_dot_fail"] += 1
                    w = S3_dual((a, t[0]), (b, t[1]), xRd, Ad, Bd, F)
                    if w != (F(0), F(0)): m2["witness_fail"] += 1
                if len(m2["true_pairs"]) < NEWTON_CAP:
                    m2["true_pairs"].append((a, b))
            # ScreenC: dual-number addition chain with fixed (+,+) sign choice
            ch = (not (FBP[i]+FBP[j]).is_zero()) and ((FBP[i]+FBP[j]).xy()[0] == xRv) \
                 and (FBP[i]+FBP[j] == R)
            if ch:
                m2["chain_true"] += 1
                # constructive tangent-lift witness: random t1,t2; first-order part
                # must equal the omega-scalar sum w = t1/(2*ya) + t2/(2*yb)
                P1, P2 = FBP[i], FBP[j]
                xa, ya = P1.xy(); xb, yb = P2.xy()
                if ya != 0 and yb != 0 and xa != xb and R.xy()[1] != 0:
                    t1 = F(randint(0, p-1)); t2 = F(randint(0, p-1))
                    la = (3*xa**2 + A)/(2*ya); lb = (3*xb**2 + A)/(2*yb)
                    w = t1/(2*ya) + t2/(2*yb)
                    Pt = ((xa, t1), (ya, la*t1)); Qt = ((xb, t2), (yb, lb*t2))
                    lt = ddiv(ds(Qt[1], Pt[1]), ds(Qt[0], Pt[0]))
                    xs = ds(ds(dm(lt, lt), Pt[0]), Qt[0])
                    ys = ds(dm(lt, ds(Pt[0], xs)), Pt[1])
                    yRv = R.xy()[1]
                    lc = (3*xRv**2 + A)/(2*yRv)
                    c3 = 2*yRv*w
                    ok = (xs[0] == xRv and ys[0] == yRv
                          and xs[1] == c3 and ys[1] == lc*c3)
                    if not ok: m2["chain_true_witness_fail"] += 1
                else:
                    m2["chain_true_witness_skip"] += 1

    # Newton (one-step jet-linear solve) probe on true m=2 relations.
    # Regime split: S_R(x1,z) = (x_R - x_1)^2 z^2 + ... is LINEAR when x1 == x_R
    # (degree-drop fiber, zeroth-order observable); one Newton step then solves it
    # from every start. Non-degenerate fibers: exact hit rate 2/p (the 2 root-starts).
    nw = {"relations_used": len(m2["true_pairs"]), "starts": 0, "hits": 0,
          "deriv0_skips": 0,
          "nondegenerate": {"relations": 0, "starts": 0, "hits": 0},
          "degenerate_x1_eq_xR": {"relations": 0, "starts": 0, "hits": 0}}
    for (a, b) in m2["true_pairs"]:
        deg = (a == xRv)
        bucket = nw["degenerate_x1_eq_xR"] if deg else nw["nondegenerate"]
        bucket["relations"] += 1
        for _ in range(NEWTON_STARTS):
            x20 = F(randint(0, p-1))
            f = SR(a, x20); d = gSR2(a, x20)
            if d == 0:
                nw["deriv0_skips"] += 1; continue
            x2h = x20 - f/d
            nw["starts"] += 1
            bucket["starts"] += 1
            if SR(a, x2h) == 0:
                nw["hits"] += 1
                bucket["hits"] += 1
    m2["newton"] = nw
    m2["true_pairs"] = len(m2["true_pairs"])   # store count only

    # m=3 battery (P1..P5)
    m3 = {"n_tuples": 0, "n_true": 0, "n_screen_pass": 0, "n_screen_true_pass": 0,
          "n_leak": 0, "n_agree": 0, "zt_mismatch": 0, "zb_mismatch": 0,
          "n_singular_true": 0, "eps_dim_hist": {}, "witness_fail": 0,
          "grad_dot_fail": 0}
    for i in range(nFB):
        for j in range(i, nFB):
            for k in range(j, nFB):
                a, b, c = FBx[i], FBx[j], FBx[k]
                c0 = S3(a, b, c)
                Z = (c0 == 0)
                gs = [gS[0](a, b, c), gS[1](a, b, c), gS[2](a, b, c)]
                dim, t = kernel_dim_witness(F, gs)
                screen = Z and (dim >= 1)
                bt = base_truth3(i, j, k)
                m3["n_tuples"] += 1
                if Z: m3["n_true"] += 1
                if screen: m3["n_screen_pass"] += 1
                if Z and screen: m3["n_screen_true_pass"] += 1
                if screen and not Z: m3["n_leak"] += 1
                if screen == Z: m3["n_agree"] += 1
                else: m3["zt_mismatch"] += 1
                if Z != bt: m3["zb_mismatch"] += 1
                if Z:
                    if gs[0] == 0 and gs[1] == 0 and gs[2] == 0:
                        m3["n_singular_true"] += 1
                    m3["eps_dim_hist"][str(dim)] = m3["eps_dim_hist"].get(str(dim), 0) + 1
                    if t is not None:
                        if sum(gs[u]*t[u] for u in range(3)) != 0:
                            m3["grad_dot_fail"] += 1
                        w = S3_dual((a, t[0]), (b, t[1]), (c, t[2]), Ad, Bd, F)
                        if w != (F(0), F(0)): m3["witness_fail"] += 1

    # constructed-relations control (P2 = R - P1 with x in FB)
    cc = {"found": 0, "z_pass": 0, "screen_pass": 0, "witness_fail": 0}
    for i in range(nFB):
        P2c = R - FBP[i]
        if P2c.is_zero(): continue
        x2c = P2c.xy()[0]
        if x2c not in FBx_set: continue
        cc["found"] += 1
        a, b = FBx[i], x2c
        c0 = SR(a, b)
        g1, g2 = gSR1(a, b), gSR2(a, b)
        dim, t = kernel_dim_witness(F, [g1, g2])
        if c0 == 0: cc["z_pass"] += 1
        if c0 == 0 and dim >= 1:
            cc["screen_pass"] += 1
            if t is not None:
                w = S3_dual((a, t[0]), (b, t[1]), xRd, Ad, Bd, F)
                if w != (F(0), F(0)): cc["witness_fail"] += 1

    # random non-relation negative control (uniform pairs over F_p^2)
    rn = {"n": 0, "z_true": 0, "leak": 0, "dual_repair_fail_expected": 0}
    for _ in range(RAND_NEG_PAIRS):
        a = F(randint(0, p-1)); b = F(randint(0, p-1))
        c0 = SR(a, b)
        Z = (c0 == 0)
        rn["n"] += 1
        if Z:
            rn["z_true"] += 1; continue
        t1 = F(randint(0, p-1)); t2 = F(randint(0, p-1))
        w = S3_dual((a, t1), (b, t2), xRd, Ad, Bd, F)
        if w[0] == 0:   # eps-repair of a zeroth-order failure would be leakage
            rn["leak"] += 1

    fg = fg_probe(E, A, Bv, FG_PROBES)

    row = {"p": p, "seed": seed,
           "curve": {"A": int(A), "B": int(Bv), "N": N, "trace": tr,
                     "ell": ell, "cofactor": cof, "search_trials": trials},
           "R": {"x": int(xRv), "in_prime_subgroup": True},
           "B_target": Bt, "n_fb": nFB,
           "m2": m2, "m3": m3, "constructed": cc, "random_negative": rn, "fg": fg,
           "elapsed_seconds": float(time.time() - t_inst)}

    if do_exhaustive:
        lift = {}
        for xv in range(p):
            try:
                pts = E.lift_x(F(xv), all=True)
            except Exception:
                continue
            if pts:
                lift[F(xv)] = min(pts, key=lambda Q: int(Q.xy()[1]))
        ex = {"n_pairs": 0, "n_true": 0, "zt_mismatch": 0, "zb_checked": 0,
              "zb_mismatch": 0, "n_singular_true": 0, "eps_dim_hist": {}}
        for av in range(p):
            for bv in range(p):
                a, b = F(av), F(bv)
                c0 = SR(a, b)
                Z = (c0 == 0)
                g1, g2 = gSR1(a, b), gSR2(a, b)
                dim, t = kernel_dim_witness(F, [g1, g2])
                screen = Z and (dim >= 1)
                ex["n_pairs"] += 1
                if Z:
                    ex["n_true"] += 1
                    if g1 == 0 and g2 == 0: ex["n_singular_true"] += 1
                    ex["eps_dim_hist"][str(dim)] = ex["eps_dim_hist"].get(str(dim), 0) + 1
                if screen != Z: ex["zt_mismatch"] += 1
                if a in lift and b in lift:
                    P1, P2 = lift[a], lift[b]
                    bt = False
                    S = P1 + P2
                    if not S.is_zero() and S.xy()[0] == xRv: bt = True
                    D = P1 - P2
                    if not D.is_zero() and D.xy()[0] == xRv: bt = True
                    ex["zb_checked"] += 1
                    if Z != bt: ex["zb_mismatch"] += 1
        row["exhaustive"] = ex

    print(f"p={p} seed={seed} N={N} ell={ell} nFB={nFB} "
          f"m2[true={m2['n_true']}/{m2['n_tuples']} zt_mm={m2['zt_mismatch']} "
          f"zb_mm={m2['zb_mismatch']} leak={m2['n_leak']} sing={m2['n_singular_true']}] "
          f"m3[true={m3['n_true']}/{m3['n_tuples']} zt_mm={m3['zt_mismatch']} "
          f"zb_mm={m3['zb_mismatch']}] newton[hits={nw['hits']}/{nw['starts']}] "
          f"fg[tested={fg['tested']} lin_fail={fg['lin_fail']}]", file=sys.stderr, flush=True)
    return row

def rate(a, b):
    return (float(a)/float(b)) if b else None

rows = []
for p in PRIMES:
    for s in SEEDS:
        rows.append(instance(p, s, do_exhaustive=(p == PRIMES[0] and s == SEEDS[0])))

# ---- aggregation per prime ----
per_prime = []
for p in PRIMES:
    rs = [r for r in rows if r["p"] == p and "error" not in r]
    agg = {"p": p, "n_seeds": len(rs)}
    for tag in ["m2", "m3"]:
        nt = sum(r[tag]["n_tuples"] for r in rs)
        ntrue = sum(r[tag]["n_true"] for r in rs)
        npass = sum(r[tag]["n_screen_pass"] for r in rs)
        ntp = sum(r[tag]["n_screen_true_pass"] for r in rs)
        nleak = sum(r[tag]["n_leak"] for r in rs)
        nagree = sum(r[tag]["n_agree"] for r in rs)
        agg[tag] = {
            "tuples_total": nt, "true_total": ntrue,
            "p_m": rate(ntrue, nt),
            "sigma_pass": rate(npass, nt),
            "sigma_true": rate(ntp, ntrue),
            "leakage": rate(nleak, nt - ntrue),
            "agreement_ZT": rate(nagree, nt),
            "sigma_pass_over_pm": rate(npass, ntrue),
            "zt_mismatches": sum(r[tag]["zt_mismatch"] for r in rs),
            "zb_mismatches": sum(r[tag]["zb_mismatch"] for r in rs),
            "singular_true": sum(r[tag]["n_singular_true"] for r in rs),
            "witness_fail": sum(r[tag]["witness_fail"] for r in rs),
            "grad_dot_fail": sum(r[tag]["grad_dot_fail"] for r in rs),
            "eps_dim_hist": {d: sum(int(r[tag]["eps_dim_hist"].get(d, 0)) for r in rs)
                             for d in ["1", "2", "3"]},
        }
    nwj = [r["m2"]["newton"] for r in rs]
    hits = sum(w["hits"] for w in nwj); starts = sum(w["starts"] for w in nwj)
    nd_h = sum(w["nondegenerate"]["hits"] for w in nwj)
    nd_s = sum(w["nondegenerate"]["starts"] for w in nwj)
    dg_h = sum(w["degenerate_x1_eq_xR"]["hits"] for w in nwj)
    dg_s = sum(w["degenerate_x1_eq_xR"]["starts"] for w in nwj)
    agg["newton"] = {"starts": starts, "hits": hits,
                     "sigma_solve": rate(hits, starts),
                     "bound_2_over_p": rate(2, p),
                     "deriv0_skips": sum(w["deriv0_skips"] for w in nwj),
                     "nondegenerate": {"relations": sum(w["nondegenerate"]["relations"] for w in nwj),
                                       "starts": nd_s, "hits": nd_h,
                                       "sigma_solve": rate(nd_h, nd_s),
                                       "expected_2_over_p": rate(2, p)},
                     "degenerate_x1_eq_xR": {"relations": sum(w["degenerate_x1_eq_xR"]["relations"] for w in nwj),
                                             "starts": dg_s, "hits": dg_h,
                                             "sigma_solve": rate(dg_h, dg_s),
                                             "expected": 1.0,
                                             "mechanism": "S_R(x1,z) drops to degree 1 when x1 == x_R (z^2 coefficient (x_R-x_1)^2 vanishes); one Newton step solves a linear equation exactly; degree-drop is zeroth-order observable"}}
    agg["chain"] = {"chain_true": sum(r["m2"]["chain_true"] for r in rs),
                    "witness_fail": sum(r["m2"]["chain_true_witness_fail"] for r in rs),
                    "witness_skip": sum(r["m2"]["chain_true_witness_skip"] for r in rs)}
    agg["fg"] = {k: sum(r["fg"][k] for r in rs)
                 for k in ["tested", "base_fail", "lin_fail", "swap_fail", "skipped"]}
    agg["constructed"] = {k: sum(r["constructed"][k] for r in rs)
                          for k in ["found", "z_pass", "screen_pass", "witness_fail"]}
    agg["random_negative"] = {k: sum(r["random_negative"][k] for r in rs)
                              for k in ["n", "z_true", "leak"]}
    per_prime.append(agg)

FINISHED = nowz()
out = {
    "experiment_id": "EXP-JETB-001", "run_id": "RUN-JETB-001-a",
    "script": "experiments/EXP-JETB-001/jetbarrier1_model_check.sage",
    "sage_version": SAGE_VERSION,
    "started_at": STARTED, "finished_at": FINISHED,
    "wall_seconds": float(time.time() - T0),
    "parameters": {"primes": PRIMES, "seeds": SEEDS,
                   "B_rule": "max(8, ceil(sqrt(2*p)))",
                   "fb": "x-interval, one min-y lift per x",
                   "varieties": {"m2": "S_R(x1,x2)=S3(x1,x2,x_R)",
                                 "m3": "S3(x1,x2,x3)"},
                   "newton": {"starts_per_relation": NEWTON_STARTS, "cap": NEWTON_CAP},
                   "fg_probes": FG_PROBES, "random_negative_pairs": RAND_NEG_PAIRS},
    "rows": rows,
    "per_prime_summary": per_prime,
}
print(json.dumps(out, default=lambda o: int(o)))
