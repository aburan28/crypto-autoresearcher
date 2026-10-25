"""Checks of the integrated instrument's public and artifact boundaries."""

import json
from pathlib import Path

from crypto_autoresearcher.index_calculus.__main__ import main
from crypto_autoresearcher.index_calculus.curve import Curve as IndexCurve
from crypto_autoresearcher.index_calculus.representation_arithmetic import ordinary_curve
from crypto_autoresearcher.index_calculus.representation_controls import (
    circularity_controls, curve_metadata,
)
from tools.curve_identity import inspect_manifest


def test_cli_emits_a_single_json_document(capsys):
    assert main(["representation-controls", "--experiment", "filters", "--seed", "7"]) == 0
    captured = capsys.readouterr()
    report = json.loads(captured.out)
    assert report["schema"] == "ecdlp-representation-controls/v1"
    assert report["seed"] == 7
    assert "filters" in report and "controls" not in report
    assert "not an approved trial" in report["scope"]
    assert report["filters"]["positive_control_sets_identical"]
    assert not captured.err


def test_cli_refuses_an_existing_report_before_starting_work(tmp_path, monkeypatch, capsys):
    from crypto_autoresearcher.index_calculus import representation_controls

    def forbidden(*args):
        raise AssertionError("Refused output must not start a control run")

    monkeypatch.setattr(representation_controls, "build_report", forbidden)
    output = tmp_path / "prior.json"
    output.write_text("prior bytes\n")
    assert main(["representation-controls", "--out", str(output)]) == 2
    assert output.read_text() == "prior bytes\n"
    assert "Refusing to overwrite" in capsys.readouterr().err


def test_cli_writes_only_the_requested_new_report(tmp_path, capsys):
    output = tmp_path / "nested" / "controls.json"
    assert main(["representation-controls", "--experiment", "filters", "--out", str(output)]) == 0
    assert json.loads(output.read_text())["filters"]["lost_positive_controls"] == 0
    assert [p for p in tmp_path.rglob("*") if p.is_file()] == [output]
    assert not capsys.readouterr().out


def test_curve_identity_matches_the_repository_reference_and_changes_with_model():
    curve = ordinary_curve(37)
    first = curve_metadata(curve)
    second = curve_metadata(curve.scaled(2), curve.transport(curve.generator, 2), order=curve.order)
    manifest = {"field": first["field"],
                "curve": first["curve"] | {"curve_id": first["curve_id"]}}
    assert inspect_manifest(manifest)["curve_uid"] == first["curve_uid"]
    assert first["curve_uid"] != second["curve_uid"]


def test_hidden_challenge_answers_replay_in_the_existing_group_implementation():
    report = circularity_controls(seed=11, samples=3, hidden_trials=2)
    positive = report["cases"][0]
    assert positive["status"] == "passes_bounded_signal_checks"
    metadata = positive["curve_identity"]
    curve = IndexCurve(metadata["field"]["characteristic"],
                       metadata["curve"]["a"], metadata["curve"]["b"],
                       metadata["curve"]["subgroup_order"])
    for certificate in positive["public_challenge_certificates"]:
        assert "secret" not in certificate and "label" not in certificate
        for answer in certificate["answers_by_variant"]:
            assert curve.mul(answer, tuple(certificate["base"])) == tuple(certificate["target"])


def test_documented_corpus_links_exist():
    root = Path(__file__).resolve().parents[1]
    for path in ("knowledge/techniques/KN-TECH-73630e.md",
                 "knowledge/open-problems/KN-OPEN-3417fc.md",
                 "docs/lifting-representation-controls.md"):
        assert (root / path).is_file()
