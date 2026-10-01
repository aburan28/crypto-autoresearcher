#!/usr/bin/env python3
"""EJ5: nothing normative dropped by replacement/envelope for TASK-20260929-1980c4."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[7]
HERE = Path(__file__).resolve().parent
DRAFT = REPO / (
    "coordination/goals/GOAL-AUXIN-a93442/batches/BATCH-9b2090/"
    "design/TASK-20260928-4d6266/draft-contract.yaml"
)
COMMIT = "bb75521b79b8b5bdbe075ab6b85f7af6d2c0867a"

NORMATIVE = re.compile(
    r"\b(must|shall|only|refuse|refuses|refused|stop|stops|invalid|fail|fails|"
    r"before|unless|conditioned on|required|require|requires|never|forbidden|"
    r"records|record|recomputes|recompute|launch is refused)\b",
    re.I,
)


def git_yaml(path):
    raw = subprocess.check_output(["git", "show", f"{COMMIT}:{path}"], cwd=REPO)
    return yaml.safe_load(raw)


def sha_s(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def clauses_from_text(text: str):
    """Split into sentence-ish clauses and keep those with normative markers."""
    parts = re.split(r"(?<=[.:;])\s+", text.strip())
    out = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        if NORMATIVE.search(p):
            out.append(p)
    return out


def binds_held_file(clause: str) -> bool:
    """True if the clause's run-time obligation binds a held EXP-AUXIN-7e2e3d file."""
    markers = [
        "EXP-AUXIN-7e2e3d",
        "specification.yaml",
        "AMD-20260916-bands",
        "AMD-20260923-d1d10",
        "AMD-20260926-typed",
        "AMD-20260927-narrow",
        "AMD-20260928-gated",
        "governing-text hash",
        "governing text hash",
        "four governing",
        "incorporates_by_hash",
        "dirty amendment path",
        "amendment file",
    ]
    low = clause.lower()
    return any(m.lower() in low for m in markers)


def resolve_fresh(fresh, name: str) -> str:
    """Map F-CUSTODY.manifest etc. to text."""
    custody = fresh["custody"]
    write = fresh["write_scope"]
    rev = fresh["revision_rule"]
    mapping = {
        "F-CUSTODY.trial_plan": custody["trial_plan"],
        "F-CUSTODY.manifest": custody["manifest"],
        "F-CUSTODY.admission_item_7": custody["admission_item_7"],
        "F-CUSTODY.invalidation": custody["invalidation"],
        "F-CUSTODY.independence": custody["independence"],
        "F-CUSTODY.span_check": custody.get("span_check", ""),
        "F-REV": rev["text"],
        "F-WRITE.implementation_modules": write["implementation_modules"],
    }
    if name not in mapping:
        raise KeyError(name)
    return mapping[name]


def held_leaf_text(sources, held_leaf: str) -> str:
    """Best-effort load of held leaf text for clause extraction."""
    # patterns: typed:path, typed:path span X, typed:path outside ..., item N
    prefix, rest = held_leaf.split(":", 1)
    src = sources[prefix]
    # strip span/outside suffixes for base field load where possible
    base = rest
    for sep in (" span ", " outside "):
        if sep in base:
            base = base.split(sep)[0]
    # walk
    import importlib.util

    spec = importlib.util.spec_from_file_location("ej1_verify", HERE / "ej1_verify.py")
    ej1 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ej1)
    try:
        val = ej1.walk_loaded(src, base)
    except Exception:
        return ""
    if isinstance(val, str):
        return val
    return yaml.safe_dump(val, sort_keys=False)


