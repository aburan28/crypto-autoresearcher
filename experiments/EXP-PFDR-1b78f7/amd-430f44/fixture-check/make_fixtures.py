"""Synthetic fixtures for the pre-pin exercise of merge_census.py (TASK-20260929-89c123).

Every record is generated from random.Random(89123) with the census KEY and STATUS
fields plus random filler; no solver runs, no engine module is imported, and no panel
file or archived run file is read.  Layout mirrors protocol v3 (AMD-20260929-430f44):

  F1  r11like/        run root = frozen-invocation attempt 1 (rows / staircase / harvest-rows
                      .jsonl.gz, execution.json) with job-crash rows (10 arms x 2 modes, i.e.
                      2 non-cell known_log rows per crashed job) for exactly the 33 M-2 jobs;
                      attempt-2/ PJ jobs for those 33 jobs; PLANTED: a resumed job, and one
                      non-cell known_log row written by an attempt-2 job.
  F1d r11dup/         as F1, PLANTED duplicate key inside one attempt-2 job   -> merge must stop
  F1r r11resume/      as F1, one extra crashed job (b26-c0)                   -> resume-set assertion fails
  F1o r11outside/     as F1, attempt-2 also ran a job outside the resume set  -> merge must stop
  F2  r12like/        PJ from the start: attempt-1 with 55 jobs; PLANTED missing key (one row
                      dropped from b20-c3), an abnormal job end (b18-c1: no rows, exit -9) and
                      an M-4 per-arm attempt-2 (b18-c1:subgroup, b30-c2:dickson) whose
                      b30-c2 dickson rows equal attempt-1 rows up to excluded keys
  F2n r12nondet/      as F2, but the b30-c2:dickson re-run differs in a non-excluded key -> stop
  F3  j0like/         j0 panel PJ attempt-1 with rho rows (U = 280 + 35)
  F3c j0cert/         as F3, PLANTED one rho row with a k that fails verification -> merge writes the
                      canonical files but refuses the manifest (certificate failure, status invalid)
  C1  compare/        IE-1 style: attempt-1 records of (main, 4, 26, 0) vs a check job equal up to
                      `seconds`, `*_seconds`, worker_maxrss_bytes, ru_maxrss_bytes (-> pass)
  C2  compare-diff/   the same with one non-excluded key changed in one staircase record (-> fail)
  V   viewroot/       two run dirs, one with merged/ (M-6 link targets)
"""
import gzip
import json
import os
import random
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "fixtures")
MAIN_ARMS = ("subgroup", "dickson", "small_x", "random_sub_r0", "random_sub_r1",
             "random_sub_r2", "random_dick_r0", "random_dick_r1", "random_dick_r2")
ALL_MAIN = MAIN_ARMS + ("known_log",)
J0_ARMS = ("j0_coset", "j0_random_r0", "j0_random_r1", "j0_random_r2")
BITS = list(range(12, 33, 2))
RESUME = [(b, c) for b in (12, 14, 16, 18, 20, 22) for c in range(5)] + [(24, c) for c in (1, 3, 4)]
rng = random.Random(89123)


def wgz(path, recs):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with gzip.GzipFile(path, "wb", mtime=0) as fh:
        for r in recs:
            fh.write((json.dumps(r) + "\n").encode())


def solver_row(panel, m, b, c, arm, mode, status="completed_valid", reason=None):
    return {"bits": b, "curve": c, "p": rng.randrange(2 ** 20), "method": f"ic_m{m}", "panel": panel,
            "arm": arm, "mode": mode, "seconds": rng.random(), "filler": rng.randrange(10 ** 9),
            "nested": {"harvest_seconds": rng.random(), "worker_maxrss_bytes": rng.randrange(10 ** 9),
                       "count": rng.randrange(100)},
            "status": status, "status_reason": reason}


def crash_rows(m, b, c):
    return [{"bits": b, "curve": c, "m": m, "panel": "main", "arm": arm, "mode": mode, "ok": False,
             "status": "failed_infrastructure",
             "status_reason": "job crashed: BrokenProcessPool: synthetic"} for arm in ALL_MAIN
            for mode in ("census", "on")]


def side(m, b, c, arm, mode):
    k = {"bits": b, "curve": c, "m": m, "arm": arm, "mode": mode}
    st = [k | {"class": cl, "stair": [rng.randrange(50) for _ in range(3)]} for cl in ("TT", "TB", "SS")]
    hv = [k | {"class": "SS", "coeffs": {str(rng.randrange(40)): 1}} for _ in range(2)]
    return st, hv


