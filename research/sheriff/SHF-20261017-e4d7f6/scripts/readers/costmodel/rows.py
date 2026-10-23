#!/usr/bin/env python3
"""List every row in baselines.json carrying s_ic_* fields and test s_ic_setup == s_ic_cold - s_ic_online.
Usage: python3 -I -B rows.py <path-to-baselines.json>"""
import json, sys
d = json.load(open(sys.argv[1]))
print("schema:", d.get("schema"), "as_of:", d.get("as_of"))
def walk(obj, path):
    if isinstance(obj, dict):
        if any(k.startswith("s_ic_") for k in obj):
            yield path, obj
        for k, v in obj.items():
            yield from walk(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from walk(v, f"{path}[{i}]")
for sec in ("baselines", "other_records", "stage_results", "sizes"):
    for p, row in walk(d.get(sec), sec):
        c, o, s = row.get("s_ic_cold"), row.get("s_ic_online"), row.get("s_ic_setup")
        name = row.get("name") or row.get("producer") or row.get("id") or row.get("what") or ""
        n = row.get("n")
        diff = None
        if all(isinstance(x, (int, float)) for x in (c, o, s)):
            diff = round(s - (c - o), 6)
            rel = diff / s if s else None
        else:
            rel = None
        extra = {k: row[k] for k in row if k.startswith("s_ic_") and k not in ("s_ic_cold", "s_ic_online", "s_ic_setup", "s_ic_setup_derivation")}
        print(f"{p} n={n} name={str(name)[:70]!r}\n   cold={c} online={o} setup={s} setup-(cold-online)={diff} rel={None if rel is None else round(rel,6)} extra={extra}")
        print("   unit:", str(row.get("unit"))[:200])
