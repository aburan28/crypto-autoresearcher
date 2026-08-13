#!/usr/bin/env python3
"""Create additive, hash-pinned run-schema completions from archived bytes."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "tools/run_supersession_registry.yaml"

SUPERSEDED = [
    "experiments/EXP-DREG-001/runs/RUN-DREG-001-CTRLB-N12-D6/manifest.yaml",
    "experiments/EXP-ECDLP-03a8c9/runs/RUN-ECDLP-03a8c9-001/manifest.yaml",
    "experiments/EXP-ECDLP-1ed445/runs/RUN-ECDLP-1ed445-001/manifest.yaml",
    *[f"experiments/EXP-FIB-001/runs/{run}/manifest.yaml" for run in (
        "RUN-FIB-001", "RUN-FIB-002", "RUN-FIB-003", "RUN-FIB-004",
        "RUN-FIB-005", "RUN-FIB-006", "RUN-FIB-006B", "RUN-FIB-006C",
        "RUN-FIB-007", "RUN-FIB-008")],
    "experiments/EXP-MLDSA-2b6f17/runs/RUN-MLDSA-2b6f17-001/manifest.yaml",
    "experiments/EXP-MLDSA-3f7ab2/runs/RUN-MLDSA-3f7ab2-001/manifest.yaml",
    "experiments/EXP-MLDSA-a8d531/runs/RUN-MLDSA-a8d531-001/manifest.yaml",
    "experiments/EXP-MTBK-306bdb/runs/RUN-MTBK-306bdb-fr2/manifest.yaml",
    "experiments/EXP-P13-NC2b/runs/RUN-P13-NC2b-a/manifest.yaml",
    "experiments/EXP-P13-NC2d/runs/RUN-P13-NC2d-a/manifest.yaml",
    "experiments/EXP-SEMAEV-f48dd1/runs/RUN-SEMAEV-f48dd1-grid/manifest.yaml",
    "experiments/EXP-SEMAEV-f48dd1/runs/RUN-SEMAEV-f48dd1-smoke/manifest.yaml",
    "experiments/EXP-SSI-6a2619/runs/RUN-SSI-6a2619-001/manifest.yaml",
    "experiments/EXP-SSI-9b542d/runs/RUN-SSI-9b542d-001/manifest.yaml",
    "experiments/EXP-SSI-eca132/runs/RUN-SSI-eca132-001/manifest.yaml",
]

LEGACY_SOURCES = [
    "experiments/EXP-ECTD-001/runs/RUN-ECTD-001-screen/run.yaml",
    "experiments/EXP-ECTD-001/runs/RUN-ECTD-001-impl/run.yaml",
    "experiments/EXP-ICI-e622fd/runs/RUN-ICI-001/manifest.json",
    "experiments/EXP-IT-001/runs/RUN-IT-001-rc47/manifest.json",
    "experiments/EXP-OIFP-0ca0c9/runs/RUN-OIFP-001/manifest.json",
    "experiments/EXP-OIFP-0ca0c9/runs/RUN-OIFP-002/manifest.json",
    "experiments/EXP-OIFP-0ca0c9/runs/RUN-OIFP-003/manifest.json",
    "experiments/EXP-YIELD-004/runs/RUN-YIELD-004/manifest.json",
    "experiments/EXP-YIELD-004/runs/RUN-YIELD-005/manifest.json",
    "experiments/EXP-YIELD-004/runs/RUN-YIELD-006/manifest.json",
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def first(*values):
    for value in values:
        if value not in (None, "", {}):
            return value
    return None


def nested(mapping, *keys):
    value = mapping
    for key in keys:
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value


def archive_commit(path: Path) -> str:
    output = subprocess.check_output(
        ["git", "log", "-1", "--format=%H", "--", str(path.relative_to(ROOT))],
        cwd=ROOT, text=True).strip()
    return output or "unavailable"


def load(path: Path) -> dict:
    if path.suffix == ".json":
        value = json.loads(path.read_text(encoding="utf-8"))
    else:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(path)
    return value


def command_from(doc: dict, body: dict, run_dir: Path) -> str:
    command_file = run_dir / "command.txt"
    if command_file.exists() and command_file.read_text(encoding="utf-8").strip():
        return command_file.read_text(encoding="utf-8").strip()
    command = first(
        nested(body, "code", "command"),
        nested(body, "execution", "command"),
        nested(doc, "execution", "command"),
        doc.get("command"),
        body.get("command") if isinstance(body.get("command"), str) else None,
        nested(body, "implementation", "command"),
    )
    if isinstance(command, dict):
        parts = [command.get("executable"), command.get("script")]
        parts.extend(str(v) for v in command.get("arguments") or [])
        command = " ".join(str(v) for v in parts if v)
    if command:
        return str(command)
    method = body.get("method")
    if (body.get("no_computation") or body.get("no_computation_required")
            or method in {"corpus_analysis", "arithmetic_rederivation"}):
        return "NO_COMPUTATION: archived corpus-analysis procedure"
    return "COMMAND_NOT_CAPTURED: run classified provenance-incomplete"


def canonical_body(doc: dict, source: Path) -> dict:
    original = doc.get("run") if isinstance(doc.get("run"), dict) else doc
    body = dict(original)
    run_dir = source.parent
    run_id = first(body.get("id"), body.get("run_id"), run_dir.name)
    experiment_id = first(body.get("experiment_id"), run_dir.parents[1].name)
    command = command_from(doc, body, run_dir)
    commit = first(
        nested(body, "code", "commit"), body.get("git_commit"),
        nested(body, "git", "commit"), nested(body, "git", "head_commit"),
        nested(body, "execution", "git_commit"),
        nested(body, "provenance", "git_commit"),
        nested(body, "implementation", "git_commit"),
        nested(doc, "provenance", "git_commit"),
        nested(doc, "execution", "git_commit"),
    )
    commit_note = None
    if not commit:
        commit = archive_commit(source)
        commit_note = (
            "The execution revision was not captured in the archived record; "
            "this is the commit that first archived the source receipt, not an "
            "assertion about the implementation revision.")
    code = dict(body.get("code") or {})
    code["commit"] = str(commit)
    code["command"] = command
    if commit_note:
        code["commit_note"] = commit_note
    environment = first(body.get("environment"), doc.get("environment"), {})
    parameters = first(body.get("parameters"), doc.get("parameters"), {})
    inputs = body.get("inputs")
    if not isinstance(inputs, dict):
        inputs = {"parameters": parameters or {}}
        seeds = first(body.get("seeds"), body.get("random_seeds"), doc.get("seeds"))
        if seeds is not None:
            inputs["seeds"] = seeds
    elif "parameters" not in inputs:
        inputs = {"parameters": dict(inputs)}
    timing = first(
        body.get("timing"), body.get("timestamps"), body.get("execution"),
        doc.get("execution"), {
            "started_at": first(body.get("started_at"), body.get("start_time"),
                                body.get("timestamp")),
            "completed_at": first(body.get("completed_at"), body.get("end_time"),
                                  body.get("ended_at"), body.get("finished_at")),
            "wall_seconds": first(body.get("wall_clock_seconds"),
                                  body.get("elapsed_seconds")),
        })
    result = body.get("result")
    if not isinstance(result, dict):
        observations = first(
            body.get("results_summary"), body.get("results"), doc.get("results"),
            body.get("validity"), doc.get("validity"), {})
        result = {"observations": observations}
    result = dict(result)
    cert = result.get("certificate")
    if not isinstance(cert, dict):
        top_cert = body.get("certificate")
        cert = dict(top_cert) if isinstance(top_cert, dict) else {
            "kind": "none", "verified": True,
            "note": "No discrete-log or decomposition certificate is claimed.",
        }
    if cert.get("kind") not in {"discrete_log", "decomposition", "none"}:
        cert = {"kind": "none", "verified": True,
                "note": "Archived run made no schema-recognized certificate claim."}
    result["certificate"] = cert
    status = first(body.get("status"), nested(body, "validity", "status"),
                   body.get("validity"), "provenance_incomplete")
    repaired = {
        "id": str(run_id),
        "experiment_id": str(experiment_id),
        "status": str(status),
        "code": code,
        "environment": environment if isinstance(environment, dict)
        else {"archived_value": environment},
        "inputs": inputs,
        "timing": timing if isinstance(timing, dict) else {"archived_value": timing},
        "result": result,
    }
    for key, value in body.items():
        if key not in repaired and key not in {"run_id", "parameters", "certificate"}:
            repaired[key] = value
    repaired["schema_completion"] = {
        "source_path": str(source.relative_to(ROOT)),
        "source_sha256": sha(source),
        "method": "additive transcription from archived manifest and companions",
        "no_rerun": True,
    }
    return repaired


def copy_or_disclose(run_dir: Path, destination: str, candidates: list[str],
                     disclosure: str) -> None:
    target = run_dir / destination
    if target.exists():
        return
    for candidate in candidates:
        source = run_dir / candidate
        if source.exists():
            target.write_bytes(source.read_bytes())
            return
    target.write_text(disclosure + "\n", encoding="utf-8")


def companions(run_dir: Path, body: dict) -> None:
    copy_or_disclose(run_dir, "command.txt", [], body["code"]["command"])
    env_path = run_dir / "environment.json"
    if not env_path.exists():
        env_path.write_text(json.dumps(body["environment"], indent=2, default=str)
                            + "\n", encoding="utf-8")
    copy_or_disclose(run_dir, "stdout.log", ["stdout.txt"],
                     "STDOUT_NOT_CAPTURED: additive schema correction; no rerun")
    copy_or_disclose(run_dir, "stderr.log", ["stderr.txt"],
                     "STDERR_NOT_CAPTURED: additive schema correction; no rerun")
    copy_or_disclose(run_dir, "raw-result.json",
                     ["raw.json", "results.json", "result.json", "raw-results.json",
                      "collision_table.json", "summary.json", "manifest.json"],
                     '{"status":"RAW_RESULT_NOT_CAPTURED","no_rerun":true}')


def add_ssi_s1_runs() -> None:
    task = (ROOT / "coordination/goals/GOAL-SSI-001/batches/BATCH-044/tasks/"
            "TASK-20260804-946415")
    execution = yaml.safe_load((task / "execution_report.yaml").read_text())
    source_commit = archive_commit(task / "execution_report.yaml")
    for index in range(1, 4):
        run_id = f"RUN-SSI-S1-{index:02d}"
        run_dir = ROOT / "experiments/EXP-SSI-7c41d9/runs" / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        source = task / "runs" / f"run_{index:02d}" / "results.json"
        raw = json.loads(source.read_text())
        body = {
            "id": run_id,
            "experiment_id": "EXP-SSI-7c41d9",
            "status": "completed_valid",
            "code": {
                "commit": source_commit,
                "commit_note": "Commit that archived the frozen execution task.",
                "command": "python3 implementation/exp_ssi_s1.py",
            },
            "environment": {"source": "execution_report.yaml",
                            "archived": execution.get("execution_report", execution)},
            "inputs": {"parameters": raw.get("parameters", {}),
                       "seed": raw.get("seed")},
            "timing": raw.get("timing") or {"source": "results.json"},
            "result": {"observations": raw, "certificate": {
                "kind": "none", "verified": True,
                "note": "Statistical measurement; no DLP/decomposition claim."}},
            "schema_completion": {
                "source_path": str(source.relative_to(ROOT)),
                "source_sha256": sha(source), "no_rerun": True,
            },
        }
        (run_dir / "manifest.yaml").write_text(
            yaml.safe_dump({"run": body}, sort_keys=False), encoding="utf-8")
        (run_dir / "raw-result.json").write_bytes(source.read_bytes())
        companions(run_dir, body)


def main() -> None:
    registry = yaml.safe_load(REGISTRY.read_text())
    existing = {entry["superseded_path"]: entry
                for entry in registry.get("records") or []}
    for relative in SUPERSEDED:
        source = ROOT / relative
        doc = load(source)
        body = canonical_body(doc, source)
        body["supersedes"] = {
            "prior_manifest_path": relative,
            "prior_manifest_sha256": sha(source),
            "precedence": "Archived source governs every field it already carries.",
        }
        target = source.with_name("manifest_v2.yaml")
        target.write_text(yaml.safe_dump({"run": body}, sort_keys=False),
                          encoding="utf-8")
        companions(source.parent, body)
        existing[relative] = {
            "run_id": body["id"],
            "superseded_path": relative,
            "superseded_sha256": sha(source),
            "superseding_path": str(target.relative_to(ROOT)),
            "superseding_sha256": sha(target),
            "registered": "2026-08-08",
            "supersession_kind": "additive_schema_completion",
            "defect": "Archived manifest is incomplete under the current run schema.",
            "notes": "No experiment was rerun; fields and companions derive from archived bytes.",
        }
    for relative in LEGACY_SOURCES:
        source = ROOT / relative
        body = canonical_body(load(source), source)
        target = source.parent / "manifest.yaml"
        target.write_text(yaml.safe_dump({"run": body}, sort_keys=False),
                          encoding="utf-8")
        companions(source.parent, body)
    add_ssi_s1_runs()
    records = sorted(existing.values(), key=lambda item: item["superseded_path"])
    REGISTRY.write_text(yaml.safe_dump({
        "schema": "run-supersession-registry-v1", "records": records,
    }, sort_keys=False), encoding="utf-8")
    print(f"wrote {len(SUPERSEDED)} run supersessions, "
          f"{len(LEGACY_SOURCES) + 3} canonical manifests")


if __name__ == "__main__":
    main()
