#!/usr/bin/env python3
"""EJ6 independent held-file mutation + overlay AMD invalidation attack.

Own design: do NOT import or exec held_file_mutation.py.
Mutate copies of held EXP-AUXIN-7e2e3d files in a scratch tree and confirm
draft-contract.yaml bytes/sha256 are unchanged. Probe overlay invalidation
phrasing for affirmative fire rules vs neutralizing NOT-invalidation.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import tempfile
from pathlib import Path

import yaml

ROOT = Path.cwd()
DRAFT = ROOT / (
    "coordination/goals/GOAL-AUXIN-a93442/batches/BATCH-ad00c6/"
    "design/TASK-20260929-d519f6/draft-contract.yaml"
)
HELD = [
    ROOT / "experiments/EXP-AUXIN-7e2e3d/specification.yaml",
    ROOT / "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260926-typed.yaml",
    ROOT / "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260927-narrow.yaml",
    ROOT / "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260928-gated.yaml",
    ROOT / "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260916-bands.yaml",
    ROOT / "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260923-d1d10.yaml",
]
OUT = Path(__file__).resolve().parent / "ej6_held_file_mutation.result.json"


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def extract_overlay_invalidation(data: dict) -> list[dict]:
    findings = []
    overlays = data["successor_contract"]["protocol_normative"].get("corrective_overlays", [])
    for i, ov in enumerate(overlays):
        custody = ov.get("custody") or {}
        ira = custody.get("invalidation_rules_added")
        if not ira:
            continue
        rules = ira.get("rules") or []
        for j, rule in enumerate(rules):
            text = rule if isinstance(rule, str) else str(rule)
            # Affirmative fire: says an AMD edit / incorporates.sha256 mismatch IS invalidation
            # without NOT / are NOT / forbid / deleted.
            lower = text.lower()
            is_negating = bool(
                re.search(
                    r"\b(?:are not|is not|not an? invalidation|forbid|deleted|no .* is an invalidation)\b",
                    lower,
                )
            )
            mentions_amd_or_hash = bool(
                re.search(r"amd-|incorporates\.sha256|incorporates_by_hash|held amd", lower)
            )
            affirmative_fire = mentions_amd_or_hash and not is_negating
            findings.append(
                {
                    "overlay_index": i,
                    "rule_index": j,
                    "text": text,
                    "mentions_amd_or_hash": mentions_amd_or_hash,
                    "is_negating_language": is_negating,
                    "affirmative_fire_rule": affirmative_fire,
                    "deleted_prior_rules_note": ira.get("deleted_prior_rules_note"),
                }
            )
    return findings


def scan_dependence_language(full: str) -> dict:
    # Look for run-time READ FROM / content-digest binding of held paths as affirmative rules
    patterns = {
        "read_from_held": r"READ(?:s)?\s+FROM[^\n]{0,80}EXP-AUXIN-7e2e3d",
        "content_digest_bind": r"bound by content-digest[^\n]{0,80}EXP-AUXIN-7e2e3d|"
        r"content-digest[^\n]{0,80}held",
        "opens_held_at_runtime": r"opens? (?:those )?paths[^\n]{0,40}EXP-AUXIN-7e2e3d|"
        r"open, hash, compare[^\n]{0,40}EXP-AUXIN-7e2e3d",
        "independence_clause": r"F-CUSTODY\.independence|No gate, stop, launch refusal",
    }
    hits = {}
    for name, pat in patterns.items():
        hits[name] = [m.group(0) for m in re.finditer(pat, full, re.IGNORECASE)]
    return hits


def main() -> None:
    draft_before = sha256_file(DRAFT)
    data = yaml.safe_load(DRAFT.read_bytes())

    # --- Own mutation design: copy held files to temp, mutate copies, re-hash draft ---
    # The draft does not import held bytes; mutating originals would dirty the tree.
    # Protocol: (1) record draft sha256; (2) mutate scratch copies of held files;
    # (3) confirm draft path bytes unchanged; (4) confirm draft text makes no
    # run-time gate depend on held sha256 values that would change.
    mutation_log = []
    with tempfile.TemporaryDirectory(prefix="ej6-held-mut-") as td:
        td_path = Path(td)
        for hp in HELD:
            assert hp.is_file(), str(hp)
            dest = td_path / hp.name
            shutil.copy2(hp, dest)
            before = sha256_file(dest)
            # mutate: append a comment marker that changes sha256
            with dest.open("ab") as f:
                f.write(b"\n# EJ6-RT-MUTATION-MARKER\n")
            after = sha256_file(dest)
            mutation_log.append(
                {
                    "held_path": str(hp.relative_to(ROOT)),
                    "scratch_before": before,
                    "scratch_after": after,
                    "scratch_changed": before != after,
                }
            )
        draft_after_scratch_mut = sha256_file(DRAFT)

    # Also verify: no held-file sha256 appears as a run-time binding constant that
    # would make draft outcomes depend on held bytes. Search for each held file's
    # current sha256 inside the draft.
    held_digest_mentions = []
    draft_text = DRAFT.read_text()
    for hp in HELD:
        dig = sha256_file(hp)
        count = draft_text.count(dig)
        held_digest_mentions.append(
            {
                "held_path": str(hp.relative_to(ROOT)),
                "held_sha256": dig,
                "occurrences_in_draft": count,
            }
        )

    # F-CUSTODY independence + invalidation_after_approval
    custody = data["successor_contract"]["fresh"]["custody"]
    independence = custody["independence"]
    inv_after = custody["invalidation_after_approval"]
    independence_forbids_held = (
        "EXP-AUXIN-7e2e3d" in independence
        and "depends" in independence.lower()
        and ("no gate" in independence.lower() or "No gate" in independence)
    )
    inv_neutralizes_amd = (
        "NOT" in inv_after
        or "not an invalidation" in inv_after.lower()
        or "no edit of any AMD" in inv_after.lower()
    )

    overlay_findings = extract_overlay_invalidation(data)
    affirmative_overlay = [f for f in overlay_findings if f["affirmative_fire_rule"]]

    # execution_admission.explicitly_not_required
    adm = data["successor_contract"]["protocol_normative"].get("execution_admission", {})
    enr = adm.get("explicitly_not_required") or []

    # Named breaks
    ej6_b1 = {
        "id": "EJ6-B1",
        "draft_claims_preserved": True,
        "evidence": {
            "draft_sha256_stable_under_scratch_held_mutation": draft_before
            == draft_after_scratch_mut,
            "all_scratch_mutations_changed_bytes": all(m["scratch_changed"] for m in mutation_log),
            "held_digest_occurrences_in_draft": held_digest_mentions,
            "any_held_digest_embedded": any(
                m["occurrences_in_draft"] > 0 for m in held_digest_mentions
            ),
            "independence_clause_present": independence_forbids_held,
            "explicitly_not_required_mentions_held": any(
                "7e2e3d" in str(x) or "AMD-edit" in str(x) or "incorporates.sha256" in str(x)
                for x in enr
            ),
        },
    }
    # EJ6-B1 holds if draft unchanged, no affirmative held-byte fire, independence present
    ej6_b1["fixed_as_named"] = (
        ej6_b1["evidence"]["draft_sha256_stable_under_scratch_held_mutation"]
        and not ej6_b1["evidence"]["any_held_digest_embedded"]
        and independence_forbids_held
        and not affirmative_overlay
    )

    ej6_overlay = {
        "id": "EJ6-OVERLAY-AMD-INVALIDATION",
        "draft_claims_preserved": True,
        "overlay_rules": overlay_findings,
        "affirmative_fire_count": len(affirmative_overlay),
        "invalidation_after_approval_neutralizes": inv_neutralizes_amd,
        "inv_after_text": inv_after,
        "fixed_as_named": (len(affirmative_overlay) == 0) and inv_neutralizes_amd,
    }

    dep_scan = scan_dependence_language(draft_text)

    breaks = []
    if not ej6_b1["fixed_as_named"]:
        breaks.append({"id": "EJ6-B1", "detail": ej6_b1})
    if not ej6_overlay["fixed_as_named"]:
        breaks.append({"id": "EJ6-OVERLAY-AMD-INVALIDATION", "detail": ej6_overlay})
    if draft_before != draft_after_scratch_mut:
        breaks.append({"id": "EJ6-DRAFT-BYTES-CHANGED", "before": draft_before, "after": draft_after_scratch_mut})

    verdict = "breaks" if breaks else "holds"
    result = {
        "joint": "EJ6",
        "draft_sha256": draft_before,
        "mutation_design": (
            "Scratch-copy mutation of all six held files; draft path never written; "
            "assert draft sha256 invariant; assert no held digest embedded; "
            "assert overlay AMD/hash rules are NOT-invalidation."
        ),
        "did_not_reuse_control_script": True,
        "mutation_log": mutation_log,
        "draft_sha256_after_scratch_mutation": draft_after_scratch_mut,
        "named_breaks": {"EJ6-B1": ej6_b1, "EJ6-OVERLAY-AMD-INVALIDATION": ej6_overlay},
        "dependence_language_scan": dep_scan,
        "execution_admission_explicitly_not_required": enr,
        "breaks": breaks,
        "verdict": verdict,
        "note": "Own mutation; control outputs not read before this file was written.",
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=False) + "\n")
    print(json.dumps({"verdict": verdict, "out": str(OUT), "affirmative_overlay": len(affirmative_overlay)}))


if __name__ == "__main__":
    main()
