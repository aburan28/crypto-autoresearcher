"""scripts/relay.py: Claude Code <-> Codex handoff when a budget runs out."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

RELAY = Path(__file__).resolve().parents[1] / "scripts" / "relay.py"


def sh(cwd, *args, **kw):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, check=True, **kw)


def relay(cwd, *args, stdin="", env=None):
    full = {**os.environ, "RELAY_RUNTIME": "", **(env or {})}
    full.pop("CLAUDE_PROJECT_DIR", None)
    full.pop("CLAUDECODE", None)
    return subprocess.run([sys.executable, str(RELAY), *args], cwd=cwd, input=stdin,
                          capture_output=True, text=True, env=full, check=False)


@pytest.fixture
def repo(tmp_path):
    r = tmp_path / "work"
    r.mkdir()
    sh(r, "git", "init", "-q", "-b", "feature/x")
    sh(r, "git", "config", "user.email", "t@example.com")
    sh(r, "git", "config", "user.name", "t")
    (r / ".gitignore").write_text(".resume/\n")
    (r / "a.txt").write_text("one\n")
    sh(r, "git", "add", ".")
    sh(r, "git", "commit", "-qm", "first commit")
    (r / "a.txt").write_text("two\n")
    return r


def claude_transcript(path: Path) -> Path:
    rows = [
        {"type": "user", "message": {"role": "user", "content": "Measure rho on curve C17 with seed 7"}},
        {"type": "assistant", "message": {"role": "assistant", "content": [
            {"type": "text", "text": "Starting the sweep."},
            {"type": "tool_use", "name": "Bash", "input": {"command": "make sweep CURVE=C17 token=abcdefghijklmnop"}},
        ]}},
        {"type": "user", "message": {"role": "user", "content": [{"type": "tool_result", "content": "ok"}]}},
        {"type": "assistant", "message": {"role": "assistant", "content": [{"type": "text", "text": "Sweep half done."}]}},
    ]
    path.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    return path


def test_claude_turn_snapshot_then_budget_failure(repo, tmp_path):
    t = claude_transcript(tmp_path / ".claude-projects.jsonl")
    hook = {"hook_event_name": "Stop", "session_id": "s1", "transcript_path": str(t), "cwd": str(repo)}
    assert relay(repo, "--runtime", "claude", "snapshot", stdin=json.dumps(hook)).returncode == 0
    h = json.loads((repo / ".resume/handoff.json").read_text())
    assert h["status"] == "draft" and h["from"] == "claude"
    assert h["transcript"]["last_user"].startswith("Measure rho on curve C17")
    assert h["transcript"]["last_assistant"] == "Sweep half done."
    assert "abcdefghijklmnop" not in json.dumps(h)  # redacted
    assert any("a.txt" in d for d in h["git"]["dirty"])

    fail = {**hook, "hook_event_name": "StopFailure", "error": "rate_limit", "error_details": "5-hour limit"}
    assert relay(repo, "--runtime", "claude", "snapshot", stdin=json.dumps(fail)).returncode == 0
    h = json.loads((repo / ".resume/handoff.json").read_text())
    assert h["status"] == "pending" and h["to"] == "codex" and h["reason"] == "budget: rate_limit"
    md = (repo / ".resume/HANDOFF.md").read_text()
    assert "Takeover checklist" in md and "feature/x" in md
    hops = (repo / ".resume/relay.jsonl").read_text().splitlines()
    assert json.loads(hops[-1])["to"] == "codex"


def test_non_budget_api_error_stays_draft(repo):
    hook = {"hook_event_name": "StopFailure", "error": "server_error", "session_id": "s1", "cwd": str(repo)}
    relay(repo, "--runtime", "claude", "snapshot", stdin=json.dumps(hook))
    assert json.loads((repo / ".resume/handoff.json").read_text())["status"] == "draft"


def test_pending_handoff_survives_other_sessions_turns_and_is_announced(repo):
    relay(repo, "--runtime", "claude", "out", "--to", "codex", "--no-push", "--note", "resume at step 3")
    before = (repo / ".resume/handoff.json").read_text()
    stop = {"hook_event_name": "Stop", "session_id": "codex-1", "cwd": str(repo)}
    relay(repo, "--runtime", "codex", "snapshot", stdin=json.dumps(stop))
    assert (repo / ".resume/handoff.json").read_text() == before

    start = {"hook_event_name": "SessionStart", "session_id": "codex-1", "cwd": str(repo)}
    out = relay(repo, "--runtime", "codex", "session-start", stdin=json.dumps(start)).stdout
    assert "relay.py accept" in out and "HANDOFF.md" in out
    out = relay(repo, "--runtime", "claude", "session-start", stdin=json.dumps(start)).stdout
    assert json.loads(out)["hookSpecificOutput"]["hookEventName"] == "SessionStart"

    acc = relay(repo, "--runtime", "codex", "accept")
    assert acc.returncode == 0 and "resume at step 3" in acc.stdout
    h = json.loads((repo / ".resume/handoff.json").read_text())
    assert h["status"] == "accepted" and h["accepted_by"] == "codex"
    # Once accepted, the new runtime's own turns update the draft again.
    relay(repo, "--runtime", "codex", "snapshot", stdin=json.dumps(stop))
    assert json.loads((repo / ".resume/handoff.json").read_text())["from"] == "codex"


def test_accept_warns_when_head_moved(repo):
    relay(repo, "--runtime", "claude", "out", "--no-push", "--quiet")
    sh(repo, "git", "commit", "-qam", "moved")
    assert "WARNING: HEAD is" in relay(repo, "--runtime", "codex", "accept").stdout


def test_codex_rollout_transcript(repo, tmp_path):
    t = tmp_path / ".codex" / "rollout.jsonl"
    t.parent.mkdir()
    rows = [
        {"type": "response_item", "payload": {"type": "message", "role": "user",
                                               "content": [{"type": "input_text", "text": "Fix the failing test"}]}},
        {"type": "response_item", "payload": {"type": "function_call", "name": "shell",
                                               "arguments": json.dumps({"command": ["bash", "-lc", "pytest -q tests"]})}},
        {"type": "response_item", "payload": {"type": "message", "role": "assistant",
                                               "content": [{"type": "output_text", "text": "Tests pass now."}]}},
    ]
    t.write_text("\n".join(json.dumps(r) for r in rows))
    hook = {"hook_event_name": "Stop", "session_id": "c1", "transcript_path": str(t), "cwd": str(repo)}
    relay(repo, "snapshot", stdin=json.dumps(hook))
    h = json.loads((repo / ".resume/handoff.json").read_text())
    assert h["from"] == "codex"
    assert h["transcript"]["last_user"] == "Fix the failing test"
    assert h["transcript"]["commands"] == ["pytest -q tests"]


def fake_cli(path: Path, body: str) -> Path:
    path.write_text("#!/usr/bin/env bash\n" + textwrap.dedent(body))
    path.chmod(0o755)
    return path


def test_run_fails_over_on_budget_stop(repo, tmp_path):
    seen = tmp_path / "seen.txt"
    claude = fake_cli(tmp_path / "fake-claude", f"""
        echo "claude got: ${{@: -1}}" >> {seen}
        echo "Claude usage limit reached. Your limit will reset at 3pm"
        exit 1
    """)
    codex = fake_cli(tmp_path / "fake-codex", f"""
        echo "codex got: ${{@: -1}}" >> {seen}
        echo done
    """)
    env = {"RELAY_CLAUDE_CMD": str(claude), "RELAY_CODEX_CMD": str(codex)}
    r = relay(repo, "run", "--no-push", "--", "Measure", "rho", env=env)
    assert r.returncode == 0, r.stderr
    log = seen.read_text()
    assert "claude got: Measure rho" in log
    assert "codex got: You are taking over work from a claude session" in log
    assert "Measure rho" in log.split("codex got:")[1]
    hops = [json.loads(l) for l in (repo / ".resume/relay.jsonl").read_text().splitlines()]
    assert hops[-1]["from"] == "claude" and hops[-1]["to"] == "codex"


def test_run_does_not_fail_over_on_ordinary_failure(repo, tmp_path):
    claude = fake_cli(tmp_path / "fake-claude", "echo 'syntax error'; exit 3\n")
    codex = fake_cli(tmp_path / "fake-codex", "echo should-not-run; exit 0\n")
    r = relay(repo, "run", "--no-push", "--", "task",
              env={"RELAY_CLAUDE_CMD": str(claude), "RELAY_CODEX_CMD": str(codex)})
    assert r.returncode == 3 and "should-not-run" not in r.stdout


def test_out_prints_launch_command(repo):
    out = relay(repo, "--runtime", "claude", "out", "--no-push").stdout
    assert "codex -- 'You are taking over work from a claude session" in out


def test_doctor_reports_gaps_in_bare_repo(repo):
    r = relay(repo, "doctor")
    assert r.returncode == 1 and "gap(s)" in r.stdout


def test_this_repo_is_wired():
    root = RELAY.parents[1]
    settings = json.loads((root / ".claude/settings.json").read_text())["hooks"]
    for ev in ("StopFailure", "Stop", "SessionStart"):
        assert "relay.py" in json.dumps(settings[ev])
    codex = json.loads((root / ".codex/hooks.json").read_text())["hooks"]
    for ev in ("Stop", "SessionStart"):
        assert "relay.py" in json.dumps(codex[ev])
    assert "docs/runtime-relay.md" in (root / "AGENTS.md").read_text()
    assert "relay.py accept" in (root / "docs/runtime-relay.md").read_text()


def test_outgoing_sessions_own_stop_keeps_pending(repo):
    hook = {"hook_event_name": "Stop", "session_id": "s1", "cwd": str(repo)}
    relay(repo, "--runtime", "claude", "snapshot", stdin=json.dumps(hook))
    relay(repo, "--runtime", "claude", "out", "--to", "codex", "--no-push", "--quiet", "--note", "keep me")
    relay(repo, "--runtime", "claude", "snapshot", stdin=json.dumps(hook))
    h = json.loads((repo / ".resume/handoff.json").read_text())
    assert h["status"] == "pending" and h["note"] == "keep me" and h["to"] == "codex"


def test_run_stops_when_no_runtime_is_installed(repo, tmp_path):
    env = {"RELAY_CLAUDE_CMD": str(tmp_path / "nope1"), "RELAY_CODEX_CMD": str(tmp_path / "nope2")}
    r = subprocess.run([sys.executable, str(RELAY), "run", "--max-hops", "0", "--cooldown", "0", "--", "t"],
                       cwd=repo, capture_output=True, text=True, timeout=20, check=False,
                       env={**os.environ, **env})
    assert r.returncode == 127 and "no runtime executable" in r.stderr


def test_restore_announcement_exits_zero_without_handoff():
    body = (RELAY.parent / "checkpoint.sh").read_text()
    assert '[ -f "$dest/.resume/HANDOFF.md" ] && echo' not in body


def test_prompt_survives_multi_value_flags(repo, tmp_path):
    # claude -p --allowedTools A B <prompt> would read the prompt as a tool name.
    seen = tmp_path / "argv.txt"
    cli = fake_cli(tmp_path / "fake-claude", f'printf "%s\\n" "$@" > {seen}\n')
    r = relay(repo, "run", "--no-push", "--", "do", "it",
              env={"RELAY_CLAUDE_CMD": f"{cli} -p --allowedTools Read Bash"})
    assert r.returncode == 0, r.stderr
    assert seen.read_text().splitlines()[-2:] == ["--", "do it"]
