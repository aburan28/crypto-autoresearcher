"""EXP-PFDR-1b78f7 R15 analysis (and the R16 Stage R reading).

    python3 experiments/EXP-PFDR-1b78f7/analyze_census.py \
        --runs-dir experiments/EXP-PFDR-1b78f7/runs \
        --stage0 experiments/EXP-PFDR-7c8bf2/runs/RUN-PFDR-7c8bf2-stage0/fits.json \
        --out experiments/EXP-PFDR-1b78f7/runs/RUN-PFDR-1b78f7-analysis
    python3 experiments/EXP-PFDR-1b78f7/analyze_census.py --stage-r \
        --runs-dir experiments/EXP-PFDR-1b78f7/runs --out <stage-r run dir>

Implements the frozen `analysis` section A1-A9, the gates G1-G7, the positive
controls PC-1/PC-2 and the outcome table of
experiments/EXP-PFDR-1b78f7/specification.yaml.  Writes analysis.json,
kappa-cells.jsonl, fits.json and raw-result.json into --out.  Observations
only: the outcome ids are computed from the table; nothing is interpreted.

stats.bootstrap_slope / fit_exponent (unchanged) are loaded from their file by
importlib (no solver module is imported).
"""
from __future__ import annotations

import argparse
import gzip
import importlib.util
import json
import math
import os
import random
import statistics
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
P = "RUN-PFDR-1b78f7-"
CLASSES = ("TT", "TB", "SS")
STRUCT = ("subgroup", "small_x", "dickson")
RANDOMS = {"subgroup": ("random_sub_r0", "random_sub_r1", "random_sub_r2"),
           "small_x": ("random_sub_r0", "random_sub_r1", "random_sub_r2"),
           "dickson": ("random_dick_r0", "random_dick_r1", "random_dick_r2")}
RANDOM_ARMS = ("random_sub_r0", "random_sub_r1", "random_sub_r2",
               "random_dick_r0", "random_dick_r1", "random_dick_r2")
J0_RANDOMS = ("j0_random_r0", "j0_random_r1", "j0_random_r2")
RUNGS = (12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32)
REPS = 2000
ALPHA = 0.05
DISCLOSED_A8 = {"small_x": [1.00, 1.07, 1.01], "random": [0.71, 0.91, 0.98],
                "subgroup": [0.68, 0.97, 1.05]}


