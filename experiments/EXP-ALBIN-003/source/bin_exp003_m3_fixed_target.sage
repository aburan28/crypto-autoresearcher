# BIN-EXP-003 : m=3 solving-degree discriminator with a KNOWN-DECOMPOSABLE target.
#
# Fixes the two BIN-EXP-002 flaws: (1) m=3 (first non-degenerate arity; m=2 linearizes
# at deg 2 and cannot show the FPPR effect); (2) target R = P1+P2+P3 with x(Pi) in V is
# GUARANTEED to decompose, so the genuine descended system is consistent and the
# genuine-vs-control comparison is meaningful.
#
# Question (the pivotal one per literature_binary_field.md): does the GENUINE binary
# Weil-descent S4 decomposition system solve at a LOWER Groebner degree than a RANDOM
# control with a planted solution, matched on #eqs/#vars/degree profile? FPPR/Petit-
# Quisquater predict genuine << generic; Huang-Kosters-Yeo dispute it. We measure.
#
# Hard per-cell timeout via signal.alarm (the m=3 cell hung in EXP-001). Toy params only.
import json, time, signal
LOGP = "/Volumes/Volume/autolab/experiments/ecdlp_binary_field/bin_exp003_m3_fixed_target.log"
_lf = open(LOGP, "w")
def out(s):
    print(s); _lf.write(str(s) + "\n"); _lf.flush()
out("=== BIN-EXP-003 m=3 fixed-target solving-degree discriminator ===  " + time.asctime())

class Timeout(Exception): pass
def _alarm(sig, frm): raise Timeout()
signal.signal(signal.SIGALRM, _alarm)

def make_curve(n, seed=1):
    set_random_seed(int(seed))
    F = GF(2**n, 'a'); a = F.gen(); best = None
    for _ in range(400):
        a2 = F.random_element(); a6 = F.random_element()
        if a6.is_zero(): continue
        try: E = EllipticCurve(F, [1, a2, 0, 0, a6])
        except Exception: continue
        N = E.order(); big = max(p for p, e in factor(N))
        if best is None or big > best[5]: best = (F, a, E, a2, a6, big, N)
        if big >= N // 2: return F, a, E, a2, a6, N, big
    F, a, E, a2, a6, big, N = best; return F, a, E, a2, a6, N, big

def build_S4(F, a6):
    P = PolynomialRing(F, 'X1,X2,X3,X4,T'); X1, X2, X3, X4, T = P.gens()
    def S3(u, v, w): return (u*v + u*w + v*w)**2 + u*v*w + a6
    S3a = S3(X1, X2, T); S3b = S3(X3, X4, T)
    S4full = S3a.resultant(S3b, T)
    P4 = PolynomialRing(F, 'X1,X2,X3,X4'); g = P4.gens()
    S4 = P4(S4full.subs({X1: g[0], X2: g[1], X3: g[2], X4: g[3], T: 0}))
    try:
        S4 = prod(f for f, e in factor(S4))  # squarefree part
    except Exception:
        pass
    return P4, S4

def verify_S4(E, P4, S4, ntest=20):
    g = P4.gens(); van = tot = nz = ntot = 0; tries = 0
    while tot < ntest and tries < 6000:
        tries += 1
        P1 = E.random_point(); P2 = E.random_point(); P3 = E.random_point()
        P4pt = -(P1 + P2 + P3)
        pts = [P1, P2, P3, P4pt]
        if any(Q.is_zero() for Q in pts): continue
        xs = [Q.xy()[0] for Q in pts]; van += (S4(*xs) == 0); tot += 1
    tries = 0
    while ntot < ntest and tries < 8000:
        tries += 1
        pts = [E.random_point() for _ in range(4)]
        if any(Q.is_zero() for Q in pts): continue
        if sum(pts, E(0)).is_zero(): continue
        xs = [Q.xy()[0] for Q in pts]; nz += (S4(*xs) != 0); ntot += 1
    return van, tot, nz, ntot

def f2_components(Phi, F, n, R2):
    comps = [R2(0)] * n; ngens = R2.ngens()
    for coeff, mono in zip(Phi.coefficients(), Phi.monomials()):
        bits = list(coeff.polynomial().list()); bits += [GF(2)(0)] * (n - len(bits))
        e = mono.exponents()[0]
        m2 = R2.monomial(*[int(e[i]) for i in range(ngens)]) if any(e) else R2(1)
        for k in range(n):
            if bits[k] != 0: comps[k] = comps[k] + m2
    return comps

def gb_info(bpolys, B, var_cap=15):
    I = B.ideal(bpolys); t0 = time.time(); gb = list(I.groebner_basis()); dt = time.time() - t0
    if len(gb) == 1 and gb[0] == B(1):
        return {"maxdeg": 0, "ngb": 1, "consistent": False, "nsols": 0, "secs": round(dt, 2)}
    md = max((g.degree() for g in gb), default=0); nsols = None
    if B.ngens() <= var_cap:
        try: nsols = len(I.variety())
        except Exception: nsols = None
    return {"maxdeg": int(md), "ngb": len(gb), "consistent": True, "nsols": nsols, "secs": round(dt, 2)}

