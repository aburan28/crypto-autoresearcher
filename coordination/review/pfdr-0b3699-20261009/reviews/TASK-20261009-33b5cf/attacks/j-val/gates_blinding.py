"""J-VAL (5) gates and (7) blinding I-A7, EXP-PFDR-0b3699. TASK-20261009-33b5cf.
Standard library only (plus the stdlib xml parser); no producer code.

(5) For every gate of specification gates / gate_rule: the deciding artifact, its
    pass value read from the file, whether RA-06 read it (analysis.json gates_read and
    the RA-06 view-map path + sha256 equal to the file's bytes now).
    G-T: junit.xml totals and the four test files in it; the three pre-existing test
    files' bytes vs the 38be58dad bytes (extracted to scratch by `git archive`).
    G4-R chain: row-verify.json pass and per-instance PASS count vs checks-report
    G4-R; checks-report top-level pass == AND of its checks.
(7) arm-read-log.json: only null arms parsed in every file entry, structured lines
    skipped unparsed, file list == run-root rows + every job's harvest-rows; RA-05 and
    RA-06 view-maps: equal sha256 on every common path, every listed sha256 equal to the
    bytes now, RA-05 lists no calibration/analysis output and no structured-only file.
    RA-04 report files (every non-job file of the RA-04 run directory and the
    checks/merge step directories): every JSON key and log line scanned for count-like
    keys; each hit reported with its location, and whether it can carry a count of a
    structured or planted arm.
No seeds. Usage: python gates_blinding.py <repo> <tests-38be58dad-dir> <out.json>
"""
import hashlib
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

RUNS = "experiments/EXP-PFDR-0b3699/runs"
STRUCT = ("small_x", "small_x_offset", "subgroup", "planted_sub", "planted_target")
NULLS = {"random_sub_r0", "random_sub_r1", "random_sub_r2", "known_null_sub"}
COUNT_KEYS = re.compile(r"^(relations(_distinct(_sign)?|_nonformal)?|R_star|rows_emitted|cert_pass|"
                        r"rows_checked|failed|failure_count|C_X|C_A|C_R|C_M|kappa.*|z|z_.*|"
                        r"multiplicity_histogram|informative_rank|relation_pairs.*|total.*|.*_count|"
                        r"count|counts|harvest_rows|rows|pairs_.*|star_groups.*)$")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def walk_keys(x, path, hits):
    if isinstance(x, dict):
        for k, v in x.items():
            p = f"{path}.{k}"
            if COUNT_KEYS.match(str(k)) and not isinstance(v, (dict, list)) or (
                    COUNT_KEYS.match(str(k)) and isinstance(v, (dict, list)) and len(v) < 50):
                hits.append({"key_path": p, "value_preview": json.dumps(v)[:120]})
            walk_keys(v, p, hits)
    elif isinstance(x, list):
        for i, v in enumerate(x[:200000]):
            walk_keys(v, f"{path}[{i}]" if i < 3 else f"{path}[*]", hits)


