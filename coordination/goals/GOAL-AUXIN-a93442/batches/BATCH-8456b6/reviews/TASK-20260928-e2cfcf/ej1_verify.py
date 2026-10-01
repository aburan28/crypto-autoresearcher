#!/usr/bin/env python3
"""Independent EJ1 span verifier for TASK-20260928-e2cfcf (REVIEW-AUXIN-20260928-8456b6).

Written by the validator; shares no code with build_draft.py. For every item of
successor_contract.transcluded.entries of a draft file it reads the source blob
with `git show <source_commit>:<source_path>`, checks source_blob_sha256,
resolves the anchor to a concrete node path (tuple of mapping keys / list
indices), cuts the span under the declared convention, compares it with
entry.text, and hashes UTF-8 bytes against span_sha256. Overlap is checked on
concrete node ancestry per source plus char_range intersection on one node.

Usage (repository root): python3 ej1_verify.py <draft.yaml> [--json out.json]
Exit status 0 only if no finding.
"""
import hashlib
import json
import re
import subprocess
import sys

import yaml

_blobs = {}


def h(b):
    return hashlib.sha256(b).hexdigest()


def blob(commit, path):
    k = (commit, path)
    if k not in _blobs:
        raw = subprocess.run(["git", "show", f"{commit}:{path}"], check=True,
                             capture_output=True).stdout
        text = raw.decode("utf-8")
        _blobs[k] = {"raw": raw, "text": text, "doc": yaml.safe_load(text),
                     "node": yaml.compose(text)}
    return _blobs[k]


def segments(fp):
    """Split on '.' outside brackets; then each segment is key, key[sel], or
    'key item N' (possibly 'key[sel] item N')."""
    out, depth, cur = [], 0, []
    for ch in fp:
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
        if ch == "." and depth == 0:
            out.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
    out.append("".join(cur))
    parsed = []
    for s in out:
        m = re.fullmatch(r"([^\[\] ]+)(?:\[([^\]]+)\])?(?: item ([0-9]+))?", s)
        if not m:
            raise ValueError(f"unparseable segment {s!r}")
        parsed.append(m.groups())
    return parsed


def resolve(doc, fp):
    """Return (value, concrete path tuple, notes). Selector [x]: the unique list
    item that is a mapping whose 'id' equals x; if no item has id x, the unique
    item with some string value equal to x. 'item N' is 1-based."""
    cur, path, notes = doc, [], []
    for key, sel, item in segments(fp):
        if not isinstance(cur, dict) or key not in cur:
            raise KeyError(f"key {key!r} absent")
        cur = cur[key]
        path.append(key)
        if sel is not None:
            if not isinstance(cur, list):
                raise KeyError(f"selector [{sel}] on non-list")
            by_id = [i for i, it in enumerate(cur) if isinstance(it, dict) and it.get("id") == sel]
            if len(by_id) == 1:
                idx = by_id[0]
            else:
                anyv = [i for i, it in enumerate(cur) if isinstance(it, dict)
                        and sel in [v for v in it.values() if isinstance(v, str)]]
                if len(anyv) != 1:
                    raise KeyError(f"selector [{sel}] matches {len(by_id)} by id, {len(anyv)} by value")
                idx = anyv[0]
                notes.append(f"selector [{sel}] resolved by non-id value")
            cur = cur[idx]
            path.append(idx)
        if item is not None:
            n = int(item)
            if not isinstance(cur, list) or not (1 <= n <= len(cur)):
                raise KeyError(f"item {n} out of range")
            cur = cur[n - 1]
            path.append(n - 1)
    return cur, tuple(path), notes


def node_at(root, path):
    cur = root
    for p in path:
        if isinstance(p, int):
            cur = cur.value[p]
        else:
            m = [v for k, v in cur.value if k.value == p]
            if len(m) != 1:
                raise KeyError(f"node key {p!r} occurs {len(m)} times")
            cur = m[0]
    return cur


def lc_to_index(text, line, col):
    lines = text.split("\n")
    if line < 1 or line > len(lines) or col < 0 or col > len(lines[line - 1]):
        raise ValueError(f"line/col {line}:{col} out of range")
    return sum(len(x) + 1 for x in lines[:line - 1]) + col


