"""Source-bound finite YAML adapter, local execution_approval format 1.

DEC-20260909-8ccd1a authorizes this narrow timing/mirror correction under
the inherited DEC-20260909-7db063 engineering contract.
Only a published, parent-owned benign fixture can be admitted by this version.
Scientific activation and semantic review remain separate future authorities.
Importing this file imports standard-library code only; no scientific kernel.
"""
from __future__ import annotations

import argparse
import ctypes
import dataclasses
from datetime import datetime, timezone
import hashlib
import importlib.util
import importlib.metadata
import json
import math
import os
from pathlib import Path
import re
import resource
import select
import shlex
import shutil
import stat
import struct
import subprocess
import sys
import sysconfig
import tempfile
import time

_helper_path = Path(__file__).absolute().with_name("finite_yaml_process_v2.py")
_helper_spec = importlib.util.spec_from_file_location("_finite_yaml_process_v2", _helper_path)
_p = importlib.util.module_from_spec(_helper_spec)
sys.modules[_helper_spec.name] = _p
_helper_spec.loader.exec_module(_p)
FiniteYamlLockError = _p.AdmissionError
require = _p.require
REPO_ROOT = Path(__file__).absolute().parents[1]
AUTHORITY_PATH = "coordination/pending-ideas/BATCH-e9d1c7/timing-correction/qa-admission/fixture-authority.json"
REPAIR_PATH = "coordination/pending-ideas/BATCH-e9d1c7/repair/repair-disposition.json"
REPAIR_SHA = "574b4c5fc848d44843cdcdfc53b02a8ad5714dbb83155eb72e66fbee4fa6fbae"
METRIC_PATH = "ledger/decisions/DEC-20260908-195f0f.yaml"
METRIC_SHA = "887329e20719824c7b8dba659c532892933a32c1fde9f9d9610aa9cdff3eb455"
FIXED_WORKER = "tests/fixtures/finite_yaml_locked_v3/worker.py"
SYSTEM_GIT = "/usr/bin/git"
_issued = {}


def utc():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def timestamp(value, predicate):
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        require(parsed.tzinfo is not None, predicate, "timezone required")
        return parsed.astimezone(timezone.utc)
    except (TypeError, AttributeError, ValueError) as exc:
        raise FiniteYamlLockError(predicate, exc) from exc


def exact(value, expected, predicate):
    # Canonical bytes distinguish True from 1 and forbid nonfinite values.
    require(_p.canonical(value) == _p.canonical(expected), predicate, "does not match frozen value")


def check_configuration(experiment_id, run_id, configuration):
    matches = [r for r in CONFIGURATIONS if r["experiment_id"] == experiment_id and r["run_id"] == run_id]
    require(len(matches) == 1, "configuration_membership", "unknown or cross-experiment reservation")
    exact(configuration, matches[0]["configuration"], "configuration_membership")
    return matches[0]


def validate_recovery_case_inventory(cases):
    ids = [r["id"] for r in RECOVERY_CASES]
    expected = ids if isinstance(cases, list) and all(isinstance(x, str) for x in cases) else RECOVERY_CASES
    exact(cases, expected, "recovery_case_inventory")


def validate_recovery_case_arms(arm_b, arm_i):
    validate_recovery_case_inventory(arm_b)
    validate_recovery_case_inventory(arm_i)
    exact(arm_b, arm_i, "recovery_arm_inventory")


def read_approval(raw):
    """Strict YAML with duplicate-key, alias and nonfinite rejection."""
    # JSON is the normal generated fixture form; YAML is the retained v1 API.
    try:
        return _p.strict_json(raw)
    except FiniteYamlLockError as exc:
        if exc.predicate != "json_syntax":
            raise
    import yaml
    class Loader(yaml.SafeLoader):
        def compose_node(self, parent, index):
            require(not self.check_event(yaml.AliasEvent), "yaml_alias", "aliases are not launch data")
            return super().compose_node(parent, index)
    def mapping(loader, node):
        value = {}
        for k, v in node.value:
            key = loader.construct_object(k, deep=True)
            require(type(key) is str and key not in value, "duplicate_keys", str(key))
            value[key] = loader.construct_object(v, deep=True)
        return value
    Loader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, mapping)
    try:
        value = yaml.load(raw, Loader=Loader)
        _p.canonical(value)
        return value
    except (yaml.YAMLError, ValueError, TypeError) as exc:
        if isinstance(exc, FiniteYamlLockError):
            raise
        raise FiniteYamlLockError("yaml_syntax_or_nonfinite", exc) from exc


def schema_validate(value, root, name):
    import jsonschema
    schema = _p.strict_json(_p.read_regular(root / "schemas" / name)[0])
    try:
        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.Draft202012Validator(schema).validate(value)
    except jsonschema.exceptions.SchemaError as exc:
        raise FiniteYamlLockError("schema_definition", exc.message) from exc
    except jsonschema.exceptions.ValidationError as exc:
        raise FiniteYamlLockError("schema_instance", str(list(exc.absolute_path)) + ": " + exc.message) from exc


def source_file(root, relative, expected, bindings):
    _p.relative_name(relative)
    path = root / relative
    record, raw = _p.bind_file(path, expected)
    previous = bindings.get(str(path))
    require(previous is None or previous == record, "source_binding_conflict", relative)
    for old in bindings.values():
        require(old["path"] == str(path) or old["identity"][:2] != record["identity"][:2],
                "duplicate_file_identity", relative)
    bindings[str(path)] = record
    return raw


def tool_environment():
    # Bootstrap context is fixed, not selected by the capsule or inherited credentials.
    return {"PATH": "/usr/bin:/bin", "LC_ALL": "C"}


def published_authority(reference, bindings):
    required = {"authority_repository", "authority_path", "authority_sha256", "publication_commit",
                "publication_ref", "case_id", "git"}
    require(type(reference) is dict and set(reference) == required,
            "authority_reference_shape", "exact reference fields required")
    require(reference["authority_path"] == AUTHORITY_PATH, "authority_namespace", "wrong authority namespace")
    repository = Path(reference["authority_repository"])
    allowed = [p for p in (REPO_ROOT, *REPO_ROOT.parents) if (p / ".git").exists()]
    require(repository in allowed and str(repository) == os.path.normpath(str(repository)),
            "authority_repository", "authority must belong to the source checkout or enclosing parent checkout")
    # Never execute a caller-selected binary. /usr/bin/git belongs to the trusted
    # parent/OS bootstrap; its independently published pin is compared here.
    require(type(reference["git"]) is dict and set(reference["git"]) == {"path", "sha256"}
            and reference["git"]["path"] == SYSTEM_GIT, "bootstrap_git_path", "fixed system Git required")
    pin, _ = _p.bind_file(SYSTEM_GIT, reference["git"]["sha256"])
    bindings[pin["path"]] = pin
    env = tool_environment()
    branch = _p.git(repository, reference["git"], ["symbolic-ref", "--short", "HEAD"], env).decode().strip()
    require(reference["publication_ref"] == "refs/remotes/origin/" + branch,
            "authority_publication_ref", "must be the checkout's origin branch")
    commit = reference["publication_commit"]
    require(type(commit) is str and re.fullmatch("[0-9a-f]{40}", commit), "authority_commit", "full commit required")
    _p.git(repository, reference["git"], ["merge-base", "--is-ancestor", commit, reference["publication_ref"]], env)
    raw = source_file(repository, AUTHORITY_PATH, reference["authority_sha256"], bindings)
    blob = _p.git(repository, reference["git"], ["show", commit + ":" + AUTHORITY_PATH], env)
    require(blob == raw, "authority_published_blob", "current authority differs from published bytes")
    doc = _p.strict_json(raw)
    require(doc.get("schema") == "crypto.autoresearch.finite_yaml_fixture_authority.v1"
            and doc.get("approved_by") == "coordinator"
            and doc.get("decision_id") == "DEC-20260909-8ccd1a"
            and doc.get("prior_decision_id") == "DEC-20260909-7db063"
            and doc.get("scientific_execution_authorized") is False,
            "authority_record", "wrong authority kind/scope")
    require(_p.digest(source_file(repository, REPAIR_PATH, REPAIR_SHA, bindings)) == REPAIR_SHA,
            "repair_authority", "repair bytes must match")
    for name, expected in ((CORRECTION_PATH, CORRECTION_SHA), (CORRECTION_DECISION_PATH, CORRECTION_DECISION_SHA)):
        correction_raw = source_file(repository, name, expected, bindings)
        correction_blob = _p.git(repository, reference["git"], ["show", commit + ":" + name], env)
        require(correction_blob == correction_raw, "correction_published_blob", name)
    excluded = doc.get("excluded_session_ids")
    require(type(excluded) is list and all(type(x) is str for x in excluded)
            and set(REQUIRED_EXCLUDED_SESSIONS) <= set(excluded),
            "qa_excluded_session_binding", "parent must bind actual planner and producer identities")
    cases = doc.get("cases")
    require(type(cases) is list, "authority_cases", "case list required")
    matches = [c for c in cases if c.get("case_id") == reference["case_id"]]
    require(len(matches) == 1, "authority_case_membership", "exactly one selected case")
    return repository, doc, matches[0]


def validate_native(native, claim, expected, excluded_sessions=()):
    require("bedrock" not in _p.canonical(native).decode().lower(), "prohibited_native_provider", "prohibited metadata")
    for field in ("thread_id", "turn_id", "parent_thread_id", "requested_policy", "requested_model_id",
                  "configured_model_id", "requested_reasoning_effort", "configured_reasoning_effort",
                  "provider", "resolved_model_id", "served_reasoning_effort", "model_verified",
                  "adapter_probe_performed", "fallback_allowed", "fallback_used", "degraded_allowed",
                  "degraded_requirements", "metadata_source"):
        require(field in native, "native_required_field", field)
    exact(native, expected, "native_receipt_content")
    require(native["thread_id"] not in excluded_sessions,
            "native_copied_producer", "actual producer/planner session excluded by published authority")
    require(native["requested_reasoning_effort"] == native["configured_reasoning_effort"] == "ultra",
            "native_reasoning_effort", "literal ultra required")
    require(native["thread_id"] != native["parent_thread_id"] and native["parent_thread_id"] == claim["session"],
            "native_claim_session", "claim parent and actual child must remain distinct")
    require(native["thread_id"] not in ("01a08403-33a5-7672-9ddc-3d3b48b22a0d",
                                       "01a08463-f2ad-7f61-8cca-a92c74f283a5"),
            "native_copied_producer", "QA must have a fresh session")
    require(all(native[k] is False for k in ("fallback_allowed", "fallback_used", "degraded_allowed"))
            and native["degraded_requirements"] == [], "native_fallback_degradation", "no fallback or degradation")
    if native["model_verified"] is True:
        require(native["adapter_probe_performed"] is True and type(native.get("probe_ref")) is dict
                and all(native[k] for k in ("provider", "resolved_model_id", "served_reasoning_effort")),
                "native_probe", "verification requires real bound serving probe")
    else:
        require(native["model_verified"] is False and native["adapter_probe_performed"] is False
                and all(native[k] is None for k in ("provider", "resolved_model_id", "served_reasoning_effort")),
                "native_unprobed_fields", "unexposed serving fields must remain null")


