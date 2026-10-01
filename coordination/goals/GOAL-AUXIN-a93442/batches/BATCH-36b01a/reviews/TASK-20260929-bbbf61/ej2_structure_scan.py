#!/usr/bin/env python3
"""EJ2: normative completeness of the fresh rewrite vs typed RS-B extract."""

from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[7]
WRITE = Path(__file__).resolve().parent
DESIGN = (
    ROOT
    / "coordination/goals/GOAL-AUXIN-a93442/batches/BATCH-36b01a/design/TASK-20260929-6d01d7"
)
TYPED = ROOT / "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260926-typed.yaml"
DRAFT = DESIGN / "draft-contract.yaml"
# Refused 92dccc draft — citation of what was refused only (plan EJ2 attack).
REFUSED_92 = (
    ROOT
    / "coordination/goals/GOAL-AUXIN-a93442/batches/BATCH-1907cf/design/TASK-20260929-ef0945/draft-contract.yaml"
)

TYPED_KEYS = [
    "definitions",
    "change",
    "conventions",
    "tools_and_admission",
    "stages",
    "controls",
    "controls_distinctness",
    "what_the_controls_exercise",
    "null_arm",
    "preregistered_prediction",
    "metrics",
    "budget",
    "stopping_rules",
    "invalidation_rules",
    "required_artifacts",
    "success_criterion",
    "falsification_criterion",
    "interpretation_limits",
    "proof_search_map",
]

CLAUSE_RE = re.compile(
    r"\b(must|shall|refuse[sd]?|required|stop(?:s|ping)?|void|forbidden|never)\b",
    re.I,
)
HELD_PATH_RE = re.compile(
    r"EXP-AUXIN-7e2e3d|specification\.yaml|AMD-2026092[678]|READ FROM|incorporated by hash",
    re.I,
)


def walk_strings(obj):
    if isinstance(obj, dict):
        for v in obj.values():
            yield from walk_strings(v)
    elif isinstance(obj, list):
        for x in obj:
            yield from walk_strings(x)
    elif isinstance(obj, str):
        yield obj


def extract_clauses(text: str) -> list[str]:
    out = []
    for sent in re.split(r"(?<=[.:;])\s+", text):
        s = sent.strip()
        if len(s) < 20:
            continue
        if CLAUSE_RE.search(s):
            out.append(s)
    return out


def control_ids(controls) -> set[str]:
    ids = set()
    if isinstance(controls, list):
        for c in controls:
            if isinstance(c, dict) and "id" in c:
                ids.add(c["id"])
            elif isinstance(c, dict):
                for v in c.values():
                    if isinstance(v, list):
                        for item in v:
                            if isinstance(item, dict) and "id" in item:
                                ids.add(item["id"])
    elif isinstance(controls, dict):
        for v in controls.values():
            if isinstance(v, list):
                for item in v:
                    if isinstance(item, dict) and "id" in item:
                        ids.add(item["id"])
            elif isinstance(v, dict) and "id" in v:
                ids.add(v["id"])
    return ids


def stage_ids(stages) -> set[str]:
    ids = set()
    if isinstance(stages, dict):
        for k, v in stages.items():
            if isinstance(v, dict) and "id" in v:
                ids.add(v["id"])
            else:
                ids.add(str(k))
    elif isinstance(stages, list):
        for s in stages:
            if isinstance(s, dict) and "id" in s:
                ids.add(s["id"])
    return ids


def outcome_ids(sc) -> set[str]:
    ids = set()
    if not isinstance(sc, dict):
        return ids
    outcomes = sc.get("outcomes") or {}
    if isinstance(outcomes, dict):
        ids.update(outcomes.keys())
    elif isinstance(outcomes, list):
        for o in outcomes:
            if isinstance(o, dict) and "id" in o:
                ids.add(o["id"])
            elif isinstance(o, str):
                ids.add(o)
    return ids


def jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 1.0
    return len(a & b) / len(a | b)


def normalize_item(s: str) -> str:
    s = re.sub(r"\s+", " ", s).strip().lower()
    s = HELD_PATH_RE.sub("<HELD>", s)
    s = re.sub(r"experiments/exp-auxin-369078/", "<EXP>/", s)
    s = re.sub(r"exp-auxin-369078", "<EXPID>", s)
    s = re.sub(r"experiments/exp-auxin-55c6c0/", "<EXP>/", s)
    s = re.sub(r"exp-auxin-55c6c0", "<EXPID>", s)
    return s


