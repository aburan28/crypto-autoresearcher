# EXP-R6-001 executor — arbitrary explicit factor-base membership solve.
# Chained Semaev m=3 (+ m=4 spot arm) over F_p with membership prod_{f in F}(x_i - x(f))
# for an explicit arbitrary index set F (random | interval arms), |F| ~ l^(1/m).
# Controls: (1) Pollard rho on same instances (H040 op convention: 1 op = 1 point
# addition during the walk, exact first-repeat seen-set, setup not counted);
# (2) matched random curves in the same l-window (independent fields/orders);
# (3) same-order isogenous curve (explicit small-degree isogeny when found);
# (4) support-matched random-coefficient null systems (same monomial support).
#
# usage: sage R6_run.sage MODE out=PATH [k=v ...]
#   modes: probe | cell | rho_ladder | censor_doc
# Every run is seeded (deterministic), writes raw.json incrementally after every
# record (kill-safe), honors a soft deadline, and prints progress to stderr.
import time, json, sys, os, subprocess, resource

T0 = time.time()
def now(): return time.time()
def elapsed(): return now() - T0
def eprint(*a):
    print(f"[{elapsed():8.1f}s]", *a, file=sys.stderr, flush=True)

def maxdeg(gb):
    return int(max((g.total_degree() for g in gb if g != 0), default=0))

def S3(X1, X2, X3, a, b):
    return ((X1-X2)**2*X3**2 - 2*((X1+X2)*(X1*X2+a)+2*b)*X3
            + ((X1*X2-a)**2 - 4*b*(X1+X2)))

# ---------------------------------------------------------------- state / io
STATE = {"records": {"units": [], "curves": [], "solves": [], "rho": [],
                     "nulls": [], "control3": [], "probe": [], "attempts": []},
         "notes": [], "complete": False, "termination": "running"}
OUT = None
def flush():
    if OUT:
        tmp = OUT + ".tmp"
        with open(tmp, "w") as f:
            json.dump(STATE, f, default=_ser)
        os.replace(tmp, OUT)
def _ser(o):
    try: return int(o)
    except Exception:
        try: return float(o)
        except Exception: return str(o)
def rec(kind, d):
    STATE["records"][kind].append(d)
    flush()
def note(s):
    STATE["notes"].append(str(s)); eprint("NOTE:", s); flush()

def git_info():
    try:
        root = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                              capture_output=True, text=True).stdout.strip()
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root,
                              capture_output=True, text=True).stdout.strip()
        st = subprocess.run(["git", "status", "--porcelain"], cwd=root,
                            capture_output=True, text=True).stdout.strip()
        return {"commit": head, "dirty": bool(st)}
    except Exception as e:
        return {"commit": None, "dirty": None, "error": str(e)}

def peak_rss():
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)  # bytes on macOS

# ------------------------------------------------------------ curve / group
def rand_prime_in(lo, hi):
    while True:
        p = int(next_prime(randint(int(lo), int(hi))))
        if p <= int(hi):
            return p

def find_curve_with_subgroup(qmin, qmax, hmax, seed, max_p_tries=200, curves_per_p=30):
    """Random curve whose order N = h*q with q prime in [qmin,qmax], h <= hmax."""
    set_random_seed(seed)
    qmid = (int(qmin) + int(qmax)) // 2
    spread = 4 * int(isqrt(2 * int(qmax))) + 16
    p_lo = max(5, int(qmin) - spread); p_hi = int(qmax) + spread
    tries = 0
    for _ in range(max_p_tries):
        p = rand_prime_in(p_lo, p_hi)
        for _ in range(curves_per_p):
            tries += 1
            a = GF(p).random_element(); b = GF(p).random_element()
            if 4*a**3 + 27*b**2 == 0: continue
            E = EllipticCurve(GF(p), [a, b])
            N = int(E.order())
            for (q, e) in factor(N):
                q = int(q)
                if e == 1 and int(qmin) <= q <= int(qmax) and N // q <= hmax:
                    return {"p": p, "a4": int(a), "a6": int(b), "order": N,
                            "q": q, "h": N // q, "construction_tries": tries,
                            "seed": int(seed)}
    raise RuntimeError(f"no curve found with q in [{qmin},{qmax}] h<={hmax}")

