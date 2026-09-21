#!/usr/bin/env python3
"""Deterministic public-entry resolver for EXP-INSTR-36c8cf amendment v12.

This is a static control-plane program.  It never executes an experiment, the
research harness, Phase B, JINV work, elliptic-curve arithmetic, rho, or BSGS.
The exact v11 payload is data, not executable code.  The pinned dispatcher is
loaded from exact bytes into a side-effect-free definition namespace: no
module import, sys.modules mutation, bytecode, or repository output occurs.
"""

from __future__ import annotations

import argparse
import ast
import builtins
import copy
import hashlib
import importlib
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from types import MappingProxyType, SimpleNamespace
from typing import Any, Callable, Protocol, Sequence

import yaml


sys.dont_write_bytecode = True


EXPERIMENT_ID = "EXP-INSTR-36c8cf"
VERSION = 12
BASE = "experiments/EXP-INSTR-36c8cf/amendments/v12-452868"
DEFAULT_INPUT = f"{BASE}/resolution-input.json"
DEFAULT_RESOLVED = f"{BASE}/resolved-contract.json"
DEFAULT_ORIGIN = f"{BASE}/origin-trace.json"

V11_BASE = "experiments/EXP-INSTR-36c8cf/amendments/v11-2174b9"
V11_AMENDMENT = "experiments/EXP-INSTR-36c8cf/amendments/v11-2174b9.yaml"
V11_RESOLVER = f"{V11_BASE}/resolver.py"
V11_INPUT = f"{V11_BASE}/resolution-input.json"
V11_RESOLVED = f"{V11_BASE}/resolved-contract.json"
V11_ORIGIN = f"{V11_BASE}/origin-trace.json"

V11_SOURCE_FIELDS_SHA256 = "a15dd1116fff1593440c82e91083e6744eb84c5d05615c554c23902480e9717b"
V11_ORIGIN_ROWS_SHA256 = "d90a95aafbdc06a90a18587003595f1f19f12ae83bfaf8a9ba3f259ed922e413"

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

V11_PACKAGE = (
    ("amendment_v11", V11_AMENDMENT, 10816, "f7a654ca5b9a5cb9f846aa362a315423f4d9656e994c28daad9f7335ee525655"),
    ("v11_resolver", V11_RESOLVER, 91088, "7030158e6bd1a4d725d7acd47e75ebde1e28fb110797a24127f40404a9eb5aee"),
    ("v11_resolution_input", V11_INPUT, 569806, "d8782804e6e0dfacbaf529b3864d5a22df374e1649be4c4eccd069fa4ac21f8f"),
    ("v11_resolved_contract", V11_RESOLVED, 706482, "7fe66f6de21177eaed291535ab5d6f877a9af52d9ecc4b031e7bb642e3fe2523"),
    ("v11_origin_trace", V11_ORIGIN, 1202864, "d628827fcdd6b2ab30618669675011f58a17bab50e68c84c7eafe6341f4a5df5"),
)

QUEUE_PATH = "coordination/goals/GOAL-ENDO-001/batches/BATCH-d7e255/instr-v11-2174b9-nested-import-public-control-repair/dispatch_queue.json"
RECEIPT_PATH = "coordination/goals/GOAL-ENDO-001/batches/BATCH-d7e255/instr-v11-2174b9-nested-import-public-control-repair/archives/TASK-20260813-83d804/snapshot-receipt.json"
REVIEW_PATH = "coordination/goals/GOAL-ENDO-001/batches/BATCH-d7e255/instr-v11-2174b9-nested-import-public-control-repair/reviews/TASK-20260813-50afc3/red-team-report.yaml"
DETERMINATION_PATH = "coordination/goals/GOAL-ENDO-001/batches/BATCH-d7e255/instr-v11-2174b9-nested-import-public-control-repair/decisions/TASK-20260813-b11b6a/approval-determination.yaml"
EVIDENCE_PATH = "ledger/evidence/EV-INSTR-039cc2.yaml"
DECISION_PATH = "ledger/decisions/DEC-20260813-9f5120.yaml"
LEDGER_RECEIPT_PATH = "coordination/goals/GOAL-ENDO-001/batches/BATCH-d7e255/instr-v11-2174b9-nested-import-public-control-repair/archives/TASK-20260813-db44cb/ledger-receipt.json"
DISPATCHER_PATH = "tools/research_dispatch.py"

INFERENCE_BINDINGS = (
    ("model_policies", "orchestration/model-policies.yaml", 12067, "4b6aa0cf9b472471d5574b03b004446fbd194153f8aede4d1a92a37bcf045d65"),
    ("providers", "orchestration/providers.yaml", 10537, "67e91048e1d00a7e25d88b9ece814521d5b6d12afae2a1483eb0c38992f6f086"),
    ("model_bindings", "orchestration/model-bindings.yaml", 17954, "144eb0e73c4b2362f6ba7d742a4458f7db326e3210bb897c2baac25804f45187"),
)
NESTED_IMPORT_AST_SHA256 = "91e2936dfa8e8e26e6be503ed56f7e6c459d54ce6a03163da728c13e7889009f"

QUEUE_SIZE = 56731
QUEUE_RAW_SHA256 = "602e5324d6a294f6078d73f50fcfcdb3cb921e20a9334bfcfc5710a0ed94f42a"
PLAN_SOURCE_QUEUE_SHA256 = "8cb1f0ad527e0d8c512ac1cf3c9c13e60c9073045e19653b8824640adcf8c55e"
PLAN_SHA256 = "8c31d5967d4410de43f5e187035951f6866a5402fce9426077cfaedaa7afd3a6"
DISPATCHER_PLAN_SHA256 = "e3000c898a01d23dc4314146379617eef0ac9eb1152a95ec101d44e9af69915a"
PLAN_PRETTY_SIZE = 2025
PLAN_PRETTY_SHA256 = "7e2146abd61fecb2c53f236b9901fd905f182cdb59078f479c1868632dd3b808"

RECEIPT_SIZE = 5214
RECEIPT_SHA256 = "5bbc0e3caf827e4846b7aa79c815680038f21bf610377d677968628c42dcc508"
REVIEW_SIZE = 35880
REVIEW_SHA256 = "f74d3089d8ef56877762afca076fa5015fff0e1249cfc466c0ec08520bd1a935"
DETERMINATION_SIZE = 32078
DETERMINATION_SHA256 = "c7a8cff593a99a96dc3588b8bd3ca9e0a65c979c394f2e354e3ca33b84fe84ec"
EVIDENCE_SIZE = 15779
EVIDENCE_SHA256 = "986dd6888f36f6472f71ee4417e91fc7c140088e657191af2c0c02dce8666f7e"
DECISION_SIZE = 21105
DECISION_SHA256 = "8a1953857e1fc70b2906c909ada87ecc2967fd789b7a1dd532b5facdeffa02ac"
LEDGER_RECEIPT_SIZE = 7528
LEDGER_RECEIPT_SHA256 = "61a401351112cc68ebb8eea3c70d9655469c12494437910bf3b606102df356cd"
DISPATCHER_SIZE = 56104
DISPATCHER_SHA256 = "04878bf31e1da2b24f43adfa214b744a125039651233d7357889731b0b0f397a"

SNAPSHOT_TASK = "TASK-20260813-83d804"
SNAPSHOT_COMMIT = "679ada540b31a2b3fbc06c2245e0c6c34225239d"
SNAPSHOT_PARENT = "f9c95c0995a5624c18b404d8720894af8e14b0a4"
LEDGER_COMMIT = "d5d7027358c6d7740cc9d9688a4ed5255a4d0a87"
LEDGER_PARENT = "d87581eb8f008bdfef3fbd67b24149fe842fc6e0"
TERMINAL_HEAD = "8c477b2e856e50c1a0edf616f8fc66c310f2197a"

SNAPSHOT_PATH_HASHES = {
    V11_AMENDMENT: V11_PACKAGE[0][3],
    V11_RESOLVER: V11_PACKAGE[1][3],
    V11_INPUT: V11_PACKAGE[2][3],
    V11_RESOLVED: V11_PACKAGE[3][3],
    V11_ORIGIN: V11_PACKAGE[4][3],
    RECEIPT_PATH: RECEIPT_SHA256,
}
SNAPSHOT_PATHS = tuple(SNAPSHOT_PATH_HASHES)
REQUIRED_MESSAGE_IDS = (
    "GOAL-ENDO-001",
    "BATCH-d7e255",
    EXPERIMENT_ID,
    "TASK-20260813-2174b9",
    SNAPSHOT_TASK,
)
EXPECTED_TOPOLOGY = {
    "TASK-20260813-2174b9": ("executor", ()),
    SNAPSHOT_TASK: ("coordinator", ("TASK-20260813-2174b9",)),
    "TASK-20260813-50afc3": ("red-team", ("TASK-20260813-2174b9", SNAPSHOT_TASK)),
    "TASK-20260813-b11b6a": ("coordinator", ("TASK-20260813-50afc3",)),
    "TASK-20260813-db44cb": ("coordinator", ("TASK-20260813-50afc3", "TASK-20260813-b11b6a")),
}

CONTROL_BINDINGS = (
    ("v11_snapshot_receipt", RECEIPT_PATH, RECEIPT_SIZE, RECEIPT_SHA256),
    ("v11_red_team", REVIEW_PATH, REVIEW_SIZE, REVIEW_SHA256),
    ("v11_determination", DETERMINATION_PATH, DETERMINATION_SIZE, DETERMINATION_SHA256),
    ("v11_evidence", EVIDENCE_PATH, EVIDENCE_SIZE, EVIDENCE_SHA256),
    ("v11_decision", DECISION_PATH, DECISION_SIZE, DECISION_SHA256),
    ("v11_ledger_receipt", LEDGER_RECEIPT_PATH, LEDGER_RECEIPT_SIZE, LEDGER_RECEIPT_SHA256),
)

