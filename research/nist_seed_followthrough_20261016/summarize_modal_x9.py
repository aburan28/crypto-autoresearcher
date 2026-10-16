#!/usr/bin/env python3
"""Validate every returned X9 count and apply the frozen public criteria."""

import argparse
import collections
import hashlib
import json
import math
import platform
import sys
import time
from pathlib import Path

from cypari2 import Pari


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
PREVIOUS = REPO / "research/nist_seed_selection_20261016"
ENDPOINTS = ("P-521", "P-384", "P-224", "P-256", "prime239v3", "prime192v2")
CENSUS = {"P-521": 871002724, "P-384": 872952608,
          "P-224": 891607927, "P-256": 871696354,
          "prime239v3": 863711343, "prime192v2": 863966734}
REPRESENTATIVE = {
    "prime192v2": ("P-192", "prime192v3", "prime192v2"),
    "prime239v3": ("prime239v1", "prime239v2", "prime239v3"),
    "P-224": ("P-224",), "P-256": ("P-256",),
    "P-384": ("P-384",), "P-521": ("P-521",),
}
PRIMES = tuple(x for x in range(2, 256)
               if all(x % divisor for divisor in range(2, math.isqrt(x) + 1)))
LMAX = (7, 15, 31, 63, 127, 255)
RBITS = (160, 180, 200)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_campaign(attempt):
    directory = HERE / "raw" / f"modal_campaign_{attempt}"
    plan_path, events_path, stop_path = (directory / part for part in
                                         ("plan.json", "events.jsonl", "stop.json"))
    plan, stop = json.loads(plan_path.read_text()), json.loads(stop_path.read_text())
    if (plan["mode"] != "full" or stop["status"] != "complete" or
            stop["total_shards"] != 221 or stop["successful_shards"] != 221 or
            stop["plan_sha256"] != digest(plan_path) or
            stop["events_sha256"] != digest(events_path)):
        raise AssertionError("full campaign plan/stop mismatch")
    for rel, frozen_sha in plan["input_sha256"].items():
        if digest(REPO / rel) != frozen_sha:
            raise AssertionError(f"source changed: {rel}")
    items = [tuple(item) for item in plan["items"]]
    if len(items) != 221 or sum(end - start + 1 for _, start, end, _ in items) != 21753:
        raise AssertionError("full grid is incomplete")
    events = [json.loads(line) for line in events_path.read_text().splitlines()]
    if len(events) != len(items):
        raise AssertionError("event count differs from plan")
    by_item = {}
    for event in events:
        key = tuple(event["item"])
        if key in by_item or key not in items:
            raise AssertionError("duplicate or out-of-plan event")
        by_item[key] = event
    candidates = {}
    with (PREVIOUS / "raw/candidates.jsonl").open() as source:
        for line in source:
            item = json.loads(line)
            if item["target"] in ENDPOINTS:
                candidates[(item["target"], item["index"])] = item
    rows = collections.defaultdict(dict)
    shard_hashes = {}
    for item in items:
        event = by_item[item]
        target, start, end, attempt_in_item = item
        if (event["item"] != list(item) or event["verification"] != "PASS" or
                event["status"] != "PROCESS_OK" or event["returncode"] != 0 or
                event["artifact_status"] != "complete_file" or
                attempt_in_item != attempt):
            raise AssertionError(f"shard not verified: {item}")
        path = REPO / event["local_path"]
        if digest(path) != event["local_sha256"] or digest(path) != event["data_sha256"]:
            raise AssertionError(f"shard changed: {path}")
        shard_hashes[event["local_path"]] = digest(path)
        lines = path.read_text().splitlines()
        header = json.loads(lines[0])
        if (header["record"] != "run" or header["target"] != target or
                header["start"] != start or header["end"] != end or
                header["script_sha256"] != plan["input_sha256"][
                    "research/nist_seed_followthrough_20261016/count_x9.py"] or
                header["targets_sha256"] != plan["input_sha256"][
                    "research/nist_seed_selection_20261016/targets.json"] or
                header["candidates_sha256"] != plan["input_sha256"][
                    "research/nist_seed_selection_20261016/raw/candidates.jsonl"] or
                header["census_sha256"] != plan["input_sha256"][
                    f"research/nist_seed_provenance_20261016/census/orders_{CENSUS[target]}.txt"] or
                header["gp_version"] != event["gp_version"] or
                len(lines) != end - start + 2):
            raise AssertionError(f"shard header/length mismatch: {path}")
        for index, line in enumerate(lines[1:], start):
            row = json.loads(line)
            source = candidates[(target, index)]
            if (row["target"] != target or row["index"] != index or
                    row["seed"] != source["seed"] or row["status"] != "COMPLETE" or
                    index in rows[target]):
                raise AssertionError(f"candidate mismatch: {target}:{index}")
            rows[target][index] = row
    targets = {target["name"]: target for target in json.loads(
        (PREVIOUS / "targets.json").read_text())}
    for target in ENDPOINTS:
        if set(rows[target]) != set(range(1, targets[target]["candidate_index"] + 1)):
            raise AssertionError(f"stream missing positions: {target}")
    return plan_path, events_path, shard_hashes, candidates, rows, targets


