#!/usr/bin/env python3
"""EXP-R6-001 analysis: consolidate all runs, per-cell costs, exponent fits with
bootstrap CIs, control comparisons, censoring table. Reads runs/*/raw.json,
writes analysis.json. No Sage needed."""
import json, math, random, statistics as st, glob, os

ROOT = os.path.dirname(os.path.abspath(__file__))
RUNS = sorted(glob.glob(os.path.join(ROOT, "runs", "RUN-EXP-R6-001-*", "raw.json")))

def load(p):
    with open(p) as f:
        return json.load(f)

runs = {}
for p in RUNS:
    s = load(p)
    runs[s.get("run_id") or os.path.basename(os.path.dirname(p))] = s

# ---------------------------------------------------------------- collect
solves, nulls, rhos, c3s, probes, attempts, units = [], [], [], [], [], [], []
for rid, s in runs.items():
    for r in s["records"].get("solves", []):
        r["run"] = rid; solves.append(r)
    for r in s["records"].get("nulls", []):
        r["run"] = rid; nulls.append(r)
    for r in s["records"].get("rho", []):
        r["run"] = rid; rhos.append(r)
    for r in s["records"].get("control3", []):
        if r.get("status") not in ("not_available", "invalid"):
            r["run"] = rid; c3s.append(r)
    for r in s["records"].get("probe", []):
        r["run"] = rid; probes.append(r)
    for r in s["records"].get("attempts", []):
        r["run"] = rid; attempts.append(r)
    for r in s["records"].get("units", []):
        r["run"] = rid; units.append(r)

# group-op-equivalent conversion: use units measured in the same run when present
GOP = {}
for u in units:
    GOP.setdefault(u["run"], u["group_op_s"])
GOP_DEFAULT = 5.09e-6  # RUN-b measured at p~2^13 (mac arm64)

def goe(r):
    g = GOP.get(r["run"], GOP_DEFAULT)
    return r["total_s"] / g

# ---------------------------------------------------------------- per-cell
cells = {}
for r in solves:
    key = (r["m"], r["F"], r["arm"])
    cells.setdefault(key, []).append(r)
cell_table = []
for (m, F, arm), rs in sorted(cells.items()):
    gb = [r["gb_s"] for r in rs]
    tot = [r["total_s"] for r in rs]
    cell_table.append({
        "m": m, "F": F, "arm": arm, "n": len(rs),
        "n_empty": sum(1 for r in rs if r["status"] == "empty"),
        "q_median": st.median(r["q"] for r in rs),
        "gb_median_s": st.median(gb), "gb_mean_s": st.mean(gb),
        "total_median_s": st.median(tot), "total_mean_s": st.mean(tot),
        "total_mean_goe": st.mean([goe(r) for r in rs]),
        "solve_only_mean_s": st.mean([r["gb_s"] + r["variety_s"] for r in rs]),
        "build_mean_s": st.mean([r["build_s"] for r in rs]),
        "d_reg_max": max(r["d_reg"] for r in rs),
        "d_reg_median": st.median(r["d_reg"] for r in rs),
        "vdim_median": st.median([r["vdim"] for r in rs if r["vdim"] is not None] or [0]),
        "vdim_max": max([r["vdim"] for r in rs if r["vdim"] is not None] or [0]),
        "n_verified_total": sum(r["n_verified"] for r in rs),
        "n_degenerate_total": sum(r["n_degenerate"] for r in rs),
        "n_fallback": sum(1 for r in rs if r.get("method") == "singular_variety"),
    })

