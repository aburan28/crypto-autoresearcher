# BIN-EXP-004 : LARGER-n (not-too-large) binary Semaev index calculus, m=3.
#
# The decisive question (per literature_binary_field.md, the binary analog of the
# prime-field NR-026 capstone): as n grows beyond toy size, does the genuine binary
# Weil-descent Semaev decomposition system (a) keep a BOUNDED solving degree
# (the FPPR-favorable direction), and (b) where does the resulting index-calculus
# COST sit relative to Pollard rho?  These are two different questions:
#   - solving-degree bounded?  -> is polynomial solving the bottleneck?
#   - IC vs rho cost balance?   -> where is the crossover (if any)?
#
# Design fixes vs BIN-EXP-003 (which hung at n=11 m=3 on a for-Q-in-E factor base):
#   * FAST factor base: enumerate x over the F2-subspace V (2^l ~ 2^{n/3} values) and
#     E.lift_x, instead of iterating up to 2^n curve points.
#   * KNOWN-decomposable target R = P1+P2+P3 (guarantees a consistent genuine system).
#   * VERIFY S4 (20/20 vanish on real 4-tuples) before metering.
#   * Measure: genuine Groebner solving degree (max deg of reduced GB) + wall-clock;
#     real-solution-recovery check; actual |FB|; and the analytic IC/rho balance.
#   * Hard per-cell signal.alarm timeout; write each cell immediately (partial-safe).
# Toy/scaled parameters only; no real keys. NOT a real-world break.
import json, time, signal
LOGP = "/Volumes/Volume/autolab/experiments/ecdlp_binary_field/bin_exp004_larger_n.log"
_lf = open(LOGP, "w")
def out(s):
    print(s); _lf.write(str(s) + "\n"); _lf.flush()
out("=== BIN-EXP-004 larger-n binary Semaev IC (m=3) ===  " + time.asctime())

class Timeout(Exception): pass
def _alarm(sig, frm): raise Timeout()
signal.signal(signal.SIGALRM, _alarm)

def make_curve(n, seed=1):
    set_random_seed(int(seed))
    F = GF(2**n, 'a'); a = F.gen(); best = None
    for _ in range(300):
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
    S4full = S3(X1, X2, T).resultant(S3(X3, X4, T), T)
    P4 = PolynomialRing(F, 'X1,X2,X3,X4'); g = P4.gens()
    S4 = P4(S4full.subs({X1: g[0], X2: g[1], X3: g[2], X4: g[3], T: 0}))
    try: S4 = prod(f for f, e in factor(S4))
    except Exception: pass
    return P4, S4

def verify_S4(E, P4, S4, ntest=20):
    van = tot = nz = ntot = 0; tries = 0
    while tot < ntest and tries < 6000:
        tries += 1
        P1 = E.random_point(); P2 = E.random_point(); P3 = E.random_point()
        pts = [P1, P2, P3, -(P1 + P2 + P3)]
        if any(Q.is_zero() for Q in pts): continue
        van += (S4(*[Q.xy()[0] for Q in pts]) == 0); tot += 1
    tries = 0
    while ntot < ntest and tries < 8000:
        tries += 1
        pts = [E.random_point() for _ in range(4)]
        if any(Q.is_zero() for Q in pts): continue
        if sum(pts, E(0)).is_zero(): continue
        nz += (S4(*[Q.xy()[0] for Q in pts]) != 0); ntot += 1
    return van, tot, nz, ntot

def fb_from_V(E, F, w, l):
    """factor base = points with x-coord in V = span_{F2}(w[0..l-1]); fast (2^l)."""
    fb = []
    for bits in range(1, 2**l):
        x = sum((w[j] for j in range(l) if (bits >> j) & 1), F(0))
        if x.is_zero(): continue
        try: P = E.lift_x(x)
        except ValueError: continue
        fb.append((P, x))
    return fb

def f2_components(Phi, F, n, R2):
    comps = [R2(0)] * n; ngens = R2.ngens()
    for coeff, mono in zip(Phi.coefficients(), Phi.monomials()):
        bits = list(coeff.polynomial().list()); bits += [GF(2)(0)] * (n - len(bits))
        e = mono.exponents()[0]
        m2 = R2.monomial(*[int(e[i]) for i in range(ngens)]) if any(e) else R2(1)
        for k in range(n):
            if bits[k] != 0: comps[k] = comps[k] + m2
    return comps

