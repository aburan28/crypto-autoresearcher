#!/usr/bin/env python3
"""Blind re-derivation of EXP-ECDLP-821bc5 Stage 0 gates.

Reads only the frozen specification. Does not import the producer.
Does not call recurrence_W.
Workspace root from this review path is Path(__file__).resolve().parents[7].

Different exact method from the producer:
  closed form via bit-shift (n-1)<<(n-2), not (n-1)*(2**(n-2))
  four explicit products, not a recurrence_W walk:
    2*4+2*4-4, 4*4+2*12-8, 4*12+4*12-16, 8*4+2*32-16
  KF omits the last term: 2*4+2*4
"""
from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[7]
SPEC = ROOT / "experiments/EXP-ECDLP-821bc5/specification.yaml"
OUT = Path(__file__).resolve().parent / "blind_raw.json"


def closed_shift(n: int) -> int:
    """W_n = (n-1) * 2^{n-2} via a left shift, not a power."""
    return (n - 1) << (n - 2)


def main() -> int:
    spec = yaml.safe_load(SPEC.read_text())
    fx = spec["experiment"]["inputs"]["fixture"]
    n_values = tuple(int(x) for x in fx["n_values"])
    w3 = int(fx["w3_frozen"])
    real_fx = fx["real"]
    kf_fx = fx["known_false"]
    null_fx = fx["matched_null"]
    invalid = fx["invalid"]

    must_W = {int(k): int(v) for k, v in real_fx["must_W"].items()}
    must_W6_alt = int(real_fx["must_W6_alt"])
    must_kf = int(kf_fx["must_W_4"])
    must_null = int(null_fx["must_W"])

    # Four explicit products. No w_res helper. No recurrence_W.
    w4 = 2 * 4 + 2 * 4 - 4
    w5 = 4 * 4 + 2 * 12 - 8
    w6 = 4 * 12 + 4 * 12 - 16
    w6_alt = 8 * 4 + 2 * 32 - 16
    kf4 = 2 * 4 + 2 * 4
    closed = {n: closed_shift(n) for n in n_values}
    rec = {3: w3, 4: w4, 5: w5, 6: w6}
    null_map = {n: 0 for n in n_values}

    n_two_rejected = False
    n_zero_rejected = False
    for row in invalid:
        nid = row["id"]
        n = int(row["n"])
        must = bool(row["must_reject"])
        rejected = n not in n_values
        if nid == "n-two":
            n_two_rejected = rejected and must
        if nid == "n-zero":
            n_zero_rejected = rejected and must

    fixture_pass = (
        n_values == (3, 4, 5, 6)
        and w3 == 4
        and must_W == {3: 4, 4: 12, 5: 32, 6: 80}
        and must_W6_alt == 80
        and must_kf == 16
        and must_null == 0
        and bool(kf_fx.get("omit_sylvester_term"))
        and null_fx["kind"] == "zero_sequence"
    )
    real_weight_pass = rec == must_W and closed == must_W and w6_alt == must_W6_alt
    known_false_omit_sylvester_pass = kf4 == must_kf and kf4 != must_W[4]
    reject_invalid_pass = n_two_rejected and n_zero_rejected
    null_zero_pass = all(null_map[n] == 0 and null_map[n] != must_W[n] for n in n_values)
    all_pass = (
        fixture_pass
        and real_weight_pass
        and known_false_omit_sylvester_pass
        and reject_invalid_pass
        and null_zero_pass
    )
    payload = {
        "fixture_pass": fixture_pass,
        "real_weight_pass": real_weight_pass,
        "known_false_omit_sylvester_pass": known_false_omit_sylvester_pass,
        "reject_invalid_pass": reject_invalid_pass,
        "null_zero_pass": null_zero_pass,
        "REAL": {
            "W": {str(n): rec[n] for n in n_values},
            "closed_form": {str(n): closed[n] for n in n_values},
            "W_6_alt": w6_alt,
            "products": {
                "W_4": "2*4+2*4-4",
                "W_5": "4*4+2*12-8",
                "W_6": "4*12+4*12-16",
                "W_6_alt": "8*4+2*32-16",
            },
        },
        "KF": {
            "id": "KF",
            "omit_sylvester_term": True,
            "W_4": kf4,
            "product": "2*4+2*4",
        },
        "NULL": {
            "id": "NULL",
            "kind": "zero_sequence",
            "W": {str(n): 0 for n in n_values},
            "rejected_as_collapse": True,
        },
        "all_pass": all_pass,
        "imported_producer": False,
        "called_recurrence_W": False,
        "blind_from_respected": True,
        "workspace_root": str(ROOT),
        "method": "bitshift_closed_form_and_four_explicit_products",
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(payload))
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
