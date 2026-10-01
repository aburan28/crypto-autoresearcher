"""Controls behave as specified (C-6): known-false scramble, random-x null,
rho baseline, stage-2 scan agreement; certificates verified.

PYTEST_DONT_REWRITE (v4b A-3): this module evaluates frozen fixtures, so assertion
rewriting is disabled and a failing assert reports no compared values."""

import b0
import common
import pipeline
import rho
from verify import VCurve

FX = common.fixture(16, 21)
NS = common.SMOKE_NS + "|tests"


def test_primary_identities(smoke_primary):
    r = smoke_primary
    assert r["stage3"]["log_verification"]["all_ok"]
    assert r["stage3"]["agrees_dense_reference"]
    assert r["stage3"]["k_recovered"] == r["target"]["k"]
    assert r["descents"]["n_verified"] == r["descents"]["n_descents"] == 2
    assert r["stage1"]["n_relations"] >= r["factor_base"]["L"] + 1 + common.EXCESS_ROWS
    assert r["stage2_alpha2"]["agreement_with_brute_force"] == r["stage2_alpha2"]["n_heldout"]


def test_known_false_scramble_fails_verification(smoke_primary):
    kf = smoke_primary["known_false"]
    assert kf["rows_changed"] > 0
    assert kf["log_verification_all_ok"] is False
    assert kf["control_passed"] is True


def test_known_false_detects_a_pipeline_that_accepts_scrambled_rows(smoke_primary, monkeypatch):
    """Proves-too-much check of the control itself: if the 'scramble' were the
    identity, the solve would verify and the control must report failure."""
    rels = smoke_primary["stage1"]["relations"]
    fb = b0.interval_fb(FX, 5)
    Q = tuple(smoke_primary["target"]["Q"])

    def identity_scramble(fx, ns, relations, fbkind, L):
        return list(range(len(relations))), 0, [{"a": r["a"], "row_scrambled": r["row"]} for r in relations]
    monkeypatch.setattr(pipeline, "scramble", identity_scramble)
    kf = pipeline.known_false(FX, NS, fb, rels, Q)
    assert kf["log_verification_all_ok"] is True and kf["control_passed"] is False


def test_random_fb_null_matched_size_and_distinct():
    ifb = b0.interval_fb(FX, 5)
    rfb = b0.random_fb(FX, NS, ifb.L, ifb.B)
    vc = VCurve(FX["p"], FX["a"], FX["b"])
    assert rfb.L == ifb.L and len(set(rfb.V)) == rfb.L
    assert all(vc.liftable(x) for x in rfb.V)
    assert rfb.cost["units"] > 0 and rfb.draws >= rfb.L


def test_null_cell_runs_and_reports_yield():
    r = pipeline.run_null_randfb(FX, NS, log_fn=lambda *a: None)
    assert r["stage3"]["log_verification"]["all_ok"]
    assert 0 < r["stage1"]["relation_yield"] <= 1
    assert r["factor_base"]["L"] == r["interval_L"]


def test_rho_baseline_solves_and_counts_units():
    out = rho.run_rho(FX, NS, 3)
    assert out["n_solved"] == 3
    for t in out["targets"]:
        assert t["k_true_matches"] and t["units"] > t["walk_units"] > 0
        assert t["units"] == t["precompute_units"] + t["walk_units"]


def test_stage2_scan_work_is_linear_in_L():
    fb = b0.interval_fb(FX, 5)
    s2 = pipeline.stage2(FX, NS, fb, 4)
    assert all(p["units"] == 2 * fb.L * (13 + 1) for p in s2["per_point"])
    assert s2["agreement_with_brute_force"] == 4
