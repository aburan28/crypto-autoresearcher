#!/usr/bin/env python3
"""Validator recomputation for EXP-ECDLP-502ae2 / RUN-ECDLP-502ae2-01 (independent of analyze.py).
Usage: recompute.py MSOLVE_RAW SINGULAR_RAW  -> JSON on stdout"""
import json, sys, hashlib, statistics as st
from collections import defaultdict
ms = [json.loads(l) for l in open(sys.argv[1])]
sg = [json.loads(l) for l in open(sys.argv[2])]
out = {}
# --- integrity: seeds, row coverage, arms per L (stopping rule)
seed_ok = all(r["seed"] == int(hashlib.sha256(f"EXP-ECDLP-f49f75/v1|{r['m']}|{r['L']}|{r['inst']}".encode()).hexdigest()[:12], 16) for r in ms)
out["seed_derivation_matches"] = seed_ok
out["rows_per_L"] = {L: sorted(r["inst"] for r in ms if r["L"] == L) for L in sorted({r["L"] for r in ms})}
out["arms_run_per_L"] = {L: sorted({a for r in ms if r["L"] == L for a in r["results"]}) for L in sorted({r["L"] for r in ms})}
out["kind_by_inst"] = sorted({(r["inst"], r["kind"]) for r in ms})
# --- status-derivation consistency
bad_status = []
for r in ms:
    for a, v in r["results"].items():
        if a == "E":
            continue
        gs, ss = v.get("gb_status"), v.get("solve_status")
        exp = "ok" if gs == "ok" and ss == "ok" else ("timeout" if "timeout" in (gs, ss) else gs if gs != "ok" else ss)
        if exp != v["status"] or (gs != "ok" and ss is not None):
            bad_status.append((r["L"], r["inst"], a))
out["status_inconsistencies"] = bad_status
# --- cells
cells = defaultdict(list)
for r in ms:
    for a, v in r["results"].items():
        cells[(r["L"], a)].append(dict(v, inst=r["inst"], kind=r["kind"]))
summ = {}
for (L, a), vs in sorted(cells.items()):
    ok = [v for v in vs if v["status"] == "ok"]
    c = dict(n=len(vs), n_ok=len(ok), n_timeout=sum(v["status"] == "timeout" for v in vs),
             n_crash=sum(str(v["status"]).startswith("rc") for v in vs),
             n_degenerate=sum(v["status"] == "degenerate_target" for v in vs),
             ok_kinds=sorted(v["kind"] for v in ok))
    if a != "E":
        c["n_gb_ok"] = sum(v.get("gb_status") == "ok" for v in vs)
        c["n_gb_timeout"] = sum(v.get("gb_status") == "timeout" for v in vs)
        c["n_solve_timeout"] = sum(v.get("solve_status") == "timeout" for v in vs)
        if ok:
            c["median_solve_s"] = st.median(v["solve_wall_s"] for v in ok)
            c["median_gb_s"] = st.median(v["gb_wall_s"] for v in ok)
            c["max_gb_plus_solve_s"] = max(v["gb_wall_s"] + v["solve_wall_s"] for v in ok)
        gbd = [v for v in vs if v.get("gb_status") == "ok"]
        if gbd:
            c["median_gb_s_all_gb_done"] = st.median(v["gb_wall_s"] for v in gbd)
            c["f4_max_deg_set"] = sorted({v.get("f4_max_deg") for v in gbd})
            c["quotient_dims"] = {v["inst"]: v.get("quotient_dim") for v in gbd}
            c["nvars"] = sorted({v["nvars"] for v in gbd})
    else:
        c["decompositions"] = {v["inst"]: v.get("decompositions") for v in vs}
    summ[f"L{L}-{a}"] = c
out["cells"] = summ
# --- positive control
pc = dict(planted_ok=0, planted_ok_true=0, planted_gbdone=0, planted_gbdone_true=0, failures=[], qdim_zero_on_planted=[])
for r in ms:
    if r["kind"] != "planted":
        continue
    for a, v in r["results"].items():
        if a == "E":
            continue
        if v.get("gb_status") == "ok":
            pc["planted_gbdone"] += 1
            pc["planted_gbdone_true"] += v.get("planted_in_variety") is True
            if not v.get("quotient_dim"):
                pc["qdim_zero_on_planted"].append((r["L"], r["inst"], a))
            if v.get("planted_in_variety") is not True:
                pc["failures"].append((r["L"], r["inst"], a, v.get("planted_in_variety")))
        if v["status"] == "ok":
            pc["planted_ok"] += 1
            pc["planted_ok_true"] += v.get("planted_in_variety") is True
    for a in r["results"]:
        pass
