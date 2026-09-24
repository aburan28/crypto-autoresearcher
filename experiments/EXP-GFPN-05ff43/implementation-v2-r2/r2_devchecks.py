#!/usr/bin/env python3
"""EXP-GFPN-05ff43 successor stage (TASK-20260923-de3a7d) -- DEVELOPMENT CHECKS (paristack PS-6 DV-1..DV-10 with
DEC-20260923-80e280 RC-2..RC-5, RC-7..RC-10 re-pointed to r2; solverevent SE-8 with seedresolve SF-6 and
DEC-20260924-15a77a SC-3, SC-5, SC-6). Started from implementation-v2-r1/r1_devchecks.py. Development only: never
imported by an entry point, the wrapper or the checker. Every output goes under --out (the session scratchpad).

usage: python3 -B r2_devchecks.py {dv2,dv3,semantics,dv1,dv5,dv6,dv8,dv9,dv10,dv11,dv12,dv15} --out DIR [...]

No ladder cell, build, fixture system or anchor system is solved at any ladder or fixture prime. The group
orders of the three fixture curves ARE computed (DV-2, DV-3): they are parameters, not results.
Every capped child (gp) runs through v2_solver.run_child: RLIMIT_AS 10737418240 set in the child and read
back with getrlimit before exec; one memory-heavy process at a time (sequential); no outer guard.
"""
import argparse
import json
import math
import os
import random
import subprocess
import sys
import time

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import r2_common as R                                    # noqa: E402

DV2_POINTS = [(4111, 3), (16777291, 3), (4111, 4)]
KNOWN_N_4111_3 = 69477519282                             # RUN-GFPN-ac4487 (execution-report-v2.yaml line 100)
GP = "/usr/bin/gp"


def dump(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        json.dump(obj, fh, indent=1, default=str)


def child_env():
    return dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONUNBUFFERED="1")


# ============================================================================ DV-2 / DV-3 workers (fresh processes)
def fixture_objects(C, p, n):
    if n == 3:
        fx = C.fixture_n3(p)
        stream = "%d:v2:fixture:%d:basepoint" % (C.SEED_CURVES, p)            # v2_driver.py line 309
    else:
        fx = C.fixture_n4()
        assert fx["F"].p == p
        stream = "%d:v2:fixture4:%d:basepoint" % (C.SEED_CURVES, p)           # v2_driver.py line 543
    return fx, stream


def hasse_ok(N, q):
    d = N - (q + 1)
    return d * d <= 4 * q                                                       # |N-(q+1)| <= 2 sqrt(q), integers


