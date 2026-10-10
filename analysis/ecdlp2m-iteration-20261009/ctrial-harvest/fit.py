#!/usr/bin/env python3
"""Deterministic fit of log2 c_trial(m, n, l) from ctrial.csv; extrapolation to ECC2K-130.

Pure standard library (no numpy/scipy on this host).  Re-running produces
byte-identical fit_results.json / fit_tables.md given the same ctrial.csv.

    python3 fit.py            # reads ./ctrial.csv and ./ctrial_targets.csv

Conventions
  * y = log2(per-attempt cost).  Wall seconds for time fits; conflicts; field ops.
  * OLS of y on x (x = l, or n).  Two CIs are reported:
      - bootstrap 95% percentile CI.  Where per-target values exist the bootstrap
        resamples targets within each cell (cell median recomputed), otherwise it
        resamples cells (pairs bootstrap; degenerate resamples with one distinct x
        are redrawn).  B = 4000, seed 20261009.
      - analytic 95% prediction-of-the-mean CI from the t distribution (df = k-2),
        which is the only honest interval when there are 3-4 cells.
    The verdict uses the UNION (widest) of the two intervals.
  * Censored cells (median censored) are excluded from fits and listed; never imputed.
  * Conversion wall-seconds -> rho steps:  log2(steps) = log2(wall_s) - log2(t_rho).
      t_rho (primary)      = 1/(22.45e6/4) s  (ECC2K-130 Core 2 Quad, 530 cycles/iter/core; KR-RHO-18cc42)
      t_rho (IC-generous)  = 4.10e-5 s        (Sage/Python rho step, EXP-ICI-001 RUN-d, macOS arm64)
    Field ops -> rho steps: one rho step ~ 2^3.32 = 10 counted field ops (stated assumption).
"""
import csv, json, math, os, random, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = 20261009
B = 4000
N_TARGET = 131
L_CEIL = {3: 44, 4: 33, 5: 27, 6: 22}            # ceil(131/m)
L_BUDGET = {3: 29, 4: 29, 5: 28, 6: 24}          # LA-capped l of the budget table (EXP-ICPERF-783e9e budget_table, n=131)
BUDGETS = {  # log2 rho steps per attempt
    "plain product law (KN-FIND-aa2efc / H-CERTBIN-6e6287)": {3: -15.55, 4: 11.01, 5: 32.6, 6: 37.0},
    "single/double LP rebalanced j=2 (H-BINSTD-555991)": {3: 8.71, 4: 22.34},
    "2LP N^(2(m-1)/m^2) analogue (UNVERIFIED closure audit)": {3: 2.6, 4: 11.7},
}
LOG2_T_RHO = {"primary": math.log2(4 / 22.45e6), "ic_generous": math.log2(4.10e-5)}
LOG2_FIELDOPS_PER_RHO = math.log2(10.0)
# Solver-independent floor: descended-ANF monomial count at the budget's l (EXP-ICPERF-783e9e, n=131)
ANF_FLOOR_LOG2_MONOMIALS = {3: 29.02, 4: 52.78, 5: 79.71, 6: 103.13}
LOG2_BITOPS_PER_RHO = 77.0 - 60.9               # KR-RHO-18cc42: ~2^77 bit ops for ~2^60.9 iterations


def load():
    rows = list(csv.DictReader(open(os.path.join(HERE, "ctrial.csv"))))
    tg = {}
    for r in csv.DictReader(open(os.path.join(HERE, "ctrial_targets.csv"))):
        tg.setdefault(r["row_id"], []).append((float(r["value_s"]), int(r["censored"])))
    return rows, tg


def fnum(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def ols(xs, ys):
    k = len(xs)
    mx, my = sum(xs) / k, sum(ys) / k
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx == 0:
        return None
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    a = my - b * mx
    res = [y - (a + b * x) for x, y in zip(xs, ys)]
    s2 = sum(e * e for e in res) / (k - 2) if k > 2 else float("nan")
    return a, b, s2, sxx, mx


T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262,
        10: 2.228, 12: 2.179, 14: 2.145, 16: 2.120, 20: 2.086, 30: 2.042}


def tcrit(df):
    if df <= 0:
        return float("inf")
    keys = sorted(T975)
    for kk in keys:
        if df <= kk:
            return T975[kk]
    return 1.96


def pct(v, p):
    v = sorted(v)
    k = (len(v) - 1) * p
    f, c = math.floor(k), math.ceil(k)
    return v[f] if f == c else v[f] + (v[c] - v[f]) * (k - f)


