#!/usr/bin/env python3
"""EXP-SEMBIN-35bf67 orchestrator: instances -> exact s -> dual-arm SOLV4 -> records.

Per instance (OP-INSTANCE / OP-S / OP-SOLV4 / OP-DUAL / OP-CAPS):
  1. build the descended system (builder.py), record its sha256 (file not retained;
     regenerable from the recorded seed namespace);
  2. s: primary -> S-A and S-B (+ S-C when N <= 30), solution SETS must coincide;
     null -> S-C only (Gray-code exhaustive, split over 2^T prefixes);
  3. SOLV4 by arm A (M4RI) and arm B (own kernels) as separate processes, each under
     RLIMIT_CPU = 28800 s and an 8 GiB RSS watchdog;
  4. agreement = identical dim_R4, closure rounds, product rounds, chunk-rank trajectory
     and per-round low-space digests. Any difference -> instance flagged ARTIFACT.
Records are appended to instances.jsonl (resumable); nothing is overwritten.
"""
import hashlib
import json
import os
import resource
import shutil
import signal
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import builder  # noqa: E402

BIN = os.environ.get("SEMBIN_BIN", "")
WORK = os.environ.get("SEMBIN_WORK", "")
CPU_CAP = 28800
RSS_CAP = 8 * 2**30
CH = 8192
SUB = {"A": 2048, "B": 1024}
_lock = threading.Lock()


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def _limits():
    resource.setrlimit(resource.RLIMIT_CPU, (CPU_CAP, CPU_CAP + 60))
    os.setsid()


def run_capped(cmd, log_prefix):
    """Run cmd with CPU cap and RSS watchdog. Returns dict(rc, censored, reason, peak_rss)."""
    t0 = time.time()
    with open(log_prefix + ".out", "w") as fo, open(log_prefix + ".err", "w") as fe:
        p = subprocess.Popen(cmd, stdout=fo, stderr=fe, preexec_fn=_limits)
        peak, killed = 0, None
        while p.poll() is None:
            try:
                with open("/proc/%d/status" % p.pid) as st:
                    for line in st:
                        if line.startswith("VmRSS:"):
                            rss = int(line.split()[1]) * 1024
                            peak = max(peak, rss)
                            if rss > RSS_CAP:
                                killed = "rss_cap_8GiB"
                                os.killpg(p.pid, signal.SIGKILL)
            except (FileNotFoundError, ProcessLookupError):
                pass
            time.sleep(0.5)
        rc = p.returncode
    censored, reason = False, None
    if killed:
        censored, reason = True, killed
    elif rc == -signal.SIGXCPU or rc == -signal.SIGKILL and not killed:
        censored, reason = True, "cpu_cap_28800s_or_killed(rc=%d)" % rc
    elif rc != 0:
        reason = "nonzero_exit_%d" % rc
    return {"rc": rc, "censored": censored, "reason": reason, "watch_peak_rss": peak,
            "wall": round(time.time() - t0, 3)}


def read_points(p):
    with open(p) as fh:
        lines = [l.strip() for l in fh if l.strip() and not l.startswith("#")]
    return lines


def instance_files(rec_dir, tag):
    d = os.path.join(WORK, rec_dir)
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, tag)


def make_system(cell, stage, arm, i, workdir):
    if arm == "primary":
        inst = builder.primary_instance(tuple(cell), stage, i)
    else:
        inst = builder.null_instance(tuple(cell), stage, i)
    sysp = os.path.join(workdir, "sys_%s_%d.txt" % (arm, i))
    nzero = builder.write_system(sysp, inst["N"], inst["equations"],
                                 {"cell": cell, "stage": stage, "arm": arm, "index": i})
    return inst, sysp, nzero


