"""V3(1): validator's own reduction of results.jsonl to per-(cell,label,engine,config)
medians and P1-P6, written from the hypothesis statement and the contract's metric
definitions only, BEFORE reading code/summary.py.

Finished row := status in {SAT, UNSAT}.  Median := statistics.median (mean of the two
middle values for even n).  Also writes my_summary.json for the diff step.
"""
import json
import os
import statistics
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(__file__))
from gf2n import BinaryCurve, GF2n, poly_from_string_le

RUN = "/workspace/experiments/EXP-ICPERF-66fd51/runs/RUN-ICPERF-305ca3"
BENCH = "/workspace/inputs/TRIMOSKA-ECICB-2024/upstream/benchmarks"
OUT = os.path.join(os.path.dirname(__file__), "my_summary.json")

rows = [json.loads(l) for l in open(f"{RUN}/results.jsonl")]
FIN = {"SAT", "UNSAT"}


def med(xs):
    xs = [x for x in xs if x is not None]
    return statistics.median(xs) if xs else None


def conflicts_of(r):
    if r.get("conflicts") is not None:
        return r["conflicts"]
    st = r.get("stats") or {}
    return st.get("conflicts")


# ---------------- per-group medians ----------------
groups = defaultdict(list)
for r in rows:
    if r.get("engine") == "certificate":
        continue
    groups[(r["cell"], r["label"], r["engine"], r["config"])].append(r)

table = {}
for k, rs in sorted(groups.items()):
    fin = [r for r in rs if r["status"] in FIN]
    table["/".join(k)] = dict(
        n_rows=len(rs), n_finished=len(fin),
        n_timeout=sum(r["status"] == "budget_stop_timeout" for r in rs),
        n_infra=sum(str(r["status"]).startswith("infrastructure") for r in rs),
        median_wall_s=med([r["wall_s"] for r in fin]),
        median_cpu_s=med([r["cpu_s"] for r in fin]),
        median_conflicts=med([conflicts_of(r) for r in fin]),
    )

# ---------------- P1 ----------------
infos = {}
for f in os.listdir(BENCH):
    if f.startswith("INFO"):
        name = f[4:-7]
        ls = open(f"{BENCH}/{f}").read().split("\n")
        infos[name] = dict(n=int(ls[0].split()[0]), l=int(ls[0].split()[1]), modulus=ls[1].strip(),
                           xR=ls[2].strip(), label=ls[3].strip(), cert=ls[4].strip())
fields = {}


def F_of(n):
    if n not in fields:
        inf = next(v for v in infos.values() if v["n"] == n)
        fields[n] = GF2n(inf["modulus"])
    return fields[n]


def my_verify(name, bits):
    inf = infos[name]
    F = F_of(inf["n"])
    E = BinaryCurve(F, 1, 1)
    l = inf["l"]
    xs = [poly_from_string_le(bits[i * l:(i + 1) * l]) for i in range(3)]
    xR = poly_from_string_le(inf["xR"])
    lifts = []
    for x in xs:
        L = E.lift(x)
        if L is None:
            return False, "x=%#x not on E" % x
        lifts.append(L)
    for s in range(8):
        P = E.add(E.add(lifts[0][s & 1], lifts[1][(s >> 1) & 1]), lifts[2][(s >> 2) & 1])
        if P is not None and P[0] == xR:
            return True, "ok"
    return False, "no sign choice gives x_R"


cert_rows = [r for r in rows if r.get("engine") == "certificate"]
sat_rows = [r for r in rows if r.get("status") == "SAT" and r.get("config") != "default_on_null_object"]
p1_unverified_mine = []
p1_producer_false = []
n_checked = 0
for r in sat_rows:
    bits = r.get("assignment") or r.get("assignment_core_bits")
    assert bits, r["instance"]
    ok, why = my_verify(r["instance"], bits)
    n_checked += 1
    if not ok:
        p1_unverified_mine.append(dict(instance=r["instance"], engine=r["engine"], config=r["config"], why=why))
    if not (r.get("verification") or {}).get("verified"):
        p1_producer_false.append((r["instance"], r["engine"], r["config"]))