def make_order_checker(pari):
    primality = {}
    checks = {}
    def isprime(n):
        if n not in primality:
            primality[n] = (n > 1 and bool(pari.ispseudoprime(n)) and
                            bool(pari.isprime(n)))
        return primality[n]
    def check(p, n):
        key = (p, n)
        if key in checks:
            return checks[key]
        if (n - p - 1) ** 2 > 4 * p:
            raise AssertionError("count outside Hasse interval")
        remainder = n
        h = 1
        by_lmax = {}
        small_index = 0
        for limit in LMAX:
            while small_index < len(PRIMES) and PRIMES[small_index] <= limit:
                small = PRIMES[small_index]
                while remainder % small == 0:
                    remainder //= small
                    h *= small
                small_index += 1
            prime = isprime(remainder) if remainder > 2**160 else False
            mov = prime and all(pow(p, k, remainder) != 1 for k in range(1, 21))
            by_lmax[limit] = {
                "smooth_cofactor": str(h), "prime_subgroup": str(remainder),
                "prime_pari": prime, "mov20": bool(mov),
                "accepted_rbits": [bits for bits in RBITS
                                   if prime and mov and n != p and
                                   remainder > 2**bits and remainder * remainder > 16 * p],
            }
        checks[key] = by_lmax
        return by_lmax
    return check, primality