def main():
    repo, tests38, outp = sys.argv[1:4]
    R = lambda *p: os.path.join(repo, *p)  # noqa: E731
    out = {"gates": {}, "blinding": {}}
    an = json.load(open(R(RUNS, "RUN-PFDR-0b3699-analysis", "analysis.json")))
    vm6 = {f["path"]: f["sha256"] for f in json.load(open(R(RUNS, "RUN-PFDR-0b3699-analysis", "view-map.json")))["files"]}
    vm5 = {f["path"]: f["sha256"] for f in json.load(open(R(RUNS, "RUN-PFDR-0b3699-calibrate", "view-map.json")))["files"]}
    cal = json.load(open(R(RUNS, "RUN-PFDR-0b3699-calibrate", "calibration.json")))
    design = json.load(open(R(RUNS, "RUN-PFDR-0b3699-p0-design", "design.json")))
    chk = json.load(open(R(RUNS, "RUN-PFDR-0b3699-table", "checks-report.json")))
    rv = json.load(open(R(RUNS, "RUN-PFDR-0b3699-table", "row-verify.json")))
    gr = json.load(open(R(RUNS, "RUN-PFDR-0b3699-repro", "g-repro-report.json")))
    p0 = json.load(open(R(RUNS, "RUN-PFDR-0b3699-p0-design", "p0x-a-report.json")))

    def read_by_ra06(path):
        return {"in_gates_read": an["gates_read"].get(path), "in_ra06_view_map": path in vm6,
                "view_map_sha256_equals_file": vm6.get(path) == sha(R(path)) if path in vm6 else None}

    # junit
    jx = R(RUNS, "RUN-PFDR-0b3699-tests", "junit.xml")
    root = ET.parse(jx).getroot()
    suites = [root] if root.tag == "testsuite" else list(root)
    tot = {k: sum(int(s.get(k, 0)) for s in suites) for k in ("tests", "failures", "errors", "skipped")}
    files = sorted({(tc.get("classname") or "").split(".")[-1] for s in suites for tc in s.iter("testcase")})
    unedited = {f: sha(R("tests", f)) == sha(os.path.join(tests38, f)) for f in
                ("test_index_calculus_fp.py", "test_index_calculus_harvest.py", "test_index_calculus_relcensus.py")}
    gt_path = f"{RUNS}/RUN-PFDR-0b3699-tests/junit.xml"
    out["gates"]["G-T"] = {"artifact": gt_path, "junit_totals": tot, "test_modules": files,
                           "three_preexisting_tests_equal_38be58dad_bytes": unedited,
                           "pass": tot["tests"] > 0 and tot["failures"] == 0 and tot["errors"] == 0,
                           "ra06": {"in_gates_read": an["gates_read"].get(gt_path + " (G-T)"),
                                    "in_ra06_view_map": gt_path in vm6,
                                    "view_map_sha256_equals_file": vm6.get(gt_path) == sha(R(gt_path))}}
    gp = f"{RUNS}/RUN-PFDR-0b3699-repro/g-repro-report.json"
    out["gates"]["G-REPRO"] = {"artifact": gp, "pass": gr["pass"], "pairs_pass": [p["pass"] for p in gr["pairs"]],
                               "pair_mismatch_counts": [p.get("mismatch_count") for p in gr["pairs"]],
                               "ra06": read_by_ra06(gp)}
    pp = f"{RUNS}/RUN-PFDR-0b3699-p0-design/p0x-a-report.json"
    out["gates"]["P0X-A"] = {"artifact": pp, "pass": p0["pass"], "integer_pairs": p0["integer_pairs"],
                             "ra06": read_by_ra06(pp)}
    out["gates"]["G-FRESH"] = {"artifact": f"{RUNS}/RUN-PFDR-0b3699-p0-design/design.json (G-FRESH)",
                               "pass": design["G-FRESH"]["pass"],
                               "ra06": {"in_gates_read": an["gates_read"].get("design.json G-FRESH"),
                                        "design_in_ra06_view_map_sha_ok": vm6.get(f"{RUNS}/RUN-PFDR-0b3699-p0-design/design.json") == sha(R(RUNS, "RUN-PFDR-0b3699-p0-design", "design.json"))}}
    cp = f"{RUNS}/RUN-PFDR-0b3699-table/checks-report.json"
    for g in ("G4", "G4-R", "G7", "G7-OFFSET", "G-CURVE", "G-REL", "PC-R-iii"):
        out["gates"][g] = {"artifact": cp + f" checks[{g}]", "pass": chk["checks"][g]["pass"],
                           "instances_evaluated": chk["checks"][g]["instances_evaluated"],
                           "mismatch_keys": len(chk["checks"][g]["mismatch_keys"]),
                           "ra06": read_by_ra06(cp)}
    out["gates"]["checks_report_top_pass_is_AND"] = chk["pass"] == all(c["pass"] for c in chk["checks"].values())
    pi = rv["per_instance"]
    out["gates"]["G4-R_chain"] = {
        "row_verify_pass": rv["pass"], "row_verify_per_instance": len(pi),
        "row_verify_PASS": sum(1 for v in pi.values() if v == "PASS"),
        "checks_report_G4-R_instances": chk["checks"]["G4-R"]["instances_evaluated"],
        "per_instance_G4-R_PASS_in_checks_report": sum(1 for d in chk["per_instance"].values() if d.get("G4-R") == "PASS"),
        "row_verify_passed_to_ra06_as_gate_report": f"{RUNS}/RUN-PFDR-0b3699-table/row-verify.json" in an["gates_read"],
        "row_verify_in_ra06_view_map": f"{RUNS}/RUN-PFDR-0b3699-table/row-verify.json" in vm6,
        "sampled_instances_expected_c_mod_10": sum(1 for c in design["curves"] if c["curve"] % 10 == 0) * 8,
        "verifier_sha256_matches_pin": rv["verifier_sha256"] == "ff1b27d8150aa85db545a48c444f6a677cf88c42a540a647d975aa0a06800726",
        "harvest_files_sha256_match_bytes": all(sha(R(p)) == h for p, h in rv["harvest_files_sha256"].items()),
    }
    out["gates"]["PC-NULL-R"] = {"artifact": f"{RUNS}/RUN-PFDR-0b3699-calibrate/calibration.json PC-NULL-R",
                                 "pass": cal["PC-NULL-R"].get("pass"), "detail": json.dumps(cal["PC-NULL-R"])[:600],
                                 "ra06_reads": an["controls"]["PC-NULL-R"]}
    out["gates"]["PC-R-T"] = an["controls"]["PC-R-T"]
    out["gates"]["PC-R-D"] = an["controls"]["PC-R-D"]
    out["gates"]["invalidating_gates_failed"] = an["invalidating_gates_failed"]
    out["gates"]["calibration_sha256_in_ra06"] = {
        "analysis_json": an["calibration_sha256"], "file_now": sha(R(RUNS, "RUN-PFDR-0b3699-calibrate", "calibration.json")),
        "view_map": vm6.get(f"{RUNS}/RUN-PFDR-0b3699-calibrate/calibration.json")}

    # (7) blinding
    al = json.load(open(R(RUNS, "RUN-PFDR-0b3699-calibrate", "arm-read-log.json")))
    bad_arms, not_skipped, paths = [], [], []
    for f in al["files"]:
        paths.append(f["path"])
        extra = set(f.get("parsed_lines_by_arm", {})) - NULLS
        if extra:
            bad_arms.append([f["path"], sorted(extra)])
        if f.get("structured_lines_skipped_unparsed") is not True:
            not_skipped.append(f["path"])
    jobs = sorted(os.listdir(R(RUNS, "RUN-PFDR-0b3699-table", "attempt-1", "jobs")))
    expected = {f"{RUNS}/RUN-PFDR-0b3699-table/rows.jsonl.gz"} | {
        f"{RUNS}/RUN-PFDR-0b3699-table/attempt-1/jobs/{j}/harvest-rows.jsonl.gz" for j in jobs}
    al_keys = set()
    for f in al["files"]:
        al_keys |= set(f.keys())
    out["blinding"]["arm_read_log"] = {"files": len(al["files"]), "file_set_equals_expected": set(paths) == expected,
                                       "non_null_arms_parsed": bad_arms, "files_not_marked_skipped": not_skipped,
                                       "entry_keys": sorted(al_keys)}
    common = set(vm5) & set(vm6)
    out["blinding"]["view_maps"] = {
        "ra05_files": len(vm5), "ra06_files": len(vm6), "common": len(common),
        "common_sha_disagree": [p for p in common if vm5[p] != vm6[p]],
        "ra05_sha_vs_bytes_bad": [p for p, h in vm5.items() if sha(R(p)) != h],
        "ra06_sha_vs_bytes_bad": [p for p, h in vm6.items() if sha(R(p)) != h],
        "ra06_only": sorted(set(vm6) - set(vm5)), "ra05_only": sorted(set(vm5) - set(vm6)),
        "ra05_paths_outside_null_inputs": sorted(p for p in vm5 if not (
            p.endswith("harvest-rows.jsonl.gz") or p.endswith("/rows.jsonl.gz") or p.endswith("design.json")
            or p.endswith("merge-report.json")))}
    # RA-04 report files
    t = R(RUNS, "RUN-PFDR-0b3699-table")
    files = [os.path.join(t, f) for f in os.listdir(t) if os.path.isfile(os.path.join(t, f))]
    for step in ("checks", "merge"):
        d = os.path.join(t, "attempt-1", step)
        files += [os.path.join(d, f) for f in os.listdir(d)]
    files += [os.path.join(t, "attempt-1", f) for f in os.listdir(os.path.join(t, "attempt-1"))
              if os.path.isfile(os.path.join(t, "attempt-1", f))]
    scan = {}
    for f in sorted(files):
        rel = os.path.relpath(f, repo)
        if f.endswith(".gz") or f.endswith("run_wrapper.py") or f.endswith("checksums.sha256"):
            continue
        hits = []
        if f.endswith(".json"):
            walk_keys(json.load(open(f)), "$", hits)
        else:
            for i, line in enumerate(open(f, errors="replace")):
                if re.search(r"cert_pass|rows_emitted|relations_|R_star|kappa|\bz[_ =]|identity_failures|rows_checked|failure_count", line):
                    hits.append({"line": i + 1, "text": line.strip()[:200]})
        scan[rel] = {"hits": len(hits), "hit_samples": hits[:12]}
    out["blinding"]["ra04_report_files_scan"] = scan
    json.dump(out, open(outp, "w"), indent=1, default=str)
    print(json.dumps(out, indent=1, default=str)[:12000])


if __name__ == "__main__":
    main()
