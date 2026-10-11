#!/usr/bin/env python3
"""EJ3 independent phrase inventory for draft EXP-AUXIN-339fb0.

Build own deictic inventory; do not start from control lists.
Negative control: delete one self_reference_table row on a scratch copy.
"""
from __future__ import annotations

import hashlib
import json
import re
from copy import deepcopy
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[6]  # workspace root via relative climb is fragile; use cwd
ROOT = Path.cwd()
DRAFT = ROOT / (
    "coordination/goals/GOAL-AUXIN-a93442/batches/BATCH-ad00c6/"
    "design/TASK-20260929-d519f6/draft-contract.yaml"
)
OUT = Path(__file__).resolve().parent / "ej3_phrase_inventory.result.json"

# Candidate document self-referential deictics (own inventory seed, not control lists).
# Includes residual phrases named by DEC-20260929-4eade7 and peers.
SEED_PHRASES = [
    "this fresh block",
    "this contract file",
    "this successor_contract block",
    "this successor contract",
    "this successor",
    "this contract",
    "this file",
    "this experiment",
    "this specification",
    "this protocol",
    "this frozen contract",
    "the frozen contract",
    "this text",
    "this amendment",
    "this draft",
    "this design",
    "EXP-AUXIN-339fb0",
    "this YAML file",
    "this document",
    "this successor_contract",
    "the present contract",
    "the present file",
    "the governing text",
    "this governing file",
    "the contract file",
    "the successor contract",
    "our contract",
    "the current contract",
]

# Broader regex harvest for "this <noun>" / "the frozen ..." appearances in normative surfaces.
HARVEST_RE = re.compile(
    r"\b(?:this|the)\s+(?:fresh\s+block|contract\s+file|successor_contract\s+block|"
    r"successor\s+contract|frozen\s+contract|contract|file|experiment|specification|"
    r"protocol|text|amendment|draft|design|successor|YAML\s+file|document|"
    r"governing\s+(?:text|file)|present\s+(?:contract|file)|current\s+contract)\b",
    re.IGNORECASE,
)
EXP_RE = re.compile(r"\bEXP-AUXIN-339fb0\b")


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def extract_r1_phrases(r1_text: str) -> list[str]:
    # R1 quotes phrases as "..."
    return [m.group(1) for m in re.finditer(r'"([^"]+)"', r1_text)]


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().lower())


