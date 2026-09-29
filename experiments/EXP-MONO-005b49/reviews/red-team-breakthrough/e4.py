import json, collections, math
rows=json.load(open("/tmp/claude/panel.json"))
seen=set(); pairs=[]
for r in rows:
    if r["tau"]==1: continue
    k=(r["p_ord"],r["p_cm"],r["v"])
    if k in seen: continue
    seen.add(k)
    pairs.append(r)
hi=sum(1 for r in pairs if r["e4c"]>r["e4o"])
lo=sum(1 for r in pairs if r["e4c"]<r["e4o"])
eq=sum(1 for r in pairs if r["e4c"]==r["e4o"])
print("matched cells (tau>1): %d ;  #E[4]_CM > #E[4]_ord : %d ; < : %d ; equal : %d"%(len(pairs),hi,lo,eq))
co=collections.Counter((r["tau"],r["e4o"]) for r in pairs); cc=collections.Counter((r["tau"],r["e4c"]) for r in pairs)
print(" ordinary (tau,#E4) counts:",dict(sorted(co.items())))
print(" CM       (tau,#E4) counts:",dict(sorted(cc.items())))
diff=[r for r in pairs if abs(r["exact_ord"]-r["exact_cm"])>1e-15]
print("\ncells with a NONZERO exact ord-vs-CM difference: %d"%len(diff))
for r in diff:
    rel=(r["exact_cm"]-r["exact_ord"])/r["exact_ord"]
    print("  p_ord=%4d p_cm=%4d %-6s N=%4d tau=%d  #E4 ord=%2d cm=%2d  exact rel diff (cm-ord)/ord = %+0.5f%%  observed rel diff = %+0.2f%%"
          %(r["p_ord"],r["p_cm"],r["v"],r["N"],r["tau"],r["e4o"],r["e4c"],100*rel,100*(r["obs_cm"]-r["obs_ord"])/r["obs_ord"]))
print("\ncell 2 (p=3541, same-prime): #E4 ord=8, cm=16 -> exact (cm-ord)/ord = %+0.5f%% ; observed = %+0.2f%%"
      %(100*(0.005002776225113788-0.005006490238643939)/0.005006490238643939, 100*(94-98)/98))
