#!/usr/bin/env python3
"""Emit the blind_rederivation and proves_too_much_control YAML blocks of
readers/stats.yaml from rederive_out.json, controls_out.json and
multiplicity_out.json (all produced by this reader's own scripts).

Usage: python3 -I emit_yaml_tables.py <dir_with_outputs> <out_part>
"""
import json
import sys

d = sys.argv[1]
M = json.load(open(f"{d}/rederive_out.json"))
CT = json.load(open(f"{d}/controls_out.json"))
f3 = lambda x: f"{x:.3f}"
f4 = lambda x: f"{x:.4f}"
ci = lambda c, f=f4: f"[{f(c[0])}, {f(c[1])}]"
L = []
A = L.append
A("blind_rederivation:")
A("  method: >-")
A("    Own Python (scripts/readers/stats/rederive.py) written from PROTOCOL.md,")
A("    PROTOCOL_AMENDMENT_1.md, raw records.jsonl and a read-only reading of the ecbench")
A("    source. S = cost.total_gae / sqrt(r) (checked on all 1,536 records); warm-ups")
A("    excluded (record.rs:361-363, compare.rs:208-210); pairs keyed (workload_id, round),")
A("    both verified (compare.rs:230-260); ratio = sum S_B / sum S_A (compare.rs:213-221);")
A("    95% interval = ecbench two-stage cluster bootstrap (targets, then pairs within")
A("    target), 4000 resamples, seed 20261002, splitmix64 state chain, linear-interpolated")
A("    2.5/97.5% quantiles (stats.rs:53-140, ecbench.rs:238-241). Cross-check: one-stage")
A("    numpy target-cluster bootstrap (20000 resamples). Band: priced_S(w) = (total_gae +")
A("    w*U)/sqrt(r), U = sum of the record's cost.unpriced counters found in counters or")
A("    phase native maps (band.rs:39-64,136-152); no record carries calibration pins, so")
A("    C = n_C = 0. ecbench band gives point means only; the per-weight interval below is")
A("    this reader's: the same two-stage cluster bootstrap applied to priced S pairs.")
A("  table_columns: >-")
A("    mean_S per arm (24 measured runs) with ecbench table's cluster CI of the mean;")
A("    alt/plan ratio at w=0 [ecbench-method CI] {numpy one-stage CI}; band mean S at")
A("    w=0,0.1,1; alt/plan band ratio per weight [two-stage CI] and class; protocol label.")
A("  sessions:")
for s, x in M.items():
    A(f"    {s}:")
    A(f"      curve: {{slug: {x['curve']['slug']}, r: {x['curve']['r']}, log2_r: {x['curve']['log2_r']:.4f}}}")
    A(f"      records: {x['n_records']}  # status {x['status_counts']}, warm-ups {x['warmups']}")
    A("      mean_S:")
    for arm, t in x["table"].items():
        A(f"        {arm}: {{mean: {f3(t['mean_s'])}, ci95: {ci(t['ci95'], f3)}, S_over_rho: {f3(t['s_over_ref'])}, levels: {json.dumps(t['levels'])}}}")
    A("      ratios_w0:")
    for k, c in x["compare"].items():
        b, a = k.split("__")[1], k.split("__")[0]
        A(f"        {b}/{a}: {{ratio: {f4(c['ratio'])}, ci95_ecbench: {ci(c['ci95'])}, ci95_numpy_target_cluster: {ci(c['np_cluster_boot']['ci95'])}, pairs: {c['pairs']}, unpaired: {c['unpaired']}}}")
    A("      band_mean_S_w0_0.1_1:")
    for arm, b in x["band"].items():
        A(f"        {arm}: [{', '.join(f3(v) for v in b['mean_s'])}]  # mean unpriced ops/run {b['mean_unpriced_ops']:.0f}")
    A("      band_ratio_alt_over_plan:")
    for arm, br in x["band_ratios"].items():
        if arm == "plan_over_rho":
            A("        plan/rho-neg: \"" + "; ".join(f"w{p['w']}: {f4(p['ratio'])} {ci(p['ci95_ecbench_method'])}" for p in br) + "\"")
            continue
        cells = "; ".join(f"w{p['w']}: {f4(p['ratio'])} {ci(p['ci95_ecbench_method'])} {p['class']}" for p in br["per_weight"])
        A(f"        {arm}: {{cells: \"{cells}\", protocol_label: {br['protocol_label']!r}, point_order_holds_across_band: {str(br['band_order_holds']).lower()}}}")
    p4 = x["P4"]
    A(f"      P1_plan_lowest_mean_S_of_IC_arms_w0: {str(x['P1']['plan_lowest']).lower()}")
    A(f"      P4: {{S_plan_over_S_rho: {f4(p4['S_plan_over_S_rho'])}, predicted: {p4['predicted']}, measured_over_predicted: {f4(p4['measured_over_predicted'])}, within_factor_2: {str(p4['within_factor_2']).lower()}}}")
    A(f"      plan_vs_plan_aa_identical_counts_every_pair: {str(x['determinism']['plan_vs_plan_aa_identical_total_and_counters_every_pair']).lower()}")
