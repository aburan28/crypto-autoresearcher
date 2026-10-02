#!/usr/bin/env python3
"""Control 3 of the TASK-20260928-4d6266 design report (control_targets:
fresh-against-transcluded conflict scan).

Scans every STATED transcluded entry of draft EXP-AUXIN-bafa2e (entries a
leaf_map row with disposition stated assigns) for the five reserved topics of
F-PREC (revision, approval, custody, governing text, write scope), with a token
list broader than the producer's design-time scan, then applies the Coordinator
classifications below. Each classification is bound to the entry's span_sha256
so a reading cannot silently drift to other text. Every scanned candidate gets a
class: an explicit one below, or NO_CONFLICT_TOPIC_TOKEN_ONLY by default (listed).

Classes:
  CONFLICT            the entry states a rule on a reserved topic that differs from
                      the fresh field and no F-READ rule neutralises it
  SCOPE_AMBIGUITY     conflict or not depends on an undefined topic word
  TENSION_NO_EFFECT   differs on its face; no run-time decision found that it changes
  RESOLVED_BY_F_READ  an F-READ rule turns the apparent conflict into agreement
Writes one JSON result to stdout.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

import yaml

DRAFT = Path("coordination/goals/GOAL-AUXIN-a93442/batches/BATCH-9b2090/design/"
             "TASK-20260928-4d6266/draft-contract.yaml")
DRAFT_SHA256 = "667cf21e1a0680eaa5eb862164835a0074c109f2254f5ac6f52428327ba27bbd"
FRESH_FIELDS = ["revision_rule", "approval", "custody", "write_scope", "precedence",
                "reading_of_references", "transclusion_convention"]
TOPICS = {
    "revision": r"amend|supersed|revis|rewrit|new (?:EXP )?id|successor|layer|in place|immutable|never edit|edited",
    "approval": r"approv|authoriz|scientific_execution|coordinator decision|sign[- ]off",
    "custody": r"sha256|hash|dirty|git status|snapshot|path_sha256|evidence-integrity|launch commit|custody|manifest",
    "governing": r"governing|governs|precedence|incorporat|combined text|this file|this amendment|this text|"
                 r"this protocol|this specification|this contract|held text",
    "write_scope": r"write[_ ]scope|writes? (?:nothing|only|no)|under experiments/|implementation/|run directory",
}

READINGS = {
    "T-0463": ("CONFLICT", "approval",
               "Stated v1 launch_gate.note asserts that scientific_execution_authorized is true because the census "
               "protocol is complete. It is quoted older text, not a field of this draft, and R7 makes the bare "
               "path provenance only, but the sentence still states an authorization on the approval topic that "
               "F-APPROVAL denies. F-PREC reserved_topics lets F-APPROVAL decide and calls such a finding a draft "
               "defect. Carried from the design report as EJ3-M4, unchanged."),
    "T-0388": ("CONFLICT", "custody",
               "'dirty amendment path' is rewritten by no F-READ rule; a dirty held amendment file at launch makes "
               "the package invalid_measurement, where F-CUSTODY.manifest says such a line refuses nothing and "
               "F-CUSTODY.independence says no validity rule depends on held git status. Same finding as the "
               "held-file mutation control."),
    "T-0457": ("CONFLICT", "custody",
               "Admission requires a verified snapshot archive naming H-AUXIN-66e6fd and EXP-AUXIN-7e2e3d (R6 "
               "neutralises only the DEC and TASK ids). That archive's verification reads held bytes, which "
               "F-CUSTODY.independence excludes. The design report leaves it to review as EJ3-M1."),
    "T-0636": ("CONFLICT", "custody+governing",
               "States that every cut-off 'governs from its own clause, in the layer governing_text_table names' "
               "and that pre-registration 'rests on the sha256 binding of all four governing layers before any "
               "value is seen (change.D8_custody and custody_additions below)'. R7 maps governing_text_table to "
               "leaf_map, whose rows still carry held_governing_layer, so a layer is said to govern, contrary to "
               "F-PREC and R6 ('no layer governs'). 'Governing layers' is not a phrase R3 lists. The four-layer "
               "hash binding it gives as the pre-registration basis does not exist in this contract "
               "(F-CUSTODY binds one hash). The producer's reading that no stated entry states custody of a held "
               "file does not hold for this entry."),
    "T-0162": ("CONFLICT", "governing",
               "Q0-11 outside span: 'Where a referenced record and this file's text could differ, this file's text "
               "governs'. Under R1 'this file' is the entries copied from AMD-20260926-typed.yaml, so the entry "
               "sets a precedence of typed-sourced entries over other referenced records, including other held "
               "files whose spans are stated here. F-PREC reserves precedence and governing text to the fresh "
               "fields."),
    "T-0124": ("CONFLICT", "revision",
               "'A later amendment may pre-register a rule on the basis of this arm'. F-REV: no amendment layers "
               "this contract; any change is a new successor contract under a new EXP id. No F-READ rule rewrites "
               "'a later amendment'."),
    "T-0627": ("TENSION_NO_EFFECT", "revision",
               "'Revisit when any later amendment edits C-PLANT-PL' presupposes amendments that edit fields, which "
               "F-REV rules out. It is a design statement read by no gate."),
    "T-0541": ("TENSION_NO_EFFECT", "approval+revision",
               "Stage 2 is gated on 'separate design ... plus a superseding Coordinator decision', a route F-REV and "
               "F-APPROVAL do not name; R6 makes the decision reference provenance only, which would leave the gate "
               "without a referent. Stated T-0528 ('Do not enter a protocol-supply stage under this contract') "
               "keeps stage 2 closed either way."),
    "T-0019": ("SCOPE_AMBIGUITY", "custody",
               "Staged-source sha256 binding. F-CUSTODY.scope says custody binds this contract file and the spans "
               "'and nothing else', and F-PREC reserved_topics makes the fresh fields the only custody rules. If "
               "'custody' there means all custody, this and every implementation, source and artifact custody "
               "entry decides nothing; if it means governing-text custody, there is no conflict. The draft does "
               "not define the word."),
    "T-0097": ("SCOPE_AMBIGUITY", "custody", "As T-0019 (retrieved pinned-revision sources)."),
    "T-0557": ("SCOPE_AMBIGUITY", "custody", "As T-0019 (retrieval digest check)."),
    "T-0144": ("SCOPE_AMBIGUITY", "custody", "As T-0019 (implementation snapshot and launch comparison; paths under R5)."),
    "T-0146": ("SCOPE_AMBIGUITY", "custody", "As T-0019 (post-run snapshot; paths under R5)."),
    "T-0362": ("SCOPE_AMBIGUITY", "custody", "As T-0019 (implementation snapshot stop)."),
    "T-0364": ("SCOPE_AMBIGUITY", "custody", "As T-0019 (staged-source digest stop)."),
    "T-0387": ("SCOPE_AMBIGUITY", "custody", "As T-0019 (hashed artifact rewritten)."),
    "T-0412": ("SCOPE_AMBIGUITY", "custody", "As T-0019 (implementation/typed/ in the snapshot's path_sha256; R5)."),
    "T-0373": ("RESOLVED_BY_F_READ", "custody", "R3: governing-text hash is successor_contract_sha256."),
    "T-0395": ("RESOLVED_BY_F_READ", "custody", "R3: governing-text hashes is successor_contract_sha256."),
    "T-0535": ("RESOLVED_BY_F_READ", "custody", "R2: 'this specification' is this contract."),
    "T-0461": ("RESOLVED_BY_F_READ", "custody", "R2: 'this frozen contract' is this contract."),
    "T-0430": ("RESOLVED_BY_F_READ", "revision", "R2: 'the amendment returns to review' is this contract returning "
               "to review; any change it needs is a new successor under F-REV."),
    "T-0432": ("RESOLVED_BY_F_READ", "revision", "As T-0430."),
    "T-0566": ("RESOLVED_BY_F_READ", "governing", "R6: '(governing layer v1)' is provenance; R8: the read is of "
               "stated entries."),
    "T-0638": ("RESOLVED_BY_F_READ", "governing", "'specification.yaml tail_checks item 1 governs (layer v1)': R7 "
               "resolves the field through leaf_map and R6 makes the layer name provenance; 'stay incorporated by "
               "hash' is read under R7 as stated by its row."),
    "T-0610": ("RESOLVED_BY_F_READ", "governing", "R7: 'stays incorporated' means stated by its leaf_map row."),
    "T-0140": ("RESOLVED_BY_F_READ", "write_scope", "R7: change.D10_additivity resolves to F-REV and "
               "F-WRITE.implementation_modules (row not_stated_replaced_by_fresh); R5 remaps the paths."),
    "T-0139": ("RESOLVED_BY_F_READ", "write_scope", "R5: the new module path is under experiments/EXP-AUXIN-bafa2e/."),
    "T-0143": ("RESOLVED_BY_F_READ", "write_scope", "R5 remaps every EXP-AUXIN-7e2e3d implementation path."),
    "T-0180": ("RESOLVED_BY_F_READ", "write_scope", "R5."),
    "T-0458": ("RESOLVED_BY_F_READ", "write_scope", "R5."),
    "T-0602": ("RESOLVED_BY_F_READ", "write_scope", "R5."),
    "T-0637": ("RESOLVED_BY_F_READ", "governing", "Provenance of index completeness claims; 'governing text' under "
               "R3 is this contract, which claims no complete index."),
    "T-0639": ("RESOLVED_BY_F_READ", "governing", "Errata adds_to references read under R7 through leaf_map and "
               "additions_read_together; see the F-READ control for the unlisted R7 tokens in this entry."),
}


def main() -> int:
    raw = DRAFT.read_bytes()
    if hashlib.sha256(raw).hexdigest() != DRAFT_SHA256:
        print(json.dumps({"label": "NOT_RUN", "reason": "draft sha256 mismatch"}))
        return 2
    doc = yaml.safe_load(raw.decode("utf-8"))["successor_contract"]
    by_id = {e["entry_id"]: e for e in doc["transcluded"]["entries"]}
    stated = sorted({eid for r in doc["leaf_map"]["rows"] if r["disposition"] == "stated"
                     for eid in r.get("entries", [])})
    candidates = {}
    for eid in stated:
        tops = [k for k, p in TOPICS.items() if re.search(p, by_id[eid]["text"], re.IGNORECASE)]
        if tops:
            candidates[eid] = tops

    missing_fresh = [f for f in FRESH_FIELDS if f not in doc["fresh"]]
    classified, defaults, stale = [], [], []
    for eid, tops in candidates.items():
        if eid in READINGS:
            cls, topic, reading = READINGS[eid]
            classified.append({"entry": eid, "states_leaf": by_id[eid]["states_leaf"],
                               "span_sha256": by_id[eid]["span_sha256"], "scan_topics": tops,
                               "class": cls, "reserved_topic": topic, "reading": reading})
        else:
            defaults.append({"entry": eid, "scan_topics": tops, "class": "NO_CONFLICT_TOPIC_TOKEN_ONLY"})
    for eid in READINGS:
        if eid not in candidates:
            stale.append(eid)

    conflicts = [c["entry"] for c in classified if c["class"] == "CONFLICT"]
    label = "NOT_RUN" if (missing_fresh or stale) else ("CONFLICT_FOUND" if conflicts else "NO_CONFLICT_FOUND")
    result = {
        "control": "fresh-against-transcluded conflict scan",
        "design_report": ("coordination/goals/GOAL-AUXIN-a93442/batches/BATCH-9b2090/design/"
                          "TASK-20260928-4d6266/design-report.yaml control_targets.controls[2]"),
        "object": {"path": str(DRAFT), "sha256": DRAFT_SHA256},
        "label": label,
        "conflicts": conflicts,
        "by_class": {k: [c["entry"] for c in classified if c["class"] == k]
                     for k in ("CONFLICT", "SCOPE_AMBIGUITY", "TENSION_NO_EFFECT", "RESOLVED_BY_F_READ")},
        "fresh_fields_read": FRESH_FIELDS,
        "fresh_fields_missing": missing_fresh,
        "readings_without_scan_hit": stale,
        "topic_patterns": TOPICS,
        "classified": classified,
        "default_classified": defaults,
        "limits": ("The token scan is mechanical; the classes are Coordinator readings of each entry under F-PREC "
                   "and F-READ, made before any reviewer exists and bound to span_sha256. An entry the scan did not "
                   "flag was not read for conflict. The producer's design-time candidate list was not used as input."),
    }
    json.dump(result, sys.stdout, indent=1, sort_keys=True, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