agree = len(p1_unverified_mine) == len(p1_producer_false) and \
    {(d["instance"], d["engine"], d["config"]) for d in p1_unverified_mine} == set(p1_producer_false)
P1 = dict(n_certificate_rows=len(cert_rows),
          producer_verified_true=sum(bool(r.get("verified")) for r in cert_rows),
          n_sat_answers_checked_by_me=n_checked,
          my_unverified=p1_unverified_mine,
          producer_unverified_count=len(p1_producer_false),
          my_and_producer_agree_on_which_rows=agree,
          holds=(len(p1_unverified_mine) == 0))

# ---------------- P2 ----------------
GROEBNER = {"macaulay2_F4_ZZ2_fieldeqs", "singular_std_GF2_fieldeqs"}
P2 = dict(cells={}, holds=None)
p2_vals = []
for cell in ("n15l5", "n17l6", "n19l6"):
    for lab in ("S", "U"):
        wd = table.get(f"{cell}/{lab}/wdsat/default")
        for eng in GROEBNER:
            for k, t in table.items():
                c, l_, e, cfg = k.split("/")
                if (c, l_, e) == (cell, lab, eng) and t["n_finished"] > 0:
                    ratio = wd["median_wall_s"] / t["median_wall_s"]
                    P2["cells"][k] = dict(wdsat_over_groebner=ratio, holds=ratio <= 0.1)
                    p2_vals.append(ratio <= 0.1)
if p2_vals:
    P2["holds"] = all(p2_vals)

# ---------------- P3 ----------------
byinst = defaultdict(dict)
for r in rows:
    if r.get("engine") == "wdsat":
        byinst[r["instance"]][r["config"]] = r
p3a_mismatch = []
for inst, d in byinst.items():
    if "default" in d and "core_order" in d:
        if d["default"]["conflicts"] != d["core_order"]["conflicts"] or d["default"]["status"] != d["core_order"]["status"]:
            p3a_mismatch.append(inst)
P3a = dict(n_instances=sum(1 for d in byinst.values() if "core_order" in d), mismatching=p3a_mismatch, holds=not p3a_mismatch)

P3b = {}
for cell in ("n15l5", "n17l6", "n19l6"):
    for lab in ("S", "U"):
        nc = [r for r in rows if r.get("config") == "noncore_first" and r["cell"] == cell and r["label"] == lab]
        insts = [r["instance"] for r in nc]
        censored = [r["wall_s"] if r["status"] in FIN else r["timeout_s"] for r in nc]
        assert all(r["timeout_s"] == 120 for r in nc)
        dflt_same = [byinst[i]["default"]["wall_s"] for i in insts]
        m_nc, m_d = med(censored), med(dflt_same)
        P3b[f"{cell}/{lab}"] = dict(instances=insts, n_noncore_finished=sum(r["status"] in FIN for r in nc),
                                    n_noncore_timeout=sum(r["status"] == "budget_stop_timeout" for r in nc),
                                    noncore_censored_median_wall_s=m_nc, default_same5_median_wall_s=m_d,
                                    default_all10_median_wall_s=table[f"{cell}/{lab}/wdsat/default"]["median_wall_s"],
                                    ratio_lower_bound_same5=m_nc / m_d, holds=(m_nc / m_d) >= 2)
P3c = {}
for cell in ("n17l6", "n19l6"):
    for lab in ("S", "U"):
        cms = [r for r in rows if r.get("engine") == "cryptominisat5" and r.get("config") == "pure_cnf" and r["cell"] == cell and r["label"] == lab]
        insts = [r["instance"] for r in cms]
        cms_fin = [r["wall_s"] for r in cms if r["status"] in FIN]
        m_cms = med(cms_fin)
        wd_all = table[f"{cell}/{lab}/wdsat/default"]["median_wall_s"]
        wd_same = med([byinst[i]["default"]["wall_s"] for i in insts])
        P3c[f"{cell}/{lab}"] = dict(instances=insts, n_cms_finished=len(cms_fin), cms_pure_cnf_median_wall_s=m_cms,
                                    wdsat_default_all10_median_wall_s=wd_all, wdsat_default_same5_median_wall_s=wd_same,
                                    ratio_vs_all10=m_cms / wd_all, ratio_vs_same5=m_cms / wd_same,
                                    holds_vs_all10=(m_cms / wd_all) >= 10, holds_vs_same5=(m_cms / wd_same) >= 10)
