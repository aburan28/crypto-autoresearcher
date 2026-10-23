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


def require_discovery_stage(admission: dict) -> int:
    """This package implements discovery only; never borrow later-stage approval."""
    stage = admission.get("execution_stage")
    if isinstance(stage, bool) or stage != 0:
        raise ValueError("graph discovery launcher requires execution_stage 0; later-stage launchers are not implemented")
    return stage


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
    selection = None
    prior_admission = None
    if execution_stage == 0:
        require_discovery_stage(admission)
    elif execution_stage == 1:
        selection_value = admission.get("selection_path")
        if not isinstance(selection_value, str) or not selection_value:
            raise ValueError("confirmation admission requires a bound selection")
        selection_path = repo_path(selection_value)
        if sha(selection_path) != admission.get("selection_sha256"):
            raise ValueError("confirmation admission selection digest differs")
        selection = json.loads(selection_path.read_text())
        if (selection.get("schema") != "ectd.graph-discovery-selection-candidate/v1" or
                selection.get("status") != "selected_from_validated_discovery" or
                selection.get("discovery_arms_checked") != 8206 or
                selection.get("schedule_sha256") != sha(SCHEDULE_DIR / "discovery-arms.jsonl")):
            raise ValueError("confirmation admission lacks the complete frozen discovery selection")
        prior_value = admission.get("prior_admission_path")
        if not isinstance(prior_value, str) or not prior_value:
            raise ValueError("confirmation admission requires a bound prior discovery admission")
        prior_path = repo_path(prior_value)
        if sha(prior_path) != admission.get("prior_admission_sha256"):
            raise ValueError("confirmation admission prior-stage digest differs")
        prior_admission = json.loads(prior_path.read_text())
        if (prior_admission.get("schema") != "ectd.graph-study-admission.v1" or
                prior_admission.get("status") != "approved" or
                prior_admission.get("execution_stage") != 0 or
                prior_admission.get("experiment_id") != admission.get("experiment_id")):
            raise ValueError("confirmation admission does not descend from this study's discovery admission")
    else:
        raise ValueError("unsupported graph study execution stage")

    source_commit = admission.get("source_commit")
    frozen_paths = list(source_paths.values())
    if execution_stage == 1:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from build_confirmation_plan import SOURCE_PATHS as confirmation_sources
        frozen_paths = list(dict.fromkeys([*frozen_paths, *confirmation_sources]))
    check_frozen_sources(ROOT, frozen_paths, source_commit)
    expected_sources = {relpath(path): sha(path) for path in frozen_paths}
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
    if prior_admission is not None:
        prior_roots = prior_admission.get("root_files", {})
        if set(prior_roots) != {"base", "target", "verifier"}:
            raise ValueError("prior discovery admission root set differs")
        old_roots = {name: repo_path(path) for name, path in prior_roots.items()}
        if (root_paths["base"].read_bytes() != old_roots["base"].read_bytes() or
                root_paths["verifier"].read_bytes() != old_roots["verifier"].read_bytes() or
                root_paths["target"].read_bytes() == old_roots["target"].read_bytes()):
            raise ValueError("confirmation must reuse base/verifier roots and commit a fresh target root")
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
    _, row = load_schedule(arm_key, "discovery" if execution_stage == 0 else "confirmation")
    if selection is not None:
        selected = selection.get("strata", {}).get(stratum, {})
        if (arm_key not in selected.get("confirmation_arm_keys", []) or
                selected.get("commitment_sha256") !=
                prior_admission.get("strata", {}).get(stratum, {}).get("commitment_sha256")):
            raise ValueError("confirmation arm or discovery graph commitment differs from selection")

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

    quota = row["target_count"]
    if (manifest.get("stage") != row["stage"] or
            manifest.get("target_count") != quota or
            row.get("target_count") != quota or
            row.get("base_rule") != manifest.get("arm") or
            row.get("path_index") != manifest.get("index") or
            row.get("p") != manifest.get("p") or
            row.get("r") != manifest.get("r") or
            row.get("model", {}).get("j") != manifest.get("j") or
            manifest.get("graph_sha256") != sha(WALKS[stratum]) or
            manifest.get("commitment_sha256") != sha(commitment_path)):
        raise ValueError("prepared input differs from the prespecified discovery arm")

    binding = expected_binding(row, roots, commitment_path, args.manifest.parent,
                               "discovery" if execution_stage == 0 else "confirmation")
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
