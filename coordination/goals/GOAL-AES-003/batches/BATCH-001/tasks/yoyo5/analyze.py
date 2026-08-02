#!/usr/bin/env python3
"""Score every arm against the FROZEN pre-registered null (PREREGISTRATION.md
sections 3-4). No statistic is invented here that is not in the pre-registration:
Z ~ Binomial(16, 2^-8), W ~ Binomial(4, 2^-32).  Poisson tail for rare-event
counts.  Resolution in bits = log2(N/3)."""
import json, math, sys

def binom_pmf(n, k, p):
    return math.comb(n, k) * p**k * (1-p)**(n-k)

ZP = [binom_pmf(16, k, 1/256) for k in range(17)]
PW1 = 1 - (1 - 2**-32)**4          # P(W >= 1) under the PRP null

def pois_tail(k, lam):
    """P(X >= k) for Poisson(lam), exact-ish."""
    if k == 0: return 1.0
    s, term = 0.0, math.exp(-lam)
    for i in range(0, k):
        s += term
        term *= lam / (i+1)
    return max(0.0, 1.0 - s)

def chi2_z(zh, N):
    """Pearson chi-square of the Z histogram against Binomial(16,2^-8),
    bins pooled so that every expected count >= 25."""
    obs, exp, o, e = [], [], 0.0, 0.0
    for k in range(17):
        o += zh[k]; e += N*ZP[k]
        if e >= 25:
            obs.append(o); exp.append(e); o = e = 0.0
    if o or e:
        if obs: obs[-1] += o; exp[-1] += e
    x2 = sum((a-b)**2/b for a, b in zip(obs, exp))
    return x2, len(obs)-1, obs, exp

def report(d):
    N = d["trials"]; r = d["rounds"]
    zh, wh = d["zhist"], d["whist"]
    res = math.log2(N/3)
    out = {
        "rounds": r, "amask": d["amask"], "smask": d["smask"], "seed": d["seed"],
        "trials": N, "resolution_bits": round(res, 2), "seconds": d["seconds"],
        "zhist": zh, "whist": wh,
    }
    x2, dof, obs, exp = chi2_z(zh, N)
    out["Z_chi2"] = round(x2, 2); out["Z_dof"] = dof
    out["Z_expected_pooled"] = [round(e, 1) for e in exp]
    out["Z_observed_pooled"] = [int(o) for o in obs]
    wge1 = N - wh[0]
    lam = N * PW1
    out["W_ge1_observed"] = wge1
    out["W_ge1_expected_under_PRP_null"] = round(lam, 3)
    out["W_ge1_poisson_tail_p"] = pois_tail(wge1, lam)
    out["W_ge1_excess_factor"] = (wge1/lam) if lam else None
    for k in ("trivial_swaps", "whist_nontrivial", "ct_zero_words_hist",
              "W1_word_index", "xtab_ctzerowords_by_W"):
        if k in d: out[k] = d[k]
    if "whist_nontrivial" in d:
        nt = d["whist_nontrivial"]
        ntge1 = sum(nt[1:])
        Nnt = N - d["trivial_swaps"]
        lam_nt = Nnt * PW1
        out["W_ge1_nontrivial_observed"] = ntge1
        out["W_ge1_nontrivial_expected"] = round(lam_nt, 3)
        out["W_ge1_nontrivial_poisson_tail_p"] = pois_tail(ntge1, lam_nt)
    return out

rows = []
for path in sys.argv[1:]:
    for line in open(path):
        line = line.strip()
        if not line.startswith("{"): continue
        rows.append(report(json.loads(line)))
print(json.dumps(rows, indent=1))
