"""EXP-PFDR-011cd0 fixture builder for the pre-pin exercise (card PINNED BEFORE DATA).

Writes everything under FX (the task scratch, never archived) and never touches a panel file:

(A) TOY ENGINE fixtures (real row formats, 12-14-bit curves c in {0, 1}, outside every census
    rung): built by calling the census CLI directly (not run_jobs.py):
      A1 a table run, a search run and a search-check run (merge, tabcompare, srchcompare, grel,
         curvecheck, verify_rows), as attempt layouts with jobs-index.json / jobs-spec.json;
      A2 an "archived" EXP-PFDR-1b78f7-like layout (census-m3 root, census-m4 merged/ +
         merge-report.json, census-m5 root + merge-report.json) from the legacy census
         invocation, with two PLANTED edits: an SS pairs_raw lowered on an instance holding a
         straddling SS group (attributable) and an s3_solves changed (unattributed);
      A3 the matching R10-like new run (--relcount --solve-certs per job, harvest rows in a
         scratch directory) for fixcompare.
(B) SYNTHETIC COUNT panel (numbers drawn here, no engine): table and search run roots with
    random, known-null, structured, planted and known_log arms on synthetic curves, a PLANTED
    EXCESS OF KNOWN SIZE (subgroup TT3 at kappa = 1.5; planted_sub n_tt = 2, n_tb = 1 per
    curve with the planted relation rows), PC-1 known_log rows, and a synthetic design.json.
(C) synthetic P0 inputs: a fake specification with small declared n, synthetic design curves,
    the A2 archive relabelled to 30/32 bits, and a bundles file with one PLANTED wrong count.
"""
from __future__ import annotations

import argparse
import gzip
import json
import math
import os
import random
import shutil
import subprocess
import sys

REPO = "/home/user/crypto-autoresearcher"
PY = sys.executable
CLI = [PY, "-m", "crypto_autoresearcher.index_calculus", "census", "--panel", "main"]
ARMS_11 = ["subgroup", "dickson", "small_x", "random_sub_r0", "random_sub_r1", "random_sub_r2",
           "known_null_sub", "random_dick_r0", "random_dick_r1", "random_dick_r2", "known_null_dick"]


def sh(cmd, **kw):
    r = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, **kw)
    if r.returncode not in (0, 1):
        raise SystemExit(f"command failed {cmd}: {r.stderr[-2000:]}")
    return r


def gz(path):
    subprocess.run(["gzip", "-n", "-f", path], check=True)
    return path + ".gz"


def read(path):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt") as fh:
        return [json.loads(l) for l in fh if l.strip()]


def write(path, recs):
    with open(path, "w") as fh:
        for r in recs:
            fh.write(json.dumps(r) + "\n")


