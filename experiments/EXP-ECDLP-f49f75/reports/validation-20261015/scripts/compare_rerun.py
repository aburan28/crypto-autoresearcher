import json, sys, statistics
d, rr = sys.argv[1], sys.argv[2]
rec = {}
for r in ("01", "02", "03"):
    for l in open(f"{d}/runs/RUN-ECDLP-f49f75-{r}/raw-result.jsonl"):
        x = json.loads(l)
        if r == "01" and x["m"] == 2 and x["L"] >= 8:  # AMD-02 excluded; RUN-03 supersedes
            continue
        rec[(x["m"], x["L"], x["inst"])] = (r, x)
new = {(x["m"], x["L"], x["inst"]): x for x in map(json.loads, open(rr))}
DET = ("status", "vdim", "gb_size", "gb_maxdeg", "planted_in_variety", "fb_size", "group_ops", "decompositions")
mism, ncmp = [], 0
for k, x in sorted(new.items()):
    run, y = rec[k]
    for f in ("seed", "p", "b", "chain_c", "kind"):
        if x[f] != y[f]: mism.append((k, f))
    if set(x["results"]) != set(y["results"]): mism.append((k, "keys"))
    for a in x["results"]:
        for f in DET:
            ncmp += 1
            if x["results"][a].get(f) != y["results"].get(a, {}).get(f):
                mism.append((k, a, f, x["results"][a].get(f), y["results"].get(a, {}).get(f)))
print("instances re-run", len(new), "deterministic field comparisons", ncmp, "mismatches", len(mism))
for m in mism[:20]: print(" ", m)
print("\nmedian total ms recorded -> re-run (ratio re-run/recorded), source run")
cells = sorted({k[:2] for k in new})
for (m, L) in cells:
    parts = []
    for a in ("A", "A:slimgb", "B", "B:slimgb", "C", "C:slimgb"):
        def med(src):
            v = [s["results"][a]["std_ms"] + s["results"][a]["fglm_ms"] for s in src if a in s["results"] and s["results"][a]["status"] == "ok"]
            return statistics.median(v) if v else None
        r0 = med([rec[(m, L, i)][1] for i in range(6)])
        r1 = med([new[(m, L, i)] for i in range(6)])
        parts.append(f"{a}:{r0}->{r1}" + (f"({r1 / r0:.2f})" if r0 and r1 else ""))
    print(f" m={m} L={L} [{rec[(m, L, 0)][0]}] " + "  ".join(parts))
print("\ncriterion-1 under re-run medians (A>=B?)")
for s in ("", ":slimgb"):
    out = []
    for (m, L) in cells:
        A = statistics.median(new[(m, L, i)]["results"]["A" + s]["std_ms"] + new[(m, L, i)]["results"]["A" + s]["fglm_ms"] for i in range(6) if new[(m, L, i)]["results"].get("A" + s, {}).get("status") == "ok")
        B = statistics.median(new[(m, L, i)]["results"]["B" + s]["std_ms"] + new[(m, L, i)]["results"]["B" + s]["fglm_ms"] for i in range(6) if new[(m, L, i)]["results"].get("B" + s, {}).get("status") == "ok")
        out.append(f"m{m}L{L}:{'A>=B' if A >= B else 'A<B'}({A}/{B})")
    print(" std" if not s else " slimgb", " ".join(out))
