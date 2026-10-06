import json
import math

import pytest

import analysis


def cell(bits, seed, dp, er_dp, giant=0.5, cr=None, cyc=1, ns="EXP-RELN-c5a377/v2"):
    L = 6
    cr = cr if cr is not None else (round(L ** (dp + 1)) if dp is not None else 0)

    def blk(bu):
        return {"budget": bu,
                "graph": {"delta_proof": dp, "delta_ratio": None, "cycle_rank": cr, "E": 100, "V": 50,
                          "giant_component_fraction": giant, "components_with_cycle": cyc},
                "null_er": {"replicates": [{"delta_proof": er_dp}] * 32},
                "null_rewire": {"replicates": [{"delta_proof": er_dp}] * 32},
                "recovery": {"lp_recovery_fraction": 0.5},
                "charged": {"charged_work_over_sqrt_q": 10.0}}
    return {"fixture_id": f"b{bits}-s{seed}", "fixture": {"bits": bits, "seed": seed}, "ns": ns,
            "budgets": [blk("A1"), blk("A2")]}


def grid(f):
    return [f(b, s) for b in (16, 20, 24) for s in (11, 12, 13)]


def test_supercritical_when_er_low():
    cells = grid(lambda b, s: cell(b, s, 0.6 + 0.01 * (s - 12) + 0.001 * b, 0.1))
    v = analysis.verdict(cells)
    assert v["verdict"] == "supercritical-enriched"
    assert "definitional_impediment" in v


def test_er_also_exceeding_gives_inconclusive():
    cells = grid(lambda b, s: cell(b, s, 0.6 + 0.01 * (s - 12), 0.5))
    v = analysis.verdict(cells)
    assert v["verdict"] == "inconclusive"
    assert v["clauses"]["er_null_exceeds_quarter_in_any_cell"]


def test_falling_trend_blocks_supercritical():
    cells = grid(lambda b, s: cell(b, s, 3.0 - 0.1 * b + 0.001 * (s - 12), 0.0))
    v = analysis.verdict(cells)
    assert not v["clauses"]["trend_flat_or_rising_both_budgets"]
    assert v["verdict"] != "supercritical-enriched"


def test_wide_ci_blocks_supercritical():
    cells = grid(lambda b, s: cell(b, s, {11: 0.3, 12: 1.2, 13: 0.26}[s], 0.0))
    assert analysis.verdict(cells)["verdict"] != "supercritical-enriched"


def test_undefined_delta_fails_ci():
    cells = grid(lambda b, s: cell(b, s, None if (b, s) == (20, 12) else 0.8, 0.0))
    assert not analysis.verdict(cells)["clauses"]["ci_gt_quarter_all_cells"]


def test_certified_subcritical():
    cells = grid(lambda b, s: cell(b, s, None, None, giant=0.01, cr=2, cyc=1))
    v = analysis.verdict(cells)
    assert v["verdict"] == "certified-subcritical"


def test_subcritical_needs_every_fixture():
    cells = grid(lambda b, s: cell(b, s, None, None, giant=0.01 if b < 24 else 0.2, cr=2, cyc=1))
    assert analysis.verdict(cells)["verdict"] == "inconclusive"


def test_missing_cells_inconclusive():
    cells = grid(lambda b, s: cell(b, s, 0.8, 0.0))[:-1]
    assert analysis.verdict(cells)["verdict"] == "inconclusive"


def test_lower_ci_value():
    vals = [1.0, 2.0, 3.0]
    assert analysis.lower_ci(vals) == pytest.approx(2.0 - 4.302652729911275 / math.sqrt(3))


def test_main_refuses_smoke(tmp_path):
    p = tmp_path / "raw.json"
    p.write_text(json.dumps({"cells": grid(lambda b, s: cell(b, s, 0.8, 0.0, ns="smoke|x"))}))
    assert analysis.main([str(p)]) == 2