def cell(n, seed=1, tcap=150):
    r = {"n": n, "m": 3}
    signal.alarm(int(tcap))
    try:
        F, a, E, a2, a6, N, big = make_curve(n, seed)
        r["largest_prime"] = int(big); r["rho_log2"] = float(log(0.886 * sqrt(float(big)), 2))
        l = max(2, int(round(n / 3))); m = 3; nvars = m * l; r["l"] = l; r["nvars"] = nvars
        # factor base: points with x(P) in V = span(a^0..a^{l-1})
        w = [a**j for j in range(l)]
        def in_V_coords(beta):
            v = list(beta.polynomial().list()); v += [GF(2)(0)] * (n - len(v))
            return None if any(v[j] != 0 for j in range(l, n)) else [int(v[j]) for j in range(l)]
        fb = []
        for Q in E:
            if Q.is_zero(): continue
            cc = in_V_coords(Q.xy()[0])
            if cc is not None: fb.append((Q, Q.xy()[0], cc))
            if len(fb) >= 40: break
        r["fb_size"] = len(fb)
        if len(fb) < 3:
            r["status"] = "FB<3 (subspace too small for n=%d, l=%d)" % (n, l); signal.alarm(0); return r
        # KNOWN-decomposable target R = P1+P2+P3
        (P1, x1, c1), (P2, x2, c2), (P3, x3, c3) = fb[0], fb[1], fb[2]
        Rt = P1 + P2 + P3
        if Rt.is_zero():
            (P3, x3, c3) = fb[3]; Rt = P1 + P2 + P3
        xR = Rt.xy()[0]; r["target_decomposable"] = True
        # build + verify S4
        P4, S4 = build_S4(F, a6)
        van, tot, nz, ntot = verify_S4(E, P4, S4, ntest=20)
        r["S4_verify"] = "%d/%d vanish, %d/%d nonzero" % (van, tot, nz, ntot)
        r["S4_GENUINE"] = bool(van == tot and tot >= 15 and nz >= int(0.7 * max(1, ntot)))
        r["S4_total_degree"] = int(S4.degree())
        if not r["S4_GENUINE"]:
            r["status"] = "S4 not verified -> abort"; signal.alarm(0); return r
        # descend S4(x1,x2,x3,xR)=0
        R2 = PolynomialRing(GF(2), ['c%d_%d' % (i, j) for i in range(m) for j in range(l)])
        B = BooleanPolynomialRing(nvars, ['c%d_%d' % (i, j) for i in range(m) for j in range(l)])
        PF = PolynomialRing(F, ['c%d_%d' % (i, j) for i in range(m) for j in range(l)]); cF = PF.gens()
        def xexpr(i): return sum(cF[i*l + j]*w[j] for j in range(l))
        gpf = P4.gens()
        Phi = S4.subs({gpf[0]: xexpr(0), gpf[1]: xexpr(1), gpf[2]: xexpr(2), gpf[3]: xR})
        comps = [g for g in f2_components(Phi, F, n, R2) if g != 0]
        def R2toB(g):
            res = B(0)
            for c, mo in zip(g.coefficients(), g.monomials()):
                if c == 0: continue
                e = mo.exponents()[0]; term = B(1)
                for i in range(nvars):
                    if e[i]: term *= B.gen(i)
                res += term
            return res
        gen_b = [g for g in (R2toB(g) for g in comps) if g != 0]
        r["n_gen_eqs"] = len(gen_b); r["gen_degs"] = sorted(set(int(g.degree()) for g in gen_b))
        gen = gb_info(gen_b, B); r["genuine"] = gen
        # sanity: the real solution (c1|c2|c3) must be a root of the genuine ideal
        realsol = {B.gen(j): GF(2)(c1[j]) for j in range(l)}
        realsol.update({B.gen(l + j): GF(2)(c2[j]) for j in range(l)})
        realsol.update({B.gen(2*l + j): GF(2)(c3[j]) for j in range(l)})
        r["real_sol_satisfies"] = bool(all(g.subs(realsol) == 0 for g in gen_b))
        # control: random with planted solution, matched #eqs + degree profile
        set_random_seed(int(seed) + 123)
        prof = sorted(int(g.degree()) for g in gen_b)
        sol = [B(GF(2).random_element()) for _ in range(nvars)]
        ss = {B.gen(i): sol[i] for i in range(nvars)}
        ctrl_b = []
        for idx in range(len(gen_b)):
            d = prof[idx]; cap = int(min(14, binomial(nvars, max(1, min(d, nvars)))))
            g = B.random_element(degree=d, terms=cap); g = g + g.subs(ss)
            if g != 0: ctrl_b.append(g)
        ctrl = gb_info(ctrl_b, B); r["control"] = ctrl
        if gen["consistent"] and ctrl["consistent"]:
            r["DISCRIMINATES"] = bool(gen["maxdeg"] < ctrl["maxdeg"])
            r["gen_minus_ctrl"] = gen["maxdeg"] - ctrl["maxdeg"]
        else:
            r["DISCRIMINATES"] = None
        r["status"] = "OK"
    except Timeout:
        r["status"] = "TIMEOUT(%ds)" % tcap
    except Exception as ex:
        r["status"] = "EXC %s" % repr(ex)[:140]
    finally:
        signal.alarm(0)
    return r

GRID = [7, 11]
results = []
for n in GRID:
    t0 = time.time()
    r = cell(n, seed=1, tcap=150)
    r["cell_secs"] = round(time.time() - t0, 1)
    results.append(r)
    g = r.get("genuine", {}); c = r.get("control", {})
    out("[n=%2d m=3] status=%s S4_gen=%s S4deg=%s realsol=%s nvars=%s gen{md=%s cons=%s sols=%s} ctrl{md=%s cons=%s} DISCRIM=%s rho2^%.1f (%.1fs)"
        % (n, r.get("status"), r.get("S4_GENUINE"), r.get("S4_total_degree"), r.get("real_sol_satisfies"),
           r.get("nvars"), g.get("maxdeg"), g.get("consistent"), g.get("nsols"),
           c.get("maxdeg"), c.get("consistent"), r.get("DISCRIMINATES"),
           r.get("rho_log2", float('nan')), r["cell_secs"]))

out("\nRESULTS_JSON " + json.dumps(results, default=str))
_lf.close()
print("WROTE", LOGP)
