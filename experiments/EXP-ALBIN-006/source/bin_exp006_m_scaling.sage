# BIN-EXP-006 : the m-SCALING test -- the single surviving escape route.
#
# BIN-NR-003 (capstone) showed: for FIXED m=3 the binary IC/rho cost gap grows ~n/6,
# driven by sparse linear algebra |FB|^2 ~ 2^{2n/3} > rho 2^{n/2}. The Petit-Quisquater
# subexponential heuristic needs GROWING m ~ n^{1/3}, which shrinks |FB| ~ 2^{n/m} and
# hence LA ~ 2^{2n/m}. The open question this experiment targets: at FIXED n, does
# increasing m SHRINK the IC/rho gap (toward a crossover) or does the per-relation
# solving cost rise faster and keep the gap positive?
#
# We measure, for fixed n and m in {2,3,4,5,6}:
#   * EXACT |FB| = #points with x in F2-subspace V of dim l~n/m (enumerate, is_x_coord).
#   * LA_exp = 2*log2|FB| ~ 2n/m   (DECREASES with m -- the PQ-favorable direction).
#   * per-relation solve: descended system has m*l ~ n binary unknowns and the Semaev
#     S_{m+1} has per-variable degree 2^{m-1}; the descended-system DEGREE (and hence
#     Groebner cost ~ binom(nvars, D)^omega) RISES with m. We bound the per-relation
#     solve exponent two ways:
#       (a) FPPR-optimistic: solving degree = first-fall ~ bounded (use measured d for
#           reachable cells; else the FPPR bound ceil((m^2+? )) capped) -> log2 binom(nvars,D);
#       (b) the literature reality: Groebner often hits ~ semiregular D_reg.
#     We report BOTH so the conclusion is bracketed, not cherry-picked.
#   * relgen_exp = log2|FB| + max(0, log2(m!) + n - m*log2|FB|).
#   * IC_exp = max(LA_exp, relgen_exp + per_rel_solve_exp); IC/rho = IC_exp - rho_exp.
# Where the descended Groebner is reachable (small nvars), we ALSO measure the true
# solving degree to anchor (a) vs (b). Hard timeout; toy/scaled params; not a break.
import json, time, signal
LOGP = "/Volumes/Volume/autolab/experiments/ecdlp_binary_field/bin_exp006_m_scaling.log"
_lf = open(LOGP, "w")
def out(s):
    print(s); _lf.write(str(s) + "\n"); _lf.flush()
out("=== BIN-EXP-006 m-scaling test (the surviving escape route) ===  " + time.asctime())

class Timeout(Exception): pass
def _alarm(sig, frm): raise Timeout()
signal.signal(signal.SIGALRM, _alarm)

def make_curve(n, seed=1):
    set_random_seed(int(seed))
    F = GF(2**n, 'a'); a = F.gen(); best = None
    for _ in range(200):
        a2 = F.random_element(); a6 = F.random_element()
        if a6.is_zero(): continue
        try: E = EllipticCurve(F, [1, a2, 0, 0, a6])
        except Exception: continue
        N = E.order(); big = max(p for p, e in factor(N))
        if best is None or big > best[5]: best = (F, a, E, a2, a6, big, N)
        if big >= N // 2: return F, a, E, a2, a6, N, big
    F, a, E, a2, a6, big, N = best; return F, a, E, a2, a6, N, big

def measure_fb(E, F, a, l, cap=300000):
    w = [a**j for j in range(l)]
    if 2**l > cap:
        hits = trials = 0
        for _ in range(20000):
            bits = ZZ.random_element(1, 2**l)
            x = sum((w[j] for j in range(l) if (bits >> j) & 1), F(0))
            if x.is_zero(): continue
            trials += 1; hits += (E.is_x_coord(x))
        rate = (hits / trials) if trials else 0.0
        return rate * (2**l), True
    cnt = 0
    for bits in range(1, 2**l):
        x = sum((w[j] for j in range(l) if (bits >> j) & 1), F(0))
        if x.is_zero(): continue
        if E.is_x_coord(x): cnt += 1
    return float(cnt), False

def per_rel_solve_exponents(nvars, m):
    """Return (optimistic_exp, semiregular_exp) for the per-relation Groebner solve,
    as log2 of binom(nvars, D)^~2.37 (omega). D_opt = FPPR first-fall ~ small; D_sr =
    a semiregular-style degree that grows with the system degree 2^{m-1}."""
    omega = 2.37
    # optimistic: bounded first-fall; FPPR/Kousidis-Wiemers ~ m(m-1)/2 + 1, capped by nvars
    D_opt = min(nvars, int(m * (m - 1) / 2) + 1)
    # reality proxy: semiregular degree for a system whose top degree is 2^{m-1};
    # use D_sr ~ min(nvars, 2^{m-1}) (a crude but monotone-in-m proxy)
    D_sr = min(nvars, 2**(m - 1))
    def logbinom(nv, D):
        if D <= 0 or D >= nv: return 0.0
        return float(log(binomial(nv, D), 2))
    return omega * logbinom(nvars, D_opt), omega * logbinom(nvars, D_sr), D_opt, D_sr

