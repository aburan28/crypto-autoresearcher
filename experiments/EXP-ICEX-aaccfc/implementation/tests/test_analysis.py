"""C-5 ratio/exponent/verdict rule on synthetic inputs (never on data)."""

import math

import analysis
import common

QS = {(16, 21): 60821, (16, 22): 63703, (16, 23): 47059, (20, 21): 562333, (20, 22): 619537, (20, 23): 909289}


def synth(expo, c, shares=(0.2, 0.1, 0.7), jitter=0.0):
    out = []
    for i, ((bits, seed), q) in enumerate(sorted(QS.items())):
        total = c * q ** expo * (1 + jitter * ((-1) ** i))
        comp = {"stage1": total * shares[0], "stage3": total * shares[1], "descents": total * shares[2]}
        out.append({"fixture": {"bits": bits, "seed": seed, "N": q}, "fixture_id": f"b{bits}-s{seed}",
                    "complete_units": total, "complete_units_components": comp, "peak_rss_bytes": 1,
                    "stage2_alpha2": {"mean_units": 28 * (3 + i)}, "factor_base": {"L": 3 + i}})
    return out


def test_ratio_definition():
    a = analysis.analyse(synth(0.5, 13 * 0.886))
    for p in a["per_fixture"]:
        assert math.isclose(p["ratio"], 1.0, rel_tol=1e-9)
        assert math.isclose(p["ratio"], p["complete_units"] / (13 * 0.886 * math.sqrt(p["q"])))


def test_sub_rho_signal():
    a = analysis.analyse(synth(0.3, 1.0))
    assert a["exponent_bootstrap"]["ci95"][1] < 0.5
    assert all(p["ratio"] < 1 for p in a["per_fixture"] if p["bits"] == 20)
    assert a["verdict"] == "sub_rho_signal" and a["dominant_stage_20bit"] is None


def test_low_exponent_but_ratio_above_one_is_not_sub_rho():
    a = analysis.analyse(synth(0.3, 1e6))
    assert a["exponent_bootstrap"]["ci95"][1] < 0.5
    assert a["verdict"] == "inconclusive"


def test_scoped_negative_names_dominant_stage():
    a = analysis.analyse(synth(0.8, 1.0, shares=(0.6, 0.1, 0.3)))
    assert a["exponent_bootstrap"]["ci95"][0] >= 0.5
    assert a["verdict"] == "scoped_negative" and a["dominant_stage_20bit"] == "stage1"


def test_inconclusive_when_ci_straddles():
    a = analysis.analyse(synth(0.5, 1.0, jitter=0.6))
    lo, hi = a["exponent_bootstrap"]["ci95"]
    assert lo < 0.5 <= hi or hi >= 0.5 > lo
    assert a["verdict"] == "inconclusive"


def test_exponent_exact_and_bootstrap_deterministic():
    a = analysis.analyse(synth(0.62, 3.0))
    assert math.isclose(a["exponent"], 0.62, abs_tol=1e-9)
    b = analysis.analyse(synth(0.62, 3.0))
    assert a["exponent_bootstrap"] == b["exponent_bootstrap"]
    assert a["exponent_bootstrap"]["resamples"] == common.BOOTSTRAP_RESAMPLES


def test_alpha2_slope_one_for_linear_scan():
    a = analysis.analyse(synth(0.6, 1.0))
    assert math.isclose(a["alpha2"], 1.0, abs_tol=1e-9)


# ---- AMD-20260929-5a84eb FX-8: leave-b16-s21-out sensitivity (non-verdict)
VERDICT_KEYS = ("verdict", "exponent", "exponent_bootstrap", "dominant_stage_20bit", "pooled_units_20bit")


def test_leave_out_fit_is_the_five_point_fit_and_labelled_nonverdict():
    prim = synth(0.62, 3.0, jitter=0.2)
    a = analysis.analyse(prim)
    s = a["exponent_leave_out_b16_s21_nonverdict"]
    assert s["applicable"] and s["left_out"] == "b16-s21" and "NOT a verdict input" in s["label"]
    assert "verdict" not in s and "b16-s21" not in s["fixtures"] and len(s["fixtures"]) == 5
    kept = [p for p in a["per_fixture"] if p["fixture_id"] != "b16-s21"]
    want = analysis.ols_slope([math.log(p["q"]) for p in kept], [math.log(p["complete_units"]) for p in kept])
    assert math.isclose(s["exponent"], want, abs_tol=1e-12)
    lo, hi = s["exponent_bootstrap"]["ci95"]
    assert lo <= hi and s["exponent_bootstrap"]["resamples"] == common.BOOTSTRAP_RESAMPLES
    assert s["exponent_bootstrap"]["label"] == common.lab(common.FROZEN_NS, "bootstrap", "leave_out", "b16-s21")
    assert s["exponent_bootstrap"]["label"] != a["exponent_bootstrap"]["label"]


def test_verdict_unchanged_by_leave_out_block():
    for expo, c, j in ((0.3, 1.0, 0.0), (0.8, 1.0, 0.0), (0.5, 1.0, 0.6), (0.3, 1e6, 0.0)):
        prim = synth(expo, c, jitter=j)
        with_s = analysis.analyse(prim)
        without = analysis.analyse(prim, sensitivity=False)
        assert "exponent_leave_out_b16_s21_nonverdict" not in without
        for k in VERDICT_KEYS:
            assert with_s[k] == without[k]


def test_verdict_follows_primary_fit_even_when_leave_out_disagrees():
    # five points on slope 0.3 with ratio < 1; b16-s21 made a large outlier so
    # the six-point fit is not sub-rho while the leave-out fit is.
    prim = synth(0.3, 1.0)
    for r in prim:
        if r["fixture_id"] == "b16-s21":
            for s in r["complete_units_components"]:
                r["complete_units_components"][s] *= 1e-6
            r["complete_units"] *= 1e-6
    a = analysis.analyse(prim)
    s = a["exponent_leave_out_b16_s21_nonverdict"]
    assert s["exponent_bootstrap"]["ci95"][1] < 0.5
    assert a["exponent_bootstrap"]["ci95"][1] >= 0.5 and a["verdict"] != "sub_rho_signal"
    assert a["verdict"] == analysis.analyse(prim, sensitivity=False)["verdict"]


def test_leave_out_not_applicable_without_b16_s21():
    prim = [r for r in synth(0.6, 1.0) if r["fixture_id"] != "b16-s21"]
    s = analysis.analyse(prim)["exponent_leave_out_b16_s21_nonverdict"]
    assert s["applicable"] is False and s["exponent"] is None