def pj_job(ad, run_id, b, c, rows, stairs, hrows, arm=None, exit_code=0, write=True, m=4, panel="main"):
    name = f"b{b:02d}-c{c}" + (f"-{arm}" if arm else "")
    jd = os.path.join(ad, "jobs", name)
    os.makedirs(jd, exist_ok=True)
    if write:
        wgz(os.path.join(jd, "rows.jsonl.gz"), rows)
        wgz(os.path.join(jd, "staircase.jsonl.gz"), stairs)
        wgz(os.path.join(jd, "harvest-rows.jsonl.gz"), hrows)
    return {"job": name, "bits": b, "curve": c, "arm": arm, "panel": panel, "m": m,
            "job_dir": os.path.relpath(jd, "/home/user/crypto-autoresearcher"),
            "exit_code": exit_code, "signal": -exit_code if exit_code < 0 else None,
            "watchdog_expired": False, "wall_seconds": 1.0, "peak_rss_bytes": 1000, "cpu_seconds": 1.0}


def write_index(ad, run_id, jobs, panel="main", m=4, rho_curves=None):
    with open(os.path.join(ad, "jobs-index.json"), "w") as fh:
        json.dump({"run_id": run_id, "panel": panel, "m": m, "rho_curves": rho_curves, "wall_seconds": 10.0,
                   "run_stop_at_job": None, "not_started": [], "jobs": jobs}, fh, indent=1)


def full_job(m, b, c, arms=MAIN_ARMS, panel="main"):
    rows, st, hv = [], [], []
    for arm in arms:
        for mode in ("census", "on"):
            rows.append(solver_row(panel, m, b, c, arm, mode))
            s1, h1 = side(m, b, c, arm, mode)
            st += s1
            hv += h1
    return rows, st, hv


def r11like(name, extra_crash=None, dup=False, outside=False):
    root = os.path.join(OUT, name, "runs", "RUN-PFDR-1b78f7-census-m4")
    rows, st, hv = [], [], []
    crashed = set(RESUME) | ({extra_crash} if extra_crash else set())
    for b in sorted(BITS, reverse=True):
        for c in range(5):
            if (b, c) in crashed:
                rows += crash_rows(4, b, c)
            else:
                r1, s1, h1 = full_job(4, b, c)
                rows += r1
                st += s1
                hv += h1
    wgz(os.path.join(root, "rows.jsonl.gz"), rows)
    wgz(os.path.join(root, "staircase.jsonl.gz"), st)
    wgz(os.path.join(root, "harvest-rows.jsonl.gz"), hv)
    with open(os.path.join(root, "execution.json"), "w") as fh:
        json.dump({"peak_rss_bytes_max_descendant": 3000, "cpu_seconds_descendants": 100.0, "wall_seconds": 50.0,
                   "watchdog_expired": False, "exit_code": 0}, fh)
    ad = os.path.join(root, "attempt-2")
    jobs = []
    todo = list(RESUME) + ([(26, 0)] if outside else [])
    for b, c in todo:
        r1, s1, h1 = full_job(4, b, c)
        if (b, c) == (20, 2):
            r1.append({"bits": b, "curve": c, "m": 4, "panel": "main", "arm": "known_log", "mode": "census",
                       "status": "failed_infrastructure", "status_reason": "job crashed: planted non-cell row"})
        if dup and (b, c) == (16, 3):
            r1.append(dict(r1[0]))
        jobs.append(pj_job(ad, "RUN-PFDR-1b78f7-census-m4", b, c, r1, s1, h1))
    write_index(ad, "RUN-PFDR-1b78f7-census-m4", jobs)


def r12like(name, nondet=False):
    root = os.path.join(OUT, name, "runs", "RUN-PFDR-1b78f7-census-m5")
    ad1 = os.path.join(root, "attempt-1")
    jobs = []
    keep = {}
    for b in sorted(BITS, reverse=True):
        for c in range(5):
            r1, s1, h1 = full_job(5, b, c)
            if (b, c) == (20, 3):
                r1 = [r for r in r1 if not (r["arm"] == "small_x" and r["mode"] == "on")]
            if (b, c) == (18, 1):
                jobs.append(pj_job(ad1, "R12", b, c, [], [], [], exit_code=-9, write=False, m=5))
                continue
            keep[(b, c)] = r1
            jobs.append(pj_job(ad1, "R12", b, c, r1, s1, h1, m=5))
    write_index(ad1, "RUN-PFDR-1b78f7-census-m5", jobs, m=5)
    ad2 = os.path.join(root, "attempt-2")
    jobs2 = []
    r1, s1, h1 = full_job(5, 18, 1, arms=("subgroup",))
    jobs2.append(pj_job(ad2, "R12", 18, 1, r1, s1, h1, arm="subgroup", m=5))
    old = [dict(r) for r in keep[(30, 2)] if r["arm"] == "dickson"]
    for r in old:
        r["seconds"] = rng.random()
        r["nested"] = dict(r["nested"], harvest_seconds=rng.random(), worker_maxrss_bytes=rng.randrange(10 ** 9))
    if nondet:
        old[1]["filler"] += 1
    s1, h1 = [], []
    for r in old:
        s, h = side(5, 30, 2, "dickson", r["mode"])
        s1 += s
        h1 += h
    jobs2.append(pj_job(ad2, "R12", 30, 2, old, s1, h1, arm="dickson", m=5))
    write_index(ad2, "RUN-PFDR-1b78f7-census-m5", jobs2, m=5)