def validate_claim(repository, authority, case, bindings):
    ref = authority["claim"]
    claim = _p.strict_json(source_file(repository, ref["path"], ref["sha256"], bindings))
    exact(claim, ref["record"], "claim_content")
    for key in ("task_id", "owner", "epoch", "branch", "session", "acquired_at", "expires_at"):
        exact(claim.get(key), case["claim"].get(key), "claim_" + key)
    _p.exact_integer(claim["epoch"], "claim_epoch", 1)
    now = datetime.now(timezone.utc)
    acquired = timestamp(claim["acquired_at"], "claim_acquired_at")
    expires = timestamp(claim["expires_at"], "claim_expires_at")
    require(acquired <= now < expires and acquired < expires, "claim_current", "claim is future-acquired or expired")
    require(claim["task_id"] == "TASK-20260909-3d02f7", "claim_task", "only the frozen QA task is admitted")
    claim_dir = repository / Path(ref["path"]).parent
    pin = {"path": SYSTEM_GIT, "sha256": authority["tools"]["git"]["sha256"]}
    branch = _p.git(repository, pin, ["symbolic-ref", "--short", "HEAD"], tool_environment()).decode().strip()
    require(claim["branch"] == branch and claim["worktree"] == str(repository), "claim_branch_worktree", "current owner checkout mismatch")
    # Canonical claims live on ordinary branches. Match goal_lanes._scan_refs:
    # inspect every immutable addition across all refs, not an invented refs/claims namespace.
    prefix = claim["task_id"] + "."
    history = _p.git(repository, pin,
        ["log", "--all", "--diff-filter=A", "--format=%H", "--name-only", "--",
         ":(glob)**/" + prefix + "*.claim.json", ":(glob)**/" + prefix + "*.release.json"],
        tool_environment()).decode().splitlines()
    found, commit = {}, None
    for line in history:
        if re.fullmatch("[0-9a-f]{40}", line):
            commit = line
        elif line and commit:
            found.setdefault(line, commit)
    observations = []
    def check_record(name, record):
        require(record.get("task_id") == claim["task_id"], "claim_task", name)
        _p.exact_integer(record.get("epoch"), "claim_epoch", 1)
        if name.endswith(".release.json"):
            require(record["epoch"] < claim["epoch"], "claim_release", name)
        else:
            require(record["epoch"] <= claim["epoch"], "claim_newer_epoch", name)
            if record["epoch"] == claim["epoch"]:
                exact(record, claim, "claim_overlay_content")
    for name, added_commit in sorted(found.items()):
        raw = _p.git(repository, pin, ["show", added_commit + ":" + name], tool_environment())
        check_record(name, _p.strict_json(raw))
        observations.append({"path": name, "added_commit": added_commit, "sha256": _p.digest(raw)})
    observed_live = []
    for path in sorted(claim_dir.glob(prefix + "*")):
        record = _p.strict_json(_p.read_regular(path)[0])
        check_record(path.name, record)
        if path.name.endswith(".claim.json"):
            observed_live.append(record)
    require(claim in observed_live, "claim_file", "current canonical claim absent")
    require(_p.digest(_p.canonical(observations)) == authority["claim_overlay_sha256"],
            "claim_overlay_digest", "published canonical claim inventory changed")
    require(case["run_id"] in authority["owned_run_ids"], "claim_run_membership", "run not owned by fixture authority")
    native_ref = authority["native_receipt"]
    native = _p.strict_json(source_file(repository, native_ref["path"], native_ref["sha256"], bindings))
    validate_native(native, claim, native_ref["record"], authority["excluded_session_ids"])
    if native.get("probe_ref"):
        probe = native["probe_ref"]
        evidence = _p.strict_json(source_file(repository, probe["path"], probe["sha256"], bindings))
        require(evidence.get("success") is True and evidence.get("thread_id") == native["thread_id"]
                and evidence.get("provider") == native["provider"]
                and evidence.get("resolved_model_id") == native["resolved_model_id"]
                and evidence.get("served_reasoning_effort") == native["served_reasoning_effort"],
                "native_probe_content", "probe must attest the exact runtime binding")
    return claim, native


def loaded_images():
    """Actual loaded-library identity; macOS shared-cache images use LC_UUID.

    The Mach-O header/load-command digest and UUID identify the mapped image;
    they are not falsely labeled a hash of inaccessible shared-cache file bytes.
    """
    if sys.platform == "darwin":
        dyld = ctypes.CDLL(None)
        dyld._dyld_image_count.restype = ctypes.c_uint32
        dyld._dyld_get_image_name.argtypes = [ctypes.c_uint32]
        dyld._dyld_get_image_name.restype = ctypes.c_char_p
        dyld._dyld_get_image_header.argtypes = [ctypes.c_uint32]
        dyld._dyld_get_image_header.restype = ctypes.c_void_p
        rows = []
        for i in range(dyld._dyld_image_count()):
            pointer = dyld._dyld_get_image_header(i)
            header = ctypes.string_at(pointer, 32)
            magic, _, _, _, ncmds, size, _, _ = struct.unpack("<8I", header)
            require(magic == 0xFEEDFACF and size < 16 * 1024 * 1024 and ncmds < 100000,
                    "loaded_library_header", "unsupported mapped image header")
            commands = ctypes.string_at(pointer + 32, size)
            offset, uuid = 0, None
            for _ in range(ncmds):
                require(offset + 8 <= size, "loaded_library_commands", "truncated")
                cmd, count = struct.unpack_from("<II", commands, offset)
                require(count >= 8 and offset + count <= size, "loaded_library_commands", "invalid command size")
                if cmd == 0x1B:
                    uuid = commands[offset + 8:offset + 24].hex()
                offset += count
            require(uuid is not None, "loaded_library_uuid", "no UUID")
            rows.append({"image": dyld._dyld_get_image_name(i).decode(), "kind": "mapped_macho_uuid_and_load_commands",
                         "uuid": uuid, "load_commands_sha256": _p.digest(commands)})
        return sorted(rows, key=lambda r: r["image"])
    if sys.platform.startswith("linux"):
        paths = set()
        for line in Path("/proc/self/maps").read_text().splitlines():
            pieces = line.split(None, 5)
            if len(pieces) == 6 and pieces[5].startswith("/") and "x" in pieces[1]:
                paths.add(pieces[5])
        return [{"image": p, "kind": "mapped_file_sha256", "sha256": _p.digest(Path(p).read_bytes())}
                for p in sorted(paths)]
    raise FiniteYamlLockError("loaded_library_host", "no implemented library identity observation")


def _bind_dependency_files(closure, bindings):
    require(type(closure) is dict and set(closure) == {"python", "stdlib", "distributions", "loaded_images", "module_origins"},
            "dependency_closure_shape", "complete dependency closure required")
    python = closure["python"]
    executable = str(Path(sys.executable).resolve())
    require(python["executable"] == executable and python["version"] == sys.version,
            "python_identity", "actual executable/version mismatch")
    bound, _ = _p.bind_file(executable, python["sha256"])
    bindings[executable] = bound
    stdlib = closure["stdlib"]
    require(stdlib["root"] == str(Path(sysconfig.get_path("stdlib")).resolve()),
            "stdlib_root", "wrong Python standard library")
    actual = []
    for base, dirs, names in os.walk(stdlib["root"], followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in ("site-packages", "dist-packages", "__pycache__"))
        for name in sorted(names):
            path = Path(base) / name
            if name.endswith((".py", ".so", ".dylib", ".zip")):
                require(not path.is_symlink(), "stdlib_alias", path)
                actual.append(str(path))
    require(sorted(actual) == sorted(r["path"] for r in stdlib["files"]),
            "stdlib_complete_membership", "missing/extra standard-library or extension file")
    for ref in stdlib["files"]:
        binding, _ = _p.bind_file(ref["path"], ref["sha256"])
        bindings[ref["path"]] = binding
    dist_rows = closure["distributions"]
    require(type(dist_rows) is list and len({d["name"].lower() for d in dist_rows}) == len(dist_rows),
            "dependency_distributions", "unique distributions required")
    names = {d["name"].lower().replace("_", "-") for d in dist_rows}
    require({"pyyaml", "jsonschema", "attrs", "jsonschema-specifications", "referencing", "rpds-py"} <= names,
            "dependency_distribution_membership", "complete PyYAML/JSON Schema dependency set required")
    for row in dist_rows:
        distribution = importlib.metadata.distribution(row["name"])
        require(distribution.version == row["version"], "dependency_version", row["name"])
        installed = sorted(str(Path(distribution.locate_file(f)).resolve()) for f in distribution.files or []
                           if not str(f).endswith(".pyc") and Path(distribution.locate_file(f)).is_file())
        require(installed == sorted(r["path"] for r in row["files"]),
                "dependency_complete_membership", row["name"])
        for ref in row["files"]:
            binding, _ = _p.bind_file(ref["path"], ref["sha256"])
            bindings[ref["path"]] = binding


def validate_dependency_closure(closure, bindings, *, child=False):
    _bind_dependency_files(closure, bindings)
    # Children use -I -S and do not load site-packages. Parent origin checking
    # additionally covers the actual loaded PyYAML/JSON Schema dependency modules.
    if not child:
        import yaml
        import jsonschema
        _p.load_core(REPO_ROOT)
    expected_origins = closure["module_origins"]["child" if child else "outer"]
    actual_origins = {name: str(Path(m.__file__).resolve()) for name, m in sys.modules.copy().items()
                      if getattr(m, "__file__", None) and not str(m.__file__).startswith("<")}
    require(actual_origins == expected_origins, "module_origins", "unbound or shadowed imported module")
    require(all(path in bindings for path in actual_origins.values()),
            "module_origin_closure", "every imported file must be bound")
    exact(loaded_images(), closure["loaded_images"]["child" if child else "outer"], "loaded_library_identity")


@dataclasses.dataclass(frozen=True, slots=True)
class VerifiedLaunch:
    lock_path: str
    expected_sha256: str
    run_id: str
    authority_json: str
    snapshot_json: str


