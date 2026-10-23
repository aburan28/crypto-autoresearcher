#!/usr/bin/env python3
"""Re-derive the K1/K2 disclosure numbers from raw producer records (no verify_receipt.py, no result.json),
then compare to result.json only for bootstrap CIs. Usage: python3 -I -B k1k2.py <experiment-dir>"""
import json, os, statistics as st, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
exp = sys.argv[1]; run = os.path.join(exp, "run_github_38862448935", "panel")
import base64, hashlib
def decode(p):
    txt = open(os.path.join(run, p)).read()
    raw = base64.b64decode([l for l in txt.splitlines() if l.startswith("raw_b64=")][0][8:])
    return json.loads(raw)
rows = [json.loads(l) for l in open(os.path.join(run, "runs.jsonl"))]
R = {x["serial"]: (x, decode(x["stdout_file"])) for x in rows}
def prod(d): return [q for q in d["records"] if "timing_ms" in q][0]
def tgt(d): return [q for q in d["records"] if "probes" in q and "online_ms" in q][0]
rank = {a: [prod(d) for s, (x, d) in sorted(R.items()) if x["arm"] == a] for a in ("kP", "kS")}
cold = {a: [(prod(d), tgt(d)) for s, (x, d) in sorted(R.items()) if x["arm"] == a and x["segment"] != "O1"] for a in ("cP", "cS")}
out = {}
for a in ("kP", "kS"):
    w = sum(p["timing_ms"]["rank_stage"] for p in rank[a]); pr = sum(p["rank_probes_total"] for p in rank[a])
    out[a] = dict(rank_wall_ms_sum=w, probes=pr, roots=sum(p["rank_root_calls_total"] for p in rank[a]), ns_per_probe=w*1e6/pr,
                  attempts=sum(p["rank_attempts"] for p in rank[a]), stored_states=[p["stored_states"] for p in rank[a]])
out["rank_wall_ratio"] = out["kP"]["rank_wall_ms_sum"] / out["kS"]["rank_wall_ms_sum"]
out["probe_ratio"] = out["kP"]["probes"] / out["kS"]["probes"]
out["root_ratio"] = out["kP"]["roots"] / out["kS"]["roots"]
out["ns_per_probe_ratio"] = out["kP"]["ns_per_probe"] / out["kS"]["ns_per_probe"]
out["product_check"] = out["probe_ratio"] * out["ns_per_probe_ratio"]
for a in ("cP", "cS"):
    out[a] = dict(stored_states=sorted({p["stored_states"] for p, t in cold[a]}), index_ms_mean=st.mean(p["timing_ms"]["index_build"] for p, t in cold[a]),
                  online_probes_sum=sum(t["probes"] for p, t in cold[a]), mean_cold=st.mean(p["cold_in_process_ms"] for p, t in cold[a]),
                  base_source=sorted({str(p.get("base_source")) for p, t in cold[a]}), factor_base_ms_mean=st.mean(p["cold_phase_ms"]["factor_base"] for p, t in cold[a]),
                  setup_input_control_ms_mean=st.mean(p["cold_phase_ms"]["setup_input_control"] for p, t in cold[a]))
out["index_build_ratio"] = out["cP"]["index_ms_mean"] / out["cS"]["index_ms_mean"]
out["online_probe_ratio_cP_cS"] = out["cP"]["online_probes_sum"] / out["cS"]["online_probes_sum"]
e2eP = st.mean(p["timing_ms"]["rank_stage"] for p in rank["kP"]) + out["cP"]["mean_cold"]
e2eS = st.mean(p["timing_ms"]["rank_stage"] for p in rank["kS"]) + out["cS"]["mean_cold"]
out["rank_share_pP"] = st.mean(p["timing_ms"]["rank_stage"] for p in rank["kP"]) / e2eP
out["rank_share_stack"] = st.mean(p["timing_ms"]["rank_stage"] for p in rank["kS"]) / e2eS
U = 29314.197725685277  # unit from blind_n83.py (ratio of sums)
out["X_sensitivity"] = {X: dict(R=(e2eP + X*1000)/(e2eS + X*1000), S=(e2eS + X*1000)/U) for X in (0, 1, 10, 60)}
out["X_to_reach_R2"] = (e2eP - 2*e2eS) / 1000.0
out["rank_process_wall_s"] = {x["arm"]+x["segment"]: x["process_wall_ms"]/1000 for s, (x, d) in R.items() if x["arm"] in ("kP", "kS")}
rj = json.load(open(os.path.join(run, "result.json")))
def find(o, key, path=""):
    if isinstance(o, dict):
        for k, v in o.items():
            if key in k: yield path+"."+k, v
            yield from find(v, key, path+"."+k)
for key in ("gap_cP_over_rT", "gap_cS_over_rT", "primary_e2e"):
    for p, v in find(rj, key): out.setdefault("result_json", {})[p] = v
print(json.dumps(out, indent=1, default=str))
