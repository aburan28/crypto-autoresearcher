#!/usr/bin/env python3
"""EXP-GFPN-05ff43 successor stage -- DV-12 (seedresolve SF-6 (a)-(g)): the re-solve path, FORCED, in a scratch toy
copy through a development shim that no delivered entry can reach (new file). Development only.

Called as `python3 -B r2_devchecks.py dv12 --out DIR`. Everything it writes goes under DIR.

Toy copy (no ladder or fixture prime is solved; toy prime only): the toy G1 package `fixture --p 1033`, with the n = m
= 3 toy fixture data of stage R1's DV-7 (same construction and the same declared stream label, so the toy inputs are
the stage-R1 toy inputs), a toy copy of trial-plan-v2-r2.json whose G1 driver_args are `fixture --p 1033`, the real
trial-plan-v2-a1-r2.json and trial-plan-v2.json, a synthetic TASK-20260924-689d2f phase-A receipt in scratch and a
git-state stub for the (uncommitted) r2 tree. Each case runs the DELIVERED r2_run_wrapper.main in this process and the
DELIVERED r2_entry_v2.py in a child through the shim below; each case has its own scratch runs directory.

Declared forced target: solver tag fx_reg1_S3 (regression target reg1, arm S3; per-target timeout 1800 s).
Cases (SF-6):
  U   unforced (the reference for (a)-(c)); also traced for the DV-11 partial dynamic count and DV-1 dynamic trace;
  (a) attempt 1 forced to SSF clause (ii)                      -> recorded result must equal U's;
  (b) attempt 1 forced to SSF clause (iv) (substitution)       -> the same;
  (c) attempt 1 forced to SSF clause (v) via a shimmed .ms.log carrying the random-form string -> the same;
  (d) all K + 1 = 6 attempts forced to clause (ii)             -> degenerate_parametrisation, D undefined, as frozen;
  (e) attempt 1 forced SSF, attempt 2's input sha256 forced to mismatch -> the package ends failed (implementation_error);
  (f) all attempts forced SSF, the wrapper clock shimmed so that attempt 2's wall seconds reach timeout_s -> the
      recorded result is attempt 2's class, with resolve_cap_reached;
  (g) attempt 1 forced SSF, the 2 s wait shimmed away          -> the package ends failed (SF-2 (b)).
A FORCED attempt is a real frozen solve() whose returned result dict the shim rewrites after the call (and, for (c),
whose .ms.log gains the random-form string). Each forcing is logged in DIR/<case>/shim-log.jsonl.
"""
import copy
import datetime
import io
import json
import os
import random
import shutil
import sys
import contextlib

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import r2_common as R                                    # noqa: E402

TOY_P = 1033
TARGET_TAG = "fx_reg1_S3"
TARGET = ("targets", "reg1", "S3")
CASES = ["U", "a", "b", "c", "d", "e", "f", "g"]
SYN = "SYNTHETIC (DV-12 only): written by the check; never a measurement"


