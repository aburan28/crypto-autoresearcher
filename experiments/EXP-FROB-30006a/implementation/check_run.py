#!/usr/bin/env python3
"""Independent completion check for one EXP-FROB-30006a run directory (the trial plan's check_argv).

Exits 0 when the reproduction package is complete and internally consistent:
  * manifest.yaml parses with yaml.safe_load and names this run directory's id and trial;
  * command.txt, environment.json, stdout.log, raw-result.json exist (stderr.log may be empty);
  * raw-result.json and manifest.yaml agree on status, trial, timestamps and (for cells) on every
    reported conflict count / ratio;
  * no WDSat row is marked `scored` unless the run carries an exhaustive_enumeration_unsat certificate
    whose verdict is UNSAT and complete, the row status is UNSAT, and MAX_ID/MAX_ANF_ID match the ANF
    (C-CERT, C-SIZE); ratio == conflicts / (2^{ml}/m!) is recomputed exactly;
  * no resource_exhaustion row carries a conflict count or ratio (EX-4);
  * every WDSat build referenced by a row has config_used.json with the constants the row reports.
Exits 1 with a list of findings otherwise.  It asserts nothing about the decision rule.
"""
from __future__ import annotations

import json
import math
import sys
from fractions import Fraction
from pathlib import Path

import yaml


def main(run_dir: str) -> int:
    d = Path(run_dir)
    findings: list[str] = []
    for f in ("manifest.yaml", "command.txt", "environment.json", "stdout.log", "raw-result.json"):
        if not (d / f).is_file() or (d / f).stat().st_size == 0:
            findings.append(f"missing or empty required file {f}")
    if not (d / "stderr.log").is_file():
        findings.append("missing stderr.log")
    if findings:
        return report(findings)
    man = yaml.safe_load((d / "manifest.yaml").read_text())
    raw = json.loads((d / "raw-result.json").read_text())
    if man["run"]["id"] != d.name:
        findings.append(f"manifest run id {man['run']['id']} != directory {d.name}")
    if man["run"]["id"] != raw.get("run_id") or man["run"]["trial_id"] != raw.get("trial_id"):
        findings.append("manifest and raw-result disagree on run/trial id")
    if man["run"]["started_at"] != raw.get("started_at") or man["run"]["finished_at"] != raw.get("finished_at"):
        findings.append("manifest and raw-result disagree on timestamps")
    if (man["run"]["status"] == "completed_valid") != (raw.get("status") == "completed"):
        findings.append(f"validity {man['run']['status']} inconsistent with raw status {raw.get('status')}")
    for key in ("inference", "certificate", "code", "environment", "command"):
        if key not in man:
            findings.append(f"manifest lacks {key} block")
    inf = man.get("inference", {})
    if inf.get("requested_policy") != "executor-implementation" or inf.get("model_verified") is not False \
            or inf.get("bedrock_prohibition_observed") is not True:
        findings.append("inference block incomplete (policy / model_verified / bedrock_prohibition_observed)")
    if not man.get("code", {}).get("commit"):
        findings.append("no git commit recorded")
    if man.get("code", {}).get("dirty_tree") and not man["code"].get("implementation_sha256"):
        findings.append("dirty tree without per-file hashes")

    kind = raw.get("trial", {}).get("kind")
    if kind == "cell":
        check_cell(d, man, raw, findings)
    elif kind == "regression":
        g = raw.get("gate", {})
        if man["result_summary"].get("gate") != g:
            findings.append("gate block differs between manifest and raw-result")
        if raw.get("status") == "completed" and g.get("C-REG") != "PASS":
            findings.append("regression run completed without C-REG PASS")
        for cfg in ("default", "gauss_elim"):
            row = raw["wdsat"][cfg]
            ref = row.get("archived_conflicts")
            ok = row["status"] == "UNSAT" and ref is not None and ref / 2 <= row["conflicts"] <= 2 * ref
            if ok != row.get("within_2x"):
                findings.append(f"within_2x recomputation differs for {cfg}")
    elif kind == "pipeline":
        for row in raw.get("rows", []):
            for cfg, w in row.get("wdsat", {}).items():
                if w.get("status", "").startswith("resource_exhaustion") and w.get("conflicts") is not None:
                    findings.append(f"{row['label']}/{cfg}: resource_exhaustion carries a conflict count")
                if w.get("status") in ("SAT", "UNSAT") and w["status"] != row.get("certifier_verdict"):
                    findings.append(f"{row['label']}/{cfg}: WDSat {w['status']} vs certifier {row.get('certifier_verdict')}")
                if w.get("status") == "SAT" and not (w.get("sat_verification") or {}).get("verified"):
                    findings.append(f"{row['label']}/{cfg}: SAT assignment not verified on the field")
    else:
        findings.append(f"unknown trial kind {kind}")
    return report(findings)


