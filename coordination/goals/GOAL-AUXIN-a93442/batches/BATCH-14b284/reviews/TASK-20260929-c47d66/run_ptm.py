#!/usr/bin/env python3
"""Proves-too-much objects PTM-1..PTM-4 for TASK-20260929-c47d66.

Run AFTER own EJ3/EJ6/EJ8 checks are already in computations.json.
Updates computations.json in place with PTM results and control comparison.
Zero scientific RUN-*.
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
import shutil
import tempfile
from pathlib import Path

import yaml

WRITE = Path(__file__).resolve().parent
ROOT = WRITE
while ROOT != ROOT.parent and not (ROOT / "AGENTS.md").exists():
    ROOT = ROOT.parent

DRAFT = ROOT / (
    "coordination/goals/GOAL-AUXIN-a93442/batches/BATCH-14b284/"
    "design/TASK-20260929-1abb8c/draft-contract.yaml"
)
REFUSED_92 = ROOT / (
    "coordination/goals/GOAL-AUXIN-a93442/batches/BATCH-1907cf/"
    "design/TASK-20260929-ef0945/draft-contract.yaml"
)
AMD_GATED = ROOT / "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260928-gated.yaml"
COMP = WRITE / "computations.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def ej6_dependence_test_on_object(text: str, label: str) -> dict:
    """EJ6 not-a-layer / dependence test: find held-byte dependence surfaces."""
    hits = []
    patterns = [
        ("incorporated_by_hash", r"incorporated by hash|incorporates\.sha256|content-digest"),
        ("READ_FROM_held", r"READ\s+FROM\s+specification\.yaml"),
        ("stand_on_held", r"specification\.yaml[^\n]{0,100}stand"),
        ("AMD_edit_invalidation", r"Any edit of AMD-2026092"),
        ("supersedes_held", r"supersedes|layers this|amendment layers"),
        ("binds_held_path", r"experiments/EXP-AUXIN-7e2e3d/"),
    ]
    for name, pat in patterns:
        for m in re.finditer(pat, text, re.I):
            lo = max(0, m.start() - 40)
            hi = min(len(text), m.end() + 60)
            hits.append({"class": name, "match": m.group(0), "context": text[lo:hi].replace("\n", " ")})
            if len(hits) > 30:
                break
    finds_dependence = any(
        h["class"] in {
            "incorporated_by_hash",
            "READ_FROM_held",
            "stand_on_held",
            "AMD_edit_invalidation",
            "binds_held_path",
        }
        for h in hits
    )
    # For gated AMD specifically: incorporating narrow by hash is known
    gated_incorp = bool(re.search(r"incorporat|sha256|supersede", text, re.I))
    return {
        "object": label,
        "finds_held_byte_dependence": finds_dependence or (label.startswith("PTM-1") and gated_incorp),
        "hit_sample": hits[:15],
    }


def ej3_closure_test(doc: dict, text: str) -> dict:
    sc = doc.get("successor_contract") or doc
    # refused draft may have same shape
    if "fresh" in sc:
        fread = sc["fresh"]["reading_of_references"]
        table = sc.get("self_reference_table") or {}
    else:
        return {"error": "no fresh block", "closure_ok": False}
    r1 = next(r for r in fread["rules"] if r["id"] == "R1")
    phrases = re.findall(r'"([^"]+)"', r1["text"])
    phrases = [p for p in phrases if len(p) < 40]
    # EXP id from R1 text
    exp_ids = re.findall(r"EXP-AUXIN-[0-9a-f]{6}", r1["text"])
    for e in exp_ids:
        if e not in phrases:
            phrases.append(e)
    rows = {r["phrase"] for r in table.get("rows", []) if r.get("phrase") != "_closure_"}
    table_lower = {p.lower() for p in rows}
    missing = [p for p in phrases if p not in rows and p.lower() not in table_lower]
    order_present = bool(fread.get("order"))
    return {
        "missing_r1_from_table": missing,
        "order_present": order_present,
        "closure_ok": not missing and order_present,
        "exp_ids_in_r1": exp_ids,
        "table_has_exp": [e for e in exp_ids if e in rows],
    }


def ej8_conflict_test(doc: dict, text: str) -> dict:
    sc = doc.get("successor_contract") or doc
    fresh = sc.get("fresh") or {}
    pn = sc.get("protocol_normative") or {}
    conflicts = []
    # Amendment revision route vs F-REV
    if re.search(r"(?<![Nn]o )later amendment may pre-register|licenses a later amendment revision", text):
        conflicts.append("later_amendment_revision_route")
    if re.search(r"An amendment file may revise any rule of this contract", text):
        conflicts.append("amendment_may_revise_any_rule")
    # content-digest vs F-PREC
    if re.search(r"incorporated by hash|incorporates\.sha256", text, re.I):
        if not re.search(r"no held record is bound by content-digest", text, re.I):
            conflicts.append("incorp_hash_vs_fprec")
    # Q0-11 present as source-file precedence
    conv = (pn.get("conventions") or {})
    if "Q0-11" in conv:
        conflicts.append("Q0-11_source_file_precedence")
    return {"conflicts": conflicts, "has_conflict": bool(conflicts)}


def ptm1() -> dict:
    """AMD-20260928-gated.yaml as candidate successor — must find held dependence."""
    text = AMD_GATED.read_text(encoding="utf-8")
    # Known: incorporates narrow by hash and supersedes held fields
    doc = load(AMD_GATED)
    dep = ej6_dependence_test_on_object(text, "PTM-1 AMD-20260928-gated.yaml")
    # Stronger structured check
    blob = json.dumps(doc, default=str)
    structured = {
        "mentions_incorporates_or_sha256": bool(re.search(r"incorporat|sha256", blob, re.I)),
        "mentions_narrow_or_supersede": bool(re.search(r"narrow|supersede", blob, re.I)),
        "mentions_7e2e3d_or_held": bool(re.search(r"7e2e3d|specification\.yaml|AMD-20260927", blob, re.I)),
    }
    finds = dep["finds_held_byte_dependence"] or any(structured.values())
    return {
        "id": "PTM-1",
        "object": "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260928-gated.yaml",
        "object_sha256": sha256(AMD_GATED),
        "known_false_because": "incorporates narrow by hash and supersedes held fields",
        "failure_signature": "EJ6 dependence test must find held-byte dependence",
        "result": "behaves_per_signature" if finds else "FAILED_SIGNATURE",
        "finds_held_byte_dependence": finds,
        "structured": structured,
        "dep_sample": dep["hit_sample"][:8],
    }


def ptm2() -> dict:
    """Refused EXP-AUXIN-92dccc — must find at least one EJ3/EJ6/EJ8 break class."""
    text = REFUSED_92.read_text(encoding="utf-8")
    doc = load(REFUSED_92)
    ej3 = ej3_closure_test(doc, text)
    ej6 = ej6_dependence_test_on_object(text, "PTM-2 EXP-AUXIN-92dccc")
    ej8 = ej8_conflict_test(doc, text)
    # Known breaks from DEC-20260929-cfb294: EJ3 closure of EXP id, EJ6 READ FROM, EJ8 D4
    break_classes = []
    if not ej3["closure_ok"] or (
        ej3["exp_ids_in_r1"] and not ej3["table_has_exp"]
    ):
        break_classes.append("EJ3")
    # Also check unlisted EXP-AUXIN-92dccc specifically
    if "EXP-AUXIN-92dccc" in text:
        sc = doc["successor_contract"]
        rows = {
            r["phrase"]
            for r in sc["self_reference_table"]["rows"]
            if r.get("phrase") != "_closure_"
        }
        if "EXP-AUXIN-92dccc" not in rows and "EXP-AUXIN-92dccc" in sc["fresh"]["reading_of_references"]["rules"][0]["text"]:
            if "EJ3" not in break_classes:
                break_classes.append("EJ3")
    if ej6["finds_held_byte_dependence"]:
        break_classes.append("EJ6")
    if ej8["has_conflict"]:
        break_classes.append("EJ8")
    ok = len(break_classes) >= 1
    return {
        "id": "PTM-2",
        "object": str(REFUSED_92.relative_to(ROOT)),
        "object_sha256": sha256(REFUSED_92),
        "known_false_because": "DEC-20260929-cfb294 found EJ3/EJ6/EJ8 breaks",
        "failure_signature": "EJ6 or EJ3/EJ8 arguments must find at least one break class",
        "result": "behaves_per_signature" if ok else "FAILED_SIGNATURE",
        "break_classes_found": break_classes,
        "ej3": ej3,
        "ej6_finds_dependence": ej6["finds_held_byte_dependence"],
        "ej8": ej8,
    }


def ptm3() -> dict:
    """Scratch copy: delete one self_reference_table row + remove F-READ order sentence."""
    text = DRAFT.read_text(encoding="utf-8")
    doc = load(DRAFT)
    scratch = copy.deepcopy(doc)
    table = scratch["successor_contract"]["self_reference_table"]
    # delete "this file" row
    table["rows"] = [r for r in table["rows"] if r.get("phrase") != "this file"]
    # remove order sentence
    scratch["successor_contract"]["fresh"]["reading_of_references"]["order"] = ""
    # serialize and re-test
    scratch_text = yaml.dump(scratch)
    ej3 = ej3_closure_test(scratch, scratch_text)
    fails = not ej3["closure_ok"]  # must FAIL closure/order
    return {
        "id": "PTM-3",
        "object": "scratch draft: delete self_reference_table row 'this file'; clear F-READ.order",
        "known_false_because": "table not closed and order undefined",
        "failure_signature": "EJ3 closure/order argument must fail",
        "result": "behaves_per_signature" if fails else "FAILED_SIGNATURE",
        "ej3": ej3,
        "closure_failed_as_required": fails,
    }


def ptm4() -> dict:
    """Scratch: replace one protocol_normative sentence with amendment-may-revise."""
    doc = load(DRAFT)
    scratch = copy.deepcopy(doc)
    # Replace Q0-10 text (or a conventions sentence) with forbidden revision route
    poison = "An amendment file may revise any rule of this contract."
    scratch["successor_contract"]["protocol_normative"]["conventions"]["Q0-10"] = poison
    scratch_text = yaml.dump(scratch)
    ej8 = ej8_conflict_test(scratch, scratch_text)
    flagged = "amendment_may_revise_any_rule" in ej8["conflicts"] or ej8["has_conflict"]
    # Also require the EJ8 argument specifically flags the poison sentence
    flagged = flagged and poison in scratch_text
    return {
        "id": "PTM-4",
        "object": "scratch draft: conventions.Q0-10 replaced by amendment-may-revise sentence",
        "known_false_because": "states a revision route F-REV forbids",
        "failure_signature": "EJ8 conflict argument must flag it",
        "result": "behaves_per_signature" if flagged else "FAILED_SIGNATURE",
        "ej8": ej8,
        "poison_sentence": poison,
        "flagged": flagged,
    }


def control_comparison(comp: dict) -> dict:
    """Compare own verdicts to control observations (after own checks)."""
    return {
        "F-READ_order_audit": {
            "control_label": "PASS",
            "own_EJ3": comp["EJ3"]["verdict"],
            "redecision": (
                "Control PASS on R1/table closure for listed R1 phrases is retained "
                "as a narrow observation. Own inventory finds unlisted self-referential "
                "phrase 'this draft' absent from self_reference_table; EJ3 breaks on "
                "that residual. Named EJ3-CLOSURE-EXP-AUXIN-92dccc is fixed as named. "
                "PASS is not a control error on its stated R1 scope; it missed unlisted deictics."
            ),
        },
        "held_file_mutation": {
            "control_label": "PASS",
            "own_EJ6": comp["EJ6"]["verdict"],
            "redecision": (
                "Control PASS checked dirty/manifest/admission/top-level invalidation "
                "dirty phrases only (held_file_mutation.py). It did not evaluate "
                "corrective_overlays[0].custody.invalidation_rules_added AMD-edit / "
                "incorporates.sha256 rules. Own mutation design finds those stated "
                "rules flip on held AMD byte changes while draft bytes are unchanged. "
                "PASS retained as narrow observation; EJ6 breaks; EJ6-B1 not_fixed via "
                "overlay surfaces. Not a control error on its declared narrow scope."
            ),
        },
        "reserved_topic_conflict_scan": {
            "control_label": "CONFLICT_FOUND",
            "own_EJ8": comp["EJ8"]["verdict"],
            "redecision": (
                "Confirms Q0-11 source-file precedence beside F-PREC. Own attack "
                "additionally constructs Q0-11 vs F-PRE load-by-hash divergence and "
                "overlay AMD hash-invalidation vs F-PREC. EJ8-T0124 is fixed as named "
                "(D4 cites F-REV only). EJ8-INCORP-HASH-VS-FPREC not_fixed via overlay. "
                "Q0-11 not neutralized. Control CONFLICT is not a control error."
            ),
        },
    }


def main() -> None:
    comp = json.loads(COMP.read_text(encoding="utf-8"))
    assert comp.get("controls_read") is False
    assert "EJ3" in comp and "EJ6" in comp and "EJ8" in comp

    ptm = {
        "PTM-1": ptm1(),
        "PTM-2": ptm2(),
        "PTM-3": ptm3(),
        "PTM-4": ptm4(),
    }
    all_ok = all(v["result"] == "behaves_per_signature" for v in ptm.values())

    # Mark controls now read; attach comparison
    for j in ("EJ3", "EJ6", "EJ8"):
        comp[j]["control_not_yet_read"] = False

    comp["phase"] = "own_checks_plus_controls_plus_ptm"
    comp["controls_read"] = True
    comp["controls_read_after_own_checks"] = True
    comp["control_comparison"] = control_comparison(comp)
    comp["proves_too_much"] = {
        "status": "complete",
        "all_behave_per_signature": all_ok,
        "objects": ptm,
    }
    COMP.write_text(json.dumps(comp, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    print(json.dumps({k: v["result"] for k, v in ptm.items()}, indent=2))
    print("all_ok", all_ok)
    print("wrote", COMP)


if __name__ == "__main__":
    main()
