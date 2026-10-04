#!/usr/bin/env python3
"""Diagnosis of the measured-ratio-above-1 halt required by the contract.

EXP-SEMBIN-354a75 stopping rule: a measured ratio above 1 halts for diagnosis
and is never reported as a finding, because it contradicts the paper's own
inequality chain. This script performs that diagnosis from the retained run
artifacts alone. It fits nothing and measures nothing new: it decomposes the
measured-over-predicted ratio into exact multiplicative factors, each of which
is separately computable, and checks that their product reproduces the measured
ratio to floating-point tolerance. A residual of 1 means the excess is fully
attributed and no unexplained excess yield remains.

Mean-level decomposition, over the WHOLE target population (no sampling):

    measured_mean / lambda_eq11
      = f_legal * f_multiset * f_base * f_pop

    f_legal    = incidences / C(L+t-1, t)        <= 1
                 fraction of point multisets whose sum is a legal target
                 (the rest sum to O or to a point whose x lies in V)
    f_multiset = C(L+t-1, t) / (L**t / t!)       >= 1
                 exact multiset count against the t!-division approximation
    f_base      = (L / |V|)**t
                 eq. (11) charges |V| x-values where the factor base holds L
                 F_q-rational points; L = 2r-1 with r the number of x in V
                 carrying a rational point
    f_pop      = q / |target population|
                 eq. (11) divides by q; the algorithm's targets are the
                 affine points whose x lies outside V

Probability-level decomposition:

    P_measured / P_eq11
      = f_dispersion * f_mean_level

    f_mean_level  = (1-exp(-measured_mean)) / (1-exp(-lambda_eq11))
                    everything the mean-level factors above do to P
    f_dispersion  = P_measured / (1-exp(-measured_mean))
                    departure of the realized count distribution from the
                    Poisson shape eq. (11) assumes, at the realized mean

Usage:
    python3 yield_diagnose.py --raw <raw-result.json>
"""

from __future__ import annotations

import argparse
import json
import math
from math import comb, exp, factorial


def label(cell: dict) -> str:
    return "n%d m%d t%d k%d" % (cell["n"], cell["m"], cell["t"], cell["k"])


def mean_decomposition(cell_rec: dict) -> dict | None:
    """Exact factorisation of measured_mean / lambda_eq11 for one cell."""
    key = "exact_usable_all_R_B1_low_degree"
    ex = cell_rec.get(key)
    if not ex:
        return None
    cell = cell_rec["cell"]
    t, k, n = cell["t"], cell["k"], cell["n"]
    q = 1 << n
    v_size = 1 << k
    L = ex["rational_factor_base_points_L"]
    multisets = ex["enumerated_multisets"]
    incidences = ex["incidences"]
    population = ex["target_population_affine_x_outside_V"]

    measured_mean = incidences / population
    lam_eq11 = v_size ** t / factorial(t) / q

    f_legal = incidences / multisets
    f_multiset = multisets / (L ** t / factorial(t))
    f_base = (L / v_size) ** t
    f_pop = q / population
    product = f_legal * f_multiset * f_base * f_pop
    observed = measured_mean / lam_eq11

    return {
        "L": L,
        "V_size": v_size,
        "multisets_C_L_plus_t_minus_1_choose_t": multisets,
        "incidences_on_legal_targets": incidences,
        "target_population": population,
        "measured_mean": measured_mean,
        "lambda_eq11_semaev": lam_eq11,
        "observed_ratio_of_means": observed,
        "f_legal_multisets_reaching_a_legal_target": f_legal,
        "f_multiset_exact_over_t_factorial_approximation": f_multiset,
        "f_base_L_over_V_to_the_t": f_base,
        "f_pop_q_over_target_population": f_pop,
        "product_of_factors": product,
        "residual_observed_over_product": (observed / product) if product else None,
        "attribution_closes": (abs(observed / product - 1.0) < 1e-9) if product
        else observed == 0.0,
    }


def probability_decomposition(cell_rec: dict, side: str) -> dict | None:
    key = "exact_usable_all_R_B1_low_degree"
    ex = cell_rec.get(key)
    if not ex:
        return None
    lam_eq11 = cell_rec["eq11"]["semaev_v_to_the_t_over_t_factorial"]["lambda"]
    p_eq11 = cell_rec["eq11"]["semaev_v_to_the_t_over_t_factorial"]["P"]
    p_meas = ex["exact_hit_fraction"]
    mean_meas = ex["exact_mean_count"]
    p_poisson_at_realized_mean = 1.0 - exp(-mean_meas)
    f_mean_level = p_poisson_at_realized_mean / p_eq11
    if p_poisson_at_realized_mean == 0.0:
        f_dispersion = float("nan")
    else:
        f_dispersion = p_meas / p_poisson_at_realized_mean
    return {
        "lambda_eq11": lam_eq11,
        "P_eq11": p_eq11,
        "measured_mean": mean_meas,
        "measured_P": p_meas,
        "P_poisson_at_measured_mean": p_poisson_at_realized_mean,
        "f_mean_level": f_mean_level,
        "f_dispersion": f_dispersion,
        "product": f_mean_level * f_dispersion,
        "observed_ratio_of_P": p_meas / p_eq11,
    }