def _admit(lock_path, expected_sha256, run_id, reference, *, child_approval=None, output_identity=None, mirror_baseline=None):
    require(type(expected_sha256) is str and re.fullmatch("[0-9a-f]{64}", expected_sha256),
            "external_hash_format", "published SHA256 required")
    require("bedrock" not in _p.canonical(reference).decode().lower(), "prohibited_caller_provider", "prohibited metadata")
    bindings = {}
    repository, authority, case = published_authority(reference, bindings)
    root = Path(case["fixture_root"])
    require(root == REPO_ROOT and root.is_relative_to(repository / "coordination/pending-ideas/BATCH-e9d1c7/timing-correction/qa/scratch"),
            "fixture_root", "only the parent-created QA copy can run")
    require(case["run_id"] == run_id, "authority_run", "selected run mismatch")
    lock_path = Path(lock_path)
    require(lock_path == root / _p.relative_name(case["lock"]["path"]), "lock_path", "wrong lock path")
    require(expected_sha256 == case["lock"]["sha256"], "external_lock_hash", "caller differs from published lock digest")
    raw = source_file(root, case["lock"]["path"], expected_sha256, bindings)
    # Read the JSON sidecar and bind all runtime source and dependency bytes
    # before importing PyYAML/JSON Schema or the core monitor.
    early_plan_raw = source_file(root, case["plan"]["path"], case["plan"]["sha256"], bindings)
    early_plan = _p.strict_json(early_plan_raw)["execution_plan"]
    early_paths = [r["path"] for r in early_plan["source_closure"]]
    early_required = set(MANDATORY + EXPERIMENT_FILES[case["experiment_id"]] + TEST_FILES + [REPAIR_PATH])
    require(len(set(early_paths)) == len(early_paths) and early_required <= set(early_paths),
            "source_closure_membership", sorted(early_required - set(early_paths)))
    for entry in early_plan["source_closure"]:
        if entry["path"] in ORIGINAL_SOURCE_PINS:
            require(entry["sha256"] == ORIGINAL_SOURCE_PINS[entry["path"]], "original_source_pin", entry["path"])
        source_file(root, entry["path"], entry["sha256"], bindings)
    _bind_dependency_files(early_plan["dependency_closure"], bindings)
    approval_doc = child_approval if child_approval is not None else read_approval(raw)
    require(_p.digest(_p.canonical(approval_doc)) == case["approval_document_sha256"],
            "approval_document_binding", "parsed v1 document not bound by parent")
    require(type(approval_doc) is dict and set(approval_doc) == {"execution_approval"},
            "approval_envelope", "execution_approval required")
    approval = approval_doc["execution_approval"]
    _p.exact_integer(approval.get("format_version"), "format_version", 1)
    require(approval["format_version"] == 1 and approval.get("allowed_verifier_transitions") == [],
            "approval_version_or_transition", "format 1 without predecessor transitions required")
    plan_raw = source_file(root, case["plan"]["path"], case["plan"]["sha256"], bindings)
    require(_p.digest(plan_raw) == approval["execution_plan_sha256"], "execution_plan_hash", "sidecar digest mismatch")
    plan_doc = _p.strict_json(plan_raw)
    require(type(plan_doc) is dict and set(plan_doc) == {"execution_plan"}, "plan_envelope", "execution_plan required")
    plan = plan_doc["execution_plan"]
    require(plan["scientific_execution_authorized"] is False, "scientific_authority", "engineering version refuses scientific activation")
    require(approval["experiment_id"] == plan["experiment_id"] == case["experiment_id"], "experiment_binding", "wrong experiment")
    expected_rows = [r for r in CONFIGURATIONS if r["experiment_id"] == plan["experiment_id"]]
    require([r["run_id"] for r in plan["runs"]] == [r["run_id"] for r in expected_rows],
            "plan_run_inventory", "complete ordered two/five reservation list required")
    for row in plan["runs"]:
        mapping = check_configuration(plan["experiment_id"], row["run_id"], row["configuration"])
        require(row["run_directory"] == mapping["run_directory"], "reserved_directory", "reservation mapping changed")
        require(row["role"] == "generator" and type(row["seed"]) is int and row["seed"] == 0,
                "run_role_seed", "fixed generator and deterministic seed required")
        exact(row["output_allowlist"], PROFILES[plan["experiment_id"]]["complete_names"], "output_allowlist")
        for name in row["output_allowlist"]:
            _p.relative_name(name, leaf=True)
    row = next(r for r in plan["runs"] if r["run_id"] == run_id)
    require(_p.digest(_p.canonical(row)) == case["run_object_sha256"], "run_object_binding", "published selected row mismatch")
    mapping = check_configuration(plan["experiment_id"], run_id, row["configuration"])
    exact(plan["specification"], mapping["specification"], "specification_membership")
    spec_raw = source_file(root, mapping["specification"]["path"], approval["specification_sha256"], bindings)
    require(_p.digest(spec_raw) == mapping["specification"]["sha256"], "specification_hash", "raw original specification mismatch")
    if plan["experiment_id"] == "EXP-ECDLP-abf981":
        constants = _p.strict_json(spec_raw)["experiment"]["inputs"]["constants"]
        actual_constants = next(c for c in constants if c["cell"] == row["configuration"]["cell"])
        exact(actual_constants, mapping["constants"], "model_constants")
        require(plan["metric_interpretation_ref"] is None, "metric_decision", "models has no incidence decision")
    else:
        exact(plan["metric_interpretation_ref"], {"id": "DEC-20260908-195f0f", "path": METRIC_PATH, "sha256": METRIC_SHA}, "metric_decision")
        source_file(root, METRIC_PATH, METRIC_SHA, bindings)
    claim, native = validate_claim(repository, authority, case, bindings)
    fixture = plan["fixture_authorization"]
    exact(fixture, case["fixture_authorization"], "fixture_authorization")
    require(fixture["case_id"] == case["case_id"], "fixture_case_id", "fixture belongs to another case")
    mirror_result = inspect_authority_mirrors(repository, authority, fixture, bindings, mirror_baseline)
    require_mirror_checks(mirror_result)
    mirror_bindings = mirror_result["bindings"]
    bindings.update({value["path"]: value for value in mirror_bindings.values()})
    require(fixture["scientific_execution_authorized"] is False and fixture["worker"]["path"] == FIXED_WORKER,
            "fixed_benign_worker", "only the fixed benign sentinel is permitted")
    output = _p.relative_name(fixture["output_directory"])
    require(output.startswith("fixture-outputs/"), "fixture_output_namespace", "output must be inside the disposable fixture checkout")
    require(not output.startswith("experiments/") and fixture["simulated_reservation"] == mapping["run_directory"],
            "fixture_reservation_alias", "real RUN path cannot be used")
    run_dir = root / output
    parent_fd = _p.open_directory(run_dir.parent)
    parent_identity = list(_p.file_identity(os.fstat(parent_fd)))
    os.close(parent_fd)
    if output_identity is None:
        require(not os.path.lexists(run_dir), "output_existing", run_dir)
    else:
        fd = _p.open_directory(run_dir)
        try:
            require(list(_p.file_identity(os.fstat(fd)))[:2] == output_identity[:2], "output_directory_identity", run_dir)
        finally:
            os.close(fd)
    source_rows = plan["source_closure"]
    paths = [r["path"] for r in source_rows]
    mandatory = set(MANDATORY + EXPERIMENT_FILES[plan["experiment_id"]] + TEST_FILES + [REPAIR_PATH])
    require(len(paths) == len(set(paths)) and mandatory <= set(paths), "source_closure_membership", sorted(mandatory - set(paths)))
    for source in source_rows:
        source_file(root, source["path"], source["sha256"], bindings)
    require(len({x["path"] for x in approval["protocol_hashes"]}) == len(approval["protocol_hashes"]), "protocol_hash_duplicate", "duplicate protocol path")
    for source in approval["protocol_hashes"]:
        source_file(root, source["path"], source["sha256"], bindings)
    require(set(paths) <= {p["path"] for p in approval["protocol_hashes"]}, "protocol_closure_membership", "protocol hashes omit source closure")
    source_file(root, FIXED_WORKER, fixture["worker"]["sha256"], bindings)
    source_file(root, fixture["worker_input"]["path"], fixture["worker_input"]["sha256"], bindings)
    environment = plan["environment_policy"]
    for values in (environment["outer"], environment["inner"]):
        require(type(values) is dict and all(type(k) is str and type(v) is str for k, v in values.items()),
                "environment_allowlist", "exact string dictionary required")
        require(not any(k.startswith(("PYTHON", "LD_", "DYLD_")) or any(token in k.upper() for token in ("TOKEN", "SECRET", "PASSWORD", "API_KEY")) for k in values),
                "environment_injection", "loader/startup/credential variables are not allowed")
    exact(dict(os.environ), environment["inner" if child_approval is not None else "outer"], "actual_environment")
    for key in environment["absent_test_keys"]:
        require(key not in environment["inner"], "environment_absence", key)
    tools = authority["tools"]
    require(tools["git"]["path"] == SYSTEM_GIT, "git_tool_path", "system Git pin required")
    for name in ("git", "ps"):
        require(str(Path(shutil.which(name, path=environment["outer"]["PATH"]) or "").resolve()) == tools[name]["path"],
                "outer_tool_path", name)
        bound, _ = _p.bind_file(tools[name]["path"], tools[name]["sha256"])
        bindings[bound["path"]] = bound
    dependency = plan["dependency_closure"]
    require(approval["python"] == dependency["python"], "python_approval", "executable pins differ")
    require(row["argv"] == [approval["python"]["executable"], "-I", "-S", "-B", str(root / mapping["source_entry"]), "--launch-context-fd", "{launch_context_fd}"],
            "argv_binding", "only the fixed isolated entry and dedicated descriptor are allowed")
    if child_approval is None:
        schema_validate(approval_doc, root, "finite-yaml-execution-approval-v1.schema.json")
        schema_validate(plan_doc, root, "finite-yaml-execution-plan-v1.schema.json")
    validate_dependency_closure(dependency, bindings, child=child_approval is not None)
    policy = plan["resource_policy"]
    _p.exact_integer(policy["maximum_workers"], "maximum_workers", 1)
    _p.exact_integer(policy["descendant_slots"], "descendant_slots")
    require(policy["maximum_workers"] == 1 and policy["descendant_slots"] == 0,
            "worker_policy", "one worker and no descendants")
    _p.positive_number(policy["timeout_seconds"], "watchdog")
    _p.exact_integer(policy["memory_bytes"], "memory_bytes", 1)
    if policy["cpu_seconds"] is not None:
        _p.positive_number(policy["cpu_seconds"], "cpu_limit")
        require(fixture["case_id"] == "synthetic-cpu-limit", "cpu_control_scope", "finite CPU cap requires a named approved control")
    _p.host_supported()
    require(policy["effective_uid"] == os.geteuid() and type(policy["effective_uid"]) is int,
            "effective_uid", "wrong host UID")
    exact(approval["resource_policy"], {k: policy[k] for k in ("descendant_policy", "effective_uid")}, "resource_policy_binding")
    require(plan["source_snapshot"] == authority["source_snapshot"] and approval["approved_base_commit"] == authority["approved_base_commit"],
            "source_commit_binding", "source/approval commit mismatch")
    for source in source_rows:
        if source["path"] in mandatory:
            blob = _p.git(root, tools["git"], ["show", plan["source_snapshot"] + ":" + source["path"]], environment["outer"])
            require(_p.digest(blob) == source["sha256"], "source_snapshot_blob", source["path"])
    launch_commit = _p.git(root, tools["git"], ["rev-parse", "HEAD"], environment["outer"]).decode().strip()
    require(launch_commit == case["fixture_commit"], "launch_commit", "actual clean fixture commit differs")
    _p.git(root, tools["git"], ["merge-base", "--is-ancestor", plan["source_snapshot"], launch_commit], environment["outer"])
    require(_p.tree_clean(root, tools["git"], environment["outer"], output if output_identity is not None else None),
            "clean_tree", "fixture tree must be clean apart from its one actual output directory")
    return {"root": str(root), "authority_repository": str(repository), "authority": authority,
            "case": case, "approval_document": approval_doc, "plan": plan, "row": row,
            "claim": claim, "native": native, "bindings": bindings, "mirror_bindings": mirror_bindings,
            "mirror_checks": mirror_result["checks"], "run_directory": str(run_dir),
            "parent_identity": parent_identity, "launch_commit": launch_commit,
            "lock_path": str(lock_path), "lock_sha256": expected_sha256, "reference": reference}


def validate_lock(lock_path, expected_sha256, run_id, launch_authority):
    snapshot = _admit(lock_path, expected_sha256, run_id, launch_authority)
    token = VerifiedLaunch(str(lock_path), expected_sha256, run_id,
                           _p.canonical(launch_authority).decode(), _p.canonical(snapshot).decode())
    _issued[id(token)] = token.snapshot_json
    return token


