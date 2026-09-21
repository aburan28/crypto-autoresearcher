import importlib.util
import hashlib
import json
import subprocess
import sys
from pathlib import Path


SOURCE = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "coord_energy_certificate_v21.py"
)
SPEC = importlib.util.spec_from_file_location(
    "coord_energy_certificate_v21_test", SOURCE
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
    result = MODULE.run([8, 9, 10], [19], 2, 1, 2, True)
    assert not result["config"]["strict_confirmatory_configuration"]
    assert result["summary"]["candidate_positive_signals"] == 0
    assert all(
        not gate["producer_screening_signal"]
        for gate in result["family_gates"].values()
    )
    assert result["config"]["heldout_bits"] == 10
    assert result["config"]["execution_profile"] == "exploratory_development"
    assert not result["summary"]["predictor_calibration_pass"]


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


def predictor_rows_for_coverage():
    rows = []
    for curve_index in (0, 1):
        for index in range(200):
            rows.append(
                {
                    "curve_index": curve_index,
                    "features": {
                        "feature": "rare" if index == 0 else "broad"
                    },
                    "multiplicity": 10 if index == 0 else index % 2,
                    "positive": index == 0,
                }
            )
    return rows


def test_predictor_excludes_sub_one_percent_bucket():
    training = predictor_rows_for_coverage()
    heldout = predictor_rows_for_coverage()
    fitted = MODULE.fit_predictor(training, heldout)
    assert fitted["selected_buckets"] == ["broad"]
    selected = fitted["eligibility"]["selected"]
    assert selected["eligible"]
    assert selected["pooled_bucket_rows"] == 398
    feature = fitted["eligibility"]["features"]["feature"]
    assert feature["eligible_buckets"] == ["broad"]


def test_predictor_requires_one_percent_on_every_training_curve():
    training = predictor_rows_for_coverage()
    training[1]["features"]["feature"] = "rare"
    training[2]["features"]["feature"] = "rare"
    training[3]["features"]["feature"] = "rare"
    training[200]["features"]["feature"] = "broad"
    heldout = predictor_rows_for_coverage()
    rare = MODULE.bucket_eligibility(training, "feature", "rare")
    assert rare["pooled_pass"]
    assert not rare["eligible"]
    assert [row["bucket_rows"] for row in rare["per_curve"]] == [4, 0]


def test_registered_eligibility_boundary_controls():
    controls = MODULE.eligibility_boundary_controls()
    assert controls["all_pass"]
    assert controls["balanced_null"]["model"]["heldout"]["recall"] == 0.5
    assert (
        controls["balanced_null"]["model"]["heldout"][
            "retained_oracle_enrichment"
        ]
        == 0.0
    )
    assert controls["just_above_one_percent_positive"]["passes"]


def test_confirmatory_seed_lock_derivation(tmp_path):
    freeze_commit = "1" * 40
    seeds = []
    for index in range(3):
        encoded = (
            f"{MODULE.SEED_LOCK_DOMAIN}|{freeze_commit}|{index}"
        ).encode("ascii")
        value = int.from_bytes(hashlib.sha256(encoded).digest()[:8], "big")
        seeds.append(1 + value % (2**31 - 2))
    lock = {
        "protocol": (
            "EXP-ECDLP-COORD-EXPANSION-001-coord-energy-cert-v2.1"
        ),
        "freeze_commit": freeze_commit,
        "derivation_domain": MODULE.SEED_LOCK_DOMAIN,
        "curve_seeds": seeds,
        "construction_command": "test fixture",
    }
    path = tmp_path / "confirmatory-seed-lock.json"
    path.write_text(json.dumps(lock), encoding="ascii")
    original = MODULE.SEED_LOCK_PATH
    MODULE.SEED_LOCK_PATH = path
    try:
        assert MODULE.load_seed_lock() == lock
    finally:
        MODULE.SEED_LOCK_PATH = original