def worker_dv2(p, n, out):
    """Runs the layer's configuration EXACTLY as r2_entry_v2 does up to dispatch (PS-1 P-A, the RC-3 redirections,
    the SE-3 replacement and its read-back, the RC-2 start read-back), then calls the UNCHANGED
    v2_common.curve_order_pari on the objects built by the unchanged v2_common.fixture_n3 / fixture_n4."""
    stack = R.PariStack()
    stack.configure()
    sys.path.insert(0, R.V2_DIR)
    import v2_common as C
    C.PLAN_PATH = R.PLAN_V2_R2
    C.TASK_ID = R.TASK_RUNS_V2
    import v2_driver as D                                # as the entry imports it
    import r2_resolve as RS
    scratch_rd = os.path.join(os.path.dirname(out), os.path.basename(out) + ".rundir")
    os.makedirs(scratch_rd, exist_ok=True)
    RS.install(D, scratch_rd)
    import v2_solver as V
    redir, reasons = R.check_redirections({"v2_common.PLAN_PATH": R.PLAN_V2_R2, "v2_common.TASK_ID": R.TASK_RUNS_V2})
    se3, se3_reasons = RS.readback(D)
    reasons += se3_reasons
    redir["v2_driver.solve (SE-3 replacement)"] = dict(se3, equal=not se3_reasons)
    reasons += stack.start_readback()
    rec = {"point": {"p": p, "n": n}, "pid": os.getpid(), "PYTHONHASHSEED": os.environ.get("PYTHONHASHSEED"),
           "start_refusal_reasons": reasons, "redirections": redir}
    fx, stream = fixture_objects(C, p, n)
    F, E = fx["F"], fx["E"]
    q = F.p ** F.n
    rec["field"] = F.describe()
    rec["curve"] = fx["cv"].get("model")
    rec["readback_before_call"] = stack._read(stack.handle)
    rec["proc_status_before_call"] = R.proc_status()
    t0 = time.time()
    try:
        N = C.curve_order_pari(F, E)
        rec["call"] = {"returned": True, "N": N}
    except Exception as e:                               # noqa: BLE001
        N = None
        rec["call"] = {"returned": False, "exception_type": type(e).__name__, "exception": str(e)}
    rec["wall_seconds"] = round(time.time() - t0, 3)
    rec["readback_after_call"] = stack._read(stack.handle)
    rec["proc_status_after_call"] = R.proc_status()
    rec["DV4_self_rss_bytes_v2_solver"] = V.self_rss_bytes()
    rec["DV4_below_1GiB"] = rec["DV4_self_rss_bytes_v2_solver"] < R.DRIVER_RSS_LIMIT
    if N is not None:
        G = E.random_point(random.Random(stream))
        rec["basepoint_stream"] = "random.Random('%s')" % stream
        rec["N_times_basepoint_is_O"] = E.mul(N, G) is None
        s2 = "2026092002:v2r2:dv2:%d:%d" % (p, n)                             # RC-5 (ii) declared development stream
        P2 = E.random_point(random.Random(s2))
        rec["second_point_stream"] = "random.Random('%s')" % s2
        rec["N_times_second_point_is_O"] = E.mul(N, P2) is None
        rec["second_point_differs_from_basepoint"] = P2 != G
        rec["hasse_interval"] = {"q": q, "q_plus_1": q + 1, "N_minus_q_minus_1": N - q - 1, "holds": hasse_ok(N, q)}
        rec["serialisation"] = {"modulus": list(F.modulus), "a2": F.coeffs(E.a2), "a4": F.coeffs(E.a4), "a6": F.coeffs(E.a6)}
    ex = stack.exit_readback()
    rec["exit_readback"] = ex
    rec["pari_stack_record"] = stack.rec
    dump(out, rec)
    return 0


def worker_dv3(p, n, out):
    """Negative control: a fresh process WITHOUT the layer's configuration."""
    sys.path.insert(0, R.V2_DIR)
    import v2_common as C
    fx, _ = fixture_objects(C, p, n)
    import cypari2
    h = cypari2.Pari()
    rec = {"point": {"p": p, "n": n}, "configuration_applied": False, "pid": os.getpid(),
           "readback_before_call": {"parisize": int(h.default("parisize")), "parisizemax": int(h.default("parisizemax"))}}
    t0 = time.time()
    try:
        N = C.curve_order_pari(fx["F"], fx["E"])
        rec["call"] = {"returned": True, "N": N}
    except Exception as e:                               # noqa: BLE001
        rec["call"] = {"returned": False, "exception_type": type(e).__name__, "exception": str(e)}
    rec["wall_seconds"] = round(time.time() - t0, 3)
    rec["proc_status_after_call"] = R.proc_status()
    msg = rec["call"].get("exception", "")
    rec["reproduces_RUN_GFPN_3377f1"] = (not rec["call"]["returned"]) and "ellcard: the PARI stack overflows" in msg
    dump(out, rec)
    return 0


def worker_semantics(out):
    """RC-2 (b): what default(parisize) reports after the stack GREW, under the layer's configuration. A plain
    PARI allocation (no experiment object) forces growth beyond 64 MiB."""
    stack = R.PariStack()
    stack.configure()
    import cypari2
    h = cypari2.Pari()
    rec = {"before": stack._read(h), "proc_status_before": R.proc_status()}
    v = h("my(v = vector(4000000, i, i^2 + 2^70)); #v")
    rec["computation"] = "my(v = vector(4000000, i, i^2 + 2^70)); #v  (about 4e6 t_INT of 4 words + the vector: > 64 MiB of stack)"
    rec["result"] = int(v)
    rec["after_same_handle"] = stack._read(h)
    rec["proc_status_after"] = R.proc_status()
    h2 = cypari2.Pari()
    rec["after_fresh_handle_constructed"] = stack._read(h2)
    rec["grew"] = rec["after_same_handle"]["stacksize_current"] > R.PARISIZE
    rec["default_parisize_after_growth"] = rec["after_same_handle"]["parisize"]
    rec["semantics"] = ("requested" if rec["after_same_handle"]["parisize"] == R.PARISIZE else "current_grown") if rec["grew"] else "not_established_no_growth"
    dump(out, rec)
    return 0