def variant_roots(row, source, mapping, p, check):
    variant_name = "nist_fips_186_2" if mapping == "unmasked" else "ansi_x9_62_1998"
    variant = source["variants"][variant_name]
    item = row["unmasked" if mapping == "unmasked" else "strict_x9"]
    if item["status"] == "REUSED_UNMASKED":
        if not row["same_c"] or variant["c"] != source["variants"]["nist_fips_186_2"]["c"]:
            raise AssertionError("strict mapping reuse mismatch")
        item = row["unmasked"]
    if item["status"] == "NO_CURVE":
        if variant["reason"] == "nonsingular":
            raise AssertionError("valid coefficient marked NO_CURVE")
        return []
    if item["status"] != "COUNTED" or variant["reason"] != "nonsingular":
        raise AssertionError(f"unrecognized mapping state: {item['status']}")
    b = int(item["canonical_b"])
    roots = [int(value, 16) for value in variant["b_roots"]]
    if (variant["c"] != item["c"] or set(roots) != {b, p - b} or
            int(item["canonical_order"]) + int(item["other_order"]) !=
            (2 * (p + 1) if p % 4 == 3 else 2 * int(item["canonical_order"]))):
        raise AssertionError("coefficient, roots or twist identity mismatch")
    records = []
    for side, root_b, order in (("canonical", b, int(item["canonical_order"])),
                                ("other", p - b, int(item["other_order"]))):
        records.append({"side": side, "b": hex(root_b), "order": str(order),
                        "criteria": check(p, order)})
    return records


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--attempt", default="modalfull1")
    args = parser.parse_args()
    plan_path, events_path, hashes, candidates, rows, targets = load_campaign(args.attempt)
    output = HERE / "raw" / f"modal_campaign_{args.attempt}" / "x9_summary.json"
    if output.exists():
        raise FileExistsError(output)
    pari = Pari()
    pari.allocatemem(512 * 1024 * 1024)
    field_prime = {rep: bool(pari.isprime(int(targets[rep]["p"]))) for rep in ENDPOINTS}
    if not all(field_prime.values()):
        raise AssertionError("a field modulus is composite")
    check, primality = make_order_checker(pari)
    eligible = collections.defaultdict(lambda: collections.defaultdict(list))
    states = collections.defaultdict(lambda: collections.Counter())
    sensitivity = collections.defaultdict(lambda: collections.defaultdict(
        lambda: collections.defaultdict(set)))
    for rep in ENDPOINTS:
        p = int(targets[rep]["p"])
        for index in sorted(rows[rep]):
            row = rows[rep][index]
            source = candidates[(rep, index)]
            for mapping in ("unmasked", "strict_x9"):
                roots = variant_roots(row, source, mapping, p, check)
                states[rep][mapping + ":valid_coefficient"] += bool(roots)
                for root in roots:
                    for limit, result in root["criteria"].items():
                        for bits in result["accepted_rbits"]:
                            sensitivity[rep][mapping][f"lmax={limit},r>2^{bits}"].add(index)
                    if 160 in root["criteria"][255]["accepted_rbits"]:
                        eligible[rep][mapping].append({"index": index, "seed": row["seed"],
                                                       "side": root["side"], "b": root["b"],
                                                       "order": root["order"],
                                                       "smooth_cofactor": root["criteria"][255]["smooth_cofactor"],
                                                       "prime_subgroup": root["criteria"][255]["prime_subgroup"]})
    named = {}
    for rep, names in REPRESENTATIVE.items():
        for name in names:
            end = targets[name]["candidate_index"]
            previous = {targets[older]["candidate_index"]: older for older in names
                        if targets[older]["candidate_index"] < end}
            named[name] = {"representative": rep, "published_index": end,
                           "prior_published": previous, "mappings": {}}
            for mapping in ("unmasked", "strict_x9"):
                earlier = [root for root in eligible[rep][mapping] if root["index"] < end]
                anchor = [root for root in eligible[rep][mapping] if root["index"] == end]
                anchor_exact = any(int(root["b"], 16) == int(targets[name]["published_b"])
                                   and int(root["order"]) == int(targets[name]["published_subgroup_order"])
                                   for root in anchor)
                by_index = collections.defaultdict(list)
                for root in earlier:
                    by_index[root["index"]].append(root)
                prior_exact = []
                for index, roots in by_index.items():
                    older = previous.get(index)
                    if older and any(int(root["b"], 16) == int(targets[older]["published_b"])
                                     and int(root["order"]) == int(targets[older]["published_subgroup_order"])
                                     for root in roots):
                        prior_exact.append(index)
                named[name]["mappings"][mapping] = {
                    "published_anchor_same_curve": anchor_exact,
                    "earlier_eligible_seed_count": len(by_index),
                    "earlier_eligible_root_count": len(earlier),
                    "earlier_eligible_indices": sorted(by_index),
                    "earlier_unpublished_seed_count": len(by_index) - len(prior_exact),
                    "prior_published_exact_indices": sorted(prior_exact),
                    "eligible_root_records": earlier,
                    "sensitivity_seed_count": {
                        f"lmax={limit},r>2^{bits}":
                            sum(i < end for i in sensitivity[rep][mapping][
                                f"lmax={limit},r>2^{bits}"])
                        for limit in LMAX for bits in RBITS},
                }
    prior_crosscheck = json.loads((PREVIOUS / "raw/full_census_crosscheck_v4.json").read_text())
    skip_replay = {}
    for rep in ENDPOINTS:
        indices = prior_crosscheck["streams"][rep]["screen_skipped"]
        skip_replay[rep] = {str(i): {mapping: [root for root in eligible[rep][mapping]
                                               if root["index"] == i]
                                      for mapping in ("unmasked", "strict_x9")}
                            for i in indices}
    summary = {
        "scope": "complete exact near-prime X9 public-reference count for six distinct prime streams",
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "command": sys.argv, "python": platform.python_version(),
        "pari_version": str(pari("version()")),
        "plan_sha256": digest(plan_path), "events_sha256": digest(events_path),
        "shard_sha256": hashes, "candidate_positions": sum(map(len, rows.values())),
        "primality_inputs_checked": len(primality),
        "field_prime_pari": field_prime,
        "criteria": {"lmax": list(LMAX), "r_bits": list(RBITS), "mov_degree_max": 20,
                     "hasse_factor": 4, "exclude_anomalous": True},
        "mapping_states": {rep: dict(counter) for rep, counter in states.items()},
        "accepted_roots_by_stream": {
            rep: {mapping: roots for mapping, roots in variants.items()}
            for rep, variants in eligible.items()},
        "named_targets": named, "known_skips": skip_replay,
        "limitations": ["September 1998 draft is later than the recovered 1997 timestamps",
                        "historical lmax, rmin, root choice, restart count and stopping rule remain unknown"]}
    output.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"output": str(output), "sha256": digest(output),
                      "named_eligible": {name: {mapping: detail["earlier_eligible_seed_count"]
                                               for mapping, detail in target["mappings"].items()}
                                         for name, target in named.items()}}, sort_keys=True))


if __name__ == "__main__":
    main()
