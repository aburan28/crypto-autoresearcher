"""J2a (Q1): M-5 canonical row sets of R11, R12, R14 and R16, built blind from the
attempt files, jobs-index.json and AMD-20260929-430f44 M-5's text alone (never
merge_census.py). Conventions: rederivation/conventions.yaml CV-16.

Usage: python j2a_canonical.py   (writes rederivation/out/j2a-*.json and
canonical-*.jsonl.gz; prints a summary with digests and counts)."""
import collections, glob, gzip, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (RUNS, RUN, MAIN_BITS, J0_BITS, MAIN_ARMS, J0_ARMS, MODES, RAND,
                    read_jsonl_gz, read_json, key_of, sort_key, stair_key, row_m,
                    canon_bytes, sha256_bytes, dump, OUT, is_rho)


class Stop(Exception):
    pass


def jobs_of(attempt_dir):
    return sorted(glob.glob(os.path.join(attempt_dir, "jobs", "*")))


def load_attempt_jobs(run_dir, attempt):
    """Return {jobname: (rows, stairs)} for <run>/<attempt>/jobs/*."""
    out = {}
    for jd in jobs_of(os.path.join(run_dir, attempt)):
        name = os.path.basename(jd)
        rows = read_jsonl_gz(os.path.join(jd, "rows.jsonl.gz"), "J2a input: job rows")
        stairs = read_jsonl_gz(os.path.join(jd, "staircase.jsonl.gz"), "J2a input: job staircase")
        out[name] = (rows, stairs)
    return out


def index_unique(rows, where):
    idx = {}
    for r in rows:
        k = key_of(r)
        if k in idx:
            raise Stop(f"rule (4): duplicate key {k} within {where}")
        idx[k] = r
    return idx


def stairs_by_key(stairs):
    d = collections.defaultdict(list)
    for s in stairs:
        d[(s["bits"], s["curve"], s["m"], s.get("arm"), s.get("mode"))].append(s)
    return d


def build(run_label, U, sources, exit_status_of_job, job_of_key):
    """sources: list of (source_name, rows, stairs) in precedence order low->high;
    for each key the LAST source that holds it wins (rule (1)).
    Returns canonical rows, canonical stairs, report."""
    per_source = []
    for name, rows, stairs in sources:
        per_source.append((name, index_unique(rows, name), stairs_by_key(stairs), rows))
    canon, cstairs, src_of = [], [], {}
    placeholders, noncell = [], []
    for k in sorted(U, key=lambda k: tuple(str(x) for x in k)):
        chosen = None
        for name, idx, sidx, _ in per_source:
            if k in idx:
                chosen = (name, idx[k], sidx)
        if chosen is None:
            panel, m, bits, curve, arm, mode = k if len(k) == 6 else (k[0], k[1], k[2], k[3], "", "")
            ph = {"panel": panel, "m": m, "bits": bits, "curve": curve, "arm": arm, "mode": mode,
                  "status": "failed_infrastructure",
                  "status_reason": f"no row: {exit_status_of_job(job_of_key(k))}",
                  "placeholder": True}
            canon.append(ph)
            placeholders.append(list(k))
            src_of[k] = "placeholder"
            continue
        name, row, sidx = chosen
        canon.append(row)
        src_of[k] = name
        if not is_rho(row):
            skey = (row["bits"], row["curve"], row_m(row), row.get("arm"), row.get("mode"))
            cstairs.extend(sidx.get(skey, []))
    for name, idx, sidx, rows in per_source:
        for r in rows:
            k = key_of(r)
            if k not in U:
                noncell.append({"source": name, "key": list(k), "status": r.get("status"),
                                "status_reason": r.get("status_reason")})
    canon.sort(key=sort_key)
    cstairs.sort(key=stair_key)
    rb, sb = canon_bytes(canon), canon_bytes(cstairs)
    counts_status = collections.Counter(r.get("status") for r in canon)
    counts_src = collections.Counter(src_of.values())
    rep = {
        "run": run_label, "U_size": len(U), "canonical_rows": len(canon),
        "canonical_rows_sha256_normal_form": sha256_bytes(rb),
        "canonical_staircase_records": len(cstairs),
        "canonical_staircase_sha256_normal_form": sha256_bytes(sb),
        "counts_by_status": dict(counts_status),
        "counts_by_source": dict(counts_src),
        "placeholders": placeholders,
        "noncell_rows_excluded": len(noncell),
        "noncell_rows": noncell,
    }
    with gzip.GzipFile(os.path.join(OUT, f"canonical-{run_label}-rows.jsonl.gz"), "wb", mtime=0) as f:
        f.write(rb)
    with gzip.GzipFile(os.path.join(OUT, f"canonical-{run_label}-staircase.jsonl.gz"), "wb", mtime=0) as f:
        f.write(sb)
    return canon, cstairs, rep