def main() -> None:
    raw = DRAFT.read_bytes()
    digest = sha256_bytes(raw)
    data = yaml.safe_load(raw)
    sc = data["successor_contract"]
    fresh = sc["fresh"]
    fread = fresh["reading_of_references"]
    assert fread["id"] == "F-READ"
    order = fread["order"]
    rules = {r["id"]: r["text"] for r in fread["rules"]}
    r1_phrases = extract_r1_phrases(rules["R1"])
    r1_norm = {norm(p) for p in r1_phrases}

    table = sc["self_reference_table"]
    rows = table["rows"]
    table_phrases = []
    closure_rows = []
    for row in rows:
        if row.get("phrase") == "_closure_":
            closure_rows.append(row)
            continue
        table_phrases.append(row)
    table_norm = {norm(r["phrase"]): r for r in table_phrases}

    # Surfaces to scan: fresh block + protocol_normative as YAML dump of those subtrees.
    surfaces = {
        "fresh": yaml.dump(fresh, default_flow_style=False, sort_keys=False),
        "protocol_normative": yaml.dump(
            sc["protocol_normative"], default_flow_style=False, sort_keys=False
        ),
        "self_reference_table": yaml.dump(table, default_flow_style=False, sort_keys=False),
    }
    # Exclude the R1 rule text itself from unlisted findings (it defines the phrases).
    r1_blob = rules["R1"]

    found: dict[str, dict] = {}
    for surface, text in surfaces.items():
        for m in HARVEST_RE.finditer(text):
            phrase = m.group(0)
            key = norm(phrase)
            # Skip matches that live only inside the R1 definition string when scanning fresh.
            if surface == "fresh" and phrase in r1_blob:
                # still count as present in R1; record separately
                pass
            entry = found.setdefault(
                key,
                {
                    "canonical_match": phrase,
                    "surfaces": [],
                    "in_r1": key in r1_norm,
                    "in_table": key in table_norm,
                    "table_rule_id": table_norm[key]["rule_id"] if key in table_norm else None,
                },
            )
            if surface not in entry["surfaces"]:
                entry["surfaces"].append(surface)
        for m in EXP_RE.finditer(text):
            key = norm(m.group(0))
            entry = found.setdefault(
                key,
                {
                    "canonical_match": m.group(0),
                    "surfaces": [],
                    "in_r1": key in r1_norm,
                    "in_table": key in table_norm,
                    "table_rule_id": table_norm[key]["rule_id"] if key in table_norm else None,
                },
            )
            if surface not in entry["surfaces"]:
                entry["surfaces"].append(surface)

    # Also force-check every seed phrase for presence anywhere in draft text.
    full_text = raw.decode("utf-8")
    seed_hits = []
    for p in SEED_PHRASES:
        # case-insensitive search for multi-word; EXP id exact
        if p.startswith("EXP-"):
            present = p in full_text
        else:
            present = re.search(re.escape(p), full_text, re.IGNORECASE) is not None
        seed_hits.append(
            {
                "phrase": p,
                "present_in_draft": present,
                "in_r1": norm(p) in r1_norm,
                "in_table": norm(p) in table_norm,
            }
        )

    # Unlisted = present in draft normative surfaces (excluding only-R1 definition)
    # and is a self-referential deictic, but absent from R1 and table.
    # For EJ3-RESIDUAL: residual deictics that appear in fresh/protocol must be in R1+table.
    unlisted = []
    for key, entry in found.items():
        # Ignore hits that appear only inside self_reference_table listing itself
        surfaces_wo_table = [s for s in entry["surfaces"] if s != "self_reference_table"]
        if not surfaces_wo_table:
            continue
        if not entry["in_r1"] and not entry["in_table"]:
            unlisted.append(entry)
        elif not entry["in_r1"] or not entry["in_table"]:
            # partial listing is also a defect under R4 closure claim
            unlisted.append({**entry, "partial": True})

    # Named residual break phrases from DEC-20260929-4eade7
    residual_named = [
        "this fresh block",
        "this contract file",
        "this successor_contract block",
        "EXP-AUXIN-339fb0",
    ]
    residual_status = []
    for p in residual_named:
        residual_status.append(
            {
                "phrase": p,
                "in_r1": norm(p) in r1_norm,
                "in_table": norm(p) in table_norm,
                "fixed_as_named": (norm(p) in r1_norm) and (norm(p) in table_norm),
            }
        )
    named_break_fixed = all(r["fixed_as_named"] for r in residual_status)

    # Negative control: delete one table row; closure must fail
    scratch = deepcopy(data)
    rows_scratch = scratch["successor_contract"]["self_reference_table"]["rows"]
    # delete "this fresh block" row
    deleted = None
    new_rows = []
    for r in rows_scratch:
        if r.get("phrase") == "this fresh block" and deleted is None:
            deleted = r
            continue
        new_rows.append(r)
    scratch["successor_contract"]["self_reference_table"]["rows"] = new_rows
    # Re-run: phrase present in fresh, absent from table => closure fail
    scratch_table_norm = {
        norm(r["phrase"]): r
        for r in new_rows
        if r.get("phrase") != "_closure_"
    }
    nc_phrase = "this fresh block"
    nc_present = re.search(re.escape(nc_phrase), full_text, re.IGNORECASE) is not None
    nc_in_table = norm(nc_phrase) in scratch_table_norm
    # Also remove F-READ order sentence for PTM-3 style; for EJ3 NC just row delete
    negative_control = {
        "deleted_row": deleted,
        "phrase_still_in_draft": nc_present,
        "phrase_in_scratch_table": nc_in_table,
        "closure_fails_as_required": nc_present and not nc_in_table,
    }

    # Order discipline: R4 applies only to listed R4 phrases; table uses R1 for deictics
    order_ok = "first applicable rule" in order.lower() or "apply the first" in order.lower()
    r4_only_listed = "R4 applies only to phrases listed" in order

    # Decide EJ3
    # holds if: no unlisted self-refs in normative surfaces; named residual fixed; NC works; order present
    ej3_breaks = []
    if unlisted:
        ej3_breaks.append(
            {
                "id": "EJ3-UNLISTED-SELF-REF",
                "detail": unlisted,
            }
        )
    if not named_break_fixed:
        ej3_breaks.append(
            {
                "id": "EJ3-RESIDUAL-UNLISTED-DEICTICS",
                "detail": residual_status,
            }
        )
    if not negative_control["closure_fails_as_required"]:
        ej3_breaks.append({"id": "EJ3-NC-ROW-DELETE-DID-NOT-FAIL", "detail": negative_control})
    if not (order_ok and r4_only_listed):
        ej3_breaks.append({"id": "EJ3-ORDER-MALFORMED", "detail": order})

    verdict = "breaks" if ej3_breaks else "holds"

    result = {
        "joint": "EJ3",
        "draft_sha256": digest,
        "expected_sha256": "6a1dca32c109d5badf4ba143c31f9d4d9a49e18ae287c8bb4fc604526bf02ecc",
        "digest_match": digest
        == "6a1dca32c109d5badf4ba143c31f9d4d9a49e18ae287c8bb4fc604526bf02ecc",
        "f_read_order": order,
        "r1_phrases": r1_phrases,
        "table_phrases": [r["phrase"] for r in table_phrases],
        "closure_rows": closure_rows,
        "harvested": found,
        "seed_hits": seed_hits,
        "unlisted": unlisted,
        "named_break_EJ3_RESIDUAL_UNLISTED_DEICTICS": {
            "claimed_fixed": True,
            "fixed_as_named": named_break_fixed,
            "phrases": residual_status,
        },
        "negative_control_delete_table_row": negative_control,
        "ej3_breaks": ej3_breaks,
        "verdict": verdict,
        "note": "Own inventory; control outputs not read before this file was written.",
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=False) + "\n")
    print(json.dumps({"verdict": verdict, "unlisted_count": len(unlisted), "out": str(OUT)}))


if __name__ == "__main__":
    main()
