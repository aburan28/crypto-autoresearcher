"""The formal-lane CI gate's decision logic.

The gate itself (`lake build`, the axiom audit, the per-theorem target audit)
belongs to `autoresearch formal verify` and is tested with the rest of the
formal lane.  What is tested here is the part this script adds, which is what
CI is allowed to conclude from the verifier's exit codes.

Two of these are the reason the script exists.  `test_floor_rejects_a_run_that
_verifies_nothing` is the vacuous pass that the previous workflow had: a job
that builds no proofs and reports success.  `test_infrastructure_failure_is
_not_a_failed_proof` is AGENTS.md rule 3 -- a toolchain that fell over must
never be recorded as a proof that did not check out.

The verifier is stubbed by exit code on purpose.  Driving real Lean here would
make this suite need a Mathlib build to say anything about branching.
"""
import importlib.util
import json
import shutil
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


def gate():
    """Import tools/verify_formal_targets.py, which is a script, not a module."""

    spec = importlib.util.spec_from_file_location(
        "verify_formal_targets", REPO_ROOT / "tools" / "verify_formal_targets.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def run(monkeypatch, tmp_path, exit_code, extra=None):
    """Run the gate over the real target set with the verifier stubbed."""

    module = gate()
    monkeypatch.setattr(module, "formal_main", lambda argv: exit_code)
    return module.main(["--artifact-dir", str(tmp_path / "receipts"), *(extra or [])])


def test_verified_target_passes(monkeypatch, tmp_path):
    assert run(monkeypatch, tmp_path, 0) == 0


def test_unverified_target_fails(monkeypatch, tmp_path):
    assert run(monkeypatch, tmp_path, 1) == 1


def test_infrastructure_failure_is_not_a_failed_proof(monkeypatch, tmp_path):
    """Exit 3, distinct from 1: red, but never negative mathematical evidence."""

    assert run(monkeypatch, tmp_path, 3) == 3


def test_floor_rejects_a_run_that_verifies_nothing(monkeypatch, tmp_path):
    """A gate that machine-checks no proof must not report success.

    Every committed target here is undischarged, so nothing is verified -- the
    exact shape of the workflow this script replaced.
    """

    targets = tmp_path / "targets"
    targets.mkdir()
    undischarged = REPO_ROOT / "formal/targets/ncp-reachability.yaml"
    shutil.copy2(undischarged, targets / undischarged.name)

    module = gate()
    monkeypatch.setattr(module, "formal_main",
                        lambda argv: pytest.fail("verifier ran for an absent theorem file"))
    assert module.main(["--artifact-dir", str(tmp_path / "receipts"),
                        "--targets-dir", str(targets)]) == 1


def test_floor_is_a_floor_not_a_count(monkeypatch, tmp_path):
    """Verifying fewer than the floor fails even when nothing failed outright.

    Uses a one-target fixture so the assertion stays true when more proofs
    land on main — running against the live target set with ``--min-verified 2``
    would start passing the moment a second theorem file appears.
    """

    targets = tmp_path / "targets"
    targets.mkdir()
    discharged = REPO_ROOT / "formal/targets/semaev-s3-degree2-fall-witness.yaml"
    shutil.copy2(discharged, targets / discharged.name)

    module = gate()
    monkeypatch.setattr(module, "formal_main", lambda argv: 0)
    assert module.main([
        "--artifact-dir", str(tmp_path / "receipts"),
        "--targets-dir", str(targets),
        "--min-verified", "2",
    ]) == 1


def test_failure_reason_is_printed_not_buried_in_the_artifact(tmp_path, capsys):
    """A red build must say why in its own log, not only in an uploaded file."""

    module = gate()
    receipt = tmp_path / "r.json"
    receipt.write_text(json.dumps({
        "verification": {"blocking_reason": "lake build failed"},
        "build_log": "\n".join(f"line {i}" for i in range(100)),
        "audit_log": "",
    }), encoding="utf-8")

    assert module._explain(receipt) == "lake build failed"
    err = capsys.readouterr().err
    assert "lake build failed" in err
    assert "last 40 of 100 lines" in err   # clipped, so one failure cannot bury the summary
    assert "line 99" in err                # and the clip keeps the END, where errors are


def test_explain_survives_a_missing_receipt(tmp_path, capsys):
    """Verification can fail before any receipt exists; triage must not crash."""

    module = gate()
    assert module._explain(tmp_path / "absent.json") == ""
    assert "could not read receipt" in capsys.readouterr().err
