#!/usr/bin/env python3
"""w9_classes.py -- joint W9 (1)(2): (a) every '[ech ...]' / 'rank' line quoted in RUN-SEMBIN-9bb990/NOTES-deviations-and-limitations.md is searched for, by its numbers, in the package's
m4ri_defect_investigation logs; (b) a table of the record classes of the run with the instrument, whether M4RI is used at all, and the elimination / library fields the records carry;
(c) the recorded counter agreement. Read-only. Writes outputs/w9_classes.json."""
import json, glob, re, os, collections
REPO = "/home/user/crypto-autoresearcher"; WS = os.environ["WS"]
RUN = f"{REPO}/experiments/EXP-SEMBIN-7e1371/runs/RUN-SEMBIN-9bb990"
notes = open(f"{RUN}/NOTES-deviations-and-limitations.md").read().splitlines()
logs = {os.path.basename(p): open(p).read() for p in glob.glob(f"{RUN}/m4ri_defect_investigation/*.log")}
quoted = []
for i, l in enumerate(notes, 1):
    m = re.match(r"\s+\[ech (\d+)(?: (\w+))?\]\s+(\d+) x (\d+)\s+rank\s+(\d+)\s*\|\s*in=(\d+) out=(\d+)", l)
    if m:
        quoted.append({"notes_line": i, "call": int(m[1]), "routine": m[2], "rows": int(m[3]), "cols": int(m[4]), "rank": int(m[5]), "in": int(m[6]), "out": int(m[7]), "text": l.strip()[:140]})
for q in quoted:
    hits = []
    for name, txt in logs.items():
        for l in txt.splitlines():
            m = re.match(r"\[ech (\d+)(?: (\w+))?\] (\d+) x (\d+) rank (\d+) \| rows not vanishing at the zero: in=(\d+) out=(\d+)", l)
            if m and (int(m[1]), int(m[3]), int(m[4]), int(m[5]), int(m[6]), int(m[7])) == (q["call"], q["rows"], q["cols"], q["rank"], q["in"], q["out"]):
                hits.append({"log": name, "routine_in_log": m[2] or "(unlabelled)"})
    q["found_in"] = hits
print("quoted [ech] lines in NOTES:", len(quoted))
for q in quoted: print(f"  NOTES line {q['notes_line']:3d}: [ech {q['call']}{' ' + q['routine'] if q['routine'] else ''}] {q['rows']} x {q['cols']} rank {q['rank']} in={q['in']} out={q['out']}  -> found in package logs: {[(h['log'][:42], h['routine_in_log']) for h in q['found_in']] or 'NOT FOUND'}")
# other quoted numbers
extra = {"rank 139,204 / 131,030 pivots ('pivot count 131030 != rank 139204')": "pivot count 131030 != rank 139204" in logs["n44_pluq_m4ri-20200125_evalcheck_FAILED.log"],
         "std=127628 verdict insufficient (PLUQ 20200125)": "std=127628" in logs["n44_pluq_m4ri-20200125_evalcheck_FAILED.log"],
         "20240729 verdict std=2 sufficient": "std=2 |V(I)|=2 verdict=sufficient" in logs["n44_verdict_pluq_m4ri-20240729_evalcheck.log"],
         "39 eliminations logged (20240729 verdict run: 22 + 17)": None}
nel = [len(re.findall(r"\[ech \d+ pluq\]", t)) for n, t in logs.items() if "verdict" in n]
extra["39 eliminations logged (20240729 verdict run: 22 + 17)"] = nel
print("other quoted facts:", extra)
# (b) record classes
recs = []
for f in glob.glob(f"{RUN}/*/cells/results.jsonl"):
    lane = f.split("/")[-3]
    for l in open(f):
        r = json.loads(l); r["_lane"] = lane; recs.append(r)
def fields(r):
    pd = r.get("per_D") or []
    return {"has_elimination_field": any("elimination" in p for p in pd), "has_m4ri_library_field": any("m4ri_library" in p for p in pd),
            "elims": sorted({p.get("elimination") for p in pd if p.get("elimination")}), "libs": sorted({p.get("m4ri_library") for p in pd if p.get("m4ri_library")})}
tab = collections.defaultdict(lambda: collections.Counter())
for r in recs:
    key = (r["instrument"], r.get("family"))
    f = fields(r)
    tab[key]["n"] += 1
    tab[key]["with_elimination_field"] += f["has_elimination_field"]; tab[key]["with_m4ri_library_field"] += f["has_m4ri_library_field"]
    for e in f["elims"]: tab[key]["elim=" + e] += 1
print("\nrecord classes (instrument, family): counts and the elimination/library fields they carry")
for k, v in sorted(tab.items(), key=lambda kv: str(kv[0])): print("  ", k, dict(v))
# (c) counters
cnt = [r for r in recs if r["instrument"] == "exhaustive_solution_count"]
agree = collections.Counter()
for r in cnt:
    if r.get("t") == 2:
        agree["t=2 records"] += 1
        if "cross_check_count_m2" in r: agree["with count_m2 cross-check"] += 1; agree["cross-check agrees" if r.get("cross_check_agrees") else "cross-check DISAGREES"] += 1
        if "reference_agrees" in r: agree["with O(2^2k) reference"] += 1; agree["reference agrees" if r["reference_agrees"] else "reference DISAGREES"] += 1
    agree["method=" + str(r.get("instrument")) + "/" + str(r.get("method"))[:30]] += 1
print("\nexact counter records:", dict(agree))
json.dump({"quoted": quoted, "extra": extra, "classes": {str(k): dict(v) for k, v in tab.items()}, "counter_agreement": dict(agree)}, open(f"{WS}/outputs/w9_classes.json", "w"), indent=1, default=str)
