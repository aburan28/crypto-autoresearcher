#!/usr/bin/env python3
"""Find the r24/r26/r28 slugs in the registry blob and the amendment's cited sources (read via
git cat-file at b4f056101), and compare p, a, b, order, generator with the frozen specs.
(SHF-20261021-477d51 receipts reader)"""
import json, sys
blobdir, specdir = sys.argv[1], sys.argv[2]
want = {"r24": "icv1-fp24-tm5099-a6f137c6", "r26": "icv1-fp26-tm1775-7e8fb6df", "r28": "icv1-fp28-t28201-65099091"}
def walk(o, slug, path=""):
    if isinstance(o, dict):
        if slug in json.dumps(o)[:0] or o.get("slug") == slug or o.get("name") == slug or o.get("icv1_slug") == slug:
            yield path, o
        for k, v in o.items():
            yield from walk(v, slug, path + "/" + str(k))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from walk(v, slug, path + "[%d]" % i)
def ints(o, acc):
    if isinstance(o, dict):
        for k, v in o.items():
            ints(v, acc) if isinstance(v, (dict, list)) else acc.append((k, v))
    elif isinstance(o, list):
        for v in o:
            ints(v, acc) if isinstance(v, (dict, list)) else acc.append(("", v))
    return acc
def num(v):
    if isinstance(v, int): return v
    if isinstance(v, str):
        try: return int(v, 16) if v.startswith("0x") else int(v)
        except ValueError: return None
    return None
for s, slug in want.items():
    sp = json.load(open(f"{specdir}/{s}.json"))["workloads"]["curves"][0]
    need = {"p": sp["p"], "a": sp["a"], "b": sp["b"], "r": sp["r"], "gx": sp["gx"], "gy": sp["gy"]}
    for name in ("registry.json", "prime_curves.json", "generated.json"):
        doc = json.load(open(f"{blobdir}/{name}"))
        hits = list(walk(doc, slug))
        for path, o in hits[:2]:
            vals = {num(v) for _, v in ints(o, []) if num(v) is not None}
            present = {k: (v in vals) for k, v in need.items()}
            print(s, name, path[:60], "all_spec_values_present=%s" % all(present.values()), {k: v for k, v in present.items() if not v})
        if not hits:
            print(s, name, "slug not found")
