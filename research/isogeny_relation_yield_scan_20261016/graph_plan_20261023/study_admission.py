"""Validate a study-wide Coordinator admission for one scheduled graph arm."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import yaml

STUDY = Path(__file__).resolve().parents[1]
ROOT = STUDY.parents[1]
MATERIALIZER_DIR = STUDY / "graph_input_schedule_20261023"
sys.path.insert(0, str(MATERIALIZER_DIR))
from materialize import (  # noqa: E402
    SCHEDULE_DIR, WALKS, check_commitment, expected_binding, load_schedule, sha,
)


def relpath(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def repo_path(relative: str) -> Path:
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts or "\\" in relative:
        raise ValueError("admission path must be repository-relative")
    resolved = (ROOT / path).resolve()
    if resolved != ROOT.resolve() and ROOT.resolve() not in resolved.parents:
        raise ValueError("admission path escapes repository")
    return resolved


def validate_approval_fields(admission: dict, decision_doc: dict,
                             specification_doc: dict) -> tuple[dict, dict, int]:
    decision = decision_doc.get("coordinator_decision") if isinstance(decision_doc, dict) else None
    specification = (specification_doc.get("experiment")
                     if isinstance(specification_doc, dict) else None)
    stage = admission.get("execution_stage")
    if (not isinstance(decision, dict) or
            decision.get("id") != admission.get("decision_id") or
            decision.get("decided_by") != "coordinator" or
            decision.get("decision") != "approve" or
            decision.get("mode") != "design_experiment_approval" or
            decision.get("approved_by") != decision.get("id") or
            admission.get("experiment_id") not in decision.get("target_ids", []) or
            isinstance(stage, bool) or not isinstance(stage, int) or
            stage not in decision.get("official_transitions", {}).get("execution_authorized_stages", [])):
        raise ValueError("Coordinator decision does not authorize this experiment")
    if (not isinstance(specification, dict) or
            specification.get("id") != admission["experiment_id"] or
            specification.get("status") not in ("approved", "running") or
            specification.get("approved_by") != decision["id"] or
            specification.get("frozen") is not True or
            specification.get("execution_authorized") is not True or
            stage not in specification.get("execution_authorized_stages", [])):
        raise ValueError("experiment specification is not Coordinator-approved and frozen")
    return decision, specification, stage


def verify_study_admission(admission_path: Path, binding_path: Path, args,
                           manifest: dict, source_paths: dict[str, Path],
                           check_frozen_sources) -> tuple[str, dict]:
    """Recompute the shared study identity and one arm binding before execution.

    The approval record binds fixed study inputs once. Per-arm input hashes are
    derived and checked here, avoiding thousands of independent approval files.
    """
    admission = json.loads(admission_path.read_text())
    if (admission.get("schema") != "ectd.graph-study-admission.v1" or
            admission.get("status") != "approved" or
            admission.get("approved_by") != "coordinator" or
            not isinstance(admission.get("experiment_id"), str) or
            not admission["experiment_id"].startswith("EXP-")):
        raise ValueError("missing Coordinator-approved graph study admission")

    decision_path = repo_path(admission.get("decision_path", ""))
    decision_sha = admission.get("decision_sha256")
    if not isinstance(decision_sha, str) or sha(decision_path) != decision_sha:
        raise ValueError("Coordinator decision file digest differs")
    decision_doc = yaml.safe_load(decision_path.read_text())
    specification_path = repo_path(admission.get("specification_path", ""))
    specification_sha = admission.get("specification_sha256")
    if not isinstance(specification_sha, str) or sha(specification_path) != specification_sha:
        raise ValueError("approved experiment specification digest differs")
    specification_doc = yaml.safe_load(specification_path.read_text())
    decision, specification, execution_stage = validate_approval_fields(
        admission, decision_doc, specification_doc)

    source_commit = admission.get("source_commit")
    check_frozen_sources(ROOT, source_paths.values(), source_commit)
    expected_sources = {relpath(path): sha(path) for path in source_paths.values()}
    if admission.get("source_sha256") != expected_sources:
        raise ValueError("study admission source hashes differ")

    schedule_path = SCHEDULE_DIR / "discovery-arms.jsonl"
    schedule_manifest = SCHEDULE_DIR / "manifest.json"
    schedule_verification = SCHEDULE_DIR / "verification.json"
    schedule_sha = sha(schedule_path)
    schedule = admission.get("schedule")
    if schedule != {
            "arms_sha256": schedule_sha,
            "manifest_sha256": sha(schedule_manifest),
            "verification_sha256": sha(schedule_verification),
            "graph_manifest_sha256": sha(STUDY / "manifest-v2.json"),
            "arm_count": 8206,
            "target_probes": 60889088,
    }:
        raise ValueError("study admission schedule or graph digest differs")

    stratum = manifest.get("stratum")
    if stratum not in ("P29", "P37"):
        raise ValueError("unsupported graph stratum")
    strata = admission.get("strata")
    if not isinstance(strata, dict) or set(strata) != {"P29", "P37"}:
        raise ValueError("study admission must bind both P29 and P37")
    root_files = admission.get("root_files")
    if not isinstance(root_files, dict) or set(root_files) != {"base", "target", "verifier"}:
        raise ValueError("study admission root file set differs")
    root_paths = {name: repo_path(path) for name, path in root_files.items()}
    root_digests = None
    checked_commitments = {}
    for family in ("P29", "P37"):
        identity = strata[family]
        commitment_path = repo_path(identity.get("commitment_path", ""))
        _, source_row = load_schedule(f"{family}-v0000-graph_transport")
        roots, _ = check_commitment(source_row, root_paths, commitment_path)
        current_root_digests = {
            name + "_root_sha256": hashlib.sha256(root).hexdigest()
            for name, root in roots.items()}
        if (identity.get("commitment_sha256") != sha(commitment_path) or
                identity.get("graph_sha256") != sha(WALKS[family]) or
                any(identity.get(key) != value for key, value in current_root_digests.items())):
            raise ValueError(f"{family} commitment or roots differ from admission")
        if root_digests is None:
            root_digests = current_root_digests
        elif root_digests != current_root_digests:
            raise ValueError("P29 and P37 do not use the shared committed root set")
        checked_commitments[family] = commitment_path

    selected = strata[stratum]
    commitment_path = checked_commitments[stratum]
    arm_key = f"{stratum}-v{manifest.get('index', -1):04d}-{manifest.get('arm', '')}"
    _, row = load_schedule(arm_key)

    binaries = admission.get("binaries")
    if not isinstance(binaries, dict) or set(binaries) != {
            "collector_path", "collector_sha256", "count_verifier_path", "count_verifier_sha256"}:
        raise ValueError("study admission binary bindings are incomplete")
    collector = repo_path(binaries["collector_path"])
    count_verifier = repo_path(binaries["count_verifier_path"])
    if (sha(collector) != binaries["collector_sha256"] or
            sha(count_verifier) != binaries["count_verifier_sha256"] or
            sha(collector) != sha(args.collector) or
            sha(count_verifier) != sha(args.count_verifier)):
        raise ValueError("study admission binary digest differs")

    quota = 8192 if stratum == "P29" else 2048
    if (manifest.get("stage") != "discovery" or
            manifest.get("target_count") != quota or
            row.get("discovery_targets") != quota or
            row.get("base_rule") != manifest.get("arm") or
            row.get("path_index") != manifest.get("index") or
            row.get("p") != manifest.get("p") or
            row.get("r") != manifest.get("r") or
            row.get("model", {}).get("j") != manifest.get("j") or
            manifest.get("graph_sha256") != sha(WALKS[stratum]) or
            manifest.get("commitment_sha256") != sha(commitment_path)):
        raise ValueError("prepared input differs from the prespecified discovery arm")

    binding = expected_binding(row, roots, commitment_path, args.manifest.parent)
    saved = json.loads(binding_path.read_text())
    if saved != binding:
        raise ValueError("prepared arm binding does not replay")

    output_prefix = admission.get("output_prefix")
    prefix = repo_path(output_prefix)
    output = args.output.resolve()
    if prefix not in output.parents:
        raise ValueError("trial output is outside the admitted experiment run tree")
    return source_commit, {
        "study_admission_sha256": sha(admission_path),
        "study_schedule_sha256": schedule_sha,
        "arm_key": arm_key,
        "commitment_sha256": sha(commitment_path),
        "prepared_binding_sha256": sha(binding_path),
        "coefficient_vector_sha256": binding["coefficient_vector_sha256"],
        "source_commit": source_commit,
        "experiment_id": admission["experiment_id"],
        "approved_by": admission["approved_by"],
        "decision_id": decision["id"],
        "decision_sha256": decision_sha,
        "specification_sha256": specification_sha,
        "execution_stage": execution_stage,
    }
