"""FX-A (AMD-20260929-143d11): descriptive incremental-R_j figure.

PYTEST_DONT_REWRITE (v4b A-3): this module evaluates frozen fixtures, so assertion
rewriting is disabled and a failing assert reports no compared values."""

import copy
import json

import pytest

import analysis
import common
import pipeline
from test_analysis import synth


def dbl_add_ops(k: int) -> int:
    """Right-to-left double-and-add on a prime-order point, k in [1, q): the
    first set bit is free (R = O), each further set bit one addition, each
    shift but the last one doubling -- absent an accidental R = +-Qp."""
    return (bin(k).count("1") - 1) + (k.bit_length() - 1) if k else 0


def test_closed_form_on_tiny_case():
    assert dbl_add_ops(1) == 0 and dbl_add_ops(5) == 3 and dbl_add_ops(8) == 3 and dbl_add_ops(7) == 4
    fx = common.fixture(16, 21)
    from arith import Cost, Curve, Fp
    G = tuple(fx["G"])
    for k in (1, 5, 8, 7, 12345):
        c = Cost()
        Curve(Fp(fx["p"], c), fx["a"], fx["b"]).mul(k, G)
        assert c.pt_add + c.pt_dbl == dbl_add_ops(k)


def _fake_primary(n_attempts=3, pt_ops=1000, complete=10 ** 7):
    fx = common.fixture(16, 21)
    ns = common.SMOKE_NS + "|tests-fxa"
    from verify import VCurve
    Q = VCurve(fx["p"], fx["a"], fx["b"]).mul(pipeline.target_k(fx, ns), tuple(fx["G"]))
    return {"fixture": fx, "namespace": ns, "target": {"Q": list(Q)}, "complete_units": complete,
            "stage1": {"attempt_log": {"member_bits": "0" * n_attempts, "pt_ops": [pt_ops] * n_attempts}},
            "descents": {"targets": []}}


def test_fxa_matches_closed_form_on_tiny_receipt():
    r = _fake_primary()
    f = analysis.fxa_figure(r)
    exp_excess = 0
    for j in range(3):
        a, b = pipeline.attempt_ab(r["fixture"], r["namespace"], j)
        exp_excess += dbl_add_ops(a) + dbl_add_ops(b) + 1 - 1
    assert f["rj_stage1_excess_ops"] == exp_excess
    assert f["complete_units_rj_incremental"] == r["complete_units"] - 13 * exp_excess
    assert f["ratio_rj_incremental_nonverdict"] == pytest.approx(
        f["complete_units_rj_incremental"] / (13 * 0.886 * r["fixture"]["N"] ** 0.5))


def test_fxa_cross_check_failure_is_a_procedure_defect():
    r = _fake_primary(pt_ops=5)  # far below any R_j double-and-add count
    with pytest.raises(pipeline.ProcedureDefect):
        analysis.fxa_figure(r)


def test_fxa_on_smoke_primary(smoke_primary):
    r = json.loads(json.dumps(smoke_primary))
    f = analysis.fxa_figure(r)
    n = r["stage1"]["n_attempts"]
    assert f["rj_stage1_attempts"] == n and f["rj_stage1_excess_ops"] > 0
    assert f["complete_units_rj_incremental"] < r["complete_units"]
    assert f["complete_units_rj_incremental_with_descents"] < f["complete_units_rj_incremental"]
    assert f["rj_descent_attempts"] == sum(t["attempts"] for t in r["descents"]["targets"])
    bad = copy.deepcopy(r)
    bad["stage1"]["attempt_log"]["pt_ops"][0] = 1
    with pytest.raises(pipeline.ProcedureDefect):
        analysis.fxa_figure(bad)
    bad = copy.deepcopy(r)
    bad["descents"]["targets"][0]["attempt_log"]["pt_ops"][0] = 1
    with pytest.raises(pipeline.ProcedureDefect):
        analysis.fxa_figure(bad)


@pytest.mark.parametrize("expo,c", [(0.3, 1.0), (0.8, 1.0), (0.5, 1.0), (0.3, 1e6)])
def test_verdict_unchanged_by_fxa(expo, c):
    prim = synth(expo, c)
    base = analysis.analyse(prim, fxa=None)
    for r in prim:
        r["stage1"] = {}

    def extreme(r):  # an FX-A figure that would flip any verdict if it were read
        return {"complete_units_rj_incremental": 1e-9, "ratio_rj_incremental_nonverdict": 1e-12}
    with_fxa = analysis.analyse(prim, fxa=extreme)
    for k in ("verdict", "exponent", "exponent_bootstrap", "dominant_stage_20bit", "pooled_units_20bit"):
        assert with_fxa[k] == base[k]
    assert [p["ratio"] for p in with_fxa["per_fixture"]] == [p["ratio"] for p in base["per_fixture"]]
    assert all(p["ratio_rj_incremental_nonverdict"] == 1e-12 for p in with_fxa["per_fixture"])
    assert all(p["fxa_nonverdict"] is None for p in base["per_fixture"])
