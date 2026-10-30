#!/usr/bin/env python3
"""Write out/report.yaml for TASK-20261029-2c7b52 (J1) from the FROZEN outputs only.

Refuses unless freeze-manifest.json exists and every frozen output still matches its recorded sha256.
Standard library only; emits YAML by hand (JSON-quoted scalars are valid YAML)."""
import hashlib
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(ROOT, "out")
SCOPE = "coordination/goals/GOAL-PFDR-fd09e0/batches/BATCH-924d2c/reviews/TASK-20261029-2c7b52"


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        h.update(fh.read())
    return h.hexdigest()


def load(name):
    return json.load(open(os.path.join(OUT, "outputs", name)))


fm = load("freeze-manifest.json")
for rel, digest in list(fm["outputs"].items()) + list(fm["scripts"].items()):
    if sha(os.path.join(ROOT, rel)) != digest:
        sys.exit("frozen file changed: " + rel)
if os.path.exists(os.path.join(OUT, "report.yaml")):
    sys.exit("report.yaml exists")

inv = load("record-invariants.json")
des = load("blind-design.json")
cells = load("blind-cells.json")["cells"]
rd = load("blind-reading.json")
amb = load("ambiguity-table.json")
rel = load("relation-expectation.json")
seed = load("bootstrap-seed.json")


def q(s):
    return json.dumps(s, ensure_ascii=False)


def emit(obj, ind=0):
    pad = "  " * ind
    lines = []
    if isinstance(obj, dict):
        if not obj:
            return [pad + "{}"]
        for k, v in obj.items():
            key = k if all(ch.isalnum() or ch in "_-" for ch in k) else q(k)
            if isinstance(v, (dict, list)) and v:
                if isinstance(v, list) and all(not isinstance(x, (dict, list)) for x in v) and len(q(v)) < 110:
                    lines.append("%s%s: %s" % (pad, key, flow(v)))
                else:
                    lines.append("%s%s:" % (pad, key))
                    lines.extend(emit(v, ind + 1))
            else:
                lines.append("%s%s: %s" % (pad, key, scalar(v)))
    elif isinstance(obj, list):
        if not obj:
            return [pad + "[]"]
        for v in obj:
            if isinstance(v, dict) and v:
                sub = emit(v, ind + 1)
                sub[0] = pad + "- " + sub[0].lstrip()
                lines.extend(sub)
            elif isinstance(v, list) and v:
                lines.append(pad + "- " + flow(v))
            else:
                lines.append(pad + "- " + scalar(v))
    else:
        lines.append(pad + scalar(obj))
    return lines


def flow(v):
    return "[" + ", ".join(scalar(x) if not isinstance(x, list) else flow(x) for x in v) + "]"


def scalar(v):
    if v is None:
        return "null"
    if v is True:
        return "true"
    if v is False:
        return "false"
    if isinstance(v, int):
        return str(v)
    if isinstance(v, float):
        return repr(v)
    if isinstance(v, (dict, list)):
        return "{}" if isinstance(v, dict) else "[]"
    return q(v)


cmap = {c["cell"]: c for c in cells}
table = []
for c in cells:
    table.append({"cell": c["cell"], "n_curves": c["n_curves"], "ok": c["ok_records"], "S": c["S"], "M": c["M_exact"],
                  "V": c["V_exact"], "kappa": c["kappa_exact"], "kappa_dec": round(c["kappa"], 6),
                  "z": c["z_str"][:12], "ci95_nr_A": [round(x, 5) for x in c["ci95"]],
                  "ci95_lin_A": [round(x, 5) for x in c["bootstrap"]["A"]["kappa_ci95_linear"]],
                  "plant_kappa": round(c["plant_kappa"], 5), "plant_z": round(c["plant_z"], 3),
                  "plant_feasible_all": c["plant_feasible_all_recorded"], "z_cal": round(c["z_cal"], 5),
                  "powered": c["powered"], "cls": c["cls"]})

