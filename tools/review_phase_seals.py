"""Prospective sealed-then-unblind review consistency checks.

This validates declared chronology and actual file bytes. It cannot prove that
an undeclared read did not happen or authenticate the actor recording a seal.
Old plans do not opt in merely by describing phases in prose.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath

import yaml

SCHEMA = "sealed-blind-review/v1"
CONTRACT_KEYS = {"schema", "plan_path", "phase1_allowed", "phase2_allowed",
                 "derivation_path", "seal_path", "release_path"}
SEAL_KEYS = {"schema", "task_id", "recorded_at", "plan_sha256",
             "derivation_path", "derivation_sha256"}


class InvalidPhase(ValueError):
    pass


class UniqueSafeLoader(yaml.SafeLoader):
    """New phased plans never resolve duplicate keys by choosing a winner."""


def _unique_mapping(loader, node):
    loader.flatten_mapping(node)
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=True)
        _require(key not in result, f"duplicate YAML key: {key}")
        result[key] = loader.construct_object(value_node, deep=True)
    return result


UniqueSafeLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _unique_mapping)


def load_phase_yaml(content):
    return yaml.load(content, Loader=UniqueSafeLoader)


def _same_tree(left, right):
    """Equality preserving scalar types (Python otherwise equates True and 1)."""
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return (len(left) == len(right) and all(isinstance(k, str) and k in right
                and _same_tree(v, right[k]) for k, v in left.items()))
    if isinstance(left, list):
        return len(left) == len(right) and all(_same_tree(a, b) for a, b in zip(left, right))
    return type(left) in (str, int, float, bool, type(None)) and left == right


def _require(condition, message):
    if not condition:
        raise InvalidPhase(message)


def _time(value, label):
    _require(isinstance(value, str), f"{label} must be an aware UTC timestamp")
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise InvalidPhase(f"{label} must be an aware UTC timestamp") from error
    _require(result.tzinfo is not None and result.utcoffset() == timedelta(0),
             f"{label} must be an aware UTC timestamp")
    _require(result <= datetime.now(timezone.utc),
             f"{label} is in the future relative to the checking host's UTC clock")
    return result


def _path(root, value):
    _require(isinstance(value, str) and value and value == value.strip()
             and "\\" not in value, "paths must be nonempty repository-relative POSIX paths")
    parts = PurePosixPath(value)
    _require(not parts.is_absolute() and ".." not in parts.parts
             and str(parts) != ".", f"unsafe repository path: {value!r}")
    try:
        result = (root / value).resolve()
    except (OSError, RuntimeError) as error:
        raise InvalidPhase(f"cannot resolve repository path: {value!r}") from error
    _require(result.is_relative_to(root), f"path escapes repository: {value!r}")
    return result


def _paths(root, values, label):
    _require(isinstance(values, list) and values, f"{label} must be a nonempty path list")
    result = [_path(root, item) for item in values]
    _require(len(result) == len(set(result)), f"{label} contains duplicate paths")
    return result


def _covered(path, allowed):
    return any(path == parent or path.is_relative_to(parent) for parent in allowed)


def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        _require(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _json(path):
    result = json.loads(path.read_text(), object_pairs_hook=_unique_object)
    _require(isinstance(result, dict), f"{path.name} must contain an object")
    return result


def _plan_of(document):
    if not isinstance(document, dict):
        return None
    for location in (document, document.get("handoff", {})):
        if isinstance(location, dict):
            for key in ("review_plan", "read_plan"):
                if isinstance(location.get(key), dict):
                    return location[key]
    return None


def check_sealed_phases(plan, attestation, root):
    """Return consistency errors; a nonempty result never permits blind reads.

    Contract and evidence have deliberately small, versioned, exact schemas.
    A changed/composed plan requires a new prospective plan file and seal.
    """
    try:
        _check(plan, attestation, Path(root).resolve())
    except (InvalidPhase, OSError, ValueError, TypeError, yaml.YAMLError) as error:
        return [f"sealed review: {error}"]
    return []


def _check(plan, attestation, root):
    blind = plan["blind_rederivation"]
    contract = blind["phased_release"]
    _require(isinstance(contract, dict) and set(contract) == CONTRACT_KEYS,
             "phased_release has missing or unknown contract fields")
    _require(contract["schema"] == SCHEMA, "unknown phased_release schema")
    task = blind.get("assigned_to")
    _require(blind.get("required") is True and attestation.get("task_id") == task,
             "phase contract requires the assigned required blind re-deriver")
    names = ("plan_path", "derivation_path", "seal_path", "release_path")
    paths = {key: _path(root, contract[key]) for key in names}
    _require(len(set(paths.values())) == len(paths), "phase artifact paths must be distinct")
    # Bind the plan actually checked, not merely an arbitrary file hash supplied
    # by the report. Addendum composition cannot introduce a retrospective lift.
    on_disk = _plan_of(load_phase_yaml(paths["plan_path"].read_text()))
    _require(_same_tree(on_disk, plan), "checked plan differs from the bound prospective plan file")
    plan_time = _time(plan.get("recorded_at"), "plan.recorded_at")
    allowed1 = _paths(root, contract["phase1_allowed"], "phase1_allowed")
    allowed2 = _paths(root, contract["phase2_allowed"], "phase2_allowed")
    protected = _paths(root, blind.get("blind_from"), "blind_from")
    _require(not any(_covered(p, [a]) or _covered(a, [p])
                     for p in protected for a in allowed1),
             "phase1_allowed overlaps a protected blind_from path")
    _require(not _covered(paths["derivation_path"], protected),
             "blind derivation must not itself be a protected source")

    derivation = _json(paths["derivation_path"])
    _require(derivation.get("task_id") == task, "derivation task_id mismatch")
    _require(isinstance(derivation.get("quantities"), dict) and derivation["quantities"],
             "blind derivation must contain nonempty quantities")
    generated = _time(derivation.get("generated_at"), "derivation.generated_at")
    blind_reads = _paths(root, derivation.get("sources_read"), "derivation.sources_read")
    plan_hash = _sha(paths["plan_path"])
    derivation_hash = _sha(paths["derivation_path"])
    boundaries = {}
    for name in ("seal", "release"):
        record = _json(paths[f"{name}_path"])
        keys = SEAL_KEYS | ({"seal_path", "seal_sha256"} if name == "release" else set())
        _require(set(record) == keys and record.get("schema") == SCHEMA,
                 f"{name} has missing, unknown or invalid schema fields")
        _require(record.get("task_id") == task, f"{name} task_id mismatch")
        _require(record.get("plan_sha256") == plan_hash, f"{name} plan hash mismatch")
        _require(_path(root, record.get("derivation_path")) == paths["derivation_path"]
                 and record.get("derivation_sha256") == derivation_hash,
                 f"{name} derivation path/hash mismatch")
        boundaries[name] = _time(record.get("recorded_at"), f"{name}.recorded_at")
        if name == "release":
            _require(_path(root, record.get("seal_path")) == paths["seal_path"]
                     and record.get("seal_sha256") == _sha(paths["seal_path"]),
                     "release seal path/hash mismatch")
    _require(plan_time < generated < boundaries["seal"] < boundaries["release"],
             "require plan < derivation < seal < unblind release")

    phase = attestation.get("phased_release")
    _require(isinstance(phase, dict) and set(phase) == {"schema", "events"}
             and phase.get("schema") == SCHEMA, "missing or unknown attested phase schema")
    events = phase.get("events")
    _require(isinstance(events, list) and events, "missing complete read/boundary timeline")
    seen = {"seal": 0, "unblind": 0}
    all_reads, phase1_reads = set(), set()
    previous = plan_time
    stage = 1
    for index, event in enumerate(events, 1):
        _require(isinstance(event, dict), "timeline event must be an object")
        kind = event.get("kind")
        _require(kind in {"read", "seal", "unblind"}, "unknown timeline event kind")
        keys = {"seq", "kind", "at"} | ({"source"} if kind == "read" else {"artifact", "sha256"})
        _require(set(event) == keys and type(event.get("seq")) is int and event["seq"] == index,
                 "timeline must have exact event fields and contiguous unique seq1..N")
        moment = _time(event.get("at"), f"event{index}.at")
        _require(moment >= previous, "timeline timestamps are disordered")
        previous = moment
        if kind == "read":
            source = _path(root, event.get("source"))
            _require(source.is_file(), f"read source is not an existing file: {event.get('source')}")
            all_reads.add(source)
            if stage == 1:
                _require(moment < generated and moment < boundaries["seal"],
                         "phase1 read occurs after derivation or seal")
                _require(source.stat().st_nlink == 1,
                         "multiply linked phase1 input could alias a protected source")
                _require(_covered(source, allowed1) and not _covered(source, protected),
                         f"protected or unauthorized pre-seal read: {event.get('source')}")
                phase1_reads.add(source)
            else:
                _require(stage == 3 and moment > boundaries["release"],
                         "read occurs before unblind release or at its boundary")
                _require(_covered(source, allowed2),
                         f"post-unblind read outside phase2_allowed: {event.get('source')}")
        else:
            name = "seal" if kind == "seal" else "release"
            expected_stage = 1 if kind == "seal" else 2
            _require(stage == expected_stage, "duplicate or disordered seal/unblind event")
            _require(moment == boundaries[name]
                     and _path(root, event.get("artifact")) == paths[f"{name}_path"]
                     and event.get("sha256") == _sha(paths[f"{name}_path"]),
                     f"{kind} event timestamp/path/hash mismatch")
            seen[kind] += 1
            stage += 1
    _require(seen == {"seal": 1, "unblind": 1}, "require exactly one seal and unblind event")
    _require(phase1_reads == set(blind_reads), "phase1 read coverage differs from sealed derivation")
    reported_reads = _paths(root, attestation.get("sources_read"), "attestation.sources_read")
    _require(all_reads == set(reported_reads), "timeline read coverage differs from sources_read")
    _require(attestation.get("blind_from_respected") is True,
             "blind_from_respected must explicitly attest phase1 blindness")
