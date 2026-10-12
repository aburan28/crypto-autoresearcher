"""J-PDI9: the A-TAIL secondary tail screen under both means. TASK-20261009-33b5cf.
Standard library only; no producer code.

For every arm analysis.json reports poisson_tail_lt_1e-4 for (small_x, small_x_offset;
the TT per-curve count n_{A,j} of the J-VAL recount), list the curves with
P(Poisson(mu_j) >= n_{A,j}) < 1e-4 under
  (a) mu_j = mu_model(j), the uncalibrated model mean EXP-PFDR-011cd0 A-TAIL uses
      (design.json curves[].mu_model, TT at m = 4);
  (b) mu_j = rho1_hat_b x mu_model(j), the calibrated null mean PDI-9 uses
      (calibration.json rho1_hat_b of RA-05);
and their symmetric difference; compare with analysis.json. Margin: per arm and mean,
the smallest tail probability over curves, and the smallest factor f by which the
mean of some curve would have to be multiplied (f < 1) for that curve to be listed
(bisection on f in (0, 1]); this says how far the list is from depending on the mean.
Sanity link: harvester TT poisson_mean / 3 == mu_model (generic TT multiplicity 3, L2).
Supplementary (not in the plan): the TB screen that metrics.secondary also names
("TB counts of every arm ... Poisson tail screen as A-TAIL"), which analysis.json does
not report: TB counts from the J-VAL recount (PDI-3 reading), mean = harvester TB
poisson_mean / 3 (ASSUMPTION: generic TB multiplicity 3 at arity 2, L2), every arm.
No seeds. Usage: python pdi9.py <repo> <percurve.jsonl.gz> <out.json>
"""
import gzip
import json
import math
import os
import sys

RUNS = "experiments/EXP-PFDR-0b3699/runs"


def sf(n, mu):
    """P(Poisson(mu) >= n), exact summation (n small)."""
    if n <= 0:
        return 1.0
    term = math.exp(-mu)
    cdf = term
    for i in range(1, n):
        term *= mu / i
        cdf += term
    return max(0.0, 1.0 - cdf)


def sf_tail(n, mu):
    """Same, as a direct upper-tail sum (better relative accuracy for tiny values)."""
    if n <= 0:
        return 1.0
    term = math.exp(-mu) * mu ** n / math.factorial(n)
    s = 0.0
    k = n
    while term > 1e-300 and k < n + 200:
        s += term
        k += 1
        term *= mu / k
    return s


