#!/usr/bin/env python3
"""Deterministic public-entry resolver for EXP-INSTR-36c8cf amendment v10.

This is a static control-plane program.  It never executes an experiment, the
research harness, Phase B, JINV work, elliptic-curve arithmetic, rho, or BSGS.
The exact v9 payload is data, not executable code.  The pinned dispatcher is
loaded from exact bytes into a side-effect-free definition namespace: no
module import, sys.modules mutation, bytecode, or repository output occurs.
"""

from __future__ import annotations

import argparse
import ast
import builtins
import copy
import hashlib
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from types import SimpleNamespace
from typing import Any, Callable, Protocol, Sequence


sys.dont_write_bytecode = True


EXPERIMENT_ID = "EXP-INSTR-36c8cf"
VERSION = 10
BASE = "experiments/EXP-INSTR-36c8cf/amendments/v10-1f543e"
DEFAULT_INPUT = f"{BASE}/resolution-input.json"
DEFAULT_RESOLVED = f"{BASE}/resolved-contract.json"
DEFAULT_ORIGIN = f"{BASE}/origin-trace.json"

V9_BASE = "experiments/EXP-INSTR-36c8cf/amendments/v9-e9e3bf"
V9_AMENDMENT = "experiments/EXP-INSTR-36c8cf/amendments/v9-e9e3bf.yaml"
V9_RESOLVER = f"{V9_BASE}/resolver.py"
V9_INPUT = f"{V9_BASE}/resolution-input.json"
V9_RESOLVED = f"{V9_BASE}/resolved-contract.json"
V9_ORIGIN = f"{V9_BASE}/origin-trace.json"

V9_SOURCE_FIELDS_SHA256 = "a15dd1116fff1593440c82e91083e6744eb84c5d05615c554c23902480e9717b"
V9_ORIGIN_ROWS_SHA256 = "d90a95aafbdc06a90a18587003595f1f19f12ae83bfaf8a9ba3f259ed922e413"

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

V9_PACKAGE = (
    ("amendment_v9", V9_AMENDMENT, 5211, "2237499428c0039f38bc760f4799fe742dd8dbadb59236a93c3a67db5f6b6bff"),
    ("v9_resolver", V9_RESOLVER, 52053, "cc883b9c7891439eb3533940ab399f1a764722d843b4bbda68697b9f15de4b2d"),
    ("v9_resolution_input", V9_INPUT, 443949, "3e42be2567002e89a0ff9dd7c43e831da0bf2d02ef4d425618d81cf3f3a0a551"),
    ("v9_resolved_contract", V9_RESOLVED, 580624, "23d05e05b1a991f811d5a4a9908fbcf44b00c0f5fc020beda2446ebd32462b62"),
    ("v9_origin_trace", V9_ORIGIN, 1200794, "b272bca282de54152c816aa6e357e6e99d872c810633d5ad5f5c2e262c688394"),
)

QUEUE_PATH = "coordination/goals/GOAL-ENDO-001/batches/BATCH-d7e255/instr-v9-role-capability-reconciliation/dispatch_queue.json"
RECEIPT_PATH = "coordination/goals/GOAL-ENDO-001/batches/BATCH-d7e255/instr-v9-role-capability-reconciliation/archives/TASK-20260813-a7fc5a/snapshot-receipt.json"
REVIEW_PATH = "coordination/goals/GOAL-ENDO-001/batches/BATCH-d7e255/instr-v9-role-capability-reconciliation/reviews/TASK-20260813-9c2c62/red-team-report.yaml"
DETERMINATION_PATH = "coordination/goals/GOAL-ENDO-001/batches/BATCH-d7e255/instr-v9-role-capability-reconciliation/decisions/TASK-20260813-7dfb90/approval-determination.yaml"
EVIDENCE_PATH = "ledger/evidence/EV-INSTR-cba55e.yaml"
DECISION_PATH = "ledger/decisions/DEC-20260813-638fb4.yaml"
LEDGER_RECEIPT_PATH = "coordination/goals/GOAL-ENDO-001/batches/BATCH-d7e255/instr-v9-role-capability-reconciliation/archives/TASK-20260813-eb0b02/ledger-receipt.json"
DISPATCHER_PATH = "tools/research_dispatch.py"

QUEUE_SIZE = 39291
QUEUE_RAW_SHA256 = "f89c5ca62bb71a7683183ace8ba7251fd0149fd012a1c84fef21db35e6ee2e97"
PLAN_SOURCE_QUEUE_SHA256 = "3976086f62ab13cacdb331e9e6cb98f92c3284787b275da0e9fbf845d2f7da59"
PLAN_SHA256 = "be27b77d8d9d25d61a7eaf08a7174fc00d97dd13951758cea13ec73d7f458ca4"
PLAN_PRETTY_SIZE = 1963
PLAN_PRETTY_SHA256 = "1e8902c308ddea445dd6351c7f68843bd637353cfa6571fbaf6887b79452c4fa"

RECEIPT_SIZE = 5357
RECEIPT_SHA256 = "5c1fed24fdaffaa470b7c30d302f7c4c0e32ead39defc2d75d1d7270da191584"
REVIEW_SIZE = 37502
REVIEW_SHA256 = "b26c36d1ba270315508ff03c166be1fae8ef6937b6185a13d2ea923ae43d60a4"
DETERMINATION_SIZE = 18754
DETERMINATION_SHA256 = "a1ed394860e6802b5496b2c786ae8a676c01c883ee96890f0944d1b5908644ac"
EVIDENCE_SIZE = 11756
EVIDENCE_SHA256 = "6f9b4d4602cd459f45bb67faf33dd832cca073884a7b9682e6c8cc319b43b0a0"
DECISION_SIZE = 13983
DECISION_SHA256 = "871610148030bf320471eced2d0c2530fd9f35743169bf288a4a5726b5533ecb"
LEDGER_RECEIPT_SIZE = 7277
LEDGER_RECEIPT_SHA256 = "e8259d443703b23a7d5530fddd93b96e3cdf9b6603820d51e09ae9c5f599ead3"
DISPATCHER_SIZE = 56104
DISPATCHER_SHA256 = "04878bf31e1da2b24f43adfa214b744a125039651233d7357889731b0b0f397a"

SNAPSHOT_TASK = "TASK-20260813-a7fc5a"
SNAPSHOT_COMMIT = "4598bea48a5a050aa27b3be5223de32bc5d7be70"
SNAPSHOT_PARENT = "3d1f6065e752efe252907798db1072d907307ae7"
LEDGER_COMMIT = "12fc0488c69c27d3e65cd4b75b874d289616d250"
LEDGER_PARENT = "e27aa20329f9a51c3ab2da04546e2ccf9a1dbef0"
MERGED_MAIN_COMMIT = "241a7dcc47f9b6cc95a0c76783f0d60491d04c00"

SNAPSHOT_PATH_HASHES = {
    V9_AMENDMENT: V9_PACKAGE[0][3],
    V9_RESOLVER: V9_PACKAGE[1][3],
    V9_INPUT: V9_PACKAGE[2][3],
    V9_RESOLVED: V9_PACKAGE[3][3],
    V9_ORIGIN: V9_PACKAGE[4][3],
    RECEIPT_PATH: RECEIPT_SHA256,
}
SNAPSHOT_PATHS = tuple(SNAPSHOT_PATH_HASHES)
REQUIRED_MESSAGE_IDS = (
    "GOAL-ENDO-001",
    "BATCH-d7e255",
    EXPERIMENT_ID,
    "TASK-20260813-e9e3bf",
    SNAPSHOT_TASK,
)
EXPECTED_TOPOLOGY = {
    "TASK-20260813-e9e3bf": ("executor", ()),
    SNAPSHOT_TASK: ("coordinator", ("TASK-20260813-e9e3bf",)),
    "TASK-20260813-9c2c62": ("red-team", ("TASK-20260813-e9e3bf", SNAPSHOT_TASK)),
    "TASK-20260813-7dfb90": ("coordinator", ("TASK-20260813-9c2c62",)),
    "TASK-20260813-eb0b02": ("coordinator", ("TASK-20260813-9c2c62", "TASK-20260813-7dfb90")),
}

CONTROL_BINDINGS = (
    ("v9_snapshot_receipt", RECEIPT_PATH, RECEIPT_SIZE, RECEIPT_SHA256),
    ("v9_red_team", REVIEW_PATH, REVIEW_SIZE, REVIEW_SHA256),
    ("v9_determination", DETERMINATION_PATH, DETERMINATION_SIZE, DETERMINATION_SHA256),
    ("v9_evidence", EVIDENCE_PATH, EVIDENCE_SIZE, EVIDENCE_SHA256),
    ("v9_decision", DECISION_PATH, DECISION_SIZE, DECISION_SHA256),
    ("v9_ledger_receipt", LEDGER_RECEIPT_PATH, LEDGER_RECEIPT_SIZE, LEDGER_RECEIPT_SHA256),
)

