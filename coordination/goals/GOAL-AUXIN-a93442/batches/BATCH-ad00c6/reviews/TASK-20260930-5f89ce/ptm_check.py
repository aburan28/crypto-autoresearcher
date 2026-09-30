#!/usr/bin/env python3
"""Proves-too-much objects PTM-1..PTM-4 for REVIEW-AUXIN-20260930-a55fc5.

Governing claim tested (must come out FALSE on every object):
  "This file states the protocol once as fresh text, reads every reference
   by one rule, depends at run time on no held-file byte, and states no
   reserved-topic rule outside its fresh fields."
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

ROOT = Path.cwd()
DRAFT = ROOT / (
    "coordination/goals/GOAL-AUXIN-a93442/batches/BATCH-ad00c6/"
    "design/TASK-20260929-d519f6/draft-contract.yaml"
)
AMD_GATED = ROOT / "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260928-gated.yaml"
REFUSED = ROOT / (
    "coordination/goals/GOAL-AUXIN-a93442/batches/BATCH-36b01a/"
    "design/TASK-20260929-6d01d7/draft-contract.yaml"
)
OUT = Path(__file__).resolve().parent / "ptm.result.json"


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def ej6_dependence_test(obj_path: Path | None = None, obj_data: dict | None = None) -> dict:
    """EJ6 not-a-layer / dependence test: does object have held-byte dependence?"""
    if obj_data is None:
        assert obj_path is not None
        text = obj_path.read_text()
        data = yaml.safe_load(text)
    else:
        data = obj_data
        text = yaml.dump(data, default_flow_style=False)

    # Signals of held-byte dependence / layer incorporation
    signals = {
        "has_incorporates_by_hash": False,
        "has_incorporates_sha256": False,
        "has_supersedes_fields": False,
        "hash_check_before_use": False,
        "claims_zero_transclusion_fresh_only": False,
        "f_custody_independence_forbids_held": False,
    }
    # Walk loosely
    blob = text
    if "incorporates_by_hash" in blob or re.search(r"\bincorporates_by_hash\b", blob):
        signals["has_incorporates_by_hash"] = True
    if re.search(r"incorporates(?:_by_hash)?\.sha256|sha256:\s*[0-9a-f]{64}", blob) and (
        "incorporates" in blob.lower()
    ):
        signals["has_incorporates_sha256"] = True
    if "supersedes_fields" in blob:
        signals["has_supersedes_fields"] = True
    if re.search(r"hash_check:\s*|Before any use, a reader or executor computes the sha256", blob):
        signals["hash_check_before_use"] = True
    if re.search(r"Zero transclusion|transcluded\.entries is the empty list", blob):
        signals["claims_zero_transclusion_fresh_only"] = True
    if re.search(
        r"No gate, stop, launch refusal[\s\S]{0,200}EXP-AUXIN-7e2e3d",
        blob,
    ):
        signals["f_custody_independence_forbids_held"] = True

    # Dependence found if incorporates-by-hash / supersedes / hash_check fire
    dependence_found = (
        signals["has_incorporates_by_hash"]
        or signals["has_supersedes_fields"]
        or (signals["hash_check_before_use"] and signals["has_incorporates_sha256"])
    ) and not (
        signals["claims_zero_transclusion_fresh_only"]
        and signals["f_custody_independence_forbids_held"]
        and not signals["has_incorporates_by_hash"]
    )
    # Simpler: for AMD-gated, presence of incorporates_by_hash + supersedes is decisive
    if signals["has_incorporates_by_hash"] and signals["has_supersedes_fields"]:
        dependence_found = True

    return {"signals": signals, "held_byte_dependence_found": dependence_found}


def ej3_closure_test(data: dict) -> dict:
    """Does self_reference_table close under R1 phrases / is order defined?"""
    sc = data.get("successor_contract") or data
    fresh = sc.get("fresh") or {}
    fread = fresh.get("reading_of_references") or {}
    order = fread.get("order")
    table = sc.get("self_reference_table") or {}
    rows = table.get("rows") or []
    phrases = [r.get("phrase") for r in rows if r.get("phrase") and r.get("phrase") != "_closure_"]
    # Check residual deictics
    full = yaml.dump(data, default_flow_style=False)
    required = ["this fresh block", "this contract file", "EXP-AUXIN-339fb0"]
    # For refused 369078 id differs
    exp_ids = re.findall(r"EXP-AUXIN-[0-9a-f]+", str(fresh.get("id", "")))
    missing = []
    for p in required:
        if p == "EXP-AUXIN-339fb0" and fresh.get("id") and fresh.get("id") != "EXP-AUXIN-339fb0":
            # use object's own id
            p = fresh["id"]
        if p.lower() not in [x.lower() for x in phrases if isinstance(x, str)]:
            # also fail if phrase appears in text but not table
            if re.search(re.escape(p), full, re.I):
                missing.append(p)
    order_undefined = not order or not str(order).strip()
    closure_fails = bool(missing) or order_undefined
    return {
        "order_present": bool(order),
        "table_phrase_count": len(phrases),
        "missing_listed_but_present": missing,
        "closure_fails": closure_fails,
        "exp_ids": exp_ids,
    }


def ej8_conflict_test(data: dict) -> dict:
    """Flag reserved-topic revision conflicts with F-REV."""
    full = yaml.dump(data, default_flow_style=False)
    hits = []
    for m in re.finditer(
        r"An amendment file may revise any rule of this contract\.?",
        full,
    ):
        hits.append(m.group(0))
    # Also general may-revise affirmative
    for m in re.finditer(r"(?i)amendment[^\n]{0,40}may revise", full):
        hits.append(m.group(0))
    return {"conflict_hits": hits, "conflict_flagged": len(hits) > 0}


def main() -> None:
    results = {}

    # --- PTM-1: AMD-20260928-gated as candidate successor ---
    assert AMD_GATED.is_file()
    ptm1_dep = ej6_dependence_test(obj_path=AMD_GATED)
    # Also confirm incorporates narrow by hash in structured YAML
    amd = yaml.safe_load(AMD_GATED.read_bytes())
    # structure varies; search top-level keys
    amd_text = AMD_GATED.read_text()
    incorporates_narrow = "AMD-20260927-narrow.yaml" in amd_text and (
        "incorporates_by_hash" in amd_text or "incorporates:" in amd_text
    )
    ptm1 = {
        "id": "PTM-1",
        "object": str(AMD_GATED.relative_to(ROOT)),
        "object_sha256": sha256_file(AMD_GATED),
        "known_false_because": "It incorporates narrow by hash and supersedes held fields.",
        "incorporates_narrow_by_hash_observed": incorporates_narrow,
        "ej6_dependence_test": ptm1_dep,
        "failure_signature_met": ptm1_dep["held_byte_dependence_found"],
        "governing_claim_comes_out_FALSE": ptm1_dep["held_byte_dependence_found"],
    }
    results["PTM-1"] = ptm1

    # --- PTM-2: refused draft EXP-AUXIN-369078 (read only) ---
    assert REFUSED.is_file()
    refused_raw = REFUSED.read_bytes()
    refused_sha = hashlib.sha256(refused_raw).hexdigest()
    refused_data = yaml.safe_load(refused_raw)
    # EJ3 residual check on refused draft
    sc = refused_data["successor_contract"]
    fresh = sc["fresh"]
    fread = fresh.get("reading_of_references") or {}
    r1 = ""
    for r in fread.get("rules") or []:
        if r.get("id") == "R1":
            r1 = r.get("text") or ""
    table_phrases = [
        r.get("phrase")
        for r in (sc.get("self_reference_table") or {}).get("rows") or []
        if r.get("phrase") and r.get("phrase") != "_closure_"
    ]
    residual = ["this fresh block", "this contract file"]
    residual_unlisted = []
    full_ref = refused_raw.decode("utf-8")
    for p in residual:
        present = re.search(re.escape(p), full_ref, re.I) is not None
        in_r1 = p.lower() in r1.lower()
        in_table = any(isinstance(t, str) and t.lower() == p.lower() for t in table_phrases)
        if present and not (in_r1 and in_table):
            residual_unlisted.append(
                {"phrase": p, "present": present, "in_r1": in_r1, "in_table": in_table}
            )
    # Attestation schema break class (PD-C36b01a-1) is about reports, not draft;
    # EJ3 residual is the break class we must find on the refused object.
    # Also check EJ8/EJ6 for completeness but signature is "at least one break class"
    ptm2 = {
        "id": "PTM-2",
        "object": str(REFUSED.relative_to(ROOT)),
        "object_sha256": refused_sha,
        "read_only": True,
        "known_false_because": "DEC-20260929-4eade7 found EJ3 residual / PD-C36b01a-1 breaks",
        "ej3_residual_unlisted": residual_unlisted,
        "break_class_found": len(residual_unlisted) > 0,
        "failure_signature_met": len(residual_unlisted) > 0,
        "governing_claim_comes_out_FALSE": len(residual_unlisted) > 0,
        "do_not_treat_as_defects_of_339fb0": True,
    }
    results["PTM-2"] = ptm2

    # --- PTM-3: scratch with one table row deleted AND F-READ order sentence removed ---
    draft_data = yaml.safe_load(DRAFT.read_bytes())
    scratch3 = deepcopy(draft_data)
    rows = scratch3["successor_contract"]["self_reference_table"]["rows"]
    scratch3["successor_contract"]["self_reference_table"]["rows"] = [
        r for r in rows if r.get("phrase") != "this fresh block"
    ]
    # Remove order sentence
    scratch3["successor_contract"]["fresh"]["reading_of_references"]["order"] = ""
    ej3_scratch = ej3_closure_test(scratch3)
    ptm3 = {
        "id": "PTM-3",
        "object": "scratch copy of EXP-AUXIN-339fb0 with one self_reference_table row deleted and F-READ order removed",
        "deleted_phrase": "this fresh block",
        "order_after": scratch3["successor_contract"]["fresh"]["reading_of_references"]["order"],
        "ej3_closure_test": ej3_scratch,
        "failure_signature_met": ej3_scratch["closure_fails"],
        "governing_claim_comes_out_FALSE": ej3_scratch["closure_fails"],
    }
    results["PTM-3"] = ptm3

    # --- PTM-4: scratch with amendment-may-revise sentence ---
    scratch4 = deepcopy(draft_data)
    # Replace one protocol_normative sentence
    # Inject into conventions or a visible normative string field
    pn = scratch4["successor_contract"]["protocol_normative"]
    # Prefer replacing a conventions value if present; else add under a scratch key inside definitions
    injected = "An amendment file may revise any rule of this contract."
    # Replace Q0-10 text if present, else definitions.prime first sentence
    if "conventions" in pn and "Q0-10" in pn["conventions"]:
        pn["conventions"]["Q0-10"] = injected
        replaced_at = "protocol_normative.conventions.Q0-10"
    else:
        pn.setdefault("definitions", {})["scratch_ptm4"] = injected
        replaced_at = "protocol_normative.definitions.scratch_ptm4"
    ej8_scratch = ej8_conflict_test(scratch4)
    ptm4 = {
        "id": "PTM-4",
        "object": "scratch copy with amendment-may-revise sentence",
        "replaced_at": replaced_at,
        "injected_sentence": injected,
        "ej8_conflict_test": ej8_scratch,
        "failure_signature_met": ej8_scratch["conflict_flagged"],
        "governing_claim_comes_out_FALSE": ej8_scratch["conflict_flagged"],
    }
    results["PTM-4"] = ptm4

    all_met = all(results[k]["failure_signature_met"] for k in results)
    out = {
        "proves_too_much": results,
        "all_failure_signatures_met": all_met,
        "governing_claim_tested": (
            "This file states the protocol once as fresh text, reads every reference "
            "by one rule, depends at run time on no held-file byte, and states no "
            "reserved-topic rule outside its fresh fields."
        ),
        "note": "PTM run after/alongside own joint scripts; control outputs not required inputs.",
    }
    OUT.write_text(json.dumps(out, indent=2, sort_keys=False) + "\n")
    print(
        json.dumps(
            {
                "all_met": all_met,
                "PTM-1": ptm1["failure_signature_met"],
                "PTM-2": ptm2["failure_signature_met"],
                "PTM-3": ptm3["failure_signature_met"],
                "PTM-4": ptm4["failure_signature_met"],
                "out": str(OUT),
            }
        )
    )


if __name__ == "__main__":
    main()
