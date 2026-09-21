#!/usr/bin/env python3
"""TASK-20260803-a0a7b9 analysis. No scipy on this host; every exact interval
below is computed from lgamma-based CDFs by bisection, and the machinery is
self-checked by reproducing EV-AES-8b8dcf OBS-B8-3's published [2.13, 592]
from its published counts (14 vs 1) before it is used on anything new."""
import json, math, os, sys

D = os.path.dirname(os.path.abspath(__file__))
R = os.path.join(D, "runs")
B8 = ("/home/user/crypto-autoresearcher/coordination/goals/GOAL-AES-003/"
      "batches/BATCH-008/tasks/TASK-20260803-05e072/runs")

# ---------------------------------------------------------------- exact stats
def pois_cdf(k, lam):          # P(X <= k)
    if lam <= 0: return 1.0
    if k < 0: return 0.0
    s, t = 0.0, math.exp(-lam)
    for i in range(int(k) + 1):
        if i: t *= lam / i
        s += t
    return min(s, 1.0)

def pois_sf_ge(k, lam):        # P(X >= k)
    return 1.0 - pois_cdf(k - 1, lam)

def _root(g, lo, hi, it=300):
    """Bisect a continuous monotone g on [lo,hi] with g(lo), g(hi) of opposite
    sign. Returns the root. Asserts the bracket rather than silently returning
    a wrong endpoint -- the first version of this helper did exactly that and
    produced a nonsense lower bound, which the OBS-B8-3 self-check caught."""
    glo, ghi = g(lo), g(hi)
    assert glo * ghi <= 0, "bad bracket: g(%g)=%g g(%g)=%g" % (lo, glo, hi, ghi)
    for _ in range(it):
        mid = 0.5 * (lo + hi)
        if g(lo) * g(mid) <= 0: hi = mid
        else: lo = mid
    return 0.5 * (lo + hi)

def poisson_exact_ci(x, alpha=0.05):
    """Garwood exact CI for the Poisson mean given count x.
    lower solves P(X >= x | L) = alpha/2  (increasing in L)
    upper solves P(X <= x | U) = alpha/2  (decreasing in U)"""
    a = alpha / 2.0
    hi_b = max(10.0, x * 4.0 + 50.0)
    lo = 0.0 if x == 0 else _root(lambda L: pois_sf_ge(x, L) - a, 0.0, hi_b)
    hi = _root(lambda U: pois_cdf(x, U) - a, 0.0, hi_b)
    return lo, hi

def lchoose(n, k):
    return math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)

def binom_cdf(k, n, p):
    if p <= 0: return 1.0
    if p >= 1: return 1.0 if k >= n else 0.0
    s = 0.0
    for i in range(int(k) + 1):
        s += math.exp(lchoose(n, i) + i * math.log(p) + (n - i) * math.log1p(-p))
    return min(s, 1.0)

def binom_pmf(i, n, p):
    if p <= 0: return 1.0 if i == 0 else 0.0
    if p >= 1: return 1.0 if i == n else 0.0
    return math.exp(lchoose(n, i) + i * math.log(p) + (n - i) * math.log1p(-p))

def clopper_pearson(x, n, alpha=0.05):
    if n == 0: return (0.0, 1.0)
    a = alpha / 2.0
    lo = 0.0 if x == 0 else _root(
        lambda p: (1.0 - binom_cdf(x - 1, n, p)) - a, 0.0, 1.0)
    hi = 1.0 if x == n else _root(
        lambda p: binom_cdf(x, n, p) - a, 0.0, 1.0)
    return lo, hi

def binom_exact_two_sided_p(x, n, p0):
    """Exact two-sided binomial test, minimum-likelihood (Sterne/'small-p')
    convention: sum the probabilities of every outcome no more likely than the
    observed one. This is the convention that returns 9.77e-4 for 14/15."""
    obs = binom_pmf(x, n, p0)
    tot = 0.0
    for i in range(n + 1):
        pi = binom_pmf(i, n, p0)
        if pi <= obs * (1 + 1e-9): tot += pi
    return min(tot, 1.0)

def poisson_ratio(xA, mA, xB, mB, alpha=0.05):
    """Exact conditional-binomial comparison of two Poisson rates.
    Returns the two-sided p for rate_A == rate_B and an exact CI for
    theta = rate_A / rate_B."""
    n = xA + xB
    if n == 0:
        return dict(p_value=None, ratio_point=None, ratio_ci=[None, None], n=0)
    p0 = mA / (mA + mB)
    p = binom_exact_two_sided_p(xA, n, p0)
    pl, pu = clopper_pearson(xA, n, alpha)
    f = mB / mA
    def odds(q): return float('inf') if q >= 1 else (q / (1 - q)) * f
    point = odds(xA / n)
    return dict(p_value=p, ratio_point=point, ratio_ci=[odds(pl), odds(pu)],
                n=n, p0_null=p0, cp_p_ci=[pl, pu])

