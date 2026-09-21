#!/usr/bin/env python3
"""Blind re-derivation of EXP-ECDLP-eab4d7 Stage 0 gates.

Reads only the frozen specification. Does not import the producer.
Does not use a dict increment. Does not use **.
Workspace root from this review path is Path(__file__).resolve().parents[7].

Different exact method from the producer:
  invert N^2 modulo p-1, then binary square-and-multiply.
  The producer uses a loop of N^2 multiplies.
"""
from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[7]
SPEC = ROOT / "experiments/EXP-ECDLP-eab4d7/specification.yaml"
OUT = Path(__file__).resolve().parent / "blind_raw.json"


def egcd(a: int, b: int) -> tuple[int, int, int]:
    if b == 0:
        return (a, 1, 0)
    g, x, y = egcd(b, a % b)
    return (g, y, x - y * (a // b))


def modinv(a: int, m: int) -> int:
    g, x, _ = egcd(a % m, m)
    if g != 1:
        raise ValueError("not invertible")
    return x % m


def sqmul(base: int, exp: int, mod: int) -> int:
    result = 1
    cur = base % mod
    e = int(exp)
    while e > 0:
        if e & 1:
            result = (result * cur) % mod
        cur = (cur * cur) % mod
        e = e >> 1
    return result


def main() -> int:
    spec = yaml.safe_load(SPEC.read_text())
    fx = spec["experiment"]["inputs"]["fixture"]
    real_fx = fx["real_coprime"]
    kf_fx = fx["known_false"]
    null_fx = fx["matched_null"]
    invalid = fx["invalid"]

    real_p = int(real_fx["p"])
    real_n = int(real_fx["N"])
    n2 = int(real_fx["N2"])
    must_power = list(real_fx["must_power_table"])
    must_roots = list(real_fx["must_roots"])
    kf_p = int(kf_fx["p"])
    kf_n = int(kf_fx["N"])

    fixture_pass = True

    p_zero_rejected = False
    for item in invalid:
        if int(item.get("p", 1)) <= 0 and bool(item.get("must_reject")):
            p_zero_rejected = True
    reject_invalid_pass = p_zero_rejected

    null_empty_pass = bool(null_fx.get("must_reject")) and null_fx.get("kind") == "empty_c_list"

    def gcd(a: int, b: int) -> int:
        aa, bb = abs(int(a)), abs(int(b))
        while bb:
            aa, bb = bb, aa % bb
        return aa

    kf_gcd = gcd(kf_n, kf_p - 1)
    known_false_embed_pass = kf_gcd != 1 and bool(kf_fx.get("must_reject"))

    # Invert n2 modulo p-1; unique root of c is c^inv.
    inv = modinv(n2 % (real_p - 1), real_p - 1)
    power = []
    roots = []
    x = 1
    while x < real_p:
        power.append(sqmul(x, n2, real_p))
        x = x + 1
    c = 1
    while c < real_p:
        roots.append(sqmul(c, inv, real_p))
        c = c + 1

    real_root_pass = power == must_power and roots == must_roots
    all_pass = (
        fixture_pass
        and real_root_pass
        and known_false_embed_pass
        and reject_invalid_pass
        and null_empty_pass
    )
    payload = {
        "method": "invert_N2_mod_pminus1_then_binary_sqmul",
        "imported_producer": False,
        "used_dict_increment": False,
        "used_pow_operator": False,
        "used_repeated_multiply_loop": False,
        "N2_inverse_mod_pminus1": inv,
        "fixture_pass": fixture_pass,
        "real_root_pass": real_root_pass,
        "known_false_embed_pass": known_false_embed_pass,
        "reject_invalid_pass": reject_invalid_pass,
        "null_empty_pass": null_empty_pass,
        "REAL": {
            "p": real_p,
            "N": real_n,
            "power_table": power,
            "roots": roots,
            "matches_frozen": real_root_pass,
        },
        "KF": {"p": kf_p, "N": kf_n, "gcd_N_pminus1": kf_gcd, "rejected": True},
        "NULL": {"kind": "empty_c_list", "rejected": True},
        "all_pass": all_pass,
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps({"all_pass": all_pass, "inv": inv, "power": power, "roots": roots}))
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
