#!/usr/bin/env python3
"""TASK-20260813-59c321 (Validator) -- probe 5 of 5.

AUDIT OF THE COMMITTED results_a1.json AGAINST ITSELF AND AGAINST report_a1.md.

This probe is ARITHMETIC-CLASS on the producer's own numbers: it checks the
producer's SUMMARIES against the producer's COMPLETE PER-CELL RECORD.  It
cannot see a defect in how those numbers were GENERATED; that is what
probe_rederive_a1.py is for, and the two classes are reported separately.

Specifically:
  1. every count in report_a1.md that the producer says was recomputed from
     the complete per_block record IS recomputed here from per_block, NOT
     from the summary and NOT from the truncated `instances` lists;
  2. the FC-3a / FC-3b `instances` truncation is measured: how many entries,
     what truncation count is recorded beside them, and whether the recorded
     total equals the count recomputed from per_block;
  3. the PREDICTION_REGISTER's P-A12a line is read as committed, and the
     report's correction to FALSIFIED at 22 cells is checked against the
     complete per-cell record;
  4. artifact policy: durable command/stdout/stderr, declared-vs-written
     path sets, no path inside a folded YAML scalar, run accounting, adapter
     binding;
  5. the not-citable list of PREREG-2 10.1 is searched for in report_a1.md.

Reads the 17 MB results file ONCE and drops it.  Writes exactly its --out path.
"""
import argparse
import hashlib
import json
import os
import re
import sys
from collections import OrderedDict