def dump(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        json.dump(obj, fh, indent=1, default=str)


def toy_fixture_n3(p):
    """Stage R1 DV-7's toy fixture construction (implementation-v2-r1/r1_toy.py lines 56-75), reproduced here (no r1
    module is imported), with the same declared stream label."""
    sys.path.insert(0, R.V2_DIR)
    from v2_field import Fq, Curve
    import v2_arms as A
    cmod = next(c for c in range(2, p) if pow(c, (p - 1) // 3, p) != 1)
    F = Fq.binomial(p, 3, cmod)
    for c in range(1, p):
        E = Curve(F, 2, c * F.z, 0, "fixture_n3")
        if not F.is_square(E.a4) and not F.is_square(E.a2 * E.a2 - 4 * E.a4):
            break
    rng = random.Random("r1-dv7:toy-fixture-n3:%d:regression" % p)
    tg = []
    while len(tg) < 2:
        P = E.random_point(rng)
        if P is None or P[0] == 0:
            continue
        cs = F.coeffs(P[0])
        tg.append({"target": len(tg), "x_R": "%d*z^2 + %d*z + %d" % (cs[2], cs[1], cs[0])})
    return {"p": p, "field": "F_%d[z]/(z^3 - %d)" % (p, cmod), "curve": "y^2 = x(x^2 + 2x + %d*z)" % c, "b_is_square": False,
            "a2^2-4b_is_square": False, "beta": A.smallest_nonsquare(p), "targets": tg, "toy_note": "DV-12 toy fixture data (stage R1 DV-7 construction)"}


# ============================================================================ shim (development only; never delivered)
SHIM = r'''
import os, sys, json, re, traceback, datetime, importlib.abc, importlib.util, runpy
sys.dont_write_bytecode = True
CFG = json.load(open(os.environ["R2_DV12_CFG"]))
sys.path.insert(0, CFG["layer_dir"])
import r2_common as R
for k, v in CFG["R"].items():
    setattr(R, k, v)
import r2_resolve as RS
CASE = os.environ.get("R2_DV12_CASE") or "U"
TRACE = CFG["trace"]
SHIMLOG = CFG["shim_log"]
TARGET = CFG["target_tag"]

def _log(ev, extra=None):
    st = traceback.extract_stack()[:-2]
    rec = {"event": ev, "pid": os.getpid(), "case": CASE,
           "inside_wrapper": any(f.filename.endswith("r2_resolve.py") and f.name == "solve" for f in st),
           "stack": ["%s:%d" % (os.path.basename(f.filename), f.lineno) for f in st if "implementation-v2" in f.filename][-8:]}
    if extra:
        rec.update(extra)
    with open(TRACE, "a") as fh:
        fh.write(json.dumps(rec) + "\n")

import cypari2
_Base = cypari2.Pari
class TracingPari(_Base):
    def __call__(self, s, *a, **k):
        m = re.search(r"ffgen\(Mod\(1, (\d+)\)\*\((.*?)\), 'w\)", str(s))
        _log("cypari2.Pari.__call__", {"p": int(m.group(1)) if m else None,
             "field_degree": max(int(x) for x in re.findall(r"w\^(\d+)", m.group(2))) if m else None})
        return super().__call__(s, *a, **k)
cypari2.Pari = TracingPari

class Hook(importlib.abc.MetaPathFinder):
    def find_spec(self, name, path, target=None):
        if name not in CFG["mods"] and name != "v2_solver":
            return None
        sys.meta_path.remove(self)
        spec = importlib.util.find_spec(name)
        sys.meta_path.insert(0, self)
        orig = spec.loader.exec_module
        def exec_module(module, _o=orig, _n=name):
            _o(module)
            for k, v in CFG["mods"].get(_n, {}).items():
                setattr(module, k, v)
            if _n == "v2_solver":
                rc = module.run_child
                def run_child(argv, *a, **k):
                    flags = [x for x in argv if x in ("-P", "-g")]
                    _log("child", {"child_argv0": os.path.basename(argv[0]), "child_flags": flags,
                                   "msolve_in_argv": any(os.path.basename(x) == "msolve" for x in argv)})
                    return rc(argv, *a, **k)
                module.run_child = run_child
        spec.loader.exec_module = exec_module
        return spec
sys.meta_path.insert(0, Hook())

# ---- DV-12 forcing (SF-6 (a)-(g)) on the r2_resolve indirections
OFFSET = [datetime.timedelta(0)]
calls = {}
def slog(rec):
    with open(SHIMLOG, "a") as fh:
        fh.write(json.dumps(rec, default=str) + "\n")
if CASE != "U":
    _orig_call = RS._call_original
    def forced(original, args, kwargs):
        tag = args[3]
        if tag != TARGET or kwargs.get("gb_only"):
            return _orig_call(original, args, kwargs)
        k = calls[tag] = calls.get(tag, 0) + 1
        res = _orig_call(original, args, kwargs)
        real = {"outcome": res.get("outcome"), "reason": res.get("reason"), "D": res.get("D"), "output_sha256": res.get("output_sha256")}
        force = (CASE in ("a", "b", "c", "e", "g") and k == 1) or CASE in ("d", "f")
        clause = {"b": "iv", "c": "v"}.get(CASE, "ii")
        if force:
            if clause == "ii":
                res.update(outcome="degenerate_parametrisation", D=None, D_defined=False, solutions=[],
                           reason="eliminating polynomial degree %s != quotient dimension %s (DV-12 FORCED by the development shim)"
                                  % ((res.get("solution_info") or {}).get("elim_degree"), res.get("dimension_of_quotient_printed")))
            elif clause == "iv":
                res.update(outcome="degenerate_parametrisation", D=None, D_defined=False, solutions=[],
                           reason="1 parsed solution(s) fail substitution into the descended system")
            else:
                res.update(outcome="positive_dimensional", D=None, D_defined=False, solutions=[], reason="msolve reported positive dimension")
                with open(os.path.join(args[0].rd, "solver", tag + ".ms.log"), "a") as fh:
                    fh.write("\n" + RS.RANDOM_FORM + "  (DV-12 shimmed log line)\n")
        if CASE == "e" and k == 2:
            res["input"]["sha256"] = "0" * 64
        if CASE == "f" and k == 2:
            OFFSET[0] += datetime.timedelta(seconds=float(args[4]) + 1.0)
        slog({"case": CASE, "tag": tag, "attempt": k, "forced": force, "clause_forced": clause if force else None, "real_result": real,
              "recorded_as": {"outcome": res.get("outcome"), "reason": res.get("reason")},
              "input_sha_forced": CASE == "e" and k == 2, "clock_offset_s": OFFSET[0].total_seconds()})
        return res
    RS._call_original = forced
    if CASE == "f":
        RS._now = lambda: RS._utc() + OFFSET[0]
    if CASE == "g":
        RS._wait_spacing = lambda prev_end: slog({"case": CASE, "wait_spacing_shimmed_away_after": str(prev_end)})
entry = CFG["entry"]
sys.argv = [entry] + sys.argv[1:]
runpy.run_path(entry, run_name="__main__")
'''


def target_arm(raw):
    lst, t, arm = TARGET
    for x in raw.get(lst) or []:
        if x.get("target") == t:
            return (x.get("arms") or {}).get(arm)
    return None


def dv12(out, rest):
    os.makedirs(out, exist_ok=True)
    sys.path.insert(0, R.V2_DIR)
    fx = {"task": "DV-12 toy", "n": 3, "m": 3, "primes": [toy_fixture_n3(TOY_P)]}
    fx_path = os.path.join(out, "toy_fixture_n3.json")
    dump(fx_path, fx)
    v2r2 = R.load_json(R.PLAN_V2_R2)
    G = v2r2["gate"]["blocking_packages"]
    toy = copy.deepcopy(v2r2)
    by = {pk["order"]: pk for pk in toy["packages"]}
    by[1].update(driver_args=["fixture", "--p", str(TOY_P)], p=TOY_P)
    toy["toy_note"] = "TOY copy (DV-12): G1 -> fixture --p %d; everything else as trial-plan-v2-r2.json" % TOY_P
    toy_plan = os.path.join(out, "toy-trial-plan-v2-r2.json")
    dump(toy_plan, toy)
    r2files = sorted(os.path.relpath(os.path.join(dp, f), R.REPO) for dp, _d, fn in os.walk(os.path.join(R.REPO, R.R2_PATHS_REL[0])) for f in fn) + R.R2_PATHS_REL[1:]
    rec_a = os.path.join(out, "synthetic-689d2f-phase-a-receipt.json")
    dump(rec_a, {"synthetic": SYN, "commit_sha": "dv12-synthetic-not-a-commit", "path_sha256": {p: R.sha256_file(os.path.join(R.REPO, p)) for p in r2files}})
    shims = os.path.join(out, "shims")
    os.makedirs(shims, exist_ok=True)
    shim = os.path.join(shims, "entry_v2_dv12.py")
    with open(shim, "w") as fh:
        fh.write(SHIM)
    cache = os.path.join(out, "cache")
    os.makedirs(cache, exist_ok=True)
    os.environ["GFPN_V2_CACHE_DIR"] = cache
    import r2_run_wrapper as W
    real_git = W.git_tree_state
    W.git_tree_state = lambda paths: (r2files, []) if paths == R.R2_PATHS_REL else real_git(paths)
    W.ENTRY_V2 = shim
    R.PLAN_V2_R2 = toy_plan
    R.RECEIPT_R2_PHASE_A = rec_a
    cases = [c for c in CASES if not rest or c in rest]
    report = {"toy_prime": TOY_P, "target_tag": TARGET_TAG, "g1": G[0], "cases": {}, "no_ladder_or_fixture_prime_solved": True}
    for case in cases:
        cd = os.path.join(out, case)
        if os.path.exists(cd):
            raise SystemExit("REFUSING: %s exists (a case is run once; a re-run needs a recorded harness reason)" % cd)
        exp = os.path.join(cd, "exp")
        runs = os.path.join(exp, "runs")
        os.makedirs(runs)
        cfgp = os.path.join(cd, "cfg.json")
        dump(cfgp, {"layer_dir": HERE, "entry": os.path.join(HERE, "r2_entry_v2.py"), "target_tag": TARGET_TAG,
                    "trace": os.path.join(cd, "trace.jsonl"), "shim_log": os.path.join(cd, "shim-log.jsonl"),
                    "R": {"PLAN_V2_R2": toy_plan, "RECEIPT_R2_PHASE_A": rec_a, "RUNS_DIR": runs},
                    "mods": {"v2_common": {"EXP_DIR": exp, "FIXTURE_N3_JSON": fx_path}}})
        os.environ["R2_DV12_CFG"] = cfgp
        if case == "U":
            os.environ.pop("R2_DV12_CASE", None)
        else:
            os.environ["R2_DV12_CASE"] = case
        W.RUNS = runs
        t0 = datetime.datetime.now(datetime.timezone.utc)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = W.main([G[0]])
        t1 = datetime.datetime.now(datetime.timezone.utc)
        rd = os.path.join(runs, G[0])
        import yaml
        man = yaml.safe_load(open(os.path.join(rd, "manifest.yaml")))["run"] if os.path.exists(os.path.join(rd, "manifest.yaml")) else None
        raw = json.load(open(os.path.join(rd, "raw-result.json"))) if os.path.exists(os.path.join(rd, "raw-result.json")) else None
        sev = json.load(open(os.path.join(rd, "solver-events.json"))) if os.path.exists(os.path.join(rd, "solver-events.json")) else None
        ev = [e for e in (sev or {}).get("events") or [] if e.get("tag") == TARGET_TAG]
        report["cases"][case] = {"run_dir": rd, "wrapper_rc": rc, "wrapper_stdout": buf.getvalue().splitlines(), "started": t0.isoformat(),
                                 "finished": t1.isoformat(), "status": man and man["status"], "failure_class": man and man["failure_class"],
                                 "gate_pass": man and man["result"]["gate_pass"],
                                 "hashseed_readback": man and (man["environment"].get("PYTHONHASHSEED_driver_readback") or {}).get("PYTHONHASHSEED_env"),
                                 "getrlimit": man and man["resources"]["child_rlimit_as_read_back_by_getrlimit"],
                                 "threads": man and man["resources"]["msolve_threads_executed"],
                                 "solver_events_block": man and man.get("solver_events"),
                                 "target_event": ev[0] if ev else None, "all_event_tags": [e.get("tag") for e in (sev or {}).get("events") or []],
                                 "target_recorded_arm": {k: (target_arm(raw) or {}).get(k) for k in ("outcome", "reason", "D", "D_defined")} if raw else None,
                                 "renamed_files": sorted(os.path.basename(x) for x in os.listdir(os.path.join(rd, "solver")) if ".ssf-attempt" in x) if os.path.isdir(os.path.join(rd, "solver")) else []}
        print("  case %-2s rc=%s status=%s fclass=%s gate_pass=%s target=%s events=%s (%.0fs)" % (
            case, rc, report["cases"][case]["status"], report["cases"][case]["failure_class"], report["cases"][case]["gate_pass"],
            report["cases"][case]["target_recorded_arm"], report["cases"][case]["all_event_tags"], (t1 - t0).total_seconds()))
        dump(os.path.join(out, "dv12-progress.json"), report)
    dump(os.path.join(out, "dv12-runs.json"), report)
    return evaluate(out, report)


def evaluate(out, report):
    import r2_reg1 as REG
    cs = report["cases"]
    res = {}
    U = cs.get("U")
    ref_receipt = os.path.join(out, "toy-U-receipt.json")
    if U and os.path.exists(U["run_dir"]):
        dump(ref_receipt, {"synthetic": SYN, "path_sha256": {os.path.relpath(os.path.join(dp, f), R.REPO): R.sha256_file(os.path.join(dp, f))
                                                             for dp, _d, fn in os.walk(U["run_dir"]) for f in fn}})

    def spacing_ok(ev):
        a = ev["attempts"]
        gaps = []
        for i in range(1, len(a)):
            s = datetime.datetime.strptime(a[i]["start_utc"], "%Y-%m-%dT%H:%M:%S.%fZ")
            e = datetime.datetime.strptime(a[i - 1]["end_utc"], "%Y-%m-%dT%H:%M:%S.%fZ")
            gaps.append((s - e).total_seconds())
        return gaps
    for case in ("a", "b", "c"):
        c = cs.get(case)
        if not c:
            continue
        ev = c["target_event"] or {}
        clause = {"a": "ii", "b": "iv", "c": "v"}[case]
        reg = REG.compare(U["run_dir"], c["run_dir"], receipt=ref_receipt) if U else None
        chk = {"attempt1_ssf_clause": (ev.get("attempts") or [{}])[0].get("ssf_clause") == clause,
               "re_solved": len(ev.get("attempts") or []) >= 2,
               "renamed_attempt1_files": all(f in c["renamed_files"] for f in (TARGET_TAG + ".ms.out.ssf-attempt1", TARGET_TAG + ".ms.log.ssf-attempt1", TARGET_TAG + ".ms.err.ssf-attempt1")),
               "spacing_ge_2s": all(g >= 2.0 for g in spacing_ok(ev)) if ev else False,
               "recorded_target_equals_U": c["target_recorded_arm"] == U["target_recorded_arm"],
               "reg1_d_parsed_vs_U_pass": bool(reg) and reg["verdict"] == "PASS",
               "package_completed": c["status"] == U["status"]}
        res[case] = {"checks": chk, "pass": all(chk.values()), "spacing_s": spacing_ok(ev) if ev else None,
                     "reg1_failures": reg and reg["failures"], "reg1_output": reg and REG.render(reg)}
    c = cs.get("d")
    if c:
        ev = c["target_event"] or {}
        chk = {"six_attempts": len(ev.get("attempts") or []) == R.K + 1,
               "all_clause_ii": all(a.get("ssf_clause") == "ii" for a in ev.get("attempts") or []) and bool(ev),
               "still_ssf_after_last_attempt": ev.get("still_ssf_after_last_attempt") is True,
               "recorded_degenerate_D_undefined": (c["target_recorded_arm"] or {}).get("outcome") == "degenerate_parametrisation"
                                                  and (c["target_recorded_arm"] or {}).get("D_defined") is False and (c["target_recorded_arm"] or {}).get("D") is None,
               "renamed_attempts_1_to_5": all((TARGET_TAG + ".ms.out.ssf-attempt%d" % k) in c["renamed_files"] for k in range(1, 6)),
               "spacing_ge_2s": all(g >= 2.0 for g in spacing_ok(ev)) if ev else False,
               "no_resolve_cap": ev.get("resolve_cap_reached") is False}
        res["d"] = {"checks": chk, "pass": all(chk.values()), "spacing_s": spacing_ok(ev) if ev else None, "package": [c["status"], c["failure_class"], c["gate_pass"]]}
    for case, needle in (("e", "input sha256"), ("g", "s after attempt 1's recorded end")):
        c = cs.get(case)
        if not c:
            continue
        ev = c["target_event"] or {}
        viol = (ev.get("consistency") or {}).get("violations") or []
        chk = {"package_failed": c["status"] == "failed", "implementation_error": c["failure_class"] == "implementation_error",
               "violation_recorded": any(needle in v for v in viol),
               "manifest_block_records_violation": ((c["solver_events_block"] or {}).get("consistency_violation") is True)}
        res[case] = {"checks": chk, "pass": all(chk.values()), "violations": viol}
    c = cs.get("f")
    if c:
        ev = c["target_event"] or {}
        chk = {"two_attempts": len(ev.get("attempts") or []) == 2, "resolve_cap_reached": ev.get("resolve_cap_reached") is True,
               "recorded_is_attempt2_class": (c["target_recorded_arm"] or {}).get("outcome") == "degenerate_parametrisation"
                                             and ev.get("accepted_attempt") == 2,
               "manifest_block_counts_cap": ((c["solver_events_block"] or {}).get("resolve_cap_reached") or 0) >= 1}
        res["f"] = {"checks": chk, "pass": all(chk.values()), "cap_detail": ev.get("resolve_cap_detail")}
    report["evaluation"] = res
    report["all_cases_pass"] = all(v["pass"] for v in res.values()) and len(res) == 7
    report["STOP"] = None if report["all_cases_pass"] else "SF-6: a DV-12 case failed: %s" % sorted(k for k, v in res.items() if not v["pass"])
    dump(os.path.join(out, "dv12.json"), report)
    for k in sorted(res):
        print("  DV-12 (%s): %s %s" % (k, "PASS" if res[k]["pass"] else "FAIL", json.dumps(res[k]["checks"])))
    print("DV-12:", "PASS" if report["all_cases_pass"] else "FAIL/STOP")
    return 0 if report["all_cases_pass"] else 3