def main_U(m):
    return {("main", m, b, c, a, mo) for b in MAIN_BITS for c in range(5) for a in MAIN_ARMS for mo in MODES}


def exit_fn(jobs_index):
    by = {}
    for j in jobs_index["jobs"]:
        by[j["job"]] = j
    def f(job):
        j = by.get(job)
        if j is None:
            return "job not in jobs-index.json"
        return f"exit_code {j.get('exit_code')} signal {j.get('signal')} watchdog_expired {j.get('watchdog_expired')}"
    return f


def run_R11():
    rd = os.path.join(RUNS, RUN["R11"])
    a1_rows = read_jsonl_gz(os.path.join(rd, "rows.jsonl.gz"), "J2a input: R11 attempt-1 root rows")
    a1_stairs = read_jsonl_gz(os.path.join(rd, "staircase.jsonl.gz"), "J2a input: R11 attempt-1 root staircase")
    ji = read_json(os.path.join(rd, "attempt-2", "jobs-index.json"), "J2a input: R11 attempt-2 jobs-index")
    a2 = load_attempt_jobs(rd, "attempt-2")
    # resume set
    by_job = collections.defaultdict(list)
    for r in a1_rows:
        by_job[(r["bits"], r["curve"])].append(r)
    resume = sorted(j for j, rs in by_job.items()
                    if all((r.get("status_reason") or "").startswith("job crashed:") for r in rs))
    expected = sorted([(b, c) for b in [12, 14, 16, 18, 20, 22] for c in range(5)] + [(24, 1), (24, 3), (24, 4)])
    a2_jobs = sorted((int(n.split("-")[0][1:]), int(n.split("-")[1][1:])) for n in a2)
    notes = {"resume_set": [list(x) for x in resume], "resume_set_size": len(resume),
             "resume_set_equals_M2_assertion": resume == expected,
             "attempt2_job_dirs_equal_resume_set": a2_jobs == resume,
             "attempt1_rows": len(a1_rows),
             "attempt1_status": {f"{k[0]}|{k[1]}": v for k, v in collections.Counter((r.get("status"), (r.get("status_reason") or "")[:12]) for r in a1_rows).items()},
             "jobs_index_jobs": len(ji["jobs"])}
    if a2_jobs != resume:
        raise Stop("rule (1): attempt-2 job set differs from the resume set")
    a2_rows, a2_stairs = [], []
    # each attempt-2 job's rows must be of its own job; check key coverage per job
    for name, (rows, stairs) in sorted(a2.items()):
        b, c = int(name.split("-")[0][1:]), int(name.split("-")[1][1:])
        for r in rows:
            if (r["bits"], r["curve"]) != (b, c):
                raise Stop(f"row of another job in {name}")
        a2_rows.extend(rows)
        a2_stairs.extend(stairs)
    # rule (1) for R11: attempt-1 row unless the key's job is in the resume set.
    rs = set(resume)
    a1_keep = [r for r in a1_rows if (r["bits"], r["curve"]) not in rs]
    a1_super = [r for r in a1_rows if (r["bits"], r["curve"]) in rs]
    U = main_U(4)
    job_of_key = lambda k: f"b{k[2]}-c{k[3]}"
    # sources: attempt-1 rows of non-resume jobs, then attempt-2 rows. Superseded attempt-1
    # rows of resume jobs are not candidates for any key (rule (1)); they are counted below.
    canon, cst, rep = build("R11", U, [("attempt-1", a1_keep, a1_stairs), ("attempt-2", a2_rows, a2_stairs)],
                            exit_fn(ji), job_of_key)
    # non-cell rows among the superseded attempt-1 rows (the 66 known_log rows of M-9)
    nc_super = [{"source": "attempt-1 (resume job)", "key": list(key_of(r)), "status": r.get("status"),
                 "status_reason": (r.get("status_reason") or "")[:80]} for r in a1_super if key_of(r) not in U]
    rep["noncell_rows"].extend(nc_super)
    rep["noncell_rows_excluded"] = len(rep["noncell_rows"])
    rep["superseded_attempt1_cell_rows"] = sum(1 for r in a1_super if key_of(r) in U)
    rep["noncell_by_arm_m"] = dict(collections.Counter(f"{x['key'][4]}|m{x['key'][1]}" for x in rep["noncell_rows"]))
    # attempt-2 keys outside the resume set would be a stop: already guaranteed by job check.
    rep.update(notes)
    return canon, cst, rep


