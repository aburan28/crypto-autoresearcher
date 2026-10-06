"""Assemble implementation_report.yaml (file hashes, tests, smoke, open questions).
Usage: python3 make_report.py   (runs pytest; reads smoke/ outputs)"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
REL = "experiments/EXP-SDEG-85eefd/implementation"
REPORT = HERE / "implementation_report.yaml"
QUESTIONS = HERE / "open_questions.yaml"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def run_tests() -> dict:
    pr = subprocess.run([sys.executable, "-m", "pytest", "-q", "-rA", "-p", "no:cacheprovider", "tests"],
                        cwd=HERE, capture_output=True, text=True)
    passed = re.findall(r"^PASSED (\S+)", pr.stdout, re.M)
    failed = re.findall(r"^(?:FAILED|ERROR) (\S+)", pr.stdout, re.M)
    summary = [ln for ln in pr.stdout.splitlines() if re.search(r"\d+ (passed|failed)", ln)]
    return {"command": "python3 -m pytest -q -rA tests", "returncode": pr.returncode,
            "summary": summary[-1].strip("= ") if summary else None,
            "passed": len(passed), "failed": len(failed), "failed_ids": failed, "test_ids": passed}


SMOKE_MAC = HERE / "smoke" / "mac_v4"
SMOKE_MAC_V3 = HERE / "smoke" / "mac"
SMOKE_POD = HERE / "smoke" / "pod"
SMOKE_POD_V3 = HERE / "smoke" / "pod_v4"  # written only if the v4 pod smoke ran
DRY_MAC = HERE / "smoke" / "driver_dryrun" / "DRYRUN-v3-mac"


def smoke_summary(path=SMOKE_MAC) -> dict:
    s = json.loads((path / "smoke_results.json").read_text())
    cells = s["cells"]
    b2 = s.get("b2_sage_crosscheck", {})
    return {
        "namespace": s["namespace"], "fixture": s["fixture"], "not_a_scientific_run": True,
        "fixture_reproduction": {k: s["fixture_reproduction"].get(k) for k in
                                 ("byte_identical", "reproduced_sha256", "frozen_json_sha256",
                                  "generator_sha256_matches_amendment")},
        "semaev_polys_sha256": s["semaev_polys_sha256"],
        "identity_check_1000_tuples": {"passed": s["identity_check"]["passed"],
                                       "failures": s["identity_check"]["failures"],
                                       "zero_nonzero_counts": s["identity_check"]["zero_nonzero_counts"]},
        "cells": {k: {kk: v[kk] for kk in ("V_size", "forward_table_size", "forward_table_s3_roots_ok",
                                           "oracle_enumerated", "oracle_expected", "n_queries",
                                           "oracle_members", "planted_all_members",
                                           "decision_agreement_B0_B1_oracle", "hit_triple_sets_equal",
                                           "witnesses_checked", "all_witnesses_verified", "defects")}
                  for k, v in cells.items()},
        "totals": {"queries": sum(v["n_queries"] for v in cells.values()),
                   "decision_agreement": sum(v["decision_agreement_B0_B1_oracle"] for v in cells.values()),
                   "hit_triple_sets_equal": sum(v["hit_triple_sets_equal"] for v in cells.values()),
                   "witnesses_checked": sum(v["witnesses_checked"] for v in cells.values()),
                   "all_witnesses_verified": all(v["all_witnesses_verified"] for v in cells.values())},
        "accounting_audit_on_all_smoke_receipts": {k: s["accounting_audit"][k]
                                                   for k in ("receipts_checked", "accepted")},
        "b2_vs_sage": {"returncode": b2.get("returncode"), "by_method": b2.get("by_method"),
                       "fglm_queries": [d["query_id"] for d in b2.get("details", []) if d["method"] == "fglm"],
                       "fglm_seconds": {d["query_id"]: d.get("seconds") for d in b2.get("details", [])
                                        if d["method"] == "fglm"}},
        "rho_correctness_only": {k: s["rho_correctness"][k] for k in ("targets", "solved_and_verified")},
        "b2_split_nosage": {"checked": sum(v.get("b2_split_nosage_checked", 0) for v in cells.values()),
                            "mismatches": [m for v in cells.values() for m in v.get("b2_split_nosage_mismatches", [])]},
        "opcounts": s.get("opcounts"),
        "host": {k: (s.get("host") or {}).get(k) for k in ("hostname", "host_kind", "platform", "python",
                                                            "numpy", "container_id", "cpu_quota")},
    }


def dryrun_v3_summary() -> dict | None:
    d = DRY_MAC
    if not (d / "manifest.yaml").exists():
        return None
    m = yaml.safe_load((d / "manifest.yaml").read_text())
    raw = json.loads((d / "raw-result.json").read_text())
    ch = yaml.safe_load((d / "charged" / "manifest.yaml").read_text())
    return {"path": f"{REL}/smoke/driver_dryrun/DRYRUN-v3-mac",
            "parts": {k: {"status": v["status"], "host": (v.get("host") or {}).get("hostname")}
                      for k, v in m["parts"].items()},
            "charged_summary": ch.get("summary"), "opcounts_sha256": m.get("opcounts_sha256"),
            "fixture_reproduction_byte_identical": raw["fixture_reproduction"]["byte_identical"],
            "b2_fglm_checks": len(raw["b2_fglm_crosscheck"]),
            "b2_fglm_all_match": all(r["degree_match"] and r["root_set_match"] for r in raw["b2_fglm_crosscheck"]),
            "merge_problems": raw["merge_problems"], "merged_validity": m["validity"],
            "note": "three-part driver path (charged -> sage -> merge) on the Mac in the smoke namespace "
                    "(L8-s1, 4 queries/deck, 2 rho targets, --b2-fglm-per-cell 0 so FGLM ran on the |V|=4 deck "
                    "only). The metrics/outcome over one size are pipeline output only and are NOT reported; "
                    "'procedure_defect' is the expected consequence of a single size (every beta undefined)."}


def pod_summary(q) -> dict:
    mac = SMOKE_MAC / "opcounts.json"
    pod = SMOKE_POD / "smoke" / "opcounts.json"
    lg = HERE / "smoke" / "pod_attempts.log"
    lines = lg.read_text().split("\n") if lg.exists() else []
    lines = [ln for ln in lines if ln.strip()]
    out = {"performed": pod.exists(),
           "endpoint_probes": {"log": f"{REL}/smoke/pod_attempts.log", "n": len(lines),
                               "first": lines[0] if lines else None, "last": lines[-1] if lines else None,
                               "n_open": sum(1 for ln in lines if ln.endswith(" open"))}}
    if not pod.exists():
        out["reason"] = "pod SSH endpoint refused connections; see infrastructure_incidents"
        return out
    out["smoke"] = smoke_summary(SMOKE_POD / "smoke")
    out["opcount_identity"] = {"mac_sha256": sha(mac), "pod_sha256": sha(pod),
                               "byte_identical": mac.read_bytes() == pod.read_bytes()}
    dm = SMOKE_POD / "driver_dryrun_pod" / "DRYRUN-v3-pod" / "charged" / "manifest.yaml"
    if dm.exists():
        m = yaml.safe_load(dm.read_text())
        out["charged_driver_dry_run"] = {"status": m["status"], "workers": m.get("workers"),
                                         "summary": m.get("summary"), "host": m.get("host"),
                                         "admission_readings_C9": m.get("admission_readings_C9"),
                                         "opcounts_sha256": m.get("opcounts_sha256")}
    return out


def dryrun_summary() -> dict | None:
    d = HERE / "smoke" / "v2" / "driver_dryrun" / "DRYRUN-smoke-001"
    if not (d / "manifest.yaml").exists():
        return None
    m = yaml.safe_load((d / "manifest.yaml").read_text())
    raw = json.loads((d / "raw-result.json").read_text()) if (d / "raw-result.json").exists() else {}
    return {"path": f"{REL}/smoke/v2/driver_dryrun/DRYRUN-smoke-001",
            "status": m.get("status"), "validity": m.get("validity"),
            "fixture_reproduction_byte_identical": (m.get("fixture_reproduction") or {}).get("byte_identical"),
            "oracle_agreement": raw.get("oracle_agreement"), "n_scored": raw.get("n_scored"),
            "witnesses_verified": raw.get("witnesses_verified"),
            "accounting_audit_accepted": raw.get("accounting_audit_accepted"),
            "b2_sage_crosscheck": raw.get("b2_sage_crosscheck"),
            "rho": [{k: r[k] for k in ("fixture", "n", "solved_verified")} for r in raw.get("rho", [])],
            "note": "driver end-to-end path in the smoke namespace (L8-s1, 4 queries/deck, 2 rho targets); "
                    "the metrics/outcome it wrote over one size are pipeline output only and are NOT reported. "
                    "Its validity label 'procedure_defect' is the expected consequence of a single size: every "
                    "beta is undefined, so the progression beta_elim < 0.30 check cannot pass."}


def v2_identity() -> dict:
    new = {(r["query_id"], r["backend"]): r for r in json.loads((SMOKE_MAC / "opcounts.json").read_text())}
    n = diff = 0
    for f in sorted((HERE / "smoke" / "v2" / "cells").glob("*.json")):
        for qq in json.loads(f.read_text())["queries"]:
            for be in ("B0", "B1"):
                o, r = qq["backends"][be], new[(qq["query_id"], be)]
                n += 1
                diff += not (o["ops"] == r["ops"] and o["W_query"] == r["W_query"]
                             and o.get("W_query_to_first_hit") == r["W_query_to_first_hit"]
                             and [list(t) for t in o["hit_triples"]] == r["hit_triples"])
    return {"rows_compared": n, "rows_differing": diff}


def fx_identity() -> dict:
    def h(p):
        return sha(p) if p.exists() else None
    out = {"mac_v4": h(SMOKE_MAC / "opcounts.json"), "mac_v3": h(SMOKE_MAC_V3 / "opcounts.json"),
           "pod_v4": h(SMOKE_POD_V3 / "smoke" / "opcounts.json"),
           "pod_v4_note": ("None = pod smoke with the v4 code not performed (pod SSH endpoint refused every "
                           "probe; see pod_smoke.endpoint_probes)"),
           "pod_v3": h(SMOKE_POD / "smoke" / "opcounts.json"),
           "pod_v3_note": "smoke/pod holds the v3-code pod smoke (before FX-1..FX-5); its pytest step had failed "
                          "with 'No module named pytest', so no pod test count exists",
           "reference": "79e80dd11f48c5c6553e1782e74605656ca6c2a1178b2428c5c35eb00ca80651"}
    p = SMOKE_MAC / "opcounts.json"
    out["mac_v4_rows"] = len(json.loads(p.read_text())) if p.exists() else None
    tp = SMOKE_POD / "pod_pytest.txt"
    out["pod_pytest_tail"] = tp.read_text().strip().splitlines()[-1] if tp.exists() and tp.read_text().strip() else None
    return out


def main():
    files = sorted(p for p in HERE.rglob("*") if p.is_file() and "__pycache__" not in p.parts
                   and ".pytest_cache" not in p.parts and p.name not in (REPORT.name,))
    q = yaml.safe_load(QUESTIONS.read_text())
    tests = run_tests()
    sm = smoke_summary()
    sm["v2_opcount_identity"] = v2_identity()
    rep = {"implementation_report": {
        "task_id": "TASK-20260928-c7aad3", "experiment_id": "EXP-SDEG-85eefd", "protocol_version": 4,
        "protocol_v4_amendment": "AMD-20260928-d3ed9e", "protocol_v4_decision": "DEC-20260928-48a648",
        "approval_decision_id": "DEC-20260928-54db4a", "batch_id": "BATCH-656ba1",
        "protocol_v3_amendment": "AMD-20260928-7ce387", "protocol_v3_decision": "DEC-20260928-6b03c5",
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "worktree_base_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=HERE, capture_output=True,
                                               text=True).stdout.strip(),
        "scientific_run_performed": False, "runs_directory_created": False,
        "inference": q["inference"],
        "files": [{"path": f"{REL}/{p.relative_to(HERE)}", "sha256": sha(p), "bytes": p.stat().st_size}
                  for p in files],
        "tests": tests,
        "fx_v4": dict(q["fx_v4"], opcounts_identity=fx_identity()),
        "v3_changes": q["v3_changes"],
        "smoke": sm,
        "driver_smoke_dry_run_v3": dryrun_v3_summary(),
        "pod_smoke": pod_summary(q),
        "v2_archive": {"path": f"{REL}/smoke/v2", "driver_smoke_dry_run_v2": dryrun_summary(),
                       "note": "v2 smoke outputs kept unchanged for reference; the v3 Mac smoke reproduces "
                               "their 128 B0/B1 per-query op-count rows exactly (see smoke.v2_opcount_identity)"},
        "completion_gate": q["completion_gate"],
        "completion_gate_v3": q["completion_gate_v3"],
        "deviations": q["deviations"],
        "open_questions": q["open_questions"],
        "open_questions_v3": q["open_questions_v3"],
        "infrastructure_incidents": q["infrastructure_incidents"],
        "blocking_for_scientific_run": q["blocking_for_scientific_run"],
    }}
    REPORT.write_text(yaml.safe_dump(rep, sort_keys=False, width=100, allow_unicode=True))
    print(tests["summary"])


if __name__ == "__main__":
    main()
