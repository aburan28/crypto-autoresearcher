#!/usr/bin/env python3
"""Builder for the RS-B draft transclusion set of TASK-20260928-fa9275.

Reads the four held governing texts of EXP-AUXIN-7e2e3d from one commit, walks
governing_text_table of AMD-EXP-AUXIN-7e2e3d-20260928-gated as a design input,
and emits byte-exact transclusions under DEC-20260928-2afb23 plan_amendment
PA-8456b6-T1 (T1 to T5), composed with the fresh text of fresh-text.yaml. It
writes only draft-contract.yaml beside itself and never edits a source. Every
span hash is recomputed on reload (T5).

Usage: python3 build_draft.py <commit>   (run from the repository root)
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
        loaded = yaml.safe_load(self.text)
        node = yaml.compose(self.text)
        self.top_key = "experiment" if prefix == "v1" else "amendment"
        self.doc = loaded[self.top_key]
        self.node = [v for k, v in node.value if k.value == self.top_key][0]

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
    """One transclusion. kind loaded_value: the string a YAML safe loader
    returns for path (optionally a [start, end) character sub-range, the held
    span convention of AMD-20260927-narrow.yaml). kind source_bytes: the exact
    blob bytes of the value node, for non-string leaves."""
    if kind == "loaded_value":
        v = walk(src.doc, path, False)
        s = v if start is None else v[start:end]
        b = s.encode("utf-8")
        anchor = {"field_path": src.full(path), "kind": "loaded_value"}
        if start is not None:
            anchor["char_range"] = [start, end]
        return {"source_path": src.path, "source_commit": commit, "source_blob_sha256": src.sha,
                "anchor": anchor, "span_sha256": sha(b), "text": s}
    n = walk(src.node, path, True)
    s = src.text[n.start_mark.index:n.end_mark.index]
    b = s.encode("utf-8")
    lc = [n.start_mark.line + 1, n.start_mark.column, n.end_mark.line + 1, n.end_mark.column]
    return {"source_path": src.path, "source_commit": commit, "source_blob_sha256": src.sha,
            "anchor": {"field_path": src.full(path), "kind": "source_bytes", "line_col_range": lc},
            "span_sha256": sha(b), "text": s}


def line_col_slice(text, lc):
    """Characters from (line, column) to (line, column); lines 1-based, columns 0-based."""
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


def main(commit):
    srcs = {p: Src(p, commit) for p in SOURCES}
    table = srcs["gated"].doc["governing_text_table"]
    entries, leaf_map, stated_at = [], [], {}

    def add(e, leaf, segment):
        key = (e["source_path"], e["anchor"]["field_path"], tuple(e["anchor"].get("char_range", ())))
        if key in stated_at:
            return stated_at[key]
        eid = f"T-{len(entries) + 1:04d}"
        e = {"entry_id": eid, "states_leaf": leaf, "segment": segment, **e}
        entries.append(e)
        stated_at[key] = eid
        return eid

    span_targets = set()
    for row in table:
        m = re.match(r"^\w+:(.*) span (\S+)$", row["field"])
        if m and not is_meta(row["field"].split(":", 1)[0], m.group(1)):
            span_targets.add(span_replacement_location(srcs, m.group(2), row["layer"]))

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
            rec.update(disposition="stated", entries=eids,
                       composition=f"segments of {prefix}:{base} in order, each span of {', '.join(ids)} at its position")
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

    # Indirect rows: a target already stated at or below its path by direct rows
    # points at those entries, so no text is stated twice.
    def under(e, pre, path):
        fp = e["anchor"]["field_path"]
        root = srcs[pre].full(path)
        return e["source_path"] == srcs[pre].path and (fp == root or fp.startswith(root + ".")
                                                          or fp.startswith(root + " item "))
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
        raise SystemExit(f"overlapping entries: {[(x, y, [e["anchor"]["field_path"] + " <- " + e["states_leaf"] for e in entries if e["entry_id"] in (x, y)]) for x, y in overlaps[:5]]}")

    def leaf_entries(prefix, path):
        ids = []
        for r in leaf_map:
            h = r["held_leaf"]
            if r["disposition"] == "stated" and h.startswith(f"{prefix}:{path}") and (
                    h == f"{prefix}:{path}" or h[len(prefix) + 1 + len(path)] in ". ["):
                ids += [i for i in r["entries"] if i not in ids]
        return ids

    def source_entries(prefix, path):
        root = srcs[prefix].full(path)
        out = []
        for e in entries:
            fp = e["anchor"]["field_path"]
            if e["source_path"] != srcs[prefix].path:
                continue
            if fp == root or fp.startswith(root + ".") or fp.startswith(root + " item ") \
                    or root.startswith(fp + ".") or root.startswith(fp + " item "):
                out.append(e["entry_id"])
        return out

    typed_sf = srcs["typed"].doc["supersedes_fields"]
    for r in leaf_map:
        if r["disposition"] != "not_stated_superseded_in_held_table":
            continue
        m = re.search(r"supersedes_fields items? (\d+)(?: and (\d+))?", r["superseded_via"])
        ids = []
        for n in [g for g in (m.groups() if m else ()) if g]:
            text = typed_sf[int(n) - 1]
            for ctl in re.findall(r"amendment\.controls ((?:C-[A-Z\-]+(?:, | and )?)+)", text):
                for cid in re.findall(r"C-[A-Z]+(?:-[A-Z]+)*", ctl):
                    ids += [i for i in leaf_entries("typed", f"controls[{cid}]") if i not in ids]
            for p in re.findall(r"amendment\.([A-Za-z0-9_.\-]+[A-Za-z0-9_])", text):
                if p == "controls":
                    continue
                ids += [i for i in (leaf_entries("typed", p) or source_entries("typed", p)) if i not in ids]
        r["replaced_by_entries"] = ids

    additions = []
    for pa in srcs["gated"].doc["path_additions"]:
        m = re.match(r"^(\S+) of AMD-20260927-narrow\.yaml$", pa["path"])
        held = source_entries("narrow", m.group(1)) if m else leaf_entries("typed", pa["path"])
        add_ids = []
        for a in pa["additions"]:
            layer, apath = a.split(":", 1)
            add_ids += source_entries(PREFIX[layer], apath)
        if not held or not add_ids:
            raise SystemExit(f"unresolved addition group: {pa['path']}")
        additions.append({"path": pa["path"], "held_entries": held, "addition_entries": add_ids})

    fresh = yaml.safe_load((HERE / "fresh-text.yaml").read_text(encoding="utf-8"))["fresh"]
    out = {"successor_contract": {
        "fresh": fresh,
        "additions_read_together": {"text_kind": "fresh", "note": (
            "Fresh grouping, derived by build_draft.py from path_additions of AMD-20260928-gated.yaml "
            "read as a design input. Each group is read together under F-PREC."), "groups": additions},
        "transcluded": {
        "text_kind": "transcluded",
        "governed_by_plan_amendment": "DEC-20260928-2afb23 plan_amendment PA-8456b6-T1 (T1 to T5)",
        "source_commit": commit,
        "sources": {p: {"path": s.path, "blob_sha256": s.sha} for p, s in srcs.items()},
        "anchor_convention": (
            "loaded_value: the span is the string a YAML 1.1 safe loader returns for anchor.field_path from "
            "the source blob at source_commit, or its [start, end) character sub-range when char_range is "
            "given; span_sha256 is over its UTF-8 bytes (the span convention of "
            "AMD-20260927-narrow.yaml incorporates.span_hash_convention). source_bytes: the span is the exact "
            "text of the source blob from line_col_range[0:2] to line_col_range[2:4] (lines 1-based, "
            "columns 0-based characters), the value node of anchor.field_path as a YAML composer locates "
            "it; span_sha256 is over its UTF-8 bytes. In both kinds the transcluded span is the value a "
            "YAML safe loader returns for this entry's text field."),
        "entries": entries},
        "leaf_map": {"text_kind": "fresh", "note": (
            "One row per leaf of governing_text_table of AMD-20260928-gated.yaml (read as a design input, "
            "not as governing text). Each held leaf has exactly one disposition in this contract."),
            "rows": leaf_map},
    }}
    header = (
        "# =============================================================================\n"
        "# DRAFT successor-experiment contract EXP-AUXIN-edd104 (RS-B), written by\n"
        "# TASK-20260928-fa9275 in BATCH-8456b6, GOAL-AUXIN-a93442. status draft,\n"
        "# approved_by null. It authorizes no run and approves nothing.\n"
        "#\n"
        "# GENERATED by build_draft.py from fresh-text.yaml (fresh text) and byte-exact\n"
        "# spans of the held EXP-AUXIN-7e2e3d records (transcluded text, under\n"
        "# DEC-20260928-2afb23 plan_amendment PA-8456b6-T1). Fresh and transcluded\n"
        "# parts are kept apart and each is labelled by text_kind. Do not edit by hand.\n"
        "# =============================================================================\n")
    target = HERE / "draft-contract.yaml"
    target.write_text(header + yaml.safe_dump(out, sort_keys=False, allow_unicode=True, width=1 << 20),
                      encoding="utf-8")

    doc = yaml.safe_load(target.read_text(encoding="utf-8"))["successor_contract"]
    back = {"entries": doc["transcluded"]["entries"], "sources": doc["transcluded"]["sources"],
            "leaf_map": doc["leaf_map"]["rows"]}
    if doc["fresh"] != fresh:
        raise SystemExit("fresh block changed on reload")
    bad = [e["entry_id"] for e in back["entries"] if sha(e["text"].encode("utf-8")) != e["span_sha256"]]
    by_path = {s.path: s for s in srcs.values()}
    for e in back["entries"]:
        s = by_path[e["source_path"]]
        path = e["anchor"]["field_path"]
        path = path[len(s.top_key) + 1:]
        if e["anchor"]["kind"] == "loaded_value":
            v = walk(s.doc, path, False)
            cr = e["anchor"].get("char_range")
            ref = v if not cr else v[cr[0]:cr[1]]
            if ref != e["text"]:
                bad.append(e["entry_id"])
        elif line_col_slice(s.text, e["anchor"]["line_col_range"]) != e["text"]:
            bad.append(e["entry_id"])
    counts = {}
    for r in back["leaf_map"]:
        counts[r["disposition"]] = counts.get(r["disposition"], 0) + 1
    print(json.dumps({"entries": len(back["entries"]), "leaf_map_rows": len(back["leaf_map"]),
                      "dispositions": counts, "addition_groups": len(additions), "t5_failures": bad,
                      "draft_contract_sha256": sha(target.read_bytes())}, indent=1))
    return 1 if bad or counts.get("UNRESOLVED") else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
