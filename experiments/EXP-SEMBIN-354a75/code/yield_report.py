#!/usr/bin/env python3
"""Read raw-result.json and print the tables the task report needs.

Derives nothing new: every number here is already in raw-result.json. This
exists so the report and the artifact cannot drift apart, and so a reader can
regenerate the report's tables from the artifact in one command.
"""
from __future__ import annotations

import argparse
import json
from math import factorial, prod

SEM = "semaev_v_to_the_t_over_t_factorial"
EXA = "exact_multiset_count_binom_V_plus_t_minus_1_choose_t"
KF = "known_false_v_to_the_t_no_symmetry"


def cellkey(c):
    return (c["cell"]["n"], c["cell"]["m"], c["cell"]["t"], c["cell"]["k"])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True)
    ap.add_argument("--side", default="E")
    args = ap.parse_args()
    d = json.load(open(args.raw))
    side = args.side

    print("=" * 100)
    print("CONTROL 1  BASELINE: eq. (11) against every printed P_theoretical "
          "of Tables 1-2")
    b = d["controls"]["baseline"]
    print(f"  cells checked            {b['cells_checked']}")
    print(f"  matched by truncation    {b['matched_by_truncation']}")
    print(f"  matched by rounding      {b['matched_by_rounding']}")
    print(f"  matched by either        {b['matched_by_either']}")
    print(f"  all matched to 4 dp      {b['all_matched_to_four_decimals']}")
    print(f"  max abs error            {b['max_abs_error']:.3e}")
    sa = d["controls"]["specification_annotation_crosscheck"]
    print(f"  spec annotations agree   {sa['all_annotations_match']}")
    for r in sa["rows"]:
        if not r["annotation_matches_frozen_table"]:
            print(f"    MISMATCH {r['cell']}: spec says "
                  f"{r['specification_annotation']}, frozen table prints "
                  f"{r['frozen_table_printed_values']}, eq.(11) gives "
                  f"{r['recomputed_eq11']:.6f}")

    print()
    print("=" * 100)
    print("CONTROL 2  MATCHED NULL: realized symmetric random map, exact class "
          "count, all q targets")
    print(f"{'cell':>18s} {'K':>12s} {'vs matched':>11s} {'range':>19s} "
          f"{'vs semaev':>10s} {'inflation':>10s}")
    for nb in d["controls"]["matched_null"]["cells"]:
        c = nb["cell"]
        s0 = nb["per_seed"][0]
        print(f"{f'n{c[chr(110)]} t{c[chr(116)]} k{c[chr(107)]}':>18s} "
              f"{nb['realized_class_count']:12d} "
              f"{nb['matched_ratio_mean']:11.4f} "
              f"[{nb['matched_ratio_min']:.4f},{nb['matched_ratio_max']:.4f}] "
              f"{s0[SEM]['exact_ratio_all_q_targets']:10.4f} "
              f"{nb['class_count_inflation_closed_form']:10.4f}")
    print(f"  min over all cells of the matched ratio: "
          f"{d['controls']['matched_null']['min_matched_ratio']:.4f}   "
          f"(gate: the run stops if this is BELOW 1)")

    print()
    print("=" * 100)
    print("CONTROL 4  KNOWN-FALSE CLASS COUNT: ratio shift, which must be t!")
    print(f"{'cell':>18s} {'t!':>6s} {'semaev/kf ratio':>16s} "
          f"{'P_sem/P_kf':>11s} {'lam_kf/lam_sem':>15s}")
    for cell in d["cells"]:
        n, m, t, k = cellkey(cell)
        if side not in cell["pooled"]:
            continue
        p = cell["pooled"][side]["single"]
        rs, rk = p[SEM]["ratio_zero_headline"], p[KF]["ratio_zero_headline"]
        e = cell["eq11"]
        print(f"{f'n{n} t{t} k{k}':>18s} {factorial(t):6d} "
              f"{(rk / rs if rs else float('nan')):16.4f} "
              f"{e[SEM]['P'] / e[KF]['P']:11.4f} "
              f"{e[KF]['lambda'] / e[SEM]['lambda']:15.1f}")
    print("  NOTE: the ratio shift equals t! only where lambda << 1, since P "
          "saturates; lam_kf/lam_sem is t! exactly by construction.")

    print()
    print("=" * 100)
    print(f"HEADLINE RATIOS, pooled over 20 configurations per cell, target "
          f"population {side}")
    for pres in ("single", "chained", "usable"):
        print(f"\n  presentation = {pres}")
        print(f"{'cell':>16s} {'tk-n':>5s} {'draws':>7s} {'P_eq11':>8s} "
              f"{'hit':>8s} {'zero':>8s} {'ratio':>8s} {'ci95':>17s} "
              f"{'ratio_exact':>11s} {'mean':>8s} {'r_mean':>8s}")
        for cell in d["cells"]:
            n, m, t, k = cellkey(cell)
            if side not in cell["pooled"]:
                continue
            p = cell["pooled"][side][pres]
            s, e = p[SEM], p[EXA]
            print(f"{f'n{n} m{m} t{t} k{k}':>16s} {t*k-n:5d} "
                  f"{s['draws']:7d} {s['modelled_P_zero_complement']:8.5f} "
                  f"{s['measured_hit_fraction']:8.5f} "
                  f"{s['measured_zero_fraction']:8.5f} "
                  f"{s['ratio_zero_headline']:8.3f} "
                  f"[{s['ratio_zero_ci95'][0]:6.3f},{s['ratio_zero_ci95'][1]:6.3f}] "
                  f"{e['ratio_zero_headline']:11.3f} "
                  f"{s['measured_mean_count']:8.4f} "
                  f"{s['ratio_mean']:8.3f}")

    print()
    print("=" * 100)
    print("TAIL CHECK 2  ZERO-DECOMPOSITION FRACTION, separately from the mean")
    print(f"{'cell':>16s} {'zero_single':>12s} {'zero_chained':>13s} "
          f"{'zero_usable':>12s} {'1-P_eq11':>10s} {'mean_single':>11s}")
    for cell in d["cells"]:
        n, m, t, k = cellkey(cell)
        if side not in cell["pooled"]:
            continue
        pl = cell["pooled"][side]
        print(f"{f'n{n} m{m} t{t} k{k}':>16s} "
              f"{pl['single'][SEM]['measured_zero_fraction']:12.5f} "
              f"{pl['chained'][SEM]['measured_zero_fraction']:13.5f} "
              f"{pl['usable'][SEM]['measured_zero_fraction']:12.5f} "
              f"{1 - cell['eq11'][SEM]['P']:10.5f} "
              f"{pl['single'][SEM]['measured_mean_count']:11.4f}")

    print()
    print("=" * 100)
    print("TAIL CHECK 3  CHAINED MINUS SINGLE, per R, not averaged")
    print(f"{'cell':>16s} {'differ':>8s} {'diff&HELD':>10s} "
          f"{'diff&FAILED':>12s} {'L2 fail frac':>13s} {'histogram':>34s}")
    for cell in d["cells"]:
        n, m, t, k = cellkey(cell)
        if side not in cell["pooled"]:
            continue
        l2 = cell["pooled"][side]["lemma2"]
        h = {kk: vv for kk, vv in l2["chained_minus_single_histogram"].items()}
        print(f"{f'n{n} m{m} t{t} k{k}':>16s} {l2['R_where_they_differ']:8d} "
              f"{l2['R_where_they_differ_and_condition_HELD']:10d} "
              f"{l2['R_where_they_differ_and_condition_FAILED']:12d} "
              f"{l2['side_condition_failure_fraction']:13.6f} "
              f"{str(h)[:34]:>34s}")

    print()
    print("=" * 100)
    print("LEMMA 2 / F_(q^2)\\F_q SOLUTIONS")
    print(f"{'cell':>16s} {'outside_tot':>12s} {'R_with_any':>11s} "
          f"{'frac_of_pm':>11s} {'L2_fail':>9s} {'ci95':>19s}")
    for cell in d["cells"]:
        n, m, t, k = cellkey(cell)
        if side not in cell["pooled"]:
            continue
        l2 = cell["pooled"][side]["lemma2"]
        print(f"{f'n{n} m{m} t{t} k{k}':>16s} "
              f"{l2['outside_fq_solution_total']:12d} "
              f"{l2['R_with_any_outside_fq_solution']:11d} "
              f"{l2['y_outside_Fq_solution_fraction']:11.6f} "
              f"{l2['side_condition_failure_fraction']:9.6f} "
              f"[{l2['side_condition_failure_ci95'][0]:.6f},"
              f"{l2['side_condition_failure_ci95'][1]:.6f}]")

    print()
    print("=" * 100)
    print("POISSON FIT AND FITTED c(t)")
    print(f"{'cell':>16s} {'lambda_fit':>11s} {'chi2':>10s} {'dof':>4s} "
          f"{'p':>9s} {'bins':>5s} {'c_class':>8s} {'c_ord':>8s} {'maxobs':>7s} "
          f"{'p_tail':>9s}")
    for cell in d["cells"]:
        n, m, t, k = cellkey(cell)
        if side not in cell["pooled"]:
            continue
        p = cell["pooled"][side]["single"]
        f = p["poisson_fit"]
        et = p["extreme_tail"]
        cc = cell["pooled"][side]["c_of_t"]
        row = (f"{f'n{n} m{m} t{t} k{k}':>16s} "
               f"{f.get('fitted_lambda', float('nan')):11.5f} ")
        if f.get("applicable"):
            row += (f"{f['chi2']:10.3f} {f['dof']:4d} {f['p_value']:9.3e} "
                    f"{f['bins']:5d} ")
        else:
            row += f"{'n/a: ' + str(f.get('reason'))[:24]:>30s} "
        row += (f"{cc['c_of_t_class_granularity_single']['value']:8.3f} "
                f"{cc['c_of_t_ordered_granularity_single']['value']:8.3f} "
                f"{et.get('max_count', -1):7d} "
                f"{et.get('p_any_of_n_draws_at_least_max', float('nan')):9.3e}")
        print(row)

    print()
    print("=" * 100)
    print("EXACT MEASUREMENTS OVER ALL TARGETS (no sampling error)")
    print(f"{'cell':>16s} {'L':>6s} {'multisets':>11s} {'conserv':>8s} "
          f"{'targets':>9s} {'exact_hit':>10s} {'exact_mean':>11s} "
          f"{'mean/lam_sem':>13s}")
    for cell in d["cells"]:
        n, m, t, k = cellkey(cell)
        ex = cell.get("exact_usable_all_R_B1_low_degree")
        if not ex:
            continue
        print(f"{f'n{n} m{m} t{t} k{k}':>16s} "
              f"{ex['rational_factor_base_points_L']:6d} "
              f"{ex['enumerated_multisets']:11d} "
              f"{str(ex['conservation']['identity_holds']):>8s} "
              f"{ex['target_population_affine_x_outside_V']:9d} "
              f"{ex['exact_hit_fraction']:10.6f} "
              f"{ex['exact_mean_count']:11.6f} "
              f"{ex['ratio_of_exact_mean_to_eq11_semaev_lambda']:13.4f}")
    print()
    print(f"{'cell':>16s} {'targets':>9s}   exhaustive per-R over the whole "
          f"population (single / chained / usable hit fraction)")
    for cell in d["cells"]:
        n, m, t, k = cellkey(cell)
        eh = cell.get("exhaustive_all_R_B1_low_degree")
        if not eh or not eh.get("completed"):
            continue
        print(f"{f'n{n} m{m} t{t} k{k}':>16s} {eh['targets']:9d}   "
              f"single={eh['single']['hit_fraction']:.6f} "
              f"chained={eh['chained']['hit_fraction']:.6f} "
              f"usable={eh['usable']['hit_fraction']:.6f}   "
              f"means {eh['single']['mean']:.4f}/"
              f"{eh['chained']['mean']:.4f}/{eh['usable']['mean']:.4f}")

    print()
    print("=" * 100)
    print("SPREAD ACROSS CONFIGURATIONS (why a single pooled ratio is not the "
          "whole story)")
    print(f"{'cell':>16s} {'L range':>12s} {'ratio min':>10s} "
          f"{'ratio max':>10s} {'ratio spread':>13s}")
    for cell in d["cells"]:
        n, m, t, k = cellkey(cell)
        rs, Ls = [], []
        for cfg in cell["configurations"]:
            sd = cfg["sides"].get(side)
            if not sd or "ratios" not in sd:
                continue
            rs.append(sd["ratios"]["single"][SEM]["ratio_zero_headline"])
            Ls.append(cfg["factor_base_rational_points"])
        if not rs:
            continue
        print(f"{f'n{n} m{m} t{t} k{k}':>16s} "
              f"{f'{min(Ls)}-{max(Ls)}':>12s} {min(rs):10.3f} "
              f"{max(rs):10.3f} {max(rs) - min(rs):13.3f}")

    print()
    print("=" * 100)
    print("TARGET POPULATION COMPARISON: E-side (the algorithm's R) vs T-side")
    print(f"{'cell':>16s} {'E hit':>9s} {'T hit':>9s} {'E ratio':>9s} "
          f"{'T ratio':>9s} {'mean of the two ratios':>23s}")
    for cell in d["cells"]:
        n, m, t, k = cellkey(cell)
        if "E" not in cell["pooled"] or "T" not in cell["pooled"]:
            continue
        e = cell["pooled"]["E"]["single"][SEM]
        tt = cell["pooled"]["T"]["single"][SEM]
        print(f"{f'n{n} m{m} t{t} k{k}':>16s} "
              f"{e['measured_hit_fraction']:9.5f} "
              f"{tt['measured_hit_fraction']:9.5f} "
              f"{e['ratio_zero_headline']:9.3f} "
              f"{tt['ratio_zero_headline']:9.3f} "
              f"{(e['ratio_zero_headline'] + tt['ratio_zero_headline']) / 2:23.3f}")

    print()
    print("=" * 100)
    print("CONTROLS 5 and 6")
    print(f"  invalid_input   passed={d['controls']['invalid_input']['passed']}"
          f"  {json.dumps({kk: vv for kk, vv in d['controls']['invalid_input'].items() if isinstance(vv, bool)})}")
    exc = d["controls"]["exhaustiveness"]
    print(f"  exhaustiveness  passed={exc['passed']}")
    for e in exc["cells"]:
        print(f"    {e['cell']}  V^t={e['V_to_the_t']}  "
              f"multisets={e['multisets_enumerated']}  "
              f"order_independent={e['order_independent']}  "
              f"agrees_with_per_R={e['agrees_with_independent_per_R_path']}")
    print()
    print(f"  unreached cells: {d['unreached_cells']}")
    print(f"  configurations run: {d['total_configurations_run']} "
          f"(cap {d['maximum_runs_allowed']})")
    print(f"  unexpected observations recorded: "
          f"{len(d['unexpected_observations'])}")
    for u in d["unexpected_observations"]:
        print(f"    - {u['kind']}: {str(u.get('cell', ''))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
