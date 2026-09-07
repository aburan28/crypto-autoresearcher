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
               approved: bool = True, report: bool = False) -> None:
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


def test_newest_runnable_skips_completed_and_orders_newest(tmp_path, monkeypatch):
    (tmp_path / "orchestration").mkdir()
    (tmp_path / "orchestration/research-priority.yaml").write_text(
        "ecc_areas: [ECDLP]\n")
    _write_exp(tmp_path, "EXP-ECDLP-old111", designed_at="2026-09-01")
    _write_exp(tmp_path, "EXP-ECDLP-new222", designed_at="2026-09-07")
    _write_exp(tmp_path, "EXP-ECDLP-done33", designed_at="2026-09-08", report=True)
    _write_exp(tmp_path, "EXP-AES-new444", designed_at="2026-09-09")
    _write_exp(tmp_path, "EXP-ECDLP-no555", designed_at="2026-09-10", approved=False)

    rows = mod.newest_runnable(tmp_path)
    assert [r["id"] for r in rows] == [
        "EXP-ECDLP-new222", "EXP-ECDLP-old111", "EXP-AES-new444"]
    assert all("specification.yaml" in r["specification"] for r in rows)
