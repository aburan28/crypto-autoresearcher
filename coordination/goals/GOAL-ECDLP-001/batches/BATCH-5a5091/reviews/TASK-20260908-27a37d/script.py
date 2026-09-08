#!/usr/bin/env python3
"""Blind re-derivation of EXP-ECDLP-735974 Stage 0 gates.

Reads only the frozen specification. Does not import the producer.
Workspace root from this review path is Path(__file__).resolve().parents[7].

Closed forms, not successive (1-t^{d_i}) convolution:
  m=n+1 quadrics: (1-t)(1+t)^{n+1}
  complete intersection of n quadrics: (1+t)^n
  empty-degree n=2 ring: hf[k] = k+1
Binomial coefficients via Pascal triangle (opposite the producer's
multiplicative C(n+k-1, k) start plus convolution).
"""
from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[7]
SPEC = ROOT / "experiments/EXP-ECDLP-735974/specification.yaml"
OUT = Path(__file__).resolve().parent / "blind_raw.json"
MAX_DEGREE = 16


def pascal_row(n: int) -> list[int]:
    """Row n of Pascal's triangle: C(n, 0)..C(n, n)."""
    row = [1]
    for k in range(n):
        row.append(row[-1] * (n - k) // (k + 1))
    return row


def coeffs_one_plus_t_power(p: int, max_degree: int) -> list[int]:
    """Coefficients of (1+t)^p through max_degree."""
    row = pascal_row(p)
    out = []
    for k in range(max_degree + 1):
        out.append(row[k] if k <= p else 0)
    return out


def times_one_minus_t(hf: list[int]) -> list[int]:
    """Multiply a polynomial/series by (1-t)."""
    out = []
    for k, c in enumerate(hf):
        prev = hf[k - 1] if k else 0
        out.append(c - prev)
    return out


def d_reg_from_hf(hf: list[int]) -> int | None:
    for k, c in enumerate(hf):
        if c <= 0:
            return k
    return None


def main() -> int:
    spec = yaml.safe_load(SPEC.read_text())
    fx = spec["experiment"]["inputs"]["fixture"]
    real_fx = fx["real"]
    base_fx = fx["baseline"]
    kf_fx = fx["known_false"]
    null_fx = fx["matched_null"]
    max_degree = int(fx["max_degree"])

    real_n = int(real_fx["n"])
    real_d = tuple(int(x) for x in real_fx["degrees"])
    base_n = int(base_fx["n"])
    base_d = tuple(int(x) for x in base_fx["degrees"])
    kf_n = int(kf_fx["n"])
    kf_d = tuple(int(x) for x in kf_fx["degrees"])
    null_n = int(null_fx["n"])
    null_d = tuple(int(x) for x in null_fx["degrees"])

    # REAL: n=2, three quadrics → (1-t)(1+t)^3
    if real_n != 2 or real_d != (2, 2, 2):
        raise ValueError("blind closed form covers only REAL (2,(2,2,2))")
    real_hf = times_one_minus_t(coeffs_one_plus_t_power(3, max_degree))
    real_reg = d_reg_from_hf(real_hf)

    # BASE: n=4, five quadrics → (1-t)(1+t)^5
    if base_n != 4 or base_d != (2, 2, 2, 2, 2):
        raise ValueError("blind closed form covers only BASE (4,(2,2,2,2,2))")
    base_hf = times_one_minus_t(coeffs_one_plus_t_power(5, max_degree))
    base_reg = d_reg_from_hf(base_hf)

    # KF: n=2, two quadrics complete intersection → (1+t)^2
    if kf_n != 2 or kf_d != (2, 2):
        raise ValueError("blind closed form covers only KF (2,(2,2))")
    kf_hf = coeffs_one_plus_t_power(2, max_degree)
    kf_reg = d_reg_from_hf(kf_hf)

    # NULL: empty degree list at n=2 → hf[k]=k+1
    if null_n != 2 or null_d != ():
        raise ValueError("blind closed form covers only NULL n=2 empty")
    null_hf = [k + 1 for k in range(max_degree + 1)]
    null_reg = d_reg_from_hf(null_hf)

    def refuse(n: int, degrees: tuple[int, ...]) -> bool:
        if n <= 0:
            return True
        if any(d <= 0 for d in degrees):
            return True
        return False

    n_zero_rejected = refuse(0, (2, 2, 2))
    nonpos_rejected = refuse(2, (2, 0, 2))

    fixture_pass = (
        max_degree == 16
        and real_n == 2
        and real_d == (2, 2, 2)
        and int(real_fx["must_d_reg"]) == 2
        and base_n == 4
        and int(base_fx["must_d_reg"]) == 3
        and kf_n == 2
        and kf_d == (2, 2)
        and int(kf_fx["must_d_reg"]) == 3
        and null_fx["kind"] == "empty_degree_list"
        and null_fx["must_d_reg"] is None
    )
    real_identity_pass = real_reg == 2 and base_reg == 3
    known_false_ci_pass = kf_reg == 3 and kf_reg != real_reg
    reject_invalid_pass = n_zero_rejected and nonpos_rejected
    null_empty_degree_pass = null_reg is None and null_reg != real_reg
    all_pass = (
        fixture_pass
        and real_identity_pass
        and known_false_ci_pass
        and reject_invalid_pass
        and null_empty_degree_pass
    )
    payload = {
        "fixture_pass": fixture_pass,
        "real_identity_pass": real_identity_pass,
        "known_false_ci_pass": known_false_ci_pass,
        "reject_invalid_pass": reject_invalid_pass,
        "null_empty_degree_pass": null_empty_degree_pass,
        "REAL": {
            "n": real_n,
            "degrees": list(real_d),
            "d_reg": real_reg,
            "hf_prefix": real_hf[:6],
            "base_n": base_n,
            "base_d_reg": base_reg,
        },
        "KF": {
            "n": kf_n,
            "degrees": list(kf_d),
            "d_reg": kf_reg,
            "hf_prefix": kf_hf[:6],
        },
        "NULL": {
            "id": "NULL",
            "kind": "empty_degree_list",
            "n": null_n,
            "d_reg": null_reg,
            "hf_prefix": null_hf[:6],
            "rejected_as_collapse": null_reg != real_reg,
        },
        "all_pass": all_pass,
        "imported_producer": False,
        "blind_from_respected": True,
        "workspace_root": str(ROOT),
        "method": "pascal_closed_form_one_minus_t_times_one_plus_t_power",
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(payload))
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
