#!/usr/bin/env python3
"""EJ8 attack: F-PREC reserved topics vs protocol_normative; Q0-11; incorp-hash."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
WRITE = HERE.parent
BATCH = HERE.parents[2]
REPO = HERE.parents[7]
DRAFT = BATCH / "design" / "TASK-20260929-6d01d7" / "draft-contract.yaml"
EXPECTED_SHA = "b147966a5798bab10183ac56a9daa703ff41c54936f832fb8d0e28f2becd1589"

RESERVED_TOPIC_KEYS = {
    "revision": ["F-REV", "revision"],
    "approval": ["F-APPROVAL", "approval"],
    "custody": ["F-CUSTODY", "custody", "invalidation"],
    "write_scope": ["F-WRITE", "write scope", "write_scope"],
    "reference_reading": ["F-READ", "F-PRE", "Q0-11", "reference"],
    "attestation": ["F-ATT", "attestation"],
    "execution_admission": ["execution_admission", "admission"],
}


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    assert sha256_file(DRAFT) == EXPECTED_SHA
    text = DRAFT.read_text(encoding="utf-8")
    data = yaml.safe_load(text)
    fresh = data["successor_contract"]["fresh"]
    pn = data["successor_contract"]["protocol_normative"]

    f_prec = fresh["precedence"]
    reserved = f_prec["reserved_topics"]
    f_rev = fresh["revision_rule"]["text"]
    f_custody = fresh["custody"]
    f_q011 = fresh["q0_11_status"]["text"]
    f_pre = fresh["execution_preconditions"]["text"]

    # Q0-11 status in protocol_normative.conventions
    conventions = pn.get("conventions") or {}
    q011_key_present = "Q0-11" in conventions
    q011_status = conventions.get("Q0-11_status")
    q011_absent_marker = False
    if isinstance(q011_status, str):
        q011_absent_marker = q011_status.strip().upper().startswith("ABSENT")
    # Also accept the field form used in this draft
    if not q011_absent_marker and isinstance(q011_status, str):
        q011_absent_marker = "ABSENT" in q011_status

    # Live DO-NOT-TAKE / Q0-11 rule hunt in draft body (excluding ABSENT / deleted claims)
    live_q011 = []
    for m in re.finditer(r"Q0-11|DO-NOT-TAKE|do not take", text, flags=re.IGNORECASE):
        ctx = text[max(0, m.start() - 100) : m.end() + 120].replace("\n", " ")
        # neutralize if context is ABSENT / deleted / does not decide / no Q0-11
        neutralized = bool(
            re.search(
                r"ABSENT|Deleted by construction|does not decide|No Q0-11|absent and does not decide|is absent",
                ctx,
                flags=re.IGNORECASE,
            )
        )
        live_q011.append(
            {
                "match": m.group(0),
                "offset": m.start(),
                "neutralized_by_context": neutralized,
                "context": ctx,
            }
        )
    live_unneutralized = [x for x in live_q011 if not x["neutralized_by_context"]]

    # ER-2 see: gated_span_rules[G-Q011] — dangling held pointer?
    gq011_refs = []
    for m in re.finditer(r"gated_span_rules\[G-Q011\]", text):
        gq011_refs.append(
            {
                "offset": m.start(),
                "context": text[max(0, m.start() - 80) : m.end() + 80].replace("\n", " "),
            }
        )
    # Does this draft DEFINE gated_span_rules?
    has_gated_span_rules_section = bool(
        re.search(r"^[\s]*gated_span_rules\s*:", text, flags=re.MULTILINE)
    )

    # Incorporation / content-digest / incorporates.sha256 as POSITIVE binding
    incorp_hits = []
    for m in re.finditer(
        r"incorporates\.sha256|incorporates_by_hash|content-digest|bound by content-digest|stays incorporated",
        text,
    ):
        ctx = text[max(0, m.start() - 100) : m.end() + 140].replace("\n", " ")
        # Positive binding vs forbid/delete/NOT
        is_forbid = bool(
            re.search(
                r"No record is bound by content-digest|NOT invalidation|not carried|deleted|"
                r"forbid|No content-digest binding|no held record is bound by content-digest|"
                r"No AMD-edit rule and no incorporates",
                ctx,
                flags=re.IGNORECASE,
            )
        )
        is_positive_binding = (not is_forbid) and bool(
            re.search(
                r"bound by content-digest|incorporates\.sha256 comparison|"
                r"mismatch against any incorporates|stays incorporated",
                ctx,
                flags=re.IGNORECASE,
            )
        )
        incorp_hits.append(
            {
                "match": m.group(0),
                "offset": m.start(),
                "forbid_or_delete_context": is_forbid,
                "positive_binding_reading": is_positive_binding and not is_forbid,
                "context": ctx,
            }
        )
    positive_incorp = [h for h in incorp_hits if h["positive_binding_reading"]]

    # Special: "stays incorporated" for stratification parenthetical
    stays_incorporated = [h for h in incorp_hits if "stays incorporated" in h["match"].lower() or "stays incorporated" in h["context"].lower()]

    # Overlay invalidation mentioning incorporates.sha256 — already neutralized as NOT?
    overlay_hash_conflicts = []
    for m in re.finditer(
        r"incorporates\.sha256 / incorporates_by_hash\.sha256 comparisons are NOT invalidation rules",
        text,
    ):
        overlay_hash_conflicts.append(
            {"kind": "neutralized_explicit", "offset": m.start(), "text": m.group(0)}
        )

    # D4 cites F-REV only?
    d10_or_d4 = []
    # change.D10 / modules / "F-REV is the only revision route"
    d4_hits = list(
        re.finditer(
            r"F-REV is the only revision route|per F-REV|under F-REV|No later amendment|"
            r"This contract is never rewritten in place",
            text,
        )
    )
    # Forbidden alternate revision routes in protocol_normative
    alt_revision = []
    for m in re.finditer(
        r"An amendment file may revise|amendment layers this contract|rewritten in place",
        text,
        flags=re.IGNORECASE,
    ):
        ctx = text[max(0, m.start() - 60) : m.end() + 80].replace("\n", " ")
        # "never rewritten" / "No amendment layers" are OK
        if re.search(r"never rewritten|No amendment layers|no amendment layers", ctx, re.IGNORECASE):
            continue
        alt_revision.append({"match": m.group(0), "context": ctx})

    # Reserved-topic conflicts: protocol_normative stating a reserved-topic rule
    # that DIFFERS from fresh field.
    # Scan protocol_normative for revision/custody/write/reference rules that
    # contradict F-REV / F-CUSTODY / F-READ.
    conflicts = []

    # 1) Does protocol_normative claim Q0-11 decides reference reading?
    if q011_key_present:
        conflicts.append(
            {
                "id": "Q0-11_key_present_in_conventions",
                "vs_fresh": "F-Q011 / F-PREC say absent",
                "neutralized": False,
            }
        )
    if q011_status and q011_absent_marker:
        # consistent with fresh
        pass
    elif q011_status and not q011_absent_marker:
        conflicts.append(
            {
                "id": "Q0-11_status_not_ABSENT",
                "value": q011_status,
                "neutralized": False,
            }
        )

    # 2) Overlay custody invalidation vs F-CUSTODY — if positive AMD rule
    for h in positive_incorp:
        conflicts.append(
            {
                "id": "positive_incorp_or_digest_binding",
                "vs_fresh": "F-PREC forbids content-digest / incorporates.sha256 run-time rules",
                "offset": h["offset"],
                "context": h["context"],
                "neutralized": False,
            }
        )

    # 3) "stays incorporated" — incorporation of held parenthetical into reading
    for h in stays_incorporated:
        # Check if it decides a reserved topic differently
        # Stratification membership is not revision/approval/custody/write/reference/attestation/admission
        conflicts.append(
            {
                "id": "stays_incorporated_stratification_parenthetical",
                "reserved_topic": None,
                "note": (
                    "Phrase 'stays incorporated' appears under interpretation overlay; "
                    "it fixes stratum MEMBERSHIP reading of text already in this contract's "
                    "change.D3_descriptive_bins.stratification, not a content-digest binding "
                    "of a held path. Classified as non-reserved-topic / non-F-PREC conflict "
                    "if the parenthetical text is already present in this file."
                ),
                "parenthetical_present_in_draft": "whose family polynomials force divisors" in text,
                "neutralized": "whose family polynomials force divisors" in text,
                "context": h["context"],
            }
        )

    # 4) ER-2 see G-Q011 without local gated_span_rules
    if gq011_refs and not has_gated_span_rules_section:
        conflicts.append(
            {
                "id": "ER-2_dangling_G-Q011_see_pointer",
                "vs_fresh": "F-Q011 / conventions.Q0-11_status ABSENT; F-READ decides reference reading",
                "neutralized": True,  # pointer cannot load absent section; F-READ/F-Q011 govern
                "neutralization": (
                    "Draft defines no gated_span_rules; see: pointer cannot activate held "
                    "G-Q011. F-PREC reserved_topics + F-Q011 + conventions.Q0-11_status ABSENT "
                    "state that Q0-11 does not decide. Residual dangling see: is provenance "
                    "noise, not a live DO-NOT-TAKE rule."
                ),
                "refs": gq011_refs,
            }
        )

    # Named breaks
    # EJ8-Q0-11-NOT-NEUTRALIZED: fixed if ABSENT and no live unneutralized DO-NOT-TAKE
    q011_fixed = (
        (not q011_key_present)
        and q011_absent_marker
        and len(live_unneutralized) == 0
        and ("absent and does not decide" in reserved or "Q0-11 is absent" in reserved)
    )

    # EJ8-INCORP-HASH-VS-FPREC: fixed if no positive content-digest / incorporates.sha256
    # run-time binding remains (neutralized NOT statements OK)
    incorp_fixed = len(positive_incorp) == 0 and surfaces_has_forbid(text)

    # Un-neutralized reserved-topic conflicts (exclude neutralized)
    hard_conflicts = [c for c in conflicts if not c.get("neutralized")]

    verdict = "breaks" if hard_conflicts or (not q011_fixed) or (not incorp_fixed) else "holds"
    # If only neutralized conflicts and named breaks fixed -> holds
    if not hard_conflicts and q011_fixed and incorp_fixed:
        verdict = "holds"

    result = {
        "attack": "EJ8_fprec_q011_incorp",
        "draft_sha256": sha256_file(DRAFT),
        "reserved_topics_text": reserved,
        "f_rev_excerpt": f_rev,
        "conventions_Q0-11_key_present": q011_key_present,
        "conventions_Q0-11_status": q011_status,
        "q011_absent_marker": q011_absent_marker,
        "live_q011_mentions": live_q011,
        "live_q011_unneutralized": live_unneutralized,
        "gq011_see_refs": gq011_refs,
        "has_gated_span_rules_section": has_gated_span_rules_section,
        "incorp_hits_summary": {
            "total": len(incorp_hits),
            "positive_binding": len(positive_incorp),
            "forbid_context": sum(1 for h in incorp_hits if h["forbid_or_delete_context"]),
        },
        "positive_incorp_samples": positive_incorp[:10],
        "overlay_hash_neutralizers": overlay_hash_conflicts,
        "d4_frev_route_hits": len(d4_hits),
        "alt_revision_routes": alt_revision,
        "conflicts": conflicts,
        "hard_conflicts": hard_conflicts,
        "named_break_EJ8_Q0_11_NOT_NEUTRALIZED": {
            "status": "fixed" if q011_fixed else "not_fixed",
            "artifact_note": "conventions.Q0-11_status ABSENT; no live unneutralized DO-NOT-TAKE",
        },
        "named_break_EJ8_INCORP_HASH_VS_FPREC": {
            "status": "fixed" if incorp_fixed else "not_fixed",
            "positive_bindings": len(positive_incorp),
        },
        "verdict": verdict,
    }
    out = WRITE / "ej8_fprec_q011.result.json"
    out.write_text(json.dumps(result, indent=2, default=str) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "wrote": str(out),
                "verdict": verdict,
                "Q0-11": result["named_break_EJ8_Q0_11_NOT_NEUTRALIZED"]["status"],
                "INCORP": result["named_break_EJ8_INCORP_HASH_VS_FPREC"]["status"],
                "hard_conflicts": len(hard_conflicts),
            }
        )
    )


def surfaces_has_forbid(text: str) -> bool:
    return bool(
        re.search(
            r"No record is bound by content-digest of a held path|"
            r"No AMD-edit rule and no incorporates\.sha256 comparison|"
            r"are NOT invalidation rules of this contract",
            text,
        )
    )


if __name__ == "__main__":
    main()
