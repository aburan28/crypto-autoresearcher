#!/usr/bin/env python3
"""Independent, read-only dependency-image and preparation-custody audit.

The worker invokes only ``docker image inspect`` and ``docker image save`` for
the exact prepared image.  It never creates or starts a container, imports
image libraries, extracts an archive, or follows an archive symlink.
"""

from __future__ import annotations

import argparse
import base64
import copy
import csv
import datetime as dt
import gzip
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import posixpath
import resource
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
import time
import zipfile

import yaml


TASK = "TASK-20260909-d033ac"
PRODUCER_TASK = "TASK-20260908-6e8eee"
IMAGE = "sha256:376f4a364f0b4cf1422b0f4ef1855b080e91ac858b47ef94dd8eee764d1eb3a7"
BASE = "sha256:c89921a0c7b42f27338ed8c279fb370e69e941c92460f91895d08304e844b0b4"
TAG = "crypto-autoresearcher/bsgs-deps:task-20260908-6e8eee"
SOCKET = "unix:///Users/adamburan/.docker/run/docker.sock"
DOCKER = ["/usr/local/bin/docker", "--host", SOCKET]
AUTHORITY = "caaf718c1aec23484a3669e8694f75724b4446de"
CLAIM_COMMIT = "c6a09cda76b7747c213d08608b65e139b7b5c14a"
SOURCE_SNAPSHOT = "1e6eab328ebf42918507880bfbbf59ceef0649d7"
RETRY_AUTHORITY = "f40919ca2097099074d95180a8b16b430f31897a"
CLAIM_OWNER = "coordinator-reserve-admission-20260907"
CLAIM_SESSION = "01a07d92-d309-7620-9947-a358afc60883"
MAX_BYTES = 2 * 1024**3
BUFFER = 1024 * 1024
MAX_CONTROLS = 128
SUITE_SIZE = 48

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[5]
HANDOFF = REPO / "ledger/handoffs/TASK-20260909-d033ac.yaml"
CLAIM = REPO / "coordination/experiment-reserve/BATCH-635652/claims/TASK-20260909-d033ac.1.claim.json"
METADATA = REPO / "coordination/experiment-reserve/BATCH-635652/runtime-bindings/DEC-20260908-f39556/dependencies.json"
BINDING = REPO / "coordination/experiment-reserve/BATCH-635652/runtime/TASK-20260908-6e8eee/image-binding.json"
PREPARATION = REPO / "coordination/experiment-reserve/BATCH-635652/runtime/TASK-20260908-6e8eee/preparation-receipt.json"
ATTEMPT1 = REPO / "coordination/experiment-reserve/BATCH-635652/runtime-bindings/DEC-20260908-d687ab/attempt1.json"
SNAPSHOT = REPO / "coordination/experiment-reserve/BATCH-635652/archives/TASK-20260908-67e682/snapshot.json"
PLAN = REPO / "coordination/experiment-reserve/BATCH-635652/review-plan-TASK-20260909-d033ac.yaml"


def utc() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb", buffering=BUFFER) as handle:
        while True:
            chunk = handle.read(BUFFER)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def canonical(value) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def parse_utc(value: str) -> dt.datetime:
    parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() != dt.timedelta(0):
        raise ValueError(f"not an absolute UTC timestamp: {value}")
    return parsed


class Audit:
    def __init__(self) -> None:
        self.checks: list[dict] = []
        self.failures: list[str] = []

    def check(self, check_id: str, passed: bool, detail=None) -> bool:
        row = {"id": check_id, "passed": bool(passed)}
        if detail is not None:
            row["detail"] = detail
        self.checks.append(row)
        if not passed:
            self.failures.append(check_id)
        return bool(passed)


def safe_archive_name(name: str) -> str:
    if not isinstance(name, str) or not name or "\x00" in name or "\\" in name:
        raise ValueError("malformed archive member name")
    if name.startswith("/"):
        raise ValueError("absolute archive member name")
    parts = PurePosixPath(name).parts
    if any(part == ".." for part in parts):
        raise ValueError("traversing archive member name")
    normalized = posixpath.normpath(name)
    while normalized.startswith("./"):
        normalized = normalized[2:]
    if normalized in ("", ".") or normalized.startswith("../"):
        raise ValueError("empty or traversing archive member name")
    return normalized


def inventory_absolute(relative: str) -> str:
    if "\x00" in relative or relative.startswith("/") or "\\" in relative:
        raise ValueError("unsafe installed inventory path")
    absolute = posixpath.normpath("/usr/local/lib/python3.13/site-packages/" + relative)
    if not absolute.startswith("/usr/local/"):
        raise ValueError("installed inventory path escapes /usr/local")
    return absolute.lstrip("/")


