"""Pre-declared analysis for PROTOCOL.md. Reads raw/*.csv and bench/ns_per_step.csv."""
import csv, glob, json, math
import numpy as np
from scipy import stats

L = 230603167
NAMES = ["K-tau", "K-neg"] + [f"I{i}" for i in range(1, 9)]
CLASS = {n: 2 for n in NAMES}; CLASS["K-tau"] = 2 * 37
rng = np.random.default_rng(20261005)
B = 10000


def load(name):
    ops, sec, ok, cyc = [], [], [], []
    for f in sorted(glob.glob(f"raw/{name}_r*.csv")):
        for r in csv.DictReader(open(f)):
            ops.append(int(r["ops"])); sec.append(float(r["sec"])); ok.append(int(r["ok"])); cyc.append(int(r["cycles"]))
    return np.array(ops, float), np.array(sec), np.array(ok), np.array(cyc)


def boot_ratio(x, y, level):
    """bootstrap CI for mean(x)/mean(y)"""
    bx = rng.choice(x, (B, len(x))).mean(1); by = rng.choice(y, (B, len(y))).mean(1)
    r = bx / by; a = (1 - level) / 2
    return float(x.mean() / y.mean()), float(np.quantile(r, a)), float(np.quantile(r, 1 - a))


def holm(ps):
    order = np.argsort(ps); m = len(ps); adj = np.empty(m); run = 0
    for k, i in enumerate(order):
        run = max(run, min(1, (m - k) * ps[i])); adj[i] = run
    return adj


D = {n: load(n) for n in NAMES}
out = {"arms": {}}
for n in NAMES:
    ops, sec, ok, cyc = D[n]
    th = math.sqrt(math.pi * L / (2 * CLASS[n]))
    out["arms"][n] = dict(n=len(ops), verified=int(ok.sum()), mean_ops=ops.mean(), sd_ops=ops.std(ddof=1),
                          median_ops=float(np.median(ops)), p10_ops=float(np.quantile(ops, .1)), p90_ops=float(np.quantile(ops, .9)),
                          mean_ms=sec.mean() * 1e3, median_ms=float(np.median(sec)) * 1e3, sd_ms=sec.std(ddof=1) * 1e3,
                          theory_ops=th, ops_over_theory=ops.mean() / th, cycles_per_solve=cyc.mean())

# H1: is any isogenous curve faster than K-tau?
kt_ops, kt_sec = D["K-tau"][0], D["K-tau"][1]
h1 = {}
for metric, idx, ref in (("ops", 0, kt_ops), ("sec", 1, kt_sec)):
    ps = [stats.mannwhitneyu(D[f"I{i}"][idx], ref, alternative="less").pvalue for i in range(1, 9)]
    adj = holm(np.array(ps))
    h1[metric] = {f"I{i}": dict(p_holm=float(adj[i - 1]), ratio_vs_Ktau=boot_ratio(D[f"I{i}"][idx], ref, .95)) for i in range(1, 9)}
out["H1_isogenous_faster_than_Ktau"] = h1

# H2: does curve choice inside the class matter (no tau)?
neg = ["K-neg"] + [f"I{i}" for i in range(1, 9)]
h2 = {}
for metric, idx in (("ops", 0), ("sec", 1)):
    kw = stats.kruskal(*[D[n][idx] for n in neg])
    tost = {}
    for i in range(1, 9):
        r, lo, hi = boot_ratio(D[f"I{i}"][idx], D["K-neg"][idx], .90)
        tost[f"I{i}"] = dict(ratio=r, ci90=[lo, hi], equivalent_within_5pct=bool(lo > .95 and hi < 1.05))
    h2[metric] = dict(kruskal_H=float(kw.statistic), kruskal_p=float(kw.pvalue), tost_vs_Kneg=tost)
out["H2_curve_choice_without_tau"] = h2

# per-step timing
ns = {n: [] for n in NAMES}
for r in csv.reader(open("bench/ns_per_step.csv")):
    ns[r[0]].append(float(r[2]))
ns = {n: np.array(v) for n, v in ns.items()}
kw = stats.kruskal(*[ns[n] for n in neg])
step = {}
for n in NAMES:
    v = ns[n]
    bm = np.median(rng.choice(v, (B, len(v))), 1) / np.median(rng.choice(ns["K-neg"], (B, len(ns["K-neg"]))), 1)
    step[n] = dict(reps=len(v), median_ns=float(np.median(v)), iqr_ns=[float(np.quantile(v, .25)), float(np.quantile(v, .75))],
                   ratio_vs_Kneg=float(np.median(v) / np.median(ns["K-neg"])), ci90=[float(np.quantile(bm, .05)), float(np.quantile(bm, .95))])
out["per_step_ns"] = dict(kruskal_p_neg_arms=float(kw.pvalue), arms=step)

# speedup from Frobenius
out["speedup_Kneg_over_Ktau"] = dict(ops=boot_ratio(D["K-neg"][0], kt_ops, .95), sec=boot_ratio(D["K-neg"][1], kt_sec, .95),
                                     ideal=math.sqrt(37))
json.dump(out, open("results.json", "w"), indent=1, default=float)

# console summary
print(f"{'arm':6} {'n':>5} {'ok':>5} {'mean ops':>9} {'sd':>7} {'p10':>7} {'p90':>7} {'ops/theory':>10} {'mean ms':>8} {'ns/step':>8}")
for n in NAMES:
    a = out["arms"][n]
    print(f"{n:6} {a['n']:5d} {a['verified']:5d} {a['mean_ops']:9.0f} {a['sd_ops']:7.0f} {a['p10_ops']:7.0f} {a['p90_ops']:7.0f} {a['ops_over_theory']:10.3f} {a['mean_ms']:8.3f} {step[n]['median_ns']:8.1f}")
print("\nH1 (isogenous faster than K-tau?)  min Holm p:",
      {m: min(v["p_holm"] for v in h1[m].values()) for m in h1},
      " min ratio lower CI:", {m: min(v["ratio_vs_Ktau"][1] for v in h1[m].values()) for m in h1})
for m in h2:
    print(f"H2 {m}: KW p={h2[m]['kruskal_p']:.3f}; ratios vs K-neg:",
          ", ".join(f"{k}={v['ratio']:.3f}[{v['ci90'][0]:.3f},{v['ci90'][1]:.3f}]{'=' if v['equivalent_within_5pct'] else '?'}" for k, v in h2[m]["tost_vs_Kneg"].items()))
print("per-step KW p (neg arms):", round(out["per_step_ns"]["kruskal_p_neg_arms"], 4))
print("speedup K-neg/K-tau:", out["speedup_Kneg_over_Ktau"])
