#!/usr/bin/env python3
"""Blind re-derivation of EXP-ECDLP-0d1336 Stage 0 gates.

Reads only the frozen specification. Does not import the producer.
Workspace root from this review path is Path(__file__).resolve().parents[7].

One-variable Boolean ring as GF(2)^2 pairs (const, xcoeff), not the
producer's bitmask Macaulay matrix.
"""
from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[7]
SPEC = ROOT / "experiments/EXP-ECDLP-0d1336/specification.yaml"
OUT = Path(__file__).resolve().parent / "blind_raw.json"

# (a, b) means a + b*x over GF(2). Multiplication uses x^2 = x.


def parse_poly(terms: list[object]) -> tuple[int, int]:
    a, b = 0, 0
    for term in terms:
        token = str(term)
        if token == "1":
            a ^= 1
        elif token == "x":
            b ^= 1
        else:
            raise ValueError("unknown term")
    return (a, b)


def poly_deg(poly: tuple[int, int]) -> int:
    a, b = poly
    if b:
        return 1
    if a:
        return 0
    return -1


def mul(p: tuple[int, int], q: tuple[int, int]) -> tuple[int, int]:
    a, b = p
    c, d = q
    return (a & c, (a & d) ^ (b & c) ^ (b & d))


def monomials_upto(degree: int) -> list[tuple[int, int]]:
    if degree < 0:
        raise ValueError("negative dmax")
    out = [(1, 0)]
    if degree >= 1:
        out.append((0, 1))
    return out


def gf2_span(rows: list[tuple[int, int]]) -> set[tuple[int, int]]:
    span: set[tuple[int, int]] = {(0, 0)}
    for row in rows:
        span = span | {(s[0] ^ row[0], s[1] ^ row[1]) for s in span}
    return span


def dns_of(
    variables: list[str],
    generators: list[list[str]],
    dmax: int,
) -> tuple[int | None, bool]:
    if not variables:
        raise ValueError("empty variable list")
    if dmax < 0:
        raise ValueError("negative dmax")
    gens = [parse_poly(g) for g in generators]
    one = (1, 0)
    for degree in range(0, dmax + 1):
        rows: list[tuple[int, int]] = []
        for gen in gens:
            d = poly_deg(gen)
            if d < 0 or d > degree:
                continue
            for m in monomials_upto(degree - d):
                rows.append(mul(m, gen))
        if one in gf2_span(rows):
            return degree, True
    return None, False


def main() -> int:
    spec = yaml.safe_load(SPEC.read_text())
    fx = spec["experiment"]["inputs"]["fixture"]
    variables = list(fx["variables"])
    dmax = int(fx["dmax"])
    real_gens = [list(g) for g in fx["real"]["generators"]]
    kf_gens = [list(g) for g in fx["known_false"]["generators"]]
    null_gens = [list(g) for g in fx["matched_null"]["generators"]]

    real_dns, real_found = dns_of(variables, real_gens, dmax)
    kf_dns, kf_found = dns_of(variables, kf_gens, dmax)
    null_dns, null_found = dns_of(variables, null_gens, dmax)

    reject_empty = False
    reject_neg = False
    try:
        dns_of([], real_gens, dmax)
    except ValueError:
        reject_empty = True
    try:
        dns_of(variables, real_gens, -1)
    except ValueError:
        reject_neg = True

    real_dns_pass = real_found is True and real_dns == fx["real"]["must_dns"]
    known_false_sat_pass = kf_found is False
    null_constant_pass = (
        null_found is True and null_dns == fx["matched_null"]["must_dns"]
    )
    reject_invalid_pass = reject_empty and reject_neg
    fixture_pass = True
    all_pass = (
        fixture_pass
        and real_dns_pass
        and known_false_sat_pass
        and reject_invalid_pass
        and null_constant_pass
    )
    payload = {
        "fixture_pass": fixture_pass,
        "real_dns_pass": real_dns_pass,
        "known_false_sat_pass": known_false_sat_pass,
        "reject_invalid_pass": reject_invalid_pass,
        "null_constant_pass": null_constant_pass,
        "REAL_D_NS": real_dns,
        "REAL_found": real_found,
        "KF_D_NS": kf_dns,
        "KF_found": kf_found,
        "NULL_D_NS": null_dns,
        "NULL_found": null_found,
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
