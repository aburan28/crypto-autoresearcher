import json,glob,collections,sys
rows=[]
for f in glob.glob("raw_*.jsonl"):
    for line in open(f):
        d=json.loads(line)
        if "halt" in d: continue
        rows.append(d)
by=collections.defaultdict(list)
for d in rows: by[(d["arm"],d["r"])].append(d)
out={"runs":len(rows),"per_arm_round":[]}
for (arm,r),ds in sorted(by.items()):
    res=[d["n_mod8"] for d in ds]
    hist=[res.count(v) for v in range(8)]
    out["per_arm_round"].append({
      "arm":arm,"r":r,"trials":len(ds),
      "n_values":[d["n"] for d in ds],
      "residue_mod8":res,"residue_mod8_histogram_0to7":hist,
      "residue_mod16":[d["n_mod16"] for d in ds],
      "all_zero_mod8":all(v==0 for v in res),
      "p_under_uniform_null_if_all_zero": (8.0**-len(ds)) if all(v==0 for v in res) else None,
      "max_occupancy":[d["max_occupancy"] for d in ds],
      "overflow_any":any(d["overflow"] for d in ds),
      "identity_check_all_ok":all(d["identity_check_ok"] for d in ds),
      "sum_m_ok":all(d["sum_m"]==(1<<d["nbits"]) for d in ds),
      "seconds":[round(d["seconds"],1) for d in ds]})
json.dump(out,open("results_summary.json","w"),indent=1)
for e in out["per_arm_round"]:
    print(f"{e['arm']:34s} r={e['r']:2d} t={e['trials']:2d} mod8={e['residue_mod8']} allzero={e['all_zero_mod8']} ovf={e['overflow_any']} idok={e['identity_check_all_ok']} summ_ok={e['sum_m_ok']}")
