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

    (repo / "director-reply.md").write_text("written after the run by the director, not the run")
    assert tc.assessment_facts(card, None, repo)["writes_outside_scope"] == []

    repo2, script2, head2 = _git_repo(tmp_path / "second")
    stray = _frozen_card(script2, head2)
    stray["commands"][1]["argv"] = ["python3", "-c", "open('stray.txt', 'w').write('outside scope')"]
    tc.run_card("card.yaml", "0" * 64, stray, repo2)
    facts = tc.assessment_facts(stray, None, repo2)
    assert facts["writes_outside_scope"] == ["stray.txt"] and facts["outcome"] == "executor_deviated"


# ---------------------------------------------------------------------------
# Lane: compile -> run -> assess end to end through a batch backend
# ---------------------------------------------------------------------------

import json  # noqa: E402
import sys  # noqa: E402

_ANSWER = r'''
import re, yaml
def answer(prompt, digest=None):
    """What a batch model given only the prompt would reply."""
    if "compile mode" in prompt:
        head = re.search(r"repository HEAD: (\w+)", prompt).group(1)
        sha = digest or re.search(r"bind tools/emit.py: sha256 (\w+)", prompt).group(1)
        receipt = re.search(r"Receipt at `([^`]+)`", prompt).group(1)
        scope = re.search(r"Write scope: `([^`]+)`", prompt).group(1)
        card = {"schema": "crypto.autoresearch.mechanical-task-card.v1", "card_id": "CARD-EXAMPLE-lane-01",
                "experiment_id": "EXAMPLE-lane", "author_role": "experiment-director",
                "executor_role": "executor-mechanical", "kind": "frozen_command", "commit": head,
                "receipt": receipt, "binds": [{"path": "tools/emit.py", "sha256": sha}],
                "commands": [{"id": "emit", "argv": ["python3", "tools/emit.py", "0"],
                              "timeout_seconds": 30, "success_exit_codes": [0]}],
                "bus_address": "executor-mechanical-lane", "background": False,
                "write_scope": [scope], "stop_when": ["The run command exits with status 2."]}
        return ("```yaml\n" + yaml.safe_dump(card, sort_keys=False) + "```\n\n"
                "```yaml\nspecification_errors: []\n```\n")
    block = re.search(r"```yaml\n(execution_assessment:.*?)```", prompt, re.S).group(1)
    allowed = re.search(r"recommendation: <one of ([a-z_]+)", block).group(1)
    block = re.sub(r"<one of [^>]+>", allowed, block)
    return "```yaml\n" + block.replace("[<one line each>]", '["Computed facts: status."]') + "```\n"
'''


def _fake(tmp_path, name, body):
    path = tmp_path / name
    path.write_text(f"#!{sys.executable}\nimport json, os, sys\n{_ANSWER}\n{body}")
    path.chmod(0o755)
    return str(path)


def _fake_delphi(tmp_path, digest=None):
    return _fake(tmp_path, "delphi", f"""
args = sys.argv[1:]
out = args[args.index("-out") + 1]
prompt = args[args.index("-prompt") + 1]
os.makedirs(out, exist_ok=True)
with open(os.path.join(out, "results.jsonl"), "w") as fh:
    fh.write(json.dumps({{"id": "prompt-1", "status": "succeeded", "model": args[args.index("-model") + 1],
                         "batch_id": "msgbatch_fake", "usage": {{"input_tokens": 10, "output_tokens": 5}},
                         "text": answer(prompt, {digest!r})}}) + "\\n")
""")


def _fake_conductor(tmp_path, log):
    return _fake(tmp_path, "conductor", f"""
args = sys.argv[1:]
open({str(log)!r}, "a").write(json.dumps(args) + "\\n")
if args[:2] == ["delphi", "profiles"]:
    print("director  anthropic  claude-sonnet-5-5  high")
    sys.exit(0)
print(answer(open(args[args.index("--file") + 1]).read()))
""")


def _lane_repo(tmp_path):
    repo, script, head = _git_repo(tmp_path)
    _with_contract(repo)
    (repo / "design.md").write_text(
        "Run tools/emit.py with argument 0, timeout 30 seconds, success exit code 0.\n"
        "Pin the commit. Bind tools/emit.py. Receipt at `out/receipt.json`.\n"
        "Write scope: `out/` only.\n")
    return repo


