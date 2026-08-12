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
    # Name the exact variable and where to put it, not just "credentials".
    assert "ANTHROPIC_API_KEY" in output and ".env" in output


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
    for name in (
        "autoresearch-adapter",
        "autoresearch-agent",
        "autoresearch-eval",
        "autoresearch-campaign-mcp",
    ):
        assert name in scripts
    packaged = set(manifest["tool"]["setuptools"]["packages"])
    assert {
        "orchestration",
        "orchestration.campaign",
        "orchestration.eval",
        "orchestration.knowledge",
        "orchestration.routing",
        "harness",
    } <= packaged


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


# --------------------------------------------------------------------------
# credentials and endpoints
# --------------------------------------------------------------------------
def test_backends_lists_endpoints_and_key_variables(capsys):
    code, output = run(["backends"], capsys)
    assert code == 0
    for backend, url, key in (
            ("anthropic", "https://api.anthropic.com", "ANTHROPIC_API_KEY"),
            ("zai", "https://api.z.ai/api/paas/v4", "ZAI_API_KEY"),
            ("zai-anthropic", "https://api.z.ai/api/anthropic", "ZAI_API_KEY"),
            ("local", "localhost", "LOCAL_LLM_API_KEY")):
        assert backend in output and url in output and key in output
    assert "AUTORESEARCH_BACKEND" in output
    assert ".env.example" in output


def test_backends_distinguishes_missing_key_from_missing_binding(capsys,
                                                                 monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    _, output = run(["backends"], capsys)
    assert "no credentials" in output          # anthropic: bound, no key
    assert "unbound" in output                 # openrouter/local remain unbound


def test_dotenv_is_loaded_without_overriding_the_shell(tmp_path, monkeypatch):
    env = {"ALREADY_SET": "from-shell"}
    (tmp_path / ".env").write_text(
        '# comment\n'
        'ALREADY_SET=from-file\n'
        'ANTHROPIC_API_KEY="quoted-value"\n'
        "ZAI_API_KEY='single'\n"
        'export EXPORTED_FORM=yes\n'
        'BLANK=\n'
        'no_equals_line\n')
    loaded = cli_module.load_dotenv(tmp_path / ".env", env)
    assert env["ALREADY_SET"] == "from-shell"     # the shell always wins
    assert env["ANTHROPIC_API_KEY"] == "quoted-value"
    assert env["ZAI_API_KEY"] == "single"
    assert env["EXPORTED_FORM"] == "yes"
    assert "BLANK" not in env
    assert set(loaded) == {"ANTHROPIC_API_KEY", "ZAI_API_KEY", "EXPORTED_FORM"}


def test_a_missing_dotenv_is_not_an_error(tmp_path):
    assert cli_module.load_dotenv(tmp_path / "absent", {}) == []


def test_env_example_documents_every_backend_variable():
    """A backend whose key variable is undocumented cannot be wired up."""
    import yaml
    example = (REPO / ".env.example").read_text(encoding="utf-8")
    providers = yaml.safe_load(
        (REPO / "orchestration/providers.yaml").read_text(encoding="utf-8"))
    for name, backend in providers["backends"].items():
        assert backend["api_key_env"] in example, f"{name} key var undocumented"
        assert backend["base_url_env"] in example, f"{name} url var undocumented"
        assert str(backend["base_url"]) in example, f"{name} url undocumented"


def test_env_example_is_gitignored():
    """The template is committed; the filled-in file must never be."""
    ignored = (REPO / ".gitignore").read_text(encoding="utf-8").split()
    assert ".env" in ignored
    assert (REPO / ".env.example").is_file()