EXPECTED_ARTIFACTS: dict[str, dict[str, Any]] = {
    DEFAULT_INPUT: {
        "size_bytes": 506961,
        "sha256": "7c778a6974c78cf1b502feda55e42cc1971bcc89e4017531505aa965c6c2ade9",
    },
    DEFAULT_RESOLVED: {
        "size_bytes": 643637,
        "sha256": "f52e0f939f36d0e75f7ac3b6bcb3a7165cb239beadffafc5c1913cf7c9d6927d",
    },
    DEFAULT_ORIGIN: {
        "size_bytes": 1201829,
        "sha256": "18f0f208dfd98bda174eebe232afd90d28ba06be1e1fb42f8c8afd857b0f42eb",
    },
}

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


def repository_path(root: Path, relative: str) -> Path:
    if not isinstance(relative, str) or not relative or relative.startswith("/"):
        raise ResolutionFailure("UNEXPECTED_SOURCE", f"invalid repository path {relative!r}")
    target = (root / relative).resolve()
    try:
        target.relative_to(root.resolve())
    except ValueError as exc:
        raise ResolutionFailure("UNEXPECTED_SOURCE", f"path escapes repository: {relative!r}") from exc
    return target


@dataclass(frozen=True)
class Diagnostic:
    code: str
    detail: str
    phase: str


class DiagnosticCollector:
    """The one compiled-order collector used by each public resolve call."""

    def __init__(self, compiled_priority: tuple[dict[str, Any], ...]):
        self._compiled_priority = tuple(copy.deepcopy(compiled_priority))
        self._items: list[Diagnostic] = []
        self._adjudicated = False

    def add(self, code: str, detail: str, phase: str) -> None:
        if code not in PRIORITY_BY_CODE:
            detail = f"unknown diagnostic {code!r}: {detail}"
            code = "UNRESOLVED_CONTRADICTION"
            phase = f"{phase}:normalization"
        self._items.append(Diagnostic(code, str(detail), str(phase)))

    def merge_nested(self, phase: str, exc: ResolutionFailure) -> None:
        if not exc.diagnostics:
            self.add(exc.code, exc.detail, phase)
            return
        for row in exc.diagnostics:
            if not isinstance(row, dict):
                self.add(
                    "UNRESOLVED_CONTRADICTION",
                    f"malformed nested diagnostic: {row!r}",
                    f"{phase}:nested",
                )
                continue
            nested_phase = row.get("phase", "unknown")
            self.add(
                str(row.get("code", "UNRESOLVED_CONTRADICTION")),
                str(row.get("detail", "nested diagnostic omitted detail")),
                f"{phase}>{nested_phase}",
            )

    def capture(self, phase: str, default_code: str, action: Callable[[], Any]) -> Any:
        try:
            return action()
        except ResolutionFailure as exc:
            self.merge_nested(phase, exc)
        except Exception as exc:
            self.add(default_code, f"{type(exc).__name__}: {exc}", phase)
        return None

    def compare_source_table(self, source_table: Any, phase: str) -> None:
        if source_table != list(self._compiled_priority):
            self.add(
                "UNRESOLVED_CONTRADICTION",
                "source priority table differs from immutable COMPILED_PRIORITY",
                phase,
            )

    def diagnostics(self) -> list[dict[str, Any]]:
        unique = {(item.code, item.detail, item.phase): item for item in self._items}
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

    def final_adjudication(self) -> list[dict[str, Any]]:
        if self._adjudicated:
            raise RuntimeError("compiled adjudicator called more than once")
        self._adjudicated = True
        diagnostics = self.diagnostics()
        if diagnostics:
            winner = diagnostics[0]
            raise ResolutionFailure(winner["code"], winner["detail"], diagnostics)
        return diagnostics


_MISSING = object()


class ReadView:
    """Read-only path overlay used to replay public-entry negative controls."""

    def __init__(self, overrides: dict[str, bytes | object] | None = None):
        self._overrides = dict(overrides or {})

    def read(self, root: Path, relative: str) -> bytes:
        if relative in self._overrides:
            value = self._overrides[relative]
            if value is _MISSING:
                raise FileNotFoundError(relative)
            if not isinstance(value, bytes):
                raise TypeError(f"virtual source for {relative} is not bytes")
            return value
        return repository_path(root, relative).read_bytes()


@dataclass(frozen=True)
class FaultFixture:
    fixture_id: str
    plan_mutation: str | None = None
    dispatcher_output_mismatch: bool = False
    input_generation_output_mismatch: bool = False
    nested_failure: ResolutionFailure | None = None


def _read_bound_sources(
    root: Path,
    view: ReadView,
    collector: DiagnosticCollector,
) -> dict[str, bytes]:
    raw_by_path: dict[str, bytes] = {}
    for source_id, relative, size, digest in V9_PACKAGE:
        raw = collector.capture(
            f"lineage:{source_id}:read",
            "MISSING_SOURCE",
            lambda relative=relative: view.read(root, relative),
        )
        if not isinstance(raw, bytes):
            continue
        raw_by_path[relative] = raw

        def verify(raw: bytes = raw, relative: str = relative, size: int = size, digest: str = digest) -> None:
            if len(raw) != size:
                raise ResolutionFailure("SOURCE_SIZE", f"{relative}: expected {size}, observed {len(raw)}")
            observed = sha256(raw)
            if observed != digest:
                raise ResolutionFailure("SOURCE_SHA256", f"{relative}: expected {digest}, observed {observed}")

        collector.capture(f"lineage:{source_id}:binding", "SOURCE_SHA256", verify)
    return raw_by_path


def _parse_bound_json(
    raw_by_path: dict[str, bytes],
    relative: str,
    collector: DiagnosticCollector,
) -> Any:
    raw = raw_by_path.get(relative)
    if raw is None:
        collector.add("UNRESOLVED_CONTRADICTION", f"prerequisite unavailable: {relative}", "dependency")
        return None
    return collector.capture(
        f"dependency:{relative}:strict-parse",
        "DUPLICATE_KEY",
        lambda: strict_json(raw, relative),
    )


def _verify_control_bindings(root: Path, view: ReadView, collector: DiagnosticCollector) -> None:
    for source_id, relative, size, digest in CONTROL_BINDINGS:
        raw = collector.capture(
            f"custody-binding:{source_id}:read",
            "CUSTODY_ABSENT",
            lambda relative=relative: view.read(root, relative),
        )
        if not isinstance(raw, bytes):
            continue

        def verify(raw: bytes = raw, relative: str = relative, size: int = size, digest: str = digest) -> None:
            if len(raw) != size or sha256(raw) != digest:
                raise ResolutionFailure("CUSTODY_DISAGREEMENT", f"bound predecessor bytes drift: {relative}")

        collector.capture(f"custody-binding:{source_id}:verify", "CUSTODY_DISAGREEMENT", verify)


def _dispatcher_namespace(raw: bytes) -> Any:
    if len(raw) != DISPATCHER_SIZE or sha256(raw) != DISPATCHER_SHA256:
        raise ResolutionFailure("SOURCE_SHA256", "pinned dispatcher byte binding drift")
    source = raw.decode("utf-8")
    parsed = ast.parse(source, filename=DISPATCHER_PATH, mode="exec")
    allowed = (ast.Expr, ast.Assign, ast.AnnAssign, ast.ClassDef, ast.FunctionDef)
    body: list[ast.stmt] = []
    for node in parsed.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            continue
        if isinstance(node, ast.If):
            continue
        if not isinstance(node, allowed):
            raise ResolutionFailure(
                "UNRESOLVED_CONTRADICTION",
                f"unexpected top-level dispatcher AST node: {type(node).__name__}",
            )
        body.append(node)
    module = ast.fix_missing_locations(ast.Module(body=body, type_ignores=[]))
    namespace: dict[str, Any] = {
        "__builtins__": builtins.__dict__,
        "__name__": "_pinned_dispatcher_definition_namespace",
        "argparse": argparse,
        "hashlib": hashlib,
        "json": json,
        "re": re,
        "subprocess": subprocess,
        "sys": sys,
        "Path": Path,
        "PurePosixPath": PurePosixPath,
        "Any": Any,
        "Protocol": Protocol,
        "Sequence": Sequence,
    }
    code = compile(module, DISPATCHER_PATH, "exec", dont_inherit=True, optimize=0)
    exec(code, namespace, namespace)
    required = ("select", "GitRepositoryVerifier", "DispatchError")
    if any(name not in namespace for name in required):
        raise ResolutionFailure("UNRESOLVED_CONTRADICTION", "dispatcher definition namespace incomplete")
    return SimpleNamespace(**namespace)


