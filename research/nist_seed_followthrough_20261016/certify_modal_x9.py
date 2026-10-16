#!/usr/bin/env python3
"""Independently certify every exact-X9 survivor with subgroup points."""

import argparse
import hashlib
import json
import os
import platform
import sys
import time
from pathlib import Path

from cypari2 import Pari


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
PREVIOUS = REPO / "research/nist_seed_selection_20261016"
sys.path.insert(0, str(PREVIOUS))
from certify_prime_orders import first_point, multiply  # noqa: E402


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def smooth_255(h):
    for prime in range(2, 256):
        if all(prime % divisor for divisor in range(2, int(prime**0.5) + 1)):
            while h % prime == 0:
                h //= prime
    return h == 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--attempt", default="modalfull1")
    args = parser.parse_args()
    campaign = HERE / "raw" / f"modal_campaign_{args.attempt}"
    summary_path = campaign / "x9_summary.json"
    output = campaign / "accepted_root_certificates.jsonl"
    partial = output.with_suffix(".jsonl.partial")
    if output.exists() or partial.exists():
        raise FileExistsError(output)
    summary = json.loads(summary_path.read_text())
    if summary["scope"] != "complete exact near-prime X9 public-reference count for six distinct prime streams":
        raise AssertionError("X9 summary is incomplete")
    targets = {item["name"]: item for item in json.loads((PREVIOUS / "targets.json").read_text())}
    work = {}
    for rep, mappings in summary["accepted_roots_by_stream"].items():
        for mapping, roots in mappings.items():
            for root in roots:
                key = (rep, root["index"], int(root["b"], 16))
                item = {"representative": rep, "index": root["index"],
                        "seed": root["seed"], "b": root["b"],
                        "order": root["order"],
                        "smooth_cofactor": root["smooth_cofactor"],
                        "prime_subgroup": root["prime_subgroup"]}
                if key in work:
                    if any(work[key][name] != item[name] for name in item):
                        raise AssertionError("two mappings disagree about one curve")
                    work[key]["mappings"].append(mapping)
                else:
                    item["mappings"] = [mapping]
                    work[key] = item
    sources = {}
    needed_sources = {(rep, index) for rep, index, _ in work}
    with (PREVIOUS / "raw/candidates.jsonl").open() as source:
        for line in source:
            row = json.loads(line)
            key = (row["target"], row["index"])
            if key in needed_sources:
                sources[key] = row
    pari = Pari()
    pari.allocatemem(512 * 1024 * 1024)
    fields = {rep: bool(pari.isprime(int(targets[rep]["p"])))
              for rep, _, _ in work}
    if not all(fields.values()):
        raise AssertionError("a tested field is composite")
    with partial.open("x") as sink:
        sink.write(json.dumps({"record": "certificate_run",
                               "summary_sha256": digest(summary_path),
                               "candidate_sha256": digest(PREVIOUS / "raw/candidates.jsonl"),
                               "script_sha256": digest(Path(__file__)),
                               "expected_distinct_curves": len(work),
                               "python": platform.python_version(),
                               "pari_version": str(pari("version()")),
                               "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())},
                              sort_keys=True) + "\n")
        for key in sorted(work):
            item = work[key]
            rep, index, b = key
            p = int(targets[rep]["p"])
            source = sources[(rep, index)]
            h = int(item["smooth_cofactor"])
            r = int(item["prime_subgroup"])
            n = int(item["order"])
            mapping_ok = {}
            for mapping in item["mappings"]:
                name = "nist_fips_186_2" if mapping == "unmasked" else "ansi_x9_62_1998"
                variant = source["variants"][name]
                mapping_ok[mapping] = (variant["reason"] == "nonsingular" and
                                       b in [int(x, 16) for x in variant["b_roots"]] and
                                       int(variant["c"], 16) * b * b % p == -27 % p)
            point = first_point(p, b)
            projected = multiply(h, point, p)
            checks = {
                "field_prime_pari": fields[rep],
                "seed_matches_source": item["seed"] == source["seed"],
                "seed_mapping": all(mapping_ok.values()),
                "point_on_curve": (point[1] * point[1] - point[0] ** 3 + 3 * point[0] - b) % p == 0,
                "prime_subgroup_pari": bool(pari.isprime(r)),
                "cofactor_255_smooth": smooth_255(h),
                "order_factors": h * r == n,
                "subgroup_size": r > 2**160 and r * r > 16 * p,
                "mov20": all(pow(p, k, r) != 1 for k in range(1, 21)),
                "not_anomalous": n != p,
                "hasse_interval": (n - p - 1) ** 2 <= 4 * p,
                "projected_nonidentity": projected is not None,
                "subgroup_order": projected is not None and multiply(r, projected, p) is None,
            }
            record = {**item, "point_x": hex(point[0]), "point_y": hex(point[1]),
                      "checks": checks, "certified": all(checks.values())}
            sink.write(json.dumps(record, sort_keys=True) + "\n")
            sink.flush()
            if not record["certified"]:
                raise AssertionError(f"independent certificate failed: {key}")
    os.replace(partial, output)
    print(json.dumps({"output": str(output), "sha256": digest(output),
                      "certified_curves": len(work)}, sort_keys=True))


if __name__ == "__main__":
    main()
