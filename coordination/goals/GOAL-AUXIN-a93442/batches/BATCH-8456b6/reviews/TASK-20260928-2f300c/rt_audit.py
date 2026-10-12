#!/usr/bin/env python3
"""Red-team computations for TASK-20260928-2f300c (REVIEW-AUXIN-20260928-8456b6).

Joints EJ3, EJ5, EJ6 and proves-too-much objects PTM-1 to PTM-4 on draft
EXP-AUXIN-edd104 at snapshot 7170c2974b. Review computations only: no
experiment run, no RUN-* id. Reads the producer's four design files, the six
held sources at bb75521b79 and the review plan; writes only under this task's
reviews/ directory. Run from the repository root.

Output text carries no census value, minimising divisor, control integer,
witness integer or depth: entries are cited by id and leaf name, and no held
text containing a numeral is quoted.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

OUT = Path("coordination/goals/GOAL-AUXIN-a93442/batches/BATCH-8456b6/reviews/TASK-20260928-2f300c")
DESIGN = "coordination/goals/GOAL-AUXIN-a93442/batches/BATCH-8456b6/design/TASK-20260928-fa9275"
SNAP = "7170c2974bc5d0988c8255c889ff91c4c7645245"
SRC_COMMIT = "bb75521b79b8b5bdbe075ab6b85f7af6d2c0867a"
PLAN = "coordination/review/auxin-20260928-8456b6/review-plan.yaml"
HELD = {
    "v1": "experiments/EXP-AUXIN-7e2e3d/specification.yaml",
    "typed": "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260926-typed.yaml",
    "narrow": "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260927-narrow.yaml",
    "gated": "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260928-gated.yaml",
    "bands": "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260916-bands.yaml",
    "d1d10": "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260923-d1d10.yaml",
}
SRC_PREFIX = {Path(p).name: k for k, p in HELD.items()}


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def git_show(commit: str, path: str) -> bytes:
    return subprocess.run(["git", "show", f"{commit}:{path}"], check=True, capture_output=True).stdout


# --------------------------------------------------------------------------- custody
plan = yaml.safe_load(open(PLAN))["review_plan"]
custody = {"plan_sha256": sha(Path(PLAN).read_bytes()), "producer_files": [], "held_files": []}
for f in plan["object_under_review"]["files"]:
    wt, snap = sha(Path(f["path"]).read_bytes()), sha(git_show(SNAP, f["path"]))
    custody["producer_files"].append({"path": f["path"], "plan": f["sha256"], "working_tree": wt,
                                      "at_snapshot": snap, "match": wt == snap == f["sha256"]})
for path, want in plan["object_under_review"]["held_sources_at_source_commit"]["files"].items():
    got = sha(git_show(SRC_COMMIT, path))
    custody["held_files"].append({"path": path, "plan": want, "at_source_commit": got,
                                  "working_tree": sha(Path(path).read_bytes()), "match": got == want})
if not all(x["match"] for x in custody["producer_files"] + custody["held_files"]):
    print("custody mismatch; refusing to rely on inputs", file=sys.stderr)
    json.dump({"custody": custody}, sys.stderr, indent=1)
    sys.exit(2)

DRAFT_PATH = f"{DESIGN}/draft-contract.yaml"
DRAFT_RAW = Path(DRAFT_PATH).read_text(encoding="utf-8")
draft = yaml.safe_load(DRAFT_RAW)["successor_contract"]
held = {k: yaml.safe_load(git_show(SRC_COMMIT, p)) for k, p in HELD.items() if k in ("v1", "typed", "narrow", "gated")}
V1, TY, NA, GA = held["v1"]["experiment"], held["typed"]["amendment"], held["narrow"]["amendment"], held["gated"]["amendment"]


def entries_of(sc):
    return {e["entry_id"]: e for e in sc["transcluded"]["entries"]}


E = entries_of(draft)
ROWS = draft["leaf_map"]["rows"]
ROW_BY_LEAF = {r["held_leaf"]: r for r in ROWS}
FRESH = draft["fresh"]
src_of = lambda e: SRC_PREFIX[Path(e["source_path"]).name]


# --------------------------------------------------------------------------- EJ3
TOKEN_CLASSES = {
    "this_file": r"\bthis file\b",
    "this_amendment": r"\bthis amendment\b",
    "this_text": r"\bthis text\b",
    "this_protocol": r"\bthis protocol\b",
    "the_combined_text": r"\bthe combined (?:governing )?text\b",
    "this_frozen_contract_or_other_this_X": r"\bthis (?:frozen )?contract\b",
    "amendment_path": r"\bamendment\.[A-Za-z_]",
    "experiment_path": r"\bexperiment\.[A-Za-z_]",
    "held_file_name": r"\b(?:specification|AMD-2026\d{4}-[a-z0-9]+)\.yaml\b",
    "record_id": r"\b(?:DEC|EXP|RUN|TASK|AMD|H|EV|KN|REVIEW|BATCH|GOAL|CORR|IDEA|VAL|RT)-[A-Z0-9][A-Za-z0-9\-]*\b",
    "layer_name": r"\b(?:typed-by-hash|narrow-by-hash|refused-typed-by-hash)\b|\blayer v1\b|\bgoverning layer\b",
    "predecessor_path": r"experiments/EXP-AUXIN-7e2e3d/",
    "positional": r"\b(?:above|below|the following|this field|the item above)\b",
    "layering_machinery_name": r"governing_text_table|\bprecedence\b|path_additions|reading_of_self_references|incorporat",
}
ej3_census = {}
for cls, pat in TOKEN_CLASSES.items():
    by_src, ids = {}, []
    for eid, e in E.items():
        n = len(re.findall(pat, e["text"]))
        if n:
            by_src[src_of(e)] = by_src.get(src_of(e), 0) + n
            ids.append(eid)
    ej3_census[cls] = {"occurrences_by_source": by_src, "entry_ids": ids}

fread = {r["id"]: r["text"] for r in FRESH["reading_of_references"]["rules"]}
R1_R2_phrases = re.findall(r'"([^"]+)"', fread["R1"] + " " + fread["R2"])


def row(leaf):
    r = ROW_BY_LEAF.get(leaf)
    return None if r is None else r["disposition"]


ej3_checks = {
    "fread_phrases_in_R1_R2": R1_R2_phrases,
    "this_frozen_contract_named_by_any_fread_rule": any("contract" in p for p in R1_R2_phrases),
    "T-0471_contains_this_frozen_contract": "this frozen contract" in E["T-0471"]["text"],
    "T-0471_leaf": E["T-0471"]["states_leaf"],
    "T-0467_leaf": E["T-0467"]["states_leaf"],
    "T-0467_names_v1_hypothesis_not_successor_hypothesis": ("H-AUXIN-66e6fd" in E["T-0467"]["text"]
                                                             and "H-AUXIN-6db354" not in E["T-0467"]["text"]),
    "successor_hypothesis": FRESH["hypothesis_id"],
    "v1_hypothesis": V1["hypothesis_id"],
    "R3_has_datum_exception_for_envelope_rows": "a sha256 or byte count written there is a datum" in fread["R3"],
    "R3_has_incorporates_provenance_only_clause": bool(re.search(r"to incorporates or\s+incorporates_by_hash, provenance only", fread["R3"])),
    "row_narrow:incorporates.sha256": row("narrow:incorporates.sha256"),
    "row_gated:incorporates_by_hash.sha256": row("gated:incorporates_by_hash.sha256"),
    "T-0617_references_incorporates.sha256": "incorporates.sha256" in E["T-0617"]["text"],
    "T-0658_references_incorporates_by_hash.sha256": "incorporates_by_hash.sha256" in E["T-0658"]["text"],
    "held_hash_check_rows_dropped": {k: row(k) for k in ("narrow:incorporates.hash_check", "gated:incorporates_by_hash.hash_check")},
    "R6_applies_to_all_spans_incl_v1": "A reference to a decision" in fread["R6"] and "Inside spans copied from" not in fread["R6"],
    "held_gated_reading_scopes_decision_provenance_to_narrow_and_gated_text":
        "References made inside the text of AMD-20260927-narrow.yaml or of this file are read as written" in GA["reading_of_self_references"],
    "T-0475_v1_decision_reference": E["T-0475"]["states_leaf"],
    "T-0473_asserts_v1_execution_flag_true": "scientific_execution_authorized is true" in E["T-0473"]["text"],
    "row_v1:scientific_execution_authorized": row("v1:scientific_execution_authorized"),
    "amendment_path_refs_resolve_via_leaf_map": {},
}
for eid in ej3_census["amendment_path"]["entry_ids"]:
    for m in re.finditer(r"\bamendment\.([A-Za-z_][\w]*)", E[eid]["text"]):
        top = m.group(1)
        hits = [r["held_leaf"] for r in ROWS if r["held_leaf"].startswith(f"typed:{top}")]
        ej3_checks["amendment_path_refs_resolve_via_leaf_map"][f"{eid}:amendment.{top}"] = {
            "rows": len(hits), "all_stated_or_grouped": all(ROW_BY_LEAF[h]["disposition"] == "stated" for h in hits)}

# positional references: in the successor, are entries of one source kept in source order?
order_ok = {}
for s in ("v1", "typed", "narrow", "gated"):
    ids = [eid for eid, e in E.items() if src_of(e) == s and e["anchor"]["kind"] == "loaded_value"
           and "char_range" not in e["anchor"]]
    order_ok[s] = len(ids)
ej3_checks["positional_refs_same_source_neighbours_T-0132_T-0133_T-0134"] = [
    E[i]["states_leaf"] for i in ("T-0132", "T-0133", "T-0134")]
ej3_checks["positional_T-0569_expected_sha_entries_precede"] = all(
    list(E).index(i) < list(E).index("T-0569") for i in ("T-0562", "T-0563", "T-0564", "T-0565", "T-0566"))

# --------------------------------------------------------------------------- EJ5
NORMATIVE = r"\b(must|shall|only|refuse[sd]?|stop|invalid|fail|before|unless|conditioned on|never|no run|not approved|authoriz\w*|may not|is not)\b"


def resolve(doc, path):
    """Resolve a governing_text_table-style leaf path against a loaded document."""
    m = re.match(r"^(.*?)(?: item (\d+))?$", path)
    base, item = m.group(1), m.group(2)
    cur = doc
    for tok in re.findall(r"[^.\[\]]+(?:\[[^\]]+\])?", base):
        mm = re.match(r"^([^\[]+)(?:\[([^\]]+)\])?$", tok)
        key, sel = mm.group(1).strip(), mm.group(2)
        if not isinstance(cur, dict) or key not in cur:
            return None
        cur = cur[key]
        if sel is not None:
            if isinstance(cur, list):
                cur = next((x for x in cur if isinstance(x, dict) and sel in [str(v) for v in x.values()]), None)
            elif isinstance(cur, dict):
                cur = cur.get(sel)
            if cur is None:
                return None
    if item is not None:
        if not isinstance(cur, list) or int(item) > len(cur):
            return None
        cur = cur[int(item) - 1]
    return cur


HELD_DOC = {"v1": V1, "typed": TY, "narrow": NA, "gated": GA}
env_rows = [r for r in ROWS if r["disposition"] == "not_stated_envelope_or_layering"]
env_scan = []
for r in env_rows:
    pre, path = r["held_leaf"].split(":", 1)
    if pre not in HELD_DOC:
        env_scan.append({"leaf": r["held_leaf"], "resolved": False, "normative_hits": None})
        continue
    p = re.sub(r" (?:outside )?spans? [A-Z0-9\-, ]+$", "", path)
    val = resolve(HELD_DOC[pre], p)
    txt = val if isinstance(val, str) else (yaml.safe_dump(val, width=10000) if val is not None else None)
    hits = sorted(set(w.lower() for w in re.findall(NORMATIVE, txt or "", re.I)))
    env_scan.append({"leaf": r["held_leaf"], "held_layer": r["held_governing_layer"], "resolved": val is not None,
                     "normative_hits": hits})

# Curated disposition of every envelope group whose held text carries a normative clause
# (the rows resolved and scanned above); each names the successor text that states it.
ej5_disposition = [
    {"group": "typed/narrow/gated approval.* (approved_if_and_only_if, until_approved, immutability, how_approval_is_recorded)",
     "clause": "approval tie to the file's own decision; no run, implementation dispatch or executor card relies on the text until approved; any revision is a new file",
     "successor": "F-APPROVAL (approved_if_and_only_if, transcluded_conditions, how_approval_is_recorded) and fresh authorization; F-REV",
     "status": "stated_elsewhere", "caveat": "F-REV is contradicted by transcluded T-0158 (see EJ6-B2)"},
    {"group": "narrow incorporates.hash_check; gated incorporates_by_hash.hash_check",
     "clause": "before any use the reader or executor hashes the incorporated files; mismatch is an evidence-integrity stop before Stage A0 completes",
     "successor": "F-CUSTODY span_sha256 recomputation from source blobs at source_commit before Stage A0 completes",
     "status": "replaced", "caveat": "the invalidation rules that read the dropped hash fields (T-0617, T-0658) are still stated; see EJ3-B1"},
    {"group": "narrow incorporates.status_of_that_file; gated incorporates_by_hash.status_of_the_incorporated_files (OB-1)",
     "clause": "incorporated fields govern only through the incorporating file and only if it is approved",
     "successor": "F-PREC (held records govern nothing) and F-APPROVAL", "status": "no_counterpart_needed", "caveat": None},
    {"group": "narrow/gated what_is_incorporated, span_hash_convention, envelope_not_incorporated, narrow_envelope_not_incorporated",
     "clause": "which held fields govern and how spans are cut; a span is never cut from a value an earlier layer replaced",
     "successor": "leaf_map dispositions and transcluded.anchor_convention", "status": "no_counterpart_needed",
     "caveat": "correctness of leaf_map against these is EJ2/EJ7, not assessed here"},
    {"group": "narrow/gated precedence, gated reading_of_self_references, governing_text_table, path_additions",
     "clause": "layer order, single governing layer per leaf, union reading of additions, reading of self-references",
     "successor": "F-PREC, F-READ, leaf_map, additions_read_together", "status": "replaced",
     "caveat": "F-READ departs from held reading for v1 decision references and leaves 'this frozen contract' unresolved (EJ3)"},
    {"group": "typed/narrow/gated authorization",
     "clause": "one census package (maximum_runs 1), stages A0 P C N D R T only, no Cheon, no auxiliary power, no supply audit, no stage2 join, first dispatch precondition admission gate, runs fd1edc and 6117d3 not rehabilitated",
     "successor": "T-0363 and T-0533 (maximum_runs), typed stages T-0202 to T-0208, T-0550 (stage2 authorized false), T-0386 (stopping rule 16), F-PRE with T-0201",
     "status": "stated_elsewhere_except_one",
     "caveat": "non-rehabilitation of RUN-AUXIN-fd1edc and RUN-AUXIN-6117d3 is stated by no entry and no fresh field; inert at run time"},
    {"group": "typed not_superseded (7 items, held layer typed-by-hash, i.e. governing in held)",
     "clause": "claim_ceiling, what_this_is_not, invalidation_rules, budget, stage2 authorized false, write_scope stand",
     "successor": "v1 rows stated (T-0475 to T-0482, T-0539 to T-0545, T-0529 to T-0535, T-0550); write_scope replaced by F-WRITE",
     "status": "stated_elsewhere", "caveat": "v1 write_scope (predecessor implementation and runs) is replaced, not stated; deliberate for a new EXP id"},
    {"group": "typed does_not_rewrite (7 items, held layer typed-by-hash); narrow/gated does_not_rewrite",
     "clause": "spec, bands, d1d10, existing implementation files, existing runs, hypothesis and goal records are not rewritten",
     "successor": "F-WRITE (exclusive paths; implementation/typed/ new files only) and T-0158", "status": "stated_elsewhere", "caveat": None},
    {"group": "typed non_claims (4 items, held layer typed-by-hash); narrow/gated non_claims ('held non_claims stay incorporated')",
     "clause": "no Cheon, no auxiliary power, no supply audit; claim_ceiling stands; criterion 4 and pause condition 3 not discharged",
     "successor": "T-0386, T-0476, T-0477, T-0480 to T-0482, T-0453; fresh non_claims", "status": "stated_elsewhere", "caveat": None},
    {"group": "typed does_not_rehabilitate (2 items, held layer typed-by-hash)",
     "clause": "RUN-AUXIN-fd1edc stays invalid as evidence; RUN-AUXIN-6117d3 stays void",
     "successor": None, "status": "dropped", "caveat": "no run-time decision of the protocol reads a prior run; permits nothing at run time"},
    {"group": "v1 scientific_execution_authorized, execution_authorized, evidence_eligible, scientific_execution_scope, frozen, status",
     "clause": "v1's own state flags and execution scope",
     "successor": "F-APPROVAL, fresh authorization; scope limits via T-0386, T-0476, T-0477, T-0550",
     "status": "no_counterpart_needed", "caveat": "T-0473 transcludes a sentence asserting scientific_execution_authorized is true; only R3 makes it provenance"},
    {"group": "narrow span_rules[*], gated gated_span_rules[*], typed/narrow/gated supersedes_fields",
     "clause": "where replacement text sits and which held text it retires",
     "successor": "replacement spans stated at position; superseded rows' replaced_by_entries", "status": "no_counterpart_needed",
     "caveat": "composition correctness is EJ1/EJ2"},
]

# read-together groups against held path_additions
PA = GA["path_additions"]
groups = draft["additions_read_together"]["groups"]
layer_to_prefix = {"narrow-by-hash": "narrow", "gated": "gated", "typed-by-hash": "typed"}
ej5_groups = []
for pa, g in zip(PA, groups):
    held_adds = []
    for a in pa["additions"]:
        lay, p = a.split(":", 1)
        held_adds.append(f"{layer_to_prefix[lay]}:{p}")
    add_leaves = [E[x]["states_leaf"] for x in g["addition_entries"]]
    broader = sorted({l for l in add_leaves for h in held_adds if h.startswith(l) and h != l})
    outside = sorted({l for l in add_leaves if not any(l.startswith(h) or h.startswith(l) for h in held_adds)})
    covered = all(any(l.startswith(h) or h.startswith(l) for l in add_leaves) for h in held_adds)
    ej5_groups.append({"path": pa["path"], "path_equal": pa["path"] == g["path"], "read_as": pa["read_as"],
                       "held_additions": held_adds, "every_held_addition_covered": covered,
                       "entries_broader_than_held_addition": broader, "entries_outside_held_additions": outside})
ej5_group_summary = {
    "count_held": len(PA), "count_successor": len(groups),
    "paths_equal_in_order": all(x["path_equal"] for x in ej5_groups),
    "all_held_additions_covered": all(x["every_held_addition_covered"] for x in ej5_groups),
    "groups_with_broader_entries": [x["path"] for x in ej5_groups if x["entries_broader_than_held_addition"]],
    "held_precedence_says_no_union_member_overrides": "no union member overrides another" in GA["precedence"],
    "fprec_says_none_overrides": "none overrides another" in FRESH["precedence"]["text"],
}


def completeness(sc):
    """EJ5 completeness argument: every id a leaf_map row or group names exists, and every entry is assigned."""
    ents = entries_of(sc)
    dangling = []
    for r in sc["leaf_map"]["rows"]:
        for k in ("entries", "replaced_by_entries"):
            for x in r.get(k) or []:
                if x not in ents:
                    dangling.append({"row": r["held_leaf"], "field": k, "entry_id": x})
    for g in sc["additions_read_together"]["groups"]:
        for k in ("held_entries", "addition_entries"):
            for x in g.get(k) or []:
                if x not in ents:
                    dangling.append({"group": g["path"], "field": k, "entry_id": x})
    assigned = {x for r in sc["leaf_map"]["rows"] for x in (r.get("entries") or [])}
    unassigned = sorted(set(ents) - assigned)
    return {"dangling_ids": dangling, "entries_not_assigned_by_any_stated_row": unassigned,
            "complete": not dangling}


ej5_completeness_draft = completeness(draft)

# --------------------------------------------------------------------------- EJ6
HELD_NAMES = ["specification.yaml", "AMD-20260916-bands.yaml", "AMD-20260923-d1d10.yaml",
              "AMD-20260926-typed.yaml", "AMD-20260927-narrow.yaml", "AMD-20260928-gated.yaml"]
CUSTODY_VERB = r"sha256|byte difference|edit of|dirty_summary|recomput|mismatch|hash"
dependence = []
for eid, e in E.items():
    t = e["text"]
    if re.search(CUSTODY_VERB, t, re.I):
        named = [n for n in HELD_NAMES if n in t]
        if named:
            dependence.append({"entry_id": eid, "leaf": e["states_leaf"], "held_files_named": named})
fcust = FRESH["custody"]["text"]
ej6_checks = {
    "held_file_custody_clauses": dependence,
    "F-CUSTODY_keeps_transcluded_hashes": "Every hash the" in fcust and "kept unchanged" in fcust,
    "F-CUSTODY_span_check_reads_blobs_at_source_commit": "from its source blob at source_commit" in fcust,
    "F-PREC_held_records_are_sources_nothing_more": "sources that" in FRESH["precedence"]["text"] and "nothing more" in FRESH["precedence"]["text"],
    "F-PREC_only_three_fresh_fields_may_change_what_an_entry_decides":
        "No other fresh field changes what a transcluded entry decides" in FRESH["precedence"]["text"],
    "T-0158_leaf": E["T-0158"]["states_leaf"], "T-0158_row": row(E["T-0158"]["states_leaf"]),
    "T-0158_says_later_change_is_new_amendment_file": "Any later change is a new amendment file" in E["T-0158"]["text"],
    "T-0158_self_reference": re.findall(r"\bThis amendment\b", E["T-0158"]["text"]),
    "R2_maps_this_amendment_to_this_contract": '"This amendment"' in fread["R2"] and "mean this contract" in fread["R2"],
    "F-REV_forbids_amendments": "No amendment layers this contract" in FRESH["revision_rule"]["text"],
    "stopping_rule_12_text_is_governing_text_hash": "Governing-text hash mismatch" in E["T-0382"]["text"],
    "F-WRITE_paths": FRESH["write_scope"]["paths"],
    "predecessor_implementation_typed_dir_exists_now": Path("experiments/EXP-AUXIN-7e2e3d/implementation/typed").exists(),
    "T-0144_trial_plan_path_under_predecessor_typed": "experiments/EXP-AUXIN-7e2e3d/implementation/typed/trial-plan.json" in E["T-0144"]["text"],
    "F-H_reads_fc_mapping_and_states_correction_condition":
        "falsification-condition mapping" in FRESH["hypothesis_binding"]["text"] and "DEC-20260926-96f970" in FRESH["hypothesis_binding"]["text"],
}
dec = yaml.safe_load(open("ledger/decisions/DEC-20260927-f680f7.yaml"))["coordinator_decision"]["dispatch_preconditions_carried"]
ej6_checks["F-PRE_cited_sha256_recomputes"] = (sha(dec.encode()) == "c3be35ae13929b45fc10dbf65f2b28cdb10a1e2580b6d7d6b57b1cf6fcd1e553")
d96 = yaml.safe_load(open("ledger/decisions/DEC-20260926-96f970.yaml"))["coordinator_decision"]["next_actions"][1]["action"]
ej6_checks["DEC-20260926-96f970_item2_concerns_interpretation_limits"] = "interpretation_limits" in d96
IDX = {"T-0121", "T-0627", "T-0628", "T-0629", "T-0649", "T-0650", "T-0651", "T-0652", "T-0122", "T-0123"}
HIDDEN = (r"(?:every|each|all|any) (?:numeric )?(?:cut-offs?|thresholds?|decision constants?|constants?)|listed (?:cut-offs|constants|thresholds)"
          r"|the (?:index|inventory)\b|(?:cut-offs?|thresholds?|constants?) (?:above|below|listed)")
ej6_checks["F-INDEX_hidden_reader_scan"] = [
    {"entry_id": eid, "leaf": e["states_leaf"], "match": m.group(0)}
    for eid, e in E.items() if eid not in IDX for m in re.finditer(HIDDEN, e["text"], re.I)]
ej6_checks["F-INDEX_parent_path_readers"] = [
    {"entry_id": eid, "leaf": e["states_leaf"]} for eid, e in E.items()
    if re.search(r"change\.D4_calibration(?!\.threshold_inventory)", e["text"])]


def layer_form(obj: dict, own_text_keys=("precedence",)) -> dict:
    """The not-a-layer criterion applied under EJ6 (and to PTM-1).

    L1 incorporation with governing force; L2 supersession machinery; L3 precedence over
    more than one governing file. An object is a governing layer on held text iff L1 or L2
    or L3. L4 (run-time dependence on another file's bytes) is reported beside it: it is the
    CD-6 independence clause, not part of the layer form.
    """
    flat = json.dumps(obj, ensure_ascii=False)
    incorporation_blocks = [k for k in obj if re.match(r"incorporat", k)]
    l1 = any("govern" in json.dumps(obj[k]) and "sha256" in json.dumps(obj[k]) for k in incorporation_blocks)
    l2 = any(isinstance(obj.get(k), list) and obj.get(k) for k in ("supersedes_fields", "span_rules", "gated_span_rules"))
    prec = obj.get("precedence")
    prec_text = prec if isinstance(prec, str) else (prec or {}).get("text", "")
    layers_named = set(re.findall(r"\b(v1|typed-by-hash|narrow-by-hash|gated|refused-typed-by-hash|corrective)\b", prec_text))
    l3 = len(layers_named) >= 2
    return {"L1_incorporation_with_governing_force": l1, "incorporation_blocks": incorporation_blocks,
            "L2_supersession_machinery": bool(l2), "L3_multi_file_precedence": l3,
            "layers_named_in_precedence": sorted(layers_named), "is_layer": bool(l1 or l2 or l3)}


draft_form_obj = dict(FRESH)
draft_form_obj["precedence"] = FRESH["precedence"]["text"]
ej6_layer_form_draft = layer_form(draft_form_obj)
ej6_layer_form_draft["L4_runtime_dependence_on_held_file_bytes"] = bool(dependence) and ej6_checks["F-CUSTODY_keeps_transcluded_hashes"]

# --------------------------------------------------------------------------- PTM
ptm_dir = OUT / "ptm"
ptm_dir.mkdir(exist_ok=True)
ptm = {}

# PTM-1: gated itself, read as a candidate successor.
g_form = layer_form(GA)
g_form["L4_runtime_dependence_on_held_file_bytes"] = any(n in json.dumps(GA.get("custody_additions")) for n in HELD_NAMES[3:5])
ptm["PTM-1"] = {"object": HELD["gated"] + " at " + SRC_COMMIT, "object_sha256": sha(git_show(SRC_COMMIT, HELD["gated"])),
                "criterion_result": g_form, "required": "classified as a layer",
                "behaves_per_failure_signature": g_form["is_layer"]}

# PTM-2: four-file concatenation under distinct top-level keys.
concat_text = "".join(
    f"{key}:\n" + "".join("  " + ln + "\n" for ln in git_show(SRC_COMMIT, HELD[key]).decode("utf-8").splitlines())
    for key in ("v1", "typed", "narrow", "gated"))
p2 = ptm_dir / "PTM-2-four-file-concatenation.yaml"
p2.write_text(concat_text, encoding="utf-8")
concat = yaml.safe_load(p2.read_text(encoding="utf-8"))


def stated_once(obj_kind: str, obj) -> dict:
    """The 'stated once and equivalently' test applied under EJ3 and EJ5.

    S1: no held leaf that the held table records as superseded still has its superseded
        text stated in the object as governing text beside its replacement.
    S2: at most one precedence rule, and no incorporation block, so no layer order is
        needed to decide which text governs.
    """
    sup = [r for r in ROWS if r["disposition"] == "not_stated_superseded_in_held_table"]
    dup = []
    if obj_kind == "concat":
        for r in sup:
            pre, path = r["held_leaf"].split(":", 1)
            v = resolve(obj[pre]["experiment" if pre == "v1" else "amendment"], path)
            if v is not None:
                dup.append(r["held_leaf"])
        precedence_blocks = sum(1 for k in ("typed", "narrow", "gated") if "precedence" in obj[k]["amendment"])
        incorporation_blocks = sum(1 for k in ("typed", "narrow", "gated") for kk in obj[k]["amendment"] if kk.startswith("incorporat"))
    else:
        texts = {e["text"] for e in obj["transcluded"]["entries"]}
        for r in sup:
            pre, path = r["held_leaf"].split(":", 1)
            v = resolve(HELD_DOC[pre], path)
            if isinstance(v, str) and len(v) > 40 and any(v in t for t in texts):
                dup.append(r["held_leaf"])
        precedence_blocks = 1
        incorporation_blocks = sum(1 for k in obj["fresh"] if k.startswith("incorporat"))
    return {"S1_superseded_leaves_still_stated": len(dup), "S1_examples": dup[:5],
            "S2_precedence_rules": precedence_blocks, "S2_incorporation_blocks": incorporation_blocks,
            "accepted": not dup and precedence_blocks <= 1 and incorporation_blocks == 0}


ptm["PTM-2"] = {"object": str(p2), "object_sha256": sha(p2.read_bytes()), "test_result": stated_once("concat", concat),
                "required": "rejected"}
ptm["PTM-2"]["behaves_per_failure_signature"] = not ptm["PTM-2"]["test_result"]["accepted"]
stated_once_draft = stated_once("draft", draft)

# PTM-3: F-N4 bound comparison replaced by exact equality, all else unchanged.
OLD = ("it misses its expected closed-form expression by more than the gate-2 tolerance or the floor invariant fails, "
       "so gate 2 fails on that state; or, for the upper bound of BND-1, CONSISTENCY fails, so gate 3 fails. "
       "Exact equality of a real-valued bound is never tested.")
NEW = ("it is not exactly equal to its expected closed-form expression. Exact equality of each real-valued bound is tested.")
assert DRAFT_RAW.count(OLD) == 1
p3 = ptm_dir / "PTM-3-draft-n4-exact-equality.yaml"
p3.write_text(DRAFT_RAW.replace(OLD, NEW), encoding="utf-8")


def n4_stop_argument(sc) -> dict:
    """The argument the draft and design report state: the N4 condition and stopping rule 10 coincide.

    Step A: categorical fields -- N4 lists them; gate 1 compares exactly those.
    Step B: bound fields -- F-N4 fixes 'other than the fixed value' for a bound; gates 2 and 3
            fail exactly then. Reading of Step B is taken from the F-N4 text of the object.
    Evaluated over a symbolic case grid (no numeric tolerance or control value is used):
    delta in {zero, within_tolerance_nonzero, beyond_tolerance}, floor invariant, CONSISTENCY.
    """
    ents = entries_of(sc)
    fn4 = sc["fresh"]["n4_bound_comparison"]["text"]
    gate1 = ents["T-0295"]["text"] + ents["T-0294"]["text"] + ents["T-0296"]["text"]
    gate1_fields = [f for f in ("status", "witness set", "witness", "bin_at_least", "bin", "boundary_flag", "bound")
                    if re.search(rf"\b{re.escape(f)}\b", gate1)]
    n4_fields = [f for f in ("status", "witness set", "witness", "bound", "bin_at_least", "bin", "boundary_flag")
                 if re.search(rf"\b{re.escape(f)}\b", ents["T-0438"]["text"])]
    gate2_is_tolerance = "within" in ents["T-0297"]["text"] and "floor invariant" in ents["T-0297"]["text"]
    stop10 = "Any C-BOUND gate fails" in ents["T-0380"]["text"]
    bound_by_tolerance = "gate-2 tolerance" in fn4 and "never tested" in fn4
    bound_by_exact = "not exactly equal" in fn4 or "Exact equality of each real-valued bound is tested" in fn4
    disagreements = []
    for state in ("BND-1", "BND-2", "BND-3"):
        for path in ("A", "B"):
            cases = [("categorical:" + f, {"cat": f}) for f in gate1_fields if f != "bound"]
            cases += [("bound_delta:" + d, {"delta": d}) for d in ("zero", "within_tolerance_nonzero", "beyond_tolerance")]
            cases += [("floor_invariant_fails", {"floor": True})]
            if state == "BND-1":
                cases += [("consistency_fails", {"cons": True})]
            for name, c in cases:
                g1 = "cat" in c and c["cat"] in gate1_fields
                g2 = gate2_is_tolerance and (c.get("delta") == "beyond_tolerance" or c.get("floor", False))
                g3 = state == "BND-1" and c.get("cons", False)
                stop = stop10 and (g1 or g2 or g3)
                if "cat" in c:
                    n4 = c["cat"] in n4_fields
                elif "delta" in c:
                    if bound_by_tolerance:
                        n4 = c["delta"] == "beyond_tolerance"
                    elif bound_by_exact:
                        n4 = c["delta"] != "zero"
                    else:
                        n4 = None
                else:
                    n4 = True if bound_by_tolerance else (False if bound_by_exact else None)
                if n4 is None or n4 != stop:
                    disagreements.append({"state": state, "path": path, "case": name, "n4_condition": n4,
                                          "stopping_rule_10": stop})
    return {"gate1_fields": gate1_fields, "n4_fields": n4_fields,
            "n4_fields_not_compared_by_gate1": sorted(set(n4_fields) - set(gate1_fields) - {"bound"}),
            "fn4_bound_reading": "tolerance" if bound_by_tolerance else ("exact" if bound_by_exact else "undetermined"),
            "disagreements": disagreements, "argument_goes_through": not disagreements}


ptm3_draft = n4_stop_argument(draft)
ptm3_variant = n4_stop_argument(yaml.safe_load(p3.read_text(encoding="utf-8"))["successor_contract"])
ptm["PTM-3"] = {"object": str(p3), "object_sha256": sha(p3.read_bytes()), "argument_on_unmodified_draft": ptm3_draft,
                "argument_on_variant": ptm3_variant, "required": "argument fails on the variant",
                "behaves_per_failure_signature": ptm3_draft["argument_goes_through"] and not ptm3_variant["argument_goes_through"]}

# PTM-4: one transcluded entry removed; its leaf_map row still names it.
REMOVED = "T-0380"
lines = DRAFT_RAW.splitlines(keepends=True)
start = next(i for i, ln in enumerate(lines) if ln.strip() == f"- entry_id: {REMOVED}")
indent = len(lines[start]) - len(lines[start].lstrip())
end = next(i for i in range(start + 1, len(lines))
           if (len(lines[i]) - len(lines[i].lstrip())) <= indent and lines[i].strip())
p4 = ptm_dir / "PTM-4-draft-entry-removed.yaml"
p4.write_text("".join(lines[:start] + lines[end:]), encoding="utf-8")
p4_obj = yaml.safe_load(p4.read_text(encoding="utf-8"))["successor_contract"]
ptm4 = completeness(p4_obj)
ptm["PTM-4"] = {"object": str(p4), "object_sha256": sha(p4.read_bytes()), "removed_entry": REMOVED,
                "removed_entry_leaf": E[REMOVED]["states_leaf"],
                "row_still_names_it": any(REMOVED in (r.get("entries") or []) for r in p4_obj["leaf_map"]["rows"]),
                "completeness_on_variant": ptm4, "completeness_on_draft": ej5_completeness_draft["complete"],
                "required": "missing entry detected",
                "behaves_per_failure_signature": ej5_completeness_draft["complete"] and not ptm4["complete"]}

# --------------------------------------------------------------------------- write
result = {
    "task_id": "TASK-20260928-2f300c", "review_plan": "REVIEW-AUXIN-20260928-8456b6",
    "experiment_id": "EXP-AUXIN-edd104", "snapshot_commit": SNAP, "source_commit": SRC_COMMIT,
    "runs_launched": 0, "custody": custody,
    "EJ3": {"token_census": ej3_census, "checks": ej3_checks},
    "EJ5": {"envelope_rows_scanned": len(env_scan),
            "envelope_rows_resolved": sum(1 for x in env_scan if x["resolved"]),
            "envelope_rows_with_normative_words": [x["leaf"] for x in env_scan if x["normative_hits"]],
            "envelope_rows_unresolved": [x["leaf"] for x in env_scan if not x["resolved"]],
            "disposition_of_normative_envelope_groups": ej5_disposition,
            "read_together_groups": ej5_groups, "read_together_summary": ej5_group_summary,
            "completeness_on_draft": ej5_completeness_draft, "stated_once_on_draft": stated_once_draft},
    "EJ6": {"checks": ej6_checks, "layer_form_draft": ej6_layer_form_draft},
    "PTM": ptm,
}
(OUT / "computations.json").write_text(json.dumps(result, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps({k: v.get("behaves_per_failure_signature") for k, v in ptm.items()}))
print("draft layer form:", {k: ej6_layer_form_draft[k] for k in ("is_layer", "L4_runtime_dependence_on_held_file_bytes")})
print("stated_once draft:", stated_once_draft)
print("completeness draft:", ej5_completeness_draft["complete"], "unassigned:", len(ej5_completeness_draft["entries_not_assigned_by_any_stated_row"]))
print("groups broader:", ej5_group_summary["groups_with_broader_entries"])
print("PTM-3 draft:", ptm3_draft["argument_goes_through"], ptm3_draft["n4_fields_not_compared_by_gate1"], "variant disagreements:", len(ptm3_variant["disagreements"]))
