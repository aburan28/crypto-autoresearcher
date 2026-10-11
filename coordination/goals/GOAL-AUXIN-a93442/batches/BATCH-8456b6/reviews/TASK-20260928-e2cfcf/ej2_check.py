#!/usr/bin/env python3
"""Independent EJ2 checker for TASK-20260928-e2cfcf (REVIEW-AUXIN-20260928-8456b6).

Shares no code with build_draft.py. Held side: the effective value of every row
of governing_text_table of AMD-20260928-gated is derived from the held
supersession texts themselves (narrow supersedes_fields, custody_consequences,
span_rules and incorporates.span_hash_convention; gated supersedes_fields and
gated_span_rules), not from leaf_map. Draft side: each stated row is composed
from the entries it names (outside segments and span-position rows joined by
character position; structured leaves tiled node by node), and compared with
the held effective value. Superseded rows are resolved from the cited typed
supersedes_fields item(s).

Usage (repository root): python3 ej2_check.py <draft.yaml> <out.json> [--drop ROW_INDEX:ENTRY_ID]
"""
import copy
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ej1_verify import resolve  # noqa: E402  (validator's own resolver)

COMMIT = "bb75521b79b8b5bdbe075ab6b85f7af6d2c0867a"
PATHS = {"v1": "experiments/EXP-AUXIN-7e2e3d/specification.yaml",
         "typed": "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260926-typed.yaml",
         "narrow": "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260927-narrow.yaml",
         "gated": "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260928-gated.yaml"}
OWN = {"v1": "v1", "typed": "typed-by-hash", "narrow": "narrow-by-hash", "gated": "gated"}
TOP = {"v1": "experiment", "typed": "amendment", "narrow": "amendment", "gated": "amendment"}