def subgroup_generator(E, q, h, seed):
    set_random_seed(seed)
    while True:
        G = E.random_point()
        P = h * G
        if not P.is_zero():
            return P  # order divides q; q prime, P != O -> order q

def fb_random(E, fsize, seed):
    F = E.base_field(); p = int(F.characteristic()); set_random_seed(seed)
    pts = []; xs = []
    while len(pts) < fsize:
        x = F(randint(0, p - 1))
        try:
            P = E.lift_x(x)
            if not P.is_zero():
                pts.append(P); xs.append(x)
        except Exception:
            pass
    return xs, pts

def fb_interval(E, fsize, seed):
    F = E.base_field(); p = int(F.characteristic())
    pts = []; xs = []; i = 0
    while len(pts) < fsize and i < p:
        x = F(i)
        try:
            P = E.lift_x(x)
            if not P.is_zero():
                pts.append(P); xs.append(x)
        except Exception:
            pass
        i += 1
    return xs, pts

def measure_units(E, P):
    F = E.base_field()
    A = P; t0 = now()
    for _ in range(500): A = A + P
    gop = (now() - t0) / 500.0
    x = F.random_element(); y = F.random_element(); t0 = now()
    for _ in range(20000): x = x * y
    fmul = (now() - t0) / 20000.0
    return {"p": int(F.characteristic()), "group_op_s": float(gop),
            "field_mult_s": float(fmul)}

# ------------------------------------------------------- system build/solve
def build_system(F, a4, a6, FBx, xR, m):
    if m == 3:
        Rp = PolynomialRing(F, ['x1', 'x2', 'x3', 'u'], order='degrevlex')
        x1, x2, x3, u = Rp.gens()
        eqs = [S3(x1, x2, u, a4, a6), S3(u, x3, F(xR), a4, a6)]
        eqs += [prod(z - f for f in FBx) for z in (x1, x2, x3)]
        gens = [x1, x2, x3, u]
    else:
        Rp = PolynomialRing(F, ['x1', 'x2', 'x3', 'x4', 'u1', 'u2'],
                            order='degrevlex')
        x1, x2, x3, x4, u1, u2 = Rp.gens()
        eqs = [S3(x1, x2, u1, a4, a6), S3(u1, x3, u2, a4, a6),
               S3(u2, x4, F(xR), a4, a6)]
        eqs += [prod(z - f for f in FBx) for z in (x1, x2, x3, x4)]
        gens = [x1, x2, x3, x4, u1, u2]
    return Rp, gens, eqs

def verify_solution(E, R, sol, gens, m):
    """sol: dict gen->GF(p). Returns 'verified' | 'degenerate'."""
    pts = []
    for i in range(m):
        xi = sol[gens[i]]
        try:
            pts.append(E.lift_x(xi))
        except Exception:
            return "degenerate"
    for bits in range(2**m):
        S = E(0)
        for i in range(m):
            S = S + (pts[i] if (bits >> i) & 1 else -pts[i])
        if S == R or S == -R:
            return "verified"
    return "degenerate"

def back_substitute(lexgb, F):
    """Greedy triangular solve of a lex GB. Returns list of dicts {gen: value}.
    Raises on non-triangular shape (caller falls back to I.variety())."""
    partial = [{}]
    remaining = list(lexgb)
    while remaining:
        progressed = False
        for g in list(remaining):
            newp = []
            handled = True
            for sol in partial:
                h = g.subs(sol)
                vs = [v for v in h.variables() if h.degree(v) > 0]
                if len(vs) > 1:
                    handled = False
                    break
                if len(vs) == 0:
                    if h.is_zero():
                        newp.append(sol)
                    continue
                hv = h.polynomial(vs[0])
                for (r, _) in hv.roots(F):
                    s2 = dict(sol); s2[vs[0]] = r
                    newp.append(s2)
            if handled:
                partial = newp
                remaining.remove(g)
                progressed = True
                break
        if not progressed:
            raise ValueError("non-triangular lex GB element")
    return partial

