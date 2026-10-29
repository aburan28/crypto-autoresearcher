"""tools/runbook.py: one session id, one execution (TASK-20261029-1bcf80,
DEC-20261029-9bc3ff).

RBS-ICPERF-b7e41c was written by two executions under one frozen session_id,
each unseen by the other, and the audit could not tell. `run` now refuses to
start a session whose journal already exists on a local branch or a fetched
remote-tracking ref, and refuses a resume when a ref holds a journal that is
neither a byte prefix nor an extension of the local one. `audit` reports every
unrelated journal chain the session path has had in full git history.

Every test works in a temporary git repository holding a copy of the
conformance example. No real session is read or written.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
import runbook as rb  # noqa: E402

EXAMPLE = "examples/runbooks/toy-ecdlp-bsgs"
RUNBOOK = f"{EXAMPLE}/runbook.yaml"
EXAMPLE_FILES = [f"{EXAMPLE}/{name}" for name in
                 ("curve.json", "solve.py", "check.py", "trial-plan.json", "runbook.yaml", "README.md")]
EXAMPLE_FILES += ["formal/targets/runbook-example-bsgs-coverage.yaml",
                  "formal/CryptoResearch/Runbook/BsgsCoverage.lean"]
GIT_ENV = {"GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1",
           "GIT_AUTHOR_NAME": "test", "GIT_AUTHOR_EMAIL": "test@example.invalid",
           "GIT_COMMITTER_NAME": "test", "GIT_COMMITTER_EMAIL": "test@example.invalid"}


def g(root: Path, *args: str) -> str:
    done = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True,
                          env={**os.environ, **GIT_ENV}, check=True)
    return done.stdout.strip()


def repo_with_example(root: Path) -> Path:
    for relative in EXAMPLE_FILES:
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO / relative, target)
    g(root, "init", "-q", "-b", "main")
    g(root, "add", "-A")
    g(root, "commit", "-q", "-m", "example")
    return root


def session_rel(root: Path) -> str:
    return rb.load_runbook(root, RUNBOOK).session_dir


def journal(root: Path) -> Path:
    return root / session_rel(root) / "journal.jsonl"


def run(root: Path, owner: str | None = None) -> dict:
    return rb.Runner(rb.load_runbook(root, RUNBOOK), owner=owner).run()


def interrupted_run(root: Path, owner: str) -> None:
    """A session that stops mid-step, leaving a resumable journal."""
    class Crashing(rb.Runner):
        def run_trials(self, journal, step, attempt, out_dir):
            raise KeyboardInterrupt
    with pytest.raises(KeyboardInterrupt):
        Crashing(rb.load_runbook(root, RUNBOOK), owner=owner).run()


def commit_session(root: Path, message: str) -> str:
    g(root, "add", "-A", session_rel(root))
    g(root, "commit", "-q", "-m", message)
    return g(root, "rev-parse", "HEAD")


def blob_of(root: Path, rev: str) -> str:
    return g(root, "rev-parse", f"{rev}:{session_rel(root)}/journal.jsonl")


def files_under(root: Path) -> set[str]:
    return {p.relative_to(root).as_posix() for p in root.rglob("*") if ".git" not in p.parts}


def put_journal_on_ref(root: Path, ref: str, data: bytes) -> str:
    """Commit `data` as the session journal on `ref`, on top of HEAD, without
    touching the work tree: another execution's journal, pushed elsewhere."""
    blob = subprocess.run(["git", "-C", str(root), "hash-object", "-w", "--stdin"], input=data,
                          capture_output=True, check=True).stdout.decode().strip()
    index = root / ".git" / "collision-test-index"
    env = {**os.environ, **GIT_ENV, "GIT_INDEX_FILE": str(index)}
    def plumb(*args: str) -> str:
        return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True,
                              env=env, check=True).stdout.strip()
    plumb("read-tree", "HEAD")
    plumb("update-index", "--add", "--cacheinfo", f"100644,{blob},{session_rel(root)}/journal.jsonl")
    commit = plumb("commit-tree", plumb("write-tree"), "-p", "HEAD", "-m", f"journal on {ref}")
    index.unlink()
    g(root, "update-ref", ref, commit)
    return blob


