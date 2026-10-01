#!/usr/bin/env python3
"""Completion-gate check for an EXP-GFPN-05ff43 run package.

Verifies: required artifacts exist (contract required_artifacts); manifest has the
validator's required top-level fields; certificate.kind is decomposition only when
certificates exist and every one re-verifies with verify_independent (pure Python)
-- otherwise none; manifest status/metrics agree with raw-result.json; ladder-table
rows agree with raw-result metrics; run id matches the directory.
"""
import json, os, sys, yaml
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import verify_independent

REQ = ["manifest.yaml", "command.txt", "environment.json", "stdout.log", "stderr.log", "raw-result.json",
       "ladder-table.yaml", "heur-dflat.yaml", "cost-band-p64.yaml", "certificates"]
TOP = ["id", "experiment_id", "status", "code", "environment", "inputs", "timing", "result"]

def main(run_dir):
    errs, notes = [], []
    for a in REQ:
        if not os.path.exists(os.path.join(run_dir, a)): errs.append(f"missing artifact {a}")
    man = yaml.safe_load(open(os.path.join(run_dir, "manifest.yaml")))["run"]
    for k in TOP:
        if man.get(k) in (None, ""): errs.append(f"manifest missing {k}")
    raw = json.load(open(os.path.join(run_dir, "raw-result.json")))
    if man["status"] != raw["run_status"]: errs.append("manifest status != raw run_status")
    if "metrics" not in raw:
        # the wrapper's own fallback record for a command that died before writing a
        # result: it legitimately has no metrics, and the manifest must agree
        if man["result"]["metrics"] not in ({}, None): errs.append("manifest carries metrics the raw result does not")
        notes.append("no metrics: command exited before writing a result (" + str(raw.get("note"))[:120] + ")")
    elif json.loads(json.dumps(man["result"]["metrics"], default=str)) != json.loads(json.dumps(raw["metrics"], default=str)):
        errs.append("manifest metrics != raw metrics")
    if man["id"] != os.path.basename(run_dir.rstrip("/")): errs.append("manifest id != directory")
    if not man["code"].get("commit") or not man["code"].get("command"): errs.append("code.commit/command missing")
    cert = man["result"]["certificate"]
    certfiles = sorted(f for f in os.listdir(os.path.join(run_dir, "certificates")) if f.endswith(".json"))
    if certfiles:
        if cert["kind"] != "decomposition": errs.append("certificates present but certificate.kind != decomposition")
        n_ok = 0
        for f in certfiles:
            c = json.load(open(os.path.join(run_dir, "certificates", f)))
            ok, npts, reasons = verify_independent.verify(c)
            if not ok: errs.append(f"certificate {f} FAILS independent re-verification: {reasons}")
            else: n_ok += 1
            if not c.get("known_scalar"): errs.append(f"certificate {f} not known-scalar")
        notes.append(f"{n_ok}/{len(certfiles)} decomposition certificates re-verified independently")
        if cert.get("verified") is not True and man["status"] == "completed_valid": errs.append("certificate.verified not true on completed_valid run with certificates")
        if raw["metrics"].get("lifted_verified_points_total") != sum(json.load(open(os.path.join(run_dir, "certificates", f))).get("m", 0) for f in certfiles if json.load(open(os.path.join(run_dir, "certificates", f)))["independent_verification"]["pass"]):
            errs.append("lifted_verified_points_total disagrees with verified certificates")
    else:
        if cert["kind"] != "none": errs.append("no certificates but certificate.kind != none")
    lt_path = os.path.join(run_dir, "ladder-table.yaml")
    if not os.path.exists(lt_path):
        print(f"{run_dir}: {'FAIL'}; {notes}")
        for e in errs: print("  -", e)
        return 1
    lt = yaml.safe_load(open(lt_path))["ladder_table"]
    if raw.get("kind") in ("cell", "raw") and lt.get("rows"):
        row = lt["rows"][0]
        if row["D"] != raw["metrics"].get("ideal_degree_D") or row["targets_attempted"] != raw["metrics"]["targets_attempted"]: errs.append("ladder-table row disagrees with raw metrics")
    if raw.get("kind") in ("cell", "raw") and not lt.get("rows") and raw["run_status"] == "completed_valid":
        errs.append("completed cell run has no ladder-table row")
    if raw.get("kind") in ("cell", "raw"):
        for nm in raw.get("not_measured", []):
            if nm["class"] not in ("resource_exhaustion", "infrastructure_error"): errs.append(f"not_measured entry with class {nm['class']}")
        if raw["run_status"] == "failed" and raw.get("failure_class") == "negative_observation": errs.append("timeout classified as negative_observation")
    print(f"{run_dir}: {'OK' if not errs else 'FAIL'}; {notes}")
    for e in errs: print("  -", e)
    return 0 if not errs else 1

if __name__ == "__main__":
    sys.exit(max(main(d) for d in sys.argv[1:]))