def solve_system(E, R, Rp, gens, eqs, m, do_variety=True):
    """Returns (gb_s, d_reg, dim, vdim, n_verified, n_degenerate, variety_s, method)."""
    I = Rp.ideal(eqs)
    t0 = now(); gb = I.groebner_basis(); gb_s = now() - t0
    d_reg = maxdeg(gb)
    if any(g.is_one() for g in gb):
        return gb_s, d_reg, -1, 0, 0, 0, 0.0, "unit_ideal"
    dim = int(I.dimension())
    vdim = None; n_ver = 0; n_deg = 0; var_s = 0.0; method = "none"
    if dim == 0:
        t0 = now()
        vdim = int(I.vector_space_dimension())
        if do_variety and vdim <= 256:
            sols = None
            try:
                lex = I.transformed_basis("fglm")
                sols = back_substitute(lex, E.base_field())
                method = "fglm"
            except Exception:
                method = "singular_variety"
            if sols is None:
                for sol in I.variety():
                    if verify_solution(E, R, sol, gens, m) == "verified":
                        n_ver += 1
                    else:
                        n_deg += 1
            else:
                for sol in sols:
                    if verify_solution(E, R, sol, gens, m) == "verified":
                        n_ver += 1
                    else:
                        n_deg += 1
        var_s = now() - t0
    return gb_s, d_reg, dim, vdim, n_ver, n_deg, var_s, method

def null_like(F, g, seed):
    """Same monomial support as g, coefficients randomized nonzero (T11-style)."""
    set_random_seed(seed)
    out = g.parent()(0)
    for mon in g.monomials():
        c = F.random_element()
        while c == 0:
            c = F.random_element()
        out += c * mon
    return out

# ------------------------------------------------------------- rho control
def rho_dl(E, P, R, q, seed, r=20, max_iter=2000000):
    """H040 convention: 1 op = 1 point addition during the walk; exact
    first-repeat via seen-set; A-table/start setup not counted."""
    set_random_seed(seed)
    tab = []
    for _ in range(r):
        ai = randint(0, q - 1); bi = randint(0, q - 1)
        tab.append((ai, bi, ai * P + bi * R))
    a0 = randint(0, q - 1); b0 = randint(0, q - 1)
    X = a0 * P + b0 * R
    seen = {X: (a0, b0)}
    ops = 0
    while ops < max_iter:
        if X.is_zero():
            i = 0
        else:
            i = int(X.xy()[0]) % r
        ai, bi, Ai = tab[i]
        X = X + Ai; a0 = (a0 + ai) % q; b0 = (b0 + bi) % q; ops += 1
        if X in seen:
            a1, b1 = seen[X]
            db = (b1 - b0) % q
            if db == 0:
                return {"status": "fail_denominator", "ops": ops}
            k = ((a0 - a1) % q) * int(inverse_mod(db, q)) % q
            return {"status": "ok", "ops": ops, "k": int(k),
                    "verified": bool(k * P == R)}
        seen[X] = (a0, b0)
    return {"status": "fail_maxiter", "ops": ops}

