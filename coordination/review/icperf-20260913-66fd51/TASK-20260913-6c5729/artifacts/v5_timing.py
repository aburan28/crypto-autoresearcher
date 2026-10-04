#!/usr/bin/env python3
"""Joint V5 of REVIEW-ICPERF-20260913-66fd51 (TASK-20260913-6c5729): timing integrity.
Pure arithmetic over results.jsonl.

(1) recorded_at gaps between consecutive rows; wall_s vs cpu_s on every measured row.
(2) P3c (corrected per-cell ratios, both comparators) and P4 medians recomputed EXCLUDING
    rows with loadavg1_at_start > 2; per-cell change in percent; verdict flips.
(3) rows with wall_s > timeout_s + 1.
(extra) monotonicity of max_rss_kb_children_highwater in recording order (it is a
    RUSAGE_CHILDREN high-water mark, so a per-row reading is only valid until the first
    larger child has run).
"""
import json
import os
import statistics as st
from collections import Counter, defaultdict
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = "/workspace/experiments/EXP-ICPERF-66fd51/runs/RUN-ICPERF-305ca3"
rows = [json.loads(l) for l in open(f"{RUN}/results.jsonl") if l.strip()]
assert len(rows) == 504


def ts(s):
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).timestamp()


def med(v):
    v = [x for x in v if x is not None]
    return st.median(v) if v else None


def finished(r):
    s = r.get("status") or ""
    return bool(s) and not (s.startswith("budget_stop") or s.startswith("infrastructure") or s == "unknown")


out = {}
# ---------------------------------------------------------------- (1) gaps and wall vs cpu
order = sorted(range(len(rows)), key=lambda i: (ts(rows[i]["recorded_at"]), i))
gaps = []
for a, b in zip(order, order[1:]):
    g = ts(rows[b]["recorded_at"]) - ts(rows[a]["recorded_at"])
    gaps.append((g, rows[a]["instance"], rows[a]["engine"], rows[a]["config"], rows[a]["recorded_at"],
                 rows[b]["instance"], rows[b]["engine"], rows[b]["config"], rows[b]["recorded_at"], rows[b].get("wall_s")))
gaps_sorted = sorted(gaps, reverse=True)
measured = [r for r in rows if r.get("wall_s") is not None]
span = ts(rows[order[-1]]["recorded_at"]) - ts(rows[order[0]]["recorded_at"])
sum_wall = sum(r["wall_s"] for r in measured)
big = [g for g in gaps_sorted if g[0] > 600]
# a recorded_at gap is "explained" by the following row's own wall if gap - wall_next is small
out["gaps"] = {
    "n_rows": len(rows), "first_recorded_at": rows[order[0]]["recorded_at"], "last_recorded_at": rows[order[-1]]["recorded_at"],
    "span_s": span, "sum_wall_s_measured_rows": round(sum_wall, 1), "span_minus_sum_wall_s": round(span - sum_wall, 1),
    "gaps_over_600s": [{"gap_s": g[0], "after_row": (g[1], g[2], g[3], g[4]), "before_row": (g[5], g[6], g[7], g[8]),
                        "next_row_wall_s": g[9], "gap_minus_next_wall_s": round(g[0] - (g[9] or 0), 1)} for g in big],
    "top10_gaps_s": [round(g[0], 1) for g in gaps_sorted[:10]],
    "sum_of_gaps_over_600s": round(sum(g[0] for g in big), 1),
    "note": "recorded_at is written at row END (it follows the row's own wall), so a gap of G before a row of wall w "
            "contains at most G - w of idle/suspension time between rows",
}

wc = []
for r in measured:
    w, c = r["wall_s"], r.get("cpu_s")
    if c is None:
        continue
    wc.append((w - c, (w / c if c > 0 else None), r["instance"], r["engine"], r["config"], r["status"], w, c, r.get("timeout_s")))
