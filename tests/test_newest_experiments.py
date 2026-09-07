from __future__ import annotations

import importlib.util
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "newest_experiments", ROOT / "tools/newest_experiments.py")
mod = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(mod)


def _write_exp(root: Path, exp_id: str, *, designed_at: str,
               approved: bool = True, report: bool = False,
               has_runs: bool = False) -> None:
    d = root / "experiments" / exp_id
    d.mkdir(parents=True)
    body = {"experiment": {
        "id": exp_id,
        "status": "approved" if approved else "proposed",
        "approved_by": "coordinator" if approved else None,
        "frozen": approved,
        "execution_authorized": approved,
        "designed_at": designed_at,
    }}
    (d / "specification.yaml").write_text(yaml.safe_dump(body))
    if report:
        (d / "execution-report.yaml").write_text("execution_report: {}\n")
    if has_runs:
        # The real, universal signal this repo's own executor writes: a
        # populated runs/RUN-*/ directory. The actual execution_report.yaml
        # (underscore) lives per-batch under coordination/, not reachable
        # from the experiment directory alone -- runs/ is what _completed
        # must actually check.
        run_dir = d / "runs" / f"RUN-{exp_id.split('-', 1)[1]}-001"
        run_dir.mkdir(parents=True)
        (run_dir / "manifest.yaml").write_text("run: {}\n")


def test_newest_runnable_skips_completed_and_orders_newest(tmp_path):
    (tmp_path / "orchestration").mkdir()
    (tmp_path / "orchestration/research-priority.yaml").write_text(
        "ecc_areas: [ECDLP]\n")
    _write_exp(tmp_path, "EXP-ECDLP-old111", designed_at="2026-09-01")
    _write_exp(tmp_path, "EXP-ECDLP-new222", designed_at="2026-09-07")
    _write_exp(tmp_path, "EXP-ECDLP-done33", designed_at="2026-09-08", report=True)
    _write_exp(tmp_path, "EXP-AES-new444", designed_at="2026-09-09")
    _write_exp(tmp_path, "EXP-ECDLP-no555", designed_at="2026-09-10", approved=False)
    _write_exp(tmp_path, "EXP-ECDLP-ran666", designed_at="2026-09-11", has_runs=True)

    rows = mod.newest_runnable(tmp_path)
    assert [r["id"] for r in rows] == [
        "EXP-ECDLP-new222", "EXP-ECDLP-old111", "EXP-AES-new444"]
    assert all("specification.yaml" in r["specification"] for r in rows)


def test_newest_runnable_skips_an_experiment_with_a_populated_runs_dir(tmp_path):
    """The real convention: an executed experiment carries a non-empty
    runs/RUN-*/ directory, never a bare execution-report.yaml at its own
    top level (that file lives per-batch under coordination/, per this
    program's own convention). A tool that only checks for the latter
    silently re-lists every already-executed experiment as runnable."""
    (tmp_path / "orchestration").mkdir()
    (tmp_path / "orchestration/research-priority.yaml").write_text(
        "ecc_areas: [ECDLP]\n")
    _write_exp(tmp_path, "EXP-ECDLP-ran777", designed_at="2026-09-12", has_runs=True)

    rows = mod.newest_runnable(tmp_path)
    assert [r["id"] for r in rows] == []