def _git(root: Path, *args: str) -> bytes:
    completed = subprocess.run(
        ["git", "-C", str(root), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", "replace").strip()
        raise ResolutionFailure(
            "CUSTODY_DISAGREEMENT",
            f"git {' '.join(args)}: {detail or completed.returncode}",
        )
    return completed.stdout


def _find_task(queue: dict[str, Any], task_id: str) -> dict[str, Any] | None:
    tasks = queue.get("tasks")
    if not isinstance(tasks, list):
        return None
    matches = [row for row in tasks if isinstance(row, dict) and row.get("id") == task_id]
    return matches[0] if len(matches) == 1 else None


def _mutate_plan(plan: dict[str, Any], mutation: str | None) -> dict[str, Any]:
    result = copy.deepcopy(plan)
    if mutation is None:
        return result
    if mutation == "fabricated_authority":
        return {"content_only_archives": [{"task_id": SNAPSHOT_TASK, "paths_verified": 6}]}
    if mutation == "plan_drift":
        result["plan_sha256"] = "0" * 64
        return result
    if mutation == "gate_drift":
        result["gates"]["concurrency_cap_respected"] = False
        return result
    raise ResolutionFailure("OUTPUT_MISMATCH", f"unknown plan mutation: {mutation}")


def _collect_git_identity(root: Path, collector: DiagnosticCollector) -> None:
    for label, commit, parent in (
        ("snapshot", SNAPSHOT_COMMIT, SNAPSHOT_PARENT),
        ("ledger", LEDGER_COMMIT, LEDGER_PARENT),
    ):
        object_type = collector.capture(
            f"custody-git:{label}:type",
            "CUSTODY_DISAGREEMENT",
            lambda commit=commit: _git(root, "cat-file", "-t", commit),
        )
        if isinstance(object_type, bytes) and object_type.strip() != b"commit":
            collector.add("CUSTODY_DISAGREEMENT", f"{label} object is not a commit", f"custody-git:{label}")
        observed_parent = collector.capture(
            f"custody-git:{label}:parent",
            "CUSTODY_DISAGREEMENT",
            lambda commit=commit: _git(root, "rev-parse", f"{commit}^1"),
        )
        if isinstance(observed_parent, bytes) and observed_parent.decode("ascii", "replace").strip() != parent:
            collector.add("CUSTODY_DISAGREEMENT", f"{label} actual first parent drift", f"custody-git:{label}")
        collector.capture(
            f"custody-git:{label}:reachable",
            "CUSTODY_DISAGREEMENT",
            lambda commit=commit: _git(root, "merge-base", "--is-ancestor", commit, "HEAD"),
        )
    collector.capture(
        "custody-git:merged-main:type",
        "CUSTODY_DISAGREEMENT",
        lambda: _git(root, "cat-file", "-t", MERGED_MAIN_COMMIT),
    )
    collector.capture(
        "custody-git:merged-main:reachable",
        "CUSTODY_DISAGREEMENT",
        lambda: _git(root, "merge-base", "--is-ancestor", MERGED_MAIN_COMMIT, "HEAD"),
    )


def _collect_custody(
    root: Path,
    view: ReadView,
    collector: DiagnosticCollector,
    fixture: FaultFixture | None,
) -> dict[str, Any] | None:
    queue_raw = collector.capture(
        "custody:queue-read",
        "CUSTODY_ABSENT",
        lambda: view.read(root, QUEUE_PATH),
    )
    receipt_raw = collector.capture(
        "custody:receipt-read",
        "CUSTODY_ABSENT",
        lambda: view.read(root, RECEIPT_PATH),
    )
    dispatcher_raw = collector.capture(
        "dependency:dispatcher-read",
        "MISSING_SOURCE",
        lambda: view.read(root, DISPATCHER_PATH),
    )

    queue = None
    receipt = None
    dispatch = None
    plan = None
    if isinstance(queue_raw, bytes):
        queue = collector.capture(
            "custody:queue-strict-parse",
            "CUSTODY_DISAGREEMENT",
            lambda: strict_json(queue_raw, QUEUE_PATH),
        )
        if len(queue_raw) != QUEUE_SIZE or sha256(queue_raw) != QUEUE_RAW_SHA256:
            collector.add("CUSTODY_DISAGREEMENT", "terminal v9 queue raw-byte binding drift", "custody:queue")
    if isinstance(receipt_raw, bytes):
        receipt = collector.capture(
            "custody:receipt-strict-parse",
            "CUSTODY_DISAGREEMENT",
            lambda: strict_json(receipt_raw, RECEIPT_PATH),
        )
        if len(receipt_raw) != RECEIPT_SIZE or sha256(receipt_raw) != RECEIPT_SHA256:
            collector.add("CUSTODY_DISAGREEMENT", "v9 snapshot receipt raw-byte binding drift", "custody:receipt")
    if isinstance(dispatcher_raw, bytes):
        dispatch = collector.capture(
            "dependency:dispatcher-definition-load",
            "UNRESOLVED_CONTRADICTION",
            lambda: _dispatcher_namespace(dispatcher_raw),
        )

    if isinstance(queue, dict) and dispatch is not None:
        plan = collector.capture(
            "custody:dispatcher-selection",
            "CUSTODY_DISAGREEMENT",
            lambda: dispatch.select(queue, repository_verifier=dispatch.GitRepositoryVerifier(root)),
        )
        if isinstance(plan, dict) and fixture is not None and fixture.plan_mutation:
            plan = collector.capture(
                "custody:dispatcher-plan-fixture",
                "OUTPUT_MISMATCH",
                lambda: _mutate_plan(plan, fixture.plan_mutation),
            )
        if fixture is not None and fixture.dispatcher_output_mismatch:
            collector.add(
                "OUTPUT_MISMATCH",
                "frozen dispatcher output mismatch injected after prior lineage collection",
                "custody:dispatcher-output",
            )

    if isinstance(queue, dict):
        if queue.get("schema") != "crypto.autoresearch.dispatch_queue.v1":
            collector.add("CUSTODY_DISAGREEMENT", "queue schema drift", "custody:queue")
        if queue.get("goal_id") != "GOAL-ENDO-001" or queue.get("batch_id") != "BATCH-d7e255":
            collector.add("CUSTODY_DISAGREEMENT", "queue goal or batch drift", "custody:queue")
        tasks = queue.get("tasks")
        if not isinstance(tasks, list):
            collector.add("CUSTODY_ABSENT", "queue tasks absent", "custody:queue")
            tasks = []
        ids = [row.get("id") for row in tasks if isinstance(row, dict)]
        if len(ids) != len(tasks) or len(ids) != len(set(ids)):
            collector.add("CUSTODY_ABSENT", "nested, malformed, or duplicate queue tasks", "custody:queue")
        if set(ids) != set(EXPECTED_TOPOLOGY):
            collector.add("CUSTODY_DISAGREEMENT", "direct queue task set drift", "custody:queue")
        for task_id, (role, dependencies) in EXPECTED_TOPOLOGY.items():
            task = _find_task(queue, task_id)
            if task is None:
                collector.add("CUSTODY_ABSENT", f"queue task absent: {task_id}", "custody:queue")
                continue
            if task.get("role") != role:
                collector.add("CUSTODY_DISAGREEMENT", f"queue role drift: {task_id}", "custody:queue")
            if tuple(task.get("depends_on", ())) != dependencies:
                collector.add("CUSTODY_DISAGREEMENT", f"direct dependency topology drift: {task_id}", "custody:queue")
            if task.get("state") != "completed":
                collector.add("CUSTODY_DISAGREEMENT", f"terminal task is not completed: {task_id}", "custody:queue")

        archive_task = _find_task(queue, SNAPSHOT_TASK)
        archive = archive_task.get("archive") if isinstance(archive_task, dict) else None
        if not isinstance(archive, dict):
            collector.add("CUSTODY_ABSENT", "completed v9 snapshot archive absent", "custody:archive")
        else:
            checks = (
                (archive.get("commit_sha") == SNAPSHOT_COMMIT, "snapshot commit identity drift"),
                (archive.get("parent_sha") == SNAPSHOT_PARENT, "snapshot parent identity drift"),
                (archive.get("path_sha256") == SNAPSHOT_PATH_HASHES, "snapshot path hash set drift"),
                (archive.get("record_ids") == list(REQUIRED_MESSAGE_IDS), "snapshot required record IDs drift"),
                (archive.get("source_task_ids") == ["TASK-20260813-e9e3bf"], "snapshot source topology drift"),
                (archive.get("kind") == "snapshot", "snapshot archive kind drift"),
                (archive.get("binding_mode") == "content_first", "snapshot binding mode drift"),
            )
            for condition, detail in checks:
                if not condition:
                    collector.add("CUSTODY_DISAGREEMENT", detail, "custody:archive")

    if isinstance(receipt, dict):
        if receipt.get("task_id") != SNAPSHOT_TASK:
            collector.add("CUSTODY_DISAGREEMENT", "receipt task identity drift", "custody:receipt")
        if receipt.get("commit_sha") is not None:
            collector.add("CUSTODY_DISAGREEMENT", "self-neutral receipt claims its future commit", "custody:receipt")
        if receipt.get("paths") != list(SNAPSHOT_PATHS):
            collector.add("CUSTODY_DISAGREEMENT", "receipt path set drift", "custody:receipt")
        receipt_hashes = receipt.get("path_sha256")
        receipt_sizes = receipt.get("path_size_bytes")
        if not isinstance(receipt_hashes, dict) or not isinstance(receipt_sizes, dict):
            collector.add("CUSTODY_ABSENT", "receipt hash or size declarations absent", "custody:receipt")
        else:
            if receipt_hashes.get(RECEIPT_PATH) is not None or receipt_sizes.get(RECEIPT_PATH) is not None:
                collector.add("CUSTODY_DISAGREEMENT", "receipt illegally self-binds", "custody:receipt")
            for relative in SNAPSHOT_PATHS:
                if relative == RECEIPT_PATH:
                    continue
                current = collector.capture(
                    f"custody:receipt-current:{relative}",
                    "CUSTODY_ABSENT",
                    lambda relative=relative: view.read(root, relative),
                )
                if not isinstance(current, bytes):
                    continue
                if receipt_hashes.get(relative) != SNAPSHOT_PATH_HASHES[relative]:
                    collector.add("CUSTODY_DISAGREEMENT", f"receipt hash drift: {relative}", "custody:receipt")
                if receipt_sizes.get(relative) != len(current):
                    collector.add("CUSTODY_DISAGREEMENT", f"receipt size drift: {relative}", "custody:receipt")

    if isinstance(plan, dict):
        if plan.get("plan_sha256") != PLAN_SHA256:
            collector.add("CUSTODY_DISAGREEMENT", "canonical plan digest drift", "custody:plan")
        if plan.get("source_queue_sha256") != PLAN_SOURCE_QUEUE_SHA256:
            collector.add("CUSTODY_DISAGREEMENT", "canonical source queue digest drift", "custody:plan")
        gates = plan.get("gates")
        if not isinstance(gates, dict) or len(gates) != 10 or not all(gates.values()):
            collector.add("CUSTODY_DISAGREEMENT", "one or more canonical dispatcher gates failed", "custody:plan")
        if plan.get("dispatches") != []:
            collector.add("CUSTODY_DISAGREEMENT", "terminal v9 queue unexpectedly dispatches work", "custody:plan")
        terminal = plan.get("terminal")
        if not isinstance(terminal, list) or {row.get("id") for row in terminal if isinstance(row, dict)} != set(EXPECTED_TOPOLOGY):
            collector.add("CUSTODY_DISAGREEMENT", "terminal plan topology drift", "custody:plan")
        plan_raw = pretty_bytes(plan)
        if len(plan_raw) != PLAN_PRETTY_SIZE or sha256(plan_raw) != PLAN_PRETTY_SHA256:
            collector.add("CUSTODY_DISAGREEMENT", "canonical plan pretty-byte drift", "custody:plan")
        expected_content = [{
            "task_id": SNAPSHOT_TASK,
            "reason": "declared content_first binding mode",
            "paths_verified": 6,
            "generated_paths_skipped": [],
        }]
        if plan.get("content_only_archives") != expected_content:
            collector.add("CUSTODY_DISAGREEMENT", "content-first archive rendering drift", "custody:plan")

    _collect_git_identity(root, collector)
    _verify_control_bindings(root, view, collector)
    return plan if isinstance(plan, dict) else None


def _v9_lineage_object() -> list[dict[str, Any]]:
    return [
        {"source_id": source_id, "path": path, "size_bytes": size, "sha256": digest}
        for source_id, path, size, digest in V9_PACKAGE
    ]


def _custody_contract() -> dict[str, Any]:
    return {
        "mandatory_on_every_public_entry": True,
        "archive_task_id": SNAPSHOT_TASK,
        "commit_sha": SNAPSHOT_COMMIT,
        "parent_sha": SNAPSHOT_PARENT,
        "expected_content_paths": list(SNAPSHOT_PATHS),
        "path_sha256": SNAPSHOT_PATH_HASHES,
        "required_message_ids": list(REQUIRED_MESSAGE_IDS),
        "queue": {
            "path": QUEUE_PATH,
            "size_bytes": QUEUE_SIZE,
            "raw_sha256": QUEUE_RAW_SHA256,
        },
        "receipt": {
            "path": RECEIPT_PATH,
            "size_bytes": RECEIPT_SIZE,
            "sha256": RECEIPT_SHA256,
            "self_neutral": True,
        },
        "dispatcher": {
            "path": DISPATCHER_PATH,
            "size_bytes": DISPATCHER_SIZE,
            "sha256": DISPATCHER_SHA256,
            "loading": "exact_byte_bound_side_effect_free_AST_definition_namespace",
            "module_import": False,
            "bytecode_or_repository_state": False,
        },
        "canonical_plan": {
            "source_queue_sha256": PLAN_SOURCE_QUEUE_SHA256,
            "plan_sha256": PLAN_SHA256,
            "pretty_size_bytes": PLAN_PRETTY_SIZE,
            "pretty_sha256": PLAN_PRETTY_SHA256,
            "gate_count": 10,
            "all_gates_required": True,
            "paths_verified": 6,
            "generated_paths_skipped": [],
        },
        "direct_queue_topology": [
            {"task_id": task_id, "role": role, "depends_on": list(dependencies)}
            for task_id, (role, dependencies) in EXPECTED_TOPOLOGY.items()
        ],
        "terminal_ledger_commit": LEDGER_COMMIT,
        "terminal_ledger_parent": LEDGER_PARENT,
        "merged_main_commit": MERGED_MAIN_COMMIT,
        "failure_semantics": "typed_compiled_order_diagnostics_with_one_final_adjudication",
    }


def _conformance_fixtures() -> dict[str, Any]:
    pairs = [
        {
            "first": first,
            "second": second,
            "expected": first if PRIORITY_BY_CODE[first] <= PRIORITY_BY_CODE[second] else second,
        }
        for first in ERROR_CODES
        for second in ERROR_CODES
    ]
    return {
        "public_custody_matrix": [
            {
                "fixture_id": case,
                "expected": "CUSTODY_ABSENT" if case in CUSTODY_ABSENT_CASES else "CUSTODY_DISAGREEMENT",
                "strategies": ["latest_entry", "ordered_entry"],
            }
            for case in CUSTODY_CASES
        ],
        "public_custody_cell_count": 32,
        "temporal_collisions": [
            {
                "fixture_id": "prior_source_sha_then_dispatcher_output_mismatch",
                "faults": ["SOURCE_SHA256", "OUTPUT_MISMATCH"],
                "expected": "SOURCE_SHA256",
                "strategies": ["latest_entry", "ordered_entry"],
            },
            {
                "fixture_id": "prior_source_sha_then_input_generation_output_mismatch",
                "faults": ["SOURCE_SHA256", "OUTPUT_MISMATCH"],
                "expected": "SOURCE_SHA256",
                "strategies": ["latest_entry", "ordered_entry"],
            },
        ],
        "temporal_collision_cell_count": 4,
        "inherited_v8_actual_input_collisions": [
            {
                "fixture_id": "missing_disposition_plus_invalid_class",
                "expected": "PATH_DISPOSITION_MISSING",
                "required_codes": ["PATH_DISPOSITION_MISSING", "OWNERLESS_FIELD", "OUTPUT_MISMATCH"],
            },
            {
                "fixture_id": "missing_pointer_plus_edge_id_drift",
                "expected": "OVERRIDE_POINTER_MISSING",
                "required_codes": ["OVERRIDE_POINTER_MISSING", "UNRESOLVED_CONTRADICTION", "OUTPUT_MISMATCH"],
            },
        ],
        "cross_phase_collisions": [
            {"faults": ["SOURCE_SHA256", "CUSTODY_DISAGREEMENT"], "expected": "SOURCE_SHA256"},
            {"faults": ["CUSTODY_ABSENT", "PATH_DISPOSITION_MISSING"], "expected": "CUSTODY_ABSENT"},
            {"faults": ["OVERRIDE_OWNER_MISMATCH", "AUTHORITY_NONZERO"], "expected": "OVERRIDE_OWNER_MISMATCH"},
            {"faults": ["RNG_FIXTURE_DRIFT", "OUTPUT_MISMATCH"], "expected": "RNG_FIXTURE_DRIFT"},
            {"faults": ["DUPLICATE_KEY", "EXCLUDED_FINGERPRINT"], "expected": "EXCLUDED_FINGERPRINT"},
        ],
        "priority_table_drift": {
            "mutation": "reverse_source_table",
            "expected": "UNRESOLVED_CONTRADICTION",
        },
        "ordered_error_pairs": pairs,
        "ordered_error_pair_count": len(pairs),
        "ordered_error_pair_insertion_orders": 2,
        "quarantined_mutation_count": 2,
        "nested_diagnostic_merge_required": True,
        "experiment_runs_consumed": 0,
    }


def generate_input(v9_input: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(v9_input)
    result["schema"] = "crypto.autoresearch.resolution_input.v10"
    result["version"] = VERSION
    composition = result["composition"]
    composition["controlling_v9_disposition"] = {
        "decision_id": "DEC-20260813-638fb4",
        "disposition": "not_approved_revise",
        "material_findings": ["O-INSTR-V9-1"],
        "scientific_effect": "none",
    }
    composition["v9_package_manifest"] = _v9_lineage_object()
    composition["snapshot_custody"] = _custody_contract()
    composition["error_priority"] = list(COMPILED_PRIORITY)
    composition["global_diagnostic_contract"] = {
        "collector_count_per_public_resolve": 1,
        "collector_constructed_from": "immutable_COMPILED_PRIORITY",
        "collector_is_first_public_resolve_object": True,
        "all_fallible_stages_typed_and_captured": True,
        "independent_stages_continue_after_capture": True,
        "nested_diagnostics_merged": True,
        "deterministic_deduplication_and_sort": True,
        "final_adjudicator_count_per_public_resolve": 1,
        "final_adjudicator_is_only_selector_or_raiser": True,
        "source_table_drift": "UNRESOLVED_CONTRADICTION_under_compiled_order",
        "traversal_strategy_and_exception_timing_may_not_select": True,
        "compiled_priority_table": list(COMPILED_PRIORITY),
        "compiled_error_count": 25,
    }
    resolver_contract = copy.deepcopy(composition["resolver_contract"])
    resolver_contract.update({
        "canonical_output_framing": "v10_sorted_compact_UTF8_JSON_exactly_one_terminal_LF",
        "custody_optional": False,
        "public_entry_collector": "constructed_first_from_immutable_compiled_order",
        "public_entry_stage_capture": "typed_all_fallible_stages",
        "public_entry_independent_continuation": True,
        "nested_diagnostic_merge": True,
        "sole_final_adjudication": True,
        "dependency_loading": "side_effect_free_exact_byte_AST_definition_namespace",
        "effectful_module_import": False,
        "normal_entry_without_authenticated_custody": "prohibited",
        "v9_scientific_source_payload": "byte_preserved_under_two_subdigests",
    })
    composition["resolver_contract"] = resolver_contract
    static = copy.deepcopy(composition["static_conformance_fixtures"])
    static["v10"] = _conformance_fixtures()
    composition["static_conformance_fixtures"] = static
    composition["v9_payload_binding"] = {
        "source_fields_sha256": V9_SOURCE_FIELDS_SHA256,
        "origin_rows_sha256": V9_ORIGIN_ROWS_SHA256,
        "canonical_subdigest_framing": "sorted_compact_UTF8_JSON_plus_exactly_one_LF",
        "source_field_count": 1363,
        "origin_row_count": 1363,
        "scientific_or_source_change": False,
    }
    return result


def _collect_input_diagnostics(
    input_object: Any,
    expected_input: dict[str, Any] | None,
    collector: DiagnosticCollector,
) -> None:
    if not isinstance(input_object, dict):
        collector.add("UNRESOLVED_CONTRADICTION", "v10 input is not a mapping", "input")
        return
    if input_object.get("schema") != "crypto.autoresearch.resolution_input.v10" or input_object.get("version") != VERSION:
        collector.add("VERSION_CHAIN", "v10 input schema or version drift", "input:version")
    if input_object.get("experiment_id") != EXPERIMENT_ID:
        collector.add("VERSION_CHAIN", "experiment identity drift", "input:version")
    composition = input_object.get("composition")
    if not isinstance(composition, dict):
        collector.add("UNRESOLVED_CONTRADICTION", "composition is not a mapping", "input")
        collector.add("OUTPUT_MISMATCH", "v10 input differs from generated contract", "input")
        return
    collector.compare_source_table(composition.get("error_priority"), "input:priority")
    if expected_input is None:
        collector.add("UNRESOLVED_CONTRADICTION", "generated v10 input prerequisite unavailable", "input")
        return
    expected_composition = expected_input["composition"]
    if input_object.get("authority") != expected_input.get("authority"):
        collector.add("AUTHORITY_NONZERO", "v10 authority boundary drift", "input:authority")
    for field, code in (
        ("snapshot_custody", "CUSTODY_DISAGREEMENT"),
        ("v9_package_manifest", "SOURCE_SHA256"),
        ("resolver_contract", "GENERIC_MERGE"),
        ("global_diagnostic_contract", "GENERIC_MERGE"),
    ):
        if composition.get(field) != expected_composition.get(field):
            collector.add(code, f"v10 {field} drift", f"input:{field}")

    rows = composition.get("source_leaf_disposition")
    expected_rows = expected_composition.get("source_leaf_disposition")
    if not isinstance(rows, list):
        collector.add("PATH_DISPOSITION_MISSING", "source disposition table absent", "input:disposition")
        rows = []
    if isinstance(expected_rows, list):
        expected_keys = {
            (row.get("source_id"), row.get("source_pointer"))
            for row in expected_rows
            if isinstance(row, dict)
        }
        counts: dict[tuple[Any, Any], int] = {}
        invalid_rows = []
        for row in rows:
            if not isinstance(row, dict):
                invalid_rows.append(row)
                continue
            key = (row.get("source_id"), row.get("source_pointer"))
            counts[key] = counts.get(key, 0) + 1
            if row.get("disposition") not in {"executable-owned", "excluded-provenance", "common-metadata"}:
                invalid_rows.append(row)
        observed_keys = set(counts)
        if expected_keys - observed_keys:
            collector.add("PATH_DISPOSITION_MISSING", "one or more source disposition rows are missing", "input:disposition")
        if any(count > 1 for count in counts.values()):
            collector.add("PATH_DISPOSITION_DUPLICATE", "one or more source disposition rows are duplicated", "input:disposition")
        if invalid_rows:
            collector.add("OWNERLESS_FIELD", "invalid or ownerless source disposition row", "input:disposition")
        if observed_keys - expected_keys:
            collector.add("OWNERLESS_FIELD", "source disposition key is outside the exact key set", "input:disposition")
        if rows != expected_rows and not (expected_keys - observed_keys) and not invalid_rows and not (observed_keys - expected_keys):
            collector.add("DUAL_OWNER_FIELD", "source disposition classification or order drift", "input:disposition")

    edges = composition.get("allowed_overrides")
    expected_edges = expected_composition.get("allowed_overrides")
    if not isinstance(edges, list):
        collector.add("UNRESOLVED_CONTRADICTION", "override edge table absent", "input:override")
        edges = []
    if isinstance(expected_edges, list):
        expected_ids = {row.get("edge_id") for row in expected_edges if isinstance(row, dict)}
        observed_ids = [row.get("edge_id") for row in edges if isinstance(row, dict)]
        if set(observed_ids) != expected_ids or len(observed_ids) != len(set(observed_ids)):
            collector.add("UNRESOLVED_CONTRADICTION", "override edge ID set drift", "input:override")
        expected_by_id = {row.get("edge_id"): row for row in expected_edges if isinstance(row, dict)}
        for edge in edges:
            if not isinstance(edge, dict):
                collector.add("UNRESOLVED_CONTRADICTION", "override edge is not a mapping", "input:override")
                continue
            edge_id = edge.get("edge_id")
            expected_edge = expected_by_id.get(edge_id)
            if expected_edge is None:
                continue
            for pointer_field in ("predecessor_pointer", "successor_pointer"):
                pointer = edge.get(pointer_field)
                if pointer != expected_edge.get(pointer_field):
                    collector.add(
                        "OVERRIDE_POINTER_MISSING",
                        f"missing or drifted override pointer for {edge_id}:{pointer_field}",
                        "input:override",
                    )
            if edge != expected_edge:
                collector.add("UNRESOLVED_CONTRADICTION", f"override edge content drift: {edge_id}", "input:override")

    if input_object != expected_input:
        collector.add("OUTPUT_MISMATCH", "v10 input differs from the complete generated contract", "input")


def _verify_quarantines(root: Path, collector: DiagnosticCollector) -> list[dict[str, Any]]:
    cases = (
        ("b480bae05e1a9a040f57f21a333953bde10a9fe2", "experiments/EXP-INSTR-36c8cf/amendments/v6.yaml", "44a217ffddfa4a7f60f377b54fcc3eb4043efef79c905cde8ac8755f5b17396f"),
        ("b7cb136f026a384dc1ef244bea1be2fec5f8684e", "experiments/EXP-INSTR-36c8cf/amendments/v7.yaml", "58e3c2b0d78bd95e4c7a76e67b0175aff70c651ccc523f7a2895bbbae93152cc"),
    )
    results: list[dict[str, Any]] = []
    for commit, path, digest in cases:
        raw = collector.capture(
            f"quarantine:{commit}:git-show",
            "CUSTODY_DISAGREEMENT",
            lambda commit=commit, path=path: _git(root, "show", f"{commit}:{path}"),
        )
        observed = "EXCLUDED_FINGERPRINT" if isinstance(raw, bytes) and sha256(raw) == digest else "NOT_REJECTED"
        if observed != "EXCLUDED_FINGERPRINT":
            collector.add("OUTPUT_MISMATCH", f"quarantined mutation not rejected: {commit}:{path}", "quarantine")
        results.append({"commit": commit, "path": path, "expected": "EXCLUDED_FINGERPRINT", "observed": observed})
    return results


def _verify_v9_payload(
    v9_resolved: Any,
    v9_origin: Any,
    collector: DiagnosticCollector,
) -> None:
    if not isinstance(v9_resolved, dict):
        collector.add("UNRESOLVED_CONTRADICTION", "v9 resolved contract unavailable", "payload")
    else:
        source_fields = v9_resolved.get("source_fields")
        if not isinstance(source_fields, dict) or len(source_fields) != 1363:
            collector.add("OUTPUT_MISMATCH", "v9 source_fields count drift", "payload")
        elif sha256(canonical_bytes(source_fields)) != V9_SOURCE_FIELDS_SHA256:
            collector.add("OUTPUT_MISMATCH", "v9 source_fields subdigest drift", "payload")
    if not isinstance(v9_origin, dict):
        collector.add("UNRESOLVED_CONTRADICTION", "v9 origin trace unavailable", "payload")
    else:
        rows = v9_origin.get("rows")
        if not isinstance(rows, list) or len(rows) != 1363:
            collector.add("OUTPUT_MISMATCH", "v9 origin rows count drift", "payload")
        elif sha256(canonical_bytes(rows)) != V9_ORIGIN_ROWS_SHA256:
            collector.add("OUTPUT_MISMATCH", "v9 origin rows subdigest drift", "payload")


def _derive_outputs(
    input_object: dict[str, Any],
    input_raw: bytes,
    v9_resolved: dict[str, Any],
    v9_origin: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    input_binding = {"path": DEFAULT_INPUT, "size_bytes": len(input_raw), "sha256": sha256(input_raw)}
    resolved = copy.deepcopy(v9_resolved)
    resolved["schema"] = "crypto.autoresearch.resolved_contract.v10"
    resolved["version"] = VERSION
    resolved["resolution_input"] = input_binding
    resolved["authority"] = copy.deepcopy(input_object["authority"])
    resolved["preservation"] = copy.deepcopy(input_object["preservation"])
    composition = resolved["composition"]
    input_composition = input_object["composition"]
    for field in (
        "controlling_v9_disposition",
        "error_priority",
        "global_diagnostic_contract",
        "resolver_contract",
        "snapshot_custody",
        "static_conformance_fixtures",
        "v9_package_manifest",
        "v9_payload_binding",
    ):
        composition[field] = copy.deepcopy(input_composition[field])
    source_fields = resolved["source_fields"]
    resolved["source_fields_sha256"] = sha256(canonical_bytes(source_fields))

    origin = copy.deepcopy(v9_origin)
    origin["schema"] = "crypto.autoresearch.origin_trace.v10"
    origin["version"] = VERSION
    origin["resolution_input"] = input_binding
    origin["v10_composition_origin_rows"] = [
        {"owner_source_id": "amendment_v10", "resolved_field_path": path, "authority_role": "additive_control_plane_only"}
        for path in (
            "/composition/controlling_v9_disposition",
            "/composition/global_diagnostic_contract",
            "/composition/resolver_contract",
            "/composition/snapshot_custody",
            "/composition/static_conformance_fixtures/v10",
            "/composition/v9_package_manifest",
            "/composition/v9_payload_binding",
        )
    ]
    origin["rows_sha256"] = sha256(canonical_bytes(origin["rows"]))
    return resolved, origin


def _compare_materialized(root: Path, view: ReadView, relative: str, generated: bytes) -> None:
    actual = view.read(root, relative)
    if actual != generated:
        raise ResolutionFailure("OUTPUT_MISMATCH", f"materialized bytes drift: {relative}")
    expected = EXPECTED_ARTIFACTS[relative]
    if expected["size_bytes"] is None or expected["sha256"] is None:
        raise ResolutionFailure("OUTPUT_MISMATCH", f"recorded size/hash absent: {relative}")
    if len(actual) != expected["size_bytes"] or sha256(actual) != expected["sha256"]:
        raise ResolutionFailure("OUTPUT_MISMATCH", f"recorded size/hash drift: {relative}")


def resolve(
    root: str | Path,
    strategies: list[str],
    *,
    materialize_input: bool = False,
    read_view: ReadView | None = None,
    fault_fixture: FaultFixture | None = None,
    compare_materialized: bool = True,
) -> tuple[bytes, bytes, bytes, dict[str, Any]]:
    collector = DiagnosticCollector(COMPILED_PRIORITY)

    root_path = collector.capture(
        "public-entry:root",
        "UNEXPECTED_SOURCE",
        lambda: Path(root).resolve(),
    )
    if not isinstance(root_path, Path):
        root_path = Path(".")
    view = collector.capture(
        "public-entry:read-view",
        "UNRESOLVED_CONTRADICTION",
        lambda: read_view if read_view is not None else ReadView(),
    )
    if not isinstance(view, ReadView):
        view = ReadView()

    raw_by_path = _read_bound_sources(root_path, view, collector)
    v9_input = _parse_bound_json(raw_by_path, V9_INPUT, collector)
    v9_resolved = _parse_bound_json(raw_by_path, V9_RESOLVED, collector)
    v9_origin = _parse_bound_json(raw_by_path, V9_ORIGIN, collector)

    expected_input = None
    if isinstance(v9_input, dict):
        expected_input = collector.capture(
            "input-generation:v10",
            "OUTPUT_MISMATCH",
            lambda: generate_input(v9_input),
        )
    else:
        collector.add("UNRESOLVED_CONTRADICTION", "v10 input generation prerequisite unavailable", "input-generation")
    if fault_fixture is not None and fault_fixture.input_generation_output_mismatch:
        collector.add(
            "OUTPUT_MISMATCH",
            "frozen input-generation mismatch injected after prior lineage collection",
            "input-generation:output",
        )

    input_object = None
    input_raw = None
    if materialize_input and isinstance(expected_input, dict):
        input_object = collector.capture(
            "input-generation:materialize-copy",
            "TYPE_COERCION",
            lambda: copy.deepcopy(expected_input),
        )
        if isinstance(input_object, dict):
            input_raw = collector.capture(
                "input-generation:canonicalize",
                "TYPE_COERCION",
                lambda: canonical_bytes(input_object),
            )
    else:
        input_raw_read = collector.capture(
            "public-entry:input-read",
            "MISSING_SOURCE",
            lambda: view.read(root_path, DEFAULT_INPUT),
        )
        if isinstance(input_raw_read, bytes):
            input_object = collector.capture(
                "public-entry:input-strict-parse",
                "DUPLICATE_KEY",
                lambda: strict_json(input_raw_read, DEFAULT_INPUT),
            )
            if isinstance(input_object, dict):
                input_raw = collector.capture(
                    "public-entry:input-canonicalize",
                    "TYPE_COERCION",
                    lambda: canonical_bytes(input_object),
                )
                if isinstance(input_raw, bytes) and input_raw != input_raw_read:
                    collector.add(
                        "OUTPUT_MISMATCH",
                        "v10 resolution input is not canonical compact JSON plus one LF",
                        "input",
                    )
    collector.capture(
        "input-validation",
        "UNRESOLVED_CONTRADICTION",
        lambda: _collect_input_diagnostics(input_object, expected_input, collector),
    )

    collector.capture(
        "custody-validation",
        "CUSTODY_DISAGREEMENT",
        lambda: _collect_custody(root_path, view, collector, fault_fixture),
    )
    quarantine_results = collector.capture(
        "quarantine-validation",
        "OUTPUT_MISMATCH",
        lambda: _verify_quarantines(root_path, collector),
    )
    collector.capture(
        "payload-validation",
        "OUTPUT_MISMATCH",
        lambda: _verify_v9_payload(v9_resolved, v9_origin, collector),
    )

    if fault_fixture is not None and fault_fixture.nested_failure is not None:
        collector.capture(
            "nested-resolver",
            "UNRESOLVED_CONTRADICTION",
            lambda: (_ for _ in ()).throw(fault_fixture.nested_failure),
        )

    resolved_raw = None
    origin_raw = None
    strategy_outputs: list[tuple[bytes, bytes]] = []
    if (
        isinstance(input_object, dict)
        and isinstance(input_raw, bytes)
        and isinstance(v9_resolved, dict)
        and isinstance(v9_origin, dict)
    ):
        for strategy in strategies:
            if strategy not in {"latest_entry", "ordered_entry"}:
                collector.add("ECOMP_LATEST_ONLY", f"unsupported strategy: {strategy}", "strategy")
                continue
            derived = collector.capture(
                f"output-derivation:{strategy}",
                "OUTPUT_MISMATCH",
                lambda: _derive_outputs(input_object, input_raw, v9_resolved, v9_origin),
            )
            if isinstance(derived, tuple) and len(derived) == 2:
                resolved_object, origin_object = derived
                encoded = collector.capture(
                    f"output-canonicalization:{strategy}",
                    "TYPE_COERCION",
                    lambda resolved_object=resolved_object, origin_object=origin_object: (
                        canonical_bytes(resolved_object),
                        canonical_bytes(origin_object),
                    ),
                )
                if isinstance(encoded, tuple):
                    strategy_outputs.append(encoded)
    else:
        collector.add("UNRESOLVED_CONTRADICTION", "output derivation prerequisite unavailable", "output")

    if not strategies:
        collector.add("ECOMP_LATEST_ONLY", "at least one entry strategy is mandatory", "strategy")
    if strategy_outputs:
        resolved_raw, origin_raw = strategy_outputs[0]
        if any(item != strategy_outputs[0] for item in strategy_outputs[1:]):
            collector.add("ECOMP_LATEST_ONLY", "entry strategies did not converge byte-identically", "strategy")
    else:
        collector.add("UNRESOLVED_CONTRADICTION", "no strategy produced output", "output")

    if compare_materialized and not materialize_input:
        if isinstance(input_raw, bytes):
            collector.capture(
                "output-comparison:resolution-input",
                "OUTPUT_MISMATCH",
                lambda: _compare_materialized(root_path, view, DEFAULT_INPUT, input_raw),
            )
        if isinstance(resolved_raw, bytes):
            collector.capture(
                "output-comparison:resolved-contract",
                "OUTPUT_MISMATCH",
                lambda: _compare_materialized(root_path, view, DEFAULT_RESOLVED, resolved_raw),
            )
        if isinstance(origin_raw, bytes):
            collector.capture(
                "output-comparison:origin-trace",
                "OUTPUT_MISMATCH",
                lambda: _compare_materialized(root_path, view, DEFAULT_ORIGIN, origin_raw),
            )

    collector.final_adjudication()
    assert isinstance(input_raw, bytes) and isinstance(resolved_raw, bytes) and isinstance(origin_raw, bytes)
    summary = {
        "authority": "zero",
        "custody": "authenticated_mandatory_public_entry",
        "dependency_loading": "side_effect_free_exact_byte_AST_definition_namespace",
        "experiment_id": EXPERIMENT_ID,
        "experiment_runs_consumed": 0,
        "final_adjudicator_calls": 1,
        "origin_rows_sha256": V9_ORIGIN_ROWS_SHA256,
        "origin_trace": {"size_bytes": len(origin_raw), "sha256": sha256(origin_raw)},
        "quarantined_post_snapshot_mutations": quarantine_results,
        "resolved_contract": {"size_bytes": len(resolved_raw), "sha256": sha256(resolved_raw)},
        "resolution_input": {"size_bytes": len(input_raw), "sha256": sha256(input_raw)},
        "source_fields_sha256": V9_SOURCE_FIELDS_SHA256,
        "status": "PASS",
        "strategies": strategies,
        "version": VERSION,
    }
    return input_raw, resolved_raw, origin_raw, summary


def _mutate_custody_sources(root: Path, case: str) -> tuple[ReadView, FaultFixture | None]:
    queue = strict_json(repository_path(root, QUEUE_PATH).read_bytes(), QUEUE_PATH)
    receipt = strict_json(repository_path(root, RECEIPT_PATH).read_bytes(), RECEIPT_PATH)
    overrides: dict[str, bytes | object] = {}
    fixture = None
    archive = _find_task(queue, SNAPSHOT_TASK)["archive"]
    if case == "omitted_custody":
        overrides[QUEUE_PATH] = _MISSING
        overrides[RECEIPT_PATH] = _MISSING
    elif case == "missing_receipt":
        overrides[RECEIPT_PATH] = _MISSING
    elif case == "malformed_commit":
        archive["commit_sha"] = "not-a-commit"
    elif case == "unreachable_commit":
        archive["commit_sha"] = "a" * 40
    elif case == "stale_commit":
        archive["commit_sha"] = SNAPSHOT_PARENT
    elif case == "fabricated_authority":
        fixture = FaultFixture(case, plan_mutation="fabricated_authority")
    elif case == "wrong_parent":
        archive["parent_sha"] = "b" * 40
    elif case == "extra_path":
        archive["path_sha256"]["unexpected/path"] = "0" * 64
    elif case == "hash_drift":
        archive["path_sha256"][V9_RESOLVED] = "0" * 64
    elif case == "queue_drift":
        queue["objective"] += " drift"
    elif case == "plan_drift":
        fixture = FaultFixture(case, plan_mutation="plan_drift")
    elif case == "topology_drift":
        queue["tasks"][2]["depends_on"] = [SNAPSHOT_TASK]
    elif case == "gate_drift":
        fixture = FaultFixture(case, plan_mutation="gate_drift")
    elif case == "schema_drift":
        queue["schema"] = "fabricated"
    elif case == "duplicate_task":
        queue["tasks"].append(copy.deepcopy(queue["tasks"][0]))
    elif case == "receipt_hash_drift":
        receipt["path_sha256"][V9_RESOLVED] = "f" * 64
        overrides[RECEIPT_PATH] = pretty_bytes(receipt)
    else:
        raise ResolutionFailure("UNRESOLVED_CONTRADICTION", f"unknown custody case: {case}")
    if queue != strict_json(repository_path(root, QUEUE_PATH).read_bytes(), QUEUE_PATH):
        overrides[QUEUE_PATH] = pretty_bytes(queue)
    return ReadView(overrides), fixture


def _mutate_actual_input(input_object: dict[str, Any], case: str) -> dict[str, Any]:
    result = copy.deepcopy(input_object)
    composition = result["composition"]
    if case == "missing_disposition_plus_invalid_class":
        rows = composition["source_leaf_disposition"]
        rows.pop(0)
        rows[0]["disposition"] = "invalid-class"
    elif case == "missing_pointer_plus_edge_id_drift":
        edges = composition["allowed_overrides"]
        edges[0]["successor_pointer"] = "/missing-v10-control-pointer"
        edges[1]["edge_id"] = "v10-drifted-edge-id"
    elif case == "priority_table_drift":
        composition["error_priority"] = list(reversed(COMPILED_PRIORITY))
    else:
        raise ResolutionFailure("UNRESOLVED_CONTRADICTION", f"unknown input case: {case}")
    return result


def _public_case(
    root: Path,
    strategy: str,
    *,
    view: ReadView | None = None,
    fixture: FaultFixture | None = None,
) -> dict[str, Any]:
    try:
        resolve(root, [strategy], read_view=view, fault_fixture=fixture)
    except ResolutionFailure as exc:
        diagnostics = exc.diagnostics
        if not diagnostics:
            raise AssertionError(f"typed failure omitted diagnostics: {exc}") from exc
        expected_sorted = sorted(
            diagnostics,
            key=lambda row: (row["priority"], row["code"], row["phase"], row["detail"]),
        )
        if diagnostics != expected_sorted:
            raise AssertionError("diagnostics are not in deterministic compiled order")
        identities = {(row["code"], row["detail"], row["phase"]) for row in diagnostics}
        if len(identities) != len(diagnostics):
            raise AssertionError("diagnostics are not deterministically deduplicated")
        return {"winner": exc.code, "diagnostics": diagnostics, "raw_exception": False}
    return {"winner": "PASS", "diagnostics": [], "raw_exception": False}


def _adjudicate_codes(codes: list[str]) -> dict[str, Any]:
    collector = DiagnosticCollector(COMPILED_PRIORITY)
    for index, code in enumerate(codes):
        collector.add(code, f"injected ordered fault {index}", "fixture")
    try:
        collector.final_adjudication()
    except ResolutionFailure as exc:
        return {"winner": exc.code, "diagnostics": exc.diagnostics}
    raise AssertionError("diagnostic fixture unexpectedly passed")


def run_self_test(root: Path) -> dict[str, Any]:
    input_raw, resolved_raw, origin_raw, positive = resolve(root, ["latest_entry", "ordered_entry"])
    input_object = strict_json(input_raw, DEFAULT_INPUT)

    custody_cells = []
    for case in CUSTODY_CASES:
        view, fixture = _mutate_custody_sources(root, case)
        expected = "CUSTODY_ABSENT" if case in CUSTODY_ABSENT_CASES else "CUSTODY_DISAGREEMENT"
        for strategy in ("latest_entry", "ordered_entry"):
            outcome = _public_case(root, strategy, view=view, fixture=fixture)
            if outcome["winner"] != expected:
                raise ResolutionFailure(
                    "OUTPUT_MISMATCH",
                    f"public custody cell {case}/{strategy}: expected {expected}, observed {outcome['winner']}",
                )
            custody_cells.append({
                "fixture_id": case,
                "strategy": strategy,
                "expected": expected,
                "observed": outcome["winner"],
                "diagnostics": outcome["diagnostics"],
                "raw_exception": outcome["raw_exception"],
            })

    corrupted_v9_resolver = bytearray(repository_path(root, V9_RESOLVER).read_bytes())
    corrupted_v9_resolver[-2] ^= 1
    temporal_cells = []
    temporal_fixtures = (
        FaultFixture(
            "prior_source_sha_then_dispatcher_output_mismatch",
            dispatcher_output_mismatch=True,
        ),
        FaultFixture(
            "prior_source_sha_then_input_generation_output_mismatch",
            input_generation_output_mismatch=True,
        ),
    )
    for fixture in temporal_fixtures:
        view = ReadView({V9_RESOLVER: bytes(corrupted_v9_resolver)})
        for strategy in ("latest_entry", "ordered_entry"):
            outcome = _public_case(root, strategy, view=view, fixture=fixture)
            codes = [row["code"] for row in outcome["diagnostics"]]
            if outcome["winner"] != "SOURCE_SHA256" or "OUTPUT_MISMATCH" not in codes:
                raise ResolutionFailure("OUTPUT_MISMATCH", f"temporal collision failed: {fixture.fixture_id}/{strategy}")
            temporal_cells.append({
                "fixture_id": fixture.fixture_id,
                "strategy": strategy,
                "expected": "SOURCE_SHA256",
                "observed": outcome["winner"],
                "diagnostics": outcome["diagnostics"],
                "raw_exception": outcome["raw_exception"],
            })

    inherited_cells = []
    for case, expected, required_codes in (
        (
            "missing_disposition_plus_invalid_class",
            "PATH_DISPOSITION_MISSING",
            {"PATH_DISPOSITION_MISSING", "OWNERLESS_FIELD", "OUTPUT_MISMATCH"},
        ),
        (
            "missing_pointer_plus_edge_id_drift",
            "OVERRIDE_POINTER_MISSING",
            {"OVERRIDE_POINTER_MISSING", "UNRESOLVED_CONTRADICTION", "OUTPUT_MISMATCH"},
        ),
    ):
        mutated = _mutate_actual_input(input_object, case)
        view = ReadView({DEFAULT_INPUT: canonical_bytes(mutated)})
        for strategy in ("latest_entry", "ordered_entry"):
            outcome = _public_case(root, strategy, view=view)
            codes = {row["code"] for row in outcome["diagnostics"]}
            if outcome["winner"] != expected or not required_codes.issubset(codes):
                raise ResolutionFailure("OUTPUT_MISMATCH", f"inherited collision failed: {case}/{strategy}")
            inherited_cells.append({
                "fixture_id": case,
                "strategy": strategy,
                "expected": expected,
                "observed": outcome["winner"],
                "diagnostics": outcome["diagnostics"],
            })

    priority_view = ReadView({DEFAULT_INPUT: canonical_bytes(_mutate_actual_input(input_object, "priority_table_drift"))})
    priority_cells = []
    for strategy in ("latest_entry", "ordered_entry"):
        outcome = _public_case(root, strategy, view=priority_view)
        if outcome["winner"] != "UNRESOLVED_CONTRADICTION":
            raise ResolutionFailure("OUTPUT_MISMATCH", f"priority-table drift failed: {strategy}")
        priority_cells.append({
            "strategy": strategy,
            "expected": "UNRESOLVED_CONTRADICTION",
            "observed": outcome["winner"],
            "diagnostics": outcome["diagnostics"],
        })

    cross_phase = []
    for fixture in _conformance_fixtures()["cross_phase_collisions"]:
        forward = _adjudicate_codes(fixture["faults"])
        reverse = _adjudicate_codes(list(reversed(fixture["faults"])))
        if forward["winner"] != fixture["expected"] or reverse["winner"] != fixture["expected"]:
            raise ResolutionFailure("OUTPUT_MISMATCH", f"cross-phase collision failed: {fixture}")
        cross_phase.append({
            **fixture,
            "observed_forward": forward["winner"],
            "observed_reverse": reverse["winner"],
            "forward_diagnostics": forward["diagnostics"],
            "reverse_diagnostics": reverse["diagnostics"],
        })

    pair_rows = []
    for fixture in _conformance_fixtures()["ordered_error_pairs"]:
        forward = _adjudicate_codes([fixture["first"], fixture["second"]])
        reverse = _adjudicate_codes([fixture["second"], fixture["first"]])
        if forward["winner"] != fixture["expected"] or reverse["winner"] != fixture["expected"]:
            raise ResolutionFailure("OUTPUT_MISMATCH", f"ordered error pair failed: {fixture}")
        pair_rows.append({
            **fixture,
            "observed_forward": forward["winner"],
            "observed_reverse": reverse["winner"],
        })

    nested = ResolutionFailure(
        "OUTPUT_MISMATCH",
        "nested wrapper",
        [
            {"code": "SOURCE_SHA256", "detail": "nested higher-priority diagnostic", "phase": "nested:lineage"},
            {"code": "OUTPUT_MISMATCH", "detail": "nested lower-priority diagnostic", "phase": "nested:output"},
        ],
    )
    nested_outcome = _public_case(
        root,
        "latest_entry",
        fixture=FaultFixture("nested_diagnostic_merge", nested_failure=nested),
    )
    nested_codes = {row["code"] for row in nested_outcome["diagnostics"]}
    if nested_outcome["winner"] != "SOURCE_SHA256" or nested_codes != {"SOURCE_SHA256", "OUTPUT_MISMATCH"}:
        raise ResolutionFailure("OUTPUT_MISMATCH", "nested diagnostic merge failed")

    return {
        "status": "PASS",
        "authority": "zero",
        "public_custody_cells": custody_cells,
        "public_custody_cell_count": len(custody_cells),
        "temporal_collision_cells": temporal_cells,
        "temporal_collision_cell_count": len(temporal_cells),
        "inherited_v8_actual_input_cells": inherited_cells,
        "inherited_v8_actual_input_cell_count": len(inherited_cells),
        "cross_phase_collisions": cross_phase,
        "priority_table_drift_cells": priority_cells,
        "ordered_error_pairs": pair_rows,
        "ordered_error_pairs_checked": len(pair_rows),
        "ordered_error_pair_insertion_orders": 2,
        "nested_diagnostic_merge": nested_outcome,
        "quarantined_post_snapshot_mutations": positive["quarantined_post_snapshot_mutations"],
        "strategies_byte_identical": True,
        "source_field_count": 1363,
        "source_fields_sha256": V9_SOURCE_FIELDS_SHA256,
        "origin_row_count": 1363,
        "origin_rows_sha256": V9_ORIGIN_ROWS_SHA256,
        "resolution_input": {"size_bytes": len(input_raw), "sha256": sha256(input_raw)},
        "resolved_contract": {"size_bytes": len(resolved_raw), "sha256": sha256(resolved_raw)},
        "origin_trace": {"size_bytes": len(origin_raw), "sha256": sha256(origin_raw)},
        "experiment_runs_consumed": 0,
        "raw_exception_count": 0,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--strategy", choices=("latest_entry", "ordered_entry", "both"), default="both")
    parser.add_argument("--emit", choices=("summary", "resolution-input", "resolved-contract", "origin-trace"), default="summary")
    parser.add_argument("--materialize", action="store_true", help="write only the three declared generated v10 JSON artifacts")
    parser.add_argument("--self-test", action="store_true", help="run the frozen deterministic static matrix")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    if args.self_test:
        sys.stdout.buffer.write(canonical_bytes(run_self_test(Path(args.root))))
        return 0
    strategies = ["latest_entry", "ordered_entry"] if args.strategy == "both" else [args.strategy]
    input_raw, resolved_raw, origin_raw, summary = resolve(
        args.root,
        strategies,
        materialize_input=args.materialize,
        compare_materialized=not args.materialize,
    )
    if args.materialize:
        for relative, raw in (
            (DEFAULT_INPUT, input_raw),
            (DEFAULT_RESOLVED, resolved_raw),
            (DEFAULT_ORIGIN, origin_raw),
        ):
            path = repository_path(Path(args.root).resolve(), relative)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
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