def main():
    repo, pc, outp = sys.argv[1:4]
    rows = {(r["bits"], r["curve"]): r for r in (json.loads(l) for l in gzip.open(pc, "rt"))}
    design = json.load(open(os.path.join(repo, RUNS, "RUN-PFDR-0b3699-p0-design", "design.json")))
    cal = json.load(open(os.path.join(repo, RUNS, "RUN-PFDR-0b3699-calibrate", "calibration.json")))
    an = json.load(open(os.path.join(repo, RUNS, "RUN-PFDR-0b3699-analysis", "analysis.json")))
    mu = {(c["bits"], c["curve"]): c["mu_model"] for c in design["curves"]}
    rho = {int(b): v for b, v in cal["rho1_hat_b"].items()}
    hs = {int(b): design["height_screen"][b] for b in design["height_screen"]}
    out = {"rho1_hat_b": rho, "arms": {}}
    for arm in ("small_x", "small_x_offset"):
        res = {}
        for name, mf in (("a_uncalibrated_mu_model", lambda k: mu[k]),
                         ("b_calibrated_rho1_x_mu_model", lambda k: rho[k[0]] * mu[k])):
            lst, minp, minf = [], (2.0, None), (1.0, None)
            for k, r in sorted(rows.items()):
                if arm == "small_x_offset" and k[1] in hs.get(k[0], []):
                    continue
                n = r[arm]
                p = sf_tail(n, mf(k))
                if p < 1e-4:
                    lst.append([k[0], k[1], n, p])
                if p < minp[0]:
                    minp = (p, [k[0], k[1], n])
                # smallest f in (0,1] with sf(n, f*mu) < 1e-4 (sf increases with mu)
                if n > 0 and sf_tail(n, 1e-12) < 1e-4 <= p:
                    lo, hi = 0.0, 1.0
                    for _ in range(80):
                        mid = (lo + hi) / 2
                        if sf_tail(n, mid * mf(k)) < 1e-4:
                            lo = mid
                        else:
                            hi = mid
                    if lo < minf[0] or minf[1] is None:
                        if minf[1] is None or lo > minf[0]:
                            pass
                    # track the LARGEST f at which some curve becomes listed (closest to 1)
                    if minf[1] is None or lo > minf[0]:
                        minf = (lo, [k[0], k[1], n])
            res[name] = {"listed": lst, "n_listed": len(lst), "min_tail_probability": minp[0],
                         "min_tail_at": minp[1],
                         "largest_mean_factor_at_which_some_curve_is_listed": minf[0] if minf[1] else None,
                         "that_curve": minf[1]}
        la = {tuple(x[:3]) for x in res["a_uncalibrated_mu_model"]["listed"]}
        lb = {tuple(x[:3]) for x in res["b_calibrated_rho1_x_mu_model"]["listed"]}
        rec = {tuple(x[:3]) for x in an["tail_checks"][arm]["poisson_tail_lt_1e-4"]}
        res["symmetric_difference_a_b"] = sorted(list(x) for x in la ^ lb)
        res["analysis_json_list"] = an["tail_checks"][arm]["poisson_tail_lt_1e-4"]
        res["analysis_equals_a"] = rec == la
        res["analysis_equals_b"] = rec == lb
        res["max_count"] = max(r[arm] for r in rows.values())
        out["arms"][arm] = res
    # sanity: harvester TT poisson_mean / 3 == mu_model; and TB means for the supplementary screen
    tbmu = {}
    worst = 0.0
    with gzip.open(os.path.join(repo, RUNS, "RUN-PFDR-0b3699-table", "rows.jsonl.gz"), "rt") as fh:
        for line in fh:
            r = json.loads(line)
            k = (r["bits"], r["curve"])
            pm = r["harvest"]["TT"]["at_stop"]["poisson_mean"]
            worst = max(worst, abs(pm / 3 - mu[k]) / mu[k])
            tbmu[(k[0], k[1], r["arm"])] = r["harvest"]["TB"]["at_stop"]["poisson_mean"] / 3
    out["sanity_TT_poisson_mean_over_3_vs_mu_model_max_rel_diff"] = worst
    tb = {}
    for arm in ("subgroup", "small_x", "random_sub_r0", "random_sub_r1", "random_sub_r2", "known_null_sub",
                "planted_sub", "small_x_offset"):
        hist = {}
        lst = []
        for k, r in sorted(rows.items()):
            n = r[arm + "|TB"]
            hist[n] = hist.get(n, 0) + 1
            p = sf_tail(n, tbmu[(k[0], k[1], arm)])
            if p < 1e-4:
                lst.append([k[0], k[1], n, p])
        tb[arm] = {"TB_per_curve_histogram": {str(a): b for a, b in sorted(hist.items())},
                   "TB_screen_listed_n": len(lst), "TB_screen_listed_first": lst[:20]}
    out["supplementary_TB_screen_uncalibrated_poisson_mean_over_3"] = tb
    out["analysis_json_reports_TB_tail_list"] = any("TB" in k and "tail" in k.lower()
                                                     for k in json.dumps(an["tail_checks"]).split('"'))
    json.dump(out, open(outp, "w"), indent=1, default=str)
    print(json.dumps(out, indent=1, default=str)[:7000])


if __name__ == "__main__":
    main()
