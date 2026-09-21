#!/usr/bin/env python3
"""Compile deterministic, non-authorizing history indexes for RECON-20260802-001.

All semantic inputs are read from immutable Git objects.  In particular, the
contract commit and digest below are code constants rather than CLI options;
candidate-side copies cannot redefine the trust anchor.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Iterator, Sequence

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


RECONCILIATION_ID = "RECON-20260802-001"
TASK_ID = "TASK-20260803-003"
SNAPSHOT_COMMIT = "171f33f451bb643a27aceaa1aaa6c0972e1db9f0"
SNAPSHOT_PARENT = "939c71dbd364b7f690cb1518c0980fadbe149c61"
CONTRACT_PATH = (
    "coordination/reconciliation/RECON-20260802-001/tasks/"
    "TASK-20260803-001/source_adjudication_contract.yaml"
)
CONTRACT_SHA256 = "a22453cecbd5c5f787bc8fcc0314e353e090f3135fdcc1368bd8da82398bfd2f"
INVENTORY_PATH = (
    "coordination/reconciliation/RECON-20260802-001/"
    "reported_conflict_inventory.draft.yaml"
)
SUCCESSOR_PATH = (
    "coordination/reconciliation/RECON-20260802-001/tasks/"
    "TASK-20260802-950/successor_map.yaml"
)
PHASE_PATH = (
    "coordination/reconciliation/RECON-20260802-001/tasks/"
    "TASK-20260802-991/generated_artifact_phase_table.yaml"
)
PARENT_COMMITS = {
    "local": "a9664afbf72d2dc6ff297b7a67fc517e601fff49",
    "reanchor": "717d932c2765469f381bb182c6905c66c35e2e42",
}
PRESERVATION_ROOTS = {
    "local": "coordination/reconciliation/RECON-20260802-001/variants/local-a9664afb",
    "reanchor": "coordination/reconciliation/RECON-20260802-001/variants/reanchor-717d932c",
}
BATCHES = tuple(f"BATCH-{number:03d}" for number in range(20, 25))
GENERATED_FILENAMES = ("dispatch_queue.json", "dispatch_plan.json", "dispatch_plan.md")
QUEUE_SCHEMA = "crypto.autoresearch.reconciliation_history_index.v1"
VIEW_SCHEMA = "crypto.autoresearch.reconciliation_history_view.v1"
SOURCE_TABLE_SCHEMA = "crypto.autoresearch.reconciliation_source_occurrences.v1"
REFERENCE_TABLE_SCHEMA = "crypto.autoresearch.reconciliation_reference_occurrences.v1"
AUTHORITY_CODE = "NONAUT"
EXPECTED_CONTRACT_CONTROL_HASHES = {
    INVENTORY_PATH: "9db75a9ea2e27a611ed8926a2a9a8997c1abd394e03f0691ecd85aad619e989e",
    SUCCESSOR_PATH: "62ba7f84d3577545af4386aa51f9c6152196b4f5de939c23fd7d4decf53e9c08",
    PHASE_PATH: "3ebe802526b358a8cbb84910b658b31ba1ebc5334f6647a0b175fdd8a51101c6",
}


class HistoryCompilerError(ValueError):
    """Fail-closed compiler error carrying a stable machine-readable code."""

    def __init__(self, code: str, detail: str):
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


def _fail(code: str, detail: str) -> None:
    raise HistoryCompilerError(code, detail)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")


def pretty_json(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode(
        "ascii"
    )


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _safe_relative(path: str, location: str) -> str:
    if not isinstance(path, str) or not path or path != path.strip():
        _fail("PATH_INVALID", f"{location} is not nonempty canonical text")
    candidate = PurePosixPath(path)
    if (
        candidate.is_absolute()
        or ".." in candidate.parts
        or candidate.as_posix() != path
        or path.startswith("./")
        or any(char in path for char in ("\x00", "\n", "\r", "\t"))
    ):
        _fail("PATH_INVALID", f"{location} is not a safe repository-relative path: {path!r}")
    return path


class GitObjects:
    """Read immutable objects from one repository without consulting worktree files."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root.resolve()

    def run(self, arguments: Sequence[str], *, allow_failure: bool = False) -> bytes | None:
        try:
            result = subprocess.run(
                ["git", "-C", str(self.repo_root), *arguments],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
        except OSError as error:
            _fail("GIT_UNAVAILABLE", str(error))
        if result.returncode:
            if allow_failure:
                return None
            detail = result.stderr.decode("utf-8", "replace").strip()
            _fail("GIT_OBJECT_UNAVAILABLE", f"{' '.join(arguments)}: {detail}")
        return result.stdout

    def resolve_commit(self, reference: str) -> str:
        raw = self.run(["rev-parse", "--verify", f"{reference}^{{commit}}"])
        assert raw is not None
        return raw.decode("ascii").strip()

    def parents(self, commit: str) -> list[str]:
        raw = self.run(["show", "-s", "--format=%P", commit])
        assert raw is not None
        return raw.decode("ascii").split()

    def object_type(self, commit: str, path: str) -> str | None:
        raw = self.run(["cat-file", "-t", f"{commit}:{path}"], allow_failure=True)
        return None if raw is None else raw.decode("ascii").strip()

    def blob_id(self, commit: str, path: str) -> str | None:
        raw = self.run(["rev-parse", "--verify", f"{commit}:{path}"], allow_failure=True)
        return None if raw is None else raw.decode("ascii").strip()

    def blob(self, commit: str, path: str) -> bytes:
        if self.object_type(commit, path) != "blob":
            _fail("PARENT_OBJECT_TYPE_INVALID", f"{commit}:{path} is not a regular Git blob")
        raw = self.run(["cat-file", "blob", f"{commit}:{path}"])
        assert raw is not None
        return raw

    def changed_paths(self, commit: str) -> list[str]:
        raw = self.run(
            ["diff-tree", "--no-commit-id", "--no-renames", "--name-only", "-r", "--root", "-z", commit]
        )
        assert raw is not None
        return [item.decode("utf-8", "surrogateescape") for item in raw.split(b"\0") if item]

    def is_ancestor(self, commit: str, descendant: str) -> bool:
        raw = self.run(["merge-base", "--is-ancestor", commit, descendant], allow_failure=True)
        return raw is not None


def _load_yaml_bytes(raw: bytes, location: str) -> dict[str, Any]:
    if yaml is None:
        _fail("YAML_UNAVAILABLE", "PyYAML is required")
    try:
        value = yaml.safe_load(raw)
    except yaml.YAMLError as error:
        _fail("BOUND_INPUT_INVALID", f"{location}: {error}")
    if not isinstance(value, dict):
        _fail("BOUND_INPUT_INVALID", f"{location} is not a mapping")
    return value


def validate_contract_bytes(raw: bytes) -> dict[str, Any]:
    """Validate the hard-coded external trust anchor before parsing semantics."""

    observed = sha256_bytes(raw)
    if observed != CONTRACT_SHA256:
        _fail(
            "IMMUTABLE_BINDING_MISMATCH",
            f"contract SHA-256 expected {CONTRACT_SHA256}, observed {observed}",
        )
    contract = _load_yaml_bytes(raw, CONTRACT_PATH)
    if contract.get("schema") != "crypto.autoresearch.reconciliation_source_adjudication_contract.v1":
        _fail("CONTRACT_SCHEMA_MISMATCH", str(contract.get("schema")))
    if contract.get("id") != "RECON-20260802-001-SOURCE-CONTRACT-002":
        _fail("CONTRACT_ID_MISMATCH", str(contract.get("id")))
    for field in ("authoritative_research_evidence", "candidate_materialization_authorized", "merge_authorized"):
        if contract.get(field) is not False:
            _fail("CONTRACT_AUTHORITY_MISMATCH", field)
    immutable = contract.get("immutable_inputs")
    if not isinstance(immutable, dict) or immutable.get("parent_commits") != PARENT_COMMITS:
        _fail("CONTRACT_PARENT_MISMATCH", "parent commits")
    if immutable.get("preservation_roots") != PRESERVATION_ROOTS:
        _fail("CONTRACT_ROOT_MISMATCH", "preservation roots")
    controls = immutable.get("control_documents")
    if not isinstance(controls, dict):
        _fail("CONTRACT_CONTROL_MISMATCH", "missing control_documents")
    expected_fields = {
        "inventory": INVENTORY_PATH,
        "successor_map": SUCCESSOR_PATH,
        "prior_phase_table": PHASE_PATH,
    }
    for field, path in expected_fields.items():
        entry = controls.get(field)
        if not isinstance(entry, dict) or entry.get("path") != path or entry.get("sha256") != EXPECTED_CONTRACT_CONTROL_HASHES[path]:
            _fail("CONTRACT_CONTROL_MISMATCH", field)
    enforcement = contract.get("research_dispatch_enforcement")
    if not isinstance(enforcement, dict) or enforcement.get("failure_code") != "POLICY_NONAUTHORITATIVE":
        _fail("CONTRACT_AUTHORITY_MISMATCH", "dispatcher failure code")
    return contract


def load_bound_inputs(store: GitObjects) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    if store.resolve_commit(SNAPSHOT_COMMIT) != SNAPSHOT_COMMIT:
        _fail("SNAPSHOT_COMMIT_MISMATCH", SNAPSHOT_COMMIT)
    if store.parents(SNAPSHOT_COMMIT) != [SNAPSHOT_PARENT]:
        _fail("SNAPSHOT_PARENT_MISMATCH", repr(store.parents(SNAPSHOT_COMMIT)))
    contract = validate_contract_bytes(store.blob(SNAPSHOT_COMMIT, CONTRACT_PATH))
    values: list[dict[str, Any]] = []
    for path in (INVENTORY_PATH, SUCCESSOR_PATH, PHASE_PATH):
        raw = store.blob(SNAPSHOT_COMMIT, path)
        if sha256_bytes(raw) != EXPECTED_CONTRACT_CONTROL_HASHES[path]:
            _fail("CONTROL_DOCUMENT_BINDING_MISMATCH", path)
        values.append(_load_yaml_bytes(raw, path))
    inventory, successor, phase = values
    heads = inventory.get("heads", {})
    if heads.get("local_ecdlp", {}).get("commit") != PARENT_COMMITS["local"] or heads.get("audited_reanchor", {}).get("commit") != PARENT_COMMITS["reanchor"]:
        _fail("INVENTORY_PARENT_MISMATCH", "inventory heads")
    return contract, inventory, successor, phase


def _generated_path(batch: str, filename: str) -> str:
    return f"coordination/goals/GOAL-ECDLP-001/batches/{batch}/{filename}"


def _task_digest(task: dict[str, Any]) -> str:
    return sha256_bytes(canonical_bytes(task))


def _verify_archive(
    store: GitObjects,
    source_parent: str,
    task: dict[str, Any],
    queue_tasks: dict[str, dict[str, Any]],
) -> tuple[str, bool | None]:
    archive = task.get("archive")
    if not isinstance(archive, dict):
        return "not_archive", None
    commit = archive.get("commit_sha")
    if commit is None:
        if archive.get("parent_sha") is not None or archive.get("path_sha256") not in ({}, None):
            _fail("ARCHIVE_UNBOUND_FIELDS_INVALID", task.get("id", "unknown"))
        return "historical_unbound", None
    if not isinstance(commit, str):
        _fail("ARCHIVE_COMMIT_INVALID", str(task.get("id")))
    resolved = store.resolve_commit(commit)
    source_history_reachable = store.is_ancestor(resolved, source_parent)
    parents = store.parents(resolved)
    declared_parent = archive.get("parent_sha")
    if not parents or not isinstance(declared_parent, str) or store.resolve_commit(declared_parent) != parents[0]:
        _fail("ARCHIVE_PARENT_MISMATCH", str(task.get("id")))
    source_ids = archive.get("source_task_ids")
    if not isinstance(source_ids, list) or not all(source_id in queue_tasks for source_id in source_ids):
        _fail("ARCHIVE_SOURCE_SET_INVALID", str(task.get("id")))
    expected_paths = set(task.get("artifact_paths", []))
    for source_id in source_ids:
        expected_paths.update(queue_tasks[source_id].get("artifact_paths", []))
    actual_paths = store.changed_paths(resolved)
    if len(actual_paths) != len(set(actual_paths)) or set(actual_paths) != expected_paths:
        _fail("ARCHIVE_PATH_SET_MISMATCH", str(task.get("id")))
    hashes = archive.get("path_sha256")
    if not isinstance(hashes, dict) or set(hashes) != expected_paths:
        _fail("ARCHIVE_HASH_SET_MISMATCH", str(task.get("id")))
    for path in sorted(expected_paths):
        _safe_relative(path, f"archive {task.get('id')}")
        content = store.blob(resolved, path)
        if sha256_bytes(content) != hashes[path]:
            _fail("ARCHIVE_PATH_HASH_MISMATCH", f"{task.get('id')}:{path}")
    return "historical_hash_bound", source_history_reachable


def _successor_reference(side: str, task_id: str, successor: dict[str, Any]) -> dict[str, Any]:
    mappings = successor.get("local_semantic_remaps", {}).get("task_lineage", {})
    successor_id = mappings.get(task_id) if side == "local" else None
    return {
        "successor_id": successor_id,
        "mapping_status": "proposed" if successor_id else "none",
        "successor_state": None,
        "fresh_handoff_present": False,
        "completion_or_receipt_inherited": False,
    }


def build_source_occurrence_table(
    store: GitObjects,
    contract: dict[str, Any],
    successor: dict[str, Any],
) -> tuple[dict[str, Any], dict[tuple[str, str], dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    queue_documents: dict[tuple[str, str], dict[str, Any]] = {}
    queue_blobs = contract["immutable_inputs"]["queue_blobs"]
    for side in ("local", "reanchor"):
        parent = PARENT_COMMITS[side]
        for batch in BATCHES:
            path = _generated_path(batch, "dispatch_queue.json")
            observed_blob = store.blob_id(parent, path)
            expected_blob = queue_blobs[batch][side]
            if observed_blob != expected_blob:
                _fail("SOURCE_QUEUE_BLOB_MISMATCH", f"{side}:{batch}")
            raw = store.blob(parent, path)
            try:
                queue = json.loads(raw)
            except json.JSONDecodeError as error:
                _fail("SOURCE_QUEUE_INVALID", f"{side}:{batch}:{error}")
            if not isinstance(queue, dict) or not isinstance(queue.get("tasks"), list):
                _fail("SOURCE_QUEUE_INVALID", f"{side}:{batch}:tasks")
            queue_documents[(side, batch)] = queue
            by_id = {task.get("id"): task for task in queue["tasks"] if isinstance(task, dict)}
            if len(by_id) != len(queue["tasks"]):
                _fail("SOURCE_TASK_ID_DUPLICATE", f"{side}:{batch}")
            for ordinal, task in enumerate(queue["tasks"]):
                if not isinstance(task, dict) or not isinstance(task.get("id"), str) or not isinstance(task.get("state"), str):
                    _fail("SOURCE_TASK_INVALID", f"{side}:{batch}:{ordinal}")
                archive_status, archive_reachable = _verify_archive(
                    store, parent, task, by_id
                )
                rows.append(
                    {
                        "side": side,
                        "batch": batch,
                        "ordinal": ordinal,
                        "source_task_id": task["id"],
                        "source_state": task["state"],
                        "source_queue_blob": expected_blob,
                        "source_task_canonical_sha256": _task_digest(task),
                        "identity_class": None,
                        "source_bytes_disposition": "preserve_verbatim_in_variant",
                        "historical_state_disposition": "preserve_exactly_in_occurrence_ledger",
                        "dispatch_authority": AUTHORITY_CODE,
                        "successor_reference": _successor_reference(side, task["id"], successor),
                        "archive_binding": archive_status,
                        "archive_source_history_reachable": archive_reachable,
                    }
                )
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["source_task_id"]].append(row)
    identity_counts = Counter()
    for task_id, occurrences in grouped.items():
        if len(occurrences) == 1:
            classification = "unique"
        elif len(occurrences) == 2:
            digests = {row["source_task_canonical_sha256"] for row in occurrences}
            classification = "shared_identical" if len(digests) == 1 else "shared_conflicting"
        else:
            _fail("IDENTITY_MULTIPLICITY_INVALID", task_id)
        identity_counts[classification] += 1
        for row in occurrences:
            row["identity_class"] = classification
    table = {
        "schema": SOURCE_TABLE_SCHEMA,
        "reconciliation_id": RECONCILIATION_ID,
        "task_id": TASK_ID,
        "authority": _authority_envelope(),
        "summary": {
            "row_count": len(rows),
            "original_id_count": len(grouped),
            "state_counts": dict(sorted(Counter(row["source_state"] for row in rows).items())),
            "identity_id_counts": dict(sorted(identity_counts.items())),
            "archive_entry_count": sum(row["archive_binding"] != "not_archive" for row in rows),
            "archive_hash_bound_count": sum(row["archive_binding"] == "historical_hash_bound" for row in rows),
            "archive_unbound_count": sum(row["archive_binding"] == "historical_unbound" for row in rows),
            "archive_source_history_unreachable_count": sum(
                row["archive_binding"] == "historical_hash_bound"
                and row["archive_source_history_reachable"] is False
                for row in rows
            ),
        },
        "rows": rows,
    }
    validate_source_occurrence_table(table, contract)
    return table, queue_documents


def _expected_group_order(contract: dict[str, Any], side: str, batch: str) -> list[str]:
    groups = contract["source_occurrence_table"]["exact_group_census"]
    entry = next(item for item in groups if item["side"] == side and item["batch"] == batch)
    if "exact_order" in entry:
        return entry["exact_order"]
    first = int(entry["first"].rsplit("-", 1)[1])
    last = int(entry["last"].rsplit("-", 1)[1])
    prefix = entry["first"].rsplit("-", 1)[0]
    return [f"{prefix}-{number:03d}" for number in range(first, last + 1)]


def validate_source_occurrence_table(table: dict[str, Any], contract: dict[str, Any]) -> None:
    if table.get("schema") != SOURCE_TABLE_SCHEMA or table.get("authority") != _authority_envelope():
        _fail("SOURCE_TABLE_ENVELOPE_MISMATCH", "schema or authority")
    rows = table.get("rows")
    if not isinstance(rows, list) or len(rows) != contract["source_occurrence_table"]["expected_rows"]:
        _fail("SOURCE_OCCURRENCE_COUNT_MISMATCH", str(len(rows) if isinstance(rows, list) else None))
    keys = []
    for row in rows:
        if not isinstance(row, dict):
            _fail("SOURCE_OCCURRENCE_ROW_INVALID", "non-object")
        key = tuple(row.get(field) for field in ("side", "batch", "ordinal", "source_task_id"))
        keys.append(key)
        if row.get("dispatch_authority") != AUTHORITY_CODE or row.get("source_bytes_disposition") != "preserve_verbatim_in_variant":
            _fail("SOURCE_OCCURRENCE_DISPOSITION_MISMATCH", repr(key))
        reference = row.get("successor_reference")
        if not isinstance(reference, dict) or reference.get("completion_or_receipt_inherited") is not False:
            _fail("COPIED_COMPLETION_FORBIDDEN", repr(key))
    if len(keys) != len(set(keys)):
        _fail("SOURCE_OCCURRENCE_DUPLICATE", "row key")
    for side in ("local", "reanchor"):
        for batch in BATCHES:
            group = [row for row in rows if row.get("side") == side and row.get("batch") == batch]
            expected_ids = _expected_group_order(contract, side, batch)
            if [row.get("ordinal") for row in group] != list(range(len(group))) or [row.get("source_task_id") for row in group] != expected_ids:
                _fail("SOURCE_OCCURRENCE_ORDER_MISMATCH", f"{side}:{batch}")
            expected_entry = next(item for item in contract["source_occurrence_table"]["exact_group_census"] if item["side"] == side and item["batch"] == batch)
            if len(group) != expected_entry["rows"] or dict(Counter(row["source_state"] for row in group)) != expected_entry["states"]:
                _fail("SOURCE_OCCURRENCE_STATE_MISMATCH", f"{side}:{batch}")
    ids: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        ids[row["source_task_id"]].append(row)
    classifications = Counter()
    for task_id, group in ids.items():
        values = {row["identity_class"] for row in group}
        if len(values) != 1:
            _fail("IDENTITY_CLASSIFICATION_MISMATCH", task_id)
        classification = next(iter(values))
        classifications[classification] += 1
        digests = {row["source_task_canonical_sha256"] for row in group}
        expected = "unique" if len(group) == 1 else ("shared_identical" if len(digests) == 1 else "shared_conflicting")
        if classification != expected:
            _fail("IDENTITY_CLASSIFICATION_MISMATCH", task_id)
    exact = contract["identity_classification"]["expected"]
    observed = {
        "unique_ids": classifications["unique"],
        "shared_identical_ids": classifications["shared_identical"],
        "shared_conflicting_ids": classifications["shared_conflicting"],
    }
    if observed != exact or set(ids) and len(ids) != contract["source_occurrence_table"]["expected_original_ids"]:
        _fail("IDENTITY_CENSUS_MISMATCH", repr(observed))
    if {row["source_task_id"] for row in rows if row["identity_class"] == "shared_identical"} != {"TASK-20260731-043"}:
        _fail("TASK_043_EQUIVALENCE_MISMATCH", "shared identical set")
    expected_conflicts = set(contract["identity_classification"]["shared_conflicting"]["exact_ids"])
    if {row["source_task_id"] for row in rows if row["identity_class"] == "shared_conflicting"} != expected_conflicts:
        _fail("SHARED_CONFLICT_SET_MISMATCH", "exact IDs")
    expected_states = contract["source_occurrence_table"]["expected_state_totals"]
    if dict(Counter(row["source_state"] for row in rows)) != expected_states:
        _fail("SOURCE_OCCURRENCE_STATE_MISMATCH", "combined")
    if sum(row["archive_binding"] != "not_archive" for row in rows) != 44 or sum(row["archive_binding"] == "historical_hash_bound" for row in rows) != 35 or sum(row["archive_binding"] == "historical_unbound" for row in rows) != 9:
        _fail("ARCHIVE_CENSUS_MISMATCH", "expected 44/35/9")


def _iter_schema_text(value: Any, path: tuple[Any, ...] = ()) -> Iterator[tuple[tuple[Any, ...], str]]:
    if isinstance(value, dict):
        for key, item in value.items():
            if isinstance(key, str):
                yield path + ("<key>",), key
            yield from _iter_schema_text(item, path + (key,))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from _iter_schema_text(item, path + (index,))
    elif isinstance(value, str):
        yield path, value


def _monitored_ids(successor: dict[str, Any], contract: dict[str, Any]) -> tuple[list[str], set[str]]:
    remaps = successor.get("local_semantic_remaps")
    if not isinstance(remaps, dict):
        _fail("MONITORED_ID_SET_MISMATCH", "missing local_semantic_remaps")
    ids: list[str] = []
    for value in remaps.values():
        if isinstance(value, dict):
            ids.extend(value.keys())
    if len(ids) != 33 or len(set(ids)) != 33:
        _fail("MONITORED_ID_SET_MISMATCH", f"expected 33 unique keys, observed {len(ids)}/{len(set(ids))}")
    additional = contract["reference_occurrence_policy"]["additional_historical_ids"]
    all_ids = ids + list(additional)
    if len(all_ids) != len(set(all_ids)):
        _fail("MONITORED_ID_SET_MISMATCH", "duplicate additional ID")
    return all_ids, set(additional)


def _reference_disposition(reference_id: str, additional: set[str]) -> str:
    if reference_id in additional:
        return "preserve_verbatim_and_classify_by_side_no_live_dereference"
    return "preserve_verbatim_and_side_qualify_in_index"


def build_reference_occurrence_table(
    store: GitObjects,
    contract: dict[str, Any],
    inventory: dict[str, Any],
    successor: dict[str, Any],
) -> dict[str, Any]:
    monitored, additional = _monitored_ids(successor, contract)
    conflict_blobs = {
        row["path"]: row
        for row in inventory.get("conflicts", [])
        if isinstance(row, dict) and row.get("class") == "dispatch_artifact_collision"
    }
    rows: list[dict[str, Any]] = []
    path_counts: dict[tuple[str, str], int] = {}
    for side in ("local", "reanchor"):
        parent = PARENT_COMMITS[side]
        for batch in BATCHES:
            for filename in GENERATED_FILENAMES:
                path = _generated_path(batch, filename)
                expected_blob = conflict_blobs.get(path, {}).get(f"{side}_blob")
                if not expected_blob or store.blob_id(parent, path) != expected_blob:
                    _fail("GENERATED_PARENT_BLOB_MISMATCH", f"{side}:{path}")
                raw = store.blob(parent, path)
                try:
                    text = raw.decode("utf-8")
                except UnicodeDecodeError as error:
                    _fail("GENERATED_UTF8_INVALID", f"{side}:{path}:{error}")
                raw_counts = Counter({identifier: text.count(identifier) for identifier in monitored})
                raw_counts = +raw_counts
                schema_counts: Counter[str] = Counter()
                locations: dict[str, list[str]] = defaultdict(list)
                if filename.endswith(".json"):
                    try:
                        document = json.loads(text)
                    except json.JSONDecodeError as error:
                        _fail("GENERATED_JSON_INVALID", f"{side}:{path}:{error}")
                    for schema_path, item in _iter_schema_text(document):
                        pointer = "/" + "/".join(str(piece).replace("~", "~0").replace("/", "~1") for piece in schema_path)
                        for identifier in monitored:
                            count = item.count(identifier)
                            schema_counts[identifier] += count
                            locations[identifier].extend([pointer] * count)
                else:
                    schema_counts = raw_counts.copy()
                    for identifier, count in raw_counts.items():
                        locations[identifier] = ["<markdown-raw-text>"] * count
                if schema_counts != raw_counts:
                    _fail("REFERENCE_TRAVERSAL_RAW_MISMATCH", f"{side}:{path}")
                ordinal = 0
                per_id_seen: Counter[str] = Counter()
                matches: list[tuple[int, str]] = []
                for identifier in monitored:
                    matches.extend((match.start(), identifier) for match in re.finditer(re.escape(identifier), text))
                matches.sort(key=lambda item: (item[0], monitored.index(item[1])))
                for byte_offset, identifier in matches:
                    index = per_id_seen[identifier]
                    per_id_seen[identifier] += 1
                    rows.append(
                        {
                            "side": side,
                            "batch": batch,
                            "artifact_kind": filename,
                            "source_path": path,
                            "source_blob": expected_blob,
                            "artifact_occurrence_ordinal": ordinal,
                            "reference_id": identifier,
                            "reference_occurrence_ordinal": index,
                            "raw_utf8_offset": len(text[:byte_offset].encode("utf-8")),
                            "schema_location": locations[identifier][index],
                            "match_mode": "raw_substring_and_schema_traversal",
                            "disposition": _reference_disposition(identifier, additional),
                            "dispatch_authority": AUTHORITY_CODE,
                        }
                    )
                    ordinal += 1
                path_counts[(side, path)] = len(matches)
    table = {
        "schema": REFERENCE_TABLE_SCHEMA,
        "reconciliation_id": RECONCILIATION_ID,
        "task_id": TASK_ID,
        "authority": _authority_envelope(),
        "monitored_ids": monitored,
        "summary": {
            "row_count": len(rows),
            "queue_row_count": sum(row["artifact_kind"] == "dispatch_queue.json" for row in rows),
            "side_counts": {side: sum(row["side"] == side for row in rows) for side in ("local", "reanchor")},
            "side_queue_counts": {side: sum(row["side"] == side and row["artifact_kind"] == "dispatch_queue.json" for row in rows) for side in ("local", "reanchor")},
            "distinct_monitored_ids_present": {side: len({row["reference_id"] for row in rows if row["side"] == side}) for side in ("local", "reanchor")},
            "unclassified_count": 0,
            "multiply_classified_count": 0,
        },
        "rows": rows,
    }
    validate_reference_occurrence_table(table, contract)
    return table


def validate_reference_occurrence_table(table: dict[str, Any], contract: dict[str, Any]) -> None:
    if table.get("schema") != REFERENCE_TABLE_SCHEMA or table.get("authority") != _authority_envelope():
        _fail("REFERENCE_TABLE_ENVELOPE_MISMATCH", "schema or authority")
    rows = table.get("rows")
    if not isinstance(rows, list):
        _fail("REFERENCE_OCCURRENCE_ROW_INVALID", "rows")
    keys = []
    for row in rows:
        if not isinstance(row, dict) or row.get("dispatch_authority") != AUTHORITY_CODE:
            _fail("REFERENCE_OCCURRENCE_ROW_INVALID", repr(row))
        if row.get("disposition") not in {
            "preserve_verbatim_and_classify_by_side_no_live_dereference",
            "preserve_verbatim_and_side_qualify_in_index",
        }:
            _fail("REFERENCE_UNCLASSIFIED", str(row.get("reference_id")))
        keys.append((row.get("side"), row.get("source_path"), row.get("reference_id"), row.get("reference_occurrence_ordinal")))
    if len(keys) != len(set(keys)):
        _fail("REFERENCE_OCCURRENCE_DUPLICATE", "occurrence key")
    counts = contract["reference_occurrence_policy"]["expected_counts"]
    expected_total = counts["combined"]["all_30_generated_artifacts"]
    expected_queues = counts["combined"]["ten_queues"]
    if len(rows) != expected_total or sum(row["artifact_kind"] == "dispatch_queue.json" for row in rows) != expected_queues:
        _fail("REFERENCE_OCCURRENCE_COUNT_MISMATCH", f"{len(rows)}/{sum(row['artifact_kind'] == 'dispatch_queue.json' for row in rows)}")
    for side in ("local", "reanchor"):
        expected = counts[side]
        if sum(row["side"] == side for row in rows) != expected["all_15_generated_artifacts"] or sum(row["side"] == side and row["artifact_kind"] == "dispatch_queue.json" for row in rows) != expected["five_queues"] or len({row["reference_id"] for row in rows if row["side"] == side}) != expected["distinct_monitored_ids_present"]:
            _fail("REFERENCE_OCCURRENCE_COUNT_MISMATCH", side)


def build_preservation_mappings(
    store: GitObjects,
    contract: dict[str, Any],
    inventory: dict[str, Any],
) -> list[dict[str, Any]]:
    mappings: list[dict[str, Any]] = []
    seen_source: set[tuple[str, str]] = set()
    seen_target: set[str] = set()

    def add(side: str, path: str, blob_id: str | None) -> None:
        _safe_relative(path, "preservation source")
        source_key = (side, path)
        target = f"{PRESERVATION_ROOTS[side]}/{path}"
        _safe_relative(target, "preservation target")
        if source_key in seen_source:
            _fail("PRESERVATION_SOURCE_DUPLICATE", f"{side}:{path}")
        if target in seen_target:
            _fail("PRESERVATION_TARGET_DUPLICATE", target)
        seen_source.add(source_key)
        seen_target.add(target)
        parent = PARENT_COMMITS[side]
        observed = store.blob_id(parent, path)
        if blob_id is None:
            if observed is not None:
                _fail("PRESERVATION_ABSENCE_MISMATCH", f"{side}:{path}")
            mappings.append(
                {
                    "side": side,
                    "source_commit": parent,
                    "source_path": path,
                    "source_blob": None,
                    "source_sha256": None,
                    "target_root": PRESERVATION_ROOTS[side],
                    "target_path": target,
                    "disposition": "absence_attestation",
                }
            )
            return
        if observed != blob_id:
            _fail("PRESERVATION_BLOB_MISMATCH", f"{side}:{path}")
        content = store.blob(parent, path)
        mappings.append(
            {
                "side": side,
                "source_commit": parent,
                "source_path": path,
                "source_blob": blob_id,
                "source_sha256": sha256_bytes(content),
                "target_root": PRESERVATION_ROOTS[side],
                "target_path": target,
                "disposition": "copy_blob_verbatim",
            }
        )

    conflicts = inventory.get("conflicts")
    if not isinstance(conflicts, list) or len(conflicts) != 60:
        _fail("PRESERVATION_CONFLICT_CENSUS_MISMATCH", str(len(conflicts) if isinstance(conflicts, list) else None))
    for conflict in conflicts:
        for side in ("local", "reanchor"):
            add(side, conflict["path"], conflict[f"{side}_blob"])
    package = inventory.get("package_closure", {}).get("entries")
    if not isinstance(package, list) or len(package) != 15:
        _fail("PRESERVATION_PACKAGE_CENSUS_MISMATCH", str(len(package) if isinstance(package, list) else None))
    for entry in package:
        for side in ("local", "reanchor"):
            if (side, entry["path"]) not in seen_source:
                add(side, entry["path"], entry[f"{side}_blob"])
    expected = contract["preservation_policy"]
    if len(mappings) != expected["expected_total_mappings"] or sum(row["disposition"] == "copy_blob_verbatim" for row in mappings) != expected["expected_blob_copies"] or sum(row["disposition"] == "absence_attestation" for row in mappings) != expected["expected_absence_attestations"]:
        _fail("PRESERVATION_MAPPING_CENSUS_MISMATCH", str(len(mappings)))
    return mappings


def _authority_envelope() -> dict[str, Any]:
    return {
        "code": AUTHORITY_CODE,
        "authoritative_research_evidence": False,
        "dispatch_authority": AUTHORITY_CODE,
        "live_dispatch_semantics": "none",
        "candidate_materialization_authorized_by_contract": False,
        "merge_authorized": False,
        "contract_snapshot_commit": SNAPSHOT_COMMIT,
        "contract_sha256": CONTRACT_SHA256,
    }


def _history_outputs(
    source_table: dict[str, Any],
    reference_table: dict[str, Any],
    contract: dict[str, Any],
) -> dict[str, bytes]:
    outputs: dict[str, bytes] = {}
    for batch in BATCHES:
        occurrences = [row for row in source_table["rows"] if row["batch"] == batch]
        references = [row for row in reference_table["rows"] if row["batch"] == batch]
        source_queues = []
        for side in ("local", "reanchor"):
            path = _generated_path(batch, "dispatch_queue.json")
            blob_id = contract["immutable_inputs"]["queue_blobs"][batch][side]
            source_queues.append(
                {
                    "side": side,
                    "source_commit": PARENT_COMMITS[side],
                    "source_path": path,
                    "source_blob": blob_id,
                    "preservation_target": f"{PRESERVATION_ROOTS[side]}/{path}",
                    "dispatch_authority": AUTHORITY_CODE,
                }
            )
        index = {
            "schema": QUEUE_SCHEMA,
            "reconciliation_id": RECONCILIATION_ID,
            "batch_id": batch,
            "authority": _authority_envelope(),
            "source_queues": source_queues,
            "source_occurrence_rows": occurrences,
            "historical_state_counts": dict(sorted(Counter(row["source_state"] for row in occurrences).items())),
            "identity_id_counts": {
                classification: len({row["source_task_id"] for row in occurrences if row["identity_class"] == classification})
                for classification in ("unique", "shared_identical", "shared_conflicting")
            },
            "successor_reference_rule": "references_are_proposed_or_none; copied_receipts_never_complete_successors",
        }
        view = {
            "schema": VIEW_SCHEMA,
            "reconciliation_id": RECONCILIATION_ID,
            "batch_id": batch,
            "authority": _authority_envelope(),
            "history_index_path": _generated_path(batch, "dispatch_queue.json"),
            "source_occurrence_count": len(occurrences),
            "reference_occurrence_count": len(references),
            "historical_state_counts": index["historical_state_counts"],
            "identity_id_counts": index["identity_id_counts"],
            "source_artifacts": [
                {
                    "side": side,
                    "source_commit": PARENT_COMMITS[side],
                    "paths": [
                        {
                            "path": _generated_path(batch, filename),
                            "preservation_target": f"{PRESERVATION_ROOTS[side]}/{_generated_path(batch, filename)}",
                        }
                        for filename in GENERATED_FILENAMES
                    ],
                }
                for side in ("local", "reanchor")
            ],
        }
        markdown = [
            f"# {batch} Reconciliation History View",
            "",
            "Authority: `NONAUT` — historical index only; live dispatch semantics: none.",
            "",
            f"Contract snapshot: `{SNAPSHOT_COMMIT}`",
            f"Contract SHA-256: `{CONTRACT_SHA256}`",
            "",
            "| Side | Source commit | Historical rows |",
            "|---|---|---:|",
        ]
        for side in ("local", "reanchor"):
            markdown.append(f"| {side} | `{PARENT_COMMITS[side]}` | {sum(row['side'] == side for row in occurrences)} |")
        markdown.extend(
            [
                "",
                "Historical states are reproduced as provenance only. They do not imply readiness, completion, or authorization after reconciliation.",
                "",
                f"Source occurrences: {len(occurrences)}. Monitored reference occurrences: {len(references)}.",
                "",
            ]
        )
        outputs[_generated_path(batch, "dispatch_queue.json")] = pretty_json(index)
        outputs[_generated_path(batch, "dispatch_plan.json")] = pretty_json(view)
        outputs[_generated_path(batch, "dispatch_plan.md")] = "\n".join(markdown).encode("utf-8")
    return outputs


@dataclass(frozen=True)
class Compilation:
    contract: dict[str, Any]
    source_occurrences: dict[str, Any]
    reference_occurrences: dict[str, Any]
    preservation_mappings: list[dict[str, Any]]
    generated_outputs: dict[str, bytes]

    def summary(self) -> dict[str, Any]:
        return {
            "schema": "crypto.autoresearch.reconciliation_history_compilation_summary.v1",
            "reconciliation_id": RECONCILIATION_ID,
            "task_id": TASK_ID,
            "contract_snapshot_commit": SNAPSHOT_COMMIT,
            "contract_sha256": CONTRACT_SHA256,
            "source_occurrence_rows": len(self.source_occurrences["rows"]),
            "reference_occurrence_rows": len(self.reference_occurrences["rows"]),
            "preservation_mapping_rows": len(self.preservation_mappings),
            "preservation_blob_copies": sum(row["disposition"] == "copy_blob_verbatim" for row in self.preservation_mappings),
            "preservation_absence_attestations": sum(row["disposition"] == "absence_attestation" for row in self.preservation_mappings),
            "generated_history_outputs": len(self.generated_outputs),
            "authority": AUTHORITY_CODE,
        }


def build_compilation(repo_root: Path) -> Compilation:
    store = GitObjects(repo_root)
    contract, inventory, successor, _phase = load_bound_inputs(store)
    source, _queues = build_source_occurrence_table(store, contract, successor)
    references = build_reference_occurrence_table(store, contract, inventory, successor)
    preservation = build_preservation_mappings(store, contract, inventory)
    outputs = _history_outputs(source, references, contract)
    return Compilation(contract, source, references, preservation, outputs)


def _safe_destination(output_root: Path, relative: str) -> Path:
    _safe_relative(relative, "output")
    root = output_root.resolve()
    destination = root.joinpath(*PurePosixPath(relative).parts)
    try:
        destination.resolve(strict=False).relative_to(root)
    except ValueError:
        _fail("OUTPUT_PATH_ESCAPE", relative)
    return destination


def materialize_compilation(compilation: Compilation, output_root: Path, repo_root: Path) -> list[str]:
    """Materialize one candidate into a caller-owned root, never overwriting files."""

    output_root = output_root.resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    store = GitObjects(repo_root)
    written: list[str] = []
    payloads: list[tuple[str, bytes]] = []
    for mapping in compilation.preservation_mappings:
        destination = _safe_destination(output_root, mapping["target_path"])
        if mapping["disposition"] == "absence_attestation":
            if destination.exists() or destination.is_symlink():
                _fail("ABSENCE_MATERIALIZED", mapping["target_path"])
            continue
        payloads.append((mapping["target_path"], store.blob(mapping["source_commit"], mapping["source_path"])))
    payloads.extend(sorted(compilation.generated_outputs.items()))
    targets = [relative for relative, _content in payloads]
    if len(targets) != len(set(targets)):
        _fail("OUTPUT_TARGET_DUPLICATE", "candidate payloads")
    for relative in targets:
        destination = _safe_destination(output_root, relative)
        if destination.exists() or destination.is_symlink():
            _fail("OUTPUT_ALREADY_EXISTS", relative)
    for relative, content in payloads:
        destination = _safe_destination(output_root, relative)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)
        mode = destination.lstat().st_mode
        if not stat.S_ISREG(mode) or destination.is_symlink():
            _fail("OUTPUT_TYPE_INVALID", relative)
        written.append(relative)
    return written


def discover_repository_root(start: Path) -> Path:
    try:
        result = subprocess.run(
            ["git", "-C", str(start.resolve()), "rev-parse", "--show-toplevel"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except OSError as error:
        _fail("GIT_UNAVAILABLE", str(error))
    if result.returncode:
        _fail("GIT_UNAVAILABLE", result.stderr.decode("utf-8", "replace").strip())
    return Path(result.stdout.decode("utf-8").strip()).resolve()


def _write_new(path: Path, content: bytes) -> None:
    if path.exists() or path.is_symlink():
        _fail("OUTPUT_ALREADY_EXISTS", str(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path)
    parser.add_argument("--output-root", type=Path, help="materialize preservation copies and 15 history outputs")
    parser.add_argument("--source-table", type=Path)
    parser.add_argument("--reference-table", type=Path)
    args = parser.parse_args(argv)
    try:
        repo_root = args.repo_root.resolve() if args.repo_root else discover_repository_root(Path.cwd())
        compilation = build_compilation(repo_root)
        if args.output_root:
            materialize_compilation(compilation, args.output_root, repo_root)
        if args.source_table:
            _write_new(args.source_table, pretty_json(compilation.source_occurrences))
        if args.reference_table:
            _write_new(args.reference_table, pretty_json(compilation.reference_occurrences))
        if not any((args.output_root, args.source_table, args.reference_table)):
            _fail("OUTPUT_REQUIRED", "provide --output-root and/or table paths")
    except (OSError, HistoryCompilerError) as error:
        print(f"history compiler error: {error}", file=sys.stderr)
        return 2
    sys.stdout.write(json.dumps(compilation.summary(), sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
