#!/usr/bin/env python3
"""Blind re-derivation of EXP-ECDLP-fdae20 Stage 0 gates.

Reads only the frozen specification. Does not import the producer.
Workspace root from this review path is Path(__file__).resolve().parents[7].

Evaluate n^{p/q} as 2^{4p/q} because n=16=2^4, requiring 4p divisible
by q (opposite the producer's integer_root-then-raise).
"""
from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[7]
SPEC = ROOT / "experiments/EXP-ECDLP-fdae20/specification.yaml"
OUT = Path(__file__).resolve().parent / "blind_raw.json"


class InvalidParamsError(ValueError):
    pass


def pow2_frac(exp_num: int, exp_den: int) -> int:
    """16^{exp_num/exp_den} = 2^{4 exp_num / exp_den} as an exact integer."""
    if exp_den <= 0:
        raise ValueError("non-positive exponent denominator")
    if exp_num < 0:
        raise ValueError("negative exponent")
    bit = 4 * exp_num
    if bit % exp_den != 0:
        raise ValueError(f"16^{exp_num}/{exp_den} is not an integer power of two")
    return 1 << (bit // exp_den)


def c_prep_pow2(n: int, M: int, sigma_num: int, sigma_den: int) -> int:
    if n != 16:
        raise ValueError("blind method is the n=16=2^4 power-of-two identity")
    if n <= 1:
        raise InvalidParamsError("n<=1 makes log n undefined")
    if M <= 0:
        raise InvalidParamsError("M<=0 makes σ* undefined")
    off_num = sigma_den + sigma_num
    off_den = 2 * sigma_den
    on_num = sigma_den - sigma_num
    on_den = 2 * sigma_den
    return pow2_frac(off_num, off_den) + M * pow2_frac(on_num, on_den)


def bar_pow2(n: int, M: int) -> int:
    if n != 16:
        raise ValueError("blind method is the n=16=2^4 power-of-two identity")
    if n <= 1:
        raise InvalidParamsError("n<=1 makes log n undefined")
    if M <= 0:
        raise InvalidParamsError("M<=0 makes σ* undefined")
    # 2√(M n) = 2√(16 M) = 8 √M; M=4 → 16, M=1 → 8
    # √(16M) = 4 √M; require M a square.
    if M == 1:
        return 8
    if M == 4:
        return 16
    raise ValueError("blind bar table covers only M in {1, 4}")


def cheap_offline_pow2(n: int, M: int, sigma_num: int, sigma_den: int) -> int:
    if n != 16:
        raise ValueError("blind method is the n=16=2^4 power-of-two identity")
    if n <= 1:
        raise InvalidParamsError("n<=1 makes log n undefined")
    if M <= 0:
        raise InvalidParamsError("M<=0 makes σ* undefined")
    on_num = sigma_den - sigma_num
    on_den = 2 * sigma_den
    return M * pow2_frac(on_num, on_den)


def main() -> int:
    spec = yaml.safe_load(SPEC.read_text())
    fx = spec["experiment"]["inputs"]["fixture"]
    real_fx = fx["real"]
    kf_fx = fx["known_false"]
    null_fx = fx["matched_null"]

    n = int(fx["n"])
    M = int(fx["M"])
    sn = int(fx["sigma_star"]["num"])
    sd = int(fx["sigma_star"]["den"])

    real_c = c_prep_pow2(n, M, sn, sd)
    real_bar = bar_pow2(n, M)
    m1_c = c_prep_pow2(n, 1, 0, 1)
    m1_bar = bar_pow2(n, 1)
    kf_c = c_prep_pow2(n, M, 0, 1)
    null_c = cheap_offline_pow2(n, M, sn, sd)

    reject_n = False
    reject_m = False
    try:
        c_prep_pow2(1, M, sn, sd)
    except (InvalidParamsError, ValueError):
        reject_n = True
    try:
        c_prep_pow2(n, 0, sn, sd)
    except InvalidParamsError:
        reject_m = True

    fixture_pass = (
        n == 16
        and M == 4
        and sn == 1
        and sd == 2
        and int(real_fx["must_c_prep"]) == 16
        and int(real_fx["must_bar"]) == 16
        and int(real_fx["m1_must_c_prep"]) == 8
        and int(kf_fx["must_c_prep"]) == 20
        and int(null_fx["must_c_null"]) == 8
        and null_fx["kind"] == "cheap_offline"
    )
    real_identity_pass = (
        real_c == 16 and real_bar == 16 and real_c == real_bar
        and m1_c == 8 and m1_bar == 8 and m1_c == m1_bar
    )
    known_false_subopt_pass = kf_c == 20 and kf_c != real_bar
    reject_invalid_pass = reject_n and reject_m
    null_cheap_offline_pass = null_c == 8 and null_c != real_bar
    all_pass = (
        fixture_pass
        and real_identity_pass
        and known_false_subopt_pass
        and reject_invalid_pass
        and null_cheap_offline_pass
    )
    payload = {
        "fixture_pass": fixture_pass,
        "real_identity_pass": real_identity_pass,
        "known_false_subopt_pass": known_false_subopt_pass,
        "reject_invalid_pass": reject_invalid_pass,
        "null_cheap_offline_pass": null_cheap_offline_pass,
        "REAL": {
            "n": n,
            "M": M,
            "c_prep": real_c,
            "bar": real_bar,
            "m1_c_prep": m1_c,
            "m1_bar": m1_bar,
        },
        "KF": {"n": n, "M": M, "sigma": 0, "c_prep": kf_c, "bar": real_bar},
        "NULL": {
            "id": "NULL",
            "kind": "cheap_offline",
            "c_null": null_c,
            "bar": real_bar,
            "rejected_as_collapse": null_c != real_bar,
        },
        "all_pass": all_pass,
        "imported_producer": False,
        "blind_from_respected": True,
        "workspace_root": str(ROOT),
        "method": "powers_of_two_n16_is_2_to_4",
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(payload))
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