# ------------------------------------------------------------------- modes
def mode_probe(P):
    deadline = float(P.get("deadline_s", 520))
    # reference curve near 2^13 for units + calibration
    c = find_curve_with_subgroup(2**13, int(1.15 * 2**13), 16, seed=101)
    E = EllipticCurve(GF(c["p"]), [c["a4"], c["a6"]])
    G = subgroup_generator(E, c["q"], c["h"], 102)
    rec("curves", dict(c, role="probe_reference"))
    rec("units", measure_units(E, G))
    # m=3 planted calibration ladder
    for fsize in [int(x) for x in P.get("m3_sizes", "12,14,16,18,20,24").split(",")]:
        if elapsed() > deadline: note("probe deadline before m3 F=%d" % fsize); break
        xs, pts = fb_random(E, fsize, seed=1000 + fsize)
        while True:  # planted target: sum of 3 distinct FB points
            i, j, k = sorted([randint(0, fsize - 1) for _ in range(3)])
            if i < j < k:
                R = pts[i] + pts[j] + pts[k]
                if not R.is_zero(): break
        xR = R.xy()[0]
        t0 = now()
        Rp, gens, eqs = build_system(E.base_field(), E.a4(), E.a6(), xs, xR, 3)
        build_s = now() - t0
        gb_s, d_reg, dim, vdim, n_ver, n_deg, var_s, method = solve_system(E, R, Rp, gens, eqs, 3)
        rec("probe", {"kind": "m3_planted", "F": fsize, "q": c["q"], "p": c["p"],
                      "build_s": float(build_s), "gb_s": float(gb_s),
                      "variety_s": float(var_s), "total_s": float(build_s + gb_s + var_s),
                      "d_reg": d_reg, "dim": dim, "vdim": vdim,
                      "n_verified": n_ver, "n_degenerate": n_deg, "method": method,
                      "peak_rss_bytes": peak_rss()})
        eprint(f"probe m3 F={fsize}: gb={gb_s:.2f}s d_reg={d_reg} vdim={vdim} ver={n_ver}/{n_ver+n_deg}")
    # rho sanity at q ~ 2^20 (constants anchor vs 1.2533)
    if elapsed() < deadline - 60:
        c2 = find_curve_with_subgroup(2**20, int(1.15 * 2**20), 16, seed=103)
        E2 = EllipticCurve(GF(c2["p"]), [c2["a4"], c2["a6"]])
        P2 = subgroup_generator(E2, c2["q"], c2["h"], 104)
        rec("curves", dict(c2, role="probe_rho"))
        set_random_seed(105)
        for t in range(8):
            k = randint(1, c2["q"] - 1); R = k * P2
            r = rho_dl(E2, P2, R, c2["q"], seed=10000 + t)
            r.update({"curve_q": c2["q"], "target": t,
                      "const": r["ops"] / float(sqrt(c2["q"])) if r.get("ops") else None})
            rec("rho", r)
            eprint(f"probe rho t={t}: ops={r['ops']} const={r.get('const')}")

    # m=4 planted calibration ladder (last: an m4 GB may hang past the
    # internal deadline and rely on the external timeout; records preserved)
    for fsize in [int(x) for x in P.get("m4_sizes", "6,7,8").split(",")]:
        if elapsed() > deadline: note("probe deadline before m4 F=%d" % fsize); break
        xs, pts = fb_random(E, fsize, seed=2000 + fsize)
        while True:
            idx = sorted([randint(0, fsize - 1) for _ in range(4)])
            if len(set(idx)) == 4:
                R = pts[idx[0]] + pts[idx[1]] + pts[idx[2]] + pts[idx[3]]
                if not R.is_zero(): break
        xR = R.xy()[0]
        t0 = now()
        Rp, gens, eqs = build_system(E.base_field(), E.a4(), E.a6(), xs, xR, 4)
        build_s = now() - t0
        gb_s, d_reg, dim, vdim, n_ver, n_deg, var_s, method = solve_system(E, R, Rp, gens, eqs, 4)
        rec("probe", {"kind": "m4_planted", "F": fsize, "q": c["q"], "p": c["p"],
                      "build_s": float(build_s), "gb_s": float(gb_s),
                      "variety_s": float(var_s), "total_s": float(build_s + gb_s + var_s),
                      "d_reg": d_reg, "dim": dim, "vdim": vdim,
                      "n_verified": n_ver, "n_degenerate": n_deg, "method": method,
                      "peak_rss_bytes": peak_rss()})
        eprint(f"probe m4 F={fsize}: gb={gb_s:.2f}s d_reg={d_reg} vdim={vdim} ver={n_ver}/{n_ver+n_deg}")
def run_one_cell_curve(P, m, fsize, qlo, qhi, arm, cseed, role):
    """Build curve + FB + targets; returns dict with everything needed."""
    c = find_curve_with_subgroup(qlo, qhi, 16, seed=cseed)
    E = EllipticCurve(GF(c["p"]), [c["a4"], c["a6"]])
    G = subgroup_generator(E, c["q"], c["h"], cseed + 1)
    if arm == "random":
        xs, pts = fb_random(E, fsize, seed=cseed + 2)
    else:
        xs, pts = fb_interval(E, fsize, seed=cseed + 2)
    c.update({"role": role, "arm": arm, "m": m, "F": fsize})
    return c, E, G, xs, pts

