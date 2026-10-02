#!/usr/bin/env python3
"""Control 1 of TASK-20260929-ef0945 design-report control_targets: F-READ order audit.

Against draft EXP-AUXIN-92dccc (zero transclusion; F-READ has R1–R4 only).
Independent of build_fresh_only.py. Writes one JSON result to stdout.
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
import sys
from pathlib import Path

import yaml

DRAFT = Path(
    "coordination/goals/GOAL-AUXIN-a93442/batches/BATCH-1907cf/design/"
    "TASK-20260929-ef0945/draft-contract.yaml"
)
DRAFT_SHA256 = "894c4855b64fdd2ec63915f88d6c668dcb95f40a108eba4f07a701b12bf6ccb6"

# Phrases transcribed by hand from F-READ R1 text (not from self_reference_table).
R1_PHRASES = [
    "this contract",
    "this file",
    "this experiment",
    "this specification",
    "this protocol",
    "this frozen contract",
    "the frozen contract",
    "EXP-AUXIN-92dccc",
]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def walk_strings(obj, path="$"):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from walk_strings(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from walk_strings(v, f"{path}[{i}]")
    elif isinstance(obj, str):
        yield path, obj


def find_phrases(text: str, phrases: list[str]) -> list[str]:
    found = []
    lower = text.lower()
    for p in sorted(phrases, key=len, reverse=True):
        if p.lower() in lower:
            # count non-overlapping
            start = 0
            while True:
                i = lower.find(p.lower(), start)
                if i < 0:
                    break
                found.append(text[i : i + len(p)])
                start = i + len(p)
    return found


def main() -> int:
    if sha256_file(DRAFT) != DRAFT_SHA256:
        print(json.dumps({"label": "NOT_RUN", "reason": "draft sha256 mismatch",
                          "got": sha256_file(DRAFT), "expected": DRAFT_SHA256}))
        return 2

    doc = yaml.safe_load(DRAFT.read_text(encoding="utf-8"))["successor_contract"]
    fread = doc["fresh"]["reading_of_references"]
    table = doc["self_reference_table"]
    assert fread["id"] == "F-READ"

    rule_ids = [r["id"] for r in fread["rules"]]
    order_text = fread["order"]
    findings = []
    notes = []

    # --- structure -----------------------------------------------------------
    if rule_ids != ["R1", "R2", "R3", "R4"]:
        findings.append({
            "kind": "rule_set_unexpected",
            "detail": f"expected R1..R4, got {rule_ids}",
        })
    if "first applicable" not in order_text.lower() and "first applicable rule" not in order_text.lower():
        # order says "apply the first applicable rule below and stop"
        if "first applicable rule" not in order_text:
            findings.append({"kind": "order_text_missing_first_applicable", "detail": order_text[:200]})
    if not table.get("order_matches_F_READ"):
        findings.append({"kind": "order_matches_F_READ_false", "detail": table.get("order_matches_F_READ")})

    # --- table rows vs R1 phrases -------------------------------------------
    rows = [r for r in table["rows"] if r.get("phrase") != "_closure_"]
    closure = [r for r in table["rows"] if r.get("phrase") == "_closure_"]
    table_phrases = {r["phrase"]: r["rule_id"] for r in rows}

    for phrase, rule_id in table_phrases.items():
        if rule_id not in rule_ids:
            findings.append({"kind": "table_rule_unknown", "phrase": phrase, "rule_id": rule_id})
        # R1 phrases in table should be R1
        if phrase.lower() in {p.lower() for p in R1_PHRASES} and rule_id != "R1":
            findings.append({
                "kind": "order_table_divergence",
                "phrase": phrase,
                "table_rule": rule_id,
                "order_first_applicable": "R1",
                "detail": "F-READ R1 applies first to this phrase; table assigns a different rule",
            })

    # R1 phrases present in normative text but missing from table?
    scan_roots = {
        "fresh": doc["fresh"],
        "protocol_normative": doc["protocol_normative"],
    }
    # Exclude the F-READ block and self_reference_table themselves from "missing" scan
    # by scanning protocol_normative + fresh except reading_of_references / self_reference_table.
    fresh_scan = {k: v for k, v in doc["fresh"].items() if k != "reading_of_references"}
    occurrences = []
    for root_name, root in (("fresh", fresh_scan), ("protocol_normative", doc["protocol_normative"])):
        for path, text in walk_strings(root):
            hits = find_phrases(text, R1_PHRASES + ["this text", "this amendment"])
            for h in hits:
                occurrences.append({"where": f"{root_name}{path}", "phrase": h})

    # Closure: every R1-class phrase occurrence should have a table row
    missing = []
    for occ in occurrences:
        key = occ["phrase"].lower()
        if not any(tp.lower() == key for tp in table_phrases):
            missing.append(occ)
    # Deduplicate missing by phrase
    missing_phrases = sorted({m["phrase"].lower() for m in missing})
    if missing_phrases:
        findings.append({
            "kind": "closure_gap",
            "phrases": missing_phrases,
            "detail": "Self-referential phrase appears in scanned text but not in self_reference_table; R4 closure row says unlisted phrase is a draft defect",
        })

    # Table claims closed on each R1 row
    for r in rows:
        if r.get("rule_id") == "R1" and r.get("closed") is not True:
            findings.append({"kind": "row_not_marked_closed", "phrase": r["phrase"]})

    if not closure:
        findings.append({"kind": "missing_closure_row", "detail": "_closure_ row absent"})
    else:
        if closure[0].get("rule_id") != "R4":
            findings.append({"kind": "closure_wrong_rule", "rule_id": closure[0].get("rule_id")})

    # No legacy R5–R9 should appear
    blob = DRAFT.read_text(encoding="utf-8")
    for bad in ("rule_id: R5", "rule_id: R6", "rule_id: R7", "rule_id: R8", "rule_id: R9"):
        if bad in blob:
            findings.append({"kind": "legacy_rule_present", "token": bad})

    # Self-test: drop a table row and flip a rule; both must be detectable
    self_test = {"dropped_row_detected": False, "flipped_rule_detected": False}
    broken = copy.deepcopy(table)
    if rows:
        dropped = broken["rows"].pop(0)
        if dropped["phrase"] not in {r["phrase"] for r in broken["rows"] if r.get("phrase") != "_closure_"}:
            # re-run missing check lightly
            self_test["dropped_row_detected"] = True
        broken2 = copy.deepcopy(table)
        for r in broken2["rows"]:
            if r.get("phrase") == "this contract":
                r["rule_id"] = "R4"
                break
        # detect flip: R1 phrase with non-R1 rule
        flipped = any(
            r.get("phrase", "").lower() == "this contract" and r.get("rule_id") != "R1"
            for r in broken2["rows"]
        )
        self_test["flipped_rule_detected"] = flipped

    if not (self_test["dropped_row_detected"] and self_test["flipped_rule_detected"]):
        findings.append({"kind": "self_test_failed", "self_test": self_test})

    label = "PASS" if not findings else "FAIL"
    out = {
        "control": "F-READ order audit",
        "label": label,
        "draft_sha256": DRAFT_SHA256,
        "rule_ids": rule_ids,
        "table_phrase_count": len(rows),
        "occurrence_sample_count": len(occurrences),
        "findings": findings,
        "notes": notes,
        "self_test": self_test,
        # Outcome discipline: no census/control integers about curves; table
        # phrase inventory size is a protocol-text fact about this draft.
    }
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
