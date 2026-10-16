import json, sys, statistics
d = sys.argv[1]
load = lambda r: {(x["m"], x["L"], x["inst"]): x for x in map(json.loads, open(f"{d}/runs/RUN-ECDLP-f49f75-{r}/raw-result.jsonl"))}
r1, r3 = load("01"), load("03")
meta_mismatch = e_mismatch = 0
for k in sorted(r3):
    a, b = r1[k], r3[k]
    for f in ("seed", "p", "b", "chain_c", "kind"):
        if a[f] != b[f]:
            meta_mismatch += 1; print("meta mismatch", k, f, a[f], b[f])
    ea, eb = a["results"]["E"], b["results"]["E"]
    for f in ("status", "group_ops", "decompositions", "fb_size"):
        if ea.get(f) != eb.get(f):
            e_mismatch += 1; print("E mismatch", k, f, ea.get(f), eb.get(f))
    for arm in ("A", "B", "C"):
        for s in ("", ":slimgb"):
            ka = arm + s
            if ka in a["results"] and ka in b["results"]:
                x, y = a["results"][ka], b["results"][ka]
                if x.get("fb_size") != y.get("fb_size"):
                    print("fb mismatch", k, ka)
print("RUN-01 vs RUN-03 cells", sorted({k[:2] for k in r3}), "meta mismatches", meta_mismatch, "E mismatches", e_mismatch)
print("\nmedian total ms (std+fglm), RUN-01 (overflowed poly; excluded) vs RUN-03, and vdim medians")
for L in (8, 9, 10, 11):
    for key in ("A", "A:slimgb", "B", "B:slimgb", "C", "C:slimgb"):
        def med(rr):
            ok = [x["results"][key] for kk, x in rr.items() if kk[:2] == (2, L) and key in x["results"] and x["results"][key]["status"] == "ok"]
            st = sorted({x["results"][key]["status"] for kk, x in rr.items() if kk[:2] == (2, L) and key in x["results"]})
            if not ok: return f"{st}"
            return f"{statistics.median(v['std_ms']+v['fglm_ms'] for v in ok):>9} vdim~{statistics.median(v['vdim'] for v in ok)}"
        print(f" L={L} {key:9s} R01={med(r1):>24}  R03={med(r3):>24}")
# per-instance listing for RUN-03 L=8 A (first wave inst 0-3 vs second wave 4-5)
print("\nRUN-03 m=2 L=8 per-instance A std/slimgb total ms:")
for i in range(6):
    x = r3[(2, 8, i)]["results"]
    print(" inst", i, x["A"]["std_ms"] + x["A"]["fglm_ms"], x["A:slimgb"]["std_ms"] + x["A:slimgb"]["fglm_ms"], "wall", x["A"]["wall_s"], x["A:slimgb"]["wall_s"])
print("\nRUN-02 m=3 L=3 per-instance totals (A, A:slimgb, B, B:slimgb, C, C:slimgb):")
r2 = load("02")
for i in range(6):
    x = r2[(3, 3, i)]["results"]
    print(" inst", i, [x[k]["std_ms"] + x[k]["fglm_ms"] for k in ("A", "A:slimgb", "B", "B:slimgb", "C", "C:slimgb")], "sum wall_s", round(sum(v["wall_s"] for v in x.values()), 2))
for L in (3, 4, 5):
    tot = [sum(v["wall_s"] for v in r2[(3, L, i)]["results"].values()) for i in range(6)]
    print(f" m=3 L={L} per-instance summed wall_s", [round(t, 1) for t in tot])
