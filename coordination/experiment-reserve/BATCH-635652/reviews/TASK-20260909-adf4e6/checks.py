#!/usr/bin/env python3
"""Independent fixed-source checks for TASK-20260909-adf4e6.

This checker exercises the snapshotted TASK-20260909-d31be5 helpers on fixed
synthetic groups and validates their source/custody graph.  It never constructs
an elliptic-curve fixture, calls the rho solver, or enters the experiment
runner.  Each invocation writes one exclusive receipt and launches one worker.
"""
from __future__ import annotations

import argparse
import ast
from array import array
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import importlib
import inspect
import json
from math import isqrt
import os
from pathlib import Path
import platform
import resource
import signal
import subprocess
import sys
import tempfile
import time
from typing import Any, Callable

import yaml


TASK_ID = "TASK-20260909-adf4e6"
EXPERIMENT_ID = "EXP-ECDLP-709063"
REPO = Path(__file__).resolve().parents[5]
SOURCE = REPO / "experiments/EXP-ECDLP-709063/implementation/TASK-20260909-d31be5"
HANDOFF = REPO / "ledger/handoffs/TASK-20260909-adf4e6.yaml"
PLAN = REPO / "coordination/experiment-reserve/BATCH-635652/review-plan-TASK-20260909-adf4e6.yaml"
SOURCE_SNAPSHOT = "1c9b23b662dbe890c5b6e40a5a05979e15e079d0"
AUTHORITY_COMMIT = "758abfa92b4c3a37800fa5ce28e37f9df784c74c"
CLAIM_COMMIT = "b20284d778917d619b175e1cc15139587fa79ae2"
LIMIT_SECONDS = 10
AGGREGATE_LIMIT_SECONDS = 1800
MEMORY_LIMIT_BYTES = 2 * 1024**3

if str(SOURCE) not in sys.path:
    sys.path.insert(0, str(SOURCE))

table = importlib.import_module("table")
bsgs = importlib.import_module("bsgs")


class CheckFailure(AssertionError):
    pass


class CaseTimeout(TimeoutError):
    pass


class Case:
    def __init__(self, name: str, action: Callable[[], None]) -> None:
        self.name = name
        self.action = action


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def require(condition: bool, detail: str) -> None:
    if not condition:
        raise CheckFailure(detail)


def raises(exc: type[BaseException], action: Callable[[], object]) -> None:
    try:
        action()
    except exc:
        return
    except BaseException as caught:
        raise CheckFailure(f"expected {exc.__name__}, got {type(caught).__name__}: {caught}") from caught
    raise CheckFailure(f"expected {exc.__name__}")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args], cwd=REPO, text=True, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, check=check,
    )


class BytesTrap:
    def __init__(self, payload: bytes) -> None:
        self.payload = payload
        self.calls = 0

    def __bytes__(self) -> bytes:
        self.calls += 1
        return self.payload


class HostileBytes(bytes):
    def __new__(cls, payload: bytes) -> "HostileBytes":
        obj = super().__new__(cls, payload)
        obj.bytes_calls = 0
        obj.len_calls = 0
        return obj

    def __bytes__(self) -> bytes:
        self.bytes_calls += 1
        raise CheckFailure("HostileBytes.__bytes__ executed")

    def __len__(self) -> int:
        self.len_calls += 1
        raise CheckFailure("HostileBytes.__len__ executed")


class HostileBytearray(bytearray):
    def __init__(self, payload: bytes) -> None:
        super().__init__(payload)
        self.bytes_calls = 0
        self.len_calls = 0

    def __bytes__(self) -> bytes:
        self.bytes_calls += 1
        raise CheckFailure("HostileBytearray.__bytes__ executed")

    def __len__(self) -> int:
        self.len_calls += 1
        raise CheckFailure("HostileBytearray.__len__ executed")


class CyclicGroup:
    """Fixed complete cyclic group with an exact log of public operations."""

    def __init__(self, order: int, enc_alias: dict[int, int] | None = None,
                 false_equals: bool = False) -> None:
        self.order = order
        self.enc_alias = dict(enc_alias or {})
        self.false_equals = false_equals
        self.add_calls: list[tuple[int, int]] = []
        self.neg_calls: list[int] = []
        self.encode_calls: list[int] = []
        self.equals_calls: list[tuple[int, int]] = []

    @property
    def oracle_secret(self) -> int:
        raise CheckFailure("forbidden oracle_secret read")

    @property
    def known_scalar(self) -> int:
        raise CheckFailure("forbidden known_scalar read")

    def identity(self) -> int:
        return 0

    def add(self, left: int, right: int) -> int:
        self.add_calls.append((left, right))
        return (left + right) % self.order

    def neg(self, point: int) -> int:
        self.neg_calls.append(point)
        return (-point) % self.order

    def equals(self, left: int, right: int) -> bool:
        self.equals_calls.append((left, right))
        return False if self.false_equals else left == right

    def encode_point(self, point: int) -> table.LogicalPoint:
        self.encode_calls.append(point)
        value = self.enc_alias.get(point, point)
        if value % self.order == 0:
            return table.LogicalPoint.infinity()
        return table.LogicalPoint.affine(value % self.order, 0)


class MissingInterface:
    def add(self, left: int, right: int) -> int:
        return left + right


class ScalarCurve:
    def __init__(self, order: int) -> None:
        self.order = order
        self.calls: list[tuple[int | None, int | None]] = []

    def identity(self) -> None:
        return None

    def add(self, left: int | None, right: int | None) -> int | None:
        self.calls.append((left, right))
        if left is None:
            return right
        if right is None:
            return left
        return (left + right) % self.order

    def neg(self, point: int | None) -> int | None:
        return None if point is None else (-point) % self.order

    def equals(self, left: object, right: object) -> bool:
        return left == right

    def encode_point(self, point: int | None) -> table.LogicalPoint:
        return table.LogicalPoint.infinity() if point is None else table.LogicalPoint.affine(point, 0)


def logical_payload() -> bytes:
    return table.encode_logical_point(table.LogicalPoint.affine(7, 8))


def hash_payload() -> bytes:
    return table.encode_hash_preimage(table.LogicalPoint.affine(7, 8))


def physical_payload() -> bytes:
    return table.encode_physical_slot(table.PhysicalSlot(table.AFFINE, 7, 8, 3))


DECODERS: tuple[tuple[str, Callable[[Any], Any], bytes, Any], ...] = (
    ("logical", table.decode_logical_point, logical_payload(), table.LogicalPoint.affine(7, 8)),
    ("hash", table.decode_hash_preimage, hash_payload(), table.LogicalPoint.affine(7, 8)),
    ("physical", table.decode_physical_slot, physical_payload(), table.PhysicalSlot(table.AFFINE, 7, 8, 3)),
)


def check_counterexample(decoder: Callable[[Any], Any], value: object) -> None:
    raises(table.TableValidationError, lambda: decoder(value))


def check_hostile(decoder: Callable[[Any], Any], payload: bytes, expected: Any,
                  carrier: type[HostileBytes] | type[HostileBytearray]) -> None:
    raw = carrier(payload)
    require(decoder(raw) == expected, "hostile genuine carrier did not preserve buffer bytes")
    require(raw.bytes_calls == 0, "decoder executed overridden __bytes__")
    require(raw.len_calls == 0, "decoder executed overridden __len__")


def check_trap(decoder: Callable[[Any], Any], payload: bytes) -> None:
    raw = BytesTrap(payload)
    raises(table.TableValidationError, lambda: decoder(raw))
    require(raw.calls == 0, "unrelated __bytes__ object was coerced")


def check_released(decoder: Callable[[Any], Any], payload: bytes) -> None:
    raw = memoryview(bytearray(payload))
    raw.release()
    raises(table.TableValidationError, lambda: decoder(raw))


def check_weird_view(label: str, decoder: Callable[[Any], Any], payload: bytes, expected: Any) -> None:
    if label == "physical":
        raw = memoryview(array("I", [int.from_bytes(payload[i:i + 4], sys.byteorder)
                                     for i in range(0, 16, 4)]))
    else:
        raw = memoryview(bytearray(payload)).cast("B", shape=[3, 3])
    require(raw.nbytes == len(payload), "control has wrong byte count")
    require(len(raw) != raw.nbytes, "control failed to distinguish element count and nbytes")
    require(decoder(raw) == expected, "decoder used element count instead of nbytes")


