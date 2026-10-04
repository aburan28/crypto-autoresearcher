"""Exact-ID Docker host adapter for a future governed native invocation.

The adapter is real but inert until ``run_case`` is called.  Tests inject a
fixed command transport and exercise this production orchestration without
contacting Docker.  A future live handoff may use ``SubprocessTransport``.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from io import BytesIO
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import tarfile
import time
from typing import Any, Callable, Mapping, Protocol, Sequence
import uuid

from container import (
    CASES,
    RESULT_SCHEMA,
    PINNED_IMAGE,
    PINNED_IMAGE_DIGEST,
    TASK_ID,
    ContainerBindingError,
    ContainerInspection,
    inspection_from_docker_json,
    planned_container,
    require_full_container_id,
    require_inspection_matches,
)


DOCKER = "/usr/local/bin/docker"
ENDPOINT = "unix:///Users/adamburan/.docker/run/docker.sock"
MAX_TEXT_BYTES = 2 * 1024 * 1024
HELPERS = ("container.py", "supervisor.py")


class HostError(RuntimeError):
    def __init__(self, code: str, detail: str = "") -> None:
        super().__init__(f"{code}{(': ' + detail) if detail else ''}")
        self.code = code
        self.detail = detail


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class CommandResult:
    argv: tuple[str, ...]
    started_at_UTC: str
    ended_at_UTC: str
    exit_code: int | None
    stdout: str
    stderr: str
    timed_out: bool
    timeout_seconds: float
    wall_seconds: float
    stdin_bytes: int
    stdin_sha256: str | None
    process_pid: int | None
    process_group_id: int | None
    terminal_observed: bool
    session_id: str | None = None
    yielded_session_ids: tuple[str, ...] = ()
    stdout_base64: str | None = None
    stderr_base64: str | None = None
    cleanup_failures: tuple[Mapping[str, str], ...] = ()


class CommandTransport(Protocol):
    def run(self, argv: Sequence[str], stdin: bytes | None, timeout_seconds: float) -> CommandResult: ...


class CommandTransportFailure(HostError):
    """A failed invocation with the observations available at that boundary."""

    def __init__(self, observations: Mapping[str, Any]) -> None:
        self.observations = dict(observations)
        primary = observations["primary_exception"]
        super().__init__("command_transport_failed", f"{primary['type']}:{primary['message']}")


class SubprocessTransport:
    """Capture returned bytes and retain launch/cleanup failures independently."""

    def run(self, argv: Sequence[str], stdin: bytes | None, timeout_seconds: float) -> CommandResult:
        started = utc_now()
        began = time.monotonic()
        row: dict[str, Any] = {
            "argv": list(argv), "started_at_UTC": started,
            "timeout_seconds": timeout_seconds,
            "stdin_bytes": len(stdin or b""),
            "stdin_sha256": hashlib.sha256(stdin).hexdigest() if stdin is not None else None,
            "process_pid": None, "process_group_id": None,
            "exit_code": None, "terminal_observed": None,
            "stdout": None, "stderr": None,
            "stdout_base64": None, "stderr_base64": None,
            "launch_state": "not_started", "timed_out": False,
            "cleanup_failures": [],
        }

        def record_streams(out: bytes | None, err: bytes | None) -> None:
            # Store bytes losslessly before supplementary human-readable decoding.
            for name, value in (("stdout", out), ("stderr", err)):
                if value is not None:
                    row[name + "_base64"] = base64.b64encode(value).decode("ascii")
                    row[name] = value.decode("utf-8", errors="replace")

        def fail(primary: Exception) -> None:
            row["primary_exception"] = {"type": type(primary).__name__, "message": str(primary)}
            row["ended_at_UTC"] = utc_now()
            row["wall_seconds"] = time.monotonic() - began
            raise CommandTransportFailure(row) from primary

        try:
            process = subprocess.Popen(
                list(argv), stdin=subprocess.PIPE if stdin is not None else subprocess.DEVNULL,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True,
            )
        except Exception as primary:
            # No returned handle/exit/output is invented after Popen fails.
            fail(primary)
        row.update(launch_state="started", process_pid=process.pid, process_group_id=process.pid)
        try:
            out, err = process.communicate(input=stdin, timeout=timeout_seconds)
            record_streams(out, err)
        except Exception as primary:
            row["timed_out"] = isinstance(primary, subprocess.TimeoutExpired)
            if isinstance(primary, subprocess.TimeoutExpired):
                record_streams(primary.output, primary.stderr)
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass  # Terminal state is established by communicate, not guessed.
            except Exception as cleanup:
                row["cleanup_failures"].append({"phase": "kill_owned_group", "type": type(cleanup).__name__, "message": str(cleanup)})
            try:
                out, err = process.communicate(timeout=timeout_seconds)
                # communicate returns cumulative output after TimeoutExpired.
                # Its prefix must not be appended a second time.
                record_streams(out, err)
            except Exception as cleanup:
                if isinstance(cleanup, subprocess.TimeoutExpired):
                    record_streams(cleanup.output, cleanup.stderr)
                row["cleanup_failures"].append({"phase": "reap_owned_process", "type": type(cleanup).__name__, "message": str(cleanup)})
            row.update(exit_code=process.returncode, terminal_observed=process.returncode is not None)
            if not row["timed_out"] or row["cleanup_failures"]:
                fail(primary)
        row.update(exit_code=process.returncode, terminal_observed=process.returncode is not None,
                   ended_at_UTC=utc_now(), wall_seconds=time.monotonic() - began)
        return CommandResult(
            argv=tuple(argv), started_at_UTC=started, ended_at_UTC=row["ended_at_UTC"],
            exit_code=row["exit_code"], stdout=row["stdout"], stderr=row["stderr"],
            timed_out=row["timed_out"], timeout_seconds=timeout_seconds,
            wall_seconds=row["wall_seconds"], stdin_bytes=row["stdin_bytes"], stdin_sha256=row["stdin_sha256"],
            process_pid=process.pid, process_group_id=process.pid,
            terminal_observed=row["terminal_observed"],
            stdout_base64=row["stdout_base64"], stderr_base64=row["stderr_base64"],
            cleanup_failures=tuple(row["cleanup_failures"]),
        )


@dataclass
class HostOutcome:
    task_id: str
    case_id: str
    started_at_UTC: str
    status: str = "running"
    classification: str | None = None
    primary_failure: Mapping[str, Any] | None = None
    failures: list[Mapping[str, Any]] = field(default_factory=list)
    container_name: str | None = None
    container_id: str | None = None
    helper_source_sha256: Mapping[str, str] = field(default_factory=dict)
    helper_archive_sha256: str | None = None
    startup_identity: Mapping[str, Any] | None = None
    image_inspection_json: str | None = None
    initial_container_inspection_json: str | None = None
    verified_inspection: Mapping[str, Any] | None = None
    inner_report: Mapping[str, Any] | None = None
    terminal_container_inspections: list[Mapping[str, Any]] = field(default_factory=list)
    complete_logs: list[Mapping[str, Any]] = field(default_factory=list)
    commands: list[Mapping[str, Any]] = field(default_factory=list)
    cleanup: list[Mapping[str, Any]] = field(default_factory=list)
    exact_container_removed: bool = False
    operational_container_start_attempts: int = 0
    ended_at_UTC: str | None = None
    wall_seconds: float | None = None

    def as_dict(self) -> Mapping[str, Any]:
        return asdict(self)


def _command_row(result: CommandResult) -> Mapping[str, Any]:
    return asdict(result)


def _require_success(result: CommandResult, code: str) -> str:
    if result.timed_out or result.exit_code != 0 or not result.terminal_observed:
        raise HostError(code, f"exit={result.exit_code};timeout={result.timed_out}")
    return result.stdout


def _single_inspect(raw: str, expected_id: str) -> Mapping[str, Any]:
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise HostError("malformed_terminal_inspection") from exc
    if isinstance(value, list):
        if len(value) != 1:
            raise HostError("ambiguous_terminal_inspection")
        value = value[0]
    if not isinstance(value, Mapping) or value.get("Id") != expected_id:
        raise HostError("terminal_inspection_identity_mismatch")
    return dict(value)


def _parse_inner(stdout: str) -> Mapping[str, Any]:
    encoded = stdout.encode("utf-8")
    if len(encoded) > MAX_TEXT_BYTES:
        raise HostError("inner_report_too_large")
    lines = [line for line in stdout.splitlines() if line.strip()]
    if len(lines) != 1:
        raise HostError("inner_report_missing_or_ambiguous", f"lines={len(lines)}")
    try:
        value = json.loads(lines[0])
    except json.JSONDecodeError as exc:
        raise HostError("inner_report_malformed_or_truncated") from exc
    if not isinstance(value, Mapping):
        raise HostError("inner_report_not_object")
    return dict(value)


def _tar_helpers(helper_dir: Path, expected_hashes: Mapping[str, str]) -> tuple[bytes, Mapping[str, str]]:
    actual: dict[str, str] = {}
    payloads: dict[str, bytes] = {}
    for name in HELPERS:
        path = helper_dir / name
        payload = path.read_bytes()
        digest = hashlib.sha256(payload).hexdigest()
        if expected_hashes.get(name) != digest:
            raise HostError("helper_source_hash_mismatch", name)
        actual[name] = digest
        payloads[name] = payload
    archive = BytesIO()
    with tarfile.open(fileobj=archive, mode="w") as tar:
        for name in HELPERS:
            info = tarfile.TarInfo(f"group-oom/{name}")
            info.size = len(payloads[name])
            info.mode = 0o444
            info.mtime = 0
            info.uid = info.gid = 0
            info.uname = info.gname = ""
            tar.addfile(info, BytesIO(payloads[name]))
    return archive.getvalue(), actual


class DockerHostAdapter:
    """Create, inspect, attach, terminally inspect, log, and remove one exact ID."""

    def __init__(
        self,
        transport: CommandTransport,
        helper_dir: Path,
        expected_helper_hashes: Mapping[str, str],
        nonce_factory: Callable[[], str] | None = None,
    ) -> None:
        self.transport = transport
        self.helper_dir = helper_dir
        self.expected_helper_hashes = dict(expected_helper_hashes)
        self.nonce_factory = nonce_factory or (lambda: uuid.uuid4().hex[:12])

    @staticmethod
    def _docker(*args: str) -> tuple[str, ...]:
        if "bedrock" in ENDPOINT.lower():
            raise HostError("prohibited_endpoint_token")
        return (DOCKER, "--host", ENDPOINT, *args)

    def _run(
        self,
        outcome: HostOutcome,
        args: Sequence[str],
        stdin: bytes | None = None,
        timeout: float = 30.0,
    ) -> CommandResult:
        argv = self._docker(*args)
        started = utc_now()
        began = time.monotonic()
        row: dict[str, Any] = {
            "argv": list(argv), "started_at_UTC": started,
            "attempt_started_at_UTC": started, "timeout_seconds": timeout,
            "stdin_bytes": len(stdin or b""),
            "stdin_sha256": hashlib.sha256(stdin).hexdigest() if stdin is not None else None,
            "launch_state": "unknown", "exit_code": None,
            "process_pid": None, "process_group_id": None, "terminal_observed": None,
            "stdout": None, "stderr": None, "stdout_base64": None, "stderr_base64": None,
        }
        outcome.commands.append(row)
        try:
            result = self.transport.run(argv, stdin, timeout)
        except Exception as exc:
            if isinstance(exc, CommandTransportFailure):
                row.update(exc.observations)
            else:
                row["primary_exception"] = {"type": type(exc).__name__, "message": str(exc)}
                row["ended_at_UTC"] = utc_now()
                row["wall_seconds"] = time.monotonic() - began
            raise
        row.update(_command_row(result))
        row["launch_state"] = "started" if result.process_pid is not None else "unavailable_in_transport_result"
        return result

    def _inspect(self, outcome: HostOutcome, cid: str, phase: str) -> Mapping[str, Any]:
        result = self._run(outcome, ("inspect", cid), timeout=20)
        raw = _require_success(result, f"{phase}_inspect_failed")
        inspected = _single_inspect(raw, cid)
        outcome.terminal_container_inspections.append({"phase": phase, "inspection": inspected})
        return inspected

    def _logs(self, outcome: HostOutcome, cid: str, phase: str) -> None:
        result = self._run(outcome, ("logs", "--timestamps", cid), timeout=20)
        outcome.complete_logs.append(
            {
                "phase": phase,
                "exit_code": result.exit_code,
                "timed_out": result.timed_out,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "stdout_prefix": result.stdout[:4096],
                "stderr_prefix": result.stderr[:4096],
            }
        )
        if result.timed_out or result.exit_code != 0 or not result.terminal_observed:
            raise HostError("complete_container_logs_unavailable", phase)

    def _failure(self, outcome: HostOutcome, phase: str, code: str, detail: str = "") -> None:
        row = {"at_UTC": utc_now(), "phase": phase, "code": code, "detail": detail}
        outcome.failures.append(row)
        if outcome.primary_failure is None:
            outcome.primary_failure = row

    def _cleanup_command(self, outcome: HostOutcome, args: Sequence[str], *, action: str) -> CommandResult | None:
        """Retain cleanup transport failures in the outcome that owns the call.

        Callers reach this helper only after exact created-container identity
        verification. Missing transport observations remain unknown.
        """
        command_index = len(outcome.commands)
        try:
            result = self._run(outcome, args, timeout=20)
        except Exception as error:
            self._failure(outcome, "cleanup", "exact_container_cleanup_transport_failed",
                          f"{action}: {type(error).__name__}:{error}")
            facts: dict[str, Any] = {"type": type(error).__name__, "message": str(error)}
            if isinstance(error, CommandTransportFailure):
                facts["transport_observations"] = dict(error.observations)
            outcome.cleanup.append({
                "action": action, "container_id": args[-1], "result": None,
                "command_index": command_index if len(outcome.commands) > command_index else None,
                "transport_exception": facts,
                "launch_state": outcome.commands[command_index].get("launch_state", "unknown")
                    if len(outcome.commands) > command_index else "unknown",
            })
            return None
        outcome.cleanup.append({"action": action, "container_id": args[-1],
                                "command_index": command_index, "result": _command_row(result)})
        for failure in result.cleanup_failures:
            self._failure(outcome, "cleanup", "cleanup_command_resource_disposition_failed",
                          f"{action}: {failure}")
        return result

    def _create_argv(self, name: str, nonce: str) -> tuple[str, ...]:
        plan = planned_container()
        mount = plan.mounts[0]
        return (
            "create",
            "--pull",
            "never",
            "--name",
            name,
            "--label",
            f"crypto.autoresearch.task={TASK_ID}",
            "--label",
            f"crypto.autoresearch.nonce={nonce}",
            "--platform",
            plan.platform,
            "--user",
            plan.user,
            "--network",
            plan.network,
            "--read-only",
            "--cap-drop",
            "ALL",
            "--cap-add",
            "SETUID",
            "--cap-add",
            "SETGID",
            "--security-opt",
            "no-new-privileges:true",
            "--cgroupns",
            "host",
            "--pid",
            "private",
            "--pids-limit",
            str(plan.pids_limit),
            "--cpus",
            str(plan.cpu_quota_cores),
            "--memory",
            str(plan.outer_memory_bytes),
            "--memory-swap",
            str(plan.outer_memory_swap_total_bytes),
            "--tmpfs",
            "/tmp:rw,size=16m",
            "--mount",
            f"type={mount.type},source={mount.source},target={mount.target}",
            "--interactive",
            "--attach",
            "stdin",
            "--attach",
            "stdout",
            "--attach",
            "stderr",
            plan.image,
            "python3",
            "-B",
            "/opt/group-oom/container.py",
        )

    def run_case(self, case_id: str) -> HostOutcome:
        if case_id not in CASES:
            raise HostError("unknown_fixed_case", case_id)
        began = time.monotonic()
        outcome = HostOutcome(TASK_ID, case_id, utc_now())
        cid: str | None = None
        attach_succeeded = False
        inner_cleanup_complete = False
        terminal_seen = False
        identity_verified = False
        nonce = self.nonce_factory()
        if not re.fullmatch(r"[0-9a-f]{12}", nonce):
            raise HostError("unsafe_container_nonce")
        name = f"{TASK_ID.lower()}-{case_id.replace('_', '-')}-{nonce}"
        outcome.container_name = name
        try:
            archive, hashes = _tar_helpers(self.helper_dir, self.expected_helper_hashes)
            outcome.helper_source_sha256 = hashes
            outcome.helper_archive_sha256 = hashlib.sha256(archive).hexdigest()

            image_result = self._run(outcome, ("image", "inspect", PINNED_IMAGE), timeout=20)
            image_json = _require_success(image_result, "cached_pinned_image_unavailable")
            outcome.image_inspection_json = image_json
            image = _single_inspect(image_json, str(json.loads(image_json)[0]["Id"]) if image_json.lstrip().startswith("[") else str(json.loads(image_json)["Id"]))
            image_id = str(image.get("Id", ""))
            if image.get("Os") != "linux" or image.get("Architecture") != "arm64":
                raise HostError("cached_image_platform_mismatch")
            if PINNED_IMAGE_DIGEST not in {str(value).split("@", 1)[-1] for value in (image.get("RepoDigests") or [])}:
                raise HostError("cached_image_digest_mismatch")

            created = self._run(outcome, self._create_argv(name, nonce), timeout=30)
            cid = require_full_container_id(_require_success(created, "container_create_failed").strip())
            outcome.container_id = cid

            inspected_result = self._run(outcome, ("inspect", cid), timeout=20)
            inspected_json = _require_success(inspected_result, "initial_inspect_failed")
            outcome.initial_container_inspection_json = inspected_json
            inspection: ContainerInspection = inspection_from_docker_json(inspected_json, image_json, cid)
            require_inspection_matches(inspection, cid, image_id, nonce)
            outcome.verified_inspection = asdict(inspection)
            identity_verified = True

            copied = self._run(outcome, ("cp", "-", f"{cid}:/opt"), stdin=archive, timeout=20)
            _require_success(copied, "helper_copy_failed")

            startup = {"task_id": TASK_ID, "expected_container_id": cid, "case_id": case_id}
            startup_bytes = (json.dumps(startup, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
            outcome.startup_identity = {
                **startup,
                "stdin_bytes": len(startup_bytes),
                "stdin_sha256": hashlib.sha256(startup_bytes).hexdigest(),
            }
            outcome.operational_container_start_attempts = 1
            attached = self._run(outcome, ("start", "--attach", "--interactive", cid), stdin=startup_bytes, timeout=60)
            attach_succeeded = attached.exit_code == 0 and not attached.timed_out and attached.terminal_observed
            try:
                outcome.inner_report = _parse_inner(attached.stdout)
                if outcome.inner_report.get("schema") != RESULT_SCHEMA:
                    raise HostError("inner_report_schema_mismatch")
                if "startup_failure" in outcome.inner_report:
                    raise HostError("inner_startup_failure", json.dumps(outcome.inner_report["startup_failure"], sort_keys=True))
                if outcome.inner_report.get("startup_identity") != startup:
                    raise HostError("inner_report_startup_identity_mismatch")
                inner = outcome.inner_report.get("outcome") if isinstance(outcome.inner_report, Mapping) else None
                inner_cleanup_complete = bool(
                    isinstance(inner, Mapping)
                    and inner.get("status") == "inner_complete"
                    and inner.get("cleanup_complete") is True
                )
            except HostError as exc:
                self._failure(outcome, "inner_report", exc.code, exc.detail)

            terminal = self._inspect(outcome, cid, "terminal")
            terminal_seen = True
            self._logs(outcome, cid, "terminal")
            state = terminal.get("State") if isinstance(terminal.get("State"), Mapping) else {}
            outer_ok = (
                not bool(state.get("Running"))
                and state.get("ExitCode") == 0
                and state.get("OOMKilled") is False
                and attach_succeeded
            )
            if not outer_ok:
                self._failure(
                    outcome,
                    "outer_terminal",
                    "outer_container_terminal_not_clean",
                    json.dumps(
                        {
                            "attach_exit": attached.exit_code,
                            "attach_timeout": attached.timed_out,
                            "running": state.get("Running"),
                            "exit_code": state.get("ExitCode"),
                            "oom_killed": state.get("OOMKilled"),
                        },
                        sort_keys=True,
                    ),
                )
            if not inner_cleanup_complete:
                self._failure(outcome, "inner_cleanup", "inner_cleanup_or_report_incomplete")
            if outcome.primary_failure is None and outer_ok and inner_cleanup_complete:
                inner = outcome.inner_report["outcome"]
                inner_classification = inner.get("classification")
                expected = {
                    "exact_profile": "profile_accepted",
                    "group_zero_refused": "typed_refusal",
                    "small_group_oom": "oom_observed_inner_pending_outer",
                }[case_id]
                if inner_classification != expected:
                    self._failure(outcome, "classification", "inner_classification_mismatch", str(inner_classification))
                else:
                    outcome.status = "complete"
                    outcome.classification = "oom_observed" if case_id == "small_group_oom" else str(inner_classification)
        except (HostError, ContainerBindingError) as exc:
            code = exc.code if isinstance(exc, HostError) else "container_binding_refused"
            detail = exc.detail if isinstance(exc, HostError) else str(exc)
            self._failure(outcome, "primary", code, detail)
        except Exception as exc:
            self._failure(outcome, "primary", "unexpected_host_error", f"{type(exc).__name__}:{exc}")
        finally:
            if cid is not None and not identity_verified:
                outcome.cleanup.append({
                    "action": "refuse_mutation_of_unverified_container_identity",
                    "container_id": cid,
                    "verified_owned_identity": False,
                })
            if cid is not None and identity_verified:
                if not terminal_seen:
                    try:
                        self._inspect(outcome, cid, "failure_pre_cleanup")
                    except Exception as exc:
                        self._failure(outcome, "cleanup", "precleanup_inspect_failed", f"{type(exc).__name__}:{exc}")
                if outcome.status != "complete" or not inner_cleanup_complete:
                    self._cleanup_command(outcome, ("kill", "--signal", "KILL", cid),
                        action="terminate_exact_created_container_on_incomplete_path")
                    try:
                        self._inspect(outcome, cid, "after_exact_kill")
                    except Exception as exc:
                        self._failure(outcome, "cleanup", "postkill_inspect_failed", f"{type(exc).__name__}:{exc}")
                try:
                    self._logs(outcome, cid, "final_before_remove")
                except Exception as exc:
                    self._failure(outcome, "cleanup", "final_logs_failed", f"{type(exc).__name__}:{exc}")
                removed = self._cleanup_command(outcome, ("rm", cid), action="remove_exact_created_container")
                outcome.exact_container_removed = bool(removed is not None and removed.exit_code == 0
                                                       and not removed.timed_out and removed.terminal_observed)
                if not outcome.exact_container_removed:
                    self._failure(outcome, "cleanup", "exact_container_remove_failed")
            if outcome.primary_failure is not None or not outcome.exact_container_removed:
                outcome.status = "failed"
            outcome.ended_at_UTC = utc_now()
            outcome.wall_seconds = time.monotonic() - began
        return outcome
