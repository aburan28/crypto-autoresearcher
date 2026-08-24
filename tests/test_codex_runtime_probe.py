"""Fixture-only tests for the exact-session Codex runtime probe."""
from __future__ import annotations

import json
import os
import sqlite3
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from orchestration.adapter import config as config_module
from orchestration.adapter import codex_runtime


THREAD_ID = "019fc3a3-5f11-7812-9570-e1b96ac49833"
OTHER_ID = "019fc3a3-5f11-7812-9570-e1b96ac49834"
BASE = datetime(2026, 8, 2, 12, 0, 0, tzinfo=timezone.utc)


class TickClock:
    def __init__(self):
        self.index = 0

    def __call__(self):
        value = BASE + timedelta(seconds=self.index)
        self.index += 1
        return value


class SequenceClock:
    def __init__(self, offsets):
        self.values = [BASE + timedelta(seconds=value) for value in offsets]
        self.index = 0

    def __call__(self):
        value = self.values[self.index]
        self.index += 1
        return value


def _iso(seconds: float) -> str:
    return (BASE + timedelta(seconds=seconds)).isoformat().replace("+00:00", "Z")


def _fake_codex(path: Path, events: list[dict], *, exit_code: int = 0,
                version: str = "0.144.6") -> Path:
    script = """#!/usr/bin/env python3
import json
import sys
if sys.argv[1:] == ["--version"]:
    print("codex-cli " + VERSION)
    raise SystemExit(0)
for event in EVENTS:
    print(json.dumps(event, separators=(",", ":")))
raise SystemExit(EXIT_CODE)
"""
    script = script.replace("VERSION", repr(version), 1)
    script = script.replace("EVENTS", repr(events), 1)
    script = script.replace("EXIT_CODE", repr(exit_code), 1)
    path.write_text(script, encoding="utf-8")
    path.chmod(0o755)
    return path


def _events(thread_ids=(THREAD_ID,), messages=("PROBE_OK",)) -> list[dict]:
    values = [{"type": "thread.started", "thread_id": item}
              for item in thread_ids]
    values.extend({"type": "item.completed", "item": {
        "type": "agent_message", "text": message}} for message in messages)
    return values


def _session(**changes):
    payload = {
        "id": THREAD_ID,
        "cwd": None,
        "source": "exec",
        "cli_version": "0.144.6",
        "model_provider": "openai",
        "base_instructions": "PRIVATE_BASE_INSTRUCTIONS",
    }
    payload.update(changes)
    return {"timestamp": _iso(2.2), "type": "session_meta", "payload": payload}


def _turn(**changes):
    payload = {
        "session_id": THREAD_ID,
        "cwd": None,
        "model": "gpt-5.6-sol",
        "effort": "xhigh",
        "model_provider": "openai",
        "sandbox_policy": {"type": "read-only"},
        "user_instructions": "PRIVATE_PROBE_SIDE_INSTRUCTIONS",
    }
    payload.update(changes)
    return {"timestamp": _iso(2.4), "type": "turn_context", "payload": payload}


def _bindings_ok(argv, **kwargs):
    assert argv == ["python3", "tools/check_runtime_bindings.py"]
    assert kwargs["shell"] is False
    return subprocess.CompletedProcess(argv, 0, b"runtime bindings: OK\n", b"")


