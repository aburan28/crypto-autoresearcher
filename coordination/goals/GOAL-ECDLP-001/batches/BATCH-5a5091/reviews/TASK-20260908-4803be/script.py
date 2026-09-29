#!/usr/bin/env python3
"""Blind re-derivation of EXP-ECDLP-b3f975 Stage 0 gates.

Reads only the frozen specification. Does not import the producer.
Workspace root from this review path is Path(__file__).resolve().parents[7].

D = -4. Split iff p ≡ 1 (mod 4). Root of T^2+1 found by scanning
downward from p-1 (opposite producer loop order). Image enumerated
as a set of u + r v residues. NULL non-split is a rejection, not
a false membership.
"""
from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[7]
SPEC = ROOT / "experiments/EXP-ECDLP-b3f975/specification.yaml"
OUT = Path(__file__).resolve().parent / "blind_raw.json"


class NonSplitError(ValueError):
    pass


def splits(p: int) -> bool:
    return p % 4 == 1


def root_downward(p: int) -> int:
    for r in range(p - 1, -1, -1):
        if (r * r + 1) % p == 0:
            return r
    raise NonSplitError("no root of T^2+1")


def image_and_membership(p: int, R: int, x: int) -> dict[str, object]:
    if p <= 0 or R < 0:
        raise ValueError("non-positive p or negative R")
    if not splits(p):
        raise NonSplitError("p does not split in Z[i]")
    r = root_downward(p)
    xs = {((u + r * v) % p) for u in range(-R, R + 1) for v in range(-R, R + 1)}
    x_mod = x % p
    return {
        "p": p,
        "R": R,
        "x": x_mod,
        "splits": True,
        "root": r,
        "in_box": x_mod in xs,
        "image": sorted(xs),
        "image_size": len(xs),
    }


def main() -> int:
    spec = yaml.safe_load(SPEC.read_text())
    fx = spec["experiment"]["inputs"]["fixture"]
    real_fx = fx["real"]
    kf_fx = fx["known_false"]
    null_fx = fx["matched_null"]

    real = image_and_membership(int(real_fx["p"]), int(real_fx["R"]), int(real_fx["x"]))
    kf = image_and_membership(int(kf_fx["p"]), int(kf_fx["R"]), int(kf_fx["x"]))

    null_rejected = False
    null_splits = True
    try:
        image_and_membership(int(null_fx["p"]), 1, 0)
    except NonSplitError:
        null_rejected = True
        null_splits = False

    reject_p = False
    reject_r = False
    try:
        image_and_membership(0, int(real_fx["R"]), int(real_fx["x"]))
    except ValueError:
        reject_p = True
    try:
        image_and_membership(int(real_fx["p"]), -1, int(real_fx["x"]))
    except ValueError:
        reject_r = True

    fixture_pass = (
        int(real_fx["p"]) == 13
        and int(real_fx["R"]) == 1
        and int(real_fx["x"]) == 1
        and int(kf_fx["p"]) == 13
        and int(kf_fx["R"]) == 1
        and int(kf_fx["x"]) == 2
        and int(null_fx["p"]) == 7
    )
    real_box_pass = real["in_box"] is bool(real_fx["must_in_box"])
    known_false_out_pass = kf["in_box"] is bool(kf_fx["must_in_box"])
    reject_invalid_pass = reject_p and reject_r
    null_nonsplit_pass = null_rejected and (null_splits is False)
    all_pass = (
        fixture_pass
        and real_box_pass
        and known_false_out_pass
        and reject_invalid_pass
        and null_nonsplit_pass
    )
    payload = {
        "fixture_pass": fixture_pass,
        "real_box_pass": real_box_pass,
        "known_false_out_pass": known_false_out_pass,
        "reject_invalid_pass": reject_invalid_pass,
        "null_nonsplit_pass": null_nonsplit_pass,
        "REAL": real,
        "KF": kf,
        "NULL": {
            "id": "NULL",
            "p": int(null_fx["p"]),
            "rejected": null_rejected,
            "splits": null_splits,
        },
        "all_pass": all_pass,
        "imported_producer": False,
        "blind_from_respected": True,
        "workspace_root": str(ROOT),
        "method": "downward_root_and_set_image",
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(payload))
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
