"""Create and validate rootless documents consumed by graph trial workers.

The custodian keeps the seed roots and private materializer binding.  The
worker receives only a public admission projection and a binding projection
that omits the low-entropy scalar commitment.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

from study_admission import ROOT, repo_path

WORKER_SCHEMA = "ectd.graph-worker-admission.v1"
PUBLIC_BINDING_SCHEMA = "ectd.graph-prepared-arm-public-binding.v1"
ROOT_NAMES = ("base", "target", "verifier")
SECRET_KEYS = {
    "root_files", "base_root_file", "target_root_file", "verifier_root_file",
    "q_scalar_commitment_sha256", "commitment_path", "commitment_file_path",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def assert_rootless(value: object, where: str = "document") -> None:
    """Fail closed if any private root locator or scalar commitment is present."""
    if isinstance(value, dict):
        for key, child in value.items():
            if key in SECRET_KEYS:
                raise ValueError(f"{where} contains executor-forbidden field {key}")
            assert_rootless(child, f"{where}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            assert_rootless(child, f"{where}[{index}]")


def _root_digests(admission: dict) -> dict[str, str]:
    root_files = admission.get("root_files")
    if not isinstance(root_files, dict) or set(root_files) != set(ROOT_NAMES):
        raise ValueError("private admission must bind exactly three roots")
    digests = {name + "_root_sha256": sha(repo_path(root_files[name]))
               for name in ROOT_NAMES}
    if len(set(digests.values())) != 3:
        raise ValueError("private admission roots must be distinct")
    for family in ("P29", "P37"):
        identity = admission.get("strata", {}).get(family, {})
        if any(identity.get(key) != value for key, value in digests.items()):
            raise ValueError(f"{family} commitment roots differ from private root files")
    return digests


def _public_parent(path_value: str, expected_sha: str, experiment_id: str) -> dict:
    path = repo_path(path_value)
    if sha(path) != expected_sha:
        raise ValueError("prior-stage admission digest differs")
    prior = json.loads(path.read_text())
    if (prior.get("schema") != "ectd.graph-study-admission.v1" or
            prior.get("status") != "approved" or
            prior.get("experiment_id") != experiment_id):
        raise ValueError("prior-stage private admission is invalid")
    return {
        "admission_sha256": expected_sha,
        "execution_stage": prior.get("execution_stage"),
        "root_digests": _root_digests(prior),
    }


def project_worker_admission(admission: dict) -> dict:
    """Return the allowlisted, rootless subset of an approved study admission."""
    if (admission.get("schema") != "ectd.graph-study-admission.v1" or
            admission.get("status") != "approved" or
            admission.get("approved_by") != "coordinator" or
            not str(admission.get("experiment_id", "")).startswith("EXP-")):
        raise ValueError("only a Coordinator-approved study admission can be projected")
    roots = _root_digests(admission)
    strata = {}
    for family in ("P29", "P37"):
        source = admission.get("strata", {}).get(family)
        if not isinstance(source, dict):
            raise ValueError("both strata must be present")
        strata[family] = {
            key: source[key] for key in (
                "commitment_sha256", "graph_sha256",
                "base_root_sha256", "target_root_sha256", "verifier_root_sha256")
            if key in source
        }
        if set(strata[family]) != {
                "commitment_sha256", "graph_sha256",
                "base_root_sha256", "target_root_sha256", "verifier_root_sha256"}:
            raise ValueError(f"{family} commitment binding is incomplete")
    binary_source = admission.get("binaries")
    if not isinstance(binary_source, dict):
        raise ValueError("binary bindings are missing")
    binaries = {key: binary_source[key] for key in (
        "collector_path", "collector_sha256", "count_verifier_path",
        "count_verifier_sha256", "sage_path", "sage_sha256") if key in binary_source}
    parent_stages = []
    if admission.get("execution_stage", 0) >= 1:
        parent_stages.append(_public_parent(
            admission["prior_admission_path"], admission["prior_admission_sha256"],
            admission["experiment_id"]))
    if admission.get("execution_stage") == 2:
        stage1 = repo_path(admission["prior_admission_path"])
        stage1_doc = json.loads(stage1.read_text())
        parent_stages.append(_public_parent(
            stage1_doc["prior_admission_path"], stage1_doc["prior_admission_sha256"],
            admission["experiment_id"]))
    fields = (
        "experiment_id", "approved_by", "decision_id", "decision_path",
        "decision_sha256", "specification_path", "specification_sha256",
        "execution_stage", "source_commit", "source_sha256", "schedule",
        "output_prefix", "selection_path", "selection_sha256",
        "finalist_analysis_path", "finalist_analysis_sha256",
        "prior_admission_sha256", "task_id",
    )
    result = {"schema": WORKER_SCHEMA, "status": "approved"}
    result.update({key: admission[key] for key in fields if key in admission})
    result["root_digests"] = roots
    result["strata"] = strata
    result["binaries"] = binaries
    result["prior_stages"] = parent_stages
    result["origin_admission_sha256"] = hashlib.sha256(
        json.dumps(admission, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    assert_rootless(result)
    return result


def public_binding(private_binding: dict) -> dict:
    """Drop witness-derived values before a prepared binding reaches a worker."""
    if private_binding.get("schema") != "ectd.graph-prepared-arm-binding.v1":
        raise ValueError("unexpected private materializer binding schema")
    result = {key: value for key, value in private_binding.items()
              if key not in SECRET_KEYS}
    result["schema"] = PUBLIC_BINDING_SCHEMA
    assert_rootless(result)
    return result


def write_worker_admission(private_path: Path, output_path: Path) -> dict:
    private = json.loads(private_path.read_text())
    projected = project_worker_admission(private)
    with output_path.open("x", encoding="utf-8") as stream:
        json.dump(projected, stream, indent=2, sort_keys=True)
        stream.write("\n")
    return projected


def write_public_binding(private_path: Path, output_path: Path) -> dict:
    private = json.loads(private_path.read_text())
    projected = public_binding(private)
    with output_path.open("x", encoding="utf-8") as stream:
        json.dump(projected, stream, indent=2, sort_keys=True)
        stream.write("\n")
    return projected


def verify_worker_documents(admission_path: Path, binding_path: Path,
                           input_path: Path, manifest_path: Path,
                           collector_path: Path, count_verifier_path: Path,
                           output_path: Path) -> dict:
    """Check the worker-visible projection and exact prepared-arm files.

    This deliberately cannot re-open the private admission or any seed root.
    It verifies the frozen approval documents, source snapshot, commitment,
    target input, binary digests, and the root-digest projection instead.
    """
    admission = json.loads(admission_path.read_text())
    binding = json.loads(binding_path.read_text())
    prepared = json.loads(manifest_path.read_text())
    assert_rootless(admission, "worker admission")
    assert_rootless(binding, "public binding")
    if admission.get("schema") != WORKER_SCHEMA or admission.get("status") != "approved":
        raise ValueError("worker admission schema or status is invalid")
    if binding.get("schema") != PUBLIC_BINDING_SCHEMA:
        raise ValueError("public binding schema is invalid")
    decision_path = repo_path(admission.get("decision_path", ""))
    specification_path = repo_path(admission.get("specification_path", ""))
    if sha(decision_path) != admission.get("decision_sha256"):
        raise ValueError("Coordinator decision digest differs")
    if sha(specification_path) != admission.get("specification_sha256"):
        raise ValueError("frozen specification digest differs")
    import yaml
    plan_path = str(ROOT / "research/isogeny_relation_yield_scan_20261016/graph_plan_20261023")
    if plan_path not in sys.path:
        sys.path.insert(0, plan_path)
    from study_admission import validate_approval_fields
    decision, _, stage = validate_approval_fields(
        admission, yaml.safe_load(decision_path.read_text()),
        yaml.safe_load(specification_path.read_text()))
    if stage != admission.get("execution_stage"):
        raise ValueError("worker admission stage differs from Coordinator approval")
    if (prepared.get("schema") != "isogeny-relation-input/v1" or
            prepared.get("schedule_conformant") is not True or
            prepared.get("seed_mode") != "independent_verifier_root"):
        raise ValueError("prepared manifest is not a scientific scheduled input")
    for field, path in (("prepared_input_sha256", input_path),
                        ("prepared_manifest_sha256", manifest_path)):
        if binding.get(field) != sha(path):
            raise ValueError(f"public binding {field} differs")
    if prepared.get("input_sha256") != sha(input_path):
        raise ValueError("prepared input digest differs")
    if binding.get("target_count") != prepared.get("target_count"):
        raise ValueError("public binding target count differs")
    if prepared.get("stratum") not in ("P29", "P37"):
        raise ValueError("prepared stratum is not in the frozen study")
    if not isinstance(binding.get("arm_key"), str) or not binding["arm_key"]:
        raise ValueError("public binding arm key is missing")
    from materialize import SCHEDULE_DIR, load_schedule
    stage_name = {0: "discovery", 1: "confirmation", 2: "solve"}.get(
        admission.get("execution_stage"))
    if stage_name is None:
        raise ValueError("worker admission execution stage is invalid")
    _, row = load_schedule(binding["arm_key"], stage_name)
    scheduled = {"stratum": row["stratum"], "index": row.get("path_index"),
                 "arm": row["base_rule"], "target_count": row["target_count"]}
    actual = {key: prepared.get(key) for key in scheduled}
    if actual != scheduled:
        raise ValueError("prepared input does not match its frozen schedule arm")
    schedule_path = SCHEDULE_DIR / "discovery-arms.jsonl"
    if binding.get("schedule_sha256") != row.get("side_schedule_sha256", sha(schedule_path)):
        raise ValueError("public binding schedule digest differs")
    if binding.get("schedule_manifest_sha256") != row.get(
            "side_manifest_sha256", sha(SCHEDULE_DIR / "manifest.json")):
        raise ValueError("public binding schedule manifest digest differs")
    if prepared.get("graph_sha256") != stratum.get("graph_sha256"):
        raise ValueError("prepared graph digest differs from worker admission")
    prefix = repo_path(admission.get("output_prefix", ""))
    output = output_path.resolve()
    if prefix not in output.parents:
        raise ValueError("worker output is outside Coordinator-approved output prefix")
    if admission.get("source_commit"):
        from execute_graph_prepared import check_frozen_sources, source_paths
        sources = source_paths()
        check_frozen_sources(ROOT, sources.values(), admission["source_commit"])
        expected_sources = {path.resolve().relative_to(ROOT.resolve()).as_posix(): sha(path)
                            for path in sources.values()}
        if admission.get("source_sha256") != expected_sources:
            raise ValueError("worker admission source digest map differs")
    family = prepared["stratum"]
    roots = admission.get("root_digests", {})
    for name in ROOT_NAMES:
        key = name + "_root_sha256"
        digest = roots.get(key)
        if (not isinstance(digest, str) or len(digest) != 64 or
                prepared.get(key) != digest):
            raise ValueError(f"{family} prepared {name} root digest differs")
    stratum = admission.get("strata", {}).get(family, {})
    commitment_digest = stratum.get("commitment_sha256")
    if (not isinstance(commitment_digest, str) or len(commitment_digest) != 64 or
            any(ch not in "0123456789abcdef" for ch in commitment_digest)):
        raise ValueError("rootless worker admission commitment digest is invalid")
    if prepared.get("commitment_sha256") != commitment_digest:
        raise ValueError("prepared commitment digest differs")
    if sha(collector_path) != admission.get("binaries", {}).get("collector_sha256"):
        raise ValueError("collector binary digest differs from worker admission")
    if sha(count_verifier_path) != admission.get("binaries", {}).get("count_verifier_sha256"):
        raise ValueError("count verifier digest differs from worker admission")
    return {"experiment_id": admission["experiment_id"],
            "decision_id": admission["decision_id"],
            "execution_stage": admission["execution_stage"],
            "arm_key": binding["arm_key"],
            "binding_sha256": sha(binding_path),
            "input_sha256": sha(input_path),
            "manifest_sha256": sha(manifest_path),
            "commitment_sha256": commitment_digest,
            "collector_sha256": sha(collector_path),
            "count_verifier_sha256": sha(count_verifier_path),
            "output_prefix": admission["output_prefix"]}


def load_worker_catalog(catalog_path: Path, rows: list[dict],
                       experiment_id: str, execution_stage: int) -> tuple[Path, dict]:
    """Validate a custodian-built catalog before a plan embeds worker paths."""
    catalog_path = catalog_path.resolve()
    catalog = json.loads(catalog_path.read_text())
    assert_rootless(catalog, "prepared catalog")
    if (catalog.get("schema") != "ectd.graph-prepared-worker-catalog.v1" or
            catalog.get("experiment_id") != experiment_id or
            catalog.get("execution_stage") != execution_stage):
        raise ValueError("prepared worker catalog identity differs")
    admission_path = repo_path(catalog.get("worker_admission_path", ""))
    if (sha(admission_path) != catalog.get("worker_admission_sha256") or
            json.loads(admission_path.read_text()).get("schema") != WORKER_SCHEMA):
        raise ValueError("prepared worker admission digest or schema differs")
    entries = catalog.get("arms")
    if not isinstance(entries, dict) or set(entries) != {row["arm_key"] for row in rows}:
        raise ValueError("prepared catalog arm set differs from plan schedule")
    validated = {}
    for row in rows:
        key = row["arm_key"]
        item = entries[key]
        paths = {}
        for name, digest_key in (("input", "input_sha256"),
                                 ("manifest", "manifest_sha256"),
                                 ("binding", "binding_sha256")):
            path = repo_path(item.get(name + "_path", ""))
            if sha(path) != item.get(digest_key):
                raise ValueError(f"prepared catalog {key} {name} digest differs")
            paths[name] = path
        binding = json.loads(paths["binding"].read_text())
        if (binding.get("schema") != PUBLIC_BINDING_SCHEMA or
                binding.get("arm_key") != key or
                binding.get("prepared_input_sha256") != item["input_sha256"] or
                binding.get("prepared_manifest_sha256") != item["manifest_sha256"]):
            raise ValueError(f"prepared catalog {key} public binding differs")
        manifest = json.loads(paths["manifest"].read_text())
        if (manifest.get("input_sha256") != item["input_sha256"] or
                manifest.get("stratum") != row.get("stratum") or
                manifest.get("index") != row.get("path_index") or
                manifest.get("arm") != row.get("base_rule") or
                manifest.get("target_count") != row.get("target_count", row.get("discovery_targets"))):
            raise ValueError(f"prepared catalog {key} input is for a different arm")
        validated[key] = paths
    return admission_path, validated
