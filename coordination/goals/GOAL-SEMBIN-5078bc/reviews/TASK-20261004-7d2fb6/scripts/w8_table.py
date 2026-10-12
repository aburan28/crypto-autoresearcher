#!/usr/bin/env python3
"""w8_table.py -- joint W8 (1): recompute the RUN-SEMBIN-5ed13e results table from the six lanes' results.jsonl with my own code and diff it
field by field with (a) the markdown table in NOTES.md, (b) window_table.py's output (run here, read-only), (c) results-table.json, (d) summary.json.
Also checks the run count against the declared design. Read-only on the package; writes outputs/w8_table.json."""
import json, glob, os, re, subprocess, sys, collections
REPO = "/home/user/crypto-autoresearcher"; WS = os.environ["WS"]
R = f"{REPO}/experiments/EXP-SEMBIN-7e1371/runs/RUN-SEMBIN-5ed13e"
lane_recs = {}
for lane in sorted(glob.glob(f"{R}/closure_m2_n4*")):
    name = os.path.basename(lane)
    lane_recs[name] = [json.loads(l) for l in open(f"{lane}/cells/results.jsonl") if l.strip()]
# ---- my table
mine = []
for lane, recs in lane_recs.items():
    cnt = {r["instance_id"]: r for r in recs if r["instrument"] == "exhaustive_solution_count"}
    for r in recs:
        if r["instrument"] != "closure_certificate": continue
        pd = r["per_D"]; last = pd[-1]; d4 = next((p for p in pd if p["D"] == 4), None)
        row = {"n": r["n"], "N": r["N"], "draw": r["draw"], "V": cnt[r["instance_id"]]["solutions"], "verdict": r["degree4_sufficiency_verdict"],
               "verdict_source": r["degree4_verdict_source"],
               "decided_at": f"D={last['D']}" + (" (1 in W_D)" if last.get("contains_one") else ""),
               "rank": last["rank"], "ncols": last["ncols"], "std": last.get("standard_monomials"), "lm8": (last.get("basis_lm_sha256") or "None")[:8],
               "wall_D4": (round(d4["wall_s"]) if d4 and d4.get("wall_s") else None),
               "faults": sum(p.get("elimination_faults", 0) or 0 for p in pd), "resumes": sum(p.get("checkpoint_resumes", 0) or 0 for p in pd),
               "per_D_D": [p["D"] for p in pd], "per_D_status": [p["status"] for p in pd], "per_D_verdict": [p.get("verdict") for p in pd],
               "dropped": [p.get("dropped_terms_above_D") for p in pd], "elimination": sorted({p.get("elimination") for p in pd}), "m4ri_library": sorted({p.get("m4ri_library") for p in pd}),
               "instance_id": r["instance_id"], "lane": lane}
        mine.append(row)
mine.sort(key=lambda x: (x["n"], x["draw"]))
# ---- NOTES table
notes = open(f"{R}/NOTES.md").read()
tab = [l for l in notes.splitlines() if re.match(r"^\| \d+ \| \d+ \| \d+ \|", l)]
notes_rows = []
for l in tab:
    c = [x.strip() for x in l.strip().strip("|").split("|")]
    notes_rows.append({"n": int(c[0]), "N": int(c[1]), "draw": int(c[2]), "V": int(c[3]), "verdict": c[4], "decided_at": c[5], "rank_cols": c[6], "std": int(c[7]), "lm8": c[8],
                       "wall_D4": (None if c[9] == "-" else int(c[9])), "faults": int(c[10]), "resumes": int(c[11])})
diffs = []
print("rows mine:", len(mine), " rows in NOTES.md:", len(notes_rows))
for m, nrow in zip(mine, notes_rows):
    cmp = {"n": m["n"], "N": m["N"], "draw": m["draw"], "V": m["V"], "verdict": m["verdict"], "decided_at": m["decided_at"],
           "rank_cols": f"{m['rank']} / {m['ncols']}", "std": m["std"], "lm8": m["lm8"], "wall_D4": m["wall_D4"], "faults": m["faults"], "resumes": m["resumes"]}
    # NOTES formats rank with thousands separators? normalise
    nrc = nrow["rank_cols"].replace(",", "")
    for k, v in cmp.items():
        nv = nrc if k == "rank_cols" else nrow[k]
        if str(v) != str(nv): diffs.append((m["instance_id"], k, v, nv))
