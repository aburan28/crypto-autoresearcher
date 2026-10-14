#!/usr/bin/env python3
"""Validate and analyse the frozen m=51 crater/floor rho study.

The runner must normalize the core CSVs to the schema in spec.json and
normalize successful selftest lines to certificates.json.  This script does
not run rho and refuses partial or repaired datasets.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
import shlex
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

import numpy as np


HERE = Path(__file__).resolve().parent
MASK64 = (1 << 64) - 1
ARM_IDS = (
    "crater-neg",
    "crater-tau51",
    "crater-tau17",
    "floor-neg",
    "floor-tau17",
)
ARM_MODE = {
    "crater-neg": 0,
    "crater-tau51": 1,
    "crater-tau17": 2,
    "floor-neg": 0,
    "floor-tau17": 2,
}
CORE_ACTION = {
    0: (0, 1),
    1: (1, 51),
    2: (17, 3),
}
RAW_HEADER = (
    "run",
    "target_index",
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
COMPILE_FLAGS = (
    "-std=gnu11",
    "-O2",
    "-Wall",
    "-Wextra",
    "-Wconversion",
    "-Wshadow",
    "-mpclmul",
    "-msse4.1",
)
FROZEN_FILES = (
    "PROTOCOL.md",
    "TRACE_ZERO_LANE.md",
    "spec.json",
    "sample.csv",
    "rho.c",
    "params.h",
    "run_replication.py",
    "analyze.py",
    "plot.py",
)
INTEGER_FIELDS = (
    "block_id",
    "b",
    "a2",
    "mode",
    "setup_seed",
    "target_seed",
    "walk_seed",
    "run",
    "target_index",
    "k",
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
)
SUMMARY_METRICS = (
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


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def valid_sha256(value: Any) -> bool:
    text = str(value)
    return len(text) == 64 and all(character in "0123456789abcdef" for character in text)


def valid_elapsed(value: Any, limit: float, tolerance: float) -> bool:
    return (
        not isinstance(value, bool)
        and isinstance(value, (int, float))
        and math.isfinite(float(value))
        and 0 <= float(value) <= limit + tolerance
    )


def parse_uint64_decimal(value: Any, context: str) -> int:
    if not isinstance(value, str) or not value or not value.isascii() or not value.isdecimal():
        raise ValueError(f"{context}: expected an unsigned decimal integer")
    parsed = int(value, 10)
    if parsed > MASK64:
        raise ValueError(f"{context}: integer exceeds uint64")
    return parsed


def require_json_uint64(value: Any, context: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= MASK64:
        raise ValueError(f"{context}: expected a JSON uint64 integer")
    return value


def read_frozen_manifest(base: Path) -> tuple[dict[str, str], str]:
    path = base / "FROZEN.sha256"
    try:
        content = path.read_text()
    except OSError as exc:
        raise ValueError(f"missing frozen-input manifest {path}") from exc
    if not content or not content.endswith("\n"):
        raise ValueError(f"{path}: frozen-input manifest must be nonempty and newline-terminated")
    entries: dict[str, str] = {}
    for line_number, line in enumerate(content.splitlines(), 1):
        pieces = line.split("  ", 1)
        if (
            len(pieces) != 2
            or not valid_sha256(pieces[0])
            or Path(pieces[1]).name != pieces[1]
            or pieces[1] in entries
        ):
            raise ValueError(f"{path}:{line_number}: malformed frozen-input entry")
        entries[pieces[1]] = pieces[0]
    if set(entries) != set(FROZEN_FILES) or list(entries) != sorted(FROZEN_FILES):
        raise ValueError(f"{path}: file set or ordering differs from the frozen contract")
    for name, expected in entries.items():
        target = base / name
        if not target.is_file() or sha256_file(target) != expected:
            raise ValueError(f"{target}: content differs from FROZEN.sha256")
    return entries, hashlib.sha256(content.encode()).hexdigest()


def mix64(value: int) -> int:
    value &= MASK64
    value = ((value ^ (value >> 30)) * 0xBF58476D1CE4E5B9) & MASK64
    value = ((value ^ (value >> 27)) * 0x94D049BB133111EB) & MASK64
    return (value ^ (value >> 31)) & MASK64


def indexed_word(seed: int, index: int, domain: int, attempt: int) -> int:
    return mix64(
        seed
        ^ domain
        ^ mix64((index + 0x9E3779B97F4A7C15) & MASK64)
        ^ mix64((attempt + 0xD1B54A32D192ED03) & MASK64)
    )


def indexed_bounded(seed: int, index: int, domain: int, bound: int) -> int:
    threshold = ((-bound) & MASK64) % bound
    attempt = 0
    while True:
        value = indexed_word(seed, index, domain, attempt)
        if value >= threshold:
            return value % bound
        attempt += 1


def expected_target_scalar(seed: int, index: int, subgroup_order: int) -> int:
    return 1 + indexed_bounded(seed, index, 0x5441524745544B31, subgroup_order - 1)


def expected_walk_stream(seed: int, index: int) -> int:
    return indexed_word(seed, index, 0x57414C4B53545231, 0)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text())


def parse_bool(value: str) -> bool:
    if value.lower() in {"1", "true"}:
        return True
    if value.lower() in {"0", "false"}:
        return False
    raise ValueError(f"invalid boolean value {value!r}")


def read_sample(path: Path) -> tuple[dict[str, dict[str, Any]], list[str]]:
    expected_header = (
        "curve_id",
        "level",
        "orbit_id",
        "b",
        "a2",
        "orbit_size",
        "f_E",
        "source_status",
    )
    rows: dict[str, dict[str, Any]] = {}
    floor_ids: list[str] = []
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != expected_header:
            raise ValueError("sample.csv columns or ordering differ from the frozen schema")
        for line_number, raw in enumerate(reader, 2):
            if None in raw:
                raise ValueError(f"sample.csv row {line_number} has trailing fields")
            row = dict(raw)
            curve_id = row["curve_id"]
            if curve_id in rows:
                raise ValueError(f"duplicate sample curve {curve_id}")
            for field in ("b", "a2", "orbit_size", "f_E"):
                row[field] = parse_uint64_decimal(row[field], f"sample row {line_number}:{field}")
            row["orbit_id"] = (
                parse_uint64_decimal(row["orbit_id"], f"sample row {line_number}:orbit_id")
                if row["orbit_id"]
                else None
            )
            rows[curve_id] = row
            if row["level"] == "floor-271":
                floor_ids.append(curve_id)
    if set(rows) != {"m51-crater", *(f"m51-floor-o{i:02d}" for i in range(1, 17))}:
        raise ValueError("sample.csv does not contain the exact frozen 17 curves")
    floor_ids.sort(key=lambda curve_id: rows[curve_id]["orbit_id"])
    expected_reps = [
        623162416261,
        25640824825979,
        30885819784827,
        57318330399736,
        67694307705004,
        72881269935803,
        115635957935040,
        116461223646592,
        116511665573478,
        121360481466206,
        130246110195364,
        147686731444433,
        213718369432541,
        237711860122495,
        360860333097189,
        370376419722289,
    ]
    if [rows[curve_id]["b"] for curve_id in floor_ids] != expected_reps:
        raise ValueError("sample.csv floor representatives differ from the frozen list")
    crater = rows["m51-crater"]
    if (
        crater["b"] != 1
        or crater["a2"] != 0
        or crater["f_E"] != 1
        or crater["level"] != "crater"
        or crater["orbit_id"] is not None
        or crater["orbit_size"] != 1
    ):
        raise ValueError("frozen crater identity changed")
    expected_status = "cm_floor_set_kernel_check_40of40_14of16_orbits"
    for orbit_id, curve_id in enumerate(floor_ids, 1):
        row = rows[curve_id]
        if (
            row["a2"] != 0
            or row["f_E"] != 271
            or row["level"] != "floor-271"
            or row["orbit_id"] != orbit_id
            or row["orbit_size"] != 17
            or row["source_status"] != expected_status
        ):
            raise ValueError(f"frozen floor metadata changed for {curve_id}")
    return rows, floor_ids


def read_records(path: Path, required_columns: Iterable[str]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        expected_columns = tuple(required_columns)
        if tuple(reader.fieldnames or ()) != expected_columns:
            raise ValueError("records CSV columns or ordering differ from the frozen schema")
        for line_number, raw in enumerate(reader, 2):
            if None in raw:
                raise ValueError(f"invalid records row {line_number}: trailing fields")
            row: dict[str, Any] = dict(raw)
            try:
                for field in INTEGER_FIELDS:
                    row[field] = parse_uint64_decimal(
                        row[field], f"records row {line_number}:{field}"
                    )
                row["orbit_id"] = (
                    parse_uint64_decimal(
                        row["orbit_id"], f"records row {line_number}:orbit_id"
                    )
                    if row["orbit_id"]
                    else None
                )
                row["sec"] = float(row["sec"])
                row["ok"] = parse_bool(row["ok"])
            except (KeyError, ValueError) as exc:
                raise ValueError(f"invalid records row {line_number}: {exc}") from exc
            records.append(row)
    return records


def expected_curve_for_block(arm: str, block_id: int) -> tuple[str, int | None]:
    if arm.startswith("crater-"):
        return "m51-crater", None
    orbit_id = 1 + block_id // 256
    return f"m51-floor-o{orbit_id:02d}", orbit_id


def expected_jobs(
    spec: dict[str, Any], samples: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    """Independently reconstruct the runner's 400 unshuffled jobs."""
    design = spec["design"]
    seeds = spec["seeds"]
    size = int(design["blocks_per_job"])
    jobs: list[dict[str, Any]] = []
    for target_start in range(0, int(design["primary_target_blocks"]), size):
        orbit_id = 1 + target_start // int(design["blocks_per_floor_orbit"])
        for arm in ARM_IDS:
            curve_id = (
                "m51-crater"
                if arm.startswith("crater-")
                else f"m51-floor-o{orbit_id:02d}"
            )
            sample = samples[curve_id]
            jobs.append(
                {
                    "replicate": "primary",
                    "arm": arm,
                    "curve_id": curve_id,
                    "orbit_id": sample["orbit_id"],
                    "b": sample["b"],
                    "a2": sample["a2"],
                    "mode": ARM_MODE[arm],
                    "target_start": target_start,
                    "targets": size,
                    "setup_seed": int(seeds["setup_root"]),
                    "target_seed": int(seeds["target_root"]),
                    "walk_seed": int(seeds["walk_primary_root"]),
                    "filename": f"primary_b{target_start:04d}_{arm}.csv",
                }
            )
    for orbit_id in range(1, int(design["floor_orbits"]) + 1):
        target_start = (orbit_id - 1) * int(design["blocks_per_floor_orbit"])
        for arm in ARM_IDS:
            curve_id = (
                "m51-crater"
                if arm.startswith("crater-")
                else f"m51-floor-o{orbit_id:02d}"
            )
            sample = samples[curve_id]
            jobs.append(
                {
                    "replicate": "aa-b",
                    "arm": arm,
                    "curve_id": curve_id,
                    "orbit_id": sample["orbit_id"],
                    "b": sample["b"],
                    "a2": sample["a2"],
                    "mode": ARM_MODE[arm],
                    "target_start": target_start,
                    "targets": size,
                    "setup_seed": int(seeds["setup_root"]),
                    "target_seed": int(seeds["target_root"]),
                    "walk_seed": int(seeds["walk_aa_root"]),
                    "filename": f"aa-b_b{target_start:04d}_{arm}.csv",
                }
            )
    if len(jobs) != 400 or sum(job["targets"] for job in jobs) != design["total_records"]:
        raise ValueError("internal expected-job construction differs from the frozen totals")
    return jobs


