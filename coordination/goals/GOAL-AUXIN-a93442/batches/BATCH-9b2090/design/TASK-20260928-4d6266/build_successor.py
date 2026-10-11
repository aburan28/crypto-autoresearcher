#!/usr/bin/env python3
"""Builder for the draft successor contract EXP-AUXIN-bafa2e (TASK-20260928-4d6266).

Reads the four held texts of EXP-AUXIN-7e2e3d from one commit, walks
governing_text_table of AMD-20260928-gated.yaml as a design input, and emits
byte-exact transcluded entries (F-TX of fresh-text.yaml) composed with the fresh
block. Held leaves listed in REPLACED_LEAVES are not stated; their leaf_map rows
name the fresh field that states this contract's rule. It writes only
draft-contract.yaml beside itself, never edits a source,
and reads nothing from the refused draft EXP-AUXIN-edd104.

Usage: python3 build_successor.py <commit>   (run from the repository root)
"""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
SOURCES = {
    "v1": ("experiments/EXP-AUXIN-7e2e3d/specification.yaml",
           "1f803aa0a535e4c0a321dfcb3851b89cbd4cae23596ad70e1aa1fd1b06639fbc"),
    "typed": ("experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260926-typed.yaml",
              "3c57978c91b632226c0e0543913f8a122bb16d121b0a308254b1c99cedeeaad6"),
    "narrow": ("experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260927-narrow.yaml",
               "ccd11216c3250d9ab69fafa7f4252a872704772a2091fc70989a198d1ca11dcd"),
    "gated": ("experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260928-gated.yaml",
              "77d1d5bfd8bf9d1c164903742c501f7161cc1b47814420d1957d6e39da9a8f3f"),
}
LAYER_OF = {"v1": "v1", "typed": "typed-by-hash", "narrow": "narrow-by-hash", "gated": "gated"}
PREFIX = {"v1": "v1", "typed-by-hash": "typed", "narrow-by-hash": "narrow", "gated": "gated"}

META_TOP = {
    "v1": {"id", "hypothesis_id", "derived_from_idea", "source_idea_ids", "question_id", "goal_id",
           "version", "title", "status", "frozen", "approved_by", "approval_decision", "approval_basis",
           "assigned_to", "scientific_execution_authorized", "scientific_execution_scope",
           "execution_authorized", "evidence_eligible", "derivation_provenance", "recorded_at",
           "write_scope"},
    "amd": {"id", "experiment_id", "hypothesis_id", "predecessor_amendment", "predecessor_status",
            "question_id", "goal_id", "batch_id", "producer_task", "producer_snapshot",
            "review_plan_id", "decision_id", "decision_id_note", "recorded_at", "kind", "status",
            "approval", "supersedes_fields", "supersedes_fields_note", "not_superseded",
            "does_not_rewrite", "does_not_rehabilitate", "cites", "defect", "design_record",
            "authorization", "non_claims", "incorporates", "incorporates_by_hash",
            "envelope_not_incorporated", "narrow_envelope_not_incorporated", "span_rules",
            "gated_span_rules", "precedence", "governing_text_table", "governs_nothing",
            "reading_of_self_references", "path_additions"},
}

