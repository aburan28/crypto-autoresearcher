"""Protocol gates for native paired work and one bounded follow-up."""
import copy
import json
from pathlib import Path

import pytest

from harness import sixclass_assumptions, sixclass_followup, sixclass_native, sixclass_paired


ROOT = Path(__file__).resolve().parents[1]
JOB = ROOT / "harness/fixtures/sixclass_p25.json"


def test_paired_aa_control_and_cost_claim_gate():
    native = json.loads((ROOT / "harness/evidence/sixclass-paired-p25-20261024.json").read_text())["native"]
    receipt = sixclass_paired.audit(JOB, Path(__file__), 100, 2, native, 1)
    assert len(receipt["paired_rows"]) == 2
    assert receipt["status"] == "bounded_diagnostic_only"
    broken = copy.deepcopy(native)
    broken["trials"][0]["baseline_after"]["class_visits"] += 1
    with pytest.raises(ValueError, match="A/A controls"):
        sixclass_paired.audit(JOB, Path(__file__), 100, 2, broken, 1)
    coverage = sixclass_assumptions.report([])
    assert len(coverage["clauses"]) == 5
    assert not coverage["production_claim_admissible"]
    assert all(row["status"] == "open" for row in coverage["clauses"])


def test_followup_is_write_once_and_frozen(tmp_path, monkeypatch):
    binary = tmp_path / "worker"
    binary.write_bytes(b"test binary pin")
    initial = {"walkers": 1000, "num_branches": 32, "dp_bits": 4,
               "max_steps_per_walker": 320, "seed": 7}
    attempt = tmp_path / "attempt"
    sixclass_followup.freeze(binary, JOB, attempt, initial)
    raw = json.loads((ROOT / "harness/evidence/sixclass-p25-20261024.json").read_text())["result"]

    def sealed_run(job, worker, walkers, out, **_kwargs):
        receipt = sixclass_native.receipt_for_result(job, worker, walkers, 1, raw)
        receipt["container"] = {"image": sixclass_followup.sixclass_isolated.IMAGE,
                                "private_audit_mounted": False,
                                "network": "none", "read_only": True}
        out.write_text(json.dumps(receipt))
        return receipt

    monkeypatch.setattr(sixclass_followup.sixclass_isolated, "run", sealed_run)
    sixclass_followup.initial(attempt, binary, JOB)
    with pytest.raises(ValueError, match="must change"):
        sixclass_followup.followup(attempt, binary, JOB, initial, "reviewer", "reason")
    selected = dict(initial, walkers=1001)
    sixclass_followup.followup(attempt, binary, JOB, selected, "local-test", "bounded change")
    with pytest.raises(FileExistsError):
        sixclass_followup.followup(attempt, binary, JOB, selected, "local-test", "again")
    final = sixclass_followup.finalize(attempt, binary, JOB)
    assert len(final["stages"]) == 2
    with pytest.raises(ValueError, match="finalized"):
        sixclass_followup.followup(attempt, binary, JOB, dict(initial, seed=8),
                                  "local-test", "after final")


def test_followup_replays_requested_bound_before_selection(tmp_path, monkeypatch):
    binary = tmp_path / "worker"
    binary.write_bytes(b"test binary pin")
    initial = {"walkers": 1000, "num_branches": 32, "dp_bits": 4,
               "max_steps_per_walker": 320, "seed": 7}
    attempt = tmp_path / "attempt"
    sixclass_followup.freeze(binary, JOB, attempt, initial)
    raw = json.loads((ROOT / "harness/evidence/sixclass-p25-20261024.json").read_text())["result"]
    def sealed_run(job, worker, walkers, out, **_kwargs):
        receipt = sixclass_native.receipt_for_result(job, worker, walkers, 1, raw)
        receipt["container"] = {"image": sixclass_followup.sixclass_isolated.IMAGE,
                                "private_audit_mounted": False,
                                "network": "none", "read_only": True}
        receipt["requested_walkers"] += 1
        out.write_text(json.dumps(receipt))
        return receipt
    monkeypatch.setattr(sixclass_followup.sixclass_isolated, "run", sealed_run)
    sixclass_followup.initial(attempt, binary, JOB)
    with pytest.raises(ValueError, match="independent replay"):
        sixclass_followup.followup(attempt, binary, JOB, dict(initial, walkers=1001),
                                  "local-test", "reject tamper")


def test_followup_rejects_tampered_binary_and_out_of_bounds(tmp_path):
    binary = tmp_path / "worker"
    binary.write_bytes(b"original")
    initial = {"walkers": 1, "num_branches": 32, "dp_bits": 4,
               "max_steps_per_walker": 320, "seed": 7}
    attempt = tmp_path / "attempt"
    sixclass_followup.freeze(binary, JOB, attempt, initial)
    binary.write_bytes(b"changed")
    with pytest.raises(ValueError, match="frozen binary"):
        sixclass_followup.initial(attempt, binary, JOB)
    with pytest.raises(ValueError, match="bounded schema"):
        sixclass_followup.validate_input(dict(initial, walkers=10001))
