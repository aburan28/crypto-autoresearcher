#!/usr/bin/env python3
"""Control 1 of the TASK-20260928-4d6266 design report (control_targets: F-READ coverage).

Independent scan of every transcluded entry of draft EXP-AUXIN-bafa2e. Written
without reading build_successor.py. Reads only the snapshotted draft-contract.yaml
(checked against its snapshot sha256) and writes one JSON result to stdout.

must_check (design report): every self-referential noun phrase has exactly one
rule, the stated order decides where two could fire (R4 against R7 in typed
spans; R2, R3 and R6 against R7), and the table is closed.
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import yaml

DRAFT = Path(
    "coordination/goals/GOAL-AUXIN-a93442/batches/BATCH-9b2090/design/"
    "TASK-20260928-4d6266/draft-contract.yaml"
)
DRAFT_SHA256 = "667cf21e1a0680eaa5eb862164835a0074c109f2254f5ac6f52428327ba27bbd"
ORDER = ["R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8", "R9-local"]

# Phrases quoted in the rule texts of F-READ, transcribed by hand from the draft.
R1 = ["the file in which this convention is written", "this file"]
R2 = [
    "the combined governing text", "this frozen contract", "the frozen contract",
    "the combined text", "this specification", "this experiment", "this amendment",
    "this protocol", "this contract", "this text",
]
R3 = [r"governing[- ]text hashes", r"governing[- ]text hash", r"governing texts",
      r"governing text", r"governing files?"]
R6_NAMED = ["this design session", "this session", "the refused predecessor"]
R6_LAYERS = [r"typed-by-hash", r"narrow-by-hash"]
R7_NAMED = [
    r"the frozen spec(?:ification)?\b", r"frozen spec(?:ification)?\b",
    r"the frozen [A-Za-z_][\w\-]*", r"(?:the )?held text", r"(?:the )?held rows",
    r"held invalidation rules", r"stays? incorporated(?: by hash)?",
    r"the held [A-Za-z_][\w\-]*",
]
R7_TOKENS = [r"\bincorporates_by_hash\b", r"\bincorporates\b", r"\bgoverning_text_table\b",
             r"\breading_of_self_references\b", r"\bpath_additions\b"]
THIS_X = r"\b(?:this|these)\s+[A-Za-z_][\w\-]*"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def layer_of(source_path: str) -> str:
    name = source_path.rsplit("/", 1)[-1]
    return {"specification.yaml": "v1", "AMD-20260926-typed.yaml": "typed",
            "AMD-20260927-narrow.yaml": "narrow", "AMD-20260928-gated.yaml": "gated"}.get(name, name)


def scan(text: str) -> list[tuple[str, str]]:
    """Return (phrase, class) occurrences; longest fixed phrases mask shorter ones."""
    found: list[tuple[int, int, str, str]] = []
    taken = [False] * len(text)

    def take(pattern: str, cls: str) -> None:
        for m in re.finditer(pattern, text, flags=re.IGNORECASE):
            if any(taken[m.start():m.end()]):
                continue
            for i in range(m.start(), m.end()):
                taken[i] = True
            found.append((m.start(), m.end(), m.group(0), cls))

    def fixed(p: str) -> str:
        return r"\s+".join(re.escape(w) for w in p.split(" "))

    for p in R1:
        take(fixed(p), "R1")
    for p in R2:
        take(fixed(p) + r"\b", "R2")
    for p in R3:
        take(p.replace(" ", r"\s+"), "R3")
    for p in R6_NAMED:
        take(fixed(p), "R6")
    for p in R7_NAMED:
        take(p.replace(" ", r"\s+"), "R7")
    take(THIS_X, "THIS_X")
    found.sort()
    return [(re.sub(r"\s+", " ", f[2]), f[3]) for f in found]


def candidates(phrase: str, cls: str, layer: str) -> list[str]:
    p = phrase.lower()
    out: list[str] = []
    if cls == "R1":
        out.append("R1")
    if cls == "R2":
        out.append("R2")
    if cls == "R3":
        out.append("R3")
    # R4: in typed spans, a reference to another record, report or file.
    names_other_file = cls == "R7" or p == "the refused predecessor"
    if layer == "typed" and names_other_file:
        out.append("R4")
    if cls == "R6":
        out.append("R6")
    if cls == "R7":
        out.append("R7")
    if cls == "THIS_X":
        out.append("R9-local")
    return out


def main() -> int:
    actual = sha256_file(DRAFT)
    if actual != DRAFT_SHA256:
        print(json.dumps({"label": "NOT_RUN", "reason": "draft sha256 mismatch", "sha256": actual}))
        return 2
    doc = yaml.safe_load(DRAFT.read_text(encoding="utf-8"))["successor_contract"]
    defects, notes = analyze(doc)

    # Negative self-test on in-memory copies: the scan must report a dropped
    # table row and a flipped rule. A scan that passes them proves nothing.
    dropped = copy.deepcopy(doc)
    dropped["self_reference_table"]["rows"] = [
        r for r in dropped["self_reference_table"]["rows"] if r["phrase"] != "this file"]
    d_defects, _ = analyze(dropped)
    flipped = copy.deepcopy(doc)
    for r in flipped["self_reference_table"]["rows"]:
        if r["phrase"] == "this amendment":
            r["rule"] = "R9-local"
    f_defects, _ = analyze(flipped)
    self_test = {
        "drop_this_file_rows_detected": len(d_defects.get("unlisted_occurrence", []))
        > len(defects.get("unlisted_occurrence", [])),
        "flip_this_amendment_rule_detected": len(f_defects.get("table_rule_differs_from_stated_order", []))
        > len(defects.get("table_rule_differs_from_stated_order", [])),
    }

    if not all(self_test.values()):
        label = "NOT_RUN"
    else:
        label = "PASS" if not any(defects.values()) else "FAIL"
    result = {
        "control": "F-READ coverage",
        "design_report": "coordination/goals/GOAL-AUXIN-a93442/batches/BATCH-9b2090/design/TASK-20260928-4d6266/design-report.yaml control_targets.controls[0]",
        "object": {"path": str(DRAFT), "sha256": actual},
        "label": label,
        "self_test": self_test,
        "method": ("Hand-transcribed phrase lists from F-READ R1-R3, R6, R7; longest-match masking; "
                   "generic 'this|these <word>' scan; rule candidates per occurrence and first-by-order "
                   "(R4 only in typed spans, for references naming another file); leaf_map target existence; "
                   "amendment.<path>/experiment.<path> resolution against leaf_map held_leaf keys. "
                   "build_successor.py was not read."),
        "limits": ("R8 (instructions to read a value) and bare field paths are not detected by phrase; "
                   "the R4 candidate is raised for every R7-class phrase in a typed span and for "
                   "'the refused predecessor'; whether Q0-11's named exceptions cover a given phrase is a "
                   "reading this control does not make."),
        "defect_classes": {k: len(v) for k, v in defects.items()},
        "note_classes": {k: len(v) for k, v in notes.items()},
        "defects": defects,
        "notes": notes,
    }
    json.dump(result, sys.stdout, indent=1, sort_keys=True, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


def analyze(doc: dict) -> tuple[dict, dict]:
    entries = doc["transcluded"]["entries"]
    by_id = {e["entry_id"]: e for e in entries}
    table = doc["self_reference_table"]["rows"]
    fresh = doc["fresh"]

    # (entry, lower phrase) -> set of table rules
    table_index: dict[tuple[str, str], set[str]] = defaultdict(set)
    table_phrases_by_entry: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for row in table:
        for eid in row["entries"]:
            table_index[(eid, row["phrase"].lower())].add(row["rule"])
            table_phrases_by_entry[eid].append((row["phrase"].lower(), row["rule"]))

    defects: dict[str, list] = defaultdict(list)
    notes: dict[str, list] = defaultdict(list)

    # 1. Coverage and order, occurrence by occurrence.
    seen_pairs: set[tuple[str, str]] = set()
    for e in entries:
        layer = layer_of(e["source_path"])
        for phrase, cls in scan(e["text"]):
            low = phrase.lower()
            # Table rows are keyed on a leading fragment of the phrase; accept an
            # exact match or a table phrase that is a word-prefix of the scanned one.
            matches = [(tp, rule) for tp, rule in table_phrases_by_entry.get(e["entry_id"], [])
                       if tp == low or low.startswith(tp + " ") or tp.startswith(low + " ")]
            if not matches and cls == "R1" and low != "this file":
                inner = [(tp, rule) for tp, rule in table_phrases_by_entry.get(e["entry_id"], [])
                         if tp in low]
                if inner:
                    seen_pairs.update((e["entry_id"], tp) for tp, _ in inner)
                    notes["r1_phrase_listed_by_inner_this_x"].append(
                        {"entry": e["entry_id"], "phrase": phrase, "table": inner})
                    continue
            if not matches:
                defects["unlisted_occurrence"].append(
                    {"entry": e["entry_id"], "layer": layer, "phrase": phrase, "class": cls})
                continue
            rules = {rule for _, rule in matches}
            seen_pairs.update((e["entry_id"], tp) for tp, _ in matches)
            if any(tp != low for tp, _ in matches):
                notes["granularity_differs"].append(
                    {"entry": e["entry_id"], "scanned": phrase, "table": sorted({tp for tp, _ in matches})})
            if len(rules) > 1:
                defects["two_rules_one_occurrence"].append(
                    {"entry": e["entry_id"], "phrase": phrase, "rules": sorted(rules)})
            cands = candidates(phrase, cls, layer)
            if not cands:
                continue
            expected = min(cands, key=ORDER.index)
            for rule in rules:
                if rule != expected:
                    defects["table_rule_differs_from_stated_order"].append({
                        "entry": e["entry_id"], "layer": layer, "phrase": phrase,
                        "table_rule": rule, "rules_that_could_fire": cands,
                        "first_by_stated_order": expected,
                        "referent_under_each": {
                            "R4": "typed conventions.Q0-11: provenance only unless a Q0-11 exception applies",
                            "R6": "provenance only",
                            "R7": "leaf_map row entries or fresh field",
                        }.get(expected, "") + " vs " + {
                            "R6": "provenance only",
                            "R7": "leaf_map row entries or fresh field",
                        }.get(rule, rule),
                        "same_outcome_by_rule_text": {expected, rule} == {"R4", "R6"}})

    # 2. Table rows that name an (entry, phrase) the scan did not find.
    for row in table:
        for eid in row["entries"]:
            if eid not in by_id:
                defects["table_names_unknown_entry"].append({"entry": eid, "phrase": row["phrase"]})
            elif (eid, row["phrase"].lower()) not in seen_pairs:
                notes["table_row_not_found_by_scan"].append({"entry": eid, "phrase": row["phrase"],
                                                             "rule": row["rule"]})

    # 3. R9 literal coverage: layer names R6 names and tokens R7 names.
    for e in entries:
        for pat in R6_LAYERS + R7_TOKENS:
            for m in re.finditer(pat, e["text"]):
                if (e["entry_id"], m.group(0).lower()) not in table_index:
                    notes["r6_r7_named_token_not_in_table"].append(
                        {"entry": e["entry_id"], "token": m.group(0)})

    # 3b. In typed spans, references naming another held file by file name or record
    # id: R7 names this form, but R4 is tried first and gives Q0-11 (provenance only
    # unless a named exception applies). Listed for the review round, not graded.
    for e in entries:
        if layer_of(e["source_path"]) != "typed":
            continue
        for m in re.finditer(r"AMD-(?:EXP-AUXIN-7e2e3d-)?\d{8}-[a-z0-9]+(?:\.yaml)?|specification\.yaml", e["text"]):
            notes["typed_span_named_held_file_reference_R4_decides"].append(
                {"entry": e["entry_id"], "reference": m.group(0),
                 "context": e["text"][max(0, m.start() - 80):m.end() + 40]})

    # 4. amendment.<path> / experiment.<path> references resolve through leaf_map (R7).
    leaf_rows = doc["leaf_map"]["rows"]
    leaves = [r["held_leaf"] for r in leaf_rows]
    for e in entries:
        layer = layer_of(e["source_path"])
        for m in re.finditer(r"\b(amendment|experiment)\.([A-Za-z_][\w]*(?:\.[A-Za-z_0-9][\w\-]*)*)", e["text"]):
            # experiment.<path> names v1 (specification.yaml) fields; amendment.<path> the span's file.
            target_layer = "v1" if m.group(1) == "experiment" else layer
            path = m.group(2)
            key = f"{target_layer}:{path}"
            hit = [lf for lf in leaves if lf == key or any(lf.startswith(key + s) for s in (" ", ".", "["))
                   or key.startswith(lf.split(" ")[0] + ".")]
            if not hit:
                defects["path_reference_without_leaf_map_row"].append(
                    {"entry": e["entry_id"], "layer": layer, "reference": m.group(0)})

    # 5. leaf_map targets exist.
    fresh_ids: dict[str, set[str]] = {}
    for key, value in fresh.items():
        if isinstance(value, dict) and "id" in value:
            fresh_ids[value["id"]] = {k for k in value if k != "id"}

    def fresh_exists(ref: str) -> bool:
        head, _, sub = ref.partition(".")
        return head in fresh_ids and (not sub or sub in fresh_ids[head])

    stated_entries: set[str] = set()
    for r in leaf_rows:
        disp = r["disposition"]
        if disp == "stated":
            for eid in r.get("entries", []):
                if eid not in by_id:
                    defects["leaf_map_unknown_entry"].append({"leaf": r["held_leaf"], "entry": eid})
                stated_entries.add(eid)
        for ref in r.get("replaced_by_fresh", []) or []:
            if not fresh_exists(ref):
                defects["leaf_map_unknown_fresh_field"].append({"leaf": r["held_leaf"], "fresh": ref})
        for eid in r.get("replaced_by_entries", []) or []:
            if eid not in by_id:
                defects["leaf_map_unknown_entry"].append({"leaf": r["held_leaf"], "entry": eid})
        if disp == "not_stated_replaced_by_fresh" and not r.get("replaced_by_fresh"):
            # Row may carry the field under another key; record what it has.
            if not any(k.startswith("replaced_by") for k in r):
                defects["replaced_row_names_no_fresh_field"].append({"leaf": r["held_leaf"]})
    for eid in by_id:
        if eid not in stated_entries:
            defects["entry_in_no_stated_row"].append(eid)
    return dict(defects), dict(notes)


if __name__ == "__main__":
    raise SystemExit(main())