# ---------------------------------------------------------------- self-check
SELFCHECK = poisson_ratio(14, 1.0, 1, 1.0)
selfcheck_ok = (abs(SELFCHECK["p_value"] - 9.77e-4) < 5e-6 and
                abs(SELFCHECK["ratio_ci"][0] - 2.13) < 0.02 and
                abs(SELFCHECK["ratio_ci"][1] - 592.0) < 6.0)

# ---------------------------------------------------------------- load arms
def load(p):
    with open(p) as fh: return json.load(fh)

arms = {}
for n in ("P1-R5-PAIR", "N1-IDEAL-P30", "P2-R10-PAIR", "N2-IDEAL-P33",
          "SMOKE-IDEAL", "SMOKE-AES"):
    f = os.path.join(R, n + ".json")
    if os.path.exists(f):
        try: arms[n] = load(f)
        except Exception as e: arms[n] = {"_parse_error": str(e)}
b8 = {n: load(os.path.join(B8, n + ".json"))
      for n in ("K-EQUIV-R5-K1-A2", "K-R10-NULL-P30")
      if os.path.exists(os.path.join(B8, n + ".json"))}

# ---------------------------------------------------------------- equivalence
V3_FIELDS = ["sbox_spec", "sbox_seed", "sbox_bijective", "sbox_first8", "rounds",
             "amask", "smask", "trials", "log2N", "seed", "arm_id", "threads",
             "key_hex", "thread_seeds", "trivial_swaps_excluded",
             "nontrivial_trials", "W_ge1_nontrivial", "W_ge1_by_word", "whist",
             "null_expectation_analytic", "W_ge1_prefix_k",
             "prefix_k4_equals_W_ge1", "null_expectation_prefix_k_exact"]

def equiv(newname, oldname):
    if newname not in arms or oldname not in b8:
        return {"status": "NOT RUN", "new": newname, "old": oldname}
    a, o = arms[newname], b8[oldname]
    rows, ok = [], True
    for k in V3_FIELDS:
        m = a.get(k) == o.get(k)
        ok &= m
        rows.append({"field": k, "match": m, "v4": a.get(k), "v3": o.get(k)})
    return {"status": "BIT-EXACT" if ok else "MISMATCH", "new": newname,
            "old": oldname, "all_v3_fields_match": ok, "fields": rows,
            "v4_only_keys": sorted(set(a) - set(o))}

# ---------------------------------------------------------------- null object
def prefix_check(a):
    obs, exp = a["W_ge1_prefix_k"], a["null_expectation_prefix_k_exact"]
    out = []
    for k in range(3):                     # gate is on k = 1,2,3 only
        z = (obs[k] - exp[k]) / math.sqrt(exp[k]) if exp[k] > 0 else None
        out.append({"k": k + 1, "observed": obs[k], "expected_exact": exp[k],
                    "z": z, "gate_abs_z_le_4": (z is not None and abs(z) <= 4)})
    return out

def null_reading(name):
    if name not in arms: return {"status": "NOT RUN", "arm": name}
    a = arms[name]
    x, m = a["W_ge1_nontrivial"], a["null_expectation_analytic"]
    lo, hi = poisson_exact_ci(x)
    pk = prefix_check(a)
    return {
        "arm": name, "cipher_model": a["cipher_model"],
        "trials": a["trials"], "nontrivial_trials": a["nontrivial_trials"],
        "W_ge1_nontrivial_MEASURED": x,
        "analytic_null_expectation_MODELED": m,
        "rate_ratio_R_null_point": x / m,
        "rate_ratio_R_null_exact_95CI": [lo / m, hi / m],
        "count_exact_95CI": [lo, hi],
        "ci_contains_1": (lo / m) <= 1.0 <= (hi / m),
        "ci_lower_exceeds_1": (lo / m) > 1.0,
        "prefix_selfpin_k123": pk,
        "prefix_selfpin_pass": all(r["gate_abs_z_le_4"] for r in pk),
        "stream_gap_min_log2": a["stream_gap_min_log2"],
        "stream_gap_gate_gt_2^40": a["stream_gap_min_steps"] > 2 ** 40,
        "injectivity_redraws": a["ideal_injectivity_redraws"],
        "hit_log_overflow": a["hit_log_overflow"],
        "plaintext_stream_digest": a["plaintext_stream_digest"],
    }

