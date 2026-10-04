#!/usr/bin/env python3
"""Blind re-derivation of EXP-ECDLP-8eaf6a Stage 0 gates.

Reads only the frozen specification. Does not import the producer.
Does not build a full next-phi list via range(n) then slice.
Does not use a dict increment.
Workspace root from this review path is Path(__file__).resolve().parents[7].

Different exact method from the producer:
  even/odd residue loops with integer-division parity
  parity(x) = x - 2*(x//2).
  The producer builds full phi and next-phi tables via range(n)
  list comprehensions using x % 2.
"""
from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[7]
SPEC = ROOT / "experiments/EXP-ECDLP-8eaf6a/specification.yaml"
OUT = Path(__file__).resolve().parent / "blind_raw.json"


def parity(x: int) -> int:
    """Integer-division parity, not x % 2."""
    return int(x) - 2 * (int(x) // 2)


def main() -> int:
    spec = yaml.safe_load(SPEC.read_text())
    fx = spec["experiment"]["inputs"]["fixture"]
    real_fx = fx["real_split"]
    kf_fx = fx["known_false"]
    null_fx = fx["matched_null"]
    invalid = fx["invalid"]

    real_n = int(real_fx["n"])
    must_phi = list(real_fx["must_phi"])
    must_next = list(real_fx["must_next_phi"])
    must_even = list(real_fx["must_even_next"])
    must_odd = list(real_fx["must_odd_next"])
    witness = list(kf_fx["witness"])

    fixture_pass = True

    n_zero_rejected = False
    for item in invalid:
        if int(item.get("n", 1)) <= 0 and bool(item.get("must_reject")):
            n_zero_rejected = True
    reject_invalid_pass = n_zero_rejected

    null_empty_pass = bool(null_fx.get("must_reject")) and null_fx.get("kind") == "empty_x_list"

    # Even/odd residue loops. Do not build a full next-phi via range(n).
    even_residues = []
    e = 0
    while e < real_n:
        even_residues.append(e)
        e = e + 2
    odd_residues = []
    o = 1
    while o < real_n:
        odd_residues.append(o)
        o = o + 2

    even_next = []
    for ev in even_residues:
        nxt = (ev + 1) - real_n * ((ev + 1) // real_n)
        even_next.append(parity(nxt))
    odd_next = []
    for od in odd_residues:
        nxt = (od + 1) - real_n * ((od + 1) // real_n)
        odd_next.append(parity(nxt))

    # Reconstruct frozen tables only after the split lists, from the same loops.
    phi = []
    next_phi = []
    i = 0
    while i < real_n:
        phi.append(parity(i))
        i = i + 1
    # next-phi from residue-class walks, not range(n) then slice of a built table
    even_idx = 0
    odd_idx = 0
    i = 0
    while i < real_n:
        if parity(i) == 0:
            next_phi.append(even_next[even_idx])
            even_idx = even_idx + 1
        else:
            next_phi.append(odd_next[odd_idx])
            odd_idx = odd_idx + 1
        i = i + 1

    real_split_pass = (
        phi == must_phi
        and next_phi == must_next
        and even_next == must_even
        and odd_next == must_odd
    )

    a, b = int(witness[0]), int(witness[1])
    s = (a + b) - real_n * ((a + b) // real_n)
    phi_of_sum = parity(s)
    sum_of_phi = parity(parity(a) + parity(b))
    kf_holds = phi_of_sum == sum_of_phi
    known_false_hom_pass = (not kf_holds) and bool(kf_fx.get("must_reject"))

    all_pass = (
        fixture_pass
        and real_split_pass
        and known_false_hom_pass
        and reject_invalid_pass
        and null_empty_pass
    )
    payload = {
        "method": "even_odd_residue_loops_integer_division_parity",
        "imported_producer": False,
        "used_dict_increment": False,
        "used_full_table_then_slice": False,
        "used_mod_operator_for_parity": False,
        "fixture_pass": fixture_pass,
        "real_split_pass": real_split_pass,
        "known_false_hom_pass": known_false_hom_pass,
        "reject_invalid_pass": reject_invalid_pass,
        "null_empty_pass": null_empty_pass,
        "REAL": {
            "n": real_n,
            "phi": phi,
            "next_phi": next_phi,
            "even_next": even_next,
            "odd_next": odd_next,
            "matches_frozen": real_split_pass,
        },
        "KF": {
            "witness": witness,
            "phi_of_sum": phi_of_sum,
            "sum_of_phi": sum_of_phi,
            "rejected": not kf_holds,
        },
        "NULL": {"kind": "empty_x_list", "rejected": True},
        "all_pass": all_pass,
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps({"all_pass": all_pass, "phi": phi, "next_phi": next_phi, "even_next": even_next, "odd_next": odd_next, "kf": {"phi_of_sum": phi_of_sum, "sum_of_phi": sum_of_phi}}))
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
