"""Generated health reports use normal review branches and fail closed."""
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import subprocess

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("publish_health", ROOT / "tools/publish_portfolio_health.py")
pub = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pub)


def git(root, *args):
    return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True,
                          text=True).stdout.strip()


@pytest.fixture
def repo(tmp_path):
    root, remote = tmp_path / "work", tmp_path / "remote.git"
    root.mkdir()
    git(root, "init", "-b", "main")
    git(root, "config", "user.name", "test")
    git(root, "config", "user.email", "test@example.invalid")
    cache = root / pub.CACHE
    cache.parent.mkdir(parents=True)
    cache.write_text("{}\n")
    (root / "source.txt").write_text("source\n")
    git(root, "add", ".")
    git(root, "commit", "-m", "source fixture")
    source = git(root, "rev-parse", "HEAD")
    git(root, "init", "--bare", str(remote))
    git(root, "remote", "add", "origin", str(remote))
    git(root, "push", "origin", "main")
    doc = {"schema": pub.SCHEMA, "commit": source, "shallow_clone": False,
           "generated_at": "2026-10-28T17:00:00+00:00", "active_goals": 1,
           "goals": [{"id": "GOAL-TEST-abcdef", "bucket": "needs_repair"}],
           "buckets": {"ready": [], "needs_repair": ["GOAL-TEST-abcdef"]}}
    cache.write_text(json.dumps(doc) + "\n")
    return root, remote, source, cache, doc


def test_source_bound_full_checkout_is_accepted(repo):
    root, _, source, cache, doc = repo
    raw, parsed = pub.validate_cache(root, source)
    assert raw == cache.read_bytes()
    assert parsed == doc


@pytest.mark.parametrize("field,value", [
    ("schema", "wrong"), ("commit", "f" * 40), ("shallow_clone", True),
    ("generated_at", "2026-10-28T17:00:00"), ("active_goals", 0),
    ("buckets", {"ready": ["GOAL-TEST-abcdef"]}),
])
def test_invalid_cache_cannot_be_published(repo, field, value):
    root, _, source, cache, doc = repo
    doc[field] = value
    cache.write_text(json.dumps(doc))
    with pytest.raises(ValueError):
        pub.validate_cache(root, source)


def test_source_must_be_current_full_commit(repo):
    root, _, source, _, _ = repo
    for bad in (source[:12], "f" * 40):
        with pytest.raises(ValueError, match="checked-out commit"):
            pub.validate_cache(root, bad)


@pytest.mark.parametrize("staged", [False, True])
def test_unrelated_tracked_change_never_enters_cache_commit(repo, staged):
    root, _, source, _, _ = repo
    (root / "source.txt").write_text("unexpected change\n")
    if staged:
        git(root, "add", "source.txt")
    with pytest.raises(ValueError):
        pub.validate_cache(root, source)
    assert git(root, "rev-parse", "HEAD") == source


def test_symlink_cache_is_rejected(repo):
    root, _, source, cache, _ = repo
    target = root / "external-cache"
    cache.rename(target)
    cache.symlink_to(target)
    with pytest.raises(ValueError, match="ordinary file"):
        pub.validate_cache(root, source)


def test_sparse_checkout_is_rejected(repo):
    root, _, source, _, _ = repo
    git(root, "config", "core.sparseCheckout", "true")
    with pytest.raises(ValueError, match="full checkout"):
        pub.validate_cache(root, source)


def test_shallow_checkout_is_rejected(repo, tmp_path):
    root, remote, source, _, _ = repo
    shallow = tmp_path / "shallow"
    git(root, "clone", "--depth", "1", "--branch", "main", remote.as_uri(), str(shallow))
    with pytest.raises(ValueError, match="full history"):
        pub.validate_cache(shallow, source)


def fake_pr(monkeypatch, *, fail=False):
    original = pub.command
    seen = []
    def invoke(root, *args):
        if args[0] != "gh":
            return original(root, *args)
        seen.append((args, Path(args[args.index("--body-file") + 1]).read_text()))
        if fail:
            raise subprocess.CalledProcessError(1, args, stderr="PR creation denied")
        return "https://github.com/example/repo/pull/7"
    monkeypatch.setattr(pub, "command", invoke)
    return seen


def publish(repo):
    root, _, source, _, _ = repo
    return pub.publish(root, source=source, repository="example/repo", run_id="123", run_attempt="1")


