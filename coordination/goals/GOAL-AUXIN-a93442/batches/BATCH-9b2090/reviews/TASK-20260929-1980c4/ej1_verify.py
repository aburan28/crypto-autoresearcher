#!/usr/bin/env python3
"""Independent EJ1 span-fidelity verifier for TASK-20260929-1980c4.

Does not call build_successor.py's verify path. Resolves each anchor against
git show <source_commit>:<source_path> using its own walk/selector logic.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[7]
DRAFT = REPO / (
    "coordination/goals/GOAL-AUXIN-a93442/batches/BATCH-9b2090/"
    "design/TASK-20260928-4d6266/draft-contract.yaml"
)
SOURCE_COMMIT = "bb75521b79b8b5bdbe075ab6b85f7af6d2c0867a"
# Replaced source roots from replacement_table / builder_guard (field paths
# under the held files). Checked so no entry's anchor lies inside them.
REPLACED_ROOTS = [
    ("experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260926-typed.yaml",
     "amendment.change.D8_custody.trial_plan"),
    ("experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260926-typed.yaml",
     "amendment.change.D8_custody.manifest"),
    ("experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260926-typed.yaml",
     "amendment.change.D10_additivity.rule"),
    ("experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260926-typed.yaml",
     "amendment.invalidation_rules item 10"),
    ("experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260927-narrow.yaml",
     "amendment.span_rules[TP-FOUR].replacement"),
    ("experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260927-narrow.yaml",
     "amendment.span_rules[MAN-FOUR].replacement"),
    ("experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260927-narrow.yaml",
     "amendment.span_rules[MAN-DIRTY].replacement"),
    ("experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260927-narrow.yaml",
     "amendment.span_rules[ADM-7].replacement"),
    ("experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260927-narrow.yaml",
     "amendment.custody_consequences"),
    ("experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260927-narrow.yaml",
     "amendment.corrective.custody.invalidation_rules_added"),
    ("experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260928-gated.yaml",
     "amendment.custody_additions"),
]


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def git_show(commit: str, path: str) -> bytes:
    return subprocess.run(
        ["git", "show", f"{commit}:{path}"],
        cwd=REPO, check=True, capture_output=True,
    ).stdout


def split_path(p: str):
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


SEG = re.compile(
    r"^(?P<key>[^\[ ]+)(?:\[(?P<sel>[^\]]+)\])?(?: item (?P<item>\d+))?$"
)


def _sel_loaded(items, sel):
    """Select list item by unique id, else by unique string value match."""
    by_id = []
    by_val = []
    for i, it in enumerate(items):
        if isinstance(it, dict):
            if it.get("id") == sel:
                by_id.append(i)
            vals = [v for v in it.values() if isinstance(v, str) and v == sel]
            if vals:
                by_val.append(i)
    if len(by_id) == 1:
        return by_id[0]
    if len(by_val) == 1:
        return by_val[0]
    raise KeyError(f"selector {sel!r} not unique (id={by_id}, val={by_val})")


def _sel_node(items, sel):
    by_id, by_val = [], []
    for i, it in enumerate(items):
        if not isinstance(it, yaml.MappingNode):
            continue
        for k, v in it.value:
            if not isinstance(v, yaml.ScalarNode):
                continue
            if k.value == "id" and v.value == sel:
                by_id.append(i)
            if v.value == sel:
                by_val.append(i)
    if len(by_id) == 1:
        return by_id[0]
    # unique string value among mapping children
    uniq = [i for i in by_val if by_val.count(i) == 1]
    # Prefer a single item that uniquely carries the string as some field value
    counts = {}
    for i in by_val:
        counts[i] = counts.get(i, 0) + 1
    candidates = [i for i, c in counts.items() if c >= 1]
    # Deduplicate while preserving: if exactly one mapping contains sel as a value
    seen = []
    for i in by_val:
        if i not in seen:
            seen.append(i)
    if len(by_id) == 1:
        return by_id[0]
    if len(seen) == 1:
        return seen[0]
    raise KeyError(f"node selector {sel!r} not unique")


def walk_loaded(root, path: str):
    cur = root
    for seg in split_path(path):
        m = SEG.match(seg)
        if not m:
            raise KeyError(seg)
        key, sel, item = m.group("key"), m.group("sel"), m.group("item")
        cur = cur[key]
        if sel is not None:
            cur = cur[_sel_loaded(cur, sel)]
        if item is not None:
            cur = cur[int(item) - 1]
    return cur


def walk_node(root, path: str):
    cur = root
    for seg in split_path(path):
        m = SEG.match(seg)
        if not m:
            raise KeyError(seg)
        key, sel, item = m.group("key"), m.group("sel"), m.group("item")
        nxt = [v for k, v in cur.value if k.value == key]
        if not nxt:
            raise KeyError(key)
        cur = nxt[0]
        if sel is not None:
            cur = cur.value[_sel_node(cur.value, sel)]
        if item is not None:
            cur = cur.value[int(item) - 1]
    return cur


def line_col_slice(text: str, lc):
    lines = text.split("\n")
    start = sum(len(x) + 1 for x in lines[: lc[0] - 1]) + lc[1]
    end = sum(len(x) + 1 for x in lines[: lc[2] - 1]) + lc[3]
    return text[start:end], start, end


def under_path(fp: str, root: str) -> bool:
    return (
        fp == root
        or fp.startswith(root + ".")
        or fp.startswith(root + " item ")
        or fp.startswith(root + "[")
    )


def node_ancestry_range(node):
    return node.start_mark.index, node.end_mark.index


def ranges_overlap(a, b):
    return not (a[1] <= b[0] or b[1] <= a[0])


def verify(entries):
    failures = []
    blob_cache = {}
    resolved = []  # (source_path, entry_id, kind, byte_range_or_None, field_path)

    for e in entries:
        eid = e["entry_id"]
        sp = e["source_path"]
        sc = e["source_commit"]
        if sc != SOURCE_COMMIT:
            failures.append({"entry_id": eid, "kind": "source_commit_mismatch"})
            continue
        key = (sc, sp)
        if key not in blob_cache:
            raw = git_show(sc, sp)
            blob_cache[key] = {
                "raw": raw,
                "sha": sha256_bytes(raw),
                "text": raw.decode("utf-8"),
            }
            composed = yaml.compose(blob_cache[key]["text"])
            # top mapping
            blob_cache[key]["doc"] = yaml.safe_load(blob_cache[key]["text"])
            blob_cache[key]["node_root"] = composed
        blob = blob_cache[key]
        if blob["sha"] != e["source_blob_sha256"]:
            failures.append({
                "entry_id": eid,
                "kind": "source_blob_sha256_mismatch",
                "recomputed": blob["sha"],
                "stated": e["source_blob_sha256"],
            })
            continue

        anchor = e["anchor"]
        fp = anchor["field_path"]
        kind = anchor["kind"]
        top = fp.split(".", 1)[0]
        path = fp[len(top) + 1 :]
        top_doc = blob["doc"][top]
        top_node = [v for k, v in blob["node_root"].value if k.value == top][0]

        try:
            if kind == "loaded_value":
                val = walk_loaded(top_doc, path)
                if not isinstance(val, str):
                    failures.append({"entry_id": eid, "kind": "loaded_value_not_str"})
                    continue
                cr = anchor.get("char_range")
                text = val if cr is None else val[cr[0] : cr[1]]
                byte_range = None
            elif kind == "source_bytes":
                node = walk_node(top_node, path)
                text, start, end = line_col_slice(blob["text"], anchor["line_col_range"])
                # Confirm line_col matches composer marks
                if (node.start_mark.line + 1, node.start_mark.column,
                        node.end_mark.line + 1, node.end_mark.column) != tuple(
                    anchor["line_col_range"]
                ):
                    failures.append({
                        "entry_id": eid,
                        "kind": "line_col_mismatch",
                        "composer": [
                            node.start_mark.line + 1,
                            node.start_mark.column,
                            node.end_mark.line + 1,
                            node.end_mark.column,
                        ],
                        "stated": list(anchor["line_col_range"]),
                    })
                    continue
                if text != blob["text"][node.start_mark.index : node.end_mark.index]:
                    failures.append({"entry_id": eid, "kind": "line_col_vs_index_mismatch"})
                    continue
                byte_range = (node.start_mark.index, node.end_mark.index)
            else:
                failures.append({"entry_id": eid, "kind": "unknown_anchor_kind", "value": kind})
                continue
        except Exception as ex:  # noqa: BLE001 — report as unresolvable
            failures.append({
                "entry_id": eid,
                "kind": "unresolvable_anchor",
                "error": f"{type(ex).__name__}: {ex}",
            })
            continue

        if text != e["text"]:
            failures.append({
                "entry_id": eid,
                "kind": "text_mismatch",
                "recomputed_sha": sha256_bytes(text.encode("utf-8")),
                "stated_sha": e["span_sha256"],
            })
            continue
        recomputed = sha256_bytes(text.encode("utf-8"))
        if recomputed != e["span_sha256"]:
            failures.append({
                "entry_id": eid,
                "kind": "span_sha256_mismatch",
                "recomputed": recomputed,
                "stated": e["span_sha256"],
            })
            continue

        # replaced-path guard
        for rsp, root in REPLACED_ROOTS:
            if sp == rsp and under_path(fp, root):
                failures.append({
                    "entry_id": eid,
                    "kind": "entry_inside_replaced_path",
                    "field_path": fp,
                    "replaced_root": root,
                })

        resolved.append({
            "entry_id": eid,
            "source_path": sp,
            "kind": kind,
            "field_path": fp,
            "byte_range": byte_range,
            "char_range": anchor.get("char_range"),
        })

    # pairwise non-overlap per source: ancestry ranges for source_bytes;
    # char_range intersection within same field for loaded_value.
    by_source = {}
    for r in resolved:
        by_source.setdefault(r["source_path"], []).append(r)
    for sp, group in by_source.items():
        # source_bytes byte ranges
        sb = [g for g in group if g["byte_range"] is not None]
        for i in range(len(sb)):
            for j in range(i + 1, len(sb)):
                if ranges_overlap(sb[i]["byte_range"], sb[j]["byte_range"]):
                    # proper containment of YAML nodes is ancestry, not overlap
                    a, b = sb[i]["byte_range"], sb[j]["byte_range"]
                    contained = (a[0] <= b[0] and b[1] <= a[1]) or (
                        b[0] <= a[0] and a[1] <= b[1]
                    )
                    if not contained:
                        failures.append({
                            "kind": "overlap_source_bytes",
                            "a": sb[i]["entry_id"],
                            "b": sb[j]["entry_id"],
                            "source_path": sp,
                        })
        # loaded_value same field_path with intersecting char_range or both whole
        lv = [g for g in group if g["kind"] == "loaded_value"]
        for i in range(len(lv)):
            for j in range(i + 1, len(lv)):
                if lv[i]["field_path"] != lv[j]["field_path"]:
                    continue
                ci, cj = lv[i]["char_range"], lv[j]["char_range"]
                if ci is None and cj is None:
                    failures.append({
                        "kind": "overlap_loaded_whole",
                        "a": lv[i]["entry_id"],
                        "b": lv[j]["entry_id"],
                    })
                elif ci is not None and cj is not None:
                    if ranges_overlap(tuple(ci), tuple(cj)):
                        failures.append({
                            "kind": "overlap_loaded_char_range",
                            "a": lv[i]["entry_id"],
                            "b": lv[j]["entry_id"],
                        })

    return {
        "entries_checked": len(entries),
        "failures": failures,
        "ok": len(failures) == 0,
        "resolved_ok": len(resolved),
    }


def main():
    draft = yaml.safe_load(DRAFT.read_text())
    entries = draft["successor_contract"]["transcluded"]["entries"]
    result = verify(entries)
    out = Path(__file__).with_name("ej1_result.json")
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"ok": result["ok"], "failure_kinds": sorted({f["kind"] for f in result["failures"]})}))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
