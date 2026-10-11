"""Sparse checkouts against real git: profile rules, and the tools that must not
mistake "off disk" for "not in the repository" (docs/sparse-checkout.md)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import experiment_execution as execution  # noqa: E402
import newest_experiments as selector  # noqa: E402
import sparse_checkout as sc  # noqa: E402

PLANNED = "EXP-ECDLP-aaaaaa"   # has a trial plan: its runs/ decide coverage
LEGACY = "EXP-ECDLP-bbbbbb"    # runs without a plan: needs reconciliation
FRESH = "EXP-ECDLP-cccccc"     # nothing run yet
GOAL = "GOAL-ECDLP-dddddd"


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], check=True,
                          capture_output=True, text=True).stdout


def _spec(exp_id: str, **extra) -> str:
    body = {"id": exp_id, "status": "approved", "approved_by": "coordinator",
            "frozen": True, "execution_authorized": True,
            "designed_at": "2026-10-01", **extra}
    lines = ["experiment:"] + [f"  {k}: {json.dumps(v)}" for k, v in body.items()]
    return "\n".join(lines) + "\n"


def _write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


@pytest.fixture()
def origin(tmp_path: Path) -> Path:
    root = tmp_path / "origin"
    root.mkdir()
    _git(root, "init", "-q", "-b", "main")
    _write(root, "README.md", "top\n")
    _write(root, "tools/x.py", "pass\n")
    _write(root, "orchestration/research-priority.yaml", "ecc_areas: [ECDLP]\n")
    _write(root, f"experiments/{PLANNED}/specification.yaml",
           _spec(PLANNED, goal_id=GOAL, inputs=["inputs/refs/paper-x/table.csv"]))
    _write(root, f"experiments/{PLANNED}/trial-plan.json", "{}\n")
    _write(root, f"experiments/{PLANNED}/runs/RUN-ECDLP-111111/raw-result.json", "{}\n")
    _write(root, f"experiments/{LEGACY}/specification.yaml", _spec(LEGACY))
    _write(root, f"experiments/{LEGACY}/runs/RUN-ECDLP-222222/manifest.yaml", "run: {}\n")
    _write(root, f"experiments/{FRESH}/specification.yaml", _spec(FRESH))
    _write(root, "inputs/refs/paper-x/table.csv", "a,b\n")
    _write(root, "inputs/refs/other/blob.bin", "x" * 4096)
    _write(root, "research/cold_ic_20260921/out.json", "{}\n")
    _write(root, "research/warm/notes.md", "kept\n")
    _git(root, "add", "-A")
    _git(root, "-c", "user.email=t@example.com", "-c", "user.name=t", "commit", "-qm", "init")
    for n in range(3):
        _write(root, "README.md", f"top {n}\n")
        _git(root, "-c", "user.email=t@example.com", "-c", "user.name=t",
             "commit", "-qam", f"c{n}")
    _git(root, "config", "uploadpack.allowFilter", "true")
    _git(root, "config", "uploadpack.allowAnySHA1InWant", "true")
    return root


@pytest.fixture()
def clone(origin: Path, tmp_path: Path) -> Path:
    repo = tmp_path / "clone"
    subprocess.run(["git", "clone", "-q", f"file://{origin}", str(repo)], check=True)
    sc._clear_caches()
    yield repo
    sc._clear_caches()


def _on_disk(repo: Path) -> set[str]:
    return {p.relative_to(repo).as_posix() for p in repo.rglob("*")
            if p.is_file() and ".git" not in p.relative_to(repo).parts}


def test_full_checkout_reports_nothing_absent(clone: Path):
    assert not sc.is_sparse(clone)
    assert sc.tracked_absent(clone, "experiments/") == []
    assert sc.outside_definition(clone, ["experiments/X/runs/R/f"]) == []
    assert sc.read_state(clone) is None


def test_harness_profile_drops_archives_and_keeps_planned_runs(clone: Path):
    info = sc.apply(clone, "harness")
    disk = _on_disk(clone)
    assert f"experiments/{PLANNED}/runs/RUN-ECDLP-111111/raw-result.json" in disk
    assert f"experiments/{LEGACY}/specification.yaml" in disk
    assert f"experiments/{LEGACY}/runs/RUN-ECDLP-222222/manifest.yaml" not in disk
    assert not any(p.startswith(("inputs/refs/", "research/cold_")) for p in disk)
    assert "research/warm/notes.md" in disk and "tools/x.py" in disk
    assert info["profile"] == "harness" and info["skipped_files"] == 4
    assert sc.tracked_absent(clone, f"experiments/{LEGACY}/runs/") == [
        f"experiments/{LEGACY}/runs/RUN-ECDLP-222222/manifest.yaml"]
    # `git add` would refuse a new run here, so the runner must know.
    assert sc.outside_definition(clone, [
        f"experiments/{LEGACY}/runs/RUN-new/x", f"experiments/{PLANNED}/runs/RUN-new/x"]) == [
        f"experiments/{LEGACY}/runs/RUN-new/x"]


def test_add_experiment_materializes_it_and_the_inputs_it_names(clone: Path):
    sc.apply(clone, "harness")
    assert main(clone, "add", "--experiment", PLANNED) == 0
    disk = _on_disk(clone)
    assert "inputs/refs/paper-x/table.csv" in disk
    assert "inputs/refs/other/blob.bin" not in disk
    assert sc.read_state(clone)["experiments"] == [PLANNED]
    # A second addition keeps the first.
    assert main(clone, "add", "--experiment", LEGACY) == 0
    assert sc.read_state(clone)["experiments"] == [PLANNED, LEGACY]
    assert f"experiments/{LEGACY}/runs/RUN-ECDLP-222222/manifest.yaml" in _on_disk(clone)


def test_goal_selects_its_experiments(clone: Path):
    sc.apply(clone, "harness")
    assert sc.goal_experiments(clone, GOAL) == [PLANNED]


def test_disable_restores_everything(clone: Path):
    sc.apply(clone, "harness")
    assert main(clone, "disable") == 0
    assert not sc.is_sparse(clone)
    assert "inputs/refs/other/blob.bin" in _on_disk(clone)


def test_patterns_change_nothing(clone: Path, capsys):
    assert main(clone, "patterns", "harness", "--experiment", FRESH) == 0
    out = capsys.readouterr().out
    assert "!/experiments/*/runs/" in out and f"/experiments/{FRESH}/" in out
    assert not sc.is_sparse(clone)


def test_unknown_experiment_id_is_refused(clone: Path):
    with pytest.raises(sc.SparseError):
        sc.render(clone, "harness", ["not-an-id"])


def test_selector_still_sees_legacy_runs_left_off_disk(clone: Path):
    full = {r["id"]: r["execution_state"]
            for r in selector.newest_runnable(clone, include_blocked=True, off_main={})}
    sc.apply(clone, "harness")
    sparse = {r["id"]: r["execution_state"]
              for r in selector.newest_runnable(clone, include_blocked=True, off_main={})}
    assert sparse[LEGACY] == full[LEGACY] == "needs_reconciliation"
    assert sparse[FRESH] == full[FRESH] == "needs_implementation_or_plan"


def test_off_disk_trial_run_is_not_planned_and_blocks_a_launch(clone: Path, monkeypatch):
    plan = {"experiment_id": PLANNED, "specification": f"experiments/{PLANNED}/specification.yaml",
            "trials": [{"id": "t1", "run_id": "RUN-ECDLP-111111"},
                       {"id": "t2", "run_id": "RUN-ECDLP-333333"}]}
    _git(clone, "sparse-checkout", "set", "--no-cone", "/*", "!/experiments/*/runs/")
    sc._clear_caches()
    assert execution.trial_state(clone, plan, plan["trials"][0], "0" * 64) == "not_materialized"
    assert execution.trial_state(clone, plan, plan["trials"][1], "0" * 64) == "planned"
    with pytest.raises(execution.ExecutionError, match="sparse_checkout.py add --experiment"):
        execution.materialized(clone, plan)
    sc.apply(clone, "harness")
    execution.materialized(clone, plan)  # plan experiments are in the harness profile


def test_selector_marks_an_unknowable_plan_as_needing_materialization(clone: Path, monkeypatch):
    report = {"measurement_complete": False, "planned": 1, "not_materialized": 1}
    monkeypatch.setattr(selector, "coverage", lambda repo, plan: report)
    progress = selector.execution_progress(clone / "experiments" / PLANNED, clone)
    assert progress["execution_state"] == "needs_materialization"
    assert f"add --experiment {PLANNED}" in progress["reason"]


def test_id_allocator_sees_identifiers_left_off_disk(clone: Path, monkeypatch):
    import allocate_id
    monkeypatch.setattr(allocate_id, "REPO", str(clone))
    sc.apply(clone, "harness")
    names = {Path(p).name for p in allocate_id._identifier_paths()}
    assert "RUN-ECDLP-222222" in names  # only in the skip-worktree index


def test_blobless_clone_downloads_only_the_profile(origin: Path, tmp_path: Path):
    repo = tmp_path / "partial"
    info = sc.clone(f"file://{origin}", repo, branch=None, profile="harness",
                    experiments=[LEGACY], paths=[])
    assert info["partial_clone_filter"] == "blob:none"
    assert f"experiments/{LEGACY}/runs/RUN-ECDLP-222222/manifest.yaml" in _on_disk(repo)
    assert "inputs/refs/other/blob.bin" not in _on_disk(repo)
    missing = _git(repo, "rev-list", "--objects", "--all", "--missing=print")
    assert sum(1 for line in missing.splitlines() if line.startswith("?")) >= 4


def test_deepen_fetches_history_without_blobs(origin: Path, tmp_path: Path):
    repo = tmp_path / "shallow"
    subprocess.run(["git", "clone", "-q", "--depth", "1", f"file://{origin}", str(repo)], check=True)
    ok, detail = sc.deepen(repo)
    assert ok and "blob:none" in detail
    assert _git(repo, "rev-parse", "--is-shallow-repository").strip() == "false"
    assert len(_git(repo, "log", "--oneline").splitlines()) == 4
    assert sc.deepen(repo) == (True, "not shallow")


def main(repo: Path, *argv: str) -> int:
    sc._clear_caches()
    try:
        return sc.main(["--repo", str(repo), *argv])
    finally:
        sc._clear_caches()


def test_a_named_directory_reincludes_excluded_subtrees_beneath_it(clone: Path):
    assert sc._include("harness", f"experiments/{LEGACY}/") == [
        f"/experiments/{LEGACY}/", f"/experiments/{LEGACY}/runs/"]
    assert sc._include("harness", "inputs/") == ["/inputs/", "/inputs/refs/",
        "/inputs/archive_from_autolab/", "/inputs/pqshield-signature-zoo-20260928/"]
    assert sc._include("harness", "inputs/refs/a.csv") == ["/inputs/refs/a.csv"]
    sc.apply(clone, "harness", paths=["research/"])
    assert "research/cold_ic_20260921/out.json" in _on_disk(clone)


def test_whole_repository_sweeps_refuse_a_sparse_checkout(clone: Path, monkeypatch, capsys):
    assert not sc.refuse_if_sparse("validate_ledger", clone)
    sc.apply(clone, "harness")
    monkeypatch.delenv("CRYPTO_AR_ALLOW_SPARSE", raising=False)
    assert sc.refuse_if_sparse("validate_ledger", clone)
    assert "refused in a sparse checkout" in capsys.readouterr().err
    monkeypatch.setenv("CRYPTO_AR_ALLOW_SPARSE", "1")
    assert not sc.refuse_if_sparse("validate_ledger", clone)