wc_sorted = sorted(wc, key=lambda x: -x[0])
out["wall_vs_cpu"] = {
    "rows_with_cpu": len(wc),
    "rows_wall_minus_cpu_over_2s": [x for x in wc_sorted if x[0] > 2.0],
    "rows_wall_over_2x_cpu_and_wall_over_1s": [x for x in wc_sorted if x[1] is not None and x[1] > 2.0 and x[6] > 1.0],
    "rows_cpu_over_wall_by_more_than_1s (multi-threaded child)": [x for x in wc_sorted if x[0] < -1.0],
    "max_wall_minus_cpu_s": round(wc_sorted[0][0], 3) if wc_sorted else None,
    "min_wall_minus_cpu_s": round(wc_sorted[-1][0], 3) if wc_sorted else None,
    "per_engine_max_wall_minus_cpu_s": {e: round(max(x[0] for x in wc if x[3] == e), 3) for e in sorted({x[3] for x in wc})},
}

# ---------------------------------------------------------------- (3) timeouts
over = [(r["instance"], r["engine"], r["config"], r["status"], r["wall_s"], r["timeout_s"]) for r in measured
        if r.get("timeout_s") and r["wall_s"] > r["timeout_s"] + 1]
timeouts = [r for r in measured if r["status"] == "budget_stop_timeout"]
out["timeout_check"] = {
    "rows_with_wall_over_timeout_plus_1s": over,
    "n_budget_stop_timeout_rows": len(timeouts),
    "timeout_rows_wall_minus_timeout_s_max": round(max((r["wall_s"] - r["timeout_s"]) for r in timeouts), 4) if timeouts else None,
    "timeout_rows_wall_minus_timeout_s_min": round(min((r["wall_s"] - r["timeout_s"]) for r in timeouts), 4) if timeouts else None,
    "timed_out_flag_consistent": all((r["status"] == "budget_stop_timeout") == bool(r.get("timed_out")) for r in measured),
}

# ---------------------------------------------------------------- (2) load-average exclusion sensitivity
LOAD = 2.0
hi = [r for r in measured if (r.get("loadavg1_at_start") or 0) > LOAD]
out["load"] = {
    "threshold": LOAD, "rows_measured": len(measured), "rows_over_threshold": len(hi),
    "by_phase": dict(Counter(r["phase"] for r in hi)),
    "by_phase_total": dict(Counter(r["phase"] for r in measured)),
    "by_engine_config_over": dict(Counter(f"{r['engine']}/{r['config']}" for r in hi)),
    "loadavg_range_over_threshold": (min(r["loadavg1_at_start"] for r in hi), max(r["loadavg1_at_start"] for r in hi)) if hi else None,
    "loadavg_percentiles_all": {p: round(sorted(r["loadavg1_at_start"] for r in measured)[int(p / 100 * (len(measured) - 1))], 2) for p in (0, 25, 50, 75, 90, 100)},
}


def sel(rs, **kw):
    return [r for r in rs if all(r.get(k) == v for k, v in kw.items())]


def medians(rs):
    """per (cell,label,engine,config): median wall over finished rows, count."""
    d = {}
    for cell in ("n15l5", "n17l6", "n19l6"):
        for lab in ("S", "U"):
            for eng, cfg in (("wdsat", "default"), ("wdsat", "gauss_elim"), ("cryptominisat5", "pure_cnf")):
                fin = [r for r in sel(rs, cell=cell, label=lab, engine=eng, config=cfg) if finished(r)]
                d[(cell, lab, eng, cfg)] = (med([r["wall_s"] for r in fin]), len(fin))
    return d


all_m = medians(measured)
lo_m = medians([r for r in measured if (r.get("loadavg1_at_start") or 0) <= LOAD])


def pct(a, b):
    return None if (a is None or b is None or a == 0) else round(100.0 * (b - a) / a, 1)


sens = {"P3c": {}, "P4": {}, "medians": {}}
for key, (m_all, n_all) in all_m.items():
    m_lo, n_lo = lo_m[key]
    sens["medians"]["/".join(key)] = {"all_rows": (m_all, n_all), "excl_highload": (m_lo, n_lo), "change_pct": pct(m_all, m_lo)}

