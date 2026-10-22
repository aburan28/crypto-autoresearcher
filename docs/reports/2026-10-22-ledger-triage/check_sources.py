"""Check that two schema replacements preserve their frozen source records."""

import hashlib
import json
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[3]
CORRECTIONS = ROOT / "ledger/corrections/schema-supersessions/20261022"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def body(path, kind):
    return yaml.safe_load(path.read_bytes())[kind]


def check_pair(source, replacement, kind, changed):
    old, new = body(source, kind), body(replacement, kind)
    actual = {key for key in old.keys() | new.keys()
              if old.get(key) != new.get(key)}
    assert actual == changed, (source, actual)
    return {"source": str(source.relative_to(ROOT)),
            "source_sha256": digest(source),
            "replacement": str(replacement.relative_to(ROOT)),
            "replacement_sha256": digest(replacement),
            "changed_fields": sorted(actual)}


def main():
    spec = ROOT / "experiments/EXP-ECDLP-daee4d/specification.yaml"
    spec_new = CORRECTIONS / "experiments__EXP-ECDLP-daee4d__specification.v2.yaml"
    trial = json.loads((spec.parent / "trial-plan-v1.json").read_text())
    assert trial["specification_sha256"] == digest(spec)
    assert digest(spec) == "3236ddfd4da01dba0bda1586cd59bf5a7e6b502d8d3e3904e51ba69448059ec8"
    spec_check = check_pair(spec, spec_new, "experiment", {
        "success_criterion", "falsification_criterion", "decision_impact"})

    ev = ROOT / "ledger/evidence/EV-QSP-2c78d3.yaml"
    ev_new = CORRECTIONS / "ledger__evidence__EV-QSP-2c78d3.v2.yaml"
    ev_check = check_pair(ev, ev_new, "evidence", {"run_ids"})
    before, after = body(ev, "evidence"), body(ev_new, "evidence")
    assert set(before["run_ids"]) - set(after["run_ids"]) == {"RUN-QSP-715b58"}
    assert set(after["run_ids"]) - set(before["run_ids"]) == set()
    run_dir = ROOT / "experiments/EXP-QSP-70b731/runs/RUN-QSP-715b58"
    receipt = json.loads((run_dir / "execution-receipt.json").read_text())
    assert receipt["status"] == "claim_expired"
    assert receipt["returncode"] is None
    assert receipt["scientific_conclusion"] is None
    assert not (run_dir / "manifest.yaml").exists()
    assert not (run_dir / "raw-result.json").exists()
    assert "execution-receipt.json" in str(after["proof_refs"])
    assert "claim_expired" in str(after["observations"])

    entries = yaml.safe_load((ROOT / "tools/schema_supersession_registry.yaml").read_bytes())["records"]
    for check in (spec_check, ev_check):
        matches = [e for e in entries if e["superseded_path"] == check["source"]]
        assert len(matches) == 1, check["source"]
        entry = matches[0]
        assert entry["superseded_sha256"] == check["source_sha256"]
        assert entry["superseding_path"] == check["replacement"]
        assert entry["superseding_sha256"] == check["replacement_sha256"]

    print(json.dumps({"status": "pass", "pairs": [spec_check, ev_check],
                      "trial_plan_original_spec_hash_matches": True,
                      "expired_attempt_receipt_sha256": digest(run_dir / "execution-receipt.json"),
                      "expired_attempt_has_run_manifest": False,
                      "expired_attempt_has_raw_result": False}, indent=2))


if __name__ == "__main__":
    main()