def load_stats():
    path = os.path.join(REPO, "src", "crypto_autoresearcher", "index_calculus", "stats.py")
    spec = importlib.util.spec_from_file_location("pfdr_census_stats", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


STATS = load_stats()


def rows_of(path: str) -> list[dict]:
    if not os.path.exists(path) and os.path.exists(path + ".gz"):
        path = path + ".gz"
    if not os.path.exists(path):
        return []
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt") as fh:
        return [json.loads(l) for l in fh if l.strip()]


def m_of(r):
    return int(r["method"][4:]) if str(r.get("method", "")).startswith("ic_m") else None


def phi_sf(z: float) -> float:
    return 0.5 * math.erfc(z / math.sqrt(2))


def poisson_cdf(n: int, mu: float) -> float:
    if n < 0:
        return 0.0
    if mu <= 0:
        return 1.0
    total, lm = 0.0, math.log(mu)
    for i in range(n + 1):
        total += math.exp(-mu + i * lm - math.lgamma(i + 1))
    return min(1.0, total)


def ks_pvalue(d: float, n: int) -> float:
    """Exact two-sided one-sample KS p-value (Marsaglia-Tsang-Wang 2003); large n: asymptotic."""
    if d <= 0:
        return 1.0
    if d >= 1:
        return 0.0
    if n > 400 or n * d > 60:  # Kolmogorov limit with Stephens' correction
        lam = (math.sqrt(n) + 0.12 + 0.11 / math.sqrt(n)) * d
        return max(0.0, min(1.0, 2 * sum((-1) ** (j - 1) * math.exp(-2 * j * j * lam * lam)
                                         for j in range(1, 101))))
    k = int(n * d) + 1
    m = 2 * k - 1
    h = k - n * d
    H = [[1.0 if i - j + 1 >= 0 else 0.0 for j in range(m)] for i in range(m)]
    for i in range(m):
        H[i][0] -= h ** (i + 1)
        H[m - 1][i] -= h ** (m - i)
    H[m - 1][0] += (2 * h - 1) ** m if 2 * h - 1 > 0 else 0.0
    for i in range(m):
        for j in range(m):
            if i - j + 1 > 0:
                for g in range(1, i - j + 2):
                    H[i][j] /= g

    def mm(A, B):
        return [[sum(A[i][t] * B[t][j] for t in range(m)) for j in range(m)] for i in range(m)]

    def mp(A, e):
        if e == 1:
            return [r[:] for r in A], 0
        V, eV = mp(A, e // 2)
        B = mm(V, V)
        eB = 2 * eV
        if e % 2:
            B = mm(A, B)
        if B[k - 1][k - 1] > 1e140:
            B = [[x * 1e-140 for x in r] for r in B]
            eB += 140
        return B, eB

    Q, eQ = mp(H, n)
    s = Q[k - 1][k - 1]
    for i in range(1, n + 1):
        s = s * i / n
        if s < 1e-140:
            s *= 1e140
            eQ -= 140
    return max(0.0, min(1.0, 1.0 - s * 10.0 ** eQ))


def ks_uniform(us):
    n = len(us)
    if not n:
        return {"n": 0, "D": None, "p": None, "reject_1pct": None}
    xs = sorted(us)
    D = max(max((i + 1) / n - x, x - i / n) for i, x in enumerate(xs))
    p = ks_pvalue(D, n)
    return {"n": n, "D": D, "p": p, "reject_1pct": p < 0.01}


def pct(vals, level=0.95):
    vals = sorted(vals)
    tail = (1 - level) / 2
    return vals[int(math.floor(tail * (len(vals) - 1)))], vals[int(math.ceil((1 - tail) * (len(vals) - 1)))]


# -- A1 kappa ------------------------------------------------------------------------------

def count(r: dict, cname: str, kind: str = "pairs_nonformal"):
    h = r["harvest"]
    if cname == "SS":
        a = h["SS"]["at_A_fix"]
        return a[kind]
    return h[cname]["at_stop"][kind]


def usable(r) -> bool:
    return r is not None and r.get("status") == "completed_valid" and r.get("harvest") is not None


def censored(r) -> bool:
    a = r["harvest"]["SS"].get("at_A_fix")
    return a is None or bool(a.get("censored"))


def kappa_stats(nA: list[float], nR: list[list[float]]):
    """nA[j], nR[j] = [three random counts] over the kept curves j."""
    C_A = sum(nA)
    C_R = sum(sum(v) for v in nR) / 3
    s2 = sum(statistics.variance(v) for v in nR) if nR else 0.0
    V = max(s2, C_R)
    SD = math.sqrt(V * 4 / 3)
    kappa = C_A / C_R if C_R > 0 else None
    z = (C_A - C_R) / SD if SD > 0 else None
    return {"C_A": C_A, "C_R": C_R, "sum_s2": s2, "V": V, "SD_null": SD, "kappa": kappa, "z": z,
            "resolved": C_R >= 10}


def band(st):
    if not st["resolved"] or st["z"] is None:
        return "unresolved"
    return "inside" if abs(st["z"]) <= 3 else ("above" if st["z"] > 3 else "below")


def build_index(rows):
    idx = {}
    for r in rows:
        if r.get("panel") in ("main", "j0") and r.get("arm"):
            idx[(r.get("panel"), m_of(r) or r.get("m"), r["bits"], r["curve"], r["arm"], r.get("mode"))] = r
    return idx


def kappa_cell(idx, m, bits, cname, A, curves, kind="pairs_nonformal", panel="main", rands=None):
    rands = rands or RANDOMS[A]
    kept, dropped = [], []
    for j in curves:
        rs = [idx.get((panel, m, bits, j, arm, "census")) for arm in (A,) + tuple(rands)]
        if all(usable(r) for r in rs) and not any(censored(r) for r in rs):
            kept.append((j, rs))
        else:
            why = []
            for arm, r in zip((A,) + tuple(rands), rs):
                if r is None:
                    why.append(f"{arm}:missing")
                elif not usable(r):
                    why.append(f"{arm}:{r.get('status')}")
                elif censored(r):
                    why.append(f"{arm}:censored_at_A_fix")
            dropped.append({"curve": j, "why": why})
    nA = [count(rs[0], cname, kind) for _, rs in kept]
    nR = [[count(r, cname, kind) for r in rs[1:]] for _, rs in kept]
    st = kappa_stats(nA, nR)
    x = statistics.mean(rs[0]["log2N"] for _, rs in kept) if kept else None
    return st | {"curves_kept": [j for j, _ in kept], "curves_dropped": dropped,
                 "counts_A": nA, "counts_R": nR, "mean_log2N": x, "band": band(st)}


def y_of(st):
    if st["C_R"] <= 0 or st["kappa"] is None:
        return None
    v = max(st["kappa"] - 1, st["SD_null"] / st["C_R"])
    return math.log2(v) if v > 0 else None


def ols(xs, ys):
    return STATS.ols_slope(xs, ys)


def slope_test(cells_by_rung: dict):
    """A2 for one (A, c, m): cells_by_rung[b] = kappa_cell dict (resolved rungs 20..32 only used)."""
    rungs = [b for b in sorted(cells_by_rung) if 20 <= b <= 32 and cells_by_rung[b]["resolved"]]
    out = {"rungs": rungs}
    if len(rungs) < 4:
        return out | {"status": "UNRESOLVED", "slope": None, "ci": None, "p_one_sided": 1.0}
    xs = [cells_by_rung[b]["mean_log2N"] for b in rungs]
    ys = [y_of(cells_by_rung[b]) for b in rungs]
    if any(y is None for y in ys):
        return out | {"status": "UNRESOLVED", "slope": None, "ci": None, "p_one_sided": 1.0,
                      "note": "undefined y at a resolved rung"}
    slope = ols(xs, ys)
    rng = random.Random(0)
    boots, dropped = [], 0
    for _ in range(REPS):
        bx, by = [], []
        bad = False
        for b in rungs:
            c = cells_by_rung[b]
            n = len(c["counts_A"])
            pick = [rng.randrange(n) for _ in range(n)]
            st = kappa_stats([c["counts_A"][i] for i in pick], [c["counts_R"][i] for i in pick])
            y = y_of(st)
            if y is None:
                bad = True
            bx.append(c["mean_log2N"])
            by.append(y)
        if bad:
            dropped += 1
            continue
        boots.append(ols(bx, by))
    lo, hi = pct(boots) if boots else (None, None)
    le0 = sum(1 for s in boots if s <= 0)
    p = (1 + le0 + dropped) / (REPS + 1)
    return out | {"status": "RESOLVED", "slope": slope, "ci": [lo, hi], "p_one_sided": p,
                  "bootstrap_dropped_replicates": dropped,
                  "ci_contains_minus_half": lo is not None and lo <= -0.5 <= hi,
                  "ci_contains_zero": lo is not None and lo <= 0 <= hi,
                  "ci_above_zero": lo is not None and lo > 0}


def holm(pvals: dict) -> dict:
    items = sorted(pvals.items(), key=lambda kv: kv[1])
    n = len(items)
    adj, run = {}, 0.0
    for i, (k, p) in enumerate(items):
        run = max(run, min(1.0, (n - i) * p))
        adj[k] = run
    return adj


# -- main ------------------------------------------------------------------------------------

def gates(runs_dir: str, panel_rows: list[dict]) -> dict:
    g = {}
    regs = {"G1": ["reg-off-sweep-20260924", "reg-off-sweep-mitm-20260926", "reg-off-sweep-arity-20260926",
                   "reg-off-sweep-minfill-20260926", "reg-off-sweep-arity-minfill-20260926",
                   "reg-off-sweep-arity67-20260928"],
            "G2": ["reg-census-sweep-minfill-20260926", "reg-census-sweep-arity-minfill-20260926"]}
    for gate, ids in regs.items():
        det = {}
        for rid in ids:
            p = os.path.join(runs_dir, P + rid, "regression-report.json")
            if os.path.exists(p):
                rep = json.load(open(p))
                det[rid] = {"pass": rep["pass"], "rows_compared": rep["rows_compared"],
                            "committed_rows": rep["committed_rows"], "mismatch_count": rep["mismatch_count"]}
            else:
                det[rid] = {"pass": False, "missing": True}
        g[gate] = {"pass": all(d["pass"] for d in det.values()), "runs": det}
    p = os.path.join(runs_dir, P + "tests", "raw-result.json")
    g["G3"] = {"pass": os.path.exists(p) and json.load(open(p)).get("G3_pass", False)}
    reg_census = []
    for rid in regs["G2"]:
        reg_census += rows_of(os.path.join(runs_dir, P + rid, "rows.jsonl"))
    harvest_rows = [r for r in panel_rows + reg_census if r.get("harvest")]
    solved = [r for r in panel_rows + reg_census if r.get("k_found") or r.get("method", "").startswith("ic_") and r.get("ok") and "k_found" not in r]
    g4_bad, g5_bad = [], []
    for r in harvest_rows:
        key = [r.get("bits"), r.get("curve"), r.get("method"), r.get("arm", r.get("fb")), r.get("mode")]
        for c in CLASSES:
            st = r["harvest"][c]["at_stop"]
            if st["cert_fail"] or st["cert_pass"] != st["rows_emitted"]:
                g4_bad.append(key + [c])
        if not r["harvest"]["ss_store"]["identity_ok"]:
            g5_bad.append(key)
    kbad = [[r.get("bits"), r.get("curve"), r.get("arm"), r.get("mode")] for r in panel_rows
            if r.get("k_found") and not r.get("k_verified")]
    invalid = [[r.get("bits"), r.get("curve"), r.get("arm"), r.get("mode"), r.get("status_reason")]
               for r in panel_rows if r.get("status") == "invalid"]
    g["G4"] = {"pass": not g4_bad and not kbad, "harvest_instances": len(harvest_rows),
               "cert_failures": g4_bad, "k_not_verified": kbad,
               "solved_instances_checked": len(solved)}
    g["G5"] = {"pass": not g5_bad, "harvest_instances": len(harvest_rows), "identity_failures": g5_bad}
    g6, g7 = defaultdict(lambda: [0, 0]), defaultdict(lambda: [0, 0])
    for r in panel_rows:
        for k, v in (r.get("checks") or {}).items():
            tgt = g6 if k.startswith("G6") else g7
            tgt[k][0 if v else 1] += 1
    g6_reason = [x for x in invalid if x[4] and "G6" in str(x[4])]
    g["G6"] = {"pass": all(v[1] == 0 for v in g6.values()) and bool(g6) and not g6_reason,
               "checks_pass_fail": {k: v for k, v in g6.items()},
               "invalid_instances_citing_G6": g6_reason}
    g["G7"] = {"pass": all(v[1] == 0 for v in g7.values()) and bool(g7),
               "checks_pass_fail": {k: v for k, v in g7.items()}}
    g["invalid_instances"] = invalid
    return g


def a3_rho(r, cname):
    h = r["harvest"]
    st = h[cname]["at_stop"]
    n = st["rows_emitted"]
    if n == 0:
        return None, n
    return st["informative_rank"] / min(n, h["U"]) if min(n, h["U"]) > 0 else None, n


def analyze(a) -> dict:
    rd = a.runs_dir
    main_rows = []
    for m in (3, 4, 5):
        main_rows += rows_of(os.path.join(rd, P + f"census-m{m}", "rows.jsonl"))
    j0_rows = rows_of(os.path.join(rd, P + "j0", "rows.jsonl"))
    rho_rows = rows_of(os.path.join(rd, P + "rho", "rows.jsonl"))
    stairs = []
    for name in ("census-m3", "census-m4", "census-m5", "j0"):
        stairs += rows_of(os.path.join(rd, P + name, "staircase.jsonl"))
    panel_rows = main_rows + j0_rows + rho_rows
    idx = build_index(main_rows + j0_rows)
    out: dict = {"inputs": {"main_rows": len(main_rows), "j0_rows": len(j0_rows),
                            "rho_rows": len(rho_rows), "staircase_records": len(stairs)}}
    # expected instance count (cells): 3040 main + 280 j0 solver instances, 110 + 35 rho
    out["instance_accounting"] = {
        "main_expected": 3040, "main_present": sum(1 for r in main_rows),
        "j0_solver_expected": 280, "j0_solver_present": sum(1 for r in j0_rows if r.get("arm")),
        "j0_rho_expected": 35, "j0_rho_present": sum(1 for r in j0_rows if r.get("method") == "rho"),
        "rho_expected": 110, "rho_present": len(rho_rows),
        "status_counts": dict(sorted(
            (f"{p}|{s}", sum(1 for r in rs if r.get("status") == s))
            for p, rs in (("main", main_rows), ("j0", j0_rows), ("rho", rho_rows))
            for s in {r.get("status") for r in rs}))}
    G = gates(rd, panel_rows)
    out["gates"] = G
    g_ok = (all(G[k]["pass"] for k in ("G1", "G2", "G3", "G4", "G5", "G6", "G7"))
            and not G["invalid_instances"])  # an invalid instance is a G4-G7 failure by construction

    # A1 + A2 ------------------------------------------------------------------------------
    curves = list(range(5))
    cells, cell_lines = {}, []
    for m in (3, 4, 5):
        for A in STRUCT:
            for cname in CLASSES:
                for b in RUNGS:
                    st = kappa_cell(idx, m, b, cname, A, curves)
                    raw = kappa_cell(idx, m, b, cname, A, curves, kind="pairs_raw")
                    cells[(A, cname, m, b)] = st
                    cell_lines.append({"arm": A, "class": cname, "m": m, "bits": b,
                                       **{k: st[k] for k in ("C_A", "C_R", "kappa", "z", "SD_null", "V",
                                                             "resolved", "band", "curves_kept",
                                                             "curves_dropped", "counts_A", "counts_R",
                                                             "mean_log2N")},
                                       "raw": {k: raw[k] for k in ("C_A", "C_R", "kappa", "z", "resolved")}})
    slopes, pvals = {}, {}
    for m in (3, 4, 5):
        for A in STRUCT:
            for cname in CLASSES:
                t = slope_test({b: cells[(A, cname, m, b)] for b in RUNGS})
                slopes[f"{A}|{cname}|{m}"] = t
                if cname in ("TT", "SS"):
                    pvals[f"{A}|{cname}|{m}"] = t["p_one_sided"]
    adj = holm(pvals)
    for k, v in adj.items():
        slopes[k]["holm_adjusted_p"] = v
    resolved_fam = [(k, v) for k, v in cells.items() if k[1] in ("TT", "SS") and v["resolved"] and v["z"] is not None]
    kk = len(resolved_fam)
    if kk:
        kmax, cmax = max(resolved_fam, key=lambda kv: abs(kv[1]["z"]))
        zo = abs(cmax["z"])
        tail = {"k": kk, "max_abs_z": zo, "cell": list(kmax),
                "p_max_of_k": 1 - (1 - 2 * phi_sf(zo)) ** kk}
    else:
        tail = {"k": 0}
    res_all = [(k, v) for k, v in cells.items() if v["resolved"] and v["kappa"] is not None]
    extremes = {}
    if res_all:
        for lab, fn in (("largest", max), ("smallest", min)):
            k_, v_ = fn(res_all, key=lambda kv: kv[1]["kappa"])
            extremes[lab] = {"cell": list(k_), "kappa": v_["kappa"], "z": v_["z"],
                             "counts_A": v_["counts_A"], "counts_R": v_["counts_R"]}
    out["A1_kappa"] = {"cells": len(cells), "resolved": sum(1 for v in cells.values() if v["resolved"]),
                       "bands": dict(sorted((b, sum(1 for v in cells.values() if v["band"] == b))
                                            for b in {v["band"] for v in cells.values()})),
                       "excursions_TT_SS": [{"cell": list(k), "z": v["z"], "kappa": v["kappa"]}
                                            for k, v in resolved_fam if abs(v["z"]) > 3],
                       "censoring_drop_rule": "applied per curve to all classes (a curve with any of A, R(A) censored at A_fix, failed or invalid is dropped for all four at that rung)",
                       "extremes": extremes}
    out["A2_slopes"] = {"tests": slopes, "family": sorted(pvals), "holm_alpha": ALPHA,
                        "tail_check_max_abs_z": tail}

    # A3 -------------------------------------------------------------------------------------
    rho_tab = defaultdict(list)
    per_m = defaultdict(list)
    h3_rank = defaultdict(lambda: [0, 0])
    for r in main_rows + j0_rows:
        if not usable(r) or r.get("mode") != "census":
            continue
        for cname in CLASSES:
            rho, n = a3_rho(r, cname)
            if rho is None or n < 10:
                continue
            rho_tab[(r["arm"], cname)].append(rho)
            per_m[(r["arm"], cname, m_of(r))].append(rho)
            st = r["harvest"][cname]["at_stop"]
            ok = st["informative_rank"] >= min(n, r["harvest"]["U"]) / 1.05
            h3_rank[(r["arm"], cname)][0 if ok else 1] += 1
    pred4 = {}
    xdef_random = STRUCT + RANDOM_ARMS
    pred4_met = True
    for (arm, cname), vals in sorted(rho_tab.items()):
        rec = {"qualifying": len(vals), "median": statistics.median(vals), "min": min(vals), "max": max(vals)}
        if arm in xdef_random:
            rec["evaluated"] = len(vals) >= 5
            if rec["evaluated"]:
                rec["meets_0_95"] = rec["median"] >= 0.95
                pred4_met &= rec["meets_0_95"]
        elif arm == "known_log":
            if cname in ("TT", "TB"):
                rec["all_le_0_05"] = all(v <= 0.05 for v in vals)
                pred4_met &= rec["all_le_0_05"]
            else:
                rec["note"] = "known_log SS reported, not evaluated"
        else:
            rec["note"] = "j0 panel arm, reported only"
        pred4[f"{arm}|{cname}"] = rec
    perm = defaultdict(lambda: [0, 0, 0])
    for s in stairs:
        if s.get("mode") != "census" or s.get("perm_saturation_indices") is None:
            continue
        if s["rows_emitted"] < 10 or s.get("saturation_index") is None:
            continue
        ps = [v for v in s["perm_saturation_indices"] if v is not None]
        stable = len(ps) == 5 and all(abs(v - s["saturation_index"]) < 0.02 for v in ps)
        perm[(s["arm"], s["class"])][0 if stable else 1] += 1
    out["A3_informative_rank"] = {
        "per_arm_class": pred4, "prediction_4_met": pred4_met,
        "per_arm_class_m": {f"{a}|{c}|{m}": {"n": len(v), "median": statistics.median(v)}
                            for (a, c, m), v in sorted(per_m.items(), key=str)},
        "H3_rank_ge_min_over_1_05": {f"{a}|{c}": {"ok": v[0], "not_ok": v[1]} for (a, c), v in sorted(h3_rank.items())},
        "H3_permutation_saturation_stable_lt_0_02": {f"{a}|{c}": {"stable": v[0], "unstable": v[1]}
                                                     for (a, c), v in sorted(perm.items())},
        "scope": "census-mode instances; qualifying n_c >= 10; prediction (4) evaluated per (arm, class) pooled over m and rungs on the main panel"}

    # A4 -------------------------------------------------------------------------------------
    groups = {"subgroup": ("subgroup",), "dickson": ("dickson",), "small_x": ("small_x",),
              "random_sub": ("random_sub_r0", "random_sub_r1", "random_sub_r2"),
              "random_dick": ("random_dick_r0", "random_dick_r1", "random_dick_r2")}
    pairs = defaultdict(list)
    for r in main_rows:
        if r.get("mode") != "census" or not usable(r) or not r.get("k_verified"):
            continue
        on = idx.get(("main", m_of(r), r["bits"], r["curve"], r["arm"], "on"))
        if not usable(on) or not on.get("k_verified"):
            continue
        for gname, arms in groups.items():
            if r["arm"] in arms:
                pairs[(m_of(r), gname)].append((r, on))
    a4 = {"ratio_medians": {}, "exponents": {}}
    met_1a, met_1b = True, True
    for m in (3, 4, 5):
        for gname in groups:
            ps = pairs[(m, gname)]
            for b in (24, 26, 28, 30, 32):
                sel = [c["s3_solves"] / o["s3_solves"] for c, o in ps if c["bits"] == b]
                if not sel:
                    continue
                med = statistics.median(sel)
                a4["ratio_medians"][f"{m}|{gname}|{b}"] = {"n": len(sel), "median": med}
                if m in (3, 5):
                    met_1a &= med >= 1.3
            sel = [(c, o) for c, o in ps if 12 <= c["bits"] <= 32]
            if not sel:
                continue
            fc = STATS.fit_exponent([c for c, _ in sel], "s3_solves", reps=REPS)
            fo = STATS.fit_exponent([o for _, o in sel], "s3_solves", reps=REPS)
            delta = fo["slope"] - fc["slope"] if fc["slope"] is not None and fo["slope"] is not None else None
            strata = defaultdict(list)
            for i, (c, _) in enumerate(sel):
                strata[c["bits"]].append(i)
            rng = random.Random(0)
            boots = []
            xs = [c["log2N"] for c, _ in sel]
            yc = [math.log2(c["s3_solves"]) for c, _ in sel]
            yo = [math.log2(o["s3_solves"]) for _, o in sel]
            for _ in range(REPS):
                ii = [rng.choice(mem) for mem in strata.values() for _ in mem]
                sc = ols([xs[i] for i in ii], [yc[i] for i in ii])
                so = ols([xs[i] for i in ii], [yo[i] for i in ii])
                if sc is not None and so is not None:
                    boots.append(so - sc)
            dci = list(pct(boots)) if boots else None
            rec = {"n_pairs": len(sel), "census": fc, "on": fo, "delta": delta, "delta_ci95_paired": dci,
                   "range_bits": [min(c["bits"] for c, _ in sel), max(c["bits"] for c, _ in sel)]}
            if m in (3, 5) and delta is not None:
                rec["abs_delta_le_0_03"] = abs(delta) <= 0.03
                met_1b &= rec["abs_delta_le_0_03"]
            a4["exponents"][f"{m}|{gname}"] = rec
    p2 = a4["exponents"].get("4|small_x", {}).get("on", {})
    a4["prediction_1a_met"] = met_1a
    a4["prediction_1b_met"] = met_1b
    a4["prediction_2"] = {"slope": p2.get("slope"), "ci95": [p2.get("lo"), p2.get("hi")],
                          "met": p2.get("slope") is not None and p2["slope"] <= 0.66,
                          "falsified": p2.get("lo") is not None and p2["lo"] > 0.66,
                          "range_bits": a4["exponents"].get("4|small_x", {}).get("range_bits")}
    out["A4_harvest_gain"] = a4

    # A5 -------------------------------------------------------------------------------------
    kl = [r for r in main_rows if r.get("arm") == "known_log" and r.get("mode") == "census" and usable(r)]
    num = den = 0.0
    units = 0
    for r in kl:
        rs = [idx.get(("main", 3, r["bits"], r["curve"], arm, "census")) for arm in RANDOMS["subgroup"]]
        if not all(usable(x) for x in rs):
            continue
        units += 1
        num += r["harvest"]["TT"]["at_stop"]["pairs_raw"]
        den += sum(x["harvest"]["TT"]["at_stop"]["pairs_raw"] for x in rs) / 3
    kl_rho = {c: [] for c in ("TT", "TB")}
    for r in kl:
        for c in ("TT", "TB"):
            rho, n = a3_rho(r, c)
            if rho is not None and n >= 10:
                kl_rho[c].append(rho)
    pc1_k = num / den if den > 0 else None
    pc1 = {"units": units, "raw_TT_known_log": num, "raw_TT_random_sub_mean": den, "raw_kappa_TT": pc1_k,
           "qualifying_rho": {c: len(v) for c, v in kl_rho.items()},
           "max_rho": {c: (max(v) if v else None) for c, v in kl_rho.items()},
           "pass": pc1_k is not None and pc1_k >= 5 and all(all(x <= 0.05 for x in v) for v in kl_rho.values())}
    jc = [r for r in j0_rows if r.get("arm") == "j0_coset" and r.get("mode") == "census" and usable(r)]
    nA, nR, rawA, rawR = [], [], 0.0, 0.0
    for r in jc:
        rs = [idx.get(("j0", 3, r["bits"], r["curve"], arm, "census")) for arm in J0_RANDOMS]
        if not all(usable(x) for x in rs):
            continue
        rawA += r["harvest"]["TB"]["at_stop"]["pairs_raw"]
        rawR += sum(x["harvest"]["TB"]["at_stop"]["pairs_raw"] for x in rs) / 3
        nA.append(r["harvest"]["TB"]["at_stop"]["pairs_nonformal"])
        nR.append([x["harvest"]["TB"]["at_stop"]["pairs_nonformal"] for x in rs])
    st = kappa_stats(nA, nR) if nA else None
    kb = rawA / rawR if rawR > 0 else None
    g6_ok = all(r["harvest"]["formal_basis_rank"] * 3 == 2 * r["fb_size"] for r in jc)
    pc2 = {"units": len(nA), "units_expected": 35, "raw_TB_coset": rawA, "raw_TB_random_mean": rawR,
           "kappa_TB_before": kb, "kappa_TB_before_note": ("None: mean raw TB pairs of the j0 random arms is 0"
                                                           if rawR == 0 else None),
           "nonformal": st, "formal_rank_2F_over_3_all": g6_ok,
           "pass": (kb is not None and kb >= 5) and st is not None and st["resolved"]
           and st["z"] is not None and abs(st["z"]) <= 3 and g6_ok}
    if rawR == 0 and rawA > 0:
        pc2["kappa_TB_before_note"] = ("random-arm raw TB mean is 0 while the coset arm has "
                                       f"{rawA:.0f} raw TB pairs; the ratio is undefined (infinite)")
    out["A5_positive_controls"] = {"PC-1": pc1, "PC-2": pc2}

    # A6 -------------------------------------------------------------------------------------
    a6 = {}
    for cname in CLASSES:
        for m in (3, 4, 5):
            us_all, us_hi = [], []
            per_rung = defaultdict(list)
            n_cens = 0
            for r in main_rows:
                if r.get("arm") not in RANDOM_ARMS or r.get("mode") != "census" or not usable(r):
                    continue
                if m_of(r) != m:
                    continue
                h = r["harvest"]
                if cname == "SS":
                    blk = h["SS"]["at_A_fix"]
                    n_cens += bool(blk["censored"])
                    n, mu = blk["pairs_nonformal"], blk["poisson_mean"]
                else:
                    n, mu = h[cname]["at_stop"]["pairs_nonformal"], h[cname]["at_stop"]["poisson_mean"]
                V = random.Random(f"pit-1b78f7|{r['bits']}|{r['curve']}|{m}|{r['arm']}|{cname}").random()
                F1, F0 = poisson_cdf(n, mu), poisson_cdf(n - 1, mu)
                u = F0 + V * (F1 - F0)
                us_all.append(u)
                if 20 <= r["bits"] <= 32:
                    us_hi.append(u)
                per_rung[r["bits"]].append((n, mu))
            tails = {}
            for b, lst in sorted(per_rung.items()):
                mx = max(n for n, _ in lst)
                prod = 1.0
                for _, mu in lst:
                    prod *= poisson_cdf(mx - 1, mu)
                pmax = 1 - prod
                tails[str(b)] = {"max_count": mx, "p_max_ge_observed": pmax, "flag_lt_0_001": pmax < 0.001}
            a6[f"{cname}|{m}"] = {"ks_12_32": ks_uniform(us_all), "ks_20_32": ks_uniform(us_hi),
                                  "ss_censored_instances_included": n_cens if cname == "SS" else None,
                                  "max_count_tail": tails}
    out["A6_poisson"] = a6

    # A7 -------------------------------------------------------------------------------------
    a7, below1, below09, excluded = [], [], [], 0
    for r in main_rows + j0_rows:
        if not usable(r) or not r.get("k_verified"):
            excluded += 1
            continue
        h = r["harvest"]
        rr = r["relations"]
        if r["mode"] == "on":
            rr += sum(h["on"]["rows_fed"].values())
        if rr <= 0:
            excluded += 1
            continue
        ratio = r["s3_solves"] / (0.5 * math.sqrt(rr * r["N"]))
        rec = {"panel": r["panel"], "bits": r["bits"], "curve": r["curve"], "m": m_of(r), "arm": r["arm"],
               "mode": r["mode"], "ratio": ratio, "r": rr}
        a7.append(rec)
        if ratio < 1.0:
            below1.append(rec)
        if ratio < 0.9:
            below09.append(rec)
    stage0 = json.load(open(a.stage0)) if a.stage0 and os.path.exists(a.stage0) else None
    out["A7_floor"] = {"instances": len(a7), "excluded_no_verified_k_or_r0": excluded,
                       "min": min(a7, key=lambda x: x["ratio"]) if a7 else None,
                       "below_1_0": below1, "below_0_9": below09,
                       "per_mode_m_median": {f"{mo}|{m}": statistics.median(x["ratio"] for x in a7 if x["mode"] == mo and x["m"] == m)
                                             for mo in ("census", "on") for m in (3, 4, 5)
                                             if any(x["mode"] == mo and x["m"] == m for x in a7)},
                       "stage0_min_ratio": stage0["min_ratio"] if stage0 else None,
                       "stage0_series_slopes_12_32": ({k: v["primary_12_32"] for k, v in stage0["series"].items()}
                                                      if stage0 else None)}
    tw_floor = bool(below09) or (stage0 is not None and stage0["min_ratio"] < 0.9)

    # A8 -------------------------------------------------------------------------------------
    reg = rows_of(os.path.join(rd, P + "reg-census-sweep-minfill-20260926", "rows.jsonl"))
    a8 = {}
    for fb in ("small_x", "random", "subgroup"):
        rec = {}
        for b in (20, 24, 28):
            vals = {r["curve"]: r["harvest"]["table"]["scratch_statistic"] for r in reg
                    if r.get("method") == "ic_m3" and r["fb"] == fb and r["bits"] == b and r.get("harvest")}
            rec[str(b)] = {"curves_0_3": statistics.mean(vals[c] for c in range(4)) if all(c in vals for c in range(4)) else None,
                           "curves_0_4": statistics.mean(vals[c] for c in range(5)) if all(c in vals for c in range(5)) else None}
        a8[fb] = {"measured": rec, "disclosed_20_24_28": DISCLOSED_A8[fb]}
    out["A8_scratch_replication"] = {"label": "replication of an unrecorded pre-protocol count",
                                     "per_base": a8,
                                     "note": "disclosed triples mapped to bases in the order the specification lists both; no decision uses A8"}

    # A9 -------------------------------------------------------------------------------------
    a9 = {"per_instance_max": {}, "per_run": {}}
    for r in main_rows + j0_rows:
        if not r.get("harvest"):
            continue
        h = r["harvest"]
        F, hh = r["fb_size"], r["table_arity"]
        code_bytes = 4 if 2 * (2 * F) ** hh < 1 << 32 else 8
        key = f"{r['panel']}|m{m_of(r)}|{r['mode']}"
        cur = a9["per_instance_max"].get(key, {"ss_store_peak_bytes": 0, "table_bytes_analytic": 0, "worker_maxrss_bytes": 0})
        cur["ss_store_peak_bytes"] = max(cur["ss_store_peak_bytes"], h["ss_store"]["peak_bytes"])
        cur["table_bytes_analytic"] = max(cur["table_bytes_analytic"], r["table_entries"] * (4 + code_bytes))
        cur["worker_maxrss_bytes"] = max(cur["worker_maxrss_bytes"], h["worker_maxrss_bytes"])
        a9["per_instance_max"][key] = cur
    for name in ("census-m3", "census-m4", "census-m5", "rho", "j0"):
        p = os.path.join(rd, P + name, "execution.json")
        if os.path.exists(p):
            ex = json.load(open(p))
            a9["per_run"][name] = {"peak_rss_bytes_max_descendant": ex["peak_rss_bytes_max_descendant"],
                                   "cpu_seconds": ex["cpu_seconds_descendants"], "wall_seconds": ex["wall_seconds"]}
    a9["modeled_before_execution"] = {"label": "MODELED (specification A9), not measured",
                                      "text": "SS store at m = 4, 32 bits about 3.4e7 encodings, 0.5-1.6 GB with merge temporaries"}
    a9["units"] = "ss_store peak_bytes analytic = entries x 12 bytes (x uint32 + packed descriptor uint64); table bytes analytic = entries x (4 + 4 or 8); worker_maxrss is the worker process high-water mark (cumulative over the instances that worker ran)"
    out["A9_memory"] = a9

    # rho panel summary ----------------------------------------------------------------------
    rho_ok = [r for r in rho_rows if r.get("ok")]
    out["rho_panel"] = {"instances": len(rho_rows), "ok": len(rho_ok),
                        "walk_exponent": STATS.fit_exponent(rho_ok, "walk_ops", reps=REPS),
                        "median_walk_per_rung": {str(b): statistics.median(r["walk_ops"] for r in rho_ok if r["bits"] == b)
                                                 for b in sorted({r["bits"] for r in rho_ok})}}

    # outcomes ---------------------------------------------------------------------------------
    pc_ok = pc1["pass"] and pc2["pass"]
    alive = []
    for m in (3, 4, 5):
        for A in STRUCT:
            for cname in ("TT", "SS"):
                c30, c32 = cells[(A, cname, m, 30)], cells[(A, cname, m, 32)]
                t = slopes[f"{A}|{cname}|{m}"]
                rho_rec = pred4.get(f"{A}|{cname}", {})
                cond = (c30["resolved"] and c32["resolved"] and (c30["z"] or 0) > 3 and (c32["z"] or 0) > 3
                        and t.get("ci_above_zero") and t.get("holm_adjusted_p", 1) < ALPHA
                        and rho_rec.get("median", 0) >= 0.95)
                if cond:
                    alive.append([A, cname, m])
    exc = out["A1_kappa"]["excursions_TT_SS"]
    if not g_ok:
        structural = "O-INVALID"
    elif not pc_ok:
        structural = "O-NO-DYNAMIC-RANGE"
    elif alive:
        structural = "O-ALIVE"
    elif exc:
        structural = "O-EXCURSION"
    else:
        structural = "O-NULL"
    outcome_ids = [structural] + (["O-GENERIC"] if g_ok else [])
    out["outcomes"] = {
        "outcome_ids": outcome_ids, "structural": structural,
        "alive_cells": alive, "excursion_cells": exc,
        "gates_G1_G7_pass": g_ok, "PC-1_pass": pc1["pass"], "PC-2_pass": pc2["pass"],
        "O-GENERIC": ({"prediction_1a_met": met_1a, "prediction_1b_met": met_1b,
                       "prediction_2": a4["prediction_2"],
                       "HEUR-4765e4-H1_rejections_1pct": sorted(k for k, v in a6.items()
                                                               if v["ks_12_32"]["reject_1pct"] or v["ks_20_32"]["reject_1pct"]),
                       "HEUR-4765e4-H3": "see A3_informative_rank H3 blocks"} if g_ok else None),
        "tripwires": {"TW-FLOOR_fired": tw_floor, "TW-ALIVE_fired": structural == "O-ALIVE",
                      "note": "tripwire flags are reported as fired or not, nothing more"},
        "precedence": "O-INVALID (any G1-G7 fails) > O-NO-DYNAMIC-RANGE (PC fails; gate_rule) > O-ALIVE > O-EXCURSION > O-NULL; O-GENERIC whenever G1-G7 pass"}
    return out, cell_lines, slopes


def stage_r(a) -> dict:
    rows = rows_of(os.path.join(a.out, "rows.jsonl"))
    idx = build_index(rows)
    prior = json.load(open(os.path.join(a.runs_dir, P + "analysis", "analysis.json")))
    res = []
    for e in prior["A1_kappa"]["excursions_TT_SS"]:
        A, cname, m, b = e["cell"]
        st = kappa_cell(idx, m, b, cname, A, list(range(5, 10)))
        rep = st["resolved"] and st["z"] is not None and abs(st["z"]) > 3 and (st["z"] > 0) == (e["z"] > 0)
        res.append({"cell": e["cell"], "original_z": e["z"], "stage_r": {k: st[k] for k in (
            "C_A", "C_R", "kappa", "z", "resolved", "band", "curves_kept", "curves_dropped", "counts_A", "counts_R")},
            "replicated_anomaly": rep})
    return {"stage_r_cells": res, "replicated": [r["cell"] for r in res if r["replicated_anomaly"]],
            "reading": ("REPLICATED ANOMALY present" if any(r["replicated_anomaly"] for r in res)
                        else "no excursion replicated")}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs-dir", required=True)
    ap.add_argument("--stage0", default=None)
    ap.add_argument("--out", required=True)
    ap.add_argument("--stage-r", action="store_true")
    a = ap.parse_args(argv)
    os.makedirs(a.out, exist_ok=True)
    if a.stage_r:
        res = stage_r(a)
        with open(os.path.join(a.out, "analysis.json"), "w") as fh:
            json.dump(res, fh, indent=2, sort_keys=True)
        print(json.dumps({"replicated": res["replicated"], "reading": res["reading"]}, indent=2))
        return 0
    out, cell_lines, slopes = analyze(a)
    with open(os.path.join(a.out, "analysis.json"), "w") as fh:
        json.dump(out, fh, indent=2, sort_keys=True, default=str)
    with open(os.path.join(a.out, "kappa-cells.jsonl"), "w") as fh:
        for line in cell_lines:
            fh.write(json.dumps(line, sort_keys=True) + "\n")
    with open(os.path.join(a.out, "fits.json"), "w") as fh:
        json.dump({"A2_slopes": slopes, "A4_exponents": out["A4_harvest_gain"]["exponents"],
                   "rho_walk_exponent": out["rho_panel"]["walk_exponent"]}, fh, indent=2, sort_keys=True)
    raw = {"outcomes": out["outcomes"], "gates": out["gates"],
           "positive_controls": out["A5_positive_controls"],
           "instance_accounting": out["instance_accounting"],
           "metrics_file": "analysis.json (A1-A9 in full)",
           "certificate": {"kind": "none", "note": "analysis of certified runs; no new solve or relation"}}
    with open(os.path.join(a.out, "raw-result.json"), "w") as fh:
        json.dump(raw, fh, indent=2, sort_keys=True, default=str)
    print(json.dumps(out["outcomes"], indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
