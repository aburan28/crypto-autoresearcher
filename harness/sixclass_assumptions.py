"""Emit a machine-readable H1 coverage and claim gate from raw receipts.

The matrix is falsifiable but currently unvalidated. This command checks
receipt integrity and maps each observation to the H1 clauses it can actually
inform. It never turns a smoke run into proof of a 256-bit cost claim.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from harness import sixclass_native

MATRIX = Path(__file__).parent / "fixtures/sixclass_h1_matrix.json"
SCHEMA = "crypto.autoresearch.sixclass-h1-coverage.v1"


def report(receipts: list[Path], matrix: Path = MATRIX) -> dict:
    spec = json.loads(matrix.read_text())
    if (spec.get("schema") != "crypto.autoresearch.sixclass-h1-matrix.v1"
            or len(spec.get("clauses", [])) != 5
            or len({c["id"] for c in spec["clauses"]}) != 5):
        raise ValueError("H1 matrix has changed or is incomplete")
    observations = []
    for path in receipts:
        data = json.loads(path.read_text())
        schema = data.get("schema")
        if schema == "crypto.autoresearch.sixclass-paired.v1":
            if (data.get("status") != "bounded_diagnostic_only"
                    or not data.get("paired_rows")
                    or not data.get("native", {}).get("unpriced")):
                raise ValueError("paired receipt omits cost or scope controls")
            routing = [row.get("routing_screen") for row in data["paired_rows"]]
            if any(row is not None for row in routing):
                informs = ["partition-dp-routing-bits", "twist-index-independence",
                           "surcharge-rates"]
                limitation = ("routing counts and A/A drift are descriptive; correlated visits "
                              "are not independent H1 samples and full-work costs remain unpriced")
            else:
                informs = ["surcharge-rates"]
                limitation = "partial counters and A/A drift only; full-work costs unpriced"
        elif schema == "crypto.autoresearch.sixclass-isolated.v1":
            if data.get("phase") == "custody" and "publication" in data:
                informs = []
                limitation = "challenge custody only; no H1 sampling"
            elif data.get("phase") == "answer-check" and data.get("result", {}).get("schema") == "crypto.sixclass.answer-check.v1":
                informs = []
                limitation = "answer correctness only; no H1 sampling"
            else:
                raise ValueError("malformed isolated receipt")
        elif schema == "crypto.autoresearch.sixclass-native.v1":
            if "result" not in data or "job_sha256" not in data:
                raise ValueError("malformed native worker receipt")
            informs = ["partition-dp-routing-bits", "nonfruitless-return"]
            limitation = "one endpoint; no held-out distribution"
        else:
            raise ValueError(f"unsupported receipt schema: {schema}")
        observations.append({"path": str(path), "sha256": sixclass_native.digest(path),
                             "schema": schema, "informs": informs,
                             "limitation": limitation})
    return {"schema": SCHEMA, "matrix_sha256": sixclass_native.digest(matrix),
            "source_commit": spec["source_commit"],
            "clauses": [{"id": c["id"], "prediction": c["prediction"],
                         "falsifier": c["falsifier"],
                         "required_controls": c["required_controls"],
                         "required_observables": c["required_observables"],
                         "status": "open",
                         "observations": [o["sha256"] for o in observations
                                          if c["id"] in o["informs"]]}
                        for c in spec["clauses"]],
            "observations": observations, "production_claim_admissible": False,
            "reason": "H1 distributions and full-work cost are not validated at secp256k1 scale"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, action="append", default=[])
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    output = report(args.receipt)
    from harness.sixclass_isolated import _write_new
    _write_new(args.out, output)
    print(json.dumps({"out": str(args.out), "production_claim_admissible": False},
                     sort_keys=True))


if __name__ == "__main__":
    main()
