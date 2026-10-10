"""Sparse CI shards: the guard sees off-disk reads, and CI's rules are the profile's."""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
import ci_sparse_guard as guard  # noqa: E402
import ci_test_shard  # noqa: E402
import sparse_checkout  # noqa: E402

RULES = "/*\n!/experiments/*/runs/\n!/inputs/refs/\n!/research/cold_*/\n"


def test_off_disk_matches_excluded_paths_and_globs_only():
    ex = guard.exclusions(RULES)
    assert guard.off_disk("experiments/EXP-A/runs/RUN-1/manifest.yaml", ex)
    assert guard.off_disk("experiments/EXP-A/runs", ex)
    assert guard.off_disk("experiments/*/runs/*/manifest.yaml", ex)  # a glob over runs
    assert guard.off_disk("research/cold_ic_20260921/out.json", ex)
    assert not guard.off_disk("experiments/EXP-A/specification.yaml", ex)
    assert not guard.off_disk("experiments/*/specification.yaml", ex)
    assert not guard.off_disk("experiments/EXP-A", ex)
    assert not guard.off_disk("inputs/other/x", ex)


def test_tripwires_are_the_skeleton_of_excluded_directories_that_held_files():
    # A test that checks a run directory exists (and skips if it does) must see
    # what it sees on a full checkout -- tests/test_sgcp_embed.py does exactly that.
    ex = guard.exclusions(RULES)
    skipped = ["experiments/EXP-A/runs/R1/m.yaml", "experiments/EXP-A/runs/R2/sub/m.yaml",
               "inputs/refs/paper/t.csv", "research/cold_x/out.json"]
    assert guard.tripwire_dirs(skipped, ex) == [
        "experiments/EXP-A/runs", "experiments/EXP-A/runs/R1", "experiments/EXP-A/runs/R2",
        "experiments/EXP-A/runs/R2/sub", "inputs/refs", "inputs/refs/paper", "research/cold_x"]


def test_hook_logs_reads_and_listings_inside_excluded_directories(tmp_path: Path):
    root = tmp_path / "repo"
    (root / "experiments/EXP-A/runs").mkdir(parents=True)   # a tripwire
    (root / "experiments/EXP-A/specification.yaml").write_text("x: 1\n")
    rules, log = tmp_path / "rules", tmp_path / "log"
    rules.write_text(RULES)
    probe = (
        "import os, glob\n"
        "open('experiments/EXP-A/specification.yaml').read()\n"
        "os.listdir('experiments/EXP-A/runs')\n"
        "glob.glob('experiments/*/runs/*/manifest.yaml')\n"
        "try:\n    open('experiments/EXP-A/runs/R1/manifest.yaml')\n"
        "except FileNotFoundError:\n    pass\n")
    env = {**os.environ, "PYTHONPATH": str(REPO / "tools" / "sparse_guard_site"),
           "CI_SPARSE_GUARD_ROOT": str(root), "CI_SPARSE_GUARD_RULES": str(rules),
           "CI_SPARSE_GUARD_LOG": str(log), "PYTEST_CURRENT_TEST": "tests/test_x.py::t (call)"}
    subprocess.run([sys.executable, "-c", probe], cwd=root, env=env, check=True)
    entries = [line.split("\t") for line in log.read_text().splitlines()]
    logged = {(e[1], e[2]) for e in entries}
    assert {("os.listdir", "experiments/EXP-A/runs"),
            ("glob.glob", "experiments/*/runs/*/manifest.yaml"),
            ("open", "experiments/EXP-A/runs/R1/manifest.yaml")} <= logged
    assert not any("specification.yaml" in path for _, path in logged)
    assert all(e[0] == "tests/test_x.py::t" for e in entries)
    assert guard.main(["report", str(log)]) == 1
    assert guard.main(["report", str(tmp_path / "absent")]) == 0


def test_ci_sparse_rules_are_the_harness_profile_exclusions():
    """validate.yml's SPARSE_RULES must not drift from tools/sparse_checkout.py."""
    workflow = yaml.safe_load((REPO / ".github/workflows/validate.yml").read_text())
    rules = workflow["env"]["SPARSE_RULES"].split()
    assert rules == ["/*"] + [f"!{r}" for r in sparse_checkout.PROFILES["harness"]["exclude"]]


def test_full_checkout_list_names_existing_test_files_pinned_to_shard_one():
    full = ci_test_shard.load_full_checkout()
    assert full and all((REPO / f).is_file() and re.search(r"/test_[^/]+\.py$", f) for f in full)
    files = full + [f"tests/test_extra_{i}.py" for i in range(40)]
    shards = ci_test_shard.plan(files, 4, {f: 5.0 for f in files}, full)
    assert set(full) <= set(shards[ci_test_shard.FULL_SHARD - 1])
    assert not set(full) & set(f for s in shards[1:] for f in s)
    assert sorted(f for s in shards for f in s) == sorted(files)