def fit_family(name, cells, xkey, x_eval, metric="wall", per_target=None):
    """cells: list of dicts with x (l or n), y (log2 value), and optional 'row_id' for per-target bootstrap."""
    xs = [c[xkey] for c in cells]
    ys = [c["y"] for c in cells]
    res = {"family": name, "x": xkey, "metric": metric, "k_cells": len(cells),
           "x_values": xs, "y_values": [round(y, 3) for y in ys]}
    if len(cells) < 3 or len(set(xs)) < 2:
        res["status"] = "insufficient (<3 cells or <2 distinct x): no slope reported"
        return res
    a, b, s2, sxx, mx = ols(xs, ys)
    res.update(status="fitted", slope=round(b, 4), intercept=round(a, 3),
               resid_sd=round(math.sqrt(s2), 3) if s2 == s2 else None)
    rng = random.Random(SEED + sum(ord(ch) for ch in name))
    boots_b, boots_pred = [], {xe: [] for xe in x_eval}
    use_targets = per_target is not None and all(c.get("row_id") in per_target for c in cells)
    tries = 0
    while len(boots_b) < B and tries < 20 * B:
        tries += 1
        if use_targets:
            bx, by = [], []
            for c in cells:
                vals = [v for v, cen in per_target[c["row_id"]]]
                samp = [vals[rng.randrange(len(vals))] for _ in vals]
                bx.append(c[xkey]); by.append(math.log2(statistics.median(samp)))
        else:
            idx = [rng.randrange(len(cells)) for _ in cells]
            bx = [xs[i] for i in idx]; by = [ys[i] for i in idx]
            if len(set(bx)) < 2:
                continue
        o = ols(bx, by)
        if o is None:
            continue
        boots_b.append(o[1])
        for xe in x_eval:
            boots_pred[xe].append(o[0] + o[1] * xe)
    res["bootstrap"] = {"B": len(boots_b), "mode": "targets-within-cells" if use_targets else "cells (pairs)",
                        "slope_ci95": [round(pct(boots_b, 0.025), 4), round(pct(boots_b, 0.975), 4)]}
    df = len(cells) - 2
    se_b = math.sqrt(s2 / sxx) if s2 == s2 else float("nan")
    tc = tcrit(df)
    res["analytic"] = {"df": df, "slope_ci95": [round(b - tc * se_b, 4), round(b + tc * se_b, 4)]}
    preds = {}
    for xe in x_eval:
        yhat = a + b * xe
        se_m = math.sqrt(s2 * (1.0 / len(cells) + (xe - mx) ** 2 / sxx)) if s2 == s2 else float("nan")
        bl, bh = pct(boots_pred[xe], 0.025), pct(boots_pred[xe], 0.975)
        al, ah = yhat - tc * se_m, yhat + tc * se_m
        preds[str(xe)] = {"y_hat": round(yhat, 2), "boot_ci95": [round(bl, 2), round(bh, 2)],
                          "analytic_ci95": [round(al, 2), round(ah, 2)],
                          "union_ci95": [round(min(bl, al), 2), round(max(bh, ah), 2)],
                          "extrapolation_distance": round(xe - max(xs), 1)}
    res["predictions"] = preds
    return res



def mols(X, y):
    """OLS with intercept for multiple regressors; returns coef list [a, b1, b2, ...] and sigma^2, (X'X)^-1."""
    k = len(y); p = len(X[0]) + 1
    A = [[1.0] + list(r) for r in X]
    XtX = [[sum(A[i][r] * A[i][c] for i in range(k)) for c in range(p)] for r in range(p)]
    Xty = [sum(A[i][r] * y[i] for i in range(k)) for r in range(p)]
    # invert XtX by Gauss-Jordan
    M = [row[:] + [1.0 if i == j else 0.0 for j in range(p)] for i, row in enumerate(XtX)]
    for c in range(p):
        piv = max(range(c, p), key=lambda r: abs(M[r][c]))
        if abs(M[piv][c]) < 1e-12:
            return None
        M[c], M[piv] = M[piv], M[c]
        pv = M[c][c]
        M[c] = [v / pv for v in M[c]]
        for r in range(p):
            if r != c:
                f = M[r][c]
                M[r] = [a - f * b for a, b in zip(M[r], M[c])]
    inv = [row[p:] for row in M]
    coef = [sum(inv[r][c] * Xty[c] for c in range(p)) for r in range(p)]
    res = [y[i] - sum(coef[j] * A[i][j] for j in range(p)) for i in range(k)]
    s2 = sum(e * e for e in res) / (k - p) if k > p else float("nan")
    return coef, s2, inv