A("  pooled_double_base_over_plan_geomean_of_curve_ratios_stratified_target_bootstrap:")
for g, v in CT["pooled_double_base_over_plan"].items():
    A(f"    {g}: \"" + "; ".join(f"w{p['w']}: {f4(p['geomean_ratio'])} {ci(p['ci95'])} curves_below_1={p['per_curve_below_1']}" for p in v) + "\"")
A("  break_even_weight_double_base_equals_plan:")
for s, v in CT["break_even_weight_double_base"].items():
    A(f"    {s}: {{w_star: {v['w_star']:.3f}, plan_unpriced_ops_per_GAE: {v['plan_unpriced_per_gae']:.3f}, double_unpriced_ops_per_GAE: {v['double_unpriced_per_gae']:.3f}}}")
A("  seed_AA_plan_vs_plan_other_round_same_target:")
for s, v in CT["seed_aa_plan_round_shift"].items():
    A(f"    {s}: {{ratio: {f4(v['ratio'])}, ci95: {ci(v['ci95'])}, class: {v['class']}, mean_within_target_cv_of_plan_S: {v['mean_within_target_cv_of_plan_S']:.3f}}}")
A("proves_too_much_control:")
A("  script: scripts/readers/stats/controls.py  # output controls_out.json, controls_tables.txt")
A("  controls:")
for s, v in CT["proves_too_much"].items():
    sw = v["swapped_double_base"]
    sh = v["swapped_half_base"]
    rp = v["random_within_pair_swap_plan_half_base_w0"]["classes"]
    inj = v["injected_effect"]
    z = v["plan_without_lookup_probe_pricing_double_base"]
    A(f"    {s}:")
    A(f"      swap_plan_half_base_labels: {{actual: {v['true_half_base']!r}, swapped: {sh[1]!r}, swapped_ratios: [{', '.join(f4(p['ratio']) for p in sh[0])}]}}")
    A(f"      swap_plan_double_base_labels: {{actual: {v['true_double_base']!r}, swapped: {sw[1]!r}, swapped_cells: \"" + "; ".join(f"w{p['w']}: {f4(p['ratio'])} {ci(p['ci95'])} {p['class']}" for p in sw[0]) + "\"}")
    A(f"      random_within_pair_swaps_plan_vs_half_base_w0_100perm: {json.dumps(rp)}")
    A(f"      injected_effect_identical_seed_copy: {{x1.03: {ci(inj['1.03']['ci95'])}, x1.10: {ci(inj['1.1']['ci95'])}}}")
    A(f"      injected_effect_with_seed_noise: {{x1.03: \"{ci(inj['1.03_with_seed_noise']['ci95'])} {inj['1.03_with_seed_noise']['class']}\", x1.10: \"{ci(inj['1.1_with_seed_noise']['ci95'])} {inj['1.1_with_seed_noise']['class']}\"}}")
    A(f"      drop_plan_lookup_and_probe_pricing_double_base: {{label: {z[1]!r}, ratios: [{', '.join(f4(p['ratio']) for p in z[0])}]}}")
open(sys.argv[2], "w").write("\n".join(L) + "\n")
print("wrote", sys.argv[2], len(L), "lines")
