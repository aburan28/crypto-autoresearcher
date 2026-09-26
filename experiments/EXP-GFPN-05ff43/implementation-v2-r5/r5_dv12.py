#!/usr/bin/env python3
"""EXP-GFPN-05ff43 r4 stage (TASK-20260924-d91a96) -- DV-12 (seedresolve SF-6 (a)-(g), at S-1): the SE-3 re-solve
path, FORCED, in a scratch toy copy through a development shim that no delivered entry can reach. Development only.
Started from implementation-v2-r3/r3_dv12.py (cases, forcing and evaluation carried; re-pointed to the r4 layer; the
toy environment is DV-7's, r5_dv7.Toy). r4 changes: the wrapper is run as RK-4 (a) words the development method
(preflight, its refusals recorded; refusals naming a DECLARED SYNTHETIC toy package (G3, G4) are expected; any other
refusal fails the case and nothing is launched; then launch); the frozen checker the wrapper runs at admission and
after the package is the toy check shim; the synthetic phase-A receipt carries commit_sha = the repository HEAD.

Called as `python3 -B r5_devchecks.py dv12 --out DIR DV7_TOY_DIR`. Everything it writes goes under DIR.

Toy copy (toy prime only): the toy G1 package `fixture --p 1033` of DV-7's toy copy of trial-plan-v2-r5.json, run by
the DELIVERED r5_run_wrapper (preflight, then launch) in this process and the DELIVERED r5_entry_v2.py in a child through the shim below;
each case has its own scratch runs directory. PYTHONHASHSEED is the delivered "0".
Declared forced target: solver tag fx_reg1_S3 (regression target reg1, arm S3; per-target timeout 1800 s).
Cases (SF-6):
  U   unforced (the reference for (a)-(c));
  (a) attempt 1 forced to SSF clause (ii)                      -> recorded result must equal U's;
  (b) attempt 1 forced to SSF clause (iv) (substitution)       -> the same;
  (c) attempt 1 forced to SSF clause (v) via a shimmed .ms.log carrying the random-form string -> the same;
  (d) all K + 1 = 6 attempts forced to clause (ii)             -> degenerate_parametrisation, D undefined, as frozen;
  (e) attempt 1 forced SSF, attempt 2's input sha256 forced to mismatch -> the package ends failed (implementation_error);
  (f) all attempts forced SSF, the wrapper clock shimmed so that attempt 2's wall seconds reach timeout_s -> the
      recorded result is attempt 2's class, with resolve_cap_reached;
  (g) attempt 1 forced SSF, the 2 s wait shimmed away          -> the package ends failed (SF-2 (b)).
A FORCED attempt is a real frozen solve() whose returned result dict the shim rewrites after the call (and, for (c),
whose .ms.log gains the random-form string). Each forcing is logged, with the real result, in DIR/<case>/shim-log.jsonl.
"""
import contextlib
import datetime
import io
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import r5_common as R                                    # noqa: E402
import r5_dv7 as T                                       # noqa: E402  (the shared toy environment; development only)

TOY_P = 1033
TARGET_TAG = "fx_reg1_S3"
TARGET = ("targets", "reg1", "S3")
CASES = ["U", "a", "b", "c", "d", "e", "f", "g"]
SYN = "SYNTHETIC (DV-12 only): written by the check; never a measurement"

FORCING = r'''
# ---- DV-12 forcing (SF-6 (a)-(g)) on the r5_resolve indirections (development only)
CASE = os.environ.get("R4_FORCE_CASE") or "U"
SHIMLOG = CFG["shim_log"]
TARGET = CFG["target_tag"]
OFFSET = [datetime.timedelta(0)]
calls = {}
def slog(rec):
    with open(SHIMLOG, "a") as fh:
        fh.write(json.dumps(rec, default=str) + "\n")
if CASE != "U":
    _inner = RS._call_original
    def forced(original, args, kwargs):
        tag = args[3]
        if tag != TARGET or kwargs.get("gb_only") or getattr(original, "__name__", "") != "solve":
            return _inner(original, args, kwargs)
        k = calls[tag] = calls.get(tag, 0) + 1
        res = _inner(original, args, kwargs)
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
        slog({"case": CASE, "site": "v2_driver.solve", "tag": tag, "attempt": k, "forced": force, "clause_forced": clause if force else None,
              "real_result": real, "recorded_as": {"outcome": res.get("outcome"), "reason": res.get("reason")},
              "input_sha_forced": CASE == "e" and k == 2, "clock_offset_s": OFFSET[0].total_seconds()})
        return res
    RS._call_original = forced
    if CASE == "f":
        RS._now = lambda: RS._utc() + OFFSET[0]
    if CASE == "g":
        RS._wait_spacing = lambda prev_end: slog({"case": CASE, "wait_spacing_shimmed_away_after": str(prev_end)})
'''