def closed_form_only(cell: dict) -> dict:
    """The class-count part of the excess, computable with no measurement.

    C(|V|+t-1, t) against |V|^t/t!: this is what eq. (11)'s own class count
    costs in the toy window, independent of any curve or any enumeration.
    """
    t, k = cell["t"], cell["k"]
    v_size = 1 << k
    exact = comb(v_size + t - 1, t)
    semaev = v_size ** t / factorial(t)
    return {
        "exact_class_count": exact,
        "semaev_class_count": semaev,
        "inflation": exact / semaev,
        "inflation_bits": math.log2(exact / semaev),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True)
    args = ap.parse_args()
    d = json.load(open(args.raw))

    print("=" * 100)
    print("DIAGNOSIS OF THE RATIO-ABOVE-1 HALT")
    print("Contract stopping rule: a measured ratio above 1 halts for diagnosis "
          "and is never reported")
    print("as a finding. Below, the excess is attributed to exactly computable "
          "factors; the residual")
    print("column is what remains unexplained and must be 1.")
    print()

    print("-" * 100)
    print("A. WHICH CELLS EXCEED 1, and under which class-count variant")
    hdr = ("%-14s %6s  %8s %8s   %8s %8s   %8s %8s" %
           ("cell", "tk-n", "sem P", "sem ci_lo", "exact P", "ex ci_lo",
            "draws", "verdict"))
    print(hdr)
    above = []
    for c in d["cells"]:
        cell = c["cell"]
        pooled = c["pooled"]["E"]
        u = pooled["usable"]
        sem = u["semaev_v_to_the_t_over_t_factorial"]
        exa = u["exact_multiset_count_binom_V_plus_t_minus_1_choose_t"]
        sem_lo = sem["ratio_zero_ci95"][0]
        exa_lo = exa["ratio_zero_ci95"][0]
        verdict = []
        if sem_lo > 1.0:
            verdict.append("SEM>1")
        if exa_lo > 1.0:
            verdict.append("EXACT>1")
        if verdict:
            above.append(label(cell))
        print("%-14s %6d  %8.4f %8.4f   %8.4f %8.4f   %8d %s" % (
            label(cell), c["tk_minus_n"], sem["ratio_zero_headline"], sem_lo,
            exa["ratio_zero_headline"], exa_lo, sem["draws"],
            ",".join(verdict) or "-"))
    print()
    print("  cells whose 95%% interval lies strictly above 1 in some variant: %s"
          % (", ".join(above) or "none"))

    print()
    print("-" * 100)
    print("B. CLOSED-FORM PART, no measurement at all: eq. (11)'s own class count")
    print("   C(|V|+t-1,t) is the exact number of unordered t-multisets from V.")
    print("   eq. (11) charges |V|^t/t!, which is smaller. A random map over the")
    print("   exact count therefore hits MORE targets than eq. (11) predicts, with")
    print("   no curve involved.")
    print("%-14s %6s %6s   %14s %14s %10s %8s" % (
        "cell", "|V|", "t", "exact classes", "semaev classes", "inflation", "bits"))
    for c in d["cells"]:
        cell = c["cell"]
        cf = closed_form_only(cell)
        print("%-14s %6d %6d   %14d %14.1f %10.4f %8.3f" % (
            label(cell), 1 << cell["k"], cell["t"], cf["exact_class_count"],
            cf["semaev_class_count"], cf["inflation"], cf["inflation_bits"]))

    print()
    print("-" * 100)
    print("C. EXACT MEAN-LEVEL ATTRIBUTION over the whole target population")
    print("   measured_mean/lambda_eq11 = f_legal * f_multiset * f_base * f_pop")
    print("%-14s %5s %6s   %8s %9s %8s %7s   %9s %9s %10s" % (
        "cell", "L", "|V|", "f_legal", "f_multi", "f_base", "f_pop",
        "product", "observed", "residual"))
    all_close = True
    for c in d["cells"]:
        m = mean_decomposition(c)
        if m is None:
            continue
        all_close &= m["attribution_closes"]
        res = m["residual_observed_over_product"]
        print("%-14s %5d %6d   %8.4f %9.4f %8.4f %7.4f   %9.4f %9.4f %10s" % (
            label(c["cell"]), m["L"], m["V_size"],
            m["f_legal_multisets_reaching_a_legal_target"],
            m["f_multiset_exact_over_t_factorial_approximation"],
            m["f_base_L_over_V_to_the_t"],
            m["f_pop_q_over_target_population"],
            m["product_of_factors"], m["observed_ratio_of_means"],
            ("%10.7f" % res) if res is not None else "0/0 (both)"))
    print()
    print("  every cell's attribution closes to 1e-9: %s" % all_close)

    print()
    print("-" * 100)
    print("D. PROBABILITY-LEVEL ATTRIBUTION: what eq. (11)'s P ratio splits into")
    print("   P_measured/P_eq11 = f_dispersion * f_mean_level")
    print("%-14s   %9s %9s   %12s %12s   %9s %9s" % (
        "cell", "lam_eq11", "mean_meas", "f_mean_level", "f_dispersion",
        "product", "observed"))
    for c in d["cells"]:
        p = probability_decomposition(c, "E")
        if p is None:
            continue
        print("%-14s   %9.5f %9.5f   %12.4f %12.4f   %9.4f %9.4f" % (
            label(c["cell"]), p["lambda_eq11"], p["measured_mean"],
            p["f_mean_level"], p["f_dispersion"], p["product"],
            p["observed_ratio_of_P"]))

    print()
    print("-" * 100)
    print("E. DOES THE EXCESS SURVIVE THE TWO TOY-WINDOW FACTORS?")
    print("   f_multiset and f_base are both O(|V|^-1/2)-type small-window")
    print("   effects: they go to 1 as |V| grows at fixed t. The cells are")
    print("   ordered by |V| below so the trend is visible.")
    print("%-14s %7s %6s   %9s %9s   %9s   %9s" % (
        "cell", "|V|", "t", "f_multi", "f_base", "f_mul*base", "P ratio"))
    rows = []
    for c in d["cells"]:
        m = mean_decomposition(c)
        p = probability_decomposition(c, "E")
        if m is None or p is None:
            continue
        rows.append((m["V_size"], label(c["cell"]), c["cell"]["t"], m, p))
    for v, lab, t, m, p in sorted(rows):
        fm = m["f_multiset_exact_over_t_factorial_approximation"]
        fb = m["f_base_L_over_V_to_the_t"]
        print("%-14s %7d %6d   %9.4f %9.4f   %9.4f   %9.4f" % (
            lab, v, t, fm, fb, fm * fb, p["observed_ratio_of_P"]))

    print()
    print("-" * 100)
    print("F. THE ONE QUANTITY THE HALT ASKS ABOUT: is there residual excess")
    print("   yield after eq. (11)'s own approximations are removed?")
    print("   f_legal is the only factor below 1 and the only one that reflects")
    print("   the curve rather than the formula. It is the realized shortfall.")
    print("%-14s   %12s   %12s" % ("cell", "f_legal", "1 - f_legal"))
    for c in d["cells"]:
        m = mean_decomposition(c)
        if m is None:
            continue
        fl = m["f_legal_multisets_reaching_a_legal_target"]
        print("%-14s   %12.6f   %12.6f" % (label(c["cell"]), fl, 1.0 - fl))

    print()
    print("-" * 100)
    print("G. SHAPE-ONLY COMPARISON, pooled over all 20 configurations per cell.")
    print("   This is the one comparison no class-count convention can move: it")
    print("   asks whether eq. (11)'s Poisson zero-probability holds AT THE")
    print("   REALIZED MEAN. f_dispersion below 1 means more targets have zero")
    print("   decompositions than a Poisson of the same mean would give.")
    print("%-14s %7s %5s   %10s %10s %10s   %12s" % (
        "cell", "|V|", "t", "mean_meas", "P_meas", "P_pois(mean)",
        "f_dispersion"))
    for c in d["cells"]:
        cell = c["cell"]
        u = c["pooled"]["E"]["usable"]["semaev_v_to_the_t_over_t_factorial"]
        mean_meas = u["measured_mean_count"]
        p_meas = u["measured_hit_fraction"]
        p_pois = 1.0 - exp(-mean_meas)
        print("%-14s %7d %5d   %10.5f %10.5f %10.5f   %12.4f" % (
            label(cell), 1 << cell["k"], cell["t"], mean_meas, p_meas, p_pois,
            (p_meas / p_pois) if p_pois else float("nan")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
