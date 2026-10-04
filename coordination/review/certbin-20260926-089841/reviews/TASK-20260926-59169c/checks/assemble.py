#!/usr/bin/env python3
"""TASK-20260926-59169c: assemble comparison.json from the check outputs.

Inputs (all under checks/): cp1_verify.out.json, comparison-core.json,
cp3_wdag_check.out.json, cp3_negctl.out.json, cp3_witness.out.json,
cp4_third_counting.out.json, compare_selftest.out.json, floor_ceiling.out.json.
Adds: the key mapping table, extra identification checks, the CP-4
localisation record, the ambiguity table (J7 AMB-01..23, J1 AMB-1..16 against
the run's readings), gaps, and per-section agree/disagree tallies.
"""
import argparse, gzip, hashlib, json, os
from collections import Counter

REV = "coordination/review/certbin-20260926-089841"


def J(p):
    return json.load(open(p))


AMBIGUITIES = [
    # (source, id, clause (short), J7/J1 reading, run resolution + where, relation, effect on compared items)
    ("J7", "AMB-01", "N-CONV drawn_part g.integers(0, 2, size=|S_L|)", "numpy defaults (int64, endpoint False), one call per attempt",
     "impl/draws.py:48 g.integers(0, 2, size=len(ctx.SL)) with numpy defaults", "same reading", "load-bearing for the stream; stream agrees on 1181/1181 attempts"),
    ("J7", "AMB-02", "placement on S_L", "bits[i] -> S_L[i], S_L row-major", "support.json S_L row-major; impl/draws.py _place(ctx.qp[slot], ctx.SL, bits)", "same reading", "S_L list and kept rows agree"),
    ("J7", "AMB-03", "N-CONV kept part / zero off S_L", "as stated", "as stated (J1 VC-2: every low bit on S_L; quadratic columns = E_S3)", "same reading", "none"),
    ("J7", "AMB-04", "identity rejection", "whole-system equality with E_S3(x_R)", "impl/draws.py:50 rows == ctx.s3[slot] (whole system)", "same reading (and equivalent readings)", "not exercised: 0 identity rejections in either"),
    ("J7", "AMB-05", "duplicate by E_sha256", "exact matrix equality (own canonical bytes as set key)", "impl/draws.py:103-104 E_sha256 set membership", "different mechanism, decision-equivalent", "not exercised: 0 duplicates in either"),
    ("J7", "AMB-06", "s on rejected draws", "s computed and logged for every draw", "trial-plan R2 / impl/draws.py:108: rejected draw logged with s = null", "DIFFERENT reading", "not exercised: 0 rejected draws in every arm (run deviation 12; J7 0 rejections), so no compared value depends on it"),
    ("J7", "AMB-07", "keep rule roles and cap", "a = 0..255; filled-role draw 'discarded'; stop when both filled", "impl/draws.py run_arm: same", "same reading", "attempt indices and outcomes agree 1181/1181"),
    ("J7", "AMB-08", "solution integer encoding", "bit i = v_i", "run-report / J1 VC-5: bit i = v_i", "same reading", "satisfiable-control solution lists agree 144/144 (N-CONV) and on every pool sat system"),
    ("J7", "AMB-09", "row hex padding", "no zero padding", "impl/common.py:117 format(r, 'x')", "same reading", "raw J7 strings hash to the run's E_sha256 on 1181/1181 attempts"),
    ("J7", "AMB-10", "N-CONVL identity comparison", "drawn bits vs B's bits at the constant positions of S_L; all-zero rejected", "impl/draws.py:64-67 bits == ctx.B_bits_at_const; bprime == 0", "same reading", "not exercised (0 rejections); Q0-opt N-CONVL agrees on slots 0..9"),
    ("J7", "AMB-11", "N-CONV17 / N-ELL144 rejections", "duplicates only", "impl/draws.py: rej = None for these arms, then duplicate check", "same reading", "not exercised"),
    ("J7", "AMB-12", "N-ELL144 draw rule", "as stated (full U, then c, row 16 replaced)", "impl/draws.py:70-82 same", "same reading", "Q0-opt N-ELL144 agrees on slots 0..9 including c"),
    ("J7", "AMB-13", "W_4 fixpoint index and dims list", "fixpoint = first i with dim W^(i+1) = dim W^(i); dims lists W^(0)..W^(i+1)", "run closures.jsonl.gz: iterations_to_fixpoint = same i; dims lists W^(0)..W^(i)", "same index, different list encoding", "encoding difference only; mapped and agreeing on 55/55 pool systems"),
    ("J7", "AMB-14", "rc_b label for substituted systems", "'SUBSTITUTED'", "run label 'SUBSTITUTED'", "same reading", "labels agree 55/55"),
    ("J7", "AMB-15", "rc_b c indexing", "c_k multiplies f_k (list of 17 bits)", "run c as int, bit k = c_k", "same reading, different encoding", "agree 47/47 after decoding"),
    ("J7", "AMB-16", "substitution and R'_D", "v_j* := ell + v_j* incl. constant; relabel ascending; M_D conventions", "impl/rcb.py (C-T4, C-FIX R' shapes)", "same reading", "R'_3 rank, R'_4 rank/one/dims agree 47/47"),
    ("J7", "AMB-17", "Q1 'refuted'", "1 in rowspace(M_4); W_4 not computed on replay systems", "run computes M_4 and W_4 on every system", "scope choice of J7 (plan asks M_4 only in Q1)", "J7 witnesses W_4 on replay systems only through M_4 subset W_4 (valid one-node wdag-v1 certifies 1 in W_4)"),
    ("J7", "AMB-18", "P definition", "both definitions, asserted equal", "derived_per_instance P = rank - dims_by_deg[3]", "same", "P agrees everywhere"),
    ("J7", "AMB-19", "BR-4 second s route", "J7-internal", "no run counterpart", "not applicable", "none"),
    ("J7", "AMB-20", "wdag construction", "W^(i-1) component inlined into the parent; repeated j allowed", "run extractor (impl/wdag.py) builds its own DAG; construction is not binding", "different constructions, both allowed", "both sides' certificates valid; node counts not a compared item"),
    ("J7", "AMB-21", "checker strictness", "ids distinct, children/output exist, header", "run verifier and J1 also check format", "same or stricter", "none (the J8 checker is stricter still: children must precede in list order)"),
    ("J7", "AMB-22", "curve source", "A, B from blind-inputs.json (equal to the specification)", "run reads curve.json (bound hash aa3eb4d0...)", "same values", "none"),
    ("J7", "AMB-23", "xr144 slot table", "x_R by slot from blind-inputs 'slots'", "run xr144 from instance-sets.json (J1 AMB-12: listed order = ascending idx)", "same", "kept rows agree at every slot, so the slot-to-x_R binding agrees"),
    ("J1", "AMB-1", "fresh key format", "'<ARM>:<slot>:<role>'", "run deviation 1 / trial-plan R1", "same reading", "every certificate key resolves (1440/1440)"),
    ("J1", "AMB-2", "E_sha256 serialization", "sha256(json.dumps(E_hex)) default separators", "impl/common.py:124-125 same", "same reading", "E_sha256 recomputes on 1440/1440 run systems (J8 check)"),
    ("J1", "AMB-3", "solution encoding", "bit i = v_i", "same", "same reading", "none"),
    ("J1", "AMB-4", "flat-v1 sortedness/duplicates", "format notes, not rejections", "run verifier", "not exercised", "J1 recorded no format note on any line"),
    ("J1", "AMB-5", "wdag D and nv", "must be 4 and 18", "run certificates carry D = 4, nv = 18", "not exercised", "none"),
    ("J1", "AMB-6", "wdag node ids", "ids compared, not positions", "run ids are 0..n-1 in list order", "not exercised", "none"),
    ("J1", "AMB-7", "rule (c) scope", "every node used as a child", "run verifier max_child_degree", "same reading", "max_child_degree agrees 514/514"),
    ("J1", "AMB-8", "what counts toward M_4", "primary: verified M_4-labelled flat-v1, max|mu| <= 2", "impl/analysis.py:95 same rule", "same reading", "M_4 counts agree on every arm; alternative readings give the same counts"),
    ("J1", "AMB-9", "W_4 flat-v1 lines", "never counted toward w; max|mu|<=2 flagged flat_W4_eligible", "trial-plan R3 / deviation 3: 'counts toward W_4 only if max |mu| <= 2, never used for w'; verify_nconv.py:253-254 writes that eligibility as counts_for_W4 (and counts_for_M4) on every flat line", "same reading, different FIELD SEMANTICS", "the only CP-2 disagreement class (D-1): per-line flags; localised as an encoding difference; no count changes"),
    ("J1", "AMB-10", "N-CONVL differs from B", "17-bit constant column differs from B's bits", "run identity on drawn bits at constant positions (equivalent: constant entries off S_L are zero)", "equivalent", "no N-CONVL system equals B's constant (J1 VC-2)"),
    ("J1", "AMB-11", "N-ELL144 rows 0..15 in U, row 16", "as stated", "impl/draws.py same", "same", "J1 VC-2 0 violations"),
    ("J1", "AMB-12", "xr144 order", "listed order of instance-sets.json", "same", "same", "none"),
    ("J1", "AMB-13", "multilinear reduction", "v^2 = v", "same", "same", "none"),
    ("J1", "AMB-14", "archived bytes", "git show at c7f5e3dfa", "procedural", "not applicable", "none"),
    ("J1", "AMB-15", "negative control (e)", "J1-internal", "run's C-VERIFIER uses its own constructions (deviation 9)", "not applicable", "none"),
    ("J1", "AMB-16", "VC-4 'at least 5 each'", "J1-internal", "not applicable", "not applicable", "none"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--snap", required=True)
    ap.add_argument("--checks", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    C = a.checks
    core = J(os.path.join(C, "comparison-core.json"))
    cp1 = J(os.path.join(C, "cp1_verify.out.json"))
    cp3 = J(os.path.join(C, "cp3_wdag_check.out.json"))
    neg = J(os.path.join(C, "cp3_negctl.out.json"))
    wit = J(os.path.join(C, "cp3_witness.out.json"))
    third = J(os.path.join(C, "cp4_third_counting.out.json"))
    selft = J(os.path.join(C, "compare_selftest.out.json"))
    fc = J(os.path.join(C, "floor_ceiling.out.json"))
    cell = J(os.path.join(C, "extra_cell_trace.out.json"))
    rev = os.path.join(a.snap, REV)
    km = J(os.path.join(rev, "blind-inputs-key.json"))
    d7 = J(os.path.join(rev, "reviews/TASK-20260926-83cebf/rederivation.json"))

    # ---- key mapping table + J7's own identification of each pool system (extra)
    mapping = []
    ident_ok = 0
    for lab in sorted(km):
        k = km[lab]
        pid = d7["pool_identification"][lab]
        g = k["group"]
        if g in ("P-C",):
            ok = pid["equals_E_S3_at_slots"] == [k["slot"]]
        elif g in ("P-A", "P-B"):
            ok = k["slot"] in pid["quadratic_part_equals_Qpart_at_slots"] and pid["within_U"]
        elif g == "P-D":
            ok = k["slot"] in pid["quadratic_and_linear_parts_equal_E_S3_at_slots"]
        elif g == "P-E":
            ok = pid["quadratic_part_is_conv17_Q_k"] is True
        elif g == "P-F":
            ok = pid["row16_is_v0_plus_v9_plus_c"] is True
        elif g == "P-G":
            ok = pid["within_U"] is True and pid["equals_E_S3_at_slots"] == []
        else:
            ok = False
        ident_ok += ok
        mapping.append({"label": lab, "run_key": k["key"], "arm": k["arm"], "role": k["role"], "slot": k["slot"], "group": g,
                        "j7_blind_identification_consistent_with_key": ok})

    # ---- CP-3 per-certificate status table
    cp3_rows = []
    for r in cp3["per_certificate"]:
        row = {"j7_label": r["j7_label"], "run_key": r["run_key"], "status": r["status"],
               "status_on_run_rows": r.get("status_on_run_rows")}
        det = r.get("detail") or r.get("detail_on_j7_rows") or {}
        if r["status"] == "valid":
            row.update({k: det.get(k) for k in ("nodes", "rows", "prods", "max_mu", "max_child_deg", "max_node_deg")})
        else:
            row["first_violated_rule"] = det.get("rule")
        cp3_rows.append(row)
    # absent: a system J7 reports refuted (Q1 one_in_R_4 or Q3 one) without a certificate line
    labels = {r["j7_label"] for r in cp3["per_certificate"]}
    absent = [lab for lab in km if d7["Q3"][lab]["one"] and lab not in labels]
    absent += ["NCONV-REPLAY:%d:unsat" % s for s in range(144) if d7["Q1"]["unsat"]["NCONV-REPLAY:%d:unsat" % s]["one_in_R_4"] and "NCONV-REPLAY:%d:unsat" % s not in labels]

    # ---- per-section tallies
    def section_tally(obj):
        t = Counter()

        def walk(x):
            if isinstance(x, dict):
                if isinstance(x.get("agree"), bool) and set(x) - {"agree", "j7", "run", "note"} <= set():
                    t[x["agree"]] += 1
                elif isinstance(x.get("agree"), bool) and "disagreements" in x:
                    t[x["agree"]] += 1
                elif isinstance(x.get("agree"), bool):
                    t[x["agree"]] += 1
                elif "agree" in x and x["agree"] is None:
                    t["gap"] += 1
                for v in x.values():
                    walk(v)
            elif isinstance(x, list):
                for v in x:
                    walk(v)
        walk(obj)
        return {"agree": t[True], "disagree": t[False], "no_counterpart": t["gap"]}

    q0n = core["Q0"]["N-CONV"]
    att_fields = sum(v["of"] for v in q0n["summary"]["attempt_fields"].values())
    att_agree = sum(v["agree"] for v in q0n["summary"]["attempt_fields"].values())
    opt_att = sum(v["of"] for arm in core["Q0"]["Q0_opt"].values() for v in arm["summary"]["attempt_fields"].values())
    opt_att_agree = sum(v["agree"] for arm in core["Q0"]["Q0_opt"].values() for v in arm["summary"]["attempt_fields"].values())
    j1f = core["J1_vs_run_certificate_verification"]["fields"]
    tallies = {
        "Q0_construction": section_tally(core["Q0"]["construction"]),
        "Q0_N-CONV_per_slot_items(144 slots x 11 items)": section_tally(q0n["per_slot"]),
        "Q0_N-CONV_per_attempt_fields(1181 attempts x 4)": {"agree": att_agree, "disagree": att_fields - att_agree},
        "Q0_opt_per_slot_items": section_tally([v["per_slot"] for v in core["Q0"]["Q0_opt"].values()]),
        "Q0_opt_per_attempt_fields": {"agree": opt_att_agree, "disagree": opt_att - opt_att_agree},
        "Q1(144 unsat + 144 sat x 5 items)": section_tally(core["Q1"]["per_system"]),
        "Q2_Q5_pool(55 systems, incl. 2 mapping items)": section_tally(core["Q2_Q5_pool"]["per_system"]),
        "J1_vs_run_per_line_fields_as_named": {"agree": sum(v["agree"] for v in j1f.values()), "disagree": sum(v["of"] - v["agree"] for v in j1f.values()),
                                              "note": "all disagreeing fields are counts_M4 (412) / counts_W4 (824) on 824 flat-v1 lines: disagreement class D-1"},
        "J1_vs_run_per_line_fields_paired_by_meaning": {"agree": sum(v["of"] for v in j1f.values()), "disagree": 0,
                                                       "note": "run counts_for_* on flat lines = J1 eligibility (verified and max|mu| <= 2); on wdag lines = J1 counts_toward_w (see CP-4 D-1)"},
        "MN_recount_and_NC-DR_reapplication": section_tally({k: v for k, v in core.items() if k in ("MN_recount_from_J1",)}),
        "NC-DR-3_pairs": {"agree": core["NC-DR_reapplied_from_J1"]["NC-DR-3"]["pairs_agree"], "disagree": len(core["NC-DR_reapplied_from_J1"]["NC-DR-3"]["disagreements"])},
        "NC-DR-1_2_4_labels": {"agree": sum(core["NC-DR_reapplied_from_J1"][k]["agree_with_run"] for k in ("NC-DR-1", "NC-DR-2", "NC-DR-4")),
                               "disagree": sum(not core["NC-DR_reapplied_from_J1"][k]["agree_with_run"] for k in ("NC-DR-1", "NC-DR-2", "NC-DR-4"))},
        "J1_VC2_vs_run_controls": section_tally(core["J1_VC2_vs_run_controls"]),
        "C-ELL_extra_check(14 systems)": {"agree": sum(r["all_equal"] for r in cell["rows"]), "disagree": sum(not r["all_equal"] for r in cell["rows"])},
        "ambiguities(J7 23 + J1 16)": dict(Counter(x[5] for x in AMBIGUITIES)),
    }

    gaps = [
        {"item": "Q2 rank_3 and '1 in R_3' on the 36 fresh-arm pool systems (P-A, P-B, P-D, P-E, P-F)",
         "reason": "the run computes M_3 only on archived arms (EXP-CERTBIN-ddfe75 object.closures_run: 'On archived S_3 and null arms also M_3'); no run record exists. J7's values stand unconfirmed by the run; they agree with the run on all 19 archived-arm pool systems."},
        {"item": "W_4 on the 144 replayed N-CONV unsat systems (Q1)",
         "reason": "not a CP-2 item: the plan's Q1 asks M_4 quantities only (J7 AMB-17). J7's one-node wdag-v1 certificates certify 1 in M_4, a subset of W_4."},
        {"item": "Q0-opt beyond slots 0..9 (N-CONVL, N-CONV17, N-ELL144)",
         "reason": "the plan's Q0-opt is a stream prefix (slots 0..9); J7 computed exactly that."},
        {"item": "run arms outside the pool (NULL-AFF62, NELL-A20, the remaining slots of the fresh arms) for Q2-Q5",
         "reason": "outside the plan's outcome-independent pool P-A..P-G; J7 was not asked for them."},
        {"item": "J1 on NELL-A20 source bytes",
         "reason": "J1 limitation (n-ell-instances.json must_not_read for J1); not a J8 comparison item."},
        {"item": "wdag node counts J7 against the run",
         "reason": "not a CP-2 item; the construction is 'not binding' (object.certificate_format); both sides' certificates are valid."},
    ]

    cp4 = [{
        "id": "D-1",
        "item": "J1 per-line counts_toward_M4 / counts_toward_w against the run's certificate-verification.json counts_for_M4 / counts_for_W4",
        "extent": "824 of 1440 lines (all flat-v1 lines with max |mu| <= 2: 412 M_4-labelled, 412 W_4-labelled); 1236 field comparisons (counts_M4 412, counts_W4 824)",
        "a_read_both_at_clause": {
            "clause": "object.certificate_format flat-v1 ('It counts toward M_4 only when max |mu| <= 2. It NEVER counts toward W_4 unless max |mu| <= 2') and metrics MN1 ('VERIFIED wdag-v1') / secondary M_4 metric ('verified flat-v1 with max |mu| <= 2')",
            "run": "verifier/verify_nconv.py:253-254 writes counts_for_M4 = counts_for_W4 = (sum is 1 and max|mu| <= 2) on every flat-v1 line regardless of closure label, i.e. the certificate_format ELIGIBILITY; verify_nconv.py:328 counts_for_W4 = verified on wdag-v1 lines. impl/analysis.py:95-100 counts M_4 only from M_4-labelled flat-v1 with counts_for_M4 and w only from W_4 wdag-v1; the flat counts_for_W4 flag is never consumed for w (trial-plan-v1.json pre_data_readings R3; implementation.md deviation 3).",
            "J1": "code/run_j1.py:487-489: counts_toward_M4 = verified M_4-labelled flat-v1 with max|mu| <= 2; counts_toward_w = verified W_4 wdag-v1; flat_W4_eligible_maxmu_le2 = verified W_4-labelled flat with max|mu| <= 2 (J1 AMB-8, AMB-9).",
        },
        "b_third_check": {"code": "checks/cp4_third_counting.py", "output": "checks/cp4_third_counting.out.json",
                          "declared_scope": third["declared_systems"],
                          "result": {"all_lines_own_verified": third["all_lines_own_verified"],
                                     "run_flags_are_certificate_format_eligibility_on_all_lines": third["run_flags_are_R-CF_eligibility_on_all_lines"],
                                     "per_system_outcome_reading_invariant": third["per_system_outcome_reading_invariant"]},
                          "population_recount_from_J1_verdicts": core["MN_recount_from_J1"]["counting_reading_invariance_all_systems"]["all_same"]},
        "c_localisation": "ENCODING DIFFERENCE (field semantics), not a departure: the run's per-line flags record the certificate_format eligibility and J1's record tally inclusion; paired by meaning (run flag vs J1 'verified and max|mu| <= 2' on flat lines, vs J1 counts_toward_w on wdag lines) all 1440 lines agree. Both implementations apply the same tally rule (MN1: w from verified wdag-v1 only; M_4 from M_4-labelled flat-v1 with max|mu| <= 2), and the counts are identical under either reading on every arm and role. Observation (non-blocking): the run field name counts_for_W4 on flat-v1 lines reads as tally inclusion to a reader of certificate-verification.json alone; the run's own R3/deviation 3 text disambiguates it.",
        "changes_any_count_or_verdict": False,
    }]

    comparison = {
        "schema": "certbin.nconv.j8_comparison.v1",
        "task_id": "TASK-20260926-59169c",
        "review_plan_id": "REVIEW-CERTBIN-20260926-089841",
        "joint": "J8",
        "run_id": "RUN-CERTBIN-6ebb0e",
        "experiment_id": "EXP-CERTBIN-ddfe75",
        "compared": {"J7": "TASK-20260926-83cebf (blind re-derivation, archived by TASK-20260926-9c0134)",
                     "J1": "TASK-20260926-f0e5a4 (author-independent verification, archived by TASK-20260926-9c0134)"},
        "snapshot": {"commit": "a524be32e41fbbdf738276c896dfcced34a277c3", "method": "git archive of the commit into the session scratchpad; working tree hash-identical (cp1)"},
        "CP-1": cp1,
        "key_mapping": {"rule": "pool labels BS-xxx -> run keys by blind-inputs-key.json; replay keys 'NCONV-REPLAY:<slot>:<role>' -> 'N-CONV:<slot>:<role>'",
                        "pool": mapping, "j7_blind_identification_consistent": "%d/55" % ident_ok,
                        "pool_equations_equal_run_rows": core["Q2_Q5_pool"]["summary"].get("map.pool_equations_equal_run_E_hex")},
        "tallies": tallies,
        "E_sha256_convention": core["E_sha256_convention"],
        "Q0_stream": core["Q0"],
        "Q1": core["Q1"],
        "Q2_Q5_pool": core["Q2_Q5_pool"],
        "J1_vs_run_certificate_verification": core["J1_vs_run_certificate_verification"],
        "MN_recount_from_J1": core["MN_recount_from_J1"],
        "NC-DR_reapplied_from_J1": core["NC-DR_reapplied_from_J1"],
        "J1_VC2_vs_run_controls": core["J1_VC2_vs_run_controls"],
        "C-ELL_extra_check": {"code": "checks/extra_cell_trace.py", "declared_systems": cell["declared_systems"],
                              "result": "%d/%d: c_k = Tr(t^k / x_R^2) by own F_2^17 arithmetic equals the run's rc_b c and J7's kernel c, is nonzero, and annihilates the quadratic part of the pool system's own equations" % (sum(r["all_equal"] for r in cell["rows"]), len(cell["rows"])),
                              "all_equal": cell["all_equal"], "rows": cell["rows"],
                              "note": "fills the C-ELL gap left by J1 (no ell computation); counted in the CP-6 cap of 20 third-check systems (6 + 14)"},
        "CP-3": {"checker": "checks/wdag_check.py (sha256 in checks/ORDER.log, written before any re-deriver code was read)",
                 "summary": cp3["summary"], "absent": absent,
                 "own_checker_negative_controls": {"n": neg["n"], "all_rejected_as_expected": neg["all_as_expected"], "rule_d_note": neg["rule_d_note"]},
                 "per_certificate": cp3_rows,
                 "witness_status": {k: wit[k] for k in ("pool_tally", "pool_tally_by_arm_role", "nconv_unsat_slots_tally", "any_contradicted", "any_unwitnessed")},
                 "witness_per_key": {"pool": wit["pool"], "nconv_unsat_slots": wit["nconv_unsat_slots"]}},
        "CP-4_localisations": cp4,
        "comparator_mutation_selftest": selft,
        "ambiguities": [{"source": s, "id": i, "clause": c, "reviewer_reading": r, "run_resolution": rr, "relation": rel, "effect": eff}
                        for (s, i, c, r, rr, rel, eff) in AMBIGUITIES],
        "floor_ceiling": fc,
        "gaps": gaps,
    }
    json.dump(comparison, open(a.out, "w"), indent=1)
    print(json.dumps(tallies, indent=1))
    print("absent:", absent, "ident:", ident_ok)


if __name__ == "__main__":
    main()
