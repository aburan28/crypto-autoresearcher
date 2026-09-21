#!/usr/bin/env python3
"""Static resolver for the additive EXP-INSTR-36c8cf v9 contract.

This is a control-plane program only.  It authenticates frozen source and
snapshot custody, re-derives the frozen v8 payload, and adjudicates diagnostics
under one compiled total order.  It never runs an experiment, the research
harness, Phase B, JINV work, elliptic-curve arithmetic, rho, or BSGS.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


# Import the exact pinned v8 and dispatcher sources without ever materializing
# bytecode or a cache outside this task's five-path write scope.
sys.dont_write_bytecode = True


EXPERIMENT_ID = "EXP-INSTR-36c8cf"
VERSION = 9
ROOT_FROM_FILE = 4
BASE = "experiments/EXP-INSTR-36c8cf/amendments/v9-e9e3bf"
DEFAULT_INPUT = f"{BASE}/resolution-input.json"
DEFAULT_RESOLVED = f"{BASE}/resolved-contract.json"
DEFAULT_ORIGIN = f"{BASE}/origin-trace.json"

V8_BASE = "experiments/EXP-INSTR-36c8cf/amendments/v8"
V8_INPUT = f"{V8_BASE}/resolution-input.json"
V8_RESOLVED = f"{V8_BASE}/resolved-contract.json"
V8_ORIGIN = f"{V8_BASE}/origin-trace.json"
V8_RESOLVER = f"{V8_BASE}/resolver.py"

V8_SOURCE_FIELDS_SHA256 = "a15dd1116fff1593440c82e91083e6744eb84c5d05615c554c23902480e9717b"
V8_ORIGIN_ROWS_SHA256 = "d90a95aafbdc06a90a18587003595f1f19f12ae83bfaf8a9ba3f259ed922e413"

ERROR_CODES = (
    "EXCLUDED_FINGERPRINT",
    "DUPLICATE_KEY",
    "MISSING_SOURCE",
    "UNEXPECTED_SOURCE",
    "SOURCE_ORDER",
    "SOURCE_SIZE",
    "SOURCE_SHA256",
    "VERSION_CHAIN",
    "CUSTODY_ABSENT",
    "CUSTODY_DISAGREEMENT",
    "PATH_DISPOSITION_MISSING",
    "PATH_DISPOSITION_DUPLICATE",
    "OWNERLESS_FIELD",
    "DUAL_OWNER_FIELD",
    "OVERRIDE_POINTER_MISSING",
    "OVERRIDE_OWNER_MISMATCH",
    "DUPLICATE_SEMANTIC_SUBJECT",
    "OVERRIDE_OUT_OF_SCOPE",
    "UNRESOLVED_CONTRADICTION",
    "TYPE_COERCION",
    "GENERIC_MERGE",
    "RNG_FIXTURE_DRIFT",
    "AUTHORITY_NONZERO",
    "ECOMP_LATEST_ONLY",
    "OUTPUT_MISMATCH",
)
COMPILED_PRIORITY = tuple(
    {"code": code, "priority": priority}
    for priority, code in enumerate(ERROR_CODES, start=1)
)
PRIORITY_BY_CODE = {row["code"]: row["priority"] for row in COMPILED_PRIORITY}

LINEAGE = (
    ("specification", "experiments/EXP-INSTR-36c8cf/specification.yaml", 33270, "de3369049eaba01290f7a320d24a94e531e168891cc77b83b62962e9e6bde3f9"),
    ("amendment_v1", "experiments/EXP-INSTR-36c8cf/amendments/v1.yaml", 39080, "39266c67c6053dbb457517f9227ebc7f8bffe8636673e1d4f941047095d7604e"),
    ("amendment_v4", "experiments/EXP-INSTR-36c8cf/amendments/v4.yaml", 18236, "df64cbb9ffd1b66682e6f5202668c0f498ecbfaa1a560d6ad932fa03331e126e"),
    ("amendment_v5", "experiments/EXP-INSTR-36c8cf/amendments/v5.yaml", 32530, "06c475171d3eb275d7f6768862b8fc7563998f089d21b8cc5caa323d8d2d12b7"),
    ("amendment_v6", "experiments/EXP-INSTR-36c8cf/amendments/v6.yaml", 19499, "862d3f93c5ace7a6d028ad35f14cc5992e292ad3e7e4a20b8bfc6ab0cd2bba39"),
    ("amendment_v7", "experiments/EXP-INSTR-36c8cf/amendments/v7.yaml", 31774, "775af0e99a1513a251082f93c13e8558c4de52cd0c2d23a63f8462225787c12e"),
    ("amendment_v8", "experiments/EXP-INSTR-36c8cf/amendments/v8.yaml", 25150, "1040c0d8998e4831eecc644ee28adafc813613237df1bf53982eaa32ca1474bc"),
    ("v8_resolver", V8_RESOLVER, 49378, "a9dc99db6a4aa7e5723d6591bfd9f36f35f7a10b97eb09046c334b8a6af5cb56"),
    ("v8_resolution_input", V8_INPUT, 379916, "ae020d74ca2cc87599b72cdc386797fcecf0974898900892885da8f22ad14b0c"),
    ("v8_resolved_contract", V8_RESOLVED, 516821, "018aa4f9b0420dd985911c3fd059bcf32362b96ca0ffeacfac6a8c51673edd22"),
    ("v8_origin_trace", V8_ORIGIN, 1199973, "75d9ad35de729fff95b9aaf80723c461150dc0511fb04592f9648023831719a4"),
)

QUEUE_PATH = "coordination/goals/GOAL-ENDO-001/batches/BATCH-d7e255/instr-v8-composition-reconciliation/dispatch_queue.json"
RECEIPT_PATH = "coordination/goals/GOAL-ENDO-001/batches/BATCH-d7e255/instr-v8-composition-reconciliation/archives/TASK-20260813-9d188d/snapshot-receipt.json"
DISPATCHER_PATH = "tools/research_dispatch.py"
SNAPSHOT_TASK = "TASK-20260813-9d188d"
SNAPSHOT_COMMIT = "cd3e43098c7acb92edcebc6a0eb616677f263286"
SNAPSHOT_PARENT = "3c2afd5c6da061922cebbbabca6640964c07c610"
QUEUE_SIZE = 28670
QUEUE_SHA256 = "01473373a6b050ef2ec3cad71458c819d0b34a4dc0665378a79e6079de93ebe4"
RECEIPT_SIZE = 4640
RECEIPT_SHA256 = "946af508b127f8d32e34e6c439dceb7fe8425c8255f967fbb2c0ff189d8e05f1"
DISPATCHER_SIZE = 56104
DISPATCHER_SHA256 = "04878bf31e1da2b24f43adfa214b744a125039651233d7357889731b0b0f397a"
PLAN_SIZE = 1960
PLAN_BYTES_SHA256 = "6602d845268dd749255639c7017dbea6fe59eb49a9f9b298b326e6f9cfd2b126"
PLAN_SHA256 = "218081f42fcfc41ac27eb4b11af2c74073d72e8490c505baa0230b5e3b954c86"
PLAN_SOURCE_QUEUE_SHA256 = "526f2e20b7d1e73054c9dde1a836acc4f60e794493335085a3318c71d448c18e"

SNAPSHOT_PATH_HASHES = {
    "experiments/EXP-INSTR-36c8cf/amendments/v8.yaml": "1040c0d8998e4831eecc644ee28adafc813613237df1bf53982eaa32ca1474bc",
    "experiments/EXP-INSTR-36c8cf/amendments/v8/resolver.py": "a9dc99db6a4aa7e5723d6591bfd9f36f35f7a10b97eb09046c334b8a6af5cb56",
    "experiments/EXP-INSTR-36c8cf/amendments/v8/resolution-input.json": "ae020d74ca2cc87599b72cdc386797fcecf0974898900892885da8f22ad14b0c",
    "experiments/EXP-INSTR-36c8cf/amendments/v8/resolved-contract.json": "018aa4f9b0420dd985911c3fd059bcf32362b96ca0ffeacfac6a8c51673edd22",
    "experiments/EXP-INSTR-36c8cf/amendments/v8/origin-trace.json": "75d9ad35de729fff95b9aaf80723c461150dc0511fb04592f9648023831719a4",
    RECEIPT_PATH: RECEIPT_SHA256,
}
SNAPSHOT_PATHS = (
    "experiments/EXP-INSTR-36c8cf/amendments/v8.yaml",
    "experiments/EXP-INSTR-36c8cf/amendments/v8/resolver.py",
    "experiments/EXP-INSTR-36c8cf/amendments/v8/resolution-input.json",
    "experiments/EXP-INSTR-36c8cf/amendments/v8/resolved-contract.json",
    "experiments/EXP-INSTR-36c8cf/amendments/v8/origin-trace.json",
    RECEIPT_PATH,
)
REQUIRED_MESSAGE_IDS = (
    "GOAL-ENDO-001",
    "BATCH-d7e255",
    EXPERIMENT_ID,
    "TASK-20260813-579c2e",
    SNAPSHOT_TASK,
)
EXPECTED_TOPOLOGY = {
    "TASK-20260813-579c2e": ("coordinator", ()),
    SNAPSHOT_TASK: ("coordinator", ("TASK-20260813-579c2e",)),
    "TASK-20260813-3e3e9e": ("red-team", ("TASK-20260813-579c2e", SNAPSHOT_TASK)),
    "TASK-20260813-371481": ("coordinator", ("TASK-20260813-3e3e9e",)),
    "TASK-20260813-e69a2b": ("coordinator", ("TASK-20260813-3e3e9e", "TASK-20260813-371481")),
}

EXPECTED_ARTIFACTS: dict[str, dict[str, Any]] = {
    DEFAULT_INPUT: {"size_bytes": 443949, "sha256": "3e42be2567002e89a0ff9dd7c43e831da0bf2d02ef4d425618d81cf3f3a0a551"},
    DEFAULT_RESOLVED: {"size_bytes": 580624, "sha256": "23d05e05b1a991f811d5a4a9908fbcf44b00c0f5fc020beda2446ebd32462b62"},
    DEFAULT_ORIGIN: {"size_bytes": 1200794, "sha256": "b272bca282de54152c816aa6e357e6e99d872c810633d5ad5f5c2e262c688394"},
}


class ResolutionFailure(Exception):
    def __init__(self, code: str, detail: str, diagnostics: list[dict[str, Any]] | None = None):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail
        self.diagnostics = diagnostics or []


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canonical_bytes(value: Any) -> bytes:
    try:
        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8") + b"\n"
    except (TypeError, ValueError) as exc:
        raise ResolutionFailure("TYPE_COERCION", f"non-canonical JSON value: {exc}") from exc


def pretty_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def repository_path(root: Path, relative: str) -> Path:
    if not isinstance(relative, str) or not relative or relative.startswith("/"):
        raise ResolutionFailure("UNEXPECTED_SOURCE", f"invalid repository path {relative!r}")
    target = (root / relative).resolve()
    try:
        target.relative_to(root.resolve())
    except ValueError as exc:
        raise ResolutionFailure("UNEXPECTED_SOURCE", f"path escapes repository: {relative!r}") from exc
    return target


def strict_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ResolutionFailure("DUPLICATE_KEY", f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def strict_json(raw: bytes, label: str) -> Any:
    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=strict_pairs)
    except ResolutionFailure:
        raise
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ResolutionFailure("DUPLICATE_KEY", f"strict JSON parse failed for {label}: {exc}") from exc


@dataclass(frozen=True)
class Diagnostic:
    code: str
    detail: str
    phase: str


class DiagnosticCollector:
    """The only diagnostic collector and priority adjudicator in v9."""

    def __init__(self, source_table: Any):
        self._items: list[Diagnostic] = []
        self._source_table = source_table

    def add(self, code: str, detail: str, phase: str) -> None:
        if code not in PRIORITY_BY_CODE:
            code = "UNRESOLVED_CONTRADICTION"
            detail = f"unknown diagnostic code: {detail}"
            phase = "priority"
        self._items.append(Diagnostic(code, detail, phase))

    def capture(self, phase: str, action: Callable[[], Any]) -> Any:
        try:
            return action()
        except ResolutionFailure as exc:
            self.add(exc.code, exc.detail, phase)
        except Exception as exc:  # dependency failures are control-plane contradictions
            code = getattr(exc, "code", "UNRESOLVED_CONTRADICTION")
            detail = getattr(exc, "detail", f"{type(exc).__name__}: {exc}")
            self.add(code, detail, phase)
        return None

    def diagnostics(self) -> list[dict[str, Any]]:
        items = list(self._items)
        if self._source_table != list(COMPILED_PRIORITY):
            items.append(Diagnostic(
                "UNRESOLVED_CONTRADICTION",
                "source priority table differs from the compiled table",
                "priority",
            ))
        unique = {(item.code, item.detail, item.phase): item for item in items}
        ordered = sorted(
            unique.values(),
            key=lambda item: (PRIORITY_BY_CODE[item.code], item.code, item.phase, item.detail),
        )
        return [
            {
                "code": item.code,
                "detail": item.detail,
                "phase": item.phase,
                "priority": PRIORITY_BY_CODE[item.code],
            }
            for item in ordered
        ]

    def raise_if_any(self) -> None:
        diagnostics = self.diagnostics()
        if diagnostics:
            winner = diagnostics[0]
            raise ResolutionFailure(winner["code"], winner["detail"], diagnostics)


def import_exact(root: Path, relative: str, size: int, digest: str, name: str) -> Any:
    path = repository_path(root, relative)
    raw = path.read_bytes()
    if len(raw) != size or sha256(raw) != digest:
        raise ResolutionFailure("SOURCE_SHA256", f"module binding drift: {relative}")
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ResolutionFailure("MISSING_SOURCE", f"cannot load module: {relative}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_lineage(root: Path, collector: DiagnosticCollector) -> None:
    for source_id, relative, size, digest in LINEAGE:
        def check(relative: str = relative, size: int = size, digest: str = digest) -> None:
            raw = repository_path(root, relative).read_bytes()
            if len(raw) != size:
                raise ResolutionFailure("SOURCE_SIZE", f"{relative}: expected {size}, observed {len(raw)}")
            if sha256(raw) != digest:
                raise ResolutionFailure("SOURCE_SHA256", f"{relative}: expected {digest}, observed {sha256(raw)}")
        collector.capture(f"lineage:{source_id}", check)


def collect_v9_input_diagnostics(
    root: Path,
    input_object: dict[str, Any],
    v8: Any,
    collector: DiagnosticCollector,
) -> None:
    """Evaluate independent input predicates without allowing early raises to win.

    V8 remains the exact source parser and semantic implementation, but v9
    evaluates the predicates that collided in v8 independently before invoking
    the frozen verifier.  Consequently missing rows/pointers and competing
    lower-priority faults are all present when the compiled adjudicator selects.
    """
    expected_input = generate_input(root)
    composition = input_object.get("composition")
    if not isinstance(composition, dict):
        collector.add("UNRESOLVED_CONTRADICTION", "composition is not a mapping", "input")
        collector.add("OUTPUT_MISMATCH", "v9 input differs from its generated contract", "input")
        return

    if composition.get("snapshot_custody") != custody_contract():
        collector.add("CUSTODY_DISAGREEMENT", "input custody contract drift", "input-custody")
    if composition.get("lineage_manifest") != lineage_object():
        collector.add("SOURCE_SHA256", "input lineage manifest drift", "input-lineage")
    if input_object.get("authority") != v8.EXPECTED_AUTHORITY:
        collector.add("AUTHORITY_NONZERO", "v9 authority boundary drift", "input-authority")
    if composition.get("entry_strategies") != ["latest_entry", "ordered_entry"]:
        collector.add("ECOMP_LATEST_ONLY", "both entry strategies are mandatory", "input-entry")
    if composition.get("resolver_contract") != expected_input["composition"]["resolver_contract"]:
        collector.add("GENERIC_MERGE", "v9 resolver contract drift", "input-merge")

    loaded = collector.capture(
        "input-source-manifest",
        lambda: v8.load_and_verify_sources(root, composition),
    )
    if loaded is not None:
        manifest, documents = loaded
        rows = composition.get("source_leaf_disposition")
        if not isinstance(rows, list):
            collector.add("PATH_DISPOSITION_MISSING", "source disposition table absent", "input-disposition")
            rows = []
        expected_keys = {
            (source_id, pointer)
            for source_id in v8.EXPECTED_SOURCE_IDS
            for pointer, _value in v8.iter_leaves(documents[source_id])
        }
        counts: dict[tuple[Any, Any], int] = {}
        invalid_dispositions = False
        for row in rows:
            if not isinstance(row, dict):
                invalid_dispositions = True
                continue
            key = (row.get("source_id"), row.get("source_pointer"))
            counts[key] = counts.get(key, 0) + 1
            if row.get("disposition") not in {"executable-owned", "excluded-provenance", "common-metadata"}:
                invalid_dispositions = True
        observed_keys = set(counts)
        if expected_keys - observed_keys:
            collector.add("PATH_DISPOSITION_MISSING", "one or more source disposition rows are missing", "input-disposition")
        if any(count > 1 for count in counts.values()):
            collector.add("PATH_DISPOSITION_DUPLICATE", "one or more source disposition rows are duplicated", "input-disposition")
        if invalid_dispositions or observed_keys - expected_keys:
            collector.add("OWNERLESS_FIELD", "invalid or ownerless source disposition row", "input-disposition")
        expected_rows = expected_input["composition"]["source_leaf_disposition"]
        if rows != expected_rows and not (expected_keys - observed_keys) and not any(count > 1 for count in counts.values()) and not invalid_dispositions:
            collector.add("DUAL_OWNER_FIELD", "source disposition classification or order drift", "input-disposition")

        edges = composition.get("allowed_overrides")
        if not isinstance(edges, list):
            collector.add("UNRESOLVED_CONTRADICTION", "override edge table absent", "input-override")
            edges = []
        expected_edges = expected_input["composition"]["allowed_overrides"]
        expected_ids = {edge["edge_id"] for edge in expected_edges}
        observed_ids = [edge.get("edge_id") for edge in edges if isinstance(edge, dict)]
        if set(observed_ids) != expected_ids or len(observed_ids) != len(set(observed_ids)):
            collector.add("UNRESOLVED_CONTRADICTION", "override edge ID set drift", "input-override")
        subjects = [edge.get("semantic_subject") for edge in edges if isinstance(edge, dict)]
        if len(subjects) != len(set(subjects)):
            collector.add("DUPLICATE_SEMANTIC_SUBJECT", "duplicate override semantic subject", "input-override")
        allowed_owners = set(v8.EXPECTED_SOURCE_IDS) | {"amendment_v8"}
        for edge in edges:
            if not isinstance(edge, dict):
                collector.add("UNRESOLVED_CONTRADICTION", "override edge is not a mapping", "input-override")
                continue
            predecessor_owner = edge.get("predecessor_owner")
            successor_owner = edge.get("successor_owner")
            if predecessor_owner not in allowed_owners or successor_owner not in allowed_owners:
                collector.add("OVERRIDE_OWNER_MISMATCH", "override owner is outside the frozen owner set", "input-override")
            for owner_key, pointer_key in (
                ("predecessor_owner", "predecessor_pointer"),
                ("successor_owner", "successor_pointer"),
            ):
                owner = edge.get(owner_key)
                pointer = edge.get(pointer_key)
                if owner in documents:
                    try:
                        v8.pointer_get(documents[owner], pointer)
                    except Exception:
                        collector.add("OVERRIDE_POINTER_MISSING", f"missing override pointer for {owner}", "input-override")
        disposition_result = collector.capture(
            "input-disposition-frozen-verifier",
            lambda: v8.verify_dispositions(composition, manifest, documents),
        )
        if disposition_result is not None:
            _rows, dispositions, _leaves = disposition_result
            collector.capture(
                "input-override-frozen-verifier",
                lambda: v8.verify_edges(composition, input_object, documents, dispositions),
            )
        collector.capture("input-preservation", lambda: v8.verify_preservation(input_object, documents))

    if input_object != expected_input:
        collector.add("OUTPUT_MISMATCH", "v9 input differs from the complete generated contract", "input")


def git(root: Path, *args: str, check: bool = True) -> bytes:
    completed = subprocess.run(
        ["git", "-C", str(root), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", "replace").strip()
        raise ResolutionFailure("CUSTODY_DISAGREEMENT", f"git {' '.join(args)}: {detail or completed.returncode}")
    return completed.stdout


def find_top_level_task(queue: dict[str, Any], task_id: str) -> dict[str, Any] | None:
    tasks = queue.get("tasks")
    if not isinstance(tasks, list):
        return None
    matches = [task for task in tasks if isinstance(task, dict) and task.get("id") == task_id]
    return matches[0] if len(matches) == 1 else None


def load_positive_custody_bundle(root: Path, dispatch: Any) -> dict[str, Any]:
    queue_raw = repository_path(root, QUEUE_PATH).read_bytes()
    receipt_raw = repository_path(root, RECEIPT_PATH).read_bytes()
    queue = strict_json(queue_raw, QUEUE_PATH)
    receipt = strict_json(receipt_raw, RECEIPT_PATH)
    plan = dispatch.select(queue, repository_verifier=dispatch.GitRepositoryVerifier(root))
    return {
        "queue": queue,
        "queue_raw": queue_raw,
        "receipt": receipt,
        "receipt_raw": receipt_raw,
        "plan": plan,
    }


def collect_custody_diagnostics(
    root: Path,
    dispatch: Any,
    bundle: dict[str, Any] | None,
    collector: DiagnosticCollector,
) -> None:
    if not isinstance(bundle, dict):
        collector.add("CUSTODY_ABSENT", "custody bundle absent", "custody")
        return
    queue = bundle.get("queue")
    receipt = bundle.get("receipt")
    plan = bundle.get("plan")
    queue_raw = bundle.get("queue_raw")
    receipt_raw = bundle.get("receipt_raw")
    if not isinstance(queue, dict) or not isinstance(receipt, dict) or not isinstance(plan, dict):
        collector.add("CUSTODY_ABSENT", "queue, receipt, and canonical plan are mandatory", "custody")
        return
    if not isinstance(queue_raw, bytes) or not isinstance(receipt_raw, bytes):
        collector.add("CUSTODY_ABSENT", "raw queue and receipt bytes are mandatory", "custody")
        return

    def disagree(condition: bool, detail: str) -> None:
        if condition:
            collector.add("CUSTODY_DISAGREEMENT", detail, "custody")

    disagree(len(queue_raw) != QUEUE_SIZE or sha256(queue_raw) != QUEUE_SHA256, "terminal queue byte binding drift")
    disagree(len(receipt_raw) != RECEIPT_SIZE or sha256(receipt_raw) != RECEIPT_SHA256, "snapshot receipt byte binding drift")
    disagree(queue.get("schema") != "crypto.autoresearch.dispatch_queue.v1", "queue schema drift")
    disagree(queue.get("goal_id") != "GOAL-ENDO-001" or queue.get("batch_id") != "BATCH-d7e255", "queue goal or batch drift")

    tasks = queue.get("tasks")
    if not isinstance(tasks, list):
        collector.add("CUSTODY_ABSENT", "queue tasks absent", "custody")
        tasks = []
    ids = [task.get("id") for task in tasks if isinstance(task, dict)]
    disagree(len(ids) != len(tasks) or len(ids) != len(set(ids)), "nested, malformed, or duplicate queue tasks")
    disagree(set(ids) != set(EXPECTED_TOPOLOGY), "direct queue task set drift")
    for task_id, (role, dependencies) in EXPECTED_TOPOLOGY.items():
        task = find_top_level_task(queue, task_id)
        if task is None:
            collector.add("CUSTODY_ABSENT", f"queue task absent: {task_id}", "custody")
            continue
        disagree(task.get("role") != role, f"queue role drift: {task_id}")
        disagree(tuple(task.get("depends_on", ())) != dependencies, f"direct dependency topology drift: {task_id}")
        disagree(task.get("state") != "completed", f"terminal task is not completed: {task_id}")

    archive_task = find_top_level_task(queue, SNAPSHOT_TASK)
    archive = archive_task.get("archive") if isinstance(archive_task, dict) else None
    if not isinstance(archive, dict):
        collector.add("CUSTODY_ABSENT", "completed snapshot archive absent", "custody")
        archive = {}
    commit = archive.get("commit_sha")
    parent = archive.get("parent_sha")
    hashes = archive.get("path_sha256")
    disagree(not isinstance(commit, str) or len(commit) != 40 or any(ch not in "0123456789abcdef" for ch in commit), "malformed commit identity")
    disagree(not isinstance(parent, str) or len(parent) != 40 or any(ch not in "0123456789abcdef" for ch in parent), "malformed parent identity")
    disagree(commit != SNAPSHOT_COMMIT, "snapshot commit identity drift")
    disagree(parent != SNAPSHOT_PARENT, "snapshot parent identity drift")
    disagree(hashes != SNAPSHOT_PATH_HASHES, "snapshot path hash set drift")
    disagree(archive.get("record_ids") != list(REQUIRED_MESSAGE_IDS), "snapshot required record IDs drift")
    disagree(archive.get("source_task_ids") != ["TASK-20260813-579c2e"], "snapshot source task topology drift")
    disagree(archive.get("kind") != "snapshot" or archive.get("binding_mode") != "content_first", "snapshot archive kind drift")

    if isinstance(commit, str) and len(commit) == 40:
        object_type = git(root, "cat-file", "-t", commit, check=False).decode("ascii", "replace").strip()
        disagree(object_type != "commit", "snapshot commit does not exist as a Git commit")
        ancestor = subprocess.run(
            ["git", "-C", str(root), "merge-base", "--is-ancestor", commit, "HEAD"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        disagree(ancestor.returncode != 0, "snapshot commit is not reachable from HEAD")
        if object_type == "commit":
            observed_parent = git(root, "rev-parse", f"{commit}^1", check=False).decode("ascii", "replace").strip()
            disagree(observed_parent != parent or observed_parent != SNAPSHOT_PARENT, "actual first parent disagrees")
            changed = tuple(sorted(
                line for line in git(root, "diff-tree", "--no-commit-id", "--name-only", "-r", commit).decode("utf-8").splitlines() if line
            ))
            disagree(changed != tuple(sorted(SNAPSHOT_PATHS)), "snapshot commit changed-path set is not exact")
            message = git(root, "show", "-s", "--format=%B", commit).decode("utf-8", "replace")
            disagree(any(identifier not in message for identifier in REQUIRED_MESSAGE_IDS), "snapshot commit message IDs incomplete")
            if isinstance(hashes, dict):
                for relative in SNAPSHOT_PATHS:
                    blob = git(root, "show", f"{commit}:{relative}", check=False)
                    disagree(sha256(blob) != hashes.get(relative), f"snapshot blob hash drift: {relative}")
                    current = repository_path(root, relative).read_bytes()
                    disagree(sha256(current) != hashes.get(relative), f"current source hash drift: {relative}")

    disagree(receipt.get("task_id") != SNAPSHOT_TASK, "receipt task identity drift")
    disagree(receipt.get("commit_sha") is not None, "self-neutral receipt claims its future commit")
    disagree(receipt.get("paths") != list(SNAPSHOT_PATHS), "receipt path set drift")
    receipt_hashes = receipt.get("path_sha256")
    receipt_sizes = receipt.get("path_size_bytes")
    if not isinstance(receipt_hashes, dict) or not isinstance(receipt_sizes, dict):
        collector.add("CUSTODY_ABSENT", "receipt hash or size declarations absent", "custody")
    else:
        disagree(receipt_hashes.get(RECEIPT_PATH) is not None, "receipt illegally self-hashes")
        disagree(receipt_sizes.get(RECEIPT_PATH) is not None, "receipt illegally self-sizes")
        for relative in SNAPSHOT_PATHS:
            if relative == RECEIPT_PATH:
                continue
            current = repository_path(root, relative).read_bytes()
            disagree(receipt_hashes.get(relative) != SNAPSHOT_PATH_HASHES[relative], f"receipt hash drift: {relative}")
            disagree(receipt_sizes.get(relative) != len(current), f"receipt size drift: {relative}")

    dispatcher_raw = repository_path(root, DISPATCHER_PATH).read_bytes()
    disagree(len(dispatcher_raw) != DISPATCHER_SIZE or sha256(dispatcher_raw) != DISPATCHER_SHA256, "pinned dispatcher drift")
    regenerated = collector.capture(
        "custody-plan",
        lambda: dispatch.select(queue, repository_verifier=dispatch.GitRepositoryVerifier(root)),
    )
    if isinstance(regenerated, dict):
        disagree(plan != regenerated, "supplied or cached plan differs from canonical regeneration")
        plan_raw = pretty_bytes(regenerated)
        disagree(len(plan_raw) != PLAN_SIZE or sha256(plan_raw) != PLAN_BYTES_SHA256, "canonical plan byte drift")
        disagree(regenerated.get("plan_sha256") != PLAN_SHA256, "canonical logical plan digest drift")
        disagree(regenerated.get("source_queue_sha256") != PLAN_SOURCE_QUEUE_SHA256, "canonical source-queue digest drift")
        gates = regenerated.get("gates")
        disagree(not isinstance(gates, dict) or len(gates) != 10 or not all(gates.values()), "one or more dispatcher gates failed")
        disagree(regenerated.get("dispatches") != [], "terminal v8 queue unexpectedly dispatches work")
        terminal = regenerated.get("terminal")
        disagree(not isinstance(terminal, list) or {row.get("id") for row in terminal} != set(EXPECTED_TOPOLOGY), "terminal plan topology drift")
        disagree(regenerated.get("content_only_archives") != [{
            "task_id": SNAPSHOT_TASK,
            "reason": "declared content_first binding mode",
            "paths_verified": 6,
            "generated_paths_skipped": [],
        }], "canonical content-only archive gate drift")


def mutate_custody_bundle(base: dict[str, Any], case: str) -> dict[str, Any] | None:
    if case == "omitted_custody":
        return None
    bundle = copy.deepcopy(base)
    queue = bundle["queue"]
    receipt = bundle["receipt"]
    plan = bundle["plan"]
    archive = find_top_level_task(queue, SNAPSHOT_TASK)["archive"]
    if case == "missing_receipt":
        bundle["receipt"] = None
    elif case == "malformed_commit":
        archive["commit_sha"] = "not-a-commit"
    elif case == "unreachable_commit":
        archive["commit_sha"] = "a" * 40
    elif case == "stale_commit":
        archive["commit_sha"] = SNAPSHOT_PARENT
    elif case == "fabricated_authority":
        bundle["plan"] = {"content_only_archives": [{"task_id": SNAPSHOT_TASK, "paths_verified": 6, "generated_paths_skipped": []}]}
    elif case == "wrong_parent":
        archive["parent_sha"] = "b" * 40
    elif case == "extra_path":
        archive["path_sha256"]["unexpected/path"] = "0" * 64
    elif case == "hash_drift":
        archive["path_sha256"][V8_RESOLVED] = "0" * 64
    elif case == "queue_drift":
        queue["objective"] += " drift"
    elif case == "plan_drift":
        plan["plan_sha256"] = "0" * 64
    elif case == "topology_drift":
        queue["tasks"][2]["depends_on"] = [SNAPSHOT_TASK]
    elif case == "gate_drift":
        plan["gates"]["concurrency_cap_respected"] = False
    elif case == "schema_drift":
        queue["schema"] = "fabricated"
    elif case == "duplicate_task":
        queue["tasks"].append(copy.deepcopy(queue["tasks"][0]))
    elif case == "receipt_hash_drift":
        receipt["path_sha256"][V8_RESOLVED] = "f" * 64
    else:
        raise ResolutionFailure("UNRESOLVED_CONTRADICTION", f"unknown custody case: {case}")
    bundle["queue_raw"] = pretty_bytes(queue)
    bundle["receipt_raw"] = pretty_bytes(receipt) if isinstance(receipt, dict) else b""
    return bundle


CUSTODY_CASES = (
    "omitted_custody",
    "missing_receipt",
    "malformed_commit",
    "unreachable_commit",
    "stale_commit",
    "fabricated_authority",
    "wrong_parent",
    "extra_path",
    "hash_drift",
    "queue_drift",
    "plan_drift",
    "topology_drift",
    "gate_drift",
    "schema_drift",
    "duplicate_task",
    "receipt_hash_drift",
)
CUSTODY_ABSENT_CASES = {"omitted_custody", "missing_receipt", "duplicate_task"}


def priority_winner(codes: list[str], source_table: Any | None = None) -> str:
    collector = DiagnosticCollector(list(COMPILED_PRIORITY) if source_table is None else source_table)
    for index, code in enumerate(codes):
        collector.add(code, f"injected ordered fault {index}", "fixture")
    diagnostics = collector.diagnostics()
    if not diagnostics:
        raise ResolutionFailure("UNRESOLVED_CONTRADICTION", "fault fixture contains no diagnostics")
    return diagnostics[0]["code"]


def conformance_fixtures() -> dict[str, Any]:
    pairs = [
        {"first": first, "second": second, "expected": first if PRIORITY_BY_CODE[first] <= PRIORITY_BY_CODE[second] else second}
        for first in ERROR_CODES
        for second in ERROR_CODES
    ]
    return {
        "custody_negative_matrix": [
            {"fixture_id": case, "expected": "CUSTODY_ABSENT" if case in CUSTODY_ABSENT_CASES else "CUSTODY_DISAGREEMENT"}
            for case in CUSTODY_CASES
        ],
        "inherited_v8_collisions": [
            {"faults": ["PATH_DISPOSITION_MISSING", "OWNERLESS_FIELD"], "expected": "PATH_DISPOSITION_MISSING"},
            {"faults": ["OVERRIDE_POINTER_MISSING", "UNRESOLVED_CONTRADICTION"], "expected": "OVERRIDE_POINTER_MISSING"},
        ],
        "cross_phase_collisions": [
            {"faults": ["SOURCE_SHA256", "CUSTODY_DISAGREEMENT"], "expected": "SOURCE_SHA256"},
            {"faults": ["CUSTODY_ABSENT", "PATH_DISPOSITION_MISSING"], "expected": "CUSTODY_ABSENT"},
            {"faults": ["OVERRIDE_OWNER_MISMATCH", "AUTHORITY_NONZERO"], "expected": "OVERRIDE_OWNER_MISMATCH"},
            {"faults": ["RNG_FIXTURE_DRIFT", "OUTPUT_MISMATCH"], "expected": "RNG_FIXTURE_DRIFT"},
            {"faults": ["DUPLICATE_KEY", "EXCLUDED_FINGERPRINT"], "expected": "EXCLUDED_FINGERPRINT"},
        ],
        "priority_table_drift": {
            "faults": ["OUTPUT_MISMATCH"],
            "expected": "UNRESOLVED_CONTRADICTION",
            "mutation": "reverse_source_table",
        },
        "ordered_error_pairs": pairs,
        "ordered_error_pair_count": len(pairs),
        "experiment_runs_consumed": 0,
    }


def lineage_object() -> list[dict[str, Any]]:
    return [
        {"source_id": source_id, "path": path, "size_bytes": size, "sha256": digest}
        for source_id, path, size, digest in LINEAGE
    ]


def custody_contract() -> dict[str, Any]:
    return {
        "mandatory_on_every_normal_entry": True,
        "archive_task_id": SNAPSHOT_TASK,
        "commit_sha": SNAPSHOT_COMMIT,
        "parent_sha": SNAPSHOT_PARENT,
        "expected_content_paths": list(SNAPSHOT_PATHS),
        "path_sha256": SNAPSHOT_PATH_HASHES,
        "required_message_ids": list(REQUIRED_MESSAGE_IDS),
        "queue": {"path": QUEUE_PATH, "size_bytes": QUEUE_SIZE, "sha256": QUEUE_SHA256},
        "receipt": {"path": RECEIPT_PATH, "size_bytes": RECEIPT_SIZE, "sha256": RECEIPT_SHA256, "self_neutral": True},
        "dispatcher": {"path": DISPATCHER_PATH, "size_bytes": DISPATCHER_SIZE, "sha256": DISPATCHER_SHA256},
        "canonical_plan": {
            "pretty_size_bytes": PLAN_SIZE,
            "pretty_sha256": PLAN_BYTES_SHA256,
            "plan_sha256": PLAN_SHA256,
            "source_queue_sha256": PLAN_SOURCE_QUEUE_SHA256,
            "gate_count": 10,
            "all_gates_required": True,
            "paths_verified": 6,
            "generated_paths_skipped": [],
        },
        "direct_queue_topology": [
            {"task_id": task_id, "role": role, "depends_on": list(dependencies)}
            for task_id, (role, dependencies) in EXPECTED_TOPOLOGY.items()
        ],
        "failure_semantics": "CUSTODY_ABSENT_or_CUSTODY_DISAGREEMENT_before_resolution",
    }


def generate_input(root: Path) -> dict[str, Any]:
    v8 = strict_json(repository_path(root, V8_INPUT).read_bytes(), V8_INPUT)
    result = copy.deepcopy(v8)
    result["schema"] = "crypto.autoresearch.resolution_input.v9"
    result["version"] = VERSION
    composition = result["composition"]
    composition["controlling_v8_disposition"] = {
        "decision_id": "DEC-20260813-5c1de7",
        "disposition": "not_approved_revise",
        "material_findings": ["O-INSTR-V8-1", "O-INSTR-V8-2", "O-INSTR-V8-3", "O-INSTR-V8-4"],
        "scientific_effect": "none",
    }
    composition["lineage_manifest"] = lineage_object()
    composition["snapshot_custody"] = custody_contract()
    composition["error_priority"] = list(COMPILED_PRIORITY)
    composition["global_diagnostic_contract"] = {
        "collector_count": 1,
        "adjudicator_count": 1,
        "compiled_priority_table": list(COMPILED_PRIORITY),
        "collect_all_applicable_before_selection": True,
        "source_table_drift": "UNRESOLVED_CONTRADICTION_under_compiled_order",
        "traversal_and_strategy_may_not_select": True,
        "ordered_pair_count": 625,
    }
    resolver_contract = copy.deepcopy(composition["resolver_contract"])
    resolver_contract.update({
        "canonical_output_framing": "v9_sorted_compact_UTF8_JSON_exactly_one_terminal_LF",
        "custody_optional": False,
        "global_diagnostic_collector": "single_compiled_priority_adjudicator",
        "normal_entry_without_authenticated_custody": "prohibited",
        "priority_table_drift": "fail_closed",
        "v8_scientific_source_payload": "byte_preserved_under_two_subdigests",
    })
    composition["resolver_contract"] = resolver_contract
    static = copy.deepcopy(composition["static_conformance_fixtures"])
    static["v9"] = conformance_fixtures()
    composition["static_conformance_fixtures"] = static
    composition["v8_payload_binding"] = {
        "source_fields_sha256": V8_SOURCE_FIELDS_SHA256,
        "origin_rows_sha256": V8_ORIGIN_ROWS_SHA256,
        "canonical_subdigest_framing": "sorted_compact_UTF8_JSON_plus_exactly_one_LF",
        "source_field_count": 1363,
        "origin_row_count": 1363,
        "scientific_or_source_change": False,
    }
    result["authority"] = copy.deepcopy(v8["authority"])
    return result


def verify_quarantined_mutations(root: Path, v8: Any, collector: DiagnosticCollector) -> list[dict[str, Any]]:
    cases = (
        ("b480bae05e1a9a040f57f21a333953bde10a9fe2", "experiments/EXP-INSTR-36c8cf/amendments/v6.yaml", "44a217ffddfa4a7f60f377b54fcc3eb4043efef79c905cde8ac8755f5b17396f"),
        ("b7cb136f026a384dc1ef244bea1be2fec5f8684e", "experiments/EXP-INSTR-36c8cf/amendments/v7.yaml", "58e3c2b0d78bd95e4c7a76e67b0175aff70c651ccc523f7a2895bbbae93152cc"),
    )
    results = []
    for commit, path, digest in cases:
        raw = git(root, "show", f"{commit}:{path}", check=False)
        observed = "EXCLUDED_FINGERPRINT" if sha256(raw) == digest and digest in v8.HISTORICAL_EXCLUDED_SHA256 else "NOT_REJECTED"
        if observed != "EXCLUDED_FINGERPRINT":
            collector.add("OUTPUT_MISMATCH", f"quarantined mutation not rejected: {commit}:{path}", "quarantine")
        results.append({"commit": commit, "path": path, "expected": "EXCLUDED_FINGERPRINT", "observed": observed})
    return results


def regenerate_v8(root: Path, v8: Any, collector: DiagnosticCollector) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    result = collector.capture(
        "v8-regeneration",
        lambda: v8.resolve_package(root, V8_INPUT, ["latest_entry", "ordered_entry"], check_custody=False),
    )
    if result is None:
        return None, None
    resolved_raw, origin_raw = result
    if resolved_raw != repository_path(root, V8_RESOLVED).read_bytes():
        collector.add("OUTPUT_MISMATCH", "v8 resolved contract no longer re-derives byte-identically", "v8-regeneration")
    if origin_raw != repository_path(root, V8_ORIGIN).read_bytes():
        collector.add("OUTPUT_MISMATCH", "v8 origin trace no longer re-derives byte-identically", "v8-regeneration")
    return strict_json(resolved_raw, V8_RESOLVED), strict_json(origin_raw, V8_ORIGIN)


def derive_outputs(
    input_object: dict[str, Any],
    input_raw: bytes,
    v8_resolved: dict[str, Any],
    v8_origin: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    input_binding = {"path": DEFAULT_INPUT, "size_bytes": len(input_raw), "sha256": sha256(input_raw)}
    source_fields = copy.deepcopy(v8_resolved["source_fields"])
    rows = copy.deepcopy(v8_origin["rows"])
    resolved = {
        "schema": "crypto.autoresearch.resolved_contract.v9",
        "experiment_id": EXPERIMENT_ID,
        "version": VERSION,
        "resolution_input": input_binding,
        "authority": copy.deepcopy(input_object["authority"]),
        "preservation": copy.deepcopy(input_object["preservation"]),
        "composition": {
            "allowed_overrides": copy.deepcopy(v8_resolved["composition"]["allowed_overrides"]),
            "canonical_framing": copy.deepcopy(input_object["composition"]["canonical_framing"]),
            "classification_summary": copy.deepcopy(v8_resolved["composition"]["classification_summary"]),
            "controlling_v8_disposition": copy.deepcopy(input_object["composition"]["controlling_v8_disposition"]),
            "error_priority": list(COMPILED_PRIORITY),
            "global_diagnostic_contract": copy.deepcopy(input_object["composition"]["global_diagnostic_contract"]),
            "lineage_manifest": copy.deepcopy(input_object["composition"]["lineage_manifest"]),
            "ordered_sources": copy.deepcopy(v8_resolved["composition"]["ordered_sources"]),
            "quarantined_fingerprints": copy.deepcopy(v8_resolved["composition"]["quarantined_fingerprints"]),
            "resolver_contract": copy.deepcopy(input_object["composition"]["resolver_contract"]),
            "semantic_winners": copy.deepcopy(v8_resolved["composition"]["semantic_winners"]),
            "snapshot_custody": copy.deepcopy(input_object["composition"]["snapshot_custody"]),
            "source_field_count": len(source_fields),
            "static_conformance_fixtures": copy.deepcopy(input_object["composition"]["static_conformance_fixtures"]),
            "v8_payload_binding": copy.deepcopy(input_object["composition"]["v8_payload_binding"]),
        },
        "source_fields": source_fields,
        "source_fields_sha256": sha256(canonical_bytes(source_fields)),
    }
    origin = {
        "schema": "crypto.autoresearch.origin_trace.v9",
        "experiment_id": EXPERIMENT_ID,
        "version": VERSION,
        "resolution_input": input_binding,
        "classification_summary": copy.deepcopy(v8_origin["classification_summary"]),
        "source_leaf_disposition": copy.deepcopy(v8_origin["source_leaf_disposition"]),
        "exact_overrides": copy.deepcopy(v8_origin["exact_overrides"]),
        "composition_origin_rows": copy.deepcopy(v8_origin["composition_origin_rows"]),
        "v9_composition_origin_rows": [
            {"owner_source_id": "amendment_v9", "resolved_field_path": path, "authority_role": "additive_control_plane_only"}
            for path in (
                "/composition/controlling_v8_disposition",
                "/composition/global_diagnostic_contract",
                "/composition/lineage_manifest",
                "/composition/snapshot_custody",
                "/composition/v8_payload_binding",
            )
        ],
        "row_order": v8_origin["row_order"],
        "rows": rows,
        "rows_sha256": sha256(canonical_bytes(rows)),
    }
    return resolved, origin


def resolve(
    root: Path,
    strategies: list[str],
    materialize_input: bool = False,
) -> tuple[bytes, bytes, bytes, dict[str, Any]]:
    v8 = import_exact(root, V8_RESOLVER, 49378, LINEAGE[7][3], "exp_instr_v8_resolver")
    dispatch = import_exact(root, DISPATCHER_PATH, DISPATCHER_SIZE, DISPATCHER_SHA256, "research_dispatch_v9_pinned")
    input_object = generate_input(root) if materialize_input else strict_json(repository_path(root, DEFAULT_INPUT).read_bytes(), DEFAULT_INPUT)
    input_raw = canonical_bytes(input_object)
    collector = DiagnosticCollector(input_object.get("composition", {}).get("error_priority"))
    if input_object.get("schema") != "crypto.autoresearch.resolution_input.v9" or input_object.get("version") != VERSION:
        collector.add("VERSION_CHAIN", "v9 input schema or version drift", "version")
    if input_object.get("experiment_id") != EXPERIMENT_ID:
        collector.add("VERSION_CHAIN", "experiment identity drift", "version")
    if not materialize_input and repository_path(root, DEFAULT_INPUT).read_bytes() != input_raw:
        collector.add("OUTPUT_MISMATCH", "v9 resolution input is not canonical compact JSON plus one LF", "input")
    collect_v9_input_diagnostics(root, input_object, v8, collector)
    verify_lineage(root, collector)
    collect_custody_diagnostics(root, dispatch, load_positive_custody_bundle(root, dispatch), collector)
    verify_quarantined_mutations(root, v8, collector)
    v8_resolved, v8_origin = regenerate_v8(root, v8, collector)
    collector.raise_if_any()
    assert v8_resolved is not None and v8_origin is not None
    if sha256(canonical_bytes(v8_resolved["source_fields"])) != V8_SOURCE_FIELDS_SHA256:
        raise ResolutionFailure("OUTPUT_MISMATCH", "frozen v8 source_fields subdigest drift")
    if sha256(canonical_bytes(v8_origin["rows"])) != V8_ORIGIN_ROWS_SHA256:
        raise ResolutionFailure("OUTPUT_MISMATCH", "frozen v8 origin rows subdigest drift")

    results: list[tuple[bytes, bytes]] = []
    for strategy in strategies:
        if strategy not in {"latest_entry", "ordered_entry"}:
            raise ResolutionFailure("ECOMP_LATEST_ONLY", f"unsupported strategy: {strategy}")
        resolved, origin = derive_outputs(input_object, input_raw, v8_resolved, v8_origin)
        results.append((canonical_bytes(resolved), canonical_bytes(origin)))
    if any(item != results[0] for item in results[1:]):
        raise ResolutionFailure("ECOMP_LATEST_ONLY", "strategies did not converge byte-identically")
    summary = {
        "authority": "zero",
        "custody": "authenticated_mandatory",
        "experiment_id": EXPERIMENT_ID,
        "experiment_runs_consumed": 0,
        "origin_trace": {"size_bytes": len(results[0][1]), "sha256": sha256(results[0][1])},
        "resolved_contract": {"size_bytes": len(results[0][0]), "sha256": sha256(results[0][0])},
        "source_fields_sha256": V8_SOURCE_FIELDS_SHA256,
        "origin_rows_sha256": V8_ORIGIN_ROWS_SHA256,
        "status": "PASS",
        "strategies": strategies,
        "version": VERSION,
    }
    return input_raw, results[0][0], results[0][1], summary


def compare_materialized(root: Path, relative: str, generated: bytes) -> None:
    path = repository_path(root, relative)
    actual = path.read_bytes()
    if actual != generated:
        raise ResolutionFailure("OUTPUT_MISMATCH", f"materialized bytes drift: {relative}")
    expected = EXPECTED_ARTIFACTS[relative]
    if expected["size_bytes"] is not None and (
        len(actual) != expected["size_bytes"] or sha256(actual) != expected["sha256"]
    ):
        raise ResolutionFailure("OUTPUT_MISMATCH", f"recorded size/hash drift: {relative}")


def run_self_test(root: Path) -> dict[str, Any]:
    input_raw, resolved_raw, origin_raw, _summary = resolve(root, ["latest_entry", "ordered_entry"])
    v8 = import_exact(root, V8_RESOLVER, 49378, LINEAGE[7][3], "exp_instr_v8_selftest")
    dispatch = import_exact(root, DISPATCHER_PATH, DISPATCHER_SIZE, DISPATCHER_SHA256, "research_dispatch_v9_selftest")
    input_object = strict_json(input_raw, DEFAULT_INPUT)
    quarantine_collector = DiagnosticCollector(input_object["composition"]["error_priority"])
    quarantine_results = verify_quarantined_mutations(root, v8, quarantine_collector)
    quarantine_collector.raise_if_any()
    base = load_positive_custody_bundle(root, dispatch)
    custody_results = []
    for case in CUSTODY_CASES:
        collector = DiagnosticCollector(input_object["composition"]["error_priority"])
        collect_custody_diagnostics(root, dispatch, mutate_custody_bundle(base, case), collector)
        diagnostics = collector.diagnostics()
        observed = diagnostics[0]["code"] if diagnostics else "PASS"
        expected = "CUSTODY_ABSENT" if case in CUSTODY_ABSENT_CASES else "CUSTODY_DISAGREEMENT"
        if observed != expected:
            raise ResolutionFailure("OUTPUT_MISMATCH", f"custody case {case}: expected {expected}, observed {observed}")
        custody_results.append({"fixture_id": case, "expected": expected, "observed": observed})

    fixtures = conformance_fixtures()
    collision_results = []
    for fixture in fixtures["inherited_v8_collisions"] + fixtures["cross_phase_collisions"]:
        observed = priority_winner(fixture["faults"])
        if observed != fixture["expected"]:
            raise ResolutionFailure("OUTPUT_MISMATCH", f"collision mismatch: {fixture}")
        collision_results.append({**fixture, "observed": observed})
    drift_observed = priority_winner(["OUTPUT_MISMATCH"], list(reversed(COMPILED_PRIORITY)))
    if drift_observed != "UNRESOLVED_CONTRADICTION":
        raise ResolutionFailure("OUTPUT_MISMATCH", "priority-table drift did not fail closed")
    pair_count = 0
    for fixture in fixtures["ordered_error_pairs"]:
        observed = priority_winner([fixture["first"], fixture["second"]])
        if observed != fixture["expected"]:
            raise ResolutionFailure("OUTPUT_MISMATCH", f"ordered pair mismatch: {fixture}")
        pair_count += 1
    return {
        "status": "PASS",
        "authority": "zero",
        "custody_negative_matrix": custody_results,
        "custody_negative_count": len(custody_results),
        "inherited_and_cross_phase_collisions": collision_results,
        "priority_table_drift": {"expected": "UNRESOLVED_CONTRADICTION", "observed": drift_observed},
        "quarantined_post_snapshot_mutations": quarantine_results,
        "ordered_error_pairs_checked": pair_count,
        "source_fields_sha256": V8_SOURCE_FIELDS_SHA256,
        "origin_rows_sha256": V8_ORIGIN_ROWS_SHA256,
        "resolution_input": {"size_bytes": len(input_raw), "sha256": sha256(input_raw)},
        "resolved_contract": {"size_bytes": len(resolved_raw), "sha256": sha256(resolved_raw)},
        "origin_trace": {"size_bytes": len(origin_raw), "sha256": sha256(origin_raw)},
        "experiment_runs_consumed": 0,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[ROOT_FROM_FILE])
    parser.add_argument("--strategy", choices=("latest_entry", "ordered_entry", "both"), default="both")
    parser.add_argument("--emit", choices=("summary", "resolution-input", "resolved-contract", "origin-trace"), default="summary")
    parser.add_argument("--materialize", action="store_true", help="write only the three declared generated v9 JSON artifacts")
    parser.add_argument("--self-test", action="store_true", help="run the frozen deterministic static matrix")
    parser.add_argument("--diagnostic-pair", nargs=2, metavar=("FIRST", "SECOND"))
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    root = args.root.resolve()
    if args.diagnostic_pair:
        sys.stdout.buffer.write(canonical_bytes({
            "first": args.diagnostic_pair[0],
            "second": args.diagnostic_pair[1],
            "winner": priority_winner(list(args.diagnostic_pair)),
        }))
        return 0
    if args.self_test:
        sys.stdout.buffer.write(canonical_bytes(run_self_test(root)))
        return 0
    strategies = ["latest_entry", "ordered_entry"] if args.strategy == "both" else [args.strategy]
    input_raw, resolved_raw, origin_raw, summary = resolve(root, strategies, materialize_input=args.materialize)
    if args.materialize:
        for relative, raw in ((DEFAULT_INPUT, input_raw), (DEFAULT_RESOLVED, resolved_raw), (DEFAULT_ORIGIN, origin_raw)):
            path = repository_path(root, relative)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
    else:
        compare_materialized(root, DEFAULT_INPUT, input_raw)
        compare_materialized(root, DEFAULT_RESOLVED, resolved_raw)
        compare_materialized(root, DEFAULT_ORIGIN, origin_raw)
    emissions = {
        "summary": canonical_bytes(summary),
        "resolution-input": input_raw,
        "resolved-contract": resolved_raw,
        "origin-trace": origin_raw,
    }
    sys.stdout.buffer.write(emissions[args.emit])
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ResolutionFailure as exc:
        sys.stderr.buffer.write(canonical_bytes({
            "code": exc.code,
            "detail": exc.detail,
            "diagnostics": exc.diagnostics,
            "status": "FAIL",
        }))
        raise SystemExit(2)