def fit_two_factor(name, cells, evals, m, unit="s"):
    """log2 y = a + b*l + c*log2(n); pairs bootstrap over cells + analytic t interval."""
    X = [(c["l"], math.log2(c["n"])) for c in cells]; y = [c["y"] for c in cells]
    o = mols(X, y)
    res = {"family": name, "x": "l + log2(n)", "metric": "wall" if unit == "s" else unit, "unit": unit, "m": m,
           "k_cells": len(cells), "rows": [c["row_id"] for c in cells]}
    if o is None or len(cells) < 5:
        res["status"] = "insufficient"; return res
    coef, s2, inv = o
    res.update(status="fitted", slope=round(coef[1], 4), slope_log2n=round(coef[2], 4), intercept=round(coef[0], 3),
               resid_sd=round(math.sqrt(s2), 3))
    rng = random.Random(SEED + 7)
    bb, bp = [], {str(e): [] for e in evals}
    while len(bb) < B:
        idx = [rng.randrange(len(cells)) for _ in cells]
        oo = mols([X[i] for i in idx], [y[i] for i in idx])
        if oo is None:
            continue
        bb.append(oo[0][1])
        for e in evals:
            bp[str(e)].append(oo[0][0] + oo[0][1] * e[0] + oo[0][2] * math.log2(e[1]))
    df = len(cells) - 3; tc = tcrit(df)
    se_b = math.sqrt(s2 * inv[1][1])
    res["bootstrap"] = {"B": B, "mode": "cells (pairs)", "slope_ci95": [round(pct(bb, 0.025), 4), round(pct(bb, 0.975), 4)]}
    res["analytic"] = {"df": df, "slope_ci95": [round(coef[1] - tc * se_b, 4), round(coef[1] + tc * se_b, 4)]}
    preds = {}
    for e in evals:
        v = [1.0, e[0], math.log2(e[1])]
        yhat = sum(cc * vv for cc, vv in zip(coef, v))
        se_m = math.sqrt(s2 * sum(v[i] * inv[i][j] * v[j] for i in range(3) for j in range(3)))
        bl, bh = pct(bp[str(e)], 0.025), pct(bp[str(e)], 0.975)
        preds[str(e[0])] = {"y_hat": round(yhat, 2), "boot_ci95": [round(bl, 2), round(bh, 2)],
                            "analytic_ci95": [round(yhat - tc * se_m, 2), round(yhat + tc * se_m, 2)],
                            "union_ci95": [round(min(bl, yhat - tc * se_m), 2), round(max(bh, yhat + tc * se_m), 2)],
                            "extrapolation_distance": round(e[0] - max(c["l"] for c in cells), 1),
                            "n_eval": e[1]}
    res["predictions"] = preds
    return res


def select(rows, **cond):
    out = []
    for r in rows:
        ok = True
        for k, v in cond.items():
            if callable(v):
                if not v(r.get(k, "")):
                    ok = False; break
            elif r.get(k, "") != v:
                ok = False; break
        if ok:
            out.append(r)
    return out


def cells_from(rows, xkey, metric="wall"):
    cells, excluded = [], []
    for r in rows:
        if r["censored"] == "yes" or r["outcome"] == "censored":
            excluded.append(r["row_id"]); continue
        v = fnum(r["wall_s"]) if metric == "wall" else fnum(r["conflicts"]) if metric == "conflicts" else fnum(r["field_ops"])
        if v is None or v <= 0:
            excluded.append(r["row_id"]); continue
        cells.append({"l": int(r["l"]), "n": int(r["n"]), "y": math.log2(v), "row_id": r["row_id"]})
    return cells, excluded


def verdict(lo, hi, budget):
    if hi < budget:
        return "INSIDE"
    if lo > budget:
        return "OUTSIDE"
    return "INDETERMINATE"


