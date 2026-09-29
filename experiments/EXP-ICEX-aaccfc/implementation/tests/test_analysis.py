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
