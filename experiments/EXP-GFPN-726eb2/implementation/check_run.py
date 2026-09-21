#!/usr/bin/env python3
"""Completion-gate check for an EXP-GFPN-726eb2 run package.

Verifies: required artifacts exist; manifest has the validator's required
top-level fields and certificate.kind none; manifest status/metrics agree with
raw-result.json; audit-table rows agree with raw-result metrics; every
certificate path named in the audit table exists; ECPP certificates named in
factorization files re-verify with gfpn_arith.verify_ecpp (independent code).
"""
import ast, json, os, sys, yaml
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gfpn_arith import verify_ecpp

REQ = ["manifest.yaml", "command.txt", "environment.json", "stdout.log", "stderr.log", "raw-result.json", "audit-table.yaml", "figure-provenance.yaml", "certificates"]
TOP = ["id", "experiment_id", "status", "code", "environment", "inputs", "timing", "result"]

def main(run_dir):
    errs = []; notes = []
    for a in REQ:
        if not os.path.exists(os.path.join(run_dir, a)): errs.append(f"missing artifact {a}")
    man = yaml.safe_load(open(os.path.join(run_dir, "manifest.yaml")))["run"]
    for k in TOP:
        if man.get(k) in (None, ""): errs.append(f"manifest missing {k}")
    if man["result"]["certificate"]["kind"] != "none": errs.append("certificate.kind != none")
    raw = json.load(open(os.path.join(run_dir, "raw-result.json")))
    if man["status"] != raw["run_status"]: errs.append("manifest status != raw run_status")
    if man["result"]["metrics"] != raw["metrics"]: errs.append("manifest metrics != raw metrics")
    if man["id"] != os.path.basename(run_dir.rstrip("/")): errs.append("manifest id != directory")
    table = yaml.safe_load(open(os.path.join(run_dir, "audit-table.yaml")))["audit_table"]
    for row in table["rows"]:
        for cp in str(row.get("certificate", "")).split("+"):
            cp = cp.strip()
            if cp and not cp.startswith("runs/") and not os.path.exists(os.path.join(run_dir, cp)):
                errs.append(f"audit row {row['criterion']} names missing certificate {cp}")
    if "steps" in raw:  # GFPN curve run
        m = raw["metrics"]
        want = {"order_certificate": "PASS" if m["order_certificate"] == "certificate" else "NOT_VERIFIABLE",
                "twist_security_bits": "PASS" if m["twist_security_bits"] == "certificate" else ("BOUND" if m["twist_security_bits"] == "bound" else "NOT_VERIFIABLE")}
        for row in table["rows"]:
            if row["criterion"] in want and row["result"] != want[row["criterion"]]:
                errs.append(f"audit row {row['criterion']}={row['result']} disagrees with metrics {m[row['criterion']]}")
        rig = [r for r in table["rows"] if r["criterion"] == "rigidity_reproduced"][0]
        if (rig["result"] == "PASS") != bool(m.get("rigidity_first_hit_equals_published")): errs.append("rigidity row disagrees with metrics")
        oc = raw["steps"]["order_certificate"]
        if oc["certified"] and oc["certified_order"] != raw["steps"]["point_count"].get("N"): errs.append("certified order != SEA count")
        n_ecpp = 0
        for fn in os.listdir(os.path.join(run_dir, "certificates")):
            if fn.startswith("factorization-"):
                fc = json.load(open(os.path.join(run_dir, "certificates", fn)))
                prod = 1
                for f in fc["prime_factors"]: prod *= int(f["p"]) ** f["e"]
                for c in fc["unfactored_composites"]: prod *= int(c["c"])
                if prod != int(fc["n"]): errs.append(f"{fn}: product mismatch")
                for p, pr in fc["primality_proofs"].items():
                    if "certificate" in pr:
                        txt = [l for l in open(os.path.join(run_dir, pr["certificate"])).read().splitlines() if l.strip()][-1]
                        ok, _ = verify_ecpp(ast.literal_eval(txt)); n_ecpp += 1
                        if not ok or str(ast.literal_eval(txt)[0][0]) != p: errs.append(f"{fn}: ECPP re-verification failed for {p[:20]}...")
        txt = [l for l in open(os.path.join(run_dir, oc["primality"]["certificate"])).read().splitlines() if l.strip()][-1]
        ok, _ = verify_ecpp(ast.literal_eval(txt)); n_ecpp += 1
        if not ok: errs.append("order prime ECPP re-verification failed")
        notes.append(f"{n_ecpp} ECPP certificates re-verified independently")
    else:
        if raw["metrics"]["scurve_control_certificate_match"] != (raw["run_status"] == "completed_valid"): errs.append("control match/status disagree")
    print(f"{run_dir}: {'OK' if not errs else 'FAIL'}; {notes}")
    for e in errs: print("  -", e)
    return 0 if not errs else 1

if __name__ == "__main__":
    sys.exit(max(main(d) for d in sys.argv[1:]))