def mode_cell(P):
    deadline = float(P.get("deadline_s", 520))
    m = int(P["m"]); fsize = int(P["F"])
    n_curves = int(P.get("curves", 3)); n_targets = int(P.get("targets", 8))
    arms = P.get("arms", "random,interval").split(",")
    seeds = [int(x) for x in P.get("seeds", "1,2,3").split(",")]
    n_nulls = int(P.get("nulls", 4))
    do_rho = int(P.get("rho", 1)); do_c3 = int(P.get("control3", 1))
    phases = P.get("phases", "solve,null,rho,control3").split(",")
    qlo = fsize ** m; qhi = int(ceil(1.15 * fsize ** m))
    skipped = []
    units_done = False
    for ci in range(n_curves):
        cseed = seeds[ci % len(seeds)] * 100 + ci
        for arm in arms:
            if "solve" not in phases: break
            c, E, G, xs, pts = run_one_cell_curve(P, m, fsize, qlo, qhi, arm,
                                                  cseed + (0 if arm == "random" else 500),
                                                  f"curve{ci}_{arm}")
            rec("curves", c)
            if not units_done:
                rec("units", measure_units(E, G)); units_done = True
            set_random_seed(cseed + 3)
            ks = [randint(1, c["q"] - 1) for _ in range(n_targets)]
            for ti, k in enumerate(ks):
                if elapsed() > deadline:
                    skipped.append(f"curve{ci}_{arm}_t{ti}+")
                    break
                R = k * G; xR = R.xy()[0]
                t0 = now()
                Rp, gens, eqs = build_system(E.base_field(), E.a4(), E.a6(), xs, xR, m)
                build_s = now() - t0
                gb_s, d_reg, dim, vdim, n_ver, n_deg, var_s, method = \
                    solve_system(E, R, Rp, gens, eqs, m)
                rec("solves", {"curve_id": c["seed"], "role": f"curve{ci}", "arm": arm,
                               "m": m, "F": fsize, "q": c["q"], "p": c["p"],
                               "target": ti, "k": int(k),
                               "build_s": float(build_s), "gb_s": float(gb_s),
                               "variety_s": float(var_s),
                               "total_s": float(build_s + gb_s + var_s),
                               "d_reg": d_reg, "dim": dim, "vdim": vdim,
                               "n_verified": n_ver, "n_degenerate": n_deg, "method": method,
                               "status": "solved" if n_ver > 0 else
                                         ("empty" if vdim == 0 else "no_verified_decomp")})
                eprint(f"cell F={fsize} m={m} c{ci} {arm} t{ti}: gb={gb_s:.2f}s "
                       f"d_reg={d_reg} vdim={vdim} ver={n_ver} deg={n_deg}")
            # rho control on the same instances (same curve + targets)
            if "rho" in phases and do_rho and arm == arms[0]:
                n_rho_done = 0
                for ti, k in enumerate(ks):
                    if elapsed() > deadline:
                        skipped.append(f"rho_curve{ci}_t{ti}+"); break
                    n_rho_done += 1
                    R = k * G
                    r = rho_dl(E, G, R, c["q"], seed=cseed * 10 + ti)
                    r.update({"curve_id": c["seed"], "role": f"curve{ci}",
                              "m": m, "F": fsize, "q": c["q"], "target": ti,
                              "k_true": int(k),
                              "const": r["ops"] / float(sqrt(c["q"])) if r.get("ops") else None})
                    rec("rho", r)
                eprint(f"cell F={fsize} c{ci}: rho done on {n_rho_done}/{len(ks)} targets")
        # control 3: same-order isogenous curve (from curve ci, once per curve)
        if "control3" in phases and do_c3:
            c0, E0, G0, xs0, pts0 = run_one_cell_curve(
                P, m, fsize, qlo, qhi, "random", cseed, f"curve{ci}_random")
            iso = None; ell_used = None
            for ell in primes(60):
                try:
                    cand = E0.isogenies_prime_degree(ell)
                except Exception:
                    cand = []
                if cand:
                    iso = cand[0]; ell_used = int(ell); break
            if iso is None:
                rec("control3", {"curve_id": c0["seed"], "status": "not_available",
                                 "reason": "no rational isogeny of degree < 60"})
            else:
                Ei = iso.codomain()
                if int(Ei.order()) != int(c0["order"]):
                    rec("control3", {"curve_id": c0["seed"], "status": "invalid",
                                     "reason": "isogeny codomain order mismatch"})
                else:
                    Gi = subgroup_generator(Ei, c0["q"], c0["h"], cseed + 7)
                    xsi, ptsi = fb_random(Ei, fsize, seed=cseed + 8)
                    set_random_seed(cseed + 9)
                    n_c3 = min(4, n_targets)
                    n_c3_done = 0
                    for ti in range(n_c3):
                        if elapsed() > deadline:
                            skipped.append(f"control3_curve{ci}_t{ti}+"); break
                        n_c3_done += 1
                        k = randint(1, c0["q"] - 1); R = k * Gi; xR = R.xy()[0]
                        t0 = now()
                        Rp, gens, eqs = build_system(Ei.base_field(), Ei.a4(), Ei.a6(),
                                                   xsi, xR, m)
                        build_s = now() - t0
                        gb_s, d_reg, dim, vdim, n_ver, n_deg, var_s, method = \
                            solve_system(Ei, R, Rp, gens, eqs, m)
                        rec("control3", {"curve_id": c0["seed"], "isogeny_degree": ell_used,
                                         "arm": "random", "m": m, "F": fsize, "q": c0["q"],
                                         "target": ti, "k": int(k),
                                         "build_s": float(build_s), "gb_s": float(gb_s),
                                         "variety_s": float(var_s),
                                         "total_s": float(build_s + gb_s + var_s),
                                         "d_reg": d_reg, "vdim": vdim,
                                         "n_verified": n_ver, "n_degenerate": n_deg, "method": method,
                                         "status": "solved" if n_ver > 0 else
                                                   ("empty" if vdim == 0 else "no_verified_decomp")})
                    eprint(f"cell F={fsize} c{ci}: control3 isogeny deg {ell_used}, {n_c3_done}/{n_c3} targets")
    # control 4: support-matched nulls, paired with curve0 random-arm systems
    if "null" in phases and n_nulls > 0:
        c0, E0, G0, xs0, pts0 = run_one_cell_curve(P, m, fsize, qlo, qhi, "random",
                                                   seeds[0] * 100, "curve0_random")
        set_random_seed(seeds[0] * 100 + 3)
        ks = [randint(1, c0["q"] - 1) for _ in range(min(n_nulls, n_targets))]
        for ti, k in enumerate(ks):
            if elapsed() > deadline:
                skipped.append(f"null_t{ti}+"); break
            R = k * G0; xR = R.xy()[0]
            Rp, gens, eqs = build_system(E0.base_field(), E0.a4(), E0.a6(), xs0, xR, m)
            neqs = [null_like(E0.base_field(), g, seed=99900 + 100 * ti + gi)
                    for gi, g in enumerate(eqs)]
            t0 = now()
            I = Rp.ideal(neqs)
            gb = I.groebner_basis()
            gb_s = now() - t0
            rec("nulls", {"m": m, "F": fsize, "q": c0["q"], "p": c0["p"], "target": ti,
                          "gb_s": float(gb_s), "d_reg": maxdeg(gb),
                          "peak_rss_bytes": peak_rss(), "status": "ok"})
            eprint(f"cell F={fsize} null t{ti}: gb={gb_s:.2f}s d_reg={maxdeg(gb)}")
    if skipped:
        note("deadline skipped: " + ",".join(skipped))