# ============================================================================ gp cross-check in a capped child (RC-5)
def gp_expr(ser, p):
    M = " + ".join("%d*w^%d" % (c, i) for i, c in enumerate(ser["modulus"]) if c)

    def poly(cs):
        s = " + ".join("%d*w^%d" % (c, i) for i, c in enumerate(cs) if c)
        return s or "0"
    return ("my(g = ffgen(Mod(1, %d)*(%s), 'w)); my(E = ellinit([0, subst(%s, 'w, g), 0, subst(%s, 'w, g), subst(%s, 'w, g)])); ellcard(E)"
            % (p, M, poly(ser["a2"]), poly(ser["a4"]), poly(ser["a6"])))


def gp_crosscheck(ser, p, n, odir, tag):
    sys.path.insert(0, R.V2_DIR)
    import v2_solver as V
    os.makedirs(odir, exist_ok=True)
    script = os.path.join(odir, tag + ".gp")
    with open(script, "w") as fh:
        fh.write("default(parisize, 256000000);\ndefault(parisizemax, 4000000000);\n")   # a1_pari.py line 38
        fh.write('print("R2GP N=", %s);\nquit;\n' % gp_expr(ser, p))
    argv = [GP, "-q", "-f", "--default", "nbthreads=1", script]
    so, se = os.path.join(odir, tag + ".stdout"), os.path.join(odir, tag + ".stderr")
    rec = V.run_child(argv, so, se, cap_bytes=R.CAP_BYTES, timeout_s=7200, count_instructions=False)
    N = None
    for line in open(so, errors="replace"):
        if line.startswith("R2GP N="):
            N = int(line.split("=", 1)[1])
    return {"argv": argv, "script": script, "script_sha256": R.sha256_file(script),
            "child": {k: rec.get(k) for k in ("outcome", "returncode", "timed_out", "wall_seconds", "rlimit_as_child_getrlimit",
                                               "rlimit_as_proc_limits_after_exec", "peak_rss_bytes", "peak_vm_bytes", "refusal_reason")},
            "N": N}


# ============================================================================ orchestrators
def run_worker(args_list, log_path):
    cmd = [sys.executable, "-B", os.path.abspath(__file__)] + args_list
    with open(log_path + ".stdout", "w") as so, open(log_path + ".stderr", "w") as se:
        pr = subprocess.run(cmd, env=child_env(), stdout=so, stderr=se)
    tail = open(log_path + ".stderr", errors="replace").read().splitlines()[-50:]
    return {"command": " ".join(cmd), "returncode": pr.returncode, "stderr_last_50_lines": tail}


def dev_dv3(out):
    os.makedirs(out, exist_ok=True)
    o = os.path.join(out, "dv3_16777291_n3.json")
    inv = run_worker(["dv3-worker", "--p", "16777291", "--n", "3", "--out", o], os.path.join(out, "dv3_16777291_n3"))
    rec = R.load_json(o) if os.path.exists(o) else {}
    rep = {"invocation": inv, "record": rec, "pass": bool(rec.get("reproduces_RUN_GFPN_3377f1"))}
    dump(os.path.join(out, "dv3.json"), rep)
    print("DV-3:", "PASS (overflow reproduced)" if rep["pass"] else "FAIL", rec.get("call"))
    return 0 if rep["pass"] else 1


def dev_semantics(out):
    os.makedirs(out, exist_ok=True)
    o = os.path.join(out, "semantics_probe.json")
    inv = run_worker(["semantics-worker", "--out", o], os.path.join(out, "semantics_probe"))
    rec = R.load_json(o) if os.path.exists(o) else {}
    dump(os.path.join(out, "semantics.json"), {"invocation": inv, "record": rec})
    print("RC-2 semantics probe:", rec.get("semantics"), rec.get("after_same_handle"), rec.get("after_fresh_handle_constructed"))
    return 0


