"""AMD-20261002-280481 A-3: every top-level function, class and constant of the archived
analyze_relcensus.py (96d3b2df) against the A-3 copy, by source text of each top-level node."""
import ast, hashlib, json, sys

def nodes(path):
    src = open(path).read()
    tree = ast.parse(src)
    out = {}
    doc = ast.get_docstring(tree, clean=False)
    out["<module docstring>"] = ("docstring", doc)
    for n in tree.body:
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            out[n.name] = ("class" if isinstance(n, ast.ClassDef) else "function", ast.get_source_segment(src, n))
        elif isinstance(n, (ast.Assign, ast.AnnAssign)):
            tg = n.targets if isinstance(n, ast.Assign) else [n.target]
            for t in tg:
                for nm in ([t] if isinstance(t, ast.Name) else getattr(t, "elts", [])):
                    out[nm.id] = ("constant", ast.get_source_segment(src, n))
        elif isinstance(n, (ast.Import, ast.ImportFrom)):
            out["<import> " + ast.get_source_segment(src, n)] = ("import", ast.get_source_segment(src, n))
        elif isinstance(n, ast.If):
            out["<if> " + ast.get_source_segment(src, n).splitlines()[0]] = ("statement", ast.get_source_segment(src, n))
    return out

old_p, new_p, out_p = sys.argv[1:4]
o, n = nodes(old_p), nodes(new_p)
h = lambda s: hashlib.sha256((s or "").encode()).hexdigest()
items = []
for name in list(o) + [k for k in n if k not in o]:
    ko, so = o.get(name, (None, None))
    kn, sn = n.get(name, (None, None))
    st = "added" if name not in o else "removed" if name not in n else ("unchanged" if so == sn else "changed")
    items.append({"name": name, "kind": kn or ko, "status": st, "old_sha256": h(so) if name in o else None,
                  "new_sha256": h(sn) if name in n else None})
summ = {}
for it in items:
    summ[it["status"]] = summ.get(it["status"], 0) + 1
json.dump({"what": "AMD-20261002-280481 A-3 function diff (top-level nodes, source-text equality)",
           "old": {"path": old_p, "sha256": hashlib.sha256(open(old_p, "rb").read()).hexdigest()},
           "new": {"path": new_p, "sha256": hashlib.sha256(open(new_p, "rb").read()).hexdigest()},
           "summary": summ, "changed_or_added": [i["name"] for i in items if i["status"] != "unchanged"],
           "items": items}, open(out_p, "w"), indent=1)
print(json.dumps(summ), [i["name"] for i in items if i["status"] != "unchanged"])
