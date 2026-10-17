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


# ---------------------------------------------------------------------------
# Frozen-command cards: executed by the tool, so they work in every repository
# ---------------------------------------------------------------------------

import subprocess  # noqa: E402

import pytest  # noqa: E402


def test_the_vagueness_list_matches_the_runbook_lint():
    """task_card.py carries its own copy so it runs where runbook.py does not."""
    assert tc.VAGUE.pattern == rb.VAGUE.pattern


def test_a_card_outside_the_repository_is_a_clean_error(tmp_path):
    outside = tmp_path / "card.yaml"
    outside.write_text("schema: x\n")
    with pytest.raises(tc.CardError, match="outside the repository"):
        tc.load_card(outside)
    assert tc.main(["lint", str(outside)]) == 2


def _git_repo(tmp_path):
    repo = tmp_path / "repo"
    (repo / "tools").mkdir(parents=True)
    script = repo / "tools" / "emit.py"
    script.write_text("import sys\nprint('line one')\nprint('value=42')\nsys.exit(int(sys.argv[1]))\n")
    for args in (["init", "-q"], ["config", "user.email", "t@t"], ["config", "user.name", "t"],
                 ["add", "-A"], ["commit", "-q", "-m", "init"]):
        subprocess.run(["git", *args], cwd=repo, check=True)
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True,
                          text=True, check=True).stdout.strip()
    return repo, script, head


def _frozen_card(script, head, codes=(0,), first_exit="0"):
    return {
        "schema": tc.SCHEMA, "card_id": "CARD-EXAMPLE-frozen-01", "experiment_id": "EXAMPLE-frozen",
        "author_role": "experiment-director", "executor_role": "executor-mechanical",
        "kind": "frozen_command", "commit": head, "receipt": "out/receipt.json",
        "binds": [{"path": "tools/emit.py", "sha256": rb.sha256_file(script)}],
        "commands": [
            {"argv": ["python3", "tools/emit.py", first_exit], "timeout_seconds": 30,
             "success_exit_codes": list(codes), "stdout": "out/c1.stdout", "stderr": "out/c1.stderr"},
            {"argv": ["python3", "tools/emit.py", "0"], "timeout_seconds": 30, "success_exit_codes": [0]},
        ],
        "bus_address": "executor-mechanical-test", "background": False,
        "write_scope": ["out/"], "stop_when": ["The run command exits with status 2."],
    }


def test_run_executes_records_and_relays_verbatim(tmp_path):
    repo, script, head = _git_repo(tmp_path)
    card = _frozen_card(script, head)
    assert tc.lint(card, repo) == []
    receipt = tc.run_card("card.yaml", "0" * 64, card, repo)
    assert receipt["status"] == "completed" and receipt["commit"] == head
    assert [c["exit_code"] for c in receipt["commands"]] == [0, 0]
    assert (repo / "out/c1.stdout").read_text() == "line one\nvalue=42\n"
    printed = tc.brief(receipt, "out/receipt.json", rb.sha256_file(repo / "out/receipt.json"))
    assert "value=42" in printed

    relay = tc.check_relay(card, "Output:\n" + printed, repo)
    assert relay["relay_verbatim"] and relay["verify_findings"] == []
    rounded = tc.check_relay(card, printed.replace("value=42", "value=40"), repo)
    assert not rounded["relay_verbatim"]


def test_a_failing_command_stops_the_card_and_is_recorded(tmp_path):
    repo, script, head = _git_repo(tmp_path)
    receipt = tc.run_card("card.yaml", "0" * 64, _frozen_card(script, head, first_exit="5"), repo)
    assert receipt["status"] == "stopped at command 1"
    assert len(receipt["commands"]) == 1 and receipt["commands"][0]["exit_code"] == 5
    assert "not run: 1 command(s) after the stop" in tc.brief(receipt, "out/receipt.json", "x")


def test_receipts_are_write_once(tmp_path):
    repo, script, head = _git_repo(tmp_path)
    card = _frozen_card(script, head)
    tc.run_card("card.yaml", "0" * 64, card, repo)
    with pytest.raises(tc.CardError, match="write-once"):
        tc.run_card("card.yaml", "0" * 64, card, repo)