def target_arm(raw):
    lst, t, arm = TARGET
    for x in raw.get(lst) or []:
        if x.get("target") == t:
            return (x.get("arms") or {}).get(arm)
    return None


def s1_events(doc):
    return ((doc or {}).get("sites") or {}).get(R.SITE_S1, {}).get("events") or []


def run_cases(out, toy_dir, cases, forcing, shim_name, target_tag, rid_of, entry_kind, reporter):
    """Shared by DV-12 and DV-16: run each case as one package through the DELIVERED wrapper and entry."""
    env = T.Toy(toy_dir).load()
    import r5_run_wrapper as W
    real_git = W.git_tree_state
    W.git_tree_state = lambda paths: (env["r4files"], []) if paths == R.R5_PATHS_REL else real_git(paths)
    shims = T.write_shims(os.path.join(out, "shims"), extra=forcing)
    W.ENTRY_V2 = W.ENTRY_A1 = shims["entry_toy.py"]
    import r5_check_run as K
    K.FROZEN_LAUNCHER = [sys.executable, "-B", shims["check_toy.py"]]
    # a synthetic TASK-20260924-4a47e5 phase-A receipt binding the r4 files as they are at THIS check's start (the layer
    # is not edited while a check runs); commit_sha: the repository HEAD
    r4files = sorted(os.path.relpath(os.path.join(dp, f), R.REPO) for dp, _d, fn in os.walk(os.path.join(R.REPO, R.R5_PATHS_REL[0])) for f in fn) + R.R5_PATHS_REL[1:]
    env["r4files"] = r4files
    env["receipt_a"] = os.path.join(out, "toy-4a47e5-phase-a-receipt.json")
    import subprocess
    head = subprocess.run(["git", "-C", R.REPO, "rev-parse", "HEAD"], capture_output=True, text=True,
                          env=dict(os.environ, GIT_OPTIONAL_LOCKS="0")).stdout.strip()
    T.dump(env["receipt_a"], {"synthetic": "development only; never a receipt", "commit_sha": head,
                              "path_sha256": {p: R.sha256_file(os.path.join(R.REPO, p)) for p in r4files}})
    for k, v in {"PLAN_V2_R5": env["plan_v2r4"], "PLAN_A1_R5": env["plan_a1r4"], "PLAN_V2": env["plan_v2"], "RECEIPT_R5_PHASE_A": env["receipt_a"]}.items():
        setattr(R, k, v)
    cache = os.path.join(out, "cache")
    os.makedirs(cache, exist_ok=True)
    os.environ["GFPN_V2_CACHE_DIR"] = cache
    rid = rid_of(env)
    Gt = R.load_json(env["plan_v2r4"])["gate"]["blocking_packages"]
    synth = {Gt[2], Gt[3]}                                   # the DV-7 toy's declared synthetic gate packages
    # the DV-7 toy's declared rule: a toy G2 that did not pass stays the gate; its 'did not pass' refusal is expected
    g2raw = os.path.join(toy_dir, "world_A", "exp", "runs", Gt[1], "raw-result.json")
    failed_g2 = None
    if os.path.exists(g2raw):
        _g2 = json.load(open(g2raw))
        if _g2.get("run_status") != "completed_valid" or _g2.get("gate_pass") is not True:
            failed_g2 = Gt[1]
    import re
    pat = re.compile(r"(?:gate package|read package) (RUN-GFPN-[0-9a-f]{6})")
    report = {"toy_env": "DV-7 toy environment (toy-env.json)", "target_tag": target_tag, "run_id": rid, "cases": {},
              "declared_synthetic_packages": sorted(synth)}
    for case in cases:
        cd = os.path.join(out, case)
        if os.path.exists(cd):
            raise SystemExit("REFUSING: %s exists (a case is run once; a re-run needs a recorded harness reason)" % cd)
        exp = os.path.join(cd, "exp")
        runs = os.path.join(exp, "runs")
        os.makedirs(runs)
        # the DV-7 world-A gate packages are needed for R-7 of the addendum package (DV-16 only); linked by copy
        for g in reporter.get("prerequisites", lambda e: [])(env):
            import shutil
            shutil.copytree(g[0], os.path.join(runs, g[1]))
        cfgp = os.path.join(cd, "cfg.json")
        T.dump(cfgp, {"layer_dir": HERE, "exp_real": R.EXP_DIR, "trace": os.path.join(cd, "trace.jsonl"), "shim_log": os.path.join(cd, "shim-log.jsonl"),
                      "target_tag": target_tag,
                      "R": {"PLAN_V2_R5": env["plan_v2r4"], "PLAN_A1_R5": env["plan_a1r4"], "PLAN_V2": env["plan_v2"],
                            "RECEIPT_R5_PHASE_A": env["receipt_a"], "RECEIPT_R5_PHASE_B": reporter.get("receipt_b", ""),
                            "RUNS_DIR": reporter.get("reg_runs", runs), "REG1_REFERENCE_RUN": R.load_json(env["plan_v2r4"])["gate"]["blocking_packages"][0],
                            "RECEIPT_V2_PHASE_B": reporter.get("reg_receipt", "")},
                      "mods": {"v2_common": {"EXP_DIR": exp, "LADDER_PATH": env["ladder"], "FIXTURE_N3_JSON": env["fx3"], "FIXTURE_N4_JSON": env["fx4"]},
                               "a1_common": {"EXP_DIR": exp, "RUNS_DIR": runs, "LADDER_PATH": env["ladder"]}},
                      "entry": {"v2": os.path.join(HERE, "r5_entry_v2.py"), "a1": os.path.join(HERE, "r5_entry_a1.py")}})
        os.environ["R4_TOY_CFG"] = cfgp
        os.environ["R4_TOY_ENTRY"] = entry_kind
        os.environ["R4_TOY_PACKAGE"] = "%s/%s" % (case, rid)
        os.environ["R4_FORCE_CASE"] = case
        R.RUNS_DIR = reporter.get("reg_runs", runs)
        R.RECEIPT_V2_PHASE_B = reporter.get("reg_receipt", "")
        R.RECEIPT_R5_PHASE_B = reporter.get("receipt_b", "")
        W.RUNS = runs
        W.DRIVER_PYTHONHASHSEED = R.DRIVER_PYTHONHASHSEED
        t0 = datetime.datetime.now(datetime.timezone.utc)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            refusals, info = W.preflight(rid)
        exp_ref = [r for r in refusals if ((r.startswith("R-7 (RB-4 (b)) the r5 checker on gate package ")
                                            or r.startswith("R-8 (RL-4; RF-3 (b) designed stop) read package "))
                                           and pat.search(r) and pat.search(r).group(1) in synth)
                   or (failed_g2 and r.startswith("R-7 repaired gate package %s did not pass" % failed_g2))]
        unexp_ref = [r for r in refusals if r not in exp_ref]
        rc = None
        if not unexp_ref:
            with contextlib.redirect_stdout(buf):
                rc = W.launch(rid, None, info)
        t1 = datetime.datetime.now(datetime.timezone.utc)
        rd = os.path.join(runs, rid)
        man = T.manifest_row(runs, rid)
        raw = json.load(open(os.path.join(rd, "raw-result.json"))) if os.path.exists(os.path.join(rd, "raw-result.json")) else None
        sev = json.load(open(os.path.join(rd, "solver-events.json"))) if os.path.exists(os.path.join(rd, "solver-events.json")) else None
        row = {"run_dir": rd, "wrapper_launch_rc": rc, "launched": rc is not None, "preflight_refusals_expected": exp_ref,
               "preflight_refusals_unexpected": unexp_ref, "r4_verdict": man and (man.get("verdict") or {}).get("r4_verdict"),
               "r4_stop_classes": man and (man.get("verdict") or {}).get("stop_classes"),
               "wrapper_stdout": buf.getvalue().splitlines(), "started": t0.isoformat(), "finished": t1.isoformat(),
               "status": man and man["status"], "failure_class": man and man["failure_class"], "gate_pass": man and man["result"]["gate_pass"],
               "hashseed_readback": man and ((man.get("environment") or {}).get("PYTHONHASHSEED_driver_readback") or {}).get("PYTHONHASHSEED_env"),
               "getrlimit": man and man["resources"]["child_rlimit_as_read_back_by_getrlimit"],
               "threads": man and man["resources"]["msolve_threads_executed"],
               "solver_events_block": man and man.get("solver_events")}
        row.update(reporter["extract"](rd, raw, sev))
        report["cases"][case] = row
        print("  case %-2s launched=%s status=%s fclass=%s gate_pass=%s verdict=%s unexpected-refusals=%s (%.0fs) %s" % (
            case, rc is not None, row["status"], row["failure_class"], row["gate_pass"], row["r4_verdict"], unexp_ref,
            (t1 - t0).total_seconds(), reporter["brief"](row)))
        T.dump(os.path.join(out, "progress.json"), report)
    return report


