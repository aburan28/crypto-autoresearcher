"""measure_context attributes per-call tokens to file groups and reads routes, without calling a model."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
import measure_context as mc  # noqa: E402


def make_repo(tmp_path: Path) -> Path:
    root = tmp_path / "src"
    files = {"CLAUDE.md": "c" * 40, ".claude/skills/run/SKILL.md": "s" * 70,
             ".claude/agents/coordinator.md": "a" * 20, ".claude/settings.json": "{}",
             "experiments/E/runs/R/raw-result.json": "x" * 1000}
    for name, text in files.items():
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        (root / name).write_text(text)
    for args in (["init", "-q"], ["add", "-A"],
                 ["-c", "user.name=t", "-c", "user.email=t@example.invalid", "commit", "-qm", "c"]):
        subprocess.run(["git", "-C", str(root), *args], check=True)
    return root


def fake_usage(args, cwd):
    """Tokens = 1000 floor + one per byte of config the variant directory holds."""
    config = sum(p.stat().st_size for p in Path(cwd).rglob("*")
                 if p.is_file() and ".git" not in p.parts)
    return json.dumps({"usage": {"input_tokens": 3, "cache_creation_input_tokens": 997 + config,
                                 "cache_read_input_tokens": 0}})


def test_context_copies_only_config_and_attributes_each_group(tmp_path):
    rows = mc.attribution(mc.context("HEAD", run=fake_usage, repo=make_repo(tmp_path)))
    assert rows == {"runtime": 1000, "claude_md": 40, "skills": 70, "agents": 20, "all": 132}


def test_input_tokens_counts_cached_and_uncached_and_refuses_empty():
    assert mc.input_tokens(json.dumps({"usage": {"input_tokens": 5, "cache_read_input_tokens": 7}})) == 12
    try:
        mc.input_tokens(json.dumps({"result": "OK"}))
    except ValueError:
        pass
    else:
        raise AssertionError("a result without usage was accepted")


def test_chosen_route_reads_the_first_skill_or_agent_call():
    def event(name, inp):
        return json.dumps({"message": {"content": [{"type": "tool_use", "name": name, "input": inp}]}})
    stream = "\n".join(["not json", event("Read", {"file_path": "x"}),
                        event("Skill", {"skill": "/deep-research RQ-1"}),
                        event("Agent", {"subagent_type": "validator"})])
    assert mc.chosen_route(stream) == "deep-research"
    assert mc.chosen_route(event("Agent", {"subagent_type": "red-team"})) == "red-team"
    assert mc.chosen_route('{"type": "result"}') == "none"


def test_routing_compares_both_refs_on_every_request(tmp_path, monkeypatch):
    monkeypatch.setattr(mc, "ROUTING_REQUESTS", [("run", "run it"), ("coordinate", "rank it")])
    def fake(args, cwd):
        prompt = args[args.index("-p") + 1]
        name = "run" if prompt == "run it" else "none"
        return json.dumps({"message": {"content": [{"type": "tool_use", "name": "Skill",
                                                    "input": {"skill": name}}]}})
    rows = mc.routing("HEAD", "HEAD", runs=1, run=fake, repo=make_repo(tmp_path), workers=1)
    assert sorted((r["arm"], r["expect"], r["ok"]) for r in rows) == [
        ("base", "coordinate", False), ("base", "run", True),
        ("ref", "coordinate", False), ("ref", "run", True)]


def test_nested_session_variables_are_dropped_credentials_kept(monkeypatch):
    monkeypatch.setenv("CLAUDE_CODE_SESSION_ID", "parent")
    monkeypatch.setenv("CCR_SOMETHING", "x")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "kept")
    env = mc.clean_env()
    assert "CLAUDE_CODE_SESSION_ID" not in env and "CCR_SOMETHING" not in env
    assert env["ANTHROPIC_API_KEY"] == "kept"
