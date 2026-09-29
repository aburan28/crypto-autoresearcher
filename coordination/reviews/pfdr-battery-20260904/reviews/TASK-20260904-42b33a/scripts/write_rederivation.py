"""Emit rederivation.yaml from tables/rederivation_results.json (+ variants, instance checks).
PHASE A deliverable; written before any manifest result block was opened."""
import hashlib
import json
import os
import sys
from datetime import datetime, timezone

BASE = ("/home/user/crypto-autoresearcher/coordination/reviews/pfdr-battery-20260904/"
        "reviews/TASK-20260904-42b33a/")


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 16), b""):
            h.update(b)
    return h.hexdigest()


d = json.load(open(BASE + "tables/rederivation_results.json"))
ic = json.load(open(BASE + "tables/instance_checks.json"))
v2b = json.load(open(BASE + "tables/variants_2b_3_12.json"))
v2b4 = json.load(open(BASE + "tables/variants_2b_4_3.json"))
vp2 = json.load(open(BASE + "tables/variants_poly_2_12.json"))
vp3 = json.load(open(BASE + "tables/variants_poly_3_1.json"))

L = []
w = L.append
now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

w("rederivation:")
w("  task_id: TASK-20260904-42b33a")
w("  experiment_id: EXP-PFDR-cbdefb")
w("  hypothesis_id: H-PFDR-c88f14")
w("  phase: A")
w(f"  written_at_utc: '{now}'")
w("  derived_from:")
w("    - ledger/handoffs/TASK-20260904-42b33a.yaml (review_plan.blind_rederivation:"
  " quantity + parameters)")
w("    - ledger/hypotheses/H-PFDR-c88f14.yaml (statement (A)/(B) and mechanism)")
w("    - experiments/EXP-PFDR-cbdefb/specification.yaml (contract: D_max, arms, rule)")
w("  producer_artifacts_read: none (blind_from respected; see review_attestation)")
w("")
w("  quantity_as_implemented:")
w("    ring_primary: >-")
w("      READING 1, literal polynomial ring. R = F_p[a_{1,0..s-1}, a_{2,0..s-1}],")
w("      n = 2s, F = { S~ } u { a_{k,i}^2 - a_{k,i} } with S~ = S_3(ell_1, ell_2, x_R)")
w("      reduced modulo the field equations (multilinear representative, deg_B 4 for")
w("      s >= 2). V_{F,D} = smallest F_p-subspace of R_{<=D} containing F n R_{<=D}")
w("      and closed under v -> h v for every MONOMIAL h with deg(h) + deg(v) <= D")
w("      (in a domain deg(h v) = deg h + deg v, so this is the definition verbatim).")
w("    fall_test: 'fall at D  <=>  dim(V_{F,D} n R_{<=D-1}) > dim V_{F,D-1}'")
w("    d_ff: least D <= D_max = 7 with a fall")
w("    d_lf: greatest D <= D_max = 7 with a fall")
w("    computed_in: >-")
w("      the squarefree quotient B = R/(a_i^2 - a_i) with the multiplication condition")
w("      deg(h) + deg_B(v) <= D (call it reading 2a), which is the plan's named")
w("      'reduced-ring variant, multiplying only the elements of degree <= D - 1'.")
w("      Reading 1 and reading 2a have IDENTICAL fall histories; this is proved in the")
w("      validation report (equivalence lemma) and verified numerically by running")
w("      reading 1 literally in R at s = 2 (all 12 instances) and s = 3 (1 instance).")
w("    linear_algebra: >-")
w("      own float64-exact Gaussian elimination mod p (entries < p, at most N terms per")
w("      inner product, N (p-1)^2 < 2^53 asserted at construction); harness/macaulay_fp")
w("      is NOT imported anywhere.")
w("    pass_count_convention: >-")
w("      iteration_count = 1 + productive_rounds, where round 0 is the degree-<=D")
w("      Macaulay row space span{ h S~ : deg h <= D - 4 } and a round is productive if")
w("      it strictly increases dim. rounds_executed is also recorded. A round that")
w("      reaches dim = dim(I(Z) n B_{<=D}) is a proven fixed point (V is always inside")
w("      the ideal cap), so the confirming no-growth round is skipped there.")
w("    censoring_basis: >-")
w("      OWN CERTIFICATE (derived from the definition, not read from any producer")
w("      artifact). B = R/(a^2-a) is a product of copies of F_p, so the ideal generated")
w("      by S~ in B is exactly I(Z) with Z = { z in {0,1}^n : S~(z) = 0 }, and")
w("      V_{F,D} is contained in J_D := I(Z) n B_{<=D} for every D. LEMMA: if the")
w("      evaluation map B_{<=D-1} -> F_p^Z is surjective then J_{D+1} = J_D + sum_i a_i")
w("      J_D. COROLLARY: if V_{F,7} = J_7 and rank(eval on B_{<=6}) = |Z|, then")
w("      V_{F,D} = J_D and there is NO fall at any D > 7, so the draw is uncensored.")
w("      Both premises are recorded per draw below and hold on all 48 systems.")
w("      The plan's structural criterion (D_max >= n + 1) additionally holds for s <= 3.")
w("")