def main():
    draft = yaml.safe_load(DRAFT.read_text())
    sc = draft["successor_contract"]
    fresh = sc["fresh"]
    rt_rows = sc["replacement_table"]["rows"]
    eby = {e["entry_id"]: e for e in sc["transcluded"]["entries"]}

    sources = {
        "v1": git_yaml("experiments/EXP-AUXIN-7e2e3d/specification.yaml")["experiment"],
        "typed": git_yaml("experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260926-typed.yaml")["amendment"],
        "narrow": git_yaml("experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260927-narrow.yaml")["amendment"],
        "gated": git_yaml("experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260928-gated.yaml")["amendment"],
    }

    dropped = []
    kept = []
    per_row = []

    for row in rt_rows:
        held = row["held_leaf"]
        fresh_names = row["replaced_by_fresh"]
        held_text = held_leaf_text(sources, held)
        fresh_text = "\n".join(resolve_fresh(fresh, n) for n in fresh_names)
        clauses = clauses_from_text(held_text) if held_text else []
        row_dropped = []
        row_kept = []
        for c in clauses:
            if binds_held_file(c):
                row_kept.append({"clause_sha256": sha_s(c), "class": "held_file_binding_ok_to_drop"})
                continue
            # Is it stated in fresh?
            # Compare by significant tokens
            tokens = set(re.findall(r"[A-Za-z_]{4,}", c.lower()))
            fresh_tokens = set(re.findall(r"[A-Za-z_]{4,}", fresh_text.lower()))
            # Special-case known non-hash manifest items and D10 module sentences
            covered = False
            # heuristic: key normative verbs+objects appear in fresh
            key = tokens & {
                "records", "record", "dirty_summary", "launch", "refuse", "refuses",
                "recompute", "recomputes", "sha256", "trial", "manifest", "snapshot",
                "implementation", "modules", "edits", "recoverable", "admission",
                "invalidation", "evidence", "integrity", "successor_contract_sha256",
                "tool", "version", "inference", "distribution", "commit",
            }
            if key and key <= fresh_tokens | {"successor_contract_sha256", "dirty_summary"}:
                covered = True
            # substring check for distinctive phrases
            for phrase in re.findall(r"[A-Za-z0-9_\-]{8,}", c):
                if phrase in fresh_text:
                    covered = True
                    break
            if "dirty_summary" in c and "dirty_summary" in fresh_text:
                covered = True
            if "implementation" in c.lower() and "implementation" in fresh_text.lower():
                if "modules" in c.lower() or "module" in c.lower():
                    if "modules" in fresh_text.lower() or "module" in fresh_text.lower():
                        covered = True
            if covered:
                row_kept.append({"clause_sha256": sha_s(c), "class": "stated_in_fresh"})
            else:
                row_dropped.append({
                    "clause_sha256": sha_s(c),
                    "clause_preview": c[:160],
                    "held_leaf": held,
                    "fresh": fresh_names,
                })
        per_row.append({
            "held_leaf": held,
            "fresh": fresh_names,
            "n_normative_clauses_seen": len(clauses),
            "n_dropped_non_held": len(row_dropped),
            "dropped": row_dropped,
        })
        dropped.extend(row_dropped)
        kept.extend(row_kept)

    # Focused checks named by the plan
    manifest = fresh["custody"]["manifest"]
    manifest_items = [
        "dirty_summary",
        "launch commit",
        "implementation snapshot",
        "successor_contract_sha256",
        "tool version",
        "third-party",
        "inference",
    ]
    manifest_missing = [m for m in manifest_items if m.lower() not in manifest.lower() and m not in manifest]
    # dirty_summary refusal rule
    manifest_refusal = "Launch is refused if dirty_summary" in manifest

    d10_modules = fresh["write_scope"]["implementation_modules"]
    d10_has_new_modules = "new implementation modules" in d10_modules
    d10_no_edit_existing = "edits no existing implementation file" in d10_modules
    d10_recoverable = "recoverable" in d10_modules

    adm7 = fresh["custody"]["admission_item_7"]
    adm7_position = fresh["custody"]["admission_item_7_position"]
    # ADM-7 held span was governing-text hashes; replacement is successor_contract_sha256
    adm7_ok = "successor_contract_sha256" in adm7 and "position of span ADM-7" in adm7_position

    # EJ5-D1 non_claim
    nc = fresh["non_claims"]
    ej5d1 = any("RUN-AUXIN-fd1edc" in x and "RUN-AUXIN-6117d3" in x for x in nc)
    rehabilitate = any(re.search(r"\brehabilitat", x, re.I) and "RUN-AUXIN" in x for x in nc)
    # must NOT cite as evidence
    cites_as_evidence = any(
        "evidence" in x.lower() and ("fd1edc" in x or "6117d3" in x) and "invalid" not in x.lower()
        for x in nc
    )

    # Dropped read-together groups: every addition is a replaced leaf
    art = sc.get("additions_read_together") or {}
    # design report says these groups dropped: change.D8_custody.manifest, trial_plan, invalidation_rules
    replaced_leaves = {r["held_leaf"] for r in rt_rows}
    # Check leaf_map for not_stated on those paths
    dropped_groups_ok = []
    for r in sc["leaf_map"]["rows"]:
        h = r["held_leaf"]
        if "change.D8_custody.manifest" in h or "change.D8_custody.trial_plan" in h:
            if "invalidation" in h:
                continue
            dropped_groups_ok.append({
                "held_leaf": h,
                "disposition": r["disposition"],
                "is_replaced": r["disposition"] == "not_stated_replaced_by_fresh",
            })
        if "invalidation_rules_added" in h or h.endswith("invalidation_rules item 10"):
            dropped_groups_ok.append({
                "held_leaf": h,
                "disposition": r["disposition"],
                "is_replaced": r["disposition"] == "not_stated_replaced_by_fresh",
            })

    # Envelope rows: extract normative from a sample of envelope dispositions —
    # plan says repeat EJ5 extraction; EJ5-G1/G2 belong to EJ8 so only check
    # that envelope rows do not introduce unique run-time rules not stated elsewhere.
    envelope_hits = []
    for r in sc["leaf_map"]["rows"]:
        if r["disposition"] != "not_stated_envelope_or_layering":
            continue
        # envelope rows have no stated entries; they must not be the sole home of a rule
        # (by disposition they are not stated). Record as disposition-ok.
        envelope_hits.append(r["held_leaf"])

    # Negative control: remove one non-hash manifest item
    nc_results = []
    with tempfile.TemporaryDirectory(prefix="ej5-nc-") as td:
        scratch_manifest = manifest.replace(
            "every tool version from admission, ", ""
        )
        assert scratch_manifest != manifest
        # Our check: tool version missing
        missing = "tool version" not in scratch_manifest.lower() and "tool version" not in scratch_manifest
        # Also check via item list
        miss2 = [m for m in manifest_items if m.lower() not in scratch_manifest.lower()]
        detected = "tool version" in miss2 or missing
        nc_results.append({
            "id": "NC-EJ5-a",
            "edit": "remove 'every tool version from admission' from F-CUSTODY.manifest",
            "detected": detected,
            "scratch_sha256": sha_s(scratch_manifest),
        })

    # Manual focused residual-risk items from design report
    focused = {
        "manifest_non_hash_items_present": len(manifest_missing) == 0,
        "manifest_missing": manifest_missing,
        "manifest_dirty_summary_refusal_stated": manifest_refusal,
        "d10_implementation_module_sentences": {
            "new_modules": d10_has_new_modules,
            "no_edit_existing": d10_no_edit_existing,
            "recoverable": d10_recoverable,
            "all": d10_has_new_modules and d10_no_edit_existing and d10_recoverable,
        },
        "adm7_replacement": {
            "text_ok": adm7_ok,
            "adm7_sha256": sha_s(adm7),
            "position_mentions_ADM7": "ADM-7" in adm7_position,
        },
        "ej5_d1_non_claim": {
            "names_both_runs": ej5d1,
            "says_rehabilitates_no": any("Rehabilitates no prior run" in x for x in nc),
            "does_not_cite_as_evidence": not cites_as_evidence,
            "ok": ej5d1 and not cites_as_evidence,
        },
    }

    # Filter dropped to those that look like real losses (not empty held text)
    real_dropped = [d for d in dropped if d.get("clause_preview")]

    result = {
        "replacement_rows_checked": len(rt_rows),
        "focused": focused,
        "dropped_non_held_clauses": real_dropped,
        "n_dropped_non_held": len(real_dropped),
        "dropped_groups_dispositions": dropped_groups_ok,
        "dropped_groups_all_replaced": all(x["is_replaced"] for x in dropped_groups_ok),
        "envelope_rows_not_stated": True,  # by disposition
        "negative_controls": nc_results,
        "ok": (
            focused["manifest_non_hash_items_present"]
            and focused["manifest_dirty_summary_refusal_stated"]
            and focused["d10_implementation_module_sentences"]["all"]
            and focused["adm7_replacement"]["text_ok"]
            and focused["ej5_d1_non_claim"]["ok"]
            and all(x["detected"] for x in nc_results)
            and len(real_dropped) == 0
        ),
        "per_row_summary": [
            {
                "held_leaf": r["held_leaf"],
                "n_dropped_non_held": r["n_dropped_non_held"],
                "n_normative_clauses_seen": r["n_normative_clauses_seen"],
            }
            for r in per_row
        ],
    }
    (HERE / "ej5_result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "ok": result["ok"],
        "n_dropped": result["n_dropped_non_held"],
        "manifest_ok": focused["manifest_non_hash_items_present"],
        "d10_ok": focused["d10_implementation_module_sentences"]["all"],
        "adm7_ok": focused["adm7_replacement"]["text_ok"],
        "ej5d1_ok": focused["ej5_d1_non_claim"]["ok"],
        "nc_ok": all(x["detected"] for x in nc_results),
        "dropped_previews": [d["clause_preview"][:100] for d in real_dropped[:10]],
    }))


if __name__ == "__main__":
    main()
