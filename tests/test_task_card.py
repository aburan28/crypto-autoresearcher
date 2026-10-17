"""Mechanical task cards: the director's instructions, checked by a tool.

`tools/task_card.py` exists so the mechanical tier is never relayed an
instruction that leaves it a choice, and so a report it paraphrased is caught
without anyone trusting it. Each lint rule is shown to bite.
"""
from __future__ import annotations

import sys
from copy import deepcopy
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))

import runbook as rb  # noqa: E402
import task_card as tc  # noqa: E402

EXAMPLE = "examples/runbooks/toy-ecdlp-bsgs/task-card.yaml"


def _card() -> dict:
    return yaml.safe_load((REPO / EXAMPLE).read_text(encoding="utf-8"))


def _findings(mutate) -> list[str]:
    card = _card()
    mutate(card)
    return tc.lint(card)


def test_the_example_card_lints_clean():
    assert tc.lint(_card()) == []
    assert tc.main(["lint", EXAMPLE]) == 0


def test_the_example_card_names_the_runbooks_current_bytes():
    runbook = rb.load_runbook(REPO, _card()["runbook"])
    assert _card()["runbook_sha256"] == runbook.sha256


def test_vague_stop_conditions_are_refused():
    findings = _findings(lambda c: c["stop_when"].append("Stop if it seems appropriate."))
    assert any("leaves a choice" in f for f in findings), findings


def test_unfilled_placeholders_are_refused():
    findings = _findings(lambda c: c["stop_when"].append("Step 2 prints <the failure line>."))
    assert any("unfilled placeholder" in f for f in findings), findings


def test_a_stale_runbook_digest_is_refused():
    findings = _findings(lambda c: c.__setitem__("runbook_sha256", "0" * 64))
    assert any("the runbook on disk is" in f for f in findings), findings


def test_a_write_scope_missing_the_session_directory_is_refused():
    findings = _findings(lambda c: c.__setitem__("write_scope", [c["write_scope"][1]]))
    assert any("runbook-sessions/" in f for f in findings), findings


def test_the_roles_are_fixed():
    findings = _findings(lambda c: c.__setitem__("executor_role", "executor"))
    assert any("executor_role" in f for f in findings), findings
    findings = _findings(lambda c: c.__setitem__("author_role", "coordinator"))
    assert any("author_role" in f for f in findings), findings


def test_an_exp_card_needs_a_committed_approval_naming_the_runbook(monkeypatch):
    """A card adds no authority: an EXP-* runbook without an approval fails."""
    card = _card()
    real = rb.load_runbook

    def as_exp(repo, path):
        runbook = real(repo, path)
        runbook.doc["experiment_id"] = "EXP-20991231-zz"
        return runbook

    monkeypatch.setattr(rb, "load_runbook", as_exp)
    monkeypatch.setattr(rb, "lint", lambda runbook: [])
    card["experiment_id"] = "EXP-20991231-zz"
    findings = tc.lint(card)
    assert any("no committed approval decision" in f for f in findings), findings


def test_frozen_command_cards_refuse_shell_and_unbound_files():
    card = _card()
    for key in ("runbook", "runbook_sha256"):
        card.pop(key)
    card["kind"] = "frozen_command"
    card["commands"] = [{"argv": ["python3", "examples/runbooks/toy-ecdlp-bsgs/solve.py", "|", "tee"],
                         "timeout_seconds": 60, "success_exit_codes": [0],
                         "outputs": ["elsewhere/out.json"]}]
    findings = tc.lint(card)
    assert any("shell syntax" in f for f in findings), findings
    assert any("binds does not pin" in f for f in findings), findings
    assert any("outside write_scope" in f for f in findings), findings


def test_the_prompt_is_deterministic_and_carries_every_value():
    path, sha, card = tc.load_card(EXAMPLE)
    first = tc.render_prompt(path, sha, card)
    assert first == tc.render_prompt(path, sha, deepcopy(card))
    for value in (card["runbook"], card["bus_address"], card["card_id"], sha,
                  *card["write_scope"], *card["stop_when"]):
        assert value in first
    assert "<" not in first.replace("<runbook>", "").replace("<your bus address>", "") \
        .replace("<session_dir>", "").replace("<session id>", "")


def test_check_relay_accepts_the_tool_output_and_catches_a_paraphrase(tmp_path):
    card = _card()
    session = rb.load_runbook(REPO, card["runbook"]).session_dir
    verbatim = rb.brief(REPO, session)
    result = tc.check_relay(card, "Here is the output:\n" + verbatim + "\nDone.")
    assert result["relay_verbatim"] and result["verify_findings"] == []

    rounded = verbatim.replace("mean=458.5", "mean=459")
    assert rounded != verbatim
    result = tc.check_relay(card, rounded)
    assert not result["relay_verbatim"]
    assert any("458.5" in line for line in result["missing_lines"])