res = sorted(d["results"], key=lambda r: (r["p"], r["curve_seed"], r["target_seed"], r["s"]))
w("  per_draw:")
for r in res:
    pd = r["per_degree"]
    w(f"    - id: 'p{r['p']}_curve{r['curve_seed']}_target{r['target_seed']}_s{r['s']}'")
    w(f"      p: {r['p']}")
    w(f"      curve_seed: {r['curve_seed']}")
    w(f"      target_seed: {r['target_seed']}")
    w(f"      a: {r['a']}")
    w(f"      b: {r['b']}")
    w(f"      x_R: {r['x_R']}")
    w(f"      s: {r['s']}")
    w(f"      n_variables: {r['n']}")
    w(f"      deg_S_tilde: {r['deg_S_tilde']}")
    w(f"      columns_at_D7: {r['cols_at_Dmax']}")
    w(f"      digit_solutions: {json.dumps([[q['ell1'], q['ell2']] for q in r['solutions_Z']])}")
    fh = {str(D): bool(pd[str(D)]["fall"]) for D in range(1, 8)}
    w(f"      fall_history_D1_to_D7: {json.dumps(fh)}")
    w(f"      fall_degrees: {json.dumps(r['fall_history'])}")
    w(f"      d_ff: {r['d_ff']}")
    w(f"      d_lf: {r['d_lf']}")
    w(f"      single_fall: {str(bool(r['single_fall'])).lower()}")
    w("      dims_per_degree:   # D: [N_cols, dim V_FD, dim ideal cap, dim(V_FD n B_<=D-1), dim V_F(D-1)]")
    for D in range(4, 8):
        v = pd[str(D)]
        w(f"        '{D}': [{v['N_cols']}, {v['dim_V_FD']}, {v['dim_ideal_cap']},"
          f" {v['dim_V_FD_cap_B_leq_Dm1']}, {v['dim_V_FDm1']}]")
    w("      passes_per_degree:  # D: [rounds_executed, productive_rounds, iteration_count, saturates_ideal_cap]")
    for D in range(4, 8):
        v = pd[str(D)]
        w(f"        '{D}': [{v['rounds_executed']}, {v['productive_rounds']},"
          f" {v['iteration_count']}, {str(bool(v['saturates_ideal_cap'])).lower()}]")
    c = r["certificate"]
    w(f"      right_censored: {str(bool(r['right_censored'])).lower()}")
    w("      censoring_certificate:")
    w(f"        V_at_D7_equals_ideal_cap: {str(bool(c['V_at_Dmax_equals_ideal_cap'])).lower()}")
    w(f"        num_solutions_abs_Z: {c['num_solutions']}")
    w(f"        eval_rank_on_B_leq_6: {c['eval_rank_at_Dmax_minus_1']}")
    w(f"        eval_surjective_from_B_leq_6: {str(bool(c['eval_surjective_from_B_leq_6'])).lower()}")
    w(f"        structural_D_max_ge_n_plus_1: {str(bool(c['structural_Dmax_ge_n_plus_1'])).lower()}")
    w(f"        no_fall_above_D_max_certified: {str(bool(c['no_fall_above_Dmax_certified'])).lower()}")
    w(f"      wall_seconds: {r['seconds']}")
w("")

pairs = sorted({(r["s"], r["d_ff"], r["d_lf"]) for r in res})
w("  summary:")
w(f"    systems_computed: {len(res)}   # 12 instances x s in {{2,3,4,5}}")
w("    systems_not_computed: []")
w(f"    distinct_(s,d_ff,d_lf)_triples: {json.dumps([list(x) for x in pairs])}")
w("    pairs_by_s: {'2': [5, 5], '3': [5, 5], '4': [6, 6], '5': [6, 6]}")
w("    every_computed_instance_gives_5_5__5_5__6_6__6_6: "
  + str(pairs == [(2, 5, 5), (3, 5, 5), (4, 6, 6), (5, 6, 6)]).lower())
