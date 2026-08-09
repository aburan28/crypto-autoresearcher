"""Privacy-preserving, session-scoped Codex CLI runtime verification.

This module deliberately does not inspect the Codex model catalog or mutate the
repository's model bindings.  It verifies one newly-created ``codex exec``
thread against that thread's single SQLite row and rollout file.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sqlite3
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path, PurePath
from typing import Any, Callable, Iterable
from urllib.parse import quote

from . import config as config_module


SCHEMA = "crypto.autoresearch.codex_runtime_session_receipt.v1"
PROBE_PROMPT = "Print exactly PROBE_OK and nothing else."
PROBE_OUTPUT = "PROBE_OK"
STATE_QUERY = (
    "SELECT id, rollout_path, cwd, source, model, reasoning_effort, "
    "model_provider, cli_version, created_at, updated_at "
    "FROM threads WHERE id = ? LIMIT 2"
)
STATE_COLUMNS = (
    "id", "rollout_path", "cwd", "source", "model", "reasoning_effort",
    "model_provider", "cli_version", "created_at", "updated_at",
)
FAILURE_CODES = frozenset({
    "invalid_argument", "receipt_exists", "codex_version_failed",
    "forbidden_inference_target",
    "launch_timeout", "launch_nonzero_exit", "probe_output_mismatch",
    "thread_id_missing", "thread_id_ambiguous", "state_db_read_failed",
    "state_row_missing", "state_row_ambiguous", "rollout_path_invalid",
    "rollout_missing", "session_meta_missing", "session_meta_ambiguous",
    "turn_context_missing", "turn_context_ambiguous", "session_id_mismatch",
    "model_mismatch", "reasoning_effort_mismatch", "provider_mismatch",
    "cli_version_mismatch", "workdir_mismatch", "source_mismatch",
    "sandbox_mismatch", "timestamp_invalid",
    "runtime_bindings_check_failed", "receipt_write_failed",
    "privacy_invariant_failed", "metadata_schema_unsupported",
})
_VERSION_RE = re.compile(r"(?<![0-9])([0-9]+\.[0-9]+\.[0-9]+(?:[-+][A-Za-z0-9.-]+)?)(?![0-9])")
_READ_ONLY_SANDBOX_ENCODINGS = (
    "read-only",
    {"type": "read-only"},
    {"mode": "read-only"},
)
_TIMESTAMP_SLOP_SECONDS = 5.0


class CodexRuntimeProbeError(RuntimeError):
    """A fail-closed probe outcome; ``codes`` are safe to print."""

    def __init__(self, codes: Iterable[str], *, receipt: Path | None = None,
                 receipt_written: bool = False):
        self.codes = tuple(dict.fromkeys(codes))
        self.receipt = receipt
        self.receipt_written = receipt_written
        super().__init__(", ".join(self.codes))


class _ProbeFailure(Exception):
    def __init__(self, *codes: str):
        unknown = set(codes) - FAILURE_CODES
        if unknown:
            raise AssertionError(f"unknown probe failure code(s): {sorted(unknown)}")
        self.codes = tuple(dict.fromkeys(codes))


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _sha256_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def _canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")


def _argv_sha256(argv: Iterable[str]) -> str:
    return _sha256_bytes(b"\0".join(os.fsencode(arg) for arg in argv))


def _path_sha256(path: Path) -> str:
    return _sha256_bytes(os.fsencode(str(path)))


def _bytes(value: bytes | str | None) -> bytes:
    if value is None:
        return b""
    return value if isinstance(value, bytes) else value.encode("utf-8")


def _existing_path(value: str | os.PathLike[str], *, kind: str) -> Path:
    try:
        path = Path(value).expanduser().resolve(strict=True)
    except (OSError, RuntimeError):
        raise _ProbeFailure("invalid_argument") from None
    if kind == "file" and not path.is_file():
        raise _ProbeFailure("invalid_argument")
    if kind == "dir" and not path.is_dir():
        raise _ProbeFailure("invalid_argument")
    return path


def _receipt_target(value: str | os.PathLike[str]) -> Path:
    raw = Path(value).expanduser()
    try:
        parent = raw.parent.resolve(strict=True)
    except (OSError, RuntimeError):
        raise CodexRuntimeProbeError(("invalid_argument",)) from None
    if not parent.is_dir() or not raw.name:
        raise CodexRuntimeProbeError(("invalid_argument",))
    target = parent / raw.name
    try:
        target.lstat()
    except FileNotFoundError:
        return target
    except OSError:
        raise CodexRuntimeProbeError(("invalid_argument",), receipt=target) from None
    raise CodexRuntimeProbeError(("receipt_exists",), receipt=target)


def _empty_receipt(*, task_id: str, role: str, independent: bool,
                   policy: str, canonical_policy: str | None, model: str,
                   effort: str, workdir: str | None,
                   cfg: config_module.Config) -> dict[str, Any]:
    return {"runtime_session_receipt": {
        "schema": SCHEMA,
        "identity": {
            "task_id": task_id,
            "role": role,
            "independent_session_id": None,
            "independent_session": independent,
            "recorded_at": None,
        },
        "requested": {
            "policy": policy,
            "canonical_policy": canonical_policy,
            "model": model,
            "reasoning_effort": effort,
            "workdir": workdir,
            "sandbox": "read-only",
            "source": "exec",
        },
        "runtime": {
            "runtime": "codex_cli",
            "provider": None,
            "cli_version": None,
            "codex_binary_sha256": None,
            "adapter_version": config_module.ADAPTER_VERSION,
            "config_digest": cfg.digest,
        },
        "version_check": None,
        "launch": {
            "safe_argv": [],
            "command_sha256": None,
            "state_db_path_sha256": None,
            "receipt_path_sha256": None,
            "started_at": None,
            "ended_at": None,
            "exit_code": None,
            "stdout_bytes": 0,
            "stderr_bytes": 0,
            "stdout_sha256": _sha256_bytes(b""),
            "stderr_sha256": _sha256_bytes(b""),
            "thread_started_event_count": 0,
            "probe_output_matches": False,
        },
        "observed": {
            "state_row_allowlist": None,
            "state_row_sha256": None,
            "session_meta_sha256": None,
            "turn_context_sha256": None,
            "rollout_relative_path": None,
            "rollout_path_sha256": None,
        },
        "verification": {
            "status": "failed",
            "runtime_resolution_verified": False,
            "verification_scope": "exact_codex_session_only",
            "global_backend_verified": False,
            "model_bindings_mutated": False,
            "model_matches": False,
            "reasoning_effort_matches": False,
            "provider_matches": False,
            "cli_version_matches": False,
            "workdir_matches": False,
            "source_matches": False,
            "sandbox_matches": False,
            "session_id_matches": False,
            "timestamp_order_valid": False,
            "runtime_bindings_check": None,
            "failures": [],
        },
    }}


def _run(argv: list[str], *, cwd: Path, timeout: int,
         runner: Callable[..., subprocess.CompletedProcess[Any]]) -> subprocess.CompletedProcess[Any]:
    return runner(argv, cwd=str(cwd), stdin=subprocess.DEVNULL,
                  stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                  timeout=timeout, check=False, shell=False)


def _process_record(argv: list[str], started: datetime, ended: datetime,
                    result: subprocess.CompletedProcess[Any]) -> dict[str, Any]:
    stdout, stderr = _bytes(result.stdout), _bytes(result.stderr)
    return {
        "safe_argv": list(argv),
        "command_sha256": _argv_sha256(argv),
        "started_at": _iso(started),
        "ended_at": _iso(ended),
        "exit_code": int(result.returncode),
        "stdout_bytes": len(stdout),
        "stderr_bytes": len(stderr),
        "stdout_sha256": _sha256_bytes(stdout),
        "stderr_sha256": _sha256_bytes(stderr),
    }


def _parse_version(stdout: bytes, stderr: bytes) -> str:
    text = (stdout + b"\n" + stderr).decode("utf-8", errors="replace")
    versions = list(dict.fromkeys(_VERSION_RE.findall(text)))
    if len(versions) != 1:
        raise _ProbeFailure("codex_version_failed")
    return versions[0]


def _valid_thread_id(value: Any) -> bool:
    if not isinstance(value, str) or not value:
        return False
    try:
        uuid.UUID(value)
    except (ValueError, AttributeError):
        return False
    return True


def _parse_launch_stdout(stdout: bytes) -> tuple[str | None, int, bool, datetime | None]:
    ids: list[str] = []
    messages: list[str] = []
    thread_events = 0
    thread_time: datetime | None = None
    for raw_line in stdout.splitlines(keepends=True):
        if not raw_line.strip():
            continue
        try:
            event = json.loads(raw_line)
        except (json.JSONDecodeError, UnicodeDecodeError):
            raise _ProbeFailure("metadata_schema_unsupported") from None
        if not isinstance(event, dict) or not isinstance(event.get("type"), str):
            raise _ProbeFailure("metadata_schema_unsupported")
        if event["type"] == "thread.started":
            thread_events += 1
            thread_id = event.get("thread_id")
            if _valid_thread_id(thread_id):
                ids.append(thread_id)
            if event.get("timestamp") is not None:
                thread_time = _parse_timestamp(event["timestamp"])
        elif event["type"] == "item.completed":
            item = event.get("item")
            if isinstance(item, dict) and item.get("type") == "agent_message" and isinstance(item.get("text"), str):
                messages.append(item["text"])
    normalized = "\n".join(messages).strip()
    # Event cardinality is intentionally independent of identifier validity:
    # accepting a valid ID after any malformed second thread event would make
    # the session identity ambiguous.
    return (ids[0] if len(ids) == 1 else None, thread_events,
            normalized == PROBE_OUTPUT, thread_time)


def _query_state_row(state_db: Path, thread_id: str) -> dict[str, Any]:
    uri = "file:" + quote(str(state_db), safe="/") + "?mode=ro"
    try:
        connection = sqlite3.connect(uri, uri=True)
        try:
            connection.execute("PRAGMA query_only=ON")
            if connection.execute("PRAGMA query_only").fetchone() != (1,):
                raise sqlite3.DatabaseError("query_only was not enabled")
            rows = connection.execute(STATE_QUERY, (thread_id,)).fetchall()
        finally:
            connection.close()
    except sqlite3.Error:
        raise _ProbeFailure("state_db_read_failed") from None
    if not rows:
        raise _ProbeFailure("state_row_missing")
    if len(rows) != 1:
        raise _ProbeFailure("state_row_ambiguous")
    row = dict(zip(STATE_COLUMNS, rows[0], strict=True))
    if any(row[name] is None for name in STATE_COLUMNS):
        raise _ProbeFailure("metadata_schema_unsupported")
    string_columns = STATE_COLUMNS[:8]
    if any(not isinstance(row[name], str) for name in string_columns):
        raise _ProbeFailure("metadata_schema_unsupported")
    if any(not isinstance(row[name], (str, int, float)) or isinstance(row[name], bool)
           for name in ("created_at", "updated_at")):
        raise _ProbeFailure("metadata_schema_unsupported")
    return row


def _resolve_rollout(state_db: Path, raw_value: Any) -> tuple[Path, str]:
    if not isinstance(raw_value, str) or not raw_value or "\0" in raw_value:
        raise _ProbeFailure("rollout_path_invalid")
    raw = Path(raw_value)
    if ".." in PurePath(raw_value).parts:
        raise _ProbeFailure("rollout_path_invalid")
    codex_home = state_db.parent.resolve()
    candidate = raw if raw.is_absolute() else codex_home / raw
    try:
        resolved = candidate.resolve(strict=True)
        relative = resolved.relative_to(codex_home)
    except FileNotFoundError:
        raise _ProbeFailure("rollout_missing") from None
    except (OSError, RuntimeError, ValueError):
        raise _ProbeFailure("rollout_path_invalid") from None
    if not resolved.is_file():
        raise _ProbeFailure("rollout_path_invalid")
    return resolved, relative.as_posix()


def _event_time(event: dict[str, Any], payload: dict[str, Any]) -> datetime:
    value = event.get("timestamp", payload.get("timestamp"))
    return _parse_timestamp(value)


def _parse_rollout(path: Path) -> tuple[dict[str, Any], str, dict[str, Any], str]:
    sessions: list[tuple[dict[str, Any], str]] = []
    turns: list[tuple[dict[str, Any], str]] = []
    try:
        with path.open("rb") as handle:
            for line in handle:
                if not line.strip():
                    continue
                try:
                    event = json.loads(line)
                except (json.JSONDecodeError, UnicodeDecodeError):
                    raise _ProbeFailure("metadata_schema_unsupported") from None
                if not isinstance(event, dict):
                    raise _ProbeFailure("metadata_schema_unsupported")
                event_type = event.get("type")
                if event_type not in ("session_meta", "turn_context"):
                    continue
                payload = event.get("payload")
                if not isinstance(payload, dict):
                    raise _ProbeFailure("metadata_schema_unsupported")
                allowlist = (("id", "cwd", "source", "cli_version",
                              "model_provider", "timestamp")
                             if event_type == "session_meta" else
                             ("session_id", "cwd", "model", "effort",
                              "model_provider", "sandbox_policy", "timestamp"))
                selected = {key: payload[key] for key in allowlist if key in payload}
                selected["_event_time"] = _event_time(event, payload)
                item = (selected, _sha256_bytes(line))
                (sessions if event_type == "session_meta" else turns).append(item)
    except _ProbeFailure:
        raise
    except OSError:
        raise _ProbeFailure("rollout_missing") from None
    if not sessions:
        raise _ProbeFailure("session_meta_missing")
    if len(sessions) != 1:
        raise _ProbeFailure("session_meta_ambiguous")
    if not turns:
        raise _ProbeFailure("turn_context_missing")
    if len(turns) != 1:
        raise _ProbeFailure("turn_context_ambiguous")
    session, session_hash = sessions[0]
    turn, turn_hash = turns[0]
    required_session = ("id", "cwd", "source", "cli_version")
    required_turn = ("model", "effort", "cwd", "sandbox_policy")
    if any(session.get(key) is None for key in required_session) or any(
            turn.get(key) is None for key in required_turn):
        raise _ProbeFailure("metadata_schema_unsupported")
    return session, session_hash, turn, turn_hash


def _parse_timestamp(value: Any) -> datetime:
    try:
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            numeric = float(value)
            if abs(numeric) > 10_000_000_000:
                numeric /= 1000.0
            return datetime.fromtimestamp(numeric, tz=timezone.utc)
        if isinstance(value, str) and value.strip():
            text = value.strip()
            try:
                return _parse_timestamp(float(text))
            except ValueError:
                parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
                if parsed.tzinfo is None:
                    parsed = parsed.replace(tzinfo=timezone.utc)
                return parsed.astimezone(timezone.utc)
    except (ValueError, OverflowError, OSError):
        pass
    raise _ProbeFailure("timestamp_invalid")


def _canonical_existing_cwd(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    try:
        path = Path(value).expanduser().resolve(strict=True)
    except (OSError, RuntimeError):
        return None
    return str(path) if path.is_dir() else None


def _sandbox_is_read_only(value: Any) -> bool:
    return any(value == encoding for encoding in _READ_ONLY_SANDBOX_ENCODINGS)


def _within(value: datetime, lower: datetime, upper: datetime) -> bool:
    return (value.timestamp() >= lower.timestamp() - _TIMESTAMP_SLOP_SECONDS and
            value.timestamp() <= upper.timestamp() + _TIMESTAMP_SLOP_SECONDS)


def _cross_checks(*, receipt: dict[str, Any], request_model: str,
                  request_effort: str, request_workdir: Path, thread_id: str,
                  thread_time: datetime | None, row: dict[str, Any],
                  session: dict[str, Any], turn: dict[str, Any],
                  cli_version: str, launch_start: datetime,
                  launch_end: datetime, binding_start: datetime,
                  binding_end: datetime, recorded_at: datetime) -> list[str]:
    verification = receipt["runtime_session_receipt"]["verification"]
    normalized_row_model = row["model"].strip() if isinstance(row["model"], str) else None
    normalized_turn_model = turn["model"].strip() if isinstance(turn["model"], str) else None
    verification["model_matches"] = request_model == normalized_row_model == normalized_turn_model

    row_effort = row["reasoning_effort"] if isinstance(row["reasoning_effort"], str) else None
    turn_effort = turn["effort"] if isinstance(turn["effort"], str) else None
    verification["reasoning_effort_matches"] = request_effort == row_effort == turn_effort

    provider = row["model_provider"].strip() if isinstance(row["model_provider"], str) else ""
    rollout_providers = [value.strip() for value in
                         (session.get("model_provider"), turn.get("model_provider"))
                         if isinstance(value, str) and value.strip()]
    verification["provider_matches"] = bool(provider) and all(
        value == provider for value in rollout_providers)

    verification["cli_version_matches"] = (
        cli_version == row["cli_version"] == session["cli_version"])
    expected_cwd = str(request_workdir)
    verification["workdir_matches"] = all(value == expected_cwd for value in (
        _canonical_existing_cwd(row["cwd"]),
        _canonical_existing_cwd(session["cwd"]),
        _canonical_existing_cwd(turn["cwd"]),
    ))
    verification["source_matches"] = row["source"] == session["source"] == "exec"
    verification["sandbox_matches"] = _sandbox_is_read_only(turn["sandbox_policy"])
    turn_session_id = turn.get("session_id")
    verification["session_id_matches"] = (
        row["id"] == session["id"] == thread_id and
        (turn_session_id is None or turn_session_id == thread_id))

    try:
        row_created = _parse_timestamp(row["created_at"])
        row_updated = _parse_timestamp(row["updated_at"])
        session_time = session["_event_time"]
        turn_time = turn["_event_time"]
        ordered = (
            launch_start <= launch_end <= binding_start <= binding_end <= recorded_at and
            row_created <= row_updated and session_time <= turn_time and
            all(_within(value, launch_start, launch_end) for value in
                (row_created, row_updated, session_time, turn_time)) and
            (thread_time is None or _within(thread_time, launch_start, launch_end))
        )
    except (TypeError, _ProbeFailure):
        ordered = False
    verification["timestamp_order_valid"] = ordered

    mapping = (
        ("model_matches", "model_mismatch"),
        ("reasoning_effort_matches", "reasoning_effort_mismatch"),
        ("provider_matches", "provider_mismatch"),
        ("cli_version_matches", "cli_version_mismatch"),
        ("workdir_matches", "workdir_mismatch"),
        ("source_matches", "source_mismatch"),
        ("sandbox_matches", "sandbox_mismatch"),
        ("session_id_matches", "session_id_mismatch"),
        ("timestamp_order_valid", "timestamp_invalid"),
    )
    return [code for field, code in mapping if not verification[field]]


def _write_exclusive(path: Path, receipt: dict[str, Any]) -> None:
    payload = json.dumps(receipt, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
    except OSError:
        raise _ProbeFailure("receipt_write_failed") from None


def _privacy_invariant(receipt: dict[str, Any], *, state_db: Path,
                       receipt_path: Path, rollout_path: Path | None) -> bool:
    body = receipt["runtime_session_receipt"]
    forbidden_keys = {"environment", "env", "raw_stdout", "raw_stderr",
                      "prompt", "base_instructions", "credentials", "token"}

    def keys(value: Any) -> Iterable[str]:
        if isinstance(value, dict):
            for key, child in value.items():
                yield str(key)
                yield from keys(child)
        elif isinstance(value, list):
            for child in value:
                yield from keys(child)

    if forbidden_keys.intersection(keys(body)):
        return False
    serialized = json.dumps(body, sort_keys=True, ensure_ascii=False)
    forbidden_values = [str(state_db), str(receipt_path)]
    if rollout_path is not None:
        forbidden_values.append(str(rollout_path))
    return all(value not in serialized for value in forbidden_values)


def probe_codex_session(*, cfg: config_module.Config, codex_bin: str,
                        state_db: str, workdir: str, model: str, effort: str,
                        policy: str, role: str, task_id: str, receipt: str,
                        independent_session: bool, timeout_seconds: int = 300,
                        process_runner: Callable[..., subprocess.CompletedProcess[Any]] = subprocess.run,
                        bindings_runner: Callable[..., subprocess.CompletedProcess[Any]] | None = None,
                        clock: Callable[[], datetime] = _now) -> dict[str, Any]:
    """Run one immutable, exact-session probe and return its written receipt.

    ``process_runner``, ``bindings_runner``, and ``clock`` exist so tests can be
    fixture-only. Production callers should not supply them.
    """
    target = _receipt_target(receipt)  # must happen before any subprocess
    bindings_runner = process_runner if bindings_runner is None else bindings_runner
    model = model.strip() if isinstance(model, str) else ""
    role = role.strip() if isinstance(role, str) else ""
    task_id = task_id.strip() if isinstance(task_id, str) else ""
    policy = policy.strip() if isinstance(policy, str) else ""
    effort = effort.strip() if isinstance(effort, str) else ""
    canonical_policy: str | None = None
    canonical_workdir: Path | None = None
    canonical_state_db: Path | None = None
    rollout_path: Path | None = None
    result = _empty_receipt(task_id=task_id, role=role,
                            independent=bool(independent_session), policy=policy,
                            canonical_policy=None, model=model, effort=effort,
                            workdir=None, cfg=cfg)
    body = result["runtime_session_receipt"]

    try:
        if (not independent_session or not model or not role or not task_id or
                not policy or effort not in cfg.effort_order or
                not isinstance(timeout_seconds, int) or timeout_seconds <= 0):
            raise _ProbeFailure("invalid_argument")
        try:
            # ``--model`` is an executable selector passed to the native CLI,
            # so reject it before even the harmless-looking version subprocess:
            # a caller-supplied Bedrock model must never reach ``codex exec``.
            cfg.assert_inference_target_allowed(
                model, context="Codex session probe requested model")
        except config_module.ConfigError:
            raise _ProbeFailure("forbidden_inference_target") from None
        try:
            canonical_policy = cfg.canonical_policy(policy)
        except config_module.ConfigError:
            raise _ProbeFailure("invalid_argument") from None
        canonical_workdir = _existing_path(workdir, kind="dir")
        canonical_state_db = _existing_path(state_db, kind="file")
        binary = _existing_path(codex_bin, kind="file")
        if not os.access(binary, os.X_OK):
            raise _ProbeFailure("invalid_argument")
        body["requested"]["canonical_policy"] = canonical_policy
        body["requested"]["workdir"] = str(canonical_workdir)
        body["runtime"]["codex_binary_sha256"] = _sha256_file(binary)
        body["launch"]["state_db_path_sha256"] = _path_sha256(canonical_state_db)
        body["launch"]["receipt_path_sha256"] = _path_sha256(target)

        version_argv = [str(binary), "--version"]
        version_start = clock()
        try:
            version_process = _run(version_argv, cwd=canonical_workdir,
                                   timeout=timeout_seconds, runner=process_runner)
        except (subprocess.TimeoutExpired, OSError):
            raise _ProbeFailure("codex_version_failed") from None
        version_end = clock()
        body["version_check"] = _process_record(
            version_argv, version_start, version_end, version_process)
        if version_process.returncode != 0:
            raise _ProbeFailure("codex_version_failed")
        cli_version = _parse_version(_bytes(version_process.stdout),
                                     _bytes(version_process.stderr))
        body["runtime"]["cli_version"] = cli_version

        launch_argv = [
            str(binary), "exec", "--json", "--sandbox", "read-only", "--cd",
            str(canonical_workdir), "--model", model, "--config",
            f"model_reasoning_effort={effort}", PROBE_PROMPT,
        ]
        body["launch"]["safe_argv"] = list(launch_argv)
        body["launch"]["command_sha256"] = _argv_sha256(launch_argv)
        launch_start = clock()
        body["launch"]["started_at"] = _iso(launch_start)
        try:
            process = _run(launch_argv, cwd=canonical_workdir,
                           timeout=timeout_seconds, runner=process_runner)
        except subprocess.TimeoutExpired as exc:
            body["launch"]["stdout_bytes"] = len(_bytes(exc.stdout))
            body["launch"]["stderr_bytes"] = len(_bytes(exc.stderr))
            body["launch"]["stdout_sha256"] = _sha256_bytes(_bytes(exc.stdout))
            body["launch"]["stderr_sha256"] = _sha256_bytes(_bytes(exc.stderr))
            body["launch"]["ended_at"] = _iso(clock())
            raise _ProbeFailure("launch_timeout") from None
        except OSError:
            body["launch"]["ended_at"] = _iso(clock())
            raise _ProbeFailure("launch_nonzero_exit") from None
        launch_end = clock()
        stdout, stderr = _bytes(process.stdout), _bytes(process.stderr)
        body["launch"].update({
            "ended_at": _iso(launch_end),
            "exit_code": int(process.returncode),
            "stdout_bytes": len(stdout), "stderr_bytes": len(stderr),
            "stdout_sha256": _sha256_bytes(stdout),
            "stderr_sha256": _sha256_bytes(stderr),
        })
        if process.returncode != 0:
            raise _ProbeFailure("launch_nonzero_exit")
        thread_id, thread_count, output_matches, thread_time = _parse_launch_stdout(stdout)
        body["launch"]["thread_started_event_count"] = thread_count
        body["launch"]["probe_output_matches"] = output_matches
        if thread_count == 0 or (thread_id is None and thread_count == 1):
            raise _ProbeFailure("thread_id_missing")
        if thread_count != 1:
            raise _ProbeFailure("thread_id_ambiguous")
        assert thread_id is not None
        body["identity"]["independent_session_id"] = thread_id
        if not output_matches:
            raise _ProbeFailure("probe_output_mismatch")

        row = _query_state_row(canonical_state_db, thread_id)
        raw_row_hash = _sha256_bytes(_canonical_json(row))
        rollout_path, rollout_relative = _resolve_rollout(
            canonical_state_db, row["rollout_path"])
        session, session_hash, turn, turn_hash = _parse_rollout(rollout_path)
        public_row = dict(row)
        public_row["rollout_path"] = rollout_relative
        body["observed"].update({
            "state_row_allowlist": public_row,
            "state_row_sha256": raw_row_hash,
            "session_meta_sha256": session_hash,
            "turn_context_sha256": turn_hash,
            "rollout_relative_path": rollout_relative,
            "rollout_path_sha256": _path_sha256(rollout_path),
        })
        provider = row["model_provider"].strip() if isinstance(row["model_provider"], str) else ""
        body["runtime"]["provider"] = provider or None
        try:
            # A native Codex session cannot establish its provider without
            # observing the session metadata after launch.  It must therefore
            # never turn a consistently reported forbidden provider or model
            # into a verified runtime receipt.
            cfg.assert_inference_target_allowed(
                row.get("model"), row.get("model_provider"),
                session.get("model"), session.get("model_provider"),
                turn.get("model"), turn.get("model_provider"),
                context="observed Codex runtime target")
        except config_module.ConfigError:
            raise _ProbeFailure("forbidden_inference_target") from None
        # Preserve the runtime-bindings gate: all request/state/rollout checks
        # must fail closed before invoking the checker.  These placeholder
        # values consume no clock reading and are only a preliminary metadata
        # check; the exact persisted final timestamp is checked below using the
        # real binding interval.
        failures = _cross_checks(
            receipt=result, request_model=model, request_effort=effort,
            request_workdir=canonical_workdir, thread_id=thread_id,
            thread_time=thread_time, row=row, session=session, turn=turn,
            cli_version=cli_version, launch_start=launch_start,
            launch_end=launch_end, binding_start=launch_end,
            binding_end=launch_end, recorded_at=launch_end)
        if failures:
            raise _ProbeFailure(*failures)
        binding_argv = ["python3", "tools/check_runtime_bindings.py"]
        binding_start = clock()
        try:
            binding_process = _run(binding_argv, cwd=config_module.REPO_ROOT,
                                   timeout=timeout_seconds, runner=bindings_runner)
        except (subprocess.TimeoutExpired, OSError):
            raise _ProbeFailure("runtime_bindings_check_failed") from None
        binding_end = clock()
        body["verification"]["runtime_bindings_check"] = _process_record(
            binding_argv, binding_start, binding_end, binding_process)
        if binding_process.returncode != 0:
            raise _ProbeFailure("runtime_bindings_check_failed")
        # This is the receipt's final timestamp.  Validate precisely this
        # value after every subprocess has finished, and do not mutate it
        # after the timestamp-order check succeeds.
        recorded_at = clock()
        body["identity"]["recorded_at"] = _iso(recorded_at)
        failures = _cross_checks(
            receipt=result, request_model=model, request_effort=effort,
            request_workdir=canonical_workdir, thread_id=thread_id,
            thread_time=thread_time, row=row, session=session, turn=turn,
            cli_version=cli_version, launch_start=launch_start,
            launch_end=launch_end, binding_start=binding_start,
            binding_end=binding_end, recorded_at=recorded_at)
        if failures:
            raise _ProbeFailure(*failures)
        body["verification"].update({
            "status": "verified",
            "runtime_resolution_verified": True,
            "failures": [],
        })
        if not _privacy_invariant(result, state_db=canonical_state_db,
                                  receipt_path=target, rollout_path=rollout_path):
            raise _ProbeFailure("privacy_invariant_failed")
        _write_exclusive(target, result)
        return result
    except _ProbeFailure as failure:
        body["verification"]["status"] = "failed"
        body["verification"]["runtime_resolution_verified"] = False
        body["verification"]["failures"] = list(failure.codes)
        if body["identity"]["recorded_at"] is None:
            body["identity"]["recorded_at"] = _iso(clock())
        # Failed receipts never make an affirmative timestamp-order claim.
        # Do this after preserving or assigning the exact persisted timestamp:
        # an earlier preliminary metadata check may have set it true.
        body["verification"]["timestamp_order_valid"] = False
        state_for_privacy = canonical_state_db or Path(state_db).expanduser()
        if not _privacy_invariant(result, state_db=state_for_privacy,
                                  receipt_path=target, rollout_path=rollout_path):
            body["verification"]["failures"] = ["privacy_invariant_failed"]
        try:
            _write_exclusive(target, result)
        except _ProbeFailure as write_failure:
            raise CodexRuntimeProbeError(write_failure.codes, receipt=target,
                                         receipt_written=False) from None
        raise CodexRuntimeProbeError(body["verification"]["failures"],
                                     receipt=target, receipt_written=True) from None
