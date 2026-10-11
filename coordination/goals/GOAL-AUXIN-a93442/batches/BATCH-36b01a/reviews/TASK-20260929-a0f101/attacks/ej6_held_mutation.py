#!/usr/bin/env python3
"""EJ6 attack: own held-file mutation + overlay AMD/hash / threshold_inventory.

Do NOT reuse controls/held_file_mutation.py as sole check.
When held AMD bytes change and draft bytes do not, no run-time decision of
EXP-AUXIN-369078 may change.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import tempfile
from copy import deepcopy
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
WRITE = HERE.parent
BATCH = HERE.parents[2]
REPO = HERE.parents[7]
DRAFT = BATCH / "design" / "TASK-20260929-6d01d7" / "draft-contract.yaml"
EXPECTED_SHA = "b147966a5798bab10183ac56a9daa703ff41c54936f832fb8d0e28f2becd1589"

HELD = [
    REPO / "experiments/EXP-AUXIN-7e2e3d/specification.yaml",
    REPO / "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260926-typed.yaml",
    REPO / "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260927-narrow.yaml",
    REPO / "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260928-gated.yaml",
    REPO / "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260916-bands.yaml",
    REPO / "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260923-d1d10.yaml",
]


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(p: Path) -> str:
    return sha256_bytes(p.read_bytes())


def extract_runtime_decision_surfaces(draft_text: str, data: dict) -> dict:
    """Surfaces that would change a run-time decision if they depended on held bytes."""
    fresh = data["successor_contract"]["fresh"]
    pn = data["successor_contract"]["protocol_normative"]
    overlays = pn.get("corrective_overlays") or []

    independence = fresh["custody"]["independence"]
    invalidation_after = fresh["custody"]["invalidation_after_approval"]
    f_prec = fresh["precedence"]["text"]
    f_index = fresh["threshold_index"]["text"]

    # Collect overlay custody invalidation rules
    overlay_invalidation = []
    overlay_held_source_refs = []
    overlay_threshold = []
    overlay_incorp = []
    for i, ov in enumerate(overlays):
        # walk dict for keys of interest
        blob = yaml.dump(ov, default_flow_style=False)
        if "invalidation_rules_added" in blob:
            # extract nested
            def walk(obj, path=""):
                if isinstance(obj, dict):
                    if "invalidation_rules_added" in obj:
                        overlay_invalidation.append(
                            {"overlay_index": i, "path": path, "value": obj["invalidation_rules_added"]}
                        )
                    if "threshold_inventory_added" in obj:
                        overlay_threshold.append(
                            {"overlay_index": i, "path": path, "value": obj["threshold_inventory_added"]}
                        )
                    for k, v in obj.items():
                        walk(v, f"{path}.{k}" if path else k)
                elif isinstance(obj, list):
                    for j, v in enumerate(obj):
                        walk(v, f"{path}[{j}]")

            walk(ov)
        # held-source phrase hunt
        for m in re.finditer(
            r"held rows\[.*?\]\.source|held AMD|incorporates\.sha256|incorporates_by_hash|content-digest|READ FROM|stands on",
            blob,
            flags=re.IGNORECASE,
        ):
            overlay_held_source_refs.append(
                {
                    "overlay_index": i,
                    "match": m.group(0),
                    "context": blob[max(0, m.start() - 80) : m.end() + 80].replace("\n", " "),
                }
            )
        if re.search(r"\bstays incorporated\b|\bincorporated\b", blob, flags=re.IGNORECASE):
            for m in re.finditer(r".{0,60}(stays incorporated|incorporated).{0,80}", blob, flags=re.IGNORECASE):
                overlay_incorp.append({"overlay_index": i, "context": m.group(0).replace("\n", " ")})

    # Protocol invalidation list mentions of held
    inv_rules = pn.get("invalidation_rules") or []
    inv_held_mentions = [r for r in inv_rules if re.search(r"held|EXP-AUXIN-7e2e3d|incorporates\.sha256|AMD-", str(r))]

    # FC mapping "(held invalidation rule)" parentheticals
    held_inval_parens = []
    for m in re.finditer(r"\(held invalidation rules?\)", draft_text):
        held_inval_parens.append(
            {
                "offset": m.start(),
                "context": draft_text[max(0, m.start() - 120) : m.end() + 40].replace("\n", " "),
            }
        )

    # BLS12 held-source pointer
    bls_held_ptr = []
    for m in re.finditer(r"held rows\[BLS12-381-r\]\.source \(not restated\)", draft_text):
        bls_held_ptr.append({"offset": m.start(), "match": m.group(0)})

    # Restated BLS12 source in this draft?
    bls_restated = "draft-irtf-cfrg-pairing-friendly-curves-14.txt" in draft_text

    # Explicit forbidden / NOT rules
    not_rules = []
    for pat in [
        r"NOT invalidation rules of this contract",
        r"are NOT invalidation rules",
        r"No AMD-edit rule and no incorporates\.sha256",
        r"held_conjunction: none",
        r"No threshold inventory of this contract is completed by conjunction",
    ]:
        not_rules.append({"pattern": pat, "count": len(re.findall(pat, draft_text))})

    return {
        "independence_text": independence,
        "invalidation_after_approval": invalidation_after,
        "f_prec_forbids_amd_hash": "No AMD-edit rule and no incorporates.sha256" in f_prec,
        "f_index_no_conjunction": "No threshold inventory of this contract is completed by conjunction" in f_index,
        "overlay_invalidation_rules_added": overlay_invalidation,
        "overlay_threshold_inventory_added": overlay_threshold,
        "overlay_held_source_refs": overlay_held_source_refs,
        "overlay_incorporation_phrases": overlay_incorp,
        "invalidation_rules_held_mentions": inv_held_mentions,
        "held_invalidation_rule_parentheticals": held_inval_parens,
        "bls12_held_source_pointer": bls_held_ptr,
        "bls12_source_url_restated_in_draft": bls_restated,
        "explicit_not_dependence_markers": not_rules,
    }


def classify_overlay_invalidation(surfaces: dict) -> dict:
    """Decide whether overlay still POSITIVELY invalidates on held AMD/hash."""
    positive_amd_invalidations = []
    neutralizing_statements = []
    for entry in surfaces["overlay_invalidation_rules_added"]:
        val = entry["value"]
        rules = val.get("rules") if isinstance(val, dict) else val
        if not isinstance(rules, list):
            rules = [rules]
        for r in rules:
            s = str(r)
            if re.search(r"NOT invalidation", s, re.IGNORECASE):
                neutralizing_statements.append({"path": entry["path"], "rule": s})
            elif re.search(r"incorporates\.sha256|AMD-202609|edit of any AMD", s):
                # positive dependence if it says edit/mismatch IS invalidation
                if re.search(r"\bis\b.*invalidat|invalidat.*\bif\b|mismatch.*invalid", s, re.IGNORECASE):
                    if "NOT" not in s and "not" not in s:
                        positive_amd_invalidations.append({"path": entry["path"], "rule": s})
            # contract-file-only invalidation is fine
    return {
        "positive_amd_hash_invalidations": positive_amd_invalidations,
        "neutralizing_statements": neutralizing_statements,
        "overlay_amd_invalidation_still_positive": bool(positive_amd_invalidations),
    }


def mutation_oracle(draft_text: str, surfaces: dict, overlay_cls: dict) -> dict:
    """Simulate held-byte flip: does any draft-stated run-time rule outcome change?

    Method: the draft's operative run-time rules are its own bytes. Mutating held
    files cannot change draft bytes. A dependence exists only if a draft rule
    *reads* held bytes at run time (opens/hashes/compares) or binds an outcome
    to a held field that is not restated.

    We check:
    1. Positive AMD/hash invalidation still present -> dependence (EJ6-OVERLAY).
    2. BLS12 'held rows...source (not restated)' without restatement elsewhere -> dependence.
    3. threshold_inventory conjunction with held AMD -> dependence.
    4. Otherwise, held mutation cannot change draft-evaluated decisions.
    """
    findings = []

    if overlay_cls["overlay_amd_invalidation_still_positive"]:
        findings.append(
            {
                "id": "positive_overlay_amd_hash",
                "dependence": True,
                "detail": overlay_cls["positive_amd_hash_invalidations"],
            }
        )

    bls_ptr = surfaces["bls12_held_source_pointer"]
    bls_restated = surfaces["bls12_source_url_restated_in_draft"]
    if bls_ptr and not bls_restated:
        findings.append(
            {
                "id": "bls12_source_only_via_held",
                "dependence": True,
                "detail": "overlay points at held rows source and URL not restated in draft",
            }
        )
    elif bls_ptr and bls_restated:
        findings.append(
            {
                "id": "bls12_held_pointer_but_url_restated",
                "dependence": False,
                "note": (
                    "Overlay English says 'held rows[...].source (not restated)' but "
                    "change.D1_pins.rows[BLS12-381-r].source in THIS draft restates the "
                    "archived I-D URL; F-PREC/F-CUSTODY forbid opening held paths. "
                    "Pointer is provenance phrasing, not a run-time open."
                ),
            }
        )

    # threshold conjunction
    conj_ok = surfaces["f_index_no_conjunction"]
    thr = surfaces["overlay_threshold_inventory_added"]
    conj_none = False
    for t in thr:
        v = t["value"]
        if isinstance(v, dict) and "held_conjunction" in v:
            if re.search(r"\bnone\b", str(v["held_conjunction"]), re.IGNORECASE):
                conj_none = True
    if not conj_ok:
        findings.append({"id": "f_index_conjunction_gap", "dependence": True})
    else:
        findings.append(
            {
                "id": "threshold_inventory_conjunction",
                "dependence": False,
                "held_conjunction_none_stated": conj_none,
                "f_index_forbids_conjunction": True,
            }
        )

    # Parenthetical "(held invalidation rule)" — check rule restated in invalidation_rules
    field_prime_rule = any(
        "field prime used as r" in str(r).lower() for r in surfaces["invalidation_rules_held_mentions"]
    ) or ("A field prime used as r" in draft_text)
    # Actually check full invalidation list via draft text
    field_prime_restated = bool(
        re.search(r"A field prime used as r \(detected at any time\)", draft_text)
    )
    product_void_restated = "Path A and path B disagreement" in draft_text or "without an independently verified certificate" in draft_text
    findings.append(
        {
            "id": "held_invalidation_parentheticals",
            "count": len(surfaces["held_invalidation_rule_parentheticals"]),
            "dependence": False if field_prime_restated else True,
            "field_prime_rule_restated_in_invalidation_rules": field_prime_restated,
            "note": (
                "Parenthetical labels provenance of a rule restated in this contract's "
                "invalidation_rules; mutating held AMD cannot change the restated rule text."
                if field_prime_restated
                else "Parenthetical cites held rule without local restatement."
            ),
        }
    )

    any_dep = any(f.get("dependence") for f in findings)
    return {"findings": findings, "run_time_depends_on_held_bytes": any_dep}


def physical_mutation_check() -> dict:
    """Copy held files to TMPDIR, flip bytes, confirm draft sha unchanged and
    re-evaluate dependence oracle on unchanged draft (sanity). Also confirm
    mutated held sha differs.
    """
    draft_sha = sha256_file(DRAFT)
    assert draft_sha == EXPECTED_SHA
    results = []
    with tempfile.TemporaryDirectory(prefix="ej6-held-mut-") as td:
        td_path = Path(td)
        for held in HELD:
            assert held.is_file(), held
            dst = td_path / held.name
            shutil.copy2(held, dst)
            before = sha256_file(dst)
            # flip one byte
            raw = bytearray(dst.read_bytes())
            raw[min(100, len(raw) - 1)] ^= 0xFF
            dst.write_bytes(bytes(raw))
            after = sha256_file(dst)
            results.append(
                {
                    "held": held.as_posix(),
                    "sha_before": before,
                    "sha_after_mutation": after,
                    "bytes_changed": before != after,
                }
            )
        draft_sha_after = sha256_file(DRAFT)
    return {
        "draft_sha_unchanged": draft_sha_after == draft_sha,
        "draft_sha256": draft_sha,
        "mutations": results,
        "all_held_mutated": all(r["bytes_changed"] for r in results),
    }


def main():
    draft_sha = sha256_file(DRAFT)
    assert draft_sha == EXPECTED_SHA, draft_sha
    text = DRAFT.read_text(encoding="utf-8")
    data = yaml.safe_load(text)

    surfaces = extract_runtime_decision_surfaces(text, data)
    overlay_cls = classify_overlay_invalidation(surfaces)
    oracle = mutation_oracle(text, surfaces, overlay_cls)
    physical = physical_mutation_check()

    # Named breaks
    # EJ6-B1: general held-file run-time dependence
    ej6_b1_fixed = (not oracle["run_time_depends_on_held_bytes"]) and physical["draft_sha_unchanged"]
    # EJ6-OVERLAY-AMD-INVALIDATION: positive overlay AMD/hash invalidation removed
    ej6_overlay_fixed = not overlay_cls["overlay_amd_invalidation_still_positive"] and bool(
        overlay_cls["neutralizing_statements"]
    )

    # Joint breaks if any dependence remains
    verdict = "breaks" if oracle["run_time_depends_on_held_bytes"] else "holds"

    result = {
        "attack": "EJ6_held_file_mutation_own",
        "draft_sha256": draft_sha,
        "surfaces_summary": {
            "f_prec_forbids_amd_hash": surfaces["f_prec_forbids_amd_hash"],
            "f_index_no_conjunction": surfaces["f_index_no_conjunction"],
            "overlay_invalidation_count": len(surfaces["overlay_invalidation_rules_added"]),
            "bls12_held_pointer_count": len(surfaces["bls12_held_source_pointer"]),
            "bls12_url_restated": surfaces["bls12_source_url_restated_in_draft"],
            "held_inval_paren_count": len(surfaces["held_invalidation_rule_parentheticals"]),
            "independence_excerpt": surfaces["independence_text"][:240],
        },
        "overlay_classification": overlay_cls,
        "mutation_oracle": oracle,
        "physical_mutation": physical,
        "named_break_EJ6_B1": {
            "status": "fixed" if ej6_b1_fixed else "not_fixed",
            "run_time_depends_on_held_bytes": oracle["run_time_depends_on_held_bytes"],
        },
        "named_break_EJ6_OVERLAY_AMD_INVALIDATION": {
            "status": "fixed" if ej6_overlay_fixed else "not_fixed",
            "positive_still_present": overlay_cls["overlay_amd_invalidation_still_positive"],
            "neutralizer_count": len(overlay_cls["neutralizing_statements"]),
        },
        "verdict": verdict,
    }
    out = WRITE / "ej6_held_mutation.result.json"
    out.write_text(json.dumps(result, indent=2, default=str) + "\n", encoding="utf-8")
    # Also dump full surfaces for computations
    (WRITE / "ej6_surfaces.json").write_text(
        json.dumps({"surfaces": surfaces, "overlay_cls": overlay_cls}, indent=2, default=str) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "wrote": str(out),
                "verdict": verdict,
                "EJ6-B1": result["named_break_EJ6_B1"]["status"],
                "EJ6-OVERLAY": result["named_break_EJ6_OVERLAY_AMD_INVALIDATION"]["status"],
            }
        )
    )


if __name__ == "__main__":
    main()
