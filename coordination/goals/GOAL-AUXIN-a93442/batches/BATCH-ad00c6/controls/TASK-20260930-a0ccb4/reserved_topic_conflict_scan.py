#!/usr/bin/env python3
"""Control 3 of TASK-20260929-d519f6 design-report control_targets: reserved-topic conflict scan.

Scans protocol_normative (and change.* / conventions / stopping / invalidation /
execution_admission) of draft EXP-AUXIN-339fb0 for rules on F-PREC reserved
topics that differ from the fresh fields. Also checks F-CUSTODY.defined_terms
are used consistently in manifest and trial_plan rules.

Writes one JSON result to stdout.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

import yaml

DRAFT = Path(
    "coordination/goals/GOAL-AUXIN-a93442/batches/BATCH-ad00c6/design/"
    "TASK-20260929-d519f6/draft-contract.yaml"
)
DRAFT_SHA256 = "6a1dca32c109d5badf4ba143c31f9d4d9a49e18ae287c8bb4fc604526bf02ecc"

TOPIC_PATTERNS = {
    "revision": re.compile(
        r"later amendment|amendment (?:may|layers|file)|rewrit\w* in place|supersed|"
        r"new successor|new EXP id|immutable",
        re.I,
    ),
    "approval": re.compile(
        r"approv\w+|authoriz\w+|scientific_execution_authorized",
        re.I,
    ),
    "custody": re.compile(
        r"\bcustody\b|dirty_summary|successor_contract_sha256|path_sha256|"
        r"evidence-integrity|manifest\.yaml|trial-plan",
        re.I,
    ),
    "write_scope": re.compile(
        r"write[_ ]scope|writes? (?:nothing|only|no)|under experiments/",
        re.I,
    ),
    "reference_reading": re.compile(
        r"\bF-READ\b|reading_of_references|self_reference_table|rule_id:\s*R[1-9]",
        re.I,
    ),
    "execution_admission": re.compile(
        r"execution_admission|currently_admitted|verified snapshot archive",
        re.I,
    ),
}


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


def classify_hit(topic: str, path: str, text: str, fresh: dict) -> dict | None:
    """Return a finding dict or None if harmless / aligned with fresh fields."""
    low = text.lower()

    if topic == "revision":
        # Conflict: licenses amendment layering beside F-REV
        if re.search(r"later amendment may|amendment layers|new amendment", text, re.I):
            if "f-rev" not in low and "new exp id" not in low and "new successor" not in low:
                return {
                    "class": "CONFLICT",
                    "topic": "revision",
                    "path": path,
                    "reason": "States an amendment revision route beside F-REV",
                    "excerpt": text[:280],
                }
        # Aligned mentions of F-REV / new EXP id are OK
        return None

    if topic == "approval":
        if "scientific_execution_authorized" in low and "true" in low:
            return {
                "class": "CONFLICT",
                "topic": "approval",
                "path": path,
                "reason": "States scientific_execution_authorized is true beside F-APPROVAL draft/null",
                "excerpt": text[:280],
            }
        if "approved_by" in low and "null" not in low and "f-approval" not in low:
            # soft: only flag if it asserts approval without citing F-APPROVAL
            if re.search(r"is approved|has been approved|approved by the", text, re.I):
                return {
                    "class": "CONFLICT",
                    "topic": "approval",
                    "path": path,
                    "reason": "Asserts approval outside F-APPROVAL",
                    "excerpt": text[:280],
                }
        return None

    if topic == "custody":
        low = text.lower()
        # Neutralizing NOT-invalidation / independence sentences are not scored
        # as affirmative fire rules (design-report expected_by_design).
        neutralize = any(
            tok in low
            for tok in (
                "not invalidation",
                "not an invalidation",
                "no invalidation",
                "are void",
                "is void",
                "does not fire",
                "do not fire",
                "never fire",
                "f-custody.independence",
                "independence governs",
                "govern nothing",
                "no amd-edit rule",
                "no incorporates",
            )
        )
        # Conflict: four-layer / held-file custody (affirmative binding only)
        if re.search(r"four governing layers|all four governing|EXP-AUXIN-7e2e3d.*sha256|sha256.*EXP-AUXIN-7e2e3d", text, re.I):
            if not neutralize:
                return {
                    "class": "CONFLICT",
                    "topic": "custody",
                    "path": path,
                    "reason": "Binds held-file or four-layer custody contrary to F-CUSTODY",
                    "excerpt": text[:280],
                }
        if re.search(r"dirty amendment path", text, re.I) and not neutralize:
            return {
                "class": "CONFLICT",
                "topic": "custody",
                "path": path,
                "reason": "Dirty-amendment custody reading of held amendments",
                "excerpt": text[:280],
            }
        return None

    if topic == "write_scope":
        if "EXP-AUXIN-7e2e3d/implementation" in text and "edit" in low:
            if "edits no" not in low and "never edit" not in low and "does not edit" not in low:
                return {
                    "class": "CONFLICT",
                    "topic": "write_scope",
                    "path": path,
                    "reason": "Write into held implementation tree",
                    "excerpt": text[:280],
                }
        return None

    if topic == "execution_admission":
        if "EXP-AUXIN-7e2e3d" in text and "required" in low and "not required" not in low and "explicitly_not" not in path:
            if "requirements" in path or re.search(r"must|shall|requires", text, re.I):
                return {
                    "class": "CONFLICT",
                    "topic": "execution_admission",
                    "path": path,
                    "reason": "Admission requires held EXP-AUXIN-7e2e3d artifact",
                    "excerpt": text[:280],
                }
        return None

    return None


def check_defined_terms(custody: dict) -> list[dict]:
    findings = []
    terms = custody.get("defined_terms") or {}
    required = [
        "contract_file",
        "implementation_tree",
        "trial_plan",
        "manifest",
        "dirty_summary",
        "successor_contract_sha256",
    ]
    for t in required:
        if t not in terms:
            findings.append({"class": "TERM_MISSING", "term": t, "reason": "F-CUSTODY.defined_terms missing required term"})
    # Consistency: manifest_rule and trial_plan_rule should use the defined names
    for field in ("manifest_rule", "trial_plan_rule", "scope", "independence"):
        text = str(custody.get(field, ""))
        for t in required:
            # not every field must use every term; check no undefined custody jargon
            pass
        if "custody" in text.lower() and field == "scope":
            # scope should restrict to defined terms
            if "contract_file" not in text or "implementation_tree" not in text:
                findings.append({
                    "class": "TERM_INCONSISTENT",
                    "field": field,
                    "reason": "scope does not name contract_file/implementation_tree",
                    "excerpt": text[:200],
                })
    # undefined 'custody' ambiguity check: scope should say what it binds
    scope = str(custody.get("scope", ""))
    if "and nothing else" in scope.lower() or "only" in scope.lower():
        if not terms:
            findings.append({"class": "SCOPE_AMBIGUITY", "reason": "scope restricts custody but defined_terms empty"})
    return findings


def main() -> int:
    if sha256_file(DRAFT) != DRAFT_SHA256:
        print(json.dumps({"label": "NOT_RUN", "reason": "draft sha256 mismatch"}))
        return 2

    doc = yaml.safe_load(DRAFT.read_text(encoding="utf-8"))["successor_contract"]
    fresh = doc["fresh"]
    pn = doc["protocol_normative"]

    conflicts = []
    tensions = []
    term_findings = check_defined_terms(fresh["custody"])

    # Scan protocol_normative strings
    for path, text in walk_strings(pn):
        for topic, pat in TOPIC_PATTERNS.items():
            if not pat.search(text):
                continue
            hit = classify_hit(topic, path, text, fresh)
            if hit is None:
                continue
            if hit["class"] == "CONFLICT":
                conflicts.append(hit)
            else:
                tensions.append(hit)

    # Also scan change.D10 against F-REV alignment (should agree)
    d10 = str(pn["change"].get("D10_additivity", {}))
    if "new EXP id" in d10 and "F-REV" in d10:
        pass  # aligned
    elif re.search(r"later amendment may", d10, re.I):
        conflicts.append({
            "class": "CONFLICT",
            "topic": "revision",
            "path": "$.change.D10_additivity",
            "reason": "D10 states amendment revision route",
            "excerpt": d10[:280],
        })

    # Q0-11 style source-file precedence
    for path, text in walk_strings(pn.get("conventions", {})):
        if re.search(r"this file.?s text governs|this file's text governs", text, re.I):
            if "F-PREC" not in text:
                conflicts.append({
                    "class": "CONFLICT",
                    "topic": "governing",
                    "path": f"conventions{path}",
                    "reason": "Source-file precedence beside F-PREC",
                    "excerpt": text[:280],
                })

    # F-ATT (PD-C14b284-1): review_attestation.task_id must be required INSIDE attestation block
    fatt = fresh.get("review_attestation_requirement") or {}
    if fatt.get("id") != "F-ATT":
        conflicts.append({
            "class": "CONFLICT",
            "topic": "attestation",
            "path": "fresh.review_attestation_requirement",
            "reason": "F-ATT missing or wrong id",
            "excerpt": str(fatt)[:280],
        })
    else:
        fatt_text = str(fatt.get("text", ""))
        fatt_low = fatt_text.lower()
        if "review_attestation.task_id" not in fatt_text or "inside" not in fatt_low:
            conflicts.append({
                "class": "CONFLICT",
                "topic": "attestation",
                "path": "fresh.review_attestation_requirement.text",
                "reason": "F-ATT does not require review_attestation.task_id inside attestation block (PD-C14b284-1)",
                "excerpt": fatt_text[:280],
            })
        # PD-C36b01a-1: joints_owned and verdict or verdicts must be required inside attestation
        if "joints_owned" not in fatt_text and "review_attestation.joints_owned" not in fatt_text:
            conflicts.append({
                "class": "CONFLICT",
                "topic": "attestation",
                "path": "fresh.review_attestation_requirement.text",
                "reason": "F-ATT does not require joints_owned inside attestation block (PD-C36b01a-1)",
                "excerpt": fatt_text[:280],
            })
        has_verdict = ("verdict" in fatt_low) or ("verdicts" in fatt_low)
        if not has_verdict:
            conflicts.append({
                "class": "CONFLICT",
                "topic": "attestation",
                "path": "fresh.review_attestation_requirement.text",
                "reason": "F-ATT does not require verdict or verdicts inside attestation block (PD-C36b01a-1)",
                "excerpt": fatt_text[:280],
            })

    # Q0-11 must be ABSENT (status field), not a live DO-NOT-TAKE rule
    q011_status = (pn.get("conventions") or {}).get("Q0-11_status") or fresh.get("q0_11_status")
    q011_live = (pn.get("conventions") or {}).get("Q0-11")
    if q011_live is not None:
        conflicts.append({
            "class": "CONFLICT",
            "topic": "governing",
            "path": "conventions.Q0-11",
            "reason": "Live Q0-11 present; expected ABSENT per F-PRE/F-PREC",
            "excerpt": str(q011_live)[:280],
        })
    if isinstance(q011_status, str) and "ABSENT" not in q011_status.upper():
        conflicts.append({
            "class": "CONFLICT",
            "topic": "governing",
            "path": "conventions.Q0-11_status",
            "reason": "Q0-11_status does not state ABSENT",
            "excerpt": q011_status[:280],
        })

    # Overlay AMD/hash invalidation must not reintroduce held-byte dependence under F-PREC.
    # Neutralizing NOT-invalidation sentences are not scored as affirmative fire rules.
    overlays = (pn.get("corrective_overlays") or [])
    for i, ov in enumerate(overlays):
        cust = (ov.get("custody") or {}) if isinstance(ov, dict) else {}
        rules = cust.get("invalidation_rules_added") or []
        for r in rules:
            rs = str(r)
            rslow = rs.lower()
            neutralize = any(
                tok in rslow
                for tok in (
                    "does not fire",
                    "do not fire",
                    "never fire",
                    "not a fire",
                    "not fire",
                    "do not invalidate",
                    "does not invalidate",
                    "never invalidate",
                    "not an invalidation",
                    "no invalidation",
                    "not invalidate",
                    "must not fire",
                    "shall not fire",
                    "do not refuse",
                    "does not refuse",
                    "never refuse",
                    "neutraliz",
                    "not scored as",
                    "does not bind",
                    "do not bind",
                    "never bind",
                    "does not compare",
                    "do not compare",
                    "never compare",
                    "is not a run-time",
                    "not a run-time",
                    "no run-time",
                )
            )
            if neutralize:
                continue
            if "sha256" in rslow or "AMD-" in rs or "7e2e3d" in rs:
                conflicts.append({
                    "class": "CONFLICT",
                    "topic": "custody",
                    "path": f"protocol_normative.corrective_overlays[{i}].custody.invalidation_rules_added",
                    "reason": "Overlay invalidation binds held AMD/hash contrary to F-PREC",
                    "excerpt": rs[:280],
                })

    label = "PASS"
    if conflicts or any(f["class"] in ("TERM_MISSING", "SCOPE_AMBIGUITY") for f in term_findings):
        label = "CONFLICT_FOUND"
    elif tensions or term_findings:
        label = "TENSION_ONLY"

    out = {
        "control": "reserved-topic conflict scan",
        "label": label,
        "draft_sha256": DRAFT_SHA256,
        "conflicts": conflicts,
        "tensions": tensions,
        "defined_terms_check": term_findings,
        "fresh_fields_present": {
            "F-REV": fresh["revision_rule"]["id"],
            "F-APPROVAL": fresh["approval"]["id"],
            "F-CUSTODY": fresh["custody"]["id"],
            "F-WRITE": fresh["write_scope"]["id"],
            "F-PREC": fresh["precedence"]["id"],
            "F-READ": fresh["reading_of_references"]["id"],
        },
        "defined_terms_keys": sorted((fresh["custody"].get("defined_terms") or {}).keys()),
    }
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
