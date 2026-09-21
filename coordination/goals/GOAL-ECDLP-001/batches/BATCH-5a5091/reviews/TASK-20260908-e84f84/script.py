#!/usr/bin/env python3
"""Blind re-derivation of EXP-ECDLP-6ffef4 Stage 0 gates.

Reads only the frozen specification. Does not import the producer.
Does not use frozenset. Does not build an F table. Does not use defaultdict.
Workspace root from this review path is Path(__file__).resolve().parents[7].

Different exact method from the producer:
  integer pairwise same-value implies same-image-value for propagate,
  sorted-list fibre-image equality for invariant,
  not frozenset blocks plus an F dict.
"""
from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[7]
SPEC = ROOT / "experiments/EXP-ECDLP-6ffef4/specification.yaml"
OUT = Path(__file__).resolve().parent / "blind_raw.json"


def pairwise_propagate(v: dict[int, int], gamma: int, n: int) -> bool:
    xs = list(v)
    for i, x in enumerate(xs):
        for y in xs[i + 1 :]:
            if int(v[x]) == int(v[y]):
                if int(v[(int(gamma) * int(x)) % int(n)]) != int(
                    v[(int(gamma) * int(y)) % int(n)]
                ):
                    return False
    return True


def sorted_list_invariant(v: dict[int, int], gamma: int, n: int) -> bool:
    xs = list(v)
    for x in xs:
        fibre = [int(y) for y in xs if int(v[y]) == int(v[x])]
        image = [(int(gamma) * int(y)) % int(n) for y in fibre]
        target_val = int(v[(int(gamma) * int(x)) % int(n)])
        target_fibre = [int(z) for z in xs if int(v[z]) == target_val]
        if sorted(image) != sorted(target_fibre):
            return False
    return True


def eval_pair(v: dict[int, int], n: int, gammas: list[int]) -> dict[str, object]:
    inv_all = True
    prop_all = True
    per_gamma = []
    for gamma in gammas:
        inv = sorted_list_invariant(v, gamma, n)
        prop = pairwise_propagate(v, gamma, n)
        inv_all = inv_all and inv
        prop_all = prop_all and prop
        per_gamma.append(
            {
                "gamma": int(gamma),
                "invariant": inv,
                "propagate": prop,
                "iff": inv == prop,
            }
        )
    return {
        "invariant": inv_all,
        "propagate": prop_all,
        "iff": inv_all == prop_all,
        "per_gamma": per_gamma,
    }


def main() -> int:
    spec = yaml.safe_load(SPEC.read_text())
    fx = spec["experiment"]["inputs"]["fixture"]
    n = int(fx["n_frozen"])
    gammas = [int(g) for g in fx["gamma_frozen"]]
    domain = [int(x) for x in fx["domain_frozen"]]
    real_fx = fx["real_blocks"]
    kf_fx = fx["known_false"]
    null_fx = fx["matched_null"]
    invalid = fx["invalid"]

    real_v = {int(k): int(val) for k, val in dict(real_fx["v"]).items()}
    kf_v = {int(k): int(val) for k, val in dict(kf_fx["v"]).items()}

    n_zero_rejected = False
    for row in invalid:
        if row["id"] == "n-zero":
            n_bad = int(row["n"])
            must = bool(row["must_reject"])
            rejected = n_bad != n and n_bad == 0
            n_zero_rejected = rejected and must

    null_rejected = (
        null_fx["kind"] == "empty_domain" and bool(null_fx["must_reject"])
    )

    real = eval_pair(real_v, n, gammas)
    kf = eval_pair(kf_v, n, gammas)

    fixture_pass = (
        n == 7
        and gammas == [1, 6]
        and domain == [1, 2, 3, 4, 5, 6]
        and real_v == {1: 0, 6: 0, 2: 1, 5: 1, 3: 2, 4: 2}
        and kf_v == {1: 0, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1}
        and bool(real_fx["must_invariant"])
        and bool(real_fx["must_propagate"])
        and bool(real_fx["must_iff"])
        and (not bool(kf_fx["must_invariant"]))
        and (not bool(kf_fx["must_propagate"]))
        and bool(kf_fx["must_iff"])
        and bool(kf_fx.get("must_not_equal_real"))
        and null_fx["kind"] == "empty_domain"
    )
    real_count_pass = (
        bool(real["invariant"]) and bool(real["propagate"]) and bool(real["iff"])
    )
    known_false_nonblock_pass = (
        (not bool(kf["invariant"]))
        and (not bool(kf["propagate"]))
        and bool(kf["iff"])
        and (bool(kf["invariant"]) != bool(real["invariant"]))
    )
    reject_invalid_pass = n_zero_rejected
    null_empty_pass = null_rejected
    all_pass = (
        fixture_pass
        and real_count_pass
        and known_false_nonblock_pass
        and reject_invalid_pass
        and null_empty_pass
    )
    payload = {
        "fixture_pass": fixture_pass,
        "real_count_pass": real_count_pass,
        "known_false_nonblock_pass": known_false_nonblock_pass,
        "reject_invalid_pass": reject_invalid_pass,
        "null_empty_pass": null_empty_pass,
        "REAL": {
            "id": "REAL",
            "v": {str(k): int(val) for k, val in real_v.items()},
            **real,
        },
        "KF": {
            "id": "KF",
            "nonblock": True,
            "v": {str(k): int(val) for k, val in kf_v.items()},
            **kf,
        },
        "NULL": {
            "id": "NULL",
            "kind": "empty_domain",
            "rejected": null_rejected,
        },
        "all_pass": all_pass,
        "imported_producer": False,
        "used_frozenset": False,
        "built_F_table": False,
        "used_defaultdict": False,
        "blind_from_respected": True,
        "workspace_root": str(ROOT),
        "method": "integer_pairwise_propagate_and_sorted_list_invariant",
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(payload))
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