def test_real_git_publication_changes_only_cache_and_leaves_main_untouched(repo, monkeypatch):
    root, remote, source, cache, _ = repo
    raw = cache.read_text()
    seen = fake_pr(monkeypatch)
    receipt = publish(repo)
    assert receipt["state"] == "pull_request_open"
    assert git(remote, "rev-parse", "main") == source
    assert git(remote, "rev-parse", receipt["branch"]) == receipt["commit"]
    assert git(remote, "show", f'{receipt["branch"]}:{pub.CACHE}') == raw.strip()
    assert git(remote, "diff", "--name-only", source, receipt["commit"]) == pub.CACHE
    assert git(remote, "rev-parse", receipt["commit"] + "^1") == source
    args, body = seen[0]
    assert args[:3] == ("gh", "pr", "create")
    assert args[args.index("--base") + 1] == "main"
    assert source in body and receipt["cache_sha256"] in body
    assert "does not mean the absolute sweep passed" in body


def test_api_failure_retains_branch_but_is_fatal(repo, monkeypatch, capsys):
    root, remote, source, _, _ = repo
    fake_pr(monkeypatch, fail=True)
    with pytest.raises(subprocess.CalledProcessError):
        publish(repo)
    receipts = [json.loads(line) for line in capsys.readouterr().out.splitlines()]
    assert [r["state"] for r in receipts] == ["prepared", "branch_pushed"]
    assert git(remote, "rev-parse", "main") == source
    assert git(remote, "rev-parse", receipts[-1]["branch"]) == receipts[-1]["commit"]


def test_existing_publication_branch_is_not_replaced_or_duplicated(repo, monkeypatch):
    root, remote, source, cache, _ = repo
    raw = cache.read_text()
    seen = fake_pr(monkeypatch)
    receipt = publish(repo)
    git(root, "checkout", "--detach", source)
    cache.write_text(raw)
    with pytest.raises(ValueError, match="already exists; reconcile"):
        publish(repo)
    assert len(seen) == 1
    assert git(remote, "rev-parse", receipt["branch"]) == receipt["commit"]
    assert git(root, "rev-parse", "HEAD") == source


def test_only_nonempty_cache_only_diff_suppresses_a_sweep(repo):
    root, _, _, _, _ = repo
    git(root, "add", pub.CACHE)
    git(root, "commit", "-m", "cache only")
    assert pub.cache_only_merge(root)
    git(root, "commit", "--allow-empty", "-m", "empty")
    assert not pub.cache_only_merge(root)
    (root / "source.txt").write_text("new source\n")
    git(root, "add", "source.txt")
    git(root, "commit", "-m", "source")
    assert not pub.cache_only_merge(root)
    git(root, "mv", pub.CACHE, "cache-renamed.json")
    git(root, "commit", "-m", "cache rename")
    assert not pub.cache_only_merge(root)


def test_missing_parent_is_an_error_not_an_empty_scope(repo):
    root, _, _, _, _ = repo
    with pytest.raises(subprocess.CalledProcessError):
        pub.cache_only_merge(root)


def test_workflow_scope_forces_manual_sweep_and_rejects_missing_history(repo, tmp_path):
    root, _, _, _, _ = repo
    # Exercise the actual workflow shell with the helper materialized into the
    # tiny fixture; an unavailable parent must not emit run_sweep=false.
    tool = root / "tools/publish_portfolio_health.py"
    tool.parent.mkdir()
    tool.write_text((ROOT / "tools/publish_portfolio_health.py").read_text())
    workflow = yaml.safe_load((ROOT / ".github/workflows/main-health.yml").read_text())
    step = next(s for s in workflow["jobs"]["scope"]["steps"] if s.get("id") == "scope")
    out = tmp_path / "output"
    def run(event):
        out.write_text("")
        return subprocess.run(["bash", "-e", "-o", "pipefail", "-c", step["run"]], cwd=root,
                              env={**os.environ, "EVENT_NAME": event, "GITHUB_OUTPUT": str(out)},
                              capture_output=True, text=True)
    assert run("pull_request_target").returncode != 0
    assert out.read_text() == ""
    assert run("workflow_dispatch").returncode == 0
    assert out.read_text() == "run_sweep=true\n"
    git(root, "add", pub.CACHE)
    git(root, "commit", "-m", "cache")
    assert run("pull_request_target").returncode == 0
    assert out.read_text() == "run_sweep=false\n"
    (root / "source.txt").write_text("new source\n")
    git(root, "add", "source.txt")
    git(root, "commit", "-m", "source")
    assert run("pull_request_target").returncode == 0
    assert out.read_text() == "run_sweep=true\n"


def test_workflow_retains_artifact_without_automatic_publication():
    workflow = yaml.safe_load((ROOT / ".github/workflows/main-health.yml").read_text())
    job = workflow["jobs"]["absolute-sweep"]
    steps = job["steps"]
    archive = next(i for i, s in enumerate(steps) if s.get("id") == "health_archive")
    assert "steps.health_cache.outcome == 'success'" in steps[archive]["if"]
    assert all("tools/publish_portfolio_health.py" not in s.get("run", "") for s in steps)
    assert job["permissions"] == {"contents": "read", "issues": "write"}
    assert "HEAD:main" not in json.dumps(workflow)
    assert job["needs"] == "scope"