def spacing(ev):
    a = ev.get("attempts") or []
    gaps = []
    for i in range(1, len(a)):
        s = datetime.datetime.strptime(a[i]["start_utc"], "%Y-%m-%dT%H:%M:%S.%fZ")
        e = datetime.datetime.strptime(a[i - 1]["end_utc"], "%Y-%m-%dT%H:%M:%S.%fZ")
        gaps.append((s - e).total_seconds())
    return gaps


def dv12(out, rest):
    os.makedirs(out, exist_ok=True)
    toy_dir = rest[0]
    cases = [c for c in CASES if len(rest) < 2 or c in rest[1:]]

    def extract(rd, raw, sev):
        ev = [e for e in s1_events(sev) if e.get("tag") == TARGET_TAG]
        sd = os.path.join(rd, "solver")
        return {"target_event": ev[0] if ev else None, "all_event_tags": [e.get("tag") for e in s1_events(sev)],
                "target_recorded_arm": {k: (target_arm(raw) or {}).get(k) for k in ("outcome", "reason", "D", "D_defined")} if raw and raw.get("targets") else None,
                "renamed_files": sorted(x for x in os.listdir(sd) if ".ssf-attempt" in x) if os.path.isdir(sd) else []}
    rep = {"extract": extract, "brief": lambda r: "target=%s events=%s" % (r["target_recorded_arm"], r["all_event_tags"])}
    report = run_cases(out, toy_dir, cases, FORCING, "entry_v2_dv12.py", TARGET_TAG,
                       lambda env: R.load_json(env["plan_v2r4"])["gate"]["blocking_packages"][0], "v2", rep)
    report["toy_prime"] = TOY_P
    return evaluate(out, report)