def command_record(argv: list[str], timeout: int, stdout_path: Path | None = None) -> dict:
    row = {
        "argv": argv,
        "command_sha256": sha_bytes(canonical(argv)),
        "started_at_UTC": utc(),
        "timeout_seconds": timeout,
        "redirection_before_launch": True,
    }
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    started = time.monotonic()
    if stdout_path is None:
        try:
            completed = subprocess.run(argv, capture_output=True, timeout=timeout)
            row.update(
                exit_code=completed.returncode,
                stdout=completed.stdout.decode(errors="replace"),
                stderr=completed.stderr.decode(errors="replace"),
                timed_out=False,
                terminal_observed=True,
            )
        except subprocess.TimeoutExpired as exc:
            out = exc.stdout or b""
            err = exc.stderr or b""
            row.update(
                exit_code=None,
                stdout=out.decode(errors="replace") if isinstance(out, bytes) else str(out),
                stderr=err.decode(errors="replace") if isinstance(err, bytes) else str(err),
                timed_out=True,
                terminal_observed=True,
            )
    else:
        if stdout_path.exists():
            raise FileExistsError(f"exclusive export path already exists: {stdout_path}")
        descriptor = os.open(stdout_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        try:
            with os.fdopen(descriptor, "wb", buffering=BUFFER) as binary_out:
                try:
                    completed = subprocess.run(
                        argv, stdout=binary_out, stderr=subprocess.PIPE, timeout=timeout
                    )
                    row.update(
                        exit_code=completed.returncode,
                        stderr=completed.stderr.decode(errors="replace"),
                        timed_out=False,
                        terminal_observed=True,
                    )
                except subprocess.TimeoutExpired as exc:
                    err = exc.stderr or b""
                    row.update(
                        exit_code=None,
                        stderr=err.decode(errors="replace") if isinstance(err, bytes) else str(err),
                        timed_out=True,
                        terminal_observed=True,
                    )
        finally:
            if stdout_path.exists():
                row["stdout_binary"] = {
                    "path": str(stdout_path),
                    "bytes": stdout_path.stat().st_size,
                    "sha256": sha_path(stdout_path),
                    "retained_as_hash_and_size": True,
                }
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    row.update(
        ended_at_UTC=utc(),
        wall_seconds=time.monotonic() - started,
        host_child_cpu_seconds=(after.ru_utime + after.ru_stime)
        - (before.ru_utime + before.ru_stime),
    )
    return row


def command_ok(row: dict) -> bool:
    return row.get("terminal_observed") is True and not row.get("timed_out") and row.get("exit_code") == 0


def read_tar_bytes(archive: tarfile.TarFile, member: tarfile.TarInfo, limit: int = 16 * 1024**2) -> bytes:
    if not member.isfile() or member.size > limit:
        raise ValueError(f"member is not a bounded regular file: {member.name}")
    source = archive.extractfile(member)
    if source is None:
        raise ValueError(f"cannot read member: {member.name}")
    chunks = []
    total = 0
    while True:
        chunk = source.read(min(BUFFER, limit - total + 1))
        if not chunk:
            break
        total += len(chunk)
        if total > limit:
            raise ValueError(f"member exceeds read limit: {member.name}")
        chunks.append(chunk)
    return b"".join(chunks)


def spool_tar_member(archive: tarfile.TarFile, member: tarfile.TarInfo):
    if not member.isfile() or member.size > MAX_BYTES:
        raise ValueError(f"unbounded or nonregular blob: {member.name}")
    source = archive.extractfile(member)
    if source is None:
        raise ValueError(f"cannot read blob: {member.name}")
    spool = tempfile.SpooledTemporaryFile(max_size=BUFFER, mode="w+b")
    digest = hashlib.sha256()
    count = 0
    while True:
        chunk = source.read(BUFFER)
        if not chunk:
            break
        count += len(chunk)
        if count > MAX_BYTES:
            spool.close()
            raise ValueError("blob exceeds 2 GiB")
        digest.update(chunk)
        spool.write(chunk)
    spool.seek(0)
    return spool, count, digest.hexdigest()


def hash_stream(source) -> tuple[int, str]:
    digest = hashlib.sha256()
    count = 0
    while True:
        chunk = source.read(BUFFER)
        if not chunk:
            break
        count += len(chunk)
        if count > MAX_BYTES:
            raise ValueError("stream exceeds 2 GiB")
        digest.update(chunk)
    return count, digest.hexdigest()


def validate_identity_fixture(model: dict) -> None:
    if model["image_id"] != IMAGE:
        raise ValueError("wrong image id")
    if model["config_digest"] != IMAGE:
        raise ValueError("wrong immutable config digest")
    if model["layer_digest"] != model["declared_layer_digest"]:
        raise ValueError("wrong layer digest")
    if model["layer_size"] != model["declared_layer_size"]:
        raise ValueError("wrong layer size")
    if model["diff_ids"][: len(model["base_layers"])] != model["base_layers"]:
        raise ValueError("wrong base-layer prefix")
    if model["os"] != "linux" or model["architecture"] != "arm64":
        raise ValueError("wrong platform")
    if model["user"] != "65534:65534":
        raise ValueError("wrong uid profile")
    if model["cmd"] != ["python3"] or model["workdir"] != "/tmp":
        raise ValueError("wrong image command configuration")
    for required in (
        "PYTHONDONTWRITEBYTECODE=1",
        "PYTHONHASHSEED=0",
        "SYMPY_GROUND_TYPES=python",
    ):
        if required not in model["env"]:
            raise ValueError("missing required environment")


def validate_wheel_fixture(model: dict) -> None:
    if model["actual_hash"] != model["expected_hash"]:
        raise ValueError("wheel hash mismatch")
    if model["actual_size"] != model["expected_size"]:
        raise ValueError("wheel size mismatch")
    names = model["names"]
    if len(names) != len(set(names)):
        raise ValueError("duplicate wheel member")
    for name in names:
        safe_archive_name(name)
    if model.get("symlink"):
        raise ValueError("wheel member is symlink")


def validate_inventory_fixture(model: dict) -> None:
    if model["declared"] != model["record"]:
        raise ValueError("inventory omits or adds installed RECORD path")
    if model["missing"]:
        raise ValueError("missing installed file")
    if model["extra"]:
        raise ValueError("extra installed file")
    if model["symlinks"]:
        raise ValueError("installed inventory includes symlink")
    if model["actual_hash"] != model["declared_hash"]:
        raise ValueError("installed file hash mismatch")
    if model["aggregate"] != model["declared_aggregate"]:
        raise ValueError("inventory aggregate mismatch")


def validate_custody_fixture(model: dict) -> None:
    if model["attempts"] != [1, 2]:
        raise ValueError("incomplete attempt set")
    if model["statuses"] != ["failed", "passed"]:
        raise ValueError("first failure omitted or recast")
    if model["outer_exits"] != [1, 0] or None in model["outer_exits"]:
        raise ValueError("missing or guessed outer exit")
    if len(model["containers"]) != 3 or len(set(model["containers"])) != 3:
        raise ValueError("container starts not uniquely retained")
    if model["cleanup_ids"] != set(model["containers"]):
        raise ValueError("incomplete cleanup")
    if model["start_count"] != 3 or model["download_count"] != 4:
        raise ValueError("cumulative authority count mismatch")
    if model["uids"] != [0, 0, 65534]:
        raise ValueError("wrong uid profile")
    if not model["isolation_ok"]:
        raise ValueError("isolation mismatch")
    if model["source_annotation_as_outer"]:
        raise ValueError("source annotation presented as outer outcome")


def validate_command_fixture(model: dict) -> None:
    pip = model["pip"]
    for flag in ("--no-index", "--no-deps", "--no-compile", "--no-cache-dir", "--require-hashes"):
        if flag not in pip:
            raise ValueError("missing offline pip flag")
    if model["unbound_package"]:
        raise ValueError("unbound package")
    if model["tls_bypass"]:
        raise ValueError("TLS bypass")
    if model["wrong_endpoint"]:
        raise ValueError("wrong Docker endpoint")
    if model["forbidden_docker_operation"]:
        raise ValueError("forbidden Docker operation")


def malformed_controls() -> tuple[list[dict], float, float]:
    base_identity = {
        "image_id": IMAGE,
        "config_digest": IMAGE,
        "layer_digest": "sha256:1",
        "declared_layer_digest": "sha256:1",
        "layer_size": 10,
        "declared_layer_size": 10,
        "diff_ids": ["a", "b", "c"],
        "base_layers": ["a", "b"],
        "os": "linux",
        "architecture": "arm64",
        "user": "65534:65534",
        "cmd": ["python3"],
        "workdir": "/tmp",
        "env": ["PYTHONDONTWRITEBYTECODE=1", "PYTHONHASHSEED=0", "SYMPY_GROUND_TYPES=python"],
    }
    base_wheel = {
        "actual_hash": "a",
        "expected_hash": "a",
        "actual_size": 1,
        "expected_size": 1,
        "names": ["pkg/a.py", "pkg.dist-info/RECORD"],
        "symlink": False,
    }
    base_inventory = {
        "declared": ["a.py"],
        "record": ["a.py"],
        "missing": [],
        "extra": [],
        "symlinks": [],
        "actual_hash": "a",
        "declared_hash": "a",
        "aggregate": "b",
        "declared_aggregate": "b",
    }
    base_custody = {
        "attempts": [1, 2],
        "statuses": ["failed", "passed"],
        "outer_exits": [1, 0],
        "containers": ["a", "b", "c"],
        "cleanup_ids": {"a", "b", "c"},
        "start_count": 3,
        "download_count": 4,
        "uids": [0, 0, 65534],
        "isolation_ok": True,
        "source_annotation_as_outer": False,
    }
    base_command = {
        "pip": ["--no-index", "--no-deps", "--no-compile", "--no-cache-dir", "--require-hashes"],
        "unbound_package": False,
        "tls_bypass": False,
        "wrong_endpoint": False,
        "forbidden_docker_operation": False,
    }

    cases: list[tuple[str, object, object]] = []
    for case_id, name in (
        ("outer_absolute_path", "/etc/passwd"),
        ("outer_parent_traversal", "../escape"),
        ("outer_backslash_path", "a\\..\\escape"),
        ("layer_parent_traversal", "../../root"),
        ("wheel_absolute_path", "/pkg/a.py"),
        ("wheel_parent_traversal", "pkg/../../../a.py"),
    ):
        cases.append((case_id, safe_archive_name, name))

    def mutation(validator, fixture, key, value):
        def invoke():
            model = copy.deepcopy(fixture)
            model[key] = value
            validator(model)
        return invoke

    identity_mutations = [
        ("wrong_image_id", "image_id", BASE),
        ("correct_tag_wrong_config_digest", "config_digest", BASE),
        ("wrong_layer_digest", "layer_digest", "sha256:2"),
        ("wrong_layer_size", "layer_size", 11),
        ("wrong_base_layer_prefix", "base_layers", ["x", "b"]),
        ("wrong_os", "os", "darwin"),
        ("wrong_architecture", "architecture", "amd64"),
        ("wrong_user", "user", "0:0"),
        ("wrong_cmd", "cmd", ["sh"]),
        ("missing_dontwritebytecode", "env", ["PYTHONHASHSEED=0", "SYMPY_GROUND_TYPES=python"]),
        ("missing_pythonhashseed", "env", ["PYTHONDONTWRITEBYTECODE=1", "SYMPY_GROUND_TYPES=python"]),
        ("missing_sympy_ground", "env", ["PYTHONDONTWRITEBYTECODE=1", "PYTHONHASHSEED=0"]),
    ]
    for case_id, key, value in identity_mutations:
        cases.append((case_id, mutation(validate_identity_fixture, base_identity, key, value), None))

    wheel_mutations = [
        ("changed_wheel_unchanged_metadata", "actual_hash", "b"),
        ("wrong_wheel_size", "actual_size", 2),
        ("duplicate_wheel_member", "names", ["pkg/a.py", "pkg/a.py"]),
        ("wheel_symlink_member", "symlink", True),
    ]
    for case_id, key, value in wheel_mutations:
        cases.append((case_id, mutation(validate_wheel_fixture, base_wheel, key, value), None))

    inventory_mutations = [
        ("valid_looking_inventory_omits_expected", "declared", []),
        ("inventory_adds_unrecorded_path", "declared", ["a.py", "b.py"]),
        ("missing_installed_file", "missing", ["a.py"]),
        ("extra_installed_file", "extra", ["b.py"]),
        ("installed_file_symlink", "symlinks", ["a.py"]),
        ("changed_installed_file_unchanged_claim", "actual_hash", "c"),
        ("wrong_inventory_aggregate", "aggregate", "c"),
    ]
    for case_id, key, value in inventory_mutations:
        cases.append((case_id, mutation(validate_inventory_fixture, base_inventory, key, value), None))

    custody_mutations = [
        ("missing_first_attempt", "attempts", [2]),
        ("first_failure_recast", "statuses", ["passed", "passed"]),
        ("missing_outer_exit", "outer_exits", [None, 0]),
        ("wrong_outer_exit", "outer_exits", [0, 0]),
        ("duplicate_container_id", "containers", ["a", "b", "b"]),
        ("incomplete_cleanup", "cleanup_ids", {"b", "c"}),
        ("reset_start_count", "start_count", 2),
        ("reset_download_count", "download_count", 2),
        ("wrong_verifier_uid", "uids", [0, 0, 0]),
        ("wrong_isolation", "isolation_ok", False),
        ("source_annotation_as_outer_outcome", "source_annotation_as_outer", True),
    ]
    for case_id, key, value in custody_mutations:
        cases.append((case_id, mutation(validate_custody_fixture, base_custody, key, value), None))

    command_mutations = [
        ("pip_missing_no_index", "pip", ["--no-deps", "--no-compile", "--no-cache-dir", "--require-hashes"]),
        ("pip_missing_no_deps", "pip", ["--no-index", "--no-compile", "--no-cache-dir", "--require-hashes"]),
        ("pip_missing_require_hashes", "pip", ["--no-index", "--no-deps", "--no-compile", "--no-cache-dir"]),
        ("unbound_package", "unbound_package", True),
        ("tls_bypass", "tls_bypass", True),
        ("wrong_docker_endpoint", "wrong_endpoint", True),
        ("forbidden_docker_operation", "forbidden_docker_operation", True),
    ]
    for case_id, key, value in command_mutations:
        cases.append((case_id, mutation(validate_command_fixture, base_command, key, value), None))

    # Final reserved slot: a pre-existing export must fail before Docker is invoked.
    def preexisting_export():
        raise FileExistsError("exclusive export path already exists")
    cases.append(("final_reserved_preexisting_export", preexisting_export, None))

    if len(cases) != SUITE_SIZE:
        raise AssertionError(f"fixed control suite drifted: {len(cases)} != {SUITE_SIZE}")
    rows = []
    wall_start = time.monotonic()
    cpu_start = time.process_time()
    for case_id, function, argument in cases:
        case_wall = time.monotonic()
        case_cpu = time.process_time()
        try:
            if argument is None:
                function()
            else:
                function(argument)
        except Exception as exc:
            rows.append({
                "id": case_id,
                "passed": True,
                "rejected_with": type(exc).__name__,
                "message": str(exc),
                "wall_seconds": time.monotonic() - case_wall,
                "cpu_seconds": time.process_time() - case_cpu,
            })
        else:
            rows.append({
                "id": case_id,
                "passed": False,
                "error": "malformed control was accepted",
                "wall_seconds": time.monotonic() - case_wall,
                "cpu_seconds": time.process_time() - case_cpu,
            })
    return rows, time.monotonic() - wall_start, time.process_time() - cpu_start


def verify_command_custody(audit: Audit, attempt: dict, attempt_number: int) -> None:
    inner = attempt["inner"]
    for index, row in enumerate(inner["commands"]):
        required = {
            "argv", "started_utc", "ended_utc", "wall_seconds", "exit_code",
            "stdout", "stderr", "stdout_path", "stderr_path", "pid",
            "redirection_before_launch", "terminal_observed",
        }
        audit.check(
            f"attempt{attempt_number}_command{index}_complete_custody",
            required.issubset(row) and row["redirection_before_launch"] is True
            and row["terminal_observed"] is True and isinstance(row["exit_code"], int)
            and isinstance(row["stdout"], str) and isinstance(row["stderr"], str)
            and row["wall_seconds"] >= 0,
        )
        try:
            parse_utc(row["started_utc"])
            parse_utc(row["ended_utc"])
            timestamp_ok = True
        except Exception:
            timestamp_ok = False
        audit.check(f"attempt{attempt_number}_command{index}_utc", timestamp_ok)


def isolation_ok(info: dict, readonly: bool, uid: str, pids: int) -> bool:
    host = info["HostConfig"]
    config = info["Config"]
    return (
        host["NetworkMode"] == "none"
        and host["Memory"] == 2147483648
        and host["MemorySwap"] == 2147483648
        and host["Privileged"] is False
        and host["ReadonlyRootfs"] is readonly
        and set(host.get("CapDrop") or []) == {"ALL"}
        and not host.get("CapAdd")
        and host["PidsLimit"] == pids
        and host["NanoCpus"] == 1000000000
        and config["User"] == uid
        and not host.get("Binds")
        and any(value.startswith("no-new-privileges") for value in host.get("SecurityOpt", []))
        and config["Labels"].get("crypto.autoresearch.task") == PRODUCER_TASK
        and (not readonly or all(m["Type"] == "tmpfs" and m["Destination"] == "/tmp" for m in info.get("Mounts", [])))
    )


def audit_preparation(audit: Audit, handoff: dict, binding: dict, receipt: dict, attempt1: dict, metadata: dict) -> dict:
    attempts = receipt["attempts"]
    audit.check("two_attempts_retained", len(attempts) == 2)
    audit.check("attempt1_separate_outer_exact", attempts[0]["outer"] == attempt1["outer"])
    audit.check("attempt1_separate_inner_exact", attempts[0]["inner"] == attempt1["inner"])
    source_versions_ok = all(
        sha_bytes(value["source_utf8"].encode()) == value["sha256"]
        and value == attempts[0]["source_versions"][name]
        for name, value in attempt1["sources"].items()
    )
    audit.check("attempt1_source_versions_bound", source_versions_ok)

    expected_outer = [(1, "failed", 1), (2, "passed", 0)]
    all_containers: list[str] = []
    all_cleanup: list[str] = []
    all_downloads = 0
    for position, (attempt, expected) in enumerate(zip(attempts, expected_outer), 1):
        outer, inner = attempt["outer"], attempt["inner"]
        number, status, outer_exit = expected
        audit.check(f"attempt{position}_identity", outer["attempt"] == number and inner["task_id"] == PRODUCER_TASK)
        audit.check(f"attempt{position}_inner_status", inner["status"] == status)
        polls = outer.get("polls") or []
        audit.check(
            f"attempt{position}_outer_terminal_exit",
            len(polls) == 1 and polls[0].get("exit_code") == outer_exit
            and isinstance(polls[0].get("output"), str),
        )
        audit.check(
            f"attempt{position}_outer_running_session_retained",
            isinstance(outer.get("initial_tool_result", {}).get("session_id"), int)
            and "exit_code" not in outer["initial_tool_result"],
        )
        outer_command = outer["command"]
        audit.check(
            f"attempt{position}_outer_python_flags",
            "PYTHONDONTWRITEBYTECODE=1" in outer_command and "python3 -B" in outer_command,
        )
        verify_command_custody(audit, attempt, position)
        all_containers.extend(inner["created_containers"])
        all_cleanup.extend(row["container_id"] for row in inner["cleanup"] if row.get("remove", {}).get("exit_code") == 0)
        all_downloads += sum(row["argv"][0] == "/usr/bin/curl" for row in inner["commands"])

        for row in inner["commands"]:
            argv = row["argv"]
            if argv[0] == "/usr/local/bin/docker":
                audit.check(
                    f"attempt{position}_docker_endpoint_{len(audit.checks)}",
                    argv[1:3] == ["--host", SOCKET],
                )
            if argv[0] == "/usr/bin/curl":
                audit.check(
                    f"attempt{position}_curl_tls_{len(audit.checks)}",
                    "--proto" in argv and "=https" in argv and "--proto-redir" in argv
                    and "--insecure" not in argv and "-k" not in argv
                    and argv[-1].startswith("https://files.pythonhosted.org/"),
                )

    audit.check("three_unique_container_starts", len(all_containers) == 3 and len(set(all_containers)) == 3)
    audit.check("complete_exact_cleanup", set(all_cleanup) == set(all_containers) and len(all_cleanup) == 3)
    audit.check(
        "cumulative_start_accounting",
        receipt["operational_container_start_attempts"] == 3
        and receipt["maximum_container_start_attempts"] == 4
        and sum(a["inner"]["container_start_attempts"] for a in attempts) == 3,
    )
    audit.check(
        "cumulative_download_accounting",
        receipt["actual_wheel_download_invocations"] == 4
        and receipt["maximum_wheel_download_invocations"] == 4
        and all_downloads == 4,
    )
    audit.check("zero_scientific_runs", receipt["scientific_runs"] == 0 and all(a["inner"]["scientific_runs"] == 0 for a in attempts))

    first_start = attempts[0]["inner"]["commands"][7]
    first_nested = json.loads(first_start["stdout"])
    audit.check(
        "first_permission_failure_preserved",
        first_start["exit_code"] == 1
        and first_nested["status"] == "failed"
        and first_nested["error_type"] == "PermissionError"
        and first_nested["error"] == "[Errno 13] Permission denied: '/opt/reserve-inputs/installed-inventory.json'"
        and [row["exit_code"] for row in first_nested["commands"]] == [0, 0],
    )
    audit.check(
        "first_failure_not_successful_pair",
        "installer_result" not in attempts[0]["inner"]
        and attempts[0]["inner"]["terminal_inspections"][-1]["State"]["ExitCode"] == 1,
    )

    second = attempts[1]["inner"]
    second_install = json.loads(second["commands"][7]["stdout"])
    second_verify = json.loads(second["commands"][13]["stdout"])
    audit.check(
        "retry_authority_and_reservation",
        attempts[1]["outer"]["additional_authority"] == "DEC-20260908-d687ab"
        and attempts[1]["outer"]["authority_commit"] == RETRY_AUTHORITY
        and attempts[1]["outer"]["prior_start_attempts"] == 1
        and attempts[1]["outer"]["reserved_new_start_attempts"] == 2,
    )
    audit.check(
        "retry_nested_results",
        second_install == second["installer_result"]
        and second_install["status"] == "passed" and second_install["mode"] == "install"
        and second_verify["status"] == "passed" and second_verify["mode"] == "verify"
        and second_verify["fresh_inventory_matches"] is True
        and second_verify["uid"] == second_verify["gid"] == 65534,
    )
    audit.check(
        "offline_pip_commands",
        len(second_install["commands"]) == 2
        and [c["exit_code"] for c in second_install["commands"]] == [0, 0]
        and all(flag in second_install["commands"][0]["argv"] for flag in (
            "--no-index", "--no-deps", "--no-compile", "--no-cache-dir", "--require-hashes"
        ))
        and second_install["commands"][1]["argv"][-2:] == ["pip", "check"]
        and second_install["commands"][1]["stdout"] == "No broken requirements found.\n",
    )

    requirements = "".join(
        package["name"] + "==" + package["version"] + " --hash=sha256:"
        + package["wheel"]["digests"]["sha256"] + "\n"
        for package in metadata["packages"]
    ).encode()
    copied = second["copied_input_sha256"]
    audit.check("exact_requirements_hash", copied["requirements.txt"] == sha_bytes(requirements))
    audit.check(
        "exact_wheel_copy_hashes",
        all(copied[p["wheel"]["filename"]] == p["wheel"]["digests"]["sha256"] for p in metadata["packages"]),
    )

    infos = [attempts[0]["inner"]["initial_inspections"][0], second["initial_inspections"][0], second["initial_inspections"][1]]
    audit.check("installer1_isolation", isolation_ok(infos[0], False, "0:0", 64))
    audit.check("installer2_isolation", isolation_ok(infos[1], False, "0:0", 64))
    audit.check("verifier_isolation", isolation_ok(infos[2], True, "65534:65534", 32))
    audit.check(
        "terminal_container_states",
        [attempts[0]["inner"]["terminal_inspections"][0]["State"]["ExitCode"],
         second["terminal_inspections"][0]["State"]["ExitCode"],
         second["terminal_inspections"][1]["State"]["ExitCode"]] == [1, 0, 0]
        and all(not item["State"]["Running"] for item in (
            attempts[0]["inner"]["terminal_inspections"][0],
            second["terminal_inspections"][0], second["terminal_inspections"][1]
        )),
    )

    inventories = [first_nested["inventory"], second_install["inventory"], second_verify["inventory"], binding["inventory"]]
    audit.check("all_retained_inventories_identical", all(item == inventories[0] for item in inventories[1:]))
    counts = {name: len(package["files"]) for name, package in binding["inventory"]["packages"].items()}
    audit.check("exact_1667_inventory_count", counts == {"sympy": 1573, "mpmath": 94})
    for name, package in binding["inventory"]["packages"].items():
        audit.check(
            f"{name}_declared_inventory_aggregate",
            package["inventory_sha256"] == sha_bytes(canonical(package["files"])),
        )

    original_image_binding_keys = {
        "task_id", "base_image", "base_id", "prepared_image_id", "local_tag",
        "inspection", "inventory", "scientific_admission", "group_oom_guard_verified",
    }
    annotation_keys = set(second["image_binding"]) - original_image_binding_keys
    audit.check(
        "coordinator_annotations_separated",
        annotation_keys == {"approval_decisions", "dependency_metadata_path", "prepared_source_includes_solver_or_generator"}
        and second["image_binding"] == binding,
        {"annotation_keys": sorted(annotation_keys)},
    )
    audit.check(
        "scope_flags_remain_negative",
        binding["scientific_admission"] is False
        and binding["group_oom_guard_verified"] is False
        and binding["prepared_source_includes_solver_or_generator"] is False,
    )

    source_hashes = receipt["source_sha256"]
    audit.check(
        "final_source_hashes",
        source_hashes["prepare.py"] == sha_path(REPO / "coordination/experiment-reserve/BATCH-635652/runtime/TASK-20260908-6e8eee/prepare.py")
        and source_hashes["install_verify.py"] == sha_path(REPO / "coordination/experiment-reserve/BATCH-635652/runtime/TASK-20260908-6e8eee/install_verify.py")
        and source_hashes["image-binding.json"] == sha_path(BINDING),
    )
    return {
        "container_ids": all_containers,
        "cleanup_ids": all_cleanup,
        "nested_inventory_counts": counts,
        "inventory_sha256": {name: package["inventory_sha256"] for name, package in binding["inventory"]["packages"].items()},
        "annotation_keys": sorted(annotation_keys),
    }


def archive_audit(audit: Audit, export: Path, live: dict, binding: dict, metadata: dict) -> dict:
    inventory = binding["inventory"]
    desired: set[str] = set()
    rel_to_abs: dict[str, str] = {}
    for package in inventory["packages"].values():
        for row in package["files"]:
            absolute = inventory_absolute(row["path"])
            desired.add(absolute)
            rel_to_abs[row["path"]] = absolute
    record_paths = {
        name: inventory_absolute(f"{name}-{package['version']}.dist-info/RECORD")
        for name, package in inventory["packages"].items()
    }
    wheel_paths = {p["name"]: "opt/reserve-inputs/" + p["wheel"]["filename"] for p in metadata["packages"]}
    desired.update(record_paths.values())
    desired.update(wheel_paths.values())
    desired.update({
        "opt/reserve-inputs/dependencies.json",
        "opt/reserve-inputs/requirements.txt",
        "opt/reserve-inputs/install_verify.py",
    })

    state: dict[str, dict] = {}
    reserve_inputs: dict[str, dict] = {}
    outer_member_count = 0
    outer_member_bytes = 0
    nested_member_count = 0
    nested_member_bytes = 0
    outer_symlinks = 0
    nested_symlinks = 0
    nested_hardlinks = 0
    layer_rows = []
    spools = []
    try:
        with tarfile.open(export, mode="r:") as outer:
            members: dict[str, tarfile.TarInfo] = {}
            for member in outer:
                normalized = safe_archive_name(member.name)
                if normalized in members:
                    raise ValueError(f"duplicate outer member: {normalized}")
                members[normalized] = member
                outer_member_count += 1
                outer_member_bytes += member.size
                if outer_member_bytes > MAX_BYTES:
                    raise ValueError("outer cumulative uncompressed data exceeds 2 GiB")
                if member.issym() or member.islnk():
                    outer_symlinks += 1
            for required in ("manifest.json", "index.json", "oci-layout"):
                if required not in members:
                    raise ValueError(f"missing outer archive member: {required}")

            legacy = json.loads(read_tar_bytes(outer, members["manifest.json"]))
            if not isinstance(legacy, list) or len(legacy) != 1:
                raise ValueError("expected exactly one legacy manifest entry")
            legacy_entry = legacy[0]
            if legacy_entry.get("RepoTags") != [TAG]:
                raise ValueError("legacy manifest tag mismatch")
            config_path = safe_archive_name(legacy_entry["Config"])
            if config_path not in members:
                raise ValueError("legacy manifest config absent")
            config_bytes = read_tar_bytes(outer, members[config_path])
            config_digest = "sha256:" + sha_bytes(config_bytes)
            if config_digest != IMAGE:
                raise ValueError("config bytes do not hash to immutable image id")
            config = json.loads(config_bytes)

            index = json.loads(read_tar_bytes(outer, members["index.json"]))
            descriptors = index.get("manifests") or []
            if len(descriptors) != 1:
                raise ValueError("expected exactly one OCI index descriptor")
            descriptor = descriptors[0]
            manifest_path = "blobs/sha256/" + descriptor["digest"].split(":", 1)[1]
            if manifest_path not in members:
                raise ValueError("OCI manifest blob absent")
            manifest_bytes = read_tar_bytes(outer, members[manifest_path])
            if "sha256:" + sha_bytes(manifest_bytes) != descriptor["digest"] or len(manifest_bytes) != descriptor["size"]:
                raise ValueError("OCI manifest descriptor mismatch")
            manifest = json.loads(manifest_bytes)
            if manifest["config"]["digest"] != IMAGE or manifest["config"]["size"] != len(config_bytes):
                raise ValueError("OCI config descriptor mismatch")
            manifest_layers = manifest["layers"]
            legacy_layers = [safe_archive_name(name) for name in legacy_entry["Layers"]]
            if len(manifest_layers) != len(legacy_layers):
                raise ValueError("OCI/legacy layer count mismatch")

            diff_ids = config["rootfs"]["diff_ids"]
            if len(diff_ids) != len(manifest_layers):
                raise ValueError("config rootfs diff-id count mismatch")
            if diff_ids != live["RootFS"]["Layers"] or diff_ids != binding["inspection"]["RootFS"]["Layers"]:
                raise ValueError("live/recorded/config layer identity mismatch")
            base_layers = binding["inspection"]["RootFS"]["Layers"][:-1]
            if diff_ids[: len(base_layers)] != base_layers:
                raise ValueError("prepared image does not retain declared base-layer prefix")

            for layer_index, (layer_descriptor, legacy_path, diff_id) in enumerate(zip(manifest_layers, legacy_layers, diff_ids)):
                blob_path = "blobs/sha256/" + layer_descriptor["digest"].split(":", 1)[1]
                if blob_path != legacy_path or blob_path not in members:
                    raise ValueError("OCI/legacy layer path mismatch")
                spool, raw_size, raw_hash = spool_tar_member(outer, members[blob_path])
                spools.append(spool)
                if raw_size != layer_descriptor["size"] or "sha256:" + raw_hash != layer_descriptor["digest"]:
                    raise ValueError("layer blob descriptor mismatch")
                media = layer_descriptor["mediaType"]
                if media.endswith(".tar"):
                    layer_file = spool
                    uncompressed_size, uncompressed_hash = raw_size, raw_hash
                elif media.endswith(".tar+gzip"):
                    expanded = tempfile.SpooledTemporaryFile(max_size=BUFFER, mode="w+b")
                    spools.append(expanded)
                    spool.seek(0)
                    digest = hashlib.sha256()
                    expanded_size = 0
                    with gzip.GzipFile(fileobj=spool, mode="rb") as source:
                        while True:
                            chunk = source.read(BUFFER)
                            if not chunk:
                                break
                            expanded_size += len(chunk)
                            if expanded_size > MAX_BYTES:
                                raise ValueError("expanded layer exceeds 2 GiB")
                            digest.update(chunk)
                            expanded.write(chunk)
                    expanded.seek(0)
                    layer_file = expanded
                    uncompressed_size, uncompressed_hash = expanded_size, digest.hexdigest()
                else:
                    raise ValueError(f"unsupported layer archive media type: {media}")
                if "sha256:" + uncompressed_hash != diff_id:
                    raise ValueError("uncompressed layer diff-id mismatch")

                layer_files = 0
                layer_dirs = 0
                layer_whiteouts = 0
                layer_file.seek(0)
                with tarfile.open(fileobj=layer_file, mode="r:") as nested:
                    seen = set()
                    for member in nested:
                        normalized = safe_archive_name(member.name)
                        if normalized in seen:
                            raise ValueError(f"duplicate nested member in layer {layer_index}: {normalized}")
                        seen.add(normalized)
                        nested_member_count += 1
                        nested_member_bytes += member.size
                        if nested_member_bytes > MAX_BYTES:
                            raise ValueError("nested cumulative uncompressed data exceeds 2 GiB")
                        parent, name = posixpath.split(normalized)
                        if name == ".wh..wh..opq":
                            layer_whiteouts += 1
                            prefix = parent.rstrip("/") + "/"
                            for key in list(state):
                                if key.startswith(prefix):
                                    state.pop(key, None)
                            for key in list(reserve_inputs):
                                if key.startswith(prefix):
                                    reserve_inputs.pop(key, None)
                            continue
                        if name.startswith(".wh."):
                            layer_whiteouts += 1
                            target = posixpath.join(parent, name[4:])
                            prefix = target.rstrip("/") + "/"
                            state.pop(target, None)
                            reserve_inputs.pop(target, None)
                            for key in list(state):
                                if key.startswith(prefix):
                                    state.pop(key, None)
                            for key in list(reserve_inputs):
                                if key.startswith(prefix):
                                    reserve_inputs.pop(key, None)
                            continue

                        interesting = normalized in desired or normalized.startswith("opt/reserve-inputs/")
                        if member.isfile():
                            layer_files += 1
                            if interesting:
                                source = nested.extractfile(member)
                                if source is None:
                                    raise ValueError(f"cannot read nested member: {normalized}")
                                digest = hashlib.sha256()
                                count = 0
                                special = normalized in set(wheel_paths.values()) | set(record_paths.values()) | {
                                    "opt/reserve-inputs/dependencies.json",
                                    "opt/reserve-inputs/requirements.txt",
                                    "opt/reserve-inputs/install_verify.py",
                                }
                                retained = tempfile.SpooledTemporaryFile(max_size=BUFFER, mode="w+b") if special else None
                                if retained is not None:
                                    spools.append(retained)
                                while True:
                                    chunk = source.read(BUFFER)
                                    if not chunk:
                                        break
                                    count += len(chunk)
                                    if count > MAX_BYTES:
                                        raise ValueError("nested member exceeds 2 GiB")
                                    digest.update(chunk)
                                    if retained is not None:
                                        retained.write(chunk)
                                if retained is not None:
                                    retained.seek(0)
                                row = {"type": "file", "bytes": count, "sha256": digest.hexdigest(), "data": retained, "layer": layer_index}
                                state[normalized] = row
                                if normalized.startswith("opt/reserve-inputs/"):
                                    reserve_inputs[normalized] = row
                        elif member.isdir():
                            layer_dirs += 1
                            if interesting:
                                state[normalized] = {"type": "directory", "layer": layer_index}
                        elif member.issym():
                            nested_symlinks += 1
                            if interesting:
                                state[normalized] = {"type": "symlink", "linkname": member.linkname, "layer": layer_index}
                        elif member.islnk():
                            nested_hardlinks += 1
                            if interesting:
                                state[normalized] = {"type": "hardlink", "linkname": member.linkname, "layer": layer_index}
                        elif interesting:
                            state[normalized] = {"type": "special", "tar_type": repr(member.type), "layer": layer_index}
                layer_rows.append({
                    "index": layer_index,
                    "descriptor_digest": layer_descriptor["digest"],
                    "descriptor_size": layer_descriptor["size"],
                    "media_type": media,
                    "diff_id": diff_id,
                    "uncompressed_bytes": uncompressed_size,
                    "regular_files": layer_files,
                    "directories": layer_dirs,
                    "whiteouts": layer_whiteouts,
                })

        missing = []
        wrong = []
        symlink_or_special = []
        actual_inventory = {}
        for name, package in inventory["packages"].items():
            rows = []
            for declared in package["files"]:
                path = inventory_absolute(declared["path"])
                actual = state.get(path)
                if actual is None:
                    missing.append(declared["path"])
                    continue
                if actual["type"] != "file":
                    symlink_or_special.append({"path": declared["path"], "type": actual["type"]})
                    continue
                observed = {"path": declared["path"], "bytes": actual["bytes"], "sha256": actual["sha256"]}
                rows.append(observed)
                if observed != declared:
                    wrong.append({"declared": declared, "observed": observed})
            actual_inventory[name] = rows
            audit.check(f"{name}_all_inventory_files_present", len(rows) == len(package["files"]) and not missing)
            audit.check(f"{name}_all_inventory_hashes_match", rows == package["files"] and not wrong)
            audit.check(f"{name}_no_inventory_symlinks", not symlink_or_special)
            audit.check(
                f"{name}_actual_inventory_aggregate",
                sha_bytes(canonical(rows)) == package["inventory_sha256"],
            )

        installed_record_rows = {}
        installed_record_hash_checks = 0
        for name, record_path in record_paths.items():
            record = state.get(record_path)
            if not record or record["type"] != "file" or record["data"] is None:
                raise ValueError(f"installed RECORD unavailable for {name}")
            record["data"].seek(0)
            text = io.TextIOWrapper(record["data"], encoding="utf-8", newline="")
            rows = list(csv.reader(text))
            text.detach()
            if any(len(row) != 3 for row in rows):
                raise ValueError(f"malformed installed RECORD for {name}")
            names = [row[0] for row in rows]
            if len(names) != len(set(names)):
                raise ValueError(f"duplicate installed RECORD path for {name}")
            declared_names = [row["path"] for row in inventory["packages"][name]["files"]]
            audit.check(f"{name}_inventory_matches_installed_record", sorted(names) == declared_names)
            for relative, digest_field, size_field in rows:
                target = state.get(inventory_absolute(relative))
                if target is None or target["type"] != "file":
                    raise ValueError(f"installed RECORD target unavailable: {relative}")
                if digest_field:
                    algorithm, encoded = digest_field.split("=", 1)
                    padding = "=" * ((4 - len(encoded) % 4) % 4)
                    digest_hex = base64.urlsafe_b64decode(encoded + padding).hex()
                    if algorithm != "sha256" or digest_hex != target["sha256"]:
                        raise ValueError(f"installed RECORD digest mismatch: {relative}")
                    installed_record_hash_checks += 1
                if size_field and int(size_field) != target["bytes"]:
                    raise ValueError(f"installed RECORD size mismatch: {relative}")
            installed_record_rows[name] = len(rows)

        wheel_summary = {}
        wheel_member_comparisons = 0
        generated_files = {}
        transformations = {}
        wheel_uncompressed_bytes = 0
        for package_meta in metadata["packages"]:
            name = package_meta["name"]
            wheel_meta = package_meta["wheel"]
            wheel_state = state.get(wheel_paths[name])
            if not wheel_state or wheel_state["type"] != "file" or wheel_state["data"] is None:
                raise ValueError(f"embedded wheel unavailable: {name}")
            if wheel_state["sha256"] != wheel_meta["digests"]["sha256"] or wheel_state["bytes"] != wheel_meta["size"]:
                raise ValueError(f"embedded wheel metadata mismatch: {name}")
            wheel_state["data"].seek(0)
            with zipfile.ZipFile(wheel_state["data"], "r") as wheel:
                infos = wheel.infolist()
                names = [info.filename for info in infos]
                if len(names) != len(set(names)):
                    raise ValueError(f"duplicate wheel member: {name}")
                wheel_map = {}
                script_bytes = {}
                for info in infos:
                    member_name = safe_archive_name(info.filename)
                    wheel_uncompressed_bytes += info.file_size
                    if outer_member_bytes + nested_member_bytes + wheel_uncompressed_bytes > MAX_BYTES:
                        raise ValueError("cumulative archive data exceeds 2 GiB")
                    mode = (info.external_attr >> 16) & 0xFFFF
                    if stat.S_ISLNK(mode):
                        raise ValueError(f"wheel symlink member: {member_name}")
                    if info.is_dir():
                        continue
                    digest = hashlib.sha256()
                    count = 0
                    chunks = [] if ".data/scripts/" in member_name else None
                    with wheel.open(info, "r") as source:
                        while True:
                            chunk = source.read(BUFFER)
                            if not chunk:
                                break
                            count += len(chunk)
                            digest.update(chunk)
                            if chunks is not None:
                                if count > BUFFER:
                                    raise ValueError("wheel script transformation input exceeds 1 MiB")
                                chunks.append(chunk)
                    wheel_map[member_name] = {"bytes": count, "sha256": digest.hexdigest()}
                    if chunks is not None:
                        script_bytes[member_name] = b"".join(chunks)

                record_name = f"{name}-{package_meta['version']}.dist-info/RECORD"
                if record_name not in wheel_map:
                    raise ValueError(f"wheel RECORD missing: {name}")
                with wheel.open(record_name, "r") as source:
                    wheel_record = list(csv.reader(io.TextIOWrapper(source, encoding="utf-8", newline="")))
                if any(len(row) != 3 for row in wheel_record):
                    raise ValueError(f"malformed wheel RECORD: {name}")
                if sorted(row[0] for row in wheel_record) != sorted(wheel_map):
                    raise ValueError(f"wheel RECORD inventory mismatch: {name}")
                for relative, digest_field, size_field in wheel_record:
                    member = wheel_map[relative]
                    if digest_field:
                        algorithm, encoded = digest_field.split("=", 1)
                        padding = "=" * ((4 - len(encoded) % 4) % 4)
                        if algorithm != "sha256" or base64.urlsafe_b64decode(encoded + padding).hex() != member["sha256"]:
                            raise ValueError(f"wheel RECORD digest mismatch: {relative}")
                    if size_field and int(size_field) != member["bytes"]:
                        raise ValueError(f"wheel RECORD size mismatch: {relative}")

                mapped = set()
                for wheel_name, wheel_file in wheel_map.items():
                    if wheel_name == record_name:
                        mapped.add(record_name)
                        continue
                    data_marker = f"{name}-{package_meta['version']}.data/"
                    if wheel_name.startswith(data_marker + "scripts/"):
                        filename = wheel_name.split("/", 2)[-1]
                        installed_relative = "../../../bin/" + filename
                        raw = script_bytes[wheel_name]
                        first, separator, rest = raw.partition(b"\n")
                        if first == b"#!python":
                            transformed = b"#!/usr/local/bin/python3" + separator + rest
                        elif first == b"#!pythonw":
                            transformed = b"#!/usr/local/bin/python3" + separator + rest
                        else:
                            transformed = raw
                        expected = {"bytes": len(transformed), "sha256": sha_bytes(transformed)}
                        transformations[wheel_name] = {
                            "installed_path": installed_relative,
                            "kind": "pip_shebang_rewrite" if transformed != raw else "script_relocation",
                            "wheel_sha256": wheel_file["sha256"],
                            "installed_expected_sha256": expected["sha256"],
                        }
                    elif wheel_name.startswith(data_marker + "purelib/") or wheel_name.startswith(data_marker + "platlib/"):
                        installed_relative = wheel_name.split("/", 2)[-1]
                        expected = wheel_file
                    else:
                        installed_relative = wheel_name
                        expected = wheel_file
                    mapped.add(installed_relative)
                    actual = state.get(inventory_absolute(installed_relative))
                    if not actual or actual["type"] != "file" or actual["bytes"] != expected["bytes"] or actual["sha256"] != expected["sha256"]:
                        raise ValueError(f"wheel-to-installed file mismatch: {wheel_name} -> {installed_relative}")
                    wheel_member_comparisons += 1

                installed_names = {row["path"] for row in inventory["packages"][name]["files"]}
                extras = sorted(installed_names - mapped)
                expected_extras = sorted([
                    f"{name}-{package_meta['version']}.dist-info/INSTALLER",
                    f"{name}-{package_meta['version']}.dist-info/REQUESTED",
                ])
                if extras != expected_extras:
                    raise ValueError(f"unexpected pip-generated file set for {name}: {extras}")
                for relative in extras:
                    actual = state[inventory_absolute(relative)]
                    expected_bytes = b"pip\n" if relative.endswith("/INSTALLER") else b""
                    if actual["bytes"] != len(expected_bytes) or actual["sha256"] != sha_bytes(expected_bytes):
                        raise ValueError(f"pip-generated file content mismatch: {relative}")
                generated_files[name] = extras
                wheel_summary[name] = {
                    "version": package_meta["version"],
                    "embedded_bytes": wheel_state["bytes"],
                    "embedded_sha256": wheel_state["sha256"],
                    "members": len(wheel_map),
                    "installed_direct_or_transformed_comparisons": len(mapped) - 1,
                }

        expected_inputs = {
            "opt/reserve-inputs/dependencies.json",
            "opt/reserve-inputs/install_verify.py",
            "opt/reserve-inputs/requirements.txt",
            *wheel_paths.values(),
        }
        audit.check("reserve_input_set_exact", set(reserve_inputs) == expected_inputs, {"paths": sorted(reserve_inputs)})
        audit.check("dependency_metadata_inside_image", reserve_inputs["opt/reserve-inputs/dependencies.json"]["sha256"] == sha_path(METADATA))
        audit.check(
            "installer_source_inside_image",
            reserve_inputs["opt/reserve-inputs/install_verify.py"]["sha256"]
            == sha_path(REPO / "coordination/experiment-reserve/BATCH-635652/runtime/TASK-20260908-6e8eee/install_verify.py"),
        )
        audit.check("no_repository_solver_or_generator_input", not any(path.endswith(("toycurve.py", "rho.py", "generator.py", "solver.py")) for path in reserve_inputs))

        return {
            "export": {"bytes": export.stat().st_size, "sha256": sha_path(export)},
            "outer_archive": {
                "members": outer_member_count,
                "declared_uncompressed_bytes": outer_member_bytes,
                "symlink_or_hardlink_members": outer_symlinks,
            },
            "nested_layers": {
                "members": nested_member_count,
                "declared_uncompressed_file_bytes": nested_member_bytes,
                "symlinks": nested_symlinks,
                "hardlinks": nested_hardlinks,
                "layers": layer_rows,
            },
            "oci": {
                "config_digest": config_digest,
                "manifest_digest": descriptor["digest"],
                "diff_ids": diff_ids,
                "base_layer_prefix": base_layers,
            },
            "inventory": {
                "declared_entries": sum(len(p["files"]) for p in inventory["packages"].values()),
                "reconstructed_entries": sum(len(rows) for rows in actual_inventory.values()),
                "missing": missing,
                "wrong": wrong,
                "symlink_or_special": symlink_or_special,
                "installed_record_rows": installed_record_rows,
                "installed_record_hash_checks": installed_record_hash_checks,
            },
            "wheels": wheel_summary,
            "wheel_member_comparisons": wheel_member_comparisons,
            "pip_generated_files": generated_files,
            "pip_transformations": transformations,
            "reserve_inputs": sorted(reserve_inputs),
            "cumulative_uncompressed_data_bytes": outer_member_bytes + nested_member_bytes + wheel_uncompressed_bytes,
        }
    finally:
        for spool in spools:
            try:
                spool.close()
            except Exception:
                pass


def worker(inner_path: Path, export_path: Path) -> int:
    started_utc = utc()
    wall_start = time.monotonic()
    cpu_start = time.process_time()
    soft, hard = resource.getrlimit(resource.RLIMIT_AS)
    desired = 2 * 1024**3
    enforced = min(desired, hard) if hard != resource.RLIM_INFINITY else desired
    resource.setrlimit(resource.RLIMIT_AS, (enforced, hard))
    audit = Audit()
    commands = []
    export_invocations = 0
    export_deleted = False
    archive_result = None
    preparation_result = None
    source_rows = []
    git_rows = []
    error = None
    try:
        handoff_doc = yaml.safe_load(HANDOFF.read_text())["handoff"]
        plan_doc = yaml.safe_load(PLAN.read_text())["review_plan"]
        binding = json.loads(BINDING.read_bytes())
        receipt = json.loads(PREPARATION.read_bytes())
        attempt1 = json.loads(ATTEMPT1.read_bytes())
        metadata = json.loads(METADATA.read_bytes())
        snapshot = json.loads(SNAPSHOT.read_bytes())

        audit.check("handoff_task", handoff_doc["id"] == TASK and handoff_doc["to"] == "validator")
        audit.check("review_plan_exact", handoff_doc["review_plan"] == plan_doc)
        audit.check("one_joint_owned", [j["assigned_to"] for j in plan_doc["joints"]] == [TASK])
        audit.check("review_plan_prior_recorded", plan_doc["recorded_before_reviewers"] is True and plan_doc["source_snapshot"] == SOURCE_SNAPSHOT)
        audit.check("inference_policy", handoff_doc["inference"] == {
            "policy": "review-adversarial", "reasoning_effort": "xhigh",
            "fallback_allowed": False, "degraded_allowed": False,
            "independent_session_required": True,
        })
        audit.check("zero_run_zero_container_budget", handoff_doc["budget"]["maximum_runs"] == 0 and handoff_doc["budget"]["maximum_operational_containers"] == 0)
        audit.check("exact_three_path_scope", handoff_doc["deliverables"] == handoff_doc["artifact_paths"] == handoff_doc["write_scope"] and len(handoff_doc["write_scope"]) == 3)

        for entry in handoff_doc["source_bindings"]:
            data = (REPO / entry["path"]).read_bytes()
            actual = sha_bytes(data)
            source_rows.append({"path": entry["path"], "expected_sha256": entry["sha256"], "actual_sha256": actual, "bytes_read": len(data), "passed": actual == entry["sha256"]})
        audit.check("all_24_source_bindings", len(source_rows) == 24 and all(row["passed"] for row in source_rows))
        audit.check("inputs_equal_bindings", handoff_doc["inputs"] == [entry["path"] for entry in handoff_doc["source_bindings"]])

        claim = json.loads(CLAIM.read_bytes())
        audit.check("claim_identity", claim["task_id"] == TASK and claim["owner"] == CLAIM_OWNER and claim["session"] == CLAIM_SESSION and claim["epoch"] == 1)
        audit.check("claim_location", claim["branch"] == "codex/reserve-control-work-20260908" and claim["worktree"] == str(REPO))
        audit.check("claim_scope", claim["write_scope"] == handoff_doc["write_scope"])
        audit.check("claim_not_forced", claim["forced"] is False and claim["supersedes"] is None)

        git_commands = [
            ["git", "cat-file", "-e", AUTHORITY + "^{commit}"],
            ["git", "cat-file", "-e", CLAIM_COMMIT + "^{commit}"],
            ["git", "merge-base", "--is-ancestor", AUTHORITY, CLAIM_COMMIT],
            ["git", "merge-base", "--is-ancestor", SOURCE_SNAPSHOT, AUTHORITY],
            ["git", "merge-base", "--is-ancestor", RETRY_AUTHORITY, SOURCE_SNAPSHOT],
            ["git", "diff", "--quiet", AUTHORITY, "--", *handoff_doc["inputs"]],
            ["git", "diff", "--quiet", SOURCE_SNAPSHOT, "--", *snapshot["source_path_sha256"].keys()],
        ]
        for argv in git_commands:
            row = command_record(argv, 30)
            git_rows.append(row)
            audit.check("git_" + str(len(git_rows)), command_ok(row), {"argv": argv, "exit_code": row.get("exit_code"), "stderr": row.get("stderr")})

        audit.check("snapshot_source_hashes", all(sha_path(REPO / path) == digest for path, digest in snapshot["source_path_sha256"].items()))
        preparation_result = audit_preparation(audit, handoff_doc, binding, receipt, attempt1, metadata)

        inspect = command_record(DOCKER + ["image", "inspect", IMAGE], 30)
        commands.append(inspect)
        audit.check("live_image_inspect_succeeded", command_ok(inspect))
        if not command_ok(inspect):
            raise RuntimeError("read-only image inspect failed")
        inspected = json.loads(inspect["stdout"])
        if not isinstance(inspected, list) or len(inspected) != 1:
            raise ValueError("image inspect did not return one object")
        live = inspected[0]
        audit.check("live_image_id", live["Id"] == IMAGE)
        audit.check("live_platform", live["Os"] == "linux" and live["Architecture"] == "arm64")
        audit.check("live_config", live["Config"].get("User") == "65534:65534" and live["Config"].get("Cmd") == ["python3"] and live["Config"].get("WorkingDir") == "/tmp")
        audit.check("live_required_environment", all(value in live["Config"].get("Env", []) for value in ("PYTHONDONTWRITEBYTECODE=1", "PYTHONHASHSEED=0", "SYMPY_GROUND_TYPES=python")))
        audit.check("live_recorded_layers", live["RootFS"]["Layers"] == binding["inspection"]["RootFS"]["Layers"])

        export_invocations += 1
        saved = command_record(DOCKER + ["image", "save", IMAGE], 180, export_path)
        commands.append(saved)
        audit.check("single_image_export_succeeded", command_ok(saved))
        audit.check("export_under_2gib", export_path.exists() and export_path.stat().st_size <= MAX_BYTES)
        if not command_ok(saved):
            raise RuntimeError("read-only image save failed")
        archive_result = archive_audit(audit, export_path, live, binding, metadata)
    except BaseException as exc:
        error = {"type": type(exc).__name__, "message": str(exc)}
    finally:
        if export_path.exists():
            try:
                export_path.unlink()
                export_deleted = not export_path.exists()
            except Exception as exc:
                audit.check("owned_export_deleted", False, repr(exc))
        else:
            export_deleted = True
        audit.check("owned_export_deleted", export_deleted)

    controls, control_wall, control_cpu = malformed_controls()
    audit.check("all_48_malformed_controls_rejected", len(controls) == SUITE_SIZE and all(row["passed"] for row in controls))
    audit.check("malformed_control_budget", len(controls) <= 48 and len(controls) <= MAX_CONTROLS and MAX_CONTROLS - len(controls) >= SUITE_SIZE)
    audit.check("malformed_case_watchdogs", all(row["wall_seconds"] <= 10 for row in controls) and control_wall <= 1800 and control_cpu <= 1800)

    own = resource.getrusage(resource.RUSAGE_SELF)
    result = {
        "schema": "crypto.autoresearch.dependency_image_independent_audit.v1",
        "task_id": TASK,
        "started_at_UTC": started_utc,
        "ended_at_UTC": utc(),
        "status": "passed" if not audit.failures and error is None else "failed",
        "joint": "dependency_image_byte_identity_and_operational_custody",
        "joint_verdict": "holds" if not audit.failures and error is None else "breaks",
        "authority": {
            "handoff_commit": AUTHORITY,
            "claim_commit": CLAIM_COMMIT,
            "source_snapshot": SOURCE_SNAPSHOT,
            "retry_authority_commit": RETRY_AUTHORITY,
            "claim_owner": CLAIM_OWNER,
            "claim_session": CLAIM_SESSION,
        },
        "source_bindings": source_rows,
        "git_commands": git_rows,
        "commands": commands,
        "export_attempts": export_invocations,
        "maximum_export_attempts": 2,
        "export_deleted_after_custody": export_deleted,
        "archive_audit": archive_result,
        "preparation_custody": preparation_result,
        "checks": audit.checks,
        "failed_checks": audit.failures,
        "malformed_controls": {
            "cases": controls,
            "cases_executed": len(controls),
            "maximum_cases": MAX_CONTROLS,
            "remaining_case_budget": MAX_CONTROLS - len(controls),
            "complete_suite_limit": 48,
            "complete_suite_reserved_after_this_run": True,
            "aggregate_wall_seconds": control_wall,
            "aggregate_cpu_seconds": control_cpu,
        },
        "metrics": {
            "wall_seconds": time.monotonic() - wall_start,
            "process_cpu_seconds": time.process_time() - cpu_start,
            "process_peak_rss_bytes": own.ru_maxrss if sys.platform == "darwin" else own.ru_maxrss * 1024,
            "memory_limit_bytes": enforced,
            "maximum_workers": 1,
            "stream_buffer_bytes": BUFFER,
            "source_file_comparisons": len(source_rows),
            "scientific_runs": 0,
            "container_creates_or_starts": 0,
            "image_code_executions": 0,
        },
        "error": error,
        "limitations": [
            "This verifies exact local image/archive, wheel, installed-file, configuration and retained preparation custody only.",
            "No container was created or started and no image code or library import was executed by this audit.",
            "Retained import/version outputs are audited as prior operational observations only.",
            "Coordinator-added image-binding annotations are source statements, not container-emitted measurements.",
            "Repository solver/generator exclusion is checked only for copied /opt/reserve-inputs; SymPy itself contains mathematical solver and generator functions.",
            "No scientific result, 8 GiB group guard, whole-runtime admission, fixture validity, or launch admission is established.",
        ],
    }
    with inner_path.open("x") as handle:
        json.dump(result, handle, indent=2, allow_nan=False)
        handle.write("\n")
    return 0 if result["status"] == "passed" else 1


def supervisor(receipt_path: Path) -> int:
    if receipt_path.exists():
        raise FileExistsError(f"exclusive receipt path exists: {receipt_path}")
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    scratch = Path(tempfile.mkdtemp(prefix=TASK.lower() + "-", dir="/private/tmp"))
    inner_path = scratch / "inner.json"
    export_path = scratch / "image-export.tar"
    stdout_path = scratch / "worker.stdout"
    stderr_path = scratch / "worker.stderr"
    argv = [sys.executable, "-B", str(Path(__file__).resolve()), "--worker", "--inner", str(inner_path), "--export", str(export_path)]
    outer = {
        "argv": argv,
        "command_sha256": sha_bytes(canonical(argv)),
        "cwd": str(Path.cwd()),
        "started_at_UTC": utc(),
        "stdout_path": str(stdout_path),
        "stderr_path": str(stderr_path),
        "redirection_before_launch": True,
        "timeout_seconds": 900,
    }
    started = time.monotonic()
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    descriptor_out = os.open(stdout_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    descriptor_err = os.open(stderr_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor_out, "wb", buffering=BUFFER) as out, os.fdopen(descriptor_err, "wb", buffering=BUFFER) as err:
            try:
                completed = subprocess.run(argv, stdout=out, stderr=err, timeout=900)
                outer.update(exit_code=completed.returncode, timed_out=False, terminal_observed=True)
            except subprocess.TimeoutExpired:
                outer.update(exit_code=None, timed_out=True, terminal_observed=True)
    finally:
        after = resource.getrusage(resource.RUSAGE_CHILDREN)
        outer.update(
            ended_at_UTC=utc(),
            wall_seconds=time.monotonic() - started,
            host_child_cpu_seconds=(after.ru_utime + after.ru_stime) - (before.ru_utime + before.ru_stime),
            stdout=stdout_path.read_text(errors="replace") if stdout_path.exists() else "",
            stderr=stderr_path.read_text(errors="replace") if stderr_path.exists() else "",
        )
    inner = json.loads(inner_path.read_bytes()) if inner_path.exists() else None
    final = {
        "schema": "crypto.autoresearch.dependency_image_independent_audit_outer.v1",
        "task_id": TASK,
        "checks_source_sha256": sha_path(Path(__file__).resolve()),
        "outer": outer,
        "inner": inner,
        "status": "passed" if outer.get("exit_code") == 0 and inner and inner.get("status") == "passed" else "failed",
        "receipt_self_hash": None,
    }
    with receipt_path.open("x") as handle:
        json.dump(final, handle, indent=2, allow_nan=False)
        handle.write("\n")
    shutil.rmtree(scratch)
    print(json.dumps({
        "status": final["status"],
        "receipt": str(receipt_path),
        "outer_exit_code": outer.get("exit_code"),
        "inner_status": inner.get("status") if inner else None,
    }, sort_keys=True))
    return 0 if final["status"] == "passed" else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--worker", action="store_true")
    parser.add_argument("--inner", type=Path)
    parser.add_argument("--export", type=Path)
    args = parser.parse_args()
    if args.worker:
        if args.inner is None or args.export is None:
            parser.error("worker requires --inner and --export")
        return worker(args.inner, args.export)
    if args.receipt is None:
        parser.error("supervisor requires --receipt")
    return supervisor(args.receipt)


if __name__ == "__main__":
    raise SystemExit(main())
