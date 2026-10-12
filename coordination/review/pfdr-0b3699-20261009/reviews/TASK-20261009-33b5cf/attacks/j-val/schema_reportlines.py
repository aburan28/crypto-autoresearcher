"""J-VAL (1)/(8): schema completeness of every run location against
specification.yaml required_artifacts, and the facts behind the tripwire / outcome /
unexpected-observation lines of execution-report-9456e8.yaml. TASK-20261009-33b5cf.
PyYAML + standard library; no producer code.
  - per run location (run root and attempt-1): presence of manifest.yaml, command.txt,
    environment.json, stdout.log, stderr.log, raw-result.json, checksums.sha256 (root
    and attempt; per-step files at step dirs), per_run_data; manifest fields: run id,
    experiment id, status, completeness, code commit/dirty/source sha256, command(s),
    environment, inputs/seeds, inference block (Bedrock never), timing non-null,
    resources, certificate block kind none / 0 / 0.
  - per-rung z of every arm and null pseudo-cell vs t_dec (U-4), U-1, U-2, U-3.
  - G4 from every RA-04 job stdout.log summary (cert_fail == 0, cert_pass ==
    rows_emitted), read after RA-06 (AR-1 (2) restricts reads before RA-06 only).
  - wall seconds and peak RSS figures of the report vs execution.json; package bytes.
No seeds. Usage: python schema_reportlines.py <repo> <out.json>
"""
import json
import os
import sys

import yaml

RUNS = "experiments/EXP-PFDR-0b3699/runs"
PER_RUN_DATA = {
    "RUN-PFDR-0b3699-tests": ["junit.xml"],
    "RUN-PFDR-0b3699-repro": ["attempt-1/jobs", "g-repro-report.json"],
    "RUN-PFDR-0b3699-p0-design": ["curves.jsonl.gz", "design.json", "power.json", "p0x-a-report.json"],
    "RUN-PFDR-0b3699-table": ["attempt-1/jobs", "rows.jsonl.gz", "staircase.jsonl.gz", "merge-report.json",
                              "row-verify.json", "checks-report.json"],
    "RUN-PFDR-0b3699-calibrate": ["calibration.json", "arm-read-log.json", "view-map.json"],
    "RUN-PFDR-0b3699-analysis": ["analysis.json", "cells.jsonl", "view-map.json"],
}
LOC_FILES = ["manifest.yaml", "command.txt", "environment.json", "stdout.log", "stderr.log", "raw-result.json",
             "checksums.sha256"]