print("NOTES.md table vs my recomputation: differing cells:", diffs if diffs else "none")
# ---- window_table.py output, run as is
wt = subprocess.run([sys.executable, f"{R}/schedulers/window_table.py"], capture_output=True, text=True).stdout.splitlines()
wt_rows = [l for l in wt if re.match(r"^\| \d+ \|", l)]
nm = [l for l in tab]
print("window_table.py rows equal NOTES.md rows (exact text):", [a == b for a, b in zip(wt_rows, nm)].count(True), "of", len(nm))
# ---- results-table.json vs lane records
rt = json.load(open(f"{R}/results-table.json"))
lane_by_key = {}
for lane, recs in lane_recs.items():
    for r in recs: lane_by_key[(r["instance_id"], r["instrument"])] = r
rt_bad = []
for row in rt:
    key = (row["instance_id"], row["instrument"]); src = lane_by_key[key]
    for k, v in row.items():
        if k in ("per_D", "f4_round_count"): continue
        if json.loads(json.dumps(src.get(k), default=str)) != v: rt_bad.append((key, k))
    if row.get("per_D") != json.loads(json.dumps(src.get("per_D"), default=str)): rt_bad.append((key, "per_D"))
print("results-table.json rows:", len(rt), "field-level differences vs lane records:", rt_bad if rt_bad else "none", "| keys covered:", len({(r['instance_id'], r['instrument']) for r in rt}) == len(lane_by_key))
# ---- summary.json
sm = json.load(open(f"{R}/summary.json"))
exp_cells = collections.defaultdict(lambda: {"verdicts": collections.Counter(), "std": set(), "counts": set(), "Ds": set()})
for r in mine:
    c = exp_cells[(r["n"],)]
    c["verdicts"][r["verdict"]] += 1; c["counts"].add(r["V"])
    for p in lane_by_key[(r["instance_id"], "closure_certificate")]["per_D"]:
        if p["D"] == 4 and p.get("standard_monomials") is not None: c["std"].add(p["standard_monomials"])
    cl = lane_by_key[(r["instance_id"], "closure_certificate")]
    if cl.get("closure_D") is not None: c["Ds"].add(cl["closure_D"])
sm_bad = []
for key, c in sm["cells"].items():
    n = c["cell"][0]; e = exp_cells[(n,)]
    if c["degree4_sufficiency_verdicts"] != dict(e["verdicts"]): sm_bad.append((n, "verdicts", c["degree4_sufficiency_verdicts"], dict(e["verdicts"])))
    if sorted(c["closure_standard_monomials"]) != sorted(e["std"]): sm_bad.append((n, "std", c["closure_standard_monomials"], sorted(e["std"])))
    if sorted(c["exact_solution_counts"]) != sorted(e["counts"]): sm_bad.append((n, "counts", c["exact_solution_counts"], sorted(e["counts"])))
    if sorted(c["closure_D_values"]) != sorted(e["Ds"]): sm_bad.append((n, "closure_D", c["closure_D_values"], sorted(e["Ds"])))
print("summary.json cell rollups differing from lane records:", sm_bad if sm_bad else "none", "| n_records", sm["n_records"], "== lane records", sum(len(v) for v in lane_recs.values()))
print("summary.json closure_D_values for n=45:", sm["cells"]["(45, 2, 2, 23)|chained_S3_eq5"]["closure_D_values"], "(both n=45 instances are insufficient at D=4: no closure_D)")
# design: lanes x instances x instruments
design = {lane: collections.Counter(r["instrument"] for r in recs) for lane, recs in lane_recs.items()}
print("records per lane by instrument:", {k: dict(v) for k, v in design.items()})
print("closure records per_D lists (D values):", {m["instance_id"][:22]: m["per_D_D"] for m in mine})
json.dump({"mine": mine, "notes_diffs": diffs, "results_table_diffs": rt_bad, "summary_diffs": [list(map(str, x)) for x in sm_bad], "design": {k: dict(v) for k, v in design.items()}}, open(f"{WS}/outputs/w8_table.json", "w"), indent=1, default=str)
