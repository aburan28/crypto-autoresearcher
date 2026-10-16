#!/usr/bin/env python3
"""Independent scalar/Hasse certificates for binary anchors and sampled skips."""

import hashlib
import json
from pathlib import Path

from cypari2 import Pari
from sage.all import EllipticCurve, GF, PolynomialRing


ROOT = Path(__file__).resolve().parent


def field_element(field, value, width):
    return sum((field.gen() ** i for i in range(width) if (value >> i) & 1), field(0))


def build_field(target):
    m = target["m"]
    ring = PolynomialRing(GF(2), "z")
    bits = int(target["polynomial"], 16)
    polynomial = sum((ring.gen() ** i for i in range(m + 1) if (bits >> i) & 1), ring(0))
    return GF(2**m, name="z", modulus=polynomial)


def certify(target, row, field, pari):
    m = target["m"]
    b = int(row["b"], 16)
    E = EllipticCurve(field, [field(1), field(1), field(0), field(0), field_element(field, b, m)])
    h = int(row["checks"]["x9_255_smooth_cofactor"])
    n = int(row["checks"]["x9_remainder"])
    chosen = None
    for x in range(1, 128):
        try:
            point = E.lift_x(field_element(field, x, m))
        except ValueError:
            continue
        projected = h * point
        if projected != E(0):
            chosen = x, point, projected
            break
    if chosen is None:
        raise ArithmeticError("no nontrivial projected point in first 127 x values")
    x, point, projected = chosen
    q = 1 << m
    record = {"target": target["name"], "index": row["index"], "seed": row["seed"],
              "polynomial": target["polynomial"], "b": row["b"], "h": str(h), "n": str(n),
              "point_x_polynomial_basis": hex(x), "point_y_sage": str(point[1]),
              "h_times_point_nonidentity": projected != E(0),
              "n_times_h_times_point_identity": n * projected == E(0),
              "n_prime_pari": bool(pari.isprime(n)),
              "hn_in_hasse_interval": (h * n - q - 1) ** 2 <= 4 * q,
              "hasse_interval_narrower_than_n": n * n > 16 * q,
              "family_accept": row["checks"]["family_accept"],
              "x9_reference_accept": row["checks"]["x9_reference_accept"]}
    record["group_order_certified"] = all(record[key] for key in (
        "h_times_point_nonidentity", "n_times_h_times_point_identity", "n_prime_pari",
        "hn_in_hasse_interval", "hasse_interval_narrower_than_n"))
    return record


def main():
    targets = [row for row in json.loads((ROOT / "targets.json").read_text()) if row["kind"] == "binary"]
    pari = Pari()
    records = []
    for target in targets:
        name = target["name"]
        field = build_field(target)
        path = ROOT / "raw" / "evaluations" / name / f"{1:05d}-{target['candidate_index']:05d}.jsonl"
        rows = [json.loads(line) for line in path.read_text().splitlines()[1:]]
        chosen = [rows[-1]]
        skipped = [row for row in rows[:-1] if row["status"] == "COUNTED" and row["checks"]["x9_reference_accept"]]
        if skipped:
            chosen.append(skipped[0])
        records.extend(certify(target, row, field, pari) for row in chosen)
    if not all(record["group_order_certified"] for record in records):
        raise ArithmeticError("binary certificate failed")
    output = ROOT / "raw" / "binary_order_certificates.json"
    if output.exists():
        raise FileExistsError(output)
    output.write_text(json.dumps({"method": "independent_scalar_multiplication_plus_hasse",
                                  "certificates": records}, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"certificates": len(records), "all_certified": True,
                      "indices": [(row["target"], row["index"]) for row in records],
                      "sha256": hashlib.sha256(output.read_bytes()).hexdigest()}, sort_keys=True))


if __name__ == "__main__":
    main()