def test_lane_runs_end_to_end_through_standalone_delphi(tmp_path):
    repo = _lane_repo(tmp_path)
    lines = []
    code = tc.lane(["design.md"], ["tools/emit.py"], "cards/c.yaml", "out/assessment.yaml", "delphi",
                   {"delphi": _fake_delphi(tmp_path)}, repo, lines.append)
    assert code == 0, lines
    assert (repo / "cards/c.yaml").is_file() and (repo / "out/assessment.yaml").is_file()
    record = json.loads((repo / "cards/c.lane/lane.json").read_text())
    assert record["backend"] == "delphi" and record["outcome"] == "executed_as_specified"
    assert record["calls"]["compile"]["batch_id"] == "msgbatch_fake"
    assert record["calls"]["assess"]["model"] == tc.DIRECTOR_MODEL
    assert any("batch msgbatch_fake" in line for line in lines)


def test_lane_auto_prefers_a_connected_conductor_and_links_the_task(tmp_path, monkeypatch):
    repo = _lane_repo(tmp_path)
    (tmp_path / "bin").mkdir()
    log = tmp_path / "conductor.log"
    conductor = _fake_conductor(tmp_path / "bin", log)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    code = tc.lane(["design.md"], ["tools/emit.py"], "cards/c.yaml", "out/assessment.yaml", "auto",
                   {"conductor": conductor, "delphi": "/nonexistent/delphi", "task": "T-42"},
                   repo, lambda _line: None)
    assert code == 0
    asks = [json.loads(line) for line in log.read_text().splitlines() if "ask" in line]
    assert len(asks) == 2
    assert all(a[a.index("--profile") + 1] == "director" and a[a.index("--task") + 1] == "T-42" for a in asks)
    assert json.loads((repo / "cards/c.lane/lane.json").read_text())["backend"] == "conductor"


def test_lane_refuses_an_invented_digest_and_writes_no_card(tmp_path):
    repo = _lane_repo(tmp_path)
    (tmp_path / "bin").mkdir()
    lines = []
    code = tc.lane(["design.md"], ["tools/emit.py"], "cards/c.yaml", "out/assessment.yaml", "delphi",
                   {"delphi": _fake_delphi(tmp_path / "bin", digest="0" * 64)}, repo, lines.append)
    assert code == 1
    assert not (repo / "cards/c.yaml").exists() and not (repo / "out").exists()
    assert json.loads((repo / "cards/c.lane/lane.json").read_text())["outcome"] == "card_refused"
    assert any("does not match its sha256" in line for line in lines)


def test_lane_without_a_backend_is_an_impediment_that_writes_nothing(tmp_path, monkeypatch):
    repo = _lane_repo(tmp_path)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    lines = []
    code = tc.lane(["design.md"], [], "cards/c.yaml", "out/a.yaml", "auto",
                   {"conductor": "/nonexistent/conductor", "delphi": "/nonexistent/delphi"}, repo, lines.append)
    assert code == 2 and lines[-1].startswith("IMPEDIMENT no batch backend")
    assert not (repo / "cards").exists()


# ---------------------------------------------------------------------------
# Lane --route: Delphi's registry chooses each step's model; refused replies escalate
# ---------------------------------------------------------------------------

def _routed_delphi(tmp_path, routes, behaviour, log):
    """A stand-in delphi with `route` (routes: family -> route JSON or an error string) and
    `run`, whose answer depends on the model: ok, bad (an invented digest), refuse, specerr."""
    return _fake(tmp_path, "delphi", f"""
args = sys.argv[1:]
routes, behaviour, log = {routes!r}, {behaviour!r}, {str(log)!r}
if args[0] == "route":
    family = args[args.index("-family") + 1]
    r = routes[family]
    print(json.dumps({{"route": {{}}, "error": r}} if isinstance(r, str) else {{"route": r}}))
    sys.exit(1 if isinstance(r, str) else 0)
out = args[args.index("-out") + 1]
prompt = args[args.index("-prompt") + 1]
model = args[args.index("-model") + 1]
open(log, "a").write(json.dumps({{"provider": args[args.index("-provider") + 1], "model": model,
                                 "effort": args[args.index("-effort") + 1] if "-effort" in args else ""}}) + "\\n")
kind = behaviour.get(model, "ok")
row = {{"id": "prompt-1", "status": "succeeded", "model": model, "batch_id": "b-" + model}}
if kind == "refuse":
    row.update(status="refused", refusal={{"category": "test"}})
elif kind == "bad":
    row["text"] = answer(prompt, "0" * 64)
elif kind == "specerr":
    row["text"] = answer(prompt).replace("specification_errors: []", "specification_errors:\\n- the design gives no timeout")
else:
    row["text"] = answer(prompt)
os.makedirs(out, exist_ok=True)
open(os.path.join(out, "results.jsonl"), "w").write(json.dumps(row) + "\\n")
""")


