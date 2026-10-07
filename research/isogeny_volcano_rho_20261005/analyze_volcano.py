"""Pre-declared analysis (PROTOCOL.md) + per-curve trait table for the volcano study."""
import csv, glob, json, math
import numpy as np
from scipy import stats

L, N, Q = 230603167, 137439487532, 1 << 37
MOD = (1 << 37) | 0x207
LEVELS = ["crater", "floor73", "floor2663", "bottom"]
COND = {"crater": 1, "floor73": 73, "floor2663": 2663, "bottom": 194399}
H = {"crater": 1, "floor73": 74, "floor2663": 2664, "bottom": 197136}
ISO73 = {"crater": "74 down", "floor73": "1 up", "floor2663": "74 down", "bottom": "1 up"}
ISO2663 = {"crater": "2664 down", "floor73": "2664 down", "floor2663": "1 up", "bottom": "1 up"}
rng = np.random.default_rng(7)
B = 4000

def gmul(a, b):
    r = 0
    while b:
        if b & 1: r ^= a
        b >>= 1; a <<= 1
        if a >> 37: a ^= MOD
    return r
def gpow(a, e):
    r = 1
    while e:
        if e & 1: r = gmul(r, a)
        a = gmul(a, a); e >>= 1
    return r
def ghs_magic(b):
    rows, z = [], b
    for _ in range(37):
        v = (1 << 37) | z
        for r in rows: v = min(v, v ^ r)
        if v: rows.append(v)
        z = gmul(z, z)
    return len(rows)
def orbit(b):
    z, m = b, b
    for i in range(1, 38):
        z = gmul(z, z); m = min(m, z)
        if z == b: return i, m

curves = list(csv.DictReader(open("sample.csv")))
cyc = {r[0]: int(r[2]) for f in glob.glob("cyc_*.out") for r in (l[4:].strip().split(",") for l in open(f))}
lt = json.load(open("level_traits.json")); se = json.load(open("smooth_endos.json"))

def load(cid, m):
    ops, sec, ok = [], [], []
    for f in sorted(glob.glob(f"raw/c{cid}_m{m}_r*.csv")):
        for r in csv.DictReader(open(f)):
            ops.append(int(r["ops"])); sec.append(float(r["sec"])); ok.append(int(r["ok"]))
    return np.array(ops, float), np.array(sec), np.array(ok)

D = {(c["id"], 0): load(c["id"], 0) for c in curves}
D[("0", 1)] = load("0", 1)
ns = {}
for r in csv.DictReader(open("ns_per_step.csv")): ns.setdefault((r["id"], int(r["mode"])), []).append(float(r["ns"]))

def boot_ratio(x, y, level):
    bx = rng.choice(x, (B, len(x))).mean(1); by = rng.choice(y, (B, len(y))).mean(1); a = (1 - level) / 2
    return float(x.mean() / y.mean()), float(np.quantile(bx / by, a)), float(np.quantile(bx / by, 1 - a))
def holm(ps):
    o = np.argsort(ps); m = len(ps); adj = np.empty(m); run = 0
    for k, i in enumerate(o): run = max(run, min(1, (m - k) * ps[i])); adj[i] = run
    return adj

# ---- per-curve trait table
rows = []
for c in curves:
    b = int(c["b"]); lev = c["level"]; ops, sec, ok = D[(c["id"], 0)]
    osz, orep = orbit(b); m = ghs_magic(b)
    row = dict(id=int(c["id"]), level=lev, b=b, j=gpow(b, Q - 2), conductor=COND[lev], disc_End=-7 * COND[lev] ** 2,
               class_number_End=H[lev], n_points=N, group="cyclic Z/%d" % N, galois_orbit_size=osz, galois_orbit_min_b=orep,
               rational_73_isogenies=ISO73[lev], rational_2663_isogenies=ISO2663[lev],
               min_isogeny_degree_to_crater=COND[lev], cycle11_measured=cyc[c["id"]],
               min_k_with_tau_k_in_End=lt[lev]["min_k_tau_power_in_End"], min_nonscalar_endo_degree=lt[lev]["min_nonscalar_endo_degree"],
               smallest_orbit_smooth_endo=se[lev]["smallest_k"], best_modelled_endo_speedup=round(se[lev]["best_S"], 5),
               ghs_magic_m=m, ghs_genus_bound=f"2^{m - 1}", aut_group_order=2,
               rho_n=len(ops), rho_verified=int(ok.sum()), rho_mean_ops=round(ops.mean(), 1), rho_sd_ops=round(ops.std(ddof=1), 1),
               rho_mean_ms=round(sec.mean() * 1e3, 4), ns_per_step_median=round(float(np.median(ns[(c["id"], 0)])), 1))
    rows.append(row)
