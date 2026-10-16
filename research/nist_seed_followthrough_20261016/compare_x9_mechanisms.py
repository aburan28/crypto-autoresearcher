#!/usr/bin/env python3
"""Compare bounded CM and twist diagnostics on every certified X9 survivor."""

import argparse
import collections
import hashlib
import json
import platform
import sys
import time
from pathlib import Path

from compare_mechanisms import primes_to, small_factors, square_cm_fields, CM_FIELDS


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
PREVIOUS = REPO / "research/nist_seed_selection_20261016"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--attempt", default="modalfull1")
    args = parser.parse_args()
    directory = HERE / "raw" / f"modal_campaign_{args.attempt}"
    summary_path = directory / "x9_summary.json"
    cert_path = directory / "accepted_root_certificates.jsonl"
    output = directory / "mechanism_comparison.json"
    if output.exists():
        raise FileExistsError(output)
    summary = json.loads(summary_path.read_text())
    lines = [json.loads(line) for line in cert_path.read_text().splitlines()]
    header, certs = lines[0], lines[1:]
    if (header["summary_sha256"] != digest(summary_path) or
            header["expected_distinct_curves"] != len(certs) or
            not all(item["certified"] for item in certs)):
        raise AssertionError("certificates missing or unbound")
    target_list = json.loads((PREVIOUS / "targets.json").read_text())
    targets = {item["name"]: item for item in target_list}
    rep_by_name = {name: rep for rep, group in (
        ("prime192v2", ("P-192", "prime192v2", "prime192v3")),
        ("prime239v3", ("prime239v1", "prime239v2", "prime239v3")),
        ("P-224", ("P-224",)), ("P-256", ("P-256",)),
        ("P-384", ("P-384",)), ("P-521", ("P-521",)))
        for name in group}
    published = collections.defaultdict(list)
    for target in target_list:
        if target["kind"] == "prime":
            rep = rep_by_name[target["name"]]
            published[(rep, target["candidate_index"])].append(target)
    prior = json.loads((PREVIOUS / "raw/full_census_crosscheck_v4.json").read_text())
    skipped = {(rep, index) for rep in summary["accepted_roots_by_stream"]
               for index in prior["streams"][rep]["screen_skipped"]}
    secp_p = int("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F", 16)
    secp_n = int("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141", 16)
    control = square_cm_fields((secp_p + 1 - secp_n) ** 2 - 4 * secp_p)
    if not any(item["fundamental_discriminant"] == -3 for item in control):
        raise AssertionError("secp256k1 positive CM control failed")
    if square_cm_fields((secp_p + 1 - secp_n) ** 2 - 4 * secp_p - 1):
        raise AssertionError("perturbed CM negative control failed")
    primes = primes_to(10000)
    rows = []
    seen = set()
    for cert in certs:
        rep, index, b = cert["representative"], cert["index"], int(cert["b"], 16)
        key = (rep, index, b)
        if key in seen:
            raise AssertionError("duplicate certified root")
        seen.add(key)
        p, n = int(targets[rep]["p"]), int(cert["order"])
        named = [target["name"] for target in published.get((rep, index), ())
                 if b == int(target["published_b"]) and
                 n == int(target["published_subgroup_order"])]
        category = ("published_curve" if named else
                    "published_seed_other_curve" if (rep, index) in published else
                    "reported_skip" if (rep, index) in skipped else "other_candidate")
        trace = p + 1 - n
        delta = trace * trace - 4 * p
        twist = 2 * (p + 1) - n
        factors, product, residual = small_factors(twist, primes)
        rows.append({"representative": rep, "index": index, "seed": cert["seed"],
                     "b": cert["b"], "order": cert["order"],
                     "mappings": cert["mappings"], "category": category,
                     "published_name": named,
                     "trace": str(trace), "frobenius_discriminant": str(delta),
                     "small_cm_field_matches": square_cm_fields(delta),
                     "twist_order": str(twist), "twist_factors_at_most_10000": factors,
                     "twist_small_factor_product": str(product),
                     "twist_residual_after_small_trial_division": str(residual)})
    rows.sort(key=lambda row: (row["representative"], row["index"], int(row["b"], 16)))
    categories = collections.defaultdict(list)
    for row in rows:
        categories[row["category"]].append(row)
    summary_by_category = {
        category: {"branches": len(group),
                   "seeds": len({(row["representative"], row["index"]) for row in group}),
                   "nine_cm_field_matches": sum(bool(row["small_cm_field_matches"])
                                                for row in group),
                   "twist_has_prime_factor_at_most_10000": sum(
                       bool(row["twist_factors_at_most_10000"]) for row in group)}
        for category, group in sorted(categories.items())}
    result = {"status": "complete_bounded_comparison",
              "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
              "command": sys.argv, "python": platform.python_version(),
              "script_sha256": digest(Path(__file__)),
              "x9_summary_sha256": digest(summary_path),
              "certificates_sha256": digest(cert_path),
              "prior_crosscheck_sha256": digest(PREVIOUS / "raw/full_census_crosscheck_v4.json"),
              "cm_fields_tested": CM_FIELDS, "twist_trial_prime_limit": 10000,
              "secp256k1_positive_control": control,
              "by_category": summary_by_category,
              "cm_match_count": sum(bool(row["small_cm_field_matches"]) for row in rows),
              "rows": rows,
              "limitations": ["CM predicate concerns nine fields and Fp-rational isogenies only",
                              "small twist factors are conditional implementation diagnostics",
                              "twist residuals are not fully factored"]}
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"output": str(output), "sha256": digest(output),
                      "branches": len(rows), "by_category": summary_by_category,
                      "cm_match_count": result["cm_match_count"]}, sort_keys=True))


if __name__ == "__main__":
    main()