for cell in ("n17l6", "n19l6"):
    for lab in ("S", "U"):
        # corrected P3c: cms pure_cnf median / wdsat default median (all-10 comparator), and matched-instance comparator
        def p3c(rs):
            pc = [r for r in sel(rs, cell=cell, label=lab, engine="cryptominisat5", config="pure_cnf") if finished(r)]
            wd = [r for r in sel(rs, cell=cell, label=lab, engine="wdsat", config="default") if finished(r)]
            insts = {r["instance"] for r in pc}
            wd_m = [r for r in wd if r["instance"] in insts]
            a, b, c = med([r["wall_s"] for r in pc]), med([r["wall_s"] for r in wd]), med([r["wall_s"] for r in wd_m])
            return {"cms_pure_cnf_median": a, "wdsat_default_median_all": b, "wdsat_default_median_matched": c,
                    "n_pc": len(pc), "n_wd": len(wd), "n_wd_matched": len(wd_m),
                    "ratio_all10": (a / b) if a is not None and b else None, "ratio_matched": (a / c) if a is not None and c else None}
        A, L = p3c(measured), p3c([r for r in measured if (r.get("loadavg1_at_start") or 0) <= LOAD])
        sens["P3c"][f"{cell}/{lab}"] = {
            "all_rows": A, "excl_highload": L,
            "ratio_all10_change_pct": pct(A["ratio_all10"], L["ratio_all10"]),
            "ratio_matched_change_pct": pct(A["ratio_matched"], L["ratio_matched"]),
            "holds_all10 (>=10x)": (A["ratio_all10"] is not None and A["ratio_all10"] >= 10, (L["ratio_all10"] >= 10) if L["ratio_all10"] is not None else None),
            "holds_matched (>=10x)": (A["ratio_matched"] is not None and A["ratio_matched"] >= 10, (L["ratio_matched"] >= 10) if L["ratio_matched"] is not None else None),
        }
for cell in ("n15l5", "n17l6", "n19l6"):
    for lab in ("S", "U"):
        def p4(rs):
            g = [r for r in sel(rs, cell=cell, label=lab, engine="wdsat", config="gauss_elim") if finished(r)]
            d = [r for r in sel(rs, cell=cell, label=lab, engine="wdsat", config="default") if finished(r)]
            gm, dm = med([r["wall_s"] for r in g]), med([r["wall_s"] for r in d])
            holds = None if (gm is None or dm is None or dm <= 0.05) else (gm >= 0.9 * dm)
            return {"gauss_elim_median": gm, "default_median": dm, "n_g": len(g), "n_d": len(d),
                    "ratio_gauss_over_default": (gm / dm) if gm is not None and dm else None, "holds": holds}
        A, L = p4(measured), p4([r for r in measured if (r.get("loadavg1_at_start") or 0) <= LOAD])
        sens["P4"][f"{cell}/{lab}"] = {"all_rows": A, "excl_highload": L,
                                       "ratio_change_pct": pct(A["ratio_gauss_over_default"], L["ratio_gauss_over_default"]),
                                       "holds": (A["holds"], L["holds"])}
flips = []
for k, v in sens["P3c"].items():
    for kk in ("holds_all10 (>=10x)", "holds_matched (>=10x)"):
        a, b = v[kk]
        if b is not None and a != b:
            flips.append(("P3c", k, kk, a, b))
for k, v in sens["P4"].items():
    a, b = v["holds"]
    if b is not None and a != b:
        flips.append(("P4", k, a, b))
