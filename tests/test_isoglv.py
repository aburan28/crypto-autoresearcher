"""Combined route: controls behave as frozen (GLV on a reached crater; no invented gain on an a = -3 curve)."""
import json
from pathlib import Path

import pytest

pytest.importorskip("flint")

from harness.endosweep import isoglv as IG  # noqa: E402

ROWS = Path(__file__).resolve().parents[1] / "experiments/EXP-ENDO-25ad84/runs/RUN-ENDO-d7cb69/raw-result.json"
KW = dict(ells=[2, 3, 5, 7, 11, 13], depth=2, max_nodes=64, disc_bound=2_000_000, build_limit=1,
          build_seconds=300, max_candidates=3, verify_scalars=2, seed=1)


def _row(name):
    return next(r for r in json.loads(ROWS.read_text())["rows"] if r["name"] == name)


def test_ascent_control_prices_glv_on_the_crater():
    r = IG.screen(_row("control+ascent: 11-descendant of a j = 0 curve (256-bit)"), **KW)
    assert r["D_K"] == -3 and r["combined"] is not None
    assert r["combined"]["route_verification"]["ok"]
    assert r["combined_vs_E_model_baseline"]["oneshot_gain"] > 0


def test_a_minus_3_curve_has_no_cheaper_neighbour():
    r = IG.screen(_row("mnt/mnt5/1"), **KW)
    assert r["glv_on_E"]["ok"] and r["candidates_cheaper_class"] == 0 and r["combined"] is None