def sha(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def canon(v):
    return v if isinstance(v, str) else json.dumps(v, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


SRC = {}
for p, path in PATHS.items():
    raw = subprocess.run(["git", "show", f"{COMMIT}:{path}"], check=True, capture_output=True).stdout
    SRC[p] = yaml.safe_load(raw.decode("utf-8"))[TOP[p]]
PREFIX_OF_PATH = {v: k for k, v in PATHS.items()}
N, G, TY = SRC["narrow"], SRC["gated"], SRC["typed"]


def strip_paren(f):
    return re.sub(r" \(.*\)$", "", f)


def held(prefix, path):
    return resolve({TOP[prefix]: SRC[prefix]}, f"{TOP[prefix]}.{path}")


# ---- held supersession derived from the held texts -------------------------
WHOLE = {}   # (prefix, path) -> (prefix, path)
for s in N["supersedes_fields"]:
    if s["extent"] == "whole":
        WHOLE[("typed", strip_paren(s["field"]))] = ("narrow", s["replaced_by"])
for s in G["supersedes_fields"]:
    if s["extent"] == "whole" and s.get("replaced_by"):
        pre = {"typed-by-hash": "typed", "narrow-by-hash": "narrow"}[s["layer_superseded"]]
        WHOLE[(pre, strip_paren(s["field"]))] = ("gated", s["replaced_by"])

SPANS = {}   # (prefix, base) -> {id: rule}
narrow_span_ids = set()
for s in N["supersedes_fields"] + N["custody_consequences"]["fields"]:
    if s["extent"].startswith("span"):
        narrow_span_ids |= set(re.findall(r"[A-Z0-9]+(?:-[A-Z0-9]+)+", s["extent"]))
for r in N["span_rules"]:
    repl, loc = r["replacement"], ("narrow", f"span_rules[{r['id']}].replacement")
    if (loc[0], loc[1]) in WHOLE:
        loc = WHOLE[loc]
        repl = held(*loc)[0]
    SPANS.setdefault(("typed", r["field"]), {})[r["id"]] = dict(r, eff=repl, eff_loc=loc,
                                                                listed=r["id"] in narrow_span_ids)
for r in G["gated_span_rules"]:
    pre = PREFIX_OF_PATH[r["file"]]
    SPANS.setdefault((pre, r["field"]), {})[r["id"]] = dict(r, eff=r["replacement"],
                                                            eff_loc=("gated", f"gated_span_rules[{r['id']}].replacement"),
                                                            listed=True)


def locate(value, rule):
    a = value.find(rule["from"])
    if a < 0 or value.find(rule["from"], a + 1) >= 0:
        raise ValueError(f"from text of {rule['id']} not unique")
    t = value.find(rule["through"], a)
    if t < 0:
        raise ValueError(f"through text of {rule['id']} not found")
    b = t + len(rule["through"])
    if sha(value[a:b]) != rule["replaced_span_sha256"]:
        raise ValueError(f"replaced_span_sha256 of {rule['id']} fails")
    return a, b


def chase(prefix, path):
    chain = []
    while (prefix, path) in WHOLE:
        chain.append(f"{prefix}:{path}")
        prefix, path = WHOLE[(prefix, path)]
    return prefix, path, chain


# ---- draft ------------------------------------------------------------------
def load_draft(p):
    return yaml.safe_load(open(p, encoding="utf-8"))["successor_contract"]


def entry_value(e):
    if e["anchor"]["kind"] == "loaded_value":
        return e["text"]
    return yaml.safe_load(" " * e["anchor"]["line_col_range"][1] + e["text"])


def entry_loc(e):
    pre = PREFIX_OF_PATH[e["source_path"]]
    _, cp, _ = resolve({TOP[pre]: SRC[pre]}, e["anchor"]["field_path"])
    return pre, cp


def tile(target_pre, target_cp, H, entries, exclude=()):
    """Cover H (value at target_cp in target_pre) with entries; exclude: concrete
    sub-paths removed from H. Returns dict of problems."""
    by = {}
    out = {"foreign": [], "ancestor": [], "mismatch": [], "uncovered": [], "dup": [], "order_ok": True}
    for e in entries:
        pre, cp = entry_loc(e)
        if pre != target_pre:
            out["foreign"].append(e["entry_id"])
            continue
        if cp[:len(target_cp)] != target_cp:
            if target_cp[:len(cp)] == cp:
                out["ancestor"].append(e["entry_id"])
                v = entry_value(e)
                for k in target_cp[len(cp):]:
                    v = v[k]
                out["ancestor_value_equal"] = v == H
            else:
                out["foreign"].append(e["entry_id"])
            continue
        if "char_range" in e["anchor"]:
            out["foreign"].append(e["entry_id"] + " (char_range in tiled row)")
            continue
        if cp in by:
            out["dup"].append(e["entry_id"])
        by[cp] = e
    order = []

    def cover(v, cp):
        if cp in exclude:
            return
        if cp in by:
            order.append(by[cp]["entry_id"])
            if entry_value(by[cp]) != v:
                out["mismatch"].append(by[cp]["entry_id"])
            return
        if isinstance(v, dict):
            for k in v:
                cover(v[k], cp + (k,))
        elif isinstance(v, list):
            for i, x in enumerate(v):
                cover(x, cp + (i,))
        else:
            out["uncovered"].append("/".join(map(str, cp)))
    if not (out["ancestor"] and not by):
        cover(H, target_cp)
    listed = [e["entry_id"] for e in entries if e["entry_id"] in order]
    out["order_ok"] = listed == order
    out["unused"] = [e["entry_id"] for e in entries if e["entry_id"] not in order
                     and e["entry_id"] not in out["foreign"] + out["ancestor"]]
    return out


def main(draft_path, out_path, drop=None):
    d = load_draft(draft_path)
    E = {e["entry_id"]: e for e in d["transcluded"]["entries"]}
    rows = d["leaf_map"]["rows"]
    if drop:
        ri, eid = drop
        rows = copy.deepcopy(rows)
        rows[ri]["entries"] = [x for x in rows[ri]["entries"] if x != eid]
    table = G["governing_text_table"]
    res = {"bijection": {}, "stated": [], "superseded": [], "envelope": 0, "findings": []}

    # bijection
    tk = [(r["field"], r["layer"]) for r in table]
    lk = [(r["held_leaf"], r["held_governing_layer"]) for r in rows]
    res["bijection"] = {"table_rows": len(tk), "leaf_map_rows": len(lk),
                        "table_dup": len(tk) - len(set(tk)), "map_dup": len(lk) - len(set(lk)),
                        "table_minus_map": sorted(set(tk) - set(lk)), "map_minus_table": sorted(set(lk) - set(tk)),
                        "same_order": tk == lk,
                        "one_disposition_each": all(isinstance(r.get("disposition"), str) for r in rows)}
    if not (len(tk) == len(lk) and set(tk) == set(lk) and len(set(lk)) == len(lk)):
        res["findings"].append({"joint": "EJ2", "kind": "bijection"})

    span_rows = {}
    for r in rows:
        if "position_in" in r:
            span_rows.setdefault(r["position_in"], []).append(r)

    for idx, (t, r) in enumerate(zip(table, rows)):
        f, layer = t["field"], t["layer"]
        pre, rest = f.split(":", 1)
        disp = r["disposition"]
        if disp == "not_stated_envelope_or_layering":
            res["envelope"] += 1
            continue
        if disp == "not_stated_superseded_in_held_table":
            res["superseded"].append({"row": idx, "held_leaf": f, "via": t["via"],
                                      "replaced_by_entries": r["replaced_by_entries"]})
            continue
        rec = {"row": idx, "held_leaf": f, "layer": layer, "entries": r.get("entries") or []}
        try:
            ents = [E[x] for x in (r.get("entries") or [])]
            if not ents:
                raise ValueError("stated row lists no entries")
            m_out = re.fullmatch(r"(.*) outside spans? (.+)", rest)
            m_span = None if m_out else re.fullmatch(r"(.*) span (\S+)", rest)
            m_exc = re.fullmatch(r"(.*) except (?:item (\d+))?\.?(.*)", rest)
            if m_span:
                base, sid = m_span.groups()
                rule = SPANS[(pre, base)][sid]
                a, b = locate(held(pre, base)[0], rule)
                composed = "".join(e["text"] for e in ents)
                rec.update(kind="span", held_sha=sha(rule["eff"]), composed_sha=sha(composed),
                           range_ok=r.get("replaces_char_range") == [a, b],
                           position_ok=r.get("position_in") == f"{pre}:{base}",
                           replacement_source=f"{rule['eff_loc'][0]}:{rule['eff_loc'][1]}")
                rec["ok"] = composed == rule["eff"] and rec["range_ok"] and rec["position_ok"]
            elif m_out:
                base, ids = m_out.group(1), [s.strip() for s in m_out.group(2).split(",")]
                V = held(pre, base)[0]
                rules = SPANS[(pre, base)]
                if set(ids) != set(rules):
                    raise ValueError(f"outside ids {ids} vs held span rules {sorted(rules)}")
                cuts = sorted((locate(V, rules[i]), i) for i in ids)
                full, pos, segs = "", 0, []
                for (a, b), i in cuts:
                    if a > pos:
                        segs.append([pos, a])
                    full += V[pos:a] + rules[i]["eff"]
                    pos = b
                full += V[pos:]
                if pos < len(V):
                    segs.append([pos, len(V)])
                own = [e["anchor"].get("char_range") for e in ents]
                pieces = [(e["anchor"]["char_range"][0], e["text"]) for e in ents]
                for sr in span_rows.get(f"{pre}:{base}", []):
                    pieces += [(sr["replaces_char_range"][0], "".join(E[x]["text"] for x in sr["entries"]))]
                composed = "".join(txt for _, txt in sorted(pieces))
                rec.update(kind="outside+spans", held_sha=sha(full), composed_sha=sha(composed),
                           segments_ok=own == segs, held_segments=segs, draft_segments=own,
                           span_rows_at_position=[sr["held_leaf"] for sr in span_rows.get(f"{pre}:{base}", [])])
                rec["ok"] = composed == full and own == segs
            else:
                exclude = ()
                path = rest
                if m_exc:
                    path = m_exc.group(1)
                tp, tpath, chain = chase(pre, path)
                H, tcp, _ = held(tp, tpath)
                if m_exc:
                    item, sub = m_exc.group(2), m_exc.group(3)
                    sub_t = tuple(sub.split(".")) if sub else ()
                    exclude = {tcp + ((int(item) - 1,) if item else ()) + sub_t}
                inner = []
                for (sp, base), rules in SPANS.items():
                    for rid, rule in rules.items():
                        lp, lpath = rule["eff_loc"]
                        _, lcp, _ = held(lp, lpath)
                        if lp == tp and lcp[:len(tcp)] == tcp and lcp != tcp:
                            inner.append(lcp)
                tl = tile(tp, tcp, H, ents, exclude)
                uncovered_inner = [u for u in tl["uncovered"]
                                   if any("/".join(map(str, c)) == u for c in inner)]
                rec.update(kind="except" if m_exc else "whole", target=f"{tp}:{tpath}", chain=chain,
                           held_sha=sha(canon(H)), tiling=tl, uncovered_are_span_positions=uncovered_inner,
                           note=r.get("note"))
                clean = not (tl["foreign"] or tl["mismatch"] or tl["dup"] or tl["unused"])
                rec["ok"] = clean and not tl["ancestor"] and not tl["uncovered"] and tl["order_ok"]
                rec["ok_modulo_note"] = clean and tl["order_ok"] and (
                    (tl["ancestor"] and not tl["uncovered"] and tl.get("ancestor_value_equal")) or
                    (tl["uncovered"] and set(tl["uncovered"]) == set(uncovered_inner)))
                rec["layer_consistent"] = OWN[tp] == layer or bool(m_exc)
        except Exception as ex:  # noqa: BLE001
            rec.update(ok=False, error=f"{type(ex).__name__}: {ex}")
        res["stated"].append(rec)

    # ---- superseded rows: independent resolution of the cited typed items ----
    sf = TY["supersedes_fields"]
    stated_by_leaf = {r["held_leaf"]: r for r in rows if r["disposition"] == "stated"}

    def entries_for_typed_path(p):
        """Entries a held reference amendment.<p> reads in the combined text:
        every stated leaf_map row whose held leaf is typed:p or under it, taken
        in table order (their entries include narrow/gated replacements)."""
        out = []
        for t, r in zip(table, rows):
            h = t["field"]
            if r["disposition"] != "stated" or not h.startswith("typed:"):
                continue
            hp = h[6:]
            hp_base = re.split(r" (?:span|outside|except) ", hp)[0]
            if hp_base == p or hp_base.startswith(p + ".") or hp_base.startswith(p + "[") or hp_base.startswith(p + " item "):
                out += [x for x in (r.get("entries") or []) if x not in out]
        return out

    for s in res["superseded"]:
        m = re.search(r"supersedes_fields items? (\d+)(?: and (\d+))?", s["via"])
        items = [int(x) for x in m.groups() if x] if m else []
        names, named_other = [], []
        for n in items:
            txt = sf[n - 1]
            rhs = txt.split(" -- ", 1)[1] if " -- " in txt else txt
            for grp in re.findall(r"amendment\.controls ((?:C-[A-Z]+(?:-[A-Z]+)*(?:, | and )?)+)", rhs):
                names += [f"controls[{c}]" for c in re.findall(r"C-[A-Z]+(?:-[A-Z]+)*", grp)]
            for p in re.findall(r"amendment\.([A-Za-z0-9_\-]+(?:\.[A-Za-z0-9_\-]+)*)", rhs):
                if p != "controls":
                    names.append(p)
            for c in re.findall(r"(?<!amendment\.controls )\bcontrol (C-[A-Z]+(?:-[A-Z]+)*)", rhs):
                named_other.append(f"controls[{c}]")
        expect = []
        for p in names:
            expect += [x for x in entries_for_typed_path(p) if x not in expect]
        expect_plus = list(expect)
        for p in named_other:
            expect_plus += [x for x in entries_for_typed_path(p) if x not in expect_plus]
        got = s["replaced_by_entries"]
        s.update(cited_items=items, cited_text=[sf[n - 1] for n in items], amendment_path_names=names,
                 other_named_fields=named_other,
                 set_equal_amendment_paths=set(got) == set(expect), order_equal_amendment_paths=got == expect,
                 set_equal_including_other_named=set(got) == set(expect_plus),
                 missing_vs_other_named=[x for x in expect_plus if x not in got],
                 extra=[x for x in got if x not in expect_plus])
        del s["replaced_by_entries"]
        s["replaced_by_count"] = len(got)

    # entries not assigned by any row / assigned by several rows
    assign = {}
    for r in rows:
        for x in (r.get("entries") or []):
            assign.setdefault(x, []).append(r["held_leaf"])
    res["entries_unassigned"] = [x for x in E if x not in assign]
    res["entries_assigned_by_several_rows"] = {x: v for x, v in assign.items() if len(v) > 1}
    res["summary"] = {
        "stated_rows": len(res["stated"]),
        "stated_ok": sum(1 for s in res["stated"] if s.get("ok")),
        "stated_ok_modulo_note": [s["held_leaf"] for s in res["stated"] if not s.get("ok") and s.get("ok_modulo_note")],
        "stated_fail": [s["held_leaf"] for s in res["stated"] if not s.get("ok") and not s.get("ok_modulo_note")],
        "superseded_rows": len(res["superseded"]),
        "superseded_amendment_path_set_equal": sum(1 for s in res["superseded"] if s["set_equal_amendment_paths"]),
        "superseded_amendment_path_order_equal": sum(1 for s in res["superseded"] if s["order_equal_amendment_paths"]),
        "superseded_missing_other_named": [s["held_leaf"] for s in res["superseded"] if s["missing_vs_other_named"]],
        "superseded_empty": [s["held_leaf"] for s in res["superseded"] if s["replaced_by_count"] == 0],
        "envelope_rows": res["envelope"],
        "entries_unassigned": len(res["entries_unassigned"]),
        "entries_assigned_by_several_rows": len(res["entries_assigned_by_several_rows"]),
    }
    json.dump(res, open(out_path, "w"), indent=1, ensure_ascii=False)
    print(json.dumps(res["bijection"], indent=1))
    print(json.dumps(res["summary"], indent=1))
    return res


if __name__ == "__main__":
    drop = None
    if "--drop" in sys.argv:
        a, b = sys.argv[sys.argv.index("--drop") + 1].split(":")
        drop = (int(a), b)
    main(sys.argv[1], sys.argv[2], drop)