def main():
    repo, outp = sys.argv[1:3]
    R = lambda *p: os.path.join(repo, *p)  # noqa: E731
    out = {"schema": {}, "report_lines": {}}
    for rid, data in PER_RUN_DATA.items():
        root = R(RUNS, rid)
        r = {"root_missing": [f for f in LOC_FILES if not os.path.exists(os.path.join(root, f))],
             "attempt_missing": [f for f in ("manifest.yaml", "raw-result.json", "checksums.sha256")
                                 if not os.path.exists(os.path.join(root, "attempt-1", f))],
             "per_run_data_missing": [f for f in data if not os.path.exists(os.path.join(root, f))]}
        step_missing = []
        for d, _, fs in os.walk(os.path.join(root, "attempt-1")):
            if "execution.json" in fs:
                for f in ("command.txt", "environment.json", "stdout.log", "stderr.log", "run_wrapper.py"):
                    if f not in fs:
                        step_missing.append(os.path.relpath(os.path.join(d, f), root))
        r["step_files_missing"] = step_missing
        for loc in ("", "attempt-1"):
            m = yaml.safe_load(open(os.path.join(root, loc, "manifest.yaml")))["run"]
            code = m.get("code", {})
            inf = m.get("inference", {})
            cert = m.get("result", {}).get("certificate", {})
            fields = {
                "id": m.get("id") == rid, "experiment_id": m.get("experiment_id") == "EXP-PFDR-0b3699",
                "status": m.get("status"), "completeness": bool(m.get("completeness")),
                "code.commit": bool(code.get("commit")), "code.dirty_recorded": "dirty" in code,
                "code.source_sha256": bool(code.get("source_sha256")),
                "code.command": "command" in code, "code.commands": bool(code.get("commands")),
                "environment": bool(m.get("environment")), "inputs": "inputs" in m,
                "seeds": m.get("seeds") if not isinstance(m.get("seeds"), (dict, list)) else "present",
                "inference.requested_policy": inf.get("requested_policy"),
                "inference.resolved_model_id_or_provenance": inf.get("resolved_model_id") is not None or bool(inf.get("model_provenance")),
                "inference.model_verified_present": "model_verified" in inf,
                "inference.fallback_used": inf.get("fallback_used"),
                "inference.degraded_requirements_present": "degraded_requirements" in inf,
                "bedrock_mentioned_as_selected": "bedrock" in json.dumps(inf).lower() and "never" not in json.dumps(inf).lower(),
                "timing_non_null": bool(m.get("timing", {}).get("started_at")) and bool(m.get("timing", {}).get("finished_at")),
                "resources": {k: m.get("resources", {}).get(k) for k in ("peak_rss_bytes_max_process", "cpu_seconds_sum",
                                                                          "wall_seconds_span")},
                "certificate": cert,
                "task_id": m.get("task_id"), "protocol.handoff": m.get("protocol", {}).get("handoff"),
                "protocol.output_archive": m.get("protocol", {}).get("output_archive"),
                "protocol.amendments": m.get("protocol", {}).get("amendments"),
            }
            r["manifest_" + (loc or "root")] = fields
        out["schema"][rid] = r

    # report lines
    an = json.load(open(R(RUNS, "RUN-PFDR-0b3699-analysis", "analysis.json")))
    cal = json.load(open(R(RUNS, "RUN-PFDR-0b3699-calibrate", "calibration.json")))
    t_dec = an["primary"]["t_dec"]
    per_rung = {}
    for arm, rec in an["cells"].items():
        for b, v in rec["per_rung"].items():
            per_rung[f"{arm}|{b}"] = v["z"]
    obs = cal["PC-NULL-R"].get("observed_cells", {})
    for nm, rec in obs.items():
        for b, v in rec.get("per_rung", {}).items():
            per_rung[f"null:{nm}|{b}"] = v["z"]
    out["report_lines"]["t_dec"] = t_dec
    out["report_lines"]["per_rung_z"] = per_rung
    out["report_lines"]["U-4_listed_by_frozen_rule"] = sorted(k for k, z in per_rung.items() if abs(z) > t_dec)
    out["report_lines"]["U-4_listed_in_analysis"] = an["unexpected_observations"]
    out["report_lines"]["U-1"] = an["mutation"]["z"] > t_dec and an["primary"]["z"] <= t_dec
    out["report_lines"]["U-2"] = an["primary"]["z"] < -t_dec
    out["report_lines"]["U-3"] = an["cells"]["subgroup"]["z"] > t_dec
    out["report_lines"]["TW-ALIVE_trigger_O-A1_O-A1b_O-A2"] = an["outcome_id"] in ("O-A1", "O-A1b", "O-A2")
    out["report_lines"]["outcome_id"] = an["outcome_id"]
    # G4 from job summaries
    jobs = R(RUNS, "RUN-PFDR-0b3699-table", "attempt-1", "jobs")
    g4 = {"jobs": 0, "instances": 0, "cert_fail_nonzero": [], "pass_ne_emitted": [], "identity_failures_nonzero": [],
          "not_all_completed_valid": []}
    for j in sorted(os.listdir(jobs)):
        s = json.loads(open(os.path.join(jobs, j, "stdout.log")).read().strip().splitlines()[-1]
                       if not open(os.path.join(jobs, j, "stdout.log")).read().strip().startswith("{") else
                       open(os.path.join(jobs, j, "stdout.log")).read())
        g4["jobs"] += 1
        g4["instances"] += s["instances"]
        c = s["certificates"]
        if c["cert_fail"]:
            g4["cert_fail_nonzero"].append(j)
        if c["cert_pass"] != c["rows_emitted"]:
            g4["pass_ne_emitted"].append(j)
        if s.get("identity_failures"):
            g4["identity_failures_nonzero"].append(j)
        if any(not k.endswith("completed_valid") for k in s["by_status"]):
            g4["not_all_completed_valid"].append(j)
    out["report_lines"]["G4_job_summaries"] = g4
    # wall / rss
    ex5 = json.load(open(R(RUNS, "RUN-PFDR-0b3699-calibrate", "attempt-1", "calibrate", "execution.json")))
    ex6 = json.load(open(R(RUNS, "RUN-PFDR-0b3699-analysis", "attempt-1", "unmask", "execution.json")))
    exm = json.load(open(R(RUNS, "RUN-PFDR-0b3699-table", "attempt-1", "merge", "execution.json")))
    exc = json.load(open(R(RUNS, "RUN-PFDR-0b3699-table", "attempt-1", "checks", "execution.json")))
    out["report_lines"]["wall_peak"] = {
        "calibrate": [ex5["wall_seconds"], ex5["peak_rss_bytes_max_descendant"]],
        "unmask": [ex6["wall_seconds"], ex6["peak_rss_bytes_max_descendant"]],
        "merge": [exm["wall_seconds"], exm["peak_rss_bytes_max_descendant"]],
        "checks": [exc["wall_seconds"], exc["peak_rss_bytes_max_descendant"]]}
    tot = 0
    big = []
    for d, _, fs in os.walk(R("experiments/EXP-PFDR-0b3699")):
        for f in fs:
            sz = os.path.getsize(os.path.join(d, f))
            tot += sz
            if sz > 95_000_000:
                big.append(os.path.join(d, f))
    out["report_lines"]["package_bytes_now"] = tot
    out["report_lines"]["files_above_95MB"] = big
    json.dump(out, open(outp, "w"), indent=1, default=str)
    print(json.dumps(out, indent=1, default=str)[:9000])


if __name__ == "__main__":
    main()
