#!/usr/bin/env python3
"""Run deterministic coefficient and basis-conversion controls."""

import hashlib
import json
from pathlib import Path

from binary_basis import normal_to_polynomial
from generate_candidates import MASK160, binary_b, prime_c


ROOT = Path(__file__).resolve().parent


def main() -> None:
    targets = {row["name"]: row for row in json.loads((ROOT / "targets.json").read_text())}
    prime = targets["P-256"]
    p = int(prime["p"])
    seed = int(prime["published_seed"], 16)
    published_b = int(prime["published_b"])
    c = prime_c(seed, p, "nist_fips_186_2")
    changed_c = prime_c((seed ^ 1) & MASK160, p, "nist_fips_186_2")
    binary = targets["B-233"]
    m = binary["m"]
    poly = int(binary["polynomial"], 16)
    binary_seed = int(binary["published_seed"], 16)
    normal = binary_b(binary_seed, m)
    changed_normal = binary_b(binary_seed ^ 1, m)
    results = {
        "prime_published_seed_matches": (c * published_b * published_b + 27) % p == 0,
        "prime_altered_seed_rejected": (changed_c * published_b * published_b + 27) % p != 0,
        "prime_altered_coefficient_rejected": (c * ((published_b + 1) % p) ** 2 + 27) % p != 0,
        "prime_singular_coefficient_rejected": (-108 + 27 * 2 * 2) % p == 0,
        "binary_published_normal_to_polynomial_matches": normal_to_polynomial(normal, m, poly) == int(binary["published_b"]),
        "binary_altered_seed_rejected": normal_to_polynomial(changed_normal, m, poly) != int(binary["published_b"]),
        "binary_basis_linearity": normal_to_polynomial(normal ^ changed_normal, m, poly)
        == normal_to_polynomial(normal, m, poly) ^ normal_to_polynomial(changed_normal, m, poly),
    }
    for row in targets.values():
        if row["kind"] == "binary":
            b = normal_to_polynomial(binary_b(int(row["published_seed"], 16), row["m"]), row["m"], int(row["polynomial"], 16))
            results[row["name"] + "_anchor_coefficient_matches"] = b == int(row["published_b"])
        else:
            c = prime_c(int(row["published_seed"], 16), int(row["p"]), "nist_fips_186_2")
            results[row["name"] + "_anchor_coefficient_matches"] = (c * int(row["published_b"]) ** 2 + 27) % int(row["p"]) == 0
    if not all(results.values()):
        raise ArithmeticError("a deterministic control failed")
    output = ROOT / "raw" / "controls.json"
    if output.exists():
        raise FileExistsError(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({"results": results, "all_passed": True}, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"controls": len(results), "all_passed": True, "sha256": hashlib.sha256(output.read_bytes()).hexdigest()}))


if __name__ == "__main__":
    main()
