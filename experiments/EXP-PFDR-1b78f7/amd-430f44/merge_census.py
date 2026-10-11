"""Canonical row sets, invocation-equivalence comparison and the R15 view for
EXP-PFDR-1b78f7 under protocol v3 (AMD-20260929-430f44 M-3, M-2, M-5, M-6, M-7).

TASK-20260929-89c123.  New harness code; imports NO crypto_autoresearcher module.
It reads census rows for KEYS, STATUS, STATUS_REASON and RECORD IDENTITY only.  It
computes no kappa, rank, ratio, exponent, Poisson or floor value, and prints no
measured value.  (`compare` and M-5 rule (5) test two records for equality after the
M-3 key exclusions and report only key NAMES and record COUNTS; `summarize` reads the
gate and certificate fields through the pinned summarize_run.py gate_checks().)

Subcommands
  compare     M-3 IE-1 / IE-2: attempt-1 records of one job vs a PJ check job, rows,
              staircases and harvest rows, record by record in emission order.
  resume-set  M-2: compute R11's resume set from the archived root rows and assert it.
  merge       M-5: write the canonical rows / staircases / execution.json /
              merge-report.json (+ raw-result.json by summarize_run.py, manifest.yaml,
              checksums.sha256) of one run at <run>/merged/ or the run root.
  view        M-6: build the view directory of symbolic links and view-map.json.
  summarize   attempt-level raw-result.json (statuses, completeness, gate and certificate
              counts) for run_jobs.py.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from collections import Counter, defaultdict

REPO = "/home/user/crypto-autoresearcher"
EXPDIR = "experiments/EXP-PFDR-1b78f7"
HERE = os.path.dirname(os.path.abspath(__file__))
PY = "/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/venv-ci/bin/python"
SUMMARIZE = f"{EXPDIR}/amd-1de84f/summarize_run.py"

MAIN_ARMS = ("subgroup", "dickson", "small_x", "random_sub_r0", "random_sub_r1",
             "random_sub_r2", "random_dick_r0", "random_dick_r1", "random_dick_r2")
J0_ARMS = ("j0_coset", "j0_random_r0", "j0_random_r1", "j0_random_r2")
MODES = ("census", "on")
R11_RESUME_SET = sorted([(b, c) for b in (12, 14, 16, 18, 20, 22) for c in range(5)]
                        + [(24, c) for c in (1, 3, 4)])
EXCLUDED_KEY_RULE = "keys named `seconds`, keys ending in `_seconds`, `worker_maxrss_bytes`, `ru_maxrss_bytes`, at any depth"


class Stop(Exception):
    """A harness stop (M-5 (4), (5), M-2 assertion, an unforeseen shape)."""


# ------------------------------------------------------------------------------------------
# identity

def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def open_text(path: str):
    if not os.path.exists(path) and os.path.exists(path + ".gz"):
        path += ".gz"
    return (gzip.open if path.endswith(".gz") else open)(path, "rt")


def iter_lines(path: str):
    """(raw line without newline, parsed record) in file order."""
    with open_text(path) as fh:
        for line in fh:
            s = line.rstrip("\n")
            if s.strip():
                yield s, json.loads(s)


def row_m(r: dict):
    if r.get("m") is not None:
        return r["m"]
    meth = str(r.get("method", ""))
    return int(meth[4:]) if meth.startswith("ic_m") else None


def row_key(r: dict) -> tuple:
    """M-5 cell-instance key: (panel, m, bits, curve, arm, mode); rho: (panel, 'rho', bits, curve)."""
    if r.get("method") == "rho" or r.get("panel") == "rho":
        return (r.get("panel"), "rho", r.get("bits"), r.get("curve"))
    return (r.get("panel"), row_m(r), r.get("bits"), r.get("curve"), r.get("arm"), r.get("mode"))


def stair_key(s: dict, panel: str) -> tuple:
    """Staircase / harvest records carry {bits, curve, m, arm, mode} (no panel)."""
    return (panel, s.get("m"), s.get("bits"), s.get("curve"), s.get("arm"), s.get("mode"))


def sort_key(k: tuple) -> tuple:
    """M-5 (7): (bits, curve, m, arm, mode); rho rows sort with arm '' (and m 0, mode '' as the
    frozen __main__._census_sort_key does for non-ic rows; any m <= 3 gives the same order)."""
    if k[1] == "rho":
        return (k[2], k[3], 0, "", "")
    return (k[2], k[3], k[1] if k[1] is not None else 0, k[4] or "", k[5] or "")


def strip_excluded(x):
    if isinstance(x, dict):
        return {k: strip_excluded(v) for k, v in x.items()
                if not (k == "seconds" or k.endswith("_seconds") or k in ("worker_maxrss_bytes", "ru_maxrss_bytes"))}
    if isinstance(x, list):
        return [strip_excluded(v) for v in x]
    return x


def diff_paths(a, b, path="") -> set:
    """Key paths (names only, no values) at which two stripped records differ."""
    if isinstance(a, dict) and isinstance(b, dict):
        out = set()
        for k in set(a) | set(b):
            p = f"{path}.{k}" if path else k
            if k not in a or k not in b:
                out.add(p + (" (only in attempt-1)" if k in a else " (only in check)"))
            else:
                out |= diff_paths(a[k], b[k], p)
        return out
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return {f"{path}[] (length)"}
        out = set()
        for i, (u, v) in enumerate(zip(a, b)):
            out |= diff_paths(u, v, f"{path}[]")
        return out
    return set() if a == b else {path or "<record>"}


# ------------------------------------------------------------------------------------------
# U (cell universe)

def universe(panel: str, m: int | None, bits: list, curves: list, rho_curves: int | None,
             arms: list | None = None) -> set:
    U = set()
    if panel == "main":
        for b in bits:
            for c in curves:
                for arm in (arms or MAIN_ARMS):
                    for md in MODES:
                        U.add(("main", m, b, c, arm, md))
    elif panel == "j0":
        for b in bits:
            for c in curves:
                for arm in (arms or J0_ARMS):
                    for md in MODES:
                        U.add(("j0", 3, b, c, arm, md))
                if c < (rho_curves or 0):
                    U.add(("j0", "rho", b, c))
    else:
        for b in bits:
            for c in curves:
                U.add(("rho", "rho", b, c))
    return U


def universe_cells(cells: list) -> set:
    """R16: U = union of excursion cells, each 'm:bits:arm1+arm2+...:c1+c2+...' (main panel)."""
    U = set()
    for spec in cells:
        m, b, arms, cs = spec.split(":")
        for c in cs.split("+"):
            for arm in arms.split("+"):
                for md in MODES:
                    U.add(("main", int(m), int(b), int(c), arm, md))
    return U


# ------------------------------------------------------------------------------------------
# compare (M-3)

def cmd_compare(a) -> int:
    b0, c0, m0 = a.bits, a.curve, a.m
    pairs = {"rows": (a.a_rows, os.path.join(a.b_dir, "rows.jsonl.gz")),
             "staircase": (a.a_stairs, os.path.join(a.b_dir, "staircase.jsonl.gz")),
             "harvest_rows": (a.a_harvest, os.path.join(a.b_dir, "harvest-rows.jsonl.gz"))}
    arm_filter = set(a.arms) if a.arms else None

    def sel(r):
        return (r.get("bits") == b0 and r.get("curve") == c0 and row_m(r) == m0
                and r.get("panel", a.panel) == a.panel
                and (arm_filter is None or r.get("arm") in arm_filter))

    report = {"what": "AMD-20260929-430f44 M-3 invocation-equivalence comparison",
              "check": a.check_id, "key": [a.panel, m0, b0, c0, "*", "*"],
              "arms": sorted(arm_filter) if arm_filter else "all",
              "excluded_keys": EXCLUDED_KEY_RULE, "sets": {}}
    ok_all = True
    for name, (fa, fb) in pairs.items():
        if fb is None or not os.path.exists(fb):
            report["sets"][name] = {"equal": False, "error": f"missing check file {fb}"}
            ok_all = False
            continue
        A = (r for _, r in iter_lines(fa) if sel(r))
        B_all = [r for _, r in iter_lines(fb)]
        B = [r for r in B_all if sel(r)]
        foreign_b = len(B_all) - len(B)
        n_a = n_b = 0
        ndiff = 0
        paths = Counter()
        bi = iter(B)
        while True:
            ra = next(A, None)
            rb = next(bi, None)
            if ra is None and rb is None:
                break
            if ra is not None:
                n_a += 1
            if rb is not None:
                n_b += 1
            if ra is None or rb is None:
                ndiff += 1
                paths["<record present in only one set>"] += 1
                continue
            sa, sb = strip_excluded(ra), strip_excluded(rb)
            if sa != sb:
                ndiff += 1
                for p in diff_paths(sa, sb):
                    paths[p] += 1
        eq = ndiff == 0 and n_a == n_b
        ok_all &= eq and (foreign_b == 0 or arm_filter is not None)
        report["sets"][name] = {"attempt1_file": os.path.relpath(fa, REPO), "attempt1_file_sha256": sha256(fa),
                                "check_file": os.path.relpath(fb, REPO), "check_file_sha256": sha256(fb),
                                "attempt1_records": n_a, "check_records": n_b,
                                "check_records_outside_key": foreign_b,
                                "records_differing": ndiff, "equal": eq,
                                "differing_key_names_with_record_counts": dict(sorted(paths.items()))}
    report["pass"] = bool(ok_all)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    if os.path.exists(a.out):
        raise SystemExit(f"refusing: {a.out} exists")
    with open(a.out, "w") as fh:
        json.dump(report, fh, indent=2, sort_keys=True)
    print(json.dumps({"pass": report["pass"],
                      "sets": {k: {kk: v.get(kk) for kk in ("attempt1_records", "check_records", "records_differing",
                                                            "equal", "differing_key_names_with_record_counts")}
                               for k, v in report["sets"].items()}}, indent=2))
    return 0 if report["pass"] else 1


# ------------------------------------------------------------------------------------------
# resume set (M-2)

def resume_set_from_root(rows_path: str, m: int) -> tuple[list, dict]:
    by_job = defaultdict(list)
    for _, r in iter_lines(rows_path):
        if r.get("panel") == "main" and row_m(r) == m:
            by_job[(r["bits"], r["curve"])].append(str(r.get("status_reason") or ""))
    rs = sorted(j for j, reasons in by_job.items() if reasons and all(x.startswith("job crashed:") for x in reasons))
    info = {"jobs_seen": len(by_job), "rows_per_resumed_job": {f"b{b}-c{c}": len(by_job[(b, c)]) for b, c in rs}}
    return rs, info


def cmd_resume_set(a) -> int:
    rs, info = resume_set_from_root(a.rows, a.m)
    exp = R11_RESUME_SET
    res = {"what": "AMD-20260929-430f44 M-2 R11 resume set (jobs whose every attempt-1 row has a status_reason "
                   "beginning 'job crashed:')",
           "rows_file": os.path.relpath(os.path.abspath(a.rows), REPO), "rows_file_sha256": sha256(a.rows),
           "computed": [f"b{b}-c{c}" for b, c in rs], "computed_count": len(rs),
           "asserted": [f"b{b}-c{c}" for b, c in exp], "asserted_count": len(exp),
           "equal": rs == exp, "cell_instances": 18 * len(rs)} | info
    if a.out:
        if os.path.exists(a.out):
            raise SystemExit(f"refusing: {a.out} exists")
        with open(a.out, "w") as fh:
            json.dump(res, fh, indent=2)
    print(json.dumps({k: res[k] for k in ("computed_count", "asserted_count", "equal", "cell_instances")}))
    return 0 if res["equal"] else 1


# ------------------------------------------------------------------------------------------
# merge (M-5, M-7)

def load_receipt_hashes(paths: list) -> dict:
    out = {}
    for p in paths:
        r = json.load(open(os.path.join(REPO, p)))
        for k, v in (r.get("path_sha256") or {}).items():
            out[k] = (v, p)
    return out


def attempt_sources(run_dir: str, attempts: list, root_attempt1: bool, panel: str, m):
    """Ordered list of attempts; each {name, jobs: {(bits, curve, arm|None): jobsrc}}."""
    out = []
    if root_attempt1:
        out.append({"name": "attempt-1 (run root, as archived)", "kind": "root",
                    "rows": os.path.join(run_dir, "rows.jsonl.gz"),
                    "staircase": os.path.join(run_dir, "staircase.jsonl.gz"),
                    "harvest": os.path.join(run_dir, "harvest-rows.jsonl.gz"),
                    "execution": os.path.join(run_dir, "execution.json")})
    for name in attempts:
        ad = os.path.join(run_dir, name)
        idx = json.load(open(os.path.join(ad, "jobs-index.json")))
        jobs = {}
        for j in idx["jobs"]:
            jd = os.path.join(REPO, j["job_dir"])
            jobs[(j.get("m"), j["bits"], j["curve"], j["arm"])] = {
                "dir": jd, "rows": os.path.join(jd, "rows.jsonl.gz"),
                "staircase": os.path.join(jd, "staircase.jsonl.gz"),
                "harvest": os.path.join(jd, "harvest-rows.jsonl.gz"),
                "exit": {k: j.get(k) for k in ("exit_code", "signal", "watchdog_expired", "wall_seconds")},
                "rec": j}
        out.append({"name": name, "kind": "pj", "dir": ad, "index": idx, "jobs": jobs})
    return out


def cmd_merge(a) -> int:
    run_dir = os.path.join(REPO, a.run_dir)
    out = os.path.join(REPO, a.out)
    os.makedirs(out, exist_ok=True)
    for f in ("rows.jsonl.gz", "staircase.jsonl.gz", "execution.json", "merge-report.json", "manifest.yaml",
              "raw-result.json", "checksums.sha256", "command.txt", "environment.json"):
        if os.path.exists(os.path.join(out, f)):
            raise SystemExit(f"refusing: {out}/{f} exists (records are immutable)")
    stdout = open(os.path.join(out, "stdout.log"), "a")
    stderr = open(os.path.join(out, "stderr.log"), "a")

    def log(msg, err=False):
        print(msg, file=sys.stderr if err else sys.stdout, flush=True)
        (stderr if err else stdout).write(msg + "\n")
        (stderr if err else stdout).flush()

    with open(os.path.join(out, "command.txt"), "w") as fh:
        fh.write(" ".join([PY, os.path.relpath(os.path.abspath(__file__), REPO)] + sys.argv[1:]) + "\n")
        fh.write(f"# then: {PY} {SUMMARIZE} census --run-dir {a.out} --run-id {a.run_id} --panel {a.panel}"
                 + (f" --m {a.m}" if a.m else "") + (f" --rho-curves {a.rho_curves}" if a.panel == "j0" else "")
                 + "  (raw-result.json)\n")
        fh.write(f"# cwd: {REPO}\n")
    rj = load_module("run_jobs_430f44", os.path.join(HERE, "run_jobs.py"))
    with open(os.path.join(out, "environment.json"), "w") as fh:
        json.dump(rj.environment_json(), fh, indent=2, sort_keys=True)
    try:
        rc = _merge(a, run_dir, out, log, rj)
    except Stop as exc:
        log(f"STOP: {exc}", err=True)
        with open(os.path.join(out, "merge-stop.json"), "w") as fh:
            json.dump({"stop": str(exc)}, fh, indent=2)
        return 4
    return rc


def load_module(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _merge(a, run_dir, out, log, rj) -> int:
    panel, m = a.panel, (a.m if a.panel == "main" else (3 if a.panel == "j0" else None))
    bits = list(a.bits)
    curves = list(a.curves)
    U = universe_cells(a.cells) if a.cells else universe(panel, m, bits, curves, a.rho_curves, a.arms)
    log(f"U({a.run_id}) = {len(U)} keys")
    srcs = attempt_sources(run_dir, a.attempts, a.root_attempt1, panel, m)
    receipts = load_receipt_hashes(a.receipt or [])
    report = {"what": "AMD-20260929-430f44 M-5 canonical row set", "run_id": a.run_id,
              "canonical_location": os.path.relpath(out, REPO), "U_size": len(U),
              "U_definition": {"cells": a.cells} if a.cells else {"panel": panel, "m": m, "bits": bits, "curves": curves,
                               "arms": a.arms or (list(MAIN_ARMS) if panel == "main" else list(J0_ARMS) if panel == "j0" else None),
                               "modes": list(MODES) if panel != "rho" else None, "rho_curves": a.rho_curves},
              "attempts": [], "inputs": [], "resume_set": None}

    def input_rec(path):
        rel = os.path.relpath(path, REPO)
        d = sha256(path)
        rec = {"path": rel, "sha256": d}
        if rel in receipts:
            rec["receipt"] = receipts[rel][1]
            rec["receipt_sha256"] = receipts[rel][0]
            rec["matches_receipt"] = receipts[rel][0] == d
            if not rec["matches_receipt"]:
                raise Stop(f"archived input {rel} does not match its receipt hash")
        return rec

    # resume set (R11)
    resumed = None
    if a.assert_r11_resume_set:
        rs, info = resume_set_from_root(srcs[0]["rows"], m)
        if rs != R11_RESUME_SET:
            raise Stop(f"R11 resume set differs from M-2's assertion: computed {rs}")
        resumed = set(rs)
        report["resume_set"] = {"jobs": [f"b{b}-c{c}" for b, c in rs], "count": len(rs),
                                "cell_instances": 18 * len(rs), "asserted_equal_to_M2": True} | info
        log(f"R11 resume set asserted: {len(rs)} jobs")

    # read every attempt: key -> (raw line, status fields) per attempt; coverage
    per_attempt_rows = []     # list of dict key -> {line, status, status_reason, file, job}
    coverage = []             # list of set of (bits, curve, arm|None) the attempt ran
    noncell = []
    for i, s in enumerate(srcs):
        rows_k = {}
        cov = set()
        files = []
        if s["kind"] == "root":
            files.append((s["rows"], None))
            cov = {"ALL"}
            report["inputs"] += [input_rec(p) for p in (s["rows"], s["staircase"], s["harvest"], s["execution"])
                                 if os.path.exists(p)]
        else:
            for jk, j in sorted(s["jobs"].items(), key=lambda kv: (kv[0][1], kv[0][2], kv[0][0] or 0, kv[0][3] or "")):
                if resumed is not None and (jk[1], jk[2]) not in resumed:
                    raise Stop(f"{s['name']} ran job {jk} outside the R11 resume set")
                for x in (jk[3].split("+") if jk[3] else [None]):
                    cov.add((jk[0], jk[1], jk[2], x))
                if os.path.exists(j["rows"]):
                    files.append((j["rows"], jk))
                    report["inputs"].append(input_rec(j["rows"]))
                for p in (j["staircase"], j["harvest"]):
                    if os.path.exists(p):
                        report["inputs"].append(input_rec(p))
        for path, jk in files:
            for line, r in iter_lines(path):
                k = row_key(r)
                if k not in U:
                    noncell.append({"key": list(k), "status": r.get("status"),
                                    "status_reason": r.get("status_reason"), "attempt": s["name"],
                                    "file": os.path.relpath(path, REPO)})
                    continue
                if jk is not None:
                    # a PJ job's cell rows must belong to that job (m, bits, curve and arm list)
                    kb, kc = k[2], k[3]
                    karm = None if k[1] == "rho" else k[4]
                    if ((kb, kc) != (jk[1], jk[2]) or (jk[3] is not None and karm not in jk[3].split("+"))
                            or (k[1] != "rho" and jk[0] is not None and k[1] != jk[0])):
                        raise Stop(f"row {k} in {path} does not belong to job {jk}")
                if k in rows_k:
                    raise Stop(f"two rows for key {k} within {s['name']} (M-5 (4) harness defect)")
                rows_k[k] = {"line": line, "status": r.get("status"), "status_reason": r.get("status_reason"),
                             "file": path, "job": jk, "placeholder": bool(r.get("placeholder"))}
        per_attempt_rows.append(rows_k)
        coverage.append(cov)
        report["attempts"].append({"attempt": s["name"], "kind": s["kind"],
                                   "jobs_ran": ("all jobs of the frozen invocation" if s["kind"] == "root"
                                                else sorted({(f"m{mm}-" if mm is not None else "") + f"b{b}-c{c}"
                                                             + (f":{jk3}" if jk3 else "") for mm, b, c, jk3 in s["jobs"]})),
                                   "cell_rows": len(rows_k)})

    def covers(i, k):
        cov = coverage[i]
        if "ALL" in cov:
            return True
        if k[1] == "rho":
            return any(e[1] == k[2] and e[2] == k[3] and e[3] is None for e in cov)
        return (k[1], k[2], k[3], None) in cov or (k[1], k[2], k[3], k[4]) in cov

    def covering_job(i, k):
        for jk, j in srcs[i]["jobs"].items():
            if jk[1] == k[2] and jk[2] == k[3] and (k[1] == "rho" or jk[0] in (None, k[1])) and (
                    jk[3] is None or (k[1] != "rho" and k[4] in jk[3].split("+"))):
                return jk
        return None

    canonical = {}
    per_key = {}
    placeholders = []
    superseded = []
    determinism = []
    for k in sorted(U, key=sort_key):
        src_i = None
        for i in range(len(srcs) - 1, -1, -1):
            if covers(i, k):
                src_i = i
                break
        earlier_rows = [(i, per_attempt_rows[i][k]) for i in range(len(srcs))
                        if k in per_attempt_rows[i] and i != src_i]
        if src_i is not None and k in per_attempt_rows[src_i]:
            rec = per_attempt_rows[src_i][k]
            canonical[k] = rec
            per_key[k] = {"attempt": srcs[src_i]["name"], "file": os.path.relpath(rec["file"], REPO)}
            for i, er in earlier_rows:
                if i > src_i:
                    raise Stop(f"key {k}: row in {srcs[i]['name']} after the latest covering attempt")
                superseded.append({"key": list(k), "attempt": srcs[i]["name"], "status": er["status"],
                                   "status_reason": er["status_reason"],
                                   "superseded_by": srcs[src_i]["name"]})
                if er["status"] == "completed_valid":
                    sa = strip_excluded(json.loads(er["line"]))
                    sb = strip_excluded(json.loads(rec["line"]))
                    eq = sa == sb
                    determinism.append({"key": list(k), "earlier": srcs[i]["name"], "later": srcs[src_i]["name"],
                                        "equal_after_M3_exclusions": eq,
                                        "differing_key_names": sorted(diff_paths(sa, sb)) if not eq else []})
                    if not eq:
                        raise Stop(f"I-5 nondeterminism at {k} ({srcs[i]['name']} vs {srcs[src_i]['name']}); "
                                   "the run is invalid; both rows retained")
        else:
            if earlier_rows:
                raise Stop(f"key {k}: the latest attempt that ran it ({srcs[src_i]['name'] if src_i is not None else None}) "
                           "wrote no row, but an earlier attempt did; M-5 (1)/(2) do not rule this case")
            if src_i is not None and srcs[src_i]["kind"] == "pj":
                jk = covering_job(src_i, k)
                ex = srcs[src_i]["jobs"][jk]["exit"]
                why = (f"exit_code {ex.get('exit_code')}, signal {ex.get('signal')}, "
                       f"watchdog_expired {ex.get('watchdog_expired')} ({srcs[src_i]['name']} job "
                       + (f"m{jk[0]}-" if jk[0] is not None and a.cells else "") + f"b{jk[1]:02d}-c{jk[2]}"
                       + (f":{jk[3]}" if jk[3] else "") + ")")
            else:
                why = "job not run in any attempt (not started)"
            if k[1] == "rho":
                ph = {"panel": k[0], "method": "rho", "bits": k[2], "curve": k[3]}
            else:
                ph = {"panel": k[0], "m": k[1], "bits": k[2], "curve": k[3], "arm": k[4], "mode": k[5]}
            ph |= {"status": "failed_infrastructure", "status_reason": f"no row: {why}", "placeholder": True}
            canonical[k] = {"line": json.dumps(ph), "status": ph["status"], "status_reason": ph["status_reason"],
                            "file": None, "job": None, "placeholder": True}
            per_key[k] = {"attempt": None, "file": None, "placeholder": True}
            placeholders.append({"key": list(k), "status_reason": ph["status_reason"]})

    # staircases (M-5 (6)) and harvest-file map (M-5 (8))
    want = defaultdict(list)          # file -> keys whose canonical row came from that source
    for k, rec in canonical.items():
        if rec["file"] and k[1] != "rho":
            want[rec["file"]].append(k)
    stair_lines = []
    harvest_map = {}
    for rows_file, keys in want.items():
        d = os.path.dirname(rows_file)
        sf = os.path.join(d, "staircase.jsonl.gz")
        hf = os.path.join(d, "harvest-rows.jsonl.gz")
        ks = set(keys)
        if os.path.exists(sf):
            for line, s in iter_lines(sf):
                sk = stair_key(s, panel)
                if sk in ks:
                    stair_lines.append((sort_key(sk), line))
        hd = sha256(hf) if os.path.exists(hf) else None
        for k in keys:
            harvest_map[json.dumps(list(k))] = {"harvest_rows_file": os.path.relpath(hf, REPO) if hd else None,
                                                "sha256": hd}
    stair_lines.sort(key=lambda t: t[0])   # stable: source order kept within an instance

    # write canonical files, sorted by M-5 (7)
    order = sorted(canonical, key=sort_key)
    with open(os.path.join(out, "rows.jsonl"), "w") as fh:
        for k in order:
            fh.write(canonical[k]["line"] + "\n")
    with open(os.path.join(out, "staircase.jsonl"), "w") as fh:
        for _, line in stair_lines:
            fh.write(line + "\n")
    for f in ("rows.jsonl", "staircase.jsonl"):
        subprocess.run(["gzip", "-n", os.path.join(out, f)], check=True)

    # execution.json aggregate (M-5)
    parts = []
    for s in srcs:
        if s["kind"] == "root":
            ex = json.load(open(s["execution"]))
            parts.append({"attempt": s["name"], "peak_rss_bytes": ex["peak_rss_bytes_max_descendant"],
                          "cpu_seconds": ex["cpu_seconds_descendants"], "wall_seconds": ex["wall_seconds"],
                          "watchdog_expired": ex["watchdog_expired"], "exit_code": ex["exit_code"],
                          "source": os.path.relpath(s["execution"], REPO)})
        else:
            js = s["index"]["jobs"]
            parts.append({"attempt": s["name"],
                          "peak_rss_bytes": max((j.get("peak_rss_bytes") or 0 for j in js), default=0),
                          "cpu_seconds": round(sum(j.get("cpu_seconds") or 0 for j in js), 3),
                          "wall_seconds": s["index"]["wall_seconds"],
                          "watchdog_expired": any(j.get("watchdog_expired") for j in js),
                          "job_exit_codes": {j["job"]: j.get("exit_code") for j in js},
                          "source": os.path.relpath(os.path.join(s["dir"], "jobs-index.json"), REPO)})
    agg = {"run_id": a.run_id,
           "label": "aggregated over attempts and jobs by AMD-20260929-430f44 M-5; not one process tree",
           "peak_rss_bytes_max_descendant": max(p["peak_rss_bytes"] for p in parts),
           "cpu_seconds_descendants": round(sum(p["cpu_seconds"] for p in parts), 3),
           "wall_seconds": round(sum(p["wall_seconds"] for p in parts), 3),
           "watchdog_expired": any(p["watchdog_expired"] for p in parts),
           "exit_code": None,
           "exit_code_note": "no single process; per-attempt / per-job exit codes in `attempts`",
           "attempts": parts,
           "excluded_from_aggregate": "the M-3 invocation-check jobs (their rows never enter the canonical set)"}
    with open(os.path.join(out, "execution.json"), "w") as fh:
        json.dump(agg, fh, indent=2)

    counts = Counter(canonical[k]["status"] for k in canonical)
    report.update({
        "per_key_source": {json.dumps(list(k)): per_key[k] for k in order},
        "placeholders": placeholders,
        "non_cell_rows_excluded": noncell,
        "superseded_rows": superseded,
        "determinism_comparisons": determinism,
        "harvest_rows_map": harvest_map,
        "harvest_rows_note": "harvest rows are not merged or copied (M-5 (8)); each canonical instance maps to the file that produced it",
        "canonical_files": {f: sha256(os.path.join(out, f)) for f in ("rows.jsonl.gz", "staircase.jsonl.gz", "execution.json")},
        "canonical_rows": len(canonical), "canonical_staircase_records": len(stair_lines),
        "counts_by_status": dict(counts),
        "keys_with_exactly_one_canonical_row": len(canonical) == len(U) and set(canonical) == U,
        "sort_rule": "M-5 (7): (bits, curve, m, arm, mode), stable; rho rows arm '' (m 0, mode '')",
    })
    with open(os.path.join(out, "merge-report.json"), "w") as fh:
        json.dump(report, fh, indent=2)
    log(f"canonical rows {len(canonical)} (U {len(U)}), placeholders {len(placeholders)}, non-cell rows "
        f"{len(noncell)}, superseded {len(superseded)}, determinism comparisons {len(determinism)}, "
        f"status counts {dict(counts)}")

    if a.cells:
        # summarize_run.py's expected() enumerates one full (m, bits, arms) grid and cannot express a
        # union of excursion cells: raw-result.json by this script over the canonical rows (card
        # REQUIRED ARTIFACTS: "else by merge_census.py"), with expected = U
        raw = summarize_rows(os.path.join(out, "rows.jsonl.gz"), sorted(U, key=sort_key), a.run_id,
                             os.path.relpath(out, REPO), "canonical")
        with open(os.path.join(out, "raw-result.json"), "w") as fh:
            json.dump(raw, fh, indent=2, sort_keys=True)
        log(f"raw-result.json by merge_census.py summarize_rows: {json.dumps(raw['gates_summary'])}")
        return _finish(a, out, log, rj, U, canonical, order, placeholders, noncell, report, parts, agg, counts,
                       srcs, bits, curves, panel, m, raw, raw_by="merge_census.py summarize_rows() (gate_checks() of the pinned summarize_run.py; its expected() cannot express R16's U)")
    # raw-result.json by the pinned summarize_run.py (interface fits: rows.jsonl.gz + execution.json)
    cmd = [PY, os.path.join(REPO, SUMMARIZE), "census", "--run-dir", out, "--run-id", a.run_id, "--panel", panel]
    if panel == "main":
        cmd += ["--m", str(m), "--known-log-max-bits", str(a.known_log_max_bits or 0)]
        if curves != list(range(5)):
            cmd += ["--curves", str(len(curves)), "--curve-offset", str(curves[0])]
    elif panel == "j0":
        cmd += ["--rho-curves", str(a.rho_curves)]
    r = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)
    log(f"$ {' '.join(cmd)}\n{r.stdout}[exit {r.returncode}]")
    if r.returncode != 0:
        log(r.stderr, err=True)
        raise Stop("summarize_run.py failed")
    raw = json.load(open(os.path.join(out, "raw-result.json")))
    return _finish(a, out, log, rj, U, canonical, order, placeholders, noncell, report, parts, agg, counts,
                   srcs, bits, curves, panel, m, raw, raw_by=f"{SUMMARIZE} (sha256 {sha256(os.path.join(REPO, SUMMARIZE))})")


def _finish(a, out, log, rj, U, canonical, order, placeholders, noncell, report, parts, agg, counts,
            srcs, bits, curves, panel, m, raw, raw_by) -> int:
    post = None
    if a.post_command:
        # e.g. R16's M-6 analysis step, which writes into this canonical location; run before the
        # manifest and checksums so that both cover its outputs
        import shlex
        import time as _t
        cmd = shlex.split(a.post_command)
        t0 = _t.time()
        r = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)
        with open(os.path.join(out, "post-step.stdout.log"), "w") as fh:
            fh.write(r.stdout)
        with open(os.path.join(out, "post-step.stderr.log"), "w") as fh:
            fh.write(r.stderr)
        post = {"command": cmd, "exit_code": r.returncode, "wall_seconds": round(_t.time() - t0, 3),
                "stdout": "post-step.stdout.log", "stderr": "post-step.stderr.log"}
        with open(os.path.join(out, "command.txt"), "a") as fh:
            fh.write(f"# then (post step, before manifest): {a.post_command}\n")
        log(f"post step exit {r.returncode}: {a.post_command}")
        if r.returncode != 0:
            raise Stop(f"post step failed (exit {r.returncode}); see post-step.stderr.log")

    # M-7 status
    invalid_rows = [k for k in canonical if canonical[k]["status"] == "invalid"]
    run_stops = [s["name"] for s in srcs if s["kind"] == "pj" and s["index"].get("run_stop_at_job")]
    if invalid_rows or run_stops:
        status, reason = "invalid", f"invalid canonical rows {len(invalid_rows)}; run-stop in {run_stops}"
    elif report["keys_with_exactly_one_canonical_row"]:
        status = "completed_valid"
        reason = ("M-7: every key of U has exactly one canonical row, no canonical row is invalid and no "
                  "run-stop rule fired; instance-level failed_infrastructure rows (placeholders included) "
                  "are allowed and listed")
    else:
        status, reason = "failed_infrastructure", "canonical set incomplete"
    completeness = {"U": len(U), "canonical_rows": len(canonical), "by_status": dict(counts),
                    "placeholders": len(placeholders), "non_cell_rows_excluded": len(noncell)}
    fi = [{"key": list(k), "status_reason": canonical[k]["status_reason"]} for k in order
          if canonical[k]["status"] == "failed_infrastructure"]
    rj.write_manifest(
        out, run_id=a.run_id, location_kind=a.location_kind, status=status, reason=reason,
        completeness=completeness,
        command=open(os.path.join(out, "command.txt")).read().splitlines()[0],
        spec_command=a.spec_command,
        job_list=[att["attempt"] for att in report["attempts"]],
        timing={"merged_at": rj.now(), "attempt_timings": parts,
                "wall_seconds": agg["wall_seconds"], "started_at": None, "finished_at": None,
                "timing_note": "canonical location; wall_seconds is the sum of attempt wall spans (M-5)"},
        resources={"peak_rss_bytes_max_descendant": agg["peak_rss_bytes_max_descendant"],
                   "cpu_seconds_descendants": agg["cpu_seconds_descendants"],
                   "wall_seconds": agg["wall_seconds"], "label": agg["label"],
                   "rlimit_as_bytes_per_process": 3_500_000_000, "instance_watchdog_seconds": 7200,
                   "attempt_watchdog_seconds": 86400},
        inputs=rj.inputs_block(panel, m if not a.cells else sorted({k[1] for k in U}),
                               bits if not a.cells else sorted({k[2] for k in U}),
                               curves if not a.cells else sorted({k[3] for k in U}),
                               report["U_definition"].get("arms") or sorted({k[4] for k in U}),
                               a.known_log_max_bits if panel == "main" else None, a.rho_curves)
               | {"attempt_inputs": "merge-report.json inputs (paths with sha256, receipt-verified where archived)"},
        summary={"canonical_rows": len(canonical), "U": len(U), "counts_by_status": dict(counts),
                 "placeholders": placeholders, "non_cell_rows_excluded": len(noncell),
                 "failed_infrastructure_instances": fi,
                 "invalid_instances": [list(k) for k in invalid_rows],
                 "resume_set": report["resume_set"],
                 "gates": {"G4": raw["gates"]["G4"]["pass"], "G5": raw["gates"]["G5"]["pass"],
                           "G6_G7": raw["gates"]["G6_G7_pass"],
                           "G4_solved_instances": raw["gates"]["G4"]["solved_instances"],
                           "G4_solved_verified": raw["gates"]["G4"]["solved_verified"],
                           "harvest_instances": raw["gates"]["harvest_instances"],
                           "G6_G7_check_counts": raw["gates"]["G6_G7_check_counts"]},
                 "raw_result_by": raw_by,
                 "post_step": post,
                 "raw_result_note": ("summarize_run.py writes the solved-instance count into its "
                                     "certificate.verified field; this manifest's certificate carries "
                                     "verified: true (boolean) and the counts in instances_claimed / "
                                     "instances_verified (card CERTIFICATE FORMAT)")},
        raw=raw)
    log(f"finalized {os.path.relpath(out, REPO)}: {status}")
    return 0


# ------------------------------------------------------------------------------------------
# view (M-6)

def cmd_view(a) -> int:
    runs_root = os.path.join(REPO, a.runs_root)
    view = a.view
    if os.path.exists(view):
        raise SystemExit(f"refusing: view {view} exists")
    os.makedirs(view)
    entries = []
    for name in sorted(os.listdir(runs_root)):
        p = os.path.join(runs_root, name)
        if not (name.startswith("RUN-PFDR-1b78f7-") and os.path.isdir(p)):
            continue
        tgt = os.path.join(p, "merged") if os.path.isdir(os.path.join(p, "merged")) else p
        os.symlink(tgt, os.path.join(view, name))
        files = {}
        for r, dirs, fs in os.walk(tgt):
            dirs.sort()
            for f in sorted(fs):
                fp = os.path.join(r, f)
                files[os.path.relpath(fp, tgt)] = sha256(fp)
        entries.append({"link": name, "target": os.path.relpath(tgt, REPO),
                        "target_is_merged": tgt.endswith("/merged"), "files_sha256": files})
    vm = {"what": "AMD-20260929-430f44 M-6 view map", "view_dir": view,
          "rule": "one link per run directory RUN-PFDR-1b78f7-*; target <run>/merged/ if it exists, else the run root",
          "entries": entries}
    if os.path.exists(a.map_out):
        raise SystemExit(f"refusing: {a.map_out} exists")
    with open(a.map_out, "w") as fh:
        json.dump(vm, fh, indent=2)
    print(json.dumps([{"link": e["link"], "target": e["target"], "files": len(e["files_sha256"])} for e in entries], indent=1))
    return 0


# ------------------------------------------------------------------------------------------
# summarize (attempt-level raw-result.json)

def cmd_summarize(a) -> int:
    ad = a.attempt_dir
    idx = json.load(open(os.path.join(ad, "jobs-index.json")))
    rj = load_module("run_jobs_430f44", os.path.join(HERE, "run_jobs.py"))

    class A:
        pass
    aa = A()
    aa.panel, aa.m, aa.rho_curves = idx["panel"], idx["m"], idx["rho_curves"]
    expected = []
    for j in idx["jobs"]:
        expected += rj.expected_job_keys(aa, j["bits"], j["curve"], j["arm"], j.get("m"))
    jobmap = {j["job"]: j for j in idx["jobs"]}
    for name in idx["not_started"]:
        # names as run_jobs.job_name(): [m<M>-]b<BB>-c<C>[-<arm>]; the arm list of an R16 job is
        # recovered from the attempt's command.txt job list is not needed: not-started R16 jobs carry
        # their spec in jobs-index "not_started_specs"
        spec = (idx.get("not_started_specs") or {}).get(name)
        if spec:
            expected += rj.expected_job_keys(aa, spec[0], spec[1], spec[2], spec[3])
            continue
        parts = name.split("-")
        mm = None
        if parts[0].startswith("m"):
            mm = int(parts[0][1:])
            parts = parts[1:]
        arm = parts[2] if len(parts) > 2 else None
        expected += rj.expected_job_keys(aa, int(parts[0][1:]), int(parts[1][1:]), arm, mm)
    rows_files = [(os.path.join(REPO, j["job_dir"], "rows.jsonl.gz"), j["job"]) for j in idx["jobs"]]
    raw = summarize_rows(rows_files, expected, a.run_id, os.path.relpath(ad, REPO), "attempt")
    out = os.path.join(ad, "raw-result.json")
    if os.path.exists(out):
        raise SystemExit(f"refusing: {out} exists")
    with open(out, "w") as fh:
        json.dump(raw, fh, indent=2, sort_keys=True)
    print(json.dumps({"completeness": {k: v for k, v in raw["completeness"].items() if k != "missing"},
                      "status_totals": raw["status_totals"], "gates": raw["gates_summary"]}))
    return 0


def summarize_rows(rows_files, expected, run_id, location, location_kind) -> dict:
    """Statuses, completeness and gate / certificate counts over row files (keys, statuses and the
    gate fields read by the pinned summarize_run.py gate_checks(); no measured quantity)."""
    sr = load_module("summarize_run_amd1de84f", os.path.join(REPO, SUMMARIZE))
    if isinstance(rows_files, str):
        rows_files = [(rows_files, None)]
    expected = [tuple(k) for k in expected]
    expset = set(expected)
    got = Counter()
    status_tot = Counter()
    failed, invalid, nonjob = [], [], []
    cert = Counter()
    g4_bad, k_bad, g5_bad, g67 = [], [], [], Counter()
    harvest_instances = solved = verified = 0
    for rp, jname in rows_files:
        if not os.path.exists(rp):
            continue
        for _, r in iter_lines(rp):
            k = row_key(r)
            if k not in expset:
                nonjob.append({"key": list(k), "status": r.get("status"), "status_reason": r.get("status_reason"),
                               "job": jname})
                continue
            got[k] += 1
            status_tot[r.get("status")] += 1
            if r.get("status") == "failed_infrastructure":
                failed.append({"key": list(k), "status_reason": r.get("status_reason"),
                               "ru_maxrss_bytes": r.get("ru_maxrss_bytes"), "job": jname})
            if r.get("status") == "invalid":
                invalid.append({"key": list(k), "status_reason": r.get("status_reason"), "job": jname})
            gc = sr.gate_checks(r)
            if r.get("harvest"):
                harvest_instances += 1
                for c, v in gc["G4_rows"].items():
                    cert[f"{c}_cert_pass"] += v["cert_pass"]
                    cert[f"{c}_cert_fail"] += v["cert_fail"]
                    cert[f"{c}_rows_emitted"] += v["rows_emitted"]
                    if not v["ok"]:
                        g4_bad.append(list(k) + [c])
                if not gc["G5_identity_ok"]:
                    g5_bad.append(list(k))
            if r.get("k_found") or (r.get("method") == "rho" and r.get("status") != "failed_infrastructure"):
                solved += 1
                ok = gc.get("G4_kP_eq_Q", r.get("ok")) if r.get("method") != "rho" else bool(r.get("ok"))
                verified += bool(ok)
                if not ok:
                    k_bad.append(list(k))
            for kk, v in gc.items():
                if kk.startswith(("G6", "G7")):
                    g67[f"{kk}|{'pass' if v else 'fail'}"] += 1
    missing = [list(k) for k in expected if got[k] == 0]
    dup = [list(k) for k, n in got.items() if n > 1]
    raw = {"run_id": run_id, "experiment_id": "EXP-PFDR-1b78f7",
           "location": location, "location_kind": location_kind,
           "summarised_by": "merge_census.py summarize_rows (gate_checks() of the pinned summarize_run.py)",
           "completeness": {"expected_keys": len(expset), "keys_present": sum(1 for k in expset if got[k]),
                            "keys_missing": len(missing), "missing": missing, "duplicates": dup,
                            "non_job_rows": len(nonjob)},
           "non_job_rows": nonjob,
           "status_totals": dict(status_tot), "failed_infrastructure": failed, "invalid": invalid,
           "gates": {"harvest_instances": harvest_instances,
                     "G4": {"pass": not g4_bad and not k_bad, "row_certificate_failures": g4_bad,
                            "k_not_verified": k_bad, "solved_instances": solved, "solved_verified": verified},
                     "G5": {"pass": not g5_bad, "identity_failures": g5_bad},
                     "G6_G7_check_counts": dict(sorted(g67.items())),
                     "G6_G7_pass": not any(x.endswith("|fail") for x in g67)},
           "certificate": {"kind": "discrete_log" if solved else "none",
                           "verifier": "kP == Q by curve.py scalar multiplication (solver `verified`; rho `verified`)",
                           "instances_claimed": solved, "instances_verified": verified,
                           "harvested_row_check": dict(cert),
                           "harvested_row_check_note": ("each harvested row re-verified as sum c_i F_i + kcoef Q == rhs P "
                                                        "on an independent Curve instance before any elimination")}}
    raw["gates_summary"] = {"G4": raw["gates"]["G4"]["pass"], "G5": raw["gates"]["G5"]["pass"],
                            "G6_G7": raw["gates"]["G6_G7_pass"], "harvest_instances": harvest_instances,
                            "solved": solved, "verified": verified}
    return raw


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("compare")
    c.add_argument("--check-id", required=True)
    c.add_argument("--panel", default="main")
    c.add_argument("--m", type=int, required=True)
    c.add_argument("--bits", type=int, required=True)
    c.add_argument("--curve", type=int, required=True)
    c.add_argument("--arms", nargs="*", default=None)
    c.add_argument("--a-rows", required=True)
    c.add_argument("--a-stairs", required=True)
    c.add_argument("--a-harvest", required=True)
    c.add_argument("--b-dir", required=True)
    c.add_argument("--out", required=True)
    r = sub.add_parser("resume-set")
    r.add_argument("--rows", required=True)
    r.add_argument("--m", type=int, default=4)
    r.add_argument("--out", default=None)
    g = sub.add_parser("merge")
    g.add_argument("--run-id", required=True)
    g.add_argument("--run-dir", required=True)
    g.add_argument("--out", required=True)
    g.add_argument("--panel", choices=("main", "j0", "rho"), required=True)
    g.add_argument("--m", type=int, default=None)
    g.add_argument("--bits", type=int, nargs="+", required=True)
    g.add_argument("--curves", type=int, nargs="+", default=[0, 1, 2, 3, 4])
    g.add_argument("--arms", nargs="+", default=None)
    g.add_argument("--rho-curves", type=int, default=None)
    g.add_argument("--known-log-max-bits", type=int, default=0)
    g.add_argument("--attempts", nargs="*", default=[])
    g.add_argument("--root-attempt1", action="store_true")
    g.add_argument("--assert-r11-resume-set", action="store_true")
    g.add_argument("--receipt", nargs="*", default=[])
    g.add_argument("--location-kind", default="canonical")
    g.add_argument("--spec-command", default="")
    g.add_argument("--cells", nargs="*", default=None,
                   help="R16: U = union of 'm:bits:arm1+arm2+...:c1+c2+...' cells (main panel)")
    g.add_argument("--post-command", default=None,
                   help="a command run after the canonical files and raw-result.json, before the manifest")
    v = sub.add_parser("view")
    v.add_argument("--runs-root", required=True)
    v.add_argument("--view", required=True)
    v.add_argument("--map-out", required=True)
    s = sub.add_parser("summarize")
    s.add_argument("--attempt-dir", required=True)
    s.add_argument("--run-id", required=True)
    a = ap.parse_args()
    return {"compare": cmd_compare, "resume-set": cmd_resume_set, "merge": cmd_merge, "view": cmd_view,
            "summarize": cmd_summarize}[a.cmd](a)


if __name__ == "__main__":
    raise SystemExit(main())
