"""The autopilot's worker drivers: one action, three agent CLIs, one grammar."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from orchestration import adapter
from orchestration.campaign import autopilot, workers


@pytest.fixture(scope="module")
def cfg():
    return adapter.load()


def test_model_reference_follows_each_cli_spelling() -> None:
    assert workers.model_reference("opencode", "local", "m") == "vllm/m"
    assert workers.model_reference("opencode", "fireworks", "m") == "fireworks-ai/m"
    assert workers.model_reference("opencode", "openrouter", "v/m") == "openrouter/v/m"
    assert workers.model_reference("claude_code", "anthropic", "claude-x") == "claude-x"
    assert workers.model_reference("codex_cli", "openrouter", "v/m") == "v/m"
    with pytest.raises(workers.WorkerError):
        workers.model_reference("cursor", "anthropic", "m")


def test_commands_and_extra_args() -> None:
    assert workers.build_command("opencode", "do it", "zai/glm", attach="http://127.0.0.1:1") == [
        "opencode", "run", "--attach", "http://127.0.0.1:1", "--format", "json",
        "--agent", "build", "--model", "zai/glm", "do it"]
    claude = workers.build_command("claude_code", "do it", "claude-x", env={})
    assert claude[:3] == ["claude", "-p", "do it"]
    assert claude[claude.index("--model") + 1] == "claude-x"
    assert "--permission-mode" in claude and "stream-json" in claude
    widened = workers.build_command(
        "claude_code", "p", "m",
        env={"AUTORESEARCH_CLAUDE_ARGS": "--allowedTools 'Bash(git:*)' --permission-mode plan"})
    assert widened[-4:] == ["--allowedTools", "Bash(git:*)", "--permission-mode", "plan"]
    codex = workers.build_command("codex_cli", "do it", "gpt-x", env={})
    assert codex[:5] == ["codex", "exec", "--json", "-m", "gpt-x"]
    assert codex[-1] == "do it" and "--sandbox" in codex
    with pytest.raises(workers.WorkerError):
        workers.build_command("claude_code", "p", "m", attach="http://127.0.0.1:1")


def test_runtime_env_points_proxies_but_leaves_native_auth_alone(cfg) -> None:
    env = {"ZAI_API_KEY": "zk", "ANTHROPIC_API_KEY": "ak", "OPENROUTER_API_KEY": "ork"}
    proxied = workers.runtime_env(cfg, "claude_code", "zai-anthropic", "glm-x", env=env)
    assert proxied["ANTHROPIC_BASE_URL"] == cfg.base_url("zai-anthropic", env)
    assert proxied["ANTHROPIC_AUTH_TOKEN"] == "zk"
    assert proxied["ANTHROPIC_MODEL"] == proxied["ANTHROPIC_SMALL_FAST_MODEL"] == "glm-x"

    native = workers.runtime_env(cfg, "claude_code", "anthropic", "claude-x", env=env)
    assert native["ANTHROPIC_MODEL"] == "claude-x"
    assert "ANTHROPIC_AUTH_TOKEN" not in native and "ANTHROPIC_SMALL_FAST_MODEL" not in native

    codex = workers.runtime_env(cfg, "codex_cli", "openrouter", "v/m", env=env)
    assert codex["OPENAI_BASE_URL"] == cfg.base_url("openrouter", env)
    assert codex["OPENAI_API_KEY"] == "ork" and codex["OPENAI_MODEL"] == "v/m"

    assert workers.runtime_env(cfg, "opencode", "zai", "glm", env=env) == {}
    # No credential in the environment: nothing is exported, nothing invented.
    assert "ANTHROPIC_AUTH_TOKEN" not in workers.runtime_env(
        cfg, "claude_code", "zai-anthropic", "glm", env={})


def test_compatibility_refuses_a_wire_mismatch(cfg) -> None:
    assert workers.check_compatibility(cfg, "claude_code", ["anthropic", "zai-anthropic"])
    with pytest.raises(workers.WorkerError, match="openrouter"):
        workers.check_compatibility(cfg, "claude_code", ["anthropic", "openrouter"])
    with pytest.raises(workers.WorkerError, match="anthropic"):
        workers.check_compatibility(cfg, "opencode", ["anthropic"])
    assert "abliteration" in workers.compatible_backends(cfg, "codex_cli")
    assert "abliteration-anthropic" in workers.compatible_backends(cfg, "claude_code")


def _jsonl(path: Path, rows: list[dict]) -> Path:
    path.write_text("\n".join(json.dumps(r) for r in rows) + "\nnot json\n", encoding="utf-8")
    return path


def test_claude_code_events(tmp_path: Path) -> None:
    quiet = _jsonl(tmp_path / "quiet.jsonl", [
        {"type": "system", "subtype": "init"},
        {"type": "assistant", "message": {"content": [{"type": "text", "text": "hi"}]}},
        {"type": "result", "subtype": "success", "is_error": False,
         "usage": {"input_tokens": 120, "output_tokens": 30}, "total_cost_usd": 0.0123}])
    assert workers.has_tool_events("claude_code", quiet) is False
    assert workers.has_error_events("claude_code", quiet) is False
    assert workers.usage("claude_code", quiet) == {
        "input_tokens": 120, "output_tokens": 30, "cost_usd": 0.0123}
    acted = _jsonl(tmp_path / "acted.jsonl", [
        {"type": "assistant", "message": {"content": [
            {"type": "tool_use", "name": "Bash", "input": {"command": "git status"}}]}},
        {"type": "result", "subtype": "error_during_execution", "is_error": True}])
    assert workers.has_tool_events("claude_code", acted) is True
    assert workers.has_error_events("claude_code", acted) is True
    assert workers.usage("claude_code", acted) == {
        "input_tokens": None, "output_tokens": None, "cost_usd": None}


def test_codex_events(tmp_path: Path) -> None:
    acted = _jsonl(tmp_path / "codex.jsonl", [
        {"type": "thread.started", "thread_id": "t"},
        {"type": "item.completed", "item": {"type": "agent_message", "text": "hi"}},
        {"type": "item.completed", "item": {"type": "command_execution",
                                             "command": "git status"}},
        {"type": "turn.completed", "usage": {"input_tokens": 10, "cached_input_tokens": 4,
                                              "output_tokens": 3}}])
    assert workers.has_tool_events("codex_cli", acted) is True
    assert workers.has_error_events("codex_cli", acted) is False
    # Codex reports no price; the cost stays unknown rather than zero.
    assert workers.usage("codex_cli", acted) == {
        "input_tokens": 10, "output_tokens": 3, "cost_usd": None}
    failed = _jsonl(tmp_path / "failed.jsonl", [{"type": "turn.failed", "error": {}}])
    assert workers.has_error_events("codex_cli", failed) is True
    assert workers.has_tool_events("codex_cli", failed) is False
    assert workers.has_tool_events("codex_cli", tmp_path / "absent.jsonl") is False


def test_invoke_worker_runs_claude_code_with_the_resolved_env(
        tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(autopilot.shutil, "which", lambda name: f"/bin/{name}")
    monkeypatch.setattr(autopilot, "_git_state", lambda _: "same")
    monkeypatch.setattr(autopilot, "candidates", lambda *_: [
        ("zai-anthropic", "glm-x", {"policy": "coordinator-orchestration-code",
                                     "verified_model": False,
                                     "resolved_model_id": "glm-x"})])
    seen = {}

    def run(command, **kwargs):
        seen["command"] = command
        seen["env"] = kwargs["env"]
        kwargs["stdout"].write(json.dumps({"type": "result", "is_error": False,
                                           "usage": {"input_tokens": 5, "output_tokens": 1},
                                           "total_cost_usd": 0.001}) + "\n")
        return subprocess.CompletedProcess(command, 0)

    action = autopilot.Action("design", "IDEA-TEST", "design it", "coordinator")
    result = autopilot.invoke_worker(
        action, tmp_path, tmp_path, backends=["zai-anthropic"], timeout=10,
        runtime="claude_code", run_command=run, env={"ZAI_API_KEY": "zk"})
    assert result["ok"] is True
    assert seen["command"][:3] == ["claude", "-p", "design it"]
    assert seen["env"]["ANTHROPIC_MODEL"] == "glm-x"
    assert seen["env"]["ANTHROPIC_AUTH_TOKEN"] == "zk"
    assert result["attempts"][0]["runtime"] == "claude_code"
    assert result["attempts"][0]["input_tokens"] == 5
    assert result["attempts"][0]["cost_usd"] == 0.001


def test_invoke_worker_reports_a_missing_binary(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(autopilot.shutil, "which", lambda _: None)
    action = autopilot.Action("design", "IDEA-TEST", "design it", "coordinator")
    result = autopilot.invoke_worker(action, tmp_path, tmp_path, backends=["openai"],
                                     timeout=1, runtime="codex_cli")
    assert result == {"ok": False, "reason": "codex CLI unavailable", "attempts": []}
