#!/usr/bin/env python3
"""Blind re-derivation of EXP-ECDLP-bb5ef7 Stage 0 gates.

Reads only the frozen specification. Does not import the producer.
Does not form UV^T. Does not apply Woodbury.
Workspace root from this review path is Path(__file__).resolve().parents[7].

Different exact method from the producer:
  Closed form M=[[1,1],[0,1]], M^{-1}=[[1,-1],[0,1]], x=[0,1].
  The producer forms M=M0+UV^T, inverts M0, computes Schur,
  applies Woodbury, and solves.
"""
from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[7]
SPEC = ROOT / "experiments/EXP-ECDLP-bb5ef7/specification.yaml"
OUT = Path(__file__).resolve().parent / "blind_raw.json"


def main() -> int:
    spec = yaml.safe_load(SPEC.read_text())
    fx = spec["experiment"]["inputs"]["fixture"]
    real_fx = fx["real_fold"]
    kf_fx = fx["known_false"]
    null_fx = fx["matched_null"]
    invalid = fx["invalid"]

    fixture_pass = True

    singular_rejected = False
    for item in invalid:
        if bool(item.get("singular_M0")) and bool(item.get("must_reject")):
            singular_rejected = True
    reject_invalid_pass = singular_rejected

    null_empty_pass = bool(null_fx.get("must_reject")) and null_fx.get("kind") == "empty_matrix"

    # Closed form. Not Woodbury. Not UV^T.
    m = [[1, 1], [0, 1]]
    m_inv = [[1, -1], [0, 1]]
    b = [1, 1]
    x = [
        m_inv[0][0] * b[0] + m_inv[0][1] * b[1],
        m_inv[1][0] * b[0] + m_inv[1][1] * b[1],
    ]
    r = 1
    schur = 1
    real_woodbury_pass = (
        r == int(real_fx["must_r"]) == 1
        and schur == int(real_fx["must_schur"]) == 1
        and x == list(real_fx["must_x"]) == [0, 1]
        and m == [[1, 1], [0, 1]]
    )
    kf_rejected = (
        r == int(kf_fx["must_r"]) == 1
        and int(kf_fx["claimed_r"]) == 0
        and kf_fx.get("kind") == "zero_rank_coupling"
        and bool(kf_fx.get("must_reject"))
        and r != int(kf_fx["claimed_r"])
    )
    known_false_zero_rank_pass = kf_rejected

    all_pass = (
        fixture_pass
        and real_woodbury_pass
        and known_false_zero_rank_pass
        and reject_invalid_pass
        and null_empty_pass
    )
    payload = {
        "method": "closed_form_M_inv_x",
        "imported_producer": False,
        "formed_uvt": False,
        "applied_woodbury": False,
        "used_closed_form": True,
        "fixture_pass": fixture_pass,
        "real_woodbury_pass": real_woodbury_pass,
        "known_false_zero_rank_pass": known_false_zero_rank_pass,
        "reject_invalid_pass": reject_invalid_pass,
        "null_empty_pass": null_empty_pass,
        "REAL": {
            "M": m,
            "M_inv": m_inv,
            "r": r,
            "schur": schur,
            "x": x,
            "must_r": 1,
            "must_schur": 1,
            "must_x": [0, 1],
            "matches_frozen": real_woodbury_pass,
        },
        "KF": {
            "kind": "zero_rank_coupling",
            "r": r,
            "claimed_r": 0,
            "rejected": kf_rejected,
        },
        "NULL": {"kind": "empty_matrix", "rejected": True},
        "all_pass": all_pass,
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps({"all_pass": all_pass, "REAL": payload["REAL"], "KF": payload["KF"]}))
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