def _postflight(snapshot, child, output):
    bindings = snapshot["bindings"]
    root = Path(snapshot["root"])
    authority = snapshot["authority"]
    plan, approval = snapshot["plan"], snapshot["approval_document"]["execution_approval"]
    def intact(path):
        return path in bindings and _p.unchanged(bindings[path])
    def git_check(arguments, expected):
        try:
            return _p.git(root, authority["tools"]["git"], arguments, plan["environment_policy"]["outer"]).decode().strip() == expected
        except (OSError, ValueError):
            return False
    try:
        clean = _p.tree_clean(root, authority["tools"]["git"], plan["environment_policy"]["outer"],
                              plan["fixture_authorization"]["output_directory"])
    except (OSError, ValueError):
        clean = False
    checks = {"process_group_quiescent": child.group_quiescent is True,
              "commit_unchanged": git_check(["rev-parse", "HEAD"], snapshot["launch_commit"]),
              "tree_unchanged": clean,
              "approval_lock_unchanged": intact(snapshot["lock_path"]),
              "specification_unchanged": intact(str(root / plan["specification"]["path"])),
              "execution_plan_unchanged": intact(str(root / snapshot["case"]["plan"]["path"])),
              "protocol_hashes_unchanged": all(intact(str(root / x["path"])) for x in approval["protocol_hashes"])}
    additional = {"external_authority_unchanged": intact(str(Path(snapshot["authority_repository"]) / AUTHORITY_PATH)),
                  "native_receipt_unchanged": intact(str(Path(snapshot["authority_repository"]) / authority["native_receipt"]["path"])),
                  "schema_unchanged": all(intact(str(root / "schemas" / name)) for name in
                     ("finite-yaml-execution-approval-v1.schema.json", "finite-yaml-execution-plan-v1.schema.json", "run-manifest.schema.json")),
                  "executable_and_dependencies_unchanged": all(_p.unchanged(value) for key, value in bindings.items()
                      if not Path(key).is_relative_to(root) and not Path(key).is_relative_to(snapshot["authority_repository"])),
                  "all_bound_file_identities_unchanged": all(_p.unchanged(value) for value in bindings.values()),
                  "exact_output_membership": not output["missing"] and not output["extra"],
                  "nonalias_regular_files": not output["aliases"],
                  "all_artifact_hashes_verified": not output["aliases"]}
    try:
        claim, native = validate_claim(Path(snapshot["authority_repository"]), authority, snapshot["case"], {})
        additional["claim_current_and_unchanged"] = claim == snapshot["claim"] and native == snapshot["native"]
    except (OSError, ValueError, KeyError):
        additional["claim_current_and_unchanged"] = False
    # Original claim/native predicates above remain independently visible.
    mirror_result = inspect_authority_mirrors(Path(snapshot["authority_repository"]), authority,
        plan["fixture_authorization"], dict(bindings), snapshot["mirror_bindings"])
    additional.update(mirror_result["checks"])
    return checks, additional


def validate_final_timing(measurement, pre_raw, endpoint):
    """Pure predicate; no supplied value is represented as a measurement here.

    Only measure_final_wrapper observes clocks/RSS. Callers testing this
    predicate must label their numbers metadata, not process observations.
    """
    fields = {"wall_seconds", "cpu_seconds", "peak_rss_bytes", "boundary"}
    reasons = []
    if type(measurement) is not dict or set(measurement) != fields:
        reasons.append("final wrapper measurement requires exactly wall_seconds, cpu_seconds, peak_rss_bytes and boundary")
    if type(pre_raw) is not dict or set(pre_raw) != fields:
        reasons.append("pre-raw sample is missing or has an invalid shape")
    if endpoint != FINAL_MEASUREMENT_ENDPOINT:
        reasons.append("final measurement endpoint is not after final raw/core hashing")
    def sample_shape(value, boundary, label):
        if type(value) is not dict or set(value) != fields:
            return False
        valid = True
        for name in ("wall_seconds", "cpu_seconds"):
            number = value[name]
            if type(number) not in (int, float) or not math.isfinite(number) or number < 0:
                reasons.append(f"{label}.{name} must be finite and nonnegative, with bool refused")
                valid = False
        if type(value["peak_rss_bytes"]) is not int or value["peak_rss_bytes"] < 0:
            reasons.append(f"{label}.peak_rss_bytes must be a nonnegative integer, with bool refused")
            valid = False
        if value["boundary"] != boundary:
            reasons.append(f"{label}.boundary does not match its declared endpoint")
            valid = False
        return valid
    final_ok = sample_shape(measurement, FINAL_TIMING_BOUNDARY, "final")
    preliminary_ok = sample_shape(pre_raw, PRE_RAW_BOUNDARY, "pre_raw")
    if final_ok and preliminary_ok:
        for name in ("wall_seconds", "cpu_seconds", "peak_rss_bytes"):
            if measurement[name] < pre_raw[name]:
                reasons.append(f"final.{name} is below the corresponding pre-raw observation")
    return {"complete": not reasons, "reason": "; ".join(reasons) or None,
            "diagnostic": None if not reasons else {
                "final_safe_repr": repr(measurement), "pre_raw_safe_repr": repr(pre_raw),
                "endpoint": str(endpoint),
                "rss_scope": "process lifetime high-water RSS; not an isolated incremental peak"}}


def measure_final_wrapper(post_start, post_cpu, pre_raw):
    """Observe the final sample only at the post-hashing call site."""
    measurement = None
    try:
        measurement = {"wall_seconds": time.monotonic() - post_start,
                       "cpu_seconds": time.process_time() - post_cpu,
                       "peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * (1 if sys.platform == "darwin" else 1024),
                       "boundary": FINAL_TIMING_BOUNDARY}
        check = validate_final_timing(measurement, pre_raw, FINAL_MEASUREMENT_ENDPOINT)
    except (OSError, ValueError, TypeError, OverflowError) as exc:
        check = {"complete": False, "reason": f"final wrapper measurement unavailable: {type(exc).__name__}: {exc}",
                 "diagnostic": {"final_safe_repr": repr(measurement),
                                "endpoint": FINAL_MEASUREMENT_ENDPOINT}}
    return measurement if check["complete"] else None, check


def classify_final(child, integrity, output_ok, timing_check):
    """Final timing adds one validity conjunct; it cannot erase a child cause."""
    result = _p.classify(child, integrity, output_ok and timing_check["complete"] is True)
    if timing_check["complete"] is not True:
        result["invalid_reason"] = "; ".join(filter(None, (
            result["invalid_reason"], "wrapper_postprocessing_complete: " + str(timing_check["reason"]))))
    return result


def inspect_authority_mirrors(repository, authority, fixture, bindings, initial=None):
    """Inspect disposable copies in addition to independently checked originals.

    This function never supplies a claim, native receipt, epoch, clock or
    authority. Its booleans describe mirror presence, aliasing, bytes and
    identity only. The caller always retains the original authority predicates.
    """
    mirrors = fixture.get("authority_mirrors")
    require(type(mirrors) is dict and set(mirrors) == {"claim", "native_receipt"},
            "authority_mirror_shape", "exact claim/native_receipt mirror pair required")
    case_id = fixture["case_id"]
    _p.relative_name(case_id, leaf=True)
    checks, observed, diagnostics = {}, {}, {}
    repository = Path(repository)
    for kind, filename in (("claim", "claim.json"), ("native_receipt", "native-receipt.json")):
        label = kind + "_mirror_"
        ref = mirrors[kind]
        require(type(ref) is dict and set(ref) == {"path", "sha256"}
                and all(type(ref[key]) is str and ref[key] for key in ref),
                label + "shape", "exact nonempty string path/sha256 required")
        expected_path = MIRROR_SCRATCH_ROOT + "/authority-mirrors/" + case_id + "/" + filename
        _p.relative_name(ref["path"])
        require(ref["path"] == expected_path, label + "path", "exact per-case mirror namespace required")
        require(ref["sha256"] == authority[kind]["sha256"] and re.fullmatch("[0-9a-f]{64}", ref["sha256"]),
                label + "bytes", "mirror pin must equal the genuine original digest")
        path = repository / ref["path"]
        original_path = repository / authority[kind]["path"]
        checks.update({label + name: False for name in ("present", "nonalias", "bytes", "identity")})
        checks[label + "present"] = os.path.lexists(path)
        if not checks[label + "present"]:
            diagnostics[kind] = "mirror absent"
            continue
        try:
            raw, identity = _p.read_regular(path)
            other_identities = {tuple(item["identity"][:2]) for name, item in bindings.items() if name != str(path)}
            other_identities.update(tuple(item["identity"][:2]) for item in observed.values())
            original_raw, original_identity = _p.read_regular(original_path)
            checks[label + "nonalias"] = identity[:2] != original_identity[:2] and identity[:2] not in other_identities
            checks[label + "bytes"] = (raw == original_raw and _p.digest(raw) == ref["sha256"]
                                         and _p.digest(original_raw) == authority[kind]["sha256"])
            binding = {"path": str(path), "sha256": _p.digest(raw), "identity": list(identity)}
            checks[label + "identity"] = initial is None or initial.get(kind) == binding
            observed[kind] = binding
        except (OSError, ValueError) as exc:
            diagnostics[kind] = f"{type(exc).__name__}: {exc}"
    return {"checks": checks, "bindings": observed, "diagnostics": diagnostics,
            "scope": "disposable mirror integrity only; genuine original authority is checked separately"}


def require_mirror_checks(result):
    for name, value in result["checks"].items():
        require(value is True, name, result["diagnostics"] or "mirror bytes/identity do not match the initial genuine original copy")


def _diagnostic(snapshot, value):
    """Only an independently scoped fixture diagnostic; never a replacement RUN."""
    relative = _p.relative_name(snapshot["plan"]["fixture_authorization"]["terminal_diagnostic"])
    root = Path(snapshot["root"])
    path = root / relative
    require(path.name == "terminal-diagnostic.json" and not path.is_relative_to(snapshot["run_directory"]),
            "diagnostic_scope", "diagnostic must be outside child output")
    fd = _p.open_directory(path.parent)
    try:
        _p.write_exclusive(fd, path.name, _p.canonical(value) + b"\n")
        os.fsync(fd)
    finally:
        os.close(fd)
    return str(path)


def fixture_barrier(stage, snapshot):
    """Only parent-published named barriers for the declared collision controls."""
    barrier = snapshot["plan"]["fixture_authorization"].get("barriers", {}).get(stage)
    if barrier is None:
        return
    allowed = {"before_command", "before_environment", "before_stdout_log", "before_stderr_log", "before_manifest"}
    require(stage in allowed and snapshot["case"]["case_id"] in {
        "manifest-last-barrier", "manifest-file-race-barrier", "child-manifest-collision",
        "symlink-command.txt", "hardlink-command.txt", "symlink-environment.json", "hardlink-environment.json",
        "symlink-stdout.log", "hardlink-stdout.log", "symlink-stderr.log", "hardlink-stderr.log",
        "symlink-manifest.yaml", "hardlink-manifest.yaml"}, "barrier_scope", "undeclared barrier control")
    permitted = Path(snapshot["authority_repository"]) / "coordination/pending-ideas/BATCH-e9d1c7/timing-correction/qa/scratch"
    fds = []
    try:
        for key in ("ready", "release"):
            ref = barrier[key]
            path = Path(ref["path"])
            require(path.is_relative_to(permitted) and not path.is_relative_to(snapshot["root"]),
                    "barrier_path", "parent-owned FIFO must be outside the clean fixture copy")
            directory = _p.open_directory(path.parent)
            try:
                fd = os.open(path.name, os.O_RDWR | os.O_NONBLOCK | os.O_NOFOLLOW, dir_fd=directory)
            finally:
                os.close(directory)
            fds.append(fd)
            st = os.fstat(fd)
            require(stat.S_ISFIFO(st.st_mode) and [st.st_dev, st.st_ino] == ref["identity"],
                    "barrier_identity", "exact parent FIFO identity required")
        os.write(fds[0], (stage + "\n").encode())
        ready, _, _ = select.select([fds[1]], [], [], snapshot["plan"]["resource_policy"]["timeout_seconds"])
        require(bool(ready) and os.read(fds[1], 64) == b"release\n", "barrier_release", "bounded barrier timeout or wrong release")
    finally:
        for fd in fds:
            os.close(fd)


