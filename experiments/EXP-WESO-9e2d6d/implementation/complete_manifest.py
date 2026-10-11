"""Complete a wrapper-written manifest.yaml with the fields tools/validate_ledger.py
requires (run.code.commit, run.code.command, run.inputs, run.result with
certificate.kind = none), WITHOUT changing any measured value.

Added at the Coordinator's request (validator feedback, 2026-09-26) before the
Stage-B analysis_freeze was recorded.  The wrapper's original manifest is kept
byte-for-byte as manifest_wrapper_original.yaml; manifest.yaml is rewritten
with the original content plus the added fields, and a
`manifest_completion` block states exactly what was added.

Usage: python3 -B complete_manifest.py --run-dir <run dir>
"""
import argparse
import json
import os
import shlex
import shutil

import yaml


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    a = ap.parse_args()
    rd = a.run_dir
    mpath = os.path.join(rd, "manifest.yaml")
    orig = os.path.join(rd, "manifest_wrapper_original.yaml")
    if os.path.exists(orig):
        raise SystemExit("refusing: %s exists (completion already applied)" % orig)
    shutil.copyfile(mpath, orig)
    m = yaml.safe_load(open(mpath))
    run = m["run"]
    code = run["code"]
    added = []
    if not code.get("commit"):
        code["commit"] = code.get("commit_at_start")
        added.append("run.code.commit (= commit_at_start)")
    if "dirty" not in code:
        code["dirty"] = code.get("dirty_at_start")
        added.append("run.code.dirty (= dirty_at_start)")
    code.setdefault("dirty_note", "Implementation files are uncommitted (untracked) at run time; the sha256 of every "
                                  "implementation file at start and end of the run (code.implementation_sha256_at_start/_at_end) "
                                  "is the binding code identity.")
    if not code.get("command"):
        code["command"] = " ".join(shlex.quote(x) for x in run["command"]["wrapper_argv"])
        added.append("run.code.command (= wrapper argv, also in command.txt)")
    if not run.get("inputs"):
        run["inputs"] = {"specification": run["specification"]["path"], "parameters": {}}
        added.append("run.inputs")
    st = {}
    sp = os.path.join(rd, "status.json")
    if os.path.exists(sp):
        st = json.load(open(sp))
    if not run.get("result"):
        run["result"] = {
            "status": run.get("status"),
            "valid": run.get("validity") == "valid",
            "reason": run.get("validity_reason"),
            "stage_outcome": run.get("stage_outcome", st.get("stage_outcome")),
            "raw_result": "raw-result.json" if os.path.exists(os.path.join(rd, "raw-result.json")) else None,
            "execution_report": "execution_report.yaml" if os.path.exists(os.path.join(rd, "execution_report.yaml")) else None,
            "certificate": run.get("certificate", {"kind": "none"}),
        }
        added.append("run.result (status/validity/outcome copied from the wrapper manifest; certificate moved under result)")
    run["manifest_completion"] = {
        "tool": "experiments/EXP-WESO-9e2d6d/implementation/complete_manifest.py",
        "reason": "validator schema (run.result, run.code.commit, run.code.command, result.certificate.kind); "
                  "requested by the Coordinator before archival",
        "original_manifest": "manifest_wrapper_original.yaml",
        "fields_added": added,
        "measured_values_changed": False,
    }
    with open(mpath, "w") as f:
        yaml.safe_dump(m, f, sort_keys=False, width=110)
    print("completed", mpath, added)


if __name__ == "__main__":
    main()
