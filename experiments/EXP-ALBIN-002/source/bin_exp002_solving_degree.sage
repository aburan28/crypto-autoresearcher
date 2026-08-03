# BIN-EXP-002 : actual Groebner SOLVING-DEGREE growth discriminator for binary IC.
#
# BIN-EXP-001 (BIN-NR-001) found the leading-form gate cannot discriminate genuine
# vs random in the binary descended setting (separated degree tiers => field eqs make
# generic early falls; real d_ff == random d_ff). CORRECTED discriminator here:
# compute the ACTUAL reduced-Groebner-basis max degree of the genuine descended S3
# system vs a RANDOM control WITH A PLANTED SOLUTION (matched #eqs, #vars, degrees),
# as n grows. FPPR/Petit-Quisquater claim genuine binary Semaev systems solve at a
# degree BOUNDED in n, BELOW the generic degree. If genuine GB max-degree grows
# SLOWER than the matched random control as n rises -> real exploitable structure.
# If they track each other -> no detectable structure at reachable n (the honest
# expectation given Shantz-Teske/Galbraith: IC does not beat rho at toy n).
# BooleanPolynomialRing builds in field equations x^2=x. Toy parameters only.
import json, time
LOGP = "/Volumes/Volume/autolab/experiments/ecdlp_binary_field/bin_exp002_solving_degree.log"
_lf = open(LOGP, "w")
def out(s):
    print(s); _lf.write(str(s) + "\n"); _lf.flush()
out("=== BIN-EXP-002 solving-degree growth discriminator ===  " + time.asctime())

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

def f2_components(Phi, F, n, R2):
    comps = [R2(0)] * n; ngens = R2.ngens()
    for coeff, mono in zip(Phi.coefficients(), Phi.monomials()):
        bits = list(coeff.polynomial().list()); bits += [GF(2)(0)] * (n - len(bits))
        e = mono.exponents()[0]
        m2 = R2.monomial(*[int(e[i]) for i in range(ngens)]) if any(e) else R2(1)
        for k in range(n):
            if bits[k] != 0: comps[k] = comps[k] + m2
    return comps

def gb_info(bpolys, B, do_variety=True):
    I = B.ideal(bpolys)
    t0 = time.time(); gb = list(I.groebner_basis()); dt = time.time() - t0
    if len(gb) == 1 and gb[0] == B(1):
        return {"maxdeg": 0, "ngb": 1, "consistent": False, "nsols": 0, "secs": round(dt, 2)}
    md = max((g.degree() for g in gb), default=0)
    nsols = None
    if do_variety and B.ngens() <= 14:
        try: nsols = len(I.variety())
        except Exception: nsols = None
    return {"maxdeg": int(md), "ngb": len(gb), "consistent": True, "nsols": nsols, "secs": round(dt, 2)}

def cell(n, m=2, seed=1):
    r = {"n": n, "m": m}
    F, a, E, a2, a6, N, big = make_curve(n, seed)
    r["largest_prime"] = int(big); r["rho_log2"] = float(log(0.886 * sqrt(float(big)), 2))
    l = max(2, int(round(n / m))); nvars = m * l; r["l"] = l; r["nvars"] = nvars
    names = ['c%d_%d' % (i, j) for i in range(m) for j in range(l)]
    R2 = PolynomialRing(GF(2), names)
    B = BooleanPolynomialRing(nvars, names)
    def R2toB(g):
        res = B(0)
        for c, mo in zip(g.coefficients(), g.monomials()):
            if c == 0: continue
            e = mo.exponents()[0]; term = B(1)
            for i in range(nvars):
                if e[i]: term = term * B.gen(i)
            res = res + term
        return res
    # ---- genuine descended S3 system (random target xR) ----
    w = [a**j for j in range(l)]
    PF = PolynomialRing(F, names); cF = PF.gens()
    def xexpr(i): return sum(cF[i * l + j] * w[j] for j in range(l))
    P3 = PolynomialRing(F, 'X1,X2,X3'); X1, X2, X3 = P3.gens()
    S3 = (X1 * X2 + X1 * X3 + X2 * X3)**2 + X1 * X2 * X3 + a6
    set_random_seed(int(seed) + 7)
    Rt = E.random_point()
    while Rt.is_zero(): Rt = E.random_point()
    xR = Rt.xy()[0]
    Phi = S3.subs({X1: xexpr(0), X2: xexpr(1), X3: xR})
    comps = [g for g in f2_components(Phi, F, n, R2) if g != 0]
    gen_b = [g for g in (R2toB(g) for g in comps) if g != 0]
    r["n_gen_eqs"] = len(gen_b); r["gen_degs"] = sorted(set(int(g.degree()) for g in gen_b))
    r["genuine"] = gb_info(gen_b, B)
    # ---- random control with PLANTED solution, matched #eqs & degree profile ----
    set_random_seed(int(seed) + 123)
    sol = [B(GF(2).random_element()) for _ in range(nvars)]
    subs_sol = {B.gen(i): sol[i] for i in range(nvars)}
    gen_deg_profile = sorted(int(g.degree()) for g in gen_b)
    ctrl_b = []
    for idx in range(len(gen_b)):
        d = gen_deg_profile[idx]
        cap = int(min(12, binomial(nvars, max(1, min(d, nvars)))))
        g = B.random_element(degree=d, terms=cap)
        g = g + g.subs(subs_sol)        # force g(sol)=0 so the control is consistent
        if g != 0: ctrl_b.append(g)
    r["n_ctrl_eqs"] = len(ctrl_b)
    r["control"] = gb_info(ctrl_b, B)
    g, c = r["genuine"], r["control"]
    if g["consistent"] and c["consistent"]:
        r["DISCRIMINATES"] = bool(g["maxdeg"] < c["maxdeg"])
        r["gen_minus_ctrl_maxdeg"] = g["maxdeg"] - c["maxdeg"]
    else:
        r["DISCRIMINATES"] = None
    return r

GRID_N = [7, 11, 13, 17, 19]
results = []
for n in GRID_N:
    t0 = time.time()
    try:
        r = cell(n, m=2, seed=1)
    except Exception as ex:
        r = {"n": n, "m": 2, "status": "EXC %s" % repr(ex)[:140]}
    r["cell_secs"] = round(time.time() - t0, 1)
    results.append(r)
    g = r.get("genuine", {}); c = r.get("control", {})
    out("[n=%2d] nvars=%s gen{maxdeg=%s ngb=%s cons=%s sols=%s %ss} ctrl{maxdeg=%s cons=%s sols=%s} DISCRIM=%s rho2^%.1f (%.1fs)"
        % (n, r.get("nvars"), g.get("maxdeg"), g.get("ngb"), g.get("consistent"), g.get("nsols"), g.get("secs"),
           c.get("maxdeg"), c.get("consistent"), c.get("nsols"), r.get("DISCRIMINATES"),
           r.get("rho_log2", float('nan')), r["cell_secs"]))

out("\n=== SUMMARY: genuine vs matched-random Groebner max-degree growth (m=2) ===")
out("%-4s %-6s %-12s %-12s %-10s" % ("n", "nvars", "gen_maxdeg", "ctrl_maxdeg", "discrim"))
for r in results:
    g = r.get("genuine", {}); c = r.get("control", {})
    out("%-4s %-6s %-12s %-12s %-10s" % (r.get("n"), r.get("nvars"),
        g.get("maxdeg"), c.get("maxdeg"), r.get("DISCRIMINATES")))
out("\nRESULTS_JSON " + json.dumps(results, default=str))
_lf.close()
print("WROTE", LOGP)