def is_prime(n):
    if n < 2:
        return False
    for q in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % q == 0:
            return n == q
    d, r = n - 1, 0
    while d % 2 == 0:
        d //= 2
        r += 1
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(r - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


# ------------------------------------------------------------------------------------------
# (A) toy engine fixtures

def attempt_from_cli(run_dir, jobs, extra_args, mode_list, certs=False, bases=False, scratch_rows=None):
    """Run each job with the census CLI into run_dir/attempt-1/jobs/<name>/ and write a
    jobs-index.json / jobs-spec.json like run_jobs.py's."""
    ad = os.path.join(run_dir, "attempt-1")
    os.makedirs(os.path.join(ad, "jobs"))
    index, spec = [], []
    for (name, m, b, c0, k, arms) in jobs:
        jd = os.path.join(ad, "jobs", name)
        os.makedirs(jd)
        hr = os.path.join(scratch_rows, name, "harvest-rows.jsonl") if scratch_rows else os.path.join(jd, "harvest-rows.jsonl")
        os.makedirs(os.path.dirname(hr), exist_ok=True)
        cmd = CLI + ["--m", str(m), "--bits", str(b), "--curve-offset", str(c0), "--curves", str(k)]
        if arms:
            cmd += ["--arms", *arms]
        cmd += extra_args + ["--workers", "1", "--quiet", "--out", os.path.join(jd, "rows.jsonl"),
                             "--rows-out", hr, "--staircase-out", os.path.join(jd, "staircase.jsonl")]
        if certs:
            cmd += ["--solve-certs", os.path.join(jd, "solve-certs.jsonl")]
        if bases:
            cmd += ["--bases-out", os.path.join(jd, "bases.jsonl"), "--bases-sample-mod", "1"]
        sh(cmd)
        for f in os.listdir(jd):
            if f.endswith(".jsonl"):
                gz(os.path.join(jd, f))
        rec = {"job": name, "m": m, "bits": b, "curve_offset": c0, "curves": k,
               "job_dir": os.path.relpath(jd, REPO), "started_at": "fixture", "ended_at": "fixture",
               "status_counts": {}, "missing_keys": [], "duplicate_keys": [], "non_job_keys": [],
               "invalid_instances": [], "failed_infrastructure_instances": [], "g4_fail_instances": [],
               "g5_fail_instances": [], "checks_failed_instances": [], "files_above_95MB": [],
               "expected_keys": 0}
        if scratch_rows:
            gz(hr)
            rec["scratch_harvest_rows"] = {"path": hr + ".gz", "sha256": None}
        rows = read(os.path.join(jd, "rows.jsonl.gz"))
        arms_eff = sorted({r["arm"] for r in rows})
        exp = [[b, c, m, a, md] for c in range(c0, c0 + k) for a in arms_eff for md in mode_list]
        rec["expected_keys"] = len(exp)
        index.append(rec)
        spec.append({"name": name, "m": m, "bits": b, "curve_offset": c0, "curves": k, "expected_keys": exp})
    json.dump({"run_id": os.path.basename(run_dir), "jobs": index, "not_started": [],
               "not_started_reason": None, "run_stop_at_job": None, "checkpoint": None, "dummy": False,
               "started_at": "fixture", "finished_at": "fixture", "wall_seconds": 0},
              open(os.path.join(ad, "jobs-index.json"), "w"), indent=1)
    json.dump({"run": "fixture", "jobs": spec}, open(os.path.join(ad, "jobs-spec.json"), "w"), indent=1)


def build_A1(FX):
    runs = os.path.join(FX, "A1", "runs")
    common = ["--known-log-max-bits", "0", "--relcount"]
    jobs = [("3-b12-c0", 3, 12, 0, 2, ARMS_11 + ["planted_sub"]), ("4-b14-c0", 4, 14, 0, 2, ARMS_11)]
    attempt_from_cli(os.path.join(runs, "RUN-PFDR-011cd0-table"), jobs,
                     common + ["--modes", "table", "--retain", "all"], ["table"], bases=True)
    jobs_s = [("3-b12-c0", 3, 12, 0, 2, ARMS_11), ("4-b14-c0", 4, 14, 0, 2, ARMS_11)]
    attempt_from_cli(os.path.join(runs, "RUN-PFDR-011cd0-search"), jobs_s,
                     common + ["--modes", "search", "--encoding-budget-lambda", "4", "--retain", "all",
                               "--digest-classes", "TT", "TB"], ["search"], bases=True)
    attempt_from_cli(os.path.join(runs, "RUN-PFDR-011cd0-srch-check"), jobs_s,
                     common + ["--modes", "census", "--budget-snapshot-only", "--encoding-budget-lambda", "4",
                               "--retain", "xfix", "--digest-classes", "TT", "TB"], ["census"], certs=True)
    # planted duplicate: a repeated row in the table job; a missing key: one row dropped from the search job
    jd = os.path.join(runs, "RUN-PFDR-011cd0-table", "attempt-1", "jobs", "3-b12-c0")
    rows = read(os.path.join(jd, "rows.jsonl.gz"))
    os.remove(os.path.join(jd, "rows.jsonl.gz"))
    write(os.path.join(jd, "rows.jsonl"), rows + [rows[0]])
    gz(os.path.join(jd, "rows.jsonl"))
    # a design.json for curvecheck: every (bits, c) of A1 with one PLANTED wrong N
    curves = {}
    for run in ("RUN-PFDR-011cd0-table", "RUN-PFDR-011cd0-search"):
        ad = os.path.join(runs, run, "attempt-1", "jobs")
        for j in os.listdir(ad):
            for r in read(os.path.join(ad, j, "rows.jsonl.gz")):
                curves[(r["bits"], r["curve"])] = {"bits": r["bits"], "curve": r["curve"], "p": r["p"],
                                                   "a": r["a"], "b": r["b"], "N": r["N"], "P": r["P"]}
    good = [curves[k] for k in sorted(curves)]
    json.dump({"curves": good}, open(os.path.join(FX, "A1", "design-good.json"), "w"))
    bad = [dict(c) for c in good]
    bad[0]["N"] += 2
    json.dump({"curves": bad}, open(os.path.join(FX, "A1", "design-planted-mismatch.json"), "w"))


def build_A2_A3(FX):
    """Archive-like layout from the legacy census invocation, and an R10-like new run."""
    arch = os.path.join(FX, "A2", "runs")
    tmp = os.path.join(FX, "A2", "tmp")
    os.makedirs(tmp)
    per_m = {}
    for m in (3, 4, 5):
        d = os.path.join(tmp, f"m{m}")
        os.makedirs(d)
        klm = "14" if m == 3 else "0"
        sh(CLI + ["--m", str(m), "--bits", "12", "14", "--curves", "2", "--known-log-max-bits", klm,
                  "--workers", "1", "--quiet", "--out", f"{d}/rows.jsonl", "--rows-out", f"{d}/harvest-rows.jsonl",
                  "--staircase-out", f"{d}/staircase.jsonl"])
        per_m[m] = d
    # PLANTED edits on the archived (old) rows
    rows3 = read(f"{per_m[3]}/rows.jsonl")
    h3 = read(f"{per_m[3]}/harvest-rows.jsonl")
    # find an instance with an SS group of >= 3 members spanning >= 2 attempts (straddle)
    from collections import defaultdict
    groups = defaultdict(lambda: defaultdict(list))
    for r in h3:
        if r["class"] == "SS":
            k = (r["bits"], r["curve"], r["m"], r["arm"], r["mode"])
            groups[k][json.dumps(r["elements"][0], sort_keys=True)].append(r)
    straddle_key = None
    for k, g in groups.items():
        for v in g.values():
            atts = {v[0]["elements"][0]["enc"][0]} | {r["attempt"] for r in v}
            if len(v) + 1 >= 3 and len(atts) >= 2:
                straddle_key = k
                break
        if straddle_key:
            break
    planted = {"straddle_key": list(straddle_key) if straddle_key else None}
    other_key = None
    for r in rows3:
        k = (r["bits"], r["curve"], 3, r["arm"], r["mode"])
        if straddle_key and k == straddle_key:
            r["harvest"]["SS"]["at_stop"]["pairs_raw"] -= 1
            r["harvest"]["SS"]["at_stop"]["pairs_nonformal"] -= 1
        elif other_key is None and r["arm"] == "random_sub_r1" and r["mode"] == "census":
            r["s3_solves"] += 1
            other_key = list(k)
    planted["s3_solves_changed_key"] = other_key
    m3 = os.path.join(arch, "RUN-PFDR-1b78f7-census-m3")
    os.makedirs(m3)
    write(f"{m3}/rows.jsonl", rows3)
    gz(f"{m3}/rows.jsonl")
    shutil.copy(f"{per_m[3]}/harvest-rows.jsonl", f"{m3}/harvest-rows.jsonl")
    gz(f"{m3}/harvest-rows.jsonl")
    shutil.copy(f"{per_m[3]}/staircase.jsonl", f"{m3}/staircase.jsonl")
    gz(f"{m3}/staircase.jsonl")
    for m, sub in ((4, "RUN-PFDR-1b78f7-census-m4/merged"), (5, "RUN-PFDR-1b78f7-census-m5")):
        d = os.path.join(arch, sub)
        os.makedirs(d)
        for f in ("rows.jsonl", "staircase.jsonl"):
            shutil.copy(f"{per_m[m]}/{f}", f"{d}/{f}")
            gz(f"{d}/{f}")
        jd = os.path.join(arch, sub.split("/")[0], "attempt-1", "jobs", "all")
        os.makedirs(jd)
        shutil.copy(f"{per_m[m]}/harvest-rows.jsonl", f"{jd}/harvest-rows.jsonl")
        hp = gz(f"{jd}/harvest-rows.jsonl")
        hmap = {}
        for r in read(f"{d}/rows.jsonl.gz"):
            hmap[json.dumps(["main", m, r["bits"], r["curve"], r["arm"], r["mode"]])] = {
                "harvest_rows_file": hp, "sha256": None}
        json.dump({"harvest_rows_map": hmap}, open(f"{d}/merge-report.json", "w"))
    # A3: the R10-like new run (per job, --relcount --solve-certs, harvest rows to scratch)
    new = os.path.join(FX, "A3", "RUN-PFDR-011cd0-fix-check")
    jobs = [(f"{m}-b{b:02d}-c{c}", m, b, c, 1, None) for m in (3, 4, 5) for b in (12, 14) for c in (0, 1)]
    # --known-log-max-bits 14 for every job: known_log runs only at m = 3 (as archived)
    attempt_from_cli(new, jobs, ["--known-log-max-bits", "14", "--relcount"], ["census", "on"], certs=True,
                     scratch_rows=os.path.join(FX, "A3", "scratch-rows"))
    return planted


# ------------------------------------------------------------------------------------------
# (B) synthetic count panel

def synth_panel(FX, seed=11):
    rng = random.Random(seed)
    out = os.path.join(FX, "B", "runs")
    design_n = {"table": {3: {20: 6, 22: 6, 24: 10, 26: 6, 28: 30, 30: 40, 32: 40},
                          4: {20: 6, 22: 6, 24: 6, 26: 6, 28: 6, 30: 40, 32: 40},
                          5: {20: 6, 22: 6, 24: 6, 26: 6, 28: 6, 30: 24, 32: 24}},
                "search": {3: {b: (4 if b < 30 else 10) for b in (20, 22, 24, 26, 28, 30, 32)},
                           4: {b: (4 if b < 30 else 12) for b in (20, 22, 24, 26, 28, 30, 32)},
                           5: {b: (4 if b < 30 else 10) for b in (20, 22, 24, 26, 28, 30, 32)}}}
    S = {3: 120, 4: 150, 5: 40}
    curves = {}
    for b in (20, 22, 24, 26, 28, 30, 32):
        nmax = max(design_n[p][m][b] for p in design_n for m in (3, 4, 5))
        for c in range(10, 10 + max(nmax, 20)):
            N = 10_000_000 + 1000 * b + 37 * c
            while not is_prime(N):
                N += 1
            curves[(b, c)] = {"bits": b, "curve": c, "p": N + 3, "a": 1, "b": 2, "N": N, "P": [1, 2],
                              "log2N": float(b) + c / 1000.0, "X_fix": 20 * math.isqrt(N),
                              "sizes": {str(m): {"size0": S[m], "F_sub": S[m], "s_sub": S[m],
                                                 "F_dick": S[m], "s_dick": S[m]} for m in (3, 4, 5)}}

    def Ep(s, m):
        h = 2 if m in (3, 4) else 3
        return s * s if h == 2 else 4 * math.comb(s + 2, 3) - 2 * math.comb(s + 1, 2)

    def pois(mu):
        # Knuth for small, normal approx for large
        if mu > 60:
            return max(0, int(round(rng.gauss(mu, math.sqrt(mu)))))
        L, k, p = math.exp(-mu), 0, 1.0
        while True:
            p *= rng.random()
            if p <= L:
                return k
            k += 1

    arms_t = {3: ARMS_11 + ["planted_sub"], 4: ARMS_11, 5: ARMS_11}
    table_rows, search_rows, hrows_planted = [], [], []
    truth = {"planted_excess_subgroup_TT3_kappa": 1.5, "planted_sub_n_tt": 2, "planted_sub_n_tb": 1}
    for m in (3, 4, 5):
        h = 2 if m in (3, 4) else 3
        for b in (20, 22, 24, 26, 28, 30, 32):
            for c in range(10, 10 + design_n["table"][m][b]):
                cv = curves[(b, c)]
                N, s = cv["N"], S[m]
                E = Ep(s, m)
                mu = {"TT": E * (E - 1) / N / (3 if h == 2 else 10), "TB": 2 * E * s / N / (h + 1)}
                for arm in arms_t[m]:
                    blk = {}
                    rels = []
                    for cls in ("TT", "TB"):
                        n = pois(mu[cls])
                        if arm == "subgroup" and cls == "TT" and m == 3:
                            n += pois(0.5 * mu[cls])
                        if arm == "planted_sub" and m == 3:
                            n += 2 if cls == "TT" else 1
                        Mg = 3 if (h == 2 or cls == "TB") else 10
                        if cls == "TB" and h == 3:
                            Mg = 4
                        blk[cls] = {"at_stop": {"relations_nonformal": n, "relations_distinct": n,
                                                "relations_distinct_sign": n, "pairs_nonformal": n * Mg,
                                                "informative_rank": n, "R_star": n, "rows_emitted": n,
                                                "cert_fail": 0, "cert_pass": n,
                                                "multiplicity_histogram": ({str(Mg): n} if n else {})}}
                    blk["SS"] = {"at_stop": {"relations_nonformal": 0, "rows_emitted": 0, "cert_fail": 0,
                                             "cert_pass": 0, "informative_rank": 0, "R_star": 0}}
                    params = {}
                    if arm == "planted_sub":
                        params = {"planted_relations": [
                            {"class": "TT", "indices": [0, 1, 2, 3], "signs": [1, 1, -1, -1]},
                            {"class": "TT", "indices": [4, 5, 6, 7], "signs": [1, 1, -1, -1]},
                            {"class": "TB", "indices": [8, 9, 10], "signs": [1, 1, -1]}]}
                        key = {"bits": b, "curve": c, "m": m, "arm": arm, "mode": "table"}
                        hrows_planted += [
                            key | {"class": "TT", "attempt": -1, "elements": [{"tail": [[0, 1], [1, 1]], "ybit": 0},
                                                                             {"tail": [[2, 1], [3, 1]], "ybit": 0}],
                                   "coeffs": [[0, 1], [1, 1], [2, -1], [3, -1]], "kcoef": 0, "rhs": 0},
                            key | {"class": "TT", "attempt": -1, "elements": [{"tail": [[4, 1], [5, 1]], "ybit": 0},
                                                                             {"tail": [[6, 1], [7, 1]], "ybit": 0}],
                                   "coeffs": [[4, 1], [5, 1], [6, -1], [7, -1]], "kcoef": 0, "rhs": 0},
                            key | {"class": "TB", "attempt": -1, "elements": [{"base": 10},
                                                                             {"tail": [[8, 1], [9, 1]], "ybit": 0}],
                                   "coeffs": [[8, -1], [9, -1], [10, 1]], "kcoef": 0, "rhs": 0}]
                    fb = {"subgroup": "subgroup", "dickson": "dickson", "small_x": "small_x",
                          "planted_sub": "planted"}.get(arm, "random")
                    table_rows.append({"bits": b, "curve": c, "m": m, "arm": arm, "mode": "table", "N": N,
                                       "p": cv["p"], "a": 1, "b": 2, "P": [1, 2],
                                       "log2N": cv["log2N"], "fb": fb, "fb_size": s, "fb_params": params,
                                       "status": "completed_valid", "checks": {},
                                       "harvest": blk | {"U": s, "table": {"formally_distinct_tails": E}}})
            if m == 3 and b in (20, 24):
                for c in range(10, 20):
                    cv = curves[(b, c)]
                    blk = {cls: {"at_stop": {"relations_nonformal": 0, "relations_distinct": 500 + c,
                                             "relations_distinct_sign": 500 + c, "pairs_nonformal": 0,
                                             "informative_rank": 0, "R_star": 50, "rows_emitted": 1000,
                                             "cert_fail": 0, "cert_pass": 1000, "multiplicity_histogram": {}}}
                           for cls in ("TT", "TB")}
                    blk["SS"] = {"at_stop": {"relations_nonformal": 0, "rows_emitted": 0, "informative_rank": 0, "R_star": 0}}
                    table_rows.append({"bits": b, "curve": c, "m": 3, "arm": "known_log", "mode": "table",
                                       "N": cv["N"], "log2N": cv["log2N"], "fb": "known_log", "fb_size": S[3],
                                       "status": "completed_valid",
                                       "checks": {"G6_known_log_Fj_eq_jP": True, "G6_known_log_formal_rank": True},
                                       "harvest": blk | {"U": 1, "table": {"formally_distinct_tails": Ep(S[3], 3)}}})
            for c in range(10, 10 + design_n["search"][m][b]):
                cv = curves[(b, c)]
                N, X = cv["N"], cv["X_fix"]
                for arm in ARMS_11:
                    n = pois(X * (X - 1) / N / 1.8)
                    st = {"relations_nonformal": n, "relations_distinct": n, "relations_distinct_sign": n,
                          "pairs_nonformal": int(n * 1.8), "multiplicity_histogram": {"1": n // 5, "2": n - n // 5},
                          "formally_distinct_encodings": X, "X_fix": X, "censored": False, "rows_emitted": n}
                    blk = {"SS": {"at_stop": {"relations_nonformal": n, "informative_rank": n, "R_star": n,
                                              "rows_emitted": n, "cert_fail": 0, "cert_pass": n},
                                  "at_X_fix": st},
                           "TT": {"at_stop": {"relations_nonformal": 0, "informative_rank": 0, "R_star": 0}},
                           "TB": {"at_stop": {"relations_nonformal": 0, "informative_rank": 0, "R_star": 0}},
                           "U": S[m], "table": {"formally_distinct_tails": Ep(S[m], m)}}
                    search_rows.append({"bits": b, "curve": c, "m": m, "arm": arm, "mode": "search", "N": N,
                                        "p": cv["p"], "a": 1, "b": 2, "P": [1, 2],
                                        "log2N": cv["log2N"], "fb": "random", "fb_size": S[m],
                                        "status": "completed_valid", "checks": {}, "harvest": blk})
    for name, rows in (("RUN-PFDR-011cd0-table", table_rows), ("RUN-PFDR-011cd0-search", search_rows)):
        d = os.path.join(out, name)
        os.makedirs(d)
        rows.sort(key=lambda r: (r["bits"], r["curve"], r["m"], r["arm"], r["mode"]))
        write(os.path.join(d, "rows.jsonl"), rows)
        gz(os.path.join(d, "rows.jsonl"))
        hmap = {}
        if name.endswith("table"):
            write(os.path.join(d, "planted-harvest-rows.jsonl"), hrows_planted)
            hp = gz(os.path.join(d, "planted-harvest-rows.jsonl"))
            for r in rows:
                if r["arm"] == "planted_sub":
                    hmap[json.dumps([r["bits"], r["curve"], r["m"], r["arm"], r["mode"]])] = {
                        "harvest_rows_file": hp, "sha256": None}
        json.dump({"harvest_rows_map": hmap}, open(os.path.join(d, "merge-report.json"), "w"))
    design = {"final_n": {p: {str(m): {str(b): v for b, v in d.items()} for m, d in pm.items()}
                          for p, pm in design_n.items()},
              "curves": [curves[k] for k in sorted(curves)]}
    json.dump(design, open(os.path.join(FX, "B", "design.json"), "w"))
    json.dump(truth, open(os.path.join(FX, "B", "planted-truth.json"), "w"), indent=1)


# ------------------------------------------------------------------------------------------
# (C) synthetic P0 inputs

def build_C(FX):
    src = os.path.join(FX, "A2", "runs")
    dst = os.path.join(FX, "C", "runs")
    relabel = {12: 30, 14: 32}
    for root, dirs, files in os.walk(src):
        for f in files:
            sp = os.path.join(root, f)
            rp = os.path.relpath(sp, src)
            dp = os.path.join(dst, rp)
            os.makedirs(os.path.dirname(dp), exist_ok=True)
            if f.endswith(".jsonl.gz"):
                recs = read(sp)
                for r in recs:
                    if "bits" in r:
                        r["bits"] = relabel.get(r["bits"], r["bits"])
                write(dp[:-3], recs)
                gz(dp[:-3])
            elif f == "merge-report.json":
                mr = json.load(open(sp))
                hm = {}
                for k, v in mr["harvest_rows_map"].items():
                    kk = json.loads(k)
                    kk[2] = relabel.get(kk[2], kk[2])
                    v = dict(v, harvest_rows_file=v["harvest_rows_file"].replace(src, dst))
                    hm[json.dumps(kk)] = v
                json.dump({"harvest_rows_map": hm}, open(dp, "w"))
            else:
                shutil.copy(sp, dp)
    # bundles: an independent sign-only count from the relabelled archive, one PLANTED wrong count
    from collections import defaultdict
    bundles = []
    lay = {3: (os.path.join(dst, "RUN-PFDR-1b78f7-census-m3", "rows.jsonl.gz"),
               os.path.join(dst, "RUN-PFDR-1b78f7-census-m3", "harvest-rows.jsonl.gz"), "RUN-PFDR-1b78f7-census-m3/harvest-rows.jsonl.gz")}
    rows = read(lay[3][0])
    hr = defaultdict(list)
    for r in read(lay[3][1]):
        hr[(r["bits"], r["curve"], r["m"], r["arm"], r["mode"])].append(r)
    for r in rows:
        if not r["arm"].startswith("random_"):
            continue
        k = (r["bits"], r["curve"], 3, r["arm"], r["mode"])
        N = r["N"]
        for cls in ("TT", "TB", "SS"):
            groups = defaultdict(list)
            for x in hr[k]:
                if x["class"] == cls:
                    groups[json.dumps(x["elements"][0], sort_keys=True)].append(x)
            classes = set()
            for g in groups.values():
                vecs = []
                for x in g:
                    v = {i: c % N for i, c in x["coeffs"] if c % N}
                    if x["kcoef"] % N:
                        v["k"] = x["kcoef"] % N
                    if x["rhs"] % N:
                        v["r"] = x["rhs"] % N
                    vecs.append(v)
                pairs = [(None, v) for v in vecs]
                if cls != "TB":
                    for i in range(len(vecs)):
                        for j in range(i):
                            d = dict(vecs[i])
                            for kk, c in vecs[j].items():
                                d[kk] = (d.get(kk, 0) - c) % N
                            pairs.append((None, {a: b for a, b in d.items() if b}))
                for _, v in pairs:
                    if not v:
                        continue
                    order = sorted(v.items(), key=lambda t: (0, t[0]) if isinstance(t[0], int) else (1, 0 if t[0] == "k" else 1))
                    first = order[0][1]
                    if first * 2 > N:
                        order = [(a, (N - b) % N) for a, b in order]
                    classes.add(tuple(order))
            bundles.append({"arm": r["arm"], "bits": r["bits"], "curve": r["curve"], "m": 3, "mode": r["mode"],
                            "class": cls, "scope": "stop", "complete": True, "file": lay[3][2],
                            "relations": len(classes), "A_fix": r["harvest"]["attempt_budget_A_fix"]})
    bundles[3]["relations"] += 1  # PLANTED wrong count
    write(os.path.join(FX, "C", "bundles.jsonl"), bundles)
    # synthetic design curves at 20..32 bits
    recs = []
    for b in (20, 22, 24, 26, 28, 30, 32):
        n = 6 if b < 30 else 3 * 12
        for c in range(10, 10 + n):
            N = 2 ** (b - 1) + 101 * c + 1
            while not is_prime(N):
                N += 1
            sizes = {}
            for m in (3, 4, 5):
                s0 = max(4, math.ceil((math.factorial(m) * N / 2) ** (1 / m) / 2))
                sizes[str(m)] = {"size0": s0, "F_sub": s0, "s_sub": s0, "F_dick": s0, "s_dick": s0}
            recs.append({"bits": b, "curve": c, "p": N + 1, "a": 1, "b": 2, "N": N, "P": [1, 2],
                         "log2N": math.log2(N), "X_fix": 20 * math.isqrt(N), "sizes": sizes})
    write(os.path.join(FX, "C", "curves.jsonl"), recs)
    gz(os.path.join(FX, "C", "curves.jsonl"))
    spec = {"experiment": {"cells": {
        "table_panel_T": {"curves_per_rung_declared": {"m3": {"b30": 8, "b32": 8, "b20_to_b28": 6},
                                                        "m4": {"b30": 12, "b32": 12, "b20_to_b28": 6},
                                                        "m5": {"b30": 8, "b32": 8, "b20_to_b28": 6}}},
        "search_panel_S": {"curves_per_rung_declared": {"m3": {"b30": 4, "b32": 4, "b20_to_b28": 2},
                                                         "m4": {"b30": 4, "b32": 4, "b20_to_b28": 2},
                                                         "m5": {"b30": 4, "b32": 4, "b20_to_b28": 2}}}}}}
    import yaml
    yaml.safe_dump(spec, open(os.path.join(FX, "C", "fake-spec.yaml"), "w"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fx", required=True)
    a = ap.parse_args()
    if os.path.exists(a.fx):
        raise SystemExit(f"refusing: {a.fx} exists")
    os.makedirs(a.fx)
    build_A1(a.fx)
    planted = build_A2_A3(a.fx)
    synth_panel(a.fx)
    build_C(a.fx)
    json.dump(planted, open(os.path.join(a.fx, "A2", "planted.json"), "w"), indent=1)
    print(json.dumps({"fx": a.fx, "planted_A2": planted}))


if __name__ == "__main__":
    main()