def count_primary(inst, sysp, workdir, i):
    n, m, t, k = inst["cell"]
    out = {}
    sets = {}
    meths = ["A", "B"]
    for meth in meths:
        pf = os.path.join(workdir, "pts_%s_%d" % (meth, i))
        t0 = time.time()
        r = subprocess.run([BIN + "/sols", meth, str(n), "%x" % inst["f"], str(k), str(t),
                            "%x" % inst["B"], "%x" % inst["z"], "%x" % inst["A"], pf],
                           capture_output=True, text=True)
        if r.returncode != 0:
            out["S-" + meth] = {"error": r.stderr[-500:]}
            sets[meth] = None
            continue
        pts = read_points(pf)
        sets[meth] = pts
        out["S-" + meth] = {"count": len(pts), "seconds": round(time.time() - t0, 3)}
    if inst["N"] <= 30:
        pf = os.path.join(workdir, "pts_C_%d" % i)
        t0 = time.time()
        r = subprocess.run([BIN + "/exhaust", sysp, "0", "0", pf], capture_output=True, text=True)
        if r.returncode == 0:
            sets["C"] = read_points(pf)
            out["S-C"] = {"count": len(sets["C"]), "seconds": round(time.time() - t0, 3)}
        else:
            sets["C"] = None
            out["S-C"] = {"error": r.stderr[-500:]}
    vals = [v for v in sets.values()]
    agree = all(v is not None for v in vals) and all(v == vals[0] for v in vals)
    pts = sets["A"] if agree else None
    return out, agree, pts


def count_null(inst, sysp, workdir, i, T):
    t0 = time.time()
    procs, files = [], []
    for pre in range(2 ** T):
        pf = os.path.join(workdir, "npts_%d_%d" % (i, pre))
        files.append(pf)
        procs.append(subprocess.Popen([BIN + "/exhaust", sysp, str(T), "%x" % pre, pf],
                                      stdout=subprocess.DEVNULL, stderr=subprocess.PIPE))
    ok = True
    for p in procs:
        p.wait()
        ok = ok and p.returncode == 0
    pts = []
    if ok:
        for pf in files:
            pts.extend(read_points(pf))
    pts.sort(key=lambda x: int(x, 16))
    return {"S-C": {"count": len(pts) if ok else None, "seconds": round(time.time() - t0, 3),
                    "split_T": T, "ok": ok}}, ok, (pts if ok else None)


def solv4_dual(sysp, ptsp, workdir, tag):
    res = {}
    threads = []

    def go(arm):
        outp = os.path.join(workdir, "%s_%s.json" % (tag, arm))
        cap = run_capped([BIN + "/solv4_" + arm, "closure", sysp, ptsp, outp, str(CH), str(SUB[arm])],
                         os.path.join(workdir, "%s_%s" % (tag, arm)))
        js = None
        if cap["rc"] == 0 and os.path.exists(outp):
            with open(outp) as fh:
                js = json.load(fh)
        res[arm] = {"cap": cap, "json": js, "path": outp}

    for arm in ("A", "B"):
        th = threading.Thread(target=go, args=(arm,))
        th.start()
        threads.append(th)
    for th in threads:
        th.join()
    return res


AGREE_KEYS = ["dim_R4", "closure_round_count", "product_rounds_run", "stopped_early", "verdict",
              "total_rows_inserted", "chunk_rank_trajectory", "rows0", "M_le4", "eval_rank_rE"]


def compare_arms(a, b):
    if a is None or b is None:
        return False, ["missing_arm_output"]
    diffs = [k for k in AGREE_KEYS if a.get(k) != b.get(k)]
    da = [(x["round"], x["rows"], x["rank_after"], x["new_low"], x["digest"]) for x in a["rounds"]]
    db = [(x["round"], x["rows"], x["rank_after"], x["new_low"], x["digest"]) for x in b["rounds"]]
    if da != db:
        diffs.append("rounds")
    return not diffs, diffs


def summarize_arm(r):
    js = r["json"]
    s = {"cap": r["cap"], "output_sha256": sha256_file(r["path"]) if js else None}
    if js:
        for k in ("dim_R4", "closure_round_count", "product_rounds_run", "stopped_early", "verdict",
                  "solv4", "total_rows_inserted", "wall_seconds", "cpu_seconds", "peak_rss_bytes",
                  "peak_R_bytes", "kernel", "points_failing_system", "eval_rank_rE", "target_rank",
                  "M_minus_dim"):
            s[k] = js.get(k)
    return s