def execute_locked(verified_launch):
    require(type(verified_launch) is VerifiedLaunch and _issued.get(id(verified_launch)) == verified_launch.snapshot_json,
            "verified_token", "only an immutable token issued by this admission can execute")
    _issued.pop(id(verified_launch))
    previous = _p.strict_json(verified_launch.snapshot_json)
    reference = _p.strict_json(verified_launch.authority_json)
    current = _admit(verified_launch.lock_path, verified_launch.expected_sha256,
                     verified_launch.run_id, reference, mirror_baseline=previous["mirror_bindings"])
    exact(current, previous, "prelaunch_identity")
    snapshot = current
    root, run_dir = Path(snapshot["root"]), Path(snapshot["run_directory"])
    plan, row = snapshot["plan"], snapshot["row"]
    policy = plan["resource_policy"]
    started_at, total_start = utc(), time.monotonic()
    parent_fd = _p.open_directory(run_dir.parent)
    dir_fd, out_fd, err_fd, context_fd = None, None, None, None
    child = None
    actual_argv = None
    context_bytes = None
    outcome = None
    try:
        require(list(_p.file_identity(os.fstat(parent_fd)))[:2] == snapshot["parent_identity"][:2],
                "output_parent_identity", "parent changed after admission")
        os.mkdir(run_dir.name, mode=0o700, dir_fd=parent_fd)
        dir_fd = os.open(run_dir.name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent_fd)
        dir_identity = list(_p.file_identity(os.fstat(dir_fd)))
        out_fd = _p.exclusive_file(dir_fd, "stdout.txt")
        err_fd = _p.exclusive_file(dir_fd, "stderr.txt")
        # The anonymous context remains read-only in the child. The exact bytes
        # are retained in raw-result/terminal diagnostic, not discarded evidence.
        writable, name = tempfile.mkstemp(prefix=".launch-context-", dir=run_dir)
        try:
            context_fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW)
            os.unlink(name)
            actual_argv = [str(context_fd) if arg == "{launch_context_fd}" else arg for arg in row["argv"]]
            context = {"format_version": 1, "snapshot": snapshot, "argv": actual_argv,
                       "parent_pid": os.getpid(), "directory_identity": dir_identity}
            context_bytes = _p.canonical(context)
            view = memoryview(context_bytes)
            while view:
                view = view[os.write(writable, view):]
            os.fsync(writable)
        finally:
            os.close(writable)
        command = shlex.join(actual_argv)
        fixture_barrier("before_command", snapshot)
        command_raw = (command + "\n").encode()
        _p.write_exclusive(dir_fd, "command.txt", command_raw)
        environment = {"python": snapshot["approval_document"]["execution_approval"]["python"],
                       "dependencies": plan["dependency_closure"], "selected_environment": plan["environment_policy"],
                       "native_launch_receipt": snapshot["native"], "claim": snapshot["claim"],
                       "platform": sys.platform, "effective_uid": os.geteuid(),
                       "authority": reference, "source_snapshot": plan["source_snapshot"],
                       "actual_launch_commit": snapshot["launch_commit"]}
        fixture_barrier("before_environment", snapshot)
        environment_raw = _p.canonical(environment) + b"\n"
        _p.write_exclusive(dir_fd, "environment.json", environment_raw)
        preexec = _admit(verified_launch.lock_path, verified_launch.expected_sha256,
                         verified_launch.run_id, reference, output_identity=dir_identity, mirror_baseline=snapshot["mirror_bindings"])
        # Directory timestamps can change from our exclusive outputs. Source,
        # data, authority and Git identities must still match the first admission.
        for key in ("bindings", "launch_commit", "row", "claim", "native", "approval_document", "plan"):
            exact(preexec[key], snapshot[key], "preexec_" + key)
        child, sampling = _p.run_child(root=root, argv=actual_argv, cwd=run_dir,
                      env=plan["environment_policy"]["inner"], stdout_fd=out_fd, stderr_fd=err_fd,
                      context_fd=context_fd, timeout_seconds=policy["timeout_seconds"],
                      memory_bytes=policy["memory_bytes"], cpu_seconds=policy["cpu_seconds"])
        # No finalization may run concurrently with an unquiesced child.
        if child.group_quiescent is not True:
            raise FiniteYamlLockError("process_group_quiescent", "preserve partials; finalization forbidden")
        post_start, post_cpu = time.monotonic(), time.process_time()
        for name, fd in (("stdout.txt", out_fd), ("stderr.txt", err_fd)):
            raw, identity = _p.read_regular(run_dir / name)
            require(identity[:2] == _p.file_identity(os.fstat(fd))[:2] and raw == _p.read_fd(fd),
                    "capture_file_identity", name)
        require(_p.read_regular(run_dir / "command.txt")[0] == command_raw,
                "command_output_unchanged", "child modified the parent command artifact")
        require(_p.read_regular(run_dir / "environment.json")[0] == environment_raw,
                "environment_output_unchanged", "child modified the parent environment artifact")
        fixture_barrier("before_stdout_log", snapshot)
        _p.write_exclusive(dir_fd, "stdout.log", _p.read_fd(out_fd))
        fixture_barrier("before_stderr_log", snapshot)
        _p.write_exclusive(dir_fd, "stderr.log", _p.read_fd(err_fd))
        profile = PROFILES[row["configuration"]["experiment_id"]]
        expected_before_raw = [name for name in profile["complete_names"] if name not in ("manifest.yaml", "raw-result.json")]
        inspected = _p.inspect_outputs(run_dir, expected_before_raw)
        checks, additional = _postflight(snapshot, child, inspected)
        integrity = {**checks, **{k: v for k, v in additional.items()
                                 if k not in ("exact_output_membership", "nonalias_regular_files", "all_artifact_hashes_verified")}}
        output_ok = not inspected["missing"] and not inspected["extra"] and not inspected["aliases"]
        outcome = _p.classify(child, integrity, output_ok)
        approval = snapshot["approval_document"]["execution_approval"]
        pre_raw_observation = {"wall_seconds": time.monotonic() - post_start,
                   "cpu_seconds": time.process_time() - post_cpu,
                   "peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * (1 if sys.platform == "darwin" else 1024),
                   "boundary": "postflight-and-existing-file-hashing-before-raw-result-serialization"}
        # Boundary is through hashing every core artifact whose bytes already
        # exist. raw-result serialization/hash is finalization, disclosed below.
        inputs = {"curve_id": row["curve_id"], "seed": row["seed"],
                  "parameters": {**row["configuration"], "fixture_only": True,
                                 "simulated_reservation": plan["fixture_authorization"]["simulated_reservation"]}}
        protocol = {"approval_lock_path": snapshot["lock_path"], "approval_lock_sha256": snapshot["lock_sha256"],
                    "specification_sha256": approval["specification_sha256"],
                    "execution_plan_sha256": approval["execution_plan_sha256"],
                    "run_object_sha256": _p.digest(_p.canonical(row)),
                    "protocol_hashes_sha256": _p.digest(_p.canonical(approval["protocol_hashes"])),
                    "approved_base_commit": approval["approved_base_commit"], "launch_commit": snapshot["launch_commit"],
                    "python_sha256": approval["python"]["sha256"], "descendant_policy": policy["descendant_policy"],
                    "effective_uid": policy["effective_uid"], "timeout_seconds": policy["timeout_seconds"],
                    "post_run_checks": checks}
        child_value = dataclasses.asdict(child)
        raw_result = {"scientific_content": False, "child_outcome": child_value, "classification": outcome,
                      "classification_scope": "pre-final-inventory-and-final-measurement; final manifest owns terminal status and validity",
                      "postflight_failures": [k for k, v in {**checks, **additional}.items() if v is not True],
                      "additional_post_run_checks": additional,
                      "launch_receipt": {"format_version": 1, "experiment_id": row["configuration"]["experiment_id"],
                          "run_id": row["run_id"], "role": row["role"], "argv": actual_argv, "command": command,
                          "inputs": inputs, **protocol, "python": approval["python"], "process_group": child_value,
                          "wrapper_postprocessing": None,
                          "wrapper_postprocessing_unavailable_reason": "The immutable raw companion precedes its own hash; authoritative final measurement is manifest.yaml#/run/resources/wrapper_postprocessing.",
                          "predecessor": None, "profile_expectations": inspected,
                          "native_launch_receipt": snapshot["native"], "claim": snapshot["claim"], "authority": reference},
                      "resource_sampling": sampling, "launch_context_utf8": context_bytes.decode(),
                      "cost_boundary": {"actual_wrapper_measurement_location": "run.resources.wrapper_postprocessing",
                          "pre_raw_observation": pre_raw_observation,
                          "raw_mirror_requirement": "unavailable_by_declared_boundary",
                          "excluded_finalization": "Final schema validation, later fsync/race rechecks and manifest serialization/write/fsync; not included in the stated endpoint.",
                          "raw_result_self_hash": False, "finalization_seconds": None,
                          "final_measurement_endpoint": FINAL_MEASUREMENT_ENDPOINT,
                          "schema_boundary_label_semantics": "Legacy compatibility token; embedded raw receipt is already written, no separate receipt is emitted.",
                          "limitation": "Final manifest owns final timing and validity; raw companion is immutable preliminary/provisional data."}}
        _p.write_exclusive(dir_fd, "raw-result.json", _p.canonical(raw_result) + b"\n")
        final_inventory = _p.inspect_outputs(run_dir, profile["complete_names"])
        final_ok = not final_inventory["missing"] and not final_inventory["extra"] and not final_inventory["aliases"]
        if not final_ok:
            outcome = _p.classify(child, integrity, False)
        # Every already captured file retains identity/hash, even if its bytes
        # happen to match a replacement inode. Parent-owned files are never reopened writable.
        for name, observed in inspected["artifacts"].items():
            exact(final_inventory["artifacts"].get(name), observed, "postflight_artifact_identity")
        artifacts = {name: {"sha256": info["sha256"], "bytes": info["bytes"]}
                     for name, info in final_inventory["artifacts"].items()}
        # Endpoint is after final raw bytes and all nonmanifest artifacts have
        # been identity-checked and hashed. Never rewrite the immutable raw file.
        wrapper, timing_check = measure_final_wrapper(post_start, post_cpu, pre_raw_observation)
        outcome = classify_final(child, integrity, output_ok and final_ok, timing_check)
        manifest = {"run": {"id": row["run_id"], "experiment_id": row["configuration"]["experiment_id"],
                   "status": outcome["status"], "code": {"commit": snapshot["launch_commit"], "dirty": False, "command": command},
                   "environment": environment, "inputs": inputs,
                   "timing": {"started_at": started_at, "finished_at": utc(), "wall_seconds": child.wall_seconds,
                              "total_wall_seconds": time.monotonic() - total_start},
                   "resources": {"peak_rss_bytes": None if child.infrastructure_error else child.peak_rss_bytes,
                                 "cpu_seconds": None if child.infrastructure_error else child.cpu_seconds},
                   "result": {"metrics": {"scope": "benign operational fixture only", "scientific_runs": 0,
                                          "wrapper_postprocessing_complete": timing_check["complete"],
                                          "wrapper_postprocessing_failure_reason": timing_check["reason"],
                                          "wrapper_postprocessing_endpoint": FINAL_MEASUREMENT_ENDPOINT,
                                          "wrapper_postprocessing_diagnostic": timing_check["diagnostic"]},
                              "valid": outcome["valid"], "invalid_reason": outcome["invalid_reason"],
                              "certificate": {"kind": "none", "verified": None, "verifier": None}},
                   "artifacts": artifacts, "protocol": protocol,
                   "inference": {"native_launch_receipt": snapshot["native"], "claim": snapshot["claim"], "authority": reference}}}
        if timing_check["complete"]:
            manifest["run"]["resources"]["wrapper_postprocessing"] = wrapper
        else:
            manifest["run"]["resources"]["unavailable_reason"] = timing_check["reason"]
        if child.infrastructure_error:
            manifest["run"]["resources"]["unavailable_reason"] = "; ".join(filter(None, (
                manifest["run"]["resources"].get("unavailable_reason"), child.infrastructure_error)))
        schema_validate(manifest, root, "run-manifest.schema.json")
        # Flush every safe ordinary output, then atomically reserve the manifest
        # name with O_EXCL. No check-then-open(w) path exists.
        for name in artifacts:
            fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=dir_fd)
            try:
                os.fsync(fd)
            finally:
                os.close(fd)
        os.fsync(dir_fd)
        fixture_barrier("before_manifest", snapshot)
        last_inventory = _p.inspect_outputs(run_dir, profile["complete_names"])
        # A manifest collision is deliberately left to exclusive creation, so
        # the raced name cannot ever be opened with overwrite permissions.
        for name in artifacts:
            exact(last_inventory["artifacts"].get(name), final_inventory["artifacts"][name],
                  "final_artifact_identity")
        require(not last_inventory["aliases"] and set(last_inventory["extra"]) <= {"manifest.yaml"},
                "final_output_membership", "late output alias or undeclared file")
        _p.write_exclusive(dir_fd, "manifest.yaml", _p.canonical(manifest) + b"\n")
        os.fsync(dir_fd)
        return str(run_dir / "manifest.yaml")
    except BaseException as exc:
        diagnostic = {"kind": "operational_terminal_diagnostic", "scientific_runs": 0,
                      "exception": type(exc).__name__, "error": str(exc), "predicate": getattr(exc, "predicate", None),
                      "child": dataclasses.asdict(child) if child is not None else None,
                      "classification": outcome, "argv": actual_argv,
                      "launch_context_utf8": context_bytes.decode() if context_bytes is not None else None,
                      "run_directory": str(run_dir), "observed_at": utc(),
                      "canonical_manifest_written": False}
        try:
            diagnostic["output_inventory"] = _p.inspect_outputs(run_dir, PROFILES[row["configuration"]["experiment_id"]]["complete_names"])
        except (OSError, ValueError) as inventory_error:
            diagnostic["inventory_error"] = str(inventory_error)
        try:
            diagnostic_path = _diagnostic(snapshot, diagnostic)
        except (OSError, ValueError) as diagnostic_error:
            raise FiniteYamlLockError("terminal_diagnostic_unavailable", f"original={exc}; diagnostic={diagnostic_error}") from exc
        raise FiniteYamlLockError("terminal_failure", f"{exc}; preserved diagnostic={diagnostic_path}") from exc
    finally:
        for fd in (context_fd, out_fd, err_fd, dir_fd, parent_fd):
            if fd is not None:
                os.close(fd)


