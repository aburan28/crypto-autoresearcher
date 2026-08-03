# BIN-EXP-001 : Weil descent of binary Semaev systems + GATED first-fall meter.
#
# Central NOVEL question (literature_binary_field.md): over F_{2^n}, is the first
# fall of the descended Semaev decomposition system GATE-MEANINGFUL (support on the
# summation-poly rows = real IC leverage) or a field-equation/FB-row ARTIFACT (as in
# the prime-field campaign NR-019/NR-032)? And does the Kosters-Yeo degree-2 S3
# trace syzygy PROPAGATE from S3 (m=2) to S4 (m=3)?
#
# Method per (n,m): build ordinary E/F_{2^n}; build+VERIFY S_{m+1}; factor base
# V = F_2-subspace dim l~n/m; Weil-descend S_{m+1}(xR, x_1..x_m)=0 to n eqs over F_2
# in m*l binary unknowns; add field equations c^2+c (the "FB/membership" rows);
# run the persisted gated meter with sumpoly_indices = the descended-Semaev rows.
# Positive control: a REAL decomposition R=P1+..+Pm with x(Pi) in V must satisfy the
# descended system (validates the descent). Negative control: random matched system.
# Toy parameters only.
import json, time
LOGP = "/Volumes/Volume/autolab/experiments/ecdlp_binary_field/bin_exp001_weil_descent_gate.log"
_lf = open(LOGP, "w")
def out(s):
    print(s); _lf.write(str(s) + "\n"); _lf.flush()

out("=== BIN-EXP-001 Weil descent + gated meter ===  " + time.asctime())
load("/Volumes/Volume/autolab/experiments/ecdlp_prime_field/round016_gated_meter.sage")

# in-run meter self-validation (trust nothing otherwise)
_ov, _rows = self_validate(verbose=False)
out("[meter] self_validate OVERALL_PASS = %s" % _ov)
assert _ov, "meter failed self-validation; aborting"

# -----------------------------------------------------------------------------
def make_curve(n, seed=1):
    set_random_seed(int(seed))
    F = GF(2**n, 'a'); a = F.gen()
    best = None
    for _ in range(400):
        a2 = F.random_element(); a6 = F.random_element()
        if a6.is_zero(): continue
        try: E = EllipticCurve(F, [1, a2, 0, 0, a6])
        except Exception: continue
        N = E.order(); big = max(p for p, e in factor(N))
        if best is None or big > best[5]:
            best = (F, a, E, a2, a6, big, N)
        if big >= N // 2:
            return F, a, E, a2, a6, N, big
    F, a, E, a2, a6, big, N = best
    return F, a, E, a2, a6, N, big

def semaev3(F, a6, names):
    P = PolynomialRing(F, names); g = P.gens()
    x1, x2, x3 = g[0], g[1], g[2]
    return P, (x1*x2 + x1*x3 + x2*x3)**2 + x1*x2*x3 + a6

def verify_poly_vanishes(E, poly, P, arity, ntest=25):
    """poly in P (arity vars) must vanish on x-coords of `arity` pts summing to O,
    and be nonzero on random non-summing tuples."""
    van = 0; tot = 0; nz = 0; ntot = 0
    tries = 0
    while tot < ntest and tries < 6000:
        tries += 1
        pts = [E.random_point() for _ in range(arity - 1)]
        last = -sum(pts, E(0))
        pts = pts + [last]
        if any(Q.is_zero() for Q in pts): continue
        xs = [Q.xy()[0] for Q in pts]
        van += (poly(*xs) == 0); tot += 1
    tries = 0
    while ntot < ntest and tries < 8000:
        tries += 1
        pts = [E.random_point() for _ in range(arity)]
        if any(Q.is_zero() for Q in pts): continue
        if sum(pts, E(0)).is_zero(): continue
        xs = [Q.xy()[0] for Q in pts]
        nz += (poly(*xs) != 0); ntot += 1
    return van, tot, nz, ntot

def f2_components(Phi, F, n, R2):
    """Phi in PolynomialRing(F, vars); return n polys over GF(2) (R2), one per
    F_2-coordinate a^k, k=0..n-1."""
    comps = [R2(0)] * n
    ngens = R2.ngens()
    for coeff, mono in zip(Phi.coefficients(), Phi.monomials()):
        bits = list(coeff.polynomial().list())
        bits = bits + [GF(2)(0)] * (n - len(bits))
        e = mono.exponents()[0]
        m2 = R2.monomial(*[int(e[i]) for i in range(ngens)]) if any(e) else R2(1)
        for k in range(n):
            if bits[k] != 0:
                comps[k] = comps[k] + m2
    return comps