# The exclusion test is underpowered where the high-load rows ARE the phase (D). The direct
# test for scheduling contention is wall - cpu on the row: a descheduled single-threaded
# process accumulates wall without cpu. So also: (i) wall-cpu on the phase-D rows and the P3c
# numerator rows; (ii) P3c and P4 recomputed on cpu_s for both numerator and denominator.
phaseD = [r for r in measured if r["phase"] == "D"]
sens["phase_D_wall_minus_cpu"] = {
    "rows": len(phaseD),
    "max_wall_minus_cpu_s": round(max(r["wall_s"] - r["cpu_s"] for r in phaseD), 3),
    "max_relative_(wall-cpu)/wall": round(max((r["wall_s"] - r["cpu_s"]) / r["wall_s"] for r in phaseD if r["wall_s"] > 0), 4),
    "max_relative_over_rows_with_wall_over_1s": round(max(((r["wall_s"] - r["cpu_s"]) / r["wall_s"] for r in phaseD if r["wall_s"] > 1.0), default=0), 4),
}
sens["P3c_cpu_based"] = {}
for cell in ("n17l6", "n19l6"):
    for lab in ("S", "U"):
        pc = [r for r in sel(measured, cell=cell, label=lab, engine="cryptominisat5", config="pure_cnf") if finished(r)]
        wd = [r for r in sel(measured, cell=cell, label=lab, engine="wdsat", config="default") if finished(r)]
        insts = {r["instance"] for r in pc}
        wd_m = [r for r in wd if r["instance"] in insts]
        a, b, c = med([r["cpu_s"] for r in pc]), med([r["cpu_s"] for r in wd]), med([r["cpu_s"] for r in wd_m])
        sens["P3c_cpu_based"][f"{cell}/{lab}"] = {
            "cms_pure_cnf_cpu_median": a, "wdsat_default_cpu_median_all": b, "wdsat_default_cpu_median_matched": c,
            "ratio_all10_cpu": a / b if b else None, "ratio_matched_cpu": a / c if c else None,
            "holds_all10_cpu (>=10x)": (a / b >= 10) if b else None, "holds_matched_cpu (>=10x)": (a / c >= 10) if c else None,
            "cms_rows_(wall,cpu,loadavg)": [(r["wall_s"], r["cpu_s"], r["loadavg1_at_start"]) for r in pc],
            "wdsat_matched_rows_(wall,cpu,loadavg)": [(r["wall_s"], r["cpu_s"], r["loadavg1_at_start"]) for r in wd_m],
        }
sens["P4_cpu_based"] = {}
for cell in ("n15l5", "n17l6", "n19l6"):
    for lab in ("S", "U"):
        g = [r for r in sel(measured, cell=cell, label=lab, engine="wdsat", config="gauss_elim") if finished(r)]
        d = [r for r in sel(measured, cell=cell, label=lab, engine="wdsat", config="default") if finished(r)]
        gm, dm = med([r["cpu_s"] for r in g]), med([r["cpu_s"] for r in d])
        sens["P4_cpu_based"][f"{cell}/{lab}"] = {"gauss_elim_cpu_median": gm, "default_cpu_median": dm,
                                                 "ratio": gm / dm if dm else None,
                                                 "holds": None if (dm is None or dm <= 0.05) else gm >= 0.9 * dm}
sens["verdict_flips"] = flips
sens["max_abs_change_pct"] = {
    "P3c_all10": max((abs(v["ratio_all10_change_pct"]) for v in sens["P3c"].values() if v["ratio_all10_change_pct"] is not None), default=None),
    "P3c_matched": max((abs(v["ratio_matched_change_pct"]) for v in sens["P3c"].values() if v["ratio_matched_change_pct"] is not None), default=None),
    "P4": max((abs(v["ratio_change_pct"]) for v in sens["P4"].values() if v["ratio_change_pct"] is not None), default=None),
}
out["exclusion_sensitivity"] = sens

# ---------------------------------------------------------------- (extra) RSS high-water monotonicity
rss = [(rows[i]["recorded_at"], rows[i].get("max_rss_kb_children_highwater"), rows[i]["engine"], rows[i]["phase"]) for i in order
       if rows[i].get("max_rss_kb_children_highwater") is not None]
nondecreasing = all(a[1] <= b[1] for a, b in zip(rss, rss[1:]))
first_big = next((x for x in rss if x[1] > 1_000_000), None)
out["rss_highwater"] = {
    "rows": len(rss), "nondecreasing_in_recording_order": nondecreasing,
    "n_decreases": sum(1 for a, b in zip(rss, rss[1:]) if b[1] < a[1]),
    "first_row_over_1GB": first_big,
    "rows_after_first_over_1GB_reporting_the_same_value": (sum(1 for x in rss if x[1] == first_big[1]) if first_big else None),
    "distinct_values_after_first_over_1GB": (len({x[1] for x in rss if ts(x[0]) >= ts(first_big[0])}) if first_big else None),
    "reading": "RUSAGE_CHILDREN ru_maxrss is the maximum over all children ever waited for; once one child has used more, "
               "every later row reports that child's peak, not its own",
}

