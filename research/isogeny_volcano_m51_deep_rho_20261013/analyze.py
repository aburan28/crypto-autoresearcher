#!/usr/bin/env python3
"""Validate and analyze the sealed four-level m=51 native-rho benchmark."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import stat
import struct
import sys
import types
from collections import defaultdict
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Sequence


CHILD_ENV = {
    "LANG": "C",
    "LC_ALL": "C",
    "PATH": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
    "TZ": "UTC",
}
ANALYSIS_ENV = {
    **CHILD_ENV,
    "MKL_NUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
    "OMP_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
}
if __name__ == "__main__":
    if sys.flags.isolated != 1 or sys.flags.dont_write_bytecode != 1:
        raise SystemExit("scientific analysis requires Python -I -B")
    if "-I" not in sys.orig_argv or "-B" not in sys.orig_argv:
        raise SystemExit("scientific analysis requires explicit separate -I and -B flags")
    if dict(os.environ) != ANALYSIS_ENV:
        raise SystemExit(
            "scientific analysis requires the exact sanitized analysis environment"
        )
    os.environ.clear()
    os.environ.update(ANALYSIS_ENV)

import numpy as np


HERE = Path(__file__).resolve().parent
MASK64 = (1 << 64) - 1
FROZEN_FILES = {
    "PROTOCOL.md",
    "README.md",
    "TRANSFER_BOUNDARY.md",
    "analyze.py",
    "batch_driver.c",
    "bind_selection.py",
    "build_schedule.py",
    "deep_selection.json",
    "design.py",
    "floor271_orbits.csv",
    "params.h",
    "rho.c",
    "run_benchmark.py",
    "schedule.csv",
    "spec.json",
    "synthetic_test.py",
}
CORE_RESULT_FIELDS = (
    "run",
    "target_scalar",
    "walk_stream_seed",
    "ops",
    "adds",
    "doubles",
    "setup_ops",
    "setup_adds",
    "setup_doubles",
    "walk_ops",
    "walk_adds",
    "walk_doubles",
    "canon_calls",
    "canon_x_squares",
    "canon_y_squares",
    "canon_sign_tests",
    "canon_negations",
    "walks",
    "cycles",
    "abandoned",
    "useless",
    "ok",
    "sec",
)
NORMALIZED_HEADER: tuple[str, ...] = ()
INTEGER_FIELDS = {
    "block_id",
    "pair_id",
    "within_pair",
    "b",
    "a2",
    "f_E",
    "mode",
    "setup_seed",
    "target_seed",
    "walk_seed",
    "target_index",
    "worker",
    "unit_id",
    *(field for field in CORE_RESULT_FIELDS if field != "sec"),
}
SUMMARY_FIELDS = (
    "walk_ops",
    "walk_adds",
    "walk_doubles",
    "setup_ops",
    "setup_adds",
    "setup_doubles",
    "ops",
    "adds",
    "doubles",
    "canon_calls",
    "canon_x_squares",
    "canon_y_squares",
    "canon_sign_tests",
    "canon_negations",
    "walks",
    "cycles",
    "abandoned",
    "useless",
    "sec",
)
NATIVE_SETUP_HEADER = (
    "worker",
    "curve_id",
    "unit_id",
    "b",
    "a2",
    "mode",
    "setup_seed",
    "pgen_x",
    "pgen_y",
    "setup_fingerprint",
    "setup_sec",
)
CONTRAST_IDS = (
    "A-C",
    "P-C",
    "B-C",
    "P-A",
    "B-A",
    "B-P",
    "M271",
    "M120871",
    "I",
)
CONTRAST_MATRIX = np.asarray(
    [
        [-1.0, 1.0, 0.0, 0.0],
        [-1.0, 0.0, 1.0, 0.0],
        [-1.0, 0.0, 0.0, 1.0],
        [0.0, -1.0, 1.0, 0.0],
        [0.0, -1.0, 0.0, 1.0],
        [0.0, 0.0, -1.0, 1.0],
        [-0.5, 0.5, -0.5, 0.5],
        [-0.5, -0.5, 0.5, 0.5],
        [0.5, -0.5, -0.5, 0.5],
    ],
    dtype=np.float64,
)

ARMS: tuple[str, ...]
FIELD_MASK: int
INFERENCE_BLOCKS: int
PAIR_COUNT: int
PLAN_HEADER: tuple[str, ...]
RNG_TEST_VECTORS: tuple[tuple[int, int, int, int, int], ...]
_design_binding: tuple[Path, str] | None = None


class AnalysisError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def valid_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def load_design_module(path: Path, expected_sha256: str) -> Any:
    """Compile exact source bytes; never consult timestamp-valid ``pyc`` files."""
    source = path.read_bytes() if path.is_file() and not path.is_symlink() else b""
    if (
        not valid_sha256(expected_sha256)
        or hashlib.sha256(source).hexdigest() != expected_sha256
    ):
        raise AnalysisError("design module differs from the run-frozen bytes")
    module_name = f"m51_frozen_design_{expected_sha256}"
    module = types.ModuleType(module_name)
    module.__file__ = str(path)
    module.__package__ = ""
    previous = sys.modules.get(module_name)
    sys.modules[module_name] = module
    try:
        exec(compile(source, str(path), "exec"), module.__dict__)
    except BaseException:
        if previous is None:
            sys.modules.pop(module_name, None)
        else:
            sys.modules[module_name] = previous
        raise
    if sha256_file(path) != expected_sha256:
        raise AnalysisError("frozen design.py changed while it was loaded")
    return module


def bind_design(path: Path, expected_sha256: str) -> None:
    """Bind analysis helpers to one exact design module for this process."""
    global ARMS, FIELD_MASK, INFERENCE_BLOCKS, NORMALIZED_HEADER, PAIR_COUNT, PLAN_HEADER
    global RNG_TEST_VECTORS
    global build_plan, build_setup_robustness_plan
    global expected_scalar, expected_walk_stream, generate_schedule
    global load_json, load_selection, read_f271_orbits, read_schedule
    global _design_binding
    if path.is_symlink() or not path.is_file():
        raise AnalysisError("design module must be a regular non-symlink file")
    resolved = path.resolve(strict=True)
    binding = (resolved, expected_sha256)
    if _design_binding is not None:
        if _design_binding != binding:
            raise AnalysisError("analysis process refuses to rebind design.py")
        return
    module = load_design_module(resolved, expected_sha256)
    required = (
        "ARMS",
        "FIELD_MASK",
        "INFERENCE_BLOCKS",
        "PAIR_COUNT",
        "PLAN_HEADER",
        "RNG_TEST_VECTORS",
        "build_plan",
        "build_setup_robustness_plan",
        "expected_scalar",
        "expected_walk_stream",
        "generate_schedule",
        "load_json",
        "load_selection",
        "read_f271_orbits",
        "read_schedule",
    )
    if any(not hasattr(module, name) for name in required):
        raise AnalysisError("run-frozen design.py lacks a required analysis symbol")
    ARMS = tuple(module.ARMS)
    FIELD_MASK = int(module.FIELD_MASK)
    INFERENCE_BLOCKS = int(module.INFERENCE_BLOCKS)
    PAIR_COUNT = int(module.PAIR_COUNT)
    PLAN_HEADER = tuple(module.PLAN_HEADER)
    RNG_TEST_VECTORS = tuple(tuple(row) for row in module.RNG_TEST_VECTORS)
    build_plan = module.build_plan
    build_setup_robustness_plan = module.build_setup_robustness_plan
    expected_scalar = module.expected_scalar
    expected_walk_stream = module.expected_walk_stream
    generate_schedule = module.generate_schedule
    load_json = module.load_json
    load_selection = module.load_selection
    read_f271_orbits = module.read_f271_orbits
    read_schedule = module.read_schedule
    NORMALIZED_HEADER = (*PLAN_HEADER, "worker", "unit_id", *CORE_RESULT_FIELDS)
    _design_binding = binding


def safe_manifest_name(value: str, *, basename_only: bool = False) -> bool:
    path = PurePosixPath(value)
    return (
        value == path.as_posix()
        and not path.is_absolute()
        and bool(path.parts)
        and all(part not in ("", ".", "..") for part in path.parts)
        and (not basename_only or len(path.parts) == 1)
    )


def read_hash_manifest(path: Path, *, basename_only: bool = False) -> tuple[dict[str, str], str]:
    if path.is_symlink() or not path.is_file():
        raise AnalysisError(f"missing regular manifest {path}")
    content = path.read_text()
    if not content or not content.endswith("\n"):
        raise AnalysisError(f"{path}: empty or unterminated manifest")
    entries: dict[str, str] = {}
    for number, line in enumerate(content.splitlines(), 1):
        pieces = line.split("  ", 1)
        if (
            len(pieces) != 2
            or not valid_sha256(pieces[0])
            or not safe_manifest_name(pieces[1], basename_only=basename_only)
            or pieces[1] in entries
        ):
            raise AnalysisError(f"{path}:{number}: malformed manifest entry")
        entries[pieces[1]] = pieces[0]
    return entries, hashlib.sha256(content.encode()).hexdigest()


def verify_tree(run: Path) -> tuple[dict[str, str], str]:
    entries, manifest_hash = read_hash_manifest(run / "MANIFEST.sha256")
    actual: set[str] = set()
    for path in run.rglob("*"):
        if path.is_symlink():
            raise AnalysisError(f"symlink forbidden in sealed run: {path}")
        if path.is_dir():
            continue
        if not path.is_file() or not stat.S_ISREG(path.stat().st_mode):
            raise AnalysisError(f"non-regular path in sealed run: {path}")
        relative = path.relative_to(run).as_posix()
        if relative != "MANIFEST.sha256":
            actual.add(relative)
    if actual != set(entries):
        raise AnalysisError(
            f"sealed run tree differs; missing={sorted(set(entries)-actual)}, "
            f"extra={sorted(actual-set(entries))}"
        )
    for name, expected in entries.items():
        if sha256_file(run / name) != expected:
            raise AnalysisError(f"sealed run hash differs: {name}")
    return entries, manifest_hash


def verify_frozen_snapshot(run: Path) -> tuple[dict[str, str], str]:
    inputs = run / "inputs"
    entries, manifest_hash = read_hash_manifest(inputs / "FROZEN.sha256", basename_only=True)
    if set(entries) != FROZEN_FILES or tuple(entries) != tuple(sorted(FROZEN_FILES)):
        raise AnalysisError("run frozen-input file set/order differs")
    actual = {
        path.name
        for path in inputs.iterdir()
        if path.is_file() and path.name != "FROZEN.sha256"
    }
    if actual != set(entries):
        raise AnalysisError("run input snapshot differs from FROZEN.sha256")
    for name, expected in entries.items():
        path = inputs / name
        if path.is_symlink() or not path.is_file() or sha256_file(path) != expected:
            raise AnalysisError(f"run frozen input differs: {name}")
    if sha256_file(Path(__file__)) != entries["analyze.py"]:
        raise AnalysisError("invoked analyzer differs from the run-frozen analyzer")
    return entries, manifest_hash


def parse_int(value: Any, context: str) -> int:
    if not isinstance(value, str) or not value or not value.isascii():
        raise AnalysisError(f"{context}: expected canonical unsigned decimal")
    if not value.isdecimal() or (value != "0" and value.startswith("0")):
        raise AnalysisError(f"{context}: expected canonical unsigned decimal")
    parsed = int(value)
    if parsed > MASK64:
        raise AnalysisError(f"{context}: integer exceeds uint64")
    return parsed


def parse_plan_csv(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != PLAN_HEADER:
            raise AnalysisError(f"{path}: record-plan header differs")
        for line_number, raw in enumerate(reader, 2):
            if None in raw or set(raw) != set(PLAN_HEADER):
                raise AnalysisError(f"{path}:{line_number}: malformed plan row")
            row: dict[str, Any] = {}
            for key, value in raw.items():
                if key in {
                    "block_id",
                    "pair_id",
                    "within_pair",
                    "conjugate",
                    "b",
                    "a2",
                    "f_E",
                    "mode",
                    "setup_seed",
                    "target_seed",
                    "walk_seed",
                    "target_index",
                }:
                    if value == "" and key == "conjugate":
                        row[key] = 0
                    else:
                        row[key] = parse_int(value, f"{path}:{line_number}:{key}")
                elif key == "orbit_id":
                    row[key] = "" if value == "" else parse_int(value, f"{path}:{line_number}:{key}")
                else:
                    row[key] = value
            rows.append(row)
    return rows


def parse_records(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != NORMALIZED_HEADER:
            raise AnalysisError(f"{path}: normalized header differs")
        for line_number, raw in enumerate(reader, 2):
            if None in raw or set(raw) != set(NORMALIZED_HEADER):
                raise AnalysisError(f"{path}:{line_number}: malformed normalized row")
            row: dict[str, Any] = {}
            for key, value in raw.items():
                if key in INTEGER_FIELDS:
                    row[key] = parse_int(value, f"{path}:{line_number}:{key}")
                elif key in ("orbit_id", "conjugate"):
                    row[key] = "" if value == "" else parse_int(value, f"{path}:{line_number}:{key}")
                elif key == "sec":
                    try:
                        row[key] = float(value)
                    except ValueError as exc:
                        raise AnalysisError(f"{path}:{line_number}: invalid seconds") from exc
                else:
                    row[key] = value
            rows.append(row)
    return rows


def validate_records_against_plan(
    records: list[dict[str, Any]],
    expected_plan: list[dict[str, Any]],
    *,
    context: str,
) -> None:
    expected_count = len(expected_plan)
    if (
        len(records) != expected_count
        or [row["record_id"] for row in records]
        != sorted(row["record_id"] for row in records)
    ):
        raise AnalysisError(f"{context}: records are incomplete, duplicated, or unsorted")
    by_id = {row["record_id"]: row for row in records}
    if len(by_id) != expected_count or set(by_id) != {
        row["record_id"] for row in expected_plan
    }:
        raise AnalysisError(f"{context}: normalized record key set differs from plan")
    for expected in expected_plan:
        row = by_id[expected["record_id"]]
        for field in PLAN_HEADER:
            if row[field] != expected[field]:
                raise AnalysisError(
                    f"{context}: record-plan binding differs: {row['record_id']}:{field}"
                )
        if row["target_scalar"] != expected_scalar(
            row["target_seed"], row["target_index"]
        ):
            raise AnalysisError(f"{context}: target scalar differs: {row['record_id']}")
        if row["walk_stream_seed"] != expected_walk_stream(
            row["walk_seed"], row["target_index"]
        ):
            raise AnalysisError(f"{context}: walk stream differs: {row['record_id']}")
        identities = (
            row["setup_ops"] == row["setup_adds"] + row["setup_doubles"],
            row["walk_ops"] == row["walk_adds"] + row["walk_doubles"],
            row["ops"] == row["adds"] + row["doubles"],
            row["ops"] == row["setup_ops"] + row["walk_ops"],
            row["adds"] == row["setup_adds"] + row["walk_adds"],
            row["doubles"] == row["setup_doubles"] + row["walk_doubles"],
        )
        if not all(identities):
            raise AnalysisError(f"{context}: counter identity differs: {row['record_id']}")
        if (
            row["ok"] != 1
            or row["setup_adds"] != 128
            or row["setup_doubles"] != 34
            or row["walk_ops"] <= 0
            or row["walks"] <= 0
            or row["abandoned"] > row["walks"]
            or row["useless"] > row["walks"]
            or row["canon_calls"] != row["canon_sign_tests"]
            or row["canon_negations"] > row["canon_sign_tests"]
            or row["canon_x_squares"] != 0
            or row["canon_y_squares"] != 0
            or not math.isfinite(row["sec"])
            or row["sec"] <= 0
        ):
            raise AnalysisError(
                f"{context}: correctness/accounting gate differs: {row['record_id']}"
            )


def validate_plan_and_records(
    run: Path, phase: Path
) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    inputs = run / "inputs"
    spec = load_json(inputs / "spec.json")
    if spec.get("schema") != "m51-deep-rho-study/v1" or spec.get("status") not in (
        "frozen-design-unlaunched",
        "frozen-design",
    ):
        raise AnalysisError("run spec is not a frozen benchmark contract")
    schedule = read_schedule(inputs / "schedule.csv")
    if schedule != generate_schedule(int(spec["seeds"]["schedule_root"])):
        raise AnalysisError("run schedule differs from deterministic regeneration")
    _binding, pairs = load_selection(inputs / "deep_selection.json")
    f271 = read_f271_orbits(inputs / "floor271_orbits.csv")
    expected_plan = build_plan(schedule, pairs, f271, spec["seeds"])
    materialized = parse_plan_csv(phase / "record_plan.csv")
    if materialized != expected_plan:
        raise AnalysisError("materialized record plan differs from frozen reconstruction")
    records = parse_records(phase / "records.csv")
    validate_records_against_plan(records, expected_plan, context="primary")
    validate_blocks(records)
    return spec, records, {"pairs": pairs, "expected_plan": expected_plan}


def validate_blocks(records: list[dict[str, Any]]) -> None:
    grouped: dict[tuple[str, int], list[dict[str, Any]]] = defaultdict(list)
    for row in records:
        grouped[(row["replicate"], row["block_id"])].append(row)
    if len(grouped) != INFERENCE_BLOCKS + 2 * 1024:
        raise AnalysisError("replicate/block key count differs")
    for (replicate, block_id), block in grouped.items():
        if len(block) != 4 or {row["arm"] for row in block} != set(ARMS):
            raise AnalysisError(f"incomplete four-arm block: {replicate}/{block_id}")
        if len({row["target_scalar"] for row in block}) != 1 or len({row["target_seed"] for row in block}) != 1:
            raise AnalysisError(f"target pairing differs: {replicate}/{block_id}")
        if len({row["setup_seed"] for row in block}) != 1:
            raise AnalysisError(f"setup namespace differs: {replicate}/{block_id}")
        p = next(row for row in block if row["arm"] == "P")
        b = next(row for row in block if row["arm"] == "B")
        if p["conjugate"] != b["conjugate"]:
            raise AnalysisError(f"P/B edge conjugacy differs: {replicate}/{block_id}")
    for block_id in range(INFERENCE_BLOCKS):
        if ("inference", block_id) not in grouped or ("aa-A", block_id) in grouped or ("aa-B", block_id) in grouped:
            raise AnalysisError(f"inference/holdout overlap or omission at block {block_id}")
    for block_id in range(INFERENCE_BLOCKS, INFERENCE_BLOCKS + 1024):
        keys = {replicate for replicate in ("aa-A", "aa-B") if (replicate, block_id) in grouped}
        if keys != {"aa-A", "aa-B"} or ("inference", block_id) in grouped:
            raise AnalysisError(f"A/A streams missing or overlap at block {block_id}")
        a = sorted(grouped[("aa-A", block_id)], key=lambda row: row["arm"])
        b = sorted(grouped[("aa-B", block_id)], key=lambda row: row["arm"])
        for row_a, row_b in zip(a, b, strict=True):
            fixed_fields = (
                "arm",
                "curve_id",
                "b",
                "a2",
                "setup_seed",
                "target_seed",
                "target_index",
                "target_scalar",
            )
            if any(row_a[field] != row_b[field] for field in fixed_fields):
                raise AnalysisError(f"A/A non-walk metadata differs at block {block_id}")
            if row_a["walk_seed"] == row_b["walk_seed"] or row_a["walk_stream_seed"] == row_b["walk_stream_seed"]:
                raise AnalysisError(f"A/A walk namespaces collide at block {block_id}")


def validate_setup_and_process_costs(
    run: Path,
    manifest: dict[str, Any],
    *,
    records: list[dict[str, Any]] | None = None,
    robustness_plan: list[dict[str, Any]] | None = None,
    setup_seeds: list[int] | None = None,
) -> dict[str, Any]:
    setup_path = run / "native_setups.csv"
    if manifest.get("native_setups_sha256") != sha256_file(setup_path):
        raise AnalysisError("run manifest native-setup hash differs")
    rows: list[dict[str, Any]] = []
    with setup_path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != NATIVE_SETUP_HEADER:
            raise AnalysisError("native setup header differs")
        for line_number, raw in enumerate(reader, 2):
            if None in raw or set(raw) != set(NATIVE_SETUP_HEADER):
                raise AnalysisError(f"native_setups.csv:{line_number}: malformed row")
            row: dict[str, Any] = {
                key: parse_int(raw[key], f"native_setups.csv:{line_number}:{key}")
                for key in (
                    "worker",
                    "unit_id",
                    "b",
                    "a2",
                    "mode",
                    "setup_seed",
                    "pgen_x",
                    "pgen_y",
                )
            }
            row["curve_id"] = raw["curve_id"]
            fingerprint = raw["setup_fingerprint"]
            if len(fingerprint) != 16 or any(character not in "0123456789abcdef" for character in fingerprint):
                raise AnalysisError(f"native_setups.csv:{line_number}: invalid fingerprint")
            row["setup_fingerprint"] = fingerprint
            try:
                row["setup_sec"] = float(raw["setup_sec"])
            except ValueError as exc:
                raise AnalysisError(f"native_setups.csv:{line_number}: invalid seconds") from exc
            if not math.isfinite(row["setup_sec"]) or row["setup_sec"] <= 0:
                raise AnalysisError(f"native_setups.csv:{line_number}: nonpositive seconds")
            if (
                row["pgen_x"] > FIELD_MASK
                or row["pgen_y"] > FIELD_MASK
                or (row["pgen_x"] == 0 and row["pgen_y"] == 0)
            ):
                raise AnalysisError(
                    f"native_setups.csv:{line_number}: invalid native generator"
                )
            rows.append(row)
    robustness = robustness_plan is not None
    expected_total = 1649 if robustness else 3556
    if len(rows) != expected_total or len(
        {(row["worker"], row["unit_id"]) for row in rows}
    ) != expected_total:
        raise AnalysisError("native setup invocation count/key set differs")
    if records is not None:
        setup_by_unit = {(row["worker"], row["unit_id"]): row for row in rows}
        used_units: set[tuple[int, int]] = set()
        for record in records:
            key = (int(record["worker"]), int(record["unit_id"]))
            setup = setup_by_unit.get(key)
            if setup is None or any(
                setup[field] != record[field]
                for field in ("curve_id", "b", "a2", "mode", "setup_seed")
            ):
                raise AnalysisError(
                    f"normalized record/native setup binding differs: {record['record_id']}"
                )
            used_units.add(key)
        if used_units != set(setup_by_unit):
            raise AnalysisError("native setup contains an unused execution unit")

    def setup_arm(curve_id: str) -> str:
        if curve_id == "C":
            return "C"
        prefix = curve_id[:1]
        if prefix not in ("A", "P", "B"):
            raise AnalysisError(f"unknown native setup curve ID {curve_id!r}")
        return prefix

    by_arm = {arm: [row for row in rows if setup_arm(row["curve_id"]) == arm] for arm in ARMS}
    expected_units = (
        {"C": 17, "A": 544, "P": 544, "B": 544}
        if robustness
        else {"C": 20, "A": 272, "P": 1632, "B": 1632}
    )
    expected_models = (
        {"C": 1, "A": 32, "P": 32, "B": 32}
        if robustness
        else {"C": 1, "A": 272, "P": 1632, "B": 1632}
    )
    for arm in ARMS:
        if len(by_arm[arm]) != expected_units[arm]:
            raise AnalysisError(f"native setup unit count differs for {arm}")
        if len({row["curve_id"] for row in by_arm[arm]}) != expected_models[arm]:
            raise AnalysisError(f"native setup model count differs for {arm}")

    worker_receipts = manifest.get("worker_receipts")
    if not isinstance(worker_receipts, list) or len(worker_receipts) != 4:
        raise AnalysisError("run manifest worker receipts differ")
    process_seconds: dict[str, float] = {}
    plan_summary = load_json(run / "plan.json")
    plan_workers = plan_summary.get("workers")
    if (
        plan_summary.get("schema") != "m51-deep-rho-plan/v1"
        or plan_summary.get("records") != (len(records) if records is not None else None)
        or plan_summary.get("distinct_models") != sum(expected_models.values())
        or plan_summary.get("execution_units") != expected_total
        or plan_summary.get("record_plan_sha256") != sha256_file(run / "record_plan.csv")
        or not isinstance(plan_workers, list)
        or len(plan_workers) != 4
    ):
        raise AnalysisError("materialized worker-plan summary differs")
    host = load_json(run.parent / "provenance.json").get("host")
    if not isinstance(host, dict) or not isinstance(host.get("taskset"), str):
        raise AnalysisError("taskset provenance differs")
    taskset_path = Path(host["taskset"])
    if (
        taskset_path.is_symlink()
        or not taskset_path.is_file()
        or host.get("taskset_sha256") != sha256_file(taskset_path)
    ):
        raise AnalysisError("taskset executable binding differs")
    for expected_worker, binding in enumerate(sorted(worker_receipts, key=lambda row: row.get("worker", -1))):
        if not isinstance(binding, dict) or binding.get("worker") != expected_worker or not valid_sha256(binding.get("sha256")):
            raise AnalysisError("run manifest worker receipt binding differs")
        path = run / "raw" / f"worker-{expected_worker}.receipt.json"
        if sha256_file(path) != binding["sha256"]:
            raise AnalysisError(f"worker {expected_worker} receipt hash differs")
        receipt = load_json(path)
        plan_binding = sorted(plan_workers, key=lambda row: row.get("worker", -1))[
            expected_worker
        ]
        plan_path = run / "plans" / f"worker-{expected_worker}.csv"
        expected_command = [
            str(taskset_path),
            "-c",
            str(expected_worker),
            str(run.parent / "build/rho-batch"),
            "run-plan",
            str(plan_path),
            str(run / "raw" / f"worker-{expected_worker}.results.csv.partial"),
            str(run / "raw" / f"worker-{expected_worker}.setups.csv.partial"),
        ]
        if (
            receipt.get("success") is not True
            or receipt.get("exit_status") != 0
            or receipt.get("timed_out") is not False
            or receipt.get("cancelled") is not False
            or receipt.get("residual_group_cleaned") is not False
            or receipt.get("environment") != CHILD_ENV
            or receipt.get("worker") != expected_worker
            or receipt.get("core") != expected_worker
            or receipt.get("command") != expected_command
            or receipt.get("cwd") != str(run)
            or receipt.get("binary_sha256")
            != sha256_file(run.parent / "build/rho-batch")
            or receipt.get("plan_sha256") != sha256_file(plan_path)
            or not isinstance(plan_binding, dict)
            or plan_binding.get("worker") != expected_worker
            or plan_binding.get("core") != expected_worker
            or plan_binding.get("plan_sha256") != sha256_file(plan_path)
            or receipt.get("expected_records") != plan_binding.get("records")
            or receipt.get("expected_units") != plan_binding.get("units")
        ):
            raise AnalysisError(f"worker {expected_worker} receipt is not successful")
        stdout = run / "raw" / f"worker-{expected_worker}.stdout"
        stderr = run / "raw" / f"worker-{expected_worker}.stderr"
        if (
            receipt.get("stdout_sha256") != sha256_file(stdout)
            or receipt.get("stderr_sha256") != sha256_file(stderr)
            or stdout.stat().st_size != 0
            or stderr.stat().st_size != 0
        ):
            raise AnalysisError(f"worker {expected_worker} stdout/stderr binding differs")
        elapsed = receipt.get("elapsed_seconds")
        if isinstance(elapsed, bool) or not isinstance(elapsed, (int, float)) or not math.isfinite(float(elapsed)) or float(elapsed) <= 0:
            raise AnalysisError(f"worker {expected_worker} elapsed seconds differ")
        process_seconds[str(expected_worker)] = float(elapsed)

    certificate_audit: dict[str, Any] | None = None
    if robustness:
        if setup_seeds is None or len(setup_seeds) != 17 or len(set(setup_seeds)) != 17:
            raise AnalysisError("setup-robustness setup seed contract differs")
        expected_by_curve: dict[str, tuple[int, int, int]] = {}
        assert robustness_plan is not None
        for planned in robustness_plan:
            identity = (
                int(planned["b"]),
                int(planned["a2"]),
                int(planned["mode"]),
            )
            prior = expected_by_curve.setdefault(str(planned["curve_id"]), identity)
            if prior != identity:
                raise AnalysisError("setup-robustness planned model identity changes")
        by_curve: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in rows:
            by_curve[str(row["curve_id"])].append(row)
        if len(expected_by_curve) != 97 or set(by_curve) != set(expected_by_curve):
            raise AnalysisError("setup-robustness setup/model coverage differs")
        seed_set = set(setup_seeds)
        for curve_id, curve_rows in by_curve.items():
            if (
                len(curve_rows) != 17
                or {int(row["setup_seed"]) for row in curve_rows} != seed_set
                or any(
                    (int(row["b"]), int(row["a2"]), int(row["mode"]))
                    != expected_by_curve[curve_id]
                    for row in curve_rows
                )
                or len(
                    {
                        (
                            int(row["pgen_x"]),
                            int(row["pgen_y"]),
                            str(row["setup_fingerprint"]),
                        )
                        for row in curve_rows
                    }
                )
                != 17
            ):
                raise AnalysisError(
                    f"setup-robustness setup certificates differ for {curve_id}"
                )
        certificate_audit = {
            "distinct_models": 97,
            "certificates_per_model": 17,
            "distinct_certificate_identities_per_model": 17,
            "setup_seeds": setup_seeds,
        }

    result = {
        "native_setup_invocations": len(rows),
        "distinct_native_models": len({row["curve_id"] for row in rows}),
        "native_setup_by_arm": {
            arm: {
                "invocations": len(by_arm[arm]),
                "distinct_models": len({row["curve_id"] for row in by_arm[arm]}),
                "setup_sec": summarize(row["setup_sec"] for row in by_arm[arm]),
            }
            for arm in ARMS
        },
        "native_setup_total_seconds_sum_across_workers": float(sum(row["setup_sec"] for row in rows)),
        "worker_process_elapsed_seconds": process_seconds,
        "worker_process_elapsed_seconds_max": max(process_seconds.values()),
        "qualification": "setup and worker wall seconds are separate descriptive costs; they are not converted to walk_ops or an end-to-end bound",
    }
    if certificate_audit is not None:
        result["setup_certificate_audit"] = certificate_audit
    return result


def calibrated_means(
    records: Sequence[dict[str, Any]],
    pair_ids: Sequence[int],
    *,
    subset: str,
    replicate: str,
) -> tuple[np.ndarray, dict[str, Any]]:
    retained = set(pair_ids)
    rows = [
        row
        for row in records
        if row["subset"] == subset
        and row["replicate"] == replicate
        and row["pair_id"] in retained
    ]
    expected_per_pair = 96 if subset == "inference" else 32
    if len(rows) != len(retained) * expected_per_pair * 4:
        raise AnalysisError(f"{subset}/{replicate}: retained record count differs")
    by_arm = {arm: [row for row in rows if row["arm"] == arm] for arm in ARMS}
    if any(len(by_arm[arm]) != len(retained) * expected_per_pair for arm in ARMS):
        raise AnalysisError(f"{subset}/{replicate}: arm balance differs")

    c = float(np.mean([row["walk_ops"] for row in by_arm["C"]]))
    a_cells: dict[tuple[int, int], list[float]] = defaultdict(list)
    for row in by_arm["A"]:
        if not isinstance(row["orbit_id"], int) or not isinstance(row["conjugate"], int):
            raise AnalysisError("A model identity is absent")
        a_cells[(row["orbit_id"], row["conjugate"])].append(float(row["walk_ops"]))
    if set(a_cells) != {(orbit_id, conjugate) for orbit_id in range(1, 17) for conjugate in range(17)}:
        raise AnalysisError(f"{subset}/{replicate}: A model coverage differs")
    a_cell_means = {key: float(np.mean(values)) for key, values in a_cells.items()}
    a = float(np.mean(list(a_cell_means.values())))

    deep_means: dict[str, float] = {}
    deep_counts: dict[str, dict[tuple[int, int], int]] = {}
    expected_conjugates = 51 if subset == "inference" else 32
    for arm in ("P", "B"):
        cells: dict[tuple[int, int], list[float]] = defaultdict(list)
        for row in by_arm[arm]:
            if not isinstance(row["conjugate"], int):
                raise AnalysisError(f"{arm} model identity is absent")
            cells[(row["pair_id"], row["conjugate"])].append(float(row["walk_ops"]))
        for pair_id in retained:
            pair_cells = [key for key in cells if key[0] == pair_id]
            if len(pair_cells) != expected_conjugates:
                raise AnalysisError(
                    f"{subset}/{replicate}: {arm} pair {pair_id} has "
                    f"{len(pair_cells)} model cells, expected {expected_conjugates}"
                )
        cell_means = {key: float(np.mean(values)) for key, values in cells.items()}
        pair_means = [
            float(np.mean([value for (pair, _), value in cell_means.items() if pair == pair_id]))
            for pair_id in sorted(retained)
        ]
        deep_means[arm] = float(np.mean(pair_means))
        deep_counts[arm] = {key: len(values) for key, values in cells.items()}

    means = np.asarray([c, a, deep_means["P"], deep_means["B"]], dtype=np.float64)
    if not np.all(np.isfinite(means)) or np.any(means <= 0):
        raise AnalysisError(f"{subset}/{replicate}: nonpositive/nonfinite calibrated mean")
    audit = {
        "subset": subset,
        "replicate": replicate,
        "pairs": len(retained),
        "records_per_arm": {arm: len(by_arm[arm]) for arm in ARMS},
        "model_cells": {
            "C": 1,
            "A": len(a_cells),
            "P": len(deep_counts["P"]),
            "B": len(deep_counts["B"]),
        },
        "calibrated_weight_sums": {arm: 1.0 for arm in ARMS},
        "A_cell_count_range": [min(map(len, a_cells.values())), max(map(len, a_cells.values()))],
        "P_cell_count_range": [min(deep_counts["P"].values()), max(deep_counts["P"].values())],
        "B_cell_count_range": [min(deep_counts["B"].values()), max(deep_counts["B"].values())],
    }
    return means, audit


def endpoint_theta(records: Sequence[dict[str, Any]], pair_ids: Sequence[int]) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    means, audit = calibrated_means(
        records, pair_ids, subset="inference", replicate="inference"
    )
    logs = np.log2(means)
    theta = CONTRAST_MATRIX @ logs
    return theta, means, {"logs": logs.tolist(), "calibration": audit}


def aa_theta(records: Sequence[dict[str, Any]], pair_ids: Sequence[int]) -> tuple[np.ndarray, dict[str, Any]]:
    means_a, audit_a = calibrated_means(records, pair_ids, subset="aa", replicate="aa-A")
    means_b, audit_b = calibrated_means(records, pair_ids, subset="aa", replicate="aa-B")
    value = np.log2(means_b / means_a)
    return value, {
        "stream_A_means": dict(zip(ARMS, means_a.tolist(), strict=True)),
        "stream_B_means": dict(zip(ARMS, means_b.tolist(), strict=True)),
        "calibration_A": audit_a,
        "calibration_B": audit_b,
    }


def jackknife(
    estimator: Any,
    pair_ids: Sequence[int],
) -> dict[str, Any]:
    pair_ids = list(pair_ids)
    n = len(pair_ids)
    if n < 3:
        raise AnalysisError("pair jackknife requires at least three clusters")
    full, *extra = estimator(pair_ids)
    full = np.asarray(full, dtype=np.float64)
    leave = np.asarray(
        [estimator([pair for pair in pair_ids if pair != omitted])[0] for omitted in pair_ids],
        dtype=np.float64,
    )
    if leave.shape != (n, len(full)) or not np.all(np.isfinite(leave)):
        raise AnalysisError("nonfinite or malformed leave-one-pair estimates")
    pseudo = n * full - (n - 1) * leave
    pseudo_mean = np.mean(pseudo, axis=0)
    influence = pseudo - pseudo_mean
    se = np.sqrt(np.sum(influence * influence, axis=0) / (n * (n - 1)))
    bias = (n - 1) * (np.mean(leave, axis=0) - full)
    return {
        "full": full,
        "extra": extra,
        "leave": leave,
        "pseudovalues": pseudo,
        "influence": influence,
        "se": se,
        "bias": bias,
        "leave_min": np.min(leave, axis=0),
        "leave_max": np.max(leave, axis=0),
    }


def _mix64_array(values: np.ndarray) -> np.ndarray:
    values = values.astype(np.uint64, copy=False)
    values = (values ^ (values >> np.uint64(30))) * np.uint64(0xBF58476D1CE4E5B9)
    values = (values ^ (values >> np.uint64(27))) * np.uint64(0x94D049BB133111EB)
    return values ^ (values >> np.uint64(31))


def rademacher(seed: int, domain: int, draws: int, clusters: int) -> tuple[np.ndarray, str]:
    draw_ids = np.arange(draws, dtype=np.uint64)
    signs = np.empty((draws, clusters), dtype=np.int8)
    for cluster in range(clusters):
        values = _mix64_array(
            np.uint64(seed)
            ^ _mix64_array(draw_ids)
            ^ _mix64_array(np.full(draws, domain, dtype=np.uint64))
            ^ _mix64_array(np.full(draws, cluster, dtype=np.uint64))
        )
        signs[:, cluster] = np.where((values & np.uint64(1)) == 0, -1, 1)
    return signs, hashlib.sha256(signs.tobytes(order="C")).hexdigest()


def restudentized_multiplier_scores(
    influence: np.ndarray, signs: np.ndarray
) -> np.ndarray:
    """Return per-draw, per-contrast cluster-multiplier t statistics."""
    influence = np.asarray(influence, dtype=np.float64)
    signs = np.asarray(signs, dtype=np.float64)
    if (
        influence.ndim != 2
        or signs.ndim != 2
        or signs.shape[1] != influence.shape[0]
        or influence.shape[0] < 3
        or np.any(~np.isfinite(influence))
        or np.any(~np.isfinite(signs))
    ):
        raise AnalysisError("malformed multiplier influence/sign array")
    clusters = influence.shape[0]
    numerator = signs @ influence
    sum_squares = np.sum(influence * influence, axis=0)
    centered_sum_squares = sum_squares[None, :] - numerator * numerator / clusters
    if np.any(~np.isfinite(centered_sum_squares)):
        raise AnalysisError("nonfinite per-draw multiplier studentizer")
    # A centered sum of squares that is zero or numerically indistinguishable
    # from zero is an infinite conservative |T*| cell.  The family is withheld
    # only if such cells reach the frozen critical quantile, rather than
    # because one rare draw contains one zero denominator.
    scale = np.maximum(
        sum_squares[None, :], numerator * numerator / clusters
    )
    tolerance = 64.0 * np.finfo(np.float64).eps * np.maximum(
        scale, np.finfo(np.float64).tiny
    )
    if np.any(centered_sum_squares < -tolerance):
        raise AnalysisError("materially negative per-draw multiplier variance")
    valid = centered_sum_squares > tolerance
    scores = np.full(centered_sum_squares.shape, np.inf, dtype=np.float64)
    scores[valid] = (
        numerator[valid]
        * math.sqrt((clusters - 1) / clusters)
        / np.sqrt(centered_sum_squares[valid])
    )
    if np.any(np.isnan(scores)):
        raise AnalysisError("NaN re-studentized multiplier score")
    return scores


def multiplier_family(
    jack: dict[str, Any],
    *,
    seed: int,
    domain: int,
    draws: int,
    confidence: float,
    ids: Sequence[str],
) -> dict[str, Any]:
    full = np.asarray(jack["full"], dtype=np.float64)
    influence = np.asarray(jack["influence"], dtype=np.float64)
    se = np.asarray(jack["se"], dtype=np.float64)
    if (
        len(ids) != len(full)
        or np.any(~np.isfinite(se))
        or np.any(se <= 0)
        or np.any(~np.isfinite(influence))
    ):
        return {
            "status": "non_estimable_zero_or_nonfinite_jackknife_scale",
            "ids": list(ids),
            "se": se.tolist(),
        }
    signs, sign_hash = rademacher(seed, domain, draws, influence.shape[0])
    scores = restudentized_multiplier_scores(influence, signs)
    maxima = np.max(np.abs(scores), axis=1)
    order = math.ceil((draws + 1) * confidence)
    if not 1 <= order <= draws:
        raise AnalysisError("multiplier critical-value order statistic is out of range")
    critical = float(np.partition(maxima, order - 1)[order - 1])
    if not math.isfinite(critical):
        return {
            "status": "non_estimable_infinite_multiplier_critical_value",
            "ids": list(ids),
            "se": se.tolist(),
            "draws": draws,
            "rademacher_sha256": sign_hash,
            "critical_order_1_based": order,
        }
    lower = full - critical * se
    upper = full + critical * se
    observed_t = np.abs(full / se)
    adjusted_p = np.asarray(
        [(1 + int(np.count_nonzero(maxima >= value))) / (draws + 1) for value in observed_t],
        dtype=np.float64,
    )
    return {
        "status": "estimable",
        "ids": list(ids),
        "draws": draws,
        "confidence": confidence,
        "studentization": "per-draw centered cluster influence re-studentization",
        "studentization_formula": "T*=sum(s_i psi_i)*sqrt((n-1)/n)/sqrt(sum(psi_i^2)-sum(s_i psi_i)^2/n)",
        "rademacher_algorithm": "mix64(seed xor mix64(draw) xor mix64(domain) xor mix64(cluster)); low bit",
        "rademacher_sha256": sign_hash,
        "critical_order_1_based": order,
        "critical_value": critical,
        "estimate": full.tolist(),
        "se": se.tolist(),
        "lower": lower.tolist(),
        "upper": upper.tolist(),
        "adjusted_p": adjusted_p.tolist(),
        "max_cluster_squared_influence_share": (
            np.max(influence * influence, axis=0)
            / np.sum(influence * influence, axis=0)
        ).tolist(),
        "jackknife_bias": np.asarray(jack["bias"]).tolist(),
        "leave_one_pair_min": np.asarray(jack["leave_min"]).tolist(),
        "leave_one_pair_max": np.asarray(jack["leave_max"]).tolist(),
    }


def all_rademacher_signs(clusters: int) -> tuple[np.ndarray, str]:
    if not 1 <= clusters <= 20:
        raise AnalysisError("exact Rademacher enumeration is outside its frozen bound")
    draw_ids = np.arange(1 << clusters, dtype=np.uint32)
    signs = np.empty((1 << clusters, clusters), dtype=np.int8)
    for cluster in range(clusters):
        signs[:, cluster] = np.where(
            ((draw_ids >> np.uint32(cluster)) & np.uint32(1)) == 0,
            -1,
            1,
        )
    return signs, hashlib.sha256(signs.tobytes(order="C")).hexdigest()


def enumerated_multiplier_family(
    jack: dict[str, Any], *, confidence: float, ids: Sequence[str]
) -> dict[str, Any]:
    full = np.asarray(jack["full"], dtype=np.float64)
    influence = np.asarray(jack["influence"], dtype=np.float64)
    se = np.asarray(jack["se"], dtype=np.float64)
    signs, sign_hash = all_rademacher_signs(16)
    draws = len(signs)
    order = math.ceil(draws * confidence)
    if (
        len(ids) != len(full)
        or influence.shape[0] != 16
        or np.any(~np.isfinite(se))
        or np.any(se <= 0)
        or np.any(~np.isfinite(influence))
    ):
        return {
            "status": "non_estimable_zero_or_nonfinite_jackknife_scale",
            "ids": list(ids),
            "se": se.tolist(),
            "draws": draws,
            "rademacher_sha256": sign_hash,
            "critical_order_1_based": order,
        }
    scores = restudentized_multiplier_scores(influence, signs)
    maxima = np.max(np.abs(scores), axis=1)
    if not 1 <= order <= draws:
        raise AnalysisError("enumerated critical-value order statistic is out of range")
    critical = float(np.partition(maxima, order - 1)[order - 1])
    if not math.isfinite(critical):
        return {
            "status": "non_estimable_infinite_multiplier_critical_value",
            "ids": list(ids),
            "se": se.tolist(),
            "draws": draws,
            "rademacher_sha256": sign_hash,
            "critical_order_1_based": order,
        }
    lower = full - critical * se
    upper = full + critical * se
    observed_t = np.abs(full / se)
    adjusted_p = np.asarray(
        [int(np.count_nonzero(maxima >= value)) / draws for value in observed_t],
        dtype=np.float64,
    )
    return {
        "status": "estimable",
        "ids": list(ids),
        "draws": draws,
        "enumeration": "all 2^16 setup-root Rademacher sign vectors in little-endian bit order",
        "enumerated_reference_not_exact_randomization": True,
        "adjusted_p_interpretation": "exhaustively enumerated multiplier-reference adjusted p; not an exact finite-sample randomization p-value",
        "confidence": confidence,
        "studentization": "per-draw centered setup-root influence re-studentization",
        "studentization_formula": "T*=sum(s_i psi_i)*sqrt((n-1)/n)/sqrt(sum(psi_i^2)-sum(s_i psi_i)^2/n)",
        "rademacher_sha256": sign_hash,
        "critical_order_1_based": order,
        "critical_value": critical,
        "estimate": full.tolist(),
        "se": se.tolist(),
        "lower": lower.tolist(),
        "upper": upper.tolist(),
        "adjusted_p": adjusted_p.tolist(),
        "max_setup_root_squared_influence_share": (
            np.max(influence * influence, axis=0)
            / np.sum(influence * influence, axis=0)
        ).tolist(),
        "jackknife_bias": np.asarray(jack["bias"]).tolist(),
        "leave_one_setup_root_min": np.asarray(jack["leave_min"]).tolist(),
        "leave_one_setup_root_max": np.asarray(jack["leave_max"]).tolist(),
    }


def setup_robustness_trigger(
    primary: dict[str, Any], config: dict[str, Any]
) -> dict[str, Any]:
    """Apply the frozen conditional-lane rule without hidden thresholds."""
    threshold = config.get("trigger_abs_bits")
    if (
        isinstance(threshold, bool)
        or not isinstance(threshold, (int, float))
        or not math.isfinite(float(threshold))
        or float(threshold) != 0.5
    ):
        raise AnalysisError("setup-robustness trigger threshold differs")
    rows = primary.get("contrasts")
    if not isinstance(rows, list) or [row.get("id") for row in rows] != list(CONTRAST_IDS):
        raise AnalysisError("primary trigger contrast family differs")
    aa = primary.get("aa_gate")
    aa_pass = isinstance(aa, dict) and aa.get("pass") is True
    modeled = primary.get("modeled_population_inference")
    family = modeled.get("family") if isinstance(modeled, dict) else None
    primary_estimable = isinstance(family, dict) and family.get("status") == "estimable"
    qualifying: list[dict[str, Any]] = []
    if aa_pass and primary_estimable and primary.get("status") == "complete":
        for row in rows:
            lower = row.get("modeled_population_lower_bits")
            upper = row.get("modeled_population_upper_bits")
            estimate = row.get("bits")
            if (
                isinstance(lower, (int, float))
                and not isinstance(lower, bool)
                and isinstance(upper, (int, float))
                and not isinstance(upper, bool)
                and isinstance(estimate, (int, float))
                and not isinstance(estimate, bool)
                and (float(lower) > 0 or float(upper) < 0)
                and abs(float(estimate)) >= float(threshold)
            ):
                qualifying.append(
                    {
                        "id": str(row["id"]),
                        "bits": float(estimate),
                        "simultaneous_lower_bits": float(lower),
                        "simultaneous_upper_bits": float(upper),
                    }
                )
    reason = (
        "aa_gate_failed"
        if not aa_pass
        else "primary_family_non_estimable"
        if not primary_estimable
        else "threshold_met"
        if qualifying
        else "no_primary_contrast_met_threshold"
    )
    return {
        "triggered": bool(qualifying),
        "aa_gate_pass": aa_pass,
        "primary_family_estimable": primary_estimable,
        "trigger_abs_bits": float(threshold),
        "qualifying_contrasts": qualifying,
        "reason": reason,
        "rule": "passing A/A and estimable primary family; any of the nine simultaneous 95% CIs strictly excludes zero and abs(estimate)>=trigger_abs_bits",
    }


def _setup_persistence_assessment(
    config: dict[str, Any],
    trigger: dict[str, Any],
    contrasts: Sequence[dict[str, Any]],
    *,
    family_estimable: bool,
) -> dict[str, Any]:
    expected_rule = {
        "scope": "each primary triggering contrast",
        "directional": "fresh-root simultaneous CI strictly excludes zero in the primary direction",
        "practical": "fresh-root simultaneous CI lies wholly at or beyond +0.5 bit for a positive primary direction or -0.5 bit for a negative primary direction",
        "practical_threshold_abs_bits": 0.5,
        "practical_boundary_inclusive": True,
        "global_categories": ["complete", "partial", "none"],
        "same-sign_point_alone_is_persistence": False,
    }
    if config.get("persistence_rule") != expected_rule:
        raise AnalysisError("setup-robustness persistence rule differs")
    qualifying = trigger.get("qualifying_contrasts")
    if trigger.get("triggered") is not True or not isinstance(qualifying, list) or not qualifying:
        raise AnalysisError("setup-robustness analysis lacks a triggered primary decision")
    if (
        any(not isinstance(row, dict) for row in qualifying)
        or len({row.get("id") for row in qualifying}) != len(qualifying)
        or any(row.get("id") not in CONTRAST_IDS for row in qualifying)
    ):
        raise AnalysisError("setup-robustness triggering contrast set differs")
    followup_by_id = {row.get("id"): row for row in contrasts}
    rows: list[dict[str, Any]] = []
    for primary in qualifying:
        lower = float(primary["simultaneous_lower_bits"])
        upper = float(primary["simultaneous_upper_bits"])
        if lower > 0:
            primary_direction = "positive"
        elif upper < 0:
            primary_direction = "negative"
        else:
            raise AnalysisError("primary triggering interval does not exclude zero")
        followup = followup_by_id.get(primary["id"])
        if not isinstance(followup, dict):
            raise AnalysisError("triggering contrast is absent from robustness family")
        row: dict[str, Any] = {
            "id": primary["id"],
            "primary_bits": float(primary["bits"]),
            "primary_abs_bits": abs(float(primary["bits"])),
            "primary_direction": primary_direction,
            "primary_simultaneous_lower_bits": lower,
            "primary_simultaneous_upper_bits": upper,
            "fresh_root_bits": float(followup["bits"]),
            "fresh_root_abs_bits": abs(float(followup["bits"])),
            "fresh_root_work_ratio": float(followup["work_ratio"]),
            "fresh_root_point_same_direction": (
                float(followup["bits"]) > 0
                if primary_direction == "positive"
                else float(followup["bits"]) < 0
            ),
            "practical_threshold_abs_bits": 0.5,
        }
        if family_estimable:
            fresh_lower = float(followup["simultaneous_lower_bits"])
            fresh_upper = float(followup["simultaneous_upper_bits"])
            fresh_direction = (
                "positive"
                if fresh_lower > 0
                else "negative"
                if fresh_upper < 0
                else "unresolved"
            )
            directional_persists = fresh_direction == primary_direction
            practical_persists = (
                fresh_lower >= 0.5
                if primary_direction == "positive"
                else fresh_upper <= -0.5
            )
            row.update(
                fresh_root_simultaneous_lower_bits=fresh_lower,
                fresh_root_simultaneous_upper_bits=fresh_upper,
                fresh_root_ci_direction=fresh_direction,
                directional_persists=directional_persists,
                practical_persists=practical_persists,
            )
        else:
            row.update(
                fresh_root_ci_direction="non_estimable",
                directional_persists=None,
                practical_persists=None,
            )
        rows.append(row)

    def global_category(field: str) -> str:
        count = sum(row[field] is True for row in rows)
        return "complete" if count == len(rows) else "none" if count == 0 else "partial"

    if not family_estimable:
        status = "non_estimable"
        directional_global = "non_estimable"
        practical_global = "non_estimable"
    else:
        status = "estimable"
        directional_global = global_category("directional_persists")
        practical_global = global_category("practical_persists")
    return {
        "status": status,
        "directional_global": directional_global,
        "practical_global": practical_global,
        "rule": expected_rule,
        "contrasts": rows,
        "point_sign_qualification": "a same-direction point estimate alone does not meet either persistence rule",
        "estimand_qualification": "the follow-up uses a fixed sparse 97-model panel and fresh target/walk streams, unlike the calibrated full-population primary estimand",
        "attribution_limit": "non-persistence cannot by itself identify an original setup-root accident because the panel and target/walk streams also differ from the primary workload",
    }


def analyze_setup_robustness(
    config: dict[str, Any],
    records: Sequence[dict[str, Any]],
    trigger: dict[str, Any],
) -> dict[str, Any]:
    setup_seeds = list(config["setup_seeds"])
    original_setup_seed = config.get("original_setup_seed")
    all_setup_seeds = [*setup_seeds, original_setup_seed]
    if (
        len(setup_seeds) != 16
        or len(set(setup_seeds)) != 16
        or isinstance(original_setup_seed, bool)
        or not isinstance(original_setup_seed, int)
        or original_setup_seed in set(setup_seeds)
        or len(records) != 2176
    ):
        raise AnalysisError("setup-robustness root/record count differs")
    seed_to_root = {seed: root_id for root_id, seed in enumerate(setup_seeds)}
    if {row["setup_seed"] for row in records} != set(all_setup_seeds):
        raise AnalysisError("setup-robustness setup-root set differs")

    def estimate_seeds(retained: set[int]) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
        selected = [row for row in records if row["setup_seed"] in retained]
        if len(selected) != len(retained) * 32 * 4:
            raise AnalysisError("setup-robustness retained record count differs")
        means = np.asarray(
            [
                np.mean([row["walk_ops"] for row in selected if row["arm"] == arm])
                for arm in ARMS
            ],
            dtype=np.float64,
        )
        if np.any(~np.isfinite(means)) or np.any(means <= 0):
            raise AnalysisError("setup-robustness arm mean is invalid")
        logs = np.log2(means)
        return CONTRAST_MATRIX @ logs, means, {"logs": logs.tolist()}

    def estimator(root_ids: Sequence[int]) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
        return estimate_seeds({setup_seeds[root_id] for root_id in root_ids})

    for setup_seed in all_setup_seeds:
        root_rows = [row for row in records if row["setup_seed"] == setup_seed]
        if len(root_rows) != 128 or {row["arm"] for row in root_rows} != set(ARMS):
            raise AnalysisError("setup-robustness root balance differs")
        for panel_slot in range(32):
            block = [row for row in root_rows if row["target_index"] == panel_slot]
            if len(block) != 4 or {row["arm"] for row in block} != set(ARMS):
                raise AnalysisError("setup-robustness root/block pairing differs")
            if len({(row["target_seed"], row["walk_seed"]) for row in block}) != 1:
                raise AnalysisError("setup-robustness target/walk pairing differs")
    first_seed = setup_seeds[0]
    distinct_models_by_arm = {
        arm: len(
            {
                (row["curve_id"], row["b"], row["a2"], row["mode"])
                for row in records
                if row["setup_seed"] == first_seed and row["arm"] == arm
            }
        )
        for arm in ARMS
    }
    if distinct_models_by_arm != {"C": 1, "A": 32, "P": 32, "B": 32}:
        raise AnalysisError("setup-robustness distinct model counts differ")
    for panel_slot in range(32):
        for arm in ARMS:
            identities = {
                (
                    row["curve_id"],
                    row["b"],
                    row["a2"],
                    row["mode"],
                    row["orbit_id"],
                    row["conjugate"],
                    row["target_seed"],
                    row["walk_seed"],
                    row["target_index"],
                )
                for row in records
                if row["pair_id"] == panel_slot and row["arm"] == arm
            }
            if len(identities) != 1:
                raise AnalysisError(
                    f"setup-robustness panel identity changes: {panel_slot}/{arm}"
                )

    jack = jackknife(estimator, list(range(16)))
    family = enumerated_multiplier_family(
        jack, confidence=float(config["family_confidence"]), ids=CONTRAST_IDS
    )
    if (
        config.get("sign_vectors") != 65536
        or config.get("critical_rank_1_based") != 62260
        or family.get("draws") != 65536
        or family.get("rademacher_sha256") != config.get("sign_vectors_sha256")
        or (
            family.get("status") == "estimable"
            and family.get("critical_order_1_based") != 62260
        )
    ):
        raise AnalysisError("setup-robustness exact-sign inference contract differs")
    family["inference_scope"] = "16 fresh SHA-256-derived setup roots only"
    family["inference_kind"] = "n=16 model-based/asymptotic cluster-multiplier reference"
    family["finite_sample_exact_randomization_inference"] = False
    family["enumeration_qualification"] = (
        "all 2^16 signs are enumerated, eliminating multiplier Monte Carlo error only"
    )
    root_rows: list[dict[str, Any]] = []
    for root_id, setup_seed in enumerate(setup_seeds):
        theta, means, _ = estimator([root_id])
        root_rows.append(
            {
                "setup_root_id": root_id,
                "setup_seed": setup_seed,
                "role": "fresh_inferential_root",
                "arm_arithmetic_mean_walk_ops": dict(
                    zip(ARMS, means.tolist(), strict=True)
                ),
                "contrasts_bits": dict(
                    zip(CONTRAST_IDS, theta.tolist(), strict=True)
                ),
            }
        )
    contrasts: list[dict[str, Any]] = []
    full = np.asarray(jack["full"], dtype=np.float64)
    for index, contrast_id in enumerate(CONTRAST_IDS):
        row: dict[str, Any] = {
            "id": contrast_id,
            "bits": float(full[index]),
            "work_ratio": float(2.0 ** full[index]),
        }
        if family["status"] == "estimable":
            row.update(
                simultaneous_lower_bits=float(family["lower"][index]),
                simultaneous_upper_bits=float(family["upper"][index]),
                setup_root_jackknife_se_bits=float(family["se"][index]),
                enumerated_multiplier_reference_adjusted_p=float(
                    family["adjusted_p"][index]
                ),
            )
        contrasts.append(row)
    persistence = _setup_persistence_assessment(
        config,
        trigger,
        contrasts,
        family_estimable=family["status"] == "estimable",
    )
    bridge_theta, bridge_means, _ = estimate_seeds({original_setup_seed})
    bridge_contrasts = [
        {
            "id": contrast_id,
            "original_root_bits": float(bridge_theta[index]),
            "original_root_work_ratio": float(2.0 ** bridge_theta[index]),
            "fresh_root_modeled_estimate_bits": float(full[index]),
            "original_minus_fresh_bits": float(bridge_theta[index] - full[index]),
        }
        for index, contrast_id in enumerate(CONTRAST_IDS)
    ]
    return {
        "schema": "m51-deep-rho-setup-robustness-analysis/v1",
        "status": "complete" if family["status"] == "estimable" else "non_estimable",
        "counts": {
            "records": len(records),
            "fresh_inferential_setup_root_clusters": 16,
            "descriptive_original_root_bridges": 1,
            "total_setup_roots": 17,
            "blocks_per_root": 32,
            "panel_slots_per_arm": 32,
            "distinct_models_by_arm": distinct_models_by_arm,
            "distinct_models_total": 97,
        },
        "family": family,
        "contrasts": contrasts,
        "persistence_assessment": persistence,
        "per_setup_root": root_rows,
        "per_setup_root_contrast_distributions": {
            contrast_id: summarize(
                row["contrasts_bits"][contrast_id] for row in root_rows
            )
            for contrast_id in CONTRAST_IDS
        },
        "descriptive_original_root_bridge": {
            "setup_seed": original_setup_seed,
            "role": "trigger-conditioned noninferential bridge",
            "arm_arithmetic_mean_walk_ops": dict(
                zip(ARMS, bridge_means.tolist(), strict=True)
            ),
            "contrasts": bridge_contrasts,
            "qualification": "descriptive matched bridge on the identical follow-up panel, targets, and walk streams; excluded from the n=16 family and assigned no confidence interval or p-value",
        },
        "setup_root_sampling_model": config["setup_root_sampling_model"],
        "claim_limit": config["claim_limit"],
        "setup_seed_to_root_id": {
            str(seed): seed_to_root[seed] for seed in setup_seeds
        },
    }


def summarize(values: Iterable[float]) -> dict[str, float | int]:
    data = np.asarray(list(values), dtype=np.float64)
    if data.size == 0 or np.any(~np.isfinite(data)):
        raise AnalysisError("cannot summarize empty/nonfinite values")
    return {
        "n": int(data.size),
        "mean": float(np.mean(data)),
        "sd": float(np.std(data, ddof=1)) if data.size > 1 else 0.0,
        "q05": float(np.quantile(data, 0.05)),
        "q25": float(np.quantile(data, 0.25)),
        "median": float(np.quantile(data, 0.50)),
        "q75": float(np.quantile(data, 0.75)),
        "q95": float(np.quantile(data, 0.95)),
        "min": float(np.min(data)),
        "max": float(np.max(data)),
    }


def descriptive_heterogeneity(records: Sequence[dict[str, Any]]) -> dict[str, Any]:
    """Expose pair/model dispersion without adding an inferential family."""
    inference = [
        row
        for row in records
        if row["subset"] == "inference" and row["replicate"] == "inference"
    ]
    if len(inference) != INFERENCE_BLOCKS * len(ARMS):
        raise AnalysisError("descriptive inference record count differs")

    pair_rows: list[dict[str, Any]] = []
    for pair_id in range(PAIR_COUNT):
        selected = [row for row in inference if row["pair_id"] == pair_id]
        means = np.asarray(
            [
                np.mean([row["walk_ops"] for row in selected if row["arm"] == arm])
                for arm in ARMS
            ],
            dtype=np.float64,
        )
        if np.any(~np.isfinite(means)) or np.any(means <= 0):
            raise AnalysisError(f"pair {pair_id}: invalid descriptive mean")
        theta = CONTRAST_MATRIX @ np.log2(means)
        pair_rows.append(
            {
                "pair_id": pair_id,
                "records_per_arm": len(selected) // len(ARMS),
                "arm_equal_row_weight_means": dict(
                    zip(ARMS, means.tolist(), strict=True)
                ),
                "contrasts_bits": dict(
                    zip(CONTRAST_IDS, theta.tolist(), strict=True)
                ),
            }
        )

    model_rows: list[dict[str, Any]] = []
    for arm in ARMS:
        cells: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
        for row in inference:
            if row["arm"] != arm:
                continue
            if arm == "C":
                key = ("C",)
            elif arm == "A":
                key = (int(row["orbit_id"]), int(row["conjugate"]))
            else:
                key = (int(row["pair_id"]), int(row["conjugate"]))
            cells[key].append(row)
        for key, values in sorted(cells.items()):
            b_values = {int(row["b"]) for row in values}
            curve_ids = {str(row["curve_id"]) for row in values}
            if len(b_values) != 1 or len(curve_ids) != 1:
                raise AnalysisError(f"{arm} descriptive model identity drift")
            work = [float(row["walk_ops"]) for row in values]
            identity: dict[str, Any] = {"arm": arm}
            if arm == "A":
                identity.update(orbit_id=key[0], conjugate=key[1])
            elif arm in ("P", "B"):
                identity.update(pair_id=key[0], edge_conjugate=key[1])
            model_rows.append(
                {
                    **identity,
                    "curve_id": next(iter(curve_ids)),
                    "b": next(iter(b_values)),
                    "records": len(values),
                    "mean_walk_ops": float(np.mean(work)),
                    "min_walk_ops": float(np.min(work)),
                    "max_walk_ops": float(np.max(work)),
                }
            )

    common_means = np.asarray(
        [
            np.mean([row["walk_ops"] for row in inference if row["arm"] == arm])
            for arm in ARMS
        ],
        dtype=np.float64,
    )
    common_theta = CONTRAST_MATRIX @ np.log2(common_means)
    return {
        "scope": "descriptive only; no confidence interval or decision label",
        "per_pair_equal_row_weight": pair_rows,
        "per_pair_contrast_distributions": {
            contrast_id: summarize(
                row["contrasts_bits"][contrast_id] for row in pair_rows
            )
            for contrast_id in CONTRAST_IDS
        },
        "per_model_cells": model_rows,
        "per_model_cell_counts": {
            arm: sum(row["arm"] == arm for row in model_rows) for arm in ARMS
        },
        "common_row_weight_sensitivity": {
            "arm_arithmetic_mean_walk_ops": dict(
                zip(ARMS, common_means.tolist(), strict=True)
            ),
            "contrasts_bits": dict(
                zip(CONTRAST_IDS, common_theta.tolist(), strict=True)
            ),
            "qualification": "all four arms give each block equal weight; this is fully target/stream paired but is not in the primary inferential family",
        },
        "primary_calibration_pairing": {
            "C_row_weight_ratio_to_C": [1.0, 1.0],
            "A_row_weight_ratio_to_C": [0.9411764705882353, 1.0267379679144386],
            "P_B_row_weight_ratio_to_C": [0.9411764705882353, 1.8823529411764706],
            "exactly_weight_paired_contrast": "B-P",
            "qualification": "shared target and walk streams are common random numbers for every arm, but unequal calibration weights prevent exact target pairing except B-P",
        },
    }


def analyze_records(spec: dict[str, Any], records: list[dict[str, Any]]) -> dict[str, Any]:
    pair_ids = list(range(PAIR_COUNT))
    main_jack = jackknife(lambda ids: endpoint_theta(records, ids), pair_ids)
    main_family = multiplier_family(
        main_jack,
        seed=int(spec["seeds"]["multiplier_root"]),
        domain=int(spec["contrast_family"]["multiplier_domain"]),
        draws=int(spec["contrast_family"]["resamples"]),
        confidence=float(spec["contrast_family"]["family_confidence"]),
        ids=CONTRAST_IDS,
    )
    aa_jack = jackknife(lambda ids: aa_theta(records, ids), pair_ids)
    aa_family = multiplier_family(
        aa_jack,
        seed=int(spec["seeds"]["multiplier_root"]),
        domain=int(spec["aa_gate"]["multiplier_domain"]),
        draws=int(spec["aa_gate"]["resamples"]),
        confidence=float(spec["aa_gate"]["family_confidence"]),
        ids=ARMS,
    )
    aa_margin = float(spec["aa_gate"]["margin_bits"])
    aa_pass = (
        aa_family["status"] == "estimable"
        and all(lower >= -aa_margin and upper <= aa_margin for lower, upper in zip(aa_family["lower"], aa_family["upper"], strict=True))
    )
    aa_family["margin_bits"] = aa_margin
    aa_family["pass"] = aa_pass
    aa_family["gate_status"] = "PASS" if aa_pass else "A/A_ALERT"

    selected_theta = np.asarray(main_jack["full"], dtype=np.float64)
    selected_means = np.asarray(main_jack["extra"][0], dtype=np.float64)
    selected_meta = main_jack["extra"][1]
    contrasts: list[dict[str, Any]] = []
    for index, contrast_id in enumerate(CONTRAST_IDS):
        row: dict[str, Any] = {
            "id": contrast_id,
            "bits": float(selected_theta[index]),
            "work_ratio": float(2.0 ** selected_theta[index]),
            "scope": "selected-32 calibrated endpoint association",
            "causal": False,
        }
        if main_family["status"] == "estimable":
            lower = float(main_family["lower"][index])
            upper = float(main_family["upper"][index])
            row.update(
                {
                    "modeled_population_lower_bits": lower,
                    "modeled_population_upper_bits": upper,
                    "modeled_population_se_bits": float(main_family["se"][index]),
                    "maxT_adjusted_p": float(main_family["adjusted_p"][index]),
                }
            )
            if aa_pass:
                row["direction"] = "positive" if lower > 0 else "negative" if upper < 0 else "unresolved"
                if index < 6:
                    margin = float(spec["contrast_family"]["pairwise_equivalence_margin_bits"])
                    row["equivalent_within_0.10_bit"] = lower >= -margin and upper <= margin
            else:
                row["decision_label"] = "WITHHELD_AA_ALERT"
        else:
            row["decision_label"] = "WITHHELD_NON_ESTIMABLE"
        contrasts.append(row)

    interaction = contrasts[CONTRAST_IDS.index("I")]
    ordinary_did: dict[str, Any] = {
        "id": "2I",
        "formula": "xC-xA-xP+xB",
        "derived_from_family_member": "I=(xC-xA-xP+xB)/2",
        "bits": 2.0 * float(interaction["bits"]),
        "work_ratio": float(2.0 ** (2.0 * float(interaction["bits"]))),
        "scope": interaction["scope"],
        "causal": False,
    }
    if "modeled_population_lower_bits" in interaction:
        ordinary_did.update(
            modeled_population_lower_bits=2.0
            * float(interaction["modeled_population_lower_bits"]),
            modeled_population_upper_bits=2.0
            * float(interaction["modeled_population_upper_bits"]),
            modeled_population_se_bits=2.0
            * float(interaction["modeled_population_se_bits"]),
            maxT_adjusted_p=float(interaction["maxT_adjusted_p"]),
        )
    if "direction" in interaction:
        ordinary_did["direction"] = interaction["direction"]
    if "decision_label" in interaction:
        ordinary_did["decision_label"] = interaction["decision_label"]

    summaries: dict[str, Any] = {}
    for subset, replicate in (("inference", "inference"), ("aa", "aa-A"), ("aa", "aa-B")):
        key = f"{subset}:{replicate}"
        summaries[key] = {
            arm: {
                metric: summarize(
                    row[metric]
                    for row in records
                    if row["subset"] == subset and row["replicate"] == replicate and row["arm"] == arm
                )
                for metric in SUMMARY_FIELDS
            }
            for arm in ARMS
        }

    return {
        "schema": "m51-deep-rho-analysis/v1",
        "status": (
            "complete"
            if aa_pass and main_family["status"] == "estimable"
            else "aa_alert_labels_withheld"
            if not aa_pass
            else "main_family_non_estimable"
        ),
        "counts": {
            "records": len(records),
            "inference_solves": sum(row["subset"] == "inference" for row in records),
            "aa_solves": sum(row["subset"] == "aa" for row in records),
            "pair_clusters": 32,
        },
        "selected_32_estimand": {
            "arm_calibrated_arithmetic_mean_walk_ops": dict(zip(ARMS, selected_means.tolist(), strict=True)),
            "arm_log2_means": dict(zip(ARMS, selected_meta["logs"], strict=True)),
            "calibration_audit": selected_meta["calibration"],
            "interpretation": "fixed realized selected endpoint set and executed target/walk distribution; no pair-jackknife CI is claimed for this fixed set",
        },
        "modeled_population_inference": {
            "conditional_on": "discovery keyed-modeled-PRP exchangeability, valid no-backfill first-32 selection, and pair-cluster asymptotics with 32 PSUs",
            "population": {
                "parent_orbits": 2369,
                "bottom_orbits": 644368,
                "pilot_parent_fibers_excluded": 1,
            },
            "one_child_per_parent_limitation": "within-parent child-orbit heterogeneity is not separately identified",
            "method": "delete-one-pair jackknife plus per-draw re-studentized Rademacher max-|T| multiplier",
            "family": main_family,
        },
        "contrasts": contrasts,
        "ordinary_difference_in_differences": ordinary_did,
        "aa_gate": aa_family,
        "descriptive_heterogeneity": descriptive_heterogeneity(records),
        "distribution_summaries": summaries,
        "claim_boundary": {
            "label": "endpoint-native lattice associations; noncausal",
            "weak_curve": False,
            "transfer": False,
            "end_to_end": False,
            "complete_named_levels": False,
        },
    }


def write_exclusive(path: Path, value: dict[str, Any]) -> None:
    if path.exists() or path.is_symlink():
        raise FileExistsError(f"refusing to overwrite {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_name(path.name + ".partial")
    with partial.open("x") as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(partial, path)


def canonical_plan_sha256(records: list[dict[str, Any]]) -> str:
    encoded = json.dumps(
        records, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def validate_runtime_provenance(
    run: Path, spec: dict[str, Any], frozen_entries: dict[str, str]
) -> dict[str, Any]:
    provenance = load_json(run / "provenance.json")
    host = provenance.get("host")
    runtime = host.get("analysis_runtime") if isinstance(host, dict) else None
    if not isinstance(runtime, dict) or runtime.get("schema") != "m51-deep-rho-analysis-runtime/v1":
        raise AnalysisError("analysis runtime provenance is absent")
    if runtime.get("environment") != spec["execution"]["analysis_environment"]:
        raise AnalysisError("analysis runtime environment differs")
    command = runtime.get("command")
    flags = runtime.get("python", {}).get("flags")
    if (
        not isinstance(command, list)
        or "-I" not in command
        or "-B" not in command
        or not isinstance(flags, dict)
        or flags.get("isolated") != 1
        or flags.get("dont_write_bytecode") != 1
        or flags.get("ignore_environment") != 1
        or flags.get("no_user_site") != 1
    ):
        raise AnalysisError("analysis Python isolation provenance differs")
    local = runtime.get("local_source")
    if not isinstance(local, dict) or local != {
        "design_sha256": frozen_entries["design.py"],
        "analyze_sha256": frozen_entries["analyze.py"],
    }:
        raise AnalysisError("analysis local-source provenance differs")
    python = runtime.get("python")
    numpy = runtime.get("numpy")
    mapped = numpy.get("mapped_numerical_objects") if isinstance(numpy, dict) else None
    if (
        not isinstance(python, dict)
        or not valid_sha256(python.get("executable_sha256"))
        or not isinstance(numpy, dict)
        or not isinstance(numpy.get("version"), str)
        or not valid_sha256(numpy.get("package_init_sha256"))
        or not valid_sha256(numpy.get("core_extension_sha256"))
        or not isinstance(numpy.get("build_config"), dict)
        or not isinstance(mapped, list)
        or not mapped
        or any(
            not isinstance(row, dict)
            or not isinstance(row.get("path"), str)
            or not valid_sha256(row.get("sha256"))
            for row in mapped
        )
    ):
        raise AnalysisError("analysis NumPy/BLAS provenance differs")
    return runtime


def current_analysis_runtime_receipt() -> dict[str, Any]:
    numpy_init = Path(np.__file__).resolve(strict=True)
    numpy_core = Path(np._core._multiarray_umath.__file__).resolve(strict=True)
    mapped: dict[str, str] = {}
    for line in Path("/proc/self/maps").read_text().splitlines():
        fields = line.split()
        if len(fields) < 6 or not fields[-1].startswith("/"):
            continue
        raw_path = fields[-1]
        if not any(
            token in raw_path.lower()
            for token in ("numpy", "openblas", "lapack", "libblas", "libgomp")
        ):
            continue
        path = Path(raw_path)
        if path.is_file() and not path.is_symlink():
            resolved = path.resolve(strict=True)
            mapped[str(resolved)] = sha256_file(resolved)
    return {
        "schema": "m51-deep-rho-analysis-runtime/v1",
        "command": list(getattr(sys, "orig_argv", sys.argv)),
        "argv": list(sys.argv),
        "environment": dict(ANALYSIS_ENV),
        "python": {
            "version": sys.version,
            "executable": str(Path(sys.executable).resolve(strict=True)),
            "executable_sha256": sha256_file(Path(sys.executable).resolve(strict=True)),
            "flags": {
                "isolated": sys.flags.isolated,
                "dont_write_bytecode": sys.flags.dont_write_bytecode,
                "ignore_environment": sys.flags.ignore_environment,
                "no_user_site": sys.flags.no_user_site,
            },
        },
        "numpy": {
            "version": np.__version__,
            "package_init": str(numpy_init),
            "package_init_sha256": sha256_file(numpy_init),
            "core_extension": str(numpy_core),
            "core_extension_sha256": sha256_file(numpy_core),
            "build_config": json.loads(
                json.dumps(getattr(np.__config__, "CONFIG", None), default=str)
            ),
            "mapped_numerical_objects": [
                {"path": path, "sha256": digest}
                for path, digest in sorted(mapped.items())
            ],
        },
        "local_source": {
            "design_sha256": _design_binding[1] if _design_binding else None,
            "analyze_sha256": sha256_file(Path(__file__)),
        },
    }


def validate_build_integrity(run: Path) -> dict[str, Any]:
    build = load_json(run / "build/build-receipt.json")
    receipts = build.get("receipts")
    if (
        "-static" not in build.get("compile_flags", [])
        or not isinstance(receipts, list)
        or len(receipts) != 2
    ):
        raise AnalysisError("static build receipt differs")
    for receipt in receipts:
        certificate = receipt.get("static_elf") if isinstance(receipt, dict) else None
        if (
            not isinstance(certificate, dict)
            or certificate.get("pt_dynamic_present") is not False
            or certificate.get("pt_interp_present") is not False
            or receipt.get("environment") != CHILD_ENV
            or receipt.get("residual_group_cleaned") is not False
            or receipt.get("exit_status") != 0
        ):
            raise AnalysisError("static build/runtime integrity certificate differs")
    for name, field in (
        ("rho-batch", "batch_binary_sha256"),
        ("rho-selftest", "selftest_binary_sha256"),
    ):
        path = run / "build" / name
        data = path.read_bytes()
        if (
            path.is_symlink()
            or not path.is_file()
            or build.get(field) != hashlib.sha256(data).hexdigest()
            or len(data) < 64
            or data[:4] != b"\x7fELF"
            or data[4] != 2
            or data[5] != 1
        ):
            raise AnalysisError(f"static binary binding differs: {name}")
        offset = struct.unpack_from("<Q", data, 32)[0]
        entry_size = struct.unpack_from("<H", data, 54)[0]
        count = struct.unpack_from("<H", data, 56)[0]
        if (
            entry_size < 56
            or count == 0
            or offset + entry_size * count > len(data)
            or any(
                struct.unpack_from("<I", data, offset + index * entry_size)[0]
                in (2, 3)
                for index in range(count)
            )
        ):
            raise AnalysisError(f"binary has PT_DYNAMIC/PT_INTERP or malformed headers: {name}")
    return build


def validate_rng_crosscheck(run: Path) -> dict[str, Any]:
    summary = load_json(run / "rng_vectors.json")
    if (
        summary.get("schema") != "m51-deep-rho-rng-crosscheck/v1"
        or len(RNG_TEST_VECTORS) != 8
        or summary.get("count") != len(RNG_TEST_VECTORS)
        or summary.get("binary_sha256") != sha256_file(run / "build/rho-batch")
        or not isinstance(summary.get("vectors"), list)
        or len(summary["vectors"]) != 8
    ):
        raise AnalysisError("RNG cross-language summary differs")
    for index, (certificate, vector) in enumerate(
        zip(summary["vectors"], RNG_TEST_VECTORS, strict=True)
    ):
        target_seed, walk_seed, target_index, scalar, stream = vector
        expected_certificate = {
            "index": index,
            "target_seed": target_seed,
            "walk_seed": walk_seed,
            "target_index": target_index,
            "target_scalar": scalar,
            "walk_stream_seed": stream,
        }
        if any(certificate.get(key) != value for key, value in expected_certificate.items()):
            raise AnalysisError(f"RNG vector certificate differs: {index}")
        directory = run / "rng-vectors"
        stdout_path = directory / f"vector-{index:02d}.stdout"
        stderr_path = directory / f"vector-{index:02d}.stderr"
        receipt_path = directory / f"vector-{index:02d}.receipt.json"
        receipt = load_json(receipt_path)
        expected_line = (
            f"target_seed={target_seed} walk_seed={walk_seed} "
            f"target_index={target_index} target_scalar={scalar} "
            f"walk_stream_seed={stream}\n"
        )
        if (
            certificate.get("stdout_sha256") != sha256_file(stdout_path)
            or certificate.get("receipt_sha256") != sha256_file(receipt_path)
            or stdout_path.read_text() != expected_line
            or stderr_path.stat().st_size != 0
            or receipt.get("stdout_sha256") != sha256_file(stdout_path)
            or receipt.get("stderr_sha256") != sha256_file(stderr_path)
            or receipt.get("environment") != CHILD_ENV
            or receipt.get("command")
            != [
                str(run / "build/rho-batch"),
                "rng-vector",
                str(target_seed),
                str(walk_seed),
                str(target_index),
            ]
            or receipt.get("cwd") != str(run / "build")
            or receipt.get("exit_status") != 0
            or receipt.get("timed_out") is not False
            or receipt.get("cancelled") is not False
            or receipt.get("residual_group_cleaned") is not False
        ):
            raise AnalysisError(f"RNG cross-language execution differs: {index}")
    return summary


def validate_setup_robustness_phase(
    run: Path,
    spec: dict[str, Any],
    pairs: list[Any],
    f271: dict[int, int],
    decision_sha256: str,
    primary_records_sha256: str,
    preflight_plan_sha256: str,
    trigger: dict[str, Any],
    outer_summary: dict[str, Any],
) -> dict[str, Any]:
    phase = run / "setup_robustness"
    _entries, phase_tree_hash = verify_tree(phase)
    if outer_summary.get("phase_manifest_sha256") != phase_tree_hash:
        raise AnalysisError("setup-robustness phase manifest binding differs")
    phase_manifest = load_json(phase / "run_manifest.json")
    if (
        phase_manifest.get("schema") != "m51-deep-rho-setup-robustness-run/v1"
        or phase_manifest.get("scientific") is not True
        or phase_manifest.get("trigger_decision_sha256") != decision_sha256
        or phase_manifest.get("primary_records_sha256") != primary_records_sha256
        or phase_manifest.get("preflight_plan_sha256") != preflight_plan_sha256
        or phase_manifest.get("records") != 2176
        or phase_manifest.get("fresh_inferential_setup_root_clusters") != 16
        or phase_manifest.get("descriptive_original_root_bridges") != 1
        or phase_manifest.get("total_setup_roots") != 17
        or phase_manifest.get("blocks_per_setup_root") != 32
        or phase_manifest.get("distinct_models") != 97
        or phase_manifest.get("execution_units") != 1649
        or phase_manifest.get("execution_status") != "complete"
        or outer_summary.get("run_manifest_sha256")
        != sha256_file(phase / "run_manifest.json")
    ):
        raise AnalysisError("setup-robustness phase manifest differs")
    expected_plan = build_setup_robustness_plan(
        pairs, f271, spec["setup_robustness"]
    )
    if canonical_plan_sha256(expected_plan) != preflight_plan_sha256:
        raise AnalysisError("setup-robustness plan differs from preflight binding")
    materialized = parse_plan_csv(phase / "record_plan.csv")
    if materialized != expected_plan:
        raise AnalysisError("setup-robustness materialized plan differs")
    records = parse_records(phase / "records.csv")
    validate_records_against_plan(records, expected_plan, context="setup robustness")
    if (
        phase_manifest.get("record_plan_sha256")
        != sha256_file(phase / "record_plan.csv")
        or phase_manifest.get("records_sha256") != sha256_file(phase / "records.csv")
        or phase_manifest.get("binary_sha256") != sha256_file(run / "build/rho-batch")
    ):
        raise AnalysisError("setup-robustness plan/record/binary binding differs")
    costs = validate_setup_and_process_costs(
        phase,
        phase_manifest,
        records=records,
        robustness_plan=expected_plan,
        setup_seeds=[
            *spec["setup_robustness"]["setup_seeds"],
            spec["setup_robustness"]["original_setup_seed"],
        ],
    )
    if phase_manifest.get("setup_certificate_audit") != costs.get(
        "setup_certificate_audit"
    ):
        raise AnalysisError("setup-robustness certificate audit differs")
    recomputed = analyze_setup_robustness(
        spec["setup_robustness"], records, trigger
    )
    stored = load_json(phase / "analysis.json")
    if stored != recomputed or phase_manifest.get("analysis_sha256") != sha256_file(
        phase / "analysis.json"
    ):
        raise AnalysisError("setup-robustness analysis differs from recomputation")
    post_seal_recovery = outer_summary.get("post_seal_recovery")
    if post_seal_recovery is not None and (
        not isinstance(post_seal_recovery, dict)
        or set(post_seal_recovery) != {
            "verified_on_disk",
            "interrupted_exception",
        }
        or post_seal_recovery.get("verified_on_disk") is not True
        or not isinstance(post_seal_recovery.get("interrupted_exception"), str)
        or not post_seal_recovery["interrupted_exception"]
    ):
        raise AnalysisError("post-seal recovery receipt differs")
    if (
        outer_summary.get("analysis_sha256") != sha256_file(phase / "analysis.json")
        or outer_summary.get("triggered") is not True
        or outer_summary.get("records") != 2176
        or phase_manifest.get("analysis_status") != recomputed["status"]
        or outer_summary.get("analysis_status") != recomputed["status"]
        or outer_summary.get("status") != recomputed["status"]
        or outer_summary.get("execution_status") != "complete"
    ):
        raise AnalysisError("outer setup-robustness analysis binding differs")
    result = {
        "status": recomputed["status"],
        "execution_status": "complete",
        "analysis_status": recomputed["status"],
        "analysis": recomputed,
        "setup_and_process_costs": costs,
        "phase_tree_manifest_sha256": phase_tree_hash,
    }
    if post_seal_recovery is not None:
        result["post_seal_recovery"] = post_seal_recovery
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    run = args.run.resolve(strict=True)
    out = args.out.resolve(strict=False)
    if out == run or run in out.parents:
        raise AnalysisError("analysis output must not mutate the sealed run tree")
    _tree_entries, tree_manifest_hash = verify_tree(run)
    frozen_entries, frozen_manifest_hash = verify_frozen_snapshot(run)
    bind_design(run / "inputs/design.py", frozen_entries["design.py"])
    session = load_json(run / "session.json")
    manifest = load_json(run / "run_manifest.json")
    allowed_status = {
        "complete",
        "primary_complete_robustness_failed",
        "primary_complete_robustness_non_estimable",
    }
    if session.get("status") not in allowed_status or session.get("scientific") is not True:
        raise AnalysisError("run session has no independently completed primary phase")
    if (
        session.get("manifest") != "MANIFEST.sha256"
        or session.get("run_manifest_sha256") != sha256_file(run / "run_manifest.json")
        or session.get("records") != 20480
        or session.get("total_records") != manifest.get("total_records")
    ):
        raise AnalysisError("terminal session/run-manifest binding differs")
    if (
        manifest.get("schema") != "m51-deep-rho-run-manifest/v1"
        or manifest.get("scientific") is not True
        or manifest.get("selftests") != 17
        or manifest.get("rng_vectors") != 8
    ):
        raise AnalysisError("outer run manifest differs")
    if manifest.get("frozen_manifest_sha256") != frozen_manifest_hash:
        raise AnalysisError("run manifest frozen-input binding differs")
    primary = run / "primary"
    _primary_entries, primary_tree_hash = verify_tree(primary)
    primary_summary = manifest.get("primary")
    primary_manifest = load_json(primary / "run_manifest.json")
    if (
        not isinstance(primary_summary, dict)
        or primary_summary.get("tree_manifest_sha256") != primary_tree_hash
        or primary_summary.get("run_manifest_sha256")
        != sha256_file(primary / "run_manifest.json")
        or primary_summary.get("records_sha256") != sha256_file(primary / "records.csv")
        or primary_summary.get("analysis_sha256") != sha256_file(primary / "analysis.json")
        or primary_summary.get("records") != 20480
        or primary_summary.get("execution_units") != 3556
        or primary_summary.get("distinct_models") != 3537
        or primary_manifest.get("schema") != "m51-deep-rho-primary-run/v1"
        or primary_manifest.get("scientific") is not True
        or primary_manifest.get("records") != 20480
        or primary_manifest.get("inference_records") != 12288
        or primary_manifest.get("aa_records") != 8192
        or primary_manifest.get("execution_units") != 3556
        or primary_manifest.get("distinct_models") != 3537
    ):
        raise AnalysisError("independently sealed primary phase binding differs")
    spec, records, primary_meta = validate_plan_and_records(run, primary)
    if spec["setup_robustness"].get("original_setup_seed") != spec["seeds"].get(
        "setup_root"
    ):
        raise AnalysisError("descriptive bridge is not the primary setup root")
    if (
        primary_manifest.get("records_sha256") != sha256_file(primary / "records.csv")
        or primary_manifest.get("analysis_sha256") != sha256_file(primary / "analysis.json")
        or primary_manifest.get("record_plan_sha256")
        != sha256_file(primary / "record_plan.csv")
    ):
        raise AnalysisError("primary phase record/analysis/plan hash differs")
    if (
        manifest.get("selection_binding_sha256")
        != sha256_file(run / "inputs/deep_selection.json")
        or manifest.get("schedule_sha256") != sha256_file(run / "inputs/schedule.csv")
        or manifest.get("rho_source_sha256") != sha256_file(run / "inputs/rho.c")
        or manifest.get("batch_driver_sha256")
        != sha256_file(run / "inputs/batch_driver.c")
        or manifest.get("binary_sha256") != sha256_file(run / "build/rho-batch")
        or primary_manifest.get("selection_binding_sha256")
        != sha256_file(run / "inputs/deep_selection.json")
        or primary_manifest.get("schedule_sha256")
        != sha256_file(run / "inputs/schedule.csv")
        or primary_manifest.get("rho_source_sha256")
        != sha256_file(run / "inputs/rho.c")
        or primary_manifest.get("batch_driver_sha256")
        != sha256_file(run / "inputs/batch_driver.c")
        or primary_manifest.get("binary_sha256") != sha256_file(run / "build/rho-batch")
    ):
        raise AnalysisError("run manifest source/selection/plan/binary binding differs")
    runtime_provenance = validate_runtime_provenance(run, spec, frozen_entries)
    build_integrity = validate_build_integrity(run)
    rng_crosscheck = validate_rng_crosscheck(run)
    setup_and_process_costs = validate_setup_and_process_costs(
        primary, primary_manifest, records=records
    )
    analysis = analyze_records(spec, records)
    if load_json(primary / "analysis.json") != analysis:
        raise AnalysisError("sealed primary trigger analysis differs from recomputation")

    robustness_plan = build_setup_robustness_plan(
        primary_meta["pairs"],
        read_f271_orbits(run / "inputs/floor271_orbits.csv"),
        spec["setup_robustness"],
    )
    preflight_plan_sha256 = canonical_plan_sha256(robustness_plan)
    preflight = load_json(run / "setup_robustness_preflight.json")
    expected_preflight = {
        "schema": "m51-deep-rho-setup-robustness-preflight/v1",
        "validated_before_primary_execution": True,
        "canonical_plan_sha256": preflight_plan_sha256,
        "records": 2176,
        "panel_slots_per_arm": 32,
        "distinct_models": 97,
        "execution_units": 1649,
        "fresh_inferential_setup_roots": 16,
        "descriptive_original_root_bridges": 1,
        "total_setup_roots": 17,
    }
    if (
        preflight != expected_preflight
        or manifest.get("setup_robustness_preflight_sha256")
        != sha256_file(run / "setup_robustness_preflight.json")
    ):
        raise AnalysisError("setup-robustness preflight differs")

    trigger = setup_robustness_trigger(analysis, spec["setup_robustness"])
    decision_path = run / "setup_robustness_decision.json"
    decision = load_json(decision_path)
    decision_fixed = {
        "schema": "m51-deep-rho-setup-robustness-decision/v1",
        "primary_tree_manifest_sha256": primary_tree_hash,
        "primary_run_manifest_sha256": sha256_file(primary / "run_manifest.json"),
        "primary_records_sha256": sha256_file(primary / "records.csv"),
        "primary_analysis_sha256": sha256_file(primary / "analysis.json"),
        "preflight_plan_sha256": preflight_plan_sha256,
        "frozen_manifest_sha256": frozen_manifest_hash,
        **trigger,
    }
    if (
        set(decision) != {*decision_fixed, "created_utc"}
        or any(decision.get(key) != value for key, value in decision_fixed.items())
        or not isinstance(decision.get("created_utc"), str)
        or manifest.get("setup_robustness_decision_sha256")
        != sha256_file(decision_path)
    ):
        raise AnalysisError("setup-robustness decision differs from recomputation")

    robustness_summary = manifest.get("setup_robustness")
    if not isinstance(robustness_summary, dict):
        raise AnalysisError("outer setup-robustness summary is absent")
    robustness_result: dict[str, Any]
    if trigger["triggered"]:
        if session.get("status") in {
            "complete",
            "primary_complete_robustness_non_estimable",
        }:
            robustness_result = validate_setup_robustness_phase(
                run,
                spec,
                primary_meta["pairs"],
                read_f271_orbits(run / "inputs/floor271_orbits.csv"),
                sha256_file(decision_path),
                sha256_file(primary / "records.csv"),
                preflight_plan_sha256,
                trigger,
                robustness_summary,
            )
            expected_session_status = (
                "complete"
                if robustness_result["analysis_status"] == "complete"
                else "primary_complete_robustness_non_estimable"
            )
            expected_phase = (
                "complete"
                if robustness_result["analysis_status"] == "complete"
                else "setup_robustness_non_estimable"
            )
            if (
                session.get("status") != expected_session_status
                or session.get("phase") != expected_phase
                or robustness_summary.get("triggered") is not True
                or manifest.get("total_records") != 22656
                or session.get("execution_units") != 5205
            ):
                raise AnalysisError("triggered complete totals differ")
        else:
            phase = run / "setup_robustness"
            if (
                session.get("status") != "primary_complete_robustness_failed"
                or session.get("phase") != "setup_robustness_failed"
                or robustness_summary.get("triggered") is not True
                or robustness_summary.get("status") != "failed"
                or robustness_summary.get("execution_status") != "failed"
                or robustness_summary.get("analysis_status") != "not_available"
                or robustness_summary.get("records") != 0
                or robustness_summary.get("partial_artifacts_retained") is not True
                or not isinstance(robustness_summary.get("error"), str)
                or not phase.is_dir()
                or (phase / "MANIFEST.sha256").exists()
                or manifest.get("total_records") != 20480
            ):
                raise AnalysisError("failed conditional-lane state differs")
            robustness_result = {
                "status": "failed_after_independently_sealed_primary",
                "analysis": None,
                "claim_limit": "the mandatory setup-robustness lane is incomplete; no persistence conclusion is permitted and no rerun/backfill is allowed",
            }
    else:
        if (
            session.get("status") != "complete"
            or session.get("phase") != "complete"
            or robustness_summary.get("triggered") is not False
            or robustness_summary.get("status") != "not_triggered"
            or robustness_summary.get("execution_status") != "not_run"
            or robustness_summary.get("analysis_status") != "not_run"
            or (run / "setup_robustness").exists()
            or manifest.get("total_records") != 20480
            or session.get("execution_units") != 3556
        ):
            raise AnalysisError("untriggered conditional-lane absence contract differs")
        robustness_result = {
            "status": "not_triggered",
            "analysis": None,
            "claim_limit": spec["setup_robustness"]["claim_limit"],
        }

    analysis["setup_and_process_costs"] = setup_and_process_costs
    analysis["setup_robustness"] = {
        "decision": decision,
        **robustness_result,
    }
    analysis["sealed_run_status"] = session["status"]
    analysis["runtime_provenance"] = runtime_provenance
    analysis["verification_runtime"] = current_analysis_runtime_receipt()
    analysis["build_integrity"] = {
        "batch_binary_sha256": build_integrity["batch_binary_sha256"],
        "selftest_binary_sha256": build_integrity["selftest_binary_sha256"],
        "static_elf_verified": True,
        "rng_cross_language_vectors_verified": rng_crosscheck["count"],
    }
    analysis["inputs"] = {
        "run_tree_manifest_sha256": tree_manifest_hash,
        "primary_tree_manifest_sha256": primary_tree_hash,
        "frozen_manifest_sha256": frozen_manifest_hash,
        "run_manifest_sha256": sha256_file(run / "run_manifest.json"),
        "records_sha256": sha256_file(primary / "records.csv"),
        "primary_analysis_sha256": sha256_file(primary / "analysis.json"),
        "setup_robustness_decision_sha256": sha256_file(decision_path),
        "selection_binding_sha256": sha256_file(run / "inputs/deep_selection.json"),
        "schedule_sha256": sha256_file(run / "inputs/schedule.csv"),
    }
    write_exclusive(out, analysis)
    print(json.dumps({"out": str(out), "status": analysis["status"], "sha256": sha256_file(out)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
