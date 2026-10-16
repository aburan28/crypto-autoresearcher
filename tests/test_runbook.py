"""tools/runbook.py: a runbook leaves the operator no choice, and its session
cannot be altered, padded, trimmed or fabricated without the record saying so.

Most tests run the committed conformance example
(`examples/runbooks/toy-ecdlp-bsgs/`) in a temporary copy of the files it
binds, then attack the copy. The guards are only worth having if each is seen
to fail on the tampering it exists for, so the adversarial tests outnumber the
happy path. The one attack the integrity checks cannot see -- a forgery that is
internally consistent -- is shown passing `verify` and failing the audit's
replay, which is the reason the audit exists.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest
import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
import runbook as rb  # noqa: E402

EXAMPLE = "examples/runbooks/toy-ecdlp-bsgs"
RUNBOOK = f"{EXAMPLE}/runbook.yaml"
EXAMPLE_FILES = [f"{EXAMPLE}/{name}" for name in
                 ("curve.json", "solve.py", "check.py", "trial-plan.json", "runbook.yaml", "README.md")]
EXAMPLE_FILES += ["formal/targets/runbook-example-bsgs-coverage.yaml",
                  "formal/CryptoResearch/Runbook/BsgsCoverage.lean"]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def copy_example(root: Path) -> Path:
    for relative in EXAMPLE_FILES:
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO / relative, target)
    return root


def session_of(root: Path) -> Path:
    return root / rb.load_runbook(root, RUNBOOK).session_dir


def edit_runbook(root: Path, mutate) -> None:
    path = root / RUNBOOK
    doc = yaml.safe_load(path.read_text())
    mutate(doc)
    path.write_text(yaml.safe_dump(doc, sort_keys=False))


def run(root: Path, path: str = RUNBOOK, owner: str | None = None) -> dict:
    return rb.Runner(rb.load_runbook(root, path), owner=owner).run()


def entries(session: Path) -> list[dict]:
    return rb.read_journal(session / "journal.jsonl")


def write_entries(session: Path, items: list[dict], *, rechain: bool) -> None:
    """Rewrite the journal. With rechain, recompute every link so the chain
    itself is consistent: the strongest forgery available to a writer who
    controls every byte."""
    if rechain:
        previous = rb.GENESIS
        for index, entry in enumerate(items):
            entry["seq"], entry["prev"] = index, previous
            entry["hash"] = rb.entry_hash(entry)
            previous = entry["hash"]
    (session / "journal.jsonl").write_text(
        "".join(json.dumps(e, sort_keys=True) + "\n" for e in items))


@pytest.fixture(scope="module")
def completed(tmp_path_factory) -> Path:
    """One completed run of the example; tests copy it before attacking it."""
    root = copy_example(tmp_path_factory.mktemp("completed"))
    result = run(root)
    assert result["status"] == "completed", result
    return root


@pytest.fixture
def fresh(completed, tmp_path) -> Path:
    root = tmp_path / "repo"
    shutil.copytree(completed, root)
    return root


# ---------------------------------------------------------------------------
# The committed example and its reference session
# ---------------------------------------------------------------------------

def test_the_committed_example_lints_clean() -> None:
    assert rb.lint(rb.load_runbook(REPO, RUNBOOK)) == []


def test_the_committed_reference_session_verifies_with_checkers_rerun() -> None:
    sessions = sorted((REPO / EXAMPLE / "runbook-sessions").glob("RBS-*"))
    assert sessions, "the example's reference session is not committed"
    for session in sessions:
        assert rb.verify(REPO, session, rerun_checks=True) == []


def test_the_committed_reference_session_replays_in_full(tmp_path) -> None:
    """The committed bytes, re-audited with every unit replayed.

    No audit is committed beside the reference session: it would be the
    producing session auditing itself, which audit-runs forbids. CI re-audits
    the committed bytes on every run instead."""
    root = copy_example(tmp_path)
    for session in (REPO / EXAMPLE / "runbook-sessions").glob("RBS-*"):
        shutil.copytree(session, root / EXAMPLE / "runbook-sessions" / session.name)
        report, _ = rb.audit(root, root / EXAMPLE / "runbook-sessions" / session.name,
                             samples=99, nonce="c1", auditor="ci")
        assert report["verdict"] == "clean", report["findings"]
        assert len(report["replays"]) == 14 and all(r["matched"] for r in report["replays"])


# ---------------------------------------------------------------------------
# Lint: every way to hand the operator a choice is a finding
# ---------------------------------------------------------------------------

def lint_after(tmp_path: Path, mutate) -> list[str]:
    root = copy_example(tmp_path)
    edit_runbook(root, mutate)
    return rb.lint(rb.load_runbook(root, RUNBOOK))


def test_vague_operator_text_is_refused(tmp_path) -> None:
    findings = lint_after(tmp_path, lambda d: d["steps"][0].update(
        title="Run the probe as needed and choose a reasonable timeout"))
    assert any("leaves a choice to the operator" in f and "'as needed'" in f for f in findings), findings


def test_a_bound_file_that_changed_is_refused(tmp_path) -> None:
    root = copy_example(tmp_path)
    with (root / EXAMPLE / "solve.py").open("a") as handle:
        handle.write("# edited after freezing\n")
    findings = rb.lint(rb.load_runbook(root, RUNBOOK))
    assert any("solve.py has changed since the runbook was frozen" in f for f in findings), findings


def test_scientific_trials_may_not_bypass_the_supervisor(tmp_path) -> None:
    def to_exp(doc):
        doc["experiment_id"] = "EXP-TEST-abcdef"
        doc["approval"] = {"mode": "decision_record"}
    findings = lint_after(tmp_path, to_exp)
    assert any("the local engine is for EXAMPLE-* runbooks" in f for f in findings), findings


def test_an_example_cannot_claim_decision_record_approval_and_vice_versa(tmp_path) -> None:
    findings = lint_after(tmp_path, lambda d: d.update(approval={"mode": "decision_record"}))
    assert any("approval mode example is only for EXAMPLE-*" in f for f in findings), findings


def test_only_infrastructure_failures_may_retry(tmp_path) -> None:
    findings = lint_after(tmp_path, lambda d: d["steps"][0].update(on_failure=[
        {"when": {"validity": False}, "class": "invalid_measurement", "action": "retry", "max_attempts": 2}]))
    assert any("only infrastructure_error, resource_exhaustion may retry" in f for f in findings), findings


def test_a_command_may_not_run_an_unbound_repository_file(tmp_path) -> None:
    root = copy_example(tmp_path)
    (root / "tools").mkdir(exist_ok=True)
    (root / "tools" / "helper.py").write_text("print('unbound')\n")
    edit_runbook(root, lambda d: d["steps"][0].update(argv=["python3", "tools/helper.py"]))
    findings = rb.lint(rb.load_runbook(root, RUNBOOK))
    assert any("argv names tools/helper.py, which is not in binds" in f for f in findings), findings


def test_shell_syntax_in_argv_is_refused(tmp_path) -> None:
    findings = lint_after(tmp_path, lambda d: d["steps"][0]["argv"].extend(["|", "tee", "x"]))
    assert any("'|' is shell syntax" in f for f in findings), findings


def test_a_command_step_cannot_carry_science(tmp_path) -> None:
    findings = lint_after(tmp_path, lambda d: d["steps"][0].pop("purpose"))
    assert any("scientific trials run only in a trials step" in f for f in findings), findings


def test_mechanical_tier_requires_each_output_tied_to_its_parameters(tmp_path) -> None:
    def untie(doc):
        step = doc["steps"][1]
        step.pop("by_trial")
        for block in step["validity"]["files"]:
            block["assertions"] = [a for a in block.get("assertions", []) if a.get("equals") != "{trial_id}"]
            if not block["assertions"]:
                block.pop("assertions")
                block.pop("json", None)
        doc["metrics"] = []
        doc.pop("report")
    findings = lint_after(tmp_path, untie)
    assert any("no assertion tying their output to their prescribed parameters" in f for f in findings), findings


def test_a_lean_obligation_binds_its_theorem_bytes(tmp_path) -> None:
    def unbind(doc):
        doc["binds"] = [b for b in doc["binds"] if not b["path"].endswith(".lean")]
    findings = lint_after(tmp_path, unbind)
    assert any("theorem file formal/CryptoResearch/Runbook/BsgsCoverage.lean must be in binds" in f
               for f in findings), findings


def test_a_spec_binding_that_disagrees_is_refused(tmp_path) -> None:
    findings = lint_after(tmp_path, lambda d: d["spec_bindings"][0].update(equals=1047691))
    assert any("/n is 1047689, the runbook says 1047691" in f for f in findings), findings


def test_an_execution_proof_needs_a_pinned_verifier(tmp_path) -> None:
    def add_proof(doc):
        doc["steps"].append({
            "id": "S04-proof", "kind": "execution_proof", "title": "Verify receipts",
            "explain": "Verifies each trial's receipt with the pinned verifier.",
            "of_step": "S02-solve", "receipt_file": "raw-result.json", "backend": "risc0",
            "image_id": "ab" * 32, "verifier": {"program": "r0-verify"},
            "verifier_args": ["{receipt}", "{out}"], "required": False, "timeout_seconds": 60})
    findings = lint_after(tmp_path, add_proof)
    assert any("the verifier binary is pinned by digest" in f for f in findings), findings


def test_an_outcome_cannot_hide_in_an_unknown_assertion_operator(tmp_path) -> None:
    findings = lint_after(tmp_path, lambda d: d["steps"][1]["validity"]["files"][1]["assertions"].append(
        {"pointer": "/verified", "predicted": True}))
    assert any("exactly one operator" in f for f in findings), findings


# ---------------------------------------------------------------------------
# A completed session
# ---------------------------------------------------------------------------

def test_a_completed_session_records_every_unit_and_computes_its_own_metrics(completed) -> None:
    session = session_of(completed)
    journal = entries(session)
    assert journal[0]["type"] == "session_started" and journal[-1]["type"] == "session_finished"
    summary = journal[-1]["summary"]
    assert summary["units"] == {"total": 14, "valid": 14, "invalid": []}
    assert summary["control_validity"] == "passed"
    assert summary["steps"]["S03-lean-coverage"] in ("unavailable", "passed")
    # Recompute the metric independently of the tool, from the raw outputs.
    ops = []
    for unit in (session / "units").iterdir():
        result = json.loads((unit / "raw-result.json").read_text())
        if result["mode"] == "search":
            ops.append(result["group_ops"])
    assert len(ops) == 12
    assert summary["metrics"]["group_ops"]["values"]["mean"] == sum(ops) / len(ops)
    assert summary["metrics"]["solved_fraction"]["values"]["fraction_true"] == 1.0
    assert summary["inferential_validity"].startswith("not_assessed")


def test_a_completed_session_verifies(completed) -> None:
    assert rb.verify(completed, session_of(completed), rerun_checks=True) == []


def test_running_a_finished_session_again_changes_nothing(fresh) -> None:
    before = (session_of(fresh) / "journal.jsonl").read_bytes()
    result = run(fresh)
    assert result["status"] == "completed"
    assert (session_of(fresh) / "journal.jsonl").read_bytes() == before


# ---------------------------------------------------------------------------
# Tampering with a session
# ---------------------------------------------------------------------------

def unit_dir(root: Path, trial_id: str) -> Path:
    plan = json.loads((root / EXAMPLE / "trial-plan.json").read_text())
    run_id = next(t["run_id"] for t in plan["trials"] if t["id"] == trial_id)
    return session_of(root) / "units" / run_id


def test_an_edited_output_is_found(fresh) -> None:
    raw = unit_dir(fresh, "s03") / "raw-result.json"
    data = json.loads(raw.read_text())
    data["group_ops"] += 1
    raw.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    findings = rb.verify(fresh, session_of(fresh))
    assert any("raw-result.json differs from the digest in its receipt" in f or "changed after its receipt" in f
               for f in findings), findings


def test_an_output_edited_with_its_receipt_rewritten_is_still_found(fresh) -> None:
    directory = unit_dir(fresh, "s03")
    raw = directory / "raw-result.json"
    data = json.loads(raw.read_text())
    data["group_ops"] += 1
    raw.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    receipt = directory / "local-receipt.json"
    doc = json.loads(receipt.read_text())
    doc["artifact_sha256"]["raw-result.json"] = sha(raw)
    doc["files_sha256"]["raw-result.json"] = sha(raw)
    receipt.write_text(json.dumps(doc, indent=2) + "\n")
    findings = rb.verify(fresh, session_of(fresh), rerun_checks=True)
    # The journal bound the original bytes, and the checker recounts the work.
    assert any("s03: artifacts recorded as" in f for f in findings), findings
    assert any("s03: checker exits 1" in f for f in findings), findings


def test_an_edited_journal_entry_breaks_the_chain(fresh) -> None:
    items = entries(session_of(fresh))
    items[5]["time"] = "2000-01-01T00:00:00.000000Z"
    write_entries(session_of(fresh), items, rechain=False)
    findings = rb.verify(fresh, session_of(fresh))
    assert any("journal entry 5: content does not match its hash" in f for f in findings), findings


def test_a_deleted_journal_entry_is_found(fresh) -> None:
    items = entries(session_of(fresh))
    del items[4]
    write_entries(session_of(fresh), items, rechain=False)
    findings = rb.verify(fresh, session_of(fresh))
    assert any("entries removed, inserted or reordered" in f for f in findings), findings


def test_reordered_journal_entries_are_found(fresh) -> None:
    items = entries(session_of(fresh))
    items[6], items[7] = items[7], items[6]
    write_entries(session_of(fresh), items, rechain=False)
    findings = rb.verify(fresh, session_of(fresh))
    assert any("prev does not match" in f for f in findings), findings


def test_a_truncated_journal_is_an_unfinished_session(fresh) -> None:
    items = entries(session_of(fresh))[:-1]
    write_entries(session_of(fresh), items, rechain=False)
    findings = rb.verify(fresh, session_of(fresh))
    assert any("has not finished" in f for f in findings), findings


def test_a_dropped_unit_is_a_coverage_gap(fresh) -> None:
    items = [e for e in entries(session_of(fresh))
             if not (e["type"] == "unit_recorded" and e["trial_id"] == "s07")]
    write_entries(session_of(fresh), items, rechain=True)
    findings = rb.verify(fresh, session_of(fresh))
    assert any("do not cover the plan's trials" in f for f in findings), findings


def test_a_file_added_to_the_session_is_found(fresh) -> None:
    (session_of(fresh) / "outputs" / "planted.json").write_text("{}\n")
    findings = rb.verify(fresh, session_of(fresh))
    assert any("planted.json is in the session directory but not in the journal" in f for f in findings), findings


def test_a_file_added_to_a_unit_is_found(fresh) -> None:
    (unit_dir(fresh, "s02") / "extra-result.json").write_text("{}\n")
    findings = rb.verify(fresh, session_of(fresh))
    assert any("extra-result.json was added to the unit after its receipt" in f for f in findings), findings


def test_a_deleted_unit_is_found(fresh) -> None:
    shutil.rmtree(unit_dir(fresh, "s09"))
    findings = rb.verify(fresh, session_of(fresh))
    assert any("s09: receipt_sha256 recorded as" in f for f in findings), findings


def test_a_runbook_edited_after_the_session_is_found(fresh) -> None:
    with (fresh / RUNBOOK).open("a") as handle:
        handle.write("# appended later\n")
    findings = rb.verify(fresh, session_of(fresh))
    assert any("has changed since the session started" in f for f in findings), findings


def test_a_rewritten_summary_is_found(fresh) -> None:
    items = entries(session_of(fresh))
    items[-1]["summary"]["metrics"]["group_ops"]["values"]["mean"] = 1.0
    write_entries(session_of(fresh), items, rechain=True)
    findings = rb.verify(fresh, session_of(fresh))
    assert any("recorded summary does not match a recomputation" in f for f in findings), findings


def forge_consistently(root: Path, trial_id: str) -> None:
    """Change a field no checker reads, then make every digest agree.

    This is what an executor that controls every byte can always do: rewrite
    the output, its receipt, the journal entry that bound it, and every chain
    link after it. Integrity checks cannot see it by construction."""
    directory = unit_dir(root, trial_id)
    raw = directory / "raw-result.json"
    data = json.loads(raw.read_text())
    data["setup_ops"] += 7
    raw.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    receipt = directory / "local-receipt.json"
    doc = json.loads(receipt.read_text())
    doc["artifact_sha256"]["raw-result.json"] = sha(raw)
    doc["files_sha256"]["raw-result.json"] = sha(raw)
    receipt.write_text(json.dumps(doc, indent=2) + "\n")
    items = entries(session_of(root))
    for entry in items:
        if entry["type"] == "unit_recorded" and entry["trial_id"] == trial_id:
            entry["artifacts"]["raw-result.json"] = sha(raw)
            entry["receipt_sha256"] = sha(receipt)
    write_entries(session_of(root), items, rechain=True)


def test_a_consistent_forgery_passes_verify_and_fails_the_audit_replay(fresh) -> None:
    forge_consistently(fresh, "s05")
    assert rb.verify(fresh, session_of(fresh), rerun_checks=True) == []
    report, target = rb.audit(fresh, session_of(fresh), samples=99, nonce="ab12", auditor="test")
    assert report["verdict"] == "flagged"
    assert any("replay S02-solve/s05" in f and "/setup_ops" in f for f in report["findings"]), report["findings"]
    assert json.loads((target / "audit.json").read_text())["verdict"] == "flagged"


# ---------------------------------------------------------------------------
# Audits
# ---------------------------------------------------------------------------

def test_an_audit_of_an_honest_session_is_clean_and_states_its_power(fresh) -> None:
    report, target = rb.audit(fresh, session_of(fresh), nonce="00ff", auditor="test")
    assert report["verdict"] == "clean", report["findings"]
    assert len(report["replays"]) == 4 and all(r["matched"] for r in report["replays"])
    assert report["detection_power"]["miss_probability"]["0.25"] == round(0.75 ** 4, 6)
    assert report["journal_tip"] == entries(session_of(fresh))[-1]["hash"]
    assert "never evidence about the hypothesis" in report["scope"]
    # Replays are verifications: they wrote nothing into the session.
    assert rb.verify(fresh, session_of(fresh)) == []
    assert (target / "replay").is_dir()


def test_the_sample_depends_on_the_nonce_and_only_the_nonce(fresh) -> None:
    def chosen(nonce):
        report, _ = rb.audit(fresh, session_of(fresh), nonce=nonce, auditor="test")
        return [r["trial_id"] for r in report["replays"]]
    first = chosen("1234")
    assert chosen("1234") == first
    assert any(chosen(nonce) != first for nonce in ("5678", "9abc", "def0"))


def test_pending_audits_lists_a_session_until_it_is_audited(fresh) -> None:
    rows = rb.pending_audits(fresh)
    assert [row["session_dir"] for row in rows] == [rb.load_runbook(fresh, RUNBOOK).session_dir]
    rb.audit(fresh, session_of(fresh), nonce="77", auditor="test")
    assert rb.pending_audits(fresh) == []


def test_an_exempt_replay_is_reported_as_not_covered(tmp_path) -> None:
    root = copy_example(tmp_path)
    edit_runbook(root, lambda d: d["steps"][1].update(
        replay={"mode": "exempt", "exempt_reason": "conformance test of the exemption path"}))
    assert run(root)["status"] == "completed"
    report, _ = rb.audit(root, session_of(root), nonce="aa", auditor="test")
    assert report["replays"] == []
    assert any("replay exempt" in item for item in report["not_covered"])
    assert report["detection_power"]["replayed_units"] == 0


# ---------------------------------------------------------------------------
# Failure semantics: the tool decides, records, and stops
# ---------------------------------------------------------------------------

def test_an_output_with_the_wrong_parameters_stops_the_session(tmp_path) -> None:
    root = copy_example(tmp_path)

    def wrong_seed(doc):
        doc["steps"][1]["by_trial"]["s01"]["files"][0]["assertions"][1] = {"pointer": "/seed", "equals": 1}
    edit_runbook(root, wrong_seed)
    result = run(root)
    assert result["status"] == "stopped"
    assert result["failure"]["step_id"] == "S02-solve"
    assert result["failure"]["class"] == "invalid_measurement"
    assert "s01" in result["failure"]["detail"] and "/seed equals 1" in result["failure"]["detail"]
    assert result["failure"]["tell"].startswith("A trial output failed its validity checks")
    # A stop is a record like any other: it verifies, and it is not reopened.
    assert rb.verify(root, session_of(root)) == []
    assert run(root)["status"] == "stopped"
    assert sum(e["type"] == "session_reopened" for e in entries(session_of(root))) == 0


def test_an_infrastructure_failure_retries_as_declared_then_reopens_once_fixed(tmp_path) -> None:
    root = copy_example(tmp_path)
    flag = root / "fail-flag"
    flag.write_text("1")

    def flaky(doc):
        doc["steps"][0].update(
            argv=["python3", "-c", "import os, sys; sys.exit(7 if os.path.exists('fail-flag') else 0)"],
            validity={"exit_code": 0},
            on_failure=[{"when": {"exit_code": 7}, "class": "infrastructure_error", "action": "retry",
                         "max_attempts": 3}])
    edit_runbook(root, flaky)
    result = run(root)
    assert result["status"] == "stopped" and result["failure"]["class"] == "infrastructure_error"
    started = [e for e in entries(session_of(root)) if e["type"] == "step_started"]
    assert [e["attempt"] for e in started] == [1, 2, 3]
    flag.unlink()
    result = run(root)
    assert result["status"] == "completed"
    journal = entries(session_of(root))
    assert sum(e["type"] == "session_reopened" for e in journal) == 1
    assert rb.verify(root, session_of(root)) == []


def test_an_interrupted_attempt_is_closed_preserved_and_never_reused(tmp_path) -> None:
    root = copy_example(tmp_path)

    class Crashing(rb.Runner):
        def run_trials(self, journal, step, attempt, out_dir):
            (out_dir / "partial.txt").write_text("written before the crash\n")
            raise KeyboardInterrupt
    with pytest.raises(KeyboardInterrupt):
        Crashing(rb.load_runbook(root, RUNBOOK)).run()
    assert run(root)["status"] == "completed"
    journal = entries(session_of(root))
    interrupted = [e for e in journal if e["type"] == "step_interrupted"]
    assert len(interrupted) == 1 and interrupted[0]["attempt"] == 1
    assert interrupted[0]["outputs"][0]["path"].endswith("S02-solve/attempt-1/partial.txt")
    assert any(e["type"] == "step_finished" and e["step_id"] == "S02-solve" and e["attempt"] == 2
               for e in journal)
    assert rb.verify(root, session_of(root)) == []


def test_a_required_lean_obligation_without_lean_stops_the_session(tmp_path, monkeypatch) -> None:
    root = copy_example(tmp_path)
    edit_runbook(root, lambda d: d["steps"][2].update(required=True))
    real = rb.program_path
    monkeypatch.setattr(rb, "program_path", lambda name: None if name == "lake" else real(name))
    result = run(root)
    assert result["status"] == "stopped"
    assert result["failure"] == {"step_id": "S03-lean-coverage", "class": "infrastructure_error",
                                 "detail": "lake is not on PATH: install Lean with formal/setup.sh on this host",
                                 "tell": None}


def test_a_lean_receipt_must_say_exactly_what_the_obligation_needs(tmp_path) -> None:
    root = copy_example(tmp_path)
    step = rb.load_runbook(root, RUNBOOK).step("S03-lean-coverage")
    task = root / step["task_file"]
    theorem = root / "formal/CryptoResearch/Runbook/BsgsCoverage.lean"
    good = {"schema": "crypto.autoresearch.formal_verification.v1",
            "verification": {"status": "machine_verified", "build_passed": True, "axiom_audit_passed": True,
                             "forbidden_constructs": [],
                             "theorem_name": "CryptoResearch.Runbook.BsgsCoverage.coverage"},
            "provenance": {"task_spec_sha256": sha(task), "theorem_sha256": sha(theorem)},
            "infrastructure_failure": None}
    receipt = tmp_path / "lean-receipt.json"

    def passes(doc) -> bool:
        if receipt.exists():
            receipt.unlink()
        receipt.write_text(json.dumps(doc))
        return all(c["passed"] for c in rb.lean_receipt_checks(root, step, receipt))
    assert passes(good)
    for path, value in (("verification.axiom_audit_passed", False), ("verification.status", "formalization_blocked"),
                        ("verification.forbidden_constructs", ["sorry"]),
                        ("verification.theorem_name", "CryptoResearch.Runbook.BsgsCoverage.weaker"),
                        ("provenance.theorem_sha256", "0" * 64)):
        bad = json.loads(json.dumps(good))
        section, key = path.split(".")
        bad[section][key] = value
        assert not passes(bad), path


# ---------------------------------------------------------------------------
# Execution proofs: only a pinned verifier's word counts, and only for this unit
# ---------------------------------------------------------------------------

PROOF_DRIVER = '''import hashlib, json, pathlib, sys
run_dir, trial = pathlib.Path(sys.argv[1]), sys.argv[2]
(run_dir / "raw-result.json").write_text(json.dumps({"trial_id": trial, "value": len(trial)}))
(run_dir / "receipt.bin").write_bytes(b"receipt-for-" + trial.encode())
'''
PROOF_CHECK = '''import json, pathlib, sys
data = json.loads((pathlib.Path(sys.argv[1]) / "raw-result.json").read_text())
sys.exit(0 if data["value"] == len(data["trial_id"]) else 1)
'''
FAKE_VERIFIER = '''#!{python}
import hashlib, json, os, pathlib, sys
receipt, out, image = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]), sys.argv[3]
mode = os.environ.get("FAKE_VERIFIER_MODE", "honest")
run_dir = receipt.parent
raw = run_dir / "raw-result.json"
digest = hashlib.sha256(raw.read_bytes()).hexdigest()
report = {{"verified": True, "dev_mode": mode == "dev", "image_id": "cd" * 32 if mode == "wrong-image" else image,
          "receipt_sha256": hashlib.sha256(receipt.read_bytes()).hexdigest(),
          "journal": {{"trial_id": json.loads(raw.read_text())["trial_id"],
                      "result_sha256": "0" * 64 if mode == "wrong-result" else digest}}}}
out.write_text(json.dumps(report))
'''


def proof_example(root: Path, *, required: bool) -> str:
    """A minimal EXAMPLE runbook whose trials leave receipts for a verifier."""
    d = root / "examples/runbooks/proof"
    d.mkdir(parents=True)
    (d / "drive.py").write_text(PROOF_DRIVER)
    (d / "check.py").write_text(PROOF_CHECK)
    verifier = root / "bin" / "fake-verify"
    verifier.parent.mkdir()
    verifier.write_text(FAKE_VERIFIER.format(python=sys.executable))
    verifier.chmod(0o755)
    rel = "examples/runbooks/proof"
    trials = [{"id": t, "run_id": f"RUN-PROOF-{i:06x}",
               "argv": ["python3", f"{rel}/drive.py", "{run_dir}", t],
               "check_argv": ["python3", f"{rel}/check.py", "{run_dir}"],
               "artifacts": ["raw-result.json", "receipt.bin"], "depends_on": []}
              for i, t in enumerate(("t1", "t2"))]
    plan = {"schema": rb.PLAN_SCHEMA, "experiment_id": "EXAMPLE-proof", "frozen": True,
            "source_sha256": {f"{rel}/drive.py": sha(d / "drive.py"), f"{rel}/check.py": sha(d / "check.py")},
            "trials": trials}
    (d / "trial-plan.json").write_text(json.dumps(plan))
    doc = {
        "schema": rb.SCHEMA, "experiment_id": "EXAMPLE-proof", "session_id": "RBS-PROOF-abc123",
        "title": "Produce receipts and verify them", "purpose": "Execution-proof seam conformance.",
        "executor_tier": "mechanical", "approval": {"mode": "example"},
        "binds": [{"path": f"{rel}/trial-plan.json", "sha256": sha(d / "trial-plan.json")}],
        "environment": {"programs": ["python3"]},
        "steps": [
            {"id": "S01-trials", "kind": "trials", "title": "Run both trials",
             "explain": "Runs drive.py then check.py for each trial.", "plan": f"{rel}/trial-plan.json",
             "engine": "local", "timeout_seconds": 60,
             "validity": {"files": [{"path": "raw-result.json", "json": True,
                                     "assertions": [{"pointer": "/trial_id", "equals": "{trial_id}"}]}]},
             "replay": {"mode": "bytes", "compare": [{"file": "raw-result.json"}], "sample": 1}},
            {"id": "S02-proofs", "kind": "execution_proof", "title": "Verify every receipt",
             "explain": "Runs the pinned verifier on each trial's receipt.", "of_step": "S01-trials",
             "receipt_file": "receipt.bin", "backend": "risc0", "image_id": "ab" * 32,
             "verifier": {"program": str(verifier), "sha256": sha(verifier)},
             "verifier_args": ["{receipt}", "{out}", "{image_id}"], "required": required,
             "timeout_seconds": 60,
             "journal": [{"pointer": "/trial_id", "equals": "{trial_id}"},
                         {"pointer": "/result_sha256", "equals_artifact_sha256": "raw-result.json"}]}],
    }
    (d / "runbook.yaml").write_text(yaml.safe_dump(doc, sort_keys=False))
    return f"{rel}/runbook.yaml"


def test_verified_receipts_bound_to_their_units_pass(tmp_path, monkeypatch) -> None:
    monkeypatch.delenv("RISC0_DEV_MODE", raising=False)
    monkeypatch.setenv("FAKE_VERIFIER_MODE", "honest")
    path = proof_example(tmp_path, required=True)
    assert rb.lint(rb.load_runbook(tmp_path, path)) == []
    result = run(tmp_path, path)
    assert result["status"] == "completed", result
    summary = entries(tmp_path / rb.load_runbook(tmp_path, path).session_dir)[-1]["summary"]
    assert summary["execution_proofs"]["verified_units"] == 2
    assert summary["execution_proofs"]["chain"].startswith("incomplete")


@pytest.mark.parametrize("mode", ["dev", "wrong-image", "wrong-result"])
def test_a_receipt_that_is_dev_for_another_image_or_another_result_fails(tmp_path, monkeypatch, mode) -> None:
    monkeypatch.delenv("RISC0_DEV_MODE", raising=False)
    monkeypatch.setenv("FAKE_VERIFIER_MODE", mode)
    result = run(tmp_path, proof_example(tmp_path, required=True))
    assert result["status"] == "stopped"
    assert result["failure"]["step_id"] == "S02-proofs"


def test_dev_mode_in_the_environment_is_never_a_proof(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("RISC0_DEV_MODE", "1")
    monkeypatch.setenv("FAKE_VERIFIER_MODE", "honest")
    path = proof_example(tmp_path, required=False)
    assert run(tmp_path, path)["status"] == "completed"
    summary = entries(tmp_path / rb.load_runbook(tmp_path, path).session_dir)[-1]["summary"]
    assert summary["execution_proofs"]["verified_units"] == 0
    assert summary["execution_proofs"]["unavailable_units"] == 2


def test_a_verifier_that_is_not_the_pinned_binary_is_not_trusted(tmp_path, monkeypatch) -> None:
    monkeypatch.delenv("RISC0_DEV_MODE", raising=False)
    monkeypatch.setenv("FAKE_VERIFIER_MODE", "honest")
    path = proof_example(tmp_path, required=True)
    with (tmp_path / "bin" / "fake-verify").open("a") as handle:
        handle.write("# swapped after pinning\n")
    result = run(tmp_path, path)
    assert result["status"] == "stopped"
    assert "does not match its pinned sha256" in result["failure"]["detail"]


def test_a_missing_optional_verifier_is_unavailable_not_verified(tmp_path, monkeypatch) -> None:
    monkeypatch.delenv("RISC0_DEV_MODE", raising=False)
    path = proof_example(tmp_path, required=False)
    (tmp_path / "bin" / "fake-verify").unlink()
    assert run(tmp_path, path)["status"] == "completed"
    summary = entries(tmp_path / rb.load_runbook(tmp_path, path).session_dir)[-1]["summary"]
    assert summary["steps"]["S02-proofs"] == "unavailable"
    assert summary["execution_proofs"]["verified_units"] == 0


# ---------------------------------------------------------------------------
# The supervisor engine: claim, supervised execution, release
# ---------------------------------------------------------------------------

FAKE_LANES = '''import json, pathlib, sys
args = sys.argv[1:]
state, log = pathlib.Path("lanes-state.json"), pathlib.Path("lanes-log.jsonl")
with log.open("a") as handle:
    handle.write(json.dumps(args) + "\\n")
data = json.loads(state.read_text()) if state.exists() else {}
if args[0] == "claims":
    print(json.dumps(data))
elif args[0] == "claim":
    owner = args[args.index("--as") + 1]
    data[args[2]] = {"status": "live", "owner": owner, "epoch": 1}
    state.write_text(json.dumps(data))
    print(f"claimed {args[2]} -> claims/{args[2]}.1.claim.json")
elif args[0] == "release":
    data[args[2]]["status"] = "released"
    state.write_text(json.dumps(data))
'''
FAKE_SUPERVISOR = '''import hashlib, json, os, pathlib, sys
args = sys.argv[1:]
plan_path = pathlib.Path(args[args.index("--plan") + 1])
plan = json.loads(plan_path.read_text())
plan_sha = hashlib.sha256(plan_path.read_bytes()).hexdigest()
code = int(os.environ.get("FAKE_SUPERVISOR_EXIT", "0"))
if code == 0:
    parent = pathlib.Path(plan["specification"]).parent
    for trial in plan["trials"]:
        run_dir = parent / "runs" / trial["run_id"]
        run_dir.mkdir(parents=True)
        (run_dir / "raw-result.json").write_text(json.dumps({"trial_id": trial["id"]}))
        (run_dir / "manifest.yaml").write_text("status: observed\\n")
        hashes = {n: hashlib.sha256((run_dir / n).read_bytes()).hexdigest() for n in trial["artifacts"]}
        (run_dir / "execution-receipt.json").write_text(json.dumps({
            "schema": "crypto.autoresearch.trial_receipt.v1", "plan_sha256": plan_sha,
            "trial_id": trial["id"], "run_id": trial["run_id"], "status": "output_validated",
            "returncode": 0, "check_returncode": 0, "artifact_sha256": hashes}))
print(json.dumps({"measurement_complete": code == 0}))
sys.exit(code)
'''


def git(root: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)


def supervised_repo(root: Path) -> str:
    exp = "experiments/EXP-TEST-abcdef"
    (root / exp).mkdir(parents=True)
    (root / "tools").mkdir()
    (root / "tools/goal_lanes.py").write_text(FAKE_LANES)
    (root / "tools/experiment_execution.py").write_text(FAKE_SUPERVISOR)
    (root / f"{exp}/specification.yaml").write_text("experiment: {id: EXP-TEST-abcdef}\n")
    trials = [{"id": t, "run_id": f"RUN-TEST-{i:06x}", "argv": ["python3", "driver.py", "{run_dir}"],
               "check_argv": ["python3", "check.py", "{run_dir}"],
               "artifacts": ["manifest.yaml", "raw-result.json"]} for i, t in enumerate(("t1", "t2"), 1)]
    plan = {"schema": rb.PLAN_SCHEMA, "experiment_id": "EXP-TEST-abcdef", "frozen": True,
            "task_id": "TASK-20261016-abcdef", "queue": f"{exp}/queue.json",
            "specification": f"{exp}/specification.yaml", "trials": trials}
    (root / f"{exp}/trial-plan.json").write_text(json.dumps(plan))
    artifacts = [f"{exp}/runs/{t['run_id']}/{name}" for t in trials
                 for name in (*rb.SUPERVISOR_GENERATED, *t["artifacts"])]
    (root / f"{exp}/queue.json").write_text(json.dumps({"tasks": [{
        "id": "TASK-20261016-abcdef", "role": "executor", "state": "queued",
        "write_scope": [f"{exp}/runs", f"{exp}/runbook-sessions"], "artifact_paths": artifacts}]}))
    doc = {"schema": rb.SCHEMA, "experiment_id": "EXP-TEST-abcdef", "session_id": "RBS-TEST-abcdef",
           "title": "Run the frozen plan under the supervisor", "purpose": "Supervisor engine conformance.",
           "executor_tier": "mechanical", "approval": {"mode": "decision_record"},
           "binds": [{"path": f"{exp}/trial-plan.json", "sha256": sha(root / f"{exp}/trial-plan.json")},
                     {"path": f"{exp}/specification.yaml", "sha256": sha(root / f"{exp}/specification.yaml")}],
           "environment": {"programs": ["python3", "git"]},
           "steps": [{"id": "S01-trials", "kind": "trials", "title": "Run the plan",
                      "explain": "Claims the task, runs the supervisor, releases the claim.",
                      "plan": f"{exp}/trial-plan.json", "engine": "supervisor", "claim": {"ttl_minutes": 60},
                      "timeout_seconds": 600,
                      "validity": {"files": [{"path": "raw-result.json", "json": True,
                                              "assertions": [{"pointer": "/trial_id", "equals": "{trial_id}"}]}]},
                      "replay": {"mode": "exempt", "exempt_reason": "the fake supervisor has no replayable driver"}}]}
    (root / f"{exp}/runbook.yaml").write_text(yaml.safe_dump(doc, sort_keys=False))
    git(root, "init", "-q")
    git(root, "config", "user.email", "test@example.invalid")
    git(root, "config", "user.name", "runbook tests")
    git(root, "add", ".")
    git(root, "commit", "-qm", "fixture")
    return f"{exp}/runbook.yaml"


def approve(root: Path, path: str) -> None:
    decision = root / "ledger/decisions/DEC-20261016-abcdef.yaml"
    decision.parent.mkdir(parents=True)
    decision.write_text(yaml.safe_dump({"coordinator_decision": {
        "id": "DEC-20261016-abcdef", "decision": "approve", "target_ids": ["EXP-TEST-abcdef"],
        "runbook_sha256": sha(root / path)}}))
    git(root, "add", ".")
    git(root, "commit", "-qm", "approve")


def test_an_unapproved_runbook_does_not_start(tmp_path) -> None:
    path = supervised_repo(tmp_path)
    with pytest.raises(rb.RunbookError, match="no committed ledger/decisions record approves"):
        run(tmp_path, path)
    assert not (tmp_path / rb.load_runbook(tmp_path, path).session_dir).exists()


def test_an_uncommitted_runbook_does_not_start(tmp_path) -> None:
    path = supervised_repo(tmp_path)
    approve(tmp_path, path)
    with (tmp_path / path).open("a") as handle:
        handle.write("# not committed\n")
    with pytest.raises(rb.RunbookError, match="not committed as-is at HEAD"):
        run(tmp_path, path)


def test_the_supervisor_engine_claims_runs_and_releases(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("FAKE_SUPERVISOR_EXIT", "0")
    path = supervised_repo(tmp_path)
    approve(tmp_path, path)
    result = run(tmp_path, path, owner="mech-test")
    assert result["status"] == "completed", result
    calls = [json.loads(line) for line in (tmp_path / "lanes-log.jsonl").read_text().splitlines()]
    assert [c[0] for c in calls] == ["claims", "claim", "claims", "release"]
    assert calls[1][calls[1].index("--as") + 1] == "mech-test" and "--publish" in calls[1]
    assert calls[3][calls[3].index("--outcome") + 1] == "completed"
    summary = entries(tmp_path / rb.load_runbook(tmp_path, path).session_dir)[-1]["summary"]
    assert summary["units"]["valid"] == 2
    paths = rb.publish_paths(tmp_path, rb.load_runbook(tmp_path, path).session_dir)["paths"]
    assert "experiments/EXP-TEST-abcdef/runs/RUN-TEST-000001" in paths


def test_a_supervisor_refusal_stops_the_session_and_releases_as_failed(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("FAKE_SUPERVISOR_EXIT", "2")
    path = supervised_repo(tmp_path)
    approve(tmp_path, path)
    result = run(tmp_path, path, owner="mech-test")
    assert result["status"] == "stopped"
    assert result["failure"]["class"] == "infrastructure_error"
    assert "impediment: the supervisor refused to launch" in result["failure"]["detail"]
    calls = [json.loads(line) for line in (tmp_path / "lanes-log.jsonl").read_text().splitlines()]
    assert calls[-1][0] == "release" and calls[-1][calls[-1].index("--outcome") + 1] == "failed"


# ---------------------------------------------------------------------------
# Reports, publication, and the assertion engine
# ---------------------------------------------------------------------------

def test_the_report_is_generated_from_the_journal(fresh, monkeypatch) -> None:
    monkeypatch.setattr(rb, "render_pdf", lambda target: "renderer disabled in this test")
    target = rb.report(fresh, session_of(fresh))
    data = json.loads((target / "data.json").read_text())
    assert data["journal_tip"] == entries(session_of(fresh))[-1]["hash"]
    assert len(data["graph"]["points"]) == 12
    typ = (target / "report.typ").read_text()
    assert "EXAMPLE-toy-ecdlp-bsgs" in typ and "states no verdict" in typ
    assert (target / "graph.svg").read_text().startswith("<svg")
    assert (target / "RENDER-BLOCKED.txt").read_text().strip() == "renderer disabled in this test"
    paths = rb.publish_paths(fresh, session_of(fresh))["paths"]
    assert rb.rel(fresh.resolve(), target) in paths


def test_typst_text_cannot_inject_markup() -> None:
    assert rb._t('a "quoted" \\ path #set') == '#"a \\"quoted\\" \\\\ path #set"'


@pytest.mark.parametrize("assertion, data, expected", [
    ({"pointer": "/x", "equals": 1}, {"x": True}, False),       # True is not 1
    ({"pointer": "/x", "equals": True}, {"x": 1}, False),
    ({"pointer": "/x", "type": "integer"}, {"x": True}, False),  # a bool is not an integer
    ({"pointer": "/x", "type": "number"}, {"x": 2.5}, True),
    ({"pointer": "/a~1b", "equals": 3}, {"a/b": 3}, True),       # RFC 6901 escaping
    ({"pointer": "/l/1", "equals": "y"}, {"l": ["x", "y"]}, True),
    ({"pointer": "/x", "min": 2}, {"x": 1}, False),
    ({"pointer": "/x", "exists": False}, {}, True),
    ({"pointer": "/x", "in": [1, 2]}, {"x": 2}, True),
    ({"pointer": "/x", "matches": "^RUN-"}, {"x": "RUN-ab"}, True),
    ({"pointer": "/x", "length": 0}, {"x": []}, True),
])
def test_assertions(assertion, data, expected) -> None:
    assert rb.check_assertion(assertion, data)[0] is expected


def test_templated_assertions_bind_the_unit() -> None:
    unit = {"trial_id": "s01", "run_id": "RUN-X-000001"}
    assert rb.check_assertion({"pointer": "/t", "equals": "{trial_id}"}, {"t": "s01"}, unit=unit)[0]
    assert not rb.check_assertion({"pointer": "/t", "equals": "{trial_id}"}, {"t": "s02"}, unit=unit)[0]
    shas = {"raw-result.json": "ab" * 32}
    assert rb.check_assertion({"pointer": "/d", "equals_artifact_sha256": "raw-result.json"},
                              {"d": "ab" * 32}, unit=unit, artifact_sha=shas)[0]


def test_non_finite_json_is_refused(tmp_path) -> None:
    path = tmp_path / "x.json"
    path.write_text('{"a": NaN}')
    with pytest.raises(ValueError, match="non-finite"):
        rb.read_json_file(path)


def test_the_cli_exit_codes(tmp_path) -> None:
    root = copy_example(tmp_path)
    tool = [sys.executable, str(REPO / "tools/runbook.py"), "--repo", str(root)]
    lint = subprocess.run([*tool, "lint", RUNBOOK], capture_output=True, text=True)
    assert lint.returncode == 0 and lint.stdout.startswith("LINT OK")
    done = subprocess.run([*tool, "run", RUNBOOK], capture_output=True, text=True, env=dict(os.environ))
    assert done.returncode == 0, done.stderr
    final = json.loads(done.stdout.strip().splitlines()[-1])
    assert final["status"] == "completed"
    verify = subprocess.run([*tool, "verify", final["session_dir"]], capture_output=True, text=True)
    assert verify.returncode == 0 and verify.stdout.strip() == "VERIFY OK"
    brief = subprocess.run([*tool, "status", final["session_dir"], "--brief"], capture_output=True, text=True)
    assert "units: 14 valid of 14" in brief.stdout
    missing = subprocess.run([*tool, "verify", "nowhere"], capture_output=True, text=True)
    assert missing.returncode == 2 and missing.stderr.startswith("IMPEDIMENT")


def test_the_template_uses_only_fields_the_tool_accepts() -> None:
    template = yaml.safe_load((REPO / "templates/runbook.yaml").read_text())
    assert set(template) <= rb.TOP_KEYS and rb.TOP_REQUIRED <= set(template)
    kinds = {step["kind"] for step in template["steps"]}
    assert kinds == set(rb.STEP_KINDS)
    for step in template["steps"]:
        assert set(step) <= rb.STEP_KEYS[step["kind"]], step["id"]


def test_the_supervisor_list_of_generated_files_is_the_supervisors() -> None:
    import experiment_execution
    assert rb.SUPERVISOR_GENERATED == experiment_execution.GENERATED


def test_a_plan_the_supervisor_would_refuse_does_not_lint(tmp_path) -> None:
    path = supervised_repo(tmp_path)
    queue = tmp_path / "experiments/EXP-TEST-abcdef/queue.json"
    doc = json.loads(queue.read_text())
    doc["tasks"][0]["artifact_paths"] = [p for p in doc["tasks"][0]["artifact_paths"] if not p.endswith("launch.json")]
    doc["tasks"][0]["write_scope"] = ["experiments/EXP-TEST-abcdef/runs"]
    queue.write_text(json.dumps(doc))
    findings = rb.lint(rb.load_runbook(tmp_path, path))
    assert any("the supervisor will refuse this plan: 2 run file(s)" in f for f in findings), findings
    assert any("write_scope does not include experiments/EXP-TEST-abcdef/runbook-sessions/RBS-TEST-abcdef" in f
               for f in findings), findings