def focus_cases() -> list[Case]:
    cases = [
        Case("decoder-type-1-logical-int9", lambda: check_counterexample(table.decode_logical_point, 9)),
        Case("decoder-type-1-hash-bool", lambda: check_counterexample(table.decode_hash_preimage, True)),
        Case("decoder-type-1-physical-int16", lambda: check_counterexample(table.decode_physical_slot, 16)),
    ]
    for label, decoder, payload, expected in DECODERS:
        cases.append(Case(f"valid-{label}-bytes", lambda d=decoder, p=payload, e=expected: require(d(p) == e, "bytes changed")))
    for label, decoder, payload, expected in DECODERS:
        cases.append(Case(f"hostile-{label}-bytes-subclass", lambda d=decoder, p=payload, e=expected: check_hostile(d, p, e, HostileBytes)))
    for label, decoder, payload, expected in DECODERS:
        cases.append(Case(f"hostile-{label}-bytearray-subclass", lambda d=decoder, p=payload, e=expected: check_hostile(d, p, e, HostileBytearray)))
    for label, decoder, payload, _ in DECODERS:
        cases.append(Case(f"unrelated-{label}-bytes-trap", lambda d=decoder, p=payload: check_trap(d, p)))
    for label, decoder, payload, expected in DECODERS:
        cases.append(Case(f"nbytes-{label}-memoryview", lambda l=label, d=decoder, p=payload, e=expected: check_weird_view(l, d, p, e)))
    for label, decoder, payload, _ in DECODERS:
        cases.append(Case(f"released-{label}-memoryview", lambda d=decoder, p=payload: check_released(d, p)))
    invalids = (("logical", table.decode_logical_point, "x"),
                ("hash", table.decode_hash_preimage, [0]),
                ("physical", table.decode_physical_slot, iter([0] * 16)))
    for label, decoder, value in invalids:
        cases.append(Case(f"unrelated-{label}-carrier", lambda d=decoder, v=value: check_counterexample(d, v)))
    require(len(cases) == 24, f"focus reservation drifted: {len(cases)}")
    return cases


def handoff_doc() -> dict[str, Any]:
    return yaml.safe_load(HANDOFF.read_text(encoding="utf-8"))["handoff"]


def check_all_declared_hashes() -> None:
    handoff = handoff_doc()
    require(len(handoff["inputs"]) == len(handoff["source_bindings"]) == 76, "declared input count changed")
    for binding in handoff["source_bindings"]:
        path = REPO / binding["path"]
        require(path.is_file(), f"missing declared input {binding['path']}")
        require(sha256_path(path) == binding["sha256"], f"binding mismatch {binding['path']}")


def check_all_declared_parse() -> None:
    for relative in handoff_doc()["inputs"]:
        path = REPO / relative
        raw = path.read_bytes()
        require(len(raw) == path.stat().st_size, f"incomplete byte read {relative}")
        text = raw.decode("utf-8")
        if path.suffix == ".json":
            json.loads(text)
        elif path.suffix in {".yaml", ".yml"}:
            yaml.safe_load(text)
        elif path.suffix == ".py":
            if relative == "experiments/EXP-ECDLP-709063/implementation/TASK-20260909-85c2fe/tests.py":
                try:
                    ast.parse(text, filename=str(path))
                except IndentationError:
                    pass
                else:
                    raise CheckFailure("failed predecessor checker unexpectedly parses")
            else:
                ast.parse(text, filename=str(path))


def check_handoff_plan_identity() -> None:
    embedded = handoff_doc()["review_plan"]
    separate = yaml.safe_load(PLAN.read_text(encoding="utf-8"))["review_plan"]
    require(embedded == separate, "separate review plan differs from handoff")
    require(embedded["recorded_before_reviewers"] is True, "plan prior is not pre-recorded")
    require(embedded["source_snapshot"] == SOURCE_SNAPSHOT, "source snapshot changed")


def check_commit_graph() -> None:
    for commit in (SOURCE_SNAPSHOT, AUTHORITY_COMMIT, CLAIM_COMMIT):
        require(git("cat-file", "-t", commit).stdout.strip() == "commit", f"missing commit {commit}")
    require(git("merge-base", "--is-ancestor", SOURCE_SNAPSHOT, AUTHORITY_COMMIT, check=False).returncode == 0,
            "source snapshot is not ancestor of authority")
    require(git("merge-base", "--is-ancestor", AUTHORITY_COMMIT, CLAIM_COMMIT, check=False).returncode == 0,
            "authority is not ancestor of claim")


def check_authority_bytes() -> None:
    for relative in ("ledger/handoffs/TASK-20260909-adf4e6.yaml",
                     "coordination/experiment-reserve/BATCH-635652/review-plan-TASK-20260909-adf4e6.yaml"):
        archived = git("show", f"{AUTHORITY_COMMIT}:{relative}").stdout.encode()
        require(archived == (REPO / relative).read_bytes(), f"authority bytes differ for {relative}")


def snapshot_doc() -> dict[str, Any]:
    path = REPO / "coordination/experiment-reserve/BATCH-635652/archives/TASK-20260909-7f5fe3/snapshot.json"
    return json.loads(path.read_text(encoding="utf-8"))


def check_snapshot_bindings() -> None:
    snapshot = snapshot_doc()
    require(snapshot["source_task_ids"] == ["TASK-20260909-d31be5"], "wrong snapshot source task")
    require(len(snapshot["source_path_sha256"]) == 8, "snapshot must bind eight producer files")
    for relative, expected in snapshot["source_path_sha256"].items():
        require(sha256_path(REPO / relative) == expected, f"live snapshot byte mismatch {relative}")


def check_snapshot_git_bytes() -> None:
    for relative, expected in snapshot_doc()["source_path_sha256"].items():
        archived = git("show", f"{SOURCE_SNAPSHOT}:{relative}").stdout.encode()
        require(sha256_bytes(archived) == expected, f"snapshot commit mismatch {relative}")
        require(archived == (REPO / relative).read_bytes(), f"post-snapshot substitution {relative}")


def producer_receipt() -> dict[str, Any]:
    return json.loads((SOURCE / "check-receipt.json").read_text(encoding="utf-8"))


def producer_cases() -> list[dict[str, Any]]:
    return producer_receipt()["attempts"][0]["inner"]["worker"]["cases"]


def predecessor_cases() -> list[dict[str, Any]]:
    path = REPO / "experiments/EXP-ECDLP-709063/implementation/TASK-20260908-7771f2/check-receipt.json"
    return json.loads(path.read_text(encoding="utf-8"))["attempts"][0]["inner_receipt"]["worker"]["cases"]


def check_producer_cases_unique() -> None:
    cases = producer_cases()
    require(len(cases) == 365, "producer case count is not 365")
    require([row["ordinal"] for row in cases] == list(range(1, 366)), "producer ordinals are not exact")
    require(len({row["name"] for row in cases}) == 365, "producer case names are not unique")
    require(all(row["status"] == "passed" for row in cases), "producer receipt contains a failed case")


def check_first_320_retained() -> None:
    old = predecessor_cases()
    new = producer_cases()[:320]
    require(len(old) == len(new) == 320, "320-case predecessor boundary missing")
    require([x["name"] for x in old] == [x["name"] for x in new], "first 320 case names changed")
    require(all(row["status"] == "passed" for row in new), "retained producer case failed")


def check_decoder_45_retained() -> None:
    names = [row["name"] for row in producer_cases()[320:]]
    require(len(names) == 45, "decoder extension is not 45 cases")
    for required_name in (
        "decoder-counterexample-reject-logical-int-9",
        "decoder-counterexample-reject-hash-bool-true",
        "decoder-counterexample-reject-physical-int-16",
        "decoder-accept-logical-bytes-subclass",
        "decoder-accept-physical-bytearray-subclass",
        "decoder-reject-physical-released-memoryview",
    ):
        require(required_name in names, f"missing producer decoder case {required_name}")


def check_producer_inner_summary() -> None:
    receipt = producer_receipt()
    attempt = receipt["attempts"][0]["inner"]
    worker = attempt["worker"]
    require((attempt["exit_code"], worker["executed_case_count"], worker["passed"], worker["failed"]) ==
            (0, 365, 365, 0), "producer inner terminal summary mismatch")
    require(attempt["case_reservation"]["reserved_before_launch"] is True, "cases not reserved before launch")
    require(attempt["process_handling"]["terminal_observed"] is True, "inner worker terminal not observed")
    require(attempt["actual_telemetry"]["maximum_workers_used"] == 1, "producer exceeded one worker")


def check_producer_outer_custody() -> None:
    receipt = producer_receipt()
    require(len(receipt["attempts"]) == 1, "unexpected producer attempt count")
    attempt = receipt["attempts"][0]
    outer = attempt["outer"]
    require(outer["initial_tool_result"].get("session_id") == 77407, "outer session handle missing")
    require(len(outer["polls"]) == 1 and outer["polls"][0].get("exit_code") == 0, "outer terminal exit missing")
    require("maximum resident set size" in attempt["outer_stderr"], "outer time/RSS log missing")
    require(attempt["outer_stdout"] == "", "unexpected outer stdout")
    require(outer["started_utc"].endswith("UTC") and outer["ended_utc"].endswith("UTC"), "outer UTC missing")


def check_report_receipt_consistency() -> None:
    report = yaml.safe_load((SOURCE / "implementation-report.yaml").read_text(encoding="utf-8"))["execution_report"]
    receipt = producer_receipt()
    require(report["checks"]["receipt_sha256"] == sha256_path(SOURCE / "check-receipt.json"), "report receipt hash mismatch")
    require((report["checks"]["smoke"], report["checks"]["full_suite"], report["checks"]["total"],
             report["checks"]["passed"], report["checks"]["failed"]) == (6, 365, 371, 371, 0),
            "report count mismatch")
    require(receipt["accounting"] == {"total_fixed_cases": 371, "passed": 371, "failed": 0,
                                      "complete_suites": 1, "maximum_cases": 800, "remaining_cases": 429},
            "receipt accounting mismatch")