def test_a_pinned_commit_that_is_not_head_is_an_impediment(tmp_path):
    repo, script, head = _git_repo(tmp_path)
    (repo / "later.txt").write_text("x")
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "later"], cwd=repo, check=True)
    with pytest.raises(tc.CardError, match="HEAD is"):
        tc.run_card("card.yaml", "0" * 64, _frozen_card(script, head), repo)
    assert not (repo / "out").exists()


def test_frozen_cards_refuse_secrets_in_env_and_streams_outside_scope(tmp_path):
    repo, script, head = _git_repo(tmp_path)
    card = _frozen_card(script, head)
    card["commands"][0]["env"] = {"ANTHROPIC_API_KEY": "x"}
    card["commands"][1]["stdout"] = "elsewhere/log"
    findings = tc.lint(card, repo)
    assert any("may not set" in f for f in findings), findings
    assert any("elsewhere/log is outside write_scope" in f for f in findings), findings


def test_runbook_cards_are_refused_where_runbook_py_is_absent(tmp_path):
    repo, script, head = _git_repo(tmp_path)
    card = _frozen_card(script, head)
    card.update(kind="runbook", runbook="x.yaml", runbook_sha256="0" * 64)
    assert any("only crypto-autoresearcher has" in f for f in tc.lint(card, repo))


def test_commands_may_run_in_a_repository_subdirectory_and_carry_an_id(tmp_path):
    repo, script, head = _git_repo(tmp_path)
    (repo / "sub").mkdir()
    card = _frozen_card(script, head)
    card["commands"][1].update(id="in-sub", cwd="sub",
                               argv=["python3", "-c", "import os; print(os.path.basename(os.getcwd()))"])
    assert tc.lint(card, repo) == []
    receipt = tc.run_card("card.yaml", "0" * 64, card, repo)
    assert receipt["commands"][1]["stdout_tail"] == ["sub"]
    assert 'command 2 (in-sub): ["python3"' in tc.brief(receipt, "out/receipt.json", "x")
    card["commands"][1]["cwd"] = "../escape"
    assert any(".cwd:" in f for f in tc.lint(card, repo))


def test_a_missing_declared_output_fails_the_command(tmp_path):
    repo, script, head = _git_repo(tmp_path)
    card = _frozen_card(script, head)
    card["commands"][0]["outputs"] = ["out/never-written.json"]
    receipt = tc.run_card("card.yaml", "0" * 64, card, repo)
    assert receipt["status"] == "stopped at command 1"
    assert receipt["commands"][0]["outputs"] == {"out/never-written.json": None}


def test_retry_reruns_only_on_the_named_exit_codes(tmp_path):
    repo, script, head = _git_repo(tmp_path)
    card = _frozen_card(script, head, first_exit="75")
    card["commands"][0]["retry"] = {"exit_codes": [75], "max_attempts": 3}
    receipt = tc.run_card("card.yaml", "0" * 64, card, repo)
    assert receipt["commands"][0]["attempts"] == 3
    assert "after 3 attempts" in tc.brief(receipt, "out/receipt.json", "x")

    repo2, script2, head2 = _git_repo(tmp_path / "second")
    card2 = _frozen_card(script2, head2, first_exit="5")
    card2["commands"][0]["retry"] = {"exit_codes": [75], "max_attempts": 3}
    assert tc.run_card("card.yaml", "0" * 64, card2, repo2)["commands"][0]["attempts"] == 1

    card2["commands"][0]["retry"] = {"exit_codes": [75], "max_attempts": 9}
    assert any(".retry:" in f for f in tc.lint(card2, repo2))


def test_must_not_exist_is_checked_before_anything_runs(tmp_path):
    repo, script, head = _git_repo(tmp_path)
    card = _frozen_card(script, head)
    card["must_not_exist"] = ["out/session"]
    (repo / "out/session").mkdir(parents=True)
    with pytest.raises(tc.CardError, match="already exist"):
        tc.run_card("card.yaml", "0" * 64, card, repo)
    assert not (repo / "out/receipt.json").exists()


