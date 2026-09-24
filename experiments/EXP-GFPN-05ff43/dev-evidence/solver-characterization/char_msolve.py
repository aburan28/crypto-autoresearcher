#!/usr/bin/env python3
"""TASK-20260923-6599cf -- ZERO-RUN msolve characterization harness (EXP-GFPN-05ff43 repair).

Card: ledger/handoffs/TASK-20260923-6599cf.yaml (CH-1..CH-10); ruling DEC-20260923-582d6b R-3;
readings: the DRAFT AMD-EXP-GFPN-05ff43-20260923-solverevent `characterization_readings` CR-1..CR-5
(bound by sha256 011d4b2c... in the TASK-20260923-4eee3b receipt); bundle hash per CORR-20260923-9abefc.

Creates NO run package. Writes only to a scratch work directory (--work) and, in `analyze`, to the
card's write_scope (--out). Every msolve child is launched through the FROZEN v2_solver.run_child
(imported, never edited) with cap_bytes 10737418240, and every solve is classified by the FROZEN
parse_msolve_log / parse_msolve_param / rational_solutions / classify_solve with n_sub_fail = 0
(the substitution check is NOT re-run: no descended system exists here).

Subcommands (run in this order; the design below is FIXED before any solve):
  integrity  CH-3 (a)-(e). Extracts the committed bundle into <work>/bundle (never into the repo).
  run        C-3 (b) first, then C-1a, C-1b, C-1c, C-2, C-3 (c). Raw per-child records only.
  analyze    classification, CR-1, CR-2 (n_c, x_c, u_c, u_max, S_ub, K), CR-3, C-3 (a), C-4; writes
             summary.json, solves.jsonl and distinct-outputs.tar.gz into --out.
Observations only. No D, degree or quotient dimension here is a result; toy values are harness
parameters and the 4111 values are archived RUN-GFPN-ac4487 values re-observed.
"""
import argparse
import collections
import datetime
import difflib
import glob
import hashlib
import io
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tarfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
EXP = os.path.join(REPO, "experiments", "EXP-GFPN-05ff43")
IMPL_V2 = os.path.join(EXP, "implementation-v2")
sys.path.insert(0, IMPL_V2)
import v2_solver as V  # noqa: E402  (frozen; imported, never edited)

# ----------------------------------------------------------------------------- fixed design
CAP = 10737418240                  # AC-1 / CH-2; DP-5 guard threshold is above 12.0 GB so no lowering
TIMEOUT_S = 600                    # declared per-child run_child timeout (CH-2: at most 600 s)
PACE_C1B_S = 1.1                   # C-1b: each start >= 1.1 s after the previous child ended
DESIGN = [                         # (label, class, input set, reps per input, pacing s, extra flags)
    ("C-1a", "C-1a", "event", 500, 0.0, []),
    ("C-1b", "C-1b", "event", 500, PACE_C1B_S, []),
    ("C-1c", "C-1c", "toy35", 100, 0.0, []),
    ("C-2", "C-2", "ac4487", 100, 0.0, []),
    ("C-3c-event-c0", "C-3c", "event", 200, 0.0, ["-c", "0"]),
    ("C-3c-event-c1", "C-3c", "event", 200, 0.0, ["-c", "1"]),
    ("C-3c-ac4487-c1", "C-3c", "ac4487", 5, 0.0, ["-c", "1"]),
]
CR_CLASSES = ["C-1a", "C-1b", "C-1c", "C-2"]

BUNDLE = os.path.join(EXP, "dev-evidence", "stageR1-dv7", "stageR1-dv7-evidence.tar.gz")
RCPT_53A47D = os.path.join(REPO, "coordination", "goals", "GOAL-GFPN-380702", "archives", "TASK-20260923-53a47d", "preservation-receipt.json")
RCPT_0FA03F = os.path.join(REPO, "coordination", "goals", "GOAL-GFPN-380702", "archives", "TASK-20260923-0fa03f", "post-run-receipt.json")
RCPT_4EEE3B = os.path.join(REPO, "coordination", "goals", "GOAL-GFPN-380702", "archives", "TASK-20260923-4eee3b", "snapshot-receipt.json")
ADDENDUM = os.path.join(EXP, "amendments", "v2_addendum_solverevent.yaml")
BUNDLE_SHA_CORRECTED = "70b83d61bfd05fcc92208c9f2bdba58fea0e7b587a927d54141bb72ccd35bd14"   # CORR-20260923-9abefc
EVENT_INPUT_SHA = "541b57b904e0c16956f9ea4615a32f1aaaae1cdfe7ca9c3b767f3b5f22d537c8"          # CH-3 (b)
WORLD_A_PREFIX = "d2878f4f2b276162"                                                            # CH-3 (c)
WORLD_B_PREFIX = "201812d43b7c7a9d"
TOY_REL = os.path.join("stageR1", "dv7", "toy", "world_%s", "exp", "runs", "RUN-GFPN-a61a10", "solver")
EVENT_STEM = "fx_reg0_torsion_S3_norm"
AC4487_SOLVER = os.path.join(EXP, "runs", "RUN-GFPN-ac4487", "solver")
NSP_PREFIXES = ("eliminating polynomial is not square-free", "eliminating polynomial degree ",
                "msolve reports square-free part degree ")                                     # draft SE-1 (i)-(iii)