def other_execution(tmp_path: Path, owner: str, *, interrupted: bool = False) -> bytes:
    """The journal another clone wrote under the same session id."""
    other = repo_with_example(tmp_path / f"other-{owner}")
    if interrupted:
        interrupted_run(other, owner=owner)
    else:
        assert run(other, owner=owner)["status"] == "completed"
    return journal(other).read_bytes()


# ---------------------------------------------------------------------------
# run: a session id that is already taken
# ---------------------------------------------------------------------------

def test_a_journal_on_another_local_branch_refuses_a_new_session(tmp_path) -> None:
    root = repo_with_example(tmp_path)
    g(root, "switch", "-q", "-c", "lane-a")
    assert run(root, owner="exec-a")["status"] == "completed"
    commit_session(root, "session from execution A")
    blob = blob_of(root, "lane-a")
    g(root, "switch", "-q", "main")
    g(root, "clean", "-fdq")
    assert not journal(root).exists()
    before = files_under(root)
    with pytest.raises(rb.RunbookError) as refused:
        run(root, owner="exec-b")
    assert "refs/heads/lane-a" in str(refused.value) and blob in str(refused.value)
    # Nothing was written.
    assert files_under(root) == before


def test_a_journal_on_a_fetched_remote_tracking_ref_refuses_a_new_session(tmp_path) -> None:
    root = repo_with_example(tmp_path)
    g(root, "switch", "-q", "-c", "lane-a")
    run(root, owner="exec-a")
    commit = commit_session(root, "session from execution A")
    g(root, "switch", "-q", "main")
    g(root, "branch", "-q", "-D", "lane-a")
    g(root, "update-ref", "refs/remotes/origin/lane-a", commit)
    g(root, "clean", "-fdq")
    before = files_under(root)
    with pytest.raises(rb.RunbookError) as refused:
        run(root, owner="exec-b")
    assert "refs/remotes/origin/lane-a" in str(refused.value)
    assert files_under(root) == before


def test_the_cli_reports_the_collision_as_an_impediment(tmp_path) -> None:
    root = repo_with_example(tmp_path)
    g(root, "switch", "-q", "-c", "lane-a")
    run(root, owner="exec-a")
    commit_session(root, "session from execution A")
    g(root, "switch", "-q", "main")
    done = subprocess.run([sys.executable, str(REPO / "tools/runbook.py"), "--repo", str(root), "run", RUNBOOK],
                          capture_output=True, text=True)
    assert done.returncode == 2 and done.stderr.startswith("IMPEDIMENT")
    assert "refs/heads/lane-a" in done.stderr


def test_a_fresh_session_id_starts_normally_in_a_git_repository(tmp_path) -> None:
    root = repo_with_example(tmp_path)
    assert run(root, owner="exec-a")["status"] == "completed"


# ---------------------------------------------------------------------------
# run: resumes
# ---------------------------------------------------------------------------

def test_an_append_only_resume_is_accepted(tmp_path) -> None:
    root = repo_with_example(tmp_path)
    interrupted_run(root, owner="exec-a")
    commit = commit_session(root, "interrupted session")
    g(root, "update-ref", "refs/remotes/origin/lane-a", commit)
    before = journal(root).read_bytes()
    assert run(root)["status"] == "completed"
    after = journal(root).read_bytes()
    assert after.startswith(before) and len(after) > len(before)


def test_a_resume_behind_a_ref_that_extends_it_is_accepted(tmp_path) -> None:
    root = repo_with_example(tmp_path)
    interrupted_run(root, owner="exec-a")
    commit_session(root, "interrupted session")
    partial = journal(root).read_bytes()
    interrupted_run(root, owner="exec-a")  # appends a second interruption
    extended = commit_session(root, "interrupted twice")
    g(root, "update-ref", "refs/remotes/origin/lane-a", extended)
    g(root, "reset", "-q", "--hard", "HEAD~1")
    g(root, "clean", "-fdq")
    assert journal(root).read_bytes() == partial
    assert run(root)["status"] == "completed"