P3 = dict(a=P3a, b=P3b, c=P3c,
          holds=P3a["holds"] and all(v["holds"] for v in P3b.values()) and all(v["holds_vs_all10"] and v["holds_vs_same5"] for v in P3c.values()))

# ---------------- P4 ----------------
P4 = {}
for cell in ("n15l5", "n17l6", "n19l6"):
    for lab in ("S", "U"):
        d = table[f"{cell}/{lab}/wdsat/default"]["median_wall_s"]
        g = table[f"{cell}/{lab}/wdsat/gauss_elim"]["median_wall_s"]
        resolvable = d > 0.05
        P4[f"{cell}/{lab}"] = dict(default_median_wall_s=d, gauss_elim_median_wall_s=g, gauss_over_default=g / d,
                                   resolvable=resolvable, speedup_more_than_10pct=(g < 0.9 * d),
                                   verdict=("holds" if not (g < 0.9 * d) else "FAILS") if resolvable else "unresolvable")
P4_holds = all(v["verdict"] != "FAILS" for v in P4.values())

# ---------------- P5 ----------------
P5 = dict(sat={}, groebner={}, holds=None)
sat_configs = [("wdsat", "default"), ("cryptominisat5", "cnf_xor"), ("cryptominisat5", "pure_cnf"),
               ("wdsat", "core_order"), ("wdsat", "symmetry"), ("wdsat", "gauss_elim")]
p5_sat_ok = []
for cell in ("n15l5", "n17l6", "n19l6"):
    for eng, cfg in sat_configs:
        s = table.get(f"{cell}/S/{eng}/{cfg}")
        u = table.get(f"{cell}/U/{eng}/{cfg}")
        if not s or not u or s["median_conflicts"] is None or u["median_conflicts"] is None:
            continue
        ratio = u["median_conflicts"] / s["median_conflicts"] if s["median_conflicts"] else float("inf")
        P5["sat"][f"{cell}/{eng}/{cfg}"] = dict(S_median_conflicts=s["median_conflicts"], U_median_conflicts=u["median_conflicts"],
                                                U_over_S=ratio, holds=ratio >= 2)
        if (eng, cfg) in (("wdsat", "default"), ("cryptominisat5", "cnf_xor")):
            p5_sat_ok.append(ratio >= 2)
    for eng in GROEBNER:
        for k, t in table.items():
            c, l_, e, cfg = k.split("/")
            if c == cell and e == eng and t["n_finished"] > 0:
                P5["groebner"][k] = t["median_cpu_s"]
P5["sat_clause_holds_for_wdsat_default_and_cms_cnf_xor"] = all(p5_sat_ok)
P5["sat_clause_holds_for_every_sat_engine_config_with_data"] = all(v["holds"] for v in P5["sat"].values())
P5["groebner_clause"] = "null: no Groebner engine finished any row"
P5["holds"] = all(p5_sat_ok)  # SAT clause only; Groebner clause unevaluable