def _route(choice, *escalation):
    return {"choice": choice, "escalation": list(escalation), "basis": f"{choice} measured good enough"}


def _calls(log):
    return [json.loads(line) for line in log.read_text().splitlines()] if log.exists() else []


def _run_routed(tmp_path, routes, behaviour, via="delphi"):
    repo = _lane_repo(tmp_path)
    (tmp_path / "bin").mkdir()
    log = tmp_path / "delphi.log"
    lines = []
    code = tc.lane(["design.md"], ["tools/emit.py"], "cards/c.yaml", "out/assessment.yaml", via,
                   {"delphi": _routed_delphi(tmp_path / "bin", routes, behaviour, log), "route": True},
                   repo, lines.append)
    record = json.loads((repo / "cards/c.lane/lane.json").read_text()) if (repo / "cards/c.lane/lane.json").exists() else None
    return code, lines, _calls(log), record, repo


def test_lane_route_sends_each_step_to_its_routed_model(tmp_path):
    code, lines, calls, record, _ = _run_routed(tmp_path, {
        "card-compile": _route("vllm:glm-5.3", "anthropic:claude-sonnet-5-5@high"),
        "assess": _route("anthropic:claude-haiku-5-5")}, {})
    assert code == 0, lines
    assert calls == [{"provider": "vllm", "model": "glm-5.3", "effort": ""},
                     {"provider": "anthropic", "model": "claude-haiku-5-5", "effort": ""}]
    assert record["routes"]["compile"]["basis"] == "vllm:glm-5.3 measured good enough"
    assert record["calls"]["compile"]["target"]["model"] == "glm-5.3"
    assert any("routed to vllm:glm-5.3" in line for line in lines)


def test_lane_route_escalates_a_reply_the_tool_refuses(tmp_path):
    code, lines, calls, record, repo = _run_routed(tmp_path, {
        "card-compile": _route("vllm:glm-5.3", "anthropic:claude-sonnet-5-5@high"),
        "assess": _route("anthropic:claude-haiku-5-5")}, {"glm-5.3": "bad"})
    assert code == 0, lines
    assert [c["model"] for c in calls] == ["glm-5.3", "claude-sonnet-5-5", "claude-haiku-5-5"]
    assert calls[1]["effort"] == "high"
    assert record["calls"]["compile"]["accepted"] is False
    assert record["calls"]["compile-escalation-1"]["accepted"] is True
    assert (repo / "cards/c.yaml").is_file()


def test_lane_route_escalates_a_model_refusal(tmp_path):
    code, lines, calls, record, _ = _run_routed(tmp_path, {
        "card-compile": _route("anthropic:claude-haiku-5-5", "anthropic:claude-sonnet-5-5@high"),
        "assess": _route("anthropic:claude-haiku-5-5")}, {"claude-haiku-5-5": "refuse"})
    # Compile escalates past the refusal; assess has nowhere to escalate and stops there.
    assert [c["model"] for c in calls] == ["claude-haiku-5-5", "claude-sonnet-5-5", "claude-haiku-5-5"]
    assert "refused" in record["calls"]["compile"] and record["calls"]["compile-escalation-1"]["accepted"]
    assert code == 1 and record["outcome"] == "assessment_refused"


def test_lane_route_never_escalates_a_specification_error(tmp_path):
    code, lines, calls, record, repo = _run_routed(tmp_path, {
        "card-compile": _route("vllm:glm-5.3", "anthropic:claude-sonnet-5-5@high"),
        "assess": _route("anthropic:claude-haiku-5-5")}, {"glm-5.3": "specerr"})
    assert code == 1 and record["outcome"] == "card_refused"
    assert [c["model"] for c in calls] == ["glm-5.3"], "a design's gap must not be escalated to a pricier model"
    assert not (repo / "cards/c.yaml").exists()


def test_lane_route_refuses_conductor_and_an_unroutable_family(tmp_path):
    code, lines, calls, _, _ = _run_routed(tmp_path, {"card-compile": _route("vllm:glm-5.3"),
                                                       "assess": _route("vllm:glm-5.3")}, {}, via="conductor")
    assert code == 2 and "--route needs standalone delphi" in lines[-1] and calls == []
    code, lines, calls, record, _ = _run_routed(tmp_path / "second", {
        "card-compile": "no model qualifies for card-compile: considered: vllm:glm-5.3 (worse)",
        "assess": _route("vllm:glm-5.3")}, {})
    assert code == 2 and "no routed model for card-compile" in lines[-1] and calls == []
    assert record["outcome"] == "impeded"
