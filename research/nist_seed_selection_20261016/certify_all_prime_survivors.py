#!/usr/bin/env python3
"""Independently certify every X9-reference prime survivor's group order."""

import hashlib
import json
from pathlib import Path

from cypari2 import Pari

from certify_prime_orders import first_point, multiply
from summarize_family_campaign import REPRESENTATIVE


ROOT = Path(__file__).resolve().parent
SUMMARY = ROOT / "raw" / "x9_campaign" / "x9_summary.json"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def smooth_255(h):
    for prime in range(2, 256):
        if all(prime % d for d in range(2, int(prime**0.5) + 1)):
            while h % prime == 0:
                h //= prime
    return h == 1


def main():
    output = ROOT / "raw" / "x9_campaign" / "prime_survivor_certificates.jsonl"
    if output.exists() or output.with_suffix(output.suffix + ".partial").exists():
        raise FileExistsError(output)
    summary = json.loads(SUMMARY.read_text())
    if summary["scope"] != "complete 255-smooth X9 reference on six unique prime streams and ten named targets":
        raise ArithmeticError("X9 summary incomplete")
    targets = {item["name"]: item for item in json.loads((ROOT / "targets.json").read_text())}
    sources = {}
    for line in (ROOT / "raw" / "candidates.jsonl").open():
        item = json.loads(line)
        if item["target"] in REPRESENTATIVE:
            sources[(item["target"], item["index"])] = item
    work = {}
    for rep in REPRESENTATIVE:
        target = summary["named_targets"][rep]
        for mapping, data in target["mappings"].items():
            for item in data["earlier_reference_eligible"]:
                for root in item["roots"]:
                    key = (rep, item["index"], int(root["b"], 16))
                    instance = {"rep": rep, "index": item["index"], "seed": item["seed"],
                                "b": int(root["b"], 16), "h": int(root["smooth_cofactor"]),
                                "n": int(root["prime_subgroup"]),
                                "group_order": int(root["group_order"]),
                                "mappings": [mapping]}
                    if key in work:
                        old = work[key]
                        if any(old[field] != instance[field] for field in
                               ("seed", "h", "n", "group_order")):
                            raise ArithmeticError(f"duplicate curve disagreement: {key}")
                        old["mappings"].append(mapping)
                    else:
                        work[key] = instance
    pari = Pari()
    field_prime = {rep: bool(pari.isprime(int(targets[rep]["p"]))) for rep in REPRESENTATIVE}
    if not all(field_prime.values()):
        raise ArithmeticError("a published field is not prime")
    partial = output.with_suffix(output.suffix + ".partial")
    with partial.open("w") as sink:
        sink.write(json.dumps({"record": "certificate_run", "x9_summary_sha256": digest(SUMMARY),
                               "candidate_sha256": digest(ROOT / "raw" / "candidates.jsonl"),
                               "method": "independent affine scalar multiplication plus Hasse uniqueness",
                               "expected_curves": len(work)}, sort_keys=True) + "\n")
        for key in sorted(work):
            item = work[key]
            rep, index, b = key
            p = int(targets[rep]["p"])
            source = sources[(rep, index)]
            if item["seed"] != source["seed"]:
                raise ArithmeticError(f"seed mismatch: {key}")
            mapping_ok = {}
            for mapping in item["mappings"]:
                variant = source["variants"]["nist_fips_186_2" if mapping == "unmasked" else "ansi_x9_62_1998"]
                c = int(variant["c"], 16)
                mapping_ok[mapping] = (variant["reason"] == "nonsingular" and
                                       b in (int(root, 16) for root in variant["b_roots"]) and
                                       c * b * b % p == -27 % p)
            h, n, N = item["h"], item["n"], item["group_order"]
            point = first_point(p, b)
            projected = multiply(h, point, p)
            checks = {
                "field_prime_pari": field_prime[rep],
                "seed_mapping": all(mapping_ok.values()),
                "on_curve": (point[1] * point[1] - point[0] ** 3 + 3 * point[0] - b) % p == 0,
                "subgroup_prime_pari": bool(pari.isprime(n)),
                "cofactor_255_smooth": smooth_255(h),
                "order_factors": h * n == N,
                "subgroup_size": n > 2**160 and n * n > 16 * p,
                "mov20": all(pow(p, i, n) != 1 for i in range(1, 21)),
                "not_anomalous": N != p,
                "hasse": (N - p - 1) ** 2 <= 4 * p,
                "projected_nonidentity": projected is not None,
                "subgroup_point_order": projected is not None and multiply(n, projected, p) is None,
            }
            record = {"representative_stream": rep, "index": index, "seed": item["seed"],
                      "b": hex(b), "h": str(h), "n": str(n), "group_order": str(N),
                      "mappings": item["mappings"], "point_x": hex(point[0]),
                      "point_y": hex(point[1]), "checks": checks,
                      "group_order_certified": all(checks.values())}
            sink.write(json.dumps(record, sort_keys=True) + "\n")
            sink.flush()
            if not record["group_order_certified"]:
                raise ArithmeticError(f"independent certificate failed: {key}")
    partial.rename(output)
    print(json.dumps({"certified_curves": len(work), "sha256": digest(output)}, sort_keys=True))


if __name__ == "__main__":
    main()