def check_failed_history_preserved() -> None:
    receipt = producer_receipt()
    custody_path = REPO / "coordination/experiment-reserve/admission-20260907/bsgs-decoder-failed-custody-20260909.json"
    custody = json.loads(custody_path.read_text(encoding="utf-8"))
    require(receipt["predecessor"]["lost_first_per_case_receipt"] == "not reconstructed", "loss was reconstructed")
    require(custody["lost_receipt"]["missing"].startswith("full original per-case"), "custody no longer states loss")
    require(custody["known_case_executions"] == 718, "historical case count changed")


def check_acyclic_receipt_graph() -> None:
    receipt_text = (SOURCE / "check-receipt.json").read_text(encoding="utf-8")
    report_text = (SOURCE / "implementation-report.yaml").read_text(encoding="utf-8")
    require(sha256_path(SOURCE / "check-receipt.json") in report_text, "report does not bind receipt")
    require(sha256_path(SOURCE / "implementation-report.yaml") not in receipt_text, "receipt/report hash cycle")
    require(producer_receipt()["receipt_self_hash"] is None, "receipt asserts self hash")


def check_original_kernel_preservation() -> None:
    old = REPO / "experiments/EXP-ECDLP-709063/implementation/TASK-20260908-7771f2"
    for name in ("bsgs.py", "rho-corrected.py"):
        require((old / name).read_bytes() == (SOURCE / name).read_bytes(), f"{name} changed")


def check_decoder_diff_scope() -> None:
    old = REPO / "experiments/EXP-ECDLP-709063/implementation/TASK-20260908-7771f2/table.py"
    old_tree = ast.parse(old.read_text(encoding="utf-8"))
    new_tree = ast.parse((SOURCE / "table.py").read_text(encoding="utf-8"))
    old_functions = {n.name: ast.dump(n, include_attributes=False) for n in old_tree.body if isinstance(n, ast.FunctionDef)}
    new_functions = {n.name: ast.dump(n, include_attributes=False) for n in new_tree.body if isinstance(n, ast.FunctionDef)}
    changed = {name for name in set(old_functions) | set(new_functions) if old_functions.get(name) != new_functions.get(name)}
    require(changed == {"_decoder_bytes", "decode_logical_point", "decode_hash_preimage", "decode_physical_slot"},
            f"unexpected table function changes: {sorted(changed)}")


def check_binding_file_consistency() -> None:
    """The successor binding must not retain contradictory current-task facts."""
    binding = json.loads((SOURCE / "solver-source-bindings.json").read_text(encoding="utf-8"))
    actual = {name: sha256_path(SOURCE / name) for name in ("table.py", "bsgs.py", "rho-corrected.py", "tests.py")}
    problems: list[str] = []
    if binding["task_source_sha256"] != actual:
        problems.append("task_source_sha256 does not bind successor")
    if binding["current_task_source_sha256"] != actual:
        problems.append("current_task_source_sha256 retains failed-predecessor table/tests hashes")
    producer_handoff = yaml.safe_load((REPO / "ledger/handoffs/TASK-20260909-d31be5.yaml").read_text(encoding="utf-8"))["handoff"]
    if binding["source_binding_preflight"]["handoff_declared_input_count"] != len(producer_handoff["inputs"]):
        problems.append("source_binding_preflight says 49 inputs but successor handoff has 62")
    if "no full suite may be run against the exact final package" in binding["validation_limitation"]:
        problems.append("validation_limitation retains superseded untested-final-source claim")
    require(not problems, "; ".join(problems))


def check_output_scope_before_finalization() -> None:
    directory = Path(__file__).resolve().parent
    names = sorted(path.name for path in directory.iterdir() if path.is_file())
    require(names == ["checks.py"], f"unexpected pre-final review outputs: {names}")


def check_valid_carrier_matrix() -> None:
    for _, decoder, payload, expected in DECODERS:
        for raw in (payload, bytearray(payload), memoryview(payload)):
            require(decoder(raw) == expected, "valid carrier changed")


def check_invalid_carrier_matrix() -> None:
    for _, decoder, payload, _ in DECODERS:
        for raw in (len(payload), True, "x", [0], iter([0]), object()):
            raises(table.TableValidationError, lambda d=decoder, value=raw: d(value))


def check_golden_logical() -> None:
    values = [table.LogicalPoint.infinity(), table.LogicalPoint.affine(0, 0),
              table.LogicalPoint.affine(7, 8), table.LogicalPoint.affine((1 << 28) - 1, 1)]
    expected = [b"\x00" + b"\x00" * 8, b"\x01" + b"\x00" * 8,
                b"\x01\x07\x00\x00\x00\x08\x00\x00\x00",
                b"\x01\xff\xff\xff\x0f\x01\x00\x00\x00"]
    for point, raw in zip(values, expected, strict=True):
        require(table.encode_logical_point(point) == raw, "logical golden bytes mismatch")
        require(table.decode_logical_point(raw) == point, "logical golden roundtrip mismatch")


def check_golden_hash() -> None:
    values = [table.LogicalPoint.infinity(), table.LogicalPoint.affine(0, 0), table.LogicalPoint.affine(7, 8)]
    expected = [b"\x00", b"\x04" + b"\x00" * 8, b"\x04\x00\x00\x00\x07\x00\x00\x00\x08"]
    for point, raw in zip(values, expected, strict=True):
        require(table.encode_hash_preimage(point) == raw, "hash golden bytes mismatch")
        require(table.decode_hash_preimage(raw) == point, "hash golden roundtrip mismatch")


def check_golden_physical() -> None:
    records = [table.PhysicalSlot.empty(), table.PhysicalSlot(table.INFINITY, 0, 0, 7),
               table.PhysicalSlot(table.AFFINE, 7, 8, 3)]
    expected = [b"\x00" * 16,
                b"\x00" * 8 + b"\x07\x00\x00\x00\x02\x00\x00\x00",
                b"\x07\x00\x00\x00\x08\x00\x00\x00\x03\x00\x00\x00\x01\x00\x00\x00"]
    for record, raw in zip(records, expected, strict=True):
        require(table.encode_physical_slot(record) == raw, "physical golden bytes mismatch")
        require(table.decode_physical_slot(raw) == record, "physical golden roundtrip mismatch")


def check_o_empty_distinct() -> None:
    logical_o = table.LogicalPoint.infinity()
    physical_o = table.PhysicalSlot.from_logical(logical_o, 0)
    empty = table.PhysicalSlot.empty()
    require(physical_o.state == table.INFINITY and empty.state == table.EMPTY, "O and empty alias")
    require(table.encode_physical_slot(physical_o) != table.encode_physical_slot(empty), "O bytes equal empty")
    raises(table.TableValidationError, empty.logical_point)


def check_invalid_logical_matrix() -> None:
    for args in ((2, 0, 0), (0, 1, 0), (0, 0, 1), (True, 0, 0), (1, 1 << 28, 0), (1, 0, -1)):
        raises(table.TableValidationError, lambda a=args: table.LogicalPoint(*a))


def check_invalid_physical_matrix() -> None:
    for args in ((3, 0, 0, 0), (0, 1, 0, 0), (2, 1, 0, 0), (True, 0, 0, 0),
                 (1, 1 << 28, 0, 0), (1, 0, -1, 0), (1, 0, 0, 1 << 28)):
        raises(table.TableValidationError, lambda a=args: table.PhysicalSlot(*a))


def check_invalid_hash_matrix() -> None:
    for raw in (b"", b"\x01", b"\x00" * 9, b"\x04" + b"\x00" * 7, b"\x05" + b"\x00" * 8):
        raises(table.TableValidationError, lambda value=raw: table.decode_hash_preimage(value))


def check_wrong_lengths() -> None:
    for decoder, lengths in ((table.decode_logical_point, (0, 8, 10)),
                             (table.decode_physical_slot, (0, 15, 17)),
                             (table.decode_hash_preimage, (0, 2, 8, 10))):
        for length in lengths:
            raises(table.TableValidationError, lambda d=decoder, n=length: d(bytearray(n)))


def check_bool_fields() -> None:
    raises(table.TableValidationError, lambda: table.LogicalPoint(table.AFFINE, True, 0))
    raises(table.TableValidationError, lambda: table.PhysicalSlot(table.AFFINE, 0, 0, False))


def check_uint28_boundary() -> None:
    require(table.LogicalPoint.affine((1 << 28) - 1, (1 << 28) - 1).x == (1 << 28) - 1, "uint28 max refused")
    raises(table.TableValidationError, lambda: table.LogicalPoint.affine(1 << 28, 0))


def check_nbytes_rule() -> None:
    for label, decoder, payload, expected in DECODERS:
        check_weird_view(label, decoder, payload, expected)


def check_noncontiguous_view() -> None:
    payload = logical_payload()
    interleaved = bytearray(18)
    interleaved[::2] = payload
    raw = memoryview(interleaved)[::2]
    require(raw.nbytes == 9 and table.decode_logical_point(raw) == table.LogicalPoint.affine(7, 8),
            "noncontiguous declared memoryview changed")


def check_mutable_carrier_snapshot() -> None:
    raw = bytearray(logical_payload())
    decoded = table.decode_logical_point(raw)
    raw[:] = b"\x00" * 9
    require(decoded == table.LogicalPoint.affine(7, 8), "decoder retained mutable alias")


