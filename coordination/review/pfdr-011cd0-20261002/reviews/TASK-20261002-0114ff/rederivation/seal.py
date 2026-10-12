#!/usr/bin/env python3
"""Writes rederivation/sealed-section.yaml (RV-2 (a)) from the validator's own outputs.

TASK-20261002-0114ff. The conventions text is fixed in CONVENTIONS below (written
before relcount.py ran); the values are copied from rederivation/outputs/*.json.
The file is YAML 1.2 (value blocks are JSON flow mappings, which YAML accepts).
Refuses to overwrite an existing sealed file (open mode 'x').
Standard library only.
"""
import datetime
import glob
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "outputs")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def j(x):
    return json.dumps(x, sort_keys=True)


def main():
    cells = json.load(open(os.path.join(OUT, "cells.json")))
    g4d = json.load(open(os.path.join(OUT, "g4d-result.json")))
    g4r = json.load(open(os.path.join(OUT, "g4r-result.json")))
    ctl = json.load(open(os.path.join(OUT, "controls.json")))
    sv = json.load(open(os.path.join(OUT, "survey.json")))
    so = json.load(open(os.path.join(OUT, "survey-orient.json")))
    conv = open(os.path.join(HERE, "conventions-sealed.txt")).read()
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    L = []
    w = L.append
    w("# =============================================================================")
    w("# TASK-20261002-0114ff -- SEALED SECTION (RV-2). Written before ANY blind_from")
    w("# path of the review plan was opened. Never edited after its sha256 is logged in")
    w("# checks/read-log.txt; a later correction is a new file that names this one.")
    w("# =============================================================================")
    w("sealed_section:")
    w("  task_id: TASK-20261002-0114ff")
    w(f"  written_at: '{now}'")
    w("  object_under_review_commit: 5753edf2e0a35d3185272983e371897c86765104")
    w("  blind_from_paths_opened_before_seal: none")
    w("  inputs_read_before_seal: 'checks/read-log.txt, every line above the SEAL line'")
    w("  deterministic_note: >-")
    w("    Every J3 quantity below (Q1-Q6) and the G4-D/G4-R results are deterministic")
    w("    functions of the archived rows, bases, certificates and design.json; no")
    w("    simulation and no random number is involved except the declared, seeded")
    w("    G4-R sample selection. They must agree EXACTLY with the producer's values")
    w("    of the same quantity under the same convention.")
    w(conv.rstrip("\n"))
    w("  format_facts_from_raw_rows:")
    w(f"    survey_rows: {j({r: {k: v for k, v in x.items() if k not in ('ss_seq_sample', 'noncontiguous_instance_keys')} for r, x in sv['runs'].items()})}")
    w(f"    xfix_design_vs_20isqrtN_mismatches: {j(sv['xfix_design_vs_20isqrtN_mismatches'])}")
    w(f"    groups_with_mixed_orientation: {j(so['groups_with_mixed_eps'])}")
    w(f"    star_group_sizes_capped6: {j(so['group_sizes_by_class_capped6'])}")
    w("  J3_values:")
    w(f"    universe: {j(cells['universe'])}")
    w(f"    census_duplicate_keys: {cells['census_duplicate_keys']}")
    w(f"    CC6_drops_listed: {j(cells['CC6_drops_listed'])}")
    keys = ["C_A", "C_R", "kappa_rel", "sum_s2", "V", "SD_null", "z", "curves_used", "design_curves", "incomplete"]
    w("    Q2_FAM1_band:")
    for k, v in cells["Q2_FAM1_band"].items():
        w(f"      '{k}': {j({x: v[x] for x in keys})}")
    w("    Q2_known_null_band:")
    for k, v in cells["Q2_known_null_band"].items():
        w(f"      '{k}': {j({x: v[x] for x in keys})}")
    w("    Q2_TB3_secondary_reading_TB_B:")
    for k, v in cells["Q2_TB3_variant_B"].items():
        w(f"      '{k}': {j({x: v[x] for x in keys})}")
    w("    Q3_planted_band:")
    for k, v in cells["Q3_planted"].items():
        w(f"      '{k}': {j({x: v[x] for x in keys + ['declared_planted_total', 'excess_C_planted_minus_C_R', 'planted_relations', 'recovered_in_own_class_set', 'recovered_in_union', 'recovery_failures']})}")
    w(f"    Q3_planted_all_rungs: {j(cells['Q3_planted_all_rungs'])}")
    v = cells["Q4_CARRY1"]
    w(f"    Q4_CARRY1_subgroup_TT3_28bits: {j({x: v[x] for x in keys})}")
    w("    Q5_PC1:")
    for k, v in cells["Q5_PC1"].items():
        w(f"      'bits {k}': {j(v)}")
    w("    Q6_random_pooled_within_curve_relation_dispersion_band:")
    for k, v in cells["Q6_random_dispersion_band"].items():
        w(f"      '{k}': {j(v)}")
    w("    Q1_band_sums_per_arm_class_m: see Q1_counts_file; per-curve n_{X,j} for every arm, class, m and curve at 30 and 32 bits")
    w(f"    Q1_counts_file: {{path: rederivation/outputs/q1-counts-band.jsonl.gz, sha256: {sha(os.path.join(OUT, 'q1-counts-band.jsonl.gz'))}}}")
    w(f"    Q1_per_instance_all_rungs_file: {{path: rederivation/outputs/relcount.jsonl.gz, sha256: {sha(os.path.join(OUT, 'relcount.jsonl.gz'))}}}")
    w("    Q1_multiplicity_histograms_band_nonformal:")
    for k, v in cells["Q1_multiplicity_histograms_band"].items():
        w(f"      '{k}': {j(v)}")
    w("    Q2_per_rung_secondary_cells: 'in rederivation/outputs/cells.json (never decision-bearing, CC-10)'")
    w("  J1_own_verifiers:")
    w(f"    G4D: {j({fp.split('wt-pfdr011cd0-5753edf2e/')[-1]: {k: x[k] for k in ('records', 'records_passing_all_checks', 'duplicate_keys', 'missing_universe_keys', 'keys_outside_universe', 'curves_with_inconsistent_target', 'pass', 'sha256')} for fp, x in g4d['files'].items()})}")
    w(f"    G4D_pass_all_files: {j(g4d['pass'])}")
    w(f"    G4R: {j({k: g4r[k] for k in ('sample_instances', 'instances_checked', 'missing_bases_for_sampled', 'rows_checked', 'rows_passing_all', 'row_check_failures', 'base_check_failures', 'pass')})}")
    w(f"    G4R_sample: {{file: rederivation/outputs/g4r-sample.json, sha256: {sha(os.path.join(OUT, 'g4r-sample.json'))}, fixed_at: '2026-10-02T14:31:04Z', rule: 'g4r_sample.py docstring'}}")
    w(f"    G4R_coverage_run_m_arm: {j(g4r['coverage_run_m_arm_instances'])}")
    w(f"  instrument_controls: {j(ctl)}")
    w("  file_hashes:")
    for p in sorted(glob.glob(os.path.join(HERE, "*.py")) + glob.glob(os.path.join(HERE, "*.yaml")) +
                    glob.glob(os.path.join(HERE, "*.txt")) + glob.glob(os.path.join(OUT, "*"))):
        if os.path.basename(p) == "sealed-section.yaml":
            continue
        w(f"    '{os.path.relpath(p, os.path.dirname(HERE))}': {sha(p)}")
    w("  read_after_seal_not_before: [t_star, t_carry, every blind_from path]")
    with open(os.path.join(HERE, "sealed-section.yaml"), "x") as fh:
        fh.write("\n".join(L) + "\n")
    print(now)


if __name__ == "__main__":
    main()