def read_jsonl(path: Path, expected_count: int) -> list[dict[str, Any]]:
    try:
        rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{path}: missing or malformed JSONL") from exc
    if len(rows) != expected_count or not all(isinstance(row, dict) for row in rows):
        raise ValueError(f"{path}: found {len(rows)} entries, expected {expected_count}")
    return rows


def validate_checksum_manifest(run_root: Path) -> dict[str, str]:
    path = run_root / "MANIFEST.sha256"
    try:
        lines = path.read_text().splitlines()
    except OSError as exc:
        raise ValueError(f"{path}: missing checksum seal") from exc
    entries: dict[str, str] = {}
    for line_number, line in enumerate(lines, 1):
        pieces = line.split("  ", 1)
        if len(pieces) != 2 or not valid_sha256(pieces[0]):
            raise ValueError(f"{path}:{line_number}: malformed checksum entry")
        relative = Path(pieces[1])
        if relative.is_absolute() or ".." in relative.parts or str(relative) in entries:
            raise ValueError(f"{path}:{line_number}: unsafe or duplicate relative path")
        target = run_root / relative
        if not target.is_file() or sha256_file(target) != pieces[0]:
            raise ValueError(f"{path}:{line_number}: missing or changed file {relative}")
        entries[str(relative)] = pieces[0]
    actual = {
        str(candidate.relative_to(run_root))
        for candidate in run_root.rglob("*")
        if candidate.is_file() and candidate != path
    }
    if set(entries) != actual:
        raise ValueError(
            f"checksum seal tree mismatch; missing={sorted(actual - set(entries))[:8]}, "
            f"extra={sorted(set(entries) - actual)[:8]}"
        )
    partials = sorted(name for name in actual if name.endswith(".partial"))
    if partials:
        raise ValueError(f"sealed run contains partial files: {partials[:8]}")
    return entries


def parse_selftest_stdout(value: Any) -> dict[str, str]:
    lines = str(value).splitlines()
    if len(lines) != 1:
        raise ValueError("selftest receipt must contain exactly one stdout line")
    fields: dict[str, str] = {}
    for token in lines[0].split():
        if token.count("=") != 1:
            raise ValueError("malformed selftest stdout token")
        key, item = token.split("=", 1)
        if key in fields:
            raise ValueError("duplicate selftest stdout field")
        fields[key] = item
    return fields


def invocation_option(argv: list[str], option: str) -> str | None:
    values: list[str] = []
    for index, item in enumerate(argv):
        if item == option:
            if index + 1 >= len(argv):
                raise ValueError(f"provenance invocation lacks a value for {option}")
            values.append(argv[index + 1])
        elif item.startswith(option + "="):
            values.append(item.split("=", 1)[1])
    if len(values) > 1:
        raise ValueError(f"provenance invocation repeats {option}")
    return values[0] if values else None


def validate_runner_options(argv: list[str]) -> None:
    allowed = {"--out", "--workers", "--cores"}
    index = 2
    while index < len(argv):
        item = argv[index]
        if item in allowed:
            if index + 1 >= len(argv):
                raise ValueError(f"provenance invocation lacks a value for {item}")
            index += 2
            continue
        if any(item.startswith(option + "=") for option in allowed):
            index += 1
            continue
        raise ValueError(f"provenance invocation contains an unsupported argument {item!r}")


