#!/usr/bin/env python3
"""Independent certificates for the first three P-256 family survivors."""

import hashlib
import json
from pathlib import Path

from cypari2 import Pari

from certify_prime_orders import certify


ROOT = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    output = ROOT / "raw" / "p256_early_root_certificates.json"
    if output.exists():
        raise FileExistsError(output)
    p = int(next(row for row in json.loads((ROOT / "targets.json").read_text())
                 if row["name"] == "P-256")["p"])
    source_paths = (ROOT / "raw" / "family_evaluations" / "P-256" / "00001-00300.jsonl",
                    ROOT / "raw" / "evaluations" / "P-256" / "00876-00876.jsonl")
    candidates = {}
    for path in source_paths:
        for line in path.read_text().splitlines()[1:]:
            row = json.loads(line)
            if row["index"] in (81, 276, 876):
                candidates[row["index"]] = row
    if set(candidates) != {81, 276, 876}:
        raise ArithmeticError("missing exact P-256 rows")
    pari = Pari()
    records = []
    for index, side in ((81, "other"), (276, "other"), (876, "canonical")):
        row = candidates[index]
        if not row[side]["family_accept"] or row["status"] != "COUNTED":
            raise ArithmeticError(f"P-256:{index} is not accepted on {side}")
        b = int(row[f"{side}_b"], 16)
        n = int(row[side]["order"])
        certificate = certify(f"P-256:{index}:{side}", p, b, n, pari)
        certificate.update({"index": index, "root_branch": side, "seed": row["seed"],
                            "strict_x9_seed_mapping_matches": row["strict_x9_same_c"]})
        if not certificate["order_certified"]:
            raise ArithmeticError(f"independent P-256 certificate failed: {index}")
        records.append(certificate)
    result = {"source_sha256": {str(path.relative_to(ROOT)): digest(path) for path in source_paths},
              "method": "independent affine scalar multiplication plus Hasse uniqueness",
              "certificates": records, "all_certified": True}
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"certificates": len(records), "all_certified": True,
                      "sha256": digest(output)}, sort_keys=True))


if __name__ == "__main__":
    main()