# Held leaves this contract does not state. Each names the fresh field that
# states this contract's rule on the subject, and the named defect it closes.
REPLACED_LEAVES = {
    "typed:change.D8_custody.trial_plan span TP-FOUR": (["F-CUSTODY.trial_plan"], "EJ6-B1"),
    "typed:change.D8_custody.trial_plan outside span TP-FOUR": (["F-CUSTODY.trial_plan"], "EJ6-B1"),
    "typed:change.D8_custody.manifest span MAN-FOUR": (["F-CUSTODY.manifest"], "EJ6-B1"),
    "typed:change.D8_custody.manifest span MAN-DIRTY": (["F-CUSTODY.manifest"], "EJ6-B1"),
    "typed:change.D8_custody.manifest outside spans MAN-FOUR, MAN-DIRTY": (["F-CUSTODY.manifest"], "EJ6-B1"),
    "typed:tools_and_admission.admission_gate span ADM-7": (["F-CUSTODY.admission_item_7"], "EJ6-B1"),
    "typed:invalidation_rules item 10": (["F-CUSTODY.invalidation"], "EJ6-B1"),
    "typed:change.D10_additivity.rule": (["F-REV", "F-WRITE.implementation_modules"], "EJ6-B2"),
    "narrow:custody_consequences.rule": (["F-CUSTODY.independence"], "EJ6-B1"),
    "narrow:custody_consequences.fields": (["F-CUSTODY.independence"], "EJ6-B1"),
    "narrow:corrective.custody.invalidation_rules_added.adds_to": (["F-CUSTODY.invalidation"], "EJ6-B1"),
    "narrow:corrective.custody.invalidation_rules_added.rules item 1": (["F-CUSTODY.invalidation"], "EJ6-B1"),
    "narrow:corrective.custody.invalidation_rules_added.rules item 2": (["F-CUSTODY.invalidation"], "EJ3-B1, EJ6-B1"),
    "gated:custody_additions.rule": (["F-CUSTODY.independence"], "EJ6-B1"),
    "gated:custody_additions.trial_plan": (["F-CUSTODY.trial_plan"], "EJ6-B1"),
    "gated:custody_additions.manifest": (["F-CUSTODY.manifest"], "EJ6-B1"),
    "gated:custody_additions.invalidation_rules_added": (["F-CUSTODY.invalidation"], "EJ3-B1, EJ6-B1"),
}
# Source paths no entry may be copied from (the texts of the replaced leaves).
REPLACED_SOURCE_PATHS = [
    ("typed", "change.D8_custody.trial_plan"), ("typed", "change.D8_custody.manifest"),
    ("typed", "change.D10_additivity.rule"), ("typed", "invalidation_rules item 10"),
    ("narrow", "span_rules[TP-FOUR].replacement"), ("narrow", "span_rules[MAN-FOUR].replacement"),
    ("narrow", "span_rules[MAN-DIRTY].replacement"), ("narrow", "span_rules[ADM-7].replacement"),
    ("narrow", "custody_consequences"), ("narrow", "corrective.custody.invalidation_rules_added"),
    ("gated", "custody_additions"),
]

SELF_REF = re.compile(r"\b(this|these|This|These|THIS|THESE)\s+([A-Za-z][A-Za-z0-9_\-]*)")
EXTRA_PHRASES = re.compile(r"(the combined governing text|the combined text|the frozen contract|"
                           r"governing[- ]text hash(?:es)?|governing texts?|governing files?|"
                           r"the frozen spec(?:ification)?\b|frozen spec(?:ification)?\b|the frozen [a-z_]+|"
                           r"the held [a-z\-]+|held invalidation rules|the refused predecessor|"
                           r"stays? incorporated)", re.I)
R1_NOUNS = {"file"}
R2_NOUNS = {"amendment", "text", "protocol", "contract", "frozen", "experiment", "specification"}
R6_NOUNS = {"design", "session"}


def phrase_rule(ph):
    head, _, rest = ph.partition(" ")
    if head in ("this", "these"):
        noun = rest.lower()
        if noun in R1_NOUNS:
            return "R1"
        if noun in R2_NOUNS:
            return "R2"
        if noun in R6_NOUNS:
            return "R6"
        return "R9-local"
    if ph in ("the combined text", "the combined governing text", "the frozen contract"):
        return "R2"
    if ph.startswith("governing"):
        return "R3"
    if ph == "the refused predecessor":
        return "R6"
    if ph.startswith("the frozen") or ph.startswith("frozen spec") or "held" in ph or "incorporated" in ph:
        return "R7"
    raise SystemExit(f"phrase without a rule: {ph}")


def sha(b):
    return hashlib.sha256(b).hexdigest()


def blob(commit, path):
    return subprocess.run(["git", "show", f"{commit}:{path}"], check=True,
                          capture_output=True).stdout


def split_path(p):
    segs, depth, cur = [], 0, ""
    for ch in p:
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
        if ch == "." and depth == 0:
            segs.append(cur)
            cur = ""
        else:
            cur += ch
    if cur:
        segs.append(cur)
    return segs


SEG = re.compile(r"^(?P<key>[^\[ ]+)(?:\[(?P<sel>[^\]]+)\])?(?: item (?P<item>\d+))?$")


def _sel(items, sel, is_node):
    for i, it in enumerate(items):
        if is_node:
            if isinstance(it, yaml.MappingNode):
                for k, v in it.value:
                    if isinstance(v, yaml.ScalarNode) and v.value == sel:
                        return i
        elif isinstance(it, dict) and sel in [v for v in it.values() if isinstance(v, str)]:
            return i
    raise KeyError(sel)