# ---------------- P6 ----------------
P6 = dict(cells={}, holds=None)
p6_vals = []
for cell in ("n15l5", "n17l6", "n19l6"):
    nul = [r for r in rows if r.get("config") == "default_on_null_object" and r["cell"] == cell]
    nul_fin = [r for r in nul if r["status"] in FIN]
    m_null = med([r["conflicts"] for r in nul_fin])
    m_u = table[f"{cell}/U/wdsat/default"]["median_conflicts"]
    m_s = table[f"{cell}/S/wdsat/default"]["median_conflicts"]
    ratio = (m_null / m_u) if m_null is not None else None
    # censored reading: timeouts have conflicts >= min finishing? we report count and the min conflicts among timeouts if recorded
    P6["cells"][cell] = dict(n_null_rows=len(nul), n_null_finished=len(nul_fin), n_null_timeout=len(nul) - len(nul_fin),
                             null_median_conflicts_finished=m_null, structured_U_median_conflicts=m_u,
                             structured_S_median_conflicts=m_s, ratio_null_over_U=ratio,
                             holds=(ratio >= 10) if ratio is not None else None,
                             null_finished_conflicts_sorted=sorted(r["conflicts"] for r in nul_fin),
                             null_min_finished_conflicts_over_U_median=(min(r["conflicts"] for r in nul_fin) / m_u) if nul_fin else None)
    p6_vals.append(P6["cells"][cell]["holds"])
P6["holds_every_cell_strict"] = all(v is True for v in p6_vals)
P6["holds_ignoring_null_cells"] = all(v for v in p6_vals if v is not None)
P6["holds"] = P6["holds_every_cell_strict"] if all(v is not None for v in p6_vals) else None

out = dict(table=table, P1=P1, P2=P2, P3=P3, P4=dict(cells=P4, holds=P4_holds), P5=P5, P6=P6,
           verdicts=dict(P1=P1["holds"], P2=P2["holds"], P3=P3["holds"], P4=P4_holds, P5=P5["holds"], P6=P6["holds"]))
json.dump(out, open(OUT, "w"), indent=1, default=str)
print(json.dumps(out["verdicts"]))
print("P1:", json.dumps({k: v for k, v in P1.items()}, indent=1)[:1500])
print("P3a:", P3a)
print("P3b:")
for k, v in P3b.items():
    print(f"  {k}: noncore censored median {v['noncore_censored_median_wall_s']:.4f} ({v['n_noncore_finished']} fin/{v['n_noncore_timeout']} to) ; default same5 median {v['default_same5_median_wall_s']:.4f} ; default all10 median {v['default_all10_median_wall_s']:.4f} ; ratio(same5) {v['ratio_lower_bound_same5']:.2f}")
print("P3c:")
for k, v in P3c.items():
    print(f"  {k}: cms pure_cnf median {v['cms_pure_cnf_median_wall_s']:.4f} (n={v['n_cms_finished']}); wdsat default all10 {v['wdsat_default_all10_median_wall_s']:.4f} -> ratio {v['ratio_vs_all10']:.2f}; same5 {v['wdsat_default_same5_median_wall_s']:.4f} -> ratio {v['ratio_vs_same5']:.2f}")
print("P4:")
for k, v in P4.items():
    print(f"  {k}: default {v['default_median_wall_s']:.4f} gauss {v['gauss_elim_median_wall_s']:.4f} ratio {v['gauss_over_default']:.2f} {v['verdict']}")
print("P5 sat:")
for k, v in P5["sat"].items():
    print(f"  {k}: S {v['S_median_conflicts']} U {v['U_median_conflicts']} ratio {v['U_over_S']:.2f} holds {v['holds']}")
print("P6:")
for k, v in P6["cells"].items():
    print(f"  {k}: null median {v['null_median_conflicts_finished']} ({v['n_null_finished']} fin / {v['n_null_timeout']} to) ; U median {v['structured_U_median_conflicts']} ; ratio {v['ratio_null_over_U']} ; min-finished-null/U {v['null_min_finished_conflicts_over_U_median']}")
print(" P6 strict every-cell:", P6["holds_every_cell_strict"], "; ignoring null cells:", P6["holds_ignoring_null_cells"])
print("\nTABLE (cell/label/engine/config: n_fin/n_rows, med wall, med cpu, med conflicts)")
for k, t in table.items():
    print(f"  {k}: {t['n_finished']}/{t['n_rows']} wall={t['median_wall_s']} cpu={t['median_cpu_s']} conf={t['median_conflicts']}")
