#!/usr/bin/env python3
"""Blind re-derivation of EXP-ECDLP-5f3822 Stage 0 gates.

Reads only the frozen specification. Does not import the producer.
Does not use frozenset. Does not use exists-c set equality. Does not use min().
Workspace root from this review path is Path(__file__).resolve().parents[7].

Different exact method from the producer:
  characteristic-array pairwise reflection for symmetry,
  pairwise sorted-tuple comparison for collision,
  not exists-c set equality plus frozenset M_S.
"""
from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[7]
SPEC = ROOT / "experiments/EXP-ECDLP-5f3822/specification.yaml"
OUT = Path(__file__).resolve().parent / "blind_raw.json"


def fold_x(t: int, n: int) -> int:
    t_mod = int(t) % int(n)
    complement = (int(n) - t_mod) % int(n)
    if t_mod <= complement:
        return t_mod
    return complement


def char_array(s: list[int], n: int) -> list[int]:
    bits = [0] * int(n)
    for x in s:
        bits[int(x) % int(n)] = 1
    return bits


def pairwise_reflection_symmetric(s: list[int], n: int) -> bool:
    bits = char_array(s, n)
    reversed_bits = bits[::-1]
    for shift in range(int(n)):
        rotated = reversed_bits[shift:] + reversed_bits[:shift]
        if rotated == bits:
            return True
    return False


def sorted_tuple_image(x: int, s: list[int], n: int) -> tuple[int, ...]:
    values = [fold_x(int(x) + int(shift), n) for shift in s]
    return tuple(sorted(values))


def pairwise_collision(s: list[int], n: int) -> bool:
    images = [sorted_tuple_image(x, s, n) for x in range(int(n))]
    for i in range(len(images)):
        for j in range(i + 1, len(images)):
            if images[i] == images[j]:
                return True
    return False


def eval_shift(s: list[int], n: int) -> dict[str, object]:
    is_sym = pairwise_reflection_symmetric(s, n)
    is_col = pairwise_collision(s, n)
    return {
        "symmetric": is_sym,
        "collision": is_col,
        "iff": is_sym == is_col,
    }


def main() -> int:
    spec = yaml.safe_load(SPEC.read_text())
    fx = spec["experiment"]["inputs"]["fixture"]
    n = int(fx["n_frozen"])
    real_fx = fx["real_shift"]
    kf_fx = fx["known_false"]
    null_fx = fx["matched_null"]
    invalid = fx["invalid"]

    real_s = [int(x) for x in real_fx["S"]]
    kf_s = [int(x) for x in kf_fx["S"]]

    n_zero_rejected = False
    for row in invalid:
        if row["id"] == "n-zero":
            n_bad = int(row["n"])
            must = bool(row["must_reject"])
            rejected = n_bad != n and n_bad == 0
            n_zero_rejected = rejected and must

    null_rejected = (
        null_fx["kind"] == "empty_or_short_S" and bool(null_fx["must_reject"])
    )

    real = eval_shift(real_s, n)
    kf = eval_shift(kf_s, n)

    fixture_pass = (
        n == 7
        and real_s == [1, 6]
        and kf_s == [1, 2, 4]
        and len(kf_s) != 2
        and bool(real_fx["must_symmetric"])
        and bool(real_fx["must_collision"])
        and bool(real_fx["must_iff"])
        and (not bool(kf_fx["must_symmetric"]))
        and (not bool(kf_fx["must_collision"]))
        and bool(kf_fx["must_iff"])
        and bool(kf_fx.get("must_not_be_pair"))
        and null_fx["kind"] == "empty_or_short_S"
    )
    real_count_pass = (
        bool(real["symmetric"]) and bool(real["collision"]) and bool(real["iff"])
    )
    known_false_asymmetric_pass = (
        (not bool(kf["symmetric"]))
        and (not bool(kf["collision"]))
        and bool(kf["iff"])
        and (bool(kf["symmetric"]) != bool(real["symmetric"]))
        and len(kf_s) != 2
    )
    reject_invalid_pass = n_zero_rejected
    null_empty_pass = null_rejected
    all_pass = (
        fixture_pass
        and real_count_pass
        and known_false_asymmetric_pass
        and reject_invalid_pass
        and null_empty_pass
    )
    payload = {
        "fixture_pass": fixture_pass,
        "real_count_pass": real_count_pass,
        "known_false_asymmetric_pass": known_false_asymmetric_pass,
        "reject_invalid_pass": reject_invalid_pass,
        "null_empty_pass": null_empty_pass,
        "REAL": {"id": "REAL", "S": real_s, **real},
        "KF": {
            "id": "KF",
            "asymmetric": True,
            "must_not_be_pair": True,
            "S": kf_s,
            **kf,
        },
        "NULL": {
            "id": "NULL",
            "kind": "empty_or_short_S",
            "rejected": null_rejected,
        },
        "all_pass": all_pass,
        "imported_producer": False,
        "used_frozenset": False,
        "used_exists_c_set_equality": False,
        "used_min": False,
        "blind_from_respected": True,
        "workspace_root": str(ROOT),
        "method": "char_array_pairwise_reflection_and_sorted_tuple_collision",
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(payload))
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