def _case(tmp_path: Path, *, exec_events=None, exit_code=0, rows=1,
          row_changes=None, rollout_events=None, rollout_value=None,
          version="0.144.6", workdir_name="repo", bindings_runner=_bindings_ok,
          process_runner=subprocess.run, clock=None):
    cfg = config_module.load()
    workdir = tmp_path / workdir_name
    workdir.mkdir()
    codex_home = tmp_path / "codex-home"
    sessions = codex_home / "sessions"
    sessions.mkdir(parents=True)
    rollout = sessions / "probe.jsonl"
    session = _session(cwd=str(workdir))
    turn = _turn(cwd=str(workdir))
    selected_events = rollout_events if rollout_events is not None else [
        session,
        {"timestamp": _iso(2.3), "type": "unrelated", "payload": {
            "thread_id": OTHER_ID, "token": "TOP_SECRET_TOKEN"}},
        turn,
    ]
    rollout.write_text("".join(json.dumps(item) + "\n" for item in selected_events),
                       encoding="utf-8")
    state_db = codex_home / "state.sqlite"
    connection = sqlite3.connect(state_db)
    connection.execute("""CREATE TABLE threads (
        id TEXT, rollout_path TEXT, cwd TEXT, source TEXT, model TEXT,
        reasoning_effort TEXT, model_provider TEXT, cli_version TEXT,
        created_at TEXT, updated_at TEXT)""")
    row = {
        "id": THREAD_ID,
        "rollout_path": (str(rollout) if rollout_value is None else rollout_value),
        "cwd": str(workdir),
        "source": "exec",
        "model": "gpt-5.6-sol",
        "reasoning_effort": "xhigh",
        "model_provider": "openai",
        "cli_version": "0.144.6",
        "created_at": _iso(2.1),
        "updated_at": _iso(2.6),
    }
    row.update(row_changes or {})
    for _ in range(rows):
        connection.execute(
            "INSERT INTO threads VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            tuple(row[name] for name in codex_runtime.STATE_COLUMNS))
    connection.commit()
    connection.close()
    binary = _fake_codex(tmp_path / "fake codex", exec_events or _events(),
                         exit_code=exit_code, version=version)
    receipt = tmp_path / "receipt.json"
    arguments = dict(
        cfg=cfg, codex_bin=str(binary), state_db=str(state_db),
        workdir=str(workdir), model="gpt-5.6-sol", effort="xhigh",
        policy="review-xhigh", role="validator", task_id="TASK-FIXTURE",
        receipt=str(receipt), independent_session=True, timeout_seconds=10,
        process_runner=process_runner, bindings_runner=bindings_runner,
        clock=TickClock() if clock is None else clock,
    )
    return arguments, receipt, row, session, turn, rollout


def _failed(arguments, receipt, expected):
    with pytest.raises(codex_runtime.CodexRuntimeProbeError) as excinfo:
        codex_runtime.probe_codex_session(**arguments)
    assert expected in excinfo.value.codes
    assert excinfo.value.receipt_written
    body = json.loads(receipt.read_text(encoding="utf-8"))["runtime_session_receipt"]
    assert body["verification"]["status"] == "failed"
    assert body["verification"]["runtime_resolution_verified"] is False
    assert expected in body["verification"]["failures"]
    return body


def test_happy_path_writes_exact_session_receipt(tmp_path):
    arguments, receipt, _, _, _, _ = _case(tmp_path)
    result = codex_runtime.probe_codex_session(**arguments)
    assert result == json.loads(receipt.read_text(encoding="utf-8"))
    body = result["runtime_session_receipt"]
    assert body["schema"] == codex_runtime.SCHEMA
    assert body["identity"]["independent_session_id"] == THREAD_ID
    assert body["identity"]["independent_session"] is True
    assert body["identity"]["recorded_at"] == _iso(6)
    assert body["requested"]["canonical_policy"] == "review-adversarial"
    assert body["runtime"]["provider"] == "openai"
    assert body["runtime"]["cli_version"] == "0.144.6"
    assert body["runtime"]["adapter_version"] == "1.1.0"
    verification = body["verification"]
    assert verification["status"] == "verified"
    assert verification["runtime_resolution_verified"] is True
    assert verification["verification_scope"] == "exact_codex_session_only"
    assert verification["global_backend_verified"] is False
    assert verification["model_bindings_mutated"] is False
    assert not verification["failures"]
    assert all(verification[name] for name in (
        "model_matches", "reasoning_effort_matches", "provider_matches",
        "cli_version_matches", "workdir_matches", "source_matches",
        "sandbox_matches", "session_id_matches", "timestamp_order_valid"))


@pytest.mark.parametrize(("events", "code"), [
    (_events(thread_ids=()), "thread_id_missing"),
    (_events(thread_ids=(THREAD_ID, OTHER_ID)), "thread_id_ambiguous"),
    (_events(messages=()), "probe_output_mismatch"),
    (_events(messages=("PROBE_OK", "EXTRA")), "probe_output_mismatch"),
])
def test_thread_and_probe_output_failures(tmp_path, events, code):
    arguments, receipt, *_ = _case(tmp_path, exec_events=events)
    _failed(arguments, receipt, code)


def test_invalid_plus_valid_thread_events_are_ambiguous_before_state_lookup(tmp_path, monkeypatch):
    invalid_id = "not-a-uuid"
    arguments, receipt, *_ = _case(
        tmp_path, exec_events=_events(thread_ids=(invalid_id, THREAD_ID)))

    def forbidden_state_lookup(*args, **kwargs):
        raise AssertionError("state lookup must not run for ambiguous stream")

    monkeypatch.setattr(codex_runtime, "_query_state_row", forbidden_state_lookup)
    body = _failed(arguments, receipt, "thread_id_ambiguous")
    assert body["launch"]["thread_started_event_count"] == 2
    assert body["identity"]["independent_session_id"] is None


def test_single_malformed_thread_id_fails_before_state_lookup(tmp_path, monkeypatch):
    arguments, receipt, *_ = _case(
        tmp_path, exec_events=_events(thread_ids=("not-a-uuid",)))

    def forbidden_state_lookup(*args, **kwargs):
        raise AssertionError("state lookup must not run for malformed ID")

    monkeypatch.setattr(codex_runtime, "_query_state_row", forbidden_state_lookup)
    body = _failed(arguments, receipt, "thread_id_missing")
    assert body["launch"]["thread_started_event_count"] == 1


def test_two_valid_thread_events_remain_ambiguous(tmp_path):
    arguments, receipt, *_ = _case(
        tmp_path, exec_events=_events(thread_ids=(THREAD_ID, OTHER_ID)))
    body = _failed(arguments, receipt, "thread_id_ambiguous")
    assert body["launch"]["thread_started_event_count"] == 2


def test_nonzero_launch_is_preserved_as_failed_receipt(tmp_path):
    arguments, receipt, *_ = _case(tmp_path, exit_code=7)
    body = _failed(arguments, receipt, "launch_nonzero_exit")
    assert body["launch"]["exit_code"] == 7
    assert body["launch"]["stdout_sha256"].startswith("sha256:")


def test_unparseable_codex_version_fails_before_session_launch(tmp_path):
    arguments, receipt, *_ = _case(tmp_path, version="not-a-version")
    body = _failed(arguments, receipt, "codex_version_failed")
    assert body["launch"]["started_at"] is None
    assert body["version_check"]["stdout_sha256"].startswith("sha256:")


def test_launch_timeout_is_preserved_without_raw_output(tmp_path):
    def timeout_runner(argv, **kwargs):
        if len(argv) > 1 and argv[1] == "exec":
            raise subprocess.TimeoutExpired(argv, kwargs["timeout"],
                                            output=b"PRIVATE STDOUT",
                                            stderr=b"PRIVATE STDERR")
        return subprocess.run(argv, **kwargs)

    arguments, receipt, *_ = _case(tmp_path, process_runner=timeout_runner)
    body = _failed(arguments, receipt, "launch_timeout")
    serialized = json.dumps(body)
    assert "PRIVATE STDOUT" not in serialized and "PRIVATE STDERR" not in serialized


@pytest.mark.parametrize(("rows", "code"), [
    (0, "state_row_missing"),
    (2, "state_row_ambiguous"),
])
def test_state_row_cardinality_is_exact(tmp_path, rows, code):
    arguments, receipt, *_ = _case(tmp_path, rows=rows)
    _failed(arguments, receipt, code)


@pytest.mark.parametrize(("kind", "code"), [
    ("session_missing", "session_meta_missing"),
    ("session_duplicate", "session_meta_ambiguous"),
    ("turn_missing", "turn_context_missing"),
    ("turn_duplicate", "turn_context_ambiguous"),
    ("session_malformed", "metadata_schema_unsupported"),
    ("turn_malformed", "metadata_schema_unsupported"),
])
def test_rollout_event_cardinality_and_schema(tmp_path, kind, code):
    workdir = tmp_path / "repo"
    session = _session(cwd=str(workdir))
    turn = _turn(cwd=str(workdir))
    cases = {
        "session_missing": [turn],
        "session_duplicate": [session, session, turn],
        "turn_missing": [session],
        "turn_duplicate": [session, turn, turn],
        "session_malformed": [{"type": "session_meta", "payload": []}, turn],
        "turn_malformed": [session, {"type": "turn_context", "payload": []}],
    }
    arguments, receipt, *_ = _case(tmp_path, rollout_events=cases[kind])
    _failed(arguments, receipt, code)


@pytest.mark.parametrize(("location", "field", "value", "code"), [
    ("row", "model", "other-model", "model_mismatch"),
    ("turn", "model", "other-model", "model_mismatch"),
    ("row", "reasoning_effort", "high", "reasoning_effort_mismatch"),
    ("turn", "effort", "high", "reasoning_effort_mismatch"),
    ("session", "model_provider", "other", "provider_mismatch"),
    ("row", "cli_version", "0.144.5", "cli_version_mismatch"),
    ("session", "cli_version", "0.144.5", "cli_version_mismatch"),
    ("row", "source", "other", "source_mismatch"),
    ("session", "source", "other", "source_mismatch"),
    ("turn", "sandbox_policy", {"type": "workspace-write"}, "sandbox_mismatch"),
    ("session", "id", OTHER_ID, "session_id_mismatch"),
    ("turn", "session_id", OTHER_ID, "session_id_mismatch"),
    ("row", "created_at", "2040-01-01T00:00:00Z", "timestamp_invalid"),
])
def test_each_runtime_cross_check_fails_closed(tmp_path, location, field, value, code):
    workdir = tmp_path / "repo"
    row_changes = {field: value} if location == "row" else None
    session = _session(cwd=str(workdir), **({field: value} if location == "session" else {}))
    turn = _turn(cwd=str(workdir), **({field: value} if location == "turn" else {}))
    arguments, receipt, *_ = _case(
        tmp_path, row_changes=row_changes, rollout_events=[session, turn])
    _failed(arguments, receipt, code)


def test_metadata_mismatch_prevents_runtime_bindings_check(tmp_path):
    calls = []

    def forbidden_bindings_runner(*args, **kwargs):
        calls.append((args, kwargs))
        raise AssertionError("metadata mismatch must prevent bindings check")

    arguments, receipt, *_ = _case(
        tmp_path, row_changes={"model": "other-model"},
        bindings_runner=forbidden_bindings_runner)
    _failed(arguments, receipt, "model_mismatch")
    assert calls == []


def test_prebinding_model_mismatch_backward_failure_clock_fails_timestamp_order(tmp_path):
    calls = []

    def forbidden_bindings_runner(*args, **kwargs):
        calls.append((args, kwargs))
        raise AssertionError("metadata mismatch must prevent bindings check")

    clock = SequenceClock((0, 1, 2, 3, 1))
    arguments, receipt, *_ = _case(
        tmp_path, row_changes={"model": "other-model"},
        bindings_runner=forbidden_bindings_runner, clock=clock)
    body = _failed(arguments, receipt, "model_mismatch")
    assert body["identity"]["recorded_at"] == _iso(1)
    assert body["verification"]["timestamp_order_valid"] is False
    assert calls == []


def test_workdir_mismatch_requires_canonical_existing_path(tmp_path):
    other = tmp_path / "other"
    other.mkdir()
    arguments, receipt, *_ = _case(tmp_path, row_changes={"cwd": str(other)})
    _failed(arguments, receipt, "workdir_mismatch")


def test_rollout_traversal_is_rejected(tmp_path):
    arguments, receipt, *_ = _case(
        tmp_path, rollout_value="sessions/../sessions/probe.jsonl")
    _failed(arguments, receipt, "rollout_path_invalid")


def test_missing_rollout_is_distinct(tmp_path):
    arguments, receipt, *_ = _case(tmp_path, rollout_value="sessions/missing.jsonl")
    _failed(arguments, receipt, "rollout_missing")


def test_rollout_symlink_escape_is_rejected(tmp_path):
    arguments, receipt, _, _, _, rollout = _case(tmp_path)
    outside = tmp_path / "outside.jsonl"
    outside.write_text(rollout.read_text(encoding="utf-8"), encoding="utf-8")
    escape = rollout.parent.parent / "escape.jsonl"
    escape.symlink_to(outside)
    state_db = Path(arguments["state_db"])
    connection = sqlite3.connect(state_db)
    connection.execute("UPDATE threads SET rollout_path = ?", (str(escape),))
    connection.commit()
    connection.close()
    _failed(arguments, receipt, "rollout_path_invalid")


def test_malformed_rollout_json_is_unsupported_metadata(tmp_path):
    arguments, receipt, _, _, _, rollout = _case(tmp_path)
    rollout.write_text("{not-json}\n", encoding="utf-8")
    _failed(arguments, receipt, "metadata_schema_unsupported")


def test_existing_receipt_is_refused_before_any_process_launch(tmp_path):
    calls = []

    def forbidden(*args, **kwargs):
        calls.append((args, kwargs))
        raise AssertionError("process must not launch")

    arguments, receipt, *_ = _case(tmp_path, process_runner=forbidden)
    receipt.write_text("original", encoding="utf-8")
    with pytest.raises(codex_runtime.CodexRuntimeProbeError) as excinfo:
        codex_runtime.probe_codex_session(**arguments)
    assert excinfo.value.codes == ("receipt_exists",)
    assert receipt.read_text(encoding="utf-8") == "original"
    assert calls == []


def test_failed_receipt_is_immutable_on_retry(tmp_path):
    arguments, receipt, *_ = _case(tmp_path, exec_events=_events(messages=()))
    _failed(arguments, receipt, "probe_output_mismatch")
    original = receipt.read_bytes()
    with pytest.raises(codex_runtime.CodexRuntimeProbeError) as excinfo:
        codex_runtime.probe_codex_session(**arguments)
    assert excinfo.value.codes == ("receipt_exists",)
    assert receipt.read_bytes() == original


def test_runtime_binding_failure_prevents_verification(tmp_path):
    def bindings_fail(argv, **kwargs):
        return subprocess.CompletedProcess(argv, 1, b"", b"fixture failure")

    arguments, receipt, *_ = _case(tmp_path, bindings_runner=bindings_fail)
    body = _failed(arguments, receipt, "runtime_bindings_check_failed")
    check = body["verification"]["runtime_bindings_check"]
    assert check["exit_code"] == 1
    assert "fixture failure" not in json.dumps(body)


def test_runtime_bindings_nonzero_backward_failure_clock_fails_timestamp_order(tmp_path):
    def bindings_fail(argv, **kwargs):
        return subprocess.CompletedProcess(argv, 1, b"", b"fixture failure")

    clock = SequenceClock((0, 1, 2, 3, 4, 5, 1))
    arguments, receipt, *_ = _case(
        tmp_path, bindings_runner=bindings_fail, clock=clock)
    body = _failed(arguments, receipt, "runtime_bindings_check_failed")
    assert body["identity"]["recorded_at"] == _iso(1)
    assert body["verification"]["timestamp_order_valid"] is False


def test_final_timestamp_before_launch_fails_timestamp_invalid(tmp_path):
    clock = SequenceClock((0, 1, 2, 3, 4, 5, 1))
    arguments, receipt, *_ = _case(tmp_path, clock=clock)
    body = _failed(arguments, receipt, "timestamp_invalid")
    assert body["identity"]["recorded_at"] == _iso(1)
    assert body["verification"]["timestamp_order_valid"] is False


def test_reversed_binding_interval_fails_timestamp_invalid(tmp_path):
    clock = SequenceClock((0, 1, 2, 3, 5, 4, 6))
    arguments, receipt, *_ = _case(tmp_path, clock=clock)
    body = _failed(arguments, receipt, "timestamp_invalid")
    assert body["identity"]["recorded_at"] == _iso(6)
    assert body["verification"]["timestamp_order_valid"] is False


def test_receipt_privacy_and_hash_only_retention(tmp_path):
    arguments, receipt, _, _, _, rollout = _case(tmp_path)
    body = codex_runtime.probe_codex_session(**arguments)["runtime_session_receipt"]
    serialized = json.dumps(body)
    assert "PRIVATE_BASE_INSTRUCTIONS" not in serialized
    assert "PRIVATE_PROBE_SIDE_INSTRUCTIONS" not in serialized
    assert "TOP_SECRET_TOKEN" not in serialized
    assert OTHER_ID not in serialized
    assert str(Path(arguments["state_db"]).resolve()) not in serialized
    assert str(receipt.resolve()) not in serialized
    assert str(rollout.resolve()) not in serialized
    assert body["observed"]["rollout_relative_path"] == "sessions/probe.jsonl"
    assert body["observed"]["session_meta_sha256"].startswith("sha256:")
    assert body["observed"]["turn_context_sha256"].startswith("sha256:")


def test_sqlite_is_query_only_and_never_enumerates_threads(tmp_path, monkeypatch):
    arguments, _, *_ = _case(tmp_path)
    statements = []
    connect_calls = []
    real_connect = sqlite3.connect

    def traced_connect(*args, **kwargs):
        connect_calls.append((args, kwargs))
        connection = real_connect(*args, **kwargs)
        connection.set_trace_callback(statements.append)
        return connection

    monkeypatch.setattr(codex_runtime.sqlite3, "connect", traced_connect)
    codex_runtime.probe_codex_session(**arguments)
    assert connect_calls[0][0][0].startswith("file:")
    assert connect_calls[0][0][0].endswith("?mode=ro")
    assert connect_calls[0][1]["uri"] is True
    normalized = [" ".join(item.split()) for item in statements]
    selects = [item for item in normalized if item.upper().startswith("SELECT")]
    assert len(selects) == 1
    assert "WHERE id =" in selects[0] and THREAD_ID in selects[0]
    assert any(item.upper().startswith("PRAGMA QUERY_ONLY=ON") for item in normalized)
    assert not any(word in " ".join(normalized).upper()
                   for word in ("INSERT ", "UPDATE ", "DELETE ", "VACUUM"))


def test_argv_is_a_list_with_shell_false_for_metacharacter_paths(tmp_path):
    calls = []

    def recording_runner(argv, **kwargs):
        calls.append((list(argv), dict(kwargs)))
        return subprocess.run(argv, **kwargs)

    arguments, receipt, *_ = _case(
        tmp_path, workdir_name="repo with spaces ; $(touch NOPE)",
        process_runner=recording_runner)
    body = codex_runtime.probe_codex_session(**arguments)["runtime_session_receipt"]
    assert calls and all(call[1]["shell"] is False for call in calls)
    assert all(isinstance(call[0], list) for call in calls)
    assert str(Path(arguments["workdir"]).resolve()) in body["launch"]["safe_argv"]
    assert str(Path(arguments["state_db"]).resolve()) not in body["launch"]["safe_argv"]
    assert str(receipt.resolve()) not in body["launch"]["safe_argv"]
    assert not (tmp_path / "NOPE").exists()


def test_probe_does_not_mutate_model_bindings(tmp_path):
    bindings = config_module.BINDINGS_PATH
    before = bindings.read_bytes()
    arguments, *_ = _case(tmp_path)
    codex_runtime.probe_codex_session(**arguments)
    assert bindings.read_bytes() == before


def test_invalid_argument_writes_failed_receipt_without_launch(tmp_path):
    calls = []

    def forbidden(*args, **kwargs):
        calls.append(1)
        raise AssertionError

    arguments, receipt, *_ = _case(tmp_path, process_runner=forbidden)
    arguments["independent_session"] = False
    body = _failed(arguments, receipt, "invalid_argument")
    assert body["identity"]["independent_session"] is False
    assert calls == []


def test_unknown_policy_writes_immutable_invalid_argument_receipt_without_launch(tmp_path):
    calls = []

    def forbidden(*args, **kwargs):
        calls.append((args, kwargs))
        raise AssertionError("no subprocess may launch for unknown policy")

    arguments, receipt, *_ = _case(tmp_path, process_runner=forbidden)
    arguments["policy"] = "unknown-policy"
    body = _failed(arguments, receipt, "invalid_argument")
    original = receipt.read_bytes()
    assert calls == []
    assert body["requested"]["canonical_policy"] is None
    with pytest.raises(codex_runtime.CodexRuntimeProbeError) as excinfo:
        codex_runtime.probe_codex_session(**arguments)
    assert excinfo.value.codes == ("receipt_exists",)
    assert receipt.read_bytes() == original


def test_forbidden_model_writes_refusal_receipt_before_any_subprocess(tmp_path):
    calls = []

    def forbidden(*args, **kwargs):
        calls.append((args, kwargs))
        raise AssertionError("no subprocess may launch for a forbidden model")

    arguments, receipt, *_ = _case(tmp_path, process_runner=forbidden)
    arguments["model"] = "amazon-BeDrOcK/us.example-model"
    body = _failed(arguments, receipt, "forbidden_inference_target")
    assert calls == []
    assert body["version_check"] is None
    assert body["launch"]["started_at"] is None


def test_model_must_match_policy_binding_before_any_subprocess(tmp_path):
    calls = []

    def forbidden(*args, **kwargs):
        calls.append((args, kwargs))
        raise AssertionError("policy mismatch must refuse before subprocess")

    arguments, receipt, *_ = _case(tmp_path, process_runner=forbidden)
    arguments.update({
        "policy": "coordinator-orchestration-code",
        "role": "coordinator",
        "model": "gpt-5.6-sol",
        "effort": "high",
    })
    body = _failed(arguments, receipt, "model_policy_mismatch")
    assert calls == []
    assert body["version_check"] is None
    assert body["policy_resolution"]["backend"] == "openai"
    assert body["policy_resolution"]["resolved_model_id"] == "gpt-5.6-terra"


def test_provider_display_name_cannot_substitute_for_backend_id(tmp_path):
    provider = "OpenAI"
    arguments, receipt, _, session, turn, rollout = _case(
        tmp_path, row_changes={"model_provider": provider})
    session["payload"]["model_provider"] = provider
    turn["payload"]["model_provider"] = provider
    rollout.write_text(
        "".join(json.dumps(event) + "\n" for event in (session, turn)),
        encoding="utf-8")

    body = _failed(arguments, receipt, "provider_mismatch")
    assert body["policy_resolution"]["backend"] == "openai"
    assert body["runtime"]["provider"] == provider


def test_observed_bedrock_provider_cannot_be_verified(tmp_path):
    provider = "Amazon-BeDrOcK"
    arguments, receipt, _, session, turn, rollout = _case(
        tmp_path, row_changes={"model_provider": provider})
    session["payload"]["model_provider"] = provider
    turn["payload"]["model_provider"] = provider
    rollout.write_text(
        "".join(json.dumps(event) + "\n" for event in (session, turn)),
        encoding="utf-8")

    body = _failed(arguments, receipt, "forbidden_inference_target")
    assert body["runtime"]["provider"] == provider
    assert body["verification"]["status"] == "failed"
    assert body["verification"]["runtime_resolution_verified"] is False


def test_cli_help_states_session_only_scope():
    result = subprocess.run(
        ["python3", "-m", "orchestration.adapter", "probe-codex-session", "--help"],
        cwd=config_module.REPO_ROOT, capture_output=True, text=True, check=False)
    assert result.returncode == 0
    assert "only to that session ID" in result.stdout
    for flag in ("--codex-bin", "--state-db", "--workdir", "--model", "--effort",
                 "--policy", "--role", "--task-id", "--receipt",
                 "--independent-session", "--timeout-seconds", "--backend"):
        assert flag in result.stdout
