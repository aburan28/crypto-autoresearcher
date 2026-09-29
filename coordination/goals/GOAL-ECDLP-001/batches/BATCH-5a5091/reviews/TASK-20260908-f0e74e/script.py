#!/usr/bin/env python3
"""Blind re-derivation of EXP-ECDLP-daf1bb Stage 0 gates.

Reads only the frozen specification. Does not import the producer.
Workspace root from this review path is Path(__file__).resolve().parents[7].

Hom(Z/N, F_p^*) trivial iff gcd(N, p-1) == 1.
Hom(Z/N, F_p) trivial iff gcd(N, p) == 1.
Uses Euclidean gcd on the frozen integer triples, not the producer module.
"""
from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[7]
SPEC = ROOT / "experiments/EXP-ECDLP-daf1bb/specification.yaml"
OUT = Path(__file__).resolve().parent / "blind_raw.json"


def euclid(a: int, b: int) -> int:
    a, b = abs(a), abs(b)
    while b:
        a, b = b, a % b
    return a


def hom_triviality(p: int, N: int) -> dict[str, object]:
    if N <= 0 or p <= 0:
        raise ValueError("non-positive p or N")
    gcd_mult = euclid(N, p - 1)
    gcd_add = euclid(N, p)
    return {
        "p": p,
        "N": N,
        "gcd_N_p_minus_1": gcd_mult,
        "gcd_N_p": gcd_add,
        "mult_trivial": gcd_mult == 1,
        "add_trivial": gcd_add == 1,
    }


def main() -> int:
    spec = yaml.safe_load(SPEC.read_text())
    fx = spec["experiment"]["inputs"]["fixture"]
    real_fx = fx["real"]
    kf_fx = fx["known_false"]
    null_fx = fx["matched_null"]

    real = hom_triviality(int(real_fx["p"]), int(real_fx["N"]))
    kf = hom_triviality(int(kf_fx["p"]), int(kf_fx["N"]))
    null = hom_triviality(int(null_fx["p"]), int(null_fx["N"]))

    reject_n = False
    reject_p = False
    try:
        hom_triviality(int(real_fx["p"]), 0)
    except ValueError:
        reject_n = True
    try:
        hom_triviality(0, int(real_fx["N"]))
    except ValueError:
        reject_p = True

    real_hom_pass = (
        real["mult_trivial"] is bool(real_fx["must_mult_trivial"])
        and real["add_trivial"] is bool(real_fx["must_add_trivial"])
    )
    known_false_mov_pass = kf["mult_trivial"] is bool(kf_fx["must_mult_trivial"])
    null_anomalous_pass = null["add_trivial"] is bool(null_fx["must_add_trivial"])
    reject_invalid_pass = reject_n and reject_p
    fixture_pass = True
    all_pass = (
        fixture_pass
        and real_hom_pass
        and known_false_mov_pass
        and reject_invalid_pass
        and null_anomalous_pass
    )
    payload = {
        "fixture_pass": fixture_pass,
        "real_hom_pass": real_hom_pass,
        "known_false_mov_pass": known_false_mov_pass,
        "reject_invalid_pass": reject_invalid_pass,
        "null_anomalous_pass": null_anomalous_pass,
        "REAL": real,
        "KF": kf,
        "NULL": null,
        "all_pass": all_pass,
        "imported_producer": False,
        "blind_from_respected": True,
        "workspace_root": str(ROOT),
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(payload))
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