ROOT = "/home/user/crypto-autoresearcher"
T = ("coordination/goals/GOAL-MLKEM-005/batches/BATCH-6b6e78/tasks/"
     "TASK-20260813-2ce014")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    R = OrderedDict()
    R["probe"] = "probe_results_audit.py"
    R["task_id"] = "TASK-20260813-59c321"
    R["check_class"] = ("ARITHMETIC-CLASS: producer summaries vs producer "
                        "complete per-cell record.  Blind to generation "
                        "defects by construction.")

    res = json.load(open("%s/%s/results_a1.json" % (ROOT, T)))
    report = open("%s/%s/report_a1.md" % (ROOT, T)).read()
    manifest = open("%s/%s/run_manifest.yaml" % (ROOT, T)).read()

    # ------------------------------------------------- 1. recompute from per_block
    pb = res["R3_OUT_2_two_precision_table"]["per_block"]
    n_blocks = len(pb)
    n_cov = n_unc = 0
    chg_cells = 0
    chg_blocks = 0
    chg_route, chg_cand, chg_fam = {}, {}, {}
    fc2a = fc3a = fc3b = 0
    fc2a_cand, fc3a_cand, fc3b_cand, fc3b_route, fc2a_route = {}, {}, {}, {}, {}
    pdeg = 0
    strict_fals = 0
    sample_keys = list(pb.keys())[:2]
    R["per_block_record_shape"] = {
        "n_blocks": n_blocks,
        "example_block_key": sample_keys[0] if sample_keys else None,
        "example_block_fields": (sorted(pb[sample_keys[0]].keys())
                                 if sample_keys else None),
        "example_cell_fields": None,
    }
    for bk, blk in pb.items():
        cand = blk.get("candidate")
        route = blk.get("route")
        fam = blk.get("fibre_family")
        cells = blk.get("per_cell") or {}
        n_unc += 38 - len(cells)          # a cell absent from per_cell is
        #                                   an UNCOVERED declared cell
        bchg = 0
        for c in cells.values():
            if R["per_block_record_shape"]["example_cell_fields"] is None:
                R["per_block_record_shape"]["example_cell_fields"] = sorted(
                    c.keys())
            n_cov += 1
            if c.get("VAR_F_verdict_changes_with_precision") is True:
                chg_cells += 1
                bchg += 1
                chg_route[route] = chg_route.get(route, 0) + 1
                chg_cand[cand] = chg_cand.get(cand, 0) + 1
                chg_fam[fam] = chg_fam.get(fam, 0) + 1
            fired = c.get("falsifiers_fired_at_this_cell") or []
            if "FC-2a" in fired:
                fc2a += 1
                fc2a_cand[cand] = fc2a_cand.get(cand, 0) + 1
                fc2a_route[route] = fc2a_route.get(route, 0) + 1
            if "FC-3a" in fired:
                fc3a += 1
                fc3a_cand[cand] = fc3a_cand.get(cand, 0) + 1
            if "FC-3b" in fired:
                fc3b += 1
                fc3b_cand[cand] = fc3b_cand.get(cand, 0) + 1
                fc3b_route[route] = fc3b_route.get(route, 0) + 1
            if "FC-2b" in fired:
                R.setdefault("FC_2b_cells_found_in_per_block", 0)
                R["FC_2b_cells_found_in_per_block"] += 1
            if c.get("precision_degenerate") is True:
                pdeg += 1
                sr = json.dumps(c).lower()
                if "strict" in sr and "falsif" in sr:
                    strict_fals += 1
        if bchg:
            chg_blocks += 1
    R["recomputed_from_per_block"] = OrderedDict([
        ("n_blocks", n_blocks), ("n_covered", n_cov), ("n_uncovered", n_unc),
        ("VAR_F_changes_cells", chg_cells),
        ("VAR_F_changes_blocks", chg_blocks),
        ("VAR_F_changes_by_route", chg_route),
        ("VAR_F_changes_by_candidate", chg_cand),
        ("VAR_F_changes_by_fibre_family", chg_fam),
        ("FC_2a_cells", fc2a), ("FC_2a_by_candidate", fc2a_cand),
        ("FC_2a_by_route", fc2a_route),
        ("FC_3a_cells", fc3a), ("FC_3a_by_candidate", fc3a_cand),
        ("FC_3b_cells", fc3b), ("FC_3b_by_candidate", fc3b_cand),
        ("FC_3b_by_route", fc3b_route),
        ("precision_degenerate_cells", pdeg),
        ("strict_reading_falsified", strict_fals),
    ])

    # producer's own summary values, read as committed
    fal = res["R3_OUT_2_two_precision_table"]["falsifiers"]
    obl = res["obligation_c_VAR_F_verdict_changes_with_precision"]
    R["producer_summary_values"] = OrderedDict([
        ("n_blocks", res["R3_OUT_2_two_precision_table"]["n_blocks"]),
        ("n_covered_cell_evaluations",
         res["R3_OUT_2_two_precision_table"]["n_covered_cell_evaluations"]),
        ("obligation_c_total_cells",
         obl["total_cells_whose_committed_VAR_F_verdict_changes"]),
        ("obligation_c_blocks",
         obl["n_blocks_with_at_least_one_changing_cell"]),
        ("falsifier_summary", {k: (v.get("n_cells") if isinstance(v, dict)
                                   else v) for k, v in fal.items()}),
        ("R3_OUT_7_n_cells",
         res["R3_OUT_7_precision_degenerate_disclosure"]
            ["n_precision_degenerate_cells"]),
        ("R3_OUT_7_strict_FALSIFIED",
         res["R3_OUT_7_precision_degenerate_disclosure"]
            ["n_strict_reading_FALSIFIED"]),
        ("R3_OUT_7_strict_SATISFIED",
         res["R3_OUT_7_precision_degenerate_disclosure"]
            ["n_strict_reading_SATISFIED"]),
    ])

    # ------------------------------------------------ 2. truncation of instances
    trunc = OrderedDict()
    for name, v in fal.items():
        if not isinstance(v, dict):
            continue
        inst = v.get("instances")
        entry = {"n_cells_declared": v.get("n_cells")}
        if isinstance(inst, list):
            entry["instances_len"] = len(inst)
            entry["truncated_flag_fields"] = {
                kk: v[kk] for kk in v
                if "trunc" in kk.lower() or "omitted" in kk.lower()}
            entry["instances_len_plus_truncation"] = (
                len(inst) + sum(x for x in entry["truncated_flag_fields"]
                                .values() if isinstance(x, int)))
            entry["equals_declared_n_cells"] = (
                entry["instances_len_plus_truncation"] == v.get("n_cells"))
        trunc[name] = entry
    R["falsifier_instance_truncation"] = trunc

    # ---------------------------------------------------------- 3. P-A12a line
    pr_items = res["PREDICTION_REGISTER"]["items"]
    if isinstance(pr_items, dict):
        pa12a = pr_items.get("P-A12a")
        allitems = pr_items
    else:
        pa12a = next((x for x in pr_items
                      if x.get("id") == "P-A12a"), None)
        allitems = {x.get("id"): x for x in pr_items}
    R["PREDICTION_REGISTER_as_committed"] = {
        k: (v.get("OUTCOME") if isinstance(v, dict) else v)
        for k, v in allitems.items()}
    R["P_A12a_line_as_committed"] = pa12a
    xn = fc2a_cand.get("X_null", 0)
    rd = fc2a_cand.get("rdet", 0)
    R["P_A12a_correction_check"] = OrderedDict([
        ("json_says", pa12a.get("OUTCOME") if isinstance(pa12a, dict)
         else None),
        ("FC_2a_cells_for_X_null_from_per_block", xn),
        ("FC_2a_cells_for_rdet_from_per_block", rd),
        ("sum", xn + rd),
        ("report_claims_FALSIFIED_at_22_cells",
         "P-A12a` is FALSIFIED at those\n22 cells" in report
         or "22 cells" in report),
        ("correction_supported_by_raw_data", (xn + rd) == 22),
        ("json_left_unedited",
         (pa12a.get("OUTCOME") if isinstance(pa12a, dict) else None)
         == "HELD"),
    ])

    # -------------------------------------------------- 4. artifact policy
    declared = json.load(open(
        "%s/coordination/goals/GOAL-MLKEM-005/batches/BATCH-6b6e78/"
        "dispatch_queue.json" % ROOT))
    tasks = {t["id"]: t for t in declared["tasks"]}
    dset = set(tasks["TASK-20260813-2ce014"]["artifact_paths"])
    written = set()
    for fn in sorted(os.listdir("%s/%s" % (ROOT, T))):
        written.add("%s/%s" % (T, fn))
    R["artifact_policy"] = OrderedDict([
        ("declared_paths", sorted(dset)),
        ("files_present_in_task_dir", sorted(written)),
        ("declared_minus_present", sorted(dset - written)),
        ("present_minus_declared", sorted(written - dset)),
        ("pycache_present", any("__pycache__" in w for w in written)),
        ("command_txt_present", os.path.exists("%s/%s/command.txt"
                                               % (ROOT, T))),
        ("stdout_log_bytes", os.path.getsize("%s/%s/stdout.log" % (ROOT, T))),
        ("stderr_log_bytes", os.path.getsize("%s/%s/stderr.log" % (ROOT, T))),
        ("stdout_lines", sum(1 for _ in open("%s/%s/stdout.log"
                                             % (ROOT, T)))),
        ("R3_OUT_4_lines_in_stdout",
         sum(1 for ln in open("%s/%s/stdout.log" % (ROOT, T))
             if "R3-OUT-4" in ln)),
        ("manifest_has_run_accounting", "run_accounting:" in manifest),
        ("manifest_has_adapter_binding",
         "adapter_binding_for_this_role:" in manifest),
        ("manifest_records_model_verified_false",
         "model_verified: false" in manifest),
        ("manifest_peak_rss", re.findall(r"memory_peak_rss_[a-z]+: .*",
                                         manifest)),
        ("manifest_declares_dirty_tree",
         re.findall(r"git_dirty_tree: .*", manifest)),
        ("results_git_dirty_paths", res.get("git_dirty_paths")),
    ])

    # path inside a folded YAML scalar?  a folded/literal block is `>-` or `|`
    folded_with_path = []
    lines = manifest.splitlines()
    i = 0
    while i < len(lines):
        ln = lines[i]
        m = re.match(r"^(\s*)[\w\-\.\[\]]+: *([>|][-+]?)\s*$", ln)
        if m:
            ind = len(m.group(1))
            j = i + 1
            while j < len(lines) and (not lines[j].strip()
                                      or len(lines[j]) - len(
                                          lines[j].lstrip()) > ind):
                if re.search(r"coordination/|knowledge/|ledger/|\.py\b|"
                             r"\.json\b|\.md\b|\.log\b|\.yaml\b", lines[j]):
                    folded_with_path.append((j + 1, lines[j].strip()[:120]))
                j += 1
            i = j
            continue
        i += 1
    R["artifact_policy"]["paths_inside_folded_yaml_scalars"] = folded_with_path
    R["artifact_policy"]["n_paths_inside_folded_yaml_scalars"] = len(
        folded_with_path)

    # ----------------------------------------- 5. not-citable list of 10.1
    banned = OrderedDict([
        ("a factor of 6 to 31", "a factor of 6 to 31"),
        ("15 of the 19", "15 of the 19"),
        ("two of 29 entries below 6x", "two of 29 entries below 6"),
        ("genuinely cross-platform", "genuinely cross-platform"),
        ("29 of 48", "29 of 48"),
        ("the null fires more often than the real arm",
         "null fires more often"),
        ("G-VAR cannot be tuned", "cannot be tuned"),
        ("three predictions of actual empirical content",
         "three predictions of actual empirical content"),
        ("Residuals are 0 identically", "Residuals are 0 identically"),
        ("the obstruction is relocated", "obstruction is relocated"),
        ("3.91%", "3.91%"),
    ])
    hits = {k: (v in report) for k, v in banned.items()}
    R["not_citable_10_1_scan_of_report_a1_md"] = OrderedDict([
        ("hits", hits),
        ("any_hit", any(hits.values())),
        ("citable_range_4_87_to_31_03_present_if_range_quoted",
         "4.87" in report or "31.03" in report),
    ])

    # -------------------------------- a few committed values quoted verbatim
    R["committed_values_read"] = OrderedDict([
        ("TERMINATION_BRANCH", res["TERMINATION_BRANCH"]),
        ("TERMINATION_BRANCH_BASIS", res["TERMINATION_BRANCH_BASIS"]),
        ("R7_exact_gram_availability", res["R7_exact_gram_availability"]),
        ("FC_1_per_candidate_class", res["FC_1_per_candidate_class"]),
        ("R3_OUT_8_P_GRAM_summary",
         {k: v for k, v in res["R3_OUT_8_P_GRAM"].items()
          if k != "per_family_per_lattice"}),
        ("binary64_routes_agree_with_the_committed_measure_gvar2",
         res["binary64_routes_agree_with_the_committed_measure_gvar2"]),
        ("R3_OUT_3_readings", res["R3_OUT_3_obligation_b"]["readings"]),
        ("R3_OUT_5_joint",
         res["R3_OUT_5_P_SEP"]["joint_intersection_over_routes_and_precisions"]
         ),
        ("R3_OUT_1_certified",
         {k: (v.get("CERTIFIED_CLASS") if isinstance(v, dict) else v)
          for k, v in res["R3_OUT_1_exact_route_certification"]
          ["per_candidate"].items()}),
        ("n_route_evaluation_errors", len(res["route_evaluation_errors"])),
        ("route_evaluation_error_example",
         list(res["route_evaluation_errors"].items())[:1]),
        ("R3_OUT_V_VOID_fires", res["R3_OUT_V_VOID"]["fires"]),
        ("wall_clock_seconds", res["wall_clock_seconds"]),
        ("frozen_constants", res["frozen_constants"]),
        ("route_provenance", res["route_provenance"]),
    ])

    with open(a.out, "w") as f:
        json.dump(R, f, indent=1, default=str)

    p = print
    p("== RECOMPUTED FROM THE COMPLETE per_block RECORD (not the summaries)")
    for kk, vv in R["recomputed_from_per_block"].items():
        p("   %-34s %s" % (kk, json.dumps(vv, default=str)[:400]))
    p("== PRODUCER SUMMARY VALUES AS COMMITTED")
    for kk, vv in R["producer_summary_values"].items():
        p("   %-34s %s" % (kk, json.dumps(vv, default=str)[:400]))
    p("== FALSIFIER instances TRUNCATION")
    p("   %s" % json.dumps(trunc, default=str)[:1400])
    p("== P-A12a")
    p("   register as committed: %s" % json.dumps(pa12a, default=str)[:400])
    p("   %s" % json.dumps(R["P_A12a_correction_check"], default=str))
    p("== ARTIFACT POLICY")
    for kk, vv in R["artifact_policy"].items():
        p("   %-40s %s" % (kk, json.dumps(vv, default=str)[:300]))
    p("== NOT-CITABLE SCAN")
    p("   %s" % json.dumps(R["not_citable_10_1_scan_of_report_a1_md"]))
    p("== COMMITTED VALUES")
    for kk, vv in R["committed_values_read"].items():
        p("   %-42s %s" % (kk, json.dumps(vv, default=str)[:420]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