def walk(root, path, is_node):
    cur = root
    for seg in split_path(path):
        m = SEG.match(seg)
        if not m:
            raise KeyError(seg)
        key, sel, item = m.group("key"), m.group("sel"), m.group("item")
        if is_node:
            nxt = [v for k, v in cur.value if k.value == key]
            if not nxt:
                raise KeyError(key)
            cur = nxt[0]
            if sel is not None:
                cur = cur.value[_sel(cur.value, sel, True)]
            if item is not None:
                cur = cur.value[int(item) - 1]
        else:
            cur = cur[key]
            if sel is not None:
                cur = cur[_sel(cur, sel, False)]
            if item is not None:
                cur = cur[int(item) - 1]
    return cur


class Src:
    def __init__(self, prefix, commit):
        self.prefix = prefix
        self.path, self.expected = SOURCES[prefix]
        self.raw = blob(commit, self.path)
        self.sha = sha(self.raw)
        if self.sha != self.expected:
            raise SystemExit(f"source hash mismatch: {self.path}")
        self.text = self.raw.decode("utf-8")
        self.top_key = "experiment" if prefix == "v1" else "amendment"
        self.doc = yaml.safe_load(self.text)[self.top_key]
        self.node = [v for k, v in yaml.compose(self.text).value if k.value == self.top_key][0]

    def full(self, path):
        return f"{self.top_key}.{path}"


def span_rule(srcs, span_id):
    for pre, key in (("narrow", "span_rules"), ("gated", "gated_span_rules")):
        for r in srcs[pre].doc[key]:
            if r["id"] == span_id:
                return pre, key, r
    raise KeyError(span_id)


def locate_span(value, rule):
    start = value.find(rule["from"])
    if start < 0 or value.find(rule["from"], start + 1) >= 0:
        raise SystemExit(f"span 'from' not unique: {rule['id']}")
    t = value.find(rule["through"], start)
    end = t + len(rule["through"])
    if sha(value[start:end].encode()) != rule["replaced_span_sha256"]:
        raise SystemExit(f"replaced span hash mismatch: {rule['id']}")
    return start, end


def span_replacement_location(srcs, span_id, layer):
    if span_id == "INV-CLAIM":
        return "gated", "corrective.threshold_index.text"
    pre, key, _ = span_rule(srcs, span_id)
    if layer == "gated" and pre != "gated":
        raise SystemExit(f"unexpected gated span {span_id}")
    return pre, f"{key}[{span_id}].replacement"


def make_entry(src, commit, path, kind, start=None, end=None):
    if kind == "loaded_value":
        v = walk(src.doc, path, False)
        s = v if start is None else v[start:end]
        anchor = {"field_path": src.full(path), "kind": "loaded_value"}
        if start is not None:
            anchor["char_range"] = [start, end]
        return {"source_path": src.path, "source_commit": commit, "source_blob_sha256": src.sha,
                "anchor": anchor, "span_sha256": sha(s.encode("utf-8")), "text": s}
    n = walk(src.node, path, True)
    s = src.text[n.start_mark.index:n.end_mark.index]
    lc = [n.start_mark.line + 1, n.start_mark.column, n.end_mark.line + 1, n.end_mark.column]
    return {"source_path": src.path, "source_commit": commit, "source_blob_sha256": src.sha,
            "anchor": {"field_path": src.full(path), "kind": "source_bytes", "line_col_range": lc},
            "span_sha256": sha(s.encode("utf-8")), "text": s}


def line_col_slice(text, lc):
    lines = text.split("\n")
    start = sum(len(x) + 1 for x in lines[:lc[0] - 1]) + lc[1]
    end = sum(len(x) + 1 for x in lines[:lc[2] - 1]) + lc[3]
    return text[start:end]


def entry_for(src, commit, path):
    v = walk(src.doc, path, False)
    return make_entry(src, commit, path, "loaded_value" if isinstance(v, str) else "source_bytes")


def is_meta(prefix, field):
    if prefix == "file":
        return True
    top = re.split(r"[.\[ ]", field)[0]
    return top in META_TOP["v1" if prefix == "v1" else "amd"]


def under_path(fp, root):
    return fp == root or fp.startswith(root + ".") or fp.startswith(root + " item ")


