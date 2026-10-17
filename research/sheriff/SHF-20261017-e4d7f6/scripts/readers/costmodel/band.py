#!/usr/bin/env python3
"""Illustrative section-5a pricing at w in {0, 0.1, 1} GAE per unpriced native op, using only counters the run emits.
IC group additions are NOT emitted, so they enter as an unknown G_IC >= 0; the band is reported as a function of it.
Usage: python3 -I -B band.py <experiment-dir>"""
import base64, json, os, statistics as st, sys
exp = sys.argv[1]; run = os.path.join(exp, "run_github_38862448935", "panel")
def decode(p):
    txt = open(os.path.join(run, p)).read()
    return json.loads(base64.b64decode([l for l in txt.splitlines() if l.startswith("raw_b64=")][0][8:]))
rows = [json.loads(l) for l in open(os.path.join(run, "runs.jsonl"))]
R = {x["serial"]: (x, decode(x["stdout_file"])) for x in rows}
rho = [d["records"][0] for s, (x, d) in sorted(R.items()) if x["arm"] == "rT" and x["segment"] != "O1"]
ga = st.mean(q["outcome"]["charges_setup_and_solve"]["group_additions"] for q in rho)
sm = st.mean(q["outcome"]["charges_setup_and_solve"]["scalar_multiplications"] + q["preparation_charges"]["scalar_multiplications"] for q in rho)
unp_rho = st.mean(sum(v for k, v in q["outcome"]["charges_setup_and_solve"].items() if k not in ("group_additions", "scalar_multiplications", "failed_collisions")) for q in rho)
print(f"rho mean group_additions {ga:,.0f}; scalar mults {sm:.1f}; other unpriced (canonicalizations, hashes, table ops) {unp_rho:,.0f}")
def prod(d): return [q for q in d["records"] if "timing_ms" in q][0]
def tgt(d): return [q for q in d["records"] if "probes" in q and "online_ms" in q][0]
ic = {}
for k, c in (("kP", "cP"), ("kS", "cS")):
    K = [prod(d) for s, (x, d) in sorted(R.items()) if x["arm"] == k]
    C = [(prod(d), tgt(d)) for s, (x, d) in sorted(R.items()) if x["arm"] == c and x["segment"] != "O1"]
    rp = st.mean(p["rank_probes_total"] for p in K); rr = st.mean(p["rank_root_calls_total"] for p in K)
    op = st.mean(t["probes"] for p, t in C); orc = st.mean(t["root_calls"] for p, t in C)
    ss = st.mean(p["stored_states"] for p, t in C)
    ic[c] = dict(unpriced=rp + rr + op + orc + ss, rank_probes=rp, rank_roots=rr, online_probes=op, online_roots=orc, index_inserts_proxy=ss)
    print(c, {kk: f"{vv:,.0f}" for kk, vv in ic[c].items()})
print("Pricing: cost(w) = G + w * unpriced (rho: G = group_additions + 1 per scalar mult as a floor; IC: G_IC unknown >= 0)")
rho_cost = lambda w: ga + sm + w * unp_rho
for c in ("cP", "cS"):
    for w in (0.0, 0.1, 1.0):
        lo = (w * ic[c]["unpriced"]) / rho_cost(w)
        print(f"  {c} w={w}: IC/rho >= {lo:,.2f} (with G_IC = 0); with G_IC = index logical states 29.88M as a guess: {(29.88e6 + w*ic[c]['unpriced'])/rho_cost(w):,.2f}")
for w in (0.0, 0.1, 1.0):
    print(f"  IC vs IC w={w}: cP/cS on emitted counters (G_IC equal in both arms assumed 0): "
          f"{'tie (no emitted priced op)' if w == 0 else round(ic['cP']['unpriced']/ic['cS']['unpriced'], 4)}")
