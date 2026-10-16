#!/usr/bin/env python3
"""Validate every frozen shard and project shared streams to named curves."""

import collections
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PLAN = ROOT / "raw" / "family_campaign" / "plan.json"
RETRY_PLAN = ROOT / "raw" / "family_campaign" / "retry_plan.json"
REPRESENTATIVE = {
    "prime192v2": ("P-192", "prime192v3", "prime192v2"),
    "prime239v3": ("prime239v1", "prime239v2", "prime239v3"),
    "P-224": ("P-224",),
    "P-256": ("P-256",),
    "P-384": ("P-384",),
    "P-521": ("P-521",),
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fail(reason):
    raise ArithmeticError(reason)


def main():
    output = ROOT / "raw" / "family_campaign" / "family_summary.json"
    if output.exists():
        raise FileExistsError(output)
    plan = json.loads(PLAN.read_text())
    libc_path = ROOT / "raw" / "libc_replay.json"
    libc = json.loads(libc_path.read_text())
    if not libc["all_matched"] or libc["candidate_sha256"] != plan["candidate_sha256"]:
        fail("independent libc seed replay incomplete")
    if (plan["candidate_sha256"] != digest(ROOT / "raw" / "candidates.jsonl") or
            plan["torsion_screen_sha256"] != digest(ROOT / "raw" / "prime_3torsion_screen.jsonl") or
            plan["evaluator_sha256"] != digest(ROOT / "evaluate_family_fast.py") or
            plan["fast_controls_sha256"] != digest(ROOT / "raw" / "fast_evaluator_controls.json")):
        fail("frozen plan input digest changed")
    targets = {item["name"]: item for item in json.loads((ROOT / "targets.json").read_text())}
    seeds = collections.defaultdict(dict)
    for line in (ROOT / "raw" / "candidates.jsonl").open():
        item = json.loads(line)
        if item["kind"] == "prime":
            seeds[item["target"]][item["index"]] = item["seed"]
    by_rep = collections.defaultdict(dict)
    shard_hashes = {}
    segment_manifest = {}
    retry_plan = json.loads(RETRY_PLAN.read_text()) if RETRY_PLAN.exists() else None
    if retry_plan:
        if (retry_plan["original_plan_sha256"] != digest(PLAN) or
                any(retry_plan[key] != plan[key] for key in
                    ("candidate_sha256", "torsion_screen_sha256", "evaluator_sha256",
                     "fast_controls_sha256"))):
            fail("retry plan does not bind original plan")
        segments = [
            {"path": source["path"], "target": source["target"],
             "start": source["start"], "end": source["end"],
             "header_end": source["original_end"], "frozen_sha256": source["sha256"]}
            for source in retry_plan["source_segments"]
        ] + [
            {"path": str((ROOT / "raw" / "family_evaluations" / shard["target"] /
                          f"{shard['start']:05d}-{shard['end']:05d}.jsonl").relative_to(ROOT)),
             "target": shard["target"], "start": shard["start"], "end": shard["end"],
             "header_end": shard["end"]} for shard in retry_plan["retry_shards"]
        ]
    else:
        segments = [
            {"path": str((ROOT / "raw" / "family_evaluations" / shard["target"] /
                          f"{shard['start']:05d}-{shard['end']:05d}.jsonl").relative_to(ROOT)),
             "target": shard["target"], "start": shard["start"], "end": shard["end"],
             "header_end": shard["end"]} for shard in plan["shards"]
        ]
    for segment in segments:
        rep, start, end = segment["target"], segment["start"], segment["end"]
        path = ROOT / segment["path"]
        if not path.exists():
            fail(f"missing segment: {path}")
        path_hash = digest(path)
        if segment.get("frozen_sha256") and segment["frozen_sha256"] != path_hash:
            fail(f"retained segment changed: {path}")
        with path.open() as source:
            header = json.loads(next(source))
            if (header["record"] != "run" or header["target"] != rep or
                    header["start"] != start or header["end"] != segment["header_end"] or
                    header["candidate_sha256"] != plan["candidate_sha256"] or
                    header["torsion_sha256"] != plan["torsion_screen_sha256"] or
                    header["script_sha256"] != plan["evaluator_sha256"]):
                fail(f"segment header mismatch: {path}")
            observed = 0
            for line in source:
                row = json.loads(line)
                index = row["index"]
                if (row["target"] != rep or index != start + observed or
                        row["seed"] != seeds[rep][index] or
                        row["status"] == "INDETERMINATE" or index in by_rep[rep]):
                    fail(f"shard row mismatch or incomplete: {path}:{index}")
                if row["status"] == "COUNTED":
                    if any(root not in row for root in ("canonical", "other")):
                        fail(f"missing point-count branch: {path}:{index}")
                    for root in ("canonical", "other"):
                        if row[f"family_accept_{root}"] != row[root]["family_accept"]:
                            fail(f"branch acceptance mismatch: {path}:{index}")
                elif row["family_accept_canonical"] or row["family_accept_other"]:
                    fail(f"rejected row accepted: {path}:{index}")
                by_rep[rep][index] = row
                observed += 1
            if observed != end - start + 1:
                fail(f"segment length mismatch: {path}")
        key = str(path.relative_to(ROOT))
        shard_hashes[key] = path_hash
        segment_manifest[key] = {"target": rep, "start": start, "end": end,
                                 "header_end": segment["header_end"]}
    named = {}
    for rep, names in REPRESENTATIVE.items():
        max_index = max(targets[name]["candidate_index"] for name in names)
        if set(by_rep[rep]) != set(range(1, max_index + 1)):
            fail(f"representative stream incomplete: {rep}")
        for name in names:
            target = targets[name]
            end = target["candidate_index"]
            prior_published = {targets[other]["candidate_index"]: other for other in names
                               if targets[other]["candidate_index"] < end}
            prior_end = max(prior_published, default=0)
            if any(by_rep[rep][i]["seed"] != seeds[name][i] for i in range(1, end + 1)):
                fail(f"shared stream mismatch: {name}")
            anchor = by_rep[rep][end]
            if anchor["status"] != "COUNTED" or not anchor.get("anchor_matches", False) and name == rep:
                fail(f"published anchor rejected: {name}")
            published_b = int(target["published_b"])
            root = "canonical" if published_b == int(anchor["canonical_b"], 16) else "other"
            if published_b != int(anchor[f"{root}_b"], 16):
                fail(f"published coefficient root missing: {name}")
            if (int(anchor[root]["order"]) != int(target["published_subgroup_order"]) or
                    not anchor[root]["family_accept"]):
                fail(f"published order or acceptance mismatch: {name}")
            states = collections.Counter()
            accepted = []
            accepted_branches = 0
            canonical_indices = []
            other_indices = []
            for index in range(1, end):
                row = by_rep[rep][index]
                states[row["status"]] += 1
                roots = [side for side in ("canonical", "other") if row[f"family_accept_{side}"]]
                if roots:
                    accepted_branches += len(roots)
                    if "canonical" in roots:
                        canonical_indices.append(index)
                    if "other" in roots:
                        other_indices.append(index)
                    accepted.append({
                        "index": index, "seed": row["seed"], "roots": [
                            {"side": side, "b": row[f"{side}_b"],
                             "prime_order": row[side]["order"]} for side in roots],
                        "strict_x9_seed_mapping_matches": row["strict_x9_same_c"],
                        "same_seed_as_prior_published_curve": prior_published.get(index),
                        "counted_shard": next(key for key, segment in segment_manifest.items()
                                              if segment["target"] == rep and
                                              segment["start"] <= index <= segment["end"]),
                    })
            named[name] = {
                "representative_stream": rep,
                "published_index": end,
                "earlier_indices": end - 1,
                "rejection_and_count_states": dict(sorted(states.items())),
                "earlier_family_eligible_seed_count": len(accepted),
                "earlier_family_eligible_root_count": accepted_branches,
                "earlier_family_eligible_canonical_indices": canonical_indices,
                "earlier_family_eligible_other_indices": other_indices,
                "prior_published_anchor_indices": dict(sorted(prior_published.items())),
                "earlier_unpublished_family_eligible_seed_count": sum(
                    item["same_seed_as_prior_published_curve"] is None for item in accepted),
                "earlier_unpublished_family_eligible_indices": [
                    item["index"] for item in accepted if item["same_seed_as_prior_published_curve"] is None],
                "since_previous_published_anchor_exclusive": prior_end,
                "family_eligible_between_previous_anchor_and_current": [
                    item["index"] for item in accepted if item["index"] > prior_end],
                "first_eligible_index": accepted[0]["index"] if accepted else None,
                "earlier_family_eligible": accepted,
                "published_anchor_root": root,
                "published_anchor_order_matches": True,
            }
    result = {
        "scope": "complete published cofactor-one family profile on all ten named prime targets",
        "plan_sha256": digest(PLAN),
        "retry_plan_sha256": digest(RETRY_PLAN) if retry_plan else None,
        "candidate_sha256": plan["candidate_sha256"],
        "libc_replay_sha256": digest(libc_path),
        "shard_sha256": shard_hashes,
        "segment_manifest": segment_manifest,
        "representative_candidate_count": sum(len(rows) for rows in by_rep.values()),
        "named_target_candidate_pairs": sum(item["published_index"] for item in named.values()),
        "named_targets": named,
        "limitation": "X9 near-prime status on torsion-rejected prime candidates is unassessed; unknown historical lmax, rmin, root choice, and private selection criteria remain open.",
    }
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"output": str(output), "sha256": digest(output),
                      "candidate_count": result["representative_candidate_count"],
                      "earlier_family_eligible_by_target": {name: item["earlier_family_eligible_seed_count"]
                                                            for name, item in named.items()}}, sort_keys=True))


if __name__ == "__main__":
    main()