def cell(n, m, seed=1):
    """One (n,m) measurement. Returns a result dict."""
    r = {"n": n, "m": m}
    F, a, E, a2, a6, N, big = make_curve(n, seed)
    r["order"] = int(N); r["largest_prime"] = int(big); r["cofactor"] = int(N // big)
    r["rho_ops"] = float(0.886 * sqrt(float(big)))
    arity = m + 1
    # build + verify S_{m+1}
    if m == 2:
        P, S = semaev3(F, a6, 'X1,X2,X3')
    elif m == 3:
        P3, S3 = semaev3(F, a6, 'u1,u2,t')
        P4tmp = PolynomialRing(F, 'X1,X2,X3,X4,T')
        X1, X2, X3, X4, T = P4tmp.gens()
        S3a = S3.subs({P3.gen(0): X1, P3.gen(1): X2, P3.gen(2): T})
        S3b = S3.subs({P3.gen(0): X3, P3.gen(1): X4, P3.gen(2): T})
        S4 = S3a.resultant(S3b, T)
        P = PolynomialRing(F, 'X1,X2,X3,X4')
        gg = P.gens()
        S = P(S4.subs({X1: gg[0], X2: gg[1], X3: gg[2], X4: gg[3]}))
        # remove repeated square factors if any (resultant may be a square)
        try:
            facs = list(factor(S))
            S = prod(f for f, e in facs)  # squarefree part
        except Exception:
            pass
    else:
        raise ValueError("m must be 2 or 3")
    van, tot, nz, ntot = verify_poly_vanishes(E, S, P, arity, ntest=25)
    r["S_verify_vanish"] = "%d/%d" % (van, tot)
    r["S_verify_nonzero"] = "%d/%d" % (nz, ntot)
    r["S_GENUINE"] = bool(van == tot and tot >= 20 and nz >= int(0.7 * max(1, ntot)))
    r["S_total_degree"] = int(S.degree())
    if not r["S_GENUINE"]:
        r["status"] = "S_NOT_VERIFIED -> abort cell (no metering on unverified S)"
        return r
    # factor base subspace V = span_{F2}{a^0..a^{l-1}}, l ~ n/m
    l = max(2, int(round(n / m)))
    w = [a**j for j in range(l)]
    r["l"] = l; r["nvars"] = m * l
    # ---- positive control: a REAL decomposition validates the descent ----
    # collect FB points (x-coord in V)
    def coords_in_V(beta):
        v = list(beta.polynomial().list()); v = v + [GF(2)(0)] * (n - len(v))
        # beta in V iff all coords with index >= l are zero
        return None if any(v[j] != 0 for j in range(l, n)) else [int(v[j]) for j in range(l)]
    fb = []
    for Q in E:
        if Q.is_zero(): continue
        xc = Q.xy()[0]; cc = coords_in_V(xc)
        if cc is not None:
            fb.append((Q, xc, cc))
        if len(fb) >= 60: break
    r["fb_size"] = len(fb)
    # build the GF(2) variable ring
    R2 = PolynomialRing(GF(2), ['c%d_%d' % (i, j) for i in range(m) for j in range(l)])
    cvars = R2.gens()
    def xblock(i):  # x_i = sum_j c_{i,j} w_j  as element of PolynomialRing(F,cvars)
        return i
    # We need x_i over a ring with F coefficients AND the c-variables.
    PF = PolynomialRing(F, ['c%d_%d' % (i, j) for i in range(m) for j in range(l)])
    cF = PF.gens()
    def xexpr(i):
        return sum(cF[i * l + j] * w[j] for j in range(l))
    pos_ok = None
    if r["fb_size"] >= 2:
        P1, x1c, c1 = fb[0]; P2, x2c, c2 = fb[1]
        Rt = P1 + P2
        if not Rt.is_zero():
            xR = Rt.xy()[0]
            if m == 2:
                Phi = S.subs({P.gen(0): xexpr(0), P.gen(1): xexpr(1), P.gen(2): xR})
            else:
                Phi = S.subs({P.gen(0): xexpr(0), P.gen(1): xexpr(1),
                              P.gen(2): xexpr(2), P.gen(3): xR})  # m=3: 3 free pts? see note
            # NOTE m=3 positive control needs 3 fb pts summing with R; approximate:
            comps = f2_components(Phi, F, n, R2)
            # evaluate at the real c-solution (only valid for m=2 here)
            if m == 2:
                subst = {}
                for j in range(l): subst[cvars[j]] = GF(2)(c1[j])
                for j in range(l): subst[cvars[l + j]] = GF(2)(c2[j])
                pos_ok = all(g.subs(subst) == 0 for g in comps)
    r["pos_control_descent_ok"] = pos_ok
    # ---- the actual structural system: random target xR, descended + field eqs ----
    set_random_seed(int(seed) + 7)
    Rt = E.random_point()
    while Rt.is_zero(): Rt = E.random_point()
    xR = Rt.xy()[0]
    if m == 2:
        Phi = S.subs({P.gen(0): xexpr(0), P.gen(1): xexpr(1), P.gen(2): xR})
    else:
        Phi = S.subs({P.gen(0): xexpr(0), P.gen(1): xexpr(1),
                      P.gen(2): xexpr(2), P.gen(3): xR})
    comps = f2_components(Phi, F, n, R2)
    comps = [g for g in comps if g != 0]        # drop trivial component eqs
    fieldeqs = [c**2 + c for c in cvars]
    polys = comps + fieldeqs
    sumpoly_indices = list(range(len(comps)))    # descended-Semaev rows
    r["n_descended_eqs"] = len(comps)
    r["n_field_eqs"] = len(fieldeqs)
    r["descended_degs"] = sorted(set(int(g.degree()) for g in comps))
    # run the gated meter
    res = meter_gated(polys, R2, sumpoly_indices, Dmax=10)
    r["d_ff"] = res["d_ff"]; r["D_reg"] = res["D_reg"]
    r["fires"] = res["fires"]; r["gate_passes"] = res["gate_passes"]
    r["gate_meaningful"] = res["gate_meaningful"]
    r["gate_detail"] = {k: res["gate_detail"][k] for k in
                        ("nontriv_full_at_dff", "nontriv_fb_only_at_dff", "summation_support")}
    # ---- negative control: random matched-degree "summation" rows + field eqs ----
    set_random_seed(int(seed) + 99)
    nc_sum = []
    degs_target = r["descended_degs"] if r["descended_degs"] else [2]
    for idx in range(len(comps)):
        d = degs_target[idx % len(degs_target)]
        nc_sum.append(R2.random_element(degree=d, terms=8))
    nc_polys = nc_sum + fieldeqs
    try:
        nres = meter_gated(nc_polys, R2, list(range(len(nc_sum))), Dmax=10)
        r["neg_d_ff"] = nres["d_ff"]; r["neg_gate_meaningful"] = nres["gate_meaningful"]
    except Exception as ex:
        r["neg_d_ff"] = None; r["neg_gate_meaningful"] = "err:%s" % repr(ex)[:40]
    r["status"] = "OK"
    return r

# ---- run the grid ----------------------------------------------------------
GRID = [(5, 2), (7, 2), (11, 2), (13, 2), (7, 3), (11, 3)]
results = []
for (n, m) in GRID:
    t0 = time.time()
    try:
        r = cell(n, m, seed=1)
    except Exception as ex:
        r = {"n": n, "m": m, "status": "EXC: %s" % repr(ex)[:120]}
    r["secs"] = round(time.time() - t0, 1)
    results.append(r)
    out("[cell n=%d m=%d] status=%s S_GENUINE=%s d_ff=%s D_reg=%s fires=%s gate_meaningful=%s "
        "pos_ctrl=%s neg_gm=%s nvars=%s descdeg=%s (%.1fs)"
        % (n, m, r.get("status"), r.get("S_GENUINE"), r.get("d_ff"), r.get("D_reg"),
           r.get("fires"), r.get("gate_meaningful"), r.get("pos_control_descent_ok"),
           r.get("neg_gate_meaningful"), r.get("nvars"), r.get("descended_degs"), r["secs"]))

out("\n================ SUMMARY TABLE ================")
out("%-3s %-3s %-7s %-6s %-6s %-6s %-9s %-9s %-8s %-8s"
    % ("n", "m", "S_gen", "d_ff", "D_reg", "fires", "gate_mng", "pos_ctrl", "neg_gm", "rho2^"))
for r in results:
    rho = ("%.0f" % log(r["rho_ops"], 2)) if "rho_ops" in r else "-"
    out("%-3s %-3s %-7s %-6s %-6s %-6s %-9s %-9s %-8s %-8s"
        % (r["n"], r["m"], r.get("S_GENUINE"), r.get("d_ff"), r.get("D_reg"),
           r.get("fires"), r.get("gate_meaningful"), r.get("pos_control_descent_ok"),
           r.get("neg_gate_meaningful"), rho))

out("\nRESULTS_JSON " + json.dumps(results, default=str))
_lf.close()
print("WROTE", LOGP)