# ---------------------------------------------------------------- RC-11
def rc11():
    if "P1-R5-PAIR" not in arms or "P2-R10-PAIR" not in arms:
        return {"status": "NOT RUN"}
    a, b = arms["P1-R5-PAIR"], arms["P2-R10-PAIR"]
    dig_match = a["plaintext_stream_digest"] == b["plaintext_stream_digest"]
    A = set(tuple(h) for h in a["hit_trials"])
    B = set(tuple(h) for h in b["hit_trials"])
    n11, n10, n01 = len(A & B), len(A - B), len(B - A)
    N = a["nontrivial_trials"]
    n00 = N - n11 - n10 - n01
    disc = n10 + n01
    p_mcnemar = binom_exact_two_sided_p(n10, disc, 0.5) if disc else None
    if disc:
        pl, pu = clopper_pearson(n10, disc)
        f = lambda q: float('inf') if q >= 1 else q / (1 - q)
        ci = [f(pl), f(pu)]
        pt = f(n10 / disc)
    else:
        ci, pt = [None, None], None
    unp = poisson_ratio(a["W_ge1_nontrivial"], a["nontrivial_trials"],
                        b["W_ge1_nontrivial"], b["nontrivial_trials"])
    return {
        "pairing_is_real_digest_match": dig_match,
        "plaintext_stream_digest_r5": a["plaintext_stream_digest"],
        "plaintext_stream_digest_r10": b["plaintext_stream_digest"],
        "hit_trials_r5": sorted(A), "hit_trials_r10": sorted(B),
        "hit_log_overflow_r5": a["hit_log_overflow"],
        "hit_log_overflow_r10": b["hit_log_overflow"],
        "table_2x2": {"n11_hit_in_both": n11, "n10_r5_only": n10,
                      "n01_r10_only": n01, "n00_neither": n00,
                      "paired_trials": N},
        "discordant_pairs": disc,
        "mcnemar_exact_two_sided_p": p_mcnemar,
        "paired_rate_ratio_point": pt,
        "paired_rate_ratio_exact_95CI": ci,
        "unpaired_recomputed_here": {
            "two_sided_p": unp["p_value"], "ratio_point": unp["ratio_point"],
            "ratio_ci": unp["ratio_ci"]},
        "published_unpaired_OBS_B8_3": {"p": 9.77e-4, "ratio_ci": [2.13, 592]},
        "paired_vs_unpaired_interval_identical": (
            ci[0] is not None and unp["ratio_ci"][0] is not None and
            abs(ci[0] - unp["ratio_ci"][0]) < 1e-6 and
            abs(ci[1] - unp["ratio_ci"][1]) < 1e-3),
        "per_thread_hit_counts_r5": {str(t): sum(1 for h in A if h[0] == t)
                                     for t in sorted({h[0] for h in A})},
    }

# ---------------------------------------------------------------- outcome rule
def decide():
    n1 = null_reading("N1-IDEAL-P30")
    n2 = null_reading("N2-IDEAL-P33")
    if "status" in n1: return {"outcome": "NOT REACHED", "reason": "N1 not run"}, n1, n2
    r5 = arms.get("P1-R5-PAIR")
    if not r5: return {"outcome": "NOT REACHED", "reason": "P1 not run"}, n1, n2
    cmp5 = poisson_ratio(r5["W_ge1_nontrivial"], r5["nontrivial_trials"],
                         arms["N1-IDEAL-P30"]["W_ge1_nontrivial"],
                         arms["N1-IDEAL-P30"]["nontrivial_trials"])
    cmp5b = None
    if "N2-IDEAL-P33" in arms:
        cmp5b = poisson_ratio(r5["W_ge1_nontrivial"], r5["nontrivial_trials"],
                              arms["N2-IDEAL-P33"]["W_ge1_nontrivial"],
                              arms["N2-IDEAL-P33"]["nontrivial_trials"])
    contains1 = n1["ci_contains_1"]
    lower_gt1 = n1["ci_lower_exceeds_1"]
    rejects = cmp5["p_value"] is not None and cmp5["p_value"] < 0.01
    if contains1 and rejects:      out = "OUTCOME-A"
    elif lower_gt1 and not rejects: out = "OUTCOME-B"
    else:                           out = "OUTCOME-C"
    return {"outcome": out,
            "r5_vs_nullobject_matched_exposure": cmp5,
            "r5_vs_nullobject_highprecision": cmp5b}, n1, n2

if __name__ == "__main__":
    dec, n1, n2 = decide()
    print(json.dumps({
        "selfcheck_reproduces_OBS_B8_3": {"ok": selfcheck_ok, **SELFCHECK},
        "equivalence_r5": equiv("P1-R5-PAIR", "K-EQUIV-R5-K1-A2"),
        "equivalence_r10": equiv("P2-R10-PAIR", "K-R10-NULL-P30"),
        "null_object_N1": n1, "null_object_N2": n2,
        "decision": dec, "rc11": rc11(),
    }, indent=1, default=str))
