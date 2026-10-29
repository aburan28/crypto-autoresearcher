#!/usr/bin/env python3
"""Cross-check the sealed review outputs without editing either review."""

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
J1 = HERE / "reports/TASK-20261026-538444"
J2 = HERE / "reports/TASK-20261026-7ab9cb"


def read(path):
    return json.loads(path.read_text())


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


one = {row["mask"]: row for row in read(J1 / "source-guided-summary.json")}
two = {row["mask"]: row for row in read(J2 / "output.json")["results"]}
expected = {131081: (17, 510, True), 313: (8, 30, True),
            471: (8, 30, True), 131073: (17, 510, False),
            257: (8, 30, False)}
assert set(one) == set(two) == set(expected)

rows = []
for mask, (degree, count, predicate) in expected.items():
    a, b = one[mask], two[mask]
    assert a["degree"] == b["degree"] == degree
    assert a["candidate_count"] == b["candidate_count"] == count
    assert len(b["candidate_rows"]) == count
    assert a["predicate"] is b["predicate"] is predicate
    first_zero = None if b["first_zero"] is None else b["first_zero"]["divisor"]
    assert a["first_zero_divisor"] == first_zero
    assert a["unfinished_count"] == 0
    rows.append({"mask": mask, "degree": degree, "candidate_count": count,
                 "predicate": predicate, "first_zero_divisor": first_zero,
                 "j1_max_reductions": a["max_reduction_steps"],
                 "j2_max_reductions": b["maximum_reduction_steps"]})

for name, expected_exit in (("direct-lean-retry", 0), ("AuditTypes", 0),
                            ("Audit", 0), ("FalseControl", 1)):
    assert read(J1 / f"{name}.result.json")["exit_code"] == expected_exit

out = {
    "schema": "binstd.lean_review_reconciliation.v1",
    "producer_revision": read(HERE / "inputs.json")["producer_revision"],
    "j1_summary_sha256": sha256(J1 / "source-guided-summary.json"),
    "j2_output_sha256": sha256(J2 / "output.json"),
    "j1_attestation_sha256": sha256(J1 / "review_attestation.yaml"),
    "j2_attestation_sha256": sha256(J2 / "review_attestation.yaml"),
    "independent_arithmetic_agreement": True,
    "direct_lean_exit_codes": {"compile": 0, "types": 0, "axioms": 0,
                               "false_control": 1},
    "full_mathlib_workspace_gate": "not_verified",
    "rows": rows,
}
(HERE / "reconciliation.json").write_text(json.dumps(out, indent=2) + "\n")
print("PASS: five masks, 1110 candidate rows, direct Lean and negative control exits")
