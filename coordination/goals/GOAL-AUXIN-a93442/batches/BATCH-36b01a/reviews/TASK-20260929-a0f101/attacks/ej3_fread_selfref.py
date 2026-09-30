#!/usr/bin/env python3
"""EJ3 attack: independent F-READ R1-R4 order + self_reference_table closure.

Own phrase inventory first; do not start from control lists.
Negative control: delete one table row on a scratch copy; closure must fail.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from copy import deepcopy
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
WRITE = HERE.parent
BATCH = HERE.parents[2]
DRAFT = BATCH / "design" / "TASK-20260929-6d01d7" / "draft-contract.yaml"
REPO = HERE.parents[7]

EXPECTED_SHA = "b147966a5798bab10183ac56a9daa703ff41c54936f832fb8d0e28f2becd1589"

# Candidate self-referential deictic patterns (document-pointing "this/the X")
# Broader than R1 inventory on purpose — hunt unlisted.
CANDIDATE_PATTERNS = [
    r"\bthis draft\b",
    r"\bthis design\b",
    r"\bthis successor contract\b",
    r"\bthis successor\b",
    r"\bthis frozen contract\b",
    r"\bthe frozen contract\b",
    r"\bthis contract file\b",
    r"\bthis contract\b",
    r"\bTHIS contract\b",
    r"\bthis experiment\b",
    r"\bthis specification\b",
    r"\bthis protocol\b",
    r"\bthis amendment\b",
    r"\bthis file\b",
    r"\bthis text\b",
    r"\bthis fresh block\b",
    r"\bthis block\b",
    r"\bthis successor_contract block\b",
    r"\bEXP-AUXIN-369078\b",
    # Adjacent deictics that may or may not be self-referential to the contract
    r"\bthis design session\b",
    r"\bthis session\b",
    r"\bthis arm\b",
    r"\bthis package\b",
    r"\bthis run\b",
    r"\bthis list\b",
    r"\bthis field\b",
    r"\bthis clause\b",
]


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load_draft(path: Path):
    text = path.read_text(encoding="utf-8")
    data = yaml.safe_load(text)
    return text, data


def extract_fread(data):
    fresh = data["successor_contract"]["fresh"]
    fread = fresh["reading_of_references"]
    assert fread["id"] == "F-READ"
    order = fread["order"]
    rules = {r["id"]: r["text"] for r in fread["rules"]}
    return order, rules


def extract_table(data):
    table = data["successor_contract"]["self_reference_table"]
    rows = table["rows"]
    phrases = []
    for r in rows:
        phrases.append(
            {
                "phrase": r.get("phrase"),
                "rule_id": r.get("rule_id"),
                "closed": r.get("closed"),
                "text": r.get("text"),
            }
        )
    return table, phrases


def parse_r1_listed_phrases(r1_text: str) -> list[str]:
    # R1 text quotes phrases between double quotes, then "and \"EXP-...\""
    # Extract all "..." segments.
    return re.findall(r'"([^"]+)"', r1_text)


def inventory_occurrences(full_text: str) -> dict:
    # Exclude self_reference_table and F-READ R1 listing region from "body"
    # by scanning whole file; also report per-phrase counts.
    out = {}
    for pat in CANDIDATE_PATTERNS:
        hits = []
        for m in re.finditer(pat, full_text, flags=re.IGNORECASE if "THIS" not in pat else 0):
            # For THIS contract keep case-sensitive; for others use IGNORECASE via lower
            start = max(0, m.start() - 40)
            end = min(len(full_text), m.end() + 40)
            hits.append(
                {
                    "match": m.group(0),
                    "offset": m.start(),
                    "context": full_text[start:end].replace("\n", " "),
                }
            )
        # Re-run case-insensitive for ordinary this-phrases
        if "THIS" not in pat:
            hits = []
            for m in re.finditer(pat, full_text, flags=re.IGNORECASE):
                start = max(0, m.start() - 40)
                end = min(len(full_text), m.end() + 40)
                hits.append(
                    {
                        "match": m.group(0),
                        "offset": m.start(),
                        "context": full_text[start:end].replace("\n", " "),
                    }
                )
        out[pat] = {"count": len(hits), "samples": hits[:8]}
    return out


def phrases_in_body_outside_inventory(full_text: str, listed: set[str]) -> list:
    """Find candidate deictics whose surface form is not in R1/table listing.

    Classification:
    - document_selfref: points at this contract / file / experiment / draft / etc.
    - section_local: this list/field/clause/arm/block within the document
    - session_meta: this design session / this session (producer, not contract)
    - package_run: this package / this run (runtime instance)
    """
    findings = []
    # Surface forms we treat as document self-refs requiring listing
    require_list = {
        "this draft",
        "this design",
        "this successor",
        "this successor contract",
        "this frozen contract",
        "the frozen contract",
        "this contract",
        "this contract file",
        "this experiment",
        "this specification",
        "this protocol",
        "this amendment",
        "this file",
        "this text",
        "this fresh block",
        "this successor_contract block",
        "exp-auxin-369078",
    }
    # Normalize listed
    listed_norm = {p.lower() for p in listed}

    body_patterns = [
        (r"\bthis fresh block\b", "document_selfref"),
        (r"\bthis successor_contract block\b", "document_selfref"),
        (r"\bthis block\b", "section_local"),
        (r"\bthis design session\b", "session_meta"),
        (r"\bthis session\b", "session_meta"),
        (r"\bthis arm\b", "section_local"),
        (r"\bthis package\b", "package_run"),
        (r"\bthis run\b", "package_run"),
        (r"\bthis list\b", "section_local"),
        (r"\bthis field\b", "section_local"),
        (r"\bthis clause\b", "section_local"),
        (r"\bthis draft\b", "document_selfref"),
        (r"\bthis design\b", "document_selfref"),
        (r"\bthis successor contract\b", "document_selfref"),
        (r"\bthis successor\b", "document_selfref"),
        (r"\bthis frozen contract\b", "document_selfref"),
        (r"\bthe frozen contract\b", "document_selfref"),
        (r"\bthis contract file\b", "document_selfref"),
        (r"\bthis contract\b", "document_selfref"),
        (r"\bthis experiment\b", "document_selfref"),
        (r"\bthis specification\b", "document_selfref"),
        (r"\bthis protocol\b", "document_selfref"),
        (r"\bthis amendment\b", "document_selfref"),
        (r"\bthis file\b", "document_selfref"),
        (r"\bthis text\b", "document_selfref"),
        (r"\bEXP-AUXIN-369078\b", "document_selfref"),
    ]
    seen_keys = set()
    for pat, klass in body_patterns:
        for m in re.finditer(pat, full_text, flags=re.IGNORECASE):
            surface = m.group(0)
            key = (surface.lower(), m.start())
            if key in seen_keys:
                continue
            seen_keys.add(key)
            listed_ok = surface.lower() in listed_norm
            # Longer phrases may be covered by shorter listed forms only if exact
            # "this design session" is NOT covered by "this design"
            if klass == "document_selfref" and not listed_ok:
                # Check if any listed phrase equals the surface
                findings.append(
                    {
                        "surface": surface,
                        "offset": m.start(),
                        "class": klass,
                        "in_r1_or_table": False,
                        "requires_list": surface.lower() in require_list
                        or surface.lower().startswith("this fresh"),
                        "context": full_text[max(0, m.start() - 50) : m.end() + 50].replace(
                            "\n", " "
                        ),
                    }
                )
            elif klass == "document_selfref" and listed_ok:
                pass  # listed — ok
            else:
                findings.append(
                    {
                        "surface": surface,
                        "offset": m.start(),
                        "class": klass,
                        "in_r1_or_table": listed_ok,
                        "requires_list": False,
                        "note": "not treated as R1-class document self-ref under this attack",
                        "context": full_text[max(0, m.start() - 50) : m.end() + 50].replace(
                            "\n", " "
                        ),
                    }
                )
    return findings


def check_order_semantics(order: str, rules: dict) -> dict:
    checks = {
        "order_states_first_applicable_and_stop": (
            "first applicable" in order.lower() and "stop" in order.lower()
        ),
        "order_states_R4_only_for_table_R4": (
            "R4 applies only to phrases listed in self_reference_table" in order
        ),
        "rules_present_R1_R2_R3_R4": set(rules) == {"R1", "R2", "R3", "R4"},
        "R1_lists_EXP_id": "EXP-AUXIN-369078" in rules.get("R1", ""),
        "R1_lists_this_draft": '"this draft"' in rules.get("R1", "")
        or "this draft" in rules.get("R1", ""),
    }
    return checks


def check_table_closure(table, phrases, r1_phrases) -> dict:
    table_phrases = [p["phrase"] for p in phrases if p["phrase"] != "_closure_"]
    closure_rows = [p for p in phrases if p["phrase"] == "_closure_"]
    r1_norm = {p.lower() for p in r1_phrases}
    table_norm = {p.lower() for p in table_phrases}

    missing_from_table = sorted(r1_norm - table_norm)
    extra_in_table = sorted(table_norm - r1_norm)
    # All non-closure rows should claim closed:true under R1 (or their rule)
    unclosed = [p for p in phrases if p["phrase"] != "_closure_" and not p.get("closed")]
    r4_only_closure = all(
        p["rule_id"] == "R1" for p in phrases if p["phrase"] != "_closure_"
    ) and all(p["rule_id"] == "R4" for p in closure_rows)

    return {
        "order_matches_F_READ": table.get("order_matches_F_READ"),
        "r1_phrase_count": len(r1_phrases),
        "table_phrase_count": len(table_phrases),
        "missing_r1_phrases_from_table": missing_from_table,
        "extra_table_phrases_not_in_r1": extra_in_table,
        "unclosed_rows": unclosed,
        "has_closure_row": len(closure_rows) == 1,
        "closure_text_mentions_this_draft": (
            "this draft" in (closure_rows[0].get("text") or "") if closure_rows else False
        ),
        "closure_text_mentions_exp_id": (
            "EXP-AUXIN-369078" in (closure_rows[0].get("text") or "") if closure_rows else False
        ),
        "non_closure_rows_are_R1": r4_only_closure,
        "table_closed_under_r1_equality": not missing_from_table and not extra_in_table,
    }


def negative_control_delete_row(data) -> dict:
    scratch = deepcopy(data)
    rows = scratch["successor_contract"]["self_reference_table"]["rows"]
    # Delete "this draft" row
    before = len(rows)
    scratch["successor_contract"]["self_reference_table"]["rows"] = [
        r for r in rows if r.get("phrase") != "this draft"
    ]
    after = len(scratch["successor_contract"]["self_reference_table"]["rows"])
    # Re-check closure: R1 still lists this draft; table missing it
    order, rules = extract_fread(scratch)
    r1_phrases = parse_r1_listed_phrases(rules["R1"])
    table, phrases = extract_table(scratch)
    closure = check_table_closure(table, phrases, r1_phrases)
    # Also: body still contains "this draft"
    # Serialize roughly via searching original requirement
    must_fail = (
        "this draft" in {p.lower() for p in r1_phrases}
        and "this draft" not in {
            p["phrase"].lower() for p in phrases if p.get("phrase") and p["phrase"] != "_closure_"
        }
    )
    return {
        "deleted_phrase": "this draft",
        "rows_before": before,
        "rows_after": after,
        "closure_after": closure,
        "negative_control_fails_as_required": must_fail
        and not closure["table_closed_under_r1_equality"],
    }


def main():
    assert DRAFT.is_file(), f"missing draft {DRAFT}"
    digest = sha256_file(DRAFT)
    if digest != EXPECTED_SHA:
        print(json.dumps({"abort": True, "reason": "draft sha256 mismatch", "got": digest}))
        sys.exit(2)

    text, data = load_draft(DRAFT)
    order, rules = extract_fread(data)
    r1_phrases = parse_r1_listed_phrases(rules["R1"])
    table, phrases = extract_table(data)
    order_checks = check_order_semantics(order, rules)
    closure = check_table_closure(table, phrases, r1_phrases)
    inv = inventory_occurrences(text)
    unlisted_scan = phrases_in_body_outside_inventory(text, set(r1_phrases) | {p["phrase"] for p in phrases if p.get("phrase")})
    unlisted_document_selfrefs = [
        f
        for f in unlisted_scan
        if f.get("class") == "document_selfref" and f.get("requires_list") and not f.get("in_r1_or_table")
    ]
    # Deduplicate by surface
    unlisted_surfaces = sorted({f["surface"].lower() for f in unlisted_document_selfrefs})

    neg = negative_control_delete_row(data)

    # Named break EJ3-UNLISTED-THIS-DRAFT: is "this draft" in R1 and table?
    this_draft_in_r1 = any(p.lower() == "this draft" for p in r1_phrases)
    this_draft_in_table = any(
        (p.get("phrase") or "").lower() == "this draft" for p in phrases
    )
    named_break_fixed = this_draft_in_r1 and this_draft_in_table and closure["has_closure_row"]

    # Joint verdict: breaks if unlisted document selfrefs remain OR order/closure fails
    order_ok = all(order_checks.values())
    closure_ok = (
        closure["table_closed_under_r1_equality"]
        and closure["has_closure_row"]
        and closure["closure_text_mentions_this_draft"]
        and closure["closure_text_mentions_exp_id"]
        and not closure["unclosed_rows"]
        and closure["order_matches_F_READ"] is True
    )
    breaks = (not order_ok) or (not closure_ok) or bool(unlisted_surfaces)
    # Note: "this fresh block" / "this successor_contract block" if found unlisted cause break

    result = {
        "attack": "EJ3_fread_selfref",
        "draft_path": str(DRAFT.relative_to(DRAFT.parents[5]) if False else DRAFT.as_posix()),
        "draft_sha256": digest,
        "order_checks": order_checks,
        "r1_phrases": r1_phrases,
        "table_phrases": [p["phrase"] for p in phrases],
        "closure": closure,
        "named_break_EJ3_UNLISTED_THIS_DRAFT": {
            "this_draft_in_r1": this_draft_in_r1,
            "this_draft_in_table": this_draft_in_table,
            "status": "fixed" if named_break_fixed else "not_fixed",
        },
        "unlisted_document_selfrefs_surfaces": unlisted_surfaces,
        "unlisted_document_selfrefs_samples": unlisted_document_selfrefs[:20],
        "adjacent_deictic_scan_note": "session_meta/section_local/package_run classified separately; not auto-break",
        "inventory_counts": {k: v["count"] for k, v in inv.items()},
        "negative_control": neg,
        "verdict": "breaks" if breaks else "holds",
        "break_reasons": [
            r
            for r, ok in [
                ("order_checks_failed", not order_ok),
                ("closure_failed", not closure_ok),
                ("unlisted_document_selfrefs", bool(unlisted_surfaces)),
            ]
            if ok
        ],
    }
    out = WRITE / "ej3_fread_selfref.result.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    print(json.dumps({"wrote": str(out), "verdict": result["verdict"], "named": result["named_break_EJ3_UNLISTED_THIS_DRAFT"]["status"], "unlisted": unlisted_surfaces}))


if __name__ == "__main__":
    main()