def main():
    rows, tg = load()
    fit = [r for r in rows if r["include_in_fit"] == "yes"]
    R = {"constants": {"n": N_TARGET, "l_ceil": L_CEIL, "l_budget": L_BUDGET, "budgets_log2_rho_steps": BUDGETS,
                       "log2_t_rho_s": {k: round(v, 3) for k, v in LOG2_T_RHO.items()},
                       "log2_fieldops_per_rho_step": round(LOG2_FIELDOPS_PER_RHO, 2),
                       "anf_floor_log2_monomials_at_l_budget": ANF_FLOOR_LOG2_MONOMIALS,
                       "log2_bitops_per_rho_step": LOG2_BITOPS_PER_RHO,
                       "seed": SEED, "bootstrap_B": B},
         "fits": [], "law_checks": {}, "extrapolations": [], "excluded_censored": {}}

    def run(name, rs, xkey, m, metric="wall", unit="s", targets=False, note=""):
        cells, exc = cells_from(rs, xkey, metric)
        if xkey == "l":
            xe = sorted(set([L_CEIL[m], L_BUDGET[m]]))
        else:
            xe = [N_TARGET]
        f = fit_family(name, cells, xkey, xe, metric, tg if targets else None)
        f["m"] = m; f["unit"] = unit; f["note"] = note
        f["rows"] = [c["row_id"] for c in cells]
        R["fits"].append(f)
        if exc:
            R["excluded_censored"][name] = exc
        return f

    lit = lambda **kw: select(fit, tier="literature_transcribed", **kw)
    # ---------------- m = 3 -----------------
    for oc in ("UNSAT", "SAT"):
        run(f"m3 WDSat complete+symbreak (Trimoska T3) {oc} wall~l", lit(solver="WDSat", outcome=oc,
            solver_config="complete: Prop.1 order + m! symmetry breaking"), "l", 3,
            note="18 cells l=6..11, n=17..89, 100-run means, Xeon E5-2640")
        run(f"m3 WDSat complete+symbreak (Trimoska T3) {oc} conflicts~l", lit(solver="WDSat", outcome=oc,
            solver_config="complete: Prop.1 order + m! symmetry breaking"), "l", 3, metric="conflicts", unit="conflicts")
        run(f"m3 WDSat complete+symbreak (Trimoska T3) {oc} wall~n", lit(solver="WDSat", outcome=oc,
            solver_config="complete: Prop.1 order + m! symmetry breaking"), "n", 3,
            note="n-only regression conflates l and n (l was varied independently of n in T3)")
        run(f"m3 WDSat Prop.1 no-symbreak (Trimoska T2) {oc} wall~l", lit(solver="WDSat", outcome=oc,
            solver_config="CNF-XOR + Prop.1 order (no symmetry breaking)"), "l", 3)
        run(f"m3 CryptoMiniSat+Prop.1 (Trimoska T2) {oc} wall~l", lit(solver="CryptoMiniSat", outcome=oc,
            solver_config="CNF-XOR + Prop.1 order"), "l", 3)
        run(f"m3 MiniSat CNF (Trimoska T2) {oc} wall~l", lit(solver="MiniSat", outcome=oc), "l", 3)
        run(f"m3 Magma F4 (Trimoska T2) {oc} wall~l", lit(solver="Magma F4 (grevlex)", outcome=oc), "l", 3,
            note="l=8 rows hit the 200 GB memory wall (censored, excluded)")
        inrepo = lambda solver, cfg: select(fit, tier="in_repo_run", solver=solver, solver_config=cfg, outcome=oc,
                                            run_id="RUN-ICPERF-305ca3")
        run(f"m3 in-repo WDSat symmetry (66fd51) {oc} wall~l", inrepo("wdsat", "symmetry"), "l", 3, targets=True,
            note="3 cells, only l in {5,6}")
        run(f"m3 in-repo WDSat symmetry (66fd51) {oc} wall~n", inrepo("wdsat", "symmetry"), "n", 3, targets=True)
        run(f"m3 in-repo WDSat default (66fd51) {oc} wall~l", inrepo("wdsat", "default"), "l", 3, targets=True)
        run(f"m3 in-repo CMS cnf_xor (66fd51) {oc} wall~l", inrepo("cryptominisat5", "cnf_xor"), "l", 3, targets=True)
        run(f"m3 in-repo CaDiCaL pure_cnf (66fd51) {oc} wall~l", inrepo("cadical", "pure_cnf"), "l", 3, targets=True)
    cb = select(fit, run_id="RUN-EXP-ICI-001-a")
    run("m3 crossbred chained-S3 (ICI-001) planted, full-enum cost wall~n", cb, "n", 3, targets=True,
        note="k=ceil(n/3); per-target cost = 2^k_fix * per-guess GB seconds (prices UNSAT too)")
    run("m3 crossbred chained-S3 (ICI-001) planted, full-enum cost wall~l", cb, "l", 3, targets=True)
    ms = select(fit, solver="msolve F4", m="3", tier="in_repo_run")
    run("m3 msolve F4 chained-S3 (SEMBIN b6eb9f/9bb990) all outcomes wall~l", ms, "l", 3,
        note="n in {17,19}; SAT and UNSAT pooled (too few cells to split)")
    run("m3 PolyBoRi (783e9e) SAT wall~l", select(fit, run_id="RUN-ICPERF-2f36fd", m="3", outcome="SAT"), "l", 3)
    ext = select(fit, tier="external_sha256_bound")
    run("m3 n=131 Riemann-Roch oracle field ops~l (solver_13)", select(ext, solver="Riemann-Roch quadratic-image oracle"),
        "l", 3, metric="field_ops", unit="field ops", note="n = 131 exactly; d = 4..8")
    run("m3 n=131 pair enumeration field ops~l (solver_13)", select(ext, solver="pair enumeration (null object)"),
        "l", 3, metric="field_ops", unit="field ops", note="n = 131 exactly; d = 4..8; = C(|F|,2) by construction")
    # ---------------- m = 4 -----------------
    mitm = select(fit, run_id="RUN-EXP-ICI-001-c")
    run("m4 MITM t=4 chained-S3 (ICI-001) wall~l", mitm, "l", 4, targets=True,
        note="combinatorial full enumeration, work = 2^(2l+1) exactly; n=28 cell censored (excluded)")
    run("m4 MITM t=4 chained-S3 (ICI-001) wall~n", mitm, "n", 4, targets=True)
    run("m4 Groebner (PolyBoRi/msolve, all engines) wall~l", select(fit, m="4", tier=lambda t: t.startswith("in_repo"),
        solver=lambda s: s != "MITM list-matching (combinatorial)"), "l", 4,
        note="heterogeneous engines/hosts; expected insufficient")
    for mm in (5, 6):
        run(f"m{mm} any solver wall~l", select(fit, m=str(mm)), "l", mm, note="expected insufficient")

    # ---------------- law checks: UNSAT conflicts vs exhaustive 2^(m l)/m! ----------------
    lc = []
    for r in rows:
        if r["m"] != "3" or r["outcome"] != "UNSAT" or not fnum(r["conflicts"]):
            continue
        if r["run_id"] not in ("", "RUN-ICPERF-305ca3"):
            continue
        cfg, sol = r["solver_config"], r["solver"]
        symbreak = (sol == "wdsat" and cfg == "symmetry") or (sol == "WDSat" and cfg.startswith("complete"))
        nosym = (sol == "wdsat" and cfg in ("default", "core_order")) or \
                (sol == "WDSat" and cfg == "CNF-XOR + Prop.1 order (no symmetry breaking)")
        if not (symbreak or nosym):
            continue
        l = int(r["l"])
        denom = 2 ** (3 * l) / (6 if symbreak else 1)
        lc.append({"row": r["row_id"], "src": r["tier"] + ":" + sol + ":" + cfg[:24], "n": int(r["n"]), "l": l,
                   "conflicts": fnum(r["conflicts"]),
                   ("ratio_to_2^(3l)/3!" if symbreak else "ratio_to_2^(3l)"): round(fnum(r["conflicts"]) / denom, 4)})
    R["law_checks"]["unsat_conflicts_vs_exhaustive"] = lc
    # per-conflict time (T3 UNSAT): fit log2(s/conflict) vs l
    pc = []
    for r in lit(solver="WDSat", outcome="UNSAT", solver_config="complete: Prop.1 order + m! symmetry breaking"):
        pc.append({"l": int(r["l"]), "n": int(r["n"]), "y": math.log2(fnum(r["wall_s"]) / fnum(r["conflicts"])), "row_id": r["row_id"]})
    f = fit_family("m3 WDSat T3 UNSAT seconds-per-conflict ~l", pc, "l", [L_BUDGET[3], L_CEIL[3]])
    f["m"] = 3; f["unit"] = "s/conflict"; R["fits"].append(f)
    f = fit_family("m3 WDSat T3 UNSAT seconds-per-conflict ~n", pc, "n", [N_TARGET])
    f["m"] = 3; f["unit"] = "s/conflict"; R["fits"].append(f)
    for oc in ("UNSAT", "SAT"):
        for tag, cfg in (("T3 complete+symbreak", "complete: Prop.1 order + m! symmetry breaking"),
                         ("T2 Prop.1 no-symbreak", "CNF-XOR + Prop.1 order (no symmetry breaking)")):
            cs, exc = cells_from(lit(solver="WDSat", outcome=oc, solver_config=cfg), "l")
            f = fit_two_factor(f"m3 WDSat {tag} {oc} wall ~ l + log2(n) [PRIMARY m=3 model]", cs,
                               [(L_BUDGET[3], N_TARGET), (L_CEIL[3], N_TARGET)], 3)
            f["note"] = "two-factor model; conflicts depend on l only, per-conflict time grows with instance size"
            R["fits"].append(f)

    # ---------------- extrapolations to n = 131 vs budgets ----------------
    for f in R["fits"]:
        if f.get("status") != "fitted":
            continue
        if f["x"] == "n" and "ICI-001" not in f["family"]:
            f["extrapolation_note"] = "not extrapolated: l was not tied to n in this design"
            continue
        if f["x"] == "l" and "crossbred" in f["family"]:
            f["extrapolation_note"] = "not extrapolated: crossbred cost depends on n (nb = 3k + n) and n was tied to l; use the n-fit"
            continue
        distinct = len(set(f.get("x_values", []))) if f["x"] in ("l", "n") else len(set(f["rows"]))
        if f["x"] in ("l", "n") and distinct < 3:
            f["extrapolation_note"] = "descriptive only: fewer than 3 distinct x values, CI not credible"
            f["used_for_verdict"] = False
        else:
            f["used_for_verdict"] = True
        for xe, p in f["predictions"].items():
            m = f["m"]
            if f["unit"] == "s":
                conv = {k: [p["union_ci95"][0] - v, p["y_hat"] - v, p["union_ci95"][1] - v] for k, v in LOG2_T_RHO.items()}
            elif f["unit"] == "field ops":
                conv = {"fieldops/10": [p["union_ci95"][0] - LOG2_FIELDOPS_PER_RHO, p["y_hat"] - LOG2_FIELDOPS_PER_RHO,
                                        p["union_ci95"][1] - LOG2_FIELDOPS_PER_RHO]}
            else:
                conv = {}
            if not conv:
                continue
            l_at = int(float(xe)) if f["x"].startswith("l") else (math.ceil(N_TARGET / m))
            for ck, (lo, mid, hi) in conv.items():
                for bname, bl in BUDGETS.items():
                    if m not in bl:
                        continue
                    R["extrapolations"].append({
                        "fit": f["family"], "m": m, "x": f["x"], "x_eval": xe, "l_at": l_at,
                        "l_role": ("ceil(131/m)" if l_at == L_CEIL[m] else "budget l" if l_at == L_BUDGET[m] else "other"),
                        "conversion": ck, "log2_ctrial_rho": round(mid, 1), "ci95": [round(lo, 1), round(hi, 1)],
                        "budget": bname, "budget_log2": bl[m], "margin_bits": round(lo - bl[m], 1),
                        "verdict": verdict(lo, hi, bl[m]) if f["used_for_verdict"] else "(descriptive) " + verdict(lo, hi, bl[m]),
                        "extrapolation_distance": p["extrapolation_distance"]})
    # solver-independent ANF floor
    fl = []
    for m, mon in ANF_FLOOR_LOG2_MONOMIALS.items():
        for bname, bl in BUDGETS.items():
            if m not in bl:
                continue
            fl.append({"m": m, "l": L_BUDGET[m], "log2_monomials": mon,
                       "floor_rho_if_1_monomial_eq_1_rho_step": mon,
                       "floor_rho_if_1_monomial_eq_1_bit_op": round(mon - LOG2_BITOPS_PER_RHO, 1),
                       "budget": bname, "budget_log2": bl[m],
                       "verdict_generous_unit": verdict(mon - LOG2_BITOPS_PER_RHO, mon - LOG2_BITOPS_PER_RHO, bl[m])})
    R["anf_floor"] = fl
    # ---------------- derived quantities ----------------
    D = {}
    byid = {r["row_id"]: r for r in rows}
    # host calibration: in-repo WDSat symmetry vs Trimoska T3 at the shared cells
    hc = []
    for n in ("17", "19"):
        a = [r for r in rows if r["run_id"] in ("RUN-ICPERF-305ca3", "RUN-ICPERF-4ec9b9") and r["solver"] == "wdsat"
             and r["solver_config"] == "symmetry" and r["n"] == n and r["outcome"] == "UNSAT"]
        b = [r for r in rows if r["tier"] == "literature_transcribed" and r["solver"] == "WDSat" and
             r["solver_config"].startswith("complete") and r["n"] == n and r["l"] == "6" and r["outcome"] == "UNSAT"]
        for x in a:
            hc.append({"n": int(n), "l": 6, "in_repo_run": x["run_id"], "in_repo_wall": fnum(x["wall_s"]),
                       "lit_wall": fnum(b[0]["wall_s"]), "wall_ratio_inrepo_over_lit": round(fnum(x["wall_s"]) / fnum(b[0]["wall_s"]), 3),
                       "in_repo_conflicts": fnum(x["conflicts"]), "lit_conflicts": fnum(b[0]["conflicts"]),
                       "conflict_ratio": round(fnum(x["conflicts"]) / fnum(b[0]["conflicts"]), 4)})
    D["host_calibration_wdsat_symmetry_unsat"] = hc
    # budgets expressed as seconds per attempt
    D["budget_seconds_per_attempt"] = {bn: {m: {"primary_s": round(2 ** (b + LOG2_T_RHO["primary"]), 7),
                                                 "ic_generous_s": round(2 ** (b + LOG2_T_RHO["ic_generous"]), 5)}
                                            for m, b in bl.items()} for bn, bl in BUDGETS.items()}
    # required per-l growth (bits per unit l) from a measured anchor to the budget's l
    anchors = []
    def anc(m, desc, rid):
        r = byid[rid]
        anchors.append((m, desc, rid, int(r["l"]), int(r["n"]), fnum(r["wall_s"])))
    t3 = [r for r in rows if r["tier"] == "literature_transcribed" and r["solver"] == "WDSat" and r["solver_config"].startswith("complete")
          and r["outcome"] == "UNSAT" and r["l"] == "11" and r["n"] == "89"]
    anc(3, "WDSat T3 UNSAT l=11 n=89 (largest measured m=3 cell)", t3[0]["row_id"])
    p4 = [r for r in rows if r["run_id"] == "RUN-ICPERF-2f36fd" and r["m"] == "4" and r["outcome"] == "UNSAT"]
    anc(4, "PolyBoRi m=4 n=12 l=3 UNSAT (only completed m=4 UNSAT cell)", p4[0]["row_id"])
    mi = [r for r in rows if r["run_id"] == "RUN-EXP-ICI-001-c" and r["l"] == "6"]
    anc(4, "MITM t=4 n=24 l=6 (largest uncensored m=4 cell)", mi[0]["row_id"])
    m6 = sorted([r for r in rows if r["m"] == "6" and r["outcome"] == "UNSAT" and fnum(r["wall_s"])], key=lambda r: -int(r["n_obs"] or 0))
    if m6:
        anc(6, "msolve chained S3 m=6 n=12 k=2 UNSAT (only m=6 cell; degenerate ml=n)", m6[0]["row_id"])
    ra = []
    for (m, desc, rid, l0, n0, w0) in anchors:
        for bn, bl in BUDGETS.items():
            if m not in bl:
                continue
            need = bl[m] + LOG2_T_RHO["primary"]           # log2 seconds allowed per attempt
            alpha = (need - math.log2(w0)) / (L_BUDGET[m] - l0)
            ra.append({"m": m, "anchor": desc, "anchor_row": rid, "anchor_l": l0, "anchor_log2_s": round(math.log2(w0), 2),
                       "budget": bn, "allowed_log2_s_at_l_budget": round(need, 2), "l_budget": L_BUDGET[m],
                       "required_bits_per_l": round(alpha, 3),
                       "exhaustive_law_bits_per_l": m})
    D["required_growth_per_l"] = ra
    # direct n = 131 lower bounds from the external panel (censored SAT encodings)
    ext = [r for r in rows if r["tier"] == "external_sha256_bound" and r["run_id"] == "solver_10"]
    lb = []
    for r in ext:
        if r["censored"] == "yes" and "SAT" in r["solver"] or (r["censored"] == "yes" and "chained" in r["solver"]):
            lb.append({"row": r["row_id"], "solver": r["solver"], "l": int(r["l"]), "stratum": r["label"],
                       "per_attempt_ge_s": fnum(r["censor_bound_s"]),
                       "log2_rho_ge_primary": round(math.log2(fnum(r["censor_bound_s"])) - LOG2_T_RHO["primary"], 1)})
    D["n131_direct_censored_lower_bounds"] = lb
    # exhaustive-law projection (MODEL, not a fit): UNSAT conflicts = 2^(m l)/m!
    D["exhaustive_law_projection_conflicts_log2"] = {m: {"l_budget": L_BUDGET[m],
        "log2_conflicts": round(m * L_BUDGET[m] - math.log2(math.factorial(m)), 1)} for m in (3, 4, 5, 6)}
    R["derived"] = D
    with open(os.path.join(HERE, "fit_results.json"), "w") as fo:
        json.dump(R, fo, indent=1, sort_keys=True)
    write_tables(R, rows)


