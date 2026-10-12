#!/usr/bin/env python3
"""Render the observation tables of RESULTS-amd-e61f2b.md from a v2 run's
raw-result.json and gate report, so the summary is generated from the raw data
and cannot drift from it. Prints markdown to stdout.

  python3 experiments/EXP-SEMBIN-04ec3c/code/v2/render_results.py <run_dir>
"""
from __future__ import annotations

import json
import os
import sys


def f(x, k=3):
    if x is None:
        return "n/a"
    if isinstance(x, bool):
        return "yes" if x else "no"
    if isinstance(x, float):
        return f"{x:.{k}f}"
    return str(x)


def main(run_dir):
    d = json.load(open(os.path.join(run_dir, "raw-result.json")))
    g = json.load(open(os.path.join(run_dir, "gate", "gate_report.json")))
    out = []
    p = out.append

    p("### T1. C-IMPL-GATE, per check and per driver\n")
    p("| driver | (a) cells / violations / max diff | (b) cells / violations / max diff | (c) cells / violations | (d) argmins at m=16 probed / bound-tracking / consistent | gate |")
    p("|---|---|---|---|---|---|")
    drivers = [("unmutated v2", g["unmutated"])]
    for mid in sorted(g["mutants"]):
        drivers.append((f"{mid} ({g['mutants'][mid]['mutation']})",
                        json.load(open(os.path.join(run_dir, g["mutants"][mid]["output"])))))
    for lab, v in drivers:
        a, b, c, dd = (v["a_yield_identity"], v["b_closed_forms"], v["c_budget_invariant"],
                       v["d_m_bound_probe"])
        p(f"| {lab} | {a['cells_checked']} / {a['violations']} / {a['max_abs_diff_bits']:.4g} | "
          f"{b['cells_checked']} / {b['violations']} / {b['max_abs_diff_bits']:.3g} | "
          f"{c['cells_checked']} / {c['violations']} | {dd['argmins_at_m16_probed']} / "
          f"{dd['bound_tracking_count']} / {f(dd['all_reevaluations_consistent'])} | "
          f"{'PASS' if v['gate_passed'] else 'FAIL ' + ','.join(v['failed_checks'])} |")
    e = g["e_gate_power_self_test"]
    p(f"\n(e) gate-power self-test: unmutated passes = {f(e['unmutated_passes'])}; every mutant fails = "
      f"{f(e['every_mutant_fails'])}; mutants passing = {e['mutants_passing'] or 'none'}; "
      f"(e) passed = {f(e['passed'])}.\n")

    fl = d["generic_lower_bound_flag"]
    p("### T2. Generic-lower-bound flag (C-3), threshold N/2 - 2.0\n")
    p(f"Cells checked (ENUM, MITM, MITM_CAPPED; in- and out-of-domain): {fl['cells_checked']}. "
      f"Fired in-domain: {fl['fired_in_domain']}; fired out-of-domain: {fl['fired_out_of_domain']}. "
      f"Fired: {f(fl['fired'])}.\n")
    p("| n | threshold N/2 - 2 | min (TOTAL - threshold) over all primary cells |")
    p("|---|---|---|")
    for n, t in fl["thresholds_by_degree"].items():
        p(f"| {n} | {t:.4f} | {fl['min_slack_bits_by_degree'][n]:.3f} |")

    p("\n### T3. Out-of-domain (CALLS < 0) cell counts, d bound n\n")
    ood = d["out_of_domain_counts_by_degree_model"]
    models = ["FREE", "ENUM", "MITM", "MITM_CAPPED"]
    p("| n | " + " | ".join(models) + " | in-domain cells, primary models |")
    p("|---|" + "---|" * (len(models) + 1))
    for n in d["parameters"]["degrees"]:
        ind = sum(c["in_domain"] for c in d["cell_counts"]
                  if c["n"] == n and c["d_bound"] == "n" and c["primary"])
        p(f"| {n} | " + " | ".join(str(ood[f'{n}|{m}']) for m in models) + f" | {ind} |")
    p("\nMITM_CAPPED counts sum over its nine budget labels. Excluded from every count and argmin below.\n")

    p("### T4. Primary sub-rho counts per (degree, model, B), in-domain cells, d bound n\n")
    p("| n | model | B | in-domain cells | sub-rho vs VOW | sub-rho vs PUB (n=131 only) |")
    p("|---|---|---|---|---|---|")
    for c in d["cell_counts"]:
        if c["primary"] and c["d_bound"] == "n":
            p(f"| {c['n']} | {c['model']} | {c['B']} | {c['in_domain']} | {c['subrho_vs_VOW']} | "
              f"{f(c['subrho_vs_PUB'])} |")
    t = d["primary_subrho_totals"]
    p(f"\nTotals: in-domain primary cells {t['cells_in_domain']}; sub-rho vs VOW {t['subrho_vs_VOW']}; "
      f"sub-rho vs PUB at n = 131 {t['subrho_vs_PUB_at_131']}; argmin rows sub-rho vs VOW "
      f"{t['argmin_rows_subrho_vs_VOW']}, vs PUB {t['argmin_rows_subrho_vs_PUB_at_131']}.\n")

    p("### T5. Per-degree minimum construction-charged TOTAL (log2 operations, modeled) beside E-2\n")
    p("| n | primary min: model, B, m, s, d | TOTAL | margin vs VOW | margin vs PUB | store-free (MITM) margin vs VOW | E-2 | v2 - E-2 | > 0.1 bit | argmin adjacent to C-2 domain edge | log2 table entries (reported, not charged) |")
    p("|---|---|---|---|---|---|---|---|---|---|---|")
    for n, v in d["per_degree_minimum"].items():
        a, s = v["n"]["primary_min"], v["n"]["store_free_min_MITM"]
        p(f"| {n} | {a['model']}, {a['B']}, {a['m']}, {a['s']}, {a['d']} | {a['TOTAL']:.3f} | "
          f"{a['margin_vs_VOW_bits']:+.3f} | {f(a['margin_vs_PUB_bits'])} | "
          f"{s['margin_vs_VOW_bits']:+.3f} | {v['n']['E2_expectation_margin_vs_VOW']:+.2f} | "
          f"{v['n']['v2_minus_E2_bits']:+.3f} | {f(v['n']['differs_from_E2_by_more_than_0_1_bit'])} | "
          f"{f(s['at_domain_edge'])} | {f(s['log2_table_entries'], 2)} |")

    p("\n### T6. Per-degree minimum TOTAL per store budget B (MITM_CAPPED), margin vs VOW\n")
    bks = d["parameters"]["budgets_log2_entries"]
    p("| n | " + " | ".join(f"B=2^{b}" if b != "unlimited" else "unlimited" for b in bks) + " | ENUM min |")
    p("|---|" + "---|" * (len(bks) + 1))
    for n, v in d["per_degree_minimum"].items():
        pb = v["n"]["per_budget_min"]
        p(f"| {n} | " + " | ".join(f"{pb[b]['margin_vs_VOW_bits']:+.2f} (m{pb[b]['m']},s{pb[b]['s']})" for b in bks)
          + f" | {v['n']['ENUM_min']['margin_vs_VOW_bits']:+.2f} (m{v['n']['ENUM_min']['m']}) |")

    c = d["controls"]
    bp = c["C-BOUND-PROBE"]
    p("\n### T7. C-BOUND-PROBE (bounds n and n/2)\n")
    p(f"Argmin rows compared {bp['argmin_rows_compared']}; agreeing {bp['argmin_rows_agreeing']}; "
      f"disagreeing {bp['argmin_rows_disagreeing']} (primary {bp['argmin_rows_disagreeing_primary']}).\n")
    p("| n | primary minimum agrees across bounds | store-free minimum agrees | TOTAL at n | TOTAL at n/2 |")
    p("|---|---|---|---|---|")
    for n, v in bp["per_degree_minimum_agreement"].items():
        pm = d["per_degree_minimum"][n]
        p(f"| {n} | {f(v['primary_min_agrees'])} | {f(v['store_free_min_agrees'])} | "
          f"{pm['n']['primary_min']['TOTAL']:.3f} | {pm['n/2']['primary_min']['TOTAL']:.3f} |")

    a6 = c["A6-TABLE"]
    p("\n### T8. A6 table (step-4 continuous minimum store vs step-3 integer-s cells)\n")
    p(f"Feasible step-4 minima across all (degree, m, bound, column): {a6['step4_feasible_count']}. "
      f"Step-3 sub-rho integer-s cells: {a6['step3_subrho_count']}.\n")
    p("| n | m | step 4 vs VOW (bound n) | step 3 sub-rho cell vs VOW | realised | closest step-3 cell: TOTAL - VOW, B, s, d |")
    p("|---|---|---|---|---|---|")
    for r in a6["rows"]:
        if r["d_bound"] != "n":
            continue
        v = r["VOW"]
        s4 = v["step4_continuous_min_store"]
        s3 = v["step3_best_integer_s_subrho_cell"]
        mt = r["step3_min_total_cell"]
        vow = d["per_degree_minimum"][str(r["n"])]["n"]["primary_min"]["TOTAL"] - \
            d["per_degree_minimum"][str(r["n"])]["n"]["primary_min"]["margin_vs_VOW_bits"]
        p(f"| {r['n']} | {r['m']} | {'infeasible' if isinstance(s4, str) else s4} | "
          f"{'none' if isinstance(s3, str) else s3} | "
          f"{v['step4_minimum_realised_by_a_step3_cell'] if not isinstance(v['step4_minimum_realised_by_a_step3_cell'], str) else 'n/a'} | "
          f"{mt['TOTAL'] - vow:+.2f}, {mt['B']}, {mt['s']}, {mt['d']} |")

    X = d.get("EXPLORATORY_NON_GATING_NEVER_CONFIRMATORY")
    if X:
        p("\n## EXPLORATORY BLOCK X-1 .. X-8 -- NON-GATING, NEVER CONFIRMATORY, never part of any primary count\n")
        p("Each value is the per-degree minimum construction-charged TOTAL (log2 operations, modeled) unless the label says otherwise, with its margin against the named column. Interpretations are listed per column and in manifest PD-7.\n")

        def mm(r):
            if "TOTAL" not in r:
                return r.get("note", "n/a")
            return f"{r['TOTAL']:.3f} ({r['margin_vs_VOW_bits']:+.3f} vs VOW; m{r.get('m', '-')}, s{r.get('s', '-')}, d{r.get('d')})"
        for key in ("X-1", "X-5"):
            col = X[key]
            p(f"**{col['label']}.** Interpretation: {col['interpretation']}.\n")
            p("| n | B=2^30 | B=2^80 | unlimited |")
            p("|---|---|---|---|")
            for n in d["parameters"]["degrees"]:
                rr = {str(r["B"]): r for r in col["rows"] if r["n"] == n}
                p(f"| {n} | {mm(rr['30.0'])} | {mm(rr['80.0'])} | {mm(rr['unlimited'])} |")
            p("")
        for key in ("X-2",):
            col = X[key]
            p(f"**{col['label']}.** Interpretation: {col['interpretation']}.\n")
            p("| n | min TOTAL (margin vs VOW; m, s, d) |")
            p("|---|---|")
            for r in col["rows"]:
                p(f"| {r['n']} | {mm(r)} |")
            p("")
        col = X["X-3"]
        p(f"**{col['label']}.** Interpretation: {col['interpretation']}.\n")
        p("| n | LA = log2 m + 2d | LA = log2 m + 2d + log2 3 |")
        p("|---|---|---|")
        for r in col["rows"]:
            p(f"| {r['n']} | {mm(r['LA_log2m_plus_2d'])} | {mm(r['LA_log2m_plus_2d_plus_log2_3'])} |")
        col = X["X-4"]
        r = col["row"]
        p(f"\n**{col['label']}.** Interpretation: {col['interpretation']}. N used {col['N_used']:.4f}. "
          f"Min TOTAL {r['TOTAL']:.3f} (m{r['m']}, s{r['s']}, d{r['d']}): {r['margin_vs_VOW_bits']:+.3f} vs VOW (from r), "
          f"{r['margin_vs_VOW_recomputed_from_4r_bits']:+.3f} vs VOW recomputed from 4r ({col['VOW_recomputed_from_4r']:.4f}), "
          f"{r['margin_vs_PUB_bits']:+.3f} vs PUB.\n")
        col = X["X-6"]
        p(f"**{col['label']}.** Interpretation: {col['interpretation']}.\n")
        p("| n | formula alone: TOTAL (vs VOW), d | with LA = 2d: TOTAL (vs VOW) | argmin at lower d bound |")
        p("|---|---|---|---|")
        for r in col["rows"]:
            a, b = r["relation_formula_alone"], r["relation_plus_LA_2d"]
            p(f"| {r['n']} | {a['TOTAL']:.3f} ({a['margin_vs_VOW_bits']:+.3f}), d{a['d']} | {b['TOTAL']:.3f} ({b['margin_vs_VOW_bits']:+.3f}) | {f(a['argmin_at_lower_d_bound'])} (bound-tracking) |")
        col = X["X-7"]
        p(f"\n**{col['label']}.** Interpretation: {col['interpretation']}.\n")
        p("| n | log2(2n) | min TOTAL (m, s, d) | vs VOW | vs VOW - log2 sqrt(2n) | vs PUB (131 only) | log2 table entries |")
        p("|---|---|---|---|---|---|---|")
        for r in col["rows"]:
            p(f"| {r['n']} | {r['log2_2n']:.3f} | {r['TOTAL']:.3f} (m{r['m']}, s{r['s']}, d{r['d']}) | {r['margin_vs_VOW_bits']:+.3f} | "
              f"{r['margin_vs_VOW_minus_log2_sqrt_2n_bits']:+.3f} | {f(r['margin_vs_PUB_bits'])} | {r['log2_table_entries']:.2f} |")
        col = X["X-8"]
        p(f"\n**{col['label']}.** Interpretation: {col['interpretation']}.\n")
        p("| n | N | VOW | construction-charged min (vs VOW) | probe-only min, NOT A COST (vs VOW) |")
        p("|---|---|---|---|---|")
        for r in col["rows"]:
            p(f"| {r['n']} | {r['N_used']:.0f} | {r['VOW']:.4f} | {mm(r['construction_charged'])} | {mm(r['probe_only_NOT_A_COST'])} |")

    print("\n".join(out))


if __name__ == "__main__":
    main(sys.argv[1])