def cell(n, seed=1, tcap=240):
    r = {"n": n, "m": 3}
    signal.alarm(int(tcap))
    try:
        F, a, E, a2, a6, N, big = make_curve(n, seed)
        r["largest_prime_bits"] = float(log(float(big), 2))
        r["rho_exp"] = float(log(0.886, 2) + 0.5 * log(float(big), 2))   # rho ~ 0.886 sqrt(big)
        l = max(2, int(round(n / 3))); m = 3; nvars = m * l
        r["l"] = l; r["nvars"] = nvars
        w = [a**j for j in range(l)]
        fb = fb_from_V(E, F, w, l)
        r["fb_size"] = len(fb)
        r["log2_fb"] = float(log(max(1, len(fb)), 2))
        # IC/rho cost balance (analytic, the real obstruction):
        #   relation generation ~ |FB| relations; sparse linear algebra ~ |FB|^2.
        r["LA_exp"] = 2.0 * r["log2_fb"]                 # |FB|^2 sparse linear algebra
        r["IC_over_rho_exp"] = r["LA_exp"] - r["rho_exp"]  # >0  => IC worse than rho
        if len(fb) < 3:
            r["status"] = "FB<3"; signal.alarm(0); return r
        (P1, x1), (P2, x2), (P3, x3) = fb[0], fb[1], fb[2]
        Rt = P1 + P2 + P3; idx = 3
        while Rt.is_zero() and idx < len(fb):
            P3, x3 = fb[idx]; Rt = P1 + P2 + P3; idx += 1
        xR = Rt.xy()[0]; r["target_decomposable"] = bool(not Rt.is_zero())
        P4, S4 = build_S4(F, a6)
        van, tot, nz, ntot = verify_S4(E, P4, S4, ntest=20)
        r["S4_verify"] = "%d/%d vanish, %d/%d nz" % (van, tot, nz, ntot)
        r["S4_GENUINE"] = bool(van == tot and tot >= 15 and nz >= int(0.7 * max(1, ntot)))
        if not r["S4_GENUINE"]:
            r["status"] = "S4 not verified"; signal.alarm(0); return r
        # descend S4(x0,x1,x2,xR)=0 to GF(2)
        names = ['c%d_%d' % (i, j) for i in range(m) for j in range(l)]
        R2 = PolynomialRing(GF(2), names)
        B = BooleanPolynomialRing(nvars, names)
        PF = PolynomialRing(F, names); cF = PF.gens()
        def xexpr(i): return sum(cF[i * l + j] * w[j] for j in range(l))
        gpf = P4.gens()
        t_sub = time.time()
        Phi = S4.subs({gpf[0]: xexpr(0), gpf[1]: xexpr(1), gpf[2]: xexpr(2), gpf[3]: xR})
        comps = [g for g in f2_components(Phi, F, n, R2) if g != 0]
        r["subs_secs"] = round(time.time() - t_sub, 2)
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
        r["n_gen_eqs"] = len(gen_b)
        r["descended_degs"] = sorted(set(int(g.degree()) for g in gen_b))
        t_gb = time.time()
        I = B.ideal(gen_b); gb = list(I.groebner_basis()); r["gb_secs"] = round(time.time() - t_gb, 2)
        if len(gb) == 1 and gb[0] == B(1):
            r["consistent"] = False; r["solving_degree"] = 0
        else:
            r["consistent"] = True
            r["solving_degree"] = int(max((g.degree() for g in gb), default=0))
            r["n_gb"] = len(gb)
        # real-solution recovery check (cheap substitution; no variety at large nvars)
        def coords(beta):
            v = list(beta.polynomial().list()); v += [GF(2)(0)] * (n - len(v))
            return [int(v[j]) for j in range(l)]
        c1, c2, c3 = coords(x1), coords(x2), coords(x3)
        realsol = {B.gen(j): GF(2)(c1[j]) for j in range(l)}
        realsol.update({B.gen(l + j): GF(2)(c2[j]) for j in range(l)})
        realsol.update({B.gen(2 * l + j): GF(2)(c3[j]) for j in range(l)})
        r["real_sol_satisfies"] = bool(all(g.subs(realsol) == 0 for g in gen_b))
        r["status"] = "OK"
    except Timeout:
        r["status"] = "TIMEOUT(%ds)" % tcap
    except Exception as ex:
        r["status"] = "EXC %s" % repr(ex)[:140]
    finally:
        signal.alarm(0)
    return r

GRID = [11, 13, 17, 19, 23, 29, 31, 37]
results = []
for n in GRID:
    t0 = time.time()
    r = cell(n, seed=1, tcap=240)
    r["cell_secs"] = round(time.time() - t0, 1)
    results.append(r)
    out("[n=%2d m=3] status=%-12s S4gen=%s |FB|=%s nvars=%s descdeg=%s solv_deg=%s cons=%s realsol=%s "
        "gb=%ss | rho2^%.1f LA2^%.1f IC/rho=2^%+.1f (%.1fs)"
        % (n, r.get("status"), r.get("S4_GENUINE"), r.get("fb_size"), r.get("nvars"),
           r.get("descended_degs"), r.get("solving_degree"), r.get("consistent"),
           r.get("real_sol_satisfies"), r.get("gb_secs"),
           r.get("rho_exp", float('nan')), r.get("LA_exp", float('nan')),
           r.get("IC_over_rho_exp", float('nan')), r["cell_secs"]))

out("\n=== SUMMARY: solving degree (bounded?) and IC/rho balance vs n (m=3) ===")
out("%-4s %-6s %-7s %-9s %-9s %-9s %-10s" % ("n", "nvars", "|FB|", "solv_deg", "rho2^", "LA2^", "IC/rho2^"))
for r in results:
    out("%-4s %-6s %-7s %-9s %-9s %-9s %-10s" % (
        r.get("n"), r.get("nvars"), r.get("fb_size"), r.get("solving_degree"),
        ("%.1f" % r["rho_exp"]) if "rho_exp" in r else "-",
        ("%.1f" % r["LA_exp"]) if "LA_exp" in r else "-",
        ("%+.1f" % r["IC_over_rho_exp"]) if "IC_over_rho_exp" in r else "-"))
out("\nRESULTS_JSON " + json.dumps(results, default=str))
_lf.close()
print("WROTE", LOGP)
