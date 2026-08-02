# BIN-EXP-005 : binary IC cost-balance capstone (the binary analog of prime NR-026).
#
# BIN-EXP-004 showed plain Groebner descent is unreachable past n~17 (degree-6
# descended system blows up). But the question that decides whether binary IC beats
# rho is NOT the per-relation solve degree alone -- it is the WHOLE-PIPELINE cost,
# dominated by sparse linear algebra ~ |FB|^2 and relation generation ~ |FB| * (solve).
# That balance is curve-only (no Groebner), so it scales to realistic n.
#
# We MEASURE the real |FB| = #{points with x in an F2-subspace V of dim l} for several
# (n, l) -- not the heuristic 2^l -- and report:
#   rho_exp   = log2(0.886 * sqrt(prime_subgroup))            [Pollard rho group ops]
#   relgen    : need ~ |FB| relations; each random R decomposes into m FB-points with
#               prob ~ |FB|^m / (m! * #E) ; #attempts/relation ~ m! * #E / |FB|^m,
#               so relation-generation field-op exponent ~ log2(|FB|) + log2(attempts).
#   LA_exp    = 2*log2(|FB|)                                  [sparse linear algebra]
#   IC_exp    = max(LA_exp, relgen_total_exp)                 [dominant IC stage]
#   IC/rho    = IC_exp - rho_exp   ( > 0 => IC worse than rho )
# Optimal l ~ n/m balances per-relation cost vs relation count; we sweep l around n/m.
# This is an ANALYTIC-with-MEASURED-|FB| capstone, clearly labelled; no toy solve is
# presented as a real break.
import json, time
LOGP = "/Volumes/Volume/autolab/experiments/ecdlp_binary_field/bin_exp005_cost_balance.log"
_lf = open(LOGP, "w")
def out(s):
    print(s); _lf.write(str(s) + "\n"); _lf.flush()
out("=== BIN-EXP-005 binary IC cost-balance capstone ===  " + time.asctime())

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

def measure_fb(E, F, a, l, cap=200000):
    """exact |FB| = #points with x in V=span(a^0..a^{l-1}); enumerate 2^l x-values."""
    w = [a**j for j in range(l)]
    cnt = 0
    if 2**l > cap:   # too big to enumerate exactly; sample to estimate the rate
        import random as _r
        hits = trials = 0
        for _ in range(20000):
            bits = ZZ.random_element(1, 2**l)
            x = sum((w[j] for j in range(l) if (bits >> j) & 1), F(0))
            if x.is_zero(): continue
            trials += 1
            hits += (E.is_x_coord(x))
        rate = (hits / trials) if trials else 0.0
        return None, float(rate), True   # (exact=None, hit_rate, sampled)
    for bits in range(1, 2**l):
        x = sum((w[j] for j in range(l) if (bits >> j) & 1), F(0))
        if x.is_zero(): continue
        if E.is_x_coord(x): cnt += 1
    return cnt, (cnt / float(2**l - 1)), False

def cell(n, m=3, seed=1):
    r = {"n": n, "m": m}
    F, a, E, a2, a6, N, big = make_curve(n, seed)
    bigbits = float(log(float(big), 2))
    r["subgroup_bits"] = bigbits
    r["rho_exp"] = float(log(0.886, 2) + 0.5 * bigbits)
    best = None
    for l in [max(2, int(round(n/m)) + d) for d in (-1, 0, 1, 2)]:
        if l < 2: continue
        t0 = time.time()
        exact, rate, sampled = measure_fb(E, F, a, l)
        # estimate |FB|: exact if enumerated, else rate * 2^l
        fb = exact if exact is not None else (rate * (2**l))
        if fb is None or fb < 1: continue
        log2fb = float(log(max(1.0, fb), 2))
        # relation generation: attempts/relation ~ m! * #E / |FB|^m ; #E ~ 2^n
        #   need |FB| relations total.
        attempts_per_rel_exp = float(log(factorial(m), 2)) + n - m * log2fb
        attempts_per_rel_exp = max(0.0, attempts_per_rel_exp)
        relgen_exp = log2fb + attempts_per_rel_exp     # |FB| rels * attempts each (per-attempt ~O(1) field ops, lower bound)
        LA_exp = 2.0 * log2fb
        IC_exp = max(LA_exp, relgen_exp)
        cand = {"l": l, "fb": (int(exact) if exact is not None else round(fb, 1)),
                "sampled": sampled, "log2fb": round(log2fb, 2),
                "attempts_per_rel_exp": round(attempts_per_rel_exp, 2),
                "relgen_exp": round(relgen_exp, 2), "LA_exp": round(LA_exp, 2),
                "IC_exp": round(IC_exp, 2), "IC_over_rho": round(IC_exp - r["rho_exp"], 2),
                "secs": round(time.time() - t0, 1)}
        if best is None or cand["IC_exp"] < best["IC_exp"]:
            best = cand
    r["best"] = best
    return r

GRID = [11, 13, 17, 19, 23, 29, 31, 37, 41, 47, 53, 61]
results = []
for n in GRID:
    t0 = time.time()
    try:
        r = cell(n, m=3, seed=1)
    except Exception as ex:
        r = {"n": n, "status": "EXC %s" % repr(ex)[:120]}
    r["cell_secs"] = round(time.time() - t0, 1)
    results.append(r)
    b = r.get("best", {}) or {}
    out("[n=%2d] subgrp_bits=%.1f rho2^%.1f | best l=%s |FB|=%s log2fb=%.1f relgen2^%.1f LA2^%.1f IC2^%.1f IC/rho=2^%+.1f (%.1fs)"
        % (n, r.get("subgroup_bits", float('nan')), r.get("rho_exp", float('nan')),
           b.get("l"), b.get("fb"), b.get("log2fb", float('nan')), b.get("relgen_exp", float('nan')),
           b.get("LA_exp", float('nan')), b.get("IC_exp", float('nan')), b.get("IC_over_rho", float('nan')),
           r["cell_secs"]))

out("\n=== SUMMARY: optimized binary IC cost vs rho (m=3, |FB| measured) ===")
out("%-4s %-9s %-9s %-9s %-10s" % ("n", "rho2^", "IC2^", "IC/rho2^", "(>0 = IC worse)"))
for r in results:
    b = r.get("best", {}) or {}
    out("%-4s %-9s %-9s %-9s" % (r.get("n"),
        ("%.1f" % r["rho_exp"]) if "rho_exp" in r else "-",
        ("%.1f" % b["IC_exp"]) if b.get("IC_exp") is not None else "-",
        ("%+.1f" % b["IC_over_rho"]) if b.get("IC_over_rho") is not None else "-"))
out("\nRESULTS_JSON " + json.dumps(results, default=str))
_lf.close()
print("WROTE", LOGP)
