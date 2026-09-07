"""Regression tests for token-efficient subagent context construction."""
from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("langgraph", reason="api_direct runtime needs requirements-agent.txt")

from orchestration import role_registry  # noqa: E402
from orchestration.agent import runner as runner_module  # noqa: E402
from orchestration.agent.tools import TaskScope  # noqa: E402

REPO = Path(__file__).resolve().parents[1]


def test_executor_system_prompt_uses_compact_core_not_full_agents():
    roles = role_registry.load_roles()
    prompt = runner_module.system_prompt("executor", roles, repo_root=REPO)
    core = (REPO / "docs/agent-runtime-core.md").read_text()
    executor = (REPO / "agents/executor.md").read_text()
    full = (REPO / "AGENTS.md").read_text()

    assert core in prompt
    assert executor in prompt
    assert len(prompt) == len(core) + len(executor) + len("\n\n---\n\n")
    assert len(prompt) < len(full)
    assert "Goal closure quorum — SUSPENDED" not in prompt


def test_context_paths_are_explicit_and_do_not_scan_state():
    task = {
        "id": "TASK-X",
        "role": "executor",
        "context_paths": [
            "experiments/EXP-X/specification.yaml",
            "ledger/handoffs/TASK-X.yaml",
        ],
        "handoff": {"objective": "run frozen protocol"},
    }
    assert runner_module._context_paths(task) == [
        "experiments/EXP-X/specification.yaml",
        "ledger/handoffs/TASK-X.yaml",
    ]


def test_executor_brief_forbids_full_corpus_scan():
    task = {
        "id": "TASK-X",
        "role": "executor",
        "context_paths": ["experiments/EXP-X/specification.yaml"],
        "handoff": {
            "objective": "execute EXP-X",
            "inputs": ["experiments/EXP-X/specification.yaml"],
            "artifact_paths": ["experiments/EXP-X/execution-report.yaml"],
        },
    }
    scope = TaskScope(
        repo_root=REPO,
        task_id="TASK-X",
        write_scope=("experiments/EXP-X",),
    )
    brief = runner_module.task_brief(task, scope, ["read_file", "run_command"])
    assert "Explicit context files" in brief
    assert "experiments/EXP-X/specification.yaml" in brief
    assert "Do not scan the full ledger, knowledge corpus, or AGENTS.md" in brief