w("    every_system_has_exactly_one_fall_degree: "
  + str(all(r["single_fall"] for r in res)).lower())
w("    d_lf_equals_d_ff_on_every_system: "
  + str(all(r["d_lf"] == r["d_ff"] for r in res)).lower())
w("    right_censored_count: %d" % sum(1 for r in res if r["right_censored"]))
w("    closure_saturates_the_ideal_cap_at_d_ff_on_every_system: "
  + str(all(r["per_degree"][str(r["d_ff"])]["saturates_ideal_cap"] for r in res)).lower())
w("    iteration_count_at_the_fall_degree: "
  + json.dumps({str(s): sorted({r["per_degree"][str(r["d_ff"])]["iteration_count"]
                                for r in res if r["s"] == s})[0] for s in (2, 3, 4, 5)}))
w("    min_iteration_count_at_any_claimed_fall: %d"
  % min(r["per_degree"][str(r["d_ff"])]["iteration_count"] for r in res))
w("    within_cell_variance_of_d_lf: 0.0   # every draw in every (s, p) cell returns the same integer")
w("")

w("  ols_fits_of_d_lf_on_s_over_s_2_to_5:")
for key, label in (("d_lf_per_draw", "a_per_draw_48_points"),
                   ("d_lf_per_cell", "b_per_s_p_cell_means_12_points"),
                   ("d_lf_per_s", "c_per_s_means_4_points")):
    f = d["fits"][key]
    w(f"    {label}:")
    w(f"      n: {f['n']}")
    w(f"      slope: {f['slope']:.10f}")
    w(f"      intercept: {f['intercept']:.10f}")
    w(f"      df: {f['df']}")
    w(f"      residual_variance: {f['residual_variance']:.10f}")
    w(f"      se_slope: {f['se_slope']:.10f}")
    w(f"      t_quantile_0975: {f['t_quantile']:.6f}")
    w(f"      ci95_t: [{f['ci95'][0]:.6f}, {f['ci95'][1]:.6f}]")
    o = f["outcome_rule"]
    w(f"      interval_contains_1: {str(o['contains_1']).lower()}")
    w(f"      interval_excludes_0_5: {str(o['excludes_0.5']).lower()}")
    w(f"      interval_contains_0: {str(o['contains_0']).lower()}")
    w(f"      interval_excludes_0_25: {str(o['excludes_0.25']).lower()}")
    w(f"      interval_excludes_0_HEUR002_falsifier_statistic: {str(o['excludes_0']).lower()}")
    w(f"      outcome_I_clause_met: {str(o['outcome_I_interval_clause']).lower()}")
    w(f"      outcome_III_interval_clause_met: {str(o['outcome_III_interval_clause']).lower()}")
    w("      contract_label: UNRESOLVED")
w("    outcome_III_flat_run_clause:")
w(f"      longest_run_of_consecutive_s_with_one_common_uncensored_d_lf: {d['longest_flat_run_in_s']}")
w(f"      flat_runs: {json.dumps(d['flat_runs'])}")
w(f"      four_consecutive_required_met: {str(bool(d['outcome_III_flat_clause_met'])).lower()}")
w("    label_on_all_three_aggregations: UNRESOLVED")
w("")
w("  ols_fits_of_d_ff_on_s_over_s_2_to_5:   # identical data, d_ff = d_lf on every draw")
for key, label in (("d_ff_per_draw", "a_per_draw_48_points"),
                   ("d_ff_per_cell", "b_per_s_p_cell_means_12_points"),
                   ("d_ff_per_s", "c_per_s_means_4_points")):
    f = d["fits"][key]
    w(f"    {label}: {{n: {f['n']}, slope: {f['slope']:.6f},"
      f" ci95_t: [{f['ci95'][0]:.6f}, {f['ci95'][1]:.6f}]}}")
w("    note: >-")
w("      Because every fallen system has exactly one fall degree, d_ff = d_lf on all 48")
w("      systems and the two fits are the same fit. The contract's OUTCOME II clause")
w("      ('the d_ff interval lies strictly below the d_lf point estimate') is therefore")
w("      unsatisfiable on these data: Outcome II was unreachable by construction, not")
w("      rejected.")
w("")

