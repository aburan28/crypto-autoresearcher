"""R0 (fit/label/band regeneration from raw) and R1 (pseudo-replication recomputation).

Red Team TASK-20260904-3a2ff5.  Reads runs/*/raw-result.json only.
"""
import json, math, os, collections
try:
    from scipy import stats
    HAVE_SCIPY = True
except Exception:
    HAVE_SCIPY = False
import sympy

ROOT = "/home/user/crypto-autoresearcher"
RUNS = os.path.join(ROOT, "experiments/EXP-PFDR-cbdefb/runs")
OUT = os.path.join(ROOT, "coordination/reviews/pfdr-battery-20260904/reviews/TASK-20260904-3a2ff5")
LADDER = [(s, p) for s in (1,2,3,4,5) for p in (4099,16411,65537)]

def tquantile(df, q=0.975):
    # exact-ish t quantile via sympy's inverse of the CDF is slow; use mpmath
    from mpmath import mp, findroot, betainc, mpf
    mp.dps = 30
    import mpmath
    f = lambda t: mpmath.mpf(0.5)*(1+mpmath.sign(t)*(1-mpmath.betainc(mpf(df)/2, mpf(0.5),
            0, mpf(df)/(df+t*t), regularized=True))) - q
    return float(findroot(f, 2.0))

def load(s, p):
    with open(os.path.join(RUNS, f"RUN-PFDR-cbdefb-m2-s{s}-p{p}", "raw-result.json")) as fh:
        return json.load(fh)

def apply_count1(sysrec):
    falls = [h["D"] for h in sysrec.get("history", [])
             if h.get("fall") and h.get("iteration_count") != 1]
    return (falls[0] if falls else None, falls[-1] if falls else None)

def ols(xs, ys):
    n = len(xs)
    mx, my = sum(xs)/n, sum(ys)/n
    sxx = sum((x-mx)**2 for x in xs)
    sxy = sum((x-mx)*(y-my) for x, y in zip(xs, ys))
    b = sxy/sxx
    a = my - b*mx
    resid = [y-(a+b*x) for x, y in zip(xs, ys)]
    ssr = sum(r*r for r in resid)
    df = n-2
    s2 = ssr/df if df > 0 else 0.0
    se = math.sqrt(s2/sxx) if df > 0 else 0.0
    t = tquantile(df) if df > 0 else float("nan")
    return {"n": n, "slope": b, "intercept": a, "resid_var": s2, "se": se,
            "df": df, "t975": t, "ci95": [b-t*se, b+t*se], "sxx": sxx, "ssr": ssr}

def rule(ci):
    lo, hi = ci
    contains = lambda v: lo <= v <= hi
    return {"contains_1": contains(1.0), "excludes_0.5": not contains(0.5),
            "contains_0": contains(0.0), "excludes_0.25": not contains(0.25),
            "excludes_0": not contains(0.0)}

def label(ci, flat_run, top_unc):
    r = rule(ci)
    if r["contains_1"] and r["excludes_0.5"]:
        return "I", r
    if r["contains_0"] and r["excludes_0.25"] and flat_run >= 4 and top_unc:
        return "III", r
    return "unresolved", r