edge_ab = max(max(abs(a - b) for a, b in zip(c["bootstrap"]["A"]["kappa_ci95_nearest_rank"], c["bootstrap"]["B"]["kappa_ci95_nearest_rank"])) for c in cells)
edge_conv = max(max(abs(a - b) for a, b in zip(c["bootstrap"]["A"]["kappa_ci95_nearest_rank"], c["bootstrap"]["A"]["kappa_ci95_linear"])) for c in cells)
ci_excl_1 = [c["cell"] for c in cells if c["cls"] == "null" and (c["ci95"][0] > 1 or c["ci95"][1] < 1)]
lam = rel["b20_r3_n4096_fraction_of_single_relations_exceeding_slack_534"] * [r for r in rel["per_cell"] if r["cell"] == "b20-r3-n4096"][0]["expected_curves_with_relation"]
tail4 = 1 - math.exp(-lam) * sum(lam ** k / math.factorial(k) for k in range(4))

cal = rd["calibration"]
fc = amb["full_cross_product"]
amb_rows = []
for r in amb["rows"]:
    alts = []
    for a in r.get("admissible_alternatives", []):
        e = a["effect"]
        alts.append({"resolution": json.dumps(a["resolution"], sort_keys=True),
                     "gate": "pass" if a["summary"]["gate_pass"] else "fail",
                     "gate_mean": round(a["summary"]["gate_mean"], 4), "gate_sd_population": round(a["summary"]["gate_sd_population"], 4),
                     "gate_sd_sample": round(a["summary"]["gate_sd_sample"], 4),
                     "changes": [k for k, v in e.items() if v] or "none"})
    row = {"id": r["id"], "topic": r["topic"], "frozen_text": r["text"], "chosen": r["chosen"],
           "alternatives": alts or "none admissible"}
    if r.get("inadmissible_alternative_tested") and isinstance(r["inadmissible_alternative_tested"], dict):
        e = r["inadmissible_alternative_tested"]["effect"]
        row["inadmissible_reading_tested"] = {
            "resolution": r["inadmissible_alternative_tested"]["resolution"]["ok_acc"],
            "changes": [k for k, v in e.items() if v and k != "classes_changed"] + [
                "%s: %s -> %s" % (x["cell"], x["base"], x["alt"]) for x in e["classes_changed"]],
            "reading_and_headline": "%s / %s (unchanged)" % (r["inadmissible_alternative_tested"]["summary"]["outcome_final"],
                                                              r["inadmissible_alternative_tested"]["summary"]["headline"])}
    if r.get("robustness_all_positions"):
        ra = r["robustness_all_positions"]
        row["robustness_all_list_positions"] = {"gate_pass_all_20": all(ra["gate_pass_by_position"]),
                                                "gate_mean_range": [round(min(ra["gate_mean_by_position"]), 4), round(max(ra["gate_mean_by_position"]), 4)],
                                                "gate_sd_population_range": [round(min(ra["gate_sd_population_by_position"]), 4), round(max(ra["gate_sd_population_by_position"]), 4)]}
    if r.get("note"):
        row["note"] = r["note"]
    amb_rows.append(row)

inventory = []
for relp, digest in sorted(fm["outputs"].items()):
    inventory.append({"path": SCOPE + "/outputs/" + relp.split("/")[-1], "tree_path": relp, "sha256": digest})
inventory.append({"path": SCOPE + "/outputs/freeze-manifest.json", "tree_path": "out/outputs/freeze-manifest.json",
                  "sha256": sha(os.path.join(OUT, "outputs", "freeze-manifest.json"))})
for relp, digest in sorted(fm["scripts"].items()):
    inventory.append({"path": SCOPE + "/scripts/" + relp.split("/")[-1], "tree_path": relp, "sha256": digest})
inventory.append({"path": SCOPE + "/scripts/write_report.py", "tree_path": "out/scripts/write_report.py",
                  "sha256": sha(os.path.join(HERE, "write_report.py")),
                  "note": "written after the freeze; reads only frozen outputs and checks their sha256 before writing report.yaml"})

