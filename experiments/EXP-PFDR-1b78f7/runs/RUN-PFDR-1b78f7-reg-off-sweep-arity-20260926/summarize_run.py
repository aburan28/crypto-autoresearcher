"""Build raw-result.json for one EXP-PFDR-1b78f7 run directory (TASK-20260928-51b8c8).

    summarize_run.py tests|regression|census <run dir> [--gate G1|G2] [--expected N]

Reads only the run's own data files (junit.xml, rows.jsonl[.gz], regression-report.json,
harvest-rows/staircase files) and counts; it interprets nothing.
"""
from __future__ import annotations

import argparse
import gzip
import json
import os
import shutil
import xml.etree.ElementTree as ET
from collections import Counter

CLASSES = ("TT", "TB", "SS")


def rows_of(path: str) -> list[dict]:
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt") as fh:
        return [json.loads(l) for l in fh if l.strip()]


def find(rd: str, stem: str):
    for name in (stem + ".gz", stem):
        p = os.path.join(rd, name)
        if os.path.exists(p):
            return p
    return None


def harvest_gates(rows: list[dict]) -> dict:
    g = {"instances_with_harvest": 0, "G4_cert_ok_instances": 0, "G4_cert_fail_instances": [],
         "cert_pass_total": {c: 0 for c in CLASSES}, "cert_fail_total": {c: 0 for c in CLASSES},
         "rows_emitted_total": {c: 0 for c in CLASSES},
         "G5_identity_ok_instances": 0, "G5_identity_fail_instances": []}
    for r in rows:
        h = r.get("harvest")
        if not h:
            continue
        g["instances_with_harvest"] += 1
        key = [r.get("bits"), r.get("curve"), r.get("method"), r.get("fb"), r.get("arm"), r.get("mode")]
        ok = True
        for c in CLASSES:
            st = h[c]["at_stop"]
            g["cert_pass_total"][c] += st["cert_pass"]
            g["cert_fail_total"][c] += st["cert_fail"]
            g["rows_emitted_total"][c] += st["rows_emitted"]
            if st["cert_fail"] or st["cert_pass"] != st["rows_emitted"]:
                ok = False
        if ok:
            g["G4_cert_ok_instances"] += 1
        else:
            g["G4_cert_fail_instances"].append(key)
        if h["ss_store"]["identity_ok"]:
            g["G5_identity_ok_instances"] += 1
        else:
            g["G5_identity_fail_instances"].append(key)
    return g


def cmd_tests(rd: str, a) -> dict:
    root = ET.parse(os.path.join(rd, "junit.xml")).getroot()
    suites = root.findall("testsuite") if root.tag == "testsuites" else [root]
    tot = Counter()
    skipped = []
    for s in suites:
        for k in ("tests", "failures", "errors", "skipped"):
            tot[k] += int(s.get(k, 0))
        for tc in s.iter("testcase"):
            sk = tc.find("skipped")
            if sk is not None:
                skipped.append({"test": f"{tc.get('classname')}::{tc.get('name')}",
                                "reason": sk.get("message")})
    passed = tot["tests"] - tot["failures"] - tot["errors"] - tot["skipped"]
    return {"junit_totals": dict(tot), "passed": passed, "skipped_tests": skipped,
            "G3_pass": tot["failures"] == 0 and tot["errors"] == 0 and passed > 0,
            "certificate": {"kind": "none", "note": "unit tests; no solve or relation claimed"}}


