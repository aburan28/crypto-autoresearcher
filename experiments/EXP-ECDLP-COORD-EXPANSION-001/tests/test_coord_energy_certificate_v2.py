import importlib.util
import subprocess
import sys
from pathlib import Path


SOURCE = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "coord_energy_certificate_v2.py"
)
SPEC = importlib.util.spec_from_file_location(
    "coord_energy_certificate_v2_test", SOURCE
)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def toy_curve():
    curve = MODULE.RECURSIVE.generate_prime_order_curve(10, 401)
    census, by_point = MODULE.subgroup_census(
        MODULE.decode_point(curve["generator"]),
        curve["q"],
        curve["p"],
        curve["a"],
    )
    return curve, census, by_point


def add_multiple(point, coefficient, curve):
    total = None
    signed = point
    if coefficient < 0:
        signed = None if point is None else (point[0], (-point[1]) % curve["p"])
    for _ in range(abs(coefficient)):
        total = MODULE.ec_add(total, signed, curve["p"], curve["a"])
    return total


def test_registered_factor_base_chains_replay():
    curve, _, _ = toy_curve()
    for family in MODULE.CANDIDATES:
        factor_base = MODULE.make_factor_base(
            family, curve, 5, MODULE.stable_seed(family)
        )
        assert len(factor_base["points"]) == 5
        assert len({tuple(point) for point in factor_base["points"]}) == 5
        parameters = factor_base["public_parameters"]
        for source in factor_base["sources"]:
            if family == "quartic_composition_chain":
                assert source["u"] == (
                    source["t"] + parameters["c"]
                ) % curve["p"]
                assert source["v"] == (
                    source["u"] ** 2 + parameters["d"]
                ) % curve["p"]
                assert source["x"] == (
                    source["v"] ** 2 + parameters["e"]
                ) % curve["p"]
            elif family == "reciprocal_denominator_chain":
                assert (
                    source["denominator"]
                    * source["denominator_inverse"]
                    % curve["p"]
                    == 1
                )
                assert (
                    source["denominator_character"]
                    == parameters["denominator_character_stratum"]
                )
            else:
                assert (
                    pow(
                        source["x"],
                        parameters["subgroup_order"],
                        curve["p"],
                    )
                    == source["coset_tag"]
                )


def test_ap_freiman_and_public_certificate_replay():
    curve, census, _ = toy_curve()
    _, _, scalars = MODULE.ap_scalars(curve["q"], 7, 99)
    metrics, _ = MODULE.set_metrics(
        scalars, curve["q"], retain_witnesses=True, census=census
    )
    assert metrics["freiman_dimension"] == 1
    assert metrics["d2"]["representation_total"] == 7**2
    assert metrics["d4"]["representation_total"] == 7**4
    certificates = metrics["certificates"]
    for relation in certificates["freiman"]["basis"]:
        total = None
        for scalar, coefficient in zip(scalars, relation):
            term = add_multiple(census[scalar], coefficient, curve)
            total = MODULE.ec_add(total, term, curve["p"], curve["a"])
        assert total is None
    for record in certificates["popular_difference"]["top_differences"]:
        scalar = record["diagnostic_scalar_difference"]
        assert record["difference_point"] == MODULE.encode_point(census[scalar])
    top = certificates["popular_difference"]["top_differences"]
    for left_index, right_index, difference_rank in certificates[
        "popular_difference"
    ]["edges"]:
        right = census[scalars[right_index]]
        negated_right = (
            None
            if right is None
            else (right[0], (-right[1]) % curve["p"])
        )
        difference = MODULE.ec_add(
            census[scalars[left_index]],
            negated_right,
            curve["p"],
            curve["a"],
        )
        assert MODULE.encode_point(difference) == top[difference_rank][
            "difference_point"
        ]


def test_rank_auc_and_holm_are_directional():
    high = MODULE.empirical_rank(10, [1, 2, 3, 10], "high")
    low = MODULE.empirical_rank(0, [0, 2, 3, 4], "low")
    assert high["rank_p"] == 0.4
    assert high["tie_aware_auc"] == 0.875
    assert low["rank_p"] == 0.4
    assert low["tie_aware_auc"] == 0.875
    corrected = MODULE.holm(
        [
            {"id": "a", "p": 0.001},
            {"id": "b", "p": 0.02},
            {"id": "c", "p": 0.2},
        ],
        0.05,
    )
    assert [row["reject"] for row in corrected] == [True, True, False]


def test_target_rows_include_zero_support():
    curve, census, by_point = toy_curve()
    factor_base = MODULE.make_factor_base(
        "quartic_composition_chain", curve, 5, 17
    )
    scalars = tuple(
        sorted(
            by_point[MODULE.decode_point(point)]
            for point in factor_base["points"]
        )
    )
    _, d4 = MODULE.set_metrics(
        scalars, curve["q"], retain_witnesses=False
    )
    rows, receipt = MODULE.target_rows(
        0, curve, census, d4, factor_base
    )
    assert len(rows) == curve["q"]
    assert receipt["rows"] == curve["q"]
    assert receipt["zero_support_rows"] > 0
    assert any(row["multiplicity"] == 0 for row in rows)


def test_development_mode_disables_confirmatory_signal():
    result = MODULE.run([8, 9, 10], [19], 2, 1, True)
    assert not result["config"]["strict_confirmatory_configuration"]
    assert result["summary"]["candidate_positive_signals"] == 0
    assert all(
        not gate["producer_screening_signal"]
        for gate in result["family_gates"].values()
    )
    assert result["config"]["heldout_bits"] == 10


def test_nonconfirmatory_cli_requires_development_flag():
    completed = subprocess.run(
        [
            sys.executable,
            str(SOURCE),
            "--null-draws",
            "3",
        ],
        capture_output=True,
        text=True,
    )
    assert completed.returncode != 0
    assert "require --development" in completed.stderr
