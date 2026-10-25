"""Red-team check for EXP-CZLIFT-f5e06c (TASK-20261023-e5df50), joints R1, R2, PTM-1.

Reads only the two archived raw-result.json files of the experiment. Computes:
  A. the curve-level design (D mix, seed overlap, lift-distance levels exercised,
     torsion-arm restrictions) that bounds what the tier move can cover;
  B. the exact null distribution of every frozen 1/p z-test, under the
     hypotheses' own model (row success probability 1/p_i, independent rows);
  C. the operating characteristic of the frozen success / falsification clauses
     against planted alternatives (rate 0, c/p, p^-1/2, a small-d leak);
  D. exact one-sided 95% upper bounds on the per-row success rate;
  E. the null-object check: the recorded z values are a function of the design
     alone when no success occurs.
No producer code is imported. Stdlib only. Deterministic (no randomness).
"""
from __future__ import annotations

import collections
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.abspath(os.path.join(HERE, "..", ".."))
RUNS = {20261009: "RUN-CZLIFT-032a92", 20261010: "RUN-CZLIFT-6447f0"}
SECTIONS = ("hensel_random", "naive", "teichmuller")
ARMS = ("cm_canonical", "random_naive")
Z_BOUND = 4.0


def load(seed):
    with open(os.path.join(EXP, "runs", RUNS[seed], "raw-result.json")) as fh:
        return json.load(fh)


def pooled_z(s, n, qbar):
    """Producer's form (validator VAL-20261022-1d018a): pooled-binomial SE."""
    se = math.sqrt(n * qbar * (1 - qbar))
    return (s - n * qbar) / se if se > 0 else None


def poisson_binomial(probs, kmax=8):
    """P(S = k) for k = 0..kmax, S a sum of independent Bernoulli(probs)."""
    dist = [1.0] + [0.0] * kmax
    for q in probs:
        for k in range(kmax, 0, -1):
            dist[k] = dist[k] * (1 - q) + dist[k - 1] * q
        dist[0] *= (1 - q)
    return dist


def cp_upper_zero(n, alpha=0.05):
    """Exact one-sided Clopper-Pearson upper bound with 0 successes in n."""
    return 1 - alpha ** (1.0 / n)


