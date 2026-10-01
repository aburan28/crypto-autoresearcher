"""Compare validator blind distributions (blind_all_cells.json, vbr.py kernel)
with the runner's results.json, per cell x convention x system kind."""
import json, sys
b = json.load(open(sys.argv[1])); r = json.load(open(sys.argv[2]))
R = {(c["n"], c["nprime"]): c for c in r["cells"]}
rows = []; agree = 0; total = 0
for c in b["cells"]:
    k = (c["n"], c["nprime"])
    for conv in ("reduced", "formal", "legacy"):
        for kind in ("semaev", "null"):
            same = c[conv][kind] == R[k][conv][kind]
            total += 1; agree += same
            rows.append(dict(cell=list(k), convention=conv, kind=kind, blind=c[conv][kind], runner=R[k][conv][kind], agree=same))
out = dict(agree=agree, total=total, rows=rows)
json.dump(out, open(sys.argv[3], "w"), indent=1)
print(f"{agree}/{total} distributions identical")
for x in rows:
    if not x["agree"]: print("DIFF", x)