def main(commit):
    srcs = {p: Src(p, commit) for p in SOURCES}
    table = srcs["gated"].doc["governing_text_table"]
    entries, leaf_map, stated_at = [], [], {}
    forbidden_roots = [(srcs[p].path, srcs[p].full(q)) for p, q in REPLACED_SOURCE_PATHS]

    def add(e, leaf, segment):
        fp = e["anchor"]["field_path"]
        for spath, root in forbidden_roots:
            if e["source_path"] == spath and (under_path(fp, root) or under_path(root, fp)):
                raise SystemExit(f"entry would state replaced text: {leaf} -> {fp}")
        key = (e["source_path"], fp, tuple(e["anchor"].get("char_range", ())))
        if key in stated_at:
            return stated_at[key]
        eid = f"T-{len(entries) + 1:04d}"
        entries.append({"entry_id": eid, "states_leaf": leaf, "segment": segment, **e})
        stated_at[key] = eid
        return eid

    span_targets = set()
    for row in table:
        m = re.match(r"^\w+:(.*) span (\S+)$", row["field"])
        if m and not is_meta(row["field"].split(":", 1)[0], m.group(1)):
            span_targets.add(span_replacement_location(srcs, m.group(2), row["layer"]))

    seen_replaced = set()
    for row in table:
        f, layer, via = row["field"], row["layer"], row["via"]
        prefix, rest = f.split(":", 1)
        rec = {"held_leaf": f, "held_governing_layer": layer}
        if is_meta(prefix, rest):
            rec["disposition"] = "not_stated_envelope_or_layering"
            leaf_map.append(rec)
            continue
        src = srcs[prefix]
        m_out = re.match(r"^(.*) outside spans? (.+)$", rest)
        m_span = re.match(r"^(.*) span (\S+)$", rest)
        m_exc = re.match(r"^(.*) except (item \d+)?\.?(.*)$", rest)
        if f in REPLACED_LEAVES:
            seen_replaced.add(f)
            fresh_ids, closes = REPLACED_LEAVES[f]
            rec.update(disposition="not_stated_replaced_by_fresh", replaced_by_fresh=fresh_ids,
                       closes=closes)
            if m_span and not m_out:
                base, sid = m_span.group(1), m_span.group(2)
                a, b = locate_span(walk(src.doc, base, False), span_rule(srcs, sid)[2])
                rec.update(position_in=f"{prefix}:{base}", replaces_char_range=[a, b])
            leaf_map.append(rec)
            continue
        if m_out:
            base = m_out.group(1)
            ids = [s.strip() for s in m_out.group(2).split(",")]
            val = walk(src.doc, base, False)
            cuts = sorted(locate_span(val, span_rule(srcs, i)[2]) for i in ids)
            pos, eids = 0, []
            for (a, b) in cuts + [(len(val), len(val))]:
                if a > pos:
                    eids.append(add(make_entry(src, commit, base, "loaded_value", pos, a),
                                    f, f"outside {', '.join(ids)} [{pos}:{a}]"))
                pos = b
            placed = []
            for i in ids:
                lbl = f"{prefix}:{base} span {i}"
                placed.append(f"{i} by {REPLACED_LEAVES[lbl][0][0]}" if lbl in REPLACED_LEAVES
                              else f"{i} by its stated entry")
            rec.update(disposition="stated", entries=eids,
                       composition=(f"segments of {prefix}:{base} in order, each span at its position "
                                    f"({'; '.join(placed)})"))
        elif m_span:
            base, sid = m_span.group(1), m_span.group(2)
            val = walk(src.doc, base, False)
            a, b = locate_span(val, span_rule(srcs, sid)[2])
            rpre, rpath = span_replacement_location(srcs, sid, layer)
            eid = add(entry_for(srcs[rpre], commit, rpath), f, f"span {sid} at [{a}:{b}] of {prefix}:{base}")
            rec.update(disposition="stated", entries=[eid], position_in=f"{prefix}:{base}",
                       replaces_char_range=[a, b])
        elif m_exc:
            base, item, sub = m_exc.group(1), m_exc.group(2), m_exc.group(3)
            val = walk(src.doc, base, False)
            eids = []
            for i, it in enumerate(val, 1):
                if item and f"item {i}" == item:
                    for k in it:
                        if k != sub:
                            eids.append(add(entry_for(src, commit, f"{base} item {i}.{k}"), f, f"item {i}.{k}"))
                else:
                    eids.append(add(entry_for(src, commit, f"{base} item {i}"), f, f"item {i}"))
            rec.update(disposition="stated", entries=eids)
        elif LAYER_OF[prefix] == layer:
            inner = [p for (q, p) in span_targets if q == prefix and p.startswith(rest + ".")]
            if inner:
                keys = [k for k in walk(src.doc, rest, False) if f"{rest}.{k}" not in inner]
                rec.update(disposition="stated",
                           entries=[add(entry_for(src, commit, f"{rest}.{k}"), f, k) for k in keys],
                           note=f"{', '.join(inner)} is stated at its span position")
            else:
                rec.update(disposition="stated", entries=[add(entry_for(src, commit, rest), f, "whole")])
        else:
            mn = re.match(r"^AMD-20260927-narrow\.yaml (\S+)$", via)
            mg = re.match(r"^(corrective\.\S+) of this file", via) or re.match(r"^supersedes_fields -> (corrective\.\S+)", via)
            if mn:
                rec.update(disposition="PENDING", target=("narrow", mn.group(1)))
            elif mg or (prefix == "narrow" and layer == "gated" and "fc6" in via.lower()):
                path = mg.group(1) if mg else "corrective.falsification_condition_mapping_fc6.outcome"
                rec.update(disposition="PENDING", target=("gated", path))
            elif prefix == "v1" and layer == "typed-by-hash":
                rec.update(disposition="not_stated_superseded_in_held_table", superseded_via=via)
            else:
                rec.update(disposition="UNRESOLVED", via=via)
        leaf_map.append(rec)

    missing = sorted(set(REPLACED_LEAVES) - seen_replaced)
    if missing:
        raise SystemExit(f"replaced leaves not in the held table: {missing}")

    def under(e, pre, path):
        return e["source_path"] == srcs[pre].path and under_path(e["anchor"]["field_path"], srcs[pre].full(path))

    for rec in leaf_map:
        if rec["disposition"] != "PENDING":
            continue
        pre, path = rec.pop("target")
        target_fp = srcs[pre].full(path)
        above = [e["entry_id"] for e in entries if e["source_path"] == srcs[pre].path and (
            target_fp.startswith(e["anchor"]["field_path"] + ".")
            or target_fp.startswith(e["anchor"]["field_path"] + " item "))]
        below = [e["entry_id"] for e in entries if under(e, pre, path)]
        if above:
            rec.update(disposition="stated", entries=above,
                       note=f"{pre}:{path} lies inside the text of the listed entry")
        elif below:
            rec.update(disposition="stated", entries=below,
                       note=f"stated by the entries for {pre}:{path} and the leaves under it")
        else:
            rec.update(disposition="stated",
                       entries=[add(entry_for(srcs[pre], commit, path), rec["held_leaf"], "whole")])

    overlaps = []
    for a in entries:
        for b in entries:
            if a is not b and a["source_path"] == b["source_path"]:
                pa, pb = a["anchor"]["field_path"], b["anchor"]["field_path"]
                if pb.startswith(pa + ".") or pb.startswith(pa + " item ") or (
                        pa == pb and not (a["anchor"].get("char_range") and b["anchor"].get("char_range"))):
                    overlaps.append([a["entry_id"], b["entry_id"]])
    if overlaps:
        raise SystemExit(f"overlapping entries: {overlaps[:5]}")

    def leaf_rows(prefix, path):
        for r in leaf_map:
            h = r["held_leaf"]
            if h.startswith(f"{prefix}:{path}") and (h == f"{prefix}:{path}" or h[len(prefix) + 1 + len(path)] in ". ["):
                yield r

    def leaf_entries(prefix, path):
        ids = []
        for r in leaf_rows(prefix, path):
            if r["disposition"] == "stated":
                ids += [i for i in r["entries"] if i not in ids]
        return ids

    def leaf_fresh(prefix, path):
        ids = []
        for r in leaf_rows(prefix, path):
            if r["disposition"] == "not_stated_replaced_by_fresh":
                ids += [i for i in r["replaced_by_fresh"] if i not in ids]
        return ids

    def source_entries(prefix, path):
        root = srcs[prefix].full(path)
        return [e["entry_id"] for e in entries if e["source_path"] == srcs[prefix].path and (
            under_path(e["anchor"]["field_path"], root) or root.startswith(e["anchor"]["field_path"] + ".")
            or root.startswith(e["anchor"]["field_path"] + " item "))]

    # EJ2 C-ORDER: a cited item's controls are read whether or not they carry the
    # "amendment." prefix, so "control C-ORDER" in item 9 is part of its set.
    ctl_prefixed = re.compile(r"amendment\.controls ((?:C-[A-Z\-]+(?:, | and )?)+)")
    ctl_bare = re.compile(r"(?<!amendment\.)\bcontrols? ((?:C-[A-Z\-]+(?:, | and )?)+)")
    typed_sf = srcs["typed"].doc["supersedes_fields"]
    for r in leaf_map:
        if r["disposition"] != "not_stated_superseded_in_held_table":
            continue
        m = re.search(r"supersedes_fields items? (\d+)(?: and (\d+))?", r["superseded_via"])
        ids, fresh_ids, bare_controls = [], [], []
        for n in [g for g in (m.groups() if m else ()) if g]:
            text = typed_sf[int(n) - 1]
            for rx, bare in ((ctl_prefixed, False), (ctl_bare, True)):
                for ctl in rx.findall(text):
                    for cid in re.findall(r"C-[A-Z]+(?:-[A-Z]+)*", ctl):
                        new = [i for i in leaf_entries("typed", f"controls[{cid}]") if i not in ids]
                        ids += new
                        if bare and new:
                            bare_controls.append(cid)
            for p in re.findall(r"amendment\.([A-Za-z0-9_.\-]+[A-Za-z0-9_])", text):
                if p == "controls":
                    continue
                ids += [i for i in (leaf_entries("typed", p) or source_entries("typed", p)) if i not in ids]
                fresh_ids += [i for i in leaf_fresh("typed", p) if i not in fresh_ids]
        r["replaced_by_entries"] = ids
        if fresh_ids:
            r["replaced_by_fresh"] = fresh_ids
        if bare_controls:
            r["note"] = (f"replaced_by_entries includes controls[{', '.join(bare_controls)}], which the cited "
                         f"supersedes_fields item names without an amendment. prefix (EJ2 C-ORDER)")

    additions, dropped_groups = [], []
    for pa in srcs["gated"].doc["path_additions"]:
        m = re.match(r"^(\S+) of AMD-20260927-narrow\.yaml$", pa["path"])
        held = source_entries("narrow", m.group(1)) if m else leaf_entries("typed", pa["path"])
        add_ids = []
        for a in pa["additions"]:
            layer, apath = a.split(":", 1)
            add_ids += source_entries(PREFIX[layer], apath)
        if not add_ids:
            dropped_groups.append({"path": pa["path"], "held_additions": pa["additions"],
                                   "reason": "every addition is a replaced held leaf; F-CUSTODY states the rule"})
            continue
        if not held:
            raise SystemExit(f"unresolved addition group: {pa['path']}")
        additions.append({"path": pa["path"], "held_entries": held, "addition_entries": add_ids})

    # Closed self-reference table (F-READ R9) over every stated entry.
    phrases = {}
    for e in entries:
        for mm in SELF_REF.finditer(e["text"]):
            ph = f"{mm.group(1).lower()} {mm.group(2)}"
            phrases.setdefault(ph, []).append(e["entry_id"])
        for mm in EXTRA_PHRASES.finditer(e["text"]):
            phrases.setdefault(mm.group(1).lower(), []).append(e["entry_id"])
    table_rows = [{"phrase": ph, "entries": sorted(set(phrases[ph])), "rule": phrase_rule(ph)}
                  for ph in sorted(phrases)]

    replacement_table = [{"held_leaf": k, "replaced_by_fresh": v[0], "closes": v[1]}
                         for k, v in REPLACED_LEAVES.items()]

    fresh = yaml.safe_load((HERE / "fresh-text.yaml").read_text(encoding="utf-8"))["fresh"]
    out = {"successor_contract": {
        "fresh": fresh,
        "self_reference_table": {"text_kind": "fresh", "note": (
            "Generated by build_successor.py by scanning every transcluded entry for 'this X', 'these X' "
            "and the phrases F-READ R2, R3, R6 and R7 name. rule is the F-READ rule of that id; R9-local is "
            "defined in F-READ R9. The table is closed (F-READ R9)."),
            "rows": table_rows},
        "replacement_table": {"text_kind": "fresh", "note": (
            "Held leaves this contract does not state, the fresh field that states this contract's rule on "
            "the subject, and the named defect the replacement closes. Mirrors the leaf_map rows with "
            "disposition not_stated_replaced_by_fresh."), "rows": replacement_table},
        "additions_read_together": {"text_kind": "fresh", "note": (
            "Fresh grouping, derived by build_successor.py from path_additions of AMD-20260928-gated.yaml "
            "read as a design input. Each group is read together under F-PREC. dropped_groups lists held "
            "path_additions whose every addition is a replaced leaf."), "groups": additions,
            "dropped_groups": dropped_groups},
        "transcluded": {
            "text_kind": "transcluded",
            "governed_by": "F-TX of this contract",
            "source_commit": commit,
            "sources": {p: {"path": s.path, "blob_sha256": s.sha} for p, s in srcs.items()},
            "anchor_convention": (
                "loaded_value: the span is the string a YAML 1.1 safe loader returns for anchor.field_path from "
                "the source blob at source_commit, or its [start, end) character sub-range when char_range is "
                "given; span_sha256 is over its UTF-8 bytes. source_bytes: the span is the exact text of the "
                "source blob from line_col_range[0:2] to line_col_range[2:4] (lines 1-based, columns 0-based "
                "characters), the value node of anchor.field_path as a YAML composer locates it; span_sha256 is "
                "over its UTF-8 bytes. In both kinds the transcluded span is the value a YAML safe loader "
                "returns for this entry's text field."),
            "entries": entries},
        "leaf_map": {"text_kind": "fresh", "note": (
            "One row per leaf of governing_text_table of AMD-20260928-gated.yaml (read as a design input, "
            "not as governing text). Each held leaf has exactly one disposition in this contract: stated, "
            "not_stated_superseded_in_held_table, not_stated_envelope_or_layering or "
            "not_stated_replaced_by_fresh."), "rows": leaf_map},
    }}
    header = (
        "# =============================================================================\n"
        "# DRAFT successor-experiment contract EXP-AUXIN-bafa2e, written by\n"
        "# TASK-20260928-4d6266 in BATCH-9b2090, GOAL-AUXIN-a93442. status draft,\n"
        "# approved_by null. It authorizes no run and approves nothing. It is not an\n"
        "# amendment to EXP-AUXIN-edd104 or EXP-AUXIN-7e2e3d.\n"
        "#\n"
        "# GENERATED by build_successor.py from fresh-text.yaml (fresh text) and\n"
        "# byte-exact spans of the held EXP-AUXIN-7e2e3d records at one commit\n"
        "# (transcluded text, under F-TX). Fresh and transcluded parts are kept apart\n"
        "# and each is labelled by text_kind. Do not edit by hand.\n"
        "# =============================================================================\n")
    target = HERE / "draft-contract.yaml"
    target.write_text(header + yaml.safe_dump(out, sort_keys=False, allow_unicode=True, width=1 << 20),
                      encoding="utf-8")

    doc = yaml.safe_load(target.read_text(encoding="utf-8"))["successor_contract"]
    if doc["fresh"] != fresh:
        raise SystemExit("fresh block changed on reload")
    bad = [e["entry_id"] for e in doc["transcluded"]["entries"] if sha(e["text"].encode("utf-8")) != e["span_sha256"]]
    by_path = {s.path: s for s in srcs.values()}
    for e in doc["transcluded"]["entries"]:
        s = by_path[e["source_path"]]
        path = e["anchor"]["field_path"][len(s.top_key) + 1:]
        if e["anchor"]["kind"] == "loaded_value":
            v = walk(s.doc, path, False)
            cr = e["anchor"].get("char_range")
            if (v if not cr else v[cr[0]:cr[1]]) != e["text"]:
                bad.append(e["entry_id"])
        elif line_col_slice(s.text, e["anchor"]["line_col_range"]) != e["text"]:
            bad.append(e["entry_id"])
    counts = {}
    for r in doc["leaf_map"]["rows"]:
        counts[r["disposition"]] = counts.get(r["disposition"], 0) + 1
    summary = {"entries": len(doc["transcluded"]["entries"]), "leaf_map_rows": len(doc["leaf_map"]["rows"]),
               "dispositions": counts, "addition_groups": len(additions),
               "dropped_groups": [g["path"] for g in dropped_groups],
               "self_reference_phrases": len(table_rows),
               "self_reference_rules": {k: sum(1 for r in table_rows if r["rule"] == k)
                                        for k in ("R1", "R2", "R3", "R6", "R7", "R9-local")},
               "reload_failures": bad, "draft_contract_sha256": sha(target.read_bytes())}
    print(json.dumps(summary, indent=1))
    return 1 if bad or counts.get("UNRESOLVED") or counts.get("PENDING") else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