# ------------------------------------------------------- exponent fit (m=3)
def ols(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    a = sxy / sxx
    b = my - a * mx
    return a, b

m3_pts = [(math.log2(r["q"]), math.log2(r["total_s"])) for r in solves if r["m"] == 3]
alpha_all, beta_all = ols([p[0] for p in m3_pts], [p[1] for p in m3_pts]) if len(m3_pts) > 2 else (None, None)

# bootstrap: resample targets within (m,F,arm) cells, refit
random.seed(20260718)
boot = []
by_cell = {}
for r in solves:
    if r["m"] != 3:
        continue
    by_cell.setdefault((r["m"], r["F"], r["arm"]), []).append(r)
keys = sorted(by_cell)
for _ in range(2000):
    xs, ys = [], []
    for k in keys:
        rs = by_cell[k]
        for _i in range(len(rs)):
            r = random.choice(rs)
            xs.append(math.log2(r["q"])); ys.append(math.log2(r["total_s"]))
    if len(set(xs)) > 1:
        a, b = ols(xs, ys)
        boot.append(a)
boot.sort()
ci = (boot[int(0.05 * len(boot))], boot[int(0.95 * len(boot))]) if boot else (None, None)

# per-cell-mean fit (each cell one point: mean log cost vs mean log q)
cm = []
for (m, F, arm), rs in sorted(by_cell.items()):
    cm.append((st.mean([math.log2(r["q"]) for r in rs]),
               st.mean([math.log2(r["total_s"]) for r in rs]),
               len(rs), F, arm))
alpha_cells, beta_cells = ols([c[0] for c in cm], [c[1] for c in cm]) if len(cm) > 2 else (None, None)

# ---------------------------------------------------------------- rho fit
rho_pts = [(math.log2(r["q"]), math.log2(r["ops"])) for r in rhos if r.get("ops")]
a_rho, b_rho = ols([p[0] for p in rho_pts], [p[1] for p in rho_pts])
rho_consts = [r["ops"] / math.sqrt(r["q"]) for r in rhos if r.get("ops")]
random.seed(7)
boot_r = []
for _ in range(2000):
    samp = [random.choice(rho_pts) for _ in rho_pts]
    if len(set(x for x, _ in samp)) > 1:
        boot_r.append(ols([p[0] for p in samp], [p[1] for p in samp])[0])
boot_r.sort()
ci_rho = (boot_r[int(0.05 * len(boot_r))], boot_r[int(0.95 * len(boot_r))])

# ---------------------------------------------------------------- controls
null_table = {}
for r in nulls:
    null_table.setdefault((r["m"], r["F"]), []).append(r["gb_s"])
null_summary = [{"m": m, "F": F, "n": len(v), "gb_mean_s": st.mean(v),
                 "gb_median_s": st.median(v)} for (m, F), v in sorted(null_table.items())]
c3_table = {}
for r in c3s:
    c3_table.setdefault((r["m"], r["F"]), []).append(r)
c3_summary = [{"m": m, "F": F, "n": len(v),
               "gb_mean_s": st.mean([r["gb_s"] for r in v]),
               "isogeny_degrees": sorted(set(r["isogeny_degree"] for r in v))}
              for (m, F), v in sorted(c3_table.items())]

# curve-to-curve (control 2): per-curve mean gb within each cell-arm
curve_spread = []
for (m, F, arm), rs in sorted(by_cell.items()):
    per_curve = {}
    for r in rs:
        per_curve.setdefault(r["role"], []).append(r["gb_s"])
    if len(per_curve) > 1:
        means = {k: st.mean(v) for k, v in per_curve.items()}
        curve_spread.append({"m": m, "F": F, "arm": arm,
                             "curve_mean_gb": means,
                             "max_min_ratio": max(means.values()) / min(means.values())})

# probe table
probe_table = [{"kind": r["kind"], "F": r["F"], "gb_s": r["gb_s"], "d_reg": r["d_reg"],
                "vdim": r["vdim"], "method": r.get("method")} for r in probes]

out = {
    "runs": {rid: {"complete": s.get("complete"), "termination": s.get("termination"),
                   "notes": s.get("notes")} for rid, s in runs.items()},
    "cell_table": cell_table,
    "m3_fit": {"alpha_per_target": alpha_all, "ci90": ci, "n_targets": len(m3_pts),
               "alpha_per_cell_mean": alpha_cells, "n_cells": len(cm),
               "cell_means": [{"log2q": c[0], "log2cost": c[1], "n": c[2], "F": c[3], "arm": c[4]} for c in cm]},
    "rho_fit": {"alpha": a_rho, "ci90": ci_rho, "const_mean": st.mean(rho_consts),
                "const_median": st.median(rho_consts), "const_theory": 1.2533141373155001,
                "n": len(rho_pts)},
    "null_summary": null_summary,
    "control3_summary": c3_summary,
    "control2_curve_spread": curve_spread,
    "probe_table": probe_table,
    "attempts": attempts,
    "units": units,
}
with open(os.path.join(ROOT, "analysis.json"), "w") as f:
    json.dump(out, f, indent=1)

# ---------------------------------------------------------------- print
print("=== cells (m,F,arm): n, empty, q_med, gb_med_s, total_mean_s, total_mean_goe, d_reg med/max, vdim med/max")
for c in cell_table:
    print(f"  m{c['m']} F={c['F']:>3} {c['arm']:<8} n={c['n']:>2} empty={c['n_empty']:>2} "
          f"q~{c['q_median']:.0f} gb={c['gb_median_s']:.2f}s tot={c['total_mean_s']:.2f}s "
          f"goe={c['total_mean_goe']:.3g} d_reg={c['d_reg_median']}/{c['d_reg_max']} "
          f"vdim={c['vdim_median']}/{c['vdim_max']} fb={c['n_fallback']}")
print(f"=== m3 exponent (per-target): alpha={alpha_all:.3f} CI90=({ci[0]:.3f},{ci[1]:.3f}) n={len(m3_pts)}")
print(f"    m3 exponent (cell means): alpha={alpha_cells:.3f} over {len(cm)} cells")
print(f"=== rho: alpha={a_rho:.4f} CI90=({ci_rho[0]:.4f},{ci_rho[1]:.4f}) const mean={st.mean(rho_consts):.3f} med={st.median(rho_consts):.3f} (theory 1.2533) n={len(rho_pts)}")
print("=== nulls:", null_summary)
print("=== c3:", c3_summary)
print("=== curve spread:", [(c['F'], c['arm'], round(c['max_min_ratio'],2)) for c in curve_spread])
