#!/usr/bin/env python3
"""EJ8 reserved-topic / F-PREC / Q0-11 attack on draft EXP-AUXIN-339fb0."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import yaml

ROOT = Path.cwd()
DRAFT = ROOT / (
    "coordination/goals/GOAL-AUXIN-a93442/batches/BATCH-ad00c6/"
    "design/TASK-20260929-d519f6/draft-contract.yaml"
)
OUT = Path(__file__).resolve().parent / "ej8_reserved_topic.result.json"


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> None:
    raw = DRAFT.read_bytes()
    digest = sha256_file(DRAFT)
    data = yaml.safe_load(raw)
    sc = data["successor_contract"]
    fresh = sc["fresh"]
    pn = sc["protocol_normative"]
    full = raw.decode("utf-8")

    # --- Q0-11 ---
    conventions = pn.get("conventions") or {}
    q011_key_present = "Q0-11" in conventions
    q011_status = conventions.get("Q0-11_status")
    q011_status_absent = isinstance(q011_status, str) and q011_status.strip().upper().startswith(
        "ABSENT"
    )
    # Live DO-NOT-TAKE under Q0-11 key
    live_do_not_take = []
    if q011_key_present:
        live_do_not_take.append({"where": "conventions.Q0-11", "value": conventions["Q0-11"]})
    # Any YAML key literally Q0-11: (not Q0-11_status)
    for m in re.finditer(r"(?m)^(\s*)Q0-11:\s*(.*)$", full):
        live_do_not_take.append({"where": f"line_match:{m.group(0)[:80]}", "value": m.group(2)})
    # Residual DO-NOT-TAKE phrasing tied to Q0-11
    for m in re.finditer(r"Q0-11[^\n]{0,120}DO-NOT-TAKE|DO-NOT-TAKE[^\n]{0,120}Q0-11", full):
        # status sentences that say no DO-NOT-TAKE remains are neutralizing
        snippet = m.group(0)
        if re.search(r"no Q0-11 DO-NOT-TAKE|DO-NOT-TAKE rule remains", snippet, re.I):
            continue
        live_do_not_take.append({"where": "regex", "value": snippet})

    ej8_q011 = {
        "id": "EJ8-Q0-11-NOT-NEUTRALIZED",
        "Q0-11_key_present": q011_key_present,
        "Q0-11_status": q011_status,
        "Q0-11_status_ABSENT": q011_status_absent,
        "live_do_not_take_hits": live_do_not_take,
        "fresh_F_Q011": fresh.get("q0_11_status"),
        "fixed_as_named": (not q011_key_present)
        and q011_status_absent
        and len(live_do_not_take) == 0,
    }

    # --- EJ8-INCORP-HASH-VS-FPREC ---
    # Affirmative incorporates.sha256 / content-digest as run-time binding for held AMD
    incorp_hits = []
    for m in re.finditer(
        r".{0,60}incorporates(?:_by_hash)?\.sha256.{0,80}|content-digest of a held|.{0,60}bound by content-digest.{0,80}",
        full,
        re.IGNORECASE,
    ):
        snip = m.group(0)
        neg = bool(
            re.search(
                r"\b(?:no |not |never |forbid|deleted|not carried|not a run-time)\b",
                snip,
                re.I,
            )
        )
        incorp_hits.append({"snippet": snip, "neutralizing": neg, "affirmative": not neg})

    f_prec = fresh["precedence"]
    f_prec_forbids = (
        "No AMD-edit rule" in f_prec["text"]
        and "incorporates.sha256" in f_prec["text"]
        and "not a run-time rule" in f_prec["text"].lower()
    )

    ej8_incorp = {
        "id": "EJ8-INCORP-HASH-VS-FPREC",
        "f_prec_forbids_held_hash_runtime": f_prec_forbids,
        "f_prec_text": f_prec["text"],
        "incorp_mentions": incorp_hits,
        "affirmative_incorp_runtime_bindings": [h for h in incorp_hits if h["affirmative"]],
        "fixed_as_named": f_prec_forbids
        and all(h["neutralizing"] for h in incorp_hits if "incorporates" in h["snippet"].lower()),
    }

    # --- Reserved-topic surfaces vs fresh fields ---
    reserved = f_prec.get("reserved_topics", "")
    reserved_topics = [
        ("revision", "F-REV", fresh["revision_rule"]),
        ("approval", "F-APPROVAL", fresh["approval"]),
        ("custody", "F-CUSTODY", fresh["custody"]),
        ("write scope", "F-WRITE", fresh["write_scope"]),
        ("reference reading", "F-READ", fresh["reading_of_references"]),
        ("blind-report attestation", "F-ATT", fresh["review_attestation_requirement"]),
        (
            "execution admission",
            "protocol_normative.execution_admission",
            pn.get("execution_admission"),
        ),
    ]
    reserved_audit = []
    for label, fresh_id, fresh_obj in reserved_topics:
        reserved_audit.append(
            {
                "topic": label,
                "fresh_field_id": fresh_id,
                "named_in_f_prec_reserved_topics": label.split()[0].lower() in reserved.lower()
                or fresh_id in reserved
                or label in reserved.lower(),
                "fresh_field_present": fresh_obj is not None,
                "path": f"successor_contract.fresh / protocol_normative as applicable ({fresh_id})",
            }
        )

    # D4 cites F-REV only as revision route
    d4 = pn.get("change", {}).get("D4_calibration") or pn.get("D4_calibration")
    # structure may nest under change
    if d4 is None:
        change = pn.get("change") or {}
        d4 = change.get("D4_calibration")
    d4_text_blob = yaml.dump(d4, default_flow_style=False) if d4 else ""
    d4_cites_frev = "F-REV" in d4_text_blob and "only revision" in d4_text_blob.lower() or (
        "F-REV is the only revision route" in d4_text_blob
    )
    # Also check what_the_null_arm_is_for specifically
    null_arm_clause = ""
    if isinstance(d4, dict):
        null_arm_clause = str(d4.get("what_the_null_arm_is_for") or "")
    d4_ok = "F-REV is the only revision route" in null_arm_clause or (
        "F-REV" in null_arm_clause and "only revision" in null_arm_clause.lower()
    )

    # Protocol_normative must not state a conflicting revision route
    conflicting_revision = []
    for m in re.finditer(
        r"(?i)(?:amendment (?:file )?may revise|may revise any rule|layers? this contract|"
        r"rewritten in place)",
        full,
    ):
        snip = m.group(0)
        # allowed when negated by F-REV text
        ctx_start = max(0, m.start() - 80)
        ctx = full[ctx_start : m.end() + 80]
        if re.search(r"(?i)never|no (?:later )?amendment|not rewritten|no amendment layers", ctx):
            continue
        conflicting_revision.append(ctx)

    breaks = []
    if not ej8_q011["fixed_as_named"]:
        breaks.append({"id": "EJ8-Q0-11-NOT-NEUTRALIZED", "detail": ej8_q011})
    if not ej8_incorp["fixed_as_named"]:
        breaks.append({"id": "EJ8-INCORP-HASH-VS-FPREC", "detail": ej8_incorp})
    if not d4_ok:
        breaks.append(
            {
                "id": "EJ8-D4-NOT-FREV-ONLY",
                "null_arm_clause": null_arm_clause,
                "d4_cites_frev": d4_cites_frev,
            }
        )
    if conflicting_revision:
        breaks.append({"id": "EJ8-CONFLICTING-REVISION-ROUTE", "hits": conflicting_revision})

    # Fresh vs protocol_normative reserved-topic divergence: Q0-11 handled;
    # custody defined_terms decide custody scope
    custody_scope = fresh["custody"].get("scope")
    defined_terms = fresh["custody"].get("defined_terms")

    verdict = "breaks" if breaks else "holds"
    result = {
        "joint": "EJ8",
        "draft_sha256": digest,
        "named_breaks": {
            "EJ8-Q0-11-NOT-NEUTRALIZED": ej8_q011,
            "EJ8-INCORP-HASH-VS-FPREC": ej8_incorp,
        },
        "reserved_topics_text": reserved,
        "reserved_topic_audit": reserved_audit,
        "d4_null_arm_clause": null_arm_clause,
        "d4_cites_F_REV_only": d4_ok,
        "custody_scope": custody_scope,
        "custody_defined_terms_keys": list(defined_terms.keys()) if defined_terms else None,
        "breaks": breaks,
        "verdict": verdict,
        "note": "Own EJ8 check; control outputs not read before this file was written.",
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=False) + "\n")
    print(json.dumps({"verdict": verdict, "out": str(OUT), "q011_fixed": ej8_q011["fixed_as_named"]}))


if __name__ == "__main__":
    main()