def cmd_regression(rd: str, a) -> dict:
    rep = json.load(open(os.path.join(rd, "regression-report.json")))
    rows = rows_of(find(rd, "rows.jsonl"))
    ic = [r for r in rows if r["method"] != "rho"]
    rho = [r for r in rows if r["method"] == "rho"]
    out = {"gate": a.gate, "gate_pass": rep["pass"],
           "regression": {k: rep[k] for k in ("committed_rows", "new_rows", "rows_compared",
                                              "fraction_committed_rows_compared", "fields_compared",
                                              "mismatch_count", "mismatch_fields", "row_count_equal",
                                              "la_pivot_report", "keys_only_in_new_rows")}
           | {"missing_in_new": len(rep["missing_in_new"]),
              "extra_rows_in_new": len(rep["extra_rows_in_new"]),
              "duplicate_keys_new": len(rep["duplicate_keys_new"])},
           "instances": {"ic": len(ic), "rho": len(rho),
                         "ok_true": sum(1 for r in rows if r["ok"]),
                         "ok_false": [[r["bits"], r["curve"], r["method"], r["fb"], r.get("engine")]
                                      for r in rows if not r["ok"]]},
           "certificate": {"kind": "discrete_log",
                           "verified": all(r["ok"] for r in rows),
                           "verifier": ("per instance: solver `verified` (k*P == Q by curve.py "
                                        "scalar multiplication) AND k equal to the instance's "
                                        "generated target log (row field ok)"),
                           "instances_verified": sum(1 for r in rows if r["ok"]),
                           "instances": len(rows)}}
    if any("harvest" in r for r in rows):
        out["harvest_gates"] = harvest_gates(rows)
    return out


def cmd_census(rd: str, a) -> dict:
    rows = rows_of(find(rd, "rows.jsonl"))
    by = Counter()
    for r in rows:
        by[f"{r.get('panel')}|{r.get('method', '-')}|{r.get('arm', '-')}|{r.get('mode', '-')}|{r.get('status')}"] += 1
    status = Counter(r.get("status") for r in rows)
    failed = [{k: r.get(k) for k in ("bits", "curve", "method", "arm", "mode", "status", "status_reason")}
              for r in rows if r.get("status") != "completed_valid"]
    checks = Counter()
    for r in rows:
        for k, v in (r.get("checks") or {}).items():
            checks[f"{k}={v}"] += 1
    solved = [r for r in rows if r.get("k_found") or (r.get("method") == "rho" and r.get("ok"))]
    out = {"instances": len(rows), "by_status": dict(status), "by_panel_method_arm_mode_status": dict(by),
           "not_completed_valid": failed, "base_checks": dict(checks),
           "harvest_gates": harvest_gates(rows),
           "certificate": {"kind": "discrete_log",
                           "verified": all(r.get("k_verified", r.get("ok")) for r in solved),
                           "verifier": ("per solved instance: solver `verified` (k*P == Q by curve.py "
                                        "scalar multiplication) and k equal to the generated target "
                                        "log; harvested rows re-verified per row on an independent "
                                        "Curve instance (harvest block cert_pass/cert_fail)"),
                           "instances_solved": len(solved),
                           "instances_capped_without_k": sum(1 for r in rows if (r.get("harvest") or {}).get("terminated_by") == "attempt_cap")}}
    if a.expected is not None:
        out["expected_instances"] = a.expected
        out["all_expected_instances_present"] = len(rows) == a.expected
    for name in ("harvest-rows.jsonl", "staircase.jsonl"):
        p = find(rd, name)
        if p:
            out[f"{name}_lines"] = sum(1 for _ in (gzip.open(p, "rt") if p.endswith(".gz") else open(p)))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("kind", choices=("tests", "regression", "census"))
    ap.add_argument("run_dir")
    ap.add_argument("--gate", default=None)
    ap.add_argument("--expected", type=int, default=None)
    a = ap.parse_args()
    rd = a.run_dir
    res = {"tests": cmd_tests, "regression": cmd_regression, "census": cmd_census}[a.kind](rd, a)
    ex = json.load(open(os.path.join(rd, "execution.json")))
    res = {"run_id": ex["run_id"], "experiment_id": ex["experiment_id"],
           "exit_code": ex["exit_code"], "watchdog_expired": ex["watchdog_expired"]} | res
    if os.path.exists(os.path.join(rd, "raw-result.json")):
        raise SystemExit("raw-result.json exists")
    with open(os.path.join(rd, "raw-result.json"), "w") as fh:
        json.dump(res, fh, indent=2, sort_keys=True)
    shutil.copy2(__file__, os.path.join(rd, "summarize_run.py"))
    print(json.dumps({k: v for k, v in res.items() if k not in ("by_panel_method_arm_mode_status",
                                                                 "not_completed_valid")}, indent=1)[:3000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