def test_a_resume_is_refused_when_a_ref_holds_an_unrelated_journal(tmp_path) -> None:
    foreign = other_execution(tmp_path, "exec-b", interrupted=True)
    root = repo_with_example(tmp_path / "root")
    interrupted_run(root, owner="exec-a")
    blob = put_journal_on_ref(root, "refs/heads/lane-b", foreign)
    local = journal(root).read_bytes()
    with pytest.raises(rb.RunbookError) as refused:
        run(root)
    message = str(refused.value)
    assert "refs/heads/lane-b" in message and blob in message
    assert "neither a prefix nor an extension" in message
    assert journal(root).read_bytes() == local


# ---------------------------------------------------------------------------
# audit: every journal chain the session path has had
# ---------------------------------------------------------------------------

def test_two_unrelated_journal_chains_in_history_are_an_audit_finding(tmp_path) -> None:
    # Execution A ran in another clone, unseen; execution B ran here.
    foreign = other_execution(tmp_path, "exec-a")
    root = repo_with_example(tmp_path / "root")
    run(root, owner="exec-b")
    commit_session(root, "session from execution B")
    blob_b = blob_of(root, "main")
    blob_a = put_journal_on_ref(root, "refs/remotes/origin/lane-a", foreign)
    report, _ = rb.audit(root, root / session_rel(root), nonce="0c", auditor="test")
    assert report["verdict"] == "flagged"
    chain_findings = [f for f in report["findings"] if "unrelated journal chain" in f]
    assert len(chain_findings) == 2
    assert any(blob_a in f and "exec-a" in f for f in chain_findings)
    assert any(blob_b in f and "exec-b" in f for f in chain_findings)
    assert {c["blob"] for c in report["journal_chains"]} == {blob_a, blob_b}
    assert all(c["first_commit"] and c["first_entry_time"] for c in report["journal_chains"])


def test_an_uncommitted_second_execution_is_a_chain_of_its_own(tmp_path) -> None:
    foreign = other_execution(tmp_path, "exec-a")
    root = repo_with_example(tmp_path / "root")
    run(root, owner="exec-b")
    put_journal_on_ref(root, "refs/heads/lane-a", foreign)
    report, _ = rb.audit(root, root / session_rel(root), nonce="0d", auditor="test")
    assert sum("unrelated journal chain" in f for f in report["findings"]) == 2
    assert any(c["first_commit"] == "working tree" for c in report["journal_chains"])


def test_an_append_only_history_is_one_chain_and_audits_clean(tmp_path) -> None:
    root = repo_with_example(tmp_path)
    interrupted_run(root, owner="exec-a")
    commit_session(root, "interrupted session")
    assert run(root)["status"] == "completed"
    commit_session(root, "resumed to completion")
    report, _ = rb.audit(root, root / session_rel(root), nonce="0e", auditor="test")
    assert report["verdict"] == "clean", report["findings"]
    assert len(report["journal_chains"]) == 1
    assert report["journal_chains"][0]["owner"] == "exec-a"


def test_two_session_started_entries_in_one_journal_are_a_finding(tmp_path) -> None:
    root = repo_with_example(tmp_path)
    run(root, owner="exec-a")
    items = rb.read_journal(journal(root))
    items.insert(1, dict(items[0]))
    previous = rb.GENESIS
    for index, entry in enumerate(items):
        entry["seq"], entry["prev"] = index, previous
        entry["hash"] = rb.entry_hash(entry)
        previous = entry["hash"]
    journal(root).write_text("".join(json.dumps(e, sort_keys=True) + "\n" for e in items))
    report, _ = rb.audit(root, root / session_rel(root), nonce="0f", auditor="test")
    assert any("2 session_started entries" in f for f in report["findings"])