def ascii_plot(points, width=60, height=18, xlab="l", ylab="log2 s"):
    xs = [p[0] for p in points]; ys = [p[1] for p in points]
    x0, x1 = min(xs), max(xs); y0, y1 = min(ys), max(ys)
    grid = [[" "] * (width + 1) for _ in range(height + 1)]
    for x, y, ch in points:
        cx = int(round((x - x0) / (x1 - x0 or 1) * width))
        cy = height - int(round((y - y0) / (y1 - y0 or 1) * height))
        grid[cy][cx] = ch if grid[cy][cx] in (" ", ch) else "*"
    out = []
    for i, row in enumerate(grid):
        yv = y1 - (y1 - y0) * i / height
        out.append("%7.1f |" % yv + "".join(row))
    out.append(" " * 8 + "+" + "-" * (width + 1))
    out.append(" " * 8 + "%-10s%s%10s" % (x0, xlab.center(width - 19), x1))
    return "\n".join(out)


def write_tables(R, rows):
    L = []
    L.append("## Fits (log2 per-attempt cost vs x)\n")
    L.append("| family | m | x | cells | slope | boot 95% | analytic 95% | resid sd | status |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for f in R["fits"]:
        if f.get("status") == "fitted":
            L.append(f"| {f['family']} | {f['m']} | {f['x']} | {f['k_cells']} | {f['slope']} | "
                     f"{f['bootstrap']['slope_ci95']} | {f['analytic']['slope_ci95']} | {f['resid_sd']} | fitted |")
        else:
            L.append(f"| {f['family']} | {f['m']} | {f['x']} | {f['k_cells']} | - | - | - | - | {f['status']} |")
    L.append("\n## Extrapolations to n = 131 (log2 rho steps per attempt; union 95% CI)\n")
    L.append("| fit | m | at l | conv | log2 c_trial | CI95 | budget line | budget | margin (CI lo - budget) | verdict |")
    L.append("|---|---|---|---|---|---|---|---|---|---|")
    for e in R["extrapolations"]:
        L.append(f"| {e['fit']} | {e['m']} | {e['l_at']} ({e['l_role']}) | {e['conversion']} | {e['log2_ctrial_rho']} | "
                 f"{e['ci95']} | {e['budget'].split(' (')[0]} | {e['budget_log2']} | {e['margin_bits']} | {e['verdict']} |")
    L.append("\n## Solver-independent floor: descended-ANF size at the budget's l (EXP-ICPERF-783e9e)\n")
    L.append("| m | l | log2 monomials | floor (1 monomial = 1 bit op) in log2 rho steps | budget | verdict |")
    L.append("|---|---|---|---|---|---|")
    for x in R["anf_floor"]:
        L.append(f"| {x['m']} | {x['l']} | {x['log2_monomials']} | {x['floor_rho_if_1_monomial_eq_1_bit_op']} | "
                 f"{x['budget'].split(' (')[0]} {x['budget_log2']} | {x['verdict_generous_unit']} |")
    L.append("\n## UNSAT conflicts vs the exhaustive law (m = 3)\n")
    L.append("| row | source | n | l | conflicts | ratio |")
    L.append("|---|---|---|---|---|---|")
    for x in R["law_checks"]["unsat_conflicts_vs_exhaustive"]:
        k = [kk for kk in x if kk.startswith("ratio")][0]
        L.append(f"| {x['row']} | {x['src']} | {x['n']} | {x['l']} | {int(x['conflicts'])} | {k} = {x[k]} |")
    # ASCII plot: m=3 UNSAT log2 wall vs l, WDSat T3 (W), in-repo symmetry (w), Magma (G), CMS (C), crossbred (X)
    pts = []
    for r in rows:
        if r["m"] != "3" or r["outcome"] not in ("UNSAT", "SAT") or not fnum(r["wall_s"]) or r["censored"] == "yes":
            continue
        ch = None
        if r["tier"] == "literature_transcribed" and r["solver"] == "WDSat" and r["solver_config"].startswith("complete"):
            ch = "W" if r["outcome"] == "UNSAT" else "w"
        elif r["tier"] == "literature_transcribed" and r["solver"].startswith("Magma"):
            ch = "G" if r["outcome"] == "UNSAT" else "g"
        elif r["run_id"] == "RUN-ICPERF-305ca3" and r["solver"] == "wdsat" and r["solver_config"] == "symmetry":
            ch = "S" if r["outcome"] == "UNSAT" else "s"
        elif r["run_id"] == "RUN-EXP-ICI-001-a":
            ch = "X"
        elif r["solver"] == "msolve F4" and r["tier"] == "in_repo_run":
            ch = "M"
        if ch:
            pts.append((int(r["l"]), math.log2(fnum(r["wall_s"])), ch))
    L.append("\n## ASCII plot: m = 3, log2(wall s) per attempt vs l\n")
    L.append("W/w = Trimoska WDSat+symbreak UNSAT/SAT (Xeon); S/s = in-repo WDSat symmetry UNSAT/SAT; "
             "G/g = Magma F4 UNSAT/SAT; X = crossbred (planted, full-enum cost); M = msolve chained S3; * = overlap\n")
    L.append("```\n" + ascii_plot(pts) + "\n```")
    open(os.path.join(HERE, "fit_tables.md"), "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