def check_cell(d: Path, man: dict, raw: dict, findings: list[str]) -> None:
    cell = raw["cell"]
    null = Fraction(2 ** cell["ml"], math.factorial(cell["m"]))
    if cell["null_conflicts_exact"] != f"{null.numerator}/{null.denominator}":
        findings.append("null_conflicts_exact differs from 2^{ml}/m!")
    cert = raw.get("certificate") or {}
    cert_ok = (cert.get("certificate_kind") == "exhaustive_enumeration_unsat" and (cert.get("result") or {}).get("verdict") == "UNSAT"
               and (cert.get("result") or {}).get("complete") is True)
    if cert_ok:
        cpath = d / (raw["candidates"][-1]["dir"]) / "certificate.json"
        if not cpath.is_file():
            findings.append("certificate.json missing on disk")
        else:
            disk = json.loads(cpath.read_text())
            if disk["result"]["verdict"] != "UNSAT" or disk["instance_anf_sha256"] != raw["instance"]["anf"]["sha256"]:
                findings.append("on-disk certificate does not bind to the solved ANF")
        if raw["instance"]["target"]["xr_in_V"]:
            findings.append("x_R lies in V (degenerate target)")
    if man["certificate"]["kind"] != ("exhaustive_enumeration_unsat" if cert_ok else "none"):
        findings.append("manifest certificate.kind inconsistent with raw certificate")
    for cfg, row in raw.get("wdsat", {}).items():
        summ = man["result_summary"]["per_config"].get(cfg, {})
        for k in ("status", "conflicts", "conflict_ratio", "scored"):
            if summ.get(k) != row.get(k):
                findings.append(f"{cfg}: manifest summary {k}={summ.get(k)} vs raw {row.get(k)}")
        if row["status"].startswith("resource_exhaustion") and (row.get("conflicts") is not None or row.get("scored")):
            findings.append(f"{cfg}: resource_exhaustion carries conflicts/scored (EX-4)")
        if row.get("scored"):
            if not cert_ok:
                findings.append(f"{cfg}: scored without an independent UNSAT certificate (C-CERT)")
            if row["status"] != "UNSAT":
                findings.append(f"{cfg}: scored row is not UNSAT")
            if not row.get("max_id_anf_match"):
                findings.append(f"{cfg}: scored with MAX_ID mismatch (C-SIZE)")
            r = Fraction(row["conflicts"]) / null
            if row.get("conflict_ratio_exact") != f"{r.numerator}/{r.denominator}" or abs(row["conflict_ratio"] - float(r)) > 1e-12:
                findings.append(f"{cfg}: conflict_ratio does not equal conflicts / null")
        cfg_path = d / row["wdsat_build"] / "config_used.json"
        if not cfg_path.is_file():
            findings.append(f"{cfg}: config_used.json missing at {row['wdsat_build']}")
        else:
            used = json.loads(cfg_path.read_text())
            if used["constants"] != row["wdsat_constants"]:
                findings.append(f"{cfg}: config_used.json constants differ from the row")
            if used["constants"]["MAX_ID"] != row["sizing"]["MAX_ID"] or used["constants"]["MAX_ANF_ID"] != row["sizing"]["MAX_ANF_ID"]:
                findings.append(f"{cfg}: build MAX_ID/MAX_ANF_ID differ from ANF-derived sizing (C-SIZE)")
        anf = d / row["anf"]
        if not anf.is_file():
            findings.append(f"{cfg}: ANF input missing")
        else:
            import hashlib
            if hashlib.sha256(anf.read_bytes()).hexdigest() != row["anf_sha256"]:
                findings.append(f"{cfg}: ANF sha256 differs from the row")
        for log in (row.get("stdout"), row.get("stderr")):
            if log and not (d / "logs" / log).is_file():
                findings.append(f"{cfg}: process log {log} missing")


def report(findings: list[str]) -> int:
    if findings:
        print("CHECK FAILED")
        for f in findings:
            print(" -", f)
        return 1
    print("CHECK OK")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: check_run.py RUN_DIR", file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