def run_simple(label, attempt, U, cell_check=None):
    rd = os.path.join(RUNS, RUN[label])
    ji = read_json(os.path.join(rd, attempt, "jobs-index.json"), f"J2a input: {label} {attempt} jobs-index")
    jobs = load_attempt_jobs(rd, attempt)
    rows, stairs = [], []
    for name, (rs, ss) in sorted(jobs.items()):
        rows.extend(rs)
        stairs.extend(ss)
    def job_of_key(k):
        if label == "R16":
            return f"m{k[1]}-b{k[2]}-c{k[3]}"
        return f"b{k[2]}-c{k[3]}"
    canon, cst, rep = build(label, U, [(attempt, rows, stairs)], exit_fn(ji), job_of_key)
    rep["jobs_read"] = len(jobs)
    rep["jobs_index_jobs"] = len(ji["jobs"])
    return canon, cst, rep, ji


def main():
    reports = {}
    try:
        c11, s11, r11 = run_R11()
        reports["R11"] = r11
        c12, s12, r12, _ = run_simple("R12", "attempt-1", main_U(5))
        reports["R12"] = r12
        U14 = {("j0", 3, b, c, a, mo) for b in J0_BITS for c in range(5) for a in J0_ARMS for mo in MODES}
        U14 |= {("j0", "rho", b, c) for b in J0_BITS for c in range(5)}
        c14, s14, r14, _ = run_simple("R14", "attempt-1", U14)
        reports["R14"] = r14
        # R16: U from the jobs-index arm lists; each job's arms must be [A] + R(A)
        rd = os.path.join(RUNS, RUN["R16"])
        ji = read_json(os.path.join(rd, "attempt-1", "jobs-index.json"), "J2a input: R16 attempt-1 jobs-index (U)")
        cells = collections.defaultdict(set)
        arm_ok = True
        for j in ji["jobs"]:
            A = j["arms"][0]
            if j["arms"] != [A] + RAND.get(A, []):
                arm_ok = False
            cells[(j["m"], j["bits"], A)].add(j["curve"])
        U16 = set()
        for (m, b, A), curves in cells.items():
            for c in range(5, 10):
                for a in [A] + RAND[A]:
                    for mo in MODES:
                        U16.add(("main", m, b, c, a, mo))
        c16, s16, r16, _ = run_simple("R16", "attempt-1", U16)
        r16["excursion_cells_from_layout"] = sorted([list(k) + [sorted(v)] for k, v in cells.items()])
        r16["job_arm_lists_are_A_plus_R(A)"] = arm_ok
        reports["R16"] = r16
    except Stop as e:
        reports["STOP"] = str(e)
    dump("j2a-report.json", reports)
    for k, v in reports.items():
        if k == "STOP":
            print("STOP", v)
            continue
        print(k, {x: v[x] for x in v if x not in ("noncell_rows", "placeholders")})
        print("   placeholders:", len(v["placeholders"]))


if __name__ == "__main__":
    main()