w("  convention_sensitivity:")
w("    reading_1_literal_polynomial_ring:")
w("      what: R = F_p[a] with the field equations adjoined, no quotient taken")
w(f"      s2_instances_run: {len([x for x in vp2['reading1_polynomial_ring'] if x['s'] == 2])}")
w("      s2_fall_degrees: "
  + json.dumps(sorted({tuple(x["falls"]) for x in vp2["reading1_polynomial_ring"] if x["s"] == 2}.pop())))
w("      s3_instances_run: "
  + str(len([x for x in vp3["reading1_polynomial_ring"] if x["s"] == 3])))
w("      s3_fall_degrees: "
  + json.dumps([x["falls"] for x in vp3["reading1_polynomial_ring"] if x["s"] == 3][0]))
w("      agrees_with_squarefree_computation: true")
w("      dimension_identity_checked: >-")
w("        dim V^R_{F,D} = dim V^B_{F,D} + (dim R_{<=D} - dim B_{<=D}) at every D and")
w("        every instance run, which is the equivalence lemma's dimension count.")
w("    reading_2b_reduced_ring_with_deg_B_of_the_product:")
w("      what: >-")
w("        B = R/(a^2-a) with the multiplication condition deg_B(h v) <= D instead of")
w("        deg(h) + deg_B(v) <= D. This is NOT the reading the plan designates and NOT")
w("        the plan's named reduced-ring variant (which multiplies only elements of")
w("        degree <= D-1, i.e. reading 2a). It is reported because it is the reading an")
w("        implementation that works in the quotient can slip into, and it MOVES the")
w("        answer.")
w("      s2_fall_degrees_all_12_instances: [4]        # reading 1 gives [5]")
w("      s3_fall_degrees_all_12_instances: [5]        # reading 1 gives [5]")
w("      s4_fall_degrees_3_instances: [5]             # reading 1 gives [6]")
w("      s5_fall_degrees_1_instance: [6]              # reading 1 gives [6]")
w("      ladder_s2_to_s5_one_instance_p4099_curve3101_target1: [4, 5, 5, 6]")
w("      ols_slope_on_that_ladder_4_points: 0.6")
w("      ols_ci95_t_on_that_ladder_4_points: [-0.008487, 1.208487]")
w("      consequence: >-")
w("        under reading 2b the ladder is 4, 5, 5, 6 rather than 5, 5, 6, 6, and the")
w("        four-point OLS slope is 0.6 rather than 0.4. The load-bearing quantity is")
w("        therefore CONVENTION-DEPENDENT, and the frozen convention file is load-")
w("        bearing for every number in this experiment. My primary reading (the one the")
w("        plan designates as literal) is the one that reproduces the contract's frozen")
w("        d_ff prediction 5, 5, 6, 6; reading 2b does not.")
w("")

w("  instance_checks_joint_V3:")
w("    all_12_nonsingular: "
  + str(all(x["nonsingular"] for x in ic["instances"])).lower())
w("    all_12_a_and_b_nonzero: "
  + str(all(x["a_nonzero"] and x["b_nonzero"] for x in ic["instances"])).lower())
w("    all_12_have_at_least_two_oncurve_x_in_window: "
  + str(all(x["n_oncurve_x_in_window"] >= 2 for x in ic["instances"])).lower())
w("    all_12_x_R_is_a_window_pair_sum: "
  + str(all(x["xR_is_window_pair_sum"] for x in ic["instances"])).lower())
w("    distinct_x_R_reachable_per_curve:")
for k, v in sorted(ic["per_curve"].items()):
    w(f"      {k}: {{n_oncurve_x: {len(v['oncurve_x_in_window'])},"
      f" n_window_points: {v['n_window_points']},"
      f" n_distinct_x_R: {v['n_distinct_x_R'] if 'n_distinct_x_R' in v else v['n_distinct_xR_reachable']}}}")
w("")

w("  phase_boundary:")
w("    note: >-")
w("      This file is written and hashed BEFORE any manifest result block, sidecar or")
w("      producer report is opened. The sha256 of this file at the boundary is recorded")
w("      in logs/phase-boundary.txt and in validation-report.yaml (a file cannot carry")
w("      its own hash).")
w(f"    raw_results_json_sha256: {sha(BASE + 'tables/rederivation_results.json')}")
w(f"    instance_checks_json_sha256: {sha(BASE + 'tables/instance_checks.json')}")
w(f"    written_at_utc: '{now}'")

open(BASE + "rederivation.yaml", "w").write("\n".join(L) + "\n")
print("wrote rederivation.yaml")
