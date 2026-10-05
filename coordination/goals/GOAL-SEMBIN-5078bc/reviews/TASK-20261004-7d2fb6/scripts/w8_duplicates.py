#!/usr/bin/env python3
"""w8_duplicates.py -- joint W8 (2): enumerate every duplicate (instance_id, instrument) key across the lane records of RUN-SEMBIN-9bb990
(the set assemble.py loads: */cells/results.jsonl, sorted by directory), compare each pair field by field, report verdict-bearing and
instrument-bearing disagreements, and say which record assemble.py's rule kept. The rule (assemble.dedupe): first record wins; a later record
replaces it only if the earlier is not 'ok' (_record_ok) and the later is. Read-only. Writes outputs/w8_duplicates.json."""
import json, glob, os, sys, collections
REPO = "/home/user/crypto-autoresearcher"; WS = os.environ["WS"]
RUN = f"{REPO}/experiments/EXP-SEMBIN-7e1371/runs/RUN-SEMBIN-9bb990"
sys.path.insert(0, f"{REPO}/experiments/EXP-SEMBIN-7e1371/code")
import importlib.util
spec = importlib.util.spec_from_file_location("assemble", f"{REPO}/experiments/EXP-SEMBIN-7e1371/code/assemble.py")
# assemble imports yaml at top; fine. We import only for its dedupe/_record_ok to apply THE producer's rule verbatim.
asm = importlib.util.module_from_spec(spec); spec.loader.exec_module(asm)
recs, workers = asm.load(__import__("pathlib").Path(RUN))
print("records loaded:", len(recs), "lanes:", len(workers))
by = collections.defaultdict(list)
for i, r in enumerate(recs): by[(r["instance_id"], r["instrument"])].append((i, r))
dups = {k: v for k, v in by.items() if len(v) > 1}
n_extra = sum(len(v) - 1 for v in dups.values())
kept, ndup = asm.dedupe(recs)
print("keys:", len(by), "duplicated keys:", len(dups), "extra records (assemble.dups):", n_extra, "assemble dedupe reports:", ndup, "kept records:", len(kept))
VERDICT_FIELDS = ("degree4_sufficiency_verdict", "closure_D", "solutions", "solutions_used", "status", "d_F4_semaev", "d_F4_naive", "quotient_dimension", "ideal_is_unit")
def per_D_core(r):
    out = []
    for p in r.get("per_D", []) or []:
        out.append({k: p.get(k) for k in ("D", "status", "verdict", "rank", "ncols", "standard_monomials", "contains_one", "solutions", "basis_lm_sha256", "elimination", "dropped_terms_above_D", "elimination_faults", "checkpoint_resumes", "m4ri_library", "deficiency_vs_columns", "rows", "cols", "sr_pred_rank")})
    return out
def strip(r):
    return {k: v for k, v in r.items() if k not in ("_worker",)}
rows = []
disagree_verdict, disagree_other = [], []
for key, lst in sorted(dups.items()):
    first = lst[0][1]
    kept_rec = next(k for k in kept if (k["instance_id"], k["instrument"]) == key)
    kept_idx = next(i for i, r in lst if r is kept_rec)
    for (i, r) in lst[1:]:
        a, b = strip(first), strip(r)
        differing = sorted(k for k in set(a) | set(b) if k not in ("per_D", "wall_s", "rounds") and a.get(k) != b.get(k))
        core_diff = per_D_core(first) != per_D_core(r)
        verdict_diff = [k for k in differing if k in VERDICT_FIELDS] + (["per_D(core)"] if core_diff else [])
        row = {"key": list(key), "first_worker": first["_worker"], "later_worker": r["_worker"], "kept_worker": kept_rec["_worker"], "kept_is_first": kept_idx == lst[0][0],
               "first_status": first.get("status"), "later_status": r.get("status"), "differing_top_level_fields": differing, "per_D_core_differs": core_diff, "verdict_bearing_diff": verdict_diff,
               "n_records_for_key": len(lst)}
        rows.append(row)
        if verdict_diff: disagree_verdict.append(row)
        elif differing: disagree_other.append(row)
print("pairs compared:", len(rows))
print("pairs with a verdict-bearing disagreement (verdict, closure_D, solutions, status, per_D core fields):", len(disagree_verdict))
for d in disagree_verdict[:20]: print("   ", d["key"], d["first_worker"], "vs", d["later_worker"], "diff:", d["verdict_bearing_diff"], "first_status", d["first_status"], "later_status", d["later_status"], "kept:", d["kept_worker"])
print("pairs differing only in other fields:", len(disagree_other))
cnt = collections.Counter(tuple(d["differing_top_level_fields"]) for d in disagree_other)
for k, v in cnt.most_common(10): print("   ", v, k)
print("duplicates by instrument:", dict(collections.Counter(k[1] for k in dups)))
print("duplicate keys by (first_worker, later_worker):", dict(collections.Counter((r["first_worker"], r["later_worker"]) for r in rows)))
print("kept record is the FIRST in", sum(r["kept_is_first"] for r in rows), "of", len(rows), "pairs")
json.dump({"records_loaded": len(recs), "duplicated_keys": len(dups), "extra_records": n_extra, "assemble_dups_reported": ndup, "pairs": rows}, open(f"{WS}/outputs/w8_duplicates.json", "w"), indent=1, default=str)