def validate_raw_job(
    path: Path,
    job: dict[str, Any],
    by_key: dict[tuple[str, int, str], dict[str, Any]],
) -> None:
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != RAW_HEADER:
            raise ValueError(f"{path}: raw header differs from the frozen core schema")
        rows = list(reader)
    if len(rows) != job["targets"]:
        raise ValueError(f"{path}: raw row count differs from the 64-target job")
    integer_fields = RAW_HEADER[:-1]
    for offset, raw in enumerate(rows):
        if None in raw:
            raise ValueError(f"{path}: trailing fields in raw row {offset}")
        try:
            parsed = {
                field: parse_uint64_decimal(raw[field], f"{path}:{offset + 2}:{field}")
                for field in integer_fields
            }
            parsed["sec"] = float(raw["sec"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"{path}: malformed raw row {offset}") from exc
        block_id = job["target_start"] + offset
        normalized = by_key[(job["replicate"], block_id, job["arm"])]
        if parsed["run"] != offset or parsed["target_index"] != block_id:
            raise ValueError(f"{path}: raw run/target index mismatch at offset {offset}")
        for raw_field, normalized_field in (
            ("target_scalar", "k"),
            ("walk_stream_seed", "walk_stream_seed"),
            *((field, field) for field in RAW_HEADER[4:-1]),
        ):
            if parsed[raw_field] != normalized[normalized_field]:
                raise ValueError(f"{path}: raw/normalized {raw_field} mismatch at {block_id}")
        if parsed["ok"] != int(normalized["ok"]) or parsed["sec"] != normalized["sec"]:
            raise ValueError(f"{path}: raw/normalized verification or timing mismatch at {block_id}")


def validate_run_archive(
    run_root: Path,
    *,
    spec: dict[str, Any],
    samples: dict[str, dict[str, Any]],
    floor_ids: list[str],
    manifest: dict[str, Any],
    certificates: dict[str, Any],
    records_path: Path,
    by_key: dict[tuple[str, int, str], dict[str, Any]],
) -> dict[str, Any]:
    """Revalidate the sealed runner tree, not only its declarative manifest."""
    run_root = run_root.resolve()
    sealed = validate_checksum_manifest(run_root)
    required_top = {
        "MANIFEST.sha256",
        "certificates.json",
        "jobs.jsonl",
        "plan.json",
        "provenance.json",
        "records.csv",
        "run-command.txt",
        "run.stdout.log",
        "run_manifest.json",
        "selftests.jsonl",
        "session.json",
    }
    actual_top = {path.name for path in run_root.iterdir() if path.is_file()}
    if not required_top.issubset(actual_top):
        raise ValueError(f"run root lacks required sealed files: {sorted(required_top - actual_top)}")

    plan = read_json(run_root / "plan.json")
    workers = int(plan.get("workers", 0))
    cores = plan.get("cores")
    if not 1 <= workers <= int(spec["design"]["max_workers"]):
        raise ValueError("plan worker count is outside the frozen bound")
    if (
        not isinstance(cores, list)
        or len(cores) != workers
        or len(set(cores)) != workers
        or not all(isinstance(core, int) and core >= 0 for core in cores)
    ):
        raise ValueError("plan does not contain distinct pinned worker cores")
    base_jobs = expected_jobs(spec, samples)
    random.Random(int(spec["seeds"]["schedule_root"])).shuffle(base_jobs)
    expected_plan_jobs = [
        job
        | {
            "schedule_index": index,
            "assigned_core": cores[index % workers],
        }
        for index, job in enumerate(base_jobs)
    ]
    exact_plan = {
        "schema": "m51-volcano-rho-plan/v1",
        "schedule_algorithm": "python-random-v3-seeded-shuffle",
        "schedule_root": spec["seeds"]["schedule_root"],
        "workers": workers,
        "cores": cores,
        "blocks_per_job": spec["design"]["blocks_per_job"],
        "jobs": expected_plan_jobs,
        "expected_jobs": 400,
        "expected_records": spec["design"]["total_records"],
    }
    if set(plan) != set(exact_plan) | {"created_utc"}:
        raise ValueError("plan fields differ from the exact frozen plan schema")
    for field, expected in exact_plan.items():
        if plan.get(field) != expected:
            raise ValueError(f"plan field {field} differs from the reconstructed frozen plan")
    if not isinstance(plan.get("created_utc"), str) or not plan["created_utc"]:
        raise ValueError("plan lacks its creation timestamp")

    session = read_json(run_root / "session.json")
    expected_session_fields = {
        "schema",
        "started_utc",
        "finished_utc",
        "status",
        "selftest_only",
        "workers",
        "cores",
        "phase",
        "binary_sha256",
        "certificates",
        "expected_jobs",
        "expected_records",
        "plan_sha256",
        "jobs_completed",
        "job_run",
        "records",
        "scientific_run",
        "run_manifest",
    }
    if set(session) != expected_session_fields:
        raise ValueError("complete session fields differ from the frozen schema")
    exact_session = {
        "schema": "m51-volcano-rho-session/v1",
        "status": "complete",
        "phase": "complete",
        "selftest_only": False,
        "scientific_run": True,
        "workers": workers,
        "cores": cores,
        "expected_jobs": 400,
        "expected_records": spec["design"]["total_records"],
        "jobs_completed": 400,
        "plan_sha256": sha256_file(run_root / "plan.json"),
    }
    for field, expected in exact_session.items():
        if session.get(field) != expected:
            raise ValueError(f"session field {field} differs from the complete frozen run")
    if session.get("error") is not None or not session.get("started_utc") or not session.get("finished_utc"):
        raise ValueError("session contains an error or lacks timestamps")
    binary = run_root / "build" / "rho"
    if not binary.is_file() or session.get("binary_sha256") != sha256_file(binary):
        raise ValueError("session binary hash is missing or differs from the archived executable")
    if session.get("records") != {
        "rows": spec["design"]["total_records"],
        "unique_keys": spec["design"]["total_records"],
        "sha256": sha256_file(records_path),
    }:
        raise ValueError("session normalized-record receipt differs from records.csv")
    session_manifest = session.get("run_manifest", {})
    if (
        not isinstance(session_manifest, dict)
        or set(session_manifest) != {"path", "sha256"}
        or session_manifest.get("sha256") != sha256_file(run_root / "run_manifest.json")
    ):
        raise ValueError("session does not bind run_manifest.json")

    provenance = read_json(run_root / "provenance.json")
    if provenance.get("schema") != "m51-volcano-rho-provenance/v1":
        raise ValueError("unexpected provenance schema")
    git = provenance.get("git", {})
    if (
        git.get("commit") != manifest["build"]["git_commit"]
        or git.get("status_porcelain") != ""
        or git.get("worktree_clean") is not True
        or provenance.get("git_before_snapshot") != git
        or provenance.get("git_after_snapshot") != git
    ):
        raise ValueError("provenance does not bind one clean commit across the input snapshot")
    host = provenance.get("host", {})
    if host.get("selected_cores") != cores or not set(cores).issubset(
        set(host.get("process_affinity", []))
    ):
        raise ValueError("provenance host affinity differs from the pinned plan")
    required_features = set(spec["execution_requirements"]["cpu_features"])
    if not required_features.issubset(set(host.get("cpu_flags", []))):
        raise ValueError("provenance host lacks a frozen CPU feature")
    canonical_frozen, canonical_frozen_sha256 = read_frozen_manifest(HERE)
    archived_frozen, archived_frozen_sha256 = read_frozen_manifest(run_root / "inputs")
    if archived_frozen != canonical_frozen or archived_frozen_sha256 != canonical_frozen_sha256:
        raise ValueError("archived frozen-input manifest differs from the canonical design")
    if provenance.get("frozen_manifest_sha256") != canonical_frozen_sha256:
        raise ValueError("provenance does not bind the frozen-input manifest")
    input_names = {*FROZEN_FILES, "FROZEN.sha256"}
    input_receipts = provenance.get("inputs")
    if not isinstance(input_receipts, dict) or set(input_receipts) != input_names:
        raise ValueError("provenance input snapshot set differs from the runner contract")
    recorded_roots = {
        Path(receipt.get("snapshot_path", "")).parent.parent
        for receipt in input_receipts.values()
        if isinstance(receipt, dict)
    }
    if len(recorded_roots) != 1:
        raise ValueError("provenance input paths do not share one recorded run root")
    recorded_root = recorded_roots.pop()
    if not recorded_root.is_absolute():
        raise ValueError("provenance recorded run root is not absolute")
    if Path(session.get("run_manifest", {}).get("path", "")) != recorded_root / "run_manifest.json":
        raise ValueError("session run-manifest path differs from the recorded run root")
    invocation = provenance.get("invocation")
    if not isinstance(invocation, list) or len(invocation) < 3 or not all(
        isinstance(item, str) for item in invocation
    ):
        raise ValueError("provenance invocation is missing or malformed")
    if Path(invocation[1]).name != "run_replication.py":
        raise ValueError("provenance invocation is not the frozen runner")
    validate_runner_options(invocation)
    if invocation[0] != host.get("python_executable"):
        raise ValueError("provenance invocation does not use the recorded Python executable")
    invoked_runner = Path(invocation[1])
    if not invoked_runner.is_absolute():
        invoked_runner = Path(provenance.get("cwd", "")) / invoked_runner
    invoked_runner = invoked_runner.resolve()
    if invoked_runner != Path(input_receipts["run_replication.py"].get("source_path", "")):
        raise ValueError("provenance invocation runner differs from the snapshotted source")
    invocation_out_value = invocation_option(invocation, "--out")
    if invocation_out_value is None:
        raise ValueError("provenance invocation lacks --out")
    invocation_out = Path(invocation_out_value)
    if not invocation_out.is_absolute():
        invocation_out = Path(provenance.get("cwd", "")) / invocation_out
    invocation_out = invocation_out.resolve()
    if invocation_out != recorded_root:
        raise ValueError("provenance invocation output differs from the recorded run root")
    if "--selftest-only" in invocation:
        raise ValueError("scientific run provenance contains --selftest-only")
    invocation_workers = invocation_option(invocation, "--workers")
    if invocation_workers is not None:
        if int(invocation_workers) != workers:
            raise ValueError("provenance invocation worker count differs from the plan")
    elif workers != 4:
        raise ValueError("nondefault worker count is absent from the provenance invocation")
    invocation_cores = invocation_option(invocation, "--cores")
    if invocation_cores is not None:
        if [int(item) for item in invocation_cores.split(",")] != cores:
            raise ValueError("provenance invocation core list differs from the plan")
    elif cores != sorted(host.get("process_affinity", []))[:workers]:
        raise ValueError("default provenance core selection differs from the plan")
    invocation_shell = shlex.join(invocation)
    if (
        provenance.get("invocation_shell") != invocation_shell
        or (run_root / "run-command.txt").read_text() != invocation_shell + "\n"
    ):
        raise ValueError("run-command.txt differs from the exact provenance invocation")
    for name in input_names:
        receipt = input_receipts[name]
        snapshot = run_root / "inputs" / name
        if (
            not snapshot.is_file()
            or receipt.get("sha256") != sha256_file(snapshot)
            or receipt.get("bytes") != snapshot.stat().st_size
            or Path(receipt.get("snapshot_path", "")) != recorded_root / "inputs" / name
            or Path(receipt.get("source_path", "")).name != name
            or sha256_file(HERE / name) != sha256_file(snapshot)
        ):
            raise ValueError(f"provenance input snapshot mismatch for {name}")

    build_receipt = read_json(run_root / "build" / "build-receipt.json")
    expected_build_receipt_fields = {
        "command",
        "cwd",
        "started_utc",
        "finished_utc",
        "elapsed_sec",
        "exit_status",
        "timed_out",
        "cancelled",
        "stdout",
        "stderr",
        "logical_frozen_command",
        "compiler_version",
        "source_sha256",
        "params_sha256",
        "binary",
        "binary_sha256",
    }
    if set(build_receipt) != expected_build_receipt_fields:
        raise ValueError("successful build receipt fields differ from the frozen schema")
    expected_actual_command = [
        "gcc",
        *COMPILE_FLAGS,
        "-o",
        str(recorded_root / "build" / "rho.partial"),
        "rho.c",
    ]
    if (
        build_receipt.get("command") != expected_actual_command
        or build_receipt.get("logical_frozen_command")
        != ["gcc", *COMPILE_FLAGS, "-o", "rho", "rho.c"]
        or Path(build_receipt.get("cwd", "")) != recorded_root / "inputs"
        or build_receipt.get("exit_status") != 0
        or build_receipt.get("timed_out") is not False
        or build_receipt.get("cancelled") is not False
        or not valid_elapsed(
            build_receipt.get("elapsed_sec"),
            float(spec["execution_requirements"]["build_timeout_seconds"]),
            float(spec["execution_requirements"]["receipt_elapsed_tolerance_seconds"]),
        )
        or not build_receipt.get("started_utc")
        or not build_receipt.get("finished_utc")
        or build_receipt.get("stderr") != ""
        or build_receipt.get("source_sha256") != sha256_file(run_root / "inputs" / "rho.c")
        or build_receipt.get("params_sha256") != sha256_file(run_root / "inputs" / "params.h")
        or build_receipt.get("binary_sha256") != sha256_file(binary)
        or Path(build_receipt.get("binary", "")) != recorded_root / "build" / "rho"
    ):
        raise ValueError("archived build receipt differs from the frozen successful build")
    if (run_root / "build" / "gcc.stdout.log").read_text() != build_receipt.get("stdout", ""):
        raise ValueError("build stdout log differs from its receipt")
    if (run_root / "build" / "gcc.stderr.log").read_text() != build_receipt.get("stderr", ""):
        raise ValueError("build stderr log differs from its receipt")

    certificate_by_pair = {
        (entry["curve_id"], int(entry["mode"])): entry
        for entry in certificates["entries"]
    }
    expected_pairs = [
        ("m51-crater", 0),
        ("m51-crater", 1),
        ("m51-crater", 2),
        *((curve_id, mode) for curve_id in floor_ids for mode in (0, 2)),
    ]
    selftest_receipts = read_jsonl(run_root / "selftests.jsonl", len(expected_pairs))
    for receipt, pair in zip(selftest_receipts, expected_pairs):
        curve_id, mode = pair
        sample = samples[curve_id]
        expected_command = [
            "taskset",
            "-c",
            str(cores[0]),
            str(recorded_root / "build" / "rho"),
            "selftest",
            str(sample["b"]),
            str(sample["a2"]),
            str(mode),
            str(spec["seeds"]["setup_root"]),
        ]
        expected_selftest_receipt_fields = {
            "command",
            "cwd",
            "started_utc",
            "finished_utc",
            "elapsed_sec",
            "exit_status",
            "timed_out",
            "cancelled",
            "stdout",
            "stderr",
            "curve_id",
            "mode",
            "core",
            "status",
            "certificate",
        }
        if (
            set(receipt) != expected_selftest_receipt_fields
            or receipt.get("cwd") is not None
            or receipt.get("curve_id") != curve_id
            or receipt.get("mode") != mode
            or receipt.get("core") != cores[0]
            or receipt.get("command") != expected_command
            or receipt.get("status") != "completed"
            or receipt.get("exit_status") != 0
            or receipt.get("timed_out") is not False
            or receipt.get("cancelled") is not False
            or not valid_elapsed(
                receipt.get("elapsed_sec"),
                300.0,
                float(spec["execution_requirements"]["receipt_elapsed_tolerance_seconds"]),
            )
            or not receipt.get("started_utc")
            or not receipt.get("finished_utc")
            or receipt.get("stderr") != ""
            or receipt.get("certificate") != certificate_by_pair[pair]
        ):
            raise ValueError(f"selftest receipt mismatch for {pair}")
        stdout_fields = parse_selftest_stdout(receipt.get("stdout"))
        certificate = certificate_by_pair[pair]
        expected_stdout = {
            field: str(certificate[field])
            for field in (
                "selftest_ok",
                "b",
                "a2",
                "mode",
                "action_step",
                "action_order",
                "setup_seed",
                "pgen_x",
                "pgen_y",
                "setup_fingerprint",
            )
        }
        if stdout_fields != expected_stdout:
            raise ValueError(f"selftest stdout differs from its certificate for {pair}")
    certificate_session = session.get("certificates", {})
    if (
        not isinstance(certificate_session, dict)
        or set(certificate_session)
        != {"entries", "receipts_sha256", "certificates_sha256"}
        or certificate_session.get("entries") != len(expected_pairs)
        or certificate_session.get("receipts_sha256")
        != sha256_file(run_root / "selftests.jsonl")
        or certificate_session.get("certificates_sha256")
        != sha256_file(run_root / "certificates.json")
    ):
        raise ValueError("session selftest/certificate receipt mismatch")

    job_receipts = read_jsonl(run_root / "jobs.jsonl", len(expected_plan_jobs))
    expected_by_key = {
        (job["replicate"], job["target_start"], job["arm"]): job
        for job in expected_plan_jobs
    }
    seen: set[tuple[str, int, str]] = set()
    expected_raw: set[str] = set()
    for receipt in job_receipts:
        job = receipt.get("job", {})
        key = (job.get("replicate"), job.get("target_start"), job.get("arm"))
        if key in seen or key not in expected_by_key:
            raise ValueError(f"duplicate or unexpected job receipt {key}")
        seen.add(key)
        planned = expected_by_key[key]
        plain_job = {k: v for k, v in planned.items() if k not in {"schedule_index", "assigned_core"}}
        if job != plain_job:
            raise ValueError(f"job receipt metadata differs from plan for {key}")
        raw = run_root / "raw" / planned["filename"]
        recorded_raw = recorded_root / "raw" / planned["filename"]
        partial = recorded_raw.with_name(recorded_raw.name + ".partial")
        expected_command = [
            "taskset",
            "-c",
            str(planned["assigned_core"]),
            str(recorded_root / "build" / "rho"),
            "run",
            str(planned["b"]),
            str(planned["a2"]),
            str(planned["mode"]),
            str(planned["targets"]),
            str(planned["setup_seed"]),
            str(planned["target_seed"]),
            str(planned["walk_seed"]),
            str(planned["target_start"]),
            str(partial),
        ]
        expected_validation = {
            "rows": planned["targets"],
            "verified": planned["targets"],
            "target_start": planned["target_start"],
            "target_stop_exclusive": planned["target_start"] + planned["targets"],
        }
        expected_job_receipt_fields = {
            "command",
            "cwd",
            "started_utc",
            "finished_utc",
            "elapsed_sec",
            "exit_status",
            "timed_out",
            "cancelled",
            "stdout",
            "stderr",
            "job",
            "core",
            "status",
            "output_partial",
            "output_final",
            "validation",
            "sha256",
        }
        if (
            set(receipt) != expected_job_receipt_fields
            or receipt.get("cwd") is not None
            or receipt.get("status") != "completed"
            or receipt.get("core") != planned["assigned_core"]
            or receipt.get("command") != expected_command
            or receipt.get("exit_status") != 0
            or receipt.get("timed_out") is not False
            or receipt.get("cancelled") is not False
            or not valid_elapsed(
                receipt.get("elapsed_sec"),
                float(spec["design"]["timeout_seconds_per_job"]),
                float(spec["execution_requirements"]["receipt_elapsed_tolerance_seconds"]),
            )
            or receipt.get("stdout") != ""
            or receipt.get("stderr") != ""
            or receipt.get("validation") != expected_validation
            or receipt.get("output_partial") != str(partial)
            or receipt.get("output_final") != str(recorded_raw)
            or (run_root / "raw" / (planned["filename"] + ".partial")).exists()
            or not raw.is_file()
            or receipt.get("sha256") != sha256_file(raw)
            or not receipt.get("started_utc")
            or not receipt.get("finished_utc")
        ):
            raise ValueError(f"job process or output receipt mismatch for {key}")
        validate_raw_job(raw, planned, by_key)
        expected_raw.add(planned["filename"])
    actual_raw = {path.name for path in (run_root / "raw").iterdir() if path.is_file()}
    if seen != set(expected_by_key) or actual_raw != expected_raw:
        raise ValueError("job receipt set or exact raw tree is incomplete")
    job_session = session.get("job_run", {})
    if (
        not isinstance(job_session, dict)
        or set(job_session) != {"jobs", "records", "receipts_sha256", "elapsed_sec"}
        or job_session.get("jobs") != 400
        or job_session.get("records") != spec["design"]["total_records"]
        or job_session.get("receipts_sha256") != sha256_file(run_root / "jobs.jsonl")
        or not valid_elapsed(
            job_session.get("elapsed_sec"),
            400.0 * float(spec["design"]["timeout_seconds_per_job"]),
            float(spec["execution_requirements"]["receipt_elapsed_tolerance_seconds"]),
        )
    ):
        raise ValueError("session job-run receipt differs from the archived jobs")

    manifest_inputs = manifest["inputs"]
    exact_manifest_inputs = {
        "rho_source_sha256": sha256_file(run_root / "inputs" / "rho.c"),
        "params_source_sha256": sha256_file(run_root / "inputs" / "params.h"),
        "runner_source_sha256": sha256_file(run_root / "inputs" / "run_replication.py"),
        "analyzer_source_sha256": sha256_file(run_root / "inputs" / "analyze.py"),
        "plot_source_sha256": sha256_file(run_root / "inputs" / "plot.py"),
        "protocol_sha256": sha256_file(run_root / "inputs" / "PROTOCOL.md"),
        "trace_zero_lane_sha256": sha256_file(
            run_root / "inputs" / "TRACE_ZERO_LANE.md"
        ),
        "frozen_manifest_sha256": sha256_file(run_root / "inputs" / "FROZEN.sha256"),
        "spec_sha256": sha256_file(run_root / "inputs" / "spec.json"),
        "sample_sha256": sha256_file(run_root / "inputs" / "sample.csv"),
        "records_sha256": sha256_file(records_path),
        "certificates_sha256": sha256_file(run_root / "certificates.json"),
    }
    if manifest_inputs != exact_manifest_inputs:
        raise ValueError("run manifest input bindings differ from the sealed archive")
    manifest_build = manifest["build"]
    if (
        manifest_build.get("actual_command") != expected_actual_command
        or manifest_build.get("binary_sha256") != sha256_file(binary)
        or manifest_build.get("compiler_version")
        != "\n".join(build_receipt["compiler_version"])
        or manifest_build.get("cpu_features") != host.get("cpu_flags")
        or manifest_build.get("cpu_affinity") != cores
        or manifest_build.get("host") != host.get("platform")
    ):
        raise ValueError("run manifest build bindings differ from the sealed archive")
    manifest_execution = manifest["execution"]
    if (
        manifest_execution.get("workers_used") != workers
        or manifest_execution.get("cores") != cores
        or manifest_execution.get("plan_sha256") != sha256_file(run_root / "plan.json")
        or manifest_execution.get("job_receipts_sha256")
        != sha256_file(run_root / "jobs.jsonl")
    ):
        raise ValueError("run manifest execution bindings differ from the sealed archive")
    return {
        "seal_entries": len(sealed),
        "jobs": len(job_receipts),
        "raw_files": len(actual_raw),
        "selftests": len(selftest_receipts),
        "binary_sha256": sha256_file(binary),
        "plan_sha256": sha256_file(run_root / "plan.json"),
        "job_receipts_sha256": sha256_file(run_root / "jobs.jsonl"),
    }


def validate_manifest(
    path: Path,
    *,
    spec: dict[str, Any],
    spec_path: Path,
    sample_path: Path,
    records_path: Path,
    certificates_path: Path,
) -> dict[str, Any]:
    manifest = read_json(path)
    manifest_schema = spec["normalized_run_manifest_schema"]
    if not isinstance(manifest, dict) or set(manifest) != set(
        manifest_schema["top_level_fields"]
    ):
        raise ValueError("run manifest top-level fields differ from the frozen schema")
    for section, fields_key in (
        ("inputs", "inputs_fields"),
        ("build", "build_fields"),
        ("parameters", "parameter_fields"),
        ("execution", "execution_fields"),
    ):
        value = manifest.get(section)
        if not isinstance(value, dict) or set(value) != set(manifest_schema[fields_key]):
            raise ValueError(f"run manifest {section} fields differ from the frozen schema")
    if manifest.get("schema") != "m51-rho-run-manifest/v1":
        raise ValueError("unexpected run-manifest schema")
    if manifest.get("study_id") != spec["study_id"] or manifest.get("status") != "complete":
        raise ValueError("run manifest is not a complete record of this study")
    if not isinstance(manifest.get("created_utc"), str) or not manifest["created_utc"]:
        raise ValueError("run manifest lacks its creation timestamp")
    inputs = manifest.get("inputs", {})
    _, frozen_manifest_sha256 = read_frozen_manifest(HERE)
    expected_inputs = {
        "rho_source_sha256": spec["provenance"]["rho_source_sha256"],
        "params_source_sha256": spec["provenance"]["params_source_sha256"],
        "runner_source_sha256": sha256_file(HERE / "run_replication.py"),
        "analyzer_source_sha256": sha256_file(HERE / "analyze.py"),
        "plot_source_sha256": sha256_file(HERE / "plot.py"),
        "protocol_sha256": sha256_file(HERE / "PROTOCOL.md"),
        "trace_zero_lane_sha256": sha256_file(HERE / "TRACE_ZERO_LANE.md"),
        "frozen_manifest_sha256": frozen_manifest_sha256,
        "spec_sha256": sha256_file(spec_path),
        "sample_sha256": sha256_file(sample_path),
        "records_sha256": sha256_file(records_path),
        "certificates_sha256": sha256_file(certificates_path),
    }
    if inputs != expected_inputs:
        raise ValueError("run manifest input bindings do not match the exact frozen inputs")
    study_dir = HERE
    if sha256_file(study_dir / "rho.c") != expected_inputs["rho_source_sha256"]:
        raise ValueError("rho.c content does not match the frozen source hash")
    if sha256_file(study_dir / "params.h") != expected_inputs["params_source_sha256"]:
        raise ValueError("params.h content does not match the frozen source hash")

    build = manifest.get("build", {})
    if build.get("command") != spec["execution_requirements"]["compile"]:
        raise ValueError("build command differs from the frozen command")
    if not valid_sha256(build.get("binary_sha256")):
        raise ValueError("run manifest lacks a valid binary SHA-256")
    if not str(build.get("compiler_version", "")).strip():
        raise ValueError("run manifest lacks a compiler version")
    required_features = set(spec["execution_requirements"]["cpu_features"])
    if not required_features.issubset(set(build.get("cpu_features", []))):
        raise ValueError("run host lacks a declared frozen CPU feature")
    commit = str(build.get("git_commit", ""))
    if len(commit) != 40 or any(c not in "0123456789abcdef" for c in commit):
        raise ValueError("run manifest lacks an exact git commit")
    if build.get("git_dirty") is not False:
        raise ValueError("run manifest does not bind a clean source tree")
    if not str(build.get("host", "")).strip() or not build.get("cpu_affinity"):
        raise ValueError("run manifest lacks host or CPU-affinity provenance")

    parameters = manifest.get("parameters", {})
    expected_parameters = {
        "field_degree": 51,
        "field_reduction_mask": 75,
        "subgroup_order": spec["curve_family"]["subgroup_order"],
        "cofactor": spec["curve_family"]["cofactor"],
        "ambient_order": spec["curve_family"]["ambient_order"],
        "a2": 0,
    }
    for field, expected in expected_parameters.items():
        if int(parameters.get(field, -1)) != expected:
            raise ValueError(f"run manifest parameter {field} differs from the frozen value")
    if parameters.get("field_polynomial") != "z^51 + z^6 + z^3 + z + 1":
        raise ValueError("run manifest field polynomial differs from the frozen value")

    execution = manifest.get("execution", {})
    expected_execution = {
        "records": spec["design"]["total_records"],
        "primary_blocks": spec["design"]["primary_target_blocks"],
        "aa_blocks": spec["design"]["aa_target_blocks"],
        "jobs_planned": 400,
        "jobs_completed": 400,
        "blocks_per_job": spec["design"]["blocks_per_job"],
        "max_workers": spec["design"]["max_workers"],
        "timeout_seconds_per_job": spec["design"]["timeout_seconds_per_job"],
        "schedule_root": spec["seeds"]["schedule_root"],
        "replacement_records": 0,
    }
    for field, expected in expected_execution.items():
        if int(execution.get(field, -1)) != expected:
            raise ValueError(f"run manifest execution field {field} differs from the frozen plan")
    for field in ("failed_jobs", "timed_out_jobs", "missing_jobs", "extra_jobs"):
        if execution.get(field) != []:
            raise ValueError(f"run manifest contains {field}")
    if execution.get("job_order") != "seeded_shuffle":
        raise ValueError("run manifest job ordering differs from the frozen plan")
    return manifest


def validate_certificates(
    path: Path,
    samples: dict[str, dict[str, Any]],
    floor_ids: list[str],
    setup_seed: int,
    manifest: dict[str, Any],
    spec: dict[str, Any],
) -> dict[str, Any]:
    document = read_json(path)
    if document.get("schema") != "m51-rho-certificates/v1":
        raise ValueError("unexpected certificate schema")
    expected_top_fields = set(spec["normalized_certificate_schema"]["top_level_fields"])
    if set(document) != expected_top_fields or not isinstance(document.get("created_utc"), str):
        raise ValueError("certificate top-level fields differ from the frozen schema")
    certificate_bindings = {
        "rho_source_sha256": spec["provenance"]["rho_source_sha256"],
        "params_source_sha256": spec["provenance"]["params_source_sha256"],
        "binary_sha256": manifest["build"]["binary_sha256"],
    }
    for field, expected in certificate_bindings.items():
        if document.get(field) != expected:
            raise ValueError(f"certificate {field} does not bind the run manifest")
    entries = document.get("entries")
    if not isinstance(entries, list):
        raise ValueError("certificate entries must be a list")
    required_pairs = {
        ("m51-crater", 0),
        ("m51-crater", 1),
        ("m51-crater", 2),
        *((curve_id, mode) for curve_id in floor_ids for mode in (0, 2)),
    }
    by_pair: dict[tuple[str, int], dict[str, Any]] = {}
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != set(
            spec["normalized_certificate_schema"]["fields"]
        ):
            raise ValueError("certificate entry fields differ from the frozen schema")
        for field in (
            "selftest_ok",
            "b",
            "a2",
            "mode",
            "action_step",
            "action_order",
            "setup_seed",
            "pgen_x",
            "pgen_y",
        ):
            require_json_uint64(entry[field], f"certificate {entry.get('curve_id')}:{field}")
        pair = (str(entry["curve_id"]), entry["mode"])
        if pair in by_pair:
            raise ValueError(f"duplicate certificate {pair}")
        by_pair[pair] = entry
    if set(by_pair) != required_pairs:
        missing = sorted(required_pairs - set(by_pair))
        extra = sorted(set(by_pair) - required_pairs)
        raise ValueError(f"certificate pair mismatch; missing={missing}, extra={extra}")

    curve_fingerprints: dict[str, set[tuple[int, int, str]]] = defaultdict(set)
    for (curve_id, mode), entry in by_pair.items():
        sample = samples[curve_id]
        step, order = CORE_ACTION[mode]
        if int(entry["selftest_ok"]) != 1:
            raise ValueError(f"failed selftest certificate for {curve_id}, mode {mode}")
        exact = {
            "b": sample["b"],
            "a2": sample["a2"],
            "mode": mode,
            "action_step": step,
            "action_order": order,
            "setup_seed": setup_seed,
        }
        for field, expected in exact.items():
            if int(entry[field]) != expected:
                raise ValueError(
                    f"certificate {curve_id}, mode {mode}: {field}={entry[field]!r}, "
                    f"expected {expected}"
                )
        fingerprint = str(entry["setup_fingerprint"])
        if len(fingerprint) != 16 or any(c not in "0123456789abcdef" for c in fingerprint):
            raise ValueError(f"invalid setup fingerprint for {curve_id}, mode {mode}")
        state = (int(entry["pgen_x"]), int(entry["pgen_y"]), fingerprint)
        if not (0 < state[0] < (1 << 51)) or not (0 <= state[1] < (1 << 51)):
            raise ValueError(f"subgroup basis encoding out of range for {curve_id}, mode {mode}")
        curve_fingerprints[curve_id].add(state)
    unequal = [curve_id for curve_id, states in curve_fingerprints.items() if len(states) != 1]
    if unequal:
        raise ValueError(f"mode-dependent same-curve setup fingerprints: {unequal}")
    return document


def validate_records(
    records: list[dict[str, Any]],
    spec: dict[str, Any],
    samples: dict[str, dict[str, Any]],
) -> tuple[dict[tuple[str, int, str], dict[str, Any]], list[str]]:
    design = spec["design"]
    seeds = spec["seeds"]
    if len(records) != design["total_records"]:
        raise ValueError(f"found {len(records)} records, expected {design['total_records']}")
    by_key: dict[tuple[str, int, str], dict[str, Any]] = {}
    problems: list[str] = []
    for row in records:
        replicate = row["replicate"]
        arm = row["arm"]
        block_id = row["block_id"]
        if replicate not in {"primary", "aa-b"}:
            raise ValueError(f"unexpected replicate {replicate!r}")
        if arm not in ARM_IDS:
            raise ValueError(f"unexpected arm {arm!r}")
        if not 0 <= block_id < design["primary_target_blocks"]:
            raise ValueError(f"block outside frozen range: {block_id}")
        key = (replicate, block_id, arm)
        if key in by_key:
            raise ValueError(f"duplicate record {key}")
        by_key[key] = row

        curve_id, orbit_id = expected_curve_for_block(arm, block_id)
        sample = samples[curve_id]
        if row["curve_id"] != curve_id or row["orbit_id"] != orbit_id:
            raise ValueError(f"curve/orbit assignment mismatch in {key}")
        if row["b"] != sample["b"] or row["a2"] != sample["a2"]:
            raise ValueError(f"curve parameters mismatch in {key}")
        if row["mode"] != ARM_MODE[arm]:
            raise ValueError(f"mode mismatch in {key}")
        if row["target_index"] != block_id:
            raise ValueError(f"target/block mismatch in {key}")
        if row["run"] != block_id % design["blocks_per_job"]:
            raise ValueError(f"within-job run index mismatch in {key}")
        if row["setup_seed"] != seeds["setup_root"]:
            raise ValueError(f"setup seed mismatch in {key}")
        if row["target_seed"] != seeds["target_root"]:
            raise ValueError(f"target seed mismatch in {key}")
        expected_walk_root = (
            seeds["walk_primary_root"] if replicate == "primary" else seeds["walk_aa_root"]
        )
        if row["walk_seed"] != expected_walk_root:
            raise ValueError(f"walk seed mismatch in {key}")
        if replicate == "aa-b" and block_id % 256 >= design["aa_blocks_per_orbit"]:
            raise ValueError(f"A/A record is outside the frozen subset: {key}")
        expected_k = expected_target_scalar(
            seeds["target_root"],
            block_id,
            spec["curve_family"]["subgroup_order"],
        )
        if row["k"] != expected_k:
            raise ValueError(f"indexed planted scalar mismatch in {key}")
        expected_stream = expected_walk_stream(expected_walk_root, block_id)
        if row["walk_stream_seed"] != expected_stream:
            raise ValueError(f"indexed walk stream mismatch in {key}")
        if not row["ok"]:
            problems.append(f"failed planted-key verification: {key}")
        for field in INTEGER_FIELDS[11:]:
            if row[field] < 0:
                raise ValueError(f"negative counter {field} in {key}")
        if not math.isfinite(row["sec"]) or row["sec"] <= 0:
            raise ValueError(f"invalid seconds in {key}")
        identities = (
            (row["setup_ops"], row["setup_adds"] + row["setup_doubles"], "setup ops"),
            (row["walk_ops"], row["walk_adds"] + row["walk_doubles"], "walk ops"),
            (row["ops"], row["setup_ops"] + row["walk_ops"], "ops"),
            (row["adds"], row["setup_adds"] + row["walk_adds"], "adds"),
            (row["doubles"], row["setup_doubles"] + row["walk_doubles"], "doubles"),
            (row["ops"], row["adds"] + row["doubles"], "group ops"),
        )
        for actual, expected, label in identities:
            if actual != expected:
                raise ValueError(f"{label} counter identity failed in {key}")
        if row["setup_adds"] != 128 or row["setup_doubles"] != 34:
            raise ValueError(f"frozen target-setup count failed in {key}")
        if row["walk_ops"] <= 0 or row["walks"] <= 0:
            raise ValueError(f"empty collision walk in {key}")
        if row["abandoned"] > row["walks"] or row["useless"] > row["walks"]:
            raise ValueError(f"walk diagnostic count exceeds starts in {key}")
        if row["canon_sign_tests"] != row["canon_calls"]:
            raise ValueError(f"canonicalizer call/sign count failed in {key}")
        if row["canon_negations"] > row["canon_sign_tests"]:
            raise ValueError(f"canonicalizer negation count failed in {key}")
        if row["mode"] == 0:
            if row["canon_x_squares"] != 0 or row["canon_y_squares"] != 0:
                raise ValueError(f"mode-0 action squares are nonzero in {key}")
        elif row["mode"] == 1:
            if (
                row["canon_x_squares"] != 50 * row["canon_calls"]
                or row["canon_y_squares"] > 50 * row["canon_calls"]
            ):
                raise ValueError(f"mode-1 action primitive count failed in {key}")
        elif row["mode"] == 2:
            if (
                row["canon_x_squares"] != 34 * row["canon_calls"]
                or row["canon_y_squares"] % 17
                or row["canon_y_squares"] > 34 * row["canon_calls"]
            ):
                raise ValueError(f"mode-2 action primitive count failed in {key}")

    primary_blocks = range(design["primary_target_blocks"])
    aa_blocks = [
        block_id
        for block_id in primary_blocks
        if block_id % design["blocks_per_floor_orbit"] < design["aa_blocks_per_orbit"]
    ]
    for block_id in primary_blocks:
        rows = [by_key.get(("primary", block_id, arm)) for arm in ARM_IDS]
        if any(row is None for row in rows):
            raise ValueError(f"incomplete primary arm set for block {block_id}")
        assert all(row is not None for row in rows)
        if len({row["k"] for row in rows}) != 1:
            raise ValueError(f"planted scalar is not paired in block {block_id}")
        if len({row["target_seed"] for row in rows}) != 1:
            raise ValueError(f"target seed is not paired in block {block_id}")
        if len({row["walk_stream_seed"] for row in rows}) != 1:
            raise ValueError(f"primary walk stream is not paired in block {block_id}")
    for block_id in aa_blocks:
        for arm in ARM_IDS:
            a = by_key[("primary", block_id, arm)]
            b = by_key.get(("aa-b", block_id, arm))
            if b is None:
                raise ValueError(f"missing A/A B record for block {block_id}, arm {arm}")
            if (a["k"], a["curve_id"], a["setup_seed"], a["target_seed"]) != (
                b["k"],
                b["curve_id"],
                b["setup_seed"],
                b["target_seed"],
            ):
                raise ValueError(f"broken A/A pairing for block {block_id}, arm {arm}")
            if a["walk_stream_seed"] == b["walk_stream_seed"]:
                raise ValueError(f"A/A walk streams are not independent in block {block_id}, arm {arm}")
    if len(aa_blocks) != design["aa_target_blocks"]:
        raise ValueError("internal A/A subset size mismatch")
    expected_keys = design["primary_records"] + design["aa_extra_records"]
    if len(by_key) != expected_keys:
        raise ValueError("record key count differs from frozen design")
    if problems:
        raise ValueError("; ".join(problems[:20]))
    return by_key, aa_blocks


def block_arrays(
    by_key: dict[tuple[str, int, str], dict[str, Any]],
    replicate: str,
    block_ids: list[int],
    metric: str,
) -> dict[str, np.ndarray]:
    return {
        arm: np.asarray([by_key[(replicate, block_id, arm)][metric] for block_id in block_ids], dtype=np.float64)
        for arm in ARM_IDS
    }


def hierarchical_bootstrap_means(
    arrays: dict[str, np.ndarray],
    *,
    blocks_per_orbit: int,
    resamples: int,
    seed: int,
    batch: int = 64,
) -> tuple[list[str], np.ndarray]:
    names = list(arrays)
    matrix = np.vstack([arrays[name] for name in names])
    orbit_count = 16
    expected = orbit_count * blocks_per_orbit
    if matrix.shape[1] != expected:
        raise ValueError(f"bootstrap matrix has {matrix.shape[1]} blocks, expected {expected}")
    rng = np.random.default_rng(seed)
    output = np.empty((resamples, len(names)), dtype=np.float64)
    for start in range(0, resamples, batch):
        count = min(batch, resamples - start)
        orbit_draw = rng.integers(0, orbit_count, size=(count, orbit_count))
        within_draw = rng.integers(
            0,
            blocks_per_orbit,
            size=(count, orbit_count, blocks_per_orbit),
        )
        indices = orbit_draw[:, :, None] * blocks_per_orbit + within_draw
        output[start : start + count] = matrix[:, indices].mean(axis=(2, 3)).T
    return names, output


def fixed_orbit_bootstrap_means(
    arrays: dict[str, np.ndarray],
    *,
    blocks_per_orbit: int,
    resamples: int,
    seed: int,
    batch: int = 64,
) -> tuple[list[str], np.ndarray]:
    """Resample paired blocks within each of the 16 fixed sampled-orbit strata."""
    names = list(arrays)
    matrix = np.vstack([arrays[name] for name in names])
    orbit_count = 16
    expected = orbit_count * blocks_per_orbit
    if matrix.shape[1] != expected:
        raise ValueError(f"bootstrap matrix has {matrix.shape[1]} blocks, expected {expected}")
    rng = np.random.default_rng(seed)
    output = np.empty((resamples, len(names)), dtype=np.float64)
    orbit_offsets = np.arange(orbit_count, dtype=np.int64)[None, :, None] * blocks_per_orbit
    for start in range(0, resamples, batch):
        count = min(batch, resamples - start)
        within_draw = rng.integers(
            0,
            blocks_per_orbit,
            size=(count, orbit_count, blocks_per_orbit),
        )
        indices = orbit_offsets + within_draw
        output[start : start + count] = matrix[:, indices].mean(axis=(2, 3)).T
    return names, output


def percentile(values: np.ndarray, confidence: float) -> tuple[float, float]:
    alpha = 1.0 - confidence
    low, high = np.quantile(values, [alpha / 2.0, 1.0 - alpha / 2.0])
    return float(low), float(high)


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    if path.exists():
        raise FileExistsError(f"refusing to overwrite {path}")
    with path.open("x", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def json_ready(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): json_ready(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_ready(v) for v in value]
    if isinstance(value, np.generic):
        return value.item()
    return value


def main() -> None:
    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument(
        "--run-root",
        type=Path,
        required=True,
        help="sealed output root created by run_replication.py",
    )
    parser.add_argument("--spec", type=Path, default=HERE / "spec.json")
    parser.add_argument("--sample", type=Path, default=HERE / "sample.csv")
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    run_root = args.run_root.resolve()
    if not run_root.is_dir():
        raise ValueError(f"run root is not a directory: {run_root}")
    records_path = run_root / "records.csv"
    certificates_path = run_root / "certificates.json"
    manifest_path = run_root / "run_manifest.json"
    output_dir = args.output_dir.resolve()
    if output_dir == run_root or run_root in output_dir.parents:
        raise ValueError("analysis outputs must be outside the sealed run root")

    spec = read_json(args.spec)
    if spec.get("schema") != "m51-volcano-rho-study/v1":
        raise ValueError("unexpected study spec schema")
    samples, floor_ids = read_sample(args.sample)
    manifest = validate_manifest(
        manifest_path,
        spec=spec,
        spec_path=args.spec,
        sample_path=args.sample,
        records_path=records_path,
        certificates_path=certificates_path,
    )
    certificates = validate_certificates(
        certificates_path,
        samples,
        floor_ids,
        int(spec["seeds"]["setup_root"]),
        manifest,
        spec,
    )
    records = read_records(records_path, spec["normalized_record_schema"])
    by_key, aa_blocks = validate_records(records, spec, samples)
    archive_validation = validate_run_archive(
        run_root,
        spec=spec,
        samples=samples,
        floor_ids=floor_ids,
        manifest=manifest,
        certificates=certificates,
        records_path=records_path,
        by_key=by_key,
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    output_paths = {
        name: output_dir / name
        for name in (
            "analysis.json",
            "arm_summary.csv",
            "contrast_summary.csv",
            "orbit_summary.csv",
            "orbit_arm_summary.csv",
            "aa_summary.csv",
        )
    }
    existing = [str(path) for path in output_paths.values() if path.exists()]
    if existing:
        raise FileExistsError(f"refusing to overwrite analysis outputs: {existing}")

    design = spec["design"]
    all_a_blocks = list(range(design["primary_target_blocks"]))
    aa_set = set(aa_blocks)
    inferential_blocks = [
        block_id
        for block_id in all_a_blocks
        if block_id % design["blocks_per_floor_orbit"] >= design["aa_blocks_per_orbit"]
    ]
    if (
        len(inferential_blocks) != design["inferential_target_blocks"]
        or len(aa_blocks) != design["aa_target_blocks"]
        or set(inferential_blocks) & aa_set
        or set(inferential_blocks) | aa_set != set(all_a_blocks)
    ):
        raise ValueError("inferential and held-out A/A subsets do not exactly partition A-stream blocks")
    if list(spec["accounting"]["distribution_summary_metrics"]) != list(SUMMARY_METRICS):
        raise ValueError("distribution summary metric contract differs from analyzer implementation")
    resamples = int(spec["estimand"]["bootstrap_resamples"])
    root_seed = int(spec["seeds"]["bootstrap_root"])
    inferential_per_orbit = int(design["inferential_blocks_per_floor_orbit"])
    walk_arrays = block_arrays(by_key, "primary", inferential_blocks, "walk_ops")
    ops_arrays = block_arrays(by_key, "primary", inferential_blocks, "ops")
    boot_names, walk_boot = fixed_orbit_bootstrap_means(
        walk_arrays,
        blocks_per_orbit=inferential_per_orbit,
        resamples=resamples,
        seed=root_seed,
    )
    ops_names, ops_boot = fixed_orbit_bootstrap_means(
        ops_arrays,
        blocks_per_orbit=inferential_per_orbit,
        resamples=resamples,
        seed=root_seed + 1,
    )
    sensitivity_names, walk_sensitivity_boot = hierarchical_bootstrap_means(
        walk_arrays,
        blocks_per_orbit=inferential_per_orbit,
        resamples=resamples,
        seed=root_seed + 100,
    )
    ops_sensitivity_names, ops_sensitivity_boot = hierarchical_bootstrap_means(
        ops_arrays,
        blocks_per_orbit=inferential_per_orbit,
        resamples=resamples,
        seed=root_seed + 101,
    )
    if not (boot_names == ops_names == sensitivity_names == ops_sensitivity_names):
        raise AssertionError("bootstrap arm order changed")
    arm_index = {arm: i for i, arm in enumerate(boot_names)}

    arm_rows: list[dict[str, Any]] = []
    for arm in ARM_IDS:
        arm_records = [by_key[("primary", block_id, arm)] for block_id in inferential_blocks]
        row: dict[str, Any] = {
            "arm": arm,
            "analysis_set": "inferential_offsets_64_255",
            "n": len(arm_records),
        }
        for metric in SUMMARY_METRICS:
            values = np.asarray([record[metric] for record in arm_records], dtype=np.float64)
            row[f"mean_{metric}"] = float(values.mean())
            row[f"sd_{metric}"] = float(values.std(ddof=1))
            quantiles = np.quantile(values, [0.05, 0.25, 0.50, 0.75, 0.95])
            for label, value in zip(("p05", "p25", "p50", "p75", "p95"), quantiles):
                row[f"{label}_{metric}"] = float(value)
        walk_low, walk_high = percentile(walk_boot[:, arm_index[arm]], 0.95)
        ops_low, ops_high = percentile(ops_boot[:, arm_index[arm]], 0.95)
        walk_sensitivity_low, walk_sensitivity_high = percentile(
            walk_sensitivity_boot[:, arm_index[arm]], 0.95
        )
        ops_sensitivity_low, ops_sensitivity_high = percentile(
            ops_sensitivity_boot[:, arm_index[arm]], 0.95
        )
        row.update(
            {
                "mean_walk_ops_ci95_low": walk_low,
                "mean_walk_ops_ci95_high": walk_high,
                "mean_ops_ci95_low": ops_low,
                "mean_ops_ci95_high": ops_high,
                "mean_walk_ops_hierarchical_sensitivity_ci95_low": walk_sensitivity_low,
                "mean_walk_ops_hierarchical_sensitivity_ci95_high": walk_sensitivity_high,
                "mean_ops_hierarchical_sensitivity_ci95_low": ops_sensitivity_low,
                "mean_ops_hierarchical_sensitivity_ci95_high": ops_sensitivity_high,
            }
        )
        arm_rows.append(row)

    contrast_rows: list[dict[str, Any]] = []
    contrast_boot: dict[str, np.ndarray] = {}
    contrast_specs = spec["contrasts"]
    for contrast in contrast_specs:
        numerator = contrast["numerator"]
        denominator = contrast["denominator"]
        point = math.log2(walk_arrays[numerator].mean() / walk_arrays[denominator].mean())
        samples_bits = np.log2(
            walk_boot[:, arm_index[numerator]] / walk_boot[:, arm_index[denominator]]
        )
        sensitivity_samples_bits = np.log2(
            walk_sensitivity_boot[:, arm_index[numerator]]
            / walk_sensitivity_boot[:, arm_index[denominator]]
        )
        contrast_boot[contrast["id"]] = samples_bits
        point_low, point_high = percentile(samples_bits, 0.95)
        sensitivity_point_low, sensitivity_point_high = percentile(
            sensitivity_samples_bits, 0.95
        )
        if contrast["tier"] == "secondary":
            family_confidence = 1.0 - 0.05 / 4.0
        else:
            family_confidence = 0.95
        family_low, family_high = percentile(samples_bits, family_confidence)
        sensitivity_family_low, sensitivity_family_high = percentile(
            sensitivity_samples_bits, family_confidence
        )
        predicted = float(contrast["predicted_bits"])
        row = {
            "contrast_id": contrast["id"],
            "tier": contrast["tier"],
            "numerator": numerator,
            "denominator": denominator,
            "analysis_set": "inferential_offsets_64_255",
            "bootstrap_scope": "fixed_16_orbit_exact_sample",
            "n_blocks": len(inferential_blocks),
            "numerator_mean_walk_ops": float(walk_arrays[numerator].mean()),
            "denominator_mean_walk_ops": float(walk_arrays[denominator].mean()),
            "observed_bits": point,
            "ci95_low": point_low,
            "ci95_high": point_high,
            "family_confidence": family_confidence,
            "family_ci_low": family_low,
            "family_ci_high": family_high,
            "hierarchical_sensitivity_scope": "modeled_orbit_superpopulation",
            "hierarchical_sensitivity_ci95_low": sensitivity_point_low,
            "hierarchical_sensitivity_ci95_high": sensitivity_point_high,
            "hierarchical_sensitivity_family_ci_low": sensitivity_family_low,
            "hierarchical_sensitivity_family_ci_high": sensitivity_family_high,
            "predicted_bits": predicted,
            "prediction_residual_bits": point - predicted,
            "prediction_residual_ci95_low": point_low - predicted,
            "prediction_residual_ci95_high": point_high - predicted,
            "prediction_residual_family_ci_low": family_low - predicted,
            "prediction_residual_family_ci_high": family_high - predicted,
            "prediction_residual_hierarchical_sensitivity_ci95_low": sensitivity_point_low
            - predicted,
            "prediction_residual_hierarchical_sensitivity_ci95_high": sensitivity_point_high
            - predicted,
            "prediction_residual_hierarchical_sensitivity_family_ci_low": sensitivity_family_low
            - predicted,
            "prediction_residual_hierarchical_sensitivity_family_ci_high": sensitivity_family_high
            - predicted,
            "prediction_in_family_interval": family_low <= predicted <= family_high,
        }
        contrast_rows.append(row)

    orbit_rows: list[dict[str, Any]] = []
    per_orbit = inferential_per_orbit
    for orbit_id in range(1, 17):
        start = (orbit_id - 1) * per_orbit
        stop = start + per_orbit
        for contrast in contrast_specs:
            numerator = contrast["numerator"]
            denominator = contrast["denominator"]
            num_mean = float(walk_arrays[numerator][start:stop].mean())
            den_mean = float(walk_arrays[denominator][start:stop].mean())
            bits = math.log2(num_mean / den_mean)
            orbit_rows.append(
                {
                    "orbit_id": orbit_id,
                    "curve_id": floor_ids[orbit_id - 1],
                    "b": samples[floor_ids[orbit_id - 1]]["b"],
                    "contrast_id": contrast["id"],
                    "tier": contrast["tier"],
                    "scope": "descriptive_exploratory",
                    "analysis_set": "inferential_offsets_64_255",
                    "n_blocks": per_orbit,
                    "numerator_mean_walk_ops": num_mean,
                    "denominator_mean_walk_ops": den_mean,
                    "observed_bits": bits,
                    "predicted_bits": contrast["predicted_bits"],
                    "prediction_residual_bits": bits - contrast["predicted_bits"],
                }
            )

    orbit_arm_rows: list[dict[str, Any]] = []
    for orbit_id in range(1, 17):
        orbit_block_ids = inferential_blocks[
            (orbit_id - 1) * per_orbit : orbit_id * per_orbit
        ]
        if len(orbit_block_ids) != per_orbit or any(
            1 + block_id // design["blocks_per_floor_orbit"] != orbit_id
            for block_id in orbit_block_ids
        ):
            raise AssertionError("inferential blocks are not contiguous in orbit-major order")
        floor_curve_id = floor_ids[orbit_id - 1]
        for arm in ARM_IDS:
            arm_records = [
                by_key[("primary", block_id, arm)] for block_id in orbit_block_ids
            ]
            row: dict[str, Any] = {
                "orbit_id": orbit_id,
                "floor_curve_id": floor_curve_id,
                "floor_b": samples[floor_curve_id]["b"],
                "arm": arm,
                "scope": "descriptive_distribution",
                "analysis_set": "inferential_offsets_64_255",
                "n": len(arm_records),
            }
            for metric in SUMMARY_METRICS:
                values = np.asarray(
                    [record[metric] for record in arm_records], dtype=np.float64
                )
                row[f"mean_{metric}"] = float(values.mean())
                row[f"sd_{metric}"] = float(values.std(ddof=1))
                quantiles = np.quantile(values, [0.05, 0.25, 0.50, 0.75, 0.95])
                for label, value in zip(
                    ("p05", "p25", "p50", "p75", "p95"), quantiles
                ):
                    row[f"{label}_{metric}"] = float(value)
            orbit_arm_rows.append(row)

    aa_primary = block_arrays(by_key, "primary", aa_blocks, "walk_ops")
    aa_b = block_arrays(by_key, "aa-b", aa_blocks, "walk_ops")
    aa_combined = {
        **{f"{arm}:a": aa_primary[arm] for arm in ARM_IDS},
        **{f"{arm}:b": aa_b[arm] for arm in ARM_IDS},
    }
    aa_names, aa_boot = fixed_orbit_bootstrap_means(
        aa_combined,
        blocks_per_orbit=spec["design"]["aa_blocks_per_orbit"],
        resamples=resamples,
        seed=root_seed + 2,
    )
    aa_sensitivity_names, aa_sensitivity_boot = hierarchical_bootstrap_means(
        aa_combined,
        blocks_per_orbit=spec["design"]["aa_blocks_per_orbit"],
        resamples=resamples,
        seed=root_seed + 102,
    )
    if aa_names != aa_sensitivity_names:
        raise AssertionError("A/A bootstrap arm order changed")
    aa_index = {name: i for i, name in enumerate(aa_names)}
    aa_rows: list[dict[str, Any]] = []
    aa_all_pass = True
    aa_confidence = 1.0 - 0.05 / 5.0
    aa_margin = float(spec["estimand"]["aa_family_margin_bits"])
    for arm in ARM_IDS:
        point = math.log2(aa_b[arm].mean() / aa_primary[arm].mean())
        bits_samples = np.log2(
            aa_boot[:, aa_index[f"{arm}:b"]] / aa_boot[:, aa_index[f"{arm}:a"]]
        )
        low, high = percentile(bits_samples, aa_confidence)
        sensitivity_bits_samples = np.log2(
            aa_sensitivity_boot[:, aa_index[f"{arm}:b"]]
            / aa_sensitivity_boot[:, aa_index[f"{arm}:a"]]
        )
        sensitivity_low, sensitivity_high = percentile(
            sensitivity_bits_samples, aa_confidence
        )
        passed = low >= -aa_margin and high <= aa_margin
        aa_all_pass = aa_all_pass and passed
        aa_rows.append(
            {
                "arm": arm,
                "analysis_set": "held_out_offsets_0_63",
                "bootstrap_scope": "fixed_16_orbit_exact_sample",
                "n_blocks": len(aa_blocks),
                "a_mean_walk_ops": float(aa_primary[arm].mean()),
                "b_mean_walk_ops": float(aa_b[arm].mean()),
                "b_over_a_bits": point,
                "family_confidence": aa_confidence,
                "family_ci_low": low,
                "family_ci_high": high,
                "hierarchical_sensitivity_scope": "modeled_orbit_superpopulation",
                "hierarchical_sensitivity_family_ci_low": sensitivity_low,
                "hierarchical_sensitivity_family_ci_high": sensitivity_high,
                "margin_low": -aa_margin,
                "margin_high": aa_margin,
                "pass": passed,
            }
        )

    primary = next(row for row in contrast_rows if row["tier"] == "primary")
    margin = float(spec["estimand"]["equivalence_margin_bits"])
    if not aa_all_pass:
        for row in contrast_rows:
            row["inference_status"] = "WITHHELD_AA_ALERT"
            row["prediction_in_family_interval"] = None
        primary_label = "WITHHELD_AA_ALERT"
        primary_equivalence_met = None
        primary_direction = "WITHHELD_AA_ALERT"
        status = "A/A_ALERT"
    else:
        for row in contrast_rows:
            row["inference_status"] = "AVAILABLE_IN_TESTED_SCOPE"
        status = "VALID_FOR_SCOPED_INFERENCE"
        primary_equivalence_met = (
            primary["ci95_low"] >= -margin and primary["ci95_high"] <= margin
        )
        if primary["ci95_low"] > 0:
            primary_direction = "POSITIVE_SAME_ACTION_MODEL_ASSOCIATION_IN_TESTED_SCOPE"
        elif primary["ci95_high"] < 0:
            primary_direction = "NEGATIVE_SAME_ACTION_MODEL_ASSOCIATION_IN_TESTED_SCOPE"
        else:
            primary_direction = "ZERO_NOT_EXCLUDED"
        if primary_equivalence_met:
            primary_label = "WITHIN_PREDECLARED_0.10_BIT_BAND"
        elif primary_direction != "ZERO_NOT_EXCLUDED":
            primary_label = primary_direction
        else:
            primary_label = "INCONCLUSIVE_FOR_0.10_BIT_BAND"

    arm_fields = list(arm_rows[0])
    contrast_fields = list(contrast_rows[0])
    orbit_fields = list(orbit_rows[0])
    orbit_arm_fields = list(orbit_arm_rows[0])
    aa_fields = list(aa_rows[0])
    write_csv(output_paths["arm_summary.csv"], arm_rows, arm_fields)
    write_csv(output_paths["contrast_summary.csv"], contrast_rows, contrast_fields)
    write_csv(output_paths["orbit_summary.csv"], orbit_rows, orbit_fields)
    write_csv(
        output_paths["orbit_arm_summary.csv"], orbit_arm_rows, orbit_arm_fields
    )
    write_csv(output_paths["aa_summary.csv"], aa_rows, aa_fields)

    analysis = {
        "schema": "m51-volcano-rho-analysis/v1",
        "study_id": spec["study_id"],
        "status": status,
        "primary_label": primary_label,
        "primary_equivalence_met": primary_equivalence_met,
        "primary_direction": primary_direction,
        "claim_boundary": spec["claim_boundary"],
        "inputs": {
            "run_root": str(run_root),
            "records": str(records_path),
            "records_sha256": sha256_file(records_path),
            "certificates": str(certificates_path),
            "certificates_sha256": sha256_file(certificates_path),
            "manifest": str(manifest_path),
            "manifest_sha256": sha256_file(manifest_path),
            "spec": str(args.spec),
            "spec_sha256": sha256_file(args.spec),
            "sample": str(args.sample),
            "sample_sha256": sha256_file(args.sample),
            "archive_validation": archive_validation,
        },
        "counts": {
            "records": len(records),
            "executed_a_stream_blocks": len(all_a_blocks),
            "inferential_blocks": len(inferential_blocks),
            "aa_holdout_blocks": len(aa_blocks),
            "floor_orbits": 16,
        },
        "inference": {
            "estimand": spec["estimand"]["definition"],
            "primary_bootstrap": spec["estimand"]["bootstrap"],
            "hierarchical_sensitivity_bootstrap": spec["estimand"][
                "hierarchical_sensitivity_bootstrap"
            ],
            "inferential_subset": spec["design"]["inferential_subset"],
            "aa_holdout_subset": spec["design"]["aa_subset"],
            "resamples": resamples,
            "root_seed": root_seed,
            "aa_all_pass": aa_all_pass,
            "causal_boundary": (
                "Same-action association among the fixed sampled crater/floor models only; "
                "curve/model choice, generator construction, and hash behavior remain bundled, "
                "so this does not isolate a causal conductor effect."
            ),
            "weakness_claim": "not assessed",
            "transfer_claim": "not assessed",
            "end_to_end_cost": "not measured",
        },
        "arm_summary": arm_rows,
        "contrasts": contrast_rows,
        "orbit_contrasts": orbit_rows,
        "orbit_arm_distributions": orbit_arm_rows,
        "aa": aa_rows,
        "unmeasured_exclusions": spec["accounting"]["unmeasured_exclusions"],
    }
    output_paths["analysis.json"].write_text(
        json.dumps(json_ready(analysis), indent=2, sort_keys=True) + "\n"
    )


if __name__ == "__main__":
    main()