def buffer_for_budget(budget: int) -> bytearray:
    return bytearray(16 * (budget // 16))


def fixed_point(index: int) -> table.LogicalPoint:
    return table.LogicalPoint.affine(index + 1, (3 * index + 7) % (1 << 28))


def check_capacity_matrix() -> None:
    for budget, slots, capacity in ((8, 0, 0), (4096, 256, 179),
                                    (32768, 2048, 1433), (262144, 16384, 11468)):
        obj = table.FixedPhysicalTable(budget, buffer_for_budget(budget))
        require((obj.slots, obj.capacity, obj.buffer_length) == (slots, capacity, 16 * slots), "capacity mismatch")


def check_budget_slack_matrix() -> None:
    for budget in (0, 1, 7, 8, 15, 16, 17, 31, 4097):
        obj = table.FixedPhysicalTable(budget, buffer_for_budget(budget))
        require(obj.slots == budget // 16 and obj.buffer_length == 16 * (budget // 16), "slack mismatch")


def check_zero_insert() -> None:
    raw = bytearray()
    obj = table.FixedPhysicalTable(8, raw)
    before = bytes(raw)
    result = obj.insert(table.LogicalPoint.infinity(), 0)
    require(result.status == "TABLE_FULL" and bytes(raw) == before and obj.occupied == 0, "zero insert mutated")


def check_zero_lookup() -> None:
    obj = table.FixedPhysicalTable(8, bytearray())
    result = obj.lookup(table.LogicalPoint.infinity())
    require(result.status == "NOT_FOUND" and result.counters.hash_calls == 0 and result.counters.probes == 0,
            "zero lookup touched table")


def check_table_constructor_types() -> None:
    raises(table.TableValidationError, lambda: table.FixedPhysicalTable(True, bytearray()))
    raises(table.TableValidationError, lambda: table.FixedPhysicalTable(16, HostileBytearray(b"\x00" * 16)))
    raises(table.TableValidationError, lambda: table.FixedPhysicalTable(16, b"\x00" * 16))


def check_nonzero_buffer_rejected() -> None:
    raw = bytearray(16); raw[0] = 1
    raises(table.TableValidationError, lambda: table.FixedPhysicalTable(16, raw))


def check_wrong_buffer_length() -> None:
    raises(table.TableValidationError, lambda: table.FixedPhysicalTable(17, bytearray(17)))
    raises(table.TableValidationError, lambda: table.FixedPhysicalTable(31, bytearray(16 * 2)))


def check_offset_bounds() -> None:
    obj = table.FixedPhysicalTable(64, bytearray(64))
    for value in (-1, 4, True):
        raises(table.TableValidationError, lambda v=value: obj._offset(v))
    require(obj._offset(3) == 48, "last offset wrong")


def check_single_insert_lookup() -> None:
    obj = table.FixedPhysicalTable(64, bytearray(64))
    point = fixed_point(1)
    inserted = obj.insert(point, 7)
    found = obj.lookup(point)
    require(inserted.status == "INSERTED" and found.status == "FOUND" and found.exponent == 7, "insert/lookup failed")


def check_e_plus_one(budget: int, capacity: int) -> None:
    raw = buffer_for_budget(budget)
    obj = table.FixedPhysicalTable(budget, raw)
    for index in range(capacity):
        require(obj.insert(fixed_point(index), index).status == "INSERTED", f"insert {index} failed")
    before = (id(raw), len(raw), bytes(raw), obj.buffer_sha256(), asdict(obj.counters()))
    refused = obj.insert(fixed_point(capacity), capacity)
    after = (id(raw), len(raw), bytes(raw), obj.buffer_sha256(), asdict(obj.counters()))
    require(refused.status == "TABLE_FULL" and refused.refusal and refused.refusal["unchanged"], "E+1 did not refuse")
    require(before[:4] == after[:4], "E+1 changed buffer")
    require(after[4]["hash_calls"] == before[4]["hash_calls"], "TABLE_FULL did not take priority")
    for index in range(capacity):
        found = obj.lookup(fixed_point(index))
        require(found.status == "FOUND" and found.exponent == index, f"retained lookup {index} failed")


def check_duplicate_same() -> None:
    obj = table.FixedPhysicalTable(80, bytearray(80)); point = fixed_point(2)
    require(obj.insert(point, 4).status == "INSERTED", "initial insert failed")
    before = obj.buffer_sha256()
    result = obj.insert(point, 4)
    require(result.status == "DUPLICATE" and obj.buffer_sha256() == before and obj.occupied == 1, "duplicate changed table")


def check_duplicate_conflict() -> None:
    obj = table.FixedPhysicalTable(80, bytearray(80)); point = fixed_point(2)
    obj.insert(point, 4); before = obj.buffer_sha256()
    result = obj.insert(point, 5)
    require(result.status == "COMPLETED_INVALID" and obj.buffer_sha256() == before, "conflict not rejected")


def check_full_priority_duplicate() -> None:
    obj = table.FixedPhysicalTable(80, bytearray(80))  # S=5,E=3
    for index in range(3): obj.insert(fixed_point(index), index)
    before_hashes = obj.counters().hash_calls
    result = obj.insert(fixed_point(0), 0)
    require(result.status == "TABLE_FULL" and obj.counters().hash_calls == before_hashes, "full priority changed")


def independent_slot(point: table.LogicalPoint, slots: int) -> int:
    preimage = b"\x00" if point.is_infinity else b"\x04" + point.x.to_bytes(4, "big") + point.y.to_bytes(4, "big")
    digest = hashlib.sha256(b"EXP-ECDLP-709063|table|v2" + preimage).digest()
    return int.from_bytes(digest[:8], "little") % slots


def collision_pair(slots: int) -> tuple[table.LogicalPoint, table.LogicalPoint]:
    seen: dict[int, table.LogicalPoint] = {}
    for index in range(1000):
        point = fixed_point(index)
        slot = independent_slot(point, slots)
        if slot in seen:
            return seen[slot], point
        seen[slot] = point
    raise CheckFailure("fixed collision search exhausted")


def check_forced_collision() -> None:
    first, second = collision_pair(7)
    obj = table.FixedPhysicalTable(112, bytearray(112))
    a = obj.insert(first, 1); b = obj.insert(second, 2)
    require(a.status == b.status == "INSERTED", "collision insertion failed")
    require(b.counters.probes >= 3, "linear collision did not probe")
    require(obj.lookup(first).exponent == 1 and obj.lookup(second).exponent == 2, "collision lookup lost key")


def check_absent_stops_at_empty() -> None:
    obj = table.FixedPhysicalTable(112, bytearray(112)); obj.insert(fixed_point(1), 1)
    before = obj.counters()
    result = obj.lookup(fixed_point(999))
    after = obj.counters()
    require(result.status == "NOT_FOUND" and after.probes > before.probes, "absent lookup failed")
    require(after.bytes_written == before.bytes_written, "lookup wrote bytes")


def check_table_counters() -> None:
    obj = table.FixedPhysicalTable(64, bytearray(64)); point = table.LogicalPoint.infinity()
    inserted = obj.insert(point, 0)
    require(inserted.counters.hash_calls == 1 and inserted.counters.hash_preimage_bytes == 1, "O hash charge wrong")
    require(inserted.counters.bytes_written == 16 and inserted.counters.bytes_read == 16, "slot I/O charge wrong")
    found = obj.lookup(point)
    require(found.counters.table_operations == 2 and found.counters.hash_calls == 2, "operation charge wrong")


def check_buffer_alias_and_resize() -> None:
    raw = bytearray(64); obj = table.FixedPhysicalTable(64, raw)
    require(obj.buffer_identity == id(raw) and obj._buffer.obj is raw, "caller buffer alias lost")
    raises(BufferError, lambda: raw.extend(b"\x00"))


def check_reserved_external_mutation() -> None:
    raw = bytearray(64); obj = table.FixedPhysicalTable(64, raw); obj.insert(fixed_point(0), 0)
    raw[12:16] = (3).to_bytes(4, "little")
    raises(table.TableValidationError, lambda: obj.lookup(fixed_point(0)))


def check_zero_external_mutation_boundary() -> None:
    raw = bytearray(64); obj = table.FixedPhysicalTable(64, raw); point = fixed_point(0)
    inserted = obj.insert(point, 0); offset = 16 * int(inserted.slot)
    raw[offset:offset + 16] = b"\x00" * 16
    result = obj.lookup(point)
    require(obj.occupied == 1 and result.status == "NOT_FOUND", "external-mutation boundary changed")


def check_table_fields() -> None:
    obj = table.FixedPhysicalTable(64, bytearray(64))
    expected = {"_budget_bytes", "_slots", "_buffer", "_buffer_identity", "_capacity", "_occupied",
                "_table_operations", "_hash_calls", "_hash_preimage_bytes", "_probes", "_bytes_read", "_bytes_written"}
    require(set(vars(obj)) == expected, f"unexpected table fields: {set(vars(obj)) - expected}")
    require(not any(isinstance(value, (dict, list, set, tuple)) for value in vars(obj).values()), "hidden index/container")


def check_independent_hash_slots() -> None:
    obj = table.FixedPhysicalTable(112, bytearray(112))
    for point in (table.LogicalPoint.infinity(), fixed_point(0), fixed_point(3), fixed_point(17)):
        require(obj._hash_slot(point, None) == independent_slot(point, 7), "table hash differs from frozen formula")


def check_probe_wraparound() -> None:
    points = [fixed_point(index) for index in range(200) if independent_slot(fixed_point(index), 7) == 6]
    require(len(points) >= 2, "wraparound collision fixture missing")
    obj = table.FixedPhysicalTable(112, bytearray(112))
    first = obj.insert(points[0], 1); second = obj.insert(points[1], 2)
    require(first.slot == 6 and second.slot == 0, "linear probe did not wrap from final slot")
    require(obj.lookup(points[1]).exponent == 2, "wrapped key not retained")


def scalar_trace(scalar: int, point: int, order: int) -> tuple[int, list[tuple[int, int]]]:
    if scalar == 0:
        return 0, []
    result = point
    calls: list[tuple[int, int]] = []
    for digit in bin(scalar)[3:]:
        calls.append((result, result)); result = (result + result) % order
        if digit == "1":
            calls.append((result, point)); result = (result + point) % order
    return result, calls


def check_scalar_cost_matrix() -> None:
    for scalar in (0, 1, 2, 3, 4, 5, 7, 8, 13, 31, 32, 63, 64):
        expected = 0 if scalar == 0 else scalar.bit_length() - 1 + scalar.bit_count() - 1
        require(bsgs.scalar_cost(scalar) == expected, f"scalar cost {scalar} wrong")


def check_scalar_trace_matrix() -> None:
    for scalar in (1, 2, 3, 5, 13, 31):
        curve = CyclicGroup(101); group = bsgs.CountingGroup(curve)
        expected_value, expected_calls = scalar_trace(scalar, 1, 101)
        actual = bsgs.left_to_right_scalar(group, scalar, 1, "certificate")
        require(actual == expected_value and curve.add_calls == expected_calls, f"scalar trace {scalar} wrong")
        require(group.certificate == len(expected_calls) == group.total_group_operations, "scalar charge mismatch")


def check_scalar_zero() -> None:
    curve = CyclicGroup(11); group = bsgs.CountingGroup(curve)
    require(bsgs.left_to_right_scalar(group, 0, 1, "certificate") == 0 and not curve.add_calls, "zero scalar called add")


def check_scalar_invalid() -> None:
    curve = CyclicGroup(11); group = bsgs.CountingGroup(curve)
    raises(bsgs.SolverInputError, lambda: bsgs.left_to_right_scalar(group, -1, 1, "certificate"))
    raises(bsgs.SolverInputError, lambda: bsgs.left_to_right_scalar(group, True, 1, "certificate"))
    require(not curve.add_calls, "invalid scalar called add")


def check_counting_add() -> None:
    curve = CyclicGroup(11); group = bsgs.CountingGroup(curve)
    require(group.add(0, 1, "baby") == 1, "O addition wrong")
    require(group.add(1, 1, "scalar_precompute") == 2, "doubling wrong")
    snap = group.snapshot()
    require((snap.total_group_operations, snap.group_additions, snap.group_doublings, snap.baby,
             snap.scalar_precompute) == (2, 2, 1, 1, 1), "counting wrapper mismatch")


def check_group_interface() -> None:
    raises(bsgs.SolverInputError, lambda: bsgs.CountingGroup(MissingInterface()))


def check_invalid_order(value: object, solver: str) -> None:
    curve = CyclicGroup(11)
    if solver == "unbounded":
        raises(bsgs.SolverInputError, lambda: bsgs.solve_unbounded(curve, 1, 1, value, bytearray()))
    elif solver == "arm_a":
        raises(bsgs.SolverInputError, lambda: bsgs.solve_arm_a(curve, 1, 1, value, 8, bytearray()))
    else:
        raises(bsgs.SolverInputError, lambda: bsgs.solve_arm_b(curve, 1, 1, value, 8, bytearray()))
    require(not curve.add_calls, "invalid order performed group work")


def check_unbounded_buffer_length() -> None:
    raises(table.TableValidationError, lambda: bsgs.solve_unbounded(CyclicGroup(11), 1, 7, 11, bytearray(16)))


def check_arm_a_nonzero_buffer() -> None:
    raw = bytearray(80); raw[0] = 1
    raises(table.TableValidationError, lambda: bsgs.solve_arm_a(CyclicGroup(5), 1, 4, 5, 80, raw))


def check_arm_b_full_occupancy() -> None:
    result = bsgs.solve_arm_b(CyclicGroup(5), 1, 4, 5, 128, bytearray(128))
    require(result.m == 5 and result.occupied == 5 and result.table.occupied == 5, "ArmB did not retain exactly M babies")


def expected_solver_trace(order: int, target: int, m: int) -> tuple[list[tuple[int, int]], list[int], dict[str, int]]:
    calls: list[tuple[int, int]] = []
    baby = 0
    for _ in range(m - 1):
        calls.append((baby, 1)); baby = (baby + 1) % order
    h, pre = scalar_trace(m, 1, order); calls.extend(pre)
    ell = target // m
    negs: list[int] = []
    giant = target
    for _ in range(ell):
        negs.append(h); neg_h = (-h) % order
        calls.append((giant, neg_h)); giant = (giant + neg_h) % order
    _, cert = scalar_trace(target, 1, order); calls.extend(cert)
    counts = {"baby": m - 1, "scalar_precompute": len(pre), "giant": ell, "certificate": len(cert)}
    return calls, negs, counts


def unbounded_buffer(order: int) -> bytearray:
    m = isqrt(order - 1) + 1
    slots = (10 * m + 6) // 7
    return bytearray(16 * slots)


def check_solver_result(result: Any, curve: CyclicGroup, order: int, target: int, m: int) -> None:
    expected_calls, expected_negs, counts = expected_solver_trace(order, target, m)
    require(result.termination == "SOLVED" and result.solution == target, "solver returned wrong candidate")
    require(curve.add_calls == expected_calls, "actual group call trace differs from independent trace")
    require(curve.neg_calls == expected_negs, "negation trace differs")
    ops = result.operations
    require((ops.baby, ops.scalar_precompute, ops.giant, ops.certificate) ==
            (counts["baby"], counts["scalar_precompute"], counts["giant"], counts["certificate"]),
            "component charge mismatch")
    require(ops.total_group_operations == len(expected_calls) == ops.group_additions, "total charge mismatch")
    require(ops.negations == len(expected_negs), "negation charge mismatch")
    require(ops.group_doublings == sum(left == right for left, right in expected_calls), "doubling charge mismatch")


def check_unbounded(order: int, target: int) -> None:
    curve = CyclicGroup(order); result = bsgs.solve_unbounded(curve, 1, target, order, unbounded_buffer(order))
    check_solver_result(result, curve, order, target, isqrt(order - 1) + 1)


def check_arm_a_refusal() -> None:
    curve = CyclicGroup(5); raw = bytearray(64); before = bytes(raw)
    result = bsgs.solve_arm_a(curve, 1, 4, 5, 64, raw)
    require(result.termination == "CAPACITY_REFUSAL" and not curve.add_calls and bytes(raw) == before, "ArmA refusal did work")


def check_arm_a_start() -> None:
    curve = CyclicGroup(5); result = bsgs.solve_arm_a(curve, 1, 4, 5, 80, bytearray(80))
    check_solver_result(result, curve, 5, 4, 3)


def check_arm_b_zero() -> None:
    curve = CyclicGroup(5); result = bsgs.solve_arm_b(curve, 1, 4, 5, 8, bytearray())
    require(result.termination == "CAPACITY_REFUSAL" and result.m == 0 and not curve.add_calls, "ArmB zero capacity worked")


def check_arm_b(order: int, target: int, budget: int) -> None:
    capacity = (7 * (budget // 16)) // 10
    m = min(capacity, order)
    curve = CyclicGroup(order); result = bsgs.solve_arm_b(curve, 1, target, order, budget, buffer_for_budget(budget))
    require(result.m == m, "ArmB M != min(E,N)")
    check_solver_result(result, curve, order, target, m)


def check_bad_certificate() -> None:
    curve = CyclicGroup(11, enc_alias={7: 1})
    result = bsgs.solve_unbounded(curve, 1, 7, 11, unbounded_buffer(11))
    require(result.termination == "COMPLETED_INVALID" and result.solution is None, "false hit was certified")


def check_conflicting_baby() -> None:
    curve = CyclicGroup(11, enc_alias={1: 0})
    result = bsgs.solve_unbounded(curve, 1, 7, 11, unbounded_buffer(11))
    require(result.termination == "COMPLETED_INVALID" and "conflicting baby" in result.reason, "baby alias not rejected")


def cancellation_case(event: str, solver: str) -> None:
    seen: list[tuple[str, dict[str, int]]] = []
    def hook(name: str, counters: dict[str, int]) -> bool:
        seen.append((name, dict(counters)))
        return name != event
    if solver == "table":
        raw = bytearray(64); obj = table.FixedPhysicalTable(64, raw); before = bytes(raw)
        result = obj.insert(fixed_point(0), 0, hook=hook)
        require(result.status == "CANCELLED", f"table did not cancel at {event}")
        require(bytes(raw) == before and obj.occupied == 0, f"table mutated after {event}")
    else:
        order, target = 11, 10
        curve = CyclicGroup(order)
        result = bsgs.solve_unbounded(curve, 1, target, order, unbounded_buffer(order), hook=hook)
        require(result.termination == "CANCELLED", f"solver did not cancel at {event}")
        if event in {"baby", "scalar_precompute", "giant", "certificate"}:
            require(result.operations.total_group_operations == len(curve.add_calls), "cancel partial charge drift")
        if event == "negation":
            require(len(curve.neg_calls) == result.operations.negations, "cancelled negation was charged")
    require(any(name == event for name, _ in seen), f"event {event} never reached")


def rho_span() -> tuple[bytes, bytes, bytes]:
    base = (REPO / "harness/rho.py").read_bytes()
    derivative = (SOURCE / "rho-corrected.py").read_bytes()
    return base, derivative, yaml.safe_load(
        (REPO / "coordination/experiment-reserve/BATCH-635652/corrections/TASK-20260908-92d6dd/EXP-ECDLP-709063.yaml").read_text(encoding="utf-8")
    )["protocol_amendment"]["rho_baseline"]["prospective_scalar_amendment"]["replacement_python"].encode()


def check_rho_hashes() -> None:
    base, derivative, _ = rho_span()
    require(sha256_bytes(base) == "de952371bfa0513b4783e78012f7eddb1098ef2a1fef5bd9adc2b34e2a86bcc0", "base rho hash")
    require(sha256_bytes(derivative) == "0d05b954593d1d6adeb8f0764eb0acda280f938f58cb453f1259fd0e61eaa233", "derivative hash")


def expected_rho_derivative() -> bytes:
    base, _, replacement = rho_span()
    indented = b"".join(b"    " + line if line.strip() else line for line in replacement.splitlines(keepends=True))
    # The frozen replacement ends in LF and the removed base span is followed
    # by two LFs.  Strip the replacement's terminal LF so the source retains
    # exactly one blank line before the unchanged suffix.
    return base[:2044] + indented.rstrip(b"\n") + base[2580:]


def check_rho_splice() -> None:
    _, derivative, _ = rho_span()
    require(derivative == expected_rho_derivative(), "rho derivative is not exact approved scalar splice")


def check_rho_mutation_controls() -> None:
    expected = expected_rho_derivative()
    outside = bytearray(expected); outside[0] ^= 1
    inside = bytearray(expected); inside[2100] ^= 1
    require(bytes(outside) != expected and bytes(inside) != expected, "mutation control did not change bytes")
    require(sha256_bytes(bytes(outside)) != sha256_bytes(expected), "outside mutation passed hash")
    require(sha256_bytes(bytes(inside)) != sha256_bytes(expected), "inside mutation passed hash")


def isolated_rho_scalar(scalar: int) -> tuple[Any, int, list[tuple[Any, Any]]]:
    curve = ScalarCurve(101)
    total_ops = 0
    if scalar < 0:
        raise ValueError("nonnegative scalar required")
    if scalar == 0:
        return None, total_ops, curve.calls
    result: Any = 1
    for digit in bin(scalar)[3:]:
        result = curve.add(result, result); total_ops += 1
        if digit == "1":
            result = curve.add(result, 1); total_ops += 1
    return result, total_ops, curve.calls


def check_rho_scalar_matrix() -> None:
    for scalar in (1, 2, 3, 5, 13, 31):
        value, count, calls = isolated_rho_scalar(scalar)
        expected_value, expected_calls = scalar_trace(scalar, 1, 101)
        require(value == expected_value and calls == expected_calls and count == len(expected_calls), "rho scalar body mismatch")


def check_no_full_rho() -> None:
    tree = ast.parse((SOURCE / "rho-corrected.py").read_text(encoding="utf-8"))
    solve_calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "solve"]
    require(not solve_calls, "rho source invokes solve at import")


def check_public_signatures() -> None:
    for fn in (bsgs.solve_unbounded, bsgs.solve_arm_a, bsgs.solve_arm_b):
        names = list(inspect.signature(fn).parameters)
        require(not {"k", "secret", "oracle", "known_scalar"}.intersection(names), f"secret parameter in {fn.__name__}")
    curve = CyclicGroup(11)
    result = bsgs.solve_unbounded(curve, 1, 7, 11, unbounded_buffer(11))
    require(result.solution == 7, "public-only sentinel solve failed")


def full_cases() -> list[Case]:
    cases: list[Case] = []
    add = lambda name, action: cases.append(Case(name, action))
    # Complete byte/custody graph.
    add("artifact-all-76-hashes", check_all_declared_hashes)
    add("artifact-all-76-complete-parse", check_all_declared_parse)
    add("artifact-handoff-plan-identity", check_handoff_plan_identity)
    add("artifact-commit-graph", check_commit_graph)
    add("artifact-authority-bytes", check_authority_bytes)
    add("artifact-snapshot-bindings", check_snapshot_bindings)
    add("artifact-snapshot-git-bytes", check_snapshot_git_bytes)
    add("artifact-producer-cases-unique", check_producer_cases_unique)
    add("artifact-first-320-retained", check_first_320_retained)
    add("artifact-decoder-45-retained", check_decoder_45_retained)
    add("artifact-producer-inner-summary", check_producer_inner_summary)
    add("artifact-producer-outer-custody", check_producer_outer_custody)
    add("artifact-report-receipt-consistency", check_report_receipt_consistency)
    add("artifact-failed-history-preserved", check_failed_history_preserved)
    add("artifact-acyclic-receipt-graph", check_acyclic_receipt_graph)
    add("artifact-original-kernels-preserved", check_original_kernel_preservation)
    add("artifact-decoder-diff-scope", check_decoder_diff_scope)
    add("artifact-successor-binding-consistency", check_binding_file_consistency)
    add("artifact-output-scope-pre-final", check_output_scope_before_finalization)

    # Decoder carrier boundary and representation domains.
    add("decoder-counterexample-logical-int9", lambda: check_counterexample(table.decode_logical_point, 9))
    add("decoder-counterexample-hash-bool", lambda: check_counterexample(table.decode_hash_preimage, True))
    add("decoder-counterexample-physical-int16", lambda: check_counterexample(table.decode_physical_slot, 16))
    for label, decoder, payload, expected in DECODERS:
        add(f"decoder-hostile-bytes-{label}", lambda d=decoder, p=payload, e=expected: check_hostile(d, p, e, HostileBytes))
    for label, decoder, payload, expected in DECODERS:
        add(f"decoder-hostile-bytearray-{label}", lambda d=decoder, p=payload, e=expected: check_hostile(d, p, e, HostileBytearray))
    for label, decoder, payload, expected in DECODERS:
        add(f"decoder-nbytes-{label}", lambda l=label, d=decoder, p=payload, e=expected: check_weird_view(l, d, p, e))
    for label, decoder, payload, _ in DECODERS:
        add(f"decoder-released-{label}", lambda d=decoder, p=payload: check_released(d, p))
    for label, decoder, payload, _ in DECODERS:
        add(f"decoder-no-unrelated-coercion-{label}", lambda d=decoder, p=payload: check_trap(d, p))
    add("decoder-valid-carrier-matrix", check_valid_carrier_matrix)
    add("decoder-invalid-carrier-matrix", check_invalid_carrier_matrix)
    add("encoding-logical-golden", check_golden_logical)
    add("encoding-hash-golden", check_golden_hash)
    add("encoding-physical-golden", check_golden_physical)
    add("encoding-o-empty-distinct", check_o_empty_distinct)
    add("encoding-invalid-logical", check_invalid_logical_matrix)
    add("encoding-invalid-physical", check_invalid_physical_matrix)
    add("encoding-invalid-hash", check_invalid_hash_matrix)
    add("encoding-wrong-lengths", check_wrong_lengths)
    add("encoding-bool-fields", check_bool_fields)
    add("encoding-uint28-boundary", check_uint28_boundary)
    add("encoding-nbytes-rule", check_nbytes_rule)
    add("encoding-noncontiguous-memoryview", check_noncontiguous_view)
    add("encoding-mutable-carrier-snapshot", check_mutable_carrier_snapshot)

    # Fixed physical table.
    add("table-exact-capacities", check_capacity_matrix)
    add("table-budget-slack", check_budget_slack_matrix)
    add("table-zero-insert", check_zero_insert)
    add("table-zero-lookup", check_zero_lookup)
    add("table-constructor-types", check_table_constructor_types)
    add("table-nonzero-buffer", check_nonzero_buffer_rejected)
    add("table-wrong-buffer-length", check_wrong_buffer_length)
    add("table-offset-bounds", check_offset_bounds)
    add("table-single-insert-lookup", check_single_insert_lookup)
    add("table-e-plus-one-4096", lambda: check_e_plus_one(4096, 179))
    add("table-e-plus-one-32768", lambda: check_e_plus_one(32768, 1433))
    add("table-e-plus-one-262144", lambda: check_e_plus_one(262144, 11468))
    add("table-duplicate-same", check_duplicate_same)
    add("table-duplicate-conflict", check_duplicate_conflict)
    add("table-full-priority", check_full_priority_duplicate)
    add("table-forced-collision", check_forced_collision)
    add("table-absent-stops-empty", check_absent_stops_at_empty)
    add("table-counter-domains", check_table_counters)
    add("table-buffer-alias-resize", check_buffer_alias_and_resize)
    add("table-external-reserved-mutation", check_reserved_external_mutation)
    add("table-external-zero-mutation-boundary", check_zero_external_mutation_boundary)
    add("table-no-hidden-index", check_table_fields)
    add("table-independent-hash-slots", check_independent_hash_slots)
    add("table-probe-wraparound", check_probe_wraparound)

    # Scalar and complete BSGS kernels.
    add("scalar-cost-matrix", check_scalar_cost_matrix)
    add("scalar-trace-matrix", check_scalar_trace_matrix)
    add("scalar-zero", check_scalar_zero)
    add("scalar-negative-and-bool", check_scalar_invalid)
    add("counting-wrapper-add-doubling-o", check_counting_add)
    add("counting-wrapper-interface", check_group_interface)
    add("bsgs-invalid-order-zero", lambda: check_invalid_order(0, "unbounded"))
    add("bsgs-invalid-order-negative", lambda: check_invalid_order(-1, "arm_b"))
    add("bsgs-invalid-order-bool", lambda: check_invalid_order(True, "arm_a"))
    add("bsgs-unbounded-wrong-buffer-length", check_unbounded_buffer_length)
    add("bsgs-arm-a-nonzero-buffer", check_arm_a_nonzero_buffer)
    add("bsgs-arm-b-full-occupancy", check_arm_b_full_occupancy)
    for order, target in ((5, 0), (5, 1), (5, 4), (7, 3), (11, 10), (13, 7),
                          (17, 16), (19, 9), (23, 22), (29, 15), (31, 30), (37, 19)):
        add(f"bsgs-unbounded-{order}-{target}", lambda n=order, k=target: check_unbounded(n, k))
    add("bsgs-arm-a-refusal", check_arm_a_refusal)
    add("bsgs-arm-a-capacity-equality", check_arm_a_start)
    add("bsgs-arm-b-zero-capacity", check_arm_b_zero)
    add("bsgs-arm-b-m-equals-n", lambda: check_arm_b(5, 4, 128))
    add("bsgs-arm-b-m-greater-half", lambda: check_arm_b(5, 4, 80))
    add("bsgs-arm-b-constrained", lambda: check_arm_b(11, 10, 80))
    add("bsgs-arm-b-last-giant-block", lambda: check_arm_b(13, 12, 80))
    add("bsgs-false-hit-certificate", check_bad_certificate)
    add("bsgs-conflicting-baby", check_conflicting_baby)
    for event in ("baby_step", "baby", "scalar_bit", "scalar_precompute", "giant_lookup",
                  "negation", "giant", "certificate"):
        add(f"bsgs-cancel-{event}", lambda e=event: cancellation_case(e, "bsgs"))
    for event in ("table_hash", "table_probe", "table_write"):
        add(f"table-cancel-{event}", lambda e=event: cancellation_case(e, "table"))

    # Exact rho scalar derivative only.
    add("rho-base-and-derivative-hashes", check_rho_hashes)
    add("rho-exact-approved-splice", check_rho_splice)
    add("rho-outside-and-inside-mutation-controls", check_rho_mutation_controls)
    add("rho-isolated-scalar-zero", lambda: require(isolated_rho_scalar(0) == (None, 0, []), "rho zero changed"))
    add("rho-isolated-scalar-positive", check_rho_scalar_matrix)
    add("rho-isolated-scalar-negative", lambda: raises(ValueError, lambda: isolated_rho_scalar(-1)))
    add("rho-no-full-solve-invocation", check_no_full_rho)
    add("bsgs-public-signatures-and-secret-sentinel", check_public_signatures)

    require(len(cases) == 128, f"full reservation drifted: {len(cases)}")
    return cases


def attempt_memory_limit() -> dict[str, Any]:
    result: dict[str, Any] = {"requested_bytes": MEMORY_LIMIT_BYTES, "installed": False,
                              "mechanism": "RLIMIT_AS", "error": None}
    try:
        soft, hard = resource.getrlimit(resource.RLIMIT_AS)
        result["before_soft"] = soft
        result["before_hard"] = hard
        new_soft = MEMORY_LIMIT_BYTES if hard == resource.RLIM_INFINITY else min(MEMORY_LIMIT_BYTES, hard)
        resource.setrlimit(resource.RLIMIT_AS, (new_soft, hard))
        after_soft, after_hard = resource.getrlimit(resource.RLIMIT_AS)
        result.update({"after_soft": after_soft, "after_hard": after_hard,
                       "installed": after_soft <= MEMORY_LIMIT_BYTES})
    except BaseException as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
    return result


def worker(suite: str, output: Path) -> int:
    if output.exists():
        raise FileExistsError(str(output))
    cases = focus_cases() if suite == "focus" else full_cases()
    reservation = [{"ordinal": i, "name": case.name} for i, case in enumerate(cases, 1)]
    memory_limit = attempt_memory_limit()
    records: list[dict[str, Any]] = []
    worker_started_wall = time.monotonic()
    worker_started_cpu = time.process_time()
    worker_started_utc = utc_now()

    def alarm_handler(_signum: int, _frame: object) -> None:
        raise CaseTimeout(f"case exceeded {LIMIT_SECONDS}s")

    prior_handler = signal.signal(signal.SIGALRM, alarm_handler)
    try:
        for ordinal, case in enumerate(cases, 1):
            started_utc = utc_now()
            before_wall = time.monotonic()
            before_cpu = time.process_time()
            status = "passed"
            detail = ""
            signal.setitimer(signal.ITIMER_REAL, LIMIT_SECONDS)
            try:
                case.action()
            except BaseException as exc:
                status = "failed"
                detail = f"{type(exc).__name__}: {exc}"
            finally:
                signal.setitimer(signal.ITIMER_REAL, 0)
            elapsed_wall = time.monotonic() - before_wall
            elapsed_cpu = time.process_time() - before_cpu
            records.append({
                "ordinal": ordinal, "name": case.name, "status": status, "detail": detail,
                "started_utc": started_utc, "wall_seconds": elapsed_wall,
                "cpu_seconds": elapsed_cpu,
                "rss_raw": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            })
    finally:
        signal.signal(signal.SIGALRM, prior_handler)

    wall = time.monotonic() - worker_started_wall
    cpu = time.process_time() - worker_started_cpu
    failed = sum(row["status"] != "passed" for row in records)
    payload = {
        "schema": "crypto.autoresearch.independent_component_worker.v1",
        "task_id": TASK_ID, "experiment_id": EXPERIMENT_ID, "suite": suite,
        "reserved_before_launch": True, "case_reservation": reservation,
        "reserved_cases": len(cases), "executed_cases": len(records),
        "passed": len(records) - failed, "failed": failed,
        "started_utc": worker_started_utc, "finished_utc": utc_now(),
        "wall_seconds": wall, "cpu_seconds": cpu,
        "maximum_case_wall_seconds": max(row["wall_seconds"] for row in records),
        "peak_rss_raw": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "rss_unit": "bytes" if platform.system() == "Darwin" else "kilobytes",
        "memory_limit": memory_limit,
        "limits": {"per_case_wall_seconds": LIMIT_SECONDS,
                   "aggregate_wall_or_cpu_seconds": AGGREGATE_LIMIT_SECONDS,
                   "maximum_workers": 1, "memory_bytes": MEMORY_LIMIT_BYTES},
        "cases": records,
    }
    with output.open("x", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(json.dumps({"task_id": TASK_ID, "suite": suite, "reserved": len(cases),
                      "executed": len(records), "passed": len(records) - failed,
                      "failed": failed}, sort_keys=True))
    return 0 if failed == 0 and wall <= AGGREGATE_LIMIT_SECONDS and cpu <= AGGREGATE_LIMIT_SECONDS else 1


def parent(suite: str, receipt: Path) -> int:
    if receipt.exists():
        raise FileExistsError(str(receipt))
    cases = focus_cases() if suite == "focus" else full_cases()
    with tempfile.TemporaryDirectory(prefix=f"{TASK_ID}-{suite}-") as temp_name:
        temp = Path(temp_name)
        worker_receipt = temp / "worker.json"
        worker_stdout = temp / "worker.stdout.log"
        worker_stderr = temp / "worker.stderr.log"
        command = [sys.executable, "-B", str(Path(__file__).resolve()), "--worker", suite, str(worker_receipt)]
        source_before = {name: sha256_path(SOURCE / name) for name in
                         ("table.py", "bsgs.py", "rho-corrected.py", "tests.py", "solver-source-bindings.json")}
        started_utc = utc_now(); before_wall = time.monotonic()
        before_usage = resource.getrusage(resource.RUSAGE_CHILDREN)
        with worker_stdout.open("xb") as out, worker_stderr.open("xb") as err:
            process = subprocess.Popen(command, cwd=REPO, stdout=out, stderr=err,
                                       env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
            pid = process.pid; polls = 0
            while process.poll() is None:
                polls += 1; time.sleep(0.005)
            exit_code = process.wait()
        after_usage = resource.getrusage(resource.RUSAGE_CHILDREN)
        wall = time.monotonic() - before_wall
        cpu = ((after_usage.ru_utime - before_usage.ru_utime) +
               (after_usage.ru_stime - before_usage.ru_stime))
        nested = json.loads(worker_receipt.read_text(encoding="utf-8")) if worker_receipt.exists() else None
        source_after = {name: sha256_path(SOURCE / name) for name in source_before}
        payload = {
            "schema": "crypto.autoresearch.independent_component_attempt.v1",
            "task_id": TASK_ID, "experiment_id": EXPERIMENT_ID, "suite": suite,
            "scientific_runs": 0, "case_reservation": {"reserved_before_launch": True,
                "count": len(cases), "cases": [{"ordinal": i, "name": case.name} for i, case in enumerate(cases, 1)]},
            "command": command, "cwd": str(REPO), "started_utc": started_utc,
            "finished_utc": utc_now(), "exit_code": exit_code,
            "process": {"pid": pid, "poll_count": polls, "terminal_observed": process.returncode is not None,
                        "stdout_redirected_before_launch": True, "stderr_redirected_before_launch": True,
                        "full_popen_handle_retained": True},
            "stdout": worker_stdout.read_text(encoding="utf-8", errors="replace"),
            "stderr": worker_stderr.read_text(encoding="utf-8", errors="replace"),
            "worker_receipt": nested,
            "telemetry": {"parent_wall_seconds": wall, "children_cpu_seconds": cpu,
                "children_user_cpu_seconds": after_usage.ru_utime - before_usage.ru_utime,
                "children_system_cpu_seconds": after_usage.ru_stime - before_usage.ru_stime,
                "children_peak_rss_raw": after_usage.ru_maxrss,
                "rss_unit": "bytes" if platform.system() == "Darwin" else "kilobytes",
                "within_aggregate_limit": wall <= AGGREGATE_LIMIT_SECONDS and cpu <= AGGREGATE_LIMIT_SECONDS,
                "maximum_workers_used": 1},
            "source_sha256_before": source_before, "source_sha256_after": source_after,
            "source_unchanged": source_before == source_after,
            "receipt_self_hash": None,
            "limitations": ["Fixed synthetic source and custody checks only; no curve fixture, rho solve, runner, performance or science."],
        }
        with receipt.open("x", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True); handle.write("\n")
    ok = (exit_code == 0 and nested is not None and nested["failed"] == 0 and
          payload["telemetry"]["within_aggregate_limit"] and payload["source_unchanged"])
    return 0 if ok else 1


def combine(final_path: Path, focus_dir: Path, full1_dir: Path, full2_dir: Path,
            focus_tool_result: str, full1_tool_result: str, full2_tool_result: str,
            pre_repair_checker_sha256: str) -> int:
    if final_path.exists():
        raise FileExistsError(str(final_path))
    attempts: list[dict[str, Any]] = []
    for ordinal, (label, suite, directory, tool_result_text, checker_sha) in enumerate((
        ("focus", "focus", focus_dir, focus_tool_result, pre_repair_checker_sha256),
        ("full-attempt-1", "full", full1_dir, full1_tool_result, pre_repair_checker_sha256),
        ("full-attempt-2", "full", full2_dir, full2_tool_result, sha256_path(Path(__file__).resolve())),
    ), start=1):
        inner_path = directory / f"{suite}-inner.json"
        inner = json.loads(inner_path.read_text(encoding="utf-8"))
        tool_result = json.loads(tool_result_text)
        attempts.append({
            "ordinal": ordinal,
            "label": label,
            "suite": suite,
            "checker_sha256_at_attempt": checker_sha,
            "unique_exclusive_inner_receipt_path": str(inner_path),
            "inner_receipt_sha256": sha256_path(inner_path),
            "inner_receipt": inner,
            "outer": {
                "command": (f"/usr/bin/time -lp env PYTHONDONTWRITEBYTECODE=1 python3 -B "
                            f"{Path(__file__).resolve()} --run {suite} --receipt {inner_path} "
                            f"> {directory / (suite + '-outer.stdout')} 2> {directory / (suite + '-outer.stderr')}"),
                "cwd": str(REPO),
                "started_utc": inner["started_utc"],
                "finished_utc": inner["finished_utc"],
                "utc_boundary_basis": "nested parent timestamps enclosing the worker; outer tool wall time is retained separately",
                "stdout": (directory / f"{suite}-outer.stdout").read_text(encoding="utf-8", errors="replace"),
                "stderr": (directory / f"{suite}-outer.stderr").read_text(encoding="utf-8", errors="replace"),
                "tool_result": tool_result,
                "terminal_exit_code": tool_result.get("exit_code"),
                "session_handle": tool_result.get("session_id"),
            },
        })
    total = sum(attempt["inner_receipt"]["case_reservation"]["count"] for attempt in attempts)
    executed = sum(attempt["inner_receipt"]["worker_receipt"]["executed_cases"] for attempt in attempts)
    passed = sum(attempt["inner_receipt"]["worker_receipt"]["passed"] for attempt in attempts)
    failed = sum(attempt["inner_receipt"]["worker_receipt"]["failed"] for attempt in attempts)
    payload = {
        "schema": "crypto.autoresearch.independent_component_review_receipt.v1",
        "task_id": TASK_ID,
        "experiment_id": EXPERIMENT_ID,
        "scientific_runs": 0,
        "attempts": attempts,
        "accounting": {
            "maximum_total_fixed_cases": 320,
            "total_reserved_cases": total,
            "total_executed_cases": executed,
            "passed": passed,
            "failed": failed,
            "complete_suites": 2,
            "final_complete_suite_cases": 128,
            "remaining_case_capacity": 320 - executed,
            "per_case_wall_seconds": LIMIT_SECONDS,
            "aggregate_wall_or_cpu_seconds": AGGREGATE_LIMIT_SECONDS,
            "maximum_workers": 1,
            "memory_bytes": MEMORY_LIMIT_BYTES,
        },
        "source_sha256": {
            "table.py": sha256_path(SOURCE / "table.py"),
            "bsgs.py": sha256_path(SOURCE / "bsgs.py"),
            "rho-corrected.py": sha256_path(SOURCE / "rho-corrected.py"),
            "tests.py": sha256_path(SOURCE / "tests.py"),
            "solver-source-bindings.json": sha256_path(SOURCE / "solver-source-bindings.json"),
            "checks.py": sha256_path(Path(__file__).resolve()),
        },
        "inference": {
            "role": "validator",
            "requested_policy": "review-adversarial",
            "reasoning_effort": "xhigh",
            "resolved_model_id": "gpt-5.6-sol",
            "model_verified_by_fresh_probe": False,
            "fallback_used": False,
            "degraded_requirements": [],
            "provider_contains_bedrock": False,
            "independent_session": True,
        },
        "receipt_self_hash": None,
        "receipt_self_hash_note": "No self hash. Coordinator archive binds the final receipt.",
        "limitations": [
            "Fixed synthetic source and custody review only; no scientific curve, fixture, rho solve, runner, manifest, Docker, guard or performance result.",
            "The failed predecessor's missing first per-case receipt remains missing and was not reconstructed.",
            "RLIMIT_AS installation status is recorded per worker; observed RSS is diagnostic when installation failed.",
        ],
        "procedure_events": [
            {
                "kind": "checker_correction",
                "after_attempt": "full-attempt-1",
                "detail": "The first full suite constructed one extra blank line at the approved rho splice boundary. Source hashes and the exact derivative hash already passed. The checker removed only that extra expected newline before the reserved final suite.",
                "scientific_effect": "none",
            },
            {
                "kind": "same_session_usage_limit_interruption",
                "after_attempt": "full-attempt-1",
                "observed_at_utc": None,
                "timestamp_reason": "The operational resume notice supplied no exact timestamp.",
                "detail": "The validator turn stopped on a usage-limit error and resumed the same independent task after an account check. No reset, model change, fallback, degradation, receipt overwrite or case-accounting restart occurred.",
                "scientific_effect": "none",
            },
        ],
    }
    with final_path.open("x", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", choices=("focus", "full"))
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--worker", choices=("focus", "full"))
    parser.add_argument("worker_receipt", nargs="?", type=Path)
    parser.add_argument("--combine", type=Path)
    parser.add_argument("--focus-dir", type=Path)
    parser.add_argument("--full1-dir", type=Path)
    parser.add_argument("--full2-dir", type=Path)
    parser.add_argument("--focus-tool-result")
    parser.add_argument("--full1-tool-result")
    parser.add_argument("--full2-tool-result")
    parser.add_argument("--pre-repair-checker-sha256")
    args = parser.parse_args()
    if args.worker:
        require(args.worker_receipt is not None, "worker receipt required")
        return worker(args.worker, args.worker_receipt)
    if args.combine:
        require(args.focus_dir is not None and args.full1_dir is not None and args.full2_dir is not None,
                "attempt directories required")
        require(args.focus_tool_result is not None and args.full1_tool_result is not None and
                args.full2_tool_result is not None and args.pre_repair_checker_sha256 is not None,
                "outer tool results and pre-repair checker hash required")
        return combine(args.combine, args.focus_dir, args.full1_dir, args.full2_dir,
                       args.focus_tool_result, args.full1_tool_result, args.full2_tool_result,
                       args.pre_repair_checker_sha256)
    require(args.run is not None and args.receipt is not None, "--run and --receipt required")
    return parent(args.run, args.receipt)


if __name__ == "__main__":
    raise SystemExit(main())