basis = (
    "Every load-bearing quantity of the toy reading is derivable from the specification, the hypothesis and the two job "
    "files, and none moves under any admissible reading of the frozen text. The 6657 main-census records match the "
    "closed-form design exactly (45 cells, 6657 planned keys, none missing or duplicated, block main only), and all %d "
    "record-invariant checks pass with zero violations. The checks cover schema, prime p of the stated size, prime N with "
    "N*P = O on all %d distinct curves, one shared curve per (bits, c), the T rule, half-box bookkeeping including the "
    "position of the last vector, Cauchy-Schwarz and range bounds tying every recorded C to its D, and the plant "
    "feasibility rule. Under the frozen class order, %d cells are null and one, b20-r3-n4096, is invalid: 4 of its 50 "
    "main curves (c = 6, 30, 42, 47) are degenerate, leaving 46 ok records. No cell is underpowered (min M = %s), every "
    "plant is recovered (min plant_kappa %.4f, min plant_z %.1f), and no cell meets the flag rule (max |kappa - 1| = %.4f, "
    "max |z| = %.3f). The calibration gate over the %d powered cells passes (mean %.4f, population sd %.4f); "
    "fraction_valid = %s; the flagged set is empty, so the frozen replication rule requires no replication records and "
    "the empty toy-rep-jobs.jsonl satisfies it. The reading is %s at analyze-main and %s at analyze-final, and the headline "
    "is %s. Over all %d combinations of the admissible resolutions enumerated, no class, gate result, fraction_valid, "
    "flagged set, reading or headline changes. The only change found comes from the inadmissible reading that counts "
    "degenerate records as present: fraction_valid becomes 45/45, while the reading and headline stay the same."
) % (len(inv["checks"]), inv["distinct_curves_checked"], rd["class_counts"].get("null", 0),
     "%s (%s, %s)" % (repr(min(c["M"] for c in cells)), [c["M_exact"] for c in cells if c["M"] == min(x["M"] for x in cells)][0],
                      [c["cell"] for c in cells if c["M"] == min(x["M"] for x in cells)][0]),
     min(c["plant_kappa"] for c in cells), min(c["plant_z"] for c in cells),
     max(abs(c["kappa"] - 1) for c in cells), max(abs(c["z"]) for c in cells), cal["n"], cal["mean"], cal["sd_population"],
     rd["fraction_valid_exact"], rd["outcome_main"], rd["outcome_final"], rd["headline"], fc["n_combinations"])

sources_read = [
    {"path": "ledger/handoffs/TASK-20261029-2c7b52.yaml", "extent": "full"},
    {"path": "experiments/EXP-PFDR-bb0d26/specification.yaml", "extent": "full (sed ranges 1-813; the first cat was truncated by the harness)"},
    {"path": "ledger/hypotheses/H-PFDR-727bfc.yaml", "extent": "full"},
    {"path": "experiments/EXP-PFDR-bb0d26/runs/RUN-PFDR-4d8c71/toy-main-jobs.jsonl", "extent": "full, by own scripts"},
    {"path": "experiments/EXP-PFDR-bb0d26/runs/RUN-PFDR-cd03e2/toy-rep-jobs.jsonl", "extent": "full (0 bytes)"},
    {"path": "agents/validator.md", "extent": "full"},
    {"path": "AGENTS.md", "extent": "heading list (grep '^#'), lines 167-207 (Core rules), lines 323-336 (Review architecture)"},
    {"path": "templates/research-records.md", "extent": "grep hits for review_attestation / blind_rederivation / sources_read, lines 720-830"},
    {"path": SCOPE + "/blind-input-manifest.json", "extent": "full (tree copy written by the dispatching session; outside the eight-file allowlist but placed in the tree by the dispatcher)"},
]

