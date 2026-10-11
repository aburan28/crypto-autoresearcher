#!/usr/bin/env python3
"""Completion-gate check for one EXP-GFPN-05ff43 v2 run package (card completion_gate; agents/executor.md).

usage: python3 -B v2_check_run.py experiments/EXP-GFPN-05ff43/runs/<RUN-ID>

Checks: required artifacts; the run id is reserved in trial-plan-v2.json; manifest and raw-result agree
(status, metrics); the manifest records the phase-A commit, a clean implementation-v2 tree, the child
RLIMIT_AS read back by getrlimit (never a wrapper default), msolve threads executed == {1}, host RAM and
swap, and an inference block with requested_policy executor-implementation and no model id;
certificate.kind is decomposition iff certificates exist, and every certificate re-verifies with the
independent verifier; F3 is reported undecidable; no ratio is scored against 2^20; torsion_S5_norm is never
given order 1920.
"""
import json
import os
import sys

import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import v2_common as C                                    # noqa: E402
import v2_verify_independent as VI                       # noqa: E402

REQ = ["manifest.yaml", "command.txt", "environment.json", "stdout.log", "stderr.log", "raw-result.json",
       "ladder-table.yaml", "heur-dflat.yaml", "cost-band-p64.yaml", "certificates"]


def walk(obj, fn, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            fn(path + "/" + str(k), k, v)
            walk(v, fn, path + "/" + str(k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            walk(v, fn, path + "[%d]" % i)


def main(rd):
    errs, notes = [], []
    rid = os.path.basename(rd.rstrip("/"))
    plan = C.load_plan()
    try:
        C.plan_package(plan, rid)
    except KeyError:
        errs.append("run id not reserved in trial-plan-v2.json")
    for a in REQ:
        if not os.path.exists(os.path.join(rd, a)):
            errs.append("missing artifact " + a)
    man = yaml.safe_load(open(os.path.join(rd, "manifest.yaml")))["run"]
    raw = json.load(open(os.path.join(rd, "raw-result.json")))
    if man["id"] != rid:
        errs.append("manifest id != directory")
    if man["status"] != raw.get("run_status") and not (raw.get("run_status") == "completed_valid" and man["status"] == "failed"):
        errs.append("manifest status disagrees with raw-result run_status")
    if json.loads(json.dumps(man["result"]["metrics"], default=str)) != json.loads(json.dumps(raw.get("metrics", {}), default=str)):
        errs.append("manifest metrics != raw metrics")
    code = man.get("code", {})
    if not code.get("commit") or not code.get("implementation_v2_last_commit"):
        errs.append("phase-A commit not recorded")
    if code.get("implementation_v2_clean") is not True:
        errs.append("implementation-v2 tree not recorded clean")
    res = man.get("resources", {})
    caps = res.get("child_rlimit_as_read_back_by_getrlimit") or []
    req_cap = res.get("child_rlimit_as_requested_bytes")
    if raw.get("kind") != "aggregate":
        if not caps:
            errs.append("no child RLIMIT_AS read-back recorded")
        for c in caps:
            if c.get("soft") != req_cap or c.get("hard") != req_cap:
                errs.append("child RLIMIT_AS read-back %s != requested %s" % (c, req_cap))
        thr = res.get("msolve_threads_executed")
        if thr and thr != [1]:
            errs.append("msolve threads executed %s != [1]" % thr)
    if res.get("host_mem_total_kB") is None or res.get("host_swap_total_kB") is None:
        errs.append("host RAM / swap not recorded")
    inf = man.get("inference", {})
    if inf.get("requested_policy") != "executor-implementation" or inf.get("resolved_model_id") is not None or inf.get("fallback_used") is not False:
        errs.append("inference block not as required (requested_policy executor-implementation, resolved_model_id null, fallback_used false)")
    certdir = os.path.join(rd, "certificates")
    certs = sorted(f for f in os.listdir(certdir) if f.endswith(".json")) if os.path.isdir(certdir) else []
    ck = man["result"]["certificate"]
    if certs:
        if ck.get("kind") != "decomposition":
            errs.append("certificates present but certificate.kind != decomposition")
        bad = 0
        for f in certs:
            ok, npts, reasons = VI.verify(json.load(open(os.path.join(certdir, f))))
            if not ok:
                bad += 1
        if bad and man["status"] == "completed_valid":
            errs.append("%d certificate(s) fail independent re-verification on a completed_valid run (must be invalid_measurement)" % bad)
        notes.append("%d/%d certificates re-verify independently" % (len(certs) - bad, len(certs)))
    elif ck.get("kind") != "none":
        errs.append("no certificates but certificate.kind != none")

    def scan(path, k, v):
        if k in ("F3", "tail_check_2_36") and isinstance(v, str) and not v.startswith("undecidable"):
            errs.append("%s at %s is not reported undecidable" % (k, path))
    walk(raw, scan)
    for cl in raw.get("cells", []):
        if cl.get("arm") == "torsion_S5_norm" and cl.get("group_order") not in (None, 3840):
            errs.append("torsion_S5_norm reported with group order %s (must be 3840)" % cl.get("group_order"))
    txt = json.dumps(raw)
    for bad_key in ("D_raw_pred_over_D", "ratio_Draw_pred_over_D", "orbit_nonfreeness_ratio_vs_predicted_raw"):
        if bad_key in txt:
            errs.append("v1 constant-anchored field %s present (DC-2 T-1)" % bad_key)
    print("%s: %s; %s" % (rd, "PASS" if not errs else "FAIL", notes))
    for e in errs:
        print("  -", e)
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
