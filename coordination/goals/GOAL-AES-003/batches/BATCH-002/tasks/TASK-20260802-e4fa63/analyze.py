# Analysis for TASK-20260802-e4fa63. Exact Poisson / conditional-binomial arithmetic
# in integer-exact rational form where feasible; no scipy dependency.
import json, math, sys
from fractions import Fraction

P_W_GE1 = Fraction(4, 2**32)   # analytic PRP null: W ~ Binomial(4, 2^-32) -> P(W>=1) = 2^-30 (first-order)
# exact: 1-(1-2^-32)^4
P_EXACT = 1 - (1 - Fraction(1,2**32))**4

def pois_tail_ge(k, lam):
    """P(X >= k) for Poisson(lam). Summed upward in log space so that extreme
    tails are not lost to the 1-x floor of double precision."""
    if k <= 0: return 1.0
    logt = -lam + k*math.log(lam) - math.lgamma(k+1)
    tot = 0.0; i = k; t = 1.0
    while t > 1e-18 and i < k + 10000:
        tot += t
        i += 1
        t *= lam/i
    return math.exp(logt) * tot if logt > -700 else 0.0

def pois_log10_tail_ge(k, lam):
    """log10 P(X >= k) for Poisson(lam), valid far below the double floor."""
    if k <= 0: return 0.0
    logt = -lam + k*math.log(lam) - math.lgamma(k+1)
    tot = 0.0; i = k; t = 1.0
    while t > 1e-18 and i < k + 10000:
        tot += t; i += 1; t *= lam/i
    return (logt + math.log(tot))/math.log(10)

def two_sample_conditional(k1, n1, k2, n2):
    """Exact conditional test that arm-1 and arm-2 rates are equal.
    Conditional on the total k1+k2, k1 ~ Binomial(k1+k2, n1/(n1+n2)).
    Returns P(K >= k1) exactly as a Fraction, plus its float and log10."""
    k = k1 + k2
    p = Fraction(n1, n1 + n2)
    tot = Fraction(0)
    for i in range(k1, k + 1):
        tot += Fraction(math.comb(k, i)) * p**i * (1 - p)**(k - i)
    f = float(tot)
    try:
        l10 = math.log10(tot.numerator) - math.log10(tot.denominator)
    except (ValueError, OverflowError):
        l10 = (math.log(tot.numerator) - math.log(tot.denominator))/math.log(10) \
              if tot.numerator else float('-inf')
    return {"p_exact_float": f, "log10_p": l10,
            "note": "exact conditional binomial two-sample Poisson rate test"}

def pois_interval(lam, conf=0.99):
    """two-sided equal-tail conf interval on a Poisson count of mean lam"""
    a = (1-conf)/2
    lo = 0
    # smallest lo with P(X <= lo) > a  -> lower bound is largest k with P(X<=k-1) <= a
    c = 0.0; term = math.exp(-lam); k = 0; lower = 0
    while True:
        c += term
        if c > a and lower == 0 and k >= 0:
            lower = k; break
        term *= lam/(k+1); k += 1
        if k > 10000: lower = k; break
    c = 0.0; term = math.exp(-lam); k = 0
    while True:
        c += term
        if c >= 1-a:
            upper = k; break
        term *= lam/(k+1); k += 1
        if k > 10000: upper = k; break
    return (max(0,lower-1) if lower>0 else 0, upper)

def binom_tail_ge(k, n, p):
    """P(X >= k), X~Bin(n,p), exact rational then float."""
    if k <= 0: return 1.0
    tot = Fraction(0)
    P = Fraction(p)
    for i in range(k, n+1):
        tot += Fraction(math.comb(n, i)) * P**i * (1-P)**(n-i)
    return float(tot)

def load(name):
    try:
        return json.load(open("arm_%s.json" % name))
    except Exception as e:
        return None

def summarize(a):
    N = a["nontrivial_trials"]
    obs = a["W_ge1_nontrivial"]
    lam = float(N) * float(P_EXACT)
    lo, hi = pois_interval(lam, 0.99)
    return {
        "arm": a["arm"], "rounds": a["rounds"], "amask": a["amask"], "smask": a["smask"],
        "trials": a["trials"], "log2N": a["log2N"], "seed": a["seed"], "arm_id": a["arm_id"],
        "key_hex": a["key_hex"], "thread_seeds": a["thread_seeds"],
        "trivial_swaps_excluded": a["trivial_swaps_excluded"],
        "nontrivial_trials": N,
        "W_ge1_observed": obs,
        "W_ge1_expected_analytic_PRP_null": lam,
        "excess_factor_vs_analytic": (obs/lam if lam else None),
        "poisson_99pct_interval_under_analytic_null": [lo, hi],
        "poisson_tail_p_ge_obs_under_analytic_null": pois_tail_ge(obs, lam),
        "poisson_log10_tail_p_ge_obs_under_analytic_null": pois_log10_tail_ge(obs, lam),
        "resolution_bits": math.log2(N/3.0),
        "whist": a["whist"], "zhist": a["zhist"], "W_ge1_by_word": a["W_ge1_by_word"],
    }

def zchi2(a):
    """chi-square of Z histogram against Binomial(16, 2^-8), pooling the tail."""
    N = a["nontrivial_trials"]; zh = a["zhist"]
    exp = [N*math.comb(16,k)*(2**-8)**k*(1-2**-8)**(16-k) for k in range(17)]
    obs_p, exp_p = [], []
    acc_o = acc_e = 0.0
    for k in range(17):
        acc_o += zh[k]; acc_e += exp[k]
        if acc_e >= 5.0:
            obs_p.append(acc_o); exp_p.append(acc_e); acc_o = acc_e = 0.0
    if acc_e > 0:
        if exp_p: obs_p[-1]+=acc_o; exp_p[-1]+=acc_e
        else: obs_p.append(acc_o); exp_p.append(acc_e)
    chi = sum((o-e)**2/e for o,e in zip(obs_p,exp_p))
    return {"chi2": chi, "dof": len(obs_p)-1,
            "observed_pooled": obs_p, "expected_pooled": exp_p}

if __name__ == "__main__":
    out = {}
    for nm in sys.argv[1:]:
        a = load(nm)
        if a is None:
            out[nm] = {"status": "not_run_or_unreadable"}
            continue
        s = summarize(a); s["Z_goodness_of_fit_vs_binomial_16_2e-8"] = zchi2(a)
        out[nm] = s
    print(json.dumps(out, indent=1))
