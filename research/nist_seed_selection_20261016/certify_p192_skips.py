#!/usr/bin/env python3
"""Independent certificates for strict-X9 earlier P-192 candidates."""

import hashlib
import json
from pathlib import Path

from cypari2 import Pari

from certify_prime_orders import first_point, multiply


ROOT = Path(__file__).resolve().parent


def main():
    target = next(row for row in json.loads((ROOT / "targets.json").read_text()) if row["name"] == "P-192")
    p = int(target["p"])
    generated = {}
    for line in (ROOT / "raw" / "candidates.jsonl").open():
        row = json.loads(line)
        if row["target"] == "P-192":
            generated[row["index"]] = row
    evaluations = [json.loads(line) for line in (ROOT / "raw" / "evaluations" / "P-192" / "00001-00139.jsonl").read_text().splitlines()[1:]]
    pari = Pari()
    records = []
    for row in evaluations:
        if row["index"] == target["candidate_index"] or row["status"] != "COUNTED":
            continue
        source = generated[row["index"]]
        if source["variants"]["nist_fips_186_2"]["c"] != source["variants"]["ansi_x9_62_1998"]["c"]:
            continue
        for branch in ("canonical", "other"):
            order = row[branch]
            if not order["x9_reference_accept"]:
                continue
            b = int(row["canonical_b"] if branch == "canonical" else row["other_b"], 16)
            h = int(order["x9_255_smooth_cofactor"])
            n = int(order["x9_remainder"])
            point = first_point(p, b)
            projected = multiply(h, point, p)
            certificate = {
                "target": "P-192", "index": row["index"], "seed": row["seed"],
                "root_branch": branch, "b": hex(b), "h": str(h), "n": str(n),
                "point_x": hex(point[0]), "point_y": hex(point[1]),
                "h_times_point_nonidentity": projected is not None,
                "n_times_h_times_point_identity": projected is not None and multiply(n, projected, p) is None,
                "n_prime_pari": bool(pari.isprime(n)),
                "hn_in_hasse_interval": (h * n - p - 1) ** 2 <= 4 * p,
                "hasse_interval_narrower_than_n": n * n > 16 * p,
                "strict_x9_seed_mapping_matches": True,
                "x9_order_reference_accept": True,
            }
            certificate["group_order_certified"] = all(certificate[key] for key in (
                "h_times_point_nonidentity", "n_times_h_times_point_identity", "n_prime_pari",
                "hn_in_hasse_interval", "hasse_interval_narrower_than_n"))
            records.append(certificate)
    if not records or not all(record["group_order_certified"] for record in records):
        raise ArithmeticError("P-192 strict-X9 independent certificate failed")
    output = ROOT / "raw" / "p192_skipped_x9_certificates.json"
    if output.exists():
        raise FileExistsError(output)
    output.write_text(json.dumps({"method": "independent_affine_scalar_multiplication_plus_hasse",
                                  "certificates": records}, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"certificates": len(records), "all_certified": True,
                      "indices": sorted({row["index"] for row in records}),
                      "sha256": hashlib.sha256(output.read_bytes()).hexdigest()}, sort_keys=True))


if __name__ == "__main__":
    main()