json.dump(out, open(f"{HERE}/v5_timing.json", "w"), indent=1, default=str)

print("GAPS: span", round(span), "s; sum wall", round(sum_wall), "s; gaps>600s:", [(round(g["gap_s"]), g["after_row"][:3], g["before_row"][:3], g["next_row_wall_s"]) for g in out["gaps"]["gaps_over_600s"]])
print("WALL vs CPU: rows", len(wc), "| wall-cpu>2s:", [(round(x[0], 2), x[2], x[3], x[5], x[6], x[7]) for x in out["wall_vs_cpu"]["rows_wall_minus_cpu_over_2s"]],
      "| wall>2*cpu&wall>1s:", [(round(x[1], 2), x[2], x[3], x[5], x[6], x[7]) for x in out["wall_vs_cpu"]["rows_wall_over_2x_cpu_and_wall_over_1s"]],
      "| cpu>wall+1s:", [(round(x[0], 2), x[2], x[3], x[6], x[7]) for x in out["wall_vs_cpu"]["rows_cpu_over_wall_by_more_than_1s (multi-threaded child)"]])
print("   per-engine max wall-cpu:", out["wall_vs_cpu"]["per_engine_max_wall_minus_cpu_s"])
print("TIMEOUT:", out["timeout_check"])
print("LOAD:", {k: out["load"][k] for k in ("rows_over_threshold", "by_phase", "by_phase_total", "loadavg_range_over_threshold", "loadavg_percentiles_all")})
print("   by engine/config:", out["load"]["by_engine_config_over"])
print("P3c sensitivity:")
for k, v in sens["P3c"].items():
    print("  ", k, "all10:", round(v["all_rows"]["ratio_all10"], 2), "->", (round(v["excl_highload"]["ratio_all10"], 2) if v["excl_highload"]["ratio_all10"] else None),
          f"({v['ratio_all10_change_pct']}%)", "| matched:", round(v["all_rows"]["ratio_matched"], 2), "->",
          (round(v["excl_highload"]["ratio_matched"], 2) if v["excl_highload"]["ratio_matched"] else None), f"({v['ratio_matched_change_pct']}%)",
          "| n_pc", v["all_rows"]["n_pc"], "->", v["excl_highload"]["n_pc"], "n_wd", v["all_rows"]["n_wd"], "->", v["excl_highload"]["n_wd"])
print("P4 sensitivity:")
for k, v in sens["P4"].items():
    print("  ", k, "ratio", round(v["all_rows"]["ratio_gauss_over_default"], 3), "->",
          (round(v["excl_highload"]["ratio_gauss_over_default"], 3) if v["excl_highload"]["ratio_gauss_over_default"] else None),
          f"({v['ratio_change_pct']}%)", "n_g", v["all_rows"]["n_g"], "->", v["excl_highload"]["n_g"], "n_d", v["all_rows"]["n_d"], "->", v["excl_highload"]["n_d"], "holds", v["holds"])
print("FLIPS:", flips, "| max abs change %:", sens["max_abs_change_pct"])
print("PHASE D wall-cpu:", sens["phase_D_wall_minus_cpu"])
print("P3c cpu-based:")
for k, v in sens["P3c_cpu_based"].items():
    print("  ", k, "all10", round(v["ratio_all10_cpu"], 3), "matched", round(v["ratio_matched_cpu"], 3), "holds", v["holds_all10_cpu (>=10x)"], v["holds_matched_cpu (>=10x)"],
          "| cms (wall,cpu,load):", v["cms_rows_(wall,cpu,loadavg)"])
print("P4 cpu-based:", {k: (round(v["ratio"], 3), v["holds"]) for k, v in sens["P4_cpu_based"].items()})
print("RSS:", {k: v for k, v in out["rss_highwater"].items() if k != "reading"})
