#!/usr/bin/env python3
"""Independent affine-multiplication certificates for known prime orders.

If a nonidentity point P satisfies [n]P = O for prime n and n itself lies in
the Hasse interval, then n divides #E and the interval contains only n when
n > 4 sqrt(p). This proves #E=n without relying on a point-counting oracle.
"""

import argparse
import hashlib
import json
import math
from pathlib import Path

from cypari2 import Pari

from generate_candidates import modular_sqrt


ROOT = Path(__file__).resolve().parent


def add(point, other, p):
    if point is None:
        return other
    if other is None:
        return point
    x1, y1 = point
    x2, y2 = other
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if x1 == x2:
        numerator = (3 * x1 * x1 - 3) % p
        denominator = (2 * y1) % p
    else:
        numerator = (y2 - y1) % p
        denominator = (x2 - x1) % p
    slope = numerator * pow(denominator, -1, p) % p
    x3 = (slope * slope - x1 - x2) % p
    return x3, (slope * (x1 - x3) - y1) % p


def multiply(k, point, p):
    result = None
    while k:
        if k & 1:
            result = add(result, point, p)
        point = add(point, point, p)
        k >>= 1
    return result


def first_point(p, b):
    for x in range(1000):
        rhs = (x * x * x - 3 * x + b) % p
        y = modular_sqrt(rhs, p)
        if y is not None and y != 0:
            return x, y
    raise ArithmeticError("no point found in first 1000 x coordinates")


def certify(name, p, b, n, pari):
    n_prime = bool(pari.isprime(n))
    point = first_point(p, b)
    on_curve = (point[1] ** 2 - point[0] ** 3 + 3 * point[0] - b) % p == 0
    scalar_zero = multiply(n, point, p) is None
    n_in_hasse = (n - p - 1) ** 2 <= 4 * p
    unique_multiple = n * n > 16 * p
    result = {"name": name, "p": str(p), "b": hex(b), "n": str(n),
              "point_x": hex(point[0]), "point_y": hex(point[1]),
              "n_prime_pari": n_prime, "on_curve": on_curve,
              "n_times_point_identity": scalar_zero,
              "n_in_hasse_interval": n_in_hasse,
              "hasse_interval_narrower_than_n": unique_multiple}
    result["order_certified"] = all((n_prime, on_curve, scalar_zero, n_in_hasse, unique_multiple))
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--include-p256-876", action="store_true")
    args = parser.parse_args()
    target_rows = json.loads((ROOT / "targets.json").read_text())
    pari = Pari()
    result = []
    for row in target_rows:
        if row["kind"] == "prime":
            result.append(certify(row["name"] + ":published", int(row["p"]), int(row["published_b"]),
                                  int(row["published_subgroup_order"]), pari))
    if args.include_p256_876:
        p256 = next(row for row in target_rows if row["name"] == "P-256")
        evaluation = ROOT / "raw" / "evaluations" / "P-256" / "00876-00876.jsonl"
        candidate = json.loads(evaluation.read_text().splitlines()[1])
        if candidate["status"] != "COUNTED" or not candidate["canonical"]["family_accept"]:
            raise ArithmeticError("P-256 candidate 876 lacks an accepted exact-order result")
        result.append(certify("P-256:876", int(p256["p"]), int(candidate["canonical_b"], 16),
                              int(candidate["canonical"]["order"]), pari))
    if not all(row["order_certified"] for row in result):
        raise ArithmeticError("a known-order certificate failed")
    output = ROOT / "raw" / "prime_order_certificates.json"
    if output.exists():
        raise FileExistsError(output)
    output.write_text(json.dumps({"method": "independent_affine_scalar_multiplication_plus_hasse", "certificates": result},
                                 indent=2, sort_keys=True) + "\n")
    print(json.dumps({"certificates": len(result), "all_certified": True,
                      "sha256": hashlib.sha256(output.read_bytes()).hexdigest()}, sort_keys=True))


if __name__ == "__main__":
    main()
