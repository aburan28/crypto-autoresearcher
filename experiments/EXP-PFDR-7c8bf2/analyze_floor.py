"""EXP-PFDR-7c8bf2 Stage 0: the generic collision floor re-read on committed rows.

    python3 experiments/EXP-PFDR-7c8bf2/analyze_floor.py \
        --results-dir src/crypto_autoresearcher/index_calculus/results \
        --out experiments/EXP-PFDR-7c8bf2/runs/RUN-PFDR-7c8bf2-stage0

Implements procedure P0-P7 of experiments/EXP-PFDR-7c8bf2/specification.yaml
exactly once.  ZERO solver runs: no module of the index_calculus package is
imported.  stats.bootstrap_slope (unchanged) is loaded straight from its file
with importlib, which does not execute the package __init__ (that __init__
imports the solver); raw-result.json records the loaded-module check.

Outputs in --out: floor-rows.jsonl.gz (gzip, mtime 0 == gzip -n), fits.json,
raw-result.json.  Observations only; the outcome id is computed from the
spec's analysis_outcomes table and nothing else.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import importlib.util
import io
import json
import math
import os
import random
import statistics
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
ARCHIVE_COMMIT = "c06f1ad8cb0fcd7bbd2ffb2afcd7a4cc8e22bf86"  # design-packet archive (TASK-20260929-58a054)

FILES = [
    ("sweep-minfill-20260926.jsonl.gz", "primary"),
    ("sweep-arity-minfill-20260926.jsonl.gz", "primary"),
    ("sweep-arity67-20260928.jsonl.gz", "primary"),
    ("sweep-mitm-20260926.jsonl.gz", "twin"),
    ("sweep-arity-20260926.jsonl.gz", "twin"),
]
TWINS = [("sweep-mitm-20260926.jsonl.gz", "sweep-minfill-20260926.jsonl.gz"),
         ("sweep-arity-20260926.jsonl.gz", "sweep-arity-minfill-20260926.jsonl.gz")]
TWIN_FIELDS = ["p", "a", "b", "N", "fb_size", "s3_solves", "table_s3_solves", "table_entries",
               "relations", "attempts", "rank", "target_ops"]
# P3 primary series: name -> (file, m, fb)
SERIES = {
    "S3-smallx-filtered": ("sweep-minfill-20260926.jsonl.gz", 3, "small_x"),
    "S3-random-filtered": ("sweep-minfill-20260926.jsonl.gz", 3, "random"),
    "S3-subgroup-filtered": ("sweep-minfill-20260926.jsonl.gz", 3, "subgroup"),
    "S3-smallx-unfiltered": ("sweep-arity-minfill-20260926.jsonl.gz", 3, "small_x"),
    "S4-smallx": ("sweep-arity-minfill-20260926.jsonl.gz", 4, "small_x"),
    "S5-smallx": ("sweep-arity-minfill-20260926.jsonl.gz", 5, "small_x"),
    "S6-smallx": ("sweep-arity67-20260928.jsonl.gz", 6, "small_x"),
    "S7-smallx": ("sweep-arity67-20260928.jsonl.gz", 7, "small_x"),
}
# Frozen prediction windows (preregistered_prediction; OUT-CONSISTENT)
WINDOWS = {3: (-0.03, 0.03), 5: (-0.03, 0.03), 7: (-0.03, 0.03),
           4: (0.095, 0.155), 6: (0.053, 0.113)}
REPS, SEED = 2000, 0


def load_stats():
    path = os.path.join(REPO, "src", "crypto_autoresearcher", "index_calculus", "stats.py")
    spec = importlib.util.spec_from_file_location("pfdr_stage0_stats", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod, path


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def m_of(row) -> int:
    return int(row["method"][len("ic_m"):])


def key_of(row):
    return (row["bits"], row["curve"], row["method"], row["fb"], row.get("engine", "enumerate"))


# -- statistics helpers (no scipy on the host) ------------------------------------------

def poisson_cdf(n: int, mu: float) -> float:
    if n < 0:
        return 0.0
    if mu <= 0:
        return 1.0
    total, logmu = 0.0, math.log(mu)
    for i in range(n + 1):
        total += math.exp(-mu + i * logmu - math.lgamma(i + 1))
    return min(1.0, total)


def ks_pvalue(d: float, n: int) -> float:
    """Exact two-sided one-sample KS p-value P(D_n >= d) (Marsaglia-Tsang-Wang 2003)."""
    if d <= 0:
        return 1.0
    if d >= 1:
        return 0.0
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

    def matmul(A, B):
        return [[sum(A[i][t] * B[t][j] for t in range(m)) for j in range(m)] for i in range(m)]

    def mpow(A, e):
        if e == 1:
            return [row[:] for row in A], 0
        V, eV = mpow(A, e // 2)
        B = matmul(V, V)
        eB = 2 * eV
        if e % 2:
            B = matmul(A, B)
        if B[k - 1][k - 1] > 1e140:
            B = [[x * 1e-140 for x in row] for row in B]
            eB += 140
        return B, eB

    Q, eQ = mpow(H, n)
    s = Q[k - 1][k - 1]
    for i in range(1, n + 1):
        s = s * i / n
        if s < 1e-140:
            s *= 1e140
            eQ -= 140
    cdf = s * 10.0 ** eQ
    return max(0.0, min(1.0, 1.0 - cdf))


def ks_uniform(us: list[float]) -> dict:
    n = len(us)
    if n == 0:
        return {"n": 0, "D": None, "p": None, "reject_1pct": None}
    xs = sorted(us)
    D = max(max((i + 1) / n - x, x - i / n) for i, x in enumerate(xs))
    p = ks_pvalue(D, n)
    return {"n": n, "D": D, "p": p, "reject_1pct": p < 0.01}


def percentile_interval(vals: list[float], level: float = 0.95):
    vals = sorted(vals)
    tail = (1 - level) / 2
    return (vals[int(math.floor(tail * (len(vals) - 1)))],
            vals[int(math.ceil((1 - tail) * (len(vals) - 1)))])


def ols(xs, ys):
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    return b, my - b * mx


# -- main ---------------------------------------------------------------------------------

def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results-dir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--archive-commit", default=ARCHIVE_COMMIT)
    a = ap.parse_args(argv)
    os.makedirs(a.out, exist_ok=True)
    stats, stats_path = load_stats()
    invalid: list[str] = []

    # P0 ------------------------------------------------------------------------------
    inputs, rows_by_file = {}, {}
    for name, role in FILES:
        path = os.path.join(a.results_dir, name)
        try:
            blob = open(path, "rb").read()
            text = gzip.decompress(blob).decode()
        except OSError as exc:
            invalid.append(f"I-1 unreadable input {name}: {exc}")
            continue
        rel = os.path.relpath(os.path.abspath(path), REPO)
        arch = subprocess.run(["git", "show", f"{a.archive_commit}:{rel}"], cwd=REPO,
                              capture_output=True)
        arch_digest = sha256_bytes(arch.stdout) if arch.returncode == 0 else None
        digest = sha256_bytes(blob)
        if arch_digest != digest:
            invalid.append(f"I-1 digest of {name} differs from archive {a.archive_commit}")
        rows = [json.loads(l) for l in text.splitlines() if l.strip()]
        rows_by_file[name] = rows
        counts: dict[str, int] = {}
        for r in rows:
            k = "|".join(str(x) for x in (r["method"], r["fb"], r.get("engine", "enumerate" if r["method"] != "rho" else "-"),
                                          r.get("la_pivot", "min_index" if r["method"] != "rho" else "-")))
            counts[k] = counts.get(k, 0) + 1
        inputs[name] = {"path": rel, "role": role, "sha256": digest,
                        "archive_sha256": arch_digest, "line_count": len(rows),
                        "count_by_method_fb_engine_pivot": counts,
                        "ok_false_rows": [list(key_of(r)) if r["method"] != "rho" else
                                          [r["bits"], r["curve"], "rho"] for r in rows if not r["ok"]]}
    readme_crosscheck = {}
    if len(rows_by_file) == 5:
        mitm = rows_by_file["sweep-mitm-20260926.jsonl.gz"]
        mf = [r for n in ("sweep-minfill-20260926.jsonl.gz", "sweep-arity-minfill-20260926.jsonl.gz")
              for r in rows_by_file[n] if r["method"] != "rho"]
        a67 = rows_by_file["sweep-arity67-20260928.jsonl.gz"]
        readme_crosscheck = {
            "sweep-mitm-20260926 rows": {"readme": 380, "file": len(mitm)},
            "min_fill sweeps IC rows": {"readme": 330, "file": len(mf)},
            "arity67 mitm rows": {"readme": 110, "file": sum(1 for r in a67 if r.get("engine") == "mitm")},
            "arity67 enumerate rows": {"readme": 20, "file": sum(1 for r in a67 if r.get("engine") == "enumerate")},
            "arity67 rho rows": {"readme": 110, "file": sum(1 for r in a67 if r["method"] == "rho")},
        }
    result = {"experiment_id": "EXP-PFDR-7c8bf2", "run_id": "RUN-PFDR-7c8bf2-stage0",
              "inputs": inputs, "readme_row_count_crosscheck": readme_crosscheck,
              "stats_module": {"path": os.path.relpath(stats_path, REPO),
                               "loaded_as": "pfdr_stage0_stats (importlib, package __init__ not executed)"},
              "bootstrap": {"reps": REPS, "seed": SEED, "level": 0.95},
              "certificate": {"kind": "none",
                              "note": "no solve and no relation claimed; ratios and fits of committed rows"}}

    def finish(outcome: str, conditions: list[str]) -> int:
        loaded = sorted(m for m in sys.modules if m.startswith("crypto_autoresearcher"))
        result["solver_modules_loaded"] = loaded
        if loaded:
            invalid.append(f"I-3 solver modules loaded: {loaded}")
            outcome = "OUT-INVALID"
        result["invalidations"] = invalid
        result["outcome_conditions_met"] = conditions
        result["outcome_id"] = outcome
        result["outcome_precedence_rule"] = (
            "first met in the order of analysis_outcomes: OUT-INVALID, OUT-FLOOR-VIOLATION, "
            "OUT-SLOPE-INTERVAL, OUT-PREDICTION-MISS; OUT-CONSISTENT only if none is met")
        with open(os.path.join(a.out, "raw-result.json"), "w") as fh:
            json.dump(result, fh, indent=2, sort_keys=True)
        print(json.dumps({"outcome_id": outcome, "conditions_met": conditions,
                          "invalidations": invalid}, indent=2))
        return 0

    if invalid:
        return finish("OUT-INVALID", ["OUT-INVALID"])

    # P1 twin consistency ---------------------------------------------------------------
    twin = {}
    for tfile, pfile in TWINS:
        prim = {key_of(r): r for r in rows_by_file[pfile] if r.get("engine") == "mitm"}
        checked, missing, unequal = 0, [], []
        for r in rows_by_file[tfile]:
            if r.get("engine") != "mitm":
                continue
            k = key_of(r)
            q = prim.get(k)
            if q is None:
                missing.append(list(k))
                continue
            checked += 1
            diff = [f for f in TWIN_FIELDS if r.get(f) != q.get(f)]
            if diff:
                unequal.append({"key": list(k), "fields": diff})
        twin[f"{tfile} vs {pfile}"] = {"mitm_rows_checked": checked, "missing_twin": missing,
                                       "unequal": unequal, "fields": TWIN_FIELDS}
        if missing or unequal:
            invalid.append(f"I-2 twin mismatch {tfile} vs {pfile}")
    result["P1_consistency"] = twin
    if invalid:
        return finish("OUT-INVALID", ["OUT-INVALID"])

    # P2 per-row -------------------------------------------------------------------------
    floor_rows, rho_seen, rho_rows = [], set(), []
    for name, _ in FILES:
        for r in rows_by_file[name]:
            if r["method"] == "rho":
                k = (r["p"], r["a"], r["b"], r["curve"], r["bits"])
                if k in rho_seen:
                    continue
                rho_seen.add(k)
                rho_rows.append({"file": name, "bits": r["bits"], "curve": r["curve"],
                                 "p_filter": r["p_filter"], "p": r["p"], "N": r["N"],
                                 "log2N": r["log2N"], "walk_ops": r["walk_ops"],
                                 "rho_ratio": r["walk_ops"] / (0.886 * math.sqrt(r["N"]))})
                continue
            if not r["ok"]:
                continue
            engine = r.get("engine", "enumerate")
            S = r["s3_solves"]
            T = r.get("table_s3_solves", 0) if engine == "mitm" else 0
            rr, N = r["relations"], r["N"]
            floor = 0.5 * math.sqrt(rr * N)
            fr = {"file": name, "bits": r["bits"], "curve": r["curve"], "method": r["method"],
                  "m": m_of(r), "fb": r["fb"], "engine": engine,
                  "la_pivot": r.get("la_pivot", "min_index"), "p": r["p"], "N": N,
                  "log2N": r["log2N"], "fb_size": r["fb_size"], "S": S, "T": T, "search": S - T,
                  "relations": rr, "table_entries": r.get("table_entries"),
                  "floor": floor, "ratio": S / floor, "table_share": T / S}
            if engine == "mitm":
                X_t, X_s = r["table_entries"], 2 * (S - T)
                mu = 2 * X_t * X_s / N
                fr.update({"X_t": X_t, "X_s": X_s, "mu_TS": mu, "q": rr / mu if mu else None})
            floor_rows.append(fr)
    buf = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", fileobj=buf, mtime=0) as gz:
        for fr in floor_rows + [dict(x, kind="rho") for x in rho_rows]:
            gz.write((json.dumps(fr, sort_keys=True) + "\n").encode())
    with open(os.path.join(a.out, "floor-rows.jsonl.gz"), "wb") as fh:
        fh.write(buf.getvalue())
    result["P2_rows"] = {"ic_rows": len(floor_rows), "rho_rows_deduplicated": len(rho_rows)}

    # P3/P4 series fits ---------------------------------------------------------------
    def series_rows(name):
        f, m, fb = SERIES[name]
        return [x for x in floor_rows if x["file"] == f and x["m"] == m and x["fb"] == fb
                and x["engine"] == "mitm"]

    fits = {}
    tails = {}
    for name in SERIES:
        sel = series_rows(name)
        out = {"n_rows": len(sel), "m": SERIES[name][1], "file": SERIES[name][0], "fb": SERIES[name][2]}
        for label, lo in (("primary_12_32", 12), ("sensitivity_20_32", 20)):
            ss = [x for x in sel if lo <= x["bits"] <= 32]
            out[label] = stats.bootstrap_slope([x["log2N"] for x in ss],
                                               [math.log2(x["ratio"]) for x in ss],
                                               groups=[x["bits"] for x in ss],
                                               reps=REPS, level=0.95, seed=SEED)
        # tail: smallest ratio row, largest abs residual of the 12..32 fit
        xs = [x["log2N"] for x in sel]
        ys = [math.log2(x["ratio"]) for x in sel]
        b, c0 = ols(xs, ys)
        resid = [(abs(y - (c0 + b * x)), s) for x, y, s in zip(xs, ys, sel)]
        big = max(resid, key=lambda t: t[0])
        small = min(sel, key=lambda x: x["ratio"])
        tails[name] = {"smallest_ratio_row": {k: small[k] for k in ("bits", "curve", "fb", "ratio", "S", "relations", "N")},
                       "largest_abs_residual_12_32": {"abs_residual_log2": big[0],
                                                      **{k: big[1][k] for k in ("bits", "curve", "fb", "ratio")}}}
        fits[name] = out
    # P5 minimum ratio ---------------------------------------------------------------------
    mn = min(floor_rows, key=lambda x: x["ratio"])
    below1 = [{k: x[k] for k in ("file", "bits", "curve", "method", "fb", "engine", "ratio", "S",
                                 "relations", "N")} for x in floor_rows if x["ratio"] < 1.0]
    p5 = {"min_ratio": mn["ratio"],
          "min_row": {k: mn[k] for k in ("file", "bits", "curve", "method", "fb", "engine", "ratio")},
          "rows_below_1": below1, "rows_below_0_9": [x for x in below1 if x["ratio"] < 0.9],
          "n_rows": len(floor_rows)}

    # P6 m = 3 base overlap on sweep-minfill ---------------------------------------------
    p6 = {}
    for fb in ("small_x", "random", "subgroup"):
        sel = [x for x in floor_rows if x["file"] == "sweep-minfill-20260926.jsonl.gz"
               and x["m"] == 3 and x["fb"] == fb and x["engine"] == "mitm" and 20 <= x["bits"] <= 32]
        by_rung: dict[int, list[float]] = {}
        for x in sel:
            by_rung.setdefault(x["bits"], []).append(math.log(x["ratio"]))
        allv = [v for vs in by_rung.values() for v in vs]
        gm = math.exp(sum(allv) / len(allv))
        rng = random.Random(SEED)
        boots = []
        for _ in range(REPS):
            smp = [rng.choice(vs) for b_ in sorted(by_rung) for vs in [by_rung[b_]] for _ in vs]
            boots.append(math.exp(sum(smp) / len(smp)))
        lo, hi = percentile_interval(boots)
        p6[fb] = {"geometric_mean_ratio": gm, "ci95": [lo, hi], "n_rows": len(sel),
                  "rungs": sorted(by_rung)}
    pairs = {}
    names = ["small_x", "random", "subgroup"]
    for i in range(3):
        for j in range(i + 1, 3):
            A, B = p6[names[i]]["ci95"], p6[names[j]]["ci95"]
            pairs[f"{names[i]}|{names[j]}"] = A[0] <= B[1] and B[0] <= A[1]
    p6_out = {"per_base": p6, "pairwise_overlap": pairs,
              "bootstrap_note": "random.Random(0) per base; curves resampled with replacement within each rung"}

    # P7 controls ----------------------------------------------------------------------------
    rho_sets = {}
    for lab in sorted({x["p_filter"] for x in rho_rows}):
        sel = [x for x in rho_rows if x["p_filter"] == lab]
        per_rung = {str(b): statistics.median(x["rho_ratio"] for x in sel if x["bits"] == b)
                    for b in sorted({x["bits"] for x in sel})}
        rho_sets[lab] = {"n": len(sel), "median_rho_ratio_per_rung": per_rung,
                         "walk_exponent": stats.bootstrap_slope(
                             [x["log2N"] for x in sel], [math.log2(x["walk_ops"]) for x in sel],
                             groups=[x["bits"] for x in sel], reps=REPS, level=0.95, seed=SEED)}
    h2 = {}
    for name in SERIES:
        ss = [x for x in series_rows(name) if 20 <= x["bits"] <= 32]
        h2[name] = stats.bootstrap_slope([x["log2N"] for x in ss],
                                         [math.log2(x["relations"] / x["fb_size"]) for x in ss],
                                         groups=[x["bits"] for x in ss], reps=REPS, level=0.95, seed=SEED)
    h1 = {}
    prim = [x for name in SERIES for x in series_rows(name)]
    for m in sorted({x["m"] for x in prim}):
        sel = [x for x in prim if x["m"] == m]
        c_m = sum(x["relations"] for x in sel) / sum(x["mu_TS"] for x in sel)
        us = []
        for x in sel:
            mu = c_m * x["mu_TS"]
            n = x["relations"]
            V = random.Random(f"pit-7c8bf2|{x['file']}|{x['bits']}|{x['curve']}|{x['fb']}|{m}").random()
            F1, F0 = poisson_cdf(n, mu), poisson_cdf(n - 1, mu)
            us.append(F0 + V * (F1 - F0))
        h1[str(m)] = {"c_m": c_m, "n_rows": len(sel),
                      "median_q": statistics.median(x["q"] for x in sel),
                      "ks_randomized_pit_vs_poisson": ks_uniform(us)}
    share32 = {}
    for name in SERIES:
        sel = [x for x in series_rows(name) if x["bits"] == 32]
        share32[name] = {"median": statistics.median(x["table_share"] for x in sel) if sel else None,
                         "values": [x["table_share"] for x in sel]}
    p7 = {"a_rho": rho_sets, "b_H2_relations_per_fb_slope_20_32": h2,
          "c_H1_descriptive": {"label": "DESCRIPTIVE, not decision-bearing (stopping-rule confound)",
                               "rows_used": "primary-series rows only (P3: min_index twins never pooled)",
                               "per_m": h1},
          "d_table_share_at_32_bits": share32}

    fits_json = {"series": fits, "min_ratio": p5["min_ratio"], "rows_below_1": below1,
                 "m3_base_geometric_means": p6_out, "rho": rho_sets,
                 "note": "generic floor 0.5*sqrt(r*N); ratio = S_3/floor; slopes vs log2 N"}
    with open(os.path.join(a.out, "fits.json"), "w") as fh:
        json.dump(fits_json, fh, indent=2, sort_keys=True)

    # outcome ------------------------------------------------------------------------------
    conds = []
    if p5["rows_below_0_9"]:
        conds.append("OUT-FLOOR-VIOLATION")
    slope_int = []
    miss = []
    for name, f in fits.items():
        m = f["m"]
        pf = f["primary_12_32"]
        target = 0.0 if m % 2 else 1.0 / (2 * m)
        if pf["lo"] is not None and not (pf["lo"] <= target <= pf["hi"]):
            slope_int.append({"series": name, "m": m, "ci": [pf["lo"], pf["hi"]], "excluded": target})
        lo, hi = WINDOWS[m]
        if not (lo <= pf["slope"] <= hi):
            miss.append({"series": name, "slope": pf["slope"], "window": [lo, hi]})
    if slope_int:
        conds.append("OUT-SLOPE-INTERVAL")
    nonoverlap = [k for k, v in pairs.items() if not v]
    if miss or nonoverlap or (0.9 <= p5["min_ratio"] < 1.0):
        conds.append("OUT-PREDICTION-MISS")
    result.update({"P3_P4_fits": fits, "tail_checks": tails, "P5_min": p5, "P6_bases": p6_out,
                   "P7_controls": p7,
                   "condition_details": {"slope_interval_exclusions": slope_int,
                                         "point_estimates_outside_window": miss,
                                         "non_overlapping_base_pairs": nonoverlap,
                                         "min_ratio_in_0.9_1.0": 0.9 <= p5["min_ratio"] < 1.0},
                   "windows": {str(k): v for k, v in WINDOWS.items()}})
    order = ["OUT-FLOOR-VIOLATION", "OUT-SLOPE-INTERVAL", "OUT-PREDICTION-MISS"]
    outcome = next((o for o in order if o in conds), "OUT-CONSISTENT")
    return finish(outcome, conds or ["OUT-CONSISTENT"])


if __name__ == "__main__":
    raise SystemExit(main())