def child_entry(experiment_id, argv=None):
    """Isolated descriptor entry: hash/identity rechecks without spawning Git.

    The parent's immediately pre-Popen publication check is the Git boundary.
    The child is forbidden to fork, uses a read-only inherited context, and
    independently compares its contents to all current published/source bytes.
    This is a trusted-parent capability, not same-user cryptographic attestation.
    """
    parser = argparse.ArgumentParser(description="Finite YAML v3 isolated benign entry")
    parser.add_argument("--launch-context-fd", type=int, required=True)
    args = parser.parse_args(argv)
    try:
        import fcntl
        require(args.launch_context_fd > 2 and fcntl.fcntl(args.launch_context_fd, fcntl.F_GETFL) & os.O_ACCMODE == os.O_RDONLY,
                "context_descriptor", "parent-owned read-only descriptor required")
        st = os.fstat(args.launch_context_fd)
        require(stat.S_ISREG(st.st_mode) and st.st_nlink == 0 and st.st_size <= 32 * 1024 * 1024,
                "context_descriptor", "anonymous bounded regular context required")
        context = _p.strict_json(_p.read_fd(args.launch_context_fd))
        require(context["format_version"] == 1 and type(context["format_version"]) is int,
                "context_version", "exact integer one")
        require(context["parent_pid"] == os.getppid(), "context_parent", "context parent mismatch")
        snapshot = context["snapshot"]
        require(snapshot["root"] == str(REPO_ROOT), "child_root", "entry belongs to another source checkout")
        require(snapshot["row"]["configuration"]["experiment_id"] == experiment_id,
                "child_experiment", "wrong source-v4 entry")
        require(context["argv"] == [str(Path(sys.executable).resolve()), "-I", "-S", "-B", str(Path(sys.argv[0]).absolute()),
                                     "--launch-context-fd", str(args.launch_context_fd)],
                "child_argv", "exact isolated argv required")
        require(sys.flags.isolated == 1 and sys.flags.no_site == 1 and sys.flags.dont_write_bytecode == 1,
                "child_python_flags", "-I -S -B required")
        require(snapshot["plan"]["scientific_execution_authorized"] is False,
                "child_scientific_authority", "engineering entry refuses scientific execution")
        mirror_paths = {value["path"] for value in snapshot["mirror_bindings"].values()}
        for binding in snapshot["bindings"].values():
            if binding["path"] not in mirror_paths:
                require(_p.unchanged(binding), "child_bound_file_identity", binding["path"])
        reference = snapshot["reference"]
        require(reference["authority_path"] == AUTHORITY_PATH and reference["git"]["path"] == SYSTEM_GIT,
                "child_authority_namespace", "wrong published root")
        authority_raw = _p.read_regular(Path(snapshot["authority_repository"]) / AUTHORITY_PATH)[0]
        require(_p.digest(authority_raw) == reference["authority_sha256"], "child_authority_hash", "published root drift")
        exact(_p.strict_json(authority_raw), snapshot["authority"], "child_authority_content")
        matches = [c for c in snapshot["authority"]["cases"] if c["case_id"] == reference["case_id"]]
        require(len(matches) == 1, "child_case", "unique parent case required")
        exact(matches[0], snapshot["case"], "child_case_content")
        row = snapshot["row"]
        check_configuration(experiment_id, row["run_id"], row["configuration"])
        require(_p.digest(_p.canonical(row)) == snapshot["case"]["run_object_sha256"], "child_configuration_hash", "row mismatch")
        plan_raw = _p.read_regular(REPO_ROOT / snapshot["case"]["plan"]["path"])[0]
        require(_p.digest(plan_raw) == snapshot["case"]["plan"]["sha256"], "child_plan_hash", "plan mismatch")
        exact(_p.strict_json(plan_raw)["execution_plan"], snapshot["plan"], "child_plan_content")
        approval_raw = _p.read_regular(snapshot["lock_path"])[0]
        require(_p.digest(approval_raw) == snapshot["case"]["lock"]["sha256"] == snapshot["lock_sha256"], "child_lock_hash", "lock mismatch")
        require(_p.digest(_p.canonical(snapshot["approval_document"])) == snapshot["case"]["approval_document_sha256"],
                "child_approval_content", "parent-parsed document digest mismatch")
        claim = snapshot["claim"]
        now = datetime.now(timezone.utc)
        require(timestamp(claim["acquired_at"], "child_claim_time") <= now < timestamp(claim["expires_at"], "child_claim_time"),
                "child_claim_current", "claim expired or future-acquired")
        validate_native(snapshot["native"], claim, snapshot["authority"]["native_receipt"]["record"], snapshot["authority"]["excluded_session_ids"])
        mirror_result = inspect_authority_mirrors(Path(snapshot["authority_repository"]), snapshot["authority"],
            snapshot["plan"]["fixture_authorization"], dict(snapshot["bindings"]), snapshot["mirror_bindings"])
        require_mirror_checks(mirror_result)
        require(Path.cwd() == Path(snapshot["run_directory"]), "child_directory", "wrong cwd")
        require(list(_p.file_identity(Path.cwd().stat()))[:2] == context["directory_identity"][:2], "child_directory_identity", "directory replaced")
        exact(dict(os.environ), snapshot["plan"]["environment_policy"]["inner"], "child_environment")
        require(resource.getrlimit(resource.RLIMIT_NPROC) == (0, 0), "child_descendant_policy", "RLIMIT_NPROC zero not enforced")
        dependency = snapshot["plan"]["dependency_closure"]
        require(str(Path(sys.executable).resolve()) == dependency["python"]["executable"] and sys.version == dependency["python"]["version"],
                "child_python_identity", "interpreter mismatch")
        actual_origins = {name: str(Path(m.__file__).resolve()) for name, m in sys.modules.copy().items()
                          if getattr(m, "__file__", None) and not str(m.__file__).startswith("<")}
        exact(actual_origins, dependency["module_origins"]["child"], "child_module_origins")
        exact(loaded_images(), dependency["loaded_images"]["child"], "child_library_identity")
        fixture = snapshot["plan"]["fixture_authorization"]
        require(fixture["worker"]["path"] == FIXED_WORKER, "child_worker", "fixed benign loader only")
        worker_path = REPO_ROOT / FIXED_WORKER
        source = _p.read_regular(worker_path)[0]
        require(_p.digest(source) == fixture["worker"]["sha256"], "child_worker_hash", "worker drift")
        worker_input = _p.strict_json(_p.read_regular(REPO_ROOT / fixture["worker_input"]["path"])[0])
        require(_p.digest(_p.canonical(worker_input)) == fixture["worker_input_document_sha256"], "child_worker_input", "input mismatch")
        validate_recovery_case_arms(RECOVERY_CASES, RECOVERY_CASES)
        # The sole callable is code at the immutable fixed worker path. No
        # caller module, import string, function or scientific kernel can enter.
        module_spec = importlib.util.spec_from_file_location("finite_yaml_v3_benign_worker", worker_path)
        module = importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(module)
        return module.run(worker_input, {"experiment_id": experiment_id, "run_id": row["run_id"],
                    "configuration": row["configuration"], "specification": snapshot["plan"]["specification"],
                    "authority_mirrors": snapshot["mirror_bindings"], "authority_repository": snapshot["authority_repository"],
                    "recovery_arms": {"B": RECOVERY_CASES, "I": RECOVERY_CASES},
                    "manifest_context": {"canonical_lock_verified": True, "scientific_authority_verified": False,
                        "claim_verified": True, "source_snapshot_verified": True, "semantic_gate_verified": False,
                        "memory_limit_enforced": True}, "output_names": PROFILES[experiment_id]["original_names"]})
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"finite_yaml_v3_refusal: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lock", required=True)
    parser.add_argument("--expected-sha256", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--authority", required=True)
    args = parser.parse_args(argv)
    try:
        reference = _p.strict_json(_p.read_regular(Path(args.authority).absolute())[0])
        launch = validate_lock(args.lock, args.expected_sha256, args.run_id, reference)
        print(execute_locked(launch))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"finite_yaml_v3_refusal: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2

CONFIGURATIONS = [{'experiment_id': 'EXP-ECDLP-abf981', 'version': 1, 'run_id': 'RUN-ECDLP-56d8aa', 'run_directory': 'experiments/EXP-ECDLP-abf981/runs/RUN-ECDLP-56d8aa', 'configuration': {'experiment_id': 'EXP-ECDLP-abf981', 'version': 1, 'cell': 'p11', 'run_id': 'RUN-ECDLP-56d8aa'}, 'constants': {'cell': 'p11', 'p': 11, 'r': 9, 's': 10, 'c': 5, 'A': 6, 'B': 10, 'a': 3, 'd_twisted': 7, 'd_edwards': 6, 'expected_group_order': 12}, 'specification': {'path': 'experiments/EXP-ECDLP-abf981/specification.yaml', 'sha256': '7d9a6cccbfdaf8d9efc1d565cf437c1e833d4de964c5fdc3cd77b72e3d3dbf93'}, 'source_entry': 'experiments/EXP-ECDLP-abf981/source-v4/locked_entry.py', 'scientific_execution_authorized': False}, {'experiment_id': 'EXP-ECDLP-abf981', 'version': 1, 'run_id': 'RUN-ECDLP-591253', 'run_directory': 'experiments/EXP-ECDLP-abf981/runs/RUN-ECDLP-591253', 'configuration': {'experiment_id': 'EXP-ECDLP-abf981', 'version': 1, 'cell': 'p23', 'run_id': 'RUN-ECDLP-591253'}, 'constants': {'cell': 'p23', 'p': 23, 'r': 4, 's': 18, 'c': 5, 'A': 16, 'B': 9, 'a': 2, 'd_twisted': 22, 'd_edwards': 11, 'expected_group_order': 24}, 'specification': {'path': 'experiments/EXP-ECDLP-abf981/specification.yaml', 'sha256': '7d9a6cccbfdaf8d9efc1d565cf437c1e833d4de964c5fdc3cd77b72e3d3dbf93'}, 'source_entry': 'experiments/EXP-ECDLP-abf981/source-v4/locked_entry.py', 'scientific_execution_authorized': False}, {'experiment_id': 'EXP-ECDLP-2cb7f8', 'version': 1, 'run_id': 'RUN-ECDLP-3c6277', 'run_directory': 'experiments/EXP-ECDLP-2cb7f8/runs/RUN-ECDLP-3c6277', 'configuration': {'experiment_id': 'EXP-ECDLP-2cb7f8', 'version': 1, 'case_id': 'E5', 'p': 5, 'curve_constant': 1, 'run_id': 'RUN-ECDLP-3c6277'}, 'specification': {'path': 'experiments/EXP-ECDLP-2cb7f8/specification.yaml', 'sha256': 'e7ea730e68d674a4de0ef6cdbc159d98ff4473a9b9539f9b18b1da52c936659e'}, 'source_entry': 'experiments/EXP-ECDLP-2cb7f8/source-v4/locked_entry.py', 'scientific_execution_authorized': False}, {'experiment_id': 'EXP-ECDLP-2cb7f8', 'version': 1, 'run_id': 'RUN-ECDLP-413b2a', 'run_directory': 'experiments/EXP-ECDLP-2cb7f8/runs/RUN-ECDLP-413b2a', 'configuration': {'experiment_id': 'EXP-ECDLP-2cb7f8', 'version': 1, 'case_id': 'E7', 'p': 7, 'curve_constant': 1, 'run_id': 'RUN-ECDLP-413b2a'}, 'specification': {'path': 'experiments/EXP-ECDLP-2cb7f8/specification.yaml', 'sha256': 'e7ea730e68d674a4de0ef6cdbc159d98ff4473a9b9539f9b18b1da52c936659e'}, 'source_entry': 'experiments/EXP-ECDLP-2cb7f8/source-v4/locked_entry.py', 'scientific_execution_authorized': False}, {'experiment_id': 'EXP-ECDLP-2cb7f8', 'version': 1, 'run_id': 'RUN-ECDLP-b0a390', 'run_directory': 'experiments/EXP-ECDLP-2cb7f8/runs/RUN-ECDLP-b0a390', 'configuration': {'experiment_id': 'EXP-ECDLP-2cb7f8', 'version': 1, 'case_id': 'E11', 'p': 11, 'curve_constant': 1, 'run_id': 'RUN-ECDLP-b0a390'}, 'specification': {'path': 'experiments/EXP-ECDLP-2cb7f8/specification.yaml', 'sha256': 'e7ea730e68d674a4de0ef6cdbc159d98ff4473a9b9539f9b18b1da52c936659e'}, 'source_entry': 'experiments/EXP-ECDLP-2cb7f8/source-v4/locked_entry.py', 'scientific_execution_authorized': False}, {'experiment_id': 'EXP-ECDLP-2cb7f8', 'version': 1, 'run_id': 'RUN-ECDLP-d7d29d', 'run_directory': 'experiments/EXP-ECDLP-2cb7f8/runs/RUN-ECDLP-d7d29d', 'configuration': {'experiment_id': 'EXP-ECDLP-2cb7f8', 'version': 1, 'case_id': 'E17', 'p': 17, 'curve_constant': 1, 'run_id': 'RUN-ECDLP-d7d29d'}, 'specification': {'path': 'experiments/EXP-ECDLP-2cb7f8/specification.yaml', 'sha256': 'e7ea730e68d674a4de0ef6cdbc159d98ff4473a9b9539f9b18b1da52c936659e'}, 'source_entry': 'experiments/EXP-ECDLP-2cb7f8/source-v4/locked_entry.py', 'scientific_execution_authorized': False}, {'experiment_id': 'EXP-ECDLP-2cb7f8', 'version': 1, 'run_id': 'RUN-ECDLP-e2e77c', 'run_directory': 'experiments/EXP-ECDLP-2cb7f8/runs/RUN-ECDLP-e2e77c', 'configuration': {'experiment_id': 'EXP-ECDLP-2cb7f8', 'version': 1, 'case_id': 'N0-Eprime5', 'p': 5, 'curve_constant': 2, 'run_id': 'RUN-ECDLP-e2e77c'}, 'specification': {'path': 'experiments/EXP-ECDLP-2cb7f8/specification.yaml', 'sha256': 'e7ea730e68d674a4de0ef6cdbc159d98ff4473a9b9539f9b18b1da52c936659e'}, 'source_entry': 'experiments/EXP-ECDLP-2cb7f8/source-v4/locked_entry.py', 'scientific_execution_authorized': False}]

RECOVERY_CASES = [{'id': 'c2_nonzero_c3_nonzero', 'condition': 'c2 != 0 and c3 != 0', 'scope': 'section regime', 'degree': 4, 'O_multiplicity': 0}, {'id': 'c2_nonzero_c3_zero', 'condition': 'c2 != 0 and c3 = 0', 'scope': 'section regime', 'degree': 3, 'O_multiplicity': 1}, {'id': 'c2_zero_h_degree_2', 'condition': 'c2 = 0 and degree(h) = 2', 'scope': 'section regime', 'degree': 2, 'O_multiplicity': 0}, {'id': 'c2_zero_h_degree_1', 'condition': 'c2 = 0 and degree(h) = 1', 'scope': 'section regime', 'degree': 1, 'O_multiplicity': 2}, {'id': 'c2_zero_h_degree_0', 'condition': 'c2 = 0 and degree(h) = 0', 'scope': 'section regime', 'degree': 0, 'O_multiplicity': 4}, {'id': 'root_y_two_nonzero', 'condition': 'c2 = 0: rational root a of h has two nonzero opposite rational y values', 'scope': 'per rational root', 'multiplicity': 'e at each point'}, {'id': 'root_y_zero', 'condition': 'c2 = 0: rational root a of h has y = 0', 'scope': 'per rational root', 'multiplicity': '2e'}, {'id': 'root_y_absent', 'condition': 'c2 = 0: rational root a of h has nonsquare curve right-hand side', 'scope': 'per rational root', 'unresolved_degree': '2e'}, {'id': 'residual_constant', 'condition': 'After all rational root divisions, the applicable F_c or h residual polynomial is constant', 'scope': 'residual support decision'}, {'id': 'residual_nonconstant', 'condition': 'After all rational root divisions, the applicable F_c or h residual polynomial is nonconstant', 'scope': 'residual support decision; nonsplit support retained'}, {'id': 'O_present', 'condition': 'Positive prescribed pole deficit; verify local section order at O', 'scope': 'infinity decision'}, {'id': 'O_absent', 'condition': 'Zero prescribed pole deficit; verify local section order zero at O', 'scope': 'infinity decision'}]

PROFILES = {'EXP-ECDLP-2cb7f8': {'original_names': ['anomalies.jsonl', 'controls.json', 'correspondence.json', 'divisors.jsonl', 'inputs.json', 'manifest.yaml', 'metrics.json', 'points.json', 'presentation-inventory.json', 'sections.jsonl', 'stderr.txt', 'stdout.txt'], 'companion_names': ['command.txt', 'environment.json', 'stdout.log', 'stderr.log', 'raw-result.json'], 'complete_names': ['anomalies.jsonl', 'command.txt', 'controls.json', 'correspondence.json', 'divisors.jsonl', 'environment.json', 'inputs.json', 'manifest.yaml', 'metrics.json', 'points.json', 'presentation-inventory.json', 'raw-result.json', 'sections.jsonl', 'stderr.log', 'stderr.txt', 'stdout.log', 'stdout.txt'], 'manifest_hashed_names': ['anomalies.jsonl', 'command.txt', 'controls.json', 'correspondence.json', 'divisors.jsonl', 'environment.json', 'inputs.json', 'metrics.json', 'points.json', 'presentation-inventory.json', 'raw-result.json', 'sections.jsonl', 'stderr.log', 'stderr.txt', 'stdout.log', 'stdout.txt']}, 'EXP-ECDLP-abf981': {'original_names': ['control-results.json', 'costs.json', 'execution-report.md', 'manifest.yaml', 'map-certificates.json', 'polynomial-systems.json', 'raw-results.json', 'relation-certificates.json', 'stderr.txt', 'stdout.txt'], 'companion_names': ['command.txt', 'environment.json', 'stdout.log', 'stderr.log', 'raw-result.json'], 'complete_names': ['command.txt', 'control-results.json', 'costs.json', 'environment.json', 'execution-report.md', 'manifest.yaml', 'map-certificates.json', 'polynomial-systems.json', 'raw-result.json', 'raw-results.json', 'relation-certificates.json', 'stderr.log', 'stderr.txt', 'stdout.log', 'stdout.txt'], 'manifest_hashed_names': ['command.txt', 'control-results.json', 'costs.json', 'environment.json', 'execution-report.md', 'map-certificates.json', 'polynomial-systems.json', 'raw-result.json', 'raw-results.json', 'relation-certificates.json', 'stderr.log', 'stderr.txt', 'stdout.log', 'stdout.txt']}}

MANDATORY = ['harness/__init__.py', 'harness/finite_yaml_locked_v2.py', 'harness/finite_yaml_process_v2.py', 'src/crypto_autoresearcher/__init__.py', 'src/crypto_autoresearcher/runner.py', 'src/crypto_autoresearcher/records.py', 'orchestration/__init__.py', 'orchestration/research_budget.py', 'schemas/finite-yaml-execution-approval-v1.schema.json', 'schemas/finite-yaml-execution-plan-v1.schema.json', 'schemas/run-manifest.schema.json', 'harness/finite_yaml_locked_v3.py', 'tests/test_finite_yaml_locked_v3.py', 'tests/fixtures/finite_yaml_locked_v3/worker.py', 'tests/fixtures/finite_yaml_locked_v3/cases.json', 'experiments/EXP-ECDLP-abf981/source-v4/locked_entry.py', 'experiments/EXP-ECDLP-abf981/source-v4/planned-execution.json', 'experiments/EXP-ECDLP-abf981/source-v4/runner-integration.md', 'experiments/EXP-ECDLP-2cb7f8/source-v4/locked_entry.py', 'experiments/EXP-ECDLP-2cb7f8/source-v4/planned-execution.json', 'experiments/EXP-ECDLP-2cb7f8/source-v4/runner-integration.md', 'coordination/pending-ideas/BATCH-e9d1c7/timing-correction/timing-correction-disposition.json', 'ledger/decisions/DEC-20260909-8ccd1a.yaml']

EXPERIMENT_FILES = {'EXP-ECDLP-abf981': ['experiments/EXP-ECDLP-abf981/specification.yaml', 'experiments/EXP-ECDLP-abf981/source-v3/locked_entry.py', 'experiments/EXP-ECDLP-abf981/source-v3/planned-execution.json', 'experiments/EXP-ECDLP-abf981/source/run_model_comparison.py'], 'EXP-ECDLP-2cb7f8': ['experiments/EXP-ECDLP-2cb7f8/specification.yaml', 'experiments/EXP-ECDLP-2cb7f8/source-v3/locked_entry.py', 'experiments/EXP-ECDLP-2cb7f8/source-v3/planned-execution.json', 'experiments/EXP-ECDLP-2cb7f8/source/run.py', 'experiments/EXP-ECDLP-2cb7f8/source/group_oracle.py', 'experiments/EXP-ECDLP-2cb7f8/source/incidence.py', 'experiments/EXP-ECDLP-2cb7f8/source/presentation_inventory.py', 'ledger/decisions/DEC-20260908-195f0f.yaml']}

TEST_FILES = ['tests/test_finite_yaml_locked_v2.py', 'tests/fixtures/finite_yaml_locked_v2/worker.py', 'tests/fixtures/finite_yaml_locked_v2/cases.json', 'tools/validate_ledger.py', 'tools/research_dispatch.py']

POST_CHECKS = ['process_group_quiescent', 'commit_unchanged', 'tree_unchanged', 'approval_lock_unchanged', 'specification_unchanged', 'execution_plan_unchanged', 'protocol_hashes_unchanged']

RECEIPT_MAP = [{'datum': 'format_version', 'location': 'raw-result.json#/launch_receipt/format_version', 'rule': 'exact integer 1'}, {'datum': 'experiment_id, run_id, role', 'location': 'run.experiment_id; run.id; raw-result.json#/launch_receipt/role', 'rule': 'exact selected row; role generator for these instruments'}, {'datum': 'argv and command', 'location': 'raw-result.json#/launch_receipt/argv; command.txt; run.code.command', 'rule': 'exact array preserved; displayed command uses proper argv quoting, never space-join as authority'}, {'datum': 'inputs', 'location': 'run.inputs; raw-result.json#/launch_receipt/inputs', 'rule': 'exact config, seed, curve_id and synthetic flag; no invented scientific parameters'}, {'datum': 'timeout_seconds', 'location': 'run.protocol.timeout_seconds; raw-result.json#/launch_receipt/timeout_seconds', 'rule': 'positive finite actual process watchdog'}, {'datum': 'approval_lock_sha256, specification_sha256, execution_plan_sha256', 'location': 'run.protocol; raw-result.json#/launch_receipt', 'rule': 'raw byte hashes'}, {'datum': 'run_object_sha256, protocol_hashes_sha256', 'location': 'run.protocol; raw-result.json#/launch_receipt', 'rule': 'canonical JSON digest recipe recorded; SHA256 UTF-8 JSON sorted keys, compact separators, finite values'}, {'datum': 'approved_base_commit, launch_commit', 'location': 'run.protocol; raw-result.json#/launch_receipt; run.code.commit', 'rule': 'source/launch commit independently observed; code.commit equals launch_commit, never archive'}, {'datum': 'python_sha256 and path/version', 'location': 'run.protocol.python_sha256; environment.json#/python; raw-result.json#/launch_receipt/python', 'rule': 'normalized actual executable equals argv[0] and version/hash probe'}, {'datum': 'process_group', 'location': 'raw-result.json#/launch_receipt/process_group; run.resources', 'rule': 'wall, CPU, RSS, quiescent, direct return code, descendant policy, effective UID; source and uncertainty identified'}, {'datum': 'wrapper_postprocessing', 'location': 'run.resources.wrapper_postprocessing; raw-result.json#/launch_receipt/wrapper_postprocessing', 'rule': 'exact current schema boundary through core-artifact hashing before receipt/manifest serialization; additional finalization time disclosed separately in raw operational metrics if observed'}, {'datum': 'post_run_checks', 'location': 'run.protocol.post_run_checks; raw-result.json#/launch_receipt/post_run_checks', 'rule': 'seven required checks plus additional named authority/output/executable/schema checks in raw diagnostics'}, {'datum': 'predecessor', 'location': 'raw-result.json#/launch_receipt/predecessor', 'rule': 'null; allowed_verifier_transitions empty; no inherited predecessor receipt'}, {'datum': 'artifacts', 'location': 'run.artifacts; raw-result.json#/launch_receipt/profile_expectations', 'rule': 'manifest owns full SHA/bytes table; raw-result holds expected/missing/extra file names and already observed identities, never its own eventual hash'}, {'datum': 'native runtime and claim custody', 'location': 'run.inference; environment.json#/native_launch_receipt; raw-result.json#/launch_receipt/native_launch_receipt; raw-result.json#/launch_receipt/claim', 'rule': 'exact real observed/requested/configured/served distinction and source paths/hashes, current owner/epoch/branch/session/acquired/expiry, source authority hash'}, {'datum': 'status and validity', 'location': 'run.status; run.result.valid; run.result.invalid_reason; raw-result.json#/child_outcome; raw-result.json#/postflight_failures', 'rule': 'keep child cause and independent failure set; engineering tests assert no scientific certificate'}]

ORIGINAL_SOURCE_PINS = {'harness/runner.py': '5716c9a550bb2792f1c7597d19210d3a9e5260f008cb922e8e6261dbd9f4dbc4', 'src/crypto_autoresearcher/runner.py': '45129762b5ddc76877420addf184c53af8964f3f5e55f36ba1b9cb17df5455e3', 'src/crypto_autoresearcher/cli.py': '02ee2cd8056a0d1603b784d10ca84568f678365a0bc5f68c229c6e96eba7a630', 'src/crypto_autoresearcher/records.py': '04feb8a0d9315e69fbefce915e03a68056ee6caba9aadd6c05f80820a11faaf3', 'src/crypto_autoresearcher/__init__.py': 'fd91824b4834ee56ff9d6b37f0bf0a7e4212aba5e8cde2487eb661a0714702d4', 'schemas/experiment.schema.json': 'b96af05a2f0fe4957f58fde44d1d3fcfcd0b3bee42ee15b36cd4f9147edf9297', 'schemas/run-manifest.schema.json': '8439d35889ef84379e09f612cace5b21a2cfbc06b0cbf0e75c413b297547e12a', 'schemas/execution-approval.schema.json': '703661252453efe5cb7eb9295ba2675a30d79b76a4269627aa1311597e2e430a', 'schemas/runner-receipt.schema.json': '2da55f4b48e03a9100d9330e49415f935010eec36bf341a07a11d20e064b67c0', 'tools/validate_ledger.py': 'f5fcf23c6d2f66fff6d6d7d349a799c75cf1bdb4dafcc8e8f47eac081835ba23', 'experiments/EXP-ECDLP-abf981/source/run_model_comparison.py': '2cdb4e92b4ba204669b81db5ed9a491497e08589df9f462dd8d782719f6d3ec9', 'experiments/EXP-ECDLP-abf981/source/implementation.md': '8cf484edd7084a9f9f333d36e8e05da42b6663841fa23a4fafa8d7c4c78f0818', 'experiments/EXP-ECDLP-abf981/source/planned-execution.json': '7e50e3918196006a2db0dd2b7a853bea78beda46d27e8f912b292c0fc5c60e98', 'experiments/EXP-ECDLP-2cb7f8/source/run.py': '74620bc97614861ed7c1bcd0077e74dfe27878b7b4945eedd131adac9089085b', 'experiments/EXP-ECDLP-2cb7f8/source/group_oracle.py': '894790d400211a923fbff54fbd7ac2abae8a690bccff48511e9171afe30a38af', 'experiments/EXP-ECDLP-2cb7f8/source/incidence.py': 'f40712ee902a7405e4dbbe0264323347cd761bbaa7b10812bac8a7bfc02f5470', 'experiments/EXP-ECDLP-2cb7f8/source/presentation_inventory.py': '416fba25e8b2b057f50ea7955c31b62a10fe49a6b5e7ece8084a645583415d25', 'experiments/EXP-ECDLP-2cb7f8/source/implementation.md': 'e2b3396f36f61227abcb815c2c303bd1bc7d621008c8d6416ca47fad7f1c2275', 'experiments/EXP-ECDLP-2cb7f8/source/primary-sources.json': '23a4919c1729deab063e9203453459333485e9bd3b455db35a3833a3613d3559', 'experiments/EXP-ECDLP-2cb7f8/source/proof-obligations.md': '623c4a8e2a504455d0a665ecf1ee3e74fa066a1f18d879d40730cce4e3c62bc0', 'experiments/EXP-ECDLP-2cb7f8/source/execution-plan-candidate.json': '0adfbcf86795094e56528d2a1b6fb02874b9fc74a95a78b7eb8916ba2c10a4a8', 'harness/finite_yaml_locked_v1.py': 'd0ae29cd9074bb0b055ca6459258e9639a45b0806e62e321ec0e6def1cac1c39', 'schemas/finite-yaml-lock-v1.schema.json': 'cacd957dd79d45b63e9374ebe2d4209da2e94485282df58b097a9a2313ef5fb4', 'experiments/EXP-ECDLP-abf981/source-v2/locked_entry.py': '2212a16d3b7d9be3ca3578b8527858f1a613c1beef9b673eedaf766b8026c86f', 'experiments/EXP-ECDLP-abf981/source-v2/runner-integration.md': '14090196384a2f6d4375e51b2516724ac473655788c7900fd5a9d925e0cba340', 'experiments/EXP-ECDLP-abf981/source-v2/planned-execution.json': 'f28dd245c7ed5bda3f6ab8aad72f2dd727f85852c0fb6b14189097aa5bd2234e', 'experiments/EXP-ECDLP-2cb7f8/source-v2/locked_entry.py': '79c6dbec4f44661f594642668df3c01f25c45f5d56a61537656ecc4e588de76e', 'experiments/EXP-ECDLP-2cb7f8/source-v2/runner-integration.md': '01ba3139d66fcc1be0e1abafa044ca53dcfa2fe01ceffe7910ae595866cb2225', 'experiments/EXP-ECDLP-2cb7f8/source-v2/planned-execution.json': 'f5657f7d45bf43f333b6532cb6321f69008bc2e1f5af9732b312d657b784ef50', 'orchestration/research_budget.py': '11a6360777bdf2c0fc6403cfcb77ab7b05a99fba4b7856f785850271bdc503a0', 'experiments/EXP-ECDLP-abf981/specification.yaml': '7d9a6cccbfdaf8d9efc1d565cf437c1e833d4de964c5fdc3cd77b72e3d3dbf93', 'experiments/EXP-ECDLP-2cb7f8/specification.yaml': 'e7ea730e68d674a4de0ef6cdbc159d98ff4473a9b9539f9b18b1da52c936659e', 'ledger/decisions/DEC-20260908-195f0f.yaml': '887329e20719824c7b8dba659c532892933a32c1fde9f9d9610aa9cdff3eb455'}

CORRECTION_PATH = 'coordination/pending-ideas/BATCH-e9d1c7/timing-correction/timing-correction-disposition.json'

CORRECTION_SHA = '9a0a308776cce66a9ddbe3d39e98621c7ff15448f609fc0d9ed9c8aae3bb26a7'

CORRECTION_DECISION_PATH = 'ledger/decisions/DEC-20260909-8ccd1a.yaml'

CORRECTION_DECISION_SHA = '51bcbb3d25dff2cd565065d21c3b4123297d8e5cf72c2565f756652789fe7d93'

REQUIRED_EXCLUDED_SESSIONS = ['01a08403-33a5-7672-9ddc-3d3b48b22a0d', '01a08463-f2ad-7f61-8cca-a92c74f283a5', '01a0849e-6929-7850-80e5-63ab82d2e2df']

FINAL_TIMING_BOUNDARY = 'through-core-artifact-hashing-before-receipt-and-manifest-write'

FINAL_MEASUREMENT_ENDPOINT = 'after-final-raw-result-and-core-artifact-hashing-before-final-manifest-serialization'

PRE_RAW_BOUNDARY = 'postflight-and-existing-file-hashing-before-raw-result-serialization'

MIRROR_SCRATCH_ROOT = 'coordination/pending-ideas/BATCH-e9d1c7/timing-correction/qa/scratch'

if __name__ == "__main__":
    raise SystemExit(main())
