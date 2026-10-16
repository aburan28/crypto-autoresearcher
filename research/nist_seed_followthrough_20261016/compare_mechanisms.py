#!/usr/bin/env python3
"""Exact, bounded CM and twist diagnostics for all certified eligible roots."""

import hashlib
import json
import math
import platform
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
OLD = REPO / "research/nist_seed_selection_20261016"
CM_FIELDS = (-3, -4, -7, -8, -11, -19, -43, -67, -163)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def primes_to(limit):
    sieve = bytearray(b"\x01") * (limit + 1)
    sieve[0:2] = b"\x00\x00"
    for d in range(2, math.isqrt(limit) + 1):
        if sieve[d]:
            sieve[d * d:limit + 1:d] = b"\x00" * (((limit - d * d) // d) + 1)
    return tuple(i for i, flag in enumerate(sieve) if flag)


def square_cm_fields(delta):
    matched = []
    for d in CM_FIELDS:
        if delta % d:
            continue
        q = delta // d
        if q >= 0 and math.isqrt(q) ** 2 == q:
            matched.append({"fundamental_discriminant": d,
                            "frobenius_conductor_candidate": str(math.isqrt(q))})
    return matched


def small_factors(n, primes):
    remainder = n
    factors = []
    product = 1
    for ell in primes:
        if remainder % ell:
            continue
        power = 0
        while remainder % ell == 0:
            power += 1
            remainder //= ell
            product *= ell
        factors.append([ell, power])
    if product * remainder != n:
        raise AssertionError("factor product mismatch")
    return factors, product, remainder


def main():
    output = HERE / "raw/mechanism_comparison.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        raise FileExistsError(output)
    cert_path = OLD / "raw/full_prime_order_certificates.jsonl"
    cross_path = OLD / "raw/full_census_crosscheck_v4.json"
    targets_path = OLD / "targets.json"
    cross = json.loads(cross_path.read_text())
    if cross["status"] != "validated":
        raise AssertionError("source census not validated")
    targets = json.loads(targets_path.read_text())
    by_name = {t["name"]: t for t in targets}
    by_run = defaultdict(list)
    for t in targets:
        if t["kind"] == "prime":
            by_run[t["unix_time"]].append(t)
    published = {(t["unix_time"], t["candidate_index"]): t["name"]
                 for t in targets if t["kind"] == "prime"}
    primes = primes_to(10000)
    lines = [json.loads(line) for line in cert_path.read_text().splitlines()]
    header, records = lines[0], [x for x in lines if x.get("record") == "certificate"]
    if header["expected_branches"] != len(records) or len(records) != 82:
        raise AssertionError("certificate branch count mismatch")
    rows = []
    seen = set()
    for cert in records:
        key = (cert["run"], cert["index"], cert["side"])
        if key in seen or not cert["order_certified"] or not cert["n_prime_pari"]:
            raise AssertionError("duplicate or uncertified source branch")
        seen.add(key)
        target = by_name[cert["target"]]
        p, n = int(cert["p"]), int(cert["n"])
        if p != int(target["p"]) or cert["run"] != target["unix_time"]:
            raise AssertionError("field or stream mismatch")
        if cert["index"] not in cross["streams"][cert["target"]]["broad_family_both_seeded_roots"]:
            raise AssertionError("branch outside eligible census")
        trace = p + 1 - n
        delta = trace * trace - 4 * p
        twist = 2 * (p + 1) - n
        factors, product, residual = small_factors(twist, primes)
        mov20 = all(pow(p, k, n) != 1 for k in range(1, 21))
        if n == p or not mov20 or n <= 2**160 or n * n <= 16 * p:
            raise AssertionError("certified branch fails family criteria")
        rows.append({"stream": cert["target"], "run": cert["run"],
                     "index": cert["index"], "side": cert["side"],
                     "published_name": published.get((cert["run"], cert["index"])),
                     "p": str(p), "n": str(n), "b": cert["b"],
                     "trace": str(trace), "frobenius_discriminant": str(delta),
                     "small_cm_field_matches": square_cm_fields(delta),
                     "ordinary_nonanomalous_mov20": True,
                     "twist_order": str(twist),
                     "twist_factors_at_most_10000": factors,
                     "twist_small_factor_product": str(product),
                     "twist_residual_after_small_trial_division": str(residual)})
    rows.sort(key=lambda x: (x["run"], x["index"], x["side"]))
    seed_keys = {(x["run"], x["index"]) for x in rows}
    if len(seed_keys) != 69 or len(seed_keys & set(published)) != 10:
        raise AssertionError("seed-level comparison count mismatch")
    counts = Counter("published" if x["published_name"] else "earlier"
                     for x in rows)
    output.write_text(json.dumps({
        "status": "complete_bounded_screen", "created_utc":
        time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "command": sys.argv, "python": platform.python_version(),
        "script_sha256": digest(Path(__file__)),
        "inputs_sha256": {str(path.relative_to(REPO)): digest(path)
                          for path in (cert_path, cross_path, targets_path)},
        "scope": "82 certified cofactor-one root branches in 69 seed slots, six fixed prime streams",
        "cm_fields_tested": CM_FIELDS, "twist_trial_prime_limit": 10000,
        "seed_count": len(seed_keys), "published_seed_count": len(seed_keys & set(published)),
        "branch_counts": counts, "cm_match_count": sum(bool(x["small_cm_field_matches"]) for x in rows),
        "rows": rows,
    }, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"path": str(output), "sha256": digest(output),
                      "seed_count": len(seed_keys), "branch_count": len(rows),
                      "cm_match_count": sum(bool(x["small_cm_field_matches"]) for x in rows)}))


if __name__ == "__main__":
    main()