with open("curve_traits.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

# ---- statistics
out = {"class_invariants": dict(q="2^37", N=N, N_factored="2^2 * 149 * 230603167", ell=L, trace=-534059,
       conductor_Z_pi="73 * 2663", embedding_degree=3116259, twist_order="2 * 260999 * 263293", anomalous=False,
       total_curves=199875, curves_per_level=H)}
pooled = {lev: (np.concatenate([D[(c["id"], 0)][0] for c in curves if c["level"] == lev]),
                np.concatenate([D[(c["id"], 0)][1] for c in curves if c["level"] == lev])) for lev in LEVELS}
ktau_ops, ktau_sec, ktau_ok = D[("0", 1)]
out["validity"] = dict(all_verified=bool(all(D[k][2].all() for k in D)), total_solves=int(sum(len(D[k][0]) for k in D)))
# H1
h1 = {}
for mi, name, ref in ((0, "ops", ktau_ops), (1, "sec", ktau_sec)):
    ids = [c["id"] for c in curves]
    ps = np.array([stats.mannwhitneyu(D[(i, 0)][mi], ref, alternative="less").pvalue for i in ids])
    adj = holm(ps)
    ratios = {lev: boot_ratio(pooled[lev][mi], ref, .95) for lev in LEVELS}
    h1[name] = dict(min_holm_p=float(adj.min()), n_curves=len(ids), level_ratio_vs_crater_tau=ratios)
out["H1_any_curve_faster_than_crater_with_frobenius"] = h1
# H2
h2 = {}
for mi, name in ((0, "ops"), (1, "sec")):
    kw = stats.kruskal(*[pooled[lev][mi] for lev in LEVELS])
    cm = {lev: [D[(c["id"], 0)][mi].mean() for c in curves if c["level"] == lev] for lev in LEVELS if lev != "crater"}
    an = stats.f_oneway(*cm.values())
    tost = {}
    for lev in LEVELS[1:]:
        r, lo, hi = boot_ratio(pooled[lev][mi], pooled["crater"][mi], .90)
        tost[lev] = dict(ratio=r, ci90=[lo, hi], equivalent_within_3pct=bool(lo > .97 and hi < 1.03))
    h2[name] = dict(kruskal_p_4_levels=float(kw.pvalue), anova_curve_means_3_lower_levels_p=float(an.pvalue), tost_vs_crater_neg=tost,
                    level_means={lev: float(pooled[lev][mi].mean()) for lev in LEVELS})
out["H2_level_effect_negation_only"] = h2
# within-level heterogeneity
out["within_level_kruskal_p_ops"] = {lev: float(stats.kruskal(*[D[(c["id"], 0)][0] for c in curves if c["level"] == lev]).pvalue)
                                    for lev in LEVELS if lev != "crater"}
# per-step
step = {lev: np.array([v for c in curves if c["level"] == lev for v in ns[(c["id"], 0)]]) for lev in LEVELS}
st = {}
for lev in LEVELS:
    bm = np.median(rng.choice(step[lev], (B, len(step[lev]))), 1) / np.median(rng.choice(step["crater"], (B, len(step["crater"]))), 1)
    st[lev] = dict(median_ns=float(np.median(step[lev])), ratio=float(np.median(step[lev]) / np.median(step["crater"])),
                   ci90=[float(np.quantile(bm, .05)), float(np.quantile(bm, .95))])
out["per_step_ns"] = dict(kruskal_p=float(stats.kruskal(*step.values()).pvalue), levels=st,
                          crater_frobenius_median_ns=float(np.median(ns[("0", 1)])))
# trait association
cm_ops = [r["rho_mean_ops"] for r in rows if r["level"] != "crater"]
out["spearman_mean_ops_vs"] = {k: float(stats.spearmanr([r[k] for r in rows if r["level"] != "crater"], cm_ops).pvalue)
                              for k in ("conductor", "ghs_magic_m", "galois_orbit_size")
                              if len({r[k] for r in rows if r["level"] != "crater"}) > 1}
out["frobenius_speedup_on_crater"] = dict(ops=boot_ratio(pooled["crater"][0], ktau_ops, .95), sec=boot_ratio(pooled["crater"][1], ktau_sec, .95))
json.dump(out, open("results.json", "w"), indent=1, default=float)

print("validity:", out["validity"])
print(f"{'level':10} {'curves':>6} {'solves':>7} {'mean ops':>9} {'ms':>7} {'ns/step':>8}")
for lev in LEVELS:
    print(f"{lev:10} {sum(c['level'] == lev for c in curves):6d} {len(pooled[lev][0]):7d} {pooled[lev][0].mean():9.0f} {pooled[lev][1].mean() * 1e3:7.3f} {st[lev]['median_ns']:8.1f}")
print(f"{'crater+tau':10} {1:6d} {len(ktau_ops):7d} {ktau_ops.mean():9.0f} {ktau_sec.mean() * 1e3:7.3f} {out['per_step_ns']['crater_frobenius_median_ns']:8.1f}")
print("H1:", {k: (v["min_holm_p"], {l: round(x[1], 3) for l, x in v["level_ratio_vs_crater_tau"].items()}) for k, v in h1.items()})
for k, v in h2.items():
    print(f"H2 {k}: KW p={v['kruskal_p_4_levels']:.3f}, ANOVA(curve means) p={v['anova_curve_means_3_lower_levels_p']:.3f},",
          {l: (round(t['ratio'], 4), [round(x, 4) for x in t['ci90']], t['equivalent_within_3pct']) for l, t in v['tost_vs_crater_neg'].items()})
print("within-level KW p:", out["within_level_kruskal_p_ops"])
print("per-step:", {l: (round(v['ratio'], 4), [round(x, 4) for x in v['ci90']]) for l, v in st.items()}, "KW p", round(out["per_step_ns"]["kruskal_p"], 3))
print("spearman p:", out["spearman_mean_ops_vs"]); print("frobenius speedup:", out["frobenius_speedup_on_crater"])