def evaluate(out, report):
    import r5_reg1 as REG
    cs = report["cases"]
    res = {}
    U = cs.get("U")
    ref_receipt = os.path.join(out, "toy-U-receipt.json")
    if U and os.path.exists(U["run_dir"]):
        T.tree_receipt(ref_receipt, U["run_dir"])
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
               "spacing_ge_2s": all(g >= 2.0 for g in spacing(ev)) if ev else False,
               "recorded_target_equals_U": c["target_recorded_arm"] == U["target_recorded_arm"],
               "reg1_d_parsed_vs_U_pass": bool(reg) and reg["verdict"] == "PASS",
               "package_completed": c["status"] == U["status"]}
        res[case] = {"checks": chk, "pass": all(chk.values()), "spacing_s": spacing(ev) if ev else None,
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
               "spacing_ge_2s": all(g >= 2.0 for g in spacing(ev)) if ev else False,
               "no_resolve_cap": ev.get("resolve_cap_reached") is False}
        res["d"] = {"checks": chk, "pass": all(chk.values()), "spacing_s": spacing(ev) if ev else None, "package": [c["status"], c["failure_class"], c["gate_pass"]]}
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
        b1 = ((c["solver_events_block"] or {}).get("sites") or {}).get(R.SITE_S1) or {}
        chk = {"two_attempts": len(ev.get("attempts") or []) == 2, "resolve_cap_reached": ev.get("resolve_cap_reached") is True,
               "recorded_is_attempt2_class": (c["target_recorded_arm"] or {}).get("outcome") == "degenerate_parametrisation"
                                             and ev.get("accepted_attempt") == 2,
               "manifest_block_counts_cap": (b1.get("resolve_cap_reached") or 0) >= 1}
        res["f"] = {"checks": chk, "pass": all(chk.values()), "cap_detail": ev.get("resolve_cap_detail")}
    report["evaluation"] = res
    report["all_cases_pass"] = all(v["pass"] for v in res.values()) and len(res) == 7 and all(c.get("launched") for c in cs.values())
    report["STOP"] = None if report["all_cases_pass"] else "SF-6: a DV-12 case failed: %s" % sorted(k for k, v in res.items() if not v["pass"])
    T.dump(os.path.join(out, "dv12.json"), report)
    for k in sorted(res):
        print("  DV-12 (%s): %s %s" % (k, "PASS" if res[k]["pass"] else "FAIL", json.dumps(res[k]["checks"])))
    print("DV-12:", "PASS" if report["all_cases_pass"] else "FAIL/STOP")
    return 0 if report["all_cases_pass"] else 3