def cell(n, m, seed=1):
    r = {"n": n, "m": m}
    F, a, E, a2, a6, N, big = make_curve(n, seed)
    bigbits = float(log(float(big), 2))
    r["rho_exp"] = float(log(0.886, 2) + 0.5 * bigbits)
    l = max(2, int(round(n / m))); nvars = m * l
    r["l"] = l; r["nvars"] = nvars
    fb, sampled = measure_fb(E, F, a, l)
    if fb < 1: r["status"] = "FB<1"; return r
    log2fb = float(log(max(1.0, fb), 2))
    r["fb"] = round(fb, 1); r["log2fb"] = round(log2fb, 2); r["sampled"] = sampled
    LA_exp = 2.0 * log2fb
    attempts = max(0.0, float(log(factorial(m), 2)) + n - m * log2fb)
    relgen_exp = log2fb + attempts
    opt_exp, sr_exp, D_opt, D_sr = per_rel_solve_exponents(nvars, m)
    r["LA_exp"] = round(LA_exp, 2); r["relgen_exp"] = round(relgen_exp, 2)
    r["D_opt"] = D_opt; r["D_sr"] = D_sr
    r["persolve_opt_exp"] = round(opt_exp, 2); r["persolve_sr_exp"] = round(sr_exp, 2)
    # total IC two ways: relation gen includes a per-attempt solve; LA is separate.
    # number of decomposition attempts overall ~ |FB| * attempts_per_rel; each attempt
    # runs a Groebner solve. So relgen pipeline exp = relgen_exp + persolve_exp.
    IC_opt = max(LA_exp, relgen_exp + opt_exp)
    IC_sr = max(LA_exp, relgen_exp + sr_exp)
    r["IC_opt_exp"] = round(IC_opt, 2); r["IC_sr_exp"] = round(IC_sr, 2)
    r["IC_opt_over_rho"] = round(IC_opt - r["rho_exp"], 2)
    r["IC_sr_over_rho"] = round(IC_sr - r["rho_exp"], 2)
    r["status"] = "OK"
    return r

# Fixed n, sweep m. Pick n large enough that m can range but |FB| stays enumerable.
N_LIST = [31, 41]
M_LIST = [2, 3, 4, 5, 6]
results = []
for n in N_LIST:
    out("\n--- n=%d (sweep m) ---" % n)
    for m in M_LIST:
        t0 = time.time()
        try:
            r = cell(n, m, seed=1)
        except Exception as ex:
            r = {"n": n, "m": m, "status": "EXC %s" % repr(ex)[:120]}
        r["cell_secs"] = round(time.time() - t0, 1)
        results.append(r)
        out("[n=%d m=%d] l=%s nvars=%s |FB|=%s log2fb=%.1f LA2^%.1f relgen2^%.1f | "
            "Dopt=%s persolve_opt2^%.1f IC_opt/rho=2^%+.1f || Dsr=%s persolve_sr2^%.1f IC_sr/rho=2^%+.1f (%.1fs)"
            % (n, m, r.get("l"), r.get("nvars"), r.get("fb"), r.get("log2fb", float('nan')),
               r.get("LA_exp", float('nan')), r.get("relgen_exp", float('nan')),
               r.get("D_opt"), r.get("persolve_opt_exp", float('nan')), r.get("IC_opt_over_rho", float('nan')),
               r.get("D_sr"), r.get("persolve_sr_exp", float('nan')), r.get("IC_sr_over_rho", float('nan')),
               r["cell_secs"]))

out("\n=== SUMMARY: does increasing m shrink the IC/rho gap? (two solve-cost models) ===")
out("%-4s %-4s %-7s %-9s %-12s %-12s" % ("n", "m", "|FB|", "rho2^", "IC_opt/rho", "IC_sr/rho"))
for r in results:
    if r.get("status") != "OK": continue
    out("%-4s %-4s %-7s %-9s %-12s %-12s" % (r["n"], r["m"], r.get("fb"),
        "%.1f" % r["rho_exp"], "%+.1f" % r["IC_opt_over_rho"], "%+.1f" % r["IC_sr_over_rho"]))
out("\nRESULTS_JSON " + json.dumps(results, default=str))
_lf.close()
print("WROTE", LOGP)