# ---------------------------------------------------------------------------
# Batch lane: request carries every fact, ingest accepts only a correct reply
# ---------------------------------------------------------------------------

def _with_contract(repo):
    agents = repo / ".claude" / "agents"
    agents.mkdir(parents=True)
    (agents / "experiment-director.md").write_text("---\nname: experiment-director\n---\nDirector rules.\n")
    (repo / "design.md").write_text("Run tools/emit.py with argument 0, timeout 30 s.\n")
    return repo


def _fence(doc):
    return "```yaml\n" + tc.yaml.safe_dump(doc, sort_keys=False) + "```\n"


def test_compile_request_carries_head_digests_contract_and_design(tmp_path):
    repo, script, head = _git_repo(tmp_path)
    _with_contract(repo)
    prompt = tc.compile_request(["design.md"], ["tools/emit.py", "missing.py"], "cards/c.yaml", repo)
    assert head in prompt and rb.sha256_file(script) in prompt
    assert "bind missing.py: DOES NOT EXIST" in prompt
    assert "Director rules." in prompt and "name: experiment-director" not in prompt
    assert "Run tools/emit.py with argument 0" in prompt
    assert prompt == tc.compile_request(["design.md"], ["tools/emit.py", "missing.py"], "cards/c.yaml", repo)


def test_ingest_writes_a_clean_card_and_refuses_errors_and_bad_digests(tmp_path):
    repo, script, head = _git_repo(tmp_path)
    card = _frozen_card(script, head)
    good = _fence(card) + _fence({"specification_errors": []})
    assert tc.ingest("Here:\n" + good, "cards/c.yaml", "card", None, repo) == []
    assert (repo / "cards/c.yaml").is_file()
    assert any("write-once" in f for f in tc.ingest(good, "cards/c.yaml", "card", None, repo))

    errs = _fence(card) + _fence({"specification_errors": ["timeout not in the design"]})
    assert tc.ingest(errs, "cards/d.yaml", "card", None, repo) == [
        "specification_error: timeout not in the design"]
    card["binds"][0]["sha256"] = "0" * 64           # a digest the model invented
    bad = _fence(card) + _fence({"specification_errors": []})
    assert any("does not match its sha256" in f for f in tc.ingest(bad, "cards/e.yaml", "card", None, repo))
    assert not (repo / "cards/d.yaml").exists() and not (repo / "cards/e.yaml").exists()


def _assessment(card, outcome, recommendation):
    return _fence({"execution_assessment": {
        "card_id": card["card_id"], "card_sha256": "x", "outcome": outcome,
        "recommendation": recommendation, "reasons": ["status: completed"],
        "interpretation": "not_assessed"}})


def test_assessment_outcome_is_determined_by_the_facts(tmp_path):
    repo, script, head = _git_repo(tmp_path)
    _with_contract(repo)
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "contract"], cwd=repo, check=True)
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True,
                          text=True, check=True).stdout.strip()
    card = _frozen_card(script, head)
    assert tc.assessment_facts(card, None, repo)["outcome"] == "impeded"
    (repo / "preexisting.txt").write_text("dirty before the run")
    tc.run_card("card.yaml", "0" * 64, card, repo)
    facts = tc.assessment_facts(card, None, repo)
    assert facts["outcome"] == "executed_as_specified" and facts["writes_outside_scope"] == []
    prompt = tc.assess_request("card.yaml", "0" * 64, card, None, repo)
    assert "`executed_as_specified`" in prompt and "value=42" in prompt

    wrong = _assessment(card, "stopped", "respecify")
    assert any("the facts determine executed_as_specified" in f
               for f in tc.ingest(wrong, "out/a.yaml", "assessment", card, repo))
    assert tc.ingest(_assessment(card, "executed_as_specified", "proceed_to_analysis"),
                     "out/a.yaml", "assessment", card, repo) == []

    (repo / "stray.txt").write_text("written after the run, outside write_scope")
    facts = tc.assessment_facts(card, None, repo)
    assert facts["writes_outside_scope"] == ["stray.txt"] and facts["outcome"] == "executor_deviated"