report = {
    "review_report": {
        "task_id": "TASK-20261029-2c7b52",
        "experiment_id": "EXP-PFDR-bb0d26",
        "hypothesis_id": "H-PFDR-727bfc",
        "goal_id": "GOAL-PFDR-fd09e0",
        "review_round": "BATCH-924d2c",
        "opened_by_decision": "DEC-20261029-8b2734",
        "joint": "J1",
        "kind": "blind re-derivation (not a validation; no producer value read or compared)",
        "recorded_at": "2026-10-29",
        "verdict_J1": "holds",
        "verdict_basis": basis,
        "inputs_bound": {"opening_commit": "d89a6d6bdd (from blind-input-manifest.json)",
                         "sha256_verified_against_manifest": True,
                         "files": json.load(open(os.path.join(ROOT, "blind-input-manifest.json")))["files"]},
        "derived": {
            "design": {"rule": des["rule"], "total_planned_jobs": des["total_planned_jobs"],
                       "n_curves_by_cell": {r["cell"]: r["n_curves"] for r in des["cells"]},
                       "cap_2000_reached": des["any_cap_reached"], "any_ceil_argument_integer": des["any_ceil_argument_integer"],
                       "float_path_agrees_everywhere": des["float_path_agrees_everywhere"],
                       "observed_census_matches_design_in_every_cell": all(r["observed_matches_design"] for r in des["cells"])},
            "record_invariants": {"main_records": inv["main_records"], "status_count": inv["main_status_count"],
                                  "replication_records": inv["replication_records"],
                                  "total_violations": inv["total_violations"],
                                  "checks": [{"id": c["id"], "n_checked": c["n_checked"], "n_violations": c["n_violations"],
                                              "check": c["description"]} for c in inv["checks"]],
                                  "not_checkable_from_records": inv["not_checkable_from_records"]},
            "statistics_conventions": {
                "S": "sum over ok curves of gap_C", "M": "sum over ok curves of the mean of the 20 null_C (exact rational)",
                "V": "sum over ok curves of the SAMPLE variance (divisor 19) of the 20 null_C, as the statement says",
                "z": "(S - M) / sqrt(V (1 + 1/20)) in 60-digit Decimal; |z| > 4 and plant_z > 4 decided exactly in rationals",
                "z_cal": "replicate 0 (list position 0) against replicates 1..19, pooled over curves like z, sample variance (divisor 18), factor 1 + 1/19",
                "calibration_gate": "population sd and mean of z_cal over cells with M >= 2500 (all 45, the invalid cell included on its 46 ok curves)",
                "bootstrap": seed["rule"] + " Seeds fixed in bootstrap-seed.json before the first draw.",
                "percentiles": "nearest-rank (50th and 1950th of 2000) primary; linear interpolation (type 7) reported"},
            "cells": table,
            "calibration": {"n": cal["n"], "mean": cal["mean_str"], "sd_population": cal["sd_population_str"],
                            "sd_sample": cal["sd_sample"], "pass": cal["pass"],
                            "band": "population sd in [0.75, 1.25] and |mean| <= 0.35",
                            "margins": cal["margins"]},
            "class_counts": rd["class_counts"],
            "fraction_valid": rd["fraction_valid_exact"] + " = " + repr(round(rd["fraction_valid"], 6)),
            "invalid_cells": [{"cell": x["cell"], "ok_records": x["ok_records"], "n_curves": x["n_curves"],
                               "non_ok": ["c=%d %s" % (y["c"], y["status"]) for y in x["non_ok_records"]],
                               "rule": "fewer ok main-census records than n_curves (degenerate)"} for x in rd["invalid_cells"]],
            "flagged_cells": rd["flagged_cells"],
            "replication": {"required_content": rd["replication"]["required_content"] or "none (no flagged cell)",
                            "required_record_count": rd["replication"]["required_record_count"],
                            "actual_file": "experiments/EXP-PFDR-bb0d26/runs/RUN-PFDR-cd03e2/toy-rep-jobs.jsonl",
                            "actual_records": rd["replication"]["actual_records"], "actual_sha256": rd["replication"]["file_sha256"],
                            "satisfies_frozen_rule": rd["replication"]["satisfies_rule"],
                            "basis": "replication_rule and stopping_rules: census-toy-rep runs only flagged cells; with none flagged it records an empty toy-rep-jobs.jsonl"},
            "reading": {"analyze_main": rd["outcome_main"], "analyze_final": rd["outcome_final"], "headline": rd["headline"],
                        "rule_path": "O-INVALID no (gate passes, 44/45 >= 1/2); O-STRUCT no (no flagged cell); O-PENDING-REPLICATION no (no flagged cell); O-NULL yes (every valid cell null, 44/45 >= 4/5); headline SUPPORT_SCOPED by outcome O-NULL",
                        "scope_of_reading": "44 of 45 cells; b20-r3-n4096 is invalid and not read"},
            "tail_checks_descriptive": {
                "max_abs_z_over_powered_valid": rd["tail_checks"]["max_abs_z_over_powered"],
                "expected_max_of_45_standard_normals": "about 2.4 (specification heuristic_validation.tail_checks_available)",
                "cells_abs_z_gt_3": rd["tail_checks"]["cells_abs_z_gt_3"],
                "cells_abs_z_gt_3_expected": "about 0.12 of 45 (0.27 percent each)",
                "null_cells_whose_interval_excludes_1": ci_excl_1,
                "plant_infeasible_cells": rd["tail_checks"]["plant_infeasible_cells"] or "none",
                "R6_null_mean_over_formula_anomalies": rd["tail_checks"]["null_mean_over_formula_anomalies"] or "none",
                "null_mean_over_formula_range": [round(min(c["null_mean_over_formula"] for c in cells), 4), round(max(c["null_mean_over_formula"] for c in cells), 4)],
                "d_ratio_range": [round(min(c["d_ratio"] for c in cells), 6), round(max(c["d_ratio"] for c in cells), 6)],
                "secondary_slope_logkappa_per_log2n": {k: (round(v, 6) if v is not None else None) for k, v in rd["secondary_slope_logkappa_per_log2n"].items()}},
            "decision_margins": {
                "closest_kappa_to_0.05": "b28-r1-n256 kappa = 80920/77703 = 1.04140 (margin 0.0086; exact, no ambiguity applies)",
                "closest_interval_edge_to_band": "b28-r1-n256 upper edge 1.07438 (margin 0.0256 to 1.10)",
                "bootstrap_edge_spread_family_A_vs_B": round(edge_ab, 6),
                "bootstrap_edge_spread_nearest_rank_vs_linear": round(edge_conv, 7),
                "closest_M_to_2500": "b28-r2-n256 M = 3869.35",
                "closest_plant_kappa_to_1.15": "b20-r2-n4096 plant_kappa = 1.28852",
                "smallest_plant_z": "b24-r2-n256 plant_z = 21.93",
                "gate_abs_mean_margin": round(cal["margins"]["abs_mean_to_bound"], 4)},
        },
        "ambiguity_table": amb_rows,
        "ambiguity_cross_product": {"combinations": fc["n_combinations"], "dimensions": fc["dimensions"],
                                    "combinations_with_any_change": fc["n_combinations_with_any_change"],
                                    "headlines": fc["distinct_headlines"], "final_outcomes": fc["distinct_outcomes_final"],
                                    "gate_pass_values": fc["distinct_gate_pass"], "fraction_valid_values": fc["distinct_fraction_valid"],
                                    "flagged_sets": [list(x) for x in fc["distinct_flagged_sets"]],
                                    "gate_sd_range": [round(x, 4) for x in fc["gate_sd_range"]],
                                    "gate_abs_mean_range": [round(x, 4) for x in fc["gate_abs_mean_range"]]},
        "class_sensitive_resolutions": "none",
        "coordinator_expected_breaks_checked": [
            "variance divisor and calibration population: gate passes in every combination (|mean| 0.267-0.313 <= 0.35; sd 0.960-1.047 inside [0.75, 1.25]); closest is Stouffer pooling (|mean| 0.313)",
            "bootstrap convention near an interval edge: closest edge margin 0.0256 (b28-r1-n256 upper) against a family A/B spread of at most %.4f and a nearest-rank/linear spread of at most %.6f" % (edge_ab, edge_conv),
            "ok-record accounting and fraction_valid: 44/45 under the frozen rule; 45/45 only if degenerate records counted as present, which the frozen parenthetical excludes; reading and headline unchanged either way",
        ],
        "unexpected_observations": [
            {"observation": "All 4 records in the census with any duplicate_skips are the 4 degenerate records of b20-r3-n4096 (duplicate_skips 1064, 624, 1600, 1988; c = 47 also has one Q = O skip); no ok record anywhere has a duplicate or Q = O skip.",
             "expectation_under_statement_model": "independent uniform P_i: about %.1f relation-bearing curves over all r >= 2 cells (4 observed, consistent), about %.2f in b20-r3-n4096, of which about %.0f%% would exceed the 534-vector slack, i.e. about %.2f degenerate and %.2f ok-with-skips expected there (observed 4 and 0); single-cell Poisson tail P(>= 4) about %.3f before look-elsewhere over 13 r >= 2 cells" % (
                 rel["total_expected_r_ge_2"], [r for r in rel["per_cell"] if r["cell"] == "b20-r3-n4096"][0]["expected_curves_with_relation"],
                 100 * rel["b20_r3_n4096_fraction_of_single_relations_exceeding_slack_534"], lam,
                 [r for r in rel["per_cell"] if r["cell"] == "b20-r3-n4096"][0]["expected_curves_with_relation"] - lam, tail4),
             "effect_on_reading": "none: a degenerate curve makes its cell invalid regardless of cause, and the four records satisfy the degenerate invariants (whole half-box enumerated, labels short of n)",
             "suggested_check_for_another_joint": "recompute P_1..P_3 for b20-r3-n4096 c in {6, 30, 42, 47} with the frozen seed rule and confirm a short relation v.P = O; approximate model, see relation-expectation.json"},
            {"observation": "%d null cells (%s) have a curve-cluster interval that excludes 1, and b24-r1-n2048 has z = -3.13 (|kappa - 1| = 0.0011)" % (len(ci_excl_1), ", ".join(ci_excl_1)),
             "effect_on_reading": "none: the null class is an effect-size band (|kappa - 1| < 0.05, interval inside [0.90, 1.10]), not a significance test; reported because the hypothesis' tail check counts |z| > 3"},
        ],
        "out_of_joint_dependencies_not_assessed": [
            "presence and content of design.json, selftest.json and the selftest pass (RUN-PFDR-e44a19 is in blind_from); the class rule's 'or the design missing' clause is taken as not triggered",
            "check.py exit codes, manifests (trial_plan_sha256, code_sha256, dirty tree, environment, resources) and every invalidation_rule other than degenerate/failed records; these condition the success_criterion, not the J1 derivation",
            "kernel correctness of C and D (label sets are not recorded; only consistency bounds were checked)",
            "seeded determinism of any record (maximum_runs 0; no generator run)",
        ],
        "limitations": [
            "The producer's per-cell bootstrap seed is not in the allowlist; my interval is exactly reproducible from bootstrap-seed.json and matches any other seed only up to Monte Carlo error (family A vs B edge spread at most %.4f); no class depends on it." % edge_ab,
            "z, plant_z, z_cal, the gate mean and sd are irrational; they are given to 28-40 significant digits from 60-digit Decimal square roots, and every threshold decision on z was made exactly in rationals.",
            "Statistics of the invalid cell b20-r3-n4096 are computed over its 46 ok curves and are descriptive only.",
            "plant_m minimality cannot be checked from the records (internal(m - 1) is not recorded); feasibility was checked against the 0.30 x mean-null threshold on every ok curve.",
            "Cells at the same bits share curves, so z_cal values and cell statistics are correlated (specification R1); the gate band is used as frozen.",
            "Nothing here bears on H-PFDR-727bfc beyond the derivation of the reading the frozen text assigns to these records.",
        ],
        "commands": {"cwd": "the blind tree root (scratchpad blind-J1)", "log": "out/scripts/commands.txt",
                     "interpreters": ["python3 -I (3.13.17)", "python3.11 -I (3.11.17, cross-check only)"],
                     "main": ["python3 -I out/scripts/blind_j1.py invariants", "python3 -I out/scripts/blind_j1.py design",
                              "python3 -I out/scripts/blind_j1.py seed", "python3 -I out/scripts/blind_j1.py cells",
                              "python3 -I out/scripts/blind_j1.py reading", "python3 -I out/scripts/relation_expectation.py",
                              "python3.11 -I out/scripts/crosscheck.py > out/outputs/crosscheck.txt",
                              "python3 -I out/scripts/blind_j1.py freeze", "python3 -I out/scripts/write_report.py"],
                     "cross_check_result": open(os.path.join(OUT, "outputs", "crosscheck.txt")).read().strip().splitlines()},
        "artifact_inventory": inventory,
    },
    "validation_report": {
        "id": "VAL-20261029-2c7b52-J1",
        "task_id": "TASK-20261029-2c7b52",
        "run_ids": ["RUN-PFDR-4d8c71", "RUN-PFDR-cd03e2"],
        "artifact_checks": ["toy-main-jobs.jsonl sha256 d34b973b...ae87 equals blind-input-manifest; 6657 records, 22 invariant checks, 0 violations",
                            "toy-rep-jobs.jsonl sha256 e3b0c442...b855 (empty file) equals blind-input-manifest; empty is the frozen recorded result when no cell is flagged"],
        "metric_recomputations": ["S, M, V, kappa, z, plant_kappa, plant_z, z_cal for 45 cells, exact; second independent path (crosscheck.py, python3.11) agrees exactly on S, M, V, kappa and to 3e-16 relative on z, plant_z, z_cal",
                                  "own curve-cluster bootstrap, 2000 resamples, pre-written seeds, nearest-rank and linear percentiles"],
        "control_checks": ["C2 matched null: per-curve 20-replicate means and variances used throughout; R6 ratio in [%.4f, %.4f], no anomaly" % (min(c["null_mean_over_formula"] for c in cells), max(c["null_mean_over_formula"] for c in cells)),
                           "C3 planted AP: feasible on every ok curve, plant_kappa >= 1.2885 and plant_z >= 21.9 in every cell",
                           "C4 calibration: n 45, mean %.4f, population sd %.4f, pass" % (cal["mean"], cal["sd_population"]),
                           "C5 replication: no flagged cell, nothing required; empty file satisfies",
                           "C1, C6, C7 (selftest, checker replay, scaling identity): not in the allowlist, not assessed"],
        "heuristic_validation_checks": ["pre-registered thresholds read from the frozen specification and applied unchanged",
                                        "sample sizes re-derived from the closed-form sizing rule; scale toy (p of 20 to 28 bits, n <= 4096) as declared"],
        "cost_model_checks": ["not applicable: no cost claim (C8 not run, by the specification)"],
        "proof_architecture_checks": [],
        "verdict": "incomplete",
        "verdict_scope": "Blind re-derivation scope only. Manifest, command, revision, dirty-tree, environment, resource, selftest and checker records are in blind_from and were deliberately not checked, so this report does not establish the admissibility of the receipts. It reports no defect. The joint verdict is review_attestation.verdict (J1 holds).",
        "limitations": ["see review_report.limitations and out_of_joint_dependencies_not_assessed"],
        "artifact_paths": [x["path"] for x in inventory] + [SCOPE + "/report.yaml"],
    },
    "review_attestation": {
        "task_id": "TASK-20261029-2c7b52",
        "joints_owned": ["J1"],
        "sources_read": sources_read,
        "harness_injected_context_not_read_by_task": [
            "the repository's CLAUDE.md text was injected into the session context by the runtime at start (generic runtime rules; no experiment content)",
            "the runtime saved the over-long output of 'cat specification.yaml' to its own tool-results file outside the tree; that file was not opened (it is a copy of an allowlisted file)",
        ],
        "read_sibling_reports": False,
        "blind_from_respected": True,
        "verdict": "holds",
        "verdicts": {"J1": "holds"},
        "procedure_deviations": [
            "docs/agent-runtime-core.md, named in my standing role prompt, was not read: it is outside the blind allowlist and the card's blindness constraint governs",
            "Outside the eight-file allowlist, blind-input-manifest.json in the tree was read (placed there by the dispatching session; it binds the copies by sha256)",
            "blind-cells.json, blind-reading.json and ambiguity-table.json were regenerated several times before the freeze as alternatives and fields were added. bootstrap-seed.json was written once before the first draw and never rewritten, and every regeneration reproduced identical bytes for unchanged content",
            "Extra outputs beyond the deliverable list: bootstrap-seed.json, relation-expectation.json, crosscheck.txt. Extra scripts: explore.py, relation_expectation.py, crosscheck.py, commands.txt, write_report.py (written after the freeze)",
            "No .resume checkpoint was written: this task runs no experiment (maximum_runs 0), and .resume is in blind_from",
        ],
        "inference_binding_served": {"policy": "review-adversarial", "reasoning_effort": "xhigh (as dispatched; not independently observable by this session)",
                                     "model": "claude-opus-5-5", "fallback_used": False, "degraded": False,
                                     "independent_session": True, "delivery": "interactive"},
        "no_producer_value_compared": True,
        "no_status_change_no_commit": True,
    },
}

text = "# report.yaml for TASK-20261029-2c7b52 (J1, blind re-derivation), written by out/scripts/write_report.py after the freeze\n"
text += "\n".join(emit(report)) + "\n"
with open(os.path.join(OUT, "report.yaml"), "w") as fh:
    fh.write(text)
print("wrote out/report.yaml", sha(os.path.join(OUT, "report.yaml")))