def verify(draft_path):
    draft = yaml.safe_load(open(draft_path, encoding="utf-8"))["successor_contract"]
    tr = draft["transcluded"]
    entries = tr["entries"]
    findings, recs = [], []
    ids = [e.get("entry_id") for e in entries]
    if len(set(ids)) != len(ids):
        findings.append({"kind": "duplicate_entry_id"})
    declared_sources = {v["path"]: v["blob_sha256"] for v in tr["sources"].values()}
    for e in entries:
        r = {"entry_id": e["entry_id"], "kind": e["anchor"]["kind"], "ok": False}
        try:
            if e["source_commit"] != tr["source_commit"]:
                raise ValueError("entry source_commit differs from transcluded.source_commit")
            b = blob(e["source_commit"], e["source_path"])
            if h(b["raw"]) != e["source_blob_sha256"]:
                raise ValueError("source_blob_sha256 mismatch")
            if declared_sources.get(e["source_path"]) != e["source_blob_sha256"]:
                raise ValueError("source not in transcluded.sources with this hash")
            top = "experiment" if "specification.yaml" in e["source_path"] else "amendment"
            fp = e["anchor"]["field_path"]
            if not fp.startswith(top + "."):
                raise ValueError(f"field_path not under {top}")
            val, cpath, notes = resolve(b["doc"], fp)
            r["notes"] = notes
            r["node_path"] = [str(p) for p in cpath]
            if e["anchor"]["kind"] == "loaded_value":
                if not isinstance(val, str):
                    raise ValueError(f"loaded_value anchor resolves to {type(val).__name__}")
                cr = e["anchor"].get("char_range")
                if cr is not None:
                    a, z = cr
                    if not (0 <= a < z <= len(val)):
                        raise ValueError(f"char_range {cr} outside [0,{len(val)}]")
                    span = val[a:z]
                else:
                    span = val
            elif e["anchor"]["kind"] == "source_bytes":
                if isinstance(val, str):
                    r["notes"].append("source_bytes anchor on a string value")
                lc = e["anchor"]["line_col_range"]
                i0 = lc_to_index(b["text"], lc[0], lc[1])
                i1 = lc_to_index(b["text"], lc[2], lc[3])
                span = b["text"][i0:i1]
                n = node_at(b["node"], cpath)
                if (n.start_mark.index, n.end_mark.index) != (i0, i1):
                    raise ValueError(f"line_col_range {lc} is not the composed value node "
                                     f"[{n.start_mark.line + 1},{n.start_mark.column},"
                                     f"{n.end_mark.line + 1},{n.end_mark.column}]")
                try:
                    reloaded = yaml.safe_load(span)
                    r["reload_equals_loaded_value"] = reloaded == val
                except yaml.YAMLError as ex:
                    r["reload_equals_loaded_value"] = f"reload error: {type(ex).__name__}"
                r["multiline"] = "\n" in span
            else:
                raise ValueError("unknown anchor kind")
            r["cpath"] = cpath
            r["char_range"] = e["anchor"].get("char_range")
            r["source_path"] = e["source_path"]
            if span != e["text"]:
                raise ValueError("resolved span differs from entry.text")
            if h(span.encode("utf-8")) != e["span_sha256"]:
                raise ValueError("span_sha256 mismatch (resolved span)")
            if h(e["text"].encode("utf-8")) != e["span_sha256"]:
                raise ValueError("span_sha256 mismatch (entry.text)")
            r["ok"] = True
        except Exception as ex:  # noqa: BLE001 - every failure is a finding
            r["error"] = f"{type(ex).__name__}: {ex}"
            findings.append({"kind": "entry_failure", "entry_id": e["entry_id"], "error": r["error"]})
        recs.append(r)

    ok = [r for r in recs if r["ok"]]
    overlaps = []
    for i, a in enumerate(ok):
        for c in ok[i + 1:]:
            if a["source_path"] != c["source_path"]:
                continue
            pa, pc = a["cpath"], c["cpath"]
            if pa == pc:
                ra, rc = a["char_range"], c["char_range"]
                if ra is None or rc is None or (ra[0] < rc[1] and rc[0] < ra[1]):
                    overlaps.append([a["entry_id"], c["entry_id"], "same node"])
            elif pc[:len(pa)] == pa or pa[:len(pc)] == pc:
                overlaps.append([a["entry_id"], c["entry_id"], "ancestor"])
    for o in overlaps:
        findings.append({"kind": "overlap", "pair": o})
    for r in recs:
        r.pop("cpath", None)
    summary = {
        "draft_sha256": h(open(draft_path, "rb").read()),
        "entries": len(entries),
        "verified": len(ok),
        "by_kind": {k: sum(1 for r in recs if r["kind"] == k) for k in ("loaded_value", "source_bytes")},
        "char_range_entries": sum(1 for e in entries if "char_range" in e["anchor"]),
        "source_bytes_multiline": sum(1 for r in recs if r.get("multiline")),
        "source_bytes_reload_not_equal": [r["entry_id"] for r in recs
                                          if r["kind"] == "source_bytes" and r.get("reload_equals_loaded_value") is not True],
        "selector_by_non_id": [r["entry_id"] for r in recs if r.get("notes")],
        "overlap_pairs": len(overlaps),
        "findings": findings,
    }
    return summary, recs


if __name__ == "__main__":
    s, recs = verify(sys.argv[1])
    if "--json" in sys.argv:
        json.dump({"summary": s, "entries": recs}, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1)
    print(json.dumps({k: v for k, v in s.items() if k != "findings"}, indent=1))
    print("findings:", len(s["findings"]))
    for f in s["findings"][:20]:
        print(" ", json.dumps(f))
    sys.exit(1 if s["findings"] else 0)