def design(seed, r):
    ca, cb = r["raw"]["curves_anomalous"], r["raw"]["curves_torsion"]
    out = {}
    out["anomalous_D_counts"] = dict(sorted(collections.Counter(c["D"] for c in ca).items()))
    out["anomalous_p_range"] = [min(c["p"] for c in ca), max(c["p"] for c in ca)]
    out["anomalous_j0_curves"] = sum(1 for c in ca if c["j_cm"] == 0)
    lv = collections.defaultdict(collections.Counter)
    vv = collections.defaultdict(collections.Counter)
    for c in ca:
        for row in c["rows"]:
            key = f"{row['class']}|e={c['e']}"
            lv[key][row["v_dj"]] += 1
            vv[key][f"vP={row['vP']},vQ={row['vQ']},deg={row['degenerate']},pred={row['predicted_degenerate']}"] += 1
    out["v_dj_by_class_and_e"] = {k: dict(sorted(v.items())) for k, v in sorted(lv.items())}
    out["valuation_pattern_by_class_and_e"] = {k: dict(v) for k, v in sorted(vv.items())}
    out["rows_per_anomalous_curve"] = sorted(set(len(c["rows"]) for c in ca))
    tor = []
    for c in cb:
        tor.append({"arm": c["arm"], "label": c["label"], "p": c["p"], "N": c["N"], "n": c["n"],
                    "cofactor": c["N"] // c["n"], "N_odd": c["N"] % 2 == 1})
    out["torsion_curves"] = len(tor)
    out["torsion_N_all_odd"] = all(t["N_odd"] for t in tor)
    out["torsion_n_range"] = [min(t["n"] for t in tor), max(t["n"] for t in tor)]
    out["torsion_prime_order_curves"] = sum(1 for t in tor if t["cofactor"] == 1)
    out["torsion_cm_D_counts"] = dict(sorted(collections.Counter(t["label"] for t in tor if t["arm"] == "cm_canonical").items()))
    out["torsion_p_range_by_arm"] = {a: [min(t["p"] for t in tor if t["arm"] == a), max(t["p"] for t in tor if t["arm"] == a)] for a in ARMS}
    out["rows_per_torsion_curve"] = sorted(set(len(c["rows"]) for c in cb))
    return out, ca, cb


def cells(ca, cb):
    """Per-row reference probabilities 1/p for every frozen z cell, plus observed successes."""
    cell = {}
    anom = [1.0 / c["p"] for c in ca for row in c["rows"] if row["degenerate"] and row["ratio_defined"]]
    anom_s = sum(1 for c in ca for row in c["rows"] if row["degenerate"] and row["ratio_defined"] and row["success"])
    cell["anomalous.degenerate"] = (anom, anom_s)
    for s in SECTIONS:
        for arm in ARMS + ("all",):
            probs, succ = [], 0
            for c in cb:
                if arm != "all" and c["arm"] != arm:
                    continue
                for row in c["rows"]:
                    sec = row["sections"][s]
                    if sec["ratio_defined"]:
                        probs.append(1.0 / c["p"])
                        succ += bool(sec["success"])
            cell[f"torsion.{s}.{arm}"] = (probs, succ)
    return cell


def threshold_count(n, qbar):
    s = 0
    while True:
        z = pooled_z(s, n, qbar)
        if z is not None and z > Z_BOUND:
            return s, z
        s += 1


def seed_fail_prob(ca, cb, rate):
    """P(some frozen cell has |z| > 4 on this seed) when each row succeeds with prob rate(p, d-model).

    rate(p) -> per-row success probability. Anomalous cell and the three sections are independent;
    within a section the cm and random arms are independent; 'all' = cm + random.
    """
    anom_p = [c["p"] for c in ca for row in c["rows"] if row["degenerate"] and row["ratio_defined"]]
    n_a = len(anom_p)
    qbar_a = sum(1.0 / p for p in anom_p) / n_a
    dist_a = poisson_binomial([rate(p) for p in anom_p], kmax=12)
    p_anom_ok = sum(dist_a[k] for k in range(len(dist_a)) if abs(pooled_z(k, n_a, qbar_a)) <= Z_BOUND)
    p_ok = p_anom_ok
    for s in SECTIONS:
        ps = {arm: [c["p"] for c in cb if c["arm"] == arm for row in c["rows"] if row["sections"][s]["ratio_defined"]] for arm in ARMS}
        allp = ps["cm_canonical"] + ps["random_naive"]
        qb = {arm: sum(1.0 / p for p in ps[arm]) / len(ps[arm]) for arm in ARMS}
        qb_all = sum(1.0 / p for p in allp) / len(allp)
        d = {arm: poisson_binomial([rate(p) for p in ps[arm]], kmax=12) for arm in ARMS}
        ok = 0.0
        for i, pi in enumerate(d["cm_canonical"]):
            for j, pj in enumerate(d["random_naive"]):
                zs = [pooled_z(i, len(ps["cm_canonical"]), qb["cm_canonical"]),
                      pooled_z(j, len(ps["random_naive"]), qb["random_naive"]),
                      pooled_z(i + j, len(allp), qb_all)]
                if all(abs(z) <= Z_BOUND for z in zs):
                    ok += pi * pj
        p_ok *= ok
    return 1 - p_ok, 1 - p_anom_ok


def main() -> int:
    data = {seed: load(seed) for seed in RUNS}
    report = {"inputs": {RUNS[s]: os.path.relpath(os.path.join(EXP, "runs", RUNS[s], "raw-result.json"), os.path.join(EXP, "..", "..")) for s in RUNS}}
    designs, arms = {}, {}
    for seed, r in data.items():
        dsg, ca, cb = design(seed, r)
        designs[seed] = dsg
        arms[seed] = (ca, cb, r)
    a1 = {(c["D"], c["p"]) for c in arms[20261009][0]}
    a2 = {(c["D"], c["p"]) for c in arms[20261010][0]}
    t1 = {(c["arm"], c["p"], c["A"], c["B"]) for c in arms[20261009][1]}
    t2 = {(c["arm"], c["p"], c["A"], c["B"]) for c in arms[20261010][1]}
    report["A_design"] = {
        "per_seed": {RUNS[s]: designs[s] for s in RUNS},
        "anomalous_curves_shared_between_seeds": len(a1 & a2),
        "anomalous_distinct_curves_both_seeds": len(a1 | a2),
        "anomalous_shared_list": sorted(a1 & a2),
        "torsion_curves_shared_between_seeds": len(t1 & t2),
        "torsion_distinct_curves_both_seeds": len(t1 | t2),
    }

    # B + E: null distribution of each frozen cell; recorded z is a function of design when S = 0.
    B = {}
    for seed, (ca, cb, r) in arms.items():
        rec = r["metrics"]
        out = {}
        for name, (probs, succ) in cells(ca, cb).items():
            n = len(probs)
            qbar = sum(probs) / n
            lam = sum(probs)
            s_star, z_star = threshold_count(n, qbar)
            dist = poisson_binomial(probs)
            if name == "anomalous.degenerate":
                z_rec = rec["anomalous"]["degenerate_z_score"]
            else:
                _, s, arm = name.split(".")
                z_rec = rec["torsion_sections"][s][arm]["z_score"]
            out[name] = {
                "n_rows": n, "observed_successes": succ, "expected_successes_under_1_over_p": lam,
                "z_if_0_successes": pooled_z(0, n, qbar), "z_recorded": z_rec,
                "z_recorded_minus_design_only_z0": (z_rec - pooled_z(0, n, qbar)) if succ == 0 else None,
                "z_if_1_success": pooled_z(1, n, qbar), "successes_needed_for_z_gt_4": s_star,
                "P_S_ge_threshold_under_1_over_p": 1 - sum(dist[:s_star]),
                "P_S_eq_0_under_1_over_p": dist[0],
                "cp95_upper_rate_given_0": cp_upper_zero(n) if succ == 0 else None,
                "cp95_upper_in_units_of_mean_1_over_p": (cp_upper_zero(n) / qbar) if succ == 0 else None,
            }
        B[RUNS[seed]] = out
    report["B_null_distribution_per_cell"] = B

    # Pooled across the two seeds (cells pooled by name).
    pooled = {}
    cs = {seed: cells(arms[seed][0], arms[seed][1]) for seed in arms}
    for name in cs[20261009]:
        probs = cs[20261009][name][0] + cs[20261010][name][0]
        succ = cs[20261009][name][1] + cs[20261010][name][1]
        qbar = sum(probs) / len(probs)
        pooled[name] = {"n_rows": len(probs), "observed_successes": succ, "expected_under_1_over_p": sum(probs),
                        "cp95_upper_rate_given_0": cp_upper_zero(len(probs)) if succ == 0 else None,
                        "cp95_upper_in_units_of_mean_1_over_p": cp_upper_zero(len(probs)) / qbar if succ == 0 else None}
    # all three torsion sections pooled per arm, if one assumes a common rate
    for arm in ARMS + ("all",):
        probs = [q for seed in cs for s in SECTIONS for q in cs[seed][f"torsion.{s}.{arm}"][0]]
        qbar = sum(probs) / len(probs)
        pooled[f"torsion.ALL_SECTIONS.{arm}"] = {"n_rows": len(probs), "expected_under_1_over_p": sum(probs),
                                                 "cp95_upper_rate_given_0": cp_upper_zero(len(probs)),
                                                 "cp95_upper_in_units_of_mean_1_over_p": cp_upper_zero(len(probs)) / qbar,
                                                 "note": "rows of different sections share the same (P, d) draws if the driver reuses them; independence is unverified"}
    report["D_pooled_upper_bounds"] = pooled

    # C: operating characteristic of the frozen clauses.
    alts = {"rate_0 (never succeeds)": lambda p: 0.0, "rate_1_over_p (H0)": lambda p: 1.0 / p}
    for c in (2, 5, 10, 20, 50, 100, 200, 500):
        alts[f"rate_{c}_over_p"] = (lambda c: (lambda p: min(1.0, c / p)))(c)
    alts["rate_p^-1/2 (rho-competitive)"] = lambda p: p ** -0.5
    # small-d leak (bdae69-like mechanism): succeeds for every d <= log2 p, else 1/p; d uniform in [2, p-2]
    alts["small_d_leak (d <= log2 p always succeeds)"] = lambda p: ((math.log2(p) - 1) / (p - 3)) + 1.0 / p
    C = {}
    for name, rate in alts.items():
        f = {seed: seed_fail_prob(arms[seed][0], arms[seed][1], rate) for seed in arms}
        p_fail1, p_anom1 = f[20261009]
        p_fail2, p_anom2 = f[20261010]
        C[name] = {
            "P_success_criterion_met_both_seeds": (1 - p_fail1) * (1 - p_fail2),
            "P_falsification_fires_both_seeds": p_fail1 * p_fail2,
            "P_neither (inconclusive)": 1 - (1 - p_fail1) * (1 - p_fail2) - p_fail1 * p_fail2,
            "per_seed_P_some_cell_z_gt_4": {RUNS[20261009]: p_fail1, RUNS[20261010]: p_fail2},
            "per_seed_P_anomalous_cell_z_gt_4": {RUNS[20261009]: p_anom1, RUNS[20261010]: p_anom2},
        }
        # torsion arm alone (the non-anomalous, security-relevant arm): P(no torsion cell fails) = P(ok)/P(anom ok)
        t1 = 1 - (1 - p_fail1) / (1 - p_anom1) if p_anom1 < 1 else None
        t2 = 1 - (1 - p_fail2) / (1 - p_anom2) if p_anom2 < 1 else None
        C[name]["torsion_only_per_seed_P_some_cell_z_gt_4"] = {RUNS[20261009]: t1, RUNS[20261010]: t2}
        C[name]["torsion_only_P_falsification_both_seeds"] = (t1 * t2) if (t1 is not None and t2 is not None) else None
    report["C_operating_characteristic"] = C

    # Bayes factor of the observed all-zero outcome, H0 (1/p) against rate 0.
    lam_total = sum(sum(probs) for seed in cs for name, (probs, _) in cs[seed].items()
                    if name == "anomalous.degenerate" or name.endswith(".all"))
    report["E_evidence_of_the_1_over_p_clause"] = {
        "total_expected_successes_under_1_over_p_both_seeds": lam_total,
        "P_all_zero_under_1_over_p": math.exp(-lam_total),
        "P_all_zero_under_rate_0": 1.0,
        "bayes_factor_1_over_p_vs_rate_0": math.exp(-lam_total),
        "log10_bayes_factor": -lam_total / math.log(10),
        "note": "lambda summed over the anomalous degenerate cell and the three torsion 'all' cells (each row counted once per section)",
    }
    out = os.path.join(HERE, "rt_power_and_design.json")
    with open(out, "w") as fh:
        json.dump(report, fh, indent=1, sort_keys=True, default=str)
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