def dev_dv2(out):
    os.makedirs(out, exist_ok=True)
    rep = {"points": {}, "rc5_gp_crosscheck": {}}
    ok = True
    for (p, n) in DV2_POINTS:
        reps = []
        for rep_i in (1, 2):
            o = os.path.join(out, "dv2_%d_n%d_rep%d.json" % (p, n, rep_i))
            inv = run_worker(["dv2-worker", "--p", str(p), "--n", str(n), "--out", o], os.path.join(out, "dv2_%d_n%d_rep%d" % (p, n, rep_i)))
            rec = R.load_json(o) if os.path.exists(o) else None
            reps.append({"invocation": inv, "record": rec})
            print("DV-2 %d n=%d rep%d rc=%s N=%s" % (p, n, rep_i, inv["returncode"], rec and rec.get("call")))
        crit = {}
        recs = [r["record"] for r in reps]
        crit["both_returned"] = all(r and r["call"]["returned"] for r in recs)
        if crit["both_returned"]:
            crit["N_times_basepoint_is_O"] = all(r["N_times_basepoint_is_O"] for r in recs)
            crit["N_times_second_point_is_O"] = all(r["N_times_second_point_is_O"] for r in recs)
            crit["hasse"] = all(r["hasse_interval"]["holds"] for r in recs)
            crit["repetitions_agree"] = recs[0]["call"]["N"] == recs[1]["call"]["N"]
            crit["start_readbacks_equal_configured"] = all(not r["start_refusal_reasons"] for r in recs)
            crit["readbacks_before_after_equal_configured"] = all(
                r[k]["parisize"] == R.PARISIZE and r[k]["parisizemax"] == R.PARISIZEMAX for r in recs for k in ("readback_before_call", "readback_after_call"))
            crit["exit_parisizemax_exact"] = all(r["exit_readback"]["pass_parisizemax_exact"] for r in recs)
            crit["vmhwm_at_most_805306368"] = all(r["proc_status_after_call"]["VmHWM_bytes"] <= R.VMHWM_BOUND for r in recs)
            crit["DV4_self_rss_below_1GiB"] = all(r["DV4_below_1GiB"] for r in recs)
            if (p, n) == (4111, 3):
                crit["N_equals_69477519282"] = recs[0]["call"]["N"] == KNOWN_N_4111_3
            if (p, n) in ((16777291, 3), (4111, 4)):
                g = gp_crosscheck(recs[0]["serialisation"], p, n, os.path.join(out, "gp"), "rc5_%d_n%d" % (p, n))
                rep["rc5_gp_crosscheck"]["%d_n%d" % (p, n)] = g
                gl = g["child"].get("rlimit_as_child_getrlimit") or {}
                crit["rc5_gp_child_ok"] = g["child"]["outcome"] == "ok"
                crit["rc5_gp_getrlimit_10737418240"] = gl.get("soft") == R.CAP_BYTES and gl.get("hard") == R.CAP_BYTES
                crit["rc5_gp_agrees_with_in_process"] = g["N"] == recs[0]["call"]["N"]
                print("  RC-5 gp cross-check %d n=%d: gp N=%s outcome=%s getrlimit=%s" % (p, n, g["N"], g["child"]["outcome"], gl))
        pt_ok = all(v is True for v in crit.values())
        ok = ok and pt_ok
        rep["points"]["%d_n%d" % (p, n)] = {"repetitions": reps, "criteria": crit, "pass": pt_ok}
        print("  criteria:", json.dumps(crit))
    rep["pass"] = ok
    dump(os.path.join(out, "dv2.json"), rep)
    print("DV-2:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("check")
    ap.add_argument("--out", required=True)
    ap.add_argument("--p", type=int)
    ap.add_argument("--n", type=int)
    a, rest = ap.parse_known_args()
    if a.check == "dv2-worker":
        return worker_dv2(a.p, a.n, a.out)
    if a.check == "dv3-worker":
        return worker_dv3(a.p, a.n, a.out)
    if a.check == "semantics-worker":
        return worker_semantics(a.out)
    fn = {"dv2": dev_dv2, "dv3": dev_dv3, "semantics": dev_semantics}.get(a.check)
    if fn is None:
        import r2_devchecks_more as MORE
        return MORE.dispatch(a.check, a.out, rest)
    return fn(a.out)


if __name__ == "__main__":
    sys.exit(main())