def mode_rho_ladder(P):
    deadline = float(P.get("deadline_s", 520))
    bits_list = [int(x) for x in P.get("bits", "20,24,28,30").split(",")]
    n_curves = int(P.get("curves", 3)); n_targets = int(P.get("targets", 8))
    for bits in bits_list:
        qlo = 2 ** bits; qhi = int(1.15 * 2 ** bits)
        for ci in range(n_curves):
            if elapsed() > deadline:
                note(f"rho_ladder deadline at bits={bits} curve{ci}"); return
            c = find_curve_with_subgroup(qlo, qhi, 16, seed=400 + bits * 10 + ci)
            E = EllipticCurve(GF(c["p"]), [c["a4"], c["a6"]])
            G = subgroup_generator(E, c["q"], c["h"], c["seed"] + 1)
            rec("curves", dict(c, role=f"rho_ladder_bits{bits}_curve{ci}", bits=bits))
            set_random_seed(c["seed"] + 3)
            for ti in range(n_targets):
                k = randint(1, c["q"] - 1); R = k * G
                r = rho_dl(E, G, R, c["q"], seed=c["seed"] * 10 + ti)
                r.update({"curve_id": c["seed"], "bits": bits, "q": c["q"], "target": ti,
                          "k_true": int(k),
                          "const": r["ops"] / float(sqrt(c["q"])) if r.get("ops") else None})
                rec("rho", r)
            eprint(f"rho_ladder bits={bits} curve{ci} done (q={c['q']})")

