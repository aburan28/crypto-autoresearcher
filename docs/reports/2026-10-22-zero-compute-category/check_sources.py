"""Bind the only admitted non-execution stage to its frozen sources."""

import hashlib
import json
from pathlib import Path
import sys

import yaml


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
import validate_ledger as ledger


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    entries = ledger.load_run_supersessions()
    matches = [entry for entry in entries.values()
               if entry.get("non_execution") is not None]
    assert len(matches) == 1
    entry = matches[0]
    assert entry["run_id"] == "RUN-QSP-33b442-S0"
    assert entry["supersession_kind"] == "zero_compute_misclassification"
    declaration = entry["non_execution"]
    paths = {role: Path(entry[f"{role}_path"])
             for role in ("superseded", "superseding")}
    paths.update({role: Path(declaration[f"{role}_path"])
                  for role in ("specification", "derivation")})
    expected = {role: (entry if role in ("superseded", "superseding")
                       else declaration)[f"{role}_sha256"]
                for role in paths}
    assert all(path.is_file() and digest(path) == expected[role]
               for role, path in paths.items())
    body = yaml.safe_load(paths["superseding"].read_text())["run"]
    spec = yaml.safe_load(paths["specification"].read_text())["experiment"]
    assert spec["inputs"]["stage_0"]["compute"] == "ZERO. No program is run in this stage."
    assert body["execution"] == "none_occurred"
    run_dir = paths["superseded"].parent
    assert ledger._registered_non_execution_derivation(
        str(paths["superseded"]), str(run_dir), body, entry)
    assert all(not (run_dir / name).exists() for name in ledger.RUN_CAPTURE_ARTIFACTS)
    return {"status": "pass", "run_id": entry["run_id"],
            "classification": "hash-bound hand derivation; no program or measurement",
            "bound_sources": {role: {"path": str(path.relative_to(ROOT)),
                                     "sha256": expected[role]}
                              for role, path in paths.items()},
            "capture_artifacts_absent": list(ledger.RUN_CAPTURE_ARTIFACTS),
            "all_admission_controls_pass": True,
            "scientific_proof_claim": False}


if __name__ == "__main__":
    print(json.dumps(main(), indent=2))
