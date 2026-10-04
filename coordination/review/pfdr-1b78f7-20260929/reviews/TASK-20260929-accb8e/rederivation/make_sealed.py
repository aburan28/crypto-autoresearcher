"""Builds rederivation/sealed-section.yaml from my own outputs in rederivation/out/
(written before any blind_from path was opened). Embeds the conventions verbatim, the
J2a digests and counts, and every J3 number and outcome id; embeds the sha256 of every
out/ file it summarises. Contains no floor ratio (RV-4). Writes the file once; refuses
to overwrite."""
import datetime, hashlib, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import OUT, W

SEALED = os.path.join(W, "rederivation", "sealed-section.yaml")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def r6(x):
    if isinstance(x, float):
        return float(f"{x:.6g}")
    return x


def yq(s):
    return json.dumps(s)


def main():
    if os.path.exists(SEALED):
        raise SystemExit("sealed-section.yaml exists; never overwritten")
    conv_p = os.path.join(W, "rederivation", "conventions.yaml")
    conv = open(conv_p).read()
    j2a = json.load(open(os.path.join(OUT, "j2a-report.json")))
    j3 = json.load(open(os.path.join(OUT, "j3-results.json")))
    q6s = json.load(open(os.path.join(OUT, "q6-summary.json")))
    q6i = json.load(open(os.path.join(OUT, "q6-impact.json")))
    a6 = json.load(open(os.path.join(OUT, "q9-a6.json")))
    h3p = os.path.join(OUT, "q9-h3.json")
    h3 = json.load(open(h3p)) if os.path.exists(h3p) else None
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    L = []
    A = L.append
    A("# =============================================================================")
    A("# SEALED SECTION -- TASK-20260929-accb8e (validator-breakthrough), J2a and J3.")
    A("# Written before ANY path in blind_rederivation.blind_from was opened, and before")
    A("# any manifest, checksums.sha256, command.txt, environment.json, execution.json,")
    A("# log, snapshot receipt, amd-1de84f/ file or engine/CLI source of the run set.")
    A("# Inputs read before this file: checks/read-log.txt entries up to the seal line.")
    A("# Never edited after its sha256 was logged; corrections are new files naming it.")
    A("# No floor ratio appears here (RV-4): TW-FLOOR is a boolean, a count and keys.")
    A("# =============================================================================")
    A("sealed_section:")
    A("  task_id: TASK-20260929-accb8e")
    A(f"  written_at_utc: '{now}'")
    A("  object_under_review_commit: a32e708088c16b46686ea19afaab72910a42d75f")
    A("  code: rederivation/common.py, j2a_canonical.py, j3_quantities.py, j3_q6_formal.py, j3_q6_impact.py, j3_q9_a6.py, j3_q9_h3.py, make_sealed.py (own code; no engine import; stats.py loaded by file path)")
    A("  outputs_sha256:")
    for fn in sorted(os.listdir(OUT)):
        if fn.endswith(".log"):
            continue
        A(f"    {fn}: {sha(os.path.join(OUT, fn))}")
    A(f"  conventions_file: rederivation/conventions.yaml")
    A(f"  conventions_sha256: {sha(conv_p)}")
    A("  conventions_fixed_before_computing: 'yes -- hash logged in checks/read-log.txt at 2026-09-29T07:43:01Z, before j2a/j3 ran (first j2a run 07:44:34Z)'")
    A("  conventions_verbatim: |")
    for line in conv.splitlines():
        A("    " + line)
    # ---------------- J2a ----------------
    A("  J2a_Q1_canonical_sets:")
    A("    normal_form: json.dumps(record, sort_keys=True, separators=(',', ':')) per record, joined by '\\n' plus a final '\\n', UTF-8; digest sha256")
    for lab in ["R11", "R12", "R14", "R16"]:
        v = j2a[lab]
        A(f"    {lab}:")
        A(f"      U_size: {v['U_size']}")
        A(f"      canonical_rows: {v['canonical_rows']}")
        A(f"      canonical_rows_sha256: {v['canonical_rows_sha256_normal_form']}")
        A(f"      canonical_staircase_records: {v['canonical_staircase_records']}")
        A(f"      canonical_staircase_sha256: {v['canonical_staircase_sha256_normal_form']}")
        A(f"      counts_by_status: {json.dumps(v['counts_by_status'])}")
        A(f"      counts_by_source_attempt: {json.dumps(v['counts_by_source'])}")
        A(f"      placeholders: {json.dumps(v['placeholders'])}")
        A(f"      noncell_rows_excluded: {v['noncell_rows_excluded']}")
        if lab == "R11":
            A(f"      resume_set: {json.dumps(v['resume_set'])}")
            A(f"      resume_set_size: {v['resume_set_size']}")
            A(f"      resume_set_equals_M2_assertion: {str(v['resume_set_equals_M2_assertion']).lower()}")
            A(f"      attempt2_job_dirs_equal_resume_set: {str(v['attempt2_job_dirs_equal_resume_set']).lower()}")
            A(f"      superseded_attempt1_cell_rows: {v['superseded_attempt1_cell_rows']}")
            A(f"      noncell_by_arm_m: {json.dumps(v['noncell_by_arm_m'])}")
            A(f"      noncell_keys: {json.dumps([x['key'] for x in v['noncell_rows']])}")
        if lab == "R16":
            A(f"      excursion_cells_from_layout: {json.dumps(v['excursion_cells_from_layout'])}")
            A(f"      job_arm_lists_are_A_plus_R_of_A: {str(v['job_arm_lists_are_A_plus_R(A)']).lower()}")
    # ---------------- J3 ----------------
    g = j3["gates_G4_G7"]
    A("  J3:")
    A("    gates_from_rows:")
    A(f"      instances_checked: {g['instances']}")
    for x in ["G4", "G5", "G6", "G7"]:
        A(f"      {x}_pass: {str(g[x + '_pass']).lower()}   # failures: {len(g[x + '_fail'])}")
    A(f"      G5_identity_recomputed_failures: {len(g['G5_recomputed_fail'])}")
    A(f"      checks_keys_seen: {json.dumps(g['checks_keys_seen'])}")
    A(f"      censored_flag_vs_attempts_lt_A_fix_disagreements: {len(g['cens_crosscheck_disagree'])}")
    A("      scope_note: G4 cert counts and k_verified, G6/G7 check flags are the recorded fields; G5 identity and the G6 rank equalities are recomputed from fields. kP = Q itself cannot be re-verified from the rows (no k, P or Q coordinates are recorded).")
    A("    Q2_A1_cells:")
    A("      columns: [arm, class, m, bits, C_A, C_R, kappa, sum_s2, V, SD_null, z, resolved, raw_kappa, curves_used, curves_dropped]")
    A("      rows:")
    for c in j3["A1_cells"]:
        dr = [[d["curve"], d["reasons"]] for d in c["curves_dropped"]]
        A("        - " + json.dumps([c["arm"], c["class"], c["m"], c["bits"], c["C_A"], r6(c["C_R"]), r6(c["kappa"]),
                                    r6(c["sum_s2"]), r6(c["V"]), r6(c["SD_null"]), r6(c["z"]), c["resolved"],
                                    r6(c["raw_kappa"]), c["curves_used"], dr]))
    A("    Q2_sensitivity_CV1_censoring_SS_only: " + json.dumps({k: {kk: r6(vv) for kk, vv in v.items()} for k, v in j3["A1_sensitivity_censoring_SS_only"].items()}))
    A("    Q3:")
    A(f"      resolved_TT_SS_cells: {j3['resolved_family_size']}   # of {j3['cells_total_TT_SS']}")
    A("      excursions:")
    for e in j3["excursions"]:
        A("        - " + json.dumps({k: r6(v) for k, v in e.items()}))
    t = j3["A2_tail_check"]
    A(f"      A2_tail_check: {json.dumps({k: r6(v) for k, v in t.items()})}")
    A(f"      tail_largest_resolved_kappa: {json.dumps(j3['tail_largest_kappa'])}")
    A(f"      tail_smallest_resolved_kappa: {json.dumps(j3['tail_smallest_kappa'])}")
    A("      A2_tests:")
    for k, v in sorted(j3["A2"].items()):
        ent = {"status": v["status"], "rungs": v["resolved_rungs"], "slope": r6(v.get("slope")), "lo": r6(v.get("lo")),
               "hi": r6(v.get("hi")), "p_one_sided": r6(v.get("p_one_sided")), "holm_adjusted_p": r6(v.get("holm_adjusted_p")),
               "replicates_undefined": v.get("replicates_undefined")}
        if v.get("x_b") is not None:
            ent["x_b"] = [r6(x) for x in v["x_b"]]
            ent["y_b"] = [r6(x) for x in v["y_b"]]
            ent["replicates_used"] = v.get("replicates_used")
        if "mc_sd" in v:
            ent["mc_sd_seeds_1_20"] = {kk: r6(vv) for kk, vv in v["mc_sd"].items() if kk != "seeds"}
            ent["xb_used_sensitivity"] = {kk: r6(vv) for kk, vv in v["xb_used_sensitivity"].items()}
        A(f"        {k}: {json.dumps(ent)}")
    A("      O_ALIVE_conditions:")
    for a in j3["O_ALIVE_conditions"]:
        A("        - " + json.dumps(a))
    A("      A3_median_rho_by_arm_class_m: " + json.dumps({k: {"n": v["n"], "median": r6(v["median"])} for k, v in j3["A3_median_by_arm_class_m"].items()}))
    A(f"      R15_outcome_id: {j3['R15_outcome_id']['id']}")
    A(f"      R15_outcome_conditional_on: {yq(j3['R15_outcome_id']['conditional_on'])}")
    A("    Q4_stage_r:")
    for s in j3["stage_r"]:
        c = s["stage_r"]
        A("      - " + json.dumps({"cell": s["cell"], "discovery_z": r6(s["discovery_z"]), "stage_r_z": r6(c["z"]),
                                  "stage_r_kappa": r6(c["kappa"]), "C_A": c["C_A"], "C_R": r6(c["C_R"]), "V": r6(c["V"]),
                                  "resolved": c["resolved"], "curves_used": c["curves_used"],
                                  "curves_dropped": c["curves_dropped"], "counts_A": c["counts_A"], "counts_R": c["counts_R"],
                                  "same_sign_and_abs_z_gt_3": s["replicated"]}))
    A(f"    final_structural_reading: {yq(j3['final_structural_reading'])}")
    A(f"    stage_r_cells_equal_my_excursion_list: {str(sorted(map(tuple, j3['stage_r_layout_vs_my_excursions'])) == sorted((x[0], x[1], x[2]) for x in j2a['R16']['excursion_cells_from_layout'])).lower()}")
    a4 = j3["A4"]
    A("    Q5_A4:")
    A(f"      pred_1a: {a4['pred_1a']}   # medians >= 1.3: {a4['pred_1a_count_ge_1.3']} of 50")
    A(f"      pred_1b: {a4['pred_1b']}   # |delta| <= 0.03: {a4['pred_1b_count_within_0.03']} of 10 (m = 3, 5)")
    A(f"      pred_2: {json.dumps({k: r6(v) for k, v in a4['pred_2'].items()})}")
    A(f"      excluded_instances: {json.dumps(a4['excluded'])}")
    A("      medians: " + json.dumps({k: [v["n"], r6(v["median"])] for k, v in a4["medians"].items()}))
    A("      fits:")
    for k, v in sorted(a4["fits"].items()):
        ent = {"n": v["n"], "census": [r6(v["census"]["slope"]), r6(v["census"]["lo"]), r6(v["census"]["hi"])],
               "on": [r6(v["on"]["slope"]), r6(v["on"]["lo"]), r6(v["on"]["hi"])], "delta": r6(v["delta"]),
               "delta_ci_seed0": [r6(x) for x in v["delta_ci"]], "mc_sd_seeds_1_20": {kk: r6(vv) for kk, vv in v["mc_sd"].items() if kk != "seeds"}}
        A(f"        {k}: {json.dumps(ent)}")
    s6 = q6s["summary"]
    A("    Q6_formal_duplicates:")
    A(f"      block_counts: {json.dumps(s6['counts'])}")
    A(f"      mismatch_counts: {json.dumps(s6['mismatch_counts'])}")
    A(f"      problems: {json.dumps(q6s['problems'])}")
    A(f"      missing_blocks: {len(q6s['missing_blocks'])}")
    A("      findings: >-")
    A("        Complete-retention blocks only. TT and TB: pairs_raw recomputed from the star")
    A("        rows equals the recorded value in every block; no emitted row has a zero")
    A("        oriented difference; no cert_ok false; generic arms carry no formal flag and")
    A("        pairs_formal = 0; known_log formal flags (log-sum rule) match the recorded")
    A("        flags in every block. SS: the recorded pairs_raw is LOWER than sum C(k',2)")
    A("        over the star-row groups in "
      + f"{s6['mismatch_counts'].get('pairs_raw', 0)} blocks at the stop and {s6['mismatch_counts'].get('ss_pairs_raw_at_A_fix', 0)} at A_fix (never higher).")
    A("        Five size-3 groups in (R10, 32, curve 0, m3, subgroup, census, SS) give 4549")
    A("        by the IC-5 definition against 4548 recorded. Mechanism unknown before the")
    A("        seal (harvest.py is blind_from). j0 formal flags: blocked (no base")
    A("        coordinates in the committed rows).")
    A(f"      A1_SS_recount_impact: {json.dumps({'cells_recomputable': q6i['cells_recomputable'], 'cells_not_recomputable': q6i['cells_not_recomputable'], 'SS_excursions_recorded_fields': q6i['SS_excursions_recorded_fields'], 'SS_excursions_recount_where_recomputable': q6i['SS_excursions_recount_where_recomputable'], 'stage_r': q6i['stage_r']})}")
    mx = max((abs(x["z_recorded"] - x["z_recount"]), x["arm"], x["m"], x["bits"]) for x in q6i["main"]
             if x["recomputable"] and x["z_recorded"] is not None and x["z_recount"] is not None)
    A(f"      A1_SS_recount_max_abs_dz: {json.dumps([r6(mx[0]), mx[1], mx[2], mx[3]])}")
    A("    Q7:")
    p1, p2 = j3["PC1"], j3["PC2"]
    A(f"      PC1: {json.dumps({'raw_kappa_TT': r6(p1['raw_kappa_TT']), 'raw_C_A': p1['cell']['raw_C_A'], 'raw_C_R': r6(p1['cell']['raw_C_R']), 'units_used': p1['cell']['units_used'], 'units_dropped': p1['cell']['units_dropped'], 'rho_TT_TB_le_0.05_all_qualifying': p1['rho_TT_TB_le_0.05_all'], 'qualifying': p1['known_log_qualifying'], 'pass': p1['pass']})}")
    A(f"      PC2: {json.dumps({'kappa_TB_before': r6(p2['kappa_TB_before']), 'raw_C_A': p2['cell']['raw_C_A'], 'raw_C_R': r6(p2['cell']['raw_C_R']), 'nonformal_C_A': p2['cell']['C_A'], 'nonformal_C_R': r6(p2['cell']['C_R']), 'V': r6(p2['cell']['V']), 'z_nonformal': r6(p2['z_nonformal']), 'resolved': p2['resolved'], 'units_used': p2['cell']['units_used'], 'units_dropped': p2['cell']['units_dropped'], 'G6_rank_2F_over_3_all_j0_coset': p2['G6_rank_2F_over_3_all_j0_coset'], 'pass': p2['pass']})}")
    A("      PC2_scope_note: the nonformal TB counts are the recorded fields; their j0 formal flags are not independently recomputed (Q6 blocked).")
    tw = j3["TW_FLOOR"]
    A("    Q8_TW_FLOOR:")
    A(f"      fired: {str(tw['fired_R10_R14']).lower()}")
    A(f"      firing_instances: {tw['count_R10_R14']}")
    A("      firing_keys_panel_bits_curve_m_arm_mode: " + json.dumps(tw["keys_R10_R14"]))
    A(f"      instances_evaluated: {tw['instances_evaluated_R10_R14']}")
    A("      not_evaluable_r_zero_keys: " + json.dumps(tw["not_evaluable_r_zero"]))
    A(f"      stage_r_R16_fired: {str(tw['fired_R16']).lower()}   # {tw['count_R16']} of {tw['instances_evaluated_R16']} evaluated")
    A("      second_disjunct_EXP_PFDR_7c8bf2_OUT_FLOOR_VIOLATION: SEE_ADDENDUM_LINE_BELOW")
    A("      note: no floor ratio was written or printed; the predicate was evaluated in memory (RV-4).")
    A("    Q9:")
    A("      A6_KS: " + json.dumps({k: {"n": v["n"], "D": r6(v["D"]), "p": r6(v["p"]), "reject_1pct": v["reject_1pct"]} for k, v in a6["ks"].items()}))
    A("      A6_tail_flags_lt_0.001: " + json.dumps({k: [v["instances"], v["max_count"], r6(v["P_max_ge"])] for k, v in a6["tail"].items() if v["flag_lt_0.001"]}))
    A(f"      A6_excluded: {json.dumps(a6['excluded'])}")
    A(f"      A6_selfcheck: {json.dumps({k: r6(v) for k, v in a6['selfcheck'].items()})}")
    A("      H3_rank_ratio_tally_recorded_fields: " + json.dumps(j3["H3_rank_ratio_tally"]))
    if h3 is not None:
        A("      H3_recomputed_checks: " + json.dumps(h3["checks"]))
        A("      H3_permutation_stability_tally_bits_le_24: " + json.dumps(h3["tally"]))
    else:
        A("      H3_permutation: blocked (not computed before the seal)")
    A("    A3_prediction4: " + json.dumps({k: {kk: r6(vv) for kk, vv in v.items()} for k, v in j3["A3_prediction4"].items()}))
    A(f"    unmatched_size_instances: {json.dumps(j3['unmatched_size_instances'])}")
    A("    monte_carlo_note: A2 and A4 bootstrap endpoints are reported at the declared seed 0 with their s.d. over seeds 1..20 (mc_sd); deterministic quantities (counts, kappa, V, z, medians, slopes, outcome ids) carry no Monte Carlo error.")
    text = "\n".join(L) + "\n"
    return text


if __name__ == "__main__":
    text = main()
    extra = sys.argv[1] if len(sys.argv) > 1 else None
    if extra:
        text = text.replace("SEE_ADDENDUM_LINE_BELOW", extra)
    with open(SEALED, "x") as f:
        f.write(text)
    print("written", SEALED, len(text))
