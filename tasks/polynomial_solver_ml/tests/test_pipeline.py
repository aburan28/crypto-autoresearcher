"""Correctness and failure-path tests; mock timings are never research evidence."""

from copy import deepcopy
import json
from pathlib import Path
import subprocess

import numpy as np
import pytest

from polynomial_ml import pipeline
from polynomial_ml.instances import features, generate_cases, make_case, original_roots, validate_case
from polynomial_ml.solver import ACTIONS, solve_case
from polynomial_ml.verify import verify_run


def test_generated_splits_are_disjoint_and_features_ignore_answers():
    cases = generate_cases()
    assert len(cases) == 23 and len(generate_cases("standard")) == 58
    assert cases == generate_cases()
    assert len({c["id"] for c in cases}) == len(cases)
    train = {c["prime"] for c in cases if c["split"] == "train"}
    assert not train & {c["prime"] for c in cases if c["split"] != "train"}
    for case in cases:
        assert case["planted_root"] in original_roots(case)
        changed = deepcopy(case)
        changed.update(planted_root=[-1, -1], family="hidden", split="hidden", id="hidden")
        assert features(changed) == features(case)


@pytest.mark.parametrize("family", ["dense_quadratic", "sparse_cubic", "triangular", "dense_cubic"])
@pytest.mark.parametrize("action", range(len(ACTIONS)))
def test_actual_solvers_match_original_integer_root_oracle(family, action):
    case = make_case(11, family, 9, 0, "unit_test")
    result = solve_case(case, action, 1)
    assert result["roots"] == original_roots(case)
    assert result["cost_seconds"] > 0
    assert result["intermediate_degree_measured"] is False


def test_validation_rejects_large_or_malformed_systems():
    case = generate_cases()[0]
    for key, value in [("prime", 65537), ("polynomials", [[[1, 4, 0]], [[1, 0, 1]]])]:
        changed = deepcopy(case)
        changed[key] = value
        with pytest.raises(ValueError):
            validate_case(changed)


def fake_child(command, *, input, **kwargs):
    """Fixture for pipeline plumbing; all measurements here are invented test data."""
    payload = json.loads(input)
    case, action = payload["case"], payload["action_id"]
    roots = original_roots(case)
    part = 0.001 * (action + 1)
    label = {"case_id": case["id"], "action_id": action, "status": "completed",
             "cost_seconds": 3 * part, "roots": roots, "root_count": len(roots),
             "timings": [{"construction_seconds": part, "groebner_seconds": part,
                          "root_seconds": part, "total_seconds": 3 * part}],
             "peak_rss_bytes": 1024, "intermediate_degree_measured": False,
             "basis_size": 2, "output_basis_max_degree": 3,
             "unit_test_fixture": True}
    return subprocess.CompletedProcess(command, 0, json.dumps(label), "")


@pytest.fixture
def completed_run(tmp_path, monkeypatch):
    monkeypatch.setattr(pipeline, "run_child", fake_child)
    return pipeline.run(tmp_path / "run", steps=50)


def rehash(out):
    manifest_path = out / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["artifact_sha256"] = pipeline.artifact_hashes(out)
    manifest_path.write_text(json.dumps(manifest))


def test_complete_artifact_replay_and_output_reuse_refusal(completed_run):
    receipt = verify_run(completed_run)
    assert receipt["verified"] and receipt["cases"] == 23 and receipt["actions"] == 92
    before = (completed_run / "manifest.json").read_bytes()
    with pytest.raises(FileExistsError):
        pipeline.run(completed_run)
    assert (completed_run / "manifest.json").read_bytes() == before


def test_verifier_rejects_corruption(completed_run):
    (completed_run / "report.md").write_text("corrupted")
    with pytest.raises(ValueError, match="hash mismatch"):
        verify_run(completed_run)


def test_verifier_rejects_wrong_roots_even_after_rehash(completed_run):
    path = completed_run / "labels.jsonl"
    labels = [json.loads(line) for line in path.read_text().splitlines()]
    labels[0]["roots"] = []
    path.write_text("\n".join(json.dumps(row) for row in labels) + "\n")
    rehash(completed_run)
    with pytest.raises(ValueError, match="root set differs"):
        verify_run(completed_run)


def test_verifier_rejects_checkpoint_not_fitted_on_training_rows(completed_run):
    path = completed_run / "models.json"
    model = json.loads(path.read_text())
    model["normalization"]["mean"][0] += 0.01
    path.write_text(json.dumps(model))
    rehash(completed_run)
    with pytest.raises(ValueError, match="checkpoint does not replay"):
        verify_run(completed_run)


def test_verifier_rejects_wrong_metrics_even_after_rehash(completed_run):
    path = completed_run / "evaluation.json"
    evaluation = json.loads(path.read_text())
    evaluation["test"]["methods"]["bandit"]["mean_par2_seconds"] *= 2
    path.write_text(json.dumps(evaluation))
    rehash(completed_run)
    with pytest.raises(ValueError, match="selected mean cost"):
        verify_run(completed_run)


def test_timeout_is_censored_not_a_fast_solve(tmp_path, monkeypatch):
    calls = 0

    def timeout_once(command, **kwargs):
        nonlocal calls
        calls += 1
        if calls == 1:
            raise subprocess.TimeoutExpired(command, kwargs["timeout"], output=b"partial")
        return fake_child(command, **kwargs)

    monkeypatch.setattr(pipeline, "run_child", timeout_once)
    out = pipeline.run(tmp_path / "timeout", action_timeout=0.1, steps=50)
    labels = [json.loads(line) for line in (out / "labels.jsonl").read_text().splitlines()]
    assert labels[0]["status"] == "timed_out" and labels[0]["censored"] is True
    assert labels[0]["cost_seconds"] == 0.2 and labels[0]["roots"] is None
    assert verify_run(out)["censored_actions"] == 1


def test_crash_preserves_failed_receipt_and_raw_logs(tmp_path, monkeypatch):
    def crash(command, **kwargs):
        return subprocess.CompletedProcess(command, 9, "", "unit-test crash")

    monkeypatch.setattr(pipeline, "run_child", crash)
    out = tmp_path / "crash"
    with pytest.raises(RuntimeError, match="solver child exited 9"):
        pipeline.run(out)
    manifest = json.loads((out / "manifest.json").read_text())
    assert manifest["status"] == "failed" and manifest["measured_actions"] == 0
    assert any(p.read_text() == "unit-test crash" for p in (out / "logs").glob("*.stderr.txt"))
    with pytest.raises(ValueError, match="did not complete"):
        verify_run(out)


def test_invalid_costs_and_action_selections_rejected():
    cases = generate_cases()
    with pytest.raises(ValueError, match="missing"):
        pipeline.cost_table(cases, [])
    costs = np.ones((len(cases), len(ACTIONS)))
    for actions in [np.full(len(cases), -1), np.zeros(len(cases), dtype=float), np.zeros(1, dtype=int)]:
        with pytest.raises(ValueError, match="invalid action"):
            pipeline.evaluate(cases, costs, {"bad": actions})