def mode_censor_doc(P):
    """Documented censorship attempts at spec-scale design points: build the
    system (relation_cost measurable), then attempt the GB under the external
    timeout; the attempt record is written BEFORE the GB starts."""
    m = int(P["m"]); fsize = int(P["F"]); bits = int(P.get("qbits", 20))
    c = find_curve_with_subgroup(2 ** bits, int(1.15 * 2 ** bits), 16, seed=777)
    E = EllipticCurve(GF(c["p"]), [c["a4"], c["a6"]])
    G = subgroup_generator(E, c["q"], c["h"], 778)
    rec("curves", dict(c, role="censor_doc", m=m, F=fsize, bits=bits))
    xs, pts = fb_random(E, fsize, seed=779)
    set_random_seed(780)
    k = randint(1, c["q"] - 1); R = k * G; xR = R.xy()[0]
    t0 = now()
    Rp, gens, eqs = build_system(E.base_field(), E.a4(), E.a6(), xs, xR, m)
    build_s = now() - t0
    rec("attempts", {"m": m, "F": fsize, "q": c["q"], "p": c["p"], "k": int(k),
                     "build_s": float(build_s), "gb_status": "started",
                     "note": "GB started; external timeout expected to kill (censored)"})
    eprint(f"censor_doc m={m} F={fsize} q~2^{bits}: build={build_s:.2f}s, GB starting")
    I = Rp.ideal(eqs)
    t0 = now(); gb = I.groebner_basis(); gb_s = now() - t0
    # only reached if the solve unexpectedly completes inside the cap
    rec("attempts", {"m": m, "F": fsize, "q": c["q"], "gb_status": "completed",
                     "gb_s": float(gb_s), "d_reg": maxdeg(gb)})
    eprint(f"censor_doc m={m} F={fsize}: GB COMPLETED in {gb_s:.1f}s")

# ------------------------------------------------------------------ main
def main():
    global OUT
    args = sys.argv[1:]
    if not args:
        eprint("usage: sage R6_run.sage MODE out=PATH [k=v ...]"); sys.exit(2)
    mode = args[0]
    P = {}
    for a in args[1:]:
        if "=" in a:
            k, v = a.split("=", 1); P[k] = v
    OUT = P.get("out")
    STATE.update({
        "run_id": P.get("run_id", "UNNAMED"), "experiment_id": "EXP-R6-001",
        "mode": mode, "params": P,
        "command": "sage experiments/EXP-R6-001/R6_run.sage " + " ".join(args),
        "git": git_info(),
        "environment": {"sage_version": sage.version.version,
                        "python_version": sys.version.split()[0],
                        "platform": sys.platform, "machine": os.uname().machine},
        "timestamps": {"started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}})
    flush()
    eprint(f"mode={mode} params={P}")
    if mode == "probe": mode_probe(P)
    elif mode == "cell": mode_cell(P)
    elif mode == "rho_ladder": mode_rho_ladder(P)
    elif mode == "censor_doc": mode_censor_doc(P)
    else:
        eprint(f"unknown mode {mode}"); sys.exit(2)
    STATE["complete"] = True
    STATE["termination"] = "clean"
    STATE["timestamps"]["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    STATE["timestamps"]["wall_s"] = float(elapsed())
    STATE["resources"] = {"peak_rss_bytes": peak_rss()}
    flush()
    print(f"DONE wall={elapsed():.1f}s")

main()
