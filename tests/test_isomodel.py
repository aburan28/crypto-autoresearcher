"""Isogenous-model screen: routes through a neighbour reproduce k*P, and the instrument sees a known gain."""
import pytest

pytest.importorskip("flint")

from harness.endosweep import isomodel as IM  # noqa: E402
from harness.endosweep.targets import deployed_targets, verify  # noqa: E402


def _row(T, **kw):
    args = dict(ells=[2, 3, 5, 7], depth=1, max_nodes=16, disc_bound=1 << 12, samples=20, verify_scalars=3, seed=1)
    args.update(kw)
    return IM.screen_curve(T, **args)


def test_ascent_control_fires_and_route_verifies():
    T, info = IM.ascent_control(64, [2, 3, 5, 7], seed=3)
    assert T is not None and T.verified
    r = _row(T)
    assert r["ascent"]["D_K"] == -3
    assert r["ascent"]["glv_on_reached_crater"] is not None          # the walk reaches j = 0
    if r["verification"] is not None:
        assert r["verification"]["ok"], r["verification"]
    assert r["instrument_check"]["pass"]


def test_a_minus_3_curve_has_no_model_gain():
    p256 = next(verify(t) for t in deployed_targets() if t.name == "NIST P-256")
    r = _row(p256, ells=[3, 5], verify_scalars=0)
    assert r["baseline"]["kind"] == "weierstrass"
    assert r["best"] is None or r["best"]["persistent_gain"] <= 0     # already on the cheapest Weierstrass class
    assert r["instrument_check"]["order_odd"] and r["instrument_check"]["pass"]


def test_positive_control_recovers_the_a_minus_3_source():
    p256 = next(verify(t) for t in deployed_targets() if t.name == "NIST P-256")
    T = IM.positive_control([p256], [3, 5])
    assert T is not None
    r = _row(T, ells=[3, 5])
    assert r["best"]["persistent_gain"] > 0
    assert r["verification"]["ok"], r["verification"]
