#!/usr/bin/env python3
"""Validate complete X9-reference shards and project their shared streams."""

import collections
import hashlib
import json
from pathlib import Path

from summarize_family_campaign import REPRESENTATIVE


ROOT = Path(__file__).resolve().parent
PLAN = ROOT / "raw" / "x9_campaign" / "plan.json"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fail(message):
    raise ArithmeticError(message)


def effective(row, mapping):
    item = row["unmasked"] if mapping == "unmasked" else row["strict_x9"]
    if item["status"] == "REUSED_UNMASKED":
        if not row["strict_x9_same_c"]:
            fail("reused different X9 coefficient")
        item = row["unmasked"]
    return item


def accepted_roots(row, mapping):
    item = effective(row, mapping)
    if item["status"].startswith("NO_CURVE_"):
        return []
    if item["status"] not in ("COUNTED", "REUSED_FAMILY_COUNT"):
        fail(f"unknown X9 status: {item['status']}")
    return [side for side in ("canonical", "other") if item[side]["x9_reference_accept"]]


def main():
    output = ROOT / "raw" / "x9_campaign" / "x9_summary.json"
    if output.exists():
        raise FileExistsError(output)
    plan = json.loads(PLAN.read_text())
    family_path = ROOT / "raw" / "family_campaign" / "family_summary.json"
    if (plan["candidate_sha256"] != digest(ROOT / "raw" / "candidates.jsonl") or
            plan["family_plan_sha256"] != digest(ROOT / "raw" / "family_campaign" / "plan.json") or
            plan["family_summary_sha256"] != digest(family_path) or
            plan["evaluator_sha256"] != digest(ROOT / "evaluate_x9_remaining.py") or
            plan["evaluator_controls_sha256"] != digest(ROOT / "raw" / "x9_evaluator_controls_v2.json")):
        fail("X9 plan input digest changed")
    family = json.loads(family_path.read_text())
    targets = {item["name"]: item for item in json.loads((ROOT / "targets.json").read_text())}
    seeds = collections.defaultdict(dict)
    for line in (ROOT / "raw" / "candidates.jsonl").open():
        item = json.loads(line)
        if item["kind"] == "prime":
            seeds[item["target"]][item["index"]] = item["seed"]
    by_rep = collections.defaultdict(dict)
    hashes = {}
    for shard in plan["shards"]:
        rep, start, end = shard["target"], shard["start"], shard["end"]
        path = ROOT / "raw" / "x9_evaluations" / rep / f"{start:05d}-{end:05d}.jsonl"
        if not path.exists():
            fail(f"missing X9 shard: {path}")
        with path.open() as source:
            header = json.loads(next(source))
            if (header["record"] != "run" or header["target"] != rep or
                    header["start"] != start or header["end"] != end or
                    header["candidate_sha256"] != plan["candidate_sha256"] or
                    header["family_plan_sha256"] != plan["family_plan_sha256"] or
                    header["family_summary_sha256"] != plan["family_summary_sha256"] or
                    header["script_sha256"] != plan["evaluator_sha256"]):
                fail(f"X9 shard header mismatch: {path}")
            observed = 0
            for line in source:
                row = json.loads(line)
                index = row["index"]
                if (row["target"] != rep or index != start + observed or
                        row["seed"] != seeds[rep][index] or
                        row.get("status") == "INDETERMINATE" or index in by_rep[rep]):
                    fail(f"X9 shard row mismatch: {path}:{index}")
                for mapping in ("unmasked", "strict_x9"):
                    accepted_roots(row, mapping)
                by_rep[rep][index] = row
                observed += 1
            if observed != end - start + 1:
                fail(f"X9 shard length mismatch: {path}")
        hashes[str(path.relative_to(ROOT))] = digest(path)
    named = {}
    for rep, names in REPRESENTATIVE.items():
        max_index = max(targets[name]["candidate_index"] for name in names)
        if set(by_rep[rep]) != set(range(1, max_index + 1)):
            fail(f"X9 representative stream incomplete: {rep}")
        for name in names:
            end = targets[name]["candidate_index"]
            prior_published = {targets[other]["candidate_index"]: other for other in names
                               if targets[other]["candidate_index"] < end}
            prior_end = max(prior_published, default=0)
            if any(by_rep[rep][i]["seed"] != seeds[name][i] for i in range(1, end + 1)):
                fail(f"X9 shared stream mismatch: {name}")
            if not by_rep[rep][end].get("anchor_order_matches") and name == rep:
                fail(f"X9 published anchor mismatch: {name}")
            record = {"representative_stream": rep, "published_index": end,
                      "earlier_indices": end - 1, "mappings": {}}
            for mapping in ("unmasked", "strict_x9"):
                survivors = []
                states = collections.Counter()
                branch_count = 0
                canonical_indices = []
                other_indices = []
                for index in range(1, end):
                    row = by_rep[rep][index]
                    item = effective(row, mapping)
                    states[item["status"]] += 1
                    roots = accepted_roots(row, mapping)
                    if not roots:
                        continue
                    branch_count += len(roots)
                    if "canonical" in roots:
                        canonical_indices.append(index)
                    if "other" in roots:
                        other_indices.append(index)
                    prior_name = prior_published.get(index)
                    identical_prior = (prior_name is not None and
                                       any(int(item[f"{side}_b"], 16) == int(targets[prior_name]["published_b"]) and
                                           int(item[side]["order"]) == int(targets[prior_name]["published_subgroup_order"])
                                           for side in roots))
                    survivors.append({"index": index, "seed": row["seed"],
                                      "c": item["c"], "roots": [
                        {"side": side, "b": item[f"{side}_b"],
                         "group_order": item[side]["order"],
                         "smooth_cofactor": item[side]["x9_255_smooth_cofactor"],
                         "prime_subgroup": item[side]["x9_remainder"]}
                        for side in roots],
                                      "same_seed_as_prior_published_curve": prior_name,
                                      "same_curve_as_prior_published": identical_prior})
                anchor = by_rep[rep][end]
                anchor_item = effective(anchor, mapping)
                anchor_match = (anchor_item["status"] in ("COUNTED", "REUSED_FAMILY_COUNT") and
                                int(targets[name]["published_b"]) in (
                                    int(anchor_item["canonical_b"], 16), int(anchor_item["other_b"], 16)))
                record["mappings"][mapping] = {
                    "published_coefficient_matches_mapping": bool(anchor_match),
                    "earlier_reference_eligible_seed_count": len(survivors),
                    "earlier_reference_eligible_root_count": branch_count,
                    "earlier_reference_eligible_canonical_indices": canonical_indices,
                    "earlier_reference_eligible_other_indices": other_indices,
                    "prior_published_anchor_indices": dict(sorted(prior_published.items())),
                    "earlier_unpublished_reference_eligible_seed_count": sum(
                        not item["same_curve_as_prior_published"] for item in survivors),
                    "earlier_unpublished_reference_eligible_indices": [
                        item["index"] for item in survivors if not item["same_curve_as_prior_published"]],
                    "since_previous_published_anchor_exclusive": prior_end,
                    "reference_eligible_between_previous_anchor_and_current": [
                        item["index"] for item in survivors if item["index"] > prior_end],
                    "first_eligible_index": survivors[0]["index"] if survivors else None,
                    "states": dict(sorted(states.items())),
                    "earlier_reference_eligible": survivors,
                }
            named[name] = record
    result = {"scope": "complete 255-smooth X9 reference on six unique prime streams and ten named targets",
              "plan_sha256": digest(PLAN), "candidate_sha256": plan["candidate_sha256"],
              "family_summary_sha256": plan["family_summary_sha256"],
              "x9_shard_sha256": hashes,
              "representative_candidate_count": sum(len(rows) for rows in by_rep.values()),
              "named_target_candidate_pairs": sum(item["published_index"] for item in named.values()),
              "named_targets": named,
              "limitations": ["The accessible X9 text is a September 1998 working draft, later than the 1997 runs.",
                              "Historical lmax, rmin, timestamp choice, coefficient root preference, and unpublished selection filters are unknown."]}
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"output": str(output), "sha256": digest(output),
                      "x9_by_target": {name: {mapping: item["earlier_reference_eligible_seed_count"]
                                              for mapping, item in target["mappings"].items()}
                                       for name, target in named.items()}}, sort_keys=True))


if __name__ == "__main__":
    main()