pc["random_with_planted_field"] = sum("planted_in_variety" in v for r in ms if r["kind"] == "random" for v in r["results"].values())
pc["E_planted_decomp_ge1"] = all(r["results"]["E"]["decompositions"] >= 1 for r in ms if r["kind"] == "planted")
out["positive_control"] = pc
# --- frozen criteria
def cell(L, a): return summ.get(f"L{L}-{a}", {})
Ls = sorted({r["L"] for r in ms})
joint = [L for L in Ls if cell(L, "A").get("n_ok", 0) >= 1 and cell(L, "B").get("n_ok", 0) >= 1]
ratios = {L: cell(L, "A")["median_solve_s"] / cell(L, "B")["median_solve_s"] for L in joint}
a_ge_b = [L for L in joint if cell(L, "A")["median_solve_s"] >= cell(L, "B")["median_solve_s"]]
a_lt_b = [L for L in joint if cell(L, "A")["median_solve_s"] < cell(L, "B")["median_solve_s"]]
def retired(a): 
    x = [L for L in Ls if cell(L, a) and cell(L, a)["n"] and cell(L, a)["n_timeout"] == cell(L, a)["n"]]
    return min(x) if x else None
def largest_completed(a, kinds=("planted", "random"), need_all=False):
    x = [L for L in Ls if cell(L, a) and ((cell(L, a)["n_ok"] == cell(L, a)["n"]) if need_all else any(k in kinds for k in cell(L, a)["ok_kinds"]))]
    return max(x) if x else None
ret = {a: dict(retired_at=retired(a), largest_L_any_ok=largest_completed(a),
               largest_L_planted_ok=largest_completed(a, ("planted",)),
               largest_L_all6_ok=largest_completed(a, need_all=True)) for a in "ABC"}
out["criteria"] = dict(jointly_completed_L=joint, median_solve_ratio_A_over_B={f"L{L}": round(v, 2) for L, v in ratios.items()},
                       median_gb_ratio_A_over_B={f"L{L}": round(cell(L, "A")["median_gb_s"] / cell(L, "B")["median_gb_s"], 2) for L in joint},
                       A_at_or_above_B=a_ge_b, A_below_B=a_lt_b,
                       frac_A_at_or_above_B=len(a_ge_b) / len(joint) if joint else None,
                       retirement=ret)
fals_1 = bool(joint) and len(a_ge_b) / len(joint) >= 0.8
fals_2 = ret["A"]["retired_at"] is not None and all(ret[x]["retired_at"] is None or ret["A"]["retired_at"] <= ret[x]["retired_at"] for x in "BC")
succ_1 = bool(joint) and len(a_lt_b) / len(joint) >= 0.8
succ_2 = all((ret["A"]["largest_L_any_ok"] or 0) > (ret[x]["largest_L_any_ok"] or 0) for x in "BC")
out["criteria"].update(falsification_clause1_medians=fals_1, falsification_clause2_retirement=fals_2,
                       falsification_met=fals_1 or fals_2, success_met=succ_1 and succ_2)
# --- robustness: falsification under alternative 'completed' readings
alt = {}
for name, key in (("any_ok", "largest_L_any_ok"), ("planted_ok", "largest_L_planted_ok"), ("all6_ok", "largest_L_all6_ok")):
    la = {x: ret[x][key] for x in "ABC"}
    alt[name] = dict(largest=la, A_strictly_larger_than_B_and_C=all((la["A"] or 0) > (la[x] or 0) for x in "BC"))
out["criteria"]["completion_reading_robustness"] = alt
# --- pairing with Singular RUN-02 (same instances)
sgi = {(r["L"], r["inst"]): r for r in sg}
pair = dict(instance_param_mismatch=[], qdim_vs_vdim=[], qdim_A_vs_B=[])
for r in ms:
    s = sgi.get((r["L"], r["inst"]))
    if s:
        for k in ("seed", "p", "b", "chain_c", "kind"):
            if r[k] != s[k]:
                pair["instance_param_mismatch"].append((r["L"], r["inst"], k))
    for a in "ABC":
        v = r["results"].get(a, {})
        if s and "quotient_dim" in v and s["results"].get(a, {}).get("vdim") is not None:
            pair["qdim_vs_vdim"].append((r["L"], r["inst"], a, v["quotient_dim"], s["results"][a]["vdim"]))
    A, B = r["results"].get("A", {}), r["results"].get("B", {})
    if "quotient_dim" in A and "quotient_dim" in B:
        pair["qdim_A_vs_B"].append((r["L"], r["inst"], A["quotient_dim"], B["quotient_dim"]))
pair["n_singular_rows_matched"] = sum((r["L"], r["inst"]) in sgi for r in ms)
pair["qdim_vs_vdim_all_equal"] = all(x[3] == x[4] for x in pair["qdim_vs_vdim"])
pair["qdim_A_eq_B_all"] = all(x[2] == x[3] for x in pair["qdim_A_vs_B"])
out["pairing"] = pair
print(json.dumps(out, indent=1, default=str))