def substance_token_drops(typed_items, proto_items, label: str):
    """Flag typed list items whose distinctive non-held tokens fail to survive."""
    proto_blob = "\n".join(normalize_item(x) for x in proto_items if isinstance(x, str))
    drops = []
    for item in typed_items:
        if not isinstance(item, str):
            continue
        if HELD_PATH_RE.search(item) and not CLAUSE_RE.search(item):
            continue
        substance = normalize_item(item)
        tokens = [t for t in re.findall(r"[a-z0-9_-]{6,}", substance) if t != "held"]
        if len(tokens) < 3:
            continue
        hits = sum(1 for t in tokens if t in proto_blob)
        if hits < max(2, len(tokens) // 2) and not HELD_PATH_RE.search(item):
            drops.append(
                {
                    "inventory": label,
                    "clause_prefix": item[:180],
                    "token_hits": hits,
                    "token_count": len(tokens),
                }
            )
    return drops


def main() -> None:
    typed = yaml.safe_load(TYPED.read_text())
    ta = typed.get("amendment", typed)
    draft = yaml.safe_load(DRAFT.read_text())
    sc = draft["successor_contract"]
    pn = sc["protocol_normative"]
    fresh = sc["fresh"]

    typed_present = [k for k in TYPED_KEYS if k in pn]
    typed_missing = [k for k in TYPED_KEYS if k not in pn]

    t_ctrl = control_ids(ta.get("controls"))
    p_ctrl = control_ids(pn.get("controls"))
    t_stages = stage_ids(ta.get("stages"))
    p_stages = stage_ids(pn.get("stages"))
    t_out = outcome_ids(ta.get("success_criterion") or {})
    p_out = outcome_ids(pn.get("success_criterion") or {})

    typed_clauses = []
    for s in walk_strings({k: ta[k] for k in TYPED_KEYS if k in ta}):
        typed_clauses.extend(extract_clauses(s))
    proto_clauses = []
    for s in walk_strings(pn):
        proto_clauses.extend(extract_clauses(s))
    fresh_clauses = []
    for s in walk_strings(fresh):
        fresh_clauses.extend(extract_clauses(s))

    proto_blob = "\n".join(proto_clauses + fresh_clauses).lower()
    candidate_drops = []
    for c in typed_clauses:
        substance = normalize_item(c)
        if len(substance) < 40:
            continue
        tokens = [t for t in re.findall(r"[a-z0-9_-]{6,}", substance) if t != "held"]
        if len(tokens) < 3:
            continue
        hits = sum(1 for t in tokens if t in proto_blob)
        if hits < max(2, len(tokens) // 2):
            is_held_binder = bool(HELD_PATH_RE.search(c))
            if not is_held_binder:
                candidate_drops.append(
                    {
                        "clause_prefix": c[:180],
                        "token_hits": hits,
                        "token_count": len(tokens),
                        "held_binder": False,
                    }
                )

    def list_items(obj):
        if isinstance(obj, list):
            return [
                normalize_item(x) if isinstance(x, str) else normalize_item(str(x))
                for x in obj
            ]
        return []

    t_inv = set(list_items(ta.get("invalidation_rules")))
    p_inv = set(list_items(pn.get("invalidation_rules")))
    t_stop = set(list_items(ta.get("stopping_rules")))
    p_stop = set(list_items(pn.get("stopping_rules")))

    inv_drops = substance_token_drops(
        ta.get("invalidation_rules") or [],
        pn.get("invalidation_rules") or [],
        "invalidation_rules",
    )
    stop_drops = substance_token_drops(
        ta.get("stopping_rules") or [],
        pn.get("stopping_rules") or [],
        "stopping_rules",
    )
    req_drops = substance_token_drops(
        ta.get("required_artifacts") or [],
        pn.get("required_artifacts") or [],
        "required_artifacts",
    )

    held_pointers = []
    for s in walk_strings(pn):
        if HELD_PATH_RE.search(s):
            held_pointers.append({"prefix": s[:160], "kind": "protocol_normative"})
    for s in walk_strings(fresh):
        if HELD_PATH_RE.search(s):
            held_pointers.append({"prefix": s[:160], "kind": "fresh"})

    affirmative_dep = []
    AFFIRM_RE = re.compile(
        r"READ FROM specification\.yaml|"
        r"All experiment\.invalidation_rules of specification\.yaml stand|"
        r"\bstay incorporated by hash\b|"
        r"\bincorporated by hash\b",
        re.I,
    )
    for s in list(walk_strings(pn)) + list(walk_strings(fresh)):
        if AFFIRM_RE.search(s):
            affirmative_dep.append(s[:180])

    emptiness = {
        "transcluded_entries": len(sc.get("transcluded", {}).get("entries") or []),
        "leaf_map_rows": len(sc.get("leaf_map", {}).get("rows") or []),
        "additions_groups": len(sc.get("additions_read_together", {}).get("groups") or []),
        "design_strategy_zero_transclusion": True,
        "intentional_emptiness": True,
    }

    refused_note = {"path_exists": REFUSED_92.exists()}
    if REFUSED_92.exists():
        r92 = yaml.safe_load(REFUSED_92.read_text())
        rsc = r92.get("successor_contract") or r92
        refused_note["transcluded_entries"] = len(
            (rsc.get("transcluded") or {}).get("entries") or []
        )
        refused_note["leaf_map_rows"] = len((rsc.get("leaf_map") or {}).get("rows") or [])
        refused_note["citation_only"] = (
            "Compared only to show this draft's zero-transclusion differs from "
            "the refused draft's structure; not treated as defect findings of "
            "EXP-AUXIN-369078."
        )

    fresh_ids = {}
    for k, v in fresh.items():
        if isinstance(v, dict) and "id" in v:
            fresh_ids[k] = v["id"]

    structure = {
        "proto_keys": list(pn.keys()),
        "typed_keys_present": typed_present,
        "typed_keys_missing": typed_missing,
        "control_ids": {
            "typed": sorted(t_ctrl),
            "proto": sorted(p_ctrl),
            "missing_from_proto": sorted(t_ctrl - p_ctrl),
            "extra_in_proto": sorted(p_ctrl - t_ctrl),
        },
        "stage_ids": {
            "typed": sorted(t_stages),
            "proto": sorted(p_stages),
            "missing_from_proto": sorted(t_stages - p_stages),
        },
        "outcome_ids": {
            "typed": sorted(t_out),
            "proto": sorted(p_out),
            "missing_from_proto": sorted(t_out - p_out),
        },
        "fresh_field_ids": fresh_ids,
        "clause_counts": {
            "typed_scanned": len(typed_clauses),
            "proto": len(proto_clauses),
            "fresh": len(fresh_clauses),
            "candidate_drops": len(candidate_drops),
        },
        "candidate_drops": candidate_drops[:30],
        "invalidation_jaccard": jaccard(t_inv, p_inv),
        "stopping_jaccard": jaccard(t_stop, p_stop),
        "invalidation_counts": {"typed": len(t_inv), "proto": len(p_inv)},
        "stopping_counts": {"typed": len(t_stop), "proto": len(p_stop)},
        "substance_drops": {
            "invalidation": inv_drops,
            "stopping": stop_drops,
            "required_artifacts": req_drops,
        },
        "held_pointer_count": len(held_pointers),
        "held_pointers_sample": held_pointers[:12],
        "affirmative_held_dependence_phrases": affirmative_dep,
        "emptiness": emptiness,
        "refused_92dccc_citation": refused_note,
        "verdict_inputs": {
            "typed_keys_complete": len(typed_missing) == 0,
            "control_ids_complete": len(t_ctrl - p_ctrl) == 0,
            "stage_ids_complete": len(t_stages - p_stages) == 0,
            "outcome_ids_complete": len(t_out - p_out) == 0,
            "non_held_candidate_drops": len(candidate_drops),
            "invalidation_substance_drops": len(inv_drops),
            "stopping_substance_drops": len(stop_drops),
            "required_artifacts_drops": len(req_drops),
            "affirmative_held_dependence_phrases": len(affirmative_dep),
            "emptiness_intentional": emptiness["intentional_emptiness"],
        },
    }

    out = WRITE / "ej2_structure_scan.json"
    out.write_text(json.dumps(structure, indent=2, sort_keys=False) + "\n")
    print(json.dumps(structure["verdict_inputs"], indent=2))
    print("held_pointers", len(held_pointers), "candidate_drops", len(candidate_drops))
    print("wrote", out)


if __name__ == "__main__":
    main()