def j0like(name="j0like", bad_rho=False):
    root = os.path.join(OUT, name, "runs", "RUN-PFDR-1b78f7-j0")
    ad1 = os.path.join(root, "attempt-1")
    jobs = []
    for b in range(24, 11, -2):
        for c in range(5):
            r1, s1, h1 = full_job(3, b, c, arms=J0_ARMS, panel="j0")
            bad = bad_rho and (b, c) == (16, 2)
            r1.append({"bits": b, "curve": c, "method": "rho", "fb": "-", "panel": "j0", "seconds": rng.random(),
                       "ok": not bad, "status": "invalid" if bad else "completed_valid",
                       "status_reason": "rho k not verified (planted)" if bad else None})
            jobs.append(pj_job(ad1, "R14", b, c, r1, s1, h1, m=3, panel="j0"))
    write_index(ad1, "RUN-PFDR-1b78f7-j0", jobs, panel="j0", m=3, rho_curves=5)


def compare(name, diff=False):
    base = os.path.join(OUT, name)
    a_rows, a_st, a_hv = [], [], []
    b_rows, b_st, b_hv = [], [], []
    for (b, c) in [(28, 1), (26, 0), (26, 1)]:
        r1, s1, h1 = full_job(4, b, c)
        a_rows += r1
        a_st += s1
        a_hv += h1
        if (b, c) == (26, 0):
            for r in r1:
                r2 = json.loads(json.dumps(r))
                r2["seconds"] = rng.random()
                r2["nested"]["harvest_seconds"] = rng.random()
                r2["nested"]["worker_maxrss_bytes"] = rng.randrange(10 ** 9)
                r2["ru_maxrss_bytes"] = 1
                b_rows.append(r2)
            b_st = json.loads(json.dumps(s1))
            b_hv = json.loads(json.dumps(h1))
            if diff:
                b_st[4]["stair"] = b_st[4]["stair"] + [0]
    wgz(os.path.join(base, "attempt1", "rows.jsonl.gz"), a_rows)
    wgz(os.path.join(base, "attempt1", "staircase.jsonl.gz"), a_st)
    wgz(os.path.join(base, "attempt1", "harvest-rows.jsonl.gz"), a_hv)
    wgz(os.path.join(base, "check", "b26-c0", "rows.jsonl.gz"), b_rows)
    wgz(os.path.join(base, "check", "b26-c0", "staircase.jsonl.gz"), b_st)
    wgz(os.path.join(base, "check", "b26-c0", "harvest-rows.jsonl.gz"), b_hv)


def viewroot():
    base = os.path.join(OUT, "viewroot", "runs")
    for n in ("RUN-PFDR-1b78f7-census-m4", "RUN-PFDR-1b78f7-census-m3"):
        os.makedirs(os.path.join(base, n), exist_ok=True)
        with open(os.path.join(base, n, "rows.jsonl"), "w") as fh:
            fh.write("{}\n")
    os.makedirs(os.path.join(base, "RUN-PFDR-1b78f7-census-m4", "merged"))
    with open(os.path.join(base, "RUN-PFDR-1b78f7-census-m4", "merged", "rows.jsonl"), "w") as fh:
        fh.write('{"merged": true}\n')
    os.makedirs(os.path.join(base, "NOT-A-RUN"))


if __name__ == "__main__":
    if os.path.exists(OUT):
        sys.exit(f"refusing: {OUT} exists")
    r11like("r11like")
    r11like("r11dup", dup=True)
    r11like("r11resume", extra_crash=(26, 0))
    r11like("r11outside", outside=True)
    r12like("r12like")
    r12like("r12nondet", nondet=True)
    j0like()
    j0like("j0cert", bad_rho=True)
    compare("compare")
    compare("compare-diff", diff=True)
    viewroot()
    print("fixtures written to", OUT)