EXPECTED_ARTIFACTS: dict[str, dict[str, Any]] = {
    DEFAULT_INPUT: {
        "size_bytes": 882541,
        "sha256": "cb5e062cf795c024f8daf9e718a1c3418298feea5362269bfde2c4c08a323f21",
    },
    DEFAULT_RESOLVED: {
        "size_bytes": 1019217,
        "sha256": "61f815f234e43855d5971ecece043d50f6e1915da3cf18c9ddccddc3c147a4fd",
    },
    DEFAULT_ORIGIN: {
        "size_bytes": 4954552,
        "sha256": "6e47ed2a30b7f79bc0d84ace67f2fe7e6550d79d26f89374593a51dbba4130e5",
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
    def __init__(self, code: str, detail: str, diagnostics: Any = None):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail
        self.diagnostics = [] if diagnostics is None else diagnostics
        self.final_adjudicator_calls = 0


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


def canonical_digest(value: Any) -> str:
    """Dispatcher-compatible compact JSON SHA-256 without a terminal LF."""

    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8"))


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


@dataclass(frozen=True)
class _DiagnosticSnapshot:
    """Detached exact-scalar form of one caller-supplied nested diagnostic."""

    code: str
    detail: str
    phase: str
    priority: int


@dataclass(frozen=True)
class _ResolutionFailureSnapshot:
    """Detached immutable form consumed by ``DiagnosticCollector.merge_nested``."""

    code: str
    detail: str
    diagnostics: tuple[_DiagnosticSnapshot, ...]
    final_adjudicator_calls: int


class DiagnosticCollector:
    """The one compiled-order collector used by each public resolve call."""

    def __init__(self, compiled_priority: tuple[dict[str, Any], ...]):
        self._compiled_priority = tuple(copy.deepcopy(compiled_priority))
        self._items: list[Diagnostic] = []
        self._adjudicated = False

    def add(self, code: str, detail: str, phase: str) -> None:
        if type(code) is not str or code not in PRIORITY_BY_CODE:
            detail = "unknown or non-exact diagnostic code"
            code = "UNRESOLVED_CONTRADICTION"
            phase = "diagnostic:normalization"
        if type(detail) is not str or not detail:
            detail = "diagnostic detail is absent or non-exact"
        if type(phase) is not str or not phase:
            phase = "diagnostic:normalization"
        self._items.append(Diagnostic(code, detail, phase))

    def merge_nested(self, phase: str, exc: _ResolutionFailureSnapshot) -> None:
        """Merge only a previously detached immutable failure snapshot."""

        if type(exc) is not _ResolutionFailureSnapshot:
            raise TypeError("merge_nested requires an exact detached failure snapshot")
        if not exc.diagnostics:
            self.add(exc.code, exc.detail, phase)
            return
        for row in exc.diagnostics:
            self.add(
                row.code,
                row.detail,
                f"{phase}>{row.phase}",
            )

    def capture_nested(
        self,
        phase: str,
        default_code: str,
        exc: _ResolutionFailureSnapshot,
    ) -> None:
        """Local containment boundary for a normalized nested merge."""

        try:
            self.merge_nested(phase, exc)
        except Exception as nested_error:
            self.add(
                default_code,
                f"nested ResolutionFailure merge failed: {type(nested_error).__name__}",
                f"{phase}:nested-merge",
            )

    def capture(self, phase: str, default_code: str, action: Callable[[], Any]) -> Any:
        try:
            return action()
        except ResolutionFailure as exc:
            # Exceptions raised while an earlier ``except`` suite is running do
            # not reach that try statement's sibling ``except Exception``.
            # Detachment and merge therefore have their own local boundary.
            try:
                snapshot = _detach_resolution_failure(exc)
            except Exception as normalization_error:
                self.add(
                    default_code,
                    f"nested ResolutionFailure normalization failed: {type(normalization_error).__name__}",
                    f"{phase}:nested-normalization",
                )
            else:
                self.capture_nested(phase, default_code, snapshot)
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
            failure = ResolutionFailure(winner["code"], winner["detail"], diagnostics)
            failure.final_adjudicator_calls = 1
            raise failure
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


@dataclass(frozen=True)
class _FaultFixtureSnapshot:
    """Detached exact-scalar form used after the public fixture boundary."""

    fixture_id: str
    plan_mutation: str | None
    dispatcher_output_mismatch: bool
    input_generation_output_mismatch: bool
    nested_failure: _ResolutionFailureSnapshot | None


class _PublicControlNormalizationError(ValueError):
    """Internal constant-message marker; caller-owned values are never formatted."""


PLAN_MUTATIONS = frozenset({"fabricated_authority", "plan_drift", "gate_drift"})


def _deep_freeze(value: Any) -> Any:
    if isinstance(value, dict):
        return MappingProxyType({str(key): _deep_freeze(child) for key, child in value.items()})
    if isinstance(value, list):
        return tuple(_deep_freeze(child) for child in value)
    return value


@dataclass(frozen=True)
class InferencePolicyView:
    """Minimal immutable projection consumed by dispatcher.validate_inference."""

    policy_table: Any
    effort_order: tuple[str, ...]

    def canonical_policy(self, name: str) -> str:
        if name in self.policy_table:
            return name
        for policy_id, policy in self.policy_table.items():
            if name in (policy.get("aliases") or ()):
                return policy_id
        known = sorted(self.policy_table) + sorted(
            alias for policy in self.policy_table.values() for alias in (policy.get("aliases") or ())
        )
        raise ValueError(
            f"unknown inference policy {name!r}; known policies and aliases: {', '.join(known)}"
        )


def _load_inference_policy_view(
    root: Path,
    view: ReadView,
    collector: DiagnosticCollector,
) -> InferencePolicyView | None:
    """Exact-bind all three configuration files before deriving one local view."""

    raw_documents: dict[str, bytes] = {}
    all_bound = True
    for source_id, relative, size, digest in INFERENCE_BINDINGS:
        raw = collector.capture(
            f"inference-config:{source_id}:read",
            "MISSING_SOURCE",
            lambda relative=relative: view.read(root, relative),
        )
        if not isinstance(raw, bytes):
            all_bound = False
            continue
        if len(raw) != size or sha256(raw) != digest:
            collector.add(
                "SOURCE_SHA256",
                f"exact inference configuration binding drift: {relative}",
                f"inference-config:{source_id}:binding",
            )
            all_bound = False
            continue
        raw_documents[source_id] = raw
    if not all_bound or len(raw_documents) != len(INFERENCE_BINDINGS):
        return None

    documents: dict[str, Any] = {}
    for source_id, relative, _, _ in INFERENCE_BINDINGS:
        parsed = collector.capture(
            f"inference-config:{source_id}:parse",
            "TYPE_COERCION",
            lambda source_id=source_id: yaml.safe_load(raw_documents[source_id].decode("utf-8")),
        )
        if not isinstance(parsed, dict):
            collector.add("TYPE_COERCION", f"{relative} is not a mapping", f"inference-config:{source_id}")
            return None
        documents[source_id] = parsed

    policies = documents["model_policies"].get("policies")
    effort_order = documents["model_policies"].get("adapter", {}).get("reasoning_effort_order")
    if not isinstance(policies, dict) or not isinstance(effort_order, list):
        collector.add("TYPE_COERCION", "inference policy projection fields are malformed", "inference-config:projection")
        return None
    if not all(isinstance(item, str) for item in effort_order):
        collector.add("TYPE_COERCION", "inference effort lattice contains a non-string", "inference-config:projection")
        return None

    # Providers and bindings are deliberately parsed and structurally checked
    # even though validate_inference consumes only policy semantics.  This keeps
    # the projection conditional on the exact three-file configuration preimage.
    if not isinstance(documents["providers"].get("backends"), dict):
        collector.add("TYPE_COERCION", "provider backend table is malformed", "inference-config:projection")
        return None
    if not isinstance(documents["model_bindings"].get("bindings"), dict):
        collector.add("TYPE_COERCION", "model binding table is malformed", "inference-config:projection")
        return None
    return InferencePolicyView(_deep_freeze(policies), tuple(effort_order))


def _exact_attribute_snapshot(value: Any, names: tuple[str, ...]) -> tuple[Any, ...]:
    """Read each field exactly once without a subclass ``__getattribute__`` hook."""

    return tuple(object.__getattribute__(value, name) for name in names)


def _detach_resolution_failure(value: Any) -> _ResolutionFailureSnapshot:
    """Exact-type check, one-read capture, and deep immutable normalization."""

    if type(value) is not ResolutionFailure:
        raise _PublicControlNormalizationError("ResolutionFailure exact type required")
    code, detail, diagnostics, final_calls = _exact_attribute_snapshot(
        value,
        ("code", "detail", "diagnostics", "final_adjudicator_calls"),
    )
    if type(code) is not str or code not in PRIORITY_BY_CODE:
        raise _PublicControlNormalizationError("ResolutionFailure code is malformed")
    if type(detail) is not str or not detail:
        raise _PublicControlNormalizationError("ResolutionFailure detail is malformed")
    if type(final_calls) is not int or final_calls < 0:
        raise _PublicControlNormalizationError("ResolutionFailure counter is malformed")
    if type(diagnostics) is not list and type(diagnostics) is not tuple:
        raise _PublicControlNormalizationError("diagnostic container exact type required")

    # Exactly one traversal of the admitted exact built-in container.  The
    # generator forces a new tuple even when the caller supplied a tuple.
    row_snapshot = tuple(row for row in diagnostics)
    detached_rows: list[_DiagnosticSnapshot] = []
    seen: set[tuple[str, str, str]] = set()
    for row in row_snapshot:
        if type(row) is not dict:
            raise _PublicControlNormalizationError("diagnostic row exact dict required")
        # One traversal detaches both keys and values; the caller row is never
        # indexed or read again after this point.
        item_snapshot = tuple((key, child) for key, child in row.items())
        if any(type(key) is not str for key, _ in item_snapshot):
            raise _PublicControlNormalizationError("diagnostic keys must be exact strings")
        keys = tuple(key for key, _ in item_snapshot)
        key_set = frozenset(keys)
        if key_set not in (
            frozenset({"code", "detail", "phase"}),
            frozenset({"code", "detail", "phase", "priority"}),
        ) or len(keys) != len(key_set):
            raise _PublicControlNormalizationError("diagnostic key set is malformed")
        detached = {key: child for key, child in item_snapshot}
        row_code = detached["code"]
        row_detail = detached["detail"]
        row_phase = detached["phase"]
        if type(row_code) is not str or row_code not in PRIORITY_BY_CODE:
            raise _PublicControlNormalizationError("diagnostic code is malformed")
        if type(row_detail) is not str or not row_detail:
            raise _PublicControlNormalizationError("diagnostic detail is malformed")
        if type(row_phase) is not str or not row_phase:
            raise _PublicControlNormalizationError("diagnostic phase is malformed")
        priority = detached.get("priority", PRIORITY_BY_CODE[row_code])
        if type(priority) is not int or priority != PRIORITY_BY_CODE[row_code]:
            raise _PublicControlNormalizationError("diagnostic priority is malformed")
        identity = (row_code, row_detail, row_phase)
        if identity in seen:
            raise _PublicControlNormalizationError("duplicate nested diagnostic")
        seen.add(identity)
        detached_rows.append(_DiagnosticSnapshot(row_code, row_detail, row_phase, priority))
    return _ResolutionFailureSnapshot(code, detail, tuple(detached_rows), final_calls)


def _detach_fault_fixture(value: Any) -> _FaultFixtureSnapshot:
    """Deep-detach an exact fixture without retaining or rereading caller state."""

    if type(value) is not FaultFixture:
        raise _PublicControlNormalizationError("FaultFixture exact type required")
    fixture_id, plan_mutation, dispatcher_mismatch, input_mismatch, nested_failure = (
        _exact_attribute_snapshot(
            value,
            (
                "fixture_id",
                "plan_mutation",
                "dispatcher_output_mismatch",
                "input_generation_output_mismatch",
                "nested_failure",
            ),
        )
    )
    if type(fixture_id) is not str or not fixture_id:
        raise _PublicControlNormalizationError("fixture_id is malformed")
    if plan_mutation is not None and (
        type(plan_mutation) is not str or plan_mutation not in PLAN_MUTATIONS
    ):
        raise _PublicControlNormalizationError("plan_mutation is malformed")
    if type(dispatcher_mismatch) is not bool or type(input_mismatch) is not bool:
        raise _PublicControlNormalizationError("fixture booleans must be exact bool")
    if nested_failure is None:
        detached_failure = None
    else:
        detached_failure = _detach_resolution_failure(nested_failure)
    return _FaultFixtureSnapshot(
        fixture_id,
        plan_mutation,
        dispatcher_mismatch,
        input_mismatch,
        detached_failure,
    )


def _detach_strategies(value: Any) -> tuple[str, ...]:
    """Admit an exact built-in, traverse once, and return one new tuple."""

    if type(value) is not list and type(value) is not tuple:
        raise _PublicControlNormalizationError("strategy container exact type required")
    snapshot = tuple(item for item in value)
    if not snapshot:
        raise _PublicControlNormalizationError("strategy container is empty")
    for item in snapshot:
        if type(item) is not str:
            raise _PublicControlNormalizationError("strategy member exact string required")
        if item not in {"latest_entry", "ordered_entry"}:
            raise _PublicControlNormalizationError("unsupported strategy member")
    return snapshot


def _normalize_public_controls(
    collector: DiagnosticCollector,
    strategies: Any,
    fault_fixture: Any,
) -> tuple[tuple[str, ...], _FaultFixtureSnapshot | None]:
    """Collector-first normalization for every public control argument."""

    try:
        normalized_strategies = _detach_strategies(strategies)
    except Exception:
        collector.add(
            "ECOMP_LATEST_ONLY",
            "strategies must be a nonempty list or tuple of exact latest_entry/ordered_entry strings",
            "public-entry:controls:strategies",
        )
        # Continue independent source, custody, and output checks against a
        # deterministic safe context without treating malformed input as valid.
        normalized_strategies = ("latest_entry",)

    normalized_fixture: _FaultFixtureSnapshot | None = None
    fixture_valid = fault_fixture is None
    if fault_fixture is not None:
        try:
            normalized_fixture = _detach_fault_fixture(fault_fixture)
            fixture_valid = True
        except Exception:
            fixture_valid = False
    if not fixture_valid:
        collector.add(
            "TYPE_COERCION",
            "fault_fixture must be None or an exact, fully validated FaultFixture",
            "public-entry:controls:fault-fixture",
        )
    return normalized_strategies, normalized_fixture


def _diagnostic_row(code: str, detail: str, phase: str) -> dict[str, Any]:
    return {
        "code": code,
        "detail": detail,
        "phase": phase,
        "priority": PRIORITY_BY_CODE[code],
    }


_EXPECTED_STRATEGY_DIAGNOSTIC = _diagnostic_row(
    "ECOMP_LATEST_ONLY",
    "strategies must be a nonempty list or tuple of exact latest_entry/ordered_entry strings",
    "public-entry:controls:strategies",
)
_EXPECTED_FIXTURE_DIAGNOSTIC = _diagnostic_row(
    "TYPE_COERCION",
    "fault_fixture must be None or an exact, fully validated FaultFixture",
    "public-entry:controls:fault-fixture",
)


def _forge_failure(*, omit: str | None = None, **changes: Any) -> ResolutionFailure:
    failure = ResolutionFailure.__new__(ResolutionFailure)
    BaseException.__init__(failure)
    values = {
        "code": "OUTPUT_MISMATCH",
        "detail": "detached nested failure",
        "diagnostics": [],
        "final_adjudicator_calls": 0,
    }
    values.update(changes)
    for key, value in values.items():
        if key != omit:
            object.__setattr__(failure, key, value)
    return failure


def _forge_fixture(*, omit: str | None = None, **changes: Any) -> FaultFixture:
    fixture = object.__new__(FaultFixture)
    values = {
        "fixture_id": "public-boundary-fixture",
        "plan_mutation": None,
        "dispatcher_output_mismatch": False,
        "input_generation_output_mismatch": False,
        "nested_failure": None,
    }
    values.update(changes)
    for key, value in values.items():
        if key != omit:
            object.__setattr__(fixture, key, value)
    return fixture


def _probe_bump(value: Any) -> None:
    calls = object.__getattribute__(value, "_hook_calls")
    object.__setattr__(value, "_hook_calls", calls + 1)


class _HookedList(list):
    """One probe covers every hook forbidden before exact-type rejection."""

    def __getattribute__(self, name: str) -> Any:
        if name not in {"_hook_calls", "_profile", "_sentinel"}:
            _probe_bump(self)
        return list.__getattribute__(self, name)

    def __bool__(self) -> bool:
        _probe_bump(self)
        return True

    def __len__(self) -> int:
        _probe_bump(self)
        return list.__len__(self)

    def __iter__(self):
        iter_calls = object.__getattribute__(self, "_iter_calls") + 1
        object.__setattr__(self, "_iter_calls", iter_calls)
        _probe_bump(self)
        profile = object.__getattribute__(self, "_profile")
        if profile == "immediate_raising":
            raise RuntimeError("probe traversal must not execute")
        if profile == "sys_modules_mutation":
            sys.modules[object.__getattribute__(self, "_sentinel")] = object()
        if profile == "toctou_bogus":
            return iter(("latest_entry",) if iter_calls == 1 else ("bogus",))
        if profile == "second_runtime" and iter_calls > 1:
            raise RuntimeError("second probe traversal must not execute")
        return list.__iter__(self)

    def __getitem__(self, key: Any) -> Any:
        _probe_bump(self)
        return list.__getitem__(self, key)

    def __eq__(self, other: Any) -> bool:
        _probe_bump(self)
        return list.__eq__(self, other)

    def __str__(self) -> str:
        _probe_bump(self)
        return "hooked-list"

    def __repr__(self) -> str:
        _probe_bump(self)
        return "hooked-list"

    def __format__(self, spec: str) -> str:
        _probe_bump(self)
        return "hooked-list"


class _HookedTuple(tuple):
    def __getattribute__(self, name: str) -> Any:
        if name not in {"_hook_calls", "_profile", "_sentinel"}:
            _probe_bump(self)
        return tuple.__getattribute__(self, name)

    def __bool__(self) -> bool:
        _probe_bump(self)
        return True

    def __len__(self) -> int:
        _probe_bump(self)
        return tuple.__len__(self)

    def __iter__(self):
        iter_calls = object.__getattribute__(self, "_iter_calls") + 1
        object.__setattr__(self, "_iter_calls", iter_calls)
        _probe_bump(self)
        profile = object.__getattribute__(self, "_profile")
        if profile == "immediate_raising":
            raise RuntimeError("probe traversal must not execute")
        if profile == "sys_modules_mutation":
            sys.modules[object.__getattribute__(self, "_sentinel")] = object()
        if profile == "toctou_bogus":
            return iter(("latest_entry",) if iter_calls == 1 else ("bogus",))
        if profile == "second_runtime" and iter_calls > 1:
            raise RuntimeError("second probe traversal must not execute")
        return tuple.__iter__(self)

    def __getitem__(self, key: Any) -> Any:
        _probe_bump(self)
        return tuple.__getitem__(self, key)

    def __eq__(self, other: Any) -> bool:
        _probe_bump(self)
        return tuple.__eq__(self, other)

    def __str__(self) -> str:
        _probe_bump(self)
        return "hooked-tuple"

    def __repr__(self) -> str:
        _probe_bump(self)
        return "hooked-tuple"

    def __format__(self, spec: str) -> str:
        _probe_bump(self)
        return "hooked-tuple"


class _HookedFaultFixture(FaultFixture):
    def __getattribute__(self, name: str) -> Any:
        if name not in {"_hook_calls", "_profile", "_sentinel"}:
            _probe_bump(self)
        profile = object.__getattribute__(self, "_profile")
        if profile == "attribute_raising":
            raise RuntimeError("fixture attribute hook must not execute")
        if profile == "sys_modules_mutation":
            sys.modules[object.__getattribute__(self, "_sentinel")] = object()
        if profile == "attribute_mutation":
            object.__setattr__(self, "fixture_id", "mutated-by-rejected-hook")
        return object.__getattribute__(self, name)

    def __bool__(self) -> bool:
        _probe_bump(self)
        return True

    def __len__(self) -> int:
        _probe_bump(self)
        return 1

    def __iter__(self):
        _probe_bump(self)
        raise RuntimeError("fixture iteration hook must not execute")

    def __getitem__(self, key: Any) -> Any:
        _probe_bump(self)
        raise RuntimeError("fixture item hook must not execute")

    def __str__(self) -> str:
        _probe_bump(self)
        return "hooked-fixture"

    def __repr__(self) -> str:
        _probe_bump(self)
        return "hooked-fixture"

    def __format__(self, spec: str) -> str:
        _probe_bump(self)
        return "hooked-fixture"


class _HookedResolutionFailure(ResolutionFailure):
    def __getattribute__(self, name: str) -> Any:
        if name not in {"_hook_calls", "_profile", "_sentinel", "args"}:
            _probe_bump(self)
        profile = object.__getattribute__(self, "_profile")
        if profile == "attribute_raising":
            raise RuntimeError("failure attribute hook must not execute")
        if profile == "sys_modules_mutation":
            sys.modules[object.__getattribute__(self, "_sentinel")] = object()
        if profile == "attribute_mutation":
            object.__setattr__(self, "detail", "mutated-by-rejected-hook")
        return BaseException.__getattribute__(self, name)

    def __bool__(self) -> bool:
        _probe_bump(self)
        return True

    def __len__(self) -> int:
        _probe_bump(self)
        return 1

    def __iter__(self):
        _probe_bump(self)
        raise RuntimeError("failure iteration hook must not execute")

    def __getitem__(self, key: Any) -> Any:
        _probe_bump(self)
        raise RuntimeError("failure item hook must not execute")

    def __str__(self) -> str:
        _probe_bump(self)
        return "hooked-failure"

    def __repr__(self) -> str:
        _probe_bump(self)
        return "hooked-failure"

    def __format__(self, spec: str) -> str:
        _probe_bump(self)
        return "hooked-failure"


class _HookedDict(dict):
    def __getattribute__(self, name: str) -> Any:
        if name not in {"_hook_calls", "_profile", "_sentinel"}:
            _probe_bump(self)
        return dict.__getattribute__(self, name)

    def __bool__(self) -> bool:
        _probe_bump(self)
        return True

    def __len__(self) -> int:
        _probe_bump(self)
        return dict.__len__(self)

    def __iter__(self):
        iter_calls = object.__getattribute__(self, "_iter_calls") + 1
        object.__setattr__(self, "_iter_calls", iter_calls)
        _probe_bump(self)
        profile = object.__getattribute__(self, "_profile")
        if profile == "immediate_raising":
            raise RuntimeError("row traversal hook must not execute")
        if profile == "sys_modules_mutation":
            sys.modules[object.__getattribute__(self, "_sentinel")] = object()
        if profile == "attribute_mutation":
            dict.__setitem__(self, "detail", "mutated-by-rejected-hook")
        return dict.__iter__(self)

    def items(self):
        item_calls = object.__getattribute__(self, "_items_calls") + 1
        object.__setattr__(self, "_items_calls", item_calls)
        _probe_bump(self)
        profile = object.__getattribute__(self, "_profile")
        if profile == "immediate_raising":
            raise RuntimeError("row items hook must not execute")
        if profile == "second_runtime" and item_calls > 1:
            raise RuntimeError("second row traversal must not execute")
        if profile == "toctou_bogus":
            if item_calls == 1:
                return dict.items(self)
            return {"code": "UNKNOWN", "detail": "bogus", "phase": "row"}.items()
        if profile == "sys_modules_mutation":
            sys.modules[object.__getattribute__(self, "_sentinel")] = object()
        if profile == "attribute_mutation":
            dict.__setitem__(self, "detail", "mutated-by-rejected-hook")
        return dict.items(self)

    def __getitem__(self, key: Any) -> Any:
        _probe_bump(self)
        return dict.__getitem__(self, key)

    def __eq__(self, other: Any) -> bool:
        _probe_bump(self)
        return dict.__eq__(self, other)

    def __str__(self) -> str:
        _probe_bump(self)
        return "hooked-row"

    def __repr__(self) -> str:
        _probe_bump(self)
        return "hooked-row"

    def __format__(self, spec: str) -> str:
        _probe_bump(self)
        return "hooked-row"


class _HookedStr(str):
    def _touch(self) -> None:
        _probe_bump(self)
        profile = object.__getattribute__(self, "_profile")
        if profile == "immediate_raising":
            raise RuntimeError("scalar string hook must not execute")
        if profile == "sys_modules_mutation":
            sys.modules[object.__getattribute__(self, "_sentinel")] = object()

    def __getattribute__(self, name: str) -> Any:
        if name not in {"_hook_calls", "_profile", "_sentinel", "_touch"}:
            _HookedStr._touch(self)
        return str.__getattribute__(self, name)

    def __bool__(self) -> bool:
        self._touch()
        return True

    def __eq__(self, other: Any) -> bool:
        self._touch()
        return str.__eq__(self, other)

    def __hash__(self) -> int:
        self._touch()
        return str.__hash__(self)

    def __str__(self) -> str:
        self._touch()
        return "hooked-string"

    def __repr__(self) -> str:
        self._touch()
        return "hooked-string"

    def __format__(self, spec: str) -> str:
        self._touch()
        return "hooked-string"


class _HookedInt(int):
    def _touch(self) -> None:
        _probe_bump(self)
        profile = object.__getattribute__(self, "_profile")
        if profile == "immediate_raising":
            raise RuntimeError("scalar integer hook must not execute")
        if profile == "sys_modules_mutation":
            sys.modules[object.__getattribute__(self, "_sentinel")] = object()

    def __getattribute__(self, name: str) -> Any:
        if name not in {"_hook_calls", "_profile", "_sentinel", "_touch"}:
            _HookedInt._touch(self)
        return int.__getattribute__(self, name)

    def __bool__(self) -> bool:
        self._touch()
        return True

    def __eq__(self, other: Any) -> bool:
        self._touch()
        return int.__eq__(self, other)

    def __hash__(self) -> int:
        self._touch()
        return int.__hash__(self)

    def __index__(self) -> int:
        self._touch()
        return int(self)

    def __str__(self) -> str:
        self._touch()
        return "hooked-integer"

    def __repr__(self) -> str:
        self._touch()
        return "hooked-integer"

    def __format__(self, spec: str) -> str:
        self._touch()
        return "hooked-integer"


def _initialize_probe(value: Any, profile: str, sentinel: str) -> Any:
    object.__setattr__(value, "_hook_calls", 0)
    object.__setattr__(value, "_iter_calls", 0)
    object.__setattr__(value, "_items_calls", 0)
    object.__setattr__(value, "_profile", profile)
    object.__setattr__(value, "_sentinel", sentinel)
    return value


def _string_probe(label: str, value: str = "latest_entry") -> _HookedStr:
    probe = _HookedStr(value)
    return _initialize_probe(probe, "sys_modules_mutation", f"__v12_string_probe_{label}__")


def _integer_probe(label: str, value: int = 7) -> _HookedInt:
    probe = _HookedInt(value)
    return _initialize_probe(probe, "sys_modules_mutation", f"__v12_integer_probe_{label}__")


def _sequence_probe(ancestry: str, profile: str, payload: Any = "latest_entry") -> Any:
    sentinel = f"__v12_strategy_probe_{ancestry}_{profile}__"
    if ancestry == "list":
        value = list.__new__(_HookedList)
        list.__init__(value, [payload])
    else:
        value = tuple.__new__(_HookedTuple, (payload,))
    return _initialize_probe(value, profile, sentinel)


def _fixture_probe(profile: str) -> _HookedFaultFixture:
    value = object.__new__(_HookedFaultFixture)
    for key, child in {
        "fixture_id": "hooked-fixture",
        "plan_mutation": None,
        "dispatcher_output_mismatch": False,
        "input_generation_output_mismatch": False,
        "nested_failure": None,
    }.items():
        object.__setattr__(value, key, child)
    return _initialize_probe(value, profile, f"__v12_fixture_probe_{profile}__")


def _failure_probe(profile: str) -> _HookedResolutionFailure:
    value = ResolutionFailure.__new__(_HookedResolutionFailure)
    BaseException.__init__(value)
    for key, child in {
        "code": "OUTPUT_MISMATCH",
        "detail": "hooked nested failure",
        "diagnostics": [],
        "final_adjudicator_calls": 0,
    }.items():
        object.__setattr__(value, key, child)
    return _initialize_probe(value, profile, f"__v12_failure_probe_{profile}__")


def _row_probe(profile: str) -> _HookedDict:
    value = dict.__new__(_HookedDict)
    dict.__init__(value, {"code": "SOURCE_SHA256", "detail": "row", "phase": "nested"})
    return _initialize_probe(value, profile, f"__v12_row_probe_{profile}__")


def _probe_metrics(probes: tuple[Any, ...]) -> tuple[int, int, list[str]]:
    hook_calls = sum(object.__getattribute__(probe, "_hook_calls") for probe in probes)
    traversal_calls = sum(
        object.__getattribute__(probe, "_iter_calls")
        + object.__getattribute__(probe, "_items_calls")
        for probe in probes
    )
    sentinels = [object.__getattribute__(probe, "_sentinel") for probe in probes]
    return hook_calls, traversal_calls, sentinels


def _boundary_case(
    case_id: str,
    strategies: Any,
    fixture: Any,
    expected_diagnostics: list[dict[str, Any]],
    *,
    probes: tuple[Any, ...] = (),
) -> dict[str, Any]:
    """Execute one public-normalization cell and materialize exact observations."""

    module_ids_before = {name: id(module) for name, module in sys.modules.items()}
    collector = DiagnosticCollector(COMPILED_PRIORITY)
    raw_exception = False
    normalized_strategies: tuple[str, ...] = ("latest_entry",)
    normalized_fixture: _FaultFixtureSnapshot | None = None
    try:
        controls = collector.capture(
            "public-entry:controls",
            "TYPE_COERCION",
            lambda: _normalize_public_controls(collector, strategies, fixture),
        )
        if type(controls) is tuple and len(controls) == 2:
            normalized_strategies, normalized_fixture = controls
        if normalized_fixture is not None and normalized_fixture.nested_failure is not None:
            collector.capture_nested(
                "nested-resolver",
                "UNRESOLVED_CONTRADICTION",
                normalized_fixture.nested_failure,
            )
        try:
            diagnostics = collector.final_adjudication()
            winner = "PASS"
            final_calls = 1
        except ResolutionFailure as exc:
            diagnostics = exc.diagnostics
            winner = exc.code
            final_calls = exc.final_adjudicator_calls
    except Exception:
        raw_exception = True
        diagnostics = []
        winner = "RAW_EXCEPTION"
        final_calls = 0

    module_ids_after = {name: id(module) for name, module in sys.modules.items()}
    module_delta = sorted(
        name
        for name in set(module_ids_before) | set(module_ids_after)
        if module_ids_before.get(name) != module_ids_after.get(name)
    )
    hook_calls, traversal_calls, sentinels = _probe_metrics(probes)
    for sentinel in sentinels:
        sys.modules.pop(sentinel, None)
    expected_sorted = sorted(
        expected_diagnostics,
        key=lambda row: (row["priority"], row["code"], row["phase"], row["detail"]),
    )
    expected_winner = expected_sorted[0]["code"] if expected_sorted else "PASS"
    expected = {
        "winner": expected_winner,
        "diagnostics": expected_sorted,
        "raw_exception": False,
        "final_adjudicator_calls": 1,
        "rejected_subclass_hook_calls": 0,
        "rejected_subclass_traversal_calls": 0,
        "sys_modules_delta": [],
    }
    observed = {
        "winner": winner,
        "diagnostics": diagnostics,
        "raw_exception": raw_exception,
        "final_adjudicator_calls": final_calls,
        "rejected_subclass_hook_calls": hook_calls,
        "rejected_subclass_traversal_calls": traversal_calls,
        "sys_modules_delta": module_delta,
        "normalized_strategies": list(normalized_strategies),
        "strategy_snapshot_detached": type(strategies) not in {list, tuple}
        or normalized_strategies is not strategies,
        "fixture_snapshot_detached": normalized_fixture is None or normalized_fixture is not fixture,
        "nested_failure_snapshot_detached": (
            normalized_fixture is None
            or normalized_fixture.nested_failure is None
            or type(normalized_fixture.nested_failure) is _ResolutionFailureSnapshot
        ),
    }
    comparable = {key: observed[key] for key in expected}
    if comparable != expected:
        raise ResolutionFailure("OUTPUT_MISMATCH", f"public boundary cell failed: {case_id}")
    return {"case_id": case_id, "expected": expected, "observed": observed, "matches_expected": True}


def _strategy_equivalence_cells() -> list[dict[str, Any]]:
    cells: list[dict[str, Any]] = []
    list_string_probe = _string_probe("strategy_list")
    tuple_string_probe = _string_probe("strategy_tuple")
    list_integer_probe = _integer_probe("strategy_list")
    tuple_integer_probe = _integer_probe("strategy_tuple")
    exact_cases = (
        ("exact_list_latest", ["latest_entry"], [], ()),
        ("exact_tuple_ordered", ("ordered_entry",), [], ()),
        ("exact_list_mixed_duplicate", ["latest_entry", "ordered_entry", "latest_entry"], [], ()),
        ("exact_tuple_mixed_duplicate", ("ordered_entry", "latest_entry", "ordered_entry"), [], ()),
        ("exact_list_empty", [], [_EXPECTED_STRATEGY_DIAGNOSTIC], ()),
        ("exact_tuple_empty", (), [_EXPECTED_STRATEGY_DIAGNOSTIC], ()),
        ("exact_list_integer", [7], [_EXPECTED_STRATEGY_DIAGNOSTIC], ()),
        ("exact_tuple_integer", (7,), [_EXPECTED_STRATEGY_DIAGNOSTIC], ()),
        ("exact_list_bogus", ["bogus"], [_EXPECTED_STRATEGY_DIAGNOSTIC], ()),
        ("exact_tuple_bogus", ("bogus",), [_EXPECTED_STRATEGY_DIAGNOSTIC], ()),
        ("exact_list_string_subclass", [list_string_probe], [_EXPECTED_STRATEGY_DIAGNOSTIC], (list_string_probe,)),
        ("exact_tuple_string_subclass", (tuple_string_probe,), [_EXPECTED_STRATEGY_DIAGNOSTIC], (tuple_string_probe,)),
        ("exact_list_integer_subclass", [list_integer_probe], [_EXPECTED_STRATEGY_DIAGNOSTIC], (list_integer_probe,)),
        ("exact_tuple_integer_subclass", (tuple_integer_probe,), [_EXPECTED_STRATEGY_DIAGNOSTIC], (tuple_integer_probe,)),
        ("noncontainer_none", None, [_EXPECTED_STRATEGY_DIAGNOSTIC], ()),
        ("noncontainer_string", "latest_entry", [_EXPECTED_STRATEGY_DIAGNOSTIC], ()),
        ("noncontainer_mapping", {"strategy": "latest_entry"}, [_EXPECTED_STRATEGY_DIAGNOSTIC], ()),
        ("noncontainer_integer", 1, [_EXPECTED_STRATEGY_DIAGNOSTIC], ()),
    )
    for case_id, value, expected, probes in exact_cases:
        cells.append(_boundary_case(case_id, value, None, list(expected), probes=probes))
    profiles = (
        "stable",
        "toctou_bogus",
        "second_runtime",
        "immediate_raising",
        "sys_modules_mutation",
        "bool_hook",
        "len_hook",
        "iter_hook",
        "getitem_hook",
        "equality_hook",
        "format_hooks",
    )
    for ancestry in ("list", "tuple"):
        for profile in profiles:
            probe = _sequence_probe(ancestry, profile)
            cells.append(_boundary_case(
                f"{ancestry}_subclass_{profile}",
                probe,
                None,
                [_EXPECTED_STRATEGY_DIAGNOSTIC],
                probes=(probe,),
            ))
    return cells


def _fixture_equivalence_specs() -> list[tuple[str, Any, list[dict[str, Any]], tuple[Any, ...]]]:
    valid_row = {"code": "SOURCE_SHA256", "detail": "nested source", "phase": "nested:source"}
    lower_row = {"code": "OUTPUT_MISMATCH", "detail": "nested output", "phase": "nested:output"}
    specs: list[tuple[str, Any, list[dict[str, Any]], tuple[Any, ...]]] = [
        ("fixture_none", None, [], ()),
        ("fixture_exact_default", FaultFixture("exact-default"), [], ()),
        ("fixture_exact_plan_mutation", FaultFixture("exact-plan", plan_mutation="plan_drift"), [], ()),
        ("fixture_exact_dispatcher_bool", FaultFixture("exact-dispatcher", dispatcher_output_mismatch=True), [], ()),
        ("fixture_exact_input_bool", FaultFixture("exact-input", input_generation_output_mismatch=True), [], ()),
        ("nonfixture_plain_object", object(), [_EXPECTED_FIXTURE_DIAGNOSTIC], ()),
        ("nonfixture_mapping", {"fixture_id": "mapping"}, [_EXPECTED_FIXTURE_DIAGNOSTIC], ()),
        ("nonfixture_string", "fixture", [_EXPECTED_FIXTURE_DIAGNOSTIC], ()),
        ("nonfixture_integer", 1, [_EXPECTED_FIXTURE_DIAGNOSTIC], ()),
        ("fixture_missing_field", _forge_fixture(omit="fixture_id"), [_EXPECTED_FIXTURE_DIAGNOSTIC], ()),
        ("fixture_empty_id", _forge_fixture(fixture_id=""), [_EXPECTED_FIXTURE_DIAGNOSTIC], ()),
        ("fixture_id_subclass", _forge_fixture(fixture_id=type("FixtureString", (str,), {})("id")), [_EXPECTED_FIXTURE_DIAGNOSTIC], ()),
        ("fixture_plan_bool", _forge_fixture(plan_mutation=True), [_EXPECTED_FIXTURE_DIAGNOSTIC], ()),
        ("fixture_plan_unknown", _forge_fixture(plan_mutation="unknown"), [_EXPECTED_FIXTURE_DIAGNOSTIC], ()),
        ("fixture_dispatcher_nonbool", _forge_fixture(dispatcher_output_mismatch=1), [_EXPECTED_FIXTURE_DIAGNOSTIC], ()),
        ("fixture_input_nonbool", _forge_fixture(input_generation_output_mismatch=0), [_EXPECTED_FIXTURE_DIAGNOSTIC], ()),
        ("fixture_nested_nonfailure", _forge_fixture(nested_failure=object()), [_EXPECTED_FIXTURE_DIAGNOSTIC], ()),
        ("failure_missing_code", _forge_fixture(nested_failure=_forge_failure(omit="code")), [_EXPECTED_FIXTURE_DIAGNOSTIC], ()),
        ("failure_missing_detail", _forge_fixture(nested_failure=_forge_failure(omit="detail")), [_EXPECTED_FIXTURE_DIAGNOSTIC], ()),
        ("failure_missing_diagnostics", _forge_fixture(nested_failure=_forge_failure(omit="diagnostics")), [_EXPECTED_FIXTURE_DIAGNOSTIC], ()),
        ("failure_missing_counter", _forge_fixture(nested_failure=_forge_failure(omit="final_adjudicator_calls")), [_EXPECTED_FIXTURE_DIAGNOSTIC], ()),
        ("failure_bad_code", _forge_fixture(nested_failure=_forge_failure(code="UNKNOWN")), [_EXPECTED_FIXTURE_DIAGNOSTIC], ()),
        ("failure_code_subclass", _forge_fixture(nested_failure=_forge_failure(code=type("CodeString", (str,), {})("OUTPUT_MISMATCH"))), [_EXPECTED_FIXTURE_DIAGNOSTIC], ()),
        ("failure_empty_detail", _forge_fixture(nested_failure=_forge_failure(detail="")), [_EXPECTED_FIXTURE_DIAGNOSTIC], ()),
        ("failure_detail_nonstring", _forge_fixture(nested_failure=_forge_failure(detail=1)), [_EXPECTED_FIXTURE_DIAGNOSTIC], ()),
        ("failure_bad_counter_bool", _forge_fixture(nested_failure=_forge_failure(final_adjudicator_calls=False)), [_EXPECTED_FIXTURE_DIAGNOSTIC], ()),
        ("failure_bad_counter_negative", _forge_fixture(nested_failure=_forge_failure(final_adjudicator_calls=-1)), [_EXPECTED_FIXTURE_DIAGNOSTIC], ()),
        ("diagnostics_noncontainer", _forge_fixture(nested_failure=_forge_failure(diagnostics={})), [_EXPECTED_FIXTURE_DIAGNOSTIC], ()),
        ("diagnostic_row_nonmapping", _forge_fixture(nested_failure=_forge_failure(diagnostics=["row"])), [_EXPECTED_FIXTURE_DIAGNOSTIC], ()),
        ("diagnostic_missing_key", _forge_fixture(nested_failure=_forge_failure(diagnostics=[{"code": "SOURCE_SHA256", "detail": "x"}])), [_EXPECTED_FIXTURE_DIAGNOSTIC], ()),
        ("diagnostic_extra_key", _forge_fixture(nested_failure=_forge_failure(diagnostics=[{**valid_row, "extra": 1}])), [_EXPECTED_FIXTURE_DIAGNOSTIC], ()),
        ("diagnostic_nonstring_key", _forge_fixture(nested_failure=_forge_failure(diagnostics=[{**valid_row, 1: "bad"}])), [_EXPECTED_FIXTURE_DIAGNOSTIC], ()),
        ("diagnostic_bad_code", _forge_fixture(nested_failure=_forge_failure(diagnostics=[{**valid_row, "code": "UNKNOWN"}])), [_EXPECTED_FIXTURE_DIAGNOSTIC], ()),
        ("diagnostic_code_subclass", _forge_fixture(nested_failure=_forge_failure(diagnostics=[{**valid_row, "code": type("RowCode", (str,), {})("SOURCE_SHA256")}])), [_EXPECTED_FIXTURE_DIAGNOSTIC], ()),
        ("diagnostic_empty_detail", _forge_fixture(nested_failure=_forge_failure(diagnostics=[{**valid_row, "detail": ""}])), [_EXPECTED_FIXTURE_DIAGNOSTIC], ()),
        ("diagnostic_detail_nonstring", _forge_fixture(nested_failure=_forge_failure(diagnostics=[{**valid_row, "detail": 1}])), [_EXPECTED_FIXTURE_DIAGNOSTIC], ()),
        ("diagnostic_empty_phase", _forge_fixture(nested_failure=_forge_failure(diagnostics=[{**valid_row, "phase": ""}])), [_EXPECTED_FIXTURE_DIAGNOSTIC], ()),
        ("diagnostic_phase_nonstring", _forge_fixture(nested_failure=_forge_failure(diagnostics=[{**valid_row, "phase": 1}])), [_EXPECTED_FIXTURE_DIAGNOSTIC], ()),
        ("diagnostic_priority_bool", _forge_fixture(nested_failure=_forge_failure(diagnostics=[{**valid_row, "priority": True}])), [_EXPECTED_FIXTURE_DIAGNOSTIC], ()),
        ("diagnostic_priority_subclass", _forge_fixture(nested_failure=_forge_failure(diagnostics=[{**valid_row, "priority": type("PriorityInt", (int,), {})(7)}])), [_EXPECTED_FIXTURE_DIAGNOSTIC], ()),
        ("diagnostic_priority_mismatch", _forge_fixture(nested_failure=_forge_failure(diagnostics=[{**valid_row, "priority": 25}])), [_EXPECTED_FIXTURE_DIAGNOSTIC], ()),
        ("diagnostic_duplicate", _forge_fixture(nested_failure=_forge_failure(diagnostics=[valid_row, dict(valid_row)])), [_EXPECTED_FIXTURE_DIAGNOSTIC], ()),
    ]
    fixture_id_probe = _string_probe("fixture_id", "fixture-id")
    plan_probe = _string_probe("fixture_plan", "plan_drift")
    failure_code_probe = _string_probe("failure_code", "OUTPUT_MISMATCH")
    failure_detail_probe = _string_probe("failure_detail", "nested detail")
    row_code_probe = _string_probe("row_code", "SOURCE_SHA256")
    row_detail_probe = _string_probe("row_detail", "nested source")
    row_phase_probe = _string_probe("row_phase", "nested:source")
    row_key_probe = _string_probe("row_key", "code")
    priority_probe = _integer_probe("row_priority", 7)
    hooked_key_row = {
        row_key_probe: "SOURCE_SHA256",
        "detail": "nested source",
        "phase": "nested:source",
    }
    # Dict construction hashes a key before the boundary; reset so the matrix
    # measures only resolver behavior.
    object.__setattr__(row_key_probe, "_hook_calls", 0)
    specs.extend((
        (
            "fixture_id_hooked_string_subclass",
            _forge_fixture(fixture_id=fixture_id_probe),
            [_EXPECTED_FIXTURE_DIAGNOSTIC],
            (fixture_id_probe,),
        ),
        (
            "fixture_plan_hooked_string_subclass",
            _forge_fixture(plan_mutation=plan_probe),
            [_EXPECTED_FIXTURE_DIAGNOSTIC],
            (plan_probe,),
        ),
        (
            "failure_code_hooked_string_subclass",
            _forge_fixture(nested_failure=_forge_failure(code=failure_code_probe)),
            [_EXPECTED_FIXTURE_DIAGNOSTIC],
            (failure_code_probe,),
        ),
        (
            "failure_detail_hooked_string_subclass",
            _forge_fixture(nested_failure=_forge_failure(detail=failure_detail_probe)),
            [_EXPECTED_FIXTURE_DIAGNOSTIC],
            (failure_detail_probe,),
        ),
        (
            "diagnostic_key_hooked_string_subclass",
            _forge_fixture(nested_failure=_forge_failure(diagnostics=[hooked_key_row])),
            [_EXPECTED_FIXTURE_DIAGNOSTIC],
            (row_key_probe,),
        ),
        (
            "diagnostic_code_hooked_string_subclass",
            _forge_fixture(nested_failure=_forge_failure(diagnostics=[{**valid_row, "code": row_code_probe}])),
            [_EXPECTED_FIXTURE_DIAGNOSTIC],
            (row_code_probe,),
        ),
        (
            "diagnostic_detail_hooked_string_subclass",
            _forge_fixture(nested_failure=_forge_failure(diagnostics=[{**valid_row, "detail": row_detail_probe}])),
            [_EXPECTED_FIXTURE_DIAGNOSTIC],
            (row_detail_probe,),
        ),
        (
            "diagnostic_phase_hooked_string_subclass",
            _forge_fixture(nested_failure=_forge_failure(diagnostics=[{**valid_row, "phase": row_phase_probe}])),
            [_EXPECTED_FIXTURE_DIAGNOSTIC],
            (row_phase_probe,),
        ),
        (
            "diagnostic_priority_hooked_integer_subclass",
            _forge_fixture(nested_failure=_forge_failure(diagnostics=[{**valid_row, "priority": priority_probe}])),
            [_EXPECTED_FIXTURE_DIAGNOSTIC],
            (priority_probe,),
        ),
    ))
    nested_empty = _forge_failure(code="OUTPUT_MISMATCH", detail="empty nested", diagnostics=[])
    specs.append((
        "failure_exact_empty_diagnostics",
        _forge_fixture(nested_failure=nested_empty),
        [_diagnostic_row("OUTPUT_MISMATCH", "empty nested", "nested-resolver")],
        (),
    ))
    for container_id, container in (("list", [valid_row, lower_row]), ("tuple", (valid_row, lower_row))):
        specs.append((
            f"failure_exact_{container_id}_diagnostics",
            _forge_fixture(nested_failure=_forge_failure(diagnostics=container)),
            [
                _diagnostic_row("SOURCE_SHA256", "nested source", "nested-resolver>nested:source"),
                _diagnostic_row("OUTPUT_MISMATCH", "nested output", "nested-resolver>nested:output"),
            ],
            (),
        ))
    specs.append((
        "failure_exact_priority_diagnostic",
        _forge_fixture(nested_failure=_forge_failure(diagnostics=[{**valid_row, "priority": 7}])),
        [_diagnostic_row("SOURCE_SHA256", "nested source", "nested-resolver>nested:source")],
        (),
    ))
    for profile in (
        "stable",
        "attribute_raising",
        "attribute_mutation",
        "sys_modules_mutation",
        "property_hook",
        "bool_hook",
        "len_hook",
        "iter_hook",
        "getitem_hook",
        "format_hooks",
    ):
        probe = _fixture_probe(profile)
        specs.append((f"fixture_subclass_{profile}", probe, [_EXPECTED_FIXTURE_DIAGNOSTIC], (probe,)))
    for profile in (
        "stable",
        "attribute_raising",
        "attribute_mutation",
        "sys_modules_mutation",
        "bool_hook",
        "len_hook",
        "iter_hook",
        "getitem_hook",
        "format_hooks",
    ):
        failure_probe = _failure_probe(profile)
        specs.append((
            f"failure_subclass_{profile}",
            _forge_fixture(nested_failure=failure_probe),
            [_EXPECTED_FIXTURE_DIAGNOSTIC],
            (failure_probe,),
        ))
    for ancestry in ("list", "tuple"):
        for profile in (
            "stable",
            "toctou_bogus",
            "second_runtime",
            "immediate_raising",
            "sys_modules_mutation",
            "bool_hook",
            "len_hook",
            "iter_hook",
            "getitem_hook",
            "equality_hook",
            "format_hooks",
        ):
            probe = _sequence_probe(ancestry, profile, valid_row)
            specs.append((
                f"diagnostic_{ancestry}_subclass_{profile}",
                _forge_fixture(nested_failure=_forge_failure(diagnostics=probe)),
                [_EXPECTED_FIXTURE_DIAGNOSTIC],
                (probe,),
            ))
    for profile in (
        "stable",
        "toctou_bogus",
        "second_runtime",
        "immediate_raising",
        "sys_modules_mutation",
        "attribute_mutation",
        "bool_hook",
        "len_hook",
        "iter_hook",
        "getitem_hook",
        "equality_hook",
        "format_hooks",
    ):
        probe = _row_probe(profile)
        specs.append((
            f"diagnostic_row_subclass_{profile}",
            _forge_fixture(nested_failure=_forge_failure(diagnostics=[probe])),
            [_EXPECTED_FIXTURE_DIAGNOSTIC],
            (probe,),
        ))
    return specs


def _fixture_equivalence_cells() -> list[dict[str, Any]]:
    cells: list[dict[str, Any]] = []
    for case_id, fixture, expected, probes in _fixture_equivalence_specs():
        for strategy in ("latest_entry", "ordered_entry"):
            cells.append(_boundary_case(
                f"{case_id}__{strategy}",
                [strategy],
                fixture,
                expected,
                probes=probes,
            ))
    return cells


def _composition_cells() -> list[dict[str, Any]]:
    """Cross public controls so compiled priority, not validation timing, wins."""

    rows: list[dict[str, Any]] = []
    strategy_probe = _sequence_probe("list", "sys_modules_mutation")
    fixture_probe = _fixture_probe("attribute_mutation")
    rows.append(_boundary_case(
        "rejected_strategy_and_fixture_subclasses",
        strategy_probe,
        fixture_probe,
        [_EXPECTED_STRATEGY_DIAGNOSTIC, _EXPECTED_FIXTURE_DIAGNOSTIC],
        probes=(strategy_probe, fixture_probe),
    ))
    rows.append(_boundary_case(
        "invalid_exact_strategy_and_malformed_exact_fixture",
        ["bogus"],
        _forge_fixture(dispatcher_output_mismatch=1),
        [_EXPECTED_STRATEGY_DIAGNOSTIC, _EXPECTED_FIXTURE_DIAGNOSTIC],
    ))
    rows.append(_boundary_case(
        "invalid_exact_strategy_and_higher_priority_nested_diagnostic",
        ["bogus"],
        _forge_fixture(nested_failure=_forge_failure(diagnostics=[{
            "code": "SOURCE_SHA256",
            "detail": "composition nested source",
            "phase": "nested:composition",
        }])),
        [
            _EXPECTED_STRATEGY_DIAGNOSTIC,
            _diagnostic_row(
                "SOURCE_SHA256",
                "composition nested source",
                "nested-resolver>nested:composition",
            ),
        ],
    ))
    rows.append(_boundary_case(
        "invalid_exact_strategy_and_lower_priority_nested_wrapper",
        ["bogus"],
        _forge_fixture(nested_failure=_forge_failure(
            code="OUTPUT_MISMATCH",
            detail="composition nested output",
            diagnostics=[],
        )),
        [
            _EXPECTED_STRATEGY_DIAGNOSTIC,
            _diagnostic_row(
                "OUTPUT_MISMATCH",
                "composition nested output",
                "nested-resolver",
            ),
        ],
    ))
    return rows


def _merge_containment_cells() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for strategy in ("latest_entry", "ordered_entry"):
        collector = DiagnosticCollector(COMPILED_PRIORITY)
        original_merge = collector.merge_nested

        def injected_merge(phase: str, failure: _ResolutionFailureSnapshot) -> None:
            raise RuntimeError("injected merge failure")

        collector.merge_nested = injected_merge  # type: ignore[method-assign]
        failure = ResolutionFailure("OUTPUT_MISMATCH", "merge injection", [])
        raw_exception = False
        try:
            collector.capture(
                "nested-resolver",
                "UNRESOLVED_CONTRADICTION",
                lambda failure=failure: (_ for _ in ()).throw(failure),
            )
            try:
                collector.final_adjudication()
                raise AssertionError("injected merge cell unexpectedly passed")
            except ResolutionFailure as exc:
                diagnostics = exc.diagnostics
                observed = {
                    "winner": exc.code,
                    "diagnostics": diagnostics,
                    "raw_exception": False,
                    "final_adjudicator_calls": exc.final_adjudicator_calls,
                }
        except Exception:
            raw_exception = True
            observed = {
                "winner": "RAW_EXCEPTION",
                "diagnostics": [],
                "raw_exception": True,
                "final_adjudicator_calls": 0,
            }
        finally:
            collector.merge_nested = original_merge  # type: ignore[method-assign]
        expected = {
            "winner": "UNRESOLVED_CONTRADICTION",
            "diagnostics": [_diagnostic_row(
                "UNRESOLVED_CONTRADICTION",
                "nested ResolutionFailure merge failed: RuntimeError",
                "nested-resolver:nested-merge",
            )],
            "raw_exception": False,
            "final_adjudicator_calls": 1,
        }
        if raw_exception or observed != expected:
            raise ResolutionFailure("OUTPUT_MISMATCH", f"merge containment cell failed: {strategy}")
        rows.append({
            "case_id": f"injected_merge_failure__{strategy}",
            "strategy_context": strategy,
            "expected": expected,
            "observed": observed,
            "matches_expected": True,
        })
    return rows


def _public_snapshot_normalization_contract() -> dict[str, Any]:
    strategy_cells = _strategy_equivalence_cells()
    fixture_cells = _fixture_equivalence_cells()
    merge_cells = _merge_containment_cells()
    composition_cells = _composition_cells()
    all_cells = strategy_cells + fixture_cells + merge_cells + composition_cells
    return {
        "strategy_admission": "type_is_exact_list_or_exact_tuple_before_any_hook_bearing_operation",
        "strategy_snapshot": "one_new_detached_tuple_and_no_caller_container_reread",
        "fixture_admission": "None_or_exact_FaultFixture_before_any_field_access",
        "failure_admission": "None_or_exact_ResolutionFailure_before_any_field_access",
        "diagnostic_container_admission": "exact_list_or_exact_tuple_only",
        "diagnostic_row_admission": "exact_dict_only",
        "deep_internal_types": [
            "_FaultFixtureSnapshot",
            "_ResolutionFailureSnapshot",
            "_DiagnosticSnapshot",
            "tuple",
            "exact_scalars",
        ],
        "merge_failure_boundary": "local_capture_nested_before_global_final_adjudication",
        "strategy_equivalence_cells": strategy_cells,
        "fixture_failure_diagnostic_composition_cells": fixture_cells,
        "merge_containment_cells": merge_cells,
        "composition_cells": composition_cells,
        "strategy_cell_count": len(strategy_cells),
        "fixture_failure_diagnostic_composition_cell_count": len(fixture_cells),
        "merge_containment_cell_count": len(merge_cells),
        "composition_cell_count": len(composition_cells),
        "total_cell_count": len(all_cells),
        "all_expected_equal_observed": all(row["matches_expected"] for row in all_cells),
        "all_raw_exception_false": all(not row["observed"]["raw_exception"] for row in all_cells),
        "all_final_adjudicator_calls_one": all(
            row["observed"]["final_adjudicator_calls"] == 1 for row in all_cells
        ),
        "all_rejected_subclass_hook_calls_zero": all(
            row["observed"].get("rejected_subclass_hook_calls", 0) == 0 for row in all_cells
        ),
        "all_rejected_subclass_traversal_calls_zero": all(
            row["observed"].get("rejected_subclass_traversal_calls", 0) == 0
            for row in all_cells
        ),
        "all_sys_modules_delta_empty": all(
            row["observed"].get("sys_modules_delta", []) == [] for row in all_cells
        ),
        "all_strategy_snapshots_detached": all(
            row["observed"].get("strategy_snapshot_detached", True) for row in all_cells
        ),
        "all_fixture_snapshots_detached": all(
            row["observed"].get("fixture_snapshot_detached", True) for row in all_cells
        ),
        "all_nested_failure_snapshots_detached": all(
            row["observed"].get("nested_failure_snapshot_detached", True) for row in all_cells
        ),
    }


def _read_bound_sources(
    root: Path,
    view: ReadView,
    collector: DiagnosticCollector,
) -> dict[str, bytes]:
    raw_by_path: dict[str, bytes] = {}
    for source_id, relative, size, digest in V11_PACKAGE:
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


class _NestedInferenceImportRewriter(ast.NodeTransformer):
    def __init__(self) -> None:
        self.matches = 0

    def visit_ImportFrom(self, node: ast.ImportFrom) -> ast.AST:
        fingerprint = sha256(ast.dump(node, include_attributes=False).encode("utf-8"))
        if fingerprint != NESTED_IMPORT_AST_SHA256:
            raise ResolutionFailure(
                "UNRESOLVED_CONTRADICTION",
                f"unexpected retained dispatcher ImportFrom fingerprint at line {node.lineno}: {fingerprint}",
            )
        self.matches += 1
        return ast.copy_location(
            ast.Assign(
                targets=[ast.Name(id="load_inference_config", ctx=ast.Store())],
                value=ast.Name(id="__preloaded_load_inference_config", ctx=ast.Load()),
            ),
            node,
        )

    def visit_Import(self, node: ast.Import) -> ast.AST:
        raise ResolutionFailure(
            "UNRESOLVED_CONTRADICTION",
            f"unexpected retained dispatcher Import at line {node.lineno}",
        )


def _dispatcher_namespace(raw: bytes, policy_view: InferencePolicyView) -> Any:
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
    rewriter = _NestedInferenceImportRewriter()
    module = ast.fix_missing_locations(rewriter.visit(module))
    if rewriter.matches != 1:
        raise ResolutionFailure(
            "UNRESOLVED_CONTRADICTION",
            f"expected exactly one fingerprinted nested inference import, observed {rewriter.matches}",
        )
    retained_imports = [
        node for node in ast.walk(module) if isinstance(node, (ast.Import, ast.ImportFrom))
    ]
    if retained_imports:
        raise ResolutionFailure(
            "UNRESOLVED_CONTRADICTION",
            f"compiled dispatcher projection retains {len(retained_imports)} import node(s)",
        )
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
        "__preloaded_load_inference_config": lambda: policy_view,
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
        "custody-git:terminal-head:type",
        "CUSTODY_DISAGREEMENT",
        lambda: _git(root, "cat-file", "-t", TERMINAL_HEAD),
    )
    collector.capture(
        "custody-git:terminal-head:reachable",
        "CUSTODY_DISAGREEMENT",
        lambda: _git(root, "merge-base", "--is-ancestor", TERMINAL_HEAD, "HEAD"),
    )


def _collect_custody(
    root: Path,
    view: ReadView,
    collector: DiagnosticCollector,
    fixture: _FaultFixtureSnapshot | None,
    policy_view: InferencePolicyView | None,
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
            collector.add("CUSTODY_DISAGREEMENT", "terminal v11 queue raw-byte binding drift", "custody:queue")
    if isinstance(receipt_raw, bytes):
        receipt = collector.capture(
            "custody:receipt-strict-parse",
            "CUSTODY_DISAGREEMENT",
            lambda: strict_json(receipt_raw, RECEIPT_PATH),
        )
        if len(receipt_raw) != RECEIPT_SIZE or sha256(receipt_raw) != RECEIPT_SHA256:
            collector.add("CUSTODY_DISAGREEMENT", "v11 snapshot receipt raw-byte binding drift", "custody:receipt")
    if isinstance(dispatcher_raw, bytes) and isinstance(policy_view, InferencePolicyView):
        dispatch = collector.capture(
            "dependency:dispatcher-definition-load",
            "UNRESOLVED_CONTRADICTION",
            lambda: _dispatcher_namespace(dispatcher_raw, policy_view),
        )
    elif isinstance(dispatcher_raw, bytes):
        collector.add(
            "UNRESOLVED_CONTRADICTION",
            "inference policy projection unavailable for dispatcher definition load",
            "dependency:dispatcher-definition-load",
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
            collector.add("CUSTODY_ABSENT", "completed v11 snapshot archive absent", "custody:archive")
        else:
            checks = (
                (archive.get("commit_sha") == SNAPSHOT_COMMIT, "snapshot commit identity drift"),
                (archive.get("parent_sha") == SNAPSHOT_PARENT, "snapshot parent identity drift"),
                (archive.get("path_sha256") == SNAPSHOT_PATH_HASHES, "snapshot path hash set drift"),
                (archive.get("record_ids") == list(REQUIRED_MESSAGE_IDS), "snapshot required record IDs drift"),
                (archive.get("source_task_ids") == ["TASK-20260813-2174b9"], "snapshot source topology drift"),
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
        if plan.get("plan_sha256") != DISPATCHER_PLAN_SHA256:
            collector.add("CUSTODY_DISAGREEMENT", "dispatcher plan digest drift", "custody:plan")
        terminal_plan = copy.deepcopy(plan)
        terminal_plan.pop("plan_sha256", None)
        terminal_plan.pop("content_only_archives", None)
        if canonical_digest(terminal_plan) != PLAN_SHA256:
            collector.add("CUSTODY_DISAGREEMENT", "terminal canonical plan digest drift", "custody:plan")
        if plan.get("source_queue_sha256") != PLAN_SOURCE_QUEUE_SHA256:
            collector.add("CUSTODY_DISAGREEMENT", "canonical source queue digest drift", "custody:plan")
        gates = plan.get("gates")
        if not isinstance(gates, dict) or len(gates) != 10 or not all(gates.values()):
            collector.add("CUSTODY_DISAGREEMENT", "one or more canonical dispatcher gates failed", "custody:plan")
        if plan.get("dispatches") != []:
            collector.add("CUSTODY_DISAGREEMENT", "terminal v11 queue unexpectedly dispatches work", "custody:plan")
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


def _v11_lineage_object() -> list[dict[str, Any]]:
    return [
        {"source_id": source_id, "path": path, "size_bytes": size, "sha256": digest}
        for source_id, path, size, digest in V11_PACKAGE
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
            "terminal_plan_sha256": PLAN_SHA256,
            "dispatcher_plan_sha256": DISPATCHER_PLAN_SHA256,
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
        "terminal_verified_head": TERMINAL_HEAD,
        "failure_semantics": "typed_compiled_order_diagnostics_with_one_final_adjudication",
    }


def _conformance_fixtures(public_contract: dict[str, Any] | None = None) -> dict[str, Any]:
    pairs = [
        {
            "first": first,
            "second": second,
            "expected": first if PRIORITY_BY_CODE[first] <= PRIORITY_BY_CODE[second] else second,
        }
        for first in ERROR_CODES
        for second in ERROR_CODES
    ]
    public_summary = None if public_contract is None else {
        "strategy_cell_count": public_contract["strategy_cell_count"],
        "fixture_failure_diagnostic_composition_cell_count": public_contract[
            "fixture_failure_diagnostic_composition_cell_count"
        ],
        "merge_containment_cell_count": public_contract["merge_containment_cell_count"],
        "composition_cell_count": public_contract["composition_cell_count"],
        "total_cell_count": public_contract["total_cell_count"],
        "all_expected_equal_observed": public_contract["all_expected_equal_observed"],
        "all_raw_exception_false": public_contract["all_raw_exception_false"],
        "all_final_adjudicator_calls_one": public_contract["all_final_adjudicator_calls_one"],
        "all_rejected_subclass_hook_calls_zero": public_contract[
            "all_rejected_subclass_hook_calls_zero"
        ],
        "all_rejected_subclass_traversal_calls_zero": public_contract[
            "all_rejected_subclass_traversal_calls_zero"
        ],
        "all_sys_modules_delta_empty": public_contract["all_sys_modules_delta_empty"],
        "all_strategy_snapshots_detached": public_contract[
            "all_strategy_snapshots_detached"
        ],
        "all_fixture_snapshots_detached": public_contract[
            "all_fixture_snapshots_detached"
        ],
        "all_nested_failure_snapshots_detached": public_contract[
            "all_nested_failure_snapshots_detached"
        ],
    }
    return {
        "malformed_public_controls": {
            "strategies": ["null", "string", "mapping", "integer_member", "unknown_member", "empty"],
            "fault_fixture": [
                "plain_object",
                "mapping",
                "empty_fixture_id",
                "non_boolean_field",
                "bad_plan_mutation",
                "malformed_nested_failure",
            ],
            "strategy_expected": "ECOMP_LATEST_ONLY",
            "fault_fixture_expected": "TYPE_COERCION",
            "raw_exception": False,
            "final_adjudicator_calls": 1,
        },
        "inference_policy_projection": {
            "exact_bound_paths": [row[1] for row in INFERENCE_BINDINGS],
            "nested_import_ast_sha256": NESTED_IMPORT_AST_SHA256,
            "compiled_import_node_count": 0,
            "unknown_policy_rejected": True,
            "below_floor_review_rejected": True,
            "positive_sys_modules_delta": [],
        },
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
        "public_snapshot_normalization": public_summary,
        "experiment_runs_consumed": 0,
    }


def generate_input(v11_input: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(v11_input)
    result["schema"] = "crypto.autoresearch.resolution_input.v12"
    result["version"] = VERSION
    composition = result["composition"]
    composition["controlling_v11_disposition"] = {
        "decision_id": "DEC-20260813-9f5120",
        "disposition": "not_approved_revise",
        "material_findings": ["O-INSTR-V11-1", "O-INSTR-V11-2", "O-INSTR-V11-3"],
        "scientific_effect": "none",
    }
    public_contract = _public_snapshot_normalization_contract()
    composition["public_snapshot_normalization"] = public_contract
    composition["v11_package_manifest"] = _v11_lineage_object()
    composition["snapshot_custody"] = _custody_contract()
    composition["error_priority"] = list(COMPILED_PRIORITY)
    composition["global_diagnostic_contract"] = {
        "collector_count_per_public_resolve": 1,
        "collector_constructed_from": "immutable_COMPILED_PRIORITY",
        "collector_is_first_public_resolve_object": True,
        "all_fallible_stages_typed_and_captured": True,
        "independent_stages_continue_after_capture": True,
        "nested_diagnostics_merged": True,
        "nested_merge_failure_locally_contained": True,
        "nested_merge_consumes_only_detached_immutable_failure": True,
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
        "canonical_output_framing": "v12_sorted_compact_UTF8_JSON_exactly_one_terminal_LF",
        "custody_optional": False,
        "public_entry_collector": "constructed_first_from_immutable_compiled_order",
        "public_entry_stage_capture": "typed_all_fallible_stages",
        "public_entry_independent_continuation": True,
        "nested_diagnostic_merge": True,
        "sole_final_adjudication": True,
        "dependency_loading": "exact_three_file_preloaded_import_free_InferencePolicyView",
        "effectful_module_import": False,
        "normal_entry_without_authenticated_custody": "prohibited",
        "v11_scientific_source_payload": "byte_preserved_under_two_subdigests",
        "public_control_normalization": "exact_type_one_snapshot_deep_detached_before_later_use",
        "strategy_container_domain": "exact_builtin_list_or_tuple_only",
        "strategy_caller_traversals": 1,
        "fixture_domain": "None_or_exact_FaultFixture_only",
        "nested_failure_domain": "None_or_exact_ResolutionFailure_only",
        "diagnostic_container_domain": "exact_builtin_list_or_tuple_only",
        "diagnostic_row_domain": "exact_builtin_dict_only",
        "nested_merge_failure_containment": "local_collector_boundary_then_one_global_adjudication",
    })
    composition["resolver_contract"] = resolver_contract
    static = copy.deepcopy(composition["static_conformance_fixtures"])
    static["v12"] = _conformance_fixtures(public_contract)
    composition["static_conformance_fixtures"] = static
    composition["v11_payload_binding"] = {
        "source_fields_sha256": V11_SOURCE_FIELDS_SHA256,
        "origin_rows_sha256": V11_ORIGIN_ROWS_SHA256,
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
        collector.add("UNRESOLVED_CONTRADICTION", "v12 input is not a mapping", "input")
        return
    if input_object.get("schema") != "crypto.autoresearch.resolution_input.v12" or input_object.get("version") != VERSION:
        collector.add("VERSION_CHAIN", "v12 input schema or version drift", "input:version")
    if input_object.get("experiment_id") != EXPERIMENT_ID:
        collector.add("VERSION_CHAIN", "experiment identity drift", "input:version")
    composition = input_object.get("composition")
    if not isinstance(composition, dict):
        collector.add("UNRESOLVED_CONTRADICTION", "composition is not a mapping", "input")
        collector.add("OUTPUT_MISMATCH", "v12 input differs from generated contract", "input")
        return
    collector.compare_source_table(composition.get("error_priority"), "input:priority")
    if expected_input is None:
        collector.add("UNRESOLVED_CONTRADICTION", "generated v12 input prerequisite unavailable", "input")
        return
    expected_composition = expected_input["composition"]
    if input_object.get("authority") != expected_input.get("authority"):
        collector.add("AUTHORITY_NONZERO", "v12 authority boundary drift", "input:authority")
    for field, code in (
        ("snapshot_custody", "CUSTODY_DISAGREEMENT"),
        ("v11_package_manifest", "SOURCE_SHA256"),
        ("v11_payload_binding", "OUTPUT_MISMATCH"),
        ("controlling_v11_disposition", "VERSION_CHAIN"),
        ("public_snapshot_normalization", "TYPE_COERCION"),
        ("resolver_contract", "GENERIC_MERGE"),
        ("global_diagnostic_contract", "GENERIC_MERGE"),
    ):
        if composition.get(field) != expected_composition.get(field):
            collector.add(code, f"v12 {field} drift", f"input:{field}")

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
        collector.add("OUTPUT_MISMATCH", "v12 input differs from the complete generated contract", "input")


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


def _verify_v11_payload(
    v11_resolved: Any,
    v11_origin: Any,
    collector: DiagnosticCollector,
) -> None:
    if not isinstance(v11_resolved, dict):
        collector.add("UNRESOLVED_CONTRADICTION", "v11 resolved contract unavailable", "payload")
    else:
        source_fields = v11_resolved.get("source_fields")
        if not isinstance(source_fields, dict) or len(source_fields) != 1363:
            collector.add("OUTPUT_MISMATCH", "v11 source_fields count drift", "payload")
        elif sha256(canonical_bytes(source_fields)) != V11_SOURCE_FIELDS_SHA256:
            collector.add("OUTPUT_MISMATCH", "v11 source_fields subdigest drift", "payload")
    if not isinstance(v11_origin, dict):
        collector.add("UNRESOLVED_CONTRADICTION", "v11 origin trace unavailable", "payload")
    else:
        rows = v11_origin.get("rows")
        if not isinstance(rows, list) or len(rows) != 1363:
            collector.add("OUTPUT_MISMATCH", "v11 origin rows count drift", "payload")
        elif sha256(canonical_bytes(rows)) != V11_ORIGIN_ROWS_SHA256:
            collector.add("OUTPUT_MISMATCH", "v11 origin rows subdigest drift", "payload")


def _json_pointer_token(value: str) -> str:
    return value.replace("~", "~0").replace("/", "~1")


def _v12_origin_rows(path: str, value: Any) -> list[dict[str, Any]]:
    """Trace every v12-owned node while leaving inherited source rows intact."""

    if type(value) is dict:
        kind = "object"
    elif type(value) is list:
        kind = "array"
    elif value is None:
        kind = "null"
    elif type(value) is bool:
        kind = "boolean"
    elif type(value) is int:
        kind = "integer"
    elif type(value) is str:
        kind = "string"
    else:
        raise ResolutionFailure("TYPE_COERCION", f"untraceable v12 field type at {path}")
    rows = [{
        "owner_source_id": "amendment_v12",
        "resolved_field_path": path,
        "authority_role": "additive_control_plane_only",
        "value_kind": kind,
        "value_sha256": canonical_digest(value),
    }]
    if type(value) is dict:
        for key in sorted(value):
            if type(key) is not str:
                raise ResolutionFailure("TYPE_COERCION", f"non-string v12 field key at {path}")
            rows.extend(_v12_origin_rows(f"{path}/{_json_pointer_token(key)}", value[key]))
    elif type(value) is list:
        for index, child in enumerate(value):
            rows.extend(_v12_origin_rows(f"{path}/{index}", child))
    return rows


def _v12_owned_resolved_fields(resolved: dict[str, Any]) -> tuple[tuple[str, Any], ...]:
    composition = resolved["composition"]
    return (
        ("/schema", resolved["schema"]),
        ("/version", resolved["version"]),
        ("/resolution_input", resolved["resolution_input"]),
        ("/source_fields_sha256", resolved["source_fields_sha256"]),
        ("/composition/controlling_v11_disposition", composition["controlling_v11_disposition"]),
        ("/composition/error_priority", composition["error_priority"]),
        ("/composition/global_diagnostic_contract", composition["global_diagnostic_contract"]),
        ("/composition/public_snapshot_normalization", composition["public_snapshot_normalization"]),
        ("/composition/resolver_contract", composition["resolver_contract"]),
        ("/composition/snapshot_custody", composition["snapshot_custody"]),
        ("/composition/static_conformance_fixtures/v12", composition["static_conformance_fixtures"]["v12"]),
        ("/composition/v11_package_manifest", composition["v11_package_manifest"]),
        ("/composition/v11_payload_binding", composition["v11_payload_binding"]),
    )


def _derive_outputs(
    input_object: dict[str, Any],
    input_raw: bytes,
    v11_resolved: dict[str, Any],
    v11_origin: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    input_binding = {"path": DEFAULT_INPUT, "size_bytes": len(input_raw), "sha256": sha256(input_raw)}
    resolved = copy.deepcopy(v11_resolved)
    resolved["schema"] = "crypto.autoresearch.resolved_contract.v12"
    resolved["version"] = VERSION
    resolved["resolution_input"] = input_binding
    resolved["authority"] = copy.deepcopy(input_object["authority"])
    resolved["preservation"] = copy.deepcopy(input_object["preservation"])
    composition = resolved["composition"]
    input_composition = input_object["composition"]
    for field in (
        "controlling_v11_disposition",
        "error_priority",
        "global_diagnostic_contract",
        "resolver_contract",
        "public_snapshot_normalization",
        "snapshot_custody",
        "static_conformance_fixtures",
        "v11_package_manifest",
        "v11_payload_binding",
    ):
        composition[field] = copy.deepcopy(input_composition[field])
    source_fields = resolved["source_fields"]
    resolved["source_fields_sha256"] = sha256(canonical_bytes(source_fields))

    origin = copy.deepcopy(v11_origin)
    origin["schema"] = "crypto.autoresearch.origin_trace.v12"
    origin["version"] = VERSION
    origin["resolution_input"] = input_binding
    v12_owned = _v12_owned_resolved_fields(resolved)
    origin["v12_composition_origin_rows"] = [
        row
        for field_path, field_value in v12_owned
        for row in _v12_origin_rows(field_path, field_value)
    ]
    origin["v12_composition_origin_rows_sha256"] = sha256(
        canonical_bytes(origin["v12_composition_origin_rows"])
    )
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
    strategies: Any,
    *,
    materialize_input: bool = False,
    read_view: ReadView | None = None,
    fault_fixture: Any = None,
    compare_materialized: bool = True,
) -> tuple[bytes, bytes, bytes, dict[str, Any]]:
    collector = DiagnosticCollector(COMPILED_PRIORITY)
    normalized_controls = collector.capture(
        "public-entry:controls",
        "TYPE_COERCION",
        lambda: _normalize_public_controls(collector, strategies, fault_fixture),
    )
    if type(normalized_controls) is tuple and len(normalized_controls) == 2:
        normalized_strategies, normalized_fault_fixture = normalized_controls
    else:
        normalized_strategies, normalized_fault_fixture = ("latest_entry",), None

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

    policy_view = _load_inference_policy_view(root_path, view, collector)

    raw_by_path = _read_bound_sources(root_path, view, collector)
    v11_input = _parse_bound_json(raw_by_path, V11_INPUT, collector)
    v11_resolved = _parse_bound_json(raw_by_path, V11_RESOLVED, collector)
    v11_origin = _parse_bound_json(raw_by_path, V11_ORIGIN, collector)

    expected_input = None
    if isinstance(v11_input, dict):
        expected_input = collector.capture(
            "input-generation:v12",
            "OUTPUT_MISMATCH",
            lambda: generate_input(v11_input),
        )
    else:
        collector.add("UNRESOLVED_CONTRADICTION", "v12 input generation prerequisite unavailable", "input-generation")
    if normalized_fault_fixture is not None and normalized_fault_fixture.input_generation_output_mismatch:
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
                        "v12 resolution input is not canonical compact JSON plus one LF",
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
        lambda: _collect_custody(root_path, view, collector, normalized_fault_fixture, policy_view),
    )
    quarantine_results = collector.capture(
        "quarantine-validation",
        "OUTPUT_MISMATCH",
        lambda: _verify_quarantines(root_path, collector),
    )
    collector.capture(
        "payload-validation",
        "OUTPUT_MISMATCH",
        lambda: _verify_v11_payload(v11_resolved, v11_origin, collector),
    )

    if normalized_fault_fixture is not None and normalized_fault_fixture.nested_failure is not None:
        collector.capture_nested(
            "nested-resolver",
            "UNRESOLVED_CONTRADICTION",
            normalized_fault_fixture.nested_failure,
        )

    resolved_raw = None
    origin_raw = None
    strategy_outputs: list[tuple[bytes, bytes]] = []
    if (
        isinstance(input_object, dict)
        and isinstance(input_raw, bytes)
        and isinstance(v11_resolved, dict)
        and isinstance(v11_origin, dict)
    ):
        for strategy in normalized_strategies:
            derived = collector.capture(
                f"output-derivation:{strategy}",
                "OUTPUT_MISMATCH",
                lambda: _derive_outputs(input_object, input_raw, v11_resolved, v11_origin),
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
        "dependency_loading": "exact_three_file_preloaded_import_free_InferencePolicyView",
        "experiment_id": EXPERIMENT_ID,
        "experiment_runs_consumed": 0,
        "final_adjudicator_calls": 1,
        "origin_rows_sha256": V11_ORIGIN_ROWS_SHA256,
        "origin_trace": {"size_bytes": len(origin_raw), "sha256": sha256(origin_raw)},
        "quarantined_post_snapshot_mutations": quarantine_results,
        "resolved_contract": {"size_bytes": len(resolved_raw), "sha256": sha256(resolved_raw)},
        "resolution_input": {"size_bytes": len(input_raw), "sha256": sha256(input_raw)},
        "source_fields_sha256": V11_SOURCE_FIELDS_SHA256,
        "status": "PASS",
        "strategies": list(normalized_strategies),
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
        archive["path_sha256"][V11_RESOLVED] = "0" * 64
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
        receipt["path_sha256"][V11_RESOLVED] = "f" * 64
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
        edges[0]["successor_pointer"] = "/missing-v11-control-pointer"
        edges[1]["edge_id"] = "v11-drifted-edge-id"
    elif case == "priority_table_drift":
        composition["error_priority"] = list(reversed(COMPILED_PRIORITY))
    else:
        raise ResolutionFailure("UNRESOLVED_CONTRADICTION", f"unknown input case: {case}")
    return result


def _public_case(
    root: Path,
    strategy: Any,
    *,
    view: ReadView | None = None,
    fixture: Any = None,
) -> dict[str, Any]:
    return _raw_public_case(root, [strategy], view=view, fixture=fixture)


def _raw_public_case(
    root: Path,
    strategies: Any,
    *,
    view: ReadView | None = None,
    fixture: Any = None,
) -> dict[str, Any]:
    try:
        resolve(root, strategies, read_view=view, fault_fixture=fixture)
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
        return {
            "winner": exc.code,
            "diagnostics": diagnostics,
            "raw_exception": False,
            "final_adjudicator_calls": exc.final_adjudicator_calls,
        }
    return {"winner": "PASS", "diagnostics": [], "raw_exception": False, "final_adjudicator_calls": 1}


def _adjudicate_codes(codes: list[str]) -> dict[str, Any]:
    collector = DiagnosticCollector(COMPILED_PRIORITY)
    for index, code in enumerate(codes):
        collector.add(code, f"injected ordered fault {index}", "fixture")
    try:
        collector.final_adjudication()
    except ResolutionFailure as exc:
        return {"winner": exc.code, "diagnostics": exc.diagnostics}
    raise AssertionError("diagnostic fixture unexpectedly passed")


def _malformed_fault_fixtures() -> list[tuple[str, Any]]:
    def forged(**changes: Any) -> FaultFixture:
        fixture = object.__new__(FaultFixture)
        values = {
            "fixture_id": "malformed-control",
            "plan_mutation": None,
            "dispatcher_output_mismatch": False,
            "input_generation_output_mismatch": False,
            "nested_failure": None,
        }
        values.update(changes)
        for key, value in values.items():
            object.__setattr__(fixture, key, value)
        return fixture

    malformed_nested = ResolutionFailure(
        "OUTPUT_MISMATCH",
        "malformed nested diagnostics",
        [{"code": "SOURCE_SHA256", "detail": "", "phase": "nested"}],
    )
    return [
        ("plain_object", object()),
        ("mapping", {"fixture_id": "mapping"}),
        ("empty_fixture_id", forged(fixture_id="")),
        ("non_boolean_field", forged(dispatcher_output_mismatch=1)),
        ("bad_plan_mutation", forged(plan_mutation="unknown-mutation")),
        ("malformed_nested_failure", forged(nested_failure=malformed_nested)),
    ]


def _inference_semantic_fixtures(root: Path) -> dict[str, Any]:
    collector = DiagnosticCollector(COMPILED_PRIORITY)
    view = ReadView()
    policy_view = _load_inference_policy_view(root, view, collector)
    if not isinstance(policy_view, InferencePolicyView):
        raise ResolutionFailure("OUTPUT_MISMATCH", "inference policy view fixture unavailable")
    dispatcher = _dispatcher_namespace(repository_path(root, DISPATCHER_PATH).read_bytes(), policy_view)
    queue = strict_json(repository_path(root, QUEUE_PATH).read_bytes(), QUEUE_PATH)
    used_policies: set[str] = set()
    used_roles: set[str] = set()
    used_efforts: set[str] = set()
    representative: dict[str, tuple[str, str | None]] = {}
    for task in queue["tasks"]:
        handoff = task["handoff"]
        dispatcher.validate_inference(handoff, task["role"], f"fixture.{task['id']}")
        used_roles.add(task["role"])
        inference = handoff.get("inference") or {}
        if inference.get("policy") is not None:
            used_policies.add(inference["policy"])
            representative.setdefault(
                inference["policy"],
                (task["role"], inference.get("reasoning_effort")),
            )
        if inference.get("reasoning_effort") is not None:
            used_efforts.add(inference["reasoning_effort"])

    alias_rows = []
    for policy_id in sorted(used_policies):
        canonical = policy_view.canonical_policy(policy_id)
        for alias in policy_view.policy_table[canonical].get("aliases") or ():
            observed = policy_view.canonical_policy(alias)
            if observed != canonical:
                raise ResolutionFailure("OUTPUT_MISMATCH", f"policy alias drift: {alias}")
            role, effort = representative[policy_id]
            dispatcher.validate_inference(
                {"inference": {"policy": alias, "reasoning_effort": effort}},
                role,
                f"fixture.alias.{alias}",
            )
            alias_rows.append({"alias": alias, "canonical": observed})

    original_sys_path = list(sys.path)
    repository_root = str(root.resolve())
    if repository_root not in sys.path:
        sys.path.insert(0, repository_root)
    try:
        canonical_adapter = importlib.import_module("orchestration.adapter")
        canonical_dispatcher = importlib.import_module("tools.research_dispatch")
        canonical_config = canonical_adapter.load()
    finally:
        sys.path[:] = original_sys_path
    canonical_dispatcher_path = Path(canonical_dispatcher.__file__).resolve()
    if canonical_dispatcher_path != repository_path(root, DISPATCHER_PATH).resolve():
        raise ResolutionFailure(
            "OUTPUT_MISMATCH",
            f"canonical dispatcher imported from wrong path: {canonical_dispatcher_path}",
        )

    frozen_policy_names = [
        "coordinator-orchestration-code",
        "coordinator-ultra-code",
        "coordinator-archive",
        "executor-implementation",
        "executor-terra",
        "review-adversarial",
        "review-xhigh",
        "validator-independent",
        "red-team-adversarial",
    ]
    frozen_efforts = ["high", "xhigh"]
    frozen_roles = ["coordinator", "executor", "red-team"]

    def validation_outcome(validate: Callable[..., None], handoff: dict[str, Any], role: str, location: str) -> dict[str, str]:
        try:
            validate(handoff, role, location)
        except Exception as exc:
            if type(exc).__name__ != "DispatchError":
                raise
            return {"outcome": "DispatchError", "detail": str(exc)}
        return {"outcome": "PASS", "detail": ""}

    combination_rows = []
    for policy_name in frozen_policy_names:
        projected_canonical = policy_view.canonical_policy(policy_name)
        canonical_canonical = canonical_config.canonical_policy(policy_name)
        if projected_canonical != canonical_canonical:
            raise ResolutionFailure(
                "OUTPUT_MISMATCH",
                f"projected/canonical policy mapping mismatch: {policy_name}",
            )
        for effort in frozen_efforts:
            for role in frozen_roles:
                handoff = {"inference": {"policy": policy_name, "reasoning_effort": effort}}
                location = f"fixture.combination.{policy_name}.{effort}.{role}"
                projected = validation_outcome(dispatcher.validate_inference, handoff, role, location)
                canonical = validation_outcome(
                    canonical_dispatcher.validate_inference,
                    handoff,
                    role,
                    location,
                )
                if projected != canonical:
                    raise ResolutionFailure(
                        "OUTPUT_MISMATCH",
                        f"projected/canonical inference mismatch: {policy_name}/{effort}/{role}",
                    )
                combination_rows.append({
                    "policy_or_alias": policy_name,
                    "canonical_policy": projected_canonical,
                    "reasoning_effort": effort,
                    "role": role,
                    "projected": projected,
                    "canonical": canonical,
                    "matches": True,
                })
    if len(combination_rows) != 54:
        raise ResolutionFailure("OUTPUT_MISMATCH", "inference equivalence matrix is not 54 cells")

    handoff_rows = []
    for task in queue["tasks"]:
        location = f"fixture.handoff.{task['id']}"
        projected = validation_outcome(
            dispatcher.validate_inference,
            task["handoff"],
            task["role"],
            location,
        )
        canonical = validation_outcome(
            canonical_dispatcher.validate_inference,
            task["handoff"],
            task["role"],
            location,
        )
        if projected != canonical:
            raise ResolutionFailure(
                "OUTPUT_MISMATCH",
                f"projected/canonical handoff mismatch: {task['id']}",
            )
        handoff_rows.append({
            "task_id": task["id"],
            "projected": projected,
            "canonical": canonical,
            "matches": True,
        })

    unknown_handoff = {"inference": {"policy": "unknown-policy-v11"}}
    projected_unknown = validation_outcome(
        dispatcher.validate_inference, unknown_handoff, "executor", "fixture.unknown"
    )
    canonical_unknown = validation_outcome(
        canonical_dispatcher.validate_inference,
        unknown_handoff,
        "executor",
        "fixture.unknown",
    )
    if projected_unknown != canonical_unknown or projected_unknown["outcome"] != "DispatchError":
        raise ResolutionFailure("OUTPUT_MISMATCH", "unknown inference policy was accepted")

    below_floor_handoff = {
        "inference": {"policy": "review-adversarial", "reasoning_effort": "high"}
    }
    projected_floor = validation_outcome(
        dispatcher.validate_inference,
        below_floor_handoff,
        "red-team",
        "fixture.below-floor",
    )
    canonical_floor = validation_outcome(
        canonical_dispatcher.validate_inference,
        below_floor_handoff,
        "red-team",
        "fixture.below-floor",
    )
    if projected_floor != canonical_floor or projected_floor["outcome"] != "DispatchError":
        raise ResolutionFailure("OUTPUT_MISMATCH", "below-floor independent review was accepted")

    return {
        "used_policies": sorted(used_policies),
        "used_policy_aliases": alias_rows,
        "used_roles": sorted(used_roles),
        "used_efforts": sorted(used_efforts),
        "effort_order": list(policy_view.effort_order),
        "frozen_policy_and_alias_names": frozen_policy_names,
        "frozen_efforts": frozen_efforts,
        "frozen_roles": frozen_roles,
        "projected_vs_canonical_combinations": combination_rows,
        "projected_vs_canonical_combination_count": len(combination_rows),
        "projected_vs_canonical_mismatch_count": 0,
        "terminal_handoff_equivalence": handoff_rows,
        "terminal_handoff_equivalence_count": len(handoff_rows),
        "unknown_policy_projected": projected_unknown,
        "unknown_policy_canonical": canonical_unknown,
        "below_floor_projected": projected_floor,
        "below_floor_canonical": canonical_floor,
        "unknown_policy_rejected": True,
        "below_floor_review_rejected": True,
        "compiled_projection_import_node_count": 0,
    }


def _full_normalization_probe_case(
    root: Path,
    case_id: str,
    strategies: Any,
    fixture: Any,
    expected_winner: str,
    probes: tuple[Any, ...] = (),
) -> dict[str, Any]:
    """Replay a boundary falsifier through the complete public resolver."""

    modules_before = {name: id(module) for name, module in sys.modules.items()}
    try:
        outcome = _raw_public_case(root, strategies, fixture=fixture)
    except Exception as exc:
        outcome = {
            "winner": "RAW_EXCEPTION",
            "diagnostics": [],
            "raw_exception": True,
            "raw_exception_type": type(exc).__name__,
            "final_adjudicator_calls": 0,
        }
    modules_after = {name: id(module) for name, module in sys.modules.items()}
    module_delta = sorted(
        name
        for name in set(modules_before) | set(modules_after)
        if modules_before.get(name) != modules_after.get(name)
    )
    hook_calls, traversal_calls, sentinels = _probe_metrics(probes)
    for sentinel in sentinels:
        sys.modules.pop(sentinel, None)
    if (
        outcome["winner"] != expected_winner
        or outcome["raw_exception"]
        or outcome["final_adjudicator_calls"] != 1
        or hook_calls != 0
        or traversal_calls != 0
        or module_delta
    ):
        raise ResolutionFailure(
            "OUTPUT_MISMATCH",
            f"full public normalization falsifier failed: {case_id}",
        )
    return {
        "case_id": case_id,
        "expected_winner": expected_winner,
        "observed_winner": outcome["winner"],
        "diagnostics": outcome["diagnostics"],
        "raw_exception": outcome["raw_exception"],
        "final_adjudicator_calls": outcome["final_adjudicator_calls"],
        "rejected_subclass_hook_calls": hook_calls,
        "rejected_subclass_traversal_calls": traversal_calls,
        "sys_modules_delta": module_delta,
        "matches_expected": True,
    }


def run_self_test(root: Path) -> dict[str, Any]:
    modules_before = {name: id(module) for name, module in sys.modules.items()}
    status_before = _git(root, "status", "--porcelain=v1", "--untracked-files=all")
    repository_files_before = sorted(str(path.relative_to(root)) for path in root.rglob("*") if path.is_file())
    cache_before = sorted(
        str(path.relative_to(root))
        for path in root.rglob("*")
        if path.name == "__pycache__" or path.suffix in {".pyc", ".pyo"}
    )
    input_raw, resolved_raw, origin_raw, positive = resolve(root, ["latest_entry", "ordered_entry"])
    modules_after = {name: id(module) for name, module in sys.modules.items()}
    status_after = _git(root, "status", "--porcelain=v1", "--untracked-files=all")
    repository_files_after = sorted(str(path.relative_to(root)) for path in root.rglob("*") if path.is_file())
    cache_after = sorted(
        str(path.relative_to(root))
        for path in root.rglob("*")
        if path.name == "__pycache__" or path.suffix in {".pyc", ".pyo"}
    )
    if modules_after != modules_before:
        module_delta = sorted(
            name
            for name in set(modules_before) | set(modules_after)
            if modules_before.get(name) != modules_after.get(name)
        )
        raise ResolutionFailure(
            "OUTPUT_MISMATCH",
            f"positive public resolve changed sys.modules identities: {module_delta}",
        )
    if status_after != status_before:
        raise ResolutionFailure("OUTPUT_MISMATCH", "positive public resolve changed repository state")
    if repository_files_after != repository_files_before:
        raise ResolutionFailure("OUTPUT_MISMATCH", "positive public resolve changed repository path inventory")
    if cache_after != cache_before:
        raise ResolutionFailure("OUTPUT_MISMATCH", "positive public resolve changed cache or bytecode state")
    input_object = strict_json(input_raw, DEFAULT_INPUT)
    resolved_object = strict_json(resolved_raw, DEFAULT_RESOLVED)
    origin_object = strict_json(origin_raw, DEFAULT_ORIGIN)
    public_contract = _public_snapshot_normalization_contract()
    if input_object["composition"].get("public_snapshot_normalization") != public_contract:
        raise ResolutionFailure(
            "OUTPUT_MISMATCH",
            "materialized public snapshot-normalization matrix drift",
        )
    if not all((
        public_contract["all_expected_equal_observed"],
        public_contract["all_raw_exception_false"],
        public_contract["all_final_adjudicator_calls_one"],
        public_contract["all_rejected_subclass_hook_calls_zero"],
        public_contract["all_rejected_subclass_traversal_calls_zero"],
        public_contract["all_sys_modules_delta_empty"],
        public_contract["all_strategy_snapshots_detached"],
        public_contract["all_fixture_snapshots_detached"],
        public_contract["all_nested_failure_snapshots_detached"],
    )):
        raise ResolutionFailure("OUTPUT_MISMATCH", "public snapshot-normalization aggregate failed")
    if resolved_object["composition"].get("public_snapshot_normalization") != public_contract:
        raise ResolutionFailure(
            "OUTPUT_MISMATCH",
            "resolved public snapshot-normalization matrix drift",
        )
    expected_v12_origin_rows = [
        row
        for field_path, field_value in _v12_owned_resolved_fields(resolved_object)
        for row in _v12_origin_rows(field_path, field_value)
    ]
    observed_v12_origin_rows = origin_object.get("v12_composition_origin_rows")
    if observed_v12_origin_rows != expected_v12_origin_rows:
        raise ResolutionFailure("OUTPUT_MISMATCH", "v12 exhaustive origin rows drift")
    origin_paths = [row["resolved_field_path"] for row in expected_v12_origin_rows]
    if len(origin_paths) != len(set(origin_paths)):
        raise ResolutionFailure("OUTPUT_MISMATCH", "v12 exhaustive origin paths are duplicated")
    v12_origin_rows_sha256 = sha256(canonical_bytes(expected_v12_origin_rows))
    if origin_object.get("v12_composition_origin_rows_sha256") != v12_origin_rows_sha256:
        raise ResolutionFailure("OUTPUT_MISMATCH", "v12 exhaustive origin-row digest drift")

    full_falsifier_cells = []
    for ancestry in ("list", "tuple"):
        for profile in (
            "stable",
            "toctou_bogus",
            "second_runtime",
            "immediate_raising",
            "sys_modules_mutation",
        ):
            probe = _sequence_probe(ancestry, profile)
            full_falsifier_cells.append(_full_normalization_probe_case(
                root,
                f"strategy_{ancestry}_subclass_{profile}",
                probe,
                None,
                "ECOMP_LATEST_ONLY",
                (probe,),
            ))
    for profile in ("attribute_raising", "attribute_mutation", "sys_modules_mutation"):
        probe = _fixture_probe(profile)
        full_falsifier_cells.append(_full_normalization_probe_case(
            root,
            f"fixture_subclass_{profile}",
            ["latest_entry"],
            probe,
            "TYPE_COERCION",
            (probe,),
        ))
        failure_probe = _failure_probe(profile)
        full_falsifier_cells.append(_full_normalization_probe_case(
            root,
            f"failure_subclass_{profile}",
            ["ordered_entry"],
            _forge_fixture(nested_failure=failure_probe),
            "TYPE_COERCION",
            (failure_probe,),
        ))
    valid_probe_row = {"code": "SOURCE_SHA256", "detail": "probe", "phase": "nested"}
    for ancestry in ("list", "tuple"):
        for profile in (
            "toctou_bogus",
            "second_runtime",
            "immediate_raising",
            "sys_modules_mutation",
        ):
            probe = _sequence_probe(ancestry, profile, valid_probe_row)
            full_falsifier_cells.append(_full_normalization_probe_case(
                root,
                f"diagnostic_{ancestry}_subclass_{profile}",
                ["latest_entry"],
                _forge_fixture(nested_failure=_forge_failure(diagnostics=probe)),
                "TYPE_COERCION",
                (probe,),
            ))
    for profile in (
        "toctou_bogus",
        "second_runtime",
        "immediate_raising",
        "sys_modules_mutation",
        "attribute_mutation",
    ):
        probe = _row_probe(profile)
        full_falsifier_cells.append(_full_normalization_probe_case(
            root,
            f"diagnostic_row_subclass_{profile}",
            ["ordered_entry"],
            _forge_fixture(nested_failure=_forge_failure(diagnostics=[probe])),
            "TYPE_COERCION",
            (probe,),
        ))
    full_falsifier_cells.append(_full_normalization_probe_case(
        root,
        "exact_fixture_missing_fixture_id",
        ["latest_entry"],
        _forge_fixture(omit="fixture_id"),
        "TYPE_COERCION",
    ))

    malformed_strategy_cells = []
    malformed_strategies = (
        ("null", None),
        ("string", "latest_entry"),
        ("mapping", {"strategy": "latest_entry"}),
        ("integer_member", [7]),
        ("unknown_member", ["bogus"]),
        ("empty", []),
    )
    for fixture_id, malformed in malformed_strategies:
        outcome = _raw_public_case(root, malformed)
        if (
            outcome["winner"] != "ECOMP_LATEST_ONLY"
            or outcome["raw_exception"]
            or outcome["final_adjudicator_calls"] != 1
        ):
            raise ResolutionFailure("OUTPUT_MISMATCH", f"malformed strategy cell failed: {fixture_id}")
        malformed_strategy_cells.append({"fixture_id": fixture_id, **outcome})

    malformed_fault_fixture_cells = []
    for fixture_id, malformed in _malformed_fault_fixtures():
        for strategy in ("latest_entry", "ordered_entry"):
            outcome = _raw_public_case(root, [strategy], fixture=malformed)
            if (
                outcome["winner"] != "TYPE_COERCION"
                or outcome["raw_exception"]
                or outcome["final_adjudicator_calls"] != 1
            ):
                raise ResolutionFailure(
                    "OUTPUT_MISMATCH",
                    f"malformed fault fixture cell failed: {fixture_id}/{strategy}",
                )
            malformed_fault_fixture_cells.append({"fixture_id": fixture_id, "strategy": strategy, **outcome})

    inference_semantic_fixtures = _inference_semantic_fixtures(root)

    custody_cells = []
    for case in CUSTODY_CASES:
        view, fixture = _mutate_custody_sources(root, case)
        expected = "CUSTODY_ABSENT" if case in CUSTODY_ABSENT_CASES else "CUSTODY_DISAGREEMENT"
        for strategy in ("latest_entry", "ordered_entry"):
            outcome = _public_case(root, strategy, view=view, fixture=fixture)
            if outcome["winner"] != expected or outcome["final_adjudicator_calls"] != 1:
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
                "final_adjudicator_calls": outcome["final_adjudicator_calls"],
            })

    corrupted_v11_resolver = bytearray(repository_path(root, V11_RESOLVER).read_bytes())
    corrupted_v11_resolver[-2] ^= 1
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
        view = ReadView({V11_RESOLVER: bytes(corrupted_v11_resolver)})
        for strategy in ("latest_entry", "ordered_entry"):
            outcome = _public_case(root, strategy, view=view, fixture=fixture)
            codes = [row["code"] for row in outcome["diagnostics"]]
            if (
                outcome["winner"] != "SOURCE_SHA256"
                or "OUTPUT_MISMATCH" not in codes
                or outcome["final_adjudicator_calls"] != 1
            ):
                raise ResolutionFailure("OUTPUT_MISMATCH", f"temporal collision failed: {fixture.fixture_id}/{strategy}")
            temporal_cells.append({
                "fixture_id": fixture.fixture_id,
                "strategy": strategy,
                "expected": "SOURCE_SHA256",
                "observed": outcome["winner"],
                "diagnostics": outcome["diagnostics"],
                "raw_exception": outcome["raw_exception"],
                "final_adjudicator_calls": outcome["final_adjudicator_calls"],
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
            if (
                outcome["winner"] != expected
                or not required_codes.issubset(codes)
                or outcome["final_adjudicator_calls"] != 1
            ):
                raise ResolutionFailure("OUTPUT_MISMATCH", f"inherited collision failed: {case}/{strategy}")
            inherited_cells.append({
                "fixture_id": case,
                "strategy": strategy,
                "expected": expected,
                "observed": outcome["winner"],
                "diagnostics": outcome["diagnostics"],
                "final_adjudicator_calls": outcome["final_adjudicator_calls"],
            })

    priority_view = ReadView({DEFAULT_INPUT: canonical_bytes(_mutate_actual_input(input_object, "priority_table_drift"))})
    priority_cells = []
    for strategy in ("latest_entry", "ordered_entry"):
        outcome = _public_case(root, strategy, view=priority_view)
        if outcome["winner"] != "UNRESOLVED_CONTRADICTION" or outcome["final_adjudicator_calls"] != 1:
            raise ResolutionFailure("OUTPUT_MISMATCH", f"priority-table drift failed: {strategy}")
        priority_cells.append({
            "strategy": strategy,
            "expected": "UNRESOLVED_CONTRADICTION",
            "observed": outcome["winner"],
            "diagnostics": outcome["diagnostics"],
            "final_adjudicator_calls": outcome["final_adjudicator_calls"],
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
        "positive_public_resolve_sys_modules_delta": [],
        "positive_public_resolve_repository_delta": False,
        "positive_public_resolve_repository_path_delta": False,
        "positive_public_resolve_cache_or_bytecode_delta": False,
        "public_snapshot_normalization": {
            "strategy_cell_count": public_contract["strategy_cell_count"],
            "fixture_failure_diagnostic_composition_cell_count": public_contract[
                "fixture_failure_diagnostic_composition_cell_count"
            ],
            "merge_containment_cell_count": public_contract["merge_containment_cell_count"],
            "composition_cell_count": public_contract["composition_cell_count"],
            "total_cell_count": public_contract["total_cell_count"],
            "matrix_sha256": sha256(canonical_bytes(public_contract)),
            "all_expected_equal_observed": True,
            "all_raw_exception_false": True,
            "all_final_adjudicator_calls_one": True,
            "all_rejected_subclass_hook_calls_zero": True,
            "all_rejected_subclass_traversal_calls_zero": True,
            "all_sys_modules_delta_empty": True,
            "all_strategy_snapshots_detached": True,
            "all_fixture_snapshots_detached": True,
            "all_nested_failure_snapshots_detached": True,
        },
        "v12_origin_field_rows": {
            "count": len(expected_v12_origin_rows),
            "sha256": v12_origin_rows_sha256,
            "unique_resolved_field_paths": True,
            "all_expected_equal_observed": True,
        },
        "full_public_v11_falsifier_cells": full_falsifier_cells,
        "full_public_v11_falsifier_cell_count": len(full_falsifier_cells),
        "inference_semantic_fixtures": inference_semantic_fixtures,
        "malformed_strategy_cells": malformed_strategy_cells,
        "malformed_strategy_cell_count": len(malformed_strategy_cells),
        "malformed_fault_fixture_cells": malformed_fault_fixture_cells,
        "malformed_fault_fixture_cell_count": len(malformed_fault_fixture_cells),
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
        "source_fields_sha256": V11_SOURCE_FIELDS_SHA256,
        "origin_row_count": 1363,
        "origin_rows_sha256": V11_ORIGIN_ROWS_SHA256,
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
    parser.add_argument("--materialize", action="store_true", help="write only the three declared generated v12 JSON artifacts")
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
