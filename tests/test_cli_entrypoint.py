"""Tests for the `autoresearch` entry point.

These guard the things a local user hits first: does `doctor` diagnose rather
than crash, does `loop --dry-run` say what it would cost before spending it,
and does delegation to the sub-CLIs actually pass arguments through.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from orchestration import cli as cli_module

REPO = Path(__file__).resolve().parents[1]


def run(argv, capsys) -> tuple[int, str]:
    code = cli_module.main(argv)
    captured = capsys.readouterr()
    return code, captured.out + captured.err


# --------------------------------------------------------------------------
def test_doctor_reports_without_crashing(capsys):
    code, output = run(["doctor"], capsys)
    assert code in (0, 1)                    # 1 when no credentials are set
    for section in ("environment", "dependencies", "configuration", "backends",
                    "role bindings"):
        assert section in output


def test_doctor_names_an_actionable_next_step_when_blocked(monkeypatch, capsys):
    for name in ("ANTHROPIC_API_KEY", "ZAI_API_KEY", "OPENAI_API_KEY",
                 "OPENROUTER_API_KEY", "LOCAL_LLM_API_KEY"):
        monkeypatch.delenv(name, raising=False)
    code, output = run(["doctor"], capsys)
    assert code == 1
    assert "no backend is usable" in output
    assert "next:" in output
    assert "export" in output


def test_doctor_passes_once_a_backend_is_usable(monkeypatch, capsys):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test")
    code, output = run(["doctor"], capsys)
    assert code == 0
    assert "anthropic: ready" in output
    assert "Ready." in output
    # An unverified model id must still be flagged, not quietly accepted.
    assert "--probe" in output


def test_doctor_detects_a_non_editable_install(monkeypatch, capsys):
    """A wheel in site-packages cannot find AGENTS.md; say so plainly."""
    monkeypatch.setattr(cli_module, "REPO", Path("/nonexistent"))
    code, output = run(["doctor"], capsys)
    assert code == 1
    assert "repository root not found" in output
    assert "pip install -e ." in output


def test_status_reports_configuration_without_running_anything(capsys):
    code, output = run(["status"], capsys)
    assert code == 0
    assert "repository" in output and "backend" in output
    assert "baselines" in output


# --------------------------------------------------------------------------
def test_loop_dry_run_states_the_cost_before_spending_it(capsys):
    code, output = run(["loop", "--dry-run", "--trials", "5"], capsys)
    assert code == 0
    assert "model-driven runs" in output
    assert "nothing executed" in output


def test_loop_dry_run_counts_trials_times_tasks(capsys):
    _, three = run(["loop", "--dry-run", "--trials", "3"], capsys)
    _, six = run(["loop", "--dry-run", "--trials", "6"], capsys)

    def total(text: str) -> int:
        line = next(l for l in text.splitlines() if l.startswith("total"))
        return int(line.split()[1])

    assert total(six) == 2 * total(three)


def test_loop_defaults_to_the_dev_split(capsys):
    _, output = run(["loop", "--dry-run"], capsys)
    assert "split    dev" in output


def test_loop_can_select_the_held_out_split(capsys):
    _, dev = run(["loop", "--dry-run", "--split", "dev"], capsys)
    _, held = run(["loop", "--dry-run", "--split", "held_out"], capsys)
    _, every = run(["loop", "--dry-run", "--split", "all"], capsys)

    def total(text: str) -> int:
        line = next(l for l in text.splitlines() if l.startswith("total"))
        return int(line.split()[1])

    assert total(every) == total(dev) + total(held)
    assert total(held) > 0, "held-out tasks must be reachable"


def test_loop_reports_missing_baselines_rather_than_failing(tmp_path, capsys,
                                                            monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test")
    code, output = run(
        ["loop", "--dry-run", "--baseline-dir", str(tmp_path / "none")], capsys)
    assert code == 0


# --------------------------------------------------------------------------
def test_delegation_passes_arguments_through(capsys):
    code, output = run(
        ["eval", "list", "--suite", "evals/suites/capability.yaml",
         "--split", "held_out"], capsys)
    assert code == 0
    assert "EVAL-CAP-DLOG-16" in output
    assert "EVAL-CAP-DLOG-12" not in output          # dev task, filtered out


def test_delegation_reaches_the_adapter(capsys):
    code, output = run(["adapter", "resolve", "--policy", "research-deep",
                        "--backend", "zai"], capsys)
    assert code == 0
    assert "glm" in output


def test_delegation_propagates_the_exit_code(capsys):
    code, _ = run(["adapter", "resolve", "--policy", "no-such-policy"], capsys)
    assert code == 2


def test_console_scripts_are_declared():
    """Every sub-CLI reachable as an installed command, not just python -m."""
    import tomllib
    manifest = tomllib.loads((REPO / "pyproject.toml").read_text(encoding="utf-8"))
    scripts = manifest["project"]["scripts"]
    assert scripts["autoresearch"] == "orchestration.cli:main"
    for name in ("autoresearch-adapter", "autoresearch-agent", "autoresearch-eval"):
        assert name in scripts
    packaged = set(manifest["tool"]["setuptools"]["packages"])
    assert {"orchestration", "orchestration.eval", "harness"} <= packaged


def test_agent_extra_matches_the_requirements_file():
    """A drifting extra means `pip install -e .[agent]` differs from CI."""
    import tomllib
    manifest = tomllib.loads((REPO / "pyproject.toml").read_text(encoding="utf-8"))
    extra = {line.split(">=")[0].split("<")[0].strip().lower()
             for line in manifest["project"]["optional-dependencies"]["agent"]}
    pinned = {line.split(">=")[0].split("<")[0].strip().lower()
              for line in (REPO / "requirements-agent.txt").read_text().splitlines()
              if line.strip() and not line.startswith("#")}
    assert extra == pinned