def main():
    per_draw = []       # (s, p, d_ff, d_lf, censored)
    for s, p in LADDER:
        raw = load(s, p)
        for d in raw["raw"]["draws"]:
            r = d["semaev"]
            if r.get("degenerate"):
                continue
            dff, dlf = apply_count1(r)
            per_draw.append((s, p, dff, dlf, bool(r.get("right_censored"))))
    res = {"n_semaev_draws_total": len(per_draw)}

    # ---- (a) per-draw primary fit s = 2..5, uncensored, fall observed
    prim = [(s, dlf) for (s, p, dff, dlf, c) in per_draw if 2 <= s <= 5 and not c and dlf is not None]
    fa = ols([x for x, _ in prim], [y for _, y in prim])
    res["A_per_draw_n480"] = fa
    # ---- (b) per (s,p) cell means
    cells = collections.defaultdict(list)
    for (s, p, dff, dlf, c) in per_draw:
        if 2 <= s <= 5 and not c and dlf is not None:
            cells[(s, p)].append(dlf)
    cx = sorted(cells)
    fb = ols([s for (s, p) in cx], [sum(cells[(s, p)])/len(cells[(s, p)]) for (s, p) in cx])
    res["B_cell_means_n12"] = fb
    res["B_within_cell_variance"] = {f"{s},{p}": (max(v)-min(v)) for (s, p), v in sorted(cells.items())}
    # ---- (c) per-s means, 4 points
    smeans = collections.defaultdict(list)
    for (s, p), v in cells.items():
        smeans[s].extend(v)
    sx = sorted(smeans)
    fc = ols(sx, [sum(smeans[s])/len(smeans[s]) for s in sx])
    res["C_per_s_n4"] = fc
    # ---- (d) per-draw, but with distinct generator systems only (x_R dedup within a cell)
    #      the number of DISTINCT (curve, x_R) systems per cell, computed from raw parameters
    distinct = {}
    for s, p in LADDER:
        raw = load(s, p)
        seen = set()
        for d in raw["raw"]["draws"]:
            seen.add((d["curve"]["a"], d["curve"]["b"], d["target"]["x_R"]))
        distinct[f"{s},{p}"] = len(seen)
    res["distinct_systems_per_cell"] = distinct
    # fit on one draw per distinct system
    ded = []
    for s, p in LADDER:
        if not (2 <= s <= 5):
            continue
        raw = load(s, p)
        seen = {}
        for d in raw["raw"]["draws"]:
            key = (d["curve"]["a"], d["curve"]["b"], d["target"]["x_R"])
            r = d["semaev"]
            if r.get("degenerate") or r.get("right_censored"):
                continue
            _, dlf = apply_count1(r)
            if dlf is None:
                continue
            seen.setdefault(key, dlf)
        for k, v in seen.items():
            ded.append((s, v))
    fd = ols([x for x, _ in ded], [y for _, y in ded])
    res["D_distinct_systems"] = fd
    res["D_n_distinct_total"] = len(ded)

    # ---- labels under each unit
    flat_run = 2   # longest run of consecutive fully-uncensored cells with one common d_lf, s=2..5
    for key, f in (("A_per_draw_n480", fa), ("B_cell_means_n12", fb), ("C_per_s_n4", fc), ("D_distinct_systems", fd)):
        lab, r = label(f["ci95"], flat_run, True)
        res[key]["rule"] = r
        res[key]["d_lf_label"] = lab
        res[key]["heur002_falsifier_fires"] = r["excludes_0"] and True

    # ---- how the interval depends on the replication count k (per s-level)
    ys = [5, 5, 6, 6]; xs = [2, 3, 4, 5]
    sweep = []
    for k in (1, 2, 3, 4, 5, 10, 20, 40, 120, 480, 4800):
        X = [x for x in xs for _ in range(k)]
        Y = [y for y in ys for _ in range(k)]
        f = ols(X, Y)
        rr = rule(f["ci95"])
        sweep.append({"k_per_s": k, "n": len(X), "ci95": f["ci95"],
                      "excludes_0.5": rr["excludes_0.5"], "excludes_0": rr["excludes_0"],
                      "excludes_0.25": rr["excludes_0.25"], "contains_1": rr["contains_1"]})
    res["replication_sweep"] = sweep

    # ---- what the OLS slope of the DERIVED law 4 + floor(s/2) is on windows [2, S]
    win = []
    for S in range(5, 41):
        X = list(range(2, S+1)); Y = [4 + x//2 for x in X]
        f = ols(X, Y)
        win.append({"window": [2, S], "ols_slope": round(f["slope"], 6)})
    res["window_sweep_of_the_derived_step_law"] = win
    res["asymptotic_slope_of_4_plus_floor_s_over_2"] = 0.5

    with open(os.path.join(OUT, "r0r1_fits.json"), "w") as fh:
        json.dump(res, fh, indent=1, default=str)
    for k in ("A_per_draw_n480", "B_cell_means_n12", "C_per_s_n4", "D_distinct_systems"):
        f = res[k]
        print(f"{k:24s} n={f['n']:5d} slope={f['slope']:.4f} ci95=[{f['ci95'][0]:.4f},{f['ci95'][1]:.4f}] "
              f"residvar={f['resid_var']:.4f} label={f['d_lf_label']} fires={f['heur002_falsifier_fires']}")
    print("distinct systems per cell:", distinct)
    print("window sweep [2,S] slope:", [(w['window'][1], w['ols_slope']) for w in win[:8]], "...", win[-1])
    for r in sweep: print(r)

if __name__ == "__main__":
    main()