# ----------------------------------------------------------------------------- utils
def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def utc(t):
    return datetime.datetime.fromtimestamp(t, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def rel(p):
    return os.path.relpath(p, REPO) if p.startswith(REPO) else p


def dump(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(obj, fh, indent=1, sort_keys=True, default=str)
        fh.write("\n")
    os.replace(tmp, path)


def git_state():
    def g(*a):
        return subprocess.run(["git", "-C", REPO] + list(a), capture_output=True, text=True).stdout.strip()
    por = g("status", "--porcelain", "--untracked-files=all")
    return {"head": g("rev-parse", "HEAD"), "branch": g("branch", "--show-current"),
            "dirty": bool(por), "porcelain": por.splitlines()}


def read_text(path):
    try:
        with open(path, errors="replace") as fh:
            return fh.read()
    except OSError:
        return None


def input_meta(path):
    with open(path) as fh:
        names = fh.readline().strip().split(",")
        p = int(fh.readline().strip())
    return {"names": names, "nvars": len(names), "p": p}


# ----------------------------------------------------------------------------- integrity (CH-3)
def input_sets(work):
    """The fixed input sets. Returns {set_name: [(stem, path_in_work, source_path)]}."""
    bsol = os.path.join(work, "bundle", TOY_REL % "B")
    toy = sorted(glob.glob(os.path.join(bsol, "*.ms")))
    ev = [x for x in toy if os.path.basename(x) == EVENT_STEM + ".ms"]
    others = [x for x in toy if os.path.basename(x) != EVENT_STEM + ".ms"]
    ac = sorted(glob.glob(os.path.join(AC4487_SOLVER, "*.ms")))
    mk = lambda xs: [(os.path.basename(x)[:-3], x) for x in xs]  # noqa: E731
    return {"event": mk(ev), "toy35": mk(others), "ac4487": mk(ac)}


def cmd_integrity(args):
    work = args.work
    os.makedirs(work, exist_ok=True)
    res = {"task": "TASK-20260923-6599cf", "checked_at": utc(time.time()), "checks": {}, "pass": False}
    ck = res["checks"]
    # (0) the draft addendum is the bytes TASK-20260923-4eee3b bound (DP-1)
    r4 = json.load(open(RCPT_4EEE3B))
    ck["draft_addendum"] = {"path": rel(ADDENDUM), "sha256": sha256_file(ADDENDUM),
                            "receipt_value": r4["addendum_sha256"]["sha256"]}
    ck["draft_addendum"]["pass"] = ck["draft_addendum"]["sha256"] == ck["draft_addendum"]["receipt_value"]
    # (a) bundle sha256 == TASK-20260923-53a47d receipt value (and the CORR-20260923-9abefc value)
    r5 = json.load(open(RCPT_53A47D))
    bsha = sha256_file(BUNDLE)
    rv = r5["path_sha256"][rel(BUNDLE)]
    ck["a_bundle"] = {"path": rel(BUNDLE), "bytes": os.path.getsize(BUNDLE), "sha256": bsha, "receipt_value": rv,
                      "receipt_bundle_status": r5.get("bundle_status"), "corrected_card_value": BUNDLE_SHA_CORRECTED,
                      "pass": bsha == rv == BUNDLE_SHA_CORRECTED and r5.get("bundle_status") == "committed"}
    if not ck["a_bundle"]["pass"]:
        dump(os.path.join(work, "integrity.json"), res)
        print("CH-3 (a) FAILED"); sys.exit(2)
    bdir = os.path.join(work, "bundle")
    if os.path.exists(bdir):
        shutil.rmtree(bdir)
    os.makedirs(bdir)
    with tarfile.open(BUNDLE, "r:gz") as tf:
        tf.extractall(bdir, filter="data")
    res["bundle_extracted_to"] = bdir
    # (b) event input
    ev = {w: os.path.join(bdir, TOY_REL % w, EVENT_STEM + ".ms") for w in "AB"}
    ck["b_event_input"] = {w: {"path": ev[w].replace(work, "<work>"), "sha256": sha256_file(ev[w])} for w in "AB"}
    ck["b_event_input"]["expected"] = EVENT_INPUT_SHA
    ck["b_event_input"]["pass"] = all(ck["b_event_input"][w]["sha256"] == EVENT_INPUT_SHA for w in "AB")
    # (c) world A / world B outputs
    outs = {w: os.path.join(bdir, TOY_REL % w, EVENT_STEM + ".ms.out") for w in "AB"}
    ck["c_event_outputs"] = {}
    for w, pref in (("A", WORLD_A_PREFIX), ("B", WORLD_B_PREFIX)):
        s = sha256_file(outs[w]) if os.path.exists(outs[w]) else None
        ck["c_event_outputs"]["world_" + w] = {"path": outs[w].replace(work, "<work>"), "sha256": s, "expected_prefix": pref,
                                               "pass": bool(s and s.startswith(pref))}
        for ext in (".ms.log", ".ms.err"):
            f = os.path.join(bdir, TOY_REL % w, EVENT_STEM + ext)
            ck["c_event_outputs"]["world_" + w][ext[1:] + "_sha256"] = sha256_file(f) if os.path.exists(f) else None
    ck["c_event_outputs"]["pass"] = all(v["pass"] for v in ck["c_event_outputs"].values() if isinstance(v, dict))
    # (d) every RUN-GFPN-ac4487 file read matches the TASK-20260923-0fa03f post-run receipt
    r0 = json.load(open(RCPT_0FA03F))["path_sha256"]
    files = sorted(glob.glob(os.path.join(AC4487_SOLVER, "*.ms")) + glob.glob(os.path.join(AC4487_SOLVER, "*.ms.out"))
                   + glob.glob(os.path.join(AC4487_SOLVER, "*.ms.log")) + glob.glob(os.path.join(AC4487_SOLVER, "*.ms.err"))
                   + [os.path.join(EXP, "runs", "RUN-GFPN-ac4487", f) for f in ("manifest.yaml", "raw-result.json")])
    bad = []
    for f in files:
        h = sha256_file(f)
        if r0.get(rel(f)) != h:
            bad.append({"path": rel(f), "sha256": h, "receipt": r0.get(rel(f))})
    ck["d_ac4487_files"] = {"n_files": len(files), "n_ms": len(glob.glob(os.path.join(AC4487_SOLVER, "*.ms"))),
                            "mismatches": bad, "pass": not bad and len(files) == 36 * 4 + 2}
    # (e) the other 35 toy inputs of the world B toy G1 package
    sets = input_sets(work)
    toy35 = sets["toy35"]
    same_A = [s for s, p in toy35 if os.path.exists(os.path.join(bdir, TOY_REL % "A", s + ".ms"))
              and sha256_file(os.path.join(bdir, TOY_REL % "A", s + ".ms")) == sha256_file(p)]
    ck["e_toy35"] = {"n_found": len(toy35), "expected": 35, "byte_identical_in_world_A": len(same_A),
                     "inputs": {s: sha256_file(p) for s, p in toy35}, "gap": 35 - len(toy35),
                     "stop_on_gap": False}
    res["pass"] = all(ck[k]["pass"] for k in ("draft_addendum", "a_bundle", "b_event_input", "c_event_outputs", "d_ac4487_files"))
    res["ac4487_input_sha256"] = {s: sha256_file(p) for s, p in sets["ac4487"]}
    dump(os.path.join(work, "integrity.json"), res)
    print(json.dumps({k: v.get("pass") for k, v in ck.items() if isinstance(v, dict)}, indent=1))
    if not res["pass"]:
        print("CH-3 FAILED: no solve may start"); sys.exit(2)
    print("CH-3 PASS")


# ----------------------------------------------------------------------------- run
KEEP = ("outcome", "returncode", "timed_out", "wall_seconds", "rlimit_as_child_getrlimit", "rlimit_as_proc_limits_after_exec",
        "child_rlimit_report", "refusal_reason", "other_processes", "peak_rss_bytes", "peak_vm_bytes", "rusage", "timeout_s",
        "cap_bytes_requested", "driver_rss_bytes_before_launch", "memory_exhausted_basis", "argv")


def envelope_stop(work, why, rec):
    dump(os.path.join(work, "STOP.json"), {"at": utc(time.time()), "why": why, "record": rec})
    print("ENVELOPE STOP:", why)
    sys.exit(3)


def cmd_run(args):
    work = args.work
    integ = json.load(open(os.path.join(work, "integrity.json")))
    if not integ.get("pass"):
        print("REFUSING: integrity.json does not pass"); sys.exit(2)
    wanted = args.labels.split(",") if args.labels else None
    os.makedirs(os.path.join(work, "records"), exist_ok=True)
    runlog = os.path.join(work, "run-meta.jsonl")
    with open(runlog, "a") as fh:
        fh.write(json.dumps({"event": "run_start", "at": utc(time.time()), "labels": wanted, "suffix": args.suffix,
                             "git": git_state(), "pid": os.getpid(), "PYTHONHASHSEED": os.environ.get("PYTHONHASHSEED"),
                             "PYTHONDONTWRITEBYTECODE": os.environ.get("PYTHONDONTWRITEBYTECODE"),
                             "host_memory": V.host_memory(), "lock_path": V.LOCK_PATH,
                             "argv": sys.argv}) + "\n")
    sets = input_sets(work)
    # ---- C-3 (b) FIRST: msolve -h through the capped child runner; package version; help search
    if wanted is None or "C-3b" in wanted:
        d = os.path.join(work, "c3b")
        os.makedirs(d, exist_ok=True)
        t0 = time.time()
        rec = V.run_child([V.MSOLVE, "-h"], os.path.join(d, "msolve-h.stdout"), os.path.join(d, "msolve-h.stderr"),
                          cap_bytes=CAP, timeout_s=60, count_instructions=False)
        t1 = time.time()
        help_text = (read_text(os.path.join(d, "msolve-h.stdout")) or "") + (read_text(os.path.join(d, "msolve-h.stderr")) or "")
        dpkg = subprocess.run(["dpkg-query", "-W", "-f", "${Package} ${Version} ${Architecture}\n", "msolve", "libmsolve-0.6.5"],
                              capture_output=True, text=True).stdout
        hits = [{"line": i + 1, "text": ln} for i, ln in enumerate(help_text.splitlines()) if re.search(r"(?i)seed|random|generic", ln)]
        dump(os.path.join(d, "c3b.json"), {"start_utc": utc(t0), "end_utc": utc(t1), "child": {k: rec.get(k) for k in KEEP},
                                           "help_sha256": sha256_bytes(help_text.encode()), "dpkg": dpkg,
                                           "msolve_binary": V.MSOLVE, "msolve_binary_sha256": sha256_file(V.MSOLVE),
                                           "version_string_note": "msolve 0.6.5 -h prints no version string and has no version option; "
                                                                  "the -v 2 log prints none either. Version from dpkg only.",
                                           "search_seed_random_generic": hits})
        if (rec.get("rlimit_as_child_getrlimit") or {}).get("soft") != CAP:
            envelope_stop(work, "C-3b child cap read-back != %d" % CAP, rec)
    for label, cls, setname, reps, pace, flags in DESIGN:
        if wanted is not None and label not in wanted:
            continue
        lab = label + (args.suffix or "")
        recpath = os.path.join(work, "records", lab + ".jsonl")
        if os.path.exists(recpath):
            print("REFUSING: records for %s already exist (a restart takes a NEW label, CH-9)" % lab); sys.exit(2)
        items = sets[setname]
        with open(runlog, "a") as fh:
            fh.write(json.dumps({"event": "class_start", "label": lab, "at": utc(time.time()), "n_inputs": len(items), "reps": reps,
                                 "pace_s": pace, "flags": flags}) + "\n")
        prev_end = None
        with open(recpath, "a") as rf:
            for stem, inp in items:
                in_sha = sha256_file(inp)
                meta = input_meta(inp)
                sd = os.path.join(work, "solves", lab, stem)
                os.makedirs(sd, exist_ok=True)
                for rep in range(reps):
                    if pace and prev_end is not None:
                        w = prev_end + pace - time.time()
                        if w > 0:
                            time.sleep(w)
                    out = os.path.join(sd, "r%04d.ms.out" % rep)
                    log = os.path.join(sd, "r%04d.ms.log" % rep)
                    err = os.path.join(sd, "r%04d.ms.err" % rep)
                    argv = V.msolve_argv(inp, out, threads=1) + list(flags)
                    t0 = time.time()
                    rec = V.run_child(argv, log, err, cap_bytes=CAP, timeout_s=TIMEOUT_S)
                    t1 = time.time()
                    prev_end = t1
                    row = {"label": lab, "class": cls, "input": stem, "input_set": setname, "input_path": inp.replace(work, "<work>") if inp.startswith(work) else rel(inp),
                           "input_sha256": in_sha, "p": meta["p"], "nvars": meta["nvars"], "rep": rep, "flags": list(flags),
                           "start_utc": utc(t0), "end_utc": utc(t1), "start_epoch": t0, "end_epoch": t1,
                           "harness_wall_seconds": round(t1 - t0, 6), "run_child": {k: rec.get(k) for k in KEEP},
                           "files": {"out": out.replace(work, "<work>"), "log": log.replace(work, "<work>"), "err": err.replace(work, "<work>")}}
                    rf.write(json.dumps(row) + "\n")
                    rf.flush()
                    if rec.get("outcome") == "refused_to_start":
                        envelope_stop(work, "run_child refused to start (%s)" % rec.get("refusal_reason"), row)
                    if (rec.get("rlimit_as_child_getrlimit") or {}).get("soft") != CAP:
                        envelope_stop(work, "child cap read-back != %d" % CAP, row)
                if sha256_file(inp) != in_sha:
                    envelope_stop(work, "input %s changed during class %s" % (stem, lab), {"before": in_sha})
        with open(runlog, "a") as fh:
            fh.write(json.dumps({"event": "class_end", "label": lab, "at": utc(time.time())}) + "\n")
        print("done", lab, flush=True)
    with open(runlog, "a") as fh:
        fh.write(json.dumps({"event": "run_end", "at": utc(time.time())}) + "\n")


# ----------------------------------------------------------------------------- classification (frozen code)
def classify_files(out, log, err, p, nvars, child_outcome):
    """Exactly v2_driver.solve's classification path with n_sub_fail = 0 (substitution not re-run)."""
    text = ""
    for f in (log, err):
        t = read_text(f)
        if t is not None:
            text += t + "\n"
    st = V.parse_msolve_log(text)
    kind = payload = sinfo = None
    sols = []
    if child_outcome == "ok":
        kind, payload = V.parse_msolve_param(out)
        if kind == "param":
            sols, sinfo = V.rational_solutions(payload, p, nvars)
    outcome, reason = V.classify_solve({"outcome": child_outcome}, st, kind, payload, sinfo, 0)
    dq = st["dimension_of_quotient"]
    if outcome == "ok":
        D = None if (kind == "none" or (st["no_solution"] and not dq)) else dq
    else:
        D = None
    solset = sorted(tuple(int(v) for v in s) for s in sols)
    hdr = None
    if kind == "param":
        hdr = {"char": payload["char"], "nvars": payload["nvars"], "degree": payload["degree"], "varnames": payload["varnames"],
               "linform": payload["linform"]}
    nsp = outcome == "degenerate_parametrisation" and isinstance(reason, str) and (
        reason == NSP_PREFIXES[0] or reason.startswith(NSP_PREFIXES[1]) or reason.startswith(NSP_PREFIXES[2]))
    return {"dimension_of_quotient_printed": dq, "squarefree_degree_printed": st["fglm"].get("squarefree_degree"),
            "minpoly_degree_reported": st["fglm"].get("minpoly_degree_reported"), "parse_kind": kind, "header": hdr,
            "elim_degree": (sinfo or {}).get("elim_degree"), "elim_squarefree": (sinfo or {}).get("elim_squarefree"),
            "classify_outcome": outcome, "classify_reason": reason, "nsp": nsp,
            "D_as_driver_would_record": D, "n_rational_solutions": len(solset),
            "solution_set_sha256": sha256_bytes(json.dumps(solset).encode()),
            "n_f4_rounds": len(st["f4_rounds"])}


def parsed_key(c):
    """SE-4 (d) d-parsed comparison: parse kind, header degree, eliminating degree, square-free flag,
    F_p-rational solution set (as a set), D."""
    return (c["parse_kind"], (c["header"] or {}).get("degree"), c["elim_degree"], c["elim_squarefree"],
            c["solution_set_sha256"], c["D_as_driver_would_record"])


# ----------------------------------------------------------------------------- statistics
def binom_cdf(x, n, p):
    if p <= 0:
        return 1.0
    if p >= 1:
        return 0.0 if x < n else 1.0
    lp, lq = math.log(p), math.log1p(-p)
    s = 0.0
    for k in range(0, x + 1):
        s += math.exp(math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1) + k * lp + (n - k) * lq)
    return min(s, 1.0)


def cp_upper(x, n, alpha=0.05):
    """One-sided Clopper-Pearson upper bound: the p with P(Binomial(n, p) <= x) = alpha (CR-2)."""
    if n == 0:
        return None
    if x >= n:
        return 1.0
    if x == 0:
        return 1.0 - alpha ** (1.0 / n)
    lo, hi = 0.0, 1.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if binom_cdf(x, n, mid) > alpha:
            lo = mid
        else:
            hi = mid
    return hi


# ----------------------------------------------------------------------------- S_ub (CR-2)
def solve_call_sites():
    sites = []
    for f in (os.path.join(IMPL_V2, "v2_driver.py"), os.path.join(EXP, "implementation-v2-a1", "a1_driver.py")):
        for i, ln in enumerate(open(f).read().splitlines(), 1):
            if re.search(r"(?<![\w.])(?:D\.)?solve\(", ln) and not ln.lstrip().startswith("def "):
                sites.append({"file": rel(f), "line": i, "gb_only_true": "gb_only=True" in ln, "text": ln.strip()[:220]})
    return sites


def s_ub():
    import v2_common as C  # frozen; only its fixture data path constant is read
    fx = json.load(open(C.FIXTURE_N3_JSON))
    nreg = {e["p"]: len(e["targets"]) for e in fx["primes"]}
    out = {"plans": {}, "call_sites": solve_call_sites(), "per_kind_bound_from_code": {
        "fixture": "(n_regression(p) + 12 + 2) x 6: fixture_core runs run_target (one solve per arm, 6 arms = fixture_arms(3)) for each regression target, for at most 12 fresh draws (`while fresh_ok < 2 and draws < 12`, one run_target per draw at most), and for at most 2 planted targets (v2_driver.py lines 271-273, 354-358, 391-431)",
        "fixture4": "2 targets x 4 arms (cmd_fixture4, v2_driver.py lines 552-565)",
        "controls": "2 labels x 2 solves (identity, raw_x) + 4 planted arms (cmd_controls, v2_driver.py lines 783-787 and 806-841)",
        "anchor": "0: both call sites pass gb_only=True (v2_driver.py lines 693, 711)",
        "build": "0: cmd_build has no solve() call (v2_driver.py lines 935-988)",
        "cells": "len(cells) x targets_per_cell: _run_cell calls solve() at most once per target (v2_driver.py lines 1140-1175); not_attempted / refused / condition-unmet cells make 0 calls but are counted (upper bound)",
        "aggregate": "0", "aggregate_a1": "0",
        "controls_a1": "2 planted arms (a1_driver.py lines 142-166)",
        "contingency": "max over the plan's NON-GATE packages: a contingency re-runs, with identical driver arguments, one non-gate package whose manifest records infrastructure_error (contingency_rule; each package replaced at most once)"}}
    total = 0
    for fname in ("trial-plan-v2.json", "trial-plan-v2-a1.json"):
        path = os.path.join(EXP, fname)
        plan = json.load(open(path))
        gate = set(plan["gate"].get("blocking_packages", []) or [])
        if "addendum_blocking_package" in plan["gate"]:
            gate.add(plan["gate"]["addendum_blocking_package"])
        rows = []
        for pk in plan["packages"]:
            k = pk["kind"]
            if k == "fixture":
                b = (nreg[pk["p"]] + 12 + 2) * 6
            elif k == "fixture4":
                b = 2 * 4
            elif k == "controls":
                b = 2 * 2 + 4
            elif k == "controls_a1":
                b = 2
            elif k == "cells":
                b = len(pk["cells"]) * int(pk["targets_per_cell"])
            elif k in ("anchor", "build", "aggregate", "aggregate_a1"):
                b = 0
            elif k == "contingency":
                b = None
            else:
                raise SystemExit("unknown package kind %s" % k)
            rows.append({"run_id": pk.get("run_id"), "kind": k, "p": pk.get("p"), "bound": b, "gate": pk.get("run_id") in gate or k == "controls_a1"})
        ng = max(r["bound"] for r in rows if r["bound"] is not None and not r["gate"])
        for r in rows:
            if r["kind"] == "contingency":
                r["bound"] = ng
        sub = sum(r["bound"] for r in rows)
        total += sub
        out["plans"][fname] = {"sha256": sha256_file(path), "packages": rows, "subtotal": sub,
                               "max_non_gate_package_bound": ng, "n_regression_by_p": {str(k): v for k, v in nreg.items()}}
    out["S_ub"] = total
    out["label"] = "a parameter count from plan parameters and driver code, not an outcome (CR-2)"
    return out


# ----------------------------------------------------------------------------- C-4 census (read-only)
def census():
    runs = sorted(glob.glob(os.path.join(EXP, "runs", "RUN-*")))
    r0 = json.load(open(RCPT_0FA03F))["path_sha256"]
    by = collections.defaultdict(lambda: {"logs": 0, "logs_with_quotient_dimension": 0, "nsp_signature": 0,
                                          "not_squarefree_text": 0, "sqfree_part_below_dimension": 0,
                                          "minimal_poly_not_square_free_text": 0, "packages": set()})
    pkgs = []
    nsp_logs = []
    for rd in runs:
        rid = os.path.basename(rd)
        man = read_text(os.path.join(rd, "manifest.yaml")) or ""
        if rid == "RUN-GFPN-ac4487":
            if r0.get(rel(os.path.join(rd, "manifest.yaml"))) != sha256_file(os.path.join(rd, "manifest.yaml")):
                raise SystemExit("CH-3 (d): ac4487 manifest does not match receipt")
        pm = re.search(r"--p\s+(\d+)", man)
        mm = re.search(r"--m\s+(\d+)", man)
        cm = re.search(r"cell-p(\d+)-[^\s]*-m(\d+)", man)
        pv = int(pm.group(1)) if pm else (int(cm.group(1)) if cm else None)
        mv = int(mm.group(1)) if mm else (int(cm.group(2)) if cm else None)
        proto = re.search(r"protocol_version:\s*(\S+)", man)
        if rid in ("RUN-GFPN-ac4487", "RUN-GFPN-3377f1"):
            pv = pv or (4111 if rid == "RUN-GFPN-ac4487" else 16777291)
            mv = mv or 3
        logs = sorted(glob.glob(os.path.join(rd, "*.ms.log")) + glob.glob(os.path.join(rd, "solver", "*.ms.log")))
        outs = sorted(glob.glob(os.path.join(rd, "*.ms.out")) + glob.glob(os.path.join(rd, "solver", "*.ms.out")))
        cellm = re.search(r"^\s*cell:\s*(\S+)", man, re.M)
        cell = cellm.group(1) if cellm else None
        for lg in logs:
            mlog = mv
            m_src = "manifest" if mv is not None else None
            if mlog is None:
                fm = re.search(r"_m(\d)\.ms\.log$", lg) or re.search(r"S(\d)(?:_rescaled)?\.ms\.log$", lg)
                mlog, m_src = (int(fm.group(1)), "log file name") if fm else (None, None)
            key = "p=%s m=%s" % (pv, mlog) + ("" if (pv is not None and mv is not None) else " [cell=%s; m from %s]" % (cell, m_src))
            text = read_text(lg) or ""
            ef = lg[:-4] + ".err"
            if os.path.exists(ef):
                text += "\n" + (read_text(ef) or "")
            if rid == "RUN-GFPN-ac4487":
                for f in (lg, ef):
                    if os.path.exists(f) and r0.get(rel(f)) != sha256_file(f):
                        raise SystemExit("CH-3 (d): %s does not match receipt" % rel(f))
            b = by[key]
            b["logs"] += 1
            b["packages"].add(rid)
            dq = re.search(r"Dimension of quotient:\s*(\d+)", text)
            sq = re.search(r"Degree of the square-free part:\s*(\d+)", text)
            if dq:
                b["logs_with_quotient_dimension"] += 1
            t1 = "not squarefree" in text
            t2 = bool(sq and dq and int(sq.group(1)) < int(dq.group(1)))
            t3 = "not square-free" in text
            b["not_squarefree_text"] += t1
            b["sqfree_part_below_dimension"] += t2
            b["minimal_poly_not_square_free_text"] += t3
            if t1 or t2:
                b["nsp_signature"] += 1
                nsp_logs.append({"path": rel(lg), "p": pv, "m": mv, "not_squarefree_text": t1, "sqfree_part_below_dimension": t2})
        pkgs.append({"run_id": rid, "cell": cell, "protocol_version": proto.group(1) if proto else None, "protocol_version_note": None if proto else "manifest has no protocol_version field (v1 package per DP-7)", "p": pv, "m": mv,
                     "retained_ms_log": len(logs), "retained_ms_out": len(outs)})
    table = {k: dict(v, packages=sorted(v["packages"])) for k, v in sorted(by.items())}
    return {"by_prime_and_m": table, "packages": pkgs, "nsp_signature_logs": nsp_logs,
            "packages_without_retained_logs": [x["run_id"] for x in pkgs if x["retained_ms_log"] == 0],
            "rule": "NSP signature = the text 'not squarefree' or 'Degree of the square-free part: s' with s below the printed "
                    "'Dimension of quotient'. Counts only; no D value is read. 'not square-free' (msolve's 'Mininimal polynomial "
                    "is not square-free' message) is counted separately and is not part of the card's signature.",
            "log_text_rule": "<tag>.ms.log plus <tag>.ms.err where one exists (v2 splits stdout/stderr; v1 kept one log)"}


# ----------------------------------------------------------------------------- analyze
def cmd_analyze(args):
    work, outdir = args.work, args.out
    integ = json.load(open(os.path.join(work, "integrity.json")))
    bdir = os.path.join(work, "bundle")
    # references
    refs = {}
    for w in "AB":
        d = os.path.join(bdir, TOY_REL % w)
        f = lambda e: os.path.join(d, EVENT_STEM + e)  # noqa: E731
        c = classify_files(f(".ms.out"), f(".ms.log"), f(".ms.err"), 1033, 3, "ok")
        c["out_sha256"] = sha256_file(f(".ms.out"))
        refs["world_" + w] = c
    ac_ref = {}
    for stem, inp in input_sets(work)["ac4487"]:
        m = input_meta(inp)
        f = lambda e: os.path.join(AC4487_SOLVER, stem + e)  # noqa: E731
        c = classify_files(f(".ms.out"), f(".ms.log"), f(".ms.err"), m["p"], m["nvars"], "ok")
        c["out_sha256"] = sha256_file(f(".ms.out"))
        ac_ref[stem] = c
    # records
    recs = []
    for rp in sorted(glob.glob(os.path.join(work, "records", "*.jsonl"))):
        for ln in open(rp):
            recs.append(json.loads(ln))
    recs.sort(key=lambda r: (r["start_epoch"]))
    W = lambda p: p.replace("<work>", work)  # noqa: E731
    for r in recs:
        fo, fl, fe = W(r["files"]["out"]), W(r["files"]["log"]), W(r["files"]["err"])
        co = r["run_child"]["outcome"]
        r["output_sha256"] = sha256_file(fo) if os.path.exists(fo) else None
        r["log_sha256"] = sha256_file(fl) if os.path.exists(fl) else None
        r["err_sha256"] = sha256_file(fe) if os.path.exists(fe) else None
        r["classification"] = classify_files(fo, fl, fe, r["p"], r["nvars"], co)
        r["n_sub_fail"] = 0
        r["input_key"] = r["input_set"] + "/" + r["input"]   # toy and ac4487 stems coincide; key by set and stem
        r["n_sub_fail_note"] = "substitution not re-run (no descended system); n_sub_fail = 0 by the card (CH-5)"
    # modal outputs (default flags) per input over ok-exited solves; ties -> smallest sha256 (declared)
    def modal(rs):
        cnt = collections.Counter(r["output_sha256"] for r in rs if r["run_child"]["outcome"] == "ok" and r["output_sha256"])
        if not cnt:
            return None
        top = max(cnt.values())
        return sorted(s for s, v in cnt.items() if v == top)[0]
    def_rs = collections.defaultdict(list)
    for r in recs:
        if not r["flags"]:
            def_rs[r["input_key"]].append(r)
    modal_default = {k: modal(v) for k, v in def_rs.items()}
    parsed_by_sha = {}
    for r in recs:
        if r["output_sha256"] and r["run_child"]["outcome"] == "ok":
            parsed_by_sha.setdefault((r["input_key"], r["output_sha256"]), r["classification"])
    # class references
    for r in recs:
        c = r["class"]
        if c in ("C-1a", "C-1b"):
            rs, rk, rname = refs["world_B"]["out_sha256"], parsed_key(refs["world_B"]), "world_B output (bundle)"
        elif c == "C-2":
            rs, rk, rname = ac_ref[r["input"]]["out_sha256"], parsed_key(ac_ref[r["input"]]), "archived RUN-GFPN-ac4487 .ms.out"
        elif c == "C-1c":
            rs = modal_default.get(r["input_key"])
            rk = parsed_key(parsed_by_sha[(r["input_key"], rs)]) if rs else None
            rname = "modal output of this input under default flags"
        else:  # C-3c: default-flag modal output of the input; archived output recorded separately for ac4487 inputs
            rs = modal_default.get(r["input_key"])
            rk = parsed_key(parsed_by_sha[(r["input_key"], rs)]) if rs else None
            rname = "default-flag modal output of this input"
        r["reference"] = {"name": rname, "sha256": rs, "bytes_equal": (r["output_sha256"] == rs) if r["output_sha256"] else None,
                          "parsed_equal": (parsed_key(r["classification"]) == rk) if (rk and r["output_sha256"]) else None}
        if c == "C-3c":
            if r["input_set"] == "ac4487":
                r["reference"]["archived_ac4487_bytes_equal"] = r["output_sha256"] == ac_ref[r["input"]]["out_sha256"]
            if r["input_set"] == "event":
                r["reference"]["world_B_bytes_equal"] = r["output_sha256"] == refs["world_B"]["out_sha256"]
                r["reference"]["world_A_bytes_equal"] = r["output_sha256"] == refs["world_A"]["out_sha256"]
    # ---- planned counts, completeness
    planned = {lab: reps * len(input_sets(work)[s]) for lab, _c, s, reps, _p, _f in DESIGN}
    by_label = collections.defaultdict(list)
    for r in recs:
        by_label[r["label"]].append(r)
    labels = {}
    for lab, rs in sorted(by_label.items(), key=lambda kv: kv[1][0]["start_epoch"]):
        base = lab.split("-r")[0] if re.search(r"-r\d+$", lab) else lab
        cnt = collections.Counter(r["run_child"]["outcome"] for r in rs)
        ccnt = collections.Counter(r["classification"]["classify_outcome"] for r in rs)
        labels[lab] = {"class": rs[0]["class"], "planned": planned.get(base), "recorded": len(rs),
                       "complete": len(rs) == planned.get(base), "run_child_outcomes": dict(cnt),
                       "classify_outcomes": dict(ccnt), "nsp": sum(r["classification"]["nsp"] for r in rs),
                       "first_start_utc": rs[0]["start_utc"], "last_end_utc": rs[-1]["end_utc"],
                       "cap_readback_all_equal_cap": all((r["run_child"].get("rlimit_as_child_getrlimit") or {}).get("soft") == CAP
                                                         and (r["run_child"].get("rlimit_as_child_getrlimit") or {}).get("hard") == CAP for r in rs),
                       "bytes_differ_from_reference": sum(1 for r in rs if r["reference"]["bytes_equal"] is False),
                       "parsed_differ_from_reference": sum(1 for r in rs if r["reference"]["parsed_equal"] is False)}
    # ---- CR-2
    cr2 = {"classes": {}}
    for c in CR_CLASSES:
        cands = [lab for lab, v in labels.items() if v["class"] == c and v["complete"]]
        partial = [lab for lab, v in labels.items() if v["class"] == c and not v["complete"]]
        if not cands:
            cr2["classes"][c] = {"n_c": None, "x_c": None, "u_c": None, "status": "no complete label", "partial_labels": partial}
            continue
        lab = cands[-1]
        rs = by_label[lab]
        n = sum(1 for r in rs if r["run_child"]["outcome"] == "ok")
        x = sum(1 for r in rs if r["run_child"]["outcome"] == "ok" and r["classification"]["nsp"])
        cr2["classes"][c] = {"label_used": lab, "partial_labels_not_used": partial, "n_c": n, "x_c": x, "u_c": cp_upper(x, n),
                             "solves_recorded": len(rs), "solves_not_exited_ok": len(rs) - n}
    us = [v["u_c"] for v in cr2["classes"].values() if v["u_c"] is not None]
    all4 = all(cr2["classes"][c]["u_c"] is not None for c in CR_CLASSES)
    cr2["u_max"] = max(us) if us else None
    cr2["u_max_over_all_four_classes"] = all4
    sub = s_ub()
    cr2["S_ub"] = sub["S_ub"]
    cr2["S_ub_derivation"] = sub
    K = None
    tab = []
    if cr2["u_max"] is not None and all4:
        for k in (2, 3, 4, 5):
            v = sub["S_ub"] * cr2["u_max"] ** (k + 1)
            tab.append({"k": k, "S_ub_times_u_max_pow_k_plus_1": v, "le_0_01": v <= 0.01})
            if K is None and v <= 0.01:
                K = k
    cr2["K_table"] = tab
    cr2["K"] = K if K is not None else ("none" if all4 else "not computable: a class is incomplete")
    cr2["formula"] = "K = least k in {2,3,4,5} with S_ub * u_max^(k+1) <= 0.01; u_c = p with P(Binomial(n_c,p) <= x_c) = 0.05"
    # ---- CR-1 (per input, pooled over the four classes and all their labels; plus C-2 vs the archived output)
    cr1 = []
    per_input = collections.defaultdict(list)
    for r in recs:
        if r["class"] in CR_CLASSES and r["run_child"]["outcome"] == "ok":
            per_input[r["input_key"]].append(r)
    sid = lambda r: "%s#%d" % (r["label"], r["rep"])  # noqa: E731
    for inp, rs in sorted(per_input.items()):
        g = collections.defaultdict(list)
        for r in rs:
            g[r["classification"]["dimension_of_quotient_printed"]].append(r)
        if len(g) > 1:
            vals = sorted(g, key=str)
            cr1.append({"input": inp, "kind": "printed quotient dimension differs",
                        "groups": {str(v): {"count": len(g[v]), "first_solve": sid(g[v][0])} for v in vals},
                        "solve_pair": [sid(g[vals[0]][0]), sid(g[vals[1]][0])]})
        cl = collections.defaultdict(list)
        for r in rs:
            lab_ = "NSP" if r["classification"]["nsp"] else r["classification"]["classify_outcome"]
            if lab_ == "degenerate_parametrisation":
                lab_ = "degenerate_parametrisation(non-NSP reason)"
            cl[lab_].append(r)
        non = sorted(k for k in cl if k != "NSP")
        if len(non) > 1:
            cr1.append({"input": inp, "kind": "outcome class change other than to/from the NSP signature",
                        "groups": {k: {"count": len(cl[k]), "first_solve": sid(cl[k][0])} for k in sorted(cl)},
                        "solve_pair": [sid(cl[non[0]][0]), sid(cl[non[1]][0])]})
        okr = [r for r in rs if r["classification"]["classify_outcome"] == "ok"]
        pg = collections.defaultdict(list)
        for r in okr:
            c_ = r["classification"]
            pg[(c_["solution_set_sha256"], c_["elim_degree"], c_["D_as_driver_would_record"])].append(r)
        if len(pg) > 1:
            ks = list(pg)
            cr1.append({"input": inp, "kind": "two ok-classified outputs differ in parsed solution set, eliminating degree or D",
                        "groups": [{"solution_set_sha256": k[0], "elim_degree": k[1], "D": k[2], "count": len(pg[k]), "first_solve": sid(pg[k][0])} for k in ks],
                        "solve_pair": [sid(pg[ks[0]][0]), sid(pg[ks[1]][0])]})
        if inp.startswith("ac4487/"):
            rk = parsed_key(ac_ref[inp.split("/", 1)[1]])
            bad = [r for r in okr if r["class"] == "C-2" and parsed_key(r["classification"]) != rk]
            if bad:
                cr1.append({"input": inp, "kind": "ok-classified C-2 output disagrees in the SE-4 (d) parsed comparison with the archived RUN-GFPN-ac4487 output (CR-3: 'a parsed disagreement is CR-1')",
                            "count": len(bad), "solves": [sid(r) for r in bad][:50]})
    # ---- CR-3
    cr3_inst = []
    for inp in sorted(ac_ref):
        okr = [r for r in recs if r["class"] == "C-2" and r["input"] == inp and r["run_child"]["outcome"] == "ok"
               and r["classification"]["classify_outcome"] == "ok"]
        shas = collections.Counter(r["output_sha256"] for r in okr)
        arch = ac_ref[inp]["out_sha256"]
        rk = parsed_key(ac_ref[inp])
        if len(set(shas) | {arch}) > 1:
            for s in sorted(set(shas) | {arch}):
                if s == arch:
                    continue
                rs_ = [r for r in okr if r["output_sha256"] == s]
                agree = all(parsed_key(r["classification"]) == rk for r in rs_)
                if agree:
                    cr3_inst.append({"input": inp, "output_sha256": s, "archived_sha256": arch, "count": len(rs_),
                                     "solves": [sid(r) for r in rs_][:50], "parsed_comparison": "agrees"})
    cr3 = {"branch": "d-parsed" if cr3_inst else "d-bytes", "instances": cr3_inst,
           "rule": "d-parsed iff for some C-2 input an ok-classified output differs in bytes from another ok-classified output of the same input or from the archived .ms.out while its SE-4 (d) parsed comparison agrees; otherwise d-bytes (CR-3)"}
    # ---- time structure (observations for the independence assumption; no reading)
    timing = {}
    for lab in labels:
        rs = sorted(by_label[lab], key=lambda r: r["start_epoch"])
        same_sec_pairs = [(a, b) for a, b in zip(rs, rs[1:]) if a["input_key"] == b["input_key"]
                          and int(a["start_epoch"]) == int(a["end_epoch"]) == int(b["start_epoch"]) == int(b["end_epoch"])]
        gaps = [b["start_epoch"] - a["end_epoch"] for a, b in zip(rs, rs[1:])]
        secs = collections.Counter(int(r["start_epoch"]) for r in rs)
        nsp_idx = [i for i, r in enumerate(rs) if r["classification"]["nsp"]]
        timing[lab] = {
            "children_per_start_second": dict(collections.Counter(secs.values())),
            "distinct_start_seconds": len(secs),
            "min_gap_end_to_next_start_s": round(min(gaps), 6) if gaps else None,
            "median_child_wall_s": sorted(r["run_child"].get("wall_seconds") or 0 for r in rs)[len(rs) // 2] if rs else None,
            "consecutive_pairs_both_children_within_one_utc_second": len(same_sec_pairs),
            "of_which_identical_output_bytes": sum(1 for a, b in same_sec_pairs if a["output_sha256"] == b["output_sha256"]),
            "nsp_solves": [{"solve": sid(rs[i]), "input": rs[i]["input_key"], "start_utc": rs[i]["start_utc"], "end_utc": rs[i]["end_utc"]} for i in nsp_idx],
            "nsp_adjacent_pairs": sum(1 for i, j in zip(nsp_idx, nsp_idx[1:]) if j == i + 1)}
    # ---- distinct outputs per input
    distinct = collections.defaultdict(lambda: collections.defaultdict(list))
    for r in recs:
        if r["output_sha256"]:
            distinct[r["input_key"]][r["output_sha256"]].append(sid(r))
    distinct_summary = {inp: {s: {"count": len(v), "flags_labels": sorted(set(x.split("#")[0] for x in v)),
                                  "classify_outcome": (parsed_by_sha.get((inp, s)) or {}).get("classify_outcome"),
                                  "nsp": (parsed_by_sha.get((inp, s)) or {}).get("nsp")} for s, v in d.items()}
                        for inp, d in sorted(distinct.items())}
    # ---- C-3 (a)
    c3a = {}
    for w in "AB":
        c = refs["world_" + w]
        c3a["world_" + w] = {k: c[k] for k in ("header", "elim_degree", "elim_squarefree", "dimension_of_quotient_printed",
                                                "squarefree_degree_printed", "minpoly_degree_reported", "classify_outcome",
                                                "classify_reason", "nsp", "out_sha256")}
    diffs = {}
    for ext in (".ms.log", ".ms.err"):
        a = (read_text(os.path.join(bdir, TOY_REL % "A", EVENT_STEM + ext)) or "").splitlines(keepends=True)
        b = (read_text(os.path.join(bdir, TOY_REL % "B", EVENT_STEM + ext)) or "").splitlines(keepends=True)
        diffs[ext] = "".join(difflib.unified_diff(a, b, fromfile="world_A/" + EVENT_STEM + ext, tofile="world_B/" + EVENT_STEM + ext))
    c3a["unified_diff_sha256"] = {k: sha256_bytes(v.encode()) for k, v in diffs.items()}
    # ---- C-3 (b), (c)
    c3b = json.load(open(os.path.join(work, "c3b", "c3b.json"))) if os.path.exists(os.path.join(work, "c3b", "c3b.json")) else None
    c3c = {}
    for lab, v in labels.items():
        if v["class"] != "C-3c":
            continue
        rs = by_label[lab]
        c3c[lab] = {"recorded": len(rs), "planned": v["planned"], "run_child_outcomes": v["run_child_outcomes"],
                    "classify_outcomes": v["classify_outcomes"], "nsp": v["nsp"],
                    "bytes_equal_default_flag_modal": sum(1 for r in rs if r["reference"]["bytes_equal"]),
                    "archived_ac4487_bytes_equal": sum(1 for r in rs if r["reference"].get("archived_ac4487_bytes_equal")),
                    "world_B_bytes_equal": sum(1 for r in rs if r["reference"].get("world_B_bytes_equal")),
                    "world_A_bytes_equal": sum(1 for r in rs if r["reference"].get("world_A_bytes_equal")),
                    "distinct_outputs": len(set(r["output_sha256"] for r in rs if r["output_sha256"])),
                    "per_input_distinct": {inp: len(set(r["output_sha256"] for r in rs if r["input_key"] == inp and r["output_sha256"]))
                                           for inp in sorted(set(r["input_key"] for r in rs))}}
    summary = {"task": "TASK-20260923-6599cf", "experiment_id": "EXP-GFPN-05ff43", "kind": "zero-run development characterization",
               "run_packages_created": 0, "analyzed_at": utc(time.time()), "harness": rel(os.path.abspath(__file__)),
               "harness_sha256": sha256_file(os.path.abspath(__file__)),
               "design": [{"label": l, "class": c, "input_set": s, "reps_per_input": n, "pace_s": p, "extra_flags": f,
                           "planned_solves": planned[l]} for l, c, s, n, p, f in DESIGN],
               "cap_bytes": CAP, "run_child_timeout_s": TIMEOUT_S, "integrity": integ, "labels": labels,
               "CR-2": cr2, "CR-1": {"instances": cr1, "n_instances": len(cr1)}, "CR-3": cr3,
               "time_structure": timing, "distinct_outputs": distinct_summary,
               "references": {"world_A": refs["world_A"], "world_B": refs["world_B"], "ac4487": ac_ref},
               "C-3a": c3a, "C-3b": c3b, "C-3c": c3c, "C-4": census(),
               "labels_note": "Observations only. D_as_driver_would_record values are harness parameters (toy) or archived RUN-GFPN-ac4487 values re-observed (4111), never results.",
               "total_children": len(recs)}
    os.makedirs(outdir, exist_ok=True)
    # solves.jsonl
    with open(os.path.join(outdir, "solves.jsonl"), "w") as fh:
        for r in recs:
            rr = dict(r)
            rr.pop("start_epoch", None)
            rr.pop("end_epoch", None)
            fh.write(json.dumps(rr, sort_keys=True) + "\n")
    dump(os.path.join(outdir, "summary.json"), summary)
    # distinct-outputs.tar.gz (CH-7), deterministic
    members = []
    seen = set()
    for r in recs:
        if r["output_sha256"] and (r["input_key"], r["output_sha256"]) not in seen:
            seen.add((r["input_key"], r["output_sha256"]))
            members.append(("distinct-outputs/%s/%s.ms.out" % (r["input_key"], r["output_sha256"]), W(r["files"]["out"])))
        keep_log = r["classification"]["nsp"] or r["reference"]["bytes_equal"] is False
        if keep_log:
            for k in ("log", "err"):
                members.append(("logs/%s/%s/r%04d.%s" % (r["label"], r["input_key"], r["rep"], "ms." + k), W(r["files"][k])))
    idx = {inp: {s: v for s, v in d.items()} for inp, d in distinct.items()}
    extra = {"distinct-outputs/index.json": json.dumps(idx, indent=1, sort_keys=True).encode(),
             "c3a/world_A_vs_world_B.ms.log.diff": diffs[".ms.log"].encode(),
             "c3a/world_A_vs_world_B.ms.err.diff": diffs[".ms.err"].encode()}
    if os.path.exists(os.path.join(work, "c3b", "msolve-h.stdout")):
        members.append(("c3b/msolve-h.stdout", os.path.join(work, "c3b", "msolve-h.stdout")))
        members.append(("c3b/msolve-h.stderr", os.path.join(work, "c3b", "msolve-h.stderr")))
    tpath = os.path.join(outdir, "distinct-outputs.tar.gz")
    import gzip
    with open(tpath, "wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as gz:
            with tarfile.open(fileobj=gz, mode="w", format=tarfile.PAX_FORMAT) as tf:
                def add(name, data):
                    ti = tarfile.TarInfo(name)
                    ti.size, ti.mtime, ti.mode, ti.uid, ti.gid, ti.uname, ti.gname = len(data), 0, 0o644, 0, 0, "", ""
                    tf.addfile(ti, io.BytesIO(data))
                for name, path in sorted(set(members)):
                    if os.path.exists(path):
                        add(name, open(path, "rb").read())
                for name in sorted(extra):
                    add(name, extra[name])
    print(json.dumps({"CR-2": {c: {k: v.get(k) for k in ("n_c", "x_c", "u_c")} for c, v in cr2["classes"].items()},
                      "u_max": cr2["u_max"], "S_ub": cr2["S_ub"], "K": cr2["K"], "CR-1_instances": len(cr1),
                      "CR-3": cr3["branch"], "total_children": len(recs)}, indent=1, default=str))


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    a = sp.add_parser("integrity")
    a.add_argument("--work", required=True)
    b = sp.add_parser("run")
    b.add_argument("--work", required=True)
    b.add_argument("--labels", default=None, help="comma list of design labels (default: all, C-3b first)")
    b.add_argument("--suffix", default="", help="CH-9 restart label suffix, e.g. -r2")
    c = sp.add_parser("analyze")
    c.add_argument("--work", required=True)
    c.add_argument("--out", required=True)
    args = ap.parse_args()
    {"integrity": cmd_integrity, "run": cmd_run, "analyze": cmd_analyze}[args.cmd](args)


if __name__ == "__main__":
    main()
