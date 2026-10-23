#!/usr/bin/env python3
"""Blind re-derivation of the n=83 baseline row S fields (s_ic_setup with the rank stage) from the raw
producer records (base64 in panel/runs/*.stdout.txt) and protocol.json definitions only.
Does not import verify_receipt.py or read result.json.
Usage: python3 -I -B blind_n83.py <experiment-dir>"""
import base64, hashlib, json, statistics as st, sys, os
exp = sys.argv[1]; run = os.path.join(exp, "run_github_38862448935", "panel")
proto = json.load(open(os.path.join(exp, "protocol.json")))
sqrt_r = proto["online"]["sqrt_r"]
r = int(proto["online"]["subgroup_order"]); print(f"sqrt_r frozen {sqrt_r}; sqrt(subgroup_order) {r**0.5:.3f}")
rows = [json.loads(l) for l in open(os.path.join(run, "runs.jsonl"))]
def decode(path):
    txt = open(os.path.join(run, path)).read()
    line = [l for l in txt.splitlines() if l.startswith("raw_b64=")][0]
    raw = base64.b64decode(line[8:])
    tail = dict(kv.split("=", 1) for kv in txt.strip().splitlines()[-1].split() if "=" in kv)
    assert hashlib.sha256(raw).hexdigest() == tail["raw_result_sha256"], path
    return json.loads(raw)
recs = {}
bad = [x for x in rows if x["status"] != "valid"]
print("rows", len(rows), "non-valid", len(bad))
for x in rows:
    recs[x["serial"]] = (x, decode(x["stdout_file"]))
def ic(serial):
    x, d = recs[serial]
    prod = [q for q in d["records"] if "timing_ms" in q][0]
    tgt = [q for q in d["records"] if "online_ms" in q and "probes" in q][0]
    return x, d, prod, tgt
def cold_arm(arm):
    out = []
    for s, (x, d) in sorted(recs.items()):
        if x["arm"] == arm and x["segment"] != "O1":
            _, _, prod, tgt = ic(s)
            out.append(dict(point=x["point_id"], cold=prod["cold_in_process_ms"], online=tgt["online_ms"],
                            setup=prod["cold_in_process_ms"] - tgt["online_ms"], fb=prod["cold_phase_ms"]["factor_base"],
                            la=prod["cold_phase_ms"]["relation_la"], probes=tgt["probes"]))
    return out
def rank_arm(arm):
    out = []
    for s, (x, d) in sorted(recs.items()):
        if x["arm"] == arm:
            _, _, prod, tgt = ic(s)
            out.append(dict(serial=s, rank=prod["timing_ms"]["rank_stage"], la=prod["timing_ms"]["linear_algebra"],
                            probes=prod["rank_probes_total"], roots=prod["rank_root_calls_total"], attempts=prod["rank_attempts"],
                            single_cold=prod["cold_in_process_ms"]))
    return out
rho = []
for s, (x, d) in sorted(recs.items()):
    if x["arm"] == "rT" and x["segment"] != "O1":
        q = d["records"][0]
        rho.append(dict(point=x["point_id"], online=q["online_ms"], setup=q["preparation_ns_excluded"]/1e6,
                        steps=q["outcome"]["walk_steps"], f_setup=d["fields"]["setup_ms"]))
print("rT runs", len(rho), "setup fields equal preparation_ns_excluded:", all(abs(a["setup"]-a["f_setup"])<1e-6 for a in rho))
ms_step_sum = sum(a["online"] for a in rho) / sum(a["steps"] for a in rho)
ms_step_med = st.median(a["online"]/a["steps"] for a in rho)
ms_step_mean = st.mean(a["online"]/a["steps"] for a in rho)
print(f"rho ms/step: ratio of sums {ms_step_sum:.6e}; median per run {ms_step_med:.6e}; mean per run {ms_step_mean:.6e}")
out = {}
for unit_name, ms_step in (("ratio_of_sums", ms_step_sum), ("median", ms_step_med)):
    U = ms_step * sqrt_r
    res = {"unit_ms": U}
    for c, k in (("cP", "kP"), ("cS", "kS"), ("cSaa", "kSaa")):
        C = cold_arm(c); K = rank_arm(k)
        mr = st.mean(z["rank"] for z in K); mc = st.mean(z["cold"] for z in C); mo = st.mean(z["online"] for z in C)
        ms = st.mean(z["setup"] for z in C)
        e2e = mr + mc
        res[c] = dict(n_points=len(C), n_rank=len(K), mean_rank_ms=mr, mean_cold_ms=mc, mean_setup_ms=ms, mean_online_ms=mo, e2e_ms=e2e,
                      s_ic_cold=e2e/U, s_ic_online=mo/U, s_ic_rank_stage=mr/U, s_ic_setup_without_rank=ms/U,
                      s_ic_setup=(mr+ms)/U, s_cold_without_rank=mc/U, check_setup_eq_cold_minus_online=(e2e-mo)/U,
                      mean_fb_ms=st.mean(z["fb"] for z in C), mean_la_ms=st.mean(z["la"] for z in C),
                      rank_probes=sum(z["probes"] for z in K), rank_roots=sum(z["roots"] for z in K),
                      rank_attempts=sum(z["attempts"] for z in K), rank_la_ms=[z["la"] for z in K])
    rc = st.mean(a["setup"] + a["online"] for a in rho); ro = st.mean(a["online"] for a in rho)
    res["rT"] = dict(mean_cold_ms=rc, mean_online_ms=ro, s_rho_cold=rc/U, s_rho_online=ro/U)
    res["R_primary"] = res["cP"]["e2e_ms"] / res["cS"]["e2e_ms"]
    res["gap_cold_cP"] = res["cP"]["e2e_ms"] / rc; res["gap_cold_cS"] = res["cS"]["e2e_ms"] / rc
    res["gap_online_cP"] = res["cP"]["mean_online_ms"] / ro; res["gap_online_cS"] = res["cS"]["mean_online_ms"] / ro
    res["probe_ratio_kP_kS"] = res["cP"]["rank_probes"] / res["cS"]["rank_probes"]
    res["root_ratio_kP_kS"] = res["cP"]["rank_roots"] / res["cS"]["rank_roots"]
    out[unit_name] = res
print(json.dumps(out, indent=1))
