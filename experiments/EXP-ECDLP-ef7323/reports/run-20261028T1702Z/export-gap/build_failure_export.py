#!/usr/bin/env python3
"""Preserve a zero-observation operational export and the official refusal.

No verifier, measurement, cohort or constructor is executed. The protocol's
unstarted 440 cells are not represented as observed rows.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    with Path(path).open("x") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")


def entry(path, out, kind="receipt"):
    return {"path": os.path.relpath(path, out), "bytes": path.stat().st_size,
            "sha256": sha(path), "kind": kind}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    repo, run, out = args.repo_root.resolve(), args.run.resolve(), args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    for name in ("export.json", "validation.json", "export-gap.json"):
        if (out / name).exists():
            raise ValueError("fresh output files required")
    sys.path.insert(0, str(repo / "tools"))
    import experiment_protocol as ep
    protocol_path = repo / "experiments/EXP-ECDLP-ef7323/protocol.v2.json"
    protocol = json.loads(protocol_path.read_text())
    controller = json.loads((run / "modal/controller-receipt.json").read_text())
    seal = json.loads((run / "modal-evidence-manifest.json").read_text())
    raw = json.loads((run / "raw-result.json").read_text())
    assert protocol["freeze"]["protocol_sha256"] == "38f281bb1824e340f4f9f8cb81a732cb4eeadafc3693dca4ef56e2e5ecf8fdf7"
    assert controller["sandbox_create_calls"] == controller["engine_exec_calls"] == controller["plan_probe_exec_calls"] == 0
    assert controller["measurement_started"] is False and controller["submission_ambiguous"] is False
    assert controller["error"] == {"type": "ConnectionError", "message": "Could not connect to the Modal server."}
    for item in seal["files"]:
        path = run / item["path"]
        assert path.stat().st_size == item["bytes"] and sha(path) == item["sha256"]
    bundle = ep.export_skeleton(protocol, os.path.relpath(protocol_path, out), "modal", "transfer-ef7323-ea5986-operational-zero-observations")
    bundle["producer"] = {"runtime": "codex_cli", "model": None, "session": None, "role": "executor"}
    bundle["source"] = {"repo": protocol["repository"], "commit": controller["plan"]["source_revision_c"], "dirty": None}
    bundle["arms"] = [{"id": arm["id"], "role": arm["role"], "commit": arm["instrument"]["commit"],
                       "binary_sha256": arm["instrument"]["binary_sha256"]} for arm in protocol["arms"]]
    bundle["runs"], bundle["flow"] = [], ep.compute_flow([])
    files = [path for path in sorted(run.rglob("*")) if path.is_file() and not path.is_symlink()]
    bundle["files"] = [entry(path, out, "raw" if path.name == "modal-evidence.tar.gz" else "receipt") for path in files]
    bundle["files"].append(entry(protocol_path, out))
    # This is the registered postrun analysis source, not a claim that it ran.
    source = (protocol_path.parent / protocol["analysis_plan"]["script"]["path"]).resolve()
    assert sha(source) == protocol["analysis_plan"]["script"]["sha256"]
    bundle["analysis"] = {"script": entry(source, out, "analysis"), "outputs": [], "blinded": False,
                          "blinding_key_sha256": None, "unmasked_at": None}
    bundle["notes"] = [{"kind": "observation", "by": "failed-attempt export adapter", "text":
        "Zero actual curve/arm observations exist. No Sandbox create, engine execution, cohort generation, independent verification or scientific measurement occurred. Registered postrun analysis source is identified only as planned source. All scientific outcomes/rates/costs are unmeasured, not numerical zero. Frozen planned440 cells remain unexecuted and are never padded as observed rows."}]
    bundle["backend_record"] = {"schema": "classical.ecdlp.transfer-study.operational-failure-export/v1",
        "experiment_id": "EXP-ECDLP-ef7323", "run_id": "RUN-ECDLP-ea5986",
        "actual_curve_arm_observations": 0, "frozen_planned_curve_arm_cells": 440,
        "frozen_planned_primary_attempt_rows": 102828, "sandbox_create_calls": 0,
        "engine_exec_calls": 0, "plan_probe_exec_calls": 0, "fresh_cohort_draws": 0,
        "measurement_started": False, "controller": controller, "driver_raw_result": raw,
        "driver_sealed_member_manifest": seal, "actual_provider_context": None, "actual_sandbox_id": None,
        "actual_scientific_cohort": None, "scientific_outcomes": None, "independent_verifier_executed": False,
        "scientific_validity": "not_assessed", "all_clocks_wall_valid": False,
        "source_counters_replayed": False, "automatic_retry": False}
    candidate = out / "export.json"
    write(candidate, bundle)
    schema_findings = ep.schema_errors(bundle, "experiment.export/v1")
    lint_findings = ep.lint_export(bundle, protocol, out, True)
    command = [sys.executable, str(repo / "tools/experiment_protocol.py"), "check-export", str(candidate),
               "--protocol", str(protocol_path), "--verify-files"]
    with (out / "check-export.stdout.txt").open("xb") as stdout, (out / "check-export.stderr.txt").open("xb") as stderr:
        result = subprocess.run(command, cwd=repo, stdout=stdout, stderr=stderr, check=False)
    validation = {"schema_findings": schema_findings, "protocol_and_files_findings": lint_findings,
                  "official_check_argv": command, "official_check_returncode": result.returncode,
                  "stdout_sha256": sha(out / "check-export.stdout.txt"), "stderr_sha256": sha(out / "check-export.stderr.txt")}
    write(out / "validation.json", validation)
    status = "accepted_zero_observation_export" if not schema_findings and not lint_findings and result.returncode == 0 else "export_gap_official_check_refused_zero_observations"
    gap = {"schema": "classical.ecdlp.transfer-study.operational-export-gap/v1", "status": status,
        "export_sha256": sha(candidate), "export_bytes": candidate.stat().st_size,
        "actual_observed_rows": 0, "frozen_planned_rows": 440, "schema_valid": not schema_findings,
        "official_protocol_check_passed": result.returncode == 0, "validation_sha256": sha(out / "validation.json"),
        "explanation": "The candidate preserves zero actual observations. Any official missing-arm/sample-size refusal is retained exactly; no440fake rows, validator changes or gate weakening are used.",
        "candidate_or_verifier_calls": 0, "canonical_writes": False}
    write(out / "export-gap.json", gap)
    print(json.dumps({**gap, "official_check_returncode": result.returncode,
                      "schema_finding_count": len(schema_findings), "protocol_finding_count": len(lint_findings)}, sort_keys=True))


if __name__ == "__main__":
    main()
