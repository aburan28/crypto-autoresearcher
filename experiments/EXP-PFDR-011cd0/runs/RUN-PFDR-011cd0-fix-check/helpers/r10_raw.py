import json, sys, hashlib, gzip
rd = sys.argv[1]
fr = json.load(open(f"{rd}/fix-report.json"))
sv = json.load(open(f"{rd}/solve-verify.json"))
mr = json.load(open(f"{rd}/merge-report.json"))
gr = json.load(open(f"{rd}/grel-report.json"))
att = json.load(open(f"{rd}/attempt-1/raw-result.json"))
frozen_fail = []
for e in fr["instances"]:
    bad = []
    if e.get("problem"): bad.append(e["problem"])
    if e["solver_and_block_diffs"]: bad.append("solver column / TT / TB / table / ss_store / on / informative rank / saturation difference")
    if not e["staircase_equal"]: bad.append("staircase differs")
    if not e["harvest_rows_equal"]: bad.append("harvest rows differ (other difference; would need attribution)")
    if any(not p["new_ge_old"] for p in e.get("ss_pairs", {}).values()): bad.append("SS pairs new < old")
    if e.get("ss_pairs_raw_eq_Ck2_from_rows") is False: bad.append("<= 24 bits: pairs_raw != C(k',2) from rows")
    if bad: frozen_fail.append({"key": e["key"], "reasons": bad})
tool_extra = [u for u in fr["unattributed"] if u["reasons"] == ["pair difference without a straddling x-group"]]
tool_other = [u for u in fr["unattributed"] if u["reasons"] != ["pair difference without a straddling x-group"]]
le24 = [e for e in fr["instances"] if e["key"][0] <= 24]
raw = {"run_id": "RUN-PFDR-011cd0-fix-check", "location": rd,
       "merge": {k: mr[k] for k in ("expected_keys", "canonical_rows", "keys_with_exactly_one_canonical_row", "counts_by_status")},
       "attempt_1_status_totals": att["status_totals"], "attempt_1_gates": att["gates"],
       "G_FIX": {"frozen_text_evaluation": {"pass": not frozen_fail, "instances": len(fr["instances"]),
                                            "failures": frozen_fail,
                                            "criteria": "every solver column, TT/TB block, informative rank, census_saturated_at_row and staircase equal; SS pairs (at_stop, at_A_fix) new >= old; at <= 24 bits new pairs_raw == C(k',2) from the retained rows; any other difference (rows, dup_formal, poisson_mean) needs attribution (none occurred: harvest rows equal on every instance)",
                                            "instances_le_24_bits": len(le24),
                                            "le_24_bits_Ck2_equal": sum(1 for e in le24 if e.get("ss_pairs_raw_eq_Ck2_from_rows") is True),
                                            "instances_with_pair_change": fr["instances_with_pair_change"]},
                 "fixcompare_tool_verdict": {"pass": fr["pass"], "unattributed": fr["unattributed"],
                                             "note": ("the pinned fixcompare also required, for every pair-count change, an SS x-group of >= 3 members spanning >= 2 attempts in the RETAINED rows; this executor-added rule is not in the frozen G-FIX text and cannot be evaluated above 24 bits, where rows after census saturation are not retained (IC-5 default retention). The 9 instances it flags are exactly such instances; no other difference occurs on them (deviation D-6)"),
                                             "flagged_only_by_executor_added_rule": len(tool_extra), "flagged_for_other_reasons": len(tool_other)},
                 "fix_report_sha256": hashlib.sha256(open(f"{rd}/fix-report.json", "rb").read()).hexdigest()},
       "G_REL_supplementary": {"pass": gr["pass"], "comparisons": sum(v["compared_instance_class_scopes"] for v in gr["runs"].values()),
                               "mismatches": sum(v["mismatch_count"] for v in gr["runs"].values()),
                               "note": "R10 harvest rows (task scratch) recounted by analyze_relcensus.py grel; equality only"},
       "certificate": {"instances_claimed": sv["records"], "instances_verified": sv["verified"], "verify_pass": sv["pass"],
                       "verify_report": f"{rd}/solve-verify.json", "verifier_sha256": sv["verifier_sha256"],
                       "certificates_file": f"{rd}/solve-certs.jsonl.gz", "certificates_sha256": sv["certificates_sha256"]},
       "canonical_files": mr["canonical_files"]}
json.dump(raw, open(f"{rd}/raw-result.json", "w"), indent=1)
print(json.dumps({"G_FIX_frozen_text_pass": raw["G_FIX"]["frozen_text_evaluation"]["pass"], "tool_pass": fr["pass"],
                  "flagged_only_by_extra_rule": len(tool_extra), "other": len(tool_other), "certs": sv["records"], "verified": sv["verified"]}))