def process_instance(run_dir, cell, stage, arm, i, workdir, stratum_hint=None, null_T=0,
                     pre=None):
    """Full pipeline for one instance. pre = (inst, sysp, nzero, s_info, agree, pts) if
    already classified. Returns the record dict (also appended to instances.jsonl)."""
    t0 = time.time()
    workdir = os.path.join(workdir, "%s_%d" % (arm, i))
    os.makedirs(workdir, exist_ok=True)
    if pre is None:
        inst, sysp, nzero = make_system(cell, stage, arm, i, workdir)
        if arm == "primary":
            s_info, agree, pts = count_primary(inst, sysp, workdir, i)
        else:
            s_info, agree, pts = count_null(inst, sysp, workdir, i, null_T)
    else:
        inst, sysp, nzero, s_info, agree, pts = pre
    rec = {"cell": cell, "stage": stage, "arm": arm, "index": i, "N": inst["N"],
           "f": "%x" % inst["f"], "B": "%x" % inst["B"], "z": "%x" % inst["z"],
           "system_sha256": sha256_file(sysp), "zero_equations_dropped": nzero,
           "s_methods": s_info, "s_agree": agree}
    if not agree:
        rec.update({"s": None, "stratum": None, "status": "ARTIFACT_s_mismatch_or_error"})
    else:
        s = len(pts)
        rec["s"] = s
        rec["stratum"] = "SAT" if s > 0 else "UNSAT"
        ptsp = os.path.join(workdir, "points_%s_%d.txt" % (arm, i))
        with open(ptsp, "w") as fh:
            fh.write("# s=%d\n" % s)
            for x in pts:
                fh.write(x + "\n")
        rec["points_sha256"] = sha256_file(ptsp)
        if s:
            sol_dir = os.path.join(run_dir, "solutions")
            os.makedirs(sol_dir, exist_ok=True)
            with open(os.path.join(sol_dir, "%s_%d.txt" % (arm, i)), "w") as fh:
                fh.write("# cell=%s stage=%s arm=%s index=%d s=%d (hex Boolean assignments)\n"
                         % (cell, stage, arm, i, s))
                for x in pts:
                    fh.write(x + "\n")
        tag = "%s_%d" % (arm, i)
        res = solv4_dual(sysp, ptsp, workdir, tag)
        arms_dir = os.path.join(run_dir, "arms")
        os.makedirs(arms_dir, exist_ok=True)
        for a in ("A", "B"):
            if res[a]["json"] is not None:
                with open(res[a]["path"]) as src, open(os.path.join(arms_dir, "%s_%s.json" % (tag, a)), "w") as dst:
                    dst.write(src.read())
        rec["arm_A"] = summarize_arm(res["A"])
        rec["arm_B"] = summarize_arm(res["B"])
        censored = res["A"]["cap"]["censored"] or res["B"]["cap"]["censored"]
        failed = (res["A"]["json"] is None or res["B"]["json"] is None) and not censored
        if censored:
            rec["status"] = "CENSORED"
        elif failed:
            rec["status"] = "FAILED_INFRASTRUCTURE"
        else:
            ok, diffs = compare_arms(res["A"]["json"], res["B"]["json"])
            rec["dual_rank_agree"] = ok
            rec["dual_rank_diffs"] = diffs
            ja = res["A"]["json"]
            if not ok:
                rec["status"] = "ARTIFACT_dual_rank_disagreement"
            elif ja["points_failing_system"] != 0:
                rec["status"] = "ARTIFACT_points_fail_system"
            elif ja["verdict"] not in ("SOLV4", "NOT_SOLV4", "fixpoint_at_target_but_rE_lt_s"):
                rec["status"] = "ARTIFACT_" + ja["verdict"]
            else:
                rec["status"] = "VALID"
                rec["solv4"] = ja["solv4"] == 1
                rec["dim_R4"] = ja["dim_R4"]
                rec["M_le4"] = ja["M_le4"]
                rec["closure_round_count"] = ja["closure_round_count"]
                rec["eval_rank_rE"] = ja["eval_rank_rE"]
                rec["stopped_early"] = ja["stopped_early"]
    shutil.rmtree(workdir, ignore_errors=True)
    rec["instance_wall_seconds"] = round(time.time() - t0, 3)
    rec["finished_at_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with _lock:
        with open(os.path.join(run_dir, "instances.jsonl"), "a") as fh:
            fh.write(json.dumps(rec, sort_keys=True) + "\n")
    return rec


def load_done(run_dir):
    p = os.path.join(run_dir, "instances.jsonl")
    done = {}
    if os.path.exists(p):
        with open(p) as fh:
            for line in fh:
                r = json.loads(line)
                done[(r["arm"], r["index"])] = r
    return done


def classify(run_dir, cell, stage, i, workdir):
    """Primary instance classification (s) without SOLV4; cached in classify.jsonl."""
    wd = os.path.join(workdir, "classify_%d" % i)
    os.makedirs(wd, exist_ok=True)
    inst, sysp, nzero = make_system(cell, stage, "primary", i, wd)
    s_info, agree, pts = count_primary(inst, sysp, wd, i)
    shutil.rmtree(wd, ignore_errors=True)
    rec = {"index": i, "agree": agree, "s": len(pts) if agree else None, "s_methods": s_info,
           "solution_set_sha256": hashlib.sha256("\n".join(pts).encode()).hexdigest() if agree else None}
    with _lock:
        with open(os.path.join(run_dir, "classify.jsonl"), "a") as fh:
            fh.write(json.dumps(rec, sort_keys=True) + "\n")
    return rec, (inst, sysp, nzero, s_info, agree, pts)


def run_primary_cell(run_dir, cell, stage, targets, deadline, workers=2, batch=24, max_index=4000):
    """OP-ORDER: classify in index order, run SOLV4 alternating next SAT / next UNSAT."""
    workdir = os.path.join(WORK, os.path.basename(run_dir))
    os.makedirs(workdir, exist_ok=True)
    done = load_done(run_dir)
    cls = {}
    cp = os.path.join(run_dir, "classify.jsonl")
    if os.path.exists(cp):
        with open(cp) as fh:
            for line in fh:
                r = json.loads(line)
                cls[r["index"]] = r
    next_cls = max(cls) + 1 if cls else 0
    # ordered run list
    def order():
        sat = [i for i in sorted(cls) if cls[i]["agree"] and cls[i]["s"] > 0]
        uns = [i for i in sorted(cls) if cls[i]["agree"] and cls[i]["s"] == 0]
        bad = [i for i in sorted(cls) if not cls[i]["agree"]]
        out = []
        for j in range(max(len(sat), len(uns))):
            if j < len(sat) and j < targets["SAT"]:
                out.append(sat[j])
            if j < len(uns) and j < targets["UNSAT"]:
                out.append(uns[j])
        return out, bad, len(sat), len(uns)
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {}
        while True:
            if time.time() > deadline:
                break
            ordered, bad, nsat, nuns = order()
            for i in bad:  # s mismatch: record as artifact instance (no SOLV4)
                if ("primary", i) not in done:
                    done[("primary", i)] = process_instance(run_dir, cell, stage, "primary", i, workdir)
            pending = [i for i in ordered if ("primary", i) not in done and i not in futs]
            need_more = (nsat < targets["SAT"] or nuns < targets["UNSAT"]) and next_cls < max_index
            if not pending and need_more:
                for _ in range(batch):
                    rec, _pre = classify(run_dir, cell, stage, next_cls, workdir)
                    cls[next_cls] = rec
                    next_cls += 1
                continue
            if not pending and not futs:
                break
            while pending and len(futs) < workers and time.time() < deadline:
                i = pending.pop(0)
                futs[i] = ex.submit(process_instance, run_dir, cell, stage, "primary", i, workdir)
            # wait for one to finish
            if futs:
                while all(not f.done() for f in futs.values()):
                    time.sleep(1)
                for i in [i for i, f in futs.items() if f.done()]:
                    done[("primary", i)] = futs.pop(i).result()
        for i, f in futs.items():
            done[("primary", i)] = f.result()
    return done


def run_null_cell(run_dir, cell, stage, target, deadline, T, workers=1):
    workdir = os.path.join(WORK, os.path.basename(run_dir))
    os.makedirs(workdir, exist_ok=True)
    done = load_done(run_dir)
    i = 0
    while i < target and time.time() < deadline:
        if ("null", i) not in done:
            done[("null", i)] = process_instance(run_dir, cell, stage, "null", i, workdir, null_T=T)
        i += 1
    return done
